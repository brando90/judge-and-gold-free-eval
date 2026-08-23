# Vector figures for Paper A. Reads papers/analysis/*.json; writes figures/*.pdf.
# Palette validated colorblind-safe: BLUE #4269d0 (certified/verify), ORANGE #c5541a
# (failed/compare), GRAY #6b7280 neutral. Min font 10pt. Run from papers/A-certificate/.
import json, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GRAY, INK = "#4269d0", "#c5541a", "#6b7280", "#1a1a1a"
AN = "../analysis"
os.makedirs("figures", exist_ok=True)
plt.rcParams.update({
    "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 9,
    "axes.edgecolor": "#c8c8c8", "axes.linewidth": 0.8, "pdf.fonttype": 42,
})


def despine(ax, keep=("left", "bottom")):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)


# ------------------------------------------------------------------ fig_h2h.pdf (HERO)
h2h = json.load(open(f"{AN}/head_to_head.json"))
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.4))
for ax, xkey, xlabel, title in (
        (axes[0], "naive_pearson", "raw agreement with human soundness $r$",
         "Naive validation cannot diagnose"),
        (axes[1], "style_partial", "style partial (nuisance loading)",
         "The audit separates by mechanism")):
    for r in h2h:
        b = r.get("bon") or {}
        gap = b.get("excess_gap")
        if gap is None:
            continue
        certified = r["config"].startswith("ref") and "sabotage" not in r["config"]
        col = BLUE if certified else ORANGE
        ax.scatter(r[xkey], gap, s=46, color=col, edgecolors="white", linewidths=0.7, zorder=3)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("excess hack gap at $n{=}64$ ($\\sigma$)")
    ax.set_title(title, loc="left", fontweight="bold", fontsize=11)
    despine(ax)
# annotate the indistinguishable pair on the left panel
sab = next(r for r in h2h if "sabotage" in r["config"])
hon14 = next(r for r in h2h if r["config"].startswith("noref") and "14B" in r["config"])
axes[0].annotate("sabotaged frontier\n($r{=}{+}0.35$)",
                 (sab["naive_pearson"], sab["bon"]["excess_gap"]),
                 (0.16, 0.70), fontsize=9, color=GRAY,
                 arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.7))
axes[0].annotate("honest 14B blind\n($r{=}{+}0.37$)",
                 (hon14["naive_pearson"], hon14["bon"]["excess_gap"]),
                 (0.50, 0.56), fontsize=9, color=GRAY,
                 arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.7))
axes[1].annotate("conviction region\n(style partial $>0.3$)", (0.45, 0.45), fontsize=9,
                 color=ORANGE, ha="center")
axes[1].axvspan(0.30, 0.72, color=ORANGE, alpha=0.06)
h = [plt.Line2D([], [], marker="o", ls="", color=BLUE, label="certified (referenced)"),
     plt.Line2D([], [], marker="o", ls="", color=ORANGE, label="failed / convicted")]
axes[0].legend(handles=h, frameon=False, loc="lower left")
fig.tight_layout(w_pad=2.2)
fig.savefig("figures/fig_h2h.pdf", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------ fig_curves.pdf
curve = json.load(open(f"{AN}/bon_curve.json"))
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.3), sharey=True)
for ax, dom, title in ((axes[0], "math", "math (MATH-500)"), (axes[1], "code", "code (MBPP+)")):
    for cfg, d in curve.items():
        if not cfg.startswith(f"{dom}__") and not (dom == "code" and cfg.startswith("code__")):
            continue
        if dom == "math" and not cfg.startswith("math__"):
            continue
        certified = "__ref" in cfg and "sabotage" not in cfg
        col = BLUE if certified else ORANGE
        xs = [4, 16, 64]
        ys = [d[str(n)]["raw_gap"] if str(4) in d else d[n]["raw_gap"] for n in xs]
        ax.plot(xs, ys, "-o", color=col, lw=1.6, ms=4, alpha=0.85)
    ax.set_xscale("log", base=2)
    ax.set_xticks([4, 16, 64], ["4", "16", "64"])
    ax.set_xlabel("best-of-$n$ (log scale)")
    ax.set_title(title, loc="left", fontweight="bold", fontsize=11)
    despine(ax)
