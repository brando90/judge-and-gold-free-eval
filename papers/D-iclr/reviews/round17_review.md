# Round 17 Area Chair review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

Reviewed: `reviews/round17_main.pdf` (43 pages; main text pages 1-9, ends at line 485). Where the main text and appendix seem to disagree, I checked the table sources in `tables/*.tex` and `analysis/r16c_protocols_exact.json`. Line numbers below are the PDF margin numbers.

---

## 1. Summary of the claims (and whether they were easy to extract)

**Question.** When a question has several correct answers, does a reference answer given to an LLM judge act as an answer key? That is, does a correct response score the same whichever correct answer is shown?

**Framing.** The paper sets out three readings of a reference:
- **Answer key:** the judge checks the candidate against every correct answer.
- **Verification failure:** the reference is the only evidence a judge has when it cannot verify on its own.
- **Agreement:** the judge rewards matching the shown answer even when it can recognize the others.

An additive scoring model, Eq. 1, organizes three predictions.

**Claims:**
1. **P1 (swap).** Moving the reference between two correct answers moves the score of byte-identical text. The shift is 2.7-5.4 points out of 10 for Qwen2.5-7B, phi-4 and Sonnet 5 on 120 constructed tasks. It replicates on 9 combinatorial puzzles, and is near zero on arithmetic with a thinking mode.
2. **P2 (grading harm).** With several correct answers, the non-matching ones are rejected more often, and their grading AUROC against wrong answers falls:
   - by 0.17-0.27 for four screened open judges;
   - by 0.06-0.08 on MACE;
   - by 0.04-0.15 for Sonnet 5;
   - by at most 0.04 for GPT-4.1.

   **P2′:** with one correct answer, the reference helps (MATH-500 best-of-64 +29-31 pp).
3. **P3 (not only verification failure).** For Sonnet 5, 9-19% of non-matching correct answers it scored 10 blind drop to 3 or below with the reference. None of the matching ones drop, and none of 111 drop on a second blind call.
4. **Moderator.** A thinking mode removes the effect on arithmetic. On factual questions it roughly halves it for Qwen3 and gives no detectable reduction for Sonnet 5.
5. **Consequence.** Selection harm is conditional: it is concentrated where no correct candidate matches the reference, and is null on MACE's natural mix. A post hoc "max rule" (keep the higher of the blind and referenced scores) keeps grading at blind level on multi-answer pools.

**Ease of extraction.** The core claim is easy to extract.
- The title, Figure 1 and the first intro paragraph give it in 30 seconds.
- Table 1 maps each prediction to a section and a verdict, which is the right device.

The secondary claims are hard to extract: the moderators, which judges each claim covers, what P3 actually rests on, and what the max rule costs. They are spread across roughly 14 judge configurations, 7 benchmarks, 2 scorers, 2 interfaces, 4 labelings and 33 registration marks. Several summary sentences also state them more broadly than the evidence supports (Section 3, M1-M3).

---

## 2. Score and confidence

**Score: 6 / 10 (weak accept). Confidence: 4 / 5.**

**Single biggest reason.** The central finding is clean, surprising in its size, carefully controlled (byte-identical text, a program-enumerated answer set) and honestly registered. But the main text is not yet at the bar for reliability of its summary sentences and cognitive load:
- The intro's one-line summary contradicts Table 1.
- The P1 verdict contradicts itself.
- The conclusion introduces numbers that appear nowhere in the main text and contradicts Section 6 on thinking modes.
- The Limitations contradict Section 7 on where the max rule was tested.
- A reader has to hold roughly 20 defined terms, subsamples and conditions to follow Sections 4-7.

None of this needs new experiments. The paper is closer to a 7 than its presentation lets it look.

---

## 3. Ranked issues

### MUST FIX (ranked)

#### M1. Headline scope is broader than Table 1 supports, and two summary sentences contradict the evidence

**(a) Intro summary contradicts Table 1.**

Location: p.2, l.092-094. Current text:
> "Table 1 gives what we observed for each: all three hold for judges that score without a thinking mode"

Table 1 (p.3) says:
- P3 "Holds for Sonnet 5" only. It was never shown for an open judge; Section 6 says Qwen2.5-7B's evidence "is not an acceptance test".
- P2 is "small for GPT-4.1", which also scores without a thinking mode.

Replacement:
> "Table 1 gives what we observed for each. P1 and P2 hold for every score-only judge we tested, although the grading harm is small for GPT-4.1; P3 holds for Sonnet 5, the judge on which we could test acceptance directly. A thinking mode removes the effect on arithmetic but not on factual questions (Section 6). On multi-answer pools, keeping the higher of the blind and referenced scores keeps grading at blind level, at a cost when the answer is unique (Section 7)."

