# Review: "Reference Answers Bias LLM Judges Against Other Correct Answers" (ICLR 2027 submission, round 6 PDF)

## Summary

The paper asks what a reference answer does to an LLM judge when a question has several correct answers. The core experiment keeps each candidate's text byte-identical and moves the reference to a different correct answer. Scores follow the reference by 2.7 to 5.4 points on a 0-10 scale (Qwen2.5-7B, phi-4, Sonnet 5), even for answers the judge accepted without a reference. Rewrites of the reference suggest the judge compares final answers. Grading of correct answers that differ from the reference gets worse on a constructed pool and on MACE. Overall grading and best-of-64 accuracy fall on constructed multi-answer pools but not on MACE. Thinking before scoring removes most of the effect on arithmetic but not on factual questions, and a "blind-then-reveal" protocol is offered as a partial fix. The paired manipulation is clean and the registration ledger is unusually honest. The problems are elsewhere: several headline sentences say more than the tables, the selection story is partly a different failure (wrong answers that resemble the reference), and the most practically important result is buried in Appendix N.

## Scores

- Overall: **5** (marginally below acceptance threshold)
- Presentation: **2**
- Soundness: **3**
- Contribution: **2**
- Confidence: **4**
- Would I champion this at 8+? **No.** Two things would make me:
  1. Show a selection or net-grading cost on a judge people actually deploy (Sonnet 5 with tie-averaged accuracy, ideally with thinking on) or on a second natural multi-answer pool. Right now every selection loss comes from 7B-14B 2024-era open judges, scored in 4 tokens, on constructed tasks, and the one natural benchmark is null.
  2. Rebuild the abstract and section claims so that every sentence matches a table, with one scorer throughout.

## Strengths

- **The rotation design is the right experiment.** The candidate text is byte-identical and only the reference moves. The "matches neither" control stays near zero (+0.12 [−0.07, +0.30], Table 34), and the blind-accepted filter (+5.27 at t=7, +5.32 at t=9, Table 38) rules out "the reference taught the judge".
- **The scorer check is thorough.** The effect is robust across the expected-value, original-rule and greedy-integer scorers (Table 34), across two rubrics, and across five open judges plus Sonnet 5.
- **Failures are disclosed properly.** Examples: the Sonnet 5 parsing fault and recollection, misaligned MATH-500 files, the program-checker bug, the contaminated CLI run (excluded, with its thinking-rate asymmetry reported), the phi-4 decode cells with no scores, and the failed training arms. The 150-prediction ledger reports falsified predictions next to confirmed ones. This is rare, and it is to the authors' credit.
- **The MACE null is reported in the main text.** The authors did not quietly drop it.
- **The mechanism rewrites work well as an idea.** Words vs. expression vs. masked worked solution is a neat, cheap design (Figure 2).

## Must-fix before submission (ranked)

### 1. The abstract's selection sentence mixes units, overstates the multi-answer-specific harm, and hides a different failure

**Location:** Abstract, sentence 5 ("On the constructed tasks, the reference also lowers overall AUROC and best-of-64 accuracy on tasks with several correct answers, by 15 to 36 points for four open judges; on MACE's multi-answer questions neither changes."). The same framing appears in contribution bullet 3, Section 5 "Selection", and the Conclusion.

**What is wrong:**

- **(a) Units.** "by 15 to 36 points" is attached to both overall AUROC and accuracy. AUROC falls by 0.14 to 0.23 on the k-pool and by 0.22/0.19 on the replication pool (Section 5). It never falls by 15-36 points.
- **(b) The 36 is not a multi-answer cost.** Qwen2.5-7B already loses 21.4 points at k=1, where the reference is the only correct answer.
  - The k=1 to k>1 step is −14.5 [−39.6, +12.7] for Qwen2.5-7B and −26.7 [−55.8, +3.0] for Qwen2.5-14B (Table 38). Both intervals include zero.
  - The multi-answer-specific step is significant only for phi-4 and gemma-2-9b.
