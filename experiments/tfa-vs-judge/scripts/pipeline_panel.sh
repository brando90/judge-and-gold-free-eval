#!/bin/bash
# Pipeline PANEL: the prospective held-out judge panel for Paper A (Registration 6).
# Two phases, deliberately separated so the audit verdicts are frozen and committed BEFORE any
# optimization outcome exists:
#   phase "audit" : score the 242 anchor traces with every panel cell  -> runs/panel_cert/
#   phase "bon"   : score the math best-of-64 pool, replicates a and b -> runs/bon_scores_panel/
# Usage (on skampere2):  bash pipeline_panel.sh <GPU> <audit|bon> <half:1|2>
set -u
ROOT=/lfs/skampere2/0/srivatsavad/tfa-vs-judge
cd "$ROOT"
GPU=${1:?usage: pipeline_panel.sh GPU PHASE HALF}
PHASE=${2:?usage: pipeline_panel.sh GPU PHASE HALF}
HALF=${3:?usage: pipeline_panel.sh GPU PHASE HALF}
mkdir -p logs runs/panel_cert runs/bon_scores_panel /lfs/skampere2/0/srivatsavad/tmp

H1_LLM="p01_phi4_blind p07_phi4_ref p10_phi4_blind_L2 p12_phi4_blind_LEN p13_phi4_ref_L3 p16_phi4_ref_L5 p11_qwen14b_blind_L4 p15_qwen14b_ref_LEN"
H1_RM=""
H2_LLM="p02_llama8b_blind p08_llama8b_ref p14_llama8b_ref_L2 p03_qwen3_8b_blind p04_coder14b_blind p09_coder7b_ref p05_qwen05b_ref p06_qwen05b_blind"
H2_RM="p17_rm_skywork_v2 p18_rm_tulu3"
ALL_RM="p17_rm_skywork_v2 p18_rm_tulu3"
if [ "$HALF" = "1" ]; then LLM_CELLS="$H1_LLM"; RM_CELLS="$H1_RM"; FETCH="";
elif [ "$HALF" = "2" ]; then LLM_CELLS="$H2_LLM"; RM_CELLS="$H2_RM";
     FETCH="Qwen/Qwen3-8B Qwen/Qwen2.5-0.5B-Instruct Skywork/Skywork-Reward-V2-Llama-3.1-8B allenai/Llama-3.1-Tulu-3-8B-RM";
else
  # explicit cell list; reward-model cells are routed to panel_rm.py automatically
  LLM_CELLS=""; RM_CELLS=""; FETCH=""
  for c in $HALF; do
    case " $ALL_RM " in *" $c "*) RM_CELLS="$RM_CELLS $c";; *) LLM_CELLS="$LLM_CELLS $c";; esac
  done
  HALF=$(echo "$HALF" | tr " " "-" | cut -c1-40)
fi

RUNNER=logs/panel_${PHASE}_${HALF}_runner.sh
LOG=logs/panel_${PHASE}_${HALF}.log
cat > "$RUNNER" <<EOF
#!/bin/bash
set -u
cd $ROOT
export HOME=/lfs/skampere2/0/srivatsavad
export XDG_CACHE_HOME=\$HOME/.cache
export HF_HOME=\$HOME/.cache/huggingface
export TMPDIR=\$HOME/tmp
export PYTHONPATH=$ROOT
PY=$ROOT/.venv/bin/python
for m in $FETCH; do
  echo "[fetch] \$m" >> $LOG
  HF_HUB_OFFLINE=0 \$PY -c "
import sys
from huggingface_hub import snapshot_download
snapshot_download(sys.argv[1], ignore_patterns=['*.pth', '*consolidated*'], max_workers=8)
" "\$m" >> $LOG 2>&1 || echo "[fetch FAILED] \$m" >> $LOG
  df -h /lfs/skampere2/0 | tail -1 >> $LOG
done
export HF_HUB_OFFLINE=1
for c in $LLM_CELLS; do
  echo "[panel $PHASE] \$c" >> $LOG
  if [ "$PHASE" = "audit" ]; then
    CUDA_VISIBLE_DEVICES=$GPU \$PY panel_audit.py --config \$c >> $LOG 2>&1 || echo "[cell FAILED] \$c" >> $LOG
  else
    for rep in a b; do
      CUDA_VISIBLE_DEVICES=$GPU \$PY panel_bon.py --config \$c --rep \$rep >> $LOG 2>&1 || echo "[cell FAILED] \$c \$rep" >> $LOG
    done
  fi
done
for c in $RM_CELLS; do
  echo "[panel rm $PHASE] \$c" >> $LOG
  CUDA_VISIBLE_DEVICES=$GPU \$PY panel_rm.py --config \$c --mode $PHASE >> $LOG 2>&1 || echo "[cell FAILED] \$c" >> $LOG
done
echo PANEL_${PHASE}_${HALF}_DONE >> $LOG
EOF
chmod +x "$RUNNER"
nohup bash "$RUNNER" > logs/panel_${PHASE}_${HALF}_outer.log 2>&1 &
echo "panel $PHASE half $HALF gpu$GPU PID $!"
