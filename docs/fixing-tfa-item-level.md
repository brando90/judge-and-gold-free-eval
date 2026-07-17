# Can we "fix" TFA for per-response evaluation? — critique + literature survey

**Context.** In [`experiments/tfa-vs-judge`](../experiments/tfa-vs-judge/RESULTS.md) we found that Teacher-Forced
Accuracy (TFA) is a valid judge-free **model-ranking** signal (ρ ≈ 0.94 vs. a frontier judge and vs. accuracy)
but has **no item-level signal**: partial ρ(TFA, judge | correct) ≈ 0. Every gold-anchored variant we tried
(surprisal/IDF weighting, answer-swap and step-shuffle contrastive) failed; the one that looked promising was a
`1/gold_length` artifact. This note asks: *is there any judge-free way to recover a per-response signal, and do the
candidate fixes actually work?* Short answer, after surveying the literature: **the cheap fixes almost certainly
don't; the one principled option (rollout-based process scoring) trades cheapness for validity and is itself uncertain.**

---

## 1. Why the item-level goal is intrinsically hard

The field's answer to "score reasoning *quality* per response" is a **Process Reward Model (PRM)**, and every
variant requires **supervision or extra compute** — there is no cheap unsupervised token statistic that does it:

- **Lightman et al., *Let's Verify Step by Step*** — step-level quality via **human process labels**; process
  supervision beats outcome supervision.
