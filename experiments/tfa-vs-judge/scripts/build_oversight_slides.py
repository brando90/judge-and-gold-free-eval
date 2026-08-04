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
 <p class="lede">We tested AI judges with errors we planted ourselves, so the right verdict was never in doubt.
 Three findings. Judges fail less often than the literature suggests. The answer keys used to measure them fail
 more often. And the most effective way to help a small judge, showing it a known-correct reference answer, makes
 judging worse on tasks that have many valid answers. One of our own results was retracted and corrected along the
 way; the final ones were checked against human-labeled data.</p>
 <div class="meta">7 judge models, 0.5B to frontier · 6 model families · 5 benchmarks · every planted error verified before use</div>
 <div class="hint">scroll or press → to advance</div></div></section>''')

# 2 the takeaway
slide("The takeaway","Three results, stated up front",
 '''<div class="cols"><div>
 <h3 class="r">1 &middot; A reference helps or hurts, predictably</h3>
 <p>Show a judge a known-good answer and it gets better at grading tasks with <b>one right answer</b>: 9 percentage
 points more of its verdicts correct, and the better the reference, the bigger the gain. Show it any reference on a
 task with <b>many valid answers</b> that it cannot verify by itself, and it gets <b>worse</b>: 7 to 8 points fewer
 correct verdicts, no matter who wrote the reference (p&le;.0005 under a paired test). A controlled synthetic version of both situations reproduced both effects.</p>
 <h3 class="g">2 &middot; A small judge with a reference is nearly frontier-level</h3>
 <p>Without a reference, a 3B judge catches 17% of hidden errors. With one, <b>85%</b>, close to frontier level.
 That boost replicates in all six model families we tried, adding 14 to 60 percentage points of detection.
 Our reading: comparing against a reference is cheap, even tiny models can do it. Producing the reference is
 the expensive part.</p></div>
 <div>
 <h3 class="a">3 &middot; The measurements themselves were broken</h3>
 <p>Three textbook-looking "judge failure" effects in our own data turned out to be errors in the benchmarks'
 grading, 71-83% of the flagged cases once adjudicated. The cleanup also produced a useful tool. When several cheap models unanimously disagree with the official
 grade, the official grade is the one that is wrong 89% of the time. We validated that rate against a
 human re-annotation.</p>
 <div class="def"><b>What we do not claim.</b> No new judge model, and no formal theory with proofs. The smaller
 results in this deck (how judges treat typos, which errors they notice, and the order-swap consistency check) are supporting evidence,
 not headlines.</div></div></div>''')

# 3 contents
slide("Contents","What this deck covers",
 '''<div class="cols"><div>
 <h3 class="ac">Terms</h3>
 <p>Five definitions used throughout. One slide, before any results.</p>
 <h3>The problem and the method</h3>
 <p>Why AI-judging-AI matters, and how we build experiments where the correct verdict is known: we take correct
 solutions and break them ourselves.</p>
 <h3 class="a">Part 1 &middot; answer keys</h3>
 <p>Patterns in our data that looked like laws of judge failure turned out, on checking the individual cases, to
 be errors in the benchmark's own answer key. Checking answer keys this way is cheap and reliable, so we kept it
 as a tool.</p>
 <h3>Part 2 &middot; how judges behave</h3>
 <p>With the labels cleaned up: judging skill rises smoothly with model size, and judges at every size grade the
 final outcome rather than checking each line of reasoning.</p></div>
 <div>
 <h3 class="g">Part 3 &middot; what a reference is worth</h3>
 <p>Showing the judge a known-correct answer makes small judges far better. We measure the effect, discard one
 buggy result along the way, and repeat the measurement in six model families.</p>
 <h3 class="r">Part 4 &middot; tasks you cannot check</h3>
 <p>On tasks with many valid answers, the same reference makes judging worse. Also: a way to measure a judge's
 reliability with no answer key, by asking the same question twice with the order swapped.</p>
 <h3>The rules</h3>
 <p>A practical checklist for anyone building oversight, then the three takeaways again.</p>
 <h3 style="color:var(--mut)">Appendix</h3>
 <p>The full walkthrough of the apparent judge-failure law, which of our own results we discarded and why, and the
 questions we left open.</p></div></div>''')

# 4 terms
slide("Terms used in this deck","Five terms, defined before we use them",
 '''<div class="cols"><div>
 <div class="def"><b>AI judge.</b> A model shown a problem and a proposed solution and asked: is this correct?
 In some experiments it instead sees two responses and picks the better one.</div>
 <div class="def"><b>Reference.</b> A known-correct answer shown to the judge next to the solution it is grading.
 Each experiment states whether the judge got one, and from whom.</div>
 <div class="def"><b>Planted error.</b> We take a solution known to be correct and break it ourselves: a subtle
 changed number, or a wrong value carried consistently through every later step so nothing looks off. Because we
 made the error, "did the judge catch it?" always has a definite answer.</div></div>
 <div>
 <div class="def"><b>Answer key.</b> Shorthand for whatever produces the official right/wrong labels: the
 benchmark's list of correct answers, plus the script that matches a model's answer against it. Either part can
 be wrong, and when we say "the grading was wrong", we mean this pipeline.</div>
 <div class="def"><b>Detection rate and AUC.</b> Detection rate: the share of planted errors a judge flags. AUC:
 show the judge one right and one wrong solution; how often does it score the wrong one lower? 1.0 means always,
 0.5 means it is guessing. AUC does not depend on choosing a pass/fail cutoff, which matters later.</div></div></div>''')

# 5 the problem
slide("The problem","Why 'AI judging AI' is the question that matters",
 '''<p>Modern AI systems produce work no one has time to check: proofs, code, plans, essays. The standard fix is to
 use another AI as a <b>judge</b>. That only moves the problem, because now someone has to check the judge. This is
 the field called <i>scalable oversight</i>, and its working assumption is that judges become unreliable as the
 systems they grade get stronger.</p>
 <div class="def"><b>What we set out to do.</b> Measure exactly when and why AI judges fail, using judges of every
 size, from a 0.5B model that fits on a phone to frontier models, and using errors we planted ourselves, so there
 is never any doubt about what the right verdict was.</div>
 <p>The next slide describes the setup. After that, the results in the order we found them, including the one we
 got wrong.</p>''')

# 6 setup
slide("The setup","Judges of every size, and errors we control",
 chips(("7","judges: 0.5B → frontier"),("2","kinds of planted error"),("100%","of errors verified before use"))+
 '''<p>The judges: the Qwen family at five sizes (0.5B, 1.5B, 3B, 7B, 14B), plus GPT-5.2 and Claude Opus as the
 frontier judges. All grade the same solutions under the same instructions.</p>
 <p>The errors: we broke known-correct solutions in two ways. A <b>typo</b> changes one number and nothing else. A
 <b>propagated error</b> changes a value early and carries it through every later step, so the arithmetic all
 checks out and the text reads smoothly, but the final answer is wrong. A mechanical checker verified every planted
 error before use: arithmetic consistent, final answer genuinely wrong, no giveaway phrasing. For code, we mutated
 correct programs and kept only mutants that actually fail the official tests.</p>
 <div class="def"><b>The three conditions, which the diagram color-codes.</b> <b class="r">No reference:</b> the
 judge sees only the problem and the solution it must grade. <b class="g">A correct reference:</b> the judge also
 sees the benchmark's own known-correct worked solution to the same problem, so it can compare the two. <b class="p">Its
 own earlier answer:</b> before judging, we ask the same model to solve the problem in a separate, earlier call;
 whatever it produced, right or wrong, is then pasted in as the reference when it judges. This last condition asks
 what happens when no trusted reference exists and the judge has to supply its own.</div>
 '''+fig("f0_method","The method at a glance: build verified errors, show them to judges of every size under three reference conditions, then move to tasks with no answer key.")+'''
 <div class="take">Every result that follows is measured against these verified errors.</div>''')

# 8 the payoff: miner
slide("Part 1 · answer keys","Benchmark answer keys contain measurable error, and that changed everything",
 chips(("4-10%","of GSM8K grades wrong, depending on model family"),("89%","of consensus flags were real grading bugs"),("0.66→0.91","r&sup2; between frontier judge scores and true accuracy, before → after fixing the grading"))+
 '''<p>Early on, our data showed three separate effects that looked like textbook laws of judge failure. The most
 striking: counting how many small judges a wrong solution fooled seemed to predict frontier-judge failure almost
 perfectly, 94% when all three were fooled. Before writing anything up, we hand-checked all 55 cases behind that
 number. 71% were <b>correct answers that the benchmark had marked wrong</b>. The judges were right; the answer key
 was not. On the genuinely wrong solutions, the frontier judge failed only 6% of the time. All three apparent
 effects dissolved the same way (the full walkthrough of the first one is in the appendix).</p>
 <p>That reverses the usual conclusion: a good share of what the literature measures as judge unreliability is
 answer-key unreliability.</p>
 <p>The check is simple. When several cheap open models <b>unanimously</b> disagree with the official grade, the
 official grade is nearly always what is wrong: usually the answer-matching script misreading a correct answer,
 occasionally the key itself. We validated this on GSM8K, a standard grade-school math benchmark, against
 GSM8K-Platinum, its human re-checked version, with no frontier model involved.</p>'''+
 fig("f2_miner","Of 74 items flagged by cheap-model consensus, 66 (89%) were genuine grading problems: 60 script misparses of correct answers, 4 broken items, 2 wrong keys. Flagging items where cheap models unanimously disagree with the official grade finds real grading errors at very low cost.")+
 '<div class="take">Check the answer key before drawing conclusions about the judge.</div>')

# 9 smooth curve
slide("Part 2 · real behavior","With clean labels, judging skill is a smooth curve",
 '''<div class="def"><b>How the AUC here is computed.</b> Each judge reads a solution and gives it a numeric score.
 Take the cleaned set of solutions, some genuinely right and some genuinely wrong. Form every pair of one right and
 one wrong solution and ask: did the judge give the wrong one the lower score? The AUC is the fraction of pairs
 where it did, with ties counting half. Always right gives 1.0; random scoring gives 0.5. No pass/fail cutoff is
 involved anywhere, which keeps the comparison honest across judges.</div>'''+
 fig("f3_auc","Separation of right from wrong solutions (AUC) on naturally occurring errors, after the label cleanup. Every increase in judge size helps; the frontier's advantage shows up as more decisive scores.")+
 '''<p>No cliff, and no special size where judging "turns on": each step up in judge size adds skill, all the way
 to the frontier.</p>
 <div class="take">Judge skill grows smoothly with size.</div>''')

# 10 typos
slide("Part 2 · planted false steps","Judges grade the outcome, not each line",
 chips(("40-50%","of explicit false equations go unpenalized"),("69-85%","still receive a passing score at a common cutoff"))+
 '''<p><b>The experiment:</b> we planted a single false equation into otherwise-correct solutions and varied two
 things: where it sits (<b>early</b> in the solution or <b>late</b>, near the conclusion) and how blatant it is
 (<b>blatant</b> arithmetic nonsense or a <b>subtle</b> slip). <b>How to read the figure:</b> each group of bars is
 one placement, each color is one judge, and bar height is the share of those planted false equations the judge
 flagged. Taller means better proofreading.</p>'''+
 fig("f4_typos","Detection of one planted false equation, by where it sits (early or late) and how blatant it is. Mid-size judges punish the blatant early ones. Frontier judges punish the quiet late ones that actually affect the conclusion, and forgive obvious typos as typos.")+
 '''<p>The pattern to notice: 3B and 14B judges react to how much an error <b>stands out</b>. Frontier judges
 re-derive the solution and react to whether the error <b>matters</b>. Both styles leave line-level slips unpunished: judges are not
 reliable step-by-step proofreaders.</p>
 <div class="take">Judges of every size grade the final answer; none reliably checks each line.</div>''')

# 11 the mechanism
slide("Part 3 · the mechanism","What a reference is worth, at every judge size",
 '''<p><b>The experiment:</b> the hidden-error solutions from the setup, the ones whose arithmetic all checks out
 but whose final answer is wrong, shown to each judge under the three conditions defined there. <b>How to read the
 figure:</b> the x-axis is judge size, the y-axis is the share of hidden errors caught, and each line is one
 condition, in the same colors as the setup diagram: <b class="r">red</b> = no reference, <b class="g">green</b> =
 shown the correct reference, <b class="p">purple</b> = its own answer from a separate pass. The vertical gray
 arrows mark the red-to-green gap, which is what handing the judge a reference is worth.</p>'''+
 fig("f5_phase","Detection of fully-propagated hidden errors, three conditions. Red: the judge sees only the problem and the solution. Green: it also sees a correct reference. Purple: it sees its own earlier answer as the reference.")+
 '''<p>Read the curves one at a time. <b>Red, no reference:</b> small judges catch almost none of the errors, and skill
 climbs slowly with size. <b>Green, with a correct reference:</b> even the 3B judge now catches 85% of hidden errors. The gap
 between red and green is what a reference is worth: 68 percentage points of detection at 3B, shrinking to 2 at
 the frontier, because the frontier can already supply what the reference provides. <b>Purple:</b> the judge generates its own answer
 first, then judges with it as the reference; it recovers most of the green curve without being handed anything.</p>
 <div class="def"><b>What this means.</b> Verification splits into two parts: getting a reference, and comparing
 against it. Comparing is cheap, tiny models can do it. Getting the reference is the expensive, capability-bound
 part. The frontier judge gains little from being handed a reference because it can already generate one itself.</div>''')

# 12 the retraction
slide("Part 3 · the bug","A bug, a retraction, and the corrected result",
 '''<p>The first version of the solve-first-then-judge result was wrong. It came out <b>perfect</b>: solving first
 seemed to recover 100% of the reference benefit at every size. That looked too good, and the giveaway was that
 its scores were exactly equal to the with-reference condition on all 128 graded items. A code audit found the
 reason: a bug in our experiment code was silently running the with-reference condition under both labels. We
 retracted the finding in the log and reran everything with a verified pipeline.</p>
 <p>The corrected experiments taught more than the original claim would have:</p>
 <ul>
 <li><b>Asking</b> a 7B judge to "solve first, then judge" in a single prompt makes it <i>worse</i> (28% vs 49%).
 It quietly skips the solving step. Small models fail instructions silently.</li>
 <li><b>Forcing</b> the two steps mechanically, generate an answer in one pass, judge with it in the next, is what
 works: detection of 59% at 1.5B, 60% at 3B, 85% at 7B, 95% at 14B.</li>
 <li>One result we did not expect: at 1.5B the judge does better with <b>its own imperfect answer</b> as the
 reference (59%) than with the official textbook solution (21%). A reference in the judge's own style beats a
 polished one it finds foreign.</li></ul>
 <div class="take">Six of our own preliminary results failed our own checks during this project. This bug was the most instructive.</div>''')

# 13 generalization
slide("Part 3 · does it generalize?","The reference boost replicates in six families and on human-labeled data",
 fig("f6_families","The reference boost, with-reference minus no-reference detection, replicates in every family tried: Qwen, Phi (Microsoft), Mistral, OLMo (AI2), Llama (Meta), Gemma (Google). Which family matters more than parameter count: Mistral-7B is weaker at this than Qwen-3B.")+
 fig("f7_processbench","On ProcessBench, a benchmark where humans marked the first wrong step of each solution, the same size trend appears, and the forced solve-first procedure adds 7-8 points of error-finding accuracy (F1) once the judge is big enough to follow it.")+
 '<div class="take">The effect is not specific to Qwen models, and not specific to our planted errors.</div>')

# 14 hard-to-verify setup
slide("Part 4 · the real frontier","The hard part: tasks where you cannot check the answer",
 '''<p>Everything so far involved tasks that can be checked: math has answer keys, code has tests. Oversight is
 hardest on tasks without either: open-ended writing, judgment calls, questions with many valid answers. So the
 question became: does giving the judge a reference, the most effective intervention so far, still help there?</p>
 <div class="def"><b>The experiment.</b> RewardBench-2 is a benchmark of response pairs, one better and one worse,
 across task types from fully checkable (math) to many-valid-answers (open questions). Note that the judge's task
 changes here: it now picks the better of two responses. We ran every judge size over 460 prompts. Each pair was
 judged <b>twice, in both orders</b>: if the verdict changes when the two responses swap places, it depended on
 presentation order, not content. Three conditions: no reference, the judge's own answer as reference, and, as a
 control, <b>another model's</b> answer as reference.</div>''')