- **(c) Much of the k>1 loss is lures, not correct answers being rejected.** For Qwen2.5-7B at k>1, picks of wrong answers containing the reference's text rise from 5% to 28%, and other wrong picks rise from 3% to 15% (Table 38).
  - So much of the accuracy loss comes from *rewarding wrong look-alikes*, not from biasing the judge *against other correct answers* (the title).
  - Section 5 half-admits this for k=1 only. The sentence "wrong answers that resemble the reference, not other correct answers, cause that loss" is trivially true at k=1, where no other correct answer exists.
- **(d) The preregistered pool disagrees.** On the preregistered replication population, Qwen2.5-7B's accuracy change is −4.8 [−15.2, +5.7]. The abstract's "constructed tasks" claim is drawn from 39 k-pool tasks only.
- **(e) The judge set was swapped.** "Four open judges" is not the registered four. The round-4 prediction was Qwen2.5-7B, Qwen2.5-14B, gemma-2-9b and Mistral-7B (Mistral −8.5 [−12, −5]). The main text swaps in phi-4's original-scorer, post hoc −20.5. Mistral has a defensible reason to be excluded, but the reader is not told.
- **(f) "Neither changes" is absence of evidence.** Qwen2.5-7B's MACE k>1 accuracy is +2.0 [−5.1, +10.1], and phi-4's is +6.1 [−1.0, +13.1].

**Fix.** Replace abstract sentence 5 with:

> "On constructed tasks with several correct answers, the reference lowers overall AUROC by 0.14 to 0.23 and best-of-64 accuracy by 15 to 36 points for four open judges; for two of them a similar accuracy loss already appears when only one answer is correct, where picks shift to wrong answers that contain the reference's text. On MACE's multi-answer questions we detect no change in either (accuracy +2.0 points, 95% CI [−5.1, +10.1])."

Also:
- Plot the k=1 to k>1 step, with its CI, as a row in Figure 3c.
- Add one sentence in Section 5 on the Table 38 pick decomposition at k>1.
- Say in one clause why Mistral-7B is omitted from the range.

### 2. "At most halves it" is false, and "reasoning removes most of the effect on arithmetic" contradicts the paper's own MT-Bench row

**Location:** Abstract, last sentence; contribution bullet 4; Figure 4 caption title; Section 6 first paragraph; Conclusion ("Reasoning before scoring removes most of the effect only where the answer can be checked by calculation").

**What is wrong:**

- **(a) The halving claim fails for one judge.** Qwen3-14B's factual added margin falls from +7.07 to +3.13 (Table 39). That is a 56% reduction, so thinking *more than* halves it for that judge.
- **(b) Written reasoning does not remove it.** The MT-Bench template makes Qwen2.5-7B write a 259-token explanation before scoring, on the same arithmetic pool, and the score still falls by 3.59 points (Table 6). Section 6 reports this in the same paragraph. The thing that removes the effect is not "reasoning before scoring" in general. It is Qwen3/Sonnet thinking, or Sonnet asked to reason, and the MT-Bench prompt also tells the judge to begin "by comparing ... with the reference answer".
- **(c) The arithmetic result is confounded with a ceiling, which the authors concede.** Thinking-on Qwen3-8B gives a 10 to 96.2% of correct answers *blind*. The thinking-off baselines are tiny (−0.69 for Qwen3-8B vs −5.41 for Qwen2.5-7B). "Removes most of the effect" on a −0.69 baseline is not the same claim as for the 5-point effect in Figure 1.

**Fix.** Abstract last sentence:

> "Judges that think before scoring (Qwen3's thinking mode, or Sonnet 5 asked to reason) show almost no effect on arithmetic tasks, where they already give nearly every correct answer full marks without a reference; a written explanation under the MT-Bench template does not remove it, and on factual questions thinking leaves 44% to 76% of the added margin."

Figure 4 title:

> "Thinking judges barely anchor on arithmetic, where they sit at the ceiling, but still anchor on factual questions."

Section 6 heading:

> "Thinking helps where judges already verify; explanations do not."

### 3. The mechanism is stated as established, but the paper's own control says it is not identified

