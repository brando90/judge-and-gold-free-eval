# Round 25 registration: three more judge types on the benchmark pool (R25-A)

Registered 2026-09-14, before any R25 call. Committed together with the harness `experiments/tfa-vs-judge/scripts/r25_judge_types.py`,
the driver `scripts/r25_run.sh` and the producer `papers/analysis/r25_analysis.py`.

## Context disclosed before any R25 call

All results through R24 are known (`registration_round24.md`, outcome recorded). On the 149-question benchmark pool
(`runs/r20/mace_gen/pool.jsonl`, 596 answers, 90.6% correct by the answer lists), one reference puts pooled accuracy 30 to 34 points
below the lists under the verbatim SimpleQA grader and 65 to 67 points under the BrowseComp/HLE judge (GPT-4.1, o3-mini, Sonnet 5),
and 10 to 22 points under the paper's score-only rubric (Sonnet 5, Opus 5, Haiku 4.5, GPT-4.1), with blind grading within 3 points for
Sonnet 5, Opus 5 and GPT-4.1. An advisor meeting asked whether the effect holds across judge types (direct scoring, chain of thought,
structured verification). The judge types already tested are score-only, explanation-first (MT-Bench template, Qwen3 with thinking
off), thinking modes, a few-shot classifier (SimpleQA) and a structured extraction judge (HLE). No R25 call has been made; the harness
was run only with `--dry-run`.

## R25-A: chain-of-thought, verify-first and solve-first judges

Harness `scripts/r25_judge_types.py` (prompts in its source; none says whether a question can have several correct answers):
- `cot`: reason step by step about whether the response is correct (using the reference answer, when given), then "correct: yes|no".
- `verify`: structured verification. (1) Verify the response's final answer on your own; (2) compare it with the reference answer
  (reference condition only); (3) decide.
- `solve`: answer the question yourself first, then grade the response using your own answer (and the reference answer, when given).

Judges: `gpt-4.1-2025-04-14` (temperature 0, max_tokens 1024; cap USD 6 per template at 2/8 per million tokens) and `claude-sonnet-5`
(thinking disabled, max_tokens 1024; cap USD 9 per template at 3/15). Conditions `noref,ref` on the benchmark pool; outputs
`runs/r25/<template>_<gpt41|sonnet>/pool.jsonl`. Grade: the last "correct: yes|no" in the reply (markdown and case ignored); a reply
without one is missing. Total caps: OpenAI USD 18, Anthropic USD 27.

Producer: `r25_analysis.py --cell <template>_<judge> --scores <file> --out papers/analysis/r25_<cell>.json`, on questions with all four
answers graded under both conditions (question bootstrap, 2,000 resamples, seed 0). A cell is scored if at least 100 questions are
complete.

Predictions, for each of the six cells:
- **P-R25A1.** Pooled accuracy with the reference is below answer-list accuracy (interval excludes zero).
- **P-R25A2.** Pooled blind accuracy is within 5 points of answer-list accuracy (point estimate).
- **P-R25A3.** Among correct answers that differ from the reference, the share credited with the reference is at least 10 points
  lower than blind (point estimate).

Reported without a prediction: per-model accuracies; credit for matching correct answers and for wrong answers.

## Verdicts, amendments and completion

Interval predictions are confirmed when the 95% interval excludes zero in the predicted direction, not confirmed when it includes
zero, and falsified when it excludes zero in the opposite direction; point predictions are confirmed or falsified. Any change to
settings after the first R25 call is recorded here as a dated amendment before its results are analyzed.

## Outcome (recorded 2026-09-14; `papers/analysis/r25_{cot,verify,solve}_{gpt41,sonnet}.json`)

Runs: 1,192 calls per cell, no API error, no reply without a grade, no reply cut off. No amendment. Spend: OpenAI USD 4.57 (cot 1.64,
verify 1.78, solve 1.14); Anthropic USD 18.69 (cot 5.29, verify 6.48, solve 6.92). All cells complete (149 questions).

| Cell | Blind minus list (pts) | Reference minus list (pts) | Reference minus blind (pts) | Differing correct credited: blind, reference | Wrong credited: blind, reference |
|---|---|---|---|---|---|
| cot, GPT-4.1 | −0.8 [−2.4, +0.7] | −3.0 [−4.7, −1.3] | −2.2 [−4.0, −0.3] | 97.7%, 94.7% | 10.7%, 8.9% |
| verify, GPT-4.1 | −0.3 [−1.8, +1.2] | −1.5 [−3.0, +0.0] | −1.2 [−2.4, +0.0] | 98.0%, 96.7% | 12.5%, 10.7% |
| solve, GPT-4.1 | −0.3 [−1.7, +1.0] | −0.5 [−2.0, +1.2] | −0.2 [−1.5, +1.0] | 98.2%, 97.5% | 12.5%, 12.5% |
| cot, Sonnet 5 | −0.5 [−1.8, +1.0] | −6.0 [−8.7, −3.5] | −5.5 [−7.9, −3.4] | 98.0%, 90.1% | 10.7%, 7.1% |
| verify, Sonnet 5 | −0.2 [−1.3, +1.0] | −6.2 [−8.9, −3.7] | −6.0 [−8.7, −3.5] | 98.7%, 90.1% | 8.9%, 5.4% |
| solve, Sonnet 5 | +0.0 [−1.3, +1.3] | −3.4 [−5.7, −1.2] | −3.4 [−5.2, −1.8] | 98.2%, 93.4% | 12.5%, 10.7% |

- **P-R25A1:** cot GPT-4.1 **confirmed**; verify GPT-4.1 **not confirmed**; solve GPT-4.1 **not confirmed**; cot, verify and solve
  Sonnet 5 **confirmed**.
- **P-R25A2:** **confirmed** in all six cells.
- **P-R25A3:** **falsified** in all six cells (the drop in credit for differing correct answers is 0.7 to 8.6 points).

Totals: 18 predictions; 10 confirmed, 2 not confirmed, 6 falsified. Judges prompted to reason about correctness before deciding show a
shortfall one to two orders of magnitude smaller than the benchmark graders of R24-A, and it remains measurable for Sonnet 5.
