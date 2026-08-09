# Phase 1 human-label results (2026-08-09)

Two annotators (Sri, Daneshvar) each graded the **same first 20 diagnostic traces** (cells A/B/C/D/F).
These are the *disagreement-selected* cells (chosen where TFA and the LLM judge disagree), so the numbers
below are **directional, not final** — the unbiased validity correlations need the random stratum (in
progress: 20 more diagnostic + 222 random still to label).

## Inter-rater agreement (the human-human ceiling)

On overall quality (0-10), n=20 double-labeled:

| Spearman | Pearson | Kendall | ICC(A,1) | mean \|diff\| | within 2 pts |
|---|---|---|---|---|---|
| +0.80 | +0.80 | +0.65 | +0.77 | 1.7 pts | 15/20 |

Humans agree well but not perfectly. This ceiling (~0.80) bounds what any automated signal can be
credited with: a judge cannot be shown "more valid" than humans are with each other.

Categorical exact agreement: answer_correct 95%, complete 70%, steps_valid 65%, lucky 60%. The finer
sub-judgments (which step is invalid, was it lucky) are noisier than the overall grade, as expected.

## The adjudication: on disagreement cells, humans side with the judge, not TFA

| cell | construction | human quality | judge | verdict |
|---|---|---|---|---|
| A | TFA high, judge low | 4.1/10 | 4.2/10 | humans side with the **judge** (TFA was wrong to call these good) |
| B | TFA low, judge high | 8.9/10 | 10.0/10 | humans side with the **judge** (TFA wrongly penalized valid solutions) |
| C | correct, judge low (lucky?) | 3.3/10 | 2.0/10 | humans confirm weak reasoning behind a correct answer |
| D | both high | 9.0/10 | 9.5/10 | calibration anchor, all agree |
| F | wrong, judge low | 1.5/10 | 0.8/10 | all agree |

In **both** disagreement directions (A and B), the human grade lands next to the judge and far from what
TFA implied. Directional correlations on these 20: judge-vs-human Spearman **+0.88**, TFA-vs-human **-0.16**.

## What this does and does not show

- **Addresses Brando's point 2 (reliability vs validity), directionally.** The concern was that item-level
  results are "agreement with a possibly style-loaded judge." On the hardest cases (where TFA fights the
  judge), humans back the judge, and TFA anti-correlates with human quality. That is early evidence the
  judge is tracking real reasoning quality, not surface, and that TFA's item-level failure is a genuine
  failure rather than the judge being wrong.
- **Does NOT yet give the clean validity number.** These cells are selected on judge-TFA disagreement, which
  is why judge-vs-human (+0.88) even exceeds the human-human ceiling (+0.80) — an artifact of selection, not
  a real effect size. The unbiased rho(judge, human), rho(TFA, human), rho(PV, human) come from the random
  stratum (cell R), still to be labeled.

## Reproduce

`python scripts/analyze_human_labels.py human_eval/labels/phase1/*.json`
Labels merge by trace id, so re-running after more come in just extends these.
