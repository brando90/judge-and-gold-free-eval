# Round 24 Area Chair review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

**Materials.**
- **PDF.** `round24_main.pdf`, 50 pages (byte-identical to `papers/D-iclr/main.pdf`).
  - Main text pp. 1-9; the Conclusion ends at l. 478 and the AI-use statement starts at l. 480.
  - Statements pp. 9-10, references pp. 10-12, appendix pp. 13-50.
  - I read every page as a rendered image, and made 300-dpi crops of Figure 2, Figure 3, Figure 4 (including a zoom on the Opus 5 panel) and appendix Figure 9.
- **Sources checked.**
  - `main.tex` and `appendix.tex`, with a word diff against the round-23 commit (`84ae0f6` → `ae5f363`).
  - `tables/r23_regrade.tex` and `tables/protocol_exact.tex`.
  - `scripts/make_figures.py`: Figure 3 (ll. 355-433), Figure 2 (ll. 786-830), Figure 4 (ll. 840-882) and the Figure 9 block.
  - `papers/analysis/` JSON files:
    - `r23a_regrade_{sonnet,opus,haiku}.json`;
    - `r22b_redraw_{sonnet,opus,haiku}.json`, `r22c_acceptance_bins.json`, `r22d_ranking_intervals.json`;
    - `r21a_mace_acceptance.json`, `r20d_matched_acceptance.json`, `r20a_{sonnet,opus}_retest.json`;
    - `r16c_protocols_exact.json` and `r19a_opus_results.json`.
  - `registration_round23.md` (all of it), `registration_round19.md` l. 69, and the ledger (Appendix B, Table 4).
- **Line numbers** are PDF margin numbers.
- **Independence.** I scored the paper before opening `round23_review.md`, and used that review only for the audit in Section 4.
- **Writes.** Nothing in the project was modified other than this file.

---

## 1. Summary and ease of extraction

**Question.** When a question has several correct answers, does a reference-guided LLM judge treat the reference as an answer key? The paper sets two alternatives against that reading:
- **Verification failure.** The reference is the only evidence available to a judge that cannot recognize other correct answers.
- **Agreement.** The judge rewards matching the one answer it is shown, even when it can recognize the others.

**Claims as a reader extracts them.**
1. **P1, the swap.** Moving the reference between two correct answers moves byte-identical text by 2.7-5.4 points out of 10 (three judges, 120 constructed tasks). Text that matches neither reference does not move.
2. **P2 and P2′, grading.**
   - *Several correct answers.* Grading AUROC for correct answers that differ from the reference falls by 0.06-0.16 for four judges on MACE and by 0.17-0.27 for four open judges on arithmetic.
   - *One correct answer.* The reference raises best-of-64 accuracy on MATH-500 by 29-31 pp.
   - *New in the Verdict:* on MACE, selection did not fall (+2.0 and +6.1 pp, intervals including zero; the registered loss was not confirmed).
3. **P3, not only verification failure.**
   - Of correct factual answers a judge accepts blind, 19%-83% of those that differ from the reference drop to 3 or below once it is shown. None of those that match do.
   - A second same-interface blind call drops 2 of 282.
   - Binned by blind score, rejection falls for three of four judges but stays at 19%-46% in their top bins. The binned figure has moved to the appendix (Figure 9).
4. **Moderators.** Thinking nearly removes the swap on arithmetic but only halves the factual rise in false rejections. A full-credit sentence halves the harm or more without restoring grading.
5. **Consequence.**
   - On 149 MACE questions, all three Claude graders shown a reference put every model below its answer-list accuracy (22, 16 and 20 points pooled). Blind, Sonnet 5 and Opus 5 stay within 3 points.
   - A second reference draw leaves the pooled shortfall unchanged but moves credit for answers whose match changes by 23-38 pp.
   - *New this round:* a registered same-reference regrade (R23-A, 9/9 confirmed) moves that credit by at most about 3 pp. The paper now declines any ranking claim.
6. **Safeguard.** The max rule keeps grading within 0.03 AUROC of blind and pooled benchmark accuracy within 2 points of the lists. It costs up to 6.7 pp when the answer is unique.
7. **Registration.** 206 predictions: 138 confirmed, 11 not confirmed, 17 falsified, 17 split, 23 other.

**2-minute pass** (title, abstract, Figure 1, Table 1). Fast and correct:
- the reference moves unchanged correct text;
- the effect survives the judge's own acceptance;
- it lowers benchmark accuracy for frontier graders.

The ranking overclaim is gone. However:
- The abstract grew again, to about 254 words (241 in round 23).
- Its benchmark clause is missing a word: "leaves this shortfall but moves credit".
- Neither the abstract nor Table 1 mentions the one new control that makes the draw effect credible (M2).

**10-minute pass** (adds Figures 2-4 and Table 2). Figure 3 is now a two-panel figure with a title that agrees with the abstract. That is a clear gain in cognitive load. The reader also gets:
- the positive control;
- the acceptance lollipop;
- the factual thinking bars;
- the benchmark slope chart with second-draw markers;
- the safeguards table.

**Where a careful reader now trips.** Once again, all of these are in text written this round:
1. **Section 7's new regrade sentence.** "Such gaps move about as much when the same reference is re-graded as when it is redrawn (by 10.7 points either way under Haiku 4.5)" is true for one of three graders.
   - For Sonnet 5 and Opus 5 the regrade leaves the gap flat (0.0, −0.7) while the redraw moves it (+7.4, +8.9). The Opus 5 redraw interval excludes zero.
   - Two registered readouts that bear on the sentence are not reported: pairwise order flips, and per-model same-draw changes (M1).
2. **The Section 7 benchmark paragraph** is still the densest in the paper: about 261 words and about 17 numbers. A full-width table splits its conclusion mid-clause across pp. 7-8 (M3).
3. **The Section 6 arithmetic "remainder is small" sentence** picks the pool where it is small. Figure 3a, directly above it, prints phi-4 at 8% (M4).

**Overall.** This round did the right thing with the round-23 criticism. Rather than only softening "the draw can reorder the models", the authors registered and ran the noise-floor experiment. It confirmed all nine predictions and cleanly separated a real draw effect (credit for answers whose match changes) from an unresolved one (model rankings). Figure 3 lost a panel and 86 caption words, and its title was corrected. The label-audit caveat is now honest.

What remains is precision in the newly written sentences, one omitted pair of registered readouts, main-text density on p. 7, and unchanged appendix housekeeping.

---

## 2. Score and confidence

**Score: 8 / 10** (accept, good paper; a secure 8 with a visible path to 9). **Confidence: 4 / 5.**

**Single biggest reason.** The central claim is established the way a best-paper committee wants:
- a byte-identical manipulation with a matches-neither control;
- a positive control;
- a separating prediction (P3) with a same-interface noise control;
- a benchmark consequence that now has a registered noise floor (R23-A), so the paper can say which part of the reference-draw effect is real.

