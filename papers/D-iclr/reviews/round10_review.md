# Round 10 review: "The Reference Is Not an Answer Key: LLM Judges Reward Agreement When Several Answers Are Correct"

Reviewer role: NeurIPS reviewer / ICLR area chair. Sources read: the 39-page PDF (all pages), `main.tex`, `figures/fig1_concept.tex`, `scripts/make_figures.py` (font sizes), `analysis/r9_*.json`, `r8_sonnet_results.json`, `r8_lenient_results.json`, `r4_results.json`, `frontier_synthk_results.json`, `exploit_dose.py` (labels used), and registration files where a claim's status mattered. I did not open earlier reviews or the supplement.

---

## Summary

The paper argues that LLM judges given a reference answer do not treat it as an answer key. On questions with several correct answers they treat it as one sample of the correct set and reward agreement with it. The central test is clean and new. Moving the reference between two correct answers changes the score of byte-identical text by about 3 to 5 points out of 10 for Qwen2.5-7B, phi-4, and Claude Sonnet 5 (Fig. 1c, Table 4). Around this test the paper builds three predictions: P1, the score follows the reference; P2, the harm needs a second correct answer; P3, knowing an answer is correct does not protect it. It tests them on constraint tasks with enumerated answer sets, on MACE factual questions, on MATH-500, and on MBPP, using twelve judges. A long preregistration ledger scores 156 predictions. The P1 evidence is strong and the design is careful. The grading-AUROC evidence for P2 is solid. The registration bookkeeping is unusually honest. But the story on pages 1 to 3 still claims more than the evidence supports in several places. The page-1 claim "P1 holds for every judge we swapped references on" is contradicted by the ledger. The "ten of ten" and "seven of seven" counts are built from selected judge-pool pairs. P3 is not actually a prediction of the stated alternative, and its verdict hides a clear failure. The selection-accuracy null for Sonnet 5 is guaranteed by the subsample design. The natural-data selection results, which ran against the thesis, are missing from the abstract. The prose in the results sections reads like a ledger, and two main-text figures are set below 7 pt. None of these problems needs new data. All of them must be fixed before I could argue for acceptance.

---

## Scores

- **Overall:** 5 / 10 (marginally below the acceptance threshold)
- **Presentation:** 2 / 4
- **Soundness:** 3 / 4
- **Contribution:** 3 / 4
- **Confidence:** 4 / 5

**Would I champion this at 8+?** No.

**Conditions that would get me to 8:**
1. P3 is restated as a test of a named third explanation (a failure to verify), with a verdict of "partly holds" and its failures shown in Table 1 (Must-fix 1).
2. Every universal quantifier in the abstract, "What we find," Table 1, the verdict lines, and the conclusion matches the evidence and names the judges it excludes (Must-fix 2).
3. The abstract and conclusion report the natural-data selection results and the blind-then-reveal failure on MACE (Must-fix 3).
4. The selection-versus-grading comparison is rescoped to candidate-pool composition, and Sonnet 5 is removed from the selection-accuracy evidence (Must-fix 4).
5. The post hoc dagger marks are audited line by line, and Table 1's caption states that verdicts use a rule adopted after outcomes were known (Must-fix 5).
6. Figure 1 shows the "several answers" condition from the title, and every main-text figure is at 7 pt or larger (Must-fix 6).
7. Sections 5 to 7 are rewritten in plain prose, with registration bookkeeping moved to Table 1 and Appendix B (Must-fix 7).

Even with all seven, contribution caps near 7 unless the paper says concretely where multi-answer references occur in practice. Its own audit finds 0% to 2.5% multi-answer items on curated math sets (Should-fix 9).

---

## Strengths

1. **One clean, visual test.** The swap test (Fig. 1b) is the kind of experiment a reader remembers: same text, same judge, and only the choice of correct reference changes. The numbers in Fig. 1b are real (Qwen2.5-7B: 10.0 blind, 2.9 with reference 35, 9.3 with reference 80), not a cartoon.
2. **P1 is robust.** The gain and loss are symmetric, and the placebo ("matches neither") stays near zero. I verified the exact-scorer values against `r4_results.json`: gainer +5.25 [4.97, 5.53], loser −5.41 [−5.73, −5.09], placebo +0.12. The effect replicates across rubrics, scorers, and greedy integers (Table 45), in a frontier judge, and on a third-party combinatorial benchmark (Appendix P).
3. **The grading result is the strongest evidence for P2 and survives relabeling.** The drop in AUROC for non-matching correct answers versus wrong ones appears under three labelings for all four open judges that pass the resolution screen, and for Sonnet 5 on MACE: 0.938 → 0.785 (`r8_sonnet_results.json`, `G_nm_blind` 0.9378, `G_nm_ref` 0.7847).
4. **A good control on unique answers.** MATH-500 (+28.6 to +30.6 points of accuracy) and MACE k=1 show that the reference helps when there is one correct answer. That is what the one-sample reading predicts.
5. **Honest bookkeeping.** Falsified predictions are reported: the distance gradient, the code exemplar, blind-then-reveal on MACE, neutral wording, and the composition dose. The labeling problem (38% to 43% of replies unboxed) is surfaced rather than hidden, and the primary endpoint is recomputed under corrected labels (Table 16; I verified it against `r9_inflation_relabeled.json`: pooled any-format 1.137 [0.984, 1.294]).
6. **Compliance.** The main text ends on page 9. The AI-use, ethics, and reproducibility statements are present. PDF metadata is empty. I found no author names, institutions, or OSF URLs in the text. The self-adjacent citation (Chen et al., 2026) is written in the third person.

