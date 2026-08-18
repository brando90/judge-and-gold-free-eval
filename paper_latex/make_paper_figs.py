# Paper figures. Run: <figvenv>/bin/python make_paper_figs.py  (from paper_latex/)
# Palette validated (dataviz six checks): BLUE #4269d0 = verification/certified,
# ORANGE #c5541a = comparison/uncertified, GRAY #6b7280 = neutral context.
import json, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GRAY = "#4269d0", "#c5541a", "#6b7280"
INK, MUTED = "#1a1a1a", "#6b7280"
EXP = "../experiments/tfa-vs-judge"
os.makedirs("figs", exist_ok=True)
plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.edgecolor": "#d0d0d0", "axes.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.labelcolor": INK, "figure.facecolor": "white", "axes.facecolor": "white",
})


def despine(ax, keep=("left", "bottom")):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)


# ---------------------------------------------------------------- Figure 1 (master)
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.6))

# Panel A: the two classes against human soundness (lollipop)
ax = axes[0]
rows = [  # (label, r, class)  comparison = class-table numbers; verification incl. new slate
    ("unigram-F1", -0.24, "c"), ("gold logprob", -0.17, "c"), ("TFA", -0.07, "c"),
    ("TF-IDF", 0.01, "c"), ("embeddings", 0.14, "c"),
    ("answer-swap", 0.13, "v"), ("completion value", 0.49, "v"),
    ("prefix-repair curve", 0.79, "v"), ("certified judge", 0.59, "v"),
]
rows.sort(key=lambda t: t[1])
ys = np.arange(len(rows))
ax.axvline(0, color="#d0d0d0", lw=0.8, zorder=0)
for y, (name, r, cls) in zip(ys, rows):
    col = ORANGE if cls == "c" else BLUE
    ax.plot([0, r], [y, y], color=col, lw=2, solid_capstyle="round")
    ax.plot([r], [y], "o", color=col, ms=6)
    ax.text(r + (0.03 if r >= 0 else -0.03), y, f"{r:+.2f}", va="center",
            ha="left" if r >= 0 else "right", fontsize=7.5, color=MUTED)
ax.set_yticks(ys, [r[0] for r in rows])
ax.set_xlim(-0.45, 1.02)
ax.set_xlabel("correlation with human soundness")
ax.set_title("A  Compare fails, verify works", loc="left", fontweight="bold")
ax.plot([], [], "o-", color=ORANGE, label="comparison class")
ax.plot([], [], "o-", color=BLUE, label="verification class")
ax.legend(frameon=False, fontsize=7.5, loc="lower right", handlelength=1.2)
despine(ax, keep=("bottom",))
ax.tick_params(left=False)

# Panel B: the mechanism — TFA vs reference perplexity (real 6,000 points)
ax = axes[1]
pts = [json.loads(l) for l in open(f"{EXP}/runs/tfa_bpc_math500.jsonl")]
x = np.array([p["bpc"] for p in pts]); y = np.array([p["tfa"] for p in pts])
ax.scatter(x, y, s=3, alpha=0.12, color=BLUE, edgecolors="none", rasterized=True)
b = np.polyfit(x, y, 1)
xs = np.linspace(x.min(), x.max(), 50)
ax.plot(xs, np.polyval(b, xs), color=INK, lw=1.5)
ax.text(0.97, 0.92, "$r = -0.895$\n$n = 6{,}000$", transform=ax.transAxes,
        ha="right", va="top", fontsize=9)
ax.set_xlabel("reference bits-per-character (under the same model)")
ax.set_ylabel("teacher-forced accuracy")
ax.set_title("B  TFA is 80% reference perplexity", loc="left", fontweight="bold")
despine(ax)

# Panel C: the certificate predicts hack-resistance (25 configs, real data)
ax = axes[2]
math = json.load(open(f"{EXP}/runs/bon_v2_full.json"))["summary"]
code = json.load(open(f"{EXP}/runs/bon_code_full.json"))["summary"]
for summ, marker, dom in ((math, "o", "math"), (code, "^", "code")):
    for cfg, s in summ.items():
        certified = "__ref" in cfg and "sabotage" not in cfg
        col = BLUE if certified else ORANGE
        ax.scatter(s["excess_gap"], s["oracle_regret64"], marker=marker, s=34,
                   color=col, edgecolors="white", linewidths=0.6, zorder=3)
