# Review: "Reference Answers Bias LLM Judges Against Other Correct Answers" (ICLR 2027 submission, round 5 PDF)

Locations are PDF page and printed line numbers (for example p.4 l.214). Quoted replacement text is meant to be pasted in.

## Summary

The paper asks what happens when a judge LLM is shown one reference answer for a question that has several correct answers. The core experiment, "rotation", keeps candidate text byte-identical and moves the reference to a different correct answer. Scores move by 3 to 5 points on a 0 to 10 scale for Qwen2.5-7B, phi-4 and Claude Sonnet 5, while a control class of correct answers that match neither reference barely moves. Rewriting the reference suggests judges compare stated final values. The paper then measures downstream cost:
- **Per-answer grading.** Grading of correct answers that differ from the reference degrades on both pools where it was measured.
- **Overall grading and best-of-64 selection.** Both degrade on constructed arithmetic pools but not on MACE's multi-answer questions.
- **Mitigations.** Reasoning before scoring and a "blind, then reveal" protocol give partial fixes.

About 150 registered predictions are scored in a ledger.

## Scores

- **Overall:** 5 (marginally below the acceptance threshold)
- **Presentation:** 2
- **Soundness:** 3
- **Contribution:** 3
- **Confidence:** 4

**Would you champion this paper at 8+?** No. The rotation finding is clean and worth publishing. But the abstract and contribution bullets sell a selection-cost and mitigation story that rests on:
- post hoc readouts;
- mixed scorers;
- a k=1 loss that contradicts the "multiple answers" explanation;
- a preregistered MACE prediction that failed and is reported without saying so.

I would move to 8 if the authors did five things:
1. Make the abstract and bullets claim only what the preregistered evidence supports: the rotation result, per-answer grading damage, and the mechanism rewrites.
2. Explain or remove the k=1 selection loss.
3. Put one scorer everywhere in the main text.
4. State the failed registered predictions where the claims are made.
5. Replace Table 2 with something validated, or cut it.

## Strengths

- **Clean manipulation.** Rotation uses byte-identical text and a "matches neither" placebo class. The blind-accepted filter (p.3 l.146-149) rules out the "the reference taught the judge" reading, and the moved-off loss for answers the judge had accepted is decisive. This is the best evidence I have seen for reference anchoring in LLM judges.
- **Cheap, informative mechanism rewrites.** Numeral, words, expression, and a worked solution with its answer visible or masked (Figure 2) separate "compares a stated value" from "string match" at little cost.
- **Registration discipline and disclosed failures.** Examples:
  - misaligned MATH-500 files (p.22 l.1135-1137);
  - a checker bug (p.25 l.1304-1309);
  - a Sonnet parsing fault (p.15 l.787-788);
  - a contaminated CLI run excluded from the counts (p.22-23);
  - the Mistral-7B score-resolution artifact (p.27).

  This is rarer than it should be.
- **Honest about MACE.** The paper says overall grading does not change on MACE's multi-answer questions (p.4 l.202-207). The nuance is already there; it just needs to reach the abstract.
- **A good thinking control.** The thinking toggle uses the same weights and prompt, and it is replicated on a second model (Qwen3-14B).
- **Hook and Figure 1.** The hook (divisor of 91) and Figure 1 communicate the finding in ten seconds.

## Must-fix before submission (ranked)

### 1. The selection loss is attributed to multiple answers, but the paper's own data say otherwise

**Where:** Abstract p.1 l.019-021; bullet 3 p.2 l.087-089; Section 5 "Selection" p.4 l.214 to p.5 l.256; Table 2 bottom-left cell.

**What is wrong.** The abstract says best-of-64 accuracy "on tasks with several correct answers falls by 8.5 to 35.9 points across five open judges". The paper's own numbers undercut that framing:
- **Losses at k=1.** Qwen2.5-7B loses 21.4 points when k=1, where only one correct answer exists (Table 36). Mistral-7B loses 10.4 at k=1 versus 8.5 at k>1. Qwen3-8B with thinking loses 5.8 at k=1 [-11.4, -1.8] versus 3.7 at k>1 [-7.5, 0.0] (Table 8).
- **The k step is significant for only two judges.** The step from k=1 to k>1 excludes zero only for phi-4 and gemma-2-9b (p.5 l.251-252; Table 39).
- **The preregistered replication population shows no loss.** Qwen2.5-7B's loss there is -4.8 [-15.2, +5.7], which includes zero.
- **The low end of the range is a broken judge.** The 8.5 comes from Mistral-7B, which Appendix M itself calls a resolution artifact ("A free screen rejects broken judges").

