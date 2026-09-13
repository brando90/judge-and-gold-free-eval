# Round-8 registration (R8-A), written and committed BEFORE any of its pools is judged

Motivation: the external review of the round-7 draft (not included in the supplement) noted that Claude Sonnet 5, the frontier judge on page 1, was scored only on correct answers, so its grading accuracy (AUROC) and selection accuracy could not be computed. R8-A scores subsamples that include wrong answers, blind and referenced, through the same command-line interface as R3-B and R5-A.

Context disclosed before any R8-A call: a post hoc relabeling of the constructed pools with a format-lenient checker (`papers/analysis/r8_lenient_labels.py`, commit ce4f899) and its re-analysis for the open judges and GPT-4.1 (`r8_lenient_analysis.py`) had already been run. Under lenient labels, those judges' grading of correct non-matching answers still gets worse with the reference, and the best-of-64 selection loss survives for Qwen2.5-7B but mostly not for other judges. No Sonnet 5 score for a wrong answer existed before this registration.

Harness (committed with this file): `experiments/tfa-vs-judge/scripts/sonnet_cli_pool.py`. Pools (built before this file, by `scripts/r8_build_sonnet_pools.py`, which reads candidate text and labels only): `runs/r8/sonnet_{repl,mace,kpool}.jsonl`. Producer (frozen, committed with this file): `papers/analysis/r8_sonnet_analysis.py`. Intervals: task-level bootstrap, 1,000 resamples, numpy default_rng(0). Verdicts: **confirmed** when the interval excludes zero in the predicted direction, **falsified** when it excludes zero in the opposite direction, **not confirmed** otherwise, as in `registration_round4.md`.

## R8-A. Sonnet 5 grading and selection with wrong answers included

**Pools.** 16 of each task's 64 Llama-3.1-8B samples, drawn at random and redrawn until the subsample holds at least one matching-correct, one non-matching-correct, and one wrong sample (numpy default_rng(8)).
- `repl`: 40 replication-pool tasks, 8 per constraint family, with lenient pass rate in [0.2, 0.8]; 640 candidates.
- `mace`: 40 MACE River and Language tasks with k > 1 and pass rate in [0.05, 0.95]; 640 candidates.
- `kpool`: all 22 eligible k-pool tasks with k > 1 and lenient pass rate in [0.2, 0.8]; 352 candidates.

Pool and label files are not tracked by git (runs/ is ignored); their md5 hashes at registration:
- `runs/r8/sonnet_repl.jsonl` 4d7f8b6e4739f0bbff5c5e1de72b13d3
- `runs/r8/sonnet_mace.jsonl` 3382472341d573884a0a46b9141fb4cb
- `runs/r8/sonnet_kpool.jsonl` 9809c9a2f172bc5f7c6b4e8de0a8f35f
- `runs/r8/lenient_repl.jsonl` 9d7f1d32d5ac4c4332c1f93088a49944
- `runs/r8/lenient_kpool.jsonl` f797c999ad5b9a10a8dac9fa3d141789

Labels: format-lenient (primary) and registered strict labels (secondary) for `repl` and `kpool`; the registered MACE oracle for `mace`. "Matching" means the candidate's extracted answer equals the reference's (constructed pools) or its boxed answer or last 200 characters equals or contains the reference (MACE, as in `r7_posthoc.py`).

**Interface.** Identical to R5-A FAST: `claude -p --model claude-sonnet-5` with the subscription login and no API key, `--system-prompt` set to rubric a (blind or referenced version, ending "Respond with only the integer score."), no tools, `--strict-mcp-config`, `--setting-sources ""`, `alwaysThinkingEnabled: false`, an empty working directory. The last integer from 0 to 10 in the reply is the score.

**Order.** Pools run in the order repl, mace, kpool. Within a pool, calls go task by task, and each candidate is scored blind and referenced before the next candidate. Four workers. Failed calls are retried twice, then recorded as missing and counted. If the subscription's usage limit interrupts the run, the run resumes after the limit clears. A pool with fewer than 20 tasks whose 32 calls all returned a score by 20 September 2026 is recorded as not scored.

**Readouts, per pool (referenced minus blind, per task).**
- *G_nm*: AUROC of the score for separating non-matching correct answers from wrong answers.
- *G_all*: AUROC for all correct answers against wrong answers.
- *FR*: share of non-matching correct answers scored 3 or below.
- *Margin*: mean score of matching minus non-matching correct answers.
- *Best-of-16 accuracy*, ties averaged, and the accuracy of the rule that takes the higher of the blind and referenced scores, both minus blind accuracy.

**Predictions.**
- **P-R8A1.** repl: G_nm < 0.
- **P-R8A2.** repl: FR > 0.
- **P-R8A3.** mace: G_nm < 0.
- **P-R8A4.** mace: FR > 0.
- **P-R8A5.** kpool: G_nm < 0.
- **P-R8A6** (manipulation check). repl: margin > 0.

No prediction for G_all, best-of-16 accuracy, or the max rule; they are reported for every pool that is scored.

---

## Amendment 1 (2026-09-13, committed before any R8-A API call)

**What happened.** The CLI run stopped when the subscription reached its monthly spend limit (about 07:58). By then 939 of the 1,280 replication-pool calls had returned a score, 118 had failed with the limit error, and the MACE and k-pool pools had not started. The harness was stopped.

**Disclosure.** Before this amendment, we ran the frozen producer on the partial CLI replication data (24 tasks with all 32 calls scored) and saw its readouts: non-matching AUROC change −0.076 [−0.116, −0.043], false-rejection change +0.231, margin change +3.34, best-of-16 accuracy change −0.006. No other R8-A readout was seen.

**Change.** With the account owner's authorization to use the metered API key, every R8-A call, including the 939 already made through the CLI, is re-run through the Anthropic Messages API, so all confirmatory readouts come from one interface:
- harness `experiments/tfa-vs-judge/scripts/sonnet_api_pool.py` (committed with this amendment), output `runs/r8/sonnet_api/{pool}.jsonl`;
- `model="claude-sonnet-5"`, `thinking={"type": "disabled"}` (Sonnet 5 otherwise thinks adaptively by default, and the CLI arm ran with thinking off), no sampling parameters (API defaults), `max_tokens=512`;
- the same system prompt (rubric a, blind or referenced) and the same user message as the CLI harness; the score is the last integer from 0 to 10 in the text reply;
- same pools, same order (task by task, both conditions per candidate), eight workers, SDK retries, a spend cap of USD 40.

**Unchanged.** Pools and their hashes, labels, readouts, predictions P-R8A1 to P-R8A6, verdict rule, and the completion rule (a pool with fewer than 20 fully scored tasks by 20 September 2026 is not scored).

**Producer.** `papers/analysis/r8_sonnet_analysis.py` gains `--scores` (default `runs/r8/sonnet_api`) and `--out` arguments and no other change. Confirmatory results: `r8_sonnet_results.json` from the API files. The partial CLI run is reported separately (`r8_sonnet_cli_partial.json`) with no verdicts, together with the per-call agreement between CLI and API scores on the calls both interfaces completed (post hoc).
