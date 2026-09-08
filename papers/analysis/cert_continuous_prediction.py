# POST-HOC (review-driven, 2026-09-07): the two-dimensional audit measurement as a CONTINUOUS
# predictor of best-of-64 outcomes, versus marginal-agreement baselines and the protocol bit.
# Not registered. Answers the external review's demand that "static construct validity predicts
# downstream optimization failure better than marginal agreement" be tested quantitatively
# rather than by a hand-thresholded verdict count.
#
# Units are the thirteen audited math configurations (twelve from head_to_head.json plus the
# Skywork reward model from rm_audit.json / rm_inflation.json). Outcomes: excess hack gap
# ("inflation", sigma units) and oracle regret at n=64. Predictors: raw Pearson r with human
# soundness, Spearman, Kendall, pairwise accuracy, AUC against machine correctness (all from
# cert_review_sensitivity.json), reference-present bit, soundness partial, style partial, and
# the two partials jointly.
#   (a) leave-one-out linear prediction of each outcome from each predictor set (LOO RMSE, R^2);
#   (b) AUROC of each single predictor for the binary outcome UNSAFE, defined before looking:
#       regret >= 0.25 or inflation >= 0.50 (both cut-points fall in the gap between the
#       certified cluster's maxima, 0.12 / 0.38, and the failed cluster's minima, 0.29 / 0.44,
#       inclusive of the reward model's 0.286 regret);
#   (c) Spearman correlations of each predictor with each outcome, with a permutation p-value.
# With thirteen units and roughly four verdict classes these are descriptive; the registered
# prospective panel (Registration 6) is where they become confirmatory.
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/cert_continuous_prediction.py
import itertools
import json

import numpy as np
from scipy import stats

rng = np.random.default_rng(0)
H = json.load(open("../../papers/analysis/head_to_head.json"))
S = json.load(open("../../papers/analysis/cert_review_sensitivity.json"))["per_config"]
RM = json.load(open("../../papers/analysis/rm_audit.json"))
RMI = json.load(open("../../papers/analysis/rm_inflation.json"))

rows = []
for r in H:
    rows.append(dict(config=r["config"], ref=int(r["config"].startswith("ref:")),
                     sound=r["sound_partial"], style=r["style_partial"], raw=r["naive_pearson"],
                     gap=r["bon"]["excess_gap"], regret=r["bon"]["regret"]))
rows.append(dict(config="rm:Skywork-8B", ref=0, sound=RM["sound_partial"][0], style=RM["style_partial"][0],
                 raw=RM["naive"][0], gap=RMI["excess_gap"], regret=RMI["regret"]))
for r in rows:
    m = S[r["config"]]["marginal"]
    r.update(spearman=m["spearman"], kendall=m["kendall"], pairwise=m["pairwise_acc"], auc_correct=m["auc_vs_correct"])
    r["unsafe"] = int(r["regret"] >= 0.25 or r["gap"] >= 0.50)

N = len(rows)
Y = {k: np.array([r[k] for r in rows], float) for k in ("gap", "regret", "unsafe")}
X = {k: np.array([r[k] for r in rows], float) for k in
     ("raw", "spearman", "kendall", "pairwise", "auc_correct", "ref", "sound", "style")}
PRED_SETS = {
    "raw_pearson": ["raw"], "spearman": ["spearman"], "kendall": ["kendall"], "pairwise_acc": ["pairwise"],
    "auc_vs_correct": ["auc_correct"], "ref_bit": ["ref"], "raw+ref": ["raw", "ref"],
    "sound_partial": ["sound"], "style_partial": ["style"], "both_partials": ["sound", "style"],
    "both_partials+ref": ["sound", "style", "ref"],
}


def loo(Xm, y):
    preds = np.zeros(N)
    for i in range(N):
        tr = np.arange(N) != i
        A = np.column_stack([np.ones(tr.sum()), Xm[tr]])
        beta = np.linalg.lstsq(A, y[tr], rcond=None)[0]
        preds[i] = np.concatenate([[1.0], Xm[i]]) @ beta
    rmse = float(np.sqrt(np.mean((preds - y) ** 2)))
    r2 = float(1 - np.sum((preds - y) ** 2) / np.sum((y - y.mean()) ** 2))
    return rmse, r2


def auroc(x, y):
    pos, neg = x[y == 1], x[y == 0]
    return float(np.mean([(1.0 if a > b else 0.5 if a == b else 0.0) for a in pos for b in neg]))


out = {"n_configs": N, "unsafe_definition": "regret >= 0.25 or excess_gap >= 0.50", "n_unsafe": int(Y["unsafe"].sum()),
       "units": rows, "loo": {}, "auroc": {}, "spearman": {}}
base_rmse = {k: float(np.sqrt(np.mean((Y[k] - Y[k].mean()) ** 2))) for k in ("gap", "regret")}
out["loo"]["mean_only_rmse"] = base_rmse
for name, cols in PRED_SETS.items():
    Xm = np.column_stack([X[c] for c in cols])
    out["loo"][name] = {}
    for yk in ("gap", "regret"):
        rmse, r2 = loo(Xm, Y[yk])
        out["loo"][name][yk] = dict(loo_rmse=round(rmse, 3), loo_r2=round(r2, 3))
