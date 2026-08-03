# Build the v2 TFA story deck (paper/slides_v2.html), revised end-to-end from Brando's review:
#   takeaway stated on slide 1-2, terminology defined before first use, every headline correlation
#   reported in triplicate (Pearson/r^2, Spearman, Kendall), correlations shown as a histogram,
#   the SWE-bench figure redrawn in the same arrow-per-family grammar, precise log-prob wording,
#   path-forward reframed as "reliable metrics WITH gold references", an APPENDIX divider, and the
#   inside-baseball slides (reconciliation, saturation detail, program) moved behind it.
import base64, json, pathlib
FIGDIR = pathlib.Path("paper/figs")
def datauri(fn): return "data:image/png;base64," + base64.b64encode((FIGDIR/fn).read_bytes()).decode()
IMG = {k: datauri(v) for k, v in {
 "f1":"fig1_model_level.png","f6":"fig7_mechanism.png","judge":"fig_judge.png","f3":"fig3_saturation.png",
 "f5":"fig6_cross_family.png","f7":"fig10_reconciliation.png","f9":"fig8_agentic_v2.png","f2":"fig2_difficulty_gradient.png",
 "f10":"fig9_mechanism.png","var":"fig_variants.png","f8":"fig5_rollout_completer_curve.png","ms":"fig_ms_multistat.png",
}.items()}
MS = json.load(open("runs/multistat.json"))
def fig(k,cap): return f'<figure class="fig"><img src="{IMG[k]}" alt="{cap}"/><figcaption>{cap}</figcaption></figure>'
def chips(*cs): return '<div class="chips">'+''.join(f'<div class="chip"><span class="cn">{n}</span><span class="cl">{l}</span></div>' for n,l in cs)+'</div>'
S=[]
def slide(kick,title,body,cls=""): S.append(f'<section class="slide {cls}"><div class="wrap"><div class="kick">{kick}</div><h2>{title}</h2>{body}</div></section>')
def refslide(kick,title,verdict,refs,edge):
 items="".join(f'<li><b>{t}</b> <span class="cite">{c}</span><br><span class="rd">{d}</span></li>' for t,c,d in refs)
 slide(kick,title,f'<div class="chips"><div class="chip"><span class="cn">{verdict}</span><span class="cl">novelty verdict</span></div></div><ul class="refs">{items}</ul><div class="take">{edge}</div>')

# ---- the boundary table, all three statistics, from runs/multistat.json ----
TORDER = ["Putnam-AXIOM","Omni-MATH (olympiad)","MATH-500","Putnam-Variations","MATH (full)",
          "HumanEval (code)","GSM8K","GSM8K-Platinum"]
def trow(lab):
    c = MS["cross_family"][lab]
    cls = ' class="neg"' if c["spearman"] < 0 else ""
    return (f'<tr{cls}><td>{lab}</td><td>{c["pearson"]:+.2f}</td><td>{c["pearson"]**2:.2f}</td>'
            f'<td>{c["spearman"]:+.2f}</td><td>{c["kendall"]:+.2f}</td><td>{c["n"]}</td></tr>')
TABLE = ('<table class="mini"><tr><th>dataset (all 17 models pooled)</th><th>Pearson r</th><th>r&sup2;</th>'
         '<th>Spearman &rho;</th><th>Kendall &tau;</th><th>n models</th></tr>'
         + "".join(trow(l) for l in TORDER) + '</table>'
         '<p style="font-size:.85rem;color:var(--mut);max-width:80ch">ICC is not reported because TFA and accuracy live on '
         'different scales; the consistency ICC on standardized scores reduces to Pearson r for two measures, so r and '
         'r&sup2; carry that information. All three reported statistics agree in sign on every row.</p>')

# 1 title: the takeaway is ON the title slide
S.append('''<section class="slide title"><div class="wrap">
 <div class="kick">Stanford · Koyejo Group · judge-free evaluation · v2, revised after Brando's review</div>
 <h1>Grading models against a gold reference<br><span class="hl">measures skill on hard tasks, style on easy ones</span></h1>
 <p class="lede">Can you score models without an LLM judge, by checking their work against a benchmark's gold
 solutions? We tested the sharpest version of that idea: TFA, which scores a model by how well it predicts the
 reference solution token by token. Seventeen models, seven families, eight math and code benchmarks. On hard
 problems it gives you a real leaderboard: models that predict the reference well are the models that solve
 problems well. On easy, saturated benchmarks that connection goes away, because everyone predicts the reference
 about equally well and the leftover differences are writing style, not skill; on GSM8K the ranking actually flips.</p>
 <div class="meta">17 models · 7 families · 8 datasets (math · olympiad · code) · every headline correlation reported as Pearson r / r&sup2; + Spearman ρ + Kendall τ</div>
 <div class="hint">scroll or press → to advance</div></div></section>''')

