# Round 14 Area Chair review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

Reviewed from `round14_main.pdf` (40 pages: main text pp. 1-9, references pp. 9-11, appendix pp. 12-40). Line numbers are the PDF's margin numbers.

---

## 1. Summary of the claims

LLM judges are usually given a reference answer, and people assume it works as an answer key. The paper shows it does not when a question has several correct answers. The judge scores highly the correct answer it was shown and marks down correct answers that differ from it.

**Main evidence (P1).** On constructed arithmetic tasks with enumerated answer sets, the authors swap the reference from one correct answer to another. The score of byte-identical candidate text moves by 2.7 to 5.4 points out of 10 for Qwen2.5-7B, phi-4 and Claude Sonnet 5 (Fig. 1c).

**Consequence for grading (P2).** Correct answers that differ from the reference become harder to separate from wrong answers. Grading AUROC falls by 0.17 to 0.27 for four open judges and 0.04 to 0.15 for Sonnet 5. With a single correct answer, the reference still raises best-of-64 accuracy by about 30 points.

**Mechanism (P3).** The effect persists on answers the judge already accepts without a reference, most clearly Sonnet 5 on 40 factual MACE questions. The authors conclude that the effect is "agreement", not only "verification failure".

**Moderator.** Reasoning or thinking before scoring removes the swap on arithmetic and shrinks it on factual questions, for reasons the paper cannot identify.

**Downstream.** Best-of-64 selection is hurt mainly on constructed pools where no candidate matches the reference, and not detectably on MACE's natural mix. No scoring protocol is best everywhere. A "keep the higher of blind and referenced score" rule is recommended.

**Was the claim easy to extract?** The headline is easy to get from the title and Figure 1, which is to the paper's credit. Everything after P1 was not. Each secondary claim comes wrapped in qualifiers: which scorer (exact or original), which labels (registered, any-format, model-read, boxed-only), which Sonnet interface (CLI or API), which subsample, and which registration mark. I had to open the appendix several times to tell whether a summary statement actually matched the numbers. That is itself a main finding of this review: the summary layer (abstract, "What we find", Table 1, the Verdict paragraphs, the Conclusion) does not reliably agree with the body.

---

## 2. Score and confidence

**Score: 5/10 (marginally below the acceptance threshold). Confidence: 4/5.**

**The single biggest reason.** The core phenomenon is real, clean and useful. The swap test in Figure 1 is the kind of result that gets remembered. But the reader cannot trust the paper's own summaries. Specifically:

- **Reasoning judges.** Table 1 and the P1 verdict say the effect is near zero "for judges that reason first". The paper's own setup counts Qwen2.5-7B under the MT-Bench template and Qwen3-14B with thinking off as reasoning-first judges, and they lose 3.59 and 1.98 points.
- **Table 1, P3 row.** The verdict says "holds for judges that score without reasoning", but the Observed cell includes the thinking-on arm.
- **Thinking and verification.** Thinking is said not to act through verification, but only the arithmetic AUROC is quoted. The factual AUROC, which does rise, is left out.
- **Scope of P2.** "Holds on natural questions" is claimed for two judges that were never run on MACE.
- **Conclusion.** The recommendation is stated more broadly than Table 2, Table 26 and Table 36 support.

Add the post hoc labels that the headline P2 numbers depend on, and an OSF primary endpoint that never appears in the main text. The result is a paper whose honesty apparatus (the ledger, the marks) is excellent in the appendix but is undercut by the main text. None of this needs new experiments; it is all rewriting and re-plotting. That is why the score is 5 and not lower.

---

## 3. Ranked issues

### MUST FIX (would mislead a reader or block acceptance)

#### M1. "Reasoning-first" means different things in different places, and the summary claims about it are contradicted by the paper's own numbers

**Where**
- l. 089-091: "Reasoning before scoring is the one change that removes the effect, and only on arithmetic".
- Table 1, P1 row (l. 116-118): "near zero for judges that reason first, on arithmetic".
- P1 Verdict (l. 208-209): "it fails on arithmetic for judges that reason before scoring".
- Setup (l. 169-171) versus Figure 3a legend versus Appendix Tables 27 and 43.

**Problem**

1. **The category is defined inconsistently.** Setup l. 169-171 defines rationale-first judges as including "Qwen3-8B and Qwen3-14B with the thinking mode on *or off*". Figure 3a draws thinking-off Qwen3 as hollow circles, "explains first, thinking off". But Table 43 (p. 36, l. 1927-1934) and Table 27 label the same thinking-off Qwen3 cells "**Score only**". One condition carries two labels.
2. **Explaining first does not remove the effect in two cases.**
   - Qwen2.5-7B under the MT-Bench template explains first and still loses 3.59 points (l. 316-317; Table 7: −3.591 [−3.936, −3.242]).
   - Qwen3-14B with thinking off loses 1.98 points (Table 50: −1.98 [−2.50, −1.49]).

   So "near zero for judges that reason first" and "fails for judges that reason before scoring" are false as written. What removes the swap on arithmetic is thinking mode on (Qwen3) or Sonnet 5 explaining first or thinking in the CLI.
