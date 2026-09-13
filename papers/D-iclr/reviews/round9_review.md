# Round 9 review: "The Reference Is Not an Answer Key: LLM Judges Grade Agreement with One Correct Answer"

Reviewer role: senior reviewer / area chair, ICLR 2027 main track. Read: `reviews/round9_main.pdf` (all 37 pages), `main.tex`, `figures/fig1_concept.tex`, the table sources behind Tables 2, 25, 28, 48, `scripts/make_figures.py` (Figures 1c, 3, 4), `analysis/r8_sonnet_results.json`, `analysis/r8_lenient_results.json`, `analysis/r4_results.json`, and `registration_round8.md`. Earlier reviews were not opened.

---

## Summary

The paper argues that when a question has several correct answers, an LLM judge shown a reference answer does not treat it as an answer key but rewards agreement with that one answer. From a one-line model (Eq. 1: referenced score = beta x blind score + lambda x [answer matches reference]) it derives three predictions. P1: swapping which correct answer is the reference moves the score of byte-identical text, by 2.7 to 5.4 points out of 10 for Qwen2.5-7B, phi-4 and Claude Sonnet 5. P2: the harm switches on at k > 1 correct answers. Evidence: best-of-64 "inflation" on constructed pools with exactly k answers and on MACE factual questions, plus a drop in AUROC for correct answers that differ from the reference. P3: the effect survives restricting to answers the judge already accepted, frontier scale, and reasoning; reasoning removes it on arithmetic but not on factual questions. A cost section reports that the preregistered selection inflation (+1.19 SD) mostly does not become an accuracy loss once answers in any format are credited, that code references do not inflate, and that a blind-then-reveal protocol removes the inflation for the two OSF judges. The work is unusually careful and transparent: 156 registered predictions with a full ledger, including 25 failures. The core swap test (P1) is clean, novel, and convincing. The paper is not yet a clean paper, though. The abstract, Table 1, and the conclusion claim more than the evidence supports in at least five places; P2 and P3 each contain failed or contradicted results that are reported only in the appendix; the registration superscripts clutter every sentence while blurring prospective and known-direction analyses; and the main figures are below print legibility and use three different meanings for "hollow marker".

## Scores

- **Overall: 5 / 10** (marginally below the acceptance threshold)
- **Presentation: 2 / 4**
- **Soundness: 3 / 4**
- **Contribution: 3 / 4**
- **Confidence: 4 / 5**

**Would I champion this at 8+? No.**

I would champion it if all of the following were true in the submitted PDF, none of which needs new model calls:

1. Every sentence in the abstract, Table 1, and the conclusion survives a claim-by-claim check against the appendix tables. Concretely: the blind-then-reveal claim is scoped to the judges and pools where it holds; "the reference helps on single-answer questions" is qualified by the k-pool k=1 result; "grading gets worse under every way of reading answers" is corrected (boxed-only, GPT-4.1, Mistral-7B); and the AUROC range is corrected.
2. Table 1 gains a verdict column, and each failed or mixed prediction appears in the row and the section where the claim is made, not only in Appendix B.
3. The preregistered inflation endpoint is recomputed under the any-format labels (existing data), or the +1.19 SD claim is explicitly scoped to labels that count 682 correct replies as wrong.
4. P3 is restated so that its reasoning result is reported as a partial falsification rather than absorbed into the prediction.
5. The inline OSF/PRE/PH superscripts are removed from running text and captions, replaced by an evidence column in Table 1 and a single marker for post hoc claims. Known-direction re-analyses get their own label.
6. Figures 1, 3, and 4 are re-plotted at final size with all text at 7 pt or larger and one consistent marker/color grammar. Figure 1 also shows the blind-vs-referenced contrast and the k switch, not only the swap test.
7. The title no longer misparses as "questions with one correct answer".

With those fixes I would move to 7. An 8 would additionally need the introduction to state the three results with numbers on page 1–2, the way the Mirage paper does, and Section 2's model claim to be scoped (see Should-fix 7).

---

## Strengths

