#!/usr/bin/env python
# Self-contained vLLM judge runner for the E4 matrix (no repo deps). One judge model, all tasks.
# Usage: python matrix_judge_runner.py --model Qwen/Qwen2.5-3B-Instruct --tasks matrix_tasks.jsonl --out out.jsonl
import argparse, json, re

RUBRIC = """You are grading the QUALITY OF MATHEMATICAL REASONING in a candidate solution.
You are given the problem, a gold reference solution, and a candidate solution.

Score the candidate's REASONING (not just its final answer) from 0 to 10:
- 10: fully valid, complete, rigorous reasoning that reaches a correct result.
- 5: partially valid; some correct steps but with a real gap, unjustified jump, or error.
- 0: invalid, incoherent, or empty reasoning (even if the final boxed answer happens to be right).

A correct final answer with hand-wavy or wrong intermediate reasoning must NOT score high.
An answer that is wrong only due to a small arithmetic slip but is otherwise rigorous can score in the middle.

Return STRICT JSON only: {{"score": <float 0-10>, "justification": "<one sentence>"}}.

Problem:
{question}

Gold reference solution:
{gold}

Candidate solution:
{candidate}
"""


RUBRIC_CODE = """You are reviewing a Python function for CORRECTNESS against its specification (the docstring).
No reference solution is provided; reason about the code yourself.

Score from 0 to 10 how likely the implementation is fully correct for ALL valid inputs:
- 10: certainly correct.
- 5: plausible but you found a questionable case or cannot fully verify.
- 0: certainly incorrect (you can point to an input it gets wrong).

Return STRICT JSON only: {{"score": <float 0-10>, "justification": "<one sentence>"}}.

Specification and candidate implementation:
{candidate}
"""


RUBRIC_MATH_NOREF = """You are grading the QUALITY OF MATHEMATICAL REASONING in a candidate solution.
No reference solution is provided; solve or verify the problem yourself as needed.

Score the candidate's REASONING from 0 to 10:
- 10: fully valid, complete, rigorous reasoning that reaches a correct result.
- 5: partially valid; some correct steps but with a real gap, unjustified jump, or error.
- 0: invalid or incorrect reasoning.

Return STRICT JSON only: {{"score": <float 0-10>, "justification": "<one sentence>"}}.

Problem:
{question}

Candidate solution:
{candidate}
"""


RUBRIC_MATH_SOLVEFIRST = """You are grading the QUALITY OF MATHEMATICAL REASONING in a candidate solution.
No reference solution is provided. FIRST, solve the problem yourself step by step and get your own answer.
THEN compare the candidate against your own solution and grade the candidate's REASONING from 0 to 10:
- 10: fully valid, complete, rigorous reasoning that reaches a correct result.
- 5: partially valid; some correct steps but with a real gap, unjustified jump, or error.
- 0: invalid or incorrect reasoning.

Work through your own solution briefly, then output the JSON verdict as the FINAL line:
{{"score": <float 0-10>}}

Problem:
{question}

Candidate solution:
{candidate}
"""


RUBRIC_STEPLOC = """You are checking a step-by-step solution for its EARLIEST ERROR.
Read the problem and the numbered steps. If every step is correct, answer -1.
Otherwise identify the index of the EARLIEST step that is incorrect.

Return STRICT JSON only, as the FINAL line: {{"first_error_step": <int, or -1 if all steps are correct>}}

Problem:
{question}

Solution steps:
{candidate}
"""

RUBRIC_STEPLOC_SOLVE = """You are checking a step-by-step solution for its EARLIEST ERROR.
FIRST, solve the problem yourself and get your own answer. THEN check the numbered steps against your
solution. If every step is correct, answer -1. Otherwise identify the EARLIEST incorrect step.

Work briefly, then return STRICT JSON as the FINAL line: {{"first_error_step": <int, or -1 if all steps are correct>}}

Problem:
{question}

Solution steps:
{candidate}
"""


RUBRIC_PAIR = """You are comparing two responses to a prompt. Decide which response is BETTER overall
(more correct, more helpful, better focused on the request).

Return STRICT JSON only, as the FINAL line: {{"winner": "A"}} or {{"winner": "B"}}

Prompt:
{question}

Response A:
{A}

Response B:
{B}"""

RUBRIC_PAIRREF = """You are comparing two responses to a prompt. You previously wrote your own answer to this
prompt; use it as a reference point. Decide which response is BETTER overall (more correct, more helpful,
better focused on the request).

Return STRICT JSON only, as the FINAL line: {{"winner": "A"}} or {{"winner": "B"}}

Prompt:
{question}

Your own earlier answer (reference):
{gold}

Response A:
{A}

Response B:
{B}"""

