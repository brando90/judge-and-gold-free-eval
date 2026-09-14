# Final check 2: "The Reference Is Not an Answer Key"

**Target: commit a74d6cf.** It is ff3f9ef plus two follow-up commits sent by the coordinator mid-review:
- **8549b11**, four wording edits;
- **a74d6cf**, the abstract's P3 clause.

The committed PDF matches the working-tree PDF, and `main.tex` and `appendix.tex` match HEAD. The PDF has 51 pages, and `pdfinfo` Title and Author are empty.

**What I read.**
- `final_review.md`, and the diffs `a73ab91..ff3f9ef`, `ff3f9ef..8549b11` and `8549b11..a74d6cf`.
- All of `main.tex`, plus these parts of `appendix.tex`: B (ledger), F (mitigations) and G (labelings).
- `tables/labelings_{gnm,fr,acc,numbers}.tex` and `tables/score_rules.tex`.
- These JSON files and scripts:
  - Labels: `r8_lenient_results.json` (unrounded labeling values).
  - Score rules: `r7_posthoc.py` (the RULES dict).
  - Grid instruction: `synthk_results.json`, `synthk_refinst2.json`, and the P-S2 entries in `supplement/preregistration/registration_ledger.md`.
  - Benchmark: `r20c_leaderboard.json`, `r21a_leaderboard_{opus,haiku}.json`, `r22b_redraw_*.json`, `r23a_regrade_*.json`.
  - Prompts: `frontier_api_judge.py`, `sonnet_api_pool.py`, `bon_judge.py`.
- `main.log`.
- Page images (pdftoppm) of pp. 1-10, 26 and 27. Pages 7-9 were re-rendered from the 8549b11 build. For a74d6cf, `pdftotext` confirms that Figure 1 is still on p. 1 and that the Conclusion, Table 2, Table 16 and Table 17 are on the same pages.

**Conventions.** Line numbers are PDF margin numbers; `main.tex` line numbers are also given. Nothing in the project was modified except this file.

---

## BLOCKERS

### B1. The Section 3 labeling sentence claims more than the data show
- **Location.** p. 4, l. 189-191 (`main.tex` l. 153).
- **Quoted text.** "Registered, any-format, and model-read labels and boxed replies alone agree on the direction of every grading result of the core judges; the labeling changes the size of an effect, not its sign, and boxed replies give the smallest estimates."

**Problem 1: the claim covers two judges that were never run under the other labelings.**
- Section 3 (p. 4, l. 174-176) defines the core judges as the four open judges, Sonnet 5, Opus 5 and GPT-4.1.
- Sonnet 5 and Opus 5 were scored under any-format labels only:
  - `r8_lenient_results.json` has registered, any-format, model-read and boxed-only values only for Qwen2.5-7B, phi-4, Qwen2.5-14B, gemma-2-9b, Mistral-7B and GPT-4.1.
  - `make_figures.py` l. 763-764 draws the boxed-only ticks only for the open judges and GPT-4.1, and Figure 2 has no ticks on the Sonnet 5 or Opus 5 rows.
- So the sentence claims agreement across four labelings for two judges that have one.

**Problem 2: "the labeling changes the size of an effect, not its sign" is false for selection accuracy.** Selection results belong to the same judges.

| Selection accuracy (`tab:labelings-acc`) | Registered | Boxed only |
|---|---|---|
| Qwen2.5-7B, *k*-pool *k*>1 | −35.9 | +4.0 |
| Qwen2.5-14B, *k*-pool *k*>1 | −23.1 | +4.0 |
| gemma-2-9b, *k*-pool *k*>1 | −15.4 | +8.0 |
| Qwen2.5-7B, replication pool | −4.8 | +3.9 |
| GPT-4.1, *k*-pool *k*>1 | −1.6 | +12.5 [+3.3, +24.3] (interval excludes zero) |

Appendix G says so itself: "The selection loss at *k*>1 does not survive in the same way".

**Problem 3: false rejections cannot be counted in "every grading result".** GPT-4.1's *k*-pool model-read change is +0.0004 [−0.036, +0.039], which the table prints as +0.0. Boxed-only is also not the smallest false-rejection estimate: for Qwen2.5-7B on the replication pool it is +28.3, against +27.0 any-format.

