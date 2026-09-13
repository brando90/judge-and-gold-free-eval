# Round-2 registration (ICLR revision), written and committed BEFORE any of its data exists

Date: 2026-09-13. Motivation: a presentation-focused AC review of the ICLR draft (papers/D-iclr/reviews/round1_review.md) raised two evidence gaps that wording cannot fix:
(B1) blind-then-reveal (M1) was never tested on a pool where the reference genuinely helps, so the paper cannot say what M1 buys over blind judging;
(B2) every judge so far emits a single score token under our own rubrics, so the anchoring could be an artifact of forbidding reasoning or of our wording.
This file registers two experiments. Producers (frozen, committed with this file):
`papers/analysis/r2_math_m1_analysis.py`, `papers/analysis/r2_realism_analysis.py`.
Harnesses: `experiments/tfa-vs-judge/scripts/mitigation_judge_math.py`, `r2_build_subsamples.py`, `r2_judge.py`, `r2_chain.sh`.
Compute: one GPU on the shared cluster, jobs run sequentially.

---

## R2-A. Blind-then-reveal where the reference helps: MATH-500 (unique answers)

**Pool.** `runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl` (500 MATH-500 problems, 64 samples each, exact answer oracle), restricted to the 105 problems whose pool pass rate lies in [0.2, 0.8] (the same band used throughout the paper).

**Judges.** Qwen2.5-7B-Instruct and Qwen2.5-14B-Instruct. Blind (`noref`) and reference (`ref`) score files already exist (`runs/bon_scores/math__{judge}__{noref,ref}_{a,b}.jsonl`) and are frozen.

**New condition M1-math.** Call 1 repeats the blind prompt exactly. Call 2 uses the math reference rubric, shows the trusted reference solution and the blind score from call 1, and adds: "You have already assessed this candidate without seeing any reference. A correct solution that differs from the reference in method or presentation must keep the score you gave it; revise only if the reference reveals the candidate is actually wrong." The reported score is call 2's expected score. Rubrics a and b.

**Readout (frozen).** Selected-answer accuracy under best-of-64: select with rubric-a scores, average validity over samples tied at the maximum. Per problem, paired across conditions; item-level bootstrap, 1000 resamples, numpy default_rng(0).

**Predictions.**
- **P-R2A1.** The reference improves selected-answer accuracy over blind: mean(acc_ref − acc_blind) > 0 with 95% CI excluding zero, for both judges.
- **P-R2A2.** M1 keeps less than half of that benefit: mean(acc_M1 − acc_blind) < 0.5 × mean(acc_ref − acc_blind), point estimates, for both judges. (This is what "the reveal call defers to the displayed blind score" predicts.)
- Exploratory: acc_M1 − acc_blind with CI; the paper's inflation estimator on the same conditions; agreement between call-1 blind scores and the frozen blind file.

---

## R2-B. Judge realism: a reasoning judge and a standard third-party prompt

**Protocols.**
- **REASON.** Qwen3-8B with thinking enabled (chat template `enable_thinking=True`), temperature 0.6, top-p 0.95, top-k 20, max 4096 new tokens. System prompt = the paper's rubric a (blind or referenced version) with its last sentence replaced by: "Think it through, then end your reply with a final line of the form 'Score: N', where N is an integer from 0 to 10." Score = last "Score: N" in the text after the thinking block.
- **MTBENCH.** Qwen2.5-7B-Instruct with the verbatim FastChat MT-Bench single-answer templates: `single-math-v1` (reference shown; "Begin your evaluation by comparing the assistant's answer with the reference answer") for referenced conditions and `single-v1` for blind; system prompt "You are a helpful assistant."; greedy, max 1024 new tokens. Score = last "[[N]]" (1–10).
Unparseable replies are counted and excluded, never defaulted.

**Pools (built deterministically by `r2_build_subsamples.py`, seed 0, before any judging).**
- **ROT.** From the 120-task replication pool and its frozen rotated counterpart (`bon_replrot`): per task, up to 3 oracle-valid samples in each class (matches the original reference = LOSER; matches the rotated reference = GAINER; valid and matches neither = PLACEBO), classes defined exactly as in `replrot_analysis.py`. Conditions: `ref` (original reference), `refrot` (rotated reference), `noref`.
- **KSUB.** From the 75-task k-pool: 16 samples per task drawn uniformly at random. Conditions: `noref`, `ref`.

**Readouts (frozen).**
- ROT: per-task mean same-sample change (refrot − ref) for GAINERS, LOSERS, PLACEBO; item-level bootstrap CIs; gainer-minus-placebo contrast where both exist.
- KSUB: anchoring margin at k>1 (mean referenced score of valid matching samples minus valid non-matching samples, per task with both) for `ref` and for `noref`; paired ref-minus-noref margin difference. Selected-answer accuracy at best-of-16 (tie-averaged) for ref and noref; the step = mean over k>1 tasks of (acc_ref − acc_noref) minus mean over k=1 tasks of the same.

**Predictions, each registered separately for REASON and for MTBENCH.**
- **P-R2B1.** GAINER change > 0, CI excluding zero.
- **P-R2B2.** LOSER change < 0, CI excluding zero.
- **P-R2B3.** KSUB referenced margin at k>1 exceeds the blind margin: paired difference > 0, CI excluding zero.
- **P-R2B4 (directional only, underpowered).** Accuracy step < 0 (point estimate).
- Exploratory: effect sizes relative to the single-token judges; unparseable rates; thinking length.

Whatever the outcomes, all are reported in the paper's ledger.

---

## Amendment 1 (2026-09-12, 23:40 local), after the first R2-A output and before any other R2 readout

**What happened.** The first M1-math file (Qwen2.5-7B, rubric a) was pulled and the frozen producer run locally. It reported M1 accuracy 0.952 against blind 0.400 and reference 0.571, and the call-1 blind scores correlated −0.51 with the "frozen" blind file. A check of score–oracle correlations showed that the LOCAL copies of `runs/bon_scores/math__Qwen__Qwen2.5-*-Instruct__{noref,ref}_*.jsonl` are misaligned with the Qwen-generated MATH pool (mean per-problem correlation with the oracle −0.24 to 0.00) and instead align with the Llama-generated MATH pool (+0.27 to +0.43). The CLUSTER copies of the same filenames align with the Qwen-generated pool (blind +0.25 to +0.34, reference +0.73 to +0.85). The local files are therefore stale copies of a different pool; the cluster files are the frozen ones the registration names.

**Deviation (path only).** `r2_math_m1_analysis.py` now reads the frozen blind and reference files from `runs/r2/frozen_math/`, which holds byte-exact copies of the cluster files. The design, readout, and predictions are unchanged. The first local readout above is void. The M1 scores themselves are unaffected (they were produced on the cluster from the correct pool). Consequence for P-R2A1: its inputs are pre-existing files, and a post-hoc accuracy readout on the misaligned local copies was seen before this amendment; P-R2A1 is therefore reported without registration weight. P-R2A2 involves the new M1 data and keeps its registered status, with this amendment disclosed.
