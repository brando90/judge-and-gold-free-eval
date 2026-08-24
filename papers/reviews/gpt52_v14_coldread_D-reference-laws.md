## (a) Three-sentence summary of what the paper claims
The paper claims that *showing a single reference answer* to an LLM judge—often used as an anti-gaming safeguard—*increases* selection-induced score inflation on tasks with multiple valid answers, effectively turning the judge into an “answer matcher” rather than a validity checker. It claims this inversion is confirmed by an externally preregistered replication (Table 1), is *caused* by anchoring (proved via reference rotation; Figure 1 / Table 2), and that the harm switches on when moving from unique-answer tasks (k=1) to multi-valid tasks (k>1) (Table 4 / Table 6). It further claims a preregistered structural mitigation—**score blind first, then reveal the reference**—removes the *measured* inflation at k>1 for two judges (Table 6), while instruction-based mitigations mostly fail below high capability (Table 5).

---

## (b) Scores (1–10), each with justification

### NOVELTY: **7/10**
The static observation that reference answers bias judges on open-ended / multi-valid tasks is not new and the paper explicitly concedes it (“We claim none of that as new.” in Related Work; cites [7,8] and companion [3]). The novel parts, as written, are: (i) the *dynamic* selection-pressure result (“Reference-guided judging … widely treated as a safeguard… On tasks with several valid answers it does the opposite.” Abstract; and “dynamic: … under best-of-64 selection pressure” in Intro), (ii) the causal demonstration by **rotating** which valid answer is shown (“rotating the shown reference… raises the score of the identical sample text by up to +9.5” Abstract; Figure 1/Table 2), and (iii) a preregistered protocol-level mitigation (M1) rather than prompt tweaks (Section 3.4/Table 6). These are genuinely incremental beyond [7,8] if you buy the “dynamic under selection” framing as distinct, and rotation-as-intervention is a clean mechanism test.

Novelty is capped because the “anchoring” mechanism is basically the obvious hypothesis from the static bias literature, and much of the framing relies on companion-paper results for the “unique-answer helps” side (math/code) rather than being established here. Also, “one fix works” is overstated: M1 reduces measured inflation but “leaves roughly half the anchoring premium in place” (Abstract; Table 6 margins), so it’s not actually solving anchoring, just changing how it expresses in the registered inflation metric.

### SOUNDNESS: **6/10**
Strengths: the paper makes a serious effort at preregistration discipline and sharply separates confirmatory vs exploratory *in structure* (“Sections 3.1 through 3.4 are confirmatory… Sections 3.5 and 3.6 are exploratory” at start of Results). The replication is plausibly well-controlled: “externally preregistered … with population, estimators, and endpoints frozen before any pool generation” (Abstract), uses a “non-Qwen generator” and “two cross-family judges” (Abstract; Table 1 notes: generator Llama-3.1-8B, judges Qwen2.5-7B and phi-4), and uses “exact programmatic check” (Table 1 notes). The causal mechanism test is strong because it uses *paired same-sample deltas* with only reference changed (“nothing changed but the reference” Section 3.2; Table 2 “Gainers: same-sample ∆”), which largely immunizes it from a lot of confounds.

Major weaknesses / hostile Q&A issues:
1. **The main dynamic claim is only cleanly supported for a fairly specific task type** (short constraint problems with exact oracles) and not for the open-ended settings that motivate “LLM judges” in practice. The replication pool is explicitly “constraint-style short-answer problems, not free-form generation” (Limitations). That doesn’t invalidate the claim, but it narrows it; the paper’s rhetoric (“widely treated as a safeguard” / “folklore”) invites overgeneralization.
2. **Estimator dependence and “inflation” construct validity**: “Inflation… excess hack gap… against a null built by shuffling judge scores among samples the checker grades identically” (Setup). This is nonstandard enough that you should expect questions like: does this metric behave sensibly when pass rates are high/low, when scores are saturated, when extraction fails? The paper partly addresses extraction and pass-rate bands (Table 1 notes; Section 3.1 boxed-compliance split), but it is still hard to assess whether “+1.19 baseline SD” is a stable object across task families and scoring scales.
3. **Pilot calibration / killed run**: Section 3.1 admits “two-pass pilot calibration… [and] an uncalibrated main-pool generation launched between the passes was killed before any scoring or analysis.” That is defensible, but it will trigger suspicion: did calibration choices indirectly optimize for the effect? You say no because analysis code and endpoints were frozen, but the tasks themselves and prompt constraints were tuned to hit pass-rate bands, which can change the optimization landscape.
4. **Rotation experiment preregistration is weak**: you admit the addendum “was pool-aware” and “adds little inferential weight beyond its git timestamp” (Section 3.2). That’s honest, but it means the “registered mechanism predictions” shouldn’t be sold as a major preregistered confirmation; the evidence is still good, but not preregistered in the way a skeptical reader expects.
5. **Mitigation M2 deviates from registration**: “M2 was registered as a hard gate … implemented as the soft multiplier” (Table 6 notes; Section 3.4). Even with an OSF amendment, this is still a significant deviation in an experiment whose point is to recommend fixes. It weakens confidence in the mitigation section’s preregistration discipline.
6. **Small n per cell in the k-grid**: Table 4 admits that after filtering, “the analysis runs on n=6 items at k=1 and n=20 item-strata pooled over k>1.” Many claims in Section 3.3 are built on patterns in these tiny strata, and then “post-hoc paired re-analysis” (Table 4) becomes the backbone for the “universal step” claim. That’s shaky: it’s not wrong to analyze, but it is not the same as a preregistered primary endpoint.

