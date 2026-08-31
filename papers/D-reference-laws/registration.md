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
  [+1.03, +1.37] for this same contrast; those differ in the bootstrap's second decimal (for example
  a lower bound of 1.017 against 1.028), which is Monte Carlo variation, not a different result.
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

### 18. Round-9 corrections forced by the internal verification of v15

**Provenance paragraph, false for the second consecutive round.** Two sentences were wrong:
(a) "two committed producers regenerate those three artifacts" -- `round6_disclosures.py` writes
all three; `round7_linkage.py` writes a fourth artifact and `round8_followups.py` a fifth, neither
declared. Now stated as five post-hoc artifacts regenerated by three committed producers.
(b) "nothing in this paper's confirmatory claims rests on them" -- false, because the P-M1, P-M2
and P-M3 verdicts are read off `mitigation_registered_contrasts.json`. The statistics those
predictions name were registered in advance; the computation of them was post hoc. The paragraph
now says exactly that, and scopes the "no confirmatory claim depends on a post-hoc artifact"
statement to the remaining predictions.

**Band-match overreach.** The band-matched comparison removes the pass-rate confound only. The
pools still differ in multiplicity: 44% of the band-matched k-stratified items have k >= 8 against
16% of the replication's (means 6.51 vs 5.82), and this paper's own grid shows inflation rising
with k, so the composition gap runs in the direction of Qwen-7B's residual (+1.48 vs +1.19). The
paper now claims the pass-rate confound removed, not full comparability.

**The attenuation simulation was recalibrated, and its conclusion RETRACTED.** The v16 version
stipulated its noise parameters and concluded that phi-4's r=+0.29 "sits at the bottom" of the
range an exact pathway would produce while Qwen's +0.06 "falls below it." That conclusion was an
artifact of the stipulated inflation-measurement SD of 0.55. Recalibrated so the margin
distribution (mean 4.65), the valid-sample counts (7.77 matching, 22.17 non-matching) and the
within-item judge score SD (1.028) all come from the pool itself, the recovered correlation turns
almost entirely on the one quantity that is NOT identifiable from the data, how noisily each
item's inflation is measured:

| inflation measurement SD | recovered r under an EXACT pathway |
|---|---|
| 0.25 | 0.751 [0.582, 0.864] |
| 0.55 | 0.473 [0.171, 0.710] |
| 1.00 | 0.289 [-0.029, 0.545] |
| 1.50 | 0.199 [-0.098, 0.483] |

Both observed values sit inside that span. So the test does not discriminate, and the honest
conclusion is that the negative linkage result is UNINFORMATIVE rather than evidence against
anchoring. The paper says this. The mechanism claim rests on the rotation intervention, which is
within-item and needs no cross-item linkage.

**Structural: the ledger left the exploratory subsection.** The prediction ledger and the
reproducibility paragraph sat inside Section 3.5, which the Results signpost calls "wholly
exploratory, not evidence for the claims," while that same signpost directed readers there for
every prediction's verdict. Both are now a top-level section, "Every prediction, and where every
number comes from," placed after Results.

**Also:** the headline panel now carries the conservative +0.90 alongside the +1.19, since it is
the most-read object in the paper; the "helps five of six judges" tally now discloses that it is
one pool rather than six replications, and that the single judge it fails for is the only one
tested on a different generator's text.

---

## Round 9 (v19): the "uninformative" reading of the linkage null is RETRACTED

**Deviation/supersession disclosure, 2026-08-24.** The round-8 attenuation sweep (previous
section) treated the inflation measurement SD as "NOT identifiable from the data." The v18
internal review showed it IS identifiable: the two rubric replicates give two estimates of every
item's margin and inflation, and the roles-swapped split-half (estimates (a,b) vs (b,a),
SD of the difference divided by sqrt(2)) puts the inflation measurement SD at 0.457 (Qwen-7B)
and 0.352 (phi-4), against observed per-item inflation spreads of 1.107 and 0.987. Rerunning the
exact-pathway simulation at that data-implied noise, with two corrections to the round-8 sim
(margins deconvolved before the pathway is applied, where round 8 drew true margins from the
OBSERVED margins and re-added measurement noise, double-counting; slope set so the exact pathway
reproduces the measurement-corrected inflation variance, where round 8 stipulated 0.22 and
wrongly noted that slope "only sets scale"):

| judge | exact-pathway r at data-implied noise | observed r | percentile |
|---|---|---|---|
| Qwen-7B | 0.818 [0.687, 0.906] | +0.06 | 0.0 |
| phi-4   | 0.901 [0.824, 0.951] | +0.29 | 0.0 |

