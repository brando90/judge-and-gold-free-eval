# Build a self-contained, CSP-safe Artifact page for labeling reasoning traces.
# Math is pre-rendered to native MathML (no JS math library, no CDN). Output is BODY-ONLY
# content (no doctype/html/head/body) because the Artifact runtime wraps it in a skeleton.
import json, re, html as H
import latex2mathml.converter as C

# Segments to convert: inline \(..\), display \[..\], and bare multi-line environments
# (align/aligned/gather/equation, starred or not) that sit in plain text without $ delimiters.
SEG = re.compile(
    r"\\\((.+?)\\\)"                                   # group 1: inline
    r"|\\\[(.+?)\\\]"                                  # group 2: display
    r"|(\\begin\{(?:align|aligned|gather|equation|multline|eqnarray)\*?\}.+?\\end\{(?:align|aligned|gather|equation|multline|eqnarray)\*?\})",  # group 3: env
    re.S)

def to_html(t):
    # t is already texified (MATH math wrapped as \(..\) / \[..\]; GSM8K left as plain text).
    out, i = [], 0
    for m in SEG.finditer(t):
        out.append(H.escape(t[i:m.start()]))
        latex = m.group(1) or m.group(2) or m.group(3)
        display = m.group(1) is None      # display for \[..\] and environments, inline for \(..\)
        try:
            ml = C.convert(latex)
            if display:
                ml = ml.replace("<math ", '<math display="block" ', 1)
            out.append(ml)
        except Exception:
            out.append(H.escape(m.group(0)))
        i = m.end()
    out.append(H.escape(t[i:]))
    return "".join(out)

rows = [json.loads(l) for l in open("human_eval/traces_to_label.jsonl")]

Q = [
    ("answer_correct", "Final answer correct?", ["yes", "no", "unsure"]),
    ("steps_valid", "Are the individual steps valid?", ["all valid", "minor slip", "major error"]),
    ("complete", "Reasoning complete (no unjustified leaps)?", ["complete", "minor gap", "major gap"]),
    ("quality", "Overall reasoning quality (0 worst to 10 best)", [str(i) for i in range(11)]),
    ("lucky", "Lucky-correct? (right answer, invalid/incomplete reasoning)", ["no", "yes", "n/a"]),
]

def card(d):
    ga = d.get("gold_answer_disp") or d["gold_answer"]
    parts = [f'<article class=card data-id="{H.escape(d["id"])}" data-order="{d["order"]}" '
             f'data-dataset="{d["dataset"]}" data-model="{H.escape(d["model"])}" data-cell="{d["cell"]}" '
             f'data-tfa="{d["tfa"]}" data-judge="{d["judge"]}" data-correct="{d["correct"]}">']
    parts.append('<div class=meta>')
    parts.append(f'<span class=chip>#{d["order"]}</span><span class=chip>{d["dataset"]}</span>')
    parts.append(f'<span class="chip rev">{H.escape(d["model"])}</span>')
    parts.append('<span class="done-tag" hidden>saved</span>')
    parts.append(f'<div class="cell rev">Cell {d["cell"]}: {H.escape(d["cell_desc"])}</div>')
    verdict = "correct" if d["correct"] else "wrong"
    parts.append(f'<div class="scores rev">TFA {d["tfa"]} &middot; judge {d["judge"]}/10 &middot; '
                 f'final answer {verdict} (deterministic checker)</div>')
    parts.append('</div>')
    parts.append(f'<div class=block><div class=lbl>Problem</div><div class=body>{to_html(d["question"])}</div></div>')
    parts.append(f'<div class=block><div class=lbl>Reference solution &mdash; answer {to_html(ga)}</div>'
                 f'<div class=body>{to_html(d["gold_solution"])}</div></div>')
    parts.append(f'<div class=block><div class=lbl>Model trace to grade</div>'
                 f'<div class=body>{to_html(d["trace"])}</div></div>')
    parts.append('<div class=rubric>')
    for k, q, opts in Q:
        parts.append(f'<div class=q><span class=qt>{H.escape(q)}</span><div class=opts>')
        for o in opts:
            nm = f'{d["id"]}__{k}'
            parts.append(f'<label><input type=radio name="{nm}" value="{o}"> {o}</label>')
        parts.append('</div></div>')
    parts.append(f'<div class=q><span class=qt>Notes (what is wrong or right, and why)</span>'
                 f'<textarea data-note="{H.escape(d["id"])}" rows=2></textarea></div>')
    parts.append('</div></article>')
    return "".join(parts)

CARDS = "\n".join(card(d) for d in rows)

