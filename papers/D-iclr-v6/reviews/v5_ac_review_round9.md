# Meta-review (AC), ICLR 2027 — v5, round 9

**Paper:** "Reference Anchoring Biases LLM Judges Toward the Answer They Are Shown When Several Are Correct"

**Artifacts checked:** `main.tex`, `main.pdf` (39 pp), `appendix.tex`, `appendix_extended.tex`, `extended_appendix.pdf` (56 pp), `SUBMISSION.md`, `scripts/check_numbers.py`, `scripts/check_cross_doc.py`, `scripts/cross_doc_residue.txt`, all 69 `tables/*.tex`, `registration_round30.md`, `../D-reference-laws/RESULTS_SUMMARY.md`, `../D-reference-laws/registration.md`, all `papers/analysis/*.json`, commit `d23b80b`, and `reviews/v5_ac_review_round8.md`.

**Method.** I did not accept a single control the authors describe. I rebuilt a lean but complete tree (both appendices, all tables, all registrations, all producer JSONs, `D-reference-laws/`), confirmed it reproduces the clean-tree signature exactly (15 flags, 16 assertion lines, 2 `ledger guards reading:` lines, 0 cross-doc findings, both exits 0, 196 matched pairs), and then ran **18 injected defects** against it — the four the authors documented, plus fourteen they did not anticipate, chosen from the classes named in this round's charge: a colliding wrong value in `appendix.tex`; a wrong value in `appendix_extended.tex` with no condensed twin; a deleted sentence in each file; two changed CI bounds (one sourced, one not); a value altered inside a generated `tables/*.tex` fragment; a stale `cross_doc_residue.txt` baseline; residue-preserving digit slips in both files; a verdict inversion; a ledger row deletion; and an argv-substitution test against a deliberately mangled ledger. Page limit verified by **rendering** (`pdftotext -f 9 -l 10`). I re-derived §3 and §6 from `registration_round30.md` and the `app:r30` tables. I ran no model calls.

---

## (a) Score

**8: good paper, accept. Confidence: 4.** Up from round 8's **7**, and from 7 at rounds 6 and 7.

This is the first round in which a claimed fix survived attacks it was not built against. Round 8's charge was that the authors verify in the direction that passes. I injected six defects they never mention — a colliding value in the condensed caption, two altered CI bounds, a wrong `% kept`, and residue-preserving digit slips in both appendices — and **every one fired**. The N-3 argv fix works on a mangled file I built. N-2's numbers are not unsourced: they are stated verbatim in `RESULTS_SUMMARY.md:193` and `registration.md:2058`, and adding that file to the source list was correct, not a silencing move.

Why not 9. Item 16 is still undone. More to the point, two things this round's work produced are genuinely wrong: the caption at the centre of N-2 **misdescribes the filter that produced its own numbers** (N-1 below, and it is disprovable from the caption's own two percentages), and the N-4 fix shipped with a documented workflow step that **launders exactly the corruption it was built to catch** (N-2 below). Round 8 gave one blocking finding for testing the easy direction; this round gives two for a fix whose escape hatch was written into the instructions beside it.

Why not 7. The four blocking findings are closed on evidence I generated, not evidence they chose. The science re-verified without discrepancy for the third round running.

**9 requires:** item 16; N-1 and N-2 below; and the residue baseline made tamper-evident rather than regenerable-on-request.

---

## (b) Round-8 findings: closed / not closed

All evidence below is from my own injections in full tree copies, not from the authors' reported controls.