3. **"The one change that removes the effect" is overclaimed.** Other changes also remove the margin on arithmetic:
   - a one-step encoding of the reference (Table 30: −0.18 [−0.44, +0.08]);
   - writing the reference as "30+1" (−94% for Qwen2.5-7B);
   - hiding the final answer of a worked reference (+0.05 [−0.52, +0.63]);
   - blind-then-reveal (Table 39: +0.01 inflation).

**Fix**
- In §3, name three conditions and use them everywhere, in the text, Figure 3 legends, Table 27 and Table 43:
  - *score-only*;
  - *explanation first (thinking mode off)*;
  - *thinking mode on*.
- Replace l. 089-091 with: "Letting the judge think before scoring (Qwen3 thinking mode, or Sonnet 5 explaining or thinking) removes the swap on arithmetic; a written explanation alone does not (Qwen2.5-7B under MT-Bench still loses 3.59 points; Qwen3-14B with thinking off, 1.98)."
- Table 1, P1 row, Observed: "... near zero with thinking on (Qwen3) or when Sonnet 5 explains first; 2.0-3.6 when open judges explain without thinking."
- Replace the P1 verdict clause with: "it fails on arithmetic when the judge thinks before scoring."
- Rename the Table 43 and Table 27 column "Score only" to "Thinking off" for the Qwen3 rows.

#### M2. Table 1's P3 verdict contradicts its own Observed cell

**Where**
- Table 1, P3 row (l. 127-130): Observed "Sonnet 5 ranks correct factual answers above a wrong one 94-97% of the time blind, yet the reference widens the matching answer's lead by 3.0-4.0 points"; Verdict "Holds for judges that score without reasoning".
- §6 Verdict (l. 346-347): "P3 holds for judges that score without reasoning first".

**Problem.** The ranges 94-97% and 3.0-4.0 merge two arms (Appendix N, l. 1906-1911): score-only (94.4%, +3.98) and **thinking on** (96.9%, +3.03). So the table's own evidence shows the effect persisting *with* reasoning on factual questions. That is a stronger and different claim than the verdict makes. On arithmetic, P3 cannot be tested for thinking judges at all, because there is no effect left to persist.

**Fix.** Split the Observed cell by arm. Change the verdict to: "Holds on factual questions with and without thinking (Sonnet 5, 40 tasks); untestable on arithmetic for thinking judges, where the effect is absent." Make the §6 Verdict match.

#### M3. "Thinking shrinks the effect" is not supported for Sonnet 5

**Where**
- Abstract l. 023-025: "only shrinks it on factual questions".
- Table 1, "Not predicted" row (l. 131-133): "shrinks it by a quarter to a half".
- l. 319-320: "and by 12.5 pp for Sonnet 5 (17.5 pp with it off)".
- Conclusion l. 429-430: "removes the effect on arithmetic but **not** on factual questions". Note this says "not"; the abstract says "only shrinks". The two must agree.

**Problem**
- **Sonnet 5.** Appendix N (l. 1907-1908) gives the paired margin difference as **−0.95 [−2.45, +0.63]**; the interval includes zero. The false-rejection rises, +17.5 [+5.0, +30.0] and +12.5 [+2.5, +25.0] (Table 43), overlap almost entirely. The registered prediction was scored on "point estimates" (ledger, l. 887-888).
- **Qwen3.** The reductions are real: false rejections go from +44.3 [36.9, 52.3] to +21.6 [13.3, 29.9], and the margin from +7.07 to +3.13.
- **"A quarter to a half" is inaccurate.** The computed reductions run from 24% (Sonnet margin) to 57% (Qwen3-14B false rejections).

**Fix.** Rewrite as: "On factual questions thinking roughly halves the effect for Qwen3-8B and Qwen3-14B; for Sonnet 5 the reduction (−0.95 points [−2.45, +0.63]) is not distinguishable from zero." Use one verb ("shrinks" or "does not remove") consistently in the abstract, Table 1 and the Conclusion.

#### M4. The verification claim for thinking reports only the pool that supports it

**Where**
- l. 320-322: "Thinking does not act through better measured verification: on arithmetic it leaves Qwen3's blind AUROC unchanged (0.85 to 0.86 for 14B, 0.86 for 8B in both modes)".
- Same idea at l. 090-091.

**Problem.** Table 50 (l. 2114) also reports factual blind AUROC. For Qwen3-14B it rises from **0.72 [0.67, 0.77] to 0.81 [0.77, 0.85]** with thinking on (8B: 0.78 to 0.80). That is exactly where the effect shrinks. The sentence as written is selective reporting.

**Fix.** Replace with: "On arithmetic, thinking removes the swap without raising blind AUROC (14B 0.85→0.86; 8B 0.86→0.86). On factual questions it raises Qwen3-14B's blind AUROC from 0.72 to 0.81 while shrinking the effect, so better verification may contribute there." Change l. 090-091 to match.

#### M5. P2 is claimed "on natural questions" for judges that were never run on natural questions

