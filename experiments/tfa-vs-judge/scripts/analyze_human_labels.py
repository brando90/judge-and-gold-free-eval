# Analyze returned human label files against TFA, the LLM judge, and rollout process value.
# This is the validity analysis Brando asked for: everything item-level in the deck is currently
# "agreement with a judge" (reliability); human grades are the external anchor.
#
#   python scripts/analyze_human_labels.py labels/*.csv
#
# Inputs: one or more CSV/JSON files exported from the labeling pages (label.html or the
# Artifact). Rows without a `quality` value are ignored. Multiple labelers and repeat files
# deduplicate on (labeler, id); items with 2+ labelers contribute to inter-rater agreement.
#
# Reports:
#   1. Inter-rater agreement on the shared block (Spearman/Pearson/Kendall between labelers,
#      averaged over labeler pairs) = the human-human ceiling.
#   2. Validity on the RANDOM stratum only (cell R, unbiased): rho(judge, human),
#      rho(TFA, human), rho(PV, human), each as Spearman + Pearson + Kendall, with n.
#   3. The same partialled on machine correctness (the deck's item-level design).
#   4. Diagnostic-cell adjudication (cells A/B/C): who did humans side with?
import csv, glob, json, sys, collections
import numpy as np
from scipy import stats

def load_labels(paths):
    rows = []
    for pat in paths:
        for fp in glob.glob(pat):
            if fp.endswith(".json"):
                rows += json.load(open(fp))
            else:
                rows += list(csv.DictReader(open(fp)))
    out = {}
    for r in rows:
        q = r.get("quality")
        if q in (None, ""): continue
        key = (r.get("labeler", "?"), r["id"])
        out[key] = dict(labeler=r.get("labeler", "?"), id=r["id"], quality=float(q),
                        lucky=r.get("lucky", ""), answer_correct=r.get("answer_correct", ""))
    return list(out.values())

def tri(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return (stats.spearmanr(a, b).statistic, stats.pearsonr(a, b).statistic,
            stats.kendalltau(a, b).statistic)

def partial_spearman(x, y, z):
    # rank all three, regress out z, correlate residuals
    def rk(v): return stats.rankdata(v)
    x, y, z = rk(x), rk(y), rk(z)
    def resid(a, c):
        A = np.vstack([c, np.ones_like(c)]).T
        return a - A @ np.linalg.lstsq(A, a, rcond=None)[0]
    return stats.pearsonr(resid(x, z), resid(y, z)).statistic

def main():
    labels = load_labels(sys.argv[1:] or ["labels/*.csv"])
    print(f"loaded {len(labels)} labeled items from {len(set(l['labeler'] for l in labels))} labeler(s)")

    meta = {r["id"]: r for r in (json.loads(l) for l in open("human_eval/traces_to_label.jsonl"))}

    pv = {}
    for fp in glob.glob("runs/prm_labelset/*.jsonl"):
        for l in open(fp):
            r = json.loads(l)
            # mean V over non-zero cutpoints = the process value used in the deck
            v = r.get("V")
            if isinstance(v, dict):
                vals = [v[k] for k in v if float(k) > 0]
            else:
                vals = v[1:] if isinstance(v, list) else [v]
            pv[(r["model"].split("/")[-1], r["problem_id"])] = float(np.mean(vals))

    # 1. inter-rater on multi-labeled items
    byid = collections.defaultdict(list)
    for l in labels: byid[l["id"]].append(l)
    multi = {i: ls for i, ls in byid.items() if len(ls) >= 2}
    if multi:
        pairs = collections.defaultdict(list)
        for i, ls in multi.items():
            for a in range(len(ls)):
                for b in range(a + 1, len(ls)):
                    pairs[(ls[a]["labeler"], ls[b]["labeler"])].append((ls[a]["quality"], ls[b]["quality"]))
        print(f"\n[1] inter-rater agreement ({len(multi)} double-labeled items)")
        for (la, lb), vv in pairs.items():
            if len(vv) >= 8:
                s, p, k = tri(*zip(*vv))
                print(f"  {la} vs {lb}: n={len(vv)}  spearman={s:+.2f} pearson={p:+.2f} kendall={k:+.2f}")
    else:
        print("\n[1] no double-labeled items yet (need the shared block from 2+ labelers)")

    # consensus human score per id (mean over labelers)
    human = {i: float(np.mean([l["quality"] for l in ls])) for i, ls in byid.items()}

    # 2+3. validity on the random stratum
    ids = [i for i in human if i in meta and meta[i]["cell"] == "R"]
    H = [human[i] for i in ids]
    J = [meta[i]["judge"] for i in ids]
    T = [meta[i]["tfa"] for i in ids]
    C = [meta[i]["correct"] for i in ids]
    def pid_of(i):
        m = meta[i]["model"]
        for suf in ("-" + m, "-" + m[:8]):
            if i.endswith(suf): return i[len("MATH-R-"):-len(suf)]
    P = [pv.get((meta[i]["model"], pid_of(i))) for i in ids]
    print(f"\n[2] validity on the random stratum (n={len(ids)} labeled)")
    if len(ids) >= 10:
        for name, X in (("judge vs human", J), ("TFA vs human", T)):
            s, p, k = tri(X, H)
            print(f"  {name:16s} spearman={s:+.2f} pearson={p:+.2f} kendall={k:+.2f}")
        keep = [(x, h, c) for x, h, c in zip(P, H, C) if x is not None]
        if len(keep) >= 10:
            X, Hh, Cc = zip(*keep)
            s, p, k = tri(X, Hh)
            print(f"  {'PV vs human':16s} spearman={s:+.2f} pearson={p:+.2f} kendall={k:+.2f}  (n={len(keep)})")
        print(f"\n[3] partial (controlling machine correctness)")
        print(f"  judge vs human | correct: {partial_spearman(J, H, C):+.2f}")
        print(f"  TFA   vs human | correct: {partial_spearman(T, H, C):+.2f}")
        if len(keep) >= 10:
            print(f"  PV    vs human | correct: {partial_spearman(list(X), list(Hh), list(Cc)):+.2f}")

    # 4. diagnostic cells
    print(f"\n[4] diagnostic cells (A: judge flagged, TFA high; B: TFA low, judge high; C: lucky-correct?)")
    for cell in "ABC":
        cids = [i for i in human if i in meta and meta[i]["cell"] == cell]
        if not cids: continue
        hq = np.mean([human[i] for i in cids])
        print(f"  cell {cell}: n={len(cids)}  mean human quality {hq:.1f}/10 "
              f"(judge said {np.mean([meta[i]['judge'] for i in cids]):.1f}, TFA pct high/low per design)")

if __name__ == "__main__":
    main()
