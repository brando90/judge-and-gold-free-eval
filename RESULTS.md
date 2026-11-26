# Results

Paper-ready results for experiments 03 and 04. Every figure is a committed output. This note does not draw new samples. Self-consistency (SC) needs no gold answer, no human label, and no judge. Pass@1 needs the gold answer. Paths point at the file that stores the number.

## Experiment 03: model-level SC versus pass@1

Six instruction models, the same 500 MATH-500 problems, $n = 16$ samples (temperature $1.0$, top-p $0.95$, 1024 new tokens, seed 0). Model-level SC is the mean, over problems, of pairwise agreement of normalized answer keys. An unboxed sample scores $0$ and counts wrong. The frozen rule in [`experiments/03_model_level_ranking_sc/PREREG.md`](experiments/03_model_level_ranking_sc/PREREG.md) returns YES when the number of discordant pairs satisfies $D \le 2$ out of 15, every discordant pass@1 gap is below $0.05$, and a 2000-draw problem-cluster bootstrap has $P(D \le 3) \ge 0.80$.

**Verdict: YES.** SC orders the six models as pass@1 does, with one discordant pair: $D = 1$, Kendall $\tau = 0.867$, Spearman $\rho = 0.943$, Pearson $r = 0.997$, $P(D \le 3) = 1.00$, and the bootstrap 95% interval for $\tau$ is $[0.73, 0.87]$. Source: [`experiments/03_model_level_ranking_sc/results/results.json`](experiments/03_model_level_ranking_sc/results/results.json) (`E1.sc`, `E1.sc.pearson`, `E1_boot.sc`, `E1_verdict`) and [`experiments/03_model_level_ranking_sc/results/tables.md`](experiments/03_model_level_ranking_sc/results/tables.md).

The discordant pair is DeepSeek-Math-7B-RL (pass@1 $0.145$, SC $0.048$) versus Mistral-7B-Instruct-v0.2 (pass@1 $0.102$, SC $0.062$). The pass@1 gap is $0.043$ (exact value $0.042625$ in `E1_discordant_pairs`). The bootstrap probability that this pair matches pass@1 is $0.007$ (`E1_pair_concordance_prob`). DeepSeek-Math boxes $0.263$ of its samples (`model_level.dsmath_7b_rl.boxed`). The gap sits under the frozen line of $0.05$. The lab note flags that a format-robust gold grader could move it ([`experiments/03_model_level_ranking_sc/RESULTS.md`](experiments/03_model_level_ranking_sc/RESULTS.md)); experiment 04 measures that grader.

The boxed-rate control has $D = 4$ ($\tau = 0.467$), so the SC order carries information beyond whether a sample contains a box. Mean SCP matches SC ($D = 1$, $\tau = 0.867$). Majority@16 and pass@16, both gold-using, have $D = 0$.

SC orders models and sits below pass@1 on every model. Pearson $r(\mathrm{SC}, \mathrm{pass@1}) = 0.997$, and $\mathrm{SC} - \mathrm{pass@1}$ runs from $-0.04$ to $-0.10$ (`E2`, and the same range in the lab note). At plurality share $\mathrm{SCP} \ge 0.5$, Mistral's precision is $0.742$ on coverage $0.062$ (`E3`; `tables.md`). The pre-registered line, precision $\ge 0.90$ for every model, fails for Mistral.

| model | pass@1 | SC | boxed rate |
|---|---:|---:|---:|
| Qwen2.5-7B-Instruct | 0.721 | 0.680 | 0.910 |
| Qwen3-4B (non-thinking) | 0.702 | 0.662 | 0.767 |
| Qwen3-1.7B (non-thinking) | 0.633 | 0.580 | 0.747 |
| Llama-3.1-8B-Instruct | 0.377 | 0.281 | 0.723 |
| DeepSeek-Math-7B-RL | 0.145 | 0.048 | 0.263 |
| Mistral-7B-Instruct-v0.2 | 0.102 | 0.062 | 0.834 |

