# Round 2 review: "Reference Answers Mislead Fast LLM Judges When Many Answers Are Valid"

Reviewer role: Area Chair, focused on presentation and polish. I read the frozen PDF (23 pages; the main text ends at p. 8, l. 403) and page renders at 110 and 220 dpi. I checked `main.tex`, `appendix.tex`, `tables/r2b.tex`, `tables/acc_kpool.tex`, `tables/repl_robust.tex` and `main.log`. I wrote Sections 1-2 in draft before opening `round1_review.md`, and did not change the scores after reading it.

---

## 1. Skim impression (3-minute AC pass)

**What I took away.**
- A reference-guided LLM judge treats a reference answer as the answer key. When several answers are valid, it scores agreement with the reference.
- The clean test holds the candidate text fixed and swaps which valid answer is the reference. The score moves by 2.5 to 6.3 of 10 points, while answers matching neither reference stay put (Fig. 1b).
- Best-of-64 then loses 9 to 31 accuracy points on multi-answer tasks. On MATH-500, where each problem has one answer, the reference gains about 30 points.
- Judges seem to run an equality check against a readable answer.
- One thinking judge is immune.
- "Blind, then reveal" keeps the unique-answer benefit and recovers part of the multi-answer loss. Table 1 turns this into advice.

The story now flows problem → cause → consequence → mechanism → fix, and the section order matches the contribution bullets. This is a much easier paper to skim than round 1.

**Where I got lost, in order:**
1. **The title word "Fast".**
   - The abstract defines it as "score in one token or after a short explanation". The MT-Bench judge writes about 259 tokens and counts as fast. The thinking judge writes 569 tokens and does not. The boundary is a factor of two in length.
   - The only non-fast judge is a *different model* (Qwen3-8B, against Qwen2.5-7B) with a different estimator (sampled integers at T=0.6, against expected score).
   - I could not tell whether the title rests on thinking, on model generation, or on the sampling interface.
2. **The headline numbers come from a "Claude command-line interface" judge** (abstract; intro para 2; Fig. 1a). The model version and thinking setting are not stated, and blind it already fails 20.5% of correct answers. There is also a separate "Sonnet 5" API judge, and Fig. 2b shows both as if they were two different judges.
3. **Table 1 says "Thinking judge unaffected".** Table 6 (p. 15, 5-pt font) shows the thinking judge's best-of-16 accuracy falling by 5.8 points at k=1 with the reference, with an interval of [−11.4, −1.8] that excludes zero.
4. **Table 1 recommends the reference when "Answer known to be unique"**, yet Fig. 2a's own k=1 tasks show no gain for any judge, and losses for Qwen2.5-7B and Mistral-7B.
5. **"Inflation (SD)"** is still in Fig. 3b and in several key sentences. I still do not have an intuition for one SD of it.
6. **"blind-then-reveal ... recovers part of the lost accuracy".** Only in Sec. 6 prose do I learn that for phi-4 and gemma-2-9b it recovers a quarter of the loss. Table 7 shows it stays 13 to 15 points below blind for those two judges. The "validity gate" in the same table is within 3 points of blind for four of five judges and never reaches the main text.

**One-sentence AC summary:** a careful, honest and now readable study with one excellent experiment (reference rotation). The revision fixed most round-1 problems, but the new title-level claim ("Fast") and the practitioner table go further than the evidence.

---

## 2. Scores

| Dimension | Score |
|---|---|
| **Overall (ICLR scale)** | **5**: marginally below threshold, upper half. Text-only calibration fixes (Section 3, B1-B3 wording, B4, B6) would make it a 6. |
| Presentation | 6 |
| Clarity | 5 |
| Soundness of claims (calibration) | 5 |
| Significance | 5 |
| **Confidence** | **4** |

**Against the calibration set:**
- "Emergent Abilities Mirage" and "LLMs Get Lost in Multi-Turn" each take one reusable idea and show it on natural settings people already use. "Registers" pairs a mechanism with a fix that is validated broadly.
- This paper's core rotation test is as clean as any of those.
- But the harm is shown mainly on synthetic arithmetic tasks with open judges of 14B parameters or smaller, and the practical boundary (thinking judges) rests on a single confounded comparison.
- The natural-data consequence is never measured end to end. The prevalence audit is labeled by LLMs and has no judge run attached.

---

## 3. Blocking issues (ranked)

### B1. The title's boundary ("Fast") is not identified by the evidence.
- **Confounds.** The only non-fast judge is Qwen3-8B with thinking on. The fast judges are Qwen2.5-7B, phi-4, Sonnet 5 with thinking off, and so on. The two sides differ in:
  - model generation and post-training (Qwen3 against Qwen2.5);
  - estimator (sampled integer at T=0.6 against expected score over tokens);
  - scale and template (rubric a with a "Score: N" line against 0-10 single-token or MT-Bench 1-10).
