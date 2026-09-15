# R24 (papers/D-iclr-v2/registration_round24.md): one harness for the round-24 graders. Resumable; spend capped.
# Run from experiments/tfa-vs-judge.
#   --template rubric   the paper's score-only rubric a (bon_rubrics.RUBRIC_TIES); conditions noref, ref, reflist.
#                       Anthropic judges: sampled integer, last integer 0-10 in the reply (as sonnet_api_pool.py).
#                       OpenAI judges: logprob-expected score over the tokens 0-10 (as frontier_api_judge.py: temperature 0,
#                       max_completion_tokens 4, top_logprobs 5).
#   --template simpleqa the verbatim SimpleQA grader (GRADER_TEMPLATE of openai/simple-evals simpleqa_eval.py, vendored in
#                       scripts/vendor/ at commit 5e623c2). OpenAI calls reproduce simple-evals' grading sampler (system
#                       "You are a helpful assistant.", temperature 0.5, max_tokens 2048). Grade: first standalone A, B or C.
#   --template hle      the verbatim HLE judge prompt (JUDGE_PROMPT of centerforaisafety/hle run_judge_results.py, vendored at
#                       commit a590489). o3-mini calls reproduce HLE (structured output ExtractedAnswer, max_completion_tokens
#                       4096). Other models get the text prompt and are parsed as simple-evals BrowseComp parses the same
#                       judge format ("correct: yes|no"), made robust to markdown.
# Conditions: noref = blind (rubric only); ref = the pool's reference; reflist = every answer in the MACE answer list
# (runs/mace_tasks.jsonl valid_answers, sorted alphabetically), stated as any one of them being a complete correct answer.
# --instruction anyvalid appends the full-credit sentence (verbatim from bon_judge.py) to the referenced rubric (R24-D).
# Binary templates store score 10 (correct) or 0 (incorrect), so the r20/r22 producers' threshold of 7 applies unchanged; a
# reply with no parseable grade is stored with score None (missing) and its official-default grade in `grade_official`.
import argparse
import ast
import json
import math
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bon_rubrics import RUBRIC_TIES  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--provider", choices=("anthropic", "openai"), required=True)
ap.add_argument("--model", required=True)
ap.add_argument("--template", choices=("rubric", "simpleqa", "hle"), required=True)
ap.add_argument("--conds", required=True, help="comma-separated subset of noref,ref,reflist")
ap.add_argument("--tasks", default="runs/mace_tasks.jsonl")
ap.add_argument("--thinking", choices=("disabled", "adaptive"), default="disabled")
ap.add_argument("--max-tokens", type=int, default=512, help="Anthropic calls")
ap.add_argument("--instruction", choices=("none", "anyvalid"), default="none")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--cap-usd", type=float, required=True)
ap.add_argument("--price-in", type=float, required=True, help="USD per million input tokens (ledger only)")
ap.add_argument("--price-out", type=float, required=True, help="USD per million output tokens (ledger only)")
ap.add_argument("--dry-run", action="store_true", help="print the first prompt of each condition and exit; no calls")
args = ap.parse_args()

ANYVALID = (" Note: the reference shown is one valid answer among possibly many; the "
            "question may have several correct answers, and any correct answer "
            "deserves full credit even if it differs from the reference.")
OPENAI_SYSTEM_MESSAGE_API = "You are a helpful assistant."