RUBRIC_ANSWER = """{question}"""

def parse_pair(text):
    import re as _re
    ms=_re.findall(r'"winner"\s*:\s*"?([AB])', text or "")
    if ms: return 0.0 if ms[-1]=="A" else 1.0
    tail=(text or "").strip()[-10:]
    ms=_re.findall(r"\b([AB])\b", tail)
    return (0.0 if ms[-1]=="A" else 1.0) if ms else None

def parse_steploc(text):
    import re as _re, json as _json
    ms=_re.findall(r'\{[^{}]*?"first_error_step"[^{}]*?\}', text or "")
    for mm in reversed(ms):
        try: return float(_json.loads(mm)["first_error_step"])
        except Exception: pass
    ms=_re.findall(r'first_error_step\D{0,5}(-?\d+)', text or "")
    return float(ms[-1]) if ms else None

def parse_score(text):
    m = re.search(r"\{.*?\}", text or "", re.DOTALL)
    if m:
        try: return float(json.loads(m.group(0))["score"])
        except Exception: pass
    m = re.search(r"score\D{0,5}([0-9]+(?:\.[0-9]+)?)", text or "", re.IGNORECASE)
    return float(m.group(1)) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max_model_len", type=int, default=8192)
    ap.add_argument("--gpu_frac", type=float, default=0.92)
    ap.add_argument("--dump_text", action="store_true")
    ap.add_argument("--rubric", default="math", choices=["math","code","mathnoref","norefsolve","steploc","steplocsolve","pair","pairref","answer"])
    args = ap.parse_args()

    from vllm import LLM, SamplingParams
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model)
    tasks = [json.loads(l) for l in open(args.tasks)]

    def clip(s, n):  # keep prompts inside context
        return s if len(s) <= n else s[:n] + " ...[truncated]"
    prompts = []
    for t in tasks:
        if args.rubric == "pair":
            body = RUBRIC_PAIR.format(question=clip(t["question"], 4000), A=clip(t["A"], 5000), B=clip(t["B"], 5000))
        elif args.rubric == "pairref":
            body = RUBRIC_PAIRREF.format(question=clip(t["question"], 4000), gold=clip(t["gold"], 3000),
                                         A=clip(t["A"], 5000), B=clip(t["B"], 5000))
        elif args.rubric == "answer":
            body = RUBRIC_ANSWER.format(question=clip(t["question"], 4000))
        elif args.rubric == "norefsolve":
            body = RUBRIC_MATH_SOLVEFIRST.format(question=clip(t["question"], 4000), candidate=clip(t["candidate"], 8000))
        elif args.rubric == "steploc":
            body = RUBRIC_STEPLOC.format(question=clip(t["question"], 4000), candidate=clip(t["candidate"], 9000))
        elif args.rubric == "steplocsolve":
            body = RUBRIC_STEPLOC_SOLVE.format(question=clip(t["question"], 4000), candidate=clip(t["candidate"], 9000))
        elif args.rubric == "mathnoref":
            body = RUBRIC_MATH_NOREF.format(question=clip(t["question"], 4000), candidate=clip(t["candidate"], 8000))
        elif args.rubric == "code":
            body = RUBRIC_CODE.format(candidate=clip(t["candidate"], 8000))
        else:
            body = RUBRIC.format(question=clip(t["question"], 4000), gold=clip(t["gold"], 6000),
                                 candidate=clip(t["candidate"], 8000))
        msgs = [{"role": "user", "content": body}]
        prompts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True))

    llm = LLM(model=args.model, max_model_len=args.max_model_len,
              gpu_memory_utilization=args.gpu_frac, trust_remote_code=True)
    sp = SamplingParams(temperature=0.0, max_tokens=(900 if args.rubric in ("norefsolve","steplocsolve") else (700 if args.rubric == "answer" else 300)))
    outs = llm.generate(prompts, sp)
    with open(args.out, "w") as f:
        for t, o in zip(tasks, outs):
            txt = o.outputs[0].text if o.outputs else ""
            f.write(json.dumps(dict(task_id=t["task_id"], dataset=t.get("dataset"), solver=t.get("solver"),
                                    pid=t.get("pid"), cc=t.get("cc"), label_src=t.get("label_src"),
                                    tfa=t.get("tfa"), cond=t.get("cond"),
                                    judge=args.model, score=(parse_steploc(txt) if args.rubric in ("steploc","steplocsolve") else (parse_pair(txt) if args.rubric in ("pair","pairref") else (None if args.rubric=="answer" else parse_score(txt)))), text=(txt if args.dump_text else None))) + "\n")
    done = sum(1 for _ in open(args.out))
    print(f"[done] {args.model}: {done} judgments -> {args.out}")

if __name__ == "__main__":
    main()