---

## Must-fix before submission (ranked)

### 1. P3 is not a prediction of the stated alternative, and its verdict hides a failure

**Where:** page 2, the P3 bullet; Section 2, line 138 ("nothing in Equation (1) depends on whether the judge already knew c was correct (P3)"); Section 6; Table 1, P3 row; abstract, sentence 5.

**What is wrong:**
- The introduction says of all three predictions that "each would fail if the reference acted as an answer key." That is false for P3. Under the answer-key reading there is no effect, so "prior acceptance does not remove the effect" is vacuous.
- P3 actually tests a third explanation that the paper never names: the judge anchors because it cannot verify the other answer. Section 6's own opening sentence says so: "If the judge merely did not know that the other answer was correct, three things should remove the effect."
- Equation (1) does not predict P3. It is silent on P3. Absence of a term is not a prediction.
- Under the paper's own prediction ("reasoning before scoring should not remove the effect"), P3 fails for all three reasoning judges on arithmetic: Qwen3-8B −0.69 → +0.01, Qwen3-14B −1.98 → −0.12, Sonnet 5 −2.85 → −0.20.
- P3 also fails for phi-4 under the instruction arm (+1.91 → +0.03), which Table 1 lists as a P3 test.
- The verdict "Holds, except reasoning on arithmetic" presents a split result as a confirmation.

**Fix:**
- Name the third explanation on page 1 and restate P3 as ruling it out. Suggested bullet:
  > **P3 The effect is not a failure to verify.** If judges anchored only because they could not tell that another answer was correct, anchoring would vanish for answers the judge already accepted blind, for stronger judges, and for judges that reason before scoring (Section 6).
- In Section 2, replace "and nothing in Equation (1) depends on whether the judge already knew c was correct (P3)" with:
  > A verification-failure account instead predicts that λ shrinks as the judge becomes able to check c; P3 tests this.
- Table 1, P3 verdict: "**Partly holds.** Holds for blind-accepted answers and frontier judges (smaller effect); fails for reasoning judges on arithmetic and for phi-4 with an any-valid-answer instruction."
- Section 6 verdict:
  > P3 partly holds. Anchoring persists for answers the judge accepted blind, for frontier judges, and on factual questions even with thinking on. It disappears when reasoning judges can check arithmetic, which is what a verification-failure account predicts for that domain.
- Abstract sentence 5: "Third, the effect is not simply a failure to verify: it persists for answers the judge accepted blind and for frontier judges, but judges that reason before scoring stop anchoring on arithmetic."

### 2. Universal claims contradicted by the paper's own evidence

**Where:** page 2, "What we find"; the abstract; Table 1, P1 and P2 rows; Section 5, line 210.

**(a) "P1 holds for every judge we swapped references on" (page 2, line 89).**
- The ledger (Table 3, "Judges that write first: thinking judge (Qwen3-8B)") records "Rotation gain (**not confirmed**); rotation loss (**not confirmed**)."
- Table 6 shows Qwen3-8B moving by −0.006 and +0.011 points. Fig. 4a shows Qwen3-14B with thinking on at −0.12 and Sonnet 5 reasoning at −0.20.
- Fix: "P1 holds for every judge that scores without reasoning: identical text gains 3.0 to 5.3 points when the reference is moved onto its answer and loses about as much when it is moved off. Judges that reason before scoring on arithmetic barely move (Section 6)."
- Table 1, P1 verdict: "Holds, 3 of 3 judges scoring without reasoning."

**(b) "higher with several correct answers than with one in all ten judge–pool pairs" (abstract; page 2; Table 1).**
- The ten pairs are 2 k-pool judges, 2 MACE judges, and 6 grid judges.
- The paper measured more pairs. On the k-pool (Table 38), Qwen2.5-14B (−0.30 → +0.98) and gemma-2-9b (−0.05 → +1.43) support the claim and are left out. Mistral-7B (+0.07 → +0.03) does not support it.
- GPT-4.1's step is +0.27 [−0.02, +0.61] on the k-pool. On the synthetic grid it is −0.08, with the k>1 level at −0.112 [−0.221, −0.010] (`frontier_synthk_results.json`).
- The count is therefore neither "all" nor chosen by a stated rule. The honest version is actually stronger.
- Fix: "higher with several correct answers than with one in all 12 judge–pool pairs whose scores passed our resolution screen (excluding zero at k>1 in 9); the two judges that failed the screen, Mistral-7B and GPT-4.1, show no step."
- The grid step is a post hoc paired re-analysis (Fig. 2 caption, Table 11). Add "post hoc" to that row's Evidence cell.

