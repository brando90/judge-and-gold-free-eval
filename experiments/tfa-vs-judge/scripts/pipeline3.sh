#!/bin/bash
# Pipeline 3: (a) sabotage-ladder audits (closes A's two unaudited configs), (b) ties
# reference-rotation ref grid (repowers D's anchoring margins: rotated ref present among valid
# samples on 40/51 items), (c) cross-family generator (Llama-3.1-8B) BoN math: gen -> oracle ->
# 16-run judge grid (kills A's self-preference confound). Sequential on ONE GPU.
# Run ON skampere1: bash pipeline3.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=$HOME/.cache
export HF_HOME=$HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=$HOME/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline3.sh GPU}
mkdir -p logs runs/bon_scores_ties_rot

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY audit_sabotage_ladder.py --judge Qwen/Qwen2.5-7B-Instruct >> logs/pipeline3.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY audit_sabotage_ladder.py --judge Qwen/Qwen2.5-14B-Instruct >> logs/pipeline3.log 2>&1; \
  for m in Qwen/Qwen2.5-14B-Instruct Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-1.5B-Instruct; do \
    for rep in a b; do \
      CUDA_VISIBLE_DEVICES=$GPU \$PY bon_judge.py --pool runs/bon/bon_tiesrot__Qwen__Qwen2.5-7B-Instruct.jsonl \
        --judge \$m --cond ref --rep \$rep --domain ties --out runs/bon_scores_ties_rot >> logs/pipeline3.log 2>&1; \
    done; done; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY bon_generate.py --domain math --model meta-llama/Llama-3.1-8B-Instruct >> logs/pipeline3.log 2>&1; \
  \$PY bon_oracle.py --domain math --pool runs/bon/bon_math__meta-llama__Llama-3.1-8B-Instruct.jsonl >> logs/pipeline3.log 2>&1; \
  for m in Qwen/Qwen2.5-14B-Instruct Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-1.5B-Instruct; do \
    for cr in noref_a noref_b ref_a ref_b; do \
      CUDA_VISIBLE_DEVICES=$GPU \$PY bon_judge.py --pool runs/bon/bon_math__meta-llama__Llama-3.1-8B-Instruct.jsonl \
        --judge \$m --cond \${cr%_*} --rep \${cr#*_} --domain math --filter-band --tasks runs/bon_math_tasks.jsonl \
        --out runs/bon_scores_llama >> logs/pipeline3.log 2>&1; \
    done; done; \
  echo PIPELINE3_DONE >> logs/pipeline3.log" > logs/pipeline3_outer.log 2>&1 &
echo "pipeline3 gpu$GPU PID $!"
