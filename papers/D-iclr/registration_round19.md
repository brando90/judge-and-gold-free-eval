# Round 19 registration: a second frontier judge (R19-A) and a frontier thinking judge with wrong answers (R19-B)

Registered 2026-09-13, before any R19 call. Committed together with the producers named below.

## Context disclosed before any R19 call

All R8-A results for Claude Sonnet 5 (Messages API, thinking disabled) are known and reported in the paper (round 19 draft):
grading AUROC for correct answers that differ from the reference against wrong answers changes by -0.04 (replication, any-format
labels), -0.15 (MACE) and -0.08 (k-pool); false rejections rise by +9.2, +35.6 and +22.5 pp. Post hoc analyses of those scores
(`r15_checks.py`, `r16d_sonnet_noise_floor.py`, `r19_sonnet_wrong_tens.py`) found that, among correct answers Sonnet 5 scored 10
blind, 18.5% / 8.7% / 14.9% of those that differ from the reference drop to 3 or below with the reference against 0% of those that
match, and that Sonnet 5 gives a blind 10 to 1.8-3.7% of wrong answers. Thinking-mode results for Sonnet 5 exist only through the
command-line interface on 40 MACE questions with one answer of each kind (R5-A). No Claude Opus 5 score and no Sonnet 5
thinking-on API score exists for these pools.

Purpose. R19-A asks whether the grading harm and the acceptance result replicate on a second, stronger frontier judge.
R19-B asks, under the API design with wrong answers, whether a thinking mode removes Sonnet 5's grading harm on factual questions.

## Design

- Pools (unchanged R8-A subsamples, 16 candidates per task, blind and referenced calls), md5 at registration, identical to those
  recorded in `registration_round8.md`:
  - `runs/r8/sonnet_repl.jsonl` 4d7f8b6e4739f0bbff5c5e1de72b13d3 (40 tasks)
  - `runs/r8/sonnet_mace.jsonl` 3382472341d573884a0a46b9141fb4cb (40 tasks)
  - `runs/r8/sonnet_kpool.jsonl` 9809c9a2f172bc5f7c6b4e8de0a8f35f (22 tasks)
  - labels `runs/r8/lenient_repl.jsonl` 9d7f1d32d5ac4c4332c1f93088a49944, `runs/r8/lenient_kpool.jsonl` f797c999ad5b9a10a8dac9fa3d141789
- Harness: `experiments/tfa-vs-judge/scripts/sonnet_api_pool.py` (defaults reproduce R8-A; new flags only select the model,
  thinking mode, token limit and ledger prices). Prompts, rubric (a), call order and score parsing are unchanged.
  - R19-A: `--model claude-opus-5 --thinking disabled --max-tokens 512`, all three pools, output `runs/r19/opus_api/<pool>.jsonl`.
  - R19-B: `--model claude-sonnet-5 --thinking adaptive --max-tokens 8000`, MACE pool only, output `runs/r19/sonnet_think_api/mace.jsonl`.
- Spend caps: R19-A USD 40; R19-B USD 30 (ledger prices are conservative upper bounds).
- Producers (frozen, committed with this file):
  - `papers/analysis/r8_sonnet_analysis.py --scores <dir> --out <json>` (unchanged from R8-A) for AUROC, false rejections,
    margin and best-of-16 accuracy;
  - `papers/analysis/r19_acceptance.py --scores <dir> --out <json>` for the acceptance and blind-10 readouts.
- Intervals: task-level bootstrap as in the producers. Verdicts: **confirmed** when the 95% interval excludes zero in the predicted
  direction (or a point prediction holds), **falsified** when it excludes zero in the opposite direction (or a point prediction
  fails), **not confirmed** otherwise.
- Completion: a pool is scored if at least 20 tasks have all their calls scored. Unparseable replies are treated as missing, as in R8-A.

## Predictions

R19-A (Claude Opus 5, thinking disabled):
- **P-R19A1.** Replication pool, any-format labels: grading AUROC (non-matching correct vs wrong) is lower with the reference.
- **P-R19A2.** MACE: grading AUROC (non-matching correct vs wrong) is lower with the reference.
- **P-R19A3.** k-pool, any-format labels: grading AUROC (non-matching correct vs wrong) is lower with the reference.
- **P-R19A4.** MACE: the false-rejection rate of non-matching correct answers rises with the reference.
- **P-R19A5.** Pooled over the three pools, among correct answers scored 10 blind, the share scored 3 or below with the reference is
  higher for answers that differ from the reference than for answers that match it (point estimates, with the non-matching share above 0).
- **P-R19A6.** In each pool, at most 5% of wrong answers are scored 10 blind (point estimate).

