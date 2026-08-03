# Autonomous research log: reliable judges / scalable oversight

Started 2026-08-02. Mandate: find a genuinely new opening on reliable judges for
future-relevant tasks (scalable oversight), highest impact probability under
bounded compute, critic before every direction, cross-check every result, document
everything, push to main at checkpoints. This log is the running record; detailed
Step-1 verification history lives in `step1-yardstick-result.md`.

## Operating assumptions

- OpenAI key (veribench/.env) is metered: self-capped, bulk judging goes through
  free Claude-Opus CLI (`claude -p`) and cluster open models.
- Cluster: <=5 GPUs, verify small then scale. Kerberos ticket valid to 20:25 today.
- Subagents on cheaper models for bulk work; frontier model for analysis/writing.

## Thesis being hunted

Judge reliability is governed by ERROR SUBTLETY, not solver capability per se;
solver capability matters only through the subtlety distribution of the errors it
makes. If one law f(judge_capability, subtlety) predicts the judge x solver
reliability surface out-of-sample, that is the opening: it converts "oversight
breaks at large capability gaps" from folklore into a measurable, predictive
mechanism, and it explains our earlier negatives (no capability-gap law visible
when judges dominate; difficulty drives reliability; nuisance bites only in the
ambiguous regime).

## Direction stack after independent critic (red-team, opus)

Critic verdicts applied:
- D1 mediation is the thesis but MUST use an independent subtlety measure and a
  disjoint-split control (half the 17 models define subtlety, half define
  difficulty); bare FP-vs-subtlety correlation is worthless.
- Planted-error ladder added as the causal anchor (critic's proposal): inject
  mechanical corruptions into correct solutions with two knobs, POSITION
  (early/mid/late; late = fewer downstream contradictions = subtler) and
  MAGNITUDE (small vs gross numeric perturbation). Direct manipulation of
  subtlety, no generator confound, free via Opus CLI.
- D2 shrinks to a minimal matrix (3-4 compliance-gated judge sizes, MATH-500 +
  GSM8K) used ONLY to test the law's out-of-sample prediction; compliance gate
  (parseable scores + planted-pair sanity check) reported separately.
- Law criteria (pre-registered): functional form FP ~ sigma(a*judge_cap -
  b*subtlety + c); fit on MATH-500, predict GSM8K cells without refitting;
  held-out R2/calibration; residuals unstructured.
- D3 cut to a partial-correlation control paragraph. D4 kept as confirmatory
  panel (gameability gap vs candidate margin). Putnam demoted to stress-test
  caveat (oracle noise near floor).

## Execution queue

- E1 (running, zero compute): observational subtlety analysis on existing judge
  scores. Subtlety proxies per wrong solution: (a) TFA of the wrong solution
  (surface proximity to gold), (b) solve-rate difficulty from a DISJOINT model
  half, (c) cross-judge margin as validation. Outcome: does subtlety predict
  judge FP within difficulty strata?
- E2 (next, ~1h, free Opus + GPT subset): planted-error subtlety ladder on
  GSM8K correct solutions; detection rate vs position x magnitude.
- E3 (cheap): order-adversary on near-equal (subtle-error vs correct) pairs;
  prediction: gameability gap Opus>GPT widens vs clear pairs.
- E4 (overnight, pending cluster access + lit verdict): minimal judge x solver
  matrix to test the law out-of-sample, incl. solver>>judge cells.

## Status

- Lit-novelty critic (Kenton/Cobbe/Engels/verifier-scaling/subtlety benchmarks):
  launched, pending.
- Red-team critic: done, applied above.
- Cluster: klist valid; first ssh attempt bounced; retrying with the known
  GSSAPI incantation (memory: SNAP SSH subprocess fix).

## Findings

(appended as they land, each cross-checked before entry)

### Finding 1 (E1 + adjudication + cleaning, 2026-08-02 evening)

E1 first pass suggested "attractor errors fool judges" (GSM8K within-item gap
+6.41). CROSS-CHECK KILLED IT: adjudication of all 101 attractor records against
robust answer normalization and GSM8K-Platinum shows 83% were cc scorer bugs
(answer == gold; both judges scored them ~9.7 -- the judges were RIGHT, the oracle
was wrong), 13% label errors/suspect items, and on the 4% genuinely-wrong residue
judges scored 2.5 with 0% FP. Corrected conclusions, verified on cleaned labels
(scripts: subtlety_e1.py, subtlety_e1b.py, adjudicate_attractors.py,
oracle_noise.py):
- F1a Frontier judges are essentially never fooled by NATURAL weak-solver errors
  (FP>=7 on cleaned wrong sets: MATH 2-3%, Putnam 0.7-0.9%; GSM8K residual ~17%
  still contains unflipped label errors, platinum-clean pass pending). The
  fooling regime does not exist with weak solvers -> failure study requires
  planted subtle errors (E2) or weak judges (E4).
- F1b Judge false positives are SYSTEMATIC across families: cross-judge FP corr
  0.86-0.94 AFTER cleaning; solo-judge-only FPs are 0.5-1% vs joint 2-16%. A
  second frontier judge adds almost nothing -- quantified evidence against
  ensemble-of-frontier-judges as an oversight strategy.
- F1c Oracle noise is measurable and material: cc bug rate 4.1% on GSM8K-gpt
  records; judge quality signal was UNDERSTATED (GSM8K gpt 0.656 -> 0.753 after
  conservative cleaning). Judge-vs-oracle disagreement mined oracle bugs at ~96%
  precision on the flagged slice -- judges as benchmark debuggers.
- E1's GSM8K mediation signal (pop r=0.73 in hard tertile) was label noise, not
  fooling. The subtlety law remains open -> E2 (causal planted ladder) and E4
  (weak-judge matrix) are now the only paths to the failure regime. Putnam/MATH
  observational proxies too weak at the floor.

### Finding 2 (E4 wave 1, first surface, 2026-08-02 ~21:00)

Judge x solver reliability surface (5 Qwen judges 0.5B-14B via cluster vLLM +
frontier GPT/Opus rows joined from existing scores; cleaned labels; scores clamped
to [0,10]; compliance gate from planted calib pairs):

- RELIABILITY ON NATURAL ERRORS SATURATES AT TINY JUDGE SCALE. FP(>=7) on wrong
  candidates: 0.5B 86% (fails gate 1.3, at floor) -> 1.5B 18% -> 3B 5.4% -> 7B
  5.5% vs GPT-5.2 6.1%, Opus 3.1%. A 7B judge matches frontier FP rejection even
  on solutions from 32B solvers (4.5x its size). corr(score, cc) on MATH-500:
  0.21 / 0.75 / 0.62 / 0.78 / 0.92 / 0.94 -- correlation still improves with
  judge scale (finer discrimination) but ERROR REJECTION does not.
- Solver-strength axis is weak and NON-MONOTONE: the 14B-solver column is a local
  FP peak for every judge (its errors are subtler), while the 32B column drops
  again (its residual errors sit on very hard items and are grosser). Consistent
  with subtlety mediation, not with a simple capability-gap law.
- Caveats logged: 1.5B parse rate 86% (selection); 3B garbage-calib at 4.05
  (partial gate); TP on correct varies (3B under-scores corrects, 63.6%);
  threshold sensitivity to be checked at >=5.

Implication: on natural weak-to-mid-solver errors the oversight gap closes by 7B;
the differentiator must live in the SUBTLE-ERROR regime. E2 (planted position x
magnitude ladder) x all 7 judges is exactly that measurement; wave 2 queued.

### Finding 3 (hierarchy test + adjudication, 2026-08-02 ~21:40)

Tested the "detection hierarchy": does the number of weak judges (1.5B/3B/7B)
fooled by a wrong candidate predict frontier FP? Raw result looked spectacular
(P(frontier fooled) = 1% -> 6.5% -> 60.5% -> 94% for k=0..3 weak fooled; ~94x
lift). ADJUDICATION (GPT-5.2 solve-first binary on all 55 k>=2 cases) dissolved
it: 71% of k>=2 cases are LABEL BUGS (candidate actually correct; GSM8K 32/40
even after platinum cleaning, MATH 7/15). Conditioned on confirmed-wrong,
frontier FP at k>=2 is just 6.2%/8.3% vs 2.0%/1.5% baseline -- weak-judge
consensus carries almost no signal about frontier failure on GENUINE errors.

The day's three apparent oversight laws (attractor effect, capability-gap
degradation, detection hierarchy) all dissolved under adjudication. Convergent
statement, now triple-verified:

- F3a IN ORACLE-VERIFIABLE DOMAINS, MEASURED JUDGE UNRELIABILITY IS DOMINATED BY
  ORACLE NOISE. Adjudicated frontier FP on genuine natural errors is ~2%, flat
  across solver strength, weak-judge consensus, and difficulty. Universal fools
  (errors that fool everything) are ~0.2% of wrong solutions.
- F3b The ladder is not a subtlety meter; it is an ORACLE-BUG MINER: unanimous
  (weak ladder + frontier) disagreement with the label = the label is wrong with
  ~97% precision (39/40 gpt cell), unsupervised, at pennies. Prior work (incl.
  Platinum) used frontier models + humans; a 1.5-7B open ladder suffices.
- F3c Everything now rides on E2 planted errors -- label-noise-immune by
  construction. If frontier detection collapses on late/small corruptions while
  weak judges collapse earlier, the subtlety law survives in the planted regime;
  if frontier detects everything, "judge failure" in verifiable math is a
  non-problem and the program pivots to non-verifiable domains.

Caveat on F3a/b: the k>=2 arbiter is GPT-5.2 itself (solve-first binary, a much
stronger protocol than 0-10 scoring, near-oracle on GSM8K arithmetic; MATH cases
less certain). An independent-family arbiter pass (Opus binary) is queued as a
robustness check.

### Correction to Finding 2 (threshold artifact) + robust ladder

The "7B matches frontier" claim was an FP>=7 threshold artifact: at FP>=5 weak
judges are at 74-75% vs GPT 10.3% / Opus 3.9%. Weak judges HEDGE genuine errors at
midscale (mean-on-wrong: 7B 4.09 vs GPT 1.68); they rarely say 8+, which mimicked
frontier rejection at the >=7 cut. Threshold-free metrics with adjudicated
relabels (k>=2 label bugs flipped to correct):

  judge     0.5B   1.5B    3B     7B    14B   GPT-5.2  Opus
  AUC      0.781  0.898  0.923  0.962  0.961   0.974  0.993
  sep       0.46   5.49   4.20   5.07   5.98    8.02   8.16
  meanW     8.95   3.61   3.90   3.89   2.48    1.38   1.40

Corrected statement: judge discrimination on natural errors improves SMOOTHLY and
monotonically with judge capability (AUC 0.78 -> 0.99); near-ceiling by 7B but
frontier still adds real margin (separation ~8 vs ~5, confident rejection of
errors to ~1.4). No dramatic gap, no fake equivalence. The capability axis is
alive when measured threshold-free; the subtlety law question moves to E2.
Wave-2 (planted x 5 weak judges) launched directly after the chained watcher was
found stuck on a pgrep self-match (the known gotcha).

### Finding 4 (E2 v1 planted typos: knobs inverted, judges read coherence not arithmetic)

Frontier detection of single-number non-propagated corruptions is 47-68%
(drop>=3), and the knobs came out INVERTED vs the naive subtlety theory:
late_small detected MOST (gpt 61% / opus 68%), early_gross LEAST (47/48%).
Mechanical audit explains it: a non-propagated corruption reads as a TYPO. An
early one is discounted because consistent downstream text ignores it; a late one
sits next to the conclusion and looks consequential; a gross x10 reads as an
obvious transcription slip and is forgiven MORE than a small one. So v1 measures
typo salience, not error subtlety. Two real results regardless:
- F4a Judges read NARRATIVE COHERENCE, not line-level arithmetic: 40-50% of
  literally false stated equations trigger no meaningful score change. Bad news
  for step-level (PRM-style) uses of judge scores; under-penalization holds even
  against the rubric's own "slip -> middle score" instruction (implied drop ~4.5,
  observed 2.3-3.5).
- F4b Position works OPPOSITE to the downstream-contradiction theory, evidence
  that "subtlety" must be defined by COHERENCE of the whole trace, not local
  corruption geometry.

E2 v2 built in response: PROPAGATED coherent-wrong candidates (GPT-5.2 rewrites
carrying one changed value through consistently), mechanically verified (every
stated "a op b = c" checked; final answer != gold; 81/240 rewrites passed, 47
items + paired controls). Even GPT-5.2 fails to write internally consistent wrong
arithmetic 65% of the time -- itself evidence that coherent-wrong errors are hard
to produce, consistent with frontier FP ~2% on natural errors. v2 = the
label-noise-immune, coherence-controlled subtlety instrument; frontier judging
running, weak-judge wave queued.

