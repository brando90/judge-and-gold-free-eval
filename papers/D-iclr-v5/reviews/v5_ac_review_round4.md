# Meta-review (AC), ICLR 2027 — v5, round 4

**Paper:** "Reference Anchoring Biases LLM Judges Toward the Answer They Are Shown When Several Are Correct"

**Artifacts checked:** `main.tex` (00:14), `main.pdf` (39 pp, built 00:14:42), `appendix.tex` (00:14), `tables/labelings_gnm.tex`, `papers/analysis/r30a_*.json`, `papers/analysis/r30b_*.json` (all six), `registration_round29.md`, `registration_round30.md`, `template_iclr2027.tex`, `scripts/check_numbers.py`, `SUBMISSION.md`, and `reviews/v5_ac_review_round2.md` / `v5_ac_review_round3.md`. I re-derived every R30-B shortfall and every R30-A shift from the producer JSONs, re-ran `check_numbers.py`, and verified the page limit by rendering `main.pdf` to text and reading the page break, not by label positions. I did not rerun any model call.

---

## (a) Score

**6: marginally above the acceptance threshold. Confidence: 4.** Up from round 3's 5.

I am moving off 5 for one reason, and it is the reason this review exists: **the documented failure mode did not recur this round.** For three consecutive rounds the team fixed the previous round's overclaims and wrote fresh ones into the new prose; round 3 found the regression had reached the abstract. This round the new prose is, with one narrow exception (N-1 below), accurate. The abstract is correct end to end for the first time in four rounds, and every number in it that I could check against a producer JSON is right, including the one the team had most incentive to round in its favour.

I want to be precise about what earned the point, because the team should be able to reproduce it:

- **R3-1 fixed.** `main.tex:54` again carries "with the reference drawn at random".
- **R3-2 fixed, both halves.** "9 to 56" is arithmetically exact, spans both registered rules, and "two of those graders" correctly stops attributing the range to BrowseComp, which was never run. Verified below.
- **R3-4 fixed in substance.** §3 no longer asserts the falsified placebo; it reports it.
- **R3-8 fixed.** "only" → "almost entirely" at `main.tex:260`.
- **§6 now labels the modal rule** "the best case for the grader" and prints the first-listed arm (26 and 56), which round 3 said appeared nowhere in the main text.

That is a genuine round. It is a **low** 6, for two reasons. First, R3-3 is only half fixed and the half-fix created a fresh collision on page 4 (N-1). Second, and more structurally: **round-2 items 3, 5 and 10 have now gone untouched for two consecutive rounds**, as have R3-5, R3-6 and R3-7. The team is fixing whatever the newest review shouts loudest about and letting older items rot. Round 3 set the bar for 6 at "R3-1 through R3-4 fixed plus round-2 items 3, 5 and 10"; on a strict reading that bar is not met, since none of the three carried-over items was done. I am awarding the 6 anyway because the abstract — the thing that held the score at 5 — is now clean, and because the remaining items are each one clause of text. But I am not awarding 7, and the path to 7 is unchanged from round 3: items R3-5/6/7 plus the three carried-over clauses, and then the counter-instructed swap cell.

---

## (b) The five claimed changes, verified

### 1. Abstract, "9 to 56" — **CORRECT, and correctly scoped.** One residual framing problem.

`main.tex:54`:

> "Those benchmarks rarely contain such questions. Run verbatim on 149 factual questions that do, **with the reference drawn at random**, their graders credit 0\% to 53\% of correct answers that differ from it and score four models 30 to 67 points below answer-list accuracy; choosing the reference instead leaves **two of those graders 9 to 56 points short**."

**The number checks out.** Accuracy minus answer-list accuracy, from `ref_minus_list` in the six `r30b_*.json`:

| Grader | first-listed | modal |
|---|---|---|
| SimpleQA, GPT-4.1 | −0.258389 → 25.8 | −0.090604 → **9.1** |
| BrowseComp/HLE, o3-mini | −0.562081 → **56.2** | −0.203020 → 20.3 |
| *(our rubric, Sonnet 5)* | *−0.181208 → 18.1* | *−0.078859 → 7.9* |

