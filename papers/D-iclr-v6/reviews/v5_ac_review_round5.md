# Meta-review (AC), ICLR 2027 — v5, round 5

**Paper:** "Reference Anchoring Biases LLM Judges Toward the Answer They Are Shown When Several Are Correct"

**Artifacts checked:** `main.tex` (00:36), `main.pdf` (38 pp, built 00:37), `appendix.tex` (00:30), `appendix_extended.tex` (00:52), `extended_appendix.pdf` (56 pp, 00:53), `SUBMISSION.md` (00:53), `scripts/check_numbers.py`, `tables/labelings_gnm.tex`, `registration_round27.md`, `registration_round30.md`, and `reviews/v5_ac_review_round4.md`. I verified the page limit by rendering (`pdftotext -f 10 -l 10`), not from `.aux`. I re-derived the ledger column sums independently, re-ran `check_numbers.py`, and re-checked every round-30 number against `registration_round30.md`. I did not rerun any model call.

---

## (a) Score

**6: marginally above the acceptance threshold. Confidence: 4.** Unchanged from round 4's 6 — but a *flatter* 6, and for the first time in five rounds I am holding the score rather than moving it.

The reasoning matters, so I will be explicit. Round 4 awarded the 6 for a specific reason: "this round you fixed the previous round's overclaims without writing new ones." That property **half-held** this round. No new overclaim was written into the main-text argument — the claims prose is clean, and the §6 split disclosure (claimed change 4) is a genuine, correctly scoped concession. But the team shipped **a fresh numeric contradiction inside the ledger** (N-1), and it is the *same class* of defect as the 290-vs-321 error round 4 caught: a count in one place not updated when another place changed. Round 4 named that class explicitly and the team built a checker in response — a checker that verifies the ledger *table* and does not look at the ledger *caption* eighteen lines below it. The instance was fixed; the class was not.

What genuinely improved: the extended appendix is now ledger-consistent with the paper (227/14/39 of 321 checks out exactly), 34 of 37 stale section references are corrected and I verified the resulting distribution matches the claim character for character, the Introduction duplication is gone, §6 discloses the split, and §7's relocated paragraph is back and reachable. Five of the six claimed changes are real.

What did not improve, and is why the score does not move to 7: **round-4 required change #1 — the one item round 4 called "the one blocker not closed" — is still not closed.** It was addressed by adding two words ("of credit") that round 4 had *pre-emptively rejected as insufficient* in the same paragraph that requested the fix. That is the failure mode the team was warned about in this exact place. Alongside it, round-4 items 2, 7, 8, 9, 10, 12 and 13 are untouched — items 8, 9 and 10 have now survived **three** consecutive reviews without a single character changing.

The paper is good. The science is careful, the ledger discipline is real, and the abstract is still accurate end to end apart from one carried clause. It is being held below 7 by roughly nine sentences of text that nobody has written.

---

## (b) Round-4 findings: closed / not closed

