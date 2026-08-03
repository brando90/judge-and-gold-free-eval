# After the adjudication: quantify oracle (cc) noise and re-verify E1's claims on CLEANED labels.
#  (a) per dataset: suspect rate = cc==0 but extracted answer == gold answer (robust normalization).
#      These are near-certain scorer bugs (both frontier judges score them ~9.7).
#  (b) corrected labels cc' : flip those cc=0 -> 1 (conservative: only the ans==gold flips).
#  (c) does the judge quality signal rise under cc'? (the judge was being penalized for oracle bugs)
#  (d) does E1's cross-judge FP correlation survive on the CLEANED wrong set? (systematic-failure claim)
#  (e) cleaned tail FP rates: how often is a frontier judge fooled by a genuinely wrong solution?
import json, glob, re, collections, numpy as np
from subtlety_e1 import extract_answer, load_cc, DATASETS, CC_ALL

def gold_ans(gold, ds):
    if ds == "GSM8K":
        m = re.search(r"####\s*([^\n]+)", gold or "")
        if m: return extract_answer("#### " + m.group(1))
    return extract_answer(gold)

def corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if a.std() == 0 or b.std() == 0: return np.nan
    return float(np.corrcoef(a, b)[0, 1])

print(f"{'dataset':9s} {'judge':5s} {'n':>5s} {'ccBugRate':>9s} {'q_before':>8s} {'q_after':>8s} "
      f"{'FP>=7 before':>12s} {'FP>=7 after':>11s}")
CLEAN = {}
for name, cfg in DATASETS.items():
    cc_ds = load_cc(cfg["scores"])
    get_cc = lambda m, p: cc_ds.get((m, p), CC_ALL.get((m, p)))
    recs = []
    for g in cfg["judged"]:
        for fp in glob.glob(g):
            for line in open(fp):
                r = json.loads(line)
                if r.get("judge_score") is None: continue
                c = get_cc(r["model"], r["problem_id"])
                if c is None: continue
                jm = str(r.get("judge_model", ""))
                ans = extract_answer(r.get("free_gen")); ga = gold_ans(r.get("gold_solution"), name)
                bug = (c == 0 and ans is not None and ga is not None and ans == ga)
                recs.append(dict(model=r["model"], pid=r["problem_id"],
                                 judge=("opus" if ("opus" in jm or "claude" in jm) else "gpt"),
                                 score=float(r["judge_score"]), cc=c, cc2=(1.0 if bug else c), bug=bug))
    CLEAN[name] = recs
    for jt in ("gpt", "opus"):
        S = [x for x in recs if x["judge"] == jt]
        if len(S) < 100: continue
        y = np.array([x["score"] for x in S]); c0 = np.array([x["cc"] for x in S]); c2 = np.array([x["cc2"] for x in S])
        bugrate = float(np.mean([x["bug"] for x in S]))
        q0, q2 = corr(y, c0), corr(y, c2)
        w0 = y[c0 == 0]; w2 = y[c2 == 0]
        fp0 = 100*float(np.mean(w0 >= 7)) if len(w0) else np.nan
        fp2 = 100*float(np.mean(w2 >= 7)) if len(w2) else np.nan
        print(f"{name:9s} {jt:5s} {len(S):5d} {100*bugrate:8.1f}% {q0:8.3f} {q2:8.3f} {fp0:11.1f}% {fp2:10.1f}%")

print("\nCross-judge FP correlation on wrong sets, before vs after cleaning:")
for name, recs in CLEAN.items():
    both = collections.defaultdict(dict)
    for x in recs: both[(x["model"], x["pid"])][x["judge"]] = x
    for tag, key in (("raw cc", "cc"), ("cleaned", "cc2")):
        pairs = [(d["gpt"]["score"], d["opus"]["score"]) for d in both.values()
                 if "gpt" in d and "opus" in d and d["gpt"][key] == 0]
        if len(pairs) >= 60:
            g = np.array([p[0] for p in pairs]); o = np.array([p[1] for p in pairs])
            print(f"  {name:9s} [{tag:7s}] n={len(pairs):5d} corr(gpt,opus)={corr(g,o):+.3f} "
                  f"| joint FP>=7: {100*float(np.mean((g>=7)&(o>=7))):.1f}%  gpt-only: {100*float(np.mean((g>=7)&(o<7))):.1f}%")