**What does hold.** For grading AUROC, all four labelings are negative for every open judge and for GPT-4.1, so registered versus boxed-only agrees too. For example, Qwen2.5-7B on the replication pool is −0.29 registered and −0.10 boxed-only; GPT-4.1 on the *k*-pool is −0.04 and −0.01. Boxed-only gives the smallest fall for every open judge. GPT-4.1 on the *k*-pool ties at the printed precision (−0.0143 boxed, −0.0129 model-read, −0.0147 any-format).

**Replacement.** Same length, so the layout should not change:
> "For the open judges and GPT-4.1, registered, any-format, and model-read labels and boxed replies alone agree on the sign of every grading AUROC change, with boxed replies giving the smallest falls; selection-accuracy losses are less robust to the labeling (\cref{app:grid})."

The Section 5 sentence "the direction holds under every labeling, and only the magnitude changes" (p. 5, l. 257-259) is about the open judges' AUROC and is correct as written.

---

## SHOULD FIX

**S1. The synthetic-grid clause overstates "unmoved" for 7B.**
- **Location.** p. 6, l. 322-323 (`main.tex` l. 203); the same wording is in `appendix.tex` l. 285.
- **Quoted text.** "the same instruction left Qwen2.5 judges up to 7B unmoved or worse".
- **What is correct.**
  - It is the same instruction: `frontier_api_judge.py` l. 131-133 copies the `refinst` sentence verbatim from `bon_judge.py`.
  - The ledger does cover 1.5B, 3B and 7B. The Synthetic grid row reads "Qwen2.5-1.5B, 3B, and 7B falsified", and `registration_ledger.md` P-S2 gives the *k* = 16 rubric-*a* margins: 1.5B +3.58 → +4.54, 3B +7.91 → +7.75, and 7B +5.01 → +4.54 ("marginal").
- **What is wrong.** In `synthk_results.json`, rubric *b*, the instruction lowers 7B's margin at every *k*:
  - +5.66 → +4.67, +6.16 → +4.80, +5.95 → +4.76 and +6.20 → +4.88, a fall of about 20%.
  - At *k* = 8 the intervals do not overlap: [5.44, 6.72] against [4.26, 5.48].
- **Also.** The 1.5B "worse" result holds only on rubric *a*; rubric *b* improves, +2.52 → +2.12.
- **Replacement** (same length): "On a synthetic arithmetic grid the same instruction did little or nothing for Qwen2.5 judges up to 7B (\cref{app:mitigation})."
- **Optional appendix edit** (l. 285): "leaves smaller judges unmoved or worse" → "does little or nothing for smaller judges".

**S2. The P3 wording in the Verdict and the abstract is categorical, while the intro and Section 6 are hedged.**
- **Locations.**
  - Section 6 Verdict, p. 7, l. 354-356 (`main.tex` l. 208): "The effect therefore cannot be explained solely by verification failure, although blind acceptance is a proxy for verification, not a direct test of it."
  - Abstract, p. 1, l. 020 (`main.tex` l. 48), after a74d6cf: "so verification failure alone cannot explain the effect".
- **Consistency.**
  - The two now match each other.
  - Both say "cannot", which is stronger than the intro ("P3 indicates an agreement component") and Section 6 ("consistent with an agreement component").
  - In the Verdict, the "although ... proxy" clause undercuts "cannot"; the abstract has no hedge at all.
  - A reviewer who reads the Limitations ("No experiment manipulates verification directly") may call "cannot" an overclaim.
  - The old wording "not only a failure to verify" was about as strong, so this is not a blocker.
- **Replacements.** Both keep the two sentences matched.
  - Verdict: "The effect therefore does not appear to be explained by verification failure alone, although blind acceptance is a proxy for verification, not a direct test of it."
  - Abstract: "so verification failure alone does not appear to explain the effect".
- **Caution.** The abstract version adds two words. Recompile and confirm Figure 1 (`[!b]`) stays on p. 1.

**S3. The new "Judges and prompts" limitation misdescribes the full-credit arm.**
- **Location.** p. 9, l. 450-452 (`main.tex` l. 276).
- **Quoted text.** "The MT-Bench template and the full-credit instruction show that the effect is not specific to our ``trusted'' wording".
- **Problem.** Only the MT-Bench template drops "trusted". The full-credit arm still shows "Reference answer (trusted):" (`frontier_api_judge.py` l. 140; `sonnet_api_pool.py` l. 70) and appends the sentence to the system prompt (`sonnet_api_pool.py` l. 76-77).
- **Replacement.** "The MT-Bench template, which drops ``trusted'', and the full-credit instruction show that the effect survives two changes to our wording, but they do not exhaust reference prompts."
- **Fit.** Page 9 has about 3 free lines.