Round 4's numbered required changes, verified against current files. Line numbers are current (the file shifted by ~2 lines when the §7 paragraph was restored).

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | `main.tex:177` — say the 26/13 and 3/6 figures are a yes/no credited share, not the 0–10 score | **NOT CLOSED** (reworded only) | Now reads "against $-3$ and $-6$ points **of credit** for text matching neither reference". Round 4 pre-rejected this exact fix: "'points of credit' is in any case ambiguous, since the rubric's 0–10 output is also credit." See N-2. |
| 2 | `main.tex:52` — drop "and GPT-4.1" from abstract claim (2) | **NOT CLOSED** | `:52` still reads "for the four open judges and GPT-4.1 under every labeling we tried". Three rounds open. See N-3. |
| 3 | `main.tex:260` — note the SimpleQA/first-listed split | **CLOSED** | "— though under that rule the SimpleQA grader's shrinkage is the one case our interval does not separate from zero." Matches `registration_round30.md:239-241` (+0.045 [−0.003, +0.092], split). Correctly scoped: it *is* the only one of the six cells whose interval includes zero. |
| 4 | Add `\cref{app:r30}` from §7 **and** `\ref{sec:fix}` to the `appendix.tex:32` index row | **HALF CLOSED** | `main.tex:304` now carries `(\cref{app:r30})`, rendering as "(Appendix Q)" — the orphan is reachable. But `appendix.tex:32` still reads `& \ref{sec:p1}, \ref{sec:cost} \\` with no `\ref{sec:fix}`. See N-4. |
| 5 | `SUBMISSION.md` TL;DR — refresh for the reference regime and the chosen-reference result | **HALF CLOSED** | The regime qualifier was added: "run as shipped, **with the reference drawn at random**, score four models 30 to 67 points below". The chosen-reference result is still absent, which was the other half of the ask. |
| 6 | `main.tex:95-97` — cut the Introduction sentences duplicating the abstract | **CLOSED** (over-corrected) | All three sentences rewritten, duplication gone. But every number went with them; see N-10. |
| 7 | `main.tex:140` — name Mistral-7B as a fifth open judge | **NOT CLOSED** | `grep -c Mistral main.tex` → **0**. Two rounds open. |
| 8 | `appendix.tex:601-602` — "design-independent" → "moved least between our two reference rules"; note 396 → 121 | **NOT CLOSED, untouched** | Verbatim unchanged: "which is why we report the credited share as the **design-independent** statistic". Three rounds. |
| 9 | `appendix.tex:600-601` — credited-share range over graders that credit anything (1.1 to 5.7) | **NOT CLOSED, untouched** | Still "the credited share moves by **0.0 to 5.7** points". Three rounds. |
| 10 | `appendix.tex:576-589` — add intervals to the R30-B table; mark the rubric row self-graded | **NOT CLOSED, untouched** | The table still prints bare point estimates with no CI column and no self-graded marker. Three rounds. |
| 11 | `main.tex:54` — optional: prefer the exogenous arm over the "9 to 56" two-rule hull | **NOT TAKEN** (was optional) | `:54` unchanged. Acceptable; round 4 marked this optional and non-blocking. |
| 12 | `main.tex:332` — noise-control sentence stale for R30-A | **NOT CLOSED** | Still "only the API judges have a second blind call as a noise control." |
| 13 | `main.tex:224`, `:229` — "on MACE" for phi-4/Qwen2.5-7B; "pooled" for 843/117 | **NOT CLOSED, untouched** | `:229` still "Of the 843 answers they had accepted, 2 fell to 3 or below". Round-2 item 5, three rounds. |
| 14 | Run the counter-instructed swap cell | **NOT DONE** | Still the 6 → 7 item. |

**Score: 2 closed, 2 half closed, 9 not closed, 1 optional declined.**

### The six claimed changes, verified independently

| Claim | Verdict |
|---|---|
| 1. Cut duplicated Introduction sentences | **TRUE.** Diff confirms all three rewritten; no abstract sentence is now restated. But see N-10 — the cut removed every number from the Introduction's only results paragraph. |
| 2. Restored "Why a reference is given at all" to §7, fixing the orphaned `\cref{app:r30}` | **TRUE in the main text, INCOMPLETE in the index.** Paragraph is at `main.tex:303-304` and renders on page 8. Index row not updated (N-4). |
| 3. Attached "of credit" to the §3 placebo figures | **TRUE textually, INEFFECTIVE substantively.** The words are there; the defect they were meant to fix is not fixed (N-2). |
| 4. Disclosed the SimpleQA first-listed shrinkage interval | **TRUE and correctly scoped.** Verified against the registration. This is the best edit of the round. |
| 5. Page budget recovered by layout, not by cutting hedges or figures | **TRUE.** Diff shows `arraystretch 1.12 → 1.0`, `itemsep 2pt/1pt → 0pt` on three lists, and the "A recipe" de-duplication. No hedge, figure or interval was removed. `main.pdf` went 39 pp → 38 pp. |
| 6. Extended-appendix ledger corrected to 227/14/39 of 321, r27/r30 rows, r30 section | **TRUE.** `appendix_extended.tex:144` now reads "the ledger records 227 confirmed, 14 not confirmed, and 39 falsified, of 321 … through round 26 alone they were 202 confirmed, 14 not confirmed, and 34 falsified, of 290." Cross-checks exactly against `tab:ledger-totals`. §"The direct prompt and a chosen reference" exists at `appendix_extended.tex:935` and its numbers are identical to `appendix.tex`. **This fix is what exposed N-1.** |
| 7. 34 of 37 "Section~N of the paper" refs corrected, MACE row left | **TRUE, and verified precisely.** `grep -o` gives 37 occurrences on 35 lines, distribution Section 2×1, 3×8, 4×3, 5×3, 6×13, 7×9 — matching `SUBMISSION.md:19` exactly. No residual Section 8 or 9. `appendix_extended.tex:195` (MACE end to end) still says "Section~7 of the paper", as declared. |

