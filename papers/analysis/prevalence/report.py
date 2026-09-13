import json, math, collections
def wilson(k,n,z=1.959964):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0.0,c-h), min(1.0,c+h)]
S=json.load(open('_stats.json'))
F={ds:{r['id']:r for r in map(json.loads,open(f'final_labels_{ds}.jsonl'))} for ds in S}
META={
 'math500':dict(name='MATH-500',source='HuggingFaceH4/MATH-500 (test, 500 rows)',sampling='seeded sample of 200: random.seed(0); random.sample(range(500),200)'),
 'gsm8k':dict(name='GSM8K test',source='openai/gsm8k, config main, split test (1319 rows)',sampling='random.seed(0); random.sample(range(1319),200)'),
 'deepscaler':dict(name='DeepScaleR-Preview (RLVR train)',source='agentica-org/DeepScaleR-Preview-Dataset, split train (40315 rows)',sampling='random.seed(0); random.sample(range(40315),200)'),
 'nqopen':dict(name='Natural Questions open (val)',source='google-research-datasets/nq_open, split validation (3610 rows); chosen over TriviaQA (both allowed by the brief; NQ-open is a small direct download)',sampling='random.seed(0); random.sample(range(3610),200)'),
}
EX={
 'gsm8k':[
  ('gsm8k-187','106.12','Monthly compounding: 100*1.02^3 = 106.1208 (python); simple interest gives the reference 106.'),
  ('gsm8k-306','5','Literal parse: 20 loaves left; "half of what is left" (10) is split equally between afternoon and evening -> 5; reference splits all 20 -> 10.'),
  ('gsm8k-649','160000','"The number of likes was 70 times the initial" read as the total: 140000 + 20000 = 160000; reference adds 140000 new likes to 2000 -> 162000.'),
  ('gsm8k-93','36.36','Speed up 10% means time = 40/1.1 = 36.36 s; reference reduces time by 10% -> 36.'),
  ('gsm8k-1254','5','If the 6 paintings dry at the same time, the new varnish takes 12-7 = 5 min longer; reference sums per painting -> 30.')],
 'deepscaler':[
  ('deepscaler-30908','750 (or 2250)','Underdetermined p(2f+200)=7500: f=25 tickets at $30 + 175 at $10 = 2500 -> full-price revenue 750; f=150 at $15 + 50 at $5 = 2500 -> 2250; reference f=50,p=25 -> 1250 (python-enumerated).'),
  ('deepscaler-31879','3','a.b = -x^2+2x+3 = 0 has roots 3 and -1; x=3 gives a=(2,1,-3), b=(-3,3,-1), dot = -6+3+3 = 0 (python); question asks for "the value", reference -1.'),
  ('deepscaler-7605','-\\sqrt{3}','theta = -pi/3 satisfies cos(pi+theta) = -1/2 and gives tan(theta-9pi) = -sqrt3 (python); no quadrant given; reference sqrt3.'),
  ('deepscaler-12237','29/36','Broken chair in an interior position leaves 7 adjacent usable pairs of 36 -> 29/36; end chair -> 7/9 (reference); enumerated all 10 positions in python.'),
  ('deepscaler-8179','64.38 (837/13)','Weakest item: "up to 75 minutes" does not force the minimum number of CDs; 13 equal CDs hold 64.38 min each; reference assumes 12 -> 69.75.')],
 'nqopen':[
  ('nqopen-2502','John F. Kennedy','JFK was the first president who had been a Boy Scout; Ford was the only Eagle Scout; gold lists only Ford.'),
  ('nqopen-2783','submarine','"SS" on naval ships is the US Navy hull classification for submarine; gold gives the civilian steamship prefix.'),
  ('nqopen-3458','1978','Oregon restored the death penalty by ballot in 1978 (struck down 1981) and again in 1984; gold only 1984.'),
  ('nqopen-1154','Lewis Hamilton','Temporal: Schumacher (91) held the record until Hamilton passed him in 2020.'),
  ('nqopen-3450','Ann Douglas','Two characters named Stephanie Forrester: Stephanie Sr.\'s mother is Ann Douglas; Steffy\'s mother is Taylor Hayes (gold).')],
 'math500':[]}
