# Cross-family SWE-bench check: does masked patch-TFA rank CODER models by real code capability
# (HumanEval pass@1) ACROSS families? Correlate mean added-lines patch-TFA (runs/swebench) with mean
# HumanEval pass@1 (runs/code), restricted to coder families.
import json, glob, re, collections, numpy as np
from scipy import stats

CODER = ("qwen2.5-coder", "deepseek-coder", "codellama", "starcoder2")
def is_coder(m): return any(c in m.lower() for c in CODER)
def fam(m):
    m = m.lower()
    if "qwen2.5-coder" in m: return "Qwen-Coder"
    if "deepseek-coder" in m: return "DeepSeek-Coder"
    if "codellama" in m: return "CodeLlama"
    if "starcoder2" in m: return "StarCoder2"
    return "other"

swe, he = {}, {}
for f in glob.glob("runs/swebench/swebench__*.jsonl"):
    R = [json.loads(l) for l in open(f)]
    if R and is_coder(R[0]["model"]):
        swe[R[0]["model"]] = float(np.mean([r["tfa_masked_added"] for r in R]))
for f in glob.glob("runs/code/humaneval__*.jsonl"):
    R = [json.loads(l) for l in open(f)]
    if R and is_coder(R[0]["model"]):
        he[R[0]["model"]] = float(np.mean([r["code_pass"] for r in R]))

both = sorted(set(swe) & set(he), key=lambda m: (fam(m), swe[m]))
print(f"{'model':38s} {'family':14s} {'patch-TFA':>9s} {'HE-pass@1':>9s}")
for m in both:
    print(f"{m.split('/')[-1]:38s} {fam(m):14s} {swe[m]:9.3f} {he[m]:9.3f}")
if len(both) >= 4:
    t = np.array([swe[m] for m in both]); p = np.array([he[m] for m in both])
    fams = len(set(fam(m) for m in both))
    print(f"\nCROSS-FAMILY  Spearman(patch-TFA, HumanEval pass@1) = {stats.spearmanr(t, p).statistic:+.2f}"
          f"   Pearson = {stats.pearsonr(t, p)[0]:+.2f}   (n={len(both)} models, {fams} families)")
    # within Qwen-Coder for contrast
    q = [m for m in both if fam(m) == "Qwen-Coder"]
    if len(q) >= 3:
        qt = [swe[m] for m in q]; qp = [he[m] for m in q]
        print(f"within Qwen-Coder Spearman(patch-TFA, pass@1) = {stats.spearmanr(qt, qp).statistic:+.2f}  (n={len(q)})")
