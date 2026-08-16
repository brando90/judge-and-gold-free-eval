# Class-law test (derisk for Paper 1): does the TFA boundary + reference-nuisance structure
# hold for OTHER text-matching metrics (unigram-F1, bigram-F1 of the model's own solution vs
# the gold text)? If yes, the 83-92% nuisance is a property of the "match the reference text"
# CLASS, not of TFA. Pure re-scoring of existing generations; no GPU.
import json, glob, re, collections
import numpy as np
from scipy import stats

TOK = re.compile(r"\w+|[^\w\s]")
def fam(m):
    m=m.lower()
    if "qwen2.5-math" in m: return "Qwen-Math"
    if "qwen" in m: return "Qwen2.5"
    if "phi" in m: return "Phi"
    if "mistral" in m or "ministral" in m: return "Mistral"
    if "olmo" in m: return "OLMo"
    if "deepseek" in m: return "DeepSeek-Math"
    if "mathstral" in m: return "Mathstral"
    return "other"

def f1(a, b, n=1):
    ta = TOK.findall(a.lower()); tb = TOK.findall(b.lower())
    if n > 1:
        ta = list(zip(*[ta[i:] for i in range(n)])); tb = list(zip(*[tb[i:] for i in range(n)]))
    if not ta or not tb: return 0.0
    ca, cb = collections.Counter(ta), collections.Counter(tb)
    ov = sum((ca & cb).values())
    p, r = ov/len(ta), ov/len(tb)
    return 0.0 if p+r == 0 else 2*p*r/(p+r)

ANCH = {
 "MATH-500": ["runs/math500/*.judged.jsonl","runs/d2/math500__*.judged.jsonl","runs/wsv/math500__*.jsonl","runs/all/math500__*.jsonl"],
 "MATH (full)": ["runs/mathfull/*.judged.jsonl","runs/all/math-full__*.jsonl"],
 "Putnam-AXIOM": ["runs/putnam/*.judged.jsonl","runs/d2/putnam-axiom__*.judged.jsonl","runs/wsv/putnam-axiom__*.jsonl","runs/all/putnam-axiom__*.jsonl"],
 "Putnam-Variations": ["runs/putnamvar/*.judged.jsonl","runs/all/putnam-axiom-var__*.jsonl"],
 "GSM8K": ["runs/gsm8k/*.judged.jsonl","runs/d2/gsm8k__*.judged.jsonl","runs/all/gsm8k__*.jsonl"],
 "GSM8K-Platinum": ["runs/gsm8kp/*.judged.jsonl","runs/all/gsm8k-platinum__*.jsonl"],
}
GEN = {"Qwen2.5","Phi","Mistral","OLMo"}
pmcache = json.load(open("paper/figs/.permodel_cache.json"))  # for per-model accuracy

out = {}
for ds, globs in ANCH.items():
    per = {}   # model -> {pid: (u1, u2, judge)}
    for g in globs:
        for fp in glob.glob(g):
            for l in open(fp):
                r = json.loads(l)
                fg, gs = r.get("free_gen"), r.get("gold_solution")
                if not fg or not gs: continue
                per.setdefault(r["model"], {})[str(r["problem_id"])] = (
                    f1(fg, gs, 1), f1(fg, gs, 2), r.get("judge_score"))
    accs = {m.split("/")[-1]: v["acc"] for m, v in pmcache[ds].items()}
    # model-level boundary: mean metric vs accuracy across ALL models with acc
    rows = []
    for m, items in per.items():
        short = m.split("/")[-1]
        if short not in accs: continue
        u1 = np.mean([v[0] for v in items.values()]); u2 = np.mean([v[1] for v in items.values()])
        rows.append((short, fam(m), u1, u2, accs[short]))
    r1 = stats.spearmanr([x[2] for x in rows], [x[4] for x in rows]).statistic
    r2 = stats.spearmanr([x[3] for x in rows], [x[4] for x in rows]).statistic
    # two-way decomposition on unigram-F1, 4 general families with >=3 models
    fams = collections.defaultdict(list)
    for m in per:
        if fam(m) in GEN: fams[fam(m)].append(m)
    fams = {f: sorted(ms) for f, ms in fams.items() if len(ms) >= 3}
    models = [m for ms in fams.values() for m in ms]
    dec = {}
    if len(fams) >= 3:
        shared = set.intersection(*(set(per[m]) for m in models))
        items = sorted(shared)
        if len(items) >= 30:
            for k, name in ((0, "u1"),):
                T = np.array([[per[m][j][k] for j in items] for m in models])
                D = T - T.mean(axis=1, keepdims=True)
                famof = np.array([fam(m) for m in models]); fn = sorted(fams)
                Cm = np.array([D[famof == f].mean(axis=0) for f in fn])
                b = Cm.mean(axis=0)
                ss_t = (D**2).sum()
                ss_item = len(models) * (b**2).sum()
                ss_ixf = sum(((Cm[fn.index(fam(m))] - b)**2).sum() for m in models)
                ss_res = ss_t - ss_item - ss_ixf
                dec = dict(item=100*ss_item/ss_t, ixf=100*ss_ixf/ss_t, res=100*ss_res/ss_t,
                           n_models=len(models), n_items=len(items))
    out[ds] = dict(rho_u1=r1, rho_u2=r2, n_models=len(rows), dec=dec)
    d = dec or {}
    print(f"{ds:20s} boundary: u1-F1 rho={r1:+.2f}  u2-F1 rho={r2:+.2f} (n={len(rows)}) | "
          f"decomp u1: item={d.get('item',float('nan')):.1f}% ixf={d.get('ixf',float('nan')):.1f}% res={d.get('res',float('nan')):.1f}%")

json.dump(out, open("runs/class_law_test.json", "w"), indent=1)
ms = json.load(open("runs/multistat.json"))["cross_family"]
print("\nTFA boundary for comparison:", {k: round(v["spearman"],2) for k,v in ms.items() if k in out})
