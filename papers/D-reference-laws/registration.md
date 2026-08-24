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

## External registration note (2026-08-23): OSF registrations posted

Three registrations were posted to the Open Science Framework on 2026-08-23, with immutable
public timestamps (approved and publicly visible as of 2026-08-23 (anonymous access verified), which does not affect the timestamps):

- `osf.io/ym5x9`: the clean preregistered replication of the reference-lever inversion
  (this paper), registered before any pool generation, with the population, estimators,
  and both primary endpoints pre-specified.
- `osf.io/jg4ak`: the DPO training-pressure rerun (companion paper A), registered before
  the rerun's evaluation was read, with the frozen manipulation check and predictions
  P-D1..P-D3.
- `osf.io/axp3s`: the Putnam second-dataset audit replication (companion paper A),
  registered before any Putnam labels were collected, under the frozen revised CI rule.

All earlier registrations in this file remain internal git timestamps only.

## Outcome note (2026-08-23): clean preregistered replication (osf.io/ym5x9) run; all three predictions confirmed

The replication registered at `osf.io/ym5x9` (2026-08-23, before any pool generation, with the
analysis population, estimators, and primary endpoints frozen in the pre-committed
`papers/analysis/repl_analysis.py`) has now run. All numbers:
`papers/analysis/repl_results.json` (canonical; produced by the frozen script).

Design as registered: 120 fresh tasks across five programmatically verifiable constraint
families (CRT remainders, subset-sum, Goldbach pairs, divisor counts, digit sums), each with an
exact answer-checkable validity oracle (no enumeration, no LLM adjudication); generator
Llama-3.1-8B-Instruct (non-Qwen); judges Qwen2.5-7B-Instruct and phi-4 (cross-family pair),
blind vs single-reference, two rubric replicates.

Calibration disclosure: pass rates are in-band by design after a two-pass pilot calibration.
The calibration passes adjusted task-family difficulty and added a mandatory-boxing instruction
to the generation prompt; pilot items never enter the analysis. Final pool: 105/120 items in
the registered [0.2, 0.8] band, mean pass rate 0.455.

- **P-R1 (primary endpoint E1): CONFIRMED.** Pooled per-item paired referenced-minus-blind
  excess-gap delta over the two judges, item-level cluster bootstrap: +1.19 [+1.02, +1.36],
  n=105 in-band items. Per-judge deltas individually significant: Qwen-7B +1.29 [+1.07, +1.52];
  phi-4 +1.08 [+0.94, +1.24].
- **P-R2 (selection collapse): CONFIRMED.** Exact McNemar per judge on the 93 eligible items
  (both matching and non-matching valid answers present): Qwen-7B 56 referenced-only vs 2
  blind-only discordant items; phi-4 76 vs 0; both p < 1e-5 (reported as p < 10^-5).
- **P-R3 (anchoring margins positive for both judges): CONFIRMED.** Qwen-7B +4.62
  [+4.29, +4.94]; phi-4 +3.79 [+3.47, +4.09] (n=93).

The replicated effect is roughly three times the original Ties-pool estimate (+0.41 checker
labels / +0.50 label-corrected), on a pool where the checker is exact and the population was
fixed in advance, so no post-hoc population or estimator freedom exists. The k=1-helps leg was
not retested: the arms are blind vs single-reference only, and multiplicity varies across items
without k being controlled per stratum. Integrated in the paper as Section RQ5 (Table 7), with
the abstract, contributions, ledger, and Limitations updated accordingly.


## Public-visibility note (2026-08-23)
All three OSF registrations (jg4ak, axp3s, ym5x9) were approved by the registrant and are publicly visible with anonymous access; registration timestamps 2026-08-23 19:29 UTC precede all corresponding data.

## Outcome note (2026-08-23): k-stratified structural mitigations (osf.io/qugbd); P-M1 confirmed, P-M2 partial, P-M3 confirmed

Externally registered at `osf.io/qugbd` on 2026-08-23 22:56, before any pool was built and before
any data was generated. This is the paper's fourth external registration. All numbers below:
`papers/analysis/mitigation_results.json` (canonical; produced by the committed
`papers/analysis/mitigation_analysis.py`, written and registered before the run).

