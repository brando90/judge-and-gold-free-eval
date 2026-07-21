#!/bin/bash
# WS5: TFA on gold code vs pass@1 across a capability spread on HumanEval. Fixed pipeline (os._exit + GPU cleanup).
cd ~/tfa-vs-judge || exit 1
export HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface
set -a; . ~/.env_frontier 2>/dev/null; set +a
export PYTHONPATH=.
mkdir -p runs/code logs
runworker () {
  gpu="$1"; shift; models=("$@")
  for model in "${models[@]}"; do
    dd=$(echo "$model" | sed 's#/#__#g'); lg=$(echo "$model" | tr '/' '_')
    if ls runs/code/"humaneval__${dd}"*.jsonl >/dev/null 2>&1; then
      echo "[$(date +%H:%M:%S)] g$gpu SKIP $model" >> logs/ws5_progress.log; continue; fi
    echo "[$(date +%H:%M:%S)] g$gpu START $model" >> logs/ws5_progress.log
    CUDA_VISIBLE_DEVICES="$gpu" timeout 1800 .venv/bin/python scripts/run_code.py \
      --model "$model" --dataset humaneval --out runs/code >> "logs/ws5_${lg}.log" 2>&1
    rc=$?
    nvidia-smi -i "$gpu" --query-compute-apps=pid --format=csv,noheader 2>/dev/null | xargs -r kill -9 2>/dev/null
    sleep 4
    echo "[$(date +%H:%M:%S)] g$gpu END $model rc=$rc" >> logs/ws5_progress.log
  done
  echo "[$(date +%H:%M:%S)] g$gpu WORKER DONE" >> logs/ws5_progress.log
}
export -f runworker; export HF_HOME PYTHONPATH
nohup setsid bash -c 'runworker 1 "Qwen/Qwen2.5-0.5B-Instruct" "Qwen/Qwen2.5-3B-Instruct" "mistralai/Mistral-7B-Instruct-v0.3"' >/dev/null 2>&1 &
nohup setsid bash -c 'runworker 2 "Qwen/Qwen2.5-1.5B-Instruct" "Qwen/Qwen2.5-7B-Instruct" "microsoft/phi-4"' >/dev/null 2>&1 &
nohup setsid bash -c 'runworker 3 "Qwen/Qwen2.5-14B-Instruct" "allenai/OLMo-2-1124-13B-Instruct"' >/dev/null 2>&1 &
echo "WS5 launched: 8 models on HumanEval, 3 GPUs"
