# Analysis for the two registered metric ablations (predictions committed pre-run):
#  A) position-weighted TFA sweep — weight reference-token hits by ((pos+1)/n)^gamma.
#     Prediction: late-weighting decays the cross-family model-ranking signal toward the
#     answer-only null (comparison-class metric; the reweighted variance is reference nuisance).
#  B) answer-swap counterfactual support — lp(own boxed answer|prefix) - lp(swapped alt|prefix)
#     under a fixed 7B scorer. Prediction: carries real correctness signal (verification-class).
# Inputs: runs/postok/*.jsonl, runs/answer_swap.jsonl, runs/cc_math500_all.jsonl
import glob, json

import numpy as np


def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


cc = {}
for l in open('runs/cc_math500_all.jsonl'):
    r = json.loads(l); cc[(r['model'], r['problem_id'])] = r['cc']
models_acc = {}
for (m, p), v in cc.items():
    models_acc.setdefault(m, []).append(v)
models_acc = {m: float(np.mean(v)) for m, v in models_acc.items()}

res = {"A_position_weighted_tfa": {}, "B_answer_swap": {}}

data = {}
for fn in glob.glob('runs/postok/*.jsonl'):
    m = fn.split('/')[-1][:-6].replace('__', '/')
    if m in models_acc:
        data[m] = [json.loads(l) for l in open(fn)]
for g in [0, 0.5, 1, 2, 4, 8, 'last16', 'last4']:
    xs, ys = [], []
    for m, rows in data.items():
        vals = []
        for r in rows:
            h = np.array([int(c) for c in r['hits']], float)
            n = len(h)
            if n == 0:
                continue
            if isinstance(g, str):
                k = int(g[4:]); w = np.zeros(n); w[-min(k, n):] = 1
            else:
                w = ((np.arange(n) + 1) / n) ** g
            vals.append((w * h).sum() / w.sum())
        xs.append(np.mean(vals)); ys.append(models_acc[m])
    res["A_position_weighted_tfa"][str(g)] = dict(rho=spearman(xs, ys), n_models=len(xs))
    print(f"A gamma={g!s:6} rho={spearman(xs, ys):+.3f} n={len(xs)}")

sw = [json.loads(l) for l in open('runs/answer_swap.jsonl')]
per_model = {}
for r in sw:
    key = (r['model'], r['problem_id'])
    if key in cc:
        per_model.setdefault(r['model'], []).append((r['support'], cc[key]))
rs = []
for m, pairs in sorted(per_model.items()):
    s, c = zip(*pairs)
    if len(set(c)) < 2:
        continue
    r_ = pearson(s, c); rs.append(r_)
    res["B_answer_swap"][m] = dict(r=r_, n=len(pairs),
                                   support_correct=float(np.mean([x for x, y in pairs if y == 1])),
                                   support_wrong=float(np.mean([x for x, y in pairs if y == 0])))
    print(f"B {m:45s} r={r_:+.3f} n={len(pairs)}")
pos = sum(1 for v in res["B_answer_swap"].values() if v["r"] > 0)
res["B_answer_swap"]["_summary"] = dict(mean_within_model_r=float(np.mean(rs)),
                                        n_models=len(rs), sign_positive=pos)
print(f"B mean within-model r={np.mean(rs):+.3f}, {pos}/{len(rs)} positive")
json.dump(res, open('runs/metric_ablations.json', 'w'), indent=1)
