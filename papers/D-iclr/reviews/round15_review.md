# Round 15 Area Chair review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

Reviewer role: harsh AC, ICLR 2027 main track. I read the full PDF (main text pp. 1-9, references, and appendix A-P, pp. 13-41) and rendered every main-text page and the appendix figure pages. All line numbers below are PDF line numbers.

---

## 1. Summary of the claims

The question is whether an LLM judge given a reference answer treats it as an answer key (every correct answer scores the same) when a question has several correct answers. The paper sets out three readings: answer key, verification failure, and agreement. It tests three predictions.

- **P1.** Swapping the reference between two correct answers moves the score of byte-identical text by 2.7-5.4 points out of 10 (Qwen2.5-7B, phi-4, Sonnet 5; Figure 1c).
- **P2.** Correct answers that differ from the reference are rejected more often and separated worse from wrong answers. Grading AUROC falls 0.17-0.27 for four open judges on constructed pools (0.07-0.14 boxed-only), 0.06-0.08 on MACE, and 0.04-0.15 for Sonnet 5. With a unique answer the reference still helps (about +30 pp best-of-64 on MATH-500).
- **P3.** The effect persists on answers the judge already accepts blind, so it is not just verification failure. Sonnet 5 drops 19% of the factual answers it scored 10 blind to 3 or below once shown a different correct answer.

A thinking mode removes the effect on arithmetic and roughly halves it on factual questions. Selection harm shows up mainly where no correct candidate matches the reference. On natural MACE data, selection accuracy does not fall.

The core claim is easy to extract; Figure 1 and the title do their job. What is hard to extract is the paper's **position on moderators and on what practitioners should do**. Those claims are spread over "score-only", "explains first", and "thinking on", over three labelings and two scorers, and over two Sonnet interfaces. The reader has to rebuild the taxonomy from Section 3, Figure 3, and Table 1, and these sources do not quite agree (issue M1).

## 2. Score

**6 / 10 (marginally above the acceptance threshold). Confidence: 4/5.**

**Biggest reason.** The central P1 result is clean, pre-specified, replicated across judges and rubric wordings, and shown with an excellent Figure 1, and the reporting is unusually candid. But several main-text sentences are contradicted by the paper's own appendix or data. These include:
- the moderator claim ("at most halves")
- the mechanism claim ("literal answer string")
- the labeling-robustness claim ("same direction for every grading result")
- the scorer claim ("exact scorer except in Table 2")
- the selection claim ("no candidate matches")
- the reason given for dropping the registered primary endpoint ("inflation follows from P1")

For a paper whose selling point is reliability, each of these is a credibility hit a reviewer will find within an hour. Separately, the abstract and Sections 3-7 carry roughly a dozen coined terms and several numeric ranges per paragraph. Cognitive load is well above the Emergent-Mirage bar. Everything below is fixable by rewriting and re-analysing existing data.

---

## 3. Ranked issues

### MUST FIX (would mislead a reader or be caught by a reviewer as an internal contradiction)

**M1. The moderator story is inconsistent, and "at most halves" is contradicted by the paper's own numbers.**

*Location:* Abstract l.27-28 ("A thinking mode removes the effect on arithmetic and at most halves it on factual questions"); Figure 3 title l.343 ("on factual questions it at most halves it"); Conclusion l.444-445 (same). Compare Table 1 l.134-135 and Section 6 l.305 ("roughly halves").

*Problem, part (a).* "At most halves" means a reduction of no more than 50%. Table 50 (l.2180-2181) shows Qwen3-14B's factual false rejections going from +41.6 to +17.8, a 57% reduction, and its factual margin from +7.07 to +3.13, a 56% reduction. Qwen3-8B's false rejections go from +44.3 to +21.6, a 51% reduction. So thinking *more* than halves it for Qwen3.

*Problem, part (b).* The moderator is described three incompatible ways:
- Intro l.91-92: "all three hold for judges that output only a score".
- Table 1 P1 verdict: "Holds for score-only judges".
- Section 4 verdict l.259: "P1 holds for every score-only judge we swapped. With a thinking mode it fails on arithmetic".
- Abstract: "a thinking mode removes the effect".

The data (Figure 3a; Table 7; Appendix N l.1955-1958) show three regimes:
- **Score-only:** the effect is always present.
- **Explanation first, no thinking:** present for open judges (Qwen2.5-7B under MT-Bench −3.59; Qwen3-14B thinking-off −1.98; Qwen3-8B thinking-off −0.69), but nearly gone for Sonnet 5 (−0.20).
- **Thinking on:** gone on arithmetic, reduced on factual questions.