**Where**
- l. 087-088: "P2 holds for the four open judges that passed our score-resolution screen and for Sonnet 5, on constructed and on natural questions."
- §5 Verdict l. 262-263: "every screened open judge and Sonnet 5 grade the others worse, on constructed and on natural questions."

**Problem.** Table 3 lists MACE judges as Qwen2.5-7B, phi-4 and Sonnet 5 only. Qwen2.5-14B and gemma-2-9b have no MACE data.

**Fix.** Rewrite as: "P2 holds for all four screened open judges and Sonnet 5 on constructed pools, and for Qwen2.5-7B, phi-4 and Sonnet 5 on MACE."

#### M6. The headline P2 magnitudes depend on post hoc, unvalidated labels and halve under the cleanest labeling

**Where**
- Abstract l. 018-020 ("0.17 to 0.27 for four open judges").
- Table 1, P2 row.
- l. 252-255.

**Problem**
- **The labels behind the headline.** The any-format labels are post hoc and were not checked against humans. A 30-reply spot check found 3 doubtful (Appendix D, l. 1011-1012).
- **The boxed-only fall is about half as large.** Under boxed-only labels, which need no relabeling, Table 14 gives −0.10 and −0.08 on the replication pool and −0.09, −0.07, −0.14, −0.12 on the k-pool, a range of 0.07 to 0.14. The main text mentions this in one subordinate clause (l. 255) and the abstract not at all.
- **The explanation for the shrinkage is not given.** Table 18 shows that 73-77% of wrong answers that contain the reference's answer are unboxed, which would account for it, but the main text never says so.
- **The label-robust grading metric is missing from the main text.** Table 15 shows the false-rejection rise is almost identical under all four labelings: Qwen2.5-7B replication +28.2 / +27.0 / +25.9 / +28.3; gemma-2-9b k-pool +54.4 / +52.8 / +51.8 / +53.7. It is not quoted in the main text for any open judge.

**Fix**
1. Abstract: "grading AUROC falls by 0.17 to 0.27 (0.07 to 0.14 when only boxed replies are scored)".
2. Add a label-robust number to the abstract and §5: "the share of these correct answers scored 3 or below rises from 0.4% to 28% for Qwen2.5-7B, and by 26 to 28 pp under every labeling we tried (Table 15)."
3. In §5, say in one sentence why boxed-only shrinks the AUROC fall, or say that it is unexplained.
4. Table 1 and l. 253 quote levels "Qwen2.5-7B from 0.91 to 0.63" that appear in no appendix table. Table 14 reports changes only; Table 48 reports 0.87 → 0.60 under registered labels. Add the levels to Table 14 or quote Table 48.

#### M7. The OSF-registered primary endpoint is missing from the main text, and the registration summary hides the splits

**Where**
- l. 092-093: "We registered 156 predictions before their analyses; Appendix B reports all of them, including the 25 that were not confirmed or were falsified."
- The main text never uses the word "inflation".

**Problem**
1. **Outcome switching, in appearance.** The three OSF registrations (Table 4, first three rows) have best-of-64 *inflation* as the primary endpoint. The main text instead leads with swap change, grading AUROC and any-format accuracy. Most of these are † or were registered late: the grading-AUROC endpoint is in the "Exact scorer ... grading" commit, l. 875-886, registered after much data had been seen. A reader who opens Appendix B will see this as outcome switching. That is a pity, because the primary endpoint was **confirmed** and survives relabeling: +1.19 [+1.02, +1.36], then +1.14 and +1.12 (Table 17).
2. **"The 25 that were not confirmed or were falsified" undercounts the failures.** The ledger (l. 732-735) also lists **16 split** predictions (each with at least one failed judge or arm) and **18 not evaluable**. The verdict rule was also applied retroactively on the date of this draft (l. 726-728).

**Fix**
- Add two sentences to §3 "Measurements": "Our OSF-registered primary endpoint was best-of-64 inflation (the standardized score of the chosen answer above answers of the same correctness); it is confirmed (+1.19 SD [1.02, 1.36]) and survives relabeling (Appendix D). We lead with the swap, grading and accuracy metrics because they are directly interpretable; the grading-AUROC endpoint was registered later and its any-format values are post hoc."
- Replace l. 092-093 with: "Of 156 registered predictions, 92 were confirmed, 25 not confirmed or falsified, 16 split across judges, and 18 not evaluable (Appendix B)."

#### M8. Table 2 and the §7 text sit on the same page but use different scorers without saying so, and Table 2 has no intervals

**Where**
- l. 359-361: "lowers k-pool accuracy at k>1 by 30.3 pp for Qwen2.5-7B ... and leaves Qwen2.5-14B and gemma-2-9b within 3 points".
- Table 2 (l. 332) for the same pool, labels and protocol: Reference shown −24.2, +0.0, −3.0, −15.2.
- l. 357 says "about 10 points (Table 2)" for MACE (Table 2: +9.8, original scorer), while Figure 2a and l. 246-248 use exact-scorer MACE values (+29.4 at k=1; Table 49 overall +9.0).

