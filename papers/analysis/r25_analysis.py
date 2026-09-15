# PRE-SPECIFIED producer for R25 (papers/D-iclr-v2/registration_round25.md); committed before any R25 call.
# Run from experiments/tfa-vs-judge:
#   python ../../papers/analysis/r25_analysis.py --cell <template>_<judge> --scores runs/r25/<cell>/pool.jsonl --out ../../papers/analysis/r25_<cell>.json
# On runs/r20/mace_gen/pool.jsonl, questions whose four answers are scored blind and with the reference: pooled and per-model accuracy
# (10 = correct) blind, with the reference, and by the answer list; the credited share of correct answers that differ from the
# reference, of those that match it, and of wrong answers, blind and with the reference. Question bootstrap, 2,000 resamples, seed 0.
import argparse
import json

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--cell", required=True)
ap.add_argument("--scores", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

S = {}
for line in open(args.scores):
    r = json.loads(line)
    if r.get("score") is not None and not r.get("error"):
        S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
pool = [json.loads(l) for l in open("runs/r20/mace_gen/pool.jsonl")]
rows = [t for t in pool if all((t["problem_id"], i, c) in S for i in t["idx"] for c in ("noref", "ref"))]
n = len(rows)
rng = np.random.default_rng(0)
boots = [rng.integers(0, n, n) for _ in range(2000)]


def ci(x):
    x = np.asarray(x, float)
    m = [x[b].mean() for b in boots]
    return [round(float(x.mean()), 6), [round(float(np.percentile(m, 2.5)), 6), round(float(np.percentile(m, 97.5)), 6)]]


def masked(mask, val):
    def f(ix):
        d = mask[ix].sum()
        return float((mask[ix] * val[ix]).sum() / d) if d else np.nan
    m = [f(b) for b in boots]
    return [round(f(np.arange(n)), 6), [round(float(np.nanpercentile(m, 2.5)), 6), round(float(np.nanpercentile(m, 97.5)), 6)], int(mask.sum())]


B = np.array([[S[(t["problem_id"], i, "noref")] >= 7 for i in t["idx"]] for t in rows], float)
R = np.array([[S[(t["problem_id"], i, "ref")] >= 7 for i in t["idx"]] for t in rows], float)
O = np.array([t["oracle"] for t in rows], float)
NM = np.array([[o == 1 and g == "nonmatch" for o, g in zip(t["oracle"], t["group"])] for t in rows], float)
MT = np.array([[o == 1 and g == "match" for o, g in zip(t["oracle"], t["group"])] for t in rows], float)
W = 1 - O
res = dict(cell=args.cell, questions=n, generators={})
for k, g in enumerate(pool[0]["generators"]):
    res["generators"][g] = dict(list=ci(O[:, k]), blind=ci(B[:, k]), ref=ci(R[:, k]))
P = dict(blind_minus_list=ci((B - O).mean(1)), ref_minus_list=ci((R - O).mean(1)), ref_minus_blind=ci((R - B).mean(1)))
for name, mask in (("nonmatch_correct", NM), ("match_correct", MT), ("wrong", W)):
    P[f"{name}_credited_blind"] = masked(mask, B)
    P[f"{name}_credited_ref"] = masked(mask, R)
    P[f"{name}_credited_ref_minus_blind"] = masked(mask, R - B)
res["pooled"] = P
if n >= 100:
    res["predictions"] = {
        "P-R25A1 ref below list (interval)": ("confirmed" if P["ref_minus_list"][1][1] < 0 else
                                              "falsified" if P["ref_minus_list"][1][0] > 0 else "not confirmed"),
        "P-R25A2 blind within 5 points of list (point)": "confirmed" if abs(P["blind_minus_list"][0]) <= 0.05 else "falsified",
        "P-R25A3 differing-correct credit ref minus blind <= -10 pp (point)":
            "confirmed" if P["nonmatch_correct_credited_ref_minus_blind"][0] <= -0.10 else "falsified",
    }
else:
    res["predictions"] = "not scored (fewer than 100 complete questions)"
json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res["predictions"], indent=1))
