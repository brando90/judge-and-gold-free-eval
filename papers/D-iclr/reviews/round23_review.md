# Round 23 Area Chair review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

**Materials.**
- **PDF.** `round23_main.pdf`, 49 pages (byte-identical to `papers/D-iclr/main.pdf`).
  - Main text pp. 1-9; the Conclusion ends at l. 478 and the AI-use statement starts at l. 480.
  - Statements pp. 9-10, references pp. 10-12, appendix pp. 13-49.
  - Every page was read as a rendered image. I also made 300-dpi crops of Figure 2b, Figure 3 (a, b-c) and Figure 4.
- **Sources checked.**
  - `main.tex` and `appendix.tex` (the Appendix K binned paragraph).
  - `scripts/make_figures.py`: the Figure 3 block (ll. 330-465), the Figure 2 block (ll. 757-864) and the Figure 4 block (ll. 867-914).
  - `papers/analysis/` JSON files:
    - `r22a_label_audit.json`, `r22b_redraw_{sonnet,opus,haiku}.json`, `r22c_acceptance_bins.json`, `r22d_ranking_intervals.json`;
    - `r20a_{sonnet,opus}_retest.json`, `r20c_leaderboard.json`, `r20d_matched_acceptance.json`, `r20g_frontier_safeguards.json`;
    - `r21a_mace_acceptance.json`, `r21a_leaderboard_{opus,haiku}.json`, `r21a_maxrule_{opus,haiku}.json`.
  - `registration_round21.md` and `registration_round22.md`, plus the ledger (Appendix B, Table 4).
  - `experiments/tfa-vs-judge/scripts/r8_extract_answers.py` and `r22_opus_read_answers.py`.
- **One re-analysis of my own.** A paired question bootstrap (seed 0, 2,000 resamples) of the between-draw change in the Haiku 4.5 − Llama-3.1-8B gap. It was computed in memory from `runs/r20|r21/leaderboard_*_api/pool.jsonl` and `runs/r22/redraw_*_api/pool.jsonl` with the selection rule of `r22_redraw_analysis.py`. No file was written.
- **Line numbers** are PDF margin numbers.
- **Independence.** The round-22 review was read only for the audit in Section 4.
- **Writes.** Nothing in the project was modified other than this file.

---

## 1. Summary and ease of extraction

**Question.** When a question has several correct answers, does a reference-guided LLM judge treat the reference as an answer key? Two alternatives are set against it:
- **Verification failure.** The reference is the only evidence for a judge that cannot recognize other correct answers.
- **Agreement.** The judge rewards matching the one answer it is shown, even when it can recognize the others.

**Claims as a reader extracts them.**
1. **P1, the swap.** Moving the reference between two correct answers moves byte-identical text by 2.7-5.4 points out of 10 (three judges, 120 constructed tasks). Text matching neither reference does not move.
2. **P2 and P2′, grading.**
   - Several correct answers: grading AUROC for correct answers that differ from the reference falls 0.06-0.16 for four judges on MACE. On arithmetic it falls 0.17-0.27 for four open judges (0.16-0.25 with model-read labels, 0.07-0.14 on boxed replies only).
   - One correct answer: the reference raises best-of-64 accuracy on MATH-500 by 29-31 pp.
3. **P3, not only verification failure.**
   - Among correct factual answers a judge accepts blind, 19%-83% of those that differ from the reference drop to 3 or below once it is shown. None of those that match do.
   - A second same-interface blind call drops 2 of 282.
   - *Rewritten this round:* binned by blind score, rejection falls from the middle to the top bins for phi-4 and the API judges. Among each judge's surest answers it stays at 19% or more, where matching answers are never rejected.
4. **Moderators.** Thinking nearly removes the swap on arithmetic but only halves the factual false-rejection rise. A full-credit sentence halves the harm without restoring grading.
5. **Consequence.**
   - On 149 MACE questions, all three Claude graders shown a reference put every model below its answer-list accuracy (22, 16, 20 points pooled). Blind, Sonnet 5 and Opus 5 stay within 3 points.
   - A registered second reference draw keeps the pooled shortfall within 3 points and moves credit for answers whose match status changes by 23-38 pp.
   - *Promoted to the abstract this round:* "which listed answer is drawn as the reference can reorder the models."
6. **Safeguard.** The max rule keeps grading within 0.03 AUROC of blind and pooled benchmark accuracy within 2 points of the lists. It costs up to 6.7 pp with a unique answer.
7. **Labels.** In a registered audit, Opus 5's reading agrees with the any-format labels on 91% but confirms only 86% of the rule's credits (a prediction of 90% was falsified).
8. **Registration.** 197 predictions: 129 confirmed, 11 not confirmed, 17 falsified, 17 split, 23 other.

**2-minute pass** (title, abstract, Figure 1, Table 1). Fast and mostly correct:
- the reference moves unchanged correct text;
- the effect survives the judge's own acceptance;
- it lowers benchmark accuracy for frontier graders.

The abstract (241 words) now ends its benchmark sentence with a ranking claim that no interval in the paper supports (M1).

**10-minute pass** (adds Figures 2-4, Table 2). The reader also gets:
- the positive control;
- the acceptance lollipop and the binned panel, now with a grey matching floor;
- the factual thinking bars;
- the benchmark slope chart, now with hollow second-draw markers;
- the safeguards table.

**Where a careful reader now trips.** Again, all in text rewritten this round:
1. **Figure 3's title** says "confidence and thinking reduce this without removing it". The abstract and Table 1 say thinking nearly removes the effect on arithmetic. Qwen2.5-7B's curve in panel b does not fall with confidence at all (M2).
2. **The ranking claim.** Abstract, introduction, Section 7 and Conclusion all say the reference draw reorders or decides the ranking. Every interval behind that is compatible with no change (M1).
3. **Section 6's new arithmetic clause**, "phi-4 and Opus 5 fall to 5% or less among their surest answers", is false for phi-4 on the k-pool (15%) (M3).

**Overall.** The paper keeps the strengths that make it an accept:
- one question and a three-reading model saying what each reading predicts;
- a byte-identical swap with a matches-neither control;
- a positive control;
- a separating test with a registered noise control;
- a benchmark consequence replicated across three graders and two registered reference draws;
- unusually honest registration, including falsified predictions in the main text.

Round 22's must-fix list was addressed in substance, and in several places verbatim (Section 4). The recurring pattern is that each round's newly written sentences are less precise than the ones they replace. This round the imprecision reached the abstract.

---

## 2. Score and confidence

**Score: 8 / 10** (accept, good paper). **Confidence: 4 / 5.**

**Single biggest reason.** The central claim is established the way a best-paper committee wants: a byte-identical manipulation, a positive control, a separating prediction with a same-interface noise control, and a registered consequence with 18/18 confirmed predictions. The round-22 errors were fixed and verified against the JSON files (Figure 3b floor, second-draw markers, audit counts, the Table 1 draw range).

