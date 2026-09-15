# Paper D v2: independent QA review (correctness and structure)

Reviewed: `papers/D-iclr-v2/` at 32987b0 (`main.tex`, `appendix.tex`, `references.bib`, tables, figures), compared with `papers/D-iclr/` (tag `paper-d-iclr-v1`).

Sources checked:
- `papers/analysis/r24*.json`, `r25*.json`, `prevalence_v2/{prevalence_v2_results.json,RESULTS.md,PROTOCOL.md}`;
- `survey/{practice_survey.json,practice_survey.md,prompts/*}`;
- `registration_round24.md`, `registration_round25.md`;
- vendored grader sources and the R24/R25 harnesses;
- raw R19/R20/R24 score files, used for one recomputation.

Line numbers refer to the current `main.tex` and `appendix.tex`.

---

## BLOCKERS

### B1. The abstract credits verify-first prompts with a range that comes from three prompt types
- **Where:** `main.tex` l.50 (abstract).
- **Current text:** "without a list, prompting the judge to verify the answer itself cuts the shortfall to 0.5 to 6 points."
- **Source** (`r25_*.json`, `ref_minus_list`):

  | Prompt | GPT-4.1 | Sonnet 5 |
  |---|---|---|
  | verify-first | −1.5 | −6.2 |
  | solve-first | −0.5 | −3.4 |
  | chain of thought | −3.0 | −6.0 |

- **Problem:** The 0.5 comes from solve-first GPT-4.1. Verify-first alone covers 1.5 to 6.2 points. Verify-first does no better than plain chain of thought for Sonnet 5 (−6.2 against −6.0), so the data do not single out verification as the lever.
- **Replacement:** "without a list, prompting the judge to reason about correctness before deciding (chain of thought, verify first, or solve first) cuts the shortfall to 0.5 to 6 points."

The same attribution appears in three more places. Fix them together:
- **`main.tex` l.233.** Current: "judges told to verify the answer on their own or to solve the question first fall 0.5 to 6 points short on the benchmark, against 30 to 67 for the matching prompts". This leaves out chain of thought, which does just as well. Replace with: "judges asked to reason about correctness before deciding (chain of thought, verify first, or solve first) fall 0.5 to 6 points short on the benchmark, against 30 to 67 for the matching prompts; solving the question first did best for both judges (0.5 and 3.4 points)".
- **`main.tex` l.239 (recipe).** Current: "ask the judge to verify the answer on its own before consulting the reference". Replace with: "ask the judge to answer the question itself before consulting the reference".
- **`main.tex` l.274 (Conclusion).** Current: "Where the answers cannot be listed, ask the judge to verify the answer itself before it consults the reference". Replace with: "Where the answers cannot be listed, ask the judge to answer the question itself before it consults the reference".

### B2. "removed the factual effect" overstates a null interval
- **Where:** `main.tex` l.92 (intro).
- **Current text:** "and a thinking judge told that other answers can be correct removed the factual effect for one judge (\cref{sec:fix})."
- **Source** (`r24d_think_sentence.json`):
  - False-rejection change: −0.2 pp [−7.2, +4.6].
  - Grading AUROC change: −0.024 [−0.062, +0.006].
  - P-R24D3 was *not confirmed*. That is a null interval, not an equivalence test.
- **My recomputation** (same definitions as `r24_analysis.py` part d, 40 tasks):
  - Sonnet 5 with thinking already gives 3 or below to 12.2% of differing correct answers blind, against 7.2% for the non-thinking blind calls.
  - With thinking plus the sentence, the referenced rate is 11.9%.
  - So "no rise" is measured against a stricter blind baseline, and about one in eight such answers is still rejected.
- **Replacement:** "and for one judge on 40 factual tasks, thinking plus a sentence that other answers can be correct left no measurable rise in false rejections ($-0.2$~pp, 95\% interval $-7.2$ to $+4.6$; \cref{sec:fix})."
- **Suggested addition at l.233**, after "(… \ci{-7.2}{+4.6}; 40 tasks)": "; grading AUROC $-0.02$ \ci{-0.06}{+0.01}, and with thinking Sonnet~5 already rejects 12\% of these answers blind".

