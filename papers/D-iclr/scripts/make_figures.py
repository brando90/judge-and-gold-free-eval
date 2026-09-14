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
MARK = {"Qwen2.5-7B": "o", "phi-4": "s", "Qwen2.5-14B": "D", "gemma-2-9b": "v", "Mistral-7B": "<", "Sonnet 5": "^",
        "Qwen3-8B": "P", "Qwen3-14B": "X"}  # one judge -> one marker, in every figure

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"], "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
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
s5 = acc["repl_sonnet5_scores"]
rows = [("correct, matches\nthe reference", s5["noref"]["match"][0], s5["ref"]["match"][0]),
        ("correct, differs\nfrom the reference", s5["noref"]["nonmatch"][0], s5["ref"]["nonmatch"][0])]
CIS = {rows[0][0]: (s5["noref"]["match"][1], s5["ref"]["match"][1]), rows[1][0]: (s5["noref"]["nonmatch"][1], s5["ref"]["nonmatch"][1])}
for y, (lab, b, r) in enumerate(rows[::-1]):
    a1.barh(y + 0.19, b, height=0.34, color=ORANGE, zorder=3)
    a1.barh(y - 0.19, r, height=0.34, color=BLUE, zorder=3)
    ci_b, ci_r = CIS[lab]
    a1.errorbar(b, y + 0.19, xerr=[[b - ci_b[0]], [ci_b[1] - b]], fmt="none", ecolor=INK, elinewidth=0.8, capsize=1.6, zorder=4)
    a1.errorbar(r, y - 0.19, xerr=[[r - ci_r[0]], [ci_r[1] - r]], fmt="none", ecolor=INK, elinewidth=0.8, capsize=1.6, zorder=4)
    a1.text(max(b, ci_b[1]) + 0.25, y + 0.19, f"{b:.1f}", va="center", fontsize=7, color=MUTED)
    a1.text(max(r, ci_r[1]) + 0.25, y - 0.19, f"{r:.1f}", va="center", fontsize=7, color=MUTED)
a1.set_yticks([0, 1], [l for l, _, _ in rows[::-1]])
a1.set_xlim(0, 12.5)
a1.set_ylim(-0.55, 1.95)
a1.set_xticks([0, 5, 10])
a1.set_xlabel("mean score (0–10)")
a1.set_title("Sonnet 5 scores", loc="left")
a1.legend(handles=[Patch(color=ORANGE, label="blind"), Patch(color=BLUE, label="reference shown")],
          loc="upper left", bbox_to_anchor=(-0.02, 1.02), ncol=2, frameon=False, handlelength=1.0, fontsize=6.8,
          columnspacing=0.8)
style(a1, "x")
label(a1, "a", x=-0.52)

r4res = load("r4_results.json") or {}


def conv4(x):
    return {"gainers": {"mean": x["gainer"][0], "ci": x["gainer"][1]}, "losers": {"mean": x["loser"][0], "ci": x["loser"][1]},
            "placebo": {"mean": x["placebo"][0], "ci": x["placebo"][1]}}


q7rot = conv4(r4res["rotation"]["escore"]) if r4res.get("rotation") else rot[f"{Q}__a"]  # exact estimator (R4-A)
cols = [("Qwen-7B", q7rot), ("phi-4", rot[f"{P}__a"]), ("Sonnet 5", fr["rotation__a"])]
for key, lab in ():
    rr = r2.get(key)
    if isinstance(rr, dict) and "rot" in rr:
        conv = {c: {"mean": rr["rot"][c][0], "ci": rr["rot"][c][1]} for c in ("gainer", "loser", "placebo")}
        cols.append((lab, {"gainers": conv["gainer"], "losers": conv["loser"], "placebo": conv["placebo"]}))
w = 0.3
GAP = 1.3
for i, (name, r) in enumerate(cols):
    i = i * GAP
    for dx, k, kw in ((-w, "gainers", dict(color="#3a3a3a")), (0, "placebo", dict(color="#bdbdbd")),
                      (w, "losers", dict(facecolor="white", edgecolor="#3a3a3a", hatch="/////", lw=0.8))):
        m, ci = r[k]["mean"], r[k]["ci"]
        a2.bar(i + dx, m, width=w - 0.04, zorder=3, **kw)
        a2.errorbar(i + dx, m, yerr=yerr(m, ci), fmt="none", ecolor=INK, elinewidth=0.8, capsize=1.8, zorder=4)
        if k != "placebo":  # the matches-neither values are small and are given in the caption
            a2.text(i + dx, (ci[1] + 0.3) if m > 0 else (ci[0] - 0.3), sgn(m), ha="center",
                    va="bottom" if m > 0 else "top", fontsize=6.8, color=MUTED)
a2.axhline(0, color=MUTED, lw=0.8, zorder=2)
a2.set_xticks([i * GAP for i in range(len(cols))], ["Qwen2.5-7B", "phi-4", "Sonnet 5"], fontsize=7.5)
a2.set_xlim(-0.6, (len(cols) - 1) * GAP + 0.6)
a2.set_ylim(-8, 9.5)
a2.set_ylabel("change in score of\nthe same text (0–10)")
a2.set_title("Swap the reference", loc="left")
style(a2)
label(a2, "b", x=-0.28)
fig.tight_layout(w_pad=2.2)
a2.legend(handles=[Patch(color="#3a3a3a", label="reference moved onto the answer"), Patch(color="#bdbdbd", label="matches neither"),
                   Patch(facecolor="white", edgecolor="#3a3a3a", hatch="/////", label="reference moved off the answer")],
          loc="upper center", ncol=1, frameon=False, handlelength=1.1, fontsize=6.4, bbox_to_anchor=(0.5, -0.2))
save(fig, "fig1_teaser")

# Figure 1 data panel for the concept diagram (figures/fig1_concept.tex): the swap result over the pool.
# Drawn at the size it is placed (natural size inside the TikZ picture) so every label prints at 7 pt or larger.
fig, ax = plt.subplots(figsize=(2.0, 1.36))
for i, (name, r) in enumerate(cols):
    i = i * GAP
    for dx, k, kw in ((-w, "gainers", dict(color=BLUE)), (0, "placebo", dict(color="#bdbdbd")),
                      (w, "losers", dict(facecolor="white", edgecolor=BLUE, hatch="/////", lw=0.8))):
        m, ci = r[k]["mean"], r[k]["ci"]
        ax.bar(i + dx, m, width=w - 0.04, zorder=3, **kw)
        ax.errorbar(i + dx, m, yerr=yerr(m, ci), fmt="none", ecolor=INK, elinewidth=0.8, capsize=1.4, zorder=4)
        if k != "placebo":
            ax.text(i + dx, (ci[1] + 0.3) if m > 0 else (ci[0] - 0.3), sgn(m), ha="center",
                    va="bottom" if m > 0 else "top", fontsize=7.2, color=MUTED)
ax.axhline(0, color=MUTED, lw=0.9, ls=(0, (3, 2)), zorder=2)
ax.set_xticks([i * GAP for i in range(len(cols))], ["Qwen2.5-7B", "phi-4", "Sonnet 5\n(API)"], fontsize=7.4)
ax.set_xlim(-0.8, (len(cols) - 1) * GAP + 0.7)
ax.set_ylim(-8.2, 9.2)
ax.set_yticks([-6, -3, 0, 3, 6])
ax.tick_params(axis="y", labelsize=7.4)
ax.set_ylabel("change in score", fontsize=7.6)
style(ax)
ax.legend(handles=[Patch(color=BLUE, label="reference moved onto its answer"), Patch(color="#bdbdbd", label="answer matches neither"),
                   Patch(facecolor="white", edgecolor=BLUE, hatch="/////", label="reference moved off its answer"),
                   Line2D([], [], color=MUTED, ls=(0, (3, 2)), lw=0.9, label="an answer key predicts 0")],
          loc="upper center", ncol=1, frameon=False, handlelength=1.1, fontsize=7.2, bbox_to_anchor=(0.4, -0.25))