Three-decimal figures as printed in [`experiments/03_model_level_ranking_sc/results/tables.md`](experiments/03_model_level_ranking_sc/results/tables.md). Exact floats are in `results.json` under `model_level`. Figure: [`experiments/03_model_level_ranking_sc/results/model_rank.png`](experiments/03_model_level_ranking_sc/results/model_rank.png).

## Experiment 04: format-robust SC

The extractor in [`experiments/04_format_robust_sc_and_more_models/scripts/fr_extract.py`](experiments/04_format_robust_sc_and_more_models/scripts/fr_extract.py) keeps a boxed answer and otherwise falls back through a final-answer phrase, the last math expression, and a trailing number. The primary comparison applies that extractor on both sides: format-robust SC versus format-robust pass@1. Strict pass@1 is the experiment 03 target (boxed answer, else wrong). Part A re-scores the six experiment 03 sample files. Part B adds four models sampled with the same harness. Rules were frozen in [`experiments/04_format_robust_sc_and_more_models/PREREG.md`](experiments/04_format_robust_sc_and_more_models/PREREG.md) before any fallback number.

### Part A (six models, no new sampling)

**Verdict: YES.** $D = 0$ of 15, $\tau = 1.000$, Spearman $\rho = 1.000$, $P(D \le 3) = 1.00$. The stored bootstrap 95% interval for $\tau$ is $[0.866667, 1.0]$ (`A.primary_scfr_vs_p1fr.tau_ci` in [`experiments/04_format_robust_sc_and_more_models/results/results.json`](experiments/04_format_robust_sc_and_more_models/results/results.json)).

DeepSeek-Math-7B-RL versus Mistral-7B-Instruct-v0.2 is concordant. Format-robust SC is $0.494$ versus $0.069$ (strict SC was $0.048$ versus $0.062$). Format-robust pass@1 is $0.506$ versus $0.105$ (strict pass@1 was $0.145$ versus $0.102$). The bootstrap probability of concordance is $1.00$ (`flip_dsmath_vs_mistral.sc_fr_vs_p1_fr`). The phrase tier covers $0.66$ of DeepSeek-Math-7B-RL samples (`tables.md`), which is why strict scoring had placed it last among the gold-free metrics.

### Part B (ten models)

**Verdict: YES** under the Part B rule: $\tau \ge 0.80$, every discordant format-robust pass@1 gap below $0.05$, and $P(\tau \ge 0.733) \ge 0.80$. The estimate is $D = 1$ of 45, $\tau = 0.956$, Spearman $\rho = 0.988$, bootstrap 95% interval $[0.87, 1.00]$ ([`experiments/04_format_robust_sc_and_more_models/RESULTS.md`](experiments/04_format_robust_sc_and_more_models/RESULTS.md); stored `tau_ci` is $[0.866667, 1.0]$), and $P(\tau \ge 0.733) = 1.00$. The problem-cluster probability $P(D \le 3)$ is $0.9985$ (`B.primary_scfr_vs_p1fr.boot_P_D_le_3`), printed as $1.00$ in `tables.md`.

The discordant pair is Qwen3-4B versus Qwen3-8B, both non-thinking: format-robust pass@1 $0.710$ versus $0.714$ (gap $0.004$; exact gap $0.00425$), format-robust SC $0.680$ versus $0.678$ (`tables.md`; `B.primary_scfr_vs_p1fr.discordant`).

Over the ten models, Pearson $r = 0.995$ between format-robust SC and format-robust pass@1, and format-robust SC reads $0.012$ to $0.089$ below format-robust pass@1 ([`experiments/04_format_robust_sc_and_more_models/RESULTS.md`](experiments/04_format_robust_sc_and_more_models/RESULTS.md); per-model values in `results.json` `table`). Four pairs have a format-robust pass@1 gap below $0.05$, and three of those four are concordant (`close_pairs_all` in `results.json`, listed in `tables.md`).

