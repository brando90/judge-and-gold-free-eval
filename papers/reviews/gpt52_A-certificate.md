## (a) Three-sentence summary of what the paper claims
The paper claims that *static* “raw agreement with humans” is an insufficient pre-deployment check for LLM judges because a judge can agree on unoptimized data yet be reward-hacked under optimization pressure. It proposes a cheap “certificate” audit: collect ~60 blind human labels on **two axes** (soundness vs. style) and compute **partial correlations** to output a categorical verdict (**pass/fail/convict**) that predicts whether best-of-n optimization will game the judge. It reports that these frozen verdicts predict downstream best-of-64 behavior for **10/11 registered** judge configurations (12/13 including two late-scored additions), including “convicting” a sabotaged frontier judge and a popular open reward model that raw agreement cannot distinguish from honest mid-size judges (Table 1).

---

## (b) Axis assessments (1–10), with concrete quotes and table callouts

### 1) NOVELTY — **6/10**
**What’s actually new:**  
- The paper’s *core idea*—separating “substance” vs “style” and checking evaluator susceptibility to superficial cues—exists in prior work class-wide (they cite it: “Style over substance biases are documented…” [23, 14, 20], and reward-model style fragility [19]).  
- The **incremental novelty** is the *operationalization* as a **per-deployment, pre-registered, categorical audit** using partial correlations plus a positive control, and validating it against actual optimization pressure (“frozen verdicts predicted the pressure outcome for ten of the eleven registered configurations.” Abstract / Table 1 / Table 3).

**Where it’s less novel than advertised:**  
- Partial correlations + multi-trait reasoning is literally acknowledged as old: “The design has a classical lineage… multitrait-multimethod construct validation… [12]… not inventing the statistics.” (Related Work). So the novelty is packaging + applied demonstration, not conceptual/statistical invention.  
- The paper leans hard on companion drafts [7,9] for the mechanistic story (“Companion work shows… compare vs verify…”), which makes this submission feel like the “productization wrapper” around another paper’s core insight.

**Where novelty *is* real:**  
- The explicit *pass/fail/convict* framing with a sign-anchored “convict” region (“convict if the style partial exceeds 0.30”) is a clear operational contribution that practitioners can implement.  
- The claim that “raw agreement cannot tell apart” a sabotaged capable judge from weak/honest judges is convincingly illustrated in Table 1 and Figure 2.

### 2) SOUNDNESS — **4/10**
The paper is well-intentioned and does more preregistration than typical ML papers, but a hostile Q&A will shred multiple inferential and design gaps.

**Major threats:**
1) **Single primary annotator (author, hypothesis-aware) on the headline audit.**  
   They admit it: “The primary annotator is an author and hypothesis-aware” (Sec. 7). The replication is only **30 items** and style reliability is poor (Table 4: style reliability 0.48). Convictions rely on *style partial*, i.e., the noisiest axis. Your “convict” decisions are thus riding on a weak instrument.

2) **n=60 per configuration is extremely small for stable partial correlations**, especially with correlated axes.  
   They themselves say style/soundness correlates at +0.82 “in the wild” (Sec. 1/2). Estimating partial correlations with strong collinearity at n≈60 is high-variance and sensitive to any scoring nonlinearity/outliers. The paper attempts to mitigate with a decorrelated subsample but then refuses to use it for headline partials (“numbers never enter the headline partials”). That choice is not obviously correct; it reads like cherry-picking which dataset gets to count.

3) **The verdict thresholds look tuned to this dataset, and the paper implicitly admits it via a post-hoc rule change.**  
   The “frozen rule” fails on the blind 14B (Table 1; Sec. 4). Then: “We therefore revise the rule, explicitly post hoc: certification requires the soundness-partial confidence interval… to clear the bar.” (Sec. 4). That’s exactly the kind of “nice-sounding correction” that ruins the purported pre-deployment guarantee. You can’t claim a *certificate* and then patch the certificate after seeing the one counterexample.

4) **Registration is internal git timestamps, not an external registry.**  
   “Registration means internal git timestamps… not an external registry” (Sec. 2). This is better than nothing, but it is not robust against accusations of selective disclosure or timeline massaging. For a paper selling itself on preregistered prediction (“one prediction ledger”), this choice is a credibility tax.

5) **Outcome validation is not as independent as it sounds.**  
   Many “configurations” are not independent tests: they’re a near-deterministic function of whether a reference is present + model scale (“verdicts are strongly collinear with one protocol bit… there are roughly four distinct verdict classes” Sec. 7). This is the authors admitting their own effective sample size is closer to **~4**, not 13. That collapses the evidential weight of “10/11 correct.”

6) **Best-of-n selection pressure is not training.**  
   They acknowledge: “pressure test is selection, not training… DPO validation is registered… queued” (Sec. 7). But the motivation (“LLM judges now rank models, filter data…”) often involves *training against the judge*, not only best-of-n sampling. The paper’s strongest claim—predicting “gets gamed the moment something optimizes against it”—is only partially supported by selection experiments.

