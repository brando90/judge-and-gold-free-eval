# Registration 32 — frozen holdout replication of the reference swap

**Status: REGISTERED by this commit. No judging call had been made against this pool when
this document and `papers/analysis/holdout_analysis.py` were committed; the commit
timestamp is the registration. Candidate generation and oracle labelling were complete
before this point and are reference-independent. An OSF copy may follow; it does not
change the hypotheses or thresholds below.**

*Amended 2026-09-19, before any data exists, to record the weights-source deviation in
the Design section. Amending a draft before the timestamp is legitimate; amending after
would not be.*

Written 2026-09-19, after the v6 manuscript was complete, in response to a reviewer request for
"one completely locked holdout replication" whose hypotheses, metrics, thresholds and verdict rule
are fixed before any data exists. This document and `papers/analysis/holdout_analysis.py` are to be
committed and timestamped together, before the first judging call. The commit timestamp is the
registration.

## Why this run exists

Every rotation result in the paper comes from one task pool (`runs/repl_main_tasks.jsonl`, 120
items, registration 3). The reviewer's objection is not that the effect is absent but that the
ledger's 329 predictions, many analysed after their data existed, make the confirmatory boundary
hard to read. This run answers that with a single pre-registered replication on items that did not
exist when the paper was written.

## Pool

`runs/holdout_main_tasks.jsonl`, 110 items, built by
`scripts/build_replication_pool.py --seed 20260919 --out-prefix runs/holdout --n-main 600`
followed by the novelty filter described below. The builder is the one that produced the original
pool; it was parameterised on 2026-09-19 to accept `--seed` and `--out-prefix`, and its defaults
reproduce the frozen pool byte for byte (verified by diff).

**Novelty filter.** Any generated instance whose family and full parameter dictionary matched an
item in `runs/repl_main_tasks.jsonl` or `runs/repl_pilot_tasks.jsonl` was discarded, as were
duplicates within the draw. Overlap with the frozen pool after filtering is **0 of 110**.

**Family imbalance is a known constraint, not an accident.** crt, subset, goldbach and divcount
contribute 24 items each; `digitsum` contributes 14. A 2,000-item draw yields only 14 novel
`digitsum` instances, so that family's parameter space is substantially exhausted by the frozen
pool. We register the imbalance rather than rebalance by reusing seen items.

Per-item valid-answer counts range 2 to 23 (median 5). Each item stores its full enumerated
solution set and one reference drawn from it.

## Design

The rotation design of `app:rotation`, unchanged. For each item we build a rotated twin in which
`ref_answer` is replaced by a different member of the solution set, with `rot_from` recording the
original. Candidate responses are generated once, by Llama-3.1-8B-Instruct at 64 samples per item,
and are **byte-identical across the two reference conditions** — only the reference block differs.

**Weights source, recorded before any judging.** The frozen pool's candidates came from
`meta-llama/Llama-3.1-8B-Instruct`. That repository is gated and this cluster holds no
HuggingFace credential, so the holdout's candidates are sampled from
`NousResearch/Meta-Llama-3.1-8B-Instruct`, an ungated mirror of the same release. Its
`config.json` matches the original on every architectural field (32 layers, hidden 4096,
intermediate 14336, 32 attention heads, 8 key-value heads, vocab 128256, context 131072,
rope_theta 500000, bfloat16). We could not checksum the weights against the gated original, so
this is recorded as a deviation: if the mirror differs from the release in any way, the holdout's
candidate distribution differs from the frozen pool's by that much. No hypothesis below depends on
the generator's identity — all five are within-item paired comparisons on identical candidate text
— but H32-5 is a magnitude threshold and would be affected by a materially different generator.

**Judges.** Qwen2.5-7B-Instruct and microsoft/phi-4, the two judges of the registered rotation,
scored under rubrics `a` and `b` separately. Four judge × rubric cells.

**Sample classes**, from the loose-normalised boxed answer (fallback: whole reply), identical to
`replrot_analysis.py`:
- GAINER — oracle-valid, answer equals the rotated reference;
- LOSER — oracle-valid, answer equals the original reference;
- PLACEBO — oracle-valid, answer equals neither.

**Readout.** Same-sample delta: rotated-reference expected score minus original-reference expected
score, for the identical sample text. Per-item means, item-level cluster bootstrap, NBOOT = 1000,
`numpy.random.default_rng(0)`.

## Hypotheses, fixed before any judging call

- **H32-1 (gainers).** Mean same-sample delta of GAINERS is positive with a 95% interval excluding
  zero, in all 4 judge × rubric cells.
- **H32-2 (losers).** Mean same-sample delta of LOSERS is negative with a 95% interval excluding
  zero, in all 4 cells.
- **H32-3 (specificity).** The gainer-minus-placebo contrast, paired per item where both classes
  exist, is positive with a 95% interval excluding zero, in all 4 cells.
- **H32-4 (placebo bound).** The PLACEBO mean is within ±0.5 points of zero in all 4 cells. This is
  new to this registration and is the endpoint the reviewer's "identification" praise rests on: it
  states that moving the reference onto an answer the candidate does not give leaves the score
  alone.
- **H32-5 (magnitude, weak).** The GAINER mean is at least +2.0 points in all 4 cells. Registered
  because the paper quotes "3 to 5 points" and a replication that confirmed only the sign would not
  support that range. We register +2.0, not +3.0, because the frozen run's four cells span +3.25 to
  +6.34 and we do not want a threshold that only the favourable rubric clears.

## Verdict rule

Applied per cell, then aggregated as stated in each hypothesis.

- **Confirmed** — the 95% interval excludes zero in the predicted direction (H32-1 to H32-3), or the
  point estimate satisfies the stated bound (H32-4, H32-5).
- **Not confirmed** — the interval includes zero, or the bound is not met.
- **Falsified** — the interval excludes zero in the direction opposite to the prediction.

A hypothesis stated "in all 4 cells" is **confirmed** only if all four cells are confirmed, **split**
if some are, and **falsified** if any cell is falsified.

## Analysis

`papers/analysis/holdout_analysis.py`, committed with this document.

**External copy.** The text of this registration was posted to OSF on 2026-09-19 as
`osf.io/npd9u` (Registration 9 of the project `osf.io/kszeu`). That post was made AFTER the
judging and analysis were complete and does not assert pre-data status: it is a durable
third-party copy of this document's text, and the pre-data evidence remains the commit that
carries this file and the frozen analysis script. The paper cites the commit. It is a copy of the frozen
`replrot_analysis.py` with the pool path and judge list changed and H32-4/H32-5 added; the
normaliser, extractor, class assignment and bootstrap are byte-identical. It is run **once**, after
judging completes, and its output is reported whatever it says.

## Exploratory, carrying no registration weight

Per-family splits; blind-margin comparison; any judge beyond the two named; any rubric beyond `a`
and `b`; the relationship between an item's valid-answer count and its delta.

## What would make us wrong

H32-1 or H32-2 not confirmed in any cell would mean the central swap does not replicate on fresh
items and the paper's main claim is pool-specific. H32-4 failing would mean the reference perturbs
scores generally rather than moving them toward the displayed answer, which would undercut the
causal reading. H32-5 failing while H32-1 held would mean the effect replicates in sign but the
paper's quoted magnitude does not generalise, and the "3 to 5 points" range would have to be
restated as pool-specific.
