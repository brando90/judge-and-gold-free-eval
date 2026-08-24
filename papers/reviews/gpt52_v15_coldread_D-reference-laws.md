## PART 1: CORE REVIEW (cold read, strict)

### 1) NOVELTY — **6/10**
There are two distinct “novelty” claims here: (i) *dynamic* harm under selection pressure, and (ii) a *causal* mechanism via rotation.

**What is genuinely new vs cited prior work**
- The paper correctly concedes the **static** failure is not novel: *“The static direction of the failure is established, and not only by us.”* (Intro) and again *“We claim none of that as new.”* (Related work).
- The **dynamic inversion under best-of-n selection** is positioned as the main novelty: *“The open question was dynamic…”* (Intro) and *“This paper adds five things. The dynamic result…”* (Related work). That does appear meaningfully beyond the cited static-bias papers [7,8] and the RewardBench-2 “Ties” design [9].
- The **reference rotation** is a clean causal intervention (good): *“rotating the shown reference proves it causal”* (Abstract) and *“Nothing about the answer changed, so the premium is caused by the reference, full stop.”* (Sec. 3.2). This is a real conceptual step beyond “judges prefer reference-like answers” correlational claims.

**But the paper overstates novelty in places**
- You repeatedly frame “anchoring” as *the* mechanism, but the per-item linkage test fails to support it tightly (Sec. 3.2). So the novelty is “rotation changes scores a lot” more than “we have the quantitative mechanism for selection inflation.”
- The “k boundary at k=2” is not deeply surprising; it’s almost definitional once you accept anchoring and multi-validity. The grid is valuable, but the boundary reads more like careful auditing than a conceptual breakthrough.

### 2) SOUNDNESS — **7/10**
The strongest part is the externally preregistered replication with exact oracles. The weakest parts are (a) comparability of effect sizes across experiments/populations, (b) underspecified multiplicity/selection of items, and (c) some “registered” claims leaning on post-hoc re-analyses.

**Strong points**
- You do the right thing by restricting the main claim: *“short-answer tasks with exact programmatic validity oracles… free-form generation is outside what we test.”* (Abstract).
- Replication has real teeth: *“externally preregistered replication… population, estimators, and endpoints frozen before any pool generation”* (Abstract) and Table 2 gives large deltas: **+1.19 [+1.02, +1.36] baseline SD** with **n=105** in-band items, plus exact McNemar collapse tests (**56/2**, **76/0**, *p* < 1e-5).
- You actively disclose deviations and weaknesses instead of hiding them (good reviewer hygiene): e.g., in Table 2 notes about endpoint populations differing; Sec. 3.4 about M2 deviating from registered hard gate; Sec. 3.2 about rotation being pool-aware.

**Serious soundness issues / confounds you don’t fully neutralize**
1) **Population mismatch across endpoints inside the “confirmatory” replication table.**  
   Table 2: primary endpoint E1 is on **105** items in [0.2,0.8], but P-R2/P-R3 are on **93 eligible items** (and “83 also inside the band”). You defend this as “frozen in code,” but scientifically it still weakens interpretability: readers cannot compare E1 vs anchoring margin vs selection collapse on the same population. The note admits: *“The two secondary endpoints therefore sit on a slightly larger population than the primary one…”* (Table 2 Notes). This is not fatal, but it’s messy and avoidable.

2) **“Anchoring mechanism” is causally shown, but not quantitatively linked to inflation.**  
   You do the right test and it mostly doesn’t support your story per-item: *“the per-item correlation between anchoring margin and inflation is r=+0.29… for phi-4 and r=+0.06… for Qwen-7B”* with non-monotone terciles (Sec. 3.2). This is a direct hit to mechanistic completeness and to any strong causal language about the pathway “margin → inflation under selection.”

3) **Grid inference leans on post-hoc re-analysis to make the “universal step” claim.**  
   Sec. 3.3: *“The paired step… estimates quoted in this section are a post-hoc re-analysis (Table 5), kept distinct from the frozen registered analysis.”* Yet the narrative then elevates the step to the main universal statement: *“The step is the universal claim (P-S1).”* This is rhetorically inconsistent: either the registered analysis supports the universal step directly, or your universal claim is built from post-hoc inference.

