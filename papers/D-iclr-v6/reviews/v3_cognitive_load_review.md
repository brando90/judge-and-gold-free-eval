# v3 main text: cognitive-load and flow review

Reviewer role: ICLR area chair / scientific editor. Scope: `main.tex` from `\begin{abstract}` to the Conclusion (PDF pages 1–9), read against the rebuilt `main.pdf` and against `appendix.tex` for fact preservation. Read-only review; nothing in the paper was modified.

**Source state.** Based on the current `main.tex`, i.e. after the recent rewrites of §2 ("Answer extraction"; "Measurements and conventions", now a definition list), §3 (three short paragraphs, `fig:rotation-pool` promoted into the main text), §4 ("Several correct answers", claim first, per-judge attributions left to the figure), §7 ("What did not help" folded in), the simplified `fig:onevsseveral` caption, and the tightened Related work, Limitations and Conclusion. Those passes removed most of the load they targeted. What remains is concentrated in §5, §6 and §7, plus three problems the promotions and simplifications introduced (units 22, 23, 26).

Figures are referred to by label, since the promotion of `fig:rotation-pool` renumbered them: `fig:concept` = Fig. 1, `fig:rotation-pool` = Fig. 2, `fig:onevsseveral` = Fig. 3, `fig:reasoning` (acceptance) = Fig. 4, `fig:graders` = Fig. 5.

**Scales.** Load 1 (easy) … 5 (overloaded). Flow 1 (smooth) … 5 (jarring). Sentence lengths and number counts are measured on cleaned LaTeX (each citation or `\cref` counted as one token, `\%` handled correctly).

**Page budget.** The conclusion ends at line 485, the last line of page 9: there is no slack. Every rewrite is costed in lines (≈97 characters of body text per line; the abstract ≈80). The full set below is **net ≈ 0**, funded mainly by trimming two captions and the Table 1 columns. Figure 1 must also stay on page 1, so the abstract rewrite is length-neutral by construction (−7 characters).

**Caption standard applied** (per the editorial instruction): title, what is plotted, the conditions the reader needs, and nothing already in the Setup, the plot legend, or the appendix. Units 22, 30 and 35 apply it to the three captions that still carry such material; `fig:concept` and `fig:onevsseveral` already meet it.

---

## 1. Score table

| # | Unit | Load | Flow | Action | Δ lines |
|---|------|------|------|--------|---------|
| 1 | Abstract | 4 | 3 | rewrite | −0.1 |
| 2 | `fig:concept` caption | 2 | 2 | no change | — |
| 3 | Intro ¶1 (35/80 example) | 2 | 1 | no change | — |
| 4 | Intro ¶2 (survey, scope) | 3 | 3 | rewrite | +0.3 |
| 5 | Intro "What the reference could be doing" | 2 | 2 | no change | — |
| 6 | P1 list item | 1 | 1 | no change | — |
| 7 | P2 list item | 2 | 2 | no change | — |
| 8 | P3 list item | 2 | 2 | no change | — |
| 9 | Intro "What we find" | 4 | 3 | rewrite | +0.4 |
| 10 | Table 1 + caption | 3 | 2 | rewrite (cells, caption, column widths) | **−1.0 to −2.0** |
| 11 | §2 "Tasks" | 3 | 2 | rewrite | 0.0 |
| 12 | §2 bullet "Candidates" | 1 | 1 | no change | — |
| 13 | §2 bullet "Conditions" | 1 | 2 | no change | — |
| 14 | §2 bullet "Open judges" | 2 | 2 | no change | — |
| 15 | §2 bullet "API judges" | 2 | 3 | rewrite (restores the n/a reason) | +0.2 |
| 16 | §2 bullet "Benchmark graders" | 3 | 3 | rewrite | +0.1 |
| 17 | §2 bullet "Prompts" | 2 | 2 | no change | — |
| 18 | §2 "Answer extraction" ¶1 | 3 | 2 | rewrite (one sentence) | +0.2 |
| 19 | §2 "Answer extraction" ¶2 | 3 | 2 | rewrite | **−0.6** |
| 20 | §2 "Measurements" definition list | 2 | 2 | no change | — |
| 21 | §2 "Measurements" prose tail | 3 | 3 | rewrite | +0.3 |
| 22 | `fig:rotation-pool` caption (new in §3) | 3 | 2 | rewrite | **−0.5** |
| 23 | §3 ¶1 (swap size, registration) | 3 | 2 | rewrite (mark placement) | 0.0 |
| 24 | §3 ¶2 (wording; expression/masked) | 2 | 2 | no change | — |
| 25 | §3 ¶3 ("Does the problem fade…") | 2 | 2 | no change | — |
| 26 | `fig:onevsseveral` caption | 2 | 3 | no change (see unit 15) | — |
| 27 | §4 "Several correct answers" ¶1 | 3 | 2 | rewrite (scope, not load) | +0.2 |
| 28 | §4 "Several correct answers" ¶2 (relabeling) | 2 | 2 | no change | — |
| 29 | §4 "One correct answer" | 3 | 2 | rewrite | +0.1 |
| 30 | `fig:reasoning` caption | 3 | 2 | rewrite | **−0.9** |
| 31 | §4 "Verdict" (now split in two) | 2 | 2 | no change | — |
| 32 | §5 "What an inability to verify would predict" | 3 | 2 | rewrite | +0.1 |
| 33 | §5 "Answers the judge accepts without a reference" | 3 | 2 | rewrite | −0.1 |
| 34 | §5 "It is not score noise" | 4 | 3 | rewrite | +0.1 (+1.0 for the preferred split) |
| 35 | `fig:graders` caption | 3 | 2 | rewrite | **−1.0** |
| 36 | §5 "Verdict" | 3 | 2 | rewrite | +0.2 |
| 37 | §6 "Graders shipped with benchmarks" | 5 | 3 | rewrite | +0.8 |
| 38 | §6 "Who should care: reuse" | 5 | 3 | rewrite | +0.4 |
| 39 | §6 "What sets the size" | 5 | 2 | rewrite | +0.4 |
| 40 | §7 "Give the judge every correct answer" | 4 | 2 | rewrite | +0.6 |
| 41 | §7 "When the answers cannot be listed" | 4 | 3 | rewrite | +0.4 |
| 42 | §7 "Questions beyond the judge" | 3 | 2 | rewrite | +0.3 |
| 43 | §7 "A recipe" (4 bullets) | 2 | 2 | no change | — |
| 44 | §8 "Reference-guided judging" | 3 | 2 | rewrite (light) | 0.0 |
| 45 | §8 "Single references and many correct answers" | 2 | 2 | no change | — |
| 46 | §8 "Judge biases and optimization" | 2 | 2 | no change | — |
| 47 | §9 "Labels" bullet | 2 | 2 | no change | — |
| 48 | §9 "Tasks" bullet | 2 | 2 | no change | — |
| 49 | §9 "Judges and prompts" bullet | 2 | 2 | one-phrase alignment | 0.0 |
| 50 | §9 "Mechanism and registration" bullet | 2 | 2 | no change | — |
| 51 | §10 Conclusion | 3 | 2 | rewrite | +0.1 |

---

## 2. Unit-by-unit

### 1. Abstract — load 4, flow 3 — Δ −0.1 line

Causes: 270 words in 8 sentences (mean 34 w/s); one sentence of **102 words** carrying findings (1), (2) and (3), five numbers and an inference; 14 numbers; a 42-word opener separating subject from predicate with a three-item list plus an appositive. Flow: the setting ("more than a dozen judges on constructed tasks, MACE, and MATH-500, with a complete preregistration ledger") arrives second from last, after the reader has already carried three findings and two benchmark results.

