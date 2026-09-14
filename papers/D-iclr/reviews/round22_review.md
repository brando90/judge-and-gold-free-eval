# Round 22 Area Chair review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

**Materials.**
- **PDF.** `round22_main.pdf`, 49 pages: main text pp. 1-9 (ends l. 485), statements p. 10, references pp. 10-12, appendix pp. 13-49. I read every page as a rendered image, with 220-dpi renders of pp. 5-7 and a 400-dpi crop of Figure 3b-c.
- **Sources checked.**
  - `main.tex`, `appendix.tex`.
  - `tables/r22_{redraw,redraw_models,haiku_llama,bins_open,bins_api}.tex`, `tables/r21_graders.tex`, `tables/protocol_exact.tex`.
  - `scripts/make_figures.py` (the Figure 3 block, ll. 360-457).
  - `papers/analysis/`: `r22a_label_audit.json`, `r22b_redraw_{sonnet,opus,haiku}.json`, `r22c_acceptance_bins.json`, `r22d_ranking_intervals.json`, `r20a_*_retest.json`, `r20d_matched_acceptance.json`, `r21a_mace_acceptance.json`.
  - `registration_round19.md` to `registration_round22.md`, and the ledger (Appendix B, Table 4).
- **Line numbers.** PDF margin numbers.
- **Independence.** The round-21 review was read only for the audit in Section 4.
- **Writes.** Nothing in the project was modified other than this file.

---

## 1. Summary and ease of extraction

**Question.** When a question has several correct answers, does a reference-guided LLM judge treat the reference as an answer key? Two alternatives are set against that reading:
- **Verification failure:** the reference is the judge's only evidence.
- **Agreement:** the judge rewards matching the one answer it is shown.

**Claims as extracted.**
1. **P1, the swap.** Moving the reference between two correct answers moves byte-identical text by 2.7-5.4 points out of 10 (Qwen2.5-7B, phi-4, Sonnet 5; 120 tasks). Text matching neither reference does not move.
2. **P2 and P2′, grading.**
   - With several correct answers, grading AUROC for correct answers that differ from the reference falls 0.06-0.16 for four judges on MACE, and 0.17-0.27 for four open judges on arithmetic (0.07-0.14 on boxed replies only).
   - With one correct answer, the reference raises best-of-64 accuracy by 29-31 pp (MATH-500).
3. **P3, not only verification failure.**
   - Among correct factual answers the judge accepts blind, 19%-83% of those that differ from the reference drop to 3 or below once it is shown. None of those that match do.
   - A same-interface second blind call gives 2 of 282.
   - *New:* binned by blind score, rejection falls with confidence but stays far above zero (Figure 3b).
4. **Moderators.** Thinking nearly removes the arithmetic swap but only halves the factual false-rejection rise. A full-credit sentence reduces the harm without restoring grading.
5. **Consequence.**
   - On 149 multi-answer MACE questions, three Claude graders shown the reference put four models 16-22 points (pooled) below answer-list accuracy. Blind, Sonnet 5 and Opus 5 stay within 3 points.
   - *New (R22-B, registered):* a second reference draw leaves the pooled shortfall within 3 points and moves credit for answers whose match status changes by 23-38 pp.
6. **Safeguard.** The max rule keeps grading within 0.03 AUROC of blind, and pooled benchmark accuracy within 2 points of the lists. It costs up to 6.7 pp with a unique answer.
7. **Labels (new, R22-A, registered).** Opus 5's reading agrees with the any-format labels on 91%, but confirms only 86% of the rule's credits (prediction of 90% falsified).
8. **Registration.** 197 predictions: 129 confirmed, 11 not confirmed, 17 falsified, 17 split, 23 other.

**2-minute takeaway** (title, abstract, Figure 1, Table 1). Correct and quick:
- the reference moves unchanged correct text;
- the effect survives the judge's own acceptance;
- it lowers benchmark accuracy for frontier graders.

What still slows a skimmer:
- **Abstract length.** 252 words, with three numbered findings in one sentence.
- **Table 1's Consequence row.** "7-40 points ... under either of two reference draws" is a draw-1 range attributed to both draws (M2).

**10-minute takeaway** (adds Figures 2-4 and Table 2). The reader also gets:
- the one-answer positive control;
- the acceptance lollipop;
- the new binned-rejection panel;
- the thinking moderators;
- the benchmark slope chart;
- the safeguards table.

**Where a careful reader now trips.** All three spots are in material added this round:
1. **Figure 3b caption.** It says matching answers "stay at or below 10% in every bin". The appendix tables it cites show 45% and 64% (M1).
2. **The benchmark ranking sentence.** It reports that Sonnet 5 and Haiku 4.5 "erase" Haiku 4.5's lead over Llama-3.1-8B using only the first draw. The registered second draw restores part of that lead, and the main text does not say so (M2).
3. **Figure 3b itself.** Its markers use open symbols for three of four judges, which Figure 3a's legend defines as "matches the reference". Its legend is set at about 6 pt (M3).

**Overall.** The paper keeps the strengths that earned round 21 its score:
- one question and a model saying what each reading predicts;
- a separating test with a noise control;
- a replicated consequence;
- unusually honest registration.

This round did the two cheapest high-value things the previous review asked for: a second reference draw and binned acceptance curves. It also added a registered label audit. The problem is that the new material was written up faster than it was checked. The two headline additions each carry a statement the underlying JSON contradicts or qualifies. These are precision errors, not design flaws, but they are exactly what a best-paper committee checks.

---

## 2. Score and confidence

**Score: 8 / 10** (accept, good paper). **Confidence: 4 / 5.**

**Single biggest reason.** The central claim is tested the way it should be, and the round-21 must-fix list was addressed in substance, which I verified line by line (Section 4):
- a byte-identical swap;
- a one-answer positive control;
- P3 with a same-interface retest;
- a benchmark consequence with three graders, now across two registered reference draws.

**Why not 9.**
1. **The new analyses introduce new precision errors.**
   - A false caption claim about matching answers in Figure 3b and Appendix K.
   - A ranking sentence that reports the first draw and omits the registered second.
   - An overgeneralization from two draws to "whichever listed answer is the reference".
2. **Figure 3b is not yet a decisive figure.**
   - It clashes with panel a's marker grammar and uses sub-7-pt legend text.
   - It hides the matching-answer baseline. That baseline shows part of the "falls with confidence" slope is shared by answers the reference cannot penalize.
3. **The consequence is still narrow.** One benchmark, graders from one provider, and factual P3 noise-controlled only for Anthropic judges. It is honestly disclosed, but it caps the paper below 9.

