# Round 4 review: "Reference Answers Mislead LLM Judges When Many Answers Are Valid"

Reviewer role: senior AC, ICLR 2027. Read from the frozen PDF (30 pp.; main text pp. 1-7), with LaTeX sources, `registration_round4.md`, and `papers/analysis/*.json` used to check numbers.

## Summary

The paper shows that when a question has several correct answers, LLM judges given one of them as a "trusted reference" grade agreement with it. Rotating the reference to another correct answer moves the score of byte-identical text by 2.7 to 5.4 points (Qwen2.5-7B, phi-4, Sonnet 5), while a placebo class that matches neither reference stays flat. The authors argue the judge compares final values (words survive; an expression or a masked worked solution does not). They report that the reference damages separation of non-matching correct answers on both pools tested, but hurts overall grading and selection only where the blind judge already verifies well. They then test extended thinking, instructions, and a blind-then-reveal protocol, and score 147 registered predictions in a ledger. The core rotation result is clean and convincing. The moderator claim, the thinking claim, the headline selection number, and the decision table are all stronger than their evidence. The main text also relies on numbers that are either appendix-only or computed with a different scorer than the tables it cites.

## Scores

- **Overall:** 5 (marginally below the acceptance threshold)
- **Presentation:** 3
- **Soundness:** 2. The rotation result alone would earn a 4; the moderator, thinking, and mitigation claims pull it down.
- **Contribution:** 2
- **Confidence:** 4
- **Champion at 8+?** No. I would champion it if the "blind verification decides the overall cost" claim survived the two checks in Must-fix 1 (MACE restricted to k>1, and a within-pool split-half analysis), if a frontier judge with thinking on were run through the API on the rotation and MACE tests, and if every main-text number matched a table computed with the same scorer.

## Strengths

- The central manipulation is the right experiment. Candidates stay byte-identical, only the reference moves among correct answers, and the placebo class barely moves (+0.12, +0.30, +0.04). Figure 1b makes the case in one glance.
- The effect is shown not to come from the score estimator: expected score, exact two-token estimator, and greedy integer all agree (Table 34). It also survives the verbatim MT-Bench template, two frontier APIs, and 11 judges.
- The mechanism probes (numeral, words, "30+1", worked solution visible or masked) are cheap, well chosen, and informative.
- Registration practice is unusually honest. Falsified predictions, a checker bug, misaligned MATH-500 files, a scorer defect fixed by pre-specified rescoring, and an excluded contaminated CLI run are all disclosed.
- Section titles state claims, the abstract is concrete, and the prose is plain.

## Must-fix before submission (ranked)

### 1. The moderator claim, "grading overall depends on blind verification", is confounded with how many questions have a single answer

**Where it appears:** abstract sentences 4-5; contribution bullet 3; Sec. 5 paragraph title "Grading overall depends on blind verification."; Table 1 rows 3-4; Conclusion ("Whether the distortion makes grading and selection worse overall depends on how well the judge verifies without the reference").

**What is wrong:** the MACE arm, where the reference helps, is largely a single-answer effect.
- MACE's overall AUROC gain (+0.07, Table 37) is computed over all 133 tasks. That includes the 34 k=1 tasks, where every correct answer matches the reference and the reference can only help. The non-matching AUROC uses 91 tasks (`r4_results.json`, `grading/mace/G_all` n=133 vs `G_nm` n=91).
- Selection shows the same split. The reference adds +29.4 points at k=1 but only +2.0 [−5.1, +9.1] at k>1 (Table 33; Sec. 5 itself says "almost entirely on single-answer questions").
- The contrast "high blind AUROC hurts, low blind AUROC helps" is also:
  - perfectly confounded with constructed arithmetic vs. natural factual tasks;
  - partly mechanical, because a pool at 0.87 has less room to improve than one at 0.73;
  - resting on two pools per side and one pre-specified judge (phi-4 is post hoc).
- Your own Limitations admit this ("rests on one natural and two constructed pools, measured with one judge"). Yet the claim is still the paper's third contribution bullet and a section title.

