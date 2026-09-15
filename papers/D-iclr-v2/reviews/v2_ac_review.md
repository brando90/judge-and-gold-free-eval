# Area Chair review, version 2: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

**Materials.**
- **PDF.** `papers/D-iclr-v2/main.pdf`, 62 pages.
  - Main text pp. 1-9; the Conclusion ends at l. 480.
  - Statements pp. 9-10, references pp. 10-16, appendix pp. 17-62.
  - I read pp. 1-10 as page images (pdftoppm), plus a 220-dpi render of p. 7 cropped to Figures 3 and 4. Appendix pp. 19-27 and 53-57 were also read as images: the ledger tail, Appendices C and D, and Appendices M and N.
- **Sources.**
  - `main.tex` in full.
  - From `appendix.tex`: the ledger (Appendix B), C (prevalence), D (survey), M (R24), N (R25) and O (reasoning).
  - `tables/r24_standard.tex`, `tables/r25_types.tex`, `tables/prevalence_v2.tex`.
  - `registration_round24.md` and `registration_round25.md`, including their outcomes.
  - `survey/practice_survey.md`.
  - `papers/analysis/r25_verify_sonnet.json`.
  - Spot checks of `papers/analysis/prevalence_v2/adjudicated_*.jsonl`.
  - The v1 `papers/D-iclr/main.tex`, to see what was cut.
- **Context.** I read `round24_review.md` and `final_review2.md` for v1.
- **Line numbers** are PDF margin numbers unless marked `main.tex`.
- **Writes.** Nothing was modified except this file.

---

## 1. Summary

**Question.** When a question has several correct answers, does a reference-guided LLM judge use the reference as an answer key? The alternatives are that it is the only evidence available to a judge that cannot verify, or that the judge rewards agreement with it.

**Claims, as a reader extracts them.**
1. **P1, the swap (unchanged from v1).** Moving the reference between two correct answers moves byte-identical text by 2.7-5.4 points out of 10.
2. **P2 (extended).** Grading AUROC for correct answers that differ from the reference falls by 0.06-0.16 on MACE, now including GPT-4.1 (−0.06, interval including zero). On arithmetic it falls by 0.17-0.27. With one correct answer, the reference raises best-of-64 accuracy by 29-31 pp.
3. **P3 (unchanged).** Of correct answers a judge accepts blind, 19%-83% of those that differ from the reference drop to 3 or below once it is shown. A second blind call drops 2 of 282.
4. **New, importance.**
   - Survey: 35 of 43 benchmarks, libraries, platforms and RL pipelines grade against one reference, plus 34 research papers. None of 34 readable prompts tells the judge to credit an answer outside the reference.
   - Graders run verbatim: the SimpleQA grader (GPT-4.1, Sonnet 5) and the BrowseComp/HLE judge (GPT-4.1, o3-mini, Sonnet 5), on 149 multi-answer MACE questions, score four models 30-67 points below the answer lists.
   - A GPT-4.1 grader with the paper's rubric falls 10 points short.
   - Prevalence: 0-4% of sampled SimpleQA, BrowseComp, HLE and TriviaQA questions have several answers; 5.5% of an RL training set does.
5. **New, judge types.** Chain-of-thought, verify-first and solve-first prompts (GPT-4.1, Sonnet 5, thinking off) fall only 0.5-6 points short. A registered ≥10-point drop was falsified in 6 of 6 cells.
6. **New, fixes.**
   - The full answer list, stated as "any one of", brings all five graders within 0.5 points of the lists. Grading AUROC ends 0.03-0.06 above blind for three judges.
   - Thinking plus a full-credit sentence left no measurable factual false-rejection rise for Sonnet 5 (40 tasks).
   - A four-bullet recipe.

**2-minute pass** (title, abstract, Figure 1, Table 1).
- **What lands:** "graders that ship with SimpleQA, BrowseComp, and HLE" fail, and a full list fixes them. It is memorable and far more consequential than v1's abstract.
- **What also lands, and is wrong:** that SimpleQA, BrowseComp and HLE scores are 30-67 points off. They are not; the questions were MACE questions.
- **What does not land:**
  - the effect shrinks by an order of magnitude when the judge is asked to reason;
  - the benchmarks these graders ship with have almost no multi-answer questions.

A skimming reviewer who later reaches p. 6 l. 320-322 ("so their own scores change little; the risk is reuse") and p. 8 l. 388 ("Reasoning shrinks the effect by an order of magnitude") will feel the abstract oversold both. This is the paper's main new vulnerability (W1, W2).

**10-minute pass** (adds Figures 2-4, Sections 7-8).
- Figure 4a is the most persuasive figure the project has produced. The one-reference and full-list dots of five verbatim graders sit 30-67 points apart, and the full-list dots land on zero.
- Its bottom block, where the paper's most important qualification lives, is squeezed into 6 points of a 70-point axis (W8).
- The recipe (p. 8 l. 415-424) is readable and plausible. Two of its four bullets rest on evidence that is thinner than the bullets suggest (W3).

**Overall.** v2 is the more important paper. The practice survey and the verbatim graders answer "who cares?" in a way v1 could not. But v2's new claims are less well-founded than v1's old ones, reversing the v1 pattern where the core was airtight.
- **Importance.** Shown on a pool built to contain the failure, with a one-sentence "the risk is reuse" argument.
- **Fix.** The no-list fix was validated on a pool that is 90.6% correct, so false acceptances are nearly invisible.
- **Judge types.** Changing the prompt changes three things at once, so the result cannot yet say whether reasoning or the instruction removes the effect.

All three are repairable. Most of the repair is text; three small experiments close the rest.

---

## 2. Score and confidence

**Score: 7 / 10 as submitted** (accept-leaning; a hostile reviewer can push it to 5-6 through W1-W3). **Confidence: 4 / 5.**

- **Text-only edits (W1, W2 text, W4-W7, W9, W10).** These would return a secure **8**, in one to two days with no API spend.
- **Experiments E1, E2, and one of E4/E5 (Section 9).** These make a **9** credible, for about USD 50-70 and a few GPU-hours.

**Single biggest reason for the score.** The paper now makes three headline claims, and each is stated more strongly in the abstract, Table 1 and the Conclusion than its evidence supports:
- the protocol failure is "large in practice";
- verify-first prompting "cuts the shortfall";
- reasoning judges show a smaller effect.

Taken together, they give reviewers an easy dismissal: "the harm lives on a pool the authors built, and a sensible prompt removes it." The data can rebut this. The paper's text currently does not.

**Why not lower.**
- v1's core (P1-P3 with controls and a registered noise floor) is intact.
- The verbatim-grader experiment is registered, clean and striking.
- The full-list fix is registered with 9/9 grading predictions confirmed.
- The survey is verified against primary sources at pinned commits.

---

## 3. Strengths

1. **Practical relevance is now demonstrated, not asserted.**
   - Graders copied from `openai/simple-evals` and `centerforaisafety/hle` at pinned commits run with their configured judge models (App. M, p. 54 l. 2887-2897).
   - There were no parse failures, and the official and robust parses agree on every grade.
   - The HLE/BrowseComp judge credits 0.0% of 396 differing correct answers with GPT-4.1 and o3-mini (Table 58). "Graders that ship with HLE give zero credit to correct alternatives" is a sentence reviewers will remember.
2. **The survey is careful.**
   - 43 graders and 34 papers, each checked against a primary source.
   - 24 verbatim prompt files with commit headers.
   - 133 quote fragments re-matched against source text.
   - Honest caveats: prompts that could not be fetched are excluded from the tallies (`practice_survey.md` §7).
   - Quotes such as CompassVerifier's "THE STANDARD ANSWER IS ALWAYS CORRECT ... NEVER QUESTION THEM" (p. 25 l. 1327-1329) are exactly the right evidence.
3. **The fix is tested the way a fix should be.**
   - It restores accuracy on the benchmark pool: all five graders within 0.5 points (Table 58).
   - It restores *grading* against wrong answers: AUROC +0.03 to +0.06 over blind, false rejections not rising (Table 60, 9/9 registered predictions confirmed).
   - False acceptances are reported by name ("Democratic Republic of Congo", "Wales", ...).
