#!/usr/bin/env python
"""Generate vector (PDF) figures for the reference-matching paper.

Outputs (relative to the paper directory):
  figures/fig_class.pdf      lollipop of Pearson r vs human soundness, all canonical signals
  figures/fig_mechanism.pdf  scatter of per-solution TFA vs reference bits-per-char
  figures/fig_sweeps.pdf     position-weight decay sweep + prefix-repair rise

Data sources:
  ../analysis/canonical_validity.json                       (canonical anchor-set numbers)
  ../../experiments/tfa-vs-judge/runs/tfa_bpc_math500.jsonl (6,000 model-item pairs)
"""

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PAPER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(PAPER_DIR, "figures")
CANONICAL = os.path.join(PAPER_DIR, "..", "analysis", "canonical_validity.json")
TFA_BPC = os.path.join(
    PAPER_DIR, "..", "..", "experiments", "tfa-vs-judge", "runs", "tfa_bpc_math500.jsonl"
)

COMPARISON = "#c5541a"  # comparison metrics
VERIFICATION = "#4269d0"  # verification signals
INK = "#1f2430"
MUTED = "#6b7280"
GRID = "#d7dae0"

plt.rcParams.update(
    {
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "font.family": "sans-serif",
        "axes.edgecolor": MUTED,
        "axes.linewidth": 0.8,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "pdf.fonttype": 42,
    }
)

os.makedirs(FIG_DIR, exist_ok=True)


def despine(ax, keep=("left", "bottom")):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)


# ---------------------------------------------------------------- fig_class
# Display order: comparison class at bottom, judge-free verification above,
# LLM judges (expensive comparison points) on top.
SIGNALS = [
    # key, label, class ("comparison" | "verification" | "judge")
    ("u1", "Unigram-F1", "comparison"),
    ("logprob", "Gold-token logprob ($n{=}42$)", "comparison"),
    ("tfa", "Teacher-forced accuracy (TFA)", "comparison"),
    ("tfidf", "TF-IDF cosine", "comparison"),
    ("embed", "Sentence embeddings", "comparison"),
    ("pv_v0", "Prefix-repair $k{=}0$", "verification"),
    ("pv_v25", "Prefix-repair $k{=}0.25$", "verification"),
    ("pv_v5", "Prefix-repair $k{=}0.5$", "verification"),
    ("pv_v75", "Prefix-repair $k{=}0.75$", "verification"),
    ("pv_mean", "Prefix-repair curve mean", "verification"),
    ("critic_opus", "LLM critic (Claude)", "judge"),
    ("judge_ref", "LLM judge (referenced)", "judge"),
    ("critic_gpt", "LLM critic (GPT)", "judge"),
]


def fig_class():
    with open(CANONICAL) as f:
        data = json.load(f)["signals"]

    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ys = np.arange(len(SIGNALS))

    for y, (key, label, cls) in zip(ys, SIGNALS):
        d = data[key]
        r, (lo, hi) = d["pearson"], d["ci"]
        color = COMPARISON if cls == "comparison" else VERIFICATION
        filled = cls != "judge"
        ax.plot([lo, hi], [y, y], color=color, lw=1.6, solid_capstyle="round", zorder=2)
        ax.plot(
            [0, r], [y, y], color=color, lw=0.0, zorder=1
        )  # (lollipop stem folded into CI bar)
        ax.scatter(
            [r],
            [y],
            s=52,
            facecolor=color if filled else "white",
            edgecolor=color,
            linewidth=1.6,
            zorder=3,
        )

    ax.axvline(0.0, color=MUTED, lw=0.8, ls="--", zorder=0)
    ax.axvline(0.79, color=MUTED, lw=0.8, ls=":", zorder=0)
    ax.text(
        1.0, len(SIGNALS) + 0.15, "inter-rater ceiling (Spearman, shared block)",
        ha="right", va="center", fontsize=10, color=MUTED,
    )

    ax.set_yticks(ys)
    ax.set_yticklabels([s[1] for s in SIGNALS])
    ax.set_xlabel("Pearson $r$ vs. blind human soundness (95% CI)")
    ax.set_xlim(-0.65, 1.02)
    ax.set_ylim(-0.7, len(SIGNALS) + 0.7)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    despine(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)

    handles = [
        plt.Line2D([], [], marker="o", ls="-", color=COMPARISON, label="comparison metrics"),
        plt.Line2D([], [], marker="o", ls="-", color=VERIFICATION, label="verification signals"),
        plt.Line2D(
            [], [], marker="o", ls="-", color=VERIFICATION,
            markerfacecolor="white", label="LLM judges (comparison points)",
        ),
    ]
    ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0.0, 0.96),
        frameon=False, handlelength=1.4,
    )
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig_class.pdf"))
    plt.close(fig)