- **Missing control.** The clean contrast is Qwen3-8B with thinking *off*: same weights, same prompt, same sampling. It is one cheap run and it is missing. Without it, "thinking removes the effect" is one of at least three explanations.
- **Ceiling.** The thinking judge gives 10/10 to 96.2% of valid rotation samples blind (App. C). The "now matches" gain (−0.006) cannot be positive at the ceiling, so only the loss side (+0.011) is informative. Say so.
- **Accuracy is not zero.** Table 6: thinking-judge accuracy with the reference is −5.8 [−11.4, −1.8] at k=1 and −3.7 [−7.5, +0.0] at k>1. The main text (p. 4, l. 214) prints these without intervals. Fig. 1's caption says "the thinking judge's bars are at zero", and Table 1 says "Thinking judge unaffected".
- **Scope.** Tested only on calculable tasks the thinking judge can solve itself. References matter most where the judge *cannot* verify, and that regime is untested (Limitations says so, but the title does not).
- **"Fast" is a coined, non-standard term,** and its definition names a class that was never tested ("lightweight verifiers", p. 2, l. 080).
- **Required:**
  - either run Qwen3-8B with thinking off (and ideally Sonnet 5 with extended thinking) on the R2-B subsample,
  - or retitle to drop "Fast" (e.g., "Reference Answers Mislead LLM Judges When Many Answers Are Valid") and move the thinking result to a scoped sentence: "one thinking judge, a different model, was unaffected on tasks it could solve; we did not isolate thinking from model".

### B2. The practitioner table (Table 1) and its paragraph claim more than the tables support.
- **Row "Answer known to be unique → Reference".**
  - The evidence is MATH-500 only. The ledger says reference-over-blind there carries no registration weight after Amendment 1, and Table 14 is PH.
  - The paper's own controlled k=1 cells (Fig. 2a, Table 7) show no gain for any judge, and −21.4 (Qwen2.5-7B) and −10.3 [−15.5, −5.2] (Mistral-7B). The authors attribute these to wrong answers that resemble the reference.
  - The row needs that caveat.
- **Row "Several answers may be valid → Thinking judge, blind, or blind-then-reveal".**
  - It lists three options with no ranking.
  - "reveal matched blind for three of five judges" counts Qwen2.5-7B's −10.3 [−25.6, +5.1] as a match because its interval includes zero.
  - For phi-4 and gemma-2-9b, BTR is −15.4 [−28.2, −2.6] and −12.8 [−25.6, −2.6] below blind.
  - Only blind is backed by the evidence here. The validity gate (Table 7: −2.6, 0.0, −2.6, −2.6, −11.2) beats BTR on accuracy for four of five judges and is never mentioned in the main text.
- **Row "Unknown → Blind-then-reveal".**
  - No mixed-prevalence pool was run.
  - The paper has every ingredient for the break-even calculation and does not do it. For Qwen2.5-7B: reference beats BTR by 2.9 points on unique answers (98.1 against 95.2), and BTR beats reference by 20.5 on multi-answer tasks. Break-even is at roughly 12% multi-answer prevalence.
  - By the paper's own audit (0% MATH-500, 2.5% GSM8K) the plain reference wins on curated math. BTR wins on NQ-open-like data (18.5 to 30%).
  - That is the actual practitioner guidance, and it is stronger and more honest than "blind-then-reveal does acceptably in both cases" (p. 7, l. 339).
- **Also:** "blind never less accurate than the reference" is true only pooled over k>1. Qwen2.5-14B at k=2 is +7.7 [+0.0, +23.1] for the reference. The table is 25 pt overfull (`main.log`, "Overfull \hbox (25.38742pt too wide) in paragraph at lines 252--265").

### B3. The headline frontier number rests on the weakest-provenance judge.
- **Undocumented judge.** The abstract's "83.3% ... against 20.5%", intro para 2 and Fig. 1a all come from a judge called "through Claude's command-line interface".
  - The model version is not given ("a frontier Claude Sonnet model").
  - The thinking setting is not given, which matters now that thinking is the title's boundary.
  - Nor is whether the CLI's own system prompt and tools were in context.
- **Weak blind baseline.** Blind, it already scores 20.5% of correct non-matching answers ≤3, and 19.1% of correct matching ones (App. H). That is a poorly calibrated blind judge.
- **A documented alternative exists.** Sonnet 5 through the API, thinking off, forced tool call: rotation +3.04 / −2.66, false rejection 4.9% → 26.2%.
- **Required:** lead with the documented API judge, or fully specify the CLI configuration in Sec. 2. Round-1 items 3 and 38 raised this and it is still unresolved.