out={}
for ds,s in S.items():
    rows=F[ds]
    A=[r['pass1'] for r in rows.values()]; B=[r['pass2'] for r in rows.values()]
    inter=sum(a=='MULTI' and b=='MULTI' for a,b in zip(A,B)); union=sum(a=='MULTI' or b=='MULTI' for a,b in zip(A,B))
    d=dict(dataset=META[ds]['name'], source=META[ds]['source'], sampling=META[ds]['sampling'], **{k:v for k,v in s.items()})
    d['sensitivity']=dict(both_annotators_multi=inter, rate_both=inter/200, wilson_both=wilson(inter,200) if inter else [0.0,wilson(0,200)[1]],
                          either_annotator_multi=union, rate_either=union/200, wilson_either=wilson(union,200))
    if ds=='nqopen':
        nt=sum(1 for r in rows.values() if r['label']=='MULTI' and r['subtype']!='temporal')
        d['multi_excluding_temporal']=dict(count=nt, rate=nt/200, wilson_ci=wilson(nt,200))
    d['examples']=[dict(id=i, question_snippet=rows[i]['question'][:240], reference=rows[i]['reference'], alternative_valid_answer=alt, verification=why, subtype=rows[i]['subtype']) for i,alt,why in EX[ds]]
    for e in d['examples']: assert rows[e['id']]['label']=='MULTI', e['id']
    d['multi_items']=[dict(id=r['id'], subtype=r['subtype'], justification=r['justification'], adjudicated=r['adjudicated']) for r in rows.values() if r['label']=='MULTI']
    d['unclear_items']=[dict(id=r['id'], reason=r['adjudication_reason'] or r['justification']) for r in rows.values() if r['label']=='UNCLEAR']
    d['adjudications']=[dict(id=r['id'], pass1=r['pass1'], pass2=r['pass2'], final=r['label'], reason=r['adjudication_reason']) for r in rows.values() if r['adjudicated']]
    out[ds]=d
out['_meta']=dict(date='2026-09-12', annotators='LLM annotators (Claude), not humans: pass 1 = orchestrating Claude session; pass 2 = fresh Claude subagents (one per dataset/batch of 100-200) that saw only the definitions and items; disagreements adjudicated by the pass-1 annotator with recorded reasons.',
   kappa_note='Cohen kappa over 3 classes (MULTI/UNIQUE/UNCLEAR) and binary MULTI-vs-rest; MATH-500 kappa undefined because both passes labeled all 200 items UNIQUE (100% raw agreement).',
   ci='95% Wilson score interval on MULTI/n (n=200, UNCLEAR kept in denominator); rate_excl_unclear also given.')
json.dump(out, open('prevalence_results.json','w'), indent=1, ensure_ascii=False)

P=lambda x:f"{100*x:.1f}%"
CI=lambda c:f"[{100*c[0]:.1f}, {100*c[1]:.1f}]"
K=lambda k:'undefined (100% agree)' if k is None else f"{k:.2f}"
L=[]
L+=["# Multi-answer prevalence audit (single-reference datasets)","",
"Date: 2026-09-12. **All labels were produced by LLM annotators (Claude), not humans**: pass 1 by the orchestrating Claude session, pass 2 by fresh Claude subagents that saw only the definitions and the items (not pass-1 labels); disagreements were adjudicated by the pass-1 annotator, and each reason is recorded. Both passes come from the same model family, so their errors may be correlated and kappa may overstate reliability. A human spot-check of the MULTI and UNCLEAR items is recommended before citing.","",
"## Question","In widely used datasets that ship ONE reference answer per question, what fraction of questions admit two or more DISTINCT valid final answers?","",
"## Definitions (applied strictly)",
"- **MULTI (k>1):** the question as written is satisfied by at least two final answers that are not equivalent (not the same number, expression, or set written differently). Examples: \"find a positive integer n such that ...\", \"give an example of ...\", a question genuinely ambiguous between two readings with different correct answers, or a free parameter the question leaves unpinned.",
"- **UNIQUE (k=1):** exactly one correct final answer up to equivalence. This includes \"find all x\" questions whose answer is one set, smallest/largest questions, equivalent forms, and numeric answers within rounding tolerance.",
"- **UNCLEAR:** cannot be decided without deep solving, or the question is malformed (missing figure or choices, inconsistent data, undefined symbols).",
"- Surface-equivalent forms (1/2 vs 0.5, x=3 vs 3) are **not** MULTI. A wrong reference is **not** MULTI by itself. Conservative rule: when in doubt, UNIQUE or UNCLEAR.",
"- Extra NQ-open rules: aliases are not MULTI. MULTI requires genuinely different correct entities, a genuine two-reading ambiguity, or a *temporal* question whose answer has changed and whose wording fixes no time (temporal items are reported separately). Complete co-author or co-developer sets and fixed-set answers (\"who survives\", \"which aqueducts\") count as one answer.",
"- Rules settled during adjudication: \"find the value of x\" with two roots is MULTI, because each root satisfies the question as written (not a \"find all\"). A question whose stated request differs from the quantity the reference answers is UNCLEAR.","",
"## Results","",
"| Dataset | n | MULTI | UNIQUE | UNCLEAR | MULTI rate [95% Wilson] | kappa (3-class) | kappa (MULTI vs rest) | raw agree | disagreements | both-annotator MULTI (lower) | either-annotator MULTI (upper) |",
"|---|---|---|---|---|---|---|---|---|---|---|---|"]
for ds in ['math500','gsm8k','deepscaler','nqopen']:
    d=out[ds]; s=d['sensitivity']
    L.append(f"| {d['dataset']} | {d['n']} | {d['multi']} | {d['unique']} | {d['unclear']} | {P(d['rate'])} {CI(d['wilson_ci'])} | {K(d['kappa_3class'])} | {K(d['kappa_multi_vs_rest'])} | {P(d['raw_agreement_3class'])} | {d['n_disagreements']} | {s['both_annotators_multi']} ({P(s['rate_both'])}) | {s['either_annotator_multi']} ({P(s['rate_either'])}) |")
