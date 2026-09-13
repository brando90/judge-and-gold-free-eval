# Round 12 review: "The Reference Is Not an Answer Key: LLM Judges Reward Agreement When Several Answers Are Correct"

Reviewer role: NeurIPS reviewer / ICLR area chair. Sources: `reviews/round12_main.pdf` (all 41 pages), `main.tex`, `appendix.tex`, `figures/fig1_concept.tex`, `tables/*.tex`, `scripts/make_figures.py`, and `analysis/{r11_p3_checks, r9_inflation_relabeled, r9_inflation_relabeled_kpool, r9_sonnet_item_level, r8_sonnet_results, r8_lenient_results, r4_results, r5_sonnet_mace_results, r3_mace_accuracy_results}.json`. Registration status was checked against `registration_round{3,4,5,8}.md`. I did not open earlier reviews or the supplement.

---

## Summary

The paper asks whether an LLM judge treats a reference answer as an answer key when a question has several correct answers. The core manipulation is a clean *swap test*. Byte-identical candidate text is re-scored with the reference moved from one correct answer to another. The text gains 3.0 to 5.3 points out of 10 when the reference moves onto its answer and loses 2.7 to 5.4 when it moves off (Qwen2.5-7B, phi-4, Sonnet 5). Correct text that matches neither reference barely moves. The paper frames three readings of a reference (answer key, verification failure, agreement) and three predictions:
- **P1:** the score follows the reference. It holds.
- **P2:** with one correct answer the reference helps; with several, correct answers that differ from it are graded worse. It holds for grading.
- **P3:** the effect is not only a failure to verify. It "partly holds".

A fourth section reports that the grading harm does not become a selection harm on natural multi-answer questions (MACE). A 156-prediction ledger, several relabelings, and a long appendix back all of this.

The empirical core (P1) is sound, large, and a useful diagnostic. The paper does not yet meet the "Mirage" standard it aims at, for five reasons:
- Figure 1 has a rendering bug that hides the very text it says is "the same", and it does not depict the readings at all.
- The readings matrix contains exactly one cell that can separate the proposed "agreement" reading from verification failure, and that cell comes out split.
- Several headline sentences in the abstract, the verdict lines, and the conclusion claim more than the tables show.
- A handful of registration marks are wrong.
- Pages 1–3 repeat the same numbers five times in five formats, while Section 7 leans on an opaque endpoint that the paper itself concedes is implied by P1.

---

## Scores

- **Overall: 5 / 10** (marginally below acceptance). The P1 result is solid, but presentation, one over-reaching mechanism claim, and several quantifier and marking errors keep it from being championable.
- **Presentation: 2 / 4**
- **Soundness: 3 / 4**
- **Contribution: 3 / 4**
- **Confidence: 4 / 5**

**Would I champion this at 8+? No, not in its current form.**

I would move to 8 if, and only if, **all** of the following are done. Every item is a rewrite, re-plot, re-mark, cut, or analysis of existing data.

1. **Figure 1 is repaired and shows the idea.** The candidate text is visible (Must-fix 1). A schematic of the three readings, with the discriminating test marked, replaces the result text box in panel (a).
2. **The mechanism claim is scoped to what P3 shows.**
   - The abstract and intro describe behavior ("scores follow the correct answer the judge is shown"), not a mechanism that holds "whether or not it can verify the answer".
   - P2 is relabeled as a consequence of P1, not a discriminating prediction.
   - The uniqueness-assumption alternative is addressed with the masking data or conceded (Must-fix 2).
3. **Every quantifier listed in Must-fix 3 is corrected**, and every number in the abstract and Table 1 appears verbatim in a table.
4. **Registration marks are corrected** (Must-fix 4), and the abstract states the full outcome distribution of the 156 predictions.
5. **Pages 1–3 are consolidated.** The readings matrix and Table 1 become one captioned table with the verdicts. "What we find" shrinks to three one-line verdicts. Figure 4a, which duplicates Figure 2b, is dropped (Must-fix 5).
6. **Section 7 becomes a short consequences section.** It makes no claim beyond the evidence. The claim "only when no candidate matching the reference is in the pool" is either backed by the partition analysis in Must-fix 6 or deleted.

Even with all of this, the ceiling is 8 rather than 10. The practical harm on natural data is confined to grading of non-matching answers, the mechanism remains "partly", and no downstream training harm was shown.

---

## Strengths

1. **The swap test is the right experiment.** Holding candidate text byte-identical and moving only which correct answer is shown removes the confounds that plague prior work: flawed solutions in the reference's style (Li et al., 2025) and wrong references (Lee et al., 2026; Krumdick et al., 2025). The test has three parts:
   - a within-sample contrast (onto / off);
   - a placebo that matches neither reference (+0.12 [−0.07, +0.30], Table 45);
   - robustness to the score estimator: exact +5.25, original +4.96, greedy integer +5.65 (Table 45; `r4_results.json` rotation block matches).