### B4. The mechanism claims mix confounded and contradicted evidence.
- **"shrinks when the answer is a program"** (abstract, bullet 3, Fig. 3 title "the harm shrinks as that comparison gets harder").
  - App. K discloses that program outputs cluster (a median of two distinct returned lists per task). Format and effective k change together, and k is the paper's own main driver of harm.
  - phi-4's program value (−0.37) exists only after a post-registration checker fix. Under the registered labels it is −0.06 [−0.22, +0.11].
  - Fig. 3b is labeled PRE with no mention of this.
- **"only exact equality matters"** (p. 5, l. 253) contradicts App. I: invalid "lure" answers that resemble the reference get +1.4 and +1.7 point bonuses. It also contradicts App. N: a one-swap invalid answer scores +3.47 above an unrelated one. What the data show is "numeric closeness does not reduce the penalty on valid answers".
- **The decode-cost follow-up** (p. 5, l. 254-256) is confounded by the authors' own admission. It adds cognitive load without evidence. Move it to the appendix.

### B5. Evidence labels are mostly right but wrong in load-bearing places.
- **Synthetic-grid step.** P. 4, l. 209: "it is positive for all six judges on a separate synthetic grid^PRE". Table 10's caption says "Post-hoc paired re-analysis of a pre-specified grid", and the ledger scores the registered prediction as "confirmed in direction". → PH.
- **Fig. 4b** is labeled PRE for all three bars. The ledger says reference-over-blind on MATH-500 is "without registration weight after Amendment 1". Label the BTR bar PRE and the reference-vs-blind comparison PH.
- **Unlabeled PRE work.** The Training paragraph (p. 5, l. 238) and "A second wording" (p. 6, l. 298) carry no label, although both are PRE.
- **Framing.** Every accuracy and false-rejection number in the abstract and bullets 2 and 4 is post hoc. The OSF-registered endpoint (inflation) is absent from the abstract. One clause in the abstract or at l. 100 should say so. Otherwise the OSF badge implies more than it covers.

### B6. Figures still break their own visual grammar and have new collisions.
- **Fig. 1b x-axis.**
  - Tick labels overprint: "Sonnet 5MT-Bench" and "MT-Benchthinking".
  - The axis mixes judges (Qwen-7B, phi-4, Sonnet 5), a template (MT-Bench) and a mode (thinking).
  - "Qwen-7B" here, "Qwen2.5-7B" elsewhere.
- **Fig. 1 layout.** Panel a's legend runs into panel b's y-label. The "−0.0" data label is an artifact.
- **Hatching changes meaning:** "no longer matches" in Fig. 1b, "phi-4" in Fig. 3a.
- **Hollow vs filled changes meaning:** k=1 vs k>1 in Fig. 2a, phi-4 vs Qwen in Fig. 3b.
- **Redundant or misleading encodings in Fig. 2a.** Marker shape repeats the judge already named on the y-axis. Hollow markers at exactly 0 with zero-width intervals look like missing data.
- **Fig. 3a:** the "thirty-one" tick wraps, and "one" collides with the legend.
- **Fig. 4a:** the orange "blind" label touches the panel title.
- **The paper's central dose-response ("the loss grows with k") has no figure.** Fig. 2a pools k>1.

### B7. Cognitive load is still high for a 9-page paper with 1.5 pages unused.
- **Coined terms in the main text: about 18.** Fast judge, thinking judge, blind, referenced, rotation, anchoring margin, selection accuracy, false-rejection rate, inflation/added inflation (SD), replication pool, k-pool, synthetic grid, rubric a/b, blind-then-reveal, OSF/PRE/PH, "step from k=1 to k>1", Claude CLI judge, MT-Bench template.
- **Metrics: four** (margin, accuracy, false rejection, inflation).
- **Number density.**
  - P. 3, l. 139-157 has 25 numbers in one paragraph.
  - "The effect of k" (p. 4, l. 200-214) packs eight findings from five pools, with three evidence labels, into one paragraph.
- **Unused space.** The main text ends mid-p. 8, so there is room for the by-k figure and the thinking on/off control.

---

## 4. Line-level fixes

Quotes are exact current text. Page and line numbers are from the PDF.