Design as registered: 75 tasks with EXACTLY k valid answers, 15 items per stratum at
k in {1, 2, 4, 8, 16}, drawn from the same five programmatically verifiable families as the
ym5x9 replication, so validity is exact by construction (all 465 stored answers verified against
the family oracles). Generator: Llama-3.1-8B-Instruct. Judges: Qwen2.5-7B-Instruct and phi-4
(the same cross-family pair as the replication). Four conditions, each with two rubric
replicates:

- **blind**: no reference.
- **ref**: single reference in context (the paper's standard referenced condition).
- **M1, blind-then-reveal**: call one scores the candidate blind; call two shows the reference
  plus the judge's own blind score, instructing that a correct answer differing from the
  reference keeps its score.
- **M2, equivalence-gated**: call one scores blind; a separate call asks only whether the
  candidate's final answer is valid, with the reference shown as one valid example; the final
  score is the blind score if the candidate is judged valid, and zero otherwise.

Estimands identical to the rest of the paper: anchoring margins (E1, rubric a, defined for
k > 1 on items where matching and non-matching valid answers coexist) and per-item paired
condition-minus-blind excess-gap deltas at n=64 with an item bootstrap (E2). Per-stratum item
counts entering E2: 15, 15, 13, 14, 11 at k = 1, 2, 4, 8, 16 (k>1 pooled n=53). Margin item
counts: 15 at k=2, 12 at k=4, 10 at k=8; the k=16 stratum has too few coexistence items to
report a margin.

- **P-M3 (single reference helps at k=1, harms at k>1): CONFIRMED**, now with exact per-item k
  control and external preregistration. Gap delta vs blind at k=1: +0.05 [-0.30, +0.43]
  (Qwen-7B) and -0.11 [-0.14, -0.07] (phi-4), i.e. no harm, or a benefit, when the answer is
  unique. Pooled over k>1: +1.50 [+1.17, +1.82] (Qwen-7B) and +1.07 [+0.81, +1.34] (phi-4).
  Trend: the harm steps up at k=2 and stays elevated, Qwen-7B +0.96 [+0.58, +1.34] at k=2 and
  +1.39 [+0.71, +2.05] at k=16; phi-4 +0.58 [+0.29, +0.87] and +1.28 [+0.89, +1.69].
- **P-M1 (M1 reduces margin and gap at k>1, preserves the k=1 benefit): CONFIRMED**, and
  importantly NOT capability-gated. M1 gap delta vs blind at k>1 pooled: -0.05 [-0.32, +0.21]
  (Qwen-7B) and +0.16 [+0.00, +0.33] (phi-4), against single-reference +1.50 and +1.07. Margins
  roughly halve for both judges: at k=2, Qwen-7B 5.02 [4.45, 5.51] -> 2.98 [2.35, 3.57] and
  phi-4 3.73 [3.04, 4.39] -> 1.79 [1.18, 2.36]. The k=1 benefit is preserved: M1 deltas at k=1
  are +0.41 [-0.09, +0.84] (Qwen-7B) and +0.04 [-0.13, +0.27] (phi-4), both indistinguishable
  from blind. Unlike the one-sentence any-correct-answer instruction (P-S2/P-S2b), which is a
  placebo below frontier capability, M1 works for the mid-size judge and the strong judge alike.
- **P-M2 (M2 removes the margin, CI including zero at every k>1, gap at or below blind):
  PARTIALLY CONFIRMED**, capability-gated in the OPPOSITE direction from the instruction fix.
  For phi-4 M2 fully neutralizes anchoring: k=2 margin +0.14 [-0.07, +0.34], CI including zero
  and indistinguishable from that judge's blind margin of +0.11 [-0.06, +0.28]; gap delta at
  k>1 pooled -0.07 [-0.11, -0.03], with no stratum above blind by more than sampling noise
  (per-k -0.07, -0.11, +0.03, -0.15 at k=2,4,8,16). For Qwen2.5-7B M2 fails and is worse than a
  plain reference: k=2 margin +6.62 [5.60, 7.56] against +5.02 for single reference, gap delta
  at k>1 +1.31 [+0.91, +1.77]. Mechanism of the failure: the standalone validity call is
  unreliable at that scale, and a wrong invalid verdict zeroes an otherwise good blind score.
  Below the capability line the instruction fix was inert and harmless, while M2 is actively
  harmful, so protocol choice is itself capability-dependent.
- **P-M4 (per-k trend across protocols): EXPLORATORY**, not individually registered, reported
  descriptively. The single-reference harm steps up at k=2 and stays elevated for both judges.
  M1 sits near zero at every stratum for Qwen-7B (deltas -0.30 to +0.12 across k=2,4,8,16) and
  for phi-4 except a residual at k=16, +0.44 [+0.13, +0.76], the only M1 cell whose interval
  excludes zero. M2 splits by judge at every k: phi-4 spans -0.15 to +0.03 and never rises above
  blind detectably, while Qwen-7B climbs with multiplicity to +2.77 [+1.75, +3.89] at k=16, the
  largest single cell in the experiment.

Practitioner payoff, now stated in the paper rather than only a prohibition: score blind first
and let the reference only correct demonstrated errors. That removes the measured harm at k>1
for both judges tested while preserving the k=1 benefit, and where the judge is strong enough to
decide validity on its own, decomposing validity into a separate call removes the harm entirely.

Scope stated in the paper's Limitations: 75 items, five constraint families of the same
programmatic kind as the replication rather than free-form generation, one generator, two
judges, two protocol families; margins are rubric-a only and the k=16 stratum yields no margin;
M2's failure at mid scale means protocol choice is capability-dependent and neither protocol
should be assumed to transfer without auditing the validity call on the deployment's own tasks;
and both protocols cost two judge calls per candidate, roughly doubling judge inference, which
is a real practical trade against leaving the judge blind at single cost.

Integrated in the paper as Section 3.4 (`sec:struct`, "Structural mitigations: judge blind
first, then reveal", Table 6 `tab:struct`), placed after the k-grid section and before the
exploratory Ties section, with the abstract, contributions, boundary/practitioner rule,
conclusion, ledger (rows P-M1..P-M4), and Limitations updated accordingly.

## Deviation and rescoring note (2026-08-24): M2 soft gate, registered P-M contrasts, P-M1 downgraded to PARTIAL

Recorded after the round-6 review. Three items: a protocol deviation we had not disclosed, the
registered contrasts that P-M1/P-M2/P-M3 were actually registered on (now computed), and the
consequent rescoring of P-M1. New canonical artifact:
`papers/analysis/mitigation_registered_contrasts.json` (committed). It was computed after the
round-6 review from the same frozen score files, so it carries no pre-registration weight of its
own; the statistics in it, however, are the ones the P-M predictions were registered on.

### 1. DEVIATION: M2 is a soft probabilistic gate, not the hard gate registered

The `osf.io/qugbd` registration and the M2 description above both state a HARD gate: "the final
score is the blind score if the candidate is judged valid, and zero otherwise". The implementation
(`experiments/tfa-vs-judge/scripts/mitigation_judge.py`) instead multiplies the blind score by the
validity call's probability of Yes, `P(Yes) / (P(Yes) + P(No))`, read from the answer token's
logprobs, with a text fallback when that mass is below 0.05. Every M2 number reported in the paper
and above is the SOFT version. Nothing was rerun; the deviation is disclosed rather than repaired.

A public amendment recording this deviation was posted to the OSF project wiki
(`osf.io/kszeu`, 2026-08-24), so the correction carries a third-party timestamp of its own.
The paper discloses it in Section `sec:struct` (a dedicated "Registration deviation" paragraph),
in the notes to `tab:struct` and `tab:rule`, in the P-M2 ledger row, and in Limitations.

### 2. MEASURED failure mechanism for M2, replacing the earlier hand-waved one

The earlier explanation ("the standalone validity call is unreliable at that scale, and a wrong
invalid verdict zeroes an otherwise good blind score") was an inference from the protocol, not a
measurement, and it also described the hard gate. The soft gate exposes its multiplier, so the
mechanism is now measured directly, averaged over 591 reference-matching and 1335 equally valid
non-matching answers per judge:

- Qwen2.5-7B: mean multiplier 0.998 for reference-matching valid answers versus 0.422 for
  equally valid non-matching ones.
- phi-4: 0.987 versus 0.965.

The validity call still shows the reference. For the weaker judge the anchoring channel therefore
RELOCATES into the validity call rather than being removed, which is why M2's k=2 margin (+6.62)
exceeds the raw reference's (+5.02). For phi-4 the multiplier is nearly flat across answer types
and the channel is genuinely removed. This is stated in the paper as the measured mechanism.

### 3. Registered contrasts, now computed

P-M3 was registered on the STEP, and P-M1 and P-M2 on contrasts against the SINGLE REFERENCE.
Earlier drafts scored them by reading adjacent columns of `tab:struct` instead. The registered
statistics (Qwen2.5-7B then phi-4, n=53 items at k>1, n=15 at k=1):

- **P-M3 step (k>1 delta minus k=1 delta):** +1.45 [+0.94, +1.93] and +1.18 [+0.90, +1.45].
  Both exclude zero, so P-M3 is CONFIRMED on its registered statistic, not on a side-by-side
  comparison of two columns.
- **M1 versus single reference at k>1:** -1.55 [-1.89, -1.19] and -0.91 [-1.10, -0.72].
  Both exclude zero.
- **M2 versus single reference at k>1:** -0.19 [-0.57, +0.25] and -1.14 [-1.40, -0.88].
  The Qwen-7B interval CROSSES ZERO, so M2 does NOT significantly improve on simply showing the
  reference for the weaker judge. Recorded in the P-M2 ledger row.

### 4. RESCORING: P-M1 is downgraded from CONFIRMED to PARTIAL

P-M1 was registered as two legs: (a) M1 reduces the margin and the inflation versus a single
reference at k>1, and (b) M1 preserves the k=1 benefit. The earlier "CONFIRMED" scored both.

- **Leg (a): CONFIRMED.** Registered contrast -1.55 [-1.89, -1.19] and -0.91 [-1.10, -0.72];
  deltas versus blind at k>1 -0.05 [-0.32, +0.21] and +0.16 [+0.00, +0.33].
- **Leg (b): NOT DEMONSTRATED.** The only k=1 benefit this experiment measures is phi-4's
  single-reference -0.11 [-0.14, -0.07]. M1's k=1 deltas are +0.04 [-0.13, +0.27] (phi-4) and
  +0.41 [-0.09, +0.84] (Qwen-7B, the largest k=1 harm point estimate in the table). Both are
  indistinguishable from blind, which supports "M1 costs nothing at k=1" and does NOT support
  "M1 preserves the k=1 benefit".

The paper now says "costs nothing when the answer is unique (its k=1 deltas are indistinguishable
from blind)" in all six places that previously claimed benefit preservation (abstract,
contributions, `tab:struct` caption, `tab:rule` M1 and M2 k=1 cells, `sec:boundary`, conclusion),
and `tab:rule`'s k=1 cells for M1 and M2 read "No cost (not shown to preserve the benefit)".
P-M1's ledger row is rescored PARTIAL.

Related softening in the same pass: "M1 removes the harm" is now "M1 removes the measured
inflation at n=64 while leaving roughly half the anchoring premium" (margins +2.98 Qwen-7B and
+1.79 phi-4 at k=2 against blind +0.08 and +0.11), with the note that whether the residual
re-emerges under optimization stronger than best-of-64 is untested. "Capability-gated" language
for M2 is replaced by "differed between the two judges tested, in a direction consistent with
capability but not isolated from it (N=2 judges)".

