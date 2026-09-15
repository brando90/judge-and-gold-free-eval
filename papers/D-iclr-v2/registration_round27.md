# Round 27 registration: P3 for correctness prompts (R27-A) and false acceptance on hard single-answer questions (R27-B)

Registered 2026-09-15, before any R27 analysis or call. Committed together with `papers/analysis/r27_analysis.py`,
`experiments/tfa-vs-judge/scripts/r27_generate.py`, `scripts/r27_build_pool.py`, `scripts/r27_run.sh`, and the vendored
`scripts/vendor/centerforaisafety_hle_eval_run_model_predictions.py` (commit 67b3251).

## Context disclosed before R27

All results through R26 are known (`registration_round24.md` to `registration_round26.md`). On the benchmark pool
(`runs/r20/mace_gen/pool.jsonl`), the R25 chain-of-thought, verify-first and solve-first prompts and the R26 direct prompt credit
differing correct answers slightly less with the reference than blind (R25: 0.8 to 8.6 points; R26 direct: 91.4% to 73.2% for GPT-4.1
and 96.5% to 83.3% for Sonnet 5), while credit for matching correct answers changes by at most 1.4 points in R25 (not computed for the R26 direct prompt); the answer-level
transitions for answers credited blind (the P3 readout) have not been computed. A fresh area-chair review of v2
(`reviews/v2_final_ac_review.md`) noted that P3 was never tested for these prompts, and that the recommended solve-first prompt was
tested only where judges answer most questions correctly. No R27-B call has been made; the scripts were run only with `--dry-run`.

## R27-A: P3 for prompts that ask whether the answer is correct (stored data; pre-specified re-analysis)

Cells: `runs/r25/{cot,verify,solve}_{gpt41,sonnet}/pool.jsonl` and `runs/r26/bench_direct_{gpt41,sonnet}/scores.jsonl` (eight cells).
Producer: `r27_analysis.py --part a --cell <cell> --scores <file> --out papers/analysis/r27a_<cell>.json`. Among correct answers
credited blind, the share not credited with the reference, for answers that differ from the reference and answers that match it;
question bootstrap of the difference. No same-prompt second blind call exists for these prompts, so there is no noise floor.

- **P-R27A1** (each cell). Blind-accepted correct answers that differ from the reference are rejected with the reference more often than
  blind-accepted answers that match it (point estimate).

## R27-B: false acceptance on hard single-answer questions

- **Questions.** The 200 text-only exact-answer HLE questions sampled (seed 0) for the second prevalence audit
  (`papers/analysis/prevalence_v2/items_hle.jsonl`); HLE answers are single, so the reference-agreement effect is not at issue here.
- **Answers.** `gpt-4.1-mini-2025-04-14` and `claude-haiku-4-5-20251001` answer every question with HLE's official system prompt
  (`scripts/r27_generate.py`; 2,048 output tokens); `scripts/r27_build_pool.py` builds `runs/r27/hle_pool.jsonl` (400 answers).
- **Labels.** HLE's official judge: the verbatim HLE judge prompt with `o3-mini-2025-01-31` and structured output
  (`scripts/r24_grader_pool.py --template hle`), against the HLE answer. A label call without a parsed result is missing.
- **Graders under test.** GPT-4.1 (`gpt-4.1-2025-04-14`) and Sonnet 5 (`claude-sonnet-5`) with `scripts/r26_judges.py` (the R26
  settings): the verbatim HLE judge (reference), the direct prompt and the solve-first prompt (blind and reference).
- **Producer.** `r27_analysis.py --part b --judge <j> --labels runs/r27/labels_o3mini/pool.jsonl --hle ... --direct ... --solve ...
  --out papers/analysis/r27b_<j>.json`, on questions whose two answers have a label and every condition scored; scored if at least 100
  questions. False acceptance = share of label-wrong answers credited; recall = share of label-correct answers credited.

For each judge:
- **P-R27B1.** Solve-first with the reference accepts at most 5 points more wrong answers than the verbatim HLE judge (point).
- **P-R27B2.** The direct prompt with the reference accepts at most 5 points more wrong answers than the verbatim HLE judge (point).
- **P-R27B3.** Solve-first with the reference credits at least the verbatim HLE judge's recall minus 5 points (point).

Reported without a prediction: blind false acceptance and recall, agreement with the labels, and the number of label-correct answers
(expected to be small, so recall is noisy).

## Verdicts, spend, amendments

Point predictions are confirmed or falsified. Caps: generation USD 3 (GPT-4.1-mini, 0.4/1.6) and USD 4 (Haiku 4.5, 1/5); labels USD 6
(o3-mini, 1.1/4.4); graders USD 6 per GPT-4.1 cell (2/8) and USD 10 per Sonnet 5 cell (3/15). Any change after the first R27-B call is
recorded here as a dated amendment before its results are analyzed. 14 predictions (8 in R27-A, 6 in R27-B).

## Outcome, R27-A (recorded 2026-09-15; `papers/analysis/r27a_<cell>.json`)

149 questions per cell. Among correct answers credited blind, share rejected with the reference (differing; matching; difference with
95% interval):

| Cell | Differing | Matching | Difference |
|---|---|---|---|
| direct, GPT-4.1 | 22.4% (362) | 0.0% (139) | +22.4 [+17.7, +27.0] |
| cot, GPT-4.1 | 4.4% (387) | 0.7% (142) | +3.7 [+1.3, +6.2] |
| verify, GPT-4.1 | 2.1% (388) | 0.7% (143) | +1.4 [−0.7, +3.2] |
| solve, GPT-4.1 | 1.3% (389) | 0.0% (142) | +1.3 [+0.3, +2.5] |
| direct, Sonnet 5 | 14.1% (382) | 0.0% (142) | +14.1 [+10.1, +18.4] |
| cot, Sonnet 5 | 8.5% (388) | 0.7% (143) | +7.8 [+4.4, +11.4] |
| verify, Sonnet 5 | 9.2% (391) | 0.7% (143) | +8.5 [+4.7, +12.7] |
| solve, Sonnet 5 | 4.9% (389) | 0.0% (144) | +4.9 [+2.6, +7.5] |

- **P-R27A1:** confirmed in all eight cells (the interval excludes zero in seven; verify-first GPT-4.1 includes zero).
