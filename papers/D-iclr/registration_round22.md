# Round 22 registration: a frontier-model audit of the any-format labels (R22-A) and a second reference draw for the benchmark (R22-B)

Registered 2026-09-13, before any R22 call. Committed together with the builders, harness and producers named below.

## Context disclosed before any R22 call

- The main text uses *any-format labels* on the constructed pools (`papers/analysis/r8_lenient_labels.py`): the boxed answer if
  present, otherwise an integer rule applied to the last line with a digit, checked by each task's constraint. A post hoc second
  labeling had Qwen2.5-14B-Instruct read every unboxed reply (`runs/r8/model_{repl,kpool}.jsonl`); it agrees with the any-format rule on
  88% of unboxed replies. No human has checked either labeling.
- All benchmark results of R20-C and R21-A are known (`registration_round20.md`, `registration_round21.md`): with the first reference
  draw, pooled referenced minus answer-list accuracy is −22.3 (Sonnet 5), −15.6 (Opus 5, 141 questions) and −20.1 (Haiku 4.5). The
  round-21 review asked how much these numbers and the Haiku 4.5 / Llama-3.1-8B ranking depend on which listed answer was drawn as the
  reference.

## R22-A: Claude Opus 5 reads a stratified sample of unboxed replies

- Sample (`experiments/tfa-vs-judge/scripts/r22_build_label_sample.py`, `random.Random(22)`): from the replication pool and the k-pool
  (Llama-3.1-8B-Instruct samples), every reply without `\boxed{`, stratified by pool and by any-format label; 50 replies labeled correct
  and 50 labeled wrong per pool, 200 in total, with each stratum's population size. Output `runs/r22/label_sample.jsonl`.
- Reader (`scripts/r22_opus_read_answers.py`): `claude-opus-5`, Messages API, thinking disabled, temperature 0, 200 output tokens, with the
  extraction prompt of `scripts/r8_extract_answers.py` verbatim. Output `runs/r22/opus_read.jsonl`; cap USD 10.
- Producer (`papers/analysis/r22_label_audit.py`): reader label = registered label OR the constraint check (`check` of
  `r8_lenient_labels.py`, copied verbatim) accepts the integers of the last non-empty line of the reader's answer; NONE or no digit on
  that line keeps the registered label. Readouts per stratum and pooled with weights proportional to stratum population sizes.
- **P-R22A1.** Pooled weighted agreement between the any-format label and the reader label is at least 85% (point estimate).
- **P-R22A2.** Among replies the any-format rule labels correct, the reader confirms at least 90% (weighted point estimate).
- **P-R22A3.** Among replies the any-format rule labels wrong, the reader calls at most 15% correct (weighted point estimate).
- Reported without a prediction: per-pool readouts, the Qwen2.5-14B labels against the reader, the NONE share, and the disagreements.
- Scored if at least 180 of the 200 replies have a reader answer.

## R22-B: a second reference draw for the benchmark study

- Pool (`scripts/r22_build_redraw_pool.py`, `random.Random(23)`): for each of the 149 questions of `runs/r20/mace_gen/pool.jsonl`, a
  second reference drawn from the listed answers that neither contain nor are contained in the first (normalized); questions with no
  such answer are dropped. Same answers and answer-list labels; match groups recomputed. Output `runs/r22/redraw_pool.jsonl`.
- Calls: each grader's existing blind calls are copied into `runs/r22/redraw_{sonnet,opus,haiku}_api/pool.jsonl`; the harness adds
  referenced calls with the second reference only (`scripts/sonnet_api_pool.py --conds ref`), with the R20-C / R21-A settings
  (thinking disabled, 512 tokens): Sonnet 5 defaults (cap USD 5); Opus 5 `--model claude-opus-5 --price-in 15 --price-out 75` (cap USD
  15); Haiku 4.5 `--model claude-haiku-4-5-20251001 --price-in 1 --price-out 5` (cap USD 5).
- Producer (`papers/analysis/r22_redraw_analysis.py --grader G --draw1 <first-draw scores> --draw2 <second-draw scores>`), a score of 7 or
  above counting as correct, on questions with blind and both referenced calls scored for all four answers.
- For each grader G in {Sonnet 5, Opus 5, Haiku 4.5}:
  - **P-R22B1 (G).** With the second reference, pooled referenced accuracy is below answer-list accuracy (question-level interval excludes zero).
  - **P-R22B2 (G).** Correct answers that match the first reference but not the second are credited (score 7 or above) less often under
    the second draw than under the first (point estimate).
  - **P-R22B3 (G).** Correct answers that match the second reference but not the first are credited more often under the second draw than
    under the first (point estimate).
- Reported without a prediction: per-model accuracy under each draw and its change between draws; rankings under each draw; Haiku 4.5
  minus Llama-3.1-8B accuracy under each draw with paired intervals.
