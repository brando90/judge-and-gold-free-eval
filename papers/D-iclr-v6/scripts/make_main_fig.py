#!/usr/bin/env python
"""Candidate main figure: the claim as data, in three panels that make one argument.

WHAT THE EARLIER CANDIDATES GOT WRONG. fig_main_candidate.tex is a three-band schematic, mostly
text in boxes, so a reviewer reads it rather than sees it, and two of its bands restate figures the
paper already has. fig_grid_candidate is a real chart of a secondary question (do prompt fixes
help), and every cell of it is post hoc. Neither shows the paper's claim as data.

THE MODEL FOR THIS ONE. Putnam-AXIOM's Figure 3 puts one row per model and two connected dots for
the two conditions, sorted by the drop; the drop is the picture, and every model is shown, so no
one can ask what was left out. That is structurally this paper's problem -- same items, two
grading conditions -- so panel (a) is built that way. The Mirage paper's Figure 2 makes its
argument through LAYOUT: same underlying data, scored two ways, opposite conclusions. That is why
these three panels are ordered as they are rather than sized by how much data each holds.

THE ARGUMENT, one panel at a time:

(a) IT HAPPENS TO EVERY JUDGE.  Twelve judge-by-pool cells, no holes. Each row is the same set of
    correct answers scored twice by the same judge: once with the reference set to that answer,
    once with the reference set to a DIFFERENT correct answer. The text is byte-identical between
    the two dots. Sorted by the drop, which runs from 4.7 points out of 10 down to 0.1. Showing
    all twelve is the point -- the small frontier drops are as much a result as the large ones, and
    a figure that showed only Qwen2.5-7B would deserve the cherry-picking question.

(b) A "4.7 POINT DROP" IS NOT A GENTLE SHIFT.  The same 449 answers under three prompts, as whole
    distributions. With the reference set to the answer itself the mass piles on 10; on identical
    text with a different correct answer shown, 130 of 449 are scored ZERO. A mean hides that.

(c) IT IS NOT THAT THE JUDGE CANNOT VERIFY.  Answers two frontier judges had ALREADY accepted with
    no reference in front of them -- they had shown they can tell the answer is correct. Showing a
    different correct answer takes the credit back from 117 of 843. Two controls: asked a second
    time still blind, 2 of the same 843 fall; and of 383 accepted answers that MATCH the shown
    reference, none falls. That second control is the stronger one and the earlier schematic
    omitted it: same judges, same prompt, a reference displayed in both arms, differing only in
    whether the candidate happens to agree with it.

COLOUR. make_figures.py fixes orange = blind, blue = reference shown. The harm condition --
reference shown AND differing from the candidate -- has no colour there, and fig1_concept already
paints it red; that is the extension, used here and nowhere else. Judges are never colour-coded.

PROVENANCE. (a) and (b) from experiments/tfa-vs-judge/runs/v4_judge/*.jsonl, the stored runs behind
tab:panel2-mitig's bare column. (c) from papers/analysis/r20a_{sonnet,opus}_retest.json. Every
plotted number is written to papers/analysis/main_fig_values.json so the caption can be checked
without rerunning the figure.
"""

import collections
import json
import random
import statistics as st
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
ANALYSIS = PAPER.parent / "analysis"
RUNS = PAPER.parent.parent / "experiments" / "tfa-vs-judge" / "runs" / "v4_judge"
FIG = PAPER / "figures"

BLUE, ORANGE, RED, GREY = "#4269d0", "#c5541a", "#a51c30", "#9a9a9a"
INK, MUTED, GRID = "#1a1a1a", "#5f5f5f", "#e6e6e6"
SEED, B = 20260923, 4000

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.5, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "pdf.fonttype": 42, "axes.linewidth": 0.8, "axes.unicode_minus": True,
})

