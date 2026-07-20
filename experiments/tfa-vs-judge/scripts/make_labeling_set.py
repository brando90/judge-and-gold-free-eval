# Build a human-labeling set of reasoning traces, over-sampling the cells where a human
# tiebreak is most informative: within-correct (deterministic checker cannot resolve) and
# TFA-vs-judge disagreement (high-TFA/low-judge and low-TFA/high-judge). Emits JSONL + CSV
# (portable) and a self-contained HTML labeler with MathJax rendering. No external deps
# except MathJax (CDN) for math; degrades to raw LaTeX if offline.
import json, glob, csv, html, random, collections, re
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent

def texify(t, ds):
    # Convert single-$ and $$ math to \( \) and \[ \] so MathJax (whose defaults do NOT
    # treat $ as a delimiter) renders MATH/Putnam LaTeX while GSM8K money ($18) stays literal.
    if ds == "GSM8K":
        return t
    t = re.sub(r"\$\$(.+?)\$\$", r"\\[\1\\]", t, flags=re.S)
    t = re.sub(r"\$([^$\n]+?)\$", r"\\(\1\\)", t)
    return t

random.seed(0)
OUTDIR = "human_eval"
import os; os.makedirs(OUTDIR, exist_ok=True)

# datasets where the item-level question is live and the correct stratum is populated,
# with a mix of families/styles (Qwen strong-and-verbose, Phi-4/Mistral different style).
POOLS = {
    "MATH-500": (["runs/math500/*Qwen2.5-7B*.judged.jsonl", "runs/math500/*Qwen2.5-14B*.judged.jsonl",
                  "runs/d2/math500__*phi-4*.judged.jsonl"], "math500"),
    "GSM8K":    (["runs/gsm8k/*Qwen2.5-7B*.judged.jsonl", "runs/d2/gsm8k__*phi-4*.judged.jsonl",
                  "runs/d2/gsm8k__*Mistral*.judged.jsonl"], "gsm8k"),
}
CAPS = {"A": 6, "B": 6, "C": 6, "D": 2, "E": 2, "F": 2}   # per dataset
CELL_DESC = {
    "A": "correct answer, high TFA, LOW judge  (metric says good, judge flags the reasoning)",
    "B": "correct answer, LOW TFA, high judge  (metric penalizes a valid but different-style solution)",
    "C": "lucky-correct? correct answer, low judge  (right answer, weak reasoning per judge)",
    "D": "correct answer, high TFA, high judge  (both agree it is good, calibration anchor)",
    "E": "wrong answer, high judge  (near-miss: wrong result, coherent reasoning)",
    "F": "wrong answer, low judge  (incoherent: wrong and unsound)",
}

def gold_ans(r, dk):
    return r["gold_solution"].split("####")[-1].strip().replace(",", "") if dk == "gsm8k" else extract_boxed(r["gold_solution"])

def pct(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0.0] * len(xs)
    for rank, i in enumerate(order): r[i] = rank / max(1, len(xs) - 1)
    return r

rows = []
for ds, (globs, dk) in POOLS.items():
    R = []
    for g in globs:
        for f in glob.glob(g):
            R += [json.loads(l) for l in open(f)]
    R = [r for r in R if r.get("judge_score") is not None]
    for r in R:
        r["cc"] = int(answers_equivalent(extract_final_answer(r["free_gen"], dk), gold_ans(r, dk)))
    tp = pct([r["tfa_argmax"] for r in R])
    for r, p in zip(R, tp): r["tfa_pct"] = p
    def cell(r):
        c, j, hi, lo = r["cc"], r["judge_score"], r["tfa_pct"] >= 0.70, r["tfa_pct"] <= 0.30
        if c == 1 and hi and j <= 5: return "A"
        if c == 1 and lo and j >= 8: return "B"
        if c == 1 and j <= 4: return "C"
        if c == 1 and hi and j >= 8: return "D"
        if c == 0 and j >= 6: return "E"
        if c == 0 and j <= 2: return "F"
        return None
    buckets = collections.defaultdict(list)
    for r in R:
        cl = cell(r)
        if cl: buckets[cl].append(r)
    for cl, cap in CAPS.items():
        pick = random.sample(buckets[cl], min(cap, len(buckets[cl])))
        for r in pick:
            ga = str(gold_ans(r, dk))
            rows.append(dict(
                id=f"{ds[:4]}-{cl}-{r['problem_id']}-{r['model'].split('/')[-1][:8]}",
                cell=cl, cell_desc=CELL_DESC[cl], dataset=ds, model=r["model"].split("/")[-1],
                tfa=round(r["tfa_argmax"], 3), judge=r["judge_score"], correct=r["cc"],
                question=texify(r["question"], ds), gold_solution=texify(r["gold_solution"], ds),
                gold_answer=ga, gold_answer_disp=(ga if ds == "GSM8K" else "\\(" + ga + "\\)"),
                trace=texify(r["free_gen"], ds)))

