# Round 20 Area Chair review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

Reviewed from `round20_main.pdf` (46 pages: main text pp. 1-9, statements pp. 9-10, references pp. 10-12, appendix pp. 13-46). I read the pages as rendered images, including 220-dpi renders of pp. 1, 5 and 6. I checked numbers against `main.tex`, `appendix.tex`, `tables/*.tex`, `papers/analysis/*.json`, `registration_round19.md` and `registration_round20.md`. Line numbers are the PDF margin numbers. The previous review was read only for the audit in Section 4; the score here is independent.

---

## 1. Summary of the claims and how easy they were to extract

**Question.** When a question has several correct answers, does a reference-guided LLM judge treat the reference as an answer key? Under an answer key, a correct answer scores the same whichever correct answer is shown.

**Claims as extracted:**

1. **P1, the swap.** Moving the reference between two correct answers moves the score of byte-identical text.
   - 2.7-5.4 points out of 10 for Qwen2.5-7B, phi-4 and Sonnet 5 on 120 constructed tasks.
   - 3.2-5.0 on 9 MathConstraint puzzles.
   - The pull depends on how explicitly the answer is stated: it survives words, mostly vanishes as an expression, and vanishes when masked.
2. **P2, grading harm.** Correct answers that differ from the reference lose ground against wrong answers.
   - Grading AUROC falls 0.17-0.27 for four open judges on arithmetic pools (0.07-0.14 counting boxed replies only).
   - It falls 0.15-0.16 for Sonnet 5 and Opus 5 on MACE, where false rejections rise 36 pp.
   - With one correct answer the reference helps (+29-31 pp best-of-64 on MATH-500).
3. **P3, not only verification failure.** Among correct answers a judge accepts blind, those that differ from the reference drop to 3 or below with the reference far more often than those that match.
   - Sonnet 5 19% and Opus 5 31% on MACE; matching answers 0%.
   - A same-interface second blind call gives 2 of 843.
   - The pattern repeats for four open judges at a threshold that about 3% of wrong answers pass.
4. **Moderators.**
   - Thinking shrinks the arithmetic swap to near zero but only about halves the factual false-rejection rise.
   - A full-credit sentence cuts the factual rise (36 to 18 pp Sonnet 5; 36 to 8 pp Opus 5), but grading AUROC stays below blind.
5. **Consequence.** Sonnet 5 grading one answer per model on 149 multi-answer MACE questions: with the reference, accuracy falls 13-40 points below the answer list (Haiku 4.5 drops from 95% to 55%, level with Llama-3.1-8B); blind, it stays within 3 points.
6. **Safeguard.** Keeping the higher of blind and referenced scores (the max rule) holds grading AUROC within 0.03 of blind. It costs up to 6.7 pp when the answer is unique.
7. **Registration.** 176 registered predictions: 109 confirmed, 11 not confirmed, 16 falsified, 17 split, 23 not evaluable, not scored or excluded.

**What a skimming reviewer takes away in 2 minutes** (title, abstract, Figure 1, Table 1):
- The swap is real and large, and the effect is not only a failure to verify.
- Thinking helps on arithmetic.
- Reference-guided judging distorts a benchmark leaderboard.

That is the right takeaway, and it arrives faster than in round 19. The abstract is still 254 words, and its benchmark sentence reads as a general property of "a judge" on "factual questions" rather than one judge on 149 multi-answer questions.

**In 10 minutes** (plus Figures 2-3 and Table 2), the reader also gets:
- the one-answer positive control;
- P3 extended to six judges with a proper noise control;
- the instruction and thinking moderators;
- the max rule.

The reader also meets 27 numbers in each of the two central paragraphs of Sections 5 and 6, three interfaces, four labelings, and a Table 2 whose three sub-messages (benchmark, sentence, max rule) and 32-word title take several passes. Two things will trip a careful skimmer:
- **P2 verdicts that disagree.** Table 1 says P2 is small for GPT-4.1 on one pool; Section 5 says both pools.
- **A MACE accuracy row labeled "Several correct answers" that is actually the natural mix.**

**Overall.** The paper now answers its question with the controls it needed and gives a real "why it matters" result. What stands between it and the best-paper bar is presentation density and a handful of claims stated more broadly or more cleanly than their evidence.

---

## 2. Score and confidence

**Score: 7 / 10** (accept; clearly above threshold, not yet a top-tier accept). **Confidence: 4 / 5.**

**Single biggest reason.** The science is now sound and the story is right.
- **Swap, positive control, P3.** The swap is byte-identical, the one-answer positive control is there, and P3 now holds with a same-interface noise control (0/318, 2/525) on two frontier judges, with a matched-threshold analogue on four open judges.
- **Consequence.** The benchmark result gives the paper a real consequence.

It stops short of an 8 for three reasons:
1. **Broad claims on narrow evidence.** The headline consequence is stated for "a reference-guided judge" on "factual questions". It rests on one judge that grades its own answers, on 149 multi-answer questions from two MACE domains. An analysis that complicates it (open judges as benchmark graders, `r20e_benchmark_open_judges.json`) was computed and left out.
2. **Factual P3 coverage.** P3 on factual questions, the paper's most striking finding, rests on two models from one provider.
3. **Density.** The main text remains a number ledger (M11 of round 19 is not fixed). Several verdict statements disagree with each other or with the table beside them.

None of these needs large experiments. Most are rewrites and re-analyses of stored scores.

---

## 3. Ranked issues

### MUST FIX

#### M1. The benchmark consequence is stated beyond its evidence, and a relevant computed analysis is omitted
**New data: none required (re-analysis and text). Optional small run for the 8: about 1.2k API calls.**

**Location.**
- Abstract ll. 024-027: "with the reference, Claude Sonnet 5 as a judge lowers four models' accuracy on factual questions by 13 to 40 points, and without it stays within 3 points of the answer lists".
- Conclusion ll. 470-471: "a reference-guided judge under-reports benchmark accuracy by 13 to 40 points".
- Section 7 ll. 351-359; Table 2a; Limitations l. 448.

**Problems.**
1. **Scope creep.**
   - "a reference-guided judge" (conclusion) and "on factual questions" (abstract) generalize from one judge (Sonnet 5, thinking disabled) on 149 MACE questions, all selected to have several correct answers (R20-C: "all MACE River and Language questions with more than one correct answer").
   - On the natural benchmark mix (a quarter of these domains have k=1, where the reference helps), the shortfall would be smaller. The reader cannot tell by how much.
   - Two of the four generators are at ceiling on the answer list (98.7%, 100.0%).
   - The judge grades its own answers (disclosed, l. 358).