Both observed values fall below the 2.5th percentile. The design does discriminate, and an exact
per-item linear pathway from anchoring margin to inflation is REJECTED for both judges. The
round-8 conclusion ("uninformative") is retracted; the paper, ledger, and Limitations now state
the rejection. The rotation result (anchoring causally moves scores within items) and the
aggregate correspondence are unaffected. Producer: papers/analysis/round9_provenance.py
(artifact round9_provenance.json), which also commits producers for three previously
hand-computed quantities (band-match multiplicity composition 43.6% vs 16.2% k>=8, mean k 6.51
vs 5.82; the boxed-compliance decomposition previously computed by boxed_diag.py, which wrote
nothing; a worked example of the inflation estimator on item repl/crt-11). The artifact
manifest the paper references now exists at papers/analysis/MANIFEST.md.

---

## Matched-pool exploitability experiment (P-E1, P-E2) — registered 2026-08-26, FALSIFIED

**Registration.** `papers/analysis/exploit_dose.py`, committed at `36efc6b` before the analysis
was run on any data. The script header pins the design (sub-pool size m=24, v=4 valid samples of
which d are reference-matching, d in {0,1,2,4}, R=20 resamples, paired sub-pool indices reused
across conditions and judges), the estimator (a mirror of the frozen `bon_analysis.py` excess
gap at n=m with a within-oracle-stratum permutation null), the eligibility rule, and both
predictions. No OSF post (external registration is on hold at the collaborator's request); the
git timestamp is the internal registration.

**Motivation.** Round 9 rejected an exact per-item linear pathway from anchoring margin to
inflation and named pool composition, "whether a matching valid sample happens to exist among
the 64," as unresolved structure the existing design could not separate. This experiment
manipulates that composition directly, at zero marginal compute: every sample already carries
blind and referenced scores, so best-of-n over a subset of scored samples is arithmetic.

**Outcome: P-E1 is FALSIFIED, and in the opposite direction.** Paired referenced-minus-blind
excess gap by dose (48 eligible items: 12 k-stratified k>1, 36 replication):

| judge | d=0 | d=1 | d=2 | d=4 | d=4 minus d=0 |
|---|---|---|---|---|---|
| Qwen2.5-7B | +1.18 [+0.99,+1.37] | +1.11 [+0.95,+1.26] | +0.65 [+0.50,+0.78] | -0.23 [-0.43,-0.03] | **-1.41 [-1.66,-1.15]** |
| phi-4 | +0.95 [+0.82,+1.08] | +0.58 [+0.45,+0.72] | +0.22 [+0.13,+0.31] | -0.44 [-0.56,-0.33] | **-1.39 [-1.56,-1.22]** |

P-E1 predicted a positive step excluding zero; the step is negative and excludes zero for both
judges. P-E1's second clause (paired delta's CI includes zero at d=0) is also falsified: d=0 is
where inflation is LARGEST. P-E2 (referenced judge picks reference-matching valid answers more
often than blind at every dose >= 1) is CONFIRMED: 0.93/0.98 vs 0.18/0.43 at d=1,2 (Qwen-7B) and
0.96/0.99 vs 0.24/0.50 (phi-4).

**Post-hoc mechanism (unregistered; `exploit_dose_diag.py`, `exploit_dose_attract.py`).** The
sign reverses because the harm is not the opportunity to select a matching CORRECT answer. When
no valid answer matches the shown reference (d=0), the referenced judge selects a VALID sample
only 0.14 (Qwen-7B) / 0.21 (phi-4) of the time against 0.72 / 0.79 blind, and its true gain
collapses to -0.03 / +0.05 against blind's +0.55 / +0.63. Of the invalid samples the referenced
judge selects, 58% (Qwen-7B) and 72% (phi-4) contain the reference answer's text, against 43%
and 35% for the blind judge on the same sub-pools. Reading: absent a correct look-alike,
reference similarity pulls selection onto INCORRECT look-alikes. At d=4 every valid sample
matches, both arms select validly, and the referenced arm's residual is its score-polarization
term only, which nets slightly negative.

**Status of the claim.** This is a registered-then-falsified prediction and is reported as such;
the mechanism reading above is post hoc and carries no registration weight. It converges with
the independently registered similarity-vs-correctness 2x2 (P-SC1/P-SC2), which tests the same
"similarity beats correctness" hypothesis with constructed candidates rather than by
subsampling; that experiment's construction is committed and its judging has not been run.

---

## Distance-from-reference gradient (P-D1..P-D3) — registered 2026-08-26, MIXED