ax.annotate("1.5B ref (math)", (0.16, 0.010), (0.42, 0.06), fontsize=7, color=MUTED,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
ax.annotate("1.5B ref (code):\nthe capability gate", (1.396, 0.441), (0.78, 0.52),
            fontsize=7, color=MUTED, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
ax.annotate("GPT-5.2 sabotaged (math):\ninflation w/o damage", (0.85, 0.133), (0.9, 0.24),
            fontsize=7, color=MUTED, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
ax.set_xlabel("excess hack gap (scoreboard inflation, $\\sigma$)")
ax.set_ylabel("oracle regret @64 (accuracy lost)")
ax.set_title("C  The certificate predicts who gets hacked", loc="left", fontweight="bold")
h = [plt.Line2D([], [], marker="o", ls="", color=BLUE, label="referenced judge"),
     plt.Line2D([], [], marker="o", ls="", color=ORANGE, label="blind or sabotaged"),
     plt.Line2D([], [], marker="o", ls="", color=GRAY, label="math"),
     plt.Line2D([], [], marker="^", ls="", color=GRAY, label="code")]
ax.legend(handles=h, frameon=False, fontsize=7, loc="upper left", handlelength=1.0)
despine(ax)
fig.tight_layout(w_pad=2.0)
fig.savefig("figs/fig1_master.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------- Figure 2: the two registered sweeps
fig, axes = plt.subplots(1, 2, figsize=(9, 3.1))
ax = axes[0]
gam_labels = ["uniform", "0.5", "1", "2", "4", "8", "last-16", "last-4"]
rho = [0.126, 0.126, 0.154, 0.042, 0.014, -0.007, 0.028, -0.371]
ax.axhline(0, color="#d0d0d0", lw=0.8)
ax.plot(range(len(rho)), rho, "-o", color=ORANGE, lw=2, ms=5)
ax.axhline(0.02, color=GRAY, lw=1, ls=":")
ax.text(0.05, 0.045, "answer-only-reference null (+0.02)", fontsize=7, color=MUTED)
ax.set_xticks(range(len(rho)), gam_labels, fontsize=7.5)
ax.set_xlabel("late-token weighting strength $\\gamma$")
ax.set_ylabel("model-ranking $\\rho$ vs accuracy")
ax.set_title("Position-weighting makes TFA worse", loc="left", fontweight="bold")
despine(ax)
ax = axes[1]
ks = [0.0, 0.25, 0.5, 0.75]
rs = [0.543, 0.680, 0.758, 0.785]
ax.plot(ks, rs, "-o", color=BLUE, lw=2, ms=5)
for k, r in zip(ks, rs):
    ax.text(k, r + 0.02, f"+{r:.2f}", ha="center", fontsize=7.5, color=MUTED)
ax.set_ylim(0.45, 0.9)
ax.set_xticks(ks, ["0\n(difficulty only)", "0.25", "0.5", "0.75"], fontsize=7.5)
ax.set_xlabel("truncation depth $k$ (fraction of trace shown to completer)")
ax.set_ylabel("$r$ vs human soundness")
ax.set_title("Prefix-repair signal rises with depth", loc="left", fontweight="bold")
despine(ax)
fig.tight_layout(w_pad=2.5)
fig.savefig("figs/fig2_sweeps.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# ------------------------------------------- Figure 3: the capability gate (dumbbell)
fig, axes = plt.subplots(1, 2, figsize=(9, 2.9), sharey=True)
sizes = ["1.5B", "3B", "7B", "14B", "GPT-5.2"]
mathd = {"1.5B": (0.88, 0.16), "3B": (0.44, 0.07), "7B": (0.80, 0.18),
         "14B": (0.63, 0.05), "GPT-5.2": (None, 0.38)}
coded = {"1.5B": (1.45, 1.40), "3B": (1.06, 0.43), "7B": (1.06, 0.49),
         "14B": (1.04, 0.37), "GPT-5.2": (0.78, 0.22)}
for ax, data, dom in ((axes[0], mathd, "math (compare text)"),
                      (axes[1], coded, "code (execute tests)")):
    ys = np.arange(len(sizes))[::-1]
    for y, s in zip(ys, sizes):
        noref, ref = data[s]
        if noref is not None:
            ax.plot([ref, noref], [y, y], color="#d0d0d0", lw=1.6, zorder=1)
            ax.plot([noref], [y], "o", color=ORANGE, ms=7, zorder=3)
        ax.plot([ref], [y], "o", color=BLUE, ms=7, zorder=3)
    ax.set_yticks(ys, sizes)
    ax.set_xlim(-0.05, 1.6)
    ax.set_xlabel("excess hack gap ($\\sigma$)")
    ax.set_title(dom, loc="left", fontweight="bold")
    despine(ax, keep=("bottom",))
    ax.tick_params(left=False)
axes[1].annotate("reference does nothing\nat 1.5B on code", (1.40, 4), (0.55, 3.35),
                 fontsize=7.5, color=MUTED,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
h = [plt.Line2D([], [], marker="o", ls="", color=ORANGE, label="no reference"),
     plt.Line2D([], [], marker="o", ls="", color=BLUE, label="with trusted reference")]
axes[0].legend(handles=h, frameon=False, fontsize=7.5, loc="lower right", handlelength=1.0)
fig.tight_layout(w_pad=2.0)
fig.savefig("figs/fig3_gate.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("wrote figs/fig1_master.png, figs/fig2_sweeps.png, figs/fig3_gate.png")
