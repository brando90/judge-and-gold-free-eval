# PREREG: experiment 02, gold-free and judge-free self-consistency (pilot)

Dated 2026-11-24 (Tue), written and committed BEFORE any outcome number is computed.
Harness: analysis only (Python 3, Math-Verify 0.9.0, numpy/scipy). No model is called, so no tokens
are spent on any account. Every number comes from data already committed in this repo.

## Claim under test (Brando, 2026-11-24)
> A metric that **replaces the gold reference / target metrics** (human labels, boxed-answer accuracy,
> pass@k). Replacing LLM judges too is a bonus. **The more trustworthy the better.**

Testable form: a candidate metric M that uses **no gold answer, no human label and no LLM judge**
(a) ranks and selects a model's answers about as well as the judge baselines do, (b) tracks the gold
metrics (boxed correctness, pass rate), and (c) passes falsifiable sanity properties, not only a
correlation. Correlation with humans or gold is necessary, never sufficient (see "Properties").

## Candidate metric M: self-consistency agreement (SC)
For a problem with n = 64 samples from one model:
- `ans(s)` = last `\boxed{...}` of sample s. A sample with no box has no answer.
- Two answers match if Math-Verify says they are equivalent (fallback: whitespace-normalised
  string equality when Math-Verify cannot parse either one). A missing answer matches nothing.
- Item score `SC(s)` = fraction of the OTHER 63 samples whose answer matches ans(s). Missing answer: 0.
- Problem score `SCP(p)` = share of the largest answer cluster among the 64 samples (plurality share).
- Selection by M = the sample with the largest SC (ties: the lowest sample index) = plurality vote.

## Data (all committed in `experiments/tfa-vs-judge/runs/`)
- G: `bon/bon_math__meta-llama__Llama-3.1-8B-Instruct.jsonl`: 500 MATH-500 problems x 64 samples from
  Llama-3.1-8B-Instruct, gold correctness bit per sample (`oracle`), `level` 1 to 5.
- J: `bon_scores_llama/math__Qwen__Qwen2.5-{1.5B,3B,7B,14B}-Instruct__{noref,ref}_{a,b}.jsonl`:
  Qwen judge scores (`escore`, 64 per problem) on 176 of the 500 problems (the in-band subset).
  Judge baseline score = mean of its `_a` and `_b` files. "noref" judges see no gold (fair rivals of M).
  "ref" judges see the gold reference (gold-needing, so NOT rivals: shown for context).
- Alignment control (pre-registered): the Qwen-14B ref judge must reach pooled AUROC >= 0.85 on
  the gold bit. If not, the J files are not aligned to G's sample order and J results are dropped.

## Metrics compared
| name | needs gold | needs judge | role |
|---|---|---|---|
| boxed correctness (`oracle`) | yes | no | the target to replace |
| pass rate per problem (pass@1), pass@k (k=4,16,64) | yes | no | the target to replace |
| SC / SCP (candidate M) | no | no | candidate |
| Qwen {1.5B,3B,7B,14B} noref judge | no | yes | rivals |
| Qwen {1.5B,3B,7B,14B} ref judge | yes | yes | context |

## Primary endpoints (frozen)
E1 (item level, within problem). Mean over problems that have both correct and wrong samples of the
   AUROC of the score against the gold bit, on the 176-problem judge subset. Cluster bootstrap over
   problems, 2000 resamples, 95% CI. Report M, each noref judge, each ref judge.
E2 (selection, the best-of-n use). Accuracy of the sample chosen by argmax score, mean over the 176
   problems (ties by lowest index). Compare M, each judge, mean pass@1, and the oracle (pass@64).
E3 (problem level). Spearman between SCP and pass@1 over all 500 problems. Also on each level 1 to 5.

## Properties (the trust part; each is pass/fail with its threshold)
P1 Surface-form invariance. Rewrite every answer string with meaning-preserving edits (`\frac`<->`\dfrac`,
   delete spaces, `\left(`->`(`, add/remove a trailing period, wrap in `$`). SC recomputed must match the
   original: mean |delta SC| < 0.01 and Spearman with the original >= 0.99. Run for the Math-Verify
   matcher (expected pass) and for plain string equality (expected FAIL: shows why equivalence is needed).
P2 Repeat stability. Split the 64 samples of each problem into two random halves (fixed seed). SCP of the
   two halves: Spearman >= 0.90, and the plurality answers agree (Math-Verify) on >= 90% of problems.
   Baseline for comparison: judge replicas a vs b item-level Spearman.
P3 Monotone in evidence. AUROC (E1 definition, all 500 problems where both classes exist) with n_ref in
   {4, 8, 16, 32, 63} reference samples per item (random subsets, seeded, 20 repeats). Weakly
   increasing: each step may drop by at most 0.01.
P4 Bug detection. Replace one sample's answer with another problem's gold-unrelated wrong answer
   (the plurality answer of a different problem, seeded). SC of the corrupted sample must fall below its
   original for >= 95% of originally-agreeing samples (SC > 0). Near-tautological, kept as a sanity floor.
P5 No confident wrongness (the real risk). Among problems with SCP >= 0.5, the share whose plurality
   answer is correct (precision) must be >= 0.90; also report ECE of SC read as P(correct) (10 equal bins),
   and coverage and precision by SCP threshold (0.3, 0.5, 0.7, 0.9) and by MATH level.

## Predictions (written before running)
- E1: SC within-problem AUROC about 0.75 (0.65 to 0.85); best noref judge about 0.65 to 0.75; ref judges
  >= 0.90. Probability SC >= best noref judge - 0.02: 70%.
- E2: plurality selection accuracy beats the best noref judge selection: 80%. Stays below the oracle.
- E3: Spearman(SCP, pass@1) about 0.80 over 500 problems, weaker on level 5 (consistently wrong).
- P1 passes with Math-Verify and fails with plain strings: 90%. P2 passes: 90%. P3 passes: 85%.
  P4 passes: 99%. P5 passes (precision >= 0.90 at SCP >= 0.5): 50%; the failure, if any, sits at levels 4 to 5.

## Decision rule (verdict on "M matches or beats the judge baselines and is trustworthy")
- YES: E1 lower bound of (SC minus best noref judge) > -0.02 AND E2 SC >= best noref judge AND P1 to P3 pass AND P5 passes.
- NO: E1 point estimate of SC is more than 0.05 below the best noref judge, OR any of P1, P2, P3 fails for the Math-Verify matcher.
- INCONCLUSIVE: anything else. A P5 failure alone turns YES into "YES with a stated abstention region".
The comparison with gold-needing targets (boxed accuracy, pass@k) is reported, not decided: M is expected
to approximate them, never to equal them.

## Not claimed
- Model-level ranking (do SC scores rank different models like gold accuracy does?) needs several models'
  answers on the same problems; the committed data has one model with 64 samples. That is the next step.
- One generator (Llama-3.1-8B-Instruct), one benchmark (MATH-500), final-answer tasks only. Proofs and code
  are out of scope for this pilot.

## Deviations
Any change after this commit is listed in RESULTS.md under "Deviations" with the reason.
