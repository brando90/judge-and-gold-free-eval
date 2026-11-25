# 03 model-level ranking by self-consistency (SC) vs gold accuracy

Dated 2026-11-25. Follows 02 (item-level SC on one model). Goal block (Brando, 2026-11-24): a metric that replaces the gold
reference metrics (human labels, boxed accuracy, pass@k) and is trustworthy; replacing judges is a bonus.

- Question: does SC (no gold, no human, no judge) rank 6 models on the same 500 MATH-500 problems like gold pass@1?
  Plus two audits from 02's review: the argmax-picks-unboxed-sample case, and canonical keys vs pairwise Math-Verify.
- Files: `PREREG.md` (committed before any sampling), `scripts/generate.py` + `scripts/run_gen.sh` (vLLM sampling, 5 new
  models, n = 16, GPU host), `scripts/analyze.py` (all numbers, CPU), `results/` (json, tables, figures), `RESULTS.md`.
- Data: 5 new models sampled here (`results/gen/`), Llama-3.1-8B from the committed 02 data.
- Reproduce: generation `bash scripts/run_gen.sh` on a vLLM host with `bon_math_tasks.jsonl` and `generate.py` in `~/jfe03`;
  analysis `~/.venvs/jfe/bin/python experiments/03_model_level_ranking_sc/scripts/analyze.py` (math-verify, numpy, scipy, matplotlib).