| # | Item | Status | My evidence |
|---|---|---|---|
| N-1 (r8) | Sign fix collision-blind; round 7's `appendix.tex` flip still passed | **CLOSED** | Injected round 8's exact defect (`$-0.164$` → `$+0.164$` in `appendix.tex`). Now fires twice: `CROSS-DOC MISMATCH: condensed-only ['+0.164'], extended-only ['-0.013', '-0.117', '-0.164']` and `RESIDUE ADDED: -0.164 now appears only in appendix_extended.tex and did not before`. Exit 1. The `only_cond` pairing test (`:151`) is the mechanism and it is sound. |
| | *…and six defects they did not anticipate* | **ALL CAUGHT** | (i) `$+4.08$` → `$+4.09$` in the `tab:rotation` caption — a value that **does** occur in `appendix_extended.tex`, i.e. the pure collision case → `RESIDUE ADDED: 4.08` + `RESIDUE REMOVED: 4.09`. (ii) `\ci{+4.69}{+5.32}` → `\ci{+4.66}{+5.32}`, where `4.66` is a real value in `tables/rotation_exact.tex` → `MISSING NUMBER: 4.66`. (iii) the same bound → `+4.61`, sourced nowhere → fires. (iv) `91\% kept` → `98\% kept`, colliding with `98` in the same caption → `RESIDUE ADDED: 91`. (v) `$+0.247$` → `$+0.248$` in `appendix.tex`'s R30-A table, a realistic digit slip where **both** values already occur in **both** files → `CROSS-DOC MISMATCH: condensed-only ['+0.248','+0.248'], extended-only ['+0.247']`. (vi) the same slip in `appendix_extended.tex` → fires symmetrically. |
| N-2 (r8) | `tab:rotation` caption's six numbers have no producer | **CLOSED on sourcing; a NEW substantive defect remains (N-1 below)** | Round 8 was wrong that these are unsourced, and the authors are right to have pushed back. `../D-reference-laws/RESULTS_SUMMARY.md:193`: "Applied post hoc to the exact-oracle rotation replication: gainers **+4.99 [+4.69, +5.32]** vs +4.97 unfiltered (Qwen-7B, **91%** retained), **+4.08** vs +4.09 (phi-4, **98%** retained), n=119–120." Verbatim, all six. The sixth, which the commit message does **not** claim and which round 8 flagged separately, is also real: `registration.md:2058` — "Phase 1 margins, corrected Sonnet 5 (rubric a; retained sample **3194/3494** for the filter)". I confirmed the unfiltered baselines tie to the shipped table: `tables/rotation_exact.tex` prints Qwen2.5-7B rubric $a$ `+4.97` and phi-4 rubric $a$ `+4.09`, exactly the "vs unfiltered" values in the source. Adding the file to `text_sources` cleared **only** `+4.69`, twice: with the file removed the run reports **17** flags, the two extra being `appendix.tex:300: +4.69` and `appendix_extended.tex:535: +4.69`. Nothing else was silenced. |
| N-3 (r8) | argv silently ignored; guards validate the project copy | **CLOSED** | `check_numbers.py:81-82` is now `argv_app or [...]`. I mangled a copy to `Falsified & 1 & 1 & 1` and `rows contain 999 not confirmed, 999 falsified` and ran `check_numbers.py <copy>/appendix.tex`: `LEDGER MISMATCH: column 1 rows sum to 257, table prints 290`, columns 2 and 3 likewise, `LEDGER CAPTION MISMATCH: caption says 999 not confirmed, rows sum to 14`, `… says 999 falsified, rows sum to 3`, `EXTENDED LEDGER MISMATCH: prose says 321 total, rows give 285`. Round 8's identical injection reported success; it now fails loudly. The two `ledger guards reading: <path>` lines print the file actually read. |
| N-4 (r8) | Both cross-doc tests one-way; extended-only wrong value invisible | **CLOSED for substitutions; NOT closed for deletions, and newly launderable** | Round 8's own demo (`3,264` → `3,494` in `appendix_extended.tex`) now fires `RESIDUE REMOVED: 3264`, exit 1 — confirmed. A realistic variant, `81 tasks, 825 samples` → `879 samples`, also fires. But see **N-2** (the `--write-baseline` laundering path) and **N-3** (deletions) below. |
| N-5 (r8) | Verdict words and row counts unguarded | **NOT CLOSED, still honestly documented** | `Distance gradient & … (\textbf{falsified}, both judges)` → `\textbf{confirmed}`: 15 flags, 16 guard lines all "matching", cross-doc exit 0. Deleting the whole row: identical clean result. The cheap half **was** done — the spelled-out counts are now digits in both appendices (I re-grepped; the survivors at `appendix.tex:114`, `:139`, `:517` are prose, not counts). |
| N-6 (r8) | Flag count presented as though it measures fidelity | **CLOSED** | `SUBMISSION.md:44` now carries the honest paragraph, and its arithmetic checks: I independently measured 101/101 two-decimal values in 0.00–1.00 accepted and 994/1,001 one-decimal values in 0.0–100.0. My pre-ledger reconstruction gives 6,717 and 424/1,000 integers against the stated 6,722 and 429; the difference is exactly the five values `ledger_totals()` adds at `:219`, so the stated figures are the post-ledger ones and are right. |
| N-7 (r8) | `check_cross_doc.py main.tex appendix.tex` neither done nor declined | **CLOSED** | `SUBMISSION.md:34(ii)`: "run, and it is not applicable", with the 29 false positives itemised. Correct disposition. |
| N-8 (r8) | Readability (4 items) | **3 of 4 done** | §3 recast and "beyond" → "more than" (`main.tex:173`); §6 recast (`:256`); caption split (`appendix.tex:300`). "What we find" unchanged. See **N-7** below. |
| F-7 (r7/r8) | One name for the round-30 row | **DECLINED, and the reason is right** | `SUBMISSION.md:34(i)`. I checked: `appendix.tex`'s `tab:ledger-failures` splits round 30 into two rows naming individual predictions (`:192` "Swap under the direct prompt", `:193` "Chosen reference"), while `appendix_extended.tex:217` is one row naming the experiment. Forcing one label would make the condensed table mislabel its own rows. Do not re-raise. |
| 16 | Counter-instructed swap | **NOT DONE, correctly declared** | `SUBMISSION.md:50`: "Not started: it costs money and was not authorised." Claimed nowhere. |

