# PRE-SPECIFIED producer for R20-C (papers/D-iclr/registration_round20.md); committed before any R20 call.
# Run from experiments/tfa-vs-judge:
#   python ../../papers/analysis/r20_leaderboard_analysis.py --scores runs/r20/leaderboard_sonnet_api/pool.jsonl --out ../../papers/analysis/r20c_leaderboard.json
# Per generator, accuracy on MACE questions with several correct answers under three graders: the answer list (oracle), the judge
# blind (score >= 7 counts as correct), and the judge with the reference (score >= 7). Also: the referenced judge's undercount
# (referenced minus answer-list accuracy), the share of the generator's correct answers that differ from the reference, the
# false-rejection rate (correct answers scored 3 or below) for non-matching and matching correct answers under each condition, and
# the generator ranking under each grader. Intervals: question-level bootstrap (2,000 resamples, seed 0), paired across graders.
import argparse
import json

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--scores", required=True)
ap.add_argument("--pool", default="runs/r20/mace_gen/pool.jsonl")
ap.add_argument("--out", required=True)
ap.add_argument("--threshold", type=int, default=7, help="R21: scores at or above count as correct; default 7 reproduces R20-C")
args = ap.parse_args()
THRESH, NB = args.threshold, 2000

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
bl = np.array([[S[(t["problem_id"], i, "noref")] >= THRESH for i in range(len(G))] for t in rows], float)
rf = np.array([[S[(t["problem_id"], i, "ref")] >= THRESH for i in range(len(G))] for t in rows], float)
rng = np.random.default_rng(0)
boots = [rng.integers(0, n, n) for _ in range(NB)]


def ci(x):
    m = [x[b].mean() for b in boots]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)]]


res = {"questions": n, "threshold": THRESH, "generators": {}}
for i, g in enumerate(G):
    grp = [t["group"][i] for t in rows]
    nm = [j for j, x in enumerate(grp) if x == "nonmatch"]
    mt = [j for j, x in enumerate(grp) if x == "match"]
    fr = lambda cond, idxs: round(float(np.mean([S[(rows[j]["problem_id"], i, cond)] <= 3 for j in idxs])), 4) if idxs else None
    res["generators"][g] = dict(
        accuracy_answer_list=ci(orc[:, i]), accuracy_blind=ci(bl[:, i]), accuracy_referenced=ci(rf[:, i]),
        undercount_referenced_minus_list=ci(rf[:, i] - orc[:, i]), blind_minus_list=ci(bl[:, i] - orc[:, i]),
        correct=int(orc[:, i].sum()), correct_nonmatching=len(nm), share_correct_nonmatching=round(len(nm) / max(orc[:, i].sum(), 1), 4),
        false_rejection_nonmatch_blind=fr("noref", nm), false_rejection_nonmatch_ref=fr("ref", nm),
        false_rejection_match_blind=fr("noref", mt), false_rejection_match_ref=fr("ref", mt))
for key, mat in (("answer_list", orc), ("blind", bl), ("referenced", rf)):
    res[f"ranking_{key}"] = [G[j] for j in np.argsort(-mat.mean(0), kind="stable")]
nm_all = [(j, i) for j, t in enumerate(rows) for i in range(len(G)) if t["group"][i] == "nonmatch"]
mt_all = [(j, i) for j, t in enumerate(rows) for i in range(len(G)) if t["group"][i] == "match"]
res["pooled"] = dict(
    false_rejection_nonmatch_blind=round(float(np.mean([S[(rows[j]["problem_id"], i, "noref")] <= 3 for j, i in nm_all])), 4) if nm_all else None,
    false_rejection_nonmatch_ref=round(float(np.mean([S[(rows[j]["problem_id"], i, "ref")] <= 3 for j, i in nm_all])), 4) if nm_all else None,
    false_rejection_match_ref=round(float(np.mean([S[(rows[j]["problem_id"], i, "ref")] <= 3 for j, i in mt_all])), 4) if mt_all else None,
    undercount_referenced_minus_list=ci((rf - orc).mean(1)), blind_minus_list=ci((bl - orc).mean(1)))
json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res, indent=1))