2. **The effect is large and replicated.** It shows up across open judges from 1.5B to 14B, two rubrics, and a frontier API judge, and 12 of 12 registered rotation cells went as predicted.
3. **The masking suite (Table 28) is informative mechanism evidence.** Writing the reference in words keeps the effect; "30+1" cuts it by 77–94%; masking removes it. The paper under-uses this (see Must-fix 2).
4. **The transparency is unusual and commendable:**
   - a full ledger that includes falsified and non-evaluable predictions;
   - disclosure that the registered checker miscounts prose answers, with three relabelings;
   - disclosure of the 67% command-line versus API agreement for Sonnet 5;
   - exclusion of a contaminated command-line run;
   - honest reporting that selection accuracy on MACE did *not* fall and that blind-then-reveal lost to the plain reference there.
5. **The "Verification reduces the effect" within-judge tercile analysis is a nice use of existing data.** Qwen2.5-7B's swap size is 5.2 / 5.4 / 3.6 across blind-AUROC terciles 0.83 / 0.93 / 0.98, with Spearman −0.40 [−0.53, −0.25]; `r11_p3_checks.json` matches exactly.
6. **Numbers are overwhelmingly accurate.** I spot-checked about 45 main-text numbers against the JSON outputs and tables. The only discrepancies are the handful noted below.

---

## Must-fix before submission (ranked)

### 1. Figure 1 hides the candidate text and does not show the idea (page 1, Figure 1; `figures/fig1_concept.tex`)

**What is wrong.**
- **Rendering bug.** In `fig1_concept.tex`, the task box (node `q`, anchored at y = 2.3) contains three items: Question, Correct answers, and **"Candidate (fixed text): '… The answer is 80.'"** The second box (node `k`) is anchored at (0, −0.05) with `fill=white` and is drawn afterwards, so it paints over the bottom of `q`. In the compiled PDF, panel (a) ends at "Correct answers. 35 and 80." and the candidate line is invisible; I rendered page 1 at 220 dpi to confirm. Panel (b) is titled "Same text, three prompts", but the reader never sees the text. This is the first thing every reviewer looks at.
- **Panel (a) mixes the example with P2 results.** The lower box ("One correct answer: … MATH-500: about +30 accuracy points. Several: … AUROC 0.94 → 0.78") sits under the heading "The task". It is a third copy of abstract numbers, not part of the task.
- **The figure shows P1 only.** Nothing on page 1 visualizes the three readings or where the discriminating evidence lands. The Mirage paper's Figure 1 makes its alternative explanation *visual*; this one makes a single swap visual.
- **The stated marker grammar is not followed.** The caption says: "Throughout, orange marks scores without a reference and blue scores with one; hollow markers mark the contrast condition (one correct answer, or reasoning before scoring)."
  - Figure 2 has no hollow markers for "one correct answer" (panel a uses filled dots).
  - Figure 4 introduces five marker types (circles, grey ticks, grey crosses, diamonds, squares).
  - Figure 8 uses black circles and squares.
  - Figure 9 adds teal.

**Fix.**
- Move node `k` down, or delete it: shift its anchor to about y = −0.9, or remove the "One correct answer / Several" box entirely. Then confirm the candidate line renders.
- Replace that box with a small schematic panel titled "What each reading predicts":
  - x-axis: "how well the judge can check the answer without a reference";
  - y-axis: "score change when the reference is swapped";
  - answer key: a flat line at 0;
  - verification failure: a line falling to 0 at full verification;
  - agreement: a line that stays above 0.
  - Mark two annotated dots from existing data. One is "Sonnet 5, factual: ranks correct above wrong 94% blind, margin +4.0" (above 0 at high verification). The other is "thinking judges, arithmetic: swap loss −0.69 → +0.01 (Qwen3-8B), −2.85 → −0.32 (Sonnet 5)" (near 0).

  This is the Mirage move: the reader sees on page 1 that P3a is the only test that separates the readings, and that it splits.
- Caption rewrite: "**(a)** A replication-pool task with two correct answers and one of its 64 candidates (chosen for a large swap; selection rule and full reply in Appendix A). **(b)** Qwen2.5-7B scores that same text 10.0 blind, 2.9 when the reference is 35, and 9.3 when it is 80. **(c)** Over the replication pool, the change in score of identical text when the reference moves onto its answer (blue), off it (hatched), or between two answers it matches neither of (grey); 95% intervals. **(d)** What each reading predicts as the judge becomes able to check the answer, with the two tests that separate them (Section 6)."
- Delete the "Throughout…" sentence, or make Figures 2–4 obey it.

