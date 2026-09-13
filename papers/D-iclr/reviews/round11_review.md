# Round 11 review: "The Reference Is Not an Answer Key: LLM Judges Reward Agreement When Several Answers Are Correct"

Reviewer role: harsh NeurIPS reviewer / ICLR area chair. I read the full 39-page PDF (`round11_main.pdf`), `main.tex`, `appendix.tex`, `figures/fig1_concept.tex`, and `scripts/make_figures.py`. I spot-checked numbers against `r4_results.json`, `r8_sonnet_results.json`, `r8_lenient_results.json`, `r9_inflation_relabeled*.json`, `r9_sonnet_item_level.json`, `p17_coverage_results.json`, and `registration_round8.md`. I did not open earlier reviews or the supplement.

---

## Summary

The paper argues that when a question has several correct answers, an LLM judge treats the reference as "one sample" of them and rewards agreement with it, rather than using it as an answer key. It sets up three readings (answer key, one sample, verification failure) and three predictions:
- **P1:** swapping which correct answer is the reference moves the score of byte-identical text.
- **P2:** the reference helps with one correct answer and hurts grading of the other correct answers with several.
- **P3:** the effect is not a failure to verify.

The evidence comes from constructed constraint tasks with enumerated answer sets (replication pool, k-pool, synthetic grid), two audited MACE factual domains, MATH-500, and MBPP. Candidates come mostly from one generator (Llama-3.1-8B). Judges are small open models (scoring in about four tokens), Qwen3 with thinking on and off, Claude Sonnet 5, and GPT-4.1.

What the evidence shows:
- **P1 is very convincing.** Qwen2.5-7B gains +5.25 when the reference moves onto its answer and loses -5.41 when it moves off, with a near-zero placebo. phi-4 and Sonnet 5 show the same pattern. The masking and rewriting suite strengthens it.
- **The P2 grading harm is real and robust to relabeling**, but much smaller on natural data for the open judges.
- **P3 is where the argument breaks.** The tests do not cleanly separate the proposed reading from verification failure, and much of the evidence fits verification failure.
- **Selection costs are mixed** and largely disappear once answers written in prose are counted as correct.
- **Registration practice is unusually transparent**: all 156 predictions are ledgered and failures are reported.

The paper is honest and careful. It is not yet clean. The story is diluted by a fourth "costs" axis, a figure spent on a test the paper itself calls non-independent, overbroad quantifiers, and a P3 whose logic does not hold.

---

## Scores

| | Score |
|---|---|
| Overall (ICLR scale) | **5** (marginally below the acceptance threshold) |
| Presentation (1–4) | **2** |
| Soundness (1–4) | **3** |
| Contribution (1–4) | **2** |
| Confidence (1–5) | **4** |

**Would I champion this at 8+? No.**

These conditions, all doable by rewriting, re-scoping, re-plotting, or re-analyzing existing data, would get me to 8:
1. **Make the readings-by-predictions logic explicit.** Add a matrix in Section 2 showing which reading predicts what. Admit that P1 and P2 rule out only the answer key. Rewrite P3 as "not *only* a failure to verify", lead it with the discriminating evidence, and correct the misattributed instruction result (Must-fix 1).
2. **Define "reasoning".** Resolve the MT-Bench contradiction everywhere it appears: abstract, P1 verdict, P3, conclusion (Must-fix 2).
3. **Tie every quantifier to the configurations actually tested** ("every judge", "3 to 5 points", "12 judge–pool pairs with fine-grained scores", "twelve judges", "treat the one they are shown as the only one") (Must-fix 3).
4. **Fix Equation (1)** so it actually implies the grading-AUROC prediction (Must-fix 4).
5. **Re-scope the k=1 half of P2** and mark the post hoc relabeling that rescues it (Must-fix 5).
6. **Rebuild the main-text visual story.**
   - Figure 1 should carry the three readings and the one-vs-several contrast, not only P1.
   - Figure 2 (inflation) goes to the appendix and is replaced by an independent P2 figure.
   - One color and marker grammar is used throughout (Must-fix 6, Should-fix 1–3).
7. **Make Table 1 verifiable**: per-claim evidence labels, the relevant failed predictions (composition dose, MACE blind margin), and the "Costs" row demoted (Must-fix 7).

With (1)–(4) alone I would move to 6. The 8 needs the presentation work too.

---

## Strengths

1. **The swap test is exactly the right experiment and is executed cleanly.** Byte-identical text with only the reference moved, three readouts per cell (onto, off, neither), and a placebo near zero (Table 4: "Neither" +0.13 [-0.04, +0.31] for Qwen2.5-7B rubric a). An answer key cannot produce this, and the rubric, scorer, and judge-family replications make it hard to dismiss.
2. **The mechanism probes are good science.** Pre-specified rewrites (Table 28) show matching on the literal answer: "thirty-one" keeps phi-4's margin (+3.68 vs +3.79), "30+1" cuts it by 77–94%, and masking removes it. The encoded-reference cells for phi-4 are honestly declared not evaluable (Table 29).
3. **Transparency is well above the norm.**
   - Every registered prediction is scored (Table 3), including 15 falsified and 10 not confirmed.
   - The verdict-rule change and which verdicts moved against the authors are disclosed.
   - A contaminated CLI run was discovered and excluded (Appendix H, "very likely included a git status listing recent commit messages that name the anchoring hypothesis").
   - Checker bugs are reported. "Failed nearby" in Table 1 is a good idea.
