# Grading the Answer Key, Not the Student — AAAI-27 Workshop Draft

**Doc link:** <https://github.com/brando90/judge-free-eval/blob/main/paper_latex_and_notes/AAAI_2027_EvalAIScientists_ReferenceMatching/README.md>

**TLDR:** Anonymized 4-page AAAI-27 Workshop (*Effective and Efficient Evaluation for AI Scientists*, Position / Critique & Negative-Result track) edition of Paper B (`papers/B-reference-matching/`), with dual venue (`00_main_aaai_2027.pdf`, 4-page body + references + ~1.5x core appendices) and arXiv (`00_main_arxiv.pdf`, adding post-appendix Supplementary `S1–S3`) PDFs per Trigger Rule 89.

## Venue, Track, and Archetype

- **Target venue:** AAAI-27 Workshop on *Effective and Efficient Evaluation for AI Scientists* (<https://eval-ai-scientists.github.io/aaai27/>), OpenReview submission deadline `2026-11-20 06:00 UTC`.
- **Track:** Position / Critique & Negative-Result paper (`2–4` main-body pages excluding references, official `aaai2027.sty` two-column anonymized submission).
- **Paper archetype (`writing/ml_research/paper-archetypes.md`):** Primary **Countervailing Wisdom** (challenging the cost-versus-quality spectrum assumption in reference-based evaluation) supported by **Discovery** (cross-family item-variance decomposition and aggregate boundary map).
- **Why Paper B (and not Paper D or Paper A):** Paper D (`papers/D-reference-laws/`) was spun out into `aryanguls/judge-reference-anchoring/papers/AAAI27/` targeting this exact workshop; Paper B is `judge-free-eval`'s unsubmitted core TFA/reference-similarity study, and scoping it as a 4-page critique/negative-result submission resolves prior NeurIPS main-track concerns regarding untested trained similarity models and extractable-endpoint scope.

## Dual Build (Trigger Rules 35 & 89)

```bash
make -C paper_latex_and_notes/AAAI_2027_EvalAIScientists_ReferenceMatching
```

- `00_main_aaai_2027.pdf` — Venue PDF (`\supplementaryfalse`): 4 main-body pages (`Conclusion` ends on Page 4, `References` begins on Page 5) + ~5.5–6.0 pages of core appendices (`A–C`), committed alongside sources.
- `00_main_arxiv.pdf` — arXiv companion PDF (`\def\withsupplementary{1}` via `00_main_arxiv.tex`): identical body/references/core appendices + post-appendix Supplementary `S1–S3` (`10-supplementary.tex`).
- Figures regenerate deterministically from `papers/analysis/canonical_validity.json`, `papers/analysis/free_baseline.json`, and `experiments/tfa-vs-judge/runs/tfa_bpc_math500.jsonl` via `scripts/generate_plots.py`.

## Provenance

Every number traces directly to `papers/analysis/*.json` (`canonical_validity.json`, `free_baseline.json`, `bit_vs_curve_paired.json`, `decomp_cis.json`, `completer_sweep.json`, `pv_completer.json`, `strong_baselines.json`, `code_sims.json`, `answerline_delta_itemlevel.json`, `answerline_delta_ci.json`, `padref_control.json`, `padref_delta_itemlevel.json`, `within_correct_tost.json`, `within_correct_cis.json`, `interrater.json`) and `papers/B-reference-matching/`.