# 2 takeaway
slide("The takeaway","Three results, stated up front",
 chips(("+0.86 / +0.84 / +0.71","hard math: ρ / r / τ, TFA vs accuracy"),("&minus;0.25 / &minus;0.14 / &minus;0.16","saturated GSM8K: ρ / r / τ"),("&approx; 0","grading one solution, all variants"))+
 '''<div class="cols"><div>
 <h3 class="g">1 &middot; TFA can rank models, if the benchmark is hard</h3>
 <p>We compared mean TFA to accuracy for 17 models from 7 families. On Putnam and olympiad math the two agree
 closely. The agreement fades as benchmarks get easier, and on GSM8K it goes <b class="r">negative</b>: the models
 with the best TFA are not the most accurate ones. Same story on SWE-bench: TFA ranks the four Qwen-Coder sizes
 correctly, and tells you nothing when comparing across families.</p>
 <h3 class="p">2 &middot; TFA cannot grade a single solution</h3>
 <p>We checked whether a solution's TFA tracks the grade a judge gives that solution. It does not: 89-96% of what
 per-solution TFA measures is how predictable the reference text is, which says nothing about the solution being
 graded. We tried seven fixes and none recovered a signal. Earlier work assumed TFA could stand in for a judge here;
 as far as we can tell, nobody had actually tested it.</p></div>
 <div>
 <h3 class="a">3 &middot; Grading without a judge is possible, just expensive</h3>
 <p>One thing did grade: cut a solution off partway, have a fixed model finish it, and check whether it still lands
 on the right answer. That correlates +0.43 with the judge's grade and even tells sound solutions from lucky ones.
 The catch: it needs many completions per solution, roughly 100x the compute of TFA.</p>
 <div class="def"><b>The reason behind all three.</b> On a hard problem, predicting the reference's next step takes
 the same skill as solving the problem. On an easy problem everyone can predict it, so whatever differences remain
 come from formatting and phrasing. When the benchmark is easy, that is all TFA has left to measure.</div></div></div>''')

# 3 terminology
slide("Terms used in this deck","Five terms, defined before we use them",
 '''<div class="cols"><div>
 <div class="def"><b>TFA (Teacher-Forced Accuracy).</b> Give the model the problem, then feed it the gold solution
 one token at a time. At each position, ask: would the model have predicted this next token itself? TFA is the
 fraction of positions where the answer is yes. It takes one deterministic forward pass, and no judge or rubric is
 involved anywhere.</div>
 <div class="def"><b>Model-level correlation.</b> Answers: can TFA build a leaderboard? Each model gets one number,
 its average TFA over all problems, and we correlate that with its accuracy across the 17 models. If the most
 accurate model also has the highest average TFA, the second most accurate the second highest, and so on, Spearman
 ρ comes out +1.</div></div>
 <div>
 <div class="def"><b>Item-level correlation.</b> Answers: can TFA grade one answer? Take a single solution and ask
 whether its TFA tracks the grade a judge gives it, after right-vs-wrong is factored out (a partial correlation
 controlling for correctness). Concretely: the judge gives one solution 0.8 and another 0.3; a grader worth using
 should score the first clearly higher, even when both end on the correct answer. That is the bar TFA has to clear.</div>
 <div class="def"><b>Saturated benchmark.</b> One where every reasonable model scores near the ceiling; on GSM8K,
 every strong model is above 95%. With that little room for skill to differ, whatever still differs between models
 is mostly style.</div>
 <div class="def"><b>The boundary (map).</b> Our shorthand for the table and figure that record, dataset by dataset,
 where model-level TFA works and where it fails: clearly positive on hard math, weaker on code, negative on
 saturated data. When we say SWE-bench "lands on the map", we mean coding agents show the same pattern the map
 predicts.</div></div></div>
 <p class="q">One reporting rule for the whole deck: every headline correlation appears three ways, <b>Pearson r</b>
 (with r&sup2;), <b>Spearman ρ</b> (rank order), and <b>Kendall τ</b> (pairwise orderings). Where a figure caption
 shows only one, the other two are in the table on the boundary-map slide.</p>''')

