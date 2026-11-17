#!/usr/bin/env python3
"""Generate vector (PDF) figures for the AAAI-27 EvalAIScientists paper.

Outputs (relative to the paper directory):
  figures/fig_class.pdf      lollipop of Pearson r vs human soundness, all canonical signals
  figures/fig_mechanism.pdf  scatter of per-solution TFA vs reference bits-per-character
  figures/fig_sweeps.pdf     position-weight decay sweep + completion-curve depth rise

Data sources:
  papers/analysis/canonical_validity.json
  papers/analysis/free_baseline.json
  experiments/tfa-vs-judge/runs/tfa_bpc_math500.jsonl
"""

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PAPER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(os.path.dirname(PAPER_DIR))
FIG_DIR = os.path.join(PAPER_DIR, "figures")
CANONICAL = os.path.join(REPO_ROOT, "papers", "analysis", "canonical_validity.json")
FREE_BASELINE = os.path.join(REPO_ROOT, "papers", "analysis", "free_baseline.json")
TFA_BPC = os.path.join(
    REPO_ROOT, "experiments", "tfa-vs-judge", "runs", "tfa_bpc_math500.jsonl"
)

MATCHING = "#c5541a"
VERIFICATION = "#4269d0"
INK = "#1f2430"
MUTED = "#5a6270"
GRID = "#d7dae0"

plt.rcParams.update(
    {
        "font.size": 9.5,
        "axes.labelsize": 9.5,
        "axes.titlesize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 8.5,
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


SIGNALS = [
    ("u1", "Unigram-F1", "matching"),
    ("logprob", "Gold-token logprob ($n{=}42$)", "matching"),
    ("tfa", "Teacher-forced accuracy (TFA)", "matching"),
    ("tfidf", "TF-IDF cosine", "matching"),
    ("embed", "Sentence embeddings", "matching"),
    ("pv_v0", "Completion curve ($k{=}0$)", "verification"),
    ("pv_v25", "Completion curve ($k{=}0.25$)", "verification"),
    ("pv_v5", "Completion curve ($k{=}0.50$)", "verification"),
    ("pv_v75", "Completion curve ($k{=}0.75$)", "verification"),
    ("pv_mean", "Completion-curve mean", "verification"),
    ("free_bit", "Extracted-answer check", "verification"),
    ("critic_opus", "LLM critic (Claude)", "judge"),
    ("judge_ref", "LLM judge (referenced)", "judge"),
    ("critic_gpt", "LLM critic (GPT)", "judge"),
]


def fig_class():
    with open(CANONICAL) as f:
        data = json.load(f)["signals"]
    with open(FREE_BASELINE) as f:
        fb = json.load(f)["answer_correct_vs_soundness"]
    data["free_bit"] = {"pearson": fb["r"], "ci": fb["ci"]}

    fig, ax = plt.subplots(figsize=(5.5, 4.1))
    ys = np.arange(len(SIGNALS))

    for y, (key, _label, cls) in zip(ys, SIGNALS):
        d = data[key]
        r, (lo, hi) = d["pearson"], d["ci"]
        color = MATCHING if cls == "matching" else VERIFICATION
        filled = cls != "judge"
        ax.plot([lo, hi], [y, y], color=color, lw=1.7, solid_capstyle="round", zorder=2)
        ax.scatter(
            [r],
            [y],
            s=46,
            facecolor=color if filled else "white",
            edgecolor=color,
            linewidth=1.5,
            zorder=3,
        )

    ax.axvline(0.0, color=MUTED, lw=0.9, ls="--", zorder=0)
    ax.axvline(0.83, color=MUTED, lw=0.8, ls=":", zorder=0)
    ax.axvline(0.91, color=MUTED, lw=0.8, ls=":", zorder=0)
    ax.text(
        0.99,
        len(SIGNALS) + 0.05,
        "dotted: inter-rater 0.83 / ceiling 0.91",
        ha="right",
        va="center",
        fontsize=8.0,
        color=MUTED,
    )

    ax.set_yticks(ys)
    ax.set_yticklabels([s[1] for s in SIGNALS])
    ax.set_xlabel("Pearson $r$ vs. blind soundness (95% CI)")
    ax.set_xlim(-0.63, 1.03)
    ax.set_ylim(-0.7, len(SIGNALS) + 0.7)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    despine(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)

    handles = [
        plt.Line2D([], [], marker="o", ls="-", color=MATCHING, label="reference-matching"),
        plt.Line2D([], [], marker="o", ls="-", color=VERIFICATION, label="verification"),
        plt.Line2D(
            [],
            [],
            marker="o",
            ls="-",
            color=VERIFICATION,
            markerfacecolor="white",
            label="LLM judges",
        ),
    ]
    ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.0, 1.01),
        frameon=False,
        handlelength=1.1,
        columnspacing=0.9,
        ncol=3,
    )
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig_class.pdf"), bbox_inches="tight")
    plt.close(fig)


