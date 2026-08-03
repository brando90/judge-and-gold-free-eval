# Step 1 result: the yardstick certifies an evaluator without trusting it

**The step.** Reliable judges without ground truth needs a gate: with little
ground truth, how do you tell a good judge from a bad one? The proposed answer is
a nuisance fraction computed as a mechanism, not a trained metric. This is the
first run of it on real LLM judges, and it has been through a critic pass.

**Method.** For each dataset and judge we split the item-level score variance into
a quality part (explained by ground-truth correctness) and a surface part (length,
line count, LaTeX density, boxed-answer presence) that a good judge should ignore.
The sharp number is measured among already-correct answers, where correctness is
constant, so leftover spread is quality or surface. We run GPT-5.2, Opus 4.8, and
TFA on the Qwen ladder over MATH-500, GSM8K, Putnam. Correctness is the
authoritative `cc` field, joined by (model, problem_id); every record matched.
All surface numbers below are **5-fold cross-validated** and, where noted, taken
**beyond solver-model fixed effects**, so they are not in-sample or model-confound
artifacts.

Code: `scripts/judge_nuisance.py` (raw), `scripts/step1_verify.py` (critic pass +
subsampling, writes `runs/step1_verified.json`), `scripts/make_step1_fig.py`
(`paper/figs/fig_step1_yardstick.png`, `fig_step1_subsample.png`).

## Verified results

| dataset | evaluator | quality signal | surface nuisance (within-correct, CV) |
|---|---|---:|---:|
| MATH-500 | judge GPT-5.2 | 85% | 1.3% |
| MATH-500 | judge Opus | 85% | 3.8% |
| MATH-500 | TFA | 0% | 9.8% |
| GSM8K | judge GPT-5.2 | 73% | ~0% |
| GSM8K | judge Opus | 74% | **9.7% (9.5% length; 10.1% beyond model FE)** |
| GSM8K | TFA | 1% | 1.1% |
| Putnam | judge GPT-5.2 | 36% | not reliable (small n) |
| Putnam | judge Opus | 29% | not reliable (small n) |

Reading:

- **The yardstick separates a real evaluator from a surface one.** LLM judges
  track correctness (29 to 85%); TFA does not (0 to 1%), and the variance TFA does
  have is surface. The certificate is the pair, quality high and surface low; a low
  surface number alone is not a pass (TFA on GSM8K has low surface only because it
  has almost no signal at all).

- **It flags a specific, verified judge failure.** Among correct GSM8K answers the
  Opus judge's score is 9.7% surface, almost all length (9.5%), and it survives
  cross-validation and solver-model controls (10.1%). GPT-5.2 there is length-free
  (~0%). That is an actionable, pre-deployment warning invisible to accuracy.

## Critic pass: what survived and what did not

- **Circularity (passed).** `cc` is judge-independent (joined by model and item,
  identical across both judges) and correlates 0.82 with a separate deterministic
  scorer, so the quality axis is not the judge grading itself. Caveat: on MATH `cc`
  correlates 0.92 with the judge score, so "quality signal" there is really
  correctness detection, not fine-grained quality grading.
- **Model confound (controlled).** The GSM8K Opus and MATH surface effects survive
  solver-model fixed effects, so they are judge behavior, not a "which model wrote
  it" artifact.
- **Overfitting (caught, and it bit Putnam).** The earlier Putnam within-correct
  surface numbers (4.9%, 7.7%) were in-sample overfitting: cross-validated they
  drop to about zero or negative, and to 0.0% beyond model fixed effects, on only
  ~120 correct answers. **Those numbers are retracted.** Putnam is under-powered
  for the within-correct analysis.
- **Ceiling caveat.** 70 to 96 percent of correct-answer judge scores sit at the
  maximum, so the within-correct analysis explains only the non-ceiling minority.

## Why the quality signal is low on GSM8K/Putnam, and can a prompt fix it?

`scripts/improved_prompt.py`. Two facts.

1. **The quality signal is an identity, not a coincidence.** With one binary
   regressor, R2 = correlation^2, so the quality signal *equals* corr(judge,
   accuracy)^2. MATH 85% <-> 0.92, GSM8K 73% <-> 0.86, Putnam 29-36% <-> 0.54-0.60.
   If a judge's agreement with accuracy is low, the quality signal is low by
   definition.
