# PRE-SPECIFIED producer for R21-A (papers/D-iclr/registration_round21.md); committed before any R21 call.
# Run from experiments/tfa-vs-judge:
#   python ../../papers/analysis/r21_leaderboard_maxrule.py --scores runs/r21/leaderboard_opus_api/pool.jsonl --out ../../papers/analysis/r21a_maxrule_opus.json
# The benchmark study of R20-C under the max rule: an answer counts as correct when max(blind score, referenced score) is at or above
# the threshold (default 7). Per generator: max-rule accuracy and its difference from answer-list accuracy; pooled over generators:
# the difference. Question-level bootstrap (2,000 resamples, seed 0), as in r20_leaderboard_analysis.py.
import argparse
import json

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--scores", required=True)
ap.add_argument("--pool", default="runs/r20/mace_gen/pool.jsonl")
ap.add_argument("--out", required=True)
ap.add_argument("--threshold", type=int, default=7)
args = ap.parse_args()

pool = [json.loads(l) for l in open(args.pool)]
S = {}
for l in open(args.scores):
    r = json.loads(l)
    if r.get("score") is not None and not r.get("error"):
        S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
G = pool[0]["generators"]
rows = [t for t in pool if all((t["problem_id"], i, c) in S for i in t["idx"] for c in ("noref", "ref"))]
n = len(rows)
orc = np.array([[t["oracle"][i] for i in range(len(G))] for t in rows], float)
mx = np.array([[max(S[(t["problem_id"], i, "noref")], S[(t["problem_id"], i, "ref")]) >= args.threshold for i in range(len(G))] for t in rows], float)
rng = np.random.default_rng(0)
bs = [rng.integers(0, n, n) for _ in range(2000)]


def ci(x):
    m = [x[b].mean() for b in bs]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)]]


res = {"questions": n, "threshold": args.threshold,
       "generators": {g: dict(accuracy_max_rule=ci(mx[:, i]), max_minus_list=ci(mx[:, i] - orc[:, i])) for i, g in enumerate(G)},
       "pooled_max_minus_list": ci((mx - orc).mean(1))}
json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res, indent=1))