**Location:** Abstract sentence 4 ("the effect appeared only when the reference stated a final value"); Section 4 title "Judges compare stated final values"; Figure 2 caption title "The effect needs a final value stated in the reference"; contribution bullet 2.

**What is wrong:**

- **(a) The expression rewrite still anchors, with intervals excluding zero.** Qwen2.5-7B +0.29 [+0.07, +0.49], phi-4 +0.89 [+0.64, +1.13], Sonnet 5 +0.47 (Table 20, Appendix H). So "appeared only when" is false.
- **(b) The control is confounded.** The announced-decoding control also removes the margin. Section 4 concedes that "we cannot separate a reference that must be evaluated from one that is merely framed unusually". A claim you cannot separate from a framing confound cannot be a section title.
- **(c) Words lose part of the effect.** "Thirty-one" is a stated final value, yet it loses 38% of Qwen2.5-7B's rubric-a margin (4.62 to 2.88).

**Fix.** Section 4 title:

> "The effect tracks an explicitly written answer."

Abstract sentence 4:

> "In our rewrites, writing the reference's answer in words kept most of the effect, while an expression to evaluate, or a worked solution with its final answer masked, removed most or all of it; a control with unusual framing removed it too, so we cannot say which property matters."

Figure 2 title:

> "Anchoring shrinks when the reference does not state its answer outright."

### 4. Several registration labels in the main text are wrong. The paper sells itself on these labels, so each error costs credibility.

**Wrong labels:**

- **Section 5, "Grading overall".** "On the replication pool, overall AUROC falls by 0.22 for Qwen2.5-7B^PRE". Round-4 registration R4-D registered G_all only on MACE (P-R4D3) and only G_nm on the replication pool (P-R4D4). The replication overall-AUROC drop is post hoc. Change the label to PH.
- **Registered result replaced by a post hoc split.**
  - The registered overall-grading prediction was "MACE G_all referenced minus blind > 0": +0.07 [+0.02, +0.13], confirmed.
  - It never appears in the main text prose. Instead the post hoc k-split is used to say overall grading "does not change on MACE's multi-answer questions".
  - Report the registered result first, then the split: "On MACE overall AUROC rises by 0.07 [+0.02, +0.13], as registered; the rise comes from single-answer questions (+0.29), and on multi-answer questions it is 0.00 [−0.05, +0.05] (post hoc)."
- **Figure 3 caption conflicts with Section 5.** The caption says the MACE accuracy rows are post hoc ("the other rows are post hoc"). But Section 5 marks the MACE k>1 accuracy prediction PRE, and the ledger ("MACE end to end") confirms it was registered. The caption also lumps phi-4's original-scorer, post hoc k>1 row under "pre-specified or pre-specified re-analyses". Label each row, or add a registration marker next to each row label in the plot.
- **Section 5 "Selection" RE label.** "35.9 ... 23.1 ... 20.5 for phi-4 ... 15.4 for gemma-2-9b, all with intervals excluding zero^RE". The phi-4 value is not RE (see item 1e). Split the sentence.
- **Section 6 "Blind, then reveal".** "all of Qwen2.5-14B's and Mistral-7B's" counts Mistral-7B as a success. Appendix M calls Mistral-7B's null harm "a resolution artifact", and the paper argues its scores (11 distinct values, 32.3% substituted 5.0s) cannot support selection claims. Delete Mistral-7B from this sentence.

**Verdict-rule timing.** Appendix B says the verdict rule was adopted "on 13 September 2026, after most outcomes were known", and that it converts some documented falsifications into "not confirmed". Every such reclassification helps the authors. Add a column or footnote giving the counts under the registration documents' original verdicts, and name the predictions that moved.

### 5. Sonnet 5's selection accuracy is "not reported because its integer scores tie", but the accuracy metric is defined to handle ties

**Location:** Table 9 caption; Table 18 caption; Section 2 ("the accuracy of the best-of-64 pick, averaging over ties"); Appendix A ("when several samples tie at the maximum, accuracy is the mean validity of the tied samples").

