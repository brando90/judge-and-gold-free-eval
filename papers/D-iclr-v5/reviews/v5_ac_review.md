# Meta-review (AC), ICLR 2027 — v5

**Paper:** "Reference Anchoring Biases LLM Judges to Match Answers Instead of Grading Them"
**Reviewed artifacts:** `main.tex` / `main.pdf` (built 13:22), `appendix.tex` (state at 14:00:14), `appendix_extended.tex`, `papers/analysis/*.json`, `tables/*.tex`, `template_iclr2027.tex`, `SUBMISSION.md`. Diffed against `../D-iclr-v3/`.

**Note on a moving target.** `appendix.tex` was modified at 14:00:14, during this review. The threshold paragraph at `appendix.tex:372` gained two hedges ("for most judges, though not for all"; "except in bins of fewer than 15 answers") between my first and second read. Everything below is verified against the **14:00:14** state. Two criticisms I had drafted against the earlier text are withdrawn and noted as such in §(c), because the current text is correct on those points.

---

## (a) Score

**5: marginally below the acceptance threshold. Confidence: 4** (I checked every quoted number against `papers/analysis/*.json` and `tables/*.tex`; I did not rerun any analysis.)

The underlying science is unchanged from v3 and remains a 6: the phenomenon is real, cleanly isolated with a byte-identical-text manipulation, replicated across judges and three data sources, and the ledger is well above field norm. v5 makes four genuine honesty improvements to the abstract (the survey denominator, the judge-composition statement, the single-answer carve-out, the "partly by construction" caveat). I am scoring it **below** v3 anyway, for three reasons:

1. **The submission is over the strict 9-page limit** (BLOCKER 1). v3 was not. This is a desk-reject condition, and the team's own checklist item for it is unchecked.
2. **The new material reintroduces the exact failure mode the revision was meant to cure.** You asked me to hunt for the summary layer overclaiming relative to the body. Two of the six new items contain a sentence that the paper's own appendix or cited table contradicts (BLOCKERS 4 and 5). The pattern was not eliminated; it moved into the new prose.
3. **None of the three items the v3 AC named as holding the score at 6 (W1 random-draw framing, W2 RL/DPO null, W3 compare-instructing rubrics) is fixed, and none of the three v3 QA blockers is fixed.** A revision round that changes the title and abstract but leaves all six is unlikely to move a reviewer pool.

Every fix below is text-only and none needs new data. With BLOCKERS 1–5 fixed I would restore 6; with the v3 AC's T-list applied on top, 7.

---

## (b) BLOCKERS

### BLOCKER 1 — The main text exceeds the 9-page limit (desk-reject risk)

`template_iclr2027.tex:131`:

> "There will be a strict upper limit of **9 pages** for the main text of the initial submission, with unlimited additional pages for citations."

The AI use / ethics / reproducibility statements are exempt (`template_iclr2027.tex:399,416,430`); **Section 9 Limitations is not**. In `main.pdf`, Section 9 runs onto page 10 — the first seven lines of page 10 are Limitations body text, ending "…with a verdict rule adopted afterwards (Appendix D)", before the AI USE STATEMENT heading.

In `../D-iclr-v3/main.pdf`, page 10 **begins** with "AI USE STATEMENT". v3 was compliant; v5's additions (longer abstract, the new §7 paragraph, the new Limitations sentence) pushed it over.

The team already knows the rule. `SUBMISSION.md`, "Before submitting", unchecked:

> "- [ ] `latexmk -pdf main.tex` builds with no undefined references; **main text ends on or before page 9**."

Fix: recover ~7 lines. The cheapest source is the §7 paragraph named in BLOCKER 4, which needs rewriting anyway.

---

### BLOCKER 2 — §5's headline percentages are MACE-only and unlabeled, and are 2×–10× the pooled values the very next paragraph reports

`main.tex:224`:

> "Sonnet~5 and Opus~5 take back credit from 19\% and 31\% of the accepted answers that differ from the reference, and from none of the 140 that match it; at the open judges' post hoc threshold, phi-4 takes back 42\% and Qwen2.5-7B 83\%."

