# GPT frontier arms for validity-under-pressure Phase 0. Same pre-registered machinery as
# bon_judge.py: escore = expected value over 0..10 from top_logprobs at the score position;
# A/B rubric paraphrases as replicates. Cost-gated: --pilot measures $/call on 5 items and
# exits; every run appends usage to runs/bon_scores/gpt_spend.json and hard-stops at $90.
import argparse, json, math, os, re
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--cond", choices=["noref", "ref", "sabotage"], required=True)
ap.add_argument("--rep", choices=["a", "b"], required=True)
ap.add_argument("--pilot", action="store_true")
ap.add_argument("--price-in", type=float, default=1.75, help="$/M input tokens")
ap.add_argument("--price-out", type=float, default=14.0, help="$/M output tokens")
ap.add_argument("--out", default="runs/bon_scores")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
MODEL = "gpt-5.2"
SPEND_F = f"{args.out}/gpt_spend.json"
spent = json.load(open(SPEND_F))["usd"] if os.path.exists(SPEND_F) else 0.0
if spent >= 90:
    raise SystemExit(f"HARD STOP: cumulative GPT spend ${spent:.2f} >= $90")

import sys
sys.path.insert(0, "scripts")
from bon_rubrics import RUBRIC

pool = [json.loads(l) for l in open(args.pool)]
pool = [r for r in pool if "oracle" in r and 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8]
if args.pilot:
    pool = pool[:5]
out = f"{args.out}/math__gpt-5.2__{args.cond}_{args.rep}{'_pilot' if args.pilot else ''}.jsonl"
done = set()
if os.path.exists(out):
    done = {json.loads(l)["problem_id"] for l in open(out)}
pool = [r for r in pool if r["problem_id"] not in done]
print(f"[gpt] {len(pool)} items, cond={args.cond}_{args.rep}, spent so far ${spent:.2f}", flush=True)

from openai import OpenAI
client = OpenAI()
usage = {"in": 0, "out": 0}


def build(r, s):
    sysm = RUBRIC[(args.cond, args.rep)]
    parts = [f"Problem:\n{r['problem']}"]
    if args.cond == "ref":
        parts.append(f"Reference solution (trusted):\n{r['solution']}")
    parts.append(f"Candidate solution:\n{s[:6000]}\n\nScore:")
    return [{"role": "system", "content": sysm}, {"role": "user", "content": "\n\n".join(parts)}]


def escore_of(resp):
    ch = resp.choices[0]
    usage["in"] += resp.usage.prompt_tokens; usage["out"] += resp.usage.completion_tokens
    try:
        top = ch.logprobs.content[0].top_logprobs
        num = den = 0.0
        for t in top:
            m = re.fullmatch(r"\s?(\d|10)", t.token)
            if m:
                p = math.exp(t.logprob)
                num += p * int(m.group(1)); den += p
        if den >= 0.25:
            return num / den
    except Exception:
        pass
    m = re.search(r"\d+", ch.message.content or "")
    return min(int(m.group()), 10) if m else 5.0


def grade_item(r):
    def one(s):
        return escore_of(client.chat.completions.create(
            model=MODEL, messages=build(r, s), max_completion_tokens=4,
            logprobs=True, top_logprobs=20, timeout=120))
    with ThreadPoolExecutor(max_workers=8) as ex:
        esc = list(ex.map(one, r["samples"]))
    return dict(problem_id=r["problem_id"], escore=esc)


with open(out, "a") as f:
    for i, r in enumerate(pool):
        row = grade_item(r)
        f.write(json.dumps(row) + "\n"); f.flush()
        cost = usage["in"] / 1e6 * args.price_in + usage["out"] / 1e6 * args.price_out
        if (i + 1) % 10 == 0 or args.pilot:
            print(f"[gpt] {i+1}/{len(pool)} run-cost ${cost:.2f}", flush=True)
        if spent + cost >= 90:
            print(f"HARD STOP mid-run at ${spent+cost:.2f}"); break
cost = usage["in"] / 1e6 * args.price_in + usage["out"] / 1e6 * args.price_out
json.dump({"usd": spent + cost}, open(SPEND_F, "w"))
print(f"[gpt done] {out} run ${cost:.2f} cumulative ${spent+cost:.2f} "
      f"tokens in/out {usage['in']}/{usage['out']}", flush=True)