Min over the four shipped-grader cells = 9.1, max = 56.2. "9 to 56" ✓.

**The exclusion of the rubric is verifiable from the low end**, which is a nice property: had the team's own rubric/Sonnet 5 been folded in, the modal cell 7.9 would have forced the low end to 8, not 9. The printed 9 is itself the evidence that the restriction to shipped graders was honoured. I checked this specifically because it is the kind of boundary a paper under space pressure quietly blurs, and it was not blurred.

**"Two of those graders"** ✓. `registration_round30.md:147-149` and the six JSON filenames confirm R30-B ran SimpleQA/GPT-4.1, HLE/o3-mini and the rubric/Sonnet 5. BrowseComp's grader was never run with a chosen reference, and the abstract no longer implies it was. This was R3-2(ii) and it is closed.

**Residual (moderate, not blocking): the range is a hull over two different reference rules, and nothing says so.** 9 comes from SimpleQA under *modal*; 56 comes from HLE under *first-listed*. **No single reference-choice policy produces both endpoints.** Under the exogenous rule the range is 26 to 56; under the best-case rule it is 9 to 20. A reader parses "9 to 56" by analogy with the "30 to 67" in the preceding clause — which *is* a homogeneous range under one condition — and will take it as across-graders under one condition. It is not.

This is not an overclaim in the paper's favour; if anything the "9" understates the failure the paper is documenting, and round 3 explicitly offered "give both and label modal as a best case" as an acceptable option. But §6 gives both arms in 25 words (`main.tex:260`), and the abstract could too. The sharper and shorter framing is the exogenous arm alone, since that is the rule that models what benchmark authors actually do: *"choosing the reference by the benchmark's own answer ordering still leaves two of those graders 26 to 56 points short."* That is one fewer number, it is the honest headline of R30-B, and it does not require the reader to hold two rules in mind.

### 2. §3 placebos and the falsification — **FIXED in substance; one element of the ask not done.**

`main.tex:177`: "…answers that stop matching it lose 26 points of credit for GPT-4.1 and 13 for Sonnet~5, against $-3$ and $-6$ points for text matching neither reference, **which for Sonnet~5 exceeds the 5 points we registered** (\cref{app:r30})."

Every number verified against `r30a_*.json`: GPT-4.1 stop −0.263889 → 26 ✓; Sonnet 5 stop −0.131944 → 13 ✓; placebos −0.031532 → −3 ✓ and −0.058559 → −6 ✓. The registered bound was "at most 5 points" (`registration_round30.md:99`), and 5.9 exceeds it ✓. The rounding 5.9 → 6 is in the honest direction.

**Both placebos are now reported and the falsification is stated.** This closes R3-4, which was the worst defect of round 3 — §3 previously asserted "text matching neither reference barely moves", the exact claim that failed. Good.

Two things the ask included that were not done, neither blocking:

- **The word "failed" or "falsified" is never used.** "Exceeds the 5 points we registered" conveys the breach, but `main.tex:175` two sentences earlier uses the paper's own better pattern — "one registered prediction … **failed** (\cref{app:ledger})". Matching that phrasing costs one word and makes the ledger discipline visible at the point of use.
- **The placebo-corrected shifts are still not reported.** Sonnet 5's stop-matching effect is −13.2 raw, −7.3 after subtracting its own −5.9 placebo: the placebo absorbs 45% of the effect for one of the two judges. The sentence now places both numbers side by side so a reader *can* do the subtraction, which is a real improvement, but the paper still never states the corrected figure.
- **Only the stop-matching direction is quoted.** Start-matching (+24.7 GPT-4.1, +17.8 Sonnet 5) is dropped entirely. This does fix round 3's complaint that the selection was *inconsistent* — both quoted numbers are now the same class — so I count it as resolved, but half the effect is now invisible in the main text.

### 3. Units, "points of credit" — **PARTIALLY FIXED, and the fix introduced N-1.** See below.

### 4. §6 modal labelling and the first-listed arm — **FIXED, except the split.**