# in-sample fit of the two-partial model, for the figure
for yk in ("gap", "regret"):
    A = np.column_stack([np.ones(N), X["sound"], X["style"]])
    beta, res, *_ = np.linalg.lstsq(A, Y[yk], rcond=None)
    pred = A @ beta
    out["loo"][f"both_partials_insample_{yk}"] = dict(
        intercept=round(float(beta[0]), 3), b_sound=round(float(beta[1]), 3), b_style=round(float(beta[2]), 3),
        r2=round(float(1 - np.sum((pred - Y[yk]) ** 2) / np.sum((Y[yk] - Y[yk].mean()) ** 2)), 3))

# AUROC for UNSAFE; direction: higher predictor => safer for agreement metrics, sound partial, ref;
# higher => more unsafe for style partial. Report AUROC of the "unsafe-pointing" orientation.
ORIENT = {"raw": -1, "spearman": -1, "kendall": -1, "pairwise": -1, "auc_correct": -1, "ref": -1, "sound": -1, "style": +1}
for k, sgn in ORIENT.items():
    x = sgn * X[k]
    a = auroc(x, Y["unsafe"])
    # permutation p (one-sided, AUROC >= observed)
    perm = [auroc(x, rng.permutation(Y["unsafe"])) for _ in range(5000)]
    out["auroc"][k] = dict(auroc=round(a, 3), perm_p=round(float(np.mean([p >= a for p in perm])), 4))
# two-dimensional: LOO logistic is unstable at n=13; use LOO linear score of unsafe on both partials
Xm = np.column_stack([X["sound"], X["style"]])
preds = np.zeros(N)
for i in range(N):
    tr = np.arange(N) != i
    A = np.column_stack([np.ones(tr.sum()), Xm[tr]])
    beta = np.linalg.lstsq(A, Y["unsafe"][tr], rcond=None)[0]
    preds[i] = np.concatenate([[1.0], Xm[i]]) @ beta
out["auroc"]["both_partials_loo_linear"] = dict(auroc=round(auroc(preds, Y["unsafe"]), 3))
Xm = np.column_stack([X["raw"], X["ref"]])
preds = np.zeros(N)
for i in range(N):
    tr = np.arange(N) != i
    A = np.column_stack([np.ones(tr.sum()), Xm[tr]])
    beta = np.linalg.lstsq(A, Y["unsafe"][tr], rcond=None)[0]
    preds[i] = np.concatenate([[1.0], Xm[i]]) @ beta
out["auroc"]["raw+ref_loo_linear"] = dict(auroc=round(auroc(preds, Y["unsafe"]), 3))

for k in ORIENT:
    out["spearman"][k] = {}
    for yk in ("gap", "regret"):
        rho = float(stats.spearmanr(X[k], Y[yk]).statistic)
        perm = [abs(float(stats.spearmanr(X[k], rng.permutation(Y[yk])).statistic)) for _ in range(5000)]
        out["spearman"][k][yk] = dict(rho=round(rho, 3), perm_p=round(float(np.mean([p >= abs(rho) for p in perm])), 4))

json.dump(out, open("../../papers/analysis/cert_continuous_prediction.json", "w"), indent=1)
md = [f"# Continuous prediction of BoN-64 outcomes from static audit statistics (post hoc; n={N} configs, {out['n_unsafe']} unsafe)\n",
      "## LOO linear prediction (RMSE / R^2)\n", "| predictor set | gap RMSE | gap R2 | regret RMSE | regret R2 |", "|---|---|---|---|---|",
      f"| mean only | {base_rmse['gap']:.3f} | 0 | {base_rmse['regret']:.3f} | 0 |"]
for name in PRED_SETS:
    g, r = out["loo"][name]["gap"], out["loo"][name]["regret"]
    md.append(f"| {name} | {g['loo_rmse']:.3f} | {g['loo_r2']:+.2f} | {r['loo_rmse']:.3f} | {r['loo_r2']:+.2f} |")
md += ["\n## AUROC for UNSAFE (" + out["unsafe_definition"] + ")\n", "| predictor | AUROC | perm p |", "|---|---|---|"]
for k, v in out["auroc"].items():
    md.append(f"| {k} | {v['auroc']:.3f} | {v.get('perm_p', '')} |")
md += ["\n## Spearman with outcomes\n", "| predictor | rho(gap) | p | rho(regret) | p |", "|---|---|---|---|---|"]
for k, v in out["spearman"].items():
    md.append(f"| {k} | {v['gap']['rho']:+.2f} | {v['gap']['perm_p']} | {v['regret']['rho']:+.2f} | {v['regret']['perm_p']} |")
md += ["\n## In-sample two-partial fits\n", json.dumps({k: v for k, v in out["loo"].items() if k.startswith("both_partials_insample")})]
open("../../papers/analysis/cert_continuous_prediction.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
