#!/bin/bash
# Pipeline 9: RM paraphrase-replicate protocol (registered P-R1 in rm_paraphrase.py).
# Paraphrase the in-band math pool with Qwen-7B, then RM-score the paraphrases; the
# original-pool RM scores (runs/rm_scores_math.jsonl) are the selection replicate.
# Waits for PIPELINE8_DONE. Run ON skampere1: bash pipeline9.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=$HOME/.cache
export HF_HOME=$HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=$HOME/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline9.sh GPU}
mkdir -p logs

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE8_DONE logs/pipeline8.log 2>/dev/null; do sleep 300; done; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY rm_paraphrase.py >> logs/pipeline9.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY rm_score.py --pool runs/bon/bon_math_para.jsonl \
    --tasks runs/bon_math_tasks.jsonl --out runs/rm_scores_math_para.jsonl >> logs/pipeline9.log 2>&1; \
  echo PIPELINE9_DONE >> logs/pipeline9.log" > logs/pipeline9_outer.log 2>&1 &
echo "pipeline9 gpu$GPU PID $!"