- Scored for a grader if at least 100 questions have all calls scored.

## Amendment 1 (2026-09-13, before any reader answer existed)

The first R22-A run returned HTTP 400 for all 200 calls ("`temperature` is deprecated for this model"), so no reader answer and no
spend exist. The reader now runs with the API's default temperature; nothing else changes. The failed rows stay in
`runs/r22/opus_read.jsonl` and the producer ignores rows with errors. No R22-B result had been read when this amendment was written
(the Sonnet 5 second-draw producer had been run; its output is not an input to R22-A).

## Verdicts

Confirmed when the interval excludes zero in the predicted direction (or a point prediction holds); falsified when it excludes zero in the
opposite direction (or a point prediction fails); not confirmed otherwise. Unparseable or errored calls are missing.

## Outcome

### R22-B (recorded 2026-09-13; `papers/analysis/r22b_redraw_{sonnet,opus,haiku}.json`)

Pool: 149 questions, none dropped; 318 of 596 answers change match group between draws. Referenced calls: 596 per grader, no errors;
unparseable replies are missing (Opus 5 again truncates some referenced replies at 512 tokens). Questions scored (blind and both draws
complete): Sonnet 5 149, Opus 5 136, Haiku 4.5 149.

| Grader | Referenced − list, draw 1 | Draw 2 | Draw 2 − draw 1 | Stop matching: credited draw 1 → 2 (n) | Start matching: draw 1 → 2 (n) | Haiku 4.5 − Llama-3.1-8B, draw 1; draw 2 |
|---|---|---|---|---|---|---|
| Sonnet 5 | −22.3 | −21.3 [−25.8, −16.8] | +1.0 [−3.9, +5.9] | 100% → 61.8% (144) | 64.4% → 99.4% (174) | −0.7; +6.7 [−3.4, +16.1] |
| Opus 5 | −15.1 | −16.9 [−21.3, −12.7] | −1.8 [−6.6, +2.9] | 99.3% → 72.1% (140) | 76.2% → 99.4% (164) | +16.2; +25.7 |
| Haiku 4.5 | −20.1 | −17.1 [−21.1, −13.3] | +3.0 [−1.3, +7.4] | 99.3% → 74.3% (144) | 68.4% → 97.7% (174) | −7.4; +3.4 [−6.0, +12.8] |

(Opus 5's draw-1 value here is on its 136 questions with both draws complete; on 141 questions it was −15.6.)

- **P-R22B1:** Sonnet 5 **confirmed**; Opus 5 **confirmed**; Haiku 4.5 **confirmed**.
- **P-R22B2:** Sonnet 5 **confirmed** (−38.2 pp); Opus 5 **confirmed** (−27.1); Haiku 4.5 **confirmed** (−25.0).
- **P-R22B3:** Sonnet 5 **confirmed** (+35.1 pp); Opus 5 **confirmed** (+23.2); Haiku 4.5 **confirmed** (+29.3).
- Reported without a prediction: per-model referenced accuracy moves by at most 8.1 points between draws (Haiku 4.5 graded by itself).
  Under the second draw, Sonnet 5 and Haiku 4.5 rank Haiku 4.5 above Llama-3.1-8B again (point estimates; paired intervals include
  zero), where under the first draw they had put Llama-3.1-8B level with or above it.

### R22-A (recorded 2026-09-13; `papers/analysis/r22a_label_audit.json`)

Reader run after Amendment 1: 200 of 200 replies answered, no errors, ledger spend USD 2.56. Scored (at least 180).

| Stratum (population) | Agreement, any-format vs reader | Agreement, Qwen2.5-14B vs reader | Reader calls correct | Reader NONE |
|---|---|---|---|---|
| Replication, any-format correct (760) | 84% | 96% | 84% | 2% |
| Replication, any-format wrong (2,190) | 96% | 96% | 4% | 64% |
| k-pool, any-format correct (453) | 90% | 96% | 90% | 8% |
| k-pool, any-format wrong (1,608) | 88% | 92% | 12% | 60% |
| Pooled, population-weighted | 91.1% | 94.7% | | 48.3% |

- **P-R22A1: confirmed** (91.1%).
- **P-R22A2: falsified** (the reader confirms 86.2% of any-format "correct" replies; predicted at least 90%).
- **P-R22A3: confirmed** (the reader calls 7.4% of any-format "wrong" replies correct).
- Disagreements (21 of 200): of the 13 replies the any-format rule credits and the reader does not, 6 end by listing several numbers (the
  rule takes the last integer of the last line) and 5 commit to no answer; of the 8 replies the rule rejects and the reader credits, 5
  are subset-sum or Goldbach answers written in an order or format the rule misparses. The Qwen2.5-14B reading agrees with the reader more
  often than the any-format rule does on every stratum.