<!-- REWRITE: ABSTRACT -->
```latex
\begin{abstract}
LLM judges often grade with a reference answer, including the graders that ship with SimpleQA, BrowseComp, and Humanity's Last Exam.
The premise is that the reference acts as an answer key: a correct response should score the same whichever correct answer is shown.
On questions with several correct answers the premise fails.
We test it with more than a dozen judges on constructed tasks, MACE, and MATH-500, with a complete preregistration ledger.
(1) Swapping the reference between two correct answers moves the score of identical text by about 3 to 5 points out of 10.
(2) Correct answers that differ from the reference are graded worse against wrong answers, in the same direction under every answer-labeling scheme we tried.
(3) Judges reject such answers even after accepting them without a reference: for two frontier judges, 117 of 843 accepted answers score 3 or below once the reference is shown, against 2 of 843 on a repeated call without it, so an inability to verify them cannot alone explain the effect.
Those benchmarks rarely contain such questions, but run verbatim on 149 factual questions that do, with a reference drawn at random from each answer list, their graders score four models 30 to 67 points below their answer-list accuracy.
Much of this comes from the instruction to match: asked instead whether the answer is correct, judges shrink the gap on questions they can answer.
Given the full answer list, the benchmark graders come within a point of answer-list accuracy.
On such questions, a low score from a reference-guided judge does not reliably mean the answer is wrong.
\end{abstract}
```
Moved: nothing leaves the paper; the "more than a dozen judges … ledger" sentence moves from position 7 to position 4. 1610 characters against 1617, so Figure 1 keeps its place on page 1.

### 2. `fig:concept` caption — no change (load 2, flow 2). Meets the caption standard: title, what each panel shows, the selection caveat, and a pointer for the full reply.

### 3. Introduction ¶1 — no change (load 2, flow 1). Thirteen numbers, each anchored to a named condition in the worked example.

### 4. Introduction ¶2 — load 3, flow 3 — Δ +0.3 line

Causes: a 42-word survey sentence with three coordinated clauses; "which optimization exploits" compresses a literature into three words; two topic switches, and "The failure is not about math" names a failure the reader has not been given yet (§1 so far shows one example).

<!-- REWRITE: INTRO-P2 -->
```latex
Reference-guided judging is how many benchmarks are scored.
The judge used by BrowseComp and Humanity's Last Exam (HLE), for example, is told ``do not argue for any answer different than [correct\_answer]''~\citep{wei2025browsecomp,phan2025hle}.
Of 43 benchmarks, evaluation libraries, platforms, and RL reward pipelines we checked, 35 grade with a single reference or a closed list, and none of the judge prompts we could read tells the judge to credit a correct answer outside it (\cref{app:survey}).\ph{}
The same judges choose among sampled answers (\emph{selection}) and serve as reward signals, which optimization exploits~\citep{gao2022scaling}.
The problem is not confined to math: factual answers, agent outputs, informal proofs, and RL rewards on general reasoning data have no formal checker, which is why LLM judges grade them. We use arithmetic tasks only as a controlled testbed, because a checker lists every correct answer, and factual questions because benchmark graders operate there.
```
Moved: nothing. `(\emph{selection})` names the term that §2 ("selection accuracy") and §4 ("Selection among sampled answers") both use undefined; it is the first thing to drop if the budget tightens (−0.2 line).

### 5.–8. "What the reference could be doing", P1, P2, P3 items — no change (load 1–2, flow 1–2).

### 9. "What we find" — load 4, flow 3 — Δ +0.4 line

Causes: 181 words in 5 sentences (mean 36 w/s); a 58-word sentence with two fronted participial phrases before its subject; a 64-word prior-work sentence chaining three citation groups with semicolons and closing on "whereas"; two hedges in one sentence. Flow: findings and prior-work positioning share one paragraph.

<!-- REWRITE: WHAT-WE-FIND -->
```latex
\paragraph{What we find.}
All three predictions hold (\cref{tab:summary}), and the effect matters in practice.
We ran the graders of SimpleQA, BrowseComp, and HLE as their authors configure them, on questions with several answers, with a reference drawn at random from each answer list.
They credit 0\% to 53\% of correct answers that differ from the reference and score four models 30 to 67 points below their answer-list accuracy (\cref{sec:cost}).
Much of this comes from the instruction to match: asking whether the answer is correct shrinks the gap where the judge can answer the question, although on harder questions one of our two judges then accepted wrong answers.
Given the full answer list, the benchmark graders come within a point of answer-list accuracy (\cref{sec:fix}).
Prior work comes close without isolating this failure.
\citet{fixation2025} name ``solution fixation'' but measure it with flawed solutions rewritten in the reference's style, and \citet{judgingref2026} and \citet{krumdick2025nofreelabels} replace the reference with a wrong one.
Question-answering evaluation has long under-credited correct answers missing from a gold list~\citep{min2020ambigqa,kamalloo2023evaluating}; here the list is complete and the judge still favors the answer it was shown.
```

### 10. Table 1 and caption — load 3, flow 2 — Δ **−1.0 to −2.0 lines** (confirm in a rebuild)

Causes: the Verdict column is 2.7 cm, so the P2 verdict wraps to seven short lines and reads as a semicolon chain; "Inability to verify, alone" is a fragment parsed twice; "those benchmarks" has no antecedent inside the table; the Fix verdict answers only half of its own Key-evidence cell; the caption's "failed near each row" is unclear, and by the caption standard the caption should point, not explain. The cheapest load reduction is typographic — 0.1 cm each from *Rules out* and *Key evidence* into *Verdict* — which removes wrapped lines from the two tallest rows. The table stays word-only.

<!-- REWRITE: TABLE1 -->
```latex
\begin{table}[t]
\centering
\small
\caption{\textbf{What each prediction tests and what we observed.} Each row's numbers, intervals, and failed registered predictions are in the cited section and the ledger (\cref{app:ledger}).}
\label{tab:summary}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.12}
\begin{tabular}{L{2.9cm}L{1.9cm}L{4.9cm}L{2.9cm}}
\toprule
Question & Rules out & Key evidence & Verdict \\
\midrule
\textbf{P1} Does the score follow the reference? & Answer key & Identical text moves 3--5 points when the reference moves to another correct answer (\cref{sec:p1}) & Holds; near zero on arithmetic for a thinking judge \\
\addlinespace[2pt]
\textbf{P2} Are differing correct answers graded worse? & Answer key & Their grading against wrong answers drops under every answer labeling; with one correct answer the reference helps (\cref{sec:p2}) & Holds. Small for API judges on arithmetic; interval includes zero for GPT-4.1 (factual) and Opus~5 (one pool) \\
\addlinespace[2pt]
\textbf{P3} Does it persist after blind acceptance? & Inability to verify, on its own & Answers accepted blind are rejected once another correct answer is the reference; a repeated blind call almost never does this (\cref{sec:p3}) & Holds for every judge with an acceptance test \\
\addlinespace[2pt]
\emph{Consequence} & --- & Shipped benchmark graders and RL verifiers under-credit such answers heavily (\cref{sec:cost}) & Large on questions with several answers; those are rare on the shipped benchmarks \\
\addlinespace[2pt]
\emph{Fix} & --- & A full answer list closes the gap for the benchmark graders; correctness prompts shrink it but can admit wrong answers on hard questions (\cref{sec:fix}) & The list works, except for one 1.5B verifier \\
\bottomrule
\end{tabular}
\end{table}
```

### 11. §2 "Tasks" — load 3, flow 2 — Δ 0.0