**Score: 6 closed, 1 partly, 1 correctly declined, 1 correctly deferred.**

### What still escapes both scripts, concretely

Stated as the charge asked, from my injections rather than from the code:

1. **Deletion of anything.** Both scripts are presence tests; neither is a completeness test. Removing the entire "interval that includes zero" disclosure from `appendix.tex:300` — the single best sentence added in round 8 — leaves **15 flags, 0 ledger mismatches, 0 cross-doc findings, both exits 0, and 196 matched pairs, all unchanged**. Same for a `tab:ledger-failures` row. A deletion is caught only by luck, when the deleted text happened to contain the last condensed-only instance of some value.
2. **Any change that preserves the extended-only *set*.** `check_cross_doc.py:198` is `extra = sorted({x for x in ea if x not in set(ca)})` and `:181` is `absent = sorted({x for x in ca if x not in seen})` — both **sets**, never multisets. So a value's *count* may change freely. Demonstrated: altering one occurrence of a value that occurs twice in `appendix_extended.tex`, in a sentence with no condensed twin, to another value already extended-only → both scripts clean.
3. **Anything inside a generated `tables/*.tex` fragment.** See N-4.
4. **Anything non-numeric**: verdict words, judge names, model names, direction words ("above"/"below"), and the registration marks `\pre` / `\ph` / `\reana`.
5. **`main.tex` entirely**, for cross-document purposes — correctly, per `SUBMISSION.md:34(ii)`.

---

## (c) NEW findings

### N-1 — **BLOCKING.** The `tab:rotation` caption misdescribes the filter that produced its own numbers, and the caption disproves itself.

`appendix.tex:300` and `appendix_extended.tex:535`, rendered verbatim in `main.pdf`:

> "The last row keeps only samples **Sonnet~5** scored at least 7 blind (3,194 of 3,494). For the open judges **the same filter**, applied post hoc, gives $+4.99$ \ci{+4.69}{+5.32} (Qwen2.5-7B, 91\% kept) and $+4.08$ (phi-4, 98\% kept)."

"The same filter" has exactly one antecedent: *samples Sonnet 5 scored at least 7 blind*. That is not what produced `+4.99` and `+4.08`. The source the authors added to the checker this round says so in its own section heading. `RESULTS_SUMMARY.md` §6.2, **"The judge's own prior verdicts"**:

> "**Setup.** Registered filter: keep only samples **the judge itself** scored ≥7 of 10 *while blind*, then re-ask whether rotating the reference still moves them."

So Qwen2.5-7B's `+4.99` is computed on samples **Qwen2.5-7B** accepted blind, and phi-4's `+4.08` on samples **phi-4** accepted blind. The caption asserts all three share Sonnet 5's sample set.

**The caption refutes itself on its own numbers.** If the filter were literally the same, the retained set would be the same set, so every judge's kept fraction would be identical. The caption prints **91%** and **98%**. Two different fractions cannot both come from one filter applied to one pool. (Sonnet 5's own fraction is 3,194/3,494 = 91.4%, which rounds to the same 91% that the source attributes to Qwen2.5-7B — a coincidence that makes the error almost impossible to catch by eye, and is presumably why it survived nine rounds.)

