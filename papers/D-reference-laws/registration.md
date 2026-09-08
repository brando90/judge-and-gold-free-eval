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

---

## Worked-reference arm (E1) and method rotation (H-METHOD) — RESULT 2026-08-31

Registered pre-data at commit `1328c87` (design, estimators, P-W1..P-W3). Both re-judge the
frozen k-stratified pool; nothing generated or trained. Judges Qwen2.5-7B and phi-4, rubrics a
and b, conditions `refsol` (worked derivation, route A) and `refsol2` (worked derivation, route
B, same final answer).

**E1 — a worked reference anchors LESS than a bare answer (P-W1 confirmed).** Every result in
the paper until now showed the judge a bare answer string; practitioners show worked solutions.
Replacing the bare answer with a short derivation that reaches the same answer:

| judge | margin, bare ref | margin, worked ref | difference | inflation, bare | inflation, worked | difference |
|---|---|---|---|---|---|---|
| Qwen2.5-7B | +5.17 | +3.73 | **-1.44** [-1.99,-0.92] | +1.50 | +1.08 | **-0.42** [-0.69,-0.16] |
| phi-4 | +4.20 | +3.67 | **-0.53** [-0.90,-0.11] | +1.07 | +0.77 | **-0.30** [-0.48,-0.12] |

P-W1 predicted a difference without predicting direction; the direction is that a longer,
more informative reference anchors *less*, contradicting the "more surface to match" intuition
recorded as plausible at registration. The reduction is real but partial: inflation stays firmly
positive (+1.08, +0.77), so a worked reference is a milder form of the same lever, not a safe one.

**H-METHOD — method anchoring exists but is one to two orders of magnitude smaller than answer
anchoring (P-W2 falsified as stated; its substance supported).** On the 15 k=1 items every valid
sample carries the same final answer, so rotating the reference between derivation routes varies
method alone. Paired same-sample deltas (refsol2 minus refsol):

| judge | rubric | overall shift | route-A samples | route-B samples | differential |
|---|---|---|---|---|---|
| Qwen-7B | a | -0.32 [-0.56,-0.08] | -0.62 | -0.18 | **-0.44** |
| Qwen-7B | b | -0.40 [-0.69,-0.15] | -0.40 | -0.37 | -0.03 |
| phi-4 | a | -0.02 [-0.04,+0.00] | -0.01 | -0.03 | +0.02 |
| phi-4 | b | -0.02 [-0.04,-0.01] | -0.02 | -0.02 | -0.00 |

P-W2 predicted the paired delta's CI would contain zero. It does not (three of four cells exclude
zero), so **P-W2 is falsified as literally stated**. But the decomposition matters more than the
verdict: an *overall* shift means the second derivation makes the judge marginally stingier about
everything, which is calibration, not anchoring. True method anchoring must appear as a
*differential* — samples whose own route matches the shown one faring better. That differential
appears in exactly **one of four** judge-by-rubric cells (Qwen rubric a, -0.44) and is absent in
the other three. Against the paper's answer-rotation result of up to **±9.5 points**, method
effects are 20x to 400x smaller.

P-W3 (positive control) holds: the same machinery on the same items detects the standing
reference-minus-blind difference at -4.02 (Qwen) and -3.03 (phi-4), so the near-nulls above are
not an insensitive instrument.

**Reading.** The judge anchors overwhelmingly on the *answer*, not the derivation route. This was
the collaborator's hypothesis; it survives in substance while its strict form fails. Practical
consequence: worked-solution references are safer than bare answers but still inflationary, and
the paper's warning remains scoped to answer multiplicity rather than extending to
unique-answer tasks with differing solution methods. Caveat carried from the registration: the
route classifier is a heuristic token-Jaccard match with a small mean similarity margin (0.032),
so the differential readout is weakly identified; the overall-shift readout is classifier-free.

---

## Frontier-judge anchoring check (P-F1..P-F3) — RESULT 2026-08-31

