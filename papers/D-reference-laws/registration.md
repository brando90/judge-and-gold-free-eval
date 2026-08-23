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

## Addendum (2026-08-23): registered follow-up, reference-rotation rerun

Registered AFTER the primary analysis (post-data for the main experiment, pre-data for the
rerun). Motivation: the P-T2 margin rests on only 4 items because, of the 10 items whose
sampled pool contains a valid reference-matching sample, 6 have zero other-valid samples
(all 64 samples give the same answer), a property of the generator's answer distribution.

- **Design:** re-judge the SAME frozen 64-sample pools with permuted reference choices:
  for each item, rotate `ref_answer` over the other members of the enumerated valid set
  (seeded permutation, fixed before any re-judging), so different valid answers play the
  reference role. Generation and oracle scoring are unchanged and frozen.
- **Purpose:** repower the P-T2 margin cell (more items where valid matching and valid
  non-matching samples coexist under some rotation) and test that the anchoring premium
  follows the shown reference, not a particular answer.
- **Prediction (P-T2r):** under rotation the referenced margin remains positive and tracks
  whichever answer is designated as the reference; blind margins remain near zero.

## Correction note (2026-08-23): rotation deviated from the registered assignment mechanism

The implemented rotation deviated from the seeded permutation registered in the addendum above.
Instead of a blind seeded permutation over each item's valid set, the rotated `ref_answer` was
constructed pool-aware: for each item it prefers a different valid answer that also appears among
the pool's oracle-valid samples, to maximize paired coverage (rotated reference in pool on 40/51
items versus 10/51 for the original build-time reference). This deviation is disclosed in the
paper (Setup and RQ2). The within-sample paired contrast is unaffected by the assignment
mechanism, since the samples are frozen and only the shown reference varies; the cross-sectional
rotated margins, however, over-represent answers the generator actually produced.

## Status

- [x] Task file built (51 items) and committed.
- [x] Scripts patched (`bon_generate.py`, `bon_oracle.py`, `bon_judge.py`, `bon_rubrics.py`)
  and committed before any data generation.
- [ ] Generation + oracle + 16-run judge grid (`scripts/bon_chain_ties.sh`, 1 GPU) - blocked on
  cluster access at time of registration.
- [ ] Analysis (`bon_analysis.py` on the ties pool) + P-T2 margin analysis.
