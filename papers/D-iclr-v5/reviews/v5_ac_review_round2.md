# Meta-review (AC), ICLR 2027 — v5, round 2

**Paper:** "Reference Anchoring Biases LLM Judges Toward the Answer They Are Shown When Several Are Correct"
**Artifacts checked:** `main.tex` (14:49), `main.pdf` (14:50), `appendix.tex` (14:30), `appendix_extended.tex`, `tables/*.tex`, `papers/analysis/*.json`, `scripts/check_numbers.py`, `SUBMISSION.md`, `template_iclr2027.tex`. Diffed `main.tex` and `appendix.tex` against `../D-iclr-v3/`. I re-derived the binned-acceptance claims from `r22c_acceptance_bins.json` and the threshold sensitivity from `r21a_mace_acceptance.json`; I did not rerun any model calls.

---

## (a) Score

**5: marginally below the acceptance threshold. Confidence: 4.**

Three of the five blockers are closed cleanly, and the two hardest ones (page limit, threshold-independence) are closed properly. The title now carries the scope qualifier, the Kapetanovic citation is distinguished, `SUBMISSION.md`'s stale TL;DR is fixed, and `check_numbers.py` now flags five numbers, none of them in `main.tex`. That is real work and it is well done.

I am holding at 5 rather than restoring 6 because **the failure mode this round was supposed to cure reproduced in the new prose, twice, in exactly the same form**:

1. **Blocker 4 was restated, not fixed.** "Telling it to match can only cost" became "that instruction lowering grading accuracy **without buying anything**" (`main.tex:308`). The paper's own `tables/r26_instruction.tex` shows the match instruction buying 7.1 points of wrong-answer exclusion on the exact pool the cited "correctness-prompt results" come from, and `main.tex:293` — two paragraphs earlier in the same section — reports the cost of removing it. The sentence is also ungrammatical and ships that way on page 8 of the PDF.
2. **Blocker 3's fix introduced a new overclaim of the same class.** The abstract dropped "every answer-labeling scheme" and gained "**for the four open judges and GPT-4.1**". GPT-4.1's interval includes or touches zero in three of its four $k$-pool labelings and in the factual measurement, which is what `main.tex:115` and `main.tex:202` say. The abstract now names a judge the body calls null.

Plus three new defects that are not judgement calls: the ledger total in `main.tex:160` is **290 where the ledger says 304** (NEW-1); the Limitations self-grading cross-reference points to an appendix that measures a different pipeline and different judges (NEW-3); and the "falls with the judge's own blind score for most judges" hedge is not supported at the granularity the analysis has (NEW-5).

With NEW-1 through NEW-5 fixed I restore 6. The three items that would take it to 7 (AC W3's instructed-comparison decomposition, the prevalence-κ exposure in the abstract that the team's own `registration_round29.md` prescribes, and a roster for "more than a dozen judges") remain untouched.

---

## (b) The five prior blockers, verified

### BLOCKER 1 — page limit. **CLOSED.**

`pdftotext -layout main.pdf` confirms it. Page 9 ends with the last line of Limitations:

> "…most registrations are timestamped commits with a verdict rule adopted afterwards (Appendix D)."

Page 10 begins with `AI USE STATEMENT`, which is exempt (`template_iclr2027.tex:399,416,430`). Main text is within the 9-page strict limit of `template_iclr2027.tex:131`. `main.log` reports 0 undefined references. `SUBMISSION.md`'s checklist item is now `[x]` with the verification recorded. Nothing further owed.

### BLOCKER 2 — §5's 19%/31% unlabeled. **HALF CLOSED.**

Fixed for the two API judges. `main.tex:224` now opens:

> "On \textsc{MACE}'s multi-answer questions, Sonnet~5 and Opus~5 take back credit from 19\% and 31\% of the accepted answers that differ from the reference, and from none of the 140 that match it; the constructed pools give smaller shares (\cref{tab:r20-retest})."

Verified against `tables/r20_retest.tex`: MACE $k{>}1$ 15/81 = 18.5% and 63/201 = 31.3%; matching 38 + 102 = 140; constructed pools 8.7 / 14.9 and 4.7 / 2.7, all smaller. Correct and correctly scoped.

**But the same paragraph's next sentence reintroduces the defect for the other two judges:**

> "At the open judges' post hoc threshold, phi-4 takes back 42\% and Qwen2.5-7B 83\%."

