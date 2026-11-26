# Next experiment

One run: take the ten models and the format-robust extractor from experiment 04 onto GSM8K, and apply the Part B decision rule unchanged. Experiments 03 and 04 already answer the MATH-500 ranking question, including the strict-target comparison and the truncation sensitivities in [`experiments/04_format_robust_sc_and_more_models/results/tables.md`](experiments/04_format_robust_sc_and_more_models/results/tables.md). Both lab notes limit the claim to MATH-500. GSM8K is the benchmark where reference-anchored teacher-forced accuracy in this repo reverses (cross-family Spearman $-0.37$ on GSM8K, root [`README.md`](README.md)), and it is where pass rates compress, the regime of experiment 04's only discordant pair (Qwen3-4B vs Qwen3-8B, format-robust pass@1 gap $0.004$).

## Experiment 05: format-robust SC on GSM8K

**Question.** On the GSM8K test split, does format-robust SC rank the same ten models as format-robust pass@1?

**What stays fixed.** The ten model ids in [`experiments/04_format_robust_sc_and_more_models/results/results.json`](experiments/04_format_robust_sc_and_more_models/results/results.json) (`models`). The sampler from experiment 04: temperature $1.0$, top-p $0.95$, max tokens $1024$, seed $0$, $n = 16$, Qwen3 and Qwen3.5 in non-thinking mode, the boxed-answer prompt used on MATH-500. The extractor [`experiments/04_format_robust_sc_and_more_models/scripts/fr_extract.py`](experiments/04_format_robust_sc_and_more_models/scripts/fr_extract.py), unmodified. The Part B rule in [`experiments/04_format_robust_sc_and_more_models/PREREG.md`](experiments/04_format_robust_sc_and_more_models/PREREG.md):

- YES: Kendall $\tau \ge 0.80$, every discordant format-robust pass@1 gap $< 0.05$, and $P(\tau \ge 0.733) \ge 0.80$.
- NO: $\tau < 0.60$, or any discordant gap $\ge 0.10$.
- INCONCLUSIVE otherwise.

Bootstrap: 2000 resamples of problems, one resample shared by all models. The script records its seed before the run. Problems: the full GSM8K test split, fixed before any sample is drawn. The preregistration records the item count from the loader at commit time.

**Primary endpoint.** Format-robust SC versus format-robust pass@1, same extractor on both sides, gold checked as in experiment 04 (Math-Verify on the extracted answer; unextractable counts wrong).

**Secondary endpoint, same rule, reported beside the primary.** Format-robust SC versus official GSM8K accuracy: exact match of the extracted answer to the gold string after the dataset's `####` marker, with the same normalization the GSM8K grader uses, and unextractable counted wrong. The secondary asks whether the order survives the benchmark's own grader. It does not edit the primary verdict.

**Sensitivities, descriptive.** S1 and S2 from the experiment 04 preregistration: no fallback on samples cut at 1024 tokens; boxed and phrase tiers only. Report the per-model truncation rate. On MATH-500, Qwen3.5-4B was cut on $0.45$ of samples (`tables.md` in experiment 04).

**Reading the outcome.** A YES on the primary, with the secondary also YES or with every secondary discordant gap below $0.05$, is the result that carries the ranking claim off MATH-500. A NO on either endpoint, or a secondary discordant gap of $0.10$ or more, leaves the claim on final-answer competition math under a boxed prompt.

**Freeze before sampling.** Write `experiments/05_gsm8k_format_robust_sc/PREREG.md` with this protocol and commit it before any GSM8K generation and before any GSM8K fallback number. Scope of that folder is this benchmark change: the model list, the extractor, and the Part B thresholds stay as written above.