P1 therefore holds for more than score-only judges, and for Sonnet 5 on arithmetic *explaining* is enough, so "thinking mode" is not the moderator there.

*Problem, part (c).* In Figure 3b the "thinking off" bar means *explanation first* for Qwen3 but *score only* for Sonnet 5 (caption l.346-347). The same colour stands for different conditions.

*Fix.*
1. Replace "at most halves" with "roughly halves" everywhere (abstract, Figure 3 title, conclusion).
2. Define the three regimes once in Section 3 (l.176-179 already nearly does) and use exactly these words in the abstract, Table 1, and both verdicts.
3. Suggested abstract wording: "Reasoning before scoring removes the effect on arithmetic (for Sonnet 5, a written explanation suffices; open judges need a thinking mode) and roughly halves it on factual questions for Qwen3, with no detectable reduction for Sonnet 5."
4. Change the Table 1 P1 verdict to "Holds without a thinking mode; for Sonnet 5 only when it scores without explaining."
5. In Figure 3b, label the Sonnet 5 bar "score only" and use the score-only marker from 3a.
6. Table 1 l.135, "no detectable change for Sonnet 5", is ambiguous because Sonnet's arithmetic swap *did* fall from 2.85 to 0.32. Write "on factual questions, no detectable reduction for Sonnet 5."

**M2. Five main-text statements are contradicted by the appendix or by the paper's own data.**

**(a) "The pull comes from the literal answer string."** (l.252)
- The next sentence says "thirty-one" "leaves phi-4's almost unchanged" (Table 29, l.1667: +3.79 numeral vs +3.68 words).
- Sonnet 5 shows +3.06 numeral vs **+3.14 words** (l.255).
- A spelled-out number is not the literal string "31". What the data show is that the pull needs the answer *stated outright*, not left to compute ("30+1": −94%/−77%; decode steps; masked worked solution).
- *Fix:* "The pull depends on the reference stating its answer outright. Writing 31 as '30+1' cuts the margin by 94% and 77%, masking the final answer of a worked solution removes it, but spelling it out ('thirty-one') leaves it largely intact for phi-4 and Sonnet 5 (a 38% cut for Qwen2.5-7B)."

**(b) "inflation follows from P1".** (l.204-205, the stated reason for not leading with the OSF primary endpoint)
- Appendix I (l.1622-1625): "The margin alone does not predict which tasks inflate". The margin-inflation correlation is +0.29 and +0.06 against noise ceilings of 0.82 and 0.90.
- The registered composition prediction (inflation rises with the number of matching answers) was falsified: inflation is *largest* with none (Table 28).
- Inflation depends on β<1 and on lures (γ), not just on P1.
- *Fix:* "We lead with the swap, rejection, grading, and accuracy measures because they are easier to interpret; inflation is a composite that also depends on how much of its own assessment the referenced judge keeps and on look-alike wrong answers (Appendix I)."

**(c) "…and boxed replies alone give the same direction for every grading result".** (l.191)
- Table 14 (l.1254): Mistral-7B k-pool boxed-only is **+0.01 [−0.05, +0.07]**. Appendix D l.1070 says so explicitly: keeping only boxed replies "removes it for Mistral-7B".
- GPT-4.1 k-pool is −0.01 in every labeling with intervals reaching zero.
- Section 5 l.280-281 quotes Mistral-7B's 0.08 fall without saying that it disappears boxed-only.
- *Fix:* change l.191 to "give the same direction for every grading result of the screened judges and Sonnet 5". At l.281 add: "(Mistral-7B's fall disappears when only boxed replies are scored)".

**(d) "The main text uses the exact scorer except in Table 2."** (l.175-176) This is false in at least four places:
- The masking percentages (94%, 38%; l.252-254) come from Table 29. Appendix O's rescoring list (l.2014-2017) does not include the masking suite, so these are original-scorer values.
- The Ties swap "9.8 … 3.1" (l.249) comes from Table 6, which is original-scorer.
- "2.6 pp for Qwen2.5-14B on the k-pool under the registered labels" (l.379) comes from Table 36, "Original scorer".
- "9 to 11 pp" over the natural mix (l.366) uses Table 2 values (+9.8, +11.3), which are original-scorer; the exact value is +9.0 (Table 49).
- *Fix:* "The main text uses the exact scorer where it exists (all replication, k-pool, MACE, and MATH-500 results for Qwen2.5 and gemma-2); the Ties pool, masking suite, and protocol comparisons use the original scorer, which differs by 0.07-0.17 points per score (Appendix O)." Alternatively, mark original-scorer numbers with a symbol.

