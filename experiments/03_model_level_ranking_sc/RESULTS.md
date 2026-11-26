# RESULTS: experiment 03, model-level ranking by self-consistency (SC) vs gold accuracy

## Paper-ready

**Verdict: YES.** Model-level SC, which needs no gold answer, no human label, and no judge, orders the six models as gold pass@1 does: $D = 1$ of 15, Kendall $\tau = 0.867$, Spearman $\rho = 0.943$, Pearson $r = 0.997$, $P(D \le 3) = 1.00$, $\tau$ 95% interval $[0.73, 0.87]$. The discordant pair is DeepSeek-Math-7B-RL versus Mistral-7B-Instruct-v0.2, pass@1 gap $0.043$ (exact $0.042625$ in `results/results.json`, `E1_discordant_pairs`). The joint paper section for experiments 03 and 04, with the table and paths, is [`../../RESULTS.md`](../../RESULTS.md). The sections below are the lab record.

Dated 2026-11-25 (Wed). PREREG.md was committed before any sampling (cc1a7a3). Harness: vLLM (bf16, T=1.0, top_p=0.95,
max 1024 new tokens, seed 0, same prompt as `tfa-vs-judge/scripts/bon_generate.py`, `scripts/generate.py`) on skampere1 A100s
for 5 new models, Llama-3.1-8B-Instruct from the committed experiment-02 samples; analysis `scripts/analyze.py`
(Python 3, Math-Verify 0.9.0, numpy/scipy). 6 models x 500 MATH-500 problems x 16 samples. No plan account and no paid API
was used for sampling (lab GPUs). Models: Qwen2.5-7B-Instruct, Qwen3-4B and Qwen3-1.7B (non-thinking mode),
Llama-3.1-8B-Instruct, DeepSeek-Math-7B-RL, Mistral-7B-Instruct-v0.2.

## Takeaway (first)
- **YES, by the frozen rule in PREREG.md.** Model-level SC, which needs no gold, no human label and no judge, orders the 6 models
  like gold pass@1 with 1 of 15 pairs wrong (D = 1; Kendall tau 0.867, Spearman 0.943, Pearson 0.997). The decision rule needed
  D <= 2, every wrong pair's pass@1 gap < 0.05 (it is 0.043) and bootstrap P(D <= 3) >= 0.80 (it is 1.00).
- **The one wrong pair.** DeepSeek-Math-7B-RL (pass@1 0.145) vs Mistral-7B (0.102): SC says Mistral is ahead (0.062 vs 0.048) in
  99.3% of problem-bootstrap resamples (this resamples problems only, not samples or seeds). DeepSeek-Math writes a `\boxed{}`
  answer in only 26% of its samples and SC counts an unboxed sample as 0; that is the likely cause but it is **not tested** here
  (SC boxed-only gives DeepSeek-Math 0.530 vs Mistral 0.072, consistent with it; next step 1 tests it). The boxed-rate control
  alone ranks worse (D = 4), so SC is more than format.
- **The YES rests on a thin margin.** The wrong pair's pass@1 gap is 0.043 against the 0.05 line, and pass@1 also counts unboxed
  samples as wrong, so target and candidate share the same format penalty. Among boxed samples only (exact string match,
  independent check) DeepSeek-Math is right 47% of the time vs Mistral 8%, so a format-robust gold grader would likely widen that
  gap past 0.05 and could turn the verdict into INCONCLUSIVE or NO. The grader choice alone moves Llama pass@1 by 0.045 (D3).
- **What this does not show.** Six models whose pass@1 spans 0.10 to 0.72 are far apart; the two closest pairs (Qwen2.5-7B vs
  Qwen3-4B, gap 0.019, and DeepSeek-Math vs Mistral, gap 0.043) are where the ranking is least safe. SC does not replace the gold
  metric as a number: it reads 4 to 10 points below pass@1 and one model's confident answers are often wrong (E3). One
  benchmark (MATH-500), final-answer tasks only.

## Model-level table (n = 16 samples per problem; primary matcher = normalised canonical keys)
| model | pass@1 | maj@16 | pass@16 | **SC** (gold-free) | mean SCP (gold-free) | SC boxed-only | boxed rate |
|---|---|---|---|---|---|---|---|
| Qwen2.5-7B-Instruct | 0.721 | 0.834 | 0.902 | 0.680 | 0.763 | 0.738 | 0.910 |
| Qwen3-4B (non-thinking) | 0.702 | 0.810 | 0.846 | 0.662 | 0.720 | 0.879 | 0.767 |
| Qwen3-1.7B (non-thinking) | 0.633 | 0.764 | 0.820 | 0.580 | 0.659 | 0.773 | 0.747 |
| Llama-3.1-8B-Instruct | 0.377 | 0.604 | 0.774 | 0.281 | 0.422 | 0.362 | 0.723 |
| DeepSeek-Math-7B-RL | 0.145 | 0.514 | 0.622 | 0.048 | 0.184 | 0.530 | 0.263 |
| Mistral-7B-Instruct-v0.2 | 0.102 | 0.202 | 0.426 | 0.062 | 0.187 | 0.072 | 0.834 |