### 5. Population disclosures added in the same pass

- **Mitigation pool (this experiment).** Items enter the inflation deltas only if their pool pass
  rate lies in [0.05, 0.95], which is WIDER than the [0.2, 0.8] band registered for the ym5x9
  replication. Analyzed counts 15/15/13/14/11 at k=1/2/4/8/16 out of 15 built per stratum. The
  paper now flags that cross-experiment comparisons (+1.50 / +1.07 here versus +1.19 on the
  replication pool) span populations selected by different rules.
- **Replication pool (ym5x9).** P-R2 and P-R3 are computed on all 93 eligible items, of which 83
  are also inside the registered [0.2, 0.8] band; E1 alone applies the band, as frozen in
  `repl_analysis.py`. Disclosed in the Table 1 notes; the claim of uniform population discipline
  across all three endpoints is withdrawn.

### 6. Corrected disclosure numbers on the replication pool

New canonical artifact: `papers/analysis/repl_disclosures.json` (committed).

- Boxed-answer compliance is 0.616 over all 120 items and 0.639 over the 105 in-band items. The
  paper previously said "0.62" without saying which.
- Mean pass rate 0.455 is over all 120 items; the in-band mean is 0.491. The paper previously
  attributed 0.455 to the in-band pool.
- Pilot overlap: six main-pool items duplicate pilot problem text through seeded-window
  collisions, of which two survive the band filter. Excluding those two leaves E1 unchanged:
  +1.20 [+1.04, +1.37] on n=103 versus +1.19 [+1.03, +1.36] on n=105, as produced by the
  committed `round6_disclosures.py` (seeded). Earlier drafts quoted +1.19/+1.19 and +1.20
  [+1.03, +1.37] for this same contrast; those differ only in the bootstrap's third digit.
  The producer's seeded output is now the canonical figure, and bootstrap bounds carry a
  Monte Carlo tolerance of roughly +/-0.02 against the frozen registered run. The conclusion
  is unaffected either way: the endpoint does not move when the two overlapping items are
  dropped.