**(e) Mistral-7B's score described as "the expected value over the score tokens".** (l.172-173)
- Appendix A l.692-694: "Mistral-7B's tokenizer has no single-token digits, so all of its scores, under either estimator, are the integers parsed from its greedy replies."
- *Fix:* move Mistral-7B out of that clause: "…the open judges Qwen2.5 (1.5B to 14B), phi-4, and gemma-2-9b, whose score is the expected value over the score tokens; Mistral-7B, whose scores are parsed integers; and Claude Sonnet 5 and GPT-4.1 through their APIs."

**M3. "No candidate matches the reference" should say "no *correct* candidate", and the constructed-pool selection claim is overstated.**

*Location:* Abstract l.28-29 ("where no candidate matches the reference"); Intro l.93; Conclusion l.445-446; Figure 2 title l.238 ("it degrades grading everywhere and selection on constructed pools").

*Problem, part (a).* Section 7 l.372 correctly says "no *correct* candidate". The dropped word matters: wrong candidates that contain the reference's answer (look-alikes) are 23.6% and 26.8% of wrong candidates (Table 18). They are exactly the γ mechanism, and they exist on these tasks.

*Problem, part (b).* The split is post hoc and rests on 11 k-pool and 16 replication tasks (Table 49 l.2139-2149). The abstract states it without a mark or a hedge.

*Problem, part (c).* Figure 2's title says selection degrades on constructed pools. Under the any-format labels the figure uses, only **2 of 6** constructed open-judge cells exclude zero (Table 13 l.1229-1239):

| Cell | Change (pp) | 95% CI |
|---|---|---|
| Qwen2.5-7B, k-pool | −30.3 | [−48.5, −12.1] |
| Qwen2.5-7B, replication | −9.3 | [−17.5, −1.0] |
| phi-4, k-pool | −15.2 | [−30.3, +0.0] |
| Qwen2.5-14B, k-pool | −3.0 | [−18.2, +9.1] |
| gemma-2-9b, k-pool | −3.0 | [−12.1, +0.0] |
| phi-4, replication | −3.1 | [−7.2, +1.0] |

Appendix D l.1071-1072 says it directly: "leaves a loss that excludes zero only for Qwen2.5-7B". Section 7 l.368-369 also quotes phi-4's 15.2 pp loss without saying its interval reaches zero. "Grading everywhere" is also too strong: GPT-4.1 k-pool is −0.01 [−0.04, +0.00].

*Fix.*
1. Abstract and conclusion: "…and best-of-64 selection loses accuracy mainly on constructed tasks where no *correct* candidate matches the reference (a post hoc split)."
2. Figure 2 title: "With one correct answer the reference helps; with several, it degrades grading for every screened judge and Sonnet 5, and selection only for some judges on constructed pools."
3. l.368-370: add "(phi-4's interval reaches zero)".
4. l.373-375: give all four judges, not just the two with large losses. Qwen2.5-14B and gemma-2-9b lose 18 and 9 pp without a matching correct candidate, and both intervals reach zero.

**M4. The look-alike (γ>0) explanation uses statistics from the labeling it is meant to explain away.**

*Location:* l.276-278: "Wrong answers that contain the reference's answer are mostly unboxed (73% to 77%), consistent with part of the larger fall coming from the bonus such look-alikes collect (γ > 0)."

*Problem.*
- The 73.3% and 76.9% come from Table 18 (source `tables/round7_numbers.tex`), the look-alike analysis done under the **registered** labels.
- Appendix D l.1078-1079 says of exactly those look-alikes: "most of those were unboxed replies stating a correct value, which the relabelings count as correct."
- The sentence is explaining why the *any-format* fall (0.17-0.27) is larger than the *boxed-only* fall (0.07-0.14). Under any-format labels most of the 73-77% are no longer wrong answers at all, so the statistic cannot support γ>0 under the labels being explained.
- A plainer alternative explanation is not mentioned: dropping unboxed replies selects better-formatted, probably easier replies.

*Fix (no new data needed).* Either (i) recompute the look-alike share and its unboxed fraction under the any-format labels from the stored labelings and quote that, or (ii) cut the sentence and write: "Boxed replies alone give the conservative estimate; we do not separate how much of the difference comes from look-alike wrong answers and how much from which replies use the format."

