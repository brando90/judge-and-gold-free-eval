# Semantic-embedding similarity (the missing metric class): all four columns.
# boundary rho, item-level grading partial, human anchor, two-way decomposition.
import json, glob, collections
import numpy as np
from scipy import stats
from sentence_transformers import SentenceTransformer

M = SentenceTransformer("all-MiniLM-L6-v2")
def embed(texts):
    return M.encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)

def fam(m):
    m=m.lower()
    if "qwen2.5-math" in m: return "Qwen-Math"
    if "qwen" in m and "coder" not in m: return "Qwen2.5"
    if "phi" in m: return "Phi"
    if "mistral" in m or "ministral" in m: return "Mistral"
    if "olmo" in m: return "OLMo"
    return "other"

ANCH={
 "MATH-500":["runs/math500/*.judged.jsonl","runs/d2/math500__*.judged.jsonl","runs/wsv/math500__*.jsonl","runs/all/math500__*.jsonl"],
 "Putnam-AXIOM":["runs/putnam/*.judged.jsonl","runs/d2/putnam-axiom__*.judged.jsonl","runs/wsv/putnam-axiom__*.jsonl","runs/all/putnam-axiom__*.jsonl"],
 "GSM8K":["runs/gsm8k/*.judged.jsonl","runs/d2/gsm8k__*.judged.jsonl","runs/all/gsm8k__*.jsonl"],
}
pm=json.load(open("paper/figs/.permodel_cache.json"))
def partial(x,y,z):
    x,y,z=stats.rankdata(x),stats.rankdata(y),stats.rankdata(z);A=np.vstack([z,np.ones_like(z)]).T
    rx=x-A@np.linalg.lstsq(A,x,rcond=None)[0];ry=y-A@np.linalg.lstsq(A,y,rcond=None)[0]
    return stats.pearsonr(rx,ry).statistic
GEN={"Qwen2.5","Phi","Mistral","OLMo"}
res={}
for ds,globs in ANCH.items():
    per={}
    for g in globs:
        for fp in glob.glob(g):
            for l in open(fp):
                r=json.loads(l)
                if r.get("free_gen") and r.get("gold_solution"):
                    per.setdefault(r["model"],{})[str(r["problem_id"])]=(r["free_gen"][:2000],r["gold_solution"][:2000],r.get("judge_score"),r.get("boxed_correct",0))
    golds={}
    for m,it in per.items():
        for pid,(fg,gs,_,_) in it.items(): golds[pid]=gs
    gvec={pid:v for pid,v in zip(golds, embed(list(golds.values())))}
    sim={}
    for m,it in per.items():
        pids=list(it); fvecs=embed([it[p][0] for p in pids])
        for p,fv in zip(pids,fvecs): sim[(m,p)]=float(np.dot(fv,gvec[p]))
    accs={m.split("/")[-1]:v["acc"] for m,v in pm[ds].items()}
    means=[(np.mean([sim[(m,p)] for p in it]),accs[m.split("/")[-1]]) for m,it in per.items() if m.split("/")[-1] in accs]
    rho=stats.spearmanr([x[0]for x in means],[x[1]for x in means]).statistic
    X=[];J=[];C=[]
    for m,it in per.items():
        if fam(m)=="Qwen2.5":
            for p,(fg,gs,j,c) in it.items():
                if j is not None: X.append(sim[(m,p)]);J.append(j);C.append(c)
    pr=partial(X,J,C) if len(X)>50 else float('nan')
    dec=None
    fams=collections.defaultdict(list)
    for m in per:
        if fam(m) in GEN: fams[fam(m)].append(m)
    fams={f:sorted(ms) for f,ms in fams.items() if len(ms)>=3}
    models=[m for ms in fams.values() for m in ms]
    if len(fams)>=3:
        shared=set.intersection(*(set(per[m]) for m in models)); items=sorted(shared)
        if len(items)>=30:
            T=np.array([[sim[(m,j)] for j in items] for m in models]); D=T-T.mean(axis=1,keepdims=True)
            famof=np.array([fam(m) for m in models]); fn=sorted(fams)
            Cm=np.array([D[famof==f].mean(axis=0) for f in fn]); b=Cm.mean(axis=0)
            sst=(D**2).sum(); ssi=len(models)*(b**2).sum()
            ssx=sum(((Cm[fn.index(fam(m))]-b)**2).sum() for m in models)
            dec=(100*ssi/sst,100*ssx/sst,100*(sst-ssi-ssx)/sst)
    res[ds]=dict(rho=rho,partial=pr,dec=dec)
    print(f"{ds:14s} embed-cos: boundary={rho:+.2f}  item-partial={pr:+.3f}  dec={dec}",flush=True)
    # save sims for the human anchor
    if ds=="MATH-500":
        json.dump({f"{m}|{p}":v for (m,p),v in sim.items()},open("runs/embed_sims_math500.json","w"))
json.dump(res,open("runs/embed_class_law.json","w"),default=str)
print("[embed-done]")