save(fig, "fig1_rotation")

# ============================================================== Figure 2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.5, 2.3), gridspec_kw={"width_ratios": [1.25, 1.0]})
ks = ["k1", "k2", "k4", "k8", "k16"]
xs = [1, 2, 4, 8, 16]
for name, key in KJ:
    d = acc["kpool"][key]
    ys = [100 * d[k]["ref_minus_blind"][0] for k in ks]
    main = name in ("Qwen2.5-7B", "phi-4")
    if main:
        for x, k in zip(xs, ks):
            lo, hi = d[k]["ref_minus_blind"][1]
            a1.plot([x, x], [100 * lo, 100 * hi], color=BLUE, lw=0.8, alpha=0.6, zorder=2)
    a1.plot(xs, ys, marker=MARK[name], ms=4.5 if main else 3.5, lw=1.5 if main else 0.8, color=BLUE,
            alpha=1.0 if main else 0.35, zorder=3 if main else 1, label=name)
a1.axhline(0, color=ORANGE, lw=0.9, zorder=1)
a1.text(1.05, 9, "blind", fontsize=7, color=ORANGE, va="bottom")
a1.set_xscale("log", base=2)
a1.set_xticks(xs, [str(x) for x in xs])
a1.minorticks_off()
a1.set_ylim(-100, 45)
a1.set_xlabel("valid answers per question, $k$")
a1.set_ylabel("change in accuracy of\nthe pick (points)")
a1.set_title("Showing the reference, by $k$", loc="left")
a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), frameon=False, fontsize=6.3, handlelength=1.6, ncol=3, columnspacing=0.8, labelspacing=0.2)
style(a1)
label(a1, "a")

groups = [("Qwen2.5-7B", acc["repl"][Q]["false_reject"]["blind_nonmatch"], acc["repl"][Q]["false_reject"]["ref_nonmatch"]),
          ("phi-4", acc["repl"][P]["false_reject"]["blind_nonmatch"], acc["repl"][P]["false_reject"]["ref_nonmatch"]),
          ("Sonnet 5", acc["repl_sonnet5_false_reject"]["blind_nonmatch"], acc["repl_sonnet5_false_reject"]["ref_nonmatch"])]
w = 0.36
for i, (name, b, r) in enumerate(groups):
    for dx, v, col in ((-w / 2, b, ORANGE), (w / 2, r, BLUE)):
        a2.bar(i + dx, 100 * v[0], width=w - 0.04, color=col, zorder=3)
        a2.errorbar(i + dx, 100 * v[0], yerr=yerr(100 * v[0], [100 * v[1][0], 100 * v[1][1]]), fmt="none",
                    ecolor=INK, elinewidth=0.8, capsize=1.8, zorder=4)
    a2.text(i + w / 2, 100 * r[1][1] + 2, f"{100 * r[0]:.0f}%", ha="center", va="bottom", fontsize=6.8, color=MUTED)
a2.set_xticks(range(len(groups)), [g for g, _, _ in groups])
a2.set_ylim(0, 40)
a2.set_ylabel("scored 3 or below (%)")
a2.set_title("Correct answers that differ from it", loc="left")
a2.legend(handles=[Patch(color=ORANGE, label="blind"), Patch(color=BLUE, label="reference shown")],
          loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, handlelength=1.0)
style(a2)
label(a2, "b")
fig.tight_layout(w_pad=1.2)
save(fig, "fig2_selection")

# ============================================================== Figure: reasoning and verification
# a: swap loss (reference moved off a correct answer): r3_sonnet_results.json (Sonnet 5 CLI arms), r2_realism_results.json
#    (MT-Bench template), r3_toggle_results.json and r4_toggle14b_results.json (Qwen3).
# b: false-rejection change on MACE, thinking off vs. on: r3_toggle_results.json and r4_toggle14b_results.json (Qwen3),
#    r8_sonnet_results.json (Sonnet 5 API, thinking disabled) and r19b_sonnet_think_results.json (Sonnet 5 API, adaptive thinking).
tog = load("r3_toggle_results.json")
t14 = (load("r4_toggle14b_results.json") or {}).get("Qwen3-14B", {})
r2r = load("r2_realism_results.json")
LIGHT = "#b7c6ee"
KIND3 = {"score": dict(marker="o", mfc=BLUE, mec=BLUE, ms=5.0),
         "rationale": dict(marker="o", mfc="white", mec=BLUE, mew=1.1, ms=5.0),
         "think": dict(marker="D", mfc="white", mec=BLUE, mew=1.1, ms=4.4)}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.2, 2.9), gridspec_kw={"width_ratios": [1.05, 0.85], "wspace": 1.55})
fig.subplots_adjust(left=0.29, right=0.975, top=0.92, bottom=0.25)
r3s = load("r3_sonnet_results.json") or {}
rows = [("hdr", "Sonnet 5 (CLI), 60 tasks")]
for arm, lab, kind in (("fast", "score only", "score"), ("visible", "explains first", "rationale"), ("think", "thinking on", "think")):
    v = (r3s.get(arm) or {}).get("rot") if isinstance(r3s.get(arm), dict) else None
    if v and v.get("loser"):
        rows.append((lab, v["loser"][0], v["loser"][1], kind))
rows.append(("hdr", "Open judges, 120-task subsample"))
rows.append(("Qwen2.5-7B, MT-Bench template", r2r["mtbench"]["rot"]["loser"][0], r2r["mtbench"]["rot"]["loser"][1], "rationale"))
rows.append(("Qwen3-8B, thinking off", tog["off"]["rot"]["loser"][0], tog["off"]["rot"]["loser"][1], "rationale"))
rows.append(("Qwen3-8B, thinking on", tog["on"]["rot"]["loser"][0], tog["on"]["rot"]["loser"][1], "think"))
for arm, lab, kind in (("off", "Qwen3-14B, thinking off", "rationale"), ("on", "Qwen3-14B, thinking on", "think")):
    v = (t14.get(arm) or {}).get("rot")
    if v:
        rows.append((lab, v["loser"][0], v["loser"][1], kind))
n = len(rows)
ticks = []
for pos, r in enumerate(rows):
    y = n - 1 - pos
    if r[0] == "hdr":
        ticks.append((y, r[1], True))
        if pos:
            a1.axhline(y + 0.5, color="#d9d9d9", lw=0.6, zorder=1)
        continue
    lab, m, ci, kind = r
    a1.plot([ci[0], ci[1]], [y, y], color=BLUE, lw=1.0, zorder=3)
    a1.plot(m, y, ls="", zorder=4, **KIND3[kind])
    a1.text(1.0, y, sgn(m, 2), fontsize=7.4, color=MUTED, ha="left", va="center")
    ticks.append((y, lab, False))
a1.axvline(0, color=MUTED, lw=0.8, zorder=2)
a1.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=7.8)
for tl, tk, t in zip(a1.get_yticklabels(), a1.yaxis.get_major_ticks(), ticks):
    if t[2]:
        tl.set_fontweight("bold"); tk.tick1line.set_visible(False)
