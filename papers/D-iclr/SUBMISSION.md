# ICLR 2027 submission checklist and OpenReview metadata (Paper D)

Deadlines (ICLR 2027 author guidelines): abstract registration **Sep 18, 2026 AOE**; full paper **Sep 25, 2026 AOE**. Supplementary material follows the full-paper deadline; check OpenReview for the exact supplementary cutoff.

## Metadata to paste into OpenReview

- **Title:** see `main.tex` `\title` (keep identical in OpenReview).
- **Abstract:** paste the plain-text version of the `abstract` environment (replace `\%` with `%`, `$n$` with n).
- **TL;DR:** When a question has several valid answers, a reference answer makes LLM judges grade agreement with it rather than correctness, which best-of-n selection and training exploit; scoring blind first and then revealing the reference with the blind score removes the measured harm.
- **Keywords:** LLM-as-a-judge, reference-guided evaluation, reward hacking, Goodhart's law, best-of-n selection, anchoring bias, evaluation, multiple correct answers
- **Primary area (suggested):** alignment, fairness, safety, privacy, and societal considerations — alternative: datasets and benchmarks / evaluation. Pick whichever area list ICLR 2027 shows that mentions evaluation of foundation models.

## Before submitting

- [ ] `latexmk -pdf main.tex` builds with no undefined references; main text ends on or before page 9.
- [ ] `python scripts/make_figures.py && python scripts/make_tables.py` regenerated from current `papers/analysis/*.json`.
- [ ] `python scripts/check_numbers.py` reports 0 unsourced numbers.
- [ ] PDF metadata anonymous: `pdfinfo main.pdf` shows no author; no acknowledgments; no OSF links in the PDF.
- [ ] `supplement.zip` under 100 MB, anonymization audit clean (see `supplement/README.md`).
- [ ] AI use statement present (required in 2027), ethics and reproducibility statements present.
- [ ] Every author has an OpenReview profile; at least one author registered as reviewer (reciprocal reviewing requirement).
- [ ] OSF registrations: confirm the view-only anonymized links work in a logged-out browser before pasting them into the supplement.
