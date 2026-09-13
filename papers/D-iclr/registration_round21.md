# Round 21 registration: two more graders for the benchmark study (R21-A)

Registered 2026-09-13, before any R21 call. Committed together with the producer changes named below.

## Context disclosed before any R21 call

All R20 results are known (`registration_round20.md`). In particular, with Claude Sonnet 5 as the grader on the 149-question pool
`runs/r20/mace_gen/pool.jsonl`: referenced minus answer-list accuracy −13.4, −39.6, −21.5 and −14.8 points (Llama-3.1-8B, Haiku 4.5,
Sonnet 5, Opus 5), pooled −22.3 [−27.0, −18.0]; blind minus list −0.7 to −2.7 points; false rejections of non-matching correct answers
1.0% blind and 24.2% referenced; under the max rule (post hoc, `r20g_frontier_safeguards.json`) max minus list −0.7 to −2.0 points, pooled
−1.0. A post hoc analysis (`r20e_benchmark_open_judges.json`) found that Qwen2.5-7B and phi-4 as graders of Llama-3.1-8B's 64 samples per
question under-count accuracy both blind (−20.8 and −15.4 points) and with the reference (−46.7 and −47.5). The round-20 review asked
whether the Sonnet 5 result depends on one grader that also grades its own answers.

## R21-A: Claude Opus 5 and Claude Haiku 4.5 as graders

- Pool: `runs/r20/mace_gen/pool.jsonl` unchanged (149 questions, one answer each from Llama-3.1-8B-Instruct, Claude Haiku 4.5, Claude
  Sonnet 5 and Claude Opus 5, with answer-list labels).
- Calls: `scripts/sonnet_api_pool.py` with the R8-A prompts, thinking disabled, 512 tokens, blind and referenced:
  - Opus 5: `--model claude-opus-5 --price-in 15 --price-out 75 --cap-usd 25`, output `runs/r21/leaderboard_opus_api/pool.jsonl`;
  - Haiku 4.5: `--model claude-haiku-4-5-20251001 --price-in 1 --price-out 5 --cap-usd 10`, output `runs/r21/leaderboard_haiku_api/pool.jsonl`.
- Producers (committed with this file):
  - `papers/analysis/r20_leaderboard_analysis.py --scores <file> --out <json>`: unchanged except a `--threshold` argument whose default (7)
    reproduces R20-C;
  - `papers/analysis/r21_leaderboard_maxrule.py --scores <file> --out <json>` (max rule, threshold 7).
- Grading: a score of 7 or above counts as correct.

### Predictions

For each grader G in {Opus 5, Haiku 4.5}:

- **P-R21A1 (G).** Pooled over generators, referenced accuracy is below answer-list accuracy (question-level interval excludes zero).
- **P-R21A2 (G).** Pooled over generators, the share of non-matching correct answers scored 3 or below is higher with the reference than
  blind (point estimate).
- **P-R21A3 (G).** For every generator with at least 10 correct answers that differ from the reference, referenced accuracy is below
  answer-list accuracy (point estimates).
- **P-R21A4 (G).** Under the max rule, pooled accuracy is within 5 points of answer-list accuracy (point estimate), and its interval
  lies above that of referenced accuracy minus list (the two intervals do not overlap).

For Opus 5 only:

- **P-R21A5.** Blind, pooled accuracy is within 5 points of answer-list accuracy (point estimate).

Reported without a prediction: generator rankings under each grader; the same readouts at thresholds 5 and 10 (`--threshold 5`,
`--threshold 10`); Haiku 4.5's blind accuracy against the list; each grader's scores on its own answers.

## Verdicts and completion

Confirmed when the interval excludes zero in the predicted direction (or a point prediction holds); falsified when it excludes zero in the
opposite direction (or a point prediction fails); not confirmed otherwise. Unparseable or errored calls are missing. A grader is scored if
at least 100 questions have all eight calls scored.

## Outcome

To be recorded here after the runs.
