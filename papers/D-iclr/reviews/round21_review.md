# Round 21 Area Chair review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

**Materials.**
- **PDF.** `round21_main.pdf`, 49 pages: main text pp. 1-9, statements p. 10, references pp. 10-13, appendix pp. 14-49. I read every page as a rendered image, with 220-dpi renders of pp. 1, 5, 6 and 7 to judge the figures at print size.
- **Sources checked.** `main.tex`, `appendix.tex`, `tables/r21_graders.tex`, `scripts/make_figures.py` (Figure 3 and 4 source comments), `scripts/make_tables.py`, `papers/analysis/*.json` (r8, r19a/b, r20a-g, r21a, r21c), `registration_round19.md`, `registration_round20.md`, `registration_round21.md`, and the ledger (Table 4).
- **Line numbers.** These are the PDF margin numbers.
- **Previous review.** Read only for the audit in Section 4; the score here is independent.
- **Re-analysis.** I ran one read-only re-analysis in my scratchpad: the open-judge MACE acceptance test binned by blind score (M5). Nothing in the project was modified.

---

## 1. Summary of the claims and how easy they were to extract

**Question.** When a question has several correct answers, does a reference-guided LLM judge treat the reference as an answer key? The paper sets that reading against two others: verification failure (the reference is the judge's only evidence) and agreement (the judge rewards matching the answer shown).

**Claims as extracted.**
1. **P1, the swap.** Moving the reference between two correct answers moves the score of byte-identical text by 2.7-5.4 points out of 10 (Qwen2.5-7B, phi-4, Sonnet 5; 120 constructed tasks). Answers that match neither reference do not move. The pull shrinks when the reference answer is written as an expression and disappears when it is masked.
2. **P2 and P2′, grading.** With several correct answers, correct answers that differ from the reference lose ground against wrong ones:
   - grading AUROC falls 0.06-0.16 for four judges on MACE;
   - it falls 0.17-0.27 for four open judges on arithmetic (0.07-0.14 counting boxed replies only);
   - with one correct answer, the reference raises best-of-64 accuracy by 29-31 pp (MATH-500).
3. **P3, not only verification failure.** Among correct answers the judge accepts blind, those that differ from the reference often drop to 3 or below once it is shown; those that match never do.
   - Factual: 19% (Sonnet 5), 31% (Opus 5), 83% (Qwen2.5-7B), 42% (phi-4).
   - A same-interface second blind call gives 2 of 843.
4. **Moderators.**
   - Thinking takes the arithmetic swap to near zero but only about halves the factual false-rejection rise.
   - A full-credit sentence halves that rise or more, but grading stays below blind.
5. **Consequence.** One answer per model on 149 multi-answer MACE questions, graded by Sonnet 5, Opus 5 and Haiku 4.5.
   - With the reference, the three graders put the four models 7-40 points below answer-list accuracy (pooled 22, 16, 20).
   - Blind, Sonnet 5 and Opus 5 stay within 3 points. Haiku 4.5 under-counts by 9 even blind.
   - Haiku 4.5 (95% on the answer list) falls to 55%, level with or below Llama-3.1-8B.
6. **Safeguard.** Keeping the higher of blind and referenced scores (the max rule) keeps grading within 0.03 AUROC of blind. It costs up to 6.7 pp of accuracy with a unique answer.
7. **Registration.** 185 registered predictions: 118 confirmed, 11 not confirmed, 16 falsified, 17 split, 23 not evaluable, not scored or excluded.

**2-minute takeaway** (title, abstract, Figure 1, Table 1). It is now the right one:
- the reference moves the score of unchanged correct text;
- the effect is not just an inability to verify;
- it changes benchmark numbers for three frontier graders.

Table 1 now has a Consequence row, and its verdicts agree with the sections.
- **What still slows a skimmer:** the abstract, at 262 words.

**10-minute takeaway** (plus Figures 2-4 and Table 2). The reader also gets:
- the one-answer positive control;
- P3 on factual questions for four judges;
- the moderators;
- the benchmark slope chart;
- the safeguard table.

Density has dropped a lot. By my count the heaviest main-text paragraphs now carry 11-15 numbers (Setup "Tasks", Section 6 acceptance, Section 5 "Several correct answers", Section 4), down from 27. Figure 4 carries the benchmark result with little prose.

**Where a careful reader now trips:**
- Section 7 and the Figure 4 title make "every model loses accuracy" and "within 2 points" claims that the Haiku 4.5 panel of Figure 4 visibly contradicts.
- Two captions disagree about which MACE accuracy results were pre-specified.
- Table 2 prints a "Reveal" column whose bold rule refers to a reference value computed with a different scorer from the one printed beside it.

**Overall.** This is now a clean, well-controlled, honest paper. It has one question, a model that says what each reading predicts, and a separating test with a noise control. The consequence is replicated across three graders.

What separates it from the best-paper bar:
- a handful of precision errors, concentrated in Section 7;
- a consequence that rests on one benchmark, one provider's graders and one reference draw;
- a P3 extension to open judges that, looked at more closely, says something more interesting than the single-threshold number reports (M5).

---

## 2. Score and confidence

**Score: 8 / 10** (accept, good paper). **Confidence: 4 / 5.**

**Single biggest reason.** The central claim is now tested the way it should be, and the paper reads like a paper rather than a ledger.
- **Swap.** A byte-identical swap.
- **Positive control.** The one-answer case.
- **Separating test.** P3 with a registered same-interface retest on two frontier judges, extended to two more model families on factual questions.
- **Consequence.** A benchmark result replicated by three graders with 9/9 registered predictions confirmed.

Most round-20 must-fix items were addressed in the text, which I checked line by line (Section 4 of this review).

**Why not 9.**
1. **Section 7 overstates.** Its claims are stated more strongly than Figure 4 shows ("every grader lowers every model's accuracy"; the max rule "within 2 points ... for all three graders"; a registered prediction said to have "held" at a threshold it did not specify).
2. **The consequence is narrow.**
   - All three graders come from one provider.
   - The questions come from two MACE domains.
   - One random reference draw is used per question.
   - The headline inversion (Llama above Haiku) has no uncertainty attached.
3. **Open-judge P3 is thin.** The factual extension to open judges is post hoc, rests on one threshold, and hides a gradient that Equation 1 was built to test.

None of these needs a large experiment. M1-M4 and M6 are rewrites. M5 is a re-analysis of stored scores. M7 has a text-only fix and a cheap optional run.

---

## 3. Ranked issues

### MUST FIX

#### M1. "Every grader lowers every model's accuracy" and the Figure 4 title are contradicted by the Haiku 4.5 panel; the low end of "7 to 40" mixes in a grader that under-counts blind
**New data: none.**

**Location.**
- Section 7 l. 377: "With the reference, every grader lowers every model's accuracy, by 22, 16, and 20 points pooled."
- Figure 4 title l. 341: "Graded with the reference, every model loses accuracy".
- Abstract l. 025-027: "three Claude judges score four models 7 to 40 points below their answer-list accuracy".
- Table 1 Consequence row l. 134-137; Conclusion l. 480-482.

**Problem.**
1. **Relative to blind, the reference raises one cell.** Under Haiku 4.5, Llama-3.1-8B scores 61.7% blind and 62.4% with the reference (`r21a_leaderboard_haiku.json` generators.meta-llama.accuracy_blind 0.6174, accuracy_referenced 0.6242).
   - Figure 4's third panel shows the dashed Llama line rising from "judge, blind" to "judge, reference".
   - A reader who reads the slope chart as blind → reference sees the opposite of the title.
2. **Relative to the answer list, the smallest cell is not a reference effect.**
   - The claim holds only as a point estimate: Haiku→Llama is −6.7 [−13.4, 0.0] (`undercount_referenced_minus_list`).
   - All of that shortfall is already present blind (−7.4 [−14.1, −0.7], `blind_minus_list`).
   - So the "7" at the bottom of the abstract's "7 to 40" range, in its Haiku→Llama instance, is not caused by the reference.
   - The range survives on the two graders that are valid blind baselines: Opus 5 grading its own answers is −7.1 [−11.3, −2.8] with blind at 0.0. But the abstract attributes the range to "three Claude judges".
3. **Haiku's pooled figure is inflated the same way.** Its "20 points pooled" includes the 9.2-point blind under-count. The reference-attributable part is about 11 points.

**Fix.**
- **Section 7 l. 377:**
  > "With the reference, all three graders put every model below its answer-list accuracy (pooled 22, 16 and 20 points). Blind, Sonnet 5 and Opus 5 stay within 3 points for every model, so for them the whole shortfall comes from the reference; Haiku 4.5, a weaker grader, already under-counts by 9 points blind, and the reference adds about 11 more."
- **Figure 4 title:**
  > "Shown the reference, every grader scores the models below their answer lists; blind, Sonnet 5 and Opus 5 do not."
  - Keep the inversion out of the title (see M7).
- **Abstract l. 025-027:**
  > "The effect reaches benchmark scores: on 149 factual questions with several correct answers, Claude Sonnet 5 and Opus 5 as reference-guided graders score four models 7 to 40 points below their answer-list accuracy, and within 3 points when grading blind; a third grader, Haiku 4.5, shows the same shortfall."

#### M2. The max-rule sentence overstates the benchmark result and misstates what was registered
**New data: none.**

**Location.** Section 7 "What helps", l. 418-421: "Keeping the higher ... keeps ... benchmark accuracy within 2 points of the answer lists for all three graders (Figure 4); for Opus 5 and Haiku 4.5 as graders this was a registered prediction, and it held." Appendix K l. 2272 repeats "under the max rule both stay within 2 points".

**Problem.**
1. **"Within 2 points" is pooled only.** Per model under Haiku 4.5:
   - Haiku's own answers: 89.3% against 94.6%, −5.4 [−10.7, 0.0] (`r21a_maxrule_haiku.json` claude-haiku max_minus_list −0.0537);
   - Llama: +2.7.
   - Figure 4's third panel shows the 5-point Haiku gap at "max rule".
   - Under Sonnet 5, Sonnet's own answers are −2.0 (−2.1 by subtraction of the printed 96.6 and 98.7).
2. **The registered prediction was different.** P-R21A4 was "pooled accuracy is within **5** points of answer-list accuracy (point estimate), and its interval lies above that of referenced accuracy minus list" (`registration_round21.md` l. 37-38). "This was a registered prediction, and it held" reads as if the 2-point claim was registered.
3. **A result is missed.** For Haiku 4.5 the max rule does better than blind grading: pooled −1.7 against −9.2 blind. The reference supplies credit for matching answers that Haiku rejects blind (`false_rejection_match_blind` 6.5%-12.1%). This is the one place the max rule beats blind rather than merely restoring it, and it is the practical point for weak graders.

**Fix.**
> "... and pooled benchmark accuracy within 2 points of the answer lists for all three graders (Figure 4; for one model under Haiku 4.5, 5 points). For Opus 5 and Haiku 4.5 we had registered that the pooled max rule would stay within 5 points of the lists and above referenced grading; both held. For Haiku 4.5, which under-counts blind, the max rule was also closer to the lists than blind grading (−1.7 against −9.2 points)."

Update Appendix K l. 2272 to "pooled".

#### M3. Registration labels contradict each other across captions, and one appendix readout disagrees with its registration record
**New data: none.**

**Location and evidence.**

| Where | Statement | Conflict | Fix |
|---|---|---|---|
| Figure 2 caption l. 248-249 | "... Qwen2.5-7B's MACE grading, and phi-4's MACE accuracy were pre-specified" | Table 2 caption l. 386-387 says "Qwen2.5-7B's MACE grading **and accuracy**" were pre-specified and omits phi-4's accuracy. The ledger (Table 4, "MACE end to end", l. 998-1000) registered the k>1 accuracy loss for **both** judges on the original scorer (Table 51: +2.0, +6.1). Table 12 (l. 1219) labels Qwen2.5-7B's exact-scorer +2.0 as post hoc. | Make both captions say: "MACE k>1 accuracy was pre-specified for both judges on the original scorer; Qwen2.5-7B's value here uses the exact scorer, a post hoc rescoring that gives the same +2.0." |
| Table 47 (p. 43) against `registration_round21.md` l. 74 | Haiku 4.5 pooled referenced false rejections "25.2%" | The registration outcome records "25.3%"; JSON `pooled.false_rejection_nonmatch_ref` 0.2525. | Use one rounding rule everywhere; state it once. |
| Section 7 l. 404-405 | "Haiku 4.5, a weaker verifier, under-counts by 9 points even blind" | R21-A lists "Haiku 4.5's blind accuracy against the list" as reported without a prediction. Unmarked is defensible as a registered readout; "a weaker verifier" is an interpretation, not a measurement (no blind AUROC for Haiku 4.5 is reported). | Write "a weaker grader", or report Haiku's blind false rejections (9.1% of differing and 6.5%-12.1% of matching correct answers). |
| Figure 4 caption l. 345 | "the rankings were reported without a prediction" | The ranking sentence in the text (l. 405-407, "level with or below Llama-3.1-8B") is unmarked. Under the paper's convention this is a registered readout, so acceptable, but the reader cannot tell from the text. | Add "(reported without a prediction)" in the text sentence. |

#### M4. Table 2's Reveal column compares against a reference value that is not printed; the "What helps" sentence about it is imprecise
**New data: none.**

**Location.** Table 2 l. 390-401 and caption l. 380-383 ("Reveal ... (original scorer, compared with the original-scorer reference)"); text l. 416-417.

**Problem.**
1. **The bold rule refers to an unprinted value.** The caption says "Bold: differs from the reference column". But the Reveal cells are judged against the original-scorer reference in Table 16, not the exact-scorer reference printed in the Reference column of the same row:
   - k-pool Qwen2.5-14B: printed Reference −0.17; the bold on Reveal −0.01 is judged against −0.13 (Table 16 top);
   - gemma-2-9b: printed −0.19, compared with −0.18;
   - Qwen2.5-7B: printed −0.23, compared with −0.22.

   A reader who applies the stated rule to the printed numbers is applying it to the wrong values. For gemma, "−0.23 bold" next to "−0.19" also reads as "the protocol made grading worse", which Table 16 does not show at that precision.
2. **"Protected selection but not grading for three of four open judges" (l. 416-417) cannot be checked from Table 2.**
   - Table 2 has no Reveal accuracy column.
   - The "three of four" count holds only on the k-pool. On MACE, neither judge's grading moves at all (−0.08 → −0.08; −0.06 → −0.05).

**Fix.**
- Either print the Reveal column as "Reveal − reference (original scorer)" with its own bold rule, or add the original-scorer reference in parentheses.
- Replace l. 416-417 with:
  > "The registered blind-then-reveal protocol recovered most of the selection loss on the k-pool (Appendix F) but left grading below blind for three of four open judges there and for both on MACE."

#### M5. Open-judge factual P3: one post hoc threshold hides the gradient that separates the readings
**New data: none (re-analysis of stored scores, about an hour).**

**Location.** Figure 3a factual rows (Qwen2.5-7B 83%, phi-4 42%); Section 6 l. 323 and l. 347 ("between 19% and 83%"); Verdict l. 368-369 ("on factual questions for four from three developers"); Intro l. 096-098; Table 1 P3 row.

**Problem.**
1. **Equation 1 makes a graded prediction.** Under verification failure λ(v) = λ₀(1−v), so the referenced rejection of differing correct answers should fall toward zero as the judge's own confidence rises. Under agreement it stays flat. A single "accepted" cut-off throws most of that information away.
2. **What the binned re-analysis shows.** I re-ran the logic of `r21a_mace_acceptance.py` (same pool, labels, matching rule and score files), binned by blind expected score. Share of correct answers scored 3 or below with the reference:

   | Blind score | Qwen2.5-7B, differ | Qwen2.5-7B, match | phi-4, differ | phi-4, match |
   |---|---|---|---|---|
   | < 5 | 98.1% (n=838) | 10.4% | 88.6% (n=658) | 7.4% |
   | 5-7 | 92.4% (409) | 1.2% | 69.2% (711) | 0.8% |
   | 7-9 | 83.7% (710) | 0.8% | 50.1% (1578) | 0.4% |
   | 9-9.6 | 83.7% (203) | 0.0% | 45.8% (911) | 0.0% |
   | 9.6-9.8 | 89.7% (126) | 0.0% | 33.9% (239) | 0.0% |
   | ≥ 9.8 | 83.3% (527) | 0.0% | 45.5% (536) | 0.0% |

   - **Qwen2.5-7B** rejects differing correct answers at 83%-98% whatever its blind score. Acceptance barely conditions anything. Its referenced mode is close to a string matcher: it credits 0.5% of differing correct answers overall (`r20e_benchmark_open_judges.json` nonmatching_credited_referenced 0.0053).
   - **phi-4** shows the decline verification failure predicts, from 89% to about 50%, then a plateau at 34%-46% among answers it is most sure of.
   - Read this way, the data support a mixed picture that is more interesting than "83%": agreement dominates for one judge; verification explains part of the effect for the other; and neither falls to zero.
   - This also matches Appendix L l. 2361-2369: swap size falls as blind AUROC rises, "verification therefore reduces the effect but does not remove it".
   - The main text never says this.
3. **Coverage is thinner than "four from three developers" suggests.**
   - Two of the four factual judges rest on a post hoc threshold with no noise control (disclosed in Limitations l. 463-464, not in the Verdict).
   - The two with a noise control are both Anthropic models.

**Fix.**
- **Figure 3a, open-judge factual rows (or a new small panel):** plot the share of differing correct answers scored 3 or below against blind-score bin, with the matching-answer line as the floor. Keep the API rows as they are.
- **Section 6, after l. 347:**
  > "For the open judges the rate barely depends on how sure the judge is blind: Qwen2.5-7B rejects 98% of differing answers it scores below 5 and 83% of those it scores at the top; phi-4 falls from 89% to about 45% and then levels off (Appendix K).† Verification lowers the effect but does not remove it, as agreement predicts."
- **Verdict l. 368-369:**
  > "... and on factual questions for four judges from three developers (two with a same-interface noise control, two at a post hoc threshold)."

#### M6. The P2 verdict still classifies identical magnitudes differently
**New data: none.**

**Location.** Section 5 Verdict l. 312-316; Table 1 P2 verdict l. 120-122.

**Problem.** The Verdict says "For the API judges the falls on the constructed pools are small", then lists four cells (0.04, 0.04, 0.02, 0.01). It omits the two API k-pool falls, which exclude zero and are not small by the paper's own standard:
- Sonnet 5: −0.080 [−0.120, −0.043] (`r8_sonnet_results.json` kpool.lenient.G_nm);
- Opus 5: −0.057 [−0.117, −0.013] (`r19a_opus_results.json`).

Both are as large as phi-4's MACE fall (−0.06), which the same verdict counts as P2 holding. The paragraph above (l. 304) says "at most 0.08", so the Verdict and its own paragraph disagree. Table 1's "small (≤0.04) for API judges on the replication pool and GPT-4.1" is correct.

**Fix, Verdict l. 313-316:**
> "On the constructed pools the API judges fall less: 0.06 to 0.08 on the k-pool for Sonnet 5 and Opus 5, and at most 0.04 on the replication pool (0.02, interval including zero, for Opus 5) and for GPT-4.1."

#### M7. The benchmark inversion is stated without uncertainty and rests on one reference draw
**New data: none for the text fix. Optional run: about 1.8k API calls, under USD 15.**

**Location.** Figure 4 title l. 341-342 ("two of three graders put Llama-3.1-8B level with or above Claude Haiku 4.5"); Section 7 l. 405-407.

**Problem.**
1. **No uncertainty on the inversion.**
   - Under Sonnet 5 the "inversion" is one question: 55.7% against 55.0%.
   - Under Haiku 4.5 it is 62.4% against 55.0%. With 149 questions each accuracy has a standard error of about 4 points, so a 7-point difference is not distinguishable from zero without a paired test, which is not reported.
   - Figure 4 has no intervals at all.
2. **One reference draw.** The references were drawn at random from each answer list once. The paper's own P1 says the score follows the reference, so the benchmark numbers, and especially a ranking decided by one question, depend on that draw. Nothing in the paper measures that dependence.
3. **The Opus 5 panel drops questions selectively.** It removes 8 questions whose referenced calls ran out of tokens while Opus deliberated over differing answers. Appendix K says this "may understate its shortfall"; the Figure 4 caption gives the count but not the direction.

**Fix.**
- **Title:** see M1.
- **Text l. 405-407:**
  > "The damage is uneven across models: Haiku 4.5 falls from 95% to 55% under Sonnet 5 and under itself, level with Llama-3.1-8B under Sonnet 5 (one question apart) and below it under Haiku 4.5 (paired difference [x, y]), reported without a prediction."
  - Compute the paired intervals from the stored score files.
- **Figure 4:** add pooled 95% intervals at "judge, reference", or a caption sentence giving the per-model interval half-width (about 6-8 points).
- **Caption:** add "(dropping these questions may understate Opus 5's shortfall)".
- **Optional, cheap, and the best single addition for the 9.** Redraw the reference from each answer list and re-grade referenced (3 graders × 596 answers). Report how much each model's referenced accuracy and the ranking move between draws. This is P1 at the leaderboard level.

---

### POLISH

1. **Abstract (262 words, up from 254).**
   - "ten judges" still undercounts the judges in the appendix (Mistral-7B, Ministral-8B, Qwen2.5-1.5B and 3B, Llama-3.1-8B); write "ten judges in the main text" or "ten main judges".
   - "the two strongest" is undefined; name Sonnet 5 and Opus 5.
   - Aim for 200 words. A version:
     > "LLM judges often grade with a reference answer, assuming it acts as an answer key: a correct response should score the same whichever correct answer is shown. On questions with several correct answers it does not. We separate three readings of a reference (answer key, the only evidence for a judge that cannot verify, or an answer the judge rewards for matching) and test their predictions on ten judges with 185 registered predictions. Swapping the reference between two correct answers moves the score of identical text by about 3 to 5 points out of 10. Correct answers that differ from the reference are rejected far more often, including ones the same judge accepts without a reference, so the effect is not only a failure to verify. Thinking nearly removes it on arithmetic; on factual questions thinking, or an instruction that any correct answer counts, only reduces it. On 149 factual benchmark questions, Claude Sonnet 5 and Opus 5 shown the reference score four models 7 to 40 points below their answer-list accuracy, and within 3 points blind. Keeping the higher of the blind and referenced scores restores grading at a small cost when the answer is unique."
2. **"Sonnet 5 shows the same pattern" (l. 259).** Appendix J gives Sonnet 5 the bare/words/expression contrast only (+3.06, +3.14, +0.47), not the worked-solution masking. Write "Sonnet 5 shows the same pattern for words and expressions".
3. **"Earlier margin-only tests of this and a second instruction agree" (l. 357-358).** On the synthetic grid the instruction left Qwen2.5-1.5B, 3B and 7B unmoved or worse (Appendix F l. 1334-1336; ledger "split ... falsified"). Write "agree for the frontier judges and phi-4; for small Qwen2.5 judges the instruction did not help (Appendix F)".
4. **Noise-control numbers pooled over pools (l. 348-350).** "2 of the 843 accepted non-matching answers" pools three pools but follows a factual-only sentence. Add the MACE-only numbers: "(on MACE alone, 2 of 282 against 78)", from `r20a_*_retest.json` mace 0+2 of 81+201 and 15+63 referenced.
5. **Table 1 P3 row "3-83%" (l. 128).** The low end (Opus 5 k-pool, 2.7%) is a per-pool value that no figure shows; Figure 3a shows pooled 4%. Use "4-83%" or say "per pool".
6. **Figure 3 caption.**
   - "an expected score above the lowest threshold" should read "at or above" (the script uses `>=`).
   - Say that API rows use 40-question, 16-candidate subsamples while open-judge rows use all 64 samples of 150 (MACE) or the full constructed pools.
7. **Dangling cross-reference (Appendix K l. 2162-2163).** "An earlier noise floor re-scored replication answers through the command-line interface (Table 12)": that block is no longer in Table 12 (`tables/main_numbers.tex` has no such row). Delete the sentence or point it to the registration file.
8. **Rounding inconsistencies a number-checker will flag.**
   - Opus 5 MACE AUROC: Table 45 −0.165; JSON −0.1645; text 0.16. Print −0.164, or say half-up.
   - Opus 5 replication false-rejection rise: Table 45 +3.6; `registration_round19.md` +3.7.
   - Max-rule AUROC cost: "0.15" (l. 422) against Table 2's +0.29 → +0.13, which subtracts to 0.16. Add "paired" or print the paired difference.
   - Haiku 4.5: 25.2% in Table 47 against 25.3% in the registration (M3).
9. **"P3 holds for all six judges on which we could test acceptance" (l. 096; l. 368).** Acceptance could also be computed for Haiku 4.5 as a grader and was computed for Qwen3 with a caveat. Write "six judges with a usable acceptance test".
10. **Figure 2 overlaps (unchanged since round 20).** At 220 dpi:
    - "not shown: subsamples" still runs across the dashed zero line in panel a (rows 227-237);
    - the grey boxed-only ticks sit on the GPT-4.1 triangles in panel b (rows 226, 232).

    Left-align the labels at x = −55, and draw the ticks as a short grey line under the marker, or offset them by a quarter row.
11. **Figure 3b.** The "−0.01" label touches the zero axis, and "0.32" touches its whisker. Move the labels to the right of the whisker end.
12. **Figure 4 design.**
    - Opus 5 (light grey diamonds) and Sonnet 5 (mid grey triangles) are hard to tell apart in print; use two distinct hues or a darker Sonnet line.
    - "max rule" is not a step in a sequence: add a gap before it, or a dotted connector.
    - Add pooled intervals (M7).
13. **Section 3 terms.** "Margin" is defined (l. 196-197) and then used once in the main text (l. 258). Replace that use with "the gap between matching and non-matching answers" and drop the definition. That removes one term from an 18-term page.
14. **Selection paragraph (l. 413-414).** "sit where no correct candidate matches the reference" needs a number or a pointer to the table (Table 12, "with a matching correct candidate ... without one").
15. **Limitations.** Add:
    - one reference draw per benchmark question (M7);
    - Opus 5's 141-question selection;
    - that open-judge factual P3 has no noise control.
16. **Human validation of any-format labels** (round-19 M6, round-20 P17). Still absent. It matters less now that MACE and the frontier judges carry P2 and P3, but Table 1's open-judge arithmetic range still rests on these labels.
17. **Appendix legibility.** At print size these are still about 5 pt:
    - Table 15 (p. 26);
    - Table 16 bottom block (p. 27);
    - Table 44 (p. 41);
    - Table 48 (p. 43);
    - Table 57 (p. 49).

    Table 46 is now fine. Use `\footnotesize` with two-line headers instead of `adjustbox` shrinking.
18. **Whitespace.** p. 13 holds one reference entry; pp. 28, 30, 34, 35, 37 and 49 are mostly empty because of float placement. `\FloatBarrier` per section plus `[!ht]` placement would recover about four pages.
19. **Section 7 first sentence (l. 375).** "from Llama-3.1-8B-Instruct to Claude Opus 5" implies an ordering; the four models are Llama-3.1-8B, Haiku 4.5, Sonnet 5 and Opus 5. Name them once.
20. **Conclusion recommendation (l. 483-485).** Now well scoped. Consider adding "or keep the higher of the two scores, which also helped a weaker grader" (M2.3).

---

## 4. Audit of round-20 items

### MUST FIX

| Item | Status | Evidence in this version |
|---|---|---|
| **M1** Benchmark consequence overstated; open-judge analysis omitted | **Fixed** (a new precision issue is raised as M1/M2 above) | Abstract l. 025-027 now scoped to "149 factual questions with several correct answers" and names the graders. Conclusion l. 480-482 scoped. Open-judge sentence added (l. 407-408, †) with Table 48 in Appendix K. Thresholds 5 and 10 in Table 47 (values match `r21a_leaderboard_*_t5/_t10`, `r21c_leaderboard_sonnet_t5/_t10`). Recommendation now "from a judge that verifies the domain" (l. 483-484). Limitations l. 460-461 "graded by three models from one provider, each of which also grades its own answers". The optional second-grader run was done with Opus 5 and Haiku 4.5 (R21-A, 9/9 confirmed), but not with GPT-4.1, so the one-provider objection remains. |
| **M2** P3 factual coverage rests on two Anthropic models | **Fixed as asked** (new substance in M5 above) | `r21a_mace_acceptance.py` adds Qwen2.5-7B (83.3%) and phi-4 (41.9%) at the 3% threshold, and at 5% (85.0%, 43.0%). Figure 3a has factual rows for both. Table 44 extended. Section 6 l. 321-323 explains the 3% threshold. The Qwen3 clause is in the thinking paragraph (l. 364-366). Table 1 verdict says "four on factual questions". Limitations l. 462-464 disclose the noise-control asymmetry. |
| **M3** Table 2b natural-mix MACE accuracy under "Several correct answers" | **Fixed** | Table 2 MACE accuracy is now k>1: +2.0/+4.0 (Qwen2.5-7B; max rule from `r16c_protocols_exact.json` mace.Qwen2.5-7B.accuracy_kgt1.max_rule_minus_blind 0.0404) and +6.1/+6.1 (phi-4). The natural mix is gone from the main table. |
| **M4** P2 verdicts disagree; Opus 5 constructed rows omitted | **Partly fixed** | Table 1 and Section 5 now agree, and Section 5's Verdict uses the replacement text verbatim. Figure 2 has "replication, Opus 5" and "k-pool, Opus 5" rows in both panels. Remaining: the Verdict's "falls on the constructed pools are small" omits the two API k-pool falls (0.06-0.08) that exclude zero (M6 above). The Sonnet 5 thinking MACE row was not added (optional). |
| **M5** Main text is a number ledger | **Largely fixed** | By my count the heaviest paragraphs now carry 11-15 numbers (Tasks, P3 acceptance, P2, P1), down from 27. Figure 4 (slope chart) replaces Table 2a, and Section 7's benchmark paragraph is prose-light. Table 2 is safeguards only, with a Reveal column. "Margin" is defined in Section 3 (l. 196-197). The OSF "primary endpoint" sentence is deleted. Remaining: Section 3 still introduces about 16 terms on one page (Polish 13); Section 6 acceptance still carries 12 numbers. |
| **M6** Unmarked post hoc statements | **Mostly fixed** (new caption conflict in M3 above) | "2% to 4%" and "3% to 15%" sentences removed. The Qwen3-8B 96% diagnostic moved out of the main text. The "tracks" sentence is gone. Table 1 row relabeled "*Moderators* (registered later; not predicted by Equation (1))". Figure 4 caption flags rankings as reported without prediction. New: Figure 2 and Table 2 captions disagree on which MACE accuracy was pre-specified; Table 45's caption still calls Opus 5's false-rejection column pre-specified, although R20-B registered FR predictions only for Sonnet 5 (defensible as a registered readout). |
| **M7** "A thinking mode removes the effect on arithmetic" | **Fixed** | Abstract l. 022-023 "thinking nearly removes the effect on arithmetic"; Intro l. 098-100 "nearly removes ... only about halves it on factual questions; and an instruction ... also reduces it there"; Conclusion l. 482 "nearly removes". Figure 3 title "nearly removes". |
| **M8** "The shortfall tracks how often the judge rejects ..." | **Fixed** | The sentence is deleted; only the descriptive "The damage is uneven across models" remains. |

### POLISH items I consider important

| Item | Status | Evidence |
|---|---|---|
| P1 Abstract length, "3 to 5", "nine judges", MBPP | **Partly** | "about 3 to 5" and "with smaller studies on MathConstraint and MBPP" are fixed. Length is up to 262 words. "ten judges" still undercounts the appendix judges. |
| P2 "both multi-answer pools" | Fixed | l. 419 "on the k-pool and MACE". |
| P3 Worked-solution baselines | Fixed by deletion | The numbers left the main text (l. 258-259). |
| P4 "such answers" pooled | **Partly** | Now "accepted non-matching answers of the two API judges" (l. 349-350), still pooled over three pools after a factual sentence (Polish 4). |
| P5 "halve it or more" | Fixed | Table 1 l. 133 "halves the factual rise in false rejections or more". |
| P6 Rounding mismatches | **Not fixed** | −0.165 against −0.1645; +3.6 against +3.7; 0.15 against 0.16; "within 2 points" is now a substantive issue (M2). |
| P7 Table 3 "120-task subsample" | Fixed | Table 3 now reads "on all 120 tasks with up to three candidates per type". |
| P8 Illegible appendix tables | **Partly** | Table 46 is now legible. Table 16 bottom, Tables 15, 44, 48 and 57 are still about 5 pt. |
| P9 Superseded CLI noise floor in Table 12 | **Partly** | Removed from the table, but Appendix K still cites Table 12 for it (Polish 7). |
| P10 Figure 1c zero line | Fixed | Dashed zero line with legend "an answer key predicts 0". The y label still lacks the unit (the caption has it). |
| P11 Figure 2 overlaps | **Not fixed** | Visible at 220 dpi (Polish 10). |
| P12 Figure 3 crosses, labels, interface | **Mostly fixed** | Crosses now drawn below the row and distinguishable. Interface shown in y ticks. "−0.01" still touches the axis. |
| P13 Table 2 title length | Fixed | About 22 words, one message. |
| P14 Consequence row in Table 1 | Fixed | l. 134-137. |
| P15 "With P2′, rules out the answer key" | Fixed | Table 1 Tests column. |
| P16 "Matched threshold" unexplained | Fixed | l. 321-323. |
| P17 Human labels | **Not done** | Limitations l. 455-456. |
| P18 Appendix vocabulary | Fixed | No "gainers/losers/placebo/wedge/git status" in `appendix.tex`. |
| P19 Blind-then-reveal column in Table 2 | Fixed, with a new problem | Column added; bold rule compares against an unprinted value (M4). |
| P20 Near-empty last page | **Not fixed** | Now p. 49 (Tables 56-57), plus p. 13 with one reference. |

### "To 8" items from round 20

| Item | Status |
|---|---|
| 1. M2 re-analysis: factual P3 for open judges | **Done** (`r21a_mace_acceptance.json`; Figure 3a; Table 44). M5 above asks for the binned version. |
| 2. Main-text restructuring (at most ~6 numbers per paragraph; Figure 4 slope chart; Table 2 safeguards only) | **Mostly done.** Figure 4 and Table 2 as proposed; numbers per paragraph roughly halved but still above 6 in four paragraphs. |
| 3. A second benchmark grader | **Done with two Anthropic graders** (Opus 5, Haiku 4.5; 9/9 confirmed; USD 8.81). GPT-4.1 was not added, so "one provider" remains. |
| 4. A non-Anthropic frontier judge on factual P3 with a same-interface retest | **Not done.** Partly offset by the post hoc open-judge factual rows. |
| 5. Human labels | **Not done.** |

### Numbers spot-checked (48 checks)

| # | Quoted (location) | Source | Result |
|---|---|---|---|
| 1 | Swap onto 5.25 / 4.09 / 3.04 (l. 212-213) | Table 8 exact +5.25; Table 34 phi-4 a +4.09, Sonnet a +3.04 | match |
| 2 | Swap off 5.41 / 3.92 / 2.66 (l. 213) | Table 8 −5.41; Table 34 −3.92, −2.66 | match |
| 3 | Neither +0.12, +0.30, +0.04 (Fig. 1 caption) | Table 8 +0.12; Table 34 +0.30, +0.04 | match |
| 4 | 10.0 / 2.9 / 9.3 (Fig. 1b, l. 059-060) | Appendix A example (swap 6.4) | consistent |
| 5 | MathConstraint "3 to 5 points" (l. 253) | Appendix O +3.21 … +5.04 | match |
| 6 | MT-Bench template loses 3.59 (l. 354) | Table 36 −3.591 | match |
| 7 | 28% against 0.4%, registered labels (l. 267-268) | Table 23 0.4% → 28.0% | match |
| 8 | MACE AUROC fall 0.06-0.16, four judges (l. 268-269) | Table 11 −0.08, −0.06; `r8_sonnet_results.json` mace −0.1531; `r19a_opus_results.json` −0.1645 | match |
| 9 | Constructed 0.17-0.27, open judges (l. 269) | `r8_lenient_results.json` lenient G_nm repl −0.2747, −0.2383; Table 27 any-format k-pool −0.23, −0.17, −0.19, −0.25 | match |
| 10 | Boxed-only 0.07-0.14 (l. 269) | Table 27 boxed only −0.10, −0.08, −0.09, −0.07, −0.14, −0.12 | match |
| 11 | API ≤ 0.08; GPT-4.1 ≤ 0.04 (l. 304-305) | Sonnet kpool −0.0796; GPT-4.1 −0.04, −0.01 | match |
| 12 | Verdict 0.04 / 0.02 / 0.01 (l. 314-315) | Sonnet repl −0.0373; Opus repl −0.0151 [−0.0385, +0.0086]; GPT-4.1 kpool −0.01 | match (omits k-pool, M6) |
| 13 | MATH-500 28.6 / 30.6 (l. 308-309) | Table 10 | match |
| 14 | MACE k=1 29.4† / 26.5 (l. 309-310) | Table 12 +29.4; Table 51 phi-4 +26.5 | match |
| 15 | P3 factual 19% / 31% (Fig. 3a) | `r20a_sonnet_retest.json` mace 0.1852; `r20a_opus_retest.json` 0.3134 | match |
| 16 | P3 factual 83% / 42% (Fig. 3a) | `r21a_mace_acceptance.json` Qwen2.5-7B\|target3 0.833; phi-4\|target3 0.4194 | match |
| 17 | Arithmetic Sonnet 11% (Fig. 3a) | (13+13)/(150+87) = 11.0% | match |
| 18 | Arithmetic Opus 4% (Fig. 3a) | (10+3)/(211+113) = 4.0% | match |
| 19 | Arithmetic Qwen2.5-7B 21%, phi-4 8% (Fig. 3a) | `r20d` weighted: (0.1923·1747+0.2504·699)/2446 = 20.9%; (0.0462·1839+0.1541·714)/2553 = 7.6% | match |
| 20 | Qwen2.5-14B 24%, gemma 57% (Fig. 3a) | `r20d` 0.2392, 0.5654 | match |
| 21 | "2 of the 843 ... against 117" (l. 348-350) | r20a pooled 318+525; 0+2; 41+76 | match |
| 22 | Matching "none do" (l. 347) | r20a match 0/137, 0/246; r21a match 0.0 | match |
| 23 | Sentence 36 → 18 and → 8 pp (l. 356-357) | `r20g_frontier_safeguards.json` FR_ref 0.3563/0.3626; FR_inst 0.1806/0.0811 | match |
| 24 | Thinking 2.85 → 0.32; 1.98 → 0.12 (l. 360-361; Fig. 3b) | Appendix L CLI −2.85 / −0.32; Table 13 −1.98 / −0.12 | match |
| 25 | Fig. 3b Qwen3-8B 0.69 / −0.01 | Table 49 −0.694 / +0.011 | match (sign shown as −0.01 for "points lost" = −(+0.011); consistent) |
| 26 | Fig. 3c +36/+15, +44/+22, +42/+18 | r8 mace FR 0.3563; `r19b_sonnet_think_results.json` FR 0.149; Table 49 44.3/21.6; Table 13 41.6/17.8 | match |
| 27 | Qwen3 thinking on 22%-23%, ≤ 2%, "about a fifth" (l. 364-366) | `r20f_qwen3_acceptance.json` 0.2335/0.2199; match 0.02/0.0; wrong blind 10 0.2077/0.2423 | match |
| 28 | Pooled shortfall 22 / 16 / 20 (l. 377) | `r20c` pooled −0.2232; `r21a_opus` −0.156; `r21a_haiku` −0.2013 | match |
| 29 | Blind within 3 for Sonnet 5 and Opus 5 (l. 404) | r20c blind_minus_list −0.0134 … −0.0268; r21a_opus −0.0071 … +0.0142 | match |
| 30 | Haiku blind −9 (l. 405) | r21a_haiku pooled blind_minus_list −0.0923 | match |
| 31 | Haiku 95% → 55% under Sonnet 5 and itself (l. 405-406) | r20c Haiku 0.9463 → 0.5503; r21a_haiku 0.9463 → 0.5503 | match |
| 32 | "level with or below Llama" (l. 406-407) | Sonnet: 55.7 vs 55.0; Haiku: 62.4 vs 55.0 | match as point estimates (M7) |
| 33 | "7 to 40" (abstract, Table 1, conclusion) | min −0.0671 (Haiku→Llama), −0.0709 (Opus→Opus); max −0.396 | match numerically (M1 on meaning) |
| 34 | "All nine registered predictions ... confirmed" (l. 407) | `registration_round21.md` P-R21A1-A4 × 2 + A5 | match |
| 35 | Figure 4, all 48 plotted values | r20c, r20g leaderboard_max_rule, r21a_leaderboard_{opus,haiku}, r21a_maxrule_{opus,haiku}; e.g. Opus-graded Haiku 94.3/95.7/73.8/95.7; Haiku-graded Llama 69.1/61.7/62.4/71.8 | match (visual read at 220 dpi) |
| 36 | "141 for Opus 5 ... 11 referenced calls" (Fig. 4 caption) | registration R21 outcome l. 55-57; `r21a_leaderboard_opus.json` questions 141 | match |
| 37 | Max rule "within 2 points ... all three graders" (l. 419-420) | pooled −1.0, +0.5, −1.7; per model Haiku→Haiku −5.37 | pooled only (M2) |
| 38 | Max rule AUROC within 0.03 (l. 418-419) | Table 2; `r20g` Sonnet mace −0.015, Opus −0.0077; Sonnet kpool −0.0231, Opus −0.0273; open k-pool ≤ 0.03 | match |
| 39 | Max-rule cost 6.7 pp, 0.15 AUROC (l. 422) | Table 16 bottom MATH-500 solution −6.7, −0.15 | match (0.16 by subtraction in Table 2) |
| 40 | Table 2, API cells −0.15/−0.06/−0.01; −0.16/−0.05/−0.01 | `r20g` −0.1531/−0.0649/−0.015; −0.1645/−0.0525/−0.0077 | match |
| 41 | Table 2 MACE max-rule accuracy +4.0 | `r16c_protocols_exact.json` mace.Qwen2.5-7B.accuracy_kgt1.max_rule_minus_blind 0.0404 | match |
| 42 | Table 2 bold cells (15 checked) | Table 16 bottom intervals (e.g. 14B accuracy max−ref +6.1 [+0.0, +15.2] not bold; phi-4 +18.2 [+6.1, +33.3] bold) | match, except the Reveal column's reference (M4) |
| 43 | Selection +2.0 / +6.1, −30.3 (l. 411-413) | Table 51 +2.0, +6.1; Table 26 any-format −30.3 | match |
| 44 | Ledger 118/11/16/17/23 = 185 (l. 205-207) | Appendix B l. 856-860: 118+11+16+17+18+2+3 = 185; R21 adds 9 confirmed to round 20's 109 | match |
| 45 | Prevalence 0%-2.5%, 30%, 18.5% (l. 071-074) | Table 5; Appendix C | match |
| 46 | 38%-43% unboxed; 88% agreement (l. 188-191) | Appendix G 61.6% / 57.1% boxed; Table 29 87.9% / 88.4% | match |
| 47 | Answer lists miss 2.3% / 8.1%; others 31%-44% (l. 170-171) | Appendix D (30.8%-43.5%) | match |
| 48 | Haiku pooled referenced false rejections (Table 47) | JSON 0.2525; Table 47 25.2%; registration 25.3% | rounding inconsistency (M3) |

`scripts/check_numbers.py` reports 8 untraced integers (185, 420, 94, 1192, 825, 1200, 405 and one repeat): counts and lengths, not results.

---

## 5. Figure-by-figure and table-by-table critique

### Main text

**Figure 1 (p. 1).**
- **At the bar.** The concrete task, one fixed reply scored 10.0 / 2.9 / 9.3, the "text never changed" sentence, and panel c's pool-level swap with an "answer key predicts 0" line. Fonts are about 8 pt at print. The selection of the example is disclosed.
- **Minor.**
  - The panel c y label "change in score" lacks "(points out of 10)".
  - Panel b's note uses registered labels while panel c uses exact-scorer any-format data (disclosed in the caption; acceptable).

**Table 1 (p. 3).**
- **At the bar.** The paper's credibility asset:
  - predictions, what each rules out, observations with registration marks, verdicts;
  - the failed predictions near each row in the caption;
  - a Consequence row.
- **Fix:**
  - "3-83%" low end (Polish 5);
  - Consequence row wording (M1);
  - the P3 verdict could say how many of the four factual judges have a noise control (M5).

**Figure 2 (p. 5).**
- **Strengths.** One shared row list, the one-answer block against the several-answers block, Opus 5 rows now present, and "not shown" labels in place of empty rows. Legible at print (minimum about 7.5 pt).
- **Problems.**
  - The label and tick overlaps from round 20 remain (Polish 10).
  - Its caption's registration sentence disagrees with Table 2's (M3).
  - The title's "for most on arithmetic" is accurate (9 of 11 arithmetic rows exclude zero).

**Figure 3 (p. 6).**
- **Strengths.** Panel a is now a strong P3 figure:
  - factual above arithmetic;
  - filled against open circles;
  - retest crosses offset and visible;
  - four factual judges.

  Panels b and c separate the arithmetic and factual thinking results cleanly. Fonts are about 7.5 pt.
- **Problems.**
  - The open-judge factual rows compress a gradient into one number (M5); a binned panel would make this the paper's second decisive figure.
  - The caption does not say that API and open-judge rows use different sample sets (Polish 6).
  - "−0.01" touches the axis in b.

**Figure 4 (p. 7).**
- **Strengths.** It delivers the Mirage-style picture the paper needed: three panels, one grammar, the referenced condition shaded, and Haiku 4.5 collapsing to Llama level. Fonts are about 8 pt; the legend is clear.
- **Problems.**
  - The title contradicts the Haiku panel for Llama (M1).
  - No intervals, while the title's inversion rests on one question under Sonnet 5 (M7).
  - The Opus and Sonnet greys are too close in print.
  - Joining "max rule" to the sequence with lines implies a progression.
  - The Opus panel's answer-list values differ from the others (141 questions), which the caption explains.

**Table 2 (p. 8).**
- **Strengths.**
  - Now one message (what helps).
  - k>1 MACE accuracy.
  - A Reveal column that makes the registered protocol's grading failure visible next to the post hoc max rule.
  - The bolding rule is stated.
- **Problems.**
  - Mixed scorers in a row, with a bold rule against an unprinted reference (M4).
  - The caption's registration sentence conflicts with Figure 2's (M3).
  - The API judges' k-pool max-rule rows (−0.023, −0.027, both excluding zero) are omitted. That is acceptable, since "within 0.03" still holds, but one line would pre-empt a question.

### Appendix (brief)

- **Table 3.** Fixed ("all 120 tasks").
- **Table 4 (ledger).** Excellent. The R21 row matches `registration_round21.md` (P-R21A1-A5, 9/9). The R19/R20 rows were re-checked against their registrations.
- **Tables 11-12.** Accurate. Table 12's CLI noise-floor rows are gone, but Appendix K still points there (Polish 7).
- **Tables 15 and 16.** Table 15 is about 5 pt. Table 16 bottom is about 4.5 pt; this is the source of Table 2 and must be readable.
- **Figures 5-10.** Legible. The caveat in Figure 7 ("not an independent test") is good practice.
- **Tables 43-45.** Accurate against `r20a` and `r20g`. Table 43's 246/247 explanation is now in the caption. Table 44 is still about 5.5 pt.
- **Tables 46-47.** Table 46 is now legible. Table 47 is new, accurate against `r21a_*` and `r21c_*`, and its registration labeling is clear.
- **Table 48.** About 5 pt, and it holds a result the main text cites.
- **Tables 49-57.** Fine. Pages 28, 30, 34, 35, 37 and 49 are mostly whitespace (Polish 18).

---

## 6. What is already at the bar (leave alone)

- **Title.** A claim, memorable and accurate.
- **Opening paragraph and Figure 1.** "The text never changed; only the correct answer the judge was shown did", now with the answer-key zero line.
- **The three readings, Equation 1 and the separation logic.**
  - It says why P2 needs P2′ and why P3 separates verification failure from agreement.
  - It says the model is not fitted.
- **The swap design with the matches-neither control.**
- **The registered same-interface retest (R20-A).** 0/318 and 2/525 against 41 and 76. Decisive.
- **The benchmark study design (R20-C, R21-A).**
  - Answers are held fixed across graders.
  - The second and third graders were registered before any call.
  - Thresholds 5 and 10 are reported.
  - Self-grading is disclosed.
- **The Table 1 Consequence row and the scoped abstract sentence.** Only the precision fixes in M1 are needed.
- **Table 2's reframing as "what helps", with the registered protocol shown beside the post hoc rule.**
- **Honesty.**
  - Registered nulls in the main text (MACE selection, distance ordering, Opus 5 replication AUROC, the small-judge instruction).
  - "Partly by construction" for the max rule.
  - The retroactive verdict-rule disclosure.
  - Opus 5's truncated calls recorded in the registration.
  - A corrected generation count.
- **Limitations.** Specific and prominent, and now names the one-provider grader set.
- **Page limit.** The main text ends on p. 9, l. 485; statements on p. 10. Compliant.

---

## 7. What would move the score

### Consolidating the 8 (rewrites and re-analyses only; 1-2 days, no API spend)

1. **M1, M2, M6.** Rewrite the Section 7 benchmark and max-rule sentences, the Figure 4 title, the abstract's grader attribution and the P2 verdict. Text only; replacement text is given above.
2. **M3, M4.** Reconcile the registration captions and Table 2's Reveal column.
3. **M5.** Binned acceptance curves for Qwen2.5-7B and phi-4 on MACE, and ideally the constructed pools, from stored scores (about 1 hour). Replace or augment the open-judge rows of Figure 3a, and add two sentences to Section 6.
4. **M7, text part.** Paired intervals for the ranking differences from stored score files (about 1 hour), pooled intervals in Figure 4, and the Opus 141-question caveat in the caption.
5. **Polish 1-10.** These are the items a careful reviewer will trip over.

### To 9 (about 1 week, under USD 60)

1. **A non-Anthropic grader on the benchmark (new data, about 1.2k calls, under USD 15).** A current OpenAI or Google model grades the 596 answers blind and referenced. This removes the last "one provider" objection to the headline consequence.
2. **Leaderboard sensitivity to the reference draw (new data, about 1.8k calls, under USD 15).** Draw a second reference from each MACE answer list and re-grade referenced with the three graders. Report per-model accuracy change between draws and ranking stability. This is P1 at leaderboard scale, and a crisp second consequence figure: "the leaderboard follows the reference draw".
3. **A non-Anthropic frontier judge on factual P3 with a same-interface retest (new data, about 2-3k calls, under USD 30).** Round-20 item 4, still open. It would let the Verdict say "noise-controlled on factual questions for judges from two providers".
4. **Main-text trim to about 6 numbers per paragraph (rewrite, 1 day).** The remaining heavy paragraphs are Setup "Tasks", Section 4, Section 5 "Several correct answers" and Section 6 acceptance. Move counts and task numbers to captions, and cut the abstract to about 200 words (Polish 1).
5. **Human labels for 200 unboxed replies (a few hours).** Lets Table 1's open-judge arithmetic P2 range drop the "not checked by humans" hedge.

### To 10, best-paper territory (weeks; new data)

1. **A second natural multi-answer benchmark with human-verified answer sets, repeating the three-grader study.** For example, AmbigQA/NQ-open items the paper's own audit flags (30% of NQ-open), or a constructive task with an executable checker. A shortfall and ranking change that recur on a benchmark people use would make the consequence general rather than illustrative.
2. **A prospective test of the recommendation.**
   - Register the max rule, and the full-credit sentence plus the max rule, before running on a fresh k-pool seed and held-out MACE questions.
   - Report grading, benchmark accuracy and unique-answer cost.
   - This turns "chosen post hoc from five combinations" into a registered safeguard.
3. **A direct manipulation of verification.**
   - Give the blind judge a verifier (the full answer list in a separate call, or a lookup tool), so v_c is set by design.
   - Show the referenced rejection curve against v_c: flat under agreement, falling to zero under verification failure.
   - With M5's binned curves as the observational version, this would move P3 from "not only verification failure" to a measured mixture.
4. **Judges as the unit.** Show that referenced grading reorders judges on a judge benchmark whose gold sets have several answers (e.g., RewardBench-2 Ties). That is the analogue of the metric-choice demonstration in the model paper.

**If only the rewrites, M5 and the two cheap runs (items 1-2 of "To 9") were done, the paper would have:**
- one question and one clean manipulation;
- a separating prediction with a graded test and a noise control across providers;
- a benchmark consequence replicated across providers and across reference draws;
- a measured partial remedy;
- a main text a reviewer absorbs in ten minutes.
