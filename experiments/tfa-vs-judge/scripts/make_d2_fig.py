# Figure 6 (cross-family generalization): mean-TFA vs boxed accuracy across the full family ladders
# (17 models, 7 families) on the three anchor datasets. Each family with >=2 models is drawn as a
# connected line so the within-family trend is visible; math-specialized models (one each) are stars.
# Shows the TFA-accuracy relation holds on hard data (MATH, Putnam) and scrambles on saturated GSM8K.
import json, glob, collections, numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent

OUT = "paper/figs"

def fam(m):
    m = m.lower()
    if "qwen2.5-math" in m: return "Qwen2.5-Math"
    if "deepseek-math" in m: return "DeepSeek-Math"
    if "mathstral" in m: return "Mathstral"
    if "qwen2.5" in m: return "Qwen2.5"
    if "mistral" in m: return "Mistral"
    if "phi" in m: return "Phi"
    if "olmo" in m: return "OLMo"
    return "other"

COL = {"Qwen2.5": "#777777", "Mistral": "#C44E52", "Phi": "#4C72B0", "OLMo": "#55A868",
       "Qwen2.5-Math": "#8452b0", "DeepSeek-Math": "#b07a1e", "Mathstral": "#1ba090"}

def gold(r, dk):
    return r["gold_solution"].split("####")[-1].strip().replace(",", "") if dk == "gsm8k" else extract_boxed(r["gold_solution"])

ANCHORS = [
    ("MATH-500", ["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl",
                  "runs/wsv/math500__*.jsonl", "runs/all/math500__*.jsonl"], "math500"),
    ("GSM8K", ["runs/gsm8k/*.judged.jsonl", "runs/d2/gsm8k__*.judged.jsonl", "runs/all/gsm8k__*.jsonl"], "gsm8k"),
    ("Putnam", ["runs/putnam/*.judged.jsonl", "runs/d2/putnam-axiom__*.judged.jsonl",
                "runs/wsv/putnam-axiom__*.jsonl", "runs/all/putnam-axiom__*.jsonl"], "putnam"),
]

fig, axes = plt.subplots(1, 3, figsize=(15, 4.9))
for ax, (ds, globs, dk) in zip(axes, ANCHORS):
    by = {}
    for g in globs:
        for f in glob.glob(g):
            R = [json.loads(l) for l in open(f)]
            if not R or "Qwen2.5-32B" in R[0]["model"]: continue   # keep the 5-model Qwen ladder
            m = R[0]["model"].split("/")[-1]
            cc = [int(answers_equivalent(extract_final_answer(r["free_gen"], dk), gold(r, dk) or "")) for r in R]
            by[m] = (fam(R[0]["model"]), float(np.mean([r["tfa_argmax"] for r in R])), float(np.mean(cc)))
    mt = np.array([v[1] for v in by.values()]); ma = np.array([v[2] for v in by.values()])
    rho = stats.spearmanr(mt, ma).statistic
    byfam = collections.defaultdict(list)
    for m, v in by.items(): byfam[v[0]].append((v[1], v[2]))
    for f, pts in sorted(byfam.items()):
        pts = sorted(pts); c = COL.get(f, "#333")
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if len(pts) >= 2:
            ax.plot(xs, ys, "-o", color=c, ms=6, lw=1.8, label=f, zorder=3)
        else:
            ax.scatter(xs, ys, c=c, marker="*", s=240, edgecolors="black", linewidths=0.5, label=f, zorder=4)
    ax.set_title(f"{ds}:  cross-family ρ(TFA, acc) = {rho:+.2f}", fontsize=11)
    ax.set_xlabel("mean TFA"); ax.set_ylabel("accuracy")
    ax.grid(alpha=0.3)
    if ds == "MATH-500": ax.legend(fontsize=7.5, loc="upper left", ncol=2)
fig.suptitle("Cross-family model ranking, full family ladders (17 models): the TFA-accuracy line holds on "
             "hard data (MATH, Putnam) and scrambles on saturated GSM8K", fontsize=12, y=1.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig6_cross_family.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE", f"{OUT}/fig6_cross_family.png")
