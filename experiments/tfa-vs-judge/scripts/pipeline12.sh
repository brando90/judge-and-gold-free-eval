#!/bin/bash
# Pipeline 12: DPO gating rerun with a stronger manipulation (registered pre-run).
# The first run (commit history: dpo_results.json) was a manipulation failure: one epoch at
# lr 5e-6 left training reward margins near zero and every downstream estimand null, so
# P-D1..P-D3 were untested. This rerun strengthens ONLY the training manipulation:
# 4 epochs, lr 2e-5, beta 0.1, same pairs, same frozen predictions P-D1..P-D3.
# REGISTERED MANIPULATION CHECK: the run counts as a test of P-D1..P-D3 only if the
# trained arm's own-judge score gain on TRAIN items is nonzero (CI excluding zero) OR final
# training reward margins exceed 0.5; otherwise report "manipulation failed" again and stop.
# Waits for PIPELINE10_DONE. Run ON skampere1: bash pipeline12.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=$HOME/.cache
export HF_HOME=$HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=$HOME/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline12.sh GPU}
mkdir -p logs

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE10_DONE logs/pipeline10.log 2>/dev/null; do sleep 300; done; \
  rm -f runs/dpo/eval_ref.jsonl runs/dpo/eval_sabotage.jsonl; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY dpo_train.py --cond ref --epochs 4 --lr 2e-5 --out runs/dpo2 >> logs/pipeline12.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY dpo_train.py --cond sabotage --epochs 4 --lr 2e-5 --out runs/dpo2 >> logs/pipeline12.log 2>&1; \
  for p in ref sabotage; do \
    CUDA_VISIBLE_DEVICES=$GPU \$PY dpo_eval.py --policy \$p --out runs/dpo2 >> logs/pipeline12.log 2>&1; \
  done; \
  echo PIPELINE12_DONE >> logs/pipeline12.log" > logs/pipeline12_outer.log 2>&1 &
echo "pipeline12 gpu$GPU PID $!"