**Fix, in two parts:**
- **(a)** Report overall AUROC and selection change on MACE restricted to k>1, for both judges, in Table 37 and Figure 3.
- **(b)** Within the k-pool and within MACE, estimate per-task blind AUROC on half of each task's samples and the referenced-minus-blind change on the other half, then show the relationship. If both analyses hold, keep the claim.

If they do not, replace abstract sentences 4-5 with:

> "On our constructed arithmetic tasks, where the judge verifies well without a reference, overall AUROC falls by 0.22 and best-of-64 accuracy on multi-answer tasks falls by 9 to 36 points across four judges. On MACE, the reference raises overall grading, almost entirely through its single-answer questions."

Retitle the Sec. 5 paragraph to "Overall grading: worse on constructed pools, better on MACE". Demote the moderator to a hypothesis in the Conclusion.

### 2. The thinking claim overstates the data and is partly a ceiling effect

**Where it appears:** abstract ("extended thinking removes it on arithmetic tasks but not on factual questions"); bullet 4; Figure 4 title; Sec. 6 "Verify when you can."; Table 1 row 5; Conclusion ("replaces that comparison with verification only where the answer can be checked by reasoning").

**What is wrong:**
- **"Not on factual questions" misreports the data.** Thinking cuts the factual margin increase from +6.16 to +3.62 (−41%) and from +7.07 to +3.13 (−56%). In absolute points, thinking removes more anchoring on factual questions than on arithmetic.
- **The arithmetic baseline was already small.** With thinking off, Qwen3-8B's rotation loss is −0.69, against −5.41 for Qwen2.5-7B.
- **The arithmetic result sits at the scale ceiling.** Valid rotation samples receive 10 in 99.8% of referenced and 96.2% of blind thinking-on replies (Appendix C and N). "Removes" therefore cannot be separated from "no room to move". Your own appendix concedes this ("leaves no room for a reference to move them").
- **"Verify less well blind" rests on a small gap.** With thinking on, blind AUROC is 0.86 vs 0.80 (8B) and 0.86 vs 0.81 (14B), with overlapping intervals.
- **The recommendation has no selection evidence.** The thinking judge still loses best-of-16 accuracy with the reference: −5.8 [−11.4, −1.8] at k=1 and −3.7 [−7.5, 0.0] at k>1 (Table 7). The ledger marks its registered selection prediction "falsified".
- **The one frontier thinking arm has no data.** It was stopped by "the subscription's monthly usage limit" (Appendix N). That experiment decides whether practitioners should care.

**Fix:**
- Abstract: "In two Qwen3 models, extended thinking removes the effect on arithmetic tasks, where their scores sit at the ceiling, and roughly halves it on factual questions."
- Figure 4 title: "Extended thinking removes the effect on arithmetic tasks and halves it on factual questions."
- Table 1 row 5: delete it, or change the evidence cell to "Rotation effect removed on arithmetic; no selection benefit measured (Table 7)."
- Run Sonnet 5 with extended thinking through the API on the 60-task rotation subsample and the MACE margin before submission.

### 3. The headline selection loss, "up to 35.9 points", is the most extreme cell, and the same contrast appears as two different numbers

**Where it appears:** abstract; Sec. 5 "Selection."; Table 1 row 3; Sec. 6 "Blind, then reveal." (30.8).

**What is wrong:**
- **35.9 is one cell.** It is Qwen2.5-7B on 39 k-pool tasks at k>1. On the preregistered replication population, the same judge loses −4.8 [−15.2, +5.7], an interval that includes zero.
- **Part of the loss is not about multiple answers.** The same judge loses 21.4 points at k=1, where the reference is the only correct answer (Table 35). The multi-answer-specific loss is about 14.5 points, and its interval is never reported.
- **This also contradicts Table 1 row 2**, which says "Few correct answers differ from the reference → Reference".
- **The main text gives two values for the same contrast.** It says "k>1 accuracy by up to 35.9 points" (exact scorer), then "30.8 for the plain reference" (original scorer, Table 26), without saying why.

