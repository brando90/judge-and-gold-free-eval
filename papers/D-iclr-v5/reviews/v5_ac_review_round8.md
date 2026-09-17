# Meta-review (AC), ICLR 2027 — v5, round 8

**Paper:** "Reference Anchoring Biases LLM Judges Toward the Answer They Are Shown When Several Are Correct"

**Artifacts checked:** `main.tex` (02:10), `main.pdf` (39 pp, 02:16), `appendix.tex` (02:15), `appendix_extended.tex` (01:49), `extended_appendix.pdf` (56 pp), `SUBMISSION.md` (02:15), `scripts/check_numbers.py` (01:41), `scripts/check_cross_doc.py` (02:14), all 69 `tables/*.tex`, `registration_round27.md`, `registration_round30.md`, `supplement/README.md`, all 211 `papers/analysis/*.json`, commit `aade5ee`, and `reviews/v5_ac_review_round7.md`. Page limit verified by **rendering** (`pdftotext -f 9 -l 10`), never from `.aux`. I ran both scripts; re-derived §3 and §6 against `registration_round30.md`; re-derived the §7 claims against `tables/r24_standard.tex`, `r26_verifiers.tex` and `r26_instruction.tex`; independently reproduced the team's two documented control measurements; and **tested both checkers against nine injected defects in full tree copies**, not against the clean tree alone. I did not rerun any model call.

---

## (a) Score

**7: good paper, accept. Confidence: 4.** Unchanged from round 7's **7**, and from round 6's 7.

Round 7 set the bar for 8 as "item 16 plus a real cross-document sweep". **Neither happened.** Item 16 is correctly declared undone. The sweep was not extended to `main.tex`, and F-5 — the round's other blocking tooling finding — was closed only in the direction that *cannot* corrupt the shipped paper: I re-ran round 7's exact sign injection and the direct test still reports clean (**N-1**).

Held rather than lowered, and this is not a courtesy. F-1, F-2 and F-4 are genuinely closed, verified by rendering and by perturbation rather than by reading. The F-1 fix is **better than either option round 7 offered**, because it also reports the placebo as null. And the team's most contestable documented claim — that resolving `\input` drops the positive control from 4 detections to 1 and the sign control from 1 to 0 — **reproduces exactly**, including which three values are lost. That is the second round running in which the authors' own measurement survived an adversarial replication.

Why not 6. I re-derived every number in §3, §6 and §7 from the registrations and producer JSONs and **all of them check out**, including all six R30-B cells, all four §3 swap values, and the falsified-prediction sentences. The new defects are in one caption and in the tooling, not in the argument.

**8 requires:** item 16; N-1, N-2 and N-3 fixed; and the cross-document test made two-way (**N-4**), which is the class the last three rounds have been about.

---

## (b) Round-7 findings: closed / not closed