2. **An analysis was computed and not reported.**
   - `papers/analysis/r20e_benchmark_open_judges.py` is headed "POST HOC (round-19 review, M10 minimum)". Its output was rendered to `tables/r20_benchmark_open.tex` by `make_tables.py` (l. 1001-1007), but no `\input` in `main.tex` or `appendix.tex` uses it.
   - It grades Llama-3.1-8B's 64 samples per question on the same 150 MACE multi-answer questions with the open judges:

     | Judge | Answer list | Blind | Referenced | Referenced − list |
     |---|---|---|---|---|
     | Qwen2.5-7B | 60.7% | 39.8% | 14.0% | −46.7 pp [−52.4, −40.9] |
     | phi-4 | 69.5% | 54.1% | 22.1% | −47.5 pp |

   - Correct answers that differ from the reference are credited 55.7% blind against 0.5% referenced (phi-4: 70.5% against 1.4%).
   - This result cuts both ways, and both matter:
     - **It strengthens the paper.** A referenced open judge credits almost none of the differing correct answers.
     - **It limits the abstract and the recommendation.** For judges that cannot verify factual answers, the blind score also undercounts by 15-21 points. "Without it stays within 3 points of the answer lists" is a property of Sonnet 5, not of blind judging.
   - The conclusion's advice ("should report blind as well as referenced scores") needs that qualifier.
   - A paper whose credibility rests on "all reported" should not leave a directly relevant analysis in a table file. It is post hoc, but it was run to answer a reviewer, and its outcome is informative.
3. **Thresholding.** "a score of 7 or above counts as correct" is one choice. Stored scores give the 5 and 10 thresholds for free.

**Fix.**
- **Abstract**, replace ll. 024-027 with:
  > "The effect reaches benchmark scores: on 149 factual questions with several correct answers, Claude Sonnet 5 as a reference-guided judge scores four models 13 to 40 points below their answer-list accuracy, against at most 3 points when it grades blind."
- **Conclusion l. 470-471:**
  > "... and on factual questions with several correct answers a reference-guided judge scored four models 13 to 40 points below their answer-list accuracy."
- **Section 7**, add after l. 356:
  > "Weaker judges show the same pull but cannot serve as the blind baseline: graded by Qwen2.5-7B and phi-4, Llama-3.1-8B's accuracy falls 47 points below the answer list with the reference and 15 to 21 points without it (Appendix K).†"
- **Appendix K:** add `r20_benchmark_open.tex` as a table, with the threshold-5 and threshold-10 variants of Table 46.
- **Conclusion recommendation:** "report blind as well as referenced scores *from a judge that verifies the domain*, or supply the full answer set".
- **Limitations, Tasks bullet:** "the benchmark study uses one judge, which also grades its own answers, on multi-answer questions only".
- **Optional run (for the 8).** Grade the same 596 answers with Opus 5 and GPT-4.1, blind and referenced (about 2.4k calls, under USD 15). This removes the self-grading objection and the one-judge objection in one step.

#### M2. P3 "for all six judges" hides that the factual case rests on two same-provider models; stored data would extend it
**New data: re-analysis only (minutes).**

**Location.** Intro l. 092-093 ("P3 for all six judges on which we could test acceptance"); Table 1 P3 row l. 128-132 ("Holds for all six judges tested"); Section 6 ll. 321-323; Verdict ll. 344-347; Figure 3a.

**Problem.**
- **Where the four open judges were tested.** They are tested only on the arithmetic pools (`r20d_matched_acceptance.json` covers `repl` and `kpool` only). On arithmetic, the verification-failure reading is already implausible for strong judges, and the frontier shares are small (3%-15%).
- **Where P3 is striking.** The factual case (19%, 31%) rests on Sonnet 5 and Opus 5, both Anthropic models through one API with one prompt.
- **Stored data would extend it.** Qwen2.5-7B and phi-4 have blind and referenced scores on the full MACE pool with wrong answers. These are the same score files used for Table 11 and in `r20e`.
- **Qwen3 on MACE is relegated.** It is in Table 44 with the note "we report them for completeness" because 12-24% of wrong answers score a blind 10. Yet Qwen3-8B thinking off shows 53.8% against 0.9%, and thinking on 23.4% against 2.0%, on factual questions. That is evidence for P3 on a thinking judge, with a stated caveat, and it belongs in the P3 paragraph.
- **"Matched" threshold is unexplained (l. 345).** The threshold is matched to nothing the reader can see. The 3% was chosen to approximate Sonnet 5's blind-10 wrong-answer rate (script header of `r20d_matched_acceptance.py`), but Opus 5's rate is 5-8%.

**Fix.**
1. Extend `r20d_matched_acceptance.py` to MACE k>1 for Qwen2.5-7B and phi-4 (answer-list labels, 3% wrong-answer threshold). Add the rows to Figure 3a under "Factual (MACE)" and to Table 44.
2. Table 1 P3 verdict: "Holds for all six judges tested (factual questions: Sonnet 5 and Opus 5 [plus open judges if step 1 holds])".
3. Section 6 l. 321: "we set the blind threshold that at most 3% of wrong answers reach, about Sonnet 5's rate for a blind 10".
4. Section 6: add one clause on Qwen3 at a blind 10 on MACE (54% against 1% thinking off; 23% against 2% thinking on), "a weaker acceptance test because 12% to 24% of wrong answers also receive a 10".
5. Limitations, Judges bullet: say that P3 on factual questions was tested with a noise control only on the two Anthropic judges.

#### M3. Table 2b labels natural-mix MACE accuracy as a "Several correct answers" result
**New data: no (re-analysis of stored scores).**

**Location.** Table 2b rows ll. 401-403 under the header "*Several correct answers*"; caption ll. 385-386 ("MACE accuracy covers its natural mix of one and several correct answers (133 tasks)"); Section 7 ll. 363-364.

**Problem.**
- The MACE best-of-64 accuracy cells (+9.0, +11.3 with the reference; +9.8, +11.3 max rule) sit under "Several correct answers". They are the natural mix, and the rise is driven by the 34 k=1 tasks (+29.4 and +26.5). On k>1 the changes are +2.0 and +6.1 (Table 49).
- A skimmer reading only Table 2 concludes that on multi-answer factual questions the reference *raises* selection accuracy by 9-11 pp. That is the opposite of the paper's message, and it is not what the data say.
- The max-rule k>1 MACE accuracy is not reported anywhere. Only the natural mix appears (Table 16 bottom).

**Fix.**
- Replace the two MACE accuracy cells with the k>1 values (+2.0, +6.1), and compute max-rule k>1 from stored scores.
- Alternatively, move the natural-mix values to a separate row group "*Natural mix (MACE, 133 tasks)*".
- Update the caption and Section 7 l. 363-364 accordingly.

