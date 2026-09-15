# v3 QA review: "The Reference Is Not an Answer Key"

Auditor pass on `main.tex`, `appendix.tex`, `reviews/v3_snapshot.pdf` (36 pp.), `tables/*.tex`, `scripts/make_figures.py`, `../analysis/*.json`, `registration_round24-27.md`, `V3_OUTLINE.md`. Read-only; nothing rebuilt. Line numbers are source lines in `main.tex` / `appendix.tex`.

Registration marks follow the paper's own convention (`main.tex:160`): unmarked = pre-specified, † = post hoc, ‡ = pre-specified re-analysis of an effect with a known direction.

---

## Blockers

### B1. The "full list closes it for LLM graders" claim is contradicted by the paper's own verifier result
**Where:**
- `main.tex:52` (abstract): "giving the grader every correct answer closes it for LLM graders"
- `main.tex:94`: "Giving the grader every correct answer removes it for LLM graders"
- `main.tex:121` (Table 1, Fix row): "A full answer list closes the gap for LLM graders" / "Holds for LLM graders, not for one small verifier"
- `main.tex:213` (Figure 4 title): "and the full answer list closes it."
- `main.tex:301` (conclusion): "The shortfall largely disappears when the grader sees every correct answer"

**Source:** `tables/r26_verifiers.tex` and `../analysis/r26c_general.json` (`conditions/v|reflist`). With the full list, General-Reasoner's verifier is still −24.2 [−28.7, −20.0] points below the lists and credits 30.4% of wrong answers. `registration_round26.md:146-147` records P-R26C2 as **falsified**. This verifier is itself a 1.5B LLM, so "for LLM graders" includes a grader the list did not fix. Table 1 contradicts itself by setting "LLM graders" against "one small verifier". Figure 4a plots this verifier's open circle at −24 directly under a title that says the list closes the gap. The conclusion drops the exception entirely.

**Replace:**
- `main.tex:52`: "…and giving the grader every correct answer closes it for the LLM judges we tested and for one of two RL-reward verifiers."
- `main.tex:94`: "Giving the grader every correct answer removes it for the benchmark graders and one of our two verifiers, but not for General-Reasoner's 1.5B verifier;"
- `main.tex:121`, Key evidence: "A full answer list closes the gap for general-purpose LLM judges and CompassVerifier-3B; correctness prompts shrink it but can admit wrong answers on hard questions (\cref{sec:fix})". Verdict: "Holds except for General-Reasoner's 1.5B verifier"
- `main.tex:213`: "…asking whether the answer is correct shrinks the gap, and the full answer list closes it for all graders but one verifier."
- `main.tex:301`: "The shortfall largely disappears when a general-purpose LLM judge sees every correct answer, although one of two RL verifiers did not follow the list, and shrinks when…"

### B2. Three of the four "correctness prompts" do tell the judge to use or compare with the reference
**Where:**
- `main.tex:91`: "including under prompts that ask only whether an answer is correct."
- `main.tex:154`: "under prompts that ask only whether an answer is correct"
- `main.tex:202`: "The same pattern holds under prompts that ask only whether an answer is correct: across four such prompts, …"
- `appendix.tex:38`: "under a direct prompt and a chain-of-thought prompt that ask only whether the response is correct and contain no instruction to compare"
- `appendix.tex:418`: the chain-of-thought quote, "Think step by step about whether the response is correct", leaves out the prompt's first line.

**Source:** `experiments/tfa-vs-judge/scripts/r25_judge_types.py`. In the reference condition:
- Chain of thought (line 33) begins "Grade the response to the question, using the reference answer."
- Verify first (line 43) says "2. Compare: check the response against the reference answer."
- Solve first (line 52) says "using your own answer and the reference answer."

Only the direct prompt (`r26_judges.py:56`) carries no instruction about the reference. The paper itself says that wording like rubric a's "using the reference to check it" invites comparison (`main.tex:154`, `appendix.tex:38`). This sentence is the paper's answer to the lead author's rubric-wording confound (`V3_OUTLINE.md:45-49`), so misdescribing the prompts undercuts the rebuttal.