**Why not 9.**
1. **A new headline overclaim.**
   - "Which listed answer is drawn as the reference can reorder the models" (abstract l. 026-027) rests on point estimates.
   - All four Haiku 4.5 − Llama-3.1-8B intervals include zero (Table 50), and all 12 per-model between-draw changes include zero (Table 49).
   - My paired bootstrap of the between-draw change in that gap gives +7.4 [−3.4, +18.1] (Sonnet 5 grading) and +10.7 [0.0, +21.5] (Haiku 4.5 grading).
   - No referenced call was ever repeated with the same reference, so there is no noise floor for a ranking flip.
2. **Figure 3 still carries two stories under a title that overgeneralizes.** Panel b remains the hardest graphic in the paper to read at print size.
3. **Main-text density rose again.** The two paragraphs with the new results carry about 17 and 18 numbers each (224 and 214 words). The Figure 3 caption is 217 words. That is far from the "Mirage" standard of one figure, one message.
4. **The consequence is still narrow and disclosed.** It has:
   - one benchmark;
   - one answer per model;
   - graders from one provider;
   - a factual P3 noise control only for Anthropic judges.

**What is needed.** M1-M6 are rewrites and one re-plot (about a day). M1 can optionally be settled with a same-draw referenced regrade (under USD 10).

---

## 3. Ranked issues

### MUST FIX

#### M1. "The draw can reorder the models" is asserted in the abstract, introduction, Section 7 and Conclusion without interval support or a noise floor
**New data: none required for the rewrite. Optional: a same-draw regrade.**

**Location.**
- Abstract l. 026-027: "which listed answer is drawn as the reference can reorder the models."
- Intro l. 096-097: "The effect lowers benchmark scores under both of two reference draws, which answer is drawn can reorder models, and keeping ..." This is also a comma splice.
- Section 7 l. 371-375: "Sonnet 5 and Haiku 4.5 shown the first reference put the two level (−0.7 and −7.4 points) and, shown a second reference ..., +6.7 and +3.4 (all four intervals include zero), while Opus 5 keeps most of the lead under both draws."
- Conclusion l. 473-474: "with rankings that depended on which listed answer was drawn."

**Problem.**
1. **The only reordering is in point estimates.**
   - The flip is Haiku 4.5 against Llama-3.1-8B under Sonnet 5 and Haiku 4.5 grading (`r22b_redraw_{sonnet,haiku}.json` `ranking_ref_draw1` vs `ranking_ref_draw2`).
   - The draw-1 gaps are −0.7 [−10.7, +8.7] and −7.4 [−18.1, +2.7] (`r22d_ranking_intervals.json` `reference`). The draw-2 gaps are +6.7 [−3.4, +16.1] and +3.4 [−6.0, +12.8] (`haiku_minus_llama.ref_draw2`).
   - Neither draw resolves the order, so "reorder" means that two unresolved orders came out differently.
2. **The quantity that would support "reorder" is compatible with zero.** That quantity is the between-draw change in the gap. My paired question bootstrap on the producer's question set gives:
   - Sonnet 5 grading (149 questions): **+7.4 [−3.4, +18.1]**;
   - Haiku 4.5 grading (149 questions): **+10.7 [0.0, +21.5]**;
   - Opus 5 grading (136 questions): +9.6 [+0.7, +19.1]. This is the only interval excluding zero, and it belongs to the grader whose order did *not* flip.

   Table 49's per-model between-draw changes all include zero (for example Haiku 4.5 graded by itself, +8.1 [−1.4, +17.4]).
3. **There is no noise floor.** The graders ran at the API's default temperature, and no referenced call was repeated with the same reference. A gap of −0.7 points is one question. A same-draw regrade could flip it as easily as a new draw. The R20-A blind retest does not bound referenced-call variability at the 7-point threshold.
4. **Two local imprecisions in Section 7.**
   - "Put the two level (−0.7 and −7.4 points)": −7.4 puts Llama-3.1-8B 7 points ahead.
   - "Opus 5 keeps most of the lead under both draws": on the 136 questions with both draws, the list gap is +23.5 (`r22b_redraw_opus.json` `haiku_minus_llama.answer_list` 0.2353) and the draw-2 gap is +25.7. Under draw 2, Opus 5 keeps all of the lead.
5. **What is solid** is the registered, interval-backed result: redrawing moves credit for the 318 answers whose match status changes, by −25 to −38 pp and +23 to +35 pp, with every interval excluding zero (`pooled.losers_draw2_minus_draw1`, `gainers_draw2_minus_draw1`). That is P1 at benchmark scale, and it is the claim to headline.

**Fix (rewrite; no new data).**
- **Abstract l. 026-027:**
  > "...and within 3 points when grading blind; a second reference drawn from the same lists leaves this shortfall unchanged but moves credit for the answers whose match changes by 23 to 38 points."
- **Intro l. 096-097:**
  > "The effect lowers benchmark scores under both of two reference draws, and which answer is drawn decides which correct answers get credit. Keeping the higher of the blind and referenced scores protects grading at a cost when the answer is unique (Section 7)."
- **Section 7 l. 371-375:**
  > "The answer lists put Haiku 4.5 25 points ahead of Llama-3.1-8B. Shown the reference, Sonnet 5 and Haiku 4.5 no longer separate the two under either draw (gaps from −7.4 to +6.7 points, all intervals including zero), while Opus 5 keeps Haiku 4.5 ahead under both (+17.0 and +25.7).†"
- **Conclusion l. 473-474:** replace "with rankings that depended on which listed answer was drawn" with:
  > "and a second reference draw moved credit for individual answers by 23 to 38 points without reducing that shortfall."

**Optional (new data, under USD 10, about 1.8k calls).** Re-run each grader's referenced calls with the *first* reference (596 calls per grader). Report:
- the same-draw change in per-model accuracy and in the Haiku 4.5 − Llama-3.1-8B gap, next to the between-draw change;
- how often the pairwise order flips under a regrade against a redraw.

Register it before running. If the redraw moves the gap more than the regrade, "the draw can reorder models" becomes a claim the paper owns. If not, the rewrite above is the right text.

#### M2. Figure 3's title contradicts the abstract and Table 1, and overstates panel b
**New data: none.**

**Location.** Figure 3 title, p. 6 l. 293-294: "The reference rejects correct answers the judge already accepts, most on factual questions; confidence and thinking reduce this without removing it."