CELLS = [("MACE", "Qwen2.5-7B", "QWEN_mace_bare"), ("MACE", "Qwen2.5-14B", "QWEN14B_mace_bare"),
         ("MACE", "gemma-2-9b", "GEMMA_mace_bare"), ("MACE", "phi-4", "PHI4_mace_bare"),
         ("MACE", "GPT-4.1", "GPT41_mace_r10bare"), ("MACE", "Sonnet 5", "SONNET_mace_bare"),
         ("arith.", "Qwen2.5-7B", "QWEN_repl_bare"), ("arith.", "Qwen2.5-14B", "QWEN14B_repl_bare"),
         ("arith.", "gemma-2-9b", "GEMMA_repl_bare"), ("arith.", "phi-4", "PHI4_repl_bare"),
         ("arith.", "GPT-4.1", "BRIDGE_gpt41_repl"), ("arith.", "Sonnet 5", "SONNET_repl_bare")]
FEATURE = "QWEN_mace_bare"      # panel (b): the largest cell, named as such in the caption


def per_candidate(stem):
    """{(question_id, sample): {condition: mean grade}}, correct candidates only."""
    f = RUNS / f"{stem}.jsonl"
    if not f.exists():
        sys.exit(f"missing {f}")
    c = collections.defaultdict(lambda: collections.defaultdict(list))
    for line in open(f):
        r = json.loads(line)
        if r.get("candidate_valid") is not True:
            continue
        try:
            g = float(r["grade"])
        except (TypeError, ValueError):
            continue                       # "NA" is dropped, never read as zero
        c[(r["question_id"], r["sample"])][r["condition"]].append(g)
    return {k: {n: st.mean(v) for n, v in d.items()} for k, d in c.items()}


def drop_with_ci(stem, tag):
    """Mean score under a matching vs a differing correct reference, on the same answers.

    Intervals are an item-clustered bootstrap over question_id, matching the estimator the rest of
    the paper uses -- a candidate's two scores are not independent of its question's difficulty."""
    cand = per_candidate(stem)
    by_item = collections.defaultdict(list)
    for (qid, _s), d in cand.items():
        if "C1_match" in d and "C1_differ" in d:
            by_item[qid].append((d["C1_match"], d["C1_differ"]))
    pairs = [p for v in by_item.values() for p in v]
    if not pairs:
        sys.exit(f"{stem}: no candidate has both a matching and a differing reference")
    match, differ = st.mean(m for m, _ in pairs), st.mean(d for _, d in pairs)
    items, rng, deltas = list(by_item), random.Random(f"{SEED}|{tag}"), []
    for _ in range(B):
        draw = [p for _ in items for p in by_item[rng.choice(items)]]
        deltas.append(sum(d - m for m, d in draw) / len(draw))
    deltas.sort()
    return dict(match=round(match, 3), differ=round(differ, 3),
                drop=round(differ - match, 3),
                ci=[round(deltas[int(.025 * B)], 3), round(deltas[int(.975 * B)], 3)],
                n_candidates=len(pairs), n_items=len(items))


def panel_b_data():
    cand = per_candidate(FEATURE)
    keys = [k for k, d in cand.items()
            if all(n in d for n in ("C0", "C1_match", "C1_differ"))]
    return {n: [cand[k][n] for k in keys] for n in ("C0", "C1_match", "C1_differ")}, len(keys)


def panel_c_data():
    pooled = {}
    for who in ("sonnet", "opus"):
        p = ANALYSIS / f"r20a_{who}_retest.json"
        if not p.exists():
            sys.exit(f"missing {p}")
        pooled[who] = json.loads(p.read_text())["pooled"]
    nm = [pooled[w]["nonmatch"] for w in pooled]
    mt = [pooled[w]["match"] for w in pooled]
    return dict(n_differ=sum(d["n"] for d in nm),
                differ_referenced=sum(d["referenced_le3"] for d in nm),
                differ_retest=sum(d["retest_le3"] for d in nm),
                n_match=sum(d["n"] for d in mt),
                match_referenced=sum(d["referenced_le3"] for d in mt))


