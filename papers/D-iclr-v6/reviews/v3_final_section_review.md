# Section-by-section area-chair review of "The Reference Is Not an Answer Key" (v3, final)

Reviewed: `The_Reference_Is_Not_an_Answer_Key_v3.pdf` (36 pp.), `main.tex`, `appendix.tex`, `tables/*.tex`; `appendix_extended.tex` checked for leftovers from the removed model section. Compared against `D-iclr-v2/main.tex`. Line numbers below are `main.tex` lines unless marked "PDF l." (PDF line numbers) or `appendix.tex`.

Status key: ADDRESSED / PARTLY / NOT ADDRESSED / DEVIATED-JUSTIFIED / DEVIATED-UNJUSTIFIED.

**Format checks.** Figure 1 is on page 1 (bottom float, below the abstract). The main text, through the Conclusion, ends on page 9 (PDF l. 460). The AI-use statement ("required, does not count"), ethics statement and reproducibility statement follow on pages 9 and 10 and do not count toward the limit (template l. 399, 416, 430). **The 9-page limit is met.** About 24 lines remain on page 9 before the Conclusion would cross onto page 10, so the should-fix additions below (net about +10 lines) fit. If they do not, cutting the Conclusion to two sentences (§10) gets back about 4 lines. No undefined references in `main.log`.

---

## Abstract

### 1. Feedback compliance
| Requirement | Status | Evidence |
|---|---|---|
| Put the labeling robustness in the abstract, one clause ("direction holds under every labelling scheme") | ADDRESSED | "(2) correct answers that differ from the reference are graded worse against wrong answers, in the same direction under every answer-labeling scheme we tried" |
| Put the second-blind-call control (2 of 843) in the abstract | ADDRESSED (should-fix: add the comparator) | "while a repeated call without the reference rejects only 2 of 843" |
| Drop three-readings naming (from the v2 abstract) | ADDRESSED | "We separate three readings of a reference ..." is gone |

### 2. Fresh AC critique
- **"2 of 843" has no comparator.** A first-time reader cannot tell whether 2 of 843 is small next to the referenced count. The number only matters next to "117 with the reference". (should-fix)
- **The "instruction to match" sentence gets its evidence backwards.** "Much of this comes from the instruction to match: given the full answer list, the benchmark graders come within a point of it". A full list is not evidence about the instruction. The evidence for the instruction is the correctness prompt. "It" also has no clear antecedent (the list? the accuracy?). A reviewer will read the colon as a non-sequitur. (should-fix)
- "in the same direction under every answer-labeling scheme we tried" is unscoped. §2 (l. 133) correctly limits it to the four core open judges and GPT-4.1, and Table 6 shows Mistral-7B at +0.01 on boxed replies. Mistral failed the score-resolution screen, so this is defensible, but the abstract claim is broader than the body's. (nit)
- "We test these predictions": the abstract no longer states any predictions, so "these" has no antecedent. "with a complete preregistration ledger" oversells, given that most registrations are timestamped commits and the verdict rule was applied retroactively (Limitations). A skeptical reviewer will quote Limitations back at this phrase. (nit)

Replacement for the last four sentences (from "Those benchmarks rarely ..." to the end):

```latex
(3) judges reject such answers even after accepting them without a reference: once the reference is shown, 117 of 843 accepted answers score 3 or below, against 2 of 843 on a repeated call without it, so an inability to verify them cannot alone explain the effect.
Those benchmarks rarely contain such questions, but run verbatim on 149 factual questions that do, with a reference drawn at random from each answer list, their graders score four models 30 to 67 points below their answer-list accuracy.
Much of this comes from the instruction to match: asked instead whether the answer is correct, judges shrink the gap on questions they can answer. Given the full answer list, the benchmark graders come within a point of answer-list accuracy.
We run these tests with more than a dozen judges on constructed tasks, MACE, and MATH-500, and report every registered prediction and its outcome.
On such questions, a low score from a reference-guided judge does not reliably mean the answer is wrong.
```
(The first line replaces clause (3) of the preceding sentence, starting at "(3) judges reject such answers ...".)

### 3. First-time reader
Reads well. The premise, the failure, three findings and the practical consequence all arrive in order. The one stumble is the "instruction to match" sentence.

---

## Figure 1 and caption

### 1. Feedback compliance
| Requirement | Status | Evidence |
|---|---|---|
| Keep the 35/80 example exactly | ADDRESSED | The panels show 10.0 / 2.9 / 9.3 unchanged. The v2 panel (c) moved to Appendix Figure 5, and the intro pointer changed from Fig. 1c to §3. |

### 2. Fresh AC critique
- The caption is honest about selection ("selected for a large, clean swap; over the whole pool the swap is about 5 points"). Good.
- Missed opportunity: the example is also P3 in miniature, because the judge gives the reply 10.0 blind. One clause would plant the paper's load-bearing argument on page 1. (nit)

Replacement for caption panel (b):
```latex
\textbf{(b)}~Qwen2.5-7B scores the same text without a reference and with each correct answer as the reference. It accepts the reply blind (10.0), so the drop to 2.9 is not an inability to recognize 80 as correct (\cref{sec:p3}). The example was selected for a large, clean swap; over the whole pool the swap is about 5 points for this judge (\cref{sec:p1}).
```

### 3. First-time reader
Immediately legible. The two-panel version is cleaner than v2's three panels.

---

## Introduction

### 1. Feedback compliance
| Requirement | Status | Evidence |
|---|---|---|
| Keep the 35/80 opening exactly | ADDRESSED | l. 68–72 match v2 word for word; only the pointer changed |
| Survey paragraph: cut to one number and one quote | ADDRESSED | "The judge used by BrowseComp and HLE ... is told 'do not argue for any answer different than [correct_answer]'. Of 43 ... we checked, 35 grade with a single reference or a closed list, and none of the judge prompts we could read tells the judge to credit a correct answer outside it" |
| (e) "none of the judge prompts we could read"; "single reference or a closed list" | DEVIATED-JUSTIFIED | Appendix B read only 34 prompts in full, so "none of the 43" would be unverifiable. Table 2 counts closed lists as reference-guided, so "or a closed list" is the accurate scope. |
| Rest of survey stays in Appendix B | ADDRESSED | The 27/34/"ALWAYS correct" details are only in App. B |
| Readings cut to two sentences, naming dropped | ADDRESSED | "Either the judge checks a candidate against every correct answer, so the reference acts as an answer key, or it rewards the one correct answer it was shown. We rule out the first with three predictions:" ("answer key" is kept because it is the title) |
| Verification-versus-agreement reintroduced where the data separates them | ADDRESSED | §5, "What an inability to verify would predict" |
| Intro shorter; reader reaches P1–P3 holding the example | ADDRESSED | P1–P3 are on page 2 (PDF l. 76–82), about 20 lines after the example |

