# Review: "Reference Answers Bias LLM Judges Against Other Correct Answers" (ICLR 2027, round 7 PDF)

## Summary

The paper asks what happens when an LLM judge gets one correct reference answer for a question that has several. In the rotation test, candidate texts stay byte-identical while the reference moves to a different correct answer. Under that test, scores from Qwen2.5-7B, phi-4 and Sonnet 5 (four-token, no-reasoning scoring) move by 2.7 to 5.4 points out of 10, including for answers the judge accepted blind. Rewriting the reference suggests the effect depends on the answer being stated outright. Grading of non-matching correct answers gets worse on constructed arithmetic pools and on MACE, and on factual questions this holds even for judges that think before scoring. The best-of-64 selection cost appears on the 39-task k-pool after a post hoc exclusion of "look-alike" wrong answers, and is not detected on MACE. The paper evaluates mitigations (thinking, instructions, blind-then-reveal, a max-score rule) and a 150-prediction registration ledger.

## Scores

- Overall: **5** (marginally below acceptance threshold)
- Presentation: **2**
- Soundness: **3** (the rotation experiment is clean; the selection and grading-accuracy evidence rests on format-dependent labels and post hoc exclusions)
- Contribution: **2**
- Confidence: **4**
- Would I champion this at 8+? **No.** Three things would get me there:
  1. Relabel the constructed pools with a format-lenient answer extractor and show that the k>1 selection loss survives with no post hoc exclusions.
  2. Collect Sonnet 5's scores for wrong answers, so the frontier judge in Figure 1 has AUROC and selection numbers and not just correct-answer means.
  3. Rebuild the story around the result that survives reasoning judges. On natural multi-answer questions, the reference improves overall grading but moves errors onto other correct answers, and this persists with thinking on.

## Strengths

- The rotation design is the right experiment and is cleanly executed: byte-identical text, a correct reference, the blind-accepted filter, and a "matches neither" control. Figure 1b is convincing on first read.
- The Figure 2 masking suite ("31" / "thirty-one" / "30+1" / masked worked solution) is a neat, cheap mechanism probe. The authors honestly concede the decode-framing confound (Appendix J).
- Unusually thorough disclosure: a complete ledger that includes falsified and non-evaluable predictions, the excluded CLI run, the misaligned MATH-500 files, the checker bug, the Mistral resolution artifact, and the failed training runs.
- The MATH-500 and MACE contrasts keep the paper from claiming references are bad in general. The limitations section is specific rather than boilerplate.

## Must-fix before submission (ranked)

### 1. The headline selection claim covers more than the evidence
**Where:** abstract, last sentence; contribution bullet 4; Conclusion.

**What is wrong:** Three problems.
- The abstract says "on constructed tasks with several correct answers, once wrong answers that repeat the reference's value are set aside, accuracy falls by 15 to 21 points for three of four open judges." The 15–21 figure comes only from the 39-task k-pool at k>1.
- The OSF replication pool is also a constructed pool with several correct answers. With look-alikes set aside, Qwen2.5-7B there is **+1.9 [−5.7, +9.5]** and phi-4 is **−5.7 [−11.4, −0.9]** (Table 12). Even with look-alikes included, Qwen2.5-7B is −4.8 [−15.2, +5.7] (Table 38).
- The result is doubly post hoc (accuracy is post hoc on these pools, and so is the look-alike exclusion, Figure 3c caption). The abstract carries no flag.

The main text never mentions the replication-pool look-alike-removed numbers, and Figure 3c omits that row while showing it for the k-pool. That is selective reporting in the body.

**Fix:**
- Abstract: "The cost to best-of-64 selection depends on the pool. In a post hoc analysis of 39 constructed tasks with 2 to 16 correct answers, accuracy falls by 15 to 21 points for three of four open judges once wrong answers that repeat the reference's value are set aside. On our preregistered replication pool the loss is 0 to 6 points, and we detect none on MACE."
- Add a "Replication, look-alikes removed" row to Figure 3c.
- Put the same wording in bullet 4 and the Conclusion ("On our constructed tasks it cost three of four small open judges 15 to 21 points" → "On one 39-task constructed pool it cost three of four small open judges 15 to 21 points (post hoc); on the replication pool, 0 to 6").