1. **The swap test is the right experiment, and it is clean.** Byte-identical candidate text, two correct references, and a score change of +5.25 / −5.41 (Qwen2.5-7B, exact scorer; verified in `r4_results.json`: gainer 5.2507, loser −5.4051, placebo +0.12), +4.09 / −3.92 (phi-4), and +3.04 / −2.66 (Sonnet 5), with the "matches neither" control near zero. No confound from answer quality is possible. This is the kind of result that belongs on page 1, and it is there.
2. **The masking suite (Table 28) isolates what "agreement" means.** Words keep the margin, "30+1" cuts it by 77–94%, a worked solution with the answer masked removes it. This is a real mechanism result and it is well designed.
3. **Transparency is exceptional.** A 156-prediction ledger with explicit re-derivation of verdicts, disclosure that the verdict rule was adopted after most outcomes were known, disclosure of a partial peek before the Sonnet 5 amendment (`registration_round8.md`, Amendment 1), an excluded contaminated CLI run (Appendix H), and a limitations section that says "we have not shown that training exploits the bias". Few papers at any venue are this honest.
4. **Breadth of judges and task types.** Open judges from 1.5B to 14B, two frontier API judges, thinking toggles on the same weights (Qwen3-8B/14B), natural factual data (MACE, with an answer-list completeness audit), unique-answer MATH-500 as the k=1 contrast, and code.
5. **Negative results are informative and kept.** The MBPP code result (a canonical program lowers inflation), the falsified distance gradient, and the MACE end-to-end failure of blind-then-reveal are all reported and make the paper more credible.
6. **The practical message is useful.** A reference helps on unique answers and hurts on multi-answer tasks, grading suffers more than selection, and scoring blind first is a cheap mitigation. Practitioners building RL verifiers and eval harnesses need to hear exactly this, once it is scoped correctly.

---

## Must-fix before submission (ranked)

### 1. The mitigation is overclaimed in the abstract, Table 1, and the conclusion

**Where.** Abstract, last sentence: "scoring blind before revealing the reference removes the selection inflation we preregistered." Table 1, "Cost and fix" row: "scoring blind first removes the inflation." Section 10: "otherwise score blind first and reveal the reference only afterwards." Section 7, "What removes it": "while wording it as someone else's score changes little."

**What is wrong.**
- Blind-then-reveal removes the inflation for the two OSF judges only: −0.05 and +0.16 SD at k > 1, Table 11. In the OSF-registered judge-coverage extension (Table 38), gemma-2-9b keeps +1.23 SD against +1.43 with the reference alone, and Qwen2.5-14B keeps +0.23 [+0.10, +0.37], an interval that excludes zero.
- On MACE, the only natural multi-answer data, the registered prediction that blind-then-reveal beats the reference at k > 1 was not confirmed for either judge. The prediction that it is at least as accurate over the natural mix was falsified for both. Table 43: 88.7% vs 91.7% (Qwen2.5-7B), 94.0% vs 95.5% (phi-4).
- Under the registered checker and original scorer, blind-then-reveal still loses 10.3, 15.4, and 12.8 accuracy points against blind at k > 1 for Qwen2.5-7B, phi-4, and gemma-2-9b (Table 36). The main text cites only the post hoc any-format relabeling ("stay within 6 points"), where phi-4 is in fact −6.1.
- "Wording it as someone else's score changes little" hides two failed predictions. The neutral-wording equivalence was falsified for Qwen2.5-7B (+0.53 [+0.29, +0.80] against +0.01). Another judge's score gives +0.38 [+0.12, +0.60] against +0.01 for Qwen2.5-7B, and was registered and falsified for gemma-2-9b (Table 4, "Variants on gemma-2-9b").

The conclusion's recommendation is therefore not supported on the one natural data set tested.

**Fix.**
- Abstract: replace the last sentence with: "Scoring blind before revealing the reference removes the added inflation for Qwen2.5-7B and phi-4 but only partly for Qwen2.5-14B and gemma-2-9b, and on natural factual questions it was less accurate than simply showing the reference."
- Table 1: "blind-then-reveal removes the inflation for 2 of 4 judges; falsified on MACE."
- Conclusion: "When correct answers can differ from the reference, check them against the task's answer set where one exists. Scoring blind first reduced the added inflation for every open judge we tested, but did not improve accuracy on natural factual questions, so it should be validated per judge and domain."
- Section 7: replace "while wording it as someone else's score changes little (Table 39)" with "wording it as someone else's score keeps part of the protection (+0.38 for Qwen2.5-7B; falsified for gemma-2-9b), and neutral wording costs Qwen2.5-7B +0.51, falsifying the equivalence we registered (Table 39)."
- Report the registered-checker accuracy of blind-then-reveal (Table 36) next to the any-format number.

### 2. P2 ("the reference helps with one correct answer and hurts with several") contradicts the constructed k=1 results, which appear only in the appendix

**Where.** Abstract: "the damage should begin exactly when a second correct answer exists; the reference helps on single-answer questions." Intro P2: "With one correct answer ... the reference should help." Figure 2 title: "The reference helps with one correct answer and hurts with several." Section 5.

