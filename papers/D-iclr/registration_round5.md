# Round-5 registration (R5-A), written and committed BEFORE any of its pool is judged

Motivation: the external review of the round-4 draft (not included in the supplement) asked whether a frontier judge with extended thinking still anchors on factual questions it cannot check by calculation. The open-model answer (Qwen3-8B, Qwen3-14B) is that thinking roughly halves the effect. R3-B tests Sonnet 5 on the arithmetic rotation pool; this experiment tests it on MACE.

Harness (committed with this file): `experiments/tfa-vs-judge/scripts/r5_build_sonnet_mace.py`, `sonnet_cli_mace.py`. Producer (frozen, committed with this file): `papers/analysis/r5_sonnet_mace_analysis.py`. Intervals: task-level bootstrap, 1,000 resamples, numpy default_rng(0). Verdict vocabulary as in `registration_round4.md`.

## R5-A. Sonnet 5, score-only versus thinking, on factual MACE questions

**Pool.** `runs/r5/sonnet_mace.jsonl`, built by `r5_build_sonnet_mace.py`:
- source: `runs/r3/macesub.jsonl` (MACE River and Language, k > 1, tasks with both matching and non-matching correct samples);
- 40 tasks drawn with default_rng(5) from those that also have a wrong sample;
- per task, the first listed matching-correct, non-matching-correct, and wrong sample.

**Interface.** Identical to R3-B (`registration_round3b.md`): `claude -p --model claude-sonnet-5` with the subscription login, no API key, `--system-prompt` replacing the default prompt, no tools, `--strict-mcp-config`, `--setting-sources ""`, an empty working directory.

**Arms and conditions.**
- **FAST:** rubric a verbatim, ending "Respond with only the integer score."; `alwaysThinkingEnabled: false`.
- **THINK:** rubric a with the "Think it through ... Score: N" tail; `alwaysThinkingEnabled: true`.
- Each arm runs blind (noref) and referenced (ref), in this order: FAST noref, FAST ref, THINK noref, THINK ref.
- Calls start only after the R3-B runs finish.
- Unparseable replies and CLI errors are excluded and counted.

**Readouts, per arm.**
- *Margin increase*: per task, (matching minus non-matching score, referenced) minus the same difference blind.
- *False-rejection change*: per task, whether the non-matching correct answer is scored ≤ 3 with the reference, minus blind.
- *Blind verification*: per task, the share of the two correct samples scored above the wrong one blind (ties count half).
- *Paired THINK minus FAST margin increase*, reported without prediction.

**Predictions.**
- **P-R5A1.** FAST: margin increase > 0, CI excluding zero.
- **P-R5A2.** THINK: margin increase > 0, CI excluding zero.
- **P-R5A3.** THINK margin increase is smaller than FAST's (point estimates).

If the subscription's usage limit interrupts the run, predictions without complete data are recorded as not scored, as in R3-B.
