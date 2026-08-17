#!/bin/bash
# Rerun of the 8 CODE ref-arm runs after the 4096-ctx crash (ref now = example_test asserts).
# Run ON skampere1 from /lfs/skampere1/0/srivatsavad/tfa-vs-judge.
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache
export HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=/lfs/skampere1/0/srivatsavad/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export POOL=runs/bon/bon_mbpp__Qwen__Qwen2.5-7B-Instruct.jsonl
mkdir -p logs
rm -f runs/bon_scores/code__*__ref_a.jsonl runs/bon_scores/code__*__ref_b.jsonl

chain () {
  cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge || exit 1
  local gpu=$1 model=$2; shift 2
  for cr in "$@"; do
    local cond=${cr%_*} rep=${cr#*_}
    CUDA_VISIBLE_DEVICES=$gpu $PY bon_judge.py --pool $POOL --judge "$model" \
      --cond $cond --rep $rep --domain code --filter-band --tasks runs/bon_mbpp_tasks.jsonl \
      >> "logs/bonjudge_coderef_$(echo $model | tr '/' '_')_gpu$gpu.log" 2>&1
  done
  echo "[chain coderef gpu$gpu $model done]" >> logs/bon_chain.log
}

GPU=${1:-7}
nohup bash -c "$(declare -f chain); chain $GPU Qwen/Qwen2.5-14B-Instruct ref_a ref_b; chain $GPU Qwen/Qwen2.5-7B-Instruct ref_a ref_b; chain $GPU Qwen/Qwen2.5-3B-Instruct ref_a ref_b; chain $GPU Qwen/Qwen2.5-1.5B-Instruct ref_a ref_b" > logs/chain_code_ref.log 2>&1 &
echo "code ref chain gpu$GPU PID $!"