`main.tex:260`: "…given the answer most of the four models produce, **which is the best case for the grader**, the SimpleQA grader falls 9 points short and the HLE judge 20; given \textsc{MACE}'s own first-listed answer, **26 and 56**. The HLE judge credits none of the answers that differ from its reference under either rule, so its gap narrows **almost entirely** because fewer answers differ."

All four numbers verified above ✓. "Best case for the grader" matches `registration_round30.md:144-145` verbatim in substance ✓. "Almost entirely" closes R3-8 ✓ (the matching-correct credit rate does tick up from ≈98.6% to ≈99.8%, so "only" was wrong and "almost entirely" is right).

**The split is still not mentioned, and adding the first-listed arm made that worse, not better.** The sentence opens "Choosing the reference rather than drawing it **shrinks the shortfall** without removing it". For SimpleQA under first-listed, that shrink is `chosen_minus_random.ref_minus_list` = **+0.045302 [−0.003356, +0.092282]** — the interval includes zero, P-R30B1 was **not confirmed** for that cell, and `registration_round30.md:250-252` records it as a split. The appendix reports it correctly (`appendix.tex:591-593`, "except the SimpleQA grader's under the first-listed rule, where it includes zero (**split**)"). The main text now prints "26" as one of the two first-listed shortfalls while asserting the shrink that, for that very cell, did not confirm. This is the paper's recurring shape — main text asserts what the appendix qualifies — and it is round-3 required-change #5, still open. Four words fix it: "…shrinks the shortfall, though not reliably for the SimpleQA grader under the first-listed rule…".

### 5. The relocated "Why a reference is given at all" paragraph — **the move is defensible; the new form is better; but the paragraph is now orphaned.**

Now at `appendix.tex:604-613`. Three findings.

**(i) The main text does not have a substantive gap.** I checked whether the paragraph's operational content survived, and it did, in three places: `main.tex:290` ("If the judge can answer the questions, remove any instruction to match and ask whether the answer is correct"), `main.tex:298` ("On such questions, the instruction to match can be what keeps wrong answers out"), and the recipe's third bullet at `main.tex:308`, which states both branches of the conditional explicitly. Critically, **the epistemic caveat also survives in the main text** — `main.tex:330` still reads "No experiment manipulates verification directly." So what was lost is the *synthesis* — the sentence connecting §7's two prescriptions to judge capability — not any claim or any hedge. For a paper five lines over the limit, cutting the synthesis and keeping the prescriptions and the caveat is the right triage.

**(ii) §7 still reads coherently, marginally.** The transition now runs from "A change of instruction is therefore safe only for the judges and questions on which it has been checked" (`main.tex:302`) straight into the recipe, which is a natural caveat-then-procedure sequence. The one rough edge: `main.tex:298` opens "On **such** questions", whose antecedent is now carried entirely by the paragraph heading "Questions beyond the judge" rather than by any preceding sentence. It works, but it leans on the heading.

**(iii) The relocated paragraph is unreachable from the section it belongs to — this is a NEW defect of the move.** `\cref{app:r30}` appears in `main.tex` at exactly three places: `:177` (§3), `:260` (§6) and `:329` (Limitations). **§7 (`sec:fix`, lines 277–310) does not cite `app:r30` at all** — its cross-references are to `app:r24`, `app:r26` ×2, `app:r27`, `app:acceptance`, `app:mitigation`, `app:prevalence`, `app:mace` and `fig:graders`. And the appendix's own index agrees: `appendix.tex:32` lists `app:r30` as referenced from "\ref{sec:p1}, \ref{sec:cost}" — not `sec:fix`. So a paragraph that opens "One reading connects the two prescriptions of `\cref{sec:fix}`" sits at the end of an appendix titled "The swap under a prompt that does not instruct comparison, and a chosen reference", topically unrelated to it, with no path from §7 to find it. It is filed where there was room, not where it belongs. **Fix:** one `\cref{app:r30}` at the end of §7's "Questions beyond the judge" paragraph, and add `\ref{sec:fix}` to the `appendix.tex:32` index row.