---

## (c) NEW findings

### N-1 — **BLOCKING.** The two ledger tables in `appendix.tex` contradict each other. The caption was updated for round 27 and not for round 30.

`appendix.tex:154-162` (`tab:ledger-totals`), columns "Through round 26 / Round 27 / Round 30":

> Falsified & 34 & 3 & 2 \\
> Split & 17 & 0 & 1 \\

Summing: **39 falsified, 18 split.**

`appendix.tex:170`, the caption of `tab:ledger-failures`, eighteen lines below:

> "The rows contain 14 not confirmed, **37 falsified**, **17 split**, 18 not evaluable, and 2 not scored predictions, and the 3 excluded ones."

**37 ≠ 39 and 17 ≠ 18.** The arithmetic identifies the cause exactly: 34 + 3 = 37 and 17 + 0 = 17, so the caption was brought current through round 27 and then **not touched when round 30 was folded in**, even though round 30's rows *were* added to the table body (the `Swap under the direct prompt` row carries two `\textbf{falsified}` verdicts and the `Chosen reference` row carries one `\textbf{split}`).

`tab:ledger-totals` is the correct one, and I can corroborate it from outside the paper: `registration_round27.md:117` reads "R27 total: 14 predictions, 11 confirmed, 3 falsified" (no split), and `registration_round30.md:257` reads "**Tally.** 17 predictions: 14 confirmed, 2 falsified (P-R30A3 for GPT-4.1, P-R30A4 for Sonnet 5), 1 split (P-R30B1 for the SimpleQA grader)." Both match the table columns exactly. So the caption is the wrong number, not the table.

**Why this is blocking and not cosmetic.** The ledger is this paper's distinguishing asset — it is the reason the paper is at 6 rather than 4, and `SUBMISSION.md:24` says so in as many words ("a paper whose distinguishing strength is the ledger"). A reviewer who adds up the columns to check the team's discipline — exactly the reviewer this paper is written for — finds the paper's own two counts of its own failures disagreeing, and the discrepancy is *in the direction of under-reporting failures*. That is the worst possible direction for this defect to point. It is also precisely the "numeric contradiction BETWEEN documents" failure mode that shipped undetected once already.

**Fix.** `appendix.tex:170`: "The rows contain 14 not confirmed, **39** falsified, **18** split, 18 not evaluable, and 2 not scored predictions, and the 3 excluded ones."

**Second fix, more important than the first.** `scripts/check_numbers.py:65-104` sums each column of `tab:ledger-totals` against its printed Total and is explicitly written to be round-count-agnostic ("Any number of verdict columns: the table gains one per round, so do not hardcode two"). It does not parse the `tab:ledger-failures` caption. Extend it to parse the five counts out of that caption and assert them against the row sums of `tab:ledger-totals`. Without that, this recurs at round 31.

### N-2 — **BLOCKING.** Round-4 item 1 was closed by adding two words that round 4 had already rejected. Page 4 still carries two incompatible meanings of "points" for the same answer class.