- The reproducibility paragraph is corrected: every number is computed from committed score
  files, and every number scoring a registered prediction comes from a committed pre-run script,
  and the three round-6 artifacts (`repl_disclosures.json`,
  `mitigation_registered_contrasts.json`, `repl_pressure_curve.json`) are post-hoc but are
  now regenerated end to end by one committed producer, `papers/analysis/round6_disclosures.py`.
  They were computed after the fact, so they carry no registered status; they are reproducible,
  not preregistered.

### 7. Selection-pressure curve (post hoc, added to the paper)

New canonical artifact: `papers/analysis/repl_pressure_curve.json` (committed). The paired
referenced-minus-blind hack gap on the same 105 replication items as a function of the best-of-n
budget: n=2 +0.076 [0.056, 0.096], n=4 +0.267 [0.233, 0.302], n=8 +0.468 [0.415, 0.525],
n=16 +0.671 [0.585, 0.759], n=32 +0.810 [0.701, 0.924], n=64 +0.895 [0.748, 1.048]. (Earlier
drafts quoted a hand-run version of this curve, n=2 +0.088 to n=64 +0.895; the values above are
the seeded output of the committed producer and supersede it. The shape and every sign are
unchanged.) Monotone,
every interval excludes zero. UNITS CAVEAT, stated in the paper: this curve is in RAW hack-gap
units, not baseline standard deviations, so it is not comparable with E1's +1.19 and must not be
read as a smaller version of it. Post hoc, not registered; the registered endpoint remains n=64.