### B3. Table 1 and Section 7 give different redraw ranges for the same four judges
- **Where:** `main.tex` l.116, Table 1 "Consequence" row.
- **Current text:** "a redraw moves credit by 23--38 points, a regrade by about 3".
- **Conflict:** Section 7 (l.221) says "12.5 to 38 points" for the same four rubric judges.
- **Source:**
  - GPT-4.1 (`r24b_gpt41.json`): stop-matching 100 → 87.5 (12.5 pp); start-matching 80.5 → 99.4 (19.0 pp).
  - Claude graders (R22): 23.2 to 38.2 pp.
- **Replacement:** "a redraw moves credit by 12.5--38 points (23--38 for the three Claude graders), a regrade by about 3".

### B4. The survey appendix wrongly implies the seven multi-answer papers are among the eight training papers
- **Where:** `appendix.tex` l.214.
- **Current text:** "Eight of the 34 papers use the judge as an RL reward or data filter. In seven the tasks admit several valid answers, and the judge still sees one reference or a closed list; IMO-ProofBench's grader is told …"
- **Source** (`practice_survey.md` §5):
  - The eight training papers are Huang 2025, MiniMax-M1, Guru, Llama-Nemotron, WebDancer, WebSailor, ASearcher and WebExplorer.
  - The seven papers whose tasks admit several answers are Kamalloo 2023, EVOUNA, DeepResearcher, DeepResearch Bench, ICE-Score, CodeJudge and Proof or Bluff.
  - The two sets do not overlap, and all seven are evaluation-only.
  - IMO-ProofBench, which the sentence cites as the example, is labeled "partially", so it is not one of the seven.
- **Replacement:** "Eight of the 34 papers use the judge as an RL reward or data filter. In seven others, all evaluations, the tasks admit several valid answers and the judge still sees one reference or a closed list~\citep{kamalloo2023evaluating,wang2023evouna,zheng2025deepresearcher,du2025deepresearchbench,zhuo2024icescore,tong2024codejudge,petrov2025proofbluff}; among them, providing reference code made all three LLM-based evaluators worse on CoNaLa~\citep{tong2024codejudge}. IMO-ProofBench's grader is told the reference ``demonstrates one valid approach'' and is reported to be ``prone to be overly punitive'' for unconventional correct solutions~\citep{luong2025imobench}."

### B5. The AI use statement contradicts the v2 prevalence audit
- **Where:** `main.tex` l.277.
- **Current text:** "… and label a sample of dataset questions for the prevalence audit; both labeling passes came from one model family, were adjudicated against each other, and were not checked by human annotators."
- **Problem 1:** v2 adds a second audit (`app:prevalence`, `RESULTS.md`). Its passes are Claude Sonnet 5 and GPT-5-mini, from different developers, and Claude Opus 5 adjudicated.
- **Problem 2:** The same statement says "three Claude models answered and graded the benchmark questions". GPT-4.1 and o3-mini now also grade them.
- **Replacement for the benchmark clause:** "three Claude models answered the benchmark questions of \cref{sec:cost}, which Claude models, GPT-4.1, and o3-mini graded,"
- **Replacement for the labeling clause:** "and label samples of dataset questions for two prevalence audits: the first with two labeling passes from one model family, adjudicated against each other; the second with Claude Sonnet~5 and GPT-5-mini, adjudicated by Claude Opus~5. No label was checked by human annotators."

---

## SHOULD-FIX

### S1. "mostly answers that name a listed country differently" is not supported
- **Where:** `main.tex` l.230.
- **Source:** `registration_round24.md` outcome, descriptive list of wrong answers credited only with the full list:
  - "The Democratic Republic of Congo" (a true alias; four cells);
  - "Territory of New Guinea" (list entry "Papua New Guinea"; h41, h03);
  - "Sudan" (list entry "South Sudan"; s41);
  - "Wales" (list entry "United Kingdom"; h03).
