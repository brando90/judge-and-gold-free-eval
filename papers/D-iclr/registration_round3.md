# Round-3 registration, written and committed BEFORE any of its judge scores exist

Motivation: an external presentation-focused review of the revised draft (papers/D-iclr/reviews/round2_review.md) found that the draft's boundary claim rests on a confounded comparison (the only judge that reasons at length, Qwen3-8B with thinking, differs from the anchoring judges in model, estimator, and template), that no thinking judge was tested on tasks it cannot verify by calculation, and that the practical consequence was never measured end to end on a natural multi-answer pool. This file registers four experiments.

Harnesses (committed with this file): `experiments/tfa-vs-judge/scripts/r3_build_subsamples.py`, `r3_judge.py`, `r3_mitigation_mace.py`, `r3_chain_gpu7.sh`, `r3_chain_gpu4.sh`.
Producers (frozen, committed with this file): `papers/analysis/r3_toggle_analysis.py`, `r3_mace_accuracy_analysis.py`.
All intervals: task-level bootstrap, 1,000 resamples, numpy default_rng(0).

---

## R3-A. Thinking on versus off, same weights (Qwen3-8B)

**Design.** The R2-B REASON protocol (Qwen3-8B, rubric a with a final "Score: N" line, temperature 0.6, top-p 0.95, top-k 20, up to 4,096 new tokens) is rerun with `enable_thinking=False` and nothing else changed, on the same ROT subsample (conditions ref, refrot, noref) and KSUB subsample (ref, noref). The thinking-on arm is the existing R2-B REASON data.

**Readouts.** As in R2-B: per-task mean same-sample change (refrot − ref) for gainers, losers, placebo; KSUB paired referenced-minus-blind margin at k>1; KSUB best-of-16 accuracy deltas. New: the per-task paired difference in loser change between arms (off − on), over tasks with losers in both arms.

**Predictions.**
- **P-R3A1.** Thinking off: loser change < 0, CI excluding zero.
- **P-R3A2.** Thinking off: gainer change > 0, CI excluding zero.
- **P-R3A3.** Loser change, thinking off minus thinking on, < 0 with CI excluding zero.
- **P-R3A4.** Thinking off: KSUB referenced-minus-blind margin at k>1 > 0, CI excluding zero.

## R3-B. Thinking on versus off, a frontier judge (Claude Sonnet 5)

Registered separately in `registration_round3b.md` after a harness pilot on items outside its pool, and before any of its pool is judged. Its pool file `runs/r3/sonnet_rot.jsonl` is built by `r3_build_subsamples.py` with this commit.

## R3-C. A thinking judge on tasks it cannot verify by calculation (MACE entity questions)

**Pool.** `runs/r3/macesub.jsonl`: every MACE River or Language task with k > 1 that has both reference-matching and non-matching valid samples among its 64; up to 4 samples from each of matching-valid, non-matching-valid, and invalid (seed 1). Matching follows `papers/analysis/mace_analysis.py`. Validity of these questions is knowledge-based, so a judge cannot check a candidate by calculation.

**Design.** Qwen3-8B, R2-B REASON prompt, conditions ref and noref, thinking on and thinking off.

**Readouts.** Per arm: per-task referenced margin (matching-valid minus non-matching-valid mean score) minus blind margin; false-rejection rate of non-matching valid samples (score ≤ 3), referenced minus blind.

**Predictions.**
- **P-R3C1.** Thinking on: referenced-minus-blind margin > 0, CI excluding zero.
- **P-R3C2.** Thinking off: referenced-minus-blind margin > 0, CI excluding zero.
- **P-R3C3.** The thinking-on margin difference is smaller than the thinking-off one (point estimates).

## R3-D. End to end on a natural multi-answer pool (MACE River + Language)

**Pool.** All MACE River and Language tasks, with the benchmark's natural mix of k ∈ {1, 2, 4, 6}, restricted to tasks with pool pass rate in [0.05, 0.95] (the band `mace_analysis.py` uses).

