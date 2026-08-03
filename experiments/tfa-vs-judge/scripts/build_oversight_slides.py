# Build the oversight story deck (self-contained, data-URI figures), same design system as the TFA deck.
# v11 restructure, applying the presentation rules from Brando's TFA-deck review: takeaway stated first
# and restated last, contents slide, terms defined before use, plain researcher voice throughout,
# figure captions that carry their verdicts, and an APPENDIX divider before the backup material.
import base64, pathlib
FIGDIR = pathlib.Path("paper/figs_oversight")
def datauri(fn): return "data:image/png;base64," + base64.b64encode((FIGDIR/fn).read_bytes()).decode()
IMG = {k: datauri(k + ".png") for k in
       ["f0_method","f1_mirage","f2_miner","f3_auc","f4_typos","f5_phase","f6_families","f7_processbench","f8_rb2","f9_flips"]}
def fig(k,cap): return f'<figure class="fig"><img src="{IMG[k]}" alt="{cap}"/><figcaption>{cap}</figcaption></figure>'
def chips(*cs): return '<div class="chips">'+''.join(f'<div class="chip"><span class="cn">{n}</span><span class="cl">{l}</span></div>' for n,l in cs)+'</div>'
S=[]
def slide(kick,title,body,cls=""): S.append(f'<section class="slide {cls}"><div class="wrap"><div class="kick">{kick}</div><h2>{title}</h2>{body}</div></section>')

# 1 title, with the takeaway in the lede
S.append('''<section class="slide title"><div class="wrap">
 <div class="kick">Stanford · Koyejo group · scalable oversight</div>
 <h1>Watching the watchers:<br><span class="hl">when do AI judges actually fail?</span></h1>
 <p class="lede">We spent a research campaign trying to break AI judges, using errors we planted ourselves so the
 right verdict was never in doubt. The short version of what we found: judges fail less than the field thinks, the
 answer keys used to measure them fail more, and the one trick that makes small judges strong, showing them a
 reference answer, backfires exactly on the tasks oversight cares about most. Every result was attacked by an
 independent critic. One was publicly retracted and corrected. The finals survived checks against human-labeled
 data.</p>
 <div class="meta">7 judge models (0.5B to frontier) · 6 model families · planted-error instruments · 5 benchmarks · 15 findings · 1 retraction · v11</div>
 <div class="hint">scroll or press → to advance</div></div></section>''')

# 2 the takeaway
slide("The takeaway","Three results, stated up front",
 '''<div class="cols"><div>
 <h3 class="r">1 &middot; A reference helps or hurts, predictably</h3>
 <p>Show a judge a known-good answer and it gets much better at grading tasks with <b>one right answer</b>: +9
 points, and the better the reference, the bigger the gain. Show it any reference on a task with <b>many valid
 answers</b> that it cannot verify by itself, and it gets <b>worse</b>: 7 to 8 points, no matter who wrote the
 reference (p&le;.0005). We then rebuilt both situations synthetically, and the harm appeared and disappeared
 exactly where this rule says it should.</p>
 <h3 class="g">2 &middot; Small judge + reference = cheap oversight</h3>
 <p>Without a reference, a 3B judge catches 17% of hidden errors. With one, <b>85%</b>, close to frontier level.
 That boost replicates in all six model families we tried (+14 to +60 points). Our reading: <i>comparing</i>
 against a reference is cheap, even tiny models can do it; <i>producing</i> the reference is the expensive part.
 The scarce resource in oversight is references, not judge size.</p></div>
 <div>
 <h3 class="a">3 &middot; The measurements themselves were broken</h3>
 <p>Three textbook-looking "judge failure" effects in our own data turned out to be errors in the benchmarks'
 grading, 71-83% of the flagged cases once adjudicated. A useful tool fell out of the cleanup: when several cheap
 models unanimously disagree with the official grade, the official grade is the thing that is wrong 89% of the
 time (validated against a human re-annotation).</p>
 <div class="def"><b>What we do not claim.</b> No new judge model, and no formal theory with proofs. The smaller
 results in this deck (typo forgiveness, the salience inversion, the order-flip meter) are supporting evidence,
 not headlines.</div></div></div>''')