**Does the new form overclaim? No — it is materially more honest than the version round 3 credited.** It adds "plausibly depends", "We state this as a reading of our results rather than a result", and a genuine confound disclosure that the earlier version lacked: "the two settings we contrast … differ in **both at once**" (capability *and* number of correct answers). That last clause is the paper conceding something a reviewer would otherwise have to find. Credit where due.

One small overreach in the final sentence (`appendix.tex:612-613`): "**Read strictly, what the evidence supports is** that reference reliance should be decided per item rather than per benchmark." "Read strictly … supports" asserts strict entailment. What the evidence strictly supports is that the cost of reference reliance *differs between two item classes that differ along two dimensions at once* — which the previous sentence has just said. That reference reliance should therefore be decided *per item* is a reasonable prescription, not a strict entailment, and "per item rather than per benchmark" is a third claim (about the right granularity) that nothing here tests. Minor; "what the evidence supports is that reference reliance may need to be decided per item rather than per benchmark" would be exact.

---

## (b, cont.) NEW defects introduced this round

### N-1 (moderate). The §3 units fix half-landed, and put two incompatible meanings of "points" for the *same answer class* seven lines apart on page 4.

This is the one place the failure mode recurred, and it recurred *out of* the R3-3/R3-4 fix.

Rendered page 4 carries, in this order:

- Figure 2's caption (`main.tex:169`): "mean change in score **(points out of 10)** … and for answers that **match neither reference** (113 tasks; **+0.12, +0.30, +0.04**)"
- `main.tex:174`: "text the reference moves onto gains **3 to 5 points** … while correct text that **matches neither reference barely moves** (Figure 2)"
- `main.tex:177`: "…lose **26 points of credit** … against **−3 and −6 points** for text **matching neither reference**"

So on one page the class "matching neither reference" moves **+0.12 to +0.30** and also **−3 to −6**, both called "points", and the paper says it "barely moves" and separately gives it a value six times the size of the headline swap. All three statements are individually correct — the first two are the 0–10 rubric swap, the third is a percentage-point change in a binary credited share — but nothing on the page says the instrument changed.

The team did add "of credit" to the first number, which is the intended signal and I credit the intent. It does not survive: the qualifier is attached to "26 points of credit" and then **dropped** for "−3 and −6 points", which is the number that collides directly with the caption. And "points of credit" is in any case ambiguous, since the rubric's 0–10 output is also credit.

The paper knows the distinction and states it plainly — `appendix.tex:563-565`: "the two are not instrument-matched, since the rubric is a 0--10 score thresholded at 7 and the direct prompt is a binary yes or no". §3 still carries none of it. Round-3 required-change #3 asked for exactly this and it is the one blocker not closed.

**Fix (one clause, no new numbers):** "…the share of answers credited falls by 26 points for GPT-4.1 and 13 for Sonnet 5, against 3 and 6 points for text matching neither reference — a yes/no credited share, not the 0–10 score above — which for Sonnet 5 exceeds the 5 points we registered."

### N-2 (minor). `main.tex:330` is now stale with respect to R30-A.

"…and only the API judges have a second blind call as a noise control." R30-A has **no** same-prompt noise control for either judge: the draw-1 arm is a reused R26 run (`appendix.tex:540-541`), and the placebo class is the sole control — which failed for Sonnet 5. Carried over from round 3 (c)(iii), unfixed, and now slightly more misleading because §3 leans harder on R30-A than it used to.

### N-3 (minor). `SUBMISSION.md`'s TL;DR still has the exact defect R3-1 flagged in the abstract.

> "…benchmark graders run as shipped score four models **30 to 67 points below their answer-list accuracy**."

No reference-regime qualifier, no chosen-reference result. This is the text pasted into OpenReview, and abstract registration is **Sep 18** — tomorrow. The abstract was fixed; its copy was not. Two checklist boxes remain open, including the stale `supplement.zip` and the title-named PDF (`cmp main.pdf Reference_Anchoring_Biases_LLM_Judges_v5.pdf` — the two files are byte-identical in size and mtime here, but the box is still unchecked; verify and tick it).

