# Round 23 registration: a same-reference regrade as the noise floor for the reference-draw effect (R23-A)

Registered 2026-09-13, before any R23 call. Committed together with the seeding script and producer named below.

## Context disclosed before any R23 call

All R20-C, R21-A and R22-B benchmark results are known (`registration_round20.md` to `registration_round22.md`). With the first reference
draw, pooled referenced minus answer-list accuracy is −22.3 (Sonnet 5), −15.6 (Opus 5, 141 questions) and −20.1 (Haiku 4.5); with a
second draw, −21.3, −16.9 (136 questions) and −17.1. Correct answers that match the first reference but not the second are credited
100%, 99.3% and 99.3% under the first draw and 61.8%, 72.1% and 74.3% under the second; answers that match only the second go from 64.4%,
76.2% and 68.4% to 99.4%, 99.4% and 97.7%. The Haiku 4.5 minus Llama-3.1-8B gap is −0.7 and +6.7 (Sonnet 5), +16.2 and +25.7 (Opus 5, 136
questions) and −7.4 and +3.4 (Haiku 4.5) under the two draws, all Sonnet 5 and Haiku 4.5 intervals including zero; a reviewer's
unregistered bootstrap of the between-draw change in that gap gave +7.4 [−3.4, +18.1], +9.6 [+0.7, +19.1] and +10.7 [0.0, +21.5]. No
referenced call has been repeated with the same reference, so these changes have no noise floor. The graders run at the API's default
temperature.

## R23-A: re-grade every answer with the first reference

- Score files: `experiments/tfa-vs-judge/scripts/r23_seed_regrade.py` copies each grader's blind calls from its first-draw file into
  `runs/r23/regrade_{sonnet,opus,haiku}_api/pool.jsonl`; the harness then adds referenced calls with the first reference on the unchanged
  pool `runs/r20/mace_gen/pool.jsonl` (`scripts/sonnet_api_pool.py --conds ref`) with the R20-C / R21-A / R22-B settings (thinking disabled,
  512 tokens): Sonnet 5 defaults (cap USD 5); Opus 5 `--model claude-opus-5 --price-in 15 --price-out 75` (cap USD 15); Haiku 4.5
  `--model claude-haiku-4-5-20251001 --price-in 1 --price-out 5` (cap USD 5).
- Producer: `papers/analysis/r23_regrade_analysis.py --grader G --orig <first-draw scores> --regrade <regrade scores> --draw2 <second-draw
  scores>`, on the questions whose blind call, original referenced call, regrade referenced call and second-draw referenced call are all
  scored for the four answers; a score of 7 or above counts as correct; question-level bootstrap, 2,000 resamples, seed 0, paired.
- Readouts: per model and pooled, the same-draw change (regrade minus original referenced accuracy) and the between-draw change (second
  draw minus original); for correct answers that match the first reference but not the second ("stop matching") and the reverse ("start
  matching"), the credited share under the original call, the regrade and the second draw; the Haiku 4.5 minus Llama-3.1-8B gap under each
  and its same-draw and between-draw changes; the number of the six model pairs whose order differs from the original call under the
  regrade and under the second draw.

### Predictions

For each grader G in {Sonnet 5, Opus 5, Haiku 4.5}:

- **P-R23A1 (G).** Pooled referenced accuracy under the regrade is within 3 points of the original referenced accuracy (point estimate).
- **P-R23A2 (G).** Among correct answers that stop matching, the regrade credits more of them than the second draw does (paired point
  estimate: credited under the regrade minus credited under the second draw is above zero).
- **P-R23A3 (G).** Among correct answers that start matching, the second draw credits more of them than the regrade does (paired point
  estimate above zero).

Reported without a prediction: same-draw against between-draw changes in per-model accuracy and in the Haiku 4.5 minus Llama-3.1-8B gap,
with intervals, and the pairwise order flips.

## Verdicts and completion

Point predictions are confirmed when they hold and falsified otherwise. Unparseable or errored calls are missing. A grader is scored if at
least 100 questions have all calls scored.

## Outcome (recorded 2026-09-13; `papers/analysis/r23a_regrade_{sonnet,opus,haiku}.json`)

Runs: 596 referenced calls per grader after seeding, no errors; unscored replies: Sonnet 5 0, Opus 5 4, Haiku 4.5 0 (spend USD 0.37,
4.29, 0.70). Questions with all four calls complete for all answers: Sonnet 5 149, Opus 5 135, Haiku 4.5 149 (all at least 100, scored).

| Grader | Pooled change: regrade; second draw | Stop matching credited: first call, regrade, draw 2 (n) | Start matching: first call, regrade, draw 2 (n) | Haiku 4.5 − Llama-3.1-8B gap change: regrade; draw 2 | Pairwise flips of 6: regrade; draw 2 |
|---|---|---|---|---|---|
| Sonnet 5 | +0.5 [−1.5, +2.5]; +1.0 | 100.0%, 99.3%, 61.8% (144) | 64.4%, 65.5%, 99.4% (174) | 0.0 [−6.7, +7.4]; +7.4 [−3.4, +18.1] | 0; 1 |
| Opus 5 | −1.9 [−4.3, +0.7]; −2.4 | 99.3%, 99.3%, 72.1% (140) | 77.6%, 74.5%, 99.4% (161) | −0.7 [−6.7, +5.9]; +8.9 [+0.7, +17.8] | 0; 1 |
| Haiku 4.5 | −0.3 [−3.5, +2.9]; +3.0 | 99.3%, 98.6%, 74.3% (144) | 68.4%, 69.0%, 97.7% (174) | +10.7 [+2.7, +19.5]; +10.7 [0.0, +21.5] | 2; 1 |

- **P-R23A1:** Sonnet 5 **confirmed**; Opus 5 **confirmed**; Haiku 4.5 **confirmed**.
- **P-R23A2:** Sonnet 5 **confirmed** (+37.5 pp); Opus 5 **confirmed** (+27.1); Haiku 4.5 **confirmed** (+24.3).
- **P-R23A3:** Sonnet 5 **confirmed** (+33.9 pp); Opus 5 **confirmed** (+24.8); Haiku 4.5 **confirmed** (+28.7).
- Reported without a prediction: per-model same-draw changes are within 4.1 points except Haiku 4.5 graded by itself (+6.7 [+0.7,
  +12.8]); for Haiku 4.5 as grader, the Haiku 4.5 − Llama-3.1-8B gap moves as much under the same-reference regrade as under the second
  draw, so ranking changes between draws are not distinguishable from call-to-call variation. The credit shift for answers whose match
  changes is a draw effect: the regrade leaves it within about 3 points.