Net: the replication and rotation pieces are reasonably sound for *what they actually measure*, but the paper still overreaches in narrative generality and leans on complex bespoke estimands that are hard to sanity-check on a cold read.

### COMPLETENESS: **6/10**
A skeptical reader will still demand:
- **Human-grounded validation** (even a small one) that the “validity” notion matches human correctness, especially because much of the narrative is about “several valid answers” in natural tasks. Right now, confirmatory work is mostly arithmetic/constraint or exact-oracle domains; the exploratory Ties pool uses an LLM adjudicator (GPT-5.2) and you admit “not a human” (Section 3.5).
- **A clearer mapping from “anchoring margin” to “inflation under selection”**. You assert “This is also why the inversion happens” (Section 3.2), but the paper doesn’t provide a quantitative decomposition showing that the observed inflation deltas are predictable from margins + answer frequency distributions. Without that, a reviewer can argue you have mechanism evidence and outcome evidence, but not a tight link.
- **Stress tests for stronger optimization than best-of-64** given you concede M1 leaves “roughly half the anchoring premium in place” and “whether that residual premium re-emerges as inflation under stronger optimization … is untested” (Section 3.4). This is a big hole because your framing is about adversarial selection/pressure.
- **Generalization across judge prompting formats and scoring ranges**: you use 0–10 scales and two rubric paraphrases; but real deployments may do pairwise comparisons, rubric grading with rationales, or tool-verified judging. The paper doesn’t test those.
- **Cleaner confirmatory evidence for the k=1 benefit** within *this* paper. You keep leaning on companion A (“collapses inflation 4–13× on math”), and in your own cross-generator grid the k=1 help fails for Qwen-7B (Section 3.3). The boundary claim is therefore asymmetric and should be presented more cautiously than it currently is in the abstract/conclusion.

### IMPACT: **7/10**
If true, this matters immediately to anyone using reference-based LLM judging in tuning loops (best-of-n, rejection sampling, RLHF/RLAIF-ish selection with judge scores) on tasks with non-unique solutions. The replication effect sizes are large (Table 1: pooled +1.19 baseline SD; Table 6 single reference at k>1: +1.50 and +1.07 vs blind), and the rotation result is a visceral demonstration (Figure 1/Table 2: same text can jump ~+9 points). The mitigation M1 is a practical procedural change (“two judge calls per candidate” Table 10) that some practitioners could adopt.

Impact is limited by domain: your cleanest confirmatory results are for short constrained tasks with exact oracles; many real “open-ended” tasks don’t have such crisp validity, and the fix “blind then reveal” may not behave similarly when the reference is long, ambiguous, or itself uncertain (Limitations). Still, even as a cautionary tale, it likely changes evaluation hygiene.

### READABILITY: **5/10**
This draft is more explicit than the earlier version you describe, but it is still **ledger-forward** and cognitively heavy on a first pass. There are too many named estimands (“inflation,” “lost accuracy,” “excess hack gap,” “baseline SD,” “oracle regret,” “anchoring margin,” “step,” “trend,” “level”), too many pools (exploratory Ties pool, replication pool, synthetic grid, cross-generator pool, mitigation pool), and too much bookkeeping in the main narrative.

Concrete examples:
- Table 1 is dense and its “Population disclosure” note is the kind of footnote that makes readers distrustful (“secondary endpoints … slightly larger population than the primary one… discipline is uniform within each endpoint rather than across all three.”). That may be correct, but it’s not readable.
- The paper repeatedly forces the reader to reconcile effect sizes on incomparable selection/population rules (“Because the two experiments select their populations by different rules, the +1.50 and +1.07 here and the +1.19 of Table 1 are not measured on comparably selected item sets and should not be differenced.” Table 6 notes). This is honest, but it makes the tables hard to use.
- You do add signposting (“How to read this section… confirmatory vs exploratory” at Results start; and Section 3.6 clearly labeled “not claims”), which helps.

A first-year PhD student can probably follow it, but not “on one pass” without rereading definitions and checking notes.

---

## (c) Revision assessment (must-answer items)

### (i) Is the “over-engineered / ledger-heavy / obscures the main result” concern resolved?
**Partially resolved.**

What improved: You now explicitly segment confirmatory vs exploratory in the main narrative, in bold, repeated, and structurally enforced:
- “Sections 3.1 through 3.4 are confirmatory… Sections 3.5 and 3.6 are exploratory… not evidence for the claims.” (start of Section 3).
- “This section reports the exploratory study… It comes after the confirmatory evidence because two of its analysis choices were post hoc.” (start of Section 3.5).
- Section 3.6 is explicitly titled “Exploratory analyses (not registered, not claims)” and includes an explicit non-claims disclaimer: “None of it is offered as evidence for the paper’s claims.”

