# Round 1 review: "Reference Answers Mislead LLM Judges When Many Answers Are Valid"

Reviewer role: Area Chair, presentation-focused. I read the PDF (22 pages) and page images at 110 and 250 dpi, and checked the LaTeX sources, the generated tables (`tables/*.tex`) and `main.log`.

---

## 1. Skim impression (3-minute AC pass)

**What I took away.** When a question has several correct answers, an LLM judge shown one reference answer scores agreement with that reference, not correctness. If you swap which valid answer is the reference, the score of the same text moves by about 4 to 5 points out of 10. When best-of-n uses such a judge, it picks answers that match the reference and are wrong more often. The authors say this starts at k=2 valid answers, that judges seem to run a surface equality check, and that a two-call protocol ("blind, then reveal") fixes it. The title states the claim, which is good. Figure 1a is easy to read.

**Where I got lost, in order:**
1. **Figure 1b.** The y-axis is "added inflation (SD)". I did not know what one unit meant. The caption's gloss ("the chosen answer's score gain beyond its true correctness") mixes a score and a correctness rate, and neither is in SD. Figures 2b, 3a and 3b use the same unit, so after the skim I still could not say how much accuracy the reference costs.
2. **The contribution bullets don't follow section order** (Sec. 4, then 3 and 5, then 6, then 7). The body opens with optimization (Sec. 3), goes back to the causal rotation test (Sec. 4), then forward again.
3. **Pages 3 to 6 read like a list of numbers.** Most sentences give two decimals, one per judge, plus a CI or n (roughly 25 to 37 decimals per page). I counted about 15 task-count denominators (120, 105, 93, 75, 60, 58, 53, 48, 37, 35, 25, 24, 21, 317, 300) and gave up tracking which pool each claim came from.
4. **Table 2 says "in decreasing order of safety"** yet puts the bolded recommended protocol last, below "Worked solution... still harmful". Taken literally, the recommendation is the least safe option.
5. **The fix section confused me.** The ablation says the judge "defers to the number", meaning it copies the blind score. Then why not just use the blind score? Figure 3a plots the fix relative to blind judging and it sits at about 0. So the fix recovers blind judging at twice the cost, and I found no result where it beats blind judging.
6. **"Section D", "Section M" and so on** point to appendices but look like main-text sections.
7. **Claims then retractions.** A training result appears in the contribution bullets, and three sentences later the body says it "does not show that the reference is the cause." "Preregistered" appears 22 times in the main text, and some of those are author-controlled git commits.

**One-sentence AC summary:** a careful and honest empirical study with a real effect, written as a lab notebook rather than a paper. The headline metric is opaque, the fix is not shown to beat the obvious baseline, and several headline claims go further than the tables.

---

## 2. Scores

| Dimension | Score (1-10) |
|---|---|
| **Overall (ICLR scale)** | **5**: marginally below the acceptance threshold |
| Presentation | 5 |
| Clarity | 4 |
| Soundness of claims (calibration) | 5 |
| Significance | 5 |
| **Confidence** | **4** |

The experimental care is well above average: exact validity checkers, rotation with byte-identical candidates, two rubrics, and a ledger that reports failed predictions. Presentation and calibration are what keep this out of the accept band.

---

## 3. Blocking issues (ranked)

### B1. The recommended fix is never shown to beat blind judging, and the paper's own ablation suggests it cannot.
- Figure 3a plots blind-then-reveal (BTR) as "added inflation over blind judging". BTR sits at about 0, so its best case equals blind judging.
- "Why it works" (Sec. 7) finds the judge "seems to defer to an explicit number that carries the blind pass's signal, and it uses that number instead of the reference token." In other words, the second call mostly copies the first.
- The one place a reference should add value over blind judging is k=1. The ledger (Table 4, row 2) reports: "blind-then-reveal preserves the k=1 benefit (**partial**: no cost, benefit not reproduced)." On the k-pool the reference does not help at k=1 either (+0.05, −0.11).
- So in every experiment shown, BTR ≈ blind, at 2× the calls. Table 2 then ranks BTR above blind judging, and describes blind judging as "weak on such tasks". BTR inherits that weakness, because it defers to the blind score.
- BTR was never run on MATH-500, the one pool where the reference cuts inflation 4 to 13-fold. It was also never run on a frontier judge or on a mixed-k pool.
- **Needed:** BTR versus blind versus reference on (i) MATH-500 or another unique-answer pool where the reference clearly helps, and (ii) a mixed pool where k is unknown to the practitioner. Report selected-answer accuracy. If BTR does not beat blind anywhere, the practical advice is "don't show the reference, or verify by program", and the paper should say that plainly.

### B2. External validity of the judging setup. The "cheap equality check" may come from forbidding the judge to reason.
- Every rubric ends with "Respond with only the integer score" or "Output only a single number" (App. A). Open judges are read from one token's log-probabilities. Sonnet 5 and GPT-4.1 use "the same prompts".
- A judge that is not allowed to reason is exactly the judge you would expect to fall back on a surface comparison. Reference-guided graders in 2026-27 (RLVR verifiers, reasoning judges) usually reason before scoring.
- Referenced rubric (b) literally says: "**Compare the candidate response against the trusted reference answer provided.**" The prompt field is labelled "Reference answer (trusted):". Under rubric b, part of the anchoring is the model following instructions. Rubric b also gives the largest Qwen effect (+6.34 rotation, +5.99 margin).
- None of this is visible in the main text, and Limitations mentions neither issue.
- **Needed:** (i) a reasoning-judge arm (e.g., Sonnet 5 with extended thinking, or an open reasoning model) on rotation and the k-step; (ii) a standard third-party reference-guided prompt (e.g., the MT-Bench reference-guided template the paper itself cites as "standard"); (iii) the prompts, or at least rubric b, in the main text.