**M5. The practical recommendation is untested on the paper's own robust harm, even though the test needs no new calls.**

*Location:* Conclusion l.447-451 ("Scoring such answers without the reference as well is a reasonable default … and we did not measure how it grades"); Section 7 l.384 ("We did not measure how any of these protocols grade").

*Problem, part (a).* Section 7's title says grading harm is robust and selection harm conditional. The recommended max rule is then checked only on selection, the conditional harm. Yet max-rule scores are just max(blind, referenced) per candidate, and both score files exist for every open judge on every pool (Table 36 already computes max-rule *accuracy* from them). Max-rule grading AUROC for non-matching correct vs wrong answers is therefore pure re-analysis. The same holds for blind-then-reveal on the k-pool and MACE, where reveal calls exist for all candidates (Tables 40 and 44).

*Problem, part (b).* The conclusion's two costs use different baselines:
- "cost 6.7 pp on unique-answer math" is relative to the *referenced* judge (Table 2: +30.5 → +23.8).
- "2.4 pp for Sonnet 5" is relative to *blind* (Table 26 l.1537: −2.4 [−5.0, −0.5] vs blind, where the reference itself is −2.6).

*Problem, part (c).* Sonnet 5's subsamples "always include a correct answer that matches the reference, so its selection is not shown" (Figure 2 caption l.243-244). By the paper's own Section 7 finding, that is the benign regime, yet the conclusion uses Sonnet's selection as evidence about the protocol.

*Fix.*
1. Add one row to Table 2, or a sentence, giving the change in grading AUROC under the max rule and blind-then-reveal, computed from the existing files. If the max rule restores grading, the recommendation becomes the paper's strongest practical contribution. If it does not, the conclusion must say so.
2. State every cost against the same baseline, e.g. "6.7 pp below the referenced judge on MATH-500; for Sonnet 5 on k-pool subsamples, which always contain a matching correct answer, 2.4 pp below blind."
3. Give the 95% interval for the 6.7 pp paired difference (max rule minus reference on MATH-500). It is computable from existing files.

**M6. The weaker GPT-4.1 result is left out of the abstract and the verdicts, so the frontier-judge generalisation rests on one model.**

*Location:* Abstract (mentions only Sonnet 5); Table 1 P2 verdict "Holds on constructed pools and on MACE"; Section 5 verdict l.283-285.

*Problem.* GPT-4.1 is the second frontier judge, and its effect is much weaker:

| Measure | GPT-4.1 | Sonnet 5 |
|---|---|---|
| k-pool margin | +0.99 | +3.00 (Table 25) |
| Grading AUROC change, replication | −0.04 | |
| Grading AUROC change, k-pool | −0.01 [−0.04, +0.00] | |
| k-pool false rejections | +1.0 [−4.0, +6.0] (Table 15) | |

The ties explanation (15 candidates tied at max) is plausible but is itself a limitation of expected-score readout with five logprobs. A reader of the abstract would assume the effect generalises to frontier judges.

*Fix.*
- Abstract: after the Sonnet 5 AUROC range, add "(0.01-0.04 for GPT-4.1, whose scores tie heavily)".
- Table 1 P2 verdict: add "small or absent for GPT-4.1".
- Section 5 verdict: name GPT-4.1 explicitly.
- Limitations l.425-426: say that one of the two frontier judges shows a much weaker effect.

**M7. P3 evidence is stated more strongly than the design allows, and the obvious "the prompt told it to" objection is not answered where it matters.**

*Location:* l.293-294 ("Sonnet 5's API subsamples give a direct test with a noise control"); l.297-298 (Qwen2.5-7B "scored 9 or above blind still gain 5.3 points"); verdict l.314-315 ("Qwen2.5-7B moves arithmetic answers it scores highly blind, so the effect is not only a failure to verify"); Limitations l.428-429 ("Every referenced prompt called the reference 'trusted'…").

*Problem, part (a).* The "noise control" is the group of matching answers scored 10 blind. Under the paper's own Equation (1) that group receives the λ bonus, so the 19% vs 0% contrast is penalty plus bonus, not penalty against noise. It controls regression to the mean only if the reference has no effect on matching answers, and the paper shows it does. No blind-blind test-retest for Sonnet 5 is reported.

*Problem, part (b).* A blind score of ≥9 does not show verification for Qwen2.5-7B. Appendix N l.1968-1970 reports that a ≥7 blind filter keeps 24% of *wrong* answers for Qwen2.5-7B, and the wrong-answer pass rate at ≥9 is not reported. The good open-judge evidence for P3 is the per-task blind-AUROC tercile: 3.6 points where blind AUROC averages 0.98 (l.298-300; App N l.1972-1976). That should lead.