**What is needed.** M1-M6 are rewrites or re-plots of stored data (about a day). The generality gap needs the cheap new runs listed in Section 7.

---

## 3. Ranked issues

### MUST FIX

#### M1. Figure 3b caption and Appendix K misstate the matching-answer baseline, and the main text reads a slope that matching answers share as evidence for verification
**New data: none (re-plot of `r22c_acceptance_bins.json`).**

**Location.**
- Figure 3 caption, p. 6 l. 302-303: "Matching answers stay at or below 10% in every bin (Appendix K)."
- Appendix K, p. 43 l. 2269-2270: "while matching answers are almost never rejected (Tables 51 and 52)."
- Section 6, p. 6 l. 323 to p. 7 l. 350: "Rejection falls as the judge's own confidence rises, as verification failure predicts, but levels off far above zero ... Verification lowers the effect but does not remove it, which is what agreement predicts."

**Problem.**
1. **The caption is false for the plotted judges.** It restricts to "bins with at least 10 answers", yet the bins it covers include:
   - Sonnet 5, blind score ≤ 6: matching answers rejected 45% (n = 20), `r22c_acceptance_bins.json` `mace|Sonnet 5` bin [0, 7] `match.share_le3_with_reference` 0.45;
   - Opus 5, ≤ 6: 64% (n = 14), `mace|Opus 5` [0, 7] 0.6429;
   - Qwen2.5-7B, < 5: 10.4% (n = 394), `mace|Qwen2.5-7B` [0, 5] 0.1041, which is above 10%.

   The appendix's "almost never rejected" is also contradicted by its own Table 52 (45, 64, and 40 and 14 on the Opus k-pool) and Table 51 (Qwen2.5-14B 20%, gemma-2-9b 11%).
2. **The contradiction matters for the argument.** In the lowest bins the reference also rejects answers that *match* it, so low-blind-score correct answers are partly malformed or hedged replies the judge rejects anyway. The P3-relevant contrast is differing minus matching, per bin:

   | Blind bin (MACE) | Sonnet 5 | Opus 5 | Qwen2.5-7B | phi-4 |
   |---|---|---|---|---|
   | lowest | 89 − 45 = **44** | 92 − 64 = **28** | 98 − 10 = 88 | 89 − 7 = 82 |
   | middle | 64 − 0 = 64 | 75 − 0 = 75 | 84 − 1 = 83 | 50 − 0 = 50 |
   | top | 19 − 0 = 19 | 31 − 0 = 31 | 83 − 0 = 83 | 46 − 0 = 46 |

   - **For the two API judges** the gap does not fall monotonically from the lowest bin. It rises and then falls. Most of the visible drop from the lowest bin in Figure 3b is shared with matching answers.
   - **For phi-4** the decline is real. **For Qwen2.5-7B** the gap is flat.
   - The main-text reading "falls ... as verification failure predicts" is therefore right for phi-4 and for the API judges from their middle to top bins, but not as a description of the plotted curves.
3. **"Levels off" is supported by one judge.** Sonnet 5 and Opus 5 have three or four bins, and their lowest value is in the last one. Only phi-4 shows a plateau (34% then 46%).
4. **"Which is what agreement predicts" is imprecise.** Pure agreement (λ constant) predicts no decline. A decline to a non-zero floor is a mixture of the two readings.

**Fix.**
- **Figure 3b.** Add the matching-answer rate as a grey line per judge (or plot differing minus matching). The reader then sees the floor the caption promises.
- **Caption (b), replace the last sentence:**
  > "Grey: answers that match the reference, which are rejected only in the lowest bins (Sonnet 5 45%, Opus 5 64% below a blind 7; Qwen2.5-7B 10% below 5) and in no bin from a blind 9 up."
- **Section 6, l. 323-350, replace from "Rejection falls":**
  > "Binned by blind score (Figure 3b),† the gap between differing and matching answers shrinks as phi-4 grows surer, but among the answers each judge is surest of it stays far above zero, where no matching answer is rejected: Sonnet 5 and Opus 5 still reject 19% and 31%, phi-4 46%, and Qwen2.5-7B at least 83% in every bin. Verification explains part of the effect; the remainder, among answers the judge already accepts, is what agreement predicts."
- **Appendix K, l. 2269-2270:** replace "while matching answers are almost never rejected" with:
  > "while matching answers are rejected only in the lowest bins (Tables 51 and 52: up to 64% below a blind 7 for Opus 5 on MACE) and in no bin from a blind 9 up."

#### M2. The benchmark ranking is reported under the first reference draw only, although the registered second draw partly reverses it; three summary sentences overgeneralize from two draws
**New data: none.**

**Location.**
- Section 7, p. 8 l. 404-410: "Sonnet 5 and Haiku 4.5 shown the reference erase that lead (−0.7 and −7.4 points, intervals including zero), while Opus 5 keeps most of it (Appendix K).† Which listed answer is the reference matters for individual answers but not for the pooled shortfall ..."
- Intro, p. 2 l. 100-101: "The effect lowers benchmark scores whichever listed answer is the reference".
- Table 1 Consequence row, p. 3 l. 135-137: "score four models 7-40 points below the answer lists (within 3 blind), under either of two reference draws".

**Problem.**
1. **The "erased" lead is draw-dependent.**
   - Under the second draw, Haiku 4.5 minus Llama-3.1-8B is +6.7 [−3.4, +16.1] (Sonnet 5 grading) and +3.4 [−6.0, +12.8] (Haiku 4.5 grading), from `r22b_redraw_sonnet.json` and `r22b_redraw_haiku.json` `haiku_minus_llama.ref_draw2`.
   - The rankings flip back: `ranking_ref_draw1` puts Llama-3.1-8B above Haiku 4.5 for both graders, and `ranking_ref_draw2` puts Haiku 4.5 above it.
   - Under Opus 5 grading, the second draw ranks Haiku 4.5 (77.2%) *above Sonnet 5* (76.5%) (`r22b_redraw_opus.json` `ranking_ref_draw2`).
   - `registration_round22.md` l. 84-86 records this, and Appendix K l. 2224-2226 says "partly restored under the second". The main text cites only the first-draw numbers, which is selective reporting of a registered readout.
2. **The omitted result is the paper's best new finding.** The reference draw moves a pairwise model gap by 7.4 (Sonnet 5) and 10.8 (Haiku 4.5) points, and single models by up to 8.1 points (Table 49), while the pooled shortfall barely moves. That is P1 at leaderboard scale.
   - The pooled stability is close to guaranteed by symmetry: both draws are random members of the same list.
   - So "matters for individual answers but not for the pooled shortfall" undersells the draw's effect on comparisons, which is what leaderboards report.
