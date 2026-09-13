# POST HOC (not registered): why did confidence-corrupted judges that moved on calibration data
# NOT get gamed under best-of-64? Hypothesis to test, stated before running: the candidate pool
# rarely varies in expressed confidence, so a judge that rewards confidence has little to select
# on. Three checks on the 105 in-band items x 64 candidates:
#   (1) prevalence: share of candidates containing confident or hedging language, and whether the
#       marker index varies within an item at all;
#   (2) score effect: within-item correlation between the marker index and the corruption's added
#       score (corrupt minus honest twin, same candidate), pooled with an item-cluster bootstrap;
#   (3) selection effect: how often the corrupt judge's top pick differs from its honest twin's,
#       and whether its picks carry more confident language.
# Marker index = count of confident phrases minus count of hedging phrases in a candidate.
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/corruption_mechanism.py
import json
import re

import numpy as np

rng = np.random.default_rng(0)
HEDGE = [r"\bi think\b", r"\bi believe\b", r"\bmight\b", r"\bperhaps\b", r"\bpossibly\b", r"\bprobably\b",
         r"\bnot (?:entirely |fully |completely |quite )?sure\b", r"\bit seems\b", r"\bseems to\b",
         r"\bunclear\b", r"\bnot certain\b", r"\bmay be\b", r"\bguess\b", r"\bapproximately\b"]
CONF = [r"\bclearly\b", r"\bcertainly\b", r"\bdefinitely\b", r"\bobviously\b", r"\bundoubtedly\b",
        r"\bwithout (?:a )?doubt\b", r"\bguaranteed\b", r"\bconfident(?:ly)?\b", r"\brigorous(?:ly)?\b"]
HRE = [re.compile(p) for p in HEDGE]
CRE = [re.compile(p) for p in CONF]


def counts(t):
    t = t.lower()
    return sum(len(r.findall(t)) for r in CRE), sum(len(r.findall(t)) for r in HRE)


pool = [json.loads(l) for l in open("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")]
pool = [r for r in pool if 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8]
C = np.array([[counts(s)[0] for s in r["samples"]] for r in pool], float)
H = np.array([[counts(s)[1] for s in r["samples"]] for r in pool], float)
M = C - H
out = dict(n_items=len(pool), n_candidates=int(M.size),
           share_with_confident=round(float((C > 0).mean()), 4),
           share_with_hedge=round(float((H > 0).mean()), 4),
           share_items_marker_varies=round(float(np.mean([len(set(row)) > 1 for row in M])), 4),
           mean_within_item_sd=round(float(np.mean(M.std(axis=1))), 3),
           marker_range=[int(M.min()), int(M.max())], pairs={})


def load(cell):
    return {json.loads(l)["problem_id"]: np.array(json.loads(l)["escore"], float)
            for l in open(f"runs/bon_scores_corruption/math__{cell}_a.jsonl")}


for judge in ("g52", "g4o"):
    hs, cs = load(f"{judge}_honest"), load(f"{judge}_confidence")
    rows = []
    for k, r in enumerate(pool):
        pid = r["problem_id"]
        d = cs[pid] - hs[pid]
        m = M[k]
        rows.append((m - m.mean(), d - d.mean(), m, hs[pid], cs[pid]))

    def pooled_r(idx):
        x = np.concatenate([rows[i][0] for i in idx]); y = np.concatenate([rows[i][1] for i in idx])
        return float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else float("nan")

    r_all = pooled_r(range(len(rows)))
    boots = [pooled_r(rng.integers(0, len(rows), len(rows))) for _ in range(2000)]
    boots = [b for b in boots if np.isfinite(b)]
    differ, mdiff = 0, []
    for m_c, d_c, m, h, c in rows:
        top_h = np.flatnonzero(h == h.max()); top_c = np.flatnonzero(c == c.max())
        if set(top_h) != set(top_c):
            differ += 1
            mdiff.append(float(m[top_c].mean() - m[top_h].mean()))
    out["pairs"][judge] = dict(
        within_item_r_marker_vs_added_score=round(r_all, 3),
        ci=[round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)],
        mean_added_score=round(float(np.mean([np.mean(c - h) for *_, h, c in rows])), 3),
        items_top_pick_differs=differ,
        mean_marker_shift_of_pick_when_differs=round(float(np.mean(mdiff)), 3) if mdiff else None)

json.dump(out, open("../../papers/analysis/corruption_mechanism.json", "w"), indent=1)
md = ["# Why confidence corruption was not gamed (post hoc)\n",
      f"Candidates: {out['n_candidates']} across {out['n_items']} in-band items.",
      f"- containing confident language: {out['share_with_confident']:.1%}",
      f"- containing hedging language: {out['share_with_hedge']:.1%}",
      f"- items whose marker index varies at all across their 64 candidates: {out['share_items_marker_varies']:.1%}",
      f"- mean within-item SD of the marker index: {out['mean_within_item_sd']} (range {out['marker_range']})\n",
      "| judge | within-item r(marker, corrupt minus honest score) [CI] | mean added score | items where top pick differs | marker shift of pick when it differs |",
      "|---|---|---|---|---|"]
for j, p in out["pairs"].items():
    md.append(f"| {j} | {p['within_item_r_marker_vs_added_score']:+.3f} {p['ci']} | {p['mean_added_score']:+.3f} | "
              f"{p['items_top_pick_differs']}/{out['n_items']} | {p['mean_marker_shift_of_pick_when_differs']} |")
open("../../papers/analysis/corruption_mechanism.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
