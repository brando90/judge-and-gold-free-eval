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

## Outcome (recorded 2026-09-13)

Runs: 1,192 calls per grader, no errors. Opus 5: 11 referenced replies had no score (all stop reason `max_tokens`: visible reasoning
about whether a differing answer is acceptable ran past 512 tokens), treated as missing, which leaves 141 questions with all eight calls
scored; Haiku 4.5: none, 149 questions. Both at least 100, so scored. Ledger spend USD 7.62 (Opus 5) and 1.19 (Haiku 4.5).
Producers: `r20_leaderboard_analysis.py` (thresholds 7, 5, 10) and `r21_leaderboard_maxrule.py`; outputs
`papers/analysis/r21a_leaderboard_{opus,haiku}[_t5|_t10].json`, `r21a_maxrule_{opus,haiku}.json`.

| Grader | Model | List | Blind | Referenced | Max rule | Referenced − list |
|---|---|---|---|---|---|---|
| Opus 5 | Llama-3.1-8B | 70.2 | 69.5 | 56.7 | 70.2 | −13.5 [−20.6, −7.1] |
| Opus 5 | Haiku 4.5 | 94.3 | 95.7 | 73.8 | 95.7 | −20.6 [−27.7, −13.5] |
| Opus 5 | Sonnet 5 | 98.6 | 99.3 | 77.3 | 99.3 | −21.3 [−27.7, −14.9] |
| Opus 5 | Opus 5 | 100.0 | 100.0 | 92.9 | 100.0 | −7.1 [−11.3, −2.8] |
| Opus 5 | pooled (change vs list) | | +0.4 [−0.7, +1.6] | −15.6 [−19.9, −11.5] | +0.5 [−0.5, +1.8] | |
| Haiku 4.5 | Llama-3.1-8B | 69.1 | 61.7 | 62.4 | 71.8 | −6.7 [−13.4, 0.0] |
| Haiku 4.5 | Haiku 4.5 | 94.6 | 84.6 | 55.0 | 89.3 | −39.6 [−47.7, −30.9] |
| Haiku 4.5 | Sonnet 5 | 98.7 | 87.9 | 81.2 | 96.6 | −17.5 [−23.5, −11.4] |
| Haiku 4.5 | Opus 5 | 100.0 | 91.3 | 83.2 | 98.0 | −16.8 [−22.8, −11.4] |
| Haiku 4.5 | pooled (change vs list) | | −9.2 [−12.6, −6.0] | −20.1 [−24.5, −15.9] | −1.7 [−4.0, +0.5] | |

False rejections of non-matching correct answers, pooled, blind / referenced: Opus 5 0.5% / 23.4%; Haiku 4.5 9.1% / 25.2% (JSON 0.2525; one decimal as printed in the paper's tables).

- **P-R21A1:** Opus 5 **confirmed**; Haiku 4.5 **confirmed**.
- **P-R21A2:** Opus 5 **confirmed**; Haiku 4.5 **confirmed**.
- **P-R21A3:** Opus 5 **confirmed** (4 of 4 models); Haiku 4.5 **confirmed** (4 of 4; Llama-3.1-8B −6.7, interval reaching 0.0, point estimate below).
- **P-R21A4:** Opus 5 **confirmed**; Haiku 4.5 **confirmed** (max-rule intervals do not overlap the referenced intervals).
- **P-R21A5:** **confirmed** (Opus 5 blind +0.4).

Reported without a prediction: the answer lists rank Opus 5 > Sonnet 5 > Haiku 4.5 > Llama-3.1-8B. Opus 5 keeps that order blind and with
the reference. Haiku 4.5 keeps it blind but, with the reference, puts Llama-3.1-8B (62.4) above Haiku 4.5 (55.0), as Sonnet 5 did by one
question. At threshold 5 the pooled referenced shortfall is −17.6 (Sonnet 5; post hoc), and see the JSON files for Opus 5 and Haiku 4.5.
At threshold 10 blind grading also collapses for every grader, because blind 10s are rare.