**Registration.** `papers/analysis/distance_gradient.py`, committed at `160e638` before being
run. Answer-space distance (numeric gap / Jaccard / edit distance, pinned per answer shape) on
the already-scored replication and k>1 k-stratified pools; primary population is oracle-valid
NON-matching samples; registered estimator is the mean per-item OLS slope with item bootstrap.

**Outcomes.** 160 items analyzed, 20 excluded. On the registered statistic, P-D1 and P-D2 are
formally confirmed (referenced slope and paired ref-minus-blind slope negative, CIs excluding
zero, both judges) — but the registered estimator is hereby disclosed as FRAGILE: the mean
per-item slope is dominated by a small set of ill-conditioned items with tiny within-item
distance spread (slopes reaching tens of points per unit distance on a 10-point scale), so the
magnitude is not interpretable. Post-hoc robust re-analysis
(`distance_gradient_robust.py`, unregistered): median and 10%-trimmed slopes and per-item
Spearman correlations give a split verdict —

| judge | robust gradient among non-matching valid | reading |
|---|---|---|
| Qwen2.5-7B | median slope -0.07 [-0.46,+0.34], Spearman ~0.00 | NO gradient: anchoring is a step at exact match |
| phi-4 | median slope -0.33 [-0.65,-0.11], trimmed -0.65 [-1.05,-0.31], Spearman -0.12 [-0.19,-0.06]; blind ~0 | small but real graded proximity effect, absent blind |

P-D3 (tercile monotonicity near>mid>far) is FALSIFIED for both judges (Qwen 3.41/2.93/3.53;
phi-4 6.81/6.32/6.71). The dominant effect remains the exact-match step: including distance-0
samples, the referenced slope is -3.38 [-3.95,-2.88] (Qwen) and -2.18 [-2.55,-1.78] (phi-4)
against blind ~0 — i.e. most of the "distance" effect IS the match/non-match margin.

**Reading.** For the weaker judge, correctness is replaced by exact proximity (a step); the
stronger judge adds a mild graded similarity term. Consistent with the k-grid's step-not-dial
finding and relevant to H-METHOD: for Qwen-7B-class judges, answer-space distance beyond
non-match does not matter, which weakly supports answer-anchoring over similarity-anchoring;
phi-4's gradient cautions against assuming that generalizes.

---

## Anchoring versus weakness (P-AW1, P-AW2) — registered 2026-08-26, CONFIRMED

**Registration.** `papers/analysis/anchor_vs_weakness.py`, committed before running. Filter: keep
only samples the judge itself blindly scored >= 7.0/10 (mean of the two blind rubric replicates),
then recompute the rotation same-sample deltas and rotation-arm margins on that subset.

**Outcome: both predictions confirmed.** Filtered gainer deltas stay positive with CIs excluding
zero at every judge size and both rubrics (rubric a: 1.5B +8.18 [+6.23,+9.68] n=9 items; 3B +9.13
[+8.39,+9.65] n=31; 7B +4.74 [+3.67,+5.87] n=33; 14B +3.09 [+2.40,+3.81] n=37), essentially
unchanged from the unfiltered values; losers stay negative; filtered margins exclude zero at all
four sizes (P-AW2 required three of four; the 1.5B margin rests on n=2 items and is noted as
fragile). Sample retention: 310/1564 (1.5B, whose blind scores are compressed), 1249/1564 (3B),
1391/1564 (7B), 1480/1564 (14B). Reading: the rotation flip is carried by samples the judge had
already demonstrably recognized as correct with no reference in sight — anchoring re-scores
answers the judge itself certified, so the effect is anchoring, not ignorance.

---

## Registration 5 (judge-coverage, pipeline17) — first judge landed 2026-08-26

**gemma-2-9b-it** (Google family; scored by the frozen estimators via `p17_coverage_analysis.py`):
P-X1 CONFIRMED — single-reference k>1 delta vs blind +1.43 [+1.15,+1.68] (n=53), the strongest
inversion of any judge tested so far, with the k=1 delta null (-0.05 [-0.14,+0.04]), matching the
boundary. P-X2 formally CONFIRMED — the M1-minus-single-reference contrast is -0.20 [-0.34,-0.05],
excluding zero — **but the level readout matters more than the contrast**: M1's own k>1 delta vs
blind is +1.23 [+0.94,+1.52]. For this judge, blind-then-reveal removes only ~14% of the harm
rather than all of it (against -0.05/+0.16 for Qwen-7B/phi-4). M2 sits at +0.61 [+0.48,+0.76],
between M1 and blind — the opposite ordering from phi-4. P-X3 holds directionally (trivially).
Provisional reading, pending the other two judges: the mitigation's magnitude is judge-dependent,
and the paper's "same outcome for both judges tested" phrasing will need revision once the
extension completes. Harness caveat on record: gemma-2 uses the registered system-role folding
path; blind and referenced conditions behave coherently under it.

