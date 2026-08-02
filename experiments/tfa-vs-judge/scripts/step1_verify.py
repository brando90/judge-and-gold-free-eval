# Critic pass on the Step-1 yardstick result, plus the low-ground-truth subsampling check.
# Threats tested: (1) circularity of the cc anchor, (2) model confound in the surface nuisance,
# (3) ceiling / degenerate within-correct variance, (4) overfitting (in-sample vs cross-validated R2).
# Then (5): can the certificate be estimated from a SMALL correctness anchor (the low-GT claim)?
import json, glob, numpy as np
from judge_nuisance import DATASETS, load_cc, load, surface_features

def r2(y, Xcols):
    X = np.column_stack([np.ones(len(y))] + Xcols)
    b, *_ = np.linalg.lstsq(X, y, rcond=None); p = X @ b
    sr = ((y - p) ** 2).sum(); st = ((y - y.mean()) ** 2).sum()
    return 0.0 if st == 0 else 1 - sr / st

def cv_r2(y, Xcols, k=5, seed=0):
    n = len(y)
    if n < k * 4: return float("nan")
    idx = np.random.RandomState(seed).permutation(n); folds = np.array_split(idx, k)
    X = np.column_stack([np.ones(n)] + Xcols); pred = np.empty(n)
    for f in folds:
        tr = np.setdiff1d(np.arange(n), f)
        b, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None); pred[f] = X[f] @ b
    sr = ((y - pred) ** 2).sum(); st = ((y - y.mean()) ** 2).sum()
    return 0.0 if st == 0 else 1 - sr / st

def dummies(models):
    u = sorted(set(models))
    return [np.array([1.0 if m == uu else 0.0 for m in models]) for uu in u[1:]]  # drop first

# ---------- gather ----------
CELLS = {}   # (dataset, judge) -> dict of arrays
for name, globs, scores_file in DATASETS:
    cc = load_cc(scores_file)
    recs_by_judge, seen, matched = load(globs, cc)
    for judge, recs in recs_by_judge.items():
        y = np.array([float(r["judge_score"]) for r in recs], float)
        tfa = np.array([float(r["tfa_argmax"]) for r in recs], float)
        c = np.array([float(r["cc"]) for r in recs], float)
        bx = np.array([float(r.get("boxed_correct", 0)) for r in recs], float)
        surf = np.array([surface_features(r.get("free_gen", "")) for r in recs], float)
        mdl = [r.get("model") for r in recs]
        CELLS[(name, judge.split("/")[-1])] = dict(y=y, tfa=tfa, cc=c, bx=bx, surf=surf, mdl=mdl)

# ---------- (1) circularity: is cc judge-derived? ----------
print("=== (1) cc provenance / non-circularity ===")
print("cc is joined by (model, problem_id), identical across judges (not judge-specific).")
for (name, jl), d in CELLS.items():
    if name == "MATH-500":
        m = np.corrcoef(d["cc"], d["bx"])[0, 1]
        # correlation of cc with the judge score, for context (should be high but cc != judge)
        js = np.corrcoef(d["cc"], d["y"])[0, 1]
        print(f"  {name} {jl:16s}: corr(cc, boxed_correct)={m:+.2f}   corr(cc, judge_score)={js:+.2f}   cc mean={d['cc'].mean():.2f}")

# ---------- (2)-(4) robustness of the within-correct surface nuisance ----------
print("\n=== (2)-(4) within-correct surface nuisance: robustness ===")
hdr = f"{'dataset':9s} {'judge':16s} {'nCorr':>5s} {'yStd':>5s} {'%ceil':>6s} {'surfIS':>7s} {'surfCV':>7s} {'surf|model(CV)':>14s} {'lenCV':>6s}"
print(hdr); print("-" * len(hdr))
verdict = {}
for (name, jl), d in CELLS.items():
    mask = d["cc"] == 1
    y = d["y"][mask]
    if mask.sum() < 40 or y.std() == 0:
        print(f"{name:9s} {jl:16s} {int(mask.sum()):5d}   (too few / no variance)"); continue
    surf = d["surf"][mask]; surf = (surf - surf.mean(0)) / (surf.std(0) + 1e-9)
    scols = [surf[:, i] for i in range(surf.shape[1])]
    mdl = [m for m, k in zip(d["mdl"], mask) if k]
    dcols = dummies(mdl)
    pct_ceil = float((y == y.max()).mean())
    surf_is = r2(y, scols)
    surf_cv = cv_r2(y, scols)
    len_cv = cv_r2(y, [surf[:, 0]])
    # surface partial beyond model fixed effects, cross-validated
    r_m = cv_r2(y, dcols) if dcols else 0.0
    r_ms = cv_r2(y, dcols + scols) if dcols else surf_cv
    surf_given_model = max(0.0, (r_ms - r_m)) if not (np.isnan(r_ms) or np.isnan(r_m)) else float("nan")
    verdict[(name, jl)] = dict(surf_cv=surf_cv, surf_given_model=surf_given_model, pct_ceil=pct_ceil, n=int(mask.sum()))
    print(f"{name:9s} {jl:16s} {int(mask.sum()):5d} {y.std():5.2f} {100*pct_ceil:5.0f}% "
          f"{100*surf_is:6.1f}% {100*surf_cv:6.1f}% {100*surf_given_model:13.1f}% {100*len_cv:5.1f}%")

