#!/bin/bash
# Pipeline 15: MAIN run of Paper D's clean preregistered replication (OSF: osf.io/ym5x9,
# registered 2026-08-23 before any generation). 120-item pool, Llama-3.1-8B generator,
# judges Qwen2.5-7B and phi-4, blind vs single reference, two rubric replicates.
# Waits for PIPELINE14_DONE (pilot). Run ON skampere1: bash pipeline15.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline15.sh GPU}
mkdir -p logs runs/bon_scores_repl
nohup env HOME=/lfs/skampere1/0/srivatsavad XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=/lfs/skampere1/0/srivatsavad/tmp PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; \
  until grep -q PIPELINE14_DONE logs/pipeline14.log 2>/dev/null; do sleep 300; done; \
  CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python bon_generate.py --domain repl --model meta-llama/Llama-3.1-8B-Instruct >> logs/pipeline15.log 2>&1; \
  .venv/bin/python repl_oracle.py --pool runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl >> logs/pipeline15.log 2>&1; \
  for m in Qwen/Qwen2.5-7B-Instruct microsoft/phi-4; do \
    for cond in noref ref; do for rep in a b; do \
      CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python bon_judge.py --pool runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl \
        --judge \$m --cond \$cond --rep \$rep --domain synthk --out runs/bon_scores_repl >> logs/pipeline15.log 2>&1; \
    done; done; done; \
  echo PIPELINE15_DONE >> logs/pipeline15.log" > logs/pipeline15_outer.log 2>&1 &
echo "pipeline15 gpu$GPU PID $!"
