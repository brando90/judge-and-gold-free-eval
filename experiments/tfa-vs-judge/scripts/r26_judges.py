# R26 (papers/D-iclr-v2/registration_round26.md): API judges for the instruction-versus-reasoning and false-acceptance tests.
# Resumable; spend capped. Run from experiments/tfa-vs-judge. All templates end in "correct: yes|no"; grade = the last such line
# (markdown and case ignored); none = missing. Anthropic: thinking disabled, max_tokens 1024. OpenAI: temperature 0, max_tokens 1024,
# no system message (the same settings for every template, so templates are compared under one configuration).
#   direct    ask whether the response is a correct answer (reference line in the ref condition); no reasoning requested
#   verify    R25 verify-first prompt (verbatim from r25_judge_types.py)
#   solve     R25 solve-first prompt (verbatim from r25_judge_types.py)
#   hle       the HLE judge prompt, verbatim (vendored), reference condition only
#   hle_edit  the HLE judge prompt with its match-only clause removed and one sentence added (see EDITS below), reference only
import argparse
import ast
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
ap.add_argument("--template", choices=("direct", "counter", "verify", "solve", "hle", "hle_edit"), required=True)
ap.add_argument("--conds", required=True)
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--cap-usd", type=float, required=True)
ap.add_argument("--price-in", type=float, required=True)
ap.add_argument("--price-out", type=float, required=True)
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--max-tokens", type=int, default=1024, help="R27 Amendment 2: output limit (default 1024 = R26 setting)")
ap.add_argument("--redo-missing", action="store_true", help="R27 Amendment 2: re-run calls whose earlier reply had no grade")
args = ap.parse_args()


def vendored(path, name):
    for node in ast.parse(open(os.path.join(HERE, "vendor", path)).read()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit(name)


HLE = vendored("centerforaisafety_hle_eval_run_judge_results.py", "JUDGE_PROMPT")
EDITS = [(", do not attempt to solve the problem, do not argue for any answer different than [correct_answer], focus only on whether the answers match.",
          ", do not attempt to solve the problem."),
         ("or if the extracted answer is incorrect.",
          "or if the extracted answer is incorrect. A response that gives a different answer that is also correct for the question is correct.")]
HLE_EDIT = HLE
for old, new in EDITS:
    assert HLE_EDIT.count(old) == 1, old
    HLE_EDIT = HLE_EDIT.replace(old, new)

TAIL = "end with a final line of exactly \"correct: yes\" or \"correct: no\"."
T = {
    ("direct", "ref"): "Is the response a correct answer to the question?\n\nQuestion: {question}\n\nReference answer: {target}\n\nResponse: {response}\n\nDo not explain; " + TAIL.replace("end with a final line", "reply with a single line"),
    ("direct", "noref"): "Is the response a correct answer to the question?\n\nQuestion: {question}\n\nResponse: {response}\n\nDo not explain; " + TAIL.replace("end with a final line", "reply with a single line"),
    # R31: the counter-instructed swap. Byte-identical to ("direct", "ref") except for the one inserted
    # sentence telling the judge NOT to use the reference. Keeping everything else fixed is the point:
    # any difference from the direct arm is attributable to the instruction, not to rewording.
    ("counter", "ref"): "Is the response a correct answer to the question?\n\nQuestion: {question}\n\nReference answer: {target}\n\nThe reference answer is only one of several correct answers. Do not compare the response to it, and do not treat agreeing or disagreeing with it as evidence; judge only whether the response is itself a correct answer to the question.\n\nResponse: {response}\n\nDo not explain; " + TAIL.replace("end with a final line", "reply with a single line"),
    ("verify", "ref"): ("Grade the response to the question in three steps.\n"
                        "1. Verify: using your own knowledge, check whether the response's final answer is correct for the question as asked.\n"
                        "2. Compare: check the response against the reference answer.\n"
                        "3. Decide whether the response is correct.\n\n"
                        "Question: {question}\n\nReference answer: {target}\n\nResponse: {response}\n\n"
                        "Write one short paragraph for each step, then " + TAIL),
    ("verify", "noref"): ("Grade the response to the question in two steps.\n"
                          "1. Verify: using your own knowledge, check whether the response's final answer is correct for the question as asked.\n"
                          "2. Decide whether the response is correct.\n\n"
                          "Question: {question}\n\nResponse: {response}\n\n"
                          "Write one short paragraph for each step, then " + TAIL),
    ("solve", "ref"): ("First answer the question yourself. Then grade the response, using your own answer and the reference answer.\n\n"
                       "Question: {question}\n\nReference answer: {target}\n\nResponse: {response}\n\n"
                       "Write your own answer, then explain whether the response is correct, and " + TAIL),
    ("solve", "noref"): ("First answer the question yourself. Then grade the response, using your own answer.\n\n"
                         "Question: {question}\n\nResponse: {response}\n\n"
                         "Write your own answer, then explain whether the response is correct, and " + TAIL),
}


def prompt(t, j, cond):
    if args.template == "hle":
        return HLE.format(question=t["question"], response=t["samples"][j], correct_answer=t["ref"])
    if args.template == "hle_edit":
        return HLE_EDIT.format(question=t["question"], response=t["samples"][j], correct_answer=t["ref"])
    return T[(args.template, cond)].format(question=t["question"], target=t["ref"], response=t["samples"][j])


pool = [json.loads(l) for l in open(args.pool)]
conds = args.conds.split(",")
if args.template.startswith("hle") and conds != ["ref"]:
    raise SystemExit("hle templates take the reference condition only")
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
    if args.max_tokens != 1024:
        row["max_tokens"] = args.max_tokens
    try:
        if args.provider == "anthropic":
            r = aclient.messages.create(model=args.model, max_tokens=args.max_tokens, thinking={"type": "disabled"}, messages=[{"role": "user", "content": user}])
            text = "".join(b.text for b in r.content if b.type == "text")
            tin, tout, stop = r.usage.input_tokens, r.usage.output_tokens, r.stop_reason
        else:
            r = oclient.chat.completions.create(model=args.model, messages=[{"role": "user", "content": user}], temperature=0, max_tokens=args.max_tokens)
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
        if not r.get("error") and not (args.redo_missing and r.get("score") is None):
            done.add((r["problem_id"], r["idx"], r["cond"]))
        elif args.redo_missing and r.get("score") is not None:
            done.add((r["problem_id"], r["idx"], r["cond"]))
jobs = [(t, j, c) for t in pool for j in range(len(t["samples"])) for c in conds if (t["problem_id"], t["idx"][j], c) not in done]
print(f"[r26 {args.provider}/{args.model} {args.template} {args.conds} {os.path.basename(args.pool)}] {len(jobs)} calls, spend ${spend['usd']:.2f}", flush=True)
n_bad = 0
with open(outf, "a") as f, ThreadPoolExecutor(args.workers) as ex:
    for i, row in enumerate(ex.map(one, jobs)):
        if row is None:
            continue
        n_bad += row.get("score") is None
        with lock:
            f.write(json.dumps(row) + "\n")
            f.flush()
            if (i + 1) % 200 == 0:
                json.dump(spend, open(ledger, "w"))
                print(f"  {i + 1}/{len(jobs)} missing/errors {n_bad} spend ${spend['usd']:.2f}", flush=True)
json.dump(spend, open(ledger, "w"))
print(f"[r26 done] {outf} missing/errors={n_bad} spend ${spend['usd']:.2f}" + (" (CAP REACHED)" if spend["usd"] >= args.cap_usd else ""), flush=True)