| # | Item | Status | Evidence (current text / experiment) |
|---|---|---|---|
| F-1 | Fig. 2 caption quotes `+0.12`; `\cref{tab:rotation}` shows `+0.13` | **CLOSED (value), and over-delivered** | `main.tex:165` is unchanged, but `appendix.tex:300` now reads "…under the exact scorer, which \cref{fig:rotation-pool} quotes, Qwen2.5-7B's ``Neither'' cell is $+0.12$ **with an interval that includes zero**, and the full exact-scorer table is in the extended appendix". Renders in `main.pdf`. Producer confirms: `r4_results.json /rotation/escore/placebo = 0.1157 [-0.0655, 0.2971], n=113`; `make_figures.py` plots that same record. Reporting the placebo as **null** is the meaningful fact and neither option round 7 gave asked for it. |
| F-1b | "Then run `check_cross_doc.py main.tex appendix.tex`" | **NOT DONE, and not declined** | No such line in `SUBMISSION.md`. See **N-7**: I ran it, and it is unusable as written. |
| F-2 | `main.tex:256` "the only comparison" → "the only one of **these** comparisons" | **CLOSED — verified by rendering** | `main.tex:256`: "the SimpleQA grader's shrinkage is **the only one of these comparisons** whose interval includes zero." `pdftotext main.pdf` → new wording 1 hit, "the only comparison whose" 0 hits. Substantively true: of the six R30-B cells only first-listed SimpleQA `+0.045 [−0.003,+0.092]` includes zero. |
| F-3 | `main.tex:173` absolute value; unit mixture; trailing instrument clause | **HALF CLOSED (1 of 3)** | Unit mixture fixed: now "$-6$ **pp** … beyond the **5 pp** we registered as a bound". But "beyond" is unchanged, so the reader still takes $|{-}6|>5$; and the instrument disclosure still trails its numbers ("lose 26 pp for GPT-4.1 and 13 for Sonnet~5, **where credit is a yes-or-no judgment** rather than the 0--10 score above"). New minor divergence: the paper now says "pp" where its own ledger row (`appendix.tex:192`) and `registration_round30.md:99` say "**points**" ("move at most 5 points"; "$-5.9$"). |
| F-4 | `SUBMISSION.md` "15 flags"; "Both figures"; orphaned "(the round-30 section)" | **CLOSED** | `:39` now: "**Both figures** have since moved…: the paper is now 39 pages and the extended appendix 56" (exactly two numbers) … "**The project checker now reports 17 flags rather than 5**, because it also scans `appendix_extended.tex`." Split into its own sentence; the orphan was deleted rather than re-attached, which is fine. Re-verified: `pdfinfo` 39/56; 69 fragments; 16 guard lines (3+5+8); "5 in `appendix.tex`, plus 12 in `appendix_extended.tex`"; and the ":36" arithmetic (10 = 4 duplicates + 6 new) all hold. |
| F-5 | Direct test sign-blind and collision-blind; whitelist the six pairs; exit code | **NOT CLOSED (1 of 4, in the wrong direction)** | Code is now `seen = set(ea)` (`:152`). Flip in `appendix_extended.tex` → fires. **Flip in `appendix.tex` — round 7's exact injection — still prints "direct test: every number in appendix.tex appears somewhere in appendix_extended.tex".** Value swap 36.3→14.9 still clean. Still "6 sentence pairs disagree"; `SUBMISSION.md:32` still calls the direct test "**the stronger**"; `check_cross_doc.py:174` still `return 1 if mismatches`, and I confirmed `exit=1` on the clean tree. See **N-1**. |
| F-6 | Restore ", 10" and the "or none" / 54–55% qualification | **NOT CLOSED** | The team's own script still prints both: `CROSS-DOC MISMATCH: ['10']` and `CROSS-DOC MISMATCH: ['88']`. So `appendix.tex:43` — "**Every number in this condensed appendix also appears in the extended appendix**" — is still literally false, by the authors' own tool, in the shipped PDF. |
| F-7 | One name for the round-30 row across both ledgers | **NOT CLOSED** | Still three: `appendix.tex:192` "Swap under the direct prompt"; `appendix_extended.tex:217` "Swap under the direct prompt, and a chosen reference"; section heading in **both** files "The swap under a prompt that does not instruct comparison, and a chosen reference". |
| F-8 | Count the rows of `tab:ledger-failures` | **NOT CLOSED, but honestly documented** | Confirmed by perturbation in a full tree copy: deleting the whole `Distance gradient & … (\textbf{falsified}, both judges)` row leaves **all 16 guard lines printing "matching"**. `SUBMISSION.md:30` now states this limit and the reason it was not shipped (multipliers reconcile only for `split`). The reasoning is sound; see **N-5** for the cheaper half. |
| 16 | Counter-instructed swap | **NOT DONE, correctly declared** | `SUBMISSION.md:42`: "Not started: it costs money and was not authorised." Not claimed anywhere. |

**Score: 3 closed, 1 half closed, 4 not closed, 1 correctly deferred.**

### Independent re-verification