These are also MACE-only. `tables/r20_matched_acceptance.tex` gives, for those two judges: MACE $k{>}1$ 41.9% and 83.3%; Replication 4.6% and 19.2%; $k$-pool 15.4% and 25.0%. The intervening clause "the constructed pools give smaller shares" has just reset the pool in the reader's head, so the sentence that follows reads as pooled or as constructed-pool. For phi-4 the unlabeled "42%" is 9× its replication value. Insert "on \textsc{MACE}" into that sentence too.

Two secondary issues in the same paragraph:

- The `\cref{tab:r20-retest}` pointer contains **no open judge**. The table holding 41.9% and 83.3% is `tab:r20-matched`, which exists only in `appendix_extended.tex:692` — outside the submitted 38 pages. The numbers do appear in prose at `appendix.tex:368`, correctly scoped to MACE, so this is a navigation failure rather than an unsourced number, but a reviewer following the `\cref` will not find them.
- `main.tex:229` is still unlabeled and still pooled: "Of the 843 answers they had accepted, 2 fell to 3 or below on that second call. With the reference in front of them, 117 did." 117/843 = 13.9%, and a reader who does that division four lines after reading "19\% and 31\%" still has no in-text explanation. One clause ("pooled over the three pools") fixes it.

### BLOCKER 3 — abstract claim (2). **CLOSED IN FORM, REOPENED IN SUBSTANCE.** See NEW-2.

The Mistral-7B exposure is genuinely gone: `tables/labelings_gnm.tex` Mistral boxed-only is $+0.01$ $[-0.05,+0.07]$, and the abstract no longer covers it. But the replacement restriction names GPT-4.1, and that creates a fresh contradiction with Table 1. Full treatment under (c).

### BLOCKER 4 — "telling it to match can only cost." **NOT CLOSED.** See NEW-4.

The offending clause was rewritten and the paragraph gained an honest hedge ("We offer this as a reading of our results rather than a result, since we never manipulate judge capability directly", `main.tex:309`), which is the right move and I credit it. But the replacement clause makes the same empirical claim in different words and the paper's own tables refute it. Full treatment under (c).

### BLOCKER 5 — the threshold paragraph's closing claim. **CLOSED, and closed well.**

`appendix.tex:372` now reads:

> "On the rejection side, \cref{tab:r21-graders} reports the benchmark study at score thresholds 5, 7, and 10 rather than at a single cut. The reference falls short of the answer lists at all three. The comparison with blind judging does move, however: at a threshold of 10 the reference beats blind judging for Sonnet~5 and Haiku~4.5, though not for Opus~5, because a blind judge rarely awards a 10. The shortfall against the lists is what we claim; the margin over blind judging depends on where the cut-off sits."

Every clause checks out against `tables/r21_graders.tex`. Ref − list: $-17.6/-22.3/-43.5$ (Sonnet), $-14.9/-15.6/-22.7$ (Opus), $-14.4/-20.1/-30.5$ (Haiku) — negative at all three thresholds. At threshold 10, Blind − list is $-53.2$ (Sonnet) and $-48.8$ (Haiku) against Ref − list $-43.5$ and $-30.5$, so the reference does beat blind for those two; Opus is $-4.8$ against $-22.7$, so it does not. The named effect, the named reversal, and the named exception are all correct. This is the model for how the other fixes should have been written.

Secondary item in the same paragraph, **also closed**: the 5%-vs-3% acceptance-threshold sensitivity is now in the condensed appendix ("raises the \textsc{MACE} rejection shares from 83.3\% to 85.0\% for Qwen2.5-7B and from 41.9\% to 43.0\% for phi-4"), and `analysis/r21a_mace_acceptance.json` gives `Qwen2.5-7B|target5` = 0.8499 and `phi-4|target5` = 0.4304. Correct.

---

## (c) New defects introduced by the fixes

### NEW-1 (blocker-class). The ledger total in the main text is 290; the ledger records 304.

`main.tex:160`, new in v5:

> "We do not correct for multiplicity; the ledger records **290** registered predictions (\cref{app:ledger})."

`tab:ledger-totals` (`appendix.tex:149-163`) has **two** columns:

| Verdict | Through round 26 | Round 27 |
|---|---|---|
| Confirmed | 202 | 11 |
| Not confirmed | 14 | 0 |
| Falsified | 34 | 3 |
| Split | 17 | 0 |
| Not evaluable | 18 | 0 |
| Not scored | 2 | 0 |
| Excluded | 3 | 0 |
| **Total** | **290** | **14** |

