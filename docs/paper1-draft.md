# What Does Comparing a Solution to a Reference Actually Measure?

*Draft v1. Authors: [Sri, Daneshvar, ...], Koyejo Group, Stanford. Status: all numbers final except
where marked [pending]; human-label items pending are listed in Limitations.*

## Abstract

Benchmarks with gold reference solutions invite a cheap evaluation recipe: score a model by how well
its output, or its next-token predictions, match the reference. We test what this recipe measures,
using seventeen models from seven families on eight math and code benchmarks, and anchoring everything
to human grades of reasoning quality rather than to another model's opinion. Three findings. First,
reference matching can rank models, but only when the reference is a long, complex piece of reasoning:
cutting the reference down to its final answer line collapses the ranking signal on the same problems
(Spearman +0.35 to +0.02), and reference entropy predicts where ranking works better than benchmark
saturation does. Second, no form of reference matching can grade an individual solution. Five metrics
spanning the space, from teacher-forced accuracy to gold-token probabilities to semantic embeddings,
all land within noise of zero against human soundness grades, and at exactly 0.00 against executed
test outcomes on 492 code solutions. The reason is a variance decomposition: 83 to 92 percent of
per-solution matching scores is a property of the reference itself, identical across model families.
Third, the two signals that do grade both avoid text matching: an LLM judge, which we validate against
blind human grades on separate soundness and style scales (it tracks soundness at rho 0.59-0.81 and
carries no detectable style loading), and a rollout method that finishes a truncated solution and
checks where it lands (rho 0.49 with human grades, at roughly one hundred times the cost). The
practical rule for benchmark builders: a reference's value is as an input to a judge or through its
answer as a checkable endpoint, never as a similarity target.

## 1. The question

Most benchmarks that matter, from grade-school math to competition problems to code, ship with a gold
reference: a worked solution or a canonical program known to be correct. Evaluating against that
reference without a judge is appealing for the obvious reasons. It is deterministic, it costs one
forward pass, it cannot be sweet-talked, and anyone can audit it. The sharpest version of the idea is
teacher-forced accuracy (TFA): feed the model the problem and the gold solution one token at a time,
and score the fraction of gold tokens the model itself would have predicted next. Prior work has used
TFA to rank models and has assumed, without testing it, that the same score can grade individual
solutions.

This paper asks what reference matching measures, and answers with three experiments that were forced
on us by our own reviewers: a decomposition of what the score's variance consists of, a validity study
anchored to human grades rather than to judge agreement, and an intervention on the reference itself.

Our starting point for skepticism was a review comment worth quoting because it names the trap
precisely: "everything item-level is defined as agreement with a judge... in measurement lingo, that's
reliability, not validity." If the judge scores surface style, then a metric failing to track the judge
proves nothing, and a metric tracking it may be succeeding at the wrong thing. So the ground truth in
this paper is human grades, collected blind, on two deliberately separated scales: whether the
reasoning is sound, and separately, how well it is written.

## 2. Setup, in one page

**Models and data.** Seventeen instruction-tuned models from seven families (Qwen, Phi, Mistral, OLMo,
plus math-specialized Qwen-Math, DeepSeek-Math, Mathstral), spanning 0.5B to 32B parameters. Eight
benchmarks: MATH-500, full MATH, Putnam-AXIOM and its variations, Omni-MATH, GSM8K and GSM8K-Platinum,
and HumanEval. Every model generates its own solution to every problem (greedy), and separately is
teacher-forced on the gold solution.

**Metrics under test.** Five ways of scoring a solution against the reference, chosen to span the
space: TFA (hard argmax match on gold tokens), gold-token log-probability (the soft version), TF-IDF
cosine (content-weighted lexical similarity of the model's own solution to the gold), unigram-F1 (raw
lexical overlap), and cosine similarity of sentence embeddings (semantic similarity). The first two
measure the model's predictive fit to the reference text; the last three measure the resemblance of
the model's own output to it.

**The two non-matching baselines.** An LLM judge (a frontier model grading each solution 0-10), and a
rollout process value: truncate the solution at several points, let a fixed mid-sized model finish it,
and score the fraction of completions that reach the correct answer. Note what the rollout method
uses from the reference: only its final answer, as a checkable endpoint. It never sees the reference
text.

**Human grades.** Annotators graded solutions blind (no model names, no metric scores) on two 0-10
scales with written anchors: soundness (is every step valid; does the argument establish the answer;
ignore the writing) and style (is it clear and well-organized; ignore correctness). Two annotators
graded a shared block for agreement (soundness rho 0.79, which is the ceiling any automatic signal can
be credited with); one annotator graded a 60-item uniformly random sample of MATH-500 solutions for
the headline validity numbers. For code, no human is needed for correctness: we execute the official
tests.

