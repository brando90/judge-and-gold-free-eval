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
s5 = acc["repl_sonnet5_scores"]
rows = [("valid, matches\nthe reference", s5["noref"]["match"][0], s5["ref"]["match"][0]),
        ("valid, differs\nfrom the reference", s5["noref"]["nonmatch"][0], s5["ref"]["nonmatch"][0])]
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
    for dx, k, kw in ((-w, "gainers", dict(color=BLUE)), (0, "placebo", dict(color=GREY)),
                      (w, "losers", dict(facecolor="white", edgecolor=BLUE, hatch="/////", lw=0.8))):
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
fig.legend(handles=[Patch(color=BLUE, label="reference moved onto the answer"), Patch(color=GREY, label="matches neither"),
                    Patch(facecolor="white", edgecolor=BLUE, hatch="/////", label="reference moved off the answer")],
           loc="upper center", ncol=3, frameon=False, handlelength=1.1, fontsize=6.8, bbox_to_anchor=(0.62, 0.02),
           columnspacing=0.8)
save(fig, "fig1_teaser")

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
a1.text(1.05, 4, "blind", fontsize=7, color=ORANGE, va="bottom")
a1.set_xscale("log", base=2)
a1.set_xticks(xs, [str(x) for x in xs])
a1.minorticks_off()
a1.set_ylim(-100, 45)
a1.set_xlabel("valid answers per question, $k$")
a1.set_ylabel("change in accuracy of\nthe pick (points)")
a1.set_title("Showing the reference, by $k$", loc="left")
a1.legend(loc="lower left", frameon=False, fontsize=6.5, handlelength=1.6, ncol=2, columnspacing=0.8, labelspacing=0.2)
style(a1)
label(a1, "a")

groups = [("Qwen-7B", acc["repl"][Q]["false_reject"]["blind_nonmatch"], acc["repl"][Q]["false_reject"]["ref_nonmatch"]),
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
tog = load("r3_toggle_results.json")
t14 = (load("r4_toggle14b_results.json") or {}).get("Qwen3-14B", {})
r2r = load("r2_realism_results.json")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.5, 2.75), gridspec_kw={"width_ratios": [1.3, 1.0]})
q7l = r4res["rotation"]["escore"]["loser"] if r4res.get("rotation") else [rot[f"{Q}__a"]["losers"]["mean"], rot[f"{Q}__a"]["losers"]["ci"]]
rows = [("hdr", "expected score"),
        ("Qwen2.5-7B", q7l[0], q7l[1], MARK["Qwen2.5-7B"], True),
        ("phi-4", rot[f"{P}__a"]["losers"]["mean"], rot[f"{P}__a"]["losers"]["ci"], MARK["phi-4"], True),
        ("hdr", "sampled integer"),
        ("Sonnet 5", fr["rotation__a"]["losers"]["mean"], fr["rotation__a"]["losers"]["ci"], MARK["Sonnet 5"], True),
        ("Qwen2.5-7B, MT-Bench", r2r["mtbench"]["rot"]["loser"][0], r2r["mtbench"]["rot"]["loser"][1], MARK["Qwen2.5-7B"], True),
        ("Qwen3-8B, thinking off", tog["off"]["rot"]["loser"][0], tog["off"]["rot"]["loser"][1], MARK["Qwen3-8B"], True),
        ("Qwen3-8B, thinking on", tog["on"]["rot"]["loser"][0], tog["on"]["rot"]["loser"][1], MARK["Qwen3-8B"], False)]
for arm, lab, filled in (("off", "Qwen3-14B, thinking off", True), ("on", "Qwen3-14B, thinking on", False)):
    v = (t14.get(arm) or {}).get("rot")
    if v:
        rows.append((lab, v["loser"][0], v["loser"][1], MARK["Qwen3-14B"], filled))
