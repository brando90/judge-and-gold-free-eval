# jfe-archive — raw run data for Paper D

*"When Several Answers Are Correct, LLM Judges Reward the One They Are Shown"*

This is the copy of record for the judge outputs that the git repository does not carry. The repo
gitignores `runs/*/` (the comment there says the heavy traces are "reproducible from /dfs" — this is
that /dfs). Of 1,872 files, git tracks 755; the other 1,117 exist only here.

## Layout

```
raw/runs/…                      byte-exact mirror of experiments/tfa-vs-judge/runs/
by-experiment/<group>/…         symlinks into raw/, grouped by experiment
meta/runs.sha256                sha256 of every file, paths relative to experiments/tfa-vs-judge/
meta/runs_experiment_map.tsv    the mapping that built by-experiment/
```

`raw/` is the part the code needs: every analysis producer hardcodes paths like
`runs/r4/scores/...`, so the tree is mirrored exactly rather than reorganised. `by-experiment/` is
the part a human needs — it costs a few kilobytes of symlinks and nothing is duplicated.

## Restoring

From a clone of the repo:

```bash
kinit srivatsavad@CS.STANFORD.EDU
cd experiments/tfa-vs-judge
scripts/archive_runs.sh restore     # refuses to run if runs/ is already non-empty
```

Or by hand, from anywhere on the cluster:

```bash
cp -a /dfs/scratch0/srivatsavad/jfe-archive/raw/runs <your-checkout>/experiments/tfa-vs-judge/
```

Verify afterwards:

```bash
cd <your-checkout>/experiments/tfa-vs-judge
shasum -a 256 -c /dfs/scratch0/srivatsavad/jfe-archive/meta/runs.sha256
```

## Finding the data for a result

`by-experiment/` is named after the paper's own structure:

| Group | What it holds |
|---|---|
| `pools` | the shared candidate pools — 64 sampled answers per task, with exact-checker oracle labels |
| `p1-rotation` | the swap. `r4` is the **registered** headline result behind Figure 2 and the abstract's "3 to 5 points out of 10" |
| `p1-mechanism` | reference reworded, re-expressed, enciphered, masked |
| `p2-grading` | MACE, k-stratified, the MATH-500 one-answer control, rounds 2 and 8 |
| `p3-acceptance` | rounds 19/20/22/23 — the 843 / 117 / 2 take-back result |
| `cost-graders` | rounds 21/24/25/26/27 — SimpleQA and BrowseComp/HLE graders run verbatim |
| `holdout` | the frozen pre-registered holdout (registration round 32) |
| `panel2` | `v4_judge`: 6 judges × 2 pools × 5 prompt arms |
| `panel2-pool` | `v4_pool`, 329 MB. Upstream input only — no analysis producer reads it |
| `rl-mechanism` | symlinks only; the simulation, best-of-*n* and KL-tilt results are re-analyses of scores already in `p1`/`p2` |
| `ext-appendix` | synthetic-k, Ties, answer-format separation, code/MBPP, DPO |
| `controls` | padded / short / position-token reference controls |
| `stale` | **do not analyse** — see below |
| `other-papers` | not Paper D: Paper A's corruption battery (176 MB), the TFA paper, WitnessBench, SWE-bench |
| `unsorted` | loose files at the top of `runs/` and leftover pools |

A file can appear in more than one group. `runs/r2`–`r8` are single judging rounds re-read by
several experiments, and `bon/` is one flat pool directory serving about eight of them, so the
group sizes do not sum to the total.

## Two warnings

- **`stale/` (`runs/bon_scores/`) is misaligned.** `registration_round2.md` records these scores as
  not matching the Qwen MATH pool they appear to belong to. They are superseded by
  `runs/r2/frozen_math/`. They are kept for the record, not for analysis.
- **`runs/r8/*` must stay byte-exact.** `registration_round8.md` records md5 hashes for those files
  as part of a pre-registration. Re-generating them would break the registration.

## One provenance note

In `panel2`, the arm named "bare" (`rubric=r10bare`) is **not** an unmitigated prompt. The
`reference_block()` function in `scripts/v4_judge_prompts.py` is unconditional, so every arm —
including that one — appends: *"The following is one known-valid reference answer. It is not
necessarily the only valid answer."* On identical candidate texts, the same judge shows a
match-vs-differ swap of **+5.11** under the `r4`/`bon` protocol, which has no such disclaimer, and
**+1.70** under `r10bare`. For phi-4 it is +4.09 versus +0.26. Do not compare numbers across the
two protocols without accounting for this.

See `RUNNABLE.md` at the root of the repository for the full reproduction guide.