What remains not fixed: the paper is still **ledger-heavy** in the sense that Table 8 (“Prediction ledger”) is huge, central, and the prose constantly routes through it (“registration history lives in one ledger (Table 8)”; “Every prediction… appears in one place, Table 8.”). You also kept lots of “provenance bookkeeping” and artifact naming in the main body (“canonical artifact repl results.json”; “repl analysis.py”; “round6 disclosures.py”), which reads like internal lab ops rather than scientific communication on a cold read. The main result is there, but the writing still “obscures” it by overloading the reader with procedural detail immediately after stating the headline (e.g., Section 3.1’s long discussion of calibration, killed run, overlap collisions, boxing compliance splits).

### (ii) Does the paper now read clearly on a first pass for a reader with no prior context?
**Only partially.** A reader *can* state the main result after two pages (Abstract + Intro + Figure 1 + the bullet list do communicate: “reference helps on unique-answer but harms on multi-valid via anchoring; replicated; rotation proves causal; blind-then-reveal mitigates”). However, that same reader will **not** be able to “parse the tables without hunting through notes,” because key interpretive constraints are buried in notes (Table 1 endpoint populations differ; Table 6 population selection not comparable to Table 1; Table 3 dashes mean “not quoted” rather than missing data; Table 4 is post-hoc reanalysis; Table 5 n=5 items per cell; etc.).

In particular, on a cold read, Table 1’s three endpoints with different populations and Table 6’s warning not to difference across experiments make it hard to know what comparisons are legitimate without careful note-reading. So: narrative clarity improved; *table usability* on first pass is still weak.

---

## (d) OVERALL SCORE: **6/10 — REJECT (borderline)**  
**Confidence: 0.62**

This is still roughly “weak accept / weak reject” territory in substance, but for a top-tier venue I lean **reject** because (1) the paper’s core confirmatory evidence is narrow-domain (constraint/oracle tasks) relative to its sweeping practitioner framing, (2) too much of the boundary claim relies on companions and exploratory contrasts, and (3) the presentation is still more complicated than it needs to be, especially in the tables and population/estimator caveats. The replication + rotation are strong enough that with sharper scoping and simplification, it could be an accept.

---

## (e) Top 5 concrete asks (ranked)

1. **Narrow and harden the main claim to what your confirmatory evidence actually supports; rewrite Abstract/Conclusion accordingly.**  
   *What to do:* Explicitly state (in Abstract first sentence and again in Conclusion) that the confirmatory inversion is shown on *short-answer constraint tasks with exact validity oracles* and on a *k-stratified oracle pool*, and that open-ended free-form tasks remain unconfirmed.  
   *Why it matters:* Right now the framing (“widely treated as a safeguard”; “many real evaluation targets… propose a design”) invites overclaiming, which is exactly what gets attacked in Q&A.

2. **Make Table 1 and Table 6 comparable or stop putting their effect sizes side-by-side.**  
   *What to do:* Either (a) rerun the replication endpoint with the same pass-rate band as the mitigation experiment (or vice versa), *as a registered sensitivity*, or (b) add an additional row in Table 6 computed under the replication’s [0.2,0.8] band, so readers can compare +1.19 to +1.50/+1.07 without the current “don’t difference these” footnote.  
   *Why it matters:* The current situation reads like statistical escaping: the headline numbers can’t be compared because of selection-rule differences you chose.

3. **Provide a quantitative link from anchoring margin to inflation under selection (even if approximate).**  
   *What to do:* Add a short model/derivation or simulation showing how a per-item margin (Table 2 / Table 6) plus answer-frequency distribution predicts expected inflation deltas under best-of-n. Include at least one plot validating predicted vs observed inflation across items in the replication pool.  
   *Why it matters:* Without this, “anchoring causes inversion” is mechanistically plausible but not quantitatively grounded; skeptics can argue other pathways could produce the same inflation metric.

4. **Promote one simple, reader-first “main result table” and demote the ledger/artifact plumbing.**  
   *What to do:* Add a 1-page “Main Results” panel early (end of Intro) with: replication inflation delta (Table 1 E1), causal rotation delta (Table 2 gainers), and mitigation delta (Table 6 M1 k>1). Move most artifact/provenance filenames (json, py) to an appendix or footnote.  
   *Why it matters:* This directly addresses the lingering “over-engineered / obscures main result” problem and would materially improve readability scores.

5. **Strengthen (or explicitly weaken) the “k=1 helps” half within this paper, without relying on companions.**  
   *What to do:* Either add a confirmatory k=1-only experiment (even small) on cross-generator text to show benefit can replicate, or reframe the boundary to: “k=1 is not harmed; benefit is capability- and domain-dependent” and remove “helps” phrasing from Abstract (“A raw reference is safe only when…” currently implies benefit).  
   *Why it matters:* Your own evidence is mixed (P-S5 fails; Table 6 shows Qwen-7B k=1 is null). The current boundary statement is too confident relative to in-paper data, which is a common reason borderline papers get rejected.