### 2. Only one cell in the readings matrix discriminates, it splits, and the title and abstract still assert the mechanism (pages 1–3 and 6: abstract, intro, Section 2 matrix, Section 6 verdict)

**What is wrong.**
- **P2's first half discriminates nothing.** All three readings predict that a reference helps with one correct answer; an answer key helps too. The matrix cell "Answer key: no harm" quietly concedes this. The +30-point MATH-500 result therefore tests none of the readings.
- **P2's second half is not independent of P1.** Given Eq. (1), a positive λ with β < 1 or γ > 0 mechanically lowers the rank of non-matching correct answers. The paper concedes the same about inflation (Figure 6 caption: "the step follows from the swap result and is not an independent test"), but not about grading AUROC. The intro's claim "P1 and P2 distinguish the answer key from the other two readings" therefore double-counts one test.
- **P3b cannot count against agreement.** The matrix marks it "not required" under agreement, so observing it is consistent with both readings.
- **Hence the agreement reading is only ever at risk in P3a, and P3a splits.**
  - It holds for Sonnet 5 on 40 factual MACE questions, through the command-line interface: margin +3.98 [+2.70, +5.30] at blind verification 0.944 (`r5_sonnet_mace_results.json`).
  - It fails for thinking judges on arithmetic, which verify and do not move. That failure is the verification-failure prediction.
  - Yet the abstract says "judges instead give extra credit for agreeing with the one they are shown", and the intro defines agreement as extra credit "whether or not it can verify the answer".
- **An obvious fourth reading is not addressed: the judge assumes the question has one intended answer** and treats a "trusted" reference that differs as evidence the candidate is not it. This *uniqueness assumption* predicts:
  - P1 yes;
  - P2 yes;
  - P3a yes on factual questions, where "ranks above a wrong answer" is not certainty;
  - removal by an any-answer instruction, which is exactly the phi-4 result the Section 6 verdict cites against verification failure.

  The instruction evidence is also split. The ledger shows the registered instruction prediction was **falsified for Qwen2.5-1.5B, 3B and 7B**, and Sonnet 5 went only from +3.00 to +2.08. The verdict cites only phi-4.
- **The operationalization of "verifies" is weak for a title-level claim.** Ranking a matching and a non-matching correct answer above *one* wrong answer 94% of the time is not verification of the non-matching answer. The stronger item-level statistic comes from a different interface and design than the 94–97% figure, and the paper does not say so in Section 6:
  - The item-level statistic is "35% scored ≤3 once shown", on 38 tasks and 214 answers of API R8-A subsamples (`r9_sonnet_item_level.json`), and it is post hoc.
  - The 94–97% figure is from command-line R5-A.

**Fix (no new data needed).**
- **Scope the mechanism language to behavior.**
  - Abstract sentence 2 → "We show that when a question has several correct answers, a judge's score follows which correct answer it is shown."
  - Title option: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown". If you keep "Reward Agreement", define it behaviorally in the first paragraph.
  - Abstract sentence on P3 → "Verification failure explains part of this: judges with a thinking mode reduce it by 89% or more on arithmetic, where they can check answers. It does not explain all of it: Sonnet 5 still penalizes factual answers it ranks above wrong ones 94% of the time without a reference."
- **Restate the matrix honestly** and merge it into Table 1 (see Must-fix 5). Rows:
  - P1: swap moves identical text → no / yes / yes.
  - P2 (consequence of P1, not a separate test): grading of non-matching correct answers worsens → no / yes / yes.
  - P3a: answers the judge verifies without a reference still move → no / no / yes → **observed: yes for Sonnet 5 on factual questions; no for thinking judges on arithmetic**.
  - P3b: the effect shrinks with verification → — / yes / either → observed: yes; does not discriminate.
- **Encode the distinction in Eq. (1).** Write the bonus as λ(v_c), where v_c ∈ [0, 1] is how reliably the judge checks c without a reference. Then "verification failure: λ(v) = λ₀(1 − v); agreement: λ(1) > 0". Right now Eq. (1) contains no verification term, so it cannot express the one prediction that matters.
- **Add a paragraph, "A fourth reading: the judge assumes one intended answer",** and use the masking suite you already have as the evidence. A judge reasoning about uniqueness should not lose 94% of its margin when 31 is written as "30+1", a trivial computation. A judge matching surface strings should, and it does (Table 28; Sonnet 5 likewise: bare +3.06, words +3.14, expression +0.47). This is the best existing evidence for *surface* agreement over *belief*, and it currently sits in P1 as a curiosity. Move "Rewriting the reference" into Section 6.
- **Section 6 verdict rewrite:** "P3 partly holds. Anchoring shrinks where judges can check answers (within-judge terciles; thinking on arithmetic), so verification failure contributes. It does not account for Sonnet 5, which penalizes factual answers it ranked above a wrong answer 94% of the time blind, or for the collapse of the effect when the reference must be computed rather than string-matched. An instruction that other answers are valid removes phi-4's margin but not those of three Qwen2.5 judges, so instructions do not separate the readings."
- In "Judges that verify still anchor", name the interface and design for each number: "(command line, one sample per class, 40 tasks)" versus "(API, 16-candidate subsamples, 38 tasks; post hoc)".

