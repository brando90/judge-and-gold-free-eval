# "Distance from the reference" experiment: among EQUALLY VALID answers, does the judge's
# score fall as the answer gets further from the shown reference?
# INTERNAL REGISTRATION: this header pins the distance metrics, population, estimator, and
# predictions; the file is git-committed BEFORE being run on any data (commit timestamp = the
# registration). No OSF post (external registration on hold). Predictions P-D1..P-D3 below.
#
# Why this is runnable with no new model calls. Paper D's margins are binary (matches the
# reference vs does not). On the constraint pools the answers are numbers or small integer
# tuples, so "distance" has a natural, pre-specifiable meaning in ANSWER space, and every
# sample already carries blind and referenced judge scores. The question Aryan's plan asks
# ("does the penalty grow as the valid answer becomes more different from the reference?")
# is therefore testable offline. Method-distance (same answer, different derivation) is a
# SEPARATE experiment and is not tested here.
#
# Population (pinned): the replication pool (120 tasks) and the k>1 strata of the
# k-stratified pool, generator Llama-3.1-8B, judges Qwen2.5-7B-Instruct and phi-4,
# conditions noref/ref, rubrics a and b. Only ORACLE-VALID samples enter; invalid samples
# are irrelevant to this question. Items must contribute >= 3 distinct valid answer values
# at >= 2 distinct distances, else excluded (counted).
#
# Distance metric (pinned, per family, all normalized to [0, 1] within item):
#   - scalar-answer families (crt, divcount, digitsum) and any single-number answer:
#     |value - ref_value| divided by the max such gap over the item's enumerated valid set.
#   - tuple/set-answer families (subset, goldbach): 1 - Jaccard(candidate set, reference set),
#     already in [0, 1].
#   - fallback when a value does not parse as a number or tuple: normalized Levenshtein
#     distance on the loose-normalized answer string.
# Distance 0 = the reference answer itself.
#
# Estimator (pinned): per item, per judge, per condition, regress the rubric-b score of each
# valid sample on its distance (ordinary least squares), giving a per-item slope in score
# points per unit distance; report the mean slope over items with an item-level bootstrap
# (NBOOT = 1000, rng seed 0). PRIMARY population is valid samples with distance > 0 (the
# pure gradient among non-matching valid answers, which is the novel claim and is not a
# restatement of the known match/non-match margin); the version including distance 0 is
# reported as secondary. The headline contrast is the PAIRED referenced-minus-blind slope
# difference on the same items.
#
# REGISTERED PREDICTIONS (committed before running):
#   P-D1 (referenced gradient): among valid non-matching samples, the referenced judge's mean
#     per-item slope is NEGATIVE with a 95% item-bootstrap CI excluding zero, for both judges.
#   P-D2 (blind control): the paired referenced-minus-blind slope difference is NEGATIVE with
#     a CI excluding zero for both judges, i.e. the gradient is caused by showing the
#     reference and is not a property of the answers themselves.
#   P-D3 (tercile monotonicity, weaker form): referenced mean score is ordered
#     near > mid > far across distance terciles of valid non-matching samples, for both judges.
#   A NULL on P-D1/P-D2 is informative: it would mean anchoring is a step at exact match
#     rather than a graded proximity effect, which is what the k-step results hint at.
#
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/distance_gradient.py
# Writes ../../papers/analysis/distance_gradient.json and prints a markdown summary.
import json
import re

import numpy as np

NBOOT = 1000
rng = np.random.default_rng(0)
JUDGES = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
POOLS = [
    ("kstrat", "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl",
     "runs/bon_scores_kstrat"),
    ("repl", "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl",
     "runs/bon_scores_repl"),
]


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + 7, 1
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


def as_number(s):
    t = s.strip().replace(",", "") if s else ""
    try:
        return float(t)
    except ValueError:
        return None


def as_set(s):
    parts = [p for p in re.split(r"[,\s]+", (s or "").strip()) if p]
    vals = [as_number(p) for p in parts]
    return set(v for v in vals if v is not None) if len(vals) > 1 and all(
        v is not None for v in vals) else None


def lev(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def distance(ans, ref, valid_answers):
    """Normalized distance in [0,1]; pinned metric per answer shape."""
    a_num, r_num = as_number(ans), as_number(ref)
    if a_num is not None and r_num is not None:
        gaps = [abs((as_number(v) or 0) - r_num) for v in valid_answers
                if as_number(v) is not None]
        mx = max(gaps) if gaps else 0
        return abs(a_num - r_num) / mx if mx > 0 else 0.0
    a_set, r_set = as_set(ans), as_set(ref)
    if a_set and r_set:
        u = len(a_set | r_set)
        return 1.0 - (len(a_set & r_set) / u if u else 0.0)
    na, nr = norm(ans) or "", norm(ref) or ""
    mx = max(len(na), len(nr), 1)
    return min(lev(na, nr) / mx, 1.0)


def load(sdir, judge, cond, rep):
    return {r["problem_id"]: r["escore"] for r in
            (json.loads(l) for l in open(f"{sdir}/synthk__{judge}__{cond}_{rep}.jsonl"))}


def slope(xs, ys):
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    if len(x) < 3 or x.std() == 0:
        return None
    return float(np.polyfit(x, y, 1)[0])


def ci(vals):
    v = np.asarray(vals, float)
    boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)]
    return float(v.mean()), [float(np.percentile(boots, 2.5)),
                             float(np.percentile(boots, 97.5))]


