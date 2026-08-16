# Metric-class results (derisk wave, 2026-08-16)

Every text-matching metric run through the same pipeline: model-level boundary (rho vs accuracy,
17 models), two-way decomposition (item / item x family / residual; 4 families), item-level grading
(partial vs judge | correct, Qwen ladder), and human anchor (rho vs human soundness, n=60).

| metric | class | boundary (hard / GSM8K) | item% / ixf% / res% | grading partial | vs human soundness |
|---|---|---|---|---|---|
| TFA (argmax) | prediction-fit | +0.60 / -0.25 | 83-92 / 3-7 / 5-11 | ~0 to +0.22 | -0.07 |
| tfa_logprob (gold-token prob) | prediction-fit | +0.43 / -0.23 | 83-91 / 7-11 / 1-6 | -0.07 to +0.32 | -0.17 |
| TF-IDF cosine | content-weighted similarity | +0.72 / +0.12 | (not run) | +0.01 to +0.17 | (not run) |
| unigram-F1 | raw similarity | -0.49 / +0.18 | 45-55 / 12-15 / 32-41 | -0.21 to -0.04 | -0.24 |
| LLM judge | reads content | n/a | n/a | (is the target) | +0.59 |
| rollout PV | endpoint-check | n/a | n/a | +0.43-0.48 | +0.49 |

Three-tier class law (sharper than "all text matching inherits everything"):
1. GRADING: NO text-matching metric grades individual solutions (all within -0.24..+0.17 of zero vs
   human soundness / weak partials), across prediction-fit, content-weighted, and raw similarity.
   Only endpoint-checking (PV) and content-reading (judge) grade.
2. RANKING: prediction-fit and content-weighted similarity rank models on hard benchmarks and die/invert
   on saturated ones (the boundary is a class property of reference-anchored scoring); raw overlap does
   not rank at all (inverted even on hard).
3. MECHANISM: the reference-nuisance structure (dominant item main effect across families) appears in
   both prediction-fit metrics (83-92%) and, attenuated, in raw similarity (~50% + huge generation-noise
   residual). Code (HumanEval) decomposition: 78.3 / 7.7 / 14.1 — mechanism extends beyond math.

GPT-critic calibration vs human (n=60 overlap): soundness rho +0.59, style +0.63, construct
discrimination correct (critic-soundness tracks human-soundness 0.59 > human-style 0.33), lucky 49/60.

## Critic-mandated fixes, second wave (2026-08-16)

Independent critic verdict: no fatal flaws; ranked fixes. Status of each:

- SEV 1.3 (missing embedding class) FIXED: MiniLM embed-cos boundary +0.45/+0.87/+0.29 (ranks like
  prediction-fit on hard), decomposition ~70/8/21, item partials +0.13..+0.21, and vs HUMAN soundness
  +0.14. Tier (i) survives its most dangerous challenger. TF-IDF cells filled: decomp 69/8/23 (M500),
  52/13/35 (GSM8K); vs human +0.01. All five text metrics vs human soundness in [-0.24,+0.14].
- SEV 2.2 (judge = endpoint-checker?) RESOLVED: random within-correct collapse is range restriction
  (judge sd 0.16; 96% of scores = 10). On divergence stratum, within CORRECT-only (n=17), judge vs
   2-rater consensus soundness = +0.81. Content-reading earned. Bonus: on saturated data even judge
  VALIDITY is unmeasurable (no information) - Sanmi's item-design point at the meta level.
- SEV 3.3c (F1 inversion) EXPLAINED: verbosity confound; controlling model output length, -0.49 -> -0.07.
- SEV 2.3 (panel construction): judge-vs-panel numbers retired; panel confined to provisional
  TFA/PV coverage with calibration bands; non-GPT panel reconstitution pending.
- SEV 2.1 (entropy vs saturation deconfound): short-reference TFA job running (same MATH-500 items,
  reference = final answer only; if boundary collapses, complexity is the mechanism).
- Code domain: chat-template regen + test execution chained (first pass had a phi-4 prompt-format bug:
  raw completion prompt -> placeholder output, 4% vs true 89% pass).
- HUMAN ACTIONS (cannot be done by models): finish n=80 as pre-stated; 2nd rater on >=30 random items;
  one external non-author annotator on 20-30; style rubric tightening or disattenuation for the style-null.

## SEV 2.1 deconfound verdict (2026-08-16): complexity, not saturation, is the mechanism

Short-reference TFA (reference = "The final answer is \boxed{X}." on the same MATH-500 items, 17 models):
boundary rho collapses from +0.35 (full worked reference) to +0.02 [-0.53,+0.53]. Same items, same models,
same accuracy distribution; only reference complexity changed. Measurement noise negligible (~5k scored
tokens/model; binomial SE ~0.006 vs between-model sd 0.063). Together with rho(boundary, ref-entropy)=+0.89:
tier (ii) reframed mechanistically - prediction-fit metrics rank models only insofar as predicting the
reference requires solving-adjacent skill; strip the reasoning content from the reference and the ranking
signal disappears. Saturation matters because saturated benchmarks HAVE short, low-entropy references, not
(only) because accuracy is compressed.

## Code domain lands (2026-08-16): the grading null with a perfect oracle

Chat-template regen fixed phi-4 (89% pass, matches original; 88% agreement with original code_pass).
On 492 regenerated HumanEval traces scored by EXECUTING the official tests (free, perfect ground truth):
  TFA vs test_pass = +0.00 point-biserial (within-model: -0.04 / -0.02 / +0.06)
  logprob vs test_pass = -0.01
The grading tier now has a second domain where the oracle is executable and human-free. No judge, no
labels, no circularity. Code labeling artifact (60 traces, 30 pass/30 fail, 20 shared) published for the
style/soundness axes tests cannot measure: e4328ef4-d4cb-463e-b0c5-a8549a134463.
