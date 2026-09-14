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

## Verdicts

Confirmed when the interval excludes zero in the predicted direction (or a point prediction holds); falsified when it excludes zero in the
opposite direction (or a point prediction fails); not confirmed otherwise. Unparseable or errored calls are missing.

## Outcome

To be recorded here after the runs.