| Claim | Verdict |
|---|---|
| `check_numbers.py` → 17 flags, 16 guard lines all matching | **TRUE.** 5 in `appendix.tex`, 12 in `appendix_extended.tex`. |
| `check_cross_doc.py` direct test clean | **TRUE** — and still the problem; see N-1, N-2, N-4. |
| Ledger arithmetic | **TRUE, and verified by perturbation.** 290+14+17 = 321. Breaking `Falsified & 34` → `33` fires `LEDGER MISMATCH: column 1 rows sum to 289, table prints 290` plus caption and extended-prose mismatches. The guards work for what they cover. |
| Registration tallies vs ledger columns | **TRUE.** `registration_round27.md:117` "R27 total: 14 predictions, 11 confirmed, 3 falsified" = column 2. `registration_round30.md:257` "17 predictions: 14 confirmed, 2 falsified … 1 split" = column 3. |
| §3 / §6 vs `registration_round30.md` | **TRUE.** −0.264→26, −0.132→13, −0.059→−5.9→"−6", −0.032→"−3"; −0.091→9, −0.203→20, −0.258→26, −0.562→56. |
| §7 fix claims vs generated tables | **TRUE.** `r24_standard.tex`: "within 0.5 points" (+0.3/−0.2/+0.0/+0.5/+0.2), "99% or more" (99.2–99.7), "at most 3 of 56" (max wrong-credited rise 5.4 pp = 3.0/56). `r26_verifiers.tex`: 67.4 / 30.4 / 5.8. `r26_instruction.tex`: "leaves 31 and 13" = −31.2 / −12.6. `r4_math.tex`: 28.6 / 30.6. |
| P3 counts vs `tables/r20_retest.tex` | **TRUE.** 18.5→"19%", 31.3→"31%", 140 matching, 843 / 117 / 2. |
| Prevalence "0% to 3%" (main) vs "0% to 4%" (appendix) | **TRUE, not a contradiction.** `prevalence_v2.tex`: 1.0 / 0.0 / 3.0, TriviaQA 4.0. |
| **`read_expanded` measurement: positive control 4 → 1, sign control 1 → 0** | **TRUE, and exactly reproducible.** I rebuilt the four v5-base defects and got 4 detections (`1011`, `28.1`, `-0.050`, `-0.164`); wiring `read_expanded` in dropped it to **1** (`1011` kept, the other three lost) and the sign control from 1 to **0**. The documented numbers are correct to the individual value. The revert was right. |
| `cmp main.pdf Reference_…_v5.pdf` silent; PDF rebuilt from edited source | **TRUE.** Both edited sentences render; both superseded wordings absent. `main.log`: 0 undefined, 0 overfull. |

---

## (c) NEW findings

### N-1 — **BLOCKING (tooling).** The sign fix was verified in the one direction that cannot corrupt the paper. Round 7's exact injection still passes.

`SUBMISSION.md:34`:

> "It **is sign-sensitive now**, and that property is **verified by injection, not by reading the code**."

`check_cross_doc.py:148-152` says the same, and commit `aade5ee` says "Reproduced by injection, fixed … and re-proved: the flipped file now reports the number missing."

I ran both directions on scratch copies:

- Flip `$-0.164$` → `$+0.164$` in **`appendix_extended.tex`** → `MISSING NUMBER: -0.164 appears in appendix.tex but nowhere in appendix_extended.tex`. **Fires.** This is the direction the commit tested.
- Flip `$-0.164$` → `$+0.164$` in **`appendix.tex`** — round 7's injection verbatim, and the only direction that puts a wrong sign in the paper a reviewer reads — → `direct test: every number in appendix.tex appears somewhere in appendix_extended.tex`. **Still blind.**

It is a **collision, not a design gap**, which makes it worse rather than better: the unsigned token `0.164` occurs three more times in `appendix_extended.tex`, at `:958` (`\ci{+0.164}{+0.328}`), `:991` (`\ci{+0.164}{+0.263}`) and `:1262` (`$+0.164$`). I neutralised those three and the check immediately fired `MISSING NUMBER: 0.164`. So the fix is real in principle and inert on this corpus, in the direction that matters, because the paper's own CI bounds shadow it.

Round 7's second injection is also untouched: changing "false rejections on \textsc{MACE} rise by **36.3** points" to **14.9** in `appendix.tex` still yields `direct test: … every number … appears somewhere`.

