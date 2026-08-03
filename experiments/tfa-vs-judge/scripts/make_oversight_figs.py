# Figures for the oversight story deck + paper. All numbers from the verified run record
# (docs/oversight-log.md); every value survived adjudication/controls.
# v2 wording pass (Brando review rules + professor critique): sentence case, no shouting caps,
# no jargon ("grading oracle" -> "answer key"), units on every axis, verdicts in plain language.
# This file is the canonical source for f0-f9 (f0 and the f2 waffle were previously ad-hoc).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np, os

os.makedirs("paper/figs_oversight", exist_ok=True)
C = dict(blue="#2b5c8a", green="#2f8f4e", amber="#c07d15", purple="#7d54c9", red="#c44e52",
         gray="#8a8f98", slate="#3b4252", brown="#8a5a1e", sand="#d9b35c")
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

def save(fig, name):
    fig.tight_layout(); fig.savefig(f"paper/figs_oversight/{name}.png", dpi=160, bbox_inches="tight"); plt.close(fig)
    print("wrote", name)

# ---- f0 method diagram (three steps, colors match the three conditions used later) ----
fig, ax = plt.subplots(figsize=(13.4, 7.6)); ax.axis("off")
ax.set_xlim(0, 100); ax.set_ylim(0, 100)
def box(x, y, w, h, text, fc, tc="white", fs=9.3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6", fc=fc, ec="none"))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs, color=tc, fontweight="bold")
def arrow(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color="#5b6470", lw=1.6))
def step(y, text): ax.text(2, y, text, fontsize=11, color=C["blue"], fontweight="bold")

# step 1
step(97, "Step 1 · Build errors we control (checkable tasks: math and code)")
box(2, 82, 16, 10, "a solution\nverified correct", "#e8eaee", "#22262c")
box(24, 88, 20, 7, "plant a typo\n(one false equation)", C["amber"])
box(24, 79, 20, 8, "plant a hidden error\n(wrong value carried\nthrough all later steps)", C["red"])
box(50, 82, 20, 10, "mechanical check:\narithmetic all true,\ncode fails real tests", C["slate"])
box(76, 82, 22, 10, "bank of known-wrong\nsolutions that read\nsmoothly", C["green"])
arrow(18, 87, 24, 90); arrow(18, 86, 24, 83); arrow(44, 86, 50, 87); arrow(70, 87, 76, 87)

# step 2
step(72, "Step 2 · Show each error to every judge, under three conditions")
box(2, 54, 18, 13, "judges:\nQwen 0.5B to 14B\n+ GPT-5.2, Opus\n(+ 5 more families)", "#e8eaee", "#22262c")
box(26, 63, 26, 5.5, "sees the problem + solution only", C["red"])
box(26, 56, 26, 5.5, "also sees a correct reference", C["green"])
box(26, 47.5, 26, 7, "also sees its own earlier answer,\nwritten in a separate forced pass", C["purple"])
box(58, 51, 40, 14, "measure: does the judge's score drop\non the broken version vs the clean one?\nThat is the detection rate,\nreported per condition", C["blue"])
arrow(20, 62, 26, 65.5); arrow(20, 60, 26, 59); arrow(20, 58, 26, 51.5)
arrow(52, 65.5, 58, 60); arrow(52, 59, 58, 58); arrow(52, 51, 58, 56)

# step 3
step(40, "Step 3 · Repeat on tasks with no answer key")
box(2, 16, 26, 17, "a pair of answers to one prompt,\none known-better, one known-worse.\nTask types range from one right\nanswer ('what is 17 x 24?') to many\nvalid answers ('name a color\nof the rainbow')", "#e8eaee", "#22262c", 8.8)
box(34, 25, 28, 8, "the judge picks the better one,\nsame three conditions, plus a control:\nanother model's answer as reference", C["purple"], fs=8.8)
box(34, 14, 28, 8, "each pair judged twice, order\nswapped; a changed verdict means\norder decided, not content", C["amber"], fs=8.8)
box(68, 16, 30, 14, "two questions answered:\n1. does a reference help or hurt,\nby task type?\n2. how order-dependent are the\nverdicts? (the order-flip rate)", C["slate"], fs=8.8)
arrow(28, 27, 34, 29); arrow(28, 22, 34, 18); arrow(62, 29, 68, 25); arrow(62, 18, 68, 21)
save(fig, "f0_method")