This matters beyond wording. The point of the blind-accepted filter is P3: the judge takes back credit it *itself* already gave. Filtering Qwen2.5-7B's scores by *Sonnet 5's* blind acceptances would not test that at all; it would be a different and much weaker claim. The caption as written describes the weaker experiment while quoting the stronger one's numbers.

**Fix.** One clause, length-neutral, in both files:

> "For the open judges the analogous filter on each judge's own blind score, applied post hoc, gives …"

And note that this is N-2's real residue. Round 8 asked whether the numbers had a producer; they did. Nobody asked whether the sentence *describes* them correctly, and it does not. **Clear a caption by checking the source's definition, not only its digits.**

### N-2 — **BLOCKING (tooling, introduced this round).** The documented workflow launders the corruption the new control was built to catch.

`SUBMISSION.md:38` states the fifth control and, two sentences later, the escape from it:

> "Fifth control: that same 3,264 → 3,494 corruption must now report `RESIDUE REMOVED: 3264`."

> "Regenerate it deliberately with `python3 scripts/check_cross_doc.py --write-baseline` whenever the extended appendix legitimately gains or loses a value, and commit the result — an un-regenerated baseline is the failure mode here."

I ran both halves. Round 8's exact corruption alone → `RESIDUE REMOVED: 3264`, exit 1. **The same corruption followed by the prescribed `--write-baseline` step → 15 flags, 0 findings, exit 0, silent.** `check_cross_doc.py:201-203` writes whatever is in the tree at that moment, with no diff shown, no count of what changed, and no record of what the previous baseline held.

The authors have identified the wrong failure mode. An *un-regenerated* baseline is loud — it prints `RESIDUE ADDED` / `RESIDUE REMOVED` and exits 1, and someone must look. The dangerous state is a baseline regenerated **while a defect is present**, which is what the instruction tells a tired author to do at 2am when the check fires and the extended appendix did in fact change for other reasons. That is not hypothetical: the extended appendix changed in several places this very round, so a legitimate regeneration was due, and a regeneration performed then would have absorbed any concurrent corruption invisibly.

Note also that the baseline is 257 bare numbers with no provenance (`scripts/cross_doc_residue.txt`), so a diff of the committed file tells a reviewer that `3264` left the set but not which sentence it left.

**Fix.** Make regeneration tamper-evident rather than silent, so the diff a human reviews is the *change*, not the file:

- `--write-baseline` should refuse to run unless the current check is otherwise clean, or should print the full added/removed lists it is about to bake in and require confirmation;
- write the baseline as `value  <tab>  first 60 chars of the sentence it came from`, so `git diff` on it is readable;
- and record in `SUBMISSION.md` that a `--write-baseline` commit must never be combined with a content commit.

### N-3 — **NON-BLOCKING.** Both scripts are presence tests, so deletion is invisible; and the residue is a set, not a multiset.

Two demonstrations, both in full tree copies:

- Deleting from `appendix.tex:300` the sentence "`\Cref{fig:rotation-pool} quotes the exact scorer, under which Qwen2.5-7B's ``Neither'' cell is $+0.12$, with an interval that includes zero; the full exact-scorer table is in the extended appendix.`" — the round-8 F-1 repair that this review's predecessor called "better than what was asked" — leaves **every output byte-identical to the clean tree**: 15 flags, 16 assertion lines all matching, `0 sentence pairs disagree`, `reverse residue: 257 extended-only values, unchanged`, exit 0.
- Altering one of two occurrences of an extended-only value in an unpaired sentence of `appendix_extended.tex`, to another already-extended-only value, is likewise clean, because `:198` compares sets.

Neither is a new regression — the authors nowhere claim to catch deletions — but the charge asked which class still escapes, and this is the largest one. It is also the class that would silently undo this paper's best hedges, which are exactly the sentences a page-pressure edit removes.

**Fix.** Cheapest useful guard, and it needs no new convention: assert and **print** a small set of structural counts that a deletion must change — the number of sentences in each appendix, the row count of `tab:ledger-failures` (37 today), and the number of `\pre` / `\ph` / `\reana` marks in each file. Any deletion moves at least one. `SUBMISSION.md:30` has conceded the row-count half for three rounds; it genuinely needs no multiplier parsing.

