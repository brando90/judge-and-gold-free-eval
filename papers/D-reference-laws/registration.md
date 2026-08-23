# Registration: best-of-64 selection pressure on a multi-valid-answer task (2026-08-22)

Committed BEFORE any generation, oracle scoring, or judge scoring for this experiment.

## Motivation

Two existing results have never been tested together. Statically, on multi-valid-answer
comparisons (RewardBench-2 Ties), showing a judge ANY reference lowers verdict accuracy by 7-8
points (p<=.0005) via anchoring against valid alternatives. Dynamically, on single-answer domains
(math, code), a trusted reference collapses best-of-64 hacking. This experiment runs the dynamic
protocol on the multi-valid task.

## Design

- Tasks: `runs/bon_ties_tasks.jsonl` (51 RewardBench-2 Ties items with >=2 enumerated valid
  answers). Each task stores the full valid set (the oracle) and one seeded-random valid answer
  (`ref_answer`) shown in the judge's ref condition, fixed at build time.
- Generation: Qwen2.5-7B-Instruct, 64 samples/item, temperature 1.0 (identical to Phase 0).
- Oracle: boxed answer (fallback: whole reply), loose-normalized membership in the valid set.
- Item filter: pool pass rate in [0.2, 0.8], as pre-registered in Phase 0.
- Judges: Qwen 1.5B/3B/7B/14B x {noref, ref} x rubric paraphrases {a, b} (RUBRIC_TIES in
  `scripts/bon_rubrics.py`). Selection on a, reporting on b, as in Phase 0.
- Estimands: excess hack gap and oracle regret, identical pre-registered estimators
  (`scripts/bon_analysis.py`, unchanged).

## Registered predictions

- **P-T1 (primary).** The reference does NOT reduce oracle regret on multi-valid items: the
  paired within-size contrast regret(noref) - regret(ref) is <= 0 (directionally, the reference
  HURTS selection quality), in contrast to math (where the same contrast was strongly positive:
  0.448->0.010 at 1.5B) and code at 3B+.
- **P-T2 (mechanism).** Among oracle-valid samples, referenced judges score samples matching the
  shown `ref_answer` higher than equally-valid non-matching samples (positive within-item margin);
  no-reference judges show a near-zero margin. This is the anchoring channel, measured directly.
- **P-T3.** The excess hack gap under ref is not reduced relative to noref (no certification
  benefit from the reference on this task class).

Falsification of P-T1 (reference still helps under pressure despite hurting static verdict
accuracy) would be reported as-is; it would mean selection pressure and static grading disagree,
which is itself informative for the certification story.

## Status

- [x] Task file built (51 items) and committed.
- [x] Scripts patched (`bon_generate.py`, `bon_oracle.py`, `bon_judge.py`, `bon_rubrics.py`)
  and committed before any data generation.
- [ ] Generation + oracle + 16-run judge grid (`scripts/bon_chain_ties.sh`, 1 GPU) - blocked on
  cluster access at time of registration.
- [ ] Analysis (`bon_analysis.py` on the ties pool) + P-T2 margin analysis.