**S4. "Five simple score combinations" counts the plain reference as a combination.**
- **Location.** p. 7, l. 375-376 (`main.tex` l. 253); p. 9, l. 453-454 (`main.tex` l. 277).
- **Problem.**
  - `tab:score-rules` has five zero-cost rows (Reference, Mean, Min, Max, and Blind with reference tie-break) plus Blind-then-reveal. The `RULES` dict in `r7_posthoc.py` adds the blind baseline.
  - Only four of the five rows actually combine the two scores. "Five" is right only if the referenced score alone counts as a rule.
- **Replacements.**
  - l. 253: "chosen post hoc from five zero-cost score rules".
  - l. 277: "chosen post hoc from five zero-cost score rules".

**S5 (optional). "Verification difficulty explains part of the effect" is causal wording for a binned correlation.**
- **Location.** p. 6, l. 314-316 (`main.tex` l. 200).
- **Replacement.** "verification difficulty may explain part of the effect".

**S6 (optional). Table 1's P3 row paraphrases the new heading.**
- **Location.** p. 3, l. 127-130 (`main.tex` l. 112).
- **Current.** "The effect persists on answers the judge accepts without a reference".
- **Option.** Use "The effect persists after blind acceptance" to match the intro list and the Section 6 title. The meaning is already the same.

**S7 (optional). The appendix Table 16 title says "removes".**
- **Location.** `appendix.tex` l. 316.
- **Quoted text.** "The max rule removes the grading harm".
- **Problem.** Qwen2.5-14B's max-rule AUROC interval excludes zero: −0.02 [−0.04, −0.01] in Table 16 and −0.03 [−0.05, −0.01] in Table 17.
- **Replacement.** "The max rule nearly removes the grading harm".

**S8 (optional). The Limitations question counts leave out the regrade.**
- **Location.** p. 9, l. 441-442.
- **Problem.** "(141 and 136 of 149 remain)" omits the Opus 5 regrade readout, which uses 135 questions (`r23a_regrade_opus.json`).

---

## VERIFIED CLEAN

### Items from final_review.md
- **B1.** ff3f9ef corrected the count to 30, which matches the ledger: 3 + 9 + 9 + 9. 8549b11 then deleted the sentence on purpose, and nothing else refers to it.
- **B2.** The Table 2 caption now reads as recommended.
  - The API judges' Reference and Sentence values are registered: ledger rows "Sonnet 5 with wrong answers", "Opus 5 on the Sonnet 5 subsamples" and "Full-credit sentence, measured by grading".
  - Every Reveal − ref. and Max rule cell is labeled post hoc, consistent with Table 16 (†), Section 7 and the Limitations.
- **B3.** `\FloatBarrier` is gone and Table 2 is `[t]`.
  - Table 2 sits at the top of p. 8, and Related work fills the page.
  - p. 8 ends with about 3 blank lines, and p. 9 ends at l. 482.
  - There are no large blank areas on pp. 1-9.
- **B5.**
  - Table 16 (p. 26) now fits on its own page, well clear of the page number.
  - Table 17 (p. 27) is at the top of its page.
  - `main.log` has no "Float too large" warning.
- **SF1-SF6** are all applied:
  - Figure 4 title;
  - † marks in "What helps";
  - † placement in the Section 5 Verdict;
  - grid disclosure (but see S1);
  - abstract benchmark sentences;
  - "indicates" in the intro.

### The coordinator's five edits (8549b11 and a74d6cf)
1. **Conclusion.** "When a question has several correct answers, ..." reads correctly; "swapping it" now refers to "the one they are shown".
2. **Verdict.** It now matches the abstract wording; see S2 for its strength.
3. **Section 7.** All numbers match:
   - "16 to 22 points pooled": referenced minus list is −22.3 (Sonnet 5), −15.6 (Opus 5, 141 questions) and −20.1 (Haiku 4.5).
   - "Blind, Sonnet 5 and Opus 5 stay within 3 points": Sonnet 5 is −0.7 to −2.7 per model (pooled −1.7); Opus 5 is −0.7 to +1.4 (pooled +0.4).
   - "Haiku 4.5 already under-counts by 9 points blind": pooled −9.2.
4. **Deleted prediction count.** The paragraph still makes sense without it, and the Figure 4 caption ("Pre-specified, except Sonnet 5's max rule") still carries the registration status.
5. **Abstract P3 clause (a74d6cf).**
   - It is grammatical and matches the Verdict (see S2).
   - It did not change the layout: Figure 1 is on p. 1, and the Conclusion, Table 2 and Tables 16-17 are on the same pages.
   - `main.log` is still clean.

