# ICLR 2027 submission checklist and OpenReview metadata (Paper D)

Deadlines (ICLR 2027 author guidelines): abstract registration **Sep 18, 2026 AOE**; full paper **Sep 25, 2026 AOE**. Supplementary material follows the full-paper deadline; check OpenReview for the exact supplementary cutoff.

## Metadata to paste into OpenReview

- **Title:** see `main.tex` `\title` (keep identical in OpenReview).
- **Abstract:** paste the plain-text version of the `abstract` environment (replace `\%` with `%`, `$n$` with n).
- **TL;DR:** When a question has several valid answers, LLM judges grade agreement with the one reference answer they are shown; extended thinking removes this only where the judge can verify the answer itself, and whether it costs best-of-n accuracy depends on how well the judge verifies without the reference.
- **Keywords:** LLM-as-a-judge, reference-guided evaluation, best-of-n selection, anchoring, verification, reasoning judges, multiple correct answers, preregistration
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