### Title and abstract
1. **Title "Reference Answers Mislead Fast LLM Judges When Many Answers Are Valid".** See B1. → Unless the thinking-off control is run: "Reference Answers Mislead LLM Judges When Many Answers Are Valid". If it is run and holds: "... Mislead Non-Reasoning LLM Judges ...". "Non-reasoning" is the field's term; "fast" is not.
2. **"for fast judges, those that score in one token or after a short explanation, including Claude Sonnet 5 and the standard MT-Bench prompt"** (l. 016-018). MT-Bench is a prompt, not a judge, and Sonnet 5 is "fast" only because thinking was disabled. → "for judges that score without extended reasoning: single-token rubrics, the MT-Bench reference-guided template, and Claude Sonnet 5 with extended thinking off".
3. **"With the reference in its prompt, a frontier judge scores 83.3% of correct answers that differ from it at 3/10 or below, against 20.5% without it"** (l. 018-020). See B3. → "With the reference, Claude Sonnet 5 scores 26.2% of correct answers that differ from it at 3/10 or below, against 4.9% without it". Alternatively, name the CLI model, version and thinking setting.
4. **"picks a correct answer 9 to 31 points less often for all five open judges we test"** (l. 020-021). You test nine or more open judges (grid judges, Ministral-8B, Qwen3-8B). → "for all five open judges we ran on this pool (post hoc)".
5. **"and shrinks when the answer is a program"** (l. 023). Confounded (B4). → "and shrinks as the requested format moves from an integer to a program, which also leaves fewer distinct valid answers".
6. **"with thinking enabled, Qwen3-8B checks each answer itself, and swapping the reference moves its scores by at most 0.011 points"** (l. 024-026). This is anthropomorphic and asserts a mechanism. → "Qwen3-8B with thinking enabled gives nearly every valid answer 10/10 with or without the reference, and swapping the reference moves its scores by at most 0.011 points; we did not run the same model without thinking."
7. **Abstract length.** About 255 words and 12 numbers. Cut the mechanism sentence to one clause and drop the parenthetical "(95.2% selection accuracy against 98.1%)" to reach about 190 words.

### Introduction (pp. 1-2)
8. **"We asked a frontier Claude Sonnet model, through Claude's command-line interface"** (l. 037). → Name the model ID and thinking setting, or switch the hook to the API judge (B3).
9. **"Most of those correct, non-matching answers now received a failing score."** (l. 041). This is a dramatic one-liner with a tense clash ("now received"). → "With the reference, 83% of them scored 3 or below."
10. **"in an audit of 200 sampled questions each, 2.5% of GSM8K and DeepScaleR problems and 30.0% of NQ-open questions admitted more than one correct answer"** (l. 049-051). The labels come from two passes by Claude models, not humans, and the multi-answer GSM8K items are mostly underspecified problems (App. E). → Add "(LLM-labeled; 0% of MATH-500; 18.5% of NQ-open after excluding time-dependent answers)".
11. **"and none asks what happens when something optimizes against such a judge"** (l. 077). The optimization studied is best-of-n. Training is inconclusive. → "and none measures what best-of-n selection does with such a judge".
12. **"as scalar judges, MT-Bench-style graders, and lightweight verifiers do"** (l. 080). Lightweight verifiers were not tested. → Delete "and lightweight verifiers". Add the token counts: "(1 token; about 260 for MT-Bench; 569 to 1,092 for the thinking judge)".
13. **Bullet 1: "It disappears for a judge that thinks at length before scoring, which verifies each answer directly."** (l. 086-087). → "It was absent for the one thinking judge we tested (Qwen3-8B, a different model) on tasks it can solve by calculation."
14. **Bullet 2: "and the loss grows with the number of valid answers k"** (l. 089-090). No main-text figure shows this. Qwen2.5-7B's losses are non-monotone (−23.1, −11.1, −30.0, −71.4). → Add a by-k panel (Section 5 below), or write "and is largest at k=16 (7 tasks)".
15. **Bullet 2: "On unique-answer math problems the same reference raises accuracy by 27.6 to 43.8 points."** (l. 090-091). → "On MATH-500 the same reference raises accuracy by 27.6 to 43.8 points; on our own k=1 tasks it did not help."
16. **Bullet 4 title "A change of protocol helps more than a change of prompt"** (l. 096). A chiasmus, and the comparison is never run on one pool and one metric. The instruction was measured as a margin on the synthetic grid; BTR was measured as accuracy on the k-pool, where for phi-4 it recovered only 5.1 of 20.5 points. → "Instructions help only some judges; scoring blind first and then revealing the reference helps more consistently".
17. **"We label evidence throughout as preregistered on OSF^OSF, pre-specified in a timestamped commit before the data existed^PRE, or post hoc^PH."** (l. 100-101). → Append: "Accuracy and false-rejection readouts are post hoc; the OSF endpoint is inflation."

### Figure 1 and Setup (pp. 2-3)
18. **Fig. 1 title "and fast judges grade agreement with it"**. → "and judges without extended reasoning grade agreement with it".
19. **Fig. 1 caption "the thinking judge's bars are at zero."** → "the thinking judge's score changes are within 0.02 points (its accuracy changes are in Table 6)".
20. **Fig. 1 caption "(a) Mean scores a frontier Claude judge gives"**. → Name the model and interface, or replace it with Sonnet 5 API data.
21. **"The preregistered endpoint of the OSF studies is inflation: how far above an average answer of the same correctness the chosen answer scores, in pool standard deviations of the judge's rubric-b scores"** (l. 127-130). The reader is never told why rubric a selects and rubric b scores. → Add "Rubric a selects and rubric b scores, so selection noise in one wording cannot inflate the reported score."
22. **"Open judges report the expected score over the tokens 0 to 10."** (l. 122). Anthropomorphic. → "For open judges we use the probability-weighted mean over the score tokens 0 to 10."

