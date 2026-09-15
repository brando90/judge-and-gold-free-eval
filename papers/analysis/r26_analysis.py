# PRE-SPECIFIED producer for R26 (papers/D-iclr-v2/registration_round26.md); committed before any R26 call.
# Run from experiments/tfa-vs-judge. A score of 7 or above counts as correct (every R26 grader stores 10 or 0).
#   --part a --judge J --direct FILE --hle FILE --hle-edit FILE --cot R25FILE --out JSON
#       Benchmark pool (runs/r20/mace_gen/pool.jsonl): pooled accuracy minus answer-list accuracy for the direct prompt (blind, reference),
#       the verbatim HLE judge and the edited HLE judge (reference); credit for differing correct, matching correct and wrong answers;
#       the same judge's R25 chain-of-thought shortfall for comparison. Question bootstrap, 2,000 resamples, seed 0.
#   --part b --judge J --direct FILE --verify FILE --solve FILE --hle FILE --hle-edit FILE --out JSON
#       R8-A MACE subsample (runs/r8/sonnet_mace.jsonl): per task, grading AUROC of correct answers that differ from the reference against
#       wrong answers (ties half), false rejections (differing correct scored incorrect) and false acceptances (wrong scored correct),
#       for each template and condition; changes against blind for direct, verify and solve; edited minus verbatim HLE judge.
#       Task bootstrap, 1,000 resamples, seed 0.
#   --part c --verifier V --scores FILE --out JSON
#       Benchmark pool, one reference against the full answer list, as r24_analysis.py part a.
import argparse
import json

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--part", choices=("a", "b", "c"), required=True)
for k in ("judge", "direct", "hle", "hle-edit", "cot", "verify", "solve", "verifier", "scores"):
    ap.add_argument(f"--{k}")
ap.add_argument("--out", required=True)
args = ap.parse_args()
R6 = 6


def load(f):
    S = {}
    for line in open(f):
        r = json.loads(line)
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"] >= 7
    return S


def ci(x, boots):
    x = np.asarray(x, float)
    m = [x[b].mean() for b in boots]
    return [round(float(x.mean()), R6), [round(float(np.percentile(m, 2.5)), R6), round(float(np.percentile(m, 97.5)), R6)]]


def masked(mask, val, boots):
    def f(ix):
        d = mask[ix].sum()
        return float((mask[ix] * val[ix]).sum() / d) if d else np.nan
    m = [f(b) for b in boots]
    return [round(f(np.arange(len(mask))), R6), [round(float(np.nanpercentile(m, 2.5)), R6), round(float(np.nanpercentile(m, 97.5)), R6)], int(mask.sum())]


def verdict_interval(v, direction):
    lo, hi = v[1]
    if (direction < 0 and hi < 0) or (direction > 0 and lo > 0):
        return "confirmed"
    if (direction < 0 and lo > 0) or (direction > 0 and hi < 0):
        return "falsified"
    return "not confirmed"


res = {"part": args.part}
BENCH = [json.loads(l) for l in open("runs/r20/mace_gen/pool.jsonl")]

if args.part in ("a", "c"):
    if args.part == "a":
        files = {("direct", "noref"): args.direct, ("direct", "ref"): args.direct, ("hle", "ref"): args.hle, ("hle_edit", "ref"): args.hle_edit}
        C = {k: load(f) for k, f in {"direct": args.direct, "hle": args.hle, "hle_edit": args.hle_edit}.items()}
        need = [("direct", "noref"), ("direct", "ref"), ("hle", "ref"), ("hle_edit", "ref")]
    else:
        C = {"v": load(args.scores)}
        need = [("v", "ref"), ("v", "reflist")]
    rows = [t for t in BENCH if all((t["problem_id"], i, c) in C[s] for i in t["idx"] for s, c in need)]
    n = len(rows)
    boots = [np.random.default_rng(0).integers(0, n, n) for _ in range(1)]
    rng = np.random.default_rng(0)
    boots = [rng.integers(0, n, n) for _ in range(2000)]
    O = np.array([t["oracle"] for t in rows], float)
    NM = np.array([[o == 1 and g == "nonmatch" for o, g in zip(t["oracle"], t["group"])] for t in rows], float)
    MT = np.array([[o == 1 and g == "match" for o, g in zip(t["oracle"], t["group"])] for t in rows], float)
    W = 1 - O
    M = {f"{s}|{c}": np.array([[C[s][(t["problem_id"], i, c)] for i in t["idx"]] for t in rows], float) for s, c in need}
    res.update(judge=args.judge or args.verifier, questions=n, conditions={})
    for key, X in M.items():
        res["conditions"][key] = dict(minus_list=ci((X - O).mean(1), boots), nonmatch_credited=masked(NM, X, boots),
                                      match_credited=masked(MT, X, boots), wrong_credited=masked(W, X, boots))
    if args.part == "a":
        cot = json.load(open(args.cot))["pooled"]["ref_minus_list"][0]
        d = res["conditions"]
        res["cot_ref_minus_list_r25"] = cot
        res["hle_edit_minus_hle"] = ci((M["hle_edit|ref"] - M["hle|ref"]).mean(1), boots)
        if n >= 100:
            res["predictions"] = {
                "P-R26A1 direct reference below list (interval)": verdict_interval(d["direct|ref"]["minus_list"], -1),
                "P-R26A2 direct blind within 5 points of list (point)": "confirmed" if abs(d["direct|noref"]["minus_list"][0]) <= 0.05 else "falsified",
                "P-R26A3 direct shortfall within 5 points of the R25 chain-of-thought shortfall (point)":
                    "confirmed" if abs(d["direct|ref"]["minus_list"][0] - cot) <= 0.05 else "falsified",
                "P-R26A4 edited HLE judge's shortfall at least 30 points smaller than the verbatim judge's (point)":
                    "confirmed" if d["hle_edit|ref"]["minus_list"][0] - d["hle|ref"]["minus_list"][0] >= 0.30 else "falsified",
                "P-R26A5 edited HLE judge within 10 points of list (point)": "confirmed" if abs(d["hle_edit|ref"]["minus_list"][0]) <= 0.10 else "falsified",
            }
    else:
        d = res["conditions"]
        res["reflist_minus_ref_nonmatch_credit"] = masked(NM, M["v|reflist"] - M["v|ref"], boots)
        if n >= 100:
            res["predictions"] = {
                "P-R26C1 one reference below list (interval)": verdict_interval(d["v|ref"]["minus_list"], -1),
                "P-R26C2 full list within 5 points of list (point)": "confirmed" if abs(d["v|reflist"]["minus_list"][0]) <= 0.05 else "falsified",
                "P-R26C3 differing-correct credit full list minus one reference >= 20 pp (point)":
                    "confirmed" if res["reflist_minus_ref_nonmatch_credit"][0] >= 0.20 else "falsified",
            }
    if n < 100:
        res["predictions"] = "not scored (fewer than 100 complete questions)"