**Design.** Qwen2.5-7B-Instruct and phi-4. Blind and reference scores: the frozen `runs/bon_scores_mace/mace__{judge}__{noref,ref}_a.jsonl`. New: blind-then-reveal (m1) and the soft validity gate (m2), prompts copied verbatim from `mitigation_judge.py`, rubric a.

**Readouts.** Best-of-64 selection accuracy (rubric-a selection, validity averaged over ties) for blind, reference, m1, m2; deltas by k = 1, k > 1, and pooled over the natural mix. Post hoc: the multi-answer prevalence at which m1 and the plain reference give equal expected accuracy, from the k = 1 and k > 1 deltas.

**Predictions.**
- **P-R3D1.** At k > 1, reference minus blind < 0 with CI excluding zero, both judges.
- **P-R3D2.** At k > 1, m1 minus reference > 0 with CI excluding zero, both judges.
- **P-R3D3.** Pooled over the natural mix, m1 accuracy ≥ reference accuracy (point estimates), both judges.

Whatever the outcomes, all are reported in the paper's ledger.

---

## Outcome, R3-D (recorded 2026-09-13 after running the frozen producer; `r3_mace_accuracy_results.json`)

133 MACE River+Language tasks in the [0.05, 0.95] band (34 with k = 1, 99 with k > 1). Blind scores correlate with validity at r = 0.361 (Qwen2.5-7B) and 0.477 (phi-4), so the frozen MACE score files are aligned.
- Qwen2.5-7B: reference − blind +0.324 [+0.176, +0.471] at k = 1, +0.020 [−0.051, +0.091] at k > 1, +0.098 [+0.023, +0.173] pooled; m1 − reference −0.088 at k = 1, −0.010 [−0.071, +0.061] at k > 1, −0.030 [−0.083, +0.023] pooled.
- phi-4: reference − blind +0.265 at k = 1, +0.061 [−0.010, +0.131] at k > 1, +0.113 [+0.052, +0.181] pooled; m1 − reference 0.000 at k = 1, −0.020 [−0.061, +0.020] at k > 1, −0.015 [−0.045, +0.015] pooled.
- **P-R3D1 FALSIFIED, P-R3D2 FALSIFIED, P-R3D3 FALSIFIED** for both judges. On this natural pool the reference raises best-of-64 accuracy overall and does not measurably lower it at k > 1, and blind-then-reveal does not beat the plain reference. The post-hoc break-even is undefined for Qwen2.5-7B (m1 never ahead) and 0 for phi-4.

## Outcomes, R3-A and R3-C (recorded 2026-09-13 after running the frozen producer; `r3_toggle_results.json`)

Unparseable: 12 of 1,200 KSUB blind thinking-off replies; none elsewhere. Thinking-on ROT/KSUB data are the R2-B REASON files.
- **R3-A, thinking off:** gainer +0.567 [+0.414, +0.747]; loser −0.694 [−0.918, −0.471]; placebo −0.035 [−0.209, +0.142]; KSUB referenced-minus-blind margin at k>1 +1.179 [+0.247, +2.381]; loser change off − on −0.704 [−0.927, −0.482]. **P-R3A1, P-R3A2, P-R3A3, P-R3A4 CONFIRMED.**
- **R3-C, MACE entity subsample (81 tasks):** referenced-minus-blind margin +3.615 [+2.551, +4.748] with thinking on and +6.160 [+5.229, +7.150] with thinking off; false-rejection increase +0.216 [+0.133, +0.299] on and +0.443 [+0.369, +0.523] off. **P-R3C1, P-R3C2, P-R3C3 CONFIRMED.**
- Reading: within the same weights, extended thinking removes anchoring on tasks the judge can check by calculation and halves it, without removing it, on questions whose validity rests on knowledge.