# 4 within family
slide("Result 1 &middot; ranking &middot; within a family","Start inside one family: TFA tracks accuracy across the Qwen ladder",
 chips(("+0.80 to +0.97","Pearson r, within-Qwen, 8 datasets"),("+0.60 to +1.00","Spearman ρ"),("+0.40 to +1.00","Kendall τ"))+
 '<p>We start with the cleanest comparison we have: five Qwen models, 0.5B to 14B, each reduced to one average-TFA number and one accuracy number per dataset. The left panel plots the correlation between the two under all three statistics. It is positive on all eight datasets, and the weakest values sit on the two datasets where accuracy is closest to the ceiling (MATH-full and GSM8K-Platinum). The right panel widens the view. In total we have 29 family ladders (one family\'s sizes on one dataset), and their correlations form a histogram with two lobes: on hard benchmarks the ladders pile up near +1.0, while on saturated benchmarks and code they spread out and some go negative.</p>'+
 fig("ms","Left: within-Qwen TFA-vs-accuracy correlation under Pearson, Spearman, and Kendall, per dataset (n=5 models each); all values are positive, so the axis starts at zero. Right: histogram of all 29 family-ladder Spearman correlations, colored by whether the dataset is hard or saturated/code.")+
 '<div class="take">Inside one family TFA orders models correctly. The histogram also shows where that stops: as soon as the benchmark gets easy.</div>')

# 5 across families
slide("Result 1 &middot; ranking &middot; across families","Across families it holds on hard math and scrambles on saturated data",
 '''<p>Now add Mistral, Phi, OLMo, and the math-specialized families. Each arrow below is one family's size ladder,
 tail at its smallest model, head at its largest. On hard data (Putnam, MATH-500) the arrows point up-right: a bigger,
 better model predicts the gold better, whatever family it comes from. As the data gets easier the arrows flatten and
 scatter, and on GSM8K Phi's and OLMo's arrows point <b class="r">down</b>: their stronger models solve more problems
 but answer in a fuller, more labeled style than the terse gold, so they predict it worse.</p>'''+
 fig("f6","Each arrow is one family's size ladder in (mean TFA, accuracy) space, tail = smallest model, head = largest. Up-right on hard data; flat, scattered, and partly inverted on saturated data. The same arrow grammar is used on every such figure in this deck, including the agents one.")+
 '<div class="take">On saturated data a family\'s house style moves TFA more than its skill does. That is the whole failure mode.</div>')

# 6 boundary + table
slide("Result 1 &middot; ranking &middot; the full map","The boundary, with every correlation in triplicate",
 '<p>Pooling all 17 models on each dataset gives the full map, as a figure and as a table. The three statistics agree in sign on every dataset: clearly positive on hard and olympiad math, noisier but positive on code, near zero to negative on saturated grade-school math.</p>'+
 TABLE+
 fig("f5","The same map as the table, drawn with 95% bootstrap confidence intervals over models (Spearman). Green = hard references, orange = saturated, purple = code.")+
 '<p style="font-size:.92rem;color:var(--mut)">Provenance: these values use the repaired answer-matching scorer; the original scorer mis-graded 4-10% of GSM8K-style answers and overstated the inversion (previously &minus;0.37/&minus;0.38, now &minus;0.25/&minus;0.19). The qualitative map is unchanged. Why saturation does this, mechanically, is one slide in the appendix (TFA range compresses 3x on easy data).</p>'+
 '<div class="take">Use TFA as a leaderboard only where the reference is hard; never on a saturated benchmark.</div>')