- **Problem:** Only one of the four answers is another name for a listed country. By instance it accounts for 4 of 8 credits, which is half, not most. Wales is part of the listed country, Territory of New Guinea is a former territory, and Sudan is a different country.
- **Replacement:** "It admits few wrong answers: at most 3 of 56 more. Half of these credits are one alias our string matching misses (``The Democratic Republic of Congo''); the rest are a part or former name of a listed country (``Wales'', ``Territory of New Guinea'') and one different country (``Sudan'')."

### S2. "the same judge instruction reappears in agent and RL evaluations"
- **Where:** `main.tex` l.218.
- **Source** (survey records `websailor`, `browsecomp_plus`):
  - BrowseComp-Plus uses the BrowseComp/HLE prompt for evaluation only.
  - WebSailor uses it in its evaluation code. The prompt of its RL reward judge is not documented (the paper calls the reward "rule-based").
  - Both apply it to BrowseComp-style questions labeled single-answer.
- **Problem:** "RL evaluations" reads as RL rewards, which the records do not show.
- **Replacement:** "the risk is reuse: the same instruction already grades web-agent benchmarks, including the evaluation of an RL-trained agent~\citep{li2025websailor,chen2025browsecompplus}, and nothing in it limits it to questions with one answer."

### S3. Conclusion: "judges grade at least as well as blind"
- **Where:** `main.tex` l.273.
- **Source** (`r24c_*.json`, AUROC with the list minus blind, 40 tasks):

  | Judge | Change | 95% interval |
  |---|---|---|
  | Sonnet 5 | +0.032 | [+0.008, +0.060] |
  | Opus 5 | +0.033 | [−0.0002, +0.084] |
  | GPT-4.1 | +0.057 | [+0.013, +0.121] |

- **Problem:** The claim is fine as non-inferiority (the registered bound was −0.03), but it generalizes from three judges on one subsample.
- **Replacement:** "given the full list, the same graders match it within a point, and three judges grade correct answers against wrong ones as well as blind or better (AUROC $+0.03$ to $+0.06$ on 40 tasks)."
- **Also:** `tables/r24_fix.tex` prints Opus 5's lower bound as "+0.000", but the value is −0.0002 (the registration prints "−0.000"). The caption of `tab:r20-safeguards` says three decimals are used so that such an interval does not look like it clears zero. Print "$-0.000$" here too.

### S4. Intro: "their graders are reused where answers are not unique"
- **Where:** `main.tex` l.79.
- **Problem:** Nothing shows the SimpleQA, BrowseComp or HLE graders being used on WebInstruct-verified or NQ-open. General-Reasoner grades WebInstruct-verified with its own verifier (survey table 2d).
- **Replacement:** "but reference-guided graders are also used where answers are not unique: 5.5\% of questions in the WebInstruct-verified RL training set, whose verifier sees one reference~\citep{ma2025generalreasoner}, and 30\% of NQ-open questions admit several, as do benchmarks such as …"

### S5. The MT-Bench quote is framed as the start of the template
- **Where:** `main.tex` l.75.
- **Current text:** "MT-Bench's math and reasoning template begins ``by comparing the assistant's answer with the reference answer''".
- **Source:** `survey/prompts/mtbench_reference_guided.txt` (single-math-v1). The template begins "Please act as an impartial judge…". The quoted words come from "Begin your evaluation by comparing the assistant's answer with the reference answer." v1 framed this correctly.
- **Replacement:** "MT-Bench's math and reasoning template tells the judge to ``Begin your evaluation by comparing the assistant's answer with the reference answer''~\citep{zheng2023judging}."

### S6. "is ALWAYS correct" with two citations
- **Where:** `main.tex` l.76.
- **Source:** The exact string appears only in Omni-MATH ("The reference answer is ALWAYS correct"). CompassVerifier says "THE STANDARD ANSWER IS ALWAYS CORRECT".
- **Replacement:** "some declare that the reference ``is ALWAYS correct''~\citep{gao2024omnimath} or ``ALWAYS CORRECT''~\citep{liu2025compassverifier}".

