# Round 19 Area Chair review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

Reviewed from `round19_main.pdf` (44 pages; main text pp. 1-9, statements pp. 9-10, references pp. 10-12, appendix pp. 13-44), with `main.tex`, `appendix.tex`, `tables/*.tex` and `papers/analysis/*.json` used to check numbers. Line numbers are the PDF margin numbers.

---

## 1. Summary of the claims and how easy they were to extract

**Question.** When a question has several correct answers, does a reference-guided LLM judge treat the reference as an answer key? Under an answer key, every correct answer would score the same whichever one is shown.

**Claims, as I extracted them:**

1. **P1, the swap.** Swapping the reference between two correct answers moves the score of byte-identical text.
   - On 120 constructed arithmetic tasks the move is 2.7-5.4 points out of 10 for Qwen2.5-7B, phi-4 and Claude Sonnet 5 (rubric b: 2.5-6.6).
   - The pattern holds on 9 MathConstraint puzzles.
   - It depends on how explicitly the reference states its answer: words keep the effect, an expression or masking removes it.
2. **P2, grading harm.** With several correct answers, correct answers that differ from the reference are graded worse.
   - Grading AUROC against wrong answers falls 0.17-0.27 for four open judges on constructed pools, 0.06-0.08 on MACE, 0.04-0.15 for Sonnet 5, and at most 0.04 for GPT-4.1.
   - With one correct answer the reference helps: +29-31 pp best-of-64 accuracy on MATH-500.
3. **P3, beyond verification failure.** For Sonnet 5, correct answers it scores 10 without a reference drop to 3 or below 9-19% of the time when a different correct answer is shown. Matching answers never do.
4. **Moderator.** A thinking mode removes the effect on arithmetic but only reduces it on factual questions.
5. **Decisions and a safeguard.**
   - Selection losses concentrate where no correct candidate matches the reference.
   - On natural MACE data, selection is not harmed.
   - A post hoc "max rule" keeps grading AUROC within 0.03 of blind, at a cost of up to 6.7 pp on unique-answer MATH-500.
6. **Registration.** 156 registered predictions are all reported: 92 confirmed, 15 falsified.

**Ease of extraction.**
- **Easy:** the question and P1. The title, Figure 1 and the opening example (35 vs 80) get the reader to the core finding in under a minute. That is at the best-paper bar.
- **Moderate:** P2. Three measures (false rejection, grading AUROC, best-of-64 accuracy), four labelings, and two scorers make it hard to say which number is the headline.
- **Hard:** P3, the thinking moderator and the safeguard. The P3 paragraph (ll. 260-269, 306-310) carries about 17 numbers, two interfaces, three pools, and a noise floor measured on a different pool and a different interface than the headline estimate. I had to open Tables 12, 41 and 44 to learn what was compared with what.
- **Overall:** the paper answers one clear question, but the main text reads like a results ledger. A skimming reviewer will take in P1 and Table 1 and lose the thread after Section 5.

---

## 2. Score and confidence

**Score: 6 / 10** (marginally above the acceptance threshold). **Confidence: 4 / 5.**

**Single biggest reason.** The central conceptual claim, P3 ("the effect is not only a failure to verify"), rests on one judge (Sonnet 5), and its only noise control breaks the paper's own rule.
- The control compares a CLI blind re-call with API referenced scores. Setup (ll. 178-180) says the two interfaces "agree exactly on only 67% of shared calls, so we compare its results only within one."
- The control was run on the replication pool, while the headline 19% is on MACE.
- Two judges that could strengthen or weaken the story were never tested where it matters: GPT-4.1 was not swap-tested and not run on factual questions, and no thinking-mode frontier judge was run on MACE through the API.

Taken together, this leaves open whether the finding holds for the judges practitioners now use. The rest is well executed, unusually honest, and mostly fixable by rewriting. The P3 and GPT-4.1 gaps need small, cheap runs.

---

## 3. Ranked issues

### MUST FIX

#### M1. P3's acceptance test: wrong interface for the noise floor, wrong pool, one judge
**New data: yes, small (~450 API calls). Also a re-analysis of stored data.**

**Location.** Section 6, ll. 264-269 and 306-308; Verdict ll. 359-361; Table 1 P3 row; abstract l. 024-025.

**Problem.**
1. **Wrong interface.** The noise floor ("a second blind call scored none of 111 such answers 3 or below, against 12 once the reference was shown") compares a **CLI** blind re-call with **API** referenced scores (Table 12, "second blind call (CLI); API with the reference"). Appendix J states that API scores run 0.38 higher and agree exactly on only 67% of calls. The paper argues the offset "if anything adds low scores". That argument concerns the mean; it says nothing about whether *low tails* are reproducible across interfaces.
2. **Wrong pool.** The floor covers the replication pool (111 of 150 answers). The Verdict (l. 359-360) says "P3 holds for Sonnet 5 on **factual** questions: ... a post hoc acceptance test with a noise floor". The factual estimate (19% of 81 MACE answers) has no noise floor at all.
3. **One judge.** P3 is tested only on Sonnet 5. Stored data allow at least a partial acceptance test for other judges, and the paper does not run it (see Fix, part 2).

