# Figures for the oversight story deck + paper. All numbers from the verified run record
# (docs/oversight-log.md); every value survived adjudication/controls.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, os

os.makedirs("paper/figs_oversight", exist_ok=True)
C = dict(blue="#2b5c8a", green="#2f8f4e", amber="#c07d15", purple="#7d54c9", red="#c44e52", gray="#8a8f98")
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

def save(fig, name):
    fig.tight_layout(); fig.savefig(f"paper/figs_oversight/{name}.png", dpi=160); plt.close(fig)
    print("wrote", name)

# ---- f1 the mirage: the detection hierarchy and its dissolution ----
fig, (a, b) = plt.subplots(1, 2, figsize=(9.4, 3.9))
k = [0, 1, 2, 3]; raw = [1.0, 6.5, 60.5, 94.1]
a.bar(k, raw, color=C["red"], width=0.6)
a.set_xticks(k); a.set_xlabel("# small judges fooled by the solution (of 3)")
a.set_ylabel("% frontier judge also fooled")
a.set_title("Looks like a law: small judges predict\nfrontier failure (raw data)", fontsize=10)
for x, v in zip(k, raw): a.text(x, v + 2, f"{v:.0f}%", ha="center", fontsize=9)
cats = ["label was\nwrong\n(71%)", "genuinely wrong,\nfrontier fooled\n(2%)", "genuinely wrong,\nfrontier right\n(27%)"]
b.bar([0, 1, 2], [71, 2, 27], color=[C["amber"], C["red"], C["green"]], width=0.6)
b.set_xticks([0, 1, 2]); b.set_xticklabels(cats, fontsize=8.5)
b.set_ylabel("% of the 'fooling' cases")
b.set_title("After checking every case:\nthe 94% was mostly bad labels", fontsize=10)
save(fig, "f1_mirage")

# ---- f2 the oracle-bug miner, externally validated ----
fig, ax = plt.subplots(figsize=(7.6, 3.6))
labels = ["scorer bug\n(answer = gold)", "bad item\n(removed by Platinum)", "wrong gold\n(Platinum relabeled)", "models wrong\ntogether"]
vals = [53, 11, 2, 8]
cols = [C["amber"], C["amber"], C["amber"], C["green"]]
bars = ax.bar(labels, vals, color=cols, width=0.6)
for r, v in zip(bars, vals): ax.text(r.get_x() + r.get_width()/2, v + 0.6, str(v), ha="center", fontsize=10)
ax.set_ylabel("flagged items (of 74)")
ax.set_title("When cheap models unanimously disagree with the answer key, the key is wrong 89% of the time\n(validated against the human-curated Platinum re-annotation; no frontier model involved)", fontsize=9.5)
save(fig, "f2_miner")

# ---- f3 judge discrimination ladder (natural errors, cleaned labels) ----
fig, ax = plt.subplots(figsize=(7.8, 3.9))
names = ["0.5B", "1.5B", "3B", "7B", "14B", "GPT-5.2", "Opus 4.8"]
auc = [0.781, 0.898, 0.923, 0.962, 0.961, 0.974, 0.993]
ax.plot(range(7), auc, "-o", color=C["blue"], lw=2, ms=6)
for i, v in enumerate(auc): ax.text(i, v + 0.008, f"{v:.2f}", ha="center", fontsize=8.5)
ax.set_xticks(range(7)); ax.set_xticklabels(names)
ax.set_ylabel("AUC: can the judge rank wrong below right?")
ax.set_ylim(0.72, 1.03)
ax.set_title("Judging skill grows smoothly with judge size (after label cleanup): no cliff, no magic size", fontsize=10)
save(fig, "f3_auc")

# ---- f4 typo probe: what different-size judges punish ----
fig, ax = plt.subplots(figsize=(8.6, 3.9))
conds = ["early+gross", "early+small", "late+gross", "late+small"]
data = {"3B judge": [69, 45, 37, 31], "14B judge": [72, 56, 40, 25], "GPT-5.2": [47, 60, 53, 61], "Opus 4.8": [48, 55, 41, 68]}
x = np.arange(4); w = 0.2
for i, (kname, v) in enumerate(data.items()):
    col = [C["purple"], C["blue"], C["green"], C["amber"]][i]
    ax.bar(x + (i - 1.5) * w, v, w, label=kname, color=col)
ax.set_xticks(x); ax.set_xticklabels(conds)
ax.set_ylabel("% of planted typos flagged")
ax.legend(fontsize=8.5, ncol=4, frameon=False)
ax.set_title("Where a false equation is planted changes who catches it: mid-size judges punish the OBVIOUS,\nfrontier judges punish the CONSEQUENTIAL (and forgive obvious typos)", fontsize=9.5)
save(fig, "f4_typos")

# ---- f5 THE central figure: coherent-wrong detection, three conditions ----
fig, ax = plt.subplots(figsize=(8.6, 4.4))
xs = range(4); names5 = ["1.5B", "3B", "7B", "14B"]
gold = [21, 85, 85, 90]; noref = [3, 17, 49, 75]; selfref = [59, 60, 85, 95]
ax.plot(xs, gold, "-o", color=C["green"], lw=2.2, label="shown the correct reference")
ax.plot(xs, noref, "-o", color=C["red"], lw=2.2, label="no reference at all")
ax.plot(xs, selfref, "-o", color=C["purple"], lw=2.2, label="judge's OWN answer as reference")
ax.scatter([3.6], [100], color=C["green"], marker="*", s=140)
ax.scatter([3.6], [98], color=C["red"], marker="*", s=140)
ax.text(3.62, 91, "frontier:\n~100% on all\nthree", fontsize=8)
for i in range(4):
    ax.annotate("", xy=(i, gold[i] - 1.5), xytext=(i, noref[i] + 1.5),
                arrowprops=dict(arrowstyle="->", color=C["gray"], lw=1))