# 3 contents
slide("Contents","What this deck covers",
 '''<div class="cols"><div>
 <h3 class="ac">Terms</h3>
 <p>Five definitions everything else depends on. One slide, before any results.</p>
 <h3>The problem and the method</h3>
 <p>Why "AI judging AI" matters, and how planting our own errors gives every experiment a known right answer.</p>
 <h3 class="a">Act I &middot; the false discovery</h3>
 <p>A beautiful "law" of judge failure that dissolved into dirty answer keys, and the cheap answer-key debugger
 that fell out of the wreckage.</p>
 <h3>Act II &middot; how judges actually behave</h3>
 <p>Judging skill is a smooth curve in model size, and judges of every size grade outcomes, not individual
 lines.</p></div>
 <div>
 <h3 class="g">Act III &middot; the reference mechanism</h3>
 <p>The lever that makes a 3B judge nearly frontier-level, the bug that forced a retraction on the way, and the
 six-family replication.</p>
 <h3 class="r">Act IV &middot; hard-to-verify domains</h3>
 <p>The same lever flips sign on tasks with many valid answers, plus a free diagnostic that needs no answer key at
 all.</p>
 <h3>The rules</h3>
 <p>A practical checklist for anyone building oversight, then the takeaway once more.</p>
 <h3 style="color:var(--mut)">Appendix</h3>
 <p>The integrity record (what died by our own checks) and the open questions.</p></div></div>''')

# 4 terms
slide("Terms used in this deck","Five terms, defined before we use them",
 '''<div class="cols"><div>
 <div class="def"><b>AI judge.</b> A model shown a problem and a proposed solution and asked: is this correct?
 In some experiments it instead sees two responses and picks the better one.</div>
 <div class="def"><b>Reference.</b> A known-correct answer shown to the judge next to the solution it is grading.
 Whether to give the judge one turns out to be the most consequential design choice in this deck.</div>
 <div class="def"><b>Planted error.</b> We take a solution known to be correct and break it ourselves: a subtle
 changed number, or a wrong value carried consistently through every later step so nothing looks off. Because we
 made the error, "did the judge catch it?" always has a definite answer.</div></div>
 <div>
 <div class="def"><b>Grading oracle.</b> Whatever produces the official right/wrong labels: the benchmark's answer
 key plus the script that matches answers against it. It can be wrong, and how often it is wrong becomes a theme
 of this deck.</div>
 <div class="def"><b>Detection rate and AUC.</b> Detection rate: the share of planted errors a judge flags. AUC: a
 threshold-free score of separation. Show the judge one right and one wrong solution; how often does it score the
 wrong one lower? 1.0 means always, 0.5 means it is guessing.</div></div></div>''')

# 5 the problem
slide("The problem","Why 'AI judging AI' is the question that matters",
 '''<p>Modern AI systems produce work no one has time to check: proofs, code, plans, essays. The standard fix is to
 use another AI as a <b>judge</b>. That only moves the problem, because now someone has to check the judge. This is
 the field called <i>scalable oversight</i>, and its working assumption is that judges become unreliable as the
 systems they grade get stronger.</p>
 <div class="def"><b>What we set out to do.</b> Measure exactly when and why AI judges fail, using judges of every
 size, from a 0.5B model that fits on a phone to frontier models, and using errors we planted ourselves, so there
 is never any doubt about what the right verdict was.</div>
 <p>What we found, one line each:</p>
 <ul><li>Judges fail less than the literature suggests.</li>
 <li>The benchmarks used to measure them fail more.</li>
 <li>The best trick for making small judges strong backfires in the domains oversight most cares about.</li></ul>''')