Rendered page 4 (`pdftotext -f 4 -l 4 -layout`) carries, in this order:

- line 177-178, Figure 2's caption: "mean change **in score (points out of 10)** … and for answers that **match neither reference** (113 tasks; **+0.12, +0.30, +0.04**)"
- line 68 of the render (`main.tex:174`): "…gains 3 to 5 points and text it moves off loses about as much, while correct text that **matches neither reference barely moves**"
- lines 80-82 of the render (`main.tex:177`): "answers that stop matching it lose **26 points of credit** for GPT-4.1 and 13 for Sonnet 5, against **−3 and −6 points of credit** for text **matching neither reference**"

So one rendered page still says the class "matching neither reference" moves **+0.12 to +0.30** and also **−3 to −6**, calls both "points", says it "barely moves", and separately gives it a value six times the headline swap. Nothing on the page says the instrument changed between the two.

The team's edit attached "of credit" to the second figure as well as the first — a real improvement over round 4, where the qualifier was dropped halfway. But round 4 rejected this fix *in advance*, in the same finding: "'points of credit' is in any case ambiguous, since the rubric's 0–10 output is also credit." That is correct, and it is why the collision survives: Figure 2's 0–10 rubric score is also a measure of credit, so "points of credit" does not distinguish the two instruments. The distinguishing fact — that one is a 0–10 score and the other a binary credited share — is stated plainly in the paper's own appendix at `appendix.tex:563-565` ("the two are not instrument-matched, since the rubric is a 0--10 score thresholded at 7 and the direct prompt is a binary yes or no") and still appears nowhere in §3.

This is round-3 item 3, round-4 item 1, and now round-5 N-2 — **three rounds on one clause.**

**Fix (one clause, no new numbers, fits the line):** `main.tex:177` → "…answers that stop matching it lose 26 points for GPT-4.1 and 13 for Sonnet 5 — a share of answers credited yes or no, not the 0–10 score above — against 3 and 6 points for text matching neither reference, which for Sonnet 5 exceeds the 5 points we registered."

### N-3 — **BLOCKING.** Abstract claim (2) still names a judge that the paper's own Table 1 flags as null.

`main.tex:52`:

> "(2) Correct answers that differ from the reference are graded worse against wrong answers, **for the four open judges and GPT-4.1** under every labeling we tried."

From `tables/labelings_gnm.tex`, GPT-4.1's four $k$-pool cells are **−0.04 [−0.08,−0.01]**, **−0.01 [−0.04,+0.00]**, **−0.01 [−0.03,+0.00]**, **−0.01 [−0.06,+0.02]** — three of four touch or include zero, and the effects are one hundredth of an AUROC. Meanwhile `main.tex:115` (Table 1) tells the reader "interval includes zero for GPT-4.1 (factual)" and `main.tex:202` says "Two intervals include zero: GPT-4.1 on factual questions, whose falls are small everywhere."

The sign claim is literally defensible and `main.tex:147` states it correctly as a sign claim. But the **abstract** asserts the effect *for* a judge that the body twice characterises as null. A reviewer who reads the abstract and then Table 1 finds them in tension on page 1 and page 3. Round-2 item 3, round-3 item 10, round-4 item 2 — **three rounds.**

**Fix:** delete "and GPT-4.1" from `:52`. It costs three words, the claim is carried entirely by the four open judges (falls of 0.17 to 0.33), and it removes the tension for free.

### N-4 — NON-BLOCKING. The §7 → appendix path was built in one direction only.

`main.tex:304` now cites `\cref{app:r30}`, which closes the orphan. But `appendix.tex:32`, the appendix's own index row, is unchanged:

> `\ref{app:r30} & The swap under a prompt that does not instruct comparison, and a chosen reference & \ref{sec:p1}, \ref{sec:cost} \\`

The index still tells a reader that Appendix Q supports §3 and §6 only, when it now also carries the material behind §7's closing paragraph — including the confound disclosure ("differ in both at once") that exists *only* there. Round-4 item 4 asked for both halves; one was done.