### 2. Correctness labels depend on `\boxed{}` formatting, and the look-alike exclusion is a patch over that
**Where:** Section 2 "Tasks"; Section 5 "Selection"; Appendix D.

**What is wrong:**
- On the k-pool, "a reply without a box is compared as a whole and so is always wrong." Only 61.6% of samples use the box.
- The rubric tells the judge "Judge the content, not the writing." A judge that correctly credits a prose answer is scored as selecting a wrong answer.
- 73–77% of look-alikes are unboxed (Table 12), so most "look-alike wrong answers" are plausibly correct answers mislabeled by format.
- The exclusion removes only unboxed answers that match the reference. Unboxed answers stating a *different* correct value stay labeled wrong. That biases every accuracy and AUROC number in an unknown net direction.
- Every accuracy number in Figure 3c, Section 6 and Tables 8/29/30/38 inherits this, including Table 27's "the reference lowers Qwen2.5-7B's accuracy by 21.4 points".

**Fix:**
- Re-run the checker with a lenient extractor: the last stated value anywhere in the reply, checked against the complete stored answer set. The answer sets are complete, so this is cheap.
- Report selection accuracy and AUROC under both labelings with no exclusions, and make the lenient labels primary.
- If the k>1 loss survives, the paper is stronger. If not, the selection bullet must go.
- Either way, add to Limitations: "38% of candidates ignore the requested answer format, and our registered checkers count them wrong; selection accuracy under format-lenient labels is [X]."

### 3. GPT-4.1 is reported as "no change" when it could not be measured
**Where:** abstract ("we detect no change on MACE or for GPT-4.1"); bullet 4; Section 5 "Selection"; Conclusion ("we found no cost ... for GPT-4.1").

**What is wrong:**
- GPT-4.1 failed the paper's own registered score-resolution screen: 15.5 candidates tied at the maximum with the reference (Table 12), so its four inflation predictions are "not evaluable" (Table 3).
- The same judge's picks shift toward matching answers 32 to 1 (Appendix H), and it has a +1.19 margin.
- Listing GPT-4.1 alongside MACE as a place with "no cost" tells readers a frontier API judge is safe. The data say the measurement was blind to the effect.

**Fix:**
- Delete GPT-4.1 from the abstract and Conclusion.
- In Section 5 write: "GPT-4.1's scores tie too heavily to resolve best-of-64 selection (15.5 of 64 candidates tie at its maximum); its picks nonetheless shift toward the reference's answer (32 referenced-only vs. 1 blind-only)."

### 4. The frontier judge on page 1 has no wrong-answer data
**Where:** Introduction para 2; Figure 1a; Table 1; Section 5 ("Sonnet 5's selection accuracy cannot be computed, because only its scores for correct answers were collected").

**What is wrong:**
- The hook and Figure 1a are Sonnet 5, but Sonnet 5 was never scored on wrong answers (0 of 4,186, Table 12).
- The paper's own central nuance is that on MACE the reference's help against wrong answers outweighs its pull away from correct ones (Appendix N). For Sonnet 5 a reader cannot tell which side wins, so Figure 1a shows half the trade-off.
- Figure 1a is also post hoc, while the paper's registered frontier evidence is elsewhere.

**Fix (preferred):** Score the 4,186 wrong replication-pool candidates and the MACE wrong answers with Sonnet 5, then add its AUROC to Figure 3a and Table 40. That is a few thousand API calls.

**Fix (minimum):** Add to the Figure 1a caption: "Sonnet 5 was scored only on correct answers, so this panel does not show whether the reference also helps it reject wrong ones." Repeat it in the Limitations "Judges" bullet, replacing the vaguer "Sonnet 5's selection accuracy was not measured."

### 5. Registration labels contradict each other, and PRE is defined wrongly
**Where:** Section 1 (label definitions); Figure 1b; Section 3; Table 1; Tables 16, 37, 39, 41; Appendix B.

