#!/bin/bash
# Pipeline 7: DPO gating experiment (registered P-D1..P-D3 in dpo_pairs.py, commit 3a964f1).
# Two identical LoRA-DPO arms on Qwen2.5-7B-Instruct differing only in the judge that built
# the pairs (certified ref vs convicted sabotage), then eval generations from base + both
# adapters on train and held-out items. Judge scoring runs off-cluster (OpenAI key lives
# on the laptop). Waits for PIPELINE6_DONE. Run ON skampere1: bash pipeline7.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=$HOME/.cache
export HF_HOME=$HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=$HOME/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline7.sh GPU}
mkdir -p logs runs/dpo

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE6_DONE logs/pipeline6.log 2>/dev/null; do sleep 300; done; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY dpo_train.py --cond ref >> logs/pipeline7.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY dpo_train.py --cond sabotage >> logs/pipeline7.log 2>&1; \
  for p in base ref sabotage; do \
    CUDA_VISIBLE_DEVICES=$GPU \$PY dpo_eval.py --policy \$p >> logs/pipeline7.log 2>&1; \
  done; \
  echo PIPELINE7_DONE >> logs/pipeline7.log" > logs/pipeline7_outer.log 2>&1 &
echo "pipeline7 gpu$GPU PID $!"