**Fix:** `\ref{sec:p1}, \ref{sec:cost}, \ref{sec:fix}`.

### N-5 — NON-BLOCKING. `SUBMISSION.md:29` states the wrong page count for the extended appendix.

> "the shipped sources compile from a fresh folder to a 38-page paper and a **54-page extended appendix**"

`pdfinfo extended_appendix.pdf` reports **56 pages**. The round-30 section (`appendix_extended.tex:935-1016`) and the two new ledger rows added two pages. The "38-page paper" half is now correct (it was 39 at round 4 and is 38 now), which is a good sign the line was partially refreshed — but the appendix half was not re-measured.

### N-6 — NON-BLOCKING. `SUBMISSION.md:29` contradicts `SUBMISSION.md:26` about the flag count.

Line 29: "`check_numbers.py` runs in the supplement layout and reports **the same five flags** as the project copy."
Line 26: "Scanning that file takes the run from 5 flags to **15**."

I ran it: **15 numbers not found**. Line 26 is right and line 29 is stale — it was written when the checker scanned only `appendix.tex`. Two claims about the same script, in the same checklist, three lines apart, disagreeing. Note this bullet is also the one unchecked box that gates the submission, so it will be read.

### N-7 — NON-BLOCKING. `SUBMISSION.md:24` describes the checker as verifying two columns; it verifies three.

> "it sums each column of `tab:ledger-totals` and verifies it against that column's printed Total **(290 and 14)**"

The run prints three lines — `ledger column 1: rows sum to 290`, `column 2: … 14`, `column 3: … 17` — and the script's own comment at line 78 says "Any number of verdict columns: the table gains one per round, so do not hardcode two." The prose hardcodes two. Minor, but it is documentation of the one script the team relies on to prevent N-1-class defects.

**Fix:** "(290, 14 and 17)".

### N-8 — NON-BLOCKING. A missing newline in `SUBMISSION.md:23` swallows a checklist item.

Line 23 ends:

> "…it was left untouched rather than guessed.**- [x]** `python scripts/make_figures.py && python scripts/make_tables.py` regenerated from current…"

The `- [x]` for the figures/tables regeneration item is glued to the end of the preceding prose paragraph with no line break, so in any Markdown renderer it is not a checklist item at all — it reads as a sentence fragment mid-paragraph. On a checklist whose purpose is that nothing is missed before a Sep 25 deadline, an item that cannot be ticked because it is not rendered as an item is worth thirty seconds.

**Fix:** insert a newline before `- [x]`.

### N-9 — NON-BLOCKING. §3 prints two placebo figures side by side; one of them is indistinguishable from zero and the text does not say so.

`main.tex:177`: "against $-3$ and $-6$ points of credit for text matching neither reference, which for Sonnet 5 exceeds the 5 points we registered".

From `appendix.tex:551,555`, the two placebos are GPT-4.1 **−0.032 [−0.089, +0.027]** and Sonnet 5 **−0.059 [−0.107, −0.011]**. GPT-4.1's interval **includes zero**; Sonnet 5's does not. `registration_round30.md:215` records exactly this: P-R30A4 "confirmed for GPT-4.1; **falsified for Sonnet 5**."

The sentence presents −3 and −6 symmetrically, then immediately invites the reader to compare them against a registered 5-point bound — so the reader is asked to weigh a real movement against one that is noise, with no signal that they differ in kind. Note this one runs *against* the authors: the GPT-4.1 placebo is a clean control, and reporting it unqualified makes the paper's own control look dirtier than it is. Fixing it is free and slightly favourable.

**Fix:** "…against $-6$ points of credit for Sonnet 5's text matching neither reference, which exceeds the 5 points we registered, and $-3$ for GPT-4.1, whose interval includes zero."

### N-10 — NON-BLOCKING (readability). The Introduction's "What we find" now contains no numbers at all, and leads with a pronoun whose antecedent is 14 words back.

Rendered page 2:

