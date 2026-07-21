# Human-facing figures + summary.json for Workstream A (TFA vs judge across NL-math datasets).
# Produces: paper/figs/*.png and paper/summary.json. Self-contained analysis (no external analyze import
# beyond tfa.* scoring helpers so the numbers match the journal exactly).
import json, glob, collections, os
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent
from tfa.analyze import bootstrap_partial, bootstrap_corr

OUT = "paper/figs"; os.makedirs(OUT, exist_ok=True); os.makedirs("paper", exist_ok=True)

DSETS = [
    ("MATH-500",   "runs/math500/*.judged.jsonl",   "math500"),
    ("MATH-full",  "runs/mathfull/*.judged.jsonl",  "math500"),
    ("GSM8K",      "runs/gsm8k/*.judged.jsonl",     "gsm8k"),
    ("GSM8K-Plat", "runs/gsm8kp/*.judged.jsonl",    "gsm8k"),
    ("Putnam",     "runs/putnam/*.judged.jsonl",    "putnam"),
    ("Putnam-Var", "runs/putnamvar/*.judged.jsonl", "putnam"),
]
# Common 5-model ladder across ALL datasets (32B was only run on MATH-500; drop it for
# apples-to-apples cross-dataset comparison of TFA range / model-level rho).
ORDER = ["Qwen2.5-0.5B-Instruct","Qwen2.5-1.5B-Instruct","Qwen2.5-3B-Instruct",
         "Qwen2.5-7B-Instruct","Qwen2.5-14B-Instruct"]
LADDER5 = set(ORDER)

def gold_ans(r, ds):
    if ds == "gsm8k": return r["gold_solution"].split("####")[-1].strip().replace(",", "")
    return extract_boxed(r["gold_solution"])

def load(glob_, ds):
    R = [json.loads(l) for fp in glob.glob(glob_) for l in open(fp)]
    R = [r for r in R if r.get("judge_score") is not None]
    for r in R:
        r["cc"] = int(answers_equivalent(extract_final_answer(r["free_gen"], ds), gold_ans(r, ds)))
    return R

def resid(y, *ctrl):
    yr = stats.rankdata(y)
    X = np.column_stack([np.ones(len(y))] + [stats.rankdata(z) for z in ctrl])
    b, *_ = np.linalg.lstsq(X, yr, rcond=None)
    return yr - X @ b

def mkey(m): return m.split("/")[-1]

S = {}
for ds, g, dskey in DSETS:
    R = load(g, dskey)
    R = [r for r in R if mkey(r["model"]) in LADDER5]  # restrict to common 5-model ladder
    if not R: continue
    by = collections.defaultdict(list)
    for r in R: by[mkey(r["model"])].append(r)
    models = [m for m in ORDER if m in by] + [m for m in by if m not in ORDER]
    mt = np.array([np.mean([x["tfa_argmax"] for x in by[m]]) for m in models])
    ma = np.array([np.mean([x["cc"] for x in by[m]]) for m in models])
    mj = np.array([np.mean([x["judge_score"] for x in by[m]]) for m in models])
    t = np.array([r["tfa_argmax"] for r in R]); j = np.array([r["judge_score"] for r in R])
    c = np.array([r["cc"] for r in R]); gl = np.array([r["n_gold_tokens"] for r in R])
    pc = bootstrap_partial(t, j, c, n_boot=3000)
    plen = stats.spearmanr(resid(t, c, gl), resid(j, c, gl)).statistic
    cm, wm = c == 1, c == 0
    S[ds] = dict(n=len(R), acc=float(ma.mean()), tfa_lo=float(mt.min()), tfa_hi=float(mt.max()),
                 ml_acc=float(stats.spearmanr(mt, ma).statistic), ml_jdg=float(stats.spearmanr(mt, mj).statistic),
                 il=float(pc.rho), il_lo=float(pc.lo), il_hi=float(pc.hi), il_len=float(plen),
                 wcorr=float(bootstrap_corr(t[cm], j[cm]).rho) if cm.sum() > 5 else None,
                 wwrong=float(bootstrap_corr(t[wm], j[wm]).rho) if wm.sum() > 5 else None,
                 ncorr=int(cm.sum()),
                 models=models, mt=mt.tolist(), ma=ma.tolist(), mj=mj.tolist())

json.dump(S, open("paper/summary.json", "w"), indent=2)
present = [d for d, _, _ in DSETS if d in S]
COL = {"MATH-500":"#4C72B0","MATH-full":"#8DA0CB","GSM8K":"#55A868","GSM8K-Plat":"#A6D854",
       "Putnam":"#C44E52","Putnam-Var":"#E07B7B"}

