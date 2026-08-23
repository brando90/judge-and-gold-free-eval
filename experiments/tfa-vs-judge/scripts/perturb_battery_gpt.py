# Frontier arms of the Tier-1 perturbation battery (see perturb_battery.py for the registered
# axis taxonomy and predictions P-B1..P-B4). Scores battery_variants.jsonl with GPT-5.2 under
# the honest referenced rubric and under the sabotage rubric.
import argparse, json, os, re
from concurrent.futures import ThreadPoolExecutor

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC

ap = argparse.ArgumentParser()
ap.add_argument("--cond", choices=["ref", "sabotage"], required=True)
args = ap.parse_args()
SPEND_F = "runs/bon_scores/gpt_spend.json"
spent = json.load(open(SPEND_F))["usd"] if os.path.exists(SPEND_F) else 0.0
if spent >= 200:
    raise SystemExit(f"HARD STOP ${spent:.2f}")
SYS = RUBRIC[(args.cond, "a")]
rows = [json.loads(l) for l in open("human_eval/battery_variants.jsonl")]
out = f"runs/battery_gpt_{args.cond}.jsonl"
done = set()
if os.path.exists(out):
    done = {(json.loads(l)["id"], json.loads(l)["axis"]) for l in open(out)}
rows = [r for r in rows if (r["id"], r["axis"]) not in done]
print(f"[battery-gpt] {len(rows)} to score, cond={args.cond}", flush=True)

from openai import OpenAI
client = OpenAI()
usage = {"in": 0, "out": 0}


def one(r):
    parts = [f"Problem:\n{r['question']}"]
    if args.cond == "ref":
        parts.append(f"Reference solution (trusted):\n{r['gold_solution']}")
    parts.append(f"Candidate solution:\n{r['trace'][:10000]}\n\nScore:")
    resp = client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "system", "content": SYS},
                  {"role": "user", "content": "\n\n".join(parts)}],
        max_completion_tokens=4, timeout=120)
    usage["in"] += resp.usage.prompt_tokens; usage["out"] += resp.usage.completion_tokens
    m = re.search(r"\d+", resp.choices[0].message.content or "")
    return dict(id=r["id"], axis=r["axis"], score=min(int(m.group()), 10) if m else None)


with open(out, "a") as f:
    B = 24
    for i in range(0, len(rows), B):
        with ThreadPoolExecutor(max_workers=8) as ex:
            res = list(ex.map(one, rows[i:i + B]))
        for r in res:
            f.write(json.dumps(r) + "\n")
        f.flush()
        cost = usage["in"] / 1e6 * 1.75 + usage["out"] / 1e6 * 14.0
        print(f"[battery-gpt] {min(i+B,len(rows))}/{len(rows)} ${cost:.2f}", flush=True)
cost = usage["in"] / 1e6 * 1.75 + usage["out"] / 1e6 * 14.0
json.dump({"usd": spent + cost}, open(SPEND_F, "w"))
print(f"[battery-gpt done] {out} ${cost:.2f} cumulative ${spent+cost:.2f}", flush=True)
