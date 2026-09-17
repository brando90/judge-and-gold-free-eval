# Meta-review (AC), ICLR 2027 — v5, round 3

**Paper:** "Reference Anchoring Biases LLM Judges Toward the Answer They Are Shown When Several Are Correct"
**Artifacts checked:** `main.tex`, `main.pdf` (39 pp, built 23:59), `appendix.tex` (23:57), `appendix_extended.tex`, `tables/*.tex`, `papers/analysis/r30a_*.json`, `papers/analysis/r30b_*.json`, `papers/analysis/r22c_acceptance_bins.json`, `papers/analysis/r30_analysis.py`, `experiments/tfa-vs-judge/scripts/r30_build_canonical_pools.py`, `experiments/tfa-vs-judge/scripts/r26_judges.py`, `registration_round30.md`, `scripts/check_numbers.py`, `SUBMISSION.md`. Diffed `main.tex`, `appendix.tex` and `appendix_extended.tex` against `../D-iclr-v3/`. I ran `check_numbers.py`, re-derived every R30-A and R30-B number from the producer JSONs, reconstructed the HLE mechanical-narrowing arithmetic by hand, and recomputed all 14 binned-acceptance cells. I did not rerun any model call.

---

## (a) Score

**5: marginally below the acceptance threshold. Confidence: 4.**

**Does the new evidence move my assessment? The science yes, the paper no.** I want to be precise about this, because it is the third consecutive 5 and it is a 5 for a different reason than the first two.

The two R30 experiments are the right experiments, they are the two the previous reviews named, they were registered before any call (`registration_round30.md:3`), they ran clean (149/149 questions, 596 calls per cell, no errors), and they produced two falsifications and a split that the team recorded rather than buried. R30-B's mechanical-narrowing analysis is the most intellectually valuable new result in the paper: it converts a reviewer's best attack ("your headline is a property of your random draw") into a sharper claim about what a canonical reference does and does not repair, and I verified the arithmetic behind it independently. On the evidence base alone I would now be at 6.5.

I am holding at 5 because **the new prose gave back what the new experiments earned, and this time it did it in the abstract.** Specifically:

1. A scope qualifier the round-2 review verified as present in the abstract — "with a reference drawn at random from each answer list" — **has been removed** (R3-1). That was the AC W1 half-fix. It was credited at round 2 and is now gone, replaced by a contrast that makes its absence actively misleading.
2. The abstract's new "9 to 20 with a chosen reference" is the **best case of two pre-registered arms**, chosen using the answering models' own outputs, presented as generic, and attributed to a grader set containing one grader R30-B never ran (R3-2).
3. §3 states a **falsified registered prediction as though it were confirmed** (R3-4), and switches measurement instrument mid-paragraph without saying so (R3-3).

Plus: three of the ten round-2 required changes (items 3, 5, 10) were not done at all.

Round 1 diagnosed "each revision fixes overclaims and introduces fresh ones in the new prose." Round 2 found the same. Round 3 finds the same, now one layer higher up the document. The pattern is the finding at this point, and it is worth the team treating it as a process problem rather than a list of sentences: every round, the experiments are careful and the appendix is honest, and every round the summary layer written last is where the unsupported claims appear.

**With R3-1 through R3-4 fixed plus round-2 items 3, 5 and 10, I restore 6.** With the counter-instructed row promoted into §3 (see (c)(i)), which now needs one new experimental cell, **7**.

**Credit where due — round-2 items genuinely closed this round:**