Round 23's headline overclaim was retired by experiment, not just by rewording.

**Why not 9.**
1. **The new regrade sentence generalizes one grader's noise to all three, and omits registered readouts that bear on it** (M1). The pattern of each round's new sentences being less precise than the old ones has shrunk, but it is not gone.
2. **The consequence is still narrow.** It has:
   - one benchmark;
   - one answer per model;
   - graders from one provider;
   - a factual P3 noise control only for Anthropic judges;
   - no human labels.

   None of round 23's "to 9" items 2-3 (a non-Anthropic grader; a non-Anthropic factual P3 retest) was attempted.
3. **Density.** The Figure 3 caption was fixed (216 → 130 words). But:
   - the abstract grew (241 → about 254 words);
   - the Section 7 benchmark paragraph still carries about 17 numbers;
   - the Table 2 caption is still 178 words.

   The "Mirage" bar is one message per paragraph.
4. **Appendix housekeeping is unchanged for the fourth round.** About 5-pt tables, half-empty pages, and a Table 2 → Table 16 cross-reference that points to different numbers (M5).

**What is needed.** M1-M5 are rewrites plus one table edit, about half a day with no new data. Moving to 9 needs a non-Anthropic grader on the benchmark (under USD 20).

---

## 3. Ranked issues

### MUST FIX

#### M1. The Section 7 regrade sentence overgeneralizes from Haiku 4.5 to all graders, and the paper omits two registered R23-A readouts that bear on it
**New data: none.**

**Location.**
- Section 7, p. 7 l. 377-378 → p. 8 l. 403: "Such gaps move about as much when the same reference is re-graded as when it is redrawn (by 10.7 points either way under Haiku 4.5), so we do not read them as a draw effect."
- Table 51 (p. 43 l. 2276-2287), which omits the readouts.

**Problem.**
1. **The sentence is true for one grader of three.** Changes in the Haiku 4.5 − Llama-3.1-8B gap (`haiku_minus_llama`):

   | Grader | Same-reference regrade (`same_draw_change`) | Second draw (`between_draw_change`) |
   |---|---|---|
   | Sonnet 5 | 0.0 [−6.7, +7.4] | +7.4 [−3.4, +18.1] |
   | Opus 5 | −0.7 [−6.7, +5.9] | **+8.9 [+0.7, +17.8]** |
   | Haiku 4.5 | +10.7 [+2.7, +19.5] | +10.7 [0.0, +21.5] |

   - For Sonnet 5 and Opus 5 the regrade leaves the gap flat and the redraw moves it by 7-9 points. For Opus 5 that is the only gap-change interval in the study that excludes zero.
   - "Such gaps move about as much" is therefore a statement about Haiku 4.5 alone.
   - The appendix paragraph (l. 2271-2275) states this correctly. The main text does not.
   - The conservative conclusion (no ranking claim) is defensible. The reason given for it is not.
2. **"Either way" is ambiguous.** It reads as "±10.7". The intended meaning is "+10.7 under both the regrade and the redraw".
3. **Two registered readouts are not reported anywhere in the paper.**
   - `registration_round23.md` l. 28-31 lists "per model and pooled, the same-draw change" and "the number of the six model pairs whose order differs ... under the regrade and under the second draw". Table 51 reports only pooled changes, and no text reports flips (`grep -i flip` finds nothing relevant).
   - Pairwise flips (`pairwise_order_flips_of_6`): regrade **0, 0, 2**; second draw **1, 1, 1** (Sonnet 5, Opus 5, Haiku 4.5). This is exactly the evidence the sentence is about.
   - Per-model same-draw changes are within about 4 points except **Haiku 4.5 graded by itself: +6.7 [+0.7, +12.8]** (`r23a_regrade_haiku.json` `generators.claude-haiku-4-5-20251001.same_draw_change` 0.0671 [0.0067, 0.1275]).
   - The registration's own Outcome section (l. 65-66) states this; the paper drops it.
4. **The intervals do not include call-to-call variation.**
   - A same-reference regrade moved one model's accuracy, and one grader's gap, with intervals excluding zero.
   - So the question-bootstrap intervals in Figure 4 (vertical lines), Table 49 and Table 50 resample questions but not grader calls, and they understate uncertainty for per-model comparisons.
   - This does not threaten the headline: pooled shortfalls of 16-22 points against at most 1.9 points of regrade movement. It belongs in Limitations.

**Fix.**
- **Section 7, replace the sentence** (and the preceding "...while Opus 5 keeps Haiku 4.5 ahead" can stay):
  > "Whether the draw also reorders models is unresolved: under Sonnet 5 and Opus 5 a same-reference regrade leaves the Haiku 4.5 − Llama-3.1-8B gap within 1 point while the redraw moves it by 7 to 9, but under Haiku 4.5 the regrade moves it as much as the redraw (10.7 points each), so we make no ranking claim (Appendix K)."
- **Appendix K regrade paragraph, append:**
  > "Of the six model pairs, 0, 0, and 2 change order under the regrade and 1, 1, and 1 under the second draw (Sonnet 5, Opus 5, Haiku 4.5). Per-model referenced accuracy moves by at most about 4 points between two calls with the same reference, except Haiku 4.5 grading its own answers (+6.7 [+0.7, +12.8])."
- **Table 51.** Add a "Pairwise flips (of 6): regrade; draw 2" column, and either a per-model same-draw block or a pointer to the registration outcome.
- **Limitations, "Tasks" bullet, add:**
  > "Benchmark intervals resample questions, not grader calls; re-grading with the same reference moved one model's referenced accuracy by up to 6.7 points."

#### M2. The paper's new noise floor is missing from the abstract, Table 1 and the Conclusion; the abstract regressed in length and grammar
**New data: none.**

**Location.**
- Abstract l. 024-027: "a second reference drawn from the same lists leaves this shortfall but moves credit for the answers whose match changes by 23 to 38 points."
- Table 1 Consequence row (l. 136-139).
- Conclusion l. 472-474.

**Problem.**
1. **The benchmark clause has no baseline.**
   - "Moves credit ... by 23 to 38 points" is exactly the comparison round 23 asked the paper to earn a noise floor for, and R23-A earned it: the same answers move by at most about 3 pp on a same-reference regrade (`stop_credited_original` vs `stop_credited_regrade` 1.000/0.993, 0.993/0.993, 0.993/0.986; `start_credited_*` 0.644/0.655, 0.776/0.745, 0.684/0.690).
   - A reader of the abstract, Table 1 or the Conclusion cannot tell that the 23-38 has a control. It is the paper's cleanest benchmark-scale P1 result, and it now sits only in the middle of a Section 7 paragraph.
2. **"Leaves this shortfall but moves credit" is missing a word** ("unchanged"). As written, "leaves this shortfall" can also be read as "leaves (i.e., abandons) this shortfall".
3. **Length.**
   - The abstract went from 241 to about 254 words (pdftotext count), against the round-22 and round-23 target of about 200.
   - The "(1) ... (2) ... (3)" sentence is still about 75 words.

