# Round 13 Area-Chair Review: "The Reference Is Not an Answer Key: LLM Judges Favor the Correct Answer They Are Shown"

Reviewed from `round13_main.pdf` only (40 pages: main text pp. 1-9, references pp. 9-11, appendix pp. 12-40). Line numbers are the PDF's margin numbers.

---

## 1. Summary of the claims

LLM judges are often given a "trusted" reference answer. The paper asks what happens when a question has several correct answers. The core experiment is a swap test. The same candidate text is re-judged with the reference moved from one correct answer to another. The score moves by about 3-5 points out of 10: +5.3/-5.4 for Qwen2.5-7B, +4.1/-3.9 for phi-4, +3.0/-2.7 for Sonnet 5. So the reference acts like a literal match target, not an answer key (P1).

Consequences for grading (P2):
- With several correct answers, correct answers that differ from the reference become harder to separate from wrong ones. Grading AUROC falls by 0.07-0.33 for four open judges and by 0.04-0.15 for Sonnet 5.
- With one correct answer, the reference helps: about +30 pp best-of-64 accuracy on MATH-500.

Mechanism (P3):
- Reasoning before scoring nearly removes the effect on arithmetic, but not on factual MACE questions.
- Sonnet 5 still anchors on factual answers it ranks above a wrong one 94% of the time blind.
- Rewriting the reference as "30+1" largely removes the effect.
- The paper concludes that verification failure and "agreement" both operate, and that judges match a literal answer.

Consequences for selection (Section 7): accuracy is not lost on natural multi-answer questions, and is lost on constructed pools mainly when no correct candidate matches the reference. A 156-prediction registration ledger is reported.

**Was this easy to extract?** The P1 claim is: it is on page 1, stated well, and Figure 1b-c shows it at a glance. Everything after Section 4 was hard to extract. I had to read the appendix to learn which scorer, which labeling, and which subsample stood behind each number, and in several places the answer contradicts the main text (see Must-fix 1, 3, 5). That difficulty is itself the main finding of this review.

---

## 2. Score and confidence

**Score: 5 / 10 (marginally below the acceptance threshold). Confidence: 4 / 5.**