### B3. "The harm switches on at exactly two valid answers for seven of the eight open judges we test and on a third-party benchmark" (abstract) overclaims.
- **"Exactly two" is shown for only two judges.** A k=2 cell with a CI exists only for Qwen2.5-7B and phi-4 (Table 10). The synthetic grid (Table 9), the coverage judges (Table 20) and MACE (Table 11) report only k=1 against pooled k>1. MACE has no k=2 cell at all.
- **"Harm" at k>1 is not significant for 3 of 6 grid judges.** The pooled k>1 level is +0.07 [−0.15,+0.26] for Qwen2.5-1.5B, +0.08 [−0.20,+0.36] for 14B, and +0.22 [−0.19,+0.65] for phi-4. For these judges the "step" is mostly losing the k=1 benefit. App. F admits this ("individually significant for only three"), but the abstract does not.
- **The grid's k=1 cell has 6 tasks** (Table 9 caption). The main text never says so.
- **There is a ninth open judge.** Ministral-8B appears in App. M ("essentially uncorrelated with validity") and is left out of the "eight".
- **The k=1 to k=2 transition is close to definitional.** At k=1, matching the reference and being correct are the same event, so no anchoring bias can hurt there. The paper presents the "boundary" as a discovery (a section title, contribution 2, a panel title "Harm starts at k=2"). The non-trivial finding is how large the harm already is at k=2. Reframe it that way.

### B4. The headline metric is opaque and, as written, cannot be reconstructed.
- **Readers can't interpret the unit.** Every quantitative figure except 1a and 2a uses "added inflation (SD)". The paper concedes "standard-deviation units are unfamiliar", then plots them anyway. Accuracy numbers appear only in Table 1, marked post hoc and without CIs. Validity is known exactly in every own-built pool, so "where the design allows it" is always.
- **Eq. 1 is underspecified.** G subtracts a raw accuracy difference, (V(s*) − μ_V), from a z-score. App. A admits "the standard-deviation normalization applies to the score term only", so "SD" is a misnomer for G.
- **The permutation step looks incoherent as described.** "π shuffles scores among samples with the same validity". If both rubric scores are permuted within validity classes, the validity class of the argmax is unchanged, so the V term cancels in G − E_π[G]. If J_a and J_b are permuted jointly, the value J_b(s*) is unchanged and inflation is identically zero. The text must say exactly what is permuted.
- **Also undefined:** whether μ_J and σ_J refer to J_a or J_b, and App. A's "averages ... over resampled sub-pools".
- **Needed:** make selected-answer accuracy (or the false-rejection rate on correct non-matching answers) the plotted headline in Figures 1b, 2b and 3, with CIs. Move the permutation estimator to the appendix with a precise definition.

### B5. The training result is promoted and then retracted.
- **Bullet 2 promotes it:** "A policy trained against a reference-showing judge raised its judge's score while its accuracy fell from 41% to 18%."
- **Paragraph title:** "Training makes it larger."
- **The body retracts it:** "It does not show that the reference is the cause: every control arm we trained failed its own manipulation check."
- **The controls also lost accuracy.** Held-out accuracy fell in every arm: −0.228 reference, −0.049 and −0.073 BTR, −0.125 blind (Table 18).
- **Selective numbers.** The 41%→18% figure is from the 60 *training* tasks, not the held-out set.
- **What was learned is not reference-specific.** The policy abandoned `\boxed{}` and wrote longer answers, and it copied the reference *less*.
- **Fix:** remove the result from the contributions and the conclusion ("optimization exploits it"). Keep one hedged sentence in Sec. 3 and move the rest to App. L.

### B6. Figure 1 does not tell the story, and the figures don't share one visual grammar.
- **No example.** Figure 1 has no schematic of the divisor-of-91 example that opens the paper. The intro's hook numbers (7.9 / 9.8 / 2.3) come from a different judge interface and appear in no figure.
- **Mixed units.** Figure 1 puts 0-10 points (a) next to SD (b).
- **The fix is missing.** A reader who only sees Figure 1 gets the problem and never the answer.
- **Color means different things in different figures.** Color encodes condition in 1a and 3a but judge in 2a and 3b. Teal is "blind, then reveal" in 3a and "Qwen2.5-7B" in 3b. Light blue is "reference moved off it" in 1a, "phi-4" in 2a and "reference shown" in 3a.
- **One caption is wrong.** Figure 3a says "(light blue, as in Figure 1b)", but the Figure 1b lines are saturated royal blue.
- **Overlaps and style breaks.** The Figure 1b legend text "Qwen2.5-7B" overlaps the k=4 error bar, and "below 0: reference helps" sits on the phi-4 k=1 marker. Figure 3a's legend overruns the axes frame, and 3a is the only panel with a closed box frame. Figure 1a's data labels use hyphens ("-5.0") instead of minus signs.

