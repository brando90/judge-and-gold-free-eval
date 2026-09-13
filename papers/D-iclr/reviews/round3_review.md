# Review: "Reference Answers Mislead LLM Judges When Many Answers Are Valid" (ICLR 2027 submission, round 3 PDF)

## Summary

The paper asks what happens when an LLM judge is given one correct reference answer for a question that has several correct answers. Its cleanest experiment keeps each candidate's text fixed and changes which valid answer is the reference (the paper calls this "rotation"). Text that now matches the reference gains 3 to 5 points out of 10 and text that no longer matches loses about as much, across two open judges, Claude Sonnet 5, and the MT-Bench template. The paper then attempts four more things:

- a moderator claim that extended thinking protects only where the judge can verify;
- a mechanism claim that the judge does an equality check against a readable answer;
- a regime-dependent account of best-of-n accuracy (worse on constructed arithmetic pools, better on MATH-500 and on the natural MACE pool);
- a two-call blind-then-reveal mitigation.

Everything is tied to a preregistration ledger that honestly reports many failed predictions.

## Scores

- **Overall:** 5 (marginally below the acceptance threshold)
- **Presentation:** 2
- **Soundness:** 3 (the core rotation result is strong; several headline claims go past their evidence)
- **Contribution:** 2
- **Confidence:** 4
- **Would I champion this at 8+?** No. The paper has one clean result (rotation distorts scores) and wraps it in claims about selection, reasoning, and mechanism that its own appendix partly contradicts. Five changes would get me there:
  1. Re-centre the paper on score distortion and how it affects grading, with a grading-accuracy result on natural multi-answer data.
  2. Measure "blind judge verifies well" the same way in every pool, so that Table 1 becomes a tested rule.
  3. Put the preregistered replication-pool accuracy and the k=1 results in the main text.
  4. Scope the reasoning claim to what one model on two task types shows.
  5. Disclose and control the MATH-500 reference-solution confound.

## Strengths

- **Rotation design.** Byte-identical candidates, a valid-to-valid reference swap, and a "matches neither" control (Table 4). This isolates the effect better than prior wrong-reference studies. The blind-accepted filter answers the obvious "the reference taught the judge" objection.
- **Breadth.** 9+ open judges, two frontier API judges, five task families, a third-party combinatorial pilot (App O), and code.
- **Honest ledger.** Appendix B reports 20+ falsified predictions, including ones that hurt the story (the MACE accuracy reversal, blind-then-reveal on MATH-500, DPO attribution). This is rare and valuable.
- **Useful negative results.** MACE, where the reference helps; the resolution screen that catches broken judges (App M).
- **A good hook.** Divisors of 91 in the first paragraph of the introduction, and the main text fits in 8 pages.

---

## Must-fix before submission (ranked)

### 1. The headline story and the data disagree on what the finding is (Title, Abstract, Sec. 6, Sec. 7 "Verify when you can", Conclusion)

The accuracy harm is shown only on constructed arithmetic pools. That is exactly the setting where the paper's own first recommendation applies: "When a program can check validity, no judge is needed" (Sec. 7).

On the one natural multi-answer pool (MACE) the reference *raises* accuracy. On MACE's multi-answer tasks the change is +2.0 [−5.1, +9.1] and +6.1 [−1.0, +13.1]. The abstract's "accuracy rises" on MACE comes from the k=1 tasks (+32.4, +26.5; Table 31).

So the practical selection message is "keep using the reference on natural data." What survives everywhere is **score distortion**:

- MACE anchoring margins of +6.44 and +5.86 (App G);
- Sonnet 5 at +5.29;
- +44.3 points of false rejections for Qwen3-8B with thinking off (Table 30).

Score distortion matters for grading and reward, but the paper never reports the most common use: **grading accuracy**, meaning agreement of a thresholded score with oracle validity, as used when reporting a model's benchmark accuracy under a judge.

**Fix:**
- Add a main-text grading result on MACE: per-sample accuracy or AUROC blind vs referenced, split by matching vs non-matching valid answers. Add the NQ-open multi-answer items from App E if at all possible.
- Lead the abstract with distortion and grading. Present selection as regime-dependent and secondary.
- Suggested abstract sentence: "On MACE, a natural benchmark of factual questions with several correct answers, the reference still leaves correct non-matching answers scored X points lower, yet best-of-64 accuracy does not fall, because these judges verify factual answers poorly without it."

