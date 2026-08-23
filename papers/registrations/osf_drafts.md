# External preregistration drafts (for OSF or AsPredicted)

Paste each block as a separate registration BEFORE its data is examined. Internal git
timestamps exist for all three (commits referenced below); the external registration adds
selective-disclosure protection that internal timestamps cannot.

---

## Registration 1: DPO training-pressure validation of the judge certificate (rerun)

**Status at registration.** Training of both arms is complete or in progress on our cluster;
no evaluation output of the rerun has been examined. Internal registration: commits
`3a964f1` (predictions, pairs) and the pipeline12 pre-run commit (rerun hyperparameters and
manipulation check). The first run's outcome (manipulation failure, all effects null) is
already public in the paper's ledger and does not enter this registration's data.

**Design.** Two LoRA-DPO arms on Qwen2.5-7B-Instruct, identical hyperparameters
(4 epochs, lr 2e-5, beta 0.1), differing only in the judge that built the preference pairs:
the certified honest referenced GPT-5.2 judge (808 pairs) versus the convicted sabotaged
GPT-5.2 judge (800 pairs), on the same 105 in-band MATH items. Evaluation: n=8 samples per
item from base and both trained policies on the 105 training items and 100 held-out MATH
items; true accuracy by deterministic answer check; judge scores by both frozen judges.

**Manipulation check (gates everything).** The rerun counts as a test only if the trained
arm moves its own judge's train-set score with a 95% bootstrap CI excluding zero, or final
training reward margins exceed 0.5. Otherwise the outcome is recorded as a second
manipulation failure and no prediction is scored.

**Predictions.** P-D1: the certified arm improves true accuracy on held-out items, and its
judge-score and true gains agree in sign. P-D2: the convicted arm shows a larger
judge-minus-true wedge (standardized) than the certified arm, and a smaller true gain.
P-D3: score gains are instrument-specific (the convicted arm gains more under its own judge
than under the honest judge; the certified arm's gain transfers).

**Analysis.** Pre-committed script `papers/analysis/dpo_analysis.py` (item-paired bootstrap
gains and wedges), unchanged from the first run.

---

## Registration 2: Putnam second-dataset replication of the audit under the frozen revised rule

**Status at registration.** The 60-item Putnam labeling instrument exists and is being
labeled; no judge partials on Putnam labels have been computed. Internal registration:
the revised certification rule was frozen in the paper before this test (pass requires the
soundness-partial CI to clear 0.40; convict on significantly positive style partial; fail
otherwise).

**Design.** The same audit applied to Putnam-AXIOM traces: blind human labels on soundness
and style for 60 traces, partial correlations for each judge configuration available on the
Putnam pools, verdicts assigned by the frozen revised rule.

**Predictions.** P-P1: referenced frontier and referenced mid-size judges certify or
abstain; no honest referenced configuration is convicted. P-P2: any configuration convicted
on Putnam shows elevated pressure damage (gap or regret in the failed range) wherever a
Putnam best-of-n pool exists. P-P3: the audit's verdicts agree with the math-domain verdicts
for shared configurations (protocol, not dataset, carries the verdict).

**Analysis.** The same partial-correlation estimators and bootstrap machinery as the math
audit (committed scripts), applied without modification.

---

## Registration 3: Clean preregistered replication of the reference-lever inversion (Paper D)

**Status at registration.** No pool has been generated. This registration defines the
population, estimators, and endpoints BEFORE any data exist, answering the post-hoc
population and pooling deviations disclosed for the original result.

**Design.** A fresh multi-valid task pool: at least 120 items with exhaustively enumerated
or programmatically verifiable valid-answer sets (constraint-satisfaction style tasks where
validity is checkable without enumeration where possible), constructed so best-of-64
pass rates fall in [0.2, 0.8] by design (calibrated by a pilot on 20 disjoint items that
does not enter the analysis). Generator: a non-Qwen open model (Llama-3.1-8B-Instruct).
Judges: Qwen2.5-7B-Instruct and phi-4 (one same-family with the original study's judges,
one not; neither shares family with the generator). Conditions: blind versus single
reference, two rubric replicates.

**Primary endpoints (both must be stated with 95% CIs).** E1: the per-item paired
referenced-minus-blind excess-gap delta, pooled over the two judges by item-level cluster
bootstrap. E2: the k=1-versus-k>1 style step is not applicable here; instead the paired
delta must be positive with CI excluding zero for the pooled estimator (prediction), with
per-judge deltas reported.

**Predictions.** P-R1: pooled paired delta positive, CI excluding zero. P-R2: the
selection-collapse rate (referenced judges selecting reference-matching valid answers)
exceeds the blind rate with McNemar p < 0.05 for each judge. P-R3: anchoring margins are
positive for both judges.

**Analysis.** The committed estimator scripts (`bon_analysis.py` machinery,
`ties_rot_controls.py`-style margins), frozen at registration; no population or estimator
changes permitted post hoc; deviations will be reported as deviations.

---

## Registration 4: k-stratified structural-mitigation experiment (Paper D follow-up)

**Status at registration.** No pool has been generated and no mitigation protocol has been
run. Registered before any data.

**Design.** A pool of tasks with EXACTLY k valid answers per stratum, k in {1, 2, 4, 8, 16},
15 items per stratum (75 total), drawn from the five verifiable constraint families of the
osf.io/ym5x9 replication (CRT, subset-sum, Goldbach pairs, divisor counts, digit sums) with
solution counts computed exactly at build time and validity checkable programmatically from
the answer alone. Generator: Llama-3.1-8B-Instruct with the mandatory-boxing prompt.
Judges: Qwen2.5-7B-Instruct and phi-4. A small pilot (10 items) may adjust family difficulty
mixes only; pilot items do not enter the analysis.

**Conditions.** Four, each with two rubric replicates (selection on replicate a, reporting
on replicate b): (1) blind; (2) single reference (the standard lever); (3) M1 blind-then-
reveal, a two-call structural protocol: call one scores blind; call two shows the judge its
own blind assessment plus the reference with the instruction that a correct answer differing
from the reference must keep its score, and the reported score is call two's; (4) M2
equivalence-gated, a two-call decomposition: call one scores blind; call two answers only
whether the candidate's final answer is a valid answer to the question (the reference shown
as one valid example); the final score is the blind score if judged valid and zero otherwise.

**Primary endpoints (frozen; per judge and pooled over judges by item-level cluster
bootstrap, within k strata and pooled over k > 1).** E1: anchoring margin per condition
(mean score of reference-matching valid samples minus other valid samples). E2: paired
excess-gap delta of each condition minus blind at n = 64.

**Predictions.** P-M1: M1 reduces both the margin and the gap-over-blind relative to the
single-reference condition at k > 1, for both judges (not capability-gated the way the
one-sentence instruction was), while preserving the k = 1 benefit (M1 gap at k = 1 at or
below blind). P-M2: M2 eliminates the anchoring margin (CI including zero at every k > 1
stratum for both judges) and holds the gap at or below blind at every k. P-M3
(k-boundary under external registration, subsuming the earlier item-3 ask): the
single-reference condition helps at k = 1 (gap below blind) and harms at k > 1 (gap above
blind) for both judges; the k = 1-to-k > 1 step is positive with CI excluding zero.
P-M4 (exploratory, no confirmatory claim): mitigation effectiveness as a function of k.

**Analysis.** Estimators identical to the committed synthk and replication analysis code
(margins, paired gaps over the bon_analysis machinery, item-level cluster bootstrap, exact
McNemar where selection collapse is reported); the analysis script will be committed before
the main pool is generated, and any deviation will be reported as a deviation.
