# De-risking Plan A — a research brief for an autonomous agent (Fable)

> **What this is.** A senior-researcher's plan for the *next* phase of the judge-free-evaluation project. It
> (1) audits which of [Plan A](plan-A-tfa-with-ground-truth.md) is already implemented, and (2) lays out — in
> executable detail — the highest-value experiments to de-risk the paper's central claim. Read this fully, then read
> the repo docs in §1, then execute the workstreams in priority order (§4). This complements the broader
> [`fable-weekend-research-brief.md`](fable-weekend-research-brief.md) (infra, rigor, formal-math track); where they
> overlap, this document is the more current and more specific.

---

## 0. Mission

**Determine whether the judge-free evaluation result we have measured is *real and general* — not an artifact of one
LLM judge and one model family — and push the one scientific question that is still open: can any judge-free signal
grade reasoning *among correct answers*?**

We are past the exploratory phase. On natural-language math we have a clean, honest result (§2). The job now is not to
find new signals; it is to **de-risk the claim** so it survives review and generalizes, and to **advance the frontier**
on the one question everything has failed at. "De-risk" here has a precise meaning: reduce the largest sources of
uncertainty that could invalidate the central claim, in decreasing order of how much they threaten it.

---

## 1. Required reading (in the repo, before you touch anything)

- [`experiments/tfa-vs-judge/paper/PAPER.md`](../experiments/tfa-vs-judge/paper/PAPER.md) — the current human-facing
  result (6 datasets, the saturation mechanism, the rollout process value, the failed-variants appendix). **Start here.**
- [`experiments/tfa-vs-judge/JOURNAL.md`](../experiments/tfa-vs-judge/JOURNAL.md) — every number, every variant tried,
  bug post-mortems, the rollout-PRM completer curve. The detailed record.
- [`docs/plan-A-tfa-with-ground-truth.md`](plan-A-tfa-with-ground-truth.md) — the original plan this brief audits.
- [`docs/fixing-tfa-item-level.md`](fixing-tfa-item-level.md) — the literature survey (PRMs, self-consistency,
  self-verification, ROSCOE/ReCEval) and why the cheap fixes were predicted to fail.
- [`docs/fable-weekend-research-brief.md`](fable-weekend-research-brief.md) — infra, rigor rules, the formal-math
  (Lean-oracle) track, Workstream C rollout depth.
- **Harness to reuse (do not rebuild):** `experiments/tfa-vs-judge/tfa/` (metric core, backends, `boxed.py` fixed
  Math-Verify, `judge.py` litellm judge, `corrupt.py` shortcut corruptions, `analyze.py` partial-ρ + bootstrap) and
  `experiments/tfa-vs-judge/scripts/` (`run_all.py`, `run_judge.py`, `run_variants.py`, `run_rollout_prm.py`,
  `analyze_workstream_a2.py`, `make_figures.py`). The local analysis venv is `.venv-local`
  (numpy/scipy/matplotlib/math-verify); the cluster venv is on `/lfs`.

---

## 2. What is already established, and the Plan-A audit (do NOT re-derive)

