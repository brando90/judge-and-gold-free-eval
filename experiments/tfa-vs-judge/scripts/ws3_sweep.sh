#!/bin/bash
# WS3: Omni-MATH (IMO-hard) across a capability spread, boxed accuracy. Fixed pipeline (os._exit in run_all
# + per-cell GPU cleanup). 3 GPU workers.
cd ~/tfa-vs-judge || exit 1
export HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface
set -a; . ~/.env_frontier 2>/dev/null; set +a
export PYTHONPATH=.
mkdir -p runs/ws3 logs /dfs/scratch0/srivatsavad/jfe_raw/tokens
TOK=/dfs/scratch0/srivatsavad/jfe_raw/tokens

runworker () {
  gpu="$1"; shift; models=("$@")
  for model in "${models[@]}"; do
    dd=$(echo "$model" | sed 's#/#__#g'); lg=$(echo "$model" | tr '/' '_')
    if ls runs/ws3/"omni-math__${dd}"*.jsonl >/dev/null 2>&1; then
      echo "[$(date +%H:%M:%S)] g$gpu SKIP $model" >> logs/ws3_progress.log; continue; fi
    echo "[$(date +%H:%M:%S)] g$gpu START $model omni-math" >> logs/ws3_progress.log
    CUDA_VISIBLE_DEVICES="$gpu" timeout 2400 .venv/bin/python scripts/run_all.py \
      --model "$model" --dataset omni-math --limit 500 --no-judge --save-tokens "$TOK" --out runs/ws3 \
      >> "logs/ws3_${lg}.log" 2>&1
    rc=$?
    nvidia-smi -i "$gpu" --query-compute-apps=pid --format=csv,noheader 2>/dev/null | xargs -r kill -9 2>/dev/null
    sleep 4
    echo "[$(date +%H:%M:%S)] g$gpu END   $model rc=$rc" >> logs/ws3_progress.log
  done
  echo "[$(date +%H:%M:%S)] g$gpu WORKER DONE" >> logs/ws3_progress.log
}
export -f runworker; export HF_HOME PYTHONPATH TOK

nohup setsid bash -c 'runworker 1 "Qwen/Qwen2.5-0.5B-Instruct" "Qwen/Qwen2.5-1.5B-Instruct" "Qwen/Qwen2.5-3B-Instruct" "mistralai/Mistral-7B-Instruct-v0.3"' >/dev/null 2>&1 &
nohup setsid bash -c 'runworker 2 "Qwen/Qwen2.5-7B-Instruct" "Qwen/Qwen2.5-14B-Instruct" "microsoft/phi-4" "Qwen/Qwen2.5-Math-7B-Instruct"' >/dev/null 2>&1 &
nohup setsid bash -c 'runworker 3 "allenai/OLMo-2-1124-13B-Instruct" "deepseek-ai/deepseek-math-7b-instruct" "mistralai/Mathstral-7B-v0.1"' >/dev/null 2>&1 &
echo "WS3 launched: 11 models on omni-math, 3 GPUs"
