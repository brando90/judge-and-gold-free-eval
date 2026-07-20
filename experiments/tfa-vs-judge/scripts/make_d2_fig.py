# Figure for D2 (cross-family generalization): per-anchor-dataset scatter of mean-TFA vs mean-judge,
# Qwen ladder as a line, new families as distinct markers. Shows cross-family ranking survives on
# hard data (MATH/Putnam) but collapses on saturated GSM8K.
import json, glob, collections, numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "paper/figs"
def fam(m):
    m = m.lower()
    return ("Qwen2.5" if "qwen2.5" in m else "Mistral" if "mistral" in m else "Phi" if "phi" in m
            else "OLMo" if "olmo" in m else "?")
STYLE = {"Qwen2.5": ("#888888", "o", 55), "Mistral": ("#C44E52", "*", 320),
         "Phi": ("#4C72B0", "s", 90), "OLMo": ("#55A868", "^", 110)}

ANCHORS = [("MATH-500", ["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl"]),
           ("GSM8K",    ["runs/gsm8k/*.judged.jsonl",   "runs/d2/gsm8k__*.judged.jsonl"]),
           ("Putnam",   ["runs/putnam/*.judged.jsonl",  "runs/d2/putnam-axiom__*.judged.jsonl"])]

fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
for ax, (ds, globs) in zip(axes, ANCHORS):
    by = collections.defaultdict(list)
    for g in globs:
        for f in glob.glob(g):
            R = [json.loads(l) for l in open(f)]
            if R: by[R[0]["model"]] += R
    pts = {}
    for m, R in by.items():
        pts[m] = (fam(m), np.mean([r["tfa_argmax"] for r in R]), np.mean([r["judge_score"] for r in R]))
    mt = np.array([v[1] for v in pts.values()]); mj = np.array([v[2] for v in pts.values()])
    fams = [v[0] for v in pts.values()]; qm = np.array([f == "Qwen2.5" for f in fams])
    rho_pool = stats.spearmanr(mt, mj).statistic
    rho_qwen = stats.spearmanr(mt[qm], mj[qm]).statistic
    # Qwen line
    q = sorted([(v[1], v[2]) for v in pts.values() if v[0] == "Qwen2.5"])
    ax.plot([a for a, _ in q], [b for _, b in q], "-", color="#bbbbbb", lw=1.5, zorder=1)
    seen = set()
    for m, (fm, t, j) in pts.items():
        col, mk, sz = STYLE[fm]
        ax.scatter(t, j, c=col, marker=mk, s=sz, edgecolors="black", linewidths=0.5,
                   label=fm if fm not in seen else None, zorder=3)
        seen.add(fm)
        if fm != "Qwen2.5":
            ax.annotate(fm, (t, j), textcoords="offset points", xytext=(6, -2), fontsize=8, color=col)
    ax.set_title(f"{ds}:  cross-family ρ={rho_pool:+.2f}   (within-Qwen {rho_qwen:+.2f})", fontsize=11)
    ax.set_xlabel("mean TFA"); ax.set_ylabel("mean judge (0–10)")
    ax.grid(alpha=0.3)
    if ds == "MATH-500": ax.legend(fontsize=8, loc="lower right")
fig.suptitle("Cross-family model ranking: TFA holds on hard data (MATH, Putnam), collapses on saturated GSM8K",
             fontsize=12.5, y=1.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig6_cross_family.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE", f"{OUT}/fig6_cross_family.png")
