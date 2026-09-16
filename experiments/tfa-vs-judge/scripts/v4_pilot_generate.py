# v4 pilot: which cheap, fast model can actually solve MathRefBench items?
# Run from experiments/tfa-vs-judge. Resumable; spend capped per model.
#   python scripts/v4_pilot_generate.py --model claude-haiku-4-5-20251001 --provider anthropic --price-in 1 --price-out 5
#
# Samples a stratified set of items (both sources, short and long answers), asks each model for ONE answer
# with the v4 candidate prompt (datasets/multirefbench_single_answer_v1.prompt, used verbatim), and scores
# the reply against the item's answer bank by normalized_answer_id matching.
#
# Scoring caveat, recorded here because it bounds every rate this script prints: the bank is a SAMPLE of
# valid answers (origin "generated" for 1,874 of 2,198 solutions), not a complete set, so a correct answer
# that is absent from the bank counts as a miss. Bank-match rate is therefore a LOWER BOUND on solve rate.
import argparse
import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))  # judge-free-eval/
BENCH = os.path.join(ROOT, "datasets/final_mathrefbench.jsonl")
PROMPT = os.path.join(ROOT, "datasets/multirefbench_single_answer_v1.prompt")

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--provider", choices=("anthropic", "openai"), required=True)
ap.add_argument("--n-items", type=int, default=10)
ap.add_argument("--seed", type=int, default=20260902)
ap.add_argument("--max-tokens", type=int, default=16000)
ap.add_argument("--workers", type=int, default=5)
ap.add_argument("--cap-usd", type=float, default=3.0)
ap.add_argument("--price-in", type=float, required=True)
ap.add_argument("--price-out", type=float, required=True)
ap.add_argument("--out-dir", default="runs/v4_pilot")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()


def norm(a):
    return re.sub(r"[\s\$]+", "", str(a)).strip().lower()


def load_key(name):
    if os.environ.get(name):
        return os.environ[name]
    for line in open(os.path.join(ROOT, ".env")):
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"\'')
    raise SystemExit(f"no {name}")


rows = [json.loads(l) for l in open(BENCH)]
template = open(PROMPT).read()

# stratified sample: both sources, and within each, short / long answers
import random
rng = random.Random(args.seed)
picked = []
for pfx in ("mathconstruct", "math_constraint"):
    sub = [r for r in rows if r["question_id"].startswith(pfx)]
    sub.sort(key=lambda r: min(len(str(s["answer"])) for s in r["solutions"]))
    half = args.n_items // 2
    short, long_ = sub[: len(sub) // 2], sub[len(sub) // 2:]
    picked += rng.sample(short, min(half - half // 2, len(short)))
    picked += rng.sample(long_, min(half // 2, len(long_)))

STRICT = ("\n\nThe boxed answer must be the literal value in exactly the format above: digits, "
          "commas and brackets only. Do not use LaTeX environments, \\ldots, ellipses, set-builder "
          "notation, or any abbreviation inside the box; write every element explicitly.")


def render(r):
    return (template.replace("[PROBLEM]", r["problem"])
                    .replace("[ANSWER_FORMAT]", r["formatting_instructions"] + STRICT))


if args.dry_run:
    print(f"{len(picked)} items sampled")
    print(render(picked[0])[:1200])
    sys.exit(0)

os.makedirs(args.out_dir, exist_ok=True)
outf = os.path.join(args.out_dir, f"{args.model.replace('/', '_')}.jsonl")
ledger = os.path.join(args.out_dir, f"spend_{args.model.replace('/', '_')}.json")
spend = json.load(open(ledger)) if os.path.exists(ledger) else {"usd": 0.0, "calls": 0}
lock = threading.Lock()

if args.provider == "anthropic":
    import anthropic
    client = anthropic.Anthropic(api_key=load_key("ANTHROPIC_API_KEY"), max_retries=5)
    ERRORS = (anthropic.APIError,)
else:
    import openai
    client = openai.OpenAI(api_key=load_key("OPENAI_API_KEY"), max_retries=5, timeout=600)
    ERRORS = (openai.APIError,)

done = set()
if os.path.exists(outf):
    for l in open(outf):
        r = json.loads(l)
        if not r.get("error"):
            done.add(r["question_id"])


def extract(text):
    m = re.findall(r"<FINAL_ANSWER>\s*\\boxed\{(.*?)\}\s*</FINAL_ANSWER>", text, re.S)
    if m:
        return m[-1].strip()
    m = re.findall(r"\\boxed\{(.*?)\}", text, re.S)
    return m[-1].strip() if m else None


def one(r):
    with lock:
        if spend["usd"] >= args.cap_usd:
            return None
    import time
    t0 = time.time()
    row = {"question_id": r["question_id"], "model": args.model, "source": r["question_id"].split("/")[0]}
    try:
        if args.provider == "anthropic":
            resp = client.messages.create(model=args.model, max_tokens=args.max_tokens,
                                          messages=[{"role": "user", "content": render(r)}])
            text = "".join(b.text for b in resp.content if b.type == "text")
            tin, tout, stop = resp.usage.input_tokens, resp.usage.output_tokens, resp.stop_reason
        else:
            kw = dict(model=args.model, messages=[{"role": "user", "content": render(r)}])
            kw["max_completion_tokens"] = args.max_tokens
            resp = client.chat.completions.create(**kw)
            text = resp.choices[0].message.content or ""
            tin, tout, stop = resp.usage.prompt_tokens, resp.usage.completion_tokens, resp.choices[0].finish_reason
        ans = extract(text)
        bank = {norm(s["answer"]): s["normalized_answer_id"] for s in r["solutions"]}
        row.update(answer=ans, truncated=(stop in ("length", "max_tokens")),
                   bank_match=bool(ans and norm(ans) in bank),
                   matched_class=bank.get(norm(ans)) if ans else None,
                   n_classes=len({s["normalized_answer_id"] for s in r["solutions"]}),
                   stop_reason=stop, input_tokens=tin, output_tokens=tout,
                   seconds=round(time.time() - t0, 1), tail=text[-400:])
        with lock:
            spend["usd"] += tin * args.price_in / 1e6 + tout * args.price_out / 1e6
            spend["calls"] += 1
    except ERRORS as e:
        row.update(error=f"{type(e).__name__}: {str(e)[:200]}")
    return row


todo = [r for r in picked if r["question_id"] not in done]
print(f"[v4 pilot {args.model}] {len(todo)} of {len(picked)} items, spend ${spend['usd']:.2f}", flush=True)
with open(outf, "a") as f, ThreadPoolExecutor(args.workers) as ex:
    for row in ex.map(one, todo):
        if row is None:
            continue
        with lock:
            f.write(json.dumps(row) + "\n")
            f.flush()
json.dump(spend, open(ledger, "w"))

got = [json.loads(l) for l in open(outf)]
ok = [r for r in got if not r.get("error")]
hit = [r for r in ok if r.get("bank_match")]
sec = [r["seconds"] for r in ok if "seconds" in r]
print(f"[done] {args.model}: bank-match {len(hit)}/{len(ok)}"
      f" | median {sorted(sec)[len(sec)//2] if sec else 0:.0f}s"
      f" | out-tokens median {sorted(r['output_tokens'] for r in ok)[len(ok)//2] if ok else 0}"
      f" | spend ${spend['usd']:.2f}", flush=True)