4. **The authors relabel against their own interest.** The any-format and model-read relabeling is applied symmetrically and shrinks the selection-cost claim (Table 12). Reviewers will trust this.
5. **The reasoning toggle is well designed.** Same weights, thinking on versus off (Tables 42, 50), and it produces a clean arithmetic-versus-factual dissociation (Figure 4b).
6. **The main numbers match the analysis outputs.** I checked:
   - Rotation: +5.2507 / -5.4051 / +0.1157 (`r4_results.json` → Section 4, Figure 1c).
   - Sonnet 5 MACE AUROC: 0.9378 → 0.7847, false-rejection change +0.3563 (`r8_sonnet_results.json` → abstract, Section 5).
   - Blind-accepted answer-level shares: 0.0923 / 0.218 / 0.3487 (`r9_sonnet_item_level.json` → Section 6).
   - Inflation: pooled +1.186 (registered) and +1.137 (any format); k-pool k=1 relabeled -0.268 / -0.145 (`r9_inflation_relabeled*.json` → Sections 5 and 7).
   - Ledger arithmetic: 92 + 10 + 15 + 16 + 18 + 2 + 3 = 156.
7. **Compliance.**
   - The main text ends on page 9 (Conclusion, line 451).
   - AI-use, ethics, and reproducibility statements are present.
   - The PDF metadata Author field is empty, OSF links are withheld, and I found no deanonymizing text.

---

## Must-fix before submission (ranked)

### 1. P3 does not discriminate the readings, and part of its verdict is attributed to the wrong reading
**Where:** §1 "Three readings of a reference" and P3 bullet (p. 2); §2, Eq. (1) paragraph (p. 3); §6 whole section and Verdict (pp. 6–7); Table 1 P3 row; abstract sentence 5.

**What is wrong.**
- **(a) Only P3 separates the two non-answer-key readings.** Under verification failure ("the judge cannot tell that the other answer is correct, so the reference is its only evidence"), swapping the reference also moves the score of fixed text (P1). The reference also helps at k=1 and hurts non-matching correct answers at k>1 (P2). So P1 and P2 refute only the answer key. The paper never says this, and "Three predictions separate these readings" (p. 2) is false as written.
- **(b) Most P3 evidence is what verification failure predicts.**
  - Anchoring shrinks with judge strength: 9.5 → 3.1 points from Qwen2.5-1.5B to 14B (Table 5), and Sonnet 5 is at about 60% of Qwen2.5-7B.
  - It vanishes where the judge demonstrably verifies: with thinking on, "valid rotation samples receive 10 in 99.8% of referenced replies and 96.2% of blind ones" (App. N).
  - It persists where verification is weak: factual blind verification AUROC is 0.72–0.81 (Table 50), against 0.85–0.86 on arithmetic.
  - The paper's own verdict concedes this ("which is what a verification-failure account predicts in those cases").
- **(c) The instruction result is misattributed.** "Telling the judge that other correct answers deserve full credit closes phi-4's margin" is not what verification failure predicts. An instruction gives a judge that cannot verify no new ability to verify. Removing a deference habit by instruction is what the *one-sample/agreement* reading predicts. The verdict sentence "It disappears ... for phi-4 when told that other answers are valid, which is what a verification-failure account predicts" has it backwards. The instruction test also does not appear in the P3 prediction (which lists only accepted answers, stronger judge, reasoning), yet Table 1's Test column includes "instruction".
- **(d) The "answers the judge already accepted" test is nearly vacuous.** The ≥7 blind filter keeps 96% (Qwen2.5-7B), 98% (phi-4), and 91% (Sonnet 5, 3,194/3,494) of samples (Table 4 caption, §6). A swap gain "as large as over all samples" is mechanically guaranteed. It is also daggered post hoc in the main text, yet it carries the abstract's P3 claim ("it persists for answers the judge accepted without a reference").
- **(e) The genuinely discriminating evidence is buried.**
  - Appendix N: on factual MACE, "Blind, Sonnet 5 ranks both correct answers above the wrong one 94.4% and 96.9% of the time, so it anchors on these questions although it can verify them."
  - §6 answer-level result: 35% of blind-accepted non-matching correct MACE answers drop to ≤3.

  These are the only results where the judge demonstrably can verify and still anchors.

**Fix (rewrite, move, re-scope; no new data).**
1. In §2, add a 4×3 matrix (small table or inline figure) with columns *answer key / verification failure / agreement (ours)*:
   - P1, swap moves identical text: no / yes / yes.
   - P2, k=1 helps and k>1 grading harm: no harm / yes / yes.
   - P3a, answers the judge verifiably accepts still move: no / no / yes.
   - P3b, effect shrinks as verification improves: n/a / yes / not required.

   Replace "Three predictions separate these readings:" with: *"P1 and P2 distinguish the answer key from the other two readings; only P3 distinguishes agreement from verification failure."*
