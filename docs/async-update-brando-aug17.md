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

**On your specific suggestion (weight first tokens less than last):** we've run its limiting case.
Answer-only-reference TFA *is* "weight everything but the end at zero" — and it kills the signal
instead of cleaning it (+0.35 → +0.02). That's the falsification: the thing position-weighting
redistributes is reference-complexity nuisance, not soundness. The full sweep (weighting exponent
from uniform → answer-only) is running now; registered prediction: monotone decay to the null.

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

Next: position-weight sweep + answer-swap results (days), human labels n=80 + second rater
(pending), Phase 1 DPO gated on writeup.
