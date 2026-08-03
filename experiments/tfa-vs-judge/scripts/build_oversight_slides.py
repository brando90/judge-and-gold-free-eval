# Build the oversight story deck (self-contained, data-URI figures), same design system as the TFA deck.
# Story: what scalable oversight is -> our setup -> the mirage (label noise) -> the miner -> how judges
# really behave -> the reference mechanism -> the retraction -> self-reference -> external checks ->
# hard-to-verify domains -> the double dissociation -> the rules -> integrity ledger.
import base64, pathlib
FIGDIR = pathlib.Path("paper/figs_oversight")
def datauri(fn): return "data:image/png;base64," + base64.b64encode((FIGDIR/fn).read_bytes()).decode()
IMG = {k: datauri(k + ".png") for k in
       ["f0_method","f1_mirage","f2_miner","f3_auc","f4_typos","f5_phase","f6_families","f7_processbench","f8_rb2","f9_flips"]}
def fig(k,cap): return f'<figure class="fig"><img src="{IMG[k]}" alt="{cap}"/><figcaption>{cap}</figcaption></figure>'
def chips(*cs): return '<div class="chips">'+''.join(f'<div class="chip"><span class="cn">{n}</span><span class="cl">{l}</span></div>' for n,l in cs)+'</div>'
S=[]
def slide(kick,title,body,cls=""): S.append(f'<section class="slide {cls}"><div class="wrap"><div class="kick">{kick}</div><h2>{title}</h2>{body}</div></section>')

# 1 title
S.append('''<section class="slide title"><div class="wrap">
 <div class="kick">Stanford · Koyejo group · scalable oversight</div>
 <h1>Watching the watchers:<br><span class="hl">when do AI judges actually fail?</span></h1>
 <p class="lede">An overnight research campaign on what breaks AI judges, told step by step. Every result
 was attacked by an independent critic, one was publicly retracted and corrected, and the final findings
 survived external validation on human-labeled data.</p>
 <div class="meta">7 judge models (0.5B to frontier) · 6 model families · planted-error instruments · 4 benchmarks · 13 findings · 1 retraction</div>
 <div class="hint">scroll or press → to advance</div></div></section>''')

# 2 the problem
slide("The problem","Why 'AI judging AI' is the question that matters",
 '''<p>Modern AI systems produce work no one has time to check: proofs, code, plans, essays. The standard
 fix is to use another AI as a <b>judge</b>. But that only moves the problem: <b>who checks the judge?</b>
 This is called <i>scalable oversight</i>, and the field's working assumption is that judges become
 unreliable as the systems they grade get stronger.</p>
 <div class="def"><b>What we set out to do.</b> Measure exactly when and why AI judges fail, using judges of
 every size, from a 0.5B model that fits on a phone to frontier models, and using errors <b>we planted
 ourselves</b>, so there is never any doubt about what the right verdict was.</div>
 <p class="q">The short version of what we found: judges fail far less than the field thinks, the
 measurements fail more, and the one lever that fixes small judges flips sign in exactly the domains
 oversight cares about most.</p>''')

# 3 setup
slide("The setup","A ladder of judges and errors we control",
 chips(("7","judges: 0.5B → frontier"),("2","planted-error instruments"),("100%","errors verified before use"))+
 '''<p>We used the Qwen model family as a <b>ladder</b> of judges (0.5B, 1.5B, 3B, 7B, 14B) plus GPT-5.2
 and Claude Opus at the top, all grading the same solutions with the same instructions.</p>
 <p>The key trick is <b>planted errors</b>. Instead of trusting a benchmark's answer key, we took solutions
 known to be correct and broke them ourselves, in two ways: subtle single-number <b>typos</b>, and fully
 <b>propagated errors</b>, where a wrong value is carried through every later step so the solution reads
 perfectly smoothly but ends wrong. A mechanical checker verified every planted error (all arithmetic
 consistent, final answer genuinely wrong, no giveaway phrases). For code, we mutated correct programs and
 kept only mutants that <b>actually fail the official tests</b>.</p>
 '''+fig("f0_method","The full method at a glance: build verified errors, show them to a ladder of judges under three reference conditions, then move to domains with no answer key.")+'''
 <div class="take">When you plant the error yourself, "did the judge catch it?" has a definite answer.</div>''')