2. Rename P3 to **"The effect is not only a failure to verify."** Replace the P3 bullet with: *"If judges anchored only because they could not verify the other answer, anchoring would vanish on answers the judge demonstrably verifies without a reference."*
3. Rebuild §6 in this order:
   1. Verified-and-still-anchors evidence (Sonnet 5 pairwise 94.4%/96.9% on MACE, moved from App. N; answer-level 9%/22%/35%).
   2. The ≥7 filter, stated with its retention rates and demoted to one sentence.
   3. Scaling and reasoning, reported openly as *consistent with a verification component*.
   4. Instructions, reattributed.
4. New verdict: *"P3 partly holds. Anchoring shrinks as judges become able to check answers (larger Qwen2.5 judges, Sonnet 5, thinking on arithmetic), so verification failure contributes. But Sonnet 5 anchors on factual questions whose answers it ranks correctly 94–97% of the time blind, and an instruction that other answers are valid removes phi-4's margin, which a pure verification failure cannot explain. Both mechanisms operate."*
5. Optional new analysis on existing scores: stratify the swap change by per-task blind AUROC and report the slope (the split-half design of Table 49 already exists for AUROC change). This directly tests P3b.

### 2. "Reasoning before scoring" is undefined, and the MT-Bench result contradicts the headline
**Where:** abstract ("judges that reason before scoring stop anchoring on arithmetic"); §1 P3 bullet; §4 Verdict (p. 4); §6 "Reasoning before scoring"; Figure 4a; §10 Conclusion ("Judges that reason before scoring escape this on arithmetic").

**What is wrong.**
- The §4 verdict lists "the MT-Bench template" among configurations that "score without reasoning". Appendix C files the same template under "Judges that explain or think before scoring", and the template "asks the judge ... to explain before a rating". Under it Qwen2.5-7B still loses 3.59 points (§6: "Writing an explanation alone is not enough").
- The Sonnet 5 CLI "reasoning" arm ran with **thinking off** and a visible reasoning line (App. N).
- Qwen3 "thinking off" writes about 159 tokens before its "Score: N" line (Table 42). This contradicts §3's "Each answers with an integer from 0 to 10 in at most four tokens", which lists Qwen3 among the open judges.
- So of four explain- or think-first configurations, three lose the effect on arithmetic and one (MT-Bench) does not. The abstract and conclusion state it as general.

**Fix.**
- In §3, define two protocol classes: *score-only* (≤4 tokens, or an integer after no rationale) and *rationale-first* (extended thinking, or a written rationale before the score). Move Qwen3 and MT-Bench out of the "four tokens" sentence.
- §4 verdict: *"P1 holds for every score-only configuration we swapped (Qwen2.5 1.5B–14B, phi-4, Sonnet 5, Qwen3 with thinking off) and for Qwen2.5-7B under the MT-Bench explain-first template."*
- Abstract and conclusion: *"judges that think before scoring stop anchoring on arithmetic, where they can check the answer, though a short written explanation (the MT-Bench template) does not stop it."*

### 3. Quantifiers exceed the configurations tested
**Where and fix, item by item:**
- **(a) §1 "What we find" (p. 2).** The paper says: "P1 holds for every judge that scores without reasoning: identical text gains 3 to 5 points when the reference moves onto its answer and loses as much when it moves off."
  - The swap was never run for gemma-2-9b, Llama-3.1-8B, Mistral-7B, or GPT-4.1 (4 of the 12 judges; I found no rotation for them in the appendix).
  - Qwen3 with thinking off moves +0.57 / -0.69 (8B) and +1.73 / -1.98 (14B) (Table 50).
  - Qwen2.5-1.5B and 3B move about 9.5 (Table 5).
  - **Replace with:** *"P1 holds in every score-only configuration we swapped (eight judge configurations): identical text gains 3 to 5 points for Qwen2.5-7B, phi-4, and Sonnet 5 when the reference moves onto its answer and loses about as much when it moves off; the swing ranges from under 1 point (Qwen3-8B, thinking off) to over 9 (Qwen2.5-1.5B)."*
- **(b) Table 1 and §5.** Table 1 defines "Fine-grained" as "the four open judges whose scores passed our score-resolution screen (Qwen2.5-7B, phi-4, Qwen2.5-14B, gemma-2-9b)". The P2 row and §5 then claim "inflation higher at k>1 in all 12 judge–pool pairs with fine-grained scores". Those 12 pairs include Qwen2.5-1.5B, Qwen2.5-3B, and Llama-3.1-8B on the synthetic grid, which were never screened.
  - **Replace with:** *"in all 12 judge–pool pairs we ran with probability-based scores (four judges on the k-pool, six on the synthetic grid, two on MACE)."* Keep "fine-grained" strictly for the screened four.
