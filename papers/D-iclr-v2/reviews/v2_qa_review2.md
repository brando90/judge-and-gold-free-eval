# Paper D v2: independent QA review 2 (after the v2 QA and AC reviews, and R26-A/B)

**Reviewed:** `papers/D-iclr-v2/`: `main.tex`, `appendix.tex`, `references.bib`, `tables/`, `figures/`, and `scripts/make_figures.py` (Figure 4 only).

**Sources:**
- `papers/analysis/`: `r24a_{s41,h41,h03,sS5,hS5}.json`, `r24b_gpt41.json`, `r24c_{sonnet,opus,gpt41}.json`, `r24d_think_sentence.json`, `r25_{cot,verify,solve}_{gpt41,sonnet}.json`, `r26a_{gpt41,sonnet}.json`, `r26b_{gpt41,sonnet}.json`;
- `prevalence_v2/prevalence_v2_results.json`;
- `survey/practice_survey.md`;
- `registration_round24.md`, `registration_round25.md`, `registration_round26.md`.

**Build:** `latexmk -pdf` in a scratch copy, so the repo's build files were not touched. Exit 0, 64 pages.

**Out of scope, as instructed:** the red `\pending` R26-C text, the empty R26-C appendix paragraph, and the missing Figure 4 verifier rows. Line numbers refer to the current `main.tex` and `appendix.tex`.

**Page budget.** The Conclusion ends at PDF line 481 on page 9, and the AI use statement fills the rest of the page to line 485. About 4 lines of main text can be added before the Conclusion runs onto page 10. The replacements below are written to stay within that: B1 is +0, B2 about +2 in a page 3 caption, B3 about +1, B4 about +1.

---

## BLOCKERS

### B1. Rounding error: "52" should be "53"
- **Where:** `main.tex` l.227 (Section 7, "What sets the size").
- **Current text:** "recovers 35 points for GPT-4.1 and 52 for Sonnet~5, leaving 31 and 13."
- **Source:** `r26a_sonnet.json` `hle_edit_minus_hle` = 0.525168, which is 52.5 points and rounds to 53. The same sentence rounds 12.6 to 13 and 35.4 to 35. The appendix (l.812) and the registration print 52.5, which is correct.
- **Replacement:** "recovers 35 points for GPT-4.1 and 53 for Sonnet~5, leaving 31 and 13."

### B2. Table 1's list of failed predictions no longer matches the ledger
- **Where:** `main.tex` l.100, Table 1 caption.
- **Problem:** The Fixes row now reports the R26-A correctness prompts ("10--17 points short"). The caption's "for the consequence and fixes" list still ends at R24/R25, and omits all 8 R26 falsifications recorded in the ledger (`appendix.tex` l.213–214) and in `registration_round26.md`:
  - P-R26A2, GPT-4.1: direct prompt blind within 5 points of the lists (−5.4);
  - P-R26A3, GPT-4.1: direct shortfall within 5 points of chain of thought (−17.4 against −3.0);
  - P-R26A5, both judges: edited HLE judge within 10 points of the lists (−31.2, −12.6);
  - P-R26B1, direct and verify-first, both judges: grading AUROC no more than 0.05 below blind (−0.089, −0.057, −0.068, −0.090).
- **Current text:** "…for the consequence and fixes, a 3-point bound on extra wrong-answer credit with the list (two of five graders), a 10-point credit drop under reasoning prompts (none of six), and a remaining rise under thinking plus the full-credit sentence."
- **Replacement:** "…for the consequence and fixes, a 3-point bound on extra wrong-answer credit with the list (two of five graders), a 10-point credit drop under reasoning prompts (none of six), a remaining rise under thinking plus the full-credit sentence, GPT-4.1's direct prompt within 5 points of chain of thought and of the lists blind, the edited HLE judge within 10 points of the lists (both judges), and grading AUROC within 0.05 of blind under direct and verify-first prompts (both judges)."
- **Consistency note (optional):** the list already includes the not-confirmed P-R24D3. The not-confirmed P-R25A1 (verify-first and solve-first GPT-4.1) is still absent. Either add "a shortfall for verify- and solve-first GPT-4.1", or make the caption say "failed or unconfirmed" and apply that rule to both.

