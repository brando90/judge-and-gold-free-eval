#!/usr/bin/env python
"""Figures for the ICLR version of Paper D (round 2: plain units, one colour grammar).

Every plotted value is read from a committed JSON in papers/analysis/:
  fig1_teaser     (a) frontier_judge.json   (b) replrot_results.json, frontier_phase1_results.json,
                                               r2_realism_results.json (if present)
  fig2_selection  (a) accuracy_readouts.json [kpool]   (b) accuracy_readouts.json [repl, frontier_cli, sonnet]
  fig3_mechanism  (a) maskident_results.json (b) sep_continuum_results.json
  fig4_fix        (a) accuracy_readouts.json [kpool m1]  (b) r2_math_m1_results.json if present, else
                                               accuracy_readouts.json [kpool_variants]
  figA_inversion  ties_fullset.json (+ frozen MATH-500 values quoted in the technical report)
Colour = condition, everywhere: orange = blind, blue = reference shown, teal = blind-then-reveal,
grey = neither/placebo. Judges are distinguished by marker shape or hatch, never by colour.
"""

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
ANALYSIS = PAPER.parent / "analysis"
FIG = PAPER / "figures"
FIG.mkdir(exist_ok=True)

BLUE, ORANGE, TEAL, GREY = "#4269d0", "#c5541a", "#2a9d8f", "#9a9a9a"
INK, MUTED, GRID = "#1a1a1a", "#5f5f5f", "#e6e6e6"
MARK = {"Qwen2.5-7B": "o", "phi-4": "s", "Qwen2.5-14B": "D", "gemma-2-9b": "^", "Mistral-7B": "v"}

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.5, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "pdf.fonttype": 42, "axes.linewidth": 0.8, "axes.unicode_minus": True, "hatch.linewidth": 0.8,
})

Q, P = "Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"
KJ = [("Qwen2.5-7B", Q), ("phi-4", P), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct"),
      ("gemma-2-9b", "google__gemma-2-9b-it"), ("Mistral-7B", "mistralai__Mistral-7B-Instruct-v0.3")]


def load(name):
    f = ANALYSIS / name
    return json.loads(f.read_text()) if f.exists() else None


def sgn(x, d=1):
    return f"{x:+.{d}f}".replace("-", "−")


def style(ax, grid="y"):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=2.5, width=0.8)
    if grid:
        getattr(ax, f"{grid}axis").grid(True, color=GRID, lw=0.7, zorder=0)
    ax.set_axisbelow(True)


def label(ax, s, x=-0.14):
    ax.text(x, 1.05, s, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom")


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    d = os.environ.get("PREVIEW_DIR")
    if d:
        fig.savefig(Path(d) / f"{name}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def yerr(m, ci):
    return [[m - ci[0]], [ci[1] - m]]


acc = load("accuracy_readouts.json")

# ============================================================== Figure 1
fj = load("frontier_judge.json")
rot = load("replrot_results.json")
fr = load("frontier_phase1_results.json")
r2 = load("r2_realism_results.json") or {}

fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.5, 2.3), gridspec_kw={"width_ratios": [1.0, 1.45]})
rows = [("valid, matches\nthe reference", fj["noref_mean_match"], fj["ref_mean_match"]),
        ("valid, differs\nfrom the reference", fj["noref_mean_nomatch"], fj["ref_mean_nomatch"])]
for y, (lab, b, r) in enumerate(rows[::-1]):
    a1.barh(y + 0.19, b, height=0.34, color=ORANGE, zorder=3)
    a1.barh(y - 0.19, r, height=0.34, color=BLUE, zorder=3)
    a1.text(b + 0.2, y + 0.19, f"{b:.1f}", va="center", fontsize=7, color=MUTED)
    a1.text(r + 0.2, y - 0.19, f"{r:.1f}", va="center", fontsize=7, color=MUTED)