The claim does survive if restated. Under the direct prompt, 22.4% (GPT-4.1) and 14.1% (Sonnet 5) of blind-credited differing answers lose credit, against 0.0% of matching ones (`tables/r27_p3.tex`). Also, the verify-first GPT-4.1 difference includes zero: +1.4 [−0.7, +3.2].

**Replace:**
- `main.tex:91`: "…including under a prompt that asks only whether the answer is correct."
- `main.tex:154`: "…under a direct prompt that asks only whether the response is correct, and for answers the judge accepted blind…"
- `main.tex:202`: "The same pattern holds under four prompts that ask whether an answer is correct, one of which gives no instruction about the reference (the other three tell the judge to use or compare with it): GPT-4.1 and Sonnet~5 withdraw credit from 1\% to 22\% of the differing correct answers they accepted blind, and from at most 0.7\% of matching ones\reana{}; under the direct prompt alone, from 22\% and 14\% (\cref{app:r27})."
- `appendix.tex:38`: "…under a direct prompt that asks only whether the response is correct and says nothing about how to use the reference, and under chain-of-thought, verify-first, and solve-first prompts that ask the judge to use the reference, although reasoning shrinks it (\cref{app:r25,app:r26});…"
- `appendix.tex:418`: "\emph{Chain of thought}: ``Grade the response to the question, using the reference answer. […] Think step by step about whether the response is correct''."

### B3. Post hoc results appear unmarked in the main text, which the convention reads as pre-specified
**Where and source:**
- `main.tex:262`: "A registered blind-then-reveal protocol … left grading below blind for most open judges; keeping the higher of the blind and referenced scores protects grading largely by construction and gives back accuracy when the answer is unique"
  - The grading readout is post hoc: `appendix.tex:536` "…except for Qwen2.5-14B (Reveal − ref. column).\ph".
  - The max rule is post hoc: `appendix.tex:538` "The max rule (post hoc)"; `tab:protocols` caption "every Reveal − ref. and Max rule value … is post hoc".
  - `main.tex:292` (Limitations) itself says "the max rule was chosen post hoc", so the unmarked sentence contradicts the Limitations.
- `main.tex:157`: "Registered labels, model-read labels, and boxed replies alone give the same sign for every grading AUROC change of the open judges and GPT-4.1; only the size changes."
  - Post hoc: `tab:labelings-gnm` caption "Qwen2.5-7B's replication value under the registered checker is pre-specified; the rest are post hoc".
  - The claim is also false for Mistral-7B, an open judge in the same table: registered −0.10 [−0.13, −0.06] against boxed-only +0.01 [−0.05, +0.07] (`tables/labelings_gnm.tex`).
- `main.tex:181`: "The direction holds under every labeling; boxed replies alone give the smallest falls." Post hoc, same source.

**Replace:**
- `main.tex:262`: "A registered blind-then-reveal protocol, in which the judge scores blind and then rescores with the reference, left grading below blind for most open judges;\ph{} keeping the higher of the blind and referenced scores, a rule chosen post hoc, protects grading largely by construction and gives back accuracy when the answer is unique;\ph{} and the full-credit instruction did little for Qwen2.5 judges up to 7B (\cref{app:mitigation})."
- `main.tex:157`: "Registered labels, model-read labels, and boxed replies alone give the same sign for every grading AUROC change of the four core open judges and GPT-4.1; only the size changes.\ph{}"
- `main.tex:181`: "The direction holds under every labeling, and boxed replies alone give the smallest falls.\ph{}"

---

## Should fix

### S1. `main.tex:253`: "cut the factual rise in false rejections for Sonnet 5 by half or more"
**Source:** The rise with one reference is +35.6 pp (`r24c_sonnet.json` `FR_ref_minus_blind` 0.35634). The sentence alone gives +18.1 (`r24d_think_sentence.json` `sentence_alone/FR_change` 0.180594), a cut of 49.3%, which is not "half or more". Thinking alone gives +14.9 (a 58% cut).

**Replace:** "The full-credit instruction cut the factual rise in false rejections for Sonnet~5 by about half and a thinking mode by more than half, and together they left no measurable rise (\cref{app:acceptance,app:r24})."