### B3. "Instruction and reasoning both matter" goes against a registered verdict
- **Where:** `main.tex` l.227, last sentence.
- **Source:**
  - **P-R26A3** predicted that the instruction, not written reasoning, sets the size. It was **confirmed for Sonnet 5** (direct −10.1 against chain of thought −6.0, within 5 points) and **falsified only for GPT-4.1** (−17.4 against −3.0).
  - **Grading (R26-B, Sonnet 5):** verify-first, a reasoning prompt, lowered grading *more* than the direct prompt (AUROC −0.090 against −0.057; false rejections +17.1 against +13.8 pp).
  - So reasoning mattered on accuracy for GPT-4.1. For Sonnet 5 it did not, by the registered test.
- **Replacement:** "Most of the gap closes when the grader is asked about correctness instead of matching (from 67 and 65 points to 17 and 10); written reasoning shrinks it further for GPT-4.1 (to 3 with chain of thought) but, by our registered 5-point test, not for Sonnet~5 (to 6), and a residual pull remains for Sonnet~5 under every prompt."

### B4. "mostly because they are told to match" (Conclusion) and "Most of this comes from the instruction to match" (intro) claim more than the one clean test shows
- **Where:** `main.tex` l.274 (Conclusion) and l.92 (intro).
- **Source:**
  - **The one single-factor test** is deleting the HLE judge's match clause (R26-A). It recovers 35.4 of 66.6 points for GPT-4.1 (53%) and 52.5 of 65.1 for Sonnet 5 (81%). GPT-4.1 still falls 31.2 points short with the clause gone.
  - **The SimpleQA grader** (30–34 of the "30 to 67") was never ablated. The direct prompt differs from it in template, few-shot examples, output format and temperature. Even so, it leaves GPT-4.1 17.4 of its 30.4 points (it recovers 43%).
  - **"the same judges"** (intro): o3-mini, one of the configured judges, was not run with the correctness prompts.
- **Conclusion replacement (l.274):** "Run as configured on such questions, the graders of SimpleQA, BrowseComp, and HLE score four models 30 to 67 points below their answer-list accuracy, largely because of what they are asked: deleting the HLE judge's match clause recovers 35 of 67 points for GPT-4.1 and 53 of 65 for Sonnet~5."
- **Intro replacement (l.92):** "Much of this comes from the instruction to match: asking GPT-4.1 and Sonnet~5 whether the answer is correct leaves 10 to 17 points, and 0.5 to 6 when they reason first (\cref{sec:cost})."

---

## SHOULD-FIX

### S1. "solving first costs grading least" rests on point estimates
- **Where:** `main.tex` l.236.
- **Source** (`r26b_*.json`, changes against blind):

  | Judge | Prompt | AUROC change | False acceptances (pp) |
  |---|---|---|---|
  | Sonnet 5 | solve-first | −0.047 [−0.082, −0.016] | +1.9 [0.0, +5.0] |
  | Sonnet 5 | direct | −0.057 [−0.106, −0.014] | |
  | GPT-4.1 | solve-first | | +3.2 [−2.0, +9.2] |
  | GPT-4.1 | verify-first | | +3.2 [−0.2, +7.9] |

- **Problem 1:** For Sonnet 5 the solve-first and direct intervals overlap almost entirely, so "least" is a point-estimate ordering.
- **Problem 2:** "up at most 3.2 points" is also a point estimate; the upper bounds reach +9.2.
- **What does hold:** solve-first is the only prompt that met the registered 0.05 bound for both judges.
- **Replacement:** "solving first had the smallest grading cost of the three prompts for both judges and was the only one within our registered 0.05 (AUROC $-0.04$ and $-0.05$ against blind; false acceptances up 3.2 and 1.9 points, with intervals reaching $+9.2$), but it still rejects 5 to 7 more points of differing correct answers (\cref{app:r26})."