---

## (c) Is the abstract now accurate, read end to end?

**Yes, with one carried-over scoping defect (claim 2) and the framing point in (b)(1).** I read it as a reviewer would, sentence by sentence, and checked each claim against its source.

- `:47` "35 of the 43 benchmarks…" — consistent with `main.tex:80`. The inclusion protocol for the 43 is still unstated (round 3 (f)(9)), and this is the abstract's first sentence. Unfixed, minor.
- `:49` "With one correct answer the premise holds and the reference helps, raising best-of-64 accuracy sharply" — supported by `main.tex:199` (+28.6/+30.6 on MATH-500, +29.4/+26.5 on MACE single-answer). ✓
- `:51` claim (1), "about 3 to 5 points out of 10" — matches §3 and Figure 2, and **correctly carries its unit**, which is what makes N-1's unitless "−3 and −6 points" jarring by comparison. ✓
- `:52` claim (2) — **the one real defect.** Treated below.
- `:53` claim (3), "of 843 answers two frontier judges accepted blind, 117 drop to 3 or below … against 2 on a repeated blind call" — matches `main.tex:229`. Still unlabelled as pooled across three pools (round-2 item 5, unfixed), but the abstract is a fair summary of what the body says. ✓
- `:54` — verified in (b)(1). ✓
- `:55` "judges shrink the gap on questions they can answer" — supported by `main.tex:275`, and the abstract correctly carries the "on questions they can answer" restriction that §7 depends on. ✓
- `:56` "partly by construction, since those lists define correctness" — this concession is in the abstract, which is unusually honest and should be kept. ✓
- `:57` "a low score from a reference-guided judge does not reliably mean the answer is wrong" — correctly hedged to "does not reliably mean". ✓

**Claim (2) remains over-scoped by naming GPT-4.1.** `main.tex:52`: "Correct answers that differ from the reference are graded worse against wrong answers, **for the four open judges and GPT-4.1 under every labeling we tried**." From `tables/labelings_gnm.tex`, GPT-4.1's eight cells:

| Pool | Registered | Any format | Model-read | Boxed only |
|---|---|---|---|---|
| Replication | −0.04 [−0.05,−0.02] | −0.04 [−0.06,−0.02] | −0.03 [−0.05,−0.02] | −0.02 [−0.04,−0.01] |
| $k$-pool, $k{>}1$ | −0.04 [−0.08,−0.01] | **−0.01 [−0.04,+0.00]** | **−0.01 [−0.03,+0.00]** | **−0.01 [−0.06,+0.02]** |

The *sign* is negative in all eight, so the claim is literally true as a sign claim and `main.tex:147` states it that way ("has the same sign; only its size varies"). But three of four $k$-pool intervals touch or include zero, the effects are −0.01, and the body twice tells the reader the opposite emphasis: Table 1 (`main.tex:115`) says "interval includes zero for GPT-4.1 (factual)" and the §4 verdict (`main.tex:202`) says "Two intervals include zero: GPT-4.1 on factual questions, whose falls are small everywhere". **The abstract names a judge that Table 1 flags as null.** Round-2 item 3, round-3 required-change #10, now two rounds unfixed. Cheapest honest fix: drop "and GPT-4.1" from `:52`, which costs nothing — claim (2) is carried by the four open judges, whose falls are 0.17 to 0.33.

---

## (d) The two undone items: blocking?

**Neither is blocking. I would not hold the paper for either, and I want to give the reasoning rather than just the verdict, because the team is clearly budgeting space against these.**

### Prevalence κ in the abstract — **not blocking.**

`registration_round29.md` does prescribe it: "State the exposure plainly in the abstract, not only in Limitations." But that fallback was written when the abstract carried more prevalence weight than it now does. Checking what actually reaches the abstract: the only prevalence claim there is `main.tex:54`, **"Those benchmarks rarely contain such questions."** That sentence *limits the paper's own scope* — under-hedging it costs the authors, not the reader. The κ-dependent figures that work *in the paper's favour* (5.5%, 18%, "30% to 44% of sampled NQ-open questions") are at `main.tex:266`, in §6, correctly marked post hoc with `\ph`, and κ ≤ 0.35 is disclosed at `main.tex:328`. The asymmetry matters: an unhedged claim that helps you is an overclaim; an unhedged claim that hurts you is not. So the registration's own rationale — "prevalence carries much of the 'who should care' argument" — points at §6, where the disclosure already is, not at the abstract.