So the paper has shown that the reference hurts selection on the k-pool. It has not shown that the harm comes from multiple answers. Appendix I hints at a different mechanism: the referenced judge picks invalid samples containing the reference text (p.23 l.1225-1227). That would be a lure effect, not multi-answer anchoring. A reader who reaches p.5 l.250 ("Part of this loss is not specific to multiple answers") will feel the abstract misled them.

**Fix.** Explain the k=1 loss in the main text (what does the referenced judge pick at k=1?), or drop the multi-answer attribution. Replace the abstract sentence with:

> "On our constructed arithmetic tasks the reference also lowers overall AUROC (by 0.22 for Qwen2.5-7B) and best-of-64 accuracy (by 15 to 36 points for four open judges on tasks with several correct answers, although Qwen2.5-7B also loses 21 points on tasks with one); on MACE's multi-answer questions neither overall grading nor selection accuracy changes."

Also state the post-filter task counts wherever k-pool accuracy appears: 14 tasks at k=1, 39 at k>1, 7 at k=16. Right now they are only in the caption of Table 9. The -71.4 at k=16 in Table 36 rests on 7 tasks.

### 2. Failed preregistered predictions are relabelled or misdescribed in the main text

**(a) MACE selection.** p.5 l.254-255: "On MACE the reference raises accuracy by 29.4 points on single-answer questions and changes it by +2.0 [-5.1, +10.1] on multi-answer ones.^PH"
- This contrast was registered as P-R3D1: at k>1, reference minus blind < 0 with CI excluding zero, both judges.
- It failed for both judges. The registration file marks it FALSIFIED; the ledger marks it "not confirmed".
- The main text quotes a post hoc exact-scorer rerun labelled PH. It never says the registered prediction failed, while the next section does say so for blind-then-reveal.

Replace with:

> "On MACE the reference raises accuracy by 29.4 points on single-answer questions; on multi-answer questions it changes accuracy by +2.0 [-5.1, +10.1], and our registered prediction that it would lower accuracy there failed for both judges (Table 34)."

**(b) Qwen3-8B selection.** p.5 l.267-269: "and our prediction that it would not was falsified (Table 8)."
- The registered prediction (P-R2B4) was not "thinking would not lose accuracy". It was that the accuracy step from k=1 to k>1 would be negative, i.e. harm concentrated on multi-answer tasks.
- It was falsified because the loss is larger at k=1.
- The sentence as written misstates what was registered and turns a result against the paper's thesis into one for it.

Replace with:

> "Thinking does not make the reference harmless for selection, but the harm is not specific to multiple answers: shown the reference, Qwen3-8B with thinking loses 5.8 points [-11.4, -1.8] of best-of-16 accuracy at k=1 and 3.7 [-7.5, 0.0] at k>1, and our registered prediction that the loss would be larger at k>1 was falsified (Table 8)."

**(c) False rejections labelled PRE.** p.4 l.199-200: "rises from 0.4% to 28.1% for Qwen2.5-7B^PRE".
- By the paper's own definition (p.2 l.095-096), a pre-specified re-analysis of an effect whose direction was known is RE.
- The original-scorer version (0.4% to 28.0%, Table 10, PH) predates the round-4 registration.
- The rotation and k-pool rescorings from the same round are correctly labelled RE (p.3 l.143, p.4 l.215-249). This one should be too.

Apply the same test to the MATH-500 "solution" contrast (p.5 l.256, PRE). Table 16 already had it post hoc; only the bare-answer arm is new.

**(d) Verdict reconciliation.** The registration documents mark P-R2B1-3 and P-R3D1-2 "FALSIFIED". Table 4 reports several of these as "not confirmed" under the uniform rule on p.14 l.705-708. That may be legitimate, but say in Appendix B that verdicts were re-derived under one rule after registration, and when.