### 3. Sentences that claim more than the evidence (abstract, Table 1, verdicts, conclusion)

Each item gives the location, the problem, and replacement wording.

**a. Abstract, "judges with a thinking mode stop anchoring on arithmetic".**
- Sonnet 5 with thinking still loses −0.32 [−0.67, −0.07], and with a written rationale −0.20 [−0.37, −0.05] (Appendix N). Both intervals exclude zero.
- Qwen3-14B with thinking on: −0.12 [−0.27, 0.00].
- → "judges with a thinking mode reduce it by 89% to 100% on arithmetic". Section 6 "a thinking mode removes the effect" → "nearly removes".

**b. Abstract, "The same habit helps when there is one correct answer".**
- This asserts that the MATH-500 benefit comes from agreement, which no test addresses (all readings predict it).
- → "A reference still helps when there is one correct answer, raising best-of-64 accuracy by about 30 points on MATH-500."

**c. Abstract, "AUROC falls by 0.16 to 0.33 for four open judges on constructed tasks and from 0.94 to 0.78 for Sonnet 5 on factual questions".**
- It omits two things:
  - restricting to boxed replies gives 0.07–0.14 (Table 13), which you report in Table 1;
  - Sonnet 5's constructed-task falls are only 0.04 and 0.08 (Table 25, `r8_sonnet_results.json`: repl −0.037, k-pool −0.080).
- The juxtaposition invites readers to think the frontier judge falls as much as the open judges on arithmetic.
- → "AUROC falls by 0.07 to 0.33 for four open judges on constructed tasks, depending on how answers are read, and for Sonnet 5 by 0.04–0.08 on constructed tasks and from 0.94 to 0.78 on factual questions."

**d. Section 4 verdict, which contradicts itself.** "…among rationale-first judges, for Qwen2.5-7B under the MT-Bench template … it fails for judges that think or write a rationale on arithmetic."
- The MT-Bench template writes a rationale and still loses 3.59.
- → "…it fails on arithmetic for judges with a thinking mode and for Sonnet 5 when asked for a written rationale (Section 6); the MT-Bench rationale template does not remove it."
- Table 1's P1 verdict "Holds for score-only judges" should add "; absent with thinking on arithmetic". The biggest failure of P1 belongs in P1's "Failed nearby", not only in P3.

**e. Section 4, "closeness to it does not matter, falsifying the gradient we registered".**
- This contradicts the ledger (Table 3, "Distance gradient"): the slope prediction was **confirmed** for both judges, the fall exceeded blind's (**confirmed**), and only the tercile ordering was **falsified**.
- → "The registered slope test came out as predicted but is driven by a few tasks, and the registered near/middle/far ordering failed; we see no reliable gradient (Appendix I)."

**f. Section 7, "the selection-accuracy harm does not survive relabeling (Figure 4b)".**
- Under any-format labels Qwen2.5-7B still loses 30.3 points [−48.5, −12.1] on the k-pool and 9.3 [−17.5, −1.0] on the replication pool (Table 12; `r8_lenient_results.json`, `repl|all/Qwen2.5-7B/lenient/acc` −0.093 [−0.175, −0.010]).
- → "survives relabeling only for Qwen2.5-7B".

**g. Section 7 verdict and intro "What we find": "The grading harm becomes a selection harm only when no candidate matching the reference is in the pool".**
- The only direct evidence is the composition experiment (Appendix I). It uses registered labels that the paper itself says are "partly label artifacts", and its dose prediction was falsified.
- Nothing shows the relabeled Qwen2.5-7B losses are confined to tasks without a matching-correct candidate.
- → Either run Must-fix 6's partition analysis, or write: "On natural multi-answer questions the reference did not lower best-of-64 accuracy; on constructed pools the loss survives relabeling only for Qwen2.5-7B, and no protocol we tried was best on every pool."

**h. Section 7 mitigations and conclusion: "taking the higher of the blind and referenced scores lost nothing to blind judging on the k-pool at k>1".**
- Table 36 has the max rule at −2.6 for Qwen2.5-14B.
- Table 25 has Sonnet 5's max rule on the k-pool at −2.4 [−5.0, −0.5], an interval that excludes zero.
- It is also post hoc and ends the paper.
- → "lost at most 2.6 points to blind judging for the open judges on the k-pool at k>1 (Sonnet 5: −2.4 on 16-candidate subsamples)†". Consider removing it from the last sentence of the conclusion.