**Problem.**
1. **"Thinking ... without removing it" is unscoped.** The abstract says "thinking nearly removes the effect on arithmetic". Table 1's P1 Verdict says "near zero on arithmetic with thinking", and Section 6 l. 353-354 says it drops "from 2.85 to 0.32 ... and from 1.98 to 0.12". The title is true only of panel c, which is factual-only. A skimmer reading the figure title gets the opposite of the abstract's finding (3).
2. **"Confidence ... reduce[s] this" is false for one of the four plotted judges.**
   - Qwen2.5-7B rejects 98% of differing answers in its lowest bin and 83% in its top bin, but its matching floor also falls from 10% to 0%. The differing-minus-matching gap is 88 against 83 points: flat (`r22c_acceptance_bins.json` `mace|Qwen2.5-7B` bins [0,5] and [9.8,10]).
   - The main text l. 314-315 correctly restricts the decline to phi-4, Sonnet 5 and Opus 5. The title does not.

**Fix.** Title:
> "Figure 3: The reference rejects correct answers the judge already accepts; on factual questions neither blind confidence nor thinking removes this."

Every clause holds:
- top-bin rejection is 19%-83% with zero matching;
- thinking leaves +15 to +22 pp.

#### M3. The new arithmetic clause in Section 6 is false for phi-4 on the k-pool
**New data: none.**

**Location.** Section 6, p. 6 l. 318-319: "On arithmetic, phi-4 and Opus 5 fall to 5% or less among their surest answers (Appendix K)."

**Problem.**
- phi-4's top bin is **15.3%** on the k-pool (`r22c_acceptance_bins.json` `kpool|phi-4` bin [9.8, 10] `nonmatch.share_le3_with_reference` 0.1533, n = 646; Table 51 row "phi-4, k-pool", "15 (646)"). Its lowest value anywhere on the k-pool is 7.7%.
- The 5% figure holds only on the replication pool (4.8%, n = 1,741). Opus 5 is 4.7% (replication) and 2.7% (k-pool).
- Appendix K l. 2274 scopes it correctly ("58.9% to 4.8% on the replication pool"); the main text dropped the scope.
- **This clause is load-bearing.** It is the main text's only observational hint that P3's remainder is small on arithmetic for some judges. It sits next to the Verdict "P3 holds for all six judges" (l. 358). The reader needs the correct magnitude to reconcile the two.

**Fix, l. 318-319:**
> "On arithmetic the remainder is small for some judges: among their surest answers on the replication pool, phi-4 and Opus 5 reject 5% or less (15% and 3% on the k-pool; Appendix K)."

#### M4. Figure 3b is still not a figure a reader can decode at print size, and the sentence reading it generalizes from three judges to all
**New data: none (re-plot of `r22c_acceptance_bins.json`).**

**Location.**
- Figure 3b, p. 6 l. 271-287; `make_figures.py` l. 427-456.
- Caption (b), l. 299-301.
- Section 6, l. 318: "Verification explains part of the effect; the remainder, among answers the judge already accepts, is what agreement predicts."

**Problem.**
1. **Two binnings share one unlabeled axis.**
   - Open judges are binned on expected score (<5, 5-7, 7-9, 9-9.6, 9.6-9.8, ≥9.8) and plotted at 2.5, 6, 8, 9.3, 9.7 and 9.9.
   - API judges are binned on integer score (≤6, 7-8, 9, 10) and plotted at 5, 7.5, 9 and 10 (`XPOS_API`).
   - The caption says only "integer scores for Sonnet 5 and Opus 5". The open-judge bin edges appear nowhere in the main text.
   - An open judge's "9.9" and an API judge's "10" look equivalent, yet the paper itself needs a 3%-wrong-answer threshold to equate them (Figure 3a).
2. **Crowding.**
   - The panel is 0.235 × 5.5 in ≈ **1.3 in (3.3 cm) wide**.
   - In x ∈ [9, 10], nine differing-answer markers and nine grey markers sit within one x-unit.
   - phi-4's non-monotone tail (46 → 34 → 46) and Qwen2.5-7B's (84 → 90 → 83) cannot be read. The phi-4 square at (9.9, 46) touches the "phi-4" end label.
   - At the 300-dpi crop the series are separable only by marker shape.
3. **The grey floor is unidentified.**
   - Four grey lines with 2.6-pt markers carry the caption's 45% (Sonnet 5), 64% (Opus 5) and 10% (Qwen2.5-7B). Which grey line is which can be inferred only from marker shapes at about 2.7 pt.
   - The caption omits phi-4's 7.4% in its lowest bin (`mace|phi-4` [0,5] `match` 0.0738, n = 325).
   - "Rejected only in the lowest bins" is approximately right (Qwen2.5-7B 1.2% in its 5-7 bin).
4. **The sentence generalizes.** "Verification explains part of the effect" is supported for phi-4, Sonnet 5 and Opus 5. It is not supported for Qwen2.5-7B, whose differing-minus-matching gap is flat (M2.2). The previous sentence (l. 314-315) is correctly scoped; this one is not.

**Fix.**
- **Re-plot.** Use a categorical x-axis, "blind-score bin (lowest to highest)", with the bin edges printed under each tick. Use two small multiples, open judges (6 bins) and API judges (4 bins), sharing the y-axis. Alternatively, plot the differing-minus-matching gap directly and drop the grey lines. Label grey series at their left end ("match, Opus 5").
  - **Space.** Drop panel c's second row of labels, or move panel c under panel a. Either way, panel b should get at least 1.8 in of width.
- **Caption (b):**
  > "On MACE, the share of correct answers scored 3 or below with the reference, by blind-score bin (open judges: <5, 5-7, 7-9, 9-9.6, 9.6-9.8, ≥9.8; API judges: ≤6, 7-8, 9, 10; bins with at least 10 differing answers). Grey: answers that match the reference, rejected at more than 2% only in each judge's lowest bin (Opus 5 64%, Sonnet 5 45%, Qwen2.5-7B 10%, phi-4 7%)."
- **Section 6 l. 318:**
  > "For phi-4 and the API judges, verification explains part of the effect; for Qwen2.5-7B it explains none. The remainder, among answers each judge already accepts, is what agreement predicts."

#### M5. The two paragraphs carrying this round's results are the densest in the paper
**New data: none.**

**Location.**
- Section 6 "Answers the judge accepts without a reference", l. 308-319: 224 words, about 17 numbers.
- Section 7 "Benchmark scores", l. 366-377: 214 words, about 18 numbers.
- Figure 3 caption: 217 words. Table 2 caption: 179 words.

**Problem.**
- The round-22 "to 9" item asked for about 6 numbers per paragraph. Instead, both paragraphs grew. The Section 7 paragraph now holds four model gaps, three pooled shortfalls, two ranges of credit changes, a per-model maximum, a blind bound and a prediction count.
- A reviewer skimming Section 7 cannot find the one sentence that matters: the reference lowers every model, and the draw decides which answers get credit.
- This is the opposite of the reference paper's low cognitive load, and it is where M1's overclaim hid.

