#!/bin/bash
# Pipeline 6: ladder perturbation-battery arms (registered P-B3, P-B4 in perturb_battery.py):
# 4 Qwen ladder judges x {noref, ref} on the 60 anchor traces' fixed-axis variants.
# Waits for PIPELINE5_DONE. Run ON skampere1: bash pipeline6.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=$HOME/.cache
export HF_HOME=$HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=$HOME/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline6.sh GPU}
mkdir -p logs

$PY perturb_battery.py --emit >> logs/pipeline6.log 2>&1

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE5_DONE logs/pipeline5.log 2>/dev/null; do sleep 300; done; \
  for m in Qwen/Qwen2.5-1.5B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-14B-Instruct; do \
    for cond in noref ref; do \
      CUDA_VISIBLE_DEVICES=$GPU \$PY perturb_battery.py --judge \$m --cond \$cond >> logs/pipeline6.log 2>&1; \
    done; done; \
  echo PIPELINE6_DONE >> logs/pipeline6.log" > logs/pipeline6_outer.log 2>&1 &
echo "pipeline6 gpu$GPU PID $!"