# 15 flips
slide("Part 4 · order-swap consistency","Ask twice, swapped: a reliability check that needs no answer key",
 fig("f9_flips","How often the verdict flips when the two responses swap places. At 0.5B, verdicts are close to coin flips. The flip rate falls steadily with size, except on precise instruction-checking, where judges of every size stay near chance.")+
 '''<p>Two things worth noticing. First, this measurement needs no ground truth: you just ask the same question
 twice with the order swapped. Second, the one line that never improves: judging <b>precise instruction
 compliance</b> ("did the response really obey every stated constraint?") stays near chance at every size we
 tested. This matches Part 2: checking every stated constraint is line-by-line work, and judges of every size skip it.</p>
 <div class="take">Instruction-compliance judging fails not because the task is ambiguous but because it requires line-by-line checking, which judges skip.</div>''')

# 16 the sign flip
slide("Part 4 · the finding","On many-valid-answer tasks, references make judging worse",
 fig("f8_rb2","Judge: Qwen-14B. On math, references help in proportion to their quality: a weak model's reference does nothing, a decent one adds +7, the judge's own adds +9. On many-valid-answer questions every reference hurts, its own, a weak model's, a decent one's, all by about the same amount of pairwise accuracy (p<=.0005 under McNemar's test for paired verdicts).")+
 '''<p>The control condition answers why. If the harm came from the judge favoring its own writing, references
 written by <i>other</i> models would be harmless. They are not: they hurt by the same amount. What actually
 happens: on a question with many valid answers, any single reference anchors the judge to one of them, and it
 starts punishing other, perfectly valid answers for being different.</p>
 <p>We then rebuilt the situation synthetically: tasks with several valid answers where checking validity is
 trivial. There the harm disappears for every judge 3B and up. So the rule needs both conditions at once:
 <b>many valid answers</b>, and <b>verification too hard for the judge to do itself</b>.</p>
 <div class="take">One right answer: give the judge a reference. Many valid answers the judge cannot verify: do not.</div>''')