7) **The reward-model inflation estimand is not the same as the judge inflation estimand.**  
   Table 1 marks inflation as “† … analogous but not identical estimand” and Section 7 says it “conflates winner’s-curse inflation with … sensitivity to content-preserving rewording.” That means the headline “largest inflation” result for the RM is not cleanly interpretable as reward hacking under optimization; it’s at least partially about paraphrase instability.

**Net:** interesting evidence, but too many degrees of freedom and too little clean, independent validation for the strength of the claims.

### 3) COMPLETENESS — **5/10**
A skeptical reader will still demand:

- **Multi-annotator labels for the full anchor set**, or at least adjudicated consensus for all 60 items, not a 30-item partial replication with low style reliability (Table 4).  
- **Sensitivity to choice of nuisance axis.** The paper says axes are threat-model-dependent, but the headline is entirely style-vs-soundness. Show that the audit works when the nuisance axis is length, verbosity, formatting, confidence tone, etc., using *human* nuisance labels (not only perturbations).  
- **A real attacker** (adaptive optimization) beyond best-of-n. “No attacker needed” is a selling point, but it also means you might simply be detecting a superficial “reference vs no reference” protocol artifact plus a contrived sabotage prompt.
- **Cross-domain, cross-task evidence with external datasets**. Right now math is the only audited domain; code is described as “post hoc extrapolation” and “pending” registered audit (Table 3).  
- **Calibrated uncertainty / decision theory**: if this is a “certificate,” what false-convict and false-pass rates should a practitioner expect? The paper reports one false pass and then changes the rule. That’s not a usable reliability story.

### 4) IMPACT — **7/10**
**What changes tomorrow (if true):**
- Teams using LLM judges for best-of-n, rejection sampling, data filtering, or evaluation could run a **small, structured audit** before deployment instead of relying on raw agreement. The “5–8 annotator-hours” pitch is actionable, and Table 1 gives an alarming example: sabotaged frontier and honest mid-size look similar under raw r but diverge under style partial.  
- The “convict” concept is practically useful: it identifies “capable-corrupt” evaluators (high style partial) that are exactly the scary failure mode (“inflates without measurable damage”).

**Why impact is capped:**
- The result risks being *folk wisdom operationalized*: everyone already suspects judges are style-biased; the contribution is a particular test, on a narrow set of judges/tasks.  
- The dependency on hand-labeling and partial-correlation heuristics means many orgs will treat this as another “internal check,” not a community standard, unless you provide stronger external validation and clearer guidance.

---

## (c) Readability verdict
**Readable but overconfident and cognitively heavy.** A first-year PhD can follow the story, find Table 1 quickly, and understand the plots (Figure 2/4), but the paper repeatedly mixes *registered*, *late-scored*, *post-hoc rule revisions*, and *companion-paper mechanisms* in a way that makes it hard to know what is actually proven versus merely suggested. The “prediction ledger” (Table 3) is helpful, but it also exposes how much is pending or partially non-registered.

---

## (d) Five highest-leverage improvements (ranked)

1) **Replace the single-author-labeled headline audit with fully blinded multi-rater labels for *all* 60 items**, with adjudication, and rerun every partial + verdict. If you want a “certificate,” your measurement procedure cannot be “author graded most of it.”

2) **Externally preregister (OSF/AsPredicted/clinical-trials style) the full audit rule + analysis + primary outcomes for at least one new dataset/domain**, and run it end-to-end. Internal git hashes are not enough given how central preregistration is to your claims.

3) **Demonstrate robustness across nuisance axes and scoring models**: show that “convict” remains meaningful if the nuisance axis is length/verbosity/confidence/structure (human-labeled), and not just “style.” Right now, your method is dangerously close to “detect style-bias with a style label,” which is tautological unless you show axis-general reliability.

4) **Run an adaptive optimization / training experiment now (even a small one)** instead of promising queued DPO. Your strongest motivating claim is optimization against the judge; best-of-n is not that.

5) **Clarify independence / effective sample size and report class-level conclusions accordingly.** You basically admit in Sec. 7 that you have ~4 independent classes. Reframe claims (and statistical tests) around that reality, or add genuinely diverse judge protocols that break the collinearity (different prompts, different reference formats, different judge families, different tasks).

---

## (e) Overall score and recommendation
**Overall: 6/10. Lean: Reject (borderline), primarily for soundness/validation gaps relative to the strength of the claims.**

This is an *interesting applied construct-validity audit* with a genuinely useful practitioner framing, and Table 1 / Figure 2 are compelling as an existence proof. But the paper oversells “certificate” strength given (i) author-provided labels on the main audit, (ii) tiny n and unstable partials near thresholds, (iii) internal-only preregistration, (iv) post-hoc rule revision after the failure case, and (v) outcome validation that is largely collinear with a single protocol bit (reference or not). If the authors deliver external preregistration + multi-rater labels + at least one adaptive-optimization replication, this could become a strong accept; in its current form, it is not NeurIPS/ICML-grade as a claims-to-evidence match.