---

## Similarity-vs-correctness 2x2 — blind naturalness audit FAILED (2026-08-27); judging blocked

The pinned audit criterion (simcorr_audit.py, committed before its first run) failed on
criterion (a): invalid-near and invalid-far candidates average 2.45 and 2.85 naturalness
against >= 3.0 required (valid classes: 4.25 / 4.22), with artificial-flag rates 87.5% / 65%
against 12.5% for both valid classes. Per the registered design, judging MUST NOT proceed.
Reading: the templated error constructions are detectably less natural than the valid
templates — the audit is discriminating on exactly the axis that would confound the 2x2
(a judge could down-score C for stiltedness rather than for not matching the reference).
Next step: revise the construction for uniform prose across all four classes (same
polish pipeline for every class, errors as plausible human slips), re-verify the oracle
assertions, and RE-run the same audit with the same pinned criterion. No judge scores of
any simcorr candidate exist, so this iteration cannot be selecting errors that fool the
target judge; it is selecting for auditor-rated naturalness only, as the design intends.

---

## Similarity-vs-correctness 2x2 — construction revision: 4 rounds, ALL FAILED the pinned audit (2026-08-27); judging remains blocked

**What was done.** Per the previous entry, the candidate construction in
`build_simcorr_candidates.py` was revised for prose uniformity and plausible-human-slip errors,
then re-audited with the UNCHANGED instrument and pinned criterion (`simcorr_audit.py`,
untouched). Four revision rounds were run; every round FAILED criterion (a) (all class means
>= 3.0/5). Criterion (b) (invalid-near flag excess <= 25 points over the other classes' max)
passed in every revision round. NO judge scores of any simcorr candidate exist — the audit gate
blocked judging throughout — so no revision could select errors against any judge; the loop
optimized auditor-rated naturalness only, as the prior entry sanctioned.

**Round history** (invalid_near, invalid_far as mean naturalness / artificial-flag rate;
valid classes stayed ~3.5-4.9 with 0-50% flags per family):

- round 0 (original, bald false equations): 2.45 / 87.5%, 2.85 / 65% — FAIL (a) and near-fail (b)
- round 1 (one shared prose pipeline; slips = dropped-constraint assertions, laundered
  transcription slips, small subtraction slips, early-terminated trial division, boundary
  misreads): 2.20 / 90%, 2.83 / 70% — FAIL (a); (b) +0.20
- round 2 (every displayed equation TRUE; fail only expensive-to-check constraints — digitsum
  restricted to q in {7,11}, goldbach to N with stealth composite complements (spf >= 7),
  divcount to ranges holding a stealth composite; subset reused an element; crt broke the
  mod-4/mod-3 congruence, never parity/last digit): 2.62 / 77.5%, 2.75 / 67.5% — FAIL (a); (b) +0.10
- round 3 (uniform addition chains, divcount invalids share the valid trial-division template,
  goldbach N >= 200, digitsum picks avoid primes/palindromes): 2.80 / 85%, 2.83 / 85% — best
  round — FAIL (a); (b) 0.00
- round 4 (carry-slip deltas of +-10, complements with spf >= 11, digitsum picks at +-1 mod q,
  crt invalids as verbatim valid-template clones with one off-by-one verification line):
  2.40 / 87.5%, 2.35 / 90.0% — FAIL (a); (b) -0.025. Final summary: valid_near 4.20 / 12.5%,
  valid_far 4.03 / 17.5%, invalid_near 2.40 / 87.5%, invalid_far 2.35 / 90.0%. VERDICT: FAIL.

**Reading.** The class-correlated TEMPLATE signal is gone: valid and invalid candidates now share
skeletons, closers, and hedging, all displayed arithmetic outside the single slip is true, and
criterion (b) — the detectability-gap criterion the design named as the revision trigger — passes
with margin in every revision round. What remains is correctness-verification: the auditor checks
the small-number arithmetic (2-digit congruences, 2-digit primality, 3-4-term sums, digit sums),
identifies the wrong answers, and scores detected wrongness as "deliberately manipulated"
regardless of prose (per-family means track exactly how cheaply the family's oracle can be
re-derived: divcount/crt worst, goldbach/digitsum best). On items this small, criterion (a) for
invalid classes measures the auditor's arithmetic reach, not writing naturalness; a construction
that passed it would need items whose validity the auditor cannot check — which this pool cannot
supply. Per the registered gate, judging MUST NOT proceed. Any relaxation or redesign of the
criterion (e.g., scoring naturalness conditional on blinded correctness, or moving to a pool with
harder-to-verify items) would be a NEW registration, recorded before any further run; none is
made here. Rounds are committed with this entry; the committed builder/tasks/audit are the
round-4 state.

---

## Registration 5 — second judge landed 2026-08-27: P-X1 and P-X2 are NOT CONFIRMED under the registered every-judge rule

**Mistral-7B-Instruct-v0.3** (Mistral family; frozen estimators): single-reference k>1 delta vs
blind is +0.02 [-0.04,+0.08] — a null. M1-minus-ref contrast -0.06 [-0.11,+0.00], also null; all
readouts null. A sanity diagnostic (unregistered) rules out a broken harness: Mistral's scores
are well-spread (sd 3.6-4.2), correlate with validity (+0.34/+0.37, comparable to gemma), and
its blind margin is ~0 as expected — but its referenced anchoring margin is only +1.04 points
against gemma's +4.32 and the original judges' +3.7-+5.0. Reading: Mistral-7B genuinely anchors
only mildly, and that mild margin does not convert into measurable best-of-64 inflation. It is
the first judge tested that is largely immune to the inversion.

**Registered scoring consequence.** P-X1 required the harm for EVERY new judge; Mistral's null
breaks it regardless of Qwen-14B's pending result, so **P-X1: NOT CONFIRMED** and likewise
**P-X2** (whose Mistral contrast crosses zero — vacuously, since there is no harm to remove).
The coverage extension has therefore done exactly what it was registered to do: the
single-reference harm and the fix's effect are both JUDGE-DEPENDENT. Emerging picture across
nine judges: strong harm + full fix (Qwen-7B, phi-4), strong harm + partial fix (gemma-2-9b),
mild-to-no harm (Mistral-7B), with the Qwen ladder and Llama-8B in the strong-harm class on the
earlier grid. The paper's universal claims stay intact only where registered (the k-step on the
six grid judges); the coverage rows get reported per judge, prediction failures included.

