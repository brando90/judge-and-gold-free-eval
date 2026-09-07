#!/bin/bash
# Pipeline 24: M1 second-pass mechanism variants (P-M1V1..P-M1V3, registered in
# papers/analysis/m1_variants_analysis.py + the mitigation_judge.py cond extensions,
# committed BEFORE this runs). 12 runs on the frozen kstrat pool: conds
# {m1noscore, m1prev, m1indep} x judges {Qwen2.5-7B, phi-4} x rubrics {a, b}.
# m1indep shows each judge the OTHER judge's frozen blind (noref_a) escores.
# WAITS for PIPELINE22_DONE so it takes over the masking suite's GPU.
# Per-run exit-code checks; PIPELINE24_DONE only if all succeeded.
# Runs on skampere2. Usage: pipeline24.sh GPU
BASE=/lfs/skampere2/0/srivatsavad
cd $BASE/tfa-vs-judge
GPU=${1:?usage: pipeline24.sh GPU}
mkdir -p logs
PY=.venv/bin/python
POOL=runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl
QW=Qwen/Qwen2.5-7B-Instruct
PHI=microsoft/phi-4
QW_BLIND=runs/bon_scores_kstrat/synthk__Qwen__Qwen2.5-7B-Instruct__noref_a.jsonl
PHI_BLIND=runs/bon_scores_kstrat/synthk__microsoft__phi-4__noref_a.jsonl
nohup setsid env HOME=$BASE XDG_CACHE_HOME=$BASE/.cache HF_HOME=$BASE/.cache/huggingface HF_HUB_OFFLINE=1 TMPDIR=$BASE/tmp PYTHONPATH=$BASE/tfa-vs-judge bash -c "
  cd $BASE/tfa-vs-judge
  until grep -q PIPELINE22_DONE logs/pipeline22.log 2>/dev/null; do sleep 180; done
  FAILED=''
  for rep in a b; do for cond in m1noscore m1prev; do
    [ -n \"\$FAILED\" ] && break 2
    CUDA_VISIBLE_DEVICES=$GPU $PY mitigation_judge.py --pool $POOL --judge $QW \
      --cond \$cond --rep \$rep >> logs/pipeline24.log 2>&1 || FAILED=\"\$FAILED qw:\$cond:\$rep\"
    CUDA_VISIBLE_DEVICES=$GPU $PY mitigation_judge.py --pool $POOL --judge $PHI \
      --cond \$cond --rep \$rep >> logs/pipeline24.log 2>&1 || FAILED=\"\$FAILED phi:\$cond:\$rep\"
  done; done
  for rep in a b; do
    [ -n \"\$FAILED\" ] && break
    CUDA_VISIBLE_DEVICES=$GPU $PY mitigation_judge.py --pool $POOL --judge $QW \
      --cond m1indep --rep \$rep --other-scores $PHI_BLIND \
      >> logs/pipeline24.log 2>&1 || FAILED=\"\$FAILED qw:m1indep:\$rep\"
    CUDA_VISIBLE_DEVICES=$GPU $PY mitigation_judge.py --pool $POOL --judge $PHI \
      --cond m1indep --rep \$rep --other-scores $QW_BLIND \
      >> logs/pipeline24.log 2>&1 || FAILED=\"\$FAILED phi:m1indep:\$rep\"
  done
  if [ -z \"\$FAILED\" ]; then echo PIPELINE24_DONE >> logs/pipeline24.log
  else echo \"PIPELINE24_FAILED:\$FAILED\" >> logs/pipeline24.log; fi
" > logs/pipeline24_outer.log 2>&1 &
echo "pipeline24 gpu$GPU PID $!"