**(b) P1 verdict is self-contradictory.**

Location: p.5, l.240-242. Current text:
> "P1 holds for every judge we swapped that scores without a thinking mode, including open judges that explain first. It fails on arithmetic with a thinking mode, and for Sonnet 5 already when it explains first."

Sonnet 5 explaining first has no thinking mode, so the second sentence falsifies the first. The same problem is in Table 1's P1 verdict, "Holds without a thinking mode".

Replacement:
> "Verdict. P1 holds for every score-only judge we swapped and for open judges that explain first. On arithmetic it nearly vanishes with a thinking mode, and for Sonnet 5 already when it explains first (Section 6)."

Table 1 verdict cell: "Holds for score-only judges; near zero with thinking (arithmetic)".

**(c) Abstract overgeneralizes and omits the moderators.**

Location: p.1, l.013-030.
- Claim (3) is stated for "the judge" in general, but it rests on one frontier judge.
- "Together, these results show that a single reference makes LLM judges undercredit valid alternatives" omits the two moderators a practitioner most needs: GPT-4.1 is barely affected, and thinking removes the effect on arithmetic.
- "test three predictions that separate them" contradicts l.083, "only P3 separates the other two readings".

Fix: see the abstract rewrite under M8.

#### M2. The conclusion introduces unanchored numbers and contradicts Section 6

Location: p.9, l.482-485.

**(a) The AUROC levels.** Current text:
> "grading AUROC with the reference falls to between 0.60 and 0.73 on our pools"

- The main text reports AUROC *changes* only; these levels appear nowhere in it.
- The levels come from Table 49 (`tables/r4_grading.tex`), under the *registered* labels, although Section 3 says the main text uses any-format labels.
- They cover only Qwen2.5-7B and phi-4 on the replication pool and MACE.
- "On our pools" is wrong for Sonnet 5, whose referenced AUROC is 0.78-0.92 (Table 26), and the k-pool is not included.

**(b) Thinking on factual questions.** Current text:
> "a thinking mode helps on arithmetic but not on factual questions"

Section 6 (l.366-368) and Table 1 say thinking "roughly halves the effect for Qwen3" on factual questions (false rejections +44 → +22 and +42 → +18 pp). "Helps ... not on factual questions" is false for Qwen3.

Replacement for l.477-485:
> "A reference answer is a good check when a question has one right answer. When it has several, judges that score without a thinking mode favor the one they are shown: swapping it moves the score of unchanged text by 2.7 to 5.4 points, correct answers that differ from it are rejected far more often, and for Sonnet 5 this happens even for answers it accepts without a reference. A low reference-guided score on such an answer is therefore weak evidence of error: for Qwen2.5-7B and phi-4, grading AUROC for these answers falls from 0.74-0.90 blind to 0.60-0.73 with the reference (Appendix O). Keeping the higher of the blind and referenced scores kept grading at blind level on our multi-answer pools, at some cost when the answer is unique. Selection suffers mainly when no correct candidate matches the reference, and a thinking mode removes the effect on arithmetic but only reduces it on factual questions."

If you keep the levels, either:
- say they are registered-label values and cite the table, or
- recompute them under any-format labels from the stored scores (a re-analysis, not a new experiment).

#### M3. The max rule: contradictions, an unsourced interval, and a near-tautological headline

**(a) Limitations contradict Section 7.**
- Limitations (p.9, l.469-470): "tested only on stored open-judge scores".
- Section 7 (p.8, l.420-422) reports the max rule for Sonnet 5: "its accuracy was 2.4 pp [−5.0, −0.5] below blind".
- The source, `tables/sonnet_r8.tex` row "Max rule accuracy, change", confirms this is Sonnet 5 API data.
- The Sonnet sentence is also ambiguous: "its accuracy" reads as Sonnet's accuracy with the reference, not under the max rule.

This result is the one place where the max rule is significantly *worse than blind*. The reference alone is −2.6 [−5.8, +0.4], which includes zero. That undercuts l.417, "The max rule recovers blind accuracy", which the text never qualifies.

Replacement for l.420-422:
> "For Sonnet 5 on its 16-candidate k-pool subsamples, the max rule's accuracy was 2.4 pp [−5.0, −0.5] below blind, about as much as the reference's own 2.6 pp [−5.8, +0.4] (Appendix H)."

Limitations bullet:
> "The max rule was chosen post hoc from five score combinations and evaluated only on stored scores: four open judges, and Sonnet 5 on 16-candidate subsamples."

