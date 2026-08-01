# Build the TFA story deck (self-contained, data-URI figures). Story: motivation -> model-level TFA by
# progressive generalization (family -> judge -> dataset/saturation -> agents) -> item-level failure + why +
# variants tried -> process rollout -> conclusions -> next steps.
import base64, pathlib
FIGDIR = pathlib.Path("paper/figs")
def datauri(fn): return "data:image/png;base64," + base64.b64encode((FIGDIR/fn).read_bytes()).decode()
IMG = {k: datauri(v) for k, v in {
 "f1":"fig1_model_level.png","f6":"fig7_mechanism.png","judge":"fig_judge.png","f3":"fig3_saturation.png",
 "f5":"fig6_cross_family.png","f7":"fig10_reconciliation.png","f9":"fig8_agentic.png","f2":"fig2_difficulty_gradient.png",
 "f10":"fig9_mechanism.png","var":"fig_variants.png","f8":"fig5_rollout_completer_curve.png",
}.items()}
def fig(k,cap): return f'<figure class="fig"><img src="{IMG[k]}" alt="{cap}"/><figcaption>{cap}</figcaption></figure>'
def chips(*cs): return '<div class="chips">'+''.join(f'<div class="chip"><span class="cn">{n}</span><span class="cl">{l}</span></div>' for n,l in cs)+'</div>'
S=[]
def slide(kick,title,body,cls=""): S.append(f'<section class="slide {cls}"><div class="wrap"><div class="kick">{kick}</div><h2>{title}</h2>{body}</div></section>')

# 1 title
S.append('''<section class="slide title"><div class="wrap">
 <div class="kick">Stanford · Koyejo Group · judge-free evaluation</div>
 <h1>When can a judge-free signal<br><span class="hl">grade reasoning?</span></h1>
 <p class="lede">Teacher-Forced Accuracy (TFA), tested by progressive generalization: within a family, across
 families, across datasets, and into agents, then flipped from ranking models to grading solutions.</p>
 <div class="meta">17 models · 7 families · 8 datasets (math · olympiad · code) · 2 frontier judges · + rollout process value · + agentic</div>
 <div class="hint">scroll or press → to advance</div></div></section>''')

# 2 motivation
slide("Motivation","The evaluation regress",
 '''<p>In the agentic era a model produces a proof, plan, tool trajectory, or code patch. Exact-match is too
 brittle; an <b>LLM judge adds another model whose reliability must itself be validated</b>. To trust the judge
 you need human labels or an oracle, an evaluation regress.</p>
 <div class="def"><b>Central question.</b> When a gold reasoning trace exists, can a <b>deterministic, judge-free</b>
 signal do part of the job? <b>TFA</b> conditions the model on the gold prefix and asks whether it predicts each
 next token, local agreement with a trusted path. No judge, no rubric, one forward pass.</div>
 <p class="q">It might penalize valid alternate proofs, favor reference style, or under-score compressed and
 tool-using solutions. Those failure modes are <b>measurable</b>, which is exactly what makes it worth testing.</p>''')

# 3 roadmap
slide("How we test it","Two questions, tested by progressive generalization",
 '''<div class="cols"><div>
   <h3 class="g">Q1 &middot; can it rank models?</h3>
   <p>Compare mean TFA to <b>accuracy</b> (judge-free), then push it outward:</p>
   <ol><li>within one model family (Qwen)</li><li>across families</li>
   <li>across datasets (easy &rarr; hard)</li><li>into agents</li></ol>
   <p style="font-size:.85rem;color:var(--mut);margin-top:6px">All against <b>accuracy</b> (judge-free); robustness to the choice of judge is in the appendix.</p></div>
   <div><h3 class="p">Q2 &middot; can it grade one solution?</h3>
   <p>Then the harder test: does TFA tell a good solution from a bad one? We show it <b>fails</b>, prove
   <b>why</b>, and show <b>everything we tried</b> to fix it.</p>
   <h3>Then</h3><p>A costlier signal that <i>does</i> grade (process rollout), and the path forward.</p></div></div>''')

