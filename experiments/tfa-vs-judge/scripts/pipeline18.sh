#!/bin/bash
# Pipeline 18: multi-valid DPO training-pressure experiment (registered internally in
# dpo_mv_pairs.py + papers/analysis/dpo_mv_analysis.py, committed BEFORE this runs).
# Two LoRA-DPO arms on meta-llama/Llama-3.1-8B-Instruct, pairs from the Qwen-7B judge's
# plain single-reference scores (ref arm) vs blind-then-reveal scores (m1 arm), identical
# hyperparameters (4 epochs, lr 2e-5, beta 0.1 = the registered R1-rerun settings).
# Waits for the pipeline17 chain to release the GPU. Usage: pipeline18.sh GPU
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline18.sh GPU}
mkdir -p logs runs/dpo_mv
PY=.venv/bin/python
nohup env HOME=/lfs/skampere1/0/srivatsavad XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=/lfs/skampere1/0/srivatsavad/tmp PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge bash -c "
  until grep -q P17CHAIN_DONE logs/p17chain.log 2>/dev/null; do sleep 300; done
  $PY dpo_mv_pairs.py --arm ref >> logs/pipeline18.log 2>&1
  $PY dpo_mv_pairs.py --arm m1 >> logs/pipeline18.log 2>&1
  for arm in ref m1; do
    CUDA_VISIBLE_DEVICES=$GPU $PY dpo_train.py --cond \$arm --model meta-llama/Llama-3.1-8B-Instruct \
      --epochs 4 --lr 2e-5 --beta 0.1 --out runs/dpo_mv >> logs/pipeline18.log 2>&1
  done
  for pol in base ref m1; do
    CUDA_VISIBLE_DEVICES=$GPU $PY dpo_mv_eval.py --policy \$pol --out runs/dpo_mv >> logs/pipeline18.log 2>&1
  done
  for pol in base ref m1; do for split in train heldout; do
    $PY repl_oracle.py --pool runs/dpo_mv/eval_\${pol}_\${split}.jsonl >> logs/pipeline18.log 2>&1
  done; done
  for pol in base ref m1; do for split in train heldout; do
    TASKS=runs/kstrat_tasks.jsonl; [ \$split = heldout ] && TASKS=runs/repl_main_tasks.jsonl
    mkdir -p runs/dpo_mv/scores_\${pol}_\${split}
    for cond in noref ref; do for rep in a b; do
      CUDA_VISIBLE_DEVICES=$GPU $PY bon_judge.py --pool runs/dpo_mv/eval_\${pol}_\${split}.jsonl \
        --judge Qwen/Qwen2.5-7B-Instruct --cond \$cond --rep \$rep --domain synthk \
        --tasks \$TASKS --out runs/dpo_mv/scores_\${pol}_\${split} >> logs/pipeline18.log 2>&1
    done; done
  done; done
  for pol in base ref m1; do
    CUDA_VISIBLE_DEVICES=$GPU $PY mitigation_judge.py --pool runs/dpo_mv/eval_\${pol}_train.jsonl \
      --judge Qwen/Qwen2.5-7B-Instruct --cond m1 --rep a --out runs/dpo_mv/scores_\${pol}_train >> logs/pipeline18.log 2>&1
  done
  echo PIPELINE18_DONE >> logs/pipeline18.log
" > logs/pipeline18_outer.log 2>&1 &
echo "pipeline18 gpu$GPU PID $!"
