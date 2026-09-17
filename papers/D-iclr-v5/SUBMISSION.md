# ICLR 2027 submission checklist and OpenReview metadata (Paper D)

Deadlines (ICLR 2027 author guidelines): abstract registration **Sep 18, 2026 AOE**; full paper **Sep 25, 2026 AOE**. Supplementary material follows the full-paper deadline; check OpenReview for the exact supplementary cutoff.

## Metadata to paste into OpenReview

- **Title:** see `main.tex` `\title` (keep identical in OpenReview).
- **Abstract:** paste the plain-text version of the `abstract` environment (replace `\%` with `%`, `$n$` with n).
- **Title (v5):** Reference Anchoring Biases LLM Judges Toward the Answer They Are Shown When Several Are Correct
  - Superseded (v3, round 18): The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown. Retitled in v5 because the v3 title asserted unconditionally what P2 refutes on single-answer questions, where the reference helps.
- **TL;DR (v5):** When a question has several correct answers, LLM judges favor the one given as the reference: swapping it moves the score of identical text by about 3 to 5 points out of 10, correct answers that differ from it are rejected even when the judge accepts them without a reference, and benchmark graders run as shipped score four models 30 to 67 points below their answer-list accuracy. With one correct answer the reference helps instead.
- **Keywords:** LLM-as-a-judge, reference-guided evaluation, multiple correct answers, anchoring, best-of-n selection, reasoning judges, evaluation reliability, preregistration
- **Primary area (suggested):** alignment, fairness, safety, privacy, and societal considerations — alternative: datasets and benchmarks / evaluation. Pick whichever area list ICLR 2027 shows that mentions evaluation of foundation models.

## Before submitting

- [x] `latexmk -pdf main.tex` builds with no undefined references; main text ends on or before page 9. (v5: verified — 0 undefined refs, 0 overfull boxes; Limitations closes page 9 and page 10 begins with the AI use statement, matching v3.)
- [ ] `python scripts/make_figures.py && python scripts/make_tables.py` regenerated from current `papers/analysis/*.json`.
- [x] `python scripts/check_numbers.py`: every flagged number checked by hand. v5 flags 5, none in `main.tex` and all in `appendix.tex`: 420 (the Figure 1 length rule), +4.69 (a CI bound quoted in a caption), and 7152, 1011 and 1192 (call counts). The ledger totals used to be flagged because they were typed rather than produced by a script, which a fresh AC review called an avoidable target for a paper whose distinguishing strength is the ledger. The checker now derives them: it sums each column of `tab:ledger-totals` and verifies it against that column's printed Total (290 and 14), printing a mismatch if they ever diverge. Run it after any ledger edit.
- [x] R3-B visible and thinking arms were completed after the usage limit reset (round 5); nothing pending.
- [ ] PDF metadata anonymous: `pdfinfo main.pdf` shows no author; no acknowledgments; no OSF links in the PDF.
- [x] `supplement.zip` under 100 MB, anonymization audit clean (see `supplement/README.md`). v5: rebuilt at 67 MB, 1613 entries, no junk files; its inventory matches the v3 archive except for the retired v3 PDF and the added v5 PDF. Anonymization audit clean — no author names (the only hit is a third-person bibliography entry), no project commit hashes, no `osf.io`, no `stanford.edu`, no absolute local paths, and every GitHub reference is to a third-party project. The two R27 run-driver logs were restored from the vetted v3 archive rather than the repository, because the shipped copies are shortened. Reverified for v5: the shipped sources compile from a fresh folder to a 38-page paper and a 54-page extended appendix with no undefined references or overfull boxes, and their extracted text is identical to the shipped PDFs; `check_numbers.py` runs in the supplement layout and reports the same five flags as the project copy.
- [ ] AI use statement present (required in 2027), ethics and reproducibility statements present.
- [ ] Every author has an OpenReview profile; at least one author registered as reviewer (reciprocal reviewing requirement).
- [ ] OSF registrations: confirm the view-only anonymized links work in a logged-out browser before pasting them into the supplement.