### Section 3 (p. 3)
23. **"The score follows the reference (Figure 1b)."** (l. 139). This is the third repetition of the tagline (bullet, Fig. 1 title). → Delete and start with the numbers.
24. **"and the second rubric gives larger gains for Qwen (+6.34) and smaller ones for phi-4 (+3.25)"** (l. 143-144) and **"Within the Qwen2.5 family on an exploratory pool ... (+3.1 against +9.5)"** (l. 145-147). → Move both to App. C. The paragraph has 25 numbers.
25. **"Qwen3-8B writes 569 to 678 tokens per rotation judgment"** (l. 152). Sec. 6 (l. 269) and App. C say "569 to 1,092". → Use one range and say what each end refers to.
26. **"It gives 10/10 to nearly every valid answer whether or not the reference agrees"** (l. 153-154). → Add "(96.2% blind), so a gain is impossible at the ceiling and the informative quantity is the absent loss (+0.011)".
27. **"most of its final explanations mention the reference before setting it aside"** (l. 154-155). Anthropomorphic, and "setting it aside" is not measured. → "82.7% of its referenced replies mention the reference in their final text".
28. **"On these tasks, which can be checked by calculation, extended reasoning replaces the equality check with verification"** (l. 155-156). A mechanism claim with no control. → "On these calculable tasks its scores did not depend on the reference; because the non-thinking judges are different models, this does not isolate the effect of thinking."
29. **"The introduction's frontier numbers come from a separate pre-specified check through Claude's command-line interface"** (l. 180-181). The provenance of the headline number is buried at the end of Sec. 3. → Move it to Sec. 2 "Candidates and judges" with the full configuration.

### Section 4 (pp. 4-5)
30. **"the reference adds +1.19SD [+1.02,+1.36]"** (l. 190). Table 11 gives the same estimate as [+1.03, +1.35]. The rendered "1.19SD" also lacks a space. → Reconcile to one CI and write "+1.19 SD".
31. **"5.8% and 0.03% by phi-4"** (l. 198). Table 8 prints "0.0% → 5.8%". → Use the same precision in both.
32. **"it is positive for all six judges on a separate synthetic grid^PRE"** (l. 209). → PH (B5).
33. **"The thinking judge's accuracy changes by −5.8 and −3.7 points on the same subsample."** (l. 213-214). → "The thinking judge's accuracy changes by −5.8 [−11.4, −1.8] at k=1 and −3.7 [−7.5, 0.0] at k>1, so its step is not negative; the k=1 drop is unexplained."
34. **"The reference is a strong tool exactly where it is an answer key."** (l. 235). An aphorism that the k=1 cells of Fig. 2a contradict. → "On MATH-500 the reference is a strong tool; on our constructed k=1 tasks it did not help, and it hurt two judges through wrong answers that resemble it."
35. **Training paragraph** (l. 238-241). The result is uninterpretable by the authors' own account. → Move it to App. L and leave one clause in Limitations. If it stays, add ^PRE and use held-out accuracy (−0.228), not the training-task 41.2% → 17.5%.

### Section 5 (p. 5)
36. **"only exact equality matters"** (l. 253). Contradicted by the lure and one-swap bonuses (B4). → "numeric closeness to the reference does not reduce the penalty".
37. **"A follow-up that encoded the reference with an explicit decoding rule removed the margin after a single step, but its prompt announced the encoding, which may explain the collapse by itself"** (l. 254-256). → Move to App. J.
38. **"Added inflation fell from +1.66 for integers to +0.13 for programs under Qwen2.5-7B, and from +1.35 to −0.37 under phi-4^PRE."** (l. 262-263). → Add "; program outputs cluster (a median of two distinct valid outputs per task), so format and the number of valid answers change together".
39. **Fig. 3 title "and the harm shrinks as that comparison gets harder"**. "Harder" is not measured. → "and the harm shrinks from integer to program answers". In (b), add "phi-4's program value uses checker labels corrected after registration".

