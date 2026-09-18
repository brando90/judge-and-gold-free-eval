# Registered predictions: Experiment 1 (valid worked-solution reference anchoring)

**Written 2026-09-18, before any judge call of that experiment has been made.**

Spec predicted against: `~/Downloads/message.txt` (worked-solution version of Experiment 1).
Predictions derive from measurements taken 2026-09-17/18 on three benchmarks with four judges,
~16,000 judge calls. Nothing here is a guess dressed as a forecast: each number is either measured
directly or obtained by re-expressing a measurement in the spec's own endpoint.

The point of this file is to be **checkable and falsifiable**. Where I am wrong, the reasoning is
written out so the failure is diagnosable rather than merely recorded.

---

## The single most important prediction

**The spec's primary endpoint will read as a near-null on the constructed-math benchmarks, even if
a large effect is present.**

Their endpoint is binary acceptance `Y = 1[G >= 2]` on a 0-3 rubric. I measured the same effect on a
0-10 scale and re-expressed it in their units:

| my measured cell | numeric effect (0-10) | **their A (binary, 0-3)** | already accepted at C0 |
|---|---|---|---|
| Qwen2.5-7B / v4 (MathConstruct+Math-Constraint) | +1.730 | **+0.005** | 100% |
| Qwen2.5-7B / replication | +1.704 | **+0.079** | 96% |
| gpt-4.1-nano / v4 | +0.567 | **+0.049** | 100% |
| Qwen2.5-7B / MACE (factual) | +4.732 | +0.722 | 78% |

A +1.73 effect becomes **+0.005**. The cause is mechanical: 96-100% of verified-correct candidates
are *already accepted* at C0, so `Delta_match` cannot rise, and a nonmatching reference must push a
grade down two full rubric levels (3 -> 1) before the binary outcome changes at all.

I hit this exact wall myself: on the 0-3 rubric with gpt-4.1, **0 of 204 candidates moved**, in any
direction. I then built a 0-10 variant specifically to test whether the scale was the constraint. On
a strong judge it was not (the null was real). On weak judges, the simulation above shows it is.

---

## Numbered predictions

### P1 - Magnitude of the primary endpoint
On MathConstruct / Math-Constraint pools, **A will fall in +0.00 to +0.10 for most of the nine
model x method cells**, with several 95% CIs spanning zero.
Confidence: **high**.

### P2 - Decomposition
**The effect will sit almost entirely in `Delta_nonmatch`, not `Delta_match`.**
Simulated: `Delta_match` +0.000 to +0.022; `Delta_nonmatch` carries the signal in every cell.
Mechanism: matching references have no headroom because correct candidates already score at the top.
Confidence: **high**.

### P3 - Best-of-n will be null, for a mechanical reason
Median share of candidates **tied at the top grade** once grades are banded 0-3:

| cell | tie rate |
|---|---|
| gpt-4.1 / v4 | 100% |
| nano / v4 | 94% |
| Qwen / replication | 50% |
| Qwen / v4 | 38% |

With most candidates tied, expected-validity tie-breaking returns the pool's valid fraction
regardless of reference condition, so the judge cannot move the winner. This is the most likely
explanation for the prior null in experiment 08, and a 4-level rubric reproduces it.
Confidence: **high**. (The spec already hedges for this outcome, correctly.)

### P4 - Judge ordering
All three judges (Qwen3-32B, Llama-3.3-70B-Instruct, Mistral-Small-3.1-24B) sit in the capability
regime where I measured anchoring, so **most cells should show positive A**.
BUT: **expect at least one judge x benchmark cell to come back null against expectation.**
Evidence: gpt-4.1-nano on MACE gave -0.147, CI [-0.410, +0.109] -- a weak judge, on the least
verifiable task, with good blind discrimination (AUROC 0.804) and ample headroom (66% at-10), that
nonetheless did not anchor. I have no account for that cell. The judge x task surface is **not
monotone**, and any prediction that assumes it is will be wrong somewhere.
Confidence: **medium**.

### P5 - Method ordering
**M0 > M1 > M2** (brief justification anchors most, structured verification least), roughly 2-3x
between the extremes. From the prior ledger's own prompt sweep on MACE: -1.477 (bare rubric),
-0.358 (CoT), -0.179 (verify-first), -0.060 (solve-first).
Caveat: requiring a justification *reversed* one of my effects (-0.739 -> +0.281 on the `subset`
family), so **M1/M2 may go slightly positive rather than merely smaller**.
Confidence: **medium**.

