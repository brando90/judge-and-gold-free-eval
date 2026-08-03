# Paper skeleton: When do LLM judges actually fail? A verification-first anatomy of oversight in verifiable domains

Assembled 2026-08-02/03 from the autonomous run (see oversight-log.md for the full
audit trail; every number below survived an adjudication or robustness pass, and
three seductive pseudo-results were killed on the way).

## One-paragraph abstract (draft)

The scalable-oversight literature assumes LLM judges become unreliable as solvers
strengthen, and evaluates judges against benchmark oracles. We show that in
oracle-verifiable math both practices mislead. (1) Measured judge "unreliability"
is dominated by ORACLE NOISE: adjudicating every case where a cheap open-model
ladder unanimously disagrees with the label (two frontier families agreeing
55/55) reveals ~4% label errors in GSM8K-style scoring and reduces frontier
false-positive rates on genuinely wrong solutions to ~2%; three apparent
oversight laws (attractor errors, capability-gap degradation, a weak-to-strong
detection hierarchy) all dissolve once labels are fixed, and ladder+frontier
disagreement mines oracle bugs at ~97% precision with no supervision. (2) The
real structure of judging is a VERIFICATION PHASE CHANGE: on mechanically
verified, internally-consistent wrong solutions (immune to label noise by
construction), detection jumps from 5%/22% (0.5B/1.5B judges) to 88% at 3B and
100% at the frontier; detection is FLAT in whether the judge can solve the item
itself, rejecting the assumption that oversight inherits the generation frontier.
(3) Judging strategy itself changes with scale: mid-size judges penalize locally
salient corruptions (early/gross planted typos) while frontier judges penalize
consequential ones (late/small) and forgive typos, reading coherence rather than
checking lines, which leaves a quantified step-level blind spot (40-50% of
explicit false equations unpenalized; 69-85% pass a deployment-style threshold).
Oversight risk in verifiable domains therefore concentrates not in judge
capability but in oracle quality and step-level leniency; we release the planted
and propagated error instruments and the adjudicated label sets.

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
   - GV decoupling: detection flat in judge's own solve status (86 vs 100%, 88
     vs 89%); small unsolved bins flagged.
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
