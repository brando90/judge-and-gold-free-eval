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
def refslide(kick,title,verdict,refs,edge):
 items="".join(f'<li><b>{t}</b> <span class="cite">{c}</span><br><span class="rd">{d}</span></li>' for t,c,d in refs)
 slide(kick,title,f'<div class="chips"><div class="chip"><span class="cn">{verdict}</span><span class="cl">novelty verdict</span></div></div><ul class="refs">{items}</ul><div class="take">{edge}</div>')

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
 chips(("+0.86","Omni-MATH"),("+0.60","Putnam"),("+0.43","code"),("&minus;0.25","GSM8K"))+
 '<p>Pooling all families across all eight datasets gives one boundary map. It holds on hard, constrained references, weakens on code (many valid programs), and <b class="a">inverts</b> on saturated grade-school math (GSM8K &minus;0.25, GSM8K-Platinum &minus;0.19). Numbers reflect a repaired answer-matching scorer: a follow-up oversight study found the original scorer mis-graded 4-10% of GSM8K-style answers, which had overstated the inversion (previously reported as &minus;0.37/&minus;0.38); the qualitative boundary is unchanged.</p>'+
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
 '<div class="def" style="font-size:.95rem"><b>Why a judge here, not accuracy?</b> Grading a solution means scoring quality <i>beyond</i> right-or-wrong. Accuracy is binary and is exactly what we control for, and among the correct answers it has no variance at all, so ρ(TFA, accuracy | correct) is undefined. The item-level target has to be <b>graded</b> (a judge, or human grades). Model ranking (Q1) is the judge-free, accuracy-based half; robustness to the choice of judge is in the appendix.</div>'+
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

# 17 the program (committed research program; alternative-bets framing + prior work in appendix)
slide("Path forward &middot; the program","Reliable judges without ground truth",
 '<p>One mission: build judges that stay reliable when they are <b>optimized against</b> and when the model they judge is <b>smarter than them</b>, in domains with little ground truth, and measure it. Five steps, in <b>dependency order</b>.</p>'+
 '<div class="cols"><div>'+
 '<h3 class="ac">1 &middot; The yardstick</h3><p>With little ground truth, how do you tell a good judge from a bad one? Split its score into real quality vs surface nuisance (the nuisance fraction) from a small anchor. A <b>mechanism, not a trained metric</b>, so it cannot itself be gamed. Everything below needs this number.</p>'+
 '<h3 class="g">2 &middot; Survives smarter models</h3><p>Does reliability fall predictably as the judged model outgrows the judge, and does the yardstick predict the fall? Plot reliability against the capability gap; test whether the nuisance fraction predicts the slope.</p>'+
 '<h3 class="r">3 &middot; Survives reward hacking</h3><p>When a model is optimized against the judge, does it break, and can we predict which judges break <b>before</b> optimizing, from the nuisance fraction?</p></div>'+
 '<div>'+
 '<h3 class="p">4 &middot; Design</h3><p>What construction survives both axes, especially where ground truth is scarce: reference-free and process signals grounded in an environment oracle, ensembles, consistency, debate? Build candidates, score them with step 1, keep what lowers the nuisance fraction and flattens the curves.</p>'+
 '<h3 class="a">5 &middot; The floor</h3><p>Is there an open-ended regime where no cheap judge survives, so the honest design keeps a human or an environment oracle in the loop? Find where the nuisance fraction cannot be driven down.</p></div></div>'+
 '<div class="take">The spine: one static, mechanism-based quantity, the nuisance fraction, that predicts <b>both</b> capability-gap collapse and hackability. That is what makes this one program, not five errands.</div>')