# 7 agents, same grammar
slide("Result 1 &middot; ranking &middot; coding agents","The same pattern on SWE-bench, drawn the same way",
 chips(("+1.00 / +0.98 / +1.00","within Qwen-Coder: ρ / r / τ (n=4)"),("+0.00 / &minus;0.24 / +0.00","across 4 families: ρ / r / τ (n=8)"))+
 '<p>Same experiment, agentic setting: teacher-force the gold repository patch on SWE-bench and compare patch-TFA to coding ability. Same figure grammar as the math slide: one arrow per family ladder. The Qwen-Coder arrow (4 sizes) points up-right, a perfect within-family ranking. The CodeLlama arrow points down-right: it reproduces the gold patch style best while writing the worst code, the repository version of the GSM8K style trap. Two families ship only one size, so they appear as single diamonds, marked as such.</p>'+
 fig("f9","SWE-bench patch-TFA vs HumanEval pass@1, one arrow per coder family (tail = smallest, head = largest). Up-right within Qwen-Coder; no cross-family relationship; CodeLlama is the high-style/low-skill outlier.")+
 '<div class="take">For agents, same conclusion in plain words: TFA can rank sizes inside one model family, and it cannot compare models across families.</div>')

# 8 item level
slide("Result 2 &middot; grading &middot; the test","Can TFA grade one solution? No.",
 chips(("&approx; 0","MATH-500 (item-level partial ρ)"),("+0.12","GSM8K"),("+0.22","Putnam")) +
 '<div class="def"><b>Reminder of the definition.</b> Item-level means: for one single solution, does TFA track the judge\'s grade for that solution once right-vs-wrong is removed (partial correlation controlling for correctness)? This is the property you would need to <b>replace a judge</b> with TFA. The statistic here is partial Spearman ρ; the target must be a graded score (a judge, or human grades), because among correct answers plain accuracy has no variance left to correlate with.</div>'+
 '<p>The answer is no. The signal is zero on MATH, small on GSM8K, and +0.22 at best on the hardest math. The small values are real (they survive label-noise and contamination controls, and replicate under a second judge from a different model family, appendix), but under 5% of variance is far too little to grade with.</p>'+
 fig("f2","Item-level partial correlation between TFA and the judge grade, controlling for correctness: ~0 on MATH, small on GSM8K, largest but still weak on Putnam.")+
 '<div class="take">TFA is a leaderboard signal, not a grader. The next slide shows why, with a number.</div>')

# 9 why
slide("Result 2 &middot; grading &middot; the reason","89-96% of per-item TFA is about the reference, not the solution",
 chips(("89-96%","of per-item variance: reference nuisance"),("4-11%","left over for solution quality"))+
 '<p>Decompose per-item TFA across the model x item grid: after removing each model\'s overall level, <b>89-96% of the remaining variation is identical for every model</b>. It is a fact about the reference (how predictable this particular gold text is), not about the solution being graded. Because it is identical across models it cancels when you average over items, which is why ranking works, and it buries the 4-11% that is actually about quality, which is why grading fails. The full recipe with a worked toy example is in the appendix.</p>'+
 fig("f10","Variance decomposition of per-item TFA on the Qwen ladder: the model-invariant reference component is 89-96% on every dataset.")+
 '<div class="take">The same number predicts that no reweighting of TFA can fix grading. We tested that prediction seven ways.</div>')

# 10 fixes, merged
slide("Result 2 &middot; grading &middot; seven repairs, all fail","If the signal were merely buried, one of these would have found it",
 '''<p>Each repair removes one component of the nuisance: <b class="a">content-token TFA</b> (mask formatting),
 <b class="a">IDF weighting</b> (up-weight rare tokens), <b class="a">surprisal weighting</b> (up-weight non-formulaic
 tokens), <b class="a">soft log-prob instead of hard match</b>, <b class="p">step-shuffle contrast</b> (gold minus
 reordered gold), <b class="p">answer-swap contrast</b> (gold minus wrong-answer gold), <b class="g">multi-reference
 max</b> (best TFA over several golds). All seven land at zero, and the reweightings go slightly negative: the
 surprising tokens are exactly the ones good models also miss.</p>'''+
 '<p style="font-size:.98rem"><b>One cautionary tale we keep on purpose.</b> The answer-swap contrast first looked like a +0.35 win. It was a length artifact (the corruption touched only the final token, so the contrast collapsed to "right answer, divided by length"). Controlling for length dropped it to zero, and we retracted it. House rule since: no item-level win is believed until it survives length and difficulty controls.</p>'+
 fig("var","Item-level correlation for each of the seven repairs: all at or below zero. The signal is absent, not masked.")+
 '<div class="take">Seven misses plus the 89-96% decomposition: per-item TFA has no quality signal to recover.</div>')

