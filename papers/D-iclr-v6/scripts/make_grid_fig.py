#!/usr/bin/env python
"""Candidate main figure: the whole mitigation grid, every judge x every pool x every prompt fix.

WHY THIS FIGURE. tab:panel2-mitig currently carries 50 cells and their intervals as a wall of
numbers in the appendix. Three facts live in it that a table cannot show and that a reviewer asks
for in this order:

  1. HOW BIG, AND ON WHOM.  The bare effect runs from -3.42 of 10 (Qwen2.5-7B) to -0.15 (Sonnet 5).
     That vertical spread at the left edge of each panel is the generalisation answer.
  2. DO THE FIXES WORK.  Every line rises toward zero and none of the large ones reaches it.
     Qwen2.5-7B keeps -1.22 of 10 under its best arm.
  3. DOES IT DEPEND ON THE DATA.  The two panels answer this directly: on MACE the lines climb,
     on the replication pool Qwen2.5-7B's are flat. Same judge, same fixes, different pool.

GRAMMAR. make_figures.py fixes the paper's colour grammar: colour encodes CONDITION (orange blind,
blue reference shown, teal blind-then-reveal, grey neither/placebo) and judges are told apart by
MARKER SHAPE, never by colour. Every cell here is one condition -- a referenced-minus-blind paired
effect -- so every mark is blue, judges take their marker from make_figures.MARK, and the prompt arm
is encoded by POSITION on the x axis. Nothing in this figure invents a new colour meaning.

PROVENANCE. Values come from papers/analysis/panel2_mitigation_results.json, written by
panel2_mitigation_analysis.py from the stored judge runs. That producer did not exist when this
figure was first drawn -- the table's 50 cells had been computed ad hoc and typed into appendix.tex
-- so this script originally parsed the LaTeX table instead. It still can (--from-tex), and the two
paths are checked against each other, because the table is what a reader sees and a figure that
disagrees with it would be worse than either. Nothing here is retyped by hand: transcription is how
two errors reached this draft earlier on.

STATUS. The whole panel-2 grid is POST HOC (app:panel2 says so in its first line). If this is
promoted to the main text the caption must carry \\ph and the registered rotation result must stay
the headline.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
ANALYSIS = PAPER.parent / "analysis"
FIG = PAPER / "figures"

# --- borrowed verbatim from make_figures.py so the two figures cannot drift apart
BLUE, ORANGE, TEAL, GREY = "#4269d0", "#c5541a", "#2a9d8f", "#9a9a9a"
INK, MUTED, GRID = "#1a1a1a", "#5f5f5f", "#e6e6e6"
MARK = {"Qwen2.5-7B": "o", "phi-4": "s", "Qwen2.5-14B": "D", "gemma-2-9b": "v",
        "Mistral-7B": "<", "Sonnet 5": "^", "Qwen3-8B": "P", "Qwen3-14B": "X",
        "GPT-4.1": "*"}  # GPT-4.1 is new to the panel; no earlier figure assigns it a marker

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.5, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "pdf.fonttype": 42, "axes.linewidth": 0.8, "axes.unicode_minus": True,
})

ARMS = ["None", "Several", "Forbid", "CoT", "Verify"]
# Short axis labels; the caption carries the full wording, as tab:panel2-mitig's does. Long
# labels collided at this width and the collision is not fixable by rotation without costing
# the reader more than the abbreviation does.
ARM_LONG = {"None": "bare", "Several": "several", "Forbid": "forbid",
            "CoT": "reason\nfirst", "Verify": "verify\nfirst"}


def parse_table(tex_path):
    """Pull tab:panel2-mitig out of appendix.tex. Returns {pool: {judge: {arm: (est, lo, hi)}}}.

    Mechanical parse of the committed table -- the same numbers the paper prints. No retyping.
    """
    s = Path(tex_path).read_text()
    i = s.find("\\label{tab:panel2-mitig}")
    if i < 0:
        sys.exit("could not find tab:panel2-mitig in " + str(tex_path))
    body = s[i:s.find("\\end{tabular}", i)]

    # $-3.42$ \ci{-3.83}{-3.03}   ->  (-3.42, -3.83, -3.03)
    cell = re.compile(r"\$([+-]?[\d.]+)\$\s*\\ci\{([+-]?[\d.]+)\}\{([+-]?[\d.]+)\}")
    out, pool = {}, None
    for line in body.split("\n"):
        if "\\multicolumn" in line and "\\emph" in line:
            pool = "MACE" if "MACE" in line else "Replication"
            out[pool] = {}
            continue
        if pool is None or "&" not in line or "\\midrule" in line:
            continue
        judge = line.split("&")[0].strip().replace("\\textsc{", "").replace("}", "")
        judge = judge.replace("~", " ").strip()
        vals = cell.findall(line)
        if not judge or not vals:
            continue
        if len(vals) != len(ARMS):
            sys.exit(f"{pool}/{judge}: parsed {len(vals)} cells, expected {len(ARMS)}")
        out[pool][judge] = {a: tuple(float(x) for x in v) for a, v in zip(ARMS, vals)}
    return out


def parse_json(path):
    """Read the producer output. Returns {pool: {judge: {arm: (est, lo, hi)}}}.

    Cells the producer marks as bare-arm-only (GPT-4.1 and Sonnet 5 on the replication pool) are
    dropped: a judge with one of five arms cannot be drawn as a line, and half a line would read
    as a result rather than as an absence.
    """
    raw = json.loads(Path(path).read_text())
    out = {}
    for pool, judges in raw.items():
        out[pool] = {}
        for judge, arms in judges.items():
            if not all(a in arms for a in ARMS):
                continue
            out[pool][judge] = {a: (arms[a]["estimate"], *arms[a]["ci"]) for a in ARMS}
    return out


def cross_check(a, b, la, lb):
    """Both provenance paths must agree to the printed precision, or we stop."""
    bad = 0
    for pool in set(a) | set(b):
        for judge in set(a.get(pool, {})) | set(b.get(pool, {})):
            for arm in ARMS:
                x = a.get(pool, {}).get(judge, {}).get(arm)
                y = b.get(pool, {}).get(judge, {}).get(arm)
                if x is None or y is None:
                    continue
                if abs(round(x[0], 2) - round(y[0], 2)) > 0.005:
                    print(f"  MISMATCH {pool}/{judge}/{arm}: {la} {x[0]:.3f} vs {lb} {y[0]:.3f}")
                    bad += 1
    print(f"  cross-check {la} vs {lb}: {'OK' if not bad else str(bad) + ' DISAGREE'}")
    if bad:
        sys.exit(1)


def draw(data, out_stem):
    pools = [p for p in ("MACE", "Replication") if p in data]
    fig, axes = plt.subplots(1, len(pools), figsize=(6.9, 2.95), sharey=True,
                             gridspec_kw=dict(wspace=0.06, left=0.105, right=0.805,
                                              top=0.87, bottom=0.17))
    if len(pools) == 1:
        axes = [axes]

    titles = {"MACE": "MACE  (factual, several correct answers)",
              "Replication": "Replication pool  (arithmetic)"}
    x = range(len(ARMS))

    for ax, pool in zip(axes, pools):
        judges = sorted(data[pool], key=lambda j: data[pool][j]["None"][0])  # worst at the bottom
        ax.axhline(0, color=MUTED, lw=0.9, zorder=1)
        for judge in judges:
            arms = data[pool][judge]
            ys = [arms[a][0] for a in ARMS]
            ax.plot(x, ys, "-", color=BLUE, lw=1.0, alpha=0.55, zorder=2)
            for xi, a in zip(x, ARMS):
                est, lo, hi = arms[a]
                ax.plot([xi, xi], [lo, hi], "-", color=BLUE, lw=0.8, alpha=0.5, zorder=2)
            ax.plot(x, ys, MARK.get(judge, "o"), color=BLUE, ms=4.2, mew=0.8,
                    mfc="white", mec=BLUE, zorder=3)
        # With six series the legend carries identity; in-plot labels collided at the bare arm
        # (Sonnet 5 over GPT-4.1, Qwen2.5-14B over gemma-2-9b) and are dropped rather than nudged.
        # The two judges absent from a pool are named, so a hole reads as a hole and not as a
        # judge that came out clean.
        absent = sorted(set(data["MACE"]) - set(data[pool]))
        if absent:
            ax.annotate("not run on this pool: " + ", ".join(absent),
                        (0.5, 0.035), xycoords="axes fraction", ha="center",
                        fontsize=6.4, color=MUTED, style="italic")
        ax.set_xticks(list(x))
        ax.set_xticklabels([ARM_LONG[a] for a in ARMS], fontsize=7.2, color=INK)
        ax.set_title(titles[pool], fontsize=8.2, color=INK, pad=5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(length=2.5, width=0.8)
        ax.set_xlim(-0.45, len(ARMS) - 0.55)
        ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
        ax.set_axisbelow(True)

    axes[0].set_ylabel("change in score when a different\ncorrect answer is the reference\n(points out of 10)",
                       fontsize=7.6)
    axes[0].set_ylim(-4.0, 0.62)

    handles = [Line2D([], [], marker=MARK.get(j, "o"), color=BLUE, mfc="white", mec=BLUE,
                      ms=4.2, lw=1.0, label=j)
               for j in sorted(data["MACE"], key=lambda j: data["MACE"][j]["None"][0])]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(0.822, 0.53),
               frameon=False, handlelength=1.6, labelspacing=0.55, fontsize=7.0)

    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{out_stem}.{ext}", dpi=300 if ext == "png" else None,
                    bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"  wrote figures/{out_stem}.pdf and .png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-tex", action="store_true",
                    help="draw from the LaTeX table instead of the producer JSON")
    ap.add_argument("--out", default="fig_grid_candidate")
    a = ap.parse_args()

    from_tex = parse_table(PAPER / "appendix.tex")
    results = ANALYSIS / "panel2_mitigation_results.json"
    data = from_tex
    if results.exists():
        from_json = parse_json(results)
        cross_check(from_json, from_tex, "JSON", "table")
        if not a.from_tex:
            data = from_json
    else:
        print(f"  NOTE: {results.name} not present; drawing from the LaTeX table", file=sys.stderr)

    n = sum(len(v) for v in data.values())
    print(f"  {n} judge-pool rows x {len(ARMS)} arms = {n * len(ARMS)} cells "
          f"(source: {'table' if data is from_tex else 'producer JSON'})")
    for pool in data:
        print(f"    {pool}: {', '.join(sorted(data[pool]))}")
    draw(data, a.out)