3. **"Whichever listed answer is the reference"** generalizes from two draws to all.
4. **Table 1's "7-40 ... under either of two reference draws" is a draw-1 range.**
   - Under draw 2, Sonnet 5 and Opus 5 put the four models 9.6 points (Opus 5 grading itself, 136 questions; `draw2_minus_list` −0.0956) to 32.9 points (Sonnet 5 grading Haiku 4.5, −0.3289) below the lists.
   - The range is "10-33" under draw 2.

**Fix.**
- **Section 7, l. 404-410:**
  > "The damage is uneven and depends on the draw. The answer lists put Haiku 4.5 25 points ahead of Llama-3.1-8B; Sonnet 5 and Haiku 4.5 shown the first reference put the two level (−0.7 and −7.4 points) and, shown a second reference drawn from the same lists, +6.7 and +3.4 (all four intervals include zero), while Opus 5 keeps most of the lead under both draws (+17.0 and +25.7).† Redrawing the reference moves each grader's pooled shortfall by at most 3 points, but moves single models by up to 8 points and reorders Haiku 4.5 and Sonnet 5 under Opus 5, because correct answers that stop matching lose 25 to 38 pp of credit and those that start matching gain 23 to 35 pp (Appendix K, Tables 48-50). All 18 predictions registered for the extra graders and the second draw were confirmed."
- **Intro, l. 100-101:** "The effect lowers benchmark scores under both of two reference draws, and which answer is drawn can reorder models".
- **Table 1 Consequence row:** "Shown the reference, Sonnet 5 and Opus 5 score four models 7-40 points below the answer lists with one reference draw and 10-33 with a second (within 3 blind)". Verdict: "Holds for three graders and two draws".
- **Conclusion, l. 481-482:** add "and a second reference draw reordered models while leaving the pooled shortfall unchanged".

#### M3. Figure 3b is hard to read at print size and contradicts panel a's marker grammar
**New data: none.**

**Location.** Figure 3b, p. 6 l. 271-288; `scripts/make_figures.py` l. 436-447.

**Problem.**
1. **A marker bug.** The script sets `mfc="white" if "5" in lab`, intended for the two Claude "5" judges. The string "Qwen2.5-7B" also contains "5", so Qwen2.5-7B, Sonnet 5 and Opus 5 are drawn open and only phi-4 filled.
   - In panel a, directly to the left, and in the shared figure legend (l. 289-290), an open circle means "matches the reference, reference shown".
   - Panel b plots only *differing* answers, so three of its four series wear the "matching" symbol.
2. **Legend text is too small.** The figure PDF is 379.9 pt wide and is placed at `\textwidth` (397.5 pt), a scale of 1.046. Panel b's legend is `fontsize=5.9`, about **6.2 pt** at print. The value labels in panels c and d are `fontsize=6.3`, about **6.6 pt**. Both are below the 7-pt floor. Tick labels (7.5 pt) are fine.
3. **Crowding and x-positions.**
   - At blind scores 9-10, ten markers from four series sit within 1 unit of x, and the Sonnet 5 and Opus 5 lines cross phi-4's markers. At print size I could not tell which marker belonged to which judge without the table.
   - API bins are plotted at interval midpoints of half-open bins: the integer bin "9" at x = 9.5, "7-8" at 8, "≤ 6" at 3.5. Open-judge bins are plotted at 2.5, 6, 8, 9.3, 9.7 and 9.9.
   - The two binnings share one axis without saying so.
   - All four series are one hue.
4. **In panel c,** "−0.01" is printed across the zero axis line, and "0.32" nearly touches "0.69" (400-dpi crop).

**Fix.**
- Use filled markers for all differing-answer series and grey for the matching floor (M1).
- Distinguish judges by marker plus two hues (open judges and API judges), or label line ends directly and drop the legend.
- Plot integer bins at their integer value (≤ 6 at 5, 7-8 at 7.5, 9 at 9, 10 at 10).
- Consider an x-axis of "blind-score bin (low to high)" with categorical ticks, which removes the crowding at 9-10.
- Set the legend and value labels to at least 7 pt, and move "−0.01" to the right of its whisker.

#### M4. The label audit is summarized inaccurately, and the main text keeps the labeling the audit found less accurate for its headline arithmetic range
**New data: none.**

**Location.**
- Setup "Reading answers", p. 4 l. 190-192: "confirms only 86% of the rule's credits (we had predicted 90%), mostly rejecting replies that list several numbers (Appendix G)."
- Table 1 P2 row, p. 3 l. 119-122, and Section 5, p. 5 l. 263-264: "0.17 to 0.27 for the four open judges on the constructed pools".
- Appendix G, p. 28 l. 1505-1507; Limitations, p. 9 l. 455-457.

**Problem.**
1. **"Mostly" is wrong.** Of the 13 replies the rule credits and the reader does not, `r22a_label_audit.json` `disagreements` shows:
   - 6 list several numbers;
   - 5 are `NONE`;
   - 2 are single integers the constraint check rejects ("17" on repl/crt-22, "31" on kstrat/digitsum-k1-3).

   Six of 13 is a plurality, and the registration (l. 103-104) reports it as such.
2. **A minor count discrepancy.** Appendix G and the registration say "of the 8 replies the rule rejects and the reader credits, 5 are subset-sum or Goldbach answers". By `problem_id`, 6 of the 8 are subset-sum or Goldbach tasks (repl/subset-34; kstrat/goldbach-k8-3; kstrat/subset-k2-4; kstrat/subset-k2-11 twice; kstrat/subset-k1-2). Either state the rule that excluded one, or write 6.
3. **The audit favors the other labeling.**
   - The Qwen2.5-14B reading agrees with the frontier reader more often (94.7% against 91.1%, `pooled.agree_qwen14b` 0.9472) and on every stratum.
   - Yet Table 1 and Section 5 quote the any-format range 0.17-0.27. Under the model-read labels, Table 27 gives 0.16-0.25 (replication −0.25, −0.21; k-pool −0.21, −0.16, −0.22, −0.22).
   - The difference is small and the direction is unchanged. But a reviewer who reads Appendix G will ask why the headline uses the labeling the registered audit ranked second.

**Fix.**
- **Setup, l. 191-192:**
  > "... confirms only 86% of the rule's credits (we had predicted 90%); most of the rest list several numbers or commit to no answer (Appendix G). A Qwen2.5-14B reading agrees with Opus 5 more often (95%)."