axes[0].set_ylabel("raw hack gap ($\\sigma$)")
h = [plt.Line2D([], [], color=BLUE, marker="o", label="certified (referenced)"),
     plt.Line2D([], [], color=ORANGE, marker="o", label="failed / convicted")]
axes[0].legend(handles=h, frameon=False, loc="lower left")
fig.tight_layout(w_pad=1.6)
fig.savefig("figures/fig_curves.pdf", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------ fig_stability.pdf
sub = json.load(open(f"{AN}/label_subsampling.json"))
fig, ax = plt.subplots(figsize=(5.4, 3.2))
series = {}
for r in sub:
    series.setdefault(r["config"], []).append((r["n"], r["agree"]))
LABELS = {"gpt_sabotage": ("sabotage conviction", ORANGE, "-"),
          "gpt_honest": ("honest frontier pass", BLUE, "-"),
          "noref_Qwen_Qwen2.5-1.5B-Instruct": ("1.5B blind conviction", ORANGE, "--"),
          "ref_Qwen_Qwen2.5-1.5B-Instruct": ("1.5B referenced pass (boundary)", BLUE, "--"),
          "noref_Qwen_Qwen2.5-14B-Instruct": ("14B blind (boundary)", GRAY, ":")}
for cfg, (lab, col, ls) in LABELS.items():
    pts = sorted(series.get(cfg, []))
    if pts:
        ax.plot(*zip(*pts), ls, color=col, marker="o", ms=4, lw=1.6, label=lab)
ax.set_xlabel("labels used $n$")
ax.set_ylabel("fraction of resamples\nreproducing full-sample verdict")
ax.set_ylim(0.4, 1.03)
ax.legend(frameon=False, fontsize=8.5, loc="lower right")
despine(ax)
fig.tight_layout()
fig.savefig("figures/fig_stability.pdf", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------ fig_gate.pdf (vector remake)
mathd = {"1.5B": (0.88, 0.16), "3B": (0.44, 0.07), "7B": (0.80, 0.18),
         "14B": (0.63, 0.05), "GPT-5.2": (None, 0.38)}
coded = {"1.5B": (1.45, 1.40), "3B": (1.06, 0.43), "7B": (1.06, 0.49),
         "14B": (1.04, 0.37), "GPT-5.2": (0.78, 0.22)}
fig, axes = plt.subplots(1, 2, figsize=(9.2, 2.9), sharey=True)
sizes = ["1.5B", "3B", "7B", "14B", "GPT-5.2"]
for ax, data, dom in ((axes[0], mathd, "math (compare text)"),
                      (axes[1], coded, "code (execute tests)")):
    ys = np.arange(len(sizes))[::-1]
    for y, s in zip(ys, sizes):
        noref, ref = data[s]
        if noref is not None:
            ax.plot([ref, noref], [y, y], color="#d0d0d0", lw=1.6, zorder=1)
            ax.plot([noref], [y], "o", color=ORANGE, ms=7, zorder=3)
        ax.plot([ref], [y], "o", color=BLUE, ms=7, zorder=3)
    ax.set_yticks(ys, sizes)
    ax.set_xlim(-0.05, 1.6)
    ax.set_xlabel("excess hack gap ($\\sigma$)")
    ax.set_title(dom, loc="left", fontweight="bold", fontsize=11)
    despine(ax, keep=("bottom",))
    ax.tick_params(left=False)
axes[1].annotate("reference does nothing\nat 1.5B on code", (1.40, 4), (0.5, 3.2),
                 fontsize=9, color=GRAY, arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.7))
h = [plt.Line2D([], [], marker="o", ls="", color=ORANGE, label="blind"),
     plt.Line2D([], [], marker="o", ls="", color=BLUE, label="with trusted reference")]
axes[0].legend(handles=h, frameon=False, loc="lower right")
fig.tight_layout(w_pad=1.8)
fig.savefig("figures/fig_gate.pdf", bbox_inches="tight")
plt.close(fig)

print("wrote figures/: fig_h2h.pdf fig_curves.pdf fig_stability.pdf fig_gate.pdf")
