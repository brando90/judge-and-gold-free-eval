# RESULTS: experiment 04, format-robust SC and 4 more models (2026-11-25)

## Paper-ready

Format-robust SC needs no gold answer, no human label, and no judge. The primary target, format-robust pass@1, uses the same extractor and the gold answer.

**Part A (six models, no new sampling): YES.** $D = 0$ of 15, $\tau = 1.000$, $P(D \le 3) = 1.00$. DeepSeek-Math-7B-RL versus Mistral-7B-Instruct-v0.2 is concordant (format-robust SC $0.494$ vs $0.069$; format-robust pass@1 $0.506$ vs $0.105$).

**Part B (ten models): YES.** $D = 1$ of 45, $\tau = 0.956$, Spearman $\rho = 0.988$, $P(\tau \ge 0.733) = 1.00$. The discordant pair is Qwen3-4B versus Qwen3-8B, format-robust pass@1 gap $0.004$.

Sources: `results/results.json`, `results/tables.md`. The joint paper section is [`../../RESULTS.md`](../../RESULTS.md). The sections below are the lab record.

**Takeaway: YES (by the rule frozen in PREREG.md, commit 56947c5).** Self-consistency (SC) with a last-expression fallback, which needs no
gold answer, human label or judge, ranks 10 models on MATH-500 like gold pass@1 computed with the same fallback: 1 discordant pair of 45,
a gap of 0.004 in pass@1. DeepSeek-Math-7B-RL vs Mistral-7B becomes concordant. The old "wrong pair" in experiment 03 was mostly the
strict (boxed-only) pass@1 mis-scoring DeepSeek-Math-RL, not only SC.

Harness for every number: vLLM bf16 sampling on skampere1 A100s (experiment 03's harness: boxed-answer prompt, temperature 1.0, top_p 0.95,
max_tokens 1024, seed 0, n = 16 per problem, the same 500 MATH-500 problems), no agent harness; scoring by Math-Verify; analysis
`scripts/analyze.py`, CPU only. Models: Qwen2.5-7B-Instruct, Qwen3-8B, Qwen3-4B, Qwen3-1.7B, Qwen3.5-4B (all Qwen3 and 3.5 in non-thinking mode),
DeepSeek-Math-7B-RL, DeepSeek-Math-7B-Instruct, Llama-3.1-8B-Instruct (first 16 of the committed 64 samples), Llama-3-8B-Instruct, Mistral-7B-Instruct-v0.2.

## Five numbers
1. **Part A (6 old models, no new sampling):** SC_fr vs pass@1_fr: D = 0/15, Kendall tau 1.000, bootstrap P(D<=3) = 1.00. Verdict YES.
2. **DeepSeek-Math-7B-RL vs Mistral-7B flips to concordant:** SC_fr 0.494 vs 0.069 (was 0.048 vs 0.062), pass@1_fr 0.506 vs 0.105; bootstrap P(concordant) = 1.00.
   The cause: 66% of DeepSeek-Math-RL samples end "The answer is: $X$" with no box. The fallback lifts its pass@1 from 0.145 to 0.506 as well.
3. **Part B (10 models: the 6 plus 4 new):** D = 1/45, tau 0.956 (bootstrap 95% CI of tau [0.87, 1.00]; P(tau >= 0.733) = 1.00). Verdict YES. The one discordant pair is Qwen3-4B vs Qwen3-8B, pass@1_fr 0.710 vs 0.714 (gap 0.004), SC_fr 0.680 vs 0.678.
4. **Level:** Pearson of SC_fr with pass@1_fr over the 10 models is 0.995; SC_fr reads 0.012 to 0.089 below pass@1_fr (not a calibrated accuracy, but close here).
5. **Close pairs:** pass@1_fr gaps under 0.05: 1 pair among the 6 (Qwen2.5-7B vs Qwen3-4B, 0.014); 4 among the 10, of which 3 are concordant (Llama-3.1-8B vs DeepSeek-Math-7B-Instruct 0.016, Qwen2.5-7B vs Qwen3-4B 0.014, Qwen2.5-7B vs Qwen3-8B 0.010; Qwen3-4B vs Qwen3-8B 0.004 is discordant).