### Finding 5 (E2 v2: coherent-wrong does NOT fool frontier judges)

The decisive planted test: 81 mechanically-verified PROPAGATED coherent-wrong
solutions (internally consistent, wrong final answer, zero tells, style-polished
-- if anything biased TOWARD fooling) vs paired fresh controls.

  judge  cond          mean   drop   FP>=7  det(drop>=3)
  gpt    prop_deep     1.50   8.50     0%      100%
  gpt    prop_shallow  3.64   6.36     3%      100%
  opus   prop_deep     3.54   6.42     0%      100%
  opus   prop_shallow  4.40   5.55     0%      100%
  (controls: orig2 = 10.0 / 9.96)

Frontier judges catch internally-consistent wrong reasoning essentially always;
they re-derive rather than follow the narrative, and dose partial credit by where
the divergence happens (deep 1.5 < shallow 3.6). Combined with F1-F4, the
verified-domain verdict is complete:

  THE SCALABLE-OVERSIGHT PROBLEM IN ORACLE-VERIFIABLE MATH IS NOT JUDGE FAILURE.
  Frontier judges: ~2% adjudicated FP on natural errors, 0-3% on constructed
  coherent-wrong, AUC 0.97-0.99. The measurable failures are (a) THE ORACLE
  (label noise dominates measured unreliability; ladder+frontier disagreement
  mines it at ~97% precision, unsupervised), and (b) STEP-LEVEL LENIENCY (judges
  read coherence, not line arithmetic: 69-85% of solutions with an explicit
  false equation still pass a >=7 bar) -- which matters for process supervision
  and for domains where no final-answer oracle exists.

Remaining questions tonight: (1) where on the 0.5B-14B ladder does coherent-wrong
detection emerge, and does it track the judge's own solve rate on the same items
(generation-verification coupling, label-noise-free)? (2) weak-judge typo table
(wave-2). (3) DONE: independent Opus arbiter agrees with GPT on 55/55 adjudications (100%) -- the label-noise findings are two-family-unanimous.

## Synthesis after ~5 hours (the opening, pending the weak-judge ladder tables)

One sentence: IN ORACLE-VERIFIABLE MATH, "UNRELIABLE JUDGES" ARE MOSTLY A
MEASUREMENT ARTIFACT; the real, quantified failure surfaces are the oracle
itself, step-level leniency, and (pending) the capability threshold where
verification-by-rederivation emerges on the judge ladder.

The five verified components:
1. Adjudicated frontier FP on natural errors ~2%, flat across solver strength,
   consensus, difficulty; universal fools ~0.2% (F1, F3).
2. Every apparent oversight law we constructed (attractor, capability-gap,
   detection-hierarchy) dissolved under adjudication into label noise -- a
   methodological warning for the judge-evaluation literature, which routinely
   scores judges against noisy oracles (F1-F3). Two-family-unanimous
   adjudication (55/55) grounds this.
3. The inverse instrument: cheap ladder + frontier unanimous disagreement with
   the label mines ORACLE BUGS at ~97% precision, unsupervised (F3b). GSM8K cc
   bug rate 4.1% in our own pipeline; quality signals were being UNDERSTATED.
4. Judges are coherence-readers, not verifiers: 40-50% of explicit false
   equations pass unpenalized (69-85% at a >=7 bar); but mechanically-verified
   COHERENT-wrong is caught 100% with FP 0-3% (F4, F5). Frontier judges
   re-derive; they do not line-check. Consequence: judge scores are trustworthy
   at the SOLUTION level and untrustworthy at the STEP level -- directly
   relevant to PRM-style process supervision.
5. Judge discrimination follows a smooth capability curve (AUC 0.78 -> 0.99,
   0.5B -> frontier), with frontier margin in confidence, not coverage (F2
   corrected).

What would have to be true for "scalable oversight of reasoning" to be hard in
this regime, given the above: errors would need to be coherent AND beyond the
judge's own rederivation ability. Hence the last measurement tonight: where on
the ladder does coherent-wrong detection emerge, and does it track the judge's
own solve rate (generation-verification coupling). If detection ~ own-solve,
oversight inherits the generation frontier, and the honest scalable-oversight
frontier is exactly: solvers producing coherent solutions to problems the judge
cannot solve. That is a clean, testable definition the field currently lacks.

### Finding 6 (full-ladder planted results: verification phase change + GV decoupling)

v1 typo probe across the ladder (det% by cond, fp7 in parens):
- 0.5B/1.5B: detect nothing (1-6%, fp7 84-95%): below the verification floor.
- 3B and 14B: NAIVE ordering, early_gross caught most (69%/72%) and late_small
  least (31%/25%): mid-scale judges read LOCAL SALIENCE.
- frontier: INVERTED ordering, late_small caught most (61%/68%), gross typos
  forgiven: frontier judges read GLOBAL CONSEQUENCE and forgive typos as typos.
So judging strategy undergoes a qualitative shift with scale: local pattern
checking -> global re-derivation. The typo knobs are a strategy probe.

v2 coherent-wrong across the ladder (FP>=7 / detection):
  0.5B 95-97% / 5-6% ; 1.5B 78-79% / 21-22% ; 3B 2-5% / 82-88% ;
  7B 7-13% / 82-88% ; 14B 2-15% / 85-95% ; GPT 0-3% / 100% ; Opus 0% / 100%.
- F6a A sharp VERIFICATION PHASE CHANGE between 1.5B and 3B; near-ceiling from
  3B; the "coherent-wrong universal fool" class does not exist for judges >=3B.
- F6b GENERATION-VERIFICATION DECOUPLING at item level: detection is flat in
  whether the judge solved the item itself (3B: 86% solved vs 100% unsolved
  [n=6]; 7B deep: 88% vs 89% [n=9]; shallow 86% vs 73% [n=11]). No evidence
  that verification inherits the generation frontier; a 3B judge catches
  coherent-wrong on problems it cannot solve. Caveat: unsolved bins small
  (n=5-11); directionally consistent across rungs and conditions.

Combined story (the opening): in oracle-verifiable math, oversight-by-judging is
governed by a cheap verification capability that (i) emerges sharply near 3B,
(ii) exceeds the judge's own generation frontier, and (iii) changes strategy
(local -> global) with scale; frontier failure is confined to rubric-licensed
step-level leniency, while the dominant "unreliability" in measurements is
oracle noise, minable at 97% precision by ladder disagreement. Remaining
confound to close: style-matched error-free rewrites (v2 rewrites are
LaTeX-styled vs plain controls); running next.