### N-4 — **NON-BLOCKING.** Generated fragments are invisible to one checker and *authoritative* for the other, so a corrupted fragment authorises itself.

`check_numbers.py:35` includes `*sorted((PAPER / "tables").glob("*.tex"))` in `text_sources`; `check_cross_doc.py:20-24` documents that it does not resolve `\input`. So a `tables/*.tex` fragment is simultaneously a thing neither script validates and a thing that makes other numbers "sourced".

Demonstrated: changing phi-4's `$+4.09$` to `$+4.99$` inside `tables/rotation_exact.tex` — a value printed in the shipped PDF, and one of the two "vs unfiltered" baselines N-2 turns on — gives 15 flags, 0 ledger mismatches, 0 cross-doc findings, both exits 0. Worse, the corrupted fragment would thereafter *source* a matching wrong value typed into prose.

The existing mitigation is real and I want it noted: `SUBMISSION.md:25` records that `make_tables.py` was rerun and "all 69 fragments unchanged", which is the guard that actually covers this. The defect is that this guard is a checklist line rather than a check, and the two scripts give no signal at all.

**Fix.** Commit fragment hashes and diff them in `check_numbers.py`, or have the checklist line record the `make_tables.py` rerun's exit status and fragment count. One line either way.

### N-5 — **NON-BLOCKING.** `SUBMISSION.md:44`'s flag breakdown went stale this round, in the paragraph that documents the flags.

The bullet correctly updates the headline — `:42` now reads "takes the run from 5 flags to **15**: 4 in `appendix.tex`, plus 11 in `appendix_extended.tex`", which I verified line by line. But the breakdown two sentences later was not updated with it:

> "Two of those **12** arrived in round 6 at `appendix_extended.tex:895` …"

> "Of those **10**, four duplicate values already cleared in `appendix.tex` (420, **+4.69**, 1192, 7152) and six are new …"

Three errors: the extended count is 11, not 12; "those 10" derives from the stale 12; and `+4.69` is listed as a duplicate flag when clearing it in both files is *this round's* headline tooling change. The correct statement is 11 = 5 occurrences of 4 duplicated values (420, 1192 ×2, 7152, 1011) + 6 new. `1011` is missing from the list entirely.

This is small but it is the exact failure mode round 8's closing note was about: a flag cleared by prose, where the prose is now wrong. **Fix.** Rewrite the two sentences from the current run, and state the duplicate list as values-with-occurrence-counts.

### N-6 — **NON-BLOCKING.** The retraction did not reach the code.

`SUBMISSION.md:32` retracts the claim explicitly and correctly: "**\"The direct one is the stronger\" was claimed here and is retracted**". But `scripts/check_cross_doc.py:163` still reads:

> `# The direct test of the claim, and the stronger of the two. Sentence pairing needs a twin to`

The docstring at `:14-18` likewise still describes only the two original tests and does not mention the reverse residue at all, so a reader of the script learns neither that the direct test was demoted nor that a third test exists. Given that this round's entire thesis is that the *pairing* pass is what catches a wrong value, the surviving comment recommends the weaker test to whoever next edits the file.

**Fix.** Replace the clause with "the weaker of the three: it asks only whether a number appears *somewhere* in a 151 KB file, so it is collision-blind; the pairing pass at `:151` is what catches a value that is wrong rather than absent." Add the reverse residue to the module docstring.

### N-7 — **NON-BLOCKING (readability and marks, requested).**

**(a) The registration mark contradicts the caption's own sentence.** `appendix.tex:300` / `appendix_extended.tex:535` end:

> "For the open judges the same filter, **applied post hoc**, gives $+4.99$ … and $+4.08$ (phi-4, 98\% kept).**\pre**"

`main.tex:33` defines `\pre` as pre-specified; `\ph` is post hoc. The `\pre` superscript lands immediately after the words "applied post hoc", so the rendered PDF shows a post-hoc sentence terminated by a pre-specified mark. The table as a whole is pre-specified and the mark is presumably scoped to it, but nothing tells the reader that. **Fix:** move `\pre` to just after "registered runs)" in the opening parenthetical, where its scope is unambiguous, and end the post-hoc sentence with `\ph`.

