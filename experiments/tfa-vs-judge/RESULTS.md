# TFA vs. the LLM judge — Results (MATH-500)

*Final conclusions. Full exploration log, diagnostics, retractions, and the correctness audit: [RESULTS_LOG.md](RESULTS_LOG.md).*

## TL;DR
On MATH-500, **Teacher-Forced Accuracy (TFA) is a valid judge-free *model-ranking* signal but not a
per-response judge replacement.** It ranks models the same way a frontier judge does (ρ ≈ 0.94), yet has
no item-level correlation with judged reasoning quality (partial ρ ≈ 0). None of the tested variants close
the item-level gap. Result verified robust after fixing a correctness-scoring bug.

## Setup
- **TFA** — teacher-force the model on the gold solution; score the fraction of gold tokens it predicts by
  argmax. Deterministic, judge-free, single forward pass (vLLM; verified bit-for-bit against HF ground truth).
- **Judge** — `gpt-5.2`, 0–10 rubric grading each model's *free-generated* solution's reasoning.
- **Correctness** — `\boxed{}` answer vs. gold via Math-Verify (`$`-delimited; see bug note below).
- **Models** — Qwen2.5-Instruct {0.5B, 1.5B, 3B, 7B, 14B, 32B}. **Data** — MATH-500 (500 problems → 3000 items).

## The finding: two levels, opposite answers

### Model level — POSITIVE (TFA ranks models like the judge)
| Model | mean-TFA | accuracy | mean-judge |
|---|---|---|---|
| 0.5B | 0.762 | 0.304 | 3.35 |
| 1.5B | 0.796 | 0.512 | 5.45 |
| 3B   | 0.795 | 0.668 | 6.92 |
| 7B   | 0.801 | 0.718 | 7.65 |
| 14B  | 0.815 | 0.786 | 8.00 |
| 32B  | 0.819 | 0.830 | 8.32 |

ρ(mean-TFA, accuracy) = **+0.94**, ρ(mean-TFA, mean-judge) = **+0.94** (n = 6, CI [0.5, 1.0]).
(Accuracies are the corrected, post-fix values; TFA↔accuracy reproduces the Putnam-AXIOM ~0.66 and exceeds it.)

### Item level — NEGATIVE (TFA cannot grade a single response)
Per (model, problem), the decisive test is the partial correlation controlling for the free correctness bit:

**partial ρ(TFA, judge | correct) = −0.02** (raw ρ = −0.03; within-correct ≈ −0.06).

TFA carries **no per-response reasoning-quality signal** beyond whether the answer is right.
(Sanity: ρ(judge, correct) = +0.72, so the judge itself is meaningful — the null is TFA's, not the judge's.)

## Why the item level fails
Gold-trace length is an **adversarial confound**: longer, more formulaic gold is more predictable
(ρ(TFA, gold-length) = +0.34) but marks harder problems the judge rates lower (ρ(judge, gold-length) = −0.33).
The shared driver pushes TFA and the judge in opposite directions. Fundamentally, **TFA measures the
predictability of the *reference*, not the quality of the model's *own* reasoning.**

## Improvement attempts (none recover item-level signal)
| Variant | Item-level partial ρ | Verdict |
|---|---|---|
| Surprisal- / IDF-weighted TFA | −0.16 / −0.01 | Fails (weighting can't create absent signal) |
| Contrastive TFA — answer-swap | apparent +0.18, **artifact** | The gain is a `1/gold_length` effect; length-independent signal ≈ 0 (−0.02 controlling for correctness + length) |
| Contrastive TFA — step-shuffle | −0.13 | Fails |

## Correctness-scoring bug (found, fixed, conclusions verified)
`answers_equivalent` parsed answers without `$…$`, so Math-Verify mis-parsed non-scalar answers:
**247 false negatives + 25 false positives** (9.1% of labels; accuracy underestimated ~7 pts). **Fixed** in
`tfa/boxed.py`. Re-scoring under corrected labels leaves every conclusion intact: item-level partial
−0.035 → −0.019 (still ≈ 0); model-level ρ(mean-TFA, corrected-accuracy) = +0.94 (unchanged).

## Bottom line
**Judge-free leaderboarding: yes. Per-response grading: no.** A per-response judge-free signal, if it exists,
must score the model's *own* computation (self-consistency, confidence, step-entailment) — not its ability to
predict a gold trace, which is confound-bound.

## Caveats / next
- Model-level rests on n = 6 (wide CI) — add Llama/Mistral families and more sizes to firm it up.
- Single judge (`gpt-5.2`); a cross-family judge is pending (the provided Anthropic key was invalid).
- MATH-500 only; TFA is saturated here (0.76–0.82). Harder sets (Putnam-AXIOM) may give more range but risk the weak-model floor.
- Prompting is raw completion-style (not chat-templated) — a cheap robustness check.