# 17 the rules
S.append('''<section class="slide concl"><div class="wrap"><div class="kick">What it adds up to</div>
 <h2>Practical rules for anyone building oversight today</h2>
 <div class="cols"><div><h3>Measurement</h3>
 <ul><li><b>Audit the grading first</b>, both the script and the key. When several cheap models unanimously disagree with
 the official grade, the grade is wrong 89% of the time, with no extra human labeling needed.</li>
 <li><b>Never trust one threshold.</b> A single pass/fail cutoff can make two very different judges look equal.
 Report threshold-free numbers such as AUC.</li>
 <li><b>Judge each pair twice, with the order swapped.</b> The order-flip rate is a reliability check that needs no ground truth.</li></ul>
 <h3>Judges are not proofreaders</h3>
 <ul><li>Explicit false steps pass 40-85% of the time. Judges grade outcomes and coherence, not lines. Do not use
 raw judge scores as step-level process rewards.</li></ul></div>
 <div class="new"><h3>The reference rule</h3>
 <ol><li><b>One right answer?</b> Give the judge a reference; quality matters, and even a small judge becomes
 reliable. No trusted reference available? Have the judge generate one in a separate, forced
 generation step. Do not just tell it to solve first inside one prompt; small judges skip the instruction
 silently.</li>
 <li><b>Many valid answers?</b> Withhold references entirely. Any reference, from any source, anchors the judge
 against valid alternatives: 7 to 8 points worse, p&le;.0005.</li>
 <li><b>Precise constraint checking?</b> No judge we tested does it reliably. Use programmatic checkers.</li></ol></div></div></div></section>''')

