# 02 gold-free, judge-free self-consistency (pilot)

Dated 2026-11-24. First experiment toward Brando's goal: a metric that replaces the gold reference /
target metrics (human labels, boxed accuracy, pass@k) and is trustworthy (passes falsifiable sanity
properties, not only a correlation). Replacing LLM judges is a bonus.

- Candidate: **self-consistency agreement (SC)**: how often a sample's final answer matches the model's
  other samples on the same problem. No judge, no gold answer, no human label.
- Rivals: four Qwen no-reference judges. Context: four Qwen reference judges (they see the gold), gold
  boxed correctness, pass@k.
- Data: committed runs only (Llama-3.1-8B, 64 samples x 500 MATH-500 problems). No model calls.
- Files: `PREREG.md` (committed before any run), `scripts/run_pilot.py`, `results/`, `results_v2_normalized/`, `results_run1_timeout1s/` (json, tables, figures),
  `RESULTS.md` (verdict and numbers).
- Reproduce: `python3 -m venv ~/.venvs/jfe && ~/.venvs/jfe/bin/pip install math-verify numpy scipy matplotlib`,
  then `~/.venvs/jfe/bin/python experiments/02_gold_free_self_consistency/scripts/run_pilot.py` (CPU, minutes).
- Next (3 days): model-level ranking: does SC rank several models like gold accuracy does? Needs several
  models' samples on the same problems (a generation job on Brando's plan accounts).