#### M4. The P2 verdicts disagree with each other and with the data; Figure 2 omits Opus 5's constructed-pool rows
**New data: no.**

**Location.** Table 1 P2 verdict l. 120-124; Section 5 Verdict ll. 308-310; Section 5 ll. 266-269; Figure 2 and its caption l. 248.

**Problems.**
1. **Table 1 and Section 5 give different GPT-4.1 verdicts.**
   - Table 1: "small for two judges on one arithmetic pool each". That can only mean GPT-4.1 on the k-pool and Opus 5 on the replication pool.
   - Section 5: "for GPT-4.1 on both constructed pools and Opus 5 on the replication pool the fall is small".
2. **The classification is not consistent with the numbers.**
   - GPT-4.1 on the replication pool: −0.038 [−0.06, −0.02] (`r8_lenient_results.json` pools.repl|all.GPT-4.1.lenient; Table 27).
   - Sonnet 5 on the replication pool: −0.037 [−0.068, −0.011] (`r8_sonnet_results.json` repl.lenient.G_nm).
   - Section 5's Verdict classes the identical Sonnet 5 value as "holds" and GPT-4.1's as "small".
3. **"Holds for every judge on factual questions" (Table 1)** reads as "all nine judges". GPT-4.1, Qwen2.5-14B and gemma-2-9b were never run on MACE, and the Qwen3 judges were measured by false rejections, not AUROC.
4. **Figure 2b omits Opus 5's constructed-pool rows.**
   - The legend lists "Opus 5, 16 candidates", and the MACE Opus row is plotted.
   - The replication (−0.015, interval includes zero: the one failed Opus P2 prediction, P-R19A1) and k-pool (−0.057) rows are sent to Appendix K (caption l. 248).
   - The plotted data should not omit a judge's null in the pool where it occurred. The data are in `r19a_opus_results.json`, so two rows cost nothing.
   - The Sonnet 5 adaptive-thinking MACE value (−0.090) belongs in the same panel.

**Fix.**
- **Replace Table 1's P2 verdict with:**
  > "Holds for all four judges run on factual questions; on arithmetic pools it holds for the four open judges, and falls are small (≤0.04) for Sonnet 5 and GPT-4.1 on the replication pool, GPT-4.1 on the k-pool, and Opus 5 on the replication pool."
- **Replace Section 5's Verdict with:**
  > "P2 holds for every judge we ran on factual questions (Sonnet 5, Opus 5, Qwen2.5-7B, phi-4) and for the four open judges on the constructed pools. For the API judges the falls on constructed pools are small: 0.04 for Sonnet 5 and GPT-4.1 on the replication pool, 0.02 (interval including zero) for Opus 5 there, and 0.01 for GPT-4.1 on the k-pool."
- **Figure 2:** add "replication, Opus 5" and "k-pool, Opus 5" rows in panel b, "not shown: subsamples" in panel a, and optionally "MACE, Sonnet 5 (thinking)". Delete "Opus 5 on the constructed pools is in Appendix K" from the caption.

#### M5. The main text is still a number ledger (round-19 M11 not fixed)
**New data: no.**

**Location.** Section 5 "Several correct answers" ll. 261-269; Section 6 "Answers the judge accepts" ll. 315-323 and "A thinking mode" ll. 335-342; Section 7 "Benchmark scores" ll. 351-359 and "What helps" ll. 369-377; Section 3 ll. 159-200.

**Problem.**
- **Density.** A count of numeric tokens per paragraph in `main.tex`:

  | Paragraph | Numeric tokens |
  |---|---|
  | Section 5, "Several correct answers" | 27 |
  | Section 6, acceptance | 27 |
  | Section 6, thinking | 23 |
  | Section 7, benchmark | 22 |
  | Section 7, selection | 16 |
  | Section 4, first paragraph | 18 |

  The model paper keeps to roughly three per paragraph and lets figures carry the rest.
- **Terms.** Section 3 still introduces about 18 terms in one page: replication pool, k-pool, core judges, explanation first, thinking mode, CLI, any-format labels, registered labels, model-read labeling, boxed replies, swap change, false-rejection rate, grading AUROC, best-of-64 accuracy, exact expected score, primary endpoint, inflation measure, and three registration marks.
- **Undefined terms.** Some main-text terms are never defined:
  - "margin between matching and non-matching correct answers" (l. 253, l. 331) is used as a measure but never defined in Section 3;
  - "blind-then-reveal" (l. 376) is never defined in the main text;
  - "a best-of-64 inflation measure" (l. 197) is named but not explained.
- **Parallel numbers.** Section 6 l. 321 quotes "3% to 15%" (per pool), while Figure 3a beside it shows the pooled 4% and 11%.

**Fix (concrete cuts):**
1. **Section 5 "Several correct answers".** Keep the three sentences that carry P2 and move the rest to Figure 2 or Appendix J/K:
   > "Correct answers that differ from the reference are rejected more often: Qwen2.5-7B scores 28% of them 3 or below with the reference against 0.4% blind. Grading AUROC against wrong answers falls by 0.17 to 0.27 for the four open judges on constructed pools (0.07 to 0.14 counting boxed replies only) and by 0.15 and 0.16 for Sonnet 5 and Opus 5 on MACE (Figure 2b). On constructed pools the API judges fall by at most 0.08 (Appendices J, K)."
2. **Section 6 acceptance.** Cut to: definition of acceptance (one number: at most 4%/8% of wrong answers); the factual result (19%, 31%, 0%); the noise control (0 of 318, 2 of 525); the open judges (5% to 57% against at most 0.4%). Delete "On arithmetic the shares are smaller, 3% to 15%"; Figure 3a shows it.
3. **Section 6 thinking.** Keep the arithmetic sentence with two numbers and the factual sentence with one range ("the rise in false rejections falls by 50% to 60%"). Move the Qwen3-8B ceiling diagnostic and the AUROC levels to Appendix L with a pointer.
4. **Section 7.** Turn Table 2a into a small slope figure: one line per model from answer list to blind to referenced to max rule. The Haiku/Llama crossing will be visible without prose. Keep one number in the text (−22 pp pooled).
5. **Section 3.**
   - Define "margin" in one clause, or replace both uses with "the gap between matching and non-matching correct answers".
   - Define blind-then-reveal in one clause where it is used, or drop the sentence at l. 376-377.
   - Delete "our OSF-preregistered primary endpoint, a best-of-64 inflation measure, was confirmed". The term is never used again in the main text; the ledger sentence already carries registration.

#### M6. Registration marks: several post hoc or unpredicted statements are unmarked
**New data: no.**

