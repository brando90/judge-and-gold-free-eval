# Round-4 registration, written and committed BEFORE any of its judge scores exist

Motivation: an external review of the round-3 draft (papers/D-iclr/reviews/round3_review.md) found four problems that new data can settle:
1. The open-judge expected score in `bon_judge.py` resolves the score token "1" to 10 or to 1 from the greedy continuation, for tokenizers that write "10" as two tokens (Qwen2.5, gemma-2, Mistral). It also substitutes 5.0 when too little probability lands on score tokens and no integer can be parsed. Neither is described in the paper.
2. The MATH-500 "unique answers" contrast shows the judge a full reference solution, not a bare final answer, so it is not like the constructed pools.
3. The claim that a thinking judge protects only where it can verify rests on one model and on an unmeasured notion of verification.
4. The paper never reports per-sample grading quality, only best-of-n selection.

Harnesses (committed with this file): `experiments/tfa-vs-judge/scripts/r4_judge_exact.py` (R4-A, R4-B); `r3_judge.py`, unchanged, with `--judge Qwen/Qwen3-14B` (R4-C); chains `r4_chain_gpu7.sh`, `r4_chain_gpu4.sh`, `r4_chain_gpu5.sh`.
Producers (frozen, committed with this file): `papers/analysis/r4_analysis.py` (R4-A, R4-B, R4-D) and `papers/analysis/r4_toggle14b_analysis.py` (R4-C).
All intervals: task-level bootstrap, 1,000 resamples, numpy default_rng(0).

**Verdict vocabulary (from this round on).** Confirmed: the 95% interval excludes zero in the predicted direction, or a point prediction holds. Not confirmed: the interval includes zero. Falsified: the interval excludes zero in the opposite direction, or a point prediction fails.

---

## The exact expected score (used by R4-A, R4-B, R4-D)

Prompts are identical to `bon_judge.py`, rubric a, temperature 0, top-20 logprobs at the first generated position.
- Single-token score candidates are the tokens for "0" to "10", with and without a leading space, as in `bon_judge.py`.
- When "10" is not a single token, for every "1" candidate token t in the top-20, the harness runs one more forward step on the prompt's token ids followed by t and reads q = P("0" | prompt, t). Candidate t then contributes value 10 with weight p_t·q and value 1 with weight p_t·(1−q).
- The expected score is renormalized over the captured score-token mass.
- If the captured mass is below 0.25, the greedy reply's first integer is used (flag 1). If there is none, the score is missing (flag 2): it is never selected and is excluded from means and AUROCs.
- Each row also stores the legacy value (the `bon_judge.py` rule, including its 5.0 substitution) and the greedy integer.

## R4-A. Main results under the exact estimator

**Design.** Judge Qwen2.5-7B-Instruct. Pools and conditions:
- replication pool: noref, ref;
- rotated replication pool (`bon_replrot`): ref;
- k-pool: noref, ref;
- MACE River+Language, pool pass rate in [0.05, 0.95]: noref, ref.

Qwen2.5-14B-Instruct, gemma-2-9b-it, and Mistral-7B-Instruct-v0.3 are scored on the k-pool (noref, ref).

**Readouts.**
- Rotation (`replrot_analysis.py` classes and per-task means): gainer, loser, and placebo changes under the exact, legacy, and greedy-integer scores.
- Replication-pool false-rejection rate (valid non-matching samples scored ≤ 3), referenced minus blind, as in `accuracy_readouts.py`.
- k-pool best-of-64 selection accuracy, referenced minus blind, by k and pooled over k > 1, tasks with pool pass rate in [0.2, 0.8].
- Shares of flag-1 and flag-2 scores, and mean |exact − legacy|, per file.

**Predictions.**
- **P-R4A1.** Exact estimator, Qwen2.5-7B: rotation loser change < 0, CI excluding zero.
- **P-R4A2.** Exact estimator, Qwen2.5-7B: rotation gainer change > 0, CI excluding zero.
- **P-R4A3.** Exact estimator: k-pool accuracy change pooled over k > 1 < 0, CI excluding zero, for each of Qwen2.5-7B, Qwen2.5-14B, gemma-2-9b, Mistral-7B (four cells).
- **P-R4A4.** Exact estimator, Qwen2.5-7B: replication-pool false-rejection increase > 0, CI excluding zero.
- Reported without prediction: the k = 1 accuracy change for each judge.

## R4-B. MATH-500 with a bare final-answer reference