### Section 6 and Table 1 (pp. 5-7)
40. **"at a cost of 569 to 1,092 generated tokens per candidate instead of one"** (l. 269, p. 6 l. 292). The MT-Bench judge writes about 260 tokens and still anchors, so length alone is not the fix. → "instead of one token (the MT-Bench template's roughly 260-token explanation did not prevent anchoring)".
41. **"but only 5.1 of 20.5 points for phi-4 and 5.1 of 17.9 for gemma-2-9b"** (l. 310-311). → Add "; for these two judges it stays 15.4 and 12.8 points below blind, with intervals excluding zero".
42. **"and the reference then matters mostly where that judgment was wrong"** (l. 321-322). Untested. → Delete, or add "which we did not test".
43. **Table 1, row 3 evidence "blind never less accurate than the reference; reveal matched blind for three of five judges"**. → "blind at least as accurate as the reference pooled over k>1; blind-then-reveal within 10 points of blind for three judges and 13 to 15 points below it for two". List "Blind" first and add the validity gate (App. M) as a measured option.
44. **Table 1, row 2 "Answer known to be unique | Reference, or blind-then-reveal"**. → Add "(MATH-500; on constructed k=1 tasks the reference gave no gain)".
45. **Table 1, "Calls" column "long, 1, or 2"**. → "1 (long), 1, or 2". Also fix the 25 pt overfull box (narrow the column widths `L{3.9cm}L{3.3cm}L{5.0cm}`).
46. **"and blind-then-reveal is the protocol we measured that does acceptably in both cases"** (l. 339-340). → Replace with the prevalence break-even (B2): "With Qwen2.5-7B, blind-then-reveal beats the plain reference once more than about 12% of questions admit several answers; curated math sets fall below that, and NQ-open above it."

### Related work, Limitations, Conclusion (pp. 7-8)
47. **"which is a question of equivalence between surface forms of one answer. Our setting is answers that are genuinely different."** (l. 357-358). A "not X but Y" split over two sentences. → "which concerns surface forms of one answer; we study distinct valid answers."
48. **Missing prior work.** Reference bias in human MT evaluation (Fomicheva & Specia, ACL 2016: annotators given a reference translation favor outputs close to it), and the multi-reference and execution-based evaluation argument (e.g., Chen et al., 2021, on functional correctness over BLEU for programs). → One sentence each. This failure has a named history outside LLM judging.
49. **Limitations, "One 8B thinking judge showed no anchoring on tasks that can be verified by calculation"** (l. 377-378). → Add "; it is a different model from the non-thinking judges, its k=1 selection accuracy fell 5.8 points with the reference, and we did not run it with thinking off".
50. **Conclusion "correct answers that differ from it are marked as failing"** (l. 398). → "correct answers that differ from it are often scored as failing (6% to 28% at 3/10 or below for open and API judges)".
51. **Conclusion "and a judge that reasons at length verifies the answer instead"** (l. 400-401). → "and the one thinking judge we tested was unaffected on tasks it could solve".
52. **Conclusion "keeps most of what the reference is good for"** (l. 402). → Add "and recovers part of what it costs when several answers are valid".

### Appendix
53. **Review-history leaks in a double-blind submission.** "including the round-2 experiments run for this revision" (App. B), "Round-2 experiment R2-B" (App. C), "Round-2 experiment R2-A" (App. M), ledger rows "R2-A:"/"R2-B:", and "Amendment 1 of the round-2 registration" (App. F). → Use neutral names ("Experiment MATH-BTR", "Amendment 1").
54. **Table 5 caption "Every referenced interval excludes zero; two of eight blind intervals do."** The table shows no intervals. → Add CIs or delete the sentence.
55. **Tables 6, 7, 25 and 27** are shrunk by `adjustbox` to about 5 pt and are unreadable in print. Table 6 is the sole evidence for the title's boundary. → Split columns across two rows or rotate. Put Table 6 in the main text if the thinking claim stays.
56. **P. 23:** three floats spread over the page with half a page of vertical gaps. → Use `[t]` placement or `\FloatBarrier` and pack them.
57. **App. H: "blind, the judge scored matching and non-matching valid answers 7.88 and 7.85 (margin +0.35 [−0.56,+1.27])"**. 7.88 − 7.85 = 0.03, while the referenced margin (+7.49) matches its means (9.83 − 2.32). → State that the margin is a per-task mean, or report consistent aggregates.
58. **Table 3 (longtable)** continues onto p. 14 with no "(continued)" marker. Table 16's Sonnet 5 inflation rows are all "—", so say in the caption why they were not run.

---

## 5. Figures and tables: verdicts

**Figure 1 (teaser). Verdict: keep the concept, fix the mechanics.**
- Panel (a) is clear and effective, but it shows the judge with the weakest provenance (B3).
- Panel (b) is the paper's best evidence.
- Fixes:
  - (i) tick labels collide ("Sonnet 5MT-Bench", "MT-Benchthinking"). Separate the three judge groups from the two protocol groups with a gap or divider, and use full names ("Qwen2.5-7B, MT-Bench template"; "Qwen3-8B, thinking").
  - (ii) Panel a's legend collides with panel b's y-label.
  - (iii) Drop the "−0.0" and "+0.0" labels and write "≈0".
  - (iv) Name the model in (a).
- Page 1 has no figure. With 1.5 spare pages, a small schematic of the divisor-of-91 prompt could sit on p. 1.