# 4 the mirage
slide("Act I · the mirage","We found a spectacular law. Then we checked it.",
 '''<p>Early in the night the data produced something beautiful: if you count how many <b>small</b> judges
 a wrong solution fools, you can predict almost perfectly whether the <b>frontier</b> judge is fooled too.
 Zero small judges fooled: the frontier fails 1% of the time. All three fooled: <b>94%</b>. A cheap early
 warning system for frontier failures!</p>'''+
 fig("f1_mirage","Left: the apparent law. Right: what adjudicating all 55 cases revealed, 71% were benchmark label errors, and on the genuinely wrong cases the frontier judge failed only 6%.")+
 '<div class="take">The "law" was an artifact. The solutions that fooled everyone were mostly <b>correct answers marked wrong by the benchmark</b>. Two other exciting effects died the same death that night.</div>')

# 5 lesson + miner
slide("Act I · the payoff","The answer keys are dirty, and that is measurable",
 chips(("4.1%","of GSM8K grades in our pipeline were wrong"),("89%","bug-miner precision, externally validated"))+
 '''<p>Three separate "judge failure" effects each dissolved into <b>label noise</b>: errors in the
 benchmark answer keys, not in the judges. This flips the usual conclusion: much of what the literature
 measures as judge unreliability is actually <b>oracle unreliability</b>.</p>
 <p>The wreckage contains a tool. When a handful of cheap open models <b>and</b> a frontier judge all
 unanimously disagree with the answer key, the key is nearly always wrong. We validated this against
 GSM8K-Platinum, a human re-annotation, with no frontier model in the loop:</p>'''+
 fig("f2_miner","Of 74 items flagged by cheap-model consensus, 66 (89%) were genuine answer-key problems. An unsupervised benchmark-debugging tool that costs pennies.")+
 '<div class="take">Rule one of oversight research: before you measure the judge, measure the answer key.</div>')

# 6 how judges really behave
slide("Act II · real behavior","With clean labels, judging skill is a smooth curve",
 fig("f3_auc","Discrimination (AUC) on naturally occurring errors, after label cleanup. Each step up the ladder helps; the frontier edge is confidence, not a different species.")+
 '''<p>No cliff, no magic threshold. We also caught ourselves here: at one scoring cutoff the 7B judge
 looked identical to the frontier. That was a <b>threshold artifact</b>, at a different cutoff the gap was
 74% vs 10%. Robust metrics or nothing.</p>
 <div class="take">Judge capability is real and smooth. The interesting question is what changes <i>qualitatively</i> with scale, next slide.</div>''')

# 7 typo probe
slide("Act II · the typo probe","Judges do not check lines. They read the story.",
 chips(("40-50%","of explicit false equations go unpenalized"),("69-85%","still pass a typical score bar"))+
 fig("f4_typos","Detection of a single planted false equation, by where it sits (early/late) and how blatant it is (gross/small). Mid-size judges punish blatant early errors; frontier judges punish the quiet late ones that actually touch the conclusion, and forgive obvious typos as typos.")+
 '''<p>Read the inversion: 3B and 14B judges react to <b>how much an error stands out</b>. Frontier judges
 re-derive the solution and react to <b>whether the error matters</b>. Both styles leave line-level slips
 unpunished, which is bad news if you want judges as step-by-step process checkers.</p>
 <div class="take">Frontier judges are outcome graders, not proofreaders.</div>''')