### 8. Analysis-n corrections in four captions

Four captions stated design n where the analysis n is smaller, and now state both: `tab:synthk`
and `fig:synthk` (12 tasks built per stratum, 4 to 6 items per cell after the [0.05, 0.95]
pass-rate filter), `tab:paired` (n=6 at k=1, n=20 pooled over k>1), and `tab:mitig` (n=5 items
per margin cell, since a margin needs matching and non-matching valid answers to coexist).

Also corrected in the same pass: "Qwen-7B's referenced inflation roughly triples over blind by
k=8" was wrong (it is 2.4x, +1.71 against +0.72), and the chance expectation for positive-side
CI exclusions over 8 cells is 0.2, not the 0.4 stated at three sites.


## Round 7 (2026-08-23, after the v13 dual review)

### 9. G8: float-placement regression, fixed

Tables 7, 8 and 10 of v13 typeset on pages 25 to 27, after the Conclusion, because an `[h]`
placement on `tab:pressure` jammed the float queue. Both reviewers marked the compiled PDF
unreviewable and both scored readability down for it. Fixed by removing the `[h]`, raising the
float fractions, and adding `placeins` barriers at subsection boundaries. All ten tables now
typeset inside their own sections. This was a typesetting bug, not a scientific one, but it is
recorded here because it, not the disclosure load, is the likely cause of the v13 readability
drop in both reviews.