### S2. `main.tex:257`: "We sampled 200 HLE questions, whose answers are unique"
**Source:** These are the same 200 questions as the second prevalence audit (`appendix.tex:482`). That audit labels 6 of 200 (3.0%) as having several answers, and 15.0% by either annotator (`tables/prevalence_v2.tex`, HLE row). `main.tex:225` itself says "0% to 3% of sampled … HLE questions admit several". The two sections contradict each other.

**Replace:** "We sampled 200 HLE questions, almost all with a single correct answer (6 admit several in our audit; \cref{app:prevalence}), and graded two models' answers to them, almost all wrong."

### S3. `main.tex:256`: "There, the instruction to match is what keeps wrong answers out, and removing it can let a judge overrule the reference." (also `appendix.tex:484`: "and the instruction to match keeps a judge from overruling it")
**Source:** `tables/r27b_hle.tex`. Without the match instruction, Sonnet 5 credits 0.5% (direct) and 1.0% (solve first) of wrong answers with the reference, against 0.0% for the verbatim judge. So for Sonnet 5 the match instruction is not what keeps wrong answers out. Only GPT-4.1 overrules (17.3%, 25.9%). The conditions also differ in more than the match clause.

**Replace:**
- `main.tex:256`: "There, the instruction to match can be what keeps wrong answers out: without it, one of our two judges overruled the reference."
- `appendix.tex:484`: "…so on these questions the reference is the judges' main evidence, and without the instruction to match GPT-4.1, though not Sonnet~5, often overrules it."

### S4. `main.tex:181`: registration marks and labels for the P2 numbers
**Quote 1:** "Qwen2.5-7B scores 28% of them 3 or below with the reference on the replication pool, against 0.4% blind (\cref{app:grid})."

**Source 1:** `r4_results.json` `repl_false_reject/le3` (ref 0.281, blind 0.004, 93 tasks), which uses the exact scorer and the registered labels (`appendix.tex:204`). The exact scorer is the paper's own example of a ‡ re-analysis (`appendix.tex:106`), so the number needs ‡. It is also on registered labels, while `main.tex:157` says the constructed pools use any-format labels.

**Quote 2:** "falls by 0.06 to 0.16 on factual questions\ph{}"

**Source 2:** Most of this range is pre-specified, and only phi-4's value is post hoc:
- Sonnet 5: −0.1531 (`r8_sonnet_results.json` `pools/mace/oracle/G_nm`; P-R8A3 confirmed)
- Opus 5: −0.1645 (`r19a_opus_results.json`)
- Qwen2.5-7B: −0.0795 (`r4_results.json` `grading/mace/G_nm/ref_minus_blind`); `tab:protocols` caption lists it as pre-specified
- phi-4: −0.0595 (`r4_posthoc_results.json`), post hoc

**Replace:** "Correct answers that differ from the reference are rejected more often: under the registered labels, Qwen2.5-7B scores 28\% of them 3 or below with the reference on the replication pool, against 0.4\% blind\reana{} (\cref{app:grid}). Their grading AUROC against wrong answers falls by 0.08 to 0.16 for Qwen2.5-7B, Sonnet~5, and Opus~5 on factual questions and by 0.06 for phi-4,\ph{} and by 0.17 to 0.27 for the four open judges on the constructed pools\ph{} (\cref{fig:onevsseveral}b)."

### S5. The P2 verdict omits a registered not-confirmed cell (Opus 5, replication pool)
**Where:**
- `main.tex:187`: "P2 holds for Sonnet 5, Opus 5, Qwen2.5-7B, and phi-4 on factual questions and for the four open judges on the constructed pools; GPT-4.1's factual interval includes zero."
- `main.tex:115` (Table 1): "Holds for all judges but GPT-4.1 on factual questions"

**Source:** `r19a_opus_results.json` `pools/repl/lenient/G_nm` = −0.0151 [−0.0385, +0.0086]. The ledger records this as **not confirmed** ("Opus 5 on the Sonnet 5 subsamples", `appendix.tex:171`), and Figure 2b plots it crossing zero. "All judges" in Table 1 also covers Qwen2.5-14B and gemma-2-9b, which were never run on factual questions.