a1.set_yticks([0, 1], [l for l, _, _ in rows[::-1]])
a1.set_xlim(0, 12.5)
a1.set_ylim(-0.55, 1.95)
a1.set_xticks([0, 5, 10])
a1.set_xlabel("mean score (0–10)")
a1.set_title("Scores of correct answers", loc="left")
a1.legend(handles=[Patch(color=ORANGE, label="blind"), Patch(color=BLUE, label="reference shown")],
          loc="upper left", bbox_to_anchor=(-0.02, 1.02), ncol=2, frameon=False, handlelength=1.0, fontsize=6.8,
          columnspacing=0.8)
style(a1, "x")
label(a1, "a", x=-0.52)

cols = [("Qwen-7B", rot[f"{Q}__a"]), ("phi-4", rot[f"{P}__a"]), ("Sonnet 5", fr["rotation__a"])]
for key, lab in (("mtbench", "MT-Bench"), ("reason", "thinking")):
    rr = r2.get(key)
    if isinstance(rr, dict) and "rot" in rr:
        conv = {c: {"mean": rr["rot"][c][0], "ci": rr["rot"][c][1]} for c in ("gainer", "loser", "placebo")}
        cols.append((lab, {"gainers": conv["gainer"], "losers": conv["loser"], "placebo": conv["placebo"]}))
w = 0.3
GAP = 1.3
for i, (name, r) in enumerate(cols):
    i = i * GAP
    for dx, k, kw in ((-w, "gainers", dict(color=BLUE)), (0, "placebo", dict(color=GREY)),
                      (w, "losers", dict(facecolor="white", edgecolor=BLUE, hatch="/////", lw=0.8))):
        m, ci = r[k]["mean"], r[k]["ci"]
        a2.bar(i + dx, m, width=w - 0.04, zorder=3, **kw)
        a2.errorbar(i + dx, m, yerr=yerr(m, ci), fmt="none", ecolor=INK, elinewidth=0.8, capsize=1.8, zorder=4)
        if k != "placebo":
            a2.text(i + dx, (ci[1] + 0.3) if m > 0 else (ci[0] - 0.3), sgn(m), ha="center",
                    va="bottom" if m > 0 else "top", fontsize=6.8, color=MUTED)
a2.axhline(0, color=MUTED, lw=0.8, zorder=2)
a2.set_xticks([i * GAP for i in range(len(cols))], [c for c, _ in cols], fontsize=6.6)
a2.set_xlim(-0.6, (len(cols) - 1) * GAP + 0.6)
a2.set_ylim(-8, 9.5)
a2.set_ylabel("change in score of\nthe same text (0–10)")
a2.set_title("Swap the reference", loc="left")
a2.legend(handles=[Patch(color=BLUE, label="now matches it"), Patch(color=GREY, label="matches neither"),
                   Patch(facecolor="white", edgecolor=BLUE, hatch="/////", label="no longer matches")],
          loc="upper center", ncol=3, frameon=False, handlelength=1.1, fontsize=6.8, bbox_to_anchor=(0.45, -0.3), columnspacing=0.8)
style(a2)
label(a2, "b")
fig.tight_layout(w_pad=1.4)
save(fig, "fig1_teaser")

# ============================================================== Figure 2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.5, 2.3), gridspec_kw={"width_ratios": [1.0, 1.0]})
for y, (name, key) in enumerate(KJ[::-1]):
    d = acc["kpool"][key]
    for kk, off, face in (("k1", 0.16, "white"), ("kgt1", -0.16, BLUE)):
        m, ci, n = d[kk]["ref_minus_blind"]
        a1.plot([100 * ci[0], 100 * ci[1]], [y + off] * 2, color=BLUE, lw=1.0, zorder=3)
        a1.plot(100 * m, y + off, marker=MARK[name], ms=5, mfc=face, mec=BLUE, mew=1.0, ls="", zorder=4)
a1.axvline(0, color=MUTED, lw=0.8, zorder=2)
a1.set_yticks(range(len(KJ)), [n for n, _ in KJ[::-1]])
a1.set_xlim(-65, 45)
a1.set_xlabel("change in accuracy of the pick (points)")
a1.set_title("Showing the reference, by $k$", loc="left")
a1.legend(handles=[Line2D([], [], marker="o", ls="", mfc="white", mec=BLUE, label="$k{=}1$ (14 tasks)"),
                   Line2D([], [], marker="o", ls="", mfc=BLUE, mec=BLUE, label="$k{>}1$ (39 tasks)")],
          loc="upper center", frameon=False, handlelength=1.0, ncol=2, bbox_to_anchor=(0.45, -0.3), columnspacing=0.8)