**Fix (replacement paragraphs; about 10 numbers each).**
- **Section 7, "Benchmark scores":**
  > "We asked Llama-3.1-8B-Instruct, Claude Haiku 4.5, Sonnet 5, and Opus 5 for one answer to each of 149 MACE questions with several correct answers, and graded every answer with Sonnet 5, Opus 5, and Haiku 4.5, blind and with a reference drawn from each answer list (Figure 4). With the reference, every grader put every model below its answer-list accuracy, by 16 to 22 points pooled; blind, Sonnet 5 and Opus 5 stay within 3 points (Haiku 4.5, a weaker grader, under-counts by 9 even blind). A second reference drawn from the same lists (hollow markers) leaves each pooled shortfall within 3 points but moves credit for the answers whose match changes by 23 to 38 pp. All 18 predictions registered for the extra graders and the second draw were confirmed. [M1 ranking sentence, with the per-grader numbers moved to Appendix K.]"
- **Section 6, "Answers the judge accepts":**
  - Keep the threshold definition and the 19%-83% sentence.
  - Keep "a second blind call ... 2 of the 282".
  - Replace the binned sentences with the M4 text.
  - Move "Sonnet 5 and Opus 5 still reject 19% and 31%, phi-4 46%" into the caption; the values already appear in panel a.
- **Figure 3 caption.** Move the (a) threshold definition to Section 6, which already states it (l. 309-311). Target about 130 words.
- **Table 2 caption.** Move the per-cell registration list to Appendix F. Keep "Bold ..." and one registration sentence.
- **Abstract.** 241 words, down 11. The "(1) ... (2) ... (3)" sentence is still 75 words. Target 200.

#### M6. The label-audit comparison with Qwen2.5-14B is not independent, and Limitations under-describes what the audit found
**New data: none.**

**Location.**
- Setup l. 187-188: "...and a Qwen2.5-14B reading agrees with Opus 5 more often (95%; Appendix G)."
- Table 1 P2 row and Section 5 l. 257, which now cite the model-read range.
- Limitations l. 446-448: "...over-credit some replies that list several numbers."

**Problem.**
1. **The two readers share a prompt.** The Opus 5 reader uses "the extraction prompt of `scripts/r8_extract_answers.py` verbatim" (`registration_round22.md` l. 21-22; `r22_opus_read_answers.py` l. 2-3). That is the script that produced the Qwen2.5-14B labeling (`r8_extract_answers.py` l. 12: `default="Qwen/Qwen2.5-14B-Instruct"`).
   - Two models answering the same extraction prompt should agree with each other more than either agrees with a regex rule.
   - So 94.7% against 91.1% (`pooled.agree_qwen14b`, `pooled.agree_any_format`) is partly shared-prompt agreement. It is not evidence that the model-read labels are more accurate.
   - Placing the sentence right after "confirms only 86%" invites exactly that inference.
2. **Limitations names half of the over-credit.** Of the 13 replies the rule credits and the reader does not, 6 list several numbers and 5 commit to no answer (`disagreements`: `reader_line` "NONE" for repl/crt-3 idx 2, kstrat/crt-k4-0, crt-k16-12, subset-k2-11 idx 24, crt-k16-4). Limitations mentions only the lists and gives no rate.

**Fix.**
- **Setup l. 187-188:**
  > "...most of the rest list several numbers or commit to no answer. A Qwen2.5-14B reading with the same extraction prompt agrees with Opus 5 on 95% (Appendix G); because the prompts are shared, we do not treat this as validating either labeling."
- **Limitations l. 446-448:**
  > "The any-format labels were checked by a frontier model's reading, not by humans; that reading rejects 14% of the unboxed replies the rule credits, mostly lists of several numbers or replies that commit to no answer. Boxed replies alone give the conservative grading estimates."

### POLISH

1. **Abstract l. 025.** "On 149 factual benchmark questions ... Opus 5 ... score four models 7 to 40 points below". Opus 5's readouts use 141 questions. Write "On up to 149".
2. **Table 1 Consequence row** (l. 135-138). The Verdict says "Holds for three graders and two draws", but Observed names only Sonnet 5 and Opus 5. Add: "Haiku 4.5: 7-40 and 9-32 points, but 9 below the lists even blind". Source: `r21a_leaderboard_haiku` −6.7 to −39.6; `r22b_redraw_haiku` `draw2_minus_list` −9.4 to −31.5.
3. **Table 1 P3 row.** "A second blind call: 2 of 843, against 117 with the reference" still lacks scope. Write "(Sonnet 5 and Opus 5, three pools)".
4. **Dangling dagger.** l. 417, "(Appendix F).†": attach the mark to "6.7 pp" or "0.15 of AUROC".
5. **Appendix K binned paragraph** (p. 42-43, l. 2268-2275), three phrases:
   - "levels off above zero" should be "stays above zero" (the main text was fixed, the appendix was not);
   - "gemma-2-9b barely falls" is inaccurate: 88.9% → 59.8% → 54.3-62.9% (`kpool|gemma-2-9b`). Write "falls from 89% to about 55-63% and then stays flat";
   - "matching answers are rejected only in the lowest bins" has exceptions: Opus 5 k-pool 7-8 bin 14% (1 of 7), Qwen2.5-7B k-pool 5-7 bin 7.7% (1 of 13). Write "rejected at more than 2% only in the lowest bins, except bins of fewer than 15 answers".
6. **Rounding, third round unchanged.** Table 45 prints Opus 5's MACE AUROC as −0.165 (JSON −0.1645; text "0.16"). It prints the Opus 5 replication false-rejection rise as +3.6 (registration +3.7). Print −0.164 and state the rounding once.
7. **Figure 2 caption, registration wording, unchanged.** "Qwen2.5-7B's values here use the exact scorer, a post hoc rescoring" still conflicts with Appendix E l. 1095-1096, "A pre-specified experiment rescored Qwen2.5-7B on ... MACE".
8. **Figure 2 legibility.**
   - The grey boxed-only ticks still touch the GPT-4.1 triangles (300-dpi crop, rows 226 and 231; the script still offsets ticks by +0.42 row). Offset by +0.25 or draw the ticks below.
   - The italic "n/a" labels are `fontsize=6.0` in a 376.7-pt PDF placed at 397.5 pt, which gives **6.3 pt** at print. Set 7.
9. **Figure 4.**
   - In the Opus 5 panel, Sonnet 5's hollow triangle (76.5) is hidden under Haiku 4.5's hollow square (77.2).
   - The same panel draws solid points on 141 questions and hollow points on 136. The visible Llama-3.1-8B change (56.7 → 51.5, −5.2) is therefore not the paired −5.9 of Table 49. Plot both draws on 136, or say "solid: 141 questions; hollow: 136".
