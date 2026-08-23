#!/bin/bash
# Pipeline 10: length-matched uninformative-reference control (registered P-L1 in
# tfa_padref.py). Waits for PIPELINE11_DONE. Run ON skampere1: bash pipeline10.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=$HOME/.cache
export HF_HOME=$HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=$HOME/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline10.sh GPU}
mkdir -p logs

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE11_DONE logs/pipeline11.log 2>/dev/null; do sleep 300; done; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY tfa_padref.py >> logs/pipeline10.log 2>&1; \
  echo PIPELINE10_DONE >> logs/pipeline10.log" > logs/pipeline10_outer.log 2>&1 &
echo "pipeline10 gpu$GPU PID $!"