---

## Registration 5 — COMPLETE (all three judges, definitive full-set scoring, 2026-08-27)

Final verdicts from `p17_coverage_analysis.py` with all three judges present (this run is
definitive; the per-judge numbers quoted in the two provisional entries above came from
partial-set scorer runs whose shared bootstrap rng consumed draws in a different order, moving
CIs by up to ~0.02 — the frozen estimators and point estimates are unchanged):

| judge | ref k>1 vs blind | M1 k>1 vs blind | M1 minus ref (P-X2) | M2 k>1 | ref k=1 |
|---|---|---|---|---|---|
| gemma-2-9b-it | +1.43 [+1.15,+1.68] | +1.23 [+0.94,+1.52] | -0.20 [-0.34,-0.05] | +0.61 | -0.05 |
| Mistral-7B-v0.3 | +0.03 [-0.03,+0.08] | -0.04 [-0.08,-0.01] | -0.07 [-0.12,-0.02] | +0.09 | +0.08 |
| Qwen2.5-14B | +0.98 [+0.64,+1.33] | +0.23 [+0.10,+0.37] | -0.75 [-1.05,-0.46] | +0.30 | -0.30 |

**P-X1: NOT CONFIRMED** (required every judge; Mistral-7B is null — the first
anchoring-resistant judge, with a healthy score distribution and only a +1.0-point margin).
**P-X2: CONFIRMED** (the M1-minus-single-reference contrast is negative with CI excluding zero
for all three judges — including, at full-set precision, Mistral's small one).
**P-X3**: holds for gemma and Qwen-14B; fails vacuously for Mistral. **P-X4**: M2 sits between
M1 and blind for gemma, near-null for Mistral, +0.30 for 14B.

**Consolidated reading across nine judges.** The harm: strong for Qwen-1.5B..14B, Llama-8B,
phi-4, gemma-2-9b; absent for Mistral-7B. The fix: full removal (Qwen-7B, phi-4), near-full
with a small residual (Qwen-14B, +0.23), partial (gemma-2-9b, +1.23 residual), moot (Mistral).
Both the vulnerability and the mitigation are properties of the judge, not of the task setup —
the extension did what it was registered to do, and the paper's fix claims are rewritten
per-judge in v22, prediction failure included.

---

## Similarity-vs-correctness 2x2 — CLOSED WITHOUT JUDGING (collaborator decision, 2026-08-27)

After the pinned naturalness audit failed in five rounds (round 0 plus four registered
construction revisions) for the structural reason documented above — on small-number arithmetic
any careful auditor re-derives the answer and flags detected errors as deliberate, so the
criterion measures the auditor's arithmetic reach rather than prose naturalness — Sri decided to
SKIP the constructed experiment rather than weaken the criterion. P-SC1 and P-SC2 are therefore
never scored: not confirmed, not falsified — the experiment did not run, and no simcorr
candidate was ever judged. The similarity-over-correctness claim rests on the observational
evidence of the composition dose experiment (the lure finding: referenced judges select invalid
reference-look-alikes when no valid match exists), which is post hoc and labeled as such in the
paper. The committed construction harness (build_simcorr_candidates.py, simcorr_analysis.py,
simcorr_audit.py, runs/simcorr_tasks.jsonl) remains in the repo for a possible future
hard-domain version (MATH-style tasks where the audit criterion is passable); any such revival
is a new registration.

---

## CORRECTION (2026-08-27): Mistral-7B is NOT anchoring-resistant; its null is a score-resolution artifact

The two entries above describe Mistral-7B-Instruct-v0.3 as "the first anchoring-resistant judge."
**That interpretation is withdrawn.** A post-hoc diagnostic prompted by a collaborator's request to
double-check the result (`p17_mistral_diagnostic.py`, artifact `p17_mistral_diagnostic.json`) shows:

| judge | distinct score values | max dev. from integer | samples tied at max (ref) | anchoring margin | ref-minus-blind score shift |
|---|---|---|---|---|---|
| Mistral-7B-v0.3 | **11** | **0.000000** | **32.1** | +1.38 | +0.79 |
| gemma-2-9b-it | 4524 | 0.4999 | 1.0 | +5.32 | -3.13 |
| Qwen2.5-7B | 4456 | 0.4999 | 1.0 | +5.17 | -3.11 |
| Qwen2.5-14B | 3966 | 0.4999 | 1.0 | +4.06 | -1.19 |
| phi-4 | 4004 | 0.4997 | 1.0 | +4.20 | -2.13 |

Mistral emits scores that are EXACTLY integers: it places essentially all probability mass on one
score token, so the logprob-expected value collapses to that integer and only 11 distinct values
exist pool-wide (52.6% of referenced scores are exactly 10). Best-of-64 selection under this judge
therefore ties 32 of 64 samples at the maximum, against exactly 1 for every other judge, and the
frozen estimator breaks ties uniformly at random — so selection is close to a lottery over half the
pool and cannot express any scoring preference. Mistral DOES anchor, mildly and with the expected
k-trend (+1.15 at k=2, +1.10 at k=4, +2.07 at k=8; overall margin +1.38, referenced scores shifted
+0.79 points), but that preference cannot propagate into measurable inflation at this resolution.

**What changes.** The P-X1 verdict itself stands: Mistral's inflation delta is null, so the
every-judge prediction fails as scored. What is withdrawn is the CAUSAL READING. The correct
statement is that best-of-n inflation requires a judge whose scores can discriminate among
candidates, and a judge that emits coarse integers is not thereby safe: its anchoring is intact,
it is merely unable to act on it under this selection rule (and its selection quality suffers for
the same reason — only 51.6% of its top-tied group is valid, against 65-77% for the other judges).
A sharper decoding rule, a tie-break by any secondary signal, or a larger candidate pool could all
surface the anchoring this pool's estimator cannot see. Paper v23 states this and drops the
"immune judge" framing everywhere.

---

## Score-resolution screen (post hoc, unregistered, 2026-08-31)

Follow-up to the Mistral correction, prompted by Sri asking whether the real story is that a
judge's score diversity must be checked. Artifact `score_resolution_screen.json`, producer
`score_resolution_screen.py`. Blind condition, k>1 items, random-pick baseline 0.386:

| judge | distinct values | entropy (bits) | ties@max | selection accuracy | lift over random | anchoring margin |
|---|---|---|---|---|---|---|
| Mistral-7B-v0.3 | 11 | 2.27 | 17.8 | 0.564 | **+0.178** | +1.38 |
| gemma-2-9b-it | 2751 | 11.18 | 1.0 | 0.750 | +0.364 | +5.32 |
| Qwen2.5-7B | 2506 | 10.55 | 1.0 | 0.767 | +0.380 | +5.17 |
| Qwen2.5-14B | 2491 | 10.85 | 1.0 | 0.750 | +0.364 | +4.06 |
| phi-4 | 2511 | 10.82 | 1.0 | 0.850 | +0.464 | +4.20 |

Mistral captures less than half the selection value the other judges do (+0.18 against +0.36 to
+0.46 over random picking), for the mechanical reason that 11 distinct score values tie 18 of 64
samples at the maximum and the estimator breaks ties at random. So the judge is not "safe": it is
both anchored (margin +1.38) and a materially worse selector.

**Caveat stated in the producer and to be stated in the paper:** n = 5 judges, four clustered and
Mistral the lone outlier, so corr(distinct, lift) = +0.90 and corr(ties, lift) = -0.92 are driven
by a single leverage point and are ILLUSTRATIVE, not inferential. The claim rests on the
mechanism, which needs no correlation: coarse scores tie, ties are broken at random, random
selection cannot exceed the base rate. The practical recommendation follows from the mechanism
alone and costs nothing: before trusting any judge for best-of-n, look at the distribution of its
own scores on a pool it has already graded (distinct values, entropy, mean ties at the maximum).
A judge that emits a handful of integers cannot rank candidates however good its rubric
understanding is, and its apparent immunity to reference anchoring is an artifact of that muteness.
This complements companion A's certification audit, which needs a few dozen human labels; this
screen needs none.

---

## Robustness note (post hoc, 2026-08-31): order-variant set answers in the `subset` family

Found while planning a MACE extension. The `subset` family's answers are sets ("37,43"), and
the generator sometimes writes the same set in a different order ("43,37"). The loose
normalization used for reference-matching is order-SENSITIVE, so such a sample is classified
"valid but non-matching" when it is in fact the same answer as the reference. Scope and effect:
6 of 60 k>1 items in the k-stratified pool contain at least one order-variant of the reference.
Recomputing the k>1 anchoring margin with an order-invariant canonicalization (sort numeric
set elements) moves it from +5.17 to +5.05 (Qwen-7B), +4.20 to +4.47 (phi-4), and +5.32 to
+5.62 (gemma-2-9b) — small, and larger for two of three judges, consistent with the expected
direction: order-variants were inflating the non-matching group's mean and thereby SHRINKING
the measured margin. The published numbers are therefore conservative on this axis for two of
three judges and essentially unchanged for the third; no conclusion depends on it. Not
retro-fitted into the frozen registered artifacts, which stand as scored; disclosed here and in
the paper's limitations. (It also explains the diagnostic curiosity that nominal-k=1 items can
show several "distinct valid answers": those are order variants, 10 subset and 2 digitsum items.)