I would still add it if space appears, because `registration_round29.md` is a committed document and a reviewer who reads it will ask. Four words at `:54` suffice: "rarely contain such questions (by LLM labels with low agreement)".

### "Mistral" absent from `main.tex` — **not blocking, and the right fix is not in the abstract.**

Confirmed: `grep -c Mistral main.tex` → **0**; `appendix.tex` → 6. The exclusion is legitimate and pre-specified — Mistral-7B's boxed-only cell is the table's only sign flip (**+0.01 [−0.05,+0.07]**), and it is excluded by a score-resolution screen disclosed at `appendix.tex:239` ("removes it for Mistral-7B, whose integer scores failed our score-resolution screen") with two ledger rows at `appendix.tex:183-184`. A disclosed, pre-registered exclusion reported in the appendix is not a blocking defect.

But the honesty gap is real and it is **in §2, not the abstract**. `main.tex:140` introduces the open judges as "Qwen2.5-7B and Qwen2.5-14B, phi-4, and gemma-2-9b" — exactly four, presented as the full set. A main-text reader therefore cannot learn that a fifth open judge was run and dropped from claim (2); there is no visible seam to notice. Fixing this in §2 costs ~12 words and is strictly better than fixing it in the abstract, which has no room: append to `main.tex:140` "…; a fifth, Mistral-7B, failed our score-resolution screen and is reported separately (\cref{app:grid})."

### What I would cut to make room — and there is far more room than five lines

The team cut a §7 paragraph to save five lines. **They cut the wrong thing.** `main.tex:95-97`, the Introduction's "What we find" paragraph, duplicates abstract lines 54–56 almost word for word:

| Abstract | Introduction |
|---|---|
| `:54` "Run verbatim on 149 factual questions that do, with the reference drawn at random, their graders credit 0\% to 53\% of correct answers that differ from it and score four models 30 to 67 points below answer-list accuracy" | `:95` "Run as their authors configure them, on questions with several answers and with a reference drawn at random from each answer list, the graders of SimpleQA, BrowseComp, and HLE credit 0\% to 53\% of correct answers that differ from the reference and score four models 30 to 67 points below their answer-list accuracy" |
| `:55` "Much of this comes from the instruction to match: asked instead whether the answer is correct, judges shrink the gap on questions they can answer." | `:96` "Much of this comes from the instruction to match: asking whether the answer is correct shrinks the gap where the judge can answer the question…" |
| `:56` "Given the full answer list, the graders come within a point of answer-list accuracy … though one open verifier stays far short." | `:97` "Given the full answer list, the benchmark graders come within a point of answer-list accuracy, though one open verifier stays far short" |

Three sentences, restated on the same page-spread, with the abstract's versions carrying the same numbers. On a nine-page paper this is the single largest block of pure redundancy in the main text, and cutting two of the three frees more than the five lines that forced the §7 excision — enough to restore "Why a reference is given at all" to §7 *and* buy the §2 Mistral clause, the abstract's κ hedge, the N-1 unit clause and the §6 split clause, with room left.

One caution: `:95-97` ends the Introduction, so cut the two most redundant sentences and keep a one-line "what we find" pointer, rather than deleting the paragraph wholesale.

---

## (e) Page limit — **COMPLIANT. Verified by rendering.**

`template_iclr2027.tex:131`: "There will be a strict upper limit of **9 pages** for the main text of the initial submission, with unlimited additional pages for citations."

I rendered `main.pdf` with `pdftotext -layout` and read the page break rather than trusting label positions. `pdfinfo` reports **39 pages**; `main.log` confirms "Output written on main.pdf (39 pages)".

