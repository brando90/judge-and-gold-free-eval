# Final pre-submission check: "The Reference Is Not an Answer Key"

**What I read.**
- **PDF.** `The_Reference_Is_Not_an_Answer_Key.pdf`, 51 pages, built 18:23. I read every page as an image.
- **Sources.**
  - `main.tex` and `appendix.tex`, with a word diff from `ae5f363` (round 24) to `a73ab91` (final).
  - `tables/*.tex` and `papers/analysis/*.json`.
  - `registration_round19.md` to `registration_round23.md`, and `supplement/preregistration/`.
  - `main.log`, `pdfinfo`, and the contents of `supplement.zip`.
- **Line numbers** are the PDF margin numbers.
- **Writes.** Nothing in the project was modified other than this file.

## (a) Verdict

**Not ready as-is, but ready after about 1-2 hours of fixes, with no new data. ICLR score: 8/10, confidence 4/5.** The science and nearly every number hold: 44 of the 46 checks below match, and one more is correct but needs its registration mark fixed. The last round's wording changes read cleanly, and no dangling reference survived the trims. What remains:
- **A miscount in rewritten text.** Section 7 says 27 registered benchmark predictions; the ledger has 30.
- **A registration-status error.** The Table 2 caption labels the max-rule and blind-then-reveal AUROC cells as pre-specified. The appendix, the registrations and the Limitations all say they are post hoc.
- **A new layout defect.** Page 8 is about 40% blank.
- **A stale supplement.** It predates the final version and lacks the round-23 registration and data.
- **An appendix table** (Table 16) runs into the footer.

Everything else passes:
- **Page limit.** The Conclusion ends on p. 9 at l. 485.
- **Figure 1** is on p. 1.
- **Figure fonts are at least 7 pt** at print size: Fig. 1 about 7.3; Fig. 2 7.37; Fig. 3 7.41; Fig. 4 7.60; Fig. 9 7.55.
- **No undefined references** in `main.log`.
- **No anonymity leak.**
  - `pdfinfo` Title and Author are empty.
  - No names, affiliations or URLs appear in the PDF. Chen et al. (with Koyejo) is cited in the third person, which is acceptable.
  - A scan of `supplement.zip` for author names, affiliation and `/Users/` paths found nothing.

## (b) BLOCKERS

### B1. Section 7 undercounts the registered benchmark predictions
- **Location.** p. 7, l. 370-371 (`main.tex` l. 221).
- **Quoted text.** "All 27 registered predictions here were confirmed."
- **Problem.** The paragraph reports four registered experiments:

  | Experiment | Predictions |
  |---|---|
  | R20-C, Sonnet 5 grader | 3 |
  | R21-A, Opus 5 and Haiku 4.5 graders (4 predictions × 2 graders, plus 1) | 9 |
  | R22-B, second draw (3 × 3) | 9 |
  | R23-A, regrade (3 × 3) | 9 |
  | **Total** | **30** |

  All 30 were confirmed. The count of 27 omits R20-C, whose Sonnet 5 results open the paragraph and appear in Figure 4.
- **Sources.**
  - `registration_round20.md` l. 53-55 and l. 112 (P-R20C1-3 confirmed).
  - `registration_round21.md` l. 76-80.
  - `registration_round22.md` l. 81-83.
  - `registration_round23.md` l. 62-64.
  - Ledger rows "Benchmark scores", "Two more benchmark graders", "Second reference draw" and "Same-reference regrade" (p. 19).
- **Replacement.** "All 30 registered predictions here were confirmed."

### B2. The Table 2 caption labels post hoc cells as pre-specified
- **Location.** p. 8, l. 417-418 (`main.tex` l. 226).
- **Quoted text.** "Pre-specified: the API judges' and blind-then-reveal values, Qwen2.5-7B's MACE grading, and MACE accuracy (original scorer); MATH-500 reference accuracy is a re-analysis; the rest is post hoc."
- **Problem.** Three groups of cells are labeled pre-specified but are post hoc:
  - The API judges' **Max rule** cells (−0.01, −0.01).
  - All seven **Reveal − ref.** cells, which are grading AUROC.
  - The open judges' **MACE Max rule** cells (AUROC −0.01, −0.01; accuracy +4.0, +6.1).

  This contradicts the paper's own Section 7 ("chosen post hoc") and Limitations ("only its benchmark result for two graders was registered in advance").