# 6 setup
slide("The setup","A ladder of judges, and errors we control",
 chips(("7","judges: 0.5B → frontier"),("2","kinds of planted error"),("100%","of errors verified before use"))+
 '''<p>The judges: the Qwen family at five sizes (0.5B, 1.5B, 3B, 7B, 14B), plus GPT-5.2 and Claude Opus at the
 top. All grade the same solutions under the same instructions.</p>
 <p>The errors: we broke known-correct solutions in two ways. A <b>typo</b> changes one number and nothing else. A
 <b>propagated error</b> changes a value early and carries it through every later step, so the arithmetic all
 checks out and the text reads smoothly, but the final answer is wrong. A mechanical checker verified every planted
 error before use: arithmetic consistent, final answer genuinely wrong, no giveaway phrasing. For code, we mutated
 correct programs and kept only mutants that actually fail the official tests.</p>
 '''+fig("f0_method","The method at a glance: build verified errors, show them to the ladder of judges under three reference conditions, then move to domains with no answer key.")+'''
 <div class="take">When you plant the error yourself, "did the judge catch it?" has a definite answer.</div>''')

# 7 the mirage
slide("Act I · the false discovery","We found a spectacular law. Then we checked it.",
 '''<p>Early in the campaign the data produced something beautiful: count how many <b>small</b> judges a wrong
 solution fools, and you can predict almost perfectly whether the <b>frontier</b> judge is fooled too. Zero small
 judges fooled: the frontier fails 1% of the time. All three fooled: <b>94%</b>. A cheap early-warning system for
 frontier failures!</p>
 <p>Before writing it up, we hand-checked every one of the 55 cases behind the 94%. Most were not judge failures
 at all. They were <b>correct answers that the benchmark had marked wrong</b>. The judges were right; the answer
 key was not.</p>'''+
 fig("f1_mirage","Left: the apparent law. Right: what checking all 55 cases revealed. 71% were benchmark labeling errors, and on the genuinely wrong solutions the frontier judge failed only 6% of the time.")+
 '<div class="take">Two other exciting effects died the same death under the same scrutiny. That changed how we ran everything that follows.</div>')

# 8 the payoff: miner
slide("Act I · the payoff","The answer keys are dirty, and that is measurable",
 chips(("4-10%","of GSM8K grades wrong, depending on model family"),("89%","of consensus flags were real grading bugs"),("0.66→0.91","frontier judge quality, before → after repairing the grading"))+
 '''<p>Three separate "judge failure" effects each dissolved into label noise: errors in the benchmark grading, not
 in the judges. That flips the usual conclusion. A good share of what the literature measures as judge
 unreliability is actually <b>answer-key unreliability</b>.</p>
 <p>The cleanup produced a tool. When several cheap open models <b>unanimously</b> disagree with the official
 grade, the official grade is nearly always what is wrong: usually the answer-matching script misreading a correct
 answer, occasionally the key itself. We validated this against GSM8K-Platinum, a human re-annotation, with no
 frontier model involved.</p>'''+
 fig("f2_miner","Of 74 items flagged by cheap-model consensus, 66 (89%) were genuine grading problems: 60 script misparses of correct answers, 4 broken items, 2 wrong keys. An answer-key debugger that costs pennies to run.")+
 '<div class="take">Rule one of oversight research: before you measure the judge, measure the answer key.</div>')

# 9 smooth curve
slide("Act II · real behavior","With clean labels, judging skill is a smooth curve",
 fig("f3_auc","Separation of right from wrong solutions (AUC) on naturally occurring errors, after the label cleanup. Every step up the ladder helps. The frontier's edge is confidence, not a different kind of ability.")+
 '''<p>No cliff, no magic threshold where judging "turns on". We also caught ourselves once here: at one scoring
 cutoff, the 7B judge looked identical to the frontier. At a different cutoff the gap was 74% versus 10%. The
 equality was an artifact of where we drew the line, so since then we report threshold-free numbers only.</p>
 <div class="take">Judge skill grows smoothly with size. What changes qualitatively with scale is on the next slide.</div>''')