**What is wrong.** The paper's selection accuracy is tie-averaged by definition, and Sonnet 5 judged every sample on the replication pool (3,494 correct samples are counted in Table 4). So the only current frontier judge's best-of-64 accuracy is computable from existing files. Ties are a reason not to use *inflation*, not accuracy. As it stands, every selection headline rests on ≤14B open judges.

**Fix.**
- Report Sonnet 5 and GPT-4.1 tie-averaged best-of-64 accuracy, blind and referenced, on the replication pool, and on MACE if Sonnet has those files, labelled PH. Also report the average number of tied maxima so readers can judge how much selection is possible.
- If the numbers are null, say so. That changes the story, and reviewers will ask anyway.

### 6. The story leads with the fragile regime and buries the robust one

**Location:** Introduction paragraph 2 (the Sonnet 5 hook, "extended thinking off"); Section 6; Appendix N ("Sonnet 5 with and without thinking").

**What is wrong.** The reader builds a mental model on the hook and Figure 1: a score-only judge on arithmetic. Four pages later the paper says that this regime mostly disappears when the judge thinks. The paper ends up arguing that:

- where the effect is robust to thinking (factual questions), it has no net selection cost (MACE); and
- where it has a selection cost (constructed arithmetic, score-only small judges), thinking largely removes it.

A busy reviewer reaches the Conclusion unable to answer "when should I worry?". The only guidance is Table 26, in the appendix, whose caption opens by disclaiming itself.

The result that answers that question is in Appendix N:
- Sonnet 5 *with thinking on*, on natural factual questions it can verify blind 97% of the time, still has an added margin of +3.03 [+1.70, +4.65]; false rejections of correct non-matching answers rise by 12.5 points.
- Qwen3-14B with thinking still shows +17.8 points of false rejections.

These appear in the main text as half a sentence.

**Fix.**
- Keep the divisor-of-91 hook, but add a closing sentence to the intro's second paragraph: "With thinking on, the same judge still marks down correct answers that differ from the reference on factual questions it can verify without one."
- Replace Table 1 (a post hoc minimax over two or three judge-specific pools, which will favour almost any intermediate protocol) with a main-text table of false-rejection increase for correct non-matching answers:
  - rows: Qwen2.5-7B, phi-4, Qwen3-8B, Qwen3-14B, Sonnet 5;
  - columns: arithmetic vs factual, each for score-only vs thinking.
- Move Table 1 to Appendix M.
- Delete the worst-case clause from contribution bullet 4, or rewrite it as: "blind-then-reveal recovers most of the k>1 loss for two of four judges and keeps nearly all of the reference's benefit on MATH-500."

### 7. Mixed scorers make main-text comparisons wrong and give the same contrast two values

**Examples:**

- **Section 6, "Blind, then reveal".**
  - The paragraph has "10.3 points instead of 30.8, which is 35.9 under the exact scorer".
  - It then says phi-4 and gemma-2-9b "stay 15.4 and 12.8 points below blind judging" (original scorer).
  - Section 5 gave gemma's reference loss as 15.4 (exact scorer). Its original-scorer reference loss is 17.9 (Table 8).
  - A reader comparing 12.8 with 15.4 concludes that blind-then-reveal recovers 2.6 points. It actually recovers 5.1 of 17.9. The identical "15.4" for phi-4's blind-then-reveal loss and for gemma's reference loss adds to the confusion.
- **MACE k=1 accuracy change for Qwen2.5-7B:** +29.4 in Section 5 and Table 38, +32.4 in Tables 17 and 33.
- **Replication-pool accuracy change for Qwen2.5-7B:** −4.8 (Table 35) vs −7.6 (Table 9).
- **Qwen2.5-14B k>1:** −23.1 (Section 5) vs −17.9 (Table 8).
- **Qwen2.5-7B blind-then-reveal at k>1:** −10.2 in Table 1 vs −10.3 in Table 8 and the Section 6 text.
- **Missing scorer statements.** The Figure 3 caption does not say which scorer each judge uses. Table 4 (file `rotation_exact.tex`) shows Qwen2.5-7B at +4.97/−5.04, which matches neither row of Table 34 (exact +5.25/−5.41; original rescored +4.96/−5.01), and its caption names no scorer.