- **Item 1 (ledger total). CLOSED, and closed properly.** `main.tex:160` now reads 321 = 290 + 14 + 17, and `check_numbers.py:65-106` derives every column *and* the pooled total. I ran it: it prints "ledger column 3: rows sum to 17, matching the printed total" and flags 5 numbers, none in `main.tex`. The per-column blind spot the round-2 review identified is fixed by `check_numbers.py:103-105`.
- **Item 2 ("without buying anything"). CLOSED.** `main.tex:306` now reads "where it cannot answer the question, the instruction to match helps keep wrong answers out; where it can, that instruction costs grading accuracy." Supported, grammatical, and consistent with `tables/r26_instruction.tex`.
- **Items 6 and 7 (binned acceptance). CLOSED in both documents.** `appendix.tex:375` and `appendix_extended.tex:772` now both read "lower in a judge's top blind-score bin than in its lowest in all fourteen judge--pool cells, although monotonically in only four, and stays above zero in every top bin." I recomputed all 14 cells from `r22c_acceptance_bins.json`: 14/14 top < lowest, 4/14 strictly monotone, 14/14 top bin above zero (smallest `kpool|Opus 5` = 0.0265). Exactly right, and the extended appendix was updated too, which was the round-2 complaint.
- **Item 4 (self-grading cross-ref). CLOSED.** `main.tex:334` now cites `app:acceptance`, and `appendix.tex:381` does carry the disclosure. "which we measure" was dropped, which was the honest resolution.
- **Item 8 (`\cref{sec:p3}`). CLOSED** — sentence rewritten.
- **Page limit still compliant.** `pdftotext` confirms page 9 ends with the recipe and page 10 begins `AI USE STATEMENT`.

---

## (b) Defects the NEW material introduced

### R3-1 (BLOCKER). The abstract's random-draw qualifier was deleted — a round-2 fix reversed.

`main.tex:54`:

> "Those benchmarks rarely contain such questions. Run verbatim on 149 factual questions that do, their graders credit 0\% to 53\% of correct answers that differ from the reference, leaving four models 30 to 67 points below answer-list accuracy, **or 9 to 20 with a chosen reference**."

The v3 abstract said "…with **a reference drawn at random from each answer list**, their graders score four models 30 to 67 points below…". The round-2 review verified that qualifier as present in v5 and credited it: *"'with the reference drawn at random' now in the abstract (`main.tex:54`) — closes half of AC W1."*

It is now gone. `grep -n "at random" main.tex` returns lines 95, 130, 133, 248, 256 and 334 — **not 54**. The R30 integration removed it while adding the chosen-reference clause.

This is worse than a neutral reversion. The sentence now contrasts an *unqualified* "30 to 67" against "9 to 20 with a chosen reference", so the reader is told explicitly that one number has a chosen reference and left to infer that the other one is the default or natural condition. It is the random draw, and the random draw is the design decision AC W1 asked the paper to surface. The one place it must appear is the one place it no longer does.

**Fix:** restore it. "…leaving four models 30 to 67 points below answer-list accuracy with a reference drawn at random from each answer list, or 26 to 56 with a reference chosen by the benchmark's own answer ordering." (See R3-2 for why the second number changes.)

### R3-2 (BLOCKER). "9 to 20 with a chosen reference" is the best of two registered arms, and names a grader that was never run.

Two problems in one clause.

**(i) It reports only the modal arm.** R30-B pre-registered two rules (`registration_round30.md:137-145`). From the producer JSONs, accuracy minus answer-list accuracy:

| Grader | first-listed | modal | random |
|---|---|---|---|
| SimpleQA, GPT-4.1 | **−0.258** | −0.091 | −0.304 |
| BrowseComp/HLE, o3-mini | **−0.562** | −0.203 | −0.666 |
| Our rubric, Sonnet 5 | −0.181 | −0.079 | −0.223 |

The abstract's "9 to 20" is the modal row (9.1 and 20.3). The first-listed row is **25.8 and 56.2** and appears nowhere in the main text.

The registration is explicit about what the modal rule is: *"This arm is **deliberately the best case for the grader**, since it maximises the chance that a model's answer matches the reference"* (`registration_round30.md:144-145`). `appendix.tex:572-573` preserves a version of this ("the most favourable reference available"). The abstract does not, and §6 does not either — `main.tex:260` says "given the answer most of the four models produce, the SimpleQA grader falls 9 points short and the HLE judge 20", which reads as an operating point rather than a bound.