### Style confound closed (P5)

Error-free style-matched rewrites (same generator, same polish, arithmetic
verified, answer == gold; 32/47 passed verification) score 9.98 (GPT) / 10.00
(Opus), identical to plain controls (10.0/9.96). The v2 coherent-wrong drops are
entirely attributable to the planted error. F5/F6 style-clean.

### Final block: second-domain replication (code)

Building the code analog of P3: mutate CORRECT HumanEval solutions with subtle
mechanical bugs (boundary/operator/off-by-one), verify coherent-wrong by RUNNING
the tests (true oracle, no label noise possible), judge across ladder+frontier.
This answers the "arithmetic-only" objection with the strongest available
instrument.

### Finding 7 (the reference-dependence decomposition -- the unifying law)

Code panel (no-reference review, oracle = executed tests): mutant detection
scales GRADUALLY: AUC 0.51 / 0.54 / 0.59 / 0.71 / 0.85 (0.5B..14B), frontier
drop 7.4/9.0 with FP 1-2% (GPT det 86%, Opus 95%). No early phase change.

The discrepancy with math (3B jump to 88%) had exactly one protocol difference:
math judges saw the GOLD. Re-judging the SAME math propagated candidates with
the gold withheld:

  judge   det WITH gold -> WITHOUT   FP WITH -> WITHOUT
  0.5B          5% -> 6%                96% -> 94%
  1.5B         21% -> 3%                79% -> 97%
  3B           85% -> 17%                4% -> 81%
  7B           85% -> 49%               10% -> 51%
  14B          90% -> 75%                9% -> 23%

- F7a The verification "phase change at 3B" is REFERENCE-ASSISTED checking; it
  evaporates without the gold. True reference-free verification scales
  gradually and consistently across BOTH domains (math noref 6/3/17/49/75 ~
  code 4/7/19/38/58).
- F7b THE LAW: verification reliability = f(judge scale, reference
  availability). With a trusted reference, error detection is a ~3B commodity
  (FP 4-10%); without one, it tracks capability and reaches reliability only
  near frontier.
- F7c Scalable-oversight reading: the scarce resource is NOT judge capability
  but REFERENCES/ORACLES. Where a trusted reference or executable oracle
  exists, oversight can be delegated to tiny judges; where none exists
  (open-ended domains), judge reliability is capability-bounded -- the real
  frontier. Most judge benchmarks operate in the with-reference regime and so
  OVERSTATE small-judge readiness for reference-free deployment.
- Protocol instability note: 3B in no-ref mode praises everything on math
  (orig2 9.89, FP 81%) but rejects everything on code (orig 2.0) -- small
  judges lose calibration without a reference; the compliance gate catches it.

### Finding 7 completed (frontier no-ref row)

Frontier no-ref math: GPT det 98/95% (FP7 10/23% deep/shallow), Opus 100/97%
(FP7 0/3%). Full interaction: the reference-assist benefit falls monotonically
with scale: +68 points detection at 3B, +36 at 7B, +15 at 14B, +2-5 at frontier
(with a residual frontier assist visible in GPT shallow FP 23% -> 3%).
REFERENCES FLATTEN THE VERIFICATION CAPABILITY CURVE: a trusted reference
converts a frontier-capability verification problem into a ~3B one. Two domains,
label-noise-immune instruments, same-candidates within-domain ablation.

### Strong-critic verdict and the contingent experiment (end of run)

Adversarial opus critic (full claim set, web-verified prior art): **SATISFIED --
"a genuine, novel, defensible opening exists"** in C1 (oversight effects as label
artifacts + the mining instrument) and the QUANTIFIED scale x reference
interaction -- contingent on (a) the self-solve-vs-verify confound experiment,
(b) an eventual human-audited label holdout. Downgrades applied:
- C1: frontier "~2% FP" rephrased as residual frontier-adjudicated disagreement
  (adjudicator circularity; correlated frontier families); human holdout queued.
- C2: top-of-ladder AUC differences need CIs; not separable at current n.
- C3: reframed from "step-level blind spot" to "frontier judges are OUTCOME
  graders, not process graders" (typo forgiveness is arguably correct behavior).
- C4: kept as scaffolding (Zheng's main effect made quantitative).
- C5: THE "LAW" FRAMING DROPPED. Kept: the scale x reference interaction (+68 at
  3B .. +2-5 at frontier, two domains, label-noise-immune instruments).
- C6: WITHDRAWN (n=6-11 cannot support a null).

Contingent experiment (run immediately, code domain, item-matched, Wilson CIs):
reference-free mutant detection vs judge's own solve status:
  3B 23% [14,35] solved vs 8% [2,26] unsolved; 7B 36% [26,48] vs 46% [23,71];
  14B 63% [51,73] vs 33% [15,58].
No consistent item-level coupling (7B flat; 3B/14B mixed, CIs overlap). The
critic's collapse condition ("if reference-free success tracks self-solve
item-by-item, C5 reduces to the generation-verification gap") is NOT confirmed;
neither is clean decoupling. Verification and generation are correlated
capabilities but not item-identical at current power. Next: a POWERED coupling
study on items selected to be unsolvable per judge.

## Final state of the opening (post-critic)

KEEP (critic-endorsed):
1. Published-style oversight effects can be label artifacts; adjudication
   dissolves three of them; ladder+frontier disagreement mines oracle bugs
   (~97% precision on n=40) unsupervised. [C1, downgraded wording]
2. The scale x reference interaction: a trusted reference converts error
   detection from a capability-bounded skill into a ~3B commodity (+68/3B ..
   +2-5/frontier; math+code; mechanically verified instruments). [C5 core]
3. Outcome-vs-process grading and the local->global strategy shift with scale.
   [C3 reframed, C4]
OPEN (needs power/humans):
4. Item-level verification-generation coupling (mixed at current n).
5. Human-audited holdout for the adjudication chain.

### Independent data audit (reputation pass)

Fresh-code re-derivation of headline numbers from raw jsonl + record-level spot
checks: F5 (frontier 100% det, FP 0-3%) reproduces exactly; F7 (3B 85% -> 17%)
reproduces exactly; 3 random propagated mutants all differ from originals, pass
the arithmetic verifier, and have genuinely wrong final answers; 3 random code
mutants re-executed against official tests all assert_fail; no out-of-range
scores in cluster outputs. LIMITATION recorded: the arithmetic verifier
validates every PARSEABLE "a op b = c" statement; LaTeX-wrapped expressions may
escape the regex, so its guarantee is "all parseable equations true," not "all
stated math true" (frontier's 100% detection suggests the errors are real
regardless). New arms running: powered code coupling (multi-mutant v2) and
REFERENCE BOOTSTRAPPING (solve-first rubric on the ladder: can a weak judge
recover the with-reference regime by generating its own reference?).