**Fix.**
- **Abstract** (222 words, down from about 254; every number verified; drop the "We test ten judges and" clause to reach about 215):
  > "LLM judges often grade with a reference answer, on the premise that it acts as an answer key: a correct response should score the same whichever correct answer is shown. We test this premise on questions with several correct answers, separating three readings of a reference: an answer key, the only evidence for a judge that cannot verify, or an answer the judge rewards for matching. Swapping the reference between two correct answers moves the score of identical text by 3 to 5 points out of 10. Correct answers that differ from the reference are rejected far more often, including ones the judge accepts without a reference, so the effect is not only a failure to verify. Thinking nearly removes it on arithmetic; on factual questions, thinking or an instruction that any correct answer counts only reduces it. On up to 149 factual benchmark questions, Claude Sonnet 5 and Opus 5 shown a reference score four models 7 to 40 points below their answer-list accuracy, and within 3 points blind. Redrawing the reference leaves this shortfall unchanged but moves credit for answers whose match changes by 23 to 38 points, against at most 3 when the same reference is re-graded. We test ten judges and report all 206 registered predictions. On such questions, a low reference-guided score is weak evidence of error."
- **Table 1 Consequence row, Observed:** append
  > "; a second draw moves credit for answers whose match changes by 23-38 points, a same-reference regrade by at most 3"
- **Table 1 Consequence row, Verdict:**
  > "Holds for three graders and two draws; draw effect exceeds a regrade"
- **Conclusion l. 473-474:**
  > "...and a second reference draw moved credit for individual answers by 23 to 38 points, against at most 3 on a same-reference regrade, without reducing that shortfall."

  Split the sentence first (Polish 3).

#### M3. The Section 7 "Benchmark scores" paragraph is still the densest in the main text, and its conclusion is split by Table 2
**New data: none.**

**Location.**
- p. 7 l. 366-378 → p. 8 l. 403-404: about 261 words, about 17 numbers, 7 sentences.
- Table 2 caption (l. 378-387): 178 words.

**Problem.**
1. **Round 23 M5 asked for about 10 numbers.** The paragraph lost the old ranking sentence but gained the regrade clause, so its density is essentially unchanged.
2. **The one message is hard to find.** The reference lowers every model, and the draw decides which answers get credit, not rankings. That message is spread over sentences 2, 4, 5 and 6.
3. **A page break splits the conclusion.** A full-width Table 2 at the top of p. 8 breaks it mid-clause ("...so we do | [Table 2] | not read them as a draw effect"). A skimmer who stops at the bottom of p. 7 reads "Such gaps move about as much ... so we do" and never sees the qualification.
4. **The Table 2 caption** carries a per-cell registration list (about 60 words) that belongs in Appendix F.

**Fix.**
- **Replacement paragraph** (about 12 numbers):
  > "We asked Llama-3.1-8B-Instruct, Claude Haiku 4.5, Sonnet 5, and Opus 5 for one answer to each of 149 MACE questions with several correct answers, and graded every answer with Sonnet 5, Opus 5, and Haiku 4.5, blind and with a reference drawn from each answer list (Figure 4). With the reference, every grader puts every model below its answer-list accuracy (16 to 22 points pooled); blind, Sonnet 5 and Opus 5 stay within 3 points, so the shortfall comes from the reference (Haiku 4.5 under-counts by 9 even blind). The draw decides which correct answers get credit: a second reference drawn from the same lists (hollow markers) leaves each pooled shortfall within 3 points, but answers that stop matching lose 25 to 38 pp of credit and answers that start matching gain 23 to 35 pp, while re-grading with the first reference moves the same answers by at most 3 pp. [M1 sentence.] All 27 predictions registered for these graders, the second draw, and the regrade were confirmed."
- **Layout.** Place Table 2 with `[b]` on p. 8, or move it after "What helps", so the benchmark paragraph ends on the page where it starts.
- **Table 2 caption.** Keep the column definitions, "Bold ...", and one registration sentence ("Registration status of each cell is in Appendix F"). Target about 100 words.

#### M4. Section 6's arithmetic "remainder is small" sentence picks its pool, and the lollipop directly above shows a different number
**New data: none.**

**Location.** Section 6, p. 6 l. 315-320:
- "...stays far above zero (19% to 46%) among the answers each judge is surest of..."
- "On the arithmetic replication pool the remainder is small for phi-4 and Opus 5 (5% or less)."

**Problem.**
1. **The k-pool numbers were dropped.**
   - The round-23 fix text gave both pools. This version keeps only the pool where the claim holds.
   - phi-4's top bin on the k-pool is **15.3%** (`r22c_acceptance_bins.json` `kpool|phi-4` [9.8, 10] `nonmatch` 0.1533, n = 646). Its matched-threshold share there is 15.4% (`r20d_matched_acceptance.json` `kpool|phi-4` 0.1541).
   - Opus 5 is small on both pools (4.7% and 2.7%).
   - The sentence is the main text's only statement about the size of P3's remainder on arithmetic, and it sits next to the Verdict "P3 holds for all six judges".
2. **Figure 3a prints phi-4 arithmetic at 8%** (pooled: (85 + 110)/(1,839 + 714) = 7.6%). A reader who reads "5% or less" and looks up at the figure sees 8%.
3. **The phi-4 figure and text disagree.** Figure 3a shows phi-4 factual at **42%** (threshold 9.6: `r21a_mace_acceptance.json` `phi-4|target3` 0.4194). One sentence later the text says the top-bin range reaches **46%** (bin ≥ 9.8: 0.4552). Nothing tells the reader these are different populations.
4. **Missing mark.** phi-4's replication share is post hoc, so the "5% or less" sentence needs a † under the paper's own rule ("a mark on a range applies to at least one value in it").

**Fix.**
> "Binned by blind score,† rejection of differing answers falls as phi-4, Sonnet 5, and Opus 5 grow surer but stays far above zero in each judge's top bin (19% to 46%), where no matching answer is rejected, while Qwen2.5-7B rejects at least 83% at every blind score (Appendix K). For three of the four judges verification explains part of the effect; the remainder, among answers the judge already accepts, is what agreement predicts. On arithmetic the remainder is small for Opus 5 (5% or less of its surest differing answers on both pools) and for phi-4 on the replication pool (5%), but not on the k-pool (15%).†"

#### M5. Cross-references in the appendix point to different numbers from the ones they claim to hold
**New data: none.**