- **Table 1 P2 and Section 5:** "0.17-0.27 for the four open judges on arithmetic (0.16-0.25 with model-read labels; 0.07-0.14 on boxed replies only)".
- **Limitations, l. 455-457:** "... checked by a frontier model's reading, not by humans; that reading rejects 14% of the unboxed replies the rule credits, mostly lists of several numbers or no answer."
- **Appendix G:** reconcile the count of 5 against 6.

#### M5. The second draw, a registered result the abstract-level claims now rely on, has no main-text display and no main-text pointer
**New data: none.**

**Location.** Section 7, p. 8 l. 407-410 ("Which listed answer ... All 18 predictions ... were confirmed."), with no reference to Tables 48-50; Figure 4, p. 7; Table 1 Consequence row.

**Problem.**
- Table 1 and the Section 7 prose now cite the second draw, but Figure 4 shows only the first.
- The only way to reach Tables 48-50 from the main text is the Appendix K pointer on the previous sentence, which was written for the first-draw paired intervals.
- A reader cannot see that the model lines move by up to 8 points between draws, which is the visual form of M2.

**Fix.**
- **Figure 4.** At the "judge, reference" position, add a hollow marker per model for the second draw, offset slightly right. Data: `r22b_redraw_*.json` `generators.*.accuracy_ref_draw2`.
- **Caption:** "hollow markers: a second reference drawn from each answer list (Opus 5: the 136 questions with both draws complete)".
- **Text:** add "(Appendix K, Tables 48-50)" after the redraw sentence, as in the M2 replacement.

#### M6. Figure 3 now carries two claims, a 33-word title, and a caption of about 260 words; the P3 story and the moderator story compete for one float
**New data: none.**

**Location.** Figure 3, p. 6 l. 293-306.

**Problem.**
- **Two unrelated jobs.** Panels a-b are the separating test (P3), and panels c-d are moderators that Table 1 says Equation 1 does not predict.
- **Overlong title and caption.** The title chains three claims with a semicolon. The caption holds per-panel sample definitions, registration status for five subsets, and a pointer to counts.
- **Cognitive load.** This is the heaviest read in the main text. It is the opposite of the "one figure, one message" standard of the reference paper.
- **The shrink hurt legibility.** The shrink that made room for panel b pushed its legend below 7 pt (M3).

**Fix (no new page).**
1. **Title:**
   > "Figure 3: The reference rejects correct answers the judge already accepts, most on factual questions; thinking removes this on arithmetic only."
2. **Move registration status.** Move the per-panel registration sentences to one closing sentence: "Pre-specified: second blind calls, Opus 5's shares in (a), and (c)-(d); the rest is post hoc."
3. **Move sample definitions.** Move the sample definitions for (c) and (d) into Appendix L, keeping only "(c) Sonnet 5 through its CLI; (d) through the API".
4. **Recover the space.** If space allows, give panels c-d their own row with Table 2 ("what changes the effect") and let panel b take their space at a legible size.

### POLISH

1. **Abstract (252 words).** Cut to about 200. The three-part "We find that (1) ... (2) ... (3)" sentence is 80 words. The round-21 200-word draft is still a good template; update its benchmark clause with "under two reference draws".
2. **"Protected selection on the k-pool"** (l. 418). It holds with any-format labels (Table 29: Qwen2.5-7B +0.0, Qwen2.5-14B +3.0, gemma-2-9b +0.0, phi-4 −6.1 [−18.2, +6.1] against the reference). Under the registered labels, gemma-2-9b and phi-4 still lose 12.8 and 15.4 pp, with intervals excluding zero (Table 22). The main-text convention covers this, but add "(any-format labels; Table 29)".
3. **Table 2, "−0.00"** (MACE, Qwen2.5-7B, Reveal − ref.). Print "0.00".
4. **Table 1 P3 row, "a second blind call: 2 of 843".** This is pooled over three pools, while Section 6 quotes 2 of 282 for MACE. Give the comparator and the scope: "a second blind call: 2 of 843 (117 with the reference), pooled over pools".
5. **Table 50, Opus 5 row.**
   - It mixes 141-question first-draw columns (+24.1, +26.2, +17.0; `r22d_ranking_intervals.json` "questions": 141) with a 136-question second-draw column (+25.7).
   - The registration outcome table gives +16.2 for draw 1 on the 136 questions.
   - Say so in the caption, or print both draws on 136.
6. **Section 6, "levels off far above zero"** (l. 349). Write "stays far above zero" (see M1.3).
7. **Arithmetic binned result.** Appendix K's finding that phi-4 falls to 4.8% and Opus 5 to 3%-5% on arithmetic at the top bin deserves one main-text clause. It is the observational counterpart of "thinking removes it on arithmetic", and it strengthens the mixture story.
8. **Rounding, unchanged since round 21.**
   - Table 45 prints Opus 5's MACE AUROC as −0.165 (JSON −0.1645; the text says 0.16).
   - Table 45 prints the Opus 5 replication false-rejection rise as +3.6 (registration +3.7).
   - Haiku's 25.2%/25.3% is now reconciled in `registration_round21.md` l. 74.
9. **Figure 2 caption registration sentence.** "Qwen2.5-7B's values here use the exact scorer, a post hoc rescoring" sits oddly beside Appendix E l. 1095, "A pre-specified experiment rescored Qwen2.5-7B on ... MACE ... with the exact scorer". Say "the rescoring was pre-specified; its MACE readouts were not registered" if that is the case.
10. **Figure 2 overlaps.** Largely fixed: the "n/a" labels are left of zero. The grey boxed-only ticks still touch the GPT-4.1 triangles (rows 226 and 231) at 220 dpi; offset them by a quarter row.
11. **Limitations.** Add:
    - Opus 5's question selection (141 and 136 of 149, dropping calls that ran out of tokens while it deliberated over differing answers);
    - that the two reference draws come from the same answer lists, which miss 2.3%-8.1% of correct answers.
12. **Conclusion recommendation** (l. 483-485). Two additions:
    - Given M2, add: "or average referenced scores over several reference draws".
    - The max-rule clause could add "and helped a weaker grader that under-counts blind".
