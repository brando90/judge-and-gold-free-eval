# Does a Certified Judge Stay Valid Under Optimization Pressure?

*Research plan, v1 (2026-08-16). Status: design; Phase 0 executable on current infrastructure.*

## The question and why it is unclaimed

The reward-hacking literature (Gao et al.'s overoptimization scaling laws and its successors) measures
how much a reward model's score inflates relative to a gold reward as you optimize against it. Two
things it does not do: it treats the reward as a scalar, never decomposing WHAT gets hacked (does the
policy get better-sounding or better-reasoning?), and it has no ex-ante predictor — you learn a reward
model is hackable by hacking it. Our certification protocol supplies both missing pieces: a validity
decomposition (soundness vs style channels, measured against humans) and a static, pre-deployment
number per judge. The claim worth a paper: **static certification predicts dynamic hack-resistance,
and the reference lever that flips judges from style-loaded to valid also flattens their hacking
curve.** Nobody has connected validity measurement to optimization robustness; our own earlier lit
pass found this exact link ("a static surface property that predicts hackability ex ante") unclaimed.

## Core design idea

Optimization pressure has a cheap, exact, controllable form: **best-of-n selection against the judge**
(pressure = log n nats, the standard KL equivalent), before any RL is needed. Our domains have free
oracles (boxed answers in math, executed tests in code), so the truth axis costs nothing at scale, and
the style/soundness composition of what the optimizer finds comes from the certification instrument.

For each judge configuration J and pressure level n:
1. A fixed generator (Qwen2.5-7B, temperature 1.0) samples n solutions per problem.
2. Select the sample J scores highest.
3. Measure three things about the selected set:
   - **judge gain**: J's score of selected minus J's score of a random sample (rises by construction);
   - **true gain**: oracle correctness (boxed/tests) of selected minus baseline;
   - **channel composition**: soundness and style grades of the selected set (model-critic panel with
     stated human calibration; human spot-checks on a fixed subset).

Define the **hack gap** at pressure n: judge gain minus true gain (normalized). A judge is hack-
resistant if its gap stays near zero as n grows; hacked if the gap opens; style-hacked if the opened
gap loads on the style channel.

## Judge configurations (chosen because we already certified them)

| config | static certification verdict |
|---|---|
| Qwen-1.5B, no reference | STYLE-LOADED (style partial +0.33) |
| Qwen-14B, no reference | FAIL, weak (+0.26) |
| Qwen-1.5B, with reference | PASS (+0.40) |
| Qwen-14B, with reference | PASS (+0.53) |
| GPT-5.2 (subsampled) | PASS (+0.59) |
| GPT-5.2 sabotage prompt | CONVICTED (style +0.56) — positive control, must hack |

Registered predictions (to be committed before results):
- P1: hack gap at n=64 orders the configs by their static certification (Spearman across configs > 0.7).
- P2: the sabotaged judge and the 1.5B-noref judge get style-hacked (gap loads on style channel).
- P3: with-reference judges show materially flatter gaps than the same model without (the reference
  removes the exploitable channel: the judge compares content instead of assessing prose).
- P4 (risk-aware): with-reference judges may show near-zero gap at BoN pressures; that is a positive
  result (a defense), not a null, because the positive control bounds the instrument's sensitivity.

## Phases

**Phase 0 — BoN probe (1-2 weeks, current infra, no training).**
200 MATH-500 problems x 64 samples from the 7B generator (~13k generations, hours on one GPU);
same for 164 HumanEval (tests as oracle). Score all samples with the four open-weights judge configs
(cheap); score a random 8-per-problem subset plus each judge's selections with GPT and the sabotage
judge (API cost bounded). Panel-grade selected sets at n in {1,4,16,64}; humans spot-check 60 selected
items (the existing labeling pipeline reused verbatim). Deliverable: hacking curves per judge config,
the certification-predicts-hacking test, and the channel decomposition of every gap.

**Phase 1 — training pressure (3-4 weeks, adds DPO).**
Build preference pairs from judge scores (chosen = judge-high, rejected = judge-low sample of the same
problem); DPO the 1.5B/3B generator against each judge config at increasing KL budgets (LoRA, one GPU
per run, well within the 5-GPU ceiling). Two measurements BoN cannot give: (a) validity is
distribution-dependent, so RE-certify each judge against the shifted policy's outputs at each KL step
— does certification survive off its calibration distribution? (b) does training find exploits BoN
selection cannot (novel style attacks, verbosity drift, format gaming)? Oracle and channel measurement
as in Phase 0.

**Phase 2 — defenses (2-3 weeks).**
Take the most-hacked configuration and test whether the levers we have measured statically also defend
dynamically: reference-in-context, forced solve-then-judge, two-family judge ensembles, and endpoint
gating (judge score only counts when the boxed answer/tests pass). Deliverable: a defended-vs-
undefended hacking curve per lever, which is the "how to design judges that survive optimization"
payoff, and the direct bridge to the oversight program's step 3.

## What we reuse (nothing here starts from scratch)

Generators, judges, and rubrics: the matrix runner and cert task machinery as-is. Oracles: boxed
scorer (repaired) and the HumanEval test harness built this week. Channel measurement: the critic
panel with its measured human calibration (0.53-0.59), plus the labeling artifacts for human spot
checks. Statistics: the bootstrap/partial machinery. The only new code is BoN sampling/selection
(~150 lines) and, in Phase 1, a standard DPO loop.

## Honest risks

1. BoN at n=64 is mild pressure (~4.2 nats); good judges may simply not hack. Mitigations: positive
   control bounds sensitivity; Phase 1 raises pressure; a flat curve for certified judges is itself
   the headline if the uncertified ones bend.
2. The channel measurement leans on the model panel between human batches; its calibration (0.53-0.59
   vs the 0.79 human ceiling) is stated, and any claim that survives only under panel grades and not
   under the human spot-checks does not ship.
3. Generator-judge family overlap (Qwen judging Qwen) could add self-preference to the hack gap;
   we cross with phi-4 as a second generator on a subset.
4. Distribution shift in Phase 1 may invalidate the static certificates in a way that is itself the
   finding ("certificates expire under optimization") — either outcome is informative, which is what
   makes the design safe to run.

## Sequencing against everything else

Phase 0 does not compete with the two papers for human labels (it uses oracles and the panel) and can
start as soon as GPUs are free. The certification paper should be submitted first: it is the
instrument this study depends on, and "we certified, then optimized" is a cleaner story than releasing
both at once.
