#!/bin/bash
# Pipeline 23: answer-separability continuum (P-SC1..P-SC4, registered in
# scripts/build_sep_tasks.py + sep_generate.py + sep_oracle.py +
# papers/analysis/sep_continuum_analysis.py, all committed BEFORE this runs).
# Chain: build tasks -> generate (Llama-3.1-8B, n=64) -> oracle (CPU, incl. sandboxed
# program execution) -> 8 judge runs ({Qwen2.5-7B, phi-4} x {noref, ref} x rubrics {a,b}).
# WAITS for PIPELINE21_DONE so it takes over the rotation replication's GPU.
# Per-step exit-code checks; PIPELINE23_DONE only if all succeeded.
# Runs on skampere2. Usage: pipeline23.sh GPU
BASE=/lfs/skampere2/0/srivatsavad
cd $BASE/tfa-vs-judge
GPU=${1:?usage: pipeline23.sh GPU}
mkdir -p logs runs/bon_scores_sep
PY=.venv/bin/python
POOL=runs/bon/bon_sep__meta-llama__Llama-3.1-8B-Instruct.jsonl
nohup setsid env HOME=$BASE XDG_CACHE_HOME=$BASE/.cache HF_HOME=$BASE/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=$BASE/tmp PYTHONPATH=$BASE/tfa-vs-judge bash -c "
  cd $BASE/tfa-vs-judge
  until grep -q PIPELINE21_DONE logs/pipeline21.log 2>/dev/null; do sleep 180; done
  FAILED=''
  $PY build_sep_tasks.py >> logs/pipeline23.log 2>&1 || FAILED='build'
  [ -z \"\$FAILED\" ] && { CUDA_VISIBLE_DEVICES=$GPU $PY sep_generate.py >> logs/pipeline23.log 2>&1 || FAILED='generate'; }
  [ -z \"\$FAILED\" ] && { $PY sep_oracle.py $POOL >> logs/pipeline23.log 2>&1 || FAILED='oracle'; }
  for judge in Qwen/Qwen2.5-7B-Instruct microsoft/phi-4; do
    for cond in noref ref; do for rep in a b; do
      [ -n \"\$FAILED\" ] && break 3
      CUDA_VISIBLE_DEVICES=$GPU $PY bon_judge.py --pool $POOL --judge \$judge --cond \$cond \
        --rep \$rep --domain synthk --tasks runs/sep_tasks.jsonl --out runs/bon_scores_sep \
        >> logs/pipeline23.log 2>&1 || FAILED=\"\$FAILED judge:\$judge:\$cond:\$rep\"
    done; done
  done
  if [ -z \"\$FAILED\" ]; then echo PIPELINE23_DONE >> logs/pipeline23.log
  else echo \"PIPELINE23_FAILED:\$FAILED\" >> logs/pipeline23.log; fi
" > logs/pipeline23_outer.log 2>&1 &
echo "pipeline23 gpu$GPU PID $!"