13. **Appendix legibility.** Still about 5 pt at print: Table 13 (p. 23), Table 15 (p. 25), Table 16 bottom block (p. 26), Tables 18 and 20 (p. 27), Table 24 (p. 29), Table 57 (p. 46), Table 62 (p. 49). Table 16 bottom is the source of Table 2 and must be readable. Use `\footnotesize` with two-line headers instead of `adjustbox` shrinking.
14. **Whitespace.** Much of pp. 25, 30 and 41 is blank, as is the top of p. 31, and p. 49 is mostly empty. `\FloatBarrier` per appendix section plus `[!ht]` placement would recover two to three pages.
15. **Table 2 caption** (about 170 words). Move the per-pool task counts to Appendix F and keep "Bold" and the registration sentence.
16. **Figure 4 hue.** Opus 5 (light grey, open diamond) and Sonnet 5 (mid grey, filled triangle) are now separable by marker, but the lines remain similar greys in print. A single accent hue for Haiku 4.5 (the model whose ranking moves) would carry the story.
17. **Appendix K binned paragraph** (l. 2273-2274). "gemma-2-9b barely falls" is fair (89 → 56). Also say Qwen2.5-14B is non-monotone (15% → 39% → 23%).

---

## 4. Audit of round-21 items

### MUST FIX (M1-M7)

| Item | Status | Evidence in this version |
|---|---|---|
| **M1** "Every grader lowers every model"; Figure 4 title; "7 to 40" attributed to three judges | **Fixed** | Section 7 l. 376-379 uses the suggested text ("all three graders put every model below its answer-list accuracy ... Haiku 4.5, a weaker grader, under-counts by 9 points even blind"). Figure 4 title l. 341-342 is verbatim. Abstract l. 025-027 now names Sonnet 5 and Opus 5 only. Table 1 row names Sonnet 5 and Opus 5. The conclusion's "frontier graders" is acceptable. New overgeneralization about draws: M2. |
| **M2** Max-rule "within 2 points"; registered threshold misstated; Haiku max rule beats blind | **Fixed** | l. 420-424: "pooled ... within 2 points ... (5 points for one model under Haiku 4.5) ... registered that it would stay within 5 points; for Haiku 4.5 ... closer to the lists than blind grading". Appendix K l. 2157 says "within 2 points pooled, although Haiku 4.5's own answers fall 5.4 points short". |
| **M3** Registration labels across captions; 25.2/25.3; "weaker verifier"; ranking readout mark | **Fixed** | Figure 2 and Table 2 captions agree that MACE accuracy was pre-specified for both open judges on the original scorer; see Polish 9 for residual wording. `registration_round21.md` l. 74 now prints 25.2% with the JSON value. "A weaker grader" is used. The ranking sentence carries † for the post hoc paired intervals. |
| **M4** Table 2 Reveal column bold rule; "What helps" sentence | **Fixed** | The column is now "Reveal − ref." with its own bold rule ("differs from zero"). Values are consistent with Table 16 to rounding (+0.11, +0.12, −0.06 [−0.05 by subtraction], +0.04 [+0.05], +0.01, −0.04). l. 418-419 uses the suggested text; "three of four ... and for both on MACE" matches Table 16 (−0.11, −0.01 [−0.02, +0.00], −0.23, −0.20; −0.08, −0.05). |
| **M5** Binned open-judge P3 | **Done, with new errors** | `r22c_acceptance_bins.json` reproduces my round-21 re-analysis exactly (Qwen2.5-7B 98.1/92.4/83.7/83.7/89.7/83.3; phi-4 88.6/69.2/50.1/45.8/33.9/45.5). Figure 3b, Section 6 l. 348-350, Tables 51-52 and the Verdict wording ("two with a registered same-interface noise control, two at a post hoc threshold") are added. New problems: false matching-answer caption, shared-slope reading, and marker and font issues (M1, M3). |
| **M6** P2 verdict classifies identical magnitudes differently | **Fixed** | l. 310-313 is verbatim: "0.06 to 0.08 on the k-pool for Sonnet 5 and Opus 5, and at most 0.04 on the replication pool (0.02, interval including zero, for Opus 5) and for GPT-4.1". It matches Table 45 (−0.080, −0.057, −0.037, −0.015) and GPT-4.1 (−0.04, −0.01). |
| **M7** Inversion without uncertainty; one reference draw; Opus selection direction | **Done, with a new selective-reporting issue** | Paired intervals are in the text and in Table 50 (match `r22d`). Figure 4 has 95% intervals at "judge, reference". The caption adds "dropping those questions may understate its shortfall". The second draw was run as registered R22-B (9/9 confirmed; USD within caps). But the main text reports the ranking under draw 1 only (M2), and Figure 4 does not show draw 2 (M5). |

### POLISH items I consider important

| Item | Status | Evidence |
|---|---|---|
| P1 Abstract 200 words; "ten judges"; "two strongest" | **Partly** | "ten judges in the main text" and named graders are fixed. Still 252 words. |
| P2 "Sonnet 5 shows the same pattern" | Fixed | Sentence now reads "(arithmetic only; Appendices I and J)" without the Sonnet claim. |
| P3 "Earlier margin-only tests agree" | Fixed | l. 357-358: "For small Qwen2.5 judges an earlier test found no reduction". |
| P4 MACE-only noise numbers | Fixed | l. 322-323: "2 of the 282 ... against 78" (Table 43 MACE rows: 0+2 of 81+201; 15+63). |
| P5 Table 1 "3-83%" | Fixed | "4-83%". |
| P6 Figure 3 caption "at or above", sample sets | Fixed | l. 296-298. |
| P7 Dangling Table 12 cross-reference | Fixed | Appendix K l. 2055-2056 has no table pointer. |
| P8 Rounding | **Partly** | 0.15 is now "(paired)"; 25.2 reconciled; −0.165 and +3.6 unchanged (Polish 8). |
| P9 "six judges with a usable acceptance test" | Fixed | l. 097 and l. 366. |
| P10 Figure 2 overlaps | **Mostly fixed** | Labels moved left of zero; ticks still touch triangles (Polish 10). |
| P11 Figure 3 label touching axis | **Not fixed** | "−0.01" still sits on the axis, now in panel c (M3.4). |
| P12 Figure 4 design (hues, max-rule connector, intervals) | **Mostly fixed** | Dotted connector to max rule, intervals and distinct markers added; greys still similar (Polish 16). |
| P13 Drop "margin" from Section 3 | Fixed | Setup defines swap change, false-rejection rate, AUROC and best-of-64 only. |
| P14 Selection paragraph number or pointer | **Partly** | Pointer (Appendix E) added; no number. |
| P15 Limitations additions | **Partly** | Open-judge factual P3 without a noise control is added (l. 465-466). The one-draw item is moot after R22-B. Opus 5 question selection is not added (Polish 11). |
| P16 Human validation of labels | **Substituted** | A registered frontier-model audit (R22-A), not humans. Honest and useful; its summary needs M4. |
| P17 Appendix legibility | **Partly** | Table 44 (now p. 39) and Table 53 are readable; Tables 13, 15, 16 bottom, 18, 20, 24, 57 and 62 are still about 5 pt. |
| P18 Whitespace | **Not fixed** | pp. 25, 30, 31, 41, 49. |
| P19 Name the four models in Section 7 | Fixed | l. 373-374. |
| P20 Conclusion max rule for a weaker grader | **Not done** | l. 484-485 unchanged in that respect. |