**(b) §6, `main.tex:256`.** The recast is a genuine improvement and is substantively true — I checked all four intervals in `app:r30`: `+0.045 [−0.003,+0.092]` includes zero, `+0.213`, `+0.104` and `+0.463` exclude it. But the noun is wrong:

> "given \textsc{MACE}'s own first-listed answer, 26 and 56. **Only one of these four shrinkages** has an interval that includes zero: the SimpleQA grader's, under the first-listed rule."

The four numbers just named — 9, 20, 26, 56 — are **shortfalls** (the `Chosen $-$ list` column: $-0.091$, $-0.203$, $-0.258$, $-0.562$), and main text prints no interval for any of them. The intervals belong to the **shrinkages** (`Chosen $-$ random`), which main text never prints. So "these four" points at four numbers that are not the things being described. **Fix:** "Only one of the four reductions has an interval that includes zero: the SimpleQA grader's, under the first-listed rule." — "reduction" matches "shrinks the shortfall" in the same sentence and does not collide with the four printed values.

**(c) §3, `main.tex:173`.** Round 8's two repairs landed and the sentence is better:

> "Credit still follows the reference, where credit is a yes-or-no judgment rather than the 0--10 score above: answers that stop matching it lose 26 pp for GPT-4.1 and 13 for Sonnet~5. Text matching neither reference moves $-6$ pp for Sonnet~5, **more than** the 5 pp we registered as a bound"

All four values re-derived clean against the `app:r30` table ($-0.264$, $-0.132$, $-0.059$, $-0.032$) and against the ledger. One thing got slightly worse, though: "beyond 5" tolerated an implicit magnitude reading, whereas "**more than** the 5 pp" is an explicit numeric comparison that is false as written, since $-6 < 5$. The registration says "move **at most** 5 points", a magnitude bound. **Fix:** "moves $-6$ pp for Sonnet~5, **a larger move than** the 5 pp we registered as a bound". Length-neutral.

**(d) Introduction, "What we find", `main.tex:93-100`** — unchanged for three rounds and the notes still stand: `:95` opens the most-skimmed paragraph in the paper with an eight-word modifier ahead of its subject ("Run as their authors configure them,"), and a paragraph headed "What we find" ends with three sentences of related work (`:98-100`). Not a defect; still the cheapest remaining readability win.

**(e) The split caption reads well now** and the divergence is right — see (f).

**(f) The two `tab:rotation` captions differ deliberately, and I confirm that is correct, not a divergence.** `appendix.tex:300` says "\Cref{fig:rotation-pool} quotes the exact scorer, under which Qwen2.5-7B's ``Neither'' cell is $+0.12$ … the full exact-scorer table is in the extended appendix"; `appendix_extended.tex:535` says "exact-scorer values for Qwen2.5-7B are in \cref{tab:r4-rotation}". Each points at what its own document contains: `tab:r4-rotation` is labelled at `appendix_extended.tex:407` and exists in **no** form in `appendix.tex`, so the condensed file could not cite it, and the extended file should cite it rather than say "in the extended appendix" of itself. The values check out — `tables/r4_rotation.tex` prints `$+0.12$ {\scriptsize$[-0.07,+0.30]$}` for the exact scorer, matching both `main.tex:165`'s figure caption and the condensed appendix's "includes zero" claim, against `$+0.13$` under the original scorer in `tables/rotation_exact.tex`. That was F-1's whole subject and it is now consistent in all four places. Leave it alone.

**(g) Minor.** `main.tex:171` "All **twelve** registered cells" is the last spelled-out count in the shipped main text; the appendices were converted to digits this round. Convert it too, so the guards can see it.

---

## (d) Overclaims — none found

I cross-checked every quantitative sentence in §3 and §6 against `tab:ledger-totals`, `tab:ledger-failures`, `registration_round30.md` and the `app:r30` tables.