**Location and evidence.** The convention (l. 197-198) is "unmarked estimates were pre-specified ... † marks post hoc".

| Location | Statement | Evidence it is not pre-specified | Fix |
|---|---|---|---|
| l. 316-317 | "Sonnet 5 ... give a blind 10 to only 2% to 4% ... of the wrong answers" | Sonnet's rates come from post hoc `r19_sonnet_wrong_tens.py` (`registration_round19.md` context) | Add † after "2% to 4%" |
| l. 321 | "On arithmetic the shares are smaller, 3% to 15%" | Includes Sonnet 5's post hoc 8.7% and 14.9% (Figure 3 caption says Sonnet's referenced shares are post hoc) | Add †, or delete the sentence (M5) |
| l. 337-338 | "Qwen3-8B gives 96% of correct arithmetic answers a blind 10 and keeps that score" | Appendix H l. 1902-1903 and Appendix L l. 2161: "These diagnostics are post hoc" | Add † |
| l. 354-357 | "Claude Haiku 4.5 falls ... level with Llama-3.1-8B" and "The shortfall tracks how often the judge rejects ... not how many such answers the model gives" | `registration_round20.md` R20-C: "Reported without a prediction: rankings under the three graders ... and the relation between a generator's undercount and its share of correct answers that differ from the reference" | Add † to both |
| l. 328-329 | "from 36 to 8 pp for Opus 5" | R20-B registered only AUROC for Opus 5 (P-R20B2); the FR readout came from a frozen producer. Defensible as a pre-specified readout, but Table 45's caption calls the whole column pre-specified | Say "pre-specified readouts; predictions only for Sonnet 5's false rejections" in Table 45's caption |
| Table 1 "Not predicted" row, l. 133-136 | "*Not predicted:* thinking, or a full-credit instruction" | These moderators *were* registered: R19-B P-R19B3 (thinking fall smaller), R20-B P-R20B1-B4 (sentence), "Thinking arm has smaller loss (confirmed)" in the ledger | Relabel "*Moderators* (predicted in later registrations, not by Eq. 1)" |

#### M7. "A thinking mode removes the effect on arithmetic" overstates the data
**New data: no.**

**Location.** Abstract l. 022-023; Intro l. 093-094; Conclusion l. 472; Table 1 P1 verdict "near zero on arithmetic with thinking".

**Problem.**
- **Sonnet 5 (CLI) with thinking** still loses −0.32 [−0.67, −0.07] on the swap (Appendix L l. 2169-2170). The interval excludes zero: a 89% reduction, not removal.
- **Qwen3-14B**: −0.12 [−0.27, +0.00].
- **Interface and judges.** The only frontier arithmetic evidence is through the CLI, which Section 3 says is compared "only with each other". No thinking API run exists on arithmetic, and "a thinking mode" generalizes from three judges.
- **Ambiguous intro sentence (l. 093-094).** "removes the effect on arithmetic but only reduces it on factual questions, as does an instruction that any correct answer deserves full credit" lets the reader think the instruction also removes the effect on arithmetic. It was measured by grading only on MACE and replication for the API judges, and on the k-pool by margin, where it did not remove the effect.

**Fix.**
- **Abstract:** "(3) a thinking mode shrinks the effect to near zero on arithmetic (by about 90%) but only halves it on factual questions, and an instruction that any correct answer deserves full credit also reduces it without removing it."
- **Intro l. 093-094:** "A thinking mode shrinks the effect to near zero on arithmetic but only about halves it on factual questions; an instruction that any correct answer deserves full credit also reduces it on factual questions without removing it."
- **Conclusion l. 472:** "nearly removes".

#### M8. "The shortfall tracks how often the judge rejects ..., not how many such answers the model gives" is not supportable with four points
**New data: no.**

**Location.** Section 7 ll. 356-358.

**Problem.**
1. **The "not" claim rests on a narrow range.** Only four generators, and the explanatory variable spans a narrow 68%-78% (`r20c_leaderboard.json` share_correct_nonmatching 0.680-0.780).
2. **The "tracks" claim is close to an identity.** The undercount is, to first order, share differing × referenced rejection rate, measured on the same answers by the same judge.
3. **The ordering does not match.**
   - By rejection rate: Opus 11.0% < Llama 18.6% < Sonnet 23.4% < Haiku 41.8%.
   - By undercount: Llama 13.4 < Opus 14.8 < Sonnet 21.5 < Haiku 39.6.

   The claim is also unregistered (M6).

**Fix.**
> "The four models give similar shares of correct answers that differ from the reference (68% to 78%); the undercount differs because the judge rejects those answers at different rates (11% to 42%), highest for Haiku 4.5.†"

Keep it descriptive. If the authors want a claim about why the judge rejects Haiku's answers more (terser answers? rarer entities?), say that it is untested.

---

### POLISH

1. **Abstract.**
   - 254 words.
   - "3 to 5 points" is inconsistent with 2.7-5.4 in Table 1 and the Conclusion; use "about 3 to 5".
   - "We test nine judges, from 7B open models" undercounts: Mistral-7B, Ministral-8B, Qwen2.5-1.5B and 3B, and Llama-3.1-8B also judge in the appendix. Write "nine judges in the main text".
   - Listing MBPP among test beds, where the canonical program added no effect (Appendix P), implies support; write "and, in smaller studies, MathConstraint and MBPP".
2. **"both multi-answer pools" (l. 371).** The paper has three multi-answer pools (replication, k-pool, MACE k>1). Write "on the k-pool and MACE".
3. **Worked-solution baselines (l. 253-254).** "+5.17 to +3.73" is the full k-pool, but "+2.97 to +0.05" starts from a different visible-solution baseline (21 single-number tasks). A reader sees the "visible" condition at 3.73 and at 2.97 in one sentence. Say "(on the 21 single-number tasks, +2.97 visible against +0.05 masked)".
4. **"such answers" (l. 319).** It refers back to factual answers, but 318 and 525 are pooled over three pools. Write "0 of 318 accepted non-matching answers across Sonnet 5's three pools".
5. **Table 1, "Not predicted" row.** "both roughly halve the rise" understates the Opus 5 sentence result (36 to 8, a 78% cut; registration R20-B "cuts it by three quarters"). Write "halve it or more".
6. **Rounding mismatches a number-checking reviewer will flag:**
   - Opus 5 replication false-rejection rise: +3.6 in Table 45 (`r20g_frontier_safeguards.json` FR_ref_minus_blind 0.0365) against +3.7 in Appendix K and `registration_round19.md`.
   - Full-solution max-rule AUROC cost: "0.15" (l. 374), but Table 2b prints +0.29 → +0.13 (0.16 by subtraction). Print the paired difference or two decimals consistently.
   - "within 2 points of the answer lists" (l. 372): Table 2a gives Sonnet 5 96.6 against 98.7 (2.1 by subtraction; JSON −0.0201). Write "within about 2 points".
   - Opus 5 MACE AUROC: "0.16" (l. 266) against "−0.165" in Table 45 and the registration. The true value is −0.1645; print −0.164 in Table 45.