# ---- f1 the apparent law and what checking revealed ----
fig, (a, b) = plt.subplots(1, 2, figsize=(9.4, 3.9))
k = [0, 1, 2, 3]; raw = [1.0, 6.5, 60.5, 94.1]
a.bar(k, raw, color=C["red"], width=0.6)
a.set_xticks(k); a.set_xlabel("# of the 3 small judges fooled by the solution")
a.set_ylabel("% frontier judge also fooled")
a.set_title("Looks like a law: small judges predict\nfrontier failure (raw data)", fontsize=10)
for x, v in zip(k, raw): a.text(x, v + 2, f"{v:.0f}%", ha="center", fontsize=9)
cats = ["answer key\nwas wrong\n(71%)", "genuinely wrong,\nfrontier fooled\n(2%)", "genuinely wrong,\nfrontier right\n(27%)"]
b.bar([0, 1, 2], [71, 2, 27], color=[C["amber"], C["red"], C["green"]], width=0.6)
b.set_xticks([0, 1, 2]); b.set_xticklabels(cats, fontsize=8.5)
b.set_ylabel("% of the 'fooling' cases")
b.set_title("After checking every case:\nthe 94% was mostly answer-key errors", fontsize=10)
save(fig, "f1_mirage")

# ---- f2 the answer-key check, as a waffle: one square per flagged item ----
fig, ax = plt.subplots(figsize=(10.2, 3.6)); ax.axis("off")
groups = [("our matching script misread a correct answer (the key was fine)", 60, C["amber"]),
          ("broken item (the human re-check removed it)", 4, C["brown"]),
          ("wrong key (the human re-check relabeled it to the models' answer)", 2, C["sand"]),
          ("the models were genuinely wrong together", 8, C["green"])]
xi = yi = 0; PERROW = 15
for lab, n, col in groups:
    for _ in range(n):
        ax.add_patch(plt.Rectangle((xi, -yi), 0.88, 0.88, color=col))
        xi += 1
        if xi == PERROW: xi = 0; yi += 1
ax.set_xlim(-0.2, 27); ax.set_ylim(-yi - 2.2, 3.4)
for j, (lab, n, col) in enumerate(groups):
    ax.add_patch(plt.Rectangle((16.2, -j * 1.35 + 0.4), 0.8, 0.8, color=col))
    ax.text(17.4, -j * 1.35 + 0.8, f"{lab}  ({n})", fontsize=9, va="center")
ax.text(-0.2, 2.7, "Each square = one item where several cheap models unanimously gave the same \"wrong\" answer (74 total)",
        fontsize=11, fontweight="bold")
ax.text(-0.2, 1.9, "each flag checked against GSM8K-Platinum, the human re-checked version of GSM8K. Who was actually wrong?",
        fontsize=9.5, color="#5b6470")
ax.text(-0.2, -yi - 1.0, "66 of 74 flags (89%): the answer key was the problem, usually our matching script, sometimes the dataset itself",
        fontsize=11, fontweight="bold", color=C["amber"])
ax.text(-0.2, -yi - 1.8, "judges measured against those labels are being mismeasured; this check needs no human labels and almost no compute",
        fontsize=9.5, color="#5b6470")
save(fig, "f2_miner")