a1.set_xlim(-4.6, 2.3)
a1.set_xticks([-4, -3, -2, -1, 0])
a1.set_ylim(-0.6, n - 0.4)
a1.tick_params(axis="x", labelsize=7.8)
a1.set_xlabel("score change when the reference\nmoves off a correct answer (points)", fontsize=8)
a1.set_title("a   Arithmetic, same text", loc="left", fontsize=9, fontweight="bold")
style(a1, "x")
a1.legend(handles=[Line2D([], [], ls="", label="score only", **KIND3["score"]),
                   Line2D([], [], ls="", label="explanation first", **KIND3["rationale"]),
                   Line2D([], [], ls="", label="thinking on", **KIND3["think"])],
          loc="upper center", bbox_to_anchor=(0.25, -0.3), ncol=3, frameon=False, fontsize=7.6, handlelength=0.9,
          columnspacing=0.9, handletextpad=0.3)

r7fr = (load("r7_posthoc_results.json") or {}).get("false_reject_change", {})
r5s = load("r5_sonnet_mace_results.json") or {}


def _fr(v):
    return None if v is None else (100 * v[0], [100 * v[1][0], 100 * v[1][1]])


def _sub(src, arm):
    return ((src.get(arm) or {}).get("macesub") or {}).get("false_reject_diff")


groups = [("Qwen3-8B\n(explains first / thinks)", _fr(_sub(tog, "off")), _fr(_sub(tog, "on"))),
          ("Qwen3-14B\n(explains first / thinks)", _fr(_sub(t14, "off")), _fr(_sub(t14, "on"))),
          ("Sonnet 5, API\n(score only / thinks)", _fr(((load("r8_sonnet_results.json") or {}).get("pools", {}).get("mace", {}).get("oracle") or {}).get("FR")),
           _fr(((load("r19b_sonnet_think_results.json") or {}).get("pools", {}).get("mace", {}).get("oracle") or {}).get("FR")))]
h = 0.38
n_g = len(groups)
for i, (lab, off, on) in enumerate(groups):
    y = n_g - 1 - i
    for dy, v, col in ((h / 2, off, BLUE), (-h / 2, on, LIGHT)):
        if v is None:
            continue
        a2.barh(y + dy, v[0], height=h - 0.05, color=col, zorder=3)
        a2.errorbar(v[0], y + dy, xerr=[[v[0] - v[1][0]], [v[1][1] - v[0]]], fmt="none", ecolor=MUTED, elinewidth=0.8, capsize=1.6, zorder=4)
        a2.text(max(v[1][1], v[0], 0) + 2.5, y + dy, sgn(v[0], 1), fontsize=7.2, color=INK, va="center", ha="left")
a2.axvline(0, color=MUTED, lw=0.8, zorder=2)
a2.set_yticks(range(n_g), [g[0] for g in groups][::-1], fontsize=7.8)
a2.set_ylim(-0.6, n_g - 0.4)
a2.set_xlim(-2, 66)
a2.set_xticks([0, 20, 40, 60])
a2.tick_params(axis="x", labelsize=7.8)
a2.set_xlabel("false rejections, reference\nminus blind (pp)", fontsize=8)
a2.set_title("b   Factual questions", loc="left", fontsize=9, fontweight="bold")
a2.legend(handles=[Patch(color=BLUE, label="no thinking mode"), Patch(color=LIGHT, label="thinking on")],
          loc="upper center", bbox_to_anchor=(0.3, -0.3), ncol=2, frameon=False, handlelength=1.0, fontsize=7.6, columnspacing=1.0)
style(a2, "x")
save(fig, "fig2_reasoning")

