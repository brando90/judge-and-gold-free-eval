# FROZEN producer for R2-A (papers/D-iclr/registration_round2.md), committed before any M1-math score exists.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r2_math_m1_results.json.
#   P-R2A1: mean(acc_ref - acc_blind) > 0, 95% CI excluding zero, both judges.
#   P-R2A2: mean(acc_M1 - acc_blind) < 0.5 * mean(acc_ref - acc_blind) (point estimates), both judges.
# Selected-answer accuracy: best-of-64 on rubric-a scores, validity averaged over samples tied at the max.
import json
import os

import numpy as np

NBOOT = 1000
POOL = "runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl"
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "Qwen__Qwen2.5-14B-Instruct"]
OUT = "../../papers/analysis/r2_math_m1_results.json"


def load(f, key="escore"):
    if not os.path.exists(f):
        return None
    return {r["problem_id"]: r[key] for r in (json.loads(l) for l in open(f))}


def sel_acc(scores, oracle):
    s = np.asarray(scores, float)
    tie = np.isclose(s, s.max(), rtol=0, atol=1e-9)
    return float(np.asarray(oracle, float)[tie].mean())


def boot(x, seed=0):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)]]


pool = [json.loads(l) for l in open(POOL)]
pool = [r for r in pool if 0.2 <= np.mean(r["oracle"]) <= 0.8]
res = {"n_items": len(pool)}
for j in JUDGES:
    blind = load(f"runs/bon_scores/math__{j}__noref_a.jsonl")
    ref = load(f"runs/bon_scores/math__{j}__ref_a.jsonl")
    m1 = load(f"runs/r2/scores/math__{j}__m1_a.jsonl")
    call1 = load(f"runs/r2/scores/math__{j}__m1_a.jsonl", "blind")
    if m1 is None:
        res[j] = "pre-data"
        continue
    ids = [r["problem_id"] for r in pool if r["problem_id"] in blind and r["problem_id"] in ref and r["problem_id"] in m1]
    orc = {r["problem_id"]: r["oracle"] for r in pool}
    ab = np.array([sel_acc(blind[p], orc[p]) for p in ids])
    ar = np.array([sel_acc(ref[p], orc[p]) for p in ids])
    am = np.array([sel_acc(m1[p], orc[p]) for p in ids])
    d_ref, d_m1, d_m1_ref = boot(ar - ab), boot(am - ab), boot(am - ar)
    agree = float(np.corrcoef(np.concatenate([blind[p] for p in ids]), np.concatenate([call1[p] for p in ids]))[0, 1])
    res[j] = dict(n=len(ids), acc_blind=round(float(ab.mean()), 4), acc_ref=round(float(ar.mean()), 4),
                  acc_m1=round(float(am.mean()), 4), ref_minus_blind=d_ref, m1_minus_blind=d_m1, m1_minus_ref=d_m1_ref,
                  call1_vs_frozen_blind_r=round(agree, 4),
                  P_R2A1=bool(d_ref[1][0] > 0), P_R2A2=bool(d_m1[0] < 0.5 * d_ref[0]))
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