Causes: 123 words, 13 numbers; a 55-word sentence carrying the MACE domains, two audit rates, the reference draw and the matching rule across a semicolon; sentence 2 joins two unrelated pool descriptions with "and".

<!-- REWRITE: TASKS -->
```latex
\paragraph{Tasks.}
Our own tasks come from five constraint families (remainder systems, subset sums, Goldbach pairs, divisor counts, digit sums); each stores its full set of correct answers and one member, drawn at random, as the reference.
The \emph{replication pool} (120 tasks) was built to replicate an exploratory observation on \textsc{RewardBench-2} Ties~\citep{malik2025rewardbench2}; the \emph{$k$-pool} has 75 tasks with exactly $k \in \{1,2,4,8,16\}$ correct answers.
\textsc{MACE}~\citep{mace2026} contributes factual questions with 1, 2, 4, or 6 correct answers from its River and Language domains, where a model's valid answer is missing from the list 2.3\% and 8.1\% of the time.
The reference is drawn at random from each list, and an answer matches it by normalized string containment (\cref{app:mace}).
MATH-500~\citep{hendrycks2021math} supplies unique answers.
```
Separate ambiguity worth one word: "the $k$-pool has 75 tasks with exactly $k \in \{1,2,4,8,16\}$" reads as either 75 in total or 75 per $k$.

### 12.–14. "Candidates", "Conditions", "Open judges" bullets — no change (load 1–2).

### 15. §2 bullet "API judges" — load 2, flow 3 — Δ +0.2 line

