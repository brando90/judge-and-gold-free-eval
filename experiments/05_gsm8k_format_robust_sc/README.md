# Experiment 05: format-robust SC on GSM8K

Protocol in [`PREREG.md`](PREREG.md), frozen before any GSM8K sample or fallback number. The question and the Part B rule are [`../../NEXT.md`](../../NEXT.md) at commit 8dfb556. The ten models, the extractor, and the thresholds are experiment 04's.

This commit does not sample GSM8K and does not report a fallback number. Generation is local vLLM on SNAP `mercury2` (no paid API).

- `scripts/generate_gsm8k.py` samples $n = 16$ at temperature 1.0, top-p 0.95, 1024 tokens, seed 0, with the MATH-500 boxed prompt. Qwen3 and Qwen3.5 run in non-thinking mode. It refuses to sample if the test split is not the frozen 1319 items.
- `scripts/analyze_gsm8k.py` applies the Part B rule. Primary target: format-robust pass@1 (Math-Verify). Secondary target: official GSM8K exact match. CPU only.
- `scripts/run_mercury2.sh` schedules the ten models on 10 RTX A4000 16 GB GPUs. 7B and 8B models use two-GPU tensor parallel. Logs and samples go to `/lfs/mercury2/0/brando9/judge-free-eval-exp05/`.

From the repo root on mercury2:

```bash
tmux new-session -d -s exp05 'bash experiments/05_gsm8k_format_robust_sc/scripts/run_mercury2.sh'
```

After the samples exist:

```bash
python3 experiments/05_gsm8k_format_robust_sc/scripts/analyze_gsm8k.py
```

CPU checks, synthetic fixtures only: `python3 -m pytest experiments/05_gsm8k_format_robust_sc/tests`.