**Location and problem.**
1. **Table 16's bottom block (p. 26, caption l. 1354-1356)** says it gives "the values quoted in Table 2".
   - Its MACE row is labeled "(accuracy: natural mix; AUROC: k>1)" and prints reference +9.0 [+2.3, +15.8] and max rule +9.8 for Qwen2.5-7B, and +11.3 / +11.3 for phi-4.
   - Table 2 (l. 393-394) quotes MACE accuracy under "Several correct answers" as reference **+2.0**, max rule **+4.0** (Qwen2.5-7B) and **+6.1 / +6.1** (phi-4). Those are the k>1 values (`r16c_protocols_exact.json` `mace/*/accuracy_kgt1/reference_minus_blind` 0.0202 and 0.0606; `max_rule_minus_blind` 0.0404 and 0.0606).
   - Table 2 is right. Its cited source table is the wrong subset, and the k>1 max-rule interval (+4.0 [+1.0, +8.1]) appears nowhere in the paper.
   - Section 5's new Verdict quotes the same +2.0 and +6.1, so this is now a main-text dependency.
2. **Opus 5's pooled second-draw change has two values in adjacent tables.** Table 48 (l. 2235) prints −1.8 (136 questions); Table 51 (l. 2284) prints −2.4 (135 questions, `r23a_regrade_opus.json` `pooled.between_draw_change` −0.0241). Neither caption flags the population difference.
3. **The same regrade change is printed three ways.** Table 51 prints −1.8, the appendix text says "at most 1.9 points" (l. 2268), and `registration_round23.md` l. 59 says −1.9. The JSON is −0.0185.

**Fix.**
- **Table 16 bottom.** Add "MACE, k>1" accuracy rows (reference +2.0 [−5.1, +9.1] / +6.1 [−1.0, +13.1]; max rule +4.0 [+1.0, +8.1] / +6.1 [+2.0, +11.1]; max − reference +2.0 [−4.0, +8.1] / 0.0 [−5.1, +5.1]) and keep the natural-mix row labeled as such. Alternatively, change the caption to "the grading values quoted in Table 2; its MACE accuracy values are the k>1 rows of `r16c`".
- **Table 51 caption.** Add "Opus 5: the 135 questions with all four calls complete, so its draw-2 change differs from Table 48's (136)".
- **Rounding.** Print −1.9 in Table 51, or write "at most 1.8" in the text, and state the rounding rule once.

### POLISH

1. **Section 5 Verdict, l. 300-302, hard to parse.** "0.06 to 0.08 on the k-pool for Sonnet 5 and Opus 5, and at most 0.04 on the replication pool (0.02, interval including zero, for Opus 5) and for GPT-4.1." Replace with:
   > "Sonnet 5 and Opus 5 fall by 0.06 to 0.08 on the k-pool and by 0.04 and 0.02 on the replication pool (Opus 5's interval includes zero), and GPT-4.1 by at most 0.04 on either pool."

   Sources: Table 45: −0.080, −0.057, −0.037, −0.015 [−0.038, +0.009]; Table 27: GPT-4.1 −0.04, −0.01.
2. **Section 3, l. 189-190.** "which, the prompt being shared, validates neither labeling" should become "; because the two readers share a prompt, this agreement validates neither labeling".
3. **Conclusion, l. 470-474.** The second sentence is about 75 words with four coordinated clauses. Split it after "without a reference."
4. **Figure 4, Opus 5 panel.** At 300 dpi, Sonnet 5's hollow triangle (76.5) is still mostly hidden under Haiku 4.5's hollow square (77.2); the x offsets are 0.29 and 0.38 (`make_figures.py` l. 868). Use 0.15 spacing, or nudge vertically. Also merge the caption's "(Opus 5: solid 141 questions, hollow 136)" with the following sentence ("Opus 5's panel uses 141 questions ..."), which repeats it.
5. **Figure 2 grey boxed-only ticks** still touch the GPT-4.1 triangles in the replication and k-pool rows (tick at `yv - 0.34`, l. 804). Offset by 0.45, or draw a small grey × beside the marker. The "n/a" labels are fixed (7.0 → about 7.4 pt at print).
6. **Figure 3.**
   - Panel (b) sits in the top-right 40% of the float with blank space beneath it; enlarge it to the height of panel (a) or move the legend up.
   - The Opus 5 arithmetic filled circle (4%) nearly covers its open circle.
   - The caption's "Arithmetic rows pool the replication and k-pool data" is not true for Qwen2.5-14B and gemma-2-9b, which are k-pool only. Add "(k-pool only for Qwen2.5-14B and gemma-2-9b)".
7. **Table 51 cells.** Triplets such as "100, 99, 62" are hard to scan. Use "100 → 99 → 62", or three sub-columns, and add the flips column (M1).
8. **Appendix K binned paragraph (l. 2292-2299).**
   - "Matching answers are rejected at more than 2% only in each judge's lowest bin ... except in bins of fewer than 15 answers" has one more exception: gemma-2-9b k-pool 5-7, **2.9% (1 of 35)** (`kpool|gemma-2-9b` [5,7] `match` 0.0286). Write "at more than 3%".
   - "Qwen2.5-14B is not monotone (15%, then 39%, then 23%)" skips the 9-9.6 bin (28%). Write "15%, 28%, 39%, 23%".
9. **Section 6, l. 315.** "Falls as phi-4 ... grow surer": phi-4 rises from 34% to 46% in its top two bins. Add "not monotonically for phi-4".
10. **Section 5 Verdict, l. 304-305.** "k-pool losses concentrate where no correct candidate matches the reference" rests on post hoc Table 12 rows and needs a †.
11. **Table 45 rounding, fourth round unchanged.**
    - Opus 5 MACE AUROC prints −0.165 (JSON −0.1645; text "0.16").
    - Opus 5 replication false-rejection rise prints +3.6 (`r19a_opus_results.json` FR 0.0365; `registration_round19.md` l. 69 "+3.7").
12. **Appendix legibility, unchanged since round 21.** These tables are about 5 pt at print: Table 13 (p. 24), Table 15 (p. 25), Table 16 bottom (p. 26, now a main-text source), Tables 18 and 20 (p. 27), Table 24 (p. 29), Tables 62-63 (p. 50).
13. **Whitespace, unchanged and now worse.**
    - p. 25 (gaps around Tables 14-15);
    - p. 30 (top half);
    - p. 31 (top quarter);
    - p. 41 (between Tables 46 and 47);
    - **new** p. 44 (Tables 52-53 float in about 45% blank);
    - pp. 49-50 (bottom halves).

    The appendix grew from 49 to 50 pages. `\FloatBarrier` per section plus `[!ht]` would recover two to three pages.
14. **Figure 9.** All four "differs" series are one blue, told apart only by marker shape, and in panel (a) the two grey "matches" lines overlap from 7% to 10%. Direct end labels ("Qwen2.5-7B", "phi-4") would remove the legend lookup.
15. **Section 7, l. 372.** "Leaves each grader's pooled shortfall within 3 points": Haiku 4.5 is +3.02 (`r22b_redraw_haiku.json` `pooled.draw2_minus_draw1` 0.0302). "By about 3 points at most" is exact.

---

## 4. Audit of round-23 items

### MUST FIX (M1-M6)