*Problem, part (c).* The agreement reading explicitly includes "because the prompt tells it to use the reference; we do not separate these" (l.80). A reviewer's first objection will be that a judge told the reference is trusted and to compare against it is just following instructions. The paper has partial evidence against a pure prompt artefact, but it is buried in Section 7 and Appendix H/M:
- With "any correct answer deserves full credit even if it differs from the reference", Sonnet 5's k-pool margin is still **+2.08 [+1.14, +3.14]** (Table 25, l.1521).
- The verbatim MT-Bench template, which does not say "trusted", still gives −3.59.

*Fix.*
1. Replace "with a noise control" with "with a comparison group of matching answers".
2. Add: "we did not measure how often Sonnet 5 moves a blind 10 to 3 or below on re-scoring without a reference".
3. For Qwen2.5-7B, lead with the tercile result. Either drop the ≥9 sentence or add the share of wrong answers scored ≥9 blind (computable from existing files).
4. Add two sentences to Section 6, and cross-reference them in Limitations: "The effect is not only the word 'trusted' or the comparison instruction: under the verbatim MT-Bench template Qwen2.5-7B still loses 3.59 points, and told that any correct answer deserves full credit, Sonnet 5 keeps a margin of +2.08 [+1.14, +3.14]."

**M8. The abstract and Section 4 pick the favourable ends of ranges.**

**(a) "2.7 to 5.4 points" is rubric (a) only.** (Abstract l.17-18; Table 1; Conclusion l.442)
- Table 5 (l.978-982), rubric (b): Qwen2.5-7B +6.34 / −6.58 (original scorer); Sonnet 5 +2.54 / −2.51.
- Across both registered wordings the swap spans about **2.5-6.6**.
- *Fix:* say "under our main rubric" at first use, or report "about 2.5 to 6.6 points across two rubric wordings". The paper counted both wordings as registered cells (l.215), so it should not quietly report one.

**(b) "reaches 9.8 points for the smallest Qwen2.5 judges and 3.1 for 14B".** (l.249)
- 9.8 is the *maximum* small-judge cell (3B, rubric b, loss; Table 6 l.994).
- 3.1 is neither the minimum nor the maximum 14B cell: 14B ranges from 2.78 (loss a) to 3.81 (loss b).
- *Fix:* "8.7 to 9.8 points for the 1.5B and 3B judges and 2.8 to 3.8 for 14B (Appendix C)."

**(c) "within 3 pp of the same value under each of the four labelings".** (l.273-274)
- Qwen2.5-7B k-pool spans +35.4 to +32.3, i.e. 3.1 pp (Table 15 l.1266).
- *Fix:* "within about 3 pp across the four labelings".

**M9. Sonnet 5 results are compared across interfaces despite the paper's own rule.**

*Location:* Section 3 l.179-180 ("agree exactly on only 67% of shared calls, so we compare Sonnet 5 results only within an interface") vs Section 6 l.307-309 ("its false rejections in this CLI design rise by 17.5 and 12.5 pp, against 36 pp on the API subsamples"). Table 1's P3 row also pools CLI (94%, 4.0, 3.0) and API (19%) into one verdict.

*Fix.* Delete "against 36 pp on the API subsamples, whose candidates differ" from l.308-309. In Table 1 P3, write "(CLI)" and "(API)" after the respective numbers so the pooling is visible.

**M10. The same glyph means different things in Figures 2 and 6, on the headline robustness caveat.**

*Location:* Figure 2 caption l.242 ("grey ticks: boxed replies only") vs Figure 6 caption l.1217 and legend ("grey ticks: registered checker"; legend "registered checker (boxed answers)").

*Problem.*
- In Figure 2 the grey tick for k-pool Qwen2.5-7B sits at about −0.09, the boxed-only value.
- In Figure 6a the grey tick for the same cell sits at about −0.30, the registered value.
- Table 14 treats "Registered" and "Boxed only" as separate columns. Figure 6's legend conflates them, and Figure 6 does not show boxed-only at all, although it is the paper's stated conservative estimate (l.419-420).

*Fix.* In Figure 6, use the grey tick for boxed-only (as in Figure 2), a different glyph for registered, and drop "(boxed answers)" from the legend.

### POLISH (would improve clarity; not individually blocking)