# ============================================================== Figure 3 (main): answers the judge accepts blind, and thinking
# a: correct answers the judge accepts without a reference. API judges: a blind score of 10 (r20a_{sonnet,opus}_retest.json, which
#    also holds a second blind call through the same interface); arithmetic rows pool the replication and k-pool subsamples. Open
#    judges: a blind expected score at or above the lowest threshold that at most 3% of wrong answers reach
#    (r20d_matched_acceptance.json; expected scores are deterministic, so a second call would repeat the first). Plotted: the share
#    scored 3 or below with the reference, for answers that differ from it and answers that match it, and on the second blind call.
# b: points lost when the reference moves off a correct answer, thinking off and on: r3_sonnet_results.json (Sonnet 5 CLI, score
#    only vs thinking), r3_toggle_results.json (Qwen3-8B), r4_toggle14b_results.json (Qwen3-14B); Qwen3 with thinking off explains first.
# c: rise in false rejections on factual MACE questions, thinking off and on: the same Qwen3 files; Sonnet 5 API with thinking
#    disabled (r8_sonnet_results.json) and adaptive (r19b_sonnet_think_results.json).
RA = {"Sonnet 5": load("r20a_sonnet_retest.json"), "Opus 5": load("r20a_opus_retest.json")}
MD = load("r20d_matched_acceptance.json")
S8f, S19f = load("r8_sonnet_results.json"), load("r19b_sonnet_think_results.json")
if all(RA.values()) and MD and tog and t14 and S8f and S19f:
    def _share(d, pools, grp, key):
        return sum(d[p][grp][key] for p in pools) / sum(d[p][grp]["n"] for p in pools)

    MA = load("r21a_mace_acceptance.json") or {}  # open judges on MACE at the 3% threshold (post hoc)

    def _open(keys, grp):  # matched-threshold shares pooled over the constructed pools, weighted by answers
        n = sum(MD[k][grp]["n"] for k in keys)
        return sum(MD[k][grp]["n"] * MD[k][grp]["share_le3_with_reference"] for k in keys) / n

    rows = [("hdr", "Factual (MACE)")]
    for jn in ("Sonnet 5", "Opus 5"):
        rows.append((f"{jn} (API)", _share(RA[jn], ["mace"], "nonmatch", "referenced_le3"), _share(RA[jn], ["mace"], "match", "referenced_le3"),
                     _share(RA[jn], ["mace"], "nonmatch", "retest_le3")))
    for jn in ("Qwen2.5-7B", "phi-4"):
        x = MA.get(f"{jn}|target3")
        if x:
            rows.append((jn, x["nonmatch"]["share_le3_with_reference"], x["match"]["share_le3_with_reference"], None))
    rows.append(("hdr", "Arithmetic"))
    for jn in ("Sonnet 5", "Opus 5"):
        pools = ["repl", "kpool"]
        rows.append((f"{jn} (API)", _share(RA[jn], pools, "nonmatch", "referenced_le3"), _share(RA[jn], pools, "match", "referenced_le3"),
                     _share(RA[jn], pools, "nonmatch", "retest_le3")))
    for jn, keys in (("Qwen2.5-7B", ["repl|Qwen2.5-7B", "kpool|Qwen2.5-7B"]), ("phi-4", ["repl|phi-4", "kpool|phi-4"]),
                     ("Qwen2.5-14B", ["kpool|Qwen2.5-14B"]), ("gemma-2-9b", ["kpool|gemma-2-9b"])):
        rows.append((jn, _open(keys, "nonmatch"), _open(keys, "match"), None))
    fig = plt.figure(figsize=(5.5, 2.75))
    a1 = fig.add_axes([0.235, 0.33, 0.27, 0.61])
    a3 = fig.add_axes([0.745, 0.47, 0.235, 0.4])
    n = len(rows)
    ticks = []
    for pos, r in enumerate(rows):
        y = n - 1 - pos
        if r[0] == "hdr":
            ticks.append((y, r[1], True))
            if pos:
                a1.axhline(y + 0.5, color="#d9d9d9", lw=0.6, zorder=1)
            continue
        lab, nm, m, rt = r
        a1.plot([0, 100 * nm], [y, y], color=BLUE, lw=1.0, alpha=0.45, zorder=2)
        a1.plot(100 * nm, y, "o", ms=4.8, mfc=BLUE, mec=BLUE, zorder=4)
        a1.plot(100 * m, y, "o", ms=4.8, mfc="white", mec=BLUE, mew=1.1, zorder=5)
        if rt is not None:
            a1.plot(100 * rt, y - 0.3, "x", ms=3.8, mew=1.1, color=ORANGE, zorder=6)
        a1.text(100 * nm + 3.5, y, f"{100 * nm:.0f}%", fontsize=7.0, color=MUTED, va="center")
        ticks.append((y, lab, False))
    a1.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=7.6)
    for tl, tk, t in zip(a1.get_yticklabels(), a1.yaxis.get_major_ticks(), ticks):
        if t[2]:
            tl.set_fontweight("bold"); tk.tick1line.set_visible(False)
    a1.set_ylim(-0.6, n - 0.4)
    a1.set_xlim(-2, 97)
    a1.set_xticks([0, 20, 40, 60, 80])
    a1.tick_params(axis="x", labelsize=7.4)
    a1.set_xlabel("correct answers accepted blind\nthat score 3 or below (%)", fontsize=7.6, labelpad=1.5)
    a1.set_title("a   Accepted without a reference", loc="left", fontsize=8.6, fontweight="bold", x=-0.62)
    style(a1, "x")

    def barpair(ax, groups, xlim, xticks, xlabel, title, fmt):
        h = 0.36
        for i, (lab, off, on) in enumerate(groups):
            y = len(groups) - 1 - i
            for dy, v, col in ((0.21, off, BLUE), (-0.21, on, LIGHT)):
                ax.barh(y + dy, v[0], height=h - 0.05, color=col, zorder=3)
                ax.errorbar(v[0], y + dy, xerr=[[max(v[0] - v[1][0], 0)], [max(v[1][1] - v[0], 0)]], fmt="none", ecolor=MUTED,
                            elinewidth=0.8, capsize=1.3, zorder=4)
                ax.text(max(v[1][1], v[0], 0) + 0.05 * xlim[1], y + dy, fmt(v[0]), fontsize=7.0, color=INK, va="center")
        ax.axvline(0, color=MUTED, lw=0.8, zorder=2)
        ax.set_yticks(range(len(groups)), [g[0] for g in groups][::-1], fontsize=7.4)
        ax.set_ylim(-0.6, len(groups) - 0.4)
        ax.set_xlim(*xlim)
        ax.set_xticks(xticks)
        ax.tick_params(axis="x", labelsize=7.2, pad=1.5)
        ax.set_xlabel(xlabel, fontsize=7.4, labelpad=1.0)
        ax.set_title(title, loc="left", fontsize=8.6, fontweight="bold", x=-0.52)
        style(ax, "x")

    neg = lambda v: (-v[0], [-v[1][1], -v[1][0]])
    frp = lambda v: (100 * v[0], [100 * v[1][0], 100 * v[1][1]])
    barpair(a3, [("Sonnet 5 (API)", frp(S8f["pools"]["mace"]["oracle"]["FR"]), frp(S19f["pools"]["mace"]["oracle"]["FR"])),
                 ("Qwen3-8B", frp(tog["off"]["macesub"]["false_reject_diff"]), frp(tog["on"]["macesub"]["false_reject_diff"])),
                 ("Qwen3-14B", frp(t14["off"]["macesub"]["false_reject_diff"]), frp(t14["on"]["macesub"]["false_reject_diff"]))],
            (-1.5, 68), [0, 20, 40, 60], "rise in false rejections (pp)", "b   Thinking: factual questions", lambda x: f"+{x:.0f}")
    fig.legend(handles=[Line2D([], [], marker="o", ls="", mfc=BLUE, mec=BLUE, ms=4.8, label="differs from the reference, reference shown"),
                        Line2D([], [], marker="o", ls="", mfc="white", mec=BLUE, mew=1.1, ms=4.8, label="matches the reference, reference shown"),
                        Line2D([], [], marker="x", ls="", color=ORANGE, mew=1.2, ms=4.4, label="differs, second blind call"),
                        Patch(color=BLUE, label="thinking off (Sonnet 5: score only; Qwen3: explains first)"),
                        Patch(color=LIGHT, label="thinking on")],
               loc="lower center", bbox_to_anchor=(0.5, -0.01), ncol=2, frameon=False, fontsize=7.0, handlelength=1.0,
               columnspacing=1.4, handletextpad=0.4, labelspacing=0.3)
    save(fig, "fig3_acceptance")

# ============================================================== Figure 3 (mechanism, single panel)
mi = load("maskident_results.json")
sc = load("sep_continuum_results.json")
forms = [("31", lambda j: (mi[f"{j}|a|ref (baseline)"]["margin"], mi[f"{j}|a|ref (baseline)"]["ci"])),
         ("thirty-one", lambda j: (mi[f"{j}|a|refword"]["margin"], mi[f"{j}|a|refword"]["ci"])),
         ("30+1", lambda j: (mi[f"{j}|a|refexpr"]["margin"], mi[f"{j}|a|refexpr"]["ci"])),
         ("visible", lambda j: (mi[f"{j}|a|refsolmask"]["refsol"]["mean"], mi[f"{j}|a|refsolmask"]["refsol"]["ci"])),
         ("masked", lambda j: (mi[f"{j}|a|refsolmask"]["masked"]["mean"], mi[f"{j}|a|refsolmask"]["masked"]["ci"]))]
xpos = [0, 1, 2, 3.5, 4.5]
fig, a1 = plt.subplots(figsize=(3.5, 2.2))
for (lab, fn), x in zip(forms, xpos):
    for dx, j, name in ((-0.13, Q, "Qwen2.5-7B"), (0.13, P, "phi-4")):
        m, ci = fn(j)
        a1.errorbar(x + dx, m, yerr=yerr(m, ci), fmt=MARK[name], color=INK, ms=4.8, elinewidth=0.9, capsize=1.8, zorder=4)
a1.axvline(2.75, color=GRID, lw=1.0, zorder=1)
a1.text(1.0, 6.0, "bare reference", ha="center", fontsize=7.2, color=INK)
a1.text(4.0, 6.0, "worked solution,\nfinal answer", ha="center", va="bottom", fontsize=7.2, color=INK)
a1.axhline(0, color=MUTED, lw=0.8, zorder=2)
a1.set_xticks(xpos, ["31", "thirty-\none", "30+1", "visible", "masked"], fontsize=7)
a1.set_xlim(-0.5, 5.0)
a1.set_ylim(-1.6, 7.6)
a1.set_ylabel("anchoring margin\n(points, 0\u201310 scale)")
fig.legend(handles=[Line2D([], [], marker="o", ls="", color=INK, label="Qwen2.5-7B"),
                    Line2D([], [], marker="s", ls="", color=INK, label="phi-4")],
           loc="upper center", bbox_to_anchor=(0.55, 0.02), ncol=2, frameon=False, handlelength=1.0, fontsize=7)
style(a1)
fig.tight_layout()
save(fig, "fig3_mechanism")

# ---- appendix figure: answer-format continuum (moved out of the main text)
strata = [("scalar", "integer"), ("pair", "pair"), ("json", "JSON"), ("program", "program")]
fig, a2 = plt.subplots(figsize=(3.4, 2.1))
for j, name, off in ((Q, "Qwen2.5-7B", -0.08), (P, "phi-4", 0.08)):
    for i, (st_, _) in enumerate(strata):
        m, ci = sc[j][st_]["infl"], sc[j][st_]["infl_ci"]
        a2.errorbar(i + off, m, yerr=yerr(m, ci), fmt=MARK[name], color=INK, ms=4.5, elinewidth=0.9, capsize=1.8, zorder=4)