- **(c) "Table 1 lists every test" (p. 2).** It does not. **Replace with:** "Table 1 lists the main tests."
- **(d) Abstract "We test three predictions with twelve judges".** The core tests rest on Qwen2.5-7B, phi-4, and Sonnet 5. **Replace with:** *"with up to twelve judges (core tests: Qwen2.5-7B, phi-4, Claude Sonnet 5)"*.
- **(e) Conclusion "judges treat the one they are shown as the only one".** A 3–5 point swing on a 10-point scale, and 9% false rejections for Sonnet 5 on the replication pool, is partial credit for agreement, not exclusivity. **Replace with:** *"judges give extra credit to the one they are shown."*
- **(f) §7 "but not for gemma-2-9b".** Table 38 shows gemma's reveal-minus-reference as -0.20 [-0.34, -0.05], a significant shrink. **Replace with:** *"and barely for gemma-2-9b (−0.20 SD)."*
- **(g) Limitations "Most open judges have at most 14B parameters".** All of them do. **Replace "Most" with "All".**

### 4. Equation (1) does not imply the grading-AUROC prediction it is used to derive
**Where:** §2, Eq. (1) and the following paragraph (p. 3): "correct answers that differ from a⋆ lose ground to wrong answers, more so when β < 1 dilutes the judge's own assessment (P2)."

**What is wrong.**
- Grading AUROC compares non-matching correct answers with wrong answers. Neither group matches a⋆, so under Eq. (1) both scores are β·b(c).
- AUROC is rank-based, and multiplying by β > 0 preserves ranks. Eq. (1) therefore predicts **no change** in grading AUROC, whatever the value of β.
- The drop must come from something outside Eq. (1): noise that does not shrink with β, floor compression, or a bonus for wrong answers containing the reference text. The lure term γ appears in Appendix I's model and in Table 17, where 23.6% of wrong replication candidates contain the reference's answer and removing them shrinks the drop to -0.24 / -0.20.
- A reviewer with a pencil will catch this on page 3 and stop trusting the formalism.

**Fix.** Replace Eq. (1) with

  s(c; a⋆) ≈ β b(c) + λ 𝕀[ans(c) = a⋆] + γ 𝕀[c wrong and contains a⋆] + ε,  λ > 0, β ≤ 1,

and replace the sentence with: *"...correct answers that differ from a⋆ lose rank against wrong answers when β < 1 shrinks the judge's own signal relative to score noise ε, or when wrong answers that contain a⋆ collect part of the bonus (γ > 0)."*

In §5, add one clause with the look-alike numbers: *"Removing wrong answers that contain the reference's answer shrinks the fall to 0.24 and 0.20 (Table 17)."*

### 5. The k=1 half of P2 is supported mainly by MATH-500, is rescued on the k-pool by post hoc relabeling, and "Holds" overstates it
**Where:** Table 1 P2 row ("Reference helps on MATH-500 ... and lowers inflation at k=1"; Verdict "Holds"); §5 Verdict ("with one correct answer the reference helps once answers written in prose are counted as correct"); Figure 2.