- **Page 9** ends with the last line of Limitations: "…most registrations are timestamped commits with a verdict rule adopted afterwards **(Appendix D)**." — matching `main.tex:330`.
- **Page 10** begins with **"AI USE STATEMENT"**, which is exempt.

So the main text ends on page 9 ✓. `main.log` reports no undefined references and no overfull boxes.

**Note on remaining slack: there is essentially none.** Page 9 carries 71 non-blank rendered lines against page 8's 70, and the final text line sits immediately above the page number. Any addition to the main text must be paid for by a cut, which is why (d)'s recommendation matters — restoring the §7 paragraph without cutting `:95-97` would push Limitations onto page 10 and break the limit.

---

## Required changes, priority order

| # | Where | Change | Status |
|---|---|---|---|
| 1 | `main.tex:177` | N-1: say the 26/13 and 3/6 figures are a yes/no credited share, not the 0–10 score of `:174` and Figure 2. Round-3 item 3, still open. | **New/open** |
| 2 | `main.tex:52` | Drop "and GPT-4.1" from abstract claim (2); Table 1 and `:202` call it null. Round-2 item 3, two rounds open. | Carried |
| 3 | `main.tex:260` | Note the split: the shrink did not confirm for SimpleQA under first-listed (+0.045 [−0.003, +0.092]). Round-3 item 5, half done. | Carried |
| 4 | `main.tex:277-310` + `appendix.tex:32` | Add `\cref{app:r30}` from §7 and `\ref{sec:fix}` to the index row, so the relocated paragraph is reachable. | **New** |
| 5 | `SUBMISSION.md` | N-3: refresh the TL;DR for the reference regime and the chosen-reference result. **Abstract registration is Sep 18.** | Carried |
| 6 | `main.tex:95-97` | Cut two of the three sentences duplicating abstract `:54-56`; spend the space on items 1–4, 7–9 and the §7 paragraph. | **New** |
| 7 | `main.tex:140` | Name Mistral-7B as a fifth open judge excluded by the score-resolution screen. | Carried |
| 8 | `appendix.tex:601-602` | "design-independent" → "moved least between our two reference rules"; note the denominator moves 396 → 121. Round-3 item 6. | Carried, untouched |
| 9 | `appendix.tex:600-601` | State the credited-share range over graders that credit anything (1.1 to 5.7); note the HLE cells are pinned at 0 by the effect under discussion. Round-3 item 7. | Carried, untouched |
| 10 | `appendix.tex:576-589` | Add intervals to the R30-B table (0.519 vs 0.530 is noise); mark the rubric row as self-graded. Round-3 item 8. | Carried, untouched |
| 11 | `main.tex:54` | Optional: prefer the exogenous arm ("26 to 56 by the benchmark's own answer ordering") over the two-rule hull "9 to 56". | **New, optional** |
| 12 | `main.tex:330` | N-2: the noise-control sentence is stale for R30-A. | Carried |
| 13 | `main.tex:224`, `:229` | "on \textsc{MACE}" for phi-4/Qwen2.5-7B; "pooled" for 843/117. Round-2 item 5, two rounds open. | Carried, untouched |
| 14 | §3 | Run the counter-instructed swap cell; build the instructed / neutral / counter-instructed table. This is what moves 6 → 7. | Carried |

Items 1–7 are text-only and cost under an hour once item 6 frees the space. Items 8–10 are appendix hygiene that has survived two reviews untouched. Item 14 is one experiment on an existing harness and pool.

---

## Closing note to the authors

The thing worth saying plainly: **this round you fixed the previous round's overclaims without writing new ones.** That had not happened in three attempts, and the abstract — where round 3 found the regression — is now accurate end to end, including a boundary (the exclusion of your own rubric from "9 to 56") that I could verify only because you drew it correctly.

The residual pattern is different and more tractable: you fix what the newest review emphasises and leave older items untouched. R3-5, R3-6, R3-7 and round-2 items 3, 5 and 10 have now survived two review cycles without a single edit. Those are six clauses. The space objection is answerable — `main.tex:95-97` restates your own abstract almost verbatim, and cutting it buys everything on this list with room to spare.
