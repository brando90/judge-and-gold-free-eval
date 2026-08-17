# Does a Certified Judge Stay Valid Under Optimization Pressure?

*Research plan, v2 (2026-08-16), revised after independent critic review. The critic's full report is
summarized in the changelog at the bottom; v1 had two flaws that would have made the headline number
an artifact (winner's curse, score-tie saturation) — both are designed out below.*

## The question and why it is unclaimed

The reward-hacking literature (Gao et al.'s overoptimization scaling laws and successors) measures how
much a reward model's score inflates relative to gold reward under optimization. It treats the reward
as a scalar (never decomposing WHAT gets hacked: presentation or reasoning) and has no ex-ante
predictor: you learn a reward model is hackable by hacking it. Our certification protocol supplies
both missing pieces: a soundness-vs-style validity decomposition measured against humans, and a
static pre-deployment certificate per judge. The claim worth a paper: **static certification predicts
dynamic hack-resistance, and the reference lever that flips judges from style-loaded to valid also
flattens their hacking curve.** Our lit pass found this link ("a static property that predicts
hackability ex ante") unclaimed.

## Core design

Pressure = best-of-n selection against the judge. A fixed generator (Qwen2.5-7B, temperature 1.0)
samples 64 solutions per problem; each judge configuration selects its favorite at
n in {1, 4, 16, 64}; free oracles (boxed answers on MATH-500, executed tests on HumanEval) give the
truth axis at zero cost.

**The estimand is the EXCESS hack gap, not the raw gap.** Two corrections, both mandatory:

1. *Split-replicate scoring (winner's-curse control).* Every sample is scored twice by independent
   judge replicates (different seeds / prompt paraphrase). Selection uses replicate A; the reported
   judge gain uses replicate B. Without this, argmax selection inflates the selected score by
   ~sigma_noise * sqrt(2 ln n) (about 2.9 sd at n=64) for a perfectly valid noisy judge, and the gap
   would rank judges by noise, not invalidity.
2. *Permutation null.* Judge scores are permuted within oracle-correctness strata (destroys validity,
   preserves marginal noise and the score-correctness base rate); excess hack gap = observed gap minus
   this null. The scale-free companion estimand is **oracle regret**: true gain under oracle-argmax
   minus true gain under judge-argmax, which needs no judge-scale normalization and is a headline
   curve in its own right.

**Continuous scores, measured pressure.** Integer 0-10 scores tie massively at n=64 (a judge that
gives 40 samples a 10 is doing best-of-1.6, not best-of-64), and tie density differs by judge, so
nominal log n is not comparable across judges. Fixes: judge scores are elicited as logprob-expected
values (sum of p(token=k) * k over the 0-10 tokens, near-zero marginal cost in vLLM); residual ties
break randomly, resampled 100x with CIs; and every arm reports **realized selection pressure**
(entropy of the selection distribution / expected top-set size) alongside nominal log n. Cross-judge
claims condition on comparable realized pressure. Nominal KL is an upper bound
(KL <= log n - (n-1)/n); realized is what gets plotted. Sub-n arms (4, 16) use bootstrapped random
subsets of the 64 (100 draws), not the first-k, to avoid ordering artifacts. The n=1 baseline is the
mean over all 64 samples, not a single draw.

## Judge configurations

Full free grid, 10 configs: Qwen {1.5B, 3B, 7B, 14B} x {no reference, gold reference} (8), plus a
sabotage-prompt (presentation-first) variant on two sizes. Frontier arms run on **Opus via the CLI**
(free; already calibrated +0.53 vs human soundness): honest Opus and an Opus-ported sabotage judge,
the latter re-certified on the existing 60-item divergence stratum (panel + ~15-item human spot
check) before being trusted as positive control. GPT-5.2 appears only as a ~50-problem validation
subset showing Opus-selection tracks GPT-selection (<= $8; full GPT selection arms would cost
$50-150 and are out of budget).

## Registered predictions (analysis script committed to git before generation)

- P1 (primary, confirmatory): the **paired within-size reference contrast** — for each Qwen size,
  excess hack gap without reference minus with reference is positive (sign test over 4 paired
  differences, plus magnitudes with bootstrap CIs). This is the mechanistic claim: the reference
  removes the exploitable style channel.
- P2: the sabotage judges and the 1.5B-noref judge are *style*-hacked: their selected sets rise on
  the style channel, corroborated by judge-free mechanical proxies (length, markdown density,
  hedge-phrase rate) that no LLM touched. Evaluated only on items whose pools contain
  style-truth decoupling (>= 2 oracle-incorrect samples in the top style-proxy quartile); the
  fraction of items with any exploitable surface is itself a reported quantity.
- P3 (descriptive, not confirmatory): across the 10-config grid, excess hack gap orders by the
  certified **style partial** (the mechanistic predictor; soundness rho is the wrong x-axis).
  With <= 12 points this cannot reach significance and is reported as descriptive structure only.
- P4: flat excess-gap curves for certified judges are a positive result (a defense), bounded below
  by the sabotage positive control, which must bend.

**Certificates are re-measured on the deployment distribution.** The static predictor is NOT the
original certification (measured on mixed-solver traces); it is the same protocol re-run on the n=1
arm of the actual Qwen-7B temperature-1.0 pool (open judges free; Opus panel free; ~30 human spot
checks), pre-registered before any selection results are computed. Comparing the two certificate sets
is a bonus result on certificate portability across distributions.

## Item selection (pre-registered filter)

All 500 MATH-500 items are generated (64 samples each; the full pool subsumes a pilot). Analysis
items are those with pool pass rate in [0.2, 0.8] (expected ~150-200, concentrated in levels 4-5);
items outside carry no truth-axis information (all-correct or all-wrong pools saturate true gain).
Full-set results go to an appendix. HumanEval gets the same filter; if too few items survive
(strong 7B, 164 items), MBPP+ is the pre-registered backfill.

## Channel measurement (circularity rules)

The panel grading sets selected by judge J **excludes J's family**: Opus-only panel for GPT/sabotage
arms, gpt+opus for Qwen arms. The panel is recalibrated on 20-30 human-labeled *selected* outputs
(the 0.53-0.59 pre-selection calibration does not transfer under adversarial shift by assumption).
Human labels concentrate where they have power: n=64 only, three configs (sabotage, 1.5B-noref, one
PASS judge), ~20 items each, prioritizing panel-vs-proxy disagreements. Mechanical style proxies run
on everything.

## Confounds held or measured

Self-preference (Qwen judging Qwen): phi-4 generates a >= 50-item subset; test is whether Qwen-judge
excess gaps shrink on phi-4 pools. Generator fixed at 7B for all Phase 0 arms.

## Phases

**Phase 0 (now):** generation (500 x 64 math + 164 x 64 code, one GPU, hours) -> oracle scoring ->
item filter -> judge scoring (10 open configs x 2 replicates, logprob-expected) -> selection curves,
excess gaps, oracle regret -> panel + proxies on selected sets -> human spot labels.

**Phase 1 (gated on Phase 0):** DPO against judge scores. Known issues to resolve on Phase 0 data
first: beta is a loose KL proxy, so both phases plot on **realized KL** from policy logprobs;
preference pairs require a minimum score margin (impossible for saturated judges — forced by the
logprob-score fix); at least one 7B DPO run bridges the generator mismatch. Re-certify judges on the
shifted policy at each KL step: certificates expiring under optimization is itself a finding.

**Phase 2:** defenses (reference-in-context, solve-then-judge, ensembles, endpoint gating) on the
most-hacked config: defended vs undefended excess-gap curves; the bridge to the oversight program.

## Honest risks

1. BoN at n=64 is ~4 nats nominal and less realized; certified judges may show no excess gap. That
   is P4's positive reading, bounded by the sabotage control, and Phase 1 raises pressure.
2. Panel-based channel claims that fail the human spot checks do not ship (standing rule).
3. Style-truth coupling in natural pools (+0.82 on random MATH) may leave few exploitable items;
   the decoupling screen and the reported exploitable-surface fraction handle this, and that
   fraction feeds the nuisance-fraction framing directly.

## Sequencing

Phase 0 competes with nothing: oracles and panel, humans only for ~90 concentrated spot labels.
Certification paper ships first; this study uses its instrument.

## Changelog v1 -> v2 (critic-driven)

Raw hack gap replaced by excess gap (split-replicate + permutation null) and oracle regret [C1].
Logprob-expected scores, resampled tie-breaks, realized-pressure reporting, bootstrap sub-n arms,
mean-of-64 baseline [C2, minors]. GPT selection arms (unaffordable) swapped to Opus-CLI with
re-certified Opus sabotage port; GPT demoted to $8 validation subset [C3]. Panel family-exclusion,
concentrated human labels, mechanical proxies, panel recalibration on selected outputs [C4].
Predictor re-registered as style partial measured on the deployment distribution (n=1 arm) [M1].
Primary analysis is the paired reference contrast; pooled cross-config correlation demoted to
descriptive (6-point Spearman could never reach significance) [M2, M5]. Pass-rate [0.2, 0.8] item
filter and P2 decoupling screen [M3, M4]. Phase 1 gated on realized-KL and margin machinery [M6].
Analysis script committed before generation [forking paths].
