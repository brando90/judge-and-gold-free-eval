# Paper skeleton: When do LLM judges actually fail? A verification-first anatomy of oversight in verifiable domains

Assembled 2026-08-02/03 from the autonomous run (see oversight-log.md for the full
audit trail; every number below survived an adjudication or robustness pass, and
three seductive pseudo-results were killed on the way).

## One-paragraph abstract (post-critic draft)

Scalable-oversight research typically scores LLM judges against benchmark
oracles and assumes judge reliability degrades as solvers strengthen. We show
both practices mislead in oracle-verifiable domains, and quantify what actually
governs judge reliability. (1) LABEL ARTIFACTS: three apparent oversight effects
(attractor errors that fool judges, capability-gap degradation, and a
weak-judge hierarchy that predicts frontier failure at 94%) each dissolve under
label adjudication, with 71-83% of the driving cases being benchmark label
bugs; a cheap open-model ladder whose unanimous disagreement with the label
flags oracle errors at ~97% precision (n=40) provides an unsupervised repair
instrument, and residual frontier-adjudicated disagreement on genuine errors is
~2%. (2) THE SCALE x REFERENCE INTERACTION: on mechanically verified
coherent-wrong solutions (immune to label noise by construction), providing a
trusted reference converts error detection from a capability-bounded skill into
a small-model commodity: detection gains from the reference are +68 points at
3B, +36 at 7B, +15 at 14B, and +2-5 at the frontier, consistently across math
and code. With-reference judge evaluations therefore overstate small-judge
readiness for reference-free deployment. (3) OUTCOME, NOT PROCESS: frontier
judges forgive non-propagated false steps (40-50% unpenalized) while catching
propagated coherent-wrong essentially always; mid-scale judges penalize salient
corruptions, frontier judges penalize consequential ones -- a local-to-global
strategy shift with scale. Item-matched tests do not support reducing
reference-free verification to the judge's own generation ability, but current
power leaves the verification-generation coupling open. We release the planted,
propagated, and mutation instruments and the adjudicated labels.

## Panels (all data in runs/, scripts in scripts/)

P1 Oracle noise dominates measured unreliability.
   - 3 pseudo-laws killed by adjudication (attractor +6.41 -> 83% scorer bugs;
     capability-gap -> difficulty confound; k-ladder hierarchy 1->94% -> 71%
     label bugs, conditional lift collapses to 6.2% vs 2.0%).
   - Two-family unanimous adjudication 55/55; GSM8K cc bug rate 4.1%; judge
     quality signal understated (0.656 -> 0.753 after conservative cleaning).
   - Instrument: ladder+frontier unanimous disagreement = 97% precision oracle
     bug mining (39/40).
P2 The judge x solver reliability surface (natural errors, cleaned labels).
   - AUC 0.781 / 0.898 / 0.923 / 0.962 / 0.961 / 0.974 / 0.993 (0.5B..14B, GPT,
     Opus); frontier margin is confidence (sep ~8 vs ~5), not coverage; FP>=7
     threshold artifact documented (7B ~ frontier at >=7, 74% vs 10% at >=5).
   - Solver-strength axis weak and non-monotone (14B-solver column peak).
P3 Verification phase change on coherent-wrong (propagated, mechanically
   verified, tell-free; the label-noise-immune instrument).
   - FP>=7 / detection: 95%/5 -> 78%/22 -> 2-5%/88 -> 7-13%/88 -> 2-15%/95 ->
     0-3%/100 -> 0%/100.
   - GV decoupling claim WITHDRAWN per critic (n=6-11 cannot support a null);
     item-matched code coupling mixed (7B 36 vs 46%, 14B 63 vs 33%, CIs overlap).
   - Even GPT-5.2 fails to WRITE coherent-wrong 65% of the time (mechanical
     verifier rejections) -- coherent errors are intrinsically hard to produce.
P4 Strategy phase change on planted typos (position x magnitude).
   - 3B/14B: early_gross detected most (69/72%), late_small least (31/25%) =
     local salience; frontier inverted (late_small 61/68% > early_gross 47/48%)
     = global consequence, typo forgiveness; 0.5B/1.5B floor.
   - Step-level blind spot: 40-50% of explicit false equations unpenalized;
     69-85% pass >=7. Direct relevance to PRM-style process supervision.
P5 Style confound closed: error-free style-matched rewrites score 9.98/10.00
   (= controls), so P3 drops are entirely the planted error.