7. **Table 3 (p. 13).** "on a 120-task subsample" is still there (round-19 P2). It is all 120 tasks with up to three candidates per type.
8. **Table 16 bottom block (p. 26, ll. 1375-1382) is still illegible (~5 pt).** Table 46 (p. 40) is also ~5 pt, and Tables 43-44 (p. 39) are ~6 pt after `adjustbox` shrinking. Split columns or use two-line headers at `\footnotesize`.
9. **Appendix Table 12 (p. 23, ll. 1212-1214)** still carries the superseded CLI noise floor ("0 of 111"). Delete it or tag it "superseded by Table 43".
10. **Figure 1c.** Draw a dashed zero line labeled "answer key: 0". The caption sentence "An answer key predicts zero for every bar" should be visible in the figure. Add "(points out of 10)" to the y label.
11. **Figure 2.**
    - The italic "not shown: ..." labels are drawn across the zero line in panel a (ll. 227-237). Left-align them in the empty space.
    - The grey boxed-only ticks overlap the GPT-4.1 triangles in panel b (ll. 227, 232).
12. **Figure 3.**
    - **Panel a:** for the API rows, the orange crosses (second blind call) sit exactly on the open circles at 0 and cannot be told apart (ll. 273-276 at 220 dpi). Offset crosses vertically by a quarter row, or print "retest 0/318" as text.
    - **Panel b:** the value labels "0.32" and "−0.01" collide with the dark bars and whiskers.
    - **Panels b and c:** the Sonnet 5 interface differs (CLI in b, API in c). Label it in the y tick (done) and in the legend.
    - **Fonts:** minimum printed glyph height is 7.5 pt (value labels) in both Figures 2 and 3. Acceptable.
13. **Table 2 title** is 32 words carrying three messages. Split Table 2a (benchmark) into its own small figure or table (see M5.4) and shorten the title of the safeguards table to "What helps: a full-credit sentence reduces the harm; keeping the higher score restores grading at a cost on unique answers".
14. **Table 1 has no row for the benchmark consequence**, although the abstract gives it a sentence and Section 7 opens with it. Add a row: "*Consequence*: benchmark accuracy | — | Sonnet 5 scores four models 13-40 points below the answer list with the reference, within 3 blind | Holds (one judge)".
15. **P2 "Rules out the answer key" (Table 1 Tests column).** An answer key with β<1 plus noise could also lower AUROC. The argument works only together with the one-answer positive control. Write "With P2′, rules out the answer key".
16. **"matched threshold" (l. 345).** See M2.3.
17. **Human validation of the any-format labels** (round-19 M6) is still absent. It matters less now that the frontier and MACE results carry P2 and P3, but the open-judge constructed-pool magnitudes (Table 1, Figure 2b) still rest on these labels. A 200-reply human check remains cheap.
18. **Appendix vocabulary** (round-19 P13) is only partly cleaned:
    - "gainers", "losers", "placebo" remain (Appendix H ll. 1840-1842), as does "wedge" (Appendix Q l. 2406);
    - the "git status listing recent commit messages" disclosure is still two sentences (Appendix J ll. 1944-1946).
19. **No blind-then-reveal column in Table 2** (round-19 P17). The registered protocol's failure on grading is the natural comparator for a post hoc max rule chosen from five combinations. One column from Table 16 would pre-empt the objection.
20. **Page 46** holds only Table 55. Float it up, or merge it into Table 54's page.

---

## 4. Audit of round-19 items

### MUST FIX

| Item | Status | Evidence in this version |
|---|---|---|
| **M1** P3 noise floor: wrong interface, wrong pool, one judge | **Fixed** (residual coverage gap, M2 above) | R20-A same-interface API retest on all three pools for Sonnet 5 and Opus 5: 0/318 and 2/525 (l. 318-320; Table 43; `r20a_*_retest.json` matches exactly). Opus 5 added (R19-A). Matched-threshold acceptance for four open judges (Table 44; `r20d`). Verdict rewritten (l. 344-347). Residual: factual P3 only on the two Anthropic judges; open judges tested on arithmetic only. |
| **M2** GPT-4.1 exception unexamined | **Partly fixed** | Text fixed: the abstract no longer attributes "the effect" to GPT-4.1; Section 5 l. 268-269 says "we did not run it on MACE"; Limitations l. 452-453. No new GPT-4.1 runs (no swap, no MACE subsample, no 20-logprob rescoring). Opus 5 now answers the "stronger frontier judge" question, which lowers this item's weight. The verdict text on GPT-4.1 is now internally inconsistent (M4 above). |
| **M3** Abstract imprecise, overclaims safeguard and breadth | **Mostly fixed** | Three readings stated plainly (l. 017-019); max-rule overclaim removed; P3 claim included. Remaining: 254 words; MBPP still listed as a test bed; verdict counts only as "176 registered predictions, all reported" (counts are in Section 3 l. 199-200, acceptable); a new overgeneralized benchmark sentence (M1 above). |
| **M4** Conclusion contradicts Section 5 | **Fixed** | The AUROC level ranges are gone. A recommendation is included (l. 473-475). New issue: "a reference-guided judge under-reports benchmark accuracy by 13 to 40 points" (M1 above). |
| **M5** Instruction confound misreported and under-measured | **Fixed** for the rewrite and for frontier judges; **not done** for open judges | l. 328-333 describe both instructions correctly and drop the undefined Qwen2.5-1.5B/3B names. R20-B measures the full-credit sentence by false rejections and grading AUROC for Sonnet 5 (MACE, replication) and Opus 5 (MACE) (Table 2b, Table 45; values match `r20b_*_instruction.json`). Not done: the forward-pass re-scoring for Qwen2.5-7B and phi-4. Limitations l. 454 discloses this. |
| **M6** P2 magnitude on post hoc, unvalidated labels | **Partly fixed** | Table 1 P2 row now shows both ranges (l. 121-122: "0.17-0.27 ... (0.07-0.14 counting boxed replies only)"). No human labels (Limitations l. 443-445 still says "not checked against human labels"). |
| **M7** Worked-solution wording | **Fixed** (minor baseline mismatch, Polish 3) | l. 252-254: "A worked solution that ends in the answer keeps most of the margin ... masking the answer inside that solution removes it". |
| **M8** Figure 2 title overclaim and garbled registration sentence | **Fixed** | The title now reads "... except GPT-4.1 on the k-pool, and clearly lowers selection accuracy only for Qwen2.5-7B" (l. 241-243). The registration sentence is clear (l. 248-249). New issue: Opus constructed rows omitted (M4 above). |
| **M9** Inconsistent registration marks | **Fixed for the listed items**; new errors introduced | l. 362-363 "+2.0 and +6.1" unmarked; l. 303-304 "29.4† and 26.5" (phi-4 unmarked); Table 2 caption lists what is pre-specified; l. 263 "(registered labels)". New unmarked post hoc statements in round-20 text (M6 above). |
| **M10** "Why it matters" weak | **Fixed, and better than asked** | R20-C benchmark study with four generators (Table 2a, Table 46; all values match `r20c_leaderboard.json`). But the requested "minimum" stored-data analysis was run (`r20e`) and not reported (M1 above). |
| **M11** Cognitive load | **Not fixed** | Some cuts: CLI caveats moved out; the ledger in one sentence; the tercile sentence gone. But round-20 additions raised the density of Sections 6-7. Numeric tokens per paragraph: 27 (Sec. 5), 27 and 23 (Sec. 6), 22 and 16 (Sec. 7). Undefined terms remain ("margin", "blind-then-reveal"). |