**Fix:**
- Abstract: "best-of-64 accuracy on multi-answer constructed tasks falls by 9 to 36 points across four open judges (all intervals exclude zero), though Qwen2.5-7B also loses 21 points when the reference is the only answer."
- Report the k>1 minus k=1 step with intervals for each judge.
- Rescore blind-then-reveal with the exact estimator so Table 26 and Sec. 5 agree. Failing that, write "(original scorer; 35.9 under the exact scorer)" at the 30.8.

### 4. Table 1, the decision table, is not actionable and parts of it are unsupported

**What is wrong:**
- **No usable threshold.** "High" and "low" blind AUROC are undefined, and the caption admits "we cannot set a threshold between them." A practitioner at 0.80 gets no answer.
- **"Few" and "many" are undefined.**
- **"Both measurable on a few dozen labeled candidates" (caption) is unsupported.**
  - Per-task AUROC needs many candidates per task, with both classes present. Your intervals come from 93 to 133 tasks × 64 samples.
  - Nothing shows that a few dozen candidates can tell 0.87 from 0.73.
- **The test is circular.** Measuring "how often correct answers differ from the reference" requires knowing the full answer set. That is a checker, and row 1 then says no judge is needed. Row 4, "auditing correct answers that differ from it", has the same problem.
- **Row 2 is contradicted** by the k-pool at k=1 (Must-fix 3).
- **Row 5 is unsupported** (Must-fix 2).
- **The rows overlap.** Row 5 cuts across rows 3-4.

**Fix:**
- Rebuild the table as a 2×2 grid: correct answers rarely vs often differ, crossed with blind AUROC ≥0.85 vs ≤0.75. Put the measured pools in their cells and write "untested" in between.
- Bootstrap from your own data how many labeled tasks are needed to tell 0.87 from 0.73 at 95%, and put that number in the caption in place of "a few dozen".
- Say how practitioners estimate the share of differing answers without a checker, for example "a sample of 50 questions audited by hand for alternative answers".

### 5. The distance result contradicts your own registered test

**Where:** Sec. 4 ("Among correct answers that differ from the reference, being numerically close to it does not help (Appendix I)"), under a PRE mark; Appendix I ("the penalty does not grow with numeric distance from it, for either judge").

**What is wrong:** the ledger (Table 3, "Distance gradient") records the registered prediction "score falls with distance from the reference" as **confirmed** for both judges. `distance_gradient.json` gives a non-matching slope of −37.4 [−79.3, −5.9] for Qwen2.5-7B and −28.2 [−70.5, −2.4] for phi-4. The "no effect" reading comes from the tercile prediction, which was falsified, and from your note that "the estimator is dominated by a few tasks." Stating the opposite of a confirmed registered outcome under a PRE label, without saying so, is exactly what a preregistration ledger is supposed to prevent.

**Fix:** "The registered slope test found scores of non-matching correct answers falling with distance from the reference, but a few tasks drive it and near, middle, and far thirds score alike (Appendix I), so we do not read closeness as mattering."

### 6. Registration labels and the ledger summary overstate confirmatory weight

**What is wrong:**
- **(a) PRE is defined as "before the data existed", but some PRE results were already known.** P-R4A3, the k-pool accuracy loss behind 35.9, was registered after the same contrast had been observed under the original scorer (Table 8: −30.8, −17.9, −17.9, −9.0). The same holds for the rotation rescoring. These are pre-specified re-analyses with known direction, not predictions. Mark them differently, for example "RE", or say it once in Sec. 1.
- **(b) Paragraph-final marks cover mixed content.**
  - Sec. 3: "+5.27 for Qwen2.5-7B (96% of samples kept) … PRE". The exact-estimator filter is post hoc (`r4_posthoc_results.json`). The registered filter gives +4.99 with 91% kept (Table 4 caption).
  - Sec. 5 "Selection.": the paragraph ends in PRE but contains the post hoc MACE-by-k readout (+29.4, listed as post hoc in `registration_round4.md`).
  - Sec. 5 "Grading.": "0.4% to 28.1% … PH" is the registered P-R4A4 and should be PRE. Only "68.9% at 5 or below" is post hoc.
  - Figure 3b's row label "Replication (prereg.)" sits on an accuracy readout that Limitations calls post hoc.