10. **Figure 3b y-label.** It has a double space ("scored  ≤ 3"); use `r"scored $\leq$3"`.
11. **Section 7 "Selection" paragraph** (l. 403-406). It is about P2 on MACE; moving it to Section 5's Verdict would lighten Section 7.
12. **Limitations.** Add that both reference draws come from the same answer lists, which miss 2.3%-8.1% of correct answers.
13. **Appendix G.** The 13 rule-credited disagreements are accounted as 6 + 5. Name the other 2: single integers the constraint rejects, repl/crt-22 "17" and kstrat/digitsum-k1-3 "31".
14. **Appendix legibility, unchanged.** These are about 5 pt at print:
    - Table 13 (p. 24);
    - Table 15 (p. 25);
    - Table 16, bottom block (p. 26), the source of Table 2;
    - Tables 18 and 20 (p. 27);
    - Table 24 (p. 29);
    - Table 62 (p. 49).

    Figure 6a's legend is also about 6 pt. Use `\footnotesize` with two-line headers instead of shrinking with `adjustbox`.
15. **Whitespace, unchanged.**
    - p. 25: gaps above Tables 14 and 15;
    - p. 30: the top half;
    - p. 31: top quarter;
    - p. 41: the space between Tables 46 and 47;
    - p. 49: four-fifths blank.

    `\FloatBarrier` per section plus `[!ht]` placement would recover two to three pages.

---

## 4. Audit of round-22 items

### MUST FIX (M1-M6)

| Item | Status | Evidence in this version |
|---|---|---|
| **M1** Fig. 3b caption and App. K misstate the matching floor; slope read without the floor | **Fixed, with a new error nearby** | Grey matching series added (`make_figures.py` l. 439). Caption (b) now reads "rejected only in the lowest bins (Sonnet 5 45% and Opus 5 64% below a blind 7; Qwen2.5-7B 10% below 5)", which matches `r22c` (0.45, n 20; 0.6429, n 14; 0.1041, n 394); phi-4's 7% is omitted (M4.3). Section 6 l. 314-318 adopts the suggested text nearly verbatim ("falls as phi-4 grows surer, and for Sonnet 5 and Opus 5 from their middle to their top bins ... where no matching answer is rejected ... 19% and 31%, phi-4 46%, and Qwen2.5-7B at least 83%"), all verified. The Appendix K sentence was replaced ("only in the lowest bins (up to 64% ...) and at most 0.4% from a blind 9 up"; max from 9 up is `repl\|Qwen2.5-7B` [9.8,10] 0.0043), but "levels off" remains (Polish 5). New: the arithmetic clause is false for phi-4 on the k-pool (M3), and "Verification explains part" is unscoped (M4.4). |
| **M2** Ranking reported under draw 1 only; "whichever listed answer"; Table 1 range | **Fixed, then overcorrected** | Section 7 now reports both draws (−0.7/−7.4 and +6.7/+3.4, "all four intervals include zero"). The intro reads "under both of two reference draws". The Table 1 Consequence row now reads "7-40 ... 10-33 with a second draw", verified (draw-2 range 9.6-32.9). The conclusion adds a rankings clause. But the round-22 suggestion "which answer is drawn can reorder models" was adopted into the abstract, intro and conclusion without the interval check it needed (M1). "Level (−7.4)" and "keeps most of the lead" are imprecise (M1.4). |
| **M3** Fig. 3b markers, fonts, bins | **Mostly fixed** | All differing series are filled. Two hues separate API judges (`#1f3a8a`) from open judges. Integer bins sit at 5/7.5/9/10. Direct end labels replace the legend. Fonts: legend 7.0 and end labels 7.0 pt in a 377.2-pt PDF placed at 397.5 pt gives about 7.4 pt; ticks about 7.6 pt. The old panel c ("−0.01") was removed. Not done: a categorical x-axis. Crowding at 9-10 and the mixed binning on a shared axis remain (M4). |
| **M4** Audit summary "mostly"; 5 vs 6; model-read range | **Fixed** | Setup: "most of the rest list several numbers or commit to no answer" (11 of 13). Appendix G and `registration_round22.md` l. 104-105 now say 6, with a correction note; verified by problem_id. Table 1 and Section 5 add "0.16-0.25 with model-read labels" (Table 27). New issue: the audit's reader shares the Qwen2.5-14B prompt (M6). Limitations was only partly updated (M6.2). |
| **M5** Second draw has no main-text display or pointer | **Fixed** | Figure 4 has hollow second-draw markers, verified against `accuracy_ref_draw2` for all 12 points. The caption reads "hollow markers use a second reference ... (Opus 5: 136 questions)". The text says "(hollow markers in Figure 4; Appendix K)". Residual overlap and population mismatch in the Opus panel (Polish 9). |
| **M6** Figure 3 title, caption length, two stories | **Partly** | The title was cut from 33 to 22 words, but now contradicts the abstract (M2). Registration was consolidated into one sentence ("Pre-specified: the second blind calls, Opus 5's shares in (a), and (c); the rest is post hoc"), consistent with the ledger. The arithmetic-swap panel was dropped, leaving three panels. The caption is still 217 words, and the float still carries P3 plus a moderator. |

### Important POLISH items from round 22

| Item | Status | Evidence |
|---|---|---|
| 1 Abstract to about 200 words | **Partly** | 252 → 241. |
| 2 "Protected selection" label scope | Fixed | l. 409: "(any-format labels)". |
| 3 Table 2 "−0.00" | Fixed | Prints "0.00". |
| 4 Table 1 "2 of 843" scope | **Partly** | Added "against 117 with the reference"; the pool and judge scope is still missing (Polish 3). |
| 5 Table 50 Opus populations | Fixed | Caption: "(Opus 5: its 141 questions) ... (Opus 5: the 136 questions with both draws complete)". |
| 6 "Levels off" | **Partly** | Fixed in the main text; still in Appendix K l. 2269. |
| 7 Arithmetic binned clause in main text | **Done, with an error** | Added at l. 318-319; false for phi-4 on the k-pool (M3). |
| 8 Rounding (−0.165, +3.6) | **Not fixed** | Table 45 unchanged. |
| 9 Figure 2 registration wording | **Not fixed** | Caption unchanged. |
| 10 Figure 2 tick overlaps | **Not fixed** | 300-dpi crop: ticks still touch the triangles. |
| 11 Limitations: Opus selection; same lists | **Partly** | "(141 and 136 of 149 remain)" added (l. 453-454); same-lists caveat not added. |
| 12 Conclusion: average over draws; max rule for weaker grader | **Not done** | On reflection the first is unnecessary: the second draw shows averaging would not remove the shortfall. The second remains optional. |
| 13 Appendix legibility | **Not fixed** | Tables 13, 15, 16 bottom, 18, 20, 24, 62. |
| 14 Whitespace | **Not fixed** | pp. 25, 30, 31, 41, 49. |
| 15 Table 2 caption length | **Partly** | 179 words; task counts now pointed to Appendix F. |
| 16 Figure 4 hue | **Partly** | Haiku 4.5 is drawn heavy black and separates; the other greys remain close. |
| 17 App. K gemma and Qwen2.5-14B | **Partly** | Qwen2.5-14B non-monotone added ("15%, then 39%, then 23%", verified). I now disagree with the round-22 acceptance of "gemma-2-9b barely falls" (89% → 56%; Polish 5). |