**Replace:**
- `main.tex:187`: "P2 holds for Sonnet~5, Opus~5, Qwen2.5-7B, and phi-4 on factual questions and for the four open judges and Sonnet~5 on the constructed pools; the interval includes zero for GPT-4.1 on factual questions and for Opus~5 on the replication pool (\cref{app:ledger})."
- `main.tex:115`, Verdict: "Holds except GPT-4.1 on factual questions and Opus~5 on the replication pool"

### S6. `main.tex:234`: "Written reasoning helps GPT-4.1 but, by our registered test, not Sonnet 5, which keeps a residual pull under every prompt."
**Source:** The registered test P-R26A3 compared the direct prompt with chain of thought only: Sonnet 5 −10.1 against −6.0 (`registration_round26.md:104`). Solve-first gives Sonnet 5 −3.4 [−5.7, −1.2] (`tables/r25_types.tex`). That is 6.7 points better than direct, outside the registered 5-point band, and Figure 4a shows it. "Not Sonnet 5" therefore overstates what the test showed.

**Replace:** "Chain-of-thought reasoning closes most of GPT-4.1's gap but, by our registered test, not Sonnet~5's, which keeps a residual pull under every prompt."

### S7. `main.tex:252`: "letting the judge solve the question first gave the smallest grading loss (AUROC −0.04 and −0.05 against blind)"
**Source:** On the same 40 tasks, Sonnet 5 with thinking plus the full-credit sentence gives −0.024 [−0.062, +0.006] (`r24d_think_sentence.json` `combined/G_change`; plotted as the triangle in Figure 4b). That is smaller than solve-first's −0.047, and the next sentence of the paragraph reports it.

**Replace:** "…letting the judge solve the question first gave the smallest grading loss of the three correctness prompts (AUROC $-0.04$ and $-0.05$ against blind)…"

### S8. `main.tex:225`: "0% to 3% … admit several, a lower bound from LLM annotators who agreed poorly (\cref{app:prevalence}), so their own leaderboards move by a few points at most."
**Source:** `tables/prevalence_v2.tex` and `appendix.tex:91`.
- Only the fallback rule is conservative. The adjudicated labels themselves are not a bound.
- BrowseComp has 108 of 200 items labeled unclear.
- HLE reaches 15.0% by either annotator, and 6.0% had the fallbacks gone the other way; κ ≤ 0.35.
- The leaderboard statement is an unmarked extrapolation; no benchmark leaderboard was re-scored.

**Replace:** "…0\% to 3\% of sampled SimpleQA, BrowseComp, and HLE questions admit several, probably an underestimate from LLM annotators who agreed poorly and left most BrowseComp items unclear (\cref{app:prevalence}), so we expect their own leaderboards to move by a few points at most.\ph{}"

### S9. `main.tex:258`: "but in a sample we read, most of these credits went to a different final answer.\ph{}"
**Source:** `registration_round27.md:120-123` and `r27b_posthoc_gpt41_sonnet.json` (`solve_ref_fa_reply_says_reference_wrong` = [40, 0.412]). The reading covered 10 of the at least 40 GPT-4.1 solve-first false acceptances whose reply says the reference is wrong. It was not a sample of all credits and did not include the direct prompt.

**Replace:** "…but most of the 10 we read, among GPT-4.1's solve-first credits that call the reference wrong, went to a different final answer.\ph{}"

### S10. `main.tex:53`: "Across eleven LLM judges, two verifiers, …"
**Source:** The count is carried over from v2 (`D-iclr-v2/main.tex:51`, written before Opus 5, Haiku 4.5, and o3-mini were added). The condensed appendix alone reports scores from 15 LLM judges: Qwen2.5-1.5B, 3B, 7B, and 14B; phi-4; gemma-2-9b; Mistral-7B; Ministral-8B; Qwen3-8B and 14B; Sonnet 5; Opus 5; Haiku 4.5; GPT-4.1; o3-mini. The extended appendix pool table (`appendix_extended.tex:25-31`) adds Llama-3.1-8B as a synthetic-grid judge.

**Replace:** "Across more than a dozen LLM judges, two RL-reward verifiers, and a ledger of every registered prediction, …" Alternatively, state an exact count that the authors verify against `tab:pools`.