And the modal rule is the *less* relevant of the two for the claim being made. A benchmark author picks a canonical answer without seeing the graded models' outputs; that is what first-listed models (`r30_build_canonical_pools.py`: "Exogenous: it uses MACE's own ordering and nothing about our models"). Under the exogenous rule, SimpleQA's improvement **did not confirm** (+0.045 `[−0.003, +0.092]`, the split) and the HLE judge is still 56 points short. That is the honest headline of R30-B, and it is the arm the abstract omits.

**(ii) It over-scopes the graders.** The abstract's subject is "their graders", i.e. the graders of SimpleQA, BrowseComp and HLE (`main.tex:54` following `:47`, and `main.tex:255`). R30-B ran **SimpleQA/GPT-4.1, HLE/o3-mini, and our own rubric/Sonnet 5** (`registration_round30.md:147-149`; the six `r30b_*.json` filenames). **The BrowseComp grader was never run with a chosen reference.** So a range attributed to three shipped graders was measured on two of them. `main.tex:260` gets this right by naming only SimpleQA and HLE; the abstract does not inherit the restriction.

**Fix:** report the exogenous arm in the abstract, or report both as a range, and name the two graders. Keep modal where the registration put it — as a stated best case.

### R3-3 (BLOCKER). §3 switches measurement instrument mid-paragraph without saying so; "26 points" is not on the scale the paragraph is using.

`main.tex:174`, three lines earlier, in the same section:

> "text the reference moves onto gains 3 to 5 points and text it moves off loses about as much"

`main.tex:177`:

> "Credit still follows the reference, **by 26 points for GPT-4.1 and 13 for Sonnet~5**, while text matching neither reference barely moves (\cref{app:r30})."

The 3-to-5 figure is points on a 0–10 score (the abstract says so at `main.tex:51`: "about 3 to 5 points out of 10"). The 26 and 13 are **percentage-point changes in a binary credited share** — the direct template emits only `correct: yes|no` (`scripts/r26_judges.py:56`), and `r30_analysis.py:27` thresholds at 7. Two different instruments, two different scales, no unit on either number, four lines apart.

A reader on page 4 reads "26 points" against "3 to 5 points" and concludes the neutral prompt produces an effect five times the headline. It does not; it is a different measurement.

The paper knows this. `appendix.tex:563-565` says it plainly — "the two are not instrument-matched, since the rubric is a 0--10 score thresholded at 7 and the direct prompt is a binary yes or no" — but only inside the falsification discussion, and §3 carries nothing.

Secondary, same sentence: the two numbers are selected inconsistently. GPT-4.1's shifts are −0.264 (stop) and +0.247 (start); Sonnet 5's are −0.132 and +0.178. The sentence quotes GPT-4.1's **larger** direction and Sonnet 5's **smaller** one. Quote both directions or state the range.

**Fix:** "Credit still follows the reference: the share of answers credited moves by 26 and 25 percentage points for GPT-4.1 and by 13 and 18 for Sonnet 5, on a yes/no instrument not directly comparable with the 0–10 swap above."

### R3-4 (BLOCKER). §3 asserts a falsified registered prediction as if it held.

Same sentence, `main.tex:177`: "**while text matching neither reference barely moves** (\cref{app:r30})."

From `r30a_sonnet.json`, `matches_neither.shift_draw2_minus_draw1`:

> **−0.058559, [−0.106679, −0.011346], n=222**

The interval excludes zero. This is **P-R30A4, and it is falsified for Sonnet 5** — `r30a_sonnet.json` records `"P-R30A4 ...": "falsified"`; `registration_round30.md:215-217` records it; `appendix.tex:192` carries it in the failure table with the interval.

"Barely moves" is not an incidental phrase. It is the *exact* claim the registration operationalised — "Answers that match neither reference change credit by at most 5 points between draws" (`registration_round30.md:99`) — and it is the exact claim that failed. The appendix draws the right inference and says so: "part of Sonnet~5's movement is therefore not specific to the reference" (`appendix.tex:567-568`). The main text asserts the opposite of the appendix, with a `\cref` pointing at the appendix that contradicts it.

The paper already demonstrates the correct pattern two sentences earlier, at `main.tex:175`: "one registered prediction, that the swap would be ordered by numeric distance from the reference, failed (\cref{app:ledger})." That is exactly how the R30-A failure should be handled, and it is in the same section.