# 4 within family
slide("Q1 &middot; step 1 &middot; within a family","TFA tracks accuracy within the Qwen ladder",
 chips(("+0.6 to +1.0","mean TFA vs accuracy, within Qwen"),("judge-free","compared to accuracy, not a judge"))+
 '<p>First, the purest test: does mean TFA order one family by <b>accuracy</b> (no judge involved)? Yes, and it is <b>strongest on the hardest data</b>, where weak models have the most room to separate.</p>'+
 fig("f1","Figure 1. Model-level: mean TFA rises with accuracy across the Qwen ladder on every dataset.")+
 '<div class="take">It ranks the family by skill. Does that survive beyond Qwen?</div>')

# 5 beyond family
slide("Q1 &middot; step 2 &middot; beyond one family","It holds across families, on hard math",
 '''<p>Add Mistral, Phi, OLMo, and math-specialized models. On hard math (Putnam, MATH) every family's
 size-ladder points <b class="g">up and to the right</b>: a bigger, better model predicts the gold better, so it
 holds <b>across families</b>, not just Qwen. On easy, saturated data (GSM8K) some families <b class="r">invert</b>:
 Phi's and OLMo's stronger models solve more but answer in a fuller, labeled style than the short, terse gold, so
 they predict it <b>worse</b> and the arrow points down. There the gold is so stylized that family <b>style</b>,
 not skill, drives the score.</p>'''+
 fig("f6","Figure 6. Family size-ladders: aligned on hard math, scattering and inverting as accuracy saturates.")+
 '<div class="take">Whether it holds or inverts depends on the data, which points straight to saturation, next.</div>')

# 7 saturation proof
slide("Q1 &middot; step 3 &middot; beyond one dataset","Why it saturates on easy data and holds on hard",
 chips(("~0.03","TFA range on GSM8K (easy)"),("~0.08","TFA range on Putnam (hard)"))+
 '<p>The proof is saturation. On easy, near-ceiling data the whole ladder is squeezed into a tiny TFA band, so there is no room to separate models; on hard data the range widens. TFA\'s discriminating power is a direct function of how far the reference pushes models from ceiling.</p>'+
 fig("f3","Figure 3. TFA compresses on easy data and spreads out on hard data.")+
 '<div class="take">So on saturated data a family style-offset can dominate, and the ranking can even invert.</div>')

# 8 boundary
slide("Q1 &middot; step 3 &middot; the boundary","Strong on hard math, weak on code, <span class='a'>negative</span> on saturated GSM8K",
 chips(("+0.86","Omni-MATH"),("+0.60","Putnam"),("+0.43","code"),("&minus;0.37","GSM8K"))+
 '<p>Pooling all families across all eight datasets gives one boundary map. It holds on hard, constrained references, weakens on code (many valid programs), and <b class="a">inverts</b> on saturated grade-school math.</p>'+
 fig("f5","Figure 5. Cross-family boundary: strong on hard/olympiad math, weak on code, negative on saturated GSM8K.")+
 '<div class="take">One rule: TFA ranks by quality only when the reference is a long, constrained trace and models share its style.</div>')

# 9 reconciliation
slide("Q1 &middot; step 3 &middot; reconciliation","This reconciles the original TFA paper's 0.66",
 '<p>Putnam-AXIOM reported TFA-vs-accuracy at <b>0.66 (MATH)</b> and <b>0.52 (Putnam)</b>, below our within-family +0.9 to +1.0. Not a disagreement: their numbers fall out once you match <b>the metric</b> (Kendall tau, the honest choice for a handful of models) and <b>the model set</b>, shown here across all four correlation measures.</p>'+
 '<p style="font-size:.98rem"><b class="r">All models</b> = the full set <b>including the math-specialized outliers</b> (Qwen-Math, DeepSeek-Math, Mathstral), which reproduce the gold style beyond their solving skill and drag the pooled number down toward their 0.66 / 0.52. <b class="g">General families only</b> = the general-purpose families (Qwen, Mistral, Phi, OLMo) with those outliers dropped, which recovers +0.86 / +0.88. Their headline 0.66 is simply our Kendall value on the full set.</p>'+
 fig("f7","Figure 7. Our correlation under four metrics x two model sets (all models vs general families only) against the reported 0.66 / 0.52.")+
 '<div class="take">Model-level reproduces exactly; their untested item-level claim (next) does not.</div>')