**P1. The abstract carries too much load.**
- 11 numbers, 7 ranges, and undefined jargon: "four ways of reading answers", "boxed replies", "best-of-64", "constructed tasks".
- The "although" at l.23-24 joins a multi-answer grading result to a unique-answer selection result, which reads as a non sequitur.
- Proposed rewrite (same facts, about 40% fewer numbers):

> LLM judges are routinely given a reference answer, as if it were an answer key. We test whether it acts like one when a question has several correct answers. On constructed arithmetic tasks whose correct answers are enumerated by a program, moving the reference from one correct answer to another changes the score of identical text by about 3 to 5 points out of 10 for Qwen2.5-7B, phi-4, and Claude Sonnet 5. Correct answers that differ from the reference are graded worse: the AUROC separating them from wrong answers falls by 0.07 to 0.27 for four open judges, depending on how answers are extracted, by 0.04 to 0.15 for Sonnet 5, and by at most 0.04 for GPT-4.1, whose scores tie heavily; on factual questions from MACE it falls by 0.06 to 0.15. This is not only a failure to verify: of the factual answers Sonnet 5 scores 10 without a reference, it scores 19% of those that differ from the reference 3 or below once the reference is shown. Reasoning before scoring removes the effect on arithmetic but only roughly halves it on factual questions. With a unique answer the reference still raises best-of-64 accuracy by about 30 points. The problem is not references but treating one correct answer as the only one.

**P2. Too many coined terms for a 9-page paper.**
- Sections 3-7 introduce: swap change, false-rejection rate, grading AUROC, best-of-64 accuracy, margin, inflation, screened judges, score-only, explanation first, thinking on, exact scorer, original scorer, any-format labels, registered labels, replication pool, k-pool, pass-rate band. Figure 3's title adds "anchoring", which the main text never defines.
- Cut from the main text:
  - "inflation": one sentence plus a pointer.
  - "original scorer": say "an approximate scorer (Appendix O)" once.
  - "anchoring": use "the effect".
  - "screened judges": list the four names once, then say "the four open judges".
- Keep "margin" only if used more than twice. It currently appears in Section 4 (masking) and Section 6.

**P3. Terms are used before they are defined.**
- "replication pool" in the Figure 1 caption (l.51) is not defined until l.160. Write "over 120 constructed tasks (the replication pool)".
- "margin" in Table 1 P3 (l.130) comes before l.198-199.
- "MACE" is used in Table 1 before Section 3; give it a two-word gloss in the intro (l.72: "the factual QA benchmark MACE").
- "pp" appears in Table 1 before l.200.

**P4. The registration tally in the intro (l.93-94) is noise at that position and invites a "59% confirmed" reading.** Move it to the end of Section 3 ("Measurements and conventions") as one sentence. Replace it in the intro with the credibility signal that matters: "The swap test and most grading results were pre-specified; we mark post hoc results with †."

**P5. Ledger count inconsistency.** Table 4 (l.866) says the frontier CLI check is "Excluded from the counts", but the 156 total (l.788-791, intro l.93-94) includes those 3 excluded predictions. Say "159 registered, 3 excluded, 156 counted", or remove them from the 156.

**P6. Sign error.** l.302-303: "Qwen3-14B's swap loss is 1.98 points with thinking off and 0.12 with it on (Qwen3-8B: 0.69 and 0.01)". Qwen3-8B with thinking on is **+0.01** (a gain, Table 50 l.2178). Write "(Qwen3-8B: 0.69 and none)".

**P7. Registration marks are ambiguous in two places.**
- l.279: "falls by 0.08 for Qwen2.5-7B and 0.06 for phi-4.†" Qwen2.5-7B's MACE grading is pre-specified (Table 48 caption l.2064; ledger l.943-944). Place † directly on "0.06†" and keep the full stop outside.
- l.311: the Qwen3-14B blind-AUROC comparison is pre-specified (ledger l.941-942), but the sentence-final † covers it. Mark only the Qwen3-8B values.
- Table 13's caption says the registered k>1 values are "pre-specified" while l.371 marks them ‡. Use ‡ in the caption too.
- In Figure 1's caption, replace "a pre-specified re-analysis" with the ‡ symbol, for the same reason.

**P8. Section 2 is dense for what it delivers.** Only λ is ever estimated in the main text, β never and γ only through the flawed look-alike sentence (M4). Keep the equation and the key point that "P2 needs more than P1" (l.148-151). Cut the λ0(1−v) parametrisation to a clause, and drop "β ≤ 1" from the display. Also, l.146-147 says every reading expects the reference to help with one answer, but the answer key only requires κ ≥ 0. Write κ > 0, or say "every reading allows the reference to help".

