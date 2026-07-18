import json, glob, numpy as np
from scipy import stats
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent
from tfa.analyze import bootstrap_partial, bootstrap_corr
def gold_ans(r, ds):
    if ds=="gsm8k": return r["gold_solution"].split("####")[-1].strip().replace(",","")
    return extract_boxed(r["gold_solution"])
def load(glob_, ds):
    R=[json.loads(l) for fp in glob.glob(glob_) for l in open(fp)]
    R=[r for r in R if r.get("judge_score") is not None]
    for r in R: r["cc"]=int(answers_equivalent(extract_final_answer(r["free_gen"], ds), gold_ans(r, ds)))
    return R
def resid(y,*ctrl):
    yr=stats.rankdata(y); X=np.column_stack([np.ones(len(y))]+[stats.rankdata(z) for z in ctrl]); b,_,_,_=np.linalg.lstsq(X,yr,rcond=None); return yr-X@b
print(f"{'dataset':9s} {'n':>4s} {'TFArange':>12s} {'ML rho(TFA,acc)':>15s} {'ML rho(TFA,jdg)':>15s} {'IL partial|corr (CI)':>24s} {'|corr&len':>9s} {'w-corr':>7s} {'w-wrong':>8s}")
for ds,g in [("MATH","runs/math500/*.judged.jsonl"),("GSM8K","runs/gsm8k/*.judged.jsonl"),("Putnam","runs/putnam/*.judged.jsonl")]:
    dskey={"MATH":"math500","GSM8K":"gsm8k","Putnam":"putnam"}[ds]
    R=load(g, dskey)
    import collections; by=collections.defaultdict(list)
    for r in R: by[r["model"]].append(r)
    mt=[];ma=[];mj=[]
    for m in by:
        rs=by[m]; mt.append(np.mean([x["tfa_argmax"] for x in rs])); ma.append(np.mean([x["cc"] for x in rs])); mj.append(np.mean([x["judge_score"] for x in rs]))
    mt,ma,mj=map(np.array,(mt,ma,mj))
    t=np.array([r["tfa_argmax"] for r in R]); j=np.array([r["judge_score"] for r in R]); c=np.array([r["cc"] for r in R]); gl=np.array([r["n_gold_tokens"] for r in R])
    pc=bootstrap_partial(t,j,c,n_boot=3000)
    plen=stats.spearmanr(resid(t,c,gl),resid(j,c,gl)).statistic
    cm=c==1; wm=c==0
    wc=bootstrap_corr(t[cm],j[cm]).rho if cm.sum()>5 else float("nan")
    ww=bootstrap_corr(t[wm],j[wm]).rho if wm.sum()>5 else float("nan")
    mlacc=stats.spearmanr(mt,ma).statistic; mljdg=stats.spearmanr(mt,mj).statistic
    print(f"{ds:9s} {len(R):4d} {mt.min():.2f}-{mt.max():.2f}   {mlacc:+15.2f} {mljdg:+15.2f}   {pc.rho:+.3f} [{pc.lo:+.2f},{pc.hi:+.2f}]   {plen:+9.3f} {wc:+7.3f} {ww:+8.3f}")
    print(f"          (correct stratum n={int(cm.sum())}, acc={ma.mean():.3f})")