# 10 agents
slide("Q1 &middot; step 4 &middot; to agents","The whole boundary reaches coding agents",
 chips(("+1.00","within Qwen-Coder (by scale)"),("+0.00","across four coder families"))+
 '<p>On SWE-bench, teacher-forcing the human gold patch ranks one coder family\'s sizes by skill <b class="g">perfectly</b>, but says <b class="r">nothing</b> across families. CodeLlama reproduces the gold-patch style best while writing some of the worst code, the repository-patch version of the GSM8K offset.</p>'+
 fig("f9","Figure 9. SWE-bench patch-TFA: within-family +1.00, cross-family +0.00, CodeLlama the high-TFA/low-skill outlier.")+
 '<div class="take">Not &ldquo;TFA works on agents,&rdquo; but &ldquo;the boundary does.&rdquo;</div>')

# 11 part 2 item-level
slide("Q2 &middot; grading individual solutions","Now the harder question: can TFA grade one solution?",
 chips(("&approx; 0","MATH (per-item, beyond correctness)"),("+0.12","GSM8K"),("+0.22","Putnam"))+
 '<p>Controlling for correctness, the per-item TFA-vs-judge signal is <b>zero on MATH</b>, small on GSM8K, and only +0.22 on the hardest math. The small signals are <b>real</b> (they survive label-noise and contamination controls) but explain under 5% of variance, far too little to replace a judge.</p>'+
 fig("f2","Figure 2. Per-item TFA-vs-judge (controlling for correctness): ~0 on MATH, small on GSM8K, largest on Putnam.")+
 '<div class="take">A leaderboard, not a grader. Why?</div>')

# 12 why
slide("Q2 &middot; why, with proof","Because per-item TFA is 89-96% reference nuisance",
 chips(("89-96%","reference nuisance"),("4-11%","left for competence"))+
 '<p>Write per-item TFA as <b class="g">competence</b> plus a <b class="a">reference-predictability nuisance</b> (how easy this particular gold is to reproduce, the same for every model) plus a <b class="r">style offset</b>.</p>'+
 '<div class="def" style="font-size:.96rem"><b>How the nuisance is measured.</b> Take the model &times; item grid of per-item TFA (the 5-model Qwen ladder) and subtract the per-model mean (each model minus its own average), so only item-to-item variation is left. The share of that variation which is <b>identical across all models</b> (the item main effect, a one-way ANOVA on the reference) is the nuisance: <b>89-96%</b> on every dataset. The other 4-11% is all that remains for competence. Reproducible via <span style="font-family:ui-monospace,Menlo,monospace;font-size:.9em">scripts/variance_decomp.py</span>.</div>'+
 '<p>Because it is the same for every model, the nuisance <b>cancels</b> when you average over items (ranking works), but <b>buries</b> the competence signal within a single item (grading fails).</p>'+
 fig("f10","Figure 10. Variance decomposition: per-item TFA is 89-96% a model-invariant reference nuisance.")+
 '<div class="take">This predicts no reweighting of TFA can recover the signal. So we tried them all.</div>')

# 13a the fixes explained
slide("Q2 &middot; what we tried &middot; the fixes","Seven cheap fixes, each removing one nuisance",
 '<p>If the per-item quality signal is merely <i>buried</i> under the reference nuisance, then reweighting or contrasting TFA should dig it out. Each fix targets one coordinate of that nuisance.</p>'+
 '''<div class="cols"><div>
   <p><b class="a">content-token TFA</b> &mdash; mask formatting and LaTeX glue; score only content tokens.</p>
   <p><b class="a">IDF-weighted TFA</b> &mdash; up-weight corpus-rare gold tokens, down-weight boilerplate.</p>
   <p><b class="a">surprisal-weighted TFA</b> &mdash; up-weight surprising, non-formulaic gold tokens.</p>
   <p><b class="a">TFA-logprob / BPC</b> &mdash; a soft gold-token log-probability instead of hard argmax match.</p></div>
   <div>
   <p><b class="p">step-shuffle contrast</b> &mdash; TFA(gold) minus TFA(gold with its reasoning lines reordered).</p>
   <p><b class="p">answer-swap contrast</b> &mdash; TFA(gold) minus TFA(gold with a wrong final answer).</p>
   <p><b class="g">multi-reference TFA</b> &mdash; the max TFA over several verified gold solutions.</p>
   <p style="color:var(--mut);font-size:.92rem">Each peels off one coordinate: glue, frequency, style, path order, or length.</p></div></div>'''+
 '<div class="take">If the signal were only masked, one of these should uncover it.</div>')