**This is also a material understatement of the placebo's consequences.** Placebo-correcting Sonnet 5 changes the numbers substantially, and the paper reports neither the correction nor the resulting asymmetry:

| Sonnet 5 | raw | placebo-corrected |
|---|---|---|
| stop matching | −13.2 | **−7.3** |
| start matching | +17.8 | **+23.7** |

The placebo absorbs 45% of the stop-matching effect for one of the two judges. That belongs in the main text, not only in the ledger.

**Fix:** "…while text matching neither reference barely moves for GPT-4.1; for Sonnet 5 it also loses 5.9 points, so our registered placebo prediction failed for that judge and part of its movement is not reference-specific (\cref{app:r30})."

### R3-5 (significant). `app:r30` upgrades "portable" to "design-independent", which is not what was tested.

`appendix.tex:600-602`:

> "…which is why we report the credited share as the **design-independent statistic** and the accuracy gap as the one that depends on how the reference was picked."

P-R30B3 claims only that the credited share "is the **portable** statistic" (`registration_round30.md:162-163`). What was tested is that the credited share moved less than the accuracy gap **across two reference rules on one 149-question pool**. That is not design independence, and the upgrade is exactly the class of overclaim the last two rounds flagged.

It is also partly definitional rather than empirical. The credited share is conditioned on "correct answers that differ from the reference", so moving the reference changes the **denominator** — 396 answers under the random draw, 121 under the modal rule (`r30b_*_modal.json`, `nonmatch_correct_credited[2]`) — rather than the measured quantity. A statistic computed on a shrinking, reference-selected subset is stable partly because the subset shrank. Note the precision cost the appendix table hides: the rubric's modal cell is **0.595 `[0.500, 0.688]`** on n=121, against 0.652 `[0.590, 0.712]` on n=396.

**Fix:** "…which is why we report the credited share as the statistic that moved least between our two reference rules." Drop "design-independent".

### R3-6 (significant). The "0.0 to 5.7 points" stability range is floored by a grader that cannot move.

`appendix.tex:600-601`: "Across all six cells the credited share moves by 0.0 to 5.7 points where the shortfall moves by 4.2 to 46.3."

I verified both ranges (0.0/1.1/2.6/1.1/5.7 and 4.5/21.3/10.4/46.3/4.2/14.4 — correct). But **two of the six cells are the HLE judge at 0.000 → 0.000**, which supplies the "0.0" floor. A statistic that is stable because the grader credits nothing under any rule is not evidence of a well-behaved statistic; it is the degenerate case, and the paragraph uses it in the preceding sentences as the *pathology*. Over the four cells where the share can move, the range is 1.1 to 5.7.

**Fix:** state it over the graders that credit anything, and note the HLE cells are pinned at zero by the effect under discussion.

### R3-7 (moderate). The `app:r30` R30-B table prints no intervals, and one of its comparisons is noise.

The R30-A table (`appendix.tex:544-558`) prints intervals on every change. The R30-B table (`appendix.tex:576-589`) prints none, on any column, although the JSONs carry them. The consequence is concrete: a reader comparing the SimpleQA first-listed credited share **0.519 against 0.530** cannot see that these are 0.519 `[0.456, 0.587]` and 0.530 `[0.471, 0.593]` — almost entirely overlapping. The same table is the support for the "0.0 to 5.7 points" claim in R3-6.

**Fix:** add the interval column, at least on "Differing correct credited".

### R3-8 (minor, but this paper's recurring word). "only" in §6.

`main.tex:260`: "The HLE judge still credits none of the answers that differ from its reference, so its gap narrows **only** because fewer answers differ."

I reconstructed this from `r30b_hle_o3mini_*.json` and it is very nearly right — see (d) for the full derivation — but not exactly. The matching-correct credit rate also rises, from ≈98.6% under the random draw to ≈99.8% under the modal rule. "Almost entirely" is accurate; "only" is not. In a paper whose last two reviews both turned on an unqualified quantifier, this one is worth spending a word on.