### 2. The decision variable in Table 1 is never measured, and the numbers the paper does report contradict it (Sec. 6 last paragraph, Table 1, Conclusion)

The paper's account is that accuracy is lost "when a blind judge can already verify." MACE is labelled the "verifies poorly" regime on the basis of a single statistic (blind score–validity correlation 0.36 / 0.48). That statistic is not reported for any other pool.

Blind selection accuracy, the one metric given across pools, orders them the wrong way:

| Pool | Qwen2.5-7B | phi-4 | Source |
|---|---|---|---|
| MACE, overall | 82.0% | 84.2% | Table 31 |
| MACE, k>1 | 86.9% | 87.9% | Table 31 |
| k-pool (arithmetic) | 76.7% | 85.0% | Table 29 |

A simpler rival explanation is not ruled out: MACE has k ≤ 6, while the k-pool's large losses sit at k=16 (−71.4, −85.7 on 7 tasks). At k=4 the k-pool losses are −11.1 [−33, 0] and 0.0 (Table 8).

**Fix:**
- Report one verification metric (blind AUROC of score vs validity) for the replication pool, the k-pool, MATH-500, and MACE, in a main-text table.
- Break Table 31 down by k (2 / 4 / 6), and compare with k-pool accuracy at k ≤ 4.
- If the ordering does not hold, drop the "verifies well / poorly" framing from Sec. 6, Table 1, and the Conclusion.
- If it holds, give Table 1 a threshold and an estimation recipe, as its caption promises ("both can be estimated on a small labeled sample").

### 3. The preregistered pool's accuracy and the k=1 results are left out of the main text; one sentence is false (Abstract, bullet 4, Sec. 6 "Constructed arithmetic tasks", Fig. 4a caption)

**(a) The abstract's range comes from the smaller, post hoc pool.** "The reference lowers accuracy by 9 to 31 points" comes from the post hoc k-pool (39 tasks). The preregistered 105-task replication pool gives −7.6 [−19.1, +3.8] for Qwen2.5-7B, with an interval that includes zero, and −11.4 for phi-4 (Table 9). Table 9 is not cited anywhere in the main text.

**(b) False sentence.** Sec. 6 says: "no judge's loss is distinguishable from zero at k=2". Mistral-7B is −11.0 [−16, −4] at k=2 (Table 8).

**(c) The k=1 row contradicts "the reference helps on unique answers."** At k=1, where the reference is the only valid answer:

- Qwen2.5-7B: −21.4 [−43, 0]
- Mistral-7B: −10.3 [−15, −5]
- Qwen3-8B thinking judge: −5.8 [−11.4, −1.8] (Table 7)
- MT-Bench template: +16.6 [−1.5, +34.2]
- The preregistered k=1 benefit "did not appear" (Table 3, "partial").

Fig. 4a shows Qwen2.5-7B at about −21 at k=1, yet its caption title says the cost appears "as the number of valid answers grows."

**Fix:**
- Add the replication-pool accuracy row to Sec. 6 and change the abstract to: "lowers best-of-64 accuracy by 8 to 11 points on the preregistered pool and by 9 to 31 points (post hoc) on a pool with up to 16 valid answers per task".
- Replace the k=2 sentence with: "losses are small and imprecise at k=2 (one of five judges excludes zero) and large at k=16."
- Discuss the k=1 losses. The lure bonus in App I (invalid answers containing the reference text get +1.4 to +1.7) is a candidate explanation, so say so.

### 4. The reasoning claim goes beyond one model and two task types, and its figure shows a different story (Abstract, bullet 2, Sec. 4 title and body, Fig. 2, Table 1 row 2, Sec. 7)

Problems:

- **(a) The baseline effect is already small.** Qwen3-8B with thinking *off* barely anchors on arithmetic: −0.69 vs −5.04 for Qwen2.5-7B (Fig. 2a). "Removes the effect" removes a small effect. The big visual drop in Fig. 2a is between model families, not between thinking off and on.
- **(b) Thinking does help on factual questions.** On MACE it cuts the margin by 41% (6.16 → 3.62) and halves false rejections (44.3 → 21.6). "Reasoning helps only where the judge can verify" is contradicted by Table 30.
- **(c) "Can verify" is asserted, not measured.** No blind AUROC is given for Qwen3-8B on either task type.
- **(d) One model.** There is n=1 thinking model, and the frontier arm was not run.
- **(e) The short-explanation comparison is not like for like.** "A short explanation before the score does not help" compares −3.59 (MT-Bench, 1–10 scale, 879-sample subsample) with −5.04 (full pool, 0–10) with no test. On its face that is a 29% reduction.
- **(f) Fig. 2a puts incomparable score interfaces on one axis.** It mixes expected-score judges with sampled-integer judges (Qwen3-8B at temperature 0.6, the MT-Bench parse, Sonnet tool-call integers). App H calls exactly this comparison "not interpretable because this interface returns sampled integers while the open judges report expected scores."
- **(g) The token counts don't match the table.** "151 to 223 tokens" and "569 to 1,092 tokens" (Sec. 4, Sec. 7) do not match Table 30 (159 / 193 / 80 off; 569 / 1009 / 631 on).

**Fix:**
- Retitle Sec. 4 "Extended thinking removes anchoring on arithmetic and halves it on factual questions (one model)".
- Abstract: "In one open model (Qwen3-8B), turning on extended thinking removes the small anchoring it shows on arithmetic tasks and roughly halves its large anchoring on factual questions."
- Delete "A short explanation before the score does not help," or replace it with "A 259-token explanation under the MT-Bench template leaves most of the effect (−3.59 vs −5.04 score-only, different subsample)."
- Split Fig. 2a by score interface, or mark the sampled-integer rows.
- Fix the token numbers.
- Table 1 row 2 is circular ("The judge can check answers by reasoning"). Tie it to a measurement or remove it.

### 5. The MATH-500 "unique answers" evidence is confounded (Sec. 6 "Unique answers", Fig. 5b, Table 1 row 3, bullet 4)

According to the supplementary scoring code (`bon_judge.py`), the MATH-500 judge sees a full **"Reference solution (trusted)"**. The constructed pools show a bare answer ("Reference answer (trusted)"). App A mentions this only for the blind-then-reveal second call.

The MATH-500 pool also differs in:
- generator: Qwen2.5-7B, with Qwen2.5 judges, so the same family grades its own samples;
- domain and difficulty;
- blind accuracy: 55–68%.

The paper's own Sec. 5 shows that worked solutions behave differently from bare references. Meanwhile the controlled unique-answer test, the k-pool at k=1, shows no benefit or a loss (item 3). Yet Table 1 says "Answers are unique → Reference."

**Fix:**
- State in Sec. 2 and Sec. 6 that MATH-500 uses a reference *solution* and a same-family generator.
- Either rerun MATH-500 with a bare final-answer reference, or reword to: "On MATH-500, where the judge sees a full reference solution and blind judges pick a correct answer only 55–68% of the time, the reference raises accuracy by 27.6 to 43.8 points."
- Make Table 1 row 3 conditional on weak blind verification.

### 6. The headline effect sizes cannot be traced to the main text, and the range is selectively bounded (Abstract, bullet 1)

"moves its score by 2.5 to 6.3 points out of 10 for open judges, Claude Sonnet 5, and the MT-Bench prompt". Neither 2.5 nor 6.3 appears in the main text. They are rubric-b cells of Table 4 (+6.34 Qwen onto; −2.51 Sonnet off), while Fig. 1b and Sec. 3 report rubric a (2.66 to 5.04).

The range also leaves out a tested open judge under the same test (Qwen3-8B thinking off, −0.69; thinking on, +0.01) and the Ties ladder (up to 9.65, Table 5). "Open judges" here means two judges.

**Fix:** "moves its score by 2.7 to 5.0 points out of 10 under our main rubric for Qwen2.5-7B, phi-4, and Claude Sonnet 5 (3.6 under the verbatim MT-Bench template)". Use the same numbers in bullet 1.

### 7. The mechanism claim contradicts its own evidence (Abstract "cheap equality check against a readable answer", bullet 3, Sec. 5, Fig. 3 caption)

Sec. 5 concludes "We read this as a semantic equality check on a readable answer." The evidence:

- "thirty-one" keeps the effect. That fits a semantic check.
- "30+1", which means the same thing, kills it (+0.29 / +0.89). That is inconsistent with a *semantic* check. An 8B model can evaluate 30+1.
- The decode-cost result collapses at one step, but App J concedes that announcing the encoding may explain it.
- Masking the answer in a worked solution removes anchoring, which any account predicts.
- The integer→program attenuation is confounded with the number of distinct valid answers (median 2). The caption admits this; bullet 3 does not.
- The MBPP failure ("lowered inflation ... instead") was reinterpreted as support after the fact.