**(c) "for all seven judges measured" (abstract), "7 of 7" (Table 1).**
- The seven include Mistral-7B. Figure 3 omits Mistral-7B "because its integer scores failed our resolution screen," and the text says its fall is "none with boxed replies only" (Table 13: +0.01 [−0.05, +0.07]).
- GPT-4.1's k-pool change under any-format labels is −0.01 [−0.04, 0.00].
- A judge cannot be excluded from the figure for failing the screen and still counted in the headline.
- Fix (abstract): "correct answers that differ from it become harder to tell from wrong ones for every judge that passed our score-resolution screen".
- Fix (Table 1): "AUROC falls for all 5 screened judges: by 0.16–0.33 for four open judges under three labelings (0.07–0.14 with boxed replies only); 0.94 → 0.78 for Sonnet 5 on factual questions; small (≤0.10) and not robust for Mistral-7B and GPT-4.1."

**(d) "most for Sonnet 5 on factual questions" (page 2, line 93), and "largest for a frontier judge on natural data" (Section 5, line 210).**
- Sonnet's fall is 0.15. Qwen2.5-7B's is 0.30 on the k-pool and 0.27 on the replication pool (Fig. 3a).
- The Limitations say Sonnet's AUROCs "are not directly comparable to the 64-candidate open-judge values," so no ranking should be implied at all.
- Fix (page 2): "including Sonnet 5 on factual questions".
- Fix (Section 5): "and it also appears for a frontier judge on natural data: on MACE's multi-answer questions, Sonnet 5's grading AUROC falls from 0.94 to 0.78 (a different subsample design; Section 9)."

**(e) "With answers read in any format, the accuracy change at k=1 is zero for every judge" (Section 5, line 249).**
- Table 12 gives Mistral-7B −3.3 and GPT-4.1 −0.1.
- Fix: "is zero for all four open judges that passed the resolution screen."

### 3. The abstract and conclusion omit the natural-data results that went against the thesis

**Where:** abstract, last sentence; Section 10, conclusion; Table 1, "Costs and fixes" row.

**What is wrong:**
- MACE is the only natural multi-answer dataset. On it, the registered prediction that the reference lowers accuracy at k>1 was **not confirmed** for both judges.
- Showing the reference *raised* best-of-64 accuracy overall (+9.8 [+2.3, +17.3] and +11.3 [+5.2, +18.1], Table 44).
- Blind-then-reveal was *less* accurate than the reference alone (falsified for both judges).
- A reader who stops at the abstract concludes that references are harmful on multi-answer questions. The paper's own natural-data evidence says that for selection they are net helpful, and that the harm is in grading.
- The conclusion's "correct answers that differ from it are graded as failing" also overclaims: false-rejection rates rise by 6 to 64 points, so the effect is not universal.
- Table 1's "Costs and fixes" row does not mention the MACE falsification at all.

**Fix:**
- Replace the last abstract sentence with:
  > The cost falls on grading more than on selection: on natural multi-answer questions the reference did not lower best-of-64 accuracy, and scoring blind before revealing the reference removed the added inflation for two of four judges but was less accurate than the reference alone.
- Conclusion sentence 2: "...and correct answers that differ from it are often scored as failing, even ones the judge accepted without a reference..."
- Table 1, "Costs and fixes" result cell: append "on MACE the reference raised overall accuracy, and blind-then-reveal was less accurate than the reference (registered prediction falsified)".

### 4. The selection-accuracy evidence depends on pool composition; the Sonnet 5 null is guaranteed by design

**Where:** abstract ("Selection suffers less than grading"); page 2, line 95; Section 7, "Selection" ("Sonnet 5's best-of-16 accuracy does not change in any pool", "Grading, not selection, is where the reference does most of its damage"); Fig. 3b; Table 1, "Costs" row.

**What is wrong:**
- Appendix H states that each Sonnet 5 subsample holds "at least one matching-correct, one non-matching-correct, and one wrong answer." A judge that anchors on the reference will pick the matching correct answer, which is correct. A null accuracy change for Sonnet is therefore produced by the design and is not evidence that selection is protected.
- The same logic applies to the open-judge pools. Selection loses accuracy only when no correct candidate matches the reference, or when a wrong candidate echoes it. Appendix I (Table 27) shows that with no matching valid sample (d=0), the referenced judge picks a valid answer 14% of the time against 72% blind.
- "Selection suffers less than grading" is thus a statement about how often these pools contain a matching candidate, not a property of selection.
- The sentence also compares an AUROC change with accuracy points, which are not on a common scale.