**Problem**
- **Mismatched numbers.** The text quotes Table 13 (exact scorer); Table 2 uses the original scorer. Readers will read −30.3 against −24.2 as a typo.
- **No intervals, coarse resolution.** Table 2 has 33 k-pool tasks, so one task is ±3.0 pp. The "max rule beats blind" cells (+3.0 against +0.0) are one-task differences. The conclusion's recommendation rests on them.

**Fix**
- Quote Table 2's own values in §7 when discussing protocols, and add to Table 2's caption: "Under the exact scorer used in Figure 2 the reference row reads −30.3, −3.0, −3.0, −15.2 on the k-pool."
- Add 95% intervals where they exist (Table 16 for the k-pool; Table 44 for MACE; Table 35 for MATH-500 reveal minus reference), and "one task = 3.0 pp" for the k-pool columns.
- Define "Blind, then reveal" in the caption. At the moment only the max rule is defined there, and the table appears before the text defines the protocol.

#### M9. The Conclusion's recommendation is broader than the evidence

**Where.** l. 431-434: "Score such answers without the reference as well: on our multi-answer pools, keeping the higher of the two scores lost no accuracy for the open judges relative to the better of blind and referenced judging".

**Problem**
1. The max rule was computed on the k-pool (33 tasks) and on MACE's natural mix. It was not computed on the replication pool, so "our multi-answer pools" is too broad.
2. Under registered labels, Table 36 gives the max rule −2.6 for Qwen2.5-14B on the k-pool, below blind.
3. For Sonnet 5, Table 26 gives the max rule on the k-pool as **−2.4 [−5.0, −0.5]**, an interval that excludes zero. This is never mentioned in the main text.
4. The advice concerns *grading* ("a low reference-guided score ... is not evidence that the answer is wrong"), yet l. 372-373 says "We did not measure how these protocols grade."

**Fix.** Rewrite as: "On the k-pool (33 tasks, any-format labels) and on MACE, keeping the higher of the blind and referenced scores matched the better of the two for the four screened open judges; it cost 6.7 points on MATH-500 and 2.4 points for Sonnet 5 on the k-pool, and we did not measure its effect on grading."

#### M10. Registration marks are applied per sentence rather than per number, and are inconsistent with the appendix and the figures

**Where**
- **l. 255-256.** "0.08 for Qwen2.5-7B and 0.06 for phi-4.†" Table 48's caption says the Qwen2.5-7B rows were pre-specified and the phi-4 rows post hoc. Figure 2b marks them correctly: MACE Qwen2.5-7B unmarked, phi-4†.
- **l. 256-259.** A trailing † covers Sonnet 5's 0.04 / 0.08 / 0.15 and "36 pp", which Table 26 marks PRE.
- **l. 307-310.** A trailing † covers the ≥7 filter swaps (+4.99, +4.08, +2.79). Table 5's caption marks them PRE, and the ledger (l. 768-770) lists "Blind-accepted filter ... confirmed".
- **Figure 2a.** In the several-answers block, "MACE, Qwen2.5-7B†" is marked but "MACE, phi-4" is not, although both come from the same pre-specified experiment (Table 44 PRE). The dagger arises only because the Qwen value uses the exact scorer. The registered original-scorer value is identical (+2.0 [−5.1, +9.1] against +2.0 [−5.1, +10.1]), so use it and drop the dagger.
- **Too many mark systems.** The main text uses three marks and the appendix two more (OSF, PRE); readers must track five.

**Fix**
- Attach a mark to each number, or remove in-text marks and carry status only in Table 1 and the figure labels, with a pointer: "status of every number: Appendix B / Table 49".
- Use the same symbols in the appendix as in the main text.
- Restate the marks in each figure caption instead of "Marks as in Section 3" (Figure 2 caption, l. 242-243).

#### M11. The P3 evidence has no noise baseline, and the open-judge filter hardly filters

**Where**
- l. 304-306: "Sonnet 5 gave 81 non-matching correct factual answers a full 10 without a reference; shown a different correct answer as the reference, it scores 19% of them 3 or below".
- l. 307-309: "Restricted to answers scored that high blind, the swap is unchanged".

**Problem**
1. **Sonnet 5's scores are noisy.** Its scores differ between interfaces (exact agreement on 67% of calls, l. 171-172). A blind 10 followed by a referenced ≤3 cannot be read as "accepted, then penalized" without the same statistic for *matching* correct answers scored 10 blind. The data for that control exist: Table 18 gives mean scores 9.19 → 9.99 for matching and 9.09 → 6.93 for differing answers. The main text does not use it.
2. **The ≥7 filter removes almost nothing.** For the open judges it keeps 91% (Qwen2.5-7B) and 98% (phi-4) of samples (Table 5 caption), so "the swap is unchanged" is nearly tautological. The paper itself says the filter admits 24-30% of wrong answers (l. 306-307).

**Fix**
- Add the matching-answer control from existing score files: "Of matching correct answers scored 10 blind, x% are scored 3 or below with the reference." If that is not computable, quote the Table 18 means.
- Drop the ≥7 open-judge sentence, or state that "the filter removes only 2-9% of samples". Keep the t=9 result (73-81% kept; Table 49) and the AUROC-tercile result as the open-judge evidence.
- Use the exact-scorer +5.27 (Table 49) rather than the original-scorer +4.99, so the number matches Figure 1c.