# ---- f3 judge skill vs size (natural errors, cleaned labels) ----
fig, ax = plt.subplots(figsize=(7.8, 3.9))
names = ["0.5B", "1.5B", "3B", "7B", "14B", "GPT-5.2", "Opus 4.8"]
auc = [0.781, 0.898, 0.923, 0.962, 0.961, 0.974, 0.993]
ax.plot(range(7), auc, "-o", color=C["blue"], lw=2, ms=6)
for i, v in enumerate(auc): ax.text(i, v + 0.008, f"{v:.2f}", ha="center", fontsize=8.5)
ax.set_xticks(range(7)); ax.set_xticklabels(names); ax.set_xlabel("judge")
ax.set_ylabel("AUC: does the judge score wrong below right?")
ax.set_ylim(0.72, 1.03)
ax.set_title("Judging skill grows smoothly with judge size (after the label cleanup): no cliff, no special size", fontsize=10)
save(fig, "f3_auc")

# ---- f4 planted false equations: who catches which kind ----
fig, ax = plt.subplots(figsize=(8.6, 3.9))
conds = ["early + blatant", "early + subtle", "late + blatant", "late + subtle"]
data = {"3B judge": [69, 45, 37, 31], "14B judge": [72, 56, 40, 25], "GPT-5.2": [47, 60, 53, 61], "Opus 4.8": [48, 55, 41, 68]}
x = np.arange(4); w = 0.2
for i, (kname, v) in enumerate(data.items()):
    col = [C["purple"], C["blue"], C["green"], C["amber"]][i]
    ax.bar(x + (i - 1.5) * w, v, w, label=kname, color=col)
ax.set_xticks(x); ax.set_xticklabels(conds); ax.set_xlabel("where the false equation sits, and how blatant it is")
ax.set_ylabel("% of planted false equations flagged")
ax.legend(fontsize=8.5, ncol=4, frameon=False)
ax.set_title("Mid-size judges punish the errors that stand out; frontier judges punish the errors\nthat affect the conclusion, and forgive obvious typos", fontsize=9.5)
save(fig, "f4_typos")

# ---- f5 the central figure: hidden-error detection under three conditions ----
fig, ax = plt.subplots(figsize=(8.9, 4.5))
xs = range(4); names5 = ["1.5B", "3B", "7B", "14B"]
gold = [21, 85, 85, 90]; noref = [3, 17, 49, 75]; selfref = [59, 60, 85, 95]
ax.plot(xs, gold, "-o", color=C["green"], lw=2.2, label="shown the correct reference")
ax.plot(xs, noref, "-o", color=C["red"], lw=2.2, label="no reference at all")
ax.plot(xs, selfref, "-o", color=C["purple"], lw=2.2, label="its own answer as reference (separate pass)")
ax.scatter([3.75], [100], color=C["green"], marker="*", s=130)
ax.scatter([3.75], [96], color=C["red"], marker="*", s=130)
ax.text(3.9, 98, "frontier judges:\n~100% in all\nthree conditions", fontsize=8, va="center")
for i in range(4):
    ax.annotate("", xy=(i, gold[i] - 1.5), xytext=(i, noref[i] + 1.5),
                arrowprops=dict(arrowstyle="->", color=C["gray"], lw=1))
ax.text(0.55, 27, "gray arrows = what a reference is\nworth: 68 points of detection at 3B,\n2 points at the frontier", fontsize=8.5, color="#5b6470")
ax.set_xticks(list(xs)); ax.set_xticklabels(names5); ax.set_xlim(-0.3, 4.95)
ax.set_xlabel("judge size (Qwen family)")
ax.set_ylabel("% of hidden-error solutions caught")
ax.legend(fontsize=9, loc="lower right", frameon=False)
ax.set_title("Detection of hidden errors by judge size: a reference lifts the 3B judge from 17% to 85%", fontsize=10)
save(fig, "f5_phase")

# ---- f6 six families ----
fig, ax = plt.subplots(figsize=(8.8, 3.9))
fam = ["Qwen-3B", "Qwen-7B", "Qwen-14B", "Phi-4\n(Microsoft)", "Mistral-7B", "OLMo-13B\n(AI2)", "Llama-3.1-8B\n(Meta)", "Gemma-2-9B\n(Google)"]
ref = [85, 85, 90, 99, 19, 64, 63, 70]; nor = [17, 49, 75, 73, 4, 4, 49, 46]
x = np.arange(8); w = 0.38
ax.bar(x - w/2, ref, w, color=C["green"], label="with reference")
ax.bar(x + w/2, nor, w, color=C["red"], label="without reference")
ax.set_xticks(x); ax.set_xticklabels(fam, fontsize=8)
ax.set_ylabel("% of hidden errors caught")
ax.legend(frameon=False, fontsize=9)
ax.set_title("The reference boost appears in every model family tested (6 of 6)", fontsize=10)
save(fig, "f6_families")