4. **Registered falsifications are kept in the record.** P-R25A3 (6/6 falsified) and P-R24A4 (2/5 falsified) are in the ledger (p. 23-24 l. 1244-1260) and in App. M/N text. The problem is only that the main text omits them (W4).
5. **The judge-type experiment was requested by the advisor and run with a registration before any call.** It reports a result that cuts against the paper's own headline. That is scientific integrity, and it should be turned into an asset (W2).
6. **The multi-family prevalence audit fixes a v1 limitation.** Sonnet 5 and GPT-5-mini label independently, κ is reported, and both/either bounds are given (Table 5).
7. **v1's strengths are intact.** They include the byte-identical swap with a matches-neither control, the MATH-500 positive control, P3 with a same-interface noise control, the second draw against the regrade, and the complete ledger.
8. **Page budget.** The main text still ends on p. 9, and Figure 1 is on p. 1.

---

## 4. Weaknesses, ranked by severity

### W1 (major). "How important?" is answered with a pool built to contain the failure; the abstract implies the benchmarks themselves are mismeasured, and "the risk is reuse" is one sentence with weak citations

**Location.**
- **Abstract, p. 1 l. 021-024.** "(3) the harm is large in practice: run verbatim with their own judge models, those benchmark graders score four models 30 to 67 points below their answer-list accuracy on 149 factual questions."
- **Intro, p. 2 l. 076-080.** "(0% to 4% of sampled SimpleQA, BrowseComp, HLE, and TriviaQA questions), but their graders are reused where answers are not unique".
- **Section 7, p. 6 l. 320-323.** "On the benchmarks these graders were written for, 0% to 3% of sampled questions have several answers (Appendix C), so their own scores change little; the risk is reuse, and the same judge instruction reappears in agent and RL evaluations (Li et al., 2025a; Chen et al., 2025b)."
- **Conclusion, p. 9 l. 475-477.** "This matters for real evaluations: run as configured, the graders of SimpleQA, BrowseComp, and HLE score four models 30 to 67 points below..."

**Problem.**
1. **The abstract and Conclusion claim more than the data show.**
   - "Large in practice", "for real evaluations" and "those benchmark graders" invite the reading that SimpleQA, BrowseComp and HLE leaderboards are off by 30-67 points.
   - The paper's own audit says those benchmarks have 0-3% multi-answer questions. The error on their leaderboards is bounded by roughly that rate: at most about 3 points with adjudicated labels, 15 on HLE if every question either annotator flagged counts.
   - The 30-67 is conditional on every question having several answers.
   - The tension is disclosed only on p. 6, after the reader has formed the wrong impression.
2. **The reuse evidence in Section 7 is the weakest available.**
   - WebSailor and BrowseComp-Plus are BrowseComp-style tasks, which are single-answer by construction (BrowseComp-ZH: "only one correct and unambiguous answer", `practice_survey.md` §5b). They show the *prompt* is reused, not that it is reused *where answers are not unique*.
   - The survey has much better evidence, which sits only in App. D (p. 25 l. 1334-1338):
     - IMO-ProofBench's reference-guided grader is "prone to be overly punitive" for "unconventional yet correct solutions";
     - reference code made all three LLM evaluators worse on CoNaLa;
     - 7 of 34 papers have multi-answer tasks graded against one reference or a closed list.
     - TinyV (cited only inside Table 6) reports that a rule-based verifier mislabels 38.5% of correct responses as incorrect. That is the closest published measurement of the RL-reward cost of false negatives.
3. **Prevalence is a lower bound, and the paper does not say so.**
   - Adjudication followed a "conservative rule" that favors UNIQUE and appeals to dataset design intent. Example: `adjudicated_simpleqa.jsonl` simpleqa-764 (Leslie Fox Prize 2017): "strictly, multiple people received Leslie Fox Prizes in 2017 ... defensible as MULTI ... The conservative rule favors UNIQUE."
   - 135 disagreements were never adjudicated and "kept the conservative label" (p. 25 l. 1297-1299).
   - BrowseComp has 108/200 *unclear*, and HLE has 53/200 unclear and 15% by either annotator. κ ≤ 0.35.
   - The main text quotes "0% to 4%" and "0% to 3%" without any of this. Understating prevalence *hurts* the importance argument, so disclosing it helps the authors.