**What is wrong.**
- **On the preregistered k-pool under registered labels,** the reference *hurt* Qwen2.5-7B at k=1: -21.4 [-43, +0]. Inflation at k=1 is not lowered for three of four judges:
  - Qwen2.5-7B: +0.05 [-0.30, +0.42]
  - Qwen2.5-14B: -0.30 [-0.73, +0.13]
  - gemma-2-9b: -0.05 [-0.14, +0.04]

  (`r9_inflation_relabeled_kpool.json`, `p17_coverage_results.json`; also Figure 2's hollow points.)
- **After the post hoc relabeling,** the k-pool k=1 accuracy change is exactly zero for all four judges. That is "does not hurt", not "helps".
- **The registered "k=1 benefit on a Llama-generated grid" was falsified.**
- **The MATH-500 benefit is confounded.** It uses a different generator (Qwen2.5-7B), domain, and pass-rate band, and in one arm shows a full worked solution.
- **The MACE k=1 benefit (+32.4, +26.5; Table 44) is the clean natural-data k=1 evidence**, yet the main text never cites it for P2.
- **The post hoc relabeling is used here in the hypothesis's favor.** That is the asymmetric use a reviewer will flag, even though elsewhere it cuts against the authors.

**Fix.**
- Table 1 P2 Result: *"Reference helps with one correct answer on MATH-500 (+29 to +31 accuracy points) and on MACE single-answer questions (+26 to +32); on the k-pool it neither helps nor hurts once prose answers are counted (post hoc)."* Keep "Failed nearby: k=1 benefit on a Llama-generated grid; margins rising with k."
- Verdict: **"Holds for grading; the k=1 benefit is shown on MATH-500 and MACE."**
- §5 Verdict: *"P2 holds: with one correct answer the reference helps on MATH-500 and MACE and is neutral on the k-pool once prose answers are counted as correct;† with several it degrades grading of the other correct answers..."*

### 6. Figure 2 spends Section 5's lead float on a test the paper calls non-independent, in its hardest unit
**Where:** Figure 2 (p. 5) and §5: "this step is the selection-level signature of P1 rather than an independent test; the grading result below is the independent test."

**What is wrong.**
- The only figure opening the P2 section plots *inflation (SD)*. It is the most opaque measurement in the paper ("a second rubric, shown the same reference, scores the pick against other answers of the same correctness"), and §3 says it "measures a shared preference for agreement, not lost accuracy".
- The independent test (grading AUROC) is relegated to Figure 3a, which shares a float with a selection panel belonging to §7.
- The figure also wastes about 40% of its width on whitespace next to a narrow caption.

**Fix.**
- Move Figure 2 to Appendix D.
- Replace it with a **one-vs-several contrast on the independent test**, re-plotted from existing data:
  - left panel, one correct answer: MATH-500 and MACE k=1 best-of-64 accuracy, blind versus referenced (Tables 47, 44);
  - right panel, several: grading AUROC blind to referenced for the four screened judges plus Sonnet 5 on MACE (Tables 13, 25, 48).
- Split Figure 3: panel (a) stays in §5; panel (b) moves to §7 as its own float.

### 7. Table 1 cannot be verified as written and omits failed predictions that bear on its claims
**Where:** Table 1 (p. 3).

**What is wrong.**
- **(a) The Evidence column is not attributable.** "OSF, pre-spec., post hoc" for the whole P2, P3, and Costs rows cannot be mapped to the individual numbers in the Result cell. That defeats the column's purpose.
- **(b) The caption misdescribes the verdicts.** It says "Verdicts apply one rule", but the rule is per-prediction (CI excludes zero). "Holds / Partly holds / Mixed" are author aggregations the rule does not produce.
- **(c) Failed predictions that bear on the claims are missing from "Failed nearby".**
  - *Composition dose*: "Inflation rises with the number of matching valid answers ... (**falsified**: it falls, and is largest with none)." This directly contradicts the naive selection story of Eq. (1).
  - *MACE blind margin null*: falsified for Sonnet 5 (blind margin -1.37 [-2.05, -0.67]) and phi-4 (-0.80). This bears on the factual-question anchoring claims in P2 and P3, because a negative blind margin inflates the "added margin".
- **(d) The Costs row does not belong in a predictions table.** It is not a prediction, its verdict is "Mixed", and it calls inflation a cost although §3 says inflation is "not lost accuracy".
- **(e) "Sonnet 5 anchors at a bit over half the 7B judge's size"** reads as parameter count.

**Fix.**
- Put per-claim superscripts inside the Result cell (OSF, PRE, RE, †) and drop the Evidence column. That also frees width.
- Caption: *"Verdicts are our summary of the per-prediction outcomes in Appendix B, which apply one rule (adopted after most outcomes were known)."*
- Add the composition dose to the Costs "Failed nearby" and the MACE blind margin to P3's.
- Move Costs out of the table into one sentence below it, or give it a separate two-line table.
- Replace (e) with *"Sonnet 5's swap gain is about 60% of Qwen2.5-7B's (3.0 vs 5.3)."*

### 8. The "selection collapses" sentence drops the appendix's own label-artifact caveat
**Where:** §7 Selection (p. 7): "When no candidate matches the reference, selection collapses: ... 14% and 21% of the time against 72% and 79% blind (Appendix I; registered labels)."

**What is wrong.** Appendix I says of these same sub-pools: "These sub-pools use the registered labels, which count many correct answers written in prose as wrong ...; so the valid-pick rates here and the lure bonus below are partly label artifacts." The paper's most dramatic selection number appears in the main text with only "(registered labels)". The same experiment's registered headline prediction was falsified in reverse, and that is not mentioned there either.

**Fix.** Replace with: *"When no candidate matches the reference, the referenced judge picks a correct answer 14% and 21% of the time against 72% and 79% blind, but under registered labels that count prose answers as wrong, so these rates partly reflect labeling (Appendix I); the registered prediction that inflation grows with the number of matching answers was falsified (it is largest with none)."* If a relabeled version can be computed from existing labels (`r8_lenient_labels`), report it instead.

### 9. Main-text registration markers do not follow the stated convention
**Where:** §1 "Unmarked claims in the main text were preregistered on OSF or pre-specified in a timestamped commit; claims marked † are post hoc."

**Violations:**
- **§6:** "With thinking on, these judges score nearly every correct arithmetic answer 10 with or without the reference" is unmarked. App. C and N: "These diagnostics are post hoc."
- **§5:** "on MACE, Qwen2.5-7B's AUROC over all answers rises by 0.07, all of it on single-answer questions" is unmarked. The k-split comes from Table 49 (†).
- **§5:** "higher at k>1 than at k=1 in all 12 judge–pool pairs" and "excludes zero in 9 of the 12" are unmarked. Six of the 12 pairs rest on the post hoc paired grid re-analysis (Table 11, and Figure 2's own dagger).
- **Abstract, Figure 1c, §4:** the Qwen2.5-7B P1 numbers (+5.25 / -5.41, exact scorer) are a *re-analysis of an effect whose direction was known* (Table 3). The main text has no marker for re-analysis. The registered original-scorer values are +4.97 / -5.04 (Table 4).

**Fix.**
- Add the missing daggers.
- Introduce the re-analysis marker in the main text, or use the registered values (+5.0 / -5.0) in the abstract and Figure 1c with the exact-scorer values in parentheses.
- Move the convention sentence from the end of the related-work paragraph to §3, where readers look for methods conventions.

---

## Should-fix (ranked)

### 1. Figure 1 explains P1 only, not the idea or the method
**Where:** Figure 1 (p. 1).

**What is wrong.**
- Against the Schaeffer et al. standard, the figure shows one swap and a bar chart. It does not show the three readings, the one-vs-several contrast (the paper's title claim), or how P2 and P3 are tested. The key sentence ("With one correct answer, matching the reference is being correct, so the same habit helps") is buried in a text box.
- Panel (a) is a paragraph of text.
- Panel (c)'s title "Over 120 tasks" overstates the data: the bars use 120 / 93 / 113 tasks.
- The hatched "moved off" bars contradict the caption's own rule, "hollow markers mark the contrast condition (one correct answer, or thinking on)".

**Fix.**
- Shrink panel (a) to the question and the two answers, one line each.
- Keep (b).
- Add a narrow strip under (b) and (c): "one correct answer → reference = correctness → helps | several → reference = one of them → other correct answers penalized", with the MATH-500 +30 and Sonnet 0.94 → 0.78 numbers.
- Retitle (c) "Replication pool (93–120 tasks)".
- Make the grammar consistent: either state "hatched = reference moved off" in the caption, or use a lighter blue.

### 2. The declared color and marker grammar is not used in half the main figures
**Where:** Figure 1 caption, then Figures 3 and 4 and appendix Figure 8.

**What is wrong.**
- Figure 1 declares "Throughout the paper, orange marks scores without a reference and blue scores with one; hollow markers mark the contrast condition."
- Figures 3 and 4 are black and grey.
- Marker shape means labeling in Figure 3 (circle = any format, × = model-read, diamond = MACE/MATH) but judge identity in Figure 4a (circle = Qwen2.5-7B, square = phi-4, triangle = Sonnet 5).
- Figure 8 introduces teal for blind-then-reveal.

**Fix.**
- Referenced-minus-blind contrasts in dark blue.
- Blind reference lines in orange.
- Hollow markers for the contrast condition only.
- Encode judges by row label, never by shape. Encode labeling by a grey tick versus a filled dot, and say so once in the Figure 1 caption.
- Blind-then-reveal: a lighter blue, or blue with an orange outline.

### 3. Figure 4a groups are mislabeled, and Figures 3 and 4 mix incomparable designs on one axis
**Where:** Figure 4a (p. 7); Figure 3 (p. 6).

**What is wrong.**
- In Figure 4a the rows "Qwen2.5-7B, MT-Bench", "Qwen3-8B, thinking off/on", and "Qwen3-14B" sit under the "Sonnet 5, command line" group header with no header of their own, so they read as Sonnet CLI conditions.
- Figure 4a mixes the full pool, a 120-task subsample, and "60 tasks with one sample each" on one axis. The caption says "compare within a group", but the groups are not visually separated.
- In Figure 3, the vertical zero line cuts through the grey annotations "not shown (see caption)" and "not defined (one correct answer)" (7.2–7.5 pt, muted grey).
- Figure 3a places Sonnet 5 and GPT-4.1 16-candidate subsample AUROCs next to 64-candidate open-judge values, although Limitations says "its AUROCs are not directly comparable".

**Fix.**
- Figure 4a: add a fourth group header "120-task rotation subsample" and thin horizontal separators between groups.
- Figure 3: move the annotations off the zero line, or replace them with an em dash plus a footnote marker; use hollow markers or a separate group for the 16-candidate designs.

### 4. Too many named quantities for a 9-page paper
**Where:** §3 "Measurements" and throughout.

**What is wrong.**
- The main text asks the reader to hold: swap change, anchoring margin, added margin, grading AUROC, false-rejection rate, inflation (rubric a/b, SD units), registered checker / any format / model-read / boxed only, exact / original scorer, fine-grained judges, replication pool / k-pool / synthetic grid / pass-rate band, blind-then-reveal, and validity gate.
- The appendix renames the swap "rotation" (and adds gainers / losers / placebo).
- The proposed "one-sample" reading collides with "64 samples per task", "byte-identical samples", and "samples each judge scored 7 or above".

**Fix.**
- Rename the reading to **"one-instance"** or **"exemplar"** reading, or simply the **"agreement"** reading.
- In the main text use only: swap change, grading AUROC, false-rejection rate, best-of-64 accuracy.
- Move anchoring margin, added margin, and inflation to Section 7 or the appendix. Figure 4b can plot false rejections (Table 43 has the numbers) instead of added margin.
- Use "swap" in the appendix too, via a global replace of "rotation", with a one-line note that the ledger calls it rotation.

### 5. Section 7 breaks the prediction-then-verdict structure, and the abstract ends on a non-significant negative
**Where:** §7 (pp. 7–8); abstract final sentence.

**What is wrong.**
- §7 has no Prediction or Verdict paragraph.
- It mixes an endpoint the paper says is not about accuracy (inflation), label-sensitive accuracy losses, a composition result with artifacts, MACE, MBPP, and a mitigation.
- The abstract closes with "scoring blind before revealing the reference was slightly less accurate than showing the reference alone". Those intervals include zero (-3.0 [-8.3, +2.3], -1.5 [-4.5, +1.5]; Table 44), and on the k-pool blind-then-reveal beat the reference.

**Fix.**
- Open §7 with: *"Question. Does the grading harm become a selection harm?"*
- Close with: *"Verdict. Only when no candidate matching the reference is in the pool; on natural multi-answer questions it did not, and no protocol we tried was best on every pool (Table 37†)."*
- Move blind-then-reveal details to Appendix M, keeping one sentence.
- Abstract: replace the final clause with *"and scoring blind before revealing the reference was no more accurate than the reference alone."* Add a sentence on registration: *"We report all 156 registered predictions, including 25 that failed."*

### 6. Natural-data effect sizes for open judges are hidden by the abstract's pairing
**Where:** abstract sentence 4; §5.

**What is wrong.** The abstract gives the constructed-pool claim for the four open judges and the natural-data number (0.94 → 0.78) only for Sonnet 5. On MACE the open judges' grading AUROC falls by only 0.08 (Qwen2.5-7B) and 0.06 (phi-4) (Table 48), a third to a quarter of the constructed-pool drops (0.16–0.33).

**Fix.** In §5, add: *"On MACE the fall is smaller for the open judges (0.08 and 0.06)."* In the abstract, either add "(0.06 to 0.08 on factual questions)" or report Sonnet 5 alone as the natural-data result.

### 7. The motivation-to-evidence gap is not stated
**Where:** §1, paragraph 2 (p. 2).

**What is wrong.**
- The paper's own audit finds that curated math, where reference-guided judging is most common, is 0–2.5% multi-answer.
- The 18.5% NQ-open figure comes from the same LLM-labeled audit (one model family, no human check), but the §1 sentence does not say so.
- Most evidence comes from synthetic constraint tasks with one generator whose replies ignore the boxed format 38–43% of the time.

**Fix.** Rewrite as: *"...where our LLM-labeled audit (no human validation) of 200 questions per dataset found 0% to 2.5% with several. It matters wherever answers are not unique: 18.5% of NQ-open questions in the same audit..."* In Limitations, add: *"Most of our evidence is from constructed arithmetic tasks; our natural-data evidence is 133 MACE River and Language questions."*

### 8. The Sonnet 5 CLI versus API interface disagreement is unreported
**Where:** Limitations; App. H and N.

**What is wrong.** `registration_round8.md` records that on 939 shared calls "CLI and API scores agree exactly on 66.9% and within one point on 81.6% ...; API scores average 0.38 points higher", and that the partial CLI readout was "about twice the API estimate". The Sonnet 5 reasoning claims in §6 rest on the CLI; the grading claims rest on the API. I found this nowhere in the PDF.

**Fix.** Add one sentence to the Limitations "Judges and prompts" bullet and to App. H: *"On 939 calls run through both interfaces, CLI and API scores agree exactly on 67% (API 0.38 points higher on average), so CLI and API results for Sonnet 5 should not be compared directly."*

### 9. The conclusion's recommendation is nearly vacuous
**Where:** §10: "check them against the task's answer set where one exists".

**What is wrong.** If an answer set exists, an LLM judge is not needed. The paper already has zero-cost evidence for something more useful (Tables 36 and 37, post hoc).

**Fix.** Replace with: *"When correct answers can differ from the reference, do not trust a reference-guided low score on an answer that differs from the reference: re-score such answers without the reference, or with a judge that thinks before scoring on checkable tasks. In our pools, taking the higher of the blind and referenced scores lost nothing to blind judging on multi-answer tasks and kept most of the reference's benefit (Table 36†)."*

### 10. Appendix tables are unreadable at print size
**Where:**
- Tables shrunk with `adjustbox{max width=\linewidth}` print at roughly 5 pt, visibly in Tables 10, 24, 33, 36, 38, and 39.
- Table 3 (the ledger) runs 3.5 pages of dense prose cells.

**Fix.**
- Split the wide tables into two, or rotate them.
- Round CIs to one decimal where the unit is points.
- Put the ledger in a machine-readable CSV in the supplement, and keep in the appendix a one-page table of prediction ID, one-line claim, and verdict.

### 11. Abstract density
**Where:** abstract sentence 4, which is 62 words with nested clauses.

**Fix.** Split it into two sentences, one for k=1 and one for k>1. A suggested full abstract (about 190 words):

> LLM judges are routinely given a reference answer, on the premise that it acts as an answer key. We show that when a question has several correct answers, judges instead reward agreement with the one they are shown. On tasks whose correct answers are enumerated by a program or an audited list, swapping the reference between two correct answers moves the score of byte-identical text by 2.7 to 5.4 points out of 10 for Qwen2.5-7B, phi-4, and Claude Sonnet 5. The same habit helps when there is one correct answer (about 30 points of best-of-64 accuracy on MATH-500). With several, correct answers that differ from the reference become harder to separate from wrong ones: AUROC falls by 0.16 to 0.33 for four open judges on constructed tasks and from 0.94 to 0.78 for Sonnet 5 on factual questions. This is not only a failure to verify: Sonnet 5 anchors on factual answers it ranks correctly without a reference, though judges that think before scoring stop anchoring on arithmetic. The harm falls on grading more than on selection. We report all 156 registered predictions, including 25 that failed.

---

## Nits

1. **§3 vs Figure 1c.** "Each answers with an integer from 0 to 10 in at most four tokens" is contradicted by Qwen3 (up to 4,096 tokens) and MT-Bench; see Must-fix 2.
2. **§7 inflation CI.** "+1.19 SD [+1.03, +1.35]" matches Table 18, but Table 16's registered column (same estimator) gives [+1.02, +1.36] (`r9_inflation_relabeled.json`: [1.017, 1.358]). Use one.
3. **Two values for one AUROC.** §5 "grading AUROC falls from 0.87 to 0.60 under the registered checker" (Table 48, exact scorer, -0.27). Table 13 "Registered" gives -0.29 for the same cell (`r8_lenient_results.json`: 0.8706 → 0.5782). State the scorer in Table 13's caption, or use one source.
4. **Figure 1 example.** The intro leads with a 10.0 → 2.9 → 9.3 example whose swap is 6.4 points, chosen by a selection rule (App. A). Add "(a typical swap moves about 5 points)".
5. **Table 1 cell.** "(0.16–0.33 under three labelings; 0.07–0.14 boxed replies only)" should read "AUROC falls by 0.16–0.33".
6. **Figure 2 labels.** The caption says "Registered labels", while the §5 text beside it discusses relabeled k=1 values (-0.27, -0.15). Say that the figure's k-pool k=1 points differ from the text.
7. **§6 comparison.** "a swap gain of 3.0 against 5.3" compares Sonnet 5 integer scores with Qwen2.5-7B expected-value scores. Greedy integers give Qwen2.5-7B +5.65 (Table 45). Note the estimator, or compare integer to integer.
8. **Forward references.** The Table 4 caption points to Table 45, and Table 26 to Table 43, forcing long jumps. Inline the one number needed.
9. **Appendix H.** The "Frontier CLI judge" row being "Excluded from the counts" is good. But "which very likely included a git status listing recent commit messages that name the anchoring hypothesis" should be stated as confirmed or unconfirmed. Check the transcript if it is stored (`cli_transcript_audit.json` exists).
10. **Verdict-rule date.** "We adopted this rule on 13 September 2026" is the same day as the PDF CreationDate. Reviewers will read that as same-day rescoring. Say how many main-text verdict words changed as a result (answer this in the ledger paragraph).
11. **§8 Related work.** "our results predict that a self-generated reference anchors the same way on multi-answer tasks" is untested speculation. Write "suggest" instead of "predict", or cut it.
12. **Figure 3a labels.** The "Replication" group header is set tight against the first row label "Qwen2.5-7B". Add vertical padding.
13. **Figure 5a (appendix).** The legend overlaps the x-axis area, with five series at small size.
14. **§5 phrasing.** "an interval reaching zero, 14 tasks" should read "95% CI [−43, 0], 14 tasks".
15. **Appendix E.** "Both passes come from one model family, so agreement may overstate reliability" is honest. Put the same caveat next to the 18.5% in §1 (Should-fix 7).
16. **Consistent naming.** Use "Claude Sonnet 5" on first use and "Sonnet 5 (API)" / "Sonnet 5 (CLI)" consistently. Figure 4a uses "Sonnet 5, API" and "Sonnet 5, command line".

---

## Questions for authors

1. What does the verification-failure reading predict for P1 and P2? Which observed result, if any, would have falsified your agreement reading while leaving verification failure intact?
2. For the ≥7 blind-accepted filter: what share of *wrong* answers pass it for each judge? If a large share of wrong answers also score ≥7 blind, "accepted" is not "verified", and the filter tests nothing.
3. How is the MACE reference chosen (first listed answer, random member)? Sonnet 5's blind margin on MACE is -1.37 and phi-4's -0.80, so matching answers score lower blind. Is the reference systematically a less common or harder answer, and how much of the factual "added margin" (Figure 4b) is recovery from that negative baseline?
4. Table 49 reports a negative split-half Spearman ρ between blind AUROC and the reference's change in AUROC (for example, -0.54 for Qwen2.5-7B on MACE). Does this mean the harm is larger where the judge verifies better? If so, that is your best evidence against pure verification failure and belongs in §6. If it is instead a ceiling effect, say so.
5. Why is the MT-Bench explain-first template not a reasoning judge, while the Sonnet 5 CLI "reasoning" arm with thinking off is? What is the operational definition?
6. Sonnet 5's 16-candidate subsamples were redrawn until they held at least one matching-correct, one non-matching-correct, and one wrong answer. Does forcing all three kinds change the expected AUROC change relative to the 64-candidate open-judge design? Can this be checked by applying the same subsample rule to the open judges' existing scores?
7. Were the d=0 valid-pick rates (14% / 21% vs 72% / 79%) a registered readout of the composition experiment, or computed after P-E1 was falsified? `MANIFEST.md` lists `exploit_dose_diag.py` as "written after P-E1's falsification".
8. Under the uniform verdict rule adopted on 13 September 2026, did any main-text verdict word ("holds", "partly holds") change, or only ledger entries?
9. Can the any-format labels be applied to the composition sub-pools (Appendix I) to report the d=0 selection result without the label artifact?