| Item | Status | Evidence in this version |
|---|---|---|
| **M1** "Draw can reorder the models" without interval support or noise floor | **Fixed, with a new overgeneralization** | Abstract l. 026-027 now: "a second reference drawn from the same lists leaves this shortfall but moves credit ... by 23 to 38 points" (missing "unchanged"; M2). Intro l. 096-097: "and which answer is drawn decides which correct answers get credit" (the round-23 text, verbatim). Conclusion l. 473-474: "a second reference draw moved credit ... without reducing that shortfall" (verbatim). Section 7: "no longer separate the two under either draw (gaps from −7.4 to +6.7 points, all intervals including zero), while Opus 5 keeps Haiku 4.5 ahead" (verified: `r22d` −0.0067, −0.0738; `r22b` `ref_draw2` 0.0671, 0.0336; Opus +17.0 [8.5, 25.5], +25.7 [16.2, 35.3]). **The optional experiment was run and registered first**: R23-A, 1,788 calls, 9/9 confirmed, all cells of Table 51 verified against `r23a_regrade_*.json`. New: the main-text regrade sentence generalizes Haiku 4.5's result to all graders, and the flip and per-model readouts are omitted (M1). |
| **M2** Figure 3 title contradicts abstract and Table 1 | **Fixed** | "The reference rejects correct answers the judge already accepts, and on factual questions thinking does not remove this." It is scoped to factual questions, drops the false "confidence reduces" clause, and agrees with the abstract ("thinking nearly removes the effect on arithmetic") and Table 1. |
| **M3** Arithmetic clause false for phi-4 on the k-pool | **Fixed in truth, not in coverage** | Now "On the arithmetic replication pool the remainder is small for phi-4 and Opus 5 (5% or less)": true (`repl\|phi-4` 0.0482, `repl\|Opus 5` 0.0474). The k-pool 15% given in the round-23 fix text was dropped, and Figure 3a's pooled 8% sits above it (M4). |
| **M4** Figure 3b undecodable; "verification explains part" unscoped | **Fixed** | The panel moved to appendix Figure 9, which has: a categorical blind-score-bin axis with printed edges; two small multiples (open: <5 ... ≥9.8; API: ≤6, 7-8, 9, 10); grey dashed matching series identified in the legend; about 7.5-pt minimum font (7.2 pt in a 379.2-pt PDF placed at 397.5 pt). Every plotted point was checked against `r22c` MACE bins. Main text: "For three of the four judges verification explains part of the effect" (l. 318). The caption still does not list the matching-floor values, but the legend now identifies the grey series, so the numbers are recoverable from Table 52-53. |
| **M5** Densest paragraphs; captions; abstract | **Partly** | Figure 3 caption 216 → **130** words (target met). Section 6 acceptance paragraph 227 → 217 words and about 17 → about 11 numbers (met). Section 7 benchmark paragraph about 288 → **261** words, still about 17 numbers (not met; M3). Table 2 caption **178** words (unchanged). Abstract 241 → **about 254** words (regressed; M2). |
| **M6** Label-audit comparison not independent; Limitations incomplete | **Fixed** | Setup l. 188-190: "A Qwen2.5-14B reading with the same extraction prompt agrees with Opus 5 on 95%, which, the prompt being shared, validates neither labeling" (substance right, prose awkward; Polish 2). Limitations l. 444-446: "that reading rejects 14% of the unboxed replies the rule credits, mostly lists of several numbers or replies that commit to no answer" (1 − 0.862 = 13.8%, verified). |

### Important POLISH items from round 23

| Item | Status | Evidence |
|---|---|---|
| 1 Abstract "up to 149" | Fixed | l. 024. |
| 2 Table 1 Consequence names two graders | Fixed | Now "all three graders score every model below the answer lists; Sonnet 5 and Opus 5 by 7-40 points (10-33 with a second draw)". |
| 3 Table 1 P3 retest scope | Fixed | "(Sonnet 5 and Opus 5, three pools): 2 of 843, against 117". |
| 4 Dangling dagger l. 417 | Fixed | "(paired)† for Qwen2.5-7B". |
| 5 Appendix K wording (levels off; gemma; match exceptions) | **Mostly** | "stays above zero"; "gemma-2-9b falls from 89% to between 54% and 63%" (verified 0.889 → 0.543-0.629); exception clause added, but gemma k-pool 5-7 at 2.9% (n = 35) still violates it (Polish 8). |
| 6 Rounding (Table 45) | **Not fixed** | −0.165, +3.6 (Polish 11). |
| 7 Figure 2 registration wording | Fixed | "whose rescoring was pre-specified but whose MACE accuracy readouts were not" now agrees with Appendix E. |
| 8 Figure 2 legibility | **Partly** | n/a 6.0 → 7.0 pt; ticks still touch the GPT-4.1 triangles (Polish 5). |
| 9 Figure 4 overlap and populations | **Partly** | Caption now "(Opus 5: solid 141 questions, hollow 136)"; the hidden hollow triangle remains (Polish 4). |
| 10 Figure 3b y-label double space | Moot | Panel removed; the Figure 9 label is clean. |
| 11 Move "Selection" to Section 5 Verdict | Fixed | l. 302-305; numbers verified (Table 57: +2.0 [−5.1, +9.1], +6.1 [−1.0, +13.1]). |
| 12 Limitations: same lists | Fixed | "both reference draws come from the same answer lists". |
| 13 Appendix G: name the other 2 | Fixed | "and 2 are single integers the constraint check rejects". |
| 14 Appendix legibility | **Not fixed** | Polish 12. |
| 15 Whitespace | **Not fixed; worse** | New half-blank p. 44 (Polish 13). |

### "To 9" items from round 23

| Item | Status |
|---|---|
| 1. Referenced noise floor for the draw effect | **Done**, and done well: registered before any call, three predictions per grader, flips pre-listed as a readout. The flips readout is not reported (M1). |
| 2. Non-Anthropic grader on the benchmark | **Not done.** Limitations: "three models from one provider". |
| 3. Non-Anthropic frontier judge on factual P3 with a retest | **Not done.** Limitations: "only for the two API judges". |
| 4. Density | **Partly** (Figure 3 and Section 6 met; Section 7, abstract and Table 2 caption not). |

### Numbers spot-checked (48 checks; new or rewritten text first)