- **Falsified predictions are printed, not buried.** `main.tex:171` ("one registered prediction … failed"), `:173` ("more than the 5 pp we registered as a bound"), `:200` ("our registered loss there was not confirmed"), `:269` ("outside our registered bound"), `:279` ("still failed") and `:270` ("by our registered test, not Sonnet~5's"). Each matches its ledger row.
- **Intervals including zero are disclosed everywhere I checked**: `main.tex:114` (GPT-4.1 factual, Opus 5 one pool), `:173` (GPT-4.1 $-3$ pp), `:198`, `:256`, `:280` ("Opus~5's interval touches zero"), and now `appendix.tex:300`. The split verdict at `appendix.tex:193` and `appendix_extended.tex:217` names the non-confirming cell with its interval, `$+0.045$ \ci{-0.003}{+0.092}`.
- **Ledger arithmetic** re-verified by perturbation, not by reading: 290 + 14 + 17 = 321; breaking `Falsified & 34` → `33` fires `LEDGER MISMATCH: column 1 rows sum to 289`, plus a caption mismatch and two extended-prose mismatches, and takes flags from 15 to 19.
- The abstract's self-limiting sentences survive a ninth round of page pressure: `:54` "Those benchmarks rarely contain such questions" and `:56` "partly by construction".

The only sentence in the paper I would call misdescriptive is N-1's caption clause, and it overstates nothing — it describes a *different* method, in a direction that would make the result weaker, not stronger.

---

## (e) Page limit — **COMPLIANT. Verified by rendering.**

`pdfinfo main.pdf` → 39 pages; `extended_appendix.pdf` → 56.

- `pdftotext -f 9 -l 9 main.pdf` — page 9 is RELATED WORK then LIMITATIONS, ending "…and most registrations are timestamped commits with a verdict rule adopted afterwards (Appendix D)", matching `main.tex:328`.
- `pdftotext -f 10 -l 10 main.pdf` — page 10 begins **"AI USE STATEMENT"**, then ETHICS, REPRODUCIBILITY, REFERENCES, all exempt.

**Main text ends on page 9.** `main.log`: 0 undefined references, 0 overfull boxes. `cmp main.pdf Reference_Anchoring_Biases_LLM_Judges_v5.pdf` silent. I confirmed by rendering that both edited main-text sentences are in the PDF and both superseded wordings are absent, and that the split `tab:rotation` caption renders as intended.

**Slack:** N-1 and N-7(b,c,g) are all length-neutral or shorter. N-2 through N-6 are outside `main.tex`. Nothing here costs a hedge.

---

## (f) What is genuinely strong — do not break these

1. **The pairing-pass fix (`check_cross_doc.py:151-161`) is correct and general.** It caught six defects I designed specifically to evade it, including two where the substituted value already existed in both files. The reasoning in the comment — "an altered number leaves its original in the twin" — is the right invariant, and it is why this works where a symmetric multiset comparison produced only noise. Preserve it verbatim.
2. **Reverting the symmetric comparison, and saying why.** "The extended file says more" really is the normal relationship; I confirmed the residue is 257 values. Choosing a baseline-diff over a symmetric test was the right call and the whitelist of five named benign pairs is the right size — the steady state is genuinely zero findings, so any line is signal.
3. **The `read_expanded` measurement and revert** (`:66-97`), still dead and still annotated. Do not wire it in.
4. **Pushing back on N-2 instead of deleting the sentence.** Round 8 told the authors to regenerate or delete six numbers; the numbers were real, and deleting them would have destroyed correct work. The authors went and found the source. That is the right response to a wrong review, and the right lesson was drawn in the commit — "clear a flag by naming its source, not by describing it". N-1 above is the next turn of that same screw, not a reversal of it.
5. **The argv fix, and printing the file each guard read.** `ledger guards reading: <path>` is exactly the "a guard whose subject is ambiguous is worse than no guard" principle, applied.
6. **The honest paragraph at `SUBMISSION.md:44`** about what the flag count cannot prove. I re-measured the coverage independently and it is accurate. Keep it next to the count forever.
7. **F-7 declined with a reason that is correct on inspection.** Do not let a future round bully the two ledgers into one label.
8. **The science.** Third consecutive round in which every number I re-derived — §3's four swap values, §6's four shortfalls and four intervals, both registration tallies, the ledger columns, the rotation tables — matched its producer or registration with no discrepancy.

---

## Required changes, priority order