### S2. "let the judge reason first" is broader than what R26-B supports
- **Where:** `main.tex` l.236 ("letting the judge reason first (\cref{sec:cost})") and l.275 (Conclusion, "let the judge reason first").
- **Problem:** R26-B falsified the grading bound for verify-first, a reasoning prompt, for both judges, and for Sonnet 5 it graded worse than no reasoning. Only solve-first held. The recipe (l.242) already says "solve the question first", so the Conclusion and the start of §8 disagree with it.
- **Replacements:** l.236: "letting the judge solve the question first". l.275: "…ask whether the answer is correct rather than whether it matches, let the judge solve the question first, and audit…".

### S3. "caps the error on their own leaderboards at about 3 points"
- **Where:** `main.tex` l.221.
- **Problem:** The same sentence quotes 15% by either annotator. The Wilson upper bound for HLE is 6.4%, and HLE reaches 6.0% if the six fallbacks involving the several-answers label had gone that way (`appendix.tex` l.129). "Caps" only holds under the adjudicated labels.
- **Replacement:** "which would bound the error on their own leaderboards at about 3 points under the adjudicated labels."
- **Also:** in the same paragraph, "RL training sets in which 5.5\% to 18\%" should read "an RL training set in which 5.5\% to 18\%". It is one set, WebInstruct-verified, which is how the intro (l.79) puts it.

### S4. The appendix is out of order at `app:reasoning`
- **What the appendix claims:** `appendix.tex` l.8 says Appendices setup–mitigation follow first use in the main text.
- **What changed:** `\cref{app:reasoning}` is now first cited in Setup (`main.tex` l.151, "Reasoning variants … are described in"). That comes before `app:grid` (l.155), but the section sits after `app:r26`.
- **First-citation order** (extra-studies block excluded, as disclosed): setup (59), survey (76), prevalence (78), ledger (100), mace (146), **reasoning (151)**, grid (155), estimator (158), rotation (165), mechanism/frontier (167), acceptance (194), r24 (218), r25/r26 (227), mitigation (236).
- **`app:r26`** is correctly placed, after r25 and before mitigation.
- **Fix:** move the `app:reasoning` section (`appendix.tex` l.836–890) to directly after `app:mace` (after l.246). Alternatively, drop the l.151 cref so that the first citation is the existing one later in the text.

### S5. Appendix R26: "the reference costs 17.4 points" misstates the quantity
- **Where:** `appendix.tex` l.812.
- **Problem:** 17.4 and 10.1 are accuracy with the reference minus the answer lists. What the reference itself costs, against blind, is 12.1 and 8.4 (−17.4 − (−5.4); −10.1 − (−1.7)).
- **Replacement:** "Without written reasoning, GPT-4.1 and Sonnet~5 fall 17.4 and 10.1 points short of the lists with the reference (5.4 and 1.7 blind), against 3.0 and 6.0 with chain of thought;"
- **Also, same paragraph:** "so the verbatim rows differ slightly from \cref{tab:r24-standard}, where GPT-4.1 ran as simple-evals configures it" explains only GPT-4.1. Sonnet 5 also differs (−65.1 against −64.9; 1.8% against 2.3% credited) although its settings match R24, which were also thinking disabled and 1,024 tokens. Add: "and Sonnet~5's differences are call-to-call variation."

### S6. Ledger count sentence: target values, and the counting rule
- **Where:** `appendix.tex` l.144, currently "181 confirmed, 14 not confirmed, and 25 falsified, of 260".
- **With R26-A and R26-B** (24 predictions; 16 confirmed, 8 falsified; tally in the Verified clean section), the sentence becomes: **"197 confirmed, 14 not confirmed, and 33 falsified, of 284"**. Split, not evaluable, not scored and excluded stay 17 / 18 / 2 / 3, so 197 + 14 + 33 + 40 = 284.
- **R26-C** will add 6 more (3 predictions × 2 verifiers). That matches the registration's total of 30.
- **Carried over from QA review 1, S8:** the text still says "Counting each registered prediction once" and defines *split* as one prediction with different verdicts across judges. By that rule, P-R26A2 and P-R26A3 (confirmed for Sonnet 5, falsified for GPT-4.1) would be splits, and 284 would not follow. Suggested wording: "Counting each registered prediction once, and each judge or grader configuration separately from round 19 on, …".