### S11. `main.tex:166-167`: "under Qwen2.5-7B, phi-4, and Sonnet 5 … All twelve registered cells went as predicted"
**Source:** The twelve cells are two judges (Qwen2.5-7B, phi-4) × two rubrics × three readouts (`D-iclr-v2/main.tex:166`; `appendix_extended.tex:167`, "12 of 12 cells"). Sonnet 5 is not among them, but placing the sentence after the three-judge list implies it is.

v2 also reported, in this same place, that the registered ordering of the swap by numeric distance failed ("Distance gradient … falsified", `appendix.tex:156`). v3 dropped that sentence, although the Table 1 caption promises that failures "near each row are in the cited sections".

The range itself is correct:
- Gains of 3.0–5.3 run from Sonnet 5 at +3.04 (`tables/rotation_exact.tex`) to Qwen2.5-7B's exact-scorer +5.25 (`tables/r4_rotation.tex`).
- Losses of 2.7–5.4 run from −2.66 to −5.41.
- Both are rubric a only; rubric b gives Qwen2.5-7B +6.34.

**Replace:** "…while correct text that matches neither reference barely moves (rubric~$a$; \cref{app:rotation}).\reana{} The twelve registered cells for Qwen2.5-7B and phi-4 went as predicted, although a registered ordering of the swap by numeric distance failed (\cref{app:ledger}); on nine MathConstraint puzzles…"

### S12. `main.tex:176` (Figure 2 caption): "Registration status per value in \cref{app:ledger}."
**Source:** The condensed ledger (`appendix.tex:103-181`) contains only the totals table and the list of failures, with no per-value registration status. That status lives in the captions of `tab:labelings-gnm` (`appendix.tex:208`) and `tab:protocols` (`appendix.tex:506`).

**Replace:** "Registration status per value is given in the captions of \cref{tab:labelings-gnm,tab:protocols}."

### S13. `main.tex:310` (Reproducibility): "\Cref{app:setup} specifies every pool, judge, prompt, and scorer, and \cref{app:ledger} lists each prediction with its registration type and outcome."
**Source:**
- `appendix.tex:13` defers the pool table to the extended appendix.
- `appendix.tex:41` says the verifiers "use their own templates", which are not quoted.
- The benchmark-grader templates are not reproduced.
- `appendix.tex:110` says the condensed ledger lists only failures, and "the extended appendix lists every registered experiment".

**Replace:** "\Cref{app:setup} and the appendices it cites specify the judges, prompts, and scorers, and \cref{app:ledger} gives the verdict totals and every registered prediction that was not confirmed; the extended appendix in the supplement tabulates every pool and lists every prediction with its registration type and outcome."

### S14. `main.tex:300` (conclusion): "Graders shipped with benchmarks and used for RL rewards inherit this failure wherever answers are open, in large part because they are told to match."
**Source:**
- Grader and verifier shortfalls were measured only on 149 MACE River and Language questions (`appendix.tex:379`).
- The paper reports small effects on code (`appendix.tex:554`).
- CompassVerifier's failure comes with a prompt that declares the answer "ALWAYS CORRECT" rather than a match instruction (`appendix.tex:456`).

**Replace:** "On the multi-answer factual questions we tested, graders shipped with benchmarks and used for RL rewards inherit this failure, in large part because they are told to match."

### S15. `appendix.tex:456` does not disclose the interim inspection recorded in the registration
**Source:** `registration_round26.md:136-140`, "Note on interim inspection". Credited-answer shares were counted in the partial General-Reasoner output (1,011 of 1,192 generations) before the registered producer ran. `appendix.tex:106` says every confirmatory prediction was committed before its analysis. That remains true, but the appendix mentions only Amendment 3.

**Replace:** Append to `appendix.tex:456` after "(Amendment 3)": "; to answer a status question we counted credited answers in the partial General-Reasoner output (1,011 of 1,192 generations) before the run finished, without changing any setting (registration note)".

---

## Nits