style(a1, "x")
label(a1, "a", x=-0.33)

groups = [("Qwen-7B", acc["repl"][Q]["false_reject"]["blind_nonmatch"], acc["repl"][Q]["false_reject"]["ref_nonmatch"]),
          ("phi-4", acc["repl"][P]["false_reject"]["blind_nonmatch"], acc["repl"][P]["false_reject"]["ref_nonmatch"]),
          ("Sonnet 5", acc["repl_sonnet5_false_reject"]["blind_nonmatch"], acc["repl_sonnet5_false_reject"]["ref_nonmatch"]),
          ("Claude\nCLI", acc["frontier_cli"]["fail_nomatch_noref"], acc["frontier_cli"]["fail_nomatch_ref"])]
w = 0.36
for i, (name, b, r) in enumerate(groups):
    for dx, v, col in ((-w / 2, b, ORANGE), (w / 2, r, BLUE)):
        a2.bar(i + dx, 100 * v[0], width=w - 0.04, color=col, zorder=3)
        a2.errorbar(i + dx, 100 * v[0], yerr=yerr(100 * v[0], [100 * v[1][0], 100 * v[1][1]]), fmt="none",
                    ecolor=INK, elinewidth=0.8, capsize=1.8, zorder=4)
    a2.text(i + w / 2, 100 * r[1][1] + 2, f"{100 * r[0]:.0f}%", ha="center", va="bottom", fontsize=6.8, color=MUTED)
a2.set_xticks(range(len(groups)), [g for g, _, _ in groups])
a2.set_ylim(0, 100)
a2.set_ylabel("scored 3 or below (%)")
a2.set_title("Correct answers that differ from it", loc="left")
a2.legend(handles=[Patch(color=ORANGE, label="blind"), Patch(color=BLUE, label="reference shown")],
          loc="upper left", frameon=False, handlelength=1.0)
style(a2)
label(a2, "b")
fig.tight_layout(w_pad=1.2)
save(fig, "fig2_selection")

# ============================================================== Figure 3
mi = load("maskident_results.json")
sc = load("sep_continuum_results.json")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.5, 2.1), gridspec_kw={"width_ratios": [1.3, 1.0]})
forms = [("31", lambda j: (mi[f"{j}|a|ref (baseline)"]["margin"], mi[f"{j}|a|ref (baseline)"]["ci"])),
         ("thirty-\none", lambda j: (mi[f"{j}|a|refword"]["margin"], mi[f"{j}|a|refword"]["ci"])),
         ("30+1", lambda j: (mi[f"{j}|a|refexpr"]["margin"], mi[f"{j}|a|refexpr"]["ci"])),
         ("visible", lambda j: (mi[f"{j}|a|refsolmask"]["refsol"]["mean"], mi[f"{j}|a|refsolmask"]["refsol"]["ci"])),
         ("masked", lambda j: (mi[f"{j}|a|refsolmask"]["masked"]["mean"], mi[f"{j}|a|refsolmask"]["masked"]["ci"]))]
xpos = [0, 1, 2, 3.5, 4.7]
w = 0.36
for (lab, fn), x in zip(forms, xpos):
    for dx, j, kw in ((-w / 2, Q, dict(color=BLUE)), (w / 2, P, dict(facecolor="white", edgecolor=BLUE, hatch="/////", lw=0.8))):
        m, ci = fn(j)
        a1.bar(x + dx, m, width=w - 0.05, zorder=3, **kw)
        a1.errorbar(x + dx, m, yerr=yerr(m, ci), fmt="none", ecolor=INK, elinewidth=0.8, capsize=1.8, zorder=4)
