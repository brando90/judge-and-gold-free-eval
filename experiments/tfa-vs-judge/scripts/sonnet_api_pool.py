# R8-A, Amendment 1 (papers/D-iclr/registration_round8.md): Claude Sonnet 5 through the Anthropic Messages API, score-only
# (rubric a, thinking disabled), blind and referenced, on the R8-A candidate subsamples. Same prompts and call order as
# sonnet_cli_pool.py. Resumable; spend capped. Run from experiments/tfa-vs-judge.
# R19 (papers/D-iclr/registration_round19.md) reuses it with --model and --thinking; the defaults reproduce R8-A exactly.
import argparse
import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import anthropic

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC_TIES

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--cap-usd", type=float, default=40.0)
ap.add_argument("--model", default="claude-sonnet-5")
ap.add_argument("--price-in", type=float, default=2.00, help="USD per million input tokens (spend ledger only)")
ap.add_argument("--price-out", type=float, default=10.00, help="USD per million output tokens (spend ledger only)")
ap.add_argument("--thinking", choices=("disabled", "adaptive"), default="disabled")
ap.add_argument("--max-tokens", type=int, default=512)
args = ap.parse_args()

MODEL = args.model
PRICE_IN, PRICE_OUT = args.price_in / 1e6, args.price_out / 1e6
outf = os.path.abspath(args.out)
os.makedirs(os.path.dirname(outf), exist_ok=True)
ledger = os.path.join(os.path.dirname(outf), "spend.json")


def load_key():
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k
    for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.env")):
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"\'')
    raise SystemExit("no ANTHROPIC_API_KEY")


client = anthropic.Anthropic(api_key=load_key(), max_retries=6)
lock = threading.Lock()
spend = json.load(open(ledger)) if os.path.exists(ledger) else {"usd": 0.0, "calls": 0}


def parse(text):
    m = re.findall(r"\b(10|[0-9])\b", text)
    return float(m[-1]) if m else None


def one(job):
    t, j, cond = job
    with lock:
        if spend["usd"] >= args.cap_usd:
            return None
    user = f"Problem:\n{t['question']}\n\n"
    if cond == "ref":
        user += f"Reference answer (trusted):\n{t['ref']}\n\n"
    user += f"Candidate solution:\n{t['samples'][j]}\n\nScore:"
    row = dict(problem_id=t["problem_id"], idx=t["idx"][j], cond=cond, interface="api")
    if MODEL != "claude-sonnet-5" or args.thinking != "disabled":
        row.update(model=MODEL, thinking=args.thinking)
    try:
        r = client.messages.create(model=MODEL, max_tokens=args.max_tokens, thinking={"type": args.thinking},
                                   system=RUBRIC_TIES[(cond, "a")], messages=[{"role": "user", "content": user}])
        text = "".join(b.text for b in r.content if b.type == "text")
        row.update(score=parse(text), stop_reason=r.stop_reason, input_tokens=r.usage.input_tokens,
                   output_tokens=r.usage.output_tokens, tail=text[-200:])
        with lock:
            spend["usd"] += r.usage.input_tokens * PRICE_IN + r.usage.output_tokens * PRICE_OUT
            spend["calls"] += 1
    except anthropic.APIError as e:
        row.update(score=None, error=f"{type(e).__name__}: {str(e)[:200]}")
    return row


done = set()
if os.path.exists(outf):
    for l in open(outf):
        r = json.loads(l)
        if not r.get("error"):
            done.add((r["problem_id"], r["idx"], r["cond"]))
pool = [json.loads(l) for l in open(args.pool)]
jobs = [(t, j, c) for t in pool for j in range(len(t["samples"])) for c in ("noref", "ref")
        if (t["problem_id"], t["idx"][j], c) not in done]
print(f"[api-pool {MODEL} thinking={args.thinking} {os.path.basename(args.pool)}] {len(jobs)} calls, spend so far ${spend['usd']:.2f}", flush=True)
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
                print(f"  {i + 1}/{len(jobs)} unparseable/errors {n_bad} spend ${spend['usd']:.2f}", flush=True)
json.dump(spend, open(ledger, "w"))
print(f"[api-pool done] {outf} unparseable/errors={n_bad} spend ${spend['usd']:.2f}"
      + (" (CAP REACHED)" if spend["usd"] >= args.cap_usd else ""), flush=True)