### POLISH items I consider important

| Item | Status | Evidence |
|---|---|---|
| P1 phi-4 rounding 6 vs 7 | Fixed | The "6 pp, as phi-4's do" sentence is gone. |
| P2 "120-task subsample" | Partly | Figure 3 caption fixed (l. 296-297); Table 3 (p. 13) unchanged. |
| P3 91 vs 99 tasks | Fixed | Table 2 caption l. 386. |
| P4 model: why P2 rules out an answer key | Fixed | l. 149-152. |
| P5 P2′ "Tests" cell | Fixed | "Positive control (every reading allows it)". |
| P6 failed predictions per row in Table 1 | Fixed | Caption l. 111-113. |
| P7 Sonnet selection contradiction | Fixed | API accuracy cells now "—". |
| P8 hedged novelty | Fixed | l. 071 "has not, to our knowledge, been tested". |
| P10 Figure 1c zero line and axis label | Partly | Caption sentence added; no line in the figure; axis label unchanged. |
| P11 Table 16 bottom block illegible | Not fixed | p. 26. |
| P12 scorer × labeling key | Not fixed | No key at the start of Appendix G; captions tag scorer and labeling individually. |
| P13 internal vocabulary | Partly | Appendix A explains "rotation" and "anchoring margin"; "gainers/losers/placebo", "wedge" and the git-status disclosure remain. |
| P15 empty rows in Figure 2a | Fixed | "not shown: ties / subsamples". |
| P17 blind-then-reveal column in Table 2 | Not fixed | One sentence at l. 376. |
| P18 power of the n = 40 CLI thinking comparison | Fixed by data | R19-B API adaptive-thinking run. |
| P19 max rule "for the four open judges" | Fixed | The max rule is now reported for the API judges too. |
| P20 AI statement wording | Fixed | l. 486-487 "we checked every quoted number". |

### Numbers spot-checked (47 checks; no substantive error found)

| # | Quoted (location) | Source | Result |
|---|---|---|---|
| 1-3 | Swap onto/off 5.25/5.41, 4.09/3.92, 3.04/2.66 (l. 205-206) | Table 8; Table 34 | match |
| 4 | Rubric b range 2.5-6.6 (l. 207) | Table 34 (2.51 … 6.58) | match |
| 5 | Neither +0.12, +0.30, +0.04 (Fig. 1 caption) | Tables 8, 34 | match |
| 6 | Expression loses 77%-94% (l. 252) | Table 38: 1−0.89/3.79 = 76.5%; 1−0.35/5.99 = 94.2% | match |
| 7 | MathConstraint 3.2-5.0; Sonnet 4.4 (l. 211-212) | Appendix O (+3.21 … +5.04; +4.38) | match |
| 8 | 28% vs 0.4%, registered labels (l. 262-263) | Table 23 (0.4% → 28.0%); Table 28 registered +28.2 | match |
| 9 | FR rise 7-53 pp (l. 263) | Table 28 any format (+6.6 … +52.8) | match |
| 10 | AUROC fall 0.17-0.27 (l. 264) | `r8_lenient_results.json` lenient G_nm (−0.1745 … −0.2747) | match |
| 11 | Boxed-only 0.07-0.14 (l. 264-265) | same file, boxed_only (−0.070 … −0.1374) | match |
| 12 | MACE 0.08 and 0.06 (l. 265) | Table 11 | match |
| 13-14 | MACE Sonnet 0.15, Opus 0.16 (l. 266-267) | `r8_sonnet_results.json` −0.1531; `r19a_opus_results.json` −0.1645 | match (print −0.164, Polish 6) |
| 15 | FR +36 both (l. 267) | 0.3563; 0.3626 | match |
| 16 | Constructed pools 0.04/0.08 Sonnet, 0.02/0.06 Opus (l. 267-268) | −0.0373/−0.0796; −0.0151/−0.0567 | match |
| 17 | GPT-4.1 replication 0.04 (l. 268) | `r8_lenient_results.json` −0.0381 | match |
| 18 | MATH-500 28.6/30.6 (l. 302-303) | Table 10 | match |
| 19 | MACE k=1 29.4/26.5; AUROC 0.29/0.23 (l. 303-304) | Table 12; Table 49; Table 16 | match |
| 20 | Blind-10 wrong 2%-4% and 5%-8% (l. 316) | Table 12 (1.9/1.8/3.7); `r19a_acceptance.json` (5.06/5.88/8.21) | match |
| 21 | 19% and 31% (l. 317) | `r20a_sonnet_retest.json` mace 0.1852; `r20a_opus_retest.json` 0.3134 | match |
| 22 | 0 of 318, 2 of 525, 41 and 76 (l. 319-320) | r20a pooled | match |
| 23 | Arithmetic 3%-15% (l. 321) | r20a repl/kpool (2.65% … 14.94%) | match (but Figure 3a shows pooled 4%, 11%) |
| 24 | Open judges 5%-57%, ≤0.4% (l. 322-323) | `r20d_matched_acceptance.json` (0.0462 … 0.5654; match max 0.0043) | match |
| 25 | "2 of 843" (Table 1) | 318 + 525; 0 + 2 | match |
| 26 | Sentence: FR 36 → 18 and 36 → 8 (l. 328-329) | `r20b_sonnet_instruction.json` FR 0.1806; `r20b_opus_instruction.json` 0.0811 | match |
| 27 | Sentence AUROC −0.06/−0.05 (Table 2b) | −0.0649; −0.0525 | match |
| 28 | Thinking swap loss 2.85 → 0.32; 1.98 → 0.12 (l. 336) | Appendix L; Table 13 | match |
| 29 | Factual FR 36 → 15; 44 → 22; 42 → 18 (l. 338-339) | `r19b_sonnet_think_results.json` FR 0.149; Table 47; Table 13 | match |
| 30 | Blind AUROC 0.85 → 0.86; 0.72 → 0.81 (l. 340) | Table 13 | match |
| 31 | Qwen3-8B 96% (l. 337) | Appendix H 96.2% | match (unmarked post hoc, M6) |
| 32 | Table 2a, 16 accuracy cells | `r20c_leaderboard.json`; `r20g` leaderboard_max_rule | match |
| 33 | "13 to 40 points" (abstract) | −13.42, −39.60, −21.48, −14.77 | match |
| 34 | "22 pp pooled [−27, −18]" (l. 354) | −22.32 [−27.01, −17.95] | match |
| 35 | 11%-42%; 68%-78% (l. 357-358) | FR_nonmatch_ref 0.1101-0.4182; share 0.6796-0.7801 | match |
| 36 | "within 3 points" blind (l. 353) | blind_minus_list −0.67 … −2.68 | match |
| 37 | Max rule "within 2 points" (l. 372) | max_minus_list −2.01 for Sonnet 5 | borderline (Polish 6) |
| 38 | Max rule AUROC within 0.03 (l. 371) | Table 2b; `r20g` (Sonnet MACE −0.015, Opus −0.008; open k-pool ≤0.03) | match |
| 39 | Max rule costs 4.8/0.05; 6.7/0.15; 0.07 (l. 373-375) | Table 16 bottom (−6.7; −0.15; −0.07) | match (0.16 by subtraction in Table 2b) |
| 40 | MACE selection +2.0/+6.1; natural mix 9-11 (l. 362-364) | Table 49; Table 2b | match |
| 41 | 11 tasks −64/−45; ≤14 (l. 366-367) | Table 12 (−63.6, −45.5; −13.6) | match |
| 42 | Ledger 109/11/16/17/23 = 176 (l. 199-200) | Appendix B l. 802-805 (18 + 2 + 3 = 23) | internally consistent |
| 43 | Prevalence 0%-2.5%; 30%; 18.5% (l. 069-072) | Table 5; Appendix C | match |
| 44 | 38%-43% unboxed; 88% agreement (l. 182-184) | Table 29 (61.6%, 57.1%; 87.9%, 88.4%) | match |
| 45 | Opus replication FR rise | Table 45 +3.6 against Appendix K and registration +3.7 | rounding inconsistency (Polish 6) |
| 46 | Answer lists miss 2.3%/8.1%; others 31%-44% (l. 164-165) | Appendix D (30.8%-43.5%) | match |
| 47 | Abstract "3 to 5 points" | Table 1 2.7-5.4 | loose rounding (Polish 1) |