### "To 9" items from round 21

| Item | Status |
|---|---|
| 1. A non-Anthropic grader on the benchmark | **Not done.** Limitations l. 460-461 still discloses "three models from one provider". |
| 2. Leaderboard sensitivity to the reference draw | **Done** (R22-B, registered, 9/9). The write-up undersells and partly misreports it (M2, M5). |
| 3. A non-Anthropic frontier judge on factual P3 with a same-interface retest | **Not done.** |
| 4. Main-text trim to about 6 numbers per paragraph; abstract to about 200 words | **Partly.** The Section 6 acceptance paragraph and Section 7 benchmark paragraph now carry about 14 and 16 numbers, *up* from round 21 because the R22 results were added inline. Abstract 252 words. |
| 5. Human labels for 200 unboxed replies | **Substituted** by a frontier-model audit (R22-A). |

### Numbers spot-checked (50 checks)

| # | Quoted (location) | Source | Result |
|---|---|---|---|
| 1 | 197 registered predictions; 129/11/17/17/23 (abstract; l. 205-207) | Appendix B l. 802-806: 129+11+17+17+18+2+3 = 197; round 21 185 + R22-A 3 + R22-B 9; confirmed 118+2+9; falsified 16+1 | match |
| 2 | "All 18 predictions registered for the extra graders and the second draw were confirmed" (l. 409-410) | `registration_round21.md` (9/9) + `registration_round22.md` l. 81-83 (9/9) | match |
| 3 | Audit agreement 91% (l. 190) | `r22a_label_audit.json` pooled.agree_any_format 0.9107 | match |
| 4 | Confirms 86%, predicted 90% (l. 191) | pooled.any_correct_confirmed 0.8624; P-R22A2 ≥ 0.90 falsified | match |
| 5 | Qwen2.5-14B reading 94.7% (App. G) | pooled.agree_qwen14b 0.9472 | match |
| 6 | Credits 7.4% of rule rejections (App. G) | pooled.any_wrong_called_correct 0.0739 | match |
| 7 | "mostly rejecting replies that list several numbers" (l. 191-192) | `disagreements`: 6 lists, 5 NONE, 2 single integers of 13 | **mismatch** (M4) |
| 8 | "5 are subset-sum or Goldbach answers" (App. G; registration l. 105) | `disagreements` any_format 0 / reader 1: 6 of 8 subset or Goldbach problem_ids | **discrepancy** (M4.2) |
| 9 | Second-draw pooled −21.3 / −16.9 / −17.1 (App. K) | `r22b_redraw_*` pooled.draw2_minus_list −0.2131 / −0.1691 / −0.1711 | match |
| 10 | Pooled change "at most 3 points" (l. 408) | draw2_minus_draw1 +0.0101 / −0.0184 / +0.0302 | match |
| 11 | Stop matching lose 25-38 pp (l. 409) | losers_draw2_minus_draw1 −0.3819 / −0.2714 / −0.25 | match |
| 12 | Start matching gain 23-35 pp (l. 409) | gainers_draw2_minus_draw1 +0.3506 / +0.2317 / +0.2931 | match |
| 13 | Credited 100 → 61.8, 99.3 → 72.1, 99.3 → 74.3 (App. K) | losers_credited_draw1/2 | match |
| 14 | Credited 64.4 → 99.4, 76.2 → 99.4, 68.4 → 97.7 (App. K) | gainers_credited_draw1/2 | match |
| 15 | Per-model move at most 8.1 points (App. K) | `r22b_redraw_haiku` claude-haiku draw2_minus_draw1 +0.0805 | match |
| 16 | Opus-graded Llama −5.9 [−13.2, +0.7] (Table 49) | `r22b_redraw_opus` meta-llama −0.0588 [−0.1324, 0.0074] | match |
| 17 | Haiku − Llama, Sonnet 5, draw 1: −0.7 [−10.7, +8.7] (l. 405; Table 50) | `r22d_ranking_intervals` Sonnet 5 reference −0.0067 [−0.1074, 0.0874] | match |
| 18 | Haiku 4.5 grader, draw 1: −7.4 [−18.1, +2.7] | `r22d` Haiku 4.5 reference −0.0738 [−0.1812, 0.0268] | match |
| 19 | Opus 5 draw 1 +17.0 [+8.5, +25.5] (Table 50) | `r22d` Opus 5 0.1702 (141 q) against registration +16.2 (`r22b_redraw_opus` ref_draw1 0.1618, 136 q) | both correct; populations unlabeled (Polish 5) |
| 20 | Draw 2 +6.7 [−3.4, +16.1]; +3.4 [−6.0, +12.8] (Table 50) | `r22b_redraw_sonnet` / `_haiku` haiku_minus_llama.ref_draw2 | match; **omitted from main text** (M2) |
| 21 | "25 points ahead" (l. 404) | haiku_minus_llama.answer_list 0.255 | match |
| 22 | Draw-2 Sonnet/Opus range (implied "7-40 under either draw", Table 1) | draw2_minus_list min −0.0956 (Opus→Opus), max −0.3289 (Sonnet→Haiku) | **imprecise** (M2.4) |
| 23 | Qwen2.5-7B 98.1% → 83.3% (App. K); "at least 83% in every bin" (l. 349) | `r22c` mace\|Qwen2.5-7B 0.9809 … 0.833; min 0.833 | match |
| 24 | phi-4 88.6% → 45.5%; "phi-4 46%" (l. 349) | `r22c` mace\|phi-4 0.886, 0.4552 | match |
| 25 | Sonnet 5 19%, Opus 5 31% at a blind 10 (l. 349) | `r22c` mace\|Sonnet 5 [10,10] 0.1852; mace\|Opus 5 0.3134 | match |
| 26 | "Matching answers stay at or below 10% in every bin" (Fig. 3 caption) | `r22c` Sonnet [0,7] match 0.45 (20); Opus 0.6429 (14); Qwen [0,5] 0.1041 (394) | **mismatch** (M1) |
| 27 | phi-4 58.9% → 4.8% on replication (App. K) | `r22c` repl\|phi-4 0.5897, 0.0482 | match |
| 28 | "2 of the 282 ... against 78" (l. 322-323) | `r20a_sonnet_retest` mace 0/81, 15; `r20a_opus_retest` mace 2/201, 63 | match |
| 29 | Factual 19%-83% (l. 320-321; Fig. 3a) | 0.1852, 0.3134, `r21a_mace_acceptance` 0.833, 0.4194 | match |
| 30 | Arithmetic Sonnet 11%, Opus 4% (Fig. 3a) | (13+13)/(150+87) = 11.0%; (10+3)/(211+113) = 4.0% | match |
| 31 | Arithmetic Qwen2.5-7B 21%, phi-4 8%, 14B 24%, gemma 57% (Fig. 3a) | `r20d` weighted 20.9%, 7.6%; 0.2392; 0.5654 | match |
| 32 | Table 1 "at most 0.4% of those that match" | `r20d` repl\|Qwen2.5-7B match 0.0043 | match |
| 33 | Pooled shortfall 22 / 16 / 20 (l. 377) | Table 47 / `r21_graders.tex` −22.3 / −15.6 / −20.1 | match |
| 34 | Sonnet-graded blind within 3 per model (l. 377-378) | Table 46: 67.8/69.1, 92.6/94.6, 96.0/98.7, 99.3/100 (max 2.7) | match |
| 35 | Haiku blind −9 (l. 379, 404) | Table 47 −9.2 | match |
| 36 | Max rule "5 points for one model under Haiku 4.5" (l. 422) | Appendix K l. 2157 −5.4 | match |
| 37 | Max-rule cost 6.7 pp, 0.15 AUROC paired (l. 425-426) | `tables/protocol_exact.tex` MATH-500 solution −6.7 [−11.4, −1.9]; −0.15 [−0.19, −0.12] | match |
| 38 | Table 2 MATH-500 max rule +23.8 for both answer and solution | `protocol_exact.tex` +23.8 [+14.3, +33.3] and +23.8 [+15.2, +32.4] | match (coincident values, distinct intervals) |
| 39 | Table 2 Reveal − ref. column | Table 16 original scorer: −0.22 → −0.11, −0.13 → −0.01, −0.18 → −0.23, −0.25 → −0.20, −0.06 → −0.05, +0.29 → +0.25 | consistent to rounding |
| 40 | "below blind for three of four ... and for both on MACE" (l. 418-419) | Table 16 Blind-then-reveal column | match |
| 41 | P2 Verdict 0.06-0.08, 0.04, 0.02 (l. 310-312) | Table 45 −0.080, −0.057, −0.037, −0.015 | match |
| 42 | Full-credit sentence 36 → 18 pp, → 8 pp (l. 355-356) | Table 45 +35.6 → +18.1; +36.3 → +8.1 | match |
| 43 | Thinking 2.85 → 0.32; 1.98 → 0.12 (l. 360-361; Fig. 3c) | Appendix L; Table 13 | match |
| 44 | Fig. 3d +36/+15, +44/+22, +42/+18 | Appendix K 35.6/14.9; Table 54 44.3/21.6; Table 13 41.6/17.8 | match |
| 45 | Open-judge arithmetic AUROC 0.17-0.27; boxed 0.07-0.14 (l. 263-264) | Table 27 any-format and boxed columns | match (model-read 0.16-0.25; M4.3) |
| 46 | Unboxed 38%-43% (l. 187-188) | Appendix G 61.6%, 57.1% boxed | match |
| 47 | Swap 5.25/4.09/3.04; 5.41/3.92/2.66 (l. 212-213) | Table 8; Table 34 | match |
| 48 | MATH-500 28.6/30.6; MACE 29.4†/26.5 (l. 268-269) | Table 10; Table 12; Table 7 | match |
| 49 | Selection +2.0/+6.1; −30.3 (l. 412-414) | Table 12 / Table 56; Table 26 any-format | match |
| 50 | Figure 3 print font sizes | `fig3_acceptance.pdf` 379.9 pt placed at 397.5 pt (× 1.046): panel b legend 5.9 → 6.2 pt; c-d value labels 6.3 → 6.6 pt | **below 7 pt** (M3) |