# 18 appendix: the alternative bets (the earlier independent-questions framing)
slide("Appendix &middot; alternative bets","The five as separate bets",
 '<p>Before the program above, these were the five as <b>independent</b> bets to choose between. Each is a different generalization of our result; the program folds them into one dependency chain. Prior-work grounding for each follows.</p>'+
 '<div class="cols"><div>'+
 '<h3 class="g">As AI gets more capable than the methods we use to check it, does our ability to catch its mistakes break down in a predictable way?</h3><p>If we can plot that breakdown as a curve, we can tell which checking methods will still hold up as models keep improving, instead of only comparing them on the models we have now.</p>'+
 '<h3 class="p">When we grade AI answers cheaply and automatically, are we measuring whether the answer looks right, or whether it is right?</h3><p>Our result suggests cheap graders, including using one AI to judge another, mostly reward answers that resemble the reference, not answers that are actually better.</p>'+
 '<h3 class="a">Is telling a good answer from a bad one really easier than producing a good answer in the first place?</h3><p>We found that judging plain correctness is easy but judging quality is not, so the assumption that checking is easier than doing may only hold for right-or-wrong tasks.</p></div>'+
 '<div>'+
 '<h3 class="r">If we train an AI to score well on a cheap evaluator, does that evaluator stop being trustworthy, and can we tell in advance which ones will break?</h3><p>An evaluator that looks accurate can fall apart once a model is optimized to satisfy it (reward hacking); the open question is which signals survive that pressure.</p>'+
 '<h3 class="ac">For open-ended work with no clear right answer, can anything cheap judge quality, or do we always need a human?</h3><p>Essays, research, and long agent tasks have no gold answer to compare against, so it is unknown whether any low-cost signal tracks quality at all.</p></div></div>'+
 '<div class="take">The program reorders these: yardstick (bet 2), survives smarter models (bet 1), survives hacking (bet 4), design (bet 3), the floor (bet 5).</div>')

# 18-23 appendix: prior work per question (verified in the literature pass)
refslide("Appendix &middot; prior work &middot; Q1","Oversight reliability vs the capability gap","PARTIAL",
 [("Scaling Laws for Scalable Oversight","arXiv:2504.18530","Engels et al. 2025. Plots oversight success against the overseer-overseen capability gap across several games."),
  ("A Benchmark for Scalable Oversight Protocols","arXiv:2504.03731","Sudhir, Kaunismaa, Panickssery 2025. Agent Score Difference: a scalar honesty-at-parity score, not a curve."),
  ("Scalable oversight with weak LLMs judging strong LLMs","arXiv:2407.04622","Kenton et al. 2024. Judge accuracy vs the debater-judge gap, inference-only."),
  ("Weak-to-strong generalization","arXiv:2312.09390","Burns et al. 2023. Training recovery vs compute, not a reliability curve.")],
 "Engels already draws the capability-gap curve, on game Elo. Unclaimed: the <b>optimization-pressure-over-time</b> axis and grounding capability in real math, code, and agentic domains.")

refslide("Appendix &middot; prior work &middot; Q2","Do cheap evaluators score surface, not quality","PARTIAL",
 [("JudgeBench","arXiv:2410.12784","Tan et al. 2024. Frontier judges near chance at picking the objectively correct answer over the stylish one."),
  ("Style Over Substance","arXiv:2307.03025","Wu and Aji 2023 (also Feuer et al. 2024, 2409.15268). Fluent-but-wrong beats plain-but-right."),
  ("Length-Controlled AlpacaEval","arXiv:2404.04475","Dubois et al. 2024. Partials out length as a mediator, one nuisance only."),
  ("ODIN: Disentangled Reward Mitigates Hacking","arXiv:2402.07319","Chen et al. 2024. Splits a reward into length vs content heads.")],
 "Each shows or removes <i>one</i> bias; none reports the <b>surface-nuisance fraction</b> of score variance as the headline. Our decomposition does.")

refslide("Appendix &middot; prior work &middot; Q3","Is judging quality easier than generating","mostly UNCLAIMED",
 [("Weaver: Shrinking the Generation-Verification Gap","arXiv:2506.18203","Saad-Falcon, Song et al. 2025. Weak-verifier ensembles, correctness selection only."),
  ("Generator-Validator Consistency","arXiv:2310.01846","Li et al. 2023. GV-consistency, still correctness / true-false."),
  ("LLMs Cannot Self-Correct Reasoning Yet","arXiv:2310.01798","Huang et al. 2023. Self-verification fails without external feedback."),
  ("Can LLMs Judge Better Than They Generate?","arXiv:2606.28050","Bandyopadhyay 2026. Generation beats self-evaluation on 3 of 4 QA benchmarks.")],
 "All correctness-only. Unclaimed: whether judging <b>quality among already-correct</b> answers is easier than producing a good one.")

