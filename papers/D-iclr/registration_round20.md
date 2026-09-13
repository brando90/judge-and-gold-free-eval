# Round 20 registration: a within-interface noise floor (R20-A), the full-credit instruction measured by grading (R20-B), and a benchmark-level consequence (R20-C)

Registered 2026-09-13, before any R20 call. Committed together with the harness changes, builders and producers named below.

## Context disclosed before any R20 call

All R8-A (Sonnet 5, API, thinking disabled), R19-A (Opus 5, API, thinking disabled) and R19-B (Sonnet 5, API, adaptive thinking) results
are known (see `registration_round8.md`, `registration_round19.md`). In particular: among correct answers scored 10 blind, the share scored
3 or below with the reference is 18.5% / 8.7% / 14.9% (Sonnet 5; MACE, replication, k-pool) and 31.3% / 4.7% / 2.7% (Opus 5) for answers
that differ from the reference, and 0% for answers that match it. The existing noise floor for Sonnet 5 used a command-line blind call
on the replication pool only (0 of 111). The full-credit instruction was run before only on the k-pool (Sonnet 5, GPT-4.1) and the
synthetic grid, and measured only as a margin. No generator other than Llama-3.1-8B-Instruct has answered the MACE questions.

## R20-A: second blind call through the same interface

- Pools: `scripts/r20_build_pools.py` selects, from the R8-A subsamples, every correct answer (matching or non-matching) the judge scored
  10 on its first blind API call: Sonnet 5 from `runs/r8/sonnet_api/`, Opus 5 from `runs/r19/opus_api/`. Output
  `runs/r20/retest_pools/<judge>_<pool>.jsonl`.
- Calls: `scripts/sonnet_api_pool.py --conds noref` with the same model and settings as the first call (Sonnet 5: defaults; Opus 5:
  `--model claude-opus-5 --thinking disabled`). Output `runs/r20/<judge>_retest_api/<pool>.jsonl`. Caps: Sonnet USD 10, Opus USD 25.
- Producer: `papers/analysis/r20_retest_analysis.py`.
- **P-R20A1 (Sonnet 5).** Pooled over the three pools, among non-matching correct answers scored 10 on the first blind call, the share
  scored 3 or below on the second blind call is at most 2%, and below the share scored 3 or below on the referenced call (point estimates).
- **P-R20A2 (Opus 5).** The same for Opus 5.
- **P-R20A3 (MACE, both judges).** On MACE alone, the same comparison holds for each judge (point estimates).

## R20-B: the full-credit instruction, measured by false rejections and grading AUROC

- Score files: `scripts/r20_build_pools.py` seeds `runs/r20/<judge>_inst_api/<pool>.jsonl` with the judge's existing blind calls; the
  harness then adds referenced calls whose rubric has the any-valid-answer sentence appended verbatim (as in `bon_judge.py` and
  `frontier_api_judge.py`): `--conds ref --instruction anyvalid`. Sonnet 5 on MACE and the replication pool; Opus 5 on MACE.
  Caps: Sonnet USD 10, Opus USD 25.
- Producer: `papers/analysis/r8_sonnet_analysis.py --scores runs/r20/<judge>_inst_api --out <json>` (unchanged), compared with the
  judge's plain referenced run.
- **P-R20B1 (Sonnet 5, MACE).** With the instruction, grading AUROC (non-matching correct vs wrong) is still lower than blind (interval
  excludes zero).
- **P-R20B2 (Opus 5, MACE).** The same for Opus 5.
- **P-R20B3 (Sonnet 5, MACE).** The false-rejection rise with the instruction is smaller than without it (+35.6 pp; point estimate).
- **P-R20B4 (Sonnet 5, replication).** The false-rejection rise with the instruction is smaller than without it (+9.2 pp; point estimate).

## R20-C: does referenced grading change a benchmark's numbers?

- Questions: all MACE River and Language questions with more than one correct answer (150).
- Generators: Llama-3.1-8B-Instruct (the first stored sample of each question's 64-sample pool) and, through the API, one answer each
  from `claude-haiku-4-5-20251001`, `claude-sonnet-5` and `claude-opus-5` with the MACE generation prompt of `bon_generate.py`
  (`scripts/r20_generate_mace.py`, default temperature, 512 tokens; caps USD 15 each).
- Labels: `scripts/r20_build_leaderboard_pool.py`, with the MACE oracle and matching rule of `mace_oracle.py`.
- Judge: Claude Sonnet 5 through the API, thinking disabled, blind and referenced (`scripts/sonnet_api_pool.py`, defaults), on
  `runs/r20/mace_gen/pool.jsonl`; output `runs/r20/leaderboard_sonnet_api/pool.jsonl`; cap USD 10. Sonnet 5 also grades its own answers;
  we report this and do not treat it as a limitation of the undercount, which compares graders on the same answers.
- Grading: a score of 7 or above counts as correct.
- Producer: `papers/analysis/r20_leaderboard_analysis.py`.
- **P-R20C1.** Pooled over generators, the referenced judge's accuracy is below answer-list accuracy (question-level interval excludes zero).
- **P-R20C2.** Pooled over generators, the share of non-matching correct answers scored 3 or below is higher with the reference than blind (point estimate).
- **P-R20C3.** For every generator with at least 10 correct answers that differ from the reference, referenced accuracy is below answer-list accuracy (point estimates).
- Reported without a prediction: rankings under the three graders, the blind judge's over- or under-count, and the relation between a
  generator's undercount and its share of correct answers that differ from the reference.

## Verdicts and completion

Confirmed when the interval excludes zero in the predicted direction (or a point prediction holds); falsified when it excludes zero in the
opposite direction (or a point prediction fails); not confirmed otherwise. Unparseable or errored calls are missing. R20-A and R20-B pools
are scored if at least 20 tasks have all their calls scored; R20-C if at least 100 questions have all eight calls scored.

## Outcome

To be recorded here after the runs.