**What is wrong:**
- The same numbers carry different labels in different places:
  - The exact-scorer rotation for Qwen2.5-7B (+5.25/−5.41) is RE in Figure 1b and Section 3, but PRE in Table 37.
  - MATH-500 accuracy +30.5 is PH in Table 16 but PRE in Table 39.
  - The exact-scorer false-rejection rise (+27.7) is PH in Table 41 but a confirmed registered prediction in Table 3.
  - The k-pool exact-scorer losses are PRE in Table 38 but RE in Section 5.
- PRE is defined as "pre-specified in a timestamped commit before the data existed". Many PRE items are rescorings of stored logits or analyses of "frozen files" (Appendix N, O), where the data already existed.
- Table 1 carries a blanket "PRE/RE/PH", which tells the reader nothing.
- The verdict rule was adopted "on 13 September 2026, after most outcomes were known." That is disclosed, but it sits badly next to "Every confirmatory prediction was written down before its data existed."

**Fix:**
- Define PRE as "pre-specified in a timestamped commit before the analysis was run (for new model calls, before the data existed)".
- Reconcile every duplicated number to one label.
- Put a label on each cell or row of Table 1.
- In Appendix B, replace "Every confirmatory prediction was written down before its data existed" with "Every confirmatory prediction was committed before its analysis was run; the verdict rule applied to them was adopted afterwards (below)."

### 6. A failed registered prediction reads as a confirmed one
**Where:** Section 6, "Blind, then reveal": "and on MACE it did not beat the reference, as we had predicted it would."

**What is wrong:** The registered prediction was that blind-then-reveal *would* beat the reference at k>1, and would be at least as accurate over the natural mix. Both failed for both judges (Table 3, "MACE end to end"). A skimming reader will parse the sentence as a confirmation.

**Fix:** "and on MACE it did not beat the reference, contrary to our registered prediction."

### 7. Table 1 is not traceable, mixes interfaces, and its title overclaims
**Where:** Table 1 and its caption (page 4).

**What is wrong:**
- **Cells found in no other table:** Qwen3-8B/14B arithmetic false-rejection changes (+1.5, +0.0, +6.1, +0.3) and Qwen2.5-7B/phi-4 MACE changes (+63.8, +54.4). I found them only in `analysis/r7_posthoc_results.json`. The Sonnet 5 factual CIs [+5.0, +30.0] and [+2.5, +25.0] likewise appear in no table (Appendix N gives the point values only).
- **Sonnet 5 row:** +21.2 has no CI anywhere in the paper, and Sonnet's arithmetic "Thinking" cell is "—" although the data exist and are quoted as levels in the caption ("fell from 26.7% to 0.4%").
- **Mixed interfaces:** the Sonnet row takes arithmetic from the API but factual values from the CLI.
- **"—" means two things:** "not applicable" for Qwen2.5/phi-4, and "measured but not tabulated" for Sonnet.
- **Rows are not comparable:** they use different task sets and sampling designs (full 64-sample pools vs. one sample per class for Sonnet vs. up to four per class for Qwen3). They also mix expected-value scores with sampled integers, which changes what "scored 3 or below" means.
- **Title overclaims:** "Correct answers that differ from the reference are marked as failing" is contradicted by +1.5 (Qwen3-8B) and +5.8 (phi-4).

**Fix:**
- Retitle: "Showing the reference raises the share of non-matching correct answers scored 3 or below, most on factual questions."
- Add the missing cells, with CIs, to an appendix table.
- Report Sonnet arithmetic as a change with a CI in both columns, and mark interface per cell (API/CLI).
- Add to the caption: "Rows use different task subsets and score readouts; compare columns within a row, not across rows."

### 8. "Every judge we tested"
**Where:** abstract ("rises by 12.5 to 63.8 points for every judge we tested"); Section 5 ("rises for every judge we tested").

**What is wrong:** The paper tests at least nine judges. Only five (Qwen2.5-7B, phi-4, Qwen3-8B, Qwen3-14B, Sonnet 5) were run on factual false rejections.

**Fix:** "for all five judges we ran on factual questions, including two that think before scoring."