**Fix:**
- Drop the Sonnet 5 rows from Fig. 3b, or mark them "subsample guaranteed to contain a matching correct answer; accuracy change uninformative." Delete "Sonnet 5's best-of-16 accuracy does not change in any pool."
- Replace "Grading, not selection, is where the reference does most of its damage" with:
  > In our pools, where a correct candidate matching the reference is usually present, the grading harm is robust across labelings but the selection-accuracy harm is not. When no candidate matches the reference, selection collapses (valid-pick rate 14% vs. 72% blind; Appendix I, registered labels).
- Abstract: replace "Selection suffers less than grading" with the sentence proposed in Must-fix 3.
- Page 2: replace "The harm is larger for grading than for selection" with "The grading harm is robust; the selection-accuracy harm depends on whether any candidate matches the reference".

### 5. Registration marks in the main text are not reliable

**Where:** page 2, line 101 ("Unmarked claims in the main text were preregistered on OSF or pre-specified in a timestamped commit"); Sections 5 to 7; Table 1 Evidence column and caption.

**What is wrong:** several unmarked main-text claims are post hoc by the paper's own appendix labels.
- **Section 6, line 228.** "Keeping only samples that Qwen2.5-7B scored 9 or above without a reference (81% of them), the swap gain is +5.32..." The registered filter was ≥7 (Table 3, "Blind-accepted filter", registered on the Ties pool, and Table 4 caption). The t=9 value comes from Table 49, which carries a dagger. Table 1 then headlines "+5.3, 81% kept."
- **Section 5, lines 200–201.** The six-grid-judge step and "excludes zero ... only for three of the six grid judges." These are from the post hoc paired re-analysis (Table 11 caption); the dagger appears only in the Fig. 2 caption.
- **Section 5, line 210.** Mistral-7B's 0.08 and GPT-4.1's 0.04 are Table 13 values, which are post hoc except Qwen2.5-7B's replication cell. No dagger.
- **Section 6, line 236.** "rise for all five judges ... by 12.5 to 63.8 points" includes the Qwen2.5-7B and phi-4 factual cells, which carry a dagger in Table 43. No dagger in the text.
- **Section 7, line 260.** "Sonnet 5's best-of-16 accuracy does not change in any pool" is not among the R8 registered predictions (`r8_sonnet_results.json` lists A1–A6 only). No dagger.
- **Verdict rule.** Appendix B: "We adopted this rule on 13 September 2026, after most outcomes were known." Every "Holds" in Table 1 is issued under that rule, and Table 1's caption does not say so.

**Fix:**
- Report the registered threshold as primary: "Keeping only samples each judge scored 7 or above blind (96% of Qwen2.5-7B's), the swap gain is +5.27, +4.08, and +2.79; at a stricter threshold of 9 (81% kept), Qwen2.5-7B still gains +5.32.†" Change Table 1 to "+5.3 (≥7 blind, 96% kept)".
- Add daggers at lines 201, 210, 236, and 260, or cut those sentences.
- Add to Table 1's caption: "Verdicts apply one rule (Appendix B) adopted after most outcomes were known."
- Add "post hoc" to the P2 inflation row's Evidence cell (see Must-fix 2b).

### 6. Figure 1 shows only P1, and two main-text figures are below print legibility

**Where:** Figure 1 (page 1) and Figure 2 (page 5).

**What is wrong:**
- **Scope of Figure 1.** The title's conditional is "When Several Answers Are Correct," but Figure 1 never shows the one-answer case. A reader of page 1 learns that the score follows the reference (P1) but not that this is harmless with one correct answer and harmful with several (P2). The benchmark figure the paper emulates (Schaeffer et al., Fig. 1) shows the alternative explanation itself, not only one symptom of it.
- **Fig. 1c legibility.** `fig1_rotation.pdf` is 182 pt wide, set with 8.2 to 8.5 pt fonts, and placed at 4.9 cm (139 pt) inside a TikZ picture resized to text width. That is a scale of about 0.77, so the tick labels, y-label, and legend print at about 6.3 pt.
- **Fig. 1c color grammar.** The bars are black, grey, and hatched, while panel (b) established orange for no reference and blue for reference.
- **Figure 2 legibility.** `fig2_boundary.pdf` is 267 pt wide with 7 pt tick and legend fonts, placed at 0.5 × text width (198 pt). That is a scale of 0.74, giving about 5.2 pt judge names and legend. At print size the judge names are unreadable.

**Fix (re-plot and relabel only):**
- Figure 1: add a compact panel "d One vs. several correct answers" drawn from existing Fig. 2 data. Four rows (k-pool Qwen2.5-7B and phi-4, MACE Qwen2.5-7B and phi-4), hollow = k=1, filled = k>1. Alternatively, add one line to panel (b): "question with one correct answer → reference = answer key → same verdict."
- Recolor Fig. 1c: blue for "reference moved onto its answer," blue-hatched for "moved off," grey for "matches neither."
- Regenerate `fig1_rotation.pdf` at its print width (1.93 in) with fonts of 7 pt or larger, or give panel (c) more width by narrowing panel (a)'s text box.
- Figure 2: make it full width (the caption can go below), or regenerate it at `figsize=(2.75*0.72, …)` with fonts of 7 pt or larger at final size. Increase marker size.