### "To 9" items from round 22

| Item | Status |
|---|---|
| 1. Non-Anthropic grader on the benchmark | **Not done.** Limitations l. 452-453 still says "three models from one provider". |
| 2. Non-Anthropic frontier judge on factual P3 with a retest | **Not done.** Limitations l. 457-459. |
| 3. Leaderboard sensitivity as a figure | **Partly**, via the hollow markers. No flip rate, no noise floor (M1). |
| 4. Main-text density | **Regressed** (M5). |
| 5. Human labels | **Not done**; the model audit is not independent of one labeling (M6). |

### Numbers spot-checked (56 checks)

| # | Quoted (location) | Source | Result |
|---|---|---|---|
| 1 | Abstract length | `main.tex` l. 46-52, word count | 241 words |
| 2 | 197 predictions: 129/11/17/17/23 (l. 200-202) | Appendix B l. 802-806: 129+11+17+17+18+2+3 | match |
| 3 | Audit agreement 91% (l. 185) | `r22a_label_audit.json` `pooled.agree_any_format` 0.9107 | match |
| 4 | Confirms 86%, predicted 90% (l. 186) | `pooled.any_correct_confirmed` 0.8624; registration P-R22A2 falsified | match |
| 5 | Qwen2.5-14B reading 95% (l. 188) | `pooled.agree_qwen14b` 0.9472 | match; not independent (M6) |
| 6 | "most of the rest list several numbers or commit to no answer" | `disagreements`: 6 lists + 5 NONE of 13 | match |
| 7 | App. G "6 are subset-sum or Goldbach" | `disagreements` any_format 0 / reader 1: subset-34, goldbach-k8-3, subset-k2-4, subset-k2-11 ×2, subset-k1-2 | match |
| 8 | Credits 7.4% of rule rejections (App. G) | `pooled.any_wrong_called_correct` 0.0739 | match |
| 9 | P2 arithmetic 0.17-0.27 any-format (Table 1; l. 256) | Table 27: −0.27, −0.24, −0.23, −0.17, −0.19, −0.25 | match |
| 10 | Model-read 0.16-0.25 | Table 27: −0.25, −0.21, −0.21, −0.16, −0.16, −0.22 | match |
| 11 | Boxed 0.07-0.14 | Table 27: −0.10, −0.08, −0.09, −0.07, −0.14, −0.12 | match |
| 12 | MACE 0.06-0.16 | Table 2 / Table 45: −0.06, −0.08, −0.153, −0.1645 | match (Polish 6 rounding) |
| 13 | Table 1 Consequence "7-40" (draw 1) | `r21a_leaderboard_opus` claude-opus-5 −7.1; `r20c_leaderboard` claude-haiku −39.6 | match |
| 14 | "10-33 with a second draw" | `r22b_redraw_opus` claude-opus `draw2_minus_list` −0.0956; `r22b_redraw_sonnet` claude-haiku −0.3289 | match |
| 15 | P3 "4-83%" | Opus 5 arithmetic (10+3)/(211+113) = 4.0% (`r20a_opus_retest`); `r21a_mace_acceptance` Qwen2.5-7B\|target3 0.833 | match |
| 16 | "at most 0.4% of those that match" | `r20d` repl\|Qwen2.5-7B match 0.0043 | match |
| 17 | "2 of 843, against 117" | `r20a` nonmatch n 81+150+87+201+211+113 = 843; referenced ≤3 15+13+13+63+10+3 = 117; retest 0+2 | match |
| 18 | Section 6 "between 19% and 83%" | `r20a_sonnet_retest` mace 0.1852; `r21a_mace_acceptance` 0.833 | match |
| 19 | "none of those that match it do" | match referenced_le3 0/38, 0/102; `r21a` match 0.0 (266), 0.0 (434) | match |
| 20 | "2 of the 282 ... against 78" | Sonnet 0/81, 15; Opus 2/201, 63 | match |
| 21 | Fig. 3b caption: 45%, 64% below 7; Qwen2.5-7B 10% below 5 | `r22c` mace\|Sonnet 5 [0,7] match 0.45 (20); mace\|Opus 5 0.6429 (14); mace\|Qwen2.5-7B [0,5] 0.1041 (394) | match |
| 22 | "rejected only in the lowest bins" (caption) | mace\|phi-4 [0,5] match 0.0738 omitted; Qwen2.5-7B [5,7] 0.0124 | approximately; incomplete (M4.3) |
| 23 | Top bins: Sonnet 19%, Opus 31%, phi-4 46%, Qwen ≥83%; no match rejected | `r22c` [10,10] 0.1852, 0.3134; [9.8,10] 0.4552, min Qwen 0.833; all top-bin match 0.0 | match |
| 24 | "falls as phi-4 grows surer" | 0.886, 0.692, 0.501, 0.458, 0.339, 0.455 | match (non-monotone tail) |
| 25 | Sonnet and Opus "from their middle to their top bins" | Sonnet 0.641 → 0.277 → 0.185; Opus 0.75 (n 12) → 0.313 ([9,10] bin n 5 dropped) | match |
| 26 | "Verification explains part of the effect" (unscoped) | Qwen2.5-7B differ − match: 88 (lowest) vs 83 (top) | **overgeneralized** (M4.4) |
| 27 | "On arithmetic, phi-4 and Opus 5 fall to 5% or less" | repl\|phi-4 0.0482; **kpool\|phi-4 0.1533 (646)**; repl\|Opus 0.0474; kpool\|Opus 0.0265 | **mismatch** (M3) |
| 28 | Fig. 3 title "confidence ... reduce this" | Qwen2.5-7B gap flat | **overgeneralized** (M2) |
| 29 | Pooled shortfall 22/16/20 (l. 369) | −22.3 / −15.6 / −20.1 | match |
| 30 | Blind within 3 points per model (Sonnet, Opus) | `r20c` blind_minus_list −1.3/−2.0/−2.7/−0.7; `r21a_opus` −0.7/+1.4/+0.7/0.0 | match |
| 31 | Haiku 4.5 blind −9 | `r21a_leaderboard_haiku` pooled blind_minus_list −0.0923 | match |
| 32 | "25 points ahead" | `haiku_minus_llama.answer_list` 0.255 | match |
| 33 | −0.7, −7.4 | `r22d` Sonnet 5 reference −0.0067; Haiku 4.5 −0.0738 | match; "level" imprecise (M1.4) |
| 34 | +6.7, +3.4 | `r22b_redraw_{sonnet,haiku}` `ref_draw2` 0.0671, 0.0336 | match |
| 35 | "all four intervals include zero" | [−10.7, +8.7], [−18.1, +2.7], [−3.4, +16.1], [−6.0, +12.8] | match |
| 36 | "Opus 5 keeps most of the lead under both draws" | 141 q: +17.0 of +24.1; 136 q: list +23.5 (0.2353), draw 2 +25.7 | **imprecise** (keeps all under draw 2) |
| 37 | Pooled shortfall moves "at most 3 points" | `pooled.draw2_minus_draw1` +0.0101 / −0.0184 / +0.0302 | match |
| 38 | "single models by up to 8" | `r22b_redraw_haiku` claude-haiku `draw2_minus_draw1` +0.0805; Table 49 prints +8.1 [−1.4, +17.4] | match; all 12 per-model intervals in Table 49 include zero |
| 39 | Stop matching lose 25-38 pp | `losers_draw2_minus_draw1` −0.3819 / −0.2714 / −0.25 | match |
| 40 | Start matching gain 23-35 pp | `gainers_draw2_minus_draw1` +0.3506 / +0.2317 / +0.2931 | match |
| 41 | "can reorder the models" (abstract) | Reviewer paired bootstrap of the gap change: Sonnet +7.4 [−3.4, +18.1]; Haiku +10.7 [0.0, +21.5]; Opus +9.6 [+0.7, +19.1] | **not supported** (M1) |
| 42 | "All 18 predictions ... confirmed" | `registration_round21.md` l. 76-80 (9) + `registration_round22.md` l. 81-83 (9) | match |
| 43 | Table 48 all cells | `registration_round22.md` outcome table; `r22b` pooled | match |
| 44 | Table 49 all 36 cells | `r22b_redraw_*` generators | match |
| 45 | Table 50 all cells | `r22d` + `r22b` `haiku_minus_llama` | match |
| 46 | Max rule within 2 pooled; 5 for one model (l. 411-412) | `r20g` pooled −0.0101; `r21a_maxrule_opus` +0.0053; `_haiku` −0.0168; claude-haiku −5.4 | match |
| 47 | Max rule within 0.03 AUROC | Table 2 −0.03 (Qwen2.5-14B); Table 45 −0.023, −0.027 | match |
| 48 | Max-rule cost 6.7 pp, 0.15 AUROC | Table 16 bottom: −6.7 [−11.4, −1.9]; −0.15 [−0.19, −0.12] | match |
| 49 | Full-credit sentence 36 → 18 pp, → 8 pp | Table 45: +35.6 → +18.1; +36.3 → +8.1 | match |
| 50 | Thinking 2.85 → 0.32; 1.98 → 0.12 | Appendix L; Table 13 | match |
| 51 | Fig. 3c +36/+15, +44/+22, +42/+18 | Table 42 / Appendix K: 35.6/14.9; 44.3/21.6; 41.6/17.8 | match |
| 52 | Qwen2.5-7B 28% vs 0.4% (l. 255) | Table 23: 0.4% → 28.0% | match |
| 53 | App. K "at most 0.4% from a blind 9 up" | max match share over bins ≥ 9 = 0.0043 | match |
| 54 | App. K "gemma-2-9b barely falls" | kpool\|gemma-2-9b 0.889 → 0.598 → 0.543-0.629 | **mismatch** (Polish 5) |
| 55 | Fig. 3 minimum print font | `fig3_acceptance.pdf` 377.16 pt → 397.5 pt (×1.054): 7.0 → 7.4 pt | ≥ 7 pt |
| 56 | Fig. 2 "n/a" print font | `fontsize=6.0`, 376.7 pt → 397.5 pt (×1.055): 6.3 pt | **below 7 pt** (Polish 8) |

