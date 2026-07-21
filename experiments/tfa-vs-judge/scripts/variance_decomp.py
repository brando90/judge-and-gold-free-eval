# Variance decomposition behind the mechanism claim: what share of the WITHIN-MODEL variance in per-item
# TFA is explained by a model-invariant reference (item) effect, the "reference-predictability nuisance."
#
# For each dataset, build T[m,i] = per-item TFA for model m on item i (5-model Qwen ladder, aligned on the
# intersection of problem_ids). Center within model: D[m,i] = T[m,i] - mean_i T[m,i]. The item main effect
# is b_i = mean_m D[m,i]. The nuisance fraction is SS(item effect) / SS(total within-model deviation) =
# sum_{m,i} b_i^2 / sum_{m,i} D[m,i]^2, i.e. the fraction of within-model TFA variance that is common to all
# models (a property of the reference), leaving the remainder for model-specific competence.
import json, glob, collections, numpy as np

A = "runs/all/{0}__*.jsonl"
ANCH = [
    ("MATH-500", ["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl", "runs/wsv/math500__*.jsonl", A.format("math500")]),
    ("MATH-full", ["runs/mathfull/*.judged.jsonl", A.format("math-full")]),
    ("GSM8K", ["runs/gsm8k/*.judged.jsonl", "runs/d2/gsm8k__*.judged.jsonl", A.format("gsm8k")]),
    ("GSM8K-Platinum", ["runs/gsm8kp/*.judged.jsonl", A.format("gsm8k-platinum")]),
    ("Putnam-AXIOM", ["runs/putnam/*.judged.jsonl", "runs/d2/putnam-axiom__*.judged.jsonl", "runs/wsv/putnam-axiom__*.jsonl", A.format("putnam-axiom")]),
]

def load_qwen(globs):
    d = collections.defaultdict(dict)
    for g in globs:
        for f in glob.glob(g):
            R = [json.loads(l) for l in open(f)]
            if not R: continue
            m = R[0]["model"]
            if "Qwen2.5-" not in m or "Math" in m or "32B" in m: continue
            mm = m.split("/")[-1]
            for r in R: d[mm][r["problem_id"]] = r["tfa_argmax"]
    return d

def decomp(d):
    models = list(d)
    if len(models) < 3: return None
    pids = set(d[models[0]])
    for m in models[1:]: pids &= set(d[m])
    pids = sorted(pids)
    T = np.array([[d[m][p] for p in pids] for m in models])
    D = T - T.mean(axis=1, keepdims=True)
    b = D.mean(axis=0)
    ss_item = np.sum((np.ones((len(models), 1)) * b) ** 2)
    ss_tot = np.sum(D ** 2)
    return ss_item / ss_tot, len(models), len(pids)

if __name__ == "__main__":
    print(f"{'dataset':16s} {'nuisance %':>10s} {'competence %':>13s}  n_models  n_items")
    fr = []
    for name, globs in ANCH:
        r = decomp(load_qwen(globs))
        if r:
            frac, nm, ni = r; fr.append(frac)
            print(f"{name:16s} {100*frac:9.1f}% {100*(1-frac):12.1f}%   {nm:6d}   {ni:6d}")
    print(f"\nnuisance fraction range: {100*min(fr):.0f}% to {100*max(fr):.0f}%")