### 10. G9: the extraction-rate contradiction, and the sensitivity that resolves it

The v13 text claimed "the one extraction problem we found, a 0.65 boxed rate, is confined to the
cross-generator synthetic pool." That is false: the replication pool's own boxed rate is 0.616.
The claim is withdrawn. The correct distinction, now stated in the paper, is not where the
friction occurs but whether it can act on the contrast: in the replication and the Ties pool the
referenced and blind arms score the SAME samples with the same fallback, so extraction failure is
common to both arms and differences out; in the cross-generator pool the compared strata are
different sample populations from different generators, so a 0.65-versus-0.89 gap is a difference
between the things being compared.

That argument is now also measured rather than asserted. NEW post-hoc analysis (producer:
`round6_disclosures.py`, artifact `repl_disclosures.json`): split the 105 in-band replication
items by their own boxed-compliance rate (pool median 0.641).

- E1 on the cleaner half: +0.94 [+0.71, +1.16], n=56
- E1 on the top tercile:  +0.90 [+0.65, +1.16], n=40
- E1 on the messier half: +1.49 [+1.27, +1.70], n=49
- per-item correlation between compliance and delta: r = -0.29 [-0.43, -0.12]

The correlation is NEGATIVE: messier items show LARGER inflation. Reported in full because it
cuts against the headline number's size. The endpoint survives on the cleanest items, so
extraction friction does not manufacture the effect, but it does inflate it, and +0.9 is stated
in the paper as the conservative reading of the headline +1.19.

