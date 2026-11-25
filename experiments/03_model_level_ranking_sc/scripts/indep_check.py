"""Independent plain exact-string SC and boxed-rate check (no Math-Verify). Usage: python3 -I scripts/indep_check.py results  (reads results/gen/*.jsonl)."""
import json,glob,os,collections
import sys
D=sys.argv[1] if len(sys.argv)>1 else 'results'
OB,CB=chr(123),chr(125)
def lb(s):
    i=s.rfind("\\boxed")
    if i<0: return None
    j=s.find(OB,i)
    if j<0: return None
    d=0
    for k in range(j,len(s)):
        if s[k]==OB: d+=1
        elif s[k]==CB:
            d-=1
            if d==0: return "".join(s[j+1:k].split())
    return None
out={}
for f in sorted(glob.glob(D+'/gen/*.jsonl')):
    rows=[json.loads(l) for l in open(f)]
    sc=box=n=em=emb=0
    for r in rows:
        a=[lb(s) for s in r['samples']]
        c=collections.Counter(x for x in a if x is not None)
        sc+=sum(v*(v-1) for v in c.values())/(16*15)
        box+=sum(x is not None for x in a); n+=len(a)
        g="".join(str(r['answer']).split())
        em+=sum(x==g for x in a)
    out[os.path.basename(f)]=dict(rows=len(rows),SC=round(sc/len(rows),4),boxed=round(box/n,4),exact_pass1=round(em/n,4),exact_pass1_boxed_only=round(em/box,4))
    print(os.path.basename(f),out[os.path.basename(f)])
json.dump(out,open(D+'/indep_check.json','w'),indent=1)