a1.axvline(2.75, color=GRID, lw=1.0, zorder=1)
a1.text(1.0, 6.05, "bare reference", ha="center", fontsize=7, color=MUTED)
a1.text(4.1, 6.05, "worked solution,\nfinal answer", ha="center", va="bottom", fontsize=7, color=MUTED)
a1.axhline(0, color=MUTED, lw=0.8, zorder=2)
a1.set_xticks(xpos, [f for f, _ in forms])
a1.set_ylim(-1.6, 7.6)
a1.set_ylabel("anchoring margin\n(points, 0–10 scale)")
a1.set_title("How the reference is written", loc="left")
a1.legend(handles=[Patch(color=BLUE, label="Qwen2.5-7B"), Patch(facecolor="white", edgecolor=BLUE, hatch="/////", label="phi-4")],
          loc="upper center", frameon=False, handlelength=1.1, ncol=2, bbox_to_anchor=(0.5, -0.2))
style(a1)
label(a1, "a")

strata = [("scalar", "integer"), ("pair", "pair"), ("json", "JSON"), ("program", "program")]
for j, name, off in ((Q, "Qwen2.5-7B", -0.08), (P, "phi-4", 0.08)):
    for i, (s, _) in enumerate(strata):
        m, ci = sc[j][s]["infl"], sc[j][s]["infl_ci"]
        a2.errorbar(i + off, m, yerr=yerr(m, ci), fmt=MARK[name], color=BLUE, ms=4.5, mfc=BLUE if j == Q else "white",
                    mec=BLUE, elinewidth=0.9, capsize=1.8, zorder=4)
a2.axhline(0, color=MUTED, lw=0.8, zorder=2)
a2.set_xticks(range(4), [l for _, l in strata])
a2.set_xlim(-0.5, 3.5)
a2.set_ylim(-0.7, 2.2)
a2.set_xlabel("requested answer format")
a2.set_ylabel("added best-of-64\ninflation (SD)")
a2.set_title("What form the answer takes", loc="left")
a2.legend(handles=[Line2D([], [], marker="o", ls="", color=BLUE, label="Qwen2.5-7B"),
                   Line2D([], [], marker="s", ls="", mfc="white", mec=BLUE, label="phi-4")],
          loc="lower left", frameon=False, handlelength=1.0)
style(a2)
label(a2, "b")
fig.tight_layout(w_pad=1.3)
save(fig, "fig3_mechanism")

# ============================================================== Figure 4
m1r = load("r2_math_m1_results.json")
have_math = isinstance(m1r, dict) and any(isinstance(v, dict) for v in m1r.values())
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.5, 2.25), gridspec_kw={"width_ratios": [1.0, 1.0]})
for y, (name, key) in enumerate(KJ[::-1]):
    d = acc["kpool"][key]["kgt1"]
    (mr, cr, _), (mm, cm, _) = d["ref_minus_blind"], d["m1_minus_blind"]
    a1.annotate("", xy=(100 * mm, y), xytext=(100 * mr, y),
                arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.9, shrinkA=4, shrinkB=4, mutation_scale=7), zorder=2)
    for m, ci, col, off in ((mr, cr, BLUE, 0.13), (mm, cm, TEAL, -0.13)):
        a1.plot([100 * ci[0], 100 * ci[1]], [y + off] * 2, color=col, lw=1.0, zorder=3)
        a1.plot(100 * m, y + off, marker=MARK[name], ms=5, color=col, ls="", zorder=4)
a1.axvline(0, color=ORANGE, lw=0.9, zorder=2)
a1.text(1.5, len(KJ) - 0.5, "blind", fontsize=7, color=ORANGE, va="center")
a1.set_yticks(range(len(KJ)), [n for n, _ in KJ[::-1]])
a1.set_xlim(-50, 20)
a1.set_xlabel("change in accuracy vs. blind (points)")
a1.set_title("Multi-answer tasks ($k{>}1$)", loc="left")
style(a1, "x")
label(a1, "a", x=-0.33)