# 10 typos
slide("Act II · the typo probe","Judges grade the outcome, not each line",
 chips(("40-50%","of explicit false equations go unpenalized"),("69-85%","still pass a typical score bar"))+
 fig("f4_typos","Detection of one planted false equation, by where it sits (early or late) and how blatant it is. Mid-size judges punish the blatant early ones. Frontier judges punish the quiet late ones that actually affect the conclusion, and forgive obvious typos as typos.")+
 '''<p>The pattern to notice: 3B and 14B judges react to how much an error <b>stands out</b>. Frontier judges
 re-derive the solution and react to whether the error <b>matters</b>. Both styles leave line-level slips
 unpunished. If you were hoping to use a judge as a step-by-step proofreader, this is the slide that says no.</p>
 <div class="take">Frontier judges behave like graders of final answers, not like proofreaders.</div>''')

# 11 the mechanism
slide("Act III · the mechanism","The most useful plot of the campaign",
 fig("f5_phase","Detection of fully-propagated hidden errors, three conditions. Red: the judge sees only the problem and the solution. Green: it also sees a correct reference. Purple: it sees its own earlier answer as the reference.")+
 '''<p>Read the curves one at a time. <b>Red, no reference:</b> small judges are nearly blind, and skill climbs
 slowly with size. <b>Green, with a correct reference:</b> even the 3B judge now catches 85% of hidden errors. The
 gap between red and green is what a reference is worth: +68 points at 3B, shrinking to +2 at the frontier, because
 the frontier can already supply what the reference provides. <b>Purple:</b> the judge generates its own answer
 first, then judges with it as the reference; it recovers most of the green curve without being handed anything.</p>
 <div class="def"><b>What this means.</b> Verification splits into two parts: getting a reference, and comparing
 against it. Comparing is cheap, tiny models can do it. Getting the reference is the expensive, capability-bound
 part. A frontier judge is, in effect, a judge that brings its own reference.</div>''')

# 12 the retraction
slide("Interlude","The bug, the retraction, and the better result",
 '''<p>Full honesty: the first version of the purple curve came out <b>perfect</b>. "Solve it yourself first"
 seemed to recover 100% of the reference benefit at every size. That looked too good, and the giveaway was that its
 numbers were <i>exactly</i> equal to the green curve, 128 scores out of 128. A code audit found the reason: a
 silent dispatch bug had been running the with-reference condition twice. We retracted the finding in the log and
 reran everything with a verified pipeline.</p>
 <p>The corrected experiments taught more than the original claim would have:</p>
 <ul>
 <li><b>Asking</b> a 7B judge to "solve first, then judge" in a single prompt makes it <i>worse</i> (28% vs 49%).
 It quietly skips the solving step. Small models fail instructions silently.</li>
 <li><b>Forcing</b> the two steps mechanically, generate an answer in one pass, judge with it in the next, is what
 works. That is the real purple curve: 59 / 60 / 85 / 95% up the ladder.</li>
 <li>Strangest of all: at 1.5B the judge does better with <b>its own scruffy answer</b> as the reference (59%) than
 with the official textbook solution (21%). A reference in the judge's own style beats a polished one it finds
 foreign.</li></ul>
 <div class="take">Six of our own results died by our own checks during this campaign. This one taught the most.</div>''')

# 13 generalization
slide("Act III · does it generalize?","Six model families and a human-labeled benchmark say yes",
 fig("f6_families","The reference boost, with-reference minus no-reference detection, replicates in every family tried: Qwen, Microsoft, Mistral, AI2, Meta, Google. Family matters more than size (Mistral-7B is weaker than Qwen-3B).")+
 fig("f7_processbench","On ProcessBench, where humans annotated the first wrong step, the same size story appears, and the forced solve-first trick adds 7-8 F1 points once the judge is big enough to follow it.")+
 '<div class="take">The mechanism is not a Qwen quirk, and not a quirk of our planted errors.</div>')