### S7. Rounding errors
- **"0.7 to 8.6 points" should be "0.8 to 8.6 points".**
  - Where: `appendix.tex` l.939, the ledger row at l.153, and `registration_round25.md`.
  - Why: solve-first GPT-4.1 credit goes from 389/396 to 386/396, a drop of 3/396 = 0.76 pp (`r25_solve_gpt41.json`: −0.0076).
- **"90.1" should be "90.2", twice, in `tables/r25_types.tex`.**
  - Where: chain-of-thought Sonnet 5 and verify-first Sonnet 5, differing correct answers credited with the reference.
  - Why: 357/396 = 90.15%. The producer rounded to 0.9015 before the table rounded again.
- **The same rounding twice shows up elsewhere.**
  - `r24_fix` Sonnet 5 full-list false rejections: −2.2 in the paper, −2.3 in the registration.
  - R24-B second draw: −7.0 in the paper, −7.1 in the registration.
  - Build tables from unrounded values.

### S8. Ledger counting unit
The arithmetic is correct:

| | Total | Confirmed | Not confirmed | Falsified |
|---|---|---|---|---|
| v1 | 206 | 138 | 11 | 17 |
| R24 | 36 | 33 | 1 | 2 |
| R25 | 18 | 10 | 2 | 6 |
| v2 | 260 | 181 | 14 | 25 |

The split, not-evaluable, not-scored and excluded counts stay at 17/18/2/3.

However, the text says "Counting each registered prediction once" and defines *split* as a prediction "registered for several judges … [that] got different verdicts across them". Two new predictions fit that definition but are counted per cell:
- P-R24A4 was registered once "for each cell" and went 3 confirmed, 2 falsified.
- P-R25A1 went 4 confirmed, 2 not confirmed.

Per-cell counting matches how the R19 to R23 rows read, but the stated rule does not describe it. Suggested wording, if that is the actual unit: "Counting each registered prediction once, and each judge or grader configuration separately from round 19 on, …".

### S9. Appendix order does not follow first citation
`appendix.tex` l.8 claims the main-text order.
- **Actual order:** setup, ledger, prevalence, survey, mace, estimator, mitigation, grid, rotation, mechanism, frontier, acceptance, r24, r25, reasoning, then the extra-studies block.
- **First-citation order:** setup (Fig. 1), survey (l.76), prevalence (l.78), ledger (Table 1 caption), mace (l.146), grid (l.155), estimator (l.158), rotation, mechanism, frontier, acceptance, r24, r25, reasoning (l.233), mitigation (l.233).
- **What moved in v2:** mitigation's first citation moved to Section 8, so it now sits far too early. The survey and prevalence sections should come before the ledger, and grid before estimator.
- **Proposed order:** setup, survey, prevalence, ledger, mace, grid, estimator, rotation, mechanism, frontier, acceptance, r24, r25, reasoning, mitigation; then composition, ties, mathconstraint, code, dpo. The extra-studies block is already disclosed at l.8.

### S10. Figure 4 text prints just under 7 pt
- **Settings:** `make_figures.py` uses 7.2 to 7.3 pt tick and row labels and a 7.2 pt legend for `fig4_graders`.
- **Scaling:** The panel-title offsets (x = −0.76 and −0.62) widen the tight-bbox PDF to 431 pt. `width=\textwidth` then shrinks it to 397.5 pt (×0.92), so row labels, ticks and legend print at about 6.6 to 6.8 pt.
- **Readability:** Readable in a 100 dpi render of page 7, but below the ~7 pt target.
- **Fix:** Raise those fonts to at least 7.8 pt, or pull the title offsets in so the PDF is no wider than 5.5 in.
- **Others are fine:** Figure 3 prints at 7.6 pt or more (7.0 × 1.086) and Figure 2 at 8 pt or more.

### S11. Registration marks on survey and v1-audit numbers in the intro
Section 3 says "unmarked estimates were pre-specified". Several intro numbers are unmarked but not pre-specified:
- the practice-survey counts (43 surveyed, 35 reference-guided, 34 papers, 27 of 34 prompts), from a survey that was not registered (`tab:survey` carries †);
- "0\% to 2.5\%" and "30\% of NQ-open", from the v1 audit (`tab:prevalence` carries †).