**Biggest reason.** The swap test is a clean, important, well-controlled result that could anchor a strong paper. But the main text wraps it in a mechanism story (Section 6, Figure 1d, the abstract's "verification failure explains part of this") that the paper's own verification measure does not support. It also wraps it in a consequences-and-mitigations story (Section 7, Conclusion) whose numbers switch between answer labelings from claim to claim. In one case this directly contradicts the Limitations section. A reader cannot tell which main-text claims are reliable without auditing 50 appendix tables. The bar here is the Mirage paper: one question, one measurement convention, every claim traceable. This draft is not there, although all the fixes below can be made without new experiments.

---

## 3. Ranked issues

### MUST FIX (would mislead a reader or block acceptance)

#### M1. The Conclusion's mitigation claims use the labels the paper says it does not use, and one headline number is wrong

**Location:** p. 8, L411-421 (Conclusion), against L391-392 (Limitations).

**Problem 1: the labels contradict the Limitations.**
- The Limitations say: "all main-text accuracy claims on constructed pools use post hoc relabelings."
- The Conclusion says blind-then-reveal "trailed blind judging by 10 to 15 pp on the k-pool **under the registered checker**." It also says the max rule "lost up to 2.6 pp for the open judges."
- These numbers come from Tables 8 and 36, which use the registered labels and the original scorer.
- Under the paper's preferred any-format labels (Table 15), blind-then-reveal changes accuracy by +0.0, +3.0, +0.0, and -6.1 pp. The max rule changes it by +3.0, +3.0, 0.0, and +3.0 pp: a *gain* for three of four judges.
- So the negative verdict on mitigations holds only under the labeling the paper calls wrong.
- Even under registered labels, "10 to 15 pp" holds for only three of the four screened judges: Qwen2.5-14B gains +2.6 (Table 8).

**Problem 2: the recommendation contradicts itself.** The last sentence tells practitioners to "re-score it without the reference." That is essentially the max rule, which the same paragraph has just called "not a fix."

**Problem 3: a wrong number.** L413 says correct answers that differ from the reference "are scored 3 or below **up to 28%** of the time for Qwen2.5-7B and 36 pp more often for Sonnet 5."
- 28% is the replication-pool level only (Table 9).
- The rise is +35.4 pp for Qwen2.5-7B on the k-pool (Table 14), +54.4 pp for gemma-2-9b, and +63.8 pp for Qwen2.5-7B on MACE (Table 43). "Up to 28%" is false as a maximum.
- The sentence also compares a *level* (28%) with a *change* (36 pp).

**Fix.**
- Choose one labeling for every accuracy claim in the main text (any-format, as the Limitations promise). Rewrite the mitigation sentence from Table 15 and Table 25, for example: "Neither blind-then-reveal nor taking the higher of the blind and referenced scores reliably closed the gap: under answers read in any format they were within 6 pp of blind judging on the k-pool, but the max rule trailed the reference by 6.7 pp on MATH-500 for Qwen2.5-7B (Table 36)."
- Replace "up to 28% … 36 pp more often" with changes on one footing, for example: "the share of those answers scored 3 or below rises by 28 to 64 pp for Qwen2.5-7B across pools, and by 36 pp for Sonnet 5 on factual questions."
- Make the final recommendation consistent with what was measured. If re-scoring blind is the advice, say it costs up to ~7 pp on unique-answer math (Table 36) and recovers the loss on multi-answer pools.

#### M2. The mechanism verdict (P3 "splits: both mechanisms", Figure 1d, the abstract) is not supported by the paper's own verification measure

**Location:**
- Abstract L23-26 ("Verification failure explains part of this: a thinking mode cuts the effect by 89% or more on arithmetic, where judges can check answers. It does not explain all of it…").
- Intro L67-69.
- Table 1, P3a row.
- Section 6 L314-317 (verdict).
- Figure 1d and its caption.

**Problem.** The paper defines v_c as "how reliably the judge can check c without a reference" (L140). It measures this as blind AUROC (P3b, L296-298; Table 50). By that measure:

*(a) Thinking does not raise verification on arithmetic.*
- Table 50: Qwen3-14B blind AUROC on arithmetic is 0.85 with thinking off and 0.86 with it on. Qwen3-8B is 0.86 in both.
- Yet thinking removes the swap effect.
- So the thinking contrast is *not* a manipulation of verification as the paper operationalizes it.
- The arithmetic-vs-factual gap in blind AUROC with thinking on is only 0.86 vs 0.81, while false rejections differ by 0 vs about 20 pp.

*(b) The thinking judges verify arithmetic no better than the score-only judge that anchors hardest.* Their blind AUROC is 0.86. Qwen2.5-7B's blind AUROC on the replication pool is 0.87 (Table 48), and Qwen2.5-7B swaps by about 5.4 points. Placing marker "2" at the far right of Figure 1d's x-axis ("how well the judge can check the answer") therefore contradicts the paper's own data.

*(c) The paper's evidence also supports "agreement" for the open judges, but that is never said in the main text.*
- In the top tercile of tasks, where Qwen2.5-7B's blind AUROC is 0.98, it still swaps by 3.6 points (L297-298).
- Among answers it scored at least 9 blind, it swaps by +5.32 (Table 49).
- Appendix N says as much: "does not remove it where the judge already separates correct from wrong answers almost perfectly." The main text uses these numbers only as P3b support.
- Table 1 says P3a is "yes" only for Sonnet 5.
- The treatment is inconsistent: ranking correct above wrong 94% of the time counts as "verifies" for Sonnet 5, but a blind AUROC of 0.98 does not count for Qwen2.5-7B.

*(d) The "agreement" side rests on thin evidence.*
- It uses 40 MACE questions, one sample per kind of answer, collected through the CLI.
- CLI and API scores agree on only 67% of calls (L171).
- The paired thinking-vs-no-thinking difference is -0.95 [-2.45, +0.63], which is compatible with up to a ~60% reduction.

*(e) The rival "one intended answer" reading is tested on the wrong domain, and selectively.*
- The "30+1" test (L285-294) is run on the arithmetic replication pool. But the evidence it is meant to protect (Sonnet 5 anchoring on verified answers) is from factual MACE questions, where an expression rewrite is impossible.
- Score-only judges emit the score token with no reasoning, so a failure to anchor on "30+1" is also what you would expect from a judge that cannot evaluate the expression in one forward pass. The test does not separate the readings for the 7B judge.
- The paragraph reports phi-4's number-words result (+3.68 vs +3.79) but omits Qwen2.5-7B's: words cut its margin by 38% (+4.62 to +2.88, Table 28).
- The paragraph ends by conceding that "the framing of a rewritten reference may contribute," which leaves the test unresolved.

**Fix (rewriting only).**
- Reframe Section 6 as *what moderates the effect*, not *which mechanism*.
- The robust, descriptive finding is: "Reasoning before scoring removes anchoring on arithmetic but not on factual questions, **without raising blind AUROC**; score-only judges anchor even on tasks they rank near-perfectly blind (Qwen2.5-7B: 3.6 points at blind AUROC 0.98; Sonnet 5 on factual questions)."
- Set the P3a verdict to "Mixed; mechanism unresolved" and the P3b verdict to "Weak."
- Abstract: replace L23-26 with something like "Reasoning before scoring removes the effect on arithmetic but not on factual questions; judges that rank correct answers above wrong ones without a reference still anchor, so the effect is not only a failure to verify."
- Drop "explains part of this", the unsourced "89%" (see M5), and the phrase "Sonnet 5 still penalizes factual answers it ranks above wrong ones 94% of the time." That phrase reads as "penalizes 94% of the time."
- Figure 1d: remove it, or replace it with data (see Section 4).
- Report Qwen2.5-7B's words result next to phi-4's, and state plainly that the expression test was run only on arithmetic.

#### M3. Main-text labels disagree with the tables behind them

**(a) L257-258, the headline grading number.**
- The text says: "grading AUROC falls from 0.87 to 0.60 **under the registered checker**."
- Table 48 gives 0.87 to 0.60 (change -0.27 [-0.31, -0.24]). That equals Table 13's *any-format* cell, not its registered cell (-0.29 [-0.32, -0.26]).
- The phi-4 check is decisive. phi-4 scores the same under both scorers, and Table 48's phi-4 value (-0.24) matches any-format (-0.24), not registered (-0.28).
- So Table 48 uses any-format labels and the main text mislabels it. Figure 2b's caption says "any format," which contradicts L258.
- Fix: correct the label in L258 and state the labeling in Table 48's caption.

**(b) L321-323, the natural-data selection result.**
- The text says the result is "falsifying our registered prediction of a loss."
- The paper's own verdict rule (Appendix B, L724-726) makes an interval that includes zero "not confirmed," and the ledger (Table 3, "MACE end to end") records "not confirmed, both judges."
- The mark is also † although the prediction was registered.
- Fix: "the registered prediction of a loss was not confirmed" and use PRE.

**(c) Scorers mixed within one argument.**
- L251: "+32.4" for Qwen2.5-7B on MACE k=1 uses the original scorer (Table 23/44).
- L322: "+2.0 [-5.1, +10.1]" uses the exact scorer (Table 49). Table 44 gives the original-scorer interval as [-5.1, +9.1].
- Table 49 claims to collect exact-scorer "numbers quoted in the main text," but lists +29.4 for k=1, which the main text never quotes.
- Fix: one scorer (exact) throughout the main text, with a footnote.

**(d) MATH-500 accuracy appears with different values in different tables.**

| Table | Qwen2.5-7B (blind → with reference) | Qwen2.5-14B (blind → with reference) |
|---|---|---|
| Table 21 | 67.6 → 98.1 | 67.6 → 95.2 |
| Table 35 | 67.6 → 98.1 | 67.6 → 95.2 |
| Table 47 ("exact estimator") | 68.6 → 99.1 | 66.7 → 95.2 |

- Appendix O says only Qwen2.5-7B was rescored with the exact scorer on MATH-500, so the different 14B blind value (66.7 vs 67.6) is unexplained.
- Figure 2a does not say which table it plots.
- Fix: one source table, with the scorer stated in the Figure 2 caption.

**(e) Replication-pool accuracy for Qwen2.5-7B is reported three ways without cross-reference.**
- Table 9: 76.2 → 68.6, -7.6.
- Table 46 footer: 77.1 → 72.4, -4.8.
- Table 12: -4.8 registered, -9.3 any format.
- Fix: consolidate.

#### M4. The judge inclusion rule is applied selectively (Sonnet 5 counts, GPT-4.1 does not, at the same effect size)

**Location:** L172-174, L264-265; abstract L21-22.

**Problem.**
- GPT-4.1 is excluded from summaries because "scores tie too often to rank candidates."
- The screen exists for *selection* (ties at the maximum). But AUROC handles ties.
- GPT-4.1's grading AUROC change on the replication pool is -0.04 [-0.05, -0.02] (Table 13; any format -0.04 [-0.06, -0.02]). Its interval excludes zero, and it is the same size as Sonnet 5's -0.04, which the abstract counts as evidence.
- GPT-4.1's false rejections also rise by +5.8 to +6.4 pp.
- Sonnet 5's tool-call scores are integers that also tie; that is why its inflation "was not run" (Table 24).
- L264 calls GPT-4.1's result "small and not robust." That is a double standard.

**Fix.** Apply one rule: the screen gates *selection* claims only, and grading AUROC is reported for every judge. Then say "grading worsens for all four screened open judges and both frontier judges (Sonnet 5: -0.04 to -0.15; GPT-4.1: -0.04 on the replication pool)." This makes the paper stronger, and it partly answers the Limitations point that only one frontier family was tested.

#### M5. Main-text numbers with no source in the appendix

Table 49's caption promises that it "collects the exact-scorer and post hoc numbers quoted in the main text that appear in no other table." These do not appear there or anywhere else I could find:

- L353-355: "on k-pool tasks without one, Qwen2.5-7B loses 64 pp (11 tasks) and phi-4 45 pp, against -14 and 0 where one exists, and on the replication pool Qwen2.5-7B loses 31 pp without one and 5 pp with one." This sentence carries Section 7's main claim, and the abstract's "selection loses accuracy mainly when no correct candidate matches the reference" rests on it.
- L279-282: "On its API subsamples (38 tasks) … 35% at 3 or below … of the 81 it had scored a full 10, 19% (9% and 15% on the constructed pools)." Table 25 says 40 MACE tasks; "38" is unexplained.
- Abstract L23-24: "cuts the effect by 89% or more on arithmetic." The number appears nowhere in the body. I reconstructed it as (2.85-0.32)/2.85 for Sonnet 5 CLI. But that arm includes a no-thinking written rationale (-0.20), so "a thinking mode" is the wrong attribution.

**Fix.**
- Add these rows to Table 49, with intervals and labeling. In particular, the 64/45/31/5 pp values need CIs; 11 tasks is small.
- Replace "89%" in the abstract with the raw numbers ("from -2.85 to -0.32 points for Sonnet 5") and attribute it to "reasoning before scoring."

#### M6. The Section 7 title and some verdicts overclaim

- **"Consequence: grading harm, not selection harm" (L319).** Selection harm is present on constructed pools: Qwen2.5-7B loses -30.3 pp [-48.5, -12.1] under the paper's preferred labels (L352), and four screened judges lose 15-36 pp under registered labels. The abstract's "more than" is accurate; the section title is not. Retitle: "Consequence: grading harm is robust; selection harm is conditional."
- **L253: "blind accuracy at k=1 was already 79%."** That leaves 21 points of headroom, so it does not explain why the reference fails to help. Say instead that the k=1 cells are 14 tasks at or near ceiling for three judges, with intervals [+0, +0] (Table 12), so the k-pool cannot test the one-answer benefit.
- **Table 1, P2 verdict "Holds (implied by P1)" contradicts Section 2.** Section 2 (L147-149) says P2 follows only if β < 1 or γ > 0. Choose one. If P2 is implied by P1, the paper has two predictions, not three; say so.
- **Table 1, P2 "Observed" cell.** It reports only the MATH-500 one-answer benefit (29-31 points). Add "neutral on the constructed k-pool (k=1)," as L269 does.

#### M7. The model in Section 2 cannot express the "answer key" it defines

**Location:** Eq. (1), L139-151.

**Problem.**
- With β = 1 and λ = γ = 0, the reference has no effect at all.
- But the paper's answer-key reading is a reference that *helps* (P2: "with one correct answer the reference should help").
- Under Eq. (1), the only way a reference can raise MATH-500 accuracy is the match bonus λ·I[ans(c) = a*], which is exactly the non-key term.
- So the MATH-500 benefit is formally evidence *for* the non-key readings, which is not what the text argues.

**Fix.** Add a correctness term. For example, write the key as λ_key·I[ans(c) ∈ A*] for the full answer set A*, and write the non-key readings as a bonus for matching the one shown answer a*. Then the answer key predicts P2's one-answer benefit and no swap effect, and the other readings predict both.

**Also (v_c).** State in Section 2 how v_c is measured. The paper currently uses five stand-ins:
- per-task blind AUROC;
- ranking of a correct answer above a wrong one;
- a blind score of at least 7;
- thinking on vs off;
- arithmetic vs factual.

The first three are measurements; the last two are manipulations that do not move the measurements (see M2).

#### M8. Registration marks are used inconsistently

This matters because the paper leans hard on registration: the ledger is in the abstract.

- **Two conventions in one main text.** L190-193 says "Unmarked claims in the main text were pre-specified." Table 1, Figure 2's caption, and Table 4's caption use an explicit PRE mark for the same status. Fix: pick one. My recommendation is explicit PRE everywhere and never "unmarked means pre-specified," because unmarked sentences such as L276-279 then look like oversights.
- **A registered analysis marked post hoc (L282-284).** The blind-accepted filter is "registered … confirmed" (Table 3, "Blind-accepted filter (Section 6)"; Table 4 caption PRE), yet L283 marks it †. Only the Qwen2.5-7B exact-scorer value is post hoc.
- **‡ over a mixed set (L351).** "15.4 to 35.9 pp for the four screened judges.‡" The ‡ registration covers Qwen2.5-7B, 14B, gemma-2-9b, and Mistral-7B (Table 3, exact-scorer row). phi-4's -20.5 is post hoc (Table 8 †), and Mistral-7B is not a screened judge.
- **Undefined mark.** Table 48's caption ends "PRE / PH". PH is never defined; the paper's post hoc mark is †.
- **Figure 3a has no marks.** It mixes PRE cells, a ‡ cell (Qwen2.5-7B exact scorer, -5.41), and post hoc diagnostics.
- **Stale section cross-references in the ledger.** Table 3 says "Masking suite (Section 4)", but it is in Section 6. "Replication (Section 7)", "k-pool and mitigations (Section 7)", "Blind-then-reveal on MATH-500 (Section 7)", and "Reveal-call variants (Section 7)" point to material that is not in Section 7. Appendix F L1349 says "The replication in Section 7," but it is Section 4. A reviewer checking the registrations will hit dead ends.

#### M9. Terms used before they are defined, or never defined in the main text

- **Never defined in the main text:**
  - "inflation" and "SD" (L356: "best-of-64 inflation, was confirmed (+1.19 SD)").
  - "a second rubric" (L357) and "two rubrics" (L206); rubrics a and b exist only in Appendix A.
  - "rotation subsample" (Figure 3 caption L347; the main text calls the test a "swap").
- **Used before definition:**
  - "exact scorer" in the Figure 1 caption (p. 2); defined L167.
  - "margin" in Table 1 (P3a); defined L185.
  - "score-only judges" at L65 and in Table 1; defined L165.
  - "replication pool" in Figure 1; defined L157.
- **Three near-identical names for different things:**
  - "registered scorer" (L204) is the original score-readout rule.
  - "registered checker" (L178, L258) is the correctness labels.
  - "original scorer" is what the appendix calls the first of these.
  - A reader will conflate them. Fix: call the readouts the "original readout" / "exact readout", and the labels "boxed labels" / "any-format labels", and use those names everywhere.
- **Fix.** Either define "inflation" in Section 3 in one sentence, or delete the L355-358 sentence from the main text. It is self-described as "not separate evidence," so deleting it is the better option.

#### M10. Cognitive load: the main text reads as a compressed lab notebook

This is not a style preference; it is why M1-M9 were possible without anyone noticing.

- **Paragraph density.** Sections 4-7 carry about 150 numeric values in about 4 pages. Many sentences carry 4-8 numbers, each with a scorer, labeling, subsample, or interface qualifier. Examples: L203-211, L257-265, L276-284, L300-307, L350-358.
- **The abstract** contains 13 numeric ranges, including a range that spans labelings (0.07-0.33, a 5x spread driven by the "boxed only" subset) and a 156-prediction ledger count. The ledger count invites a forking-paths reading (L190: "we do not correct for multiplicity").
- **Too many concepts** for one argument: three readings plus a "fourth reading" plus "matching a literal answer."
- **Fix.**
  - Fix one primary labeling (any format) and one primary scorer (exact) for the main text. Move every alternative to a single robustness table (Appendix D).
  - Limit each paragraph to the 2-3 numbers that carry its claim.
  - Move the ledger count from the abstract to the end of the Introduction ("All 156 registered predictions and their outcomes are in Appendix B; 25 were not confirmed or were falsified").
  - Fold the "fourth reading" into Section 2 as a named alternative, or cut it to one sentence plus an appendix pointer.

---

### POLISH

**P1.** Stated effect ranges are inconsistent.
- Abstract: "2.7 to 5.4."
- L37: "a typical swap moves about 5 points" (true for Qwen2.5-7B only; Sonnet 5 is 3).
- L65: "3 to 5 points" for "every score-only judge we swapped," yet L207 reports up to 9.8 for Qwen2.5-1.5B.
- Table 1: "+3.0 to +5.3."
- Fix: state "2.7 to 5.4 points on the replication pool (up to 9.8 for 1.5B-3B judges on an exploratory pool)" once, and reuse it.

**P2.** Prevalence at L49: "18.5% of NQ-open questions." Table 20 says 30.0%; 18.5% excludes answers that changed over time. Give both.

**P3.** Pool size at L159-160: "which passed our completeness audit (133 tasks)." 133 is the number of River and Language tasks in the pass-rate band (Table 44), not the audit count. Table 2 lists 300 MACE questions. Say "133 tasks in the pass-rate band."

**P4.** The Sonnet 5 MACE AUROC is reported as "0.94 to 0.78" (a 0.16 difference), while the per-task change in Table 25 is -0.15, and the open judges' MACE results are reported as changes (0.08, 0.06). Report all as changes.

**P5.** Figure 1 example: L36-38 describes the example before saying it was chosen for a large swap (6.4 points, versus a pool mean of about 5.3). Add "(an illustrative example with a larger-than-average swap)" in the text itself, not only in the caption.

**P6.** Appendix Table 26:
- It uses internal registration codes ("R3-C", "R4-C", "R5-A", "R8-A") that reviewers cannot interpret.
- It contains typos such as "93 (93 tasks)" and "81 (81 tasks)."
- It sits *before* Table 43, the table it is the source for.
- Fix: merge it into Table 43 as a "Source" column.

**P7.** Appendix bloat: 29 pages and 50 tables, with several quantities reported three times under different scorers (Tables 9/12/46; 21/35/47; 23/44). Consolidate to one table per quantity, with scorer and labeling columns.

**P8.** L171: "Sonnet 5's CLI and API scores agree exactly on 67% of shared calls, so we do not compare the two interfaces directly." Yet Figure 3a and 3b place CLI and API Sonnet 5 results side by side (grouped, but visually adjacent). Add "(different interfaces; compare within group)" to the Figure 3b row label.

**P9.** L207: "On an exploratory pool the swap moves scores by up to 9.8 points for the smallest Qwen2.5 judges." That result is on the Ties pool, with 10-40 samples per cell (Table 5). Mark it exploratory, since it is quoted as supporting P1.

**P10.** Related work, L370-371: "our results suggest that a self-generated reference could anchor the same way." This is speculation. Say "we did not test self-generated references."

**P11.** Leftover source fallback: appendix.tex L451 contains `\pending{pending}` in red if `tables/sonnet_r8.tex` is missing. It renders correctly now, but remove the fallback before submission so a broken build cannot produce red "pending" text.

---

## 4. Figure-by-figure and table-by-table critique

### Figure 1 (p. 2): the concept figure

**Earns its space?** Panels a-c: yes, and they are the best thing in the paper. Panel d: no.

**Panels a-b.** Excellent. One task, one candidate, three prompts, three scores. A reader gets the paper in ten seconds. Keep them.

**Panel c.**
- Good content, but the "+5.3" label collides with the y-axis spine.
- The grey "matches neither" bars have no value labels. They are the key placebo; add "+0.1 / +0.3 / +0.0".
- The panel mixes readouts without saying so: Qwen2.5-7B uses the exact scorer (‡), while phi-4 and Sonnet 5 use the registered runs. Put marks on the tick labels.
- "93-120 tasks" in the title is cryptic. Put "onto: 120, off: 93, neither: 113" in the caption.

**Panel d.**
- It is a schematic with two "observed" markers placed by assertion, not measurement.
- Per M2, marker 2 (thinking judges on arithmetic) does not sit at high verification by the paper's own blind-AUROC measure (0.86, vs 0.87 for the score-only judge that anchors hardest).
- It duplicates Table 1's "what each reading predicts" columns.
- Its serif font (Times) differs from panel c's sans-serif. Its axis label "swap effect" is rotated and about 6 pt in print.
- **Fix, using existing data only:** replace panel d with an observed scatter of swap size vs blind confidence on the swapped answer. Plot one point per judge-by-condition, taking swap size from Tables 4, 45, 50, and N and blind confidence as the share of correct answers scored 10 blind (reported for the thinking judges and derivable from stored scores). Or delete panel d and let Table 1 carry the predictions.

**Caption.**
- Nearly stands alone.
- The (d) text ("(1) Sonnet 5 on factual questions ranks correct answers above a wrong one 94% of the time…") is a results claim, not a caption. After the M2 rewrite, trim it.
- The title "A judge's score follows the correct answer it is shown" is accurate and good.

### Table 1 (p. 3): predictions, observations, verdicts

**Earns its space?** In principle, yes: this is the right table for a prediction-driven paper.

**Readability:**
- The "Observed" column is a wall of ranges with inline superscript marks; the P2 cell has 6 numbers and 3 marks.
- The caption is 7 lines, including a list of failed predictions "near these rows," which is honest but hard to parse.

**Content problems:**
- P2 "implied by P1" (M6).
- P3a "Splits: both mechanisms" (M2).
- The P3b verdict "Holds" is based on one post hoc correlation, and a Qwen2.5-7B swap of 3.6 points at blind AUROC 0.98 is equally P3a evidence.
- PRE marks are used here while the text says unmarked means pre-specified (M8).

**Fix:**
- Cut "Observed" to one headline number per row, under one labeling, with its mark.
- Move the failed-prediction list to a "Did not hold" column or row.
- Set P3a to "Mixed" and P3b to "Weak (post hoc)."

### Figure 2 (p. 5): selection and grading

**Earns its space?** Yes. The one-answer vs several-answers contrast is the paper's second key message.

**Problems:**
- **No uncertainty is shown at all** in a main-results figure. Intervals exist in Tables 12, 13, 25, 44, and 47. Add CI whiskers on the referenced dot, or at least on the difference.
- **Scorer and labeling are unstated** for panel a (see M3d).
- **Panel b mixes non-comparable designs** in adjacent rows: Sonnet 5 on 16-candidate subsamples vs open judges on 64 candidates, and any-format labels on constructed pools vs answer lists on MACE. The caption notes this, but visually they read as one series. Use a different marker (hollow or square) for Sonnet 5 rows; Figure 6 already does this.
- **Layout:** large dead space; the plot area uses about 75% of \textwidth. Panel a has sparse rows with large gaps, and the legend sits only under panel a. The left-aligned bold group headers ("MACE, several answers") collide visually with the row labels in panel b.
- **Fonts:** DejaVu Sans at about 6.5 pt in print. Borderline legible; increase to at least 7.5 pt.
- **Caption:** stands alone. But "without lowering accuracy on natural questions" in the title is a claim about a +2.0 [-5.1, +10.1] and +6.1 [-1.0, +13.1] result. Say "with no detectable accuracy loss on natural multi-answer questions."
- **Suggested addition, from existing data:** show GPT-4.1 in panel b, replication and k-pool (Table 13), which supports M4.

### Figure 3 (p. 7): reasoning before scoring

**Earns its space?** Partly. Panel a is useful; panel b does not support the figure's title for Sonnet 5.

**Panel a.**
- Marker convention contradicts the Setup. The caption says "Hollow: rationale-first," and L168-169 defines Qwen3-8B and 14B *with thinking off* as rationale-first ("write before a final 'Score: N' line"). But "Qwen3-8B, thinking off" and "Qwen3-14B, thinking off" are drawn filled. Either the definition or the markers are wrong. Table 42 shows thinking-off Qwen3 writes about 159 tokens, so they are rationale-first.
- Three groups with different designs sit on one axis with "compare within a group" in the caption. Readers will compare across groups anyway. Use small multiples, or at least wider separators with the design printed in each group header.
- Registration marks are missing (M8).
- The value labels are good.

**Panel b.**
- Arithmetic bars are invisible at this scale (1.5, 0.0, 6.1, 0.3 on a 0-60 axis), and there are only two ticks (0, 50).
- There is no Sonnet 5 arithmetic row. So the title's Sonnet 5 claim ("nearly removes anchoring on arithmetic but not on factual questions") is made across two metrics and two designs: swap loss in panel a, false rejections in panel b.
- Sonnet 5's factual reduction is itself "not distinguishable from zero," with a paired interval allowing a ~60% reduction.
- **Fix:** plot one metric for both domains. Available data: false-rejection *change* on arithmetic for Sonnet 5 CLI (the 26.7% → 0.4% levels in App. N, the blind level also available). Or plot the added margin for all rows (Table 50 plus App. N: Sonnet factual +3.98 / +3.03).
- Retitle: "Reasoning before scoring removes anchoring on arithmetic; on factual questions it remains (Qwen3: halved; Sonnet 5: +3.0 points)."

**Caption.** "arithmetic cells use the rotation subsample" uses an undefined term (M9).

### Tables in the appendix

- **Table 2 (pools).** Useful. The MACE row says 300 questions; the main text says 133. Reconcile.
- **Table 3 (ledger).** Valuable and honest, but its section cross-references are stale (M8). The verdict rule was "applied retroactively … on 13 September 2026, after most of their outcomes were known." Keep that disclosure; it is the right call.
- **Tables 4, 45.** Good. Table 4 should be the source for Figure 1c, and its caption should say so.
- **Table 8 vs Tables 12, 46.** Three versions of k-pool accuracy (original scorer registered labels; exact scorer, four labelings; exact scorer). Merge.
- **Table 9.** A Sonnet 5 row of "—" with a footnote that only correct answers were scored. Drop the row and point to Table 25.
- **Tables 12-14.** The core robustness tables. Promote the any-format column to "primary" and say so in the captions.
- **Table 15.** Mixes counts, agreement rates, and mitigation accuracy in one "Quantity / Value" list. The mitigation rows contradict the Conclusion (M1). Split into a labeling table and a mitigation table.
- **Table 17.** A grab-bag ("look-alikes, results with them removed, GPT-4.1 selection, Sonnet 5 score coverage, and the Sonnet 5 scores behind Figure 1a"). The caption says "behind Figure 1a," but Figure 1a is a text box with no Sonnet 5 scores; this probably means Figure 1c. Fix the reference and split the table by topic.
- **Tables 21 / 35 / 47.** Three MATH-500 tables with discrepant blind values (M3d). Merge into one.
- **Table 26.** Internal codes and an ordering problem (P6).
- **Table 34 ("descriptive map").** It uses registered-label accuracy for the k-pool (-15.4 to -35.9) that the Limitations say main-text claims avoid. It is not cited from the main text. Cut it, or relabel it with any-format values.
- **Table 43.** Useful; it is what Figure 3b should plot. Registration marks are placed on the column headers inconsistently in the rendering (the PRE/† superscripts float above the first data row).
- **Table 48.** The labeling is unstated, and it actually matches any-format (M3a). "PRE / PH" is undefined.
- **Table 49.** Does not contain several numbers the main text quotes (M5). It also contains one (+29.4) that the main text does not use.
- **Figures 4-9.** Serviceable. Figure 5's x-axis label "inflation added by the reference (SD)" is the first place a reader meets the unit. Figure 6 has "not shown (see caption)" repeated five times; use a single note instead.

---

## 5. What would move the score (no new experiments)

### To a 6 (weak accept)

1. **M1.** Rewrite the Conclusion under one labeling, correct "up to 28%," and make the recommendation consistent with the mitigation numbers.
2. **M2.** Downgrade the mechanism claims:
   - abstract, intro, Table 1, and Section 6 verdict say "moderated by reasoning; mechanism unresolved";
   - report Table 50's unchanged blind AUROC under thinking;
   - report Qwen2.5-7B's 3.6-point swap at blind AUROC 0.98 as P3a-relevant;
   - report Qwen2.5-7B's words result;
   - state that the expression test is arithmetic-only;
   - fix or drop Figure 1d.
3. **M3, M5.** Correct every mislabeled scorer or labeling (0.87 → 0.60; "falsifying"; mixed scorers). Add the unsourced numbers (64/45/31/5 pp with CIs; 35%/19%; "38 tasks"; "89%") to Table 49, or cut them.
4. **M4.** One inclusion rule for grading claims; report GPT-4.1's grading result.
5. **M8.** One registration-mark convention. Fix the † on the registered blind-accepted filter, the ‡ over a mixed set, "PH", the Figure 3a marks, and the stale ledger cross-references.

These are all corrections of statements the paper's own tables contradict. After them I would trust the main text.

### To a 7 (accept)

Everything for 6, plus:

6. **M10 restructure.**
   - One primary labeling (any format) and one primary scorer (exact) in the main text; every alternative in a single robustness table.
   - At most three numbers per claim.
   - Ledger count out of the abstract.
   - The abstract rewritten around three sentences: swap result, grading consequence, reasoning moderator. Suggested skeleton: "When a question has several correct answers, an LLM judge's score follows which one it is shown: swapping the reference moves identical text by 2.7-5.4 points (Qwen2.5-7B, phi-4, Sonnet 5). Correct answers that differ from the reference are graded worse (AUROC -0.17 to -0.27 for four open judges; -0.04 to -0.15 for two frontier judges), although a reference still helps when the answer is unique (+30 pp on MATH-500). Reasoning before scoring removes the effect on arithmetic but not on factual questions, and judges that rank correct answers above wrong ones without a reference still anchor. Selection accuracy suffers only when no candidate matches the reference."
7. **M7.** Fix Eq. (1) so the answer key is expressible, and list the operationalizations of v_c.
8. **Figures.**
   - CIs on Figure 2.
   - Figure 3b on one metric per domain, including Sonnet 5 arithmetic.
   - Figure 3a markers consistent with the rationale-first definition.
   - One font family, at least 7.5 pt, across Figures 1-3.
   - Figure 1c placebo values labeled.
9. **M6.** Retitle Section 7; fix the "already 79%" reasoning; add the k-pool k=1 neutral result to Table 1.
10. **Appendix consolidation.** One table per quantity, internal codes removed, cross-references fixed. Target: under 20 appendix pages.

### To an 8 (strong accept, best-paper-track presentation)

Everything for 7, plus:

11. **One question, answered cleanly, in the first two pages.** Lead with "Does a reference act as an answer key when there are several correct answers? No: the score follows the answer shown." Figure 1a-c is the proof, and Figure 2 is the consequence. Present the reasoning moderator (Figure 3) as the practical finding ("reasoning judges are safe on checkable tasks, not on factual ones"), not as mechanism adjudication. A Mirage-style paper earns trust by claiming exactly what the data show.
12. **Replace Figure 1d with an observed panel** built from stored scores: swap size vs per-answer blind confidence, one point per judge and condition. This would turn the mechanism discussion into a picture the reader can judge. It requires only re-analysis of stored score files.
13. **A single practitioner table in the main text**, drawn from Tables 15, 25, and 36 under one labeling: protocol (reference, blind, max rule, blind-then-reveal) by pool (unique-answer math, constructed multi-answer, natural multi-answer), giving accuracy change and grading AUROC change. The Conclusion's recommendation should cite only this table.
14. **Word the scope honestly where new experiments would be needed.**
   - All open judges are at most 14B, and there is one frontier family per analysis.
   - The expression-rewrite test exists only for arithmetic.
   - The downstream training claim is unshown.
   - The Limitations do this partly. Move the scope statement into the Introduction's "What we find" paragraph: "on judges up to 14B parameters and one frontier family per analysis."

Even with all of this, an 8 is a stretch without broader frontier coverage and a mechanism test on factual questions. Those would need new experiments. With the rewrites above, the paper can honestly claim a robust, practically important measurement result, and that deserves a 7.