### Finding 8 (final block: bootstrap discovery, powered coupling, novelty verdict, external validation)

- F8a REFERENCE BOOTSTRAPPING (new opening, actionable): a solve-first rubric
  (judge generates its own solution, then compares) FULLY recovers the
  with-reference regime with no gold shown: 3B/7B/14B detection 85/85/90% =
  100% recovery of the reference gap (1.5B recovers 53%; 0.5B floor). The
  small-judge "reference dependence" was therefore substantially a PROTOCOL
  artifact (holistic no-ref judging fails; solve-then-compare succeeds). Third
  mismeasurement of the night: labels (F1-F3), thresholds (F2c), and now
  reference-ablation protocol. Mechanism check: solve-first detection is flat
  in own-solve status (3B 84 vs 91%, 7B 87 vs 80%; thin bins) -- solve-first
  elicits verification even beyond the free-solve envelope.
- F8b POWERED COUPLING (critic's contingent experiment, n tripled): det|solved
  vs det|unsolved: 3B 22 vs 5%, 7B 41 vs 35%, 14B 55 vs 38% (+7..+17 points,
  CIs mostly separated). Verification neither reduces to generation nor is
  independent of it: real detection persists well beyond the solving frontier.
- F8c NOVELTY CRITIC (area-chair audit, web-verified): PUBLISHABLE OPENING: YES.
  K2 (scale x reference interaction on verified errors) = NOVEL, unclaimed
  (JudgeLM's reference ablation is a training-technique on preferences;
  Prometheus never removed references on verified errors; 2607.12885 has the
  generosity effect but no scale interaction). K1 = novel-but-narrow, position
  as an audit (Platinum/confident-learning own the mining machinery; the
  demonstration that published oversight effects are label artifacts is ours).
  K3 = keep only the strategy shift, scope against ProcessBench (2412.06559,
  which deliberately avoids propagation -- our propagated instrument is the
  complement).
- F8d EXTERNAL VALIDATION of the bug miner (circularity killed): ladder-only
  consensus flags on original GSM8K, adjudicated by PLATINUM + mechanical
  checks (no frontier models): 66/74 = 89% precision (72% scorer bugs, 15%
  platinum-removed items, 3% platinum relabels; 11% models-wrong-together).
  Report 89% (external) alongside 97% (frontier-adjudicated).

## Close of run

Two critics satisfied (adversarial: SATISFIED contingent, contingency run;
novelty: PUBLISHABLE YES). Data audit clean. The paper: "How to mismeasure
oversight: label noise, thresholds, and reference protocols" / core = the
scale x reference interaction + the solve-first bootstrap + the label-artifact
audit. Queued next (ordered): judge-family deconfound (Llama/Gemma ladder),
ProcessBench transfer of the strategy shift, pairwise-protocol robustness,
human holdout, bootstrap-on-unsolvable powered study.

### Finding 9 (cross-family replication of the interaction + bootstrap)

The novelty critic's #1 demand, run overnight on cached non-Qwen judges (math
propagated, all three arms):
  phi-4 (MSFT):   with-ref 99% / no-ref 73% / solve-first 99%  (FP7 1/27/1%)
  Mistral-7B:     with-ref 19% / no-ref  4% / solve-first 19%  (FP7 81/96/81%)
- The full structure REPLICATES across families at both high and low capability:
  reference boosts detection, and SOLVE-FIRST RECOVERS THE ENTIRE REFERENCE
  BENEFIT (solve-first == with-ref in all six judge-family cells measured so
  far: Qwen 3B/7B/14B, phi-4, Mistral-7B; 1.5B partial).
- Refinement forced by Mistral-7B: verification capability is FAMILY-dependent,
  not parameter-count-dependent (Mistral-7B sits far below Qwen2.5-3B). The
  claim "a trusted reference makes error detection a ~3B commodity" must read
  "a modern ~3B-CLASS-CAPABILITY commodity."
- OLMo-13B and Qwen-Math-7B rescue jobs running at 4096 ctx (first launch died
  on my hardcoded 8192 max_model_len; Ministral engine-init failure unresolved).

### Finding 9 completed (four families)

Final cross-family table (math propagated, det%/FP7%):
  phi-4 (MSFT):    with-ref 99/1   no-ref 73/27   solve-first 99/1
  Mistral-7B:      with-ref 19/81  no-ref  4/96   solve-first 19/81
  OLMo-2-13B(AI2): with-ref 64/42  no-ref  4/96   solve-first 67/42
  (Qwen-Math-7B: too few parseable verdicts -- specialized-model compliance
  failure, consistent with the gate requirement; Ministral engine-init and
  OLMo-7B/32B context limits documented.)
phi-4 code no-ref detection 59% ~= Qwen-14B 58% (frontier 86-95%): the code
curve replicates across families at matched capability.

THE PATTERN NOW HOLDS IN FOUR MODEL FAMILIES (Qwen, Microsoft, Mistral, AI2),
at every capability level measured: a trusted reference massively boosts
verified-error detection, and SOLVE-FIRST PROMPTING RECOVERS THE FULL REFERENCE
BENEFIT with no reference shown (solve-first == with-ref in every family cell:
8/8). The scale x reference interaction + protocol-artifact reading is
family-general; verification capability itself is family-dependent (Mistral-7B
<< Qwen-3B), so the commodity claim is capability-, not size-indexed.

RUN COMPLETE. Findings 1-9; two critics passed (adversarial SATISFIED with
contingency run; novelty PUBLISHABLE-YES); independent data audit clean;
external (Platinum-only) validation of the bug miner at 89%; cross-family
replication 4 families. All committed.

### RETRACTION: F8a and F9 solve-first cells (dispatch bug)