- **(c) The ledger summary undercounts failures.** "including the 25 that were not confirmed or were falsified" implies about 120 successes. The ledger has 80 of 147 confirmed (54%), plus 16 split verdicts, 18 not evaluable, 5 not scored, and 3 excluded.

**Replacement for (c):**

> "Appendix B scores all 147 registered predictions: 80 confirmed, 25 not confirmed or falsified, 16 split across judges, and 26 not evaluable, not scored, or excluded."

### 7. Failures that bear on main-text claims are not disclosed where the claims are made

- **Blind-then-reveal (Sec. 6, abstract):**
  - All three registered MACE predictions (reference lowers k>1 accuracy; blind-then-reveal beats the reference; blind-then-reveal at least as accurate over the natural mix) failed for both judges (Table 33). The main text never says so.
  - In accuracy units, blind-then-reveal costs phi-4 −15.4 [−28, −3] points against blind (Table 8), while the text says it "removes the preregistered inflation" (+0.16). The registered endpoint and the practical endpoint disagree, and the reader deserves to know.
  - Add: "Its registered test on MACE failed for both judges (Appendix N), and for phi-4 it removes inflation but still costs 15 points of accuracy against blind judging."
- **Mistral-7B as confirming evidence.** Sec. 5 counts Mistral-7B among judges "all with intervals that exclude zero". Appendix M calls Mistral's inflation result "a resolution artifact": 11 distinct score values, and a third of blind replies contain no score. Drop it from the main-text evidence or flag it in the same sentence.
- **Figure 2b.** It carries PRE and a monotone "shrinks" title, yet:
  - the registered program-format prediction was split (Qwen2.5-7B falsified);
  - the pair and JSON margins were not evaluable (7 and 1 tasks);
  - the checker had a bug.
- **Same-sentence rule.** Put each failure in the same sentence as the claim it qualifies, not only in Table 3.

### 8. Figure 2b does not earn half a main figure, its caption is inaccurate, and the central claim has no figure

**What is wrong:**
- The text itself says panel b is confounded ("the two explanations are confounded"), and Must-fix 7 lists its other problems.
- The caption says "phi-4's program value uses checker labels corrected after registration". Appendix K says both judges' program values changed: Qwen2.5-7B from +0.27 to +0.13, phi-4 from −0.06 to −0.37. The caption is therefore wrong.
- The paper's third contribution, moderation by blind AUROC, has no figure. Figure 3b never shows blind AUROC, so readers cannot see the moderator.

**Fix:** move panel 2b to Appendix K and correct the caption to "both judges' program values use corrected checker labels". In its place, add a scatter:
- x axis: blind AUROC;
- y axis: referenced-minus-blind change in overall AUROC, with best-of-64 change as a second panel;
- one marker per pool × judge, split into k=1 and k>1.

That figure would show the claim and its n at the same time.

### 9. Too many metrics, and a key one is undefined in the main text

**What is wrong:**
- The main text makes readers hold nine quantities:
  - rotation change;
  - false-rejection rate;
  - per-task AUROC (three variants);
  - best-of-64 accuracy;
  - inflation (pool SDs);
  - added inflation;
  - anchoring margin;
  - referenced-minus-blind anchoring margin;
  - margin increase.
- "Anchoring margin" drives Figure 2a, Figure 4b, Sec. 6 and Sec. 4, but Sec. 2 "Measurements" never defines it. The definition appears only inside the Figure 2 caption.
- Figure 2a (margin) and Figure 4b ("margin increase", which is referenced minus blind) are different quantities with near-identical names.
- "the pass-rate band used for selection" (Sec. 2) is never given; the [0.2, 0.8] band appears only in Appendix A.

**Fix:**
- Add to Measurements: "The *anchoring margin* is the mean score of correct answers that match the reference minus that of correct answers that do not; the *added margin* is its referenced-minus-blind difference."
- Rename the Figure 4b axis to "added margin (points)".
- State the band: "(pool pass rate between 0.2 and 0.8)".
- Convert the Sec. 6 blind-then-reveal inflation numbers to accuracy (Table 8 already has them), so that inflation appears in the main text only where the OSF endpoint is named.

