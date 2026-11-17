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

- `00_main_aaai_2027.pdf` — Venue PDF (`\supplementaryfalse`): 8 pages total (main body ends with `Conclusion` on Page 4, `References` span Pages 4–5, and Core Appendices `A–C` span Pages 5–8, well within the 1.5x cap), committed alongside sources.
- `00_main_arxiv.pdf` — arXiv companion PDF (`\def\withsupplementary{1}` via `00_main_arxiv.tex`): 10 pages total (identical body/references/core appendices + post-appendix Supplementary `S1–S3` from `10-supplementary.tex` on Pages 9–10).
- Figures regenerate deterministically from `papers/analysis/canonical_validity.json`, `papers/analysis/free_baseline.json`, and `experiments/tfa-vs-judge/runs/tfa_bpc_math500.jsonl` via `scripts/generate_plots.py`.

## OpenReview Submission Packet

- **Portal URL:** <https://openreview.net/group?id=AAAI.org/2027/Workshop/EvalAIScientists> (deadline `11-20-2026 06:00 UTC`).
- **Title:** `Grading the Answer Key, Not the Student: Reference-Matching Metrics Measure Reference Predictability, Not Solution Soundness`
- **Track:** Position / Critique & Negative-Result paper (`2–4` main-body pages excluding references).
- **TL;DR (237 chars):** `Untrained reference-matching metrics (including Teacher-Forced Accuracy) fail per-solution grading because 83-92% of variance is reference predictability; zero-cost endpoint checks (+0.92) beat rollout verifiers (+0.79).`
- **Keywords:** `evaluation methodology`, `teacher-forced accuracy`, `reference-based metrics`, `construct validity`, `LLM-as-a-judge`, `benchmark metrology`
- **Abstract (single paragraph, matches `1-abstract.tex`):**
  > Evaluating scientific and mathematical reasoning at scale often pairs a benchmark's worked gold reference with a cheap reference-matching metric instead of paying a frontier large language model (LLM) judge or a human expert. This practice assumes that reference-matching metrics approximate human grading quality with added noise along a single cost-versus-quality spectrum. We show across seventeen instruction-tuned models from four families on eight math and code benchmarks plus an agentic repository setting that untested reference-matching metrics measure how predictable the reference text is rather than whether a candidate solution is sound. Anchored to sixty blind human-graded MATH-500 solutions (with an external hypothesis-blind second rater agreeing at Pearson r = 0.83) and 492 executed code solutions, we separate reference-matching metrics from endpoint verification signals via cross-family variance decomposition and causal reference interventions. Every untrained text-matching metric we tested, from teacher-forced accuracy (TFA) and token log-probability to retrieval embeddings and entailment, sits in [-0.33, +0.14] against human reasoning soundness (0.00 to +0.17 against executed code tests), because 83-92% of TFA per-solution variance is a cross-family item effect reflecting reference perplexity (r = -0.895). Averaging cancels this shared item effect so TFA ranks models on hard olympiad sets (cross-family rho = +0.86), yet collapses under length-matched boilerplate controls (paired item-bootstrap Delta rho = +0.41 [+0.35, +0.46]) and inverts on saturated sets, while an extracted-answer check achieves r = +0.92 [+0.78, +0.99] and outperforms a thirty-two-rollout completion curve (Delta r = +0.13 [+0.05, +0.24]). Benchmark evaluation should treat gold references as checkable endpoints for verifiers rather than similarity targets for untrained scorers, and leaderboards using TFA should report reference perplexity alongside accuracy.
- **PDF to upload:** `paper_latex_and_notes/AAAI_2027_EvalAIScientists_ReferenceMatching/00_main_aaai_2027.pdf` (double-blind `Anonymous submission`).
- **Candidate co-authors to confirm before final Submit:** Brando Miranda (`brando9@stanford.edu`), Srivatsava Daruru (`vatsava@gmail.com`), Daneshvar Amrollahi (`daneshva@stanford.edu`), Aryan Gulati (`aryanguls@gmail.com`), Sanmi Koyejo (`sanmi@stanford.edu`).

## Provenance

Every number traces directly to `papers/analysis/*.json` (`canonical_validity.json`, `free_baseline.json`, `bit_vs_curve_paired.json`, `decomp_cis.json`, `completer_sweep.json`, `pv_completer.json`, `strong_baselines.json`, `code_sims.json`, `answerline_delta_itemlevel.json`, `answerline_delta_ci.json`, `padref_control.json`, `padref_delta_itemlevel.json`, `within_correct_tost.json`, `within_correct_cis.json`, `interrater.json`) and `papers/B-reference-matching/`.
