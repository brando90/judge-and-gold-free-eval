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