### 9. The "ceiling" argument is wrong for the loss direction, and the Section 6 heading contradicts its own data
**Where:** abstract ("On arithmetic, judges that think before scoring barely anchor, but they already give nearly every correct answer full marks without a reference"); Figure 4 title ("where they sit at the ceiling"); Appendix N ("leaves no room for a reference to move them"); Section 6 heading "Thinking helps where judges already verify; explanations do not"; bullet 5 ("Thinking removes the arithmetic effect").

**What is wrong:**
- A correct answer at 10 has a full 10 points of room to *fall* when the reference moves off it. The rotation-loss null for thinking judges is therefore informative: they verify and resist the pull. Calling it a ceiling effect undersells the paper's most practically useful mitigation and is logically wrong for the moved-off cell. It holds only for the moved-onto gain.
- "Explanations do not" rests on one Qwen2.5-7B MT-Bench cell. Sonnet 5's *reasoning* arm, with extended thinking off (i.e., an explanation before the score), shrinks the loss from −2.85 to −0.20 (Figure 4a).

**Fix:**
- Abstract: "On arithmetic, judges that reason before scoring verify the answer and barely anchor; on factual questions they still anchor."
- Section 6 heading: "Reasoning before scoring removes the arithmetic effect for some judges but not the factual one."
- Figure 4 title: "Judges that reason before scoring barely anchor on arithmetic but still anchor on factual questions."
- Bullet 5: "Thinking" → "Reasoning before scoring (thinking, or a written rationale for Sonnet 5, but not the MT-Bench template for Qwen2.5-7B)".

### 10. The "second reading" is dismissed with the wrong evidence and against the paper's own phi-4 result
**Where:** Section 3, para 3: "Telling the judge that other correct answers deserve full credit lowers Sonnet 5's anchoring margin by 0.93 points [−1.22, −0.65] from +3.00 but does not remove it."

**What is wrong:**
- The CI is traceable only to `frontier_instruction_results.json`, and the number is not on the replication pool this section is about. It is the 37-task k-pool subset (Table 19, no difference row).
- Section 6 then says the same instruction "removes phi-4's margin on a synthetic grid at k=16". For phi-4, the heading-implies-uniqueness reading is *supported*.
- A better control exists and is buried: the reveal call's "No score" variant uses the heading "Reference answer (one valid answer, trusted)" and still restores inflation (Table 32).

**Fix:** "In the second, the heading implies that the question has one answer. An explicit note that other correct answers deserve full credit shrinks the margin for Sonnet 5 (from +3.00 to +2.08 on 37 k-pool tasks, Table 19) and GPT-4.1, removes it for phi-4 on a synthetic grid, and does not help smaller Qwen2.5 judges (Section 6). A heading that says the reference is 'one valid answer' does not stop inflation (Table 32)." Add the difference row with its CI to Table 19.

### 11. Failures that bear on the paper's motivation are hidden in the appendix, while the main text asserts what they failed to show
**Where:** Section 2 ("which is what a policy optimized against the judge can exploit"); Introduction ("Tasks that ask for an example, a construction, or a program admit many correct answers by design"); Ethics ("Anyone optimizing against a reference-guided judge on multi-answer tasks can exploit the failure"); Limitations.

**What is wrong:**
- **Training:** the only optimization experiment (Appendix L, three LoRA-DPO runs) found that the reference arm did *not* copy the reference more ("its exact-reference rate fell"). Held-out accuracy fell in every arm, and a stopping rule closed the question as unresolved.
- **Code:** on MBPP the reference *lowers* inflation for both judges (Table 23), and the program format shows ~0 inflation (Figure 7). Yet the introduction lists "a program" as a motivating case.
- **Constraint pilot:** all four MathConstraint selection designs failed or were unresolved (Appendix P).
- None of this appears in the main text.

**Fix:**
- Section 2: "which is what a policy optimized against the judge can exploit" → "which bounds what best-of-n selection against the judge can exploit".
- Ethics: "can exploit" → "may be rewarded for matching the reference".
- Introduction: delete "or a program", or append "(though on MBPP we find the reference helps; Appendix K)".
- Add a Limitations bullet: "**Downstream.** Three DPO runs against the referenced judge did not show the policy copying the reference, and all arms lost held-out accuracy, so we have not shown that training exploits the bias (Appendix L). On code (MBPP) the reference reduced inflation (Appendix K)."