### 10. Main-text numbers that match no table, or a table from another scorer

| Main-text number | Location | Problem |
|---|---|---|
| "+5.27 for Qwen2.5-7B (96% of samples kept)" | Sec. 3 | The only printed version is Table 4's caption: +4.99, 91% kept |
| "+29.4 points for Qwen2.5-7B at k=1" | Sec. 5 | Tables 17 and 33 say +32.4; the exact-scorer value is in no table |
| "(68.9% at 5 or below)"; "explanations average 259 tokens" | Sec. 5; Sec. 6 | In no table or appendix text |
| "gains 5.25 … loses 5.41" | Sec. 3 | Cites "All twelve pre-specified cells … Appendix C", but Table 4 there shows +4.97 / −5.04 (original scorer) with no note |
| "0.4% to 28.1%" | Sec. 5 | Table 9 says "0.4% → 28.0%" |
| AUROC changes of "0.22" and "0.07" | Sec. 5 | Figure 3a's labels (0.87→0.66, 0.73→0.81) imply −0.21 and +0.08 |
| k-pool losses for four judges | Sec. 5 | Omits phi-4 (−20.5 [−36, −5], Table 8), one of the two main judges, though Figure 3b plots it |

**Fix:**
- Add the exact-scorer values to Tables 4, 9, 17 and 33, or add one "main-text numbers" table in Appendix O.
- Print the AUROC deltas in Figure 3a, or give two decimals of the unrounded values.
- Add phi-4 to the k-pool sentence.

## Should-fix (ranked)

### 1. Name the strongest alternative explanation: the prompt implies a unique answer

- **The problem:** rubric a says "a reference answer known to be correct", under the heading "Reference answer (trusted)". A careful grader may reasonably infer that the question has one answer. Sec. 3's "charitable reading" refutes a weaker version ("the reference taught it").
- **The filter test is weak:** the blind-accepted filter keeps 91-98% of samples, so it has almost no power to separate hypotheses.
- **The best evidence is in the wrong section:** the instruction experiment in Sec. 6. It fails for Qwen2.5-7B (ledger: falsified) and shrinks Sonnet 5 only from 3.00 to 2.08.

**Fix:**
- In Sec. 3: "A second reading is that the prompt implies a unique answer. Telling the judge that other correct answers deserve full credit does not remove the effect for Qwen2.5-7B, and only shrinks it for Sonnet 5 (Sec. 6)."
- Report the loss side under the filter as well, plus a stricter filter (blind score ≥9).

### 2. Use the two free pages

- **The problem:** the main text ends on page 7 of 9, while Sec. 6's hedge claim depends on Table 26 in Appendix M and the grading claims depend on Table 37 on page 30.
- **Fix:** bring Table 26 and Table 37 into the main text, plus a five-line ledger summary (confirmed, split, failed, not evaluable, by study).

### 3. Missing appendix pointers

- **The problem:** the main text never cites four appendices that hold its evidence.
  - Appendix J holds Table 20, the data behind Figure 2a. Sec. 4 cites I and K instead.
  - Appendix N holds Tables 32 and 38, the data behind Figure 4.
  - Appendix D holds Tables 8 and 9, the source of phi-4's "[−19.1, −4.8]".
  - Appendix F is never cited.
- **Fix:** add "(Table 20)" to Sec. 4, "(Tables 32 and 38)" to Sec. 6, and "(Table 9)" to Sec. 5.

### 4. Sec. 4 and Appendix J contradict each other on "30+1"

- **The problem:** Sec. 4 says "Writing it as '30+1' removes most of it". Appendix J says "'30+1' … shrank the margin only partly."
- **Fix:** use numbers in both places: "cuts the margin by 94% for Qwen2.5-7B and 77% for phi-4 (Table 20)".

### 5. The title overclaims against the paper's only natural multi-answer benchmark