**Fix.**
1. **Run the proper control on the API (new data).** Re-call Sonnet 5 blind through the **API**, twice, on every correct answer it scored 10 blind: 81 non-matching and 38 matching MACE answers, 150 and 60 on replication, 87 and 39 on the k-pool (~455 answers, ~910 calls). Report the share of ≤3 scores under blind re-call against the referenced call, within one interface. Replace ll. 268-269 and 306-308 with:
   > "The drop is not score noise: a second blind API call scored X of 81 such factual answers and Y of 150 arithmetic answers 3 or below, against 15 and 13 with the reference."
2. **Re-analysis of stored data, no new calls.** For the open judges, find the blind expected-score threshold at which wrong answers pass at the same 2-4% rate as Sonnet 5's blind 10 (Table 12 gives Sonnet's rates). Report the false-rejection rate above that threshold for non-matching against matching answers. Do the same for Qwen3-8B and Qwen3-14B with thinking on, using the 81-task MACE subsample, which contains invalid answers. If P3 holds for three to five judges rather than one, Table 1's "Holds for Sonnet 5" becomes "Holds for all judges tested", which is a much stronger paper.
3. Until then, rewrite the Verdict: "a post hoc acceptance test, with a noise floor measured on arithmetic through a different interface".

#### M2. The GPT-4.1 exception is asserted but never examined where it would matter
**New data: yes, small (~2-3k API calls, well under $50).**

**Location.** Abstract l. 025 ("It is small for GPT-4.1 and near zero on arithmetic..."); Intro l. 097; Table 1 P2 row and verdict; Section 4 l. 215 ("We did not run the swap test on GPT-4.1"); Section 5 ll. 244-245; Limitations l. 451-452.

**Problem.**
1. **Misattributed "It".** In the abstract, "It" refers to "the effect". GPT-4.1 was never swap-tested; only its grading AUROC was measured.
2. **Sonnet 5 looks the same on this pool.** On the replication pool GPT-4.1's grading AUROC falls by 0.04, but so does Sonnet 5's (Table 41: −0.04 [−0.07, −0.01]; Figure 2b). The contrast that makes GPT-4.1 look robust comes from the k-pool (−0.01 against −0.08) and from **MACE, where GPT-4.1 was not run**. MACE is exactly where Sonnet 5's effect is largest (−0.15, +36 pp false rejections).
3. **The resulting inference is unsupported.** The reader infers that stronger frontier judges are less affected, and the data do not support that. Ties do not prevent a swap test, because the swap measures mean score change of fixed text and needs no ranking.

**Fix.**
1. **New data.** Run GPT-4.1 on:
   - the swap: the 60-task one-per-type replication design, or the 120-task API design;
   - the 40-task MACE subsamples with wrong answers that Sonnet 5 used (Appendix J design).
   Report swap change, false rejections and grading AUROC. Check whether the API allows `top_logprobs` up to 20 (Appendix A says "at most five alternatives per token"). If it does, rescore GPT-4.1 with the 20-token expected score, which may also resolve its ties.
2. **Rewrite now.**
   - Abstract: delete "It is small for GPT-4.1 and".
   - Table 1 P2 verdict: replace "Holds; small for GPT-4.1" with "Holds; GPT-4.1 and Sonnet 5 both small on arithmetic (≤0.04); GPT-4.1 untested on factual questions".

#### M3. Abstract: imprecise, overlong, and overclaims the safeguard and the breadth
**New data: no.**

**Location.** Abstract ll. 013-031.

**Problems.**
1. "test two predictions that rule out the answer key and one that separates the other two" cannot be parsed on first read. It forces the reader to hold three parenthetical readings in memory.
2. "It is small for GPT-4.1" (see M2).
3. "scoring with and without the reference and keeping the higher score removed the grading harm" overclaims:
   - Section 7 (ll. 402-403) says the grading result "is partly by construction ... so the informative results are the costs".
   - The costs on unique answers (−6.7 pp, −0.15 AUROC for Qwen2.5-7B with a full solution; Table 2) are not mentioned.
4. "program-enumerated tasks and public factual, math, puzzle, and code benchmarks" overstates breadth:
   - The puzzle study has 9 items.
   - The code study found **no** inflation (Appendix O: the canonical program lowered it, −0.34 and −0.57 SD).
   - Listing code as a test bed implies support that does not exist.
5. "156 registered predictions, all reported" without the verdict counts invites suspicion. Give the counts.
6. The abstract has no concrete implication beyond "weak evidence of error".