`appendix.tex:142` says "\cref{tab:ledger-totals} gives the totals" — plural, both columns. The failure list already pools them: `tab:ledger-failures`'s caption says "The rows contain 14 not confirmed, **37** falsified, 17 split, 18 not evaluable, and 2 not scored predictions, and the 3 excluded ones", and 37 = 34 + 3. So the ledger's own accounting treats round 27 as part of the ledger, and the total is **304**. The main text undercounts the multiplicity denominator by 14.

This is worse than a typo because of what was done to prevent it. `SUBMISSION.md` records the new check as: "it sums each column of `tab:ledger-totals` and verifies it against that column's printed Total (290 and 14)". A per-column check cannot catch a main-text figure that equals column 1 exactly. The hardening added this round gives false assurance for precisely this number. Fix the sentence to 304 and make the checker assert that any main-text ledger total equals the sum of *both* columns.

### NEW-2 (blocker-class). Abstract claim (2) now names a judge the body calls null.

`main.tex:52`:

> "(2) Correct answers that differ from the reference are graded worse against wrong answers, **for the four open judges and GPT-4.1** under every labeling we tried."

`main.tex:115` (Table 1, P2 verdict row), on the same page spread:

> "Holds. Small for API judges on arithmetic; **interval includes zero for GPT-4.1 (factual)** and Opus~5 (one pool)"

`main.tex:202`:

> "Two intervals include zero: **GPT-4.1 on factual questions**, whose falls are small everywhere, and Opus~5 on the replication pool"

And `tables/labelings_gnm.tex`, GPT-4.1, $k$-pool $k{>}1$:

| Labeling | GPT-4.1, $k$-pool |
|---|---|
| Registered | $-0.04$ $[-0.08,-0.01]$ |
| Any format | $-0.01$ $[-0.04,+0.00]$ |
| Model-read | $-0.01$ $[-0.03,+0.00]$ |
| Boxed only | $-0.01$ $[-0.06,+0.02]$ |

Three of four touch or include zero. The factual value is $-0.063$ $[-0.133,+0.004]$ (`tables/r24_fix.tex`) — also includes zero. GPT-4.1's claim is supported only on the replication pool, and the abstract names no pool.

The body already has the correct, weaker formulation at `main.tex:147`: "every grading change of the four open judges and GPT-4.1 **has the same sign**; only its size varies". "Same sign" is true and checkable. "Are graded worse" is a claim about a distinguishable effect, and the abstract upgrades one to the other. **Fix:** either restore "under every labeling the direction is the same" wording in the abstract, or drop GPT-4.1 and say "for the four open judges under every labeling we tried; GPT-4.1's falls are in the same direction but small".

Related, and a reviewer will find it: **`main.tex` contains the string "Mistral" zero times.** Mistral-7B is a judge the paper uses and reports (`tables/labelings_gnm.tex`, `tables/main_numbers.tex`, two ledger rows at `appendix.tex:182-183`). The abstract's new "four open judges" restriction is only interpretable to someone who has read the appendix and discovered a fifth open judge — the one on which the claim fails. If the restriction is worth making, the main text must say a fifth open judge exists and why it is set aside.

### NEW-3 (blocker-class). The Limitations self-grading cross-reference points at a measurement of different judges in a different experiment.

`main.tex:336`, new in v5:

> "The benchmark study uses one answer per model, with references drawn at random; **three graders grade their own answers, which we measure (\cref{app:r27})**"

The three graders that grade their own answers in the benchmark study are Sonnet 5, Opus 5, and Haiku 4.5 — `appendix.tex:378` says so: "Sonnet~5 grades its own answers here; the other three models' answers are free of that concern."

`app:r27` (`appendix.tex:498-521`) is the **HLE** experiment of §7, with GPT-4.1 and Sonnet 5 grading GPT-4.1-mini and Haiku 4.5 answers. Its only self-preference sentence is `appendix.tex:514`:

> "GPT-4.1 credited more wrong answers from GPT-4.1-mini than from Haiku~4.5 (direct 20.7\% against 13.9\%; solve first 35.1\% against 16.6\%), so preference for its own family may contribute"