## E1: ranking agreement with pass@1 (D = discordant pairs of 15; cluster bootstrap over the 500 problems, 2000 resamples)
| candidate | needs gold | D | Kendall tau | Spearman | bootstrap P(D <= 3) | tau 95% CI |
|---|---|---|---|---|---|---|
| **SC (primary)** | no | 1 | 0.867 | 0.943 | 1.00 | [0.73, 0.87] |
| mean SCP | no | 1 | 0.867 | 0.943 | 1.00 | [0.87, 1.00] |
| SC boxed-only | no | 3 | 0.600 | 0.771 | 1.00 | [0.60, 0.60] |
| boxed rate (control) | no | 4 | 0.467 | 0.429 | 0.00 | [0.33, 0.47] |
| maj@16 | yes | 0 | 1.000 | 1.000 | 1.00 | [0.87, 1.00] |
| pass@16 | yes | 0 | 1.000 | 1.000 | 1.00 | [1.00, 1.00] |
Per pair, SC agrees with pass@1 in at least 96.9% of bootstrap resamples for 14 of 15 pairs; the exception is DeepSeek-Math vs
Mistral (0.7%). Pass@1 itself is split-half stable (tau 1.00); SC from one half of the samples vs pass@1 from the other half:
tau 0.867 (E4); SC half vs SC half: tau 1.00. Within MATH levels 1-2 and within levels 4-5 SC also gets 1 of 15 pairs wrong (E5).

## Secondary: level, confident wrongness
- E2 level: Pearson(SC, pass@1) = 0.997 over the 6 models, but SC - pass@1 is -0.04 to -0.10 for every model (SC underreads);
  mean SCP - pass@1 is +0.02 to +0.085 (SCP overreads). Neither is a calibrated accuracy.
- E3 confident wrongness (plurality answer at SCP >= 0.5): precision 0.93 (Llama), 0.95 (Qwen2.5), 0.98 (Qwen3-4B), 0.95
  (Qwen3-1.7B), 0.94 (DeepSeek-Math, coverage 7%), **0.74 (Mistral, coverage 6%)**. The pre-registered line (0.90 for every model)
  **fails** for Mistral. Mistral's few confident problems are often confidently wrong.

## Audit A1: argmax picks an unboxed sample
SC selection (argmax item SC, ties to the lowest index) picks sample 0 when no answer repeats; unboxed samples have SC 0, so
that sample can be unboxed. With 16 samples this is **not negligible** (pre-registered line: <= 1% of problems and
|accuracy difference| <= 0.005: **fails**).
| model@n | no repeated answer | selected sample unboxed | selection acc (02 rule) | selection acc (fixed: first boxed) | difference [95% CI] |
|---|---|---|---|---|---|
| Llama-3.1-8B @16 | 17.2% | 11.4% | 0.600 | 0.604 | +0.004 [0.000, 0.010] |
| Llama-3.1-8B @64 | 3.2% | 2.6% | 0.648 | 0.648 | 0.000 [0.000, 0.000] |
| Qwen2.5-7B | 2.4% | 2.0% | 0.834 | 0.834 | 0.000 |
| Qwen3-4B | 14.2% | 14.0% | 0.794 | 0.810 | +0.016 [0.006, 0.028] |
| Qwen3-1.7B | 15.2% | 15.0% | 0.748 | 0.764 | +0.016 [0.006, 0.028] |
| DeepSeek-Math-7B-RL | 35.4% | 30.6% | 0.454 | 0.514 | +0.060 [0.040, 0.082] |
| Mistral-7B | 34.4% | 8.8% | 0.202 | 0.202 | 0.000 |
The ranking of the 6 models by selection accuracy is the same under both rules (D = 0 vs pass@1). The effect shrinks with more
samples (Llama: 11.4% at 16 to 2.6% at 64), and the experiment-02 result (n = 64) is barely affected (difference 0.000).

