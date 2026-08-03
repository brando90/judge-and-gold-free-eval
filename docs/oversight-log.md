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
