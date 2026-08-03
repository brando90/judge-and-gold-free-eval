# Step 2 probe on existing data: does a judge's reliability (agreement with ground-truth correctness)
# DEGRADE as the solver gets more capable? A stronger solver's errors are rarer and subtler, so we expect
# the judge to have a harder time telling correct from incorrect -- the capability-gap degradation curve.
# We measure, per (judge, dataset, solver model): solver capability = mean(cc), and judge reliability =
# corr(judge_score, cc) across that model's items. Then we fit reliability vs capability. Honest caveat:
# our judges (GPT-5.2, Opus) are far stronger than the Qwen solvers (0.5-14B), so this is the
# error-subtlety form of the gap, not the solver-outgrows-overseer regime.
import json, glob, collections, numpy as np
from judge_nuisance import DATASETS, load_cc, load

def corr(a, b):
    a, b = np.array(a, float), np.array(b, float)
    return np.nan if a.std() == 0 or b.std() == 0 else float(np.corrcoef(a, b)[0, 1])

def size_of(model):
    import re
    m = re.search(r"(\d+\.?\d*)B", model or "")
    return float(m.group(1)) if m else np.nan

rows = []
for name, globs, sf in DATASETS:
    cc = load_cc(sf)
    recs_by_judge, *_ = load(globs, cc)
    for judge, recs in recs_by_judge.items():
        jl = judge.split("/")[-1]
        by_model = collections.defaultdict(list)
        for r in recs:
            by_model[r.get("model")].append(r)
        for mdl, rs in by_model.items():
            y = np.array([float(r["judge_score"]) for r in rs])
            c = np.array([float(r["cc"]) for r in rs])
            nptot, ncorr = len(c), int(c.sum())
            if nptot < 30 or c.std() == 0:  # need both classes present
                continue
            rows.append(dict(judge=jl, dataset=name, model=mdl, size=size_of(mdl),
                             n=nptot, acc=float(c.mean()), agree=corr(y, c)))

# ---- table ----
print(f"{'judge':16s} {'dataset':9s} {'model':34s} {'sizeB':>6s} {'n':>4s} {'acc':>5s} {'agree(r)':>8s}")
print("-" * 92)
for r in sorted(rows, key=lambda r: (r["judge"], r["dataset"], r["size"] if not np.isnan(r["size"]) else 0)):
    print(f"{r['judge']:16s} {r['dataset']:9s} {r['model'].split('/')[-1]:34s} "
          f"{r['size']:6.1f} {r['n']:4d} {r['acc']:5.2f} {r['agree']:8.2f}")

# ---- degradation fit: reliability vs solver capability (acc), pooled per judge ----
print("\nDegradation of judge reliability as solver capability (acc) rises:")
print("(negative slope = judge gets worse at telling correct from incorrect on stronger solvers)")
J = collections.defaultdict(list)
for r in rows:
    if not np.isnan(r["agree"]):
        J[r["judge"]].append((r["acc"], r["agree"], r["dataset"], r["n"]))
out = {}
for judge, pts in sorted(J.items()):
    acc = np.array([p[0] for p in pts]); agr = np.array([p[1] for p in pts])
    if len(pts) >= 4 and acc.std() > 0:
        slope, inter = np.polyfit(acc, agr, 1)
        r_pearson = corr(acc, agr)
        out[judge] = dict(slope=slope, r=r_pearson, n_cells=len(pts))
        print(f"  {judge:16s}: agree ~ {slope:+.2f}*acc + {inter:.2f}   corr(acc,agree)={r_pearson:+.2f}  ({len(pts)} cells)")

# within-dataset (controls difficulty): reliability vs solver size on the hardest set
print("\nWithin-dataset reliability vs solver size (difficulty held fixed):")
for name in ("MATH-500", "GSM8K", "Putnam"):
    for judge in sorted(set(r["judge"] for r in rows)):
        pts = sorted([(r["size"], r["agree"]) for r in rows
                      if r["dataset"] == name and r["judge"] == judge and not np.isnan(r["agree"]) and not np.isnan(r["size"])])
        if len(pts) >= 4:
            sz = np.log2([p[0] for p in pts]); ag = np.array([p[1] for p in pts])
            slope = np.polyfit(sz, ag, 1)[0]
            trend = " ".join(f"{a:+.2f}" for _, a in pts)
            print(f"  {name:9s} {judge:16s}: r-by-size [{trend}]  slope/log2size={slope:+.3f}")

json.dump({"rows": rows, "degradation": out}, open("runs/step2_reliability.json", "w"), indent=2, default=str)
print("\nwrote runs/step2_reliability.json")