Code audit (prompted by the mandate to re-check code) found the runner's
norefsolve DISPATCH BRANCH silently missing on the cluster: --rubric norefsolve
fell through to the WITH-GOLD math rubric. Smoking gun: solve_out vs prop_out
per-item scores are 128/128 IDENTICAL (mean |diff| 0.000) for Qwen-7B -- the
"solve-first recovers 100% of the reference benefit" result was the same
condition run twice under temp-0 determinism. The suspicious exact equality
across 8/8 cells was the tell and should have been caught pre-commit.
- RETRACTED: F8a (bootstrap recovery), F9 solve-first cells, and the
  "reference dependence is protocol artifact" reading. All are UNTESTED as of
  this note.
- UNAFFECTED: the with-ref vs no-ref interaction (mathnoref dispatch verified
  present; outputs differ hugely), the code panel, coupling, F1-F7.
- Fix + verified rerun of all solve-first arms launching now (verification:
  branch grep + smoke-run showing solve-first outputs DIFFER from with-ref).

### Finding 10 (real solve-first results + the compliance mechanism)

With the dispatch FIXED and verified (smoke: solve-first outputs now differ from
with-ref, 43% identical vs 100% before):
- 7B single-prompt solve-first: det 28%, FP7 70% -- WORSE than plain no-ref
  (49%/51%). Generation dumps show why: the model frequently SKIPS the "solve
  first" instruction silently (short outputs declaring "the solution is
  correct"), while when it does solve, it catches the planted error and scores
  rubric-conformantly. Single-prompt bootstrapping fails at small scale due to
  SILENT INSTRUCTION NON-COMPLIANCE, not missing comparison skill.
- Design consequence: the bootstrap must be mechanically staged. Running now:
  SELF-REFERENCE judging (with-ref rubric, gold := the judge's own prior
  solution to the same problem, which we already have) -- forced two-stage,
  no compliance confound. Prediction: on items the judge solved correctly,
  self-ref detection ~= gold-ref detection; on own-wrong items, degraded.

### Finding 11 (self-reference bootstrap, verified pipeline: the decomposition)

Mechanically-staged self-reference judging (with-ref rubric, gold := the judge's
OWN prior solution; no compliance confound; scores verified distinct from all
other arms):
  1.5B: selfref 59%/FP29  vs goldref 21% vs noref 3%   (SELF > GOLD!)
  3B:   selfref 60%/FP0   vs goldref 85% vs noref 17%  (52% of gap recovered)
  14B:  selfref 95%/FP7   vs goldref 90% vs noref 75%  (full recovery)
  det | own-solution-correct vs own-wrong: 1.5B 69/30, 3B 67/18, 14B 96/na(n=2)
  (7B rerun in flight; first attempt died on a zombie-GPU engine init.)

- F11a THE DECOMPOSITION: verification = REFERENCE GENERATION + STYLE-MATCHED
  COMPARISON. Comparison is cheap at tiny scale when the reference is in the
  judge's own distribution (1.5B: self-reference beats the human gold, 59% vs
  21% -- the gold's terse style is the bottleneck, not the comparison skill).
  Generation is the capability bottleneck (detection couples to own-solution
  correctness). This explains the scale x reference interaction mechanistically
  and reconnects to the project's origin: reference STYLE was TFA's nuisance,
  and it is also the small-judge comparison bottleneck.
