# Tie-handling ablation (registered prediction, committed pre-run): re-judge the math BoN pool
# with GPT-5.2 on a 0-100 scale (referenced, honest). Prediction: finer granularity reduces
# top-ties and cuts oracle regret below the 0-10 scale's 0.117, testing whether
# granularity-beats-scale is a tie artifact rather than a capability statement.
# Local run: set -a; source ../../../veribench/.env; python3 scripts/bon_judge_gpt_scale.py --rep a
import argparse, json, os, re
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--rep", choices=["a", "b"], required=True)
ap.add_argument("--out", default="runs/bon_scores")
args = ap.parse_args()
MODEL = "gpt-5.2"
SPEND_F = f"{args.out}/gpt_spend.json"
spent = json.load(open(SPEND_F))["usd"] if os.path.exists(SPEND_F) else 0.0
if spent >= 200:
    raise SystemExit(f"HARD STOP: ${spent:.2f} >= $200")

RUBRIC = {
    "a": ("You are a strict grader. You are given the problem, a reference solution known to be "
          "correct, and a candidate solution. Rate the candidate's correctness on a scale from 0 "
          "(completely wrong) to 100 (fully correct, every step valid), using the reference to "
          "check it. Use the full scale; reserve 95-100 for flawless work and spread scores so "
          "that better solutions get strictly higher numbers. Judge the mathematics, not the "
          "writing. Respond with only the integer score."),
    "b": ("Compare the candidate solution against the trusted reference solution provided. Score "
          "how correct the candidate's reasoning and final result are, from 0 (entirely "
          "incorrect) to 100 (flawless). Use fine distinctions across the whole range rather "
          "than clustering at the top. Presentation does not matter. Output only a single "
          "number."),
}

pool = [json.loads(l) for l in open("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")]
tmap = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/bon_math_tasks.jsonl")}
for r in pool:
    r.update({k: v for k, v in tmap.get(r["problem_id"], {}).items() if k not in r})
pool = [r for r in pool if "oracle" in r and 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8]
out = f"{args.out}/math__gpt-5.2-scale100__ref_{args.rep}.jsonl"
done = set()
if os.path.exists(out):
    done = {json.loads(l)["problem_id"] for l in open(out)}
pool = [r for r in pool if r["problem_id"] not in done]
print(f"[gpt100] {len(pool)} items rep={args.rep} spent ${spent:.2f}", flush=True)

from openai import OpenAI
client = OpenAI()
usage = {"in": 0, "out": 0}


def build(r, s):
    return [{"role": "system", "content": RUBRIC[args.rep]},
            {"role": "user", "content": f"Problem:\n{r['problem']}\n\nReference solution "
             f"(trusted):\n{r['solution']}\n\nCandidate solution:\n{s[:6000]}\n\nScore:"}]


def one(r, s):
    resp = client.chat.completions.create(model=MODEL, messages=build(r, s),
                                          max_completion_tokens=5, timeout=120)
    usage["in"] += resp.usage.prompt_tokens; usage["out"] += resp.usage.completion_tokens
    m = re.search(r"\d+", resp.choices[0].message.content or "")
    return min(int(m.group()), 100) if m else 50.0


with open(out, "a") as f:
    for i, r in enumerate(pool):
        with ThreadPoolExecutor(max_workers=8) as ex:
            esc = list(ex.map(lambda s: one(r, s), r["samples"]))
        f.write(json.dumps(dict(problem_id=r["problem_id"], escore=esc)) + "\n"); f.flush()
        cost = usage["in"] / 1e6 * 1.75 + usage["out"] / 1e6 * 14.0
        if (i + 1) % 10 == 0:
            print(f"[gpt100] {i+1}/{len(pool)} ${cost:.2f}", flush=True)
cost = usage["in"] / 1e6 * 1.75 + usage["out"] / 1e6 * 14.0
json.dump({"usd": spent + cost}, open(SPEND_F, "w"))
print(f"[gpt100 done] {out} ${cost:.2f} cumulative ${spent+cost:.2f}", flush=True)