# 18 closing takeaway
slide("The takeaway, once more","If you remember three things",
 '''<ul style="font-size:1.12rem">
 <li><b>References are the main design choice.</b> They make small judges nearly frontier-level on single-answer
 tasks, and they hurt on many-valid-answer tasks the judge cannot verify itself. Which way it goes depends on two
 known conditions: how many valid answers exist, and whether the judge can verify them.</li>
 <li><b>Most of the cost of oversight is producing references.</b> Comparing against one is easy, even for small
 models. Budget should go into producing good references before it goes into bigger judges.</li>
 <li><b>Check the answer key before drawing conclusions about the judge.</b> Most of our apparent judge failures
 were grading failures, and unanimous disagreement from a handful of cheap models finds those at 89%
 precision.</li></ul>
 <div class="take">Full audit trail: docs/oversight-log.md. Paper: docs/oversight-paper.md. Everything after the next slide is backup.</div>''')

# 19 appendix divider
S.append('''<section class="slide divider"><div class="wrap" style="text-align:center">
 <div class="kick">everything after this slide is backup</div>
 <h1 style="font-size:clamp(3rem,8vw,6rem)">APPENDIX</h1>
 <p class="lede" style="max-width:56ch;margin:0 auto">What was checked, which of our own results we withdrew, and the questions we left open.</p></div></section>''')