**What is wrong.**
- **k = 1 on the preregistered k-pool.** The reference lowers Qwen2.5-7B's best-of-64 accuracy by 21.4 points [−43, +0] (Table 9, Table 45) and its overall AUROC by −0.07 [−0.12, −0.03]. It also lowers overall AUROC for Qwen2.5-14B (−0.03 [−0.06, −0.01]) and Mistral-7B (−0.06 [−0.10, −0.01]; accuracy −10.4 [−15, −5]). All in Table 48. Table 34 explains why: "through picks of wrong answers that contain the reference's text." So on the constructed pool the reference does not help at k = 1 for three of five judges. That finding is actually consistent with the agreement account, since string-matching lures are rewarded, but it contradicts P2 as worded and it is not in Section 5.
- **k > 1 on the synthetic grid.** The inflation step is positive for all six judges, but "the level pooled over k>1 is individually significant for three" (Table 12). Qwen2.5-1.5B +0.07 [−0.15, +0.26], Qwen2.5-14B +0.08 [−0.20, +0.36], and phi-4 +0.22 [−0.19, +0.65] do not show that the reference "hurts with several". Across the eight judge–pool pairs in Figure 2, the level at k > 1 excludes zero for five.
- **Labels.** Table 12's caption calls its step estimates a "Post-hoc paired re-analysis of a pre-specified grid", while Figure 2 and Table 1 mark the synthetic grid PRE.

**Fix.**
- Abstract: "Second, the damage should appear when a second correct answer exists: across eight judge–pool pairs the inflation the reference adds is higher at k>1 than at k=1, and on multi-answer questions correct answers that differ from the reference are graded worse by all seven judges we measured on at least one pool ..."
- Drop "exactly" and "the reference helps on single-answer questions", or scope the latter to "on MACE and MATH-500".
- Section 5, after "The switch": add "On our constructed k-pool the reference did not help at k=1: Qwen2.5-7B's accuracy fell by 21.4 points [−43, 0] because it picked wrong answers containing the reference's text (Table 34), which an agreement-grading judge would also do."
- Figure 2 title: "The inflation the reference adds is higher with several correct answers than with one."
- Make the PRE/PH label of the synthetic-grid step consistent between Figure 2, Table 1, and Table 12.

### 3. The grading claim is numerically wrong and omits the labeling that weakens it most

**Where.** Table 1, P2 row: "AUROC falls by 0.17–0.28 for four open judges under three ways of reading answers." Section 5: "−0.17 to −0.28 in any format". Figure 3 title: "Grading gets worse under every way of reading answers." Appendix D: "Grading gets worse under all four." Abstract: "for each of the seven judges we measured."

**What is wrong.** I checked `r8_lenient_results.json`, the G_nm change, against Table 14.
- *Any format* ranges from −0.17 (Qwen2.5-14B, k-pool, −0.1745) to −0.27 (Qwen2.5-7B, replication, −0.2747). It is not −0.28.
- *Model-read* reaches −0.16 (Qwen2.5-14B −0.1577; gemma-2-9b −0.1596).
- The *registered checker* reaches −0.33 (phi-4, k-pool, −0.3266).

So "0.17–0.28 under three ways" matches none of the three labelings.

More importantly, the fourth labeling in Table 14, *boxed only*, is missing from Figure 3 and from the main text. It cuts the drop by roughly two-thirds: −0.10 (Qwen2.5-7B, replication), −0.08 (phi-4), −0.07 (Qwen2.5-14B), and **+0.0075 [−0.05, +0.07] for Mistral-7B**. For GPT-4.1 on the k-pool, the interval includes zero under three of the four labelings (any format −0.015 [−0.037, +0.005]; model-read −0.013 [−0.031, +0.003]; boxed only −0.014 [−0.060, +0.019]). "Every way of reading answers" is therefore false for two of the seven judges, and the large attenuation on well-formatted replies deserves an explanation, because it suggests part of the drop involves unboxed replies. Mistral-7B is also silently dropped from Figure 3.

**Fix.**
- Table 1: "AUROC for correct answers that differ from the reference falls for all seven judges on at least one pool: by 0.16–0.33 for four open judges across three labelings (0.07–0.14 when only boxed replies are kept), by 0.04 for GPT-4.1, and from 0.94 to 0.78 for Sonnet 5 on factual questions."
- Figure 3 title: "Grading of correct answers that differ from the reference gets worse for every judge; the selection loss mostly does not survive crediting answers in any format."
- Add the boxed-only drop in one sentence in Section 5, and add Mistral-7B to Figure 3 or say in the caption why it is excluded (it failed the score-resolution screen).
- Fix Appendix D's "Grading gets worse under all four."