**(b) The quoted interval is not in any table.**
- p.8, l.419-420: "6.7 pp lost [−11.4, −1.9]".
- Table 37 (middle block, original scorer) gives −6.7 [−12.4, −1.9].
- The main-text interval is the exact-scorer paired difference in `analysis/r16c_protocols_exact.json` (`math500/Qwen2.5-7B/ref/accuracy/max_rule_minus_reference` = −0.0667 [−0.1143, −0.019]), which no table shows.

Fix: add a "max rule − reference" column to Table 37's exact-scorer block and cite it.

**(c) The headline is largely true by construction.**

The intro (l.092-094) and conclusion present "removes the grading harm" as a finding. Section 7 (l.415-416) admits "This is partly by construction, since the reference lowers the scores of both groups". If the reference only lowers scores for non-matching correct and wrong answers, max(b, s) ≈ b for both groups, so AUROC ≈ blind AUROC. The informative content is the costs, and the main text does not show them:
- Table 2 shows "Reference" and "Max rule" against blind, not the max rule against the reference.
- The bare-answer MATH-500 cost is also significant: −4.8 pp [−9.5, −1.0] (JSON `refans/accuracy`).
- On MACE single-answer questions, grading costs −0.07 AUROC [−0.11, −0.03] for Qwen2.5-7B (JSON `grading_k1_all_correct`).

Fix:
- Reword the intro and conclusion as a safeguard with costs (see M1a and M2).
- In Table 2, add a row "Max rule − reference" with intervals (all values exist in the JSON).
- Add the full-solution MATH-500 column, which is now buried in the caption.

#### M4. Cognitive load: the main text carries too much

**Location.** Sections 3-7 (pp.3-8). In 9 pages the reader meets:

| Kind | What the main text uses |
|---|---|
| Pools | replication, k-pool, MACE, MATH-500, MathConstraint, MBPP, RewardBench-2 Ties |
| Subsamples | 60-task CLI, 120-task subsample, 40 MACE CLI, 16-candidate API, 21 k-pool masking tasks, 33/59 k-pool band, 81 MACE toggle |
| Judge configurations (about 14) | Qwen2.5 1.5B/3B/7B/14B, phi-4, gemma-2-9b, Mistral-7B, Qwen3-8B/14B with thinking off/on, Sonnet 5 API, Sonnet 5 CLI score-only / explain-first / thinking, GPT-4.1 |
| Measurement variants | 2 scorers ("exact" and "earlier approximation"), 4 labelings, 2 rubric wordings, 3 registration marks |

The text has 39 appendix pointers and 33 daggers or double daggers.

One example, p.5, l.248-258: a single paragraph gives 7 judges × 3 pools × 2 metrics, plus boxed-only variants and a failed-screen judge. The reader cannot tell which number carries the claim.

Fix, by rewriting and cutting only:
1. **Declare a core cast** at the start of Section 3 and keep to it in Sections 4-7:
   - Pools: replication, k-pool, MACE, MATH-500.
   - Judges: Qwen2.5-7B and phi-4 (open, score-only); Sonnet 5 (frontier, API); GPT-4.1 as the weak-effect contrast; Qwen3 for the thinking toggle.
   - Say explicitly that everything else is robustness and lives in the appendix.
2. **Section 3, "Candidates and judges" (l.171-187):**
   - Move the exact-scorer versus earlier-approximation detail and the 67% CLI/API agreement to Appendix A.
   - Keep: "Open judges' scores are expected values over the score tokens (Appendix A). Sonnet 5 runs through its API unless marked CLI; its two interfaces disagree often enough that we compare its results only within one."
   - Replace the Mistral/GPT-4.1 tie sentence with "GPT-4.1's scores tie too often to rank candidates, so we report only its grading AUROC."
3. **Section 3, "Measurements" (l.207-212):** compress the inflation paragraph to one sentence: "Our OSF primary endpoint, best-of-64 inflation, was confirmed (+1.19 SD) and survives relabeling† (Appendix D); we lead with measures that are easier to interpret."
4. **Section 4, "Beyond arithmetic" (l.226-231):** keep MathConstraint with its n (see P9). Cut the Ties sentence: it is exploratory, uses the earlier scorer, and the small judges saturate. Reduce MBPP to one clause.
5. **Section 4, "What the judge responds to" (l.233-238):** two sentences (see P7).
6. **Section 5:** drop the Mistral-7B sentence (l.257-258); it is a screen-failing judge, and the result is already in Appendix D.
7. **Section 7, "Constructed pools" (l.407-409):** drop the registered-label re-statement, which Section 3 and Appendix D already cover.

These cuts free about 0.6-0.8 page. Use it to:
- add a four-row "Setup at a glance" table (pool | answers | judges | readouts), or
- enlarge Figures 2 and 3, or
- give Table 2 its cost row (M3c).

#### M5. Figure 3's caption describes a quantity it does not plot, and one encoding means two things

