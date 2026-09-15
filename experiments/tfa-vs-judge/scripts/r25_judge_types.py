# R25 (papers/D-iclr-v2/registration_round25.md): three more judge types grade the benchmark pool, blind and with one reference.
# Resumable; spend capped. Run from experiments/tfa-vs-judge.
#   --template cot     reason step by step, then "correct: yes|no"
#   --template verify  structured verification: verify the final answer on your own, compare with the reference, decide
#   --template solve   answer the question yourself first, then grade using your answer (and the reference)
# None of the prompts says whether a question can have several correct answers. Conditions: noref (no reference lines), ref
# (the pool's reference). Grade: the last "correct: yes|no" in the reply, ignoring markdown and case; none = missing.
# Anthropic: thinking disabled, max_tokens 1024. OpenAI: temperature 0, max_tokens 1024. Stored score: 10 (yes) or 0 (no).
import argparse
import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--provider", choices=("anthropic", "openai"), required=True)
ap.add_argument("--model", required=True)
ap.add_argument("--template", choices=("cot", "verify", "solve"), required=True)
ap.add_argument("--conds", default="noref,ref")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--cap-usd", type=float, required=True)
ap.add_argument("--price-in", type=float, required=True)
ap.add_argument("--price-out", type=float, required=True)
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

TEMPLATES = {
    ("cot", "ref"): ("Grade the response to the question, using the reference answer.\n\n"
                     "Question: {question}\n\nReference answer: {target}\n\nResponse: {response}\n\n"
                     "Think step by step about whether the response is correct. Then end with a final line of exactly "
                     "\"correct: yes\" or \"correct: no\"."),
    ("cot", "noref"): ("Grade the response to the question.\n\n"
                       "Question: {question}\n\nResponse: {response}\n\n"
                       "Think step by step about whether the response is correct. Then end with a final line of exactly "
                       "\"correct: yes\" or \"correct: no\"."),
    ("verify", "ref"): ("Grade the response to the question in three steps.\n"
                        "1. Verify: using your own knowledge, check whether the response's final answer is correct for the question as asked.\n"
                        "2. Compare: check the response against the reference answer.\n"
                        "3. Decide whether the response is correct.\n\n"
                        "Question: {question}\n\nReference answer: {target}\n\nResponse: {response}\n\n"
                        "Write one short paragraph for each step, then end with a final line of exactly \"correct: yes\" or \"correct: no\"."),
    ("verify", "noref"): ("Grade the response to the question in two steps.\n"
                          "1. Verify: using your own knowledge, check whether the response's final answer is correct for the question as asked.\n"
                          "2. Decide whether the response is correct.\n\n"
                          "Question: {question}\n\nResponse: {response}\n\n"
                          "Write one short paragraph for each step, then end with a final line of exactly \"correct: yes\" or \"correct: no\"."),
    ("solve", "ref"): ("First answer the question yourself. Then grade the response, using your own answer and the reference answer.\n\n"
                       "Question: {question}\n\nReference answer: {target}\n\nResponse: {response}\n\n"
                       "Write your own answer, then explain whether the response is correct, and end with a final line of exactly "
                       "\"correct: yes\" or \"correct: no\"."),
    ("solve", "noref"): ("First answer the question yourself. Then grade the response, using your own answer.\n\n"
                         "Question: {question}\n\nResponse: {response}\n\n"
                         "Write your own answer, then explain whether the response is correct, and end with a final line of exactly "
                         "\"correct: yes\" or \"correct: no\"."),
}


def prompt(t, j, cond):
    return TEMPLATES[(args.template, cond)].format(question=t["question"], target=t["ref"], response=t["samples"][j])


pool = [json.loads(l) for l in open(args.pool)]
conds = args.conds.split(",")
if args.dry_run:
    for c in conds:
        print(f"===== {args.template} / {c} =====\n{prompt(pool[0], 0, c)}\n")
    sys.exit(0)


def load_key(name):
    if os.environ.get(name):
        return os.environ[name]
    for line in open(os.path.join(HERE, "../../../.env")):
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"\'')
    raise SystemExit(f"no {name}")


outf = os.path.abspath(args.out)
os.makedirs(os.path.dirname(outf), exist_ok=True)
ledger = os.path.join(os.path.dirname(outf), "spend.json")
lock = threading.Lock()
spend = json.load(open(ledger)) if os.path.exists(ledger) else {"usd": 0.0, "calls": 0}
if args.provider == "anthropic":
    import anthropic
    aclient = anthropic.Anthropic(api_key=load_key("ANTHROPIC_API_KEY"), max_retries=6)
    API_ERRORS = (anthropic.APIError,)
else:
    import openai
    oclient = openai.OpenAI(api_key=load_key("OPENAI_API_KEY"), max_retries=6, timeout=300)
    API_ERRORS = (openai.APIError,)


def grade(text):
    m = re.findall(r"correct\s*:\s*(yes|no)\b", re.sub(r"[*_`]", "", text), re.I)
    return (10.0 if m[-1].lower() == "yes" else 0.0) if m else None


def one(job):
    t, j, cond = job
    with lock:
        if spend["usd"] >= args.cap_usd:
            return None
    user = prompt(t, j, cond)
    row = dict(problem_id=t["problem_id"], idx=t["idx"][j], cond=cond, template=args.template, provider=args.provider, model=args.model)
    try:
        if args.provider == "anthropic":
            r = aclient.messages.create(model=args.model, max_tokens=1024, thinking={"type": "disabled"},
                                        messages=[{"role": "user", "content": user}])
            text = "".join(b.text for b in r.content if b.type == "text")
            tin, tout, stop = r.usage.input_tokens, r.usage.output_tokens, r.stop_reason
        else:
            r = oclient.chat.completions.create(model=args.model, messages=[{"role": "user", "content": user}], temperature=0, max_tokens=1024)
            text = r.choices[0].message.content or ""
            tin, tout, stop = r.usage.prompt_tokens, r.usage.completion_tokens, r.choices[0].finish_reason
        row.update(score=grade(text), stop_reason=stop, input_tokens=tin, output_tokens=tout, tail=text[-300:])
        with lock:
            spend["usd"] += tin * args.price_in / 1e6 + tout * args.price_out / 1e6
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
print(f"[r25 {args.provider}/{args.model} {args.template} {args.conds}] {len(jobs)} calls, spend so far ${spend['usd']:.2f}", flush=True)
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
print(f"[r25 done] {outf} missing/errors={n_bad} spend ${spend['usd']:.2f}" + (" (CAP REACHED)" if spend["usd"] >= args.cap_usd else ""), flush=True)
