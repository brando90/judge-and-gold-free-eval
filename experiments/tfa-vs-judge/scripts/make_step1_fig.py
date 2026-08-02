# Step-1 certificate figure, built on VERIFIED (cross-validated, model-controlled) numbers from
# runs/step1_verified.json. Two axes:
#   x = quality signal (variance explained by ground-truth correctness), higher better
#   y = surface nuisance among correct answers, 5-fold cross-validated, lower better
# Trustworthy = bottom-right. TFA collapses to the left (no quality signal); LLM judges sit right; the
# yardstick flags Opus's GSM8K length bias. Putnam cells are small-n (~120 correct) and drawn hollow.
import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

V = json.load(open("runs/step1_verified.json"))
ABBR = {"MATH-500": "MATH", "GSM8K": "GSM8K", "Putnam": "Putnam"}
JC = {"gpt-5.2": "#2b5c8a", "claude-opus-4-8": "#2f8f4e"}
def y_of(o): return 100 * max(0.0, o.get("surface_cv", 0.0))
def x_of(o): return 100 * o.get("quality", 0.0)

fig, ax = plt.subplots(figsize=(8.4, 5.6))
ax.axhspan(0, 6, xmin=0.5, color="#2f8f4e", alpha=0.06, zorder=0)
ax.text(47, 5.6, "trustworthy region: quality-tracking, low surface", ha="left", va="top",
        fontsize=8.5, color="#2f8f4e")

seen_tfa = set()
for d in V:
    lowconf = (d == "Putnam")
    for jm in V[d]:
        jl = jm
        js, tf = V[d][jm]["judge_score"], V[d][jm]["tfa_argmax"]
        if "surface_cv" in js:
            x, y = x_of(js), y_of(js)
            lab = "GPT-5.2" if "gpt" in jl else "Opus"
            ax.scatter(x, y, s=95, facecolor=("none" if lowconf else JC.get(jl)), zorder=3,
                       edgecolor=JC.get(jl), linewidth=1.6 if lowconf else 1.2)
            tag = f"{ABBR[d]} judge ({lab})" + (" ·small n" if lowconf else "")
            ax.annotate(tag, (x, y), fontsize=8, xytext=(6, 3), textcoords="offset points",
                        color=("#999" if lowconf else "black"))
        if "surface_cv" in tf and d not in seen_tfa:
            seen_tfa.add(d)
            x, y = x_of(tf), y_of(tf)
            ax.scatter(x, y, s=110, marker="X", facecolor=("none" if lowconf else "#b0453f"),
                       edgecolor="#b0453f", linewidth=1.6 if lowconf else 1.0, zorder=3)
            ax.annotate(f"{ABBR[d]} TFA" + (" ·small n" if lowconf else ""), (x, y), fontsize=8,
                        xytext=(6, 3), textcoords="offset points", color="#b0453f")

# callout: the verified Opus GSM8K length bias
og = V["GSM8K"]["claude-opus-4-8"]["judge_score"]
ax.annotate("Opus over-rewards length on GSM8K\n9.7% CV, survives model controls",
            (x_of(og), y_of(og)), xytext=(x_of(og) - 45, 12.4), fontsize=8, color="#2f8f4e",
            arrowprops=dict(arrowstyle="->", color="#2f8f4e", lw=1))

ax.scatter([], [], color=JC["gpt-5.2"], s=95, edgecolor="white", label="LLM judge (GPT-5.2)")
ax.scatter([], [], color=JC["claude-opus-4-8"], s=95, edgecolor="white", label="LLM judge (Opus 4.8)")
ax.scatter([], [], marker="X", color="#b0453f", s=110, label="TFA (reference-anchored)")
ax.scatter([], [], marker="o", facecolor="none", edgecolor="#888", s=95, label="hollow = small n (Putnam ~120)")
ax.legend(loc="upper right", frameon=False, fontsize=8.5)

ax.set_xlabel("Quality signal: % of score variance explained by correctness  →")
ax.set_ylabel("Surface nuisance among correct answers, cross-validated (%)  →")
ax.set_title("The yardstick: certifying evaluators without trusting them", fontsize=12, fontweight="bold")
ax.set_xlim(-5, 92); ax.set_ylim(-1, 14)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="both", color="#e6e6e6", lw=0.6)
fig.tight_layout()
fig.savefig("paper/figs/fig_step1_yardstick.png", dpi=160)
print("wrote paper/figs/fig_step1_yardstick.png (verified/CV)")