### 2. Fresh AC critique
- **Logic gap from compressing the readings (should-fix).** "We rule out the first with three predictions" contradicts Table 1, where P3 "Rules out: Inability to verify, alone", not the answer key. The P3 bullet then brings in a third possibility ("not only that the judge cannot verify them") that the two-way framing never mentioned. A careful reader sees that P3 does not do what the sentence says.

  Replacement for l. 81–82:
  ```latex
  Either the judge checks a candidate against every correct answer, so the reference acts as an answer key, or it rewards the one correct answer it was shown.
  P1 and P2 rule out the first; P3 checks that the second is not merely an inability to recognize the other correct answers:
  ```
- **The "What we find" paragraph repeats the abstract's non-sequitur (should-fix).** l. 92: "Much of this comes from the instruction to match. Given the full answer list, the benchmark graders come within a point of it; asking whether the answer is correct shrinks the gap ...". Replacement:
  ```latex
  Much of this comes from the instruction to match: asking whether the answer is correct shrinks the gap where the judge can answer the question, although on harder questions one of our two judges then accepted wrong answers. Given the full answer list, the benchmark graders come within a point of answer-list accuracy (\cref{sec:fix}).
  ```
- l. 77 "The same judges choose among sampled answers and serve as reward signals" overstates: the BrowseComp judge is not an RL reward. Replace "The same judges" with "Such judges". (nit)
- The dagger on the survey sentence (l. 76) is a little odd, since §2 says "Marks apply to effect estimates" and a survey count is not one. Harmless. (nit, no change needed)

### 3. First-time reader
Much better than v2. The example, one quote plus one count, two sentences on the alternatives, then P1–P3. The only snag is the P3 logic hiccup above.

---

## Model section and λ/equation notation removed?

| Requirement | Status | Evidence |
|---|---|---|
| Remove v2 §2 as a standalone section; no "Model" heading | ADDRESSED | No `sec:model`, `eq:model`, "three readings", "P2′" or λ/β/γ anywhere in `main.tex` or `appendix.tex` (grep) |
| Drop λ language from P1 | ADDRESSED | v2 "In the terms of Eq. 1, λ is 3 to 5 points" is gone |
| Remove the fit/disclaimer contradiction | ADDRESSED in the paper; **PARTLY in the supplement** | The composition fit (β, λ, γ) now lives only in `appendix_extended.tex` l. 1099–1100, as a self-contained descriptive model. That is fine. **But `appendix_extended.tex` l. 772 still says "Equation~1 lets the penalty on a correct answer ... shrink as the judge's own confidence rises"**. In the extended appendix, Equation 1 is now the inflation-gap equation `eq:gap` (l. 46), so the sentence points at the wrong equation. |

Replacement (`appendix_extended.tex` l. 772, first sentence; blocker for the supplement):
```latex
Under verification failure, the penalty on a correct answer that differs from the reference should shrink as the judge's own confidence rises and reach zero among answers the judge is sure of.
```

---

## §2 Setup

### 1. Feedback compliance (feedback "Section 3")
| Requirement | Status | Evidence |
|---|---|---|
| Extraction problem gets its own heading | ADDRESSED | "Answer extraction, and what it costs us." (verbatim) |
| Lead with robustness, then the extraction problem | ADDRESSED | The first sentence is "The grading results hold in direction under every answer-labeling scheme we tried ..."; the confession comes second |
| "Every headline result holds under all three schemes" | DEVIATED-JUSTIFIED (c) | Scoped to "every grading AUROC change of the four core open judges and GPT-4.1". This is correct: Table 6 has Mistral-7B at +0.01 on boxed replies, Sonnet 5 and Opus 5 have only any-format labels on the constructed pools, and App. F shows selection losses do not survive relabeling. A literal "every headline result" would be false. |
| Opus 5 audit: don't hide it, don't lead with it | ADDRESSED | Third sentence: "agrees ... on 91%, but confirms only 86% of the rule's credits against the 90% we predicted" |

### 2. Fresh AC critique
- **Factual inconsistency with Appendix F (blocker).** l. 134: "our registered checkers read an answer **only** inside \boxed{} ... so **a** correct answer written in prose counted as wrong". Appendix F (appendix.tex l. 232) says that on the k-pool an unboxed reply "is compared as a whole" and that on the replication pool the checker "needs exactly one integer in the reply's last 100 characters, so **most** answers stated in prose count as wrong". v2 said "usually". A reviewer who checks the appendix finds the main text overstating the checker's strictness, which also slightly overstates the case for switching labels. Replacement:
  ```latex
  The labeling matters because the prompt asks for the answer inside \texttt{\textbackslash boxed\{\}} and our registered checkers read it from there, so most correct answers written in prose counted as wrong; 38\% to 43\% of replies ignore the format.
  ```
- The first sentence names "any-format labels" and "labels read by a model" before they are defined (the definition is two sentences later). This is the cost of the requested reordering. It is acceptable, but a short gloss helps. Replacement for the first sentence (nit):
  ```latex
  The grading results hold in direction under every way of labeling answers we tried (the registered checker, a rule that reads answers in any format, a model's reading, and boxed replies alone): every grading AUROC change of the four core open judges and GPT-4.1 has the same sign, only the magnitude changes, and boxed replies alone give the smallest falls (\cref{app:grid}).\ph{}
  ```
- "Tasks": v2 pointed to the RewardBench-2 Ties exploration (`app:ties`). v3 names Ties with no pointer. Add "(extended appendix)". (nit)
- "We do not correct for multiplicity" across 304 registered predictions will draw a comment. It is disclosed, so no change, but see the overall weaknesses.
- "Candidates and judges" proactively answers "your rubric invites comparison" with the direct-prompt pointer. Good.

### 3. First-time reader
Dense but orderly. The extraction paragraph is now visibly a disclosure rather than something buried. A newcomer needs two passes on the first sentence.

---

## §3 Prediction 1 (the swap)

### 1. Feedback compliance (feedback "Section 4")
| Requirement | Status | Evidence |
|---|---|---|
| Don't touch the structure | ADDRESSED | The result, the 12/12 cells, the "matches neither" control, the MT-Bench template and the masking sentence are all kept. One paragraph was added after them. |
| Drop λ; say "3 to 5 points" directly | ADDRESSED | λ is gone. The individual values (5.25/4.09/3.04; 5.41/3.92/2.66) are given, and "3 to 5 points" appears in the abstract, Table 1 and the Conclusion. See the nit below about anchoring the phrase in §3. |
| Pull one sentence on thinking judges into the main text and address "is this solving itself?" | ADDRESSED | "A judge that thinks before scoring also removes most of the swap on arithmetic ..., which raises the question of whether the problem fades as judges improve. On factual questions it does not: ..." |
| "graders shipped with benchmarks are not reasoning judges" | DEVIATED-JUSTIFIED (a) | The HLE judge is configured with o3-mini (App. M, Table 14), so the literal sentence would be false and a reviewer would catch it. The replacement fact (o3-mini running the HLE judge credits 0%) is true. |
| "(Section 8)" pointer for the factual thinking result | DEVIATED-JUSTIFIED (a) | v2 §8 (= v3 §7) no longer carries the thinking result. It is in App. L (35.6 → 14.9), so `app:acceptance` is the right target. |
| Expression/masked-reference result as one clause | ADDRESSED | "On arithmetic, it survives a reference written in words but mostly vanishes when the reference is written as an expression or masked inside a worked solution (Appendix J)." |