Decomposition of that gradient (diagnostic, not in the paper's claim set): the extra inflation on
messy items comes overwhelmingly from the TRUE-accuracy term, not the judge-score term. Clean
half: judge-gain difference +0.761, true-gain difference -0.054. Messy half: judge-gain difference
+0.845, true-gain difference -0.143. The two halves also differ in difficulty (base accuracy 0.600
clean versus 0.365 messy), so the boxed split is partly a difficulty split, and the natural
reading is that harder items give the reference more room to cost real accuracy rather than that
extraction noise fakes the judge inflation.

### 11. Confirmatory and exploratory separated in the main narrative

Both reviewers asked for this. The post-hoc selection-pressure curve was moved out of the
replication section into a new subsection, "Exploratory analyses (not registered, not claims),"
and a "How to read this section" signpost at the top of Results names which subsections are
confirmatory and which are not. No analysis changed; only where it is presented and what it is
labelled.

### 12. Corrections in the same pass

- "roughly three times the original estimate" was wrong against the paper's own preferred
  comparator. It is 2.4x the label-corrected +0.50 and 2.9x the checker-label +0.41. Now stated
  as "about two and a half times," with both ratios given once.
- P-M3's "helps at k=1" leg is carried by phi-4 alone; Qwen-7B's k=1 delta is a null. The
  attribution is now explicit at both sites where the claim appears.
- The k>1 shape is non-monotone (a k=4 to k=8 hump), not flat; "does not grow much after" replaced.
- `tab:struct`'s residual band widened from "a third to a half" to "a third to three fifths"
  (Qwen k=2 is 59%).
- `repl_pressure_curve.json` was the last artifact without a producer; `round6_disclosures.py`
  now generates it.

### 13. Round-7 additions demanded by the two v14 reviews

**Band-matched comparison (producer: `round7_linkage.py`, artifact `round7_linkage.json`).**
The cold read called the "these populations are selected by different rules, do not difference
them" note statistical escaping. So we removed the fence by matching the bands. The k-stratified
k>1 single-reference-vs-blind deltas, recomputed under the replication's registered [0.2, 0.8]
band (n=39 instead of 53): Qwen-7B +1.483 [1.128, 1.831], phi-4 +1.194 [0.911, 1.494]. Against the
replication's E1 of +1.19 [1.02, 1.36], phi-4 lands on it and Qwen-7B sits above it. Under the
k-stratified experiment's own registered [0.05, 0.95] band the same contrasts are +1.497 and
+1.067. Post hoc, not registered. The registered endpoints are unchanged; this only licenses a
comparison the paper previously refused to make.

**Margin-to-inflation linkage: a NEGATIVE result, reported (same producer).**
The cold read asked for a quantitative bridge from the anchoring margin to the inflation it is
claimed to cause. We tested it at the per-item level on the 35 k>1 items of the k-stratified pool:

- phi-4:    r = +0.291 [+0.032, +0.542], slope +0.179 inflation per margin point
- Qwen-7B:  r = +0.064 [-0.306, +0.378], slope +0.060

Tercile means are non-monotone for both judges (Qwen 1.304 / 1.433 / 1.292; phi-4 0.614 / 1.112 /
0.987). So the per-item link is weak for one judge and absent for the other. This does NOT
undercut the causal claim, which rests on rotation (same sample text, reference switched), nor the
aggregate correspondence between margin levels and inflation levels. It does mean the paper cannot
claim that a given item's margin predicts that item's inflation, and the paper now says so, and
downgrades "This is also why the inversion happens" to "This is a plausible account of why."
Per-item margins rest on few valid samples per item and inflation on a noisy selection process, so
this is weak evidence against a tight link rather than evidence for a competing mechanism.

### 14. Corrections forced by the internal re-review of v14

- **Contrast CIs were truncated toward zero at nine sites**, every error narrowing the interval:
  m1_vs_ref Qwen printed [-1.89, -1.19] for [-1.900, -1.199]; m2_vs_ref Qwen [-0.57, +0.25] for
  [-0.584, +0.259]; PM3_step phi-4 [+0.90, +1.45] for [0.910, 1.453]. All nine now round rather
  than truncate. This item was reported fixed in round 6 and was not; it is fixed now.
- **The provenance paragraph contradicted itself.** One sentence said three artifacts were
  released "as committed JSON rather than as pre-existing scripts"; a sentence added five lines
  later said the same three are regenerated by a committed producer. The superseded sentence was
  retired rather than left standing beside its replacement.
- **The confirmatory/exploratory signpost overclaimed.** It asserted that everything before the
  exploratory subsection is "a registered prediction scored against a frozen estimator," which the
  paper's own captions contradict (the paired re-analysis, the boxed sensitivity, P-M4, and the
  whole Ties section are post hoc). Restated: the claims rest on the primary registered results of
  those sections, and post-hoc analyses inside them are marked where they appear.
- **Monte Carlo magnitude**: the recomputation differs in the second decimal (0.011), not the
  third, as two adjacent sentences claimed inconsistently.
- **The "roughly half the anchoring premium" figure** appeared at four sites against a measured
  range of 32.4-59.4%; all four now say "a third to three fifths."
- **The k>1 shape**: the text asserted a k=4-8 hump while quoting only k=2 and k=16. All four
  strata are now quoted (Qwen +0.96/+1.77/+1.90/+1.39, phi-4 +0.58/+1.54/+0.99/+1.28), with the
  note that every k>1 stratum excludes zero for both judges, so the boundary claim does not depend
  on the shape, which is noisy at 11-15 items per cell and is not interpreted.
- **"A factor of ten"** on the pressure curve was calibrated to the pre-rescript n=2 of 0.088; at
  0.076 it is nearly twelvefold.
- The n=103 sensitivity, the pressure-curve values, and the reproducibility bullet in this log
  were synced to the producers' seeded output (item 6 and item 7 above were edited in place).
- A missing FloatBarrier before the boundary subsection was added.

### 15. Presentation changes in the same pass

- A four-row headline panel ("the whole paper in four numbers") now sits on page 2 alongside the
  anchoring figure, so the main result is visible without reading into Section 3.
- The conservative reading of the headline (+0.90 [+0.65, +1.16], cleanest-extraction items) is
  now carried in the abstract, the intro contribution bullet, and as a row of the replication
  table, rather than appearing once mid-paragraph.