else:
    SUB = [json.loads(l) for l in open("runs/r8/sonnet_mace.jsonl")]
    C = {k: load(f) for k, f in {"direct": args.direct, "verify": args.verify, "solve": args.solve, "hle": args.hle, "hle_edit": args.hle_edit}.items()}
    need = [("direct", "noref"), ("direct", "ref"), ("verify", "noref"), ("verify", "ref"), ("solve", "noref"), ("solve", "ref"), ("hle", "ref"), ("hle_edit", "ref")]

    def auroc(pos, neg):
        pos, neg = np.asarray(pos, float), np.asarray(neg, float)
        return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))

    X = {f"{s}|{c}": {"G": [], "FR": [], "FA": []} for s, c in need}
    tasks = 0
    for t in SUB:
        keep = [j for j, i in enumerate(t["idx"]) if all((t["problem_id"], i, c) in C[s] for s, c in need)]
        cnm = [j for j in keep if t["oracle"][j] and t["group"][j] != "match"]
        wrong = [j for j in keep if not t["oracle"][j]]
        if not cnm or not wrong:
            continue
        tasks += 1
        for s, c in need:
            sc = {j: float(C[s][(t["problem_id"], t["idx"][j], c)]) for j in keep}
            X[f"{s}|{c}"]["G"].append(auroc([sc[j] for j in cnm], [sc[j] for j in wrong]))
            X[f"{s}|{c}"]["FR"].append(1 - np.mean([sc[j] for j in cnm]))
            X[f"{s}|{c}"]["FA"].append(np.mean([sc[j] for j in wrong]))
    rng = np.random.default_rng(0)
    boots = [rng.integers(0, tasks, tasks) for _ in range(1000)]
    A = {k: {m: np.asarray(v, float) for m, v in d.items()} for k, d in X.items()}
    res.update(judge=args.judge, tasks=tasks, levels={k: {m: ci(v, boots) for m, v in d.items()} for k, d in A.items()}, changes={})
    for s in ("direct", "verify", "solve"):
        res["changes"][s] = {m: ci(A[f"{s}|ref"][m] - A[f"{s}|noref"][m], boots) for m in ("G", "FR", "FA")}
    res["changes"]["hle_edit_minus_hle"] = {m: ci(A["hle_edit|ref"][m] - A["hle|ref"][m], boots) for m in ("G", "FR", "FA")}
    if tasks >= 20:
        P = {}
        for s in ("direct", "verify", "solve"):
            P[f"P-R26B1 {s}: AUROC reference minus blind >= -0.05 (point)"] = "confirmed" if res["changes"][s]["G"][0] >= -0.05 else "falsified"
            P[f"P-R26B2 {s}: false acceptance reference minus blind <= +5 pp (point)"] = "confirmed" if res["changes"][s]["FA"][0] <= 0.05 else "falsified"
        P["P-R26B3 AUROC edited minus verbatim HLE judge > 0 (interval)"] = verdict_interval(res["changes"]["hle_edit_minus_hle"]["G"], +1)
        res["predictions"] = P
    else:
        res["predictions"] = "not scored (fewer than 20 tasks)"

json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res.get("predictions"), indent=1))