Location: p.7, Figure 3(b) and caption, l.346-349.

**(a) Caption versus plotted quantity.**
- The caption says "Sonnet 5's reduction is not distinguishable from zero".
- Panel (b) plots false rejections: Sonnet 5 +17.5 [+5.0, +30.0] off and +12.5 [+2.5, +25.0] on.
- The "not distinguishable" interval in the text (l.368-369) is for the *margin*: −0.95 [−2.45, +0.63].

**(b) "Thinking off" encodes two different conditions.** For Qwen3 it means explanation first; for Sonnet 5 it means score only. The legend "thinking off / thinking on" hides this, and the only explanation is one sentence in the caption.

**(c) Unexplained 17.5 versus 36 pp for the same judge and benchmark.**
- Section 5 (l.255-256) says Sonnet 5's false rejections on MACE "rise by 36 pp".
- Figure 3(b) shows +17.5 for Sonnet 5 score-only on MACE.
- Appendix Table 44 explains the gap: API with 16-candidate subsamples versus CLI with one answer per kind on 40 tasks. The main text never does.

Fix:
- Label the bars directly: "explain first", "score only", "thinking on".
- Replace the caption of (b) with: "(b) Rise in false rejections of correct answers that differ from the reference on factual MACE questions, without and with a thinking mode (Qwen3 without thinking explains first; Sonnet 5 without thinking scores only). Sonnet 5 bars use 40 questions with one answer of each kind through the CLI and are not comparable with the 36-pp API value in Section 5 (Appendix N, Table 44). For Sonnet 5 the paired change in margin with thinking, −0.95 [−2.45, +0.63], is not distinguishable from zero."

#### M6. The registration-mark convention is violated, and the ledger summary undercounts failures

**(a) Unmarked post hoc numbers.** Section 3 (l.212-213) says "Unmarked results were pre-specified". Yet these are unmarked:
- **Prevalence audit** (p.2, l.069-072): "0% to 2.5%", "30%", "18.5%". Its source, Table 21, is marked †.
- **Relabeled inflation** (p.4, l.210-211): "+1.14 SD with any-format labels". Table 17 marks it †, and l.194 itself says any-format labels "are post hoc for the open judges".
- **Labeling agreement** (l.195): "88%", from the post hoc relabeling.

Fix, either of:
- Add † to these.
- Scope the convention in l.212: "Marks apply to effect estimates: unmarked estimates were pre-specified ...; descriptive statistics (format compliance, labeling agreement, the prevalence audit) are post hoc and unmarked." Even then, "+1.14 SD" needs a †.

**(b) Ledger summary.** Current text (l.214-215):
> "156 registered predictions ... including the 25 that were not confirmed or were falsified"

Appendix B gives 92 confirmed, 10 not confirmed, 15 falsified, 16 split, 18 not evaluable, 2 not scored and 3 excluded. Several of the 16 splits contain falsified cells, for example "instruction lowers the margin at every k: Qwen2.5-1.5B, 3B, and 7B falsified". "25" therefore understates the failures, and a reviewer who opens Appendix B will notice.

Replacement:
> "Appendix B lists all 156 registered predictions: 92 confirmed, 10 not confirmed, 15 falsified, 16 split across judges, and 23 not evaluable, not scored, or excluded."

**(c) Abstract wording on predictions.** "Test three predictions that separate them" should become "test three predictions: two that rule out the answer key and one that separates the other two readings" (see M8).

#### M7. P3's inference from "accepts" to "can verify" needs one more existing-data number, and the noise floor needs a sentence

**Location.** Section 6 (p.6, l.310-321), Verdict (p.7, l.375-377), abstract claim (3) and Table 1 P3.

**The inferential gap.** P3 treats a blind score of 10 as acceptance, and acceptance as the ability to verify. The paper's own motivation cites judges without references as "too generous" (Kranti & Vajjala, l.065-066). Appendix N reports that Sonnet 5 scores ≥7 on 7-16% of *wrong* answers in these subsamples. A skeptic will say a blind 10 may be leniency rather than verification, in which case the reference could be correcting over-credit rather than overriding a verified belief. The ranking test (94%/97%) helps, but Section 6 itself says it "measures ranking rather than acceptance".

**Fix (re-analysis of stored API scores, no new calls).**
- The 16-candidate subsamples include wrong answers. Report the share of wrong answers Sonnet 5 scores 10 blind on the same MACE, replication and k-pool subsamples, that is, the precision of "blind 10" as acceptance.
- If it is low (say under 5%), add one sentence: "Sonnet 5 gives a blind 10 to only X% of wrong answers on these subsamples, so a blind 10 is close to verification."
- If it is not low, soften the abstract to "persists on answers the judge scores 10 without a reference" and drop "so it is not only a failure to verify" from the abstract, keeping it in the Section 6 verdict with the caveat.