### 2. Fresh AC critique
- **Number misstated (blocker).** l. 145 "Rubric *b* gives up to 6.3." Table 8 (rubric *b*, Qwen2.5-7B, original scorer) gives +6.34 onto and **−6.58** off, so the largest swap is 6.6, not 6.3. Replacement:
  ```latex
  Rubric~$b$ gives larger swaps for Qwen2.5-7B ($+6.34$ onto and $-6.58$ off; \cref{tab:rotation}).
  ```
- **The thinking paragraph contradicts itself and uses a confounded example (should-fix).** "On factual questions it does not [fade]" is followed immediately by "shrinks from 36 to 15 points". And o3-mini is running a prompt that says "focus only on whether the answers match". That shows reasoning does not rescue a grader told to match; it does not show a reasoning judge's own pull persists. A hostile reviewer will split these apart. Replacement for l. 149:
  ```latex
  A judge that thinks before scoring removes most of the swap on arithmetic (\cref{app:reasoning}), which raises the question of whether the problem fades as judges improve. On factual questions it shrinks but does not disappear: with adaptive thinking, the rise in Sonnet~5's false rejections falls from 36 to 15 points (\cref{app:acceptance}), and Sonnet~5 still under-credits differing correct answers under every reasoning prompt we tried (\cref{sec:cost}). Nor does reasoning protect a grader told to match: o3-mini, a reasoning model, running the HLE judge credits almost no correct answer that differs from the reference (\cref{sec:cost}).
  ```
  (Checked: Table 17, Sonnet 5 referenced shortfall −3.4 to −6.2 with every CI excluding zero; App. L 35.6 → 14.9.)
- The masking clause says "it [the swap] survives ... vanishes", but Table 10 measures the *margin* (matching minus non-matching), not the swap. Replace "it survives a reference written in words" with "the reference's pull (its margin) survives a reference written in words". (nit)
- "All twelve registered cells (two judges, ...)": name the judges ("Qwen2.5-7B and phi-4"), since three judges were just listed. (nit)
- The Qwen2.5-7B values 5.25/5.41 are exact-scorer numbers. Table 8, which the reader lands on, shows original-scorer +4.97/−5.04, and the exact values appear only rounded in Fig. 5. Add to the Table 8 caption: "exact scorer for Qwen2.5-7B: $+5.25$ onto, $-5.41$ off (\cref{fig:rotation-pool})". (nit)
- Optional: add "(about 3 to 5 points)" after "3.04 under Sonnet~5; text it moves off loses 5.41, 3.92, and 2.66" so the Table 1 phrase is anchored in §3. (nit)

### 3. First-time reader
Still the cleanest section. The new paragraph answers the obvious "won't better models fix this" question in three lines, and the rewrite above stops it from over-answering.

---

## §4 Prediction 2

### 1. Feedback compliance (feedback "Section 5")
| Requirement | Status | Evidence |
|---|---|---|
| One sentence next to the headline estimates: post hoc, direction holds for every judge and every labeling, only magnitude moves, ledger has the pre-specified version | ADDRESSED (two sentences) | "The constructed-pool estimates are post hoc because they use the any-format labels adopted after the registered checker proved too strict. The pre-specified estimate, Qwen2.5-7B on the replication pool under the registered labels, falls by 0.29, and for all four open judges the direction is the same under every labeling, with only the magnitude moving (0.16 to 0.25 with model-read labels, 0.07 to 0.14 on boxed replies; Table 6)." |
| (b) Factual range not called post hoc; defence cites the registered −0.29 | DEVIATED-JUSTIFIED | Table 23's caption marks the API judges' MACE Reference grading and Qwen2.5-7B's MACE Reference grading as pre-specified, and phi-4's MACE value is daggered in the text. Calling the whole factual range post hoc would misreport the registration. Table 6's caption marks −0.29 as pre-specified. |
| (c) "every judge" narrowed to "all four open judges" | DEVIATED-JUSTIFIED | MACE labels come from answer lists, so there is no labeling choice there. Sonnet 5 and Opus 5 have only any-format labels on the constructed pools. |

Number check: any-format falls from Table 6 are 0.27, 0.24, 0.23, 0.17, 0.19, 0.25 → "0.17 to 0.27" ✓; model-read 0.25, 0.21, 0.21, 0.16, 0.16, 0.22 → "0.16 to 0.25" ✓; boxed 0.10, 0.08, 0.09, 0.07, 0.14, 0.12 → "0.07 to 0.14" ✓; MACE −0.08 / −0.15 / −0.16 / −0.06 (Table 23) ✓; MATH-500 +28.6 / +30.6 (Table 7) ✓.

### 2. Fresh AC critique
- **The verdict drops v2's caveat that API judges barely move on arithmetic (should-fix).** v2 said "On the constructed pools the API judges fall less, by at most 0.08". v3's verdict mentions only Opus 5 on the replication pool and is silent about GPT-4.1 on the constructed pools, where Table 6 shows −0.04 and −0.01 [−0.04, +0.00]. Table 1 ("Holds, except GPT-4.1 on factual questions and Opus 5 on one pool") then suggests GPT-4.1 holds cleanly on arithmetic. A reviewer reading Figure 2b will see frontier judges near zero on arithmetic and conclude the constructed-pool effect is mostly a small-model effect that the text does not admit. Replacement for the first sentence of the Verdict (l. 170):
  ```latex
  P2 holds for Sonnet~5, Opus~5, Qwen2.5-7B, and phi-4 on factual questions and for the four open judges and Sonnet~5 on the constructed pools. On the constructed pools the API judges fall far less than the open judges (by at most 0.08), and the interval includes zero for Opus~5 on the replication pool; GPT-4.1's falls are small everywhere (0.01 to 0.06), and its interval includes zero on factual questions (\cref{app:ledger,tab:labelings-gnm}).
  ```
- The headline sentence (l. 163) chains "and by ... and by" and is hard to parse. Replacement (nit):
  ```latex
  Their grading AUROC against wrong answers falls on factual questions by 0.08 to 0.16 for Qwen2.5-7B, Sonnet~5, and Opus~5 and by 0.06 for phi-4,\ph{} and on the constructed pools by 0.17 to 0.27 for the four open judges\ph{} (\cref{fig:onevsseveral}b).
  ```
- The Figure 2 caption says "Registration status per value is given in the captions of Tables 6 and 23". Neither covers MACE single-answer accuracy (29.4/26.5) or the API judges' constructed-pool grading. Replace with: "Registration status: \cref{tab:labelings-gnm,tab:protocols} and the marks in \cref{sec:p2}; API-judge values are pre-specified." (nit; confirm the API constructed-pool values are registered, which App. K implies)
- Boxed-only falls are about half the any-format falls, and nothing explains why (cleaner replies are easier to verify? extraction mismatch?). A reviewer will ask. One clause in App. F would pre-empt it. (nit)