**Design.** Qwen2.5-7B-Instruct and Qwen2.5-14B-Instruct on the 105 MATH-500 problems with pool pass rate in [0.2, 0.8], exact estimator. Three conditions:
- noref;
- ref: the reference solution, as in `bon_judge.py`;
- refans: the MATH answer field under the heading "Reference answer (trusted)". The system prompt is the reference rubric with "a reference solution known to be correct" replaced by "a reference answer known to be correct".

**Readouts.** Best-of-64 selection accuracy per condition; refans − noref, ref − noref, refans − ref.

**Predictions.**
- **P-R4B1.** refans − noref > 0, CI excluding zero, both judges.
- **P-R4B2.** ref − noref > 0, CI excluding zero, both judges.
- No prediction on refans − ref.

## R4-C. A second thinking toggle (Qwen3-14B)

**Design.** Identical to R3-A and R3-C with `Qwen/Qwen3-14B`:
- rotation subsample: ref, refrot, noref;
- k-subsample: ref, noref;
- MACE subsample: ref, noref;
- each with thinking on and off.

**Readouts.**
- As `r3_toggle_analysis.py`.
- Verification AUROC: per task, the AUROC of the blind score against validity, averaged over tasks with both valid and invalid samples. Computed on the k-subsample (arithmetic) and the MACE subsample (factual), per thinking arm.
- The same AUROC readouts computed for Qwen3-8B from its existing files are post hoc.

**Predictions.**
- **P-R4C1.** Thinking off: rotation loser change < 0, CI excluding zero.
- **P-R4C2.** Loser change, thinking off minus on, < 0, CI excluding zero.
- **P-R4C3.** Thinking on: MACE referenced-minus-blind margin > 0, CI excluding zero.
- **P-R4C4.** The thinking-on MACE margin difference is smaller than the thinking-off one (point estimates).
- **P-R4C5.** Thinking on: blind verification AUROC is higher on the k-subsample than on the MACE subsample (point estimates).

## R4-D. Verification and grading (computed on the R4-A files)

**Readouts** (Qwen2.5-7B, exact estimator).
- *Verification* V per pool: the mean per-task AUROC of blind scores against validity, over tasks with both valid and invalid samples. Pools: replication (all tasks), k-pool (all tasks), MACE (band), MATH-500 (band, from R4-B noref).
- *Grading*, per task, blind and referenced:
  - G_nm, the AUROC separating valid non-matching from invalid samples;
  - G_m, the same for valid matching samples;
  - G_all, for all valid against invalid samples.
  - On MACE and on the replication pool.
- Matching: normalized boxed answer as in `replrot_analysis.py` for the constructed pools; `mace_analysis.py`'s rule for MACE (as in R3-C).

**Predictions.**
- **P-R4D1.** V on MACE is lower than V on the k-pool and lower than V on the replication pool (point estimates).
- **P-R4D2.** MACE: G_nm referenced minus blind < 0, CI excluding zero.
- **P-R4D3.** MACE: G_all referenced minus blind > 0, CI excluding zero.
- **P-R4D4.** Replication pool: G_nm referenced minus blind < 0, CI excluding zero.

## Post hoc analyses planned alongside (no registration weight)

- MACE selection accuracy by k (2, 4, 6) from the frozen files.
- False-rejection rates at ≤ 5.
- A protocol regret table across pools.
- A seeded rerun of the judge-coverage analysis.

Whatever the outcomes, all are reported in the paper's ledger.

---

## Amendment 1 (recorded 2026-09-13): post hoc data-quality audit, before most R4 outputs were read

**What had been read.** The following R4 outputs had been read when this was written:
- the Qwen2.5-7B replication (noref, ref), rotated-replication, k-pool (noref, ref), and MACE noref files, through `r4_analysis.py`;
- the Qwen3-14B thinking-off files, through `r4_toggle14b_analysis.py`.

No Qwen2.5-14B, gemma-2-9b, Mistral-7B, MATH-500, MACE-referenced, or Qwen3-14B thinking-on output had been read.

**Audit** (`papers/analysis/r4_fallback_audit.py`, post hoc). It counts, in every legacy score file the paper uses, the scores exactly equal to the 5.0 fallback and the integer-valued scores, and it records how each judge's tokenizer writes the score tokens.
- **Tokenizers.**
  - phi-4 writes "10" as one token, so the "1" rule never applied to it.
  - Qwen2.5, Qwen3, and gemma-2 write "10" as two tokens.
  - Mistral-7B-Instruct-v0.3 has no single-token digit at all ("5" is two tokens, a space marker and the digit). Its score-token set is therefore empty, and every Mistral score, under either estimator, is the integer parsed from the greedy reply or the fallback.