#### M12. Sonnet 5 appears with two different factual false-rejection effects that are never reconciled

**Where**
- l. 257-258: MACE false rejections "rises by 36 pp" (API, 16-candidate subsamples; Table 26 +35.6).
- l. 320 and Figure 3b: "17.5 pp with it off" (CLI, one answer of each kind; Table 43).

**Problem.** The reader sees two numbers for Sonnet 5's score-only false-rejection rise on MACE that differ by a factor of two. Separately, the Figure 3 caption's "60 tasks with one answer each" reads as tasks with k=1, where a swap is impossible. Appendix N says one sample of each type per task.

**Fix**
- Add after l. 320: "(17.5 pp in this CLI design with one answer of each kind per task, against 36 pp on the API's 16-candidate subsamples; we do not compare across interfaces)."
- Figure 3 caption: replace "60 tasks with one answer each" with "60 tasks, one candidate of each type (gains, loses, matches neither)".

#### M13. Key terms are used before they are defined, or never defined in the main text

**Where and problem**
- **"Pass-rate band"** (l. 157, l. 327): never defined in the main text; Appendix A gives pass rate in [0.2, 0.8].
- **"Score-resolution screen"** (l. 088, 110, 172): the text never says what it checks (distinct score values and ties at the maximum; Table 41).
- **"Two rubrics, three readouts"** (l. 202-203): rubrics a and b are never introduced in the main text, and "readouts" is undefined.
- **"Replication pool"**: the reader cannot tell what it replicates (the exploratory Ties observation, Appendix F).
- **"Lead"** (abstract l. 023; Table 1) is used for what §3 calls the "margin".
- **Appendix vocabulary**: "rotation", "inflation", "anchoring margin", "gainers/losers/placebo" all appear in the appendix, and Appendix C (l. 903) admits the swap test "is called rotation in this appendix".

**Fix**
- Add a compact glossary to §3 covering: pass-rate band; screen; rubric a/b; swap = rotation; margin; inflation (one line).
- Rename the "replication pool" to something descriptive (e.g., *constraint pool*), or say in one clause what it replicates.
- Use "margin" everywhere instead of "lead".
- Rename appendix terms to match the main text.

#### M14. How MACE entity answers are matched to the reference is never described

**Where**
- l. 180-181: "MACE and MATH-500 use their answer lists and unique answers".
- Appendix A (l. 648-650) describes matching only as "the last \boxed{} content, loosely normalized".

**Problem.** For entity answers ("Nile" vs. "Nile River", language names with variants), a surface-form mismatch would turn a *matching* correct answer into a "non-matching correct" one. That would directly inflate the MACE P2 numbers (AUROC −0.08 / −0.06 / −0.15) and the P3 headline (Sonnet 5 +4.0 margin, 19% false rejections). No matching rule or alias handling is described anywhere in the paper.

**Fix**
- Describe the rule in Appendix G.
- If the stored outputs allow it, report the share of "non-matching correct" MACE answers that are aliases of the reference.
- Otherwise add it to Limitations and word the MACE claims as upper bounds.

#### M15. Formatting and reference errors

- **Table 49 overflows the page (p. 39).** The page number "39" is printed on top of the table, and the last rows (the Sonnet 5 replication and k-pool rows) run past the bottom margin. Use `longtable` or split the table.
- **Wrong cross-reference in Appendix A (l. 641-643).** "The command-line replication of Section 4" should point to §6 / Appendix N. Section 4 has no CLI run.
- **Inconsistent rounding.** The abstract says "2.7 to 5.4 points"; the Conclusion (l. 427) says "3 to 5 points". Use one.
- **Reversed percentage order.** Appendix J (l. 1620-1621) gives "94% and 77%", while §6 (l. 339) gives "77% and 94%" for the same pair of judges. Use the same order.

---

### POLISH (presentation, story flow, cognitive load)

#### P1. Too many conditions for a reader to track

To follow §5-§7 the reader must hold in mind:
- ten pools or subsamples: replication, k-pool, synthetic grid, MACE, MATH-500, exploratory Ties, the 120-task Qwen subsample, the 60-task CLI subsample, the 16-candidate API subsamples, and the 40-task MACE triples;
- four labelings;
- two scorers;
- two Sonnet interfaces;
- three marks.

For comparison, the Mirage paper (2304.15004) asks the reader to track one manipulation, the choice of metric.

**Fix**
- Use the exact scorer everywhere in the main text and mention the original scorer only in Appendix O.
- Use any-format labels, with boxed-only as a stated lower bound.
- Remove the synthetic grid and Llama-3.1-8B from §3 (they appear only in the Table 1 caption).
- Stop naming the MT-Bench template in the P1 verdict and move it to the reasoning paragraph.

#### P2. Every prediction is stated four or five times

Each prediction appears in:
- the intro list (l. 077-085);
- Table 1;
- the "Prediction." paragraphs (l. 195-196, 214-215, 269);
- the Verdict paragraphs;
- "What we find" (l. 086-093);
- the Conclusion.

