# RM paraphrase-replicate inflation (registered P-R1 in scripts/rm_paraphrase.py, commit
# 828944a): selection replicate = RM scores of the ORIGINAL samples, reporting replicate =
# RM scores of content-preserving PARAPHRASES of the same samples (index-aligned), so the
# winner's-curse cancellation matches the judge protocol. Same excess-gap estimator as every
# other configuration (bon_analysis machinery). Run from experiments/tfa-vs-judge.
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)

pool = {}
for l in open("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" in r and 0.2 <= np.mean(r["oracle"]) <= 0.8:
        pool[r["problem_id"]] = r
sa = {json.loads(l)["problem_id"]: json.loads(l)["rm_score"]
      for l in open("runs/rm_scores_math.jsonl")}
sb = {json.loads(l)["problem_id"]: json.loads(l)["rm_score"]
      for l in open("runs/rm_scores_math_para.jsonl")}

gaps, regrets = [], []
for pid, it in pool.items():
    if pid not in sa or pid not in sb:
        continue
    curves = ns["per_item_curves"](it, sa[pid], sb[pid])
    null = ns["permutation_null"](it, sa[pid], sb[pid])
    gaps.append(curves[64]["judge_gain"] - curves[64]["true_gain"] - null)
    regrets.append(curves[64]["oracle_regret"])
gaps = np.array(gaps)
boot = [float(np.mean(rng.choice(gaps, len(gaps)))) for _ in range(4000)]
out = dict(n=len(gaps), excess_gap=round(float(gaps.mean()), 3),
           ci=[round(float(np.percentile(boot, 2.5)), 3),
               round(float(np.percentile(boot, 97.5)), 3)],
           regret=round(float(np.mean(regrets)), 3),
           note="selection on original-sample RM scores, reporting on paraphrase-replicate "
                "RM scores; paraphrases by Qwen-7B, content-preserving instruction, seed 1")
json.dump(out, open("../../papers/analysis/rm_inflation.json", "w"), indent=1)
print(json.dumps(out, indent=1))
