# External NeurIPS-AC-style review of `A-certificate/Agreement_Is_Not_A_Certificate.tex` (2026-09-07)

Score: **5/10, borderline / weak reject**, high confidence. Ladder: 6/10 with wording, sensitivity
analyses, multiple independent annotators, threshold justification (no new panel); 7/10 with a
genuinely prospective held-out panel of new, decorrelated judge configurations under a frozen rule
that beats raw metrics and the reference-present baseline; 8/10 with a successful prospective
cross-domain replication as well.

## Major concerns (verbatim priority table)

1. critical: effective sample is ~4 classes, not 11-13 configurations -> prospective held-out panel of
   new judge configurations after freezing the audit.
2. critical: thresholds (.30 / .40 / .20) insufficiently principled; false pass at .41 -> derive from
   predeclared criterion / simulation / decision cost; uncertainty-aware abstention prospectively.
3. critical: one domain, one primary annotator; rater-2 covers 30 items, style reliability .48 ->
   2-3 hypothesis-blind non-author raters on all 60, soundness and style assigned to different
   raters; then a prospective second domain.
4. high: "raw agreement" is really Pearson r -> compare Pearson, Spearman, Kendall, pairwise accuracy,
   binary correctness agreement, calibration, RewardBench/RM-Bench-style scores; show none diagnose
   capable-corrupt vs weak-honest.
5. high: taxonomy mixes mechanism and outcome ("fail predicts regret", "convict predicts inflation or
   damage") -> separate (a) is this judge safe to optimize against and (b) which failure mechanism.
6. high: DPO language overstates (certified arm 0.000 held-out) -> "the audit identified the relatively
   safer signal in this experiment"; seeds or second setting.
7. medium/high: partials at n~60 under r(soundness,style)=.82 need stress tests -> simulation/power
   analysis over reliability, axis correlation, n, effect size; Spearman partials / robust regression.
8. medium: style is not universally a nuisance -> formalize as target construct(s) + forbidden
   nuisance construct(s).

## Other requested changes
- Present the continuous (target loading, nuisance loading) measurement first, the rule second;
  make the prospective rule uncertainty-based (certify only when evidence establishes target loading
  and rules out nuisance loading; otherwise abstain); call it prospective v2, never rescore
  retroactively.
- Annotation: common-method bias when one rater labels both axes; split raters by axis.
- DPO: claim only "correctly identified which of the two signals was harmful to optimize against in
  this experiment".
- Standalone: Figure 1's compare-vs-verify mechanism must be labeled companion/prior evidence; keep
  the paper centered on construct audit -> frozen prediction -> optimization outcome.
- Tone: neutralize "convict", "damning", "fails in the worst way", "certificate" in the formal
  taxonomy (pass -> qualify; fail -> insufficient target validity; convict -> nuisance-loaded/unsafe);
  "raw agreement" -> "marginal agreement/correlation" unless real agreement baselines are added.

## Follow-up message: experiment priorities for acceptance
Do exactly these four if resources are limited: (1) prospective new-judge panel, 12-20 configs, designed
so reference presence cannot predict success (strong blind judges, weak referenced judges, honest
alternative prompts, subtly style-biased prompts, length-biased prompts, new reward models, other
model families; especially referenced-but-corrupted and blind-but-capable), audit -> frozen
qualify/abstain/unsafe -> best-of-64 -> compare raw correlation, reference bit, judge accuracy, audit
by AUROC/accuracy for unsafe optimization, continuous where possible; (2) independent split-rater
annotation on the 60 items (pool A soundness only, pool B style only), optionally a prospectively
constructed factorial set (correct/wrong x good/poor style); (3) uncertainty-aware certification with
a simulation of false-certification probability vs label count under known target/nuisance
correlations and annotator noise; (4) expanded conventional-baseline comparison (Pearson, Spearman,
Kendall, pairwise accuracy, binary accuracy, AUROC, ECE, Brier, disagreement rate, raw accuracy +
reference-presence model): which static metric best predicts downstream optimization failure.
With more compute: (5) prospective code replication with executed tests as target and verbosity /
formatting / confidence as nuisances; (6) multi-seed DPO (3-5 seeds per arm, between-arm contrast,
oracle/human-pairs third arm). Also suggested: audit risk score / regress hack gap on the two partials
(R^2, LOOCV); nuisance vector beyond style; subtle-sabotage ladder with blinded auditors; predict
failure at n=64 from a rule frozen on n=16.
Paper-level: change the claim from "we have a certificate that determines whether a judge is safe" to
"static construct validity predicts downstream optimization failure better than marginal agreement";
the certificate is the application. The core idea: what the evaluator measures matters more under
optimization than how well it agrees IID.