| model | pass@1 strict | pass@1 fr | SC strict | SC fr | boxed | phrase | cut at 1024 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen2.5-7B-Instruct | 0.721 | 0.724 | 0.680 | 0.686 | 0.91 | 0.00 | 0.09 |
| Qwen3-8B (non-thinking) | 0.705 | 0.714 | 0.661 | 0.678 | 0.76 | 0.01 | 0.25 |
| Qwen3-4B (non-thinking) | 0.702 | 0.710 | 0.662 | 0.680 | 0.77 | 0.01 | 0.24 |
| Qwen3-1.7B (non-thinking) | 0.633 | 0.640 | 0.580 | 0.595 | 0.75 | 0.01 | 0.26 |
| Qwen3.5-4B (non-thinking) | 0.537 | 0.571 | 0.482 | 0.520 | 0.55 | 0.00 | 0.45 |
| DeepSeek-Math-7B-RL | 0.145 | 0.506 | 0.048 | 0.494 | 0.26 | 0.66 | 0.08 |
| DeepSeek-Math-7B-Instruct | 0.412 | 0.413 | 0.345 | 0.346 | 0.96 | 0.00 | 0.03 |
| Llama-3.1-8B-Instruct | 0.377 | 0.397 | 0.281 | 0.308 | 0.72 | 0.01 | 0.00 |
| Llama-3-8B-Instruct | 0.237 | 0.239 | 0.160 | 0.164 | 0.96 | 0.01 | 0.03 |
| Mistral-7B-Instruct-v0.2 | 0.102 | 0.105 | 0.062 | 0.069 | 0.83 | 0.02 | 0.14 |

Rows and rounding as printed in [`experiments/04_format_robust_sc_and_more_models/results/tables.md`](experiments/04_format_robust_sc_and_more_models/results/tables.md). Figure: [`experiments/04_format_robust_sc_and_more_models/results/model_rank.png`](experiments/04_format_robust_sc_and_more_models/results/model_rank.png).

| comparison | Part A | Part B |
|---|---|---|
| SC fr vs pass@1 fr (primary) | $0/15$, YES | $1/45$, YES |
| SC fr vs pass@1 strict | $1/15$, NO (max gap $0.232$) | $4/45$, NO (max gap $0.267$) |
| SC strict vs pass@1 strict | $1/15$, YES (gap $0.043$) | $2/45$, YES (gap $0.043$) |
| S1, fallback off when cut at 1024 | $0/15$, YES | $2/45$, YES (max gap $0.032$) |
| S2, boxed and phrase tiers only | $0/15$, YES | $2/45$, YES (max gap $0.033$) |

Source for this block: the Part A and Part B tables in [`experiments/04_format_robust_sc_and_more_models/results/tables.md`](experiments/04_format_robust_sc_and_more_models/results/tables.md). S1's extra discordant pair on the ten-model set is DeepSeek-Math-7B-RL versus Qwen3.5-4B.

### Scope of the claim

The primary YES uses the same extractor on the candidate and on the target. Against strict pass@1, format-robust SC is a NO on both parts, because strict pass@1 leaves DeepSeek-Math-7B-RL at $0.145$ while the fallback scores it at $0.506$. Qwen3.5-4B has $0.45$ of its samples cut at 1024 tokens, so its fallback answers include mid-reasoning guesses; S1 and S2, which drop those guesses, stay YES and add that one pair. An independent recompute matches `analyze.py` to $10^{-15}$ on all ten models ([`experiments/04_format_robust_sc_and_more_models/results/indep_check.json`](experiments/04_format_robust_sc_and_more_models/results/indep_check.json)). The ranking is one benchmark (MATH-500), $n = 16$, and final-answer tasks. The proposed next run is [`NEXT.md`](NEXT.md).
