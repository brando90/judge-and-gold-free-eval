### (a) Three-sentence summary of what the paper claims
The paper claims that giving an LLM judge a “trusted reference answer” *reduces* selection-induced scoreboard inflation on unique-answer tasks (math), but *increases* inflation on tasks with multiple valid answers (RewardBench-2 Ties-derived generation tasks). It argues the mechanism is **reference anchoring**—judges effectively become “answer matchers”—and provides a causal demonstration by rotating the shown reference among equally valid answers, producing up to **+9.5/10** score swings for identical sample text. It further claims a boundary rule: references help only when the answer is effectively unique and the judge can verify; otherwise they create an attack surface, and common mitigations (instructions, multiple references) are capability-graded and non-robust.

---

## (b) Four-axis assessments (scores 1–10), with concrete quotes and table/figure pointers

### 1) **NOVELTY — 6/10**
**What’s genuinely new:**
- The *dynamic* result under **best-of-n selection pressure** is the paper’s main novel contribution relative to cited “static” reference bias work. You explicitly frame this: “*The open question was dynamic: static verdict accuracy and behavior under selection pressure can disagree*” (Intro), and you test it with the companion-A best-of-64 protocol.
- The **reference rotation** intervention is a clean causal test *of anchoring*, not merely correlation: “*nothing changed but the reference*” (Sec 3.2). Figure 1 / Table 3 is the standout.

**What is less novel / partially known:**
- The existence of reference-induced bias on multi-answer tasks is heavily foreshadowed by your own citations: “*solution fixation bias*” (Li et al. 2025 [8]), “*degrade on open-ended tasks*” (Lee et al. 2026 [7]), and your own “*7–8 points of verdict accuracy*” hit on Ties when showing any reference [3]. The conceptual claim “reference becomes arbitrary nuisance property” is basically [5].
- The “boundary rule” (unique + capability) is mostly a synthesis of your companion A plus your new multi-answer findings; the grid gives it additional evidence, but it reads more like careful empirical *characterization* than a new principle.

**Bottom line:** rotation-causal anchoring + selection-pressure inversion is publishable novelty; much else is consolidation.

---

### 2) **SOUNDNESS — 4/10**
The core phenomenon likely exists, but the *strength of the claims* is ahead of what the experiments can safely support.

#### Major soundness failures / confounds

1) **Primary dynamic claim relies on post-hoc population change and post-hoc estimator to reach “significance.”**  
You admit: “*the 51-item full-pool analysis … is a post-hoc deviation adopted for power*” and “*the pooled cluster-bootstrap estimator … was likewise adopted post hoc, after the per-scale results were seen*” (Sec 2; Table 1).  
And the only CI excluding 0 is exactly that post-hoc pooled row: Table 2 pooled ∆inflation **+0.41 [+0.07, +0.77]**; every per-scale ∆ crosses 0. This is classic “researcher degrees of freedom” with a significance rescue.

2) **Your “ground truth” checker is demonstrably broken in the direction that makes many derived quantities ill-defined.**  
You report that GPT-5.2 judged **90% of checker-invalid samples valid** (Section 2). That means your “true quality” signal is massively noisy and biased, which contaminates:
- the inflation estimator (“scoreboard-versus-truth divergence”), because the “truth” is wrong for a large share of samples,
- the permutation null built by “*shuffling judge scores among samples the checker grades identically*” (Setup), because “identically” is often wrong.

You argue this bias is conservative: “*false negatives fall exclusively on non-matching answers … understating blind judges’ measured true gains*.” That is **not proven**. It assumes (i) false negatives are exclusively non-matching and (ii) their distribution is independent of judge condition aside from selection frequency. But selection itself changes which answers appear in the selected set; your estimator’s behavior under asymmetric label noise is not analyzed.

3) **The causal rotation experiment is clean on “scores depend on reference,” but you oversell what it implies for “gaming” and “inflation.”**  
Rotation demonstrates anchoring in scoring. It does **not** directly demonstrate increased susceptibility to adversarial optimization except via your inflation estimator (which depends on the checker). So the paper’s rhetorical line “*manufactures the very gaming it was installed to prevent*” (Abstract/Conclusion) is stronger than warranted.

4) **Selection pressure experiment uses one generator, one task source, and correlated judge ladder—non-replication risk is high.**  
For the headline Ties dynamic inversion: generator is only Qwen2.5-7B-Instruct; judges are Qwen2.5 family at multiple sizes. You acknowledge dependence: “*the four judge scales share items and a generator, so they are not independent replications*” (Sec 3.1). Yet the abstract claims “*at every judge scale tested*” as if this were robust replication; it’s four correlated readouts.

5) **“Pre-registered” framing is undermined by: (i) tiny registered subset (n=7), (ii) post-hoc main analysis, (iii) rotation addendum after seeing original margins.**  
Table 1 is admirably honest, but the net inferential weight of registration is limited. In hostile Q&A, “pre-registered” will be attacked as branding rather than design constraint.