---

## Ministral-8B screen (P-MS1, P-MS2) — RESULT 2026-08-31: P-MS1 confirmed, P-MS2 falsified, and the screen itself shown INSUFFICIENT

Registered pre-run at commit `84994aa` (threshold: distinct >= 100 AND ties@max <= 3.0).

**As registered.** P-MS1 **CONFIRMED**: Ministral-8B-Instruct-2410 produces 1547 distinct score
values, entropy 9.91 bits, mean ties at maximum 1.0 — comfortably passing, and confirming that
Mistral-7B's exact-integer quantization is a checkpoint property, not a family property.
P-MS2 **FALSIFIED**: its anchoring margin is +0.32 [+0.22, +0.43], *lower* than Mistral-7B's
+1.38, not higher, and far below gemma-2-9b (+5.32), Qwen-7B (+5.17), phi-4 (+4.20).

**The finding that matters, and it is against our own recommendation.** A post-hoc diagnostic
(unregistered) shows Ministral-8B is not a functional judge at all on this pool:

| judge | score sd | IQR | r(score, validity) | selection accuracy | lift over random (0.386) |
|---|---|---|---|---|---|
| Ministral-8B | **0.55** | 0.56 | **+0.030** | **0.217** | **-0.170** |
| Mistral-7B | 4.12 | 6.00 | +0.334 | 0.516 | +0.130 |
| Qwen2.5-7B | 2.59 | 3.00 | +0.227 | 0.533 | +0.147 |
| phi-4 | 2.48 | 3.35 | +0.204 | 0.633 | +0.247 |
| gemma-2-9b | 2.65 | 2.63 | +0.259 | 0.650 | +0.264 |