### 7. Sections 5 to 7 read as a ledger, not a paper

**Where:** page 2, the "What we find" paragraph and the prediction counts at line 101; Section 5, "Tasks with one versus several correct answers"; Section 7, "Blind-then-reveal".

**What is wrong:**
- **Too much in "What we find."** The paragraph brings in answer formats, labelings, best-of-64, judge–pool pairs, and AUROC before any of them is defined. A reader needs three passes.
- **Counts in the introduction.** "Appendix B scores all 156 registered predictions: 92 confirmed, 25 not confirmed or falsified, 16 with verdicts that differ across judges, and 23 not evaluable, not scored, or excluded" is bookkeeping, not introduction.
- **Section 7's "Blind-then-reveal" paragraph.** In 11 lines it gives eleven numbers across four judges, three labelings, two scorers, and three variants, with "falsifying the equivalence we registered, and another judge's score keeps part of the protection (+0.38 for Qwen2.5-7B; falsified for gemma-2-9b; Table 39)."
- **Appendix tables by number.** The main text cites Tables 8, 10, 12, 13, 15, 16, 24, 25, 28, 30, 38, 39, 43, 44, and 49, which forces constant page-flipping.

**Fix:**
- **"What we find," at most 5 sentences.** Suggested:
  > P1 holds for every judge that scores without reasoning: identical text gains 3 to 5 points when the reference moves onto its answer and loses as much when it moves off. P2 holds: the reference helps on unique-answer questions (+29 points of best-of-64 accuracy on MATH-500) but, with several correct answers, makes correct answers that differ from it harder to separate from wrong ones for every judge that passed our score-resolution screen. P3 partly holds: the effect survives prior acceptance and frontier scale, and disappears only when reasoning judges can check arithmetic. The harm falls mainly on grading; on natural multi-answer questions the reference did not lower selection accuracy. Table 1 lists every test and verdict.
- Move the 156-prediction count to Section 9's "Registration" bullet or the Table 1 caption.
- **Blind-then-reveal paragraph, at most 3 sentences.** Suggested:
  > Scoring blind first and then showing the reference with that score removed the added inflation for Qwen2.5-7B and phi-4 and shrank it for Qwen2.5-14B, but not for gemma-2-9b; the displayed blind score does the work (Appendix M). It did not recover accuracy: on the k-pool it trailed blind judging under the registered checker, and on MACE it was less accurate than the reference alone, falsifying our registered prediction.