### 4. The preregistered primary endpoint was never recomputed under the corrected labels

**Where.** Section 7 "Selection" ("+1.19 SD [+1.03, +1.35]"), Table 1 cost row, Appendix A "Inflation".

**What is wrong.** Inflation permutes scores within validity classes and scores the pick against samples "of the same correctness" (Eq. 2). The paper itself shows the registered validity labels are wrong for about 9% of samples: 682 of 7,680 replication samples are correct but unboxed (Table 16). It also shows that the referenced judge "favors unboxed replies that state the reference's value, which that checker counts as wrong" (Section 7). That is precisely the case that inflates G: a correct, reference-matching reply labeled invalid, picked and scored high relative to "invalid" peers. `r8_lenient_results.json` contains AUROC, false-rejection, and accuracy under the any-format labels, but no inflation, and I found no analysis script that recomputes inflation under those labels. The robustness check offered (+0.90 on the top tercile of format compliance) is a subset, not a relabeling.

**Fix.** This is a new analysis of existing score files. Recompute inflation under the any-format and model-read labels for the replication pool and the k-pool, and report it next to +1.19 SD in Section 7 and in Table 1. If that cannot be done, add this sentence to Section 7 and qualify the Table 1 cost row: "Inflation is computed under the registered labels, which count 682 correct unboxed replies as wrong; we have not recomputed it under the any-format labels, and part of it may reflect those replies."

### 5. P3 is partly falsified by the paper's own data, and the text absorbs the failure instead of reporting it

**Where.** Intro P3: "If the judge merely did not know the other answer was correct, answers it had already accepted, a stronger judge, or time to reason should remove the effect." Section 6: "The one-sample reading predicts that none of them does." Section 6 heading: "it survives what should cure ignorance."

**What is wrong.**
- **Reasoning.** The paper's own prediction is that "none of them" removes the effect, yet reasoning does remove it on arithmetic: −0.69 → +0.01 (Qwen3-8B), −1.98 → −0.12 (Qwen3-14B), −2.85 → −0.20 (Sonnet 5). The text reframes this as "these judges check arithmetic and resist the pull." That is an ignorance-style explanation: the judge verifies when it can. Section 6 closes without a verdict, and Table 1 lists the arithmetic result under a heading that says the effect survives.
- **Already-accepted filter.** At t = 7, 96% of Qwen2.5-7B's samples are kept (Table 48), so the filter removes almost nothing and "nearly as much" is close to automatic. The t = 9 row (81% / 73% kept) is the informative one.
- **Factual questions.** Every item-level "already accepted" test is on arithmetic without thinking. The factual-question persistence is supported only at the population level ("Sonnet 5 ranks correct answers above wrong ones 94% of the time without a reference"), which does not show that the specific non-matching answers were ones the judge knew were correct.

**Fix.**
- Restate P3 as registered and give it a verdict. Intro P3: "**P3 Knowing the answer is correct should not protect it.** Answers the judge accepted blind, a stronger judge, and reasoning before scoring should not remove the effect."
- Close Section 6 with: "Verdict: P3 holds for prior acceptance and frontier scale and on factual questions with thinking, but fails for reasoning on arithmetic, where judges that can check the answer stop anchoring."
- Lead with the t = 9 filter and state the kept fraction in the sentence.
- Replace the heading "It survives what should cure ignorance" with "Prediction 3: prior acceptance, scale, and reasoning".
- If the R8 MACE Sonnet 5 files allow it, add the false-rejection rate among non-matching correct answers Sonnet scored ≥ 7 blind. That is an existing-data analysis and would close the item-level gap on factual questions.

### 6. Registration labels: inconsistent, misleading in two places, and visually overwhelming

**Where.** Throughout: 40+ inline superscripts in the main text, stacked as "OSFPREPH" and "OSFPRE" in Table 1 and Section 7; Table 1 P3 row; Figure 3 caption; Appendix B.

