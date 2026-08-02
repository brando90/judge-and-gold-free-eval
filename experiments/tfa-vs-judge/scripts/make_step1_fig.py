# Step-1 certificate figure: place each evaluator on two axes the yardstick measures ---
#   x = quality signal (share of score variance explained by ground-truth correctness), higher better
#   y = surface nuisance among already-correct answers (share explained by length/format), lower better
# A trustworthy evaluator sits bottom-right. TFA collapses to the left (no quality signal); the LLM judges
# sit right, and the yardstick separates them by dataset (e.g. Opus is length-biased on GSM8K).
import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = json.load(open("runs/judge_nuisance.json"))
ABBR = {"MATH-500": "MATH", "GSM8K": "GSM8K", "Putnam": "Putnam"}
JC = {"gpt-5.2": "#2b5c8a", "claude-opus-4-8": "#2f8f4e"}

fig, ax = plt.subplots(figsize=(8.2, 5.6))
ax.axhspan(0, 6, xmin=0.5, color="#2f8f4e", alpha=0.06, zorder=0)
ax.text(47, 5.4, "trustworthy region: quality-tracking, low surface", ha="left", va="top",
        fontsize=8.5, color="#2f8f4e")

seen_tfa = set()
for d in R:
    for jm in R[d]:
        jl = jm.split("/")[-1]
        js, tf = R[d][jm]["judge_score"], R[d][jm]["tfa_argmax"]
        if js and js.get("within_correct_surface") is not None:
            x, y = 100 * js["var_correct"], 100 * js["within_correct_surface"]
            lab = "GPT-5.2" if "gpt" in jl else "Opus"
            ax.scatter(x, y, s=95, color=JC.get(jl, "#888"), zorder=3, edgecolor="white", linewidth=1.2)
            ax.annotate(f"{ABBR[d]} judge ({lab})", (x, y), fontsize=8, xytext=(6, 3), textcoords="offset points")
        if tf and tf.get("within_correct_surface") is not None and d not in seen_tfa:
            seen_tfa.add(d)
            x, y = 100 * tf["var_correct"], 100 * tf["within_correct_surface"]
            ax.scatter(x, y, s=110, marker="X", color="#b0453f", zorder=3)
            ax.annotate(f"{ABBR[d]} TFA", (x, y), fontsize=8, xytext=(6, 3), textcoords="offset points", color="#b0453f")

# callout: the yardstick catches Opus's length bias on GSM8K
gk = R["GSM8K"]["anthropic/claude-opus-4-8"]["judge_score"] if "anthropic/claude-opus-4-8" in R["GSM8K"] else R["GSM8K"]["claude-opus-4-8"]["judge_score"]
ax.annotate("Opus over-rewards length\non GSM8K (9.9% is length)",
            (100 * gk["var_correct"], 100 * gk["within_correct_surface"]),
            xytext=(100 * gk["var_correct"] - 42, 12.5), fontsize=8, color="#2f8f4e",
            arrowprops=dict(arrowstyle="->", color="#2f8f4e", lw=1))

ax.scatter([], [], color=JC["gpt-5.2"], s=95, edgecolor="white", label="LLM judge (GPT-5.2)")
ax.scatter([], [], color=JC["claude-opus-4-8"], s=95, edgecolor="white", label="LLM judge (Opus 4.8)")
ax.scatter([], [], marker="X", color="#b0453f", s=110, label="TFA (reference-anchored)")
ax.legend(loc="upper right", frameon=False, fontsize=9)

ax.set_xlabel("Quality signal: % of score variance explained by correctness  →")
ax.set_ylabel("Surface nuisance among correct answers (%)  →")
ax.set_title("The yardstick: certifying evaluators without trusting them", fontsize=12, fontweight="bold")
ax.set_xlim(-5, 92); ax.set_ylim(-1, 15)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="both", color="#e6e6e6", lw=0.6)
fig.tight_layout()
fig.savefig("paper/figs/fig_step1_yardstick.png", dpi=160)
print("wrote paper/figs/fig_step1_yardstick.png")