**i. Section 6 instruction evidence is quoted selectively.** "closes phi-4's margin on the synthetic grid at k=16 (+1.91 → +0.03)".
- Only the k=16 cell is quoted, while the registered prediction was "at every k".
- The registered prediction was falsified for three of the four Qwen2.5 sizes.
- → Report phi-4's pooled k>1 change (existing data), and add "the same instruction did not lower the margin for Qwen2.5-1.5B, 3B, or 7B, as verification failure predicts".

**j. Conclusion, "correct answers that differ from it are often scored as failing".**
- The false-rejection rate with the reference is 28% for Qwen2.5-7B but 5.8% for phi-4 (Table 9).
- → "are scored 3 or below up to 28% of the time (Qwen2.5-7B) and 36 points more often for Sonnet 5 on factual questions".

**k. Section 6, "Sonnet 5's swap gain is about 60% of Qwen2.5-7B's", and "Larger Qwen2.5 judges anchor less on an exploratory pool".**
- These are cross-model comparisons presented as evidence that *verification* reduces the effect. Model family, API, and scale use all differ.
- The Ties pool has incomplete answer lists (Appendix F).
- → Cut both sentences. The within-judge terciles and the thinking toggle carry P3b alone.

### 4. Registration marks are wrong or inconsistent (Table 1, Sections 3, 5, 6, 7, abstract)

**a. MATH-500 +29 to +31 is marked PRE (Table 1) and unmarked in Section 5.**
- The direction was known before R4-B was registered. The original-scorer MATH-500 accuracy (+27.6 to +43.8, Table 21) came from the exploratory study, and `registration_round4.md` lists "the MATH-500 'unique answers' contrast" among the motivations.
- → ‡.

**b. MACE single-answer +26 to +32 is marked PRE in Table 1 and unmarked in Section 5.**
- R3-D registered no k=1 prediction: only k>1 and pooled, and all three failed (`registration_round3.md` P-R3D1–3).
- Table 23 marks the *same numbers* † (67.7 → 100.0, 73.5 → 100.0).
- → † (or a new mark, "pre-specified readout, no prediction"), consistently in Table 1, Section 5, Figure 2, and Table 23.

**c. Section 7, "Under the registered checker the reference lowers accuracy at k>1 by 15.4 to 35.9 points", is unmarked.**
- The ledger says this exact-scorer re-analysis was "registered after the original-scorer accuracy readout had been seen".
- → ‡.

**d. Section 6, "+4.08 for phi-4, +2.79 for Sonnet 5 … †".**
- The ledger records the blind-accepted filter as a pre-specified, confirmed prediction, and Table 4's caption marks it PRE.
- → Remove † from the phi-4 and Sonnet 5 values. Keep ‡ or † for the exact-scorer Qwen value (+5.27, Table 49).

**e. Abstract, "We report all 156 registered predictions, including 25 that were not confirmed or were falsified."**
- This is technically true but understates the negatives. The ledger counts 92 confirmed, 10 not confirmed, 15 falsified, 16 split (each with at least one non-confirmed judge), 18 not evaluable, 2 not scored, and 3 excluded.
- → "Of 156 registered predictions, 92 were confirmed, 25 were not confirmed or were falsified, 16 held for some judges but not others, and 23 could not be evaluated or were excluded; all are reported."

**f. Section 3's convention merges OSF and PRE tiers ("Unmarked claims in the main text were preregistered on OSF or pre-specified in a timestamped commit"), while Table 1 distinguishes them.**
- A reader cannot tell from an unmarked main-text claim whether it has third-party timestamping.
- → Use OSF and PRE superscripts in the main text as in Table 1, or state in Section 3 that only the replication, k-pool, and coverage inflation endpoints are OSF, and everything else is a repository commit.

**g. Adoption date of the verdict rule.** The ledger says the rule was "adopted … on 13 September 2026, after most outcomes were known", but `registration_round4.md` already states the identical rule "from this round on". Clarify: "adopted with the round-4 registration for later rounds and applied retroactively to earlier rounds on 13 September".

### 5. Pages 1–3 repeat the same summary five times; the readings matrix is a floating, uncaptioned table (pages 1–3; Section 2; Table 1; Figures 2b and 4a)

**What is wrong.**
- The same headline numbers (+5.3 / +4.1 / +3.0; 0.94 → 0.78; about +30 on MATH-500; 0.16–0.33) appear in the abstract, Figure 1(a)'s text box, intro paragraph 1, "What we find", and Table 1.
- The readings matrix is a `\begin{center}` tabular with no number or caption, half a page below Table 1. The reader must join two tables to see prediction × reading × outcome.
- Table 1's result cells hold 6–10 numbers each, with 3–5 registration marks per cell. Nobody skims that.
- **Figure 2b and Figure 4a plot the same quantity for the same judge–pool cells** (grading AUROC for non-matching correct versus wrong; one as blind → referenced levels, the other as referenced-minus-blind changes). One float does not earn its space.