## Should-fix (ranked)

### 1. Figure 3b does not earn its space
**Where:** Figure 3b; Section 5 "Grading overall" last sentence.

**What is wrong:** The panel is post hoc, and the text itself calls it "a post hoc lead confounded with room to improve". It also holds only within MACE: the split-half ρ on the replication pool and k-pool is +0.10 and +0.05 (Table 41). The label lists phi-4's ρ but plots only Qwen2.5-7B points, and at print size the ρ box overlaps the data.

**Fix:** Delete panel (b) and the sentence. Use the space to enlarge (a) and (c) and to add the replication look-alike-removed row (Must-fix 1).

### 2. Two scorers are used across the main text
**Where:** Section 2; Figure 1b (exact); Figure 2 ("original scorer"); Section 6 accuracy ("under the original scorer"); Figure 3 (scorer unstated); Table 12 (scorer unstated).

**What is wrong:** The same judge's numeral margin is reported under a different scorer from its rotation effect. The reader must track which scorer each number uses, and the Setup paragraph on "10" tokenization is main-text load for a nuisance detail.

**Fix:** Rescore everything under the exact scorer (the machinery exists, Appendix O) and move the scorer history to Appendix A. If that is impossible, state the scorer in every figure and table caption.

### 3. Sections 5 and 6 compare on different bases
**Where:** Section 6 "Blind, then reveal", accuracy sentence.

**What is wrong:** The Section 5 headline uses look-alikes removed, while blind-then-reveal accuracy uses look-alikes included and the original scorer (Table 8), so "recovers two thirds of Qwen2.5-7B's loss" is measured against a loss (−30.8) the paper has just called format-inflated.

**Fix:** Report blind-then-reveal on the same labels as the Section 5 headline.

### 4. The "zero-cost rule" is neither zero-cost nor uniformly "as well or better"
**Where:** Section 6, last sentence; Table 29.

**What is wrong:**
- The max rule needs both a blind and a referenced call, which is the same cost as blind-then-reveal and twice a referenced judge.
- The comparator is unstated. Against blind-then-reveal, the claim is false for Qwen2.5-14B on the k-pool (Max −2.6 vs. reveal +2.6).
- Table 29 has no CIs, and on 39 tasks a 2.6-point difference is one task.

**Fix:** "A rule that reuses the blind and referenced scores, taking the higher of the two, matches or beats the referenced judge on the k-pool and MACE but trails it on MATH-500 for Qwen2.5-7B (Table 29, no intervals; differences of ≤3 points are one task)." Add CIs to Table 29.

### 5. The preregistered endpoint is undefined in the main text and then displaced
**Where:** Section 2 "Measurements"; Section 5 "Selection".

**What is wrong:** The main text never says inflation selects with rubric a and scores with rubric b, or that it subtracts a within-class permutation null. Without that, "+1.19 SD" has no meaning, and the next sentence moves to a post hoc metric.

**Fix:** Add one sentence: "The judge picks with one rubric and we score the pick with a second rubric, relative to samples of the same correctness, so inflation measures how far the pick is over-scored beyond its correctness." Then say plainly: "Because inflation is hard to interpret, we report accuracy, which was not registered on these pools."

### 6. "The effect tracks an explicitly written answer" is stronger than Section 4 supports
**Where:** Section 4 title; bullet 2.

**What is wrong:** The section concedes "we cannot say whether the property that matters is an answer that must be evaluated or an unusual framing".

**Fix:** Retitle Section 4 with the Figure 2 caption's wording: "Anchoring shrinks when the reference does not state its answer outright."

### 7. A loss claimed with a CI that touches zero
**Where:** Section 5 ("Qwen2.5-7B also loses 21.4 points at k=1"); Table 27 cell.

**What is wrong:** The interval is [−43, +0]. Under the paper's own verdict rule that is "not confirmed".

