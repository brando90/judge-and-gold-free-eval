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

## Post-hoc re-analysis note (2026-08-23): paired inference, McNemar, k=1 audit; P-S2b queued

Recorded after the round-4 review. The additions below are POST HOC, demanded by review, and
carry no pre-registration weight; they are produced by the committed
`papers/analysis/synthk_paired.py` into `papers/analysis/synthk_paired.json`, distinct from the
frozen pre-registered `synthk_analysis.py`, which alone scored the registered decision rules.

- **Paired step contrast (the licensed universal).** The mean per-item paired ref-minus-blind
  gap delta over the k>1 strata minus the same delta at k=1 is positive with a CI excluding
  zero for all six judges: 1.5B +0.55 [+0.26,+0.85], 3B +2.55 [+1.50,+3.67], 7B +1.22
  [+0.70,+1.73], 14B +0.46 [+0.13,+0.80], Llama-8B +0.74 [+0.25,+1.24], phi-4 +0.80
  [+0.30,+1.28]. The paired k>1 inflation LEVEL is individually significant for only three of
  six judges (3B +2.41, 7B +0.89, Llama-8B +0.46; 1.5B +0.07, 14B +0.08, phi-4 +0.22 all cross
  zero), and the k=1 paired delta is negative (reference helps) with CIs excluding zero for
  five of six (Llama-8B -0.28 [-0.65,+0.07] crosses). Per-judge slope per log2(k) beyond the
  step is null for 1.5B/3B/7B and positive for 14B +0.23 [+0.00,+0.46], Llama-8B +0.36
  [+0.08,+0.65], phi-4 +0.37 [+0.06,+0.70]. Paper claims downgraded accordingly: the step is
  the universal, the per-cell k=16 universal of earlier drafts is withdrawn.
- **Rotation-arm collapse contrast re-tested with exact McNemar** on the 18 paired items
  (replacing the unpaired Fisher tests): discordant counts 12/0 at 1.5B (p=0.0005), 9/0 at 3B
  (p=0.004), 7/1 at 7B (p=0.070, marginal), 10/0 at 14B (p=0.002).
- **k=1 audit outcome.** On the Llama-generator pool's k=1 stratum the oracle's
  boxed-extraction rate is 0.65 versus 0.89 on the Qwen pool (oracle pass rates 0.53 versus
  0.83, 12 tasks per pool), so the k=1 non-replication under P-S5 has a likely proximate cause
  in answer-extraction friction on Llama formatting rather than judge verification failure;
  likely cause, not proof.
- **P-S2b (second instruction phrasing): REGISTERED AND QUEUED.** A second, do-not-compare
  phrasing of the instruction mitigation will be run on the same grid. Registered prediction:
  the capability-graded pattern of P-S2 replicates under the do-not-compare phrasing (ordered
  improvement with judge capability, phi-4 closest to complete, no reliable improvement at
  1.5B/3B). Also recorded: the 1.5B instruction-worsens result holds only under rubric a
  (+3.58 -> +4.54 at k=16); rubric b improves (+2.52 -> +2.12), so the paper's wording is now
  "a placebo below the capability gate, with one rubric showing worse at 1.5B".

## Outcome note (2026-08-23): P-S2b second-phrasing replication

Registered in the pipeline11 pre-run commit; the run has now completed. All numbers:
`papers/analysis/synthk_refinst2.json` (canonical).

- **P-S2b (second instruction phrasing): CONFIRMED.** The do-not-compare phrasing ("do not
  compare the candidate's answer to the reference; use the reference only to understand the
  problem; verify the candidate's answer on its own merits") reproduces the capability-graded
  pattern with the identical gate ordering. At k=16 (rubric a), ref -> refinst -> refinst2
  margins: 1.5B +3.58 -> +4.54 -> +4.28 [+2.22, +5.72] (no help, slightly worse under both
  phrasings); 3B +7.91 -> +7.75 -> +7.91 [+6.69, +8.94] (no effect); 7B +5.01 -> +4.54 ->
  +4.54 [+4.05, +4.93] (marginal); 14B +3.34 -> +1.21 -> +1.76 [+0.39, +3.33] (substantial);
  Llama-8B +3.05 -> +2.30 -> +1.77 [+0.97, +2.48] (substantial); phi-4 +1.91 -> +0.03 ->
  +0.17 [+0.08, +0.30] (near-complete). The gate is therefore not a single-prompt artifact;
  the residual caveat (both phrasings are single-sentence system-prompt additions) is
  recorded in the paper's Limitations. Scope note (recorded after the round-5 review): the
  second-phrasing arm covers rubric-a margins at k>1 only, with no rubric-b replicate and no
  inflation readout, so it tests exactly the registered gate-ordering claim and nothing
  beyond it; this scope is disclosed in the paper (Table 6 caption, ledger, Limitations).

## Post-hoc audit note (2026-08-23): label-corrected recompute of the headline delta

Recorded after the round-5 review. POST HOC, not registered, no pre-registration weight.
The round-5 review's top item asked what the checker's known validity undercounting (90% of
checker-invalid samples adjudicated valid) does to the headline inflation delta, previously
answered only by the a-priori conservative-direction argument. We measured it: every unique
(item, answer) pair in the primary Ties pool was adjudicated (149 pairs, GPT-5.2, reference
not shown, checker fallback where adjudication failed), corrected validity labels were built
for all 3264 samples, and the paired pooled ref-minus-blind inflation delta was recomputed
under the corrected labels. All numbers: `papers/analysis/ties_corrected_delta.json`
(canonical).

- **Outcome: the correction WIDENS the inversion.** Pooled delta +0.50 [+0.13, +0.87] under
  corrected labels versus +0.41 [+0.07, +0.77] under checker labels. Per-scale corrected
  deltas: 1.5B +0.44 [-0.08, +0.96], 3B +0.76 [+0.08, +1.48] (now individually significant),
  7B +0.23 [-0.39, +0.85], 14B +0.56 [-0.08, +1.25].
- The conservative-direction argument (checker false negatives fall exclusively on
  non-matching answers, which blind judges select more often) is thereby confirmed as a
  measurement, not an argument. The checker-label +0.41 remains the registered-era primary;
  the corrected-label +0.50 is reported in the paper as an adjudication-robustness check
  (Setup, RQ1, Table 1 notes, Limitations).
- Saturation arithmetic, also recorded: combining the audits, roughly 97-98% of pool samples
  are truly valid under the adjudicator (checker accepts 78%; 90% of its rejections are
  adjudicated valid), so the pool is nearly saturated in true validity. Consequently the
  regret-flavored readouts are compressed toward zero by construction (consistent with their
  null CIs), and the registered in-band [0.2, 0.8] filter was computed on mismeasured pass
  rates, an additional reason the registered n=7 population was uninformative.
- Caveat: the corrected labels rest on the same LLM adjudicator, itself fallible and possibly
  lenient; human adjudication of a checker sample remains future work.