def vendored(path, name):
    for node in ast.parse(open(os.path.join(HERE, "vendor", path)).read()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            v = node.value
            if isinstance(v, ast.Call) and getattr(v.func, "attr", None) == "strip":
                return ast.literal_eval(v.func.value).strip()
            return ast.literal_eval(v)
    raise SystemExit(f"{name} not found in {path}")


SIMPLEQA_TEMPLATE = vendored("openai_simpleqa_eval.py", "GRADER_TEMPLATE")
HLE_TEMPLATE = vendored("centerforaisafety_hle_eval_run_judge_results.py", "JUDGE_PROMPT")
REF_RUBRIC = RUBRIC_TIES[("ref", "a")]
REFLIST_RUBRIC = (REF_RUBRIC.replace("a reference answer known to be correct",
                                     "a list of reference answers, each known to be correct and each a complete correct answer on its own")
                  .replace("using the reference to check it", "using the references to check it"))
assert REFLIST_RUBRIC.count("list of reference answers") == 1 and "using the references" in REFLIST_RUBRIC


def load_key(name):
    if os.environ.get(name):
        return os.environ[name]
    for line in open(os.path.join(HERE, "../../../.env")):
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"\'')
    raise SystemExit(f"no {name}")


TASKS = {}
for line in open(args.tasks):
    t = json.loads(line)
    TASKS[t["problem_id"]] = t


def answer_list(pid):
    return "; ".join(sorted(TASKS[pid]["valid_answers"]))


def target(t, cond):
    if cond == "ref":
        return t["ref"]
    return f"Any one of the following is a complete correct answer: {answer_list(t['problem_id'])}"


def build(t, j, cond):
    """Returns (system or None, user)."""
    q, s = t["question"], t["samples"][j]
    if args.template == "rubric":
        user = f"Problem:\n{q}\n\n"
        if cond == "noref":
            system = RUBRIC_TIES[("noref", "a")]
        elif cond == "ref":
            system = REF_RUBRIC
            user += f"Reference answer (trusted):\n{t['ref']}\n\n"
        else:
            system = REFLIST_RUBRIC
            user += f"Reference answers (trusted; any one of them is a complete correct answer):\n{answer_list(t['problem_id'])}\n\n"
        if cond != "noref" and args.instruction == "anyvalid":
            system += ANYVALID
        return system, user + f"Candidate solution:\n{s}\n\nScore:"
    if cond == "noref":
        raise SystemExit("binary templates need a reference condition")
    if args.template == "simpleqa":
        return None, SIMPLEQA_TEMPLATE.format(question=q, target=target(t, cond), predicted_answer=s)
    return None, HLE_TEMPLATE.format(question=q, response=s, correct_answer=target(t, cond))


pool = [json.loads(l) for l in open(args.pool)]
conds = args.conds.split(",")
if args.dry_run:
    for c in conds:
        sy, us = build(pool[0], 0, c)
        print(f"===== {args.template} / {c} =====\nSYSTEM: {sy}\nUSER:\n{us}\n")
    sys.exit(0)

outf = os.path.abspath(args.out)
os.makedirs(os.path.dirname(outf), exist_ok=True)
ledger = os.path.join(os.path.dirname(outf), "spend.json")
lock = threading.Lock()
spend = json.load(open(ledger)) if os.path.exists(ledger) else {"usd": 0.0, "calls": 0}
PRICE_IN, PRICE_OUT = args.price_in / 1e6, args.price_out / 1e6

if args.provider == "anthropic":
    import anthropic
    aclient = anthropic.Anthropic(api_key=load_key("ANTHROPIC_API_KEY"), max_retries=6)
    API_ERRORS = (anthropic.APIError,)
else:
    import openai
    from pydantic import BaseModel
    oclient = openai.OpenAI(api_key=load_key("OPENAI_API_KEY"), max_retries=6, timeout=300)
    API_ERRORS = (openai.APIError,)

    class ExtractedAnswer(BaseModel):  # verbatim from HLE run_judge_results.py
        extracted_final_answer: str
        reasoning: str
        correct: Literal["yes", "no"]
        confidence: int
        strict: Literal[True]

SCORE_TOK = {}
for v in range(11):
    for tok in (str(v), " " + str(v)):
        SCORE_TOK[tok] = v


def escore_openai(choice):
    """frontier_api_judge.py estimator: expected value over score tokens, mass-renormalized."""
    txt = (choice.message.content or "").strip()
    content = (choice.logprobs.content or []) if choice.logprobs else []
    top = content[0].top_logprobs if content else []
    one_means = 10 if txt.startswith("10") else 1
    num = den = 0.0
    for tl in top:
        if tl.token in SCORE_TOK:
            v = one_means if SCORE_TOK[tl.token] == 1 else SCORE_TOK[tl.token]
            p = math.exp(tl.logprob)
            num += p * v
            den += p
    if den >= 0.25:
        return num / den, "logprob"
    m = re.search(r"\d+", txt)
    return (float(min(int(m.group()), 10)), "text") if m else (5.0, "fallback")


def grade_text(text):
    """Returns (score or None, grade, official-default grade)."""
    if args.template == "simpleqa":
        m_off = re.search(r"(A|B|C)", text)
        m = re.search(r"\b(A|B|C)\b", text)
        off = m_off.group(0) if m_off else "C"
        return (None if not m else (10.0 if m.group(1) == "A" else 0.0)), (m.group(1) if m else None), off
    m_off = re.search(r"correct: (yes|no)", text)
    m = re.search(r"correct\s*:\s*(yes|no)\b", re.sub(r"[*_`]", "", text), re.I)
    off = m_off.group(1) if m_off else "no"
    return (None if not m else (10.0 if m.group(1).lower() == "yes" else 0.0)), (m.group(1).lower() if m else None), off


def one(job):
    t, j, cond = job
    with lock:
        if spend["usd"] >= args.cap_usd:
            return None
    system, user = build(t, j, cond)
    row = dict(problem_id=t["problem_id"], idx=t["idx"][j], cond=cond, template=args.template, provider=args.provider,
               model=args.model, interface="api")
    if args.thinking != "disabled":
        row["thinking"] = args.thinking
    if args.instruction != "none" and cond != "noref":
        row["instruction"] = args.instruction
    try:
        if args.provider == "anthropic":
            kw = dict(model=args.model, max_tokens=args.max_tokens, thinking={"type": args.thinking},
                      messages=[{"role": "user", "content": user}])
            if system:
                kw["system"] = system
            r = aclient.messages.create(**kw)
            text = "".join(b.text for b in r.content if b.type == "text")
            tin, tout, stop = r.usage.input_tokens, r.usage.output_tokens, r.stop_reason
            if args.template == "rubric":
                m = re.findall(r"\b(10|[0-9])\b", text)
                row.update(score=float(m[-1]) if m else None)
            else:
                sc, g, off = grade_text(text)
                row.update(score=sc, grade=g, grade_official=off)
        elif args.template == "rubric":
            r = oclient.chat.completions.create(model=args.model, messages=[{"role": "system", "content": system},
                                                                             {"role": "user", "content": user}],
                                                temperature=0, max_completion_tokens=4, logprobs=True, top_logprobs=5)
            text = r.choices[0].message.content or ""
            sc, how = escore_openai(r.choices[0])
            row.update(score=sc, estimator=how)
            tin, tout, stop = r.usage.prompt_tokens, r.usage.completion_tokens, r.choices[0].finish_reason
        elif args.template == "hle" and args.model.startswith("o3-mini"):
            r = oclient.chat.completions.parse(model=args.model, max_completion_tokens=4096,
                                               messages=[{"role": "user", "content": user}], response_format=ExtractedAnswer)
            p = r.choices[0].message.parsed
            text = p.reasoning if p else (r.choices[0].message.content or "")
            row.update(score=(10.0 if p.correct == "yes" else 0.0) if p else None, grade=p.correct if p else None,
                       grade_official=p.correct if p else None, extracted=p.extracted_final_answer if p else None)
            tin, tout, stop = r.usage.prompt_tokens, r.usage.completion_tokens, r.choices[0].finish_reason
        else:
            r = oclient.chat.completions.create(model=args.model, messages=[{"role": "system", "content": OPENAI_SYSTEM_MESSAGE_API},
                                                                             {"role": "user", "content": user}],
                                                temperature=0.5, max_tokens=2048)
            text = r.choices[0].message.content or ""
            sc, g, off = grade_text(text)
            row.update(score=sc, grade=g, grade_official=off)
            tin, tout, stop = r.usage.prompt_tokens, r.usage.completion_tokens, r.choices[0].finish_reason
        row.update(stop_reason=stop, input_tokens=tin, output_tokens=tout, tail=text[-300:])
        with lock:
            spend["usd"] += tin * PRICE_IN + tout * PRICE_OUT
            spend["calls"] += 1
    except API_ERRORS as e:
        row.update(score=None, error=f"{type(e).__name__}: {str(e)[:200]}")
    return row


done = set()
if os.path.exists(outf):
    for l in open(outf):
        r = json.loads(l)
        if not r.get("error"):
            done.add((r["problem_id"], r["idx"], r["cond"]))
jobs = [(t, j, c) for t in pool for j in range(len(t["samples"])) for c in conds if (t["problem_id"], t["idx"][j], c) not in done]
print(f"[r24 {args.provider}/{args.model} {args.template} {args.conds} {os.path.basename(args.pool)}] {len(jobs)} calls, "
      f"spend so far ${spend['usd']:.2f}", flush=True)
n_bad = 0
with open(outf, "a") as f, ThreadPoolExecutor(args.workers) as ex:
    for i, row in enumerate(ex.map(one, jobs)):
        if row is None:
            continue
        n_bad += row.get("score") is None
        with lock:
            f.write(json.dumps(row) + "\n")
            f.flush()
            if (i + 1) % 100 == 0:
                json.dump(spend, open(ledger, "w"))
                print(f"  {i + 1}/{len(jobs)} missing/errors {n_bad} spend ${spend['usd']:.2f}", flush=True)
json.dump(spend, open(ledger, "w"))
print(f"[r24 done] {outf} missing/errors={n_bad} spend ${spend['usd']:.2f}" + (" (CAP REACHED)" if spend["usd"] >= args.cap_usd else ""),
      flush=True)