- **The problem:** on MACE the reference improves overall grading (+0.07) and selection (+9.8 overall). "Mislead" is fully supported only for non-matching correct answers.
- **Fix:** "Reference Answers Bias LLM Judges Against Other Correct Answers".

### 6. The paper does not show the problem matters in practice

- **Weak prevalence:** the audit finds 0.0% of MATH-500 and 2.5% of GSM8K and DeepScaleR items with several correct answers.
- **Overgeneralized claim:** the 18.5% comes from NQ-open, which already ships multiple references, yet "Curated math benchmarks mostly satisfy that; other data do not" generalizes from that one dataset.
- **Unvalidated labels:** the audit labels are from one model family, not checked by humans.
- **No downstream result:** the one downstream experiment (DPO) failed its manipulation checks.

**Fix:** either measure prevalence where multi-answer tasks are common (construction or example requests in RL math data, open-ended code, agentic benchmarks), or show one consequence: a benchmark ranking flip, or a published grader prompt misjudging items in the wild. If neither is possible, soften "other data do not" to "open-domain QA often does not (18.5% of NQ-open)".

### 7. MACE label noise favours the reference, on the pool that carries the "reference helps" result

- **The problem:** Appendix G admits 2.3% (River) and 8.1% (Language) rates of valid answers missing from the shipped lists. An unlisted correct answer is labeled wrong. The referenced judge penalizes it for not matching, and the metric counts that as a correct rejection. This inflates the MACE overall-AUROC gain and the selection gain.
- **Fix:** add a sensitivity analysis that drops candidates flagged by the completeness auditor or relabels them with a second checker.

### 8. Figure consistency and label collisions

- **Marker meaning changes between figures:**
  - Hollow means phi-4 in Figure 3b but "thinking on" in Figure 4a/b.
  - Black marks judges in Figure 3b but thinking state in Figure 4b.
  - Figure 3b mixes estimators on one axis: Qwen2.5-7B exact, phi-4 original.
- **Label collisions:**
  - Figure 4b's value labels (+3.6, +0.3, −0.1, +3.1) collide with error-bar caps.
  - Figure 2a/b legends sit inside the axes next to data at the zero line.
  - Figure 5a's "blind" text overlaps the Qwen2.5-14B marker at k=1.
- **Fix:**
  - Reserve hollow/filled for one contrast across the paper.
  - Move legends outside the axes.
  - Put the Figure 4b values in the caption, or offset them horizontally.
  - State the estimator per marker in the Figure 3b legend.

### 9. The "shrinks" claims for Sonnet 5 and GPT-4.1 prompts need paired intervals

- **The problem:** Sec. 6 says Sonnet 5 goes "+3.00 to +2.08 and +2.60" and GPT-4.1 "+0.99 to +0.46 and +0.59". The marginal intervals in Table 18 overlap heavily ([+2.02, +4.02] vs [+1.14, +3.14]).
- **Fix:** give the paired difference with its interval in the text.

### 10. Limitations: incomplete and one garbled sentence

- **The scorer bullet understates.** "Several appendix analyses use the earlier scorer" is incomplete: Sec. 6's hedge numbers (Table 26), Sec. 5's "84.4% to 93.8%" (Table 17), and phi-4's selection numbers also use it. Say so.
- **Garbled sentence.** "With a fixed seed, the registered blind-then-reveal contrast for Mistral-7B excludes zero in 11 of 20 seeds" → "The registered blind-then-reveal contrast for Mistral-7B used one bootstrap seed; across 20 seeds its interval excludes zero in 11."
- **Missing items:**
  - one candidate generator (Llama-3.1-8B) for most pools;
  - MACE label noise (Should-fix 7);
  - LLM-only prevalence labels;
  - reference wording that implies uniqueness.

### 11. The effect shrinks with judge strength, and the paper does not address this

- **The pattern:** Table 5 shows margins of about 9.5 at 1.5B and 3.1 at 14B. On the k-pool, GPT-4.1's margin is +0.99 and Sonnet 5's is +3.00, against +5.17 for Qwen2.5-7B.
- **Why it matters:** the main judges are 7B and 14B open models, so readers will ask whether this is a weak-judge effect.
- **Fix:** one small panel of margin against blind AUROC or model size, with frontier judges marked, and two sentences of discussion.