print("\n  surfIS = in-sample R2; surfCV = 5-fold cross-validated; surf|model(CV) = CV surface variance")
print("  beyond solver-model fixed effects; lenCV = CV length-only. Claims must survive surfCV and surf|model.")

# ---- save verified (CV, model-controlled) metrics for the figure ----
def verified(d, which):
    score = d["y"] if which == "judge_score" else d["tfa"]
    quality = r2(score, [d["cc"]])
    mask = d["cc"] == 1
    out = {"quality": quality, "n_correct": int(mask.sum())}
    if mask.sum() >= 40 and score[mask].std() > 0:
        s = d["surf"][mask]; s = (s - s.mean(0)) / (s.std(0) + 1e-9)
        scols = [s[:, i] for i in range(s.shape[1])]
        out["surface_cv"] = cv_r2(score[mask], scols)
        mdl = [m for m, k in zip(d["mdl"], mask) if k]; dc = dummies(mdl)
        out["surface_given_model"] = max(0.0, cv_r2(score[mask], dc + scols) - cv_r2(score[mask], dc)) if dc else out["surface_cv"]
        out["pct_ceil"] = float((score[mask] == score[mask].max()).mean())
    return out

VER = {}
for (name, jl), d in CELLS.items():
    VER.setdefault(name, {})[jl] = {"judge_score": verified(d, "judge_score"), "tfa_argmax": verified(d, "tfa_argmax")}
json.dump(VER, open("runs/step1_verified.json", "w"), indent=2)
print("wrote runs/step1_verified.json (CV, model-controlled)")

# ---------- (5) low-ground-truth: estimate the certificate from a small anchor ----------
print("\n=== (5) subsampling: estimate certificate from k correctness labels ===")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
KS = [20, 50, 100, 200, 400]; B = 300
panels = [("MATH-500", "gpt-5.2"), ("MATH-500", "claude-opus-4-8"),
          ("GSM8K", "gpt-5.2"), ("GSM8K", "claude-opus-4-8")]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
for (name, jl) in panels:
    d = CELLS[(name, jl)]; y = d["y"]; c = d["cc"]
    surf = (d["surf"] - d["surf"].mean(0)) / (d["surf"].std(0) + 1e-9)
    full_q = r2(y, [c])
    mask = c == 1; ys = y[mask]; ss = surf[mask]; scols_full = [ss[:, i] for i in range(ss.shape[1])]
    full_s = r2(ys, scols_full)
    rng = np.random.RandomState(0)
    mq, sq, ms, sss = [], [], [], []
    for k in KS:
        qv, sv = [], []
        for _ in range(B):
            idx = rng.choice(len(y), size=min(k, len(y)), replace=False)
            qv.append(r2(y[idx], [c[idx]]))
            cm = c[idx] == 1
            if cm.sum() >= 8:
                sub = surf[idx][cm]
                sv.append(r2(y[idx][cm], [sub[:, i] for i in range(sub.shape[1])]))
        mq.append(np.mean(qv)); sq.append(np.std(qv))
        ms.append(np.mean(sv) if sv else np.nan); sss.append(np.std(sv) if sv else np.nan)
    lab = f"{name} {'GPT' if 'gpt' in jl else 'Opus'}"
    axes[0].errorbar(KS, [100*v for v in mq], yerr=[100*v for v in sq], marker="o", capsize=3, label=lab)
    axes[0].axhline(100*full_q, ls=":", lw=0.8, color="gray")
    axes[1].errorbar(KS, [100*v for v in ms], yerr=[100*v for v in sss], marker="o", capsize=3, label=lab)
    axes[1].axhline(100*full_s, ls=":", lw=0.8, color="gray")
    print(f"  {lab:14s} quality full={100*full_q:5.1f}%  est@100={100*mq[2]:5.1f}%±{100*sq[2]:.1f}   "
          f"surface full={100*full_s:5.1f}%  est@100={100*ms[2]:5.1f}%±{100*sss[2]:.1f}")
axes[0].set_title("Quality signal vs anchor size"); axes[1].set_title("Within-correct surface vs anchor size")
for a in axes:
    a.set_xlabel("number of correctness labels (anchor size k)"); a.set_ylabel("% variance"); a.set_xscale("log")
    a.legend(fontsize=8, frameon=False); a.grid(color="#eee")
fig.tight_layout(); fig.savefig("paper/figs/fig_step1_subsample.png", dpi=150)
print("\nwrote paper/figs/fig_step1_subsample.png")
