#!/bin/bash
# Phase 0 judge grid: 20 runs on 4 GPUs, per-GPU sequential chains, math domain.
# Run ON skampere1 from /lfs/skampere1/0/srivatsavad/tfa-vs-judge AFTER bon_oracle math.
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache
export HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=/lfs/skampere1/0/srivatsavad/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export POOL=runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl
mkdir -p logs

chain () {  # $1 gpu, $2 model, $3 space-separated "cond_rep" list
  cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge || exit 1
  local gpu=$1 model=$2; shift 2
  for cr in "$@"; do
    local cond=${cr%_*} rep=${cr#*_}
    CUDA_VISIBLE_DEVICES=$gpu $PY bon_judge.py --pool $POOL --judge "$model" \
      --cond $cond --rep $rep --domain math --filter-band --tasks runs/bon_math_tasks.jsonl \
      >> "logs/bonjudge_$(echo $model | tr '/' '_')_gpu$gpu.log" 2>&1
  done
  echo "[chain gpu$gpu $model done]" >> logs/bon_chain.log
}

FULL="noref_a noref_b ref_a ref_b"
GPU_A=${1:-0}; GPU_B=${2:-2}
nohup bash -c "$(declare -f chain); chain $GPU_A Qwen/Qwen2.5-14B-Instruct $FULL sabotage_a sabotage_b" > logs/chain_gpuA.log 2>&1 &
echo "gpuA($GPU_A) 14B PID $!"
nohup bash -c "$(declare -f chain); chain $GPU_B Qwen/Qwen2.5-7B-Instruct $FULL sabotage_a sabotage_b; chain $GPU_B Qwen/Qwen2.5-3B-Instruct $FULL; chain $GPU_B Qwen/Qwen2.5-1.5B-Instruct $FULL" > logs/chain_gpuB.log 2>&1 &
echo "gpuB($GPU_B) 7B+3B+1.5B PID $!"