### P6 - Terra pool weakest
GPT-5.6-Terra is ~76% valid with only 8 draws per item, so its candidates are high quality and
confidently graded. **Terra's cells will be the flattest of the three pools**, and its crossover
population (21 items) will not resolve.
Confidence: **medium-high**.

### P7 - Crossover underpowered
Llama 30 items, Terra 21 items. **Wide CIs, most crossover results not significant.**
Confidence: **high**.

### P8 - Population representativeness
The mechanism population requires the candidate's answer class to be **in the stored bank**. On my
gpt-4.1-mini pool only **102 of 317** items qualify, because the bank stores ~7 answers where the
problems admit thousands -- **89% of verified-correct candidates fall outside the bank entirely**.
That qualifying subset is also enriched **2.17x** for canonical answers (22 of 71 bank matches vs
10.1 expected, sd 2.95, z = 4.02, p = 5.8e-05).
**Prediction: the mechanism population will be a minority of items and skewed toward canonical
answers.** The spec states the estimand is conditional, which is honest; the consequence is that it
describes an unrepresentative slice of the correct-answer population.
Confidence: **high** (measured directly).

### P9 - Worked solutions may dilute rather than amplify
The prior ledger's experiment 02 measured the anchoring effect collapsing from +2.97 to +0.05 when
the answer was embedded in a worked solution rather than shown bare. This spec mitigates that by
displaying `rendered_answer` alongside the worked solution, so I predict **roughly bare-answer
magnitudes**. But if effects come in *below* the bare-answer version, embedding is the reason.
Confidence: **medium**.

---

## What would falsify the framework behind these predictions

- **A > +0.3 on constructed math.** Would mean the ceiling argument is wrong and the 0-3 binary
  endpoint is more sensitive than my simulation implies.
- **`Delta_match` large and positive.** Would mean correct candidates are NOT already accepted at
  C0 in their setup -- i.e. their judges are far harsher than any of my four.
- **A clean best-of-n effect.** Would mean tie-breaking is not dominating selection, and would
  reopen the selection claim that experiment 08 left unresolved.
- **A monotone judge ordering with no exceptions.** Would suggest the nano/MACE anomaly is specific
  to that model rather than a general feature of the surface.

---

## Measurements these predictions rest on

Taken 2026-09-17/18. Effect = grade change on verified-correct candidates shown a *different*
correct reference; bare prompt; item-clustered bootstrap, 10,000 resamples. `*` = CI excludes zero.

| judge | MACE (cannot verify) | replication (trivially verifiable) | v4 (expensively verifiable) |
|---|---|---|---|
| gpt-4.1 | -0.158* | -0.025 | +0.110 |
| Sonnet 5 | -- | -- | -0.053 |
| gpt-4.1-nano | -0.147 | -0.282* | -0.635* |
| Qwen2.5-7B | -3.419* | -1.151* | -0.680* |

Blind discrimination (can the judge separate correct from wrong with NO reference?):

| judge | MACE | replication | v4 |
|---|---|---|---|
| gpt-4.1 | 0.926 | 0.900 | 0.677 |
| Sonnet 5 | -- | -- | 0.941 |
| gpt-4.1-nano | 0.804 | 0.863 | 0.666 |
| Qwen2.5-7B | 0.602 | 0.839 | 0.555 |

Two cells deserve caution when used as evidence: **Qwen/v4 has AUROC 0.555** (near chance), so its
-0.680 is measured on grades that barely track correctness; and **nano/MACE** is the unexplained
null described in P4.

One result that held in every single cell measured, across 3 benchmarks, 4 judges, 2 vendors:
**agreement with the reference is always rewarded** (C1_match - C0 positive everywhere, from +0.137
to +1.302). Only the *punishment* of disagreement is regime-dependent.

---

## Honesty note

Two findings were retracted during the session that produced these measurements:

1. A `subset`-family effect of -0.739 that **reversed to +0.281** once the judge was asked to
   justify its score. It was an artifact of score-only prompting, not anchoring.
2. A claim that judge capability dominates task type, which the completed 4x3 grid contradicted --
   nano and Qwen order oppositely across benchmarks.

Both were stated confidently before the contradicting cell was run. The predictions above are
therefore deliberately scoped: claims spanning the whole grid are offered with high confidence,
claims that *rank* factors against each other are not.