**Fix.** Replacement (≈190 words; one number per claim):
> LLM judges grade benchmarks and score training rollouts, often with a reference answer in the prompt, on the premise that the reference acts as an answer key: a correct response should score the same whichever correct answer is shown. Many questions have several correct answers, and on them the premise fails. Holding the graded text byte-identical, we swap the reference between two correct answers. On 120 constructed arithmetic tasks the swap moves the score by 2.7 to 5.4 points out of 10 for Qwen2.5-7B, phi-4, and Claude Sonnet 5, and showing the reference raises the share of non-matching correct answers that Qwen2.5-7B scores 3 or below from 0.4% to 28%. This is not only a failure to verify: on factual MACE questions Sonnet 5 scores 19% of such answers 3 or below although it gave them a 10 without the reference. A thinking mode removes the effect on arithmetic but only reduces it on factual questions, and a reference still helps when the answer is unique (+29 pp best-of-64 accuracy on MATH-500). On questions with several correct answers, a low reference-guided score is weak evidence of error. We registered 156 predictions and report all of them, including 15 that were falsified.

(Add a GPT-4.1 clause only after M2's runs.)

#### M4. Conclusion contradicts Section 5 and Figure 3
**New data: no.**

**Location.** Conclusion ll. 467-475.

**Problems.**
1. **AUROC ranges disagree.**
   - l. 472-473: "for the four open judges, grading AUROC for these answers falls from **0.74-0.93** blind to **0.63-0.73**".
   - Section 5 l. 239-240: "from **0.84-0.93** blind to **0.63-0.72** with the reference".
   - The conclusion's range pulls in MACE (Qwen2.5-7B blind 0.74; phi-4 referenced 0.73; Table 11), but MACE has two open judges, not four. It also hides that the MACE falls are 0.06-0.08, a third of the constructed-pool falls.
   - Neither level range can be traced to a printed table. Table 11 gives registered-label levels (replication Qwen2.5-7B 0.87 → 0.60; phi-4 0.90 → 0.65), and 0.60 lies outside "0.63-0.72". The any-format levels behind Section 5's range appear nowhere.
2. **"Judges that score without a thinking mode favor the one they are shown" undersells the paper's own result.** With thinking on, factual false rejections still rise by +21.6, +17.8 and +12.5 pp (Figure 3b, Table 44).
3. **No actionable recommendation**, although the paper has one.

**Fix.**
- Add the any-format blind and referenced levels as two columns in Table 27, or quote changes only.
- Replace the conclusion with:
  > A reference answer is a good check when a question has one correct answer. When it has several, score-only judges favor the one they are shown: swapping it moves the score of unchanged text by 2.7 to 5.4 points, and grading AUROC for correct answers that differ from it falls by 0.17 to 0.27 on constructed pools and by 0.06 to 0.15 on MACE. For Sonnet 5 this happens even for answers it accepts without a reference. A thinking mode removes the effect on arithmetic, but on factual questions false rejections still rise by 12 to 22 pp. Evaluations of questions with several correct answers should report blind and referenced scores or supply the full answer set; when only one reference exists, keeping the higher of the two scores protected grading on our multi-answer pools at a cost of up to 7 pp when the answer is unique.

#### M5. The instruction confound is misreported and under-measured
**New data: rewrite now; small experiment for the 8.**

**Location.** Section 6 "Not only the prompt", ll. 312-317; Limitations l. 452-453; Section 1 l. 084.

**Problems.**
1. **"Our only test of the instruction itself adds a sentence..." (l. 313-314) is false.** The paper tested **two** instructions:
   - Appendix A (ll. 751-757) prints both, "any-valid-answer" and "do-not-compare".
   - Table 40 reports both: Sonnet 5 +3.00 → +2.08 and +2.60; GPT-4.1 +0.99 → +0.46 and +0.59.
2. **Undefined judges.** "failed its registered test for Qwen2.5-1.5B, 3B, and 7B" introduces three judges the main text never defines. It also omits the confirmed shrink for Qwen2.5-14B (+3.34 → +1.21; Appendix F; ledger "split").
3. **This is the first question every practitioner and reviewer will ask** ("just tell the judge several answers can be correct"), yet it is answered only in margin units, only on the k-pool and synthetic grid, and never with false rejections or grading AUROC.

**Fix (rewrite).**
> "We tested two added instructions (Appendix A): one says the question may have several correct answers that each deserve full credit, the other says not to compare the candidate's answer with the reference. Neither removes the margin for Sonnet 5 on the k-pool (+3.00 without; +2.08 and +2.60 with) or for GPT-4.1 (+0.99; +0.46 and +0.59). On a synthetic pool the first closes phi-4's margin and shrinks Qwen2.5-14B's, but not the margins of smaller Qwen2.5 judges."

**Small experiment (for an 8).** Re-score with the any-valid-answer sentence:
- stored replication and MACE candidates for Qwen2.5-7B and phi-4 (forward passes only);
- the 40-task MACE API subsample for Sonnet 5.

Report false rejections and grading AUROC next to the plain referenced prompt, as a new row in Table 2 or a panel in Figure 2.

#### M6. The P2 magnitude depends on post hoc, human-unvalidated labels
**New data: yes, tiny (~200 human labels, a few hours).**

**Location.** Section 3 "Reading answers" ll. 182-187; Section 5 ll. 239-241; Table 1 P2 row; Limitations l. 443-445.

**Problem.**
- The main-text labels are post hoc for the open judges. With them, the grading AUROC fall is 0.17-0.27. With boxed replies only it is 0.07-0.14 (Table 27), less than half.
- Agreement with the model reading (88%) is agreement between two automated rules.
- Table 1, the page most reviewers read, shows only the larger range.

**Fix.**
1. Human-label a stratified random sample of 200 unboxed replies (100 per constructed pool, half judged correct by the any-format rule). Report accuracy of the any-format rule, the model reading, and the registered checker against the human label.
2. Put both ranges in Table 1: "falls 0.17-0.27 (any format; 0.07-0.14 boxed replies only)".

#### M7. "Hidden inside a worked solution it loses all of it" misdescribes the experiment
**New data: no.**

**Location.** Section 4, ll. 224-225.

**Problem.** The experiment in Table 38 **masks** the answer inside a worked solution (+2.97 → +0.05 for Qwen2.5-7B). A worked solution that *states* the answer keeps most of the pull: Appendix F "Worked references" gives +5.17 → +3.73 (Qwen2.5-7B) and +4.20 → +3.67 (phi-4). MATH-500's full-solution reference also helps as much as the bare answer (Table 10). The current wording tells readers that references given as solutions are safe, which the paper's own data contradict.

**Fix.**
> "A worked solution that ends in the answer keeps most of the margin (+5.17 to +3.73 for Qwen2.5-7B; Appendix F); masking the answer inside that solution removes it (+2.97 to +0.05; 21 single-number k-pool tasks)."

#### M8. Figure 2's title overclaims, and its registration sentence is garbled
**New data: no.**

**Location.** Figure 2 caption ll. 295-303; Intro l. 097.

**Problems.**
1. **The title overclaims.** "it degrades grading for every core judge on the pools it was run on". Setup (l. 174-175) lists GPT-4.1 among the core judges, and its k-pool change is −0.01 [−0.04, +0.00] (Table 27, any format), so the interval includes zero. Section 5 itself says it "does not change reliably on the k-pool".
2. **The registration sentence is garbled.** "Sonnet 5's values and the open judges' MACE several-answer grading for Qwen2.5-7B were pre-specified".
3. **Selection claim is loose.** "selection for some judges on constructed pools": only Qwen2.5-7B's intervals exclude zero (replication −9.3 [−17.5, −1.0]; k-pool −30.3 [−48.5, −12.1]). phi-4's interval reaches zero.

**Fix.**
- Title:
  > "With one correct answer the reference helps; with several, it lowers grading AUROC for every judge except GPT-4.1 on the k-pool, and clearly lowers selection accuracy only for Qwen2.5-7B."
- Registration sentence:
  > "MATH-500 accuracy is a pre-specified re-analysis; Sonnet 5's values and Qwen2.5-7B's MACE grading were pre-specified; all other values are post hoc."
- Intro l. 097: "P2 for every score-only judge we tested except GPT-4.1 on the k-pool".

#### M9. Registration marks are inconsistent in a paper whose credibility rests on them
**New data: no.**

**Location.** Section 7 l. 367; Section 5 l. 250; Table 2 caption l. 384-385; Section 5 l. 237 with the Figure 1 caption.

**Problems.**
1. **Section 7 (l. 367).** "+2.0 pp for Qwen2.5-7B† and +6.1 pp for phi-4". Both values come from the pre-specified MACE end-to-end experiment (Table 45, PRE: +2.0 [−5.1, +9.1] and +6.1 [−1.0, +13.1]). The dagger appears because the main text quotes the exact-scorer re-estimate (Table 12: +2.0 [−5.1, +10.1]), which has the same point estimate. A reader sees one judge's registered null marked post hoc and the other unmarked.
2. **Section 5 (l. 250).** "29.4 and 26.5 pp†": phi-4's 26.5 is from PRE Table 45.
3. **Table 2 caption (l. 384-385).** "MATH-500 reference accuracy is a pre-specified re-analysis; the rest is post hoc". phi-4's MACE referenced accuracy (+11.3) is in PRE Table 45.
4. **Section 5 (l. 237) and Figure 1.** "28% ... 0.4%" is quoted under the convention "Unless stated otherwise, constructed pools use any-format labels" (l. 196-197). The Figure 1 caption says these rates "use the registered labels", and Table 28 confirms registered +28.2 against any-format +27.0.

**Fix.**
- Quote the registered estimate unmarked wherever the registered and re-scored point estimates coincide, and cite Table 45.
- Change Table 2's caption to list what is pre-specified.
- At l. 237 add "(registered labels; 27 pp with any-format labels)".

#### M10. "Why it matters" is weaker than the introduction implies
**New data: re-analysis now; small experiment for the 8.**

**Location.** Intro ll. 063-069; Section 7; Ethics statement.

**Problem.** The introduction motivates with benchmarks, best-of-n selection and RL rewards, but the paper's own decision-level evidence is mixed:
- MACE selection: +2.0 and +6.1 pp, registered loss not confirmed.
- DPO: no copying, protected arm failed its check.
- MBPP: no inflation.
- A thinking mode removes the effect on arithmetic.

The robust harm is **per-response grading**, which is exactly what benchmark scoring and pointwise reward do. The paper never turns that into a benchmark-level number a reader can feel.

**Fix.**
1. **Re-analysis, no new data.** From stored scores, report Llama-3.1-8B's measured accuracy on MACE k>1 and on the replication pool under three graders:
   - (i) answer list;
   - (ii) blind judge thresholded at 5;
   - (iii) referenced judge thresholded at 5.

   Example sentence: "reference-guided grading reports X% where the true rate is Y%; the shortfall falls entirely on correct answers that differ from the reference." Put it in Section 7's first paragraph.
2. **Small experiment (for an 8).** Sample 1-4 answers from 3-4 generators with different answer distributions (e.g., Llama-3.1-8B, Qwen2.5-7B, gemma-2-9b, Sonnet 5) on the 133 MACE questions. Grade each with a referenced judge and with the answer list, and show whether model rankings change or whether the under-count scales with how often a model's answers differ from the reference. One small table would give the paper its "Mirage" moment: a leaderboard artifact produced by the evaluation, not the model.
3. Re-scope the ethics sentence and intro to "grading and pointwise rewards".

#### M11. Cognitive load: the main text is a number ledger
**New data: no.**

**Location.** Throughout, worst in Section 3 (ll. 157-204), Section 5 (ll. 236-245) and Section 6 (ll. 260-269, 306-323, 352-357).

**Problem.**
- Section 3 introduces about 20 terms in one page: replication pool, k-pool, pass-rate band, core judges, explanation first, thinking mode, CLI/API, any-format labels, registered labels, model-read labeling, boxed only, swap change, false-rejection rate, grading AUROC, best-of-64 accuracy, margin, exact expected score, inflation, SD, and three registration marks.
- Section 6's first paragraph holds about 17 numbers plus three interface caveats.
- The benchmark paper (Schaeffer et al.) keeps to roughly three numbers per paragraph and lets figures carry the rest.
- Readers skim; they will not reconstruct which pool, labeling and interface each number belongs to.

**Fix (concrete cuts, which also free the space M1, M2 and M10 need):**
1. **Setup.**
   - Move the primary-endpoint sentence (ll. 198-200) and the ledger counts (ll. 202-204) to one sentence: "Appendix B lists all 156 registered predictions (92 confirmed, 15 falsified)."
   - Define "inflation" there or not at all; "+1.19 SD" is undefined in the main text.
   - Replace the Candidates and Judges prose with a 4-row pool × judge grid (a compact version of Table 3).
2. **Section 4.**
   - Cut "Beyond arithmetic" to one sentence.
   - Turn "What the judge responds to" into a 3-bar inset in Figure 1c or move it to Appendix I with a one-sentence pointer.
3. **Section 5.**
   - Drop the level ranges (M4).
   - Put the boxed-only range in parentheses once.
4. **Section 6.**
   - Move the CLI/API caveats (l. 306-308, Figure 3 caption l. 347-348) to one footnote.
   - Move the Qwen2.5-7B AUROC-tercile sentence (l. 308-310) to Appendix K.
5. **Section 7.** Keep one number per claim; leave the per-judge "without a matching candidate" intervals (ll. 375-377) to Table 12.

### POLISH

- **P1. Inconsistent rounding for phi-4 (ll. 238, 245).** "the rise ranges from 7 to 53 pp" uses phi-4's replication +6.6 as "7". Seven lines later, "its false rejections on the replication pool rise by 6 pp, as phi-4's do" rounds the same +6.6 to "6". Write "rise by 6.4 pp, about as much as phi-4's 6.6".
- **P2. Wrong subsample description (Figure 3 caption l. 345; Table 3 row "on a 120-task subsample").** Appendix H says the subsample is all 120 tasks with up to three samples per class (879 samples), not a subsample of tasks. Write "all 120 tasks, up to three candidates per type".
- **P3. Unexplained task counts (Section 7 l. 369 vs Table 2 caption l. 382).** Section 7 says "the 99 multi-answer ones"; Table 2 grades "the questions with several (91 tasks)". Add "(91 of the 99 have both a non-matching correct answer and a wrong answer)".
- **P4. The model does not show why P2 rules out an answer key (Section 2, ll. 141-149).** An answer key with β<1 could also lower AUROC. Add: "Under an answer key, κ>0 raises the AUROC of non-matching correct answers against wrong ones, as it does with one correct answer (+0.23 to +0.29); P2 predicts it falls."
- **P5. Table 1, P2′ row.** "Tests: Nothing: every reading allows it" reads oddly. Write "Positive control (every reading allows it)".
- **P6. Table 1 caption.** "Registered predictions that failed near these rows" is vague. Add a short "Failed registered predictions" line per row, e.g.:
  - P1: distance ordering;
  - P2: MACE selection loss, instruction for small Qwen2.5;
  - Moderator: none.
  This is the paper's strongest credibility asset; show it on page 3.
- **P7. Selection rationale contradicts itself (Figure 2 caption vs Section 7 l. 407-409).** Figure 2 omits Sonnet 5 selection because its subsamples "always include a correct answer that matches the reference". Section 7 then uses exactly that selection to evaluate the max rule. Separately, GPT-4.1 is excluded from selection for ties while Sonnet 5's integer tool-call scores (which also tie; Table 40 caption) are used. Either drop the Sonnet selection sentence or explain why it is informative for the max rule.
- **P8. Unhedged novelty claim (Intro l. 072).** "has not been tested directly for LLM judges" is unhedged, while l. 106-107 says "no study of LLM judges that we know of does". Use the hedged form both times.
- **P9. Ambiguous P2 name (l. 090, section title l. 233).** "the others are graded worse" is ambiguous. Write "correct answers that differ from the reference are graded worse". The section title can stay short: "Prediction 2: other correct answers are graded worse".
- **P10. Figure 1c label and caption.** The y-axis label "change in score" should read "score change (points, 0-10)". Add a dashed zero line labelled "answer key predicts 0" so the figure states the core logic, not just the result.
- **P11. Table 16's bottom sub-table is illegible (≈5 pt, p. 25, ll. 1340-1346).** Table 2 cites it for its intervals. Typeset it at the size of the other tables, or put the intervals into Table 2 in `\scriptsize` below each value.
- **P12. The same contrast appears under up to five scorer × labeling combinations.** Qwen2.5-7B k-pool k>1 accuracy change:
  - −35.9 (Tables 9, 26), −30.8 (Tables 15, 22), −30.3 (Table 2), −24.2 (Table 29);
  - max rule minus reference: +27.3 (Table 16 middle) against +33.3 (Table 2).

  Each is explained in a caption, but a reviewer checking numbers will think they found errors. Add a 5-line key at the start of Appendix G ("original vs exact scorer × registered vs any-format; the main text uses exact + any-format"), and tag every appendix table caption with a short code such as [exact, any-format].
- **P13. Internal process vocabulary leaks into the appendix.** Examples: "round-4 registration" and "13 September 2026" (Appendix B l. 796-798); "gainers", "placebo", "lures", "wedge", "anchoring margin", "rotation", "P-R2B1" IDs; "a git status listing recent commit messages" (Appendix J l. 1930-1931). Rename to main-text terms, replace round numbers with "a later registration", and keep the Appendix J disclosure to one sentence.
- **P14. Undefined domain (Table 3, MACE row).** "300 questions ... (River, Language, and Math domains)" names a Math domain the main text never mentions (it is a label-noise control, Appendix D). Say so in Section 3 or drop it from Table 3.
- **P15. Figure 2a has five empty rows** (GPT-4.1 and Sonnet 5 on replication and k-pool; Sonnet 5 on MACE). Print "not run (ties)" or "not shown (subsample design)" in the empty cells so readers do not suspect missing data.
- **P16. Figure 3 lacks comparators.**
  - Panel a: add the score-only swap losses for Qwen2.5-7B and phi-4 (−5.41, −3.92) as a faint reference, so "near zero" has a visible comparator.
  - Panel b: add Qwen2.5-7B score-only (+63.8, Table 44).
  - Panel a row labels "Qwen3-8B, thinking off" use the "explanation first" marker; relabel "thinking off (explains first)".
- **P17. Table 2 is missing its natural comparator.** Add the registered blind-then-reveal column (Table 16 has it). The contrast "registered protocol fails on grading; post hoc max rule does not" is the natural comparison, and it pre-empts the complaint that the max rule was chosen from five rules on the same data. Add "partly by construction" to the title.
- **P18. Power (Figure 3b, Table 1 "no detectable reduction for Sonnet 5").** With 40 questions the paired interval is [−2.45, +0.63]. Say "not distinguishable from zero with 40 questions" rather than implying persistence.
- **P19. Missing forward link (Intro l. 091-092).** Add "for the four open judges" after "Keeping the higher of the blind and referenced scores kept grading at blind level"; Sonnet 5's grading under the max rule is not reported.
- **P20. AI-use statement.** Fine for ICLR. "We checked every claim against those outputs" should become "we checked every quoted number against those outputs", which is verifiable.

---

## 4. Figure-by-figure and table-by-table critique

**Figure 1 (p. 1).**
- **Strengths.** The right figure in the right place: page 1, a concrete two-answer task, the same text scored three ways, and the pool-level effect. Panel b's 10.0 / 2.9 / 9.3 is memorable. The caption discloses selection of the example (good).
- **Panel a.** The abridged candidate is fine.
- **Panel b.** The note mixes registered-label rates into a figure whose other numbers use any-format labels. Either relabel the note or switch it to any-format (27 pp).
- **Panel c.** Legible. The grey "matches neither" bars carry no value labels (the caption gives them, fine). Add the "answer key predicts 0" line (P10); it would make Figure 1 carry the conceptual argument as well as the result.
- **Missing.** The figure does not show P2 or P3. Acceptable; Table 1 carries that.

**Table 1 (p. 3).** A strong device and close to the bar. One page of predictions, tests, observations and verdicts.
- **P1 row.** Verdict "Holds for score-only judges and open judges that explain first" is correct.
- **P2 row.** Add the boxed-only range (M6) and fix the GPT-4.1 verdict (M2).
- **P2′ row.** Relabel (P5).
- **P3 row.** Accurate as written, but it inherits M1's noise-floor problem.
- **"Not predicted" row.** Fine.
- **Caption.** Add failed registered predictions per row (P6).
- **Layout.** The 2 pt column separation makes columns touch at 100% zoom; use 4 pt.

**Figure 2 (p. 6).**
- **Strengths.** A good forest plot: a one-answer block against a several-answers block, shared x-axis per panel, legible at print size. The design communicates P2 and P2′ in one glance.
- **Problems.**
  - (i) The title overclaims (M8).
  - (ii) Five empty rows in panel a (P15).
  - (iii) Grey "boxed only" ticks sit without intervals and visually read as a second estimate of equal status; make them lighter or move them to Figure 7, which already shows all labelings.
  - (iv) The registration sentence is garbled (M8).
  - (v) The one-answer rows show only open judges; if M2's runs happen, add GPT-4.1 and Sonnet 5 on MACE k=1.

**Figure 3 (p. 7).**
- **Problems.**
  - Panel a mixes two designs (Sonnet 5 CLI, 60 tasks; open judges, all 120 tasks) that the caption says not to compare, yet they share an axis. Consider two small facets.
  - "120-task subsample" is wrong (P2).
  - Panel b's row labels "(explains first / thinks)" and "(score only / thinks)" are hard to parse; use a two-row legend: dark = "thinking off (Qwen3: explains first; Sonnet 5: score only)", light = "thinking on".
  - The title "on factual questions the effect persists" is fair for Qwen3 (+22/+18 pp) but rests on n = 40 for Sonnet 5 (P18).
  - Tick labels "−4 −3 −2 −1 0" are crowded.

**Table 2 (p. 8).** Clear and well captioned; the bolding rule is stated.
- **Problems.**
  - (i) No blind-then-reveal column (P17).
  - (ii) No Sonnet 5 row, although Table 41 has max-rule accuracy.
  - (iii) Intervals are relegated to an illegible sub-table (P11).
  - (iv) The caption's registration statement is wrong for the MACE rows (M9).
  - (v) The 33-task k-pool accuracy cells move in 3.0 pp steps (disclosed; fine).
- **Checked.** Table 2's values match Table 16's bottom block (exact scorer), not its top block (original scorer: k-pool reference AUROC −0.22/−0.13/−0.18/−0.25 against Table 2's −0.23/−0.17/−0.19/−0.25). The difference is explained in the Table 16 caption but is easy to misread (P12).

**Appendix figures and tables.**
- **Table 3 (pools).** Useful. Fix "120-task subsample" and the MACE Math mention (P2, P14).
- **Table 4 (ledger).** Excellent and rare. Keep it. Replace internal IDs in Appendix B prose (P13).
- **Table 5 (prevalence).** Fine. A 100-item human check on NQ-open would let the intro's "30%" stand without the "not checked by humans" hedge (optional, tiny).
- **Tables 6-7 (MACE).** Fine.
- **Tables 8-11.** Fine. Table 11 should gain any-format level columns (M4).
- **Table 12.** A numbers dump with ~70 rows. Acceptable as a reference, but split it by section so a reader looking for a Section 6 number does not scroll through the k-pool pick composition.
- **Table 13.** Fine.
- **Figure 4 (blind-then-reveal).** Legible. Arrows help.
- **Tables 15-16.** Table 16's embedded bottom block is illegible (P11). Table 15 uses registered labels and the original scorer while Table 2 uses any-format labels and the exact scorer; say so in both captions (P12).
- **Tables 17-21.** Fine. The Table 21 screen is a nice negative result ("certifies nothing").
- **Figure 5.** Legible. Panel b uses the original scorer and registered labels (28% / 6% / 26%); note that Sonnet 5's 26% is the earlier correct-answers-only file.
- **Tables 22-24.** Fine.
- **Figure 6.** Fine. The caption's "the step follows from the swap result and is not an independent test" is good.
- **Figure 7.** A good figure. It is the honest version of Figure 2 and could replace Figure 2b if space frees up.
- **Tables 26-30.** Fine. Their captions tag labeling and scorer, which is the model for P12.
- **Tables 31-37.** Fine.
- **Tables 38-39.** Fine. Table 38's column header "Worked: visible → masked" is exactly what the main text misdescribes (M7).
- **Tables 40-41.** Fine. Table 41 is where the Sonnet 5 P2 numbers live; keep it.
- **Tables 42-44.** Table 42 duplicates Table 44's sources; merge them.
- **Table 45.** Fine (the source for M9).
- **Figure 8 (Ties).** Fine.
- **Table 47, Appendix N, Table 48, Figure 9 and Table 49.** Fine.
- **Tables 50-51.** Fine. Table 51 is a lone table on an otherwise empty page 44; float it up.

---

## 5. What is already at the bar (leave alone)

- **Title.** Clear, a claim, memorable. Keep it.
- **Opening paragraph and Figure 1.** The 35/80 example, "The text never changed; only the correct answer the judge was shown did," and the honest "This example swaps more than most" are best-paper quality.
- **The swap design.** Byte-identical text with the reference moved between two correct answers is clean and hard to argue with, and the "matches neither" placebo is the right control.
- **The three-readings framing and Table 1.** The paper states in advance which prediction separates which readings, and marks where it could not separate them ("we separate the last of these only partly"). Keep the structure.
- **Honesty.**
  - Registered nulls reported in the main text (MACE selection, instruction for small judges, distance ordering).
  - "partly by construction" for the max rule.
  - The disclosed selection of the Figure 1 example.
  - The excluded CLI run.
  - The retroactive verdict-rule disclosure.

  This is well above field norms; do not dilute it while cutting.
- **Masking results (numeral / words / expression).** A crisp, interpretable mechanism probe (fix only M7's wording).
- **Positive control on unique answers (MATH-500, MACE k=1).** It pre-empts "references are just bad", and the one-vs-several contrast in Figure 2 is the right visual argument.
- **Limitations section.** Prominent, specific and correctly scoped. Keep the bullets; add the P3 interface caveat if M1 is not run.
- **Related work.** Adequately positioned, and the distinction from wrong-reference studies and solution-fixation work is clear.
- **Page limit.** The main text ends on p. 9 (Conclusion l. 475), with statements after. Compliant.

---

## 6. What would move the score

### To 7 (rewrite plus two cheap runs)

1. **M1, part 1.** Rerun the Sonnet 5 noise floor through the **API** on all blind-10 correct answers, MACE included (~455 answers × 2 calls). Rewrite the P3 paragraph and Verdict to compare within one interface.
2. **M1, part 2 (re-analysis).** A matched-threshold acceptance test for Qwen2.5-7B, phi-4, Qwen2.5-14B and gemma-2-9b, plus Qwen3 thinking-on on the MACE subsample, reported as one small table or a Table 1 cell.
3. **M2.** Run GPT-4.1 on the swap (60 or 120 tasks) and on the 40-task MACE subsamples. Try 20-token logprobs.
4. **Rewrites.** M3 (abstract), M4 (conclusion), M5 (instruction paragraph), M7 (worked solution), M8 (Figure 2 title and marks), M9 (marks).
5. **Density cuts.** M11 items 1-5, which pay for the added results.
6. **Polish.** P1-P4, P11 and P12. These are the ones a number-checking reviewer will trip over.

### To 8 (the above plus three small experiments and one restructuring)

1. **Instruction-aware prompting, measured properly (M5).** Re-score replication and MACE candidates with the any-valid-answer sentence:
   - Qwen2.5-7B and phi-4 (forward passes on stored candidates);
   - Sonnet 5 (40-task MACE subsample, ~1.3k calls).

   Report false rejections and grading AUROC in Table 2. If the effect survives the instruction for Sonnet 5 on factual questions, "agreement" becomes the paper's strongest claim. If it does not, the paper gains a practical fix. Either outcome raises the score.
2. **A modern reasoning judge on factual questions.** Sonnet 5 with extended thinking through the **API** (or one other thinking frontier judge) on the same 40-task MACE subsample, with test-retest blind calls. This answers the question the thinking results raise and a reviewer will press: does the effect survive the judges people deploy now? It turns Figure 3b's n = 40 CLI comparison into a within-interface one.
3. **A benchmark-level consequence (M10).**
   - Minimum: from stored data, measured against true accuracy of Llama-3.1-8B answers on MACE k>1 under referenced, blind and answer-list grading.
   - Better: 3-4 generators on 133 MACE questions, graded by a referenced judge and by the answer list, showing whether the under-count differs by model and whether rankings change.

   This is the "why it matters" figure the paper lacks, and the analogue of the benchmark paper's metric-choice demonstration.
4. **Prospective check of the max rule (optional but cheap).** Register it, then evaluate on a fresh k-pool generated with a new seed (75 tasks) and on held-out MACE questions from the same two domains outside the current band. Blind and referenced scores are what the pipeline already computes. This removes the "chosen post hoc from five combinations on the same data" limitation.
5. **Restructure the main text around three figures and two tables:**
   - Figure 1: swap, with the answer-key line.
   - Table 1: predictions, with failed registered predictions.
   - Figure 2: one vs several, grading and selection.
   - Figure 3: P3 acceptance test across judges, plus thinking.
   - Table 2: safeguards, with plain referenced, instruction, blind-then-reveal and max rule as columns.

   Each section gets at most three quoted numbers per paragraph; everything else goes to the appendix with a pointer.

With these, the paper would make one question, one clean manipulation, a separating prediction tested on several judges including a reasoning frontier judge, a concrete consequence for benchmark scores, and a tested remedy. That is the shape of an 8.
