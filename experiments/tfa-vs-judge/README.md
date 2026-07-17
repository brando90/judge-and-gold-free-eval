# TFA vs. the most-capable LLM judge — the crux experiment

**TL;DR.** The single highest-leverage, fastest-to-finish risk in judge-free-eval:
*does Teacher-Forced Accuracy (TFA) correlate with a frontier LLM judge's rating of
reasoning quality — **beyond** what free boxed-answer correctness already gives you?*
If yes, TFA is a validated judge replacement in the gold-reference regime. If no, TFA
is "just a cheaper exact-match" (an informative negative). We test this on **MATH-500
first** (the reproduction anchor, canonical solutions minimize the alternate-proof
confound), then GSM8K.

The published TFA result ([Putnam-AXIOM, arXiv:2508.08292](https://arxiv.org/abs/2508.08292))
only validated TFA against **boxed final-answer accuracy** (0.66±0.02 on MATH). It was
**never** checked against a judge or humans. This experiment closes exactly that gap.

## The one number that decides
`partial rho(TFA, judge | boxed-correct)` — item-level Spearman with a bootstrap CI.
- **GREEN** (CI lower bound > 0.05): TFA carries reasoning-quality signal beyond the free
  correctness bit → proceed to the shortcut/exposure-bias control (is it real or gold-copying?).
- **NEGATIVE** (CI upper bound < 0.05): TFA ≈ cheaper exact-match. Publishable, scopes the limit.
- **INCONCLUSIVE** (CI straddles 0): add items/models.

We also report raw `rho(TFA,judge)`, `rho(TFA,correct)`, `rho(judge,correct)`, correct-only
and wrong-only correlations, and the model-level `mean-TFA vs mean-judge` (Putnam-style).

## Architecture
```
tfa/core.py        backend-agnostic TFA scoring (argmax / logprob / BPC)  [unit-tested]
tfa/analyze.py     Spearman/Pearson, partial correlation, bootstrap CIs   [unit-tested]
tfa/boxed.py       \boxed / #### extraction + correctness (math_verify)    [unit-tested]
tfa/data.py        MATH-500 / GSM8K / Putnam loaders (gold trace + answer)
tfa/backends/hf.py         ground-truth teacher forcing (reference impl)
tfa/backends/vllm_backend.py  throughput via prompt_logprobs
tfa/freegen.py     free-generate the model's own trace (judged + boxed-scored)
tfa/judge.py       frontier API judge (litellm), reasoning-quality rubric
scripts/verify_backends.py  E0: assert vLLM == HF on a toy
scripts/run_all.py          one model x one dataset -> per-item JSONL
scripts/analyze_crux.py     aggregate -> the crux report + verdict
```

## Run it on SNAP
Pick a free GPU box from the [SNAP GPU stats](https://ilwiki.stanford.edu/doku.php?id=snap-servers:snap-gpu-servers-stats).
Work under `/lfs` (NFS root-squash blocks writes elsewhere), use `krbtmux` + reauth for long runs.

```bash
# 0. env on /lfs (not AFS)
cd /lfs/$(hostname)/0/$USER && git clone https://github.com/brando90/judge-free-eval.git
cd judge-free-eval/experiments/tfa-vs-judge
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
export OPENAI_API_KEY=...   # or the provider key for --judge-model

# 1. E0 — trust the metric: vLLM must match HF ground truth (once per model family)
PYTHONPATH=. python scripts/verify_backends.py --model Qwen/Qwen2.5-0.5B-Instruct   # expect PASS

# 2. Run the capability ladder on MATH-500 (one process per model; 7B/32B fit 1 GPU, 72B needs --tp)
#    WEB-SEARCH the current SOTA judge id first and pass it as --judge-model.
for M in Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-32B-Instruct meta-llama/Llama-3.1-8B-Instruct \
         meta-llama/Llama-3.3-70B-Instruct deepseek-ai/DeepSeek-R1-Distill-Qwen-7B; do
  PYTHONPATH=. python scripts/run_all.py --model "$M" --dataset math500 --limit 500 \
      --judge-model openai/gpt-5.2 --tp 1 --out runs/math500
done

# 3. The verdict
PYTHONPATH=. python scripts/analyze_crux.py 'runs/math500/*.jsonl' --out runs/math500_crux.json
```

## Models (span capability so TFA has variance)
Qwen2.5-{7B,32B,72B}-Instruct, Llama-3.1-8B / Llama-3.3-70B-Instruct, a reasoning-distilled
model (DeepSeek-R1-Distill). Weak models floor out on next-token prediction (why the paper
skipped Putnam) — the ladder is deliberate so we can see where TFA gains resolution.

## Judge
One frontier API model for the first cut (per decision). **Web-search the current SOTA id
before running** — don't hardcode. A second judge family (self-preference control) is E3,
paid for only if the crux clears.

## Deliberately deferred (don't build until the crux clears)
Human ratings (T2), the mandatory shortcut/exposure-bias control, the multi-reference variant,
Putnam-AXIOM (+contamination), and the VeriBench/Lean formal-spec track. All are conditional
on a positive partial-correlation signal here.

## Local dev (no GPU)
The correctness-critical logic is unit-tested without a GPU:
```bash
PYTHONPATH=. uv run --with numpy --with scipy --with pytest --python 3.12 pytest tests/ -q
```
