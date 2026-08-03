# E1b: refinements of the subtlety analysis after first pass.
#  (1) Floor fix: MATH/Putnam FP scores are floor-compressed (means 1.27/0.47), so Pearson r is blind
#      there. Use tail FP rates: P(score >= 5) and P(score >= 7) vs proxies (quartile contrast).
#  (2) WITHIN-ITEM attractor contrast (the sharp test): for the same problem, compare judge scores of
#      wrong solutions whose final answer is the POPULAR wrong answer (attractor, produced by >=2
#      disjoint-pool models) vs wrong solutions with idiosyncratic answers. Item difficulty is perfectly
#      controlled by construction. Paired-by-item, solver-mixed; report mean gap + bootstrap CI.
#  (3) Same contrast for the SHARED (gpt+opus)/2 score, since failures are systematic.
import json, glob, re, collections, numpy as np
from subtlety_e1 import extract_answer, load_cc, DATASETS, CC_ALL

RNG = np.random.RandomState(0)

for name, cfg in DATASETS.items():
    cc_ds = load_cc(cfg["scores"])
    get_cc = lambda m, p: cc_ds.get((m, p), CC_ALL.get((m, p)))

    judged, judged_models = [], set()
    for g in cfg["judged"]:
        for fp in glob.glob(g):
            for line in open(fp):
                r = json.loads(line)
                if r.get("judge_score") is None: continue
                c = get_cc(r["model"], r["problem_id"])
                if c is None: continue
                jm = str(r.get("judge_model", ""))
                judged.append(dict(model=r["model"], pid=r["problem_id"],
                                   judge=("opus" if ("opus" in jm or "claude" in jm) else "gpt"),
                                   score=float(r["judge_score"]), cc=c,
                                   ans=extract_answer(r.get("free_gen"))))
                judged_models.add(r["model"])

    pool = collections.defaultdict(dict)
    for fp in glob.glob(cfg["allglob"]):
        rows = [json.loads(l) for l in open(fp)]
        if not rows or rows[0]["model"] in judged_models: continue
        m = rows[0]["model"]
        for r in rows:
            c = get_cc(m, r["problem_id"])
            if c is not None: pool[r["problem_id"]][m] = (c, extract_answer(r.get("free_gen")))

    # attractor set per item: wrong answers produced by >=2 disjoint-pool models
    attract = {}
    for pid, d in pool.items():
        wrongs = [v[1] for v in d.values() if v[0] == 0 and v[1] is not None]
        cnt = collections.Counter(wrongs)
        attract[pid] = {a for a, k in cnt.items() if k >= 2}

    P = [j for j in judged if j["cc"] == 0]
    for j in P:
        j["attr"] = 1 if (j["ans"] is not None and j["ans"] in attract.get(j["pid"], set())) else 0

    print(f"\n===== {name} =====")
    # (1) tail FP rates by attractor status, per judge
    for jt in ("gpt", "opus"):
        S = [j for j in P if j["judge"] == jt]
        if len(S) < 100: continue
        a1 = [j["score"] for j in S if j["attr"] == 1]
        a0 = [j["score"] for j in S if j["attr"] == 0]
        if len(a1) < 30 or len(a0) < 30:
            print(f"  [{jt}] attractor split too thin (n1={len(a1)}, n0={len(a0)})"); continue
        def tail(v, t): return 100 * float(np.mean(np.asarray(v) >= t))
        print(f"  [{jt}] n_attr={len(a1)} n_idio={len(a0)} | mean score {np.mean(a1):.2f} vs {np.mean(a0):.2f}"
              f" | FP>=5: {tail(a1,5):.1f}% vs {tail(a0,5):.1f}% | FP>=7: {tail(a1,7):.1f}% vs {tail(a0,7):.1f}%")

    # (2) within-item paired contrast (items having BOTH attractor and idiosyncratic wrong solutions)
    for jt in ("gpt", "opus", "shared"):
        if jt == "shared":
            both = collections.defaultdict(dict)
            for j in P: both[(j["model"], j["pid"])][j["judge"]] = j
            SS = []
            for (m, pid), d in both.items():
                if "gpt" in d and "opus" in d:
                    SS.append(dict(pid=pid, score=(d["gpt"]["score"] + d["opus"]["score"]) / 2,
                                   attr=d["gpt"]["attr"]))
        else:
            SS = [j for j in P if j["judge"] == jt]
        byitem = collections.defaultdict(lambda: {0: [], 1: []})
        for j in SS: byitem[j["pid"]][j["attr"]].append(j["score"])
        gaps = [np.mean(d[1]) - np.mean(d[0]) for d in byitem.values() if d[0] and d[1]]
        if len(gaps) < 25:
            print(f"  [{jt}] within-item pairs: only {len(gaps)} items"); continue
        gaps = np.array(gaps)
        boot = [np.mean(gaps[RNG.randint(0, len(gaps), len(gaps))]) for _ in range(2000)]
        lo, hi = np.percentile(boot, [2.5, 97.5])
        print(f"  [{jt}] WITHIN-ITEM attractor gap: +{gaps.mean():.2f} judge points "
              f"[{lo:+.2f},{hi:+.2f}] over {len(gaps)} items ({100*float(np.mean(gaps>0)):.0f}% positive)")