**Fix.** Delete the three "Prediction." paragraphs and merge "What we find" into one short paragraph that points to Table 1. That frees about 15 lines for M7, M12 and P6.

#### P3. The three-readings framework promises more discrimination than it delivers

In Table 1 the "Verification failure" and "Agreement" columns hold identical entries for P1, P2 and P2′. Only P3 separates the two non-key readings, and P3 rests on one frontier judge, 40 factual tasks, and the tercile analysis.

§2 also carries unnecessary notation:
- κ is introduced and never used again;
- v_c is defined as a reliability in [0, 1] but operationalized as a single blind score of ≥7 or 10;
- "β < 1, relative to the noise ε" (l. 142-143) is unclear.

**Fix**
- Say at l. 076: "P1 and P2 test the answer-key reading; only P3 separates the other two."
- Drop κ from the equation.
- State the two routes to P2 in words.
- In Table 1, replace the three reading columns with one column, "rules out".

#### P4. The data show a penalty more than a bonus, and the framing undersells false rejection

- **Figure 1b.** Blind 10.0, matching reference 9.3, different reference 2.9.
- **Table 18 (Sonnet 5).** Matching answers go 9.19 → 9.99 (+0.8); differing answers go 9.09 → 6.93 (−2.2).
- **Table 49 (Qwen2.5-7B).** Correct non-matching answers scored ≤5 rise from 1.9% to 68.9%.

The practical harm is that *correct answers get rejected*. The title's "favor the correct answer they are shown" is accurate but soft. The abstract never gives a false-rejection number for open judges.

**Fix**
- Lead the P2 sentence of the abstract with the false-rejection rate (see M6).
- In §2, note that λ is relative, i.e. that it can be realized as a penalty on mismatches.

#### P5. The prompts themselves instruct the judge to compare with the reference

Appendix A (l. 678-683) gives the referenced rubrics:
- rubric (a): "using the reference to check it";
- rubric (b): "Compare the candidate response against the trusted reference answer provided".

The "agreement" reading therefore cannot be separated from following instructions. Limitations mention only the word "trusted".

**Fix**
- Add "or because the prompt tells it to compare" to the definition of agreement (l. 074-075).
- Add the instruction wording to Limitations.
- Point out that the any-valid-answer instruction partly addresses this: it closes phi-4's margin but fails for small Qwen judges.

#### P6. The mitigation practitioners will try first is not in the main text

That mitigation is showing several references. Appendix M (l. 1760-1764) reports that min(3, k) references remove the margin on the Qwen-generated grid but largely fail for Qwen2.5-7B on the Llama-generated grid.

**Fix.** Add one sentence to §7 "Protocols".

#### P7. "How the reference is written" sits under P3 but does not test P3

l. 337-345 concedes that these tests "show what the judges respond to rather than separating the readings". The instruction sentence (l. 343-345) is about mitigation.

**Fix**
- Move the masking results to a single sentence, either at the end of §4 ("the pull comes from the literal answer string") or in Appendix J.
- Move the instruction result to §7.

#### P8. "Points" means two different things

- "points out of 10" for score changes (l. 017);
- "points" for accuracy (l. 246: "28.6 points");
- "pp" for accuracy elsewhere (l. 360: "30.3 pp ... within 3 points" in the same sentence);
- Figure 3b's x-axis says "(points)" for a rate.

**Fix.** Use "points" only for the 0-10 score and "pp" for every change in a rate or accuracy, in the text, Table 2, Figure 2a and Figure 3b.

#### P9. §7 "Natural data" says "the single-answer questions dominate" (l. 357)

Only 34 of 133 tasks are single-answer. They dominate the *gain*, not the mix.

**Fix.** "the +29 pp gain on the 34 single-answer questions outweighs the null on the 99 multi-answer ones."

#### P10. The intro asserts harm before showing evidence, and cites a setting that was never tested

- l. 066: "It is not safe where answers are not unique" is asserted before any evidence.
- NQ-open (30% multi-answer) is the motivating natural setting, but it is never tested.

**Fix**
- Change to "It is untested where answers are not unique".
- In Limitations, state that open-domain QA such as NQ-open is untested and that the natural-data evidence is 133 MACE River/Language questions.

#### P11. Scope of the P1 claims

- l. 202-204 and the P1 Verdict (l. 207-208) list "Qwen2.5 1.5B to 14B" among swapped judges. Those swaps are only on the exploratory Ties pool, whose answer lists are known to be incomplete (Appendix F).
- l. 172-173 promises grading AUROC for Mistral-7B, but Mistral appears neither in Figure 2b nor in the text. Table 14 gives −0.08.

**Fix**
- Say "on the exploratory Ties pool" for the 1.5B-14B swaps.
- Add Mistral to Figure 2b or drop the promise.

#### P12. Appendix N's ceiling sentence (l. 1880-1881) explains only half the null

The sentence says thinking-judge scores "leave no room for a reference to move them". A ceiling explains the null *gain*. It does not explain the null *loss* (moved off −0.01 [0.00, +0.03]), which was free to fall. The main text wisely uses the "moved off" direction.