refslide("Appendix &middot; prior work &middot; Q4","Can we predict which evaluators get gamed","PARTIAL / UNCLAIMED",
 [("Scaling Laws for Reward Model Overoptimization","arXiv:2210.10760","Gao et al. 2023. Overoptimization magnitude from KL and RM size, during optimization."),
  ("Defining and Characterizing Reward Hacking","arXiv:2209.13085","Skalse et al. 2022. Unhackability is near-impossible, a theoretical property."),
  ("More Convincing, Not More Correct","arXiv:2607.05904","2026. Self-play drives reference-free judges to convincing-but-wrong outputs."),
  ("Inside the Unfair Judge","arXiv:2607.11871","Xu et al. 2026. A judge activation bias-subspace predicts its OOD failure.")],
 "None forecasts hackability <b>ex ante</b> from a static surface-nuisance property. That predictive framing is unclaimed.")

refslide("Appendix &middot; prior work &middot; Q5","Any cheap signal with no reference","PARTIAL",
 [("BARTScore","arXiv:2106.11520","Yuan, Neubig, Liu 2021. LM likelihood as a reference-free NLG score, for constrained generation."),
  ("Discovering Latent Knowledge Without Supervision (CCS)","arXiv:2212.03827","Burns et al. 2022. Unsupervised truth direction from consistency, short factual statements."),
  ("Self-Consistency","arXiv:2203.11171","Wang et al. 2022. Answer agreement as a label-free correctness proxy, where answers converge."),
  ("Reference-free NLG evaluation survey","arXiv:2501.12011","2025. Landscape and limits of reference-free metrics.")],
 "The building blocks exist, but none asks whether <b>any</b> cheap reference-free signal survives into open-ended, answer-free work, or whether human judgment is the floor.")

refslide("Appendix &middot; prior work &middot; the spine","Does the nuisance fraction predict failure","UNCLAIMED",
 [("Inside the Unfair Judge","arXiv:2607.11871","Xu et al. 2026. A measured judge property predicts OOD failure, but geometric, not a nuisance fraction, and silent on hacking."),
  ("A Long Way to Go: Length Correlations in RLHF","arXiv:2310.03716","Singhal et al. 2023. One nuisance feature, length, drives most of the hacking."),
  ("Reward Model Ensembles Help Mitigate Overoptimization","arXiv:2310.02743","Coste et al. 2023. Uncertainty mitigates, it does not predict."),
  ("Helping or Herding?","arXiv:2312.09244","Eisenstein et al. 2023. Shared systematic reward-model error survives ensembling and still gets hacked.")],
 "Each leg is foreshadowed, but no one defines a single <b>surface-nuisance fraction</b> that jointly predicts <b>both</b> OOD collapse and hackability. That unifying predictive quantity is the open gap, and the moat.")

# 21 appendix: judge robustness
slide("Appendix &middot; robustness to the judge","Not one judge's opinion",
 chips(("0.75-0.94","inter-judge agreement (ρ)"),("2 families","gpt-5.2 &amp; Opus 4.8"))+
 "<p>The model-ranking story above is judge-free (TFA vs <b>accuracy</b>). The <i>item-level</i> results in Part 2 are the only judge-defined ones, so we re-graded the three anchor datasets with a second frontier judge from a different family (Claude Opus 4.8), same rubric. Same pattern: the MATH null stays null and the small GSM8K and Putnam signals replicate, with CIs still excluding zero.</p>"+
 fig("judge","Item-level partial ρ under two judges (gpt-5.2 vs Claude Opus 4.8): the same conclusions under both.")+
 "<div class='take'>The conclusions are properties of TFA, not of the particular judge we appointed as ground truth.</div>")

