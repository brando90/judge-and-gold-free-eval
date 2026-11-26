# PREREG: experiment 05, format-robust SC on GSM8K

Dated 2026-11-26 (Thu), written and committed BEFORE any GSM8K generation and before any GSM8K
fallback number (SC_fr, pass@1_fr, official GSM8K accuracy, tier shares, truncation rates).
Protocol is the one in [`NEXT.md`](../../NEXT.md) at commit 8dfb556. The model list, the extractor,
and the Part B thresholds stay as written there. This folder is that benchmark change and nothing else.

## Question

On the GSM8K test split, does format-robust SC rank the same ten models as format-robust pass@1?

## What stays fixed

The ten model ids, in the order of [`experiments/04_format_robust_sc_and_more_models/results/results.json`](../04_format_robust_sc_and_more_models/results/results.json) (`models`):

| id | label | Hugging Face id |
|---|---|---|
| llama31_8b | Llama-3.1-8B-Instruct | meta-llama/Llama-3.1-8B-Instruct |
| qwen25_7b | Qwen2.5-7B-Instruct | Qwen/Qwen2.5-7B-Instruct |
| qwen3_4b | Qwen3-4B (non-thinking) | Qwen/Qwen3-4B |
| qwen3_1p7b | Qwen3-1.7B (non-thinking) | Qwen/Qwen3-1.7B |
| dsmath_7b_rl | DeepSeek-Math-7B-RL | deepseek-ai/deepseek-math-7b-rl |
| mistral_7b | Mistral-7B-Instruct-v0.2 | mistralai/Mistral-7B-Instruct-v0.2 |
| qwen3_8b | Qwen3-8B (non-thinking) | Qwen/Qwen3-8B |
| qwen35_4b | Qwen3.5-4B (non-thinking) | Qwen/Qwen3.5-4B |
| llama3_8b | Llama-3-8B-Instruct | meta-llama/Meta-Llama-3-8B-Instruct |
| dsmath_7b_inst | DeepSeek-Math-7B-Instruct | deepseek-ai/deepseek-math-7b-instruct |

The sampler from experiment 04: temperature $1.0$, top-p $0.95$, max tokens $1024$, seed $0$, $n = 16$.
Qwen3 and Qwen3.5 in non-thinking mode (`enable_thinking=False` when the id contains `Qwen3`).
The boxed-answer prompt used on MATH-500:

> Solve the following math problem. Show your reasoning step by step, then give the final answer in \boxed{}.

The extractor [`experiments/04_format_robust_sc_and_more_models/scripts/fr_extract.py`](../04_format_robust_sc_and_more_models/scripts/fr_extract.py), unmodified.
Answer keys and gold checks for the primary endpoint are experiment 04's: normalised canonical key and
Math-Verify `verify(parse(gold), parse(answer))` via experiment 03's `gold_ok`. An unextractable sample
(tier `none`) counts as no answer: SC 0 and wrong.

The Part B rule in [`experiments/04_format_robust_sc_and_more_models/PREREG.md`](../04_format_robust_sc_and_more_models/PREREG.md), unchanged:

- YES: Kendall $\tau \ge 0.80$, every discordant format-robust pass@1 gap $< 0.05$, and $P(\tau \ge 0.733) \ge 0.80$.
- NO: $\tau < 0.60$, or any discordant gap $\ge 0.10$.
- INCONCLUSIVE otherwise.