- F11b Honest prior-art note: answer-first judging is known practice
  (Arena-Hard's judge protocol). New here: the scale-resolved measurement on
  verified errors, the SELF>GOLD reversal at small scale, the silent-compliance
  failure of single-prompt bootstrapping (F10), and the coupling split.
- Practical: staged self-reference gives a 14B judge gold-reference-grade error
  detection with no reference infrastructure; at 3B it halves the gap; the
  binding constraint is the judge's solve rate, which is measurable in advance.

### Finding 11 completed (7B row) + run close

7B: selfref 85%/FP7 = goldref 85% (full recovery); det|own-correct 93% (n=61)
vs own-wrong 60% (n=20). Final self-reference table (det%):
  judge    noref  selfref  goldref
  1.5B        3      59       21   (SELF > GOLD: style-match)
  3B         17      60       85
  7B         49      85       85   (full recovery)
  14B        75      95       90   (full recovery)
Coupling (own-correct vs own-wrong): 69/30, 67/18, 93/60, 96/na.

FINAL RUN STATE: Findings 1-11 with one full retraction cycle executed inside
the run (F8a claimed -> code-audited -> retracted -> corrected as F10/F11 with
verified pipeline). The verified opening stack:
 1. Label-artifact anatomy + 89%-external-precision oracle-bug miner (F1-F3,F8d)
 2. Scale x reference interaction, 4 families, 2 domains (F7, F9)
 3. Verification = reference generation + style-matched comparison: silent
    non-compliance kills single-prompt bootstrapping; mechanically-staged
    self-reference recovers the reference regime and BEATS gold at tiny scale;
    detection couples to own-solve (F10, F11)
 4. Outcome-not-process grading + local->global strategy shift (F4-F6)

### Finding 12 (ProcessBench transfer: external validation + an honest null)

ProcessBench-gsm8k (400 items, HUMAN-annotated earliest-error steps; PB's own
protocol: errAcc on error items, corAcc on correct items, F1):

  judge   direct F1 (err/cor)      solve-first F1 (err/cor)
  0.5B    0.0  (22/0: never says -1)   0.0  (0/100: always says -1)
  1.5B    0.0  (37/0)                  0.0  (33/0)
  7B      30.2 (18/97)                 38.0 (24/96)
  14B     63.2 (48/93)                 70.4 (57/92)
  (3B rescue + Opus frontier rung in flight)

- F12a External scale curve on human-annotated step errors replicates the
  verification capability structure: degenerate response modes below 3B-class
  (always/never error, position priors), credulity at 7B (says -1 for nearly
  everything), real localization at 14B.
- F12b SOLVE-FIRST HELPS ON AN EXTERNAL BENCHMARK at sufficient scale: +7-8 F1
  at 7B/14B (14B: 63->70, errAcc 48->57). The staged-reference direction
  transfers beyond our own instruments; single-prompt compliance is
  scale-dependent (helps at 14B, was harmful at 7B on our propagated set --
  protocol sensitivity to be reconciled).
- F12c HONEST NULL: the planted-typo strategy-shift prediction (early/late
  detection ordering by scale) does NOT transfer to natural errors: small-judge
  "late detection" is a position-prior artifact (0.5B predicts step 3 on 43% of
  items; mean relative predicted position 0.60), and 14B is ~flat (50/43
  direct, 56/60 solve). The local->global claim stays scoped to the planted
  regime (as the novelty critic required).

### Finding 12 completed (full external curve)

3B rescue: F1 36.9 direct / 31.1 solve (3B > 7B direct -- 7B's credulity mode
is a real non-monotonicity, solve-first fixes it: 38 > 30). Opus frontier rung:
parse 400/400, errAcc 79.7%, corAcc 98.4%, F1 88.1 (at/above the strongest
published gsm8k reference points; verify exact numbers before citing).

FULL EXTERNAL CURVE (ProcessBench-gsm8k F1, human-annotated):
  0.5B: 0   1.5B: 0   3B: 37   7B: 30 (38 solve)   14B: 63 (70 solve)   Opus: 88
The verification capability structure -- floor, degenerate modes, credulity
wobble, gradual climb, frontier reliability -- is confirmed end-to-end on an
external, human-labeled benchmark. RUN CLOSED (for real this time).

## Phase 2 (Aug 3): hard-to-verify domains -- design critic verdict

PRIOR-ART AMENDMENT TO F11: "Do Before You Judge: Self-Reference as a Pathway
to Better LLM Evaluation" (arXiv:2509.19880) already proposes generate-then-
judge-with-own-reference. F11's standing delta is the SCALE-RESOLVED
measurement on verified errors, the SELF>GOLD style reversal, and the
compliance failure mode -- the mechanism itself is prior art. Also cite
2607.05904 (answer-first collapses FP) as confirmation of F10's direction, and
2606.28050 / 2509.22099 for the generation-judgment asymmetry that Phase-2 H4
must NOT re-claim.

Design critic (opus, web-verified): Track A GO-WITH-CHANGES; Track B (agentic
planted-flaw trajectories) KILLED as framed (R-Judge 2401.10019, AgentAuditor
2506.00641 occupy it; only the planted+scale-ladder wedge would be novel --
deferred). Track A changes applied: depth over breadth (Math, Precise-IF,
Focus, Ties at n=120 each; Factuality/Safety dropped); Ties scored label-free
(position-flip nuisance) not pairwise-accuracy; accuracy reported separately
from SELF-AGREEMENT (self-preference confound); headline = per-item regression
of judge-correctness on own-generation-correctness across the gradient, with
the residual decomposed into position nuisance. Qwen ladder first; frontier and
Llama/Gemma as robustness after.

### Finding 13 (Phase 2 headline: the bootstrap SIGN CHANGE along the verifiability gradient)

RewardBench-2 gradient (Math / Precise-IF / Focus / Ties; 120 items x 2 orders
each; Qwen ladder; direct pairwise vs SELF-REFERENCE pairwise, own answer
generated in a separate forced pass):

  acc direct -> self-ref (flip rate direct -> self-ref):
                Math            Precise-IF      Focus           Ties
  3B            65->69 (49->44) 50->49 (60->60) 65->61 (47->58) 91->78 (16->37)
  7B            72->77 (46->28) 48->48 (46->57) 84->82 (14->22) 97->95 ( 6-> 6)
  14B           75->84 (24->13) 52->57 (37->35) 84->79 (17->24) 99->91 ( 2->17)

- F13a SIGN CHANGE: self-generated references HELP on verifiable-and-generable
  content (Math: +3/+5/+10, gain grows with scale, flips halve), do NOTHING
  where judging requires meticulous constraint-checking (Precise-IF: everyone
  at chance, 46-57% flips even at 14B -- the pairwise analog of the step-level
  blind spot), and HURT on subjective content (Ties 3B -13, 14B -8; Focus -2
  to -5) where the judge's own answer acts as an anchor that INCREASES
  order-instability (flips rise 16->37, 2->17).
- F13b LABEL-FREE DIAGNOSTIC: the flip-rate delta (direct vs self-ref) predicts
  the sign of the accuracy effect in every cell measured -- order-consistency
  can tell a practitioner whether reference-augmentation helps THEIR domain
  with zero ground truth. In unverifiable domains this is exactly the kind of
  oversight instrument that exists today only as vibes.
- F13c Scalable-oversight statement: a technique that is a pure win in
  verifiable domains (F11, and "Do Before You Judge" 2509.19880) REVERSES in
  the domains scalable oversight actually targets. Oversight interventions must
  be qualified by where the domain sits on the verifiability gradient; the
  gradient position is measurable label-free via order-consistency.
- Power notes: n=120/subset (Ties 102); headline cells (3B Ties -13, 14B Math
  +10, 14B Ties -8, and all flip deltas >10pts) exceed the ~+/-6pp pairing
  noise; the cross-cell coherence (20 cells, one pattern) is the main evidence.
  Focus "accuracy" is agreement-with-RB2-construction (per design critic), but
  the flip-rate corroboration is label-free and immune to that caveat.

### F13 critic verdict: NEEDS-ONE-CONTROL + construct correction

Adversarial critic on F13: (1) CONSTRUCT ERROR -- RB2 "Ties" is multi-valid-
answer FACTUAL, not subjective; the -13/-8 harm is mechanically predicted
anchoring-on-one-valid-answer-among-many. The gradient's soft end must be
relabeled: the verified claim is "self-reference harms MULTI-VALID-ANSWER
evaluation," not "subjective evaluation" (Focus deltas -2/-5 are inside the
+/-8-9pt noise band and cannot carry the subjective claim). (2) Self-preference
literature (2410.21819, 2601.22548) predicts the anchoring mechanism; the sign
flip as a phenomenon is not pre-empted, but 2509.19880's per-dataset appendix
must be checked for negative subjective cells before claiming priority.
(3) Flip-rate-as-quality-proxy is established; the delta-flip diagnostic is
confounded with pair difficulty -- downgraded from headline to observation.
(4) Stats: McNemar + per-cell CIs required; surviving cells = Ties -13, 14B
Math +10 (borderline), and flip deltas >10pts.
CONTROL RUNNING: other-model reference arms (14B judge with 0.5B ref = wrong-
but-plausible; 14B with 3B ref; 3B with 14B ref), matched format. If Ties harm
persists with other-refs -> generic single-answer anchoring; if it vanishes ->
self-preference specifically; if gold-quality other-ref (14B ref for 3B judge)
HELPS Ties -> reference quality, not selfness, is the variable.

### Finding 13 FINAL (controlled): the reference double dissociation