**Fix:** "Qwen2.5-7B's k=1 point estimate is −21.4 [−43, 0]."

### 8. Table 1 splits Section 4's text
**Where:** Table 1 float, page 4.

**What is wrong:** It lands inside Section 4 and splits a sentence ("Writing 31" | Figure 2 | Table 1 | "as 'thirty-one'…"), before Section 5 has even started.

**Fix:** Move the float after the Section 5 heading (page 5, below Figure 3), or cut Figure 2 to a half-width wrap.

### 9. Terminology drift
**Where:** throughout.

**What is wrong:**
- "Anchoring margin" is defined as a within-referenced difference (Section 2, Figure 2, Section 3's "+3.00"). But "the increase in anchoring margin" (Section 6), Figure 4b's "margin, reference − blind" and Table 35's "added margin" are referenced-minus-blind.
- "Rotation change" is defined, then "rotation loss" is used.
- "Blind verification" is defined but never used in the main text.
- Main-text "correct" becomes "valid" in the appendix.

**Fix:** Define "added margin" (referenced minus blind) in Section 2, use it in Section 6 and Figure 4b, and drop "blind verification" from Section 2.

### 10. Figure legibility and encoding grammar
**Where:** Figures 3 and 4; Figure 5a.

**What is wrong:**
- Figure 3a/b tick labels and the (b) ρ box are ~5 pt at print size.
- Figure 4b x-ticks ("8B arith.", "S5 fact.") are unreadable, and there is no Sonnet arithmetic bar with no explanation.
- Figure 4's caption is nine lines and the marker legend duplicates the y-axis labels.
- Dark fill means "reference moved onto" in Figure 1b but "thinking off" in Figure 4b.
- Blue means "reference shown" in Figures 1a/3a/5b, but encodes judges in Figure 5a.

**Fix:** Raise the minimum font to 7 pt, use full names on Figure 4b's axis, cut the Figure 4 caption to four lines, and keep blue = reference and orange = blind everywhere.

### 11. Floats that nothing cites
**Where:** appendix.

**What is wrong:** 15 floats are never cited: Tables 7, 9, 10, 11, 15, 17, 18, 19, 23, 25, 27, 30 and Figures 5, 7, 8. Pages 18, 20 and 29 are mostly whitespace. Table 27 has a bold caption disclaiming itself ("not a validated decision rule") and no citation. If it is not a decision rule and not referenced, cut it.

**Fix:** Cite each float in the text or delete it. Tighten float placement.

### 12. Wrong table citations and a silently dropped judge in "Grading overall"
**Where:** Section 5 "Grading overall".

**What is wrong:** "by 0.22 on the replication pool" cites Table 41, but the number is in Table 40. "by 0.14 to 0.23 at k>1 on the k-pool for four judges" silently drops Mistral-7B (−0.07). "15.4 points for Qwen2.5-7B and gemma-2-9b and by 20.5 for phi-4 … Qwen2.5-14B" cites Figure 3c, which shows only Qwen2.5-7B and phi-4.

**Fix:** Cite Table 40 for the replication number, name the four judges, and cite Table 12 for gemma and 14B.

### 13. The Conclusion's recommendation was never tested
**Where:** Conclusion, last sentence: "audit the answers a reference-guided judge rejects before trusting its grades."

**Fix:** Tie the recommendation to something measured, e.g., "When correct answers can differ from the reference, also score blind and take the higher score, or check rejected answers against the task's answer set."

### 14. Unexplained analysis choices
**Where:** Section 2; Section 5; Table 12.

**What is wrong:**
- The pass-rate band is 0.05–0.95 on MACE but 0.2–0.8 elsewhere, with no reason given.
- The look-alike exclusion does not say whether the pass-rate filter was reapplied after removal.
- There is no multiplicity statement for ~150 predictions and dozens of main-text CIs.

**Fix:** Justify the MACE band, or report MACE under 0.2–0.8 too. State the order of filtering and exclusion. Add one sentence on multiplicity.

### 15. Cross-references that overreach
**Where:** Introduction; Section 3.

**What is wrong:**
- Introduction: "on factual questions it can verify without one (Section 6)". The verification evidence (94.4%/96.9% blind ranking) is only in Appendix N.
- Section 3: "The effect is smaller for larger Qwen2.5 judges (Appendix C)" rests on the exploratory Ties pool, which Appendix F calls "motivation only".

**Fix:** Cite Appendix N, and add "on an exploratory pool" to the Section 3 sentence.

### 16. Bullets and abstract are hard to read
**Where:** contribution bullet 4; abstract sentence 4.

**What is wrong:**
- Bullet 4's title "The selection cost is narrower" is a comparative with no referent.
- Abstract sentence 4 packs seven numbers and two pools into one sentence.
- "3/10" (abstract) vs. "3 or below" (body).

**Fix:** Bullet title: "The selection cost depends on the pool." Split abstract sentence 4 into two sentences, one for AUROC and one for false rejections. Use "3 or below" throughout.

### 17. OSF links withheld
**Where:** Appendix B.

**What is wrong:** ICLR permits anonymized view-only links. Withholding them makes the three OSF labels unverifiable during review.

**Fix:** Provide anonymized view-only OSF links.

## Nits

- Section 3: "They move just as much" → "nearly as much" (Sonnet 5 moves +3.04 overall vs. +2.79 when filtered).
- Abstract: "even for answers the judge had accepted without a reference" is attached to the 2.7–5.4 range, but the filtered moved-off value for Sonnet is −2.50 (Table 4).
- Sonnet's arithmetic false-rejection rise is implied as +21.3 in the intro (4.9% → 26.2%) and given as +21.2 in Table 1. Explain once or use one number.
- "Post-hoc" (Table 11) vs. "post hoc" elsewhere. Tables 11 and 13 state registration status in words, with no superscript.
- Degenerate intervals "+0.0 [+0.0, +0.0]" in Table 1: write "0 of N" instead.
- Appendix letters do not follow first mention (Appendix E is cited before A, B, D).
- Small caps are applied to MACE and REWARDBENCH-2 but not MATH-500, NQ-open or MBPP.
- "Claude Sonnet 5" / "Sonnet 5" / "S5": pick two at most.
- Table 2 lists MATH-500 judges as "Qwen2.5 1.5B–14B", but Tables 28/39 cover only 7B and 14B. Say which analyses use which judges.
- Eq. (1) is labeled but never referenced.
- The build log shows `Font shape OT1/ptm/m/scit undefined` (small-caps italic falling back). Check the superscript labels inside italic or emphasized captions.
- The prose is tight but has a house style of aphoristic headings ("A free screen rejects broken judges and certifies nothing.", "The validity gate backfires for one judge.", "Thinking helps where judges already verify; explanations do not.") and near-constant superscripts after clauses. That reads as a ledger rather than an argument. Put labels at the end of paragraphs where all claims share a status.

## Questions for authors (answers could change my score)

1. With a format-lenient extractor and no look-alike exclusion, what are the k>1 selection accuracy changes on the k-pool and the replication pool for the four open judges? If a loss of 10 or more points survives on both pools for at least three judges, Must-fix 1 and 2 largely dissolve and I would move up.
2. What are Sonnet 5's blind and referenced AUROCs (non-matching correct vs. wrong) on the replication pool and on MACE multi-answer questions? A frontier judge whose grading gets worse on natural multi-answer questions would be the paper's strongest practical result.
3. Were the look-alike definition and exclusion fixed before you saw how exclusion changed the k-pool and replication-pool results? When were they computed relative to the 13 September verdict rule?
4. Was the MACE 0.05–0.95 pass-rate band registered? Does the MACE k>1 selection result change under 0.2–0.8?
5. Can GPT-4.1 be resolved at all, e.g., by breaking ties with its top-5 log-probability expected score? If so, what is its k>1 accuracy change?
6. The prevalence audit found 60 multi-answer NQ-open questions. Have you run grading (false rejections, AUROC) on any natural open-domain multi-answer set beyond MACE's two audited domains? A second natural pool would address the external-validity concern that currently caps contribution at 2.
