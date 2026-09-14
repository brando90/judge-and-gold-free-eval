# PRE-SPECIFIED producer for R22-B (papers/D-iclr/registration_round22.md); committed before any R22 call.
# Run from experiments/tfa-vs-judge:
#   python ../../papers/analysis/r22_redraw_analysis.py --grader sonnet --draw1 runs/r20/leaderboard_sonnet_api/pool.jsonl \
#       --draw2 runs/r22/redraw_sonnet_api/pool.jsonl --out ../../papers/analysis/r22b_redraw_sonnet.json
# Compares referenced grading under the first and second reference draws on the same answers (a score of 7 or above counts as
# correct). Questions: those in runs/r22/redraw_pool.jsonl with blind and both referenced calls scored for all four answers.
# Readouts (question-level bootstrap, 2,000 resamples, seed 0, paired): per model and pooled, second-draw referenced accuracy minus
# answer-list accuracy, and second-draw minus first-draw referenced accuracy; "losers" (correct answers that match the first
# reference but not the second) and "gainers" (match the second but not the first): share credited under each draw and the
# difference; rankings under each draw; Haiku 4.5 minus Llama-3.1-8B accuracy under the list, blind, and each draw.
import argparse
import json

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--grader", required=True)
ap.add_argument("--draw1", required=True)
ap.add_argument("--draw2", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()
T, NB = 7, 2000


def scores(f):
    S = {}
    for l in open(f):
        r = json.loads(l)
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    return S


S1, S2 = scores(args.draw1), scores(args.draw2)
pool = [json.loads(l) for l in open("runs/r22/redraw_pool.jsonl")]
G = pool[0]["generators"]
rows = [t for t in pool if all((t["problem_id"], i, "noref") in S1 and (t["problem_id"], i, "ref") in S1 and (t["problem_id"], i, "ref") in S2
                               for i in t["idx"])]
n = len(rows)
orc = np.array([[t["oracle"][i] for i in range(len(G))] for t in rows], float)
bl = np.array([[S1[(t["problem_id"], i, "noref")] >= T for i in range(len(G))] for t in rows], float)
r1 = np.array([[S1[(t["problem_id"], i, "ref")] >= T for i in range(len(G))] for t in rows], float)
r2 = np.array([[S2[(t["problem_id"], i, "ref")] >= T for i in range(len(G))] for t in rows], float)
lose = np.array([[t["oracle"][i] and t["group_draw1"][i] == "match" and t["group"][i] != "match" for i in range(len(G))] for t in rows], float)
gain = np.array([[t["oracle"][i] and t["group"][i] == "match" and t["group_draw1"][i] != "match" for i in range(len(G))] for t in rows], float)
rng = np.random.default_rng(0)
boots = [rng.integers(0, n, n) for _ in range(NB)]


def ci(x):
    m = [x[b].mean() for b in boots]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)]]


def ratio(mask, cred):  # share credited among masked answers, question bootstrap
    def val(idx):
        d = mask[idx].sum()
        return float((mask[idx] * cred[idx]).sum() / d) if d else np.nan
    m = [val(b) for b in boots]
    return [round(val(np.arange(n)), 4), [round(float(np.nanpercentile(m, 2.5)), 4), round(float(np.nanpercentile(m, 97.5)), 4)], int(mask.sum())]


def ratio_diff(mask, a, b):
    def val(idx):
        d = mask[idx].sum()
        return float((mask[idx] * (a[idx] - b[idx])).sum() / d) if d else np.nan
    m = [val(bb) for bb in boots]
    return [round(val(np.arange(n)), 4), [round(float(np.nanpercentile(m, 2.5)), 4), round(float(np.nanpercentile(m, 97.5)), 4)], int(mask.sum())]


res = {"grader": args.grader, "questions": n, "threshold": T, "generators": {}}
for i, g in enumerate(G):
    res["generators"][g] = dict(accuracy_answer_list=ci(orc[:, i]), accuracy_blind=ci(bl[:, i]), accuracy_ref_draw1=ci(r1[:, i]),
                                accuracy_ref_draw2=ci(r2[:, i]), draw2_minus_list=ci(r2[:, i] - orc[:, i]), draw2_minus_draw1=ci(r2[:, i] - r1[:, i]))
res["pooled"] = dict(draw2_minus_list=ci((r2 - orc).mean(1)), draw1_minus_list=ci((r1 - orc).mean(1)), draw2_minus_draw1=ci((r2 - r1).mean(1)),
                     losers_credited_draw1=ratio(lose, r1), losers_credited_draw2=ratio(lose, r2), losers_draw2_minus_draw1=ratio_diff(lose, r2, r1),
                     gainers_credited_draw1=ratio(gain, r1), gainers_credited_draw2=ratio(gain, r2), gainers_draw2_minus_draw1=ratio_diff(gain, r2, r1))
for key, mat in (("answer_list", orc), ("blind", bl), ("ref_draw1", r1), ("ref_draw2", r2)):
    res[f"ranking_{key}"] = [G[j] for j in np.argsort(-mat.mean(0), kind="stable")]
h, l_ = G.index("claude-haiku-4-5-20251001"), G.index("meta-llama__Llama-3.1-8B-Instruct")
res["haiku_minus_llama"] = {k: ci(mat[:, h] - mat[:, l_]) for k, mat in (("answer_list", orc), ("blind", bl), ("ref_draw1", r1), ("ref_draw2", r2))}
p = res["pooled"]
res["predictions"] = {
    "P-R22B1 draw-2 referenced below list (interval)": "confirmed" if p["draw2_minus_list"][1][1] < 0 else ("falsified" if p["draw2_minus_list"][1][0] > 0 else "not confirmed"),
    "P-R22B2 losers credited less under draw 2 (point)": "confirmed" if p["losers_draw2_minus_draw1"][0] < 0 else "falsified",
    "P-R22B3 gainers credited more under draw 2 (point)": "confirmed" if p["gainers_draw2_minus_draw1"][0] > 0 else "falsified",
}
json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res, indent=1))