**Fix.** Compare signed multisets in both directions (N-4), or at minimum stop treating "appears somewhere in a 151 KB file" as a test. And add the condensed-direction injection to the control set, requiring it to fire — the control you ran is the one that was already going to pass.

### N-2 — **BLOCKING.** `tab:rotation`'s caption ships six numbers with no producer. `check_numbers.py` flags one of them; the other five pass by collision with unrelated quantities, and the colliding table does not ship in the submitted PDF.

`appendix.tex:300` (and identically `appendix_extended.tex:535`), rendered in `main.pdf`:

> "The last row keeps only samples Sonnet~5 scored at least 7 blind (**3,194** of 3,494). For the open judges the same filter, applied post hoc, gives **$+4.99$ \ci{+4.69}{+5.32}** (Qwen2.5-7B, **91\%** kept) and **$+4.08$** (phi-4, **98\%** kept).\pre"

Against all 211 producer JSONs:

- **No record anywhere has `share_kept` ≈ 0.91 or ≈ 0.98.** A scan of every `share_kept` key returns nothing in those ranges.
- **`4.69` has zero producer hits** at any rounding. It is one of the 17 flags.
- **`3194` appears in no JSON.** The five files that matched the substring matched it inside longer numerals (e.g. `1.2722658443194776`).
- `+4.99` is "sourced" **only** by `tables/main_numbers.tex:15` — the **CI lower bound of a different quantity**: `Moved onto, $t=7$ & $+5.27$ {\scriptsize$[+4.99,+5.57]$} (96\% kept)`, whose producer is `r5_posthoc_results.json /blind_accepted/gainer_ge7 = 5.2659 [4.9928, 5.566], share_kept 0.9625`. That is the judge's **own** blind-score filter, not Sonnet 5's.
- `+5.32` is "sourced" **only** by the *point estimate* of yet another row (`Moved onto, $t=9$ & $+5.32$`).
- `+4.08` is "sourced" **only** by `synthk_results.json /qwen_pool/gap__Qwen__Qwen2.5-3B-Instruct__ref__k16/ci[1] = 4.08` — a Qwen2.5-3B $k$-pool CI bound.

And the collision does not even ship: **`tables/main_numbers.tex` is not `\input` by `appendix.tex`** (only by `appendix_extended.tex`; the condensed appendix inputs 18 of the 69 fragments). In `main.pdf`, `4.99`, `4.69` and `4.08` each occur **exactly once** — in this caption — with nothing in the submitted document to check them against.

This is F-1's class, one table over, and it survived seven rounds because `SUBMISSION.md:26` dismisses the single flag as "**+4.69 (a CI bound quoted in a caption)**". It is not a stray bound: it is the interval of a point estimate that itself has no producer, attached to two `% kept` figures that have no producer, describing a filter no committed script appears to compute.

**Fix.** Regenerate all six from a committed producer into a `tables/` fragment that `appendix.tex` inputs, or delete the sentence. Separately, change how flags are cleared: record the **producer key** that clears each one, not a prose description. "A CI bound quoted in a caption" is exactly the note that let this through.

### N-3 — **BLOCKING (tooling).** The ledger guards silently ignore the file you pass on the command line, and validate the project copy instead. This invalidates a documented workflow.

`check_numbers.py:69-71` (and identically `:117-118`):

```python
candidates = [PAPER / "appendix.tex", PAPER / "paper" / "appendix.tex"]
candidates += [Path(a) for a in sys.argv[1:] if Path(a).name == "appendix.tex"]
src = next((c.read_text(errors="ignore") for c in candidates if c.exists()), None)
```

The project copy is **first**, so whenever it exists every argv path is discarded. Demonstrated: I mangled a scratch copy to `Falsified & 1 & 1 & 1` and `rows contain 999 not confirmed, 999 falsified`, then ran `python3 scripts/check_numbers.py a/appendix.tex`:

> `ledger column 1: rows sum to 290, matching the printed total`
> `ledger caption: falsified = 39, matching the rows`

It reported success for a file whose ledger is nonsense, because it read a different file.