# ---- f7 ProcessBench external ----
fig, ax = plt.subplots(figsize=(7.8, 3.9))
names7 = ["0.5B", "1.5B", "3B", "7B", "14B", "Opus 4.8"]
f1v = [0, 0, 36.9, 30.2, 63.2, 88.1]
ax.plot(range(6), f1v, "-o", color=C["blue"], lw=2, label="standard prompt")
ax.scatter([3, 4], [38.0, 70.4], color=C["purple"], marker="^", s=70, zorder=3, label="forced solve-first, then judge")
ax.set_xticks(range(6)); ax.set_xticklabels(names7); ax.set_xlabel("judge")
ax.set_ylabel("F1 at finding the first wrong step")
ax.legend(frameon=False, fontsize=9)
ax.set_title("External check on a public, human-labeled benchmark (ProcessBench): the same size trend,\nand forced solve-first helps once the judge is big enough to comply", fontsize=9.5)
save(fig, "f7_processbench")

# ---- f8 RB2: the same reference helps on one task type, hurts on the other (14B judge) ----
fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.0))
arms = ["no\nreference", "own answer\nas reference", "weak model's\nanswer", "mid model's\nanswer"]
math_acc = [75, 84, 73, 82]; ties_acc = [99, 91, 92, 92]
cols8 = [C["gray"], C["purple"], C["amber"], C["blue"]]
a.bar(range(4), math_acc, color=cols8, width=0.6)
a.set_xticks(range(4)); a.set_xticklabels(arms, fontsize=8)
a.set_ylim(60, 100); a.set_ylabel("% of pairs judged correctly")
a.set_title("Math (one right answer):\ngood references help, bad ones do not hurt", fontsize=9.5)
for i, v in enumerate(math_acc): a.text(i, v + 0.6, str(v), ha="center", fontsize=9)
b.bar(range(4), ties_acc, color=cols8, width=0.6)
b.set_xticks(range(4)); b.set_xticklabels(arms, fontsize=8)
b.set_ylim(60, 102)
b.set_title("Many-valid-answers questions:\nevery reference hurts (p<=.0005)", fontsize=9.5)
for i, v in enumerate(ties_acc): b.text(i, v + 0.6, str(v), ha="center", fontsize=9)
fig.suptitle("Judge = Qwen-14B. The same reference helps on one task type and hurts on the other", fontsize=10.5, y=1.02)
save(fig, "f8_rb2")

# ---- f9 order-flip rate ----
fig, ax = plt.subplots(figsize=(8.2, 3.9))
names9 = ["0.5B", "1.5B", "3B", "7B", "14B"]
subs = {"Ties (easy pairs)": ([71, 51, 16, 6, 2], C["green"]),
        "Focus": ([95, 74, 47, 14, 17], C["blue"]),
        "Math": ([np.nan, np.nan, 49, 46, 24], C["purple"]),
        "Precise instruction-following": ([85, 82, 60, 46, 37], C["red"])}
for lab, (v, col) in subs.items():
    ax.plot(range(5), v, "-o", color=col, lw=2, label=lab)
ax.set_xticks(range(5)); ax.set_xticklabels(names9); ax.set_xlabel("judge size (Qwen family)")
ax.set_ylabel("% of verdicts that flip when the order swaps")
ax.legend(fontsize=8.5, frameon=False)
ax.set_title("How often the verdict changes when the two responses swap places:\nit falls with judge size, except where the task defeats every judge", fontsize=9.5)
save(fig, "f9_flips")
print("all figures done")