a2.axhline(0, color=MUTED, lw=0.8, zorder=2)
a2.set_xticks(range(4), [l for _, l in strata])
a2.set_xlim(-0.5, 3.5)
a2.set_xlabel("requested answer format")
a2.set_ylabel("added inflation (pool SDs)")
a2.legend(handles=[Line2D([], [], marker="o", ls="", color=INK, label="Qwen2.5-7B"),
                   Line2D([], [], marker="s", ls="", color=INK, label="phi-4")], loc="upper right", frameon=False, handlelength=1.0, fontsize=7)
style(a2)
fig.tight_layout()
save(fig, "figA_continuum")

# ============================================================== Figure 4
m1r = load("r2_math_m1_results.json")
have_math = isinstance(m1r, dict) and any(isinstance(v, dict) for v in m1r.values())
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.5, 2.25), gridspec_kw={"width_ratios": [1.0, 1.0]})
for y, (name, key) in enumerate(KJ[::-1]):
    d = acc["kpool"][key]["kgt1"]
    (mr, cr, _), (mm, cm, _) = d["ref_minus_blind"], d["m1_minus_blind"]
    a1.annotate("", xy=(100 * mm, y), xytext=(100 * mr, y),
                arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.1, shrinkA=4, shrinkB=4, mutation_scale=8), zorder=2)
    for m, ci, col, off in ((mr, cr, BLUE, 0.13), (mm, cm, TEAL, -0.13)):
        a1.plot([100 * ci[0], 100 * ci[1]], [y + off] * 2, color=col, lw=1.0, zorder=3)
        a1.plot(100 * m, y + off, marker=MARK[name], ms=5, color=col, ls="", zorder=4)
a1.axvline(0, color=ORANGE, lw=0.9, zorder=2)
a1.text(1.5, len(KJ) - 0.45, "blind", fontsize=7, color=ORANGE, va="center")
a1.set_ylim(-0.5, len(KJ) - 0.2)
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

# ============================================================== Figure 3: grading vs. selection under three labelings
# a: change in per-task AUROC, non-matching correct vs. wrong; b: change in best-of-64 accuracy (points).
# Constructed pools: r8_lenient_results.json (registered, format-lenient, model-extracted labels);
# MACE: r4_results.json (Qwen2.5-7B, exact) and r4_posthoc_results.json / r3_mace_accuracy_results.json (phi-4);
# MATH-500: r4_results.json; Sonnet 5 (command line, 16-candidate subsamples): r8_sonnet_results.json if present.
ph4 = load("r4_posthoc_results.json") or {}
mace3 = load("r3_mace_accuracy_results.json")
L8 = load("r8_lenient_results.json")
S8 = load("r8_sonnet_results.json") or {}
if L8 and r4res.get("grading"):
    def lv(pool, j, how, key):
        return L8["pools"].get(pool, {}).get(j, {}).get(how, {}).get(key)

    def s8(pool, how, key):
        d = S8.get("pools", {}).get(pool)
        if not isinstance(d, dict) or how not in d or d[how].get("status"):
            return None
        return d[how][key]

    rows = []  # (group, judge label, marker, {how: (G_nm, acc)})
    for pool, grp_, js in (("repl|all", "Replication", ["Qwen2.5-7B", "phi-4", "GPT-4.1"]),
                           ("kpool|kgt1", "k-pool, k > 1", ["Qwen2.5-7B", "Qwen2.5-14B", "gemma-2-9b", "phi-4", "GPT-4.1"])):
        for j in js:
            rows.append((grp_, j, {h: (lv(pool, j, h, "G_nm"), lv(pool, j, h, "acc")) for h in ("strict", "boxed_only", "lenient", "model")}))
        sp = "repl" if pool.startswith("repl") else "kpool"
        if s8(sp, "lenient", "G_nm"):
            rows.append((grp_, "Sonnet 5 (API)", {"strict": (s8(sp, "strict", "G_nm"), s8(sp, "strict", "acc")),
                                             "lenient": (s8(sp, "lenient", "G_nm"), s8(sp, "lenient", "acc"))}))
    mq = ph4.get("mace_exact_q7", {})
    p4g = ph4.get("grading_other_judges", {}).get(P, {}).get("grading_mace", {}).get("G_nm", {})
    rows.append(("MACE, k > 1", "Qwen2.5-7B", {"oracle": (r4res["grading"]["mace"]["G_nm"]["ref_minus_blind"], mq["kgt1"]["ref_minus_blind"])}))
    rows.append(("MACE, k > 1", "phi-4", {"oracle": (p4g.get("ref_minus_blind"), mace3[P]["kgt1"]["ref_minus_blind"])}))
    if s8("mace", "oracle", "G_nm"):
        rows.append(("MACE, k > 1", "Sonnet 5 (API)", {"oracle": (s8("mace", "oracle", "G_nm"), s8("mace", "oracle", "acc"))}))
    for j, key in (("Qwen2.5-7B", Q), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct")):
        rows.append(("MATH-500 (one answer)", j, {"oracle": (None, r4res["math"][key]["ref_minus_noref"])}))

    n = len(rows)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.2, 0.215 * n + 1.0), sharey=True, gridspec_kw={"width_ratios": [1.0, 1.0], "wspace": 0.08})
    ys, labels_, prev = [], [], None
    y = 0.0
    heads = []
    for grp_, j, d in rows:
        if grp_ != prev:
            y -= 0.8 if prev is not None else 0.0
            heads.append((y + 0.78, grp_))
            prev = grp_
        ys.append(y)
        labels_.append(j)
        y -= 1.0
    STY = {"strict": dict(marker="d", mfc="white", mec=MUTED, ms=4.0, mew=0.9, zorder=4),
           "boxed_only": dict(marker="|", color=MUTED, ms=7, mew=1.3, zorder=4),
           "lenient": dict(marker="o", mfc=BLUE, mec=BLUE, ms=4.4, zorder=5),
           "model": dict(marker="x", color=MUTED, ms=4.2, mew=0.9, zorder=4),
           "oracle": dict(marker="D", mfc=BLUE, mec=BLUE, ms=3.9, zorder=5)}
    OFF = {"strict": 0.26, "boxed_only": 0.13, "lenient": 0.0, "model": -0.24, "oracle": 0.0}
    for yy, (grp_, j, d) in zip(ys, rows):
        for how, (g, a) in d.items():
            for ax, v, scale in ((a1, g, 1.0), (a2, a, 100.0)):
                if v is None or (ax is a2 and j.startswith(("Sonnet", "GPT"))):
                    continue
                yo = yy + OFF[how]
                if how in ("lenient", "oracle"):
                    ax.plot([scale * v[1][0], scale * v[1][1]], [yo, yo], color=BLUE, lw=1.0, zorder=3)
                st = dict(STY[how])
                if j.startswith("Sonnet") and how in ("lenient", "oracle"):
                    st.update(marker="s", ms=4.6)
                ax.plot(scale * v[0], yo, ls="", **st)
        if all(g is None for g, _ in d.values()):
            a1.text(-0.41, yy, "one correct answer: see Table 2", fontsize=7.5, color=MUTED, va="center", ha="left")
    for ax in (a1, a2):
        ax.axvline(0, color=MUTED, lw=0.8, zorder=2)
        for hy, _ in heads[1:]:
            ax.axhline(hy + 0.45, color=GRID, lw=0.9, zorder=1)
        style(ax, "x")
    for hy, txt in heads:
        a1.text(-0.02, hy, txt, transform=a1.get_yaxis_transform(), ha="right", va="center", fontsize=7.8, fontweight="bold")
    a1.set_yticks(ys, labels_, fontsize=7.8)
    a1.set_ylim(min(ys) - 0.7, heads[0][0] + 0.6)
    a1.set_xlim(-0.42, 0.12)
    a1.set_xticks([-0.4, -0.3, -0.2, -0.1, 0.0, 0.1])
    a1.set_xlabel("change in AUROC, non-matching\ncorrect vs. wrong answers", fontsize=8)
    a1.set_title("a   Grading", loc="left", fontsize=9, fontweight="bold")
    a2.set_xlim(-55, 45)
    a2.set_xlabel("change in best-of-64 accuracy\n(points)", fontsize=8)
    a2.set_title("b   Selection", loc="left", fontsize=9, fontweight="bold")
    a2.tick_params(axis="y", length=0)
    fig.legend(handles=[Line2D([], [], ls="", **STY["lenient"], label="answers read in any format (95% CI)"),
                        Line2D([], [], ls="", **STY["strict"], label="registered labels"),
                        Line2D([], [], ls="", **STY["boxed_only"], label="boxed replies only"),
                        Line2D([], [], ls="", **STY["model"], label="answers read by a model"),
                        Line2D([], [], ls="", **STY["oracle"], label="answer list or unique answer (95% CI)"),
                        Line2D([], [], ls="", marker="s", mfc=BLUE, mec=BLUE, ms=4.6, label="Sonnet 5: 16-candidate subsamples")],
               loc="upper center", bbox_to_anchor=(0.5, -0.025), ncol=2, frameon=False, fontsize=7.6,
               handlelength=1.0, columnspacing=1.0)
    save(fig, "fig3_cost")

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


