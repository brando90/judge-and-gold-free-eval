#!/bin/bash
# Follow-on pipeline after the in-band ties grid: (a) full-set ties judge grid (all 51 items,
# no band filter, separate out dir), (b) RM baseline scoring (audit traces + math + code pools),
# (c) cross-family completer rerun. Runs sequentially on ONE GPU.
# Run ON skampere1 from /lfs/skampere1/0/srivatsavad/tfa-vs-judge:  bash pipeline2.sh <GPU>
cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge
export HOME=/lfs/skampere1/0/srivatsavad
export XDG_CACHE_HOME=/lfs/skampere1/0/srivatsavad/.cache
export HF_HOME=/lfs/skampere1/0/srivatsavad/.cache/huggingface
export HF_HUB_OFFLINE=1
export TMPDIR=/lfs/skampere1/0/srivatsavad/tmp
export PY=/lfs/skampere1/0/srivatsavad/tfa-vs-judge/.venv/bin/python
export POOL=runs/bon/bon_ties__Qwen__Qwen2.5-7B-Instruct.jsonl
mkdir -p logs runs/bon_scores_ties_full
GPU=${1:?usage: pipeline2.sh GPU}

full_grid () {
  cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge || exit 1
  for model in Qwen/Qwen2.5-14B-Instruct Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-1.5B-Instruct; do
    for cr in noref_a noref_b ref_a ref_b; do
      cond=${cr%_*}; rep=${cr#*_}
      CUDA_VISIBLE_DEVICES=$GPU $PY bon_judge.py --pool $POOL --judge "$model" \
        --cond $cond --rep $rep --domain ties --out runs/bon_scores_ties_full \
        >> logs/pipeline2.log 2>&1
    done
  done
}

nohup bash -c "cd /lfs/skampere1/0/srivatsavad/tfa-vs-judge; $(declare -f full_grid); export GPU=$GPU PY=$PY POOL=$POOL; \
  full_grid; \
  CUDA_VISIBLE_DEVICES=$GPU $PY rm_score.py --traces human_eval/traces_to_label.jsonl --out runs/rm_scores_traces.jsonl >> logs/pipeline2.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU $PY rm_score.py --pool runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl --tasks runs/bon_math_tasks.jsonl --filter-band --out runs/rm_scores_math.jsonl >> logs/pipeline2.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU $PY rm_score.py --pool runs/bon/bon_mbpp__Qwen__Qwen2.5-7B-Instruct.jsonl --filter-band --out runs/rm_scores_code.jsonl >> logs/pipeline2.log 2>&1; \
  CUDA_VISIBLE_DEVICES=$GPU .venv/bin/python scripts/run_rollout_prm.py --completer microsoft/phi-4 --responses 'runs/math500/*.judged.jsonl' --pairs-file pv_topup_pairs.json --k 8 --out runs/prm_labelset_phi4 >> logs/pipeline2.log 2>&1; \
  echo PIPELINE2_DONE >> logs/pipeline2.log" > logs/pipeline2_outer.log 2>&1 &
echo "pipeline2 gpu$GPU PID $!"