### 3. Two scorers produce different numbers for the same quantity on consecutive pages

**Where:**
- Qwen2.5-7B's k-pool loss at k>1 is 35.9 on p.4 l.215 (exact scorer) and 30.8 on p.6 l.317 and p.7 l.355 and in Table 1 (original scorer).
- On p.3 l.147-149, the t=7 filter gives "+4.99 ... (91% of such answers kept)" (original scorer). The next sentence gives t=9 as "+5.32" with 81% kept (exact scorer). The exact t=7 value is +5.27 with 96% kept (Table 39).
- gemma-2-9b loses 15.4 on p.4 l.215 (exact) but 17.9 in Table 9 (original). Meanwhile phi-4's blind-then-reveal loss is also 15.4 (p.6 l.318), so the same number means two things a page apart.
- Figure 3c mixes an exact-scorer judge and an original-scorer judge on one axis.

**What is wrong.** Readers hold numbers across sections. This forces them to track a scorer caveat that the paper says "changes no conclusion". It is also partly false for phi-4. Table 39's caption says phi-4's original scorer "is exact for its tokenizer", and the analysis output records "phi-4 original (single-token 10, no fallbacks)". Yet Figure 3c's legend ("phi-4, original scorer") and Limitations (p.8 l.405-406, "the phi-4 and Mistral-7B numbers ... use the original scorer") present phi-4 as affected.

**Fix.**
- In Section 2 add: "phi-4 writes '10' as one token and Mistral-7B's scores are parsed integers, so their scores are the same under both scorers; we report the exact scorer for all other judges."
- Delete every "(original scorer)" tag on phi-4.
- Either rescore blind-then-reveal, or in Table 1 and p.6 l.316 say "30.8 points under the original scorer used for this comparison (35.9 under the exact scorer, Section 5)".
- Use +5.27 (96% kept) at p.3 l.147.

### 4. Table 2, the decision table, contradicts itself and the text, and is not actionable

**Where:** p.7 l.339-352.

