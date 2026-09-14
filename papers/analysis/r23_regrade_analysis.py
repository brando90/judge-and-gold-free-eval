# PRE-SPECIFIED producer for R23-A (papers/D-iclr/registration_round23.md); committed before any R23 call.
# Run from experiments/tfa-vs-judge:
#   python ../../papers/analysis/r23_regrade_analysis.py --grader sonnet --orig runs/r20/leaderboard_sonnet_api/pool.jsonl \
#       --regrade runs/r23/regrade_sonnet_api/pool.jsonl --draw2 runs/r22/redraw_sonnet_api/pool.jsonl --out ../../papers/analysis/r23a_regrade_sonnet.json
# Same-reference regrade against a second reference draw, on the same answers (a score of 7 or above counts as correct). Questions: those
# of runs/r22/redraw_pool.jsonl whose blind, original referenced, regrade referenced and second-draw referenced calls are all scored for
# all four answers. Question-level bootstrap, 2,000 resamples, seed 0, paired across conditions.
import argparse
import itertools
import json

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--grader", required=True)
ap.add_argument("--orig", required=True)
ap.add_argument("--regrade", required=True)
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


S0, S1, S2 = scores(args.orig), scores(args.regrade), scores(args.draw2)
pool = [json.loads(l) for l in open("runs/r22/redraw_pool.jsonl")]
G = pool[0]["generators"]
rows = [t for t in pool if all((t["problem_id"], i, "noref") in S0 and (t["problem_id"], i, "ref") in S0 and (t["problem_id"], i, "ref") in S1
                               and (t["problem_id"], i, "ref") in S2 for i in t["idx"])]
n = len(rows)


def mat(S):
    return np.array([[S[(t["problem_id"], i, "ref")] >= T for i in range(len(G))] for t in rows], float)


orc = np.array([[t["oracle"][i] for i in range(len(G))] for t in rows], float)
r0, r1, r2 = mat(S0), mat(S1), mat(S2)
stop = np.array([[bool(t["oracle"][i]) and t["group_draw1"][i] == "match" and t["group"][i] != "match" for i in range(len(G))] for t in rows], float)
start = np.array([[bool(t["oracle"][i]) and t["group"][i] == "match" and t["group_draw1"][i] != "match" for i in range(len(G))] for t in rows], float)
rng = np.random.default_rng(0)
boots = [rng.integers(0, n, n) for _ in range(NB)]


def ci(x):
    m = [x[b].mean() for b in boots]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)]]


def masked(mask, val):  # mean of val over masked answers, question bootstrap
    def f(idx):
        d = mask[idx].sum()
        return float((mask[idx] * val[idx]).sum() / d) if d else np.nan
    m = [f(b) for b in boots]
    return [round(f(np.arange(n)), 4), [round(float(np.nanpercentile(m, 2.5)), 4), round(float(np.nanpercentile(m, 97.5)), 4)], int(mask.sum())]


res = {"grader": args.grader, "questions": n, "threshold": T, "generators": {}}
for i, g in enumerate(G):
    res["generators"][g] = dict(accuracy_answer_list=ci(orc[:, i]), ref_original=ci(r0[:, i]), ref_regrade=ci(r1[:, i]), ref_draw2=ci(r2[:, i]),
                                same_draw_change=ci(r1[:, i] - r0[:, i]), between_draw_change=ci(r2[:, i] - r0[:, i]))
res["pooled"] = dict(same_draw_change=ci((r1 - r0).mean(1)), between_draw_change=ci((r2 - r0).mean(1)),
                     stop_credited_original=masked(stop, r0), stop_credited_regrade=masked(stop, r1), stop_credited_draw2=masked(stop, r2),
                     stop_regrade_minus_draw2=masked(stop, r1 - r2),
                     start_credited_original=masked(start, r0), start_credited_regrade=masked(start, r1), start_credited_draw2=masked(start, r2),
                     start_draw2_minus_regrade=masked(start, r2 - r1))
h, l_ = G.index("claude-haiku-4-5-20251001"), G.index("meta-llama__Llama-3.1-8B-Instruct")
gap = {k: m_[:, h] - m_[:, l_] for k, m_ in (("answer_list", orc), ("original", r0), ("regrade", r1), ("draw2", r2))}
res["haiku_minus_llama"] = {**{k: ci(v) for k, v in gap.items()}, "same_draw_change": ci(gap["regrade"] - gap["original"]),
                            "between_draw_change": ci(gap["draw2"] - gap["original"])}
means = {k: m_.mean(0) for k, m_ in (("original", r0), ("regrade", r1), ("draw2", r2))}
flips = {"regrade": 0, "draw2": 0}
for a, b in itertools.combinations(range(len(G)), 2):
    base = np.sign(means["original"][a] - means["original"][b])
    for k in flips:
        if np.sign(means[k][a] - means[k][b]) != base:
            flips[k] += 1
res["pairwise_order_flips_of_6"] = flips
p = res["pooled"]
res["predictions"] = {
    "P-R23A1 regrade within 3 points (point)": "confirmed" if abs(p["same_draw_change"][0]) <= 0.03 else "falsified",
    "P-R23A2 stop-matching: regrade credits more than draw 2 (point)": "confirmed" if p["stop_regrade_minus_draw2"][0] > 0 else "falsified",
    "P-R23A3 start-matching: draw 2 credits more than regrade (point)": "confirmed" if p["start_draw2_minus_regrade"][0] > 0 else "falsified",
}
json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res, indent=1))