GPT-4.1 is not one of the three graders in question, GPT-4.1-mini is not an answering model in the benchmark study, and HLE is not MACE. So "which we measure (app:r27)" is wrong on the judges, the pool, and the experiment.

Worse, the paper *does* have the right measurement and does not cite it. `appendix_extended.tex:721`: "Haiku~4.5 puts Llama-3.1-8B (62.4\%) above its own answers (55.0\%)", and `tab:r22-haiku-llama` (`appendix_extended.tex:754`) tabulates the Haiku−Llama gap by grader — under Haiku 4.5 as grader it goes from $+25.5$ on the answer lists to $-7.4$ with the reference, i.e. the grader under-credits its own answers. Neither is in the submitted appendix. As it stands the sentence claims a measurement that the shipped 38 pages do not contain, for judges the cited section does not cover. **Fix:** cite `app:acceptance` for the disclosure and pull the Haiku−Llama row into the condensed appendix, or delete "which we measure".

### NEW-4 (blocker-class). §7's replacement for "can only cost" makes the same false claim, and is ungrammatical.

`main.tex:308`, rendered on page 8 of `main.pdf`:

> "…where it cannot answer the question, the instruction to match helps keep wrong answers out; where it can, our correctness-prompt results show that **instruction lowering grading accuracy without buying anything**."

First, the sentence does not parse. "show that instruction lowering grading accuracy" is missing a verb; it needs "show that instruction lowers grading accuracy" or "show that instruction lowering grading accuracy without buying anything" → recast entirely. This is in the submitted PDF.

Second, "without buying anything" is false on the paper's own data, for the pool the cited results come from. MACE is the "judge can answer it" regime by the paper's own argument (`main.tex:264`: "pointed at questions the judge can answer"). From `tables/r26_instruction.tex`, on the 149 MACE questions, wrong answers credited, with the reference:

| Judge | HLE judge verbatim (told to match) | Direct yes/no (not told to match) |
|---|---|---|
| GPT-4.1 | **0.0%** | **7.1%** |
| Sonnet 5 | **3.6%** | **10.7%** |

The match instruction buys 7.1 points of wrong-answer exclusion for both judges on exactly these questions. That is what it buys.

Third, the paper says so itself two paragraphs above, `main.tex:293`:

> "Letting the judge solve the question first had the smallest grading loss: AUROC $-0.04$ and $-0.05$ against blind, **with wrong answers wrongly credited up by at most 3.2 points**. It still rejected 5 to 7 points more of the differing correct answers"

(verified: `tables/r26_subsample.tex`, false-acceptance change $+3.2$ for GPT-4.1 verify-first and solve-first, $+1.9$ for Sonnet 5 solve-first; false-rejection change $+4.7$ and $+7.4$.) And `main.tex:275`: even the best correctness prompt leaves GPT-4.1 and Sonnet 5 "17 and 10 points short" of the answer lists on these same questions.

So within nine lines the section states the cost of dropping the match instruction and then asserts the instruction buys nothing. **Fix:** "…where it can, our correctness-prompt results show that instruction costs grading accuracy, at the price of crediting up to 7 points more wrong answers when it is removed (\cref{app:r26})." That is supported, and it is the more interesting claim.

I note for the record that the hedge added at `main.tex:309` ("a reading of our results rather than a result, since we never manipulate judge capability directly") is exactly right and closes the (c)(iii) objection from the last round. The problem is the sentence it hedges.

### NEW-5. "Falls with the judge's own blind score for most judges" is not supported at the granularity of the analysis.

`appendix.tex:372`:

> "the share of differing correct answers rejected **falls with the judge's own blind score for most judges, though not for all**"

The binned analysis has 14 judge×pool cells in `analysis/r22c_acceptance_bins.json`. Strictly falling across bins: `repl|Qwen2.5-7B`, `repl|phi-4`, `mace|Sonnet 5`, `kpool|Sonnet 5` — **4 of 14**. The other ten are non-monotone, including every Opus 5 cell (`mace|Opus 5`: 0.920, 0.750, **1.000**, 0.313), `kpool|Qwen2.5-14B` (0.778, 0.374, 0.147, **0.276**, **0.390**, 0.234), `mace|phi-4` (…0.458, 0.339, **0.455**), and `kpool|phi-4` (…0.077, **0.142**, **0.153**). **No judge is monotone in all of its pools.** The extended appendix names one of these explicitly (`appendix_extended.tex:772`: "Qwen2.5-14B is not monotone"), so the paper knows.