**Statistics.** Every headline correlation is reported as Spearman with a bootstrap 95% interval, and
we checked Pearson and Kendall agree in sign throughout. Grading claims control for final-answer
correctness (a partial correlation), because checking the final answer is free and is not what anyone
needs a grader for.

## 3. Result one: matching the reference ranks models, and we know why

Averaged over a benchmark, mean TFA orders models by accuracy remarkably well on hard data and not at
all on easy data. Within model families the picture is sharp: on the three hard math benchmarks, all
twelve family ladders (four families, three datasets) rank correctly; on the three saturated
benchmarks, five of twelve invert. Pooled across all seventeen models the same boundary appears, from
rho +0.86 on Omni-MATH down through +0.60 on Putnam to a point estimate of -0.25 on GSM8K whose
interval spans zero.

The natural reading, and the one we ourselves held for months, is that this is about saturation: when
every strong model scores above 95 percent, there is no skill variance left to detect. That reading is
incomplete. Two measurements separate the explanations. Across the eight benchmarks, the boundary
correlation tracks the entropy of the reference solutions (+0.89) more tightly than it tracks
top-model accuracy (-0.81), and the two are confounded in observational data because saturated
benchmarks happen to have short, formulaic references. So we intervened: on the same MATH-500
problems, with the same seventeen models, we replaced each worked reference with the single line "The
final answer is [answer]" and recomputed TFA. The ranking signal collapsed from +0.35 to +0.02.
Nothing else changed: same items, same models, same accuracy distribution, and the measurement noise
is negligible (about five thousand scored tokens per model).

The mechanism, then, is this: predicting a long, information-dense reference requires skill adjacent
to solving the problem, so predictive fit separates strong models from weak ones. Predicting a short
or formulaic reference requires nothing, so whatever differences remain between models are stylistic.
This explains the boundary, explains why family style inverts rankings exactly on saturated data, and
has a design consequence: if you want reference matching to rank models, the reference must be worth
predicting.

Two sub-findings sharpen the picture. Content-weighted similarity metrics (TF-IDF, embeddings) show
the same boundary as TFA, ranking on hard benchmarks (+0.72 and +0.87 on Putnam) and fading on easy
ones, so the boundary belongs to reference-anchored scoring generally, not to teacher forcing. Raw
lexical overlap does not rank at all, and its apparent inversion on hard data (-0.49) is a verbosity
confound: stronger models write longer solutions and overlap metrics punish length (controlling for
output length, -0.49 becomes -0.07).

## 4. Result two: no form of reference matching can grade a solution

Ranking models and grading individual solutions are different jobs, and the second is where the recipe
fails completely. The evidence comes in three layers.

**Against human grades.** On the random MATH-500 sample, the five matching metrics correlate with
human soundness at -0.07 (TFA), -0.17 (gold-token probability), +0.01 (TF-IDF), -0.24 (unigram-F1),
and +0.14 (embeddings). Every interval includes zero. For comparison, on the same solutions the judge
reaches +0.59 and the rollout value +0.49, both clearing zero comfortably.

**Against executed tests.** Code offers a referee no one can argue with. On 492 freshly generated
HumanEval solutions scored by running the official test suites, TFA's correlation with passing is
0.00, and stays within -0.04 to +0.06 inside each of the three models. The soft probability version
does no better.

**The reason.** Decompose per-solution TFA across a grid of fifteen to sixteen models from four
families, after removing each model's overall level. Between 83 and 92 percent of the remaining
variance is an item main effect: a component identical for every family, which can only be a property
of the reference (how predictable this particular gold text is). Another 3 to 7 percent is
family-specific style, and this style channel roughly doubles on saturated benchmarks, which is the
grading-side shadow of the ranking mechanism above. What is left for the individual solution is a few
percent. The same structure appears in code (78/8/14) and, attenuated, in the similarity metrics. A
score that is nine-tenths about the reference cannot grade the solution in front of it, and no
reweighting can fix that: we tried seven repairs (masking formatting tokens, IDF and surprisal
weighting, soft scoring, two contrastive variants, multi-reference max) and all landed at or below
zero.

We emphasize the breadth deliberately. A reader may accept that word overlap cannot grade and still
hope that semantic embeddings can. They cannot, at least not here: +0.14 against human soundness, with
the judge at +0.59 on the identical items.