- **Sources.**
  - The appendix Table 45 caption (p. 41): "the max rule and the paired differences are post hoc".
  - `registration_round21.md` l. 10: "under the max rule (post hoc, `r20g_frontier_safeguards.json`)".
  - Table 16 (p. 26), the source of every Reveal and open-judge Max rule cell, is marked † as a whole.
  - No registration contains a blind-then-reveal AUROC readout. A grep of `registration_round*.md` and `supplement/preregistration/` found none. Round 8 registered only the API judges' max-rule best-of-16 accuracy, as a readout, and that value is not in Table 2.
  - The MACE Reference accuracy values are the same under both scorers (`r3_mace_accuracy_results.json` k>1: 0.0202, 0.0606 = `r16c`), so labeling them pre-specified is correct.
- **Replacement** for that sentence:
  > "Pre-specified: the API judges' Reference and Sentence values, Qwen2.5-7B's \textsc{MACE} Reference grading, and \textsc{MACE} Reference accuracy (the original scorer gives the same values); MATH-500 Reference accuracy is a re-analysis; every Reveal $-$ ref.\ and Max rule value, and the rest, is post hoc."

### B3. Page 8 is about 40% blank (new this round)
- **Location.** p. 8, l. 382-410: blank space between the end of "What helps" and Table 2 at the page bottom. Section 8 then starts on p. 9.
- **Cause.** Table 2 changed from `[t]` to `[!b]` this round (word diff `ae5f363..a73ab91`). The `\FloatBarrier` at `main.tex` l. 255 then flushes the pending bottom float and ends the page.
- **Why it matters.** A reviewer on p. 8 sees a formatting error in the main text.
- **Fix.**
  - Delete `\FloatBarrier` at `main.tex` l. 255, so Related work flows into the space above Table 2.
  - Recompile, then check that Table 2 is still on p. 8 and the Conclusion still ends by p. 9 (the fix should free about 28 lines).
  - If Table 2 then drifts past Related work, put `\FloatBarrier` after the Limitations list instead.

### B4. `supplement.zip` is stale: the round-23 registration and data are missing
- **Location.** Outside the PDF, but promised by the Reproducibility statement (p. 10, l. 510-514): "the analysis scripts that produce every number ... and the registration documents".
- **Problem.**
  - `supplement.zip` (17:41) and `supplement/preregistration/` predate the final commit.
  - Neither contains `registration_round23.md`. The zip listing also shows no `r23a_regrade_*.json`.
  - The abstract ("against about 3 when the same reference is re-graded"), Table 1, Section 7, the ledger row "Same-reference regrade" and the Limitations all rest on R23-A.
  - `supplement/preregistration/registration_ledger.md` is dated 05:36 and may not match the 206-prediction ledger.
- **Fix.**
  - Rebuild `supplement.zip` from `a73ab91`. Add:
    - `registration_round23.md`, anonymized with commit hashes tokenized and the new tokens added to `supplement_hash_map.private.md`;
    - `r23a_regrade_{sonnet,opus,haiku}.json`, `r23_regrade_analysis.py` and the regrade score files;
    - the current ledger.
  - Check that every JSON cited in `papers/analysis/MANIFEST.md` for rounds 20-23 is present (`r22c`, `r22d`, `r21a_mace_acceptance`).
  - Re-run the anonymity scan on the new zip.

### B5. Appendix Table 16 overflows the bottom margin (p. 26)
- **Location.** p. 26, l. 1350-1403. `main.log`: "Float too large for page by 17.73491pt on input line 321" (`appendix.tex` l. 314-321). The bottom block's last rows ("MATH-500, solution / Qwen2.5-14B") run into the page number.
- **Fix.**
  - End `tab:protocol-grading` after `\input{tables/protocol_selection.tex}`, and delete the "Bottom: ..." sentence from its caption.
  - Put `protocol_exact.tex` in its own `\begin{table}[htbp]`, with this caption and a new label:
    > "The reference and the max rule under the exact scorer, changes against blind judging (95\% CI); the values quoted in \cref{tab:protocols}. From stored scores.\ph"
  - Recompile and confirm the warning is gone.