### 3. First-time reader
Clear. The defence sits next to the numbers as requested. The only thing a newcomer misses is how much smaller the effect is for frontier judges on arithmetic, which is the should-fix above.

---

## §5 Prediction 3

### 1. Feedback compliance (feedback "Section 6")
| Requirement | Status | Evidence |
|---|---|---|
| Give it room (take space from the cut model section) | ADDRESSED | Grew from about 8 lines (v2) to about 25 lines of text, with three paragraphs plus the verdict |
| Spell out what verification failure predicts and why we don't see it | ADDRESSED | "A judge that accepts a correct answer with no reference in front of it has shown that it can recognize that answer as correct, so showing a different correct answer as the reference should leave its score alone ... Verification failure predicts none." |
| Reintroduce verification vs agreement here | ADDRESSED | "Call this *verification failure* ... The alternative, *agreement*, ..." |
| Promote the control number to its own sentence | ADDRESSED | Own paragraph: "It is not score noise. A second blind call ... gives 3 or below to 2 of the 843 ... against 117 once the reference is shown." |
| Put the control number in the abstract | ADDRESSED | See Abstract |
| Say plainly that blind acceptance is a proxy | ADDRESSED | "Blind acceptance is a proxy for verification, not a direct test of it: a judge can accept an answer without checking it, and Opus 5 gives a blind 10 to 5% to 8% of wrong answers" |

Number check: Table 11 gives 318 + 525 = 843, 41 + 76 = 117, retest 0 + 2 = 2 ✓; MACE 15/81 = 18.5% → 19%, 63/201 = 31% ✓; open MACE 83.3% (527 accepted), 41.9% (775) in `r20_matched_acceptance.tex` ✓; pooled arithmetic Qwen2.5-7B (0.192·1747 + 0.25·699)/2446 = 21% ✓, phi-4 8% ✓.

### 2. Fresh AC critique
- **The strongest evidence is listed last (should-fix).** "Between 19% and 83%" opens with the range's top value, 83%, from Qwen2.5-7B: the weakest verifier, at a post hoc threshold, on factual questions a 7B model barely knows. The extended bins table shows its rejection rate is almost flat across blind confidence (98% below 5, 83% at ≥9.8). That pattern is exactly what a hostile reviewer will call "acceptance is not verification". The clean evidence is Sonnet 5 and Opus 5 (blind 10, same-interface retest, Opus pre-specified). The paper also holds, without using it here, the fact that best answers "the judge demonstrably knows": blind grading AUROC of 0.938/0.936 on these same 40 MACE subsamples (Table 16). Replacement for the second and third sentences of "Answers the judge accepts without a reference" (l. 187, from "Of the correct factual answers ..."):
  ```latex
  Without a reference, Sonnet~5 and Opus~5 separate correct factual answers that differ from the reference from wrong ones with a grading AUROC of 0.94 (\cref{tab:r24-fix}). Yet of the 81 and 201 such answers they give a blind 10, 19\%\ph{} and 31\% score 3 or below once the reference is shown, and none of the 140 matching answers they accepted do (\cref{fig:reasoning}). At their post hoc threshold, the open judges do the same to 42\% (phi-4, 775 answers) and 83\% (Qwen2.5-7B, 527) of the differing factual answers they accept.\ph{} Verification failure predicts none.
  ```
  (About +2 lines.)
- **The correctness-prompt result sits under the wrong heading and is reported selectively (should-fix).** "It is not score noise" goes on to the direct-prompt result, which is about wording, not noise. It also reports only the direct prompt (22%, 14%). Table 21 shows the reasoning prompts at 1.3% to 9.2%, and GPT-4.1 verify-first has a CI that includes zero. A reviewer who opens Table 21 will think the smaller numbers were left out on purpose. Replacement for l. 191:
  ```latex
  Nor is it our rubric's wording: asked only whether the response is correct, GPT-4.1 and Sonnet~5 withdraw credit from 22\% and 14\% of the differing correct answers they accepted blind and from none of the matching ones,\reana{} and from 1\% to 9\% when asked to reason first (\cref{app:r27}); these prompts have no second blind call.
  ```
- The Figure 3 caption lost v2's "Arithmetic rows pool the replication and k-pool data (k-pool only for Qwen2.5-14B and gemma-2-9b)". Without it, App. L's "5% to 57% (by judge and pool)" does not match the plotted 8% minimum for the open judges. Restore that sentence. Also add the MACE counts to App. L ("83.3% of 527 (Qwen2.5-7B) and 41.9% of 775 (phi-4)"), because the open-judge table exists only in the extended appendix. (nit)
- Layout: the "What an inability to verify would predict" paragraph starts at the bottom of page 4 and finishes on page 5 below Figures 2 and 3. The section's central argument is split by two floats. If a rebuild allows, move `fig:reasoning` to `[t]` on page 6 or move Figure 2's source above the §4 heading. (nit)
- The conventions (l. 139) do not say what a mark on a range means. v2's Table 1 caption said "a mark on a range applies to at least one value in it". Restore it in §2 conventions. (nit)

### 3. First-time reader
This is now the best-argued section: premise, sharp prediction, test, noise control, caveat. With the reordering above, a reader meets the frontier-judge evidence first and the 83% as corroboration instead of as the headline.

---

## §6 How much it matters

### 1. Feedback compliance (feedback "Section 7")
| Requirement | Status | Evidence |
|---|---|---|
| Keep prominent | ADDRESSED | Own section with Figure 4; the first paragraph is the shipped-grader result |
| Reframe "Where it matters" as scoping; lead with the positive claim | ADDRESSED | Heading "Who should care: reuse."; "These graders are right for the benchmarks they were written for: ... The failure is about reuse" |
| Numbers: 5.5–18% RL set, 30% NQ-open, MACE, RewardBench-2 Ties | ADDRESSED | All present |
| (d) NQ-open as 30% to 44% | DEVIATED, **partly justified** | Both labelings are real (App. C: 30.0%; GPT-5-mini relabel 87/200 = 43.5%). But App. C also gives 18.5% once answers that changed over time are excluded. Widening only upward while dropping the time-excluded figure is selective. Add the qualifier (should-fix below). |
| Reward-signal sentence: shapes a policy; verifier numbers; concern, not harm | ADDRESSED | "Reward signals are the larger risk, because there the judge does not just report a score but shapes a policy ... credit almost none ... Our exploratory training runs were inconclusive ... we state this as a concern rather than a demonstrated harm." |

Number check: Table 14 gives SimpleQA 53.0/46.7 → "47% to 53%" ✓; BrowseComp/HLE 0.0/0.0/2.3 ✓; −30.4/−34.4 and −66.8/−66.6/−64.9 → "30 to 34", "65 to 67" ✓; Table 20 5.8/0.0 ✓; rubric shortfalls −22.3/−15.6/−20.1 (Table 12), −9.6 (Table 15) → "10 to 22" ✓; Table 18 −17.4/−10.1, blind −5.4/−1.7 ✓; Table 17 0.5 to 6.2 ✓.