**Fix.**
- **One Table 1** with columns: Prediction | Answer key | Verification failure | Agreement | What we observed (one headline number + one "did not hold" clause) | Verdict. Delete the Section 2 tabular.
- **"What we find"** becomes three lines:
  - "P1 holds for every score-only judge we swapped (3–5 points) and not for thinking judges on arithmetic."
  - "P2, a consequence of P1, holds: grading of other correct answers worsens for all four screened open judges and Sonnet 5."
  - "P3 splits: see Section 6."
- **Figure 4:** drop panel (a). Keep panel (b) (selection) as a half-width panel next to a short Section 7, or move it to the appendix. This frees about a third of a page for the Figure 1 schematic and the Section 6 paragraph in Must-fix 2.

### 6. Section 7 is not a prediction section, its primary endpoint is circular, and its verdict is unsupported (pages 7–8)

**What is wrong.**
- It opens with "Question." instead of a prediction and belongs to none of the readings.
- The preregistered endpoint *inflation* gets one opaque sentence: "a second rubric, shown the same reference, scores the pick against other answers of the same correctness, and +1 means one standard deviation above what its correctness warrants". The next sentence admits it "measures a shared preference for agreement, not lost accuracy", and the one after admits the k-step "follows from P1". A reader spends a paragraph learning a metric that adds nothing beyond P1.
- The "Accuracy depends on the pool" paragraph is a 60-word sentence carrying three caveats, one falsified registered prediction, and a label-artifact disclaimer.
- The verdict claim "only when no candidate matching the reference is in the pool" is not tested under corrected labels (Must-fix 3g).

**Fix.**
- Retitle it "Consequence: grading harm, not selection harm". Two paragraphs:
  1. **Natural data:** on MACE multi-answer questions the reference did not lower best-of-64 accuracy (+2.0 [−5.1, +10.1], +6.1 [−1.0, +13.1]), and overall AUROC was unchanged (+0.00, +0.02, Table 49). The harm is specific to non-matching correct answers.
  2. **Constructed pools:** the k>1 loss under the registered checker (‡) survives relabeling only for Qwen2.5-7B.
- Inflation gets one sentence: "Our OSF-registered selection endpoint, inflation, was confirmed (+1.19 SD; Appendix A); because both rubrics see the reference, it is implied by P1 and we do not treat it as separate evidence."
- Move mitigations to two sentences in the conclusion.
- **New analysis of existing data, if you want to keep "only when":** stratify the 39 k-pool k>1 tasks and 105 replication tasks by whether any candidate that matches the reference is correct under any-format labels, and report the referenced-minus-blind accuracy change per stratum, marked †. If the loss concentrates where no matching-correct candidate exists, keep the claim; otherwise delete it.

### 7. Undefined and overloaded terms raise cognitive load (throughout the main text)

**What is wrong.**
- **"margin"** is used as a key quantity in Sections 4 and 6 and in Table 1 ("adds 4.0 and 3.0 points to its margin", "closes phi-4's margin", "removes phi-4's margin"). Section 3 defines "swap change", "grading AUROC", and "false-rejection rate", but never "margin".
- **"anchoring"** is the effect's working name in Sections 4–7, while the title says "agreement", Section 5 says "match bonus", and the appendix and ledger say "rotation".
- **"fine-grained judges"** actually means "passed our score-resolution screen". It suggests something about rubric granularity that is not meant.
- **"points"** means both 0–10 score points and percentage points, sometimes in the same paragraph. Section 6: "swap loss from −0.69" versus "false rejections … rise by 18 to 22 points".
- **"Failed nearby"** (Table 1) is not standard English for "did not hold".

**Fix.**
- Define in Section 3: "The *margin* is the mean score of correct answers that match the reference minus that of correct answers that do not; *added margin* is referenced minus blind."
- Pick one name for the effect, "anchoring" or "agreement", and use it everywhere in the main text. Say once that the appendix calls the swap test "rotation".
- Rename "fine-grained" to "screened judges" (defined once).
- Use "pp" for percentage points everywhere.
- Change "Failed nearby:" to "Did not hold:".

---

## Should-fix (ranked)

