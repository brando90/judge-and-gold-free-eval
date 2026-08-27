# POST HOC robustness for distance_gradient (written after seeing the registered result):
# median slope, 10%-trimmed mean slope, and per-item Spearman(distance, score) among
# non-matching valid samples, referenced and blind.
import json, sys
import numpy as np
from scipy import stats as st
src = open("../../papers/analysis/distance_gradient.py").read()
head = src.split("rows = {")[0]
exec(compile(head, "dg", "exec"))
res = {j: {"sl_ref": [], "sl_bl": [], "rho_ref": [], "rho_bl": []} for j in JUDGES}
for pname, ppath, sdir in POOLS:
    pool = [json.loads(l) for l in open(ppath)]
    sc = {(j,c,r): load(sdir,j,c,r) for j in JUDGES for c in ("noref","ref") for r in ("a","b")}
    for it in pool:
        if pname == "kstrat" and it.get("k") == 1: continue
        ref = it["ref_answer"]; va = it.get("valid_answers") or [ref]
        pos = []
        for i,(s,ok) in enumerate(zip(it["samples"], it["oracle"])):
            if not ok: continue
            d = distance(extract_boxed(s) or s, ref, va)
            if d > 0: pos.append((i,d))
        if len(set(round(d,6) for _,d in pos)) < 2 or len(pos) < 3: continue
        for j in JUDGES:
            for c, tag in (("ref","ref"), ("noref","bl")):
                eb = sc[(j,c,"b")][it["problem_id"]]
                xs = [d for _,d in pos]; ys = [eb[i] for i,_ in pos]
                sp = slope(xs, ys)
                if sp is not None: res[j][f"sl_{tag}"].append(sp)
                if len(set(ys)) > 1:
                    res[j][f"rho_{tag}"].append(st.spearmanr(xs, ys).statistic)
rng2 = np.random.default_rng(0)
def bci(v, f):
    v = np.asarray(v, float)
    b = [f(v[rng2.integers(0,len(v),len(v))]) for _ in range(1000)]
    return f(v), np.percentile(b,2.5), np.percentile(b,97.5)
for j in JUDGES:
    for k, lab in (("sl_ref","slope ref"), ("sl_bl","slope blind"),
                   ("rho_ref","Spearman ref"), ("rho_bl","Spearman blind")):
        med = bci(res[j][k], np.median)
        tr = bci(res[j][k], lambda x: st.trim_mean(x, 0.1))
        print(f"{j:30s} {lab:14s} median {med[0]:+.3f} [{med[1]:+.3f},{med[2]:+.3f}]  "
              f"trim10 {tr[0]:+.3f} [{tr[1]:+.3f},{tr[2]:+.3f}]  n={len(res[j][k])}")