**What is wrong.**
- **PRE covers two different things.** It labels genuinely prospective predictions on data that did not exist, and also re-analyses "whose direction of effect was already known, such as the exact scorer" (Appendix B). Examples: the k-pool registered-checker accuracy loss (Table 13), registered after the original-scorer accuracy readout (Table 9) was seen post hoc, and the Qwen2.5-7B exact-scorer rotation in Figure 1c. Superscripts in the main text do not distinguish these, so they overstate registration strength. Appendix B says "the ledger names them", but Table 4 does not mark them.
- **Table 1, P3 row, is marked PRE only**, but its range "12.5–63.8 points" takes its upper end from post hoc cells: Table 2 marks Qwen2.5-7B factual +63.8 and phi-4 factual +54.4 PH.
- **The Figure 3 caption** says "Registered-checker values for ... Sonnet 5 are pre-specified; the other labelings are post hoc." `registration_round8.md` makes the format-lenient labels the primary registered labels for Sonnet 5 on the replication pool and k-pool, and Table 25 marks them PRE. The caption therefore mislabels Sonnet 5's any-format values as post hoc.
- **Clutter.** The superscripts make every sentence harder to read and are the paper's most visible "ledger-speak".

**Fix.**
- Remove superscripts from the abstract, captions, and running text.
- Add an "Evidence" column to Table 1 with one of four labels. Add a fifth marker for re-analyses of existing data where the direction was known ("RE"), and apply it in Table 4.
- In running text, mark only post hoc claims, with one sentence in Setup: "Unmarked claims in the main text are preregistered or pre-specified; claims marked † are post hoc; Table 1 gives the status of each."
- Correct the P3 row label to PRE/PH and the Figure 3 caption.

### 7. The title misparses in the direction opposite to the paper's claim

**Where.** Title: "LLM Judges Grade Agreement with One Correct Answer."

**What is wrong.** Readers will parse "with One Correct Answer" as describing questions that have one correct answer, the regime where the paper shows the reference *helps*. The title also states the claim universally, while the paper shows it fails for programs and for reasoning judges on arithmetic.

**Fix.** Keep the first half and scope the second, for example: "The Reference Is Not an Answer Key: When Several Answers Are Correct, LLM Judges Reward Matching the One They Are Shown." A shorter option: "The Reference Is Not an Answer Key: LLM Judges Reward Matching the Reference on Multi-Answer Questions."

### 8. Main-text figures are below print legibility, and Figure 4 has a clipped axis label

**Where.** Figure 1c, Figure 3, Figure 4 (pages 1, 5, 6).

**What is wrong.** Effective font sizes computed from `make_figures.py` and the inclusion widths:
- **Figure 1c.** Drawn 2.3 in wide, placed at 4.6 cm inside a TikZ picture about 13.2 cm wide, then resized to `\textwidth`, for a net scale of about 0.83. Tick labels (7.2 pt) print at about 6.0 pt, bar value labels and the legend (7 pt) at about 5.8 pt, and the y-label (7.4 pt) at about 6.1 pt. Meanwhile the TikZ text in panels a and b prints at about 8.5 pt, so the data panel, the one with the result, is the least legible part of the page-1 figure.
- **Figure 4.** Drawn 5.9 in wide, placed at 0.94 of `\textwidth` (5.17 in), for a scale of about 0.88. The 7 pt and 6.8 pt labels print at about 6.0 pt. In the round-9 PDF, panel b's x-label is clipped to "added margin, reference minus blir". The figure file was regenerated after this PDF, so check the final build.
- **Figure 3.** Scale about 0.92. "not defined (one correct answer)" prints at 6.3 pt, the legend at 6.5 pt, and row labels at 6.6 pt.

**Fix.** Set each matplotlib `figsize` to the exact final inclusion width (Figure 1c: 4.6 cm × 1.058, about 1.9 in; Figures 3 and 4: 5.17 in) and use no font below 7 pt after scaling. In Figure 1, include panel c at 100% scale rather than shrinking it into the TikZ picture. Re-check every axis label after `tight_layout`.

### 9. The judge and family counts in the introduction are wrong

**Where.** Section 1: "with nine judges from four model families." Abstract: "each of the seven judges we measured."

**What is wrong.** The main text uses at least twelve judges: Qwen2.5 1.5B/3B/7B/14B, phi-4, gemma-2-9b, Llama-3.1-8B, Mistral-7B, Qwen3-8B/14B, Claude Sonnet 5, and GPT-4.1. Appendix M adds Ministral-8B. They come from seven developers (Alibaba, Microsoft, Google, Meta, Mistral, Anthropic, OpenAI). Nine and four fit no grouping I can reconstruct, and "seven judges" in the abstract refers to a different subset without saying which.

**Fix.** "with twelve judges from seven developers (Appendix A)". In the abstract: "for all seven judges we measured grading with wrong answers, including Sonnet 5 ..."

### 10. The code result is misdescribed and uses the paper's key term backwards

**Where.** Table 1 cost row: "no anchoring on programs (a falsified prediction)". Section 7 "Where it stops": "We registered the prediction that a canonical program shown as the reference on MBPP would inflate like an answer key."

