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

### R20-A (recorded 2026-09-13; `papers/analysis/r20a_sonnet_retest.json`, `r20a_opus_retest.json`)

Unparseable or errored calls: Sonnet 5 none; Opus 5 one (MACE), missing. All pools scored.

| Judge | Pool | Non-matching correct, blind 10 | Retest 3 or below | Referenced 3 or below | Matching: retest / referenced 3 or below |
|---|---|---|---|---|---|
| Sonnet 5 | pooled | 318 | 0 (0.0%) | 41 (12.9%) | 0 / 0 of 137 |
| Sonnet 5 | MACE | 81 | 0 (0.0%) | 15 (18.5%) | 0 / 0 of 38 |
| Opus 5 | pooled | 525 | 2 (0.4%) | 76 (14.5%) | 0 / 0 of 246 |
| Opus 5 | MACE | 201 | 2 (1.0%) | 63 (31.3%) | 0 / 0 of 102 |

- **P-R20A1: confirmed.** **P-R20A2: confirmed.** **P-R20A3: confirmed** for both judges.
- Share still scored 10 on the retest (non-matching): Sonnet 5 pooled 87.1%; Opus 5 pooled 96.2%.

### R20-B (recorded 2026-09-13; `papers/analysis/r20b_sonnet_instruction.json`, `r20b_opus_instruction.json`)

Blind calls are the judge's existing ones, so plain and instructed referenced runs share their blind baseline. Tasks with all calls
scored: Sonnet 5 40 and 40; Opus 5 MACE 37 (at least 20, so scored).

| Judge | Pool | AUROC change, plain | AUROC change, instruction | False-rejection rise, plain | Rise, instruction | Margin, plain / instruction |
|---|---|---|---|---|---|---|
| Sonnet 5 | MACE | −0.153 [−0.219, −0.097] | −0.065 [−0.115, −0.019] | +35.6 pp | +18.1 pp [9.9, 28.0] | 4.21 / 2.72 |
| Sonnet 5 | replication | −0.037 [−0.068, −0.011] | −0.033 [−0.065, −0.006] | +9.2 pp | +6.1 pp [2.4, 10.6] | 1.58 / 0.95 |
| Opus 5 | MACE | −0.165 [−0.223, −0.110] | −0.053 [−0.105, −0.004] | +36.3 pp | +8.1 pp [2.1, 15.9] | 3.56 / 0.64 |

- **P-R20B1: confirmed.** **P-R20B2: confirmed.** **P-R20B3: confirmed.** **P-R20B4: confirmed.**
- Reading: the instruction halves the false-rejection rise for Sonnet 5 on MACE and cuts it by three quarters for Opus 5, but in every
  cell the grading AUROC with the instruction is still lower than blind.

### R20-C (recorded 2026-09-13; `papers/analysis/r20c_leaderboard.json`)

Generation: 150 questions per API generator, 0 errors, every reply boxed; spend USD 0.11 (Haiku 4.5), 0.19 (Sonnet 5), Opus 5 see
`runs/r20/mace_gen/spend_claude-opus-5.json`. Grading: 1,200 calls, 0 errors, 0 unparseable, USD 0.70. Questions with all eight calls
scored and labels for every generator: 149 (at least 100, so scored).

| Generator | Answer list | Blind judge | Referenced judge | Referenced minus list | Correct answers differing from reference | False rejections of those, blind / referenced |
|---|---|---|---|---|---|---|
| Llama-3.1-8B-Instruct | 69.1% | 67.8% | 55.7% | −13.4 [−20.8, −7.4] | 70 of 103 | 4.3% / 18.6% |
| Claude Haiku 4.5 | 94.6% | 92.6% | 55.0% | −39.6 [−47.7, −31.5] | 110 of 141 | 0.9% / 41.8% |
| Claude Sonnet 5 | 98.7% | 96.0% | 77.2% | −21.5 [−28.2, −14.8] | 107 of 147 | 0.0% / 23.4% |
| Claude Opus 5 | 100.0% | 99.3% | 85.2% | −14.8 [−20.1, −9.4] | 109 of 149 | 0.0% / 11.0% |
| Pooled | | −1.7 [−3.5, 0.0] vs list | | −22.3 [−27.0, −18.0] | | 1.0% / 24.2% (matching: 0% referenced) |

- **P-R20C1: confirmed.** **P-R20C2: confirmed.** **P-R20C3: confirmed** (all four generators).
- Reported without a prediction: the answer list and the blind judge rank Opus 5 > Sonnet 5 > Haiku 4.5 > Llama-3.1-8B; the referenced
  judge ranks Llama-3.1-8B (55.7%) one question above Haiku 4.5 (55.0%). The undercount does not track the share of correct answers that
  differ from the reference (68% to 78% for all four); it tracks how often the judge rejects those answers (11% to 42%).
