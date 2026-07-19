# Figure 5 for paper/PAPER.md: rollout process-value completer curve.
# Values are the final published results from the rollout-PRM experiment
# (450 responses = 150 problems x {1.5B,7B,14B}, 323 correct / 127 wrong;
# meanV feature). Source: JOURNAL.md section 4, "Scaled result (450 responses)
# + completer comparison". Hardcoded literals because these come from a separate
# experiment, not runs/scores_*.jsonl.
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "paper/figs"; os.makedirs(OUT, exist_ok=True)
comp = ["7B\n(too weak)", "14B\n(sweet spot)", "32B\n(too strong)"]
x = np.arange(3)
overall = [0.33, 0.43, 0.37]; overall_lo = [0.24, 0.35, 0.27]; overall_hi = [0.41, 0.51, 0.45]
wc = [0.09, 0.19, 0.08];      wc_lo = [-0.02, 0.09, -0.02];    wc_hi = [0.20, 0.29, 0.19]

def err(v, lo, hi):
    return [np.array(v) - np.array(lo), np.array(hi) - np.array(v)]

fig, ax = plt.subplots(figsize=(7.6, 4.7))
ax.axvspan(0.55, 1.45, color="#f3f3f3", zorder=0)
ax.axhline(0, color="gray", lw=1, ls="--")
ax.errorbar(x - 0.04, overall, yerr=err(overall, overall_lo, overall_hi), fmt="-o", ms=9, lw=2,
            capsize=5, color="#4C72B0", label="overall (partial ρ | correct)", zorder=3)
ax.errorbar(x + 0.04, wc, yerr=err(wc, wc_lo, wc_hi), fmt="-s", ms=9, lw=2,
            capsize=5, color="#DD8452", label="within-correct (grade among correct answers)", zorder=3)
ax.annotate("only the 14B completer\ncracks the within-correct case\n(+0.19, CI excludes 0)",
            xy=(1, 0.19), xytext=(1.18, 0.34), fontsize=8.5, color="#B5622F",
            arrowprops=dict(arrowstyle="->", color="#B5622F"))
for xi, lab in [(0, "n.s."), (2, "n.s.")]:
    ax.text(xi + 0.04, wc[xi] - 0.055, lab, ha="center", fontsize=8, color="#DD8452")
ax.set_xticks(x); ax.set_xticklabels(comp)
ax.set_xlabel("completer strength")
ax.set_ylabel("partial Spearman ρ(rollout value, judge | correct)")
ax.set_ylim(-0.12, 0.58)
ax.set_title("Rollout value grades solutions — best at a mid-strength completer (inverted-U)")
ax.legend(fontsize=9, loc="upper right")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(f"{OUT}/fig5_rollout_completer_curve.png", dpi=150); plt.close(fig)
print("WROTE", f"{OUT}/fig5_rollout_completer_curve.png")