---

## (c) Is R30-A correctly interpreted?

**Partly. The experiment substantially weakens the pure instruction-following reading, which is real progress. The conclusion drawn from it is stronger than the design supports, and the main text states it more strongly than the appendix does.**

The claim under test, from `registration_round30.md:221-222`: "**The instruction-following reading cannot account for the effect.**" Four problems.

### (i) The prompt does not merely show the reference — it labels it, and "no instruction to compare" is true only of the verb.

The direct template, verbatim from `scripts/r26_judges.py:56`:

> `"Is the response a correct answer to the question?\n\nQuestion: {question}\n\nReference answer: {target}\n\nResponse: {response}\n\nDo not explain; reply with a single line of exactly \"correct: yes\" or \"correct: no\"."`

`appendix.tex:538` describes this as a prompt that "names the reference and says nothing about what to do with it". That is accurate as a statement about imperative verbs and incomplete as a statement about pragmatics. The string **"Reference answer:"** is an assertion that this is the answer to the question, placed immediately above the response the model is asked to judge. Removing "compare" does not remove that framing; it removes one channel of it. The paper's own vocabulary elsewhere concedes the point — `appendix.tex:53` treats the heading "Reference answer (trusted)" as part of the manipulation, not as neutral scaffolding.

So R30-A rules out *explicit* instruction-following. It does not rule out the judge inferring, from a labelled reference answer, that matching it is what is wanted. That is a weaker but still available deflationary reading, and the paper's "cannot account for the effect" does not distinguish them.

**The condition that would distinguish them already exists and is still not run on the swap.** `appendix.tex:66` quotes it: "Important: **do not compare** the candidate's answer to the reference. Use the reference only to understand the problem. Verify the candidate's answer on its own merits; a correct answer that differs from the reference must receive the same score as one that matches it." A swap that survives *counter*-instruction is the result that closes AC W3 outright. Round 2 asked for the three-row decomposition (instructed / neutral / counter-instructed); R30-A supplies the middle row, and the paper still does not build the table. **This is now one experimental cell away**, on a pool and harness that already exist, and it is the highest-value remaining move in the paper.

### (ii) The placebo is not adequate for Sonnet 5, and the paper's own verdict rule says so.

P-R30A4 falsified for Sonnet 5: −0.059 `[−0.107, −0.011]`. The placebo class exists precisely to absorb reference-independent movement and run-to-run drift, and for one of the two judges it absorbs **45% of the stop-matching effect** (5.9 of 13.2 points). The correct reading is the appendix's: "part of Sonnet~5's movement is therefore not specific to the reference" (`appendix.tex:567-568`). The correct headline is the placebo-corrected one (−7.3 / +23.7), which the paper never computes.

It is fine — good, even — that this failed and was reported. It is not fine that §3 then says "barely moves" (R3-4).

### (iii) R30-A has no same-prompt noise control, so the failed placebo is the *only* control.

The draw-1 arm is a **reused run**: "The draw-1 arm is the existing run of \cref{app:r26}; only the draw-2 calls are new" (`appendix.tex:540-541`), made on a different pool file at a different time (`registration_round30.md:66-72`). The paper's evidence that credit shift is a draw effect rather than call-to-call variation is R23-A, the same-reference regrade — but that was run **under the rubric, with Sonnet 5, Opus 5 and Haiku 4.5** (`appendix.tex:403-404`). It covers neither the direct prompt nor GPT-4.1.

So within R30-A the placebo class is the sole noise control, and it failed for one of two judges. That makes (ii) more consequential, not less. `main.tex:335` still says "only the API judges have a second blind call as a noise control" and is not updated for R30-A.

### (iv) An available stronger reading the paper misses.

From the JSONs, under draw 2 GPT-4.1 credits the stop-matching class at **0.722** and the placebo class at **0.712** — statistically indistinguishable. Under draw 1 the same answers were at 0.986. The structure this suggests is that **matching drives credit to a ceiling (0.97–0.99) and losing the match returns an answer to the judge's unassisted baseline, rather than pushing it below.** That claim is *immune to the placebo objection*, because it is about the ceiling, not the floor. Sonnet 5 is less clean (0.868 vs 0.793) but directionally similar. This is a more defensible and more mechanistically interesting statement than the one made, and it is free — it is already in the data.