| # | Quoted (location) | Source | Result |
|---|---|---|---|
| 1 | "re-grading with the first reference moves that credit by about 3 pp at most" (§7 l. 373-374) | `r23a_*` `stop_credited_original/regrade`: 1.000/0.993, 0.993/0.993, 0.993/0.986; `start_*`: 0.644/0.655, 0.776/0.745, 0.684/0.690 → max 3.1 | match |
| 2 | "Such gaps move about as much when ... re-graded as when ... redrawn" (§7 l. 377-378) | `haiku_minus_llama` same vs between: Sonnet 0.0 vs +0.0738; Opus −0.0074 vs +0.0889 [0.0072, 0.1778]; Haiku 0.1074 vs 0.1074 | **true for 1 of 3 graders** (M1) |
| 3 | "by 10.7 points either way under Haiku 4.5" | `r23a_regrade_haiku` 0.1074 [0.0268, 0.1946]; 0.1074 [0.0, 0.2148] | value match; "either way" ambiguous |
| 4 | "All 27 predictions ... confirmed" (l. 403-404) | R21-A 9 (ledger "Two more benchmark graders") + R22-B 9 + R23-A 9 (`registration_round23.md` l. 62-64) | match |
| 5 | Stop matching lose 25-38 pp; start matching gain 23-35 pp | `r22b` `losers_draw2_minus_draw1` −0.3819/−0.2714/−0.25; `gainers_*` 0.3506/0.2317/0.2931 | match |
| 6 | Abstract "23 to 38 points" | same | match |
| 7 | "gaps from −7.4 to +6.7, all intervals including zero" | `r22d` −0.0067 [−0.1074, 0.0874], −0.0738 [−0.1812, 0.0268]; `r22b` `ref_draw2` 0.0671 [−0.0336, 0.1611], 0.0336 [−0.0604, 0.1275] | match |
| 8 | "Opus 5 keeps Haiku 4.5 ahead" | `r22d` Opus 0.1702 [0.0851, 0.2553]; `r22b_redraw_opus` `ref_draw2` 0.2574 [0.1618, 0.3529] | match |
| 9 | "leaves each grader's pooled shortfall within 3 points" | `draw2_minus_draw1` +0.0101, (Opus, 136 q) −0.018, +0.0302 | match to rounding (Polish 15) |
| 10 | Pooled shortfall 22/16/20 | −22.3/−15.6/−20.1 (Table 47) | match |
| 11 | Haiku 4.5 blind −9 | Table 47 −9.2 | match |
| 12 | Table 51 Sonnet 5 row: +0.5 [−1.5, +2.5]; +1.0 [−3.9, +5.9]; 100, 99, 62; 64, 66, 99; +0.0 [−6.7, +7.4]; +7.4 [−3.4, +18.1] | `r23a_regrade_sonnet` pooled 0.005 [−0.0151, 0.0252]; 0.0101 [−0.0386, 0.0587]; 1.0/0.9931/0.6181; 0.6437/0.6552/0.9943; gap 0.0 / 0.0738 | match |
| 13 | Table 51 Opus 5 row: −1.8 [−4.3, +0.7]; −2.4 [−7.0, +2.2]; 99, 99, 72; 78, 75, 99; −0.7 [−6.7, +5.9]; +8.9 [+0.7, +17.8] | `r23a_regrade_opus` −0.0185 [−0.0426, 0.0074]; −0.0241 [−0.0704, 0.0222]; 0.9929/0.9929/0.7214; 0.7764/0.7453/0.9938; −0.0074; 0.0889 | match (−1.85 printed as −1.8; M5) |
| 14 | Table 51 Haiku 4.5 row: −0.3 [−3.5, +2.9]; +3.0 [−1.3, +7.4]; 99, 99, 74; 68, 69, 98; +10.7 [+2.7, +19.5]; +10.7 [+0.0, +21.5] | `r23a_regrade_haiku` −0.0034; 0.0302; 0.9931/0.9861/0.7431; 0.6839/0.6897/0.977; 0.1074 ×2 | match |
| 15 | App. K "moves by at most 1.9 points between two calls" | JSON max \|pooled same_draw\| 0.0185; Table 51 prints 1.8 | **inconsistent rounding** (M5) |
| 16 | App. K "24 to 38 points beyond the regrade" | `stop_regrade_minus_draw2` 0.375/0.2714/0.2431; `start_draw2_minus_regrade` 0.3391/0.2484/0.2874 | match |
| 17 | App. K "Opus 5's regrade left 4 referenced replies unscored (135 questions)" | `registration_round23.md` l. 53-54; `r23a_regrade_opus` `questions` 135 | match |
| 18 | Per-model same-draw changes (not reported) | Haiku 4.5 self +0.0671 [0.0067, 0.1275]; all others \|·\| ≤ 0.0403 | **omitted registered readout** (M1) |
| 19 | Pairwise flips (not reported) | `pairwise_order_flips_of_6` regrade 0/0/2; draw2 1/1/1 | **omitted registered readout** (M1) |
| 20 | Ledger row "Same-reference regrade" 3/3/3 confirmed | `registration_round23.md` l. 62-64 | match |
| 21 | 206 = 138 + 11 + 17 + 17 + 23 (abstract, §3, App. B) | 197 + 9; 129 + 9; App. B 138 + 11 + 17 + 17 + 18 + 2 + 3 | match |
| 22 | §5 Verdict "+2.0 and +6.1 pp, intervals including zero" | Table 57 +2.0 [−5.1, +9.1], +6.1 [−1.0, +13.1]; `r16c` `accuracy_kgt1` 0.0202 [−0.0505, 0.0909], 0.0606 [−0.0101, 0.1313] | match |
| 23 | §5 Verdict "0.06 to 0.08 on the k-pool for Sonnet 5 and Opus 5" | Table 45 −0.080, −0.057 | match |
| 24 | "at most 0.04 on the replication pool (0.02 ... Opus 5)" | Table 45 −0.037; −0.015 [−0.038, +0.009] | match |
| 25 | "and for GPT-4.1" (≤ 0.04) | Table 27 any-format −0.04, −0.01 | match |
| 26 | Table 2 MACE accuracy +2.0/+4.0, +6.1/+6.1 | `r16c` `accuracy_kgt1` ref 0.0202/0.0606, max 0.0404/0.0606 | match; **Table 16 source block prints natural mix** (M5) |
| 27 | Table 2 bold rule on MACE max-rule accuracy (not bold) | `max_rule_minus_reference` 0.0202 [−0.0404, 0.0808]; 0.0 [−0.0505, 0.0505] | match |
| 28 | Fig. 3a factual: 19%, 31%, 83%, 42% | `r20a_sonnet_retest` mace 0.1852; `r20a_opus_retest` 0.3134; `r21a` Qwen2.5-7B 0.833, phi-4 0.4194 | match |
| 29 | Fig. 3a arithmetic: 11%, 4%, 21%, 8%, 24%, 57% | Sonnet (13 + 13)/(150 + 87) = 11.0%; Opus (10 + 3)/(211 + 113) = 4.0%; Qwen2.5-7B (336 + 175)/(1747 + 699) = 20.9%; phi-4 (85 + 110)/(1839 + 714) = 7.6%; `r20d` Qwen2.5-14B 0.2392; gemma 0.5654 | match |
| 30 | Fig. 3a crosses (retest) | Sonnet 0/81, 0/237; Opus 2/201, 0/324 | match |
| 31 | Fig. 3b +36/+15, +44/+22, +42/+18 | Table 42 / 55 / 13: 35.6/14.9, 44.3/21.6, 41.6/17.8 | match |
| 32 | §6 "between 19% and 83%"; "none of those that match" | as #28; match shares 0/38, 0/102, 0/266, 0/434 | match |
| 33 | §6 "2 of the 282 ... against 78" | 81 + 201; 0 + 2; 15 + 63 | match |
| 34 | §6 "(19% to 46%)" top bins; "no matching answer is rejected" | `r22c` mace Sonnet [10,10] 0.1852, Opus 0.3134, phi-4 [9.8,10] 0.4552; all top-bin `match` 0.0 | match (46 vs Fig. 3a 42 unexplained; M4) |
| 35 | §6 "Qwen2.5-7B rejects at least 83% at every blind score" | mace\|Qwen2.5-7B 0.981, 0.924, 0.837, 0.837, 0.897, 0.833 | match |
| 36 | §6 "For three of the four judges verification explains part" | phi-4 0.886 → 0.455; Sonnet 0.886 → 0.185; Opus 0.92 → 0.313; Qwen2.5-7B gap flat | match |
| 37 | §6 "arithmetic replication pool ... phi-4 and Opus 5 (5% or less)" | `repl\|phi-4` [9.8,10] 0.0482; `repl\|Opus 5` [10,10] 0.0474; **`kpool\|phi-4` 0.1533 omitted** | true, selectively scoped (M4) |
| 38 | Table 1 P3 "4-83%", "at most 0.4%", "2 of 843, against 117" | Opus arithmetic 4.0%; `r20d` repl\|Qwen2.5-7B match 0.0043; 81 + 150 + 87 + 201 + 211 + 113; 15 + 13 + 13 + 63 + 10 + 3 | match |
| 39 | Table 1 Consequence "7-40 ... (10-33 with a second draw)" | `r21a_leaderboard_opus` claude-opus −7.1; `r20c` claude-haiku −39.6; `r22b_redraw_opus` claude-opus −9.56; `r22b_redraw_sonnet` claude-haiku −32.9 | match |
| 40 | App. K "falls from 89% to between 54% and 63%" (gemma) | 0.889; 0.598, 0.543, 0.553, 0.629, 0.560 | match |
| 41 | App. K "more than 2% only in each judge's lowest bin ... except bins < 15" | `kpool\|gemma-2-9b` [5,7] match 0.0286, n 35 | **one exception** (Polish 8) |
| 42 | App. K "at most 0.4% from a blind 9 up" | max over bins ≥ 9: `repl\|Qwen2.5-7B` [9.8,10] 0.0043 | match |
| 43 | App. K Qwen2.5-14B "15%, then 39%, then 23%" | 0.147, 0.276, 0.390, 0.234 | match; skips a bin (Polish 8) |
| 44 | Figure 9 all plotted points | `r22c` mace bins (open and API, n ≥ 10 differing; Opus [9,10] n = 5 dropped) | match |
| 45 | Setup "91%", "86%", "90%", "95%"; Limitations "14%" | `r22a` 0.9107, 0.8624, P-R22A2, 0.9472; 1 − 0.8624 | match |
| 46 | Table 48 Opus change −1.8 vs Table 51 Opus draw 2 −2.4 | `r22b_redraw_opus` (136 q) vs `r23a_regrade_opus` (135 q) | **unflagged population difference** (M5) |
| 47 | Print fonts: Fig. 3 (min 7.0 pt, 375.7-pt PDF → 397.5 pt), Fig. 4 (7.2, 376.7 pt), Fig. 2 n/a (7.0, 377.3 pt), Fig. 9 (7.2, 379.2 pt) | ×1.058, ×1.055, ×1.054, ×1.048 → 7.4, 7.6, 7.4, 7.5 pt | all ≥ 7 pt |
| 48 | Main text ends by p. 9 | Conclusion ends l. 478, p. 9 | match |

