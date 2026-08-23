# Conceptual Figure 1: the compare-vs-verify divide, drawn as a schematic (no data).
# Palette as in make_paper_figs.py: ORANGE = comparison (fails), BLUE = verification (works).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BLUE, ORANGE, GRAY, INK = "#4269d0", "#c5541a", "#6b7280", "#1a1a1a"
BLUE_BG, ORANGE_BG = "#e8edfa", "#f9ebe2"

fig, ax = plt.subplots(figsize=(12.5, 4.4))
ax.set_xlim(0, 100)
ax.set_ylim(0, 36)
ax.axis("off")


def box(x, y, w, h, text, fc="white", ec=GRAY, fs=8.5, weight="normal", tc=INK, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4",
                                facecolor=fc, edgecolor=ec, linewidth=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, weight=weight, linespacing=1.35)


def arrow(x1, y1, x2, y2, color=GRAY, style="-|>", lw=1.4, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, color=color,
                                 linewidth=lw, linestyle=ls, mutation_scale=13,
                                 shrinkA=2, shrinkB=2))


# ------------------------------------------------ shared input (left)
box(1.5, 20, 13, 10, "Problem\n+\ncandidate solution", fc="white", ec=INK, fs=9, weight="bold")

# ------------------------------------------------ TOP: comparison (orange, fails)
ax.text(24, 33.6, "COMPARE  (measures the reference, not the solution)", fontsize=9.5,
        color=ORANGE, weight="bold", ha="left")
box(24, 24.5, 15, 6.5, 'Reference text\n"the gold solution"', fc=ORANGE_BG, ec=ORANGE)
box(45, 24.5, 21, 6.5, "How similar is the candidate\nto the reference text?\n(TFA, logprob, TF-IDF, embeddings)",
    fc=ORANGE_BG, ec=ORANGE, fs=8)
box(73, 24.5, 25, 6.5, "Score mostly reflects how predictable\nthe REFERENCE is (80% perplexity);\nuncorrelated with human judgment",
    fc="white", ec=ORANGE, fs=8, tc=ORANGE, weight="bold")
arrow(14.5, 27.5, 24, 27.7, color=ORANGE)
arrow(39, 27.7, 45, 27.7, color=ORANGE)
arrow(66, 27.7, 73, 27.7, color=ORANGE)

# ------------------------------------------------ BOTTOM: verification (blue, works)
ax.text(24, 17.3, "VERIFY  (measures the solution against something checkable)", fontsize=9.5,
        color=BLUE, weight="bold", ha="left")
box(24, 8.5, 15, 7, "Checkable endpoint:\nfinal answer, unit tests,\nor a trusted reference\nthe judge can check",
    fc=BLUE_BG, ec=BLUE, fs=7.6)
box(45, 8.5, 21, 7, "Does the work hold up?\nrun the tests / complete the\ntruncated solution / referenced\nLLM judge checks the steps",
    fc=BLUE_BG, ec=BLUE, fs=7.6)
box(73, 8.5, 25, 7, "Score tracks human judgment\n(completion test +0.79, judge +0.86\npartial; tests are a free oracle)",
    fc="white", ec=BLUE, fs=8, tc=BLUE, weight="bold")
arrow(14.5, 22.5, 24, 13.5, color=BLUE)
arrow(39, 12, 45, 12, color=BLUE)
arrow(66, 12, 73, 12, color=BLUE)

# ------------------------------------------------ bottom strip: certification
ax.plot([1.5, 98], [6.2, 6.2], color="#d0d0d0", lw=0.8)
ax.text(1.5, 4.3, "CERTIFY BEFORE TRUSTING:", fontsize=9, color=INK, weight="bold", va="center")
box(22, 1.2, 20, 4.3, "blind audit: ~60 human labels,\ntwo scales (soundness / style)", fc="white", ec=GRAY, fs=7.8)
box(50, 1.2, 15, 4.3, "PASS: judge verifies\n(reads content)", fc=BLUE_BG, ec=BLUE, fs=7.8, tc=BLUE)
box(50, -4.6, 15, 4.3, "FAIL: judge compares\n(rewards style)", fc=ORANGE_BG, ec=ORANGE, fs=7.8, tc=ORANGE)
box(72, 1.2, 26, 4.3, "resists gaming under best-of-64\nselection pressure", fc="white", ec=BLUE, fs=7.8, tc=BLUE)
box(72, -4.6, 26, 4.3, "gets gamed: inflated scores,\nreal accuracy lost", fc="white", ec=ORANGE, fs=7.8, tc=ORANGE)
arrow(42, 3.3, 50, 3.3)
arrow(46, 3.3, 50, -2.4)
arrow(65, 3.3, 72, 3.3, color=BLUE)
arrow(65, -2.4, 72, -2.4, color=ORANGE)
ax.set_ylim(-5.5, 36)

fig.savefig("figs/fig0_concept.png", dpi=300, bbox_inches="tight")
print("wrote figs/fig0_concept.png")