### 12. Density and machine-prose tells

- **Number density:** the Sec. 5 "Selection." paragraph carries about 25 numbers across six sentences.
- **Verbal tics:**
  - "X against Y" meaning "versus" appears 16 times in `main.tex`.
  - Clipped wrap-up clauses recur: "which may explain it", "so the displayed number does the work", "No protocol wins everywhere".
- **Lab-notebook detail in the appendix:** "subscription login", "the subscription's monthly usage limit", "a git status listing recent commit messages that name the anchoring hypothesis", "provider batch failure". In the main text, "the Claude command-line tool with its system prompt replaced by our rubric" invites questions the paper does not need.
- **Fix:**
  - Cap each paragraph at about 8 numbers and move the rest to tables.
  - Use "versus" or "compared with".
  - Replace the operational detail with "a second interface with the default system prompt replaced; this run was not completed".

## Nits

- The ICLR template requires "The table number and title always appear before the table." Table 3 complies; Tables 1, 2 and 4-38 put captions below.
- "valid" (figures, appendix, Figure 1a labels) vs "correct" (main text): pick one.
- Table 1 "Check membership": write "Check against the full answer set".
- MACE is never expanded. RewardBench-2 appears in small caps.
- Figure 5b x-axis "Qwen-7B" vs "Qwen2.5-7B" everywhere else.
- Abstract, "by 3.6 points under the verbatim MT-Bench template": name the judge (Qwen2.5-7B) and the direction ("lowers ... by 3.6 points").
- Abstract, "falls from 0.87 to 0.60 on our constructed tasks": this is one pool; write "on our replication pool".
- Figure 1b: the placebo bars lack value labels; the values sit in the caption instead. Label them like the other bars or drop all bar labels.
- Figure 3b row label "Replication (prereg.)": drop "(prereg.)".
- Tables 8 and 35 print intervals such as "[−43, +0]" and "[+0, +0]". State whether an upper bound of exactly zero comes from ties in the bootstrap.
- Appendix D, titled "Selection: accuracy by pool and by k", also holds inflation Tables 10-13.
- Pages 17, 19, 26 and 29 are mostly blank. Tables 11-13 float with half-page gaps.
- Appendix order does not follow first citation (Appendix O is cited in Sec. 2).
- The Conclusion's last clause ("that check is better than any judge") is untested: your labels come from those programs. Write "no judge is needed", as in Sec. 6.
- The Intro hook uses Sonnet 5 with thinking off and a post hoc readout. Given Sec. 6, add "(with extended thinking off)" to the Figure 1 title, or show the thinking-on bar once it exists.
- Related work is missing:
  - Freitag et al. (2020), "BLEU might be guilty but references are not innocent", the canonical single-reference bias result in NLG evaluation;
  - Thakur et al. (2024), "Judging the Judges".
- Sec. 3, "(96% of samples kept)": say what is kept ("of correct samples scored ≥7 blind").

## Questions for authors (answers could change my score)

1. On MACE restricted to k>1 tasks, what is the referenced-minus-blind change in overall per-task AUROC for Qwen2.5-7B and phi-4, with intervals? If it is zero or negative, the moderator claim reduces to "single-answer questions benefit".
2. Within the k-pool and within MACE, does the per-task change in overall AUROC track per-task blind AUROC when the two are estimated on disjoint halves of the samples?
3. What does a frontier judge with extended thinking on (Sonnet 5 via the API is enough) give on the 60-task rotation subsample and on the MACE margin?
4. For Qwen2.5-7B, is the k>1 minus k=1 selection step (about −14.5 points) distinguishable from zero? If not, how much of the k-pool loss is specific to multiple answers?
5. How many labeled tasks, and how many candidates per task, are needed to tell blind AUROC 0.87 from 0.73 at 95%, given your per-task variance? This decides whether Table 1 can be used.
6. Which tasks drive the confirmed negative distance slope (−37.4 [−79.3, −5.9])? Does the sign survive removing them?