### B7. Cognitive load: a lab notebook, not a story.
- **Too many numbers.** About 25 to 37 decimals per page on pp. 3-6. Nearly every claim gives "X and Y" for two judges.
- **Too many denominators.** About 15 task counts, and several sub-pools are never sourced in the main text: "58 multi-answer tasks" (Fig. 3b), "37 multi-answer tasks" (Sec. 4), "21 scalar-answer tasks" (Fig. 2a), "35 multi-answer tasks" (App. I).
- **Too many coined terms.** In the main text alone: anchoring margin, inflation, added inflation, G, replication pool, k-pool, synthetic grid, exploratory study/Ties pool, blind, referenced, blind-then-reveal, rubric a/b, pass-rate band (undefined in the main text), manipulation check (undefined), stopping rule, blind-certified (appendix), "cells", "the step", the continuum. The appendix adds wedge, hack gap, M2, validity gate, lures, d, λ/β/γ, decode cost, score-resolution screen.
- **Detours in the main text.** "Which tasks inflate most?", the MBPP failed-prediction story, several-references and worked-solution mitigations, and the GPT-4.1 tie discussion.
- **The main text ends at the top of p. 8.** That leaves about 1.7 pages unused, yet the authors still packed results into prose instead of adding a schematic and a clean summary table.

### B8. Factual and number inconsistencies an expert reviewer will find within an hour.
- **Sec. 5, "gemma-2-9b shows the largest harm of any judge at k>1 (+1.43)":** false. Qwen2.5-7B on the same k-pool is +1.50 (Table 10), and Qwen2.5-3B on the grid is +2.41.
- **App. M, gemma "is the most anchored judge we measured":** its k-pool margin is +5.32, but the frontier CLI judge's margin is +7.49 (App. H) and Qwen2.5-1.5B on Ties is +9.00 (Table 8).
- **Sec. 4, Sonnet 5 "(+2.79, 92% kept)":** Table 7 caption gives 3194/3494 = 91.4%.
- **Mistral-7B ties.** Sec. 5 and App. M: "best-of-64 ties about half of each pool at the maximum". Table 22: mean ties at max = 17.8 of 64 (28%). Sec. 5 says "nearly integer-valued", App. M says "only 11 distinct values" (exactly integer).
- **Limitations, "Two frontier judges reproduce the causal and mechanism results":** GPT-4.1 has no rotation or masking results anywhere (Table 12 and App. H report only its margins, picks, instructions and the unresolved step).
- **Limitations, "where a program decides validity":** MACE entity domains rely on shipped knowledge-base lists with measured 2.3% to 8.1% omissions (App. G). App. A likewise says "Validity is always decided by a program ... with one exception: the exploratory Ties pool."
- **Sec. 7, "Showing another judge's blind score protects Qwen and phi-4 as well as their own":** for Qwen, other-judge is +0.38 [+0.12,+0.60] against own +0.01 [−0.24,+0.29] (Table 21). Neutral wording at +0.53 was ruled non-equivalent, while +0.38 was ruled equivalent, with no margin stated.
- **Sec. 7, "at k=1 it costs nothing":** Qwen BTR at k=1 is +0.41 [−0.09,+0.84] against +0.05 for the plain reference, on 15 tasks. Visible in Figure 3a.
- **Sec. 7, "It is complete for ... phi-4":** phi-4 BTR at k=16 is +0.44 [+0.13,+0.76], and pooled it is +0.16 [+0.00,+0.33].
- **Sec. 6, "On 317 MBPP problems, showing a canonical solution reduced inflation ... (−0.34 for Qwen2.5-7B ...)":** the contrast uses 58 tasks (App. K), and Qwen's CI is [−0.737,+0.041], which includes zero.
- **The abstract's 82.5% / 19.6% figures** appear in no appendix table. App. H gives only means and margins.
- **Phi-4 program format.** "That held for phi-4, where the reference helps" (Sec. 6) depends on a checker fix made after registration. Under the registered labels phi-4's program-format value is −0.06 [−0.22,+0.11], a null. The main text does not say this.