### Calibration edits
- **P3 heading.** "The effect persists after blind acceptance" appears in the intro list (l. 088) and the Section 6 title (l. 301). Table 1 paraphrases it (S6). The Verdict says "P3 holds", which is consistent.
- **Intro.** "P3 indicates an agreement component" is present.
- **Section 6.** "Consistent with an agreement component" and "blind acceptance is a proxy for verification, not a direct test of it" both agree with Limitations ("No experiment manipulates verification directly").
- **"Partly by construction."** This is correct: max(b, s) ≥ b for every candidate, but wrong answers can rise too, so the AUROC result is not fully guaranteed.
- **"The aggregate shortfall does not hinge on the draw."** Pooled second-draw minus first-draw is +1.0 [−3.9, +5.9], −1.8 [−6.6, +2.9] and +3.0 [−1.3, +7.4]. The sentence rests on two draws, which the Limitations disclose.
- **Open-ended-tasks limitation.** This sentence is accurate. The "trusted" sentence is covered by S3.
- **Ethics statement.** It matches the ledger's "Training, runs 1-3" row: the reference arm's copy rate fell (falsified), and a pre-adopted stopping rule closed the questions as unresolved. "Inconclusive and did not show a policy learning to copy the reference" is therefore accurate.
- **Max rule.** It is called exploratory and post hoc everywhere. Only the Opus 5 and Haiku 4.5 benchmark readouts are described as registered (ledger "Two more benchmark graders"). It is absent from the abstract and the Conclusion.

### Overclaim search of main.tex
- "proves", "safe" and "fix" do not appear.
- "Mechanism" appears only as the Limitations heading.
- "Separates" appears only in the Section 2 model logic ("P2 separates them from the answer key").
- The abstract's "We separate three readings" is acceptable; "distinguish" would be slightly safer.
- Reward-signal claims are cited (intro l. 076, Related work) or hedged (Ethics).
- The only remaining categorical P3 wording is "cannot" (S2).

### Layout
- Figure 1 is on p. 1.
- The Conclusion ends on p. 9 at l. 469.
- Ethics starts on p. 10.
- `main.log` has no overfull boxes, no "Float too large" and no undefined references. It has one underfull `\vbox` on p. 1 (badness 2600) and two hyperref "Token not allowed in a PDF string" warnings from math in an appendix section title; all three are harmless.

### Numbers in changed sentences

| Claim | Source | Result |
|---|---|---|
| Abstract and Conclusion "7 to 40" | `r20c`, `r21a_opus` `undercount_referenced_minus_list`: −7.1 to −39.6 | match |
| Abstract "within 3 points of it when grading blind"; Figure 4 title | `blind_minus_list`: Sonnet 5 −0.7 to −2.7; Opus 5 −0.7 to +1.4 | match |
| Abstract and Conclusion "about the same" | `r22b` pooled `draw2_minus_draw1`: +1.0, −1.8 | match |
| "23 to 38"; Section 7 "25 to 38" and "23 to 35" | `r22b` losers −38.2/−27.1/−25.0; gainers +35.1/+23.2/+29.3 | match |
| "about 3" on a regrade | `r23a` stop 100→99.3, 99.3→99.3, 99.3→98.6; start 64.4→65.5, 77.6→74.5, 68.4→69.0 (largest 3.1) | match |
| Section 7 "16 to 22", "within 3", "9 points blind" | see edit 3 above | match |
| Section 7 "about 3 points at most" | +1.0, −1.8, +3.0 | match |
| Section 7 "within 1 point", "7 to 9", "10.7 points each" | `haiku_minus_llama` same-draw 0.0/−0.7/+10.7; between-draw +7.4/+8.9/+10.7 | match |
| Section 6 grid clause | `synthk_results.json`, `registration_ledger.md` P-S2 | 7B overstated (S1) |
| "five simple score combinations" | `tab:score-rules`, `RULES` in `r7_posthoc.py` | wording (S4) |
| Section 3 labeling sentence | `r8_lenient_results.json`, `tab:labelings-*` | **B1** |
| Table 2 caption registration labels | ledger rows cited above | match |

**Verdict: Not ready. Fix B1 (a one-sentence replacement in Section 3) and rebuild; it is then ready to submit, ideally with S1-S4 (a few one-line edits) applied in the same rebuild.**