# 22 appendix: nuisance decomposition (backup for the "why, with proof" slide)
slide("Appendix &middot; backup &middot; the nuisance decomposition","How the 89-96% is actually measured",
 chips(("94.6%","MATH-500"),("88.9%","MATH-full"),("89.1%","GSM8K"),("96.1%","Putnam"))+
 '<div class="cols"><div>'+
 '<h3 class="g">The recipe (a one-way ANOVA on the reference)</h3>'+
 '<ol><li><b>Build the grid.</b> T[model, item] = per-item TFA for the 5-model Qwen ladder, aligned on the problems all five share.</li>'+
 '<li><b>Remove each model level.</b> Subtract every model own mean over items: D = T minus its row mean. This strips out overall generosity (the model-ranking axis), leaving only how TFA rises and falls from item to item within a model.</li>'+
 '<li><b>Find the shared part.</b> Average each item column down the models: b[item] = mean over models of D. That is the item main effect, the deviation <b>identical for every model</b>, a fact about the reference, not about any model.</li>'+
 '<li><b>Take the ratio.</b> nuisance = SS(b) / SS(D) = &Sigma; b&sup2; over &Sigma; D&sup2;: the item factor share of the within-model variance. It lands at <b>89-96%</b> on every dataset; the leftover 4-11% is the model-specific residual.</li></ol>'+
 '<p style="font-size:.9rem;color:var(--mut)">Reproducible via <span style="font-family:ui-monospace,Menlo,monospace">scripts/variance_decomp.py</span>.</p>'+
 '</div><div>'+
 '<h3 class="p">A two-model, three-item toy</h3>'+
 '<table class="mini"><tr><th></th><th>item 1</th><th>item 2</th><th>item 3</th><th>row mean</th></tr>'+
 '<tr><td>Model A</td><td>0.70</td><td>0.80</td><td>0.90</td><td>0.80</td></tr>'+
 '<tr><td>Model B</td><td>0.74</td><td>0.84</td><td>0.94</td><td>0.84</td></tr></table>'+
 '<p style="font-size:.98rem">Center each row and both become [&minus;.10, 0, +.10]. The item effect is [&minus;.10, 0, +.10] and the residual is <b>zero everywhere</b>, so nuisance = 100%: item 3 is easier to reproduce for <i>both</i> models by the same amount, so nothing here tells the two apart. The uniform +0.04 on Model B is the overall level, removed in step 2, and that is the ranking axis.</p>'+
 '<div class="def" style="font-size:.95rem"><b>Why this splits the two verdicts.</b> Being identical across models, the nuisance <b>cancels</b> when you average over items (mean TFA still ranks models) but <b>swamps</b> the 4-11% model-specific residual inside any single item (so grading fails). The 89-96% is the ceiling on how much per-item signal ever existed.</div>'+
 '</div></div>'+
 '<div class="take">Grading needs that 4-11% residual, and the judge correlation shows even it is mostly noise, not competence.</div>')

# appendix: research agenda deep-dive (moved out of the main flow, kept so nothing is lost)
slide("Appendix &middot; agenda &middot; the gap","Scalable oversight is measured at the wrong point",
 '<p>Today an overseer is judged by its <b>accuracy at parity</b> and its <b>cost</b>. But what predicts whether a method <i>scales</i> is the <b>degradation curve</b>: how reliability changes as the solver grows more capable and as it is optimized against the overseer.</p>'+
 '<ul><li>The current protocol benchmark (Agent Score Difference) explicitly does <b>not</b> test long-horizon capability gaps or optimization pressure over time.</li>'+
 '<li>Judges are provably hackable: a lone &ldquo;:&rdquo; draws false positives from GPT-4o up to 35% of the time, and strong judges are near-random on JudgeBench objective-correctness pairs.</li>'+
 '<li>Reference-free reward signals get gamed under self-play.</li></ul>'+
 '<div class="take">The missing third axis: robustness under <b>capability gap &times; optimization pressure</b>.</div>')