**Fix.**
- Rescore blind-then-reveal with the exact scorer. It needs one extra forward step per "1" token, the same thing already done for five pools. Then report one scorer throughout the main text.
- If that cannot be done in time, use the original scorer for every number in the blind-then-reveal paragraph, including the reference losses it is compared against, and delete the "which is 35.9 under the exact scorer" parenthetical.
- Put the scorer in every figure and table caption.
- Reconcile Table 4 with Table 34.

### 8. The main text is a ledger written as prose

**Location:** Sections 3, 5 and 6. The worst paragraphs are Section 3 paragraph 3 (lines 131-135), Section 5 "Grading overall" (lines 173-179), and Section 6 "Blind, then reveal" (lines 210-216).

**What is wrong.**
- These three sections quote roughly 130 numbers.
- Single sentences carry 6-10 numbers, bracketed CIs, a registration superscript and a parenthetical inside a parenthetical. One example: "+5.27 for Qwen2.5-7B, keeping 96% of such answers (the registered test, under the original scorer, gave +4.99), +4.08 for phi-4, and +2.79 for Sonnet 5."
- Table 38 exists only to give main-text numbers somewhere to live.
- Superscripts after nearly every clause turn a rigor signal into noise.
- A reviewer cannot hold the replication pool, k-pool, synthetic grid, Ties pool, MACE, MATH-500, rubric a/b, three scorers and five metrics (rotation change, anchoring margin, added margin, false rejection, AUROC, accuracy, inflation) in their head. They will skim, and skimming this paper produces the overclaims in items 1-3.

**Fix.**
- Cap each paragraph at three numbers, with the takeaway sentence first.
- Push the rest to tables.
- Drop the Ties pool and synthetic grid from the main text: they are used once each.
- Drop "added margin" as a separate term from the main text. Use "anchoring margin, referenced minus blind" where needed.

Rewrite of Section 6 "Blind, then reveal" to show the target density:

> "Our preregistered mitigation scores the candidate blind, then reveals the reference together with that score. It removes the preregistered inflation at k>1 for Qwen2.5-7B and phi-4 (OSF), and hiding the blind score brings the inflation back (PRE). In accuracy it recovers two thirds of Qwen2.5-7B's k>1 loss and all of Qwen2.5-14B's, but little of phi-4's or gemma-2-9b's (PH, Table 8), and keeps nearly all of the reference's benefit on MATH-500 (PRE, Table 27). On MACE it did not beat the reference, as we had predicted it would (PRE, Table 33)."

## Should-fix (ranked)

1. **The novelty sentence overreaches.** Introduction: "None of it varies which correct answer is the reference or measures what that does to grading and selection." Fomicheva & Specia (2016), cited in your own Section 7, showed human raters different correct reference translations and measured the bias. Replace with: "No study of LLM judges that we know of varies which correct answer is the reference, or measures what that does to grading and selection."

2. **"We know every correct answer" is false for MACE.** Introduction: "so we know every correct answer". Section 8 says MACE lists miss 2.3% to 8.1% of correct answers. Replace with: "so we know every correct answer on our own tasks and nearly every one on the audited MACE domains".

3. **"On both pools where we measured grading" is inaccurate.** It appears in bullet 3 and the Conclusion. Overall grading was also measured on the k-pool (Table 38) and blind AUROC on MATH-500 (Table 37); per-answer grading was measured on two pools. Replace with: "on the replication pool and MACE, the two pools where we measured grading of each kind of correct answer".

4. **The abstract's AUROC numbers belong to one judge but read as general.** "Judges are worse at telling correct answers that differ from it apart from wrong answers: per-task AUROC falls from 0.87 to 0.60 ..." Write: "for Qwen2.5-7B, per-task AUROC falls from 0.87 to 0.60 ... (phi-4: 0.90 to 0.65 and 0.79 to 0.73)".

5. **"Added margin" is misused.** Section 3: "shrinks Sonnet 5's added margin on the k-pool by 0.93 points ... from +3.00". In Table 18, +3.00 is the *referenced* margin; the blind margin is +0.20, so the added margin is +2.80. Replace "added margin" with "anchoring margin with the reference". The same slip is in Section 6 ("Sonnet 5's and GPT-4.1's margins").