**Verdict on (c):** report R30-A as narrowing the instruction-following reading rather than eliminating it; promote the appendix's two qualifications into §3; run or cite the counter-instructed cell.

---

## (d) Is R30-B's interpretation sound?

**The mechanical-narrowing argument: yes, and I verified it independently. It is the best new material in the paper. The modal rule as a comparator: defensible as a stated bound, not as the representative number, and the main text does not label it.**

### The mechanical argument checks out.

Claim (`appendix.tex:596-599`): the HLE judge "credits 0.000 of the correct answers that differ from its reference under every rule, so its gap falls only because fewer answers count as differing, 121 under the modal rule against 396 under the random draw".

`nonmatch_correct_credited` is **0.0 `[0.0, 0.0]`** in all three conditions: first-listed (n=335), modal (n=121), random (n=396). So HLE's referenced accuracy is entirely (matching correct credited + wrong credited) / 596, and can only move by moving the match boundary. Reconstructing:

- Answer-list accuracy 0.90604 × 596 = **540 correct** of 596; 56 wrong.
- Matching correct: 540 − 396 = **144** (random); 540 − 121 = **419** (modal).
- Referenced accuracy 0.239933 × 596 ≈ **143** credited (random); 0.703020 × 596 ≈ **419** credited (modal).
- `wrong_credited` = 0.017857 × 56 = **1** answer, in both chosen arms.
- Implied matching-correct credit rate: (143 − 1)/144 ≈ **98.6%** (random); (419 − 1)/419 ≈ **99.8%** (modal).

So the 46.3-point improvement is reclassification, not better grading, to within about a point. The argument is correct and well made. The only correction is R3-8: the matching rate does tick up slightly, so "only" should be "almost entirely".

This is the right conclusion and it is the one that should be leading §6 — it is what makes the chosen-reference result a strengthening of the paper rather than a concession.

### The modal rule is circular in a way the main text does not disclose.

`r30_build_canonical_pools.py`, `modal_ref()`: for each question it counts, over the **correct samples of the four answering models**, the first listed answer each one matches, and takes the argmax. So the rule is defined by the graded models' own outputs, and it maximises the match rate **by construction**. The registration states this without flinching: "This arm is deliberately the best case for the grader, since it maximises the chance that a model's answer matches the reference" (`registration_round30.md:144-145`), and the disclosed design facts confirm the mechanism — 419 matching answers under modal against 205 under first-listed and 174 under the random draw (`registration_round30.md:132-134`).

Is it a fair comparator? **As a bound, yes** — and that is exactly how the registration framed it and how "What it settles" framed it (`registration_round30.md:168-171`). Reporting a best case is legitimate and informative.

**As the representative number, no**, for a reason the paper should find congenial: it does not model what benchmark authors actually do. An author picks a canonical or salient answer *without seeing the graded models' outputs*. The rule that models that is first-listed — and under first-listed, SimpleQA's improvement **did not confirm** (+0.045 `[−0.003, +0.092]`) and HLE is still 56.2 points short. So the arm that mimics real practice barely helps one grader and leaves the other catastrophic, while the arm that uses the models' own answers is the one the abstract quotes (R3-2).

`appendix.tex:572-573` does carry "the most favourable reference available". `main.tex:260` and the abstract do not, and those are the two places a reviewer reads.

**Two further notes:**

- **First-listed is only approximately exogenous.** MACE's list ordering is not guaranteed to be arbitrary — it may itself be salience- or frequency-ordered, which is what makes it a decent proxy for a canonical choice but also means the random-vs-chosen contrast has no clean estimand. Worth one sentence; not a blocker.
- **The rubric arm grades its own answers.** The R30-B rubric row is Sonnet 5, one of the four answering models. This is disclosed for the main benchmark study (`appendix.tex:381`) but `app:r30` does not repeat it, and the rubric row sits in the same table as the two shipped graders with no mark.

