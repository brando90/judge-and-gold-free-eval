# Round 16 review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

Reviewer role: ICLR 2027 Area Chair (presentation, story, reliability of main-text claims).
Material read: round16_main.pdf, all 43 pages. Numbers were checked against the appendix tables as rendered and, for exact wording, against main.tex and tables/*.tex. Line numbers below are the PDF's.

---

## 1. Summary of what the paper claims

The paper asks whether a reference answer given to an LLM judge works like an answer key when a question has several correct answers. It sets out three readings: an *answer key* (any correct answer scores the same), *verification failure* (the reference is the judge's only evidence), and *agreement* (the judge favors the answer it was shown even when it can recognize others). From these it derives three predictions. P1: swapping which correct answer is the reference moves the score of byte-identical text. Across the replication pool the swap is 2.7–5.4 points out of 10 for Qwen2.5-7B, phi-4 and Sonnet 5 (Fig. 1c). P2: correct answers that differ from the reference are rejected more often and separated worse from wrong answers. False rejections rise 6.5–54 pp and grading AUROC falls 0.07–0.27 on constructed pools and 0.06–0.15 on MACE. A unique reference still helps (+29–31 pp on MATH-500). P3: the effect persists on answers the judge already accepts blind. For Sonnet 5, 19% of non-matching factual answers it scored 10 blind drop to 3 or below. The paper also reports that reasoning before scoring shrinks the effect on arithmetic but much less on factual questions, and that best-of-64 selection loses accuracy mainly when no correct candidate matches the reference. Its practical fix is a post hoc "max rule" (keep the higher of the blind and referenced scores). This keeps open judges' grading AUROC within 0.03 of blind, at some cost on unique answers.

The claim is easy to extract from the title, Figure 1 and Table 1. That is a real strength. The *boundaries* of each claim are much harder to extract: which judge, which scorer, which labeling, which interface, and whether the result was registered. Those boundaries are spread across hundreds of in-line numbers, 35 registration marks and 28 appendix pointers in nine pages.

## 2. Score and confidence

**Score: 6 / 10 (marginally above the acceptance threshold). Confidence: 4 / 5.**

**Biggest reason.** The central experiment is clean, new and useful: swap the reference on byte-identical text, with a "matches neither" control. Disclosure is unusually honest. But the main text reads like an audit log rather than a paper. And several headline sentences claim more than the paper's own figures and tables show. In the abstract, the Fig. 3 title and the conclusion: "reasoning removes the effect on arithmetic", "a simple protocol removes the grading harm", "P3 holds ... with and without thinking", and "not evidence that the answer is wrong". Registration marks are also inconsistent in places, which matters in a paper whose credibility leans on its registration ledger. All of this can be fixed by rewriting.

---

## 3. Ranked issues

### MUST FIX (misleading or internally inconsistent)

**M1. "Reasoning before scoring removes the effect on arithmetic" is contradicted by Figure 3a.**
- Where it appears:
  - Abstract l.25–26: "Reasoning before scoring removes the effect on arithmetic and roughly halves it on factual questions."
  - Intro l.91–92.
  - Fig. 3 title l.344: "Reasoning before scoring removes the effect on arithmetic".
  - Sec. 6 l.351–352.
  - Conclusion l.479–480.
  - Limitations l.464–465.
  - Table 1 P1 verdict: "Holds unless the judge reasons first".
- Problem:
  - The paper defines *explanation first* as a form of reasoning before scoring (Sec. 3 l.181–184). Yet in Fig. 3a two explanation-first open judges still show the effect: Qwen2.5-7B under the MT-Bench template loses **3.59** points and Qwen3-14B with thinking off loses **1.98**. Table 1's own P1 cell says "still present when open judges explain before scoring", which contradicts its verdict "Holds unless the judge reasons first".
  - Sonnet 5's leftover effects exclude zero: −0.20 [−0.37, −0.05] explaining first and −0.32 [−0.67, −0.07] thinking (App. N l.1994–1995). So "removes" is too strong even for Sonnet 5.
  - "Roughly halves it on factual questions" holds for Qwen3 only. For Sonnet 5 the reduction is "not distinguishable from zero" (l.357).
- Fix: use one precise sentence everywhere. Abstract: "A thinking mode shrinks the effect on arithmetic to near zero, and so does explaining first for Sonnet 5 but not for open judges. On factual questions thinking roughly halves the rise in false rejections for Qwen3, with no detectable reduction for Sonnet 5." Fig. 3 title: "**A thinking mode shrinks the effect on arithmetic; explaining first is not enough for open judges; on factual questions the effect persists.**" Table 1 P1 verdict: "Holds for score-only and explain-first open judges; near zero with a thinking mode." Limitations l.464: "why a thinking mode shrinks the effect on arithmetic".

**M2. The abstract's and Table 1's AUROC range "by labeling" leaves out the labeling with the largest falls.**
- Abstract l.20–21: "grading AUROC falls by 0.07 to 0.27 for four open judges, depending on how answers are read". Table 1 P2: "falls by 0.07–0.27 for the screened judges on constructed pools, by labeling".
- Table 14 (four labelings) under registered labels: replication −0.29, −0.28; k-pool −0.30, −0.23, −0.23, **−0.33** (phi-4). Across all four readings the range is **0.07–0.33**. The 0.07–0.27 range covers only boxed-only (0.07–0.14) and any-format (0.17–0.27).
- The abstract also gives no pool. On MACE phi-4 falls by 0.06 (Table 49), outside "0.07 to 0.27 for four open judges".
- Fix: "grading AUROC falls by 0.17–0.27 with answers read in any format (0.07–0.14 counting only boxed replies) for four open judges on constructed pools, and by 0.06–0.08 on MACE." Make the same edit in Table 1, replacing "by labeling" with the two named labelings.

**M3. Registration marks break the paper's own rule in at least five places.** The Table 1 caption rule is: unmarked = pre-specified, † = post hoc, ‡ = re-analysis, and "a mark on a range means the range includes such a value".
- (a) Table 1 P1 "2.7–5.4 points" is unmarked, but 5.4 is Qwen2.5-7B's exact-scorer 5.41‡ (l.220). The abstract range has the same issue. Add ‡.
- (b) Table 1 P2 "False rejections rise by nearly the same amount under every labeling" is unmarked. The relabelings are post hoc (l.194–195 †; l.251 "Appendix D).†"; Table 15 caption †). Add †.
- (c) Sonnet 5's AUROC falls on constructed pools use any-format labels (Table 26 caption: "Replication and k-pool use answers read in any format"). The Fig. 2 caption (l.303) says "any-format and boxed-only values ... are post hoc". But Table 26 is marked PRE, and Table 1's "by 0.04–0.15 for Sonnet 5" is unmarked. One of these is wrong. If the Sonnet 5 registration named any-format labels, say so in the Table 26 caption and narrow the Fig. 2 caption rule to the open judges. Otherwise add †.
- (d) MATH-500 reference-solution accuracy (+30.5 / +27.6) is marked three different ways. Table 2 caption (l.386–387): "The reference and blind-then-reveal accuracy cells on MATH-500 and MACE were pre-specified". Table 22 caption: † (post hoc). Table 35: PRE. The ledger (l.911–913): "confirmed, **without registration weight** after a disclosed amendment". Pick one; the ledger's wording implies † or ‡, not "pre-specified".
- (e) The appendix never uses ‡. Tables 46, 47 and 48 carry PRE, while the main text marks the same numbers ‡ (5.25‡, 5.41‡, 28.6‡, 30.6‡). Add ‡ to appendix captions, or add one sentence to App. B saying PRE there includes the main text's ‡.

**M4. The abstract's protocol claim hides that it is post hoc, open-judge-only, and near-mechanical for the AUROC it reports.**
- Abstract l.26–29: "A simple protocol removes the grading harm: scoring each answer with and without the reference and keeping the higher score leaves grading AUROC within 0.03 of blind judging".
- It is post hoc. Table 2 caption: "the rest are post hoc"; Tables 36 and 37 carry †. The max rule was also picked from five combinations after seeing Table 36, where App. M l.1836–1837 says "No rule is best everywhere".
- It is shown only for open judges. For Sonnet 5 no max-rule grading AUROC is reported. Its max-rule k-pool accuracy is −2.4 [−5.0, −0.5], worse than simply showing the reference (−2.6 [−5.8, +0.4], not significant; Table 26). Sec. 7 l.413–414 reports the −2.4 without that comparison.
- Keeping AUROC within 0.03 of blind is close to automatic. The reference *lowers* both non-matching correct answers and ordinary wrong answers. So max(blind, referenced) ≈ blind for exactly the two groups this AUROC compares. The informative quantities are (i) how much of the unique-answer benefit survives (Table 2: 23.8 of 30.5 pp for Qwen2.5-7B) and (ii) look-alike wrong answers, which the reference raises and the max rule keeps raised.
- Fix, abstract: "In a post hoc analysis of stored scores, keeping the higher of each answer's blind and referenced scores kept four open judges' grading AUROC within 0.03 of blind on both multi-answer pools, and kept most of the reference's benefit on unique answers." In Sec. 7, add one sentence on why the AUROC result is near-mechanical, and give Sonnet 5's referenced −2.6 next to its max-rule −2.4.

**M5. "Not only the prompt" says more about the MT-Bench template than the template allows.**
- l.318–320: "Every referenced prompt calls the reference trusted and tells the judge to use it. Two results show the effect is not only that instruction. Under the verbatim MT-Bench template, which does not call the reference trusted, Qwen2.5-7B still loses 3.59 points".
- The MT-Bench template *does* tell the judge to use the reference. The intro quotes it (l.62, "by comparing the assistant's answer with the reference answer"), and so does App. C l.1004–1005. So the template removes the word "trusted" but keeps the instruction to use the reference. It also adds explanation first, a second change. Only the full-credit sentence tests the instruction itself.
- Fix: "Under the verbatim MT-Bench template, which drops 'trusted' but still asks the judge to compare against the reference (and to explain first), Qwen2.5-7B still loses 3.59 points. The full-credit sentence is our only test of the instruction itself: Sonnet 5 keeps +2.08 [+1.14, +3.14] against +3.00." Correct Limitations l.462–463 to match.

**M6. The conclusion's inference about low scores is literally false.**
- l.482–483: "a low reference-guided score on an answer that differs from the reference is not evidence that the answer is wrong."
- Table 49: with the reference, AUROC for non-matching correct against wrong answers is 0.60 and 0.65 on the replication pool and 0.66 and 0.73 on MACE. That is above 0.5, so a low score is still evidence, just weak.
- Fix: "... is much weaker evidence that the answer is wrong than it appears: with the reference, AUROC against wrong answers falls to 0.60–0.73 from 0.74–0.90 blind (Table 49)."

**M7. P3's verdict is stated more firmly than its evidence.**
- Verdict l.363–365: "P3 holds: Sonnet 5 penalizes factual answers it already accepts, with and without thinking, and Qwen2.5-7B still moves arithmetic answers on tasks it verifies almost perfectly."
- The registered P3 test (CLI, 40 questions) measures *ranking*: both correct answers above the wrong one 94% / 97% of the time. It does not measure acceptance. An answer ranked above a wrong one can still have v_c < 1, where verification failure also predicts a bonus (λ(v) = λ0(1 − v)).
- The acceptance test (19% of 81 blind-10 answers) is post hoc, API only, thinking disabled, one judge, and has no test–retest baseline, as l.313 admits. The matching group does not serve as a noise baseline, because the reference pushes matching answers *up*.
- "Verifies almost perfectly" for Qwen2.5-7B rests on per-task AUROC 0.98 of expected scores, which ranks answers but does not show acceptance. App. N l.2002–2005 itself calls the ≥7 filter "a weak test of verification".
- Fix, wording: "P3 holds for Sonnet 5 on factual questions. A registered ranking-based test (with and without thinking) and a post hoc acceptance test (19% of 81 blind-10 answers, thinking disabled) both show the penalty. For Qwen2.5-7B on arithmetic the effect shrinks but stays at 3.6 points where blind AUROC averages 0.98. That is consistent with agreement but is not an acceptance test." Adjust Table 1's P3 verdict in the same way.
- Fix, re-analysis (no new calls): App. H l.1511–1525 reports 939 calls that both Sonnet 5 interfaces completed (67% exact agreement, 82% within one point). If these include blind scores, report how often an API blind 10 becomes ≤3 on the CLI blind call. That gives a rough noise floor next to the 9% (replication) and 15% (k-pool) rates. If the shared calls are referenced only, say so and keep the l.313 caveat.

**M8. Presentation: too much bookkeeping per sentence (the main reason the score is not higher).**
- The main text carries 28 † and 7 ‡ marks, two scorers, four labelings, two Sonnet 5 interfaces, 16- vs 64-candidate designs and six pools. Typical sentences carry three to six numbers with qualifiers (e.g., l.249–259, l.308–315, l.377–406).
- The same quantity takes different values within a few pages:
  - Qwen2.5-14B's k-pool AUROC fall is 0.17 in Sec. 5 l.252 and Fig. 2b (exact scorer), but −0.13 in Table 2 (original scorer).
  - Qwen2.5-7B's k-pool accuracy loss is 30.3 at l.378 but −24.2 in Table 2.
  - The MACE single-answer gain is "26 to 29" at l.373 but +32.4 in Tables 24 and 45.
  - MATH-500's reference is the final answer only in Fig. 2a but the full solution in Table 2.
- Each difference is explained somewhere, but a skimming reviewer sees contradictions.
- Fix, a restructure with no new experiments:
  1. **One scorer in the main text.** App. O l.2047–2051 says the stored score files keep both exact and original values for Qwen2.5-7B (all pools), and for Qwen2.5-14B, gemma-2-9b and Mistral-7B on the k-pool. So recompute Table 2's *Reference* and *Max rule* rows under the exact scorer. Keep only the blind-then-reveal row on the original scorer, flagged, or move that row to App. M with one sentence in the text. Blind-then-reveal was the registered mitigation and it failed on grading, so a single sentence reporting that is enough.
  2. **One conventions paragraph.** State once in Sec. 3: "Unless stated, constructed pools use any-format labels, open judges use the exact scorer, and Sonnet 5 numbers are API." Then delete the in-line qualifiers.
  3. **Fewer numbers per result.** Keep one headline number per result in the prose and let the figure carry the rest. Sec. 5 "Several correct answers" (l.247–259) can go from about 25 numbers to about 8.
  4. **Compress the registration accounting.** Cut the tally in Sec. 3 l.207–215 to two sentences ("The OSF primary endpoint, best-of-64 inflation, was confirmed (+1.19 SD; App. D). App. B lists all 156 registered predictions with outcomes."). Move the 92/25/16/18/2/3 breakdown to App. B.

### SHOULD FIX (accuracy of secondary claims)

**S1. The GPT-4.1 verdict hides a false-rejection rise as large as phi-4's.** Sec. 5 verdict l.262 says "for GPT-4.1 the effect is small", and Limitations l.458–459 calls it "a much weaker effect". Table 15 shows GPT-4.1 replication false rejections rising **+6.4 [+4.0, +9.1]** pp, the same as phi-4 (+6.6). The effect is small in AUROC (−0.04) and null on the k-pool (+1.2). Fix: "for GPT-4.1 the AUROC fall is small, although its false rejections on the replication pool rise by 6 pp, as phi-4's do." Also l.257–258: "although its scores tie so often that they rank candidates poorly" should read "possibly because its scores tie so often".

**S2. Scorer mixing in Sec. 7 "Natural data".** l.373–375: "The gains of 26 to 29 pp ... raises accuracy by 9 to 11 pp (Table 2)". The 29 and the 9 are exact-scorer values (Table 50: 29.4, +9.0). Table 2, which is cited, shows +9.8 and +11.3, and Tables 24 and 45 show +32.4. Cite Table 50, or, after M8.1, use one scorer.

**S3. Table 2 caption promises intervals that are not there.** "intervals are in Table 37": Table 37 gives CIs for AUROC and for *differences from the reference*. It gives none for the max-rule and reveal accuracy changes *against blind* on MACE and MATH-500. Add those CIs to Table 37, since they come from the same bootstrap, or state where they are.

**S4. "Our constructed k-pool cannot test this" (l.243–245) gives no reason.** Say why: presumably, once answers are read in any format, the blind picks on in-band k=1 tasks are already correct (Table 13 any-format k=1: all +0.0 [+0.0, +0.0]). Also say that the registered-label k=1 losses (−21.4 for Qwen2.5-7B) were label artifacts.

**S5. Ethics statement overstates the downstream risk.** l.502–504: "A model optimized against a reference-guided judge on multi-answer tasks may be rewarded for matching the reference". Your DPO runs did not show this (l.466–468). Add "though our three DPO runs did not show a policy learning to copy the reference (App. L)".

**S6. Definitions.**
- Sec. 3 l.201–203 defines grading AUROC only as non-matching correct against wrong. Fig. 2b, Table 2 and Table 37 use all-correct against wrong for one-answer tasks. Define both in Sec. 3.
- Sec. 2 l.155–156 uses "per-task blind AUROC" before Sec. 3 defines AUROC.
- The "completeness audit" (l.165) is passed with a 2.3–8.1% miss rate and failed at 30.8–43.5% (App. G). State the threshold.
- "exact scorer.‡" appears in the Fig. 1 caption (p.1) before it is defined. Drop it from the caption, or write "(scorer details: Sec. 3)".

**S7. Appendix tables that contradict the main-text labels.**
- Table 36 does not name its labeling. Its k-pool max-rule cells (+0.0, +2.6, −2.6, +0.0) and reference cells (−30.8, …) are registered labels on 39 tasks. Table 2 gives +3.0, +3.0, +0.0, +3.0 on 33 any-format tasks. Add "registered labels, 39 tasks" to the caption.
- Table 38 (worst-case loss) is built on the registered labels that Sec. 7 l.401–402 says were "mostly prose answers counted as wrong". Recompute it with any-format labels or say so in the caption.
- Figure 6a labels MATH-500 grading "not defined (one correct answer)". Table 2 and Table 37 define it (+0.29, +0.30). Use the same definition in both.

### POLISH

- **P1. Section 5 order.** The section titled "With several correct answers, the others are graded worse" opens with "One correct answer" (l.240). Put "Several correct answers" first and close with a one-paragraph "With one correct answer (P2′)".
- **P2. Figure 2 placement.** Figure 2 is a full-page float that splits the P3 paragraph mid-sentence ("94% | of the time", l.269 → l.307). Anchor it at the top of p.5, or move the P3 opening so the paragraph starts on p.6.
- **P3. Table 1 cells are 5–7 lines.** Aim for at most 3 lines per cell, one number per cell, with detail in the section text. The P3 cell mixes CLI and API results. Keep only the acceptance number (19% vs 0%) and point to Sec. 6.
- **P4. Abstract density.** The abstract has about 12 numbers. Suggested sentence 3: "Correct answers that differ from the reference are rejected far more often (28% vs 0.4% for Qwen2.5-7B) and are separated worse from wrong answers (AUROC −0.17 to −0.27 for four open judges on constructed pools)." Drop the Sonnet 5 and GPT-4.1 AUROC ranges from the abstract.
- **P5. Typos and style.**
  - l.484 "gave up up to" → "gave up as much as".
  - l.227 uses "31" as the example while Fig. 1 uses 35/80. Either is fine, but one running example reads better.
  - l.60 "moves correct text by about 5 points": Fig. 1c shows +5.3 and −5.4; say "about 5 points in either direction".
- **P6. Appendix naming.** The appendix renames the swap test "rotation", the margin "anchoring margin", and the rubrics a/b (l.651–652). Use the main-text names in the appendix prose and tables, and keep the registration names only in the ledger (Table 4), with a one-line mapping.
- **P7. Appendix order and floats.**
  - The appendix order (A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P) does not follow the main text. Sec. 6 depends on N and O, which sit after unrelated K and L. Put the main-text-supporting appendices first, in section order, then the "additional registered studies" (F, I, K, L, P).
  - Table 27 floats alone on p.30, eight pages before Table 44, which it documents. Table 49 appears after Table 50. Pages 29, 41 and 43 are mostly blank. Use `[p]` float pages or place tables next to their text.
- **P8. Related work.** The judge-bias paragraph (l.439–444) could cite Koo et al. (2023, "Benchmarking Cognitive Biases in LLMs as Evaluators") and Ye et al. (ICLR 2025, "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge"). Both catalogue judge biases and neither varies the reference among correct answers, which sharpens your novelty claim at l.100–102.
- **P9. Interpretation of the thinking results.** App. C l.1015 shows Qwen3-8B with thinking gives a 10 to 96.2% of valid arithmetic answers blind. One clause in Sec. 6 ("thinking judges score nearly all correct arithmetic answers 10 blind, and they keep those scores when the reference moves off them") would pre-empt the obvious "ceiling" objection that App. N already answers.

---

## 4. Figure-by-figure and table-by-table critique

**Figure 1 (p.1). Earns its place; at the bar.** Panels a → b → c tell the story in five seconds: the task, the same text under three prompts, then the pool. The "matches neither" bar is the right control and is visible. Fonts are about 7–8 pt and legible in print; the colors separate. Minor points:
- Panel b's grey subtext adds a second statistic (false rejections, 0.4% → 28%) that competes with panel c's swap. Consider moving it to the caption.
- The caption's final "exact scorer.‡" is jargon on page 1.
- The caption stands alone.

**Table 1 (p.3). A good idea; too wordy, and two cells contradict themselves.**
- The Prediction / Tests / Observed / Verdict structure is exactly what a skimming reviewer wants.
- The Observed cells run to 7 lines, and the marks are inconsistent (M3a–c).
- The P1 verdict "Holds unless the judge reasons first" contradicts its own Observed cell (M1).
- The "Not predicted" row is valuable and should stay.
- Target: at most 3 lines per cell, one number each.

**Figure 2 (p.6). Needed, but heavier to read than necessary.**
- The one-answer vs several-answer contrast is the paper's second key idea and belongs in the main text.
- Panels a and b list different pools and judges in different orders, and panel a has an empty lower third. Figure 6 in the appendix already solves this with aligned rows; use that layout here (rows = pool × judge, same in both panels, blanks where undefined).
- The title is long and accurate.
- Grey boxed-only ticks are legible. Tick labels are about 7–8 pt, fine.
- The caption's last sentence (registration status of five subsets) is necessary but hard to parse. After M3, replace it with per-row marks on the y-axis labels.

**Figure 3 (p.7). Good figure; wrong title.**
- Panel a is clear, and the within-group comparison is disclosed.
- Panel b's paired bars are easy to read.
- The title claims more than panel a shows (M1).
- The legend below the panels is 7.6 pt, fine.
- The caption line "Sonnet 5's reduction is not distinguishable from zero" should also appear in the title's wording.

**Table 2 (p.8). Important, but packs in too much.**
- It has 8 data columns, 3 pools with two AUROC definitions, the original scorer (unlike the rest of the main text), and an 11-line caption.
- The blind-then-reveal row is a failed registered protocol. One sentence in the text plus App. M would do, which removes a third of the table.
- Consider replotting the max-rule vs reference comparison as a small dot plot (accuracy and AUROC, per pool) with CIs. The table currently has no CIs and points to a table that lacks some of them (S3).
- The title "at a cost with a unique answer" is well chosen and honest.

**Appendix figures and tables (spot check).**
- Fig. 4: fine.
- Fig. 5: shows the preregistered primary endpoint and is buried on p.22. Acceptable, since Sec. 3 explains why the text leads with other measures.
- Fig. 6: good aligned design; fix "not defined" (S7).
- Fig. 7: fine.
- Fig. 8: fine.
- Fig. 9: fine.
- Tables 13–15: the key robustness tables and well built.
- Table 50 ("numbers quoted in the main text that appear in no other table"): very helpful for verification. Keep it.
- Table 36: missing its labeling (S7).
- Table 38: built on the disowned labels (S7).

---

## 5. What is already at the bar and should be left alone

- **Title and single question.** "The reference is not an answer key" is one clear, memorable claim, at the level of "Are Emergent Abilities a Mirage?".
- **The core design.** Byte-identical text, reference swapped, a "matches neither" control, and program-enumerated answer sets. This is the kind of clean manipulation reviewers reward.
- **Figure 1** as the concept figure.
- **The three-readings framing with P1/P2/P3**, the argument that only P3 separates verification failure from agreement, and the note that Eq. (1) "organizes the predictions; it is not a fitted model".
- **Honest scoping.** "These tests are arithmetic only" (l.231); "We did not run the swap test on GPT-4.1" (l.225–226); "We did not measure how often Sonnet 5 would move a blind 10 that far on a second blind scoring" (l.313). Keep all of these.
- **The selection-harm explanation.** Losses sit where no correct candidate matches the reference (l.403–406: 64 pp vs at most 14 pp). This is the most useful practical finding in the paper and is stated cleanly.
- **The masking result** (l.227–231): string-level evidence for the mechanism, reported with restraint.
- **The Limitations section**: prominent, specific, and it includes the retroactive verdict rule and the failed DPO manipulation check.
- **The ledger (App. B, Table 4)** and the disclosure that the primary endpoint is not what the text leads with (l.207–211).
- **The page budget**: the main text ends on p.9.
- **The prevalence audit disclosure**: LLM-labeled, not human-checked, with the NQ-open time-varying exclusion.

---

## 6. What would move the score, without new experiments

**From 6 to 7: fix every must-fix item.**
1. Rewrite the four claims that go beyond the evidence: reasoning (M1), protocol (M4), MT-Bench (M5), and the conclusion's inference (M6). Calibrate the P3 verdict (M7).
2. Correct the AUROC range in the abstract and Table 1 (M2).
3. Apply one registration-mark rule across the abstract, Table 1, figure captions and appendix tables (M3a–e).
4. Use one scorer in the main text by recomputing Table 2's Reference and Max rows from the stored exact-scorer values, and put the conventions in one paragraph (M8.1–2).
5. Fix the GPT-4.1 verdict (S1) and the Table 2 interval pointer (S3).

**From 6 to 8: also rebuild the main text for skimmers.**
1. **Halve the numbers in the prose.** One headline number per result; figures carry the rest; the Sec. 3 registration tally goes to App. B (M8.3–4). Target no more than 10 registration marks in the main text by putting marks on figure rows and table cells instead of in sentences.
2. **Put Figure 2's two panels on aligned rows**, and turn Table 2 into a slim max-rule vs reference comparison with CIs, with blind-then-reveal as one sentence.
3. **Reorder Section 5** (several answers first) and give each of Sections 4–7 a one-sentence takeaway at the start, before any numbers.
4. **Strengthen P3 with existing data.** Report a noise floor from the Sonnet 5 CLI/API paired blind calls if they exist (M7). Add the thinking-judge ceiling clause (P9).
5. **End with a short "what practitioners should do" paragraph** in the conclusion, drawn from results already in hand:
   - grading with a reference on multi-answer tasks: use the max rule;
   - best-of-n selection: safe when some candidate matches the reference, not otherwise;
   - thinking judges: help on arithmetic, not on factual questions;
   - unique-answer tasks: keep the reference.
6. **Reorder the appendix** to follow the main text, use main-text names, and fix float placement (P6, P7).

None of these needs a new model call. The only item that depends on data availability is the M7 noise-floor re-analysis; if the paired calls are not blind, the fallback is the calibrated wording given in M7.
