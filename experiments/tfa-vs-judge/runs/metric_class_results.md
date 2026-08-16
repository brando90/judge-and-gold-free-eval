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