n = len(rows)
ticks = []
for pos, r in enumerate(rows):
    y = n - 1 - pos
    if r[0] == "hdr":
        ticks.append((y, r[1], True))
        continue
    lab, m, ci, mk, filled = r
    a1.plot([ci[0], ci[1]], [y, y], color=INK, lw=1.0, zorder=3)
    a1.plot(m, y, marker=mk, ms=5.2, color=INK, mfc=INK if filled else "white", mec=INK, ls="", zorder=4)
    a1.text(ci[0] - 0.2 if m < -0.5 else ci[1] + 0.25, y, sgn(m, 2), fontsize=6.4, color=MUTED,
            ha="right" if m < -0.5 else "left", va="center")
    ticks.append((y, lab, False))
a1.axvline(0, color=MUTED, lw=0.8, zorder=2)
a1.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=6.8)
for tl, t in zip(a1.get_yticklabels(), ticks):
    if t[2]:
        tl.set_fontstyle("italic"); tl.set_color(MUTED)
a1.set_xlim(-8.3, 1.4)
a1.set_xticks([-6, -4, -2, 0])
a1.set_ylim(-0.6, n - 0.4)
a1.set_xlabel("score change when the reference\nmoves off a correct answer (points)")
a1.set_title("Arithmetic tasks, same text", loc="left")
style(a1, "x")
label(a1, "a", x=-0.7)

groups = []
for mname, src in (("Qwen3-8B", tog), ("Qwen3-14B", t14)):
    for task, key, sub in (("arith.", "ksub", "margin_diff_kgt1"), ("factual", "macesub", "margin_diff")):
        groups.append((f"{mname[-3:].strip('-')}\n{task}", ((src.get("off") or {}).get(key) or {}).get(sub), ((src.get("on") or {}).get(key) or {}).get(sub)))
w = 0.34
for i, (lab, off, on) in enumerate(groups):
    for dx, v, kw in ((-w / 2, off, dict(color=INK)), (w / 2, on, dict(facecolor="white", edgecolor=INK, lw=1.0))):
        if v is None:
            continue
        a2.bar(i + dx, v[0], width=w - 0.04, zorder=3, **kw)
        a2.errorbar(i + dx, v[0], yerr=yerr(v[0], v[1]), fmt="none", ecolor=MUTED, elinewidth=0.8, capsize=1.6, zorder=4)
        a2.text(i + dx, max(v[1][1], 0) + 0.2, sgn(v[0]), ha="center", va="bottom", fontsize=6.0, color=MUTED)
a2.axhline(0, color=MUTED, lw=0.8, zorder=2)
a2.set_xticks(range(len(groups)), [g[0] for g in groups], fontsize=6.4)
a2.set_ylim(-0.6, 10.2)
a2.set_ylabel("margin increase from\nthe reference (points)")
a2.set_title("Qwen3, thinking off vs. on", loc="left")
a2.legend(handles=[Patch(color=INK, label="thinking off"), Patch(facecolor="white", edgecolor=INK, label="thinking on")],
          loc="upper left", frameon=False, handlelength=1.0, fontsize=6.6, borderaxespad=0.2)
style(a2)
label(a2, "b", x=-0.3)
fig.tight_layout(w_pad=1.2)
save(fig, "fig2_reasoning")

# ============================================================== Figure 3
mi = load("maskident_results.json")
sc = load("sep_continuum_results.json")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.5, 2.1), gridspec_kw={"width_ratios": [1.3, 1.0]})
forms = [("31", lambda j: (mi[f"{j}|a|ref (baseline)"]["margin"], mi[f"{j}|a|ref (baseline)"]["ci"])),
         ("thirty-\none", lambda j: (mi[f"{j}|a|refword"]["margin"], mi[f"{j}|a|refword"]["ci"])),
         ("30+1", lambda j: (mi[f"{j}|a|refexpr"]["margin"], mi[f"{j}|a|refexpr"]["ci"])),
         ("visible", lambda j: (mi[f"{j}|a|refsolmask"]["refsol"]["mean"], mi[f"{j}|a|refsolmask"]["refsol"]["ci"])),
         ("masked", lambda j: (mi[f"{j}|a|refsolmask"]["masked"]["mean"], mi[f"{j}|a|refsolmask"]["masked"]["ci"]))]