6. **The preregistered interval differs between text and table.** Section 5 has "+1.19 SD [+1.02, +1.36]"; Table 12 has "+1.19 [+1.03, +1.35]". Pick one bootstrap run and regenerate both. The AI-use statement says "we checked every claim against those outputs", and this sentence becomes a liability when a reviewer finds a mismatch in the preregistered endpoint.

7. **The preregistered endpoint is demoted without a reason.** "We report accuracy because it is easier to interpret; on these pools the accuracy readouts are post hoc." The OSF endpoint (inflation) appears nowhere in the abstract, and the main text never explains why a practitioner should care about it. Either:
   - add one sentence of motivation, e.g. "inflation measures how far the judge over-rates the answer it picks relative to answers of the same correctness, the quantity a policy optimized against the judge exploits", and put the confirmed +1.19 SD in the abstract; or
   - say plainly that the registered endpoint was replaced as the headline and why.

8. **Figure 1 has problems.**
   - (a) Panel a has no intervals, while panel b has them.
   - (b) The intro's 9.19/9.09/9.99/6.93 appear in no table; add them to Table 9 or 38 with CIs.
   - (c) Blue means "reference shown" in panel a and "reference moved onto the answer" in panel b. Use a different hue (e.g. dark grey vs hatched grey) for panel b's onto/off bars, or recolour panel a.
   - (d) The shared bottom legend sits under both panels but applies only to panel b; move it under panel b.

9. **Figure 3b does not say whose tasks the dots are.** The plot shows one scatter but annotates two ρ values (Qwen2.5-7B −0.54, phi-4 −0.38). Say whose tasks are plotted, or plot both judges with the marker grammar of panel c.

10. **Figure 4a is hard to read.**
    - Italic group headers ("expected score", "sampled integer", "Sonnet 5, command line") sit on tick rows and look like missing data.
    - It mixes 0-10 expected scores, sampled integers, and MT-Bench's 1-10 scale on one axis.
    - Its markers (circle, square, filled/hollow triangle, plus, cross) are only half explained ("hollow: thinking on").
    - Fix: use bracketed group labels with no ticks, state the MT-Bench scale, and add a marker key.

11. **Setup inconsistencies about MACE.**
    - Section 2 says "whose answer lists passed our completeness audit (133 tasks)". Table 2 says MACE is "300 questions ... (River, Language, and Math domains)". Appendix N shows 133 is River + Language *after the pass-rate band*. State the audited count and the in-band count separately.
    - Justify the MACE pass-rate band of 0.05-0.95 (vs 0.2-0.8 elsewhere) in Section 2, and say whether it was registered.

12. **Limitations miss the most consequential scoping fact.** The main open judges score in at most 4 tokens with no reasoning ("Respond with only the integer score"), and that is the regime where the arithmetic effect lives. Add it to "Judges and scorers".
    - The sentence "Our reference heading may suggest a unique answer, which an explicit instruction only partly counters" is in the "Registration" bullet. Move it to "Tasks and generators".

13. **A post hoc moderation result gets three sentences and a panel.** "Blind verification may moderate the overall cost." This is post hoc, confounded with domain, and in Figure 3b the dots at blind AUROC near 1 have no room to gain. Cut it to one sentence and drop Figure 3b, or keep it and move the "more room to improve" caveat into the Figure 3 caption.

14. **Section 3 overgeneralizes on strength.** "The effect is smaller for stronger judges (a rotation gain of 9.48 for Qwen2.5-1.5B and 3.07 for Qwen2.5-14B on the Ties pool)". This rests on one family on the exploratory pool, with n=40 onto-samples. Replace with "smaller for larger Qwen2.5 judges".

## Nits

