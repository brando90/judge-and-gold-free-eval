# v3 outline: "The Reference Is Not an Answer Key"

v3 is a deliberate rewrite of v2 (tag `paper-d-iclr-v2`, commit 938ad38): **same evidence, fewer numbers, shorter appendix, scoped claims.**
Inputs: lead-author feedback (2026-09-15), `D-iclr-v2/reviews/v2_final_ac_review.md` (8/10; text fixes T1-T10), R27 (P3 under
correctness prompts, done; false acceptance on hard HLE questions, running).

## Writing rules for v3
- **One message per paragraph**, stated in its first sentence.
- **Number budget:** abstract at most 6 numbers; intro at most 6; any body paragraph at most 5. Every other number lives in a figure,
  a table, or the appendix.
- **No registration marks in running text** unless the number is post hoc. The Setup states the convention once, and figure and table
  captions carry the rest.
- **Every claim traces to a source** (claims list below). Each sentence is checked against it after writing, not before.
- **Scope words are part of the claim:** "for LLM graders", "on questions the judge can answer", "two judges".

## Story in five sentences
1. Graders routinely give an LLM judge one reference and assume it acts as an answer key.
2. When a question has several correct answers, judges instead favor the one they are shown (P1-P3), and not only because they cannot
   verify the others.
3. Benchmark graders run as shipped, and RL-reward verifiers, under-credit such answers heavily; the questions are rare on those
   benchmarks but common in data the same graders are reused on.
4. Most of the shortfall comes from telling the grader to match; asking whether the answer is correct shrinks it, and a residual pull
   remains.
5. Listing every correct answer fixes LLM graders; when that is impossible, change the instruction, and audit.

## Section plan

| # | Section | Message | Changes from v2 |
|---|---|---|---|
| - | Abstract (~190 words) | Premise, failure, three readings, findings, practice, fix, implication | Mirage-style; no enumerated 110-word sentence; ends on the implication and the fix |
| 1 | Introduction | Practice and premise, then when it fails, three readings and P1-P3, what we find, scope | Opens without numbers; the 35/80 example described in words; "not about math" gets its own short paragraph |
| - | Figure 1 | Panels (a) task and candidate, (b) the same text scored three ways | Panel (c) moves to Appendix I; the caption loses its numbers |
| - | Table 1 | Claim, what it rules out, key evidence (one number), verdict | Qualitative; the failure list is replaced by "(F)" marks and a pointer to the ledger |
| 2 | A model of the three readings | Eq. 1 organizes P1-P3 | One added sentence: the instruction scales the agreement term (bridge to Section 7) |
| 3 | Setup | Tasks, judges and graders, reading answers, conventions | Adds Haiku 4.5 and the two verifiers; one sentence on prompt wording (see "rubric b" below) |
| 4 | P1: the score follows the reference | Swap on identical text | Keeps the three-judge numbers; points to Appendix I for the plot |
| 5 | P2: differing correct answers graded worse | Grading AUROC falls; one-answer control | Figure 2 title shortened |
| 6 | P3: persists after blind acceptance | Accepted-blind answers rejected once the reference appears | Adds R27-A: P3 holds under correctness prompts too |
| 7 | How much it matters, and what sets the size | Shipped graders and verifiers; where it matters (reuse, with the RL bound); the instruction ladder; our rubric and draws (short) | W1, W2, W5 fixes; reorder; about half the numbers |
| 8 | How to fix it | Lists (with the verifier exception and the closed-list caveat); instruction changes (with the R27-B hard-question result); what did not help; recipe | W3, W4 fixes; the "did not help" paragraph is one sentence per method |
| 9 | Related work | | Adds VerifyBench, JudgeBench, answer matching, QAMPARI, PEDANTS (bib entries verified before citing) |
| 10 | Limitations | | Adds hard-question scope of R27-B and the verifier exception |
| 11 | Conclusion | Mirage-style implication plus fix | W1/W4 scoping |

## The rubric-b point raised by the lead author
Our default referenced rubrics say "using the reference to check it" (a) and "Compare ... against the trusted reference answer" (b).
The "one valid answer among possibly many" sentence is a separate mitigation condition, not part of those rubrics. Setup will state
plainly that the default rubric invites comparison, and that the effect persists without that wording: under the MT-Bench template,
under a direct "is the response correct?" prompt, under reasoning prompts, and for answers accepted blind (R27-A).

## Claims list (each v3 sentence must map to one of these)