Under a loose "general downward trend" reading the sentence is defensible for most cells, but it does not say which reading it means, and "though not for all" implies a small minority when the minority is the majority. **Fix:** "falls over the range of blind scores for every judge, though not monotonically — Qwen2.5-14B, phi-4 and Opus 5 each rise in at least one bin."

### NEW-6. `main.tex:177`'s new cross-reference points to a section that does not contain the claim.

> "The swap is not an artifact of our own wording: it survives the verbatim MT-Bench template, which drops ``trusted'' and asks for an explanation first. **That template also asks for a comparison (\cref{sec:p3}).**"

`sec:p3` is §5, which discusses the direct prompt on MACE and never mentions the MT-Bench template. The support for the concession is `appendix.tex:70` ("It appears under the verbatim MT-Bench single-answer template (\cref{app:rotation}), which also asks for a comparison with the reference") and `app:rotation`. Retarget to `\cref{app:setup}`.

### NEW-7. The "stays above zero" scoping was applied to the condensed appendix but not to the document it points at.

`appendix.tex:372` is now correct: "stays above zero **in each judge's top bin**". I verified all 14 top bins in `r22c_acceptance_bins.json`; the smallest is `kpool|Opus 5` at 0.0265 (n=113). Closed for the condensed appendix.

But the same paragraph says "the binned analysis **in the extended appendix** shows the whole gradient behind them", and `appendix_extended.tex` is **byte-identical to v3** (`diff -q` returns equal). `appendix_extended.tex:772` still carries the unqualified form:

> "Binned by blind score, the share of such answers scored 3 or below with the reference **falls for most judges but stays above zero**, while matching answers are rejected at more than 3\% only in each judge's lowest bin … except in bins of fewer than 15 answers"

The counterexample is `repl|Opus 5`, bin $[9,10)$: **0 of 17 rejected**, n = 17, so the n<15 caveat in the same sentence does not cover it. The condensed appendix was fixed and the source it cites was not. Same for NEW-5's wording. The extended appendix ships in the supplement and is what the reproducibility statement points reviewers to.

### Checks I ran that came back clean

For completeness, these newly changed items verify:

- "35 of the 43 benchmarks, libraries, **platforms**, and RL reward pipelines" (`main.tex:47`) — `tab:survey`: surveyed 16+12+4+11 = 43; one-reference 11+11+3+10 = 35, excluding the two "partly". "platforms" correctly added; the 34 research papers are correctly excluded from the 43.
- "though one open verifier stays far short" (abstract `main.tex:56`, intro `main.tex:97`) — matches `tables/r26_verifiers.tex` ($-24.2$ with the full list) and Table 1's Fix verdict. QA B1 is now carried in the abstract. Good.
- "where the anchor is a score rather than an answer" (`main.tex:330`) and "in one surveyed pipeline the reference is used to write the rubric" — both match `tab:survey`'s "partly" classification.
- "Those three prompts do tell the judge to use the reference; only the direct prompt says nothing about it" (`main.tex:233`) — matches the prompt texts quoted at `appendix.tex:444` (chain of thought "using the reference answer"; verify first "check the response against the reference answer"; solve first "using your own answer and the reference answer") and `appendix.tex:70`. Supported. Minor: "Those three prompts" has no antecedent noun — the paragraph says "Asked to reason before deciding", never "three".
- "Our exploratory preference-training runs were inconclusive, so harm to RL training is not demonstrated" (`main.tex:336`) — consistent with the ethics statement and the ledger's training rows.
- "Whether a judge with tools or retrieval anchors the same way is untested (\cref{app:frontier} reports one exploratory command-line run, excluded for confounds)" — matches `appendix.tex:191`'s excluded (3) entry.
- "with the reference drawn at random" now in the abstract (`main.tex:54`) — closes half of AC W1.
- Abstract claim (3) dropped "so an inability to verify them cannot alone explain the effect", which removes its dependence on the falsified blind-10 check. Sensible, and `main.tex:238` still discloses the 5–8% figure.
- `SUBMISSION.md` TL;DR is refreshed to v5 with the correct 30–67 range. The stale "13 to 40 points" is gone.
- §6 and §7 numbers spot-checked: 47–53% / 30–34 points and 0–2.3% / 65–67 points (`r24_standard.tex`); "within 0.5 points" and "99\% or more" and "at most 3 of 56" (`r24_standard.tex`); "0.5 to 6 points short, with intervals that include zero for two of GPT-4.1's prompts" (`r25_types.tex`: $-3.0$ excludes, $-1.5\,[-3.0,+0.0]$ touches, $-0.5\,[-2.0,+1.2]$ includes); 5.5% / 18% / 30–44% prevalence (`prevalence_v2.tex`, `appendix.tex:121,123`). All correct.

