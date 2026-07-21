# Cross-family generalization figures, rebuilt clean and consistent with the appendix tables.
# Uses the SAME authoritative loader as scripts/analyze_model_level.py (full 17-model set per dataset,
# boxed accuracy recomputed with the fixed scorer), never the incomplete slim scores_all.jsonl.
#   fig6_cross_family.png : boundary-map lollipop. One row per dataset, x = cross-family Spearman
#                           rho(mean TFA, mean task success). Ordered so "holds -> breaks" reads at a glance.
#   fig7_mechanism.png    : two uncluttered panels (MATH-500 holds, GSM8K scrambles) showing within-family
#                           ladders connected in model-size order, so the reader sees WHY.
import json, re, collections, numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analyze_model_level import load_permodel, fam

OUT = "paper/figs"
A = "runs/all/{0}__*.jsonl"
MATH_ANCHORS = [
    ("MATH-500", ["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl", "runs/wsv/math500__*.jsonl", A.format("math500")], "math500", "hard math"),
    ("MATH (full)", ["runs/mathfull/*.judged.jsonl", A.format("math-full")], "math500", "hard math"),
    ("Putnam-AXIOM", ["runs/putnam/*.judged.jsonl", "runs/d2/putnam-axiom__*.judged.jsonl", "runs/wsv/putnam-axiom__*.jsonl", A.format("putnam-axiom")], "putnam", "hard math"),
    ("Putnam-Variations", ["runs/putnamvar/*.judged.jsonl", A.format("putnam-axiom-var")], "putnam", "hard math"),
    ("GSM8K", ["runs/gsm8k/*.judged.jsonl", "runs/d2/gsm8k__*.judged.jsonl", A.format("gsm8k")], "gsm8k", "saturated"),
    ("GSM8K-Platinum", ["runs/gsm8kp/*.judged.jsonl", A.format("gsm8k-platinum")], "gsm8k", "saturated"),
]

def size(m):
    m = m.lower()
    if "ministral-8b" in m: return 8.0
    if "mistral-small" in m: return 22.0
    if "phi-3.5" in m or "mini" in m: return 3.8
    if "phi-3-medium" in m: return 14.0
    if "phi-4" in m: return 14.7
    z = re.search(r"(\d+\.?\d*)b", m)
    return float(z.group(1)) if z else 99.0

COL = {"Qwen2.5": "#5c5c5c", "Mistral": "#C44E52", "Phi": "#4C72B0", "OLMo": "#55A868",
       "Qwen-Math": "#8452b0", "DeepSeek-Math": "#b07a1e", "Mathstral": "#1ba090"}
RCOL = {"hard math": "#2f8f4e", "saturated": "#d98c1f", "code": "#7d54c9"}

# ---- gather per-model (tfa, success) --------------------------------------
# Recomputing boxed accuracy is slow (Math-Verify), so cache the per-model aggregates; delete
# paper/figs/.permodel_cache.json to force a rebuild after new runs land.
import os
CACHE = "paper/figs/.permodel_cache.json"
permodel = {}                                   # label -> {model: dict(tfa, acc, fam, ...)}
regime = {}
for label, globs, dk, reg in MATH_ANCHORS:
    regime[label] = reg
if os.path.exists(CACHE):
    permodel = json.load(open(CACHE))
else:
    for label, globs, dk, reg in MATH_ANCHORS:
        permodel[label] = load_permodel(globs, dk)

# Omni-MATH (7 models) and HumanEval (8 models) from the complete slim files.
def load_slim(path, key):
    by = collections.defaultdict(list)
    for l in open(path):
        r = json.loads(l)
        if "Qwen2.5-32B" in r["model"]: continue
        by[r["model"]].append((r["tfa_argmax"], int(r.get(key) or 0)))
    return {m.split("/")[-1]: dict(fam=fam(m), tfa=float(np.mean([t for t, _ in v])),
                                   acc=float(np.mean([s for _, s in v]))) for m, v in by.items()}
if "Omni-MATH (olympiad)" not in permodel:
    permodel["Omni-MATH (olympiad)"] = load_slim("runs/scores_ws3.jsonl", "cc")
    permodel["HumanEval (code)"] = load_slim("runs/scores_code.jsonl", "code_pass")
    json.dump(permodel, open(CACHE, "w"))
regime["Omni-MATH (olympiad)"] = "hard math"; regime["HumanEval (code)"] = "code"

def rho(pm):
    t = np.array([v["tfa"] for v in pm.values()]); s = np.array([v["acc"] for v in pm.values()])
    return stats.spearmanr(t, s).statistic

