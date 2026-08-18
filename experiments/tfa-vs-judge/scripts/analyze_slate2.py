# Slate items 3+4 (registered in docs/async-update-brando-aug17.md before results):
#  C) entropy-normalized TFA (prediction: null — comparison class). Uses runs/tfa_bpc_math500.jsonl
#     (tfa_argmax + bpc_bits per model x item, extracted from free_gen) + runs/cc_math500_all.jsonl.
#  D) prefix-repair curve (prediction: works — verification class). Uses the truncation-fraction
#     completion-success dict V already stored in runs/prm_labelset (14B completer) + the n=80
#     random-stratum human labels (author_1_Sri_random.json).
import ast, json

import numpy as np


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def partial(x, y, z):
    x, y, z = map(lambda a: np.asarray(a, float), (x, y, z))
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return pearson(rx, ry)


res = {}

# C) entropy-normalized TFA
cc = {}
for l in open('runs/cc_math500_all.jsonl'):
    r = json.loads(l); cc[(r['model'], r['problem_id'])] = r['cc']
rows = [json.loads(l) for l in open('runs/tfa_bpc_math500.jsonl')]
rows = [r for r in rows if (r['model'], r['problem_id']) in cc]
for r in rows:
    r['cc'] = cc[(r['model'], r['problem_id'])]
models = sorted({r['model'] for r in rows})
tfa = np.array([r['tfa'] for r in rows]); bpc = np.array([r['bpc'] for r in rows])
A = np.vstack([bpc, np.ones(len(bpc))]).T
beta, *_ = np.linalg.lstsq(A, tfa, rcond=None)
resid = tfa - A @ beta
acc = {m: np.mean([r['cc'] for r in rows if r['model'] == m]) for m in models}
raw = {m: np.mean([r['tfa'] for r in rows if r['model'] == m]) for m in models}
nrm = {m: np.mean([resid[i] for i, r in enumerate(rows) if r['model'] == m]) for m in models}
res['C_entropy_normalized_tfa'] = dict(
    corr_tfa_bpc=pearson(tfa, bpc),
    ranking_rho_raw=spearman([raw[m] for m in models], [acc[m] for m in models]),
    ranking_rho_normalized=spearman([nrm[m] for m in models], [acc[m] for m in models]),
    n_models=len(models))
print("C)", res['C_entropy_normalized_tfa'])

# D) prefix-repair curve
pv = {}
for l in open('runs/prm_labelset/rollout_prm__Qwen__Qwen2.5-14B-Instruct.jsonl'):
    r = json.loads(l)
    V = ast.literal_eval(r['V']) if isinstance(r['V'], str) else r['V']
    V = {float(k): v for k, v in V.items()}
    pv[(r['model'].split('/')[-1], r['problem_id'])] = dict(
        v0=V[0.0], v25=V[0.25], v5=V[0.5], v75=V[0.75],
        mean=float(np.mean(list(V.values()))), gain=V[0.75] - V[0.0],
        cc=int(r['boxed_correct']))
labels = json.load(open('human_eval/labels/phase1/author_1_Sri_random.json'))
joined = []
for L in labels:
    if L.get('soundness') in (None, ''):
        continue
    pid = L['id'].split('-', 2)[2]
    pid = pid[:pid.find('.json') + 5]
    if (L['model'], pid) in pv:
        joined.append((pv[(L['model'], pid)], float(L['soundness']), float(L['judge'])))
s = [j[1] for j in joined]
D = dict(n=len(joined))
for f in ['v0', 'v25', 'v5', 'v75', 'mean', 'gain']:
    D[f'r_{f}_soundness'] = pearson([j[0][f] for j in joined], s)
D['r_gain_partial_v0'] = partial([j[0]['gain'] for j in joined], s, [j[0]['v0'] for j in joined])
D['r_judge_soundness_same_n'] = pearson([j[2] for j in joined], s)
corr = [(j[0], j[1]) for j in joined if j[0]['cc'] == 1]
D['among_correct_n'] = len(corr)
D['among_correct_r_v75'] = pearson([c[0]['v75'] for c in corr], [c[1] for c in corr])
allv = list(pv.values())
D['full200_r_v75_cc'] = pearson([a['v75'] for a in allv], [a['cc'] for a in allv])
res['D_prefix_repair_curve'] = D
print("D)", json.dumps(D, indent=1))
json.dump(res, open('runs/slate2_results.json', 'w'), indent=1)
