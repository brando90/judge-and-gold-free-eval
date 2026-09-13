import json, collections
def load(fn): return {d['id']:d for d in map(json.loads, open(fn))}
P2 = {'math500':['labels_pass2_math500_b1.jsonl','labels_pass2_math500_b2.jsonl'],
      'gsm8k':['labels_pass2_gsm8k.jsonl'],
      'deepscaler':['labels_pass2_deepscaler_b1.jsonl','labels_pass2_deepscaler_b2.jsonl'],
      'nqopen':['labels_pass2_nqopen.jsonl']}
def kappa(a,b,cats):
    n=len(a); po=sum(x==y for x,y in zip(a,b))/n
    pe=sum((a.count(c)/n)*(b.count(c)/n) for c in cats)
    return po, (po-pe)/(1-pe) if pe<1 else float('nan')
out={}
for ds,fns in P2.items():
    items=[json.loads(l) for l in open(f'items_{ds}.jsonl')]
    p1=load(f'pass1/labels_pass1_{ds}.jsonl'); p2={}
    for fn in fns: p2.update(load(fn))
    ids=[it['id'] for it in items]
    assert set(ids)==set(p1)==set(p2), (ds, len(set(ids)-set(p2)), len(set(p2)-set(ids)))
    a=[p1[i]['label'] for i in ids]; b=[p2[i]['label'] for i in ids]
    po,k3=kappa(a,b,['MULTI','UNIQUE','UNCLEAR'])
    ab=[x=='MULTI' for x in a]; bb=[x=='MULTI' for x in b]
    pob,kb=kappa(ab,bb,[True,False])
    dis=[i for i in ids if p1[i]['label']!=p2[i]['label']]
    print(f"== {ds}: agree={po:.3f} kappa3={k3:.3f} | binary MULTI agree={pob:.3f} kappa={kb:.3f} | disagreements={len(dis)}")
    print("   p1",collections.Counter(a)," p2",collections.Counter(b))
    q={it['id']:it for it in items}
    for i in dis:
        print(f"  {i} P1={p1[i]['label']} P2={p2[i]['label']} | REF={q[i]['reference'][:80]}")
        print(f"     Q: {q[i]['question'][:260]!r}")
        print(f"     p1: {p1[i]['justification']}")
        print(f"     p2: {p2[i]['justification']}")