- Move variant details (neutral wording, other judge's score) to Appendix M.
- Cite appendices by letter in the main text ("Appendix D"), not table numbers.
- **Space:** move the Section 7 "Code" paragraph to Appendix K. It is a falsified prediction confounded with effective k ("this decline cannot be separated from a smaller effective k"). Keep a one-line pointer.

### 8. Section 2's fitted model rests on labels the paper itself shows to be wrong

**Where:** Section 2, line 139 ("λ = 4.3 and 3.5 points and β = 0.51 and 0.69 ... ranks nine held-out pool compositions at Spearman 0.80 and 0.85"); Appendix I (Table 27, lures).

**What is wrong:**
- The composition and lure analyses split candidates into "oracle-valid" and "oracle-invalid" using the registered boxed checker (`exploit_dose.py` uses `it["oracle"]`).
- Section 3 and Appendix D show that this checker marks most prose answers wrong. Table 17 shows that 73% to 77% of "wrong candidates whose text contains the reference's answer" have no `\boxed{}` answer, so many "lures" are plausibly correct answers that match the reference.
- The "d=0" sub-pools may therefore contain matching correct answers labeled invalid. The result that the judge "picks a valid sample 14% of the time" at d=0, and the lure bonus γ, would then be partly label artifacts.
- Section 2 nonetheless presents the fitted λ and β and the held-out Spearman values as support for Equation (1).

**Fix (a new analysis of existing data, or a cut):**
- Recompute Table 27 and the selection-model fit under the any-format labels already used in Table 16.
- If that is not done, cut the λ, β, and Spearman sentence from Section 2 and replace it with: "We use Equation (1) to organize the predictions, not as a fitted model of how judges work (a fit on registered labels is in Appendix I, with caveats)."
- Add the label caveat to Appendix I either way.

### 9. "Inflation" is not interpretable from the main text, and its k-step is partly implied by P1

**Where:** Section 3, "Measurements" (line 162); the abstract ("best-of-64 inflation"); Table 1; Section 7.

**What is wrong:**
- **The definition.** "how much higher a second rubric scores the judge's best-of-64 pick than a typical sample of the same correctness, in standard deviations of that rubric's scores and net of a permutation null" cannot be understood without Appendix A.
- **Same reference for both rubrics.** Both rubrics see the same reference, so inflation measures a preference the two rubrics share, which here is agreement with the reference. It is not a measured harm.
- **The k-step is largely built in.** At k=1 every valid sample matches the reference, so a match bonus cannot create variance within the valid class. The step from k=1 to k>1 therefore largely follows from P1 plus the definition, and is not an independent test.
- **The disconnect with accuracy goes unexplained.** Inflation stays near +1.1 to +1.2 SD under relabeling while the accuracy loss mostly disappears. A reader needs to be told why.

**Fix:**
- Rewrite the definition as: "*Inflation* (the preregistered selection endpoint) asks whether the judge's top pick is over-rated for reasons other than correctness. A second rubric, shown the same reference, scores the pick against other answers of the same correctness; +1 means the pick scores one standard deviation higher than its correctness warrants. Because both rubrics see the reference, inflation measures shared preference for agreement, not lost accuracy, which we report separately."
- In Section 5, add: "Because every correct answer matches the reference when k=1, the step is the selection-level signature of P1 rather than an independent test; grading AUROC is the independent test."
- Remove "best-of-64 inflation" from the abstract (Must-fix 3's replacement sentence already avoids it).

---

## Should-fix (ranked)

### 1. Failed predictions near each claim are missing from Table 1

**Where:** Table 1.

**What is wrong:** each row reports what held. Nearby registered failures are elsewhere:
- **P1:** distance terciles falsified; solution-route no-change falsified for Qwen2.5-7B.
- **P2:** "margins rise with k (falsified)"; "same pattern on a Llama-generated pool (falsified: no k=1 benefit)"; composition dose falsified; MACE blind margin null falsified for phi-4 and Sonnet 5.
- **P3:** "instruction lowers the margin at every k" falsified for Qwen2.5-1.5B, 3B, and 7B.
- **Costs:** MACE loss not confirmed; blind-then-reveal on MACE falsified; code exemplar falsified; validity gate falsified; neutral wording falsified.

**Fix:** add a narrow column, "Registered predictions that failed," with 1 to 3 short items per row. This is exactly the test the Mirage paper passes: the failures sit next to the claims.

### 2. Mechanism sentences say more than the data show

**(a) Section 4, line 176: "judges compare against a stated answer, not against characters."**
- "30+1" is a stated answer equal to 31, yet it cuts the margin by 77% to 94%.
- The data show that judges match a *literal* answer (digits or words), not a value that must be computed.
- Fix: "judges match the reference's answer when it is written as a literal, in digits or words, and largely stop when it must be computed or is masked."

**(b) Section 6, line 235: "These judges check the arithmetic and resist the pull."**
- Appendix N reports that the thinking judge gives 10 to 96.2% of valid samples blind and 99.8% with either reference. There is a ceiling effect.
- Qwen3-8B's non-thinking loss is already small (−0.69), so "removes" is measured against a small baseline.
- Fix: "With thinking on, these judges score nearly every correct arithmetic answer 10 with or without the reference (Appendix N), consistent with verification; the non-thinking loss for Qwen3-8B was already small (−0.69)."

**(c) Frontier scale.**
- The effect shrinks with scale: up to 9.8 points for Qwen2.5-1.5B and about 3 to 4 at 14B on Ties, 3.0 for Sonnet 5, and an anchoring margin of 1.19 for GPT-4.1.
- The Section 6 verdict "P3 holds for ... frontier scale" hides the shrinkage.
- Fix: "a frontier judge still anchors, at about half the size of a 7B judge."

### 3. The Sonnet 5 item-level number is selected

**Where:** Section 6, line 229; Table 1, P3 row ("Sonnet 5 scores 35% of accepted factual answers ≤ 3").

**What is wrong:** `r9_sonnet_item_level.json` gives 34.9% on MACE, 21.8% on the k-pool, and 9.2% on the replication pool (mean change −0.92). Reporting only the MACE value overstates "does not protect it" for arithmetic.

**Fix:** "Sonnet 5 scores 9% (arithmetic), 22% (k-pool), and 35% (factual) of the correct answers it had accepted blind at 3 or below once the reference is shown.†"

### 4. The marker and color grammar is inconsistent across main-text figures

**Where:** Figs. 1 to 4.

**What is wrong:**
- Hollow markers mean k=1 in Fig. 2, the registered checker in Fig. 3, and thinking on in Fig. 4.
- Blue and orange encode reference and blind in Figs. 1b, 2, 5, 6, and 8, but Figs. 1c, 3, and 4 are black.
- Shapes encode judges in Fig. 4a (circle for Qwen2.5-7B, square for phi-4, triangle for Sonnet) but labelings in Fig. 3.

**Fix:** set one grammar for the paper and state it once in the Fig. 1 caption:
- blue = referenced, orange = blind;
- filled = the main condition, hollow = the contrast condition (k=1, or thinking on);
- labelings shown by line style or a small offset, not by hollow markers.

In Fig. 3, use filled circles for "any format," small grey ticks for "registered," and small grey crosses for "model-read."

### 5. Figure 3 spans two sections, and Figure 4a mixes designs without saying so

**Where:** Fig. 3 (page 6), Fig. 4 (page 7).

**What is wrong:**
- Fig. 3a supports Section 5 and Fig. 3b supports Section 7. The reader meets selection accuracy two sections before it is discussed.
- The Fig. 3 caption title makes two claims.
- The Fig. 4a caption says "replication pool," but its rows come from different subsamples: full pool; a rotation subsample of 879 samples; a CLI run on 60 tasks with one sample each.

**Fix:**
- Split Figure 3. Keep 3a in Section 5 with the title "Grading of correct answers that differ from the reference gets worse for every screened judge." Move 3b into Section 7 next to, or merged with, the blind-then-reveal accuracy.
- Fig. 4a caption: "rows use the full replication pool (open judges, Sonnet 5 API), a 120-task rotation subsample (Qwen3, MT-Bench), or 60 tasks with one sample each (Sonnet 5 CLI); compare within a group."

### 6. The same quantity is given different numbers in different places

**What is wrong, and the fix for each (use one value per quantity, from one table):**
- **Replication primary endpoint.** Main text and Table 18 give +1.19 [+1.03, +1.35]; Table 16 gives +1.19 [+1.02, +1.36]; the JSON gives [1.017, 1.358]. Use one interval and footnote the other.
- **phi-4 k-pool inflation at k>1.** Section 7 says "+1.06 registered" in the Selection paragraph and "+1.07 with the reference alone" in the Blind-then-reveal paragraph. Likewise phi-4 blind-then-reveal is +0.16 in the text and +0.15 in Table 16.
- **GPT-4.1 ties.** "15.5 of 64 candidates tie at its maximum" (Section 6) against "15.03 candidates per pool" (Appendix H).
- **Ties-pool swap.** "up to 9.5 points" (Section 4); Table 5 has −9.65 and −9.80.
- **Largest loss among the other three judges.** "at most 15 points" (Section 7); phi-4 is −15.2.
- **Qwen2.5-7B swap scorer.** Table 4 uses the original scorer (+4.97), while the text and Fig. 1c use the exact scorer (+5.25). Put the exact-scorer values in Table 4 or label the Fig. 1c scorer.

### 7. Sonnet 5 AUROCs are compared with open-judge AUROCs despite the paper's own caveat

**Where:** page 2 ("most for Sonnet 5"); Section 5 ("largest for a frontier judge"); Section 9 ("not directly comparable").

**Fix:** see Must-fix 2d. Never rank Sonnet against open judges on AUROC.

### 8. The abstract is dense with undefined terms

**Where:** the abstract.

**What is wrong:** "best-of-64 inflation," "judge–pool pairs," and "AUROC" (target undefined) all appear, and there is no statement of practical consequence.

**Fix:**
> LLM judges are routinely given a reference answer, on the premise that it acts as an answer key. We propose that when a question has several correct answers, the reference acts instead as one sample of them, and judges reward agreement with it. We test three predictions on tasks whose correct answers are enumerated by a program or an audited list, with twelve judges. First, swapping the reference between two correct answers moves the score of byte-identical text by 2.7 to 5.4 points out of 10 for Qwen2.5-7B, phi-4, and Claude Sonnet 5. Second, the harm needs a second correct answer: with one, the reference helps (+29 points of best-of-64 accuracy on MATH-500); with several, correct answers that differ from the reference become harder to separate from wrong ones for every judge that passed our score-resolution screen, and Sonnet 5's AUROC for this separation on factual questions falls from 0.94 to 0.78. Third, the effect is not simply a failure to verify: it persists for answers the judge accepted blind and for frontier judges, but judges that reason before scoring stop anchoring on arithmetic. The cost falls on grading more than on selection: on natural multi-answer questions the reference did not lower best-of-64 accuracy, and scoring blind before revealing the reference was less accurate than the reference alone.

### 9. The practical scope is under-argued

**Where:** page 2, paragraph 2.

**What is wrong:** the paper's own audit finds 0% to 2.5% multi-answer items on MATH-500, GSM8K, and DeepScaleR. The only broad case given is "Tasks that ask for an example or a construction have many by design," in one sentence. A reader will ask where this matters.

**Fix (rewrite, no new data):** add one sentence naming the concrete regimes the paper already covers:
> It matters wherever answers are not unique: open-domain QA (18.5% of NQ-open questions after removing time-dependent answers), benchmarks built around multiple valid answers (RewardBench-2 Ties, MACE), and construction or search tasks used for RL rollouts, where a single stored solution is the norm (Appendix P).

### 10. The Section 7 code sentence is ambiguous and overclaims

**Where:** Section 7, line 264.

**What is wrong:** "the program lowered inflation relative to blind, as the test suite did (−0.34 and −0.57 SD)." The two numbers are the program condition for 7B and 14B, not program versus test suite. The 7B interval is [−0.737, +0.041], which includes zero.

**Fix:** "the canonical program did not add inflation (−0.34 [−0.74, +0.04] and −0.57 SD for the 7B and 14B judges), and neither did the test suite." Better still, move the paragraph to the appendix (Must-fix 7).

### 11. P1's "3 of 3 judges" undersells the breadth and misstates the scope

**Where:** Table 1 and the Section 4 verdict.

**What is wrong:** the swap test was also run on four Qwen2.5 sizes (Ties pool), MT-Bench-template Qwen2.5-7B, and MathConstraint. It failed for thinking judges.

**Fix:** "Holds for every judge configuration scoring without reasoning (Qwen2.5 1.5B–14B, phi-4, Sonnet 5, the MT-Bench template, Qwen3 with thinking off); not for reasoning judges on arithmetic (Section 6)."

---

## Nits

- Page 1, Fig. 1 caption: "the full reply is in the supplement." Reviewers will not open it. Put the unabridged candidate in Appendix A (it is short).
- Page 2: "against 18.5% of NQ-open questions." Table 20 reports 30.0%. Say "18.5% after excluding questions whose answer changed over time."
- Page 4, Section 3: "MATH-500 and MBPP supply unique answers and programs." MBPP does not have unique answers. Write "MATH-500 supplies unique answers and MBPP supplies programs."
- Page 5, line 247: "Qwen2.5-7B's accuracy fell by 21.4 points [−43, 0]." The interval reaches zero on 14 tasks. Say "fell by 21.4 points (interval reaching zero, 14 tasks)."
- Page 4: "writing it as '30+1' cuts the margin by 94% and 77%." The previous clause lists phi-4 first and Qwen2.5-7B second, but these two numbers are in the opposite order. Name the judges.
- Page 3, Table 1: the Evidence code "commit (re)" is jargon. Use "pre-specified re-analysis."
- Section 3, "Candidates and judges": the reference heading is "Reference answer (trusted)." The word "trusted" plausibly strengthens anchoring. State this in Limitations as a design choice shared by all conditions.
- Section 6: "GPT-4.1's scores tie too heavily to measure selection," yet GPT-4.1 appears in Fig. 3b with selection accuracy. Either drop it from 3b or explain what the plotted value means under heavy ties.
- Appendix: page 12 is two-thirds blank, and Table 48 sits alone on a mostly blank page 37. Add `\clearpage` control or float placement.
- Fig. 5 (appendix): legend fontsize 6.3 in the script, below 7 pt. Table 36 and Table 38 are set in about 6 pt.
- Table 34's title "A descriptive map of the pools we measured, not a validated decision rule" is defensive. Title it by content ("Where the reference helped and where it hurt").
- "twelve judges from seven developers": Ministral-8B also ran (resolution screen, Appendix M). Say whether it counts.
- Section 9, "Judges": "we tested no reasoning judge from a third frontier provider." Also note that the Sonnet 5 reasoning runs used the CLI with a replaced system prompt, not the API.
- Conclusion: "Scoring blind first reduced the added inflation for every open judge we tested." For Mistral-7B the reduction (−0.07) concerns a judge the paper excludes elsewhere. Say "every screened open judge."

---

## Questions for authors

1. **Figure 1 example.** How was the candidate (digit-sum task, sample 16) chosen? Its referenced gap (9.3 − 2.9 = 6.4) is above the pool mean swap loss (5.4). Please state the selection rule, or say that it was selected to be illustrative.
2. **Composition labels.** Were the d-sub-pools in Table 27 and the lure design built on registered (boxed) labels? If so, what share of "invalid samples that contain the reference's answer text" are correct under any-format labels, and does the d=0 valid-pick rate of 14% survive relabeling?
3. **Sonnet 5 subsamples.** Can you confirm that every 16-candidate subsample contained a correct candidate matching the reference? If so, do you agree that the best-of-16 accuracy change is uninformative about selection harm?
4. **Judge–pool pair counts.** Why were Qwen2.5-14B and gemma-2-9b, which ran on the OSF k-pool and support the step, excluded from the "ten judge–pool pairs"? What rule defines the ten?
5. **Inflation at k=1.** Absent wrong answers that echo the reference, is inflation at k=1 mechanically near zero under the one-sample reading? If so, which part of P2 is independent of P1?
6. **Verdict rule.** How many Table 1 verdicts would change if verdicts were taken from the registration documents rather than from the uniform rule adopted on 13 September 2026? The ledger names seven predictions moved toward the thesis and ten moved against it; do any of the seven feed Table 1?
7. **Grading under boxed-only labels.** The grading AUROC fall shrinks from 0.16–0.33 to 0.07–0.14 with boxed replies only. Do you read boxed-only as the cleanest labeling or as a selected subpopulation? If the former, it should be the headline range.
8. **Novelty claim.** "No study of LLM judges that we know of varies which correct answer is the reference." Did your search include MACE's and RewardBench-2 Ties' own judge evaluations, which have multiple references by construction?
9. **Reference heading.** Were any pre-existing score files collected with a heading other than "Reference answer (trusted)," for example in the MT-Bench template run? If so, does the swap effect differ?
