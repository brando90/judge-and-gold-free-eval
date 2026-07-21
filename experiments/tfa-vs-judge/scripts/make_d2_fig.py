# Figure 6 (cross-family generalization): mean-TFA vs task success across the family ladders, on a
# five-panel boundary spectrum ordered hard -> saturated -> code. Each family with >=2 models is drawn
# as a connected line so the within-family trend is visible; families with one model (math-specialized,
# and the single non-Qwen models on Omni-MATH / HumanEval) are stars. The TFA-success line holds on the
# hard, constrained references (Putnam, MATH-500, Omni-MATH), scrambles on saturated GSM8K, and washes
# out on code (HumanEval), where one gold reference cannot represent many valid programs.
import json, glob, collections, numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent

OUT = "paper/figs"

def fam(m):
    m = m.lower()
    if "qwen2.5-math" in m: return "Qwen2.5-Math"
    if "deepseek-math" in m: return "DeepSeek-Math"
    if "mathstral" in m: return "Mathstral"
    if "qwen2.5" in m: return "Qwen2.5"
    if "mistral" in m: return "Mistral"
    if "phi" in m: return "Phi"
    if "olmo" in m: return "OLMo"
    return "other"

COL = {"Qwen2.5": "#777777", "Mistral": "#C44E52", "Phi": "#4C72B0", "OLMo": "#55A868",
       "Qwen2.5-Math": "#8452b0", "DeepSeek-Math": "#b07a1e", "Mathstral": "#1ba090"}

def gold(r, dk):
    return r["gold_solution"].split("####")[-1].strip().replace(",", "") if dk == "gsm8k" else extract_boxed(r["gold_solution"])

# mode: "math" recomputes correctness from free_gen; "field:<key>" reads a stored per-item 0/1 column.
ANCHORS = [
    ("Putnam", ["runs/putnam/*.judged.jsonl", "runs/d2/putnam-axiom__*.judged.jsonl",
                "runs/wsv/putnam-axiom__*.jsonl", "runs/all/putnam-axiom__*.jsonl"], "putnam", "math", "accuracy"),
    ("MATH-500", ["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl",
                  "runs/wsv/math500__*.jsonl", "runs/all/math500__*.jsonl"], "math500", "math", "accuracy"),
    ("Omni-MATH (olympiad)", ["runs/ws3/*.jsonl", "runs/*/omni-math__*.jsonl"], "omni", "field:boxed_correct", "accuracy"),
    ("GSM8K", ["runs/gsm8k/*.judged.jsonl", "runs/d2/gsm8k__*.judged.jsonl", "runs/all/gsm8k__*.jsonl"], "gsm8k", "math", "accuracy"),
    ("HumanEval (code)", ["runs/code/humaneval__*.jsonl"], "code", "field:code_pass", "pass@1"),
]

fig, axes = plt.subplots(1, 5, figsize=(24, 4.7))
for ax, (ds, globs, dk, mode, ylab) in zip(axes, ANCHORS):
    by = {}
    for g in globs:
        for f in sorted(glob.glob(g)):
            R = [json.loads(l) for l in open(f)]
            if not R or "Qwen2.5-32B" in R[0]["model"]: continue   # keep the 5-model Qwen ladder
            m = R[0]["model"].split("/")[-1]
            if m in by: continue                                   # first glob wins (avoid dup files)
            if mode == "math":
                cc = [int(answers_equivalent(extract_final_answer(r["free_gen"], dk), gold(r, dk) or "")) for r in R]
            else:
                key = mode.split(":")[1]
                cc = [int(r.get(key) or 0) for r in R]
            by[m] = (fam(R[0]["model"]), float(np.mean([r["tfa_argmax"] for r in R])), float(np.mean(cc)))
    mt = np.array([v[1] for v in by.values()]); ma = np.array([v[2] for v in by.values()])
    rho = stats.spearmanr(mt, ma).statistic
    byfam = collections.defaultdict(list)
    for m, v in by.items(): byfam[v[0]].append((v[1], v[2]))
    for f, pts in sorted(byfam.items()):
        pts = sorted(pts); c = COL.get(f, "#333")
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if len(pts) >= 2:
            ax.plot(xs, ys, "-o", color=c, ms=6, lw=1.8, label=f, zorder=3)
        else:
            ax.scatter(xs, ys, c=c, marker="*", s=240, edgecolors="black", linewidths=0.5, label=f, zorder=4)
    ax.set_title(f"{ds}\ncross-family ρ = {rho:+.2f}  (n={len(by)})", fontsize=10.5)
    ax.set_xlabel("mean TFA"); ax.set_ylabel(ylab)
    ax.grid(alpha=0.3)
    if ds == "Putnam": ax.legend(fontsize=7.5, loc="best", ncol=2)
fig.suptitle("Cross-family model ranking along the difficulty-to-code spectrum: TFA ranks by task success on "
             "hard, constrained references (Putnam, MATH, Omni-MATH),\nscrambles on saturated GSM8K, and washes "
             "out on code (HumanEval). Lines are within-family ladders; stars are single-model families.",
             fontsize=12, y=1.06)
fig.tight_layout()
fig.savefig(f"{OUT}/fig6_cross_family.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE", f"{OUT}/fig6_cross_family.png")
