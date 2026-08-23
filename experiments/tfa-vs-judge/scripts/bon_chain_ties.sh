#!/bin/bash
# Multi-valid-answer BoN grid (RewardBench-2 Ties): generation -> oracle -> 16 judge runs
# (4 Qwen sizes x noref/ref x a/b reps). Single-GPU sequential chain; respects the 2-GPU cap.
# Run ON skampere1 from /lfs/skampere1/0/srivatsavad/tfa-vs-judge AFTER scp'ing:
#   bon_ties_tasks.jsonl -> runs/, and the patched bon_generate.py bon_oracle.py
#   bon_judge.py bon_rubrics.py -> repo root.
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache
export HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=/lfs/skampere1/0/srivatsavad/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export POOL=runs/bon/bon_ties__Qwen__Qwen2.5-7B-Instruct.jsonl
mkdir -p logs

chain () {
  cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge || exit 1
  local gpu=$1 model=$2; shift 2
  for cr in "$@"; do
    local cond=${cr%_*} rep=${cr#*_}
    CUDA_VISIBLE_DEVICES=$gpu $PY bon_judge.py --pool $POOL --judge "$model" \
      --cond $cond --rep $rep --domain ties --filter-band \
      >> "logs/bonjudge_ties_$(echo $model | tr '/' '_')_gpu$gpu.log" 2>&1
  done
  echo "[chain ties gpu$gpu $model done]" >> logs/bon_chain.log
}

FULL="noref_a noref_b ref_a ref_b"
GPU=${1:?usage: bon_chain_ties.sh GPU}
nohup bash -c "$(declare -f chain); \
  CUDA_VISIBLE_DEVICES=$GPU $PY bon_generate.py --domain ties >> logs/bon_ties_gen.log 2>&1; \
  $PY bon_oracle.py --domain ties --pool $POOL >> logs/bon_ties_gen.log 2>&1; \
  chain $GPU Qwen/Qwen2.5-14B-Instruct $FULL; chain $GPU Qwen/Qwen2.5-7B-Instruct $FULL; \
  chain $GPU Qwen/Qwen2.5-3B-Instruct $FULL; chain $GPU Qwen/Qwen2.5-1.5B-Instruct $FULL" \
  > logs/chain_ties.log 2>&1 &
echo "ties chain gpu$GPU PID $!"