> "**What we find.** All three predictions hold (Table 1), and the effect matters in practice. In the graders of SimpleQA, BrowseComp, and HLE, run as their authors configure them, **it** opens a wide gap between **what a model scores and what its answers are worth** (Section 6). Much of that gap comes from the instruction to match: asking whether the answer is correct shrinks **it** where the judge can answer the question…"

Round 4 asked the team to "cut the two most redundant sentences and keep a one-line 'what we find' pointer." They instead kept all three sentences and removed every quantity from them. The duplication is genuinely gone — that part worked — but the paragraph that survived is strictly weaker than either version:

- **"it opens a wide gap"** — the antecedent is "the effect", 14 words and one long parenthetical earlier. The reader has to reach back past "the graders of SimpleQA, BrowseComp, and HLE, run as their authors configure them" to find it. Two "it"s follow in the next sentence with a *different* antecedent ("that gap").
- **"what a model scores and what its answers are worth"** — this is the paper's central quantity stated as a riddle. The old version said "30 to 67 points below their answer-list accuracy", which a skimming reviewer can act on.
- The result: the Introduction of a paper whose headline is a 30-to-67-point effect now states no effect size anywhere. On a nine-page submission, the Introduction is the second thing an AC reads after the abstract, and it is now the least informative paragraph in §1.

**Fix (restores one number, still shorter than the original three sentences):** "…run as their authors configure them, the effect opens a wide gap: four models score 30 to 67 points below what their answers are worth against the full answer lists (Section 6)." Then keep the two following sentences as they are.

### N-11 — NON-BLOCKING (readability). The new §6 clause is correct but hard to parse, and uses a non-standard phrase for a standard concept.

Rendered page 7, `main.tex:260` — one sentence, 76 words, four clauses, two reference rules, four numbers and an em-dash aside:

> "Choosing the reference rather than drawing it shrinks the shortfall without removing it: given the answer most of the four models produce, which is the best case for the grader, the SimpleQA grader falls 9 points short and the HLE judge 20; given MACE's own first-listed answer, 26 and 56 — though under that rule the SimpleQA grader's shrinkage is **the one case our interval does not separate from zero**."

Two issues, both small:

1. **"our interval does not separate from zero"** is not the phrase anyone uses. The paper's own verdict rule (`appendix.tex:141`) says "the 95\% interval **excludes** zero", and `appendix.tex:592-593` says "**includes zero**". A reader who has internalised the paper's vocabulary hits an unfamiliar construction at the most important qualification in the paragraph.
2. The reader must hold two reference rules, four numbers and a null result in one sentence. The qualification also arrives *after* the flat assertion "shrinks the shortfall without removing it" that it partly undercuts.

**Fix:** end the numbers at "26 and 56." and start a new sentence: "Under the first-listed rule, though, the SimpleQA grader's shrinkage is the one cell whose interval includes zero." Same length, two sentences, standard vocabulary, and the caveat gets its own clause.

### N-12 — NON-BLOCKING. §7's closing prescription is stated more flatly in the main text than in the appendix version round 4 criticised, and its confound disclosure is not co-located.

`main.tex:304`: "We offer this as a reading rather than a result (\cref{app:r30}): **reference reliance should be decided per item, not per benchmark.**"

Round 4 flagged the appendix's "Read strictly, what the evidence supports is that reference reliance should be decided per item rather than per benchmark" as asserting strict entailment, and recommended "may need to be decided". The team removed that sentence from the appendix — good — but the prescription moved into the main text in its **barest** form, as a flat "should", now carrying the weight for both documents. It is hedged by the preceding clause ("a reading rather than a result"), which is why this is non-blocking rather than an overclaim. But the substantive caveat — that the two settings being contrasted differ in judge capability *and* number of correct answers simultaneously, so nothing here isolates the mechanism — now lives only at `appendix.tex:606-608`, which §7's reader reaches only via the `\cref` and which the index row (N-4) does not advertise.

**Fix:** "…rather than a result (\cref{app:r30}): reference reliance may need to be decided per item rather than per benchmark." One word, and it matches the epistemic status the same sentence has just claimed for itself.