### S7. Figure 4: a clipped interval, and the legend collides with the axis label
- **Clipped interval (lower panel, all 10 rows present):** the "HLE judge, match clause cut, GPT-4.1" whisker is cut at the left spine. `make_figures.py` l.972 sets `a2.set_xlim(-36, 3)`, but the interval is [−36.4, −26.3]. A 400 dpi render of p. 7 shows the line ending at the axis. **Fix:** `a2.set_xlim(-38, 3)`.
- **Label collision:** the lower x-label "accuracy minus answer-list accuracy (points)" touches the legend row; the descenders of "(points)" run into "full-credit sentence". **Fix:** raise `bottom = 0.50 / H` to about `0.60 / H` (l.965), or anchor the legend lower.
- **Legibility is fine.** Labels and ticks are 7.8 pt (panel b ticks 7.6 pt; titles 8.8 pt). The PDF is 420.6 pt wide (the title offset `x=-1.3` widens the tight bbox) and prints at `\textwidth` = 397.5 pt (×0.945). Printed sizes are therefore 7.4 pt for labels and ticks, 7.2 pt for panel (b) ticks and 8.3 pt for titles, all at or above 7 pt.
- **Optional:** the row labels say "match clause cut" while the text and caption say "removed".

### S8. Abstract wording
- **Where:** `main.tex` l.50.
- **Current text:** "The size follows the grader's instruction: asked whether the answer is correct instead of whether it matches, judges fall 0.5 to 17 points short, and given the full answer list the benchmark graders come within a point of it."
- **Problems:**
  - "it" has no antecedent in the sentence.
  - "judges" means two judges.
  - Much of the 0.5-to-17 spread comes from reasoning (GPT-4.1: 17 to 3), not from the instruction.
- **Replacement:** "The size follows what the grader is asked: asked whether the answer is correct instead of whether it matches, two judges fall 0.5 to 17 points short of answer-list accuracy, and given the full answer list the benchmark graders come within a point of it."

### S9. Recipe bullet scope
- **Where:** `main.tex` l.242.
- **Problem:** "(two judges)" gives no pool scope, and the bullet does not say which reasoning prompt failed.
- **Replacement:** "…ask whether the response is correct and let it solve the question first (two judges; 149 benchmark questions and 40 \textsc{MACE} tasks; a verify-first prompt did not hold up on grading); this shrinks but does not remove the harm."

### S10. Carried over from QA review 1: `tables/r24_fix.tex` prints Opus 5's lower bound as `+0.000`
- **Where:** `tables/r24_fix.tex`.
- **Source:** `r24c_opus.json` gives `G_reflist_minus_blind` lower bound = −0.000209, and `registration_round24.md` l.160 prints "−0.000".
- **Why it matters:** the caption of `tab:r20-safeguards` says AUROC uses three decimals so that an interval ending just below zero does not look as if it clears zero.
- **Fix:** print `$-0.000$`, and build the table from unrounded values.

### S11. Minor
- **Residual pull scope** (l.227): "a residual pull remains for Sonnet~5 under every prompt" is true, but it undersells the grading result. On the 40-task subsample, false rejections rise for both judges under every prompt, including GPT-4.1 solve-first at +4.7 [+0.4, +10.8]. Optional: "for Sonnet~5 under every prompt, and in grading for both judges".
- **Limitations (optional):** solve-first was tested only where the judges mostly get the answer right blind (blind AUROC 0.91). On questions the judge cannot answer itself, as on HLE, it is untested. One clause could go in the "Judges and prompts" bullet.
- **Label name:** `fig:reasoning` still labels Figure 3 (acceptance). It resolves correctly; renaming it to `fig:acceptance` is cosmetic.

---

## Verified clean (numbers checked)

### R26-A (`r26a_*.json` → `tables/r26_instruction.tex`, §7, intro, Table 1, abstract, App. r26)
Every table cell matches:

| Judge | Condition | Minus list [95% CI] | Differing correct credited | Wrong credited |
|---|---|---|---|---|
| GPT-4.1 | direct, blind | −5.4 [−7.7, −3.2] | 91.4 | 12.5 |
| GPT-4.1 | direct, reference | −17.4 [−21.0, −14.1] | 73.2 | 7.1 |
| GPT-4.1 | HLE verbatim | −66.6 | 0.0 | 0.0 |
| GPT-4.1 | HLE, match clause removed | −31.2 | 53.3 | 0.0 |
| Sonnet 5 | direct, blind | −1.7 [−3.5, +0.0] | 96.5 | 10.7 |
| Sonnet 5 | direct, reference | −10.1 | 83.3 | 10.7 |
| Sonnet 5 | HLE verbatim | −65.1 | 1.8 | 3.6 |
| Sonnet 5 | HLE, match clause removed | −12.6 | 80.3 | 7.1 |