**Fix.** Correct the appendix sentence.

#### P13. The appendix reads as a lab notebook: 29 pages, 50 tables, 9 figures

Appendices F (Ties), K (code and answer format), L (DPO), P (MathConstraint pilot), the decode-cost study and the lure and dose studies support no main-text claim beyond one Limitations bullet.

**Fix.** Split the appendix into:
- "Details for main-text claims" (A-E, G, H, N, O);
- "Additional registered studies" (the rest), each opening with a two-sentence summary and its ledger verdict.

#### P14. Wording nits

- **Table 1, P3 row.** The "—" under Answer key should read "ruled out by P1".
- **Figure 1c caption.** "between two answers it matches neither of" should read "for answers that match neither reference".
- **Abstract.** "The effect is not only a failure to verify" packs a double negative into the hardest claim. Try: "The effect persists on answers the judge already accepts".
- **Intro prior-work paragraph (l. 094-099).** Mention Kapetanovic et al. (2026), the closest "anchoring" work, which is currently cited only in Related Work.

---

## 4. Figure-by-figure and table-by-table critique

### Figure 1 (p. 1): concept figure

**Earns its space. Legible. The best thing in the paper.** Panel (b) makes the core idea visible in two seconds, and panel (c) generalizes it.

- **Example selection.** The example was picked for a large swap (disclosed; Appendix A). It swaps 6.4 points against a mean of about 5.3. Acceptable.
- **Qwen label.** Remove "‡" from the axis label "Qwen2.5-7B‡"; put status in the caption.
- **Missing consequence.** The figure shows P1 only. The practical harm, false rejection, is not in it. Consider a fourth mini-panel or an annotation on (c): "correct answers scored ≤3: 0.4% blind → 28% with a different reference (Qwen2.5-7B)". This uses existing data (Table 49).
- **Caption.** The caption stands alone, but (c) packs three task counts and three "neither" values into one parenthesis. Split it.

### Table 1 (p. 3): predictions against observations

**The concept earns its space. The execution does not yet.**

- **Too dense.** Six narrow `footnotesize` columns hold cells of prose, numbers and marks.
- **Uninformative columns.** Two of the three "reading" columns are identical in every row except P3 (P3 in the essay above).
- **Inconsistencies.** It contains the M1, M2 and M3 inconsistencies, which makes it the most dangerous object in the paper, because reviewers skim it.
- **Honest but long caption.** The caption lists failed predictions, which is commendable, but it makes the caption long.

**Fix.** Collapse the reading columns into one "Rules out" column. Split the P3 Observed cell by arm. Apply the M1-M3 wording.

### Figure 2 (p. 5): one answer against several; selection and grading

**Earns its space.** Fonts are legible at print size.

- **Asymmetric design.** Panel (a) shows selection for both cases; panel (b) shows grading only for several answers. That invites the question "what happens to grading with one answer?" Overall AUROC at k=1 exists (Table 49: MACE Qwen2.5-7B +0.29, phi-4 +0.23; k-pool +0.01 to −0.07). Add a "One correct answer (overall AUROC)" block to (b) to make a clean 2×2, the figure grammar the title promises.
- **Marks clutter.** 11 of 12 labels in (a) carry † or ‡. Move marks to a status column or the caption.
- **Label robustness is missing.** The any-format-only dots hide the label dependence of M6. Figure 6 (appendix) already overlays registered, model-read and boxed ticks and is the better figure. Promote its tick marks into Figure 2b.
- **Title undersells panel (a).** Panel (a) also shows several-answer selection losses on the k-pool, which the title does not mention. Suggested title: "With one correct answer the reference helps; with several, it degrades grading everywhere and selection only on constructed pools."
- **Caption.** "Marks as in Section 3" should restate the marks. Replace "Squares ... so its selection is not shown" with a separate sentence.

### Figure 3 (p. 6): reasoning moderator

**Partly earns its space.**

**Panel (a)**
- It needs the disclaimer "three designs that should be compared only within a group", which signals a design problem.
- The "Full replication pool" group (−5.41, −3.92, −2.66) duplicates Figure 1c and has no within-group comparison. Cut it.
- Keep the Sonnet CLI triplet, the Qwen3 off/on pairs, and MT-Bench Qwen2.5-7B.
- The hollow-circle legend "explains first, thinking off" conflicts with Table 43's "score only" label for the same Qwen3 cells (M1).

**Panel (b)**
- The legend "thinking off" means score-only for Sonnet but explanation-first for Qwen3.
- The "+0.0" value labels overlap the axis.
- The x-axis should say pp.
- Mark the Sonnet row as not significant (M3).

**Caption.** "60 tasks with one answer each" is misleading (M12).

### Table 2 (p. 7): protocols

**Earns its space only if it can bear the recommendation, and currently it cannot.**

- no intervals;
- original scorer while the adjacent text uses the exact scorer (M8);
- k-pool cells at one-task resolution;
- "Blind, then reveal" undefined in the caption.

The title "No protocol is best everywhere" is weaker than what the table shows. Suggested title: "Keeping the higher score protects multi-answer selection but costs up to 6.7 pp with unique answers".

