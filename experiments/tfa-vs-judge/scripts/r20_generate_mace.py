# R20-C (papers/D-iclr/registration_round20.md): one answer per question from API generators on MACE River and Language questions
# with several correct answers, with the same prompt as the stored MACE candidate pool (bon_generate.py, domain "mace").
# Run from experiments/tfa-vs-judge. Resumable; spend capped.
#   python scripts/r20_generate_mace.py --model claude-haiku-4-5-20251001 --price-in 1 --price-out 5
import argparse
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import anthropic

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--out-dir", default="runs/r20/mace_gen")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--max-tokens", type=int, default=512)
ap.add_argument("--price-in", type=float, required=True, help="USD per million input tokens (ledger only)")
ap.add_argument("--price-out", type=float, required=True, help="USD per million output tokens (ledger only)")
ap.add_argument("--cap-usd", type=float, default=15.0)
args = ap.parse_args()


def prompt_of(r):
    return ("Answer the following question. Give exactly one answer. You MUST end your "
            "response with the answer inside \\boxed{...}, with nothing after it. "
            "Example ending: The answer is \\boxed{Paris}\n\n" + r["problem"])


def load_key():
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k
    for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.env")):
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"\'')
    raise SystemExit("no ANTHROPIC_API_KEY")


def domain(t):
    p = t["params"] if isinstance(t["params"], dict) else eval(t["params"])
    return p["domain"]


tasks = [t for t in (json.loads(l) for l in open("runs/mace_tasks.jsonl")) if domain(t) in ("River", "Language") and int(t["k"]) > 1]
os.makedirs(args.out_dir, exist_ok=True)
outf = os.path.join(args.out_dir, f"{args.model}.jsonl")
ledger = os.path.join(args.out_dir, f"spend_{args.model}.json")
spend = json.load(open(ledger)) if os.path.exists(ledger) else {"usd": 0.0, "calls": 0}
done = set()
if os.path.exists(outf):
    done = {json.loads(l)["problem_id"] for l in open(outf) if not json.loads(l).get("error")}
client = anthropic.Anthropic(api_key=load_key(), max_retries=6)
lock = threading.Lock()


def one(t):
    with lock:
        if spend["usd"] >= args.cap_usd:
            return None
    row = dict(problem_id=t["problem_id"], model=args.model)
    try:
        r = client.messages.create(model=args.model, max_tokens=args.max_tokens,
                                   messages=[{"role": "user", "content": prompt_of(t)}])
        text = "".join(b.text for b in r.content if b.type == "text")
        row.update(sample=text, stop_reason=r.stop_reason, input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens)
        with lock:
            spend["usd"] += r.usage.input_tokens * args.price_in / 1e6 + r.usage.output_tokens * args.price_out / 1e6
            spend["calls"] += 1
    except anthropic.APIError as e:
        row.update(sample=None, error=f"{type(e).__name__}: {str(e)[:200]}")
    return row


jobs = [t for t in tasks if t["problem_id"] not in done]
print(f"[r20-generate {args.model}] {len(jobs)} of {len(tasks)} questions to answer", flush=True)
with open(outf, "a") as f, ThreadPoolExecutor(args.workers) as ex:
    for row in ex.map(one, jobs):
        if row is None:
            continue
        with lock:
            f.write(json.dumps(row) + "\n")
            f.flush()
json.dump(spend, open(ledger, "w"))
print(f"[r20-generate done] {outf} spend ${spend['usd']:.2f}", flush=True)