# 14 hard-to-verify setup
slide("Act IV · the real frontier","The hard part: tasks where you cannot check the answer",
 '''<p>Everything so far had a safety net: math has answers, code has tests. Scalable oversight is hardest exactly
 where that net is gone: open-ended writing, judgment calls, questions with many valid answers. So the question
 became: does the reference trick, our best lever so far, still work there?</p>
 <div class="def"><b>The experiment.</b> RewardBench-2 provides pairs of responses, one better and one worse, across
 task types from fully checkable (math) to many-valid-answers (open questions). We ran the whole judge ladder over
 460 prompts. Each pair was judged <b>twice, in both orders</b>: if the verdict changes when you swap which response
 is shown first, the judge is guessing. Three conditions: no reference, the judge's own answer as reference, and, as
 a control, <b>another model's</b> answer as reference.</div>''')

# 15 flips
slide("Act IV · a free diagnostic","Ask twice, swapped: judging quality with no answer key at all",
 fig("f9_flips","How often the verdict flips when the two responses swap places. At 0.5B, verdicts are close to coin flips. The flip rate falls steadily with size, except on precise instruction-checking, where every judge on the ladder stays near chance.")+
 '''<p>Two things worth noticing. First, this measurement needs no ground truth: you just ask the same question
 twice with the order swapped. Second, the one line that never improves: judging <b>precise instruction
 compliance</b> ("did the response really obey every stated constraint?") stays near chance at every size we
 tested. That is the pairwise version of the proofreading blind spot from Act II.</p>
 <div class="take">Some tasks are hard for judges because they are ambiguous. Others are hard because they require exactly the line-by-line checking judges do not do.</div>''')

# 16 the sign flip
slide("Act IV · the finding","The reference lever flips sign, and we know why",
 fig("f8_rb2","Judge: Qwen-14B. On math, references help in proportion to their quality: a weak model's reference does nothing, a decent one adds +7, the judge's own adds +9. On many-valid-answer questions every reference hurts, its own, a weak model's, a decent one's, all by about the same amount (p<=.0005, McNemar).")+
 '''<p>The control arm settles the mechanism. If the harm came from the judge favoring its own writing, references
 written by <i>other</i> models would be harmless. They are not: they hurt by the same amount. What actually
 happens: on a question with many valid answers, any single reference anchors the judge to one of them, and it
 starts punishing other, perfectly valid answers for being different.</p>
 <div class="take">The dividing line needs two conditions at once: many valid answers, and verification too hard for
 the judge to do itself. On synthetic many-answer tasks whose validity is easy to check, the harm vanishes for every
 judge 3B and up, exactly where this rule says it should.</div>''')

# 17 the rules
S.append('''<section class="slide concl"><div class="wrap"><div class="kick">What it adds up to</div>
 <h2>Practical rules for anyone building oversight today</h2>
 <div class="cols"><div><h3>Measurement</h3>
 <ul><li><b>Audit the grading first</b>, both the script and the key. Cheap-model consensus disagreement finds
 grading bugs at 89% externally validated precision, with no labels needed.</li>
 <li><b>Never trust one threshold.</b> A single cutoff manufactured a fake "7B equals frontier" result in our own
 data. Report threshold-free numbers.</li>
 <li><b>Ask twice, swapped.</b> The order-flip rate is a free stress meter for any pairwise judge.</li></ul>
 <h3>Judges are not proofreaders</h3>
 <ul><li>Explicit false steps pass 40-85% of the time. Judges grade outcomes and coherence, not lines. Do not use
 raw judge scores as step-level process rewards.</li></ul></div>
 <div class="new"><h3>The reference rule</h3>
 <ol><li><b>One right answer?</b> Give the judge a reference; quality matters, and even a small judge becomes
 reliable. No trusted reference available? Have the judge generate one in a separate, forced step. Never "please
 solve it first" inside one prompt.</li>
 <li><b>Many valid answers?</b> Withhold references entirely. Any reference, from any source, anchors the judge
 against valid alternatives: 7 to 8 points worse, p&le;.0005.</li>
 <li><b>Precise constraint checking?</b> No judge on our ladder does it reliably. Use programmatic checkers.</li></ol></div></div></div></section>''')