2. **A better quality prompt does not raise it, but a binary prompt shows why it
   was low.** On a stratified sample (balanced correct/incorrect), a solve-first
   quality rubric left it flat (GSM8K 62% -> 61%, Putnam 37% -> 36%). But asking a
   **binary** "is the final answer correct?" question jumped Putnam from corr 0.62
   (38%) to **0.91 (84%)** and GSM8K from 0.78 (61%) to 0.82 (67%).

So the low Putnam signal is a **graded-vs-binary mismatch**, not judge incapacity:
the judge detects correctness very well (0.91), but the 0-10 quality rubric spreads
scores on purpose (a rigorous-but-wrong solution gets a mid score), which
under-correlates with strict binary `cc`. Implication for the certificate: the
quality axis should separate correctness detection (ask a binary question) from
graded quality, or it penalizes a judge for grading a spectrum. GSM8K stays limited
mostly by saturation.

## Coherence of the quality axis under perturbation, and the binary trap

`scripts/perturb_quality.py` (`runs/perturb_quality_{gsm8k,putnam}_gpt.jsonl`),
GPT-5.2 on balanced samples (equal correct/incorrect so accuracy has variance).

| condition | corr(acc) | quality signal | dScore vs orig |
|---|---:|---:|---:|
| GSM8K orig | 0.783 | 61.3% | - |
| GSM8K verbose | 0.788 | 62.0% | -0.07 |
| GSM8K reformat | 0.782 | 61.1% | +0.02 |
| GSM8K binary | 0.816 | 66.7% | -0.42 |
| Putnam orig | 0.614 | 37.7% | - |
| Putnam verbose | 0.594 | 35.2% | -0.14 |
| Putnam reformat | 0.598 | 35.8% | -0.07 |
| Putnam binary | 0.932 | 86.9% | +2.54 |

- **Identity holds empirically:** quality signal = corr(acc)^2 in every row.
- **The quality axis is robust to surface.** Under verbose/reformat, scores barely
  move (dScore ~ +/-0.1) and the quality signal barely moves (GSM8K 61 -> 62/61;
  Putnam 38 -> 35/36). It moves only when scores move.
- **The binary trap.** A binary "is it correct?" rubric spikes the quality signal
  (Putnam 38% -> 87%) but shifts the mean score by +2.54: it answers an easier,
  different question (correctness), which we already have for free from `cc`. So
  maximizing the quality signal is not the goal; a judge that maxes it is redundant
  with the cheap correctness check. The judge's value is graded quality BEYOND
  correctness, exactly the residual our item-level study found hard. The Step-1
  metric should therefore separate correctness detection from graded-quality
  discrimination, not reward a judge for collapsing to binary.

## Causal test (padding): the length "bias" does not reproduce — important correction

`scripts/causal_padding.py` (`runs/causal_padding_gsm8k_opus_pilot.jsonl`). We
intervened on length while holding the correct answer fixed: PAD = the same answer
with a redundant correct restatement appended (more length, no new reasoning),
re-judged fresh against a fresh re-judge of the unpadded text (orig2), on 40
correct, non-ceiling GSM8K answers with Opus.

- **Padding effect (pad - orig2): +0.04, 95% ~[-0.37, +0.45], 25% positive.**
  Essentially zero. Adding redundant length does not raise Opus's score.
- Controls are clean: re-judging the same text is stable (orig2 - old = -0.16), and
  the terse arm collapses (compress - orig2 = -8.36) because the rubric penalizes
  *showing no reasoning*, not length as such.

**Interpretation.** The observational GSM8K Opus surface effect (10.8%, hardened
with CV, feature-robustness, and CIs) is **not a manipulable length bias**. Among
correct answers, length is confounded with genuine reasoning thoroughness: terse
correct answers often have real gaps the rubric legitimately penalizes, while
verbose ones show complete work. Adding length without adding reasoning moves
nothing. So the surface-regression yardstick **overstated bias by confounding
length with quality**, and the earlier "actionable flag" is withdrawn pending a
counterfactual measure.