# 8 the central mechanism
slide("Act III · the mechanism","The single most useful plot of the campaign",
 fig("f5_phase","Detection of fully-propagated hidden errors. Red: judge sees only the problem and the solution. Green: judge also sees a correct reference. Purple: judge sees its OWN earlier answer as the reference.")+
 '''<p>Three curves, one story. <b>Without a reference</b> (red), small judges are nearly blind and skill
 climbs slowly with size. <b>With a correct reference</b> (green), even a 3B judge catches 85% of hidden
 errors. The gap between red and green is what a reference is worth: <b>+68 points at 3B, +2 at the
 frontier</b>.</p>
 <div class="def"><b>The decomposition.</b> Verification = <i>getting a reference</i> + <i>comparing against
 it</i>. Comparing is cheap, tiny models can do it. Getting the reference is the expensive,
 capability-bound part, and frontier models are just models that can generate their own.</div>''')

# 9 the retraction
slide("Interlude","The bug, the retraction, and the better result",
 '''<p>Full honesty: at 3am the purple curve first came out <b>perfect</b>, "solve it yourself first"
 seemed to recover 100% of the reference benefit at every size. Suspicious, because the numbers were
 <i>exactly</i> equal to the green curve. A code audit found a silent dispatch bug: the "solve first" arm
 had been running the with-reference condition twice. <b>128 of 128 scores identical.</b> We retracted the
 finding in the log and reran everything with a verified pipeline.</p>
 <p>The corrected experiments were more interesting than the bug:</p>
 <ul>
 <li><b>Asking</b> a 7B judge to "solve first, then judge" in one prompt makes it <i>worse</i> (28% vs 49%):
 it silently skips the solving step. Small models fail instructions quietly.</li>
 <li><b>Forcing</b> the two steps mechanically (generate an answer in one pass, judge with it in the next)
 works: that is the real purple curve, 59 / 60 / 85 / 95%.</li>
 <li>Strangest of all: at 1.5B, the judge does better with <b>its own scruffy answer</b> as reference (59%)
 than with the official textbook solution (21%). Style match matters more than polish.</li></ul>
 <div class="take">Six of our own results died by our own checks during this campaign. This one taught the most.</div>''')

# 10 external checks
slide("Act III · does it generalize?","Six families and a human-labeled benchmark say yes",
 fig("f6_families","With-reference vs no-reference detection replicates in every family tried: Qwen, Microsoft, Mistral, AI2, Meta, Google. Family matters more than parameter count (Mistral-7B is weaker than Qwen-3B).")+
 fig("f7_processbench","On ProcessBench (human-annotated first-error labels), the same capability story appears, and the solve-first trick gives +7-8 F1 once the judge is big enough to actually follow it.")+
 '<div class="take">Not a Qwen quirk, not a quirk of our planted errors.</div>')

# 11 phase 2 setup
slide("Act IV · the real frontier","Now the hard part: domains where you cannot check the answer",
 '''<p>Everything so far had a safety net: math has answers, code has tests. Scalable oversight is hardest
 precisely where that net is gone, open-ended writing, judgment calls, tasks with many valid answers. Does
 the reference trick, our best lever so far, still work there?</p>
 <div class="def"><b>The experiment.</b> RewardBench-2 provides graded pairs (a better and a worse response)
 across task types that range from fully checkable (math) to many-valid-answers questions. We ran the whole
 judge ladder over 460 prompts, each pair judged <b>in both orders</b> (if the verdict changes when you swap
 A and B, the judge is guessing), in three conditions: no reference, the judge's own answer as reference,
 and, as a control, <b>another model's</b> answer as reference.</div>''')

# 12 flips
slide("Act IV · a free diagnostic","Order-swapping exposes judging without any answer key",
 fig("f9_flips","How often the verdict flips when you swap the order of the two responses. At 0.5B, verdicts are near coin-flips. The flip rate collapses with scale, except on precise instruction-checking, which defeats every judge on the ladder.")+
 '''<p>Two things to notice. First, this measure needs <b>no ground truth at all</b>, you just ask twice.
 Second, the red line: judging precise instruction compliance ("did it really obey every constraint?") stays
 near chance for every judge up to 14B. That is the pairwise version of the proofreading blind spot.</p>
 <div class="take">Some tasks are hard for judges because they are ambiguous. Others because they require exactly the line-checking judges do not do.</div>''')