**Noise floor.**
- The "second blind call" is through the CLI; the referenced call it is compared with is API.
- Section 3 (l.182-184) says Sonnet 5 results are compared only within an interface.
- The comparison is conservative, because CLI scores run 0.38 points *lower* (Appendix H), so cross-interface noise would create more drops, not fewer.
- It also covers 111 of the 150 blind-10 replication answers, because the CLI run stopped at a spend limit.

Add after l.320:
> "(the second call crosses interfaces, which if anything adds low scores, since CLI scores run 0.38 points lower; it covers the 111 of 150 answers the interrupted CLI run reached)."

#### M8. The abstract does not follow the authors' own 6-point guide

Location: p.1, l.013-030. Checked against `ml_research_writing.md`:

| Guide point | Present? | Problem |
|---|---|---|
| 1. Problem motivation | Partly | "Routinely given" is stated, but not why it matters (benchmarks, best-of-n selection, RL rewards). |
| 2. Assumption | Yes | "on the premise that they act as answer keys" is good. |
| 3. Flip, with an immediate hook | Yes | Sentence 2, "judges favor the correct answer they are shown", is good. |
| 4. Instantiation | Yes, heavy | The parenthetical of three readings is jargon-dense on first read ("the only evidence for a judge that cannot verify"). |
| 5. Evaluation with concrete numbers | **No** | "several points out of 10", "far more often". The guide explicitly says "Concrete: X% → Y%". The "how tested" sentence comes after the findings. |
| 6. Implications | Weak | "should not read a reference-guided score as a verdict" is fine, but the two actionable findings are absent: thinking mode as a moderator, and the blind-score safeguard. |

Replacement abstract (about 225 words; no wall of numbers, three figures):
> "LLM judges are routinely given a reference answer when they grade benchmarks, pick among sampled answers, and score training rollouts, on the premise that the reference acts as an answer key: a correct response should score the same whichever correct answer is shown. Many questions have several correct answers, and on them the premise fails. We distinguish three readings of a reference (an answer key, the only evidence for a judge that cannot verify, or an answer the judge rewards for matching), formalize them in a simple scoring model, and test two predictions that rule out the answer key and one that separates the other two. Swapping the reference between two correct answers moves the score of byte-identical text by 2.7 to 5.4 points out of 10. A 7B judge scores 28% of correct answers that differ from the reference at 3 or below, against 0.4% without it, although a reference still helps when the answer is unique. For Claude Sonnet 5, answers it scores 10 without a reference still drop when shown a different correct answer, so the effect is not only a failure to verify. The effect is weak for GPT-4.1 and near zero on arithmetic with a thinking mode, but persists on factual questions. We test on program-enumerated tasks and public factual, math, and puzzle benchmarks, with 156 registered predictions, all reported. On questions with several correct answers, a low reference-guided score is weak evidence of error."

If M7's re-analysis does not support the Sonnet 5 sentence, use "answers it scores 10 without a reference still drop, 9 to 19% of them to 3 or below" and drop "so the effect is not only a failure to verify".

---

### POLISH (ranked roughly by reader impact)

**P1. Section 7's title does not match its content.**
- Current title (p.8, l.396-397): "Consequence: grading harm is robust, selection harm is conditional".
- Grading robustness is argued in Section 5, while Section 7 covers selection and the max rule.
- Retitle: "When the harm reaches decisions, and a cheap safeguard".

**P2. Figure 1(b)'s in-figure note is hard to parse.**
- Current: "Over the pool it scores correct answers that differ from the reference 3 or below 0.4% of the time blind and 28% with the reference."
- Replace: "Over the pool: correct answers that differ from the reference get ≤3 in 0.4% of cases blind and 28% with the reference."
- Note that 28% is the registered-label, exact-scorer value (Table 50: 28.1%, change +27.7). The any-format change is +27.0 (Table 15). The difference is negligible, but Section 3 says "unless stated otherwise ... any-format labels", so state it or switch to the any-format value.

**P3. Table 1's "Observed" cells are too dense to skim.**
- The P2 cell has 5 numbers, 3 daggers and a parenthetical.
- "counting only boxed replies", "labeling" and "constructed pools" are used before Section 3 defines them.
- Trim P2 Observed to: "Grading AUROC for non-matching correct answers falls 0.17-0.27 (four open judges), 0.04-0.15 (Sonnet 5), ≤0.04 (GPT-4.1)†".
- Move the boxed-only range and MACE to Section 5.
- In the "Tests" column for P2, say what P2 adds beyond P1 per Eq. 1: "Rules out the answer key; shows the harm reaches grading (needs β<1 or γ>0)". Otherwise P1 and P2 read as redundant tests.

