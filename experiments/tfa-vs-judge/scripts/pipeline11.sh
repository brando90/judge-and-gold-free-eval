#!/bin/bash
# Pipeline 11: (a) DPO gating rerun with the trl-1.10 fix (P-D1..P-D3, commit 3a964f1);
# (b) second-phrasing instruction arm on the synthk Qwen pool (registered P-S2b: the
# capability gate replicates under a do-not-compare phrasing). Waits for PIPELINE9_DONE.
# Run ON skampere1: bash pipeline11.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=$HOME/.cache
export HF_HOME=$HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=$HOME/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline11.sh GPU}
mkdir -p logs

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE9_DONE logs/pipeline9.log 2>/dev/null; do sleep 300; done; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY dpo_train.py --cond ref >> logs/pipeline11.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY dpo_train.py --cond sabotage >> logs/pipeline11.log 2>&1; \
  for p in ref sabotage; do \
    CUDA_VISIBLE_DEVICES=$GPU \$PY dpo_eval.py --policy \$p >> logs/pipeline11.log 2>&1; \
  done; \
  for m in Qwen/Qwen2.5-1.5B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-14B-Instruct meta-llama/Llama-3.1-8B-Instruct microsoft/phi-4; do \
    CUDA_VISIBLE_DEVICES=$GPU \$PY bon_judge.py --pool runs/bon/bon_synthk__Qwen__Qwen2.5-7B-Instruct.jsonl \
      --judge \$m --cond refinst2 --rep a --domain synthk --out runs/bon_scores_synthk >> logs/pipeline11.log 2>&1; \
  done; \
  echo PIPELINE11_DONE >> logs/pipeline11.log" > logs/pipeline11_outer.log 2>&1 &
echo "pipeline11 gpu$GPU PID $!"
