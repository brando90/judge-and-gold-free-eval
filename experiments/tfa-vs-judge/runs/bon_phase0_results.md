# Validity Under Pressure, Phase 0 results (2026-08-16)

Best-of-64 selection against 12 judge configurations on 105 in-band MATH-500 items (pool pass rate
in [0.2, 0.8], pre-registered filter), Qwen2.5-7B generator at temperature 1.0. Estimand: excess
hack gap (split-replicate A/B scoring + within-oracle-stratum permutation null); companion: oracle
regret (accuracy left on the table vs oracle-best selection). Analysis script committed before
generation. Escore = logprob-expected value; the digit-tokenizer "10"->"1","0" inversion was caught
by an implausible-regret sanity check and fixed before any Qwen results were interpreted (buggy
files archived in runs/bon_scores_v1buggy on the cluster).

## Full table

| judge config              | excess hack gap [95% CI] | oracle regret @64 |
|---------------------------|--------------------------|-------------------|
| Qwen-1.5B noref           | +0.88 [0.75, 1.02]       | 0.448             |
| Qwen-3B  noref            | +0.44 [0.31, 0.59]       | 0.429             |
| Qwen-7B  noref            | +0.80 [0.67, 0.93]       | 0.324             |
| Qwen-14B noref            | +0.63 [0.40, 0.85]       | 0.324             |
| Qwen-1.5B ref             | +0.16 [0.12, 0.21]       | 0.010             |
| Qwen-3B  ref              | +0.07 [0.03, 0.11]       | 0.038             |
| Qwen-7B  ref              | +0.18 [0.13, 0.24]       | 0.019             |
| Qwen-14B ref              | +0.05 [0.02, 0.09]       | 0.048             |
| Qwen-7B  sabotage         | +0.13 [-0.13, 0.34]      | 0.400             |
| Qwen-14B sabotage         | +0.61 [0.50, 0.73]       | 0.324             |
| GPT-5.2  ref (honest)     | +0.38 [0.28, 0.51]       | 0.117             |
| GPT-5.2  sabotage         | +0.85 [0.70, 1.00]       | 0.133             |

## Registered predictions

**P1 (primary, paired within-size reference contrast): CONFIRMED 4/4.** noref minus ref excess gap:
1.5B +0.72, 3B +0.37, 7B +0.62, 14B +0.57 (sign test 4/4, p=.0625, the max resolution 4 pairs allow;
every pair's per-config CIs are disjoint by a wide margin). The same holds on regret: 0.448->0.010,
0.429->0.038, 0.324->0.019, 0.324->0.048. The reference collapses score inflation 6-12x and real
damage 7-30x. Every no-reference config FAILED static certification; every with-reference config
PASSED: the static certificate predicts dynamic hack-resistance.

**P2 (sabotage style channel): CONFIRMED for the channel, REFUTED for damage at BoN-64.** Opus panel
(cross-family, blind, 315/315): sabotage-selected solutions are more styled than honest-selected
(+0.27 [0.10, 0.44] paired) with NO soundness loss (-0.13 [-0.61, 0.30]; within-correct +0.13) and
near-identical answer accuracy (87.6% vs 88.6%). Mechanical proxies (length, markdown, hedges) do
not separate the arms: frontier "style" is subtler than surface features.

**P3 (descriptive ordering): consistent.** The certified style-loaded judge (1.5B noref, style
partial +0.33) has the largest noref gap (+0.88). Ordering across all noref configs is not monotone
in size (3B dips), as expected for a descriptive-only axis.

**P4 (flat curves for certified judges = defense finding): CONFIRMED** and bounded by the positive
control (+0.85), which bent 2.3x above the honest frontier judge (+0.38).

## The finding beyond the predictions: hacking has two failure modes, and judge capability trades
one for the other

Across the sabotage ladder, self-inflation rises and real damage falls with judge capability:

| sabotaged judge | inflation (excess gap) | damage (regret) |
|-----------------|------------------------|-----------------|
| Qwen-7B         | +0.13 (ns)             | 0.400           |
| Qwen-14B        | +0.61                  | 0.324           |
| GPT-5.2         | +0.85                  | 0.133           |

A weak style-loaded judge picks genuinely worse answers without producing impressive scores
(damage without inflation). A frontier style-loaded judge picks nearly as well as its honest
counterpart while inflating its own scoreboard (inflation without damage): it deceives the metric,
not the policy, at selection time. The deferred risk (a policy TRAINED against it internalizes
style) is Phase 1's question.

## Bonus finding: granularity beats scale once a reference is in hand

With the gold reference, Qwen-1.5B is a better best-of-64 selector than GPT-5.2 (regret 0.010 vs
0.117). The frontier judge's 0-10 scale saturates (78% top-ties even with logprob-expected scores);
random tie-breaks among its top-rated samples admit wrong answers. The small judge's continuous
escores stay sharp. Judge deployments that select (RLHF data filtering, BoN serving) should elicit
fine-grained scores; coarse scales waste frontier capability.

## Caveats

Oracle is strict boxed-string match (equivalence adjudication pending; only flips 0->1, so noref
regrets can only shrink slightly and the reference contrast is conservative). One generator, one
domain analyzed so far (code pools generated and oracle-scored; grid not yet run). Panel is a single
cross-family critic (Opus) pending human spot-labels on ~60 selected items. Realized selection
pressure differs across judges (frontier tie-saturation); cross-judge magnitude comparisons carry
that caveat, the paired within-judge contrast does not.

Data: runs/bon_scores_v2 (local mirror runs/bon_scores), runs/bon_v2_full.json,
runs/bon_panel_opus.jsonl, runs/bon_selected_sets.jsonl. Spend: $39.80 ledgered of $100.