### Registration marks

- **Consistent with the registrations and ledger:**
  - Section 7 regrade clauses: unmarked, as registered R23-A readouts. That matches the paper's convention for registered readouts reported without a prediction.
  - The ranking-gap sentence: † (the first-draw paired intervals are post hoc).
  - Table 51: PRE. Figure 9, Tables 52-53 and the Appendix K binned paragraph: †.
  - Section 5 Verdict "+2.0 and +6.1": unmarked (MACE end-to-end registration; Table 57 PRE).
  - Figure 3 caption: "Pre-specified: the second blind calls, Opus 5's shares in (a), and (b)". This matches the ledger rows "Opus 5 on the Sonnet 5 subsamples", "Thinking judge on factual questions" and "Sonnet 5 with adaptive thinking through the API".
  - Figure 2 caption: now consistent with Appendix E.
- **Two missing marks (minor).**
  - Section 6 "5% or less": phi-4's replication share is post hoc (M4).
  - Section 5 Verdict "k-pool losses concentrate where ...": rests on post hoc Table 12 (Polish 10).

---

## 5. Figure-by-figure and table-by-table critique

### Main text

**Figure 1 (p. 1).** Unchanged and at the bar. It gives a concrete task, one fixed reply scored 10.0 / 2.9 / 9.3, "The text never changed", and pool-level bars with a matches-neither control. One carried-over nit: panel c's y-label "change in score" lacks "(points out of 10)".

**Table 1 (p. 3).**
- **At the bar.** One row per prediction, with what it rules out, what was observed, a verdict, and the failed predictions named in the caption.
- **Fixed this round.**
  - The Consequence row names all three graders.
  - The P3 retest is scoped.
- **Missing.**
  - The Consequence row still lacks the one claim with a registered control: the draw moves credit by 23-38 against at most 3 on a regrade (M2).
  - Nothing tells the reader that the ranking question is open.

**Figure 2 (p. 5).**
- **Strengths.** One row list for both panels, the positive control against the several-answers block, and a title that matches the data. Qwen2.5-7B's k-pool loss is the only selection interval clearly below zero; phi-4's k-pool interval reaches 0.0.
- **Fixed.** The registration wording and the n/a font.
- **Remaining.** Boxed-only ticks on the GPT-4.1 triangles (Polish 5).

**Figure 3 (p. 6).** Much improved.
- **Two panels, two clear messages.**
  - (a) is the P3 test: open against filled circles, the matching floor at zero, retest crosses.
  - (b) is the factual thinking moderator.
- **Title.** Now agrees with the abstract and Table 1.
- **Caption.** 130 words, with registration consolidated into one sentence.
- **Remaining.**
  - Panel (b) floats in the top right with unused space below.
  - phi-4 arithmetic at 8% sits directly above text that says "5% or less" (M4).
  - The Opus 5 arithmetic markers overlap.
  - The caption over-states pooling for Qwen2.5-14B and gemma-2-9b (Polish 6).

At print size this figure reads in about 20 seconds, which is the bar.

