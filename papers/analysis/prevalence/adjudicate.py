import json, math, collections
ADJ = {
# gsm8k
'gsm8k-1254':('MULTI','ambiguous_reading','Both annotators identified the concurrent-drying reading; the question never says coats are applied one after another, so 12-7=5 min longer is as defensible as the cumulative 6*(12-7)=30 (ref).'),
# deepscaler
'deepscaler-23406':('UNIQUE',None,'"standard deviation of this sample" (not "sample standard deviation"); in the source curriculum it is the n-denominator SD; n-1 variant is a convention difference -> conservative UNIQUE.'),
'deepscaler-25638':('UNIQUE',None,'VP1/VP2 are labeled, so the count is determined (997920); the reference 554400 is a reference error, not answer multiplicity.'),
'deepscaler-25643':('UNCLEAR',None,'Final request ("find the equation of line AB") has two valid lines y=x and y=-x, but the reference answers a different quantity (area 8/5); the reference/question mismatch makes the item malformed rather than cleanly MULTI -> conservative UNCLEAR.'),
'deepscaler-27487':('UNCLEAR',None,'Verified: adding two balls of the drawn colour keeps the red count even (2,4,6,8), so "exactly five red" is impossible; malformed transcription of the original problem.'),
'deepscaler-27893':('UNIQUE',None,'Natural reading has one answer (~527 m, computed); the reference 16.38 is irreproducible, which is a reference error, not multiplicity.'),
'deepscaler-31879':('MULTI','other','Question asks for "the value of x" (not "find all"); a.b=-x^2+2x+3=0 has roots x=3 and x=-1 (python-verified), each satisfies the question; reference lists only -1. Literal MULTI definition applies.'),
# nqopen
'nqopen-373':('UNIQUE',None,'Two co-writers form one complete answer (Pebe Sebert and Hugh Moffatt); co-author sets treated as UNIQUE throughout.'),
'nqopen-753':('MULTI','ambiguous_reading','"Who sings" admits the character (Hodel, ref) or a performer (Julia Migenes, 1964 Broadway; Michele Marsh, 1971 film); parallels Big Momma item 1298.'),
'nqopen-908':('UNIQUE',None,'Edition page-count variation is a small numeric tolerance, not distinct answers; neither annotator could name a concrete alternative with confidence.'),
'nqopen-1110':('UNIQUE',None,'"Amendments to the constitution" are the 27 ratified ones; 33 counts proposals that did not become amendments.'),
'nqopen-1352':('UNIQUE',None,'Season 11 is complete with 24 episodes; gold 14/12 is an outdated partial count, not a second valid answer.'),
'nqopen-1523':('UNCLEAR',None,'Version (US/UK/other) unspecified, but UK has several tied GBP1M winners and neither annotator could confirm the second gold name; cannot decide cleanly.'),
'nqopen-1577':('UNIQUE',None,'Literal "tournament of power start" is the tournament itself (ep. 97, July 2017); the Feb 2017 saga start is a looser reading -> conservative UNIQUE.'),
'nqopen-1722':('UNIQUE',None,'smen / samna / samneh are transliterations of the same Arabic word -> aliases.'),
'nqopen-1845':('MULTI','temporal','Person heading WV executive changed (Jim Justice 2017-2025, Patrick Morrisey 2025-) and the wording fixes no time; same temporal rule as other items.'),
'nqopen-1952':('UNIQUE',None,'Henry system co-devised (Henry with Haque and Bose) -> treated as one co-developer set, consistent with co-writer rule.'),
'nqopen-2004':('UNCLEAR',None,'Classification scheme unspecified (multinational corporation / retail chain / for-profit); vague rather than cleanly multi.'),
'nqopen-2021':('UNIQUE',None,'English/Welsh patronymic origin is one answer at British-Isles granularity.'),
'nqopen-2213':('UNIQUE',None,'Sierra Nevada snowmelt -> Feather River -> Delta intake is one water path described at different granularity.'),
'nqopen-2214':('UNCLEAR',None,'Earliest continent is scientifically debated (Ur vs Vaalbara) and gold Pangaea is likely wrong; cannot decide cleanly.'),
'nqopen-2247':('MULTI','temporal','Venue changed (Sherwood CC, Thousand Oaks until 2013; Albany, Bahamas since 2015) and present tense fixes no time; same temporal rule as Astros item 3391.'),
'nqopen-2357':('UNIQUE',None,'Composite anatomical answer (central retinal artery via optic nerve); choroid reading is a different vessel bed -> conservative UNIQUE.'),
'nqopen-2389':('MULTI','temporal','Conference lead changed over time: AFC led through the 1970s-early 1980s (e.g. 11-4 after SB XV), NFC leads in the gold era; ties at times.'),
'nqopen-2600':('UNCLEAR',None,'Malformed: the Coral Sea is a marginal sea of the Pacific, no crisp meeting point.'),
'nqopen-2857':('UNIQUE',None,'Tavarez is the Spanish form of Portuguese Tavares; one etymology at different depth -> conservative UNIQUE.'),
'nqopen-2996':('UNIQUE',None,'NYC supply systems (Catskill, Delaware, Croton) form one set answer.'),
'nqopen-3254':('UNCLEAR',None,'Ranking is year- and source-dependent; neither annotator could confirm a concrete alternative rank.'),
'nqopen-3380':('UNIQUE',None,'Pacific Northwest states form one set answer.'),
'nqopen-3431':('UNIQUE',None,'"played" plus title "101 Dalmatians" matches the 1996 live-action film (1961 film is "One Hundred and One Dalmatians", voice role) -> Glenn Close.'),
'nqopen-3450':('MULTI','ambiguous_reading','Two characters are named Stephanie Forrester: Stephanie Sr. (mother Ann Douglas) and Steffy (mother Taylor Hayes, the gold).'),
'nqopen-3458':('MULTI','ambiguous_reading','Oregon reinstated the death penalty twice: 1978 (Ballot Measure 8) and 1984 (Measures 6/7, gold); wording does not say "most recent".'),
'nqopen-3503':('UNIQUE',None,'Survivors (Edgar, Albany, Kent) form one set answer.'),
'nqopen-3544':('MULTI','multiple_entities','Plural open question "what are the value(s)": "ensure consistency" and "improve communication" are distinct valid values; consistent with forest-uses item 2509.'),
}
def load(fn): return {d['id']:d for d in map(json.loads, open(fn))}
P2 = {'math500':['labels_pass2_math500_b1.jsonl','labels_pass2_math500_b2.jsonl'],'gsm8k':['labels_pass2_gsm8k.jsonl'],
      'deepscaler':['labels_pass2_deepscaler_b1.jsonl','labels_pass2_deepscaler_b2.jsonl'],'nqopen':['labels_pass2_nqopen.jsonl']}
