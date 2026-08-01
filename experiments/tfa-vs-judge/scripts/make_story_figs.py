import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT="paper/figs"
# ---- fig_judge: item-level partial rho under two judges (generalizes beyond one judge) ----
ds=["MATH-500","GSM8K","Putnam-AXIOM"]
g=[-0.01,0.12,0.22]; glo=[0.04,0.04,0.06]; ghi=[0.05,0.04,0.05]      # gpt-5.2 (val, +/- from CI)
o=[-0.01,0.10,0.16]; olo=[0.04,0.04,0.05]; ohi=[0.04,0.04,0.06]      # Opus 4.8
x=np.arange(len(ds)); w=0.36
fig,ax=plt.subplots(figsize=(8.6,4.6))
ax.bar(x-w/2,g,w,yerr=[glo,ghi],capsize=4,color="#2b5c8a",label="Judge A: gpt-5.2")
ax.bar(x+w/2,o,w,yerr=[olo,ohi],capsize=4,color="#7d54c9",label="Judge B: Claude Opus 4.8 (different family)")
ax.axhline(0,color="#333",lw=1)
ax.set_xticks(x); ax.set_xticklabels(ds,fontsize=10.5); ax.set_ylabel("item-level partial ρ(TFA, judge | correct)",fontsize=10.5)
ax.legend(fontsize=9,frameon=False,loc="upper left"); ax.grid(axis="y",alpha=0.3)
ax.set_title("Generalizes beyond one judge: the same pattern under a second frontier judge from a different family\n"
             "MATH null stays null; the small GSM8K and Putnam signals replicate (CIs still exclude zero).",fontsize=10.6)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_judge.png",dpi=150,bbox_inches="tight"); plt.close(fig); print("wrote fig_judge.png")

# ---- fig_variants: every TFA variant fails to recover an item-level signal ----
V=[("baseline TFA",-0.01),("content-token TFA",0.00),("TFA-logprob / BPC",0.00),
   ("IDF-weighted TFA",-0.01),("surprisal-weighted TFA",-0.16),
   ("step-shuffle contrast",-0.13),("answer-swap contrast\n(after length control)",-0.02)]
labs=[v[0] for v in V]; vals=[v[1] for v in V]; y=np.arange(len(V))[::-1]
cols=["#c44e52" if v<-0.03 else "#9aa3af" for v in vals]
fig,ax=plt.subplots(figsize=(9,4.8))
ax.barh(y,vals,color=cols,height=0.6)
for yi,v in zip(y,vals): ax.text(v+(0.006 if v>=0 else -0.006),yi,f"{v:+.2f}",va="center",ha="left" if v>=0 else "right",fontsize=9)
ax.axvline(0,color="#333",lw=1)
ax.set_yticks(y); ax.set_yticklabels(labs,fontsize=9.5); ax.set_xlim(-0.28,0.12)
ax.set_xlabel("item-level partial ρ(variant, judge | correct)  on MATH / anchors",fontsize=10)
ax.grid(axis="x",alpha=0.3)
ax.set_title("Every cheap fix fails: no TFA variant recovers a per-item quality signal\n"
             "(the answer-swap contrast looked like +0.35 before length control, then retracted as an artifact).",fontsize=10.6)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_variants.png",dpi=150,bbox_inches="tight"); plt.close(fig); print("wrote fig_variants.png")