4) **Small effective n in key grid cells.**  
   Figure 2 / Table 4 admit *“4 to 6 items enter each plotted cell”* after the pass-rate filter. That’s extremely low for per-k conclusions, and helps explain why you later need post-hoc pooling and “step” contrasts. The paper is honest about this but still extracts a lot of structure from it.

5) **Mitigation M2 deviates from registration.**  
   You disclose: *“M2 is a soft gate, not the hard gate registered.”* (Sec. 3.4) and Table 7 repeats it. This is a big deal: it means one of the central mitigation conclusions is not actually preregistered as implemented. The OSF amendment helps provenance, but it’s still a deviation.

### 3) COMPLETENESS — **6/10**
A skeptical reader will still demand:

- **Broader task realism.** Everything is “short-answer constraint tasks” with exact oracles. You explicitly exclude free-form, but the title and framing (“LLM judges”) will make readers expect broader evaluation settings.
- **More judge diversity for mitigations.** The “one fix works” claim is based on **two judges** (Qwen-7B, phi-4). Table 11 even flags judge-dependence for M2. This is thin for a prescriptive protocol recommendation.
- **Stronger analysis of residual anchoring after M1.** You admit: *“it leaves a third to three fifths of the anchoring premium in place”* (Abstract; Table 7; Sec. 3.4). But then you still recommend it as “removes the measured inflation.” A reader will ask: under stronger optimization (n>64, RL), does that residual premium reappear as inflation?
- **Clarify multiple comparisons / researcher degrees** in the large grid of conditions (blind / 1 ref / instruction / multi-ref, 2 rubrics, multiple models, multiple k). You partially address this in Limitations: *“roughly 50 descriptive grid cells quoted here are uncorrected for multiple comparisons”* (Limitations). That should be earlier and stricter.

### 4) IMPACT — **7/10**
This can change actual evaluation practice *in the narrow regime tested*:
- Many practitioners blindly add a reference answer thinking it prevents “gaming.” Your main claim is sharply operational: *“A trusted reference answer… is widely treated as a safeguard against gaming. On tasks with several valid answers it does the opposite.”* (Abstract).
- The mitigation “score blind first, then reveal” is implementable and not just a prompt tweak. Table 7 shows near-zero inflation deltas vs blind at k>1: **−0.05** and **+0.16** compared to **+1.50** and **+1.07** under a single reference.

But impact is capped by your own scope:
- You repeatedly say this does not cover free-form generation. Many LLM-as-a-judge deployments are exactly free-form.
- The paper risks being “folk knowledge dressed up” for some communities: that a single reference biases toward surface matching is not shocking. What saves you is (i) the preregistered dynamic selection result and (ii) the magnitude (+9.5/10) in rotation.

### 5) READABILITY — **8/10**
This is unusually readable for a dense empirical audit.
- Table 1 is genuinely “the whole paper in four numbers.”
- You are explicit about what is confirmatory vs exploratory: *“Sections 3.1 through 3.4… primary results… preregistered… Sections 3.5 and 3.6 are wholly exploratory.”* (Sec. 3).
- Definitions are mostly present (inflation, lost accuracy, anchoring margin) in Setup.

Main readability flaw: you still occasionally force the reader to reconcile “registered vs post-hoc” logic across sections (e.g., “step is universal” derived from Table 5 post-hoc re-analysis while claiming P-S1).

---

## OVERALL SCORE: **7/10**
**Verdict: WEAK ACCEPT**  
**Confidence: 3/5**

Reason: The preregistered exact-oracle replication (Table 2) plus the causal rotation (Figure 1 / Table 3) are strong enough for a top-tier venue *as an evaluation-methods audit*, despite limitations in mechanistic linkage and generality. Without those two pillars, this would be a reject; with them, it clears the bar.

---

## TOP 5 CONCRETE ASKS (ranked by leverage)

