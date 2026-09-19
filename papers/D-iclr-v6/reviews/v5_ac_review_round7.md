# Meta-review (AC), ICLR 2027 — v5, round 7

**Paper:** "Reference Anchoring Biases LLM Judges Toward the Answer They Are Shown When Several Are Correct"

**Artifacts checked:** `main.tex` (01:44), `main.pdf` (39 pp, 01:45), `appendix.tex` (01:21), `appendix_extended.tex` (01:49), `extended_appendix.pdf` (56 pp, 01:50), `SUBMISSION.md` (01:52), `scripts/check_numbers.py` (01:41), `scripts/check_cross_doc.py` (01:52), all 69 `tables/*.tex`, `registration_round30.md`, `supplement/README.md`, commit `1105603`, and `reviews/v5_ac_review_round6.md`. Page limit verified by **rendering** (`pdftotext -f 9 -l 10`), never from `.aux`. I ran both scripts; re-derived the R30-A and R30-B tables against `registration_round30.md`; cross-checked every number in `main.tex` against `appendix.tex`, `appendix_extended.tex` and all 69 table fragments with a script; and **tested both checkers against deliberately injected defects** rather than only against the clean tree. I did not rerun any model call.

---

## (a) Score

**7: good paper, accept. Confidence: 4.** Unchanged from round 6's **7**.