Its 1547 distinct values are compressed into a range of sd 0.55 around a mean of 4.73, its scores
are essentially uncorrelated with validity (+0.03), and its best-of-64 pick is valid only 21.7% of
the time against a 38.6% random baseline — **worse than choosing at random**. Its near-zero
anchoring margin is therefore not resistance; it is a judge that discriminates on nothing at all.

**Consequence for the score-resolution screen proposed in v24.** The screen as registered
(distinct values, ties at maximum) is NECESSARY but NOT SUFFICIENT: it passes a judge that is
worse than random. It catches quantization (Mistral-7B) but not compression (Ministral-8B).
A cheap oracle-free repair is to add a score-SPREAD criterion (sd or IQR), which separates
Ministral (0.55 / 0.56) from every functional judge here (2.48-4.12 / 2.63-6.00) — but that
repair is post hoc and would itself need registering before use. The deeper conclusion is the
honest one: no label-free screen can certify that a judge's scores track truth, which is exactly
what companion A's human-label audit exists to measure. The resolution screen is a cheap
prerequisite, not a substitute for certification.

**Deviation disclosed.** The registration stated that a judge passing the screen earns the full
four-condition two-rubric grid. We are NOT spending that compute: the follow-up diagnostic shows
Ministral cannot select above chance, so its inflation and mitigation deltas would measure noise.
No further Ministral runs.