**What is wrong.**
- **Terminology.** In this paper an "answer key" is the reading under which the reference does *not* inflate, so "would inflate like an answer key" says the opposite of what is meant.
- **"No anchoring."** The paper did not measure a margin on MBPP. On the answer-format continuum, the anchoring margin in the program format is positive (+0.64 and +0.88, n = 19; Table 31). What fell was added inflation, not anchoring.
- **Confound.** The continuum's decline is confounded with the effective number of answers: "Program outputs cluster (a median of two distinct returned lists per task)", and the pair and JSON formats had 7 and 1 usable tasks. Yet the text concludes "the effect needs an answer the judge can read off and compare."

**Fix.**
- Section 7: "We registered the prediction that MBPP's canonical program, shown as the reference, would add inflation the way a stated answer does, while a test suite would not. It was falsified: ..."
- Table 1: "a canonical program adds no inflation (a falsified prediction)".
- After the continuum numbers, add: "Program outputs have few distinct correct values per task, so this decline cannot be separated from a smaller effective k."

---

## Should-fix (ranked)

### 1. Marker and color meanings change from figure to figure

**Where.** Figures 1–4 and 8.

**What is wrong.** Hollow means k = 1 in Figure 2, "registered checker" in Figure 3, and "thinking on" in Figure 4. Filled black means "reference moved onto" in Figure 1c, "any format" in Figure 3, and "thinking off" in Figure 4b. Orange = blind and blue = reference in Figures 5, 6, and 8, but blue means "any k" in Figure 2. In Figure 3 the MACE and MATH-500 rows are drawn with the filled "answers read in any format" marker, although MACE uses the oracle answer lists and MATH-500 has unique answers (`make_figures.py` lines 448–453 put them in the `"lenient"` slot).

**Fix.** Fix one grammar for the whole paper: orange = blind, blue = referenced, gray = control, filled = main estimate, hollow = the sensitivity condition. State it once in Figure 1's caption. In Figure 3, give MACE and MATH-500 their own legend entry ("answer list").

### 2. Figure 1 shows the swap test but not the method behind most of the paper

**Where.** Figure 1.

**What is wrong.** Most results are "referenced minus blind" and depend on k, but Figure 1 has no blind arm and no k. A reader meets "blind", "inflation", "anchoring margin", and "k-pool" on pages 3–4 with no visual anchor. Panel b's prediction box floats below the schematic, and the example is invented, with no measured s7 or s13. The Mirage paper's schematic shows both the alternative explanation *and* how it produces the observed pattern.

**Fix.** Widen panel b into a two-row schematic:
- top row: blind vs. referenced scoring of the same candidate;
- bottom row: the swap.

Replace the invented example with a real replication-pool item and its actual blind, s7, and s13 scores (existing data). Optionally add a small panel d that shows Eq. 1's prediction, flat at k = 1 and a gap at k > 1, drawn next to the Figure 2 result. The page 2 space allows it.

### 3. Too many near-synonymous terms

**Where.** Setup and throughout.

**What is wrong.** The paper uses "swap change" in the main text but "rotation" in the appendix and ledger. Other near-duplicate sets:
- "anchoring margin", "added margin", "margin"
- "inflation", "added inflation"
- "exact scorer", "original scorer", "expected score", "sampled integer"
- "registered checker", "strict", "boxed answers", "boxed only"
- "any format", "lenient", "model-read"

The Figure 1 caption uses "exact scorer" before it is defined; the definition is in Appendix A.

**Fix.** Use one term per concept, and put a five-line glossary in Setup (swap change, anchoring margin, false-rejection rate, AUROC for non-matching answers, inflation). Rename "rotation" to "swap" in the appendix and ledger. Use a single scorer in the main text, with the other in the appendix, or define both in Setup in one sentence.

### 4. Inflation, the measure behind Figure 2, is hard to grasp

**Where.** Section 3 "Measurements"; Figure 2.

**What is wrong.** The definition takes three clauses and a permutation null. No reader will understand it in one pass, yet it is the only quantity in the key P2 figure.

**Fix.**
- Add one intuitive sentence, such as "Inflation is how much higher a second rubric scores the judge's pick than a typical answer of the same correctness; 1 SD means the pick is over-scored by one standard deviation."
- Add a second Figure 2 panel with the overall AUROC change at k = 1 vs. k > 1 on the k-pool and MACE. Those numbers already exist in Table 48 (for example, phi-4 +0.01 → −0.23; MACE Qwen2.5-7B +0.29 → +0.00); label them post hoc.

### 5. No results reach the reader before page 3