#### What *is* solid
- The **rotation within-sample paired delta** is hard to dismiss as artifact: Table 3 “Gainers: same-sample ∆” **+8.7 to +9.6** at small judges and **+3.1 to +3.5** at 14B. Even if the scale saturates, the direction and the loser symmetry are compelling.
- You include some controls (placebo, losers, blind margins) and fix earlier statistical errors (McNemar vs Fisher), which helps.

**Bottom line:** mechanism (anchoring) is sound; the dynamic “inflation” claims are shaky because the “truth” substrate is incomplete and the statistical significance is post-hoc.

---

### 3) **COMPLETENESS — 5/10**
A skeptical reader will still demand:

1) **Human adjudication** (or at least high-quality multi-LLM adjudication) of validity on a meaningful sample, because your checker is explicitly incomplete and GPT-5.2 is not ground truth. Right now you have: “*the adjudicator is an LLM, not a human*” (Sec 2), and that’s inadequate given the estimator depends on correctness labels.

2) **A version of the dynamic analysis that does not rely on enumerated valid sets** (since those are incomplete by construction in many real tasks). E.g., tasks with programmatic verification, or tasks where correctness is checkable by external tools, or controlled domains beyond primes/divisors.

3) **A principled treatment of label noise** in the inflation estimator. Your argument that incompleteness makes the result conservative is a plausibility story, not an analysis.

4) **Cross-generator and cross-task replication for the headline “Ties inversion”**, not just the synthetic arithmetic grid. The grid is narrow and adversaries will say it’s “toy arithmetic.”

5) **Mitigations that actually operationalize “verification without matching.”** Your two mitigations are extremely weak interventions: a one-sentence instruction and showing a few references. No structured rubric, no decomposition, no self-consistency, no tool use, no “judge solves then compares,” no constrained outputs.

---

### 4) **IMPACT — 7/10**
If the phenomenon holds up, it matters immediately because reference answers are widely used in LLM-as-judge evaluation pipelines and RLHF/RLAIF-style optimization loops.

- The practical message “*Before installing a reference, ask whether a correct answer different from the reference exists*” (Sec 3.3) is actionable.
- The rotation result is memorable and changes how people reason about “references as safeguards.”
- However, impact is limited by current evidential fragility: practitioners will ask “does this happen on my tasks with my validators?” and your main real-world-ish dataset has a broken validator.

**Net:** high potential impact, but the paper needs more robust grounding to become a community norm rather than an interesting warning.

---

## (c) Readability verdict (for a first-year PhD)
**6/10.** The abstract is clear and the main result is findable quickly (Figure 2 inversion; Figure 1 rotation). But the paper is overloaded with meta-science bookkeeping (ledger, deviations, companion references) and nonstandard metrics (“excess hack gap”) that require effort to trust; tables mix point estimates and inferential targets in a way that’s easy to misread (e.g., Table 4 vs Table 5). A first-year PhD can follow the story, but will struggle to assess what is truly “registered vs post-hoc” and what is actually statistically supported without careful rereading.

---

## (d) Five highest-leverage concrete improvements (ranked)

1) **Replace or validate the “truth” signal with something defensible.**  
Do human adjudication on a stratified sample (matching/non-matching; checker-valid/invalid; selected/not selected). At minimum, use 3 diverse frontier LLMs + disagreement resolution; quantify false positive/negative rates and propagate into uncertainty on inflation.

2) **Pre-register (for real) a new Ties-style experiment with sufficient power and no post-hoc pooling hacks.**  
Decide population, estimator, and pooling strategy *before* generating any samples. Use multiple generators and at least one non-Qwen judge family to break correlated-family critiques.

3) **Stress-test the inflation estimator under label noise and incomplete valid sets.**  
Simulate incomplete enumerations where the missingness correlates with “distance from reference,” and show whether your “conservative” claim holds. Right now that claim is hand-wavy and likely false in some regimes.

4) **Demonstrate the effect on a realistic open-ended domain with tool-verified correctness or structured constraints.**  
E.g., code tasks with multiple correct implementations but unit-test verification; or retrieval/citation tasks with an automated verifier; or structured database queries with multiple equivalent SQL forms.

5) **Upgrade mitigation experiments beyond “one sentence instruction” and “show 3 refs.”**  
Try structured judging: judge must (i) enumerate multiple valid answers, (ii) verify candidate independently, (iii) explicitly state whether candidate is correct even if different from reference, with constrained JSON fields. Measure whether anchoring margin drops without requiring a frontier model.

---

## (e) Overall score and accept/reject lean
**Overall: 5/10 — Weak Reject (borderline).**

**Why:** The causal anchoring result (rotation) is strong and novel enough for a top venue *if* the paper’s main dynamic “inflation under selection pressure” story were on equally solid footing. But the current headline dynamic claim leans on (i) a validator you show is massively incomplete, (ii) a post-hoc population deviation, and (iii) a post-hoc pooled estimator that is the only statistically “significant” result. I’d be open to a **strong accept** after a revision that fixes the correctness signal and re-runs a properly pre-registered, multi-generator replication demonstrating the inversion without fragile estimator assumptions.