- **Fallbacks in legacy files.**
  - Mistral-7B k-pool: 32.3% (noref a), 4.6% (ref a), 19.9% (blind-then-reveal a).
  - phi-4 decode-cost runs: 81.0%, 96.0%, and 97.6% at one, two, and three steps (rubric a). The phi-4 decode-cost margins therefore measure the fallback, not the judge.
  - Llama-3.1-8B synthetic-grid rubric-b files: 3.6% to 8.0%.
  - Ministral-8B referenced k-pool: 8.9%.
  - Qwen2.5-7B, phi-4, and gemma-2 main files: none.

**Consequences.**
- No R4 prediction, readout, or producer changes.
- The Mistral-7B cell of P-R4A3 compares greedy integers, with replies that contain no integer excluded as missing (flag 2), exactly as the harness specifies.
- In the paper, the phi-4 decode-cost cells become not evaluable, and the Mistral-7B and Ministral-8B results carry the fallback shares.

---

## Outcomes, R4-A, R4-C, R4-D (recorded 2026-09-13 after running the frozen producers; `r4_results.json`, `r4_toggle14b_results.json`)

**Flags.**
- Every Qwen2.5-7B, Qwen2.5-14B, and gemma-2-9b score used an expected value (flag 0).
- Mean |exact − legacy| per Qwen2.5-7B file: 0.067 to 0.170.
- Mistral-7B, which has no single-token digits:
  - noref: 3,210 greedy integers (flag 1) and 1,590 missing (flag 2);
  - ref: 4,610 and 190.

**R4-A.**
- Rotation, Qwen2.5-7B:

  | Score | Gainer | Loser | Placebo |
  |---|---|---|---|
  | Exact | +5.251 [+4.969, +5.527] | −5.405 [−5.727, −5.088] | +0.116 [−0.066, +0.297] |
  | Legacy, rescored | +4.955 | −5.014 | |
  | Greedy integer | +5.649 | −5.785 | |

  **P-R4A1 CONFIRMED, P-R4A2 CONFIRMED.**
- k-pool accuracy change pooled over k > 1: **P-R4A3 CONFIRMED** (four of four cells).
  - Qwen2.5-7B −0.359 [−0.513, −0.205]
  - Qwen2.5-14B −0.231 [−0.385, −0.077]
  - gemma-2-9b −0.154 [−0.282, −0.051]
  - Mistral-7B −0.085 [−0.118, −0.047]
- Reported without prediction, the k = 1 change:
  - Qwen2.5-7B −0.214 [−0.429, 0.000]
  - Qwen2.5-14B +0.036 [−0.214, +0.286]
  - gemma-2-9b 0.000
  - Mistral-7B −0.104 [−0.161, −0.044]
- Replication false-rejection increase: +0.277 [+0.228, +0.332]. **P-R4A4 CONFIRMED.**

**R4-C (Qwen3-14B).**
- Thinking off, loser change: −1.984 [−2.495, −1.494]. **P-R4C1 CONFIRMED.**
- Loser change, off minus on: −1.869 [−2.366, −1.384]. **P-R4C2 CONFIRMED.**
- Thinking on, MACE margin difference: +3.130 [+2.102, +4.236]. **P-R4C3 CONFIRMED.**
- On (+3.130) is smaller than off (+7.068). **P-R4C4 CONFIRMED.**
- Thinking on, blind verification AUROC: 0.860 on the k-subsample, above 0.810 on the MACE subsample. **P-R4C5 CONFIRMED.**
- Post hoc, Qwen3-8B verification AUROC (k-subsample vs MACE subsample): on 0.857 vs 0.799; off 0.864 vs 0.783.

**R4-D (Qwen2.5-7B).**
- Blind verification AUROC: replication 0.873, k-pool 0.871, MACE 0.735 (MATH-500 0.688). **P-R4D1 CONFIRMED.**
- MACE G_nm, referenced minus blind: −0.080 [−0.143, −0.015]. **P-R4D2 CONFIRMED.**
- MACE G_all, referenced minus blind: +0.073 [+0.020, +0.127]. **P-R4D3 CONFIRMED.**
- Replication G_nm, referenced minus blind: −0.275 [−0.305, −0.245]. **P-R4D4 CONFIRMED.**

**R4-B** is recorded below once the Qwen2.5-14B runs finish.