Held rather than raised, and held rather than lowered. What was genuinely done: the four cross-document defects are fixed, `check_cross_doc.py` is real, and the team **self-found two defects round 6 had not** (the 1,011/1,192 disclosure and Qwen2.5-7B's 28.1% figure, both missing from the extended appendix entirely). The `check_numbers.py` guard work is the best engineering of the round — I perturbed the guarded sentence and it correctly printed `LEDGER GUARD NOT FOUND` instead of failing silent (N-4 closed, verified by experiment, not by reading).

Why not 8. Round 6 set the bar at "item 16 plus **a real cross-document number sweep, not just the two instances below**." The sweep was built for one pair of files and **I found a fourth instance of the identical class in a pair it does not cover** — `main.tex`'s Figure 2 caption against the table it cites (F-1). The class is better covered, not closed. Item 16 remains correctly undone.

Why not 6. Two of six required text changes were implemented in a way that misses their point, one of them creating a new main-text overclaim (F-2, F-3); and `SUBMISSION.md:35` now repeats, *in the exact sentence round 6 named*, the exact failure round 6 named (F-4). But none of this touches the argument. The science, the ledger, and the practice of printing falsified predictions in the main text are intact.

**8 requires:** F-1 through F-4 fixed, item 16 run, and the cross-doc sweep extended to `main.tex`↔appendix (F-1 is not reachable by the current script at any threshold).

---

## (b) Round-6 findings: closed / not closed

| # | Item | Status | Evidence (current text) |
|---|---|---|---|
| 1 | N-1: `appendix_extended.tex:672`/`:675` values; **add a doc-vs-doc guard** | **CLOSED**, and over-delivered | `:675` now `$-0.091$ \ci{-0.140}{-0.050}`; `:672` now `$-0.164$`. `grep -c "28.1" / "1,011"` = 1 in **both** files. Team found two defects round 6 missed. `check_cross_doc.py` exists and runs. **But see F-5/F-6: the guard is weaker than claimed.** |
| 2 | N-2: `SUBMISSION.md:33` "38-page paper" → 39; sweep `supplement/README.md` | **HALF CLOSED** | Page count fixed: `:35` "the paper is now 39 pages and the extended appendix 56" — `pdfinfo` confirms 39/56. The `supplement/README.md` lines are now *named* (`:23`, `:25`, `:633`) but not swept — defensible as a declared pre-deadline task. **Not defensible: the same sentence now ends "the project checker now reports 15 flags rather than 5" while the checker reports 17 and `:32` says 17.** See **F-4**. |
| 3 | N-3: retitle `appendix_extended.tex:935` | **HALF CLOSED** | Section heading now matches: both `appendix.tex:529` and `appendix_extended.tex:937` read `\section{The swap under a prompt that does not instruct comparison, and a chosen reference}`. **But the ledger row was renamed to a third name.** See **F-7**. |
| 4 | N-4: guard the remaining four counts; fail loudly | **CLOSED — verified by perturbation** | 16 guard lines, 8 extended-prose. I reworded `could not be evaluated` → `were not evaluable` in a scratch copy; the checker printed `LEDGER GUARD NOT FOUND: … (is a number spelled out as a word?); those four are unguarded`. Prose now uses digits ("18 predictions registered…"). This is the round's best work. **Residual: the caption guard checks the wrong table — F-8.** |
| 5 | N-5: `main.tex:173` "$-6$ … exceeds … 5" | **NOT CLOSED (1 of 3 sub-items)** | Now: "moves $-6$ pp for Sonnet~5, **beyond the 5-point bound we registered**". "Beyond" still requires the reader to take an absolute value of $-6$ against $5$; and the edit **introduced** a unit mixture ("$-6$ **pp**" vs "5-**point** bound") that did not exist before. N-5 items 2 and 3 untouched. See **F-3**. |
| 6 | N-6: `main.tex:256` "the one cell" | **NOT CLOSED — relabelled, and now an overclaim** | Now: "the SimpleQA grader's shrinkage is **the only comparison** whose interval includes zero." Round 6 asked for "the only one of **these** comparisons"; the team deleted the deixis that made the fix work. See **F-2**. |
| 7 | N-7: Introduction/abstract duplication | **NOT DONE (optional, flagged as such)** | `main.tex:95` unchanged. Round 6 marked this optional and said it preferred the current text. Correct to leave. |
| 8 | N-8: "9 to 56 points short" | **CLOSED as an explicit third decline** | `SUBMISSION.md:38`: "**Standing decision, so it stops recurring:** … raised and declined three times … Revisit only if the abstract gains room." This is exactly what was asked. Do not raise again. |
| 9 | Item 16: counter-instructed swap | **NOT DONE, correctly declared** | `SUBMISSION.md:38`: "Not started: it costs money and was not authorised." Not claimed anywhere. |

**Score: 3 closed, 3 half closed, 2 not closed, 1 correctly deferred.**

### Independent re-verification

| Claim | Verdict |
|---|---|
| `check_numbers.py` → 17 flags, 16 guard lines all matching | **TRUE.** 5 in `appendix.tex`, 12 in `appendix_extended.tex`; 3 column + 5 caption + 8 extended-prose, all "matching". |
| `check_cross_doc.py` direct test clean | **TRUE**, and that is the problem — see F-5. |
| Ledger arithmetic | **TRUE.** Columns 290 + 14 + 17 = 321, matching `main.tex:156`. Row sums match `registration_round30.md:257` ("17 predictions: 14 confirmed, 2 falsified … 1 split"). |
| §3 / §6 numbers against `registration_round30.md` | **TRUE.** $-0.264 \to$ "26 pp"; $-0.132 \to$ "13"; $-0.059 \to -5.9 \to$ "$-6$ pp"; $-0.032 \to$ "$-3$ pp". §6: $-0.091\to9$, $-0.203\to20$, $-0.258\to26$, $-0.562\to56$. All correct. |
| `main.tex` numbers exist in the appendices/tables | **TRUE** with 2 explained exceptions: "65" (`:253`) is sourced from `registration_round19/20/25/26.md`, "44" (`:262`) from `../analysis`. Neither is a defect. |
| `cmp main.pdf Reference_…_v5.pdf` silent; PDF rebuilt from edited source | **TRUE.** Both edited sentences render in `main.pdf`; zero hits for the old "the one cell" / "which exceeds the 5 pp". |
| Prevalence "0% to 3%" (main) vs "0% to 4%" (appendix) | **TRUE, not a contradiction.** The appendix range includes TriviaQA; re-confirmed. |

---

## (c) NEW findings

### F-1 — **BLOCKING.** The fourth instance of the class, in the pair the new script does not cover: `main.tex`'s Figure 2 caption cites a table that contains a different number, and the number it quotes appears in neither shipped document.

`main.tex:165`, the caption of `fig:rotation-pool`:

> "…and for answers that match neither reference (113 tasks; **$+0.12$**, $+0.30$, $+0.04$), with 95\% intervals. Pre-specified; Qwen2.5-7B uses the exact scorer (**\cref{tab:rotation}**)."

`tab:rotation` is `appendix.tex:301`, and `appendix.tex:304` inputs `tables/rotation_exact.tex`. Its Qwen2.5-7B "Neither" cell reads:

> `Qwen2.5-7B & $a$ & $+4.97$ … & $-5.04$ … & $+0.13$ {\scriptsize$[-0.04,+0.31]$}`

**+0.13, not +0.12.** The other two values check out (phi-4 $+0.30$, Sonnet~5 $+0.04$).

The `+0.12` is not wrong — it is the *exact-scorer* value, `tables/r4_rotation.tex`, row "Exact scorer": `$+5.25$ … $-5.41$ … $+0.12$`. But that fragment is input **only** at `appendix_extended.tex:410`. And `tab:rotation`'s own caption (`appendix.tex:300`) says so outright:

> "…original scorer, registered runs; **exact-scorer values for Qwen2.5-7B are in the extended appendix**"

So the caption of the paper's second figure quotes a number, tells the reader to verify it at `\cref{tab:rotation}`, and that table (a) does not contain the number, (b) shows a *different* value in exactly the cell the reader would check, and (c) states in its own caption that the value is somewhere else. A reviewer with only the submitted PDF — the extended appendix ships separately in the supplement — **cannot find `+0.12` anywhere**. This is precisely the round-6 defect, one file over.

**Why both scripts are blind to it.** `check_numbers.py` passes: `+0.12` is legitimately sourced. `check_cross_doc.py` never opens `main.tex` — it hard-codes `PAPER / "appendix.tex"` and `PAPER / "appendix_extended.tex"` (`:63-64`). No threshold change reaches this.

**Fix.** Either point the caption at the table that has the number — `Qwen2.5-7B uses the exact scorer (extended appendix)` — or quote the cited table's value and drop the exact-scorer clause: `(113 tasks; $+0.13$, $+0.30$, $+0.04$) … (\cref{tab:rotation})`. The first is truer to the figure. **Then run `check_cross_doc.py main.tex appendix.tex`** — it already accepts two path arguments, so this costs one line in `SUBMISSION.md`, not new code.

### F-2 — **BLOCKING (overclaim, introduced this round).** `main.tex:256` now asserts an unrestricted uniqueness claim that four other sentences in the same paper contradict.

`main.tex:256`:

> "Under the first-listed rule, though, the SimpleQA grader's shrinkage is **the only comparison** whose interval includes zero."

Round 6's required fix was **"the only one of these comparisons"**. The team kept the noun and deleted "one of **these**" — the deixis pointing back at the four numbers in the preceding clause (9, 20, 26, 56), which is the whole thing that made the fix work. As written, "the only comparison" scopes over the paper. The paper contradicts it four times:

- `main.tex:114` — "interval includes zero for GPT-4.1 (factual) and Opus~5 (one pool)"
- `main.tex:173` — "$-3$ pp for GPT-4.1, **whose interval includes zero**"
- `main.tex:198` — "**Two intervals include zero**: GPT-4.1 on factual questions … and Opus~5 on the replication pool"
- `main.tex:280` — "although Opus~5's interval **touches zero**"

The appendix says it correctly, with the scope attached (`appendix.tex:598`): "every interval on **that difference** excludes zero except the SimpleQA grader's under the first-listed rule". The main text dropped the scoping noun phrase and kept the superlative.

Worse, round 6's N-6 complaint was that "cell" *named a grid the main text never shows*. Renaming it "comparison" does not fix that — the six-cell R30-B table is still invisible to the main-text reader. The defect was relabelled, not repaired.

**Fix (round 6's wording, restored):** "…is **the only one of these comparisons** whose interval includes zero." Four characters longer than the current text, and it is the sentence round 6 asked for.

### F-3 — **BLOCKING (readability + new unit defect).** `main.tex:173` still asks the reader to take an absolute value, and the repair introduced a unit mixture.

`main.tex:173`:

> "Text matching neither reference moves **$-6$ pp** for Sonnet~5, **beyond the 5-point bound we registered**, and $-3$ pp for GPT-4.1, whose interval includes zero"

Round 6 called "$-6$ … exceeds … 5" *literally false*, because the registered bound is on magnitude (`registration_round30.md:99`: "change credit by **at most 5 points**"). "Exceeds" became "beyond". A negative number is not "beyond" a positive bound either; the reader must still silently take $|-6| > 5$, at the one place in §3 where the paper reports its own falsified prediction — exactly round 6's objection, one synonym over.

The edit also **created** a defect: `$-6$ **pp**` and `5-**point** bound` now name the same unit two ways inside one clause, where the previous text ("exceeds the 5 pp we registered") was at least internally consistent. `main.tex:156` defines pp; "point" is the 0–10 score word used three clauses earlier ("rather than the 0--10 score above"), so the sentence now uses "point" for the *credited share* immediately after using it for the *score*.

N-5's other two sub-items are untouched: "pp" still appears four times in two sentences for a credited share, and the instrument disclosure still trails its numbers ("lose 26 pp for GPT-4.1 and 13 for Sonnet~5, where credit is a yes-or-no judgment…").

**Fix (round 6's, unchanged and still the right one):** "Credit still follows the reference, where credit is a yes-or-no judgment rather than the 0–10 score above: answers that stop matching it lose 26 points of that credit for GPT-4.1 and 13 for Sonnet 5. Text matching neither reference moves 6 points for Sonnet 5, **more than the 5-point bound we registered**, and 3 for GPT-4.1, whose interval includes zero."

### F-4 — **BLOCKING (checklist correctness, deadline-gating).** `SUBMISSION.md:35` repeats round 6's named failure in round 6's named sentence, and now contradicts `SUBMISSION.md:32`.

Round 6's closing note: *"When you write a note saying which numbers moved, re-measure **every** number in the sentence, not the ones that prompted the note."*

`SUBMISSION.md:35`, after this round's edit:

> "**Both figures have since moved and must be re-checked on rebuild:** the paper is now 39 pages and the extended appendix 56. `supplement/README.md` still carries the pre-round-4 figures in three places … so re-measure every page count there at rebuild rather than copying these forward (the round-30 section), and the project checker now reports **15 flags** rather than 5"

`python3 scripts/check_numbers.py` → **17**. And `SUBMISSION.md:32`, eleven lines earlier, says so:

> "Scanning that file takes the run from 5 flags to **17**: the same 5 in `appendix.tex`, plus 12 in `appendix_extended.tex`."

The team corrected the two page counts it had just measured and left the third number in the same sentence stale — the identical behaviour, in the identical sentence. The document now states 17 and 15 for the same quantity.

Two more defects in the same sentence, both introduced by this round's edit:

1. **"Both figures"** is now wrong. It originally governed two numbers (extended-appendix pages, flag count). The sentence now carries three (paper pages, extended pages, flags). "Both" no longer counts them.
2. **"(the round-30 section)" is orphaned.** It previously explained *why the extended appendix grew to 56*: "the extended appendix is now 56 pages (the round-30 section)". It now sits after "rather than copying these forward", where it modifies nothing and reads as a non-sequitur.

**Fix.** `SUBMISSION.md:35`: "15 flags" → "17 flags"; "Both figures" → "These figures"; move "(the round-30 section)" back to follow "the extended appendix 56". **And add the flag count and the guard-line count to whatever is re-measured at rebuild** — `SUBMISSION.md:28` already tells the reader to count guard lines, so the checklist should state both counts in one place, once.

### F-5 — **BLOCKING (tooling).** The cross-doc test the team calls "the stronger" is blind to sign flips and to value swaps. I demonstrated both.

`SUBMISSION.md:30` and `check_cross_doc.py:88-90`:

> "The script runs two tests, and **the direct one is the stronger**"

The direct test is whole-file set membership (`check_cross_doc.py:105-108`):

```python
seen = set(ea) | {x.lstrip("-") for x in ea} | {"-" + x for x in ea}
absent = sorted({x for x in ca if x not in seen and x.lstrip("-") not in seen}, …)
```

Two consequences, both confirmed by experiment on a scratch copy:

1. **Sign-blind by construction.** `seen` is built with signs stripped *and* added, and the membership test strips again. I changed `appendix.tex:356` from `$-0.164$` to `$+0.164$` — inverting the paper's central grading-AUROC result — and the direct test printed **"direct test: every number in appendix.tex appears somewhere in appendix_extended.tex"**. A sign error is the one arithmetic error that reverses a finding, and this test cannot see it.
2. **Any value that occurs anywhere passes.** I changed "false rejections on \textsc{MACE} rise by **36.3** points" to "**14.9** points" — a real number from a different experiment three paragraphs away. Direct test: clean again.

Both defects were caught **only** by the sentence-pairing pass, which the team calls "the weaker test" and which it has already decided prints benign noise. They surfaced as a single added line among the six standing mismatches, taking the count from "6 sentence pairs disagree" to 7. Nobody re-reading a seven-line report they believe is noise will see it.

The team's evidence for "the direct one is the stronger" is a sample of two (1,011 and 28.1) — both *unusual* values. That generalises exactly backwards: the direct test is strong only for values too exotic to collide, and the paper's results are mostly two-decimal numbers in a 151 KB file where nearly every such value already occurs.

**Fix.** Make the direct test sign-sensitive (drop the `lstrip("-")` normalisation on both sides; a sign mismatch should be reported, not absorbed). Then stop describing the pairing pass as the weaker test, and **drive its mismatch count to zero** by whitelisting the six known-benign pairs explicitly, so that a seventh is an error and not a line in a list. Right now `check_cross_doc.py` also exits **1** on the clean tree (`return 1 if mismatches`), so it cannot be wired into anything that checks exit status.

### F-6 — NON-BLOCKING (tooling). Two live condensed-only numbers the direct test passes today.

Both are current output of the team's own script, both rated benign, and both are literally what `appendix.tex:43` promises cannot happen:

- `appendix.tex:200` — "The other ten predictions compare against an arm that failed its check (\textbf{not evaluable}, **10**)." `appendix_extended.tex:185` ends "(\textbf{not evaluable})." The count is condensed-only. Harmless in itself; it passes the direct test only because "10" occurs everywhere.
- `appendix.tex:236` vs `appendix_extended.tex:318` — **a substantive condensation, not a formatting one.** Condensed: "Qwen2.5-14B-Instruct reads each unboxed reply and reports the final answer it commits to; **the rule and the model agree on 88\% of unboxed replies**." Extended: "…reports the final answer it commits to, **or none; 54\% and 55\% of unboxed replies commit to none.** The rule relabels 695 … and the two agree on 88\% of unboxed replies." The condensed copy drops "or none" and the 54/55% figures — which are the facts that make the 88% interpretable, since agreement is substantially joint abstention. A reader of the submitted PDF gets an agreement statistic without the base rate that qualifies it.

**Fix.** Add ", 10" to `appendix_extended.tex:185`. Restore the "or none" clause to `appendix.tex:236`, or drop the 88% there — an agreement number without its abstention rate reads better than it is.

### F-7 — NON-BLOCKING. The round-30 appendix now has three names across the two documents.

The N-3 fix aligned the section heading but renamed the extended ledger row at the same time, creating a new divergence:

- `appendix.tex:529` = `appendix_extended.tex:937` (heading): "The swap under a prompt that does not instruct comparison, and a chosen reference" ✓
- `appendix.tex:32` (index row): same ✓
- `appendix_extended.tex:217` (ledger row): "**Swap under the direct prompt, and a chosen reference**" — renamed this round from "The direct prompt and a chosen reference"
- `appendix.tex:192` (ledger row): "**Swap under the direct prompt**" — unchanged, and shorter still

The two ledger rows do not match each other, and neither matches the section both point at. The condensed row's narrower name is defensible on content (it lists only the R30-A predictions), but then it should not have been the extended row that moved.

**Fix.** Make `appendix.tex:192` and `appendix_extended.tex:217` agree on one string, and prefer the section's own title so all four agree.

### F-8 — NON-BLOCKING (tooling). The `tab:ledger-failures` caption is guarded against a different table from the one it describes. Demonstrated.

`appendix.tex:170`:

> "**The rows contain** 14 not confirmed, 39 falsified, 18 split, 18 not evaluable, and 2 not scored predictions, and the 3 excluded ones."

The caption makes a claim about **the rows of `tab:ledger-failures`**. `check_numbers.py:122-132` reads its counts from `\label{tab:ledger-totals}` — a different table — and compares the caption to *that*. The rows the caption is about are never counted.

I deleted an entire falsified row from `tab:ledger-failures` in a scratch copy:

> `$k$-pool and mitigations\osf{} & Blind-then-reveal keeps the $k{=}1$ benefit (\textbf{not confirmed} …`

and reran the checker. **All 16 guard lines still printed "matching."** The caption would have shipped saying "the rows contain 14 not confirmed, 39 falsified…" about a table missing one of them.

This is the same shape as the defect that produced the guard: a claim about document A checked against document B. It is not urgent — the counts are right today — but the guard reads as stronger than it is, which is how the last three rounds' defects survived.

**Fix.** Count `\textbf{…}` verdicts in the `tab:ledger-failures` body, expanding the "(n)" multipliers the caption's own second sentence describes ("Counts in parentheses where one entry covers several predictions"), and compare *that* to the caption. If the multiplier parsing is too fiddly, at minimum assert the failure table's row count is unchanged and print it.

### F-9 — NON-BLOCKING (readability, requested). The Introduction's "What we find" paragraph.

`main.tex:93-100` is unchanged this round, and round 6 was right that the current trade is the better one. Two pre-existing issues stand, neither worth a required change:

- `:95` "**Run as their authors configure them,** the graders of SimpleQA, BrowseComp, and HLE score four models…" — an eight-word modifier ahead of the subject it modifies, opening the paragraph the reader skims first.
- The paragraph is headed "What we find" and its last three sentences (`:98-100`) are related work. Its most-skimmed paragraph does not end on a finding.

If §6 frees a line, move `:98-100` into §8. Otherwise leave it; it is not a defect, and the paragraph is much better than at round 5.

---

## (d) Page limit — **COMPLIANT. Verified by rendering.**

`template_iclr2027.tex:131` sets "a strict upper limit of **9 pages** for the main text".

`pdfinfo main.pdf` → **39 pages** (unchanged from round 6).

- `pdftotext -f 9 -l 9` — page 9 is Limitations, ending "…and most registrations are timestamped commits with a verdict rule adopted afterwards (Appendix D)." — matching `main.tex:328`.
- `pdftotext -f 10 -l 10` — page 10 begins **"AI USE STATEMENT"**, then ETHICS, REPRODUCIBILITY and REFERENCES, all exempt.

**Main text ends on page 9. Compliant.** `main.log`: 0 undefined references, 0 overfull boxes. The rebuilt PDF contains both edited sentences and zero occurrences of the superseded wording, so `main.pdf` matches `main.tex`; `cmp main.pdf Reference_Anchoring_Biases_LLM_Judges_v5.pdf` is silent.

**Slack:** F-2 costs four characters, F-3 about one word, F-1 is length-neutral. F-4 through F-8 are outside `main.tex`. Nothing here requires cutting a hedge.

---

## (e) What is genuinely strong — do not break these

1. **The self-found defects.** The team found 1,011/1,192 and 28.1% on its own, after round 6 had named only two. That is the first time in seven rounds the authors have out-searched the review. It is the single best signal in this round.
2. **The fail-loud guard work.** `check_numbers.py:160-183` now prints `LEDGER GUARD NOT FOUND` on a regex miss and guards all eight extended-appendix counts. I verified by perturbation, not by reading, and it behaved correctly. The "Eighteen" → "18" change closed exactly the hole round 6 predicted would recur.
3. **The commit message as an engineering record.** `1105603` documents three *failed* versions of the new script, including one that "was structurally blind to its own motivating defect" — caught because the mismatch count did not change when a known defect was fixed. That is the correct instinct (test the detector against a known-defective input), and `SUBMISSION.md:30` records it. Keep doing this.
4. **The explicit third decline of N-8.** `SUBMISSION.md:38`'s "Standing decision, so it stops recurring" is exactly the right response to a thrice-raised optional item. This item is closed; no future round should reopen it.
5. **The ledger, and printing failures in the main text.** `:171`, `:173`, `:200`, `:269`, `:279` all still print falsified or unconfirmed registered predictions in the running text. F-2 and F-3 are defects *of* these sentences, not arguments against them.
6. **The mechanical-narrowing paragraph** (`appendix.tex:596-604`), the 1.1–5.7 range, the HLE-pinning note, and the R30-B table's intervals and self-graded asterisk — all intact from round 6.
7. **The abstract's self-limiting sentences**, `:54` "Those benchmarks rarely contain such questions" and `:56` "partly by construction". Seven rounds of page pressure and still there.

---

## Required changes, priority order

| # | Where | Change | Status |
|---|---|---|---|
| 1 | `main.tex:165` | **F-1:** caption cites `\cref{tab:rotation}`, which shows $+0.13$, for a quoted $+0.12$ that exists only in `appendix_extended.tex`. Repoint the reference or requote the value. **Then run `check_cross_doc.py main.tex appendix.tex`.** | **New, BLOCKING** |
| 2 | `main.tex:256` | **F-2:** "the only comparison" → "**the only one of these comparisons**". Restores round-6's wording and removes an unrestricted claim the paper contradicts four times. | **New, BLOCKING** |
| 3 | `SUBMISSION.md:35` | **F-4:** "15 flags" → "17"; "Both figures" → "These figures"; re-attach "(the round-30 section)". **Abstract registration Sep 18.** | **New, BLOCKING** |
| 4 | `main.tex:173` | **F-3:** "$-6$ pp … beyond the 5-point bound" → "6 points … more than the 5-point bound we registered"; move the instrument clause ahead of the numbers. | **Carried ×2, BLOCKING** |
| 5 | `scripts/check_cross_doc.py:105-108` | **F-5:** make the direct test sign-sensitive; whitelist the six benign pairs so the pairing report's steady state is zero. | **New, BLOCKING** |
| 6 | `appendix_extended.tex:185`, `appendix.tex:236` | **F-6:** restore ", 10"; restore the "or none" / 54–55% qualification behind the 88%. | New |
| 7 | `appendix.tex:192`, `appendix_extended.tex:217` | **F-7:** one name for the round-30 row across both ledgers. | New |
| 8 | `scripts/check_numbers.py:122-148` | **F-8:** count the rows of `tab:ledger-failures`, which is the table its caption describes. | New |
| 9 | §3 | Run the counter-instructed swap cell. Still part of what moves 7 → 8. | Carried |

Items 1–4 are text-only and net roughly zero lines in `main.tex`.

---

## Closing note to the authors

Round 6 told you the real class was **"the same quantity printed in two documents"** and that the ledger was only its most visible member. You built the guard for that class — for *one pair of documents*. `check_cross_doc.py:63-64` hard-codes `appendix.tex` and `appendix_extended.tex`. The fourth instance was in `main.tex`, and it is the most consequential of the four so far, because it is in a **figure caption on page 3 of the submitted PDF**, and because the number it sends the reader to verify is in a file that does not ship with the paper. Your script already takes two path arguments. `check_cross_doc.py main.tex appendix.tex` would have been free.

The second thing is about how you rate your own tests. You wrote that the direct whole-file test is "the stronger" one, on the evidence of two values it caught that the pairing pass missed. Both were unusual numbers. I injected a sign flip on $-0.164$ — the paper's central grading result, inverted — and the direct test reported clean, because it normalises signs away on both sides. I then swapped 36.3 for 14.9, a real value from another experiment, and it reported clean again, because in a 151 KB file nearly every two-decimal value already occurs somewhere. The test you call stronger is the one that can only catch numbers too rare to collide. The test you call weaker caught both — and buried them as a seventh line in a six-line report you have already classified as noise. **A report with a nonzero steady state is not a test.** Drive the pairing count to zero with an explicit whitelist, and the next defect announces itself instead of joining a list.

Third, and most avoidable: `SUBMISSION.md:35`. Round 6 closed by telling you to re-measure *every* number in a sentence when you write a note about which numbers moved. You then edited that exact sentence, corrected the two page counts, and left "15 flags" — while line 32 of the same file says 17. This is the third consecutive round in which a number went stale inside the sentence declaring that numbers had gone stale. The fix is not more care; it is that `SUBMISSION.md` should not restate a count that a script prints. Say "run `check_numbers.py` and `check_cross_doc.py`; record the counts they print" and stop typing 17 and 16 into prose at all.

What is not in doubt: you found two defects this round that I did not give you, your fail-loud guard work is correct and I verified it by breaking it, and you closed a thrice-raised optional item by explicitly declining it, which is the right way to end that loop. The science, the ledger, and the willingness to print your own falsified predictions in the main text are all intact and are what the 7 rests on. The distance from 7 to 8 is item 16, four text fixes, and pointing the checker you already wrote at one more file.