No pool is named. All four numbers are **MACE-only**. From `tables/r20_retest.tex`:

| Judge | MACE, k>1 | Replication | k-pool, k>1 | **Pooled** |
|---|---|---|---|---|
| Sonnet 5 | 15/81 = **18.5%** | 13/150 = 8.7% | 13/87 = 14.9% | 41/318 = **12.9%** |
| Opus 5 | 63/201 = **31.3%** | 10/211 = **4.7%** | 3/113 = **2.7%** | 76/525 = **14.5%** |

Two paragraphs later, `main.tex:229` switches silently to the pooled figures:

> "Of the 843 answers they had accepted, 2 fell to 3 or below on that second call. With the reference in front of them, 117 did."

117/843 = **13.9%**. A reader who does that division cannot reconcile it with "19% and 31%" and has no way to learn why. The abstract (`main.tex:53`) uses the pooled counts; §5 uses the largest cell. For Opus 5 the unlabeled "31%" is **11.6× its own k-pool value (2.7%)**.

The "140 that match it" in the same sentence is itself the MACE-only matching count (38 + 102), which confirms the sentence is MACE throughout — so this is a labeling omission, not a computation error. `figures/fig3_acceptance.pdf` does separate "Factual (MACE)" from "Arithmetic" rows, so the figure is fine; the prose is not.

**Fix:** insert "on MACE" into `main.tex:224`, and add the pooled or arithmetic values so the reader sees the range. As written this is selective reporting of the largest cell.

---

### BLOCKER 3 — Abstract claim (2) is stated without the judge restriction the appendix requires

`main.tex:52` (abstract):

> "(2) Correct answers that differ from the reference are graded worse against wrong answers, **in the same direction under every answer-labeling scheme we tried**."

`appendix.tex:236` contradicts the unrestricted form:

> "Grading gets worse under the registered labels and both relabelings for every open judge; keeping only boxed replies shrinks the fall to 0.07 to 0.14 and **removes it for Mistral-7B**, whose integer scores failed our score-resolution screen."

`tables/labelings_gnm.tex`, Mistral-7B, boxed-only: **+0.01 [−0.05, +0.07]** — sign flipped, interval spanning zero.

The main text gets this right at `main.tex:147` ("every grading change of **the four open judges and GPT-4.1** has the same sign"). The abstract drops the restriction. Mistral-7B is a judge the paper uses and reports; the score-resolution screen is a defensible reason to set it aside, but the abstract must say so or inherit the restriction.

