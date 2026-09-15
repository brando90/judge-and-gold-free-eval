# Meta-review (AC), ICLR 2027: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown" (v3)

Reviewed from `reviews/v3_snapshot.pdf` (36 pages, read in full). LaTeX sources (`main.tex`, `appendix.tex`, `appendix_extended.tex`, `scripts/make_figures.py`) were checked only for exact wording and the source of one figure. The independent review below was written before reading the review of v2; the last section compares the two.

---

## 1. Summary

The paper asks whether an LLM judge given a reference answer treats it as an **answer key**: when a question has several correct answers, a correct response should score the same whichever correct answer is shown. It contrasts three readings of a reference: answer key; **verification failure** (the reference is the only evidence a judge that cannot verify has); and **agreement** (the judge favors the answer it is shown even when it could recognize the others). It then tests three predictions:

- **P1: the score follows the reference.** Identical text gains 3.0–5.3 points (0–10 scale) when the reference moves onto its answer and loses 2.7–5.4 when the reference moves off. Correct text that matches neither reference barely moves (Sec. 4, App. I, Table 8, Fig. 5).
- **P2: correct answers that differ from the reference are graded worse.** Grading AUROC against wrong answers falls by 0.06–0.16 on MACE factual questions and by 0.17–0.27 on the constructed arithmetic pools. With one correct answer the reference helps (+~30 pp best-of-64 on MATH-500) (Sec. 5, Fig. 2).
- **P3: the effect persists after blind acceptance.** Among differing correct answers a judge accepts without a reference, 19–83% score ≤3 once the reference is shown. A second blind call rejects 2 of 282 of these, against 78 of 282 with the reference (Sec. 6, Fig. 3, Table 11).

It then measures practical consequences. Setup: 149 MACE questions with several answers, one answer each from four models, and a reference drawn at random from each answer list. Graded this way, the verbatim SimpleQA and BrowseComp/HLE graders fall 30–34 and 65–67 accuracy points below the answer lists. Two open RL-reward verifiers credit 6% and 0% of differing correct answers (Sec. 7, Fig. 4, Tables 14, 20). The shortfall tracks the instruction. "Focus only on whether the answers match" gives about −66 points; a direct correctness question gives −10 to −17; reasoning-first prompts give −0.5 to −6. The paper then turns to fixes (Sec. 8):

- A full answer list closes the gap for five benchmark graders and CompassVerifier-3B, but not for General-Reasoner's 1.5B verifier.
- Correctness prompts shrink the gap. On a new set of 200 HLE questions, however, GPT-4.1 under these prompts credits 17–26% of label-wrong answers, often after declaring the reference wrong.

Supporting material:

- a survey of 34+ grader prompts (App. B);
- an LLM-labeled prevalence audit, with 0–3% multi-answer questions on SimpleQA, BrowseComp, and HLE, and 5.5–18% on WebInstruct-verified (App. C);
- a preregistration ledger of 304 predictions with every failure listed (App. D).

## 2. Strengths

1. **A clean, well-controlled core phenomenon.** The swap test holds the text byte-identical and moves only the reference. The "matches neither" arm (+0.04 to +0.30) rules out a generic distraction effect from having a reference at all. This is a strong design, and P1 replicates across open and frontier judges, two rubrics, the MT-Bench template, and a third-party combinatorial benchmark (App. R).
2. **Unusually good noise controls for frontier judges.** For P3, the same-interface second blind call is the right noise floor (Table 11). For the benchmark study, the second reference draw plus a same-reference regrade (Table 13) cleanly separates a draw effect (23–38 points of credit move) from call-to-call variation (~3 points).
3. **Practical relevance is measured, not asserted, for graders.** Verbatim graders are run at pinned commits with their configured judge models. The full-list and match-clause ablations (Tables 14, 18) make the instruction-dependence concrete and yield a usable, cheap fix.
4. **Honest negative results.** The paper reports:
   - blind-then-reveal failing;
   - selection (best-of-n) mostly not harmed;
   - effects that "mostly vanish" when the reference is an expression or masked in a worked solution;
   - small effects for code;
   - a correctness prompt that can let a judge overrule a correct reference on hard questions (new in this version, and valuable).
5. **Transparency of the ledger.** Every non-confirmed, falsified, split, and not-evaluable prediction is tabulated (Table 5). The retroactive verdict rule is disclosed together with the predictions that moved in both directions. This is well above the field norm.
6. **The HLE hard-question experiment (App. P) makes the fix recommendation meaningfully more careful.** It shows the obvious remedy ("don't tell it to match") has a cost on questions beyond the judge, and that the cost is judge-dependent (GPT-4.1 17–26% versus Sonnet 5 ≤1%).

## 3. Weaknesses, ranked by severity

### W1 (major). The headline magnitude ("30 to 67 points") is a property of the pool design and off-label use, and the abstract states it without the conditions that produce it.

- **The gap scales with how many correct answers differ from the reference.** The accuracy gap is roughly (share of all answers that are correct but differ from the reference) × (share of those rejected). In the benchmark pool, 396 of 540 correct answers (73%) differ from the reference (Table 17). That is almost exactly what a reference **drawn at random** from lists of 2–6 answers produces when models' answers are uncorrelated with the draw (expected match ≈ mean 1/k ≈ 0.3).
- **Curated references would likely give a smaller gap.** Benchmark authors typically pick the salient or canonical answer, which models also tend to give. So −67 is closer to a worst case than a typical case, and the paper never tests a canonical-reference condition.
- **These graders are run off-label.** SimpleQA, BrowseComp, and HLE were curated for single answers, and the paper's own audit finds 0–3% multi-answer items. The abstract nonetheless opens by naming those graders and then reports the 30–67 figure. A first-time reader will take away that those benchmarks mis-score models by 30–67 points, which is not what was shown.
- **A portable statistic exists.** The share of differing correct answers credited (0%–53%, Table 14) is far less design-dependent and should lead.