- **N1. `appendix.tex:328`**: "−0.165 [−0.223, −0.110] on MACE". `tab:r24-fix` prints −0.164 for the same quantity (`r24c_opus.json` `G_ref_minus_blind` −0.164458; `r19a_opus_results.json` −0.1645). **Replace:** "$-0.164$ \ci{-0.223}{-0.110}".
- **N2. `appendix.tex:331`**: "−0.090 [−0.140, −0.051]" against `tab:r24-fix` "−0.091 [−0.140, −0.050]" (`r24d_think_sentence.json` `thinking_alone/G_change` −0.090534 [−0.140209, −0.050488]). **Replace:** "$-0.091$ \ci{-0.140}{-0.050}".
- **N3. `registration_round24.md:141`** (hS5 row) gives the full-list differing-correct credit as "99.8%". The JSON (`r24a_hS5.json` `pooled/nonmatch_correct_credited_reflist` 0.997475) and `tab:r24-standard` both give 99.7%, so the paper is right. The registration file ships in the supplement, so note the typo in the extended ledger rather than editing a timestamped document.
- **N4. `main.tex:154`**: "All prompts are in \cref{app:setup}." The verifier templates and verbatim benchmark-grader templates are not reproduced there (`appendix.tex:41`). **Replace:** "Prompts are in \cref{app:setup} and the appendices it cites; verifier and benchmark-grader templates are in the supplement."
- **N5. `main.tex:289`**: "\textsc{MACE}'s answer lists miss 2.3\% to 8.1\% of correct answers". The audit measured how often a model names a valid answer missing from the list (`appendix.tex:188`). **Replace:** "a model's valid answer is missing from \textsc{MACE}'s lists 2.3\% to 8.1\% of the time".
- **N6. `main.tex:113`** (Table 1, P1 verdict): "near zero on arithmetic with a thinking mode". Sonnet 5 asked to reason with thinking off is also near zero (+0.28 / −0.20, `appendix.tex:248`). **Replace:** "Holds; near zero on arithmetic when the judge reasons or thinks first".
- **N7. `main.tex:215`** (Figure 4 caption, b): the triangle marker (Sonnet 5 with thinking plus the full-credit sentence, `r24d`) appears only in the legend. **Replace:** "\textbf{(b)}~Grading AUROC change against blind on the 40-task \textsc{MACE} subsample (triangle: Sonnet~5 with thinking and the full-credit sentence)."
- **N8. `main.tex:51` and `main.tex:92`**: "under-credit correct answers by 30 to 67 points". The quantity is pooled accuracy minus answer-list accuracy (`tables/r24_standard.tex`, `r26_verifiers.tex`), not credit for correct answers, which falls 47 to 100 points for differing answers. **Replace:** "score answers 30 to 67 points below their accuracy by the answer lists".
- **N9. `appendix.tex:536`**: "except for Qwen2.5-14B (Reveal − ref. column)". `tab:protocols` mixes scorers, so the Reference and Reveal − ref. columns cannot be added. For Qwen2.5-14B, −0.17 + 0.12 = −0.05, while `r16_protocol_grading.json` `kpool/Qwen2.5-14B/grading_any_format/reveal_minus_blind` is −0.0098. **Replace:** "…except for Qwen2.5-14B ($-0.01$; extended appendix)".
- **N10. `main.tex:246`**: CompassVerifier-3B's full-list result is cited only to `\cref{app:r24}`, but its numbers are in `app:r26`. **Replace:** "(\cref{fig:graders}b; \cref{app:r24,app:r26})".
- **N11. Layout (PDF pp. 1-9):**
  - Checks that pass: the main text ends on p. 9 (Conclusion, `main.aux` `sec:conclusion` p. 9), Figure 1 is on p. 1, Table 1 renders cleanly on p. 3, and no overfull boxes appear in `main.log`.
  - Split paragraph: the P3 verdict breaks across pp. 4-5 around Figures 2 and 3, leaving about four blank lines at the bottom of p. 5. Placing Figure 3 with `[t]` on p. 5 and Figure 2 earlier, or moving `fig:reasoning` above the P3 heading, would remove the split.
  - Appendix tables: Tables 18 and 19 on pp. 32-33 are shrunk by `adjustbox` to about 6 pt and are barely legible. Shortening their column heads ("FR change (pp)", "FA change (pp)") would let them run at `\footnotesize`.
  - Figures: Figure 4's tick labels are about 7.8 pt, legible.