**Fix:** "…in the same direction for every judge that passes our score-resolution screen, under every answer-labeling scheme we tried." (This is the v3 QA review's unfixed Mistral-7B bullet.)

---

### BLOCKER 4 — The new §7 paragraph asserts something the paper's own selection results refute

`main.tex:312` (new in v5):

> "Where the judge can answer the question, the reference tells it nothing it did not already know, and **telling it to match can only cost**."

"Can only cost" is false in the paper's own data, for the endpoint the paper itself calls the one that matters for best-of-n:

- `appendix.tex:267`: "On \textsc{MACE}'s multi-answer questions, **best-of-64 accuracy did not fall ($+2.0$ and $+6.1$~pp** for Qwen2.5-7B and phi-4, intervals including zero), so our registered loss was not confirmed."
- `tab:protocols` (`appendix.tex:546-547`), MACE Reference accuracy column: **+2.0** (Qwen2.5-7B), **+6.1** (phi-4).
- `main.tex:199`: on MACE's **single-answer** questions the reference "raises accuracy by 29.4† and 26.5~pp".
- `main.tex:204` states the general point directly: "**Selection is less exposed than grading.**"

MACE is factual questions these judges largely can answer — that is precisely why §5 can run an acceptance test on them. So on the paper's own "judge can answer it" data, with several correct answers, showing the reference **does not cost selection accuracy and may help it**. The cost is specific to *grading* (AUROC, false rejections), which is the claim the evidence supports.

There is a second, sharper contradiction. `appendix.tex:283`:

> "Across the 120 replication tasks, Qwen2.5-7B's swap size falls as its blind AUROC rises (Spearman $-0.40$ \ci{-0.53}{-0.25}): it is 5.2 and 5.4 points in the lower two thirds of tasks (mean blind AUROC 0.83 and 0.93) and **3.6 points in the top third (0.98)**. Verification is associated with a smaller effect but, in these data, **not with its absence**."

A 3.6-point swap on tasks where the judge separates correct from wrong at AUROC 0.98 is a direct counterexample to "the reference tells it nothing it did not already know" functioning as a cost-free regime boundary. The judge *can* answer and anchors anyway.

**Fix:** restrict the sentence to grading — "…and telling it to match costs grading accuracy without buying anything" — and cite `appendix.tex:283` for the residual, which is the honest version and is also more interesting.

---

### BLOCKER 5 — The new threshold paragraph's closing claim is contradicted by the table it cites as support

`appendix.tex:372` (new in v5), final two sentences:

> "On the rejection side, \cref{tab:r21-graders} reports the benchmark study at score thresholds 5, 7, and 10 rather than at a single cut, so a reader can see each threshold's values directly. **What we claim is the direction of the effects, which does not depend on where either cut-off sits.**"

`tables/r21_graders.tex` — the cited table — at threshold 10:

| Grader | Blind − list | Ref. − list | sign of (Ref − Blind) |
|---|---|---|---|
| Sonnet 5 | **−53.2** [−58.4, −47.8] | **−43.5** [−49.0, −37.9] | **reference is BETTER than blind** |
| Opus 5 | −4.8 [−7.1, −2.7] | −22.7 [−27.1, −18.4] | reference worse (as claimed) |
| Haiku 4.5 | **−48.8** [−53.2, −44.6] | **−30.5** [−34.9, −26.2] | **reference is BETTER than blind** |

At thresholds 5 and 7 the reference-versus-blind contrast is negative for all three graders. At threshold 10 it **reverses sign for two of the three**. So the direction of the paper's central contrast does depend on where the rejection cut-off sits, in the exact table offered as the demonstration that it does not.

`appendix_extended.tex:721` says so explicitly and correctly:

> "The shortfall also holds at a threshold of 5; **at a threshold of 10 every grader under-counts even blind, because blind 10s are rare.**"

I accept that under the *other* reading — "referenced accuracy is below answer-list accuracy" — the direction does hold at all three thresholds (−17.6/−22.3/−43.5, −14.9/−15.6/−22.7, −14.4/−20.1/−30.5). But "the direction of the effects", unqualified, in an appendix section that covers both the acceptance analysis (a blind-versus-reference contrast) and the benchmark scores, will be read the wrong way, and the paragraph's own framing ("On the rejection side…") invites it.

**Fix:** name the effect. "What we claim is that referenced accuracy sits below answer-list accuracy, which holds at all three thresholds; the blind-versus-reference gap narrows and reverses at a threshold of 10, where blind 10s are rare (extended appendix)." Stating the reversal costs nothing and removes an easy reviewer hit.

---

## (c) Is the new material sound?

### Item 3 — the capability-gap argument in §7: **speculation presented as derivation.** Not sound as written.

The paragraph (`main.tex:305-315`) reads as a derivation inside "How to fix it", a section where every other paragraph reports a measurement. It is unmarked, unhedged, and unregistered. Four specific problems:

**(i) The premise is asserted and is false for much of the paper's own survey.** `main.tex:308`:

> "A benchmark is worth building when current systems cannot solve its items, and an item that no system can solve is also one that no automated grader can check on its own."

The first clause is a normative claim about benchmark design with no citation and no evidence. It is contradicted by the paper's own `tab:survey` (`appendix.tex:102`), which counts SimpleQA, MT-Bench, FreshQA, CRAG and MixEval as reference-guided — all built around items models frequently answer correctly. MACE, the paper's own multi-answer testbed, ships full answer lists for questions its judges demonstrably can answer (that is what makes §5's blind-acceptance test possible). If references were "there to close a capability gap", MACE and SimpleQA would not carry them.

**(ii) The second clause conflates solving with verifying.** "An item that no system can solve is also one that no automated grader can check on its own" ignores the generation–verification gap, and is refuted one paragraph later by the paper's own recipe (`main.tex:320`):

> "**A checker exists** (constraints, tests, solvers, proof assistants): grade with it."

Constraint checkers, test suites and proof assistants check items no system can solve. That is the entire premise of the paper's arithmetic testbed (`main.tex:82`: "a checker lists every correct answer").

**(iii) The reframe trades a supported claim for a confounded one.** `main.tex:313`:

> "This also moves where the failure sits. We described it above as reuse where answers are open. More precisely, it is reuse across a capability boundary."

"Reuse where answers are open" is what the data supports: answer multiplicity is manipulated directly (the k-pool varies k ∈ {1,2,4,8,16}; MACE fixes k by construction; MATH-500 is k=1). **Capability is never manipulated.** The two "regimes" the paper contrasts — MACE multi-answer (§6) and hard HLE single-answer (`app:r27`) — differ simultaneously in judge capability, number of correct answers, benchmark, answering models, prompt set, and label provenance (the HLE labels come from HLE's own judge, which `main.tex:341` concedes). No design separates them. The paper therefore cannot say "more precisely"; the capability framing is strictly *less* well identified than the framing it replaces.

**(iv) The only within-dataset capability gradient cuts against the strong form** — `appendix.tex:283`, quoted under BLOCKER 4: anchoring shrinks but persists at 3.6 points where blind AUROC is 0.98, and the estimate is post hoc (†) and correlational.

**What to do.** The idea is worth keeping — it is the most interesting new thought in the revision — but it must be labeled. Move it to a short "Discussion / a hypothesis" paragraph, open with "We speculate", drop the two false premises in (i) and (ii), keep the item-level prescription (which follows from the measured results regardless), and state plainly that no experiment in the paper varies judge capability while holding answer multiplicity fixed. That is also where `registration_round28.md` belongs as future work. Doing this recovers most of the 7 lines BLOCKER 1 needs.

### Item 5 — the new threshold paragraph vs. the binned analysis: **mostly accurate as of 14:00:14**, with one residual and one unkept promise.

Verified clause by clause against `papers/analysis/r22c_acceptance_bins.json`, `r20d_matched_acceptance.json`, `r21a_mace_acceptance.json`:

- ✅ "calibrated separately for each judge and pool" — thresholds in `tables/r20_matched_acceptance.tex` range 8.20–9.85 across judge/pool. Accurate, and the justification given (comparability across judges with different score distributions) is the right one.
- ✅ "falls with the judge's own blind score for most judges, **though not for all**" — accurate. Non-monotone: `kpool|Qwen2.5-14B` (0.778, 0.374, 0.147, 0.276, 0.390, 0.234), `kpool|phi-4` (…0.077, 0.142, 0.153), `kpool|gemma-2-9b`, `mace|phi-4` (0.339 → 0.455 in the top bin). *This hedge was added at 14:00; the earlier text said flatly "falls as the judge's own blind score rises", which the JSON refuted. Criticism withdrawn — current text is correct.*
- ✅ "matching answers are rejected at more than 3\% only in each judge's lowest bin, **except in bins of fewer than 15 answers**" — accurate with the caveat. The two violations of the "lowest bin" rule are `kpool|Qwen2.5-7B` [5,7] (7.7%, n=13) and `kpool|Opus 5` [7,9] (14.3%, n=7), both n<15. *This caveat was also added at 14:00. Criticism withdrawn.*
- ⚠️ "**and stays above zero**" — not literally true. `repl|Opus 5`, bin [9,10): **0 of 17 rejected (0.000)**, n=17, so the n<15 caveat does not cover it. The claim holds if restricted to each judge's *top* bin (`repl|Opus 5` [10,10] is 4.7%). `appendix_extended.tex:772` carries the same unqualified wording and has the same exposure. **Fix:** "and stays above zero in each judge's top bin."
- ⚠️ "we report what happens when they move rather than defending the particular values" — only half delivered in this document. The acceptance-threshold sensitivity exists (`r21a_mace_acceptance.json`: at a 5% target, Qwen2.5-7B 83.3% → 85.0%, phi-4 41.9% → 43.0%) and is reported in `appendix_extended.tex:687`, but **not** in the condensed appendix, which points only at the binned analysis and at `tab:r21-graders`. Either add the one clause ("a 5\% threshold gives 85.0\% and 43.0\%") or soften the promise. It is one sentence and it is the paragraph's strongest argument.
- ❌ The closing sentence — **BLOCKER 5**.

### Items 1, 2, 4, 6 — brief verdicts

- **Item 2 (abstract scope commitments): sound and a real improvement.** The survey count verifies (`tab:survey`: 16+12+4+11 = 43 surveyed; 11+11+3+10 = 35 one-reference, excluding the 2 "partly"). The judge-composition phrase resolves the v3 "eleven LLM judges" defect and matches `main.tex:343`. The single-answer carve-out matches `tables/r4_math.tex` (+28.6 / +30.6). The "partly by construction" caveat matches `main.tex:284`. One nit: the abstract says "benchmarks, libraries, and RL reward pipelines" but the 43 includes 4 cloud platforms, which `main.tex:80` lists correctly — add "platforms".
- **Item 4 (single-call scoping + agentic limitation): sound.** `main.tex:143` and `main.tex:343` are consistent and honestly scoped; this closes an obvious reviewer question. The §6 subheading change is where the capability framing first appears and inherits BLOCKER 4's problem, but the §6 sentence itself (`main.tex:264`) is defensible because it is tied to a concrete contrast.
- **Item 6 (gunjal2025rar): sound, and the live wording is better than the earlier one.** `main.tex:336` now reads "where **in one surveyed pipeline** the reference is used to write the rubric", which matches `tab:survey`'s "partly" classification. (An earlier state of the file said "where the reference **often** writes the rubric", which the single survey entry did not support. Already corrected.)
- **Item 1 (title): see (d).**

---

## (d) Does the new title over- or under-claim?

**It over-claims, and it introduces a terminology defect and a novelty-collapse risk. I would not ship it.**

**1. The stated rationale for the retitle applies verbatim to the replacement.** The old title was dropped because it "asserted unconditionally something the paper's own Prediction 2 refutes on single-answer questions". The new title asserts, also unconditionally, that reference anchoring biases judges "to Match Answers **Instead of Grading Them**". On single-answer questions the paper shows the opposite — `main.tex:49`: "When a question has one correct answer the premise holds, and the reference helps: it raises best-of-64 accuracy sharply." Matching *is* grading there, and it is worth +28.6/+30.6 pp. "Instead of grading them" is also a stronger claim than "favor the correct answer they are shown": the old title named a bias; the new one names a substitution of behaviour. The scope problem was relocated, not solved. The effect additionally "mostly vanishes" for a thinking judge on arithmetic (`main.tex:179`) and for non-surface references (`tab:masking`), neither of which the title admits.

**2. "Anchoring" appears in the title and nowhere in the paper as a defined term.** `grep -i anchor main.tex` returns exactly three hits: the title (`:38`), the `kapetanovic2026anchoring` citation (`:336`), and "whether a judge … **anchors** the same way is untested" (`:343`). The paper's operational vocabulary is *swap*, *margin*, *false-rejection rate*, *grading AUROC*. The term "anchoring margin" exists only in the registration ledger's private naming (`appendix.tex:49`: "the ledger keeps the names used in the registrations, calling the swap test *rotation* and the margin the *anchoring margin*") and is explicitly *not* adopted by the main text. A reviewer will ask what "reference anchoring" is, formally, and the paper will not answer. A title noun that the body never defines is a defect on its own.

**3. Novelty-collapse risk is real and currently unmitigated.** The one work cited under that word is `kapetanovic2026anchoring`, "Anchoring bias in LLM-as-a-judge systems: Prior scores compromise evaluation independence" (CIKM 2026) — a *different* effect (judges anchoring on scores shown to them). In `main.tex:336` it sits inside an undifferentiated list of known judge biases:

> "LLM judges favor the first response…, longer responses…, their own outputs…, and **scores shown to them**~\citep{kapetanovic2026anchoring}"

A reviewer who reads the title and then this sentence has been given the impression that "anchoring bias in LLM judges" is already published, and the paper never contrasts the two. The contribution — anchoring on a shown **correct answer**, where the anchor is *true*, which is what makes it un-dismissable as sycophancy (`main.tex:336`: "except that the suggestion here is correct") — is the thing the title should be protecting and instead puts at risk.

**Recommendation.** Either drop the word, or define it and contrast it. Two options that fix scope and terminology together:

- "When Several Answers Are Correct, LLM Judges Grade the Match, Not the Answer"
- "Reference Anchoring in LLM Judges: Which Correct Answer You Show Changes the Score" — and add to `main.tex:336`: "…and scores shown to them (Kapetanovic et al., 2026); we study anchoring on a shown *answer* rather than a shown score, and on an anchor that is correct."

**Related metadata defect.** `SUBMISSION.md` still carries a round-20 TL;DR for OpenReview stating the graders "under-report models' benchmark accuracy by **13 to 40 points**". No such range appears in v5; the main text says 30 to 67 (verbatim graders, `main.tex:95`) and 10 to 22 (own rubric, `main.tex:259`). This text is pasted into OpenReview verbatim per the checklist. Update it with the title.

---

## (e) What a reviewer will object to that is NOT addressed

**All six blockers from the v3 round survive.** The v3 AC held the score at 6 on W1/W2/W3 plus the W5 inconsistency list; the v3 QA review named three blockers. v5 addresses W1 partially (the off-label half, via the prevalence sentence and carve-out; **not** the random-draw half — the abstract still reports "30 to 67 points" without "a reference drawn at random from each answer list", which appears only at `main.tex:54` and `:95`) and one of thirteen W5 bullets (the judge count). W2, W3, and QA B1–B3 are untouched. Specifically, and in order of what a reviewer will hit first:

1. **"Closes it" versus the paper's own verifier (QA B1).** `main.tex:97` and Table 1's Fix row say the full list "closes the gap for the benchmark graders", with the exception relegated to `main.tex:287`. `appendix.tex:484`: General-Reasoner's verifier with the full list "credits 67.4\% of differing correct answers but only 77.8\% of matching ones, and accepts 30.4\% of wrong answers against 8.9\%, so it stays **24.2 points short** and the registered 5-point bound failed." The new "partly by construction" caveat is a *different* caveat (circularity) and does not discharge this one. Table 1's Fix verdict ("The list works, except for one 1.5B verifier") is the honest version; the abstract's "the graders come within a point" is not, since two of the seven graded configurations are the verifiers.

2. **Every headline effect comes from a rubric that instructs comparison (AC W3).** `appendix.tex:70` concedes it: "Both default referenced rubrics invite comparison with the reference… A judge that follows the comparison instruction could therefore favor the reference because it was told to." The paper's answers (MT-Bench verbatim, the direct prompt in §5) are real but are not the headline 3–5 point swap. Until the main text carries a three-row decomposition (instructed-to-match / neutral / counter-instructed), a reviewer can reasonably say the paper demonstrates instruction-following. This is the single most damaging unaddressed objection, and the new title ("Instead of Grading Them") raises its stakes.

3. **P3's acceptance proxy rests on a check the ledger records as falsified.** The abstract (`main.tex:53`) concludes "an inability to verify them cannot alone explain the effect". The licensing assumption is that a blind 10 means verification. `appendix.tex:203`: "at most 5\% of wrong answers scored 10 blind in each pool (**falsified**: 5.1\% to 8.2\%)." `main.tex:238` discloses this honestly; the abstract does not. Table 1's P3 verdict ("Holds for every judge with an acceptance test") is also mildly circular — judges without a usable test are excluded, and the Qwen3 rows are excluded by the paper itself (`appendix.tex:370`: "those rows do not isolate acceptance").

4. **The "who should care" argument rests on labels with κ ≤ 0.35 and no human validation.** `main.tex:341` and the AI use statement ("no label was checked by human annotators"). Note that the team's own `registration_round29.md` prescribes the remedy for exactly this round: "**Fallback if human annotation is out of reach.** State the exposure plainly **in the abstract, not only in Limitations.** The prevalence figures are currently carried with more confidence in the main text than `app:prevalence` supports. This is a text change, not an experiment." v5 rewrote the abstract and did not do this. A reviewer who reaches `tab:prevalence-v2` will notice.

5. **Multiplicity, with 304 registered predictions.** `main.tex:160`: "We do not correct for multiplicity." The ledger's 202 "confirmed" includes point predictions confirmed without an interval (`appendix.tex:140`). The v3 AC asked how many; v5 does not say.

6. **The ledger totals are not machine-produced.** `scripts/check_numbers.py` flags exactly 7 numbers as "not found in any source", and two of them are `appendix.tex:153` (202) and `appendix.tex:161` (290) — the ledger totals. For a paper whose distinguishing strength is the ledger, and which states "Every number in the paper is produced by committed analysis scripts" (AI use statement), hand-maintained totals are an avoidable target. The other five flags are benign (a character count, a CI bound, call counts).

7. **Self-grading.** Three of four answering models also serve as graders. `main.tex:342` acknowledges it; the paper has the relevant measurement (`appendix.tex:514`: GPT-4.1 credited 20.7% of GPT-4.1-mini's wrong answers against 13.9% of Haiku 4.5's) but Limitations does not forward-reference it, so it reads as conceded rather than measured. One cross-reference fixes it.

8. **Minor, but a careful reviewer will list them:** "more than a dozen judges" is unverifiable from the main text (no roster; `app:setup` defers the pool table to the extended appendix, which strains the Reproducibility statement); the abstract omits "platforms" from the surveyed categories; and `tab:survey`'s 43 has no stated inclusion protocol — a sampling frame for the survey now anchors the abstract's first sentence.

---

## Summary of required changes

| # | Where | Change |
|---|---|---|
| 1 | §7 / global | Cut ~7 lines so the main text ends on page 9. Cutting/relabeling the §7 paragraph does it. |
| 2 | `main.tex:224` | Say "on MACE"; add the pooled or arithmetic values. |
| 3 | `main.tex:52` | Restrict to judges passing the score-resolution screen (Mistral-7B boxed-only is +0.01). |
| 4 | `main.tex:312` | "Can only cost" → restrict to grading; cite the +2.0/+6.1 pp selection result and the 3.6-point residual at AUROC 0.98. |
| 5 | `appendix.tex:372` | Name the effect whose direction is threshold-independent; state the threshold-10 reversal. |
| 6 | `appendix.tex:372` | "stays above zero" → "in each judge's top bin"; add the 5%-threshold sensitivity. |
| 7 | `main.tex:305-315` | Mark as speculation; drop the two false premises; state that capability is never manipulated. |
| 8 | Title + `SUBMISSION.md` | Add the scope qualifier; define or drop "anchoring"; contrast with Kapetanovic et al.; refresh the stale TL;DR. |
| 9 | Abstract / Table 1 | Carry the General-Reasoner exception with the "closes it" claim (QA B1). |
| 10 | Abstract | Add "a reference drawn at random from each answer list" to the 30–67 sentence (AC W1). |

Items 1–6 are mechanical and take under an hour. Items 7–10 are judgement calls that decide whether this sits at 5 or at 7.