def wilson(k,n,z=1.959964):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h), min(1,c+h))
def kappa(a,b,cats):
    n=len(a); po=sum(x==y for x,y in zip(a,b))/n; pe=sum((a.count(c)/n)*(b.count(c)/n) for c in cats)
    return po, ((po-pe)/(1-pe) if pe<1 else None)
stats={}
for ds,fns in P2.items():
    items=[json.loads(l) for l in open(f'items_{ds}.jsonl')]; p1=load(f'pass1/labels_pass1_{ds}.jsonl'); p2={}
    for fn in fns: p2.update(load(fn))
    rows=[]
    for it in items:
        i=it['id']; a,b=p1[i],p2[i]
        if a['label']==b['label']:
            src = a if a['label']!='MULTI' else a
            fin=dict(label=a['label'], subtype=a['subtype'] or b.get('subtype'), justification=a['justification'] or b.get('justification',''), adjudicated=False, adjudication_reason='')
        else:
            lab,st,why=ADJ[i]
            fin=dict(label=lab, subtype=st, justification=(a['justification'] if lab==a['label'] and a['justification'] else b.get('justification','')), adjudicated=True, adjudication_reason=why)
        rows.append(dict(id=i, question=it['question'], reference=it['reference'], pass1=a['label'], pass2=b['label'], pass1_just=a['justification'], pass2_just=b.get('justification',''), **fin))
    missing=[i for i in ADJ if i.startswith(ds+'-') and i not in {r['id'] for r in rows if r['adjudicated']}]
    assert not missing, missing
    with open(f'final_labels_{ds}.jsonl','w') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False)+'\n')
    A=[r['pass1'] for r in rows]; B=[r['pass2'] for r in rows]
    po,k3=kappa(A,B,['MULTI','UNIQUE','UNCLEAR']); pob,kb=kappa([x=='MULTI' for x in A],[x=='MULTI' for x in B],[True,False])
    c=collections.Counter(r['label'] for r in rows); n=len(rows); lo,hi=wilson(c['MULTI'],n)
    decided=n-c['UNCLEAR']; lo2,hi2=wilson(c['MULTI'],decided)
    sub=collections.Counter(r['subtype'] for r in rows if r['label']=='MULTI')
    stats[ds]=dict(n=n, multi=c['MULTI'], unique=c['UNIQUE'], unclear=c['UNCLEAR'], rate=c['MULTI']/n, wilson_ci=[lo,hi],
        rate_excl_unclear=c['MULTI']/decided, wilson_ci_excl_unclear=[lo2,hi2],
        raw_agreement_3class=po, kappa_3class=k3, raw_agreement_multi_vs_rest=pob, kappa_multi_vs_rest=kb,
        n_disagreements=sum(x!=y for x,y in zip(A,B)), pass1_counts=dict(collections.Counter(A)), pass2_counts=dict(collections.Counter(B)),
        multi_subtypes=dict(sub))
    print(ds, json.dumps(stats[ds]))
json.dump(stats, open('_stats.json','w'), indent=1)