**Registration marks.**
- **Consistent with the registrations and ledger:**
  - Setup audit sentence: unmarked (R22-A registered; the Qwen comparison is a registered "reported without a prediction" readout).
  - Section 6 binned sentences: † (`r22c` is not in any registration).
  - Section 6, 19%-83%: † (the range includes post hoc Sonnet 5 and open-judge shares; the "at least one value" rule applies).
  - Section 7 two-draw ranking: † (draw-1 paired intervals post hoc; draw-2 paired intervals a registered R22-B readout; the rule applies).
  - Table 1 Consequence row: unmarked (P-R20C3 / P-R21A3 per-model predictions; draw-2 per-model accuracy a registered readout).
  - Figure 3 caption: "(b)" post hoc and "(c)" pre-specified, the latter matching ledger rows "Thinking judge on factual questions" and "Sonnet 5 with adaptive thinking through the API".
  - Figure 4 caption: "Pre-specified, except Sonnet 5's max rule".
  - Table 48 and 49: PRE. Table 50 caption: split correctly.
- **One inconsistency (minor).** The Figure 2 caption calls Qwen2.5-7B's exact-scorer values "a post hoc rescoring", while Appendix E calls the rescoring pre-specified (Polish 7).

---

## 5. Figure-by-figure and table-by-table critique

### Main text

**Figure 1 (p. 1).**
- **At the bar.**
  - A concrete task, one fixed reply scored 10.0 / 2.9 / 9.3, and "The text never changed".
  - A pool-level panel with the answer-key zero line and matches-neither bars.
  - Fonts about 8 pt; the example selection rule is disclosed.
- **Minor.** Panel c's y-label "change in score" lacks "(points out of 10)", which only the caption carries.

**Table 1 (p. 3).**
- **At the bar.** Predictions, what each rules out, marks, verdicts, and failed predictions named in the caption.
- **This round's changes are correct.** The model-read range and "10-33 with a second draw" were added and verified.
- **Fix.**
  - The Consequence row names two graders but claims three (Polish 2).
  - The P3 retest needs scope (Polish 3).
- **Missing.** Nothing about the reference draw's per-answer effect. The abstract's draw claim should come from this table, and this table has the right (interval-backed) version to offer: "credit for answers whose match changes moves by 23-38 pp".

**Figure 2 (p. 5).**
- **Strengths.** One row list for both panels, the positive-control block against the several-answers block, and a title that matches the data. "Clearly lowers selection only for Qwen2.5-7B" holds: phi-4's k-pool interval reaches 0.0.
- **Remaining.**
  - Ticks touch the triangles.
  - The 6.3-pt "n/a" labels.
  - Registration wording (Polish 7-8).