def rho_ci(pm, nb=4000):
    # bootstrap the cross-family Spearman by resampling models (the units), 95% percentile CI
    t = np.array([v["tfa"] for v in pm.values()]); s = np.array([v["acc"] for v in pm.values()])
    n = len(t); vals = []
    rng = np.random.default_rng(0)
    for _ in range(nb):
        idx = rng.integers(0, n, n)
        if len(set(t[idx])) < 2: continue
        vals.append(stats.spearmanr(t[idx], s[idx]).statistic)
    return np.nanpercentile(vals, 2.5), np.nanpercentile(vals, 97.5)

# ---- Figure 6: boundary-map lollipop --------------------------------------
stat = sorted([(lab, rho(pm), len(pm), rho_ci(pm)) for lab, pm in permodel.items()], key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9.8, 5.4))
ys = np.arange(len(stat))
for y, (lab, r, n, ci) in zip(ys, stat):
    c = RCOL[regime[lab]]
    ax.plot([0, r], [y, y], color=c, lw=2.6, zorder=2, solid_capstyle="round")
    ax.plot([ci[0], ci[1]], [y, y], color=c, lw=1.0, alpha=0.55, zorder=2)   # 95% bootstrap CI
    for b in ci: ax.plot([b, b], [y - 0.13, y + 0.13], color=c, lw=1.0, alpha=0.55, zorder=2)
    ax.scatter([r], [y], s=160, color=c, zorder=3, edgecolors="white", linewidths=1.3)
    ax.text(ci[1] + 0.04, y, f"{r:+.2f}", va="center", ha="left", fontsize=10, color=c, fontweight="bold")
ax.axvline(0, color="#333", lw=1.0, zorder=1)
ax.set_yticks(ys); ax.set_yticklabels([f"{lab}  (n={n})" for lab, _, n, _ in stat], fontsize=10.5)
ax.set_xlabel("cross-family Spearman ρ(mean TFA, mean task success), with 95% bootstrap CI over models", fontsize=10.5)
ax.set_xlim(-0.85, 1.15); ax.set_ylim(-0.6, len(stat) - 0.4)
ax.grid(axis="x", alpha=0.25)
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
ax.tick_params(left=False)
handles = [plt.Line2D([0], [0], color=RCOL[k], lw=3, label=k) for k in ("hard math", "saturated", "code")]
ax.legend(handles=handles, loc="lower right", fontsize=9.5, frameon=False, title="reference type")
ax.set_title("Judge-free TFA ranks models by quality only on hard, constrained references\n"
             "Strong on hard math, it fades as accuracy saturates, is weak on code, and turns negative on saturated grade-school math",
             fontsize=11.5, loc="left")
fig.tight_layout()
fig.savefig(f"{OUT}/fig6_cross_family.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE fig6_cross_family.png")
for lab, r, n, ci in reversed(stat): print(f"   {lab:24s} rho={r:+.2f} [{ci[0]:+.2f},{ci[1]:+.2f}] n={n}")

# ---- Figure 7: mechanism (MATH-500 holds vs GSM8K scrambles) --------------
fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.7))
for ax, lab, note in [(axes[0], "MATH-500", "holds: better models predict the reference better"),
                      (axes[1], "GSM8K", "scrambles: each family sits at its own TFA offset")]:
    pm = permodel[lab]
    byfam = collections.defaultdict(list)
    for m, v in pm.items(): byfam[v["fam"]].append((size(m), v["tfa"], v["acc"]))
    r = rho(pm)
    for f, pts in sorted(byfam.items()):
        pts = sorted(pts); c = COL.get(f, "#333")
        xs = [p[1] for p in pts]; yv = [p[2] for p in pts]
        if len(pts) >= 2:
            ax.plot(xs, yv, "-o", color=c, ms=7, lw=2.0, label=f, zorder=3)
            ax.annotate(f, (xs[-1], yv[-1]), fontsize=8.5, color=c, fontweight="bold",
                        xytext=(4, 4), textcoords="offset points")
        else:
            ax.scatter(xs, yv, color=c, marker="*", s=300, edgecolors="black", linewidths=0.6, zorder=4)
            ax.annotate(f.replace("2.5", ""), (xs[0], yv[0]), fontsize=7.5, color=c,
                        xytext=(5, -10), textcoords="offset points")
    ax.set_title(f"{lab}   cross-family ρ = {r:+.2f}\n{note}", fontsize=11.5)
    ax.set_xlabel("mean TFA on the gold reference", fontsize=11)
    ax.set_ylabel("accuracy", fontsize=11)
    ax.grid(alpha=0.3)
fig.suptitle("Why ranking holds on hard math and breaks on saturated math. Each line is one family's size ladder "
             "(small to large model).\nOn MATH stronger models predict the gold better, so TFA tracks accuracy. On "
             "GSM8K the reference is short and stylized: families separate by style and Phi even inverts.",
             fontsize=11.5, y=1.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig7_mechanism.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE fig7_mechanism.png")