def draw(rows, b, n_paired, c, stem="fig_main_v3"):
    # Panel titles are one short line each; the explanation belongs in the caption, and multi-line
    # titles collided across panels at this width.
    fig = plt.figure(figsize=(7.1, 3.15))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.32, 0.86, 0.88], wspace=0.46,
                          left=0.135, right=0.995, top=0.865, bottom=0.155)

    # ================= (a) every judge, both pools: the same answers scored twice
    axa = fig.add_subplot(gs[0])
    rows = sorted(rows, key=lambda r: r["drop"])          # biggest drop at the top
    for y, r in enumerate(rows):
        axa.plot([r["match"], r["differ"]], [y, y], "-", color=GREY, lw=1.5,
                 solid_capstyle="round", zorder=2)
        # the interval is on the DROP, so it is drawn on the differing dot, which is the end that
        # moves; putting a bar on each dot separately would imply two independent estimates
        axa.plot([r["match"] + r["ci"][0], r["match"] + r["ci"][1]], [y, y], "-",
                 color=RED, lw=0.9, alpha=0.65, zorder=3)
        axa.plot(r["match"], y, "o", color=BLUE, ms=4.4, zorder=4)
        axa.plot(r["differ"], y, "o", color=RED, ms=4.4, zorder=4)
    axa.set_yticks(range(len(rows)))
    axa.set_yticklabels([f"{r['judge']}  ({r['pool']})" for r in rows], fontsize=7.0)
    axa.invert_yaxis()
    axa.set_xlim(2.55, 10.45)
    axa.set_xlabel("mean score out of 10, identical text", fontsize=7.8)
    axa.spines[["top", "right"]].set_visible(False)
    axa.tick_params(length=2.5, width=0.8)
    axa.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    axa.set_axisbelow(True)
    axa.set_title("a   Every judge: the same answers, two references",
                  fontsize=8.4, color=INK, loc="left", pad=5)
    axa.legend(handles=[Line2D([], [], marker="o", ls="", color=BLUE, ms=4.4,
                               label="reference = this answer"),
                        Line2D([], [], marker="o", ls="", color=RED, ms=4.4,
                               label="reference = another correct answer")],
               loc="lower left", frameon=False, fontsize=6.3, handletextpad=0.3,
               borderpad=0.05, labelspacing=0.25)

    # ================= (b) the drop is a collapse, not a shift
    gsb = gs[1].subgridspec(3, 1, hspace=0.34)
    axb = [fig.add_subplot(gsb[i]) for i in range(3)]
    conds = [("C1_match", "reference = this answer", BLUE),
             ("C1_differ", "reference = a different\ncorrect answer", RED),
             ("C0", "no reference shown", ORANGE)]
    top = max(max(collections.Counter(round(v) for v in b[k]).values()) for k, _, _ in conds)
    for ax, (key, label, colour) in zip(axb, conds):
        h = collections.Counter(round(v) for v in b[key])
        ax.bar(range(11), [h.get(i, 0) for i in range(11)], width=0.84,
               color=colour, edgecolor="white", linewidth=0.35, zorder=3)
        ax.set_xlim(-0.75, 10.75)
        ax.set_ylim(0, top * 1.30)
        ax.set_yticks([])
        ax.set_xticks(range(0, 11, 5))
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(length=2.5, width=0.8)
        # Label sits INSIDE its own axes -- above the axes it was ambiguous which histogram it
        # named -- and on the side away from that histogram's tallest bar, so it never sits on data.
        tall = max(range(11), key=lambda i: h.get(i, 0))
        left = tall > 5
        ax.text(0.02 if left else 0.98, 0.97, label, transform=ax.transAxes, fontsize=6.8,
                va="top", ha="left" if left else "right", color=colour,
                fontweight="bold", linespacing=1.1)
        if ax is not axb[-1]:
            ax.set_xticklabels([])
    z = collections.Counter(round(v) for v in b["C1_differ"]).get(0, 0)
    # two lines: on one line this ran past the panel's right edge into panel (c)'s labels
    axb[1].annotate(f"{z} of {n_paired}\nscored 0", (0.42, z), xytext=(0.26, 0.50),
                    textcoords="axes fraction", fontsize=6.7, color=RED, va="center",
                    linespacing=1.1,
                    arrowprops=dict(arrowstyle="-", color=RED, lw=0.7, shrinkA=2, shrinkB=1))
    axb[-1].set_xlabel("score out of 10", fontsize=7.8)
    axb[0].set_title("b   A collapse, not a shift",
                     fontsize=8.4, color=INK, loc="left", pad=5)

    # ================= (c) not verification failure
    axc = fig.add_subplot(gs[2])
    bars = [("shown a different\ncorrect answer", c["differ_referenced"], c["n_differ"], RED),
            ("shown a matching\ncorrect answer", c["match_referenced"], c["n_match"], BLUE),
            ("asked again,\nstill blind", c["differ_retest"], c["n_differ"], ORANGE)]
    for y, (lab, k, n, colour) in enumerate(bars):
        pct = 100.0 * k / n
        axc.barh(y, pct, height=0.54, color=colour, zorder=3)
        axc.text(pct + 0.55, y, f"{k} of {n}", va="center", fontsize=7.1,
                 color=colour if k else MUTED, fontweight="bold" if k else "normal")
    axc.set_yticks(range(len(bars)))
    axc.set_yticklabels([x[0] for x in bars], fontsize=6.9, linespacing=1.15)
    axc.invert_yaxis()
    axc.set_xlim(0, 21.5)
    axc.set_xlabel("% of already-accepted answers\nnow scored 3 of 10 or below", fontsize=7.6)
    axc.spines[["top", "right"]].set_visible(False)
    axc.tick_params(length=2.5, width=0.8)
    axc.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    axc.set_axisbelow(True)
    axc.set_title("c   Credit taken back, not withheld",
                  fontsize=8.4, color=INK, loc="left", pad=5)

    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{stem}.{ext}", dpi=300 if ext == "png" else None,
                    bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"  wrote figures/{stem}.pdf and .png")