# ------------------------------------------------------------ fig_mechanism
def fig_mechanism():
    tfa, bpc = [], []
    with open(TFA_BPC) as f:
        for line in f:
            rec = json.loads(line)
            tfa.append(rec["tfa"])
            bpc.append(rec["bpc"])
    tfa, bpc = np.asarray(tfa), np.asarray(bpc)
    r = np.corrcoef(bpc, tfa)[0, 1]

    fig, ax = plt.subplots(figsize=(4.9, 3.7))
    ax.scatter(bpc, tfa, s=4, alpha=0.12, color=COMPARISON, edgecolors="none", rasterized=True)

    slope, intercept = np.polyfit(bpc, tfa, 1)
    xs = np.linspace(bpc.min(), bpc.max(), 100)
    ax.plot(xs, slope * xs + intercept, color=INK, lw=1.6)
    ax.annotate(
        f"$r = {r:.3f}$",
        xy=(0.97, 0.93),
        xycoords="axes fraction",
        ha="right",
        va="top",
        fontsize=11,
        color=INK,
    )

    ax.set_xlabel("reference bits-per-character (same model)")
    ax.set_ylabel("teacher-forced accuracy")
    ax.grid(color=GRID, lw=0.6, zorder=0)
    despine(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig_mechanism.pdf"), dpi=300)
    plt.close(fig)
    return r


# --------------------------------------------------------------- fig_sweeps
def fig_sweeps():
    gammas = ["uniform", "0.5", "1", "2", "4", "8", "last-16", "last-4"]
    rho = [0.126, 0.126, 0.154, 0.042, 0.014, -0.007, 0.028, -0.371]
    null = 0.02

    ks = [0, 0.25, 0.5, 0.75]
    pv = [0.54, 0.68, 0.76, 0.78]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.8, 3.1))

    xs = np.arange(len(gammas))
    axL.axhline(null, color=MUTED, lw=0.9, ls="--", zorder=1)
    axL.text(0.05, null + 0.025, "answer-only-reference null ($+0.02$)", fontsize=10, color=MUTED)
    axL.axhline(0.0, color=GRID, lw=0.8, zorder=0)
    axL.plot(xs, rho, "-o", color=COMPARISON, lw=2, markersize=6, zorder=2)
    axL.set_xticks(xs)
    axL.set_xticklabels(gammas, rotation=45, ha="right")
    axL.set_xlabel("position weight $\\gamma$")
    axL.set_ylabel("12-model ranking $\\rho$")
    axL.set_title("up-weighting late tokens: decay", fontsize=10, color=INK)
    axL.set_ylim(-0.45, 0.3)

    axR.plot(ks, pv, "-o", color=VERIFICATION, lw=2, markersize=6, zorder=2)
    for k, v in zip(ks, pv):
        axR.annotate(
            f"$+{v:.2f}$", xy=(k, v), xytext=(0, 7), textcoords="offset points",
            ha="center", fontsize=10, color=INK,
        )
    axR.set_xticks(ks)
    axR.set_xlabel("truncation depth $k$")
    axR.set_ylabel("$r$ vs. human soundness")
    axR.set_title("prefix repair: rise", fontsize=10, color=INK)
    axR.set_ylim(0.45, 0.9)

    for ax in (axL, axR):
        ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
        despine(ax)

    fig.tight_layout(w_pad=2.0)
    fig.savefig(os.path.join(FIG_DIR, "fig_sweeps.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    fig_class()
    r = fig_mechanism()
    fig_sweeps()
    print(f"wrote 3 figures to {FIG_DIR}; measured TFA-vs-BPC r = {r:.4f}")
