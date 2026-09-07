#!/bin/bash
# Pipeline 20: DPO run 3 = GATE-F (registered commit d33614e: 2 epochs, lr 1e-5, beta 0.1,
# the single FINAL setting under the stopping rule) + the blind-judge attribution arm
# (registered addendum committed with papers/analysis/dpo_mv3_analysis.py BEFORE this runs).
# Three LoRA-DPO arms on meta-llama/Llama-3.1-8B-Instruct: ref and m1 pairs REUSED from
# runs/dpo_mv (built for run 1, unchanged), blind pairs built here by the pinned rule.
# Runs on skampere2 (skampere1 occupied); cluster repo layout is FLAT (.py at repo root).
# Per-step exit-code checks (pipeline19 lesson): marker is PIPELINE20_DONE only if every
# step succeeded, else PIPELINE20_FAILED with the failed steps.
# Usage: pipeline20.sh GPU
BASE=/lfs/skampere2/0/srivatsavad
cd $BASE/tfa-vs-judge
GPU=${1:?usage: pipeline20.sh GPU}
mkdir -p logs runs/dpo_mv3
PY=.venv/bin/python
nohup setsid env HOME=$BASE XDG_CACHE_HOME=$BASE/.cache HF_HOME=$BASE/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=$BASE/tmp PYTHONPATH=$BASE/tfa-vs-judge bash -c "
  cd $BASE/tfa-vs-judge
  FAILED=''
  cp runs/dpo_mv/pairs_ref.jsonl runs/dpo_mv/pairs_m1.jsonl runs/dpo_mv3/ || FAILED='pairs-copy'
  $PY dpo_mv_pairs.py --arm blind --out runs/dpo_mv3 >> logs/pipeline20.log 2>&1 || FAILED=\"\$FAILED pairs:blind\"
  for arm in ref m1 blind; do
    [ -n \"\$FAILED\" ] && break
    CUDA_VISIBLE_DEVICES=$GPU $PY dpo_train.py --cond \$arm \
      --model meta-llama/Llama-3.1-8B-Instruct --epochs 2 --lr 1e-5 --beta 0.1 \
      --out runs/dpo_mv3 >> logs/pipeline20.log 2>&1 || FAILED=\"\$FAILED train:\$arm\"
  done
  for pol in base ref m1 blind; do
    [ -n \"\$FAILED\" ] && break
    CUDA_VISIBLE_DEVICES=$GPU $PY dpo_mv_eval.py --policy \$pol --out runs/dpo_mv3 \
      >> logs/pipeline20.log 2>&1 || FAILED=\"\$FAILED eval:\$pol\"
  done
  for pol in base ref m1 blind; do for split in train heldout; do
    [ -n \"\$FAILED\" ] && break 2
    $PY repl_oracle.py --pool runs/dpo_mv3/eval_\${pol}_\${split}.jsonl \
      >> logs/pipeline20.log 2>&1 || FAILED=\"\$FAILED oracle:\$pol:\$split\"
  done; done
  for pol in base ref m1 blind; do for split in train heldout; do
    TASKS=runs/kstrat_tasks.jsonl; [ \$split = heldout ] && TASKS=runs/repl_main_tasks.jsonl
    mkdir -p runs/dpo_mv3/scores_\${pol}_\${split}
    for cond in noref ref; do for rep in a b; do
      [ -n \"\$FAILED\" ] && break 4
      CUDA_VISIBLE_DEVICES=$GPU $PY bon_judge.py --pool runs/dpo_mv3/eval_\${pol}_\${split}.jsonl \
        --judge Qwen/Qwen2.5-7B-Instruct --cond \$cond --rep \$rep --domain synthk \
        --tasks \$TASKS --out runs/dpo_mv3/scores_\${pol}_\${split} \
        >> logs/pipeline20.log 2>&1 || FAILED=\"\$FAILED judge:\$pol:\$split:\$cond:\$rep\"
    done; done
  done; done
  for pol in base m1; do
    [ -n \"\$FAILED\" ] && break
    CUDA_VISIBLE_DEVICES=$GPU $PY mitigation_judge.py --pool runs/dpo_mv3/eval_\${pol}_train.jsonl \
      --judge Qwen/Qwen2.5-7B-Instruct --cond m1 --rep a --out runs/dpo_mv3/scores_\${pol}_train \
      >> logs/pipeline20.log 2>&1 || FAILED=\"\$FAILED m1judge:\$pol\"
  done
  if [ -z \"\$FAILED\" ]; then echo PIPELINE20_DONE >> logs/pipeline20.log
  else echo \"PIPELINE20_FAILED:\$FAILED\" >> logs/pipeline20.log; fi
" > logs/pipeline20_outer.log 2>&1 &
echo "pipeline20 gpu$GPU PID $!"
