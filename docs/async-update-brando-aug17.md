# Async update (Aug 17) — the coherent story, and the creative-metrics ask

## The story in one sentence

**Evaluation signals work when they *verify* and fail when they *compare* — and you can certify
which side of that line an evaluator is on before trusting it, with ~60 human labels, and that
static certificate predicts whether the evaluator survives optimization pressure.**

Everything we've run fits this as one of three acts. What looked like scattered experiments is the
evidence table:

## Act 1 — The comparison class fails, for one identified mechanism (this is where TFA lives)

Not just TFA: **five** reference-similarity metrics — TFA argmax, logprob, TF-IDF, unigram-F1,
MiniLM embeddings — all fail against human soundness ([−0.24, +0.14] vs judge +0.59, PV +0.49).
And we know *why*, causally, not just descriptively:

| evidence | result | takeaway |
|---|---|---|
| variance decomposition (4 model families) | 83–92% item, 3–7% style | the signal is mostly "which problem," not "how sound" |
| boundary map vs reference entropy | ρ = +0.89 | the apparent ranking signal tracks reference *complexity* |
| short-reference deconfound (same items) | boundary +0.35 → +0.02 | strip the reference to answer-only and the signal *vanishes* |
| code domain vs executable tests | r = 0.00 (n=492) | against a perfect verifier, similarity carries nothing |
| **TFA vs reference perplexity (new)** | **r = −0.895** (12 models × 500 items) | TFA *is* 80% reference-complexity-under-the-model; entropy-normalizing it kills the ranking signal (+0.13 → −0.17) |

**On your specific suggestion (weight first tokens less than last): ran it, full sweep, today.**
Per-token reference hits for 12 cross-family models on MATH-500, weighting w ∝ (pos/n)^γ from
uniform to last-tokens-only (registered prediction before the run: decay to the answer-only null):

| γ (late-weighting strength) | uniform | 0.5 | 1 | 2 | 4 | 8 | last-16 tok | last-4 tok |
|---|---|---|---|---|---|---|---|---|
| model-ranking ρ vs accuracy | +0.13 | +0.13 | +0.15 | +0.04 | +0.01 | −0.01 | +0.03 | −0.37 |

Weighting late tokens more makes TFA *worse*, monotonically past γ=1, ending negative — consistent
with the short-reference causal test (+0.35 → +0.02 on the Qwen ladder): the variance that
position-weighting redistributes is reference-complexity nuisance, not soundness. Clean negative,
mechanism-predicted.

## Act 2 — The verification class works, in proportion to how checkable the endpoint is

- **Executable tests** (code): the perfect case — free oracle, no human needed.
- **PV / completion-based** (+0.49 vs human): the one cheap metric with real signal — it *verifies*
  (can this trace be completed to the right answer?) rather than compares.
- **Judges — but only when anchored:** every Qwen judge fails the certification audit without a
  reference; every one passes with it. References flip judge *validity*, not just accuracy.

New metric slate this generates, each with a registered prediction (the class boundary predicts
which will work): entropy-normalized TFA (predict: null — comparison), prefix-repair PV curve
(predict: works — verification), answer-swap counterfactual (predict: works — verification),
divergence-point localization (predict: null — comparison).

**First one ran today — answer-swap counterfactual** (does the trace's reasoning actually pin down
the answer it asserts? support = lp(own boxed answer | prefix) − lp(swapped alternative | prefix),
fixed 7B scorer, judge-free): within-model correlation with correctness is positive in 8/9 models
(mean r +0.13, best +0.34; correct traces support their answers more than wrong ones in 8/9).
Direction confirms the class prediction — a verification-shaped signal carries real information
where five similarity metrics carry none — but the cheap single-point version is weak (judge +0.59,
PV +0.49 remain far ahead).

**And the strongest slate result — the prefix-repair curve** (truncate the trace at depth k, ask a
completer to finish it, read the success profile over k; entirely judge-free, and the data already
existed in the PV rollouts). Against the fresh n=80 random-stratum human labels (60 joined):

| truncation depth k | 0.0 (solve from scratch) | 0.25 | 0.5 | 0.75 |
|---|---|---|---|---|
| r vs human soundness | +0.54 | +0.68 | +0.76 | **+0.79** |

Monotone in depth — the more of the trace the completer conditions on, the more soundness signal —
which is exactly what "the trace's reasoning causally supports the answer" should look like. The
+0.79 at deep truncation is the best judge-free number in the whole class table (similarity metrics
≤ |0.14|, single-point PV +0.49; the LLM judge on the same 60 traces reads +0.89). Controlling for
problem difficulty (k=0 is a pure difficulty probe), the prefix's added completability still
carries +0.69. Caveats to tighten before claiming: one rater so far, mostly correctness-mediated
(among-correct r drops to +0.21), completer shares a family with some traces.

All four slate predictions registered pre-run landed as called: two comparison-class metrics null
or worse (position-weighting, entropy-normalizing), two verification-class metrics carry signal
(answer-swap weakly, prefix-repair strongly).

## Act 3 — Trust is certifiable ex-ante, and the certificate predicts hack-resistance

New this week: best-of-64 selection pressure against 25 judge configurations, math + code,
pre-registered.

- Every judge that **failed** the static certificate got hacked (excess score inflation +0.44 to
  +1.45, real accuracy loss 32–56%); every judge that **passed** resisted.
- The reference lever is **capability-gated by verification hardness** — the clean new mechanism:
  on math (compare text) even a 1.5B judge is rescued by the reference (regret 0.010, better than
  GPT-5.2); on code (mentally execute tests) the 1.5B judge gets *nothing* from it (Δ +0.06 ns),
  3B–14B get full inflation collapse, and the frontier needs it only for scoreboard honesty
  (GPT-5.2 regret 0.212 with and without the reference, but no-ref self-inflation +0.78 vs +0.22).
- A style-hacked frontier judge shows **inflation without damage** in both domains — it deceives
  the metric, not the selection. The risk it poses is to *training* against it, which is Phase 1.

## What this makes the paper

Taxonomy + mechanism + certification: (1) similarity metrics can't grade, provably and mechanically;
(2) the fix is not a better similarity metric but signals that verify — and the design rule is
*checkable endpoints* (gold answers, tests, trusted references), not gold text; (3) a cheap static
audit tells you which evaluators to trust, and it predicts dynamic robustness. Venue thinking
stays ACL/EMNLP or NeurIPS D&B.

Next: second rater + external annotator on the n=80 (to firm up the prefix-repair claim), code labels,
(pending), Phase 1 DPO gated on writeup.
