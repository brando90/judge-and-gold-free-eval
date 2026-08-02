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

High confidence: judges track correctness far better than TFA, and Opus has a real
length bias on GSM8K. Under-powered: Putnam. Still observational (next: the causal
padding test).

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

The gate works: a mechanism-based, cross-validated, model-controlled nuisance
fraction cleanly ranks LLM judges above TFA and flags a concrete, real length bias
in one judge. The quality axis transfers to low ground truth from ~100 labels; the
within-correct surface axis needs more data or a bias-corrected estimator. Putnam
is under-powered. This is Step 1 only; it does not yet test survival under a
widening capability gap (Step 2) or optimization (Step 3).