### 2. Fresh AC critique
- **Asymmetric use of "either annotator" (blocker).** The paragraph uses the either-annotator upper bound where it strengthens the concern ("up to 18% by either annotator" for the RL set) but drops it where it weakens "their own leaderboards are probably little affected". Table 3 has HLE at **15.0% by either annotator** (v2 stated this). A hostile reviewer who spots this reads the whole scoping paragraph as spin, which is exactly what the feedback asked to avoid.
- **Attribution (should-fix).** "5.5% of questions admit several answers after adjudication, and up to 18% by either annotator~\citep{ma2025generalreasoner}" places the citation as if Ma et al. report 5.5%. These are the paper's own LLM labels (κ ≤ 0.35).
- **Deployment claim outruns evidence (should-fix).** "single-reference grading is already deployed where answers are open: ... benchmarks such as RewardBench-2 Ties and MACE consist of such questions". Nothing shows that these benchmarks are graded by single-reference LLM judges; they are simply made of multi-answer questions. For NQ-open, the survey's own LLM-judge evidence (Kamalloo et al. 2023) is not cited.

Replacement for the "Who should care: reuse." paragraph, first two sentences (l. 212):
```latex
These graders are right for the benchmarks they were written for: 0\% to 3\% of sampled SimpleQA, BrowseComp, and HLE questions have several correct answers by adjudicated LLM labels (up to 15\% on HLE by either annotator; \cref{app:prevalence}), so their own leaderboards are probably little affected. The failure is about reuse, where answers are open: General-Reasoner's single-reference verifier rewards an RL training set~\citep{ma2025generalreasoner} in which, by our labels, 5.5\% of questions admit several answers after adjudication and 18\% by either annotator; 30\% to 44\% of sampled NQ-open questions admit several under our two labelings (18.5\% in the first once answers that changed over time are excluded),\ph{} and LLM judges given its gold answers already grade it~\citep{kamalloo2023evaluating}; and benchmarks built from such questions, such as \textsc{RewardBench-2} Ties and \textsc{MACE}~\citep{malik2025rewardbench2,mace2026}, inherit the failure whenever they are graded against one reference.
```
(About +1.5 lines. The reward-signal sentence that follows is unchanged.)

- "Our own score rubric, with four judges, leaves the models 10 to 22 points below": GPT-4.1's −9.6 is in App. M, not App. L. Change the pointer to `(\cref{app:acceptance,app:r24})`. (nit)
- The Figure 4 caption dropped v2's composition "(396 differing correct, 144 matching correct, 56 wrong ... answer-list accuracy 90.6%)". That composition is what explains the size of −67: two thirds of the correct answers differ from the drawn reference, so a grader told to match must lose about that much. Restore it. A reviewer who works this out alone will call the headline number "by construction"; saying so first defuses it. (nit)
- "What sets the size" overlaps heavily with §7's "When the answers cannot be listed". Acceptable given the page budget. (no change)

### 3. First-time reader
Strong and now pitched correctly: result, who should care, why, what drives it. The fixes above keep the scoping paragraph honest in both directions.

---

## §7 How to fix it

