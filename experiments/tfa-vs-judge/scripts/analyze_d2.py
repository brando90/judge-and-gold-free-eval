# D2 — cross-family generalization analysis.
# Pools the Qwen2.5 baseline with the new families (Mistral / Phi / OLMo / ...) on the three
# anchor datasets and asks: (1) does model-level rho(mean-TFA, judge) hold across families
# (do new families lie on the Qwen TFA->judge line, or at a family-specific offset)? and
# (2) does the item-level partial rho(TFA, judge | correct) reproduce family-by-family?
import json, glob, collections, re, numpy as np
from scipy import stats
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent
from tfa.analyze import bootstrap_partial, bootstrap_corr

# anchor dataset -> (list of judged globs [baseline, d2], dskey for scoring)
ANCHORS = {
    "MATH-500": (["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl"], "math500"),
    "GSM8K":    (["runs/gsm8k/*.judged.jsonl",   "runs/d2/gsm8k__*.judged.jsonl"],   "gsm8k"),
    "Putnam":   (["runs/putnam/*.judged.jsonl",  "runs/d2/putnam-axiom__*.judged.jsonl"], "putnam"),
}

def family(model):
    m = model.lower()
    if "qwen2.5" in m: return "Qwen2.5"
    if "qwen3" in m:   return "Qwen3"
    if "mistral" in m or "mixtral" in m: return "Mistral"
    if "phi" in m:     return "Phi"
    if "olmo" in m:    return "OLMo"
    if "llama" in m:   return "Llama"
    if "gemma" in m:   return "Gemma"
    return "Other"

def gold_ans(r, ds):
    if ds == "gsm8k": return r["gold_solution"].split("####")[-1].strip().replace(",", "")
    return extract_boxed(r["gold_solution"])

def load(globs, ds):
    R = []
    for g in globs:
        for fp in glob.glob(g):
            R += [json.loads(l) for l in open(fp)]
    R = [r for r in R if r.get("judge_score") is not None]
    for r in R:
        r["cc"] = int(answers_equivalent(extract_final_answer(r["free_gen"], ds), gold_ans(r, ds)))
        r["fam"] = family(r["model"])
    return R

def resid(y, *ctrl):
    yr = stats.rankdata(y); X = np.column_stack([np.ones(len(y))] + [stats.rankdata(z) for z in ctrl])
    b, *_ = np.linalg.lstsq(X, yr, rcond=None); return yr - X @ b

summary = {}
for ds, (globs, dskey) in ANCHORS.items():
    R = load(globs, dskey)
    if not R:
        print(f"{ds}: no data"); continue
    # ---- model-level ----
    by_model = collections.defaultdict(list)
    for r in R: by_model[r["model"]].append(r)
    rows = []
    for m, rs in by_model.items():
        rows.append((family(m), m, np.mean([x["tfa_argmax"] for x in rs]),
                     np.mean([x["judge_score"] for x in rs]), np.mean([x["cc"] for x in rs]), len(rs)))
    rows.sort(key=lambda t: t[2])
    mt = np.array([r[2] for r in rows]); mj = np.array([r[3] for r in rows]); ma = np.array([r[4] for r in rows])
    ml_all_j = stats.spearmanr(mt, mj).statistic
    ml_all_a = stats.spearmanr(mt, ma).statistic
    qmask = np.array([r[0] == "Qwen2.5" for r in rows])
    ml_qwen_j = stats.spearmanr(mt[qmask], mj[qmask]).statistic if qmask.sum() > 2 else float("nan")
    # ---- item-level: pooled + per family ----
    t = np.array([r["tfa_argmax"] for r in R]); j = np.array([r["judge_score"] for r in R])
    c = np.array([r["cc"] for r in R]); gl = np.array([r["n_gold_tokens"] for r in R])
    pooled = bootstrap_partial(t, j, c, n_boot=3000)
    pooled_len = stats.spearmanr(resid(t, c, gl), resid(j, c, gl)).statistic
    perfam = {}
    for fam in sorted(set(r["fam"] for r in R)):
        idx = np.array([r["fam"] == fam for r in R])
        if idx.sum() < 30: continue
        pf = bootstrap_partial(t[idx], j[idx], c[idx], n_boot=2000)
        perfam[fam] = (pf.rho, pf.lo, pf.hi, int(idx.sum()), float(np.mean(c[idx])))
    summary[ds] = dict(rows=rows, ml_all_j=ml_all_j, ml_all_a=ml_all_a, ml_qwen_j=ml_qwen_j,
                       pooled=pooled, pooled_len=pooled_len, perfam=perfam)

    print("=" * 78)
    print(f"### {ds}   (n={len(R)}, models={len(rows)}, families={len(set(r[0] for r in rows))})")
    print("  model-level rho(mean-TFA, judge): pooled=%+.2f  Qwen2.5-only=%+.2f   rho(TFA,acc) pooled=%+.2f"
          % (ml_all_j, ml_qwen_j, ml_all_a))
    print("  per-model (sorted by TFA):  family / model / meanTFA / meanJudge / acc")
    for fam, m, a, b_, cc, n in rows:
        print(f"    {fam:8s} {m.split('/')[-1]:32s} TFA=%.3f judge=%.2f acc=%.3f (n=%d)" % (a, b_, cc, n))
    print("  item-level partial rho(TFA, judge | correct):")
    print(f"    POOLED     {pooled.rho:+.3f} [{pooled.lo:+.2f},{pooled.hi:+.2f}]   (len-controlled {pooled_len:+.3f})")
    for fam, (rho, lo, hi, n, acc) in perfam.items():
        print(f"    {fam:8s}   {rho:+.3f} [{lo:+.2f},{hi:+.2f}]   (n={n}, acc={acc:.2f})")

import os
os.makedirs("paper", exist_ok=True)
json.dump({ds: {k: (v if not hasattr(v, "rho") else [v.rho, v.lo, v.hi]) for k, v in s.items() if k != "rows"}
           for ds, s in summary.items()}, open("paper/d2_summary.json", "w"), indent=2, default=str)
print("\nwrote paper/d2_summary.json")
