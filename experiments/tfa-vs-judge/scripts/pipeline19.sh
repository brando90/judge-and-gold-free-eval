#!/bin/bash
# Pipeline 19: worked-reference arm (E1) + method rotation (H-METHOD) for Paper D.
# Registered internally in scripts/build_worked_refs.py and
# papers/analysis/worked_ref_analysis.py, both committed BEFORE this pipeline runs.
# Re-judges the FROZEN kstrat pool only — no generation, no training. The references come
# from runs/kstrat_worked_refs.jsonl: refsol shows method A (sol_a), refsol2 shows method B
# (sol_b); both derivations end in the item's own ref_answer, so refsol2-vs-refsol rotates
# the derivation METHOD with the answer held constant.
# 8 runs: judges {Qwen/Qwen2.5-7B-Instruct, microsoft/phi-4} x conds {refsol, refsol2}
# x rubrics {a, b}. --gpu-util 0.40 (phi-4 shares the card; 0.9 OOM'd in earlier chains).
# FAILURE HANDLING (changed from pipelines 10-18): those wrote their DONE marker
# unconditionally, which masked three silent OOM failures. Here every judging call's exit
# code is checked; the marker is PIPELINE19_DONE only if ALL 8 succeeded, otherwise
# PIPELINE19_FAILED with the list of failed configs. Never trust the log without grepping
# for PIPELINE19_DONE.
# Usage: pipeline19.sh GPU
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
GPU=${1:?usage: pipeline19.sh GPU}
mkdir -p logs runs/bon_scores_kstrat
PY=.venv/bin/python
POOL=runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl
WREFS=runs/kstrat_worked_refs.jsonl
nohup setsid env HOME=/lfs/skampere1/0/srivatsavad XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=/lfs/skampere1/0/srivatsavad/tmp PYTHONPATH=/lfs/skampere1/0/srivatsavad/tfa-vs-judge bash -c "
  cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
  if [ ! -f $WREFS ]; then
    echo 'PIPELINE19_FAILED missing $WREFS (run: python3 scripts/build_worked_refs.py)' >> logs/pipeline19.log
    exit 1
  fi
  FAILED=''
  for judge in Qwen/Qwen2.5-7B-Instruct microsoft/phi-4; do
    for cond in refsol refsol2; do
      for rep in a b; do
        CUDA_VISIBLE_DEVICES=$GPU $PY bon_judge.py --pool $POOL \\
          --judge \$judge --cond \$cond --rep \$rep --domain synthk \\
          --tasks runs/kstrat_tasks.jsonl --worked-refs $WREFS \\
          --gpu-util 0.40 --out runs/bon_scores_kstrat >> logs/pipeline19.log 2>&1
        rc=\$?
        if [ \$rc -ne 0 ]; then
          echo \"[pipeline19] FAIL rc=\$rc \$judge \$cond \$rep\" >> logs/pipeline19.log
          FAILED=\"\$FAILED \$judge/\$cond/\$rep\"
        fi
      done
    done
  done
  if [ -n \"\$FAILED\" ]; then
    echo \"PIPELINE19_FAILED\$FAILED\" >> logs/pipeline19.log
  else
    echo PIPELINE19_DONE >> logs/pipeline19.log
  fi
" > logs/pipeline19_outer.log 2>&1 &
echo "pipeline19 gpu$GPU PID $!"