**Full battery (both judges, three perturbations, n=150; `scripts/causal_battery.py`,
`runs/causal_battery_gsm8k.jsonl`).** Extending the pilot, we ran verbose
(connective filler), reformat (markdown headers), and dup (duplication) against a
fresh orig2, on both GPT-5.2 and Opus. Every effect is <= 0: no judge raises a
correct answer's score for length or formatting. The cleanest manipulations are ~0
(GPT dup -0.02 [-0.05,+0.01], reformat -0.03 [-0.09,+0.02]; Opus dup -0.14
[-0.34,+0.05], reformat -0.14 [-0.41,+0.12]), and Opus mildly *penalizes* filler
verbosity (-0.44 [-0.66,-0.22]). So neither judge has a pro-surface bias, and the
GPT-5.2 control is flat too. The observational "Opus over-rewards length" is
refuted. Remaining caveat: GSM8K only, and a known-bias positive control (position
bias) is the next check that the method can detect a bias when one exists.

**What survives.** The certificate's quality axis is untouched: judges track
ground-truth accuracy 0.85 to 0.92 and TFA ~0 (see the accuracy check). What this
corrects is the surface-nuisance axis: a naive score-on-surface regression is not a
trustworthy bias measure on its own, because surface (length) proxies quality among
correct answers. The nuisance axis needs a causal / counterfactual definition.

## Positive control: the causal method detects a real bias (position)

`scripts/position_bias.py` (`runs/position_bias_gsm8k.jsonl`). To show the null
above is sensitivity, not a dead method, we ran the canonical pairwise position
bias: two near-equal correct answers to the same problem, judged as (A,B) and
(B,A). p(pick first) = 0.5 is unbiased.

- GPT-5.2: p(first) = 0.47, content-consistent 0.73 (near-unbiased).
- Opus 4.8: **p(first) = 0.62**, content-consistent 0.70 (real first-position bias,
  n=40).

So the method is sensitive (flags Opus position bias) and specific (nulls the fake
surface bias): a genuine bias moves it, length and formatting do not.

## Confidence checks (bootstrap CI, held-out gain, feature robustness)

`scripts/step1_confidence.py` (`runs/step1_confidence.json`) hardens the numbers
with no new data.

- **Quality signal, bootstrap 95% CI:** MATH 85% [83, 87], GSM8K 73% [70, 77],
  Putnam 29 to 36% [22, 44]. All sit far above TFA (0 to 1%) with non-overlapping
  intervals.
- **Surface beyond model, held-out gain** (repeated 70/30 splits, so out-of-sample
  and leakage-free): the GSM8K Opus length bias is 10.8% [7.2, 16.3] and positive
  in **100% of splits**. MATH is small but real (Opus 5.8% [3.2, 8.1], GPT 2.7%
  [0.5, 4.1]). GSM8K GPT is null (0.7% [-1.2, 1.5]). Putnam is noise (negative
  medians, intervals about [-33, +5]), confirming it is under-powered.
- **Feature-set robustness:** the GSM8K Opus effect is 10.9 / 10.5 / 10.9% under
  {length only, length+words, all five features}, so it is length and does not
  depend on our feature choices; GSM8K GPT stays about 0 throughout.

High confidence: judges track correctness far better than TFA. The GSM8K Opus
surface effect is robust *observationally* but did NOT reproduce under the causal
padding test below, so it is not claimed as a bias. Under-powered: Putnam.

## Independent validation against ground-truth accuracy

`scripts/step1_accuracy_check.py` (`runs/step1_accuracy_check.json`). The surface
component is estimated without labels, so testing the de-surfaced (non-nuisance)
judge signal against accuracy is an independent check.

- **The judges' agreement with accuracy is genuine, not surface.** Removing the
  surface component barely changes it: MATH 0.92 -> 0.87, GSM8K 0.86 -> 0.85,
  Putnam ~unchanged (model-controlled partials move the same way). Surface alone
  correlates only 0.05 to 0.29 with accuracy.
- **Opus's GSM8K length bias is orthogonal to correctness:** removing surface does
  not lower its accuracy agreement (0.86 -> 0.85), so the length effect is pure
  bias among correct answers, not a truth-correlated shortcut.
- **TFA does not track accuracy at the item level** (MATH corr -0.01, GSM8K/Putnam
  ~0.11), surface-removed or not, failing the same test the judges pass.

## Low-ground-truth subsampling (`fig_step1_subsample.png`)

- **Quality signal is estimable from a small anchor.** With only ~100 correctness
  labels the estimate matches the full-data value (MATH 85.9 +/- 5.4 vs 85.5;
  GSM8K 72.8 +/- 8.4 vs 73.1). The unconditional surface dependence needs zero
  labels at all.