The prevalence-v2 ranges ("0\% to 4\%", "0\% to 3\%", 5.5%) are correctly unmarked.

**Fix:** Add `\ph{}` after "(\cref{app:survey})" and after the 0% to 2.5% and 30% clauses. Alternatively, add to Section 3: "Descriptive counts from the practice survey and the first prevalence audit are post hoc."

### S12. Prevalence v2 omits two consequences of the spending cap
- **Where:** `appendix.tex` l.176.
- **Source:** `RESULTS.md` l.125–126.
  - All 106 BrowseComp fallbacks were unclear-versus-unique pairs, so the 108 BrowseComp "unclear" labels are mostly an artifact of the cap. All 79 adjudicated BrowseComp disagreements ended unique.
  - 6 of the 29 HLE fallbacks involve a several-answers label. Had they gone that way, HLE would be 6.0% [3.5, 10.2], above the "0% to 4%" and "0% to 3%" quoted in the intro and Section 7.
- **Addition after "kept the conservative label (…)":** "; the fallback can only lower the several-answers count, and had the six HLE fallbacks that involve that label been adjudicated as several, HLE would reach 6.0\%. BrowseComp's unclear labels are mostly fallbacks."

### S13. Duplicate bibliography entry
`thakur2024judging` (cited at `main.tex` l.249) and `thakur2025judging` (cited in `tab:survey`) are the same paper, arXiv 2406.12624. The reference list prints it twice. Keep one key.

### S14. Minor wording
- **Closed lists.** `main.tex` l.76 and the `tab:survey` caption say "given one reference", but the counts include closed lists (MixEval, FreshQA; DeepResearcher and EVOUNA among papers). Say "given one reference or a closed list of them".
- **`tab:survey` research-paper row.** It reads "34 surveyed, 34 one reference", which looks like a rate. The papers were chosen because they use such a judge, and 10 checked candidates were dropped (`practice_survey.md` §5). Put "---" in the Surveyed cell and add a caption note.
- **`main.tex` l.224.** "Reasoning shrinks the effect by an order of magnitude" compares prompts that also drop the matching instructions. Suggest: "Asking the judge to reason instead of match shrinks the shortfall from 30–67 to 0.5–6 points but does not remove it for Sonnet~5".
- **Venue citations (optional).** These bib entries cite arXiv although the paper has a venue: TriviaQA (ACL 2017), FreshLLMs (Findings of ACL 2024), GAIA (ICLR 2024), Omni-MATH (ICLR 2025), Arena-Hard (ICML 2025), WebWalker and Chinese SimpleQA (ACL 2025), ICE-Score (Findings of EACL 2024), CodeJudge (EMNLP 2024).

---

## Verified clean

### R24-A (`r24a_*.json` → `tables/r24_standard.tex`, §7, §8, abstract, intro, Conclusion)
Every cell of the table matches:

| Grader | One ref minus list | Full list minus list | Differing correct credited (one ref → list) | Wrong credited (one ref → list) |
|---|---|---|---|---|
| s41 SimpleQA, GPT-4.1 | −30.4 [−35.4, −25.3] | +0.3 | 53.0 → 99.2 | 8.9 → 8.9 |
| h41 BrowseComp, GPT-4.1 | −66.8 | −0.2 | 0 → 99.2 | 0 → 3.6 |
| h03 HLE, o3-mini | −66.6 | 0.0 | 0 → 99.2 | 0 → 5.4 |
| sS5 SimpleQA, Sonnet 5 | −34.4 | +0.5 | 46.7 → 99.5 | 10.7 → 8.9 |
| hS5 HLE, Sonnet 5 | −64.9 | +0.2 | 2.3 → 99.8 | 1.8 → 3.6 |

The prose derived from it also checks:
- 47% to 53% and 0% to 2% credited;
- 30 to 34 and 65 to 67 points below the lists;
- 30 to 67 overall, and 0% to 53% credited;
- "within a point" and "within 0.5 points" with the list (largest is +0.50);
- 99% or more credited with the list;
- "at most 3 of 56" wrong answers;
- in the ledger, P-R24A4 falsified at +3.6 and +5.4;
- 396 differing correct, 144 matching correct and 56 wrong answers (total 596);
- 90.6% list accuracy; all 149 questions complete.

