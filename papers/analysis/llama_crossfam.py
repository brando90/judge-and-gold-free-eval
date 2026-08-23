# Cross-family generator check for Paper A (registered in the pipeline3 pre-run commit):
# the Qwen ladder judges' pressure outcomes on a Llama-3.1-8B-generated MATH pool.
# If blind-judge gaming on the Qwen pool were self-preference (same-family generator),
# the blind gaps should shrink here; the registered prediction is that the pattern
# replicates (blind gaps large, referenced gaps small). Run from experiments/tfa-vs-judge.
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)

pool = {}
for l in open("runs/bon/bon_math__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" in r and 0.2 <= np.mean(r["oracle"]) <= 0.8:
        pool[r["problem_id"]] = r

out = {}
for jm in ["Qwen2.5-1.5B-Instruct", "Qwen2.5-3B-Instruct", "Qwen2.5-7B-Instruct",
           "Qwen2.5-14B-Instruct"]:
    for cond in ("noref", "ref"):
        sa = {json.loads(l)["problem_id"]: json.loads(l)["escore"]
              for l in open(f"runs/bon_scores_llama/math__Qwen__{jm}__{cond}_a.jsonl")}
        sb = {json.loads(l)["problem_id"]: json.loads(l)["escore"]
              for l in open(f"runs/bon_scores_llama/math__Qwen__{jm}__{cond}_b.jsonl")}
        gaps, regrets = [], []
        for pid, it in pool.items():
            if pid not in sa:
                continue
            curves = ns["per_item_curves"](it, sa[pid], sb[pid])
            null = ns["permutation_null"](it, sa[pid], sb[pid])
            gaps.append(curves[64]["judge_gain"] - curves[64]["true_gain"] - null)
            regrets.append(curves[64]["oracle_regret"])
        gaps = np.array(gaps)
        boot = [float(np.mean(rng.choice(gaps, len(gaps)))) for _ in range(2000)]
        out[f"{jm}__{cond}"] = dict(
            n=len(gaps), excess_gap=round(float(gaps.mean()), 3),
            gap_ci=[round(float(np.percentile(boot, 2.5)), 3),
                    round(float(np.percentile(boot, 97.5)), 3)],
            regret=round(float(np.mean(regrets)), 3))
json.dump(out, open("../../papers/analysis/llama_crossfam.json", "w"), indent=1)
for k, v in out.items():
    print(f"{k:40s} gap {v['excess_gap']:+.2f} [{v['gap_ci'][0]:+.2f},{v['gap_ci'][1]:+.2f}] regret {v['regret']:.3f} n={v['n']}")
