# Round 24 registration: standard benchmark graders, a non-Anthropic grader, and fixes (R24-A to R24-D)

Registered 2026-09-14, before any R24 call. Committed together with the harness `experiments/tfa-vs-judge/scripts/r24_grader_pool.py`,
the seeding script `scripts/r24_seed.py`, the vendored grader sources in `scripts/vendor/`, the run drivers `scripts/r24_run_*.sh`, and
the producer `papers/analysis/r24_analysis.py`.

## Context disclosed before any R24 call

All results through R23 are known (`papers/D-iclr/registration_round19.md` to `registration_round23.md`; paper v1, tag
`paper-d-iclr-v1`). On the 149-question benchmark pool (`runs/r20/mace_gen/pool.jsonl`: one answer each from Llama-3.1-8B-Instruct,
Claude Haiku 4.5, Sonnet 5 and Opus 5; 540 of 596 answers correct by the answer list, 396 of them differing from the reference), the
paper's score-only rubric with a reference puts pooled accuracy 22.3 (Sonnet 5), 15.6 (Opus 5) and 20.1 (Haiku 4.5) points below the
answer list; blind, Sonnet 5 and Opus 5 are within 2 points. A second reference draw moves credit for answers whose match changes by
23 to 38 points. On the R8-A MACE subsample (`runs/r8/sonnet_mace.jsonl`, 40 tasks, 16 candidates each), grading AUROC of correct
answers that differ from the reference against wrong answers falls by 0.153 (Sonnet 5) and 0.165 (Opus 5), with false rejections
rising by 35.6 and 36.3 points; Sonnet 5 with adaptive thinking: −0.090 and +14.9; Sonnet 5 with the full-credit sentence: −0.065 and
+18.1. GPT-4.1 was run only on the constructed pools, where its grading AUROC falls by at most 0.04.

No R24 judge call has been made. The harness was run only with `--dry-run`, which prints prompts without calling an API. The
producer was exercised on existing score files, where it reproduces the numbers above (R20-C −22.3, R22-B stop-matching credit shift
+38.2 pp, R8-A −0.153 and +35.6, R19-B −0.090 and +14.9, R20-B −0.065 and +18.1), and on synthetic copies of those files to test the
new code paths; the synthetic outputs are discarded. The OpenAI models were listed through the API to confirm availability; no
completion was requested. The verbatim grader prompts were read before this registration: the SimpleQA grader counts an answer as
INCORRECT when "a factual statement in the answer contradicts the gold target", and the HLE/BrowseComp judge asks whether a response is
correct "based on the precise and unambiguous [correct_answer]" and instructs "do not argue for any answer different than
[correct_answer], focus only on whether the answers match".

## Shared settings

- Harness: `scripts/r24_grader_pool.py` (settings in its header). Vendored sources: `openai/simple-evals` at 5e623c2
  (`simpleqa_eval.py`, `browsecomp_eval.py`, `sampler/chat_completion_sampler.py`) and 496e457 (`simple_evals.py`, which sets the
  grading sampler to `gpt-4.1-2025-04-14`, system message "You are a helpful assistant.", max_tokens 2048, sampler default
  temperature 0.5); `centerforaisafety/hle` at a590489 (`hle_eval/run_judge_results.py`, judge `o3-mini-2025-01-31`, structured
  output, max_completion_tokens 4096).
- Conditions: `ref` = the pool's reference (first draw); `reflist` = the full MACE answer list (`runs/mace_tasks.jsonl`
  `valid_answers`, sorted), stated as "Any one of the following is a complete correct answer: A; B; ..." in the binary templates and
  as "Reference answers (trusted; any one of them is a complete correct answer):" with a matching rubric sentence in the rubric
  template; `noref` = blind rubric.
- Correct: score 7 or above (binary templates store 10 or 0; GPT-4.1 with the rubric uses the logprob-expected score). Unparseable
  replies and API errors are missing. For binary templates the primary parse is markdown-robust (first standalone A/B/C; `correct:
  yes|no` ignoring `*`, `_`, backticks, case); the official parse with its default (C or "no") is stored and reported as a
  descriptive secondary readout.
