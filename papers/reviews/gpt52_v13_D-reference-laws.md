## (a) Three-sentence summary of what the paper claims
The paper claims that **including a single “trusted reference answer” in an LLM judge prompt can *increase* reward hacking under best-of-n selection** whenever tasks admit multiple distinct correct answers, because the judge becomes an **answer matcher** rather than a validity assessor. It claims to establish this with an **externally preregistered replication** (Table 1) showing referenced judging increases “inflation” vs blind by **+1.19 baseline SD**, and with a **reference-rotation intervention** (Figure 1, Table 3) showing the *same exact sample* can gain **up to +9.5/10 points** purely by changing which valid reference is shown. It further claims a boundary condition (uniqueness vs multiplicity) and proposes a “structural fix”: **score blind first, then reveal the reference** (M1), which purportedly removes measured inflation at \(k>1\) (Table 7) though it leaves some anchoring residual.

---

## (b) Axis assessments (scores 1–10) with concrete quotes

### 1) NOVELTY — **6/10**
**What’s genuinely new:**
- The paper’s core novelty is *dynamic*: not just “reference bias exists” (already known), but **“reference bias becomes an optimization attack surface under selection pressure”** with a quantification of inflation under best-of-64. This is a real step beyond static accuracy drops.
- The **causal manipulation** is also a meaningful upgrade over correlational “judges prefer reference-like answers”: rotating the reference and re-scoring identical samples is a clean intervention.

**What’s not new / overstated:**
- The static phenomenon is explicitly conceded as prior art: “*We claim none of that as new*” (Related work).
- Even the dynamic direction is not entirely surprising to anyone who has thought about evaluator hacking + anchoring; the surprising part is **magnitude** and the fact that “trusted reference” is widely sold as a safeguard.
- The paper markets “anchoring” as if it’s a deep mechanism; it’s basically **prompt-induced leakage of a particular label** in multi-solution settings. Calling it anchoring is fine, but it’s not a new cognitive mechanism.

**Where novelty is blurred by companion-paper dependency:**
- The paper leans hard on companion A [3] for definitions, estimators, and the “capability gate.” As written, this is not a standalone contribution; it’s a **chapter** in a series.

Concrete quotes:
- “*A trusted reference answer in an LLM judge’s context is widely treated as a safeguard against gaming. On tasks with several valid answers it does the opposite.*” (Abstract)
- “*We claim none of that as new.* This paper adds five things. The dynamic result … The causal mechanism … The boundary statement … And a preregistered structural remedy …” (Related Work)

---

### 2) SOUNDNESS — **5/10**
There are strong elements (replication with exact oracle; causal rotation), but also several design/estimator choices that will not survive a hostile Q&A without additional ablations.

**Strengths:**
- **Externally preregistered replication** with exact programmatic validity oracles is a big deal in this literature. Table 1 is the best evidence in the paper.
- The **rotation experiment’s paired “same-sample Δ”** is a very strong causal readout: “*the identical sample text, scored twice … nothing changed but the reference*” (Section 3.2). That is hard to wiggle out of.

**Major threats / confounds / “I don’t buy it yet” points:**

1) **The main practical claim is about “gaming” under selection pressure, but the optimization is purely best-of-n sampling, not an adaptive attacker.**  
   The paper repeatedly frames this as “gaming” and “reward hacking,” but the generator is not using gradients / RL / iterative attacks; it’s just sampling. You can call it “selection pressure,” but “attack surface” implications for actual RM hacking are **inferred**, not demonstrated.  
   Quote: “*Under best-of-64 selection this preference quietly replaces ‘pick a correct answer’ with ‘pick the answer matching the key.’*” (Intro)

2) **Inflation estimator is bespoke and partly opaque without companion A.**  
   “Inflation… against a null built by shuffling judge scores among samples the checker grades identically.” That might be reasonable, but it’s not standard, and it’s easy to question whether it answers the thing you want (esp. under near-saturated validity). A reviewer will ask: why not report simpler metrics like (i) change in validity rate of selected samples, (ii) calibration curves, (iii) rank correlation with oracle validity, (iv) likelihood of selecting invalid under optimization? The paper admits lost-accuracy is mostly null and blames saturation. That’s not a satisfying story; it suggests the core “harm” may be primarily a *scoreboard artifact* rather than actual selection failure.

