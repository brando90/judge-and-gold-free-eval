# Frozen-judge scoring of DPO eval generations: both audited GPT-5.2 rubrics (honest ref and
# sabotage), rep a, same escore machinery as bon_judge_gpt.py. Judges are FROZEN: identical
# rubrics and model as the audited configurations, so score gains are comparable to the audit.
# Cost-gated against the shared spend ledger.
import argparse, json, math, os, re
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--policy", choices=["base", "ref", "sabotage"], required=True)
ap.add_argument("--judge-cond", choices=["ref", "sabotage"], required=True)
ap.add_argument("--price-in", type=float, default=1.75)
ap.add_argument("--price-out", type=float, default=14.0)
ap.add_argument("--out", default="runs/dpo")
args = ap.parse_args()
MODEL = "gpt-5.2"
SPEND_F = "runs/bon_scores/gpt_spend.json"
spent = json.load(open(SPEND_F))["usd"] if os.path.exists(SPEND_F) else 0.0
if spent >= 180:
    raise SystemExit(f"HARD STOP: cumulative GPT spend ${spent:.2f} >= $180")

import sys
sys.path.insert(0, "scripts")
from bon_rubrics import RUBRIC

out = f"{args.out}/scores_{args.policy}__judge_{args.judge_cond}.jsonl"
tmap = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/bon_math_tasks.jsonl")}
rows = [json.loads(l) for l in open(f"{args.out}/eval_{args.policy}.jsonl")]
done = set()
if os.path.exists(out):
    done = {json.loads(l)["problem_id"] for l in open(out)}
rows = [r for r in rows if r["problem_id"] not in done]
print(f"[dpo_judge] {len(rows)} items, policy={args.policy} judge={args.judge_cond}, "
      f"spent ${spent:.2f}", flush=True)

from openai import OpenAI
client = OpenAI()
usage = {"in": 0, "out": 0}


def build(r, s):
    sysm = RUBRIC[(args.judge_cond, "a")]
    t = tmap[r["problem_id"]]
    parts = [f"Problem:\n{t['problem']}"]
    if args.judge_cond == "ref":
        parts.append(f"Reference solution (trusted):\n{t['solution']}")
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
            logprobs=True, top_logprobs=5, timeout=120))
    with ThreadPoolExecutor(max_workers=8) as ex:
        esc = list(ex.map(one, r["samples"]))
    return dict(problem_id=r["problem_id"], split=r["split"], escore=esc)


with open(out, "a") as f:
    for i, r in enumerate(rows):
        f.write(json.dumps(grade_item(r)) + "\n"); f.flush()
        cost = usage["in"] / 1e6 * args.price_in + usage["out"] / 1e6 * args.price_out
        if (i + 1) % 20 == 0:
            print(f"[dpo_judge] {i+1}/{len(rows)} run-cost ${cost:.2f}", flush=True)
        if spent + cost >= 180:
            print("HARD STOP mid-run"); break
cost = usage["in"] / 1e6 * args.price_in + usage["out"] / 1e6 * args.price_out
json.dump({"usd": spent + cost}, open(SPEND_F, "w"))
print(f"[dpo_judge done] {out} run ${cost:.2f} cumulative ${spent+cost:.2f}", flush=True)