### Appendix figures

- **Figure 4 (p. 19).** Legible. Panel (a)'s three light series are hard to separate in grayscale. It uses the original scorer and registered labels, so its caption should say its numbers do not match Figure 2a.
- **Figure 5 (p. 21).** Clear. The caption honestly says the k=1 step "is not an independent test". Fine.
- **Figure 6 (p. 22).** The best robustness figure in the paper. It should inform Figure 2 (above). The "not defined (one correct answer)" text inside the plot area is good practice.
- **Figure 7 (p. 26).** Fine. Motivation only.
- **Figure 8 (p. 32).** Fine. Could be cut along with Appendix K (P13).
- **Figure 9 (p. 33).** Legible. The arrows help. Its bars use the original scorer.

### Appendix tables

- **Table 4 (ledger, pp. 14-17).** Valuable and unusually honest; keep it.
- **Table 14 (AUROC under four labelings) and Table 15 (false rejections under four labelings).** Central to M6; referenced well.
- **Table 27 and Table 43.** Carry the "score only" mislabel (M1).
- **Table 36.** No intervals; conflicts with the main-text claim as noted in M9.
- **Table 48.** Its caption does the reconciliation work the main text should do.
- **Table 49 (p. 39).** Overflows the page (M15). It is a grab-bag of "numbers quoted in the main text": useful for auditing but hard to read. Group rows by main-text section and add the section number.
- **Tables 9, 11, 13, 46.** Dense bracketed CIs in `scriptsize` are readable on screen but marginal in print. Acceptable in an appendix.

---

## 5. What would move the score (no new experiments)

### +1 (to 6): make every main-text claim match the paper's own numbers

1. **Reasoning and thinking.** Apply M1-M4: rename the reasoning conditions consistently, fix Table 1's P1 and P3 rows and the Verdicts, report the Sonnet thinking difference with its interval, and give factual as well as arithmetic AUROC.
2. **Scope and scorer.** Apply M5, M8 and M9: correct P2's natural-question scope, reconcile the scorer between Table 2 and §7 and add intervals to Table 2, and narrow the Conclusion's recommendation (adding the Sonnet max-rule loss).
3. **Registration.** Apply M7 and M10: put the confirmed OSF primary endpoint in the main text in two sentences, give the full ledger counts (splits and not-evaluable included), and fix mark placement.
4. **Terms and mechanics.** Apply M12-M15: reconcile the two Sonnet numbers, add a glossary, describe the MACE matching rule, and fix the Table 49 overflow and the wrong cross-reference.
5. **Units and rounding.** Apply P8, plus the consistent rounding in the abstract and Conclusion.

### +2 (to 7): restructure around one question and robust numbers

Everything in +1, plus:

1. **One question, one robust headline.** Keep the title's question: "does the reference act as an answer key?" Make the abstract's second sentence the label-robust false-rejection result: 0.4% → 28% for Qwen2.5-7B, consistent across all four labelings (Table 15). Give the AUROC fall as a range with its boxed-only lower bound (M6).
2. **Honest mechanism scoping.** State that P1 and P2 only rule out the answer key, and that P3 is the single discriminating test (P3 in the Polish list). Scope P3 to Sonnet 5 on 40 factual tasks, plus Qwen2.5-7B's t=9 filter and the AUROC tercile. Add the matching-answer noise control from existing scores (M11). Drop κ, and acknowledge that the prompts instruct comparison (P5).
3. **Cut repetition and conditions.** Delete the "Prediction." paragraphs (P2 in the Polish list), cut §3 to one scorer and one labeling (P1 in the Polish list), and move masking and instruction results out of §6 (P7). Use the freed half page for a short "What practitioners should do" paragraph in §7. It should cover the max rule with its honest resolution caveats, multiple references (P6), and the instruction.
4. **Figures that carry the argument.**
   - Figure 1 gains the false-rejection annotation.
   - Figure 2 becomes a 2×2 with label-robustness ticks borrowed from Figure 6.
   - Figure 3a drops the duplicated group, and its legends follow the three named conditions.
5. **Appendix as expansion.** Split it into "details for main-text claims" and "additional registered studies", and rename appendix terms (rotation, inflation, rubric) to the main-text vocabulary (P13).

### What cannot be fixed by rewriting

These need new experiments, so the paper should word the claims narrowly instead.

- **Human-validated labels.** The any-format labels need human validation. Until then, write "under automated relabeling (88% agreement with a model reading; not human-checked)" and present the boxed-only result as the conservative estimate.
- **Natural data.** Natural multi-answer evidence beyond 133 MACE questions (e.g., NQ-open) is missing. Write "on one natural benchmark (MACE River/Language)" and do not generalize to open-domain QA.
- **Frontier judges.** Thinking effects and grading protocols for frontier judges beyond Sonnet 5 are untested. Write "for Sonnet 5 (one frontier judge, two interfaces)".
- **Mechanism.** Whether thinking helps through verification or through reduced attention to the reference would need a manipulation of verification. Keep "our data do not say" (l. 322-323); it is the right sentence.