**Where.** Section 1, Table 1 placement.

**What is wrong.** The introduction ends with "Table 1 lists each test and its result," and Table 1 lands on page 3. Apart from Figure 1c, a reader who stops at page 2 has seen no number.

**Fix.** Float Table 1 to the top of page 2, or add three sentences after the P1–P3 list, one per prediction with its headline number and verdict. Model them on the Mirage paper's contribution paragraph.

### 6. The motivation leans on math grading, where multi-answer questions are rare

**Where.** Section 1.

**What is wrong.** The motivation cites MT-Bench's math template and reference-guided math grading. By the paper's own audit, multi-answer questions make up 0.0% of MATH-500 and 2.5% of GSM8K and DeepScaleR (Table 20), so the practical exposure there is small. The exposure is in factual QA (NQ-open 18.5–30%) and in "give an example" or construction tasks.

**Fix.** Add one sentence: "On curated math benchmarks such questions are rare (0–2.5% in our audit); the failure matters for factual QA, construction and example tasks, and open-ended generation, where several answers are the norm."

### 7. Section 2's model claim is stronger than the appendix supports

**Where.** Section 2, "reproduces the pattern of inflation across nine pool compositions out of sample".

**What is wrong.**
- **Missing term.** The fitted model in Appendix I has a lure term γ that Eq. 1 lacks, so the λ and β values quoted come from a different equation.
- **Weak fit.** The fit is a Spearman correlation over nine cells, with Qwen2.5-7B "at the 0.80 bar".
- **Omitted failure.** The direct composition prediction, that inflation grows with d, failed: it falls (Table 27). Section 2 does not mention this.

**Fix.** "An extended version with a term for wrong answers that contain the reference's text (Appendix I) gives λ = 4.3 and 3.5 and β = 0.51 and 0.69, and ranks nine held-out pool compositions at Spearman 0.80 and 0.85; its prediction that inflation grows with the number of matching correct answers failed."

### 8. Table 2 does not earn its main-text space

**Where.** Table 2, page 6.

**What is wrong.** Eight of 24 cells are "n/a" or "not run". The rows mix PRE and PH, and each column uses a different subset and scorer. The caption has to warn "compare within a row". Sonnet 5's API and CLI cells for the same factual contrast differ by a factor of two (+35.6 vs +17.5), with no explanation in the main text.

**Fix.** Move Table 2 to the appendix and keep one sentence in Section 6, or fold the factual false-rejection change into Figure 4b as a third bar group. Either way, add one clause explaining the API/CLI difference, or report only the API numbers.

### 9. Accuracy numbers in adjacent paragraphs use different scorers, and one judge is dropped

**Where.** Section 7, "Selection" and "What removes it".

**What is wrong.**
- **Different scorers.** "Selection" cites the Qwen2.5-7B any-format loss as −30.3 [−48.5, −12.1] (exact scorer, Table 13). "What removes it" cites Table 16, where the same contrast is −24.2 [−42.4, −6.1] (original scorer).
- **Dropped judge.** "At most 15 points with intervals reaching zero for the others" ignores Mistral-7B, whose any-format loss is −4.7 [−8.6, −0.8] (Table 13).

**Fix.** Use one scorer throughout Section 7. Either mention Mistral-7B or state why it is set aside (it failed the resolution screen).

### 10. The ledger count understates failures

**Where.** Section 1: "including the 25 that were not confirmed or were falsified."

**What is wrong.** A further 16 split predictions each contain at least one failed judge or arm.

**Fix.** "including 25 that were not confirmed or were falsified and 16 whose verdict differed across judges."

### 11. Headings are aphoristic, and sections do not close with verdicts

**Where.** Sections 4–7.

**What is wrong.** Headings such as "What 'agreement' means to the judge", "The switch", "Where it stops", "What removes it", and "It survives what should cure ignorance" (the intro says "would", the heading says "should") are clever rather than informative. Sections 4–6 open well with "Prediction." but end on a side result.

**Fix.** Use literal headings: "Rewriting the reference", "Tasks with one vs. several correct answers", "Code and answer format", "Blind-then-reveal". End each of Sections 4–6 with a one-sentence "Verdict:" line that matches Table 1's new verdict column.

### 12. Two different quantities share the same number

**Where.** Section 6 "Frontier judges" and Section 7 "Selection".

**What is wrong.** GPT-4.1's anchoring margin of +1.19 points sits a paragraph away from the replication inflation of +1.19 SD, which invites confusion.

**Fix.** Write out units every time ("+1.19 points on the 0–10 scale"), or cite GPT-4.1's picks (32 vs 1) first.