Prose that checks:
- "10 to 17 points" (10.07, 17.45), in the intro, Table 1 and §7;
- "17 and 10 points short (5 and 2 blind)";
- "0.5 to 17" (abstract);
- "35 … leaving 31 and 13" (the 52 is B1);
- App. r26 "35.4 and 52.5 … 31.2 and 12.6";
- "even with o3-mini … almost no differing correct answer" (0.0–2.3%).

### R26-B (`r26b_*.json` → `tables/r26_subsample.tex`, §8, App. r26)
- **AUROC blind → reference:** GPT-4.1 direct 0.848→0.759, verify 0.927→0.859, solve 0.907→0.868; Sonnet 5 direct 0.862→0.805, verify 0.908→0.818, solve 0.913→0.867.
- **Changes (AUROC; false rejections; false acceptances):**
  - GPT-4.1: −0.089, −0.068, −0.040; +23.0, +10.3, +4.7; −5.1, +3.2, +3.2.
  - Sonnet 5: −0.057, −0.090, −0.047; +13.8, +17.1, +7.4; −2.5, +0.9, +1.9.
- **HLE judge:** verbatim AUROC 0.485 / 0.501 with 100% / 95.6% rejected; edited 0.611 / 0.818; edited minus verbatim +0.126 [+0.077, +0.176] and +0.317 [+0.263, +0.369]; false-rejection changes −28.5 and −65.9; false-acceptance changes +3.4 and +2.5.
- **Prose that checks:**
  - "AUROC −0.04 and −0.05";
  - "false acceptances up at most 3.2 points" (see S1 for scope);
  - "rejects 5 to 7 more points" (4.7, 7.4);
  - "falls 0.04 to 0.09 under every prompt";
  - "only solve-first stays within the registered 0.05 for both judges";
  - "96% to 100%", "at chance AUROC", "0.61 and 0.82".
- **"solving first costs grading least":** holds as a point-estimate ordering for both judges (S1).

### R25 (`r25_*.json` → `tables/r25_types.tex`, §7, abstract, intro, Table 1)
- Reference minus list: −3.0, −6.0, −1.5, −6.2, −0.5, −3.4, so "0.5 to 6" holds.
- Blind: −0.8, −0.5, −0.3, −0.2, −0.3, 0.0, so "within 1 blind" holds.
- The earlier QA fixes are in: both 90.1 cells now read 90.2, and the ledger and App. r25 say "0.8 to 8.6".
- In every place, "0.5 to 6" is now paired with the 10–17 direct-prompt range (intro l.92, Table 1 l.118, §7 l.227) or merged into it (abstract "0.5 to 17"). No stale single-range use remains.

### R24 (`r24a/b/c/d` → `tables/r24_*.tex`, §7, §8, Table 1, Conclusion)
- SimpleQA grader credits 47–53%, BrowseComp/HLE judge 0–2.3%; 30 to 34 and 65 to 67 points below; "30 to 67", "0% to 53%".
- Full list: within 0.5 points (max +0.5); 99% or more credited (99.2–99.7); at most 3 of 56 wrong answers (5.4%); bound failed for h41 (+3.6) and h03 (+5.4).
- Grading AUROC with the list 0.03 to 0.06 above blind (+0.032, +0.033, +0.057), against 0.06 to 0.16 below with one reference (−0.063, −0.164, −0.153); false rejections with the list −2.2, −6.3, −2.2.
- GPT-4.1 rubric: −9.6 ("by 10"), blind −2.5; redraw shifts 12.5 and 19.0.
- Claude rubric graders: 16 to 22 points (15.6, 20.1, 22.3); Haiku blind −9.2; redraw 23.2 to 38.2.
- R24-D: +18.1 / −0.065, +14.9 / −0.090, −0.2 [−7.2, +4.6]; "36 to 18 pp for Sonnet 5, to 8 pp for Opus 5" holds (36.3 − 28.0 = 8.3); "15 pp with thinking" holds.