**Addendum to the robustness note (same session).** A second answer-classification pathway was
checked on the same k-stratified pool: samples containing no `\boxed{}` fall back to whole-reply
extraction and therefore cannot string-match the reference, so a valid sample whose true answer
IS the reference would be misclassified as non-matching. Prevalence on the k>1 items that carry
the mitigation and coverage results: 17 of 1483 oracle-valid samples (1.1%) lack a box, and of
those only 7 (0.5% of all valid samples) actually carry the reference answer in their closing
text. The effect is therefore negligible here, and its direction is the same conservative one as
the order-variant issue: it moves genuinely-matching samples into the non-matching group,
shrinking the measured margin. This is a different situation from the replication pool, whose
overall boxed-compliance rate is 0.616 and which the paper already bounds with the
extraction-friction tercile analysis; the k-stratified pool is 98.9% boxed among valid samples,
so the mitigation and judge-coverage numbers do not carry that caveat.

---

## Multi-valid DPO training-pressure experiment (GATE, P-DP1..P-DP3) — RESULT 2026-08-31

Registered pre-training at commit `9f83926` (design and predictions in `dpo_mv_pairs.py`,
frozen estimators in `dpo_mv_analysis.py`). Two LoRA-DPO arms on Llama-3.1-8B, identical
hyperparameters, differing only in which judge protocol built the preference pairs: the plain
single-reference Qwen-7B judge (**ref arm**) versus the same judge under blind-then-reveal
(**m1 arm**). Evaluation: n=8 per item from base and both arms on the k>1 training items and on
the 120 replication items as held-out; oracle accuracy plus frozen judge scores.

**Manipulation-check gate (registered, gates everything).**

| arm | own-judge score gain on train items | verdict |
|---|---|---|
| ref | **+1.76** [+1.47, +2.01] | **PASS** |
| m1  | **-1.04** [-1.36, -0.72] | **FAIL — arm void** |

The ref arm moved its own judge as required. The m1 arm did **not**: training against the
blind-then-reveal protocol produced a policy that its own protocol scores *lower* than base.
Per the registered rule the m1 arm is void, so **every contrast that uses m1 as comparator is
uninterpretable as evidence about the mitigation**, including P-DP2's and P-DP3's registered
forms. This is a null about the training setup, not about the fix.

**What the surviving (gated) arm shows, and it is the paper's most consequential number.**
On the ref arm alone against base, the wedge between scoreboard and truth is
**+4.13** [+3.50, +4.78]: its own judge's score rose **+1.76 points** while its true accuracy
*fell* from 0.412 to 0.175 (**-0.237**), and its held-out accuracy fell **-0.228**
[-0.269, -0.189]. A model trained against a reference-showing judge on multi-valid tasks
therefore became substantially worse at the task while its judge liked it substantially more.
This is the selection-time inversion reproduced under training pressure, on the arm that
passed its own gate.

**P-DP1 (parroting): FALSIFIED.** We predicted the ref arm would emit the exact reference answer
*more* often than the m1 arm. The paired difference is **-0.037** [-0.067, -0.013] — it emits it
*less*, and its own match rate fell (-0.040) relative to base. So the degradation is not
reference-copying. Consistent with companion A, whose analogous wedge prediction on unique-answer
math also failed: a corrupted preference signal damages the policy rather than teaching it to
imitate the key. What the ref arm learned is something its judge rewards that is neither
correctness nor key-matching; the registration's disclosed candidate, verbosity, is consistent
with the generations (1492 -> 2476 mean characters) but is not established here.

**P-DP2 / P-DP3 as registered: not scorable.** Both are ref-versus-m1 contrasts and the m1 arm is
void. Reported for completeness only: P-DP2 delta +2.66 [+2.07, +3.27], P-DP3 delta +0.18
[+0.14, +0.22], both nominally in the predicted direction. We do **not** claim from this
experiment that blind-then-reveal protects a trained policy; the m1 arm may simply have trained
less effectively, and its lower accuracy loss (-0.049 held-out vs the ref arm's -0.228) is
confounded with that failure. A rerun with hyperparameters tuned so the m1 arm passes its gate is
the honest way to test the mitigation under training.