### W2 (major). The RL-reward consequence is an estimate, and the training experiment that tested it failed. That failure appears only in the ethics statement and the ledger.

- **What the evidence is.**
  - The main-text RL case combines two verifiers' credit rates on MACE entity questions with an LLM-labeled prevalence of 5.5–18% on WebInstruct-verified, giving "4% to 12% of correct rollouts would go unrewarded" (Sec. 7, marked †).
  - Its upper end uses the **union** of two annotators with κ = 0.35.
  - It assumes policies' answers differ from WebInstruct's (non-random) references as often as from MACE's **random** references.
  - It transfers credit rates from entity questions to STEM items, whose references are often expressions. App. J shows the swap "mostly vanishes" for expression references.
- **What the ledger shows.** Training runs 1–3 (DPO, per the extended appendix) register "Reference arm copies the reference answer more (**falsified**: its rate fell)". Held-out accuracy fell in every arm, including the controls, and a stopping rule closed the question as unresolved.
- **How the main text reports it.** The Limitations section does not mention these runs. The Conclusion says "Graders shipped with benchmarks and used for RL rewards inherit this failure wherever answers are open", which outruns what was measured: two verifiers, one factual dataset, no training effect. A skeptical reviewer will read the omission as selective reporting.

### W3 (major). The main text never cleanly separates "the judge was told to compare" from "the judge favors the reference anyway". Every headline P1/P2/P3 effect size comes from rubrics that instruct comparison.

- **What the rubrics and heading say.** Rubric a says "using the reference to check it". Rubric b says "Compare the candidate response against the trusted reference answer provided". The user-message heading is "Reference answer (trusted)". App. A acknowledges this candidly ("A judge that follows the comparison instruction could therefore favor the reference because it was told to"). The main text gives it one clause (Sec. 3).
- **The robustness evidence cited in Sec. 3 is weaker than it sounds.**
  - The **MT-Bench template also instructs comparison** ("begin by comparing the assistant's answer with the reference answer", App. I), so it is not evidence against instruction-following.
  - **Of the "four prompts that ask only whether an answer is correct" (Sec. 6), two instruct use of the reference.** Verify-first says "2. Compare: check the response against the reference answer". Solve-first says "grade the response, using your own answer and the reference answer" (App. N). The main-text phrase "ask only whether an answer is correct" is inaccurate for these two; App. A itself restricts the no-compare claim to the direct and chain-of-thought prompts.
  - **P1 (the swap) was never run under a no-compare prompt.** Under the one reasoning judge tested (Qwen3-8B thinking) it is null (−0.006, Table 9).
- **The strongest evidence against the dismissal is buried.** Under the direct yes/no prompt, credit for differing correct answers drops 91.4→73.2 (GPT-4.1) and 96.5→83.3 (Sonnet 5), with matching answers unaffected (Table 18). With an explicit sentence that "any correct answer deserves full credit", Sonnet 5's false rejections still rise 18.1 points [9.9, 28.0] (Table 16). The edited HLE judge, told that a different correct answer is correct, still leaves −31.2 and −12.6. These results are in App. L, M, and O and deserve a main-text row.
- **What to foreground.** Three components should be shown side by side: (a) the explicit match instruction, about −50 to −65 points; (b) a neutral correctness question with a reference present, about −8 to −12 points below blind and 13–18% credit loss; (c) the residual under an explicit counter-instruction, +18 FR points for Sonnet 5. Without this, the thesis sentence ("how the grader was instructed") invites the dismissal that the result is prompt-following, and the P3 "agreement" component looks partly definitional.

### W4 (moderate). P3's interpretation is broader than the test, and Table 1 states it more strongly than Sec. 6 does.

- **The "agreement" reading is a catch-all.** It includes "because it assumes one intended answer" and "because the prompt tells it to use the reference" (Sec. 1). A judge with a uniqueness prior that sees a trusted reference differing from its own belief is *rationally* expected to lower its score, even if it could verify. P3 therefore distinguishes "cannot verify" from "a set of things that includes rational updating under a wrong uniqueness prior"; it does not isolate reward-for-matching.
- **Blind acceptance is a weak proxy for verification.** Opus 5 gives a blind 10 to 5.1–8.2% of wrong answers (App. L). The open-judge acceptance threshold (≤3% of wrong answers) was chosen post hoc (Fig. 3 caption). The paper says, correctly, that "blind acceptance is a proxy for verification, not a direct test of it".
- **Table 1 nonetheless says "Rules out: Verification failure alone … Verdict: Holds".** App. H shows the swap shrinks as blind AUROC rises (Spearman −0.40), which supports a partial verification-failure component.
- **The model contains an untested term.** Eq. (1)'s γ term (wrong answers containing a\*) appears in the model, but its registered tests were "not scored" or "split" (Table 5, lure rows) and the main text never mentions them.

### W5 (moderate). Several main-text statements do not match the paper's own tables and appendix. Individually minor, together they suggest overreporting to a careful reader.