slide("Appendix &middot; agenda &middot; the questions","The four questions, in detail",
 '<div class="cols"><div>'+
 '<h3 class="g">RQ1 &middot; flagship</h3><p><b>Oversight robustness curves.</b> Chart overseer reliability vs solver capability and vs optimization pressure, across math, code, agentic, and subjective domains, and <b>predict the slope</b> from our style/nuisance offset. Turns &ldquo;oversight breaks at large gaps&rdquo; into a predictor.</p>'+
 '<h3 class="p">RQ2</h3><p><b>Certify an evaluator without full ground truth.</b> A judge <b>nuisance fraction</b> (quality vs surface: verbosity, style, position), anchored on human grades; flags the hackable failures before deployment.</p></div>'+
 '<div><h3>RQ3</h3><p><b>Reference-free process signals for agents that survive optimization.</b> Our rollout process value, grounded in the environment oracle, hardened against reward hacking.</p>'+
 '<h3>RQ4</h3><p><b>Does verification beat generation for grading quality?</b> Our item-level null says: not for quality, only for correctness. The backbone under RQ1 and RQ2.</p></div></div>'+
 '<div class="take">Every cheap evaluator, TFA and LLM judges alike, mixes a quality signal with a surface nuisance.</div>')

slide("Appendix &middot; agenda &middot; the bet","The impactful-paper template: oversight robustness curves",
 '<p>The impactful-paper template, borrowed from generative modeling: introduce a genuine new <b>axis</b> to a problem treated as two-dimensional, then validate it across modalities with scaling curves. Our new axis is <b>oversight robustness</b>; our modalities are math, code, agentic, and subjective tasks.</p>'+
 '<p>What is uniquely ours: not just the benchmark, but a <b>mechanism that predicts the curve</b>. As the solver diverges in style and distribution from the overseer, the nuisance term grows and reliability bends, exactly the offset we measured for TFA.</p>'+
 '<div class="warn"><b>Respects the frontier constraint.</b> API models expose no token log-probabilities, so the practical toolkit is <b>certified judges (RQ2) + reference-free process signals (RQ3)</b>, with TFA the foundation that maps the limits.</div>'+
 '<div class="take">Proposal to Sanmi: RQ1 as the flagship, RQ2 as its certification engine, RQ3 as the agentic follow-on.</div>')

slide("Appendix &middot; agenda &middot; why now","The automated weak-to-strong researcher confirms the bottleneck",
 '<p>Nine Claude agents autonomously solved a weak-to-strong problem (Performance Gap Recovered <b>0.97</b> vs <b>0.23</b> for human researchers) in days. Their own conclusion: the bottleneck is no longer proposing or running ideas, it is <b>designing evals</b>. The failures were <b>reward hacking</b> (shortcut mining, test-label exfiltration) and generalization, <b>high out-of-distribution accuracy did not mean real generalization</b>.</p>'+
 '<div class="cols"><div><h3 class="g">What it changes for us</h3>'+
 '<ul><li><b>Robustness under optimization is the whole game</b>, not accuracy at parity &rarr; RQ1.</li>'+
 '<li>Their generalization bottleneck is our <b>surface-vs-competence</b> mechanism one level up &rarr; RQ2 certifies generalization.</li>'+
 '<li>Their winning methods are <b>self-elicited from the strong model</b> (unsupervised consistency) &rarr; the reference-free bridge, RQ3.</li></ul></div>'+
 '<div><h3 class="r">The caution</h3><p>An automated researcher will hack <i>our</i> eval too. A robustness benchmark has to be hacking-robust by construction. That is not a problem for the thesis, it is why the thesis matters.</p></div></div>'+
 '<div class="take">AI will do the research; the scarce skill becomes hacking-robust, generalization-faithful evaluation, which is our lane.</div>')

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
html=STYLE+'<div class="rail"></div><button class="toggle">◐ theme</button><div class="counter"></div><div class="deck">'+"".join(S)+'</div>'+SCRIPT
out="paper/slides.html"
open(out,"w").write(html); print("wrote",out,"slides:",len(S),"bytes:",len(html))