**P9. Table 2 and Section 7 print two values for the same cell on the same page.** l.369 says "30.3 pp" for Qwen2.5-7B k-pool while Table 2 shows −24.2 (the caption explains). Either print the exact-scorer reference row in Table 2 with a footnote that the other rows are original-scorer, or quote −24.2 in the text with "(−30.3 under the exact scorer)". One number per cell per page.

**P10. Wording in Section 5.**
- l.269 "the reference changes no screened judge's pick on any task". The picks can change; what is zero is the per-task accuracy change (Table 13 [+0.0, +0.0]; Table 49 l.2118 shows picks moving toward look-alikes under registered labels). Write "does not change the accuracy of any screened judge's pick on any task".
- Table 13's caption says the band is recomputed per labeling, so also state the any-format k=1 task count rather than reusing 14.

**P11. Tables 14 and 15 captions** (l.1244-1246, l.1260-1261) do not state the scorer or the matching rule. The main text quotes both tables. Add "Exact scorer for Qwen2.5 and gemma-2; matches decided from the extracted answer (compare Table 48)."

**P12. Limitation bullets.** "Tasks" (l.422-424) should add that the constructed pools come from five arithmetic families with one generator and the natural data from two MACE domains, so the grading results rest on about 300 tasks. The "Downstream" bullet is good. The intro's training motivation (l.66-67, "score rollouts for training, so what they reward is what gets optimized") should get a half-clause pointing to that null.

**P13. Reference formatting.** Bulian et al.: "Tomayto, tomahto. beyond token-level…" needs a capital B (brace it in the .bib). Check the other titles for lost capitals (MT-bench → MT-Bench in Zheng et al.).

**P14. Numbers that need an interval.** "cost 6.7 pp on MATH-500" (l.378, Table 2 title) and "2.6 pp for Qwen2.5-14B" (l.379) have no interval, while the Sonnet cost beside them does. Add paired intervals from existing files.

---

## 4. Figure-by-figure and table-by-table critique

**Figure 1 (p.1). Keep; small fixes.**
- It is at the bar: one question, one example, one aggregate, on page 1.
- Panel (b)'s two referenced scores (2.9 and 9.3) share a colour, which hides the key contrast. Colour 2.9, the reference that differs, distinctly, and keep 9.3 in the matching colour.
- The grey in-figure caption under (b) is about 6pt at print and reports a P2 statistic (0.4%/28%) inside a P1 figure. Cut it, or enlarge it to at least 7pt.
- Panel (c) is readable. Its caption should use ‡ rather than prose for status, and should define "replication pool" (P3).
- The caption stands alone apart from "replication pool".

**Table 1 (p.3). It earns its space, but it is the single source of truth and must match the text exactly.**
- Fix the P1 verdict (M1), the P2 verdict (GPT-4.1, M6), the P3 row's interface labels (M9), and the moderator row's ambiguity (M1).
- The "Observed" column for P2 packs 5 ranges into one cell. Keep one number per judge family: "AUROC falls 0.07-0.27 (open, by labeling), 0.04-0.15 (Sonnet 5), ≤0.04 (GPT-4.1)".
- The caption's mark legend is good.

**Figure 2 (p.5). Earns its space; needs restructuring.**
- *Rows do not line up across panels.* Panel (a) has 12 rows grouped "One / Several"; panel (b) has 17 rows grouped by pool, and panel (a)'s lower third is blank. Use one shared row list (pool × judge) for both panels, with "n/a" markers where a quantity is undefined, as Figure 6 already does for MATH-500 grading.
- *Status line.* The caption's "Status:" sentence (l.244-246) is a 40-word registration inventory. Put †/‡ on the row labels instead.
- *Fonts.* At 100% print, tick labels are about 6pt and row labels about 7pt. Raise both to at least 7-8pt.
- *Title.* Overclaims (M3).
- The "grey ticks: boxed replies only" convention is excellent. Keep it and make Figure 6 match (M10).

**Figure 3 (p.7). Earns its space.**
- Panel (a) is clear, and the within-group caveat is well handled with a divider.
- Panel (b) mixes condition meanings across rows (M1c).
- The title says "anchoring", which the main text never defines, and "at most halves", which is wrong (M1).
- The arithmetic bars in (b) for Qwen3 (+1.5/+0.0, +6.1/+0.3) are post hoc and add little beyond (a). Consider dropping them, so panel (b) is "factual questions only" and matches the caption's point.