- **N12. `main.tex:304`**: "we checked every quoted number against those outputs". Re-run the check after the fixes above; as written the sentence is contradicted by S1.
- **N13. `main.tex:220`**: "We asked Llama-3.1-8B-Instruct, … for one answer". Llama's answer is its first stored sample (`appendix.tex:350`). **Replace:** "We took one answer from each of Llama-3.1-8B-Instruct (its first stored sample), Claude Haiku~4.5, Sonnet~5, and Opus~5…"
- **N14. `main.tex:168`**: "It mostly vanishes when the reference is written as an expression or masked inside a worked solution". The masking suite measures the margin, not the swap (`tab:masking`). **Replace:** "The reference's pull (the margin) mostly vanishes when…"
- **N15. `main.tex:227`**: "in which 5.5\% to 18\% of questions admit several answers". The 18% is the either-annotator sensitivity bound (`tables/prevalence_v2.tex`). **Replace:** "5.5\% after adjudication and up to 18\% by either annotator".
- **N16. `main.tex:228`**: "there our own effects are small (\cref{app:code})". There is no proof experiment. **Replace:** "in our code experiments the effects are small".

---

## Checked and consistent (no change needed)

- **Abstract, intro, §5–§7 figures and roundings:** swap 3–5; 30–34 and 65–67 (`r24a_*`); 6% and 0% (`r26c_*`); 17 and 10 short, 5 and 2 blind (`r26a_*`: −17.4, −10.1; −5.4, −1.7); 0.5–6 (`r25_*`); recoveries of 35 and 53 (`hle_edit_minus_hle` 0.354, 0.525); 10–22 and three within 3 (`r20c`, `r21a`, `r24b`); redraw shifts of 23–38 and regrade within about 3 (`r22b_*`, `r23a_*`, max 3.1).
- **§6 acceptance:** 19%–83% (`r20_retest`, `r21a_mace_acceptance` 0.833); 2 of 282 against 78; 1%–22% and at most 0.7% (`r27a_*`).
- **§8 fixes and RL estimate:** within a point and at most 3 of 56 (`r24a_*`, `r26c_compass`); solve-first −0.040 / −0.047, false acceptances ≤ 3.2, false rejections 4.7–7.4 (`r26b_*`); 17% / 26% / ≤ 1% (`r27b_*`); the 4–12% RL estimate (5.5–18% × 396/540 × 0.942).
- **Figure 1:** 10.0, 2.9, 9.3; the 6.4 swap matches `appendix.tex:44`.
- **Figure 3** values and **Figure 4** data paths (`make_figures.py:887-1003`) match the JSON. Figure 4's "all values pre-specified" holds.
- **Ledger:**
  - Round totals: `tab:ledger-totals` and `tab:ledger-failures` agree with the registration outcome sections for R24 (36: 33/1/2), R25 (18: 10/2/6), R26 (30: 21/0/9), and R27 (14: 11/0/3).
  - Failure rows: every R24–R27 failure row matches its prediction by prediction.
  - Row counts: the rows sum to the caption's 14 not confirmed, 37 falsified, 17 split, 18 not evaluable, 2 not scored, and 3 excluded.
  - Pre-R24 total: the 290 through round 26 matches `appendix_extended.tex:144`.
- **Cross-references:** every other `\cref` from `main.tex` into the appendix lands on supporting content.

---

## Verdict

The numbers in v3 are in good shape. Almost every main-text value traces to its JSON with correct rounding, and the round 24–27 ledger agrees with the registrations prediction by prediction. What remains is wording and marks, not data. Three blockers should be fixed before submission. The abstract, intro, Table 1, Figure 4 title, and conclusion claim the full list fixes "LLM graders", while the paper's own 1.5B verifier stays 24 points short. The robustness claim about "prompts that ask only whether an answer is correct" misdescribes three of the four prompts, which tell the judge to use or compare with the reference; only the direct prompt fits, and it does support P3. Several post hoc analyses, including the max rule that the Limitations call post hoc, appear unmarked, which the paper's convention reads as pre-specified. The should-fix items are mostly scope words and quantifiers that each fail against a single number ("by half or more" at 49%, "whose answers are unique" against 3%, "smallest grading loss", "lower bound", "eleven judges", "twelve cells"), plus two cross-references that promise content the condensed appendix no longer holds. With the blockers and should-fix items applied, all text edits needing no new experiments, the paper's claims would match its evidence.
