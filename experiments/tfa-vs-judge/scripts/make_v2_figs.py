# Figures for the v2 (feedback-revised) TFA deck. Three additions driven by Brando's review:
#   fig_ms_multistat.png : within-Qwen TFA-vs-accuracy under THREE statistics (Pearson, Spearman,
#                          Kendall) per dataset, plus a histogram of all 29 within-family ladder
#                          correlations split hard-vs-saturated. Replaces the "0.6 to 1.0" range chip.
#   fig8_agentic_v2.png  : SWE-bench redrawn in the SAME arrow-per-family grammar as fig7_mechanism
#                          (tail = smallest model, head = largest), so the visual language never changes.
#   multistat.json       : every correlation in triplicate for the deck's tables.
import json, re, collections
import numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "paper/figs"
pm = json.load(open("paper/figs/.permodel_cache.json"))
REGIME = {"MATH-500": "hard", "MATH (full)": "hard", "Putnam-AXIOM": "hard", "Putnam-Variations": "hard",
          "Omni-MATH (olympiad)": "hard", "HumanEval (code)": "code", "GSM8K": "saturated", "GSM8K-Platinum": "saturated"}

def tri(t, s):
    t, s = np.array(t, float), np.array(s, float)
    return dict(pearson=float(stats.pearsonr(t, s).statistic), spearman=float(stats.spearmanr(t, s).statistic),
                kendall=float(stats.kendalltau(t, s).statistic), n=len(t))

res = {"cross_family": {}, "within_qwen": {}, "within_family_cells": [], "swe": {}}
for lab, d in pm.items():
    res["cross_family"][lab] = tri([v["tfa"] for v in d.values()], [v["acc"] for v in d.values()])
    q = [(v["tfa"], v["acc"]) for v in d.values() if v["fam"] == "Qwen2.5"]
    if len(q) >= 4: res["within_qwen"][lab] = tri(*zip(*q))
    byf = collections.defaultdict(list)
    for v in d.values(): byf[v["fam"]].append((v["tfa"], v["acc"]))
    for f, pts in byf.items():
        if len(pts) >= 3:
            res["within_family_cells"].append(dict(dataset=lab, family=f, regime=REGIME[lab], **tri(*zip(*pts))))

# ---- SWE-bench (patch-TFA vs HumanEval pass@1) ----------------------------
rows = [json.loads(l) for l in open("runs/scores_crossfam_swe.jsonl")]
res["swe"]["cross_family"] = tri([r["patch_tfa_added"] for r in rows], [r["humaneval_pass1"] for r in rows])
qc = sorted([r for r in rows if r["family"] == "Qwen-Coder"], key=lambda r: r["humaneval_pass1"])
res["swe"]["within_qwen_coder"] = tri([r["patch_tfa_added"] for r in qc], [r["humaneval_pass1"] for r in qc])
json.dump(res, open("runs/multistat.json", "w"), indent=1)

# ---- Figure A: three statistics + histogram --------------------------------
ORDER = ["Putnam-AXIOM", "Omni-MATH (olympiad)", "MATH-500", "Putnam-Variations", "MATH (full)",
         "HumanEval (code)", "GSM8K", "GSM8K-Platinum"]
MCOL = {"pearson": "#2b5c8a", "spearman": "#2f8f4e", "kendall": "#c07d15"}
fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.2, 5.2), gridspec_kw=dict(width_ratios=[1.25, 1]))
ys = np.arange(len(ORDER))[::-1]
for y, lab in zip(ys, ORDER):
    w = res["within_qwen"][lab]
    for k, dy in (("pearson", 0.18), ("spearman", 0.0), ("kendall", -0.18)):
        axL.scatter([w[k]], [y + dy], s=64, color=MCOL[k], zorder=3, label=k if lab == ORDER[0] else None)
    axL.plot([min(w["pearson"], w["spearman"], w["kendall"]), max(w["pearson"], w["spearman"], w["kendall"])],
             [y, y], color="#c9ced6", lw=1.2, zorder=1)
axL.set_yticks(ys); axL.set_yticklabels(ORDER, fontsize=10)
axL.set_xlim(0, 1.08); axL.grid(axis="x", alpha=0.25)
axL.set_xlabel("correlation, mean TFA vs accuracy (within-Qwen ladder, n=5 models)", fontsize=10)
axL.legend(fontsize=9.5, loc="upper left", frameon=False, title=None)
axL.set_title("Within one family, three statistics agree:\nall positive on every dataset, weakest where accuracy saturates", fontsize=11, loc="left")
for sp in ("top", "right", "left"): axL.spines[sp].set_visible(False)
axL.tick_params(left=False)