**Figure 2. Verdict: redo panel (a); fix panel (b).**
- (a) pools k>1, so the paper's dose-response claim has no figure. Replace it with selection accuracy change against k (1, 2, 4, 8, 16):
  - Qwen2.5-7B and phi-4 in bold;
  - the other three judges light;
  - blind as the zero line.
- If (a) is kept: drop the redundant shapes, and show zero-width intervals as a tick so they don't read as missing data.
- (b) mixes two pools (replication, k-pool) and two Claude interfaces. "Claude CLI" beside "Sonnet 5" reads as two models. The CLI's blind bar (20.5%) is unlabeled while the reference bars are labeled.

**Figure 3. Verdict: acceptable content; fix the grammar and caveats.**
- (a): hatching now means phi-4, but in Fig. 1b it means "no longer matches". Use the judge-marker grammar of Figs. 2 and 4 (circle = Qwen2.5-7B, square = phi-4) as a dot plot. The "thirty-\none" tick collides with the legend.
- (b) is the only main-text panel in SD units. Either convert it to accuracy or margin, or add a one-line gloss of the unit. Hollow = phi-4 conflicts with hollow = k=1 in Fig. 2a. Disclose the checker fix and the effective-k confound in the caption.

**Figure 4. Verdict: good, with minor fixes.**
- The colour grammar (orange blind, blue reference, teal BTR) is the paper's clearest and should be the rule everywhere.
- The "blind" label touches the panel (a) title.
- Split the (b) caption label: BTR PRE, reference-vs-blind PH.
- Consider adding the validity gate to (a), since it is the accuracy winner for four of five judges.

**Table 1 (decision table). Verdict: rewrite rows 2-4 (B2).**
- 25 pt overfull.
- "long, 1, or 2" is awkward.
- Add a prevalence-threshold row or footnote.

**Appendix tables.**
- Table 3 (ledger): well built and honest (38 / 21 / 7), and the scorecard is the paper's credibility asset. Add "(continued)".
- Table 4: clean.
- Table 5: its caption refers to intervals the table does not show.
- Tables 6, 7, 25, 27: illegible.
- Table 8: fine.
- Tables 9, 10, 11: fine. Table 11's CI disagrees with the main text.
- Table 13: good.
- Tables 17-22: fine.
- Table 23: tiny font.
- P. 23: poor float spacing.
- Fig. 5: fine, and its colours are consistent with the main text.

---

## 6. What to cut or move, and what is missing

**Cut or move to the appendix:**
- The training paragraph (Sec. 4), leaving one clause in Limitations.
- The decode-cost follow-up (Sec. 5).
- Rubric-b numbers and the Ties judge-size ladder (Sec. 3).
- The "worked solution in place of a bare answer" sentence (Sec. 6).
- The MT-Bench k=1 accuracy detail (Sec. 4), which belongs in a small table with the thinking judge.
- Half the paired "X and Y" decimals in prose. Quote one number per claim and point to a table.
- Prose repetitions of the tagline "The score follows the reference".

**Missing (in priority order):**
1. **Qwen3-8B with thinking off** on the R2-B subsample, the one-run control for the title (B1). Ideally also Sonnet 5 with extended thinking on rotation and false rejection.
2. **A thinking judge on tasks it cannot verify.** MACE entity domains are already built and audited. This is where references are actually needed.
3. **An end-to-end run on a natural pool:** accuracy under blind, reference, BTR and validity gate on MACE (natural k mix) or an NQ-open subset. Pair it with the prevalence break-even in Sec. 6.
4. **One deployed RL answer verifier** (e.g., xVerify, TinyV or CompassVerifier) on the rotation test. This is the ICLR RLVR audience, and "lightweight verifiers" is already in the definition of "fast".
5. **The validity gate** in the main-text accuracy comparison and in Table 1.
6. **A by-k accuracy figure** (see Fig. 2).
7. **The Claude CLI judge's configuration,** or its replacement.
8. **Prior work** on reference bias in MT evaluation.

---

## 7. Status of round-1 blocking issues