## (c) SHOULD FIX

1. **The Figure 4 title is stronger than the data** (p. 7, l. 339-340; `main.tex` l. 216).
   - **Quoted text.** "blind, Sonnet 5 and Opus 5 do not."
   - **Problem.** Blind, Sonnet 5 scores all four models below their lists: −1.3, −2.0, −2.7 and −0.7 (`r20c_leaderboard.json` `blind_minus_list`; pooled −1.7 [−3.5, 0.0]). The body says "stay within 3 points".
   - **Replacement.** "**Shown the reference, every grader scores the models below their answer lists; blind, Sonnet 5 and Opus 5 stay within 3 points of them.**"
2. **Missing † marks in "What helps"** (p. 7, l. 376-377; `main.tex` l. 253).
   - **Problem.** The k-pool and MACE max-rule AUROC values are all post hoc, and so is Sonnet 5's benchmark max rule. By the paper's rule ("a mark on a range applies to at least one value in it") both ranges need †. The cost clause in the same paragraph already carries one.
   - **Replacement.** "...keeps grading AUROC within 0.03 of blind on the $k$-pool and \textsc{MACE},\ph{} and pooled benchmark accuracy within 2 points of the answer lists for all three graders\ph{} (5 points for one model under Haiku~4.5; \cref{fig:benchmark})."
3. **Misplaced † in the Section 5 Verdict** (p. 6, l. 299-300; `main.tex` l. 183).
   - **Problem.** The † sits after "(Appendix E)." at the end of the sentence, so it also attaches to the registered +2.0 and +6.1 (Table 57, PRE).
   - **Replacement.** "...and $k$-pool losses concentrate where no correct candidate matches the reference\ph{} (\cref{app:estimator})."
4. **A failed-instruction disclosure was trimmed out of the body** (p. 6, l. 323; `main.tex` l. 203).
   - **Problem.** The trim deleted "For small Qwen2.5 judges an earlier test found no reduction". Now only the Table 1 caption mentions that failure. Meanwhile the abstract, intro and Conclusion say the instruction "reduces" the effect.
   - **Source.** Appendix F: the instruction "leaves smaller judges unmoved or worse". Ledger, Synthetic grid row: "split: Qwen2.5-14B confirmed; Qwen2.5-1.5B, 3B, and 7B falsified".
   - **Fix.** B3 frees the space. After "(\cref{tab:protocols})." append: "On a synthetic arithmetic grid the same sentence left Qwen2.5 judges up to 7B unmoved or worse (\cref{app:mitigation})."
5. **The abstract's benchmark sentences are hard to parse and slightly overstated** (p. 1, l. 023-026; `main.tex` l. 49-50).
   - **Problems.** "Opus 5 shown a reference score four models" reads as a garden path. "Unchanged" overstates: the pooled change is +1.0 and −1.8 for these two graders (`r22b` `draw2_minus_draw1`).
   - **Replacement.** "On up to 149 factual benchmark questions, Claude Sonnet~5 and Opus~5, when shown a reference, score four models 7 to 40 points below their answer-list accuracy, and within 3 points of it when grading blind. Redrawing the reference leaves this shortfall about the same but moves credit for answers whose match changes by 23 to 38 points, against about 3 when the same reference is re-graded."
6. **Optional: "establishes" in the intro is stronger than the body** (p. 2, l. 091-092; `main.tex` l. 90).
   - **Problem.** The Section 6 Verdict says "holds", with two judges tested only at a post hoc threshold. The Limitations add "No experiment manipulates verification directly".
   - **Replacement.** "All three predictions hold; P3 indicates an agreement component beyond verification failure for all six judges with a usable acceptance test, ..."
7. **Optional: appendix whitespace.** Pp. 29, 31, 36 and 38 are half blank. `[!ht]` on those floats would recover space. This is cosmetic.

## (d) Numbers checked (46)