4. **"Importance" never reaches a quantity a practitioner can act on.** No sentence says how many points a given pipeline could be off by. The RL case (5.5-18% of WebInstruct-verified questions, graded by General-Reasoner's single-reference verifier) is the most direct practical harm, and the paper does not measure it.

**Is "the risk is reuse" convincing?** As written it is a weakness: an unquantified sentence resting on two single-answer citations. As an argument it is sound and can be made airtight. The error depends on the grader's instruction multiplied by the answer space of the data it is pointed at. The graders are demonstrably pointed at open answer spaces: RL training sets, deep-research reports, proofs and code.

**Fix (text; no data).**
- **Abstract**, replace "(3) the harm is large ... 149 factual questions." with:
  > "... and (3) those benchmarks rarely contain such questions (0% to 3% of the questions we sampled), but when their graders are run verbatim, with their own judge models, on 149 factual questions that have several correct answers, they score four models 30 to 67 points below their answer-list accuracy."

  A full replacement abstract is under W2.
- **Section 7, l. 320-323**, replace with:
  > "On the benchmarks these graders were written for, 0% to 3% of sampled questions have several answers after adjudication, a lower bound because disagreements were resolved toward a unique answer (up to 15% on HLE by either annotator; Appendix C); this caps the error on those leaderboards at about 3 points. The risk is reuse where answers are open: the same single-reference prompts reward RL training sets in which 5.5% to 18% of questions admit several answers (Ma et al., 2025), grade informal proofs, where IMO-ProofBench's grader is reported to be "overly punitive" for unconventional correct solutions (Luong et al., 2025), and grade code, where a reference program made LLM evaluators worse (Tong & Zhang, 2024)."
- **Intro, l. 078-079**, "(0% to 4% of sampled ... questions)" becomes:
  > "(0% to 4% of sampled SimpleQA, BrowseComp, HLE, and TriviaQA questions after an adjudication that favored a unique answer; up to 15% by either annotator)"
- **Conclusion, l. 475-476**, "This matters for real evaluations: run as configured, the graders of ..." becomes:
  > "This matters wherever such graders meet open answer spaces: run as configured on questions with several answers, the graders of ..."
- **Limitations, "Labels" bullet, add:**
  > "Prevalence labels come from LLM annotators with low agreement (κ ≤ 0.35), an adjudication rule that favored a unique answer, and 135 unadjudicated disagreements."

**What would make it airtight (experiments; Section 9).**
- **E4.** The RL verifiers the survey names, run verbatim on the 596 benchmark answers. General-Reasoner's `general-verifier`, xVerify and CompassVerifier are open models, so this costs GPU-hours and no API spend.
- **E5.** Realized bias on natural data: the flagged multi-answer items from the prevalence audit, answered by 4 models and graded by the shipped grader, with the ~85 flagged items checked by a human.

Either one converts "risk" into a measured error rate on a surveyed pipeline.

---

### W2 (major). The judge-type result reframes the paper, and the current framing neither owns it nor can attribute it

**Location.**
- p. 8 l. 381-390 ("Judges that reason before deciding").
- Abstract l. 024-025 ("prompting the judge to verify the answer itself cuts the shortfall to 0.5 to 6 points").
- Table 1 Fixes row (l. 139-144).
- Section 8 l. 402-405.

**Problem.**
1. **The ladder in Figure 4a is not a judge-type comparison. Several factors change at once:**
   - **Instruction.** The graders say to match ("focus only on whether the answers match"). The rubric says "Compare the candidate response against the trusted reference answer" (appendix.tex l. 61). R25 asks whether the answer is correct.
   - **Output format.** The graders give a binary letter or yes/no; the rubric gives a 0-10 score thresholded at 7; R25 gives yes/no.
   - **Reasoning.** None for the graders and rubric; free-text for R25.
   - **Reference framing.** "gold target", "precise and unambiguous", "trusted" or plain.

   "Reasoning shrinks the effect" (l. 388) is therefore not identified. A direct yes/no prompt that asks *whether the answer is correct*, without reasoning, is the missing baseline.
2. **The paper's own data already point to the instruction, not reasoning, as the dominant factor, and the paper does not say so.**
   - o3-mini is a reasoning model. Under HLE's match-only prompt it credits **0.0%** of differing correct answers (Table 58).
   - Reasoning does not help when the instruction says match. This one sentence would pre-empt "just use a reasoning judge" and sharpen the story.
3. **"By an order of magnitude" (l. 388) picks its comparator.**
   - Against the match-only graders (30-67) it holds.
   - Against the paper's own rubric: GPT-4.1 goes from 9.6 to 0.5-3.0, and Sonnet 5 from 22.3 to 3.4-6.2. That is a factor of 3 or more, not 10.
4. **A change is compared with a level.** l. 386-388: "credit for correct answers that differ from the reference drops by 1 to 9 points, where the benchmark graders credit only 0% to 53% of them." The comparable level: with the reference these judges still credit **90.1%-97.5%** (Table in App. N).
5. **The failed prediction is invisible in the main text.** The registered prediction (≥10-point drop) failed 6/6. Only App. N l. ~2968 says so.
6. **Does it undermine the story?**
   - It does not undermine P1-P3, which concern the *judge*, or the practice claim, since the shipped prompts *are* match-only.
   - It does undermine the title-level impression that "LLM judges" in general favor the reference strongly. For frontier judges with a correctness-asking prompt, the effect is 1-9 points of credit.
   - The honest and more useful story is a decomposition. The shipped protocol (one reference plus a match instruction) causes most of the harm. A residual bias toward the shown answer survives a neutral correctness prompt, and it is largest for score-only and small judges.
   - That story is *more* interesting to ICLR than "judges are biased": it tells benchmark maintainers that a one-line prompt diff matters.

**Fix (text).**
- **Replace p. 8 l. 381-390 with:**
  > "**What sets the size.** The harm tracks how strongly the grader is told to match the reference. The BrowseComp/HLE judge ("focus only on whether the answers match") credits 0% to 2% of differing correct answers, even with o3-mini, a reasoning model. Our score rubric, which asks the judge to compare the candidate against the trusted reference, falls 10 to 22 points short. Three prompts that instead ask whether the response is correct (chain of thought, verify the answer on your own before comparing, or solve the question first; GPT-4.1 and Sonnet 5, thinking off; Appendix N) fall 0.5 to 6 points short: with the reference they still credit 90% to 97.5% of differing correct answers, against 98% to 99% blind. A residual pull remains for Sonnet 5 (intervals exclude zero for four of the six cells), but it is smaller than we registered: we had predicted a drop of at least 10 points in credit, and it was 0.7 to 8.6 in all six. These prompts differ from the graders in instruction, output format, and reasoning at once, so we do not attribute the reduction to reasoning alone."
- **Move the MT-Bench sentence** ("under the verbatim MT-Bench template ... 3.59 points") to Section 4 after l. 228. It is a swap result on arithmetic and reads as a non sequitur in a MACE paragraph. Write it as: "The swap survives the verbatim MT-Bench template, which drops 'trusted' and asks for an explanation first (3.59 points for Qwen2.5-7B; Appendix I)."
- **Title.** Keep it. Section 1's P-list paragraph (p. 2 l. 102-107) should add one clause:
  > "...; the size depends mostly on the grader's instruction: prompts that ask whether the answer is correct, rather than whether it matches, shrink it to a few points (Section 7)."
- **Replacement abstract (about 215 words; every number checked against Tables 58, 60 and N, and Table 5):**
  > "LLM judges often grade with a reference answer, including the graders that ship with SimpleQA, BrowseComp, and Humanity's Last Exam, on the premise that it acts as an answer key: a correct response should score the same whichever correct answer is shown. On questions with several correct answers the premise fails. We separate three readings of a reference (an answer key, the only evidence for a judge that cannot verify, or an answer the judge rewards for matching). Swapping the reference between two correct answers moves the score of identical text by 3 to 5 points out of 10, and correct answers that differ from the reference are rejected far more often, even ones the judge accepts without a reference. Those benchmarks rarely contain such questions (0% to 3% of those we sampled), but run verbatim on 149 factual questions that do, their graders score four models 30 to 67 points below their answer-list accuracy. The size follows the instruction: prompts that ask whether the answer is correct, rather than whether it matches, leave 0.5 to 6 points, and giving the grader the full answer list removes the shortfall. We test eleven judges on constructed tasks, MACE, and MATH-500, with a complete preregistration ledger. A low score from a reference-guided judge does not reliably mean the answer is wrong."

**Minimal experiment (E1; about USD 15, under a day).** Registered, on the 596 benchmark answers, GPT-4.1 and Sonnet 5, blind and one reference:
- **(a) Direct.** The R25 correctness wording with "Answer only 'correct: yes' or 'correct: no'", with no reasoning.
- **(b) Edited HLE judge.** The HLE judge verbatim with only "do not argue for any answer different than [correct_answer], focus only on whether the answers match" deleted, plus one sentence: "A response that gives a different answer that is also correct is correct."

Cost is about 4 × 1,192 calls.
- (a) separates instruction from reasoning.
- (b) is the one-line diff a benchmark maintainer would actually ship, and it is currently untested (W3.4). If (b) closes most of the 65-point gap, it is the paper's most practical result.

---

### W3 (major). "How to fix?" is actionable, but the no-list fix is validated where false acceptances are nearly invisible, and the recipe stacks untested combinations

**Location.**
- Section 8 l. 402-413.
- Recipe l. 415-424.
- Abstract l. 024-025.
- Conclusion l. 478-480 ("Where the answers cannot be listed, ask the judge to verify the answer itself before it consults the reference").

**Problem.**
1. **The base rate hides false acceptances.**
   - The benchmark pool is 90.6% correct: 56 wrong answers of 596.
   - Pooled "accuracy minus list" is dominated by recall, so a lenient grader looks excellent.
   - With the reference, the verify-first and solve-first judges credit **5.4%-12.5%** of wrong answers. The HLE judge credits 0.0%-1.8% with one reference and 3.6%-5.4% with the full list (Tables 58 and N).
   - On n = 56 this is noisy, and some "wrong" answers are unlisted aliases. The direction is still the classic trade-off the recipe does not mention.
   - The graders the paper cites are HLE and BrowseComp: benchmarks built so that models *cannot* solve the questions, where most answers are wrong.
   - A prompt that says "verify on your own" or "solve the question first" relies on the judge's knowledge exactly where it is weakest. At 70% wrong answers, a 10% false-acceptance rate adds 7 points, more than the ≤3-point multi-answer error the fix removes.
   - None of the verify-first, solve-first or CoT prompts was run on the 40-task subsample that has many wrong answers and grading AUROC (R25 ran only on the benchmark pool).
   - v1 showed the max rule costs up to 6.7 pp when the answer is unique. **The no-list fix has no P2′-style single-answer control.**
2. **The "No list and no checker" bullet (l. 419-422) stacks four interventions tested separately:**
   - verify-first: 2 judges, benchmark pool, thinking off, no full-credit sentence;
   - "tell it other answers can be correct": rubric, 40 tasks, two judges;
   - "prefer a thinking judge": rubric, 40 tasks, Sonnet 5 and two Qwen3;
   - "less relief from small judges": synthetic grid.

   The combination is never run.
3. **The "Audit" bullet (l. 423-424) is unvalidated.**
   - In deployment, "correct answers accepted blind" is unknowable. Blind-accept/referenced-reject disagreements also arise from blind over-credit on single-answer questions, the very reason references exist (l. 072-073).
   - Its precision for flagging multi-answer questions is never measured. It could be measured now from stored scores: the MACE natural mix has k=1 and k>1 questions, and MATH-500 has unique answers.
4. **The cheapest benchmark-maintainer fix is untested.** Delete the match-only line and add a full-credit sentence to the *shipped* grader. The full-credit sentence was run only with the paper's own rubric (W2, E1b).
5. **The full-list fix is a closed list.**
   - The survey itself flags closed lists as the dominant pattern ("Correctness remains membership in a closed list", `practice_survey.md` §6; Pattern C).
   - MACE's lists miss 2.3%-8.1% of correct answers. The paper cannot see whether an "any one of" list makes judges *more* dismissive of unlisted correct answers, because its gold is the list itself (App. E l. ~223: "Aliases missing from the list count as wrong").
   - The recipe's "benchmark authors should ship such lists" (l. 417-418) moves the failure one level up without testing it.
6. **Overclaims.**
   - **Intro, p. 3 l. 147-148.** "a thinking judge told that other answers can be correct removed the factual effect for one judge". This rests on a prediction scored *not confirmed*: −0.2 pp [−7.2, +4.6] on 40 tasks, with AUROC change −0.024 [−0.062, +0.006]. Absence of a detected rise is not removal.
   - **Conclusion, l. 476-478.** "The remedy is to grade against every correct answer: ... judges grade at least as well as blind." This is scoped nowhere to "when the answers can be listed", and "judges" means three judges on 40 tasks.
   - **Section 8, l. 397-399.** "mostly answers that name a listed country differently, such as 'The Democratic Republic of Congo' or 'Wales'". "Wales" for "United Kingdom", "Sudan" for "South Sudan" and "Territory of New Guinea" for "Papua New Guinea" are not naming variants; only the DRC case clearly is (App. M l. 2912-2917).

**Fix (text).**
- **Recipe, replace l. 415-424** with evidence-scoped bullets:
  > • **Several answers that can be listed:** give the grader every one, introduced by "any one of the following is a complete correct answer" (five graders from two developers on 149 questions; grading on 40 tasks for three judges). A list is still closed: whether it makes judges reject correct answers it misses is untested.
  > • **A checker exists** (constraints, tests, solvers, proof assistants): grade with it.
  > • **No list and no checker:** do not tell the grader to match; ask whether the response is correct, and have it verify the answer or solve the question before consulting the reference (two judges, one pool). Adding that other answers can be correct and using a thinking judge each helped on 40 tasks; we did not test the combination, or these prompts on questions the judge cannot answer, where they may credit more wrong answers (5% to 13% of 56 wrong answers here, against 0% to 2% for the HLE judge).
  > • **Audit:** score a sample blind as well and read the answers accepted blind but rejected with the reference; these include multi-answer questions and blind over-credit, in proportions we did not measure.
- **Intro l. 147-148:**
  > "...and thinking plus a sentence that other answers can be correct left no measurable rise in factual false rejections for one judge on 40 tasks (Section 8)."
- **Conclusion l. 476-480:**
  > "Where the correct answers can be listed, grade against all of them: given the full list, the same graders match it within a point, and three judges grade at least as well as blind. Where they cannot, do not instruct the grader to match; ask whether the answer is correct, and audit disagreements between blind and referenced scores."
- **Section 8 l. 397-399:**
  > "mostly an alias the string matching misses ("The Democratic Republic of Congo", credited in four configurations), and in single configurations "Territory of New Guinea", "Sudan", and "Wales"; the registered bound of 3 points failed for the BrowseComp/HLE judge with GPT-4.1 and o3-mini."
- **Audit bullet from stored data (zero API).** Compute, for Sonnet 5 and Opus 5 on MACE and Qwen2.5-7B on MATH-500, the share of blind-accept/referenced-reject disagreements on k=1 against k>1 questions. Report one precision number, or drop the bullet.

**Minimal experiments.**
- **E2 (about USD 25, one day).** The R25 prompts (verify-first, solve-first) and E1b on:
  - **(i)** the 40-task MACE subsample: grading AUROC and false acceptance, directly comparable to Table 60;
  - **(ii)** a hard single-answer pool with a high wrong-answer rate, e.g. 150 SimpleQA questions answered by Llama-3.1-8B and Haiku 4.5 (accuracy well below 50%), graded by the SimpleQA grader against verify-first.

  Report false acceptance. This is the P2′ control for the recommended fix.
- **E3 (about USD 10).** A leave-one-out list: give the full list minus the candidate's own answer, and measure credit for that held-out correct answer against one reference. This tests the closed-list risk directly.
- **E6 (about USD 15).** The recipe as written: verify-first plus the full-credit sentence plus adaptive thinking, on both the benchmark pool and the 40-task subsample.

---

### W4 (moderate). Registered failures in the new experiments are missing from Table 1 and the main text, which cuts against the paper's registration brand

**Location.**
- Table 1 caption (p. 3 l. 110-113): "Registered predictions that failed near these rows: for P1, ...; for P2, ...; for P3, ...".
- Section 8 l. 397; Section 7 l. 381-390.

**Problem.** The caption lists failures only for P1-P3. The Consequence and Fixes rows omit:
- **P-R24A4:** extra wrong-answer credit with the list ≤3 points, falsified for 2 of 5 graders;
- **P-R25A3:** a ≥10-point credit drop under reasoning prompts, falsified 6 of 6;
- **P-R25A1:** a referenced shortfall for verify-first and solve-first GPT-4.1, not confirmed for 2 of 6;
- **P-R24D3:** a remaining rise under thinking plus the sentence, not confirmed.

A reviewer who opens the ledger will see eight failed or unconfirmed cells beside rows whose Verdicts read "Holds" and "The list removes the effect".

**Fix.** Append to the Table 1 caption:
> "; for the consequence and fixes, that extra wrong-answer credit with the full list would stay within 3 points (BrowseComp/HLE judge with GPT-4.1 and o3-mini), that reasoning-first prompts would cut credit for differing correct answers by at least 10 points (all six), and that false rejections would still rise under thinking plus the full-credit sentence."

Change the Table 1 Consequence verdict (l. 136-138) from "Holds for nine grader configurations from two developers" to:
> "Holds for nine configurations from two developers; 0.5-6 points for six reasoning-first configurations"

---

### W5 (moderate). Internal inconsistencies and dangling references introduced by the v2 cuts

**Problems and fixes.**
1. **Redraw range.**
   - **Where it appears:** Table 1 (l. 137) says "a redraw moves credit by 23–38 points, a regrade by about 3"; Section 7 (p. 8 l. 377-379) says "those that stop or start matching move by 12.5 to 38 points, against about 3 when the Claude graders re-grade".
   - **Why the text is wrong:** 12.5 and 19.0 are GPT-4.1 (R24-B), which was not re-graded, so the "against about 3" contrast does not apply to it.
   - **Fix, l. 377-379:** "those that stop or start matching move by 23 to 38 points under the three Claude graders, against about 3 when they re-grade with the first reference, and by 12.5 and 19 points under GPT-4.1, which was not re-graded."
2. **"Figure 3a" (p. 5 l. 264, `main.tex` l. 200).** Figure 3 now has one panel and no "a". Fix: "(Figure 3)". The label `fig:reasoning` is a leftover name; rename it to `fig:acceptance`.
3. **"we test the last of these only partly (Section 6)" (p. 2 l. 091-092).**
   - **Why it is stale:** v1's "Not only the prompt" paragraph was removed. It held the MT-Bench template and full-credit sentence, and Section 6 no longer tests prompts.
   - **Fix:** "(Sections 4 and 8)", after moving the MT-Bench sentence to Section 4 (W2).
4. **AI use statement, p. 10 l. 489-491.**
   - **Text:** "label a sample of dataset questions for the prevalence audit; both labeling passes came from one model family".
   - **Why it is wrong:** v2's audit used Sonnet 5 and GPT-5-mini (App. C l. 1296-1297), and the intro relies on that.
   - **Fix:** "label dataset questions for two prevalence audits: the first audit's two passes came from one model family; the second used annotators from two developers (Claude Sonnet 5, GPT-5-mini) and a Claude adjudicator. No labels were checked by human annotators."
5. **Survey wording, p. 2 l. 068-070.**
   - **Text:** "35 grade with an LLM judge given one reference, as do 34 recent research papers".
   - **Why it is wrong, (a):** App. D's definition (l. 1320-1321) is "one gold answer, *or a closed list of them*"; MixEval and FreshQA give closed lists.
   - **Why it is wrong, (b):** the 34 papers are 34 of 34 by construction, since candidates that did not qualify were dropped (`practice_survey.md` §5). Table 6's "Surveyed 34 / One reference 34" invites a 100% reading.
   - **Why it is wrong, (c):** the 43 graders were chosen as prominent, not sampled.
   - **Fix:** "Of 43 prominent benchmarks, evaluation libraries, cloud platforms, and RL reward pipelines we checked (a purposive sample, not a census), 35 grade with an LLM judge given one reference or a closed list, and we found 34 recent papers that do the same". In Table 6, rename the research-paper columns "Found / Reference-guided" and add "(selected because they use one)".
6. **Two prevalence ranges.** Intro "0% to 4%" (l. 079, four datasets) against Section 7 "0% to 3%" (l. 321, three datasets). Both are correct, but a reader sees two numbers for "the same thing". Name the datasets at l. 321: "(SimpleQA, BrowseComp, HLE)".
7. **Limitations lost the "trusted" caveat.**
   - v1's "Judges and prompts" bullet said the MT-Bench template and full-credit instruction "do not exhaust reference prompts".
   - v2 dropped it, while Setup (l. 188) still uses "Reference answer (trusted)" and rubric (b) says "Compare ... against the trusted reference answer".
   - **Fix:** restore: "Our rubric calls the reference trusted and asks the judge to compare; the MT-Bench template, the verbatim benchmark graders, and three correctness prompts vary this wording, but do not exhaust reference prompts."

---

### W6 (moderate). General-phenomenon framing (advisor challenge 2) is asserted in two sentences; page 1 still says "arithmetic puzzle"

**Location.**
- p. 2 l. 081-085: "The failure is not specific to math: any output with several valid forms can be graded against just one of them, and LLM judges are used where no checker ... exists. We use arithmetic tasks as a testbed because ...".
- Figure 1 (p. 1): a digit-sum puzzle.

**Problem.**
1. **First impressions.** The page-1 image and the first intro sentence are a checkable arithmetic task, exactly where "just use a checker or Lean" is the natural retort. The rebuttal comes 25 lines later, at the end of a 346-word paragraph.
2. **"Not specific to math" is asserted, not evidenced, beside the claim.**
   - The paper's own non-math and non-QA test (MBPP) found *no measurable effect* (p. 5 l. 229-230), and that is not acknowledged next to the claim.
   - The best external evidence (IMO-ProofBench's punitive grading; CodeJudge; DeepResearch Bench grading reports against one reference report) sits in App. D.
3. **The factual swap is already a byte-identical result and is not on page 1.** The second draw on the benchmark pool changes only the reference for the same answer text. Answers that stop matching fall from about 100% to 62%-74% credit under the three Claude graders. That is P1 in a factual, benchmark setting.

**Fix.**
- **Text, split the intro paragraph (p. 2 l. 062-085) into two:**
  - **(i) Practice:** survey, prompts, reuse.
  - **(ii) Scope, starting with:** "The failure is not about math. Factual QA, agent answers, informal proofs, and RL rewards on general reasoning data have no formal checker, which is why LLM judges grade them; IMO-ProofBench's reference-guided grader is reported to penalize unconventional correct proofs (Luong et al., 2025). We use arithmetic tasks only as a controlled testbed, because a checker lists every correct answer, and factual questions because benchmark graders operate there; on code, where correct programs have few distinct outputs, we found no effect (Appendix S)."
- **Figure 1 (optional, half a day).** Add a factual row to panel (c): "benchmark answers, second draw: credit for the same text 99% → 62%-74% when the reference moves off it". Values from `r23a_regrade_*.json` / `r22b` are already stored. It shows P1 outside arithmetic on page 1.

---

### W7 (moderate). Coherence: Section 7's third paragraph is a fix, Section 8 repeats it, and the densest paragraphs are the new ones

**Location and measurements** (words and digit groups counted from `main.tex`):

| Paragraph | Words | Numbers | Messages |
|---|---|---|---|
| Intro practice paragraph (p. 2 l. 062-085) | 346 | about 15 | 4: practice, prevalence, scope, question |
| §7 "Graders shipped with benchmarks" (l. 313-323) | 168 | 19 | |
| §7 "Judges that reason before deciding" (l. 381-390) | 165 | 17 | |
| §8 "When the answers cannot be listed" (l. 402-413) | 204 | 23 | 7 interventions, 2 of them negative results |
| Abstract | 235 | | Its "(1) ... (2) ... (3)" sentence is about 95 words |

**Problem.**
1. **Does the paper read as one argument?** Mostly yes: question, three readings, P1-P3, consequence, fix. The v2 abstract, however, leads with benchmark graders and ends with fixes, while the body keeps P1-P3 first and reaches the practical result on p. 6. That is acceptable, but Sections 7 and 8 overlap:
   - §7 l. 381-390 introduces verify-first and solve-first as a *moderator*;
   - §8 l. 403-405 re-quotes the same "0.5 to 6 points ... against 30 to 67".

   A reader sees the same result twice under two headings.
2. **Placement of 7-8 relative to P1-P3.** It is defensible, but the importance question is answered late. Two options:
   - **(a), recommended, cheap.** Keep the order. Retitle §7 "How much it matters, and what sets the size". End it with the instruction ladder (W2 text). Make §8 fixes-only, citing §7 rather than repeating it.
   - **(b)** Move "Graders shipped with benchmarks" and Figure 4a's top block to a short §4 right after Setup, then P1-P3 as "why". This answers "how important?" by p. 4, but it breaks the prediction-first logic that v1 reviewers valued. I would not do (b) this close to the deadline.
3. **What the cuts made confusing.**
   - **Figure 3 as one panel is fine.** It reads in about 15 seconds, apart from the dangling "3a" (W5.2).
   - **Removed thinking paragraphs.** Table 1's P1 verdict "near zero on arithmetic with thinking" and the P3 verdict "Where thinking removes the effect (arithmetic; Section 8)" now rest on one parenthetical in §8 l. 407-408 ("2.85 to 0.32 points for Sonnet 5; Appendix O"). It survives, but a reader looking for the thinking result in P3 finds only a forward pointer.
   - **Setup still carries the cost.** It describes Qwen3-8B/14B explanation-first, thinking modes and the Sonnet CLI (l. 193-195), which the main text now uses in one clause.
   - **Table 2 removal is fine.** The max rule is correctly reduced to one exploratory clause. The "trusted wording" defense that lived beside it was lost (W5.7).
4. **§8 "When the answers cannot be listed" is the new hardest paragraph.** It mixes the verify prompt, the full-credit sentence, adaptive thinking, the arithmetic swap, the combination, small judges, blind-then-reveal and the max rule.

**Fix.**
- **§8 split into two paragraphs:**
  - **"Prompt changes that help"**, 4 sentences: verify/solve (cite §7); full-credit sentence (36→18/8); thinking (36→15; arithmetic near zero); both (−0.2 [−7.2, +4.6], 40 tasks).
  - **"What did not help"**, 1 sentence: "The instruction did little for Qwen2.5 judges up to 7B, a registered blind-then-reveal protocol left grading below blind for most open judges, and an exploratory max rule costs up to 6.7 pp when the answer is unique (Appendix G)."
- **Free about 12 lines for W1/W2 text:**
  - **Setup "Candidates and judges" (l. 193-195).** Replace the Qwen3/CLI sentence with "Reasoning variants are in Appendix O."
  - **Section 4, l. 228-232.** Move the MathConstraint, MBPP and masking sentences to one line: "Smaller studies on puzzles, code, and reference format are in Appendices J, K, R and S." Keep the MBPP null in the scope paragraph (W6).
  - **Section 2.** Shorten the P2 derivation (l. 166-171) by one sentence: "P2 separates both from the answer key (Appendix P)".
- **Abstract.** Adopt the W2 replacement (about 215 words, no enumerated 95-word sentence).

---

### W8 (moderate). Figure 4 hides the paper's most important qualification; Table 1 is dense

**Figure 4 (p. 7 l. 347-371), read at 220 dpi.**
1. **The reasoning block is compressed.** Panel (a) spans −70 to 0. The six "Judges that reason before deciding" rows sit within [−7, 0], so their intervals and the blind crosses overlap into one cluster. W2's decomposition, the result a reviewer must see, is visually a smudge.
2. **Mixed comparators.**
   - The legend mixes four markers across three blocks: one reference, full list, blind, and thinking + full-credit sentence.
   - The triangle appears only in panel (b).
   - The rubric rows have no full-list marker, and the graders have no blind marker. A reader must work out which comparisons exist per block.
3. **Panel (b)** is about 30% of the width with about 40% blank space. Its x-label wraps onto two lines and its fonts are about 6.5-7 pt at print.
4. **The metric under-reports the fix trade-off.** "Accuracy minus answer-list accuracy" nets missed correct answers against credited wrong answers. For the no-list prompts the per-answer credit metric (differing correct credited; wrong credited) is the honest one.

**Fix.**
- Split (a) into **(a1)**, graders and rubric on [−70, +2], and **(a2)**, reasoning-first prompts on [−10, +2], sharing the row grammar.
- Or replace (a2)'s x-axis with "differing correct answers credited (%)", with blind and reference markers and the benchmark graders' 0-53% annotated at the left edge.
- Put the E1 direct and edited-grader rows in (a2) when available.
- Enlarge (b) to the full height of (a).
- Caption: state the n (396 differing correct, 144 matching, 56 wrong) and "o3-mini is a reasoning model".

**Table 1 (p. 3 l. 108-145).**
- It now fills about 45% of p. 3 with six rows. The Fixes row's "0.5–6 points short (0–1 blind)" is hard to parse.
- **Fix, Fixes row Observed:**
  > "Full answer list: five graders within 0.5 points of the lists; grading AUROC 0.03-0.06 above blind (three judges, 40 tasks). Prompts asking whether the answer is correct: 0.5-6 points short (two judges). Thinking plus a full-credit sentence: no measurable factual rise (one judge, 40 tasks)"
- **Fix, Fixes row Verdict:**
  > "A list removes the shortfall; prompts shrink it"

---

### W9 (minor-moderate). Missing related work that reviewers will name

**Problem and fix.**

| Group | Works | What to add |
|---|---|---|
| RL verifier false negatives | TinyV (Xu et al., 2025, `xu2025tinyv`, in bib); "Pitfalls of Rule- and Model-based Verifiers" (Huang et al., 2025, `huang2025pitfalls`, in bib); xVerify, CompassVerifier (in bib) | Cited only inside App. D Table 6. Add to Related work §9 "Reference-guided judging": "Verifiers for RL rewards are evaluated mainly on equivalent forms of one answer (Chen et al., 2025; Liu et al., 2025b), and false negatives from rule-based checking are frequent enough to slow RL (Xu et al., 2025; Huang et al., 2025); we study false negatives that remain when a model verifier is shown one of several correct answers." |
| Sycophancy and suggested-answer bias | Sharma et al. (2023), "Towards Understanding Sycophancy in Language Models"; Turpin et al. (2023), "Language Models Don't Always Say What They Think" | Not in the bib. The "agreement" reading is conceptually close to models deferring to an answer suggested in the prompt, and reviewers will ask how it differs. One sentence in "Judge biases": "The agreement reading resembles sycophancy toward an answer suggested in the prompt (Sharma et al., 2023; Turpin et al., 2023); here the suggested answer is correct, so deference and correctness conflict only when a different answer is also correct." |
| Answer equivalence and multi-answer QA | PEDANTS / CFMatch (Li et al., 2024), which the survey considered and dropped; QAMPARI (Amouyal et al., 2022) | One clause in "Single references and many correct answers". |
| Answer matching as a recommended protocol | Chandak et al. (2025), "Answer Matching Outperforms Multiple Choice" (in the survey) | Its matcher is told "ONLY check whether the given response matches the ground truth answer" (`practice_survey.md` §5b). Name it in the intro as a currently *advocated* practice; that strengthens the importance argument. |

---

### W10 (minor). Smaller correctness and wording items

1. **Intro, p. 2 l. 102-104.** "P3 indicates an agreement component ... for all six judges with a usable acceptance test". This is fine, but with v2's judge-type result, add "for score-only judges" or scope it to the judges of Figure 3. R25 judges were not tested for P3.
2. **Section 8, l. 400-401.** "false rejections do not rise": −2.3 [−8.0, +4.9], −6.3 [−12.8, −1.1], −2.2 [−4.6, −0.5] (Table 60). Opus 5 and GPT-4.1 *fall*. Write "false rejections do not rise, and fall for Opus 5 and GPT-4.1".
3. **Section 8, l. 399-400.** "AUROC is 0.03 to 0.06 above blind": Opus 5's interval is [−0.000, +0.084]. Write "0.03 to 0.06 above blind (Opus 5's interval touches zero)".
4. **Section 7, l. 386-387.** "intervals exclude zero for four of the six": verify-first GPT-4.1's reference-minus-blind upper bound is +0.0 (−1.2 [−2.4, +0.0]). Write "exclude or touch zero for five".
5. **Section 7, l. 318-319.** "the BrowseComp/HLE judge credits 0% to 2%": the Sonnet 5 value is 2.3%. Acceptable, but "0% to 2.3%" avoids a rounding query next to "47% to 53%".
6. **Figure 4 caption, l. 370.** "on 40 MACE tasks": name them "the 40-task MACE subsample of Figure 2".
7. **App. C, p. 25 l. 1297-1299.** State what the "conservative label" is ("UNIQUE unless a concretely different correct answer is established") and that it lowers measured prevalence.
8. **App. D Table 6.** Research-paper row header (W5.5).
9. **Prevalence of NQ-open (30%, l. 079).** This comes from the single-family v1 audit (κ 0.74). Mark it as such where it sits beside the two-family numbers.

---

## 5. Answers to the assessment questions

### Q1. Does v2 convincingly answer "how important?"
**Partly.** The survey plus the verbatim graders convincingly establish that the *protocol* is standard and that it fails catastrophically on multi-answer questions: a 65-point shortfall and 0% credit.

The paper does not yet establish that the failure *occurs at scale anywhere a practitioner cares about*. The benchmarks whose graders fail have 0-3% prevalence, and the reuse argument is one sentence with single-answer citations (W1).

- **Is "risk is reuse" a strength or a weakness?** As written, a weakness: it reads as a concession. As an argument, it is the right one: harm equals instruction multiplied by answer space, and the survey shows these prompts grade open answer spaces.
- **To make it airtight:**
  - **(i)** Quantify the bound on shipped benchmarks (text: ≤3 points, 15 by either annotator).
  - **(ii)** Move the survey's multi-answer reuse cases (IMO-ProofBench, CodeJudge, the 7 papers, WebInstruct plus General-Reasoner) into §7.
  - **(iii)** Measure one real reuse pipeline: E4, the open RL verifiers verbatim; or E5, realized bias on flagged natural items with human checks.
  - **(iv)** Disclose that prevalence is a lower bound.

### Q2. Does v2 convincingly answer "how to fix?"
**For listable answers, yes.**
- The full-list fix is registered and replicated across five graders and two developers.
- It is checked on grading AUROC, and its false acceptances are named.
- It is near-obvious ("give the judge the answer key"). Its value is showing that judges comply with "any one of" and do not over-credit.
- Its closed-list risk is untested (E3).

**For non-listable answers, not yet.** Verify-first and solve-first are supported only on a 90.6%-correct pool, by two judges with thinking off. They credit 5-13% of wrong answers against 0-2% for the HLE judge, and they are untested where the judge cannot solve the question (HLE and BrowseComp, the motivating benchmarks).

**Overclaims:**
- the thinking-plus-sentence result "removed" the effect (one judge, 40 tasks, a not-confirmed prediction);
- the recipe stacks untested combinations;
- the audit bullet has no measured precision;
- the Conclusion's unscoped "The remedy is to grade against every correct answer".

The prompt wordings are the authors' own, and none was tested for sensitivity to wording. E1b, a one-line edit of the shipped grader, would be the most actionable fix and is missing (W3).

### Q3. Does the judge-type result undermine the story?
**It undermines the implicit claim that LLM judges in general favor the shown answer strongly. It does not undermine P1-P3 or the practice result**, because the shipped prompts are match-only.

- **As framed:** the result appears as a moderator inside "How much it matters". The phrase "by an order of magnitude" is set against the most extreme comparator, the failed ≥10-point prediction is absent from the main text, and the confound (instruction, format and reasoning change together) is unacknowledged. That framing is not fully honest and not maximally useful.
- **Reframed as a decomposition:** the instruction dominates (o3-mini credits 0% under "match"), and a residual pull survives correctness prompts. Framed that way, it becomes the paper's most useful practical insight.
- **Needs:** E1a, a direct yes/no correctness prompt, to attribute it (W2).

### Q4. Story coherence and cognitive load
- **One argument?** Yes, with a seam: §7's reasoning paragraph and §8's no-list paragraph report the same result twice (W7).
- **Abstract?** Clearer than v1 on importance, but it misleads on where the 30-67 points were measured. It omits the prevalence tension and the judge-type result, and it still has a 95-word enumerated sentence (W1, W2 replacement).
- **§7-8 placement?** Defensible after P1-P3. Recommended: retitle §7 to include "what sets the size", and make §8 fixes-only.
- **Cuts?**
  - Figure 3 as one panel is fine apart from the dangling "3a".
  - The thinking results now survive only as a parenthetical, which suffices.
  - The Table 2 removal is fine.
  - The loss of v1's "Not only the prompt" paragraph removed the paper's defense against the "trusted" wording, and left a stale "(Section 6)" pointer (W5.3, W5.7).

### Q5. Correctness red flags, overclaims, missing baselines, related work, presentation
**Red flags and overclaims:**
- the redraw range, 12.5 against 23-38 (W5.1);
- "Figure 3a" (W5.2);
- the stale "(Section 6)" pointer (W5.3);
- the AI statement's one-family claim (W5.4);
- "given one reference" against closed lists, and 34/34 by selection (W5.5);
- a change compared with a level at l. 386-388 (W2.4);
- "order of magnitude" (W2.3);
- "removed the factual effect" (W3.6);
- the unscoped Conclusion remedy (W3.6);
- "Wales" as a naming variant (W3.6);
- registered failures omitted from Table 1 (W4);
- the prevalence lower bound undisclosed (W1.3).

**Missing baselines:**
- a direct yes/no correctness prompt, and the shipped grader minus its match-only line (E1);
- no-list prompts on a high-wrong-rate, single-answer pool (E2);
- a leave-one-out list (E3);
- the recipe combination (E6);
- surveyed RL verifiers (E4);
- human labels on flagged prevalence items (E5).

**Related work:** W9. **Presentation:** W7, W8.

### Q6. Would the advisor's three challenges be satisfied?

| Challenge | Verdict | Why |
|---|---|---|
| **1. Not a "dumb judge"; protocol widespread** | **Largely satisfied** | Frontier graders (GPT-4.1, o3-mini, Sonnet 5, Opus 5) fail under shipped prompts, and the survey shows the protocol is standard. The R25 result revives a "dumb prompt" version of the objection, which the W2 decomposition answers. |
| **2. General LLM phenomenon; math only a testbed; pre-empt Lean** | **Partly satisfied** | Two sentences at the end of a 346-word paragraph. Page 1 is an arithmetic puzzle. MBPP's null is not acknowledged beside the claim. W6's split paragraph and the factual swap on Figure 1 would satisfy it. |
| **3. More judge types** | **Satisfied in breadth, not in analysis** | Types covered: score-only, few-shot classifier, structured extraction, explanation-first, CoT, verify-first, solve-first, thinking modes and a reasoning model. The comparison is confounded, and only two judges on one pool ran the new types. E1a plus W2's text would satisfy it. |

---

## 6. Numbers checked

| # | Claim (location) | Source | Result |
|---|---|---|---|
| 1 | Abstract/§7 "30 to 67 points" | Table 58: −30.4, −66.8, −66.6, −34.4, −64.9 | match |
| 2 | §7 "credits 47% to 53% ... 0% to 2%" | 53.0, 46.7; 0.0, 0.0, 2.3 | match (2.3 rounds to 2) |
| 3 | §8 "within 0.5 points ... 99% or more" | +0.3, −0.2, 0.0, +0.5, +0.2; 99.2-99.8 | match |
| 4 | §8 "at most 3 of 56 more" | h03 0 → 5.4% = 3/56 | match; registered bound failed for 2 graders (unstated; W4) |
| 5 | §8 "AUROC 0.03 to 0.06 above blind ... against 0.06 to 0.16 below" | Table 60: +0.032, +0.033 [−0.000, +0.084], +0.057; −0.153, −0.165, −0.063 | match (Opus 5 interval touches zero) |
| 6 | §8 "false rejections do not rise" | −2.3 [−8.0, +4.9], −6.3 [−12.8, −1.1], −2.2 [−4.6, −0.5] | true; two fall (W10.2) |
| 7 | §7 "GPT-4.1 falls 0.5 to 3 ... Sonnet 5 3 to 6" | Table N reference minus list: −3.0, −1.5, −0.5; −6.0, −6.2, −3.4 | match |
| 8 | §7 "Blind, all six stay within 1 point" | −0.8, −0.5, −0.3, −0.2, −0.3, +0.0 | match |
| 9 | §7 "intervals exclude zero for four of the six" | reference minus blind: [−4.0, −0.3], [−2.4, +0.0], [−1.5, +1.0], [−7.9, −3.4], [−8.7, −3.5], [−5.2, −1.8] | 4 exclude, 1 touches (W10.4) |
| 10 | §7 "credit ... drops by 1 to 9 points" | 3.0, 7.9, 1.3, 8.6, 0.7, 4.8 | 0.7-8.6; compares a change to a level (W2.4) |
| 11 | §7 "Reasoning shrinks the effect by an order of magnitude" | against the rubric: GPT-4.1 9.6 → 0.5-3.0; Sonnet 5 22.3 → 3.4-6.2 | only against the match-only graders (W2.3) |
| 12 | §7 "12.5 to 38" against Table 1 "23–38" | R24-B 12.5/19.0 (GPT-4.1, no regrade); R22-B 23.2-38.2 | **inconsistent** (W5.1) |
| 13 | §7 "GPT-4.1 by 10", "within 3 blind" | R24-B −9.6 [−12.9, −6.4]; blind −2.5 [−4.7, −0.3] | match |
| 14 | §5 "falls by 0.06 to 0.16 for the five judges we ran on MACE" | adds GPT-4.1 −0.063 [−0.133, +0.004] | match |
| 15 | §8 "36 to 18 pp ... to 8 pp for Opus 5"; "15 pp" thinking | registration_round24 context 35.6, 18.1, 14.9; v1 text 36 → 8 for Opus 5 | match |
| 16 | §8 "−0.2 pp [−7.2, +4.6]; 40 tasks" | R24-D | match; "removed" in intro is an overclaim (W3.6) |
| 17 | Intro "35 of 43", "34 papers", "27 of 34 prompts", "none tells" | `practice_survey.md` §1: 11+11+3+10 = 35 of 16+12+4+11 = 43; prompts 27/4/3 | match; definition includes closed lists (W5.5) |
| 18 | Intro "0% to 4%"; §7 "0% to 3%" | Table 5: 1.0, 0.0, 3.0, 4.0 | match; unclear 1/108/53/0; either 1.5/0/15/8 (W1.3) |
| 19 | Intro "5.5% of questions in an RL training set" | Table 5 WebInstruct 5.5 [3.1, 9.6]; either 18.0 | match |
| 20 | Table 1 "nine grader configurations from two developers" | 5 verbatim + 4 rubric; OpenAI and Anthropic | match; excludes the six reasoning configurations (W4) |
| 21 | Abstract "eleven judges" | Qwen2.5-7B, phi-4, Qwen2.5-14B, gemma-2-9b, Sonnet 5, Opus 5, GPT-4.1, o3-mini, Haiku 4.5, Qwen3-8B, Qwen3-14B | match |
| 22 | App. N "7,152 replies" | 6 × 1,192 | match |
| 23 | Ledger R24/R25 rows against the registrations | P-R24A4 3C/2F; P-R25A1 4C/2NC; P-R25A3 6F; P-R24D3 NC | match; absent from the Table 1 caption (W4) |
| 24 | §6 "Figure 3a" | Figure 3 has one unlabeled panel | **dangling** (W5.2) |
| 25 | AI statement "both labeling passes came from one model family" | App. C v2: Sonnet 5 + GPT-5-mini | **contradicts** (W5.4) |
| 26 | Wrong answers credited by R25 prompts with the reference | 8.9, 7.1, 10.7, 5.4, 12.5, 10.7% of 56 | not discussed (W3.1) |
| 27 | Main text ends p. 9; Figure 1 on p. 1 | page images | match |

---

## 7. Figure and table notes (main text)

- **Figure 1 (p. 1).** Unchanged and at the bar for P1. It anchors the paper in arithmetic (W6); consider a factual redraw row in (c).
- **Table 1 (p. 3).**
  - Dense.
  - The Consequence verdict omits the reasoning configurations.
  - The caption omits failed predictions in the new rows.
  - The redraw range is inconsistent with §7 (W4, W5.1, W8).
- **Figure 2 (p. 6).**
  - The new GPT-4.1 MACE triangle is clear.
  - The v1 nits remain: boxed-only ticks near the GPT-4.1 triangles on the replication and k-pool rows.
  - The title is still 30 words.
- **Figure 3 (p. 7).**
  - The single panel reads fast.
  - The legend sits beside the plot, leaving about 35% of the float blank on the right. Put the legend above the plot to cut the float height by about 20% and recover about 4 lines.
  - Remove the "a" reference.
- **Figure 4 (p. 7).** The strongest figure, with the key qualification compressed (W8).

---

## 8. Questions for the authors

1. What fraction of the Figure 4a gap between the HLE judge (−65) and verify-first (−6 for Sonnet 5) remains if you delete only the "do not argue for any answer different than [correct_answer], focus only on whether the answers match" line? Is the harm the instruction or the judge?
2. o3-mini credits 0.0% of differing correct answers under the HLE prompt. Did you inspect its reasoning traces? Does it recognize the alternative as correct and then follow the instruction? That would be direct P3-style evidence of instructed agreement.
3. On questions a judge cannot answer, such as HLE or BrowseComp, how often do verify-first or solve-first prompts credit wrong answers, compared with the shipped graders? Would you still recommend them there?
4. With an "any one of" list that omits the candidate's own correct answer, does credit fall below the one-reference condition? That is, does a longer closed list make judges more dismissive of unlisted answers?
5. For the RL pipelines in Table 6, what is the false-negative reward rate of `general-verifier`, xVerify or CompassVerifier on the 596 benchmark answers with one reference, compared with the full list?
6. Which way did the adjudication "conservative rule" push labels, and how many of the 135 unadjudicated disagreements would be "several" under the other annotator? What is prevalence on HLE if the 53 unclear items are resolved by a human?
7. How were the 43 graders and 34 papers selected, and what were the search terms and inclusion criteria? Would a random sample of 2025 LLM-judge papers give a similar reference-guided share?
8. For the audit bullet: on the MACE natural mix, what share of blind-accept/referenced-reject disagreements fall on k=1 questions?
9. For R25, do the six "correct: yes|no" prompts produce blind-accept → referenced-reject transitions at a rate above a same-prompt second blind call? That would extend P3 to reasoning-first judges.

---

## 9. Path to 9

### To a secure 8 (text only; one to two days; no API spend)

Listed in priority order.
1. **W1 text.** Abstract clause, §7 reuse paragraph with the survey's multi-answer cases and the ≤3-point bound, intro prevalence wording, Conclusion scope, Limitations prevalence caveat.
2. **W2 text.** Replacement abstract (about 215 words), §7 "What sets the size" paragraph with the o3-mini point, levels not changes, factor 3+ against the rubric, the failed prediction, the confound. Move the MT-Bench sentence to §4.
3. **W3 text.** Evidence-scoped recipe with the false-acceptance caveat; intro "left no measurable rise"; scoped Conclusion; the "Wales" fix. Compute the audit-bullet precision from stored scores (zero API) or drop the bullet.
4. **W4.** Table 1 caption failures; Consequence verdict.
5. **W5.** Redraw range; "Figure 3"; the "(Sections 4 and 8)" pointer; AI statement; survey "purposive ... or a closed list"; Table 6 header; the restored "trusted" limitation.
6. **W6 text.** Split the intro paragraph and add the scope paragraph with the MBPP null and IMO-ProofBench.
7. **W7.** Retitle §7; make §8 fixes-only; split the §8 no-list paragraph; free about 12 lines (Setup reasoning sentence, §4 small studies, §2 one sentence).
8. **W9.** Four related-work sentences (TinyV/Pitfalls, sycophancy, PEDANTS/QAMPARI, answer matching).
9. **W8.** Split Figure 4a into graders/rubric and reasoning-first, or use a credit axis for the latter; enlarge (b); tighten Table 1's Fixes row.

### To 9 (new data; register each first; about USD 50-70 plus a few GPU-hours; about one week)

1. **E1, instruction against reasoning** (about USD 15). A direct yes/no correctness prompt, and the shipped HLE judge minus its match-only line plus a full-credit sentence. GPT-4.1 and Sonnet 5, blind and one reference, on the 596 answers. It attributes the decomposition and tests the one-line fix a benchmark maintainer would ship.
2. **E2, false-acceptance control for the no-list fix** (about USD 25). Verify-first, solve-first and E1b on:
   - the 40-task MACE subsample (grading AUROC, comparable to Table 60);
   - a hard single-answer pool with most answers wrong (e.g. 150 SimpleQA questions answered by Llama-3.1-8B and Haiku 4.5), against the shipped grader.

   Without this, the recipe's central no-list advice is unsupported where it matters.
3. **One of the following, to make "importance" airtight:**
   - **E4, RL verifiers verbatim** (GPU only, about 2-3 GPU-hours). `TIGER-Lab/general-verifier`, an xVerify model and a CompassVerifier model on the 596 answers, one reference against the full list. This turns "risk is reuse" into a measured false-negative reward rate for pipelines named in the survey.
   - **E5, realized bias on natural data** (about USD 5 plus about 3 author-hours). Take the prevalence items flagged by either annotator: about 30 HLE, 36 WebInstruct, 16 TriviaQA and 3 SimpleQA. A human checks the alternatives. Four models answer, and the shipped graders grade. Report the realized score change per benchmark and its bound.

**Worth adding if time allows:**
- **E3, leave-one-out list** (about USD 10). This tests whether a closed "any one of" list makes judges reject unlisted correct answers.
- **E6, the recipe as written** (about USD 15). Verify-first plus the full-credit sentence plus thinking, on both pools.
- **The factual swap on Figure 1** (stored data, half a day). This answers advisor challenge 2 on page 1.

**If the text items and E1, E2 and E4 or E5 were done,** the paper would say:
- the shipped protocol is standard and fails on multi-answer questions;
- it measurably mis-rewards a real RL pipeline or real benchmark items;
- most of the harm comes from the match instruction, and a residual pull remains even when the judge is asked about correctness;
- listing the answers fixes it;
- a one-line prompt edit fixes most of it without inflating scores on hard single-answer questions.

That combination of mechanism, measured practical harm and a validated, cheap fix is a 9.