P6 THE REFERENCE-DEPENDENCE LAW (headline panel).
   - Code (no-reference, oracle = executed HumanEval tests, 85 verified
     coherent-wrong mutants): detection 4/7/19/38/58% (0.5B..14B), frontier
     86/95% (FP 1-2%); AUC 0.51/0.54/0.59/0.71/0.85. Gradual scaling, no early
     phase change.
   - Same math candidates, gold withheld: 3B 85->17% (FP 4->81%), 7B 85->49%,
     14B 90->75%, frontier ~unchanged (98-100%, GPT shallow FP 3->23%).
   - Reference-free curves match across domains (math 6/3/17/49/75 ~ code
     4/7/19/38/58). Reference-assist benefit: +68 (3B), +36 (7B), +15 (14B),
     +2-5 (frontier): REFERENCES FLATTEN THE VERIFICATION CAPABILITY CURVE.
   - Implication: the scarce resource for scalable oversight is trusted
     references/oracles, not judge capability; with-reference benchmarks
     overstate small-judge readiness; reference-free judging is
     capability-bounded and is the true oversight frontier.
   - Beyond Zheng et al. 2023 (reference-guided helps at frontier): the
     scale x reference INTERACTION, its magnitude, cross-domain consistency,
     and label-noise-immune instruments.

## Threats to validity / what a reviewer will say
- GSM8K/MATH only; arithmetic-flavored verification. NEXT: replicate P3 on a
  second verifiable domain (code with hidden tests is the natural one).
- The adjudicator is a frontier model (two families, solve-first binary,
  unanimous); no human labels. Mitigation: mechanical verifier for P3/P4 needs
  no adjudicator at all; P1 uses two independent families + platinum agreement.
- Judge = 0-10 rubric scoring; other protocols (pairwise, binary, debate) may
  shift thresholds (we showed binary lifts Putnam judge-accuracy 0.62 -> 0.91).
- Unsolved bins in GV decoupling are small (n=5-11).
- Single rubric; temperature 0; one run per cell (deterministic-ish).

## What remains for a full paper (ordered)
1. Second domain for P3 (code: planted coherent-wrong patches vs hidden tests).
2. Style/length-matched controls (running) + n boost on GV-decoupling unsolved
   bins (select items weak judges cannot solve, generate propagated errors
   there specifically).
3. Human spot-adjudication of ~50 cases (grounding the two-family unanimity).
4. Formalize the phase-change fit and the local->global strategy metric.
5. Position against: Kenton et al. 2407.04622 (weak judges, protocols), Engels
   et al. 2504.18530 (games matrices), JudgeBench 2410.12784 (judges vs labels
   -- our P1 says their labels matter), MR-GSM8K / BIG-Bench Mistake (step
   error detection), platinum benchmarks (label noise), "Great Models Think
   Alike" 2502.04313 (correlated failures; our F1b quantifies FP correlation
   0.83-0.94 across families AFTER label cleaning).

## Addendum (end of run): panels P7-P9

P7 THE BOOTSTRAP AND ITS FAILURE MODE (F10-F11; supersedes the retracted F8a).
   - Single-prompt solve-first FAILS at 7B (det 28% < no-ref 49%): silent
     instruction non-compliance (dumps show the solve step skipped).
   - Mechanically-staged SELF-REFERENCE (gold := judge's own prior solution):
     det 59/60/85/95% (1.5B-14B) vs goldref 21/85/85/90 vs noref 3/17/49/75.
     SELF > GOLD at 1.5B (style-match). Detection couples to own-solution
     correctness (93 vs 60% at 7B).
   - The mechanism: VERIFICATION = REFERENCE GENERATION (capability-bounded) +
     STYLE-MATCHED COMPARISON (cheap at tiny scale). Explains the P6
     interaction; reconnects to TFA's style-nuisance origin.
P8 CROSS-FAMILY GENERALITY (F9): interaction replicates in phi-4 (99/73/99...),
   Mistral-7B (19/4), OLMo-2-13B (64/4); verification capability is family-,
   not size-indexed. phi-4 code no-ref 59% ~= Qwen-14B 58%.
P9 EXTERNAL TRANSFER, ProcessBench-gsm8k, human-annotated (F12):
   F1 curve 0 / 0 / 37 / 30 / 63 / 88 (0.5B..14B, Opus); solve-first +7-8 F1
   at 7B/14B (fixes the 7B credulity wobble); small-judge degenerate modes
   (position priors, always/never-error). HONEST NULL: the planted-regime
   strategy-shift ordering does not transfer to natural errors.

## Integrity record
One full public retraction cycle inside the run (F8a dispatch bug: solve arm
silently ran the with-ref rubric; caught by code audit + the 128/128
identical-scores tell; corrected experiments produced the stronger F10/F11).
Six intermediate results killed by internal cross-checks. All headline numbers
re-derived from raw files with independent code; mutants re-executed against
official tests; miner validated against Platinum without frontier adjudicators.