---

## (e) Are the ledger, the falsifications and the split reported honestly and in the right places?

**The accounting is honest and correct. The placement is not: neither falsification reaches the main text, and the one that contradicts a main-text sentence is the one §3 asserts.**

### What is right

- **Arithmetic verified.** `tab:ledger-totals` (`appendix.tex:150-164`) gains a Round 30 column: 14 + 0 + 2 + 1 + 0 + 0 + 0 = **17** ✓. `main.tex:160` says 321 = 290 + 14 + 17 ✓. `check_numbers.py` derives all three columns and the pooled total; I ran it and it confirms each. The count also reconciles against the registration: R30-A 6 confirmed + 2 falsified, R30-B 8 confirmed + 1 split (`registration_round30.md:257-258`).
- **Both falsifications get their own ledger row**, with numbers and intervals (`appendix.tex:192`), and the split gets one with its interval (`appendix.tex:193`). Correct placement in the failure table.
- **`app:r30` reports both failures in prose** with the right inference drawn for each (`appendix.tex:560-568`), including the instrument-mismatch caveat on P-R30A3 that the registration also recorded. This is genuinely good practice and better than field norm.
- **The split is labelled as a split** at `appendix.tex:593`.

### What is wrong

**Neither falsification appears anywhere in the main text, and one of them is contradicted there.**

- `main.tex:177` asserts "text matching neither reference barely moves" — the falsified P-R30A4 — unmarked and unhedged (R3-4).
- `main.tex:260` reports the chosen-reference result without mentioning the split, and without mentioning the first-listed arm at all.
- `tab:summary`'s caption (`main.tex:105`) promises "Each row's numbers, intervals, and **failed registered predictions** are in the cited section and the ledger." For R30 the chain is broken: §3 is the cited section and it carries no failure.
- The paper sets its own correct precedent two sentences earlier, at `main.tex:175`, for the distance-ordering failure. The same treatment was not extended to the new result.

**A second, softer point on the ledger's growth.** Of the 14 new confirmations, 3 are P-R30B2 ("the shortfall is still below zero"), which with shortfalls of 8 to 56 points on 149 questions was never at risk, and 3 are P-R30B3, scored by hand with no interval and comparing two different quantities on different scales. So 6 of 14 were near-certain or non-inferential. The ledger is this paper's distinguishing strength and it is worth protecting from dilution. Round-2 item 7 — state what fraction of the confirmations are interval-bearing, and what a BH pass over that subset would do — is still not done, and R30 makes it more pressing, not less.

---

## (f) Still unaddressed, in the order a reviewer will hit it

