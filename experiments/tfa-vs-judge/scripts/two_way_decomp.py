# Two-way variance decomposition of per-item TFA, answering Brando's review point:
# the original 89-96% "shared" component was computed on the Qwen ladder alone, so it pools
# true reference predictability (item main effect) with Qwen's family style matching the
# reference (item x family). Here: model nested in family across 4 families (Qwen 5, Phi 3,
# Mistral 3, OLMo 3), so the two channels separate.
#
# Decomposition of the model-centered grid D[i,j] = T[i,j] - rowmean_i:
#   c_f[j]  = mean over models i in family f of D[i,j]      (family's item profile)
#   b[j]    = unweighted mean over families of c_f[j]        (item main effect: shared by ALL families)
#   D[i,j]  = b[j] + (c_f[j] - b[j]) + (D[i,j] - c_f[j])
#              item    item x family     model-specific residual
# Shares of sum-of-squares of D are reported per dataset.
import glob, json, re, collections
import numpy as np

def fam(m):
    m = m.lower()
    if "qwen2.5-math" in m: return "Qwen-Math"
    if "qwen" in m: return "Qwen2.5"
    if "phi" in m: return "Phi"
    if "mistral" in m or "ministral" in m: return "Mistral"
    if "olmo" in m: return "OLMo"
    if "deepseek" in m: return "DeepSeek-Math"
    if "mathstral" in m: return "Mathstral"
    return "other"

ANCHORS = [
    ("MATH-500", ["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl", "runs/wsv/math500__*.jsonl", "runs/all/math500__*.jsonl"]),
    ("MATH (full)", ["runs/mathfull/*.judged.jsonl", "runs/all/math-full__*.jsonl"]),
    ("Putnam-AXIOM", ["runs/putnam/*.judged.jsonl", "runs/d2/putnam-axiom__*.judged.jsonl", "runs/wsv/putnam-axiom__*.jsonl", "runs/all/putnam-axiom__*.jsonl"]),
    ("Putnam-Variations", ["runs/putnamvar/*.judged.jsonl", "runs/all/putnam-axiom-var__*.jsonl"]),
    ("GSM8K", ["runs/gsm8k/*.judged.jsonl", "runs/d2/gsm8k__*.judged.jsonl", "runs/all/gsm8k__*.jsonl"]),
    ("GSM8K-Platinum", ["runs/gsm8kp/*.judged.jsonl", "runs/all/gsm8k-platinum__*.jsonl"]),
]
GEN = {"Qwen2.5", "Phi", "Mistral", "OLMo"}   # general families with 3+ sizes

print(f"{'dataset':18s} {'models':>6s} {'fams':>4s} {'items':>5s} | {'item':>6s} {'item x fam':>10s} {'residual':>8s} | qwen-only item share")
results = {}
for label, globs in ANCHORS:
    permodel = {}
    for g in globs:
        for path in glob.glob(g):
            for line in open(path):
                r = json.loads(line)
                m = r["model"]; f = fam(m)
                if f not in GEN: continue
                t = r.get("tfa_argmax")
                if t is None: continue
                permodel.setdefault(m, {})[str(r["problem_id"])] = float(t)
    fams = collections.defaultdict(list)
    for m in permodel: fams[fam(m)].append(m)
    fams = {f: sorted(ms) for f, ms in fams.items() if len(ms) >= 3}
    models = [m for ms in fams.values() for m in ms]
    shared = set.intersection(*(set(permodel[m]) for m in models))
    items = sorted(shared)
    if len(items) < 30:
        print(f"{label:18s} skipped (only {len(items)} shared items)"); continue
    T = np.array([[permodel[m][j] for j in items] for m in models])
    D = T - T.mean(axis=1, keepdims=True)
    famof = np.array([fam(m) for m in models])
    fnames = sorted(fams)
    C = np.array([D[famof == f].mean(axis=0) for f in fnames])          # family x item profiles
    b = C.mean(axis=0)                                                   # item main effect
    ss_tot = (D**2).sum()
    ss_item = sum((b**2).sum() for _ in models)                          # b broadcast to every model row
    ss_ixf = sum(((C[fnames.index(fam(m))] - b)**2).sum() for m in models)
    ss_res = sum(((D[i] - C[fnames.index(fam(models[i]))])**2).sum() for i in range(len(models)))
    # qwen-only baseline (the original computation)
    Q = D[famof == "Qwen2.5"]
    bq = Q.mean(axis=0)
    q_share = len(Q) * (bq**2).sum() / (Q**2).sum()
    sh = (100*ss_item/ss_tot, 100*ss_ixf/ss_tot, 100*ss_res/ss_tot)
    results[label] = dict(item=sh[0], item_x_family=sh[1], residual=sh[2], qwen_only=100*q_share,
                          n_models=len(models), n_fams=len(fnames), n_items=len(items))
    print(f"{label:18s} {len(models):6d} {len(fnames):4d} {len(items):5d} | {sh[0]:5.1f}% {sh[1]:9.1f}% {sh[2]:7.1f}% | {100*q_share:.1f}%")
    print(f"{'':18s} orthogonality check: {sh[0]+sh[1]+sh[2]:.1f}% (should be ~100)")

json.dump(results, open("runs/two_way_decomp.json", "w"), indent=1)
print("\nwrote runs/two_way_decomp.json")