## Table (n = 16 x 500; sorted by pass@1_fr)
| model | pass@1 strict | pass@1 fr | SC strict | SC fr | boxed | phrase | math | number | cut at 1024 tokens |
|---|---|---|---|---|---|---|---|---|---|
| Qwen2.5-7B-Instruct | 0.721 | 0.724 | 0.680 | 0.686 | 0.91 | 0.00 | 0.09 | 0.00 | 0.09 |
| Qwen3-8B (non-thinking) | 0.705 | 0.714 | 0.661 | 0.678 | 0.76 | 0.01 | 0.23 | 0.00 | 0.25 |
| Qwen3-4B (non-thinking) | 0.702 | 0.710 | 0.662 | 0.680 | 0.77 | 0.01 | 0.23 | 0.00 | 0.24 |
| Qwen3-1.7B (non-thinking) | 0.633 | 0.640 | 0.580 | 0.595 | 0.75 | 0.01 | 0.25 | 0.00 | 0.26 |
| Qwen3.5-4B (non-thinking) | 0.537 | 0.571 | 0.482 | 0.520 | 0.55 | 0.00 | 0.45 | 0.00 | 0.45 |
| DeepSeek-Math-7B-RL | 0.145 | 0.506 | 0.048 | 0.494 | 0.26 | 0.66 | 0.07 | 0.00 | 0.08 |
| DeepSeek-Math-7B-Instruct | 0.412 | 0.413 | 0.345 | 0.346 | 0.96 | 0.00 | 0.03 | 0.00 | 0.03 |
| Llama-3.1-8B-Instruct | 0.377 | 0.397 | 0.281 | 0.308 | 0.72 | 0.01 | 0.21 | 0.06 | 0.00 |
| Llama-3-8B-Instruct | 0.237 | 0.239 | 0.160 | 0.164 | 0.96 | 0.01 | 0.03 | 0.01 | 0.03 |
| Mistral-7B-Instruct-v0.2 | 0.102 | 0.105 | 0.062 | 0.069 | 0.83 | 0.02 | 0.13 | 0.02 | 0.14 |

Full tables, all comparisons and the figure: `results/tables.md`, `results/results.json`, `results/model_rank.png` (grid on).

## Where the new models landed
Qwen3-8B (0.705) is not inside a gap; it sits between Qwen3-4B and Qwen2.5-7B (it is a tie with Qwen3-4B). Qwen3.5-4B (0.537), Llama-3-8B (0.237) and
DeepSeek-Math-7B-Instruct (0.412) land inside gaps of at least 0.05 of the old set (strict pass@1). So the new close pairs are few and mostly inside the Qwen family.

## All comparisons (Part A / Part B)
| comparison | A: D, verdict | B: D, verdict |
|---|---|---|
| SC_fr vs pass@1_fr (primary) | 0/15, YES | 1/45, YES |
| SC_fr vs pass@1 strict | 1/15, NO (max gap 0.232) | 4/45, NO (max gap 0.267) |
| SC strict vs pass@1 strict (experiment 03 definition) | 1/15, YES (gap 0.043) | 2/45, YES (gap 0.043) |
| S1 fallback only on non-truncated samples | 0/15, YES | 2/45, YES (tau 0.911) |
| S2 boxed + phrase tiers only | 0/15, YES | 2/45, YES (tau 0.911) |
| S3 raw (un-normalised) keys | 0/15, YES | not run |
| S4 SC from 8 samples | 1/15, YES | not run |

SC_fr vs strict pass@1 reads NO only because strict pass@1 puts DeepSeek-Math-RL (0.145) below Llama-3.1 and Llama-3-8B though it answers correctly about 51% of the time.

## What was not checked, caveats
- One benchmark (MATH-500, 500 problems), n = 16, 10 models, all sampled with a 1024-token cap and a boxed-answer prompt; no thinking-mode runs. No gap in pass@1 below 0.004 was tested beyond Qwen3-4B vs 8B.
- The fallback adds noise answers on truncated samples. Qwen3.5-4B has 45% of its samples cut at 1024 tokens (it writes long non-thinking answers), so its SC_fr and pass@1_fr contain mid-reasoning guesses. S1 and S2 (no guesses) leave the verdict YES but add one discordant pair (DeepSeek-Math-RL vs Qwen3.5-4B, gap 0.032).
- The verdict thresholds were fixed before sampling; the number of models rose from 6 to 10 (the Acceptance's four examples became Qwen3-8B, Qwen3.5-4B, Llama-3-8B-Instruct, DeepSeek-Math-7B-Instruct, see Deviations).
- SC is not a calibrated accuracy (0.012 to 0.089 below pass@1_fr); Mistral's confident-wrong rate (experiment 03 E3) was not rechecked.
- The independent recompute (plain Python Counter over the sample files, fr_extract, and the saved key and gold caches) matches analyze.py to 1e-15 for all 10 models (`results/indep_check.json`); it reuses the same Math-Verify caches, so it does not re-test Math-Verify. I read 6 random fallback extractions for DeepSeek-Math-RL (all correct final answers) and 6 for Qwen3.5-4B (all from truncated samples, so mid-reasoning guesses).

## Deviations
- Gemma-2-9B and Phi-3-mini (examples in the task) were not run: the host has Gemma-2-9B only as a base model and Phi-3-mini-128k has config.json only. Llama-3-8B-Instruct and DeepSeek-Math-7B-Instruct replace them. (Stated in PREREG before sampling.)
- Qwen3.5-4B failed to start on the first launch (vLLM spawn start method needs a `__main__` guard); `scripts/generate_spawn.py` fixes it; all models were then relaunched with `scripts/run_gen.sh` (resumable). No result depends on the failed launch.
- Part B has 10 models (6 old + 4 new), not 11.

## Next step (Sat 2026-11-28)
Second benchmark with the same 10 models and the same fallback: GSM8K or Minerva-style problems (different answer formats), plus 3 more models with pass@1_fr between 0.55 and 0.70 to put several pairs inside 0.05, and a thinking-mode Qwen3 run. Decision rule as in PREREG.