**Registration marks.**
- **Consistent with the registrations:**
  - the Setup audit sentence (R22-A, unmarked);
  - the redraw sentence and the Table 1 Consequence row (R22-B, unmarked);
  - the binned sentence (†; `r22c` is not in any registration);
  - the ranking-interval sentence (†; `r22d` post hoc);
  - the Table 50 caption (first-draw columns post hoc, second-draw column a registered readout, per `registration_round22.md` l. 49-50);
  - the Figure 4 caption.
- **Unmarked readouts, acceptable.** "Moves each grader's pooled shortfall by at most 3 points" is not a listed readout in R22-B ("per-model accuracy under each draw and its change" is). Under the paper's convention an unmarked registered readout is acceptable.

---

## 5. Figure-by-figure and table-by-table critique

### Main text

**Figure 1 (p. 1).**
- **At the bar.** A concrete task, one fixed reply scored 10.0 / 2.9 / 9.3, "The text never changed", and a pool-level panel with the answer-key zero line. Fonts about 8 pt; the selection of the example is disclosed.
- **Minor.** Panel c's y label still lacks "(points out of 10)"; the caption carries it.

**Table 1 (p. 3).**
- **At the bar.** The paper's credibility asset: predictions, what each rules out, marks, verdicts, and the failed predictions named near each row.
- **Fix:**
  - the Consequence row's draw range (M2.4);
  - P2 label choice (M4.3);
  - P3 "2 of 843" scope (Polish 4).
- The Moderators row is clear.

**Figure 2 (p. 5).**
- **Strengths.** A shared row list, the one-answer block against the several-answers block, "n/a" labels now left of zero, and a minimum font of about 7.5 pt.
- **Remaining.** Grey ticks touch the GPT-4.1 triangles; the registration wording is slightly at odds with Appendix E (Polish 9, 10).
- The title's "most on arithmetic" is accurate.

**Figure 3 (p. 6).**
- **Panel a** is the paper's P3 figure and is at the bar.
- **Panel b** adds the right analysis in the wrong form:
  - a false caption claim about the matching floor, and a slope read without that floor (M1);
  - the open-marker bug that makes three differing-answer series look like matching answers;
  - a 6.2-pt legend, overlapping markers at 9-10, and integer bins at midpoints (M3).
- **Panels c-d** are clear; "−0.01" still sits on the axis.
- **The float** carries two stories and an overlong title and caption (M6).
- **Registration marks** in the caption are correct.