cells = res["within_family_cells"]
bins = np.linspace(-1, 1, 9)
hard = [c["spearman"] for c in cells if c["regime"] == "hard"]
easy = [c["spearman"] for c in cells if c["regime"] != "hard"]
axR.hist([hard, easy], bins=bins, stacked=True, color=["#2f8f4e", "#d98c1f"], edgecolor="white",
         label=[f"hard references ({len(hard)} ladders)", f"saturated / code ({len(easy)} ladders)"])
axR.axvline(0, color="#333", lw=1.0)
axR.set_xlabel("Spearman ρ(TFA, accuracy) of one family ladder on one dataset", fontsize=10)
axR.set_ylabel("number of family × dataset ladders", fontsize=10)
axR.legend(fontsize=9.5, frameon=False, loc="upper left")
axR.set_title("All 29 family ladders as a histogram:\nhard-reference ladders pile up at +1, saturated ones scatter", fontsize=11, loc="left")
for sp in ("top", "right"): axR.spines[sp].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/fig_ms_multistat.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE fig_ms_multistat.png  hard cells:", len(hard), "easy cells:", len(easy))

# ---- Figure B: SWE-bench in the arrow grammar ------------------------------
def sz(m):
    z = re.search(r"(\d+\.?\d*)[bB]", m); return float(z.group(1)) if z else 0
FCOL = {"Qwen-Coder": "#1a1a1a", "DeepSeek-Coder": "#b07a1e", "CodeLlama": "#C44E52", "StarCoder2": "#4C72B0"}
byf = collections.defaultdict(list)
for r in rows: byf[r["family"]].append((sz(r["model"]), r["patch_tfa_added"], r["humaneval_pass1"]))
w, c = res["swe"]["within_qwen_coder"], res["swe"]["cross_family"]
fig, ax = plt.subplots(figsize=(9.8, 6.2))
for f, pts in sorted(byf.items()):
    pts = sorted(pts); col = FCOL[f]
    if len(pts) >= 2:
        (x0, y0), (x1, y1) = (pts[0][1], pts[0][2]), (pts[-1][1], pts[-1][2])
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.45,head_length=0.9", color=col, lw=3.2,
                                    shrinkA=0, shrinkB=0), zorder=3)
        for s, x, y in pts: ax.scatter([x], [y], color=col, s=42, zorder=4)
        ax.annotate(f, ((x0 + x1) / 2, (y0 + y1) / 2), fontsize=10, color=col, fontweight="bold",
                    xytext=(10, 12), textcoords="offset points", zorder=5)
        for s, x, y in (pts[0], pts[-1]):
            ax.annotate(f"{s:g}B", (x, y), fontsize=8.5, color=col, xytext=(4, -11), textcoords="offset points")
    else:
        s, x, y = pts[0]
        ax.scatter([x], [y], color=col, s=110, zorder=4, marker="D", edgecolors="white", linewidths=1.2)
        ax.annotate(f"{f}-{s:g}B\n(one size available)", (x, y), fontsize=8.5, color=col,
                    xytext=(8, -4), textcoords="offset points")
gx = [p[1] for pts in byf.values() for p in pts]; gy = [p[2] for pts in byf.values() for p in pts]
mx = (max(gx) - min(gx)) * 0.14; my = (max(gy) - min(gy)) * 0.12
ax.set_xlim(min(gx) - mx, max(gx) + mx * 2.6); ax.set_ylim(min(gy) - my, max(gy) + my)
ax.set_xlabel("mean patch-TFA on the gold repository patch (added lines)", fontsize=10.5)
ax.set_ylabel("HumanEval pass@1 (coding capability)", fontsize=10.5)
ax.grid(alpha=0.3)
ax.set_title("SWE-bench, drawn exactly like the math panels: each arrow is one coder family's size ladder,\n"
             f"tail = smallest model, head = largest. Within Qwen-Coder the arrow points up-right "
             f"(ρ={w['spearman']:+.2f}, τ={w['kendall']:+.2f}, r={w['pearson']:+.2f}, n=4);\n"
             f"across all four families there is no relationship (ρ={c['spearman']:+.2f}, τ={c['kendall']:+.2f}, "
             f"r={c['pearson']:+.2f}, n=8). CodeLlama's arrow points DOWN-right: best style match, worst code.",
             fontsize=10.5, loc="left")
fig.tight_layout()
fig.savefig(f"{OUT}/fig8_agentic_v2.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE fig8_agentic_v2.png")
print("SWE within:", w); print("SWE cross:", c)