## 5. Result three: what does grade, and what the reference is still for

**The judge, validated rather than assumed.** The two-scale human grading lets us test the standing
suspicion that LLM judges reward style. On items selected for disagreement between TFA and the judge,
where soundness and style pull apart (their correlation drops from +0.82 in random data to +0.31),
the judge's partial correlation with human soundness holding style fixed is +0.86, while its partial
with style holding soundness fixed is -0.06. Both annotators independently show this pattern. Among
correct-answer solutions only, where an endpoint-checking impostor would flatline, the judge still
tracks soundness at +0.81. On this task, this judge reads the work.

One honest caveat on measurement: our style scale is noisier than the soundness scale (inter-annotator
0.55 versus 0.79), so "no detectable style loading" is bounded by that precision, and we report it as
such rather than as a proof of zero.

**The rollout value.** Truncating a solution and letting a fixed completer finish it grades where
matching cannot (+0.49 against human soundness) and even separates correct-for-sound-reasons from
correct-by-luck. Its costs are real: roughly one hundred completions per solution, and a completer
strength that has to sit in a middle band (too weak cannot finish sound work; too strong rescues
broken work).

**The synthesis.** Notice what both working signals have in common, and what they lack. Neither treats
the reference text as a target. The judge reads the solution's content; the rollout method uses the
reference only through its final answer, as a checkable endpoint. Meanwhile our separate experiments
on judges show the reference is far from useless: handing a small judge a correct reference lifts its
error detection from 17 to 85 percent, nearly frontier level. Put together, the design rule is: use
the reference as context for a reader, or as an endpoint for a checker; never as a string to be
matched. Any metric that scores similarity to the reference text inherits the nuisance decomposition
of Section 4, and we predict new entrants in this class will fail the grading test before they are
built.

## 6. What this changes in practice

For benchmark maintainers: reference matching is a legitimate, auditable leaderboard signal exactly
when your references are long, information-dense worked solutions and your benchmark is not
saturated. If your references are answer lines, matching measures style. Reference entropy is
measurable in advance; we suggest reporting it alongside accuracy.

For anyone tempted to use matching scores as per-solution rewards or filters (process supervision,
data curation, RL): the per-solution signal is not weak, it is absent, across the entire metric
class, in two domains, against both human grades and executed tests.

For the judge-skeptical: validity is checkable for a few hundred dollars of annotator time. Two blind
scales, soundness and style, a shared block for the ceiling, partials for the verdict. Our judge
passed; that does not mean every judge on every task will, and the protocol matters more than our
particular result.

## 7. Limitations, stated plainly

The human anchor is currently sixty random items graded by one annotator who is also an author, plus
twenty divergence-selected items graded by two (both authors). Completion to the pre-registered
eighty, a second annotator on thirty random items, and an external non-author annotator are in
progress [pending]; the code-domain human grades (style and lucky-pass judgments that tests cannot
give) are collected but unlabeled [pending]. The validity results cover one judge on one math
benchmark plus executable code; a second dataset for the judge-validity claim is future work. The
divergence-block magnitudes are selection-conditioned and never quoted as population estimates. Model
scale tops out at 32B, and all boundary claims at the pooled level carry wide intervals at n=17
models, which is why the within-family counts carry the ranking evidence. Rollout value and the judge
have overlapping intervals against human grades; we claim only that both grade and matching does not,
not an ordering between them.

## 8. Relation to what the field is doing right now

Large-scale reliability audits of LLM judges (agreement, position bias, test-retest) have recently
concluded that reliability without validity is the field's open problem, and have called for exactly
the variance-component analysis we perform. Psychometric and IRT treatments of judges are emerging in
parallel. Our contribution to that conversation is a mechanism (the reference-nuisance decomposition),
an intervention (the short-reference collapse), a validated two-scale human protocol that can acquit a
judge rather than only indict one, and a class-level negative result with an executable-oracle
confirmation. The style-over-substance literature documents judge biases in general pools; our result
is complementary: on reference-equipped math with a strong judge, the style component is not
detectable, and the biggest measurement hazards were in the benchmarks' own answer keys and in
range-restricted saturated data rather than in the judge.

---

*Reproducibility: all scores, labels, decompositions, and scripts are in the repository
(experiments/tfa-vs-judge). Key entry points: runs/metric_class_results.md for the class table,
scripts/two_way_decomp.py, scripts/tfa_shortref.py for the intervention, scripts/run_code_tests.py
for the executable oracle, human_eval/ for the labeling instruments and returned labels.*
