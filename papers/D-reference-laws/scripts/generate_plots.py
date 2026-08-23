#!/usr/bin/env python
"""Generate figures for Paper D (reference-lever inversion under answer multiplicity).

Data sources:
  - papers/analysis/ties_fullset.json   (excess hack gap + regret per config, n=51)
  - papers/analysis/ties_p2_margin.json (anchoring margins per judge/rep/cond)
  - Math gaps are the published companion-A values (hardcoded below, cited in the paper).

Outputs vector PDFs into papers/D-reference-laws/figures/.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
ANALYSIS = PAPER.parent / "analysis"
FIGDIR = PAPER / "figures"
FIGDIR.mkdir(exist_ok=True)

BLUE = "#4269d0"   # referenced
ORANGE = "#c5541a" # blind (no reference)
INK = "#1a1a1a"
MUTED = "#6b6b6b"
GRID = "#e3e3e3"

plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 10.5,
    "axes.labelsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "font.family": "sans-serif",
    "text.color": INK,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "pdf.fonttype": 42,
})

SIZES = ["1.5B", "3B", "7B", "14B"]

# ---------------------------------------------------------------- data loading

with open(ANALYSIS / "ties_fullset.json") as f:
    fullset = json.load(f)

def ties_gap(size, cond):
    return fullset[f"ties__Qwen__Qwen2.5-{size}-Instruct__{cond}"]["excess_gap"]

TIES = {s: (ties_gap(s, "noref"), ties_gap(s, "ref")) for s in SIZES}

# Registered in-band primary analysis (pool pass rate in [0.2, 0.8]; n=7 items),
# per the registration (commit 99c40ea). (noref, ref) excess hack gaps; quoted in
# the paper's RQ1 as the underpowered registered primary that agrees in direction.
TIES_INBAND = {
    "1.5B": (1.19, 1.83),
    "3B":   (0.93, 1.82),
    "7B":   (1.26, 1.76),
    "14B":  (0.58, 1.59),
}

# Math best-of-64 excess hack gaps (noref, ref) from companion paper A (same
# estimators, same judge ladder); quoted, not recomputed here.
MATH = {
    "1.5B": (0.88, 0.16),
    "3B":   (0.44, 0.07),
    "7B":   (0.80, 0.18),
    "14B":  (0.63, 0.05),
}

with open(ANALYSIS / "ties_p2_margin.json") as f:
    margins_raw = json.load(f)

def margin_cells(size, cond):
    """Return the (margin, ci) pairs for reps a and b of one size/condition."""
    out = []
    for rep in ("a", "b"):
        key = f"ties__Qwen__Qwen2.5-{size}-Instruct__ref_{rep}:{cond}"
        row = next(r for r in margins_raw if r["config"] == key)
        out.append((row["margin"], row["ci"]))
    return out

# Average the two rubric reps; whiskers span the union of the two rep CIs.
MARGINS = {}
for size in SIZES:
    for cond in ("ref", "noref"):
        cells = margin_cells(size, cond)
        avg = sum(m for m, _ in cells) / len(cells)
        lo = min(ci[0] for _, ci in cells)
        hi = max(ci[1] for _, ci in cells)
        MARGINS[(size, cond)] = (avg, lo, hi)

# ------------------------------------------------------------- fig_inversion

def style_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(MUTED)
    ax.tick_params(colors=INK, length=3)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

def dumbbell(ax, data, title, inband=None):
    ys = range(len(SIZES))
    off = 0.055  # horizontal label offset (data units)
    for y, size in zip(ys, SIZES):
        noref, ref = data[size]
        if inband is not None:
            # registered in-band subset: small hollow markers, offset above the
            # full-pool row; same hue carries the same condition identity.
            ib_noref, ib_ref = inband[size]
            dy = 0.26
            ax.plot([ib_noref], [y + dy], "o", ms=4.5, markerfacecolor="none",
                    markeredgecolor=ORANGE, markeredgewidth=1.2, zorder=3)
            ax.plot([ib_ref], [y + dy], "o", ms=4.5, markerfacecolor="none",
                    markeredgecolor=BLUE, markeredgewidth=1.2, zorder=3)
        ax.annotate(
            "", xy=(ref, y), xytext=(noref, y),
            arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.4,
                            shrinkA=6, shrinkB=6, mutation_scale=11),
            zorder=2)
        ax.plot([noref], [y], "o", ms=8, color=ORANGE, zorder=3,
                markeredgecolor="white", markeredgewidth=1.5)
        ax.plot([ref], [y], "o", ms=8, color=BLUE, zorder=3,
                markeredgecolor="white", markeredgewidth=1.5)
        # direct value labels on the outer side of each dot
        if ref >= noref:
            ax.text(noref - off, y, f"+{noref:.2f}", ha="right", va="center",
                    fontsize=10, color=MUTED)
            ax.text(ref + off, y, f"+{ref:.2f}", ha="left", va="center",
                    fontsize=10, color=MUTED)
        else:
            ax.text(noref + off, y, f"+{noref:.2f}", ha="left", va="center",
                    fontsize=10, color=MUTED)
            ax.text(ref - off, y, f"+{ref:.2f}", ha="right", va="center",
                    fontsize=10, color=MUTED)
    ax.set_yticks(list(ys), SIZES)
    ax.set_ylim(-0.6, len(SIZES) - 0.4)
    ax.set_xlim(-0.32, 2.02)
    ax.set_title(title, loc="left", color=INK)
    ax.set_xlabel("excess hack gap at $n{=}64$ (baseline SD)")
    style_axis(ax)

fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
dumbbell(axes[0], MATH, "Math (unique answer)")
dumbbell(axes[1], TIES, "Ties (multiple valid answers)", inband=TIES_INBAND)
axes[0].set_ylabel("judge size")
handles = [
    plt.Line2D([], [], marker="o", ls="", ms=8, color=ORANGE,
               markeredgecolor="white", markeredgewidth=1.5, label="blind judge"),
    plt.Line2D([], [], marker="o", ls="", ms=8, color=BLUE,
               markeredgecolor="white", markeredgewidth=1.5, label="referenced judge"),
    plt.Line2D([], [], marker="o", ls="", ms=4.5, color="none",
               markeredgecolor=MUTED, markeredgewidth=1.2,
               label="in-band subset ($n{=}7$)"),
]
fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.08),
           ncols=3, frameon=False, handletextpad=0.3, columnspacing=1.6)
fig.tight_layout(w_pad=1.6)
fig.savefig(FIGDIR / "fig_inversion.pdf", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------- fig_anchoring

fig, ax = plt.subplots(figsize=(5.6, 3.0))
x = range(len(SIZES))
w = 0.36
for i, size in enumerate(SIZES):
    for cond, color, dx, label in (
        ("ref", BLUE, -w / 2, "referenced judge"),
        ("noref", ORANGE, +w / 2, "blind judge"),
    ):
        avg, lo, hi = MARGINS[(size, cond)]
        ax.bar(i + dx, avg, width=w - 0.04, color=color, zorder=3,
               label=label if i == 0 else None)
        ax.errorbar(i + dx, avg, yerr=[[avg - lo], [hi - avg]],
                    fmt="none", ecolor=INK, elinewidth=1.2, capsize=3, zorder=4)
        va = "bottom" if avg >= 0 else "top"
        ytext = hi + 0.25 if avg >= 0 else lo - 0.25
        ax.text(i + dx, ytext, f"{avg:+.1f}", ha="center", va=va,
                fontsize=10, color=MUTED)
ax.axhline(0, color=MUTED, lw=1.0, zorder=2)
ax.set_xticks(list(x), SIZES)
ax.set_xlabel("judge size")
ax.set_ylabel("anchoring margin\n(score points, 0–10 scale)")
ax.set_ylim(-6.4, 11.2)
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["left", "bottom"]].set_color(MUTED)
ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
ax.tick_params(colors=INK, length=3)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncols=2,
          frameon=False, handletextpad=0.4, columnspacing=1.4)
fig.tight_layout()
fig.savefig(FIGDIR / "fig_anchoring.pdf", bbox_inches="tight")
plt.close(fig)

print("wrote", FIGDIR / "fig_inversion.pdf")
print("wrote", FIGDIR / "fig_anchoring.pdf")
print("margins used:")
for k, v in MARGINS.items():
    print(" ", k, tuple(round(x, 2) for x in v))