# 13 variants
slide("Q2 &middot; what we tried &middot; the results","Every cheap fix fails",
 '<p>We ran all seven. <b>None recovers a per-item quality signal:</b> the correlations cluster at zero, and the reweighting variants come out slightly <b>negative</b> (the surprising, hard-to-predict tokens are exactly the ones good models also miss). Structurally, each fix strips just one coordinate of the nuisance and the leftover is <i>still</i> nuisance, not competence, the signature of a signal that is <b>absent, not merely masked</b>.</p>'+
 '<p style="font-size:.98rem"><b>One cautionary tale.</b> The answer-swap contrast first looked like a real win at +0.35. It was a length artifact: because the corruption changed only the final-answer token, the score collapsed to &ldquo;predicts the right answer, divided by solution length.&rdquo; Controlling for length dropped it to zero and we retracted it, now a standing rule: <b>no item-level win is believed until it survives length and difficulty controls.</b></p>'+
 fig("var","The results: item-level ρ for each cheap fix. None recovers a per-item quality signal.")+
 '<div class="take">The signal is <i>absent</i>, not masked. TFA cannot grade an individual solution.</div>')

# 14 rollout
slide("Q3 &middot; a signal that does grade","Rollout <span class='g'>process value</span> grades solutions, at a cost",
 chips(("+0.43","process value vs judge"),("+0.19","sound vs lucky correct"),("~100&times;","the cost of TFA"))+
 '<p>Stop anchoring on a gold trace, measure the model\'s <b>own</b> reasoning: truncate a solution, let a fixed completer finish it, and score whether it still reaches the right answer. This grades where TFA cannot, even separating <b>sound</b> from <b>lucky</b> correct answers, but only at a mid-strength completer and at ~100x the cost.</p>'+
 fig("f8","Figure 8. Rollout value vs the judge across completer strengths: a mid-strength 14B completer is the sweet spot.")+
 '<div class="take">A soft verifier, not a cheap judge. The open problem is a cheap, reference-free version.</div>')

# 15 conclusions
S.append('''<section class="slide concl"><div class="wrap"><div class="kick">Conclusions</div>
 <h2>TL;DR and what is new</h2>
 <div class="cols"><div><h3>The one idea</h3>
   <p><b>TFA measures agreement with the reference's <span class="p">style</span>, not reasoning
   <span class="g">quality</span></b>, and everything follows.</p>
   <ul><li><b>Model ranker:</b> excellent within a family and on hard references; noisy on code; <b>inverts</b> on saturated data; holds across judges.</li>
   <li><b>Per-solution grader:</b> essentially fails (&approx;0 on MATH); no variant fixes it.</li>
   <li><b>Rollout process value</b> does grade, weakly, at ~100&times; the cost.</li>
   <li>The boundary <b>reaches agents</b> (SWE-bench, tool-calls).</li></ul></div>
   <div class="new"><h3>Our unique contributions</h3>
   <ol><li><b>First test</b> of TFA's grading claim (prior work assumed it) &mdash; it fails.</li>
   <li><b>The mechanism:</b> the 89-96% nuisance decomposition explaining ranking-works / grading-fails.</li>
   <li><b>The boundary map</b> across families, judges, and datasets, including the GSM8K sign-flip.</li>
   <li><b>Reconciliation</b> of the original 0.66 as a metric-and-model-set effect.</li>
   <li><b>Extension to agents:</b> the same within/cross-family boundary on code patches and tool calls.</li></ol></div></div></div></section>''')

# 16 next steps
S.append('''<section class="slide fwd"><div class="wrap"><div class="kick">Path forward · proposal to Sanmi</div>
 <h2>Where judge-free evaluation goes next</h2>
 <div class="cols"><div><h3>Directions to choose between</h3>
   <ul><li><b>LLMs vs agents:</b> deepen the math/code boundary, or push into open-ended agents.</li>
   <li><b>TFA alternatives:</b> multi-reference (outcome-gated), self-consistency-anchored, per-step signals.</li>
   <li><b>The positive bet:</b> reference-free <b>process value</b> grounded in an environment's own success oracle, where no gold trace exists.</li></ul>
   <div class="warn"><b>Hard constraint.</b> Frontier <b>API models expose no token log-probabilities</b>, so TFA
   (any teacher-forcing signal) cannot run on them, only open weights. This caps TFA's reach and pushes toward
   output-only and process-based signals.</div></div>
   <div><h3>Deep-research the scalable-oversight toolkit</h3>
   <p>The setting is weak-to-strong supervision: overseeing models whose outputs we cannot fully verify.</p>
   <ul><li><b>Weak-to-strong supervision</b></li><li><b>Debate</b> and comparative judging</li>
   <li><b>Process rewards / rollout value</b> (Math-Shepherd, OmegaPRM), audited for reward hacking</li>
   <li><b>Consistency-vs-truth</b> guardrails throughout</li></ul>
   <div class="take" style="margin-top:12px">Our result is the map: a reference-anchored cheap signal is safe only
   within a family; elsewhere it rewards style. For frontier-API and agentic settings, go output-grounded and reference-free.</div></div></div></section>''')