---

## (d) Page limit — **COMPLIANT. Verified by rendering.**

`template_iclr2027.tex:131` sets "a strict upper limit of **9 pages** for the main text of the initial submission, with unlimited additional pages for citations."

`pdfinfo main.pdf` → **38 pages** (down from 39 at round 4). Rendering with `pdftotext -f 10 -l 10 main.pdf`:

- **Page 9** ends with Limitations: "…and most registrations are timestamped commits with a verdict rule adopted afterwards (Appendix D)." — matching `main.tex:332`.
- **Page 10 begins with "AI USE STATEMENT"**, followed by ETHICS STATEMENT, REPRODUCIBILITY STATEMENT and REFERENCES — all exempt.

**Main text ends on page 9. Compliant.** `main.log` reports 0 undefined references and 0 overfull boxes; `extended_appendix.log` likewise.

**Slack: none.** Page 9 renders 72 non-blank lines against page 8's 72. The claimed change 5 is confirmed — the budget was recovered by `arraystretch 1.12 → 1.0` on `tab:summary`, `itemsep → 0pt` on three lists, and the "A recipe" de-duplication, with no hedge, figure, interval or caveat cut. That was the right way to pay for it. But it means every fix above must again be paid for. The good news: N-2, N-3, N-4, N-9 and N-12 are collectively **net negative** in length (N-3 deletes three words, N-12 changes one), and N-1 and N-5 through N-8 are outside `main.tex` entirely. Only N-10 and N-11 cost lines, and N-10's suggested form is shorter than what it replaces.

---

## (e) `check_numbers.py`

Runs clean at **15 flags**, as `SUBMISSION.md:26` documents: 5 in `appendix.tex` (420, +4.69, 7152, 1011, 1192) and 10 in `appendix_extended.tex` (420, 695, 825, 1200, +4.69, 82, 1192, 58.9, 7152, 405), of which four duplicate `appendix.tex` values already cleared. Each is accounted for in the checklist and each is a call count, a caption CI bound or a character-length rule — none is a claim. The three ledger column sums verify (290, 14, 17). This is good hygiene and it matches its documentation, apart from N-6 and N-7.

Its one gap is N-1: it checks the ledger table against itself and does not check the neighbouring caption that restates the same counts in prose.

---

## (f) What is genuinely strong — do not break these

1. **The ledger, and the fact that failures are reported in the main text.** `main.tex:175` ("one registered prediction … failed"), `:204` ("our registered loss there was not confirmed"), `:283` ("Our registered bound of 3 points … still failed"), `:273` ("outside our registered bound"). Very few submissions do this. N-1 is a defect *of* this asset, not evidence against it — fix the caption, keep the practice.
2. **The §6 split disclosure (claimed change 4).** "though under that rule the SimpleQA grader's shrinkage is the one case our interval does not separate from zero" is exactly the concession a careful reviewer looks for and rarely finds. Keep it; only restyle per N-11.
3. **The abstract's self-limiting sentences.** `:54` "Those benchmarks rarely contain such questions" and `:56` "partly by construction, since those lists define correctness" both *cost* the authors and both survived five rounds of page pressure. They are a large part of why this paper reads as honest.
4. **The mechanical-narrowing analysis at `appendix.tex:596-599`.** "It credits 0.000 of the correct answers that differ from its reference under every rule, so its gap falls only because fewer answers count as differing, 121 under the modal rule against 396 under the random draw." This is the team pre-emptively dismantling its own most favourable-looking result. It is the best paragraph in the appendix.
5. **The confound disclosure at `appendix.tex:606-608`** ("differ in both at once"). Keep it; make it reachable (N-4).
6. **The 34-of-37 section-reference repair.** Fixed per reference rather than by a blanket offset, with the distribution documented and independently verifiable — I checked it and it matches exactly. That is how this kind of cleanup should be done and recorded.
7. **The page-budget discipline of claimed change 5.** Recovering a page through `arraystretch` and `itemsep` rather than by deleting hedges is the correct trade and should be the template for paying for the fixes above.