This is not hypothetical. `SUBMISSION.md:39` says the supplement's checker was run "**on the fifth version's two manuscript files (as shipped in `papers/D-iclr-v5/paper/`)**" — that is the argv path — and `supplement/README.md:634-636` records that run as having "printed the same unmatched numbers as the project's copy … **It also derives the ledger totals from `tab:ledger-totals`**". If that run was made anywhere the project `appendix.tex` was reachable, the ledger half of it validated the wrong document. The `paper/appendix.tex` fallback is second, so the supplement layout is only safe when the project copy is absent — which is precisely the condition nobody checks. It also silently invalidated two of my own perturbations this round before I noticed.

**Fix.** One line: when argv paths are given, use them **exclusively**.

```python
argv_app = [Path(a) for a in sys.argv[1:] if Path(a).name == "appendix.tex"]
candidates = argv_app or [PAPER / "appendix.tex", PAPER / "paper" / "appendix.tex"]
```

And print which file the guards actually read, so "16 lines, all matching" names its subject.

### N-4 — **BLOCKING (the requested defect class neither script catches).** A wrong number that lives only in `appendix_extended.tex` is invisible to both scripts, if it collides with any corpus value.

Both cross-document tests are **one-way**. `check_cross_doc.py:131` — `missing = [n for n in want if n not in have]` — and `:153` — `absent = {x for x in ca if x not in seen}` — only ask whether *condensed* numbers reach the extended file. Nothing ever asks the reverse. And `check_numbers.py` only asks whether a number exists *somewhere*.

Demonstrated in a full tree copy. I changed `appendix_extended.tex:674` from "3,264 calls" to "**3,494 calls**" — another real number from the corpus, and a 7% misstatement of the call count behind the paper's central grading result ($-0.164$ on MACE):

- `check_numbers.py`: **17 flags, unchanged.** `3494` is not among them.
- `check_cross_doc.py`: `direct test: every number in appendix.tex appears somewhere in appendix_extended.tex`; **6 sentence pairs, unchanged.**

Both clean. This is exactly the shape of the defect that started this whole thread — `SUBMISSION.md:36` records that `appendix_extended.tex` "shipped unguarded and had therefore kept a **stale ledger total (202/14/34 of 290)** long after the paper moved to 321" — so the class is not speculative; it is the one that already bit this paper, and the new script does not cover it because it only runs condensed → extended.

**Fix.** Run the direct test in **both** directions, reporting the extended-only residue as a separate list that is expected to be non-empty but is read once per round. Better, in the pairing pass compare multisets symmetrically (`want != have`, not `want - have`), which catches this at the sentence level where it is legible.

### N-5 — NON-BLOCKING (a second uncaught class). Verdict words and spelled-out numbers carry no digits, so nothing guards them.

Demonstrated: flipping `\textbf{falsified}` → `\textbf{confirmed}` in the `Distance gradient` row of `tab:ledger-failures` changes no number. `check_numbers.py` prints 16 guard lines, all "matching"; `check_cross_doc.py` is unchanged. Combined with F-8 (the rows are never counted), the failures table — the paper's headline integrity artifact — is unguarded against **row deletion and verdict inversion alike**.

Cheaper half, and worth closing now: spelled-out numbers are invisible to both `NUM` regexes. `appendix.tex` still carries "The other **ten** predictions compare against an arm that failed its check" (`:200`), "all **twelve** predictions were confirmed" (`:381`), and "**Seven** moved from falsified to not confirmed … **Ten** moved against us" in the `Verdicts follow one rule` paragraph of `app:ledger`. I checked all four by hand and **all four are correct today**. But this is the exact hole that produced the round 6→7 fix ("Eighteen" → "18"), and it has simply reappeared elsewhere.

**Fix.** Write them as digits, so the guards can see them; and assert the failures table's row count, which `SUBMISSION.md:30` already concedes is the minimum ("at minimum assert the failure table's row count is unchanged and print it" was round 7's wording, and it is still right — it needs no multiplier parsing at all).

### N-6 — NON-BLOCKING (tooling honesty). "17 flags" has almost no power, and the document presents it as though it measures fidelity.

Measured directly. The `known` set is **6,716 values**, built from 15 registration documents, the survey, all 69 generated tables, and 211 producer JSONs at 2 and 3 decimals *and* as percentages. Coverage:

- two-decimal values in [0.00, 1.00] — every AUROC, credited share and probability in the paper: **101 of 101 already "known"**;
- one-decimal values in [0.0, 100.0] — every pp figure: **994 of 1,001**;
- integers 0–999: 424 of 1,000.

So "0 flags in `main.tex`" is not evidence that `main.tex` is right; for the paper's two commonest number formats the checker **cannot** flag anything. That is mechanically how N-2's `+4.99`, `+5.32` and `+4.08` passed while `+4.69` did not — `4.69` was simply the one value that happened not to collide.

**Fix.** One honest sentence next to the flag count in `SUBMISSION.md:26`, e.g.: "The checker tests sourcing, not correctness; in the 0–1 two-decimal range it accepts every value, so a clean run is a necessary condition and nothing more." This costs nothing and stops the count being over-read, which is the failure mode round 7's closing note was about.

### N-7 — NON-BLOCKING (process). Round 7's second required action on F-1 was neither done nor declined.

Round 7's required-changes table, row 1: "…Repoint the reference or requote the value. **Then run `check_cross_doc.py main.tex appendix.tex`.**" The caption was fixed; the sweep was not run, and `SUBMISSION.md` gained no line about it.

I ran it. It is **unusable as written**: 29 `MISSING NUMBER` lines, essentially all false positives — `0.40` and `0.64` are `\includegraphics`/`\resizebox` widths, `43` is the survey denominator, `9.3`, `2.9`, `117`, `843` and `321` are legitimately sourced elsewhere — because `main.tex` never claims every number in it appears in `appendix.tex`. So the right disposition was to say that, not to leave a required action silently dropped. This is the third round in a row where the checklist's weak point is *what it does not record* rather than what it records wrongly.

The version of the sweep that **would** have been worth running is the one N-2 and F-1 are both instances of: *is every number in a main-text or appendix caption reachable from a table that ships inside `main.pdf`?* I ran that: the condensed appendix `\input`s 18 of the 69 fragments, and `main_numbers.tex` — where a large share of main-text-only values live — is not among them.

### N-8 — NON-BLOCKING (readability, requested).

**(a) §3, `main.tex:173`.** Round 7's objection stands and I agree with it:

> "Credit still follows the reference: answers that stop matching it lose 26 pp for GPT-4.1 and 13 for Sonnet~5, **where credit is a yes-or-no judgment rather than the 0--10 score above**. Text matching neither reference moves $-6$ pp for Sonnet~5, **beyond the 5 pp we registered as a bound**, and $-3$ pp for GPT-4.1, whose interval includes zero"

Three things, in one breath: the instrument disclosure arrives *after* the numbers it reinterprets; "beyond" still asks the reader to take an absolute value at the one place §3 reports its own falsified prediction; and "pp" appears four times in two sentences. Round 7's rewrite is still the right one and is length-neutral: lead with "where credit is a yes-or-no judgment rather than the 0–10 score above", then the numbers, then "**more than** the 5 pp we registered as a bound".

**(b) §6, `main.tex:256`.** Now *correct*, which was the point, but it front-loads two qualifications ahead of its subject and introduces "shrinkage" for the quantity the previous sentence calls a "shortfall":

> "Under the first-listed rule, though, the SimpleQA grader's shrinkage is the only one of these comparisons whose interval includes zero."

Suggest: "Only one of these four shrinkages has an interval that includes zero: the SimpleQA grader's, under the first-listed rule."

**(c) Introduction, "What we find", `main.tex:93-100`** — unchanged, and round 7's two notes stand: `:95` "**Run as their authors configure them,**" is an eight-word modifier ahead of the subject it modifies, opening the paragraph readers skim first; and a paragraph headed "What we find" ends with three sentences of related work (`:98-100`). Not a defect. Still the most-skimmed paragraph in the paper.

**(d) The newly amended `tab:rotation` caption** is right on content and heavy on packaging — a 62-word opening sentence with a five-clause parenthetical:

> "(replication pool, 0--10 scale, 95\% CI; original scorer, registered runs; under the exact scorer, which \cref{fig:rotation-pool} quotes, Qwen2.5-7B's ``Neither'' cell is $+0.12$ with an interval that includes zero, and the full exact-scorer table is in the extended appendix)"

The "includes zero" clause is the best thing added this round and it is buried in position four of a parenthesis. Split it: keep "(replication pool, 0–10 scale, 95% CI; original scorer, registered runs)", then a separate sentence: "\cref{fig:rotation-pool} quotes the exact scorer, under which Qwen2.5-7B's ``Neither'' cell is $+0.12$, with an interval that includes zero; the full exact-scorer table is in the extended appendix."

---

## (d) Page limit — **COMPLIANT. Verified by rendering.**

`template_iclr2027.tex:131` sets "a strict upper limit of **9 pages** for the main text". `pdfinfo main.pdf` → **39 pages**; `extended_appendix.pdf` → 56.

- `pdftotext -f 9 -l 9` — page 9 is LIMITATIONS, ending "…and most registrations are timestamped commits with a verdict rule adopted afterwards (Appendix D)." — matching `main.tex:328`.
- `pdftotext -f 10 -l 10` — page 10 begins **"AI USE STATEMENT"**, then ETHICS, REPRODUCIBILITY, REFERENCES, all exempt.

**Main text ends on page 9. Compliant.** `main.log`: 0 undefined references, 0 overfull boxes. Both round-7-edited sentences render and both superseded wordings are absent, so `main.pdf` matches `main.tex`; `cmp main.pdf Reference_Anchoring_Biases_LLM_Judges_v5.pdf` is silent.

**Slack:** N-8(a) and N-8(b) are length-neutral. N-1 through N-7 are entirely outside `main.tex`. Nothing here requires cutting a hedge.

---

## (e) What is genuinely strong — do not break these

1. **The `read_expanded` measurement, and the decision to revert.** I rebuilt the positive control from scratch and got 4 → 1 with exactly the documented losses (`28.1`, `-0.050`, `-0.164` gone, `1011` kept), and the sign control 1 → 0. A team that measures a tempting improvement, finds it removes sensitivity, reverts it, and leaves the dead helper *with the measurement attached* is doing this correctly. `check_cross_doc.py:54-66` should be preserved verbatim.
2. **The F-1 fix is better than what was asked.** Round 7 offered two repairs; the team found a third that makes the value reachable in the submitted PDF *and* reports the placebo as null — the scientifically meaningful fact, and one that cuts against the authors' own thesis. Producer-confirmed.
3. **The ledger guards work for what they cover, and fail loudly.** Verified by perturbation: breaking a totals column fires three distinct mismatches across table, caption and extended prose. The `LEDGER GUARD NOT FOUND` behaviour is intact.
4. **The F-8 non-fix is the right call, for the stated reason.** "A guard that reports four of five verdicts as mismatched would train the reader to ignore all of them" (`SUBMISSION.md:30`) is correct, and documenting the gap beats shipping a noisy guard. Do not let a future round bully this into existence without the multiplier convention being made machine-readable first.
5. **The science re-verified cleanly.** Every number I re-derived in §3, §6 and §7 — all six R30-B cells, all four swap values, the P3 counts, the fix-table claims, both registration tallies — matched its producer or registration. The defects this round are in one caption and in tooling.
6. **The ledger, and printing failures in the main text.** `:171`, `:173`, `:200`, `:269`, `:279` still print falsified or unconfirmed registered predictions in running prose. N-8(a) is a complaint about the sentence, not about the practice.
7. **The abstract's self-limiting sentences**, `:54` "Those benchmarks rarely contain such questions" and `:56` "partly by construction". Eight rounds of page pressure and still there.

---

## Required changes, priority order