xpos = [0, 1, 2, 3.5, 4.5]
for (lab, fn), x in zip(forms, xpos):
    for dx, j, name in ((-0.13, Q, "Qwen2.5-7B"), (0.13, P, "phi-4")):
        m, ci = fn(j)
        a1.errorbar(x + dx, m, yerr=yerr(m, ci), fmt=MARK[name], color=BLUE, ms=5, elinewidth=0.9, capsize=1.8, zorder=4)
a1.axvline(2.75, color=GRID, lw=1.0, zorder=1)
a1.text(1.0, 5.6, "bare reference", ha="center", fontsize=7.6, color=INK)
a1.text(4.0, 5.6, "worked solution,\nfinal answer", ha="center", va="bottom", fontsize=7.6, color=INK)
a1.axhline(0, color=MUTED, lw=0.8, zorder=2)
a1.set_xticks(xpos, ["31", "thirty-\none", "30+1", "visible", "masked"], fontsize=7.2)
a1.set_xlim(-0.5, 5.0)
a1.set_ylim(-1.6, 7.2)
a1.set_ylabel("anchoring margin\n(points, 0–10 scale)")
a1.set_title("How the reference is written", loc="left")
a1.legend(handles=[Line2D([], [], marker="o", ls="", color=BLUE, label="Qwen2.5-7B"),
                   Line2D([], [], marker="s", ls="", color=BLUE, label="phi-4")],
          loc="lower left", frameon=False, handlelength=1.0, fontsize=6.8)
style(a1)
label(a1, "a")

strata = [("scalar", "integer"), ("pair", "pair"), ("json", "JSON"), ("program", "program")]
for j, name, off in ((Q, "Qwen2.5-7B", -0.08), (P, "phi-4", 0.08)):
    for i, (s, _) in enumerate(strata):
        m, ci = sc[j][s]["infl"], sc[j][s]["infl_ci"]
        a2.errorbar(i + off, m, yerr=yerr(m, ci), fmt=MARK[name], color=BLUE, ms=4.5, mfc=BLUE,
                    mec=BLUE, elinewidth=0.9, capsize=1.8, zorder=4)
a2.axhline(0, color=MUTED, lw=0.8, zorder=2)
a2.set_xticks(range(4), [l for _, l in strata])
a2.set_xlim(-0.5, 3.5)
a2.set_ylim(-0.7, 2.2)
a2.set_xlabel("requested answer format")
a2.set_ylabel("added inflation\n(pool SDs)")
a2.set_title("What form the answer takes", loc="left")
a2.legend(handles=[Line2D([], [], marker="o", ls="", color=BLUE, label="Qwen2.5-7B"),
                   Line2D([], [], marker="s", ls="", color=BLUE, label="phi-4")],
          loc="lower left", frameon=False, handlelength=1.0)
style(a2)
label(a2, "b", x=-0.22)
fig.tight_layout(w_pad=2.0)
save(fig, "fig3_mechanism")

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