random.shuffle(rows)   # present in mixed order
for i, r in enumerate(rows): r["order"] = i + 1

with open(f"{OUTDIR}/traces_to_label.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
cols = ["order", "id", "dataset", "model", "cell", "cell_desc", "correct", "tfa", "judge",
        "gold_answer", "question", "gold_solution", "trace"]
with open(f"{OUTDIR}/traces_to_label.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
    for r in rows: w.writerow(r)

print(f"selected {len(rows)} traces")
cnt = collections.Counter((r["dataset"], r["cell"]) for r in rows)
for k in sorted(cnt): print(f"  {k[0]:9s} cell {k[1]}: {cnt[k]}")

# ---- self-contained HTML labeler: MathJax rendering, cell shown per card, CSV/JSON export ----
DATA = json.dumps(rows)
HTML = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>TFA trace labeling</title>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" id=MathJax-script async></script>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--card:#f7f7f8;--bd:#e2e2e5;--acc:#3452b5;--warn:#b5462f}
@media(prefers-color-scheme:dark){:root{--bg:#16171a;--fg:#e8e8ea;--mut:#9a9aa2;--card:#1f2024;--bd:#33343a;--acc:#8ea2ea;--warn:#e08a70}}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--bd);padding:10px 16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;z-index:9}
header b{font-size:16px}#prog{color:var(--mut)}
button{font:inherit;padding:7px 13px;border:1px solid var(--bd);border-radius:8px;background:var(--acc);color:#fff;cursor:pointer}
button.sec{background:transparent;color:var(--fg)}
main{max-width:960px;margin:0 auto;padding:16px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:18px;margin:0 0 26px}
.tag{display:inline-block;font-size:12px;color:var(--mut);border:1px solid var(--bd);border-radius:999px;padding:1px 9px;margin:0 6px 4px 0}
.cell{font-size:13px;font-weight:600;color:var(--warn);margin:6px 0 2px}
.scores{color:var(--mut);font-size:12.5px}
.lbl{font-size:12px;letter-spacing:.03em;text-transform:uppercase;color:var(--mut);margin:14px 0 4px}
.txt{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--bg);border:1px solid var(--bd);border-radius:8px;padding:11px 13px;margin:0;line-height:1.55;max-height:460px;overflow:auto}
.rub{margin-top:14px;border-top:1px dashed var(--bd);padding-top:12px}
.q{margin:10px 0}.q>span{display:block;font-weight:600;margin-bottom:4px}
.opts label{display:inline-block;margin:0 12px 4px 0;font-weight:400}
textarea{width:100%;min-height:52px;background:var(--bg);color:var(--fg);border:1px solid var(--bd);border-radius:8px;padding:8px;font:inherit}
body.blind .meta{display:none}
</style></head><body>
<header><b>Reasoning-trace labeling</b><span id=prog></span>
<label class=scores><input type=checkbox id=blind> blind mode (hide cell &amp; scores)</label>
<span style=flex:1></span>
<button class=sec onclick=exp('json')>Download JSON</button>
<button onclick=exp('csv')>Download CSV</button></header>
<main id=app></main>
<script>
const DATA=__DATA__;
const KEY='tfa_labels_v1';
const L=JSON.parse(localStorage.getItem(KEY)||'{}');
const Q=[
 ['answer_correct','Final answer correct?',['yes','no','unsure']],
 ['steps_valid','Are the individual steps valid?',['all valid','minor slip','major error']],
 ['complete','Reasoning complete (no unjustified leaps)?',['complete','minor gap','major gap']],
 ['quality','Overall reasoning quality (0 worst to 10 best)',['0','1','2','3','4','5','6','7','8','9','10']],
 ['lucky','Lucky-correct? (right answer, invalid/incomplete reasoning)',['no','yes','n/a']],
];
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function draw(){
 const app=document.getElementById('app');app.innerHTML='';
 DATA.forEach(d=>{
  const done=L[d.id]&&L[d.id].quality!=null;
  const c=document.createElement('div');c.className='card';
  c.innerHTML=`<div><span class=tag>#${d.order}</span><span class=tag>${d.dataset}</span>
   <span class="tag meta">${d.model}</span>
   ${done?'<span class=tag style="border-color:var(--acc);color:var(--acc)">labeled</span>':''}
   <div class="cell meta">Cell ${d.cell}: ${esc(d.cell_desc)}</div>
   <div class="scores meta">TFA=${d.tfa} &middot; judge=${d.judge}/10 &middot; answer ${d.correct?'correct':'wrong'} (by checker)</div>
   <div class=lbl>Problem</div><div class=txt>${esc(d.question)}</div>
   <div class=lbl>Reference solution (gold, answer = ${d.gold_answer_disp?esc(d.gold_answer_disp):esc(d.gold_answer)})</div><div class=txt>${esc(d.gold_solution)}</div>
   <div class=lbl>Model trace to grade</div><div class=txt>${esc(d.trace)}</div>
   <div class=rub></div></div>`;
  const rub=c.querySelector('.rub');
  Q.forEach(([k,q,opts])=>{
   const qd=document.createElement('div');qd.className='q';
   qd.innerHTML=`<span>${q}</span><div class=opts>`+opts.map(o=>
     `<label><input type=radio name="${d.id}__${k}" value="${o}" ${((L[d.id]||{})[k]===o)?'checked':''}> ${o}</label>`).join('')+`</div>`;
   rub.appendChild(qd);
  });
  const nt=document.createElement('div');nt.className='q';
  nt.innerHTML=`<span>Notes (what is wrong/right, why)</span><textarea data-id="${d.id}">${esc((L[d.id]||{}).notes||'')}</textarea>`;
  rub.appendChild(nt);
  app.appendChild(c);
 });
 document.querySelectorAll('input[type=radio]').forEach(r=>r.onchange=e=>{
   const [id,k]=e.target.name.split('__');(L[id]=L[id]||{})[k]=e.target.value;localStorage.setItem(KEY,JSON.stringify(L));prog();});
 document.querySelectorAll('textarea').forEach(t=>t.oninput=e=>{
   const id=e.target.dataset.id;(L[id]=L[id]||{}).notes=e.target.value;localStorage.setItem(KEY,JSON.stringify(L));});
 prog();mj();
}
function prog(){const n=DATA.filter(d=>L[d.id]&&L[d.id].quality!=null).length;
 document.getElementById('prog').textContent=`${n} / ${DATA.length} labeled`;}
function mj(){if(window.MathJax&&MathJax.typesetPromise){MathJax.typesetPromise();}else{setTimeout(mj,200);}}
document.getElementById('blind').onchange=e=>document.body.classList.toggle('blind',e.target.checked);
function exp(fmt){
 const rows=DATA.map(d=>Object.assign({id:d.id,order:d.order,dataset:d.dataset,model:d.model,cell:d.cell,tfa:d.tfa,judge:d.judge,machine_correct:d.correct},L[d.id]||{}));
 let blob;
 if(fmt==='json'){blob=new Blob([JSON.stringify(rows,null,2)],{type:'application/json'});}
 else{const keys=['id','order','dataset','model','cell','tfa','judge','machine_correct','answer_correct','steps_valid','complete','quality','lucky','notes'];
  const q=v=>('"'+String(v==null?'':v).replace(/"/g,'""')+'"');
  blob=new Blob([keys.join(',')+'\\n'+rows.map(r=>keys.map(k=>q(r[k])).join(',')).join('\\n')],{type:'text/csv'});}
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='tfa_human_labels.'+fmt;a.click();
}
draw();
</script></body></html>"""
open(f"{OUTDIR}/label.html", "w").write(HTML.replace("__DATA__", DATA))
print(f"wrote {OUTDIR}/label.html , traces_to_label.jsonl , traces_to_label.csv")