---

## (d) Remaining claims the evidence does not support, or that contradict the appendix

**D1. The abstract vs Table 1, on GPT-4.1.** NEW-2 above. Both sides quoted there.

**D2. The main text vs the ledger, on the number of registered predictions.** NEW-1 above. `main.tex:160` "290" against `tab:ledger-totals`' 290 + 14.

**D3. §6's capability framing is unhedged and comes before the hedge.** `main.tex:309` now says "we never manipulate judge capability directly". But `main.tex:261` is a section subheading —

> "**Who should care: reuse across a capability boundary.**"

— and `main.tex:264` states it as fact, 45 lines earlier than the hedge and with no forward reference:

> "The failure is about reuse across a capability boundary: a grader written for questions that are beyond its judge, then pointed at questions the judge can answer (\cref{sec:fix})."

The hedge was placed where the paragraph was rewritten, not where the claim is asserted. A reviewer reads §6 first. Nothing in the paper manipulates capability while holding answer multiplicity fixed — MACE and the HLE set differ in benchmark, multiplicity, answering models, prompts, and label provenance simultaneously — and the one within-dataset capability gradient (`appendix.tex:283`: the swap is still 3.6 points where blind AUROC is 0.98) cuts against the strong form. Either hedge `main.tex:264` in place, or restore "reuse where answers are open" as the heading and keep the capability reading in §7 where it is labelled.

**D4. "Reference anchoring" is still a title term the body never defines.** `main.tex` uses "anchor" only in the title (`:38`), the Kapetanovic citation (`:330`), and "Whether a judge with tools or retrieval **anchors** the same way is untested" (`:337`). The operational vocabulary is swap / margin / false-rejection rate / grading AUROC, and `appendix.tex:49` explicitly says the term "anchoring margin" belongs to the private registration naming and is not adopted. The scope problem in the title is fixed by "When Several Are Correct" — credit for that — but the undefined noun is not. One sentence in §2's Measurements list ("We call this *reference anchoring*: …") closes it.

**D5. The title admits neither of the two conditions under which the effect disappears.** `tables/masking.tex`: with the reference written as an expression the swap is $+0.29$ to $+0.89$ against $+3.11$ to $+5.99$ as a numeral, and masked inside a worked solution it is $+0.05$, $+0.31$, $-0.49$, $-0.45$. `main.tex:179`: "On arithmetic, thinking before scoring removes most of the swap." Both are conceded in the body; the title claims the phenomenon unconditionally for "LLM Judges". Less severe than the v3 title's problem, but a reviewer who reads `tab:masking` will say the effect is about *surface* reference form, which is a narrower and more mechanistic claim than the title makes.

**D6. Minor, abstract line 49.** "With one correct answer the premise holds" — with one correct answer there is only one correct answer to show, so the premise ("a correct response should score the same whichever correct answer is shown") is vacuously satisfied rather than tested. What the data show is that the reference *helps selection* there, which is a different and real finding. Say that instead.

---

## (e) What a reviewer will still object to, and which is not addressed

1. **Every headline effect comes from a rubric that instructs comparison (AC W3). Still the most damaging objection.** `appendix.tex:70` concedes it in terms: "Both default referenced rubrics invite comparison with the reference… A judge that follows the comparison instruction could therefore favor the reference because it was told to." v5 improves the disclosure — `main.tex:143` now says our rubric "invites comparison", `main.tex:177` concedes the MT-Bench template does too, and `main.tex:233` concedes three of the four correctness prompts do. That is honest and it is progress. But the headline 3–5 point swap still comes only from compare-instructing prompts, and the main text still has no three-row decomposition (instructed-to-match / neutral / counter-instructed). The counter-instructed wording exists — `appendix.tex:65` quotes it: "do not compare the candidate's answer to the reference… a correct answer that differs from the reference must receive the same score" — and its result is buried in the mitigation appendix. Promoting that row into §3 would convert the single most reachable rebuttal into a result.