# 11 rollout
slide("Result 3 &middot; a signal that does grade","Rollout process value grades solutions, at ~100x the cost",
 chips(("+0.43","rollout value vs judge grade (ρ)"),("+0.19","separates sound from lucky corrects"),("~100x","cost multiple vs TFA"))+
 '<p>Drop the reference entirely and measure the solution\'s own trajectory: truncate it partway, let a fixed completer model finish it, and score whether the completion still reaches the right answer. Averaged over truncation points this "process value" correlates +0.43 with the judge\'s grade at item level, exactly where TFA sits at zero, and it even separates solutions that are correct <i>for sound reasons</i> from solutions that are correct by luck (+0.19 among corrects only). The catch is compute: many completions per solution instead of one forward pass, roughly a hundredfold.</p>'+
 fig("f8","Rollout process value vs the judge grade as a function of completer strength: a mid-strength (14B) completer is the sweet spot; too weak cannot finish sound work, too strong rescues broken work.")+
 '<div class="take">Grading is possible without a judge, just not cheaply yet. Making this cheap is a real open problem.</div>')

# 12 conclusions
S.append('''<section class="slide concl"><div class="wrap"><div class="kick">Conclusions</div>
 <h2>What we showed, what is new</h2>
 <div class="cols"><div><h3>The one-sentence version</h3>
   <p><b>TFA measures agreement with the reference's <span class="p">style</span>; only on hard data does style move
   with <span class="g">skill</span>.</b> Everything in this deck is that sentence quantified. And though TFA is the
   metric we tested, the mechanism belongs to the whole class: any reference-matching metric inherits it.</p>
   <ul><li><b>Leaderboards:</b> trustworthy within a family and on hard references (ρ, r, τ all positive); untrustworthy on saturated benchmarks (all three negative on GSM8K).</li>
   <li><b>Grading single solutions:</b> fails; 89-96% of the per-item signal belongs to the reference; seven repairs all land at zero.</li>
   <li><b>Rollout process value</b> does grade, at ~100x cost.</li>
   <li><b>Agents:</b> the identical within-family / cross-family split on SWE-bench patches.</li></ul></div>
   <div class="new"><h3>Contributions</h3>
   <ol><li><b>First direct test</b> of TFA's item-level grading claim; it fails, and prior work had assumed it.</li>
   <li><b>The mechanism</b>: the 89-96% reference-nuisance decomposition that explains both verdicts at once.</li>
   <li><b>The boundary map</b> in triplicate statistics across 17 models, 7 families, 8 datasets, plus agents.</li>
   <li><b>A grading signal that works</b> (rollout process value) with its cost curve.</li></ol></div></div></div></section>''')

# 13 path forward, reframed
slide("Path forward","Our lane: reliable metrics <b>with</b> gold references",
 '''<p>Benchmarks and leaderboards already own gold answers; what they lack is a trustworthy way to use them without
 hiring an LLM judge for every submission. That is the problem this line of work attacks: <b>cheap, deterministic,
 auditable scoring where a gold reference exists</b>. It is deliberately not the harder problem of evaluation with
 <b>no</b> gold references (debate, and TVD-MI-style mechanism design). We think the with-references problem is worth
 solving on its own: it is more tractable precisely because the answer is known, and it is load-bearing because the
 field's leaderboards run on it.</p>
 <div class="cols"><div><h3 class="g">Design stances</h3>
 <ul><li><b>Trained metrics are allowed.</b> A metric trained <i>offline</i> and then frozen is much harder to game
 than a reward model optimized against during RL; specializing a judge to a benchmark with in-context historic
 answers (the "Master of One" autorater recipe, arXiv:2411.15387) is a template worth adapting.</li>
 <li><b>Name the threat model.</b> "Survives gaming" means different things at <b>eval time</b> (style mimicry,
 contamination, benchmark-specific tuning) and at <b>train time</b> (RL directly against the metric). We test
 eval-time robustness first; train-time robustness is a separate, harder experiment.</li></ul></div>
 <div><h3 class="p">Constraints and neighbors</h3>
 <ul><li><b>Practical constraint, stated precisely:</b> most frontier APIs return no (or only top-k) token
 log-probabilities, so teacher-forcing on frontier models is <b>impractical today</b>: expensive or noisy, not
 impossible in principle. Near-term work therefore runs on open weights or on output-based signals.</li>
 <li><b>Neighbors we build on, not against:</b> debate-based oversight (Aryan and Eric's paper,
 openreview.net/forum?id=MDArMFusA7) and reference-free mechanism design (TVD-MI) target the no-gold-reference
 regime; our boundary map says where the cheap with-reference signals stop working, which is exactly where those
 methods need to take over.</li></ul></div></div>
 <div class="take">One map, two lanes: with references, make scoring judge-free and auditable; without references, know from the map that you have crossed into the regime where debate and mechanism design are the right tools.</div>''')