### 1. Feedback compliance
No feedback item targets v3 §7 (the feedback's "Section 8" pointer is handled under §3).

### 2. Fresh AC critique
- **The list fix is partly circular (should-fix).** "the full answer list brings all five benchmark graders within 0.5 points of the answer lists". Correctness is *defined* by those same lists via string containment (App. E), so a grader that copies the list agrees with the labels almost by construction. What the experiment actually shows is that graders *follow* a list, which is still useful. A reviewer will say "you graded against the answer key and matched the answer key". Insert after "(\cref{fig:graders}a)." on l. 222:
  ```latex
  This agreement is partly by construction, because the same lists define which answers count as correct; what it shows is that the graders follow a list when given one.
  ```
- **The most obvious reviewer question is no longer answered in the main text (should-fix).** "Did you just tell the judge that other correct answers count?" v2 §8 answered it. v3 dropped the full-credit sentence from the main text, although Table 23's title is literally "What helps: a full-credit sentence reduces the grading harm". Append to "When the answers cannot be listed" (after l. 225):
  ```latex
  Telling the judge that any correct answer deserves full credit helps but does not suffice: appended to our rubric, it cuts the rise in false rejections on \textsc{MACE} from 36 to 18 points for Sonnet~5 and to 8 for Opus~5\ph{} (\cref{app:acceptance}), and the HLE judge with that statement in place of its match clause still falls 13 to 31 points short (\cref{sec:cost}).
  ```
  (Checked: App. L 35.6 → 18.1 (Table 16), Opus 36.3 − 28.0 = 8.3, post hoc per App. L; Table 18 −12.6 and −31.2.)
- "What did not help": Table 23 reports Reveal − ref. with the original scorer, while its Reference column uses the exact scorer (the §2 default). Adding the two for Qwen2.5-14B gives −0.05, but App. Q says −0.01 against blind. Add to the Table 23 caption: "Reference and Reveal − ref. use different scorers for the open judges, so their sum need not equal the protocol's change against blind." (nit)
- The "Questions beyond the judge" paragraph is a genuinely valuable safety caveat, and the recipe reflects it. Good.

### 3. First-time reader
Actionable and appropriately hedged. The two additions close the obvious "circular" and "just tell it" objections.

---

## §8 Related work

### 1. Feedback compliance
None applies.

### 2. Fresh AC critique
- "The agreement reading resembles sycophancy" (l. 252): "reading" is no longer defined anywhere, because the three-readings frame was removed. Replace with "Agreement (\cref{sec:p3}) resembles sycophancy ...". (nit)
- Coverage is adequate. The intro prior-work sentence duplicates part of §8; acceptable. No change needed otherwise.

### 3. First-time reader
Fine.

---

## §9 Limitations

### 1. Feedback compliance
Feedback (Section 6 item): "We already admit [the proxy] in Limitations". This is kept ("No experiment manipulates verification directly") and the proxy is now also stated in §5. ADDRESSED.

### 2. Fresh AC critique
- Missing: the benchmark-study magnitude depends on the share of correct answers that differ from the drawn reference (about two thirds), and the list-fix agreement is partly by construction. Add to the "Tasks" bullet (nit):
  ```latex
  The size of the benchmark shortfall depends on how many correct answers differ from the drawn reference (two thirds here), and agreement with the full list is partly by construction.
  ```
- v2 listed "MACE's lists miss 2.3% to 8.1% of correct answers" in Limitations. v3 moved it to Setup and §7. That is acceptable.

### 3. First-time reader
Compact and honest.

---

## §10 Conclusion

### 1. Feedback compliance
| Requirement | Status | Evidence |
|---|---|---|
| "we can still cut [it] (if we need space)" | Not needed; kept — DEVIATED-JUSTIFIED | The condition ("if we need space") did not arise: the main text fits in 9 pages. |

### 2. Fresh AC critique
It does repeat the abstract. If space is needed for the should-fix additions, replace it with this non-duplicative version, which saves about 3 lines (nit):
```latex
A reference answer is a sound check when a question has one correct answer and a poor one when it has several: judges favor the correct answer they are shown, even over answers they accept without it, and graders built to match turn that into large under-counts wherever they are reused on open questions. Where the correct answers can be listed, grade against all of them; otherwise, ask whether the answer is correct where the judge can answer the question, and audit disagreements between blind and referenced scores.
```

### 3. First-time reader
Fine, redundant.

---

## AI use, ethics, reproducibility statements

- **AI use**: complete and specific (subjects, graders, labelers, writing assistance, no human labels). The template marks it required and excluded from the page count. No change.
- **Ethics**: states the RL concern with the inconclusive training runs, consistent with §6. No change.
- **Reproducibility**: accurate for the v3 appendix (App. D = totals plus failures; the extended appendix lists everything). No change.
- Appendix B says "24 verbatim judge templates" are in the supplement but "We could read 34 judge prompts in full". Reconcile the counts, e.g. "24 verbatim judge templates (the other 10 prompts are quoted in the records)", if that is the reason. (nit)

---

## Table 1

### 1. Feedback compliance
| Requirement | Status | Evidence |
|---|---|---|
| (f) keep word-only | DEVIATED-JUSTIFIED | An earlier round judged the numeric version too dense; the current table is readable |

### 2. Fresh AC critique
- The P2 verdict "Holds, except GPT-4.1 on factual questions and Opus 5 on one pool" inherits the §4 omission. Replace with "Holds; small for API judges on arithmetic; interval includes zero for GPT-4.1 on factual questions and Opus 5 on one pool". (should-fix, tied to §4)
- The P2 evidence says "drops under every labeling", which is unscoped (Mistral-7B boxed +0.01). Change to "drops under every labeling for the core judges". (nit)
- The feedback calls 2 of 843 "the strongest single number in the paper", yet the table carries it only as "almost never". A word-only table can afford one number per row. P3 evidence: "... a repeated blind call does this for 2 of 843 (117 with the reference) (\cref{sec:p3})". Consequence evidence: "... under-credit such answers heavily (30--67 points; \cref{sec:cost})". (nit)
- Placement: Table 1 lands at the top of page 3, one page after P1–P3 are introduced. Moving its source above `\section{Introduction}` with `[t]` would probably place it on page 2 next to the predictions. Check that Figure 1 stays on page 1. (nit)

### 3. First-time reader
Works as a map. The "Rules out" column makes the P1/P2 versus P3 logic explicit, which is also why the intro sentence "We rule out the first with three predictions" needs the fix above.

---

## Appendix (as a whole)

### Overview table
The "Main text" column is wrong in four rows (checked against every `\cref{app:*}` in main.tex). Should-fix:

| Row | Current | Correct | Evidence (main.tex line) |
|---|---|---|---|
| G Exact scorer | 4 | **2, 4** | l. 138 (§2), l. 170 (§4) |
| H Reasoning and thinking judges | Table 1 | **2, 3** | l. 129 (§2), l. 149 (§3); Table 1 does not cite H |
| J Mechanism | — | **3** | l. 147 (§3) |
| L Acceptance ... | 5, 6 | **3, 5, 6** | l. 149 (§3), l. 194 (§5), l. 209 (§6) |
| K Frontier API judges | 4 | 2, 4 (content), or "—" (no main-text cite) | no `app:frontier` in main.tex; it supports the §2 subsample description and Fig. 2 |
| Q Mitigations | 7 | 4, 7 | Fig. 2 caption points to Table 23 |

Also, row C says "five datasets", but App. C covers 4 + 5 = **nine** datasets. (nit)

### Content
- **Supplement leftover (blocker for the supplement):** `appendix_extended.tex` l. 772 "Equation~1 ..." now points at the inflation-gap equation. Replacement given in the model-section check above.
- **App. F vs §2:** App. F's description of the checker (whole-reply comparison; last-100-characters integer) is the accurate one. Fix §2 as above.
- **App. L:** add n for the open-judge acceptance shares (527, 775), because the table is extended-only (nit). The pooling note is missing from Fig. 3 (nit).
- **Table 8 caption:** add the exact-scorer values quoted in §3 (nit).
- **Table 23:** the scorer mismatch makes the columns non-additive (nit, above).
- **App. D:** Table 4 totals and Table 5's caption agree (37 = 34 + 3 falsified; 14 not confirmed; 304 total). The retroactive-rule disclosure, including the ten predictions that moved against the authors, is exemplary. No change.
- **App. H "Does acceptance mean verification?":** Spearman −0.40 and "associated with a smaller effect but not with its absence" is the right, measured statement. It could be cited from §5's proxy sentence. (optional)
- Overall, the condensed appendix is well organized, each section opens with its registration status, and the pointers resolve. Other than the overview column and the supplement leftover, nothing needs to change.

---

# Overall assessment

**Summary.** The paper shows that when a question has several correct answers, LLM judges given one reference favor that reference. It uses a byte-identical swap test (3–5 points out of 10), grading AUROC against wrong answers (factual falls of 0.06–0.16; arithmetic 0.17–0.27 for open judges, direction robust to four labelings), and a blind-acceptance test with a same-interface noise control (117 vs 2 of 843). Together these rule out the answer-key reading and show the effect is not only an inability to verify. Shipped SimpleQA and BrowseComp/HLE graders, run verbatim on 149 multi-answer MACE questions, under-count by 30–67 points. The paper then attributes much of this to the match instruction, shows a full answer list closes the gap (with a safety caveat on hard questions), and reports a 304-prediction registration ledger including every failure.

**Strengths.**
1. A clean causal design: the swap holds the text fixed; "matches neither" and matching answers serve as within-design controls; the second blind call bounds noise.
2. P3 turns "judges are weak" into "judges defer", and this is now argued explicitly.
3. External validity through verbatim shipped graders, open RL verifiers and several prompt families, with honest scoping (graders are right for their own benchmarks; the risk is reuse).
4. Unusual transparency: labeling robustness, a label audit that failed its registered bound, retroactive verdict rules, and a full failure ledger.
5. An actionable recipe, including a counter-intuitive safety finding (removing the match instruction lets GPT-4.1 overrule correct references on HLE).

**Weaknesses (ranked).**
1. **Frontier-judge effect sizes on the controlled testbed are small.** API judges fall by at most 0.08 in AUROC on arithmetic, and GPT-4.1 by 0.01–0.04. The large constructed-pool numbers come from ≤14B open judges. Factual evidence for frontier judges rests on 40 MACE subsamples and 149 benchmark questions from two MACE domains. v3's P2 verdict currently understates this.
2. **The headline consequence is partly by construction, and so is the fix.** −67 largely follows from the grader being told to match on a pool where two thirds of the correct answers differ from the drawn reference, and "within 0.5 points" with the full list is agreement with the same list that defines the labels. Both are defensible, but neither is said in the main text.
3. **Measurement and registration fragility.** The registered checker was replaced by post hoc any-format labels for the open judges; boxed-only falls are about half as large; the frontier-model audit failed its bound (86% vs 90%); there are no human labels anywhere; prevalence κ ≤ 0.35; the verdict rule was applied retroactively; there is no multiplicity correction across 304 predictions.
4. **Mechanism left open.** Agreement is not separated from "assumes one intended answer" (acknowledged), and blind acceptance is a proxy (the open-judge 83% comes from a flat confidence curve).
5. **Practical harm is argued, not demonstrated.** Prevalence on the named benchmarks is 0–3%, and the RL harm is a stated concern with inconclusive training runs.
6. Small text-level issues a checker will find: rubric *b* "up to 6.3" vs −6.58; "only inside \boxed{}" vs App. F; asymmetric either-annotator reporting; a stale "Equation 1" in the supplement.

**Score: 6 / 10 (marginally above the acceptance threshold). Confidence: 4 / 5.**

**What would raise it.** To 7: apply the blockers and should-fixes (they remove the checkable inconsistencies and pre-empt the "by construction" and "just tell it" objections). To 8: a human-labeled validation of the any-format labels and of MACE list completeness on the 149-question set; a second natural multi-answer source beyond MACE (e.g. AmbigQA or QAMPARI) graded by a shipped grader; a larger frontier-judge factual sample (hundreds of tasks, not 40); or a small RL run showing a policy shifting toward reference-matching answers under a single-reference reward.

---

# Compliance table

| # | Feedback item | Status |
|---|---|---|
| I-1 | Keep the 35/80 opening exactly | ADDRESSED |
| I-2 | Survey cut to one number and one quote; rest to App. B | ADDRESSED (wording (e) DEVIATED-JUSTIFIED) |
| I-3 | Readings to two sentences, no naming | ADDRESSED (should-fix: P3 logic sentence) |
| I-4 | Reintroduce verification vs agreement in P3 | ADDRESSED |
| I-5 | Intro shorter; reader reaches P1–P3 with the example in mind | ADDRESSED |
| M-1 | Remove the model section; no "Model" heading; readings once in the intro, then P1–P3, then Setup | ADDRESSED |
| M-2 | Drop λ from P1; say 3–5 points directly | ADDRESSED |
| M-3 | Remove the "disclaimer vs fit" contradiction | ADDRESSED in paper; PARTLY in supplement (stale "Equation 1", appendix_extended l. 772) |
| S-1 | Extraction gets its own heading | ADDRESSED |
| S-2 | Lead with robustness, then the confession | ADDRESSED |
| S-3 | Robustness clause in the abstract | ADDRESSED (nit: scope) |
| S-4 | "Every headline result holds under all schemes" | DEVIATED-JUSTIFIED (c) |
| S-5 | Opus 5 audit neither hidden nor leading | ADDRESSED |
| P1-1 | Don't touch the P1 structure | ADDRESSED |
| P1-2 | Thinking-judge sentence in the main text, addressed head-on | ADDRESSED (should-fix: wording) |
| P1-3 | "Shipped graders are not reasoning judges"; "(Section 8)" pointer | DEVIATED-JUSTIFIED (a) |
| P1-4 | Expression/masked result as one clause | ADDRESSED |
| P2-1 | Post hoc defence sentence next to the headline estimates | ADDRESSED |
| P2-2 | Factual range labeled post hoc | DEVIATED-JUSTIFIED (b) |
| P3-1 | Give P3 room | ADDRESSED |
| P3-2 | Spell out what verification failure predicts | ADDRESSED |
| P3-3 | Control number in its own sentence | ADDRESSED |
| P3-4 | Control number in the abstract | ADDRESSED (should-fix: add the 117 comparator) |
| P3-5 | State plainly that blind acceptance is a proxy | ADDRESSED |
| C-1 | Keep the consequence section prominent | ADDRESSED |
| C-2 | Reframe "Where it matters" as scoping, lead with the positive claim | ADDRESSED (blocker: HLE 15% either-annotator omission) |
| C-3 | 5.5–18% RL, NQ-open, MACE, RB2 Ties | ADDRESSED; NQ-open 30–44% (d) DEVIATED, partly justified (add the 18.5% qualifier) |
| C-4 | Reward-signal sentence with verifier numbers, concern not harm | ADDRESSED |
| K-1 | Conclusion can be cut if space is needed | DEVIATED-JUSTIFIED (space not needed) |
| T-1 | Table 1 word-only | DEVIATED-JUSTIFIED (f) |

---

# Prioritized fix list

## Blockers (checkable errors or selective reporting; fix before submission)

**B1. §2 Setup, l. 134: checker description contradicts App. F.**
```latex
The labeling matters because the prompt asks for the answer inside \texttt{\textbackslash boxed\{\}} and our registered checkers read it from there, so most correct answers written in prose counted as wrong; 38\% to 43\% of replies ignore the format.
```

**B2. §3, l. 145: "Rubric *b* gives up to 6.3" understates Table 8 (−6.58).**
```latex
Rubric~$b$ gives larger swaps for Qwen2.5-7B ($+6.34$ onto and $-6.58$ off; \cref{tab:rotation}).
```

**B3. §6, l. 212: either-annotator bound used for the RL set but omitted for HLE (15%); citation misattributes our 5.5%.** Replace the first two sentences of "Who should care: reuse." with:
```latex
These graders are right for the benchmarks they were written for: 0\% to 3\% of sampled SimpleQA, BrowseComp, and HLE questions have several correct answers by adjudicated LLM labels (up to 15\% on HLE by either annotator; \cref{app:prevalence}), so their own leaderboards are probably little affected. The failure is about reuse, where answers are open: General-Reasoner's single-reference verifier rewards an RL training set~\citep{ma2025generalreasoner} in which, by our labels, 5.5\% of questions admit several answers after adjudication and 18\% by either annotator; 30\% to 44\% of sampled NQ-open questions admit several under our two labelings (18.5\% in the first once answers that changed over time are excluded),\ph{} and LLM judges given its gold answers already grade it~\citep{kamalloo2023evaluating}; and benchmarks built from such questions, such as \textsc{RewardBench-2} Ties and \textsc{MACE}~\citep{malik2025rewardbench2,mace2026}, inherit the failure whenever they are graded against one reference.
```
(This also resolves should-fix items on NQ-open (d) and on the RB2 Ties/MACE deployment wording.)

**B4. Supplement, `appendix_extended.tex` l. 772: stale "Equation~1" now points at the inflation equation.**
```latex
Under verification failure, the penalty on a correct answer that differs from the reference should shrink as the judge's own confidence rises and reach zero among answers the judge is sure of.
```

## Should-fix

**S1. Abstract: add the comparator, fix the instruction-to-match non-sequitur, drop "these predictions" and "complete preregistration ledger".** Replace from "(3) judges reject such answers ..." to the end:
```latex
(3) judges reject such answers even after accepting them without a reference: once the reference is shown, 117 of 843 accepted answers score 3 or below, against 2 of 843 on a repeated call without it, so an inability to verify them cannot alone explain the effect.
Those benchmarks rarely contain such questions, but run verbatim on 149 factual questions that do, with a reference drawn at random from each answer list, their graders score four models 30 to 67 points below their answer-list accuracy.
Much of this comes from the instruction to match: asked instead whether the answer is correct, judges shrink the gap on questions they can answer. Given the full answer list, the benchmark graders come within a point of answer-list accuracy.
We run these tests with more than a dozen judges on constructed tasks, MACE, and MATH-500, and report every registered prediction and its outcome.
On such questions, a low score from a reference-guided judge does not reliably mean the answer is wrong.
```

**S2. Intro l. 81–82: P3 does not rule out the answer key (contradicts Table 1).**
```latex
Either the judge checks a candidate against every correct answer, so the reference acts as an answer key, or it rewards the one correct answer it was shown.
P1 and P2 rule out the first; P3 checks that the second is not merely an inability to recognize the other correct answers:
```

**S3. Intro l. 92: same non-sequitur as the abstract.** Replace from "Much of this comes from the instruction to match." through "(\cref{sec:fix})." with:
```latex
Much of this comes from the instruction to match: asking whether the answer is correct shrinks the gap where the judge can answer the question, although on harder questions one of our two judges then accepted wrong answers. Given the full answer list, the benchmark graders come within a point of answer-list accuracy (\cref{sec:fix}).
```

**S4. §3 l. 149: "does not [fade]" vs "shrinks"; o3-mini is confounded with the match instruction.**
```latex
A judge that thinks before scoring removes most of the swap on arithmetic (\cref{app:reasoning}), which raises the question of whether the problem fades as judges improve. On factual questions it shrinks but does not disappear: with adaptive thinking, the rise in Sonnet~5's false rejections falls from 36 to 15 points (\cref{app:acceptance}), and Sonnet~5 still under-credits differing correct answers under every reasoning prompt we tried (\cref{sec:cost}). Nor does reasoning protect a grader told to match: o3-mini, a reasoning model, running the HLE judge credits almost no correct answer that differs from the reference (\cref{sec:cost}).
```

**S5. §4 Verdict l. 170 (and the Table 1 P2 verdict): API judges' small arithmetic effects omitted.** Replace the first sentence of the Verdict with:
```latex
P2 holds for Sonnet~5, Opus~5, Qwen2.5-7B, and phi-4 on factual questions and for the four open judges and Sonnet~5 on the constructed pools. On the constructed pools the API judges fall far less than the open judges (by at most 0.08), and the interval includes zero for Opus~5 on the replication pool; GPT-4.1's falls are small everywhere (0.01 to 0.06), and its interval includes zero on factual questions (\cref{app:ledger,tab:labelings-gnm}).
```
Table 1, P2 verdict cell: `Holds; small for API judges on arithmetic; interval includes zero for GPT-4.1 on factual questions and Opus~5 on one pool`

**S6. §5 l. 187: lead with the frontier judges and their blind verification ability; give n for the open judges.** Replace from "Of the correct factual answers ..." to "Verification failure predicts none." with:
```latex
Without a reference, Sonnet~5 and Opus~5 separate correct factual answers that differ from the reference from wrong ones with a grading AUROC of 0.94 (\cref{tab:r24-fix}). Yet of the 81 and 201 such answers they give a blind 10, 19\%\ph{} and 31\% score 3 or below once the reference is shown, and none of the 140 matching answers they accepted do (\cref{fig:reasoning}). At their post hoc threshold, the open judges do the same to 42\% (phi-4, 775 answers) and 83\% (Qwen2.5-7B, 527) of the differing factual answers they accept.\ph{} Verification failure predicts none.
```

**S7. §5 l. 191: the correctness-prompt result is under the "noise" heading and omits the reasoning-prompt rates (Table 21).**
```latex
Nor is it our rubric's wording: asked only whether the response is correct, GPT-4.1 and Sonnet~5 withdraw credit from 22\% and 14\% of the differing correct answers they accepted blind and from none of the matching ones,\reana{} and from 1\% to 9\% when asked to reason first (\cref{app:r27}); these prompts have no second blind call.
```

**S8. §7 l. 222: the full-list fix is partly circular.** Insert after "(\cref{fig:graders}a).":
```latex
This agreement is partly by construction, because the same lists define which answers count as correct; what it shows is that the graders follow a list when given one.
```

**S9. §7 after l. 225: answer "did you just tell it other answers count?"**
```latex
Telling the judge that any correct answer deserves full credit helps but does not suffice: appended to our rubric, it cuts the rise in false rejections on \textsc{MACE} from 36 to 18 points for Sonnet~5 and to 8 for Opus~5\ph{} (\cref{app:acceptance}), and the HLE judge with that statement in place of its match clause still falls 13 to 31 points short (\cref{sec:cost}).
```

**S10. Appendix overview "Main text" column.** G: `\ref{sec:setup}, \ref{sec:p2}`; H: `\ref{sec:setup}, \ref{sec:p1}`; J: `\ref{sec:p1}`; L: `\ref{sec:p1}, \ref{sec:p3}, \ref{sec:cost}`; Q: `\ref{sec:p2}, \ref{sec:fix}`; C contents: "nine datasets".

## Nits
- Fig. 1 caption (b): add "It accepts the reply blind (10.0), so the drop to 2.9 is not an inability to recognize 80 as correct (\cref{sec:p3})."
- Fig. 3 caption: restore "Arithmetic rows pool the replication and $k$-pool data ($k$-pool only for Qwen2.5-14B and gemma-2-9b)."
- Fig. 4 caption (a): restore "(396 differing correct, 144 matching correct, 56 wrong; answer-list accuracy 90.6\%)".
- Fig. 2 caption: fix the registration pointer (Tables 6 and 23 do not cover MACE k=1 accuracy or the API constructed-pool grading).
- §2 l. 133: gloss the labeling schemes in the first sentence (replacement above); add "(extended appendix)" after RewardBench-2 Ties (l. 124); restore "a mark on a range applies to at least one value in it" to the conventions.
- §3: "the reference's pull (its margin) survives a reference written in words"; name the two registered judges; add "(about 3 to 5 points)"; add the exact-scorer values to the Table 8 caption.
- §4 l. 163: de-chain the "and by ... and by" sentence (replacement above).
- §6: rubric pointer `(\cref{app:acceptance,app:r24})`.
- §8 l. 252: "The agreement reading" → "Agreement (\cref{sec:p3})".
- §9 Tasks bullet: add the by-construction sentence (above).
- §10: optional non-duplicative Conclusion (above; saves about 3 lines).
- Intro l. 77: "The same judges" → "Such judges".
- Abstract (2): optionally scope "under every answer-labeling scheme we tried" to the core judges.
- Table 1: add "2 of 843 (117 with the reference)" to P3 and "30--67 points" to Consequence; "every labeling for the core judges"; consider moving the float so it lands on page 2.
- Table 23 caption: note that the Reference and Reveal − ref. columns use different scorers and are not additive.
- App. L: add n (527, 775) to the MACE open-judge shares.
- App. B: reconcile "24 verbatim judge templates" with "34 judge prompts in full".
- Layout: the §5 central paragraph is split across Figures 2 and 3; consider float placement.