- **Section 3:** "keeping 96% of such answers" reads as if the reference keeps them accepted. Write "(96% of answers pass this filter)".
- **Section 6:** "extended thinking" is Anthropic's product term. For Qwen3 write "thinking mode".
- **"Sonnet 5" vs "Claude Sonnet 5":** both are used (Tables 4, 9, 18 vs text). Pick one.
- **Section 5 title:** it wraps to two lines. Suggest "What the bias costs in grading and selection".
- **Figure 2:** at 0.5\textwidth, the tick labels and the "bare reference" / "worked solution, final answer" headers are about 5pt in print. Enlarge the fonts or widen to 0.65\textwidth.
- **Page 5:** there is a visible vertical gap between the Figure 3 caption and the continuation line "pools, where blind AUROC is uniformly high".
- **Appendix floats:** \FloatBarrier leaves pages 18, 20, 25 and 27 mostly empty.
- **Figure 5a:** the legend box covers data at k=1-2, and the "blind" label overprints the zero line.
- **Table 10:** the font is too small to read in print.
- **Duplicate tables:** Tables 32 and 39 repeat the Qwen3-8B columns. Merge them.
- **Appendix H:** "the MACE reversal" is never defined. It means the negative blind margin; say so.
- **Appendix H:** the file name `cli_transcript_audit.json` does not belong in running text.
- **Appendix J "Solution route":** "Three of four cells exclude zero" follows only three reported values (−0.32, −0.40, −0.02).
- **Appendix I:** "−37.4 points per unit distance" on a 0-10 scale needs the distance normalization defined.
- **Appendix I:** "well below the 0.82 and 0.90 that measurement noise would allow under a linear link" is opaque. Say "the noise ceiling on the correlation".
- **Appendix M:** "58 multi-answer tasks from the k-pool and replication pool" conflicts with the 39 in-band k-pool tasks used elsewhere. Explain the pooling.
- **Table 24:** held-out accuracy change is a fraction (−0.228), while every other table uses points or percent.
- **Table 2:** "six open judges" for the synthetic grid; name them.
- **Appendix N:** "an interruption by the subscription's usage limit" is unnecessary detail about tooling.
- **References:** Thakur et al. (2024) sets the arXiv venue in italics, unlike the other arXiv entries.
- **Main text:** "Table 26 summarizes the pools we measured" closes Section 6 by pointing into the appendix. Either bring the map into the main text (see must-fix 6) or cut the sentence.

## Questions for authors (answers could change my score)

1. **Sonnet 5 selection.** What is Sonnet 5's tie-averaged best-of-64 accuracy, blind vs referenced, on the replication pool and MACE? How many candidates tie at the maximum? A significant multi-answer selection loss for a frontier judge would raise my contribution score. A null would mean the selection story is about small score-only judges, and the paper should say that.

2. **Lures vs. other correct answers.** Take the Qwen2.5-7B and Qwen2.5-14B k-pool k>1 pools and remove every wrong candidate that contains the reference's answer text. Does the accuracy loss remain, and is the k=1 to k>1 step then significant? This separates "biased against other correct answers" (the title) from "fooled by wrong look-alikes".

3. **A cheap baseline.** How does blind-then-reveal compare with a zero-cost score combination such as min, max or mean of the blind and referenced scores, or the blind score with the referenced score as tie-breaker, on the same pools? If a one-line rule matches it, the mitigation contribution disappears.

4. **Another natural pool.** Is there any natural multi-answer pool other than MACE River/Language where the reference has a net negative effect on grading or selection? The NQ-open multi-answer items from your audit, or Ties with repaired answer lists, are obvious candidates. As submitted, the net-cost evidence is constructed pools negative, one natural pool null.

5. **Thinking at k=1.** Why does Qwen3-8B with thinking lose 5.8 [−11.4, −1.8] points of best-of-16 accuracy at k=1 (Table 7), where the reference is the only correct answer? If thinking judges are hurt by a *correct unique* reference, that is a separate and arguably more important finding. If it is an artifact, the "harm is not specific to multiple answers" sentence in Section 6 should go.

6. **What the lures are.** Concretely, what are the "wrong answers containing the reference's answer text" at k>1? For example, a pair where one element equals one element of the reference pair. If many are partially correct by a reasonable rubric, part of the measured selection loss is a labeling choice.