**Table 2 (p.7). Earns its space; it is the only practitioner-facing artefact.**
- The honesty sentence ("One k-pool task moves a cell by 3.0 pp…") is exactly right. Keep it.
- Problems: the double-scorer issue (P9), no grading row (M5), and the missing interval on the 6.7 pp headline in the title (P14).
- The caption is long (about 110 words) but stands alone.

**Appendix figures.**
- **Figure 4:** panel (a)'s legend and tick labels are about 5pt at print; enlarge them. Panel (b) duplicates Table 10; one of them can go.
- **Figure 5:** fine.
- **Figure 6:** glyph inconsistency (M10); otherwise a useful companion to Figure 2.
- **Figure 7:** fine.
- **Figure 8:** fine.
- **Figure 9:** fine. Its arrows are a good idea; the markers are small.

**Appendix tables.**
- Table 49 ("Numbers quoted in the main text") and Table 27 (cell sources) are excellent reviewer aids. Keep them.
- Table 4 (ledger) is exhaustive and candid. Keep it, but fix the excluded-count wording (P5).

---

## 5. What is already at the bar (leave alone)

- **Title and question.** One clear, falsifiable question, stated in the title. Do not retitle.
- **Figure 1's concept.** The same text scored 10.0 / 2.9 / 9.3, then the pool average. This is the right figure-that-explains-the-idea.
- **Structure by prediction.** Sections 4-6 each end in a one-line verdict. This is the best structural decision in the paper; it keeps the flow readable despite the density.
- **The P2-needs-more-than-P1 argument** (l.148-151). It is non-obvious and correct; keep it in some form.
- **Section 7's title and the MACE null** ("our registered prediction of a loss was not confirmed"). Candid, and it strengthens the paper.
- **The Limitations section.** Prominent, specific, and it names the retroactive verdict rule. Keep it, with the M6/M7 additions.
- **The one-vs-several contrast** (P2′ with MATH-500 and MACE k=1). It pre-empts "references are just bad" and gives the paper a balanced message.
- **Registration marking in general** (unmarked / † / ‡). Consistent in the large majority of places; only the spots in P7 need work.
- **Related work.** Compact, with the right comparisons: Li et al. solution fixation, wrong-reference studies, MT reference bias. No need to expand.
- **Appendix accountability tables** (Tables 4, 27, 49). Keep them as they are.

---

## 6. What would move the score up, without new experiments

**+1 (to 7): make every main-text claim match the paper's own data, and lighten the reading.**
1. Fix M1-M4 and M8-M10 wording exactly as proposed above. These are sentence-level edits and total about half a day.
2. Rewrite the abstract along the lines of P1, including GPT-4.1 (M6).
3. Compute max-rule and blind-then-reveal grading AUROC from existing score files, add them to Table 2, and rewrite the conclusion's recommendation to match whatever they show (M5). This turns the weakest paragraph into a practical contribution.
4. Move the instruction-mitigation and MT-Bench evidence into Section 6 to answer the prompt-artefact objection (M7).
5. Restructure Figure 2 with shared rows and on-label marks, and enlarge its fonts.

**+2 (to 8): the above, plus a tighter single story.**
1. **One headline number per prediction** in the abstract, intro summary, Table 1, and conclusion, used identically everywhere. For example: P1 "about 3-5 points"; P2 "AUROC −0.07 to −0.27 (open), −0.04 to −0.15 (Sonnet 5)"; P3 "19% of blind-10 answers".
2. **Cut coined terms to about 8** (P2). Push inflation, the original scorer, the pass-rate band, and "screened" to the appendix.
3. **Add a small "when does the reference help or hurt?" panel**, re-plotted from existing Tables 2, 44, and 49. Show selection change for three regimes: one correct answer; several correct answers with a matching correct candidate; several with none. Open judges only, any-format labels, intervals. This would be the practitioner's figure, and would make Section 7 as memorable as Figure 1.
4. **Frame scope honestly in the intro.** The evidence is constructed arithmetic plus two MACE domains, with judges up to 14B plus two API judges. The prevalence audit (30% of NQ-open) is why this matters, but NQ-open itself is untested. A reviewer who sees the scope stated up front does not penalise it as a hidden weakness.

Without new experiments, I do not think this paper reaches 8 with high confidence. The ceiling is set by the scope (one frontier judge with a strong effect, mostly arithmetic tasks, no human-validated labels on the constructed pools). The rewrites above would make it a clear, trustworthy accept at 7.