ax.set_xticks(list(xs)); ax.set_xticklabels(names5); ax.set_xlim(-0.3, 4.3)
ax.set_ylabel("% of hidden-error solutions caught")
ax.legend(fontsize=9, loc="lower right", frameon=False)
ax.set_title("The core mechanism: small judges CAN compare, they just lack a reference.\nGive them one (or let them write their own) and detection jumps", fontsize=10)
save(fig, "f5_phase")

# ---- f6 six families ----
fig, ax = plt.subplots(figsize=(8.8, 3.9))
fam = ["Qwen-3B", "Qwen-7B", "Qwen-14B", "phi-4\n(Microsoft)", "Mistral-7B", "OLMo-13B\n(AI2)", "Llama-3.1-8B\n(Meta)", "Gemma-2-9B\n(Google)"]
ref = [85, 85, 90, 99, 19, 64, 63, 70]; nor = [17, 49, 75, 73, 4, 4, 49, 46]
x = np.arange(8); w = 0.38
ax.bar(x - w/2, ref, w, color=C["green"], label="with reference")
ax.bar(x + w/2, nor, w, color=C["red"], label="without reference")
ax.set_xticks(x); ax.set_xticklabels(fam, fontsize=8)
ax.set_ylabel("% hidden errors caught")
ax.legend(frameon=False, fontsize=9)
ax.set_title("The reference boost appears in every model family tested (6 of 6)", fontsize=10)
save(fig, "f6_families")

# ---- f7 ProcessBench external ----
fig, ax = plt.subplots(figsize=(7.8, 3.9))
names7 = ["0.5B", "1.5B", "3B", "7B", "14B", "Opus 4.8"]
f1v = [0, 0, 36.9, 30.2, 63.2, 88.1]
ax.plot(range(6), f1v, "-o", color=C["blue"], lw=2, label="standard prompt")
ax.scatter([3, 4], [38.0, 70.4], color=C["purple"], marker="^", s=70, zorder=3, label='"solve it yourself first" prompt')
ax.set_xticks(range(6)); ax.set_xticklabels(names7)
ax.set_ylabel("ProcessBench F1 (find the first wrong step)")
ax.legend(frameon=False, fontsize=9)
ax.set_title("External check on a public, human-labeled benchmark: same capability story,\nand solve-first helps once the judge is big enough to comply", fontsize=9.5)
save(fig, "f7_processbench")

# ---- f8 RB2 double dissociation (14B judge) ----
fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.0))
arms = ["no\nreference", "own answer\nas reference", "weak model's\nanswer", "mid model's\nanswer"]
math_acc = [75, 84, 73, 82]; ties_acc = [99, 91, 92, 92]
cols8 = [C["gray"], C["purple"], C["amber"], C["blue"]]
a.bar(range(4), math_acc, color=cols8, width=0.6)
a.set_xticks(range(4)); a.set_xticklabels(arms, fontsize=8)
a.set_ylim(60, 100); a.set_ylabel("accuracy %")
a.set_title("MATH (one right answer):\ngood references help, bad ones don't hurt", fontsize=9.5)
for i, v in enumerate(math_acc): a.text(i, v + 0.6, str(v), ha="center", fontsize=9)
b.bar(range(4), ties_acc, color=cols8, width=0.6)
b.set_xticks(range(4)); b.set_xticklabels(arms, fontsize=8)
b.set_ylim(60, 102)
b.set_title("MANY-VALID-ANSWERS questions:\nEVERY reference hurts (p<=.0005)", fontsize=9.5)
for i, v in enumerate(ties_acc): b.text(i, v + 0.6, str(v), ha="center", fontsize=9)
fig.suptitle("The double dissociation (judge = Qwen-14B): the same trick flips sign with the task type", fontsize=10.5, y=1.02)
save(fig, "f8_rb2")

# ---- f9 flip-rate: order-instability as a label-free stress meter ----
fig, ax = plt.subplots(figsize=(8.2, 3.9))
names9 = ["0.5B", "1.5B", "3B", "7B", "14B"]
subs = {"Ties (easy pairs)": ([71, 51, 16, 6, 2], C["green"]),
        "Focus": ([95, 74, 47, 14, 17], C["blue"]),
        "Math": ([np.nan, np.nan, 49, 46, 24], C["purple"]),
        "Precise instruction-following": ([85, 82, 60, 46, 37], C["red"])}
for lab, (v, col) in subs.items():
    ax.plot(range(5), v, "-o", color=col, lw=2, label=lab)
ax.set_xticks(range(5)); ax.set_xticklabels(names9)
ax.set_ylabel("% verdicts that flip when A/B order swaps")
ax.legend(fontsize=8.5, frameon=False)
ax.set_title("A label-free stress meter: how often the verdict changes if you just swap the order.\nIt falls with judge size except where the task outmatches every judge", fontsize=9.5)
save(fig, "f9_flips")
print("all figures done")