- **Table 1, P2 verdict: "Holds for all judges but GPT-4.1 on factual questions".** Opus 5 on the replication pool is −0.015 [−0.038, +0.009] (App. L; ledger "not confirmed"). GPT-4.1 on the k-pool under the plotted any-format labels is −0.01 [−0.04, +0.00] (Table 6). The Qwen3-8B thinking judge's referenced-margin prediction was not confirmed (Table 5). Sec. 5's verdict is correctly narrower than Table 1's.
- **Sec. 3: "the same sign for every grading AUROC change of the open judges".** Mistral-7B (an open judge) is +0.01 [−0.05, +0.07] on boxed replies (Table 6; App. F says the fall is "removed").
- **Sec. 3 reports the confirmed part of the label audit (91% agreement on unboxed replies) but not the falsified part.** Opus 5 confirms only 86.2% of the replies the any-format rule credits, against a registered bound of ≥90% (App. F). This matters because the P2 ranges in Sec. 5 use any-format labels and roughly halve on boxed replies.
- **Sec. 7: "0% to 3% … admit several, a lower bound … so their own leaderboards move by a few points at most".** A *lower* bound on prevalence cannot support an *at most* on leaderboard movement. Two further problems:
  - "Lower bound" is itself too strong. Adjudication errors can go either way, and only the post-cap fallback is one-directional.
  - BrowseComp has 108 of 200 items "unclear", and HLE reaches 15% by either annotator (Table 3).
- **Sec. 8: "admitting at most 3 more of 56 wrong answers".** This recasts a **falsified** registered 3-*point* bound, which failed for BrowseComp/HLE with GPT-4.1 (+3.6) and o3-mini (+5.4), as a 3-*answer* count that reads as a pass.
- **Sec. 8: "cut the factual rise in false rejections for Sonnet 5 by half or more".** The sentence cuts it 35.6→18.1, a 49% reduction.
- **Sec. 8: "200 HLE questions, whose answers are unique".** These are the audit's questions: 6 labeled several, 53 unclear (Table 3).
- **Sec. 7: "0.5 to 6 points when they reason first".** Two of the six intervals include zero (GPT-4.1 verify-first [−3.0, +0.0] and solve-first [−2.0, +1.2]; Table 17). In substance the shortfall disappears for GPT-4.1 with reasoning prompts, which the reader should know.
- **Sec. 7: "Removing the match clause … recovers 35 points … and 53".** The text omits that this still leaves 31 and 13 points and that the registered 10-point bound failed for both (App. O).
- **Fig. 5 mixes scorers without saying so.** The Qwen2.5-7B bars (+5.3/−5.4) use the exact scorer (`make_figures.py`: `q7rot = … ["escore"]`), while phi-4 and Sonnet 5 use the original scorer with rubric a (their bars equal Table 8, rubric a). Table 8 is original-scorer only (Qwen2.5-7B a: +4.97/−5.04). Sec. 4's "3.0 to 5.3 … 2.7 to 5.4" inherits the mix. Rubric b gives +6.34/−6.58, which is outside the abstract's "about 3 to 5".
- **App. Q: blind-then-reveal "does not keep grading AUROC within 0.03 of blind judging, except for Qwen2.5-14B".** As printed, Table 23 gives Qwen2.5-14B −0.17 + 0.12 = −0.05 against blind, and every open judge is −0.05 to −0.25. The exception is not supported by the table.
- **App. L: "5% to 57%" of blind-accepted differing answers rejected on constructed pools.** Fig. 3 shows 8% to 57% for open judges; say whether the range is per pool or pooled.
- **Abstract: "Across eleven LLM judges".** The paper uses at least 15 judge models (4 core open, Sonnet 5, Opus 5, GPT-4.1, Haiku 4.5, o3-mini, Qwen3-8B/14B, Mistral-7B, Ministral-8B, Qwen2.5-1.5B/3B). The count cannot be reconstructed.

### W6 (moderate). The "how to fix it" recipe is scoped more broadly than its evidence.

- **The evidence base is narrow.** The correctness-prompt advice rests on two API judges, one factual dataset (149 questions, 40-task subsample), and one hard benchmark with 7 label-correct answers.
- **The recipe's specific advice is the riskiest option measured.** It says "let it solve the question first". Solve-first was the prompt that admitted the most wrong answers on HLE for GPT-4.1 (25.9%), and "if the judge can answer the questions" has no operational test beyond the recipe's audit step.
- **The full-list fix assumes complete lists, and the paper's own data show lists are often incomplete.** MACE's shipped lists missed 30.8–43.5% of valid answers in the three excluded entity domains (App. E). "Whether it makes judges reject correct answers it omits is untested" is stated, but the recipe does not warn about it.
- **Family confound on HLE.** GPT-4.1 grades GPT-4.1-mini's answers and Sonnet 5 grades Haiku 4.5's (App. P), so the GPT-4.1 versus Sonnet 5 gap in overruling the reference could partly be family preference. The table does not split by answering model.
- **The max rule is post hoc but unmarked in Sec. 8.** It appears in "What did not help" without †.

### W7 (moderate). Labels, prevalence, and registration rest on LLMs and author-controlled timestamps.

- **No labels are human-validated.** This covers the prevalence audit (κ ≤ 0.35, adjudicator hit a spending cap, 135 disagreements defaulted), the any-format audit, and HLE labels from an o3-mini judge that is "told to match".
- **Claude plays several roles.** Claude models are judges, answerers (Sonnet 5 grades its own answers in Table 12), label auditors, prevalence annotators, and candidate generators for MathConstraint.
- **Most registrations are git commits.** Their timestamps are author-controlled, and the verdict rule was adopted after most outcomes were known. It counts "a registered point prediction holds" as *confirmed* without an interval. At least one confirmed prediction has an effect "not distinguishable from zero" (App. L, full-credit sentence on the replication pool).
- **The ledger (304 predictions) has no multiplicity discussion.**

### W8 (minor). Clarity for a first-time reader.