### R24-B (`tables/r24_gpt41.tex`, §7)
- Per-model accuracy:

  | Model | List | Blind | One ref |
  |---|---|---|---|
  | Llama-3.1-8B | 69.1 | 63.8 | 65.8 |
  | Haiku 4.5 | 94.6 | 94.6 | 80.5 |
  | Sonnet 5 | 98.7 | 94.0 | 79.9 |
  | Opus 5 | 100 | 100 | 98.0 |

- Pooled minus list: blind −2.5, one reference −9.6, second reference −7.0.
- Credit shifts: 100 → 87.5 (144 answers) and 80.5 → 99.4 (174 answers).
- Prose: "GPT-4.1 by 10", "within 3 points blind".
- Rubric shortfalls carried over: Sonnet 5 −22.3, Opus 5 −15.6, Haiku 4.5 −20.1 (so 16 to 22 points); Haiku 4.5 blind −9.2.

### R24-C (`tables/r24_fix.tex`, §8, Table 1, §6)
- AUROC blind / one ref / list: Sonnet 5 0.938/0.785/0.970; Opus 5 0.936/0.771/0.969; GPT-4.1 0.935/0.872/0.992.
- One ref minus blind: −0.153, −0.165, −0.063. GPT-4.1's interval [−0.133, +0.004] includes zero, as the paper says.
- List minus blind: +0.032, +0.033, +0.057, so "0.03 to 0.06 above blind" holds.
- False rejections with the list: −2.2, −6.3, −2.2, so "do not rise" holds.
- P2 "0.06 to 0.16 for five judges on MACE" holds.

### R24-D (`tables/r24_fix.tex`, §8)
- Sentence: −0.065 AUROC, +18.1 pp false rejections.
- Thinking: −0.090, +14.9.
- Combined: −0.024 [−0.062, +0.006], −0.2 [−7.2, +4.6].
- "36 to 18 pp for Sonnet 5, to 8 pp for Opus 5" holds (36.3 − 28.0 = 8.3); "15 pp with thinking" holds.

