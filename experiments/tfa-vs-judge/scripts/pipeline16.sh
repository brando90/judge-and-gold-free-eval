#!/bin/bash
# Pipeline 16: k-stratified structural-mitigation experiment (OSF osf.io/qugbd, registered
# 2026-08-23 22:56 before any data). 75 items (15 per k in {1,2,4,8,16}), Llama-3.1-8B
# generator, judges Qwen2.5-7B and phi-4, four conditions (blind, single-ref, M1
# blind-then-reveal, M2 equivalence-gated) x two rubric replicates.
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline16.sh GPU}
mkdir -p logs runs/bon_scores_kstrat
nohup env HOME=/lfs/skampere1/0/srivatsavad XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=/lfs/skampere1/0/srivatsavad/tmp PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python bon_generate.py --domain kstrat --model meta-llama/Llama-3.1-8B-Instruct >> logs/pipeline16.log 2>&1; \
  .venv/bin/python repl_oracle.py --pool runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl >> logs/pipeline16.log 2>&1; \
  for m in Qwen/Qwen2.5-7B-Instruct microsoft/phi-4; do \
    for cond in noref ref; do for rep in a b; do \
      CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python bon_judge.py --pool runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl \
        --judge \$m --cond \$cond --rep \$rep --domain synthk --tasks runs/kstrat_tasks.jsonl --out runs/bon_scores_kstrat >> logs/pipeline16.log 2>&1; \
    done; done; \
    for cond in m1 m2; do for rep in a b; do \
      CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python mitigation_judge.py --pool runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl \
        --judge \$m --cond \$cond --rep \$rep --out runs/bon_scores_kstrat >> logs/pipeline16.log 2>&1; \
    done; done; done; \
  echo PIPELINE16_DONE >> logs/pipeline16.log" > logs/pipeline16_outer.log 2>&1 &
echo "pipeline16 gpu$GPU PID $!"
