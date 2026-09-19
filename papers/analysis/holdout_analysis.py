# FROZEN analysis for REGISTRATION 32 -- the holdout rotation replication (H32-1..H32-5).
# Committed together with papers/D-iclr-v6/registration_round32.md BEFORE any judging call
# against runs/bon/bon_holdoutrot__*.jsonl. The commit timestamp is the registration.
#
# Why. The rotation results in the paper all come from one 120-item pool. Reviewer 1 asked for
# one completely locked holdout whose hypotheses, metrics, thresholds and verdict rule are fixed
# before any data exists. This is that run, on 110 items with ZERO parameter overlap with the
# frozen pool (digitsum contributes 14 of them; its space is largely exhausted -- see the
# registration, which registers the imbalance rather than reusing seen items).
#
# Everything below the JUDGES/paths block is byte-identical to replrot_analysis.py except the
# two added endpoints H32-4 and H32-5, which are computed from the SAME per-item arrays as
# H32-1..H32-3 and add no new estimator.
#
# H32-1 gainers  > 0, CI excludes zero, all 4 judge x rubric cells
# H32-2 losers   < 0, CI excludes zero, all 4 cells
# H32-3 gainer - placebo > 0, CI excludes zero, all 4 cells
# H32-4 |placebo mean| <= 0.5 in all 4 cells          (specificity bound; new to this round)
# H32-5 gainer mean >= +2.0 in all 4 cells            (magnitude; guards the "3 to 5 points" range)
#
# Verdict rule: confirmed = interval excludes zero in the predicted direction (H32-1..3) or the
# stated bound holds (H32-4, H32-5); not confirmed = interval includes zero or bound not met;
# falsified = interval excludes zero in the OPPOSITE direction. A hypothesis is confirmed only
# if all four cells are; split if some are; falsified if any cell is falsified.
# Run ONCE, after judging completes, and reported whatever it says.
import json
import os
import re

import numpy as np

NBOOT = 1000
rng = np.random.default_rng(0)
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
POOL_F = "runs/bon/bon_holdoutrot__NousResearch__Meta-Llama-3.1-8B-Instruct.jsonl"
ORIG_DIR, ROT_DIR = "runs/bon_scores_holdout", "runs/bon_scores_holdoutrot"


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + 7, 1
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


def load(sdir, judge, cond, rep):
    f = f"{sdir}/synthk__{judge}__{cond}_{rep}.jsonl"
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))}


pool = [json.loads(l) for l in open(POOL_F)]
need = [(j, rep) for j in JUDGES for rep in ("a", "b")]
if any(load(ROT_DIR, j, "ref", rep) is None for j, rep in need):
    print("[holdout_analysis] pre-data: rotated score files not all present. Nothing written.")
    raise SystemExit


def cluster_ci(per_item):
    v = np.asarray(per_item, float)
    boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return float(v.mean()), [float(np.percentile(boots, 2.5)),
                             float(np.percentile(boots, 97.5))], len(v)


res = {}
md = ["| judge | rubric | gainers [CI] (n items) | losers [CI] | placebo [CI] | "
      "gainer-minus-placebo [CI] |", "|---|---|---|---|---|---|"]
for j in JUDGES:
    for rep in ("a", "b"):
        orig = load(ORIG_DIR, j, "ref", rep)
        rot = load(ROT_DIR, j, "ref", rep)
        g_items, l_items, p_items, gp_items = [], [], [], []
        for it in pool:
            pid = it["problem_id"]
            if pid not in orig or pid not in rot:
                continue
            rotn, orign = norm(it["ref_answer"]), norm(it["rot_from"])
            g, lo, pl = [], [], []
            for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
                if not ok:
                    continue
                b = norm(extract_boxed(s) or s)
                d = rot[pid][i] - orig[pid][i]
                if b == rotn:
                    g.append(d)
                elif b == orign:
                    lo.append(d)
                else:
                    pl.append(d)
            if g:
                g_items.append(float(np.mean(g)))
            if lo:
                l_items.append(float(np.mean(lo)))
            if pl:
                p_items.append(float(np.mean(pl)))
            if g and pl:
                gp_items.append(float(np.mean(g)) - float(np.mean(pl)))
        gm, gci, gn = cluster_ci(g_items)
        lm, lci, ln = cluster_ci(l_items)
        pm, pci, pn = cluster_ci(p_items)
        gpm, gpci, gpn = cluster_ci(gp_items)
        res[f"{j}__{rep}"] = dict(
            gainers=dict(mean=gm, ci=gci, n_items=gn),
            losers=dict(mean=lm, ci=lci, n_items=ln),
            placebo=dict(mean=pm, ci=pci, n_items=pn),
            gainer_minus_placebo=dict(mean=gpm, ci=gpci, n_items=gpn),
            P_RR1=bool(gci[0] > 0), P_RR2=bool(lci[1] < 0), P_RR3=bool(gpci[0] > 0),
            H32_4=bool(abs(pm) <= 0.5), H32_5=bool(gm >= 2.0))
        md.append(f"| {j} | {rep} | {gm:+.2f} [{gci[0]:+.2f},{gci[1]:+.2f}] ({gn}) | "
                  f"{lm:+.2f} [{lci[0]:+.2f},{lci[1]:+.2f}] ({ln}) | "
                  f"{pm:+.2f} [{pci[0]:+.2f},{pci[1]:+.2f}] ({pn}) | "
                  f"{gpm:+.2f} [{gpci[0]:+.2f},{gpci[1]:+.2f}] ({gpn}) |")

cells = [res[k] for k in res]
verdict = dict(
    H32_1_gainers_all4=all(c["P_RR1"] for c in cells),
    H32_2_losers_all4=all(c["P_RR2"] for c in cells),
    H32_3_specificity_all4=all(c["P_RR3"] for c in cells),
    H32_4_placebo_bound_all4=all(c["H32_4"] for c in cells),
    H32_5_magnitude_all4=all(c["H32_5"] for c in cells))
res["verdicts"] = verdict
json.dump(res, open("../../papers/analysis/holdout_results.json"
                    if os.path.exists("../../papers/analysis") else "holdout_results.json",
                    "w"), indent=1)
print("\n".join(md))
print("verdicts:", verdict)
