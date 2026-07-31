# Figures that back two claims which so far had only numbers:
#   fig8_agentic.png   : the SWE-bench within-family (+1.00) vs cross-family (+0.00) collapse, with the
#                        CodeLlama high-TFA/low-capability outlier visible.
#   fig9_mechanism.png : the variance decomposition (per-item TFA is 89-96% reference-predictability
#                        nuisance), the quantitative backbone of the "style not quality" mechanism.
import json, glob, re, collections, numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "paper/figs"

# ---------- Figure 8: agentic within vs cross family ----------
rows = [json.loads(l) for l in open("runs/scores_crossfam_swe.jsonl")]
FCOL = {"Qwen-Coder": "#1a1a1a", "DeepSeek-Coder": "#b07a1e", "CodeLlama": "#C44E52", "StarCoder2": "#4C72B0"}
def sz(m):
    z = re.search(r"(\d+\.?\d*)[bB]", m); return float(z.group(1)) if z else 0

fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 5.4))

# left: within Qwen-Coder ladder
q = sorted([r for r in rows if r["family"] == "Qwen-Coder"], key=lambda r: r["humaneval_pass1"])
qx = [r["humaneval_pass1"] for r in q]; qy = [r["patch_tfa_added"] for r in q]
rho_in = stats.spearmanr(qx, qy).statistic
axL.plot(qx, qy, "-o", color=FCOL["Qwen-Coder"], ms=9, lw=2.4, zorder=3)
for r in q:
    axL.annotate(f"{sz(r['model']):g}B", (r["humaneval_pass1"], r["patch_tfa_added"]),
                 fontsize=9, color="#1a1a1a", xytext=(6, -3), textcoords="offset points")
axL.set_title(f"Within one coder family (Qwen2.5-Coder)\npatch-TFA tracks skill: Spearman = {rho_in:+.2f}", fontsize=11.5)
axL.set_xlabel("HumanEval pass@1 (capability)", fontsize=10.5); axL.set_ylabel("mean patch-TFA (added lines)", fontsize=10.5)
axL.grid(alpha=0.3)

# right: cross-family scatter
ax_all = rows
cx = [r["humaneval_pass1"] for r in ax_all]; cy = [r["patch_tfa_added"] for r in ax_all]
rho_cross = stats.spearmanr(cx, cy).statistic
b = np.polyfit(cx, cy, 1); xr = np.linspace(min(cx), max(cx), 2)
axR.plot(xr, np.polyval(b, xr), color="#bbbbbb", ls=":", lw=1.6, zorder=1)
seen = set()
for r in ax_all:
    f = r["family"]; c = FCOL.get(f, "#333")
    axR.scatter(r["humaneval_pass1"], r["patch_tfa_added"], s=110, color=c, zorder=3,
                edgecolors="white", linewidths=1.0, label=f if f not in seen else None)
    seen.add(f)
    if f == "CodeLlama":
        axR.annotate(f"CodeLlama-{sz(r['model']):g}B", (r["humaneval_pass1"], r["patch_tfa_added"]),
                     fontsize=8.5, color=c, fontweight="bold", xytext=(6, 2), textcoords="offset points")
axR.set_title(f"Across four coder families\nno relationship: Spearman = {rho_cross:+.2f}", fontsize=11.5)
axR.set_xlabel("HumanEval pass@1 (capability)", fontsize=10.5); axR.set_ylabel("mean patch-TFA (added lines)", fontsize=10.5)
axR.legend(fontsize=8.5, loc="lower left", frameon=False); axR.grid(alpha=0.3)
fig.suptitle("Teacher-forcing the gold code patch ranks models within a family but not across families. "
             "CodeLlama\nreproduces the gold-patch style best (high TFA) while writing the worst code (low pass@1).",
             fontsize=11.5, y=1.02)
fig.tight_layout(); fig.savefig(f"{OUT}/fig8_agentic.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE fig8_agentic.png  within=%.2f cross=%.2f" % (rho_in, rho_cross))

# ---------- Figure 9: variance decomposition (mechanism) ----------
# per math dataset, share of within-model per-item TFA variance explained by the model-invariant item effect
A = "runs/all/{0}__*.jsonl"
LAB = [("MATH-500", "math500"), ("MATH-full", "math-full"), ("GSM8K", "gsm8k"),
       ("GSM8K-Plat", "gsm8k-platinum"), ("Putnam", "putnam-axiom")]
by = collections.defaultdict(lambda: collections.defaultdict(dict))  # ds -> model -> pid -> tfa
for l in open("runs/scores_all.jsonl"):
    r = json.loads(l); m = r["model"]
    if "Qwen2.5-" in m and "Math" not in m and "32B" not in m:
        by[r["dataset"]][m.split("/")[-1]][r["problem_id"]] = r["tfa_argmax"]