1. **Figure 2 (page 5): the one-versus-several contrast switches metric and dataset.**
   - Panel (a) is best-of-64 accuracy on MATH-500 and MACE k=1. Panel (b) is non-matching AUROC on constructed pools and MACE k>1.
   - A reader cannot see that on MACE (the only within-dataset contrast) accuracy at k>1 did not fall (86.9 → 87.9; 87.9 → 93.9, Table 44).
   - Panel (b) shows only Sonnet 5's largest cell (MACE) and omits its replication (0.96 → 0.92) and k-pool (0.94 → 0.86) rows, which exist in `r8_sonnet_results.json`.
   - The bold header "MACE, several answers" in panel (b) collides with panel (a)'s Qwen2.5-7B point at x = 100.
   - **Fix:** add a "MACE, several answers" group to panel (a) with the k>1 accuracies; add the two Sonnet 5 constructed-pool rows to panel (b); increase `wspace` or shorten the headers. Retitle: "With one correct answer the reference raises accuracy; with several, it lowers the grading of correct answers that differ from it, without lowering accuracy on natural questions."

2. **Figure 3 (page 7) mixes designs so the arithmetic-versus-factual contrast is confounded.**
   - Panel (b)'s arithmetic false-rejection rise for Qwen3-8B with thinking *off* is only +1.5 pp (Table 43), so "thinking removes it on arithmetic" for Qwen3-8B mostly means there was little to remove.
   - Sonnet 5 has no arithmetic false-rejection cell ("not run"), so its arithmetic-versus-factual comparison is swap loss (panel a) against false rejections (panel b).
   - **Fix:** narrow the caption title to "For Sonnet 5 and Qwen3-14B, a thinking mode nearly removes anchoring on arithmetic but not on factual questions". Add Sonnet 5's factual margin change with thinking off and on (+3.98 → +3.03, paired −0.95 [−2.45, +0.63]) as a panel (b) row, so one metric family spans both panels. State in the caption that the thinking reduction on factual questions is not distinguishable from zero for Sonnet 5.

3. **Figure 4 (page 8), if kept in any form.**
   - It uses five marker types.
   - "not shown (see caption)" repeats five times and "not defined (one correct answer)" twice.
   - The latter string runs across the zero line in panel (a).
   - **Fix:** use two markers (any-format circles with intervals; registered-checker ticks), delete placeholder rows instead of labeling them, and put Sonnet 5 in a separate labeled block.

4. **Section 5 "One correct answer" (page 5): the k-pool k=1 null is explained in one hard sentence.**
   - The sentence runs "…because it picked unboxed replies stating the reference's value, which that checker counts as wrong, and counting such replies as correct the change is zero…". It also omits the ceiling: blind accuracy at k=1 is already 79–100% (`r4_results.json`).
   - **Fix:** "On our constructed k-pool the reference did not help at k=1: blind accuracy was already 79% to 100%, and the apparent 21-point loss for Qwen2.5-7B under the registered checker disappears once prose answers are counted as correct.†"

5. **Inconsistent values for the same quantity.**
   - Replication, Qwen2.5-7B, registered checker, AUROC change: −0.27 (Section 5; Table 48, exact scorer, 120 tasks) versus −0.29 (Table 13).
   - Pooled replication inflation: [+1.03, +1.35] (Section 7, Table 18) versus [+1.02, +1.36] (Table 16).
   - **Fix:** name the canonical source once and note the estimator or tie-break difference in the other caption.

6. **Intro (page 2): "construction or search tasks used for RL rollouts, where one stored solution is the norm" has no citation or evidence.** Cite two concrete datasets or cut.

7. **Conclusion recommendation (page 9) is post hoc and ignores the failed mitigation.**
   - "re-score such answers without the reference" is fine.
   - Add that blind-then-reveal lost 10.3 and 15.4 points against blind judging on the k-pool for Qwen2.5-7B and phi-4 (Table 8, registered labels) and did not beat the reference on MACE (registered, falsified). Readers will otherwise adopt it.

8. **Appendix navigation.**
   - There are 16 appendices and 50 tables with no roadmap.
   - Several pages are half empty because of float placement (pages 22, 23, 24, 25, 39).
   - Tables 10, 36, 38, 40 are shrunk by `adjustbox` well below 7 pt at print; Table 36 prints at roughly 5 pt.
   - **Fix:** open the appendix with a table mapping each main-text claim to its appendix table and JSON producer; use `[p]` floats or `\FloatBarrier` to pack tables; split Table 36 into two rows of pools rather than shrinking it.

9. **Figure 6 (appendix, cited from the main text as primary evidence for "all 12 judge–pool pairs").** A main-text claim should not rest on an appendix figure. With inflation demoted (Must-fix 6), change the sentence to "…in all 12 judge–pool pairs (Appendix D, Figure 6)", or drop it.

10. **Section 3 "Reading answers".** "38% to 43% of replies ignore the format" is a first-order threat to every registered accuracy and false-rejection readout, yet it arrives as the third paragraph of Setup. Mention it in Limitations' first bullet with the consequence: "registered accuracy and false-rejection endpoints on the OSF pools used a checker that counted most prose answers as wrong; all main-text accuracy claims use post hoc relabelings".

---