| # | Where | Change | Status |
|---|---|---|---|
| 1 | `scripts/check_cross_doc.py:152-153` | **N-1:** the sign fix does not fire for a flip in `appendix.tex`. Make the test two-way and re-run **both** injections, requiring the condensed direction to fire. | **New, BLOCKING** |
| 2 | `appendix.tex:300`, `appendix_extended.tex:535` | **N-2:** `+4.99`, `+4.69`, `+5.32`, `91%`, `98%`, `3,194` have no producer; four pass only by collision, and the colliding table is not in `main.pdf`. Regenerate from a committed producer into a fragment `appendix.tex` inputs, or delete the sentence. | **New, BLOCKING** |
| 3 | `scripts/check_numbers.py:69-71`, `:117-118` | **N-3:** argv paths are discarded whenever the project copy exists, so the supplement run validated the wrong ledger. Make argv exclusive; print the file read. | **New, BLOCKING** |
| 4 | `scripts/check_cross_doc.py:131`, `:153` | **N-4:** both tests are one-way, so a wrong extended-only number that collides with any corpus value is invisible. Demonstrated with `3,264 → 3,494`. | **New, BLOCKING** |
| 5 | `main.tex:173` | **F-3:** "beyond" → "more than"; move the instrument clause ahead of its numbers. | **Carried ×3, BLOCKING** |
| 6 | `scripts/check_cross_doc.py:174`, `SUBMISSION.md:32` | **F-5 remainder:** whitelist the six benign pairs so the steady state is zero; exit 0 on a clean tree; retract "the direct one is the stronger". | **Carried, BLOCKING** |
| 7 | `appendix_extended.tex:185`, `appendix.tex:236` | **F-6:** restore ", 10" and the "or none" / 54–55% qualification. `appendix.tex:43` is false until this is done. | Carried |
| 8 | `appendix.tex:192`, `appendix_extended.tex:217` | **F-7:** one name for the round-30 row. | Carried |
| 9 | `appendix.tex:200`, `:381`, `app:ledger` prose | **N-5:** digits not words; assert and print the failures table's row count. | New |
| 10 | `SUBMISSION.md:26` | **N-6:** one sentence stating that the flag count tests sourcing, not correctness. | New |
| 11 | §3 | Run the counter-instructed swap cell. Still part of what moves 7 → 8. | Carried |

Items 5 and 6 are the only ones touching prose; both are length-neutral.

---

## Closing note to the authors

You fixed F-5 in the direction you could test and did not test the direction that was reported. Round 7 wrote down its injection precisely — `appendix.tex:356`, `$-0.164$` → `$+0.164$` — and that exact injection still reports clean today, because the unsigned token `0.164` shadows it from three CI bounds elsewhere in the extended appendix. The commit says "re-proved". What was proved is that a flip in the *extended* file is caught. **When a review hands you a reproduction, re-run that reproduction, not a sibling of it.** This is the same shape as the thing you got right with `read_expanded`: there, you tested the change against a known-defective input and it told you the truth. Here you tested a different input and it told you what you hoped.

Second, N-2 is F-1 again, and it was reachable by the method you already used. F-1 was "a caption quotes a number the cited table does not contain". `tab:rotation`'s own caption quotes six numbers that **no producer contains**, and your checker flagged one of them — for seven rounds — while the note clearing it, "a CI bound quoted in a caption", described it in a way that made it sound harmless. It is the interval of a point estimate that does not exist. The lesson is not to look harder at flags; it is that a flag should be cleared by naming the **producer key** that sources it. A prose justification is how `+4.69` survived seven reviews.

Third, N-3. `check_numbers.py appendix.tex` does not check the `appendix.tex` you passed. Your own supplement workflow depends on that argument, and `supplement/README.md` records a ledger verification that, run in a tree where the project copy was visible, checked the project's ledger and reported it as the supplement's. A guard whose subject is ambiguous is worse than no guard, because the output is indistinguishable from success — which is the exact principle you articulated when you made the guards fail loudly in round 7. Apply it to *which file* as well as to *whether it matched*.

What is not in doubt: the science re-verified without a single discrepancy across §3, §6, §7, both registration tallies and all six R30-B cells; your `read_expanded` measurement reproduces to the individual lost value and the revert was correct; the F-1 repair is better than either option you were given; and you continue to print your own falsified predictions in the running text. That is what the 7 rests on, and none of this round's findings touch it. The distance from 7 to 8 is item 16, four tooling fixes, and one caption.
