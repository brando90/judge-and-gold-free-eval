# PREREG: experiment 03, model-level ranking by self-consistency (SC) vs gold accuracy

Dated 2026-11-25 (Wed), written and committed BEFORE any model is sampled for this experiment and before any
outcome number of it is computed. Follows experiment 02 (RESULTS.md there, next steps 1 and the open review items).

## Question (Brando's goal, 2026-11-24)
A metric that replaces gold-reference metrics (boxed accuracy, pass@k), with no gold answer, no human and no LLM
judge. Experiment 02 tested item-level SC on one model (Llama-3.1-8B). Here: **does model-level SC rank models the
way gold accuracy does?** Two open review items from 02 are audited too: (A1) the argmax-picks-an-unboxed-sample case,
(A2) canonical answer keys vs pairwise Math-Verify.

## Models and data (6 models, the same 500 MATH-500 problems, n = 16 samples each)
| id | model | source |
|---|---|---|
| llama31_8b | meta-llama/Llama-3.1-8B-Instruct | committed exp-02 data (64 samples; first 16 used for the primary result, all 64 as a supplement) |
| qwen25_7b | Qwen/Qwen2.5-7B-Instruct | new, vLLM on skampere1 A100s |
| qwen3_4b | Qwen/Qwen3-4B (non-thinking mode) | new |
| qwen3_1p7b | Qwen/Qwen3-1.7B (non-thinking mode) | new |
| dsmath_7b_rl | deepseek-ai/deepseek-math-7b-rl | new |
| mistral_7b | mistralai/Mistral-7B-Instruct-v0.2 | new |
Sampling for all (new = `scripts/generate.py`, same as `tfa-vs-judge/scripts/bon_generate.py`): the prompt "Solve the
following math problem. Show your reasoning step by step, then give the final answer in \boxed{}.", temperature 1.0,
top_p 0.95, max_tokens 1024, seed 0. Samples keep the original order. A model is dropped only if its generation fails
to run (then the table says so; no model is dropped for its results).
Route note: the plan router runs agent CLI jobs, not bulk sampling, so generation runs on the lab's own GPUs
(skampere1), which spend no plan tokens and cost nothing extra. The plan router is used for the independent review.

## Definitions (frozen)
- `ans(s)` = last `\boxed{...}` of sample s (`tfa/boxed.py`); no box = no answer (unboxed).
- Answer key: experiment 02's canonical key with the D3 normalisation (strip `$`, dfrac to frac, `\left`/`\right`,
  `\!`, `\,`, trailing punctuation, then Math-Verify `parse`; fallback whitespace-normalised string). Primary matcher =
  this normalised key. Sensitivity: the raw (un-normalised) key.
- Gold correctness: Math-Verify `verify(parse(gold), parse(ans))`; unboxed = wrong. For Llama also compared with the
  committed `oracle` bit (agreement reported).
- Item SC(s) = fraction of the other n-1 samples with the same key; unboxed = 0. Problem SC = mean item SC (this equals the
  pairwise agreement rate). SCP(p) = largest answer-cluster share among the n samples.
- **Model SC (primary candidate)** = mean over the 500 problems of problem SC. Secondary candidates: mean SCP;
  SC_boxed = problem SC computed among boxed samples only (denominator boxed-1), mean over problems with at least 2 boxed samples.
- Targets (gold-needing): pass@1 = mean correctness over all samples and problems (primary target); maj@16 = accuracy of
  the plurality answer (ties: first-occurring cluster); pass@16.
- Control (trivial, gold-free): boxed rate = share of samples with a box.

## Primary endpoint E1: does model SC rank the 6 models like pass@1?
Kendall tau and the number D of discordant model pairs (of 15) between model SC and pass@1; Spearman as secondary.
Problem-cluster bootstrap (2000 resamples of the 500 problems, same resample for all models) gives the distribution of
D and a 95% CI of tau. Per pair: probability the order matches in the bootstrap.
**Decision rule (frozen):**
- YES: D <= 2 (tau >= 0.733) AND every discordant pair has a pass@1 gap < 0.05 AND bootstrap P(D <= 3) >= 0.80.
- NO: D >= 4, OR any discordant pair has a pass@1 gap >= 0.10.
- INCONCLUSIVE: otherwise (including a bootstrap P(D <= 3) < 0.80 with D <= 2).
Reported next to it: the same table for mean SCP, SC_boxed, maj@16, pass@16, and the boxed-rate control. If boxed rate alone
ranks as well as SC (D_boxed <= D_SC), the takeaway says SC adds nothing over format compliance.

## Secondary endpoints
- E2 level: Pearson of model SC with pass@1; per model the gap (SC - pass@1) and (mean SCP - pass@1). No pass line; shows
  whether SC reads as accuracy or only orders.
- E3 confident wrongness per model: precision of the plurality answer at SCP >= 0.5 and its coverage (experiment 02's P5, now
  per model). Pass line (as in 02): precision >= 0.90 for every model.
- E4 metric stability: 200 random splits of the 16 samples into 8 + 8; Kendall tau between the model orders by SC from the
  two halves (mean), and between SC on one half and pass@1 on the other half (mean).
- E5 per-level: Kendall tau of SC vs pass@1 within MATH levels 1-2 and 4-5 (descriptive).

## Audit A1: argmax picks an unboxed sample
Experiment 02 selects by argmax item SC, ties to the lowest sample index. If no answer repeats, every SC is 0 and sample 0 is
picked, boxed or not. Per model (and Llama with all 64): (a) share of problems with max item SC = 0; (b) share of problems
where the selected sample is unboxed; (c) selection accuracy under that rule vs a fixed rule (ties broken to the lowest-index
boxed sample; no boxed sample = wrong), with the paired bootstrap CI of the difference; (d) the effect on the model ranking
by selection accuracy. Pass line "case is negligible": (b) <= 1% of problems for every model and |difference in (c)| <= 0.005.

## Audit A2: canonical keys vs pairwise Math-Verify
For 60 problems per model (seed 20261125, drawn from problems where the model has at least 2 distinct boxed answers),
compare for every pair of distinct boxed answer strings (a) key equality vs (b) pairwise `verify` (either direction True =
equal; 10 s timeout per call; a timeout counts as not equal and is counted separately). Report the 2x2 counts, the pair
disagreement rate, the problem partitions by connected components of pairwise-equal pairs vs by key, the mean absolute
difference in SCP, and whether the model ranking by SC on these audited problems changes. Pass line "canonical keys are
fine": disagreement rate <= 1% of pairs, mean |dSCP| <= 0.01, ranking unchanged.

## Predictions (frozen, my guesses before any new sample exists)
- E1: D <= 2 about 60%; NO about 20%. The risk is Mistral and the small Qwen3 model, whose 1024-token cut-off leaves many
  samples unboxed (counted 0 by SC), and Llama vs Qwen3-1.7B, whose pass@1 may be close.
- E3: at least one model below 0.90 precision, about 85% (02 found Llama 0.88).
- Boxed-rate control ranks as well as SC (D_boxed <= D_SC): about 30%.
- A1: (b) below 1% for every model about 60%; larger for Mistral.
- A2: disagreement rate <= 1% about 70%.

## Deviations
Any change to this file after the commit is listed under "Deviations" in RESULTS.md with its reason; the frozen decision
rule above is not edited.