`scripts/check_numbers.py` reports only five untraced integers (an example length, task and sample counts). None is a result.

---

## 5. Figure-by-figure and table-by-table critique

### Main text

**Figure 1 (p. 1).**
- **At the bar.** The concrete task, one fixed reply scored three ways (10.0 / 2.9 / 9.3), and the pool-level swap in panel c is the right teaser. The disclosed selection of the example is good practice.
- **Legibility.** Fine at print size.
- **Remaining.**
  - Panel c has no labeled zero line, although "an answer key predicts zero" is the paper's logical pivot.
  - The panel b note mixes registered-label rates (disclosed in the caption) with a figure whose other numbers are exact-scorer any-format.
- **Missing.** Nothing on P3 or on benchmark impact. Acceptable given Table 1.

**Table 1 (p. 3).**
- **At the bar.** Close: one table of predictions, tests, observations, verdicts, and failed registered predictions, which is the paper's credibility asset.
- **Fix:**
  - the P2 verdict (M4);
  - the P3 verdict scope (M2);
  - the "Not predicted" label (M6);
  - "roughly halve" (Polish 5);
  - add a Consequence row (Polish 14).
- **Column widths.** With 3.5 pt separation the columns no longer touch. Good.

**Figure 2 (p. 5).**
- **Strengths.** A clean forest plot. The one-answer block against the several-answers block communicates P2 and P2′ at a glance. The empty cells are now labeled. Minimum text is 7.5 pt printed.
- **Problems.**
  - Opus 5's constructed-pool rows are omitted, including its failed prediction (M4).
  - The "not shown" labels cross the zero axis.
  - The boxed-only ticks overlap the GPT-4.1 triangles.
  - Panel a's MACE rows are k>1 while Table 2b's MACE accuracy is the natural mix (M3). A reader comparing Figure 2a (+2, +6) with Table 2b (+9, +11) will think one is wrong.

**Figure 3 (p. 6).**
- **Strengths.** The redesign works:
  - Panel a is the P3 figure the paper needed: filled against open circles, with retest crosses, factual above arithmetic.
  - Panels b and c separate arithmetic from factual thinking.
  - Minimum text is 7.5 pt printed.
- **Problems.**
  - Crosses coincide with open circles at 0 for all API rows (Polish 12).
  - Value labels in panel b collide with bars.
  - Panel a has no factual rows for open judges (M2).
  - The divider between "Factual" and "Arithmetic" spans only the plot area, not the labels.
  - The "Opus 5 (API), arithmetic 4%" row pools a k-pool where 8.2% of wrong answers also get a blind 10. The caption should say that acceptance is weaker there.

**Table 2 (p. 8).**
- **Strengths.** It carries the paper's most practical content, and the (a) block is the "Mirage moment" of the paper. The bolding rule is stated.
- **Problems.**
  - It holds three messages under a 32-word title.
  - MACE natural-mix accuracy sits under "Several correct answers" (M3).
  - The API judges' k-pool and replication max-rule rows are missing, although Table 45 has them. Opus 5 k-pool max rule is −0.027 [−0.046, −0.009], which excludes zero: small but real.
  - No blind-then-reveal comparator.
  - Panel (a) would read better as a slope chart (M5.4). The Haiku/Llama crossing at 55.0/55.7 is one question apart; say so, or the reader will over-read "level with".

### Appendix (brief)