## Nits

- **Figure 1(c):** bar value labels are 6.8 pt (`make_figures.py`, `fontsize=6.8`), just under 7 pt; Figure 1 is placed at about 1.0× scale.
- **Figure 5 (appendix):** legend at 6.3 pt.
- **Figure 2(a):** large empty region; reduce panel width ratio.
- **Table 3, "Blind-accepted filter (Section 6)":** says "all four sizes" and "four of four sizes, three required", but Section 6 reports phi-4, Sonnet 5, and Qwen2.5-7B on the replication pool, not four Qwen sizes. State which pool and judges the registration covered.
- **Figure 1 caption:** "(exact scorer)" applies only to Qwen2.5-7B; phi-4 is exact by tokenizer and Sonnet 5 is integer. Say "Qwen2.5-7B exact scorer".
- **"Sonnet 5 (API)" and "Sonnet 5 (CLI)"** appear in figure labels before the reader is told why the interface matters. Define both once in Section 3.
- **Table 1, "k=1 benefit on a Llama-generated grid":** "grid" is not introduced until Section 3; use "on a second synthetic pool".
- **Section 6, "Qwen2.5-7B's swap shrinks where it verifies best but stays 3.6 points":** add "(top blind-AUROC tercile, 0.98)" in Table 1 so the number is interpretable.
- **Section 8:** "The swap test asks what such judges do when the reference is one of several correct answers" reads as a stray sentence; attach it to the previous one.
- **Main text:** "Sonnet 5 behaves the same way (Appendix H)" → give the three numbers (+3.06 / +3.14 / +0.47); they are short.
- **ICLR compliance:** the main text ends on page 9, and the AI-use, ethics, and reproducibility statements are present and follow it. Confirm the 2027 CFP still excludes these statements from the page limit. The PDF metadata is clean (no author field). **`main.tex` lines 6–7 contain the OSF project URLs in comments**; strip comments from any LaTeX source you upload.
- **Consistency:** "OSF" and "PRE" are small caps in Table 1 but spelled out elsewhere; the same holds for the dagger conventions in figure captions.

---

## Questions for authors

1. **Sonnet 5 blind scores in P3a.** Of the non-matching correct MACE answers Sonnet 5 scored at least 7 blind, what share did it score 10? If most were 10 and still fell to 3 or below with the reference, that is much stronger evidence against verification failure than "ranks above a wrong answer 94% of the time", and it uses existing data.
2. **Question wording.** Does the swap effect differ between task families whose wording signals multiplicity ("Give one 2-digit number…") and those that do not? That would bear directly on the uniqueness-assumption reading, using existing scores.
3. **Where the selection loss sits.** Under any-format labels, is Qwen2.5-7B's k-pool selection loss (−30.3 points) concentrated in tasks with no matching-correct candidate? (See Must-fix 6.)
4. **Instruction result across k.** Why is phi-4's instruction result quoted at k=16 only? What is the pooled k>1 change, and at which k does the instruction fail for Qwen2.5-7B?
5. **MATH-500 timing.** Was the original-scorer MATH-500 accuracy readout (Table 21) seen before R4-B was committed? If so, the Table 1 mark should be ‡.
6. **GPT-4.1 in the swap test.** Was GPT-4.1 run on the byte-identical swap test? If yes, why is it absent from Figure 1(c) and the P1 verdict; if no, say so, since "every score-only configuration we swapped" invites the question.
7. **The word "trusted".** Every referenced prompt calls the reference "trusted" and tells the judge to use it "to check" the candidate. Do you have any existing condition (for example, the neutral-wording blind-then-reveal variant) that weakens this framing and shows whether the swap effect depends on it?

---

## Top five must-fix items

1. Figure 1 hides the candidate text under a white box and shows neither the three readings nor the one test that separates them. Fix the node placement and add a schematic of what each reading predicts.
2. Only P3a separates agreement from verification failure, and it splits. Rewrite the mechanism claims in the title, abstract, and Section 6 verdict as behavior, treat P2 as a consequence of P1, and address the uniqueness-assumption reading with the masking data.
3. Correct the overclaims:
   - "stop anchoring";
   - "the same habit";
   - the 0.16–0.33 range without its caveats;
   - the self-contradictory P1 verdict;
   - "falsifying the gradient";
   - "does not survive relabeling";
   - "only when no matching candidate";
   - "lost nothing";
   - "often".
4. Fix the registration marks: MATH-500 should be ‡, MACE k=1 should be †, the k>1 accuracy loss should be ‡, and the blind-accepted filter should be PRE. Restate the full 156-prediction outcome in the abstract.
5. Merge the readings matrix into Table 1 and cut the repeated numbers on pages 1–3. Drop Figure 4a, which duplicates Figure 2b, and cut Section 7 down to a supported consequence claim.