# ============================================================== Figure 2: the reference helps at k = 1 and hurts at k > 1
# synthk_paired.json (synthetic grid, six judges), mitigation_results.json E2_gap_deltas (OSF k-pool), mace_results.json
sg = load("synthk_paired.json")
e2 = (load("mitigation_results.json") or {}).get("E2_gap_deltas", {})
mr = (load("mace_results.json") or {}).get("predictions", {})
if sg and e2 and mr:
    rows = []
    rows.append(("hdr", "k-pool (preregistered)"))
    for key, name in ((Q, "Qwen2.5-7B"), (P, "phi-4")):
        a, b = e2[f"{key}|ref|k1"], e2[f"{key}|ref|kgt1"]
        rows.append((name, (a["delta"], a["ci"]), (b["delta"], b["ci"])))
    cov = load("p17_coverage_results.json") or {}
    for key, name in (("Qwen__Qwen2.5-14B-Instruct", "Qwen2.5-14B"), ("google__gemma-2-9b-it", "gemma-2-9b")):
        if key in cov:
            r = cov[key]
            rows.append((name, (r["ref_k1"]["delta"], r["ref_k1"]["ci"]), (r["ref_kgt1"]["delta"], r["ref_kgt1"]["ci"])))
    rows.append(("hdr", "MACE factual questions"))
    for key, name in ((Q, "Qwen2.5-7B"), (P, "phi-4")):
        r = mr[key]["nonmath"]
        rows.append((name, (r["k1"][0], r["k1"][1]), (r["kgt1"][0], r["kgt1"][1])))
    rows.append(("hdr", "Synthetic grid"))
    for key, name in (("Qwen__Qwen2.5-1.5B-Instruct", "Qwen2.5-1.5B"), ("Qwen__Qwen2.5-3B-Instruct", "Qwen2.5-3B"),
                      ("Qwen__Qwen2.5-7B-Instruct", "Qwen2.5-7B"), ("Qwen__Qwen2.5-14B-Instruct", "Qwen2.5-14B"),
                      ("meta-llama__Llama-3.1-8B-Instruct", "Llama-3.1-8B"), ("microsoft__phi-4", "phi-4")):
        pp = sg["paired_pooled"][key]
        rows.append((name, (pp["delta_k1"], pp["ci_k1"]), (pp["delta_kgt1"], pp["ci_kgt1"])))
    fig, ax = plt.subplots(figsize=(2.05, 3.45))
    y, ticks = 0.0, []
    for r in rows:
        if r[0] == "hdr":
            y -= 0.35 if ticks else 0.0
            ticks.append((y, r[1], True))
            y -= 0.8
            continue
        name, (m1, c1), (m2, c2) = r
        for (m, ci, face, off) in ((m1, c1, "white", 0.14), (m2, c2, BLUE, -0.14)):
            ax.plot([ci[0], ci[1]], [y + off] * 2, color=BLUE, lw=0.9, zorder=3)
            ax.plot(m, y + off, "o", ms=5.0, mfc=face, mec=BLUE, mew=1.1, zorder=4)
        ticks.append((y, name, False))
        y -= 0.8
    ax.axvline(0, color=ORANGE, lw=0.9, zorder=2)
    ax.text(0.06, 0.35, "blind", color=ORANGE, fontsize=8, va="bottom")
    ax.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=8)
    for tl, tk, t in zip(ax.get_yticklabels(), ax.yaxis.get_major_ticks(), ticks):
        if t[2]:
            tl.set_fontweight("bold"); tk.tick1line.set_visible(False)
    ax.set_ylim(y + 0.3, 0.7)
    ax.set_xlim(-1.4, 3.8)
    ax.set_xlabel("inflation added by the\nreference (SD)", fontsize=8)
    ax.tick_params(axis="x", labelsize=8)
    style(ax, "x")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", mfc="white", mec=BLUE, label="one correct answer (k = 1)"),
                       Line2D([], [], marker="o", ls="", mfc=BLUE, mec=BLUE, label="several (k > 1)")],
              loc="upper center", bbox_to_anchor=(0.2, -0.17), ncol=1, frameon=False, fontsize=8, handlelength=0.8)
    save(fig, "fig2_boundary")