Flow cause, created by the caption simplification: `fig:onevsseveral` now says only "Rows marked n/a cannot be measured in that cell". Of the two reasons, one is recoverable from Setup (GPT-4.1's scores tie) and one is not — the API-judge subsamples always contain a matching correct answer, so a best-of-64 change cannot be defined there. Setup currently says only that the subsamples "include wrong answers". The fact belongs in Setup, not in the caption (`app:frontier`: "each subsample holding at least one matching-correct, one non-matching-correct, and one wrong answer"):

<!-- REWRITE: API-JUDGES-BULLET -->
```latex
\item \textbf{API judges.} Claude Sonnet~5 and Opus~5, with thinking disabled, score 16-candidate subsamples of each pool that always include a matching correct answer, a differing correct answer, and a wrong answer. GPT-4.1's scores tie too often to rank candidates, so we use it for grading only.
```
Moved: nothing new; the composition of the subsamples moves from `app:frontier` into the one-line description that the simplified caption now depends on.

### 16. §2 bullet "Benchmark graders" — load 3, flow 3 — Δ +0.1 line

Causes: sentence 1 is a three-clause semicolon chain over three grader families; sentence 2 is about reasoning variants, which are not benchmark graders, and nests a citation inside a parenthetical containing its own semicolon.

<!-- REWRITE: BENCH-GRADERS-BULLET -->
```latex
\item \textbf{Benchmark graders} (\cref{sec:cost}). The SimpleQA and BrowseComp/HLE graders run with GPT-4.1, o3-mini, and Sonnet~5; our rubric also runs with Opus~5 and Haiku~4.5; and two open RL-reward verifiers~\citep{ma2025generalreasoner,liu2025compassverifier} grade the same answers. Reasoning variants of the judges --- Qwen3~\citep{yang2025qwen3} with thinking off or on, and Sonnet~5 with thinking --- are in \cref{app:reasoning}.
```
A separate bullet for the reasoning variants would read better but costs +0.5 line, so it is not proposed.

### 17. §2 bullet "Prompts" — no change (load 2, flow 2)
With §3 no longer quoting rubric *a*/*b* values, the only main-text appearance of "rubric~$a$" is the `fig:rotation-pool` caption, which unit 22 removes.

### 18. §2 "Answer extraction" ¶1 — load 3, flow 2 — Δ +0.2 line

Causes: the four labelings are named by terms the reader has not met — "registered", "any-format", "model-read" — inside a parenthetical; only "any-format" is ever defined, one paragraph later, and "model-read" is defined nowhere in the main text. "the four **core** open judges": "core" is undefined anywhere (the main text defines exactly four open judges; Mistral-7B is appendix-only).

<!-- REWRITE: ANSEXTR-P1 -->
```latex
Our grading results do not depend on how answers are read. Under each of four labelings (our registered checkers, any format, a model's reading, and boxed replies only), every grading change of the four open judges and GPT-4.1 has the same sign; only its size varies (\cref{app:grid}).\ph{} The swap test needs no labels at all, since it compares each text with itself.
```
**Flag for the author:** sentence 1 claims independence; sentence 2 establishes it for the *sign*. The defensible headline is "the direction of our grading results does not depend on how answers are read" — a scope narrowing, so not in the rewrite.

### 19. §2 "Answer extraction" ¶2 — load 3, flow 2 — Δ **−0.6 line**

Causes: the audit sentence carries three percentages against two denominators plus a failed prediction (91% of unboxed replies; 86% of the answers those labels credit; 90% predicted) — the pattern the lead author flagged. "The labeling matters for a simple reason." spends a line on a promise.

<!-- REWRITE: ANSEXTR-P2 -->
```latex
The labeling matters because the prompt asks for the final answer inside \texttt{\textbackslash boxed\{\}} and our registered checkers read it from there, yet 38\% to 43\% of replies ignore the format, so correct answers written in prose were often marked wrong.
We therefore label the constructed pools with \emph{any-format labels}, which accept a final answer stated in any form.
A registered audit by Claude Opus~5 confirms only 86\% of the answers these labels credit, short of the 90\% we predicted (\cref{app:grid}).
Boxed replies alone give the smallest effects, and selection accuracy depends on the labeling more than grading does.
```
Moved: **the 91% agreement figure moves to the appendix**, where `app:grid` already reports it ("agrees with the any-format label on 91.1% of unboxed replies (predicted at least 85%; confirmed)"). The failed 86%-against-90% prediction stays.

### 20. §2 "Measurements" definition list — no change (load 2, flow 2)
One antecedent to watch: "Grading AUROC: how well a judge's scores separate **those answers** from wrong answers" reaches back into the previous bullet.

### 21. §2 "Measurements" prose tail — load 3, flow 3 — Δ +0.3 line

Causes: five conventions in one sentence pair; "an exact expected score" is an undefined term of art whose pointer goes to `app:estimator` while the definition is in `app:setup`; the registration legend begins mid-paragraph with "Unmarked estimates were …", so the reader meets `\ph{}` and `\reana{}` with no cue that a legend has started.

<!-- REWRITE: MEASUREMENTS-PROSE -->
```latex
Changes are referenced minus blind, per task, with task-level bootstrap intervals; scores are out of 10, and rates and accuracies are in percentage points (pp). By default, constructed pools use any-format labels and open judges the exact scorer of \cref{app:setup,app:estimator}. We do not correct for multiplicity.
Marks apply to effect estimates: unmarked estimates were pre-specified in a timestamped commit or on OSF; \ph{} marks post hoc estimates; \reana{} marks pre-specified re-analyses of an effect whose direction was already known. \Cref{app:ledger} summarizes every registered prediction and lists each failure.
```

### 22. `fig:rotation-pool` caption (newly promoted into §3) — load 3, flow 2 — Δ **−0.5 line**

Causes, all from lifting an appendix caption into the main text unchanged, and all violations of the caption standard: (i) it ends in **`\pre{}`**, a superscript "PRE" the main-text legend never defines — §2 declares only unmarked, `\ph{}` and `\reana{}`; (ii) "the exact scorer", "the original scorer" and "rubric~$a$" are appendix vocabulary, undefined in the main text; (iii) one 47-word sentence with ten numbers. Since this caption now sits between the §3 heading and its first paragraph, it is the reader's first contact with the section.

<!-- REWRITE: FIGROT-CAPTION -->
```latex
\caption{\textbf{The swap over the whole replication pool.} Qwen2.5-7B, phi-4, and Sonnet~5 (API): mean change in score (points out of 10) of identical correct text when the reference moves onto its answer (120 tasks) or off it (93 tasks), and for answers that match neither reference (113 tasks; $+0.12$, $+0.30$, $+0.04$), with 95\% intervals. Pre-specified; scorers and rubric wording in \cref{tab:rotation}.}
```
Moved: the scorer-and-rubric sentence returns to the appendix, where `tab:rotation`'s caption already states it ("original scorer, registered runs; exact-scorer values for Qwen2.5-7B are in the extended appendix"). `\pre{}` becomes the word "Pre-specified", matching how `fig:reasoning` already words its registration status. No number is lost.

### 23. §3 ¶1 — load 3, flow 2 — Δ 0.0 (registration fix, no length change)

**Registration regression from the recent rewrite.** The single `\reana{}` now ends a sentence covering Qwen2.5-7B, phi-4 *and* Sonnet~5, marking all three as pre-specified re-analyses. Previously only the Qwen2.5-7B values carried `\reana{}` (the exact-scorer rescoring of `app:estimator`); phi-4's and Sonnet~5's were unmarked, i.e. pre-specified. The appendix still supports the old split — `tab:rotation` is "original scorer, registered runs", with Qwen2.5-7B's exact-scorer values held separately. Moving the mark onto the judge it belongs to costs nothing:

<!-- REWRITE: S3-P1 -->
```latex
We re-judged the replication pool's byte-identical samples with the reference moved to another correct answer.
Under Qwen2.5-7B,\reana{} phi-4, and Sonnet~5, text the reference moves onto gains 3 to 5 points and text it moves off loses about as much, while correct text that matches neither reference barely moves (\cref{fig:rotation-pool}).
All twelve registered cells for Qwen2.5-7B and phi-4 went as predicted; one registered prediction, that the swap would be ordered by numeric distance from the reference, failed (\cref{app:ledger}).
```
Remaining minor load: "cells" is undefined and the reader cannot reconstruct the twelve (two judges × two rubric wordings × three readouts, in the pre-rewrite text). If two words are ever free: "cells (rubric wording by readout, per judge)".

### 24.–25. §3 ¶2 and ¶3 — no change (load 2, flow 2)
¶3 switches measure without saying so: the swap is in score points, "added false rejections, from 36 to 15 points" is a different quantity. Readable as written; any fix costs a line. Recorded in the terminology table.

### 26. `fig:onevsseveral` caption — load 2, flow 3 — no change here; fix in unit 15

The simplification worked for load: 53 words, longest sentence 12 words, one number. The flow cost is that "Rows marked n/a cannot be measured in that cell" now asks the reader to accept a gap without a reason, and only one of the two reasons is recoverable from Setup. Unit 15 puts the missing reason where the standard says it belongs — in Setup — rather than back in the caption. Two words of polish if they are free: "rows … in that cell" mixes units; "n/a: not measurable in that panel" is cleaner.

### 27. §4 "Several correct answers" ¶1 — load 3, flow 2 — Δ +0.2 line — **scope, not load**

The latest version reads well: claim first, 104 words in four sentences, longest 35 words, and the registration status now sits beside the estimates it qualifies instead of in a separate caveat sentence — that placement is a real improvement, because the reader learns what is pre-specified at the moment the number lands.

One problem survives from the previous pass and is now sharper. Dropping the per-judge attributions widened a claim: "The AUROC … falls **for every judge we ran**, by 0.06 to 0.16 on factual questions and by 0.17 to 0.27 on the constructed pools" reads as though those two ranges cover every judge. They do not — 0.06 to 0.16 is the four judges run on factual questions, and 0.17 to 0.27 the four open judges on the constructed pools — and the Verdict still contradicts it in words ("On the constructed pools the API judges fall far less than the open judges"; GPT-4.1's "falls are small everywhere"). Now that the reconciling numbers (0.08; 0.01 to 0.06) have moved to the figure and Appendix G, the reader cannot repair the mismatch from the main text at all. Two attributions fix it:

<!-- REWRITE: SEVERAL-P1 -->
```latex
\paragraph{Several correct answers.}
The reference makes judges reject correct answers they would otherwise accept: under the registered labels, Qwen2.5-7B scores 28\% of the differing correct answers 3 or below with the reference, against 0.4\% blind\reana{} (\cref{app:grid}).
Grading suffers with it. The AUROC that separates those answers from wrong ones falls by 0.06 to 0.16 for the four judges on factual questions and by 0.17 to 0.27 for the four open judges on the constructed pools (\cref{fig:onevsseveral}b). We registered the factual falls for Qwen2.5-7B, Sonnet~5, and Opus~5 in advance; the constructed-pool falls are post hoc,\ph{} because they use the any-format labels we adopted after the registered checker proved too strict.
```
Moved: nothing; the per-judge values stay in `fig:onevsseveral`b, as intended. Treat this as a correctness fix rather than a style one: it is the only place in the main text where two paragraphs now assert different things about the API judges.

### 28. §4 "Several correct answers" ¶2 ("Relabeling moves their size, not their sign") — no change (load 2, flow 2)
Two sentences, 44 words, one number, robustness claim first and the pre-specified 0.29 estimate last, with the ledger pointer at the end. This is the model the heavy paragraphs in §5–§7 should follow. Sentence 2 is 37 words with a semicolon and two `\cref`s, which is the outer limit but reads cleanly.

### 29. §4 "One correct answer" — load 3, flow 2 — Δ +0.1 line

Cause: a single 49-word sentence with four numbers, two registration marks, two datasets and a comparison clause ("as the full solution does") whose referent is three clauses back.

<!-- REWRITE: ONE -->
```latex
\paragraph{One correct answer.}
With one correct answer the reference helps, as P2 requires.
On MATH-500, showing only the final answer raises best-of-64 accuracy by 28.6 and 30.6~pp for Qwen2.5-7B and 14B,\reana{} as the full solution does; on \textsc{MACE}'s single-answer questions it raises accuracy by 29.4\ph{} and 26.5~pp for Qwen2.5-7B and phi-4 (\cref{fig:onevsseveral}a).
```

### 30. `fig:reasoning` caption — load 3, flow 2 — Δ **−0.9 line**

Cause, under the caption standard: three of its four sentences are already elsewhere. "Filled circles: … open circles: … crosses: …" repeats the plot's own legend, which spells out the same three series; the acceptance threshold is stated in §5 one paragraph below. Keeping the threshold is defensible (it makes the figure standalone) — the marker glossary is not.

<!-- REWRITE: FIGACCEPT-CAPTION -->
```latex
\caption{\textbf{The reference rejects correct answers the judge already accepts.}
Correct answers the judge accepts blind (a blind 10 for Sonnet~5 and Opus~5; for open judges, the blind score that at most 3\% of wrong answers reach), and the share of them scored 3 or below once the reference is shown. Pre-specified: the second blind calls and Opus~5's shares; the rest is post hoc.}
```
Moved: the marker glossary is dropped in favour of the plot legend; no number or claim is lost.

### 31. §4 "Verdict" — no change (load 2, flow 2)

The split fixed this unit. The judge verdict is now 61 words in three sentences (longest 26) and the selection result has its own paragraph of 38 words, so a summary paragraph no longer doubles as the place where a new finding appears. Moving 0.08, 0.01–0.06, $+2.0$ and $+6.1$ into `fig:onevsseveral`b and Appendix G is the right call for load — with one consequence recorded under unit 27: the main text no longer contains the numbers that reconciled ¶1's ranges with "the API judges fall far less", so ¶1 has to carry its own attributions. Minor polish if a few characters are ever free: in "Two intervals include zero: GPT-4.1 on factual questions, whose falls are small everywhere, and Opus~5 on the replication pool", the appositive interrupts a two-item list.

### 32. §5 "What an inability to verify would predict" — load 3, flow 2 — Δ +0.1 line

Causes: 141 words with sentences of 49 and 36 words; the 49-word sentence states the prediction and its analogy in one breath; "it" changes referent three times across "Call this *verification failure*; it would make … It makes a sharp prediction."

<!-- REWRITE: VF-PREDICT -->
```latex
\paragraph{What an inability to verify would predict.}
\Cref{sec:p1,sec:p2} show that the reference moves scores, but they allow a less interesting explanation: the judge cannot tell on its own that a different answer is correct, so the reference is its only evidence. Call this \emph{verification failure}. It would make the problem one of model capability rather than of judging, and it makes a sharp prediction. A judge that accepts a correct answer with no reference in front of it has shown that it can recognize that answer as correct. Showing a different correct answer as the reference should then leave its score alone, just as it leaves alone the answers that match the reference. The alternative, \emph{agreement}, is that the judge defers to the answer it was shown even when it knows another answer is correct. Agreement predicts that accepted answers still lose credit when they differ from the reference.
```

### 33. §5 "Answers the judge accepts without a reference" — load 3, flow 2 — Δ −0.1 line

Causes: a 51-word opening sentence defining two thresholds with a nested calibration remark; a result sentence whose subject is triply embedded ("Of the correct factual answers the four judges accept that differ from the reference"); "the four judges" has no antecedent in the text, only in the figure.

<!-- REWRITE: ACCEPTED -->
```latex
\paragraph{Answers the judge accepts without a reference.}
The API judges rarely give a wrong answer a blind 10, so we take a blind 10 as acceptance; the open judges' expected scores rarely reach 10, so for them we take the blind score that at most 3\% of wrong answers reach, about Sonnet~5's rate for a blind 10.
Across the four judges tested on factual questions, 19\% to 83\% of the accepted correct answers that differ from the reference score 3 or below once it is shown, and none of those that match it do (\cref{fig:reasoning}).\ph{}
Verification failure predicts none.
```

### 34. §5 "It is not score noise" — load 4, flow 3 — Δ +0.1 line (preferred version +1.0)

Causes: two sentences of 40 and 56 words carrying nine numbers; the second answers a *different* objection (rubric wording) than the heading promises, and packs two judges × two prompt families × three rates plus the missing-noise-floor caveat. The lead author's rule — the 2-of-843 control in its own paragraph — is not met, because the wording rebuttal shares the paragraph. Preferred version, if the Table 1 rebuild yields the full 2 lines:

<!-- REWRITE: NOT-NOISE-SPLIT -->
```latex
\paragraph{It is not score noise.}
A second blind call through the same interface, still without a reference, gives 3 or below to 2 of the 843 accepted differing answers of the two API judges across the three pools, against 117 once the reference is shown.

\paragraph{Nor is it our rubric's wording.}
Asked only whether the response is correct, GPT-4.1 and Sonnet~5 withdraw credit from 22\% and 14\% of the differing correct answers they accepted blind, and from none of the matching ones;\reana{} asked to reason first, from 1\% to 9\% (\cref{app:r27}).
These prompts have no second blind call.
```
Budget version (+0.1 line), same sentences under one honest heading:

<!-- REWRITE: NOT-NOISE -->
```latex
\paragraph{It is not score noise, or our wording.}
A second blind call through the same interface, still without a reference, gives 3 or below to 2 of the 843 accepted differing answers of the two API judges across the three pools, against 117 once the reference is shown.
Nor is it our rubric's wording. Asked only whether the response is correct, GPT-4.1 and Sonnet~5 withdraw credit from 22\% and 14\% of the differing correct answers they accepted blind, and from none of the matching ones;\reana{} asked to reason first, from 1\% to 9\% (\cref{app:r27}).
These prompts have no second blind call.
```
Registration note: `\reana{}` stays where the author put it; `app:r27` treats the whole analysis as one pre-specified re-analysis, so it could equally cover the 1%–9% values — the author's call.

### 35. `fig:graders` caption — load 3, flow 2 — Δ **−1.0 line**

Causes: a 25-word bold title carrying three claims is the first thing a skimming reviewer reads on that page; and, under the caption standard, the enumeration of what the upper panel contains ("and with Sonnet~5, open RL-reward verifiers, and our score rubric", "and the HLE judge with its match clause removed") repeats the figure's own row labels, while "(GPT-4.1; o3-mini)" leaves the grader mapping to be guessed.

<!-- REWRITE: FIGGRADERS-CAPTION -->
```latex
\caption{\textbf{Graders told to match under-count correct answers.} Asking whether the answer is correct shrinks the gap, and the full answer list closes it for all graders but one verifier.
\textbf{(a)}~Accuracy of four models' answers to 149 \textsc{MACE} questions with several correct answers, with a reference drawn at random from each list, minus their answer-list accuracy; the benchmark graders run verbatim with their configured judges (GPT-4.1, or o3-mini for HLE). Lower panel, on a different scale: prompts that ask whether the answer is correct.
\textbf{(b)}~Grading AUROC change against blind on the 40-task \textsc{MACE} subsample. 95\% intervals; all values pre-specified.}
```
Moved: the row enumeration is dropped in favour of the plot's row labels; the two claims move out of the bold title into the caption body. No number or claim is lost.

### 36. §5 "Verdict" — load 3, flow 2 — Δ +0.2 line

Causes: sentence 1 compresses two verdicts and a registration breakdown into a colon-plus-comma structure; three caveats follow with no signposting; "same-interface noise control" is a fourth name for the second blind call.

<!-- REWRITE: P3-VERDICT -->
```latex
\paragraph{Verdict.}
P3 holds for all six judges with a usable acceptance test, and on factual questions for four judges from three developers: two with a registered second blind call as a noise control, two at a post hoc threshold.
The effect therefore cannot be explained solely by verification failure, although verification difficulty may explain part of it for some judges.
Two limits remain.
Blind acceptance is a proxy for verification, not a direct test of it: a judge can accept an answer without checking it, and Opus~5 gives a blind 10 to 5\% to 8\% of wrong answers (\cref{app:acceptance}).
Agreement also covers a judge that assumes a question has one intended answer, which P3 does not separate from rewarding a match.
```
Dependent edit (unit 49, 0.0 lines): in §9 "Judges and prompts", "has a same-interface noise control only for the two API judges" → "has a second blind call as a noise control only for the two API judges".

### 37. §6 "Graders shipped with benchmarks" — load 5, flow 3 — Δ +0.8 line

Causes: 157 words in 4 sentences (mean 39 w/s), **17 numbers**, six parentheticals. Sentence 1 is 68 words and holds four models, a dataset size, two graders, a provenance claim and a three-way judge mapping. Sentence 2 (48 words) interleaves two credit rates with two accuracy shortfalls, so "47% to 53% … 0% to 2.3% … 30 to 34 and 65 to 67" must be bound pairwise. Flow: §5 ends on caveats, §6 opens on logistics, and *answer-list accuracy* — used since the abstract — is defined nowhere.

<!-- REWRITE: GRADERS-SHIPPED -->
```latex
\paragraph{Graders shipped with benchmarks.}
We took one answer from each of Llama-3.1-8B-Instruct (its first stored sample), Claude Haiku~4.5, Sonnet~5, and Opus~5 to each of 149 \textsc{MACE} questions with several correct answers.
Every answer was graded with the SimpleQA grader and the judge shared by BrowseComp and HLE, copied from their repositories and run as configured there (GPT-4.1 for SimpleQA and BrowseComp, o3-mini for HLE), and with Sonnet~5 (\cref{app:r24}).
Each grader saw one reference drawn at random from the answer list.
The SimpleQA grader credits 47\% to 53\% of the correct answers that differ from it, so pooled accuracy falls 30 to 34 points below \emph{answer-list accuracy}, the accuracy scored against the full lists; the BrowseComp/HLE judge credits 0\% to 2.3\%, and accuracy falls 65 to 67 points (\cref{fig:graders}a).
Two open RL-reward verifiers do the same: given one reference, General-Reasoner's verifier and CompassVerifier-3B credit 6\% and 0\% of these answers (\cref{app:r26}).
Our own score rubric, with four judges, leaves the models 10 to 22 points below the answer lists (\cref{app:acceptance}).
```
The *answer-list accuracy* gloss is 55 of the 80 added characters; drop it only under budget pressure, and then define the term in the `fig:graders` caption instead.

### 38. §6 "Who should care: reuse" — load 5, flow 3 — Δ +0.4 line

Causes: the heaviest sentence in the paper — **97 words**, three semicolon-separated reuse cases, five numbers, two citations, a nested parenthetical with its own exclusion rule, and a post hoc mark; mean sentence length 52 words. Flow: the paragraph opens on a concession, and the reward-signal point that the ethics statement leans on is welded to the end of the reuse list.

<!-- REWRITE: REUSE -->
```latex
\paragraph{Who should care: reuse.}
These graders are right for the benchmarks they were written for.
By adjudicated LLM labels, 0\% to 3\% of sampled SimpleQA, BrowseComp, and HLE questions have several correct answers (up to 15\% on HLE by either annotator; \cref{app:prevalence}), so their own leaderboards are probably little affected.
The failure is about reuse where answers are open.
General-Reasoner's single-reference verifier rewards an RL training set~\citep{ma2025generalreasoner} in which, by our labels, 5.5\% of questions admit several answers after adjudication and 18\% by either annotator.
Of sampled NQ-open questions, 30\% to 44\% admit several under our two labelings (18.5\% in the first once answers that changed over time are excluded),\ph{} and grading it with LLMs against its gold answers has been studied~\citep{kamalloo2023evaluating}.
Benchmarks built from such questions, such as \textsc{RewardBench-2} Ties and \textsc{MACE}~\citep{malik2025rewardbench2,mace2026}, inherit the failure whenever they are graded against one reference.
Reward signals are the larger risk, because there the judge does not just report a score but shapes a policy.
The two verifiers above, both built to give RL rewards, credit almost none of the correct answers that differ from the reference.
Our exploratory training runs were inconclusive (extended appendix), so we state this as a concern rather than a demonstrated harm.
```
Reserve saving if needed: either parenthetical is fully reported in `app:prevalence` and worth ~0.6 line. Both are conservative disclosures that cut against the paper's headline, so I would keep them and find the line elsewhere.

### 39. §6 "What sets the size" — load 5, flow 2 — Δ +0.4 line

Causes: 154 words, 15 numbers, one 58-word sentence holding two prompt families, four shortfalls, a parenthetical of blind values and an interval caveat; "(5 and 2 blind)" is unreadable without the appendix. The thesis is a gradient, but the prompts are presented out of order.

<!-- REWRITE: WHAT-SETS-SIZE -->
```latex
\paragraph{What sets the size.}
The shortfall tracks what the grader is asked (\cref{fig:graders}a, lower panel; \cref{app:r25,app:r26}).
Told to ``focus only on whether the answers match'', the HLE judge credits almost no differing correct answer, even with o3-mini.
Removing that match clause and adding that a different correct answer is correct recovers 35 points for GPT-4.1 and 53 for Sonnet~5, but leaves 31 and 13, outside our registered 10-point bound.
Asked instead whether the response is a correct answer, with no reasoning, GPT-4.1 and Sonnet~5 fall 17 and 10 points short, against 5 and 2 points blind.
Asked to reason first (chain of thought, verify the answer on its own, or solve the question first), they fall 0.5 to 6 points short, with intervals that include zero for two of GPT-4.1's prompts.
Chain-of-thought reasoning closes most of GPT-4.1's gap but, by our registered test, not Sonnet~5's, and a residual pull remains for Sonnet~5 under every prompt.
```

### 40. §7 "Give the judge every correct answer" — load 4, flow 2 — Δ +0.6 line

Causes: 193 words, 12 numbers, four semicolons; "at most 3 of 56 more wrong answers" collides with "the registered bound of 3 points" in one sentence (a count and a percentage-point bound); "half of these credits to an alias our string matching misses" has no verb; a caveat interrupts a three-item list; "all five benchmark graders" cannot be counted from §2.

<!-- REWRITE: GIVE-EVERY -->
```latex
\paragraph{Give the judge every correct answer.}
An answer key is the reading under which the reference is harmless.
Stated as ``any one of the following is a complete correct answer'', the full answer list brings all five benchmark-grader configurations within 0.5 points of the answer lists and raises their credit for differing correct answers to 99\% or more (\cref{fig:graders}a).
This agreement is partly by construction, because the same lists define which answers count as correct; what it shows is that the graders follow a list when given one.
The list admits at most 3 of 56 more wrong answers, and half of these credits go to an alias our string matching misses.
The registered bound of 3 points on that extra credit still failed for the BrowseComp/HLE judge with GPT-4.1 and o3-mini.
With our rubric the list also repairs grading: AUROC is 0.03 to 0.06 above blind for Sonnet~5, Opus~5, and GPT-4.1, although Opus~5's interval touches zero (\cref{fig:graders}b; \cref{app:r24}).
The list fixes CompassVerifier-3B but not General-Reasoner's 1.5B verifier, which credits 67\% of differing correct answers with the list but also 30\% of wrong ones (\cref{app:r26}).
A list is still closed: whether it makes judges reject correct answers it omits is untested, and lists can be incomplete (\cref{app:mace}).
```
"all five benchmark graders" → "all five benchmark-grader configurations", which is what `tab:r24-standard` reports (SimpleQA×GPT-4.1, BrowseComp×GPT-4.1, HLE×o3-mini, SimpleQA×Sonnet~5, HLE×Sonnet~5).

### 41. §7 "When the answers cannot be listed" — load 4, flow 3 — Δ +0.4 line

Causes: one 53-word sentence holding the subsample, its composition, a superlative over three prompts, two AUROC values, a false-acceptance bound and a residual cost; the tense slips from "had" to "rejects"; "the 40-task subsample" is ambiguous (the API-judge subsamples include 40 replication tasks as well as 40 MACE tasks); "correctness prompts" and "false acceptances" are undefined. Flow: the newly folded-in blind-then-reveal sentence is a different mitigation and arrives with no connective, so the paragraph ends on an apparent non sequitur.

<!-- REWRITE: CANNOT-LIST -->
```latex
\paragraph{When the answers cannot be listed.}
If the judge can answer the questions, remove any instruction to match and ask whether the answer is correct.
We compared three such prompts on the 40-task \textsc{MACE} subsample, which has many wrong answers.
Letting the judge solve the question first had the smallest grading loss: AUROC $-0.04$ and $-0.05$ against blind, with false acceptances of wrong answers up by at most 3.2 points.
It still raised false rejections of differing correct answers by 5 to 7 points (\cref{app:r26}).
One protocol we registered did not help: scoring blind and then rescoring with the reference left grading below blind for most open judges\ph{} (\cref{app:mitigation}).
```
"rejects 5 to 7 more points of differing correct answers" is restated as a rise in false rejections, the quantity `tab:r26-subsample` reports.

### 42. §7 "Questions beyond the judge" — load 3, flow 2 — Δ +0.3 line

Causes: "There," opens with a deictic pointing at the heading; a 38-word sentence splits one grader's two rates across a mid-sentence post hoc mark and then switches grader; "almost all wrong" leaves the labeller unnamed, although §9 discloses these labels come from HLE's own judge.

<!-- REWRITE: BEYOND-JUDGE -->
```latex
\paragraph{Questions beyond the judge.}
On such questions, the instruction to match can be what keeps wrong answers out.
We took the 200 HLE questions of our prevalence audit (6 labeled as having several answers, 53 unclear; \cref{app:prevalence}) and graded two models' answers to them; HLE's official judge marks almost all of them wrong.
With the reference, GPT-4.1 credited 17\% of those answers under the direct prompt and 26\% when it solved first, often after calling the reference wrong.\ph{}
Sonnet~5 credited at most 1\% (\cref{app:r27}).
A change of instruction is therefore safe only for the judges and questions on which it has been checked.
```

### 43. §7 "A recipe" — no change (load 2, flow 2).

### 44. §8 "Reference-guided judging" — load 3, flow 2 — Δ 0.0

Cause: sentence 2 places a 30-word compound subject ahead of its verb, with six citations landing after the predicate.

<!-- REWRITE: RW-REFGUIDED -->
```latex
\paragraph{Reference-guided judging.}
References are the standard remedy for grading math and reasoning with LLM judges~\citep{zheng2023judging,refguided2024,chen2026rethinking}, and judges without them over-credit wrong answers~\citep{generous2026}. Three kinds of grader check a response against one gold answer: judge models such as JudgeLM and Prometheus, the graders of factuality and hard-exam benchmarks, and answer matching, advocated as an alternative to multiple choice~\citep{zhu2023judgelm,kim2024prometheus,wei2024simpleqa,wei2025browsecomp,phan2025hle,chandak2025answermatching}. RL-reward verifiers and their benchmarks likewise pair each question with one reference~\citep{chen2025xverify,liu2025compassverifier,yan2025verifybench}, and false negatives from rule-based checking slow RL~\citep{xu2025tinyv,huang2025pitfalls}.
Judges depend on the reference being correct~\citep{judgingref2026,krumdick2025nofreelabels}, diverge from humans under reference-based grading~\citep{thakur2024judging}, and favor the reference's solution method~\citep{fixation2025}.
```

### 45.–46. §8 "Single references and many correct answers", "Judge biases and optimization" — no change (load 2, flow 2). The tightened sycophancy sentence works.

### 47.–48., 50. §9 "Labels", "Tasks", "Mechanism and registration" bullets — no change (load 2, flow 2).
Cutting "(it rejects 14% of the unboxed replies the rule credits)" removed the one number here whose form disagreed with §2. Residual: "the HLE labels" would read better as "the labels on the hard HLE questions of \cref{sec:fix}" (~+0.2 line, not proposed).

### 49. §9 "Judges and prompts" bullet — load 2, flow 2 — Δ 0.0
Only the terminology alignment from unit 36.

### 51. §10 Conclusion — load 3, flow 2 — Δ +0.1 line

Causes (in the newly shortened text): sentence 2 is 44 words and carries three claims joined by "and"; "favor the one they are shown, even over answers they accept without one" asks the reader to compare a reference against answers, which is not the comparison the experiment makes — the judge *rejects* answers it had accepted blind.

<!-- REWRITE: CONCLUSION -->
```latex
On the unique-answer tasks we study, a reference answer is a useful check.
When a question has several correct answers, LLM judges favor the one they are shown, and reject correct answers they had accepted without a reference.
Run with one reference on such questions, shipped graders score models far below their answer-list accuracy, largely because of what they are asked.
Where the correct answers can be listed, grade against all of them; otherwise ask whether the answer is correct, and audit disagreements between blind and referenced scores.
```
Flag, not fixed: the conclusion now carries no number while the abstract carries fourteen, and "largely because of what they are asked" is a slightly stronger attribution than the abstract's "Much of this comes from the instruction to match".

---

## 3. Ten highest-load units, ranked

1. **§6 "Who should care: reuse"** — a 97-word sentence; mean 52 words/sentence; three reuse cases in one semicolon chain.
2. **§6 "Graders shipped with benchmarks"** — 17 numbers in 4 sentences; 68-word opener; paired ranges bound across a 48-word sentence.
3. **§6 "What sets the size"** — 15 numbers; one 58-word sentence; "(5 and 2 blind)"; prompts out of gradient order.
4. **Abstract** — a 102-word sentence carrying all three findings; the setting withheld until the seventh sentence.
5. **§5 "It is not score noise"** — 96 words in two sentences (40 and 56 words), nine numbers, and a second objection under a heading about noise.
6. **§7 "Give the judge every correct answer"** — 193 words, 12 numbers, the "3 of 56" / "3 points" collision, an uncountable "all five benchmark graders".
7. **Intro "What we find"** — three sentences over 35 words, including a 64-word prior-work chain.
8. **§7 "When the answers cannot be listed"** — one 53-word sentence with six numbers, a superlative, a tense slip and an ambiguous "40-task subsample", now ending on an unconnected mitigation.
9. **`fig:rotation-pool` caption** — one 47-word sentence with ten numbers, three appendix-only terms and an undefined registration mark, sitting between the §3 heading and its first paragraph.
10. **§2 "Measurements" prose tail** — five conventions in one sentence pair, an undefined "exact expected score", and a registration legend that starts without a cue.

Just outside: §5 "What an inability to verify would predict", Table 1's Verdict column, §4 "One correct answer", §4 "Several correct answers" ¶1. Both §4 paragraphs that used to head this list — "Several correct answers" and the Verdict — are now load 2–3 after the author's rewrites; what remains in §4 is a scope mismatch (unit 27), not load.

---

## 4. Undefined or late-defined terms, and where each should first be defined

| Term | First used | Defined | Fix |
|---|---|---|---|
| *selection* / *selection accuracy* | §1 ¶2; §2 "Answer extraction" ¶2 | never (only *best-of-64 accuracy*) | `(\emph{selection})` in §1 ¶2 — unit 4 |
| *blind*, *referenced* | Intro P3 item; Table 1 | §2 "Conditions", i.e. after Table 1 | optional gloss in the P3 item: "…without a reference (\emph{blind})" |
| *any-format labels* | §2 ¶1 (as "any format") | §2 ¶2 | unit 18 names the four labelings in plain words at first use |
| *model-read labels* | §2 ¶1 | never in the main text | unit 18 ("a model's reading") |
| "four **core** open judges" | §2 ¶1 | never | drop "core" — unit 18 |
| why a cell is "n/a" in `fig:onevsseveral` | `fig:onevsseveral` caption | only one of the two reasons is in Setup | unit 15 puts the subsample composition in Setup |
| *rubric $a$*, *exact scorer*, *original scorer* | `fig:rotation-pool` caption | appendix only | unit 22 returns that sentence to `tab:rotation` |
| `\pre{}` superscript | `fig:rotation-pool` caption | §2 legend defines only unmarked, `\ph{}`, `\reana{}` | unit 22 replaces it with "Pre-specified" |
| *cells*, *readouts* | §3 ¶1 | never | unit 23 note |
| *exact scorer* (again) | §2 "Measurements" prose | `app:setup`, but the pointer goes to `app:estimator` | unit 21 fixes the pointer |
| "for every judge we ran" vs the two AUROC ranges | §4 ¶1 | contradicted by §4 Verdict | unit 27 attributes each range |
| *answer-list accuracy* | Abstract, §1, `fig:graders`, §6, §10 | never | unit 37 defines it at first measurement |
| *false acceptances* | §7 | never | unit 41 ("false acceptances of wrong answers") |
| *correctness prompts* | Table 1, §7 | never | unit 41 ("three such prompts", after the preceding sentence defines them) |
| "the 40-task subsample" | §7; `fig:graders` caption | never linked to §2's 16-candidate subsamples | unit 41 ("the 40-task \textsc{MACE} subsample") |
| "the four judges" | §5 | only `fig:reasoning` | unit 33 ("the four judges tested on factual questions") |
| "all five benchmark graders" | §7 | not countable from §2 | unit 40 ("benchmark-grader configurations") |
| *usable acceptance test* | Table 1; §5 Verdict | never | acceptable; a `(\cref{fig:reasoning})` pointer would close it |
| second blind call / repeated call / repeated blind call / same-interface noise control | Abstract, Table 1, §5, §9 | four names for one control | standardize on "second blind call" — units 36, 49 |
| *added false rejections* (§3 ¶3) vs *swap* points | §3 ¶3 | both defined; the switch is unsignalled | note only; a fix costs a line |

---

## 5. Section-to-section transitions

1. **§2 → §3.** §2 ends on the registration legend, §3 opens on method; the section title carries the point. But `fig:rotation-pool` now lands between the heading and the first paragraph, so its caption is the reader's first contact with §3 — one more reason to fix it (unit 22).
2. **§3 ¶3 → §4.** ¶3 ends with two forward references to §6. Keeping them is right — they pre-empt the "won't better judges fix this?" objection — and the current phrasing no longer duplicates §6 word for word.
3. **§4 ¶1 → §4 Verdict.** ¶1's compact ranges and the Verdict's "the API judges fall far less than the open judges" currently disagree, and since the reconciling numbers moved to the figure and Appendix G, nothing in the main text closes the gap. Unit 27 is what makes this seam hold.
4. **§4 "Verdict" → §5.** Good: §5 opens by naming §3 and §4.
5. **§5 "Verdict" → §6.** The weakest seam: §5 ends on two caveats about what P3 cannot separate, and §6 opens on logistics. At zero slack the section title has to carry the bridge; unit 37 at least front-loads the design sentence.
6. **§6 internal order.** "Who should care: reuse" sits between the measurement and its explanation, so `fig:graders`' lower panel is discussed a page after its upper panel. The order matches the section title, so leave it; if the section is reopened, "What sets the size" reads better directly after "Graders shipped", with reuse closing the section.
7. **§6 → §7.** Good: "An answer key is the reading under which the reference is harmless" picks up the intro's dichotomy.
8. **Inside §7.** "When the answers cannot be listed" now ends with the blind-then-reveal negative result, folded in without a connective; unit 41 adds "One protocol we registered did not help:".
9. **§7 → §8 → §9 → §10.** Standard; no problems.
10. **Table 1's placement** (page 3, between "Tasks" and the judges bullets) interrupts §2 and uses four terms defined later or not at all (*labeling*, *accepted blind*, *correctness prompts*, "answers are open"). The cell edits in unit 10 close three of the four.

---

## 6. Net line change

| Group | Δ lines |
|---|---|
| Savings: Table 1 columns and cells (unit 10) | −1.0 to −2.0 |
| Savings: `fig:graders` caption (unit 35) | −1.0 |
| Savings: `fig:reasoning` caption (unit 30) | −0.9 |
| Savings: `fig:rotation-pool` caption (unit 22) | −0.5 |
| Savings: §2 "Answer extraction" ¶2, 91% to the appendix (unit 19) | −0.6 |
| Savings: abstract, §5 "Answers the judge accepts" | −0.2 |
| Costs: §6 "Graders shipped" (+0.8), §7 "Give the judge every correct answer" (+0.6), §6 reuse (+0.4), §6 "What sets the size" (+0.4), §7 "cannot be listed" (+0.4), "What we find" (+0.4) | +3.0 |
| Costs: remaining fourteen rewrites, each +0.1 to +0.3 | +1.9 |
| **Total (Table 1 saving taken as −1.5)** | **≈ −0.3** |

The full set is length-neutral within the precision of a character estimate (±0.5 line), and the three caption trims alone cover the three most expensive prose rewrites. If the rebuild shows the Table 1 change saving the full 2 lines, spend the margin on the **preferred two-paragraph version of unit 34**, which restores the lead author's one-control-per-paragraph structure (+1.0). If instead the table saves less than a line, cut in this order, for about 1.6 lines: (i) the `(\emph{selection})` gloss in unit 4 (−0.2); (ii) the *answer-list accuracy* gloss in unit 37 (−0.55), defining the term in the `fig:graders` caption instead; (iii) either prevalence parenthetical in unit 38 (−0.6); (iv) "Two limits remain." in unit 36 (−0.2).

Float placement is the other risk: `fig:rotation-pool`, `fig:onevsseveral`, `fig:reasoning` and `fig:graders` are all `[t]` floats adjacent to edited paragraphs, and two of them now shrink, so page-level placement must be checked after the edit, not just the line total.

**Material moved to the appendix** (all already there, so nothing is lost): the 91% label-audit agreement (`app:grid`); the scorer-and-rubric sentence of the `fig:rotation-pool` caption (`tab:rotation`); the marker glossary of the `fig:reasoning` caption and the row enumeration of the `fig:graders` caption (both in the plots' own legends and row labels). The model-read and boxed-only AUROC ranges were already moved to `tab:labelings-gnm` by the author's §4 rewrite.

---

## 7. Overall readability verdict

The recent passes have done most of the work. §2, §3, all of §4, §7's fold, Related work, Limitations and the Conclusion now read the way the whole paper should: short paragraphs, one claim per sentence, registration status beside the estimate it qualifies, and per-judge numbers left to figures and appendix tables. §4 in particular has gone from the heaviest section in the paper to a model for the rest. Three sections have not had that treatment, and they are where a reviewer's attention will fail: **§5, §6 and §7 still carry the paper's numbers at 12–17 per paragraph in sentences averaging 36–52 words**, with the reuse paragraph's 97-word sentence the single worst offender. None of the fixes needs new evidence — sentence splits, pairing each number with the grader it belongs to, and five definitions placed at first use.

Three issues deserve attention beyond load, all introduced by otherwise-good rewrites. First, promoting `fig:rotation-pool` into §3 brought appendix vocabulary and an appendix registration mark (`\pre{}`) into the main text, where §2's legend does not define them. Second, the `\reana{}` in §3 ¶1 now spans three judges where the earlier version marked only Qwen2.5-7B's exact-scorer values. Third, and most substantive, §4 ¶1's compact phrasing — "falls for every judge we ran, by 0.06 to 0.16 … and by 0.17 to 0.27" — attaches both ranges to *every* judge, which the Verdict contradicts in words, and the numbers that used to reconcile the two now live only in the figure and Appendix G. All three are fixed at zero or near-zero line cost (units 22, 23, 27), and the third is a correctness fix, not a style one.

With the rewrites above, mean sentence length in the heaviest paragraphs falls from 39–52 words to roughly 25–30, no main-text sentence exceeds about 45 words, no paragraph carries more than four numbers per sentence, three captions stop repeating their own legends, and the page count does not move. Verdict: **currently a demanding read through §5–§7 that a careful reviewer can follow only with effort; after these edits, clear throughout at no cost in length.**