# 17 appendix: judge robustness
slide("Appendix &middot; robustness to the judge","Not one judge's opinion",
 chips(("0.75-0.94","inter-judge agreement (ρ)"),("2 families","gpt-5.2 &amp; Opus 4.8"))+
 "<p>The model-ranking story above is judge-free (TFA vs <b>accuracy</b>). The <i>item-level</i> results in Part 2 are the only judge-defined ones, so we re-graded the three anchor datasets with a second frontier judge from a different family (Claude Opus 4.8), same rubric. Same pattern: the MATH null stays null and the small GSM8K and Putnam signals replicate, with CIs still excluding zero.</p>"+
 fig("judge","Item-level partial ρ under two judges (gpt-5.2 vs Claude Opus 4.8): the same conclusions under both.")+
 "<div class='take'>The conclusions are properties of TFA, not of the particular judge we appointed as ground truth.</div>")

STYLE='''<style>
:root{--bg:#f6f7f9;--panel:#fff;--ink:#181b20;--mut:#5b6470;--line:#e2e5ea;--accent:#2b5c8a;--g:#2f8f4e;--a:#c07d15;--p:#7d54c9;--r:#c44e52;--shadow:0 1px 3px rgba(20,25,35,.08),0 8px 24px rgba(20,25,35,.06);}
@media (prefers-color-scheme:dark){:root{--bg:#0f1216;--panel:#171b21;--ink:#e9ecf1;--mut:#9aa3af;--line:#262b33;--accent:#6ea8dc;--g:#5ec97e;--a:#e0a94a;--p:#a988e6;--r:#e0777b;--shadow:0 1px 3px rgba(0,0,0,.4),0 10px 30px rgba(0,0,0,.35);}}
:root[data-theme="light"]{--bg:#f6f7f9;--panel:#fff;--ink:#181b20;--mut:#5b6470;--line:#e2e5ea;--accent:#2b5c8a;--g:#2f8f4e;--a:#c07d15;--p:#7d54c9;--r:#c44e52;--shadow:0 1px 3px rgba(20,25,35,.08),0 8px 24px rgba(20,25,35,.06);}
:root[data-theme="dark"]{--bg:#0f1216;--panel:#171b21;--ink:#e9ecf1;--mut:#9aa3af;--line:#262b33;--accent:#6ea8dc;--g:#5ec97e;--a:#e0a94a;--p:#a988e6;--r:#e0777b;--shadow:0 1px 3px rgba(0,0,0,.4),0 10px 30px rgba(0,0,0,.35);}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.55}
.deck{height:100vh;overflow-y:scroll;scroll-snap-type:y mandatory}
.slide{min-height:100vh;scroll-snap-align:start;display:flex;align-items:center;padding:64px 6vw 60px;border-bottom:1px solid var(--line);position:relative}
.wrap{width:100%;max-width:1060px;margin:0 auto}
.kick{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700;margin-bottom:12px}
h1{font-size:clamp(2.4rem,5.2vw,4rem);line-height:1.02;letter-spacing:-.02em;margin:.1em 0 .35em;font-weight:800;text-wrap:balance}
h2{font-size:clamp(1.6rem,3.2vw,2.4rem);line-height:1.07;letter-spacing:-.015em;margin:0 0 .45em;font-weight:800;text-wrap:balance}
h3{font-size:1rem;margin:.9em 0 .3em;font-weight:700}
p{font-size:1.04rem;max-width:72ch;margin:.45em 0}
ul,ol{font-size:1.02rem;max-width:72ch;padding-left:1.2em;margin:.35em 0}li{margin:.28em 0}
b,strong{font-weight:700}.g{color:var(--g);font-weight:700}.a{color:var(--a);font-weight:700}.p{color:var(--p);font-weight:700}.r{color:var(--r);font-weight:700}
.title{background:radial-gradient(1200px 500px at 15% -10%,color-mix(in srgb,var(--accent) 12%,transparent),transparent)}.title .hl{color:var(--accent)}
.lede{font-size:1.28rem;max-width:64ch;margin:.4em 0 1.1em}
.meta{font-family:ui-monospace,Menlo,monospace;font-size:.8rem;color:var(--mut);border-top:1px solid var(--line);padding-top:14px;max-width:70ch}
.hint{position:absolute;bottom:24px;left:6vw;font-size:.8rem;color:var(--mut)}
.def{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:10px;padding:13px 17px;margin:14px 0;box-shadow:var(--shadow);font-size:1.01rem;max-width:80ch}
.q{font-size:1.1rem;max-width:76ch}
.take{margin-top:16px;border-left:3px solid var(--accent);padding:5px 0 5px 15px;font-size:1.1rem;font-weight:600;max-width:76ch}
.chips{display:flex;gap:11px;flex-wrap:wrap;margin:4px 0 12px}
.chip{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:9px 13px;box-shadow:var(--shadow);min-width:110px}
.cn{display:block;font-family:ui-monospace,Menlo,monospace;font-size:1.45rem;font-weight:800;color:var(--accent);letter-spacing:-.01em}
.cl{display:block;font-size:.76rem;color:var(--mut);margin-top:2px}
.fig{margin:14px 0 4px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:11px;box-shadow:var(--shadow);overflow-x:auto}
.fig img{display:block;width:100%;max-width:100%;height:auto;border-radius:6px}
.fig figcaption{font-size:.8rem;color:var(--mut);margin-top:7px;line-height:1.4}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:30px}.cols p,.cols ul,.cols ol{font-size:1rem}
.new{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:4px 20px 14px;box-shadow:var(--shadow)}
.warn{background:color-mix(in srgb,var(--r) 9%,var(--panel));border:1px solid color-mix(in srgb,var(--r) 30%,var(--line));border-radius:10px;padding:11px 15px;margin-top:14px;font-size:.98rem}
.rail{position:fixed;top:0;left:0;height:3px;background:var(--accent);width:0;z-index:50;transition:width .15s}
.counter{position:fixed;bottom:16px;right:20px;font-family:ui-monospace,Menlo,monospace;font-size:.78rem;color:var(--mut);background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:4px 11px;z-index:50;box-shadow:var(--shadow)}
.toggle{position:fixed;top:12px;right:16px;z-index:50;background:var(--panel);border:1px solid var(--line);color:var(--mut);border-radius:20px;padding:5px 11px;font-size:.76rem;cursor:pointer;box-shadow:var(--shadow)}
@media (max-width:760px){.cols{grid-template-columns:1fr;gap:6px}.slide{padding:56px 6vw 52px}}
</style>'''
SCRIPT='''<script>
const deck=document.querySelector('.deck'),slides=[...document.querySelectorAll('.slide')];
const rail=document.querySelector('.rail'),counter=document.querySelector('.counter');
function idx(){let b=0,bd=1e9;slides.forEach((s,i)=>{const d=Math.abs(s.getBoundingClientRect().top);if(d<bd){bd=d;b=i}});return b;}
function upd(){counter.textContent=(idx()+1)+' / '+slides.length;rail.style.width=(deck.scrollTop/(deck.scrollHeight-deck.clientHeight)*100)+'%';}
deck.addEventListener('scroll',upd);upd();
function go(n){const i=Math.max(0,Math.min(slides.length-1,idx()+n));slides[i].scrollIntoView({behavior:'smooth'});}
addEventListener('keydown',e=>{if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){e.preventDefault();go(1);}
 if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();go(-1);}
 if(e.key==='Home')slides[0].scrollIntoView({behavior:'smooth'});if(e.key==='End')slides[slides.length-1].scrollIntoView({behavior:'smooth'});});
document.querySelector('.toggle').addEventListener('click',()=>{const r=document.documentElement;
 const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
 r.setAttribute('data-theme',cur==='dark'?'light':'dark');});
</script>'''
html=STYLE+'<div class="rail"></div><button class="toggle">◐ theme</button><div class="counter"></div><div class="deck">'+"".join(S)+'</div>'+SCRIPT
out="paper/slides.html"
open(out,"w").write(html); print("wrote",out,"slides:",len(S),"bytes:",len(html))