### R25 (`r25_*.json` → `tables/r25_types.tex`, §7, ledger)
- Blind minus list: −0.8, −0.5, −0.3, −0.2, −0.3, 0.0, so "within 1 point" holds.
- Reference minus list: −3.0, −6.0, −1.5, −6.2, −0.5, −3.4, so "0.5 to 3" for GPT-4.1 and "3 to 6" for Sonnet 5 hold.
- Intervals exclude zero in 4 of 6 cells (verify-first GPT-4.1's upper bound is 0.0).
- Credit drops for differing correct answers run 0.76 to 8.59 pp, so "1 to 9" holds.
- 7,152 replies = 6 × 1,192.
- Registered verdicts: 10 confirmed, 2 not confirmed, 6 falsified.
- Every other table cell matches except the 90.1 in S7.

### Ledger
- The new rows match the registration outcomes.
- Counts add up as shown in S8.
- Section references in the moved rows (`sec:fix`, `sec:cost`) point at the right sections.

### Prevalence v2 (`tables/prevalence_v2.tex` against `RESULTS.md`)
- Several / unique / unclear:
  - SimpleQA 2/197/1;
  - BrowseComp 0/92/108;
  - HLE 6/141/53;
  - TriviaQA 8/192/0;
  - WebInstruct 11/173/16.
- Rates and Wilson intervals: 1.0 [0.3, 3.6], 0.0 [0.0, 1.9], 3.0 [1.4, 6.4], 4.0 [2.0, 7.7], 5.5 [3.1, 9.6].
- κ (several versus other): 0.00, undefined, 0.10, 0.29, 0.35, so "κ ≤ 0.35" holds.
- Share labeled several by both annotators: 0 / 0 / 1.0 / 1.5 / 4.5%.
- Share labeled several by either annotator: 1.5 / 0 / 15.0 / 8.0 / 18.0%.
- 135 fallbacks = 106 BrowseComp + 29 HLE.
- Intro and §7 ranges ("0% to 4%", "0% to 3%", 5.5%, 18%) match.
- **Mark `\pre` is consistent with the record, with a caveat.**
  - The protocol commit c6f912c is at 17:31:43.
  - The earliest label-file write is at 17:32:58. The label rows carry no timestamps, so the order rests on file modification times plus two recorded pre-protocol connectivity pings.
  - The fallback rule was pre-registered (`PROTOCOL.md` l.124).

### Survey (`practice_survey.md` and `.json`)
- Groups surveyed: 16 + 12 + 4 + 11 = 43.
- Reference-guided: 11 + 11 + 3 + 10 = 35, plus 2 partly.
- Research papers: 34 = 9 + 4 + 2 + 8 + 11.
- Prompts read: 34. Of these, 27 define correctness as matching, 4 partly, 3 no.
- 2 give a closed list and 3 allow wording changes; none credits answers outside the reference; 5 declare the reference correct.
- 46% of 2025 NLG papers, up from under 1%; the CoNaLa result; 24 verbatim templates.
- `tab:survey` is marked † (post hoc), consistent with the survey not being registered.

### Quotes, all found verbatim
- SimpleQA "a factual statement in the answer contradicts the gold target" (vendor `openai_simpleqa_eval.py`, sentence-initial capital adjusted).
- HLE/BrowseComp "based on the precise and unambiguous [correct_answer]" and "do not argue for any answer different than [correct_answer]" (both vendor files and `prompts/hle_browsecomp_judge.txt`).
- MT-Bench phrase (present, but see S5).
- CRAG, Omni-MATH, CompassVerifier, OpenCompass and DeepSeek-R1 lines (`prompts/*`).
- IMO-ProofBench "demonstrates one valid approach" and "prone to be overly punitive" (survey record).
- `app:r24` details:
  - "Any one of the following is a complete correct answer" (`r24_grader_pool.py` l.99);
  - "You are a helpful assistant." with temperature 0.5 (vendor sampler default);
  - GPT-4.1 as the simple-evals grader and o3-mini as the HLE default judge (vendor sources).
- `app:r25` chain-of-thought, verify-first and solve-first prompt text (`r25_judge_types.py` l.35–55).

### Citations
- 66 bibliography entries checked against arXiv abstract pages and venue pages. That covers wei2024simpleqa, wei2025browsecomp, phan2025hle, joshi2017triviaqa, 26 more from the requested list, and 36 other added `@misc` entries.
- Title, authors, year and ID were correct for all 66. The only issues are the duplicate in S13 and the optional venue notes in S14.

### Build
- `latexmk -pdf` was run on a scratch copy of the folder, so build files in the repo were not touched. Exit code 0, 62 pages.
- No undefined citations or references, no overfull boxes, no "Float too large". BibTeX: 0 warnings. Only two hyperref "Token not allowed in a PDF string" warnings.
- The committed `main.log` also has 0 "undefined".

### Layout
- Figure 1 is on page 1.
- The Conclusion ends on page 9; the AI use statement starts on page 9.
- No `\pending` is used; only its `\newcommand` definition remains (l.36).
- Figure 2's caption "every judge on factual questions" holds, because the figure has no GPT-4.1 MACE row.
- Figure 4's caption "all values pre-specified" holds (R20–R25 registrations).

### Cross-section consistency
The abstract, intro, Table 1, §7, §8 and Conclusion agree on:
- 30 to 67 points below the lists;
- 0% to 53% credited;
- within a point with the full list;
- 0.5 to 6 points for the reasoning prompts;
- 10 to 22 points for the rubric.

Limitations match the new scope ("one judge on 40 tasks", "two judges on one pool", "string-matched lists miss some aliases"). The exceptions are B1 to B3.

---

**Verdict: not ready. Five blockers (B1 to B5) need text changes; every one is a one- or two-sentence edit and no number needs recomputing. After those and the S-list, the new numbers match their sources.**
