#!/bin/bash
# All-family reproduction via the proven bash-loop pattern (no threaded Python parent, which hung vLLM's
# EngineCore on shutdown). 3 workers, one per GPU, each runs a static model group over the 6 datasets,
# skipping cells already present in any runs/* dir. timeout guards against any single-cell hang.
cd ~/tfa-vs-judge || exit 1
export HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface
set -a; . ~/.env_frontier 2>/dev/null; set +a
export PYTHONPATH=.
mkdir -p runs/all logs /dfs/scratch0/srivatsavad/jfe_raw/tokens
TOK=/dfs/scratch0/srivatsavad/jfe_raw/tokens

runworker () {   # $1=gpu, then model names
  gpu="$1"; shift
  # dataset:limit pairs
  set -- "$@"
  models=("$@")
  DS=("math500:500" "math-full:600" "gsm8k:500" "gsm8k-platinum:500" "putnam-axiom:236" "putnam-axiom-var:265")
  for model in "${models[@]}"; do
    dd=$(echo "$model" | sed 's#/#__#g')      # jsonl naming (double underscore)
    lg=$(echo "$model" | tr '/' '_')          # log naming
    for pair in "${DS[@]}"; do
      d="${pair%%:*}"; lim="${pair##*:}"
      if ls runs/*/"${d}__${dd}"*.jsonl >/dev/null 2>&1; then
        echo "[$(date +%H:%M:%S)] g$gpu SKIP $model $d" >> logs/all_progress.log; continue
      fi
      echo "[$(date +%H:%M:%S)] g$gpu START $model $d" >> logs/all_progress.log
      CUDA_VISIBLE_DEVICES="$gpu" timeout 2400 .venv/bin/python scripts/run_all.py \
        --model "$model" --dataset "$d" --limit "$lim" --no-judge --save-tokens "$TOK" --out runs/all \
        >> "logs/all_${lg}_${d}.log" 2>&1
      echo "[$(date +%H:%M:%S)] g$gpu END   $model $d rc=$?" >> logs/all_progress.log
    done
  done
  echo "[$(date +%H:%M:%S)] g$gpu WORKER DONE" >> logs/all_progress.log
}
export -f runworker; export HF_HOME PYTHONPATH TOK

nohup setsid bash -c 'runworker 1 "mistralai/Ministral-8B-Instruct-2410" "mistralai/Mistral-Small-Instruct-2409" "Qwen/Qwen2.5-Math-7B-Instruct" "deepseek-ai/deepseek-math-7b-instruct" "mistralai/Mistral-7B-Instruct-v0.3"' >/dev/null 2>&1 &
nohup setsid bash -c 'runworker 2 "microsoft/Phi-3.5-mini-instruct" "microsoft/Phi-3-medium-4k-instruct" "microsoft/phi-4" "mistralai/Mathstral-7B-v0.1"' >/dev/null 2>&1 &
nohup setsid bash -c 'runworker 3 "allenai/OLMo-2-1124-7B-Instruct" "allenai/OLMo-2-1124-13B-Instruct" "allenai/OLMo-2-0325-32B-Instruct"' >/dev/null 2>&1 &
echo "launched 3 workers on GPUs 1,2,3"