**Figure 4 (p. 7).**
- **Strengths.** Three panels in one grammar, the referenced condition shaded, 95% intervals, a dotted max-rule connector, and hollow second-draw markers (all 12 verified). The heavy black Haiku 4.5 line visibly collapses to Llama level. The title holds under both draws.
- **Remaining.**
  - A hidden hollow triangle in the Opus 5 panel.
  - A redundant caption sentence.
  - Vertical intervals that, as the regrade shows, do not include call-to-call variation (M1.4, Polish 4).
- **A missed opportunity.** A small inset or marginal tick showing the regrade next to each hollow marker would turn the figure into the paper's second decisive figure: a draw effect against a same-draw effect.

**Table 2 (p. 8).**
- **Strengths.** One message; the registered protocol beside the post hoc rule; bold rules that are correct against `r16c` for MACE accuracy.
- **Problems.**
  - The caption is 178 words.
  - It splits the Section 7 conclusion across the page break (M3).
  - Its cited source (Table 16 bottom) prints different MACE accuracy values (M5).

### Appendix (new or changed parts)

- **Table 4 ledger (pp. 16-19).** The new "Same-reference regrade" row is accurate. Totals updated to 206.
- **Tables 48-50 (p. 42).** Unchanged and accurate. Table 48's Opus 5 −1.8 (136 questions) against Table 51's −2.4 (135) needs a note (M5).
- **Regrade paragraph and Table 51 (pp. 42-43).**
  - The paragraph is precise and correctly scoped by grader. It is the text the main-text sentence should have copied.
  - The table is accurate in every cell (checks 12-14), but it omits the registered flips and per-model readouts (M1). Its triplet cells are hard to scan (Polish 7).
- **Appendix K binned paragraph and Figure 9 (p. 43).**
  - Figure 9 is a good figure: a categorical axis, printed bin edges, separate panels for the two binnings, and a legend-identified matching floor.
  - The paragraph has one exception to its 2% rule and one skipped bin (Polish 8).
- **Tables 52-53 (p. 44).** Accurate and legible, but the page is about 45% blank.
- **Appendix G (p. 28).** The 13 disagreements are now fully accounted for (6 + 5 + 2).
- **Legibility and whitespace.** Unchanged since round 21 (Polish 12-13).

---

## 6. What is at the bar (leave alone)

- **Title.** A claim, memorable and accurate.
- **Opening paragraph and Figure 1.** "The text never changed; only the correct answer the judge was shown did."
- **The three readings, Equation 1 and the separation logic.** The paper says why P2 needs P2′, why P3 separates the readings, and that the model is not fitted.
- **The swap design** with its matches-neither control, plus the MT-Bench-template replication.
- **The registered same-interface retest** (0 of 318; 2 of 525), the backbone of the P3 verdict.
- **Figure 3 as rebuilt.** Two panels, a scoped title, a 130-word caption.
- **Section 6 "Answers the judge accepts without a reference"**, apart from the last sentence (M4). The binned result is now one scoped sentence with the figure in the appendix. That is the right allocation.
- **The R23-A design.** It was registered before any call, with a disclosed context section that quotes a reviewer's unregistered bootstrap. Its predictions are directional per grader, and it pre-lists the ranking readouts. This is how a paper should answer a reviewer's overclaim charge.
- **The Appendix K regrade paragraph.** Correct and scoped by grader.
- **Intro and Conclusion draw sentences.** "Which answer is drawn decides which correct answers get credit" is exactly the claim the data support.
- **The label-audit caveat** in Setup and Limitations.
- **The Section 5 Verdict's selection sentence**, including the unconfirmed registered loss.
- **Limitations.** Specific and prominent; now includes the same-lists caveat.
- **Page limit.** The main text ends on p. 9.

---

## 7. What would move the score

### To a secure 8, then a strong 8 (rewrites and one table edit; about half a day, no API spend)

Listed in priority order.

1. **M1** (1.5 hours).
   - Replace the Section 7 regrade sentence.
   - Add flips and per-model same-draw changes to Table 51 and the Appendix K paragraph, all from stored `r23a_regrade_*.json`.
   - Add the question-bootstrap sentence to Limitations.
2. **M2** (1 hour).
   - Adopt the 222-word replacement abstract, with the regrade comparison.
   - Add the draw-versus-regrade clause to Table 1 and the Conclusion.
3. **M3** (1.5 hours).
   - Adopt the Section 7 paragraph at about 12 numbers.
   - Re-place Table 2 so the paragraph is not split.
   - Cut the Table 2 caption to about 100 words.
4. **M4** (20 minutes). The Section 6 sentences with both pools and top-bin wording.
5. **M5** (1 hour).
   - Add Table 16 k>1 MACE rows.
   - Fix the Table 51 caption population note and rounding.
6. **Polish 1-9.** Main-text phrasing, Figure 2/3/4 overlaps, Appendix K wording.

### To 9 (about 1 week, under USD 60; new data)

1. **A non-Anthropic grader on the benchmark** (about 1.8k calls for blind, both draws and a regrade; under USD 20; register first).
   - This removes "one provider" from the headline consequence.
   - It also tests whether call-to-call variation like Haiku 4.5's is a weak-grader or a provider property.
2. **A non-Anthropic frontier judge on factual P3 with a same-interface retest** (about 2-3k calls, under USD 30). This has been open since round 20. The Verdict could then read "noise-controlled on factual questions for judges from two providers".
3. **Make Figure 4 decisive** (rewrite plus re-plot; half a day). Show the regrade next to each second-draw marker, or add a small panel: credit for answers that stop or start matching under first call, regrade and redraw. That turns the benchmark section into a figure a skimmer can read in 10 seconds: the draw moves credit and a regrade does not.
4. **Density** (overlaps M3). No main-text paragraph above about 10 numbers; every caption under 150 words; the abstract at about 200 words.

### To 10, best-paper territory (weeks; new data)

1. **A second natural multi-answer benchmark with human-verified answer sets**, repeating the three-grader, two-draw, regrade design. Candidates: NQ-open items flagged by the paper's own audit, or a constructive task with an executable checker.
2. **A direct manipulation of verification.** Set v_c by design, for example with a blind call given the full answer list or a lookup tool. Show that the differing-minus-matching rejection gap is flat under agreement and falls to zero under verification failure. Figure 9 is the observational version.
3. **A prospective registered test of the recommendation** (the max rule, and the full-credit sentence plus the max rule) on a fresh k-pool seed and held-out MACE questions.
4. **Human labels for 200 unboxed replies.** This would settle which labeling Table 1 should quote; the model audit cannot, because its reader shares a prompt with one labeling.

**If M1-M5 and "to 9" items 1-3 were done,** the paper would have:
- one question, one clean manipulation, and a separating prediction noise-controlled across providers;
- a benchmark consequence replicated across providers and reference draws, with a registered noise floor shown in the main figure;
- a measured partial remedy;
- a main text a reviewer absorbs in ten minutes.
