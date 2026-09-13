# ICLR 2027 submission checklist and OpenReview metadata (Paper D)

Deadlines (ICLR 2027 author guidelines): abstract registration **Sep 18, 2026 AOE**; full paper **Sep 25, 2026 AOE**. Supplementary material follows the full-paper deadline; check OpenReview for the exact supplementary cutoff.

## Metadata to paste into OpenReview

- **Title:** see `main.tex` `\title` (keep identical in OpenReview).
- **Abstract:** paste the plain-text version of the `abstract` environment (replace `\%` with `%`, `$n$` with n).
- **Title (round 9):** The Reference Is Not an Answer Key: LLM Judges Grade Agreement with One Correct Answer
- **TL;DR:** On questions with several correct answers, a reference is one sample of the correct answers, and LLM judges grade agreement with it: swapping it moves the score of unchanged text, correct answers that differ from it are graded as failing (even for Sonnet 5 and for thinking judges on factual questions), and scoring blind before revealing the reference removes the resulting best-of-n inflation.
- **Keywords:** LLM-as-a-judge, reference-guided evaluation, multiple correct answers, anchoring, best-of-n selection, reasoning judges, evaluation reliability, preregistration
- **Primary area (suggested):** alignment, fairness, safety, privacy, and societal considerations — alternative: datasets and benchmarks / evaluation. Pick whichever area list ICLR 2027 shows that mentions evaluation of foundation models.

## Before submitting

- [ ] `latexmk -pdf main.tex` builds with no undefined references; main text ends on or before page 9.
- [ ] `python scripts/make_figures.py && python scripts/make_tables.py` regenerated from current `papers/analysis/*.json`.
- [ ] `python scripts/check_numbers.py`: every flagged number checked by hand (as of round 3: 46 = ledger sum, 825 = MACE subsample size from `r3_build_subsamples.py`, 1,200 = split by the thousands separator in the registration).
- [ ] Optional before the deadline: if the Claude subscription usage limit resets, resume the R3-B visible and thinking arms (`experiments/tfa-vs-judge/scripts/sonnet_cli_judge.py --arm visible|think --cond ref|refrot`, resumable), rerun `r3_sonnet_analysis.py`, and score P-R3B2–B4 in the ledger.
- [ ] PDF metadata anonymous: `pdfinfo main.pdf` shows no author; no acknowledgments; no OSF links in the PDF.
- [ ] `supplement.zip` under 100 MB, anonymization audit clean (see `supplement/README.md`).
- [ ] AI use statement present (required in 2027), ethics and reproducibility statements present.
- [ ] Every author has an OpenReview profile; at least one author registered as reviewer (reciprocal reviewing requirement).
- [ ] OSF registrations: confirm the view-only anonymized links work in a logged-out browser before pasting them into the supplement.