# ============================================================== Figure 2 (main): one correct answer vs. several
# Change from showing the reference (referenced minus blind, per task, 95% CI), with one shared row list for both panels.
# a: best-of-64 accuracy. MATH-500 with the bare final answer (r4_results.json, exact scorer); MACE k = 1 and k > 1
#    (Qwen2.5-7B exact scorer: r4_posthoc_results.json mace_exact_q7; phi-4: r3_mace_accuracy_results.json);
#    constructed pools with any-format labels (r8_lenient_results.json).
# b: grading AUROC. One correct answer: all correct vs. wrong (r16c_protocols_exact.json: MATH-500 bare answer, MACE k = 1).
#    Several: correct answers that differ from the reference vs. wrong; constructed pools with any-format labels and boxed-only
#    ticks (r8_lenient_results.json; Sonnet 5: r8_sonnet_results.json); MACE with its answer lists (r4_results.json,
#    r4_posthoc_results.json, r8_sonnet_results.json). Blank cells are undefined or not run.
L8b = load("r8_lenient_results.json")
S8b = load("r8_sonnet_results.json") or {}
m3 = load("r3_mace_accuracy_results.json") or {}
ph4b = load("r4_posthoc_results.json") or {}
exb = load("r16c_protocols_exact.json") or {}
if L8b and r4res.get("math") and m3 and ph4b.get("mace_exact_q7") and exb:
    K14 = "Qwen__Qwen2.5-14B-Instruct"

    def pct(v):
        return None if v is None else [100 * v[0], [100 * v[1][0], 100 * v[1][1]]]

    def lv(pool, j, how, key):
        return L8b["pools"][pool][j].get(how, {}).get(key)

    def s8g(pool, how):
        d = S8b.get("pools", {}).get(pool, {}).get(how, {})
        return d.get("G_nm") if isinstance(d, dict) else None

    mq7 = ph4b["mace_exact_q7"]
    p4m = ph4b.get("grading_other_judges", {}).get(P, {}).get("grading_mace", {}).get("G_nm", {}).get("ref_minus_blind")
    ex_math = exb["math500"]
    ex_mace = exb["mace"]
    # (label, accuracy change, AUROC change, marker kind, boxed-only AUROC tick)
    rows = [("hdr", "One correct answer"),
            ("MATH-500, Qwen2.5-7B", pct(r4res["math"][Q]["refans_minus_noref"]), ex_math["Qwen2.5-7B"]["refans"]["grading_all_correct"]["reference_minus_blind"], "open", None),
            ("MATH-500, Qwen2.5-14B", pct(r4res["math"][K14]["refans_minus_noref"]), ex_math["Qwen2.5-14B"]["refans"]["grading_all_correct"]["reference_minus_blind"], "open", None),
            ("MACE, Qwen2.5-7B", pct(mq7["k1"]["ref_minus_blind"]), ex_mace["Qwen2.5-7B"]["grading_k1_all_correct"]["reference_minus_blind"], "open", None),
            ("MACE, phi-4", pct(m3[P]["k1"]["ref_minus_blind"]), ex_mace["phi-4"]["grading_k1_all_correct"]["reference_minus_blind"], "open", None),
            ("hdr", "Several correct answers")]
    for pool, plab in (("repl|all", "replication"), ("kpool|kgt1", "k-pool")):
        judges = ["Qwen2.5-7B", "phi-4"] if pool.startswith("repl") else ["Qwen2.5-7B", "Qwen2.5-14B", "gemma-2-9b", "phi-4"]
        for j in judges:
            rows.append((f"{plab}, {j}", pct(lv(pool, j, "lenient", "acc")), lv(pool, j, "lenient", "G_nm"), "open", lv(pool, j, "boxed_only", "G_nm")))
        rows.append((f"{plab}, GPT-4.1", None, lv(pool, "GPT-4.1", "lenient", "G_nm"), "gpt", lv(pool, "GPT-4.1", "boxed_only", "G_nm")))
        sp = "repl" if pool.startswith("repl") else "kpool"
        if s8g(sp, "lenient"):
            rows.append((f"{plab}, Sonnet 5", None, s8g(sp, "lenient"), "sonnet", None))
        o19c = ((((load("r19a_opus_results.json") or {}).get("pools", {}).get(sp) or {}).get("lenient")) or {}).get("G_nm")
        if o19c:
            rows.append((f"{plab}, Opus 5", None, o19c, "opus", None))
    rows.append(("MACE, Qwen2.5-7B", pct(mq7["kgt1"]["ref_minus_blind"]), r4res["grading"]["mace"]["G_nm"]["ref_minus_blind"], "open", None))
    rows.append(("MACE, phi-4", pct(m3[P]["kgt1"]["ref_minus_blind"]), p4m, "open", None))
    if s8g("mace", "oracle"):
        rows.append(("MACE, Sonnet 5", None, s8g("mace", "oracle"), "sonnet", None))
    o19 = (((load("r19a_opus_results.json") or {}).get("pools", {}).get("mace") or {}).get("oracle") or {}).get("G_nm")
    if o19:
        rows.append(("MACE, Opus 5", None, o19, "opus", None))

    KIND = {"open": dict(marker="o", mfc=BLUE, mec=BLUE, ms=4.6),
            "sonnet": dict(marker="s", mfc="white", mec=BLUE, mew=1.1, ms=4.4),
            "opus": dict(marker="D", mfc="white", mec=BLUE, mew=1.1, ms=4.0),
            "gpt": dict(marker="^", mfc="white", mec=BLUE, mew=1.1, ms=5.0)}
    NOACC = {"sonnet": "n/a (subsamples)", "opus": "n/a (subsamples)", "gpt": "n/a (ties)"}
    TICK = dict(marker="|", color="#b5b5b5", ms=3.5, mew=1.1)
    nrow = len(rows)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.2, 0.118 * nrow + 0.98), sharey=True, gridspec_kw={"width_ratios": [1.0, 1.0], "wspace": 0.12})
    fig.subplots_adjust(left=0.27, right=0.985, top=0.87, bottom=0.12)
    ticks, seps = [], []
    for pos, r in enumerate(rows):
        yv = nrow - 1 - pos
        if r[0] == "hdr":
            ticks.append((yv, r[1], True))
            if pos:
                seps.append(yv + 0.5)
            continue
        lab, acc_v, au_v, kind, boxed = r
        if acc_v is None and kind in NOACC:
            a1.text(-59, yv, NOACC[kind], fontsize=7.0, color=MUTED, style="italic", ha="left", va="center", zorder=6,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.3))
        for ax, v in ((a1, acc_v), (a2, au_v)):
            if v is None:
                continue
            ax.plot([v[1][0], v[1][1]], [yv, yv], color=BLUE, lw=1.0, zorder=3)
            ax.plot(v[0], yv, ls="", zorder=4, **KIND[kind])
        if boxed:
            a2.plot(boxed[0], yv - 0.34, ls="", zorder=5, **TICK)
        ticks.append((yv, lab, False))
    for ax, xlim, xticks, xlabel, title in ((a1, (-62, 52), [-40, -20, 0, 20, 40], "change in best-of-64 accuracy (pp)", "a   Selection"),
                                           (a2, (-0.37, 0.46), [-0.2, 0.0, 0.2, 0.4], "change in grading AUROC", "b   Grading")):
        for yy in seps:
            ax.axhline(yy, color="#d9d9d9", lw=0.6, zorder=1)
        ax.axvline(0, color=MUTED, lw=0.8, zorder=2)
        ax.set_xlim(*xlim)
        ax.set_xticks(xticks)
        ax.tick_params(axis="x", labelsize=7.8)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_title(title, loc="left", fontsize=9, fontweight="bold")
        style(ax, "x")
    a1.set_yticks([t_[0] for t_ in ticks], [t_[1] for t_ in ticks], fontsize=7.8)
    for tl, tk, t_ in zip(a1.get_yticklabels(), a1.yaxis.get_major_ticks(), ticks):
        if t_[2]:
            tl.set_fontweight("bold"); tk.tick1line.set_visible(False)
    a2.tick_params(axis="y", length=0)
    a1.set_ylim(-0.6, nrow - 0.4)
    fig.legend(handles=[Line2D([], [], ls="", label="open judges, 64 candidates", **KIND["open"]),
                        Line2D([], [], ls="", label="Sonnet 5, 16 candidates", **KIND["sonnet"]),
                        Line2D([], [], ls="", label="Opus 5, 16 candidates", **KIND["opus"]),
                        Line2D([], [], ls="", label="GPT-4.1", **KIND["gpt"]),
                        Line2D([], [], ls="", label="boxed replies only", **TICK)],
               loc="lower center", bbox_to_anchor=(0.6, 0.905), ncol=3, frameon=False, fontsize=7.3, handlelength=0.9,
               columnspacing=0.9, handletextpad=0.3)
    save(fig, "fig2_onevsseveral")


