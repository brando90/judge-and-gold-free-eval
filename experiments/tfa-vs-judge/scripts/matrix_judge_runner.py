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
    ap.add_argument("--rubric", default="math", choices=["math","code"])
    args = ap.parse_args()

    from vllm import LLM, SamplingParams
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model)
    tasks = [json.loads(l) for l in open(args.tasks)]

    def clip(s, n):  # keep prompts inside context
        return s if len(s) <= n else s[:n] + " ...[truncated]"
    prompts = []
    for t in tasks:
        if args.rubric == "code":
            body = RUBRIC_CODE.format(candidate=clip(t["candidate"], 8000))
        else:
            body = RUBRIC.format(question=clip(t["question"], 4000), gold=clip(t["gold"], 6000),
                                 candidate=clip(t["candidate"], 8000))
        msgs = [{"role": "user", "content": body}]
        prompts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True))

    llm = LLM(model=args.model, max_model_len=args.max_model_len,
              gpu_memory_utilization=args.gpu_frac, trust_remote_code=True)
    sp = SamplingParams(temperature=0.0, max_tokens=300)
    outs = llm.generate(prompts, sp)
    with open(args.out, "w") as f:
        for t, o in zip(tasks, outs):
            txt = o.outputs[0].text if o.outputs else ""
            f.write(json.dumps(dict(task_id=t["task_id"], dataset=t.get("dataset"), solver=t.get("solver"),
                                    pid=t.get("pid"), cc=t.get("cc"), label_src=t.get("label_src"),
                                    tfa=t.get("tfa"), cond=t.get("cond"),
                                    judge=args.model, score=parse_score(txt))) + "\n")
    done = sum(1 for _ in open(args.out))
    print(f"[done] {args.model}: {done} judgments -> {args.out}")

if __name__ == "__main__":
    main()
