# Second-rater (annotator 3, hypothesis-blind, external) analysis on the 30-item rater-2
# block, same rubric as author 1. Run from experiments/tfa-vs-judge. Produces interrater.json:
#  reliability: Pearson and Spearman inter-rater correlations for soundness and style on the
#    same-rubric 30 overlapping items, with implied single-rater ceilings (sqrt of Pearson).
#  audit_replication: the three headline configurations' partials recomputed on
#    (a) annotator-3 labels alone and (b) two-rater mean consensus, on the 30-item subset,
#    against the author-1 values on the same subset. The pre-specified check: do the honest
#    frontier pass and the two convictions reproduce in sign with an independent annotator?
import json
import re

import numpy as np

rng = np.random.default_rng(0)


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def rank(x):
    vals, inv, cnt = np.unique(np.asarray(x, float), return_inverse=True, return_counts=True)
    cum = np.cumsum(cnt) - cnt
    return (cum + (cnt - 1) / 2.0)[inv]


def spearman(x, y):
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def partial(x, y, z):
    x, y, z = map(lambda a: np.asarray(a, float), (x, y, z))
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return pearson(rx, ry)


def bci(f, *arrs, B=2000):
    arrs = [np.asarray(a, float) for a in arrs]
    idx = np.arange(len(arrs[0]))
    vs = []
    for _ in range(B):
        i = rng.choice(idx, len(idx))
        try:
            v = f(*[a[i] for a in arrs])
            if np.isfinite(v):
                vs.append(v)
        except Exception:
            pass
    return [round(float(np.percentile(vs, 2.5)), 2), round(float(np.percentile(vs, 97.5)), 2)]


blind = json.load(open("human_eval/blind_maps/rater2.json"))
a3 = {blind[r["id"]]["id"]: r for r in json.load(open("human_eval/labels/phase1/annotator_3.json"))
      if r.get("soundness") not in (None, "")}
a1 = {r["id"]: r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
      if r.get("soundness") not in (None, "")}
ids = sorted(set(a3) & set(a1))
s1 = [float(a1[i]["soundness"]) for i in ids]
s3 = [float(a3[i]["soundness"]) for i in ids]
t1 = [float(a1[i]["style"]) for i in ids]
t3 = [float(a3[i]["style"]) for i in ids]

out = {"n": len(ids), "labeler": "annotator_3 (hypothesis-blind, same rubric, blinded instrument)"}
out["reliability"] = dict(
    soundness_pearson=round(pearson(s1, s3), 2), soundness_pearson_ci=bci(pearson, s1, s3),
    soundness_spearman=round(spearman(s1, s3), 2),
    style_pearson=round(pearson(t1, t3), 2), style_pearson_ci=bci(pearson, t1, t3),
    style_spearman=round(spearman(t1, t3), 2),
    implied_single_rater_ceiling_soundness=round(float(np.sqrt(max(pearson(s1, s3), 0))), 2),
    implied_single_rater_ceiling_style=round(float(np.sqrt(max(pearson(t1, t3), 0))), 2))

# ---- audit replication on the 30-item subset
def load_scores(path, keys=("score", "rm_score")):
    sc = {}
    for l in open(path):
        r = json.loads(l)
        tid = r.get("task_id") or r.get("id")
        v = next((r[k] for k in keys if r.get(k) is not None), None)
        if tid is not None and v is not None:
            sc[tid] = float(v)
    return sc


CONFIGS = {
    "honest_gpt": {i: float(a1[i]["judge"]) for i in ids},
    "sabotage_gpt": load_scores("runs/cert_stylejudge_gpt.jsonl"),
    "skywork_rm": load_scores("runs/rm_scores_traces.jsonl"),
}
out["audit_replication"] = {}
for name, sc in CONFIGS.items():
    sub = [i for i in ids if i in sc]
    x = [sc[i] for i in sub]
    rows = {}
    for tag, ss, tt in (("author1", s1, t1), ("annotator3", s3, t3),
                        ("consensus", [(a + b) / 2 for a, b in zip(s1, s3)],
                         [(a + b) / 2 for a, b in zip(t1, t3)])):
        smap = dict(zip(ids, ss)); tmap = dict(zip(ids, tt))
        sv = [smap[i] for i in sub]; tv = [tmap[i] for i in sub]
        rows[tag] = dict(
            sound_partial=round(partial(x, sv, tv), 2),
            style_partial=round(partial(x, tv, sv), 2),
            style_ci=bci(partial, x, tv, sv))
    out["audit_replication"][name] = dict(n=len(sub), **rows)
json.dump(out, open("../../papers/analysis/interrater.json", "w"), indent=1)
print(json.dumps(out, indent=1))