## Audit A2: canonical keys vs pairwise Math-Verify (60 problems per model)
Pairs of distinct boxed answer strings in the same problem: key equality vs pairwise `verify` (either direction True).
| model | pairs | both equal | both different | key equal, verify not | key different, verify equal | mean abs dSCP |
|---|---|---|---|---|---|---|
| Llama-3.1-8B | 982 | 23 | 958 | 0 | 1 | 0.0010 |
| Qwen2.5-7B | 876 | 8 | 866 | 0 | 2 | 0.0073 |
| Qwen3-4B | 174 | 10 | 159 | 0 | 5 | 0.0073 |
| Qwen3-1.7B | 178 | 6 | 167 | 0 | 5 | 0.0052 |
| DeepSeek-Math-7B-RL | 370 | 8 | 358 | 0 | 4 | 0.0063 |
| Mistral-7B | 3743 | 31 | 3686 | 0 | 26 | 0.0156 |
Overall 0.68% of 6323 pairs disagree, all of them **missed merges** (different keys, pairwise-equivalent); no pair was wrongly
merged, no parse failure in the audited pairs. The model order by SC on the audited problems is identical under
keys and under pairwise verification. Pre-registered line (disagreement <= 1%, mean |dSCP| <= 0.01 for every model, ranking
unchanged): **fails on one leg**, Mistral's mean |dSCP| = 0.016 (it has by far the most distinct answer pairs, 3743 of 6323). So on these 60 problems per model the keys rank the same as pairwise `verify` and are slightly pessimistic for SC (they under-merge), not exact.
Every disagreement is a formatting variant that Math-Verify treats as equal and the keys do not: `33` vs `c = 33`, `10` vs `10\%`,
`Evelyn` vs `\text{Evelyn}`, `124^{\circ}` vs `x = 124^{\circ}`, `\cot x` vs `\frac{\cos x}{\sin x}`, `[\frac{\pi^2}{4}]` vs
`\{\frac{\pi^2}{4}\}`. A few merges by `verify` are loose (for example `360 + 72 = 432 degrees` vs `360^{\circ} \times 3 = 1080^{\circ}`
are judged equal by pairwise `verify`), so pairwise `verify` is not strictly better than the keys either. Math-Verify printed 8
"Timeout during comparison" lines in the full run; the script counts 0 timeouts in A2 because the library returns instead of raising,
so the A2 timeout column is a lower bound.

## Deviations and notes (all labelled; none changes the frozen verdict)
- D1 (route): the plan router runs agent CLIs, not bulk sampling, so generation ran on Brando's lab GPUs (skampere1), which uses no
  plan tokens and costs nothing extra; the router is used only for the independent review (below).
- D2: Qwen3-4B and Qwen3-1.7B have no `refs/main` in the host's offline HF cache, so `generate.py` got `--name` and they were loaded
  from their snapshot directories (same weights, `enable_thinking=False`). A first launch of Qwen3-4B was stopped after 250 of
  500 problems and resumed (rows are per problem and skipped when present; no duplicates, checked).
- D3: Llama-3.1-8B is the committed experiment-02 data (first 16 of its 64 samples, same prompt and sampling, harness
  `bon_generate.py`; n = 64 gives SC 0.291, pass@1 0.387). Gold correctness here uses the normalising Math-Verify check, so Llama
  pass@1 differs from the stored `oracle` bit (0.387 vs 0.342 at n = 64); the two agree on 95.4% of samples.
- D4: DeepSeek-Math-7B-RL boxes only 26% of its answers under this prompt which
  is the likely driver of the wrong pair (untested). The prompt was not changed after seeing this (frozen).
- Independent review (Claude Opus 5.5 through Brando's Vals plan router, read-only, 2026-11-25): leak check PASS (no gold reaches SC,
  SCP or SC-boxed), decision-rule check PASS (YES follows), wording check FAIL (fixed above: causes marked untested, thin margin
  stated, "no timeout" dropped). It ran out of turns before its own recomputation, so I ran that check myself: plain exact-string
  matching of the last `\boxed{}` on the 5 sample files gives SC 0.669 (Qwen2.5), 0.651 (Qwen3-4B), 0.570 (Qwen3-1.7B), 0.049
  (Mistral), 0.047 (DeepSeek-Math) and boxed rates equal to the table to 0.001; the order is the same, but Mistral vs DeepSeek-Math
  is nearly a tie under exact matching (0.002 apart vs 0.013 with the normalised keys). Llama (not in that check) is checked by
  `analyze.py` only. Receipt: `results/indep_check.json`.
- Not tested: models closer than a few points of pass@1, other benchmarks, thinking-mode models, answers that are not a final
  value, and a format-robust extractor (unboxed answers counted as agreeing with an extracted last expression).
- Matcher sensitivity: with the raw (un-normalised) matcher the model-level SC values are within 0.0002 of the primary ones and
  the order is identical (max absolute SC difference 0.0002; `results.json`, `model_level_raw_matcher`).

## Next (3 days, check Sat 2026-11-28)
1. Make SC format-robust (fall back to the last math expression when there is no box, so unboxed no longer counts as 0) and re-rank;
   test whether the DeepSeek-Math vs Mistral pair flips to concordant.
2. Add 4 models whose pass@1 sits inside the existing gaps (for example Qwen3-8B, Gemma-2-9B, Phi-3-mini, Qwen3.5-4B) to see
   whether SC resolves gaps of 0.02 to 0.05.
3. Same suite on a second benchmark (GSM8K or a harder set) before any claim beyond MATH-500.

## Files
`PREREG.md`, `scripts/` (generate, run_gen, analyze), `results/results.json`, `results/tables.md`, `results/model_rank.png`
(grid on), `results/gen/` (raw samples of the 5 new models), caches `key_cache.json`, `gold_cache.json`.
