# Round 26 registration: instruction against reasoning, false acceptance, and open RL verifiers (R26-A to R26-C)

Registered 2026-09-14, before any R26 judge or verifier call. Committed together with `experiments/tfa-vs-judge/scripts/r26_judges.py`,
`scripts/r26_verifiers.py`, `scripts/r26_run_api.sh` and the producer `papers/analysis/r26_analysis.py`.

## Context disclosed before any R26 call

All results through R25 are known (`registration_round24.md`, `registration_round25.md`, outcomes recorded). On the 149-question
benchmark pool (596 answers, 90.6% correct by the answer lists, 56 wrong), one reference puts pooled accuracy 30 to 34 points below
the lists under the verbatim SimpleQA grader and 65 to 67 points under the BrowseComp/HLE judge (GPT-4.1, o3-mini, Sonnet 5), 10 to 22
points under the paper's score rubric, and 0.5 to 6 points under chain-of-thought, verify-first and solve-first prompts (GPT-4.1:
cot −3.0, verify −1.5, solve −0.5; Sonnet 5: −6.0, −6.2, −3.4), which credit 5% to 13% of wrong answers with the reference. On the R8-A
MACE subsample, the full answer list raises grading AUROC above blind for Sonnet 5, Opus 5 and GPT-4.1. An area-chair review of the v2
draft (`reviews/v2_ac_review.md`) asked whether the instruction or reasoning sets the size of the effect, whether the no-list prompts
accept more wrong answers where many answers are wrong, and whether surveyed RL verifiers under-credit the same answers. The open
verifier weights were being downloaded (no generation) when this registration was committed; no R26 judge or verifier call has been made, and the harnesses were run
only with `--dry-run`.

## R26-A: instruction against reasoning on the benchmark pool

`scripts/r26_judges.py` (settings in its header; OpenAI temperature 0 and no system message, Anthropic thinking disabled, 1,024 tokens,
for every template) on `runs/r20/mace_gen/pool.jsonl`, with GPT-4.1 (`gpt-4.1-2025-04-14`) and Sonnet 5 (`claude-sonnet-5`):
- `direct` (blind and reference): "Is the response a correct answer to the question?", no reasoning requested.
- `hle` (reference): the HLE judge prompt verbatim.
- `hle_edit` (reference): the HLE judge prompt with ", do not argue for any answer different than [correct_answer], focus only on
  whether the answers match" removed and "A response that gives a different answer that is also correct for the question is correct."
  added after the `correct:` criterion.

Outputs `runs/r26/bench_<template>_<gpt41|sonnet>/scores.jsonl`. Producer `r26_analysis.py --part a --judge <j> --direct ... --hle ...
--hle-edit ... --cot papers/analysis/r25_cot_<j>.json --out papers/analysis/r26a_<j>.json`; questions with every needed call scored;
scored if at least 100.

For each judge:
- **P-R26A1.** Direct prompt, reference: pooled accuracy below the answer lists (interval excludes zero).
- **P-R26A2.** Direct prompt, blind: within 5 points of the lists (point).
- **P-R26A3.** Direct prompt, reference: shortfall within 5 points of the same judge's R25 chain-of-thought shortfall (point), i.e. the
  instruction rather than written reasoning sets the size.
- **P-R26A4.** The edited HLE judge's shortfall is at least 30 points smaller than the verbatim HLE judge's under the same settings (point).
- **P-R26A5.** The edited HLE judge is within 10 points of the lists (point).

## R26-B: grading and false acceptance on the MACE subsample

The same harness on `runs/r8/sonnet_mace.jsonl` (40 tasks, 16 candidates each, including wrong answers), GPT-4.1 and Sonnet 5:
`direct`, `verify`, `solve` (blind and reference); `hle`, `hle_edit` (reference). Outputs `runs/r26/sub_<template>_<judge>/scores.jsonl`.
Producer `--part b` (candidates scored under every template and condition; tasks with at least one correct answer that differs from the
reference and one wrong answer; task bootstrap, 1,000 resamples, seed 0); scored if at least 20 tasks.

For each judge:
- **P-R26B1** (each of direct, verify, solve). Grading AUROC with the reference minus blind is at least −0.05 (point).
- **P-R26B2** (each of direct, verify, solve). False acceptance (share of wrong answers credited) with the reference minus blind is at
  most +5 points (point).
- **P-R26B3.** Grading AUROC of the edited HLE judge is above the verbatim HLE judge's (interval excludes zero).

## R26-C: open RL-reward verifiers

`scripts/r26_verifiers.py` runs locally (Apple MPS, float16, greedy) on the benchmark pool with one reference and with the full
answer list ("Any one of the following is a complete correct answer: ..."): `TIGER-Lab/general-verifier` with General-Reasoner's
template (reward if "Final Decision: Yes" appears; max 512 new tokens) and `opencompass/CompassVerifier-3B` with `CV_PROMPT` through its
chat template (first A/B/C; A correct; max 32 new tokens). Outputs `runs/r26/verifier_<general|compass>/scores.jsonl`. Producer `--part c`;
scored if at least 100 complete questions.

For each verifier:
- **P-R26C1.** One reference: pooled accuracy below the answer lists (interval excludes zero).
- **P-R26C2.** Full list: within 5 points of the lists (point).
- **P-R26C3.** Credit for differing correct answers at least 20 points higher with the full list (point).

## Verdicts, spend, amendments

Interval predictions are confirmed when the 95% interval excludes zero in the predicted direction, not confirmed when it includes
zero, and falsified when it excludes zero in the opposite direction; point predictions are confirmed or falsified. Caps: OpenAI
USD 15, Anthropic USD 30 (ledger prices GPT-4.1 2/8, Sonnet 5 3/15 per million tokens). Any change after the first R26 call is recorded
here as a dated amendment before its results are analyzed. 30 predictions.

## Amendment 1 (2026-09-14, before any CompassVerifier generation and before any R26 analysis)

`opencompass/CompassVerifier-3B` failed to load because its configuration requests FlashAttention 2, which is not available on
Apple MPS; no generation was produced. `scripts/r26_verifiers.py` now loads both verifiers with `attn_implementation="sdpa"` (PyTorch
scaled dot-product attention). The General-Reasoner verifier run, already in progress, is unaffected (its configuration does not
request FlashAttention). Nothing else changes.
