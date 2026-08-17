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
  local gpu=$1 model=$2; shift 2
  for cr in "$@"; do
    local cond=${cr%_*} rep=${cr#*_}
    CUDA_VISIBLE_DEVICES=$gpu $PY bon_judge.py --pool $POOL --judge "$model" \
      --cond $cond --rep $rep --domain math --filter-band \
      >> "logs/bonjudge_$(echo $model | tr '/' '_')_gpu$gpu.log" 2>&1
  done
  echo "[chain gpu$gpu $model done]" >> logs/bon_chain.log
}

FULL="noref_a noref_b ref_a ref_b"
nohup bash -c "$(declare -f chain); chain 0 Qwen/Qwen2.5-14B-Instruct $FULL sabotage_a sabotage_b" > logs/chain_gpu0.log 2>&1 &
echo "gpu0 14B PID $!"
nohup bash -c "$(declare -f chain); chain 1 Qwen/Qwen2.5-7B-Instruct $FULL sabotage_a sabotage_b" > logs/chain_gpu1.log 2>&1 &
echo "gpu1 7B PID $!"
nohup bash -c "$(declare -f chain); chain 2 Qwen/Qwen2.5-3B-Instruct $FULL" > logs/chain_gpu2.log 2>&1 &
echo "gpu2 3B PID $!"
nohup bash -c "$(declare -f chain); chain 6 Qwen/Qwen2.5-1.5B-Instruct $FULL" > logs/chain_gpu6.log 2>&1 &
echo "gpu6 1.5B PID $!"