| ID | Claim | Source |
|---|---|---|
| C1 | Swapping the reference between two correct answers moves identical text by 3-5 points for three score-only judges | `tables/r4_rotation.tex`, `rotation_exact.tex`; App. I |
| C2 | Grading AUROC of differing correct answers falls for 4 of 5 judges on factual questions (GPT-4.1's interval includes zero) and for 4 open judges on arithmetic, under every labeling | `r20g`, `r16c`, `labelings_gnm.tex` |
| C3 | With one correct answer the reference raises selection accuracy (MATH-500) | `r16c` |
| C4 | Answers accepted blind that differ from the reference are rejected once it is shown; a second blind call does not reproduce this (API judges) | `r20a_*`, `r21a_mace_acceptance`, Fig. 3 |
| C5 | The same holds under correctness prompts (8 of 8 cells; 1-22% against 0-1%) | `r27a_*.json` |
| C6 | Shipped SimpleQA and BrowseComp/HLE graders score four models 30-67 points below the answer lists on multi-answer questions | `r24a_*.json` |
| C7 | Two open RL-reward verifiers credit 0-6% of differing correct answers with one reference | `r26c_*.json` |
| C8 | Those benchmarks rarely contain multi-answer questions (0-3%, LLM annotators, low agreement; lower bound); an RL training set has 5.5-18% | `prevalence_v2_results.json` |
| C9 | Implied share of that RL set's correct rollouts receiving no reward: roughly 4-12%, under a stated assumption | derived from C7, C8 and `r20c` (73% differ); stated as an estimate |
| C10 | Instruction ladder: match (-65/-67), HLE edit (-31/-13), direct (-17/-10), reasoning prompts (-0.5 to -6); reasoning matters for GPT-4.1, not by the registered test for Sonnet 5 | `r26a_*.json`, `r25_*.json` |
| C11 | Full answer list: five benchmark graders within 0.5 points; grading AUROC 0.03-0.06 above blind for three judges; CompassVerifier fixed; General-Reasoner's verifier not (24 short, 30% wrong accepted) | `r24a`, `r24c`, `r26c` |
| C12 | Solve-first on questions the judge can answer: smallest grading loss, still rejects 5-7 points more differing correct answers; on hard HLE questions: pending R27-B | `r26b_*.json`, `r27b_*.json` (pending) |
| C13 | Blind-then-reveal left grading below blind for most open judges; the max rule protects grading partly by construction and costs accuracy on unique answers | App. P (`r16*`, registered R2/R3) |
| C14 | Survey: 35 of 43 graders plus 34 papers use one reference; 27 of 34 prompts define correctness as matching; none credits answers outside it | `survey/practice_survey.md` |

## Figures and tables in the main text
- **Figure 1:** (a) and (b) only.
- **Table 1:** qualitative, at most one number per row.
- **Figure 2:** P2 (unchanged data; shorter title).
- **Figure 3:** P3 acceptance (unchanged).
- **Figure 4:** graders and fixes. Label the lower panel's axis scale, and add a ghost marker for the verbatim HLE judge on the zoomed
  panel.

## Appendix plan (target 20 pages or fewer; v2 has 49)

| Section | v2 pages | v3 | Notes |
|---|---|---|---|
| A Setup, prompts, conditions | 2 | 2 | Label the conditions of each prompt; add the rubric-b sentence |
| B Survey | 3 | 2 | Keep table and quotes; the full records stay in the supplement |
| C Prevalence (both audits) | 1 | 1 | |
| D Ledger | 5 | 2 | Summary table by round (predictions, confirmed, failed, key failures); full ledger moves to the supplement |
| E MACE audits | 1 | 1 | |
| F Labelings (grid) | 7 | 1.5 | Keep AUROC robustness; selection-accuracy grids go to the extended appendix |
| G Exact scorer and MATH-500 | 4 | 1 | |
| H Reasoning and thinking | 2 | 1 | |
| I Swap test (incl. v2 Figure 1c) | 1 | 1.5 | |
| J Masking and wording | 1 | 0.5 | |
| K Frontier judges | 1 | 0.5 | |
| L Acceptance, benchmark study, redraw | 8 | 3 | Keep P3 tables, benchmark and redraw/regrade tables; bins and per-model tables go to the extended appendix |
| M-O Rounds 24-26 | 4 | 3 | |
| New: R27 | - | 1 | |
| P Mitigations (blind-then-reveal, max rule) | 5 | 1.5 | One summary table |
| Q-U Composition, Ties, MathConstraint, code, training runs | 3 | 0.5 | One paragraph each for MathConstraint and code (cited in the main text); the rest go to the extended appendix |

**Extended appendix.** Everything cut is kept verbatim in `appendix_extended.tex`, compiled to `extended_appendix.pdf` and shipped in
the supplement. The main appendix says so once.

## Order of work
1. Mechanical, not dependent on R27-B: Figure 1 split, Table 1 redesign, intro opening, Setup additions, Section 7 reorder, appendix
   cut into main plus extended.
2. After R27-B: Section 8 no-list paragraph, recipe bullet 3, Limitations, Conclusion.
3. Abstract last, written from the final body.
4. Number check against the claims list; build (9 pages, Figure 1 on page 1); one QA pass; one final area-chair review.