### 13. Related work is missing reference-guided judge designs

**Where.** Section 8.

**What is wrong.** Judge models trained with reference answers as input (JudgeLM, which studies "reference support" and "reference drop"; Prometheus) are the most direct design context and are not discussed. Neither is the NLG literature on multi-reference evaluation.

**Fix.** Add two sentences positioning the swap test against these designs.

---

## Nits

- MATH-500 accuracy gain: Section 5 says "28.6 to 30.5 points, even when it shows only the final answer". Table 46 and `r4_results.json` give 28.6–30.6 (answer-only, 14B, +30.64). Table 1 says "29–31"; Tables 21 and 35 give +27.6 for 14B with the other scorer. Use one scorer and one range.
- Section 7: "stay within 6 points of blind accuracy", but phi-4 is −6.1 (Table 16).
- MACE is never expanded or described in one phrase at first use.
- Figure 1c's legend entry "answer matches neither" has no counterpart in panel b; either add it to b or explain it in the caption.
- Figure 1's example candidate text contains both "7" and "13". That is fine, and even helpful, since it rules out character matching, but say so in the caption, because a careful reader will wonder.
- Figure 3's "Sonnet 5*" asterisk ("best of 16") also appears on the grading rows, where it is not the relevant caveat.
- Figure 4a's italic group labels "expected score" and "sampled integer" are opaque without Appendix A. Replace them with "open judges" and "API / command-line judges".
- Figure 2 lists the synthetic grid before the preregistered k-pool. Put the OSF k-pool first; it is the stronger evidence.
- Table 25: blind 0.94, referenced 0.78, change −0.15. Readers will compute −0.16. Show three decimals (0.938 → 0.785) or add a footnote on rounding.
- The abstract's second-prediction sentence runs about 60 words. Split it.
- Appendix B refers to internal IDs (P-R2B1, P-FM3, ...) that do not appear in Table 4, so a reader cannot cross-reference them. Add an ID column or drop the IDs.
- Page 11 is nearly blank after the references. Harmless, but check float placement.
- "Reference answer (trusted)" appears in the prompt. Say once in Section 3 that the word "trusted" was held constant, since it plausibly strengthens deference.
- Section 3: "38% of replies ignore the format". The two pools are 38.4% and 42.9% (Table 16); say "38–43%".

---

## Questions for authors

1. What is the replication-pool and k-pool inflation (the OSF primary endpoint) under the any-format and model-read labels? Does +1.19 SD survive?
2. Why does keeping only boxed replies cut the drop in grading AUROC by about two-thirds (for example −0.27 → −0.10 for Qwen2.5-7B)? Does the referenced judge penalize unboxed correct answers more than boxed ones, independent of matching?
3. On the R8 MACE subsamples, among correct non-matching answers that Sonnet 5 scored at least 7 blind, what is the false-rejection rate with the reference? That would test P3 at the item level on factual questions.
4. At k = 1 on the k-pool, does the lure term γ in the Appendix I model quantitatively predict Qwen2.5-7B's −21.4-point accuracy loss?
5. Sonnet 5's factual false-rejection increase is +35.6 through the API but +17.5 through the CLI score-only arm. What differs besides the interface (subsample design, one answer per group, thinking defaults), and which should readers treat as the estimate?
6. The Sonnet 5 subsamples were redrawn until they held at least one matching-correct, one non-matching-correct, and one wrong answer. How comparable are those AUROCs to the 64-candidate open-judge AUROCs?
7. For the answer-format continuum, can you stratify tasks by the number of distinct correct outputs to separate format from effective k?
8. On MACE, does the grading drop grow from k = 2 to k = 6, as Eq. 1 with a fixed λ and more non-matching correct answers would suggest?
9. Blind-then-reveal shows the judge its own blind score. Is the protection simply that judges copy a displayed number? Table 39 suggests yes (another judge's score also works for phi-4). If so, does the "max rule" dominate it at half the conceptual complexity, and why recommend blind-then-reveal in the conclusion rather than the max rule?

---

## ICLR compliance

- **Length.** The main text ends on page 8, within the 9-page limit. The AI-use, ethics, and reproducibility statements are present.
- **Anonymity.** The PDF says "Anonymous authors", and OSF links are withheld. I grepped the full `supplement.zip` content for author and lab names and found none.
- **Informal wording.** Appendix H ("stopped at the account's spend limit") and the registration amendment ("the account owner's authorization") are informal but not identifying.
- **LLM-use disclosure.** Present and specific, including that the prevalence labels came from one model family and were not checked by humans.