Registered pre-data (`frontier_judge.py`, committed before any frontier score existed). Frontier
judge via the CLI session path, rubric-a prompt text taken verbatim from `bon_rubrics.RUBRIC_TIES`
so the prompt matches the open judges exactly; 37 k>1 items where matching and non-matching
oracle-valid samples coexist (the same population the open judges' margins use); 660 calls,
0 unparseable.

| condition | matching valid | non-matching valid | margin |
|---|---|---|---|
| blind | 7.83 | **7.85** | **+0.31** [-0.62, +1.30] |
| referenced | 9.83 | **2.32** | **+7.49** [+6.62, +8.22] |

**P-F1 CONFIRMED, emphatically.** The frontier judge anchors. **P-F2 holds** and the control is
about as clean as this design can produce: blind, it scores matching and non-matching valid
answers 7.83 and 7.85, a 0.02 difference. The rate statement is the one to quote: shown a
reference, **82.5% of genuinely correct non-matching answers receive a failing score (<= 3/10)**,
against **19.6%** for the same answers judged blind. Scale does not rescue the failure; the
paper's finding is not confined to small open judges.

**P-F3 FAILS, and its failure is NOT interpretable.** P-F3 predicted a margin smaller than the
open judges' (+4.06 to +5.32), continuing the capability trend; the observed +7.49 is larger.
But the two are measured with different score functions: the vLLM judges use the
logprob-EXPECTED value over tokens 0..10, which is pulled toward the middle whenever the judge
spreads mass across tokens, while the CLI path returns a SAMPLED INTEGER that can sit at the
extremes. A hard-integer judge can therefore express a wider margin than a smoothed one for the
same underlying preference. **We claim only that the frontier judge anchors, with a clean blind
control, and explicitly do NOT claim it anchors more than the open judges.** Establishing the
cross-scale magnitude comparison would require running the frontier judge through a logprob path,
which the free CLI does not offer.

**Also disclosed, per the pre-registered design note:** no inflation figure is computed for this
judge. Its 11-value integer scores would tie massively under best-of-64, and by this paper's own
score-resolution finding the resulting inflation estimate would measure the tie-break, not the
judge. The margin, a mean over many samples, is well resolved and is the only readout taken.

**Parser audit and correction (2026-08-31, same day as the run).** The frontier score parser
originally took the FIRST integer 0..10 in the reply. An audit of all 660 raw replies found 659
are a bare integer (mean reply length 2 characters) and exactly one shows arithmetic before its
verdict (`3 + 13 + 44 = 60. Correct.\n\n**10**`), which the first-integer rule misparsed as 3
instead of 10. The parser is corrected to take the LAST integer, the artifact regenerated, and
the effect is confined to the blind matching mean: 7.83 -> 7.88. Every headline figure is
unchanged — referenced margin +7.49, blind margin still null, 82.5% versus 19.6% failing rates
identical — and the paper's blind row is updated to the corrected values. Also verified in the
same audit: the frontier prompt is constructed from the same `RUBRIC_TIES[("ref","a")]` system
text and the same Problem / Reference answer / Candidate solution / "Score:" body as
`bon_judge.py`, so only the judge and the score function differ. One structural difference
remains inherent to the CLI path and is noted here: the open judges receive system and user as
separate chat-template turns, while the CLI receives them concatenated.

---

## Independent verification pass (2026-08-31), at the collaborator's request

Every result from this session was recomputed from raw files by scripts that deliberately do not
import or reuse the original producers. Outcomes:

**DPO training pressure — all figures reproduce exactly.** Independent recompute: accuracy
train 0.4125 (base) / 0.1750 (ref arm) / 0.3312 (m1 arm); held-out 0.4573 / 0.2292 / 0.4083;
GATE ref +1.758, GATE m1 -1.044; wedge = judge gain 1.758 minus 10 x accuracy gain (-0.2375)
= +4.133; match rates 0.0708 / 0.0312 / 0.0688 giving P-DP1's -0.0375. All match the reported
values to three decimals.

**E1 / H-METHOD — all figures reproduce, and the mechanism checks pass.** The check that mattered
most was whether the new conditions were real rather than silently identical: `ref` vs `refsol`
differ on 75/75 items (mean |score difference| 0.807), `refsol` vs `refsol2` on 75/75 (0.357), so
the worked references were genuinely loaded and the two derivation routes genuinely differ. The
worked-reference file passes its own invariants independently: 0/75 items have identical
derivations, 75/75 have both derivations boxing the item's own reference answer. Margins
reproduce (ref +5.169, refsol +3.734) as does the H-METHOD paired delta (-0.323 [-0.571,-0.090]).

**Frontier judge — one real bug found, fixed, immaterial.** See the parser audit above: 1 of 660
replies misparsed, blind matching mean 7.83 -> 7.88, no headline figure affected. Prompt
construction verified equivalent to `bon_judge.py`; the system/user concatenation difference
inherent to the CLI path is disclosed.

One bug found across four experiments, in the newest and least-exercised code path, with no
effect on any conclusion.

---

## DPO rerun (GATE-R, P-DP1r..P-DP3r) — REGISTERED 2026-08-31, before the rerun

**Why a rerun, and what changed.** In the first run the protected (m1) arm failed its
manipulation-check gate (-1.04), so its predictions were void and no claim could be made about
whether blind-then-reveal protects a trained policy. Diagnosis, stated before rerunning: both
arms trained at 4 epochs / lr 2e-5 and both degenerated toward verbosity (mean generation length
1492 -> 2476 for ref, -> 3840 for m1), and the m1 arm's own judge scores blind-first, so a
degenerate policy is penalised by it rather than rewarded. The reference arm's judge, which
rewards key-resemblance, tolerated the same degeneration. **The hyperparameters are therefore
changed for both arms symmetrically: 1 epoch, lr 5e-6** (paper A's registered DPO settings),
holding every other element identical to the first run: same pools, same pair-construction rule,
same 480 pairs per arm, same evaluation, same frozen estimators.

**Disclosure.** Changing hyperparameters after observing a gate failure is a deviation and is
recorded as one. It is legitimate only because the gate is a *precondition* on the manipulation,
not an outcome measure: the gate asks whether training moved the judge it trained against, and an
arm that fails it has not performed the manipulation the experiment is about. The first run's
outcome stands on the record in full, including the reference arm's confirmed wedge, and the
rerun's numbers will be reported as a separate, second experiment rather than replacing it.

**Predictions (identical in substance to the first run, restated for the new settings).**
GATE-R: each arm raises the score its OWN training judge assigns to its train-item generations
  relative to base, CI excluding zero. An arm failing this is void again.
P-DP1r: the reference arm's reference-match rate gain exceeds the m1 arm's.
  (Prior evidence: FALSIFIED in run 1, -0.037. Restated unchanged so the rerun is a genuine test.)
P-DP2r: the reference arm's scoreboard-versus-truth wedge exceeds the m1 arm's, CI excluding zero.
P-DP3r: the m1 arm's held-out accuracy change is no worse than the reference arm's.
Only if BOTH arms pass GATE-R do P-DP2r and P-DP3r become scorable as statements about the
mitigation; otherwise they are reported as void exactly as in run 1.

---

## MACE feasibility audit (2026-08-31) — the Math domain has an EXACT oracle, and the earlier objection is withdrawn

Planning notes above argued that extending to MACE (arXiv 2602.07842) would trade this paper's
exact programmatic oracle for Wikidata list-membership, importing the incompleteness that
corrupted the RewardBench-Ties labels. **That objection is correct for MACE's five entity domains
and wrong for its Math domain**, and the difference is decisive.

**Dataset as released** (`fzzh/MACE`, six HF configs): 12,000 questions, exactly 3,000 each at
k = 1, 2, 4, 6, matching the paper. (A first pass here mis-read the release as 2,000 award-only
k=1 items; that was an error of loading only the default config plus a parsing bug, corrected the
same session.)

**Exactness audit of MACE-Math, computed rather than trusted.** Its 2,000 questions are of five
computable kinds, each of the form "Name a {kind} number between {lo} and {hi}". We enumerated
the true answer set for every question and compared it to the shipped list:

| kind | audit against computed truth | k-distribution |
|---|---|---|
| prime | 400/400 exact | 100 each at k=1,2,4,6 |
| square | 400/400 exact | 100 each |
| cube | 400/400 exact | 100 each |
| fibonacci | 400/400 exact | 100 each |
| triangular | 400/400 exact | 100 each |

**2000/2000 (100%) of MACE-Math questions have answer lists that are exactly correct and exactly
complete.** No adjudication layer is needed, and validity can be decided for ANY candidate answer
by direct computation, exactly as on our own constraint pools.

**Consequence for the extension plan.** MACE-Math gives simultaneously what no substrate used so
far provides at once: third-party questions with third-party ground truth (answering the
monoculture objection that every constructive result to date rests on pools we designed), an
exact oracle (no Wikidata incompleteness), controlled k by construction, and natural-language
phrasing. It is therefore the right MACE subset to run first, and the entity domains become an
optional realism extension that would need the adjudication machinery. The remaining feasibility
risk is unchanged and still to be gated: realized answer diversity in the sampled pools, since
this paper's own measurement shows realized distinct valid answers plateau near 4-5 regardless of
nominal k.

**MACE entity-domain completeness audit (2026-08-31, zero GPU).** The Math domain audits exact by
computation, but the five entity domains rest on Wikidata list-membership. We audited them before
committing compute by asking an independent model to enumerate the FULL answer set for 12
multi-valid questions per domain, without showing it the shipped list, and measuring how often it
names an answer the list omits:

| domain | items | shipped answers | model named | covered by list | absent from list | rate |
|---|---|---|---|---|---|---|
| River | 12 | 52 | 44 | 43 | 1 | **2.3%** |
| Language | 12 | 56 | 37 | 34 | 3 | **8.1%** |
| Region | 12 | 40 | 39 | 27 | 12 | 30.8% |
| Office | 12 | 48 | 21 | 14 | 7 | 33.3% |
| Award | 12 | 50 | 23 | 13 | 10 | 43.5% |

**Verdict: River and Language pass; Region, Office and Award do not.** The usable pair gives what
the Math domain cannot: a NON-mathematical, natural-language, third-party substrate with
controlled k and answer lists that survive an independent completeness check. The three failing
domains would need the adjudication machinery built for the Ties pool, and are excluded from the
planned extension rather than patched.

Two caveats recorded with the number. First, an "absent" answer can mean the shipped list is
incomplete OR that the auditing model hallucinated, and the failing domains (people, offices,
administrative divisions) are exactly where hallucination is most likely, so the true
incompleteness rates are upper bounds. Second, the direction of any real incompleteness is the
familiar conservative one: a genuinely correct answer missing from the list is scored invalid,
and such answers fall on the NON-matching side, shrinking the measured margin rather than
inflating it. The gate is therefore set conservatively on purpose: we exclude domains whose noise
we cannot bound cheaply, not domains we know to be wrong.

**Planned MACE substrate, following this audit:** Math (exact oracle, arithmetic) as the
label-noise control, plus River and Language (audited, non-mathematical) as the domain-diversity
arm. Running both allows any divergence between them to be attributed to substrate rather than
to oracle quality.

---

## HYPOTHESIS recorded pre-data (2026-08-31): the harm attaches to EXEMPLARS, not to references

Raised by the collaborator while discussing code and SQL substrates. Recorded here, untested, so
that a later test has a timestamped prediction rather than a post-hoc story.

**The observation that prompts it.** Companion A reports that a reference *helps* on code above a
capability gate. Paper D reports that a reference *harms* when many answers are valid. Code has
many valid implementations, so by D's rule it should be a harm case. Checking our own harness
resolves the tension: A's code condition shows the judge the **test assertions**
(`example_test`), not a canonical solution. That is a SPECIFICATION, not an exemplar. A
specification cannot be anchored on, because there is nothing to match; consulting it *is*
verification. An exemplar invites matching.

**The hypothesis.** The paper currently states the boundary in terms of the task's answer
structure: a reference helps when the answer is effectively unique. The deeper statement may be
that **anchoring is caused by being shown one valid exemplar**, and answer multiplicity governs
only how much that costs. On this reading, unique-answer tasks are safe not because uniqueness is
protective in itself, but because with a single valid answer the exemplar IS the specification, so
matching and verifying coincide. Every result in this paper is consistent with both statements,
because every reference we have shown has been an exemplar.

**The discriminating experiment (not run, not registered as a prediction yet).** On the SAME code
tasks, three conditions: (1) canonical solution as reference (exemplar), (2) test assertions as
reference (specification, already run in companion A), (3) blind. If (1) anchors and (2) does not,
the harm is a property of the reference's TYPE rather than of the task's answer structure, and the
paper's rule should be restated accordingly. If (1) also fails to anchor, the exemplar hypothesis
is wrong and answer-structure remains the right framing. Code is additionally the untested regime
noted below.

**Regime note, also recorded for the record.** A conversational recommendation earlier in this
session claimed SQL and code test "method multiplicity, which we showed barely matters." That was
wrong and is retracted here. H-METHOD held a *separable boxed answer* fixed and varied the
derivation; in code and SQL the artifact IS the answer and no separable answer token exists, so
the judge must compare whole artifacts. That is a third regime, untested by anything in this
paper, and it is where most deployment-relevant judging (code review, query grading, patch
assessment) actually sits. The paper's own text was never affected: its H-METHOD section is
scoped to "two correct solutions taking different routes to one answer," which is accurate.

**MBPP canonical-solution verification (2026-08-31), before building the exemplar arm.** The
planned code experiment shows the judge a canonical solution as an exemplar reference. Verified
rather than assumed: MBPP's canonical solutions were executed against OUR test field, which is
the EvalPlus-augmented suite the pool's oracle labels use. **60 of 378 canonical solutions FAIL
that suite** (41 AssertionError, 6 timeout, plus IndexError/RecursionError/ZeroDivisionError
cases), because MBPP's reference code was written against the weaker original assertions. A
parallel first pass flagged 61; a serial recheck at a 30s timeout confirmed 60, so one was a
timeout artifact and the count is execution-stable. Only 7 fail the `example_test` specification
the judge is currently shown, which is why the existing specification arm was unaffected.
**Consequence: the exemplar arm is restricted to the 318 items whose canonical solution passes
our own oracle.** Showing a reference our oracle scores invalid would be a different and
confounded manipulation, not the exemplar condition.

---

## DPO rerun (GATE-R) — RESULT 2026-08-31: BOTH arms void. The mitigation-under-training question is UNRESOLVED.

Registered pre-run (1 epoch, lr 5e-6, symmetric, everything else identical to run 1).

| arm | own-judge score gain vs base | verdict |
|---|---|---|
| ref | +0.074 [-0.150, +0.302] | **FAIL — void** |
| m1  | -0.014 [-0.251, +0.222] | **FAIL — void** |

Neither arm moved the judge it trained against, so under the registered rule both are void and
P-DP1r/P-DP2r/P-DP3r are unscorable. Supporting evidence that the settings were simply too
gentle: train accuracy 0.375 (base) / 0.404 (ref) / 0.367 (m1), held-out 0.472 / 0.492 / 0.473,
and mean generation length 1499 / 1488 / 1527 characters — essentially unchanged from base on
every axis, against run 1's 1492 / 2476 / 3840.

**What the two runs jointly establish, and what they do not.** They bracket the manipulation
rather than resolving it. Run 1 (4 epochs, lr 2e-5) OVER-trained: both arms degenerated toward
verbosity, the reference arm passed its gate, and on that single gated arm the
scoreboard-versus-truth wedge was +4.13 [+3.50, +4.78] with true accuracy falling 0.412 -> 0.175.
Run 2 (1 epoch, lr 5e-6) UNDER-trained: nothing moved at all. The reference arm's wedge therefore
remains this paper's only gated observation of training pressure, and it stands; the question of
whether blind-then-reveal PROTECTS a trained policy remains **open**, because no run has yet
produced a protected arm that passed its own manipulation check.

**Stopping rule, adopted now rather than after another attempt.** A third hyperparameter setting
chosen after seeing two failures would be tuning toward a passing gate, which is the failure mode
this paper criticises judges for. Any third run must therefore be registered in advance with a
single pre-committed setting and a pre-committed stopping rule: if that arm also fails its gate,
the mitigation-under-training question is reported as unresolved in the paper and not attempted
again. Absent such a run, the paper states the question as open.

---

## MACE extension (P-MC1..P-MC3) — RESULT 2026-08-31: all three confirmed. The central claim holds on third-party, non-mathematical tasks.

Registered pre-generation (`build_mace_tasks.py`); scored by `mace_analysis.py`, written before
any MACE score existed, with the frozen `bon_analysis` estimator. Pool: 300 items, overall pass
rate 0.497. Non-math = River + Language (the two entity domains that passed the pre-run
completeness audit); Math = the exact-oracle control.

**P-MC1 (the k-step on non-mathematical tasks): CONFIRMED for both judges**, and the levels show
the complete inversion rather than only the step:

| judge | domain | k=1 delta | k>1 delta | step |
|---|---|---|---|---|
| Qwen2.5-7B | non-math | **-0.973** [-1.295,-0.670] | **+1.330** [+0.791,+1.794] | **+2.303** [+1.817,+2.841] |
| phi-4 | non-math | **-0.574** [-0.845,-0.326] | **+0.552** [+0.238,+0.876] | **+1.126** [+0.805,+1.433] |

At k=1 the reference HELPS (negative delta, CI excluding zero for both judges); at k>1 it HARMS
(positive, CI excluding zero). This is the paper's boundary reproduced end to end on
natural-language factual questions written by someone else, with answer cardinality fixed by
their construction rather than ours.

Per domain, the step holds separately: River +1.667 [+0.924,+2.479] and +1.084 [+0.543,+1.638];
Language +2.780 [+2.179,+3.467] and +1.145 [+0.805,+1.538].

**P-MC2 (margins): CONFIRMED.** Referenced anchoring margins at k>1 are +6.44 [+5.93,+6.97]
(Qwen-7B) and +5.86 [+5.40,+6.28] (phi-4) — the LARGEST margins measured on any pool in this
paper — against blind margins of -0.64 [-1.38,+0.14] and -0.80 [-1.44,-0.15]. Note phi-4's blind
margin excludes zero on the NEGATIVE side, a mild blind preference against reference-matching
answers, which makes the referenced margin's reversal starker rather than weaker.

**P-MC3 (substrate control): CONFIRMED.** The MACE-Math step is +0.748 [+0.420,+1.045] and
+0.937 [+0.715,+1.160], the same sign as the non-math step. Since Math carries an exact oracle
verified 2000/2000 against computed truth while the entity domains carry list-membership, the
agreement means the entity oracle's residual noise is not driving the result. The non-math effect
is if anything LARGER than the math effect for Qwen-7B (+2.30 against +0.75).

**What this settles.** Before this run every constructive result in the paper rested on task
pools of our own construction, and the sharpest available objection was that we built the
conditions that produce the effect. That objection is now answered: the inversion, the k=1
benefit, the k>1 harm, and the anchoring margin all reproduce on a third-party benchmark, in
natural language, in two non-mathematical domains, with an internal exact-oracle control showing
the entity labels are not responsible.

---

## Code exemplar-vs-specification experiment (P-EX1..P-EX3) — RESULT 2026-09-01: P-EX1 FALSIFIED. Where the artifact IS the answer, the exemplar does not inflate.

Registered pre-data (`build_code_exemplar.py`); 317 MBPP items whose canonical solution passes
our EvalPlus-augmented oracle, three conditions on identical samples and judges (blind and
specification from companion A's frozen runs; exemplar new, under a truthfully-worded rubric).
Note on n: the companion-A blind/specification score files were produced with the registered
pass-rate band filter, so paired contrasts run on the 58 in-band items all conditions share.

**P-EX1 (exemplar inflates where specification does not): FALSIFIED.** Paired inflation deltas
versus blind on the same items:

| judge | specification vs blind | exemplar vs blind | exemplar minus specification |
|---|---|---|---|
| Qwen2.5-7B | -0.535 [-0.811,-0.244] | -0.342 [-0.737,+0.041] | +0.193 [-0.112,+0.475] |
| Qwen2.5-14B | -0.658 [-0.965,-0.373] | -0.567 [-0.827,-0.287] | +0.091 [-0.102,+0.277] |

The exemplar does NOT inflate: its delta is negative (14B, CI excluding zero) or null (7B), and
the exemplar-minus-specification contrast crosses zero for both judges. On code, showing the
judge one valid solution behaves like showing it the test suite: both REDUCE inflation relative
to blind, the exemplar slightly less effectively.

**P-EX2 (similarity anchoring): CONFIRMED, small.** On the same 58 items, the correlation
between a valid sample's token similarity to the canonical solution and its judge score is
+0.164 [+0.072,+0.256] (7B) and +0.084 [-0.005,+0.168] (14B) under the exemplar, against
-0.061 and -0.070 blind. A real but mild tilt toward reference-resembling code — present, and
far too weak to convert into inflation. **P-EX3** (smaller than the math-pool anchoring) holds
by an order of magnitude.

**Reading, and the scope boundary it draws.** The exemplar hypothesis survives in its
conditional form and the paper's warning gains a sharp edge: anchoring requires a separable
ANSWER TOKEN to match on. On short-answer tasks the boxed answer gives the judge a cheap
equality check, and the harm is large (margins +4 to +6.4, inflation +1.1 to +1.5). On code,
where the artifact IS the answer and no such token exists, the judge cannot do the cheap match;
only a weak similarity tilt remains, and the reference — exemplar or specification — helps.
This CONFIRMS companion A's certification of references on code rather than contradicting it,
and it bounds paper D's warning to tasks with separable answers: precisely the boundary a
practitioner needs. It also retro-justifies the H-METHOD result: method-space variation never
mattered because the judge was never matching on structure, only on the answer token.

**Robustness of the code result (2026-09-01, at the collaborator's request).** Two checks, both
post hoc:

(1) *Is the null trivial because valid solutions are near-clones of the canonical reference?*
No — the opposite. Across 14,342 oracle-valid samples there are ZERO exact text matches with the
canonical solution; mean token-Jaccard similarity is 0.227 (median 0.217), and 99.8% of valid
samples sit below 0.5 similarity. The judge saw genuinely different implementations of the same
behavior and did not punish the difference. There was maximal room for anchoring, and it did not
appear.

(2) *Does the math pools' worst case — the dose-0 lure, where nothing matches the key and the
judge is drawn to wrong look-alikes — appear on code?* No; it INVERTS. Code is effectively
all-dose-0 (no sample ever string-matches a whole canonical solution), which on the constraint
pools was where the referenced judge's valid-pick rate collapsed to 0.14-0.21 against 0.72-0.79
blind. On code the exemplar-shown judge picks valid samples MORE often than blind (0.759 vs
0.586 at 7B; 0.828 vs 0.655 at 14B), and among invalid samples the similarity-to-canonical
correlation with score is ~0 (+0.04/+0.08 vs -0.09/-0.08 blind) — no lure. The cheap
string-equality shortcut that powers both the matching bonus and the lure simply has no
purchase when the reference is a whole artifact; what remains of the reference's influence is
informational, and it improves selection.

---

## DPO third and FINAL attempt (GATE-F, P-DPF1..P-DPF3) — REGISTERED 2026-09-01, before the run

**Standing under the stopping rule.** The rule adopted after run 2 permits exactly one further
attempt, with a single pre-committed setting, and binds the outcome: if the protected (m1) arm
fails its manipulation-check gate again, the mitigation-under-training question is reported
UNRESOLVED in the paper and not attempted again. This entry is that single registration. No
further hyperparameter choices are permitted after this commit, whatever the outcome.

**The one setting: 2 epochs, lr 1e-5, beta 0.1, symmetric across arms.** Chosen as the geometric
midpoint of the two failed brackets (run 1: 4 epochs / 2e-5, over-trained into degeneration;
run 2: 1 epoch / 5e-6, moved nothing), fixed here before any training. Everything else identical
to runs 1 and 2: same Llama-3.1-8B policy, same 480 preference pairs per arm (ref-judge vs
m1-judge rankings, already built), same eval protocol (n=8 per item, train + 120 held-out),
same frozen estimators (`dpo_mv_analysis.py` machinery, applied to a new output directory).

**Predictions.**
GATE-F: each arm raises its OWN training judge's score on train-item generations vs base, CI
  excluding zero. An arm failing this is void. If the m1 arm is void, the question is closed as
  unresolved per the stopping rule.
P-DPF1: conditional on both arms passing, the ref arm's scoreboard-versus-truth wedge exceeds
  the m1 arm's, CI excluding zero (the run-1 gated observation predicts this direction).
P-DPF2: conditional on both arms passing, the m1 arm's held-out true-accuracy change is no worse
  than the ref arm's (directional).
P-DPF3 (parroting, restated a third time unchanged despite two prior falsifications, so the test
  stays genuine): the ref arm's reference-match rate gain exceeds the m1 arm's.

---

## Blind-judge attribution arm for DPO run 3 (GATE-B, P-DPB1..P-DPB2) — REGISTERED 2026-09-07, before the run

**Why.** External review (2026-09-07) identified the training experiment's attribution gap:
with no successful matched control, the ref arm's wedge shows that training against a
reference-showing judge is exploitable, not that the degradation is caused specifically by
reference conditioning rather than by generic overoptimization against an imperfect judge.
This addendum adds the missing control arm to the already-registered GATE-F run (commit
d33614e): a BLIND-judge DPO arm, identical in everything except that its preference pairs
come from the Qwen-7B judge's blind (noref rubric-a) scores of the same frozen k>1 pool.

**Standing under the stopping rule.** This adds an ARM, not a setting: the single
pre-committed GATE-F setting (2 epochs, lr 1e-5, beta 0.1) is unchanged and applies
symmetrically to all three arms. The stopping rule binds the protected (m1) arm's question
exactly as registered in d33614e; the blind arm's gate failing voids only the blind-arm
predictions, never reopens hyperparameters.

**Mechanics (pinned).** Pairs: dpo_mv_pairs.py --arm blind (same pairing rule: up to 8
pairs/item, min escore gap 2.0, seed 0, k>1 items only), from
runs/bon_scores_kstrat/synthk__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl. The ref and m1
arms REUSE the already-built pairs (runs/dpo_mv/pairs_ref.jsonl, pairs_m1.jsonl) copied
into runs/dpo_mv3. Training, eval (n=8, train + 120 held-out), oracle, and judging exactly
as pipeline18, output under runs/dpo_mv3. Estimators: papers/analysis/dpo_mv3_analysis.py,
an exact mirror of the frozen dpo_mv_analysis.py extended to the third arm, committed with
this addendum BEFORE any training.

**Predictions.**
GATE-B: the blind arm raises the BLIND judge's rubric-b score on its train-item generations
  vs base, 95% item-bootstrap CI excluding zero. Failing voids P-DPB1/P-DPB2.
P-DPB1 (attribution): conditional on ref + blind gates, the ref arm's wedge
  (single-reference judge-score gain minus 10x oracle-accuracy gain, train) exceeds the
  blind arm's, CI excluding zero. This is the review's demanded comparison: if it fails,
  the ref-arm degradation is NOT attributable to reference conditioning specifically, and
  the paper must say so.
P-DPB2 (directional): the blind arm's train-item true-accuracy change is no worse than the
  ref arm's.
Disclosed exploratory readout (no registration weight): wedge per point of own-judge score
gain, as a matched-reward normalization; exact reward matching cannot be guaranteed ex ante.

---

## DPO run 3 OUTCOME (GATE-F + blind arm) — recorded 2026-09-07, after the run

GATE-F verdicts at the single pre-committed setting (2 epochs, lr 1e-5, beta 0.1):
- ref arm: own-judge gain +0.343 [+0.101, +0.572] — PASS.
- m1 arm: own-judge gain -0.992 [-1.235, -0.742] — FAIL, third and final failure.
- blind arm (addendum): own-judge gain -2.432 [-2.779, -2.120] — FAIL.

**The stopping rule is hereby engaged: the mitigation-under-training question is closed as
UNRESOLVED, permanently.** No further training attempts. The blind arm's gate failure also
voids P-DPB1/P-DPB2, so the attribution of training degradation specifically to reference
conditioning (vs generic overoptimization) likewise remains open; at this setting the two
non-reference arms LOST their own judges' scores while losing accuracy (train acc changes:
ref -0.081 [-0.125,-0.038], m1 -0.090, blind -0.200), i.e. training damage without reward
gain, which no gate can rescue.

What run 3 does add, registered and gated: the ref arm again moved its judge while true
accuracy fell (points-scale wedge +1.16 [+0.68, +1.58]; held-out acc -0.110
[-0.149,-0.074]), a second gated replication of the wedge's direction at a milder setting
than run 1. Conditional predictions P-DPF1/P-DPF3 are void (m1 gate); P-DPF2's direction
readout is void for the same reason and reported only in the results JSON
(papers/analysis/dpo_mv3_results.json, producer dpo_mv3_analysis.py).

---

## M1 variants OUTCOME (P-M1V1..P-M1V3) — recorded 2026-09-07, after the runs

P-M1V1 (score input necessary): CONFIRMED both judges. m1noscore-minus-m1 inflation
contrast +1.409 [+1.107,+1.754] (Qwen-7B) and +0.243 [+0.119,+0.360] (phi-4); m1noscore's
level (+1.42) sits at single-reference height for Qwen. The ordering + keep-correct
instruction without the number protects nobody.
P-M1V2 (framing inert): SPLIT — confirmed for phi-4 (-0.031 [-0.140,+0.079]), FALSIFIED
for Qwen-7B (+0.512 [+0.276,+0.733]): labelling the score as the judge's own adds real
protection for the weaker judge.
P-M1V3 (own vs other's score): CONFIRMED both judges (indep-minus-prev -0.149
[-0.401,+0.062] and +0.003 [-0.095,+0.091]). Deference is to a displayed number, not to
the judge's own state.
Reading (post hoc): blind-then-reveal supplies an explicit numeric anchor carrying the
blind pass's uncorrupted signal; the judge defers to it instead of the reference token.
Producer: papers/analysis/m1_variants_analysis.py -> m1_variants_results.json (n=58 k>1
kstrat items, non-degenerate oracle; population per this registration's own filter, not
the OSF mitigation population, hence M1 levels +0.01/+0.12 vs the registered -0.05/+0.16).

---

## Ledger entries for the 2026-09-07 experiments registered in producer headers (recorded 2026-09-07, after an external review noted their absence here)

The four experiments below were registered by git commit of their producer script headers on
2026-09-07 and scored the same day; their predictions and outcomes appeared in the paper but
had no entry in this ledger. Recorded now, with the registration and outcome commit hashes.
Generation and judging for each ran on the cluster through the pipeline scripts named, which
gate on the previous pipeline's DONE marker; the registration commit precedes each launch.

### 2-D composition factorial (P-2D1..P-2D4) — registered `bab23e1` 2026-09-07 12:26, outcome `2bf7dd1` 12:31

Producer `papers/analysis/exploit_lure2d.py` -> `exploit_lure2d.json`. Zero new judging: matched
14-sample sub-pools drawn from already-scored samples, d in {0,2,4} reference-matching valids
crossed with l in {0,3,6} invalid reference-resembling lures, 24 eligible items, plus a
four-parameter selection model S_ref ~ beta*S_blind + lambda*[matches] + gamma*[lure] with item
intercepts, leave-one-item-out.

- **P-2D1 (lure axis raises inflation at d=0): SPLIT.** phi-4 +0.23 [+0.05, +0.44] confirmed;
  Qwen-7B +0.15 [-0.11, +0.37] not resolvable.
- **P-2D2 (removing lures restores a rising dose-response): FALSIFIED both judges.** At d=0, l=0
  the referenced judge still inflates (+0.68, +0.66) and still selects valid answers far less
  often than blind (0.47 vs 0.77; 0.51 vs 0.83).
- **P-2D3 (lures collapse the referenced valid-pick rate at d=0): CONFIRMED.** -0.31 and -0.38,
  CIs excluding zero; blind judges barely move.
- **P-2D4 (model signed as predicted, LOIO Spearman >= 0.8): CONFIRMED.** lambda +4.3 / +3.5,
  gamma +1.4 / +1.7, all excluding zero; Spearman 0.80 (exactly at the bar) and 0.85.
- Reading (post hoc): the lure is a real but secondary channel; the load-bearing term is
  compression, beta ~ 0.5-0.7 (rubric b Qwen 0.44), read as descriptive not causal.

### Exact-oracle rotation replication (P-RR1..P-RR3) — registered `bdfd4c3` 12:34, outcome `f8edc85` 12:47

Producer `papers/analysis/replrot_analysis.py` -> `replrot_results.json`; pool built by
`build_replrot_pool.py` (pool-aware assignment, disclosed, as in the original rotation); judged
by `pipeline21.sh`. Same-sample rotation on the osf.io/ym5x9 replication pool, Qwen-7B and
phi-4, rubrics a and b.

- **All 12 registered cells CONFIRMED.** Gainers +4.97/+6.34 (Qwen a/b), +4.09/+3.25 (phi-4),
  n=120; losers -5.04/-6.58/-3.92/-3.18, n=93; placebo +0.13/+0.10/+0.30/+0.24, n=113;
  gainer-minus-placebo +3.1 to +6.2, every CI excluding zero. Retires the incomplete-checker
  caveat on the paper's central causal result.

### Masking-and-identity suite (P-MS1..P-MS3, masking) — registered `00e24c7` 12:37, outcome `5ca84ac` 13:37

Producer `papers/analysis/maskident_analysis.py` -> `maskident_results.json`; variants built by
`build_refvariant_pools.py`; judged by `pipeline22.sh`. **ID collision disclosed:** the producer
header labels these P-MS1..P-MS3, which this ledger already uses for the Ministral-8B screen
(P-MS1 confirmed, P-MS2 falsified, 2026-08-31). The masking predictions are distinct and are
referred to as "masking P-MS1..3" here.

- **Masking P-MS1 (semantic, not lexical; refword margin > 0 both judges): CONFIRMED.**
  Qwen-7B +2.88 [+2.47, +3.28] vs bare +4.62; phi-4 +3.68 [+3.27, +4.06] vs bare +3.79
  (difference -0.11 [-0.28, +0.05]).
- **Masking P-MS2 (cheapness; refexpr margin below bare, CI excluding zero, both judges):
  CONFIRMED.** Qwen-7B +0.29, difference -4.33 [-4.68, -4.01]; phi-4 +0.89, difference
  -2.90 [-3.30, -2.57].
- **Masking P-MS3 (token necessity; masked worked ref drops > half the margin, scalar
  families k>1): CONFIRMED.** Qwen-7B +2.97 -> +0.05 (drop -2.92 [-3.61, -2.32], 98%);
  phi-4 +3.51 -> -0.49 (drop -4.01 [-4.71, -3.35]). n=21 items. Rubric b replicates all six
  cells. List families exploratory only (masking leaks elements; disclosed).

### Intention-to-treat sensitivity — POST HOC, commit `7d05516`, not registered

Producer `papers/analysis/repl_itt_sensitivity.py` -> `repl_itt_sensitivity.json`, written in
response to external review. E1 over all 120 replication items, no pass-rate band:
+1.14 [+0.97, +1.31]; in-band n=105 +1.19 [+1.03, +1.36] (as registered); out-of-band n=15 alone
+0.78 [+0.19, +1.32]. The band is not load-bearing.

### Answer-separability continuum (P-SC1..P-SC4, continuum) — registered `3ce86e5` 12:41, outcome `0e28207` 13:04, ORACLE CORRECTION 2026-09-07 (evening)

Producer `papers/analysis/sep_continuum_analysis.py` -> `sep_continuum_results.json`; tasks by
`build_sep_tasks.py`, generation `sep_generate.py`, oracle `sep_oracle.py`, judged by
`pipeline23.sh`/`pipeline24.sh`. 25 single-congruence instances asked at four answer-structure
strata (scalar, pair, JSON, program), 64 Llama-3.1-8B samples each, Qwen-7B and phi-4, rubrics a
and b. **ID collision disclosed:** the producer labels these P-SC1..P-SC4, which this ledger
already uses for the closed similarity-vs-correctness 2x2; referred to as "continuum P-SC" here.

**Registered outcome (0e28207), scored on the registered oracle.** Attenuation confirmed both
judges: inflation delta scalar/pair/json/program +1.69/+1.33/+0.75/+0.27 (Qwen-7B) and
+1.32/+0.99/+1.04/-0.06 (phi-4), n=25 per stratum. Continuum P-SC1 (margin survives structure)
confirmed both; P-SC2 (json-minus-program margin cliff) confirmed both; P-SC3 (cliff not
gradient) confirmed phi-4, falsified Qwen-7B; P-SC4 (inflation follows: program cell null)
confirmed phi-4 (-0.06 [-0.22, +0.11]), falsified Qwen-7B (+0.27 [+0.13, +0.40]). Pair and JSON
margin legs starved by match scarcity (7 and 1 usable items); disclosed as a design failure.

**DEVIATION: post-registration oracle correction, applied and disclosed 2026-09-07.** An
external review of the pending push found that the registered `sep_oracle.py` executed the
LAST fenced code block in a reply and required it to contain `def f`; 387 of 1600 program
samples (all 25 items) end with a usage block such as `print(f())` after the block that defines
`f`, and were scored invalid without execution. Corrected rule: execute the last fenced block
that defines `f` (fallback to the last block). Re-scoring the frozen pool flips 330 samples
invalid -> valid and 0 valid -> invalid; program pass rate 0.613 -> 0.819; other strata
unchanged. The registered pool labels are preserved as a backup outside the repo; the
committed pool and `sep_continuum_results.json` are the corrected versions, regenerated by the
unchanged frozen producer.

Corrected program cells: inflation delta **+0.13 [+0.01, +0.24]** (Qwen-7B) and
**-0.37 [-0.49, -0.27]** (phi-4); anchoring margin +0.64 [+0.24, +1.14] and +0.88 [+0.57, +1.20]
(n=19, against +0.55/+0.80 on n=16 registered). Non-program cells move by at most 0.09 (now +1.66/+1.35/+0.71 and +1.35/+0.98/+0.94), because the producer's single seeded RNG is consumed in pool order and the relabeled program items shift the later draws; every interval still excludes zero. **No
registered verdict changes** (P-SC3/P-SC4 still falsified for Qwen-7B, confirmed for phi-4).
Direction of the correction: the mislabeled samples were correct programs; scoring them
correctly moves phi-4's program cell from null to negative (the reference HELPS on programs, as
on MBPP) and halves Qwen-7B's residue. Precedent: the frontier parser correction of 2026-08-31.
Paper updated in the abstract, Section 7.1 (with the disclosure paragraph), and the conclusion.

---

## REGISTERED 2026-09-07 (evening), before any frontier API score exists: frontier-judge extension, Phase 2 (inflation, logprob path) and Phase 1 (margins, sampled-integer path)

**Why.** The paper's only frontier-scale evidence is one anchoring-margin check (37 items, Claude
Sonnet via the CLI, sampled integers, no inflation). Every inflation result, the k-step, and the
mitigation are open-weights only. A reviewer would be right to ask whether the headline holds for
a production judge. This registration pins the protocol that the earlier P-F3 failure showed must
be pinned in advance: the score function.

**Harness.** `experiments/tfa-vs-judge/scripts/frontier_api_judge.py`, committed with this entry.
Prompts are byte-identical to `bon_judge.py` / `mitigation_judge.py` (system and user as separate
roles). Two score functions, pinned:
- **openai (Phase 2):** logprob-expected value over score tokens 0..10 at the first generated
  position, renormalized over score-token mass, from `top_logprobs=5` (the GPT-5.x API maximum;
  vLLM used 20), `reasoning_effort="none"` (GPT-5.x returns no logprobs otherwise; verified
  2026-09-07: gpt-5.5 refuses logprobs entirely, gpt-5.4/5.2 return them only at none),
  temperature 0, `max_completion_tokens` 4, fallback to parsed text when score-token mass < 0.25,
  as in `bon_judge.py`. Judge: **`gpt-5.4-2026-03-05`** (tag `openai__gpt-5.4-2026-03-05`).
  Optional second family under the same predictions: `gpt-4.1-2025-04-14` (full logprobs).
- **anthropic (Phase 1):** sampled integer (no logprobs on the Messages API), temperature 0,
  last integer 0..10. Judge: **`claude-sonnet-5`** via the API (the CLI's `sonnet` alias resolves
  to the same model, verified 2026-09-07). **No inflation is computed from this path.**
Runs use each provider's batch API where possible; identical requests either way.

**Phase 2 design (inflation).** Replication pool (120 items, 64 samples, blind and single
reference, rubrics a and b; analysis population the registered [0.2, 0.8] band) and the
k-stratified pool (75 items; blind, single reference, and M1 blind-then-reveal with this judge's
own blind score in the second call; rubrics a and b). Producer: `papers/analysis/frontier_phase2_analysis.py`,
a documented successor of `repl_analysis.py` and `mitigation_analysis.py` with estimator code copied
verbatim, committed with this entry. Output `frontier_phase2_results.json`.

**Phase 2 predictions (per judge).** P-FR1: replication E1 delta > 0, CI excluding zero.
P-FR2: selection collapse, exact McNemar p < 0.05 in the referenced direction. P-FR3: replication
anchoring margin > 0, CI excluding zero. P-FK1: k-stratified step (k>1 minus k=1 single-reference
delta) > 0, CI excluding zero. P-FK2: M1-minus-single-reference contrast at k>1 < 0, CI excluding
zero. P-FK3 (directional): M1's k>1 level is smaller in magnitude than the single reference's;
the residual is reported as a level, judge-dependent per the coverage extension. **No cross-scale
magnitude claim** (5 vs 20 logprob entries; different calibration): only signs and CIs. A null on
P-FR1 or P-FK1 bounds the paper's claim below frontier scale and is reported as prominently as a
confirmation.

**Phase 1 design (margins, Claude Sonnet 5).** Oracle-valid samples only (`--valid-only`; nulls
elsewhere), rubrics a and b: (i) exact-oracle rotation replication pool (`bon_replrot`), blind,
original reference, rotated reference; (ii) masking suite on the replication pool (`bon_replword`,
`bon_replexpr`) plus bare reference and blind; (iii) MACE k>1 items, blind and reference; (iv) the
blind-certified filter is a re-analysis of (i) and needs no calls. Producer to be committed before
Phase 1 judging (`frontier_phase1_margins.py`); predictions: P-FM1 rotation gainers > 0 and losers
< 0 with placebo flat; P-FM2 words margin > 0, expression margin below bare (CI excluding zero),
both judges' pattern; P-FM3 MACE k>1 referenced margin > 0 with blind CI containing zero; P-FM4
the rotation effect survives on samples the judge blindly scored >= 7.

**Pilot.** One replication item, sync mode, before any batch is submitted, to verify parsing and
the escore distribution. Pilot scores are deleted before the registered run and never analyzed.

**Cost, estimated 2026-09-07 at list prices:** Phase 2 ~60k calls, ~27M input tokens, ~$68
standard / ~$34 batch on gpt-5.4; Phase 1 ~69k calls, ~29M tokens, ~$60 / ~$30 on Sonnet 5.