| # | Where | Change | Status |
|---|---|---|---|
| 1 | `appendix.tex:300`, `appendix_extended.tex:535` | **N-1:** "the same filter" describes Sonnet 5's blind acceptances; the source says each judge's own. The caption's own 91% vs 98% disproves it. Replace with "the analogous filter on each judge's own blind score". | **New, BLOCKING** |
| 2 | `scripts/check_cross_doc.py:201-203`, `SUBMISSION.md:38` | **N-2:** `--write-baseline` silently absorbs any concurrent corruption, defeating the fifth control. Refuse to regenerate on an otherwise-dirty run, or print the added/removed sets; store provenance beside each value. | **New, BLOCKING** |
| 3 | both scripts | **N-3:** neither script can see a deletion. Assert and print sentence counts per appendix, `tab:ledger-failures`'s row count (37), and the `\pre`/`\ph`/`\reana` mark counts. | New |
| 4 | `scripts/check_numbers.py:35` | **N-4:** `tables/*.tex` are unvalidated yet authoritative. Commit and diff fragment hashes. | New |
| 5 | `SUBMISSION.md:44` | **N-5:** "those 12", "those 10" and "+4.69" are stale; `1011` is missing from the duplicate list. Rewrite from the current run. | New |
| 6 | `scripts/check_cross_doc.py:163`, `:14-18` | **N-6:** the code still calls the direct test "the stronger of the two" after `SUBMISSION.md:32` retracts it; the docstring omits the reverse residue. | New |
| 7 | `appendix.tex:300`, `appendix_extended.tex:535` | **N-7(a):** `\pre` terminates a sentence reading "applied post hoc". Move the mark to the opening parenthetical; end the post-hoc sentence with `\ph`. | New |
| 8 | `main.tex:256`, `:173`, `:171` | **N-7(b,c,g):** "these four shrinkages" → "the four reductions"; "more than the 5 pp" → "a larger move than the 5 pp"; "twelve" → "12". All length-neutral. | New |
| 9 | `main.tex:93-100` | **N-7(d):** "What we find" — front modifier, and three related-work sentences closing the paragraph. | Carried ×3 |
| 10 | §3 | Run the counter-instructed swap cell. Still the single change that moves 8 → 9. | Carried |

Items 1, 7 and 8 are the only ones touching prose; all are length-neutral.

---

## Closing note to the authors

You were right about N-2 and round 8 was wrong, and the way you were right matters: you did not delete a sentence to clear a flag, you went and found the source, and the source says what you said it says — verbatim, in two files, including the `3,194/3,494` that the review flagged separately and your own commit message did not claim. I verified that adding `RESULTS_SUMMARY.md` cleared `+4.69` and **nothing else**, because that was the obvious way to cheat and you did not take it.

So the finding I am left with is the one nobody had asked for. The caption's numbers are sourced; the caption's *sentence* is not. `RESULTS_SUMMARY.md` §6.2 is titled "The judge's own prior verdicts" and its setup line reads "keep only samples **the judge itself** scored ≥7 of 10 while blind". Your caption says "the same filter" with Sonnet 5 as the antecedent, and the two percentages you print — 91% and 98% — cannot both come from one filter on one pool. The digits were checked nine times; the verb was never checked once. **A number is sourced when the source's *definition* matches the sentence, not when the source contains the digits.** That is the same lesson as "name the producer key", advanced one step, and it is the last place in this paper where a nine-round verification habit still has a blind spot.

Second, N-2. You built the reverse-residue check, you wrote down the control it must pass, and then in the next sentence you wrote the instruction that makes it pass silently. I ran your own 3,264 → 3,494 corruption followed by your own `--write-baseline` step, and the tree reports clean and exits 0. You named "an un-regenerated baseline" as the failure mode; it is the opposite. An un-regenerated baseline shouts. A baseline regenerated while a defect is present is indistinguishable from success — and this round, when the extended appendix legitimately changed in several places, was exactly the round when a regeneration was due. You have now built three checkers and this is the third time the hole has been in *the affordance beside the check* rather than in the check: `read_expanded` looked like an improvement, the argv path looked like a convenience, and `--write-baseline` looks like maintenance. Ask of the next one: what does the tired version of me do with this at 2am, and what does the tool print when I do it?

What is not in doubt: four blocking findings closed and verified against fourteen defects you did not design for, six of which I built specifically to defeat your new pairing test and all six of which fired; the argv fix working on a file I mangled myself; the science re-verified across §3, §6, both registration tallies, all four R30-B intervals and all four swap values without one discrepancy; and the caption divergence between the two appendices being right rather than a drift. That is what moves this to an 8. The distance to 9 is item 16, one clause in a caption, and one flag on a command-line option.
