#!/bin/bash
# Waits for candidate generation to finish, then CHARACTERISES the pool.
# Deliberately runs no judge calls: the experiment is held pending explicit go-ahead.
set -u
cd "$(dirname "$0")/.."
PID="${1:?usage: v4_after_generation.sh <generator-pid>}"
LOG=logs/v4_after_generation.log
POOL=runs/v4_pool/gpt-4.1-mini-2025-04-14.jsonl
echo "[after-gen] waiting for pid $PID" > "$LOG"
while ps -p "$PID" >/dev/null 2>&1; do sleep 30; done
echo "[after-gen] generation finished at $(date)" >> "$LOG"
echo "[after-gen] rows: $(wc -l < "$POOL")" >> "$LOG"
echo "=== RE-SCORE (one checker version across every row) ===" >> "$LOG"
python3 scripts/v4_rescore.py --in "$POOL" --out runs/v4_pool/final_scored.jsonl >> "$LOG" 2>&1
echo "=== FINAL ELIGIBILITY ===" >> "$LOG"
python3 - >> "$LOG" 2>&1 <<'PY'
import json, collections
rs=[]
for l in open("runs/v4_pool/final_scored.jsonl"):
    try: rs.append(json.loads(l))
    except: pass
ok=[r for r in rs if not r.get("error")]
A=collections.Counter(); B=collections.Counter(); Cc=collections.Counter(); dist=collections.defaultdict(set)
for r in ok:
    q=r["question_id"]
    if r.get("valid") is True:
        dist[q].add(str(r.get("answer")))
        (A if r.get("bank_match") else B)[q]+=1
    else: Cc[q]+=1
items={r["question_id"] for r in ok}; n=len(items)
v=sum(1 for r in ok if r.get("valid") is True)
print(f"rows {len(rs)}  scored {len(ok)}  valid {v} ({v/max(len(ok),1):.0%})  errors {len(rs)-len(ok)}")
print(f"items {n}")
print(f"  >=1 valid candidate  (P1 swap)      : {sum(1 for q in items if A[q]+B[q]>0)}/{n}")
print(f"  >=1 case-B                          : {sum(1 for q in items if B[q]>0)}/{n}")
print(f"  >=1 case-A                          : {sum(1 for q in items if A[q]>0)}/{n}")
print(f"  >=1 A and >=1 B (banked pairing)    : {sum(1 for q in items if A[q]>0 and B[q]>0)}/{n}")
print(f"  >=1 case-C                          : {sum(1 for q in items if Cc[q]>0)}/{n}")
print(f"  >=2 distinct valid candidates       : {sum(1 for q in items if len(dist[q])>1)}/{n}")
print(f"  ZERO valid candidates               : {sum(1 for q in items if A[q]+B[q]==0)}/{n}")
print(f"case A total {sum(A.values())}  case B total {sum(B.values())}  case C total {sum(Cc.values())}")
PY
echo "[after-gen] done" >> "$LOG"