1) **Stop calling anchoring “the mechanism” without qualifying the missing per-item link.**  
   Rewrite Abstract/Conclusion mechanism language to match Sec. 3.2: rotation shows *causal anchoring of scores*, but per-item margins do not predict per-item inflation reliably. Concretely: change *“The mechanism is anchoring”* (Abstract) to “a mechanism is anchoring…” and add the negative-result sentence in Abstract or Conclusion.

2) **Make Table 2 populations consistent across endpoints or provide a matched-population version.**  
   Add an additional row/column where E1, P-R2, P-R3 are computed on the same item set (e.g., the intersection) so readers can compare magnitudes without footnotes. Your current note reads like a technicality: *“discipline is uniform within each endpoint rather than across all three.”* (Table 2 Notes).

3) **Strengthen the mitigation claim by testing M1 under higher selection pressure or adaptive optimization.**  
   Since you admit residual anchoring remains (Table 7), run best-of-n for n ∈ {2,4,…,256} or a lightweight hillclimb/RL-style optimizer using the judge, and report whether M1 remains stable. Right now, “removes measured inflation at best-of-64” may not survive stronger optimization.

4) **For the synthetic grid, replace or supplement post-hoc “step” inference with a registered model-based analysis.**  
   The “universal step” is central, but the key inferential table (Table 5) is explicitly post hoc. Either preregister a hierarchical model / paired contrast analysis and rerun, or downgrade the universality language.

5) **Broaden judge coverage for mitigations beyond two models.**  
   Add at least one additional judge family/size for M1/M2 (e.g., a smaller phi, a larger Qwen, or Llama judge) to support the prescriptive Table 11 recommendation. Right now “one fix works” is overstated given N=2 judges.

---

# PART 2: REVISION AUDIT (five prior asks)

### Ask 1. Narrow and harden the main claim to what confirmatory evidence supports.
**RESOLVED.**  
Evidence:
- Abstract explicitly narrows scope: *“short-answer tasks with exact programmatic validity oracles… free-form generation is outside what we test.”*
- Claims are tied to the preregistered replication: *“Within that scope the result is an externally preregistered replication…”* and the main number is Table 2.
- Sec. 3 explicitly separates confirmatory vs exploratory: *“Sections 3.1 through 3.4… preregistered… Sections 3.5 and 3.6… not evidence for the claims.”*

### Ask 2. Make replication and mitigation tables comparable, or stop side-by-side effect sizes.
**PARTIALLY RESOLVED.**  
They improved it, but comparability is still not clean.
- They now explicitly warn about different bands and **provide a band-matched recomputation**: Table 7 Notes: *“The two experiments select their populations by different pass-rate bands… recomputed under the replication’s registered [0.2, 0.8] band…”*
- However, the paper still puts headline replication (+1.19 Table 2) and mitigation deltas (Table 7) in the Abstract side-by-side as if directly comparable, and only later adds caveats. Also, Table 2 endpoints still mix populations internally.

### Ask 3. Provide a quantitative link from anchoring margin to inflation under selection.
**RESOLVED (as attempted analysis), but NEGATIVE.**  
Evidence: Sec. 3.2 explicitly runs it and reports weak/absent correlations:
- *“phi-4 r=+0.29 [+0.03, +0.54] … Qwen-7B r=+0.06 [−0.31, +0.38] … tercile means are not monotone”*
They also label it *“post hoc.”* This satisfies the ask, even though it weakens the mechanistic narrative.

### Ask 4. Promote one simple main result table early.
**RESOLVED.**  
Evidence: Table 1 appears on page 2: *“Takeaway: the whole paper in four numbers.”* This directly addresses reader-first structure.

### Ask 5. Strengthen or explicitly weaken the “k=1 helps” half without relying on companion papers.
**PARTIALLY RESOLVED.**  
Evidence of improvement:
- They no longer assert a universal “k=1 helps”; they explicitly say it’s judge/domain dependent: Abstract: *“The benefit half is capability- and domain-dependent, measurable for one of our two judges and not the other.”*
- Sec. 3.3 shows **k=1 help failing on cross-generator text**: *“The k=1 help does not replicate”* (P-S5).
- Sec. 3.4 is explicit: *“the only measured k=1 benefit is phi-4’s… with Qwen-7B’s k=1 delta a null”* (Sec. 3.4; Table 7).

