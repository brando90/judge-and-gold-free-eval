#!/bin/bash
# Pipeline 5: (a) RERUN sabotage-ladder audits (pipeline3's crashed: runs/cert_out missing),
# (b) synthk dose-response + mitigation grid (registered P-S1..P-S5, commit c505c23):
#     gen Qwen-7B pool (60 tasks, k in {1,2,4,8,16}) -> oracle -> judge grid
#     judges {Qwen 1.5B,3B,7B,14B} x conds {noref, ref, refinst, multiref} x reps {a,b}
#     + cross-family judges {Llama-3.1-8B, phi-4} same grid (P-S4)
# (c) cross-family generator: Llama-3.1-8B synthk pool -> oracle -> Qwen-7B judge grid (P-S5).
# Waits for PIPELINE3_DONE marker before starting. Run ON skampere1: bash pipeline5.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=$HOME/.cache
export HF_HOME=$HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=$HOME/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline5.sh GPU}
mkdir -p logs runs/cert_out runs/bon_scores_synthk

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE3_DONE logs/pipeline3.log 2>/dev/null; do sleep 300; done; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY audit_sabotage_ladder.py --judge Qwen/Qwen2.5-7B-Instruct >> logs/pipeline5.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY audit_sabotage_ladder.py --judge Qwen/Qwen2.5-14B-Instruct >> logs/pipeline5.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY bon_generate.py --domain synthk --model Qwen/Qwen2.5-7B-Instruct >> logs/pipeline5.log 2>&1; \
  \$PY bon_oracle.py --domain synthk --pool runs/bon/bon_synthk__Qwen__Qwen2.5-7B-Instruct.jsonl >> logs/pipeline5.log 2>&1; \
  for m in Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-14B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-1.5B-Instruct meta-llama/Llama-3.1-8B-Instruct microsoft/phi-4; do \
    for cond in noref ref refinst multiref; do \
      for rep in a b; do \
        CUDA_VISIBLE_DEVICES=$GPU \$PY bon_judge.py --pool runs/bon/bon_synthk__Qwen__Qwen2.5-7B-Instruct.jsonl \
          --judge \$m --cond \$cond --rep \$rep --domain synthk --out runs/bon_scores_synthk >> logs/pipeline5.log 2>&1; \
      done; done; done; \
  CUDA_VISIBLE_DEVICES=$GPU \$PY bon_generate.py --domain synthk --model meta-llama/Llama-3.1-8B-Instruct >> logs/pipeline5.log 2>&1; \
  \$PY bon_oracle.py --domain synthk --pool runs/bon/bon_synthk__meta-llama__Llama-3.1-8B-Instruct.jsonl >> logs/pipeline5.log 2>&1; \
  for cond in noref ref refinst multiref; do \
    for rep in a b; do \
      CUDA_VISIBLE_DEVICES=$GPU \$PY bon_judge.py --pool runs/bon/bon_synthk__meta-llama__Llama-3.1-8B-Instruct.jsonl \
        --judge Qwen/Qwen2.5-7B-Instruct --cond \$cond --rep \$rep --domain synthk --out runs/bon_scores_synthk_llamagen >> logs/pipeline5.log 2>&1; \
    done; done; \
  echo PIPELINE5_DONE >> logs/pipeline5.log" > logs/pipeline5_outer.log 2>&1 &
echo "pipeline5 gpu$GPU PID $!"