# 18 closing takeaway
slide("The takeaway, once more","If you remember three things",
 '''<ul style="font-size:1.12rem">
 <li><b>References are the lever.</b> They make small judges nearly frontier-level on single-answer tasks, and they
 actively hurt on many-valid-answer tasks the judge cannot verify itself. Same lever, opposite signs, and the two
 conditions that decide the sign are known.</li>
 <li><b>Oversight is cheaper than it looks.</b> Comparing against a reference is easy; producing the reference is
 the hard part. Spend capability on making references, not on making judges bigger.</li>
 <li><b>Check the answer key before you blame the judge.</b> Most of our apparent judge failures were grading
 failures, and unanimous disagreement from a handful of cheap models finds those at 89% precision.</li></ul>
 <div class="take">Full audit trail: docs/oversight-log.md. Paper: docs/oversight-paper.md. Everything after the next slide is backup.</div>''')

# 19 appendix divider
S.append('''<section class="slide divider"><div class="wrap" style="text-align:center">
 <div class="kick">everything after this slide is backup</div>
 <h1 style="font-size:clamp(3rem,8vw,6rem)">APPENDIX</h1>
 <p class="lede" style="max-width:56ch;margin:0 auto">The integrity record, and the questions we left open.</p></div></section>''')

# A1 integrity record
slide("Appendix · the record","How much of this should you believe?",
 chips(("15","findings"),("6","of our own results killed by our own checks"),("1","public retraction with correction"),("4","independent critic passes"))+
 '''<p>Every headline number was re-derived from the raw files with fresh code. Planted code errors were re-executed
 against the official test suites. The label-noise findings rest on two frontier model families agreeing on all 55
 adjudicated cases, plus the external check against a human re-annotation. The closest prior paper was audited page
 by page to confirm the sign-flip result is new: it tests only single-answer tasks, scored one response at a time,
 without our control conditions.</p>''')

# A2 open questions
slide("Appendix · open questions","What we did not settle",
 '''<ul>
 <li><b>Is verification bounded by generation, item by item?</b> The coupling we saw is weak; a proper answer needs
 more data.</li>
 <li><b>Human spot-audits</b> of our model-based adjudications. Two frontier families agreeing is strong but is not
 a human check.</li>
 <li><b>Agent-trajectory oversight.</b> Existing benchmarks cover safety labels; planting verified flaws inside
 agent trajectories, the analogue of what we did for math and code, is future work.</li>
 <li><b>Frontier arms on the hard-to-verify experiments.</b> The sign-flip result is established up to 14B; the
 frontier row of that table is incomplete.</li></ul>
 <div class="take">All data, instruments, and scripts are in the repo; the log records every dead end as well as every result.</div>''')

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
b,strong{font-weight:700}.g{color:var(--g);font-weight:700}.a{color:var(--a);font-weight:700}.p{color:var(--p);font-weight:700}.r{color:var(--r);font-weight:700}.ac{color:var(--accent);font-weight:700}
.title{background:radial-gradient(1200px 500px at 15% -10%,color-mix(in srgb,var(--accent) 12%,transparent),transparent)}.title .hl{color:var(--accent)}
.divider{background:radial-gradient(1000px 420px at 50% 0%,color-mix(in srgb,var(--accent) 9%,transparent),transparent)}
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