**Fix:**
- Replace the Sec. 5 conclusion with: "Judges behave as if they compare the candidate's final answer with a final value stated explicitly in the reference; the effect survives a change of surface form (words) but not a reference that must be evaluated (an expression) or that states no final value (masked)."
- Drop "semantic" and "cheap."
- In bullet 3, append "(confounded with fewer distinct valid answers)" to the program claim, or remove the program claim from the bullets.
- In the abstract, replace "The behavior resembles a cheap equality check against a readable answer." with "The effect needs an explicitly stated final value in the reference."

### 8. The CLI frontier judge may have seen the project's context, yet it counts as a confirmation (App H "CLI judge", App A "Scoring", Table 3 rows "Frontier CLI judge")

App H: "called `claude -p --model sonnet` from the project directory ... the command-line interface's default agent system prompt and project context were present." If that context described the hypothesis, this is contamination.

It is still scored "confirmed" twice in the ledger, and its 83.3% false-rejection figure is reported. Separately, App A says "The frontier Claude judge of Section 3 was called through a command-line interface." Sec. 3's primary Sonnet result is from the API, and its CLI replication used a replaced system prompt and an empty directory (App N). These are two different CLI runs described as one.

**Fix:**
- Drop the App H CLI run, or mark it "excluded: judge had project context" and remove its verdicts from the 46 / 24 / 10 count.
- Rewrite App A's Scoring sentence to name the App N configuration.

### 9. Table 1 is never referenced, sits inside Related Work, and cannot be acted on (Table 1, p. 7)

`tab:decide` is never cited. The float lands at the top of p. 7 inside Related Work, separated from Sec. 7.

The caption says "Two quantities decide the choice", but the table has five rows keyed on at least four conditions (checker exists, judge can reason, unique answers, blind verification). The rows overlap (a unique-answer task can also have a program checker). None has a threshold or measurement.

Missing options that the appendix tested:
- the any-valid-answer instruction, which works for phi-4 and 14B;
- several references, min(3, k) (App M).

**Fix:**
- Cite it at the end of Sec. 7 ("Table 1 summarizes") and force placement with `[t]` after Sec. 7.
- Rewrite it as a two-question flowchart with measurable conditions, e.g. "blind AUROC on 50 labeled items ≥ τ" and "share of correct answers that differ from the reference ≥ ρ", with the τ and ρ your data support (or state that you cannot set them).
- Add the instruction option with its judge dependence.

---

## Should-fix (ranked)

### 1. The open-judge "expected score" is not what App A describes (App A "Scoring"; supplementary `bon_judge.py`)

App A says "the probability-weighted mean over the tokens 0 to 10." The script does this instead:

```python
one_means = 10 if txt.startswith("10") else 1
```

and falls back to a parsed integer, or **5.0**, when score-token mass is below 0.25.

Qwen2.5, gemma-2, and Mistral tokenize "10" as "1","0". For them, all probability on "1" becomes 10 or 1 depending on the greedy output. The expected score therefore jumps at the greedy 9/10 boundary, which is where matching and non-matching valid answers separate. It probably does not create a 5-point rotation effect, but it can move margins, inflation, tie structure, and Table 8 accuracy. It may also explain part of Mistral's "11 distinct values."

**Fix:**
- Describe the estimator exactly.
- Rescore with P("1")·P("0" | "1") from a second forward step.
- Report how many scores used the 5.0 fallback.

### 2. Section order splits the argument (Secs. 4–7)

Sec. 4 (reasoning, a moderator and partial mitigation) comes before Sec. 5 (mechanism). Sec. 7 "Verify when you can" then repeats Sec. 4.

**Fix:** use the order phenomenon (3) → mechanism (4) → when it costs selection (5) → what to do: thinking judges, instructions, reveal (6). Put Table 1 at the end of the new Sec. 6.

### 3. Too many endpoints and units for a skimming reader (Sec. 2 "Measurements", Figs. 2–5)

The main text asks the reader to track all of these:

- rotation change (points)
- anchoring margin, referenced only (Fig. 3a)
- anchoring margin, referenced minus blind (Fig. 2b, same word)
- inflation in pool SDs
- "added inflation" (Fig. 3b)
- selection accuracy (points)
- false rejection (%)

