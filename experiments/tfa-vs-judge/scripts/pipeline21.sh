#!/bin/bash
# Pipeline 21: fresh exact-oracle rotation replication (P-RR1..P-RR3, registered in
# scripts/build_replrot_pool.py + papers/analysis/replrot_analysis.py, committed BEFORE
# this runs). Re-judges the FROZEN replication pool with the reference rotated to a
# different valid answer — no generation, no training. 4 runs: judges {Qwen2.5-7B, phi-4}
# x rubrics {a, b}, cond ref, on the rotated pool. Blind + original-ref scores are the
# frozen bon_scores_repl files; nothing is recomputed there.
# Per-run exit-code checks (pipeline19 lesson): PIPELINE21_DONE only if all succeeded.
# phi-4 weights may still be syncing: waits for ALL_SYNC_DONE in ~/sync.log before phi-4.
# Runs on skampere2. Usage: pipeline21.sh GPU
BASE=/lfs/skampere2/0/srivatsavad
cd $BASE/tfa-vs-judge
GPU=${1:?usage: pipeline21.sh GPU}
mkdir -p logs runs/bon_scores_replrot
PY=.venv/bin/python
POOL=runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl
nohup setsid env HOME=$BASE XDG_CACHE_HOME=$BASE/.cache HF_HOME=$BASE/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=$BASE/tmp PYTHONPATH=$BASE/tfa-vs-judge bash -c "
  cd $BASE/tfa-vs-judge
  FAILED=''
  $PY build_replrot_pool.py >> logs/pipeline21.log 2>&1 || FAILED='build'
  for rep in a b; do
    [ -n \"\$FAILED\" ] && break
    CUDA_VISIBLE_DEVICES=$GPU $PY bon_judge.py --pool $POOL --judge Qwen/Qwen2.5-7B-Instruct \
      --cond ref --rep \$rep --domain synthk --tasks runs/repl_main_tasks.jsonl \
      --out runs/bon_scores_replrot >> logs/pipeline21.log 2>&1 || FAILED=\"\$FAILED qwen:\$rep\"
  done
  until grep -q ALL_SYNC_DONE $BASE/sync.log 2>/dev/null; do sleep 120; done
  for rep in a b; do
    [ -n \"\$FAILED\" ] && break
    CUDA_VISIBLE_DEVICES=$GPU $PY bon_judge.py --pool $POOL --judge microsoft/phi-4 \
      --cond ref --rep \$rep --domain synthk --tasks runs/repl_main_tasks.jsonl \
      --out runs/bon_scores_replrot >> logs/pipeline21.log 2>&1 || FAILED=\"\$FAILED phi4:\$rep\"
  done
  if [ -z \"\$FAILED\" ]; then echo PIPELINE21_DONE >> logs/pipeline21.log
  else echo \"PIPELINE21_FAILED:\$FAILED\" >> logs/pipeline21.log; fi
" > logs/pipeline21_outer.log 2>&1 &
echo "pipeline21 gpu$GPU PID $!"
