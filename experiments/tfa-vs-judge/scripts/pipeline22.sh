#!/bin/bash
# Pipeline 22: masking-and-identity mechanistic suite (P-MS1..P-MS3, registered in
# scripts/build_refvariant_pools.py + papers/analysis/maskident_analysis.py, committed
# BEFORE this runs). Re-judges FROZEN pools with variant references only — no generation.
# 12 runs: {refword, refexpr} x {Qwen2.5-7B, phi-4} x rubrics {a,b} on the replication
# pool (cond ref, variant pool files) + {masked worked ref} x judges x rubrics on the
# k-stratified pool (cond refsol, masked worked-refs file).
# Per-run exit-code checks; PIPELINE22_DONE only if all succeeded. Waits for phi-4 sync.
# Runs on skampere2. Usage: pipeline22.sh GPU
BASE=/lfs/skampere2/0/srivatsavad
cd $BASE/tfa-vs-judge
GPU=${1:?usage: pipeline22.sh GPU}
mkdir -p logs runs/bon_scores_refword runs/bon_scores_refexpr runs/bon_scores_refsolmask
PY=.venv/bin/python
nohup setsid env HOME=$BASE XDG_CACHE_HOME=$BASE/.cache HF_HOME=$BASE/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=$BASE/tmp PYTHONPATH=$BASE/tfa-vs-judge bash -c "
  cd $BASE/tfa-vs-judge
  FAILED=''
  $PY build_refvariant_pools.py >> logs/pipeline22.log 2>&1 || FAILED='build'
  run_judge() { # judge pool outdir cond extra...
    local judge=\$1 pool=\$2 outdir=\$3 cond=\$4 tasks=\$5 rep=\$6; shift 6
    CUDA_VISIBLE_DEVICES=$GPU $PY bon_judge.py --pool \$pool --judge \$judge --cond \$cond \
      --rep \$rep --domain synthk --tasks \$tasks --out \$outdir \"\$@\" \
      >> logs/pipeline22.log 2>&1 || FAILED=\"\$FAILED \$judge:\$cond:\$rep:\$outdir\"
  }
  for rep in a b; do
    [ -n \"\$FAILED\" ] && break
    run_judge Qwen/Qwen2.5-7B-Instruct runs/bon/bon_replword__meta-llama__Llama-3.1-8B-Instruct.jsonl runs/bon_scores_refword ref runs/repl_main_tasks.jsonl \$rep
    run_judge Qwen/Qwen2.5-7B-Instruct runs/bon/bon_replexpr__meta-llama__Llama-3.1-8B-Instruct.jsonl runs/bon_scores_refexpr ref runs/repl_main_tasks.jsonl \$rep
    run_judge Qwen/Qwen2.5-7B-Instruct runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl runs/bon_scores_refsolmask refsol runs/kstrat_tasks.jsonl \$rep --worked-refs runs/kstrat_worked_refs_masked.jsonl
  done
  until grep -q ALL_SYNC_DONE $BASE/sync.log 2>/dev/null; do sleep 120; done
  for rep in a b; do
    [ -n \"\$FAILED\" ] && break
    run_judge microsoft/phi-4 runs/bon/bon_replword__meta-llama__Llama-3.1-8B-Instruct.jsonl runs/bon_scores_refword ref runs/repl_main_tasks.jsonl \$rep
    run_judge microsoft/phi-4 runs/bon/bon_replexpr__meta-llama__Llama-3.1-8B-Instruct.jsonl runs/bon_scores_refexpr ref runs/repl_main_tasks.jsonl \$rep
    run_judge microsoft/phi-4 runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl runs/bon_scores_refsolmask refsol runs/kstrat_tasks.jsonl \$rep --worked-refs runs/kstrat_worked_refs_masked.jsonl
  done
  if [ -z \"\$FAILED\" ]; then echo PIPELINE22_DONE >> logs/pipeline22.log
  else echo \"PIPELINE22_FAILED:\$FAILED\" >> logs/pipeline22.log; fi
" > logs/pipeline22_outer.log 2>&1 &
echo "pipeline22 gpu$GPU PID $!"