3) **Population filters differ across key experiments, undermining cross-table comparisons.**  
   Replication uses [0.2,0.8] pass-rate band for E1; mitigation experiment uses [0.05,0.95]; grid drops to 4–6 items per stratum due to filtering. The paper repeatedly warns “do not difference,” which is correct, but it also means the reader cannot build a coherent quantitative picture. In a hostile Q&A: *are your conclusions robust to the band choice?* Currently unclear.

4) **The grid (k-controlled) is severely underpowered per cell and relies on post-hoc analysis for the “step.”**  
   You build 12 tasks per stratum, then your estimator drops to **n=4–6 items per cell** (Figure 2 caption; Table 4 notes). Then you introduce the key “universal step” claim via a **post-hoc paired re-analysis** (Table 5), explicitly not preregistered. That’s a classic “the preregistered analysis was weak, so we did the analysis we needed.” It may still be right, but you can’t sell it as tight confirmatory evidence.

5) **Rotation experiment selection of rotated references is pool-aware, which is fine for within-sample causal effect, but it contaminates other readouts.**  
   The authors acknowledge: “*deliberately pool-aware … so the paired analysis would have coverage*” (Section 3.2 registration note). Great. But then they still report margins, collapse rates, etc., and try to interpret blind margins. Those are now partially about “modal answers the generator tends to output,” not purely anchoring.

6) **Mitigation M2 is a preregistration deviation that changes the object under test.**  
   You preregistered a hard gate and implemented a soft probabilistic multiplier: “*Deviation: M2 is a soft gate, not the hard gate registered.*” (Section 3.4). This is *not* a minor tweak; it changes the protocol qualitatively. The phi-4 success and Qwen-7B failure may be artifacts of this particular probabilistic design.

7) **Judge–generator entanglement is not fully resolved.**  
   The grid uses Qwen2.5-7B as both generator and judge in some cells, and the paper admits it: “*generator-equals-judge configuration*” (Limitations). That can inflate anchoring patterns (style familiarity, etc.). You try to address cross-family in some places, but the total picture is still patchy.

Bottom line: the replication + rotation are solid; the boundary-mapping + mitigation claims are promising but not yet airtight.

Concrete quotes/tables:
- Replication effect: Table 1 “*+1.19 [+1.02, +1.36]*”
- Causal flip: Table 3 “*Gainers: same-sample ∆ … +9.48 … +8.73 …*”
- Underpowered grid cells: Figure 2 caption “*so 4 to 6 items enter each plotted cell*”
- Post-hoc central statistic: Table 5 is explicitly “*Post-hoc paired re-analysis*”

---

### 3) COMPLETENESS — **4/10**
A skeptical reader will still demand the following before trusting the broad prescription “reference unsafe unless unique” and “blind-then-reveal fixes it.”

**Key missing pieces:**

1) **Real tasks where multi-validity is not a toy arithmetic set.**  
   Your confirmatory replication (Section 3.1) uses constraint families like “CRT remainders… digit sums.” That’s clean, but it’s not what most people mean by “open-ended tasks with multiple valid answers” (summaries, creative answers, design proposals, citations). The paper gestures at that, but does not test it.

2) **Human evaluation / human-grounded validity beyond LLM adjudication.**  
   In Section 3.5 checker audits, “GPT-5.2 adjudicated validity” is not a gold standard. If the central message is about evaluation reliability, outsourcing the “truth” to another LLM is shaky. For the replication you do have exact oracles, great; but then your claims about general multi-valid tasks remain ungrounded.

3) **Stronger attacker models than best-of-n sampling.**  
   The title and framing scream “reward hacking.” Then you never run an adaptive optimization loop against the judge (even a simple hill-climbing over edits, or an RL fine-tune against the judge score). Best-of-64 is a *weak* adversary. If you want to claim “attack surface,” demonstrate an attacker that *uses the reference explicitly*.

4) **Ablations of the reference format.**  
   Is the effect driven by (i) explicit “Reference answer: X” token, (ii) placement, (iii) quoting, (iv) showing rationale with reference, (v) showing multiple references sampled from the valid set, (vi) hiding reference until after scoring (M1), etc. You test a couple, but not systematically.

5) **Cost/benefit and failure modes of M1 at scale.**  
   You say “*costs nothing*” at \(k=1\), but it costs **2× judge calls** (Table 10) and leaves “roughly half the anchoring premium.” You do not test whether residual anchoring re-inflates under larger n (you explicitly say it’s untested). That’s a big hole because the whole point is optimization pressure.