# 13 the double dissociation
slide("Act IV · the finding","The reference lever flips sign, and we know why",
 fig("f8_rb2","Judge = Qwen-14B. On math, references help in proportion to their quality (a weak model's reference does nothing, a decent one +7, its own +9). On many-valid-answer questions, EVERY reference hurts, its own, a weak model's, a decent one's, all about equally (p<=.0005, McNemar).")+
 '''<p>The control arm settles the mechanism. If the harm came from the judge loving its own writing, other
 models' references would be harmless. They are not. <b>Any single reference</b> anchors the judge on one
 valid answer and makes it punish other perfectly valid ones.</p>
 <div class="take">The dividing line is not "objective vs subjective". It is <b>one right answer vs many</b>.</div>''')

# 14 the rules
S.append('''<section class="slide concl"><div class="wrap"><div class="kick">What it all adds up to</div>
 <h2>Practical rules for anyone building oversight today</h2>
 <div class="cols"><div><h3>Measurement</h3>
 <ul><li><b>Audit the answer key first.</b> Cheap-model consensus disagreement finds oracle bugs at ~89-97% precision, unsupervised.</li>
 <li><b>Never trust one threshold.</b> Report threshold-free metrics; a cutoff manufactured a fake "7B = frontier" result.</li>
 <li><b>Ask twice, swapped.</b> Order-flip rate is a free, label-free stress meter for any pairwise judge.</li></ul>
 <h3>Judges are not proofreaders</h3>
 <ul><li>Explicit false steps pass 40-85% of the time; judges grade outcomes and coherence, not lines. Do not use raw judge scores as step-level process rewards.</li></ul></div>
 <div class="new"><h3>The reference law</h3>
 <ol><li><b>One right answer?</b> Provide a reference, quality matters, and even a small judge becomes reliable. No trusted reference? Have the judge generate one in a separate forced step (never "please solve first" in one prompt).</li>
 <li><b>Many valid answers?</b> Withhold references entirely. Every reference, of any quality and any source, anchors the judge against valid alternatives (-7 to -8 points, p&le;.0005).</li>
 <li><b>Precise constraint checking?</b> No judge on our ladder can do it reliably. Use programmatic checkers, not judges.</li></ol></div></div></div></section>''')

# 15 integrity + what's next
slide("The record","How much of this should you believe?",
 chips(("13","findings"),("6","own results killed by own checks"),("1","public retraction + correction"),("4","independent critic passes"))+
 '''<p>Every headline number was re-derived from raw files with fresh code; planted code errors were
 re-executed against official tests; the label-noise findings rest on two frontier model families agreeing
 55/55 <i>plus</i> a human-curated external check; the closest prior paper was audited page by page to
 confirm the sign-flip result is genuinely new (it tests only single-answer tasks, pointwise, no controls
 like ours).</p>
 <p><b>Open questions we did not settle:</b> whether verification is item-by-item bounded by generation
 (weak coupling, needs more data); human spot-audits of our model-based adjudications; agent-trajectory
 oversight (existing benchmarks cover safety labels, our planted-flaw approach there is future work); and
 the full frontier arms on the hard-to-verify experiments.</p>
 <div class="take">Full audit trail: docs/oversight-log.md. Paper draft: docs/oversight-paper.md. All data and instruments in the repo.</div>''')

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
html='<title>Watching the watchers: when do AI judges actually fail?</title>'+STYLE+'<div class="rail"></div><button class="toggle">◐ theme</button><div class="counter"></div><div class="deck">'+"".join(S)+'</div>'+SCRIPT
out="paper/oversight_slides.html"
open(out,"w").write(html); print("wrote",out,"slides:",len(S),"bytes:",len(html))