Fig. 3 uses different units in its two panels. "Inflation" needs App A's permutation null before anyone can interpret it.

**Fix:**
- Use three main-text quantities: rotation change, false-rejection rate, selection accuracy.
- Keep inflation only where it is the preregistered endpoint, with one intuitive sentence ("1 SD means the chosen answer scores one standard deviation above other answers of the same correctness").
- Rename the Fig. 2b quantity "margin increase from the reference."

### 4. Prose is a list of numbers, and paired numbers are ambiguous

- Sec. 4 ¶2 has 13 numbers, Sec. 6 ¶1 about 18, Sec. 7 "Blind, then reveal" about 17.
- **Order flips between sentences.**
  - Sec. 5 names phi-4 first ("leaves phi-4's margin essentially unchanged (+3.68 against +3.79) and keeps about two-thirds of Qwen2.5-7B's"). The next sentence, "shrinks the margins to +0.29 and +0.89", is Qwen first, then phi-4 (Table 19).
  - Sec. 4 goes from off-then-on to "+3.62 with thinking on and +6.16 with it off", then "21.6 and 44.3" (on, off).
- **Machine-prose tells:** "Our findings, in the order of the paper:", "A charitable reading is that", "We read this as", "Three disclosures apply.", "which is what verification looks like".

**Fix:**
- Put the Sec. 5 and Sec. 7 comparisons in a compact main-text table (there is a free page).
- In prose, keep one number per claim and name the judge each time.
- Example rewrite of Sec. 5 ¶1: "Writing the reference in words keeps most of the effect; writing it as an expression or masking it in a worked solution removes most of it (Fig. 3a)."

### 5. Evidence labels: cluttered, inconsistent, and verdict rules undefined (throughout; Table 3; Sec. 1 last paragraph)

- **Many numbers carry no label.** Examples: Sec. 3 ¶2 first sentence; Sec. 3 ¶3; Sec. 5 ¶1.
- **Hard to read.** "+1.19SD[+1.02, +1.36]OSF" (Sec. 6).
- **Weak timestamps.** PRE rests on git commits, which reviewers will discount.
- **Verdicts are applied inconsistently.** "Falsified" is used when the interval still includes the predicted effect: "Reference lowers accuracy at k>1 (falsified, both judges)" with CI [−5.1, +9.1]. Elsewhere, similar cases are "not confirmed."
- **The summary sentence doesn't match the table.** App B says "46 confirmed, 24 falsified or failed, and 10 split, partial, inconclusive, not evaluable, or not scored." The table also uses "not confirmed" (2) and "not interpretable" (1), which that sentence does not name.

**Fix:**
- Label at paragraph or figure level.
- Define verdicts once: confirmed = CI excludes zero in the predicted direction; falsified = CI excludes the predicted effect; otherwise inconclusive. Re-score with that rule.
- Make the count use the table's vocabulary.
- Remove the unscored "Step-level rotation pilot" row.

### 6. Blind-then-reveal is beaten in every measured regime; argue for it as a hedge, and don't overstate its coverage (Sec. 7, Fig. 5, abstract last sentence)

It is beaten by blind judging on the k-pool for phi-4 and gemma (15.4 and 12.8 points below blind) and by the plain reference on MATH-500 and MACE. Its only case is worst-case regret across regimes, and the paper never computes that.

"On the k-pool it removes the preregistered inflation at k>1" holds for the two main judges only. For gemma-2-9b it goes from +1.43 to +1.23 (Table 26). The decomposition sentence ("+1.42 and +0.36") comes from a 58-task mixed population (Table 27) but sits next to 39-task k-pool numbers.

**Fix:**
- Add a small regret table: for each protocol, accuracy minus the best protocol in each pool; report the maximum.
- Add "(two of three judges; gemma-2-9b retains most of its inflation)".
- Name the population of the decomposition sentence.

### 7. Sec. 7 "Prompts help only some judges" relies on undefined pools and omits a fix the paper tested

- "Synthetic grid" is never defined in the main text (only in App A Table 2).
- The paragraph mixes synthetic-grid k=16 margins with k-pool Sonnet and GPT-4.1 margins.
- Showing several valid references (App M) is the first fix a practitioner would try, and it is absent from the main text.

**Fix:** define the pool in one clause, and add one sentence on several references.