- **Math-Shepherd** ([arXiv:2312.08935](https://arxiv.org/abs/2312.08935)) — removes human labels but defines a
  step's quality as its *"potential to deduce the correct final answer,"* estimated by **Monte-Carlo rollouts**.
- **OmegaPRM** ([arXiv:2406.06592](https://arxiv.org/abs/2406.06592)) — same idea via MCTS + binary search to
  locate the first error efficiently.

TFA is a **single-forward-pass token statistic**. The literature says per-step quality needs rollouts or labels.
That gap is the root reason TFA (and patches to it) stall at the item level.

---

## 2. Critique of the candidate "fixes" (grounded in literature)

### 2a. Self-consistency / own-trace confidence — *likely fails `partial | correct`*
Self-consistency (majority vote over samples) is by construction a **correctness/confidence** estimator, which is
exactly the axis we already control for. The quality-*beyond*-correctness signal is where it's documented weak:
- *Confidence Improves Self-Consistency* ([arXiv:2502.06233](https://arxiv.org/html/2502.06233v1)): confidence
  helps efficiency but **"doesn't fully capture the quality of the underlying reasoning process"**; the
  *most-calibrated* confidence was the *least* useful for the reasoning-aware variant.
- Path-quality methods (e.g. RASC) must **bolt on** explicit reasoning-path scoring precisely because vanilla
  self-consistency ignores path quality.
- **Consistency ≠ truth:** models produce *self-consistent errors*, so within the correct stratum it can't separate
  genuine reasoning from lucky/memorized-correct.
- **Verdict:** worth one cheap null-check, low prior.

### 2b. Error-detection surprise (self-verification via logprob) — *strong evidence against*
This assumes the model is a good verifier of its own steps via likelihood. The literature is nearly unanimous it is not:
- Huang et al., *LLMs Cannot Self-Correct Reasoning Yet* (ICLR 2024); ACL 2024: **LLMs cannot *find* reasoning
  errors, only fix them once the location is given.**
- *Self-Correction Bench* ([arXiv:2507.02778](https://arxiv.org/pdf/2507.02778)): a documented "self-correction
  blind spot." *Small LMs Need Strong Verifiers* (ACL 2024): the small models in our ladder especially can't self-verify.
- Likelihood tracks **fluency, not logical validity** — the teacher-forcing/"Clever Hans" shortcut
  (Bachmann & Nagarajan, [arXiv:2403.06963](https://arxiv.org/abs/2403.06963)).
- **Verdict:** the premise is exactly what the field says doesn't work.

### 2c. Multi-reference / symbolic intermediate-coverage — *partial at best, low ceiling*
Reference-based reasoning metrics are the closest prior art and they are **weak**:
- **ROSCOE** ([arXiv:2212.07919](https://arxiv.org/abs/2212.07919)) and **ReCEval**
  ([arXiv:2304.10703](https://arxiv.org/html/2304.10703)) correlate ~0.5 with humans; an LLM judge beats them
  (**SocREval**, GPT-4 ~0.58, [arXiv:2310.00074](https://arxiv.org/html/2310.00074)).
- Multi-reference fixes only the *alternate-path* half of our null, not the *length* half.
- **Verdict:** even the best gold-anchored judge-free reasoning metrics cap out ~0.5 — consistent with the
  Putnam-AXIOM paper's own ROSCOE ≤ 0.53.

---

## 3. The one principled option, explained: Math-Shepherd–style rollout PRM

This is the only item-level, **judge-free** approach with real literature support. It abandons teacher-forcing-on-gold
and instead measures whether each step of the *model's own* solution **preserves the ability to reach the correct answer**.

### Mechanics
1. Take the model's solution and split it into steps `s_1 … s_T`.
2. For each prefix `(problem, s_1..s_i)`, sample **K rollouts**: let the model (or a fixed "completer") finish the
   solution from that prefix, K times.
3. Check each rollout's final answer against gold with an **answer-checker** (Math-Verify) — *no LLM judge*.
4. **Step value** `V_i = (# rollouts from prefix-i that reach the correct answer) / K` — a Monte-Carlo estimate of
   `P(correct | reasoning up to step i)`. (Math-Shepherd's "soft" estimate; a "hard" variant credits a step if *any*
   rollout succeeds, i.e. it doesn't foreclose success.)
5. **Response score** = an aggregate of the trajectory, e.g. `min_i V_i` (a single value-destroying step tanks it),
   `mean_i V_i`, or the location/size of the largest value drop.

### Why it *could* capture quality beyond correctness (the mechanism TFA lacks)
Take two *correct* answers. In one, every step keeps `P(correct)` high (a clean derivation). In the other, some step
actually **lowers** `P(correct)` (a wrong/irrelevant move) and the model recovers by luck. The rollout PRM shows a
**dip** in the second — so it has a concrete mechanism to separate *confidently-correct* from *luckily-correct*,
which is exactly the within-correct distinction the judge makes and TFA cannot.

### How we'd test it (same protocol as everything else)
- For each (model, problem) free-gen response: segment → K rollouts/step → Math-Verify → step values → aggregate score.
- Report **partial ρ(PRM-score, judge | correct)** and within-correct ρ — does it beat TFA's ≈ 0?

### Cost — the honest tradeoff
`K × T × N × M` generations. At K=8, T≈10 steps, that's ~80 generations **per response** vs. TFA's single forward
pass. For 3000 items ≈ 240k generations — feasible on a GPU node for one model / a subset, but **~2 orders of
magnitude more expensive than TFA**. OmegaPRM's MCTS+binary-search reduces this; step-subsampling helps too.

### Critical caveats (why even this may not "win")
- **It is fundamentally an outcome predictor.** `V_i = P(reach correct answer)`, so within the correct stratum most
  values are high and the *variance that would carry quality signal may be small* — its `partial | correct` could
  also be weak. This is the central risk and an open empirical question.
- **Completer dependence:** values depend on the rollout model's ability to finish; weak models (our 0.5–3B) give
  noisy, deflated values (Math-Shepherd notes this).
- **Segmentation** of free-form math into steps is fiddly.
- **Not a "TFA fix":** it's a different, much costlier method that keeps only the "judge-free" property, not the
  cheap single-pass property that made TFA attractive.
- **Reference-dependent:** it still needs the gold *answer* for the checker (fine here, but not spec-free).

---

## 4. Bottom line & recommendation
- **None of the cheap patches is likely to make TFA a per-response judge replacement**; they either re-measure
  correctness (self-consistency) or rely on self-verification/likelihood-as-quality that the literature flags as
  unreliable, or cap at the ~0.5 ceiling of reference-based metrics.
- **TFA's real, validated niche is model-level ranking** — cheap, deterministic leaderboards. Lean into that.
- **If item-level judge-free is genuinely needed**, the rollout PRM (Math-Shepherd/OmegaPRM) is the only
  literature-backed path — but expect to pay ~KT× the compute and to face the open question of whether its
  `partial | correct` is actually non-zero.
- **Cheapest decisive next step:** run self-consistency's `partial ρ(SC, judge | correct)` as a null-check (low prior,
  but dispositive), then decide whether the rollout-PRM cost is worth it.

### Key references
- Wang et al., *Self-Consistency Improves CoT* (arXiv:2203.11171). · *Confidence Improves Self-Consistency* (arXiv:2502.06233).
- Huang et al., *LLMs Cannot Self-Correct Reasoning Yet* (ICLR 2024). · *Self-Correction Bench* (arXiv:2507.02778).
- Lightman et al., *Let's Verify Step by Step*. · *Math-Shepherd* (arXiv:2312.08935). · *OmegaPRM* (arXiv:2406.06592).
- *ROSCOE* (arXiv:2212.07919). · *ReCEval* (arXiv:2304.10703). · *SocREval* (arXiv:2310.00074).
- Bachmann & Nagarajan, *The Pitfalls of Next-Token Prediction* (arXiv:2403.06963).
- Gulati et al., *Putnam-AXIOM* (arXiv:2508.08292) — original TFA.