---

## Required changes, priority order

| # | Where | Change | Status |
|---|---|---|---|
| 1 | `appendix.tex:170` | N-1: caption must read 39 falsified, 18 split. **Then extend `check_numbers.py` to assert the caption against the table.** | **New, BLOCKING** |
| 2 | `main.tex:177` | N-2: name the instrument (yes/no credited share, not the 0–10 score). Round-3 item 3, round-4 item 1, third round open. | **Carried, BLOCKING** |
| 3 | `main.tex:52` | N-3: delete "and GPT-4.1". Round-2 item 3, third round open. | **Carried, BLOCKING** |
| 4 | `appendix.tex:32` | N-4: add `\ref{sec:fix}` to the `app:r30` index row. | Carried, half done |
| 5 | `SUBMISSION.md:23,24,29` | N-5/6/7/8: 56-page appendix; 15 flags not 5; "(290, 14 and 17)"; newline before the glued `- [x]`. **Abstract registration Sep 18.** | **New** |
| 6 | `main.tex:177` | N-9: GPT-4.1's placebo interval includes zero; say so. | **New** |
| 7 | `main.tex:95-97` | N-10: restore one effect size to the Introduction; fix the "it" antecedent. | **New** |
| 8 | `main.tex:260` | N-11: split into two sentences; "includes zero" not "does not separate from zero". | **New** |
| 9 | `main.tex:304` | N-12: "should be decided" → "may need to be decided". | **New** |
| 10 | `main.tex:140` | Name Mistral-7B as the fifth open judge excluded by the score-resolution screen. | Carried ×2 |
| 11 | `appendix.tex:601-602` | "design-independent" → "moved least between our two reference rules"; note 396 → 121. | Carried ×3, untouched |
| 12 | `appendix.tex:600-601` | Credited-share range over graders that credit anything (1.1 to 5.7); note HLE is pinned at 0 by the effect under discussion. | Carried ×3, untouched |
| 13 | `appendix.tex:576-589` | Add intervals to the R30-B table; mark the rubric row self-graded. | Carried ×3, untouched |
| 14 | `main.tex:332` | Noise-control sentence is stale for R30-A. | Carried ×2 |
| 15 | `main.tex:224`, `:229` | "on MACE" for phi-4/Qwen2.5-7B; "pooled" for 843/117. | Carried ×3, untouched |
| 16 | §3 | Run the counter-instructed swap cell. This is what moves 6 → 7. | Carried |

Items 1–9 are text-only and net roughly zero lines. Items 11–13 have survived three reviews without an edit.

---

## Closing note to the authors

Two things, and I want them weighted differently.

The first is small and fixable: **you closed round-4 item 1 with the exact two words that round-4 item 1 told you would not close it.** Round 4 wrote, in the finding itself, "'points of credit' is in any case ambiguous, since the rubric's 0–10 output is also credit" — and then "of credit" is what got added. When a review pre-rejects a fix, adding it anyway costs a whole round. Read the fix the finding proposes, not just the words it quotes.

The second is structural and is the real message of this round. Round 4 caught a stale count (290 vs 321) in the extended appendix, and you did something better than fixing it: you extended `check_numbers.py` to scan that file, and you wrote down why the checker could not have caught it alone. That was the right instinct. But the guard you built checks the ledger *table* against itself, and the very same round-30 integration left the ledger *caption* eighteen lines below saying 37 and 17 where the table says 39 and 18. **You fixed the instance and generalised the tooling one notch short of the class.** The caption is one line. The checker extension that makes it impossible to recur is perhaps fifteen. Do the second one, or round 6 finds the third instance somewhere neither of us has looked yet.

What is not in doubt: the science, the ledger discipline, and the willingness to print your own failures in the main text. Five of your six claimed changes this round were real, and the sixth was real in the text and merely insufficient in effect. The distance from here to a 7 is item 16 plus about nine sentences, most of which are shorter than what they replace.