labels, nui = [], []
for lab, dk in LAB:
    d = by.get(dk, {})
    if len(d) < 3: continue
    models = list(d); pids = set(d[models[0]])
    for m in models[1:]: pids &= set(d[m])
    pids = sorted(pids)
    T = np.array([[d[m][p] for p in pids] for m in models])
    D = T - T.mean(axis=1, keepdims=True); bvec = D.mean(axis=0)
    frac = np.sum((np.ones((len(models), 1)) * bvec) ** 2) / np.sum(D ** 2)
    labels.append(f"{lab}\n(n={len(pids)})"); nui.append(100 * frac)

fig, ax = plt.subplots(figsize=(8.2, 4.8))
xs = np.arange(len(labels)); rem = [100 - v for v in nui]
ax.bar(xs, nui, color="#d98c1f", label="reference-predictability nuisance (same for every model)")
ax.bar(xs, rem, bottom=nui, color="#2f8f4e", label="competence + noise (what a grader needs)")
for x, v in zip(xs, nui):
    ax.text(x, v - 6, f"{v:.0f}%", ha="center", color="white", fontsize=10, fontweight="bold")
    ax.text(x, v + (100 - v) / 2 - 1, f"{100-v:.0f}%", ha="center", color="white", fontsize=9)
ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("share of within-model per-item TFA variance (%)", fontsize=10.5)
ax.set_ylim(0, 100); ax.legend(fontsize=9, loc="lower center", frameon=False)
ax.set_title("Per-item TFA is 89 to 96 percent a reference-predictability nuisance that is identical across models.\n"
             "It cancels when averaged over items (so model ranking works) but buries competence per item (so grading fails).",
             fontsize=10.8)
fig.tight_layout(); fig.savefig(f"{OUT}/fig9_mechanism.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE fig9_mechanism.png  nuisance%%:", [f"{v:.0f}" for v in nui])

# ---------- Figure 10: reconciliation with the original TFA paper's 0.66 / 0.52 ----------
# Our model-level TFA-vs-accuracy correlation under four metrics x two model sets, against the numbers the
# Putnam-AXIOM paper reports. Shows their 0.66 (MATH) / 0.52 (Putnam) fall out of matching metric (Kendall)
# and model set (whether the math-specialized outliers are included). Values from the committed appendix table.
MET = ["Pearson", "Spearman", "Kendall", "ICC"]
DATA = {
    "MATH-500": dict(all=[0.54, 0.55, 0.38, 0.56], drop=[0.77, 0.86, 0.64, 0.79], theirs=[("their 0.66", 0.66)]),
    "Putnam":   dict(all=[0.68, 0.68, 0.51, 0.70], drop=[0.85, 0.88, 0.71, 0.86], theirs=[("their 0.52", 0.52), ("0.62 no-outliers", 0.62)]),
}
fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.3))
for ax, (ds, d) in zip(axes, DATA.items()):
    y = np.arange(len(MET))
    ax.scatter(d["all"], y, s=120, color="#C44E52", zorder=3, label="all models (incl. math-specialized)")
    ax.scatter(d["drop"], y, s=120, color="#2f8f4e", zorder=3, label="general families only")
    for yi, a, b in zip(y, d["all"], d["drop"]):
        ax.plot([a, b], [yi, yi], color="#bbb", lw=1.5, zorder=1)
    for lab, v in d["theirs"]:
        ax.axvline(v, color="#333", ls="--", lw=1.2)
        ax.text(v, len(MET) - 0.35, lab, rotation=90, va="top", ha="right", fontsize=8.5, color="#333")
    ax.set_yticks(y); ax.set_yticklabels(MET, fontsize=10)
    ax.set_xlim(0.2, 1.0); ax.set_xlabel("model-level correlation (TFA vs accuracy)", fontsize=10)
    ax.set_title(ds, fontsize=11.5); ax.grid(axis="x", alpha=0.3)
    if ds == "MATH-500": ax.legend(fontsize=8.5, loc="lower right", frameon=False)
fig.suptitle("Reconciling the original TFA paper's headline 0.66 (MATH) and 0.52 (Putnam): they fall out once you\n"
             "match the correlation metric (Kendall, honest for a handful of models) and the model set (math-specialized outliers).",
             fontsize=11, y=1.03)
fig.tight_layout(); fig.savefig(f"{OUT}/fig10_reconciliation.png", dpi=150, bbox_inches="tight"); plt.close(fig)
print("WROTE fig10_reconciliation.png")