# 14 appendix divider
S.append('''<section class="slide divider"><div class="wrap" style="text-align:center">
 <div class="kick">everything after this slide is backup</div>
 <h1 style="font-size:clamp(3rem,8vw,6rem)">APPENDIX</h1>
 <p class="lede" style="max-width:56ch;margin:0 auto">Saturation mechanics, the reconciliation with the original TFA
 paper, judge-robustness checks, the full nuisance-decomposition recipe, the scalable-oversight program (the
 no-gold-references lane), and per-question prior work.</p></div></section>''')

# A1 saturation detail
slide("Appendix &middot; saturation mechanics","Why easy data kills the signal: the TFA range collapses 3x",
 chips(("~0.03","TFA range across the ladder, GSM8K"),("~0.08","TFA range, Putnam"))+
 '<p>On near-ceiling data the whole 5-model ladder is squeezed into a 0.03-wide TFA band; on hard data the band is three times wider. When the skill-driven spread shrinks below the size of a family style offset, style wins and rankings can invert. This is the mechanical link between the histogram\'s two lobes on the within-family slide.</p>'+
 fig("f3","TFA compresses on easy data and spreads on hard data; discriminating power tracks distance from ceiling.")+
 fig("f1","Backup: the raw within-Qwen model-level scatter per dataset behind the multi-statistic panel."))

# A2 reconciliation
slide("Appendix &middot; reconciliation","The original TFA paper's 0.66 is our Kendall τ on the full model set",
 '<p>Putnam-AXIOM reported TFA-vs-accuracy at <b>0.66 (MATH)</b> and <b>0.52 (Putnam)</b>, well below our within-family values. There is no disagreement, only a metric and model-set difference, which the triplicate-statistics habit makes visible immediately: their 0.66 matches our <b>Kendall τ on the full 17-model set including the math-specialized outliers</b> (Qwen-Math, DeepSeek-Math, Mathstral, which reproduce gold style beyond their skill); dropping those outliers and reading Spearman recovers +0.86/+0.88.</p>'+
 fig("f7","Our correlation under four statistics x two model sets, against the reported 0.66 / 0.52: the reported numbers are one cell of this grid.")+
 '<div class="take">Two papers, one dataset, no contradiction, and a live demonstration of why single-statistic reporting misleads.</div>')

# A3 judge robustness
slide("Appendix &middot; judge robustness","The item-level conclusions do not depend on which judge we appointed",
 chips(("0.75-0.94","inter-judge agreement (ρ)"),("2 judge families","gpt-5.2 and Claude Opus 4.8"))+
 '<p>The ranking results are judge-free (TFA vs accuracy). The item-level results are the only judge-defined ones, so we re-graded the three anchor datasets with a second frontier judge from a different model family under the same rubric: the MATH null stays null, the small GSM8K and Putnam signals replicate with confidence intervals excluding zero.</p>'+
 fig("judge","Item-level partial ρ under two frontier judges from different families: same conclusions under both."))