### B9. Positioning and significance are thin.
- **Prior work is one sentence.** The intro says "Earlier work shows that judges penalize valid answers that differ from a provided reference (Li et al., 2025; Lee et al., 2026)". Lee et al. is about knowledge conflict, not multiple valid answers. The reader cannot tell what Li et al. already measured: did they rotate references, and did they have multi-answer items?
- **The obvious ICLR audience is not addressed.** That audience is RL with verifiable rewards that uses LLM or model-based verifiers given a ground-truth answer, where false negatives on equivalent or alternative answers are a known problem. Huang et al. (2025) is cited only in passing, and closely related verifier false-negative work (e.g., TinyV, xVerify, CompassVerifier, General-Reasoner's verifier) is missing.
- **No prevalence estimate.** The paper never estimates how often k>1 occurs in real benchmarks or RL training sets. Without that, a practitioner cannot tell whether this matters for their pipeline.
- **Narrow generation setup.** Candidates are mostly from Llama-3.1-8B on synthetic arithmetic puzzles.
- **GPT-4.1 is not a frontier judge in 2027.**

### B10. "Preregistered" is used for two different levels of evidence.
- The intro makes the distinction ("three experiments through public preregistrations and the rest as timestamped commits"). The captions then drop it: Figure 2 ("Preregistered.") and Figure 3b ("Preregistered.") are git-only, while Figure 1b is OSF. Author-controlled git timestamps are not third-party verifiable.
- **Fix:** use two labels throughout, e.g., "OSF-registered" and "pre-specified (git)", and add a summary count, e.g., "N predictions: X confirmed, Y falsified, Z unresolved".

---

## 4. Line-level fixes

**A note on voice first.** The prose is mostly plain and readable, which is better than most. But it keeps returning to a few patterns that read as machine-written:
- **Short dramatic sentences:** "They are not.", "It did not.", "Under optimization, the reference stops being a safeguard.", "The robust claim is the step.", "So the two-call structure alone protects nothing."
- **Repeated "not X, Y" / "X rather than Y" frames:** the Sec. 4 title, "about meaning, not characters", "changes the protocol rather than the prompt" (twice, in the Table 2 caption and the conclusion), "A protocol change fixes it, and prompt changes do not", "Distance does not matter, equality does", "Two correct routes ... do not trigger the failure; two correct answers do", "rejects broken judges and certifies nothing".
- **Rhetorical questions and colon reveals:** "Which tasks inflate most?", "a different question: does this answer agree with the one I was shown?"
- **Human-like verbs for a judge:** "overrides its own earlier verdict", "give up when that check stops being free", "defer to the number".

Cut about half of these. Keep the divisor-of-91 opening.

### Abstract and introduction (p. 1-2)

1. **"That assumption quietly requires the question to have one correct answer."** "Quietly" is a verbal tic. → "That assumption holds only when the question has one correct answer."
2. **"moves the score of an unchanged candidate by 3 to 6 points on a 10-point scale"** The scale is 0-10, and the observed range across judges and rubrics is 2.5 to 6.6 (Sonnet 5 rubric b +2.54; Qwen rubric b −6.58, Table 7). → "by 2.5 to 6.6 points on a 0-10 scale", or restrict to "3 to 5 points under the primary rubric".
3. **"a frontier judge fails 82.5% of correct answers that differ from the reference, against 19.6%"** The judge is unnamed ("a frontier Claude judge"), it returns sampled integers through a CLI, it covers 37 tasks, and neither number appears in any table. → Name the model and version, give n, define "fails" (score ≤3), and add these rates with CIs to App. H.
4. **"Under optimization, the reference stops being a safeguard."** A dramatic fragment that adds nothing. Merge into the next sentence.
5. **"the harm switches on at exactly two valid answers for seven of the eight open judges we test and on a third-party benchmark."** See B3. → "Going from one valid answer to several turns the reference from helpful or neutral to harmful for seven of eight open judges with usable score resolution, and on the third-party MACE benchmark."
6. **"and the harm fades as answers get harder to compare."** The format continuum changes match rate and effective k along with comparison difficulty (App. K: a median of two distinct program outputs; pair and JSON have 7 and 1 usable tasks). → "and the harm shrinks as the requested answer format moves from an integer to a program."
7. **"What does help is to score blind first ... ablations show the judge is deferring to the number."** This omits that the fix largely fails for gemma-2-9b and that it matches blind judging rather than beating it. → Add "for three of four judges tested", and state what BTR buys over blind judging (or admit it buys nothing measured).
8. **"The judge had not become stricter. It had started answering a different question: does this answer agree with the one I was shown?"** Colon-reveal drama. → "The judge was not stricter overall: matching answers rose as non-matching ones fell, so the score tracked agreement with the reference."
9. **"Earlier work shows ... (Li et al., 2025; Lee et al., 2026). What was missing is what that bias does once something optimizes against the judge, why it happens, and what to do about it."** A vague delta in a stacked triad. → Two concrete sentences: what Li et al. measured (static penalty? rotation? multi-answer?), and exactly what this paper adds.
10. **"The harm should appear as soon as a second valid answer exists, and reverse when the answer is unique."** On the k-pool the reference does not help at k=1 (+0.05, −0.11; ledger: "benefit not reproduced"). → "and be absent when the answer is unique."
11. **"Confirmatory predictions were committed before their data existed, three experiments through public preregistrations and the rest as timestamped commits. Several predictions failed, and we report those next to the ones that held (Section B)."** The failures are in an appendix, not "next to" anything. → "Appendix B scores all N predictions (X confirmed, Y falsified, Z unresolved); OSF-registered and git-pre-specified experiments are labelled separately throughout."
12. **Bullet order.** The bullets cite Sec. 4, then 3 and 5, then 6, then 7. Reorder the sections (rotation → selection and k-step → mechanism → fix) or reorder the bullets.
13. **Bullet 1: "and answers matching neither reference do not move ... This holds for frontier judges"** phi-4's "neither" shift is +0.30 [+0.04,+0.57], which excludes zero. Only Sonnet 5 has rotation results. → "barely move"; "This holds for Sonnet 5".
14. **Bullet 2: "A policy trained against a reference-showing judge raised its judge's score while its accuracy fell from 41% to 18%."** Delete (B5). If kept, give held-out numbers and add "; control arms failed their checks, so we cannot attribute this to the reference."
15. **Bullet 3 title "The judge runs a cheap equality check"** states a behavioral inference as fact. → "Judges behave as if they run a surface equality check".
16. **Bullet 4: "removes the measured harm for the judges it works on."** Circular. → "removes the harm for Qwen2.5-7B, phi-4 and Qwen2.5-14B, and barely helps gemma-2-9b." The bullet title "prompt changes do not" is also contradicted by phi-4 at k=16 (+1.91 → +0.03). → "prompt changes help only some judges".

### Figure 1 caption and Setup (p. 2-3)

17. **"(Section D)"** and every other appendix pointer renders as "Section X". → Make cleveref print "Appendix D" (e.g., `\crefalias{section}{appendix}` after `\appendix`, or the `appendix` package with `\crefname{appendix}{Appendix}{Appendices}`).
18. **Fig. 1 caption: "120 questions with exact validity checks"** The n differs per bar (onto 120, off 93, neither 113; Table 7). → "up to 120 questions per bar".
19. **Fig. 1 caption: "(the chosen answer's score gain beyond its true correctness; Section 2)"** The unit is SD for the score term but raw proportion for correctness. → Replot 1b as selected-answer accuracy, or define the unit precisely.
20. **"A candidate is *correct* if its answer is in 𝒱, never merely if it equals r."** Illogical, since r ∈ 𝒱 means matching r does make an answer correct. → "A candidate is correct iff its answer is in 𝒱; matching r is sufficient but not necessary."
21. **"We also use a six-judge synthetic grid, MACE (...) for questions whose number of answers is fixed by that benchmark's authors, MBPP (...) for code, and MATH-500 for unique answers."** Mixes a design (the grid) with datasets, so it reads as if MACE feeds the grid. → Use a four-row inline table: pool, n tasks, generator, role. Also name the sources of the 58-, 37- and 21-task sub-pools.
22. **"Open judges report the expected score under their distribution over the tokens 0 to 10."** Add, in the main text, that judges output a single score token with no reasoning, and give the referenced rubric b wording (B2).
23. **"Selection uses rubric a and reporting uses rubric b, so a lucky draw on one wording cannot inflate the reported score."** Fig. 1a and 2a then say "bars show rubric a". → Clarify: "For inflation, rubric a selects and rubric b scores; margins and rotation are reported under each rubric."
24. **Eq. 1 and "Inflation is G − 𝔼_π[G], where π shuffles scores among samples with the same validity."** Not reconstructible (B4). → State which scores are permuted (J_b only? J_a only?), why the V term remains after taking the permutation expectation, and which of J_a or J_b μ_J and σ_J refer to.
25. **"Because standard-deviation units are unfamiliar, we also report the plain accuracy of the selected answer where the design allows it."** Validity is exactly known in all own pools, so the design always allows it. → Make accuracy the primary readout. Keep inflation as the preregistered endpoint in tables.
26. **The pass-rate band is undefined in the main text.** Table 1's caption uses "the preregistered pass-rate band". → Add one clause to Sec. 2: "tasks whose generator pass rate is in [0.2, 0.8], where selection can change correctness."

### Section 3 (p. 3-4)

27. **Table 1.** A 31 pt overfull hbox (`main.log`, lines 139-152): the rules visibly overrun the right margin. The header "( SD, 95% CI)" has a spurious space because `\sd` starts with `\,`; the same bug appears in the captions of Tables 5, 9, 10, 11, 12, 13, 17, 20 and 21. Accuracy columns have no CIs. The Pooled row has four empty cells. → Remove `\,` from the macro, cut `\tabcolsep` or abbreviate the headers, add bootstrap CIs, and fill in the pooled accuracy.
28. **"The replication confirms all three of its predictions (Table 1)."** Table 1 does not show the McNemar prediction or the margin prediction. → List the three predictions in a parenthesis, and cite App. B and App. C.
29. **"With the reference, the answer that phi-4 selects is correct 86.7% of the time instead of 98.1%"** Only the larger-effect judge is quoted, the analysis is post hoc, and there is no CI. → "Selected-answer accuracy falls from 76.2% to 68.6% (Qwen) and 98.1% to 86.7% (phi-4) [CIs]; post hoc."
30. **"about twelve times larger at best-of-64 (Section C)"** Table 6 uses the raw gap, not the headline estimator. → "(raw paired gap, App. C)".
31. **Paragraph title "Training makes it larger."** The paragraph's own last sentence contradicts it. → "Training also exploits the referenced judge", with one sentence of result and one of caveat. Move the rest to App. L.
32. **"It does not show that the reference is the cause: every control arm we trained failed its own manipulation check, across three runs, so we cannot separate a reference-specific effect from generic overoptimization (Gao et al., 2023), and our preregistered stopping rule closed the question as unresolved (Section L)."** A 50-word colon-comma-and chain with an undefined "manipulation check". → Split into two sentences and define the check ("each arm's own judge score must rise").

### Section 4 (p. 4)

33. **Section title "The score follows the reference, not the answer"** is another "not X" frame. → "Moving the reference moves the score of unchanged text".
34. **"All twelve preregistered cells confirm"** Readers cannot know what a cell is. → "(2 judges × 2 rubrics × 3 predictions: gain > 0, loss < 0, gain > neither)".
35. **"so larger judges anchor less, and none we tested stopped."** Table 8 is not monotone (3B rubric b +9.58 > 1.5B +8.73). The frontier CLI margin (+7.49) and Sonnet 5 on MACE (+5.29, "the largest referenced margin we measured anywhere") both contradict a size trend. "None we tested stopped" is clumsy. → "Within Qwen2.5, the 14B judge anchors about a third as much as the 1.5B judge; no judge we tested stops anchoring."
36. **Paragraph title "The judge overrides its own earlier verdict."** The blind and referenced scores come from independent calls, so there is no earlier verdict in context. → "Answers the judge accepts blind are still penalized." Delete the fragment "They are not." and merge.
37. **"Sonnet 5 behaves the same way (+2.79, 92% kept)."** 3194/3494 = 91.4%. → "91%". The Qwen and phi-4 filtered numbers (+4.99, 91%; +4.08, 98%) appear in no table. → Add rows to Table 7.
38. **"gave a frontier Claude judge the same 37 multi-answer tasks and the open judges' rubric, over 660 calls."** Unnamed model, unsourced task subset, unexplained call count. Why does the intro hook use a CLI with sampled integers when a Sonnet 5 API run exists? → Name the model, source the 37 tasks, and either use the API judge for the hook or explain the choice.

### Section 5 (p. 4-5)

39. **"So the reference should help at k=1 and start to hurt at k=2."** The k-pool does not show help at k=1, and the transition is close to definitional (B3). → "An anchoring judge cannot hurt at k=1; the question is how much harm appears once k=2."
40. **"The same step is positive, with its interval excluding zero, for all six judges on the synthetic grid ... ranging from +0.46 to +2.55"** Add: "6 tasks at k=1; the k>1 level alone is significant for three of six."
41. **"On the k-pool, gemma-2-9b shows the largest harm of any judge at k>1 (+1.43)."** False: Qwen2.5-7B is +1.50 on the same pool. → "the largest of the three added judges".
42. **"Its scores are nearly integer-valued, so best-of-64 ties about half of each pool at the maximum"** Table 22 gives 17.8 ties out of 64, and App. M says exactly 11 values. → Reconcile. Also mention Ministral-8B, excluded by the screen, and change "eight open judges" to "nine" everywhere.
43. **"harm keeps growing with k for Llama-8B and phi-4 and stays flat for the smaller Qwen judges, which falsified half of our preregistered grid prediction."** The registered prediction was about *margins* (Table 4, "margins grow with k"), not inflation. On the k-pool, phi-4 is not monotone (0.58, 1.54, 0.99, 1.28). → Say which quantity was falsified, and restrict "keeps growing" to the grid.
44. **"The same reference, judges, and estimator give opposite signs, and what sets the sign is whether the answer is unique."** MATH-500 and Ties differ in domain, difficulty, checker completeness, and analysis choices made after seeing data (App. E). → "consistent with uniqueness setting the sign; the k-pool and MACE isolate it."
45. **"The one judge where this did not clearly replicate is GPT-4.1"** Mistral-7B also did not, and Sonnet 5 has no k-step or MACE-step numbers in any table (Table 12 shows "---"). → Report Sonnet 5's MACE step with a CI, or drop "the one".
46. **"Which tasks inflate most? A preregistered composition experiment shows ..."** A rhetorical question opening a detour whose key term (β < 1) the appendix calls partly measurement attenuation. → Move to App. I, leaving one sentence at most.

### Section 6 (p. 5-6)

47. **Fig. 2 caption title "The judge compares a readable answer token"** → "Judges behave as if comparing a readable answer token". "(21 scalar-answer tasks)": say which pool they come from. "Preregistered.": say "pre-specified (git)".
48. **"First, the comparison is about meaning, not characters. Second, the comparison has to be cheap. Third, the answer token is necessary."** A formulaic triad. "Has to be cheap" also over-reads "30+1", which a judge may simply not treat as an answer. App. J admits the decode-cost follow-up is confounded by its framing. → Make one claim-led paragraph and mention the confound.
49. **"those closer to the reference are not penalized less, and only exact equality counts"** A double negative. → "the penalty does not shrink with numeric closeness; only exact equality matters."
50. **"and give up when that check stops being free."** Human-like verb, and "free" is not measured. → "and the effect collapses once equality requires any computation."
51. **"On 317 MBPP problems, showing a canonical solution reduced inflation relative to blind judging (−0.34 for Qwen2.5-7B and −0.57 for Qwen2.5-14B)"** The contrast is on 58 tasks, and the Qwen 7B CI includes zero. → "On the 58 MBPP tasks shared by all conditions, ... (−0.34, CI including zero; −0.57)".
52. **"That held for phi-4, where the reference helps, and failed for Qwen"** Depends on the checker fix made after registration (App. K). → Add "(after correcting a checker bug found after registration; under registered labels phi-4 is null)".
53. **"These programs are two-line list comprehensions a judge can run in its head, ... We have not tested that explanation."** Speculation followed by a disclaimer. Cut both sentences.

### Section 7 and Table 2 (p. 6-7)

54. **"closes phi-4's margin at k=16 (+1.91 to +0.03)"** No pool is named (it is the synthetic grid, 4 to 6 tasks per cell), and this paragraph mixes margins with inflation. → Name the pool and n, and report inflation for the instruction arms, or say it was not measured.
55. **"and at k=1 it costs nothing (Figure 3a)."** Qwen +0.41 [−0.09,+0.84] against +0.05, with 15 tasks. → "no significant cost at k=1 (15 tasks; Qwen's point estimate is +0.36 worse)".
56. **"It is complete for Qwen2.5-7B and phi-4, nearly complete for Qwen2.5-14B (+0.23 left), and partial for gemma-2-9b (+1.23 left, against +1.43 with a plain reference)."** phi-4 at k=16 is +0.44 [+0.13,+0.76], and gemma's reduction is 14%. → "near-complete for Qwen2.5-7B, phi-4 and Qwen2.5-14B; largely ineffective for gemma-2-9b".
57. **"Showing another judge's blind score protects Qwen and phi-4 as well as their own"** Not for Qwen: +0.38 [+0.12,+0.60] against +0.01. → State the equivalence margin, or write "mostly protects".
58. **"The judge seems to defer to an explicit number ... and it uses that number instead of the reference token."** This is the B1 problem stated by the authors themselves. → Add one sentence on what the reveal call contributes beyond returning the blind score, backed by data.
59. **Table 2.** Never referenced in the text (`\cref{tab:decide}` appears only as its label). "in decreasing order of safety" contradicts putting the bolded row last. The "Blind judging" row's weakness applies equally to BTR. The p-columns are justified without `\raggedright`, so wrapped rows blur together. "most judges tested" means 3 of 4. → Reference it in Sec. 7, order rows by the stated criterion, add a "cost vs. blind" column, use `>{\raggedright\arraybackslash}p{}` and `\addlinespace`, and write "3 of 4 judges tested".

### Related work, Limitations, Conclusion (p. 7-8)

60. **"Our results show when that remedy holds and when it backfires: a self-generated reference is still a single sample, so it should anchor just the same when many answers are valid."** An untested prediction presented as a result. → "We did not test self-generated references; our account predicts they anchor too."
61. **"We show a case where a mitigation believed to make a judge harder to exploit makes it easier"** "Believed" by whom? Cite, or → "a standard mitigation".
62. **Limitations layout.** One run-in block with six bold heads spilling from p. 7 to p. 8 is not prominent. → Use a list or a small table. Add the missing items: single-token scoring with no reasoning; rubric b instructs comparison; BTR untested on frontier judges, unique-answer pools and trained policies; one 8B generator for most pools; GPT-4.1 as the only non-Anthropic API judge.
63. **Limitations: "Every positive result comes from constraint-style or short factual questions where a program decides validity."** Contradicted by MACE's list-based entity domains. → "... where validity is decided by a program or an audited answer list."
64. **Limitations: "Two frontier judges reproduce the causal and mechanism results"** → "Sonnet 5 reproduces the causal and mechanism results; GPT-4.1 was tested only for margins and selection."
65. **Conclusion: "it survives frontier judges and the judge's own earlier verdicts, and optimization exploits it."** Plural "judges" means one model. "Earlier verdicts" is the anthropomorphism from item 36. "Optimization exploits it" leans on the unattributed training run. → "it appears in Sonnet 5 and on answers the judge accepts blind, and best-of-n selection exploits it."

### Appendix

66. **Table 6 caption "Paired referenced-minus-blind hack gap"**: "hack gap" is internal jargon and undefined. → "raw paired gap (G without permutation adjustment)".
67. **Table 20 column "M2, k>1"**: undefined label. → "Validity gate, k>1".
68. **Tables 3 and 4 (longtable)**: justified narrow p-columns produce rivers ("k-pool (preregis-tered)", "51 generation tasks built from", "Exact-oracle rotation"), plus about 30 underfull hbox warnings. → Use `>{\raggedright\arraybackslash}p{..}`.
69. **Table 10** is `\scriptsize` with six CI columns and unreadable in print. → Split by judge, or move CIs to a second line.
70. **Table 14**: the worked visible → masked column has no CIs, although Fig. 2a draws error bars for those cells. → Add them.
71. **Table 17**: margins with n=1 (JSON) are shown as numbers. → Replace with "—" and a footnote.
72. **Fig. 4 caption "The same protocol gives opposite signs."** Inflation is positive in both panels. What flips is the effect of the reference. → "Showing the reference lowers inflation on MATH-500 and raises it on Ties."
73. **App. E title "The exploratory study that started this, and the unique-answer contrast"**: casual, and it wraps. → "Exploratory Ties study and MATH-500 contrast".
74. **App. M "gemma-2-9b ... is the most anchored judge we measured"**: false globally (item 41 and B8). → "the most anchored of the five k-pool judges".
75. **Appendix contents list**: labels "I" and "M" are misaligned. **Bibliography**: Liu et al. 2023 has lowercase "rigorous" after "?". The Huang et al. entry carries "To appear at EMNLP 2026. Earlier version titled ...". AmbigQA alone has a URL. Clean these up.

---

## 5. Figures and tables

**Figure 1 (teaser). Verdict: redo.**
- **Not self-contained.** No example schematic, no fix, and two different units side by side.
- **Proposed layout:** (a) a small schematic of the divisor-of-91 prompt with blind and referenced scores for "7" and "13"; (b) the current rotation bars; (c) selected-answer accuracy vs. k for blind, reference and BTR. This puts problem → cause → fix in one figure.
- **Mechanical fixes.** Move 1b's legend out of the data, since it overlaps the k=4 error bar. Move the "below 0: reference helps" annotation off the k=1 phi-4 marker. Separate judges by color, not just dash style in the same blue. Center 1a's legend under panel a or put it inside. Use true minus signs (`axes.unicode_minus`). The gray "matches neither" bars are nearly invisible, which is fine as the point, but add a "≈0" label.

**Figure 2 (mechanism). Verdict: acceptable content, weak grammar.**
- **(a) labels.** The x tick labels mix literals ("31", "30+1") with a category name ("words"). Use "numeral 31 / words / 30+1" consistently. Label the right-hand group on the axis ("worked solution: visible / masked") instead of relying on "to the right of the line". Make it visible that the two groups come from different task sets.
- **(a) axis and colors.** The y-label "(0–10)" names a scale, not a unit; use "points". The phi-4 light blue repeats the "moved off" color from Fig. 1a.
- **(b)** connects categorical formats with lines, implying a measured ordinal axis of "comparison difficulty". Use points with error bars and no lines, or justify the ordering. Switch the y-axis to selected-answer accuracy or state what 1 SD means.

**Figure 3 (fix). Verdict: redo panel b; fix panel a.**
- **(a) caption and styling.** The caption's "(light blue, as in Figure 1b)" is false, and the colors must actually match. The legend overruns the axes frame. This is the only panel with a closed box frame, so drop the top and right spines.
- **(a) shows what the text denies.** The Qwen teal point at k=1 (+0.41) sits visibly above the reference line, which contradicts "costs nothing". Either address it in the text or show CIs more clearly.
- **(b) needs a baseline.** Add a "plain reference" bar so the reader can see that "no score" returns to that level, and a blind = 0 line label.
- **(b) needs gemma-2-9b,** the counterexample, currently only in App. M.
- **(b) scale and colors.** Match the y-range to (a) or note the difference. Teal now encodes judge, while in (a) it encodes condition; pick one mapping for the whole paper (e.g., color = condition, marker or hatch = judge).

**Table 1. Verdict: fix mechanics.** 31 pt overflow; "( SD" spacing bug; no CIs on accuracies; empty pooled cells; the header "Selected valid answer matches r" is conditional and ambiguous (→ "P(matches r | selected answer valid)").

**Table 2. Verdict: fix or remove.** Its ordering contradicts its own caption. It is never referenced. It has rivers. It overstates the fix relative to blind judging (B1). A small decision flowchart ("Can a program check validity? → Is k known to be 1? → ...") would do this better.

**Appendix tables.**
- Table 3 and Table 4: ragged-right columns needed.
- Table 6: jargon ("hack gap").
- Table 7: add the open-judge blind-certified rows.
- Table 10: illegible scriptsize.
- Table 12: Sonnet 5 inflation and step cells are "---", which undercuts "two frontier judges reproduce".
- Table 14: missing CIs.
- Table 17: n=1 cells.
- Table 20: "M2".
- Table 22: tie count disagrees with the text.
- Figure 4: caption misdescribes what flips; orange/blue is yet another color mapping.

---

## 6. What to cut or move, and what's missing from the main text

### Cut or move to the appendix
- **Training (Sec. 3, "Training makes it larger")**: leave one hedged sentence, move the rest to App. L. Remove it from the contributions and the conclusion.
- **"Which tasks inflate most?"** (the composition result): move to App. I.
- **The MBPP failed-prediction story (Sec. 6)**: two sentences are enough ("a canonical program does not anchor; a preregistered format continuum then showed harm shrinks from integer to program").
- **Several-references and worked-solution mitigations (Sec. 7)**: one clause each, or move to App. M.
- **The exploratory Ties ladder numbers (9.5 / 3.1) in Sec. 4 and the GPT-4.1 tie explanation in Sec. 5**: move to the appendix.
- **Half the paired "X and Y" per-judge decimals in prose**: put them in one compact main-text results table (rotation, selection accuracy, k-step, fix) and quote one number per claim.
- **Every "Preregistered." in captions**: replace with a consistent badge (e.g., † OSF, ‡ git).

### Missing from the main text
1. **A reasoning-judge result, and a standard third-party reference-guided prompt** (B2).
2. **The referenced rubric wording,** at least rubric b, and the fact that judges emit a single score token.
3. **BTR versus blind** on a pool where the reference helps, in accuracy units (B1).
4. **An accuracy-unit headline figure** (B4) and a precise, reconstructible definition of the estimator (in the appendix, with a one-line intuition in the main text).
5. **A prevalence estimate:** what fraction of a common math, QA or RLVR training set has k>1? Even a 200-item audit of MATH, GSM8K or a popular RL mix would anchor significance.
6. **An explicit delta against Li et al. (2025)** (what they rotated, measured and missed), plus the RLVR / model-based-verifier false-negative literature.
7. **Definitions** of the pass-rate band and "manipulation check", and where the 58-, 37- and 21-task sub-pools come from.
8. **A one-line scorecard of predictions** (confirmed / falsified / unresolved, split by OSF vs. git).
9. **A practitioner paragraph with costs:** when to enumerate, when to go blind, when BTR is worth a second call.
10. **The ~1.7 unused pages** are room for items 1, 3, 4 and a schematic Figure 1.

---

## 7. Verdict

**Would I champion it now? No.** The core finding (reference rotation moves scores of fixed correct text by about 4 points, and best-of-n selection follows) is solid and carefully measured. But the paper as submitted:
- recommends a fix that is not shown to beat the obvious baseline,
- uses judges forbidden to reason under a rubric that tells them to compare against the reference,
- headlines an opaque SD metric,
- overstates its "k=2 for 7 of 8 judges" and training claims,
- and contains at least a dozen checkable inconsistencies.

**Changes after which I would champion at 8+:**
1. **Fix vs. blind:** run BTR against blind and reference on a unique-answer pool (MATH-500) and a mixed-k pool, in accuracy units. Rewrite Sec. 7, Table 2 and the abstract to match what BTR actually buys, including "nothing over blind" if that is the result.
2. **Judge realism:** add a reasoning judge (frontier with thinking, or an open reasoning model) and a standard third-party reference-guided prompt on rotation and the k-step. Put rubric wording and the single-token protocol in the main text and in Limitations.
3. **Metric:** replace SD-unit plots with selected-answer accuracy (or false-rejection rate) with CIs in Figures 1b, 2b and 3. Define the permutation estimator precisely in the appendix.
4. **Figure 1:** rebuild as problem (example schematic) → cause (rotation) → consequence and fix (accuracy vs. k for blind, reference, BTR). Enforce one color and marker grammar across all figures.
5. **Calibration:** rewrite the abstract and bullets per items 2-7 and 13-16. Remove training from the contributions. Restate the k-boundary as "step from k=1 to k>1" with the per-judge significance caveat and the definitional point. Count Ministral-8B.
6. **Consistency:** fix every B8 item (gemma "largest", 92% → 91%, Mistral ties, GPT-4.1 "reproduces", MACE validity, "as well as their own", "costs nothing", "complete for phi-4", MBPP n and CI, 82.5%/19.6% sourcing, disclosure of the checker fix). Rerun `check_numbers.py` against the prose, not just the tables.
7. **Structure:** make section order follow the story (rotation → selection and k → mechanism → fix). Add one compact main-text results table. Move the detours listed in §6. Cut decimals in prose by about half.
8. **Positioning:** add a concrete delta against Li et al. (2025), engage the RLVR/verifier false-negative literature, and add a small prevalence audit of k>1 in a widely used dataset.
9. **Mechanics:** fix Table 1 overflow, the `\sd` spacing, "Section" vs. "Appendix" cross-refs, ragged-right table columns, undefined appendix jargon ("hack gap", "M2"), figure overlaps and minus signs, OSF vs. git labels in captions, and the bibliography nits.