What’s still missing: a clean confirmatory demonstration of “helps” beyond a narrow setting; the paper mostly ends up at “doesn’t hurt / sometimes helps,” which is fine but contradicts some strong phrasing like Table 4 caption *“the reference helps at k=1”*.

---

# PART 3: THREE SPECIFIC QUESTIONS

## (a) Compact ask-by-ask verdict list
1. Ask 1 (narrow/harden claim): **RESOLVED**  
2. Ask 2 (replication vs mitigation comparability): **PARTIALLY RESOLVED**  
3. Ask 3 (margin→inflation quantitative link): **RESOLVED (negative result)**  
4. Ask 4 (promote simple main table early): **RESOLVED**  
5. Ask 5 (“k=1 helps” strengthened or weakened): **PARTIALLY RESOLVED**

## (b) Negative result judgement (Ask 3)
Reporting this negative result **strengthens the paper’s credibility** but **weakens the paper’s mechanistic case**.

- It strengthens credibility because it is exactly the kind of analysis authors are tempted to omit. You say: *“we report it because it is the test the causal story most invites.”* (Sec. 3.2). That’s the right scientific behavior.
- It weakens the “anchoring margin is the pathway that explains inflation” story. Rotation shows anchoring *exists* and is *causal for scores*. But if per-item margins don’t predict per-item inflation (especially Qwen’s r≈0), then “anchoring” may be necessary-but-not-sufficient, or your margin estimate is too noisy, or inflation is driven by other item-level features (e.g., pass-rate distributions, score variance structure, extraction/formatting noise, or selection dynamics interacting with saturation).

Would my accept/reject change vs omission? **Yes: it makes me more likely to accept.**  
If you had omitted the linkage test, a hostile Q&A would ask “do larger anchoring margins actually produce larger inflation?” and your answer would be hand-wavy. Including the weak result preempts that and forces you to appropriately downgrade causal pathway language. Top-tier venues reward that honesty.

What you should do about it:
- **Downgrade “mechanism” phrasing** (especially in Abstract: *“The mechanism is anchoring”*). Replace with: anchoring is a causal bias; the mapping from bias magnitude to selection inflation is not yet established at item level.
- Add a short paragraph proposing why linkage may fail: measurement noise (few valid samples per item), ceiling saturation (noted in Sec. 3.2), inflation estimator variance, and heterogeneity in pool composition. Ideally add a simple simulation showing that even if anchoring causes inflation, per-item correlation can be low under realistic noise.

## (c) Cold-read clarity after two pages
**Yes, mostly.** After ~2 pages, I can state:
- **Main claim:** Showing a single reference answer to an LLM judge causes harmful anchoring on tasks with multiple valid answers, increasing selection-induced score inflation vs blind judging.
- **Main number:** Table 1 / Abstract: **+1.19 [+1.02, +1.36] baseline SD** inflation increase (conservative **+0.90** on clean extraction items).
- **Scope:** *“short-answer tasks with exact programmatic validity oracles”*; not free-form.

Where I had to backtrack / hunt:
- The definition of **“inflation”** is only fully spelled out in Setup: *“Inflation, formally the excess hack gap…”* I had to jump to Section 2 to understand “baseline SD over permutation null.”
- “Selection uses rubric a and reporting uses rubric b…” (Setup) is nonstandard; I had to reread to see why that’s not leakage and how it “cancels winner’s-curse inflation.”
- The replication Table 2 note about different populations across endpoints is subtle and required rereading: E1 uses [0.2,0.8] but P-R2/P-R3 use all 93 eligible items. This is exactly the kind of “wait, which n is which?” friction that Table 1 tries to eliminate but doesn’t fully.

Overall: the frontloaded Table 1 + Figure 1 + “How to read this section” paragraph in Sec. 3 are strong improvements; the remaining clarity issues are mostly around estimator/population bookkeeping and scale units.