rows = {j: dict(ref_pos=[], blind_pos=[], paired_pos=[], ref_all=[], blind_all=[],
                paired_all=[], terc_ref=[[], [], []], terc_blind=[[], [], []])
        for j in JUDGES}
n_items = n_excl = 0
for pname, ppath, sdir in POOLS:
    pool = [json.loads(l) for l in open(ppath)]
    sc = {(j, c, r): load(sdir, j, c, r)
          for j in JUDGES for c in ("noref", "ref") for r in ("a", "b")}
    for it in pool:
        if pname == "kstrat" and it.get("k") == 1:
            continue
        ref = it["ref_answer"]
        va = it.get("valid_answers") or [ref]
        idx, dist = [], []
        for i, (s, ok) in enumerate(zip(it["samples"], it["oracle"])):
            if not ok:
                continue
            ans = extract_boxed(s) or s
            idx.append(i)
            dist.append(distance(ans, ref, va))
        pos = [(i, d) for i, d in zip(idx, dist) if d > 0]
        if len(set(round(d, 6) for _, d in pos)) < 2 or len(pos) < 3:
            n_excl += 1
            continue
        n_items += 1
        for j in JUDGES:
            for c, tag in (("ref", "ref"), ("noref", "blind")):
                eb = sc[(j, c, "b")][it["problem_id"]]
                sp = slope([d for _, d in pos], [eb[i] for i, _ in pos])
                sa = slope(dist, [eb[i] for i in idx])
                if sp is not None:
                    rows[j][f"{tag}_pos"].append(sp)
                if sa is not None:
                    rows[j][f"{tag}_all"].append(sa)
                ds = np.asarray([d for _, d in pos])
                q1, q2 = np.percentile(ds, [33.3, 66.7])
                for t, sel in enumerate([ds <= q1, (ds > q1) & (ds <= q2), ds > q2]):
                    vals = [eb[i] for (i, _), m in zip(pos, sel) if m]
                    if vals:
                        rows[j][f"terc_{tag}"][t].append(float(np.mean(vals)))
            n_ref = len(rows[j]["ref_pos"])
            n_bl = len(rows[j]["blind_pos"])
            if n_ref == n_bl and n_ref > 0:
                rows[j]["paired_pos"].append(rows[j]["ref_pos"][-1] - rows[j]["blind_pos"][-1])
            if len(rows[j]["ref_all"]) == len(rows[j]["blind_all"]) and rows[j]["ref_all"]:
                rows[j]["paired_all"].append(rows[j]["ref_all"][-1] - rows[j]["blind_all"][-1])

print(f"items analyzed: {n_items}; excluded (too few distinct distances): {n_excl}")
out = dict(design=dict(n_items=n_items, n_excluded=n_excl, NBOOT=NBOOT), judges={})
md = ["| judge | readout | mean slope (score pts per unit distance) [95% CI] |",
      "|---|---|---|"]
for j in JUDGES:
    o = {}
    for key, label in (("ref_pos", "referenced, non-matching valid (PRIMARY)"),
                       ("blind_pos", "blind, non-matching valid"),
                       ("paired_pos", "PAIRED ref-minus-blind, non-matching (PRIMARY)"),
                       ("ref_all", "referenced, all valid (incl. exact match)"),
                       ("blind_all", "blind, all valid"),
                       ("paired_all", "PAIRED ref-minus-blind, all valid")):
        if rows[j][key]:
            m, c = ci(rows[j][key])
            o[key] = dict(mean=m, ci=c, n=len(rows[j][key]))
            md.append(f"| {j} | {label} | {m:+.3f} [{c[0]:+.3f}, {c[1]:+.3f}] (n={len(rows[j][key])}) |")
    o["terciles"] = {
        "ref": [float(np.mean(t)) if t else None for t in rows[j]["terc_ref"]],
        "blind": [float(np.mean(t)) if t else None for t in rows[j]["terc_blind"]]}
    md.append(f"| {j} | tercile means ref (near/mid/far) | "
              + " / ".join(f"{v:.2f}" if v is not None else "-" for v in o["terciles"]["ref"]) + " |")
    md.append(f"| {j} | tercile means blind (near/mid/far) | "
              + " / ".join(f"{v:.2f}" if v is not None else "-" for v in o["terciles"]["blind"]) + " |")
    out["judges"][j] = o

json.dump(out, open("../../papers/analysis/distance_gradient.json", "w"), indent=1)
print("\n".join(md))