- **The within-correct surface axis is not cheaply estimable naively.** In-sample
  R2 is upward-biased at small n (MATH GPT full 1.8% but 7.3 +/- 5.2 at k=100), so
  the sharp certificate axis needs a bias-corrected estimator and more correct
  answers than a tiny anchor provides. This is a real limitation, not a pass.

## Bottom line

The gate half-works, with one clear correction. The **quality axis is solid and
independently validated**: judges track ground-truth accuracy 0.85 to 0.92, TFA
~0, and it transfers to low ground truth from ~100 labels. The **surface-nuisance
axis is not yet a trustworthy bias measure**: the one bias it flagged (Opus length
on GSM8K), though robust observationally, did not reproduce causally, because
length proxies reasoning thoroughness among correct answers. So the nuisance axis
needs a counterfactual definition, not a score-on-surface regression. Putnam is
under-powered throughout. This is Step 1 only; it does not yet test survival under
a widening capability gap (Step 2) or optimization (Step 3).

---

# Feasibility of the two axes (self-contained: read this if you have no prior context)

This section explains, from scratch, what the Step-1 "yardstick" is trying to do,
and how feasible each half actually is. It assumes no knowledge of the rest of the
document.

## The goal, in one paragraph

We want to certify an LLM "judge" (a model that scores other models' answers) as
trustworthy, in domains where we have little or no labeled ground truth. A judge is
trustworthy to the extent that its score (a) tracks real answer quality and (b) is
not driven by superficial properties of the answer it should ignore. So the
certificate has two axes: a QUALITY axis (does the score track truth?) and a
NUISANCE axis (does the score chase surface?). Below we break down how to measure
each cheaply, what it costs in labels, and where it breaks.

## Axis 1: quality (does the judge track truth?)

**What it is.** The quality signal is how much of the judge's per-item score is
explained by whether the answer is actually correct. Formally it is the R^2 of the
judge score regressed on a correctness label; with a single binary label this
equals corr(judge score, correctness)^2. It is, in plain terms, "judge accuracy,"
expressed as variance explained.

**How many labels ("the anchor") does it need?**
- Empirically, ~100 labels reproduced the full-dataset value in our runs (MATH 85.9
  +/- 5.4% vs 85.5% full; GSM8K 72.8 +/- 8.4% vs 73.1%).
- Why so few, and does it depend on dataset size? The standard error of a
  correlation is about (1 - r^2)/sqrt(n), where n is the number of LABELED items,
  not the size of the full pool. So the anchor size needed is essentially
  INDEPENDENT of how big the full dataset is (the finite-population correction is
  negligible unless the anchor is a large fraction of the whole). Roughly 100 to
  300 labels give a stable estimate.
- What it does depend on: (1) the true correlation, a judge that tracks truth well
  (r ~ 0.85) is easy to pin down, a weak one (r ~ 0.55) needs more labels for the
  same precision; and (2) CLASS BALANCE, if 96% of answers are correct (a saturated
  benchmark), you need many more labels to collect enough of the rare incorrect
  class. Class balance, not scale, is the binding constraint.

**How do you get labels in the domains the program targets, and what is a label?**
The cost of a label depends entirely on whether an oracle exists:
- Hard reasoning (math, code): the label is AUTOMATIC and cheap, answer-checking for
  math, unit tests for code. No humans needed. The label is the correctness of the
  END solution, not of the reasoning trace.
- Agents: the label is the ENVIRONMENT's own success signal, SWE-bench tests pass,
  a web task is completed, and so on. Also automatic, and again about the end state,
  not the trajectory.
- Open-ended work (essays, research, open agentic goals): NO cheap label exists, and
  even DEFINING the label is hard because quality is multi-dimensional with no single
  truth. Here you must fall back on a small set of human ratings, and this axis
  becomes weak and partly ill-defined. This is the same "floor" issue that Step 5 of
  the program is about.

**A distinction the one-line pitch hides (important).** There are really two
quality targets with very different label costs:
1. Correctness-tracking: does the judge agree with a cheap end-answer oracle? Cheap
   wherever an oracle exists. But a judge that maximizes ONLY this is redundant with
   the oracle we already have (see "the binary trap" earlier in this document, a
   binary correctness rubric spikes this signal while adding nothing beyond the free
   correctness check).
2. Quality-beyond-correctness: does the judge grade the reasoning/trace among answers
   that are all correct (or all incorrect)? This needs TRACE-LEVEL quality labels,
   which are expensive and, in open domains, ill-defined. This is the judge's real
   value and the genuinely hard thing to certify.
The phrase "real quality" in the pitch is ambiguous between these two and should be
disambiguated.

**Does it map onto existing LLM-judge benchmarks?** Yes, which both validates and
bounds the idea. Judge meta-benchmarks (for example JudgeBench, RewardBench) ARE
labeled anchors, "does the judge agree with ground truth" is exactly what they
measure. So in a labeled benchmark the quality axis is just judge accuracy and works
trivially. The NOVEL and untested claim is recovering that number from a SMALL anchor
in an UNLABELED domain. A clean external check is to take such a benchmark,
subsample to ~100 to 300 labels, and show the small-anchor estimate matches the full
benchmark. (A dedicated benchmark-landscape subsection is added below.)

## Axis 2: nuisance (does the judge chase surface?)

**What it is.** The share of the judge's score driven by quality-irrelevant surface
properties of the answer, length, formatting, position, style, and so on.

**Two ways to measure it, and why one is untrustworthy.**
- Observational (a regression): regress the judge score on surface features and read
  off how much variance they explain. This is cheap and needs no labels for the raw
  version, but it OVERSTATES bias, because surface correlates with quality (for
  example, among correct answers, longer solutions often show more complete
  reasoning). In this study the regression flagged a 10.8% length "bias" for one
  judge that a causal test then refuted.
- Causal (a perturbation, the trustworthy one): apply a CONTENT-PRESERVING change to
  the answer (make it more verbose, reformat it, reorder a pairwise comparison), then
  re-judge and measure how much the score moves. The score change IS the bias, by
  construction it cannot be confounded with quality, and it needs NO labels. This is
  what should define nuisance.

**Which nuisance types do you consider? (the real weakness.)** Length and formatting
are two of many, and you cannot enumerate every possible confound in advance. What
you can do:
1. Start from the known taxonomy in the judge-bias literature: length/verbosity,
   formatting/markdown, position (pairwise order), self-preference (a judge favoring
   its own family's style), sycophancy (agreeing with a stated answer or stated
   confidence), politeness/tone, authority or citation cues, answer-first vs
   reasoning-first. This gives a BATTERY of perturbations, not a single number.
2. Adversarial / generative discovery: let a model SEARCH for a content-preserving
   perturbation that changes the judge's score. Anything that moves the score is a
   nuisance you did not hand-specify. This turns "which types?" from guesswork into a
   search, and the worst score change found is an adversarial nuisance bound that
   tightens the harder you search.
3. Decorrelation test: move to a distribution where surface and quality are
   deliberately DEcorreLATED and measure how much the judge's agreement with truth
   drops; if it relied on surface, it falls there. This catches aggregate
   surface-reliance without naming every feature.

**Can you get the "full" nuisance fraction? No, and this is a genuine limit.** You
cannot certify the ABSENCE of nuisance, only detect its presence. What is actually
obtainable is (a) a battery of causal sensitivities per known bias type
(interpretable), and (b) an adversarial LOWER BOUND (the worst content-preserving
perturbation found so far). You never get a certified upper bound. This is
acceptable for the program's purpose, because a lower bound on gameability is exactly
what a pre-deployment check wants: if you already found a perturbation that moves the
judge, that is a fielded exploit regardless of what else exists. But it means the
"nuisance fraction" is not one scalar; it is a battery plus an adversarial bound, and
the pitch wording ("the nuisance fraction ... cannot be gamed") should become "a
mechanism-based LOWER BOUND on nuisance that flags exploits before deployment."

## Net

- Quality axis: cheap and solid where an oracle exists (math, code, agents), from
  ~100 to 300 labels, independent of dataset size, limited mainly by class balance;
  weak and ill-defined in open-ended domains; and it must be split into cheap
  correctness-tracking versus expensive quality-beyond-correctness.
- Nuisance axis: not a single "full fraction," a causal battery plus an adversarial
  lower bound; you certify the presence of gameability, never its absence.
- Two external checks worth running before this is presentation-ready: (1) small-anchor
  recovery on a public judge benchmark (validate the label-count claim off our own
  data), and (2) one round of adversarial nuisance discovery (does a search find a
  perturbation the hand-picked battery missed?).
