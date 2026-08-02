# Validate the certificate against ground-truth ACCURACY (the user's check), no new compute.
# The surface-nuisance is estimated WITHOUT labels (regress score on surface features), so testing the
# de-surfaced ("non-nuisance") signal against accuracy is an independent validation:
#   - a good judge: removing surface should NOT lower its agreement with accuracy (surface was orthogonal
#     to truth), so corr(non-nuisance, acc) ~= corr(raw, acc).
#   - a surface-shortcut judge: agreement with accuracy DROPS after removing surface (it was leaning on
#     surface to guess correctness), and/or the surface component itself correlates with accuracy.
# We report pooled and model-controlled (partial, given solver model) correlations, with bootstrap CIs.
import json, numpy as np
from judge_nuisance import DATASETS, load_cc, load, surface_features
RNG = np.random.RandomState(0)

def resid(x, cols):
    if not cols: return x - x.mean()
    X = np.column_stack([np.ones(len(x))] + cols)
    b, *_ = np.linalg.lstsq(X, x, rcond=None)
    return x - X @ b

def corr(a, b):
    if a.std() == 0 or b.std() == 0: return 0.0
    return float(np.corrcoef(a, b)[0, 1])

def dummies(models):
    u = sorted(set(models)); return [np.array([1.0 if m == uu else 0.0 for m in models]) for uu in u[1:]]

def boot_corr(a, b, B=1000):
    n = len(a); v = np.empty(B)
    for i in range(B):
        s = RNG.randint(0, n, n); v[i] = corr(a[s], b[s])
    return np.percentile(v, [2.5, 97.5])

print("Agreement with ground-truth accuracy, before vs after removing the (label-free) surface component")
print("partial = controlling for solver model.  [.] = bootstrap 95% CI on the pooled correlation.\n")
hdr = f"{'dataset':9s} {'judge':16s} {'ev':6s} {'corr(raw,acc)':>18s} {'corr(nonNuis,acc)':>18s} {'corr(surface,acc)':>18s}  partial: raw/nonNuis"
print(hdr); print("-" * len(hdr))
OUT = {}
for name, globs, sf in DATASETS:
    cc = load_cc(sf); recs_by_judge, *_ = load(globs, cc)
    for judge, recs in recs_by_judge.items():
        jl = judge.split("/")[-1]
        acc = np.array([float(r["cc"]) for r in recs])
        surf = np.array([surface_features(r.get("free_gen", "")) for r in recs])
        surf = (surf - surf.mean(0)) / (surf.std(0) + 1e-9)
        scols = [surf[:, i] for i in range(surf.shape[1])]
        mdl = [r.get("model") for r in recs]; dc = dummies(mdl)
        for ev, key in (("judge", "judge_score"), ("tfa", "tfa_argmax")):
            S = np.array([float(r[key]) for r in recs])
            nonnuis = resid(S, scols)                     # remove label-free surface component
            surface_part = S - S.mean() - nonnuis         # the surface-explained component
            c_raw, c_nn, c_sf = corr(S, acc), corr(nonnuis, acc), corr(surface_part, acc)
            ci_raw = boot_corr(S, acc); ci_nn = boot_corr(nonnuis, acc)
            # model-controlled partial correlations
            acc_m = resid(acc, dc); pc_raw = corr(resid(S, dc), acc_m); pc_nn = corr(resid(nonnuis, dc), acc_m)
            OUT.setdefault(name, {}).setdefault(jl, {})[ev] = dict(
                raw=c_raw, nonnuis=c_nn, surface=c_sf, partial_raw=pc_raw, partial_nonnuis=pc_nn)
            print(f"{name:9s} {jl:16s} {ev:6s} {c_raw:6.2f} [{ci_raw[0]:5.2f},{ci_raw[1]:5.2f}] "
                  f"{c_nn:6.2f} [{ci_nn[0]:5.2f},{ci_nn[1]:5.2f}] {c_sf:16.2f}   {pc_raw:5.2f} / {pc_nn:5.2f}")
    print()
json.dump(OUT, open("runs/step1_accuracy_check.json", "w"), indent=2)
print("wrote runs/step1_accuracy_check.json")
