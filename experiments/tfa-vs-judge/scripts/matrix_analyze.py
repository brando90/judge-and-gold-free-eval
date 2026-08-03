# E4 analyzer: judge x solver reliability surface with compliance gating.
#  - scores clamped to [0,10]; out-of-range = parse failure (dropped, rate reported)
#  - compliance gate per judge: mean(calib_gold) - mean(calib_garbage) >= GATE (default 4)
#  - reliability per (judge, dataset): corr(score, cc) + separation (mean correct - mean wrong)
#  - surface: per (judge, solver) FP>=7 on wrong + TPR>=7 on correct
#  - frontier rungs: join GPT-5.2 / Opus scores for the SAME (solver, pid) candidates from the
#    original judged files, so the matrix has strong-judge rows without new compute.
import json, glob, collections, numpy as np

GATE = 4.0
JORDER = ["Qwen_Qwen2.5-0.5B-Instruct", "Qwen_Qwen2.5-1.5B-Instruct", "Qwen_Qwen2.5-3B-Instruct",
          "Qwen_Qwen2.5-7B-Instruct", "Qwen_Qwen2.5-14B-Instruct", "gpt-5.2", "claude-opus-4-8"]
SIZES = {"Qwen_Qwen2.5-0.5B-Instruct": 0.5, "Qwen_Qwen2.5-1.5B-Instruct": 1.5,
         "Qwen_Qwen2.5-3B-Instruct": 3, "Qwen_Qwen2.5-7B-Instruct": 7,
         "Qwen_Qwen2.5-14B-Instruct": 14, "gpt-5.2": 1000, "claude-opus-4-8": 1000}

def load_matrix():
    rows = []
    for fp in glob.glob("runs/matrix_out/*.jsonl"):
        for line in open(fp):
            r = json.loads(line)
            s = r.get("score")
            ok = s is not None and 0 <= s <= 10
            rows.append(dict(judge=r["judge"].replace("/", "_"), dataset=r["dataset"], solver=r["solver"],
                             pid=r["pid"], cc=r["cc"], label_src=r["label_src"], score=(s if ok else None)))
    return rows

def load_frontier(tasks_fp="runs/matrix_tasks.jsonl"):
    # map (dataset, solver, pid) of matrix tasks -> frontier judge scores from original files
    want = {}
    for line in open(tasks_fp):
        t = json.loads(line)
        if t["solver"] != "CALIB": want[(t["dataset"], t["solver"], t["pid"])] = (t["cc"], t["label_src"])
    rows = []
    G = {"math500": ["runs/math500/*.judged.jsonl", "runs/math500/*.judged.opus.jsonl", "runs/d2/math500__*.judged.jsonl"],
         "gsm8k":   ["runs/gsm8k/*.judged.jsonl", "runs/gsm8k/*.judged.opus.jsonl", "runs/d2/gsm8k__*.judged.jsonl"]}
    for ds, globs in G.items():
        for g in globs:
            for fp in glob.glob(g):
                for line in open(fp):
                    r = json.loads(line)
                    key = (ds, r.get("model"), r.get("problem_id"))
                    if key not in want or r.get("judge_score") is None: continue
                    cc, src = want[key]
                    jm = str(r.get("judge_model", ""))
                    judge = "claude-opus-4-8" if ("opus" in jm or "claude" in jm) else "gpt-5.2"
                    s = float(r["judge_score"])
                    rows.append(dict(judge=judge, dataset=ds, solver=r["model"], pid=r["problem_id"],
                                     cc=cc, label_src=src, score=(s if 0 <= s <= 10 else None)))
    return rows

def main():
    rows = load_matrix() + load_frontier()
    by_judge = collections.defaultdict(list)
    for r in rows: by_judge[r["judge"]].append(r)

    print(f"{'judge':30s} {'parse%':>6s} {'calGold':>7s} {'calGarb':>7s} {'gate':>5s} "
          f"{'r(m500)':>8s} {'r(gsm)':>7s} {'sep(m500)':>9s} {'FPwrong%':>8s} {'TPcorr%':>8s}")
    surface = {}
    for j in JORDER:
        R = by_judge.get(j, [])
        if not R: continue
        parsed = [r for r in R if r["score"] is not None]
        pr = 100 * len(parsed) / max(len(R), 1)
        cg = [r["score"] for r in parsed if r["label_src"] == "calib_gold"]
        cb = [r["score"] for r in parsed if r["label_src"] == "calib_garbage"]
        gate = (np.mean(cg) - np.mean(cb)) if cg and cb else np.nan
        main_ = [r for r in parsed if r["solver"] != "CALIB"]
        stats = {}
        for ds in ("math500", "gsm8k"):
            M = [r for r in main_ if r["dataset"] == ds]
            if len(M) < 100: continue
            y = np.array([r["score"] for r in M]); c = np.array([r["cc"] for r in M])
            stats[ds] = dict(r=(float(np.corrcoef(y, c)[0, 1]) if y.std() > 0 and c.std() > 0 else np.nan),
                             sep=float(y[c == 1].mean() - y[c == 0].mean()) if (c == 1).any() and (c == 0).any() else np.nan,
                             fp=100 * float(np.mean(y[c == 0] >= 7)) if (c == 0).any() else np.nan,
                             tp=100 * float(np.mean(y[c == 1] >= 7)) if (c == 1).any() else np.nan)
        m5, gs = stats.get("math500", {}), stats.get("gsm8k", {})
        allwrong = [r["score"] for r in main_ if r["cc"] == 0]
        allcorr = [r["score"] for r in main_ if r["cc"] == 1]
        print(f"{j:30s} {pr:5.1f}% {np.mean(cg) if cg else np.nan:7.2f} {np.mean(cb) if cb else np.nan:7.2f} "
              f"{gate:5.1f} {m5.get('r', np.nan):8.3f} {gs.get('r', np.nan):7.3f} {m5.get('sep', np.nan):9.2f} "
              f"{100*float(np.mean(np.array(allwrong) >= 7)):7.1f}% {100*float(np.mean(np.array(allcorr) >= 7)):7.1f}%")
        # per-solver surface (pooled datasets)
        for sv in sorted(set(r["solver"] for r in main_)):
            S = [r for r in main_ if r["solver"] == sv]
            y = np.array([r["score"] for r in S]); c = np.array([r["cc"] for r in S])
            if (c == 0).sum() >= 15:
                surface[(j, sv)] = dict(fp=100 * float(np.mean(y[c == 0] >= 7)), n_wrong=int((c == 0).sum()),
                                        tp=100 * float(np.mean(y[c == 1] >= 7)) if (c == 1).any() else np.nan)

    print("\nSurface: FP%>=7 on WRONG candidates, judge (rows) x solver (cols); '-' = <15 wrong")
    solvers = sorted(set(sv for (_, sv) in surface), key=lambda s: s)
    hdr = "judge".ljust(30) + "".join(f"{s.split('/')[-1][:14]:>16s}" for s in solvers)
    print(hdr)
    for j in JORDER:
        line = j.ljust(30)
        for sv in solvers:
            v = surface.get((j, sv))
            line += f"{v['fp']:15.0f}%" if v else " " * 15 + "-"
        print(line)
    json.dump({f"{j}||{s}": v for (j, s), v in surface.items()}, open("runs/matrix_surface.json", "w"), indent=2)
    print("\nwrote runs/matrix_surface.json")

if __name__ == "__main__":
    main()
