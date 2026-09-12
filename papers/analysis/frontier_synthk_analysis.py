# FROZEN analysis for the frontier-judge synthetic-grid extension (P-FG1).
# INTERNAL REGISTRATION: committed BEFORE any frontier synthk score exists; the commit timestamp
# is the registration.
#
# Why. gpt-4.1's k-stratified-pool k-step (P-FK1) did not confirm (+0.25, CI crossing zero), the
# first place a headline open-judge result failed to reproduce at frontier scale. Two readings are
# open: a genuinely smaller/absent effect at this capability level, or noise from gpt-4.1's
# score-resolution screen failure (ties@max 15.03, mean, against a <=3.0 bar) inflating the
# k-stratified pool's variance. This experiment gives the SAME step statistic a second, cleaner
# shot on the exact pool and estimator that gave the paper's cleanest, most universal open-judge
# result: the synthetic grid's paired step (synthk_paired.py), confirmed for all six open judges
# there (+0.55 to +2.55 SD, every CI excluding zero) where the k-stratified pool's step was only
# individually significant for 3 of 6. Same judge (gpt-4.1, unaffected by the Sonnet 5 incident),
# same pool (runs/bon/bon_synthk__Qwen__Qwen2.5-7B-Instruct.jsonl, 60 items, k in {1,2,4,8,16},
# frozen samples, no new generation), same estimator, mirrored verbatim from synthk_paired.py.
#
# REGISTERED PREDICTION:
#   P-FG1: the paired step (mean per-item ref-minus-blind gap delta at k>1 minus the same delta
#   at k=1) is positive with a 95% item-bootstrap CI excluding zero, matching all six open judges.
#   A null here, on the cleanest available design, would be the strongest evidence yet that the
#   k=2 boundary claim does not extend to this frontier judge rather than being a k-stratified-
#   pool artifact.
#
# Run from experiments/tfa-vs-judge: python3 ../../papers/analysis/frontier_synthk_analysis.py [judge_tag ...]
import json
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)

JUDGES = sys.argv[1:] or ["openai__gpt-4.1-2025-04-14"]
POOL = "runs/bon/bon_synthk__Qwen__Qwen2.5-7B-Instruct.jsonl"


def load(path):
    if not (__import__("os").path.exists(path)):
        return None
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(path)}


def per_item_gaps(pool, sa, sb):
    g = {}
    for it in pool:
        pid = it["problem_id"]
        if pid not in sa or None in sa[pid] or None in sb[pid]:
            continue
        c = ns["per_item_curves"](it, sa[pid], sb[pid])
        nl = ns["permutation_null"](it, sa[pid], sb[pid])
        g[pid] = c[64]["judge_gain"] - c[64]["true_gain"] - nl
    return g


def bci(vals, B=4000):
    v = np.asarray(vals, float)
    if len(v) == 0:
        return None
    b = [float(np.mean(rng.choice(v, len(v)))) for _ in range(B)]
    return dict(mean=round(float(v.mean()), 3), n=len(v),
               ci=[round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)])


pool = [json.loads(l) for l in open(POOL) if "oracle" in json.loads(l)]
out = {"judges": JUDGES, "pool": POOL}
for jtag in JUDGES:
    ra, rb = load(f"runs/bon_scores_synthk/synthk__{jtag}__ref_a.jsonl"), load(f"runs/bon_scores_synthk/synthk__{jtag}__ref_b.jsonl")
    na, nb = load(f"runs/bon_scores_synthk/synthk__{jtag}__noref_a.jsonl"), load(f"runs/bon_scores_synthk/synthk__{jtag}__noref_b.jsonl")
    if any(x is None for x in (ra, rb, na, nb)):
        out[f"{jtag}"] = "score files missing"
        continue
    gr, gn = per_item_gaps(pool, ra, rb), per_item_gaps(pool, na, nb)
    pids = sorted(set(gr) & set(gn))
    k_of = {it["problem_id"]: it["k"] for it in pool}
    d1 = [gr[p] - gn[p] for p in pids if k_of[p] == 1]
    dg = [gr[p] - gn[p] for p in pids if k_of[p] > 1]
    d1_ci, dg_ci = bci(d1), bci(dg)
    boot = [float(np.mean(rng.choice(dg, len(dg))) - np.mean(rng.choice(d1, len(d1)))) for _ in range(4000)]
    step_ci = [round(float(np.percentile(boot, 2.5)), 3), round(float(np.percentile(boot, 97.5)), 3)]
    out[f"{jtag}__k1"] = d1_ci
    out[f"{jtag}__kgt1"] = dg_ci
    out[f"{jtag}__step"] = dict(mean=round(float(np.mean(dg) - np.mean(d1)), 3), ci=step_ci,
                                n_k1=len(d1), n_kgt1=len(dg), P_FG1=bool(step_ci[0] > 0))

json.dump(out, open("../../papers/analysis/frontier_synthk_results.json", "w"), indent=1)
for k, v in out.items():
    print(k, json.dumps(v) if not isinstance(v, str) else v)