if __name__ == "__main__":
    rows = []
    print("  (a) same answers, matching vs differing correct reference")
    print(f"      {'pool':<8}{'judge':<14}{'match':>7}{'differ':>8}{'drop':>8}   95% CI")
    for pool, judge, stem in CELLS:
        r = drop_with_ci(stem, f"{pool}|{judge}")
        r.update(pool=pool, judge=judge, source=f"{stem}.jsonl")
        rows.append(r)
        print(f"      {pool:<8}{judge:<14}{r['match']:>7.2f}{r['differ']:>8.2f}"
              f"{r['drop']:>+8.2f}   [{r['ci'][0]:+.2f}, {r['ci'][1]:+.2f}]  "
              f"n={r['n_candidates']}")
    b, n_paired = panel_b_data()
    c = panel_c_data()
    print(f"\n  (b) {n_paired} answers graded under all three prompts "
          f"({FEATURE.replace('.jsonl','')})")
    for k in ("C1_match", "C1_differ", "C0"):
        h = collections.Counter(round(v) for v in b[k])
        print(f"      {k:<10} mean {st.mean(b[k]):5.2f}   at 10: {h.get(10,0):>3}   "
              f"at 0: {h.get(0,0):>3}")
    print(f"\n  (c) differing: {c['differ_referenced']}/{c['n_differ']} fall; "
          f"repeat blind {c['differ_retest']}/{c['n_differ']}; "
          f"matching {c['match_referenced']}/{c['n_match']}")

    (ANALYSIS / "main_fig_values.json").write_text(json.dumps(
        dict(panel_a=rows,
             panel_b=dict(n_paired=n_paired, judge="Qwen2.5-7B", pool="MACE",
                          source=f"{FEATURE}.jsonl",
                          by_condition={k: dict(mean=round(st.mean(b[k]), 3),
                                                hist={str(i): collections.Counter(
                                                    round(v) for v in b[k]).get(i, 0)
                                                    for i in range(11)})
                                        for k in ("C0", "C1_match", "C1_differ")}),
             panel_c=c), indent=1))
    print("  wrote papers/analysis/main_fig_values.json")
    draw(rows, b, n_paired, c)