- **Abstract.** It is dense: the parenthetical list of three readings, "under-credit correct answers by 30 to 67 points" (units and base unclear), "closes it for LLM graders" (General-Reasoner's verifier is also an LLM), and an uncountable "eleven".
- **Table 1.** It sits on page 3, before "labeling", "blind acceptance", "correctness prompts", and "second blind call" are defined. The Consequence row ("under-credit multi-answer questions heavily") gives no number, and the verdicts are broader than the sections (W5).
- **Fig. 1.** It is effective, but it is an arithmetic toy selected for a large clean swap (6.4 points; App. A). The Scope paragraph opens with "The failure is not about math". The caption should say the example was selected; a MACE factual example would align the hook with the practical claim.
- **Appendix jargon.** "Round 19/25/26/27", "inflation", "anchoring margin", and "rotation" are ledger terms. "Round" is never defined, and two different "34"s (prompts and papers) appear in App. B.
- **Typo (App. B).** "DeepSeek-R1's rates an answer correct".
- **Unclear phrasing (App. P).** "342 of the 460 Sonnet 5 calls made at that limit".
- **Figures 2 and 4.** They are information-dense (17 rows with n/a cells; two x-scales). Acceptable for an appendix-heavy paper, but hard at first read.

### W9 (minor). Novelty relative to known single-reference problems.

Under-crediting of correct answers missing from a gold list is well known in QA evaluation (AmbigQA, Si et al. 2021, Bulian et al. 2022, Kamalloo et al. 2023), and the related-work section acknowledges it. The paper's distinctive contributions are:

- showing that LLM judges keep the bias when the list is complete and the judge can verify (P3);
- the byte-identical swap design;
- the grader and fix measurements.

The introduction should say this directly, so that reviewers do not file it under "exact-match problem, again".

## 4. What a skeptical reviewer will seize on in the appendix (checklist)

1. **Training runs (DPO).** The registered "reference arm copies the reference more" prediction was falsified, held-out accuracy fell in all arms including controls, and the result is only in the ethics statement and extended appendix (Table 5, "Training, runs 1–3").
2. **Retroactive verdict rule** that counts point predictions as confirmed. App. L has a "confirmed" prediction whose effect is indistinguishable from zero.
3. **Falsified label audit** (86.2% versus ≥90%), not mentioned in Sec. 3.
4. **Prevalence audit weaknesses.** BrowseComp has 108/200 unclear, κ is 0.00–0.35, the adjudicator ran out of budget, and no humans checked labels. The main text still calls the rates "a lower bound".
5. **MACE domain selection.** Three of five domains were excluded for list incompleteness (31–44%): both data curation and evidence against the full-list fix's premise.
6. **Fig. 5 scorer mix** and the **Table 23 / "except for Qwen2.5-14B"** inconsistency.
7. **Surface-form dependence.** The effect "mostly vanishes" for expression and masked references (Table 10), and the thinking judge's swap is null (Table 9). This suggests surface matching and limits relevance to math RL, where references are often expressions.
8. **Frontier CLI harness.** One check was excluded because the judge may have seen repository metadata naming the hypothesis. App. H's Sonnet three-arm design also ran through the CLI. Confirm that no main-text number relies on CLI calls.
9. **HLE experiment details.** There are 7 label-correct answers, heavy truncation at 1,024 tokens (161/800 GPT-4.1 calls; 342/460 Sonnet calls) repaired by amendment, a 10-reply reading behind "most … went to a different final answer", and the same-family grader/answerer pairing.
10. **End-to-end MACE selection.** All three predictions failed for both judges (App. H), and five MathConstraint selection attempts include three "falsified or not evaluable for diagnosed design reasons" (App. R).
11. **Dropped or truncated replies.** Opus 5's 11 unscored replies, cut off "while it reasoned about whether a differing answer was acceptable", are dropped (Table 12). 12 General-Reasoner replies at 512 tokens count as incorrect.
12. **Survey sampling frame** is unstated for the benchmarks, libraries, and RL rows, and research papers were selected on the outcome (Table 2 caption).

## 5. Questions for the authors

1. **Canonical reference.** What happens to the benchmark-grader gap (Table 14) when the reference is the answer most often produced by the answering models, or the first-listed or most canonical list entry, instead of a random draw? This is the single most important number for the practical claim.
2. **Swap under a neutral prompt.** Can you run the swap test (P1) on the MACE benchmark answers under the direct yes/no prompt, which contains no instruction to compare? Currently P1 has only been shown under compare-instructing prompts.
3. **Reference heading.** In the direct yes/no and chain-of-thought conditions, how is the reference labeled in the user message ("Reference answer (trusted)", "[correct_answer]", something else)? If "trusted" is present, does removing it change the 13–18% credit loss?
4. **HLE family confound.** In App. P, what are GPT-4.1's and Sonnet 5's false-acceptance rates split by answering model (GPT-4.1-mini versus Haiku 4.5)?
5. **Confirmation criteria.** How many of the 202 + 11 "confirmed" predictions were confirmed by a point prediction without an interval that excludes zero?
6. **Table 23.** Please reconcile the Qwen2.5-14B blind-then-reveal claim with the table (−0.17 + 0.12 = −0.05 against blind).
7. **Human validation.** Did any human check (i) a sample of MACE differing-correct and wrong labels, (ii) the prevalence labels, or (iii) the HLE "wrong" labels that GPT-4.1 credited? A 100-item human check of each would substantially raise confidence.
8. **RL transfer.** What types of WebInstruct-verified items were labeled "several", and are their references expressions? App. J suggests the effect is much smaller for expression references.
9. **Which judges count as the "eleven LLM judges"?**
10. **Surface form versus meaning.** Does the swap survive when the reference is a correct *alias* of the candidate's answer (e.g., "Nile" versus "Nile River")? That is, is the bonus semantic or lexical?

## 6. Score

**6: marginally above the acceptance threshold. Confidence: 4** (confident; I checked the appendix numbers against the main text but did not rerun analyses).

The core phenomenon is real, cleanly isolated, replicated across judges, and practically relevant for anyone reusing single-reference graders on open-answer data. The fix measurements are useful, and the transparency is exemplary. Three things hold the score at 6: the headline magnitude and the RL claim are framed more broadly than the design supports (W1, W2); the instruction-following explanation is not separated in the main text (W3); and a series of main-text sentences outrun their own appendix tables (W5). All are fixable without new experiments except Q1 and Q2.

## 7. What would move the score up

- **To 8:**
  1. A canonical-reference condition for the benchmark-grader study (Q1), or the abstract and intro rescoped to "reference drawn at random", leading with the share of differing correct answers credited.
  2. The swap and credit-loss results under a no-compare prompt in the main text, as a three-row decomposition (explicit match instruction / neutral correctness question / explicit counter-instruction) (W3, Q2).
  3. The DPO training result moved into the Limitations section, and the Conclusion's RL sentence narrowed (W2).
  4. All W5 inconsistencies fixed (text below).
  5. A small human validation of labels (Q7).
- **To 6 with higher confidence (no new experiments):** the text fixes in Section 8 of this review.

## 8. Requested text fixes (exact replacement text)

**T1. Abstract, magnitude (W1).**
Replace:
> Where the premise fails, the consequence is large: on factual questions with several answers, benchmark graders run verbatim and open RL-reward verifiers under-credit correct answers by 30 to 67 points.

With:
> Where the premise fails, the consequence is large: on 149 factual questions with several answers and a reference drawn at random from each answer list, benchmark graders run verbatim and open RL-reward verifiers credit 0\% to 53\% of the correct answers that differ from the reference, leaving accuracy 30 to 67 points below the answer lists. The benchmarks those graders ship with rarely contain such questions; the risk is reusing the graders where answers are open.

**T2. Abstract, fix and count (W5, W8).**
Replace:
> and giving the grader every correct answer closes it for LLM graders.
> Across eleven LLM judges, two verifiers, and a ledger of every registered prediction,

With:
> and giving the grader every correct answer closes it for five benchmark graders and one of two open verifiers.
> Across the LLM judges and verifiers we test, and a ledger of every registered prediction,

(If the count is kept, list the eleven judges in App. A.)

**T3. Abstract, swap range (W5, Fig. 5).**
Replace "by about 3 to 5 points out of 10" with "by about 3 to 6 points out of 10".

**T4. Introduction, "What we find" (W3).**
Replace:
> including under prompts that ask only whether an answer is correct.

With:
> including, to a smaller degree, under prompts that ask whether an answer is correct rather than whether it matches.

**T5. Introduction, fix sentence (W5).**
Replace:
> Giving the grader every correct answer removes it for LLM graders;

With:
> Giving the grader every correct answer removes it for five benchmark graders and one of the two open verifiers we test;

**T6. Table 1 (W4, W5, W8).**
- P2 Verdict: replace "Holds for all judges but GPT-4.1 on factual questions" with "Holds for the four open judges, Sonnet 5, and Opus 5; intervals reach zero for GPT-4.1 on factual questions, Opus 5 on the replication pool, and a thinking judge on arithmetic".
- P3 Key evidence: replace "also under correctness prompts; a second blind call does not do this" with "also, with smaller losses, under correctness prompts; a second blind call by the API judges does not do this".
- P3 Verdict: replace "Holds" with "Holds for all judges with a usable acceptance test; blind acceptance is a proxy for verification".
- Consequence, Key evidence: replace "Shipped benchmark graders and RL verifiers under-credit multi-answer questions heavily" with "With a randomly drawn reference, shipped benchmark graders and two RL verifiers credit 0–53\% of correct answers that differ from it".
- Fix, Key evidence: replace "A full answer list closes the gap for LLM graders;" with "A full answer list closes the gap for five benchmark graders and CompassVerifier-3B;".
- Fix, Verdict: replace "Holds for LLM graders, not for one small verifier" with "Holds for six of seven graders; not for General-Reasoner's 1.5B verifier".

**T7. Sec. 3, Candidates, judges, and prompts (W3).**
Replace:
> the effect also appears under the verbatim MT-Bench template, under prompts that ask only whether an answer is correct, and for answers the judge accepted blind

With:
> the effect also appears under the verbatim MT-Bench template (which also asks for a comparison), under a direct and a chain-of-thought prompt that ask whether the response is correct without any instruction to compare, where it is smaller, and for answers the judge accepted blind

**T8. Sec. 3, Reading answers (W5).**
Replace:
> A registered audit by Claude Opus~5 agrees with these labels on 91\% of unboxed replies (\cref{app:grid}). Registered labels, model-read labels, and boxed replies alone give the same sign for every grading AUROC change of the open judges and GPT-4.1; only the size changes.

With:
> A registered audit by Claude Opus~5 agrees with these labels on 91\% of unboxed replies but confirms only 86\% of the replies they credit (registered bound 90\%; falsified), so we also report boxed replies alone (\cref{app:grid}). Registered labels, model-read labels, and boxed replies alone give the same sign for every grading AUROC change of the four core open judges and GPT-4.1, with falls roughly halved on boxed replies; Mistral-7B, which failed our score-resolution screen, shows no fall on boxed replies.

**T9. Sec. 4 (Fig. 5 scorer mix).**
Replace:
> Text the reference moves onto gains 3.0 to 5.3 points under Qwen2.5-7B, phi-4, and Sonnet~5, and text it moves off loses 2.7 to 5.4,

With:
> Under rubric~$a$, text the reference moves onto gains 3.0 to 5.3 points under Qwen2.5-7B (exact scorer), phi-4, and Sonnet~5, and text it moves off loses 2.7 to 5.4 (up to $+6.3$ and $-6.6$ under rubric~$b$),

Fig. 5 caption: append "Qwen2.5-7B bars use the exact scorer (\cref{app:estimator}); phi-4 and Sonnet~5 use the original scorer, rubric~$a$ (\cref{tab:rotation})."

**T10. Sec. 6 (W3, W5).**
Replace:
> The same pattern holds under prompts that ask only whether an answer is correct: across four such prompts, GPT-4.1 and Sonnet~5 withdraw credit from 1\% to 22\% of the differing correct answers they accepted blind, and from at most 0.7\% of matching ones\reana{} (\cref{app:r27}).

With:
> A weaker form of the pattern holds under four prompts that ask whether an answer is correct, two of which (verify first, solve first) also tell the judge to use the reference: GPT-4.1 and Sonnet~5 withdraw credit from 1\% to 22\% of the differing correct answers they accepted blind, and from at most 0.7\% of matching ones; the difference excludes zero in seven of eight cells, and these prompts have no second-blind-call noise floor\reana{} (\cref{app:r27}).

**T11. Sec. 7, Where it matters, prevalence (W5).**
Replace:
> 0\% to 3\% of sampled SimpleQA, BrowseComp, and HLE questions admit several, a lower bound from LLM annotators who agreed poorly (\cref{app:prevalence}), so their own leaderboards move by a few points at most.

With:
> 0\% to 3\% of sampled SimpleQA, BrowseComp, and HLE questions admit several by adjudicated LLM labels ($\kappa \le 0.35$; up to 15\% on HLE by either annotator, and 108 of 200 BrowseComp items unclear; \cref{app:prevalence}), so the effect on their own leaderboards is probably small, although these labels do not bound it.

**T12. Sec. 7, RL estimate (W1, W2).**
Replace:
> roughly 4\% to 12\% of that set's correct rollouts would go unrewarded, an estimate rather than a measurement.\ph{}

With:
> roughly 4\% to 12\% of that set's correct rollouts would go unrewarded. This is an unvalidated estimate of reward error, not of training harm: its upper end uses the union of two low-agreement annotators, our references were drawn at random rather than chosen as the most common answer, and our exploratory preference-training runs did not show a policy learning to copy the reference (extended appendix).\ph{}

**T13. Sec. 7, What sets the size (W5).**
Replace:
> and 0.5 to 6 points when they reason first (\cref{app:r25,app:r26}).
> Removing the match clause from the HLE judge and stating that a different correct answer is correct recovers 35 points for GPT-4.1 and 53 for Sonnet~5; the edited judge still calls the reference ``precise and unambiguous''.

With:
> and 0.5 to 6 points when they reason first, with intervals that include zero for GPT-4.1's verify-first and solve-first prompts (\cref{app:r25,app:r26}).
> Removing the match clause from the HLE judge and stating that a different correct answer is correct recovers 35 points for GPT-4.1 and 53 for Sonnet~5 but leaves them 31 and 13 points short (our registered 10-point bound failed for both); the edited judge still calls the reference ``precise and unambiguous''.

**T14. Sec. 8, full answer list (W5).**
Replace:
> while admitting at most 3 more of 56 wrong answers,

With:
> while crediting at most 3 more of 56 wrong answers (up to 5.4 points; our registered 3-point bound failed for two graders, and some of these answers are near-aliases of listed ones),

After "A list is also closed; whether it makes judges reject correct answers it omits is untested." add:
> Lists are often incomplete: in three \textsc{MACE} domains we excluded, the shipped lists missed 31\% to 44\% of valid answers (\cref{app:mace}).

**T15. Sec. 8, When the answers cannot be listed (W5).**
Replace:
> each cut the factual rise in false rejections for Sonnet~5 by half or more, and together left no measurable rise

With:
> each cut the factual rise in false rejections for Sonnet~5 by about half (from 36 points to 18 with the sentence and 15 with thinking), and together left no measurable rise on 40 tasks

**T16. Sec. 8, Questions beyond the judge (W5, W6).**
Replace:
> We sampled 200 HLE questions, whose answers are unique, and graded two models' answers to them, almost all wrong.

With:
> We took the 200 HLE questions of our prevalence audit (6 labeled as having several answers, 53 unclear) and graded two models' answers to them, almost all wrong.

Replace:
> Those labels come from a judge told to match, but in a sample we read, most of these credits went to a different final answer.\ph{}

With:
> Those labels come from a judge told to match; restricting to answers with an explicit answer line leaves 15\% and 23\% for GPT-4.1, and in a post hoc reading of 10 of its 97 solve-first credits, most went to a different final answer.\ph{} GPT-4.1 grades answers from GPT-4.1-mini here, so family preference may contribute.

**T17. Sec. 8, What did not help (W5, W6).**
Replace:
> left grading below blind for most open judges; keeping the higher of the blind and referenced scores protects grading

With:
> left grading below blind for every open judge we tested; keeping the higher of the blind and referenced scores (chosen post hoc)\ph{} protects grading

**T18. Sec. 8, recipe (W6).**
Replace the heading "A recipe." with:
> A recipe (from two API judges, one factual dataset, and one hard benchmark).

Replace the third bullet with:
> \item \textbf{No list and no checker:} if the judge can answer the questions, do not tell it to match; ask whether the response is correct. Letting the judge solve first gave the smallest grading loss on our factual questions but admitted the most wrong answers on HLE for GPT-4.1, so first check on known wrong answers that the judge does not overrule the reference.

**T19. Limitations, new bullet (W1, W2).**
Add:
> \item \textbf{Consequences.} References were drawn at random from answer lists, which likely raises the share of correct answers that differ from them relative to curated references. Our exploratory preference-training runs were inconclusive: the registered prediction that a policy trained with a reference-guided judge would copy the reference was falsified, and held-out accuracy fell in every arm, including controls (extended appendix). Harm to RL training is therefore not demonstrated.

In "Mechanism and registration", replace "and the verdict rule was applied retroactively" with "and the verdict rule, which counts a registered point prediction that holds as confirmed without an interval, was applied retroactively".

**T20. Conclusion (W2, W5).**
Replace:
> When a question has several correct answers, LLM judges favor the one they are shown, even for answers they accept without it.
> Graders shipped with benchmarks and used for RL rewards inherit this failure wherever answers are open, in large part because they are told to match.

With:
> When a question has several correct answers, the LLM judges we tested favor the one they are shown, even for answers they accept without it.
> The benchmark graders and RL-reward verifiers we tested inherit this failure when run on such questions, in large part because they are told to match; whether it harms RL training remains open.

**T21. Sec. 2, Eq. (1) text (W4).**
After "or wrong answers containing $a^\star$ to share the bonus ($\gamma > 0$)" insert:
> (our registered lure tests of $\gamma$ were not scored or split; \cref{app:ledger})

**T22. Fig. 1 caption (W8).**
Replace:
> \textbf{(b)}~Qwen2.5-7B scores the same text without a reference and with each correct answer as the reference. The effect over the whole pool is in \cref{sec:p1}.

With:
> \textbf{(b)}~Qwen2.5-7B scores the same text without a reference and with each correct answer as the reference. The example was selected for a large, clean swap (6.4 points); over the whole pool the swap averages about 5 points for this judge (\cref{sec:p1}).

**T23. App. Q, Blind-then-reveal (W5).**
Replace:
> it does not keep grading AUROC within 0.03 of blind judging, except for Qwen2.5-14B (Reveal $-$ ref.\ column).\ph{}

With (if Table 23 is correct as printed):
> it does not keep grading AUROC within 0.03 of blind judging for any open judge in \cref{tab:protocols} (Reference plus Reveal $-$ ref.\ is $-0.05$ to $-0.25$).\ph{}

**T24. App. L, full-credit sentence (W7).**
Replace:
> All four predictions were confirmed:

With:
> All four predictions were confirmed, two as point predictions:

(Adjust the count to the registration.) After "on the replication pool neither change is distinguishable from zero" keep the † and add "so the replication-pool confirmation rests on the point estimate alone".

**T25. App. L, acceptance threshold range (W5).**
Replace "On the constructed pools, 5\% to 57\% of those that differ from the reference score 3 or below" with "On the constructed pools, 5\% to 57\% per pool (8\% to 57\% pooled, as in \cref{fig:reasoning}) of those that differ from the reference score 3 or below" (verify against the analysis output).

**T26. App. B (W8).**
Replace "DeepSeek-R1's rates an answer correct" with "DeepSeek-R1's reward prompt rates an answer correct".
Replace "We could read 34 judge prompts in full." with "We could read 34 judge prompts in full (a different set from the 34 research papers in \cref{tab:survey})."

**T27. App. D (W8).**
After "Counting each registered prediction once, and from round 19 on once per judge or grader configuration," insert the sentence: "(A round is one dated batch of registered experiments; the registration documents in the supplement are numbered by round.)"

**T28. App. P, caveat (i) (W8).**
Replace "342 of the 460 Sonnet~5 calls made at that limit" with "342 of the 460 Sonnet~5 solve-first calls run at that limit before the amendment".

---

## 9. Previous weaknesses: resolved / partly / not

Written after the independent review above. The reference is `D-iclr-v2/reviews/v2_final_ac_review.md` (score 8, confidence 4). Page and section references are to the v3 snapshot.

| v2 item | Topic | Status | Evidence in v3 | What remains |
|---|---|---|---|---|
| **W1** | Instruction-ladder attribution overstated. Conclusion called the edit a "deletion"; 0.5–17 range omitted the edited HLE judge; SimpleQA grader and o3-mini not decomposed. | **Partly** | Abstract hedged to "Much of this gap comes from telling the grader to match" (p. 1). Conclusion now "in large part because they are told to match", with no "deleting" (p. 9). §7 describes both parts of the edit and gives blind shortfalls "(5 and 2 points blind)" (p. 7, l. 327–335). | The E1' decomposition (SimpleQA edit, o3-mini with the edit) was not run; nothing in App. M–O covers it. §7 dropped "leaving 31 and 13" (see T13). The ladder still mixes instruction and reasoning for GPT-4.1 (Table 17 intervals include zero). |
| **W2** | Importance rests on a built pool; reuse citations concerned method multiplicity; RL case not quantified; prevalence caveats incomplete. | **Partly** | §7 "Where it matters" now gives the 4–12% RL estimate, marked † (p. 6, l. 320–322). It concedes "for proofs and code … our own effects are small", and the CodeJudge citation is gone (p. 6–7). | E2' (in-distribution WebInstruct measurement) not run. The estimate does not state its random-reference and union-annotator assumptions (my W1, W2). BrowseComp's 108/200 unclear and κ values are not in the main text. New contradiction: "a lower bound … at most" (l. 316–318; T11). The DPO training null is still only in the ethics statement. |
| **W3** | "Give every correct answer" stated as universal despite General-Reasoner. | **Largely resolved** | §8: "It does not fix every grader: General-Reasoner's 1.5B verifier credits 67% … but also 30% of wrong ones" (p. 7, l. 348–350). Table 1 Fix verdict: "not for one small verifier". Recipe bullet 1: "one of our two did not" (p. 7). | Abstract and intro still say "closes/removes it for LLM graders" (l. 026, l. 092), which is ambiguous because General-Reasoner is an LLM (T2, T5). The leave-one-out list (E3) was not run; the closed-list caveat is in §8 but not the recipe (T14). |
| **W4** | No-list advice validated only on questions judges can answer. | **Resolved in substance** | E4' run: 200 HLE questions, direct and solve-first, GPT-4.1 and Sonnet 5 (App. P, Table 22; §8 "Questions beyond the judge", p. 7). Recipe bullet 3 adds a check on known wrong answers (p. 8). Table 1 Fix row mentions hard questions. | The recipe still says "let it solve the question first", the option with the most false acceptances for GPT-4.1 on HLE (25.9%). "Whose answers are unique" overstates the pool (T16). Same-family grader/answerer pairing (Q4). |
| **W5** | Two arguments, thin bridge; Eq. 1 has no instruction term; P3 untested for correctness prompts (E5a/E5b). | **Largely resolved** | Eq. 1 text ends "Section 7 suggests that the grader's instruction scales the agreement term λ" (p. 3, l. 140). §7 closes with "the instruction appears to scale the agreement term without removing it" (p. 7). E5a done: App. P, Table 21, reported in §6 (p. 4, l. 210–212) and Table 1. | E5b (second blind call under correctness prompts) not run; App. P says "no noise floor", but §6 does not. §6 calls verify-first and solve-first prompts that "ask only whether an answer is correct", although both instruct use of the reference (my W3; T7, T10). |
| **W6** | Cognitive load: abstract enumeration, unsplit intro paragraph, long Table 1 caption, mixed §8 paragraph. | **Resolved** | Abstract enumeration removed (p. 1). Intro split into "Three readings", "What we find", "Scope" (p. 2). Table 1 caption is one sentence (p. 3). §8 split into five paragraphs plus the recipe (p. 7–8). | Residual density: undefined terms in Table 1, "eleven" count, ledger jargon ("round") (my W8). |
| **W7.1** | "Eleven judges" stale | **Partly** | Now "eleven LLM judges, two verifiers" (l. 027). | The eleven still cannot be reconstructed from the paper (T2). |
| **W7.2** | Table 1 Consequence verdict "nine configurations" | **Resolved** | Verdict now "Large where it applies; such questions are rare on those benchmarks" (p. 3). | — |
| **W7.3** | "False rejections do not rise" (they fall for Opus 5 and GPT-4.1) | **Resolved** | Sentence removed; values in Table 16 (p. 31). | — |
| **W7.4** | Scope of "registered 5-point test" | **Partly** | Now "by our registered test, not Sonnet 5" (p. 7, l. 333–334). | The test is still not named in the main text (App. O). |
| **W7.5** | Interim count of General-Reasoner output not disclosed | **Not resolved** | App. O mentions only "after three low-memory stops the runs continued in chunks (Amendment 3)" (p. 33). | Add the interim-inspection note. |
| **W7.6–7.7** | Setup omitted Haiku 4.5 and verifiers; AI statement lists graders | **Resolved** | §3: "Haiku 4.5, o3-mini, and two open RL-reward verifiers also grade benchmark answers" (p. 3). AI statement: "served as the judges and verifiers under study" (p. 9). | — |
| **W7.8** | Figure 2 placed before §4 text | **Resolved** | Figure 2 is on p. 5, after §5 begins on p. 4. | — |
| **W8** | Related work (VerifyBench, JudgeBench, answer matching, QAMPARI, PEDANTS); human grader baseline | **Related work resolved; human baseline not** | §9 cites Yan et al. 2026 (VerifyBench), Tan et al. 2025 (JudgeBench), Chandak et al. 2025, Amouyal et al. 2022, Li et al. 2024 (p. 8). | No human check of any label or of HLE-instruction grading; the AI use statement confirms "no label was checked by human annotators" (p. 9; my W7). |
| **v2 §8 figures** | Figure 4 double scale; empty quadrant; Figure 1 arithmetic-only | **Partly** | Figure 4 lower block has its own labeled axis, and the caption says "on a different scale" (p. 6). | Figure 1 is still an arithmetic example and still lacks a selection disclosure in the caption (T22). Figure 5 mixes scorers without disclosure; this was already true in v2 (its spot check #5 reads r4_rotation +5.25/−5.41). |
| **v2 §6 overclaims** | "restores grading"; P3 "for all six judges"; RL verifier scope | **Resolved** | "brings grading AUROC to blind or above for three judges" (l. 349). "P3 holds for all judges with a usable acceptance test" (l. 214). "credit 6% and 0% of those answers" (l. 314). | Table 1's P2 verdict has become broader than §5's ("all judges but GPT-4.1"; T6). |

**Net.** Of v2's eight weaknesses, one is resolved (W6) and one resolved in substance (W4). Three are largely resolved: W3, W5, and W8's related-work half (W8's human baseline is not done). Two are partly resolved (W1, W2). W7's small items are mostly fixed, but W7.5 (the interim-count note) is still open. The authors ran E4' (hard HLE questions) and E5a (P3 under correctness prompts). They did not run E1', E2', E3, or E5b.

**Why this review scores 6 against v2's 8.**
- **Issues v3 introduced while absorbing v2's requests.** The prevalence sentence became self-contradictory ("lower bound … at most"). The HLE pool is called "unique". Verify-first and solve-first are described as prompts that "ask only whether an answer is correct". Table 1's P2 verdict is broader than §5's. The Table 23 "except for Qwen2.5-14B" claim is not supported by the table.
- **Issues v2 did not raise.** The random-reference origin of the 30–67 magnitude. The DPO training null being absent from the main text. The compare-instructing wording of the headline rubrics. The falsified label audit being omitted from §3. The undisclosed scorer mix in Figure 5.
- **None needs new data.** Except Q1 (canonical reference) and Q2 (swap under a neutral prompt), they are text fixes. With T1–T28 applied, I would expect this version to sit at 6–8 depending on the reviewer pool, and at 8 with Q1 and Q2 answered.
