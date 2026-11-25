# PREREG: experiment 04, format-robust SC and more models

Dated 2026-11-25 (Wed), written and committed BEFORE any model of this experiment is sampled and before any
fallback-extraction number (SC_fr, pass@1_fr, tier shares) is computed on any data. Follows experiment 03 (commit e26af2f).

## Questions
- A: With the fallback extractor (below), do SC_fr and the ranking of the 6 experiment-03 models match gold pass@1? In particular does
  DeepSeek-Math-7B-RL vs Mistral-7B-Instruct-v0.2 (pass@1 0.145 vs 0.102, SC 0.048 vs 0.062 in exp 03) become concordant?
- B: Does the ranking claim survive when more models whose pass@1 sits inside the existing gaps are added?

## Frozen definitions
- Fallback extractor `scripts/fr_extract.py` (tiers: boxed, phrase, math, number, none), frozen as committed with this file. Samples whose
  generation was cut at max_tokens (finish_reason "length") are NOT excluded in the primary analysis; sensitivity S1 below.
- Everything else as in experiment 03 PREREG: answer key (normalised canonical key, Math-Verify), item SC = fraction of the other n-1
  samples with the same key, model SC = mean over the 500 MATH-500 problems, n = 16 samples (Llama-3.1-8B: first 16 of the committed 64),
  prompt, temperature 1.0, top_p 0.95, max_tokens 1024, seed 0 (Qwen3-family in non-thinking mode), same gold matcher
  (Math-Verify, `verify(parse(gold), parse(answer))`).
- "Unextractable" (tier none) counts as no answer: SC 0 and wrong, as before.
- Candidates: SC_fr (SC under fr_answer). Targets: pass@1_strict (boxed only; exp 03's target) and pass@1_fr (gold match applied to
  fr_answer; the like-for-like target for SC_fr). Also reported: SC_strict (exp 03), boxed rate, tier shares per model.
- Primary comparison: **SC_fr vs pass@1_fr** (same extraction on both sides). Secondary: SC_fr vs pass@1_strict, SC_strict vs pass@1_fr.

## Part A endpoint (6 models, no new sampling)
Same rule as experiment 03, on D = discordant pairs of 15 between SC_fr and pass@1_fr, with the problem-cluster bootstrap (2000
resamples of the 500 problems, same resample for all models):
- YES: D <= 2 AND every discordant pair has a pass@1_fr gap < 0.05 AND bootstrap P(D <= 3) >= 0.80.
- NO: D >= 4 OR any discordant pair has a gap >= 0.10.
- INCONCLUSIVE otherwise.
Flip question (reported for both targets): DeepSeek-Math vs Mistral is concordant when sign(SC_fr diff) = sign(pass@1 diff);
it also needs SC_fr gap reported with a bootstrap P(order matches).

## Part B endpoint (6 + new models, same rule extended)
New models (all sampled by `scripts/generate.py`, n = 16, on skampere1): Qwen3-8B (non-thinking), Qwen3.5-4B (non-thinking),
Meta-Llama-3-8B-Instruct, DeepSeek-Math-7B-Instruct. Substitutions from the Acceptance's examples: Gemma-2-9B is on the host only as a
base model (no chat template) and Phi-3-mini has config.json only (no weights), so they are not run. Whether each new model's pass@1
lands inside a pre-existing gap (between two neighbouring old models at least 0.05 apart) is reported, not required; a model is not
dropped for its pass@1. A model is dropped only if generation fails to run (then RESULTS says so).
Rule on all M models (M(M-1)/2 pairs), SC_fr vs pass@1_fr:
- YES: Kendall tau >= 0.80 AND every discordant pair has a pass@1_fr gap < 0.05 AND bootstrap P(tau >= 0.733) >= 0.80.
- NO: tau < 0.60 OR any discordant pair has a gap >= 0.10.
- INCONCLUSIVE otherwise.
Also reported: the count of close pairs (pass@1_fr gap < 0.05) before and after adding models, and for those pairs the share concordant.

## Sensitivities (descriptive, no verdict)
- S1: fallback only for samples with finish_reason "stop" (truncated ones count unboxed). Llama-3.1 rows have no finish field and count as stop.
- S2: SC_fr and pass@1_fr by tier-1 + tier-2 only (no math/number guess).
- S3: SC_fr from raw (un-normalised) keys.
- S4: Part A verdict on the 6 models when SC uses n = 8 (first 8 samples).

## Predictions (frozen guesses)
- A: DeepSeek-Math vs Mistral becomes concordant about 70% (the fallback lifts DeepSeek-Math's SC); Part A verdict YES about 60%, NO about 15%.
- Risk: the fallback adds noise answers on truncated or unboxed samples; SC_fr for Mistral may rise too (it is confidently wrong).
- B: verdict YES about 40%, INCONCLUSIVE about 40%, NO about 20%.

## Deviations
Any change after this commit is listed under "Deviations" in RESULTS.md with its reason; the frozen rules above are not edited.