| # | Main-text claim (location) | Source | Result |
|---|---|---|---|
| 1 | Abstract "3 to 5 points"; Table 1 "2.7-5.4"; §4 5.25, 4.09, 3.04, 5.41, 3.92, 2.66 | `tables/r4_rotation.tex`, `tables/rotation_exact.tex`, `replrot_results.json` | match |
| 2 | Fig. 1c +0.12/+0.30/+0.04; 120/93/113 tasks | same tables | match |
| 3 | Abstract and Table 1 "7 to 40" (Sonnet 5, Opus 5) | `r20c_leaderboard` and `r21a_leaderboard_opus` `undercount_referenced_minus_list`: min −7.1 (Opus 5 on Opus 5), max −39.6 (Sonnet 5 on Haiku 4.5) | match |
| 4 | "within 3 points blind" | `blind_minus_list`: Sonnet 5 −0.7 to −2.7; Opus 5 −0.7 to +1.4 | match (but see SF1) |
| 5 | Table 1 "10-33 with a second draw" | `r22b_redraw_{sonnet,opus}` `draw2_minus_list`: −9.6 to −32.9 | match |
| 6 | Abstract, Table 1 and §7 "23 to 38"; "lose 25 to 38", "gain 23 to 35" | `r22b` losers −38.2/−27.1/−25.0; gainers +35.1/+23.2/+29.3 | match |
| 7 | "about 3" on a regrade | `r23a` stop 100→99.3, 99.3→99.3, 99.3→98.6; start 64.4→65.5, 77.6→74.5, 68.4→69.0 (max 3.1) | match |
| 8 | §7 "16 to 22 points pooled"; Haiku 4.5 "by 9 even blind" | −22.3, −15.6, −20.1; −9.2 (Table 47) | match |
| 9 | §7 redraw "moves each pooled shortfall by about 3 points at most" | +1.0, −1.8 (136 questions), +3.0 | match |
| 10 | §7 gap "within 1 point", "7 to 9", "10.7 points each" | `r23a` `haiku_minus_llama`: same-draw 0.0/−0.7/+10.7; between-draw +7.4/+8.9/+10.7 | match |
| 11 | §7 "All 27 registered predictions" | R20-C 3 + R21-A 9 + R22-B 9 + R23-A 9 = 30 | **error (B1)** |
| 12 | Max rule "within 0.03 of blind on the k-pool and MACE" | `r16c` (max −0.030); `r20g` (−0.027, −0.023, −0.015, −0.008) | match; mark missing (SF2) |
| 13 | Max rule "within 2 points ... for all three graders (5 points for one model)" | `r20g` −1.0; `r21a_maxrule` +0.5, −1.7; Haiku 4.5 grading itself −5.4 | match |
| 14 | "For Haiku 4.5 ... closer to the lists than blind" | blind −9.2 vs max rule −1.7 | match |
| 15 | "up to 6.7 pp of accuracy and 0.15 of AUROC (paired)" | `r16c` math500/ref `max_rule_minus_reference` −0.0667, −0.1545 | match |
| 16 | Table 2: all 44 numeric cells and the bold marks | `r16c`, `r20g`, Table 16 top block (Reveal minus Reference) | match; registration labels wrong (B2) |
| 17 | §6 "36 to 18 pp for Sonnet 5 and to 8 pp for Opus 5" | `r20g` FR 35.6→18.1; 36.3→8.1 | match |
| 18 | §6 and §7 "grading stays below blind" with the sentence | `r20g` −0.065 [−0.115, −0.019]; −0.053 [−0.105, −0.004] | match |
| 19 | Table 1 "halves ... or more" | as #17 (51% and 78% reductions) | match |
| 20 | Table 1 P2 and §5 "0.06-0.16" on MACE | −0.153, −0.165 (`r20g`); −0.080, −0.060 (`r16c`) | match |
| 21 | "0.17-0.27"; model-read "0.16-0.25"; boxed "0.07-0.14" | `tables/labelings_gnm.tex` | match |
| 22 | §5 Verdict API judges "0.06 to 0.08", "0.04 and 0.02"; GPT-4.1 "at most 0.04" | `r20g` −0.080/−0.057, −0.037/−0.015 [−0.039, +0.009]; `labelings_gnm` −0.04/−0.01 | match |
| 23 | §5 Verdict "+2.0 and +6.1 pp, intervals including zero" | `r16c` `accuracy_kgt1` 0.0202 [−0.05, 0.09], 0.0606 [−0.01, 0.13]; `r3_mace_accuracy` (original scorer) identical | match |
| 24 | §5 "28% ... against 0.4% blind" | `tables/main_numbers.tex` 28.1%/0.4% | match |
| 25 | P2′ "29-31 pp"; §5 "28.6 and 30.6" | `r16c` math500 `refans` 0.2857, 0.3064 | match |
| 26 | §5 MACE single-answer "29.4† and 26.5" | `main_numbers.tex` +29.4 (exact scorer); `mace_accuracy.tex` +26.5 | match |
| 27 | Table 1 P3 "2 of 843, against 117" | `r20a` pooled: 318+525; 0+2; 41+76 | match |
| 28 | §6 "2 of the 282 ... against 78" | `r20a` mace: 81+201; 0+2; 15+63 | match |
| 29 | §6 "between 19% and 83%"; Fig. 3a 42% | `r20a` 0.1852, 0.3134; `r21a_mace_acceptance` 0.833, 0.4194 | match |
| 30 | §6 Opus 5 "5% or less on both pools"; phi-4 "5%" and "15%" | `r20a` 4.74%, 2.65%; Table 52 top bins 5 (n = 1741), 15 (n = 646) | match |
| 31 | Table 1 "at most 0.4% of those that match" | Table 44: replication Qwen2.5-7B 0.4% | match |
| 32 | §6 MT-Bench template "3.59" | `tables/r2b.tex` −3.591 | match |
| 33 | §6 thinking "2.85 to 0.32"; "1.98 to 0.12" | App. L CLI arms; `tables/r4_toggle.tex` | match |
| 34 | Fig. 3b +36/+15, +44/+22, +42/+18; "about halves" | Table 56 / `r19b`: 35.6/14.9, 44.3/21.6, 41.6/17.8 | match |
| 35 | §3 "38% to 43% of replies ignore the format" | `labelings_numbers.tex`: boxed 61.6% and 57.1% | match |
| 36 | §3 91%, 86%, 90% predicted, 95%; Limitations "14%" | `r22a_label_audit.json` 0.9107, 0.8624, P-R22A2 falsified, 0.9472 | match |
| 37 | Intro "0% to 2.5%" and "30% of NQ-open" | `prevalence_results.json` 0.0/0.025/0.025; nqopen 0.30 | match |
| 38 | §3 MACE lists "miss 2.3% and 8.1%" | App. D | match |
| 39 | §4 MathConstraint "3 to 5 points" | App. O +3.46 to +5.01 | match |
| 40 | §3 "206 ... 138, 11, 17, 17, 23" | App. B text: 138 + 11 + 17 + 17 + 18 + 2 + 3 = 206 | match |
| 41 | Limitations "6.7 points" regrade; "141 and 136 of 149" | `r23a_regrade_haiku` Haiku 4.5 grading itself +0.0671; `r21a_leaderboard_opus` 141; `r22b_redraw_opus` 136 | match |
| 42 | Fig. 4 caption "141 questions (136 for hollow markers)" | as #41 | match |
| 43 | Abstract "ten judges" | the ten main-text judges, Qwen2.5-7B/14B, phi-4, gemma-2-9b, Sonnet 5, Opus 5, GPT-4.1, Qwen3-8B/14B and Haiku 4.5 (the appendix adds Mistral-7B and others) | match |
| 44 | Fig. 2 title "clearly lowers selection accuracy only for Qwen2.5-7B" | Table 26: only Qwen2.5-7B k-pool excludes zero; phi-4 reaches 0.0 | match |
| 45 | "blind-then-reveal left grading below blind for most open judges" | Table 16 top: 5 of 6 below zero (Qwen2.5-14B −0.01 [−0.02, 0.00]) | match |
| 46 | Figure fonts at print size | matplotlib `Tf` sizes × included-width scale; Fig. 1 from pdftohtml (11 units / 1.5) | all ≥ 7 pt |

**Registration marks otherwise verified against the ledger and the table marks.**
- Table 1 and Section 4: ‡ on Qwen2.5-7B's exact-scorer swap.
- Section 5: † on the P2 ranges; 29.4† and 26.5 unmarked.
- Section 6: † on 19-83%, on the binned result and on 15%.
- Figure 2 and Figure 3 registration sentences; Figure 4 "except Sonnet 5's max rule".
- Section 7 regrade and gap readouts unmarked (registered R22-B and R23-A readouts).

The only mark problems are B2, SF2 and SF3.