**P4. Table 2 formatting.**
- Column heads "Qwen-7B", "Qwen-14B" and "gemma" differ from the names used everywhere else ("Qwen2.5-7B", "gemma-2-9b").
- The k-pool max-rule "+3.0" cells are single tasks, as the caption says ("One k-pool task moves an accuracy cell by 3.0 pp"). Printing them as gains invites misreading: print "+3.0 (1 task)" or grey them out.
- Add intervals, or bold the cells whose 95% interval excludes zero; all are in Table 37 bottom and the JSON.
- The 120-word caption carries a result (the 6.7 pp full-solution cost) that belongs in the table (M3c).

**P5. Sign conventions are mixed between magnitudes and intervals.** Examples:
- "Qwen2.5-7B loses 64 pp [−91, −36]" (l.409-410)
- "reduction in margin, 0.95 points [−2.45, +0.63]" (l.368)
- "6.7 pp lost [−11.4, −1.9]" (l.419-420)
- "accuracy was 2.4 pp [−5.0, −0.5] below blind" (l.421)

A positive point estimate with a negative interval makes the reader stop and check. Use signed changes throughout, e.g. "changes accuracy by −64 pp [−91, −36]".

**P6. "Several correct answers" paragraph wording.**
- Current (p.5, l.250-251): "across the four screened judges and both constructed pools the rise ranges from 6.5 to 54 pp".
- Table 3 shows Qwen2.5-14B and gemma-2-9b were run only on the k-pool, not the replication pool.
- The range 6.5-54 also spans all four labelings, not the any-format labels the text defaults to (any-format: 6.6-52.8).
- Replace: "across the four screened judges (two on both constructed pools, two on the k-pool only) the rise ranges from 7 to 53 pp under any-format labels and changes by about 3 pp or less across labelings".

**P7. "What the judge responds to" interleaves three manipulations.**
- Location: p.5, l.233-238. The "while" joins unrelated tests.
- Replace: "The pull depends on how explicitly the reference states its answer. Spelled out in words ('thirty-one'), it keeps most of its effect (Qwen2.5-7B's margin falls by 38%, phi-4's barely); written as an expression ('30+1'), it loses most of it (94% and 77%); hidden inside a worked solution, it loses all of it (21 k-pool tasks). Sonnet 5 shows the same pattern (+3.06 numeral, +3.14 words, +0.47 expression). These tests are arithmetic only."

**P8. Figure 2's two panels use different row sets and grammar.**
- Panel (a) puts the dataset in each row label ("MACE, Qwen2.5-7B"); panel (b) uses group headers ("One answer · MACE").
- Panel (b) has no MATH-500 rows, although P2′ in panel (a) leads with MATH-500 and Table 2 has the MATH-500 grading values.
- Panel (a)'s replication-pool accuracy rows (Qwen2.5-7B about −9 pp, phi-4 about −3 pp) are never discussed in the text.
- Use one shared row layout across both panels, leaving a cell blank where a readout does not exist.
- Move the 50-word registration sentence in the caption onto the row labels as † and ‡.

**P9. MathConstraint needs its n in the main text.**
- "The swap replicates on MathConstraint's combinatorial puzzles" (l.226-227) and Table 1's "also on combinatorial puzzles" rest on 9 eligible all-interval-series items with Claude-written candidates.
- The Sonnet 5 interval is wide: +4.38 [+1.88, +6.88].
- Say "on 9 all-interval-series puzzles with generated solutions (Appendix P)".