- Spend caps are enforced by the harness ledger with the listed prices (USD per million input/output tokens).

## R24-A: standard benchmark graders, one reference against the full answer list

Pool `runs/r20/mace_gen/pool.jsonl`, conditions `ref,reflist`. Five cells:

| Cell | Template | Judge | Settings | Output | Cap |
|---|---|---|---|---|---|
| s41 | SimpleQA grader | gpt-4.1-2025-04-14 (SimpleQA's configured grader) | as simple-evals | `runs/r24/std_s41/pool.jsonl` | 8 (2/8) |
| h41 | HLE/BrowseComp judge | gpt-4.1-2025-04-14 (BrowseComp's configured grader) | as simple-evals | `runs/r24/std_h41/pool.jsonl` | 8 (2/8) |
| h03 | HLE/BrowseComp judge | o3-mini-2025-01-31 (HLE's judge) | as HLE | `runs/r24/std_h03/pool.jsonl` | 8 (1.1/4.4) |
| sS5 | SimpleQA grader | claude-sonnet-5 | thinking disabled, max_tokens 512 | `runs/r24/std_sS5/pool.jsonl` | 6 (3/15) |
| hS5 | HLE/BrowseComp judge | claude-sonnet-5 | thinking disabled, max_tokens 1024 | `runs/r24/std_hS5/pool.jsonl` | 6 (3/15) |

Producer: `r24_analysis.py --part a --cell <cell> --scores <file> --out papers/analysis/r24a_<cell>.json`, on questions with all four
answers scored under both conditions (question bootstrap, 2,000 resamples, seed 0, paired). A cell is scored if at least 100 questions
are complete.

Predictions, for each cell:
- **P-R24A1.** Pooled accuracy with one reference is below answer-list accuracy (interval excludes zero).
- **P-R24A2.** Pooled accuracy with the full answer list is within 5 points of answer-list accuracy (point estimate).
- **P-R24A3.** Among correct answers that differ from the reference, the share credited is at least 20 points higher with the full list
  than with one reference (point estimate).
- **P-R24A4.** Among wrong answers, the share credited is at most 3 points higher with the full list than with one reference (point
  estimate).

Reported without a prediction: per-model accuracies and gaps, credit for matching correct answers, official-parse readouts.

## R24-B: a non-Anthropic grader with the paper's rubric

GPT-4.1 (`gpt-4.1-2025-04-14`, rubric template, logprob-expected score) grades the benchmark pool blind and with the first reference
(`--conds noref,ref`, output `runs/r24/leaderboard_gpt41_api/pool.jsonl`, cap 3 at 2/8). Then `r24_seed.py --part b` copies its blind
rows to `runs/r24/redraw_gpt41_api/pool.jsonl`, and GPT-4.1 grades `runs/r22/redraw_pool.jsonl` with the second reference
(`--conds ref`, cap 2). Producer: `r24_analysis.py --part b --leaderboard ... --redraw ... --out papers/analysis/r24b_gpt41.json`.
Scored if at least 100 complete questions (each readout).

- **P-R24B1.** Pooled referenced accuracy is below answer-list accuracy (interval excludes zero).
- **P-R24B2.** Pooled blind accuracy is within 5 points of answer-list accuracy (point estimate).
- **P-R24B3.** Correct answers that match the first reference but not the second are credited more under the first draw (point).
- **P-R24B4.** Correct answers that match the second reference but not the first are credited more under the second draw (point).

## R24-C: the answer key restores grading

`r24_seed.py --part c` copies the existing blind and referenced calls of Sonnet 5 (R8-A) and Opus 5 (R19-A) on
`runs/r8/sonnet_mace.jsonl`; the harness adds `reflist` calls with the same settings (thinking disabled, max_tokens 512): Sonnet 5
(`runs/r24/reflist_sonnet_api/mace.jsonl`, cap 3 at 3/15), Opus 5 (`runs/r24/reflist_opus_api/mace.jsonl`, cap 8 at 15/75). GPT-4.1
grades the subsample under `noref,ref,reflist` (`runs/r24/reflist_gpt41_api/mace.jsonl`, cap 2). Producer: `r24_analysis.py --part c
--judge <judge> --scores <file> --out papers/analysis/r24c_<judge>.json` (candidates scored in all three conditions; tasks with at least
one correct answer that differs from the reference and one wrong answer; task bootstrap, 1,000 resamples, seed 0). Scored if at least
20 tasks.

For each judge in {Sonnet 5, Opus 5, GPT-4.1}:
- **P-R24C1.** Grading AUROC with the full list minus blind is at least −0.03 (point estimate).
- **P-R24C2.** The rise in false rejections with the full list over blind is at most 5 points (point estimate).
- **P-R24C3.** Grading AUROC with the full list is above AUROC with one reference (interval excludes zero).

## R24-D: a prompt-only fix when the set cannot be listed

`r24_seed.py --part d` copies the blind calls of Sonnet 5 with adaptive thinking (R19-B). The harness adds referenced calls with
adaptive thinking and the full-credit sentence (`--thinking adaptive --max-tokens 8000 --instruction anyvalid --conds ref`, output
`runs/r24/think_inst_sonnet_api/mace.jsonl`, cap 8 at 3/15). Producer: `r24_analysis.py --part d --combined <that file> --thinking
runs/r19/sonnet_think_api/mace.jsonl --sentence runs/r20/sonnet_inst_api/mace.jsonl --out papers/analysis/r24d_think_sentence.json`.
Scored if at least 20 tasks.

- **P-R24D1.** The rise in false rejections with thinking and the sentence is below both thinking alone and the sentence alone (point).
- **P-R24D2.** The change in grading AUROC with thinking and the sentence is above both (point).
- **P-R24D3.** With thinking and the sentence, false rejections still rise (interval excludes zero).

## Verdicts, amendments and completion

Interval predictions are confirmed when the 95% interval excludes zero in the predicted direction, not confirmed when it includes
zero, and falsified when it excludes zero in the opposite direction; point predictions are confirmed or falsified. A cell or experiment
below its completeness threshold is not scored. Any change to settings after the first R24 call is recorded here as a dated amendment
before its results are analyzed. Total caps: OpenAI USD 31, Anthropic USD 31.

## Amendment 1 (2026-09-14, during the runs, before any R24 analysis)

Cell sS5 (SimpleQA grader, Claude Sonnet 5): spend cap raised from USD 6 to USD 10, and the Anthropic total from USD 31 to USD 35.
Its ledger showed USD 2.64 after 401 of 1,192 calls (projection about USD 7.8); the registration underestimated the length of the
SimpleQA few-shot prompt. If the cap stops the run, the same command is re-run with `--cap-usd 10`; the harness resumes and skips
completed calls. Nothing else changes. Before this amendment we had looked only at run logs, spend ledgers and a parse check of the
first rows of each output file (counts of parsed grades by condition, error counts); no producer was run on R24 data.

## Outcome (recorded 2026-09-14; `papers/analysis/r24a_{s41,h41,h03,sS5,hS5}.json`, `r24b_gpt41.json`, `r24c_{sonnet,opus,gpt41}.json`, `r24d_think_sentence.json`)

Runs: every call completed with no API error and no unparseable reply (1,192 per R24-A cell; 1,192 + 1,192 for R24-B; 640
`reflist` calls each for Sonnet 5 and Opus 5 and 1,920 calls for GPT-4.1 in R24-C; 640 for R24-D). The markdown-robust parse and the
official parse agree on every binary grade. Spend: OpenAI USD 7.76 (s41 3.45, h41 1.37, h03 1.83, R24-B 0.58, R24-C 0.53);
Anthropic USD 16.18 (sS5 7.80 under Amendment 1, hS5 4.14, R24-C Sonnet 5 0.50 and Opus 5 2.47, R24-D 1.27). All experiments
complete: 149 questions in every R24-A cell and both R24-B readouts, 40 tasks in R24-C and R24-D. Answer-list accuracy of the pool:
90.6%.

| Cell | One reference minus list (pts) | Full list minus list (pts) | Differing correct answers credited: one ref, full list | Wrong answers credited (of 56): one ref, full list |
|---|---|---|---|---|
| s41 SimpleQA grader, GPT-4.1 | −30.4 [−35.4, −25.3] | +0.3 [−0.7, +1.5] | 53.0%, 99.2% | 8.9%, 8.9% |
| h41 BrowseComp judge, GPT-4.1 | −66.8 [−71.8, −61.7] | −0.2 [−0.8, +0.5] | 0.0%, 99.2% | 0.0%, 3.6% |
| h03 HLE judge, o3-mini | −66.6 [−71.8, −61.6] | 0.0 [−0.8, +0.8] | 0.0%, 99.2% | 0.0%, 5.4% |
| sS5 SimpleQA grader, Sonnet 5 | −34.4 [−39.9, −29.2] | +0.5 [−0.3, +1.5] | 46.7%, 99.5% | 10.7%, 8.9% |
| hS5 HLE judge, Sonnet 5 | −64.9 [−70.3, −59.9] | +0.2 [−0.3, +0.7] | 2.3%, 99.8% | 1.8%, 3.6% |

- **P-R24A1:** confirmed in all five cells. **P-R24A2:** confirmed in all five. **P-R24A3:** confirmed in all five.
- **P-R24A4:** s41 **confirmed** (0.0 pp); sS5 **confirmed** (−1.8); hS5 **confirmed** (+1.8); h41 **falsified** (+3.6, 2 of 56 wrong
  answers); h03 **falsified** (+5.4, 3 of 56).
- Descriptive, post hoc: the wrong answers credited only with the full list are "The Democratic Republic of Congo" (list entry
  "Democratic Republic of the Congo", which string containment misses; credited in four cells), "Territory of New Guinea" (list
  entry "Papua New Guinea"; h41, h03), "Sudan" (list entry "South Sudan"; s41) and "Wales" (list entry "United Kingdom"; h03).

R24-B (GPT-4.1, the paper's rubric): referenced minus list −9.6 [−12.9, −6.4], blind minus list −2.5 [−4.7, −0.3]; second draw minus
list −7.0 [−10.1, −4.0]; answers that stop matching are credited 100% under the first draw and 87.5% under the second (144 answers);
answers that start matching 80.5% and 99.4% (174).
- **P-R24B1 confirmed; P-R24B2 confirmed; P-R24B3 confirmed (+12.5 pp); P-R24B4 confirmed (+19.0 pp).**

R24-C (40 tasks; grading AUROC blind, one reference, full list; changes against blind):

| Judge | AUROC blind / one ref / full list | One ref minus blind | Full list minus blind | Full list minus one ref | False-rejection rise: one ref, full list (pp) |
|---|---|---|---|---|---|
| Sonnet 5 | 0.938 / 0.785 / 0.970 | −0.153 [−0.219, −0.097] | +0.032 [+0.008, +0.060] | +0.185 [+0.125, +0.258] | +35.6, −2.2 [−8.0, +4.9] |
| Opus 5 | 0.936 / 0.771 / 0.969 | −0.165 [−0.223, −0.110] | +0.033 [−0.000, +0.084] | +0.198 [+0.145, +0.253] | +36.3, −6.3 [−12.8, −1.1] |
| GPT-4.1 | 0.935 / 0.872 / 0.992 | −0.063 [−0.133, +0.004] | +0.057 [+0.013, +0.121] | +0.120 [+0.055, +0.190] | +15.6, −2.2 [−4.6, −0.5] |

- **P-R24C1, P-R24C2, P-R24C3:** confirmed for all three judges.

R24-D (Sonnet 5, 40 tasks): with adaptive thinking and the full-credit sentence, the rise in false rejections is −0.2 pp [−7.2, +4.6]
and the grading AUROC change −0.024 [−0.062, +0.006], against +14.9 and −0.090 with thinking alone and +18.1 and −0.065 with the
sentence alone.
- **P-R24D1 confirmed; P-R24D2 confirmed; P-R24D3 not confirmed** (the combination leaves no measurable rise in false rejections).

Totals: 36 predictions; 33 confirmed, 1 not confirmed, 2 falsified.