R19-B (Claude Sonnet 5, adaptive thinking, MACE):
- **P-R19B1.** Grading AUROC (non-matching correct vs wrong) is lower with the reference.
- **P-R19B2.** The false-rejection rate of non-matching correct answers rises with the reference.
- **P-R19B3.** The AUROC fall is smaller in magnitude than R8-A's thinking-disabled fall of -0.15 (point estimate).

## Outcome

### R19-A (recorded 2026-09-13, after the run)

Run: 3,264 calls (1,280 replication, 1,280 MACE, 704 k-pool), 0 errors, 10 replies without a score (treated as missing; corrected 2026-09-13 from "1 unparseable reply": 1 on the replication pool and 9 on MACE cut off at 512 tokens, found in a supplement audit; no readout changes because the producers already treated them as missing); tasks with all calls
scored: 39 replication, 34 MACE, 22 k-pool (all at least 20). Ledger spend USD 32.19 at conservative prices.
Producers: `r8_sonnet_analysis.py --scores runs/r19/opus_api --out ../../papers/analysis/r19a_opus_results.json`,
`r19_acceptance.py --scores runs/r19/opus_api --out ../../papers/analysis/r19a_acceptance.json`.

| Readout (Opus 5; Sonnet 5 R8-A for comparison) | Replication | MACE | k-pool |
|---|---|---|---|
| AUROC non-matching vs wrong, change | -0.015 [-0.038, +0.009] (Sonnet -0.037) | -0.165 [-0.223, -0.110] (Sonnet -0.153) | -0.057 [-0.117, -0.013] (Sonnet -0.080) |
| False rejections, change (points) | +3.7 [+0.8, +6.9] | +36.3 [+26.7, +46.7] | +8.4 [+1.0, +20.2] |
| Wrong answers scored 10 blind | 5.9% (16 of 272) | 5.1% (13 of 257) | 8.2% (11 of 134) |
| Blind-10 correct answers scored <= 3 with the reference: non-matching / matching | 4.7% / 0% | 31.3% / 0% | 2.7% / 0% |

- **P-R19A1 not confirmed** (replication AUROC change -0.015, interval includes zero).
- **P-R19A2 confirmed** (MACE -0.165).
- **P-R19A3 confirmed** (k-pool -0.057).
- **P-R19A4 confirmed** (MACE false rejections +36.3).
- **P-R19A5 confirmed** (pooled: 76 of 525 non-matching blind-10 answers scored <= 3 with the reference, 14.5%, against 0 of 247 matching).
- **P-R19A6 falsified** (wrong answers scored 10 blind exceed 5% in every pool: 5.9%, 5.1%, 8.2%).

Observed and disclosed, not a protocol change: with thinking disabled and a score-only rubric, Opus 5 wrote visible reasoning before
the score on 25% (replication), 33% (MACE) and 24% (k-pool) of blind calls and 12-16% of referenced calls; the score was parsed from
the last integer, which was the final score in every inspected reply. A post hoc check (`r19c_opus_visible_reasoning.py`) restricted
to answers whose two calls both gave a bare score leaves the false-rejection rise essentially unchanged (MACE +35.3 against +35.0 pp).

### R19-B (recorded 2026-09-13, after the run; R19-A still running)

Run: 1,280 calls on `runs/r8/sonnet_mace.jsonl`, 0 errors, 0 unparseable replies, 40 of 40 tasks fully scored, ledger spend USD 1.67.
Producers: `r8_sonnet_analysis.py --scores runs/r19/sonnet_think_api --out ../../papers/analysis/r19b_sonnet_think_results.json`
and `r19_acceptance.py --scores runs/r19/sonnet_think_api --out ../../papers/analysis/r19b_acceptance.json`.

| Readout (MACE, k > 1) | Adaptive thinking (R19-B) | Thinking disabled (R8-A) |
|---|---|---|
| AUROC non-matching vs wrong, blind -> reference | 0.945 -> 0.854 | 0.938 -> 0.785 |
| Change | -0.090 [-0.140, -0.051] | -0.153 [-0.219, -0.097] |
| False rejections, change (points) | +14.9 [+8.2, +23.1] | +35.6 [+24.8, +48.0] |
| Margin, change | +3.12 [+2.14, +4.09] | +4.21 [+2.89, +5.65] |

- **P-R19B1 confirmed** (-0.090, interval excludes zero).
- **P-R19B2 confirmed** (+14.9 pp, interval excludes zero).
- **P-R19B3 confirmed** (point estimate -0.090 is smaller in magnitude than -0.15).

Descriptive (not predicted): with thinking, Sonnet 5 gives a blind 10 to 0 of 258 wrong answers and 22 of 382 correct answers; of the
13 non-matching correct answers it scored 10 blind, 1 is scored 3 or below with the reference, against 0 of 9 matching ones.