### 8. The figure colour and marker grammar is inconsistent, and labels collide

- **Blue means different things.** "Reference shown" in Figs. 1a, 4b, 5, 6; "now matches it" in Fig. 1b; judge colour in Figs. 2 and 3.
- **Markers are reused.** Diamond is Qwen3-8B in Fig. 2a but Qwen2.5-14B in Figs. 4a and 5a.
- **Fig. 1b:** the grey "matches neither" bars, the key control, are invisible slivers with no value labels, and "now matches it" has an unclear "it".
- **Fig. 2a:** the "+0.01" label sits on the zero line.
- **Fig. 2b:** the y-axis runs to 10 for data ≤ 6.2.
- **Fig. 3a:** no legend (it is only in 3b). Tick "31" is one example value, not a condition name. The grey annotations "bare reference" and "worked solution, final answer" are unreadable at print size.
- **Fig. 4a:**
  - the orange "blind" label is overprinted by the light 14B markers at k=1–2;
  - the caption says only the bold judges have intervals, but a light series shows a large interval at k=4 (−67 to +22);
  - the three light series cannot be told apart.
- **Fig. 5a:** the "blind" label collides with the Mistral marker, and the arrows are too faint to read direction.
- **Panel letters** sit in inconsistent positions (Fig. 2a letter far from its title; Fig. 2b letter adjacent).

**Fix:**
- Reserve orange / blue / teal for blind / reference / reveal everywhere; use marker shape only for judge, with one fixed map.
- Label the control bars.
- Give Fig. 3a its own legend.
- Move in-axis labels off the data.

### 9. Fig. 4 bundles unrelated panels and repeats numbers

Fig. 4b (replication-pool false rejection) sits in a k-pool accuracy figure and repeats the Sonnet 4.9% → 26.2% already in the abstract, intro, and Fig. 1a.

**Fix:** move false rejection to Fig. 1 as panel (c), with all three judges. Make Fig. 4 accuracy-only, with the replication pool and the k=1 point visible.

### 10. The "scored 3 or below" false-rejection threshold is arbitrary (Sec. 2, Figs. 1 and 4, abstract)

Its meaning differs between expected-score judges and integer judges.

**Fix:** report robustness at ≤ 5 and a threshold-free measure (the drop in AUROC for non-matching valid vs invalid answers), or show the score distributions in the appendix.

### 11. The motivating prevalence figure is inflated and doesn't match the phenomenon (Sec. 1 ¶3)

- "30.0% of NQ-open questions" includes questions whose answer changed over time; the figure is 18.5% without them (App E).
- The multi-answer math items are underspecified or erroneous problems, not the "example / construction" questions the paper studies.
- The labels come from one LLM family with no human check.

**Fix:** "18.5% of NQ-open questions (30.0% counting answers that changed over time), by LLM annotation", and one clause noting that the math cases are mostly underspecified problems.

### 12. "Not fully deterministic" confirmatory analysis (Table 3, Judge coverage; Limitations)

A registered confirmation (Mistral-7B) flips in 3 of 8 reruns.

**Fix:** fix the seeds, report the seeded result, and remove the rerun language.

### 13. Unfinished-experiment language (Sec. 4 last sentence, Limitations "Reasoning", App N, Table 3)

"stopped by a usage limit" and "the subscription's monthly usage limit" read as incomplete work.

**Fix:** run the Sonnet thinking arm through the API with thinking enabled (the API judge already exists). Otherwise, state once in Limitations "we did not test extended thinking on a frontier judge" and delete the billing narrative.

### 14. A garden-path sentence ends Sec. 6

"The accuracy cost therefore appears when a blind judge can already verify and correct answers that differ from the reference are common; the distortion of scores appears throughout." It reads as "verify and correct [verb] answers."

**Fix:** "The accuracy cost appears when two conditions hold: the blind judge already verifies well, and many correct answers differ from the reference. The score distortion appears in every pool." (Subject to must-fix 2.)

### 15. Terminology drifts

