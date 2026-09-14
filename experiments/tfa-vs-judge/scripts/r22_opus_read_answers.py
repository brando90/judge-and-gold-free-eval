# R22-A harness (papers/D-iclr/registration_round22.md): Claude Opus 5 reads the sampled unboxed replies of
# runs/r22/label_sample.jsonl and reports the final answer each commits to, with the extraction prompt of
# scripts/r8_extract_answers.py verbatim. Messages API, thinking disabled, default temperature (Amendment 1), 200 output tokens. Resumable; spend capped.
# Run from experiments/tfa-vs-judge. Output: runs/r22/opus_read.jsonl rows {pool, problem_id, idx, answer, stop_reason}.
import argparse
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import anthropic

ap = argparse.ArgumentParser()
ap.add_argument("--sample", default="runs/r22/label_sample.jsonl")
ap.add_argument("--out", default="runs/r22/opus_read.jsonl")
ap.add_argument("--model", default="claude-opus-5")
ap.add_argument("--cap-usd", type=float, default=10.0)
ap.add_argument("--workers", type=int, default=8)
args = ap.parse_args()
SYSTEM = "You read a reply to a question and report the final answer the reply commits to. You do not solve the question."
USER = ("Question:\n{q}\n\nReply:\n{r}\n\n"
        "What final answer does the reply commit to? If it commits to one answer, write only that answer: a number, or "
        "numbers separated by commas. If it gives no final answer, or ends with several different answers, write NONE.")
PRICE_IN, PRICE_OUT = 15 / 1e6, 75 / 1e6  # conservative ledger prices


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
spend = {"usd": 0.0, "calls": 0}
done = set()
if os.path.exists(args.out):
    for l in open(args.out):
        r = json.loads(l)
        if not r.get("error"):
            done.add((r["problem_id"], r["idx"]))
jobs = [r for r in map(json.loads, open(args.sample)) if (r["problem_id"], r["idx"]) not in done]
print(f"[r22 read {args.model}] {len(jobs)} replies", flush=True)


def one(r):
    with lock:
        if spend["usd"] >= args.cap_usd:
            return None
    row = dict(pool=r["pool"], problem_id=r["problem_id"], idx=r["idx"])
    try:
        m = client.messages.create(model=args.model, max_tokens=200, thinking={"type": "disabled"}, system=SYSTEM,
                                   messages=[{"role": "user", "content": USER.format(q=r["question"], r=r["reply"])}])
        row.update(answer="".join(b.text for b in m.content if b.type == "text").strip(), stop_reason=m.stop_reason)
        with lock:
            spend["usd"] += m.usage.input_tokens * PRICE_IN + m.usage.output_tokens * PRICE_OUT
            spend["calls"] += 1
    except anthropic.APIError as e:
        row.update(answer=None, error=f"{type(e).__name__}: {str(e)[:200]}")
    return row


with open(args.out, "a") as f, ThreadPoolExecutor(args.workers) as ex:
    for row in ex.map(one, jobs):
        if row is not None:
            f.write(json.dumps(row) + "\n")
            f.flush()
json.dump(spend, open(os.path.join(os.path.dirname(os.path.abspath(args.out)), "spend_read.json"), "w"))
print(f"[r22 read done] spend ${spend['usd']:.2f}", flush=True)
