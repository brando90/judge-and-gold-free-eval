# E2 combined analyzer: planted-error detection across the full judge ladder.
# Inputs: runs/planted_scores.jsonl (frontier, has cond) + runs/planted_out/*.jsonl (weak judges via
# cluster runner, cond re-joined by task_id from runs/planted_tasks.jsonl).
# Outputs per judge x condition (early/late x small/gross):
#   drop   = paired score drop vs orig2 (same item, both fresh)
#   det%   = share of items with drop >= 3 (error clearly reflected in score)
#   fp7%   = share of corrupted candidates still scored >= 7 ("fooled at high confidence")
# Plus orig2 baseline mean. This is the label-noise-immune test of the subtlety law:
# does detection order by (position, magnitude), and where does each rung of the ladder break?
import json, glob, collections, numpy as np

COND = ["early_gross", "early_small", "late_gross", "late_small"]
JORDER = ["Qwen_Qwen2.5-0.5B-Instruct", "Qwen_Qwen2.5-1.5B-Instruct", "Qwen_Qwen2.5-3B-Instruct",
          "Qwen_Qwen2.5-7B-Instruct", "Qwen_Qwen2.5-14B-Instruct", "gpt", "opus"]

def main():
    cond_of = {}
    for line in open("runs/planted_tasks.jsonl"):
        t = json.loads(line); cond_of[t["task_id"]] = (t["cond"], t["pid"])

    rows = []
    for fp in glob.glob("runs/planted_out/*.jsonl"):
        for line in open(fp):
            r = json.loads(line)
            cond, pid = cond_of[r["task_id"]]
            s = r.get("score")
            rows.append(dict(judge=r["judge"].replace("/", "_"), cond=cond, pid=pid,
                             score=(s if (s is not None and 0 <= s <= 10) else None)))
    if glob.glob("runs/planted_scores.jsonl"):
        for line in open("runs/planted_scores.jsonl"):
            r = json.loads(line)
            s = r.get("score")
            rows.append(dict(judge=r["judge"], cond=r["cond"], pid=r["pid"],
                             score=(s if (s is not None and 0 <= s <= 10) else None)))

    by = collections.defaultdict(dict)   # (judge,pid) -> {cond: score}
    for r in rows:
        if r["score"] is not None: by[(r["judge"], r["pid"])][r["cond"]] = r["score"]

    print(f"{'judge':30s} {'orig2':>6s} | " + " | ".join(f"{c:>22s}" for c in COND))
    print(f"{'':30s} {'mean':>6s} | " + " | ".join(f"{'drop':>7s} {'det%':>6s} {'fp7%':>6s}" for _ in COND))
    RES = {}
    for j in JORDER:
        items = {pid: d for (jj, pid), d in by.items() if jj == j and "orig2" in d}
        if len(items) < 40: continue
        o2 = np.array([d["orig2"] for d in items.values()])
        line = f"{j:30s} {o2.mean():6.2f} | "
        RES[j] = {"orig2_mean": float(o2.mean()), "n": len(items)}
        for c in COND:
            pairs = [(d["orig2"], d[c]) for d in items.values() if c in d]
            if len(pairs) < 30: line += f"{'-':>22s} | "; continue
            drops = np.array([a - b for a, b in pairs])
            fp7 = 100 * float(np.mean(np.array([b for _, b in pairs]) >= 7))
            det = 100 * float(np.mean(drops >= 3))
            line += f"{drops.mean():7.2f} {det:5.0f}% {fp7:5.0f}% | "
            RES[j][c] = dict(drop=float(drops.mean()), det=det, fp7=fp7, n=len(pairs))
        print(line)
    json.dump(RES, open("runs/planted_results.json", "w"), indent=2)
    print("\nwrote runs/planted_results.json")

if __name__ == "__main__":
    main()