- **Valid vs correct:** "valid", "correct", "oracle-valid", and "correct but non-matching" are used interchangeably. Pick "correct" in prose and define "valid set V" once.
- **Reference vs key:** "reference", "key" (Table 3: "picks collapse onto the key", "inflates like a key", "copies the key more"), and "answer on file" (Sec. 1). Use "reference".
- **Pool:** means both the task set and the 64 candidates ("pool standard deviations", "tie at its maximum per pool"). Use "candidate set" for the latter.
- **Undefined in the main text:**
  - "blind-first judge" (App L) should be "blind-then-reveal";
  - "validity gate" is used in Tables 8 and 31 before its definition in App M and is never defined in the main text;
  - "placebo" (Table 3) should be "matches neither";
  - "paraphrased rubrics" (Sec. 2) should be "two rubric wordings";
  - "k-subsample", "rotation subsample", and "16-sample subsample" (Fig. 2 caption) need defining.
- **Model names:** "Qwen-7B" in Fig. 4b should be "Qwen2.5-7B".

### 16. Appendix layout

- p. 17 has four floats separated by large vertical gaps.
- pp. 15 and 25 are half empty.
- Tables 24 and 26 are scriptsize and hard to read in print.
- Table 3 has its caption above while every other table has it below.
- The Table 2 caption refers to "The 37-task subset in the main text", but the main text never uses a 37-task subset; it appears only in App H.

**Fix:** use `[t]` / `[p]` placement instead of `[h]` + FloatBarrier, set a consistent caption position, and correct the Table 2 caption.

---

## Nits

- Fig. 1 caption: "Mean scores Claude Sonnet 5 (API, extended thinking off) gives oracle-valid answers" → "Mean score that Claude Sonnet 5 (API, extended thinking off) gives to correct answers".
- Sec. 6: "the same reference raises selection accuracy" on MATH-500. It is not the same reference; use "a reference".
- Sec. 7: "within the intervals" → "both intervals include zero".
- Decimal precision is inconsistent: −0.694, +0.011, +3.618 (Sec. 4, Table 6) vs two decimals elsewhere. Use two.
- Sec. 4: "gives 10/10" vs "a score of 10" elsewhere.
- Fig. 2 caption: "hollow marker: thinking on", but Fig. 2b uses hollow *bars*.
- "+1.19SD" needs a thin space before SD.
- App G: "Anchoring margins at k>1 are +6.44 and +5.86" does not name the judges.
- Table 3: "Constructed lure test" has no appendix pointer.
- Table 9: explain the "—" for Sonnet selection accuracy (integer ties) in the caption.
- Sec. 1 last paragraph: "including the many that failed" → "including the 24 of 80 that failed".
- Conclusion: "correct answers that differ from it are marked as failing" → "are often scored 3/10 or below".
- Sec. 2: say here, not only in Limitations, that rubric b instructs "Compare the candidate response against the trusted reference answer", and that rubric a, which does not, is the one used in the figures.
- Abstract sentence 3 is 56 words and carries two results. Split it.
- Abstract: "its help in rejecting wrong answers wins" is colloquial → "its help in rejecting wrong answers outweighs its cost".
- Sec. 2: "k-pool ... 15 tasks each" shrinks to 53 tasks after the pass-rate filter. State this once in Sec. 2, not first in the Limitations.

---

## Questions for authors (answers could change my score)

1. **Blind verification by pool.** Using one metric (blind AUROC, score vs validity), how do the replication pool, k-pool, MATH-500, and MACE rank? Does the ordering support Table 1's "verifies well / poorly" split?
2. **MACE by k.** What is MACE selection accuracy at k = 2, 4, 6 separately, and how does it compare with the k-pool at k ≤ 4? Is the MACE "reversal" explained by low k rather than weak verification?
3. **Corrected "10" scoring.** After rescoring digit-splitting judges with proper two-token probabilities for "10", do the rotation changes, margins, inflation, and Table 8 accuracy changes hold? How many scores used the 5.0 fallback?
4. **Unique answers.**
   - With a bare final-answer reference on MATH-500, does the +27.6 to +43.8 gain remain?
   - Why does a correct unique reference cost Qwen2.5-7B 21 points and Mistral-7B 10 points at k=1 on the k-pool?
5. **Grading accuracy on MACE.** Blind vs referenced, how accurate is per-sample grading (not best-of-n)? If the reference makes judges worse graders on multi-answer questions, the paper's significance rises substantially.
6. **Qwen3-8B on MACE.** What is its blind AUROC with thinking on (is it actually unable to verify)? Is there a second thinking judge, e.g. Sonnet 5 through the API with thinking enabled?
7. **CLI contamination.** Did the project context visible to the App H CLI judge contain any description of the hypothesis or the expected results?