# ============================================================== Figure 4 (main): benchmark accuracy under each grader
# r20c_leaderboard.json with r20g_frontier_safeguards.json leaderboard_max_rule (Sonnet 5 grader; max rule post hoc) and
# r21a_leaderboard_{opus,haiku}.json with r21a_maxrule_{opus,haiku}.json (R21-A). One line per answering model across the answer
# list, the blind judge, the judge shown the reference, and the max rule; a score of 7 or above counts as correct.
GRADERS = [("Sonnet 5", load("r20c_leaderboard.json"), (load("r20g_frontier_safeguards.json") or {}).get("leaderboard_max_rule")),
           ("Opus 5", load("r21a_leaderboard_opus.json"), load("r21a_maxrule_opus.json")),
           ("Haiku 4.5", load("r21a_leaderboard_haiku.json"), load("r21a_maxrule_haiku.json"))]
GRADERS = [g for g in GRADERS if g[1] and g[2]]
if GRADERS:
    MODELS = [("claude-opus-5", "Opus 5", "D", "#b8b8b8", "-"), ("claude-sonnet-5", "Sonnet 5", "^", "#5c5c5c", "-"),
              ("claude-haiku-4-5-20251001", "Haiku 4.5", "s", INK, "-"), ("meta-llama__Llama-3.1-8B-Instruct", "Llama-3.1-8B", "o", "#4d4d4d", (0, (3, 1.5)))]
    XS = [0, 1, 2, 3.35]
    R22 = {"Sonnet 5": load("r22b_redraw_sonnet.json"), "Opus 5": load("r22b_redraw_opus.json"), "Haiku 4.5": load("r22b_redraw_haiku.json")}
    fig, axes = plt.subplots(1, len(GRADERS), figsize=(5.5, 1.9), sharey=True, gridspec_kw={"wspace": 0.1})
    axes = list(axes) if len(GRADERS) > 1 else [axes]
    lo = 100
    for ax, (gname, lb, mr) in zip(axes, GRADERS):
        mrg = mr.get("generators", mr)
        ax.axvspan(1.62, 2.38, color="#e9eefa", zorder=0, lw=0)
        for key, lab, mk, col, ls in MODELS:
            g = lb["generators"][key]
            ys = [100 * g["accuracy_answer_list"][0], 100 * g["accuracy_blind"][0], 100 * g["accuracy_referenced"][0], 100 * mrg[key]["accuracy_max_rule"][0]]
            lo = min(lo, min(ys))
            heavy = key.startswith("claude-haiku")
            ax.plot(XS[:3], ys[:3], marker=mk, ms=4.3 if heavy else 3.8, lw=1.7 if heavy else 1.0, color=col, ls=ls, mfc=col, mec=col,
                    zorder=4 if heavy else 3, label=lab)
            ax.plot(XS[2:], ys[2:], ls=":", lw=0.9, color=col, zorder=2)
            ax.plot(XS[3], ys[3], marker=mk, ms=4.3 if heavy else 3.8, ls="", mfc=col, mec=col, zorder=4 if heavy else 3)
            lo_ci, hi_ci = g["accuracy_referenced"][1]
            ax.plot([XS[2], XS[2]], [100 * lo_ci, 100 * hi_ci], color=col, lw=0.8, alpha=0.8, zorder=2)
            lo = min(lo, 100 * lo_ci)
            if R22.get(gname):
                v2 = 100 * R22[gname]["generators"][key]["accuracy_ref_draw2"][0]
                ax.plot(XS[2] + 0.2 + 0.09 * [m[0] for m in MODELS].index(key), v2, marker=mk, ms=3.8, ls="", mfc="white", mec=col, mew=1.0, zorder=5)
                lo = min(lo, v2)
        ax.set_xticks(XS, ["answer\nlist", "judge,\nblind", "judge,\nreference", "max\nrule"], fontsize=7.2)
        ax.set_xlim(-0.3, 3.65)
        ax.set_title(f"Graded by {gname}", loc="left", fontsize=8.6, fontweight="bold")
        style(ax, "y")
    axes[0].set_ylabel("accuracy (%)", fontsize=8)
    axes[0].set_ylim(max(0, 10 * int(lo // 10) - 5), 103)
    axes[0].tick_params(axis="y", labelsize=7.4)
    handles = [Line2D([], [], marker=mk, ms=4.3 if key.startswith("claude-haiku") else 3.8, lw=1.7 if key.startswith("claude-haiku") else 1.0, color=col, ls=ls,
                      mfc=col, mec=col, label=lab) for key, lab, mk, col, ls in MODELS]
    handles.append(Line2D([], [], marker="o", ls="", ms=3.8, mfc="white", mec="#5c5c5c", mew=1.0, label="second reference draw"))
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=5, frameon=False, fontsize=7.4,
               handlelength=2.2, columnspacing=1.4)
    save(fig, "fig4_benchmark")


# ============================================================== Appendix figure: rejection by blind score (post hoc; round-23 review M4)
# r22c_acceptance_bins.json. On MACE, the share of correct answers scored 3 or below with the reference, by blind-score bin, for answers
# that differ from the reference (solid) and answers that match it (dashed grey); open judges binned on expected score, API judges on
# integer score; bins with at least 10 differing answers.
BINS = load("r22c_acceptance_bins.json")
if BINS:
    fig, (b1, b2) = plt.subplots(1, 2, figsize=(5.5, 2.5), sharey=True, gridspec_kw={"width_ratios": [1.45, 1.0], "wspace": 0.08})
    for ax, series, edges, title in ((b1, (("mace|Qwen2.5-7B", "Qwen2.5-7B", "o"), ("mace|phi-4", "phi-4", "s")),
                                     ["<5", "5-7", "7-9", "9-9.6", "9.6-9.8", "\u22659.8"], "a   Open judges (expected blind score)"),
                                    (b2, (("mace|Sonnet 5", "Sonnet 5", "^"), ("mace|Opus 5", "Opus 5", "D")),
                                     ["\u22646", "7-8", "9", "10"], "b   API judges (integer blind score)")):
        for key, lab, mk in series:
            xs, dif, mat = [], [], []
            for k_, bb in enumerate(BINS[key]):
                if bb["nonmatch"]["n"] < 10:
                    continue
                xs.append(k_)
                dif.append(100 * bb["nonmatch"]["share_le3_with_reference"])
                mat.append(100 * bb["match"]["share_le3_with_reference"] if bb["match"]["share_le3_with_reference"] is not None else float("nan"))
            ax.plot(xs, dif, marker=mk, ms=4.6, lw=1.3, color=BLUE, mfc=BLUE, mec=BLUE, label=f"{lab}: differs")
            ax.plot(xs, mat, marker=mk, ms=4.0, lw=0.9, ls=(0, (3, 2)), color="#8c8c8c", mfc="white", mec="#8c8c8c", label=f"{lab}: matches")
        ax.set_xticks(range(len(edges)), edges, fontsize=7.6)
        ax.set_xlim(-0.4, len(edges) - 0.6)
        ax.set_xlabel("blind-score bin", fontsize=8)
        ax.set_title(title, loc="left", fontsize=9, fontweight="bold")
        style(ax, "y")
    hs = b1.get_legend_handles_labels()[0] + b2.get_legend_handles_labels()[0]
    fig.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=4, frameon=False, fontsize=7.2, handlelength=2.0,
               columnspacing=1.0, labelspacing=0.25)
    b1.set_ylabel("scored 3 or below with the reference (%)", fontsize=8)
    b1.set_ylim(-3, 105)
    b1.tick_params(axis="y", labelsize=7.6)
    save(fig, "figA_bins")
