# Style-loading test on divergence cases (2026-08-09)

Directly answers Sanmi/Brando point 2: "everything item-level is agreement with a judge (reliability, not
validity); if the judge is style-loaded, TFA failing to track it isn't clean evidence TFA can't grade."

## Setup

20 TFA-vs-judge divergence cases (diagnostic cells A/B/C/D/F), re-graded by author 1 on the soundness+style
rubric. These cells are selected where TFA and the judge disagree, which is exactly where human soundness and
style pull apart — so the axes decouple and the style-loading test has power:

- soundness vs style correlation: **+0.31** here (vs +0.82 in the near-ceiling random block, where the test is
  underpowered). soundness mean 6.7 (sd 3.4), style mean 8.1 (sd 1.5).

Single rater (author 1), n=20. Divergence-selected, so magnitudes are not population estimates; the *comparison*
between soundness- and style-tracking is what this sample is built to support.

## Result

| relationship | Spearman ρ | 95% CI | partial (other axis held fixed) |
|---|---|---|---|
| judge vs **soundness** | **+0.78** | [+0.57, +0.89] | **+0.77** |
| judge vs style | +0.20 | [−0.26, +0.60] | −0.08 |
| TFA vs soundness | −0.13 | [−0.53, +0.31] | +0.04 |
| TFA vs **style** | **−0.53** | [−0.81, −0.10] | −0.51 |

## Reading

- **The judge is not style-loaded.** Its correlation with human grades is almost entirely soundness (+0.77
  controlling for style); the style component vanishes (−0.08 controlling for soundness). On this dataset the
  judge tracks substance, not surface.
- **TFA is detached from soundness.** It carries no soundness signal even on cases designed to test it (partial
  +0.04) and its item-level behavior is a style reaction (partial −0.51; negative because the divergence set
  includes valid-but-different-style solutions TFA penalizes).
- **So "TFA fails to grade" is now clean and direct**, not laundered through the judge: TFA does not track human
  soundness. And because the judge *does* track soundness, using it as the item-level target was defensible after
  all.

## Caveats / next

- n=20, single rater, divergence-selected. Needs author 2's (Daneshvar) re-grade of the same 20 for inter-rater
  on the new axes and to confirm the pattern.
- The unbiased magnitudes (population ρ) come from the random block (Author 1's 20 + Author 2's 80). The random
  block is near-ceiling, so it gives the honest effect sizes but weak style separation; the divergence block gives
  the style separation. The two strata are complementary and answer different halves of the question.

Reproduce: the inline analysis in the chat; inputs are author1_sri_with_style.json + traces_to_label.jsonl +
runs/prm_labelset/.

## Update: random block n=30 (2026-08-09)

As harder items entered (correct rate 80%, vs the easy first-20's 90%), the unbiased read sharpened and now
matches the divergence block:

| vs human soundness | ρ | 95% CI |
|---|---|---|
| LLM judge | +0.57 | [+0.12, +0.81] excl. 0 |
| rollout PV | +0.48 | [+0.08, +0.77] excl. 0 |
| TFA | −0.00 | [−0.39, +0.37] |

Style-loading partials (random, n=30): judge soundness|style +0.48, style|soundness −0.07; TFA soundness|style
+0.17, style|soundness −0.24. Same pattern as the divergence block.

Note: TFA vs soundness fell from +0.36 at n=20 (an unusually easy draw, 90% correct) to 0.00 at n=30, confirming
the +0.36 was subsample luck, not signal. Continue random labeling toward n=80 to tighten the CIs; the qualitative
three-way separation (judge & PV track soundness, TFA does not; judge not style-loaded) is stable across both the
divergence and random strata, single rater (Sri). Second rater (Daneshvar) still needed for inter-rater on the new axes.

## Update: random block n=41 (2026-08-09)

| vs human soundness | ρ | 95% CI |
|---|---|---|
| LLM judge | +0.52 | [+0.13, +0.75] excl. 0 |
| rollout PV | +0.34 | [+0.01, +0.63] excl. 0 (softening) |
| TFA | −0.04 | [−0.35, +0.29] |

Style-loading partials (n=41): judge soundness|style +0.47, style|soundness +0.06; TFA soundness|style 0.00,
style|soundness −0.11. Judge-tracks-soundness-not-style is now stable across n=20/30/41 and the divergence block.

Watch item: PV vs soundness has drifted 0.59 (n=20) -> 0.48 (n=30) -> 0.34 (n=41) as harder items entered; CI now
barely excludes zero. "PV grades where TFA cannot" holds directionally but is more modest than the easy-draw
suggested. Remaining ~40 random labels + Daneshvar's second-rater pass will settle it.

## Update: random block n=50 (2026-08-09) — halfway, stable

| vs human soundness | ρ | 95% CI |
|---|---|---|
| LLM judge | +0.51 | [+0.17, +0.74] excl. 0 |
| rollout PV | +0.39 | [+0.10, +0.64] excl. 0 |
| TFA | −0.09 | [−0.39, +0.20] |

Style-loading partials (n=50): judge soundness|style +0.46, style|soundness +0.12; TFA soundness|style −0.04.
Three-way separation stable: judge (~0.51) > PV (~0.39) > TFA (~0). Judge-not-style-loaded holds at n=20/30/41/50
and on the divergence block. PV settled ~0.39 after the early wobble. Single rater (Sri); n toward 80 + Daneshvar
second-rater still pending.
