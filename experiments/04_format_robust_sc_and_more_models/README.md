# Experiment 04: format-robust SC re-rank, then more models inside the pass@1 gaps (2026-11-25)

Follows experiment 03 (model-level SC ranking vs pass@1; one discordant pair, DeepSeek-Math-7B-RL vs Mistral-7B, where
DeepSeek-Math boxes only 26% of answers and SC counts an unboxed answer as 0).

Paper-ready verdict (numbers only from `results/`): **Part A YES**, $D = 0$ of 15. **Part B YES**, $D = 1$ of 45, $\tau = 0.956$, discordant gap $0.004$. Joint writeup: [`../../RESULTS.md`](../../RESULTS.md). Lab record: [`RESULTS.md`](RESULTS.md).

- Part A (no new sampling): answer extraction falls back to the last math expression when there is no `\boxed{}`
  (`scripts/fr_extract.py`). Re-rank the 6 experiment-03 models by format-robust SC; does DeepSeek-Math vs Mistral become concordant?
- Part B (new sampling): add 4 models whose pass@1 should sit inside the existing gaps, same harness as experiment 03.

Files: `PREREG.md` (frozen before sampling or any fallback number), `scripts/` (generate.py, fr_extract.py, run_gen.sh, analyze.py),
`results/` (gen/, results.json, tables.md, figure), `RESULTS.md`.