Ties are not discordant. $\tau$ is Kendall $\tau$-b (`scipy.stats.kendalltau`), and a NaN $\tau$ is read as $0$
(experiment 03's `tau`). The bootstrap probability uses the same cutoff literal as experiment 04, $0.733$.

## Bootstrap

2000 resamples of problems, one resample shared by all models. The script's seed is $20261126$.
`scripts/analyze_gsm8k.py` writes that seed to `bootstrap_seed.json` before it draws any resample and before it
computes any fallback number.

## Problems

The full GSM8K test split, fixed before any sample is drawn. The loader is
[`experiments/tfa-vs-judge/tfa/data.py`](../tfa-vs-judge/tfa/data.py) (`load_problems("gsm8k")`:
`openai/gsm8k`, config `main`, split `test`). At commit time that loader returned **1319** items
(dataset revision `740312add88f781978c0658806c59bc2815b9866`).

sha256 of `problem_id`, question, and the loader's gold answer (the string after `####`, stripped, thousands
commas removed), in loader order, separated by NUL and newline:

`2ab55b8ba24d95e56625bf32c8be06010990fce4b0f4c08bb44d289f68cfb587`

`scripts/generate_gsm8k.py` loads that revision, checks the count and the hash, and does not sample if either differs.
Every gold string in this split is an integer. The task file is written before the first `LLM` is constructed.

## Primary endpoint

Format-robust SC versus format-robust pass@1, same extractor on both sides, gold checked as in experiment 04
(Math-Verify on the extracted answer; unextractable counts wrong). Item SC is the fraction of the other $n-1$
samples with the same normalised key. Model SC is the mean over the 1319 problems. pass@1 is the mean of the
gold checks. The first 16 samples are used, in the order generated.

## Secondary endpoint, same rule, reported beside the primary

Format-robust SC versus official GSM8K accuracy: exact match of the extracted answer to the gold string after
the dataset's `####` marker, with the same normalization the GSM8K grader uses, and unextractable counted wrong.

The grader is OpenAI `grade_school_math/dataset.py` `extract_answer`: take the match of
`#### (\-?[0-9\.\,]+)`, strip it, and delete thousands commas. Gold is that value (the loader's `gold_answer`,
which matches `extract_answer` on every test item). The prediction is the format-robust extraction, then the
same strip-and-delete-commas step, then exact string equality. No Math-Verify on this endpoint. The secondary
asks whether the order survives the benchmark's own grader. It does not edit the primary verdict.

## Sensitivities, descriptive

S1 and S2 from the experiment 04 preregistration. They do not set the verdict.

- S1: no fallback on samples cut at 1024 tokens. A sample with `finish_reason` `length` whose tier is not `boxed` counts unextractable. A boxed sample cut at 1024 tokens stays. A missing finish field counts as `stop`, as in experiment 04.
- S2: boxed and phrase tiers only. Tiers `math` and `number` count unextractable.

Report the per-model truncation rate, the share of samples with `finish_reason` `length`. On MATH-500, Qwen3.5-4B was cut on $0.45$ of samples.

## Reading the outcome

A YES on the primary, with the secondary also YES or with every secondary discordant gap below $0.05$, is the result that carries the ranking claim off MATH-500. A NO on either endpoint, or a secondary discordant gap of $0.10$ or more, leaves the claim on final-answer competition math under a boxed prompt.

The verdict fields are written only when all ten models have 16 samples on all 1319 frozen items. A partial run keeps the descriptive table and sets the verdicts to null.

## Sampling host

Local vLLM only, no paid API. SNAP `mercury2`, ten RTX A4000 16 GB GPUs. Logs, the frozen task file, and the sample files go under `/lfs/mercury2/0/brando9/judge-free-eval-exp05/`.

7B and 8B models use tensor parallel 2 so the weights fit in 16 GB. Qwen3-1.7B, Qwen3-4B, and Qwen3.5-4B use one GPU. Qwen3-1.7B is not a 7B model. dtype bfloat16, `max_model_len` 4096, `gpu_memory_utilization` 0.90, eager mode (no CUDA-graph capture on these cards), and a batch of 4 problems. Those are memory settings. The sampling parameters above are the ones from experiment 04. `run_mercury2.sh` is the launch script.

## Deviations

Any change after this commit is listed under "Deviations" in RESULTS.md with its reason. The frozen rules above are not edited.