- The abstract now states the scope in its third sentence: short-answer tasks with exact
  programmatic validity oracles; free-form generation is outside what is tested.
- The abstract's k=1 leg was weakened from "where the reference helps" to "where the reference is
  at worst harmless," with the benefit half explicitly marked capability- and domain-dependent and
  measurable for one of the two judges.
- Canonical artifact filenames were cut from narrative prose and table notes (17 mentions down to
  9), surviving only in the reproducibility paragraph, the ledger, and the two registered-analysis
  script names where they are load-bearing for the preregistration claim.

### 16. Round-8 additions demanded by the v15 cold read (producer: `round8_followups.py`)

**Matched-population recomputation, closing the endpoint-population footnote.**
The replication table's three endpoints ran on different populations (E1 on the 105 in-band items,
P-R2/P-R3 on all 93 eligible items). Recomputed on the 83-item intersection: E1 +1.200
[1.022, 1.387]; selection collapse 49/2 (Qwen-7B) and 67/0 (phi-4); anchoring margins +4.58
[4.219, 4.937] and +3.83 [3.491, 4.172]. Every conclusion is unchanged from the registered rows,
which remain the ones the predictions were scored on. Post hoc.

**M1 under rising selection pressure: the residual premium does NOT convert into inflation.**
M1 removes measured inflation at best-of-64 but leaves a third to three fifths of the anchoring
premium standing in the margins, and both reviews asked whether that residual re-emerges under
more optimization. Paired hack-gap delta versus blind at k>1, by selection budget:

| n | ref (Qwen) | M1 (Qwen) | ref (phi-4) | M1 (phi-4) |
|---|---|---|---|---|
| 2 | +0.07 | -0.03 | +0.08 | +0.03 |
| 4 | +0.29 | -0.00 | +0.25 | -0.02 |
| 8 | +0.55 | -0.01 | +0.39 | -0.08 |
| 16 | +0.87 | -0.00 | +0.53 | -0.11 |
| 32 | +1.13 | -0.01 | +0.70 | -0.12 |
| 64 | +1.44 | -0.06 | +0.83 | -0.09 |

The single reference's premium climbs monotonically across a 32x range of selection pressure;
M1's stays flat and indistinguishable from blind throughout. This is the strongest available
evidence that M1's residual anchoring is inert rather than merely dormant. It does not cover
budgets beyond 64, nor optimizers that adapt to the judge rather than sampling independently.
Post hoc, not registered.

**Simulation bounding the negative linkage result (item 13).**
Ground truth: inflation is an EXACT linear function of the per-item anchoring margin. Both
quantities are then observed through this design's sampling noise (about 4 matching and 6
non-matching valid samples per item, judge score SD 1.6, inflation measurement SD 0.55, 35 items,
400 replicates). The recovered per-item correlation is r = 0.481 on average, 95% spread
[0.226, 0.698]; 12% of replicates would yield a CI including zero.

Interpretation, stated in the paper without spin: phi-4's observed +0.29 sits at the bottom of
that range, so it is consistent with a real pathway attenuated by noise. Qwen-7B's +0.06 falls
BELOW the range, so noise does not explain it away. The simulation therefore bounds the negative
result rather than rescuing it, and the paper's summary is that anchoring is causal for scores
(by rotation), tracks inflation in aggregate, and is NOT established as a per-item quantitative
pathway.

### 17. Claim language corrected in the same pass

- Abstract: "The mechanism is anchoring" -> "Anchoring is the mechanism we can demonstrate," with
  the per-item negative result stated in the abstract itself rather than only in Section 3.2.
- The k=1 benefit had been over-weakened in v15 to "measurable for one of our two judges." That
  understated the paper's own grid evidence, where the reference helps at k=1 for five of six
  judges with CIs excluding zero. Restated precisely: it helps five of six judges on the grid, does
  not survive a change of generator (P-S5), and is a null for one of the two judges in the
  registered k-controlled pool. Two table captions asserting a flat "the reference helps at k=1"
  were corrected to match.
