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

## Outcome note (2026-08-23): synthetic-multiplicity grid, P-S1 through P-S5

The synthetic-multiplicity design registered at commit `c505c23` (60 tasks with exactly k valid
answers, k in {1,2,4,8,16}, 12 per stratum; prime-window and divisor families with enumerable
oracles; judges Qwen 1.5B/3B/7B/14B, Llama-3.1-8B, phi-4; conditions noref/ref/refinst/multiref
with two rubric replicates; Qwen-7B generator pool plus a Llama-3.1-8B generator pool judged by
Qwen-7B) has now run. All numbers: `papers/analysis/synthk_results.json`, produced by the
pre-committed `papers/analysis/synthk_analysis.py`. Scored outcomes:

- **P-S1 (dose-response; ref helps at k=1): CONFIRMED on the gap leg, FALSIFIED on the
  margin-trend leg.** At k=1 the reference reduces the excess gap for all six judges
  (Qwen-7B: +0.10 [+0.01,+0.20] ref vs +0.50 [+0.35,+0.67] blind; phi-4: +0.02 vs +0.56).
  At k=16 the referenced gap exceeds blind for all six judges (Qwen-7B: ref
  +0.91/+1.39/+1.71/+1.64 at k=2/4/8/16 vs blind +0.59/+0.32/+0.72/+0.33; phi-4: +1.42 vs
  +0.77 at k=16). The sub-prediction that margins grow with k is falsified: margins saturate
  immediately (Qwen-7B ref margins +4.4 to +6.2 at every k>1, flat in k).
- **P-S2 (instruction mitigation reduces the margin): CAPABILITY-GATED** (neither cleanly
  confirmed nor cleanly falsified). At k=16 (rep a), ref -> refinst margin: 1.5B +3.58 ->
  +4.54 (worse), 3B +7.91 -> +7.75 (no help), 7B +5.01 -> +4.54 (marginal), 14B +3.34 ->
  +1.21 (substantial), Llama-8B +3.05 -> +2.30 (partial), phi-4 +1.91 -> +0.03 (complete
  fix). On gaps, refinst brings phi-4 to +0.33 at k=16, below its blind +0.77, while
  Qwen-7B stays inflated at +1.93.
- **P-S3 (multiple references reduce anchoring below single-ref): CONFIRMED on the Qwen
  pool, POOL-DEPENDENT overall.** Margins toward the original reference collapse to null at
  k=16 for all judges (-0.94 to +0.19); Qwen-7B multiref gaps +0.56/+0.81/+0.50/+1.13 vs
  ref +0.91/+1.39/+1.71/+1.64, though not to blind level at k=16 (+0.33). On the Llama pool
  the mitigation largely fails (+2.06 vs +2.19 at k=16; margins +4.73/+5.57 at k=8).
- **P-S4 (cross-family judges replicate the inversion): CONFIRMED.** Llama-8B judge: k=1 ref
  +0.38 vs blind +0.65; k=16 ref +1.27 vs blind +0.21. phi-4 as under P-S1.
- **P-S5 (cross-family generator replicates): PARTIAL.** The k>1 inversion replicates on the
  Llama pool (Qwen-7B judge: ref +2.19 [+1.81,+2.57] vs blind +0.89 [+0.66,+1.11] at k=16,
  inverted at every k>=2), but the k=1 help does NOT replicate (ref +0.98 [+0.64,+1.31] vs
  blind +0.78 [+0.54,+1.04], overlapping, reference slightly worse), and both mitigations
  fail on this pool for the Qwen-7B judge (refinst +2.39, multiref +2.06 at k=16). Cause of
  the k=1 non-replication left unattributed; blind gaps on this pool are elevated at every k
  (+0.78 to +1.13), so the Qwen judge is generally less reliable on Llama text.

Boundary status after this grid: the multiplicity half (only-if) is supported across six
judges, two task families (Ties and synthetic), and two generators; the uniqueness half (if)
is supported within-family and for the strongest cross-family judge but failed for a mid-size
judge on cross-generator text. Reported in the paper as directionally established with one
failed leg, conditional, not a law.