**Figure 3 (p. 6).**
- **Panel a** remains the paper's P3 figure and is at the bar: the threshold is defined, open against filled circles, retest crosses.
- **Panel b** is improved: filled series, two hues, direct labels, integer positions and a grey floor. It is still not decodable at print size:
  - two binnings on one axis;
  - about 18 markers within x ∈ [9, 10];
  - unidentified grey series;
  - a 1.3-in panel.
- **Panel c** is clear.
- **Title** contradicts the abstract (M2).
- **Caption** is 217 words (M5).
- **Two stories.** The float still tells P3 and a moderator. Given the page budget I would accept this if the title were scoped and panel b widened.

**Figure 4 (p. 7).**
- **Strengths.**
  - Three panels in one grammar and the referenced condition shaded.
  - 95% intervals at "judge, reference" and a dotted max-rule connector.
  - Hollow markers for the second draw, all 12 verified.
  - The Haiku 4.5 line in heavy black visibly collapsing to Llama level.
  - About 7.6 pt minimum font.
  - The title ("every grader scores the models below their answer lists; blind, Sonnet 5 and Opus 5 do not") holds under both draws: every `draw2_minus_list` is negative.
- **Problems.**
  - Intervals exist only for draw 1, so the figure invites reading the hollow-square-over-hollow-circle reversal as real (M1).
  - The Opus panel's hollow Sonnet triangle is hidden, and that panel's 141 vs 136 question populations are mixed (Polish 9).

**Table 2 (p. 8).**
- **Strengths.** One message; the registered protocol beside the post hoc rule; "Reveal − ref." with its own bold rule; 0.00 fixed. Values are consistent with Tables 16 and 45 to rounding.
- **Problems.**
  - The caption runs to 179 words.
  - The Reference column (exact scorer) and the Reveal − ref. column (original scorer) cannot be added: Qwen2.5-14B shows −0.17 against −0.13. The caption says so, but a footnote mark on the column would help.

### Appendix (brief)

- **Table 4 ledger (pp. 16-19).** Current and accurate. The R22 rows match `registration_round22.md`: 2 confirmed and 1 falsified; 9 of 9 confirmed; the amendment disclosed.
- **Appendix G (p. 28).** The account is accurate and the 6 correction was made. Add the shared-prompt caveat (M6) and name the 2 unaccounted disagreements (Polish 13).
- **Tables 43-47 (pp. 39-41).** Accurate. Page 41 is half whitespace.
- **Tables 48-50 (p. 42).** Accurate against `r22b` and `r22d` (every cell checked). This is the most interesting new evidence. Adding a paired between-draw gap change with its interval to Table 50 would settle M1 on stored data.
- **Tables 51-52 (p. 43).** Accurate and legible. The paragraph above them has three wording errors (Polish 5).
- **Legibility and whitespace.** Unchanged since round 21 (Polish 14-15).

---

## 6. What is at the bar (leave alone)

- **Title.** A claim, memorable and accurate.
- **Opening paragraph and Figure 1.** "The text never changed; only the correct answer the judge was shown did."
- **The three readings, Equation 1 and the separation logic.** It says why P2 needs P2′, why P3 separates the readings, and that the model is not fitted.
- **The swap design** with its matches-neither control, and the MT-Bench-template replication.
- **The registered same-interface retest** (0 of 318; 2 of 525), the backbone of the P3 verdict.
- **The benchmark design.**
  - Answers held fixed across three graders.
  - A second draw registered before any call, with a rule excluding containment.
  - Thresholds 5 and 10 reported.
  - Self-grading disclosed.
  - Opus 5's question loss disclosed in both the caption and Limitations.
- **The label audit.** It carries a falsified prediction reported in the main text and an amendment disclosed after an API failure.
- **The P2 Verdict and the max-rule paragraph.** Precise.
- **Section 6's binned sentences** (l. 314-317). Correctly scoped, once the unscoped follow-on sentence is fixed (M4).
- **Limitations.** Specific and prominent.
- **Page limit.** The main text ends on p. 9.

---

## 7. What would move the score

### To a secure 8 (rewrites and one re-plot; about 1 day, no API spend)

1. **M1** (1 hour). Rewrite the abstract, intro, Section 7 and Conclusion draw sentences as given. Add the paired between-draw gap change (with intervals) to Table 50 from stored scores.
2. **M2 and M3** (30 minutes). Figure 3 title; the Section 6 arithmetic clause.
3. **M4** (3 hours). Re-plot Figure 3b with categorical bins or two small multiples, labeled grey series and at least 1.8 in of width. Rewrite caption (b) and the "Verification explains part" sentence.
4. **M5** (half a day). Section 7 and Section 6 paragraphs to about 10 numbers each; Figure 3 caption to about 130 words; Table 2 caption to about 100; abstract to about 200 words.
5. **M6** (30 minutes). Setup audit sentence and Limitations.
6. **Polish 1-5, 7-9.**

### To 9 (about 1 week, under USD 60)

1. **A referenced noise floor for the draw effect** (new data; about 1.8k calls, under USD 10; register first). Re-grade every answer with the *first* reference for all three graders. Report:
   - same-draw against between-draw changes in per-model accuracy and pairwise gaps;
   - flip rates.

   This either earns "the draw reorders models" or retires it cleanly. Either way, it gives the paper a second consequence with a proper control.
2. **A non-Anthropic grader on the benchmark** (new data; about 1.8k calls per grader for blind plus two draws, under USD 20). This removes "one provider" from the headline consequence.
3. **A non-Anthropic frontier judge on factual P3 with a same-interface retest** (new data; about 2-3k calls, under USD 30). Open since round 20. The Verdict could then read "noise-controlled on factual questions for judges from two providers".
4. **Density** (rewrite; overlaps M5). No main-text paragraph above about 8 numbers. Figure captions under 150 words.

### To 10, best-paper territory (weeks; new data)

1. **A second natural multi-answer benchmark with human-verified answer sets**, repeating the three-grader, two-draw design. Candidates: the NQ-open items the paper's own audit flags, or a constructive task with an executable checker.
2. **A direct manipulation of verification.** Set v_c by design (for example, a blind call given the full answer list or a lookup tool). Show the differing-minus-matching rejection gap against v_c: flat under agreement, falling to zero under verification failure. Figure 3b is the observational version.
3. **A prospective registered test of the recommendation** (max rule; full-credit sentence plus max rule) on a fresh k-pool seed and held-out MACE questions.
4. **Human labels for 200 unboxed replies**, which would settle which labeling Table 1 should quote. The model audit cannot, because its reader shares a prompt with one labeling.

**If the M-list and "to 9" items 1-3 were done,** the paper would have:
- one question, one clean manipulation, and a separating prediction noise-controlled across providers;
- a benchmark consequence replicated across providers and reference draws, with a registered noise floor for the draw effect;
- a measured partial remedy;
- a main text a reviewer absorbs in ten minutes.