nq=out['nqopen']['multi_excluding_temporal']
L+=["",f"- NQ-open without temporal items: {nq['count']}/200 = {P(nq['rate'])} {CI(nq['wilson_ci'])}. MULTI subtypes: {out['nqopen']['multi_subtypes']}.",
f"- Rates excluding UNCLEAR from the denominator: GSM8K {P(out['gsm8k']['rate_excl_unclear'])}, DeepScaleR {P(out['deepscaler']['rate_excl_unclear'])}, NQ-open {P(out['nqopen']['rate_excl_unclear'])}.",
"- **Takeaway:** single-answer math benchmarks are almost all UNIQUE. MATH-500 has 0/200 MULTI (upper bound 1.9%), and both GSM8K and DeepScaleR are at 2.5% (upper bound ~5.7%). The math MULTI cases are mostly wording ambiguities and unpinned parameters, not \"give an example\" questions. Open-domain QA is very different: about 30% MULTI, or 18.5% without temporal drift, which is in line with AmbigQA's finding that NQ-open is often ambiguous.",
f"- **Separate data-quality signal (not MULTI):** DeepScaleR has {out['deepscaler']['unclear']}/200 UNCLEAR (malformed: missing figures or choices, inconsistent data, impossible conditions) and several multi-part prompts where the reference answers only one part. Several references look wrong (e.g. gsm8k-454, deepscaler-25638, deepscaler-27893, deepscaler-29528). One DeepScaleR \"find all\" item has an incomplete reference (deepscaler-31229: answer set {18, -18}, reference 18).","",
"## Datasets and sampling"]
for ds in ['math500','gsm8k','deepscaler','nqopen']:
    L.append(f"- **{out[ds]['dataset']}**: {out[ds]['source']}; {out[ds]['sampling']} (sorted). Items: `items_{ds}.jsonl` / `.csv`.")
L+=["- No substitutions were needed. MATH-500 used the seeded 200-item option rather than all 500. For the optional open-domain set, NQ-open was used rather than TriviaQA.","",
"## Representative MULTI examples (alternatives verified)","Math alternatives were checked with python (`checks_gsm8k.py`, `checks_deepscaler.py`). NQ-open alternatives rest on annotator knowledge only (no web search), so they are lower-confidence.",""]
for ds in ['math500','gsm8k','deepscaler','nqopen']:
    d=out[ds]; L.append(f"### {d['dataset']}")
    if not d['examples']:
        L+=["No MULTI items. Nearest borderline: math500-385 (\"round to the nearest whole number\": rounding the final difference gives 22 = reference, rounding each currency amount first gives 23). Both annotators labeled it UNIQUE.",""]; continue
    for e in d['examples']:
        q=e['question_snippet'].replace('\n',' ').replace('|','/')
        L.append(f"- **{e['id']}** ({e['subtype']}): \"{q}{'...' if len(e['question_snippet'])>=240 else ''}\" Reference: `{e['reference'][:60]}`. Alternative: **{e['alternative_valid_answer']}**. {e['verification']}")
    L.append("")
L+=["## All MULTI and UNCLEAR ids",""]
for ds in ['gsm8k','deepscaler','nqopen']:
    d=out[ds]
    L.append(f"- **{d['dataset']}** MULTI: " + ", ".join(f"{m['id'].split('-')[1]}{'*' if m['adjudicated'] else ''}" for m in d['multi_items']) + "  (* = adjudicated)")
    L.append(f"- **{d['dataset']}** UNCLEAR: " + "; ".join(f"{u['id'].split('-')[1]}: {u['reason'][:90]}" for u in d['unclear_items']))
L+=["","## Adjudications (disagreements between passes)",""]
for ds in ['gsm8k','deepscaler','nqopen']:
    for a in out[ds]['adjudications']:
        L.append(f"- {a['id']}: P1={a['pass1']}, P2={a['pass2']} -> **{a['final']}**. {a['reason']}")
L+=["","## Files",
"- `items_*.jsonl|csv`: sampled items (id, row, question, reference).",
"- `pass1/labels_pass1_*.jsonl`: pass-1 labels. `labels_pass2_*.jsonl`: pass-2 subagent labels.",
"- `final_labels_*.jsonl`: both passes, final label, justification, and adjudication reason per item.",
"- `prevalence_results.json`: machine-readable counts, rates, Wilson CIs, kappas, sensitivity bounds, examples, and adjudications.",
"- Scripts: `sample.py`, `agreement.py`, `adjudicate.py`, `report.py`, `checks_*.py`."]
open('RESULTS.md','w').write("\n".join(L)+"\n")
for ds in ['math500','gsm8k','deepscaler','nqopen']:
    d=out[ds]; s=d['sensitivity']
    print(ds, d['multi'], d['unique'], d['unclear'], P(d['rate']), CI(d['wilson_ci']), K(d['kappa_3class']), K(d['kappa_multi_vs_rest']), d['n_disagreements'], 'both',s['both_annotators_multi'],'either',s['either_annotator_multi'])
print('nq excl temporal', nq)