def fig_mechanism():
    tfa, bpc = [], []
    with open(TFA_BPC) as f:
        for line in f:
            rec = json.loads(line)
            tfa.append(rec["tfa"])
            bpc.append(rec["bpc"])
    tfa, bpc = np.asarray(tfa), np.asarray(bpc)
    r = np.corrcoef(bpc, tfa)[0, 1]

    fig, ax = plt.subplots(figsize=(4.6, 3.3))
    ax.scatter(bpc, tfa, s=4, alpha=0.12, color=MATCHING, edgecolors="none", rasterized=True)

    slope, intercept = np.polyfit(bpc, tfa, 1)
    xs = np.linspace(bpc.min(), bpc.max(), 100)
    ax.plot(xs, slope * xs + intercept, color=INK, lw=1.6)
    ax.annotate(
        f"$r = {r:.3f}$",
        xy=(0.97, 0.93),
        xycoords="axes fraction",
        ha="right",
        va="top",
        fontsize=10.5,
        color=INK,
    )

    ax.set_xlabel("reference bits-per-character (same model)")
    ax.set_ylabel("teacher-forced accuracy (TFA)")
    ax.grid(color=GRID, lw=0.6, zorder=0)
    despine(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig_mechanism.pdf"), dpi=300)
    plt.close(fig)
    return r


def fig_sweeps():
    gammas = ["uniform", "0.5", "1", "2", "4", "8", "last-16", "last-4"]
    rho = [0.126, 0.126, 0.154, 0.042, 0.014, -0.007, 0.028, -0.371]
    null = 0.02

    ks = [0, 0.25, 0.5, 0.75]
    pv = [0.54, 0.68, 0.76, 0.78]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.6, 2.95))

    xs = np.arange(len(gammas))
    axL.axhline(null, color=MUTED, lw=0.9, ls="--", zorder=1)
    axL.text(0.05, -0.055, "answer-only null ($+0.02$)", fontsize=8.5, color=MUTED)
    axL.axhline(0.0, color=GRID, lw=0.8, zorder=0)
    axL.plot(xs, rho, "-o", color=MATCHING, lw=1.8, markersize=5.5, zorder=2)
    axL.set_xticks(xs)
    axL.set_xticklabels(gammas, rotation=45, ha="right")
    axL.set_xlabel("position weight $\\gamma$")
    axL.set_ylabel("12-model ranking $\\rho$")
    axL.set_title("up-weighting late tokens: decay", fontsize=9.5, color=INK)
    axL.set_ylim(-0.45, 0.30)

    with open(FREE_BASELINE) as f:
        free_bit = json.load(f)["answer_correct_vs_soundness"]["r"]
    axR.axhline(free_bit, color=MUTED, lw=0.9, ls="--", zorder=1)
    axR.text(
        -0.04,
        free_bit + 0.015,
        f"extracted-answer check ($+{free_bit:.2f}$)",
        fontsize=8.5,
        color=MUTED,
    )
    axR.plot(ks, pv, "-o", color=VERIFICATION, lw=1.8, markersize=5.5, zorder=2)
    for k, v in zip(ks, pv):
        axR.annotate(
            f"$+{v:.2f}$",
            xy=(k, v),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            fontsize=8.8,
            color=INK,
        )
    axR.set_xticks(ks)
    axR.set_xlim(-0.08, 0.83)
    axR.set_xlabel("truncation depth $k$")
    axR.set_ylabel("Pearson $r$ vs. human soundness")
    axR.set_title("completion curve: rise below check", fontsize=9.5, color=INK)
    axR.set_ylim(0.45, 1.01)

    for ax in (axL, axR):
        ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
        despine(ax)

    fig.tight_layout(w_pad=1.8)
    fig.savefig(os.path.join(FIG_DIR, "fig_sweeps.pdf"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_class()
    r = fig_mechanism()
    fig_sweeps()
    print(f"wrote 3 figures to {FIG_DIR}; measured TFA-vs-BPC r = {r:.4f}")