**P10. Thinking-mode wording.**
- "Qwen3-8B: 0.69 and none" (l.361-362): write "0.69 and +0.01".
- "explaining first is not enough for open judges" (l.363, and Figure 3's title): Qwen3-8B explaining first loses only 0.69 points. Write "not enough for Qwen2.5-7B under the MT-Bench template or for Qwen3-14B".

**P11. Intro claims and citations.**
- "Whether it is safe where answers are not unique has not been tested" (l.070-071) is strong given Li et al. (2025) and Fomicheva & Specia (2016), cited 25 lines later. Write "has not been tested directly for LLM judges".
- Gao et al. (2023), cited for judges that "score rollouts for training" (l.067-068), is about reward-model overoptimization, not LLM judges scoring rollouts. Reword ("and serve as reward signals, which optimization exploits") or cite an LLM-as-reward paper.

**P12. Appendix consistency (cheap to fix).**
- **Bootstrap intervals differ between tables for identical contrasts.** Qwen2.5-7B MATH-500 solution − blind is +30.5 [+21.9, +40.0] in Table 48 and [+21.9, +39.1] in Table 37. Qwen2.5-14B answer − blind is [+22.1, +39.2] versus [+21.9, +39.4]. Fix the seed, or note that intervals come from separate bootstrap runs.
- **Table order.** Table 27 ("Sources of the cells of Table 44") sits in Appendix H, 17 tables before the table it annotates in Appendix N.
- **Table 3 is incomplete.** It lists MACE judges as Qwen2.5-7B, phi-4 and Sonnet 5, but Qwen3-8B and 14B were run on a MACE subsample, and the 120-task replication subsample with Qwen3 and MT-Bench is missing.
- **Ambiguous antecedent.** Appendix N, "Thinking on versus off", ends with "With thinking on, blind verification AUROC is 0.86 ... and 0.81", which follows the Qwen3-14B sentences but sits in the Qwen3-8B paragraph. The factual 0.81 is Qwen3-14B's; Qwen3-8B's is 0.80. Name the model.

**P13. LaTeX font warning.** The log reports `OT1/ptm/m/scit undefined` twice: small caps inside italics, probably a `\textsc{}` inside an `\emph{}` or a caption. Check that the rendered text is not silently substituted.

**P14. Prose that reads machine-dense.** Examples to break up:
- Table 1 caption: "a mark on a range means the range includes such a value". Write "a mark on a range applies to at least one value in it".
- l.188-190: the thinking AUROC sentence stacks four parentheticals. Split it: "Thinking does not change blind AUROC on arithmetic (0.85-0.86). On factual questions it raises it (Qwen3-14B 0.72 → 0.81), so better verification may contribute there."

---

## 4. Figure-by-figure and table-by-table critique

**Figure 1 (p.1) is near the bar; keep its design.**

Strengths:
- It is the right figure on the right page: a concrete task, the same text under three prompts, then the pool-level effect.
- The example selection is disclosed, with a selection rule in Appendix A, which pre-empts the cherry-picking objection.
- Panel (c) values match `tables/r4_rotation.tex` and `tables/rotation_exact.tex`: +5.25/−5.41, +4.09/−3.92, +3.04/−2.66, with n = 120/93/113.

Issues:
1. The note in panel (b) (P2).
2. Panel (c)'s grey "matches neither" bars carry no value labels, although the text relies on them ("barely moves"). Add +0.1, +0.3, +0.0.
3. Panel (c) does not say that Sonnet 5 is API while Figure 3(a)'s Sonnet 5 is CLI (−2.7 versus −2.85). Add "API" to the x label.
4. Colors are consistent with the appendix (orange for blind, blue for referenced); good.

**Table 1 (p.3): right concept, too dense.**
- Its best feature is the "Tests" column that ties each prediction to the readings; keep it.
- Problems: M1b (P1 verdict), P3 (density and undefined terms).
- The "Not predicted: a thinking mode" row is honest and useful; keep it.

**Equation 1 (p.3): earns its space.**
- It shows why P2 needs more than P1 (β<1 or γ>0), and "it is not a fitted model" is the right hedge.
- Consider reusing λ in Section 4's text ("swapping a⋆ moves fixed text by about λ; we estimate 3-5 points"), so the model is used after it is introduced rather than left as scaffolding.

**Figure 2 (p.6): the content is right, the layout is not unified.**
- The forest-plot form suits the claim, and the grey boxed-only ticks are a good compact robustness cue.
- Problems: P8 (row sets and grammar), a 150-word caption.
- The title claims "degrades grading for every screened judge and Sonnet 5", but panel (b) shows only two screened judges on the replication pool and on MACE. Qualify it with "on the pools each was run on", or fix via M4.
- The x-axis label "change in best-of-64 accuracy (pp)" is fine; the tick labels are legible at 100 dpi.

**Figure 3 (p.7): needs the most work.**
- Panel (a) puts two designs on one axis with the instruction "should be compared only within a group". A figure that tells readers not to compare its rows is a design smell. Either separate the groups with a visible gap and separate row headers, which is partly done, or move the three Sonnet 5 CLI values to a small inset or into the text.
- Panel (b): M5 (plotted quantity, the double meaning of "thinking off", 17.5 versus 36).
- The bar value labels are small and grey. Increase contrast.

**Table 2 (p.8): useful, but framed to understate costs.**
- See M3c and P4.
- Its values check out against `tables/protocol_exact.tex`:
  - k-pool −30.3/−3.0/−3.0/−15.2 and +3.0/+3.0/+0.0/+3.0.
  - AUROC −0.23/−0.17/−0.19/−0.25 and +0.00/−0.03/+0.00/−0.01.
  - MACE +9.0/+11.3, +9.8/+11.3, −0.08/−0.06, −0.01/−0.01.
  - MATH-500 +28.6/+30.6, +23.8/+29.7, +0.29/+0.25, +0.24/+0.22.
- The problem is what the table leaves out: the max rule's cost against the reference, and the full-solution condition.

**Appendix (not scored for the page limit).**
- It is thorough and honest.
- The ledger (Table 4) is exemplary in disclosing retroactive verdict changes in both directions.
- Issues: P12.
- 51 tables across 16 appendices is heavy. Appendix A's first sentence, saying which appendices support main-text claims, is exactly the right navigation aid; keep it.

---

## 5. What is already at the bar (leave alone)

- **Title.** Memorable, states the finding, and the "answer key" metaphor carries through the whole paper.
- **First intro paragraph** (l.057-061). A concrete example with numbers, then the pool-level generalization, and it discloses that the example "swaps more than most". This is best-paper-style opening.
- **Three-readings framing with predictions mapped to sections.** P1/P2/P3 become the section titles, and each section ends with an explicit "Verdict" paragraph. Keep this skeleton.
- **Controls.**
  - Byte-identical text, with a "matches neither" placebo.
  - A program-enumerated answer set, which removes incomplete gold lists as a confound, and the related-work sentence at l.441-442 makes that point well.
  - The MATH-500 unique-answer contrast.
- **Honest negative results in the main text.**
  - MACE selection null against a registered prediction of a loss (l.399-402).
  - The failed distance ordering (l.223-224).
  - The failed instruction test for small judges (l.355-357).
  - The weak GPT-4.1 effect.
  - The DPO null in Limitations.
- **Limitations** (p.9). Specific, prominent, and they include the retroactive verdict rule. Keep it as a bulleted list; fix only the max-rule bullet (M3a).
- **Number accuracy.** I checked about 45 main-text numbers against table sources, including Figure 1c, the P1 swap values, the masking percentages (94/77/38%), the thinking toggles (1.98/0.12, 0.69/+0.01, 44.3/21.6, 41.6/17.8, AUROC 0.85/0.86/0.72/0.81/0.78/0.80), Sonnet 5's P3 rates (18.5%/8.7%/14.9%, 0/111 versus 12/111), MACE (+29.4/+26.5, +2.0/+6.1, +9.0/+11.3), the k-pool no-match losses (−63.6/−45.5/−18.2/−9.1), prevalence (0/2.5/2.5/30.0%), the ledger counts, and the Ties ladder. Apart from the items in M2, M3b, M5c and P6, they match. This is a well-audited paper.
- **Page limit.** The main text fits in 9 pages, and the statements and references start on page 10.
- **Related work.** Positioned by what prior work did *not* vary, which is the right way to claim novelty. It is concise.

---

## 6. What would move the score up one and two points (no new experiments)

**+1 (to 7): fix every internal contradiction and scope the headline.** All text edits:
1. M1: intro summary, P1 verdict and Table 1 verdict.
2. M2: conclusion rewrite.
3. M3a and M3b: the Limitations/Section 7 contradiction on the max rule, and the unsourced interval.
4. M5: Figure 3 caption and labels.
5. M6: registration marks and the full ledger counts.
6. M8: the abstract rewrite, with two or three concrete numbers, the moderators, and the correct "two rule out, one separates" framing.

After this, every summary sentence in the abstract, intro, table, verdicts and conclusion says the same thing the evidence says. That is the reliability bar this AC cares about most. Estimated effort: one careful editing pass.

**+2 (to 8): also make it a paper a reader can hold in their head, and close the P3 gap.**
1. **M4, the core-cast restructure.** Cut the Ties, Mistral, earlier-scorer and extra-labeling detail from the main text, and add a four-row "Setup at a glance" table. The target is a Section 5 that a skimmer reads as: "Four open judges lose 0.17-0.27 AUROC, Sonnet 5 0.04-0.15, GPT-4.1 ≤0.04; with a unique answer the reference helps."
2. **M3c, reframe Section 7.** Present the max rule as a safeguard whose costs are shown in Table 2 ("Max rule − reference" row, full-solution column; all values in `r16c_protocols_exact.json`), and retitle the section (P1).
3. **M7, the P3 re-analysis.** Report the share of wrong answers Sonnet 5 scores 10 blind in the stored 16-candidate subsamples, and add the sentence on the cross-interface noise floor. This turns the paper's one distinguishing claim from "persists on accepted answers" into "persists on answers the judge verified", or honestly scopes it.
4. **P8, a unified Figure 2 layout.** Same rows in both panels, registration marks on the row labels, and a 60-word caption.

Together these would give the paper what the "Mirage" bar asks for: one question, one concept figure, main results on pages 1-3, every number in the main text traceable and consistent, and the appendix as pure expansion.