Concrete quote that admits incompleteness:
- “*Whether that residual premium re-emerges as inflation under stronger optimization than best-of-64 is untested here.*” (Section 3.4)

---

### 4) IMPACT — **7/10**
If correct, this changes evaluation practice for a large class of benchmarks and internal eval pipelines.

**Who changes what tomorrow:**
- Anyone doing **LLM-as-a-judge evaluation with a single reference** on tasks with multiple acceptable answers should stop treating “add reference” as a default safety measure.
- Benchmark designers might stop shipping single “gold” references for multi-answer tasks, or they’ll ship protocols like M1 (“blind then reveal”), or they’ll ship enumerators/oracles where possible.

**Is it consequential or folk knowledge?**
- The static bias (“judges overreward reference-matching solutions”) is close to folk knowledge *among people who’ve looked*. The consequential part is the **dynamic inversion under selection** plus a **clean causal demonstration** and a protocol-level mitigation that at least works in the constrained setting.
- The preregistered replication helps: it’s not just another arXiv claim.

However: impact is limited by external validity. Right now the strongest evidence is on **short-answer, programmatically checkable** domains. The paper’s rhetorical scope is broader than the data.

---

## (c) Readability verdict — **6/10**
A first-year PhD student can follow the high-level story (reference causes matching; rotation proves it; replication shows inflation), but the paper is **over-engineered** and **ledger-heavy** in a way that obscures the main result.

Problems:
- The core estimator (“excess hack gap,” “baseline SD over permutation null”) is not explained concretely enough in the paper itself; it relies on companion A and vague intuition blurbs.
- Tables are information dense but not reader-friendly; Table 7 mixes deltas and margins and requires parsing long Notes to understand populations and bands.
- The paper is too proud of its preregistration machinery; Table 9 is useful but bloats the narrative and distracts from the cleanest experiments (Table 1 + rotation).

Positives:
- Figure 1 and Table 1 are strong, and the “rotation” story is easy to communicate.
- The authors are unusually explicit about deviations.

---

## (d) Five highest-leverage concrete improvements (ranked)

1) **Demonstrate the effect and M1 fix on at least one real multi-valid *natural language* task** (e.g., “give any valid citation,” “propose any satisfying design,” “any correct explanation”), with a human or rule-based verifier if possible. Right now “multi-valid answers” is rhetorically open-ended but empirically mostly arithmetic.

2) **Run an adaptive attacker, not just best-of-n**, even a simple one: iterative paraphrase/edit search maximizing judge score under blind vs referenced vs M1. Show that “reference matching” becomes an explicit exploit channel when the reference is shown.

3) **Make the inflation estimator auditable and replaceable in-paper.** Include a compact formal definition + sanity checks + alternative metrics (validity@1, validity@best-of-n, score–validity calibration, Spearman correlation of judge score with oracle validity). If the conclusion depends strongly on a bespoke “baseline SD” scaling, you need to prove it doesn’t.

4) **Fix the k-grid power issue**: increase items per stratum so that per-k claims aren’t built on “4 to 6 items enter each plotted cell.” If compute is tight, reduce judges/conditions but increase item count. Right now the “boundary mapping” section looks like it’s straining a tiny dataset.

5) **Cleanly separate confirmatory vs exploratory in the main narrative** and stop leaning on post-hoc analyses for key takeaways. The post-hoc “step” (Table 5), selection-pressure curve (Table 2), and pooled estimators muddy what is actually preregistered evidence. Put all post-hoc inferential claims in an “Exploratory analyses” subsection with explicit non-claims.

---

## (e) Overall score and accept/reject lean
**Overall score: 6/10. Lean: weak accept (borderline).**

Why not reject: Table 1 (externally preregistered replication with exact oracles) + the rotation intervention (Table 3 / Figure 1) together are a **credible, nontrivial, practically relevant** demonstration that “reference answers” can systematically *worsen* judge robustness under selection when multiple answers are correct.

Why not clear accept: the paper **overclaims generality**, the boundary and mitigation sections are underpowered / partly post-hoc / partially deviating from preregistration, and the “gaming” framing is stronger than what best-of-n sampling actually demonstrates. The work is likely publishable at a top venue if the authors tighten claims and add one compelling real-world multi-valid NLP setting plus an adaptive attacker.