### Prevalence (`prevalence_v2_results.json`, `tables/prevalence*.tex`)
- **Several-answer rates:** SimpleQA 1.0%, BrowseComp 0.0%, HLE 3.0% [1.4, 6.4], TriviaQA 4.0%, WebInstruct 5.5%. So "0% to 3%" (abstract, §7) and "0% to 4%" (intro) hold.
- **Either annotator:** HLE 15.0% and WebInstruct 18.0%, so "up to 15% on HLE" and "5.5% to 18%" hold.
- **Agreement:** κ at most 0.35.
- **First audit:** 0% / 2.5% / 2.5% for MATH-500, GSM8K and DeepScaleR, so "0% to 2.5%" holds; NQ-open 30.0%.
- **"about 3 points":** matches the 3.0% adjudicated rate (scope in S3).

### Survey (`practice_survey.md` §1)
- 16 + 12 + 4 + 11 = 43 surveyed; 11 + 11 + 3 + 10 = 35 reference-guided.
- 34 research papers.
- 34 prompts read, of which 27 define correctness as matching; none credits an answer outside the reference.
- CompassVerifier's "NEVER QUESTION" and Omni-MATH's "ALWAYS correct" quotes are present.

### Registration verdicts
- **Ledger row "Instruction against reasoning"** (`appendix.tex` l.213) matches `registration_round26.md` exactly:
  - A1: confirmed, both.
  - A2: confirmed for Sonnet 5, falsified for GPT-4.1 (−5.4).
  - A3: confirmed for Sonnet 5, falsified for GPT-4.1 (−17.4 against −3.0).
  - A4: confirmed, both.
  - A5: falsified, both.
- **Ledger row "Grading with many wrong answers"** (l.214) matches exactly:
  - B1: confirmed for solve-first; falsified for direct and verify-first, both judges.
  - B2: confirmed, all six.
  - B3: confirmed, both.
- **Tally:** A is 10 predictions (6 confirmed, 4 falsified); B is 14 (10 confirmed, 4 falsified). Together, 24 predictions: 16 confirmed and 8 falsified, matching the registration.
- **Section references** in both rows (`sec:cost`, `sec:fix`, `app:r26`) point at the right sections.

### Table 1 against the body
- P1 2.7–5.4 (2.66 to 5.41, §4); P2 0.06–0.16 and 0.17–0.27 (0.07–0.14 boxed); P2′ 29–31 (28.6, 30.6).
- Consequence row: 30–67, 10–22, 12.5–38, about 3; "nine configurations from two developers".
- Fixes row: within 0.5, 0.03–0.06, 10–17 and 0.5–6, one judge. All consistent with §§4–8 and the Conclusion.

### Cross-references and build
- No undefined references or citations, no multiply defined labels.
- No overfull boxes; underfull boxes only.
- Two hyperref "Token not allowed in a PDF string" warnings, as before.
- `\cref{fig:reasoning}` resolves to Figure 3; `\cref{app:r25,app:r26}` resolve.
- `app:r26` is correctly placed after `app:r25` and before `app:mitigation`. The only order break is `app:reasoning` (S4).

### Layout
- Figure 1 is on page 1.
- The main text through the Conclusion ends on page 9 (PDF line 481).
- Figure 4 prints at 7.2 pt or more, and its lower panel shows all 10 rows. The exceptions are the one clipped whisker and the label collision in S7.

### Stale wording
- No "verify the answer itself", "removed the (factual) effect", "removes the effect" or "order of magnitude" in `main.tex`, `appendix.tex`, `tables/` or `figures/`.
- The "verify the answer on your own" at l.227 is the name of the prompt, not a claim.
- The remaining pre-R26 generalizations are "let the judge reason first" (S2) and "Most of this comes from…" / "mostly because…" (B4).

---

**Verdict: not ready. There are four blockers (B1 is a one-word rounding fix; B2 to B4 each need a one- or two-sentence change) and all fit the page-9 budget; otherwise the R24–R26 numbers match their sources.**