**Figure 4 (p. 7).**
- **Strengths.** Three panels in one grammar, the referenced condition shaded, 95% intervals at "judge, reference", a dotted max-rule connector, and Haiku 4.5 visibly collapsing to Llama level. The title now agrees with the Haiku panel. Fonts are about 8-9 pt at print (351 pt scaled to 397.5).
- **Problems.**
  - It shows the first draw only, while the text and Table 1 now rely on two (M5).
  - The Opus 5 and Sonnet 5 lines are similar greys.
  - The Opus panel's 141 questions against 136 for the draw comparison should be stated once.

**Table 2 (p. 8).**
- **Strengths.** One message; the registered protocol beside the post hoc rule; the Reveal − ref. column with a coherent bold rule; k>1 MACE accuracy.
- **Problems.**
  - "−0.00".
  - A 170-word caption.
  - The API judges' k-pool max-rule values (−0.023, −0.027) are still only in Table 45. "Within 0.03" holds, so this is acceptable.

### Appendix (brief)

- **Table 4 (ledger).** Excellent and current. The R22 rows (p. 19) match `registration_round22.md` (2 confirmed and 1 falsified; 9 confirmed), and the amendment for the temperature error is disclosed.
- **Appendix G (p. 28).** Clear account of the audit; fix "5 against 6" and add the model-read preference (M4).
- **Tables 43-44 (p. 39).** Accurate against `r20a`, `r20d` and `r21a`; Table 44 is now legible.
- **Tables 45-47 (pp. 40-41).** Accurate. Page 41 is half whitespace.
- **Tables 48-50 (p. 42).** Accurate against `r22b` and `r22d`. Table 50's Opus row mixes populations (Polish 5). These three tables are the most interesting new evidence in the paper and deserve a main-text pointer (M5).
- **Tables 51-52 (p. 43).** Accurate against `r22c`, and they contradict the paragraph above them (M1). Legible.
- **Table 53.** Accurate; legible.
- **Legibility and whitespace.** Tables 13, 15, 16 (bottom), 18, 20, 24, 57 and 62 are still about 5 pt (Polish 13). Pages 25, 30, 31, 41 and 49 carry large whitespace (Polish 14).

---

## 6. What is at the bar (leave alone)

- **Title.** A claim, memorable and accurate.
- **Opening paragraph and Figure 1.** "The text never changed; only the correct answer the judge was shown did."
- **The three readings, Equation 1 and the separation logic.** It says why P2 needs P2′, why P3 separates the readings, and that the model is not fitted.
- **The swap design** with the matches-neither control.
- **The registered same-interface retest** (0 of 318; 2 of 525).
- **The benchmark design.**
  - Answers are held fixed across graders.
  - Additional graders and the second draw were registered before any call, with the draw rule excluding containment.
  - Thresholds 5 and 10 are reported.
  - Self-grading is disclosed.
- **The registered label audit.** It includes a falsified prediction reported in the main text, and a disclosed amendment after an API failure before any answer existed. This is the kind of honesty reviewers remember.
- **The P2 Verdict and the max-rule paragraph.** Precise after the round-21 fixes.
- **Table 2's "Reveal − ref." column and bold rule.**
- **Limitations.** Specific and prominent, including one provider and no factual noise control for open judges.
- **Page limit.** The main text ends on p. 9, l. 485.

---

## 7. What would move the score

### To a secure 8 (rewrites and re-plots only; about 1 day, no API spend)

1. **M1 and M3.** Re-plot Figure 3b with the matching floor, filled markers, integer bin positions and 7-pt text. Rewrite the caption, the Section 6 sentence and the Appendix K sentence. About 2 hours.
2. **M2 and M5.** Rewrite the Section 7 ranking and redraw sentences, the intro clause and the Table 1 Consequence row. Add hollow second-draw markers to Figure 4 from `r22b_redraw_*.json`. About 2 hours.
3. **M4.** Correct the audit summary and add the model-read range to Table 1 and Section 5. 30 minutes.
4. **M6.** Retitle Figure 3 and move its per-panel registration and sample text to one sentence and Appendix L. 1 hour.
5. **Polish 1-5 and 11.**

### To 9 (about 1 week, under USD 60)

1. **A non-Anthropic grader on the benchmark** (new data; about 1.2k calls per draw, under USD 15 per draw). A current OpenAI or Google model grades the 596 answers blind and under both reference draws. This removes "one provider" from the headline consequence, and gives a fourth replication of the draw effect.
2. **A non-Anthropic frontier judge on factual P3 with a same-interface retest** (new data; about 2-3k calls, under USD 30). Round-20 item 4 and round-21 item 3, still open. The Verdict could then say "noise-controlled on factual questions for judges from two providers".
3. **Leaderboard sensitivity as a figure** (re-analysis; 2 hours). For each grader, plot per-model referenced accuracy under draw 1 against draw 2 (12 points, one diagonal). Report how often a pairwise order flips between draws. Optionally add a third draw where a third non-containing answer exists (about 1.8k calls, under USD 15). "The leaderboard follows the reference draw" is the crispest second consequence the paper has, and it is currently in an appendix table.
4. **Main-text density** (rewrite, 1 day). The Section 6 acceptance paragraph (about 14 numbers) and the Section 7 benchmark paragraph (about 16) are heavier than in round 21. Move counts to captions and target 6 numbers per paragraph. Cut the abstract to about 200 words.

### To 10, best-paper territory (weeks; new data)

1. **A second natural multi-answer benchmark with human-verified answer sets**, repeating the three-grader, two-draw study. For example, NQ-open items that the paper's own audit flags (30%), or a constructive task with an executable checker.
2. **A prospective registered test of the recommendation.** Register the max rule, and the full-credit sentence plus max rule, before a fresh k-pool seed and held-out MACE questions. Report grading, benchmark accuracy and the unique-answer cost.
3. **A direct manipulation of verification.** Set v_c by design (for example, give the blind call the full answer list or a lookup tool). Show the differing-minus-matching rejection gap against v_c: flat under agreement, falling to zero under verification failure. Figure 3b, once corrected per M1, is the observational version.
4. **Human labels for 200 unboxed replies.** Upgrades R22-A from a model audit to ground truth, and settles which labeling Table 1 should quote.

**If the rewrites, the Figure 3b and Figure 4 re-plots, and items 1-3 of "To 9" were done,** the paper would have:
- one question and a clean manipulation;
- a separating prediction with a noise control across providers and a correctly baselined graded test;
- a benchmark consequence replicated across providers and reference draws, including the finding that the draw reorders models;
- a measured partial remedy;
- a main text a reviewer absorbs in ten minutes.