Cross-reference controls (14B judge with 0.5B/3B references; 3B judge with 14B
reference; format-matched) + McNemar item-paired stats:

  14B judge      Math acc/flip     Ties acc/flip
  direct           75 / 24           99 /  2
  selfref          84 / 13  p=.006   91 / 17  p<.0001
  xweak(0.5B ref)  73 / 21  ~0       92 /  9  p=.0005
  xmid(3B ref)     82 / 11  +7       92 / 11  p=.0002
  (3B judge: xstrong 14B-ref harms Ties 91->81 like selfref 91->78)

- F13a' ON SINGLE-ANSWER VERIFIABLE CONTENT the reference effect tracks
  REFERENCE QUALITY: good references help (+7..+9, p<.01), a bad reference is
  ~neutral. Selfness is irrelevant; quality is the variable.
- F13b' ON MULTI-VALID-ANSWER CONTENT, ANY single reference degrades judging
  (-7..-8, p<=.0005; order-instability 2 -> 9-17%), regardless of quality or
  source: the judge anchors on one valid answer and penalizes equally-valid
  alternatives. Self-preference is CLEARED as the mechanism by the controls.
- F13c' The oversight-relevant axis is ANSWER MULTIPLICITY, not "subjectivity":
  reference-based oversight is structurally harmful under answer plurality.
  Combined with F7/F11: references are the cheap-oversight lever exactly and
  only where answers are unique; under plurality the lever inverts. Precise-IF
  remains untouched by any reference (the meticulous-checking bottleneck).
- Critic loop closed: construct error fixed (Ties = multi-valid factual), the
  demanded control run, self-preference alternative eliminated, McNemar
  reported. Remaining verification before external claims: check 2509.19880's
  per-dataset appendix for any prior negative cells.

### F13 novelty positioning confirmed (2509.19880 appendix audit)

"Do Before You Judge" covers 21 subtasks, ALL single-deterministic-answer or
meta-judged binary; POINTWISE only (pairwise deliberately avoided); no
other-model-reference control; no order-consistency measures; the only conceded
negative is the wrong-self-reference case (one -2.11 F1 cell). Our F13-final
(multi-valid-answer pairwise, ANY-reference harm at -7/-8 with p<=.0005,
reference-source controls, order-instability, scale-resolved) is untested there:
position as THE BOUNDARY AND INVERSION of their mechanism. Verdict: PARTIAL
adjacency, specific claim unclaimed.

### Finding 9 extension: gated families close the deconfound (6/6)

Llama-3.1-8B: ref 63% / noref 49% (+14). Gemma-2-9B: ref 70% / noref 46% (+24).
The scale x reference interaction now replicates in SIX model families (Qwen,
Microsoft, MistralAI, AI2, Meta, Google) -- every family shows the reference
boost at mid-scale, magnitude varying with family verification capability. The
novelty critic's judge-family deconfound is complete.

## PHASE 2 CLOSED

Deliverables: F13-final (reference double dissociation: quality-tracked help on
single-answer content, ANY-reference harm under answer multiplicity, controls +
McNemar, novelty positioned against 2509.19880 as its boundary/inversion);
Precise-IF checking bottleneck at all scales; label-free flip-rate scale curve;
6-family interaction replication. Full record: Findings 1-13 across both
phases, two design critics + two adversarial critics passed, one public
retraction cycle, external validations (Platinum, ProcessBench, RB2).

### Finding 14 (plurality replication: partial, and the boundary condition)

Synthetic plurality instrument (validity code-checkable; reference = a DIFFERENT
valid answer; single-answer twins as within-family control; 5 judges incl.
Gemma; McNemar):
  single twins: reference helps hugely for capable judges (7B +39 p<1e-4,
  14B +32, Gemma +12; flips 68-78% -> 3-7%). Clean replication of the
  quality-tracking side.
  plural items: NO harm for >=3B (deltas 0..+3, n.s.) -- but harm reappears at
  1.5B on BOTH kinds (-13/-14, p<1e-4; plural flips 57->95%).
Interpretation, exactly the minimal model's q-term: the anchoring harm operates
through COMPARATOR RELIANCE, which engages only when independent verification
is hard relative to the judge. Synthetic validity checks are easy for >=3B
(they keep verifying; no harm); RB2 Ties' factuality checks are hard for every
judge on the ladder (all defer; all harmed); 1.5B cannot verify anything (harmed
everywhere).
REVISED LAW (final form): a reference degrades judging when (a) valid answers
are plural AND (b) the judge cannot cheaply verify validity itself, i.e. in the
comparator-reliant regime -- which is where scalable oversight's hard cases
live by definition. Scope narrowed, mechanism strengthened, model prediction
confirmed rather than assumed.

### Finding 15 (adaptive reference policy: proof of concept)

Router = "use self-reference when a cheap classification pass says the prompt
has one right answer; go bare otherwise" (14B classifier, 462 prompts: 300
single / 162 multiple). Evaluated on existing RB2 arms (14B judge, per-item):
  subset      direct  selfref  ROUTER  oracle
  Math          75      84       84      89
  Precise IF    52      57       56      64
  Focus         84      79       79      88
  Ties          99      91       95      99
  pooled        76      77       78      84
The router simultaneously captures the Math reference gain AND undoes most of
the Ties anchoring harm, beating both fixed policies pooled, with honest
limits: it misroutes Focus (multiplicity is the wrong key there; per F14 the
right key is verification hardness relative to the judge), and oracle routing
shows +6 points of headroom. Deliverable: a deployable adaptive judging
protocol standing in for "a new judge model," with its failure mode and
improvement direction identified.

### Scorer retrofit (root-cause fix, user-directed)

tfa/boxed.py patched (GSM8K answer-phrase + last-number fallbacks; numeric
folding in normalization). Legacy score files retrofitted to *_corrected.jsonl
copies with a full ledger (runs/cc_corrections.jsonl): 751 upgrades 0->1,
concentrated exactly in the diagnosed bug class (gsm8k 256, gsm8k-platinum 249,
putnam-axiom-var 246; zero on boxed-style MATH files). First retrofit attempt
DISCARDED after self-audit: without local math_verify it produced ~2.5k
artifactual downgrades on LaTeX answers; rerun with math_verify installed under
an UPGRADE-ONLY policy (original cc=1 never re-litigated; the validated failure
mode is false negatives). Spot-checked upgrades all genuine ("$57.00" vs 57,
"Answer: 38", comma formatting). Note: original files untouched; analyses
wanting corrected labels should read cc_corrected.
