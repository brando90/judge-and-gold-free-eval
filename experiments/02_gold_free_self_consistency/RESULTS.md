# RESULTS: experiment 02, gold-free and judge-free self-consistency (pilot)

Dated 2026-11-24 (Tue). Harness: local Python 3 + Math-Verify 0.9.0 + numpy/scipy, analysis only, **no model
was called** (no plan account used, no tokens spent). Data: committed Llama-3.1-8B-Instruct samples (64 x 500
MATH-500 problems) and committed Qwen2.5 judge scores (1.5B/3B/7B/14B, noref and ref). PREREG.md was
committed (d1d53e8) before any outcome number was computed.

## Takeaway (first)
- **Versus LLM judges: YES.** SC, which needs no gold, no human and no judge, beats the best no-reference
  judge (Qwen-14B) by +0.19 within-problem AUROC [0.16, 0.22] and +0.19 selection accuracy [0.12, 0.26].
- **As a trustworthy replacement for the gold metric (boxed accuracy, pass@k): NO, per the prereg.**
  Pre-registered properties P2 (repeat stability) and P5 (confident wrongness) fail, and P1
  (surface-form invariance) failed on the original matcher. A post-hoc normalizing matcher fixes P1 only.
- Why it can fail: SC measures consensus, not correctness. At SCP >= 0.5 (40% of problems) the consensus
  answer is wrong 12% of the time (precision 0.876 to 0.880), and no amount of self-agreement flags a model
  that is consistently wrong. SC also needs many samples per problem, and ranks answers within one model only.

## Numbers (primary matcher = Math-Verify canonical keys, as pre-registered; deviations below)
| result | value |
|---|---|
| Alignment control: Qwen-14B ref judge pooled AUROC (need >= 0.85) | 0.913 (pass) |
| E1, 176-problem judge subset: SC / best noref judge (14B) within-problem AUROC | 0.956 [0.937, 0.973] / 0.767 [0.747, 0.787] |
| E2, same subset: SC / best noref judge selection accuracy (pass@1 of a random sample 0.495) | 0.949 / 0.761 |
| E1/E2 on all 500 problems (SC only, no judge scores exist): within AUROC / selection acc (pass@1 0.342, pass@64 0.802) | 0.884 [0.863, 0.905] / 0.580 |
| E3: Spearman(SCP, per-problem pass@1), all 500 (by MATH level 1..5: 0.91, 0.83, 0.82, 0.75, 0.67) | 0.836 |

Context (gold-needing, not rivals): the four ref judges reach AUROC 0.915 to 0.938 and selection accuracy
0.869 to 0.938; SC (no gold) matches them on this subset.

## Properties (pre-registered pass lines in PREREG.md)
| property | result | pass |
|---|---|---|
| P1 surface-form invariance, original rewrites (strip trailing period, `$`-wrap, dfrac) | mean abs change 0.033, Spearman 0.973 (plain string matcher: 0.139) | FAIL |
| P1b held-out rewrites (frac to a/b, add .0, commute sum, sqrt n) | 0.0002, Spearman 0.9997 | pass |
| P2 repeat stability: SCP split-half Spearman / plurality answer agreement (need >= 0.90 each) | 0.955 / 0.694 | FAIL |
| P3 monotone in evidence: AUROC at n_ref = 4, 8, 16, 32, 63 | 0.781, 0.817, 0.846, 0.868, 0.884 | pass |
| P4 bug detection (injected wrong answer scores below the original) | 484 of 484 (near-tautological by construction) | pass |
| P5 confident wrongness: precision at SCP >= 0.5 (need >= 0.90) / coverage; ECE | 0.876 / 0.402; 0.062 | FAIL |

By MATH level, precision at SCP >= 0.5 is .94, .88, .88, .83, .86 for levels 1 to 5 (hard problems are
where confident-wrong consensus is most common).

## Deviations and post-hoc work (all labelled; none changes the verdict)
- D1: pairwise Math-Verify verification was too slow (more than 25 min on a loaded CPU, killed). Answers are
  instead mapped to a canonical key via `math_verify.parse` and compared by key. Same matcher family.
- D2: `parse` timeout 1 s gave load-induced timeouts, raised to 10 s; the 1 s run is kept in `results_run1_timeout1s/`.
- D3 (post hoc, in `results_v2_normalized/`): strip `$`, dfrac/tfrac to frac, `\left`/`\right`, `\!`, `\,` and
  trailing punctuation before parsing. Diagnosis: Math-Verify misparses `33/100.` as 33.0 and `15x - 80.` as 80.0,
  so keys changed under trivial rewrites. With it: P1 passes (0.0005, Spearman 0.9998) and fallback to plain
  strings drops from 6.5% to 0.9%; **P2 and P5 still fail** (plurality agreement 0.682, precision 0.880 at
  SCP >= 0.5), SC E1 0.960, E2 0.955, E3 0.836. Verdict stays NO.
- The prereg verdict is NO because of P2 and P5 (and P1 on the original set). It is not driven by SC versus the judges.

## Caveats
- The 176-problem judge subset is the committed "in-band" set, so absolute SC numbers there (0.96) are higher
  than on all 500 (0.88); compare SC with judges on the subset only.
- 27% of samples have no `\boxed{}` answer and score 0; on boxed samples only, SC 0.947 vs 14B noref 0.761.
- One generator, one benchmark, final-answer tasks only. **Model-level ranking is untested** (one model here).
- SC selection is plurality voting (majority@64); the contribution is using agreement as a gold-free metric with
  properties, not the voting idea itself.
- Judge repeat stability is partly model noise (noref 1.5B replicas correlate 0.68); SC split-half item
  Spearman is 0.957, similar to the better judges.
- Figures (grid on): `results*/auroc.png`, `results*/calibration.png`. Raw: `results*/results.json`, `tables.md`.

## Next (3 days, check Wed 2026-11-25 10:00 onward)
1. Model-level ranking: samples from 4 to 6 models on the same 500 problems (generation job through the plan
   router, Vals and Stanford first, included usage only, no agy); test whether SC ranks models like gold accuracy.
2. Add an abstention rule (SCP >= 0.7: precision 0.908 to 0.915, coverage 0.26) and test it on a second benchmark.
3. Properties for the judge/human/boxed-accuracy side: run the same P1-P5 suite on the boxed-accuracy and judge scores.