# A4 nuisance recipe
slide("Appendix &middot; the nuisance decomposition","The 89-96%, step by step, with a toy example",
 chips(("94.6%","MATH-500"),("88.9%","MATH-full"),("89.1%","GSM8K"),("96.1%","Putnam"))+
 '<div class="cols"><div>'+
 '<h3 class="g">The recipe (a one-way ANOVA on the reference)</h3>'+
 '<ol><li><b>Build the grid.</b> T[model, item] = per-item TFA for the 5-model Qwen ladder on the shared problems.</li>'+
 '<li><b>Remove each model\'s level.</b> Subtract each model\'s own mean: D = T minus its row mean. This strips overall generosity (the ranking axis), leaving item-to-item variation.</li>'+
 '<li><b>Find the shared part.</b> Average each item\'s column across models: b[item], the deviation identical for every model, a fact about the reference.</li>'+
 '<li><b>Take the ratio.</b> nuisance = &Sigma;b&sup2; / &Sigma;D&sup2; = 89-96% on every dataset; the leftover 4-11% is the model-specific residual grading would need.</li></ol>'+
 '<p style="font-size:.9rem;color:var(--mut)">Reproducible via <span style="font-family:ui-monospace,Menlo,monospace">scripts/variance_decomp.py</span>.</p>'+
 '</div><div>'+
 '<h3 class="p">A two-model, three-item toy</h3>'+
 '<table class="mini"><tr><th></th><th>item 1</th><th>item 2</th><th>item 3</th><th>row mean</th></tr>'+
 '<tr><td>Model A</td><td>0.70</td><td>0.80</td><td>0.90</td><td>0.80</td></tr>'+
 '<tr><td>Model B</td><td>0.74</td><td>0.84</td><td>0.94</td><td>0.84</td></tr></table>'+
 '<p style="font-size:.98rem">Center each row and both become [&minus;.10, 0, +.10]: the item effect explains everything, nuisance = 100%. Item 3 is easier to reproduce for <i>both</i> models by the same amount, so nothing distinguishes them per-item; the uniform +0.04 on Model B is the ranking axis, removed in step 2.</p>'+
 '<div class="def" style="font-size:.95rem"><b>Why one number gives both verdicts.</b> Identical-across-models means it cancels in the average (ranking survives) and swamps any single item (grading dies).</div>'+
 '</div></div>')

# A5 the oversight program (the other lane), with Brando's caveats attached
slide("Appendix &middot; the other lane","The scalable-oversight program (no-gold-references), for discussion",
 '<div class="def"><b>Status: framing under discussion.</b> This program targets the regime <b>without</b> gold references, the reverse of the deck\'s main lane, and is kept here as the long-horizon agenda. Two design stances updated after review: trained-offline metrics are admissible (they are hard to game outside RL loops), and every robustness claim must name its threat model, eval-time gaming vs train-time optimization against the metric.</div>'+
 '<div class="cols"><div>'+
 '<h3 class="ac">1 &middot; The yardstick</h3><p>With little ground truth, split a judge\'s score into real quality signal vs surface nuisance from a small labeled anchor. Everything below needs this number.</p>'+
 '<h3 class="g">2 &middot; Survives smarter models</h3><p>Does judge reliability fall predictably as the judged model outgrows the judge, and does the nuisance fraction predict the slope?</p>'+
 '<h3 class="r">3 &middot; Survives optimization</h3><p>When a model is optimized against the judge (train-time threat model), which judges break, and is that predictable ex ante from the nuisance fraction?</p></div>'+
 '<div>'+
 '<h3 class="p">4 &middot; Design</h3><p>What lowers the nuisance fraction: environment-grounded process signals, ensembles, consistency, debate, offline-trained specialized judges (arXiv:2411.15387)?</p>'+
 '<h3 class="a">5 &middot; The floor</h3><p>Is there an open-ended regime where no cheap judge survives and the honest design keeps a human or an environment oracle in the loop?</p></div></div>'+
 '<div class="take">The spine is one static quantity, the nuisance fraction, predicting both capability-gap collapse and hackability. Whether to pivot the group\'s effort to this lane is exactly the discussion to have.</div>')

# A6+ prior work
refslide("Appendix &middot; prior work &middot; capability gap","Oversight reliability vs the capability gap","PARTIAL",
 [("Scaling Laws for Scalable Oversight","arXiv:2504.18530","Engels et al. 2025. Plots oversight success against the overseer-overseen capability gap across several games."),
  ("A Benchmark for Scalable Oversight Protocols","arXiv:2504.03731","Sudhir, Kaunismaa, Panickssery 2025. Agent Score Difference: a scalar honesty-at-parity score, not a curve."),
  ("Scalable oversight with weak LLMs judging strong LLMs","arXiv:2407.04622","Kenton et al. 2024. Judge accuracy vs the debater-judge gap, inference-only."),
  ("Debate paper (Aryan and Eric)","openreview.net/forum?id=MDArMFusA7","Flagged by Brando as directly relevant to the oversight-program slide; to be integrated after reading.")],
 "Engels already draws the capability-gap curve, on game Elo. Unclaimed: the optimization-pressure axis and grounding capability in real math, code, and agentic domains.")