BODY = """<style>
:root{
  --bg:#fbfbfc; --card:#f3f4f7; --fg:#1b1d21; --mut:#6b6f77; --bd:#e2e4ea;
  --acc:#3a52c4; --warn:#a85a1c; --good:#2f7d55; --field:#ffffff;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#141519; --card:#1c1e24; --fg:#e8eaef; --mut:#989ca6; --bd:#2f323a;
  --acc:#96a6f2; --warn:#dda06a; --good:#6cc295; --field:#101116;
}}
:root[data-theme="light"]{--bg:#fbfbfc;--card:#f3f4f7;--fg:#1b1d21;--mut:#6b6f77;--bd:#e2e4ea;--acc:#3a52c4;--warn:#a85a1c;--good:#2f7d55;--field:#ffffff;}
:root[data-theme="dark"]{--bg:#141519;--card:#1c1e24;--fg:#e8eaef;--mut:#989ca6;--bd:#2f323a;--acc:#96a6f2;--warn:#dda06a;--good:#6cc295;--field:#101116;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-variant-numeric:tabular-nums;}
.wrap{max-width:900px;margin:0 auto;padding:0 18px 80px}
header{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--bd);}
.bar{max-width:900px;margin:0 auto;padding:11px 18px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.bar h1{font-size:16px;margin:0;font-weight:650;letter-spacing:-.01em}
.grow{flex:1}
#prog{color:var(--mut);font-size:13px}
input[type=text]{background:var(--field);color:var(--fg);border:1px solid var(--bd);
  border-radius:8px;padding:6px 10px;font:inherit;width:150px}
button{font:inherit;font-weight:550;padding:7px 14px;border:1px solid var(--bd);border-radius:9px;
  background:var(--acc);color:#fff;cursor:pointer}
button.ghost{background:transparent;color:var(--fg)}
button:focus-visible,input:focus-visible,label:focus-within{outline:2px solid var(--acc);outline-offset:2px}
.note{max-width:900px;margin:14px auto 0;padding:11px 15px;border:1px solid var(--bd);
  border-left:3px solid var(--acc);border-radius:9px;background:var(--card);color:var(--fg);font-size:14px}
.note b{font-weight:650}
.card{background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:20px;margin:22px 0}
.meta{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.chip{font-size:12px;color:var(--mut);border:1px solid var(--bd);border-radius:999px;padding:1px 9px}
.cell{flex-basis:100%;font-size:13px;font-weight:600;color:var(--warn);margin-top:4px}
.scores{flex-basis:100%;font-size:12.5px;color:var(--mut)}
.done-tag{font-size:12px;color:var(--good);border:1px solid var(--good);border-radius:999px;padding:1px 9px}
.block{margin-top:14px}
.lbl{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);margin-bottom:5px}
.body{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--bg);border:1px solid var(--bd);
  border-radius:9px;padding:12px 14px;line-height:1.6;max-height:430px;overflow:auto}
.body math{font-size:1.06em}
.rubric{margin-top:16px;border-top:1px dashed var(--bd);padding-top:14px}
.q{margin:11px 0}.qt{display:block;font-weight:600;margin-bottom:5px}
.opts{display:flex;gap:6px;flex-wrap:wrap}
.opts label{font-weight:400;border:1px solid var(--bd);border-radius:8px;padding:4px 10px;cursor:pointer;
  background:var(--field)}
.opts input{margin-right:5px}
.opts label:has(input:checked){border-color:var(--acc);color:var(--acc);font-weight:600}
textarea{width:100%;background:var(--field);color:var(--fg);border:1px solid var(--bd);border-radius:9px;
  padding:9px;font:inherit;resize:vertical}
body.blind .rev{display:none}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<header><div class=bar>
  <h1>Reasoning-trace labeling</h1>
  <span id=prog></span>
  <span class=grow></span>
  <input type=text id=who placeholder="your name / initials">
  <label style="font-size:13px;color:var(--mut)"><input type=checkbox id=blind> blind</label>
  <button class=ghost id=dljson>Download JSON</button>
  <button id=dlcsv>Download CSV</button>
</div></header>

<div class=wrap>
<div class=note>You are grading the <b>reasoning quality</b> of each solution, which the automatic
answer-checker cannot see. For each trace, read the problem and the reference solution, then judge the
model trace on the rubric. Your work saves in this browser as you go. <b>When you finish (or partway),
put your name above, click Download CSV, and send the file back to whoever shared this link.</b> Each
card is tagged with its category and the metric scores; tick <b>blind</b> to hide those and judge cold.</div>

__CARDS__
</div>

<script>
const KEY='tfa_label_artifact_v1';
const store=JSON.parse(localStorage.getItem(KEY)||'{}');
const who=document.getElementById('who');
who.value=store.__who||'';
function restore(){
  document.querySelectorAll('.card').forEach(c=>{
    const id=c.dataset.id, s=store[id]||{};
    c.querySelectorAll('input[type=radio]').forEach(r=>{const k=r.name.split('__')[1];if(s[k]===r.value)r.checked=true;});
    const ta=c.querySelector('textarea'); if(s.notes)ta.value=s.notes;
    mark(c);
  });
  prog();
}
function grab(c){
  const s={};
  c.querySelectorAll('input[type=radio]:checked').forEach(r=>{s[r.name.split('__')[1]]=r.value;});
  const ta=c.querySelector('textarea'); if(ta.value)s.notes=ta.value;
  return s;
}
function mark(c){const s=store[c.dataset.id]||{};c.querySelector('.done-tag').hidden=(s.quality==null);}
function save(c){store[c.dataset.id]=grab(c);store.__who=who.value;localStorage.setItem(KEY,JSON.stringify(store));mark(c);prog();}
function prog(){const n=document.querySelectorAll('.card').length;
  const d=[...document.querySelectorAll('.card')].filter(c=>(store[c.dataset.id]||{}).quality!=null).length;
  document.getElementById('prog').textContent=d+' / '+n+' labeled';}
document.querySelectorAll('.card').forEach(c=>{
  c.querySelectorAll('input[type=radio]').forEach(r=>r.addEventListener('change',()=>save(c)));
  c.querySelector('textarea').addEventListener('input',()=>save(c));
});
who.addEventListener('input',()=>{store.__who=who.value;localStorage.setItem(KEY,JSON.stringify(store));});
document.getElementById('blind').addEventListener('change',e=>document.body.classList.toggle('blind',e.target.checked));
function rowsOut(){
  return [...document.querySelectorAll('.card')].map(c=>{const s=store[c.dataset.id]||{};
    return {labeler:who.value,id:c.dataset.id,order:+c.dataset.order,dataset:c.dataset.dataset,
      model:c.dataset.model,cell:c.dataset.cell,tfa:+c.dataset.tfa,judge:+c.dataset.judge,
      machine_correct:+c.dataset.correct,answer_correct:s.answer_correct||'',steps_valid:s.steps_valid||'',
      complete:s.complete||'',quality:s.quality==null?'':s.quality,lucky:s.lucky||'',notes:s.notes||''};});
}
function showCopy(name,text){
  let p=document.getElementById('copypanel');
  if(!p){p=document.createElement('div');p.id='copypanel';
    p.style.cssText='position:fixed;inset:8% 10%;z-index:99;background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:10px;box-shadow:0 12px 40px rgba(0,0,0,.35)';
    p.innerHTML='<div style="display:flex;align-items:center;gap:10px"><b id=cpname></b><span style="flex:1"></span><button id=cpcopy>Copy to clipboard</button><button class=ghost id=cpclose>Close</button></div><div style="font-size:13px;color:var(--mut)">Direct saving was not available in this view, so here is the file content instead. Copy it, paste it into a new file with the name shown above, and send that file back.</div><textarea id=cpta style="flex:1;font:12px ui-monospace,monospace;white-space:pre"></textarea>';
    document.body.appendChild(p);
    document.getElementById('cpclose').onclick=()=>p.remove();
    document.getElementById('cpcopy').onclick=()=>{const t=document.getElementById('cpta');t.select();try{navigator.clipboard.writeText(t.value);}catch(e){document.execCommand('copy');}};
  }
  document.getElementById('cpname').textContent=name;
  const ta=document.getElementById('cpta');ta.value=text;ta.focus();ta.select();
}
async function dl(name,text,type){
  if(window.claude&&window.claude.downloads){
    let err=null;
    try{await window.claude.downloads.save({filename:name,data:text});return;}catch(e){err=e;}
    if(err&&err.code==='extension_not_enabled'){
      try{await window.claude.downloads.save({filename:name.replace(/\\.[a-z]+$/,'.txt'),data:text});return;}catch(e2){err=e2;}
    }
    if(err&&(err.code==='declined'||err.code==='rate_limited'))return;
  }
  showCopy(name,text);
}
document.getElementById('dljson').addEventListener('click',()=>dl('tfa_labels.json',JSON.stringify(rowsOut(),null,2),'application/json'));
document.getElementById('dlcsv').addEventListener('click',()=>{
  const r=rowsOut();const keys=Object.keys(r[0]);const q=v=>'"'+String(v).replace(/"/g,'""')+'"';
  const csv=keys.join(',')+String.fromCharCode(10)+r.map(x=>keys.map(k=>q(x[k])).join(',')).join(String.fromCharCode(10));
  dl('tfa_labels.csv',csv,'text/csv');});
restore();
</script>"""

open("human_eval/label_artifact_v2.html", "w").write(BODY.replace("__CARDS__", CARDS))
print("wrote human_eval/label_artifact_v2.html  (%d cards)" % len(rows))
print("size: %.0f KB" % (len(open("human_eval/label_artifact_v2.html").read()) / 1024))