if have_math:
    names = [("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct")]
    w = 0.26
    for i, (name, key) in enumerate(names):
        d = m1r.get(key)
        if not isinstance(d, dict):
            continue
        for dx, k, col in ((-w, "acc_blind", ORANGE), (0, "acc_ref", BLUE), (w, "acc_m1", TEAL)):
            a2.bar(i + dx, 100 * d[k], width=w - 0.04, color=col, zorder=3)
            a2.text(i + dx, 100 * d[k] + 1.2, f"{100 * d[k]:.0f}", ha="center", fontsize=6.8, color=MUTED)
    a2.set_xticks(range(len(names)), [n for n, _ in names])
    a2.set_ylim(0, 110)
    a2.set_yticks([0, 25, 50, 75, 100])
    a2.set_ylabel("accuracy of the chosen\nanswer (%, best of 64)")
    a2.set_title("Unique answers (MATH-500)", loc="left")
    fig.legend(handles=[Patch(color=ORANGE, label="blind"), Patch(color=BLUE, label="reference shown"),
                        Patch(color=TEAL, label="blind, then reveal")], loc="lower center", frameon=False,
               handlelength=1.0, ncol=3, bbox_to_anchor=(0.5, -0.08), columnspacing=1.2)
else:
    var = [("ref", "reference\nshown"), ("m1", "reveal +\nown score"), ("m1noscore", "reveal,\nno score"),
           ("m1prev", "reveal +\nneutral"), ("m1indep", "reveal +\nother judge")]
    for jdx, (name, key) in enumerate([("Qwen2.5-7B", Q), ("phi-4", P), ("gemma-2-9b", "google__gemma-2-9b-it")]):
        for i, (k, _) in enumerate(var):
            m, ci, _ = acc["kpool_variants"][key][f"{k}_minus_blind"]
            col = BLUE if k == "ref" else TEAL
            x = i + (jdx - 1) * 0.2
            a2.plot([x, x], [100 * ci[0], 100 * ci[1]], color=col, lw=0.9, zorder=3)
            a2.plot(x, 100 * m, marker=MARK[name], ms=4.5, color=col, ls="", zorder=4)
    a2.set_xticks(range(len(var)), [l for _, l in var], fontsize=6.8)
    a2.axhline(0, color=ORANGE, lw=0.9)
    a2.set_ylabel("change in accuracy vs.\nblind (points)")
    a2.set_title("Variants of the reveal call", loc="left")
style(a2)
label(a2, "b")
fig.tight_layout(w_pad=1.3)
save(fig, "fig4_fix")

# ============================================================== Appendix figure
full = load("ties_fullset.json")
SIZES = ["1.5B", "3B", "7B", "14B"]
MATH = {"1.5B": (0.88, 0.16), "3B": (0.44, 0.07), "7B": (0.80, 0.18), "14B": (0.63, 0.05)}
TIES = {s: (full[f"ties__Qwen__Qwen2.5-{s}-Instruct__noref"]["excess_gap"],
            full[f"ties__Qwen__Qwen2.5-{s}-Instruct__ref"]["excess_gap"]) for s in SIZES}
fig, axes = plt.subplots(1, 2, figsize=(5.5, 2.0), sharey=True)
for ax, data, title in ((axes[0], MATH, "MATH-500 (unique answer)"), (axes[1], TIES, "RewardBench-2 Ties (several valid)")):
    for y, s in enumerate(SIZES):
        b, r = data[s]
        ax.annotate("", xy=(r, y), xytext=(b, y), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.0, shrinkA=4, shrinkB=4, mutation_scale=8))
        ax.plot([b], [y], "o", ms=5.5, color=ORANGE, zorder=3)
        ax.plot([r], [y], "o", ms=5.5, color=BLUE, zorder=3)
    ax.set_yticks(range(4), SIZES)
    ax.set_xlim(-0.1, 1.6)
    ax.set_title(title, loc="left")
    ax.set_xlabel("best-of-64 inflation (SD)")
    style(ax, "x")
axes[0].set_ylabel("Qwen2.5 judge size")
fig.legend(handles=[Line2D([], [], marker="o", ls="", color=ORANGE, label="blind"),
                    Line2D([], [], marker="o", ls="", color=BLUE, label="reference shown")],
           loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False)
fig.tight_layout()
save(fig, "figA_inversion")
print("figures written; R2-B in fig1:", [c for c, _ in cols][3:], "; math panel:", have_math)