refslide("Appendix &middot; prior work &middot; surface vs quality","Do cheap evaluators score surface, not quality","PARTIAL",
 [("JudgeBench","arXiv:2410.12784","Tan et al. 2024. Frontier judges near chance at picking the objectively correct answer over the stylish one."),
  ("Style Over Substance","arXiv:2307.03025","Wu and Aji 2023 (also Feuer et al. 2024). Fluent-but-wrong beats plain-but-right."),
  ("Length-Controlled AlpacaEval","arXiv:2404.04475","Dubois et al. 2024. Partials out length as a mediator, one nuisance only."),
  ("From Jack of All Trades to Master of One","arXiv:2411.15387","Specialized offline autoraters stabilized with in-context historic answers; Brando's template for trustworthy trained metrics.")],
 "Each shows or removes one bias; none reports the surface-nuisance fraction of score variance as the headline. Our decomposition does.")

refslide("Appendix &middot; prior work &middot; verification vs generation","Is judging quality easier than generating","mostly UNCLAIMED",
 [("Weaver: Shrinking the Generation-Verification Gap","arXiv:2506.18203","Saad-Falcon, Song et al. 2025. Weak-verifier ensembles, correctness selection only."),
  ("Generator-Validator Consistency","arXiv:2310.01846","Li et al. 2023. GV-consistency, still correctness / true-false."),
  ("LLMs Cannot Self-Correct Reasoning Yet","arXiv:2310.01798","Huang et al. 2023. Self-verification fails without external feedback."),
  ("TVD-MI mechanism design (Robertson)","no-gold-references lane","Peer-prediction-style evaluation without gold references; the harder neighboring problem our boundary map hands off to.")],
 "All correctness-only. Unclaimed: whether judging quality among already-correct answers is easier than producing a good one.")

refslide("Appendix &middot; prior work &middot; gaming","Can we predict which evaluators get gamed","PARTIAL / UNCLAIMED",
 [("Scaling Laws for Reward Model Overoptimization","arXiv:2210.10760","Gao et al. 2023. Overoptimization magnitude from KL and RM size, during optimization (train-time threat model)."),
  ("Defining and Characterizing Reward Hacking","arXiv:2209.13085","Skalse et al. 2022. Unhackability is near-impossible, a theoretical property."),
  ("A Long Way to Go: Length Correlations in RLHF","arXiv:2310.03716","Singhal et al. 2023. One nuisance feature, length, drives most of the hacking."),
  ("Helping or Herding?","arXiv:2312.09244","Eisenstein et al. 2023. Shared systematic reward-model error survives ensembling and still gets hacked.")],
 "None forecasts hackability ex ante from a static surface-nuisance property, and few separate the eval-time from the train-time threat model explicitly.")

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
.mini{border-collapse:collapse;font-family:ui-monospace,Menlo,monospace;font-size:.9rem;margin:8px 0 12px}
.mini th,.mini td{border:1px solid var(--line);padding:5px 11px;text-align:right;font-variant-numeric:tabular-nums}
.mini th{color:var(--mut);font-weight:600;background:color-mix(in srgb,var(--accent) 7%,var(--panel))}
.mini td:first-child,.mini th:first-child{text-align:left;color:var(--ink);font-weight:700}
.mini tr.neg td{color:var(--r)}
.refs{font-size:.98rem;max-width:82ch}.refs li{margin:.55em 0}
.cite{font-family:ui-monospace,Menlo,monospace;font-size:.78em;color:var(--accent)}
.rd{color:var(--mut);font-size:.92rem}
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
html='<title>Judge-free grading against references: skill on hard tasks, style on easy</title>'+STYLE+'<div class="rail"></div><button class="toggle">◐ theme</button><div class="counter"></div><div class="deck">'+"".join(S)+'</div>'+SCRIPT
out="paper/slides_v2.html"
open(out,"w").write(html); print("wrote",out,"slides:",len(S),"bytes:",len(html))