# ============================================================== Figure: what the reference costs (grading and selection)
ph4 = load("r4_posthoc_results.json") or {}
mace3 = load("r3_mace_accuracy_results.json")
if r4res.get("grading"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.5, 2.5), gridspec_kw={"width_ratios": [1.15, 1.1]})
    G = r4res["grading"]
    groups = [(glab, G[p][k], plab) for p, plab in (("repl", "Replication"), ("mace", "MACE")) if p in G
              for k, glab in (("G_nm", "non-\nmatching"), ("G_all", "all\ncorrect"))]
    for i, (lab, g, plab) in enumerate(groups):
        for dx, key, col in ((-0.17, "blind", ORANGE), (0.17, "ref", BLUE)):
            v = g[key]
            a1.plot([i + dx, i + dx], v[1], color=col, lw=1.1, zorder=3)
            a1.plot(i + dx, v[0], "o", ms=4.8, color=col, zorder=4)
            a1.text(i + dx, v[1][1] + 0.008, f"{v[0]:.2f}", ha="center", va="bottom", fontsize=5.8, color=MUTED)
    for c0, plab in ((0.5, "Replication"), (2.5, "MACE")):
        a1.text(c0, 1.0, plab, ha="center", va="bottom", fontsize=7, color=INK)
    a1.axvline(1.5, color=GRID, lw=0.9, zorder=1)
    a1.axhline(0.5, color=MUTED, lw=0.8, ls=":", zorder=2)
    a1.text(len(groups) - 0.45, 0.51, "chance", fontsize=6.0, color=MUTED, ha="right", va="bottom")
    a1.set_xlim(-0.6, len(groups) - 0.4)
    a1.set_ylim(0.45, 1.06)
    a1.set_xticks(range(len(groups)), [g[0] for g in groups], fontsize=6.3)
    a1.set_ylabel("AUROC, correct vs. wrong\nanswers (per task)")
    a1.set_title("Grading (Qwen2.5-7B)", loc="left")
    style(a1)
    label(a1, "a", x=-0.3)

    pr = []
    if r4res.get("repl_accuracy"):
        pr.append(("Replication (prereg.)", r4res["repl_accuracy"]["ref_minus_blind"], acc["repl"][P]["acc_ref_minus_blind"]))
    kq = (r4res.get("kpool") or {}).get(Q, {}).get("escore", {})
    for k, lab in (("k1", "k-pool, k = 1"), ("kgt1", "k-pool, k > 1")):
        if k in kq:
            pr.append((lab, kq[k]["ref_minus_blind"], acc["kpool"][P][k]["ref_minus_blind"]))
    mq = ph4.get("mace_exact_q7", {})
    for k, lab in (("k1", "MACE, k = 1"), ("kgt1", "MACE, k > 1")):
        if k in mq:
            pr.append((lab, mq[k]["ref_minus_blind"], mace3[P][k]["ref_minus_blind"]))
    mm = (r4res.get("math") or {}).get(Q)
    if mm:
        pr.append(("MATH-500, solution", mm["ref_minus_noref"], None))
        pr.append(("MATH-500, final answer", mm["refans_minus_noref"], None))
    n = len(pr)
    for pos, (lab, q, p4v) in enumerate(pr):
        y = n - 1 - pos
        a2.plot([100 * q[1][0], 100 * q[1][1]], [y + 0.12] * 2, color=INK, lw=1.0, zorder=3)
        a2.plot(100 * q[0], y + 0.12, "o", ms=4.8, color=INK, zorder=4)
        if p4v:
            a2.plot([100 * p4v[1][0], 100 * p4v[1][1]], [y - 0.14] * 2, color=MUTED, lw=0.9, zorder=3)
            a2.plot(100 * p4v[0], y - 0.14, "s", ms=4.2, mfc="white", mec=INK, color=INK, zorder=4)
    a2.axvline(0, color=MUTED, lw=0.8, zorder=2)
    a2.set_yticks(range(n), [p[0] for p in pr[::-1]], fontsize=6.6)
    a2.set_xlim(-75, 75)
    a2.set_xlabel("accuracy change from showing\nthe reference (points)")
    a2.set_title("Selection", loc="left")
    a2.legend(handles=[Line2D([], [], marker="o", ls="", color=INK, label="Qwen2.5-7B"),
                       Line2D([], [], marker="s", ls="", mfc="white", mec=INK, color=INK, label="phi-4")],
              loc="lower left", frameon=False, handlelength=1.0, fontsize=6.6)
    style(a2, "x")
    label(a2, "b", x=-0.62)
    fig.tight_layout(w_pad=1.0)
    fig.legend(handles=[Patch(color=ORANGE, label="blind"), Patch(color=BLUE, label="reference shown")], loc="upper left",
               bbox_to_anchor=(0.12, 0.1), ncol=2, frameon=False, handlelength=1.0, fontsize=6.6)
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
