# Confidence hardening for Step 1 (no new compute; re-analysis of data in hand):
#   A. bootstrap 95% CI on the quality signal (variance explained by correctness)
#   B. within-correct surface effect measured as HELD-OUT gain beyond solver-model fixed effects
#      (repeated 70/30 splits): median, 5-95% interval, and fraction of splits where surface helps
#      (a leakage-free, assumption-light significance check). Reported for judges and for TFA.
#   C. feature-set robustness: does the conclusion survive under {length-only, length+words, all 5}?
import json, numpy as np
from judge_nuisance import DATASETS, load_cc, load, surface_features

RNG = np.random.RandomState(0)

def dummies(models):
    u = sorted(set(models))
    return [np.array([1.0 if m == uu else 0.0 for m in models]) for uu in u[1:]]

def test_r2(y, cols, tr, te):
    X = np.column_stack([np.ones(len(y))] + cols)
    b, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None); p = X[te] @ b
    st = ((y[te] - y[te].mean()) ** 2).sum()
    return 0.0 if st == 0 else 1 - ((y[te] - p) ** 2).sum() / st

def heldout_gain(y, base, add, R=500, frac=0.7):
    n = len(y); g = np.empty(R)
    for i in range(R):
        idx = RNG.permutation(n); k = int(frac * n); tr, te = idx[:k], idx[k:]
        g[i] = test_r2(y, base + add, tr, te) - test_r2(y, base, tr, te)
    return dict(median=float(np.median(g)), lo=float(np.percentile(g, 5)),
                hi=float(np.percentile(g, 95)), pos=float((g > 0).mean()))

def boot_quality_ci(y, c, B=1000):
    n = len(y); v = np.empty(B)
    for i in range(B):
        s = RNG.randint(0, n, n); X = np.column_stack([np.ones(n), c[s]])
        b, *_ = np.linalg.lstsq(X, y[s], rcond=None); p = X @ b
        st = ((y[s] - y[s].mean()) ** 2).sum()
        v[i] = 0.0 if st == 0 else 1 - ((y[s] - p) ** 2).sum() / st
    return np.percentile(v, [2.5, 50, 97.5])

# gather
CELLS = {}
for name, globs, sf in DATASETS:
    cc = load_cc(sf); recs_by_judge, *_ = load(globs, cc)
    for judge, recs in recs_by_judge.items():
        CELLS[(name, judge.split("/")[-1])] = dict(
            y=np.array([float(r["judge_score"]) for r in recs]),
            tfa=np.array([float(r["tfa_argmax"]) for r in recs]),
            cc=np.array([float(r["cc"]) for r in recs]),
            surf=np.array([surface_features(r.get("free_gen", "")) for r in recs]),
            mdl=[r.get("model") for r in recs])

FEATS = {"length": [0], "length+words": [0, 1], "all-5": [0, 1, 2, 3, 4]}
OUT = {}
print("=== A. quality signal, bootstrap 95% CI (evaluator=judge) ===")
for (name, jl), d in CELLS.items():
    lo, md, hi = boot_quality_ci(d["y"], d["cc"])
    OUT.setdefault(name, {}).setdefault(jl, {})["quality_ci"] = [lo, md, hi]
    print(f"  {name:9s} {jl:16s}  quality = {100*md:4.1f}%  [{100*lo:4.1f}, {100*hi:4.1f}]")

print("\n=== B. within-correct surface beyond model: held-out gain (median [5,95], %splits>0) ===")
print(f"  {'dataset':9s} {'judge':16s} {'evaluator':10s} {'nCorr':>5s} {'gain':>6s} {'[5,95]':>14s} {'%>0':>5s}")
for (name, jl), d in CELLS.items():
    mask = d["cc"] == 1
    if mask.sum() < 40:
        print(f"  {name:9s} {jl:16s} (nCorr={int(mask.sum())}, skipped)"); continue
    mdl = [m for m, k in zip(d["mdl"], mask) if k]; base = dummies(mdl)
    s = d["surf"][mask]; s = (s - s.mean(0)) / (s.std(0) + 1e-9)
    for ev, arr in (("judge", d["y"]), ("tfa", d["tfa"])):
        y = arr[mask]
        if y.std() == 0: continue
        add = [s[:, i] for i in range(5)]
        r = heldout_gain(y, base if base else [np.zeros(len(y))], add)
        OUT[name][jl].setdefault("surface_beyond_model", {})[ev] = r | {"n": int(mask.sum())}
        print(f"  {name:9s} {jl:16s} {ev:10s} {int(mask.sum()):5d} {100*r['median']:5.1f}% "
              f"[{100*r['lo']:4.1f},{100*r['hi']:4.1f}]  {100*r['pos']:3.0f}%")

print("\n=== C. feature-set robustness (judge, within-correct surface beyond model, median held-out gain) ===")
print(f"  {'dataset':9s} {'judge':16s}" + "".join(f"{fn:>13s}" for fn in FEATS))
for (name, jl), d in CELLS.items():
    mask = d["cc"] == 1
    if mask.sum() < 40: continue
    mdl = [m for m, k in zip(d["mdl"], mask) if k]; base = dummies(mdl)
    s = d["surf"][mask]; s = (s - s.mean(0)) / (s.std(0) + 1e-9)
    y = d["y"][mask]
    if y.std() == 0: continue
    row = ""
    for fn, cols in FEATS.items():
        r = heldout_gain(y, base if base else [np.zeros(len(y))], [s[:, i] for i in cols], R=300)
        row += f"{100*r['median']:11.1f}% "
    print(f"  {name:9s} {jl:16s}{row}")

json.dump(OUT, open("runs/step1_confidence.json", "w"), indent=2)
print("\nwrote runs/step1_confidence.json")