# A0 the pattern that started Part 1 (moved from the main flow; slide 8 summarizes it)
slide("Appendix · the pattern behind Part 1","The apparent law of judge failure, in full",
 '''<p>Early on we noticed an interesting pattern: count how many of the small judges a wrong solution fools, and
 you can predict almost perfectly whether the frontier judge is fooled too. Zero small
 judges fooled: the frontier fails 1% of the time. All three of the small judges fooled: <b>94%</b>. It looked like a cheap early-warning system for frontier
 failures.</p>
 <p>Before writing it up, we hand-checked every one of the 55 cases behind the 94%. Most were not judge failures
 at all. They were <b>correct answers that the benchmark had marked wrong</b>. The judges were right; the answer
 key was not.</p>'''+
 fig("f1_mirage","Left: the apparent law. Right: what checking all 55 cases revealed. 71% were benchmark labeling errors, and on the genuinely wrong solutions the frontier judge failed only 6% of the time.")+
 '<div class="take">Two other promising effects turned out the same way when we checked their cases. That changed how we ran everything that follows.</div>')

# A1 integrity record
slide("Appendix · the record","What was checked, and how",
 chips(("15","findings"),("6","preliminary results withdrawn after failing our own checks"),("1","public retraction with correction"),("4","independent critic passes"))+
 '''<p>Every headline number was re-derived from the raw files with fresh code. Planted code errors were re-executed
 against the official test suites. The answer-key findings rest on two frontier model families agreeing on all 55
 disputed cases we re-checked, plus the external check against a human re-annotation. We also read the closest
 prior paper carefully to confirm the reference-harm result is new: that paper tests only single-answer tasks,
 scores one response at a time, and has no control conditions like ours.</p>''')

# A2 open questions
slide("Appendix · open questions","What we did not settle",
 '''<ul>
 <li><b>Can a model verify only what it could itself generate?</b> That hypothesis is common in the field. The
 correlation we saw item by item is weak; a proper answer needs more data.</li>
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