1. **AC W3, the instructed-comparison decomposition. Now 2/3 built and still not assembled.** §3 has instructed (rubric, MT-Bench) and neutral (R30-A). The counter-instructed wording exists (`appendix.tex:66`) and its result is still buried in `app:mitigation`. One cell and one three-row table converts the paper's most reachable rebuttal into a result. **Highest-value item in the paper.**
2. **Round-2 item 3: NOT DONE.** `main.tex:52` still reads "for the four open judges and GPT-4.1 under every labeling we tried", while `main.tex:115` and `main.tex:202` both say GPT-4.1's factual interval includes zero, and `tables/labelings_gnm.tex` has three of four GPT-4.1 $k$-pool labelings touching or including zero. The abstract still names a judge the body calls null. And **`grep -c Mistral main.tex` returns 0** — the "four open judges" restriction is still uninterpretable without the appendix, because the fifth open judge, the one it exists to exclude, is never mentioned.
3. **Round-2 item 5: NOT DONE.** `main.tex:224` still reads "At the open judges' post hoc threshold, phi-4 takes back 42\% and Qwen2.5-7B 83\%" with no pool named, immediately after a clause that resets the reader's pool to the constructed pools. These are MACE-only (`appendix.tex:373`); phi-4's replication value is 4.6%. `main.tex:229`'s 843/117 is still unlabeled as pooled.
4. **Round-2 item 10: NOT DONE.** The prevalence κ ≤ 0.35 exposure is still not in the abstract, contrary to the team's own `registration_round29.md`. "Reference anchoring" is still a title term the body never defines: `grep -i anchor main.tex` returns the title (`:38`), the Kapetanovic citation (`:328`), and one verb in Limitations (`:335`).
5. **Round-2 item 9: PARTIAL.** `main.tex:265` is now hedged ("We read the failure as reuse across a capability boundary"), but the §6 subheading at `main.tex:262` still asserts it flatly, and the subheading is what a skimming reviewer reads.
6. **`SUBMISSION.md` is stale again.** The TL;DR still says graders "score four models 30 to 67 points below their answer-list accuracy" with no reference-regime qualifier and no mention of the chosen-reference result — the same class of defect as R3-1, in the text that gets pasted into OpenReview. The supplement checklist item is explicitly marked **Stale**, and `registration_round30.md` and `papers/analysis/r30*.json` are not yet synced into it. Two boxes remain unchecked, including the title-named PDF refresh.
7. **Multiplicity.** 321 predictions, no correction, no statement of the interval-bearing fraction. See (e).
8. **P3's acceptance proxy** still rests on a check the ledger records as falsified (`appendix.tex:206`: "at most 5\% of wrong answers scored 10 blind in each pool (**falsified**: 5.1\% to 8.2\%)"). Disclosed well at `main.tex:238`; Table 1's "Holds for every judge with an acceptance test" remains mildly circular.
9. **`tab:survey`'s 43 still has no stated inclusion protocol**, and it now opens the abstract.

---

## Required changes, in priority order

| # | Where | Change |
|---|---|---|
| 1 | `main.tex:54` | Restore "with a reference drawn at random from each answer list". It was present at round 2 and was deleted this round. |
| 2 | `main.tex:54` | Replace "9 to 20 with a chosen reference" with the exogenous first-listed arm (26 to 56), or give both and label modal as a best case. Name the two graders actually run; BrowseComp was not. |
| 3 | `main.tex:177` | Give "26 points … and 13" a unit and say it is a yes/no credited share, not the 0–10 swap of the preceding sentence. Quote both directions per judge. |
| 4 | `main.tex:177` | Stop asserting the falsified placebo. State Sonnet 5's −5.9 and that P-R30A4 failed for it, in the style already used at `main.tex:175`. Report the placebo-corrected shifts (−7.3 / +23.7). |
| 5 | `main.tex:260` | Label the modal rule as the best case, per `registration_round30.md:144`. "only because fewer answers differ" → "almost entirely". Mention the split. |
| 6 | `appendix.tex:600-602` | "design-independent" → "moved least between our two reference rules" (the registration says "portable"). Note the denominator changes 396 → 121. |
| 7 | `appendix.tex:600-601` | State the credited-share range over graders that credit anything (1.1 to 5.7); note the HLE cells are pinned at 0 by the effect under discussion. |
| 8 | `appendix.tex:576-589` | Add intervals to the R30-B table, at minimum on "Differing correct credited"; 0.519 vs 0.530 is noise and the table cannot show it. Mark the rubric row as self-graded. |
| 9 | §3 / `app:r30` | Report R30-A as narrowing the instruction-following reading, not eliminating it. Note the reference is still labelled "Reference answer:" and that no same-prompt noise control exists for this arm. |
| 10 | Carried over from round 2 | Items 3, 5 and 10: the GPT-4.1 abstract restriction + naming Mistral-7B; "on MACE" for phi-4/Qwen2.5-7B and "pooled" for 843/117; prevalence-κ in the abstract and one defining sentence for "reference anchoring". |
| 11 | `SUBMISSION.md` | Refresh the TL;DR for the chosen-reference result and the reference regime; sync `registration_round30.md` and `r30*.json` into the supplement. |
| 12 | §3 | Run the counter-instructed swap cell and build the three-row decomposition. This is what moves the paper from 6 to 7. |

Items 1–8 are text-only and take under an hour; they are what stands between 5 and 6. Item 12 is one experiment on an existing harness and pool, and it is the one that retires AC W3.