**Problems.**
- **"Untested" cell that reports a test.** The top-left cell reads "Untested; on the k-pool at k=1 the reference lowers Qwen2.5-7B's and Mistral-7B's accuracy". The k=1 k-pool is exactly the "rarely differ, high blind AUROC" cell, and it shows harm.
- **"By hand" contradicts the method.** The caption says the prevalence can be estimated "by auditing about 50 questions by hand ..., as in our prevalence audit". The audit (Appendix E; AI-use statement p.8-9) used 200 LLM-labelled questions per dataset, not hand checks.
- **Plural "pools" is untraceable.** "Constructed pools: overall AUROC -0.19 to -0.22" says pools, but overall AUROC is reported only for the replication pool (Table 38; p.4 l.203-204). The analysis outputs contain blind verification AUROC for the k-pool but no referenced-minus-blind change there.
- **Selective accuracy range.** "Accuracy -8.5 to -35.9 points" in that cell omits the preregistered replication population (-4.8, n.s.).
- **"0.80" is not in the paper.** The upper value in "0.69 to 0.80 here" appears in no table (it matches phi-4's MACE k>1 blind AUROC, 0.802, in an analysis JSON only).
- **Self-contradictory power sentence.** "Separating 0.87 from 0.73 with 80% power takes about 40 labeled tasks ... (power 0.93 ...)" gives two powers for one condition.
- **Column axis is post hoc and confounded.** The column split is the moderator p.4 l.212-213 calls "a candidate moderator, not a rule". It is post hoc and perfectly confounded with domain (arithmetic versus factual or MATH). No threshold between 0.80 and 0.87 is given.
- **Untested recommendations.** "Reference, auditing the answers it rejects" was never evaluated. "Use blind-then-reveal as a hedge" sits in the cell where that protocol loses 15.4 and 12.8 points to blind for phi-4 and gemma.

**Fix.** Either demote the table to the appendix as a descriptive map, or rewrite it:
- Top-left cell:
  > "k-pool, k=1 (14 tasks): the reference lowers Qwen2.5-7B's accuracy by 21 points [-43, 0]. No recommendation."
- Caption:
  > "Rows: how often correct answers differ from the reference (our estimate, Appendix E, used two LLM annotators on 200 questions per dataset). Columns: the judge's blind AUROC for correct against wrong answers; with 64 candidates per task, 40 labeled tasks distinguish 0.87 from 0.73 with power 0.93 (0.76 with 16 candidates). Cells describe the pools we measured. The column split is a post hoc moderator confounded with domain, not a validated threshold."
- Bottom-left: change "Constructed pools" to "Replication pool (AUROC); k-pool (accuracy)".
- Remove the untested bold recommendations.

### 5. The abstract's mitigation claim is post hoc, compares unequal pool sets, and omits the registered failure

**Where:** Abstract p.1 l.024-025; bullet 4 p.2 l.093; Table 1; p.6 l.319-323.

**What is wrong.** "Limits the worst-case selection loss for two of three judges" comes from Table 1, which is PH. The worst case is taken over different pools for each judge:
- **Qwen2.5-7B:** k-pool, MATH-500 and MACE.
- **phi-4:** k-pool and MACE only. It has no MATH-500 row, where blind judging loses about 30 points for the Qwen judges. So "blind judging has the smaller worst case" for phi-4 is an artifact of the missing pool.
- **Qwen2.5-14B:** k-pool and MATH-500 only, with no MACE row.

The registered predictions for this protocol on MACE failed for both judges (p.6 l.320-321), and the abstract is silent on that. "Bounds the worst-case loss" (l.093) is also wrong as English: every loss is bounded.

**Fix.**
- Run phi-4 on MATH-500 and Qwen2.5-14B on MACE, or restrict Table 1 to a common pool set.
- Replace the abstract sentence with:
  > "In post hoc comparisons, scoring blind first and revealing the reference afterwards had the smallest worst-case selection loss for Qwen2.5-7B and Qwen2.5-14B, but not for phi-4, and it did not beat the plain reference on MACE as we had registered."
- In bullet 4, change "bounds the worst-case loss for two of three judges" to "has the smallest worst-case loss for two of three judges in post hoc comparisons".

### 6. "Every pool" and "every judge" overclaim what the paper measured

**Where:**
- Bullet 3 title p.2 l.087: "graded worse on every pool we tested".
- Figure 3 caption title p.5 l.242: "damages grading of correct answers that differ from it everywhere".
- Conclusion p.8 l.421: "on every pool we measured".
- p.3 l.154-155: "but present in every judge we tested".

**What is wrong.**
- **Pools.** The body says "on both pools we tested" (p.4 l.197). Grading of non-matching answers is measured on two pools, replication and MACE. The MACE change is -0.08 [-0.14, -0.01], barely excluding zero.
- **Judges.** Qwen3-8B with thinking shows no rotation effect on arithmetic (-0.006 [-0.017, 0.000], Table 7). Mistral-7B's registered inflation was not confirmed.

**Fix.**
- Bullet 3:
  > "Correct answers that differ from the reference are graded worse on both pools where we measured grading."
- Figure 3 title:
  > "The reference degrades grading of correct answers that differ from it on both pools; its overall cost depends on the pool."
- p.3 l.154:
  > "... and positive for every judge that scores without reasoning; Qwen3 judges that think before scoring show almost none on arithmetic tasks (Section 6)."

### 7. The preregistered primary endpoint is missing from the main text

**Where:** p.3 l.129-130 ("we mention it only where it was registered"); p.6 l.322 ("brings back the preregistered inflation").

**What is wrong.**
- **No main-text result for the primary endpoint.** The OSF studies registered best-of-64 inflation as the primary endpoint. Every main-text selection claim is instead accuracy, which Limitations (p.8 l.408) concedes is post hoc on the OSF pools.
- **Inflation is never defined in the main text,** yet it is used as if the reader knows it.
- **The reader cannot see the primary result.** A reviewer who cares about registration cannot tell from the main text whether the primary endpoint was confirmed. It was, which helps the paper.

**Fix.** Add to Section 5 "Selection":

> "On the preregistered endpoint, best-of-64 inflation (Appendix A; the standardized rubric-b score of the pick above samples of the same correctness), the reference adds +1.19 SD [+1.03, +1.35] on the replication pool and +1.50 and +1.07 SD at k>1 on the k-pool for Qwen2.5-7B and phi-4 (Tables 11 and 13), all confirmed; we report accuracy because it is interpretable, and those readouts are post hoc on these pools."

### 8. Bullet 1 has a misplaced modifier that inverts the finding

**Where:** p.2 l.080-082: "while correct answers that match neither reference barely move, including answers the judge had already accepted without a reference."

**What is wrong.** Grammatically, the already-accepted answers belong to the class that barely moves. The finding is the opposite: already-accepted answers move by 5 points.

**Fix.**

> "Moving the reference to a different correct answer, with the candidate's text unchanged, moves its score by 2.7 to 5.4 points, even for answers the judge had already accepted without a reference; correct answers that match neither reference barely move."

### 9. Broken cross-reference, duplicated table, and visible macro bugs

**Duplicate label.** `\label{tab:regret}` is defined twice (main.tex:227 and appendix.tex:506).
- The main text at p.6 l.323 therefore cites "Table 27", a verbatim duplicate of Table 1 in Appendix M, instead of Table 1.
- **Fix:** delete the appendix copy (or change its label) and point Appendix M to Table 1.

**Swallowed space after `\pre`.** Written at the end of a source line followed by more text, `\pre` eats the space. The PDF shows "97% of the time.PREA short explanation" (p.6 l.302) and "that had failed.PREA second pre-specified" (p.29 l.1552).
- **Fix:** use `\pre{}` (main.tex:206, appendix.tex:603), and grep for the same pattern with `\ph`, `\reana` and `\osf`.

### 10. Main-text numbers that cannot be traced to any table, figure or appendix

- **"Whose explanations average 259 tokens"** (p.6 l.303). The number 259 appears nowhere else in the paper. Add it to Appendix C.
- **phi-4 per-answer AUROC.** "phi-4 shows the same pattern, from 0.90 to 0.65 and from 0.79 to 0.73" (p.4 l.198-199). Table 38 and Figure 3a are Qwen2.5-7B only. Add phi-4 rows to Table 38.
- **"Ranks both correct answers above the wrong one 97% of the time"** (p.6 l.301-302). Appendix N gives 94.4% and 96.9%, two numbers, of which the main text quotes the more favourable. Write "94% and 97% of the time".
- **"Each interval excluding zero"** for the 0.40-point shrinks (p.6 l.310). Table 19 gives levels, not difference intervals. Add difference CIs to Table 19.
- **"On the preregistered replication population the loss is 4.8 points for Qwen2.5-7B, an interval that includes zero"** (p.5 l.252-253). A loss is not an interval, and phi-4 gets a CI in the same sentence while Qwen does not. Write "-4.8 points [-15.2, +5.7]".

## Should-fix (ranked)

### 1. Sections 5 and 6 carry too many numbers to follow

**Where:** p.4 l.194 to p.7 l.358.

**What is wrong.**
- **Section 5** carries about 35 numbers, and **Section 6** about 45, many with scorer and registration qualifiers.
- **The thinking paragraph** (p.5 l.261 to p.6 l.304) alone has about 20 numbers across four models and three task types.
- **Appendix-only pools.** A busy reviewer needs Appendix C, H, M and N open to follow Section 6. "An exploratory pool" (p.3 l.154) and "a synthetic grid of 60 tasks" (p.6 l.306) are not introduced in Setup.

**Fix.**
- Let Figure 4 carry the thinking result. In the text keep one sentence per model family and one takeaway.
- Cut the MT-Bench and prompt-wording paragraphs to one sentence each.
- Add the Ties pool and synthetic grid to the Setup "Tasks" paragraph, or drop them from the main text.
- Remove the program-answer sentence from Section 4 (p.4 l.189-190): it is off-topic for "what the judge is checking" and rests on a split verdict.
- The main text ends on p.8, so there is spare room. Use it to enlarge Figure 3, not to add prose.

### 2. The mechanism claim is stated more strongly than three rewrites support

**Where:** Abstract p.1 l.022 ("The effect needs a final value stated explicitly in the reference"); Figure 2 title; bullet 2.

**What is wrong.** Appendix J's decode-cost experiment shows the margin collapsing for Qwen2.5-7B when the reference is given with a stated decoding step. The paper itself says "that framing may explain the collapse" (p.24 l.1266-1267). So "any unusual reference disengages comparison" is not ruled out as an explanation for "30+1". Sonnet 5's masking results (Appendix H) are also missing from Figure 2.

**Fix.**
- Abstract:
  > "In our rewrites, the effect appeared only when the reference stated a final value."
- Add the Sonnet 5 numeral, words and expression points to Figure 2.
- Say in Section 4 that the decode-cost control could not separate "must evaluate" from "unusual framing".

### 3. Figure 3 (p.5): legibility and grammar

**Label collision.** The panel letter "b" sits on top of panel b's rotated y-axis label ("... (other half)").

**Legend over the chance line.** In panel a the legend overlaps the dotted 0.5 line ("reference shown" is struck through).

**Floating group labels.** "Replication", "MACE, k=1" and "MACE, k>1" float inside the axes with no separators. At print size the MACE k=1 group (a single "all" pair) is easy to misread.

**Panel c problems.**
- MATH-500 rows have only Qwen2.5-7B, which neither legend nor caption explains.
- The caption does not say that "k-pool, k=1" and "MACE, k=1" have opposite signs.

**Registration labels.** Panel c is labelled "RE/PH", but its MATH-500 rows are PRE. Label each row, or put the labels in the y-tick text.

**Wrong task count in a related caption.** Table 38's caption says MACE non-matching AUROC uses 133 tasks. The analysis output shows 91 (k>1 tasks with non-matching answers).

### 4. Figure 4 (p.6)

- **Collided tick labels.** Panel b's x-tick labels run together ("14B factualSonnet factual").
- **Inconsistent terms.** Panel b's y-axis says "margin increase from the reference", while the text says "added margin".
- **Tick labels used as headers.** Panel a uses italic tick labels ("expected score", "sampled integer") as group headers, which read as data rows.
- **Undefined "CLI".** "CLI" is never defined in the main text; p.3 l.145 calls it "a second interface".
- **Undisclosed n.** Neither caption gives the n for the Sonnet MACE bars (40 tasks) at the bar.

**Fix.** Break the tick labels onto two lines ("14B" / "factual"). Rename the y-axis "added margin (points)". Replace "CLI" with "command line" everywhere.

### 5. Colour and marker meanings are inconsistent across figures

**What is wrong.**
- **Blue has two meanings.** In Figures 1a, 3a, 5b and 8, blue means "reference shown" and orange "blind". In Figures 2 and 7, blue means "both judges", with judge given by marker shape.
- **Other schemes elsewhere.** Figure 4 switches to black and white, and Figure 1b uses hatching for "moved off".
- **Figure 2 is oversized.** It spends 0.6 of the text width on ten points.

**Fix.** Keep blue and orange strictly for reference versus blind. Use neutral grey or black with marker shapes for judges in Figures 2 and 7. Shrink Figure 2 to about 0.45 of the width or set it beside Table 1.

### 6. Thinking claim in the abstract omits the ceiling caveat

**Where:** Abstract p.1 l.022-023.

**What is wrong.** "Reasoning before scoring removes most of it on arithmetic tasks" leaves out two things:
- The Qwen3 baselines are small: -0.69 and -1.98, against about -5 for Qwen2.5-7B.
- With thinking on, 96.2% of correct answers get a 10 even blind (p.5 l.264-265).

**Fix.**

> "Reasoning before scoring removes most of it on arithmetic tasks, where these judges already give nearly every correct answer full marks, but on factual questions extended thinking at most halves it."

### 7. Selective reporting of false-rejection rates

**Where:** p.4 l.199-200.

**What is wrong.** Qwen2.5-7B (28.1%) and Sonnet 5 (26.2%) are reported. phi-4 (0.0% to 5.8%, Table 10) is omitted, yet it is one of the two main judges and much smaller.

**Fix.**

> "... rises from 0.4% to 28.1% for Qwen2.5-7B, from 0.0% to 5.8% for phi-4, and from 4.9% to 26.2% for Sonnet 5."

### 8. The MACE blind-then-reveal result reads as significant

**Where:** p.6 l.320-321.

**What is wrong.** "It was 1.5 to 3.0 points less accurate overall" reads as a significant loss. The intervals are [-8.3, +2.3] and [-4.5, +1.5] (Table 34).

**Fix.** Append: "(both intervals include zero)".

### 9. Frontier-judge evidence covers one model family

**What is wrong.**
- GPT-4.1 failed the score-resolution screen (Appendix H), yet its margin is used in the main text as evidence (p.3 l.151-152, p.6 l.310) without noting that.
- GPT-5.4 was dropped.
- Every frontier result with thinking comes from one Anthropic model on 40 to 60 tasks.

**Fix.** Note GPT-4.1's screen failure where its margin is cited. Given that "open judges are 14B or smaller", add one non-Anthropic reasoning judge on the 40-task MACE contrast. This is the experiment most likely to change a reviewer's view of practical significance.

### 10. Terminology drifts, and several terms are used before they are defined

- **correct / valid / oracle-valid:** main text versus appendix.
- **questions / tasks / problems / items.**
- **Scorer names:** "exact scorer" versus "exact estimator" (Appendix O, Tables 35-37), and "original scorer" versus "original rule".
- **Protocol names:** "blind-then-reveal", "blind, then reveal", "Reveal", "reveal arm".
- **Margin names:** "added margin", "margin increase", "margin, ref - blind".
- **Rotation class names:** "moved off", "no longer matches" (Table 7, Table 40), "loser".
- **Filter names:** "blind-certified only" (Table 5), "blind-accepted filter" (Table 4), "scored at least 7 blind" (text).
- **"Rotation change"** is defined on p.3 l.123, but the text then says "rotation effect", "rotation gain" and "rotation loss".
- **"Blind verification"** is first used on p.4 l.208 and never defined in the main text; the definition is in Appendix O.
- **"Rubric a, used in every figure"** (p.3 l.116) is false: Figure 4a includes the MT-Bench template.

**Fix.** Pick one term for each, define "blind verification" in Section 2 Measurements, and change "used in every figure" to "used unless stated".

### 11. Section titles do not state their findings

**Where:** "What the judge is checking" (p.3), "What the reference costs" (p.4), "What to do about it" (p.5). The paragraph titled "Verify when you can" (p.5 l.261) is really about thinking.

**What is wrong.** The first sentence of that paragraph, "When a program can check correctness, no judge is needed", is repeated in the Conclusion (p.8 l.424).

**Fix.**
- Section 4: "Judges compare stated final values".
- Section 5: "Per-answer grading degrades everywhere; net cost depends on the pool".
- Section 6: "Mitigations are partial".
- The paragraph: "Thinking helps on arithmetic, less on factual questions".
- Cut the program sentence from Section 6.

### 12. Machine-prose tells

**What is wrong.**
- **Repeated "X, not Y" closers:** "a candidate moderator, not a rule" (p.4 l.213), "a hedge, not a fix" (p.8 l.423), "rather than a settled rule" (p.8 l.422).
- **Duplicated slogans:** "No protocol is best everywhere" is both Table 1's title and a sentence on p.6 l.323.
- **Wall of qualifiers:** a registration superscript ends nearly every sentence.
- **Ungrounded operational detail:** file names (`cli_transcript_audit.json`, p.23 l.1190) and "the subscription's usage limit" (p.29 l.1551) read as lab notebook, not paper.

**Fix.** Vary the closers, keep each slogan once, and move file names and operational details to the supplement README.

### 13. Limitations bullets need correcting

**Where:** p.8.

**What is wrong.**
- **"Wording and training."** It introduces a DPO result that appears nowhere else in the main text.
- **"Judges and scorers."** It misdescribes phi-4 (see must-fix 3).
- **Missing limitations.** It omits the two things a reviewer will raise: the unexplained k=1 selection loss, and the small post-filter n on the k-pool (7 to 15 tasks per k).

**Fix.** Replace the DPO clause with those two limitations.

### 14. Missing related work on answer equivalence and alternative answers in QA evaluation

**What is wrong.** Several directly relevant papers are not cited:
- Si et al., 2021, "What's in a Name? Answer Equivalence for Open-Domain Question Answering" (EMNLP).
- Bulian et al., 2022, "Tomayto, Tomahto. Beyond Token-level Answer Equivalence for Question Answering Evaluation" (EMNLP).
- Kamalloo et al., 2023, "Evaluating Open-Domain Question Answering in the Era of Large Language Models" (ACL), which documents lexical and LLM evaluators under-crediting correct answers absent from the gold list.

These are about surface-form equivalence and gold-list incompleteness, but a reviewer from QA will expect them next to Min et al. (2020).

**Fix.** Cite them in "Single references and many correct answers", with one clause separating their surface-form or incompleteness failures from this paper's result, where a correct and complete gold list still biases the judge.

### 15. Appendix float placement is sloppy

- **Near-empty pages.** p.20 has three tables separated by half-page gaps. p.28 has three tables and roughly two-thirds whitespace.
- **Out-of-order references.** p.18 cites Tables 13-14, which appear two pages later, after Tables 9-12.
- **Tiny fonts.** Tables 26, 29 and 40 are shrunk below legible print size.

**Fix.** Use `[htbp]` with grouped `\FloatBarrier`s per appendix section, and split the wide tables instead of shrinking them.

## Nits

- **Abstract, p.1 l.017-018:** "separate correct answers that differ from it from wrong answers less well" is a garden path. Suggest: "are worse at telling correct answers that differ from it apart from wrong answers".
- **Abstract, p.1 l.017-018:** "per-task AUROC 0.87 to 0.60" reads as a range; write "falls from 0.87 to 0.60".
- **"-0.00 [-0.05, +0.05]"** (p.4 l.204): write 0.00.
- **Heading capitalization:** p.3 l.150 writes "reference answer (trusted)" in lower case; the prompt heading is "Reference answer (trusted)".
- **Figure 1:** the panel-a letter is not aligned with panel b's.
- **Figure 1b** mixes an RE cell (Qwen2.5-7B, exact scorer) with PRE cells in one panel. Consider using the registered original-scorer Qwen value so the panel has one registration status.
- **"Sonnet 5" vs "Claude Sonnet 5":** choose one after first use.
- **Table 4 "Record" column:** "git" undersells the registration. Use "timestamped commit".
- **Table 3:** "Qwen2.5 1.5B–14B" is missing a hyphen style consistent with "Qwen2.5-7B".
- **MBPP** is introduced in Setup (p.3 l.108) but has no main-text result. Drop it from the main-text Setup or add a one-line result.
- **"k-subsample" vs "16-sample k-pool subsample":** use one term.
- **References:** Thakur et al. (2024) has no venue.
- **AI-use statement:** says "label a sample of dataset questions ... double-coded and adjudicated" while Appendix E says both passes came from one model family. Say so in the statement too.

## Questions for authors (answers could change my score)

1. **What does the referenced judge pick at k=1 on the k-pool?**
   - Qwen2.5-7B loses 21.4 points and Qwen3-8B with thinking loses 5.8 there.
   - If the picks are invalid samples containing the reference's text (the lure effect of Appendix I), the k-pool selection loss is largely not about multiple correct answers.
   - Then the abstract's selection headline has to go. If there is a multi-answer-specific explanation, my soundness score rises.
2. **What is the overall AUROC change on the k-pool for Qwen2.5-7B and phi-4?** If it does not fall, the "constructed pools" grading claim rests on one pool.
3. **Would "two of three judges" survive on a common pool set?** Specifically, with phi-4 run on MATH-500, Qwen2.5-14B run on MACE, and blind-then-reveal rescored with the exact scorer. If not, the mitigation claim should leave the abstract.
4. **When was the uniform verdict rule in Appendix B fixed?** The registration documents label P-R2B1-3 and P-R3D1-2 "FALSIFIED"; the ledger reports several as "not confirmed". Was the rule written before or after those outcomes were seen?
5. **Have you run any non-Anthropic reasoning judge on the 40-task MACE contrast?** If a second frontier family with thinking shows no added margin on factual questions, practical significance for current evaluation pipelines drops substantially. If it shows the Sonnet 5 pattern, my contribution score rises.