**Fixed setup so far.** Qwen2.5-Instruct ladder {0.5B…14B (+32B on MATH-500)} × six NL-math datasets. Judge = gpt-5.2
(0–10 reasoning rubric on the model's free-generation). Correctness = `$`-delimited Math-Verify (boxed-first).
Decision metric = **partial Spearman ρ(signal, judge | correct)** with bootstrap 95% CIs, length- and difficulty-controlled.

**The result to build on (all six datasets, 5-model ladder):**
- **Model-level TFA works everywhere** — ρ(mean-TFA, judge) = **+0.60 → +1.00**, strongest on the hardest data (Putnam
  +1.00), weakest on saturated easy data.
- **Item-level TFA is a saturation/family effect** — statistically **0 on MATH** (both subsets), **+0.12 on GSM8K**,
  **+0.22 on Putnam**; length-robust. It appears only where TFA's range across the ladder is wide (0.03 easy → 0.07 hard).
- **The signal is genuine, not artifact** — survives contamination control (Putnam→functional Variations, +0.22→+0.15)
  and label-noise control (GSM8K→Platinum, +0.12→+0.06).
- **Rollout process value is the only item-level signal that works** — on MATH-500, partial ρ(value, judge | correct)
  = **+0.43** with a mid-strength 14B completer (inverted-U in completer strength), and it produces the first-ever
  positive **within-correct** signal, **+0.19 [0.09, 0.29]** — where every cheap TFA variant sat at 0. It is a
  process-reward / soft-verifier, **not cheap** (~K·T× a forward pass).
- **All cheap gold-token TFA variants failed** (content-token, logprob/BPC, surprisal-, IDF-weighted, answer-swap
  [a `1/length` artifact, retracted], step-shuffle). The item-level signal is *absent* under gold-prediction, not
  hidden under a confound.

### Plan-A audit — implemented vs. not

| Plan-A item | Status | Evidence / gap |
|---|---|---|
| **E0** harness (vLLM logprobs, masking, argmax+logprob, HF==vLLM) | ✅ **Done** | `tfa/core.py`, `scripts/verify_backends.py` (exact match) |
| **E1** reproduce MATH TFA↔accuracy | ✅ **Done, exceeded** | model-level ρ +0.94 on MATH ladder (paper > 0.66 cross-model) |
| **RQ1 / E2 crux — TFA vs. LLM judge, item-level** | 🟡 **Half done** | Judge side complete (6 datasets). **Human-rating (T2) side NOT done — the biggest validity gap.** |
| **RQ2 shortcut / exposure-bias control** | ✅ **Done** | content-token, answer-swap, step-shuffle in `corrupt.py`; length confound characterized |
| **RQ4 Putnam-AXIOM + contamination Variations** | ✅ **Done** | first TFA on Putnam; Variations +0.22→+0.15 |
| **RQ5 argmax vs. logprob / normalization** | ✅ **Mostly done** | argmax + logprob/BPC compared; length-norm via length control. `TFA-topk` not run (low value) |
| **RQ3 multi-reference TFA** | ❌ **Not done** | needs K verified gold refs per problem |
| **Baseline-metric matrix** (ROSCOE ×18, BERTScore, BLEU/ROUGE) | ❌ **Not done** | only TFA-variants + rollout compared; no prior-metric positioning |
| **≥15 models across families** | ❌ **Not done** | Qwen2.5 only — single family, single tokenizer |
| **≥2 judge families (self-preference bound)** | ❌ **Not done** | single judge (gpt-5.2) — the ground truth is unreplicated |
| **RQ6 / E4 formal-math (Lean) track** | ❌ **Not done** | entire formal track unstarted (see `fable-weekend-research-brief.md` §B) |
| Rollout process value (beyond Plan A) | ✅ **Done (v1)** | completer curve, within-correct +0.19; step-level & self-reference not yet |

---

## 3. Priorities — what to de-risk, and why (the senior-researcher call)

The central claim is *"a judge-free, reference-grounded signal can evaluate math reasoning — cleanly at the model
level, and, with a costly process signal, weakly at the item level."* Ranked by how much each threatens that claim:

1. **Is the ground truth real? (judge validity).** Every item-level number is measured against *one* LLM judge. A
   reviewer's first attack is "you validated a judge-free metric against an unvalidated judge — circular." **De-risk
   two ways:** (D1) cross-family judge invariance — fully autonomous, cheap, do first; (D5) a human-calibrated subset
   — needs humans, so Fable *builds the pipeline and picks the sample*, humans grade. **This is the #1 external-validity risk.**
2. **Is it Qwen-specific? (generalization).** One model family, one tokenizer. TFA is a tokenizer-level statistic, so
   family-specificity is a live worry. **De-risk:** (D2) cross-family, cross-scale models on the three anchor datasets.
3. **The open science: grade-among-correct.** The deepest question — can any judge-free signal separate *valid-correct*
   from *lucky-correct*? We have a fragile +0.19. **Advance:** (D3) rollout depth (step-level dips) + the **self-reference**
   idea (anchor on the model's own consistent solution, not a fixed gold). Highest reward, highest uncertainty.
4. **Paper completeness.** (D4) multi-reference TFA (quantify the alternate-path penalty) and the baseline-metric matrix
   (position TFA vs. ROSCOE/BERTScore/BPC). Necessary for a submission, lower scientific risk.
5. **Second-paper frontier.** (D6) the formal-math (Lean-kernel-oracle) track — the only setting with a *true* oracle,
   so it sidesteps the judge-validity problem entirely. High value, high build cost; scope as a follow-on.

**Execution order for an autonomous agent:** D1 → D2 → D3 in parallel where compute allows (D1 is API-only/GPU-free and
can run alongside D2's GPU jobs), then D4; prepare D5's artifacts early (it unblocks the human de-risk); treat D6 as stretch.

---

## 4. Workstreams (full detail)

### D1 — Cross-family judge invariance: *is the ground truth real?* (do first; cheap, GPU-free)

**Problem.** All item-level conclusions rest on gpt-5.2 as ground truth. If a different judge family reverses them, the
"judge-free" claim is measured against a mirage. LLM judges are known to be prompt-sensitive and self-preferring
(Zheng et al. 2023 arXiv:2306.05685; Self-Preference arXiv:2410.21819).

**Hypothesis.** The qualitative item-level picture — **MATH ≈ 0, GSM8K small +, Putnam largest +** — and the
model-level ranking are **judge-invariant**; different frontier judges agree at the item level well above chance.

**Method.** Re-judge the *already-saved* free-generations (no GPU, no re-generation) with ≥2 more judge families using
the existing pipeline — it is one flag:
```
python scripts/run_judge.py "runs/<ds>/*.jsonl" --judge-model anthropic/claude-opus-4-8   --workers 16 --suffix judged_claude
python scripts/run_judge.py "runs/<ds>/*.jsonl" --judge-model gemini/gemini-3-pro          --workers 16 --suffix judged_gemini
```
Verify current SOTA judge IDs by web-search before pinning (do not hardcode from memory). Use the *same* rubric prompt
for all judges (it lives in `tfa/judge.py`) so differences are the judge, not the prompt. Run all six datasets × the
5-model ladder. Reuse `run_judge.py`'s per-item exception handling (a flagged prompt must not kill the run).

**Analysis & decision criteria.**
- For each judge, recompute the full `analyze_workstream_a2.py` table (model-level ρ, item-level partial ρ | correct,
  within strata, length control). **Report all three judges side by side.**
- Compute **inter-judge agreement** at the item level: pairwise Spearman ρ between judges' 0–10 scores, overall and
  *within-correct* (the hard stratum), per dataset. Also report exact/±1 agreement and Krippendorff's α.
- **Success (claim holds):** the sign/ordering pattern replicates under all three judges, and inter-judge item-level ρ
  is substantial (pre-register a bar, e.g. overall ρ ≥ 0.6, within-correct ρ ≥ 0.3). The paper can then say the result
  is judge-invariant.
- **Informative failure:** judges disagree at the item level (esp. within-correct) → the "ground truth" is unstable →
  this *itself* is a headline result ("even frontier judges don't agree on what good reasoning is beyond correctness")
  and reframes the whole contribution around judge unreliability motivating judge-free signals. Either outcome is a win.

**Cost.** API only. ~2 judges × ~11k traces (6 datasets × 5 models × 500–1180) ≈ 22k calls; a few hours, low $. **This
is the single best value-per-dollar experiment in the plan — do it first.**

---

### D2 — Cross-family & cross-scale generalization: *is it Qwen-specific?* (GPU)

**Problem.** TFA is computed from a model's own tokenizer and logprobs; the model-level correlation and the item-level
saturation gradient could be idiosyncratic to Qwen2.5's tokenizer and post-training. Plan A wants ≥15 models across
families for exactly this reason.

**Hypothesis.** Model-level ρ(mean-TFA, judge) stays high (> 0.7) across families, and the item-level pattern
(≈0 on MATH → +0.2 on Putnam) reproduces family-by-family.

**Method.** Add ≥5 models from ≥4 other families spanning 7B→70B, keeping open-weights + logprob access. Recommended
starting set (verify availability, licence, and logprob support on the cluster before pinning; web-search current
open-math SOTA first): **Llama-3.x-{8B,70B}-Instruct, Qwen3-{8B,32B}, Mistral/Mixtral, Gemma-2/3-{9B,27B}, OLMo-2,
DeepSeek-R1-distill (reasoning-tuned)**. Run on the three **anchor datasets** (MATH-500, GSM8K, Putnam-AXIOM) — the
cheapest set that spans the difficulty regimes — via the existing `run_all.py` (TFA + free-gen), then judge with the
D1 judges. Include base vs. instruct vs. reasoning-tuned where a family offers them, to probe the weak-model
next-token floor and the reasoning-tuned tokenizer effect.

**Analysis & decision criteria.**
- Model-level: pool all families, recompute ρ(mean-TFA, judge) and ρ(mean-TFA, accuracy) per dataset with the larger n;
  also report *within-family* to check the correlation is not driven only by cross-family scale.
- Item-level: recompute partial ρ | correct pooled and **stratified by family** (guard against a Simpson's-paradox
  pooling artifact — different families at different TFA offsets can manufacture or mask a pooled correlation).
- **Success:** model-level ρ stays high across and within families; the MATH→Putnam item gradient reproduces. Claim generalizes.
- **Informative failure:** the pattern is Qwen-specific → scope the claim to "within-family model ranking" and report
  the tokenizer/family dependence as a limitation and a finding.

**Cost.** GPU. ~8–10 models × 3 datasets × (TFA + free-gen), vLLM; ≈ 1–2 GPU-days on a shared node (right-size per
GPU-allocation rules in the weekend brief). Then D1-style judging (API).

---

### D3 — The grade-among-correct frontier: rollout depth + self-reference (highest reward)

**Problem (the whole fight).** Can *any* judge-free signal separate a genuinely-sound correct solution from a
luckily-correct one? TFA and all variants: 0. Rollout value: a fragile +0.19 (14B completer only). This is the marquee
scientific question and where a novel result lives.

**Two bets.**

**(a) Rollout depth — step-level value dips.** Replace the 4 fixed cut-points with true per-step values on the
model's own trace; a *within-correct* solution whose value **dips then recovers** contains a wrong/irrelevant move a
clean derivation does not. Use the 14B sweet-spot completer (from the completer curve); apply OmegaPRM's efficiency
(binary-search the first value-drop on monotone trajectories; reuse rollouts) *only after* the dip signal is confirmed.
Features to test against the judge: `min_i V_i`, the size/location of the largest drop, and a "recovered-from-dip" flag.
Reuse `scripts/run_rollout_prm.py --completer Qwen/Qwen2.5-14B-Instruct --k 8 --cutpoints <fine grid> --save-raw`.

**(b) Self-reference — anchor on the model's *own* best solution, not a fixed gold (novel; motivated by the saturation
finding).** The item-level failure of TFA is that a *fixed, easy* gold is uninformative. Instead:
- **Self-TFA:** teacher-force the model on its *own* highest-confidence / self-consistent solution (or the majority-vote
  answer among K samples) rather than the dataset gold. Signal = "how coherently does this trace agree with the model's
  own best reasoning." Does not saturate on easy references; needs no gold at all (a bridge toward Plan B).
- **Consistency-graded value:** among K sampled solutions to a problem, does agreement with the *modal reasoning path*
  (not just the modal answer) track judged quality within the correct stratum?
Test both against the judge with the standard partial-ρ protocol; compare head-to-head to fixed-gold TFA and to the
rollout value on the *same* items.

**Analysis & decision criteria.** Primary endpoint = **within-correct partial ρ(signal, judge | correct)** with CI, on
MATH-500 (where fixed-gold everything is 0, so any positive is meaningful) and Putnam (where fixed-gold TFA already
has range). Control for correctness, difficulty (V(0)), and length; construct a confound-independent version and check
survival (the retraction discipline). **Success:** a within-correct signal whose CI excludes 0 and that beats +0.19,
*or* a clean, well-controlled **negative** establishing the ceiling ("no judge-free signal grades among correct answers
— here is the evidence"). Both are publishable; the negative is a real scientific result, not a failure.

**Cost.** GPU-heavy (rollouts / K-sampling). Start on a MATH-500 subset (≥150 problems × 3 evaluated models) before scaling.

---

### D4 — Multi-reference TFA + baseline-metric positioning (paper completeness; medium)

**Problem.** Two Plan-A deliverables remain for a credible submission: quantify the single-canonical-path penalty
(RQ3), and position TFA against the prior reference-based reasoning metrics it claims to beat.

**Method.**
- **Multi-reference TFA (RQ3):** obtain K gold references per problem — human alternates where available; otherwise
  synthesize alternates and **gate them by Math-Verify answer-equivalence** (never teacher-force against unverified
  "gold"). Compute `TFA-multiref = max_k TFA(gold_k)` and report the shrinkage of the low-TFA/high-judge (alternate-path)
  tail. Expectation (from `fixing-tfa-item-level.md`): fixes only the alternate-path half of the null, not the length
  half — confirm and quantify. Extend `run_variants.py`.
- **Baseline matrix:** compute BPC/perplexity (have), **ROSCOE ×18**, **BERTScore**, **BLEU/ROUGE**, and Math-Verify
  exact-match on the same traces; correlate each against the judge (and, when D5 lands, against humans). The headline
  comparisons: `ρ(TFA, judge)` vs. `ρ(ROSCOE, judge)` (TFA claims to beat ROSCOE's ≤0.53) and vs. `ρ(EM, judge)` (does
  TFA's *process* granularity beat the free final-answer bit?).

**Decision criteria.** Multi-ref: report the penalty size and whether within-correct improves. Baselines: a single
comparison table (all metrics × datasets × {vs-accuracy, vs-judge}) with CIs. **Cost:** modest GPU (multi-ref logprobs)
+ CPU (metric libraries).

---

### D5 — Human-calibration harness (enabling the #1 de-risk; Fable builds, humans grade)

**Problem.** The judge is validated only against itself and other judges (D1). The proposal's Tier-2 human ratings are
"the primary ground truth and the biggest external-validity gap." Fable cannot recruit raters, but it can remove every
other obstacle so grading is turnkey.

**Fable's deliverables (no human needed to produce these):**
- **Stratified sample of 300–500 traces** across {dataset × difficulty × correctness × TFA-decile × judge-agreement},
  deliberately over-sampling the **within-correct, high-judge/low-TFA and low-judge/high-TFA disagreement cells** (where
  the metric and judge conflict — the most informative to grade).
- **Rubric + annotation UI** (final-answer correctness, local step validity, gap severity, overall quality — matching
  the judge rubric so human-vs-judge is apples-to-apples) with per-item logging, ≥2 raters/item for IRR, and a gold
  seed set for rater calibration.
- **Analysis script, pre-written**, that on ingest of human labels computes `ρ(TFA, human)`, `ρ(judge, human)`,
  `ρ(rollout-value, human)`, inter-rater reliability, and the head-to-heads Plan A §7 specifies.

**Decision criteria (once humans grade):** `ρ(TFA, human)` vs. `ρ(judge, human)` on ≥2 datasets; and does the judge
faithfully stand in for humans (high `ρ(judge, human)`)? If yes, every judge-based number in the paper inherits
external validity; if no, the judge-free framing gets *stronger* (judges are unreliable) but item-level ground truth
must be rebuilt on humans.

---

### D6 — Formal-math (Lean-kernel-oracle) track (stretch / second paper)

The one setting with a **true, judge-free oracle**: the Lean kernel decides correctness with no judge and no
faithfulness gap. This sidesteps D1/D5 entirely for the correctness signal. Naive token-TFA on proofs is known-inadequate
(alpha-equivalence, definitional equality; arXiv:2406.07222), so use **semantic-equivalence grading** (bidirectional
prover entailment / SMT) and a **rollout value with the kernel as oracle** (V = P(a completion compiles). Full spec,
datasets (VeriBench, VERINA, MiniF2F, PutnamBench), and methodology are in
[`fable-weekend-research-brief.md` §4B](fable-weekend-research-brief.md). Scope as a follow-on once D1–D3 land.

---

## 5. Rigor rules (non-negotiable — carried from the retraction lesson)

1. **Decision metric is always `partial ρ(signal, judge | correct)` with a bootstrap 95% CI**, plus within-correct and
   within-wrong strata reported separately.
2. **Stress-test every positive before believing it.** Additionally control for length and difficulty; build a
   confound-independent version and check it survives. If it dies under control, it is an artifact — say so and drop it.
   (This is how `contrast_answer` was caught.)
3. **Correctness = `$`-delimited Math-Verify** (NL) / **Lean kernel** (FL). Never the raw-string fallback for headline
   numbers; verify `math_verify` is importable before trusting any accuracy.
4. **Report negatives honestly and precisely.** A well-scoped negative (e.g. "judge-free signals cannot grade among
   correct answers," or "the result is Qwen-specific") is a real result. Keep a **claims ledger**: every number →
   the script/run/commit that produced it.
5. **Save all raw artifacts to `/dfs/scratch0/<user>/jfe_raw/`** (rollouts, per-token records, free-gen, judge
   responses) with fixed seeds and a `manifest.jsonl` (run-id → config → artifact path). Commit only slim per-item
   scores + summaries + figures. Regenerate numbers from `runs/scores_*.jsonl` via `analyze_workstream_a2.py`.
6. **Same rubric prompt across judges; verify current SOTA model IDs by web-search before pinning; right-size GPUs**
   (`CUDA_VISIBLE_DEVICES`, baseline-then-scale) per the weekend brief.

---

## 6. Analysis protocol (apply uniformly)

For each (signal, dataset, judge): Spearman **and** partial ρ(·, judge | correct) with bootstrap CI; within-correct
and within-wrong strata; for any positive, the length- and difficulty-controlled version. Model-level:
ρ(mean-signal, accuracy) and ρ(mean-signal, judge) with n and CI. For D1/D2 add the cross-judge and cross-family
agreement matrices. Produce a **single comparison table** spanning all datasets × signals × judges, and figures
(reuse `make_figures.py`; add a cross-judge panel and a cross-family panel). Prefer plots of signal vs. judge colored
by correctness.

---

## 7. Deliverables & definition of done

1. **Cross-judge table + agreement matrix** (D1): the six-dataset result under ≥3 judge families, with an explicit
   invariance verdict and inter-judge item-level agreement. *(Highest priority; ship first.)*
2. **Cross-family generalization table** (D2): model-level and item-level results across ≥4 model families, pooled and
   stratified, with a Qwen-specific-or-general verdict.
3. **Grade-among-correct result** (D3): a within-correct number for rollout-depth and for self-reference signals — a
   positive that beats +0.19, or a controlled negative pinning the ceiling.
4. **Multi-reference penalty + baseline-metric table** (D4).
5. **Human-calibration harness** (D5): stratified sample + UI + pre-written analysis, ready for raters.
6. A running **claims ledger** and incremental commits to `main`; update `PAPER.md` and `JOURNAL.md` as results land.

**Done** = (1) and (2) complete with clear verdicts (the claim is either shown judge-invariant + general, or precisely
re-scoped), (3) has a defensible within-correct result (positive or a clean ceiling), and every headline number is in
the claims ledger with a reproducible script.

---

## 8. Explicit non-goals

- Do **not** chase more cheap gold-token TFA patches (weighting/masking/contrastive) — ruled out; the null is absence
  of signal under gold-prediction, not a hidden confound. (Self-reference in D3 is *not* this — it changes the anchor.)
- Do **not** report a positive without the confound-control + CI (the retraction lesson).
- Do **not** conflate judge-free *model ranking* (solved) with judge-free *per-response grading* (open).
- Plan B (agentic / sparse-feedback / gold-free) remains future work, except the self-reference bridge in D3.