- **Table 3.** Fix "120-task subsample". The MACE row's "Math" domain is explained in Appendix D; a pointer would help.
- **Table 4 (ledger).** Excellent and rare. The round-19/20 rows are accurate against both registration files (checked P-R19A1-A6, B1-B3, R20A1-A3, B1-B4, C1-C3).
- **Table 12.** Still a ~70-row dump; drop the superseded CLI noise-floor block.
- **Tables 13, 34-39, 47-49.** Fine.
- **Table 16.** The bottom block is illegible (Polish 8).
- **Tables 26-28.** Good models of scorer and labeling tags.
- **Table 42.** Now sources a table (Table 48) that the main text no longer uses. Consider merging 42 into 48.
- **Tables 43-44.**
  - Useful and accurate against `r20a` and `r20d`.
  - Printed at about 6 pt after `adjustbox`; reset at `\footnotesize` with abbreviated headers.
  - Table 43's Opus MACE matching count (102) differs from Appendix K text "0 of 247" pooled (the Table shows 246). One call failed, which the text explains two lines later. Put the explanation in the caption.
- **Table 45.** Accurate against `r20g_frontier_safeguards.json`. Three decimals where the main text uses two (Polish 6).
- **Table 46.** About 5 pt, illegible in print. This is the benchmark table the main text cites, so it must be readable.
- **Figures 4-9.** Legible. Figure 6's "not an independent test" caveat is good.
- **Page 46.** Near-empty (Polish 20).

---

## 6. What is already at the bar (leave alone)

- **Title.** A claim, memorable, accurate.
- **Opening paragraph and Figure 1.** "The text never changed; only the correct answer the judge was shown did." Best-paper quality.
- **The swap design and the matches-neither control.** Byte-identical text, a clean manipulation, an obvious null.
- **The three-readings framing, Equation 1, and the separation logic.** It now explains why P2 needs P2′ and why P3 separates verification failure from agreement, and it says plainly that the model is not fitted.
- **The P3 noise control (R20-A).**
  - A registered same-interface retest on every accepted answer, with regression to the mean working against the finding.
  - 0/318 and 2/525 against 41 and 76 is decisive.
  - This fixed the round-19 central weakness completely.
- **The Opus 5 replication.** It includes a registered prediction that failed (blind-10 wrong answers above 5%) and a registered null (replication AUROC), both reported.
- **The full-credit sentence measured by grading (R20-B).** It answers the first question every practitioner asks, with a nuanced and credible answer: it helps a lot and does not fix grading.
- **The benchmark study design (R20-C).** Answers held fixed across graders, registered predictions, rankings reported without a prediction. The design is right. Fix only its scope (M1).
- **Honesty.**
  - Registered nulls are in the main text (MACE selection, distance ordering, instruction for small judges).
  - "partly by construction" for the max rule.
  - The retroactive verdict-rule disclosure.
  - Opus 5's visible-reasoning check.
  - The corrected Opus generation count in the registration.
- **Limitations section.** Specific and prominent.
- **Page limit.** The main text ends on p. 9, l. 475. Compliant.

---

## 7. What would move the score

### To a solid 7 (the current score, with no open objections): rewrites and re-analyses only, about 2 days, no API spend

1. **M1.** Rescope the abstract and conclusion benchmark sentences. Add the `r20e` open-judge benchmark table to Appendix K with one sentence in Section 7. Add threshold 5/10 variants from stored scores.
2. **M3.** Replace the natural-mix MACE accuracy in Table 2b with k>1 values (compute max-rule k>1).
3. **M4.** Reconcile the P2 verdicts in Table 1 and Section 5; add the two Opus 5 rows to Figure 2.
4. **M6, M7, M8.** Registration marks, "nearly removes", and the "tracks" sentence.
5. **Polish 1-8 and 12.** These are the items a number-checking or print-reading reviewer will trip over.

### To 8: the above, plus one restructuring pass and three small experiments (about 1 week, under USD 50)

1. **M2 re-analysis (hours).** Matched-threshold acceptance for Qwen2.5-7B and phi-4 on MACE from stored scores. Add factual rows to Figure 3a, and bring Qwen3's MACE acceptance into the P3 paragraph with its caveat. If the pattern holds, "P3 holds on factual questions for four judges from three families" is a much stronger sentence than "for two Anthropic models".
2. **Main-text restructuring (M5, 2-3 days).** Target at most 6 numbers per paragraph:
   - Figure 1: swap, with the answer-key line.
   - Table 1: predictions, with a Consequence row.
   - Figure 2: one vs several, with Opus rows.
   - Figure 3: P3 and thinking.
   - New Figure 4: benchmark slope chart (answer list → blind → referenced → max rule per model, plus the two open judges as a faint second panel).
   - Table 2: safeguards only, with reference, sentence, blind-then-reveal and max rule as columns.

   This also frees space for item 3.
3. **A second benchmark grader (new data, about 2.4k calls, under USD 15).** Opus 5 and GPT-4.1 grade the same 596 answers blind and referenced. This removes both the one-judge and the self-grading objections to the paper's headline consequence. Report whether the Haiku/Llama inversion recurs.
4. **A non-Anthropic frontier judge on factual P3 (new data, about 2-3k calls, under USD 30).** GPT-4.1, or a current OpenAI or Google model, on the 40-task MACE subsample with a same-interface retest. This closes the "one provider" limitation for the paper's central claim. It would also finally test GPT-4.1 where Sonnet's effect is largest (round-19 M2).
5. **Optional, cheap: human labels.** 200 unboxed replies, a few hours. It lets Table 1's open-judge P2 range stand without the "not checked by humans" hedge.

### To 9: best-paper territory (weeks; new data)

1. **A second natural multi-answer benchmark outside MACE**, with human-verified answer sets, repeating the benchmark study. For example, AmbigQA/NQ-open items the paper's own audit flags as multi-answer, or a constructive-code task scored by execution. A leaderboard inversion that recurs on a benchmark people use would make the paper's consequence undeniable, not illustrative.
2. **A prospective test of the recommendation.** Register the max rule (and the full-credit sentence plus max rule) before a fresh k-pool seed and held-out MACE questions, then evaluate grading, accuracy and the unique-answer cost. This turns "chosen post hoc from five combinations" into a registered safeguard.
3. **A direct manipulation of verification.** For example, give the blind judge a verifier tool or the full answer list in a separate call, and show that the effect scales with the judge's measured verification where agreement predicts it should not. This would move P3 from "not only verification failure" to a mechanism.
4. **Judges as the unit.** Show that referenced grading reorders *judges* on a judge benchmark such as RewardBench-2 Ties when the gold set has several answers. That is the analogue of the metric-choice demonstration in the model paper, and it would give practitioners a second, independent reason to care.

With the 8-level items, the paper would have:
- one question, one clean manipulation;
- a separating prediction confirmed on factual questions across model families with a same-interface noise control;
- a benchmark consequence replicated across graders;
- a measured partial remedy;
- a main text a reviewer can absorb in ten minutes.