# ---- Fig 1: headline — item-level partial rho with CI, grouped by dataset family ----
fam_order = ["MATH-500", "MATH-full", "GSM8K", "GSM8K-Plat", "Putnam-Var", "Putnam"]
order = [d for d in fam_order if d in present]
fig, ax = plt.subplots(figsize=(8.5, 4.4))
xs = np.arange(len(order))
ys = [S[d]["il"] for d in order]
lo = [S[d]["il"] - S[d]["il_lo"] for d in order]; hi = [S[d]["il_hi"] - S[d]["il"] for d in order]
ax.axhline(0, color="gray", lw=1, ls="--")
ax.errorbar(xs, ys, yerr=[lo, hi], fmt="none", capsize=5, lw=2, ecolor="#333", zorder=3)
for x, d in zip(xs, order):
    ax.plot(x, S[d]["il"], "o", ms=11, color=COL[d], zorder=4)
# family band separators
for xb in [1.5, 3.5]:
    ax.axvline(xb, color="#ccc", lw=1, ls=":")
for xc, lab in [(0.5, "MATH  (≈0)"), (2.5, "GSM8K  (small +)"), (4.5, "Putnam  (large +)")]:
    ax.text(xc, ax.get_ylim()[1] * 0.96 if False else 0.26, lab, ha="center", fontsize=9, color="#555")
ax.set_xticks(xs); ax.set_xticklabels([f"{d}\n(acc={S[d]['acc']:.2f})" for d in order], fontsize=8.5)
ax.set_ylabel("item-level partial ρ(TFA, judge | correct)")
ax.set_ylim(-0.16, 0.30)
ax.set_title("Per-item TFA→judge signal by family: ~0 on MATH, small on GSM8K, largest on Putnam", fontsize=11)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2_difficulty_gradient.png", dpi=150); plt.close(fig)

# ---- Fig 2: model-level scatter mean-TFA vs accuracy across ladder ----
fig, ax = plt.subplots(figsize=(7, 5))
for d in present:
    ax.plot(S[d]["mt"], S[d]["ma"], "-o", color=COL[d], label=f"{d} (ρ={S[d]['ml_acc']:+.2f})", ms=6)
ax.set_xlabel("mean TFA (argmax gold-token match)"); ax.set_ylabel("free-gen accuracy")
ax.set_title("Model-level: mean-TFA tracks accuracy across the ladder (ρ = +0.6 to +1.0)")
ax.legend(fontsize=8, loc="lower right"); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1_model_level.png", dpi=150); plt.close(fig)

# ---- Fig 3: TFA saturation — range bars vs accuracy ----
fig, ax = plt.subplots(figsize=(8, 4))
order2 = sorted(present, key=lambda d: S[d]["acc"])
xs = np.arange(len(order2))
for x, d in zip(xs, order2):
    ax.plot([x, x], [S[d]["tfa_lo"], S[d]["tfa_hi"]], color=COL[d], lw=8, solid_capstyle="round")
    ax.text(x, S[d]["tfa_hi"] + 0.005, f"{S[d]['tfa_hi']-S[d]['tfa_lo']:.02f}", ha="center", fontsize=8)
ax.set_xticks(xs); ax.set_xticklabels([f"{d}\n(acc={S[d]['acc']:.2f})" for d in order2], fontsize=9)
ax.set_ylabel("mean-TFA range across Qwen ladder")
ax.set_title("TFA compresses (saturates) on easy data, spreads out on hard data")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(f"{OUT}/fig3_saturation.png", dpi=150); plt.close(fig)

# ---- Fig 4: robustness comparisons (label-noise + contamination) ----
pairs = [("GSM8K", "GSM8K-Plat", "Label-noise\n(clean labels)"),
         ("Putnam", "Putnam-Var", "Contamination\n(functional variants)")]
pairs = [(a, b, lbl) for a, b, lbl in pairs if a in S and b in S]
if pairs:
    fig, ax = plt.subplots(figsize=(7.5, 4))
    xs = []; lbls = []; i = 0
    for a, b, lbl in pairs:
        for d, off in [(a, 0), (b, 1)]:
            x = i + off * 0.9
            e_lo = S[d]["il"] - S[d]["il_lo"]; e_hi = S[d]["il_hi"] - S[d]["il"]
            ax.bar(x, S[d]["il"], width=0.8, color=COL[d], yerr=[[e_lo], [e_hi]], capsize=4)
            ax.text(x, S[d]["il"] + e_hi + 0.006, d.split("-")[-1] if "-" in d else d, ha="center", fontsize=8)
            xs.append(x)
        ax.text(i + 0.45, -0.03, lbl, ha="center", fontsize=9)
        i += 2.4
    ax.axhline(0, color="gray", lw=1)
    ax.set_ylabel("item-level partial ρ(TFA, judge | correct)")
    ax.set_title("Item signal survives clean-label & contamination controls (attenuated, still >0)")
    ax.set_xticks([]); ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig4_robustness.png", dpi=150); plt.close(fig)

print("WROTE", sorted(glob.glob(f"{OUT}/*.png")))
print("DATASETS", present)