2. **The team's own registered remedy for the prevalence labels was not carried out.** `registration_round29.md` prescribes stating the κ exposure "**in the abstract, not only in Limitations**". The abstract still says only "Those benchmarks rarely contain such questions" (`main.tex:54`), and the whole "who should care" argument rests on labels with κ ≤ 0.35 and no human validation (`main.tex:335`; AI use statement: "no label was checked by human annotators"). Compounding it: `main.tex:263` reports "0\% to 3\%" for the three benchmarks, but `appendix.tex:123` says "had the six HLE fallbacks that involve that label gone the other way, **HLE would reach 6.0\%**". The main text reports the conservative end of a range whose other end doubles the headline, and uses it to conclude "their own leaderboards are probably little affected".

3. **"More than a dozen judges" still has no roster inside the submitted pages.** `app:setup` defers the pool table to the extended appendix (which lives in the supplement). A reviewer counting judges in `main.tex` finds nine at most and cannot confirm the abstract's first methodological claim. This also strains the Reproducibility statement. Combined with the Mistral-7B omission (NEW-2), the judge set is the least legible part of the paper.

4. **P3's acceptance proxy still rests on a check the ledger records as falsified.** `appendix.tex:203`: "at most 5\% of wrong answers scored 10 blind in each pool (**falsified**: 5.1\% to 8.2\%)." `main.tex:238` discloses it well. Table 1's P3 verdict, "Holds for every judge with an acceptance test", remains mildly circular — judges without a usable test are excluded, and the paper itself excludes the Qwen3 rows (`appendix.tex:368`: "those rows do not isolate acceptance").

5. **`tab:survey`'s 43 has no stated inclusion protocol.** `appendix.tex:90` says what categories were surveyed and that "10 checked candidates that did not [use such a judge] were dropped" for research papers, but gives no sampling frame for the 43. That number now opens the abstract.

6. **Self-grading.** Three of four answering models also grade. Beyond NEW-3's mis-citation, the measurement that exists (`appendix_extended.tex:721,754`) is not in the submitted pages at all.

7. **Multiplicity.** 304 registered predictions, no correction, and 202 of the "confirmed" verdicts include point predictions confirmed without an interval (`appendix.tex:140`). The ledger's transparency is the paper's best feature and the honest thing to do is to say what fraction of the confirmations would survive a Bonferroni or BH pass on the interval-bearing subset. One paragraph.

---

## Required changes, in priority order

| # | Where | Change |
|---|---|---|
| 1 | `main.tex:160` | 290 → 304 (both ledger columns). Extend `check_numbers.py` to assert the main-text total equals the sum of both columns, not each column against its own. |
| 2 | `main.tex:308` | Rewrite: the sentence does not parse, and "without buying anything" is refuted by `r26_instruction.tex` (0.0%/3.6% vs 7.1%/10.7% wrong credited) and by `main.tex:293` in the same section. |
| 3 | `main.tex:52` | Drop GPT-4.1 or downgrade to "in the same direction", per `main.tex:115`, `main.tex:202`, and `labelings_gnm.tex`. Name Mistral-7B somewhere in the main text so the restriction is legible. |
| 4 | `main.tex:336` | Fix the self-grading cross-reference; cite `app:acceptance`, or pull `tab:r22-haiku-llama` into the condensed appendix, or delete "which we measure". |
| 5 | `main.tex:224` | Add "on \textsc{MACE}" to the phi-4 / Qwen2.5-7B sentence; label `main.tex:229`'s 843/117 as pooled. |
| 6 | `appendix.tex:372` | "for most judges" → name the non-monotone judges (4 of 14 cells are monotone; no judge is monotone in every pool). |
| 7 | `appendix_extended.tex:772` | Apply the same "in each judge's top bin" scoping the condensed appendix received; `repl|Opus 5` $[9,10)$ is 0 of 17. |
| 8 | `main.tex:177` | `\cref{sec:p3}` → `\cref{app:setup}`. |
| 9 | `main.tex:261,264` | Hedge the capability framing where it is asserted, not only 45 lines later at `:309`. |
| 10 | Abstract | Carry the prevalence-κ exposure, per `registration_round29.md`. Define "reference anchoring" once in §2. |

Items 1–8 are mechanical and take under an hour; they are what stands between 5 and 6. Items 9–10 and the §3 decomposition in (e)1 are what stands between 6 and 7.