| # | Round-1 issue | Status | One line |
|---|---|---|---|
| B1 | Fix never shown to beat blind | **Partly resolved** | BTR on MATH-500 beats blind (95.2 vs 67.6) and keeps nearly all of the reference's benefit. There is still no mixed-prevalence pool. On multi-answer tasks BTR stays 13 to 15 points below blind for two of five judges, and the validity gate beats it but goes unmentioned. |
| B2 | Judges forbidden to reason; rubric b instructs comparison | **Partly resolved** | The MT-Bench template and a thinking judge were added, and the rubric wording is quoted in Sec. 2. But the thinking arm is a different model with no thinking-off control, and it now carries the title (new B1). |
| B3 | "Exactly two valid answers, seven of eight judges" overclaim | **Resolved** | The claim is removed, and Limitations gives per-cell n. Residual: the abstract's "all five open judges we test" miscounts. |
| B4 | Opaque SD metric; unreconstructible estimator | **Mostly resolved** | Figs. 1, 2 and 4 are in points and accuracy. The estimator in App. A is now precise, and the permutation logic is explained. Residual: Fig. 3b is still in SD, and the rubric a/b split is unexplained in the main text. |
| B5 | Training promoted then retracted | **Mostly resolved** | Removed from contributions and conclusion. A full paragraph remains in Sec. 4 and should move. |
| B6 | Figure 1 and visual grammar | **Partly resolved** | Units are consistent and colour mostly means condition. There is still no schematic. There are new tick-label collisions, and hatch and hollow markers change meaning between figures. |
| B7 | Lab notebook, not a story | **Partly resolved** | Section order now follows the bullets, and the composition and GPT-4.1 detours are gone. Still about 18 coined terms, paragraphs with 20+ numbers, and 1.5 pages unused. |
| B8 | Factual and number inconsistencies | **Mostly resolved** | Every listed item is fixed or disclosed (gemma "largest", 91%, Mistral ties, GPT-4.1, MACE validity, MBPP n, checker fix, 83.3/20.5 sourcing). New ones: the 1.19 CI, the grid PRE/PH label, the token ranges, 0.03% vs 0.0%, and the CLI blind margin. |
| B9 | Thin positioning; no prevalence | **Mostly resolved** | Prevalence audit added (LLM-labeled). Li et al. delta, TinyV and xVerify now cited. Still missing: the MT reference-bias literature and any deployed verifier model. |
| B10 | "Preregistered" conflates two evidence levels | **Resolved** | OSF/PRE/PH labels and a ledger scorecard throughout. Residual mislabels are in B5. |
| r1 items 3 and 38 | Unnamed CLI frontier judge used as the hook | **Unresolved** | Still "a frontier Claude Sonnet model, through Claude's command-line interface". |
| r1 item 27 | Overfull main-text table | **Unresolved** | The new Table 1 is 25 pt overfull. |
| r1 item 17 | "Section X" for appendices | **Resolved** | |

---

## 8. Verdict

**Would I champion it now? No.** The revision is real. It adds accuracy units, BTR on unique answers, a standard template, a thinking judge, a prevalence audit and clean evidence labels, and it reads far better than round 1. But it has turned its least-supported result into the title. It gives practitioner advice that the paper's own Table 7 and k=1 cells contradict. And it still opens with a judge whose configuration is undocumented.

**Changes after which I would champion at 8+:**
1. **Identify the boundary.**
   - Run Qwen3-8B with thinking off, same weights and prompt, on the R2-B rotation and k subsamples. Add Sonnet 5 with extended thinking on rotation and false rejection.
   - Keep "Non-reasoning" in the title only if thinking-off anchors and thinking-on does not. Otherwise retitle without it.
   - Either way, report the thinking judge's accuracy intervals and ceiling in the main text.
2. **Test a thinking judge where references matter,** on at least one task family it cannot solve itself (MACE entity domains are ready).
3. **Show the consequence on natural data.** Measure blind / reference / BTR / validity-gate accuracy on a natural multi-answer pool (MACE with its natural k mix, or NQ-open), and add the prevalence break-even to Sec. 6.
4. **Rewrite Table 1 and its paragraph** per B2. Blind first for multi-answer tasks, with the k=1 caveat for "unique". Add the validity gate. Replace "does acceptably in both cases" with the break-even statement. Fix the overfull box.
5. **Replace the CLI hook** with the API Sonnet 5 numbers, or fully document the CLI configuration (B3).
6. **Fix the mechanism calibration** (B4): the program-format confound in the abstract, bullet and Fig. 3; "only exact equality matters"; move decode cost to the appendix.
7. **Fix the labels and numbers** (B5; items 30-33, 57): grid step PH, Fig. 4b split, unlabeled PRE paragraphs, the 1.19 CI, token ranges, the CLI margin aggregation. State in the abstract or intro that the accuracy readouts are post hoc.
8. **Figures** (B6): a by-k accuracy panel in place of Fig. 2a; fix the Fig. 1b collisions and mixed axis; one grammar (colour = condition, shape = judge, hollow = k=1 only, hatching nowhere); gloss or remove the SD unit in Fig. 3b.
9. **Cut load** (B7): move training, decode cost, rubric b and the ladder to the appendix; quote one number per claim; use the freed space for items 1 and 6.
10. **Mechanics:** remove the "round-2"/"revision" language, make Tables 6, 7, 25 and 27 legible, fix the Table 5 caption, fix the p. 23 float spacing, and add the MT reference-bias citation.

Items 4-10 are text and figure work. With those alone I would move to a 6. Items 1-3 are what separate a careful 6 from a paper I would argue for at 8.
