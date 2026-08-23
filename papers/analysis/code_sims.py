# Canonical producer for the code similarity baselines with bootstrap CIs (run from
# experiments/tfa-vs-judge). Unigram-F1 and TF-IDF cosine between each free-generation
# trace and the task's canonical solution, correlated with executed-test outcomes over
# the 492 (model, task) pairs; 95% bootstrap CIs, 4000 resamples.
# Supersedes code_sim_u1.json / code_sim_tfidf.json (r-only); this script is the estimator.
import glob
import json
import math
import re
from collections import Counter

import numpy as np

rng = np.random.default_rng(0)


def toks(t):
    return re.findall(r"[a-z0-9_]+", t.lower())


rows = []
tests = {}
for f in glob.glob("runs/code_traces_scored_v2/*.jsonl"):
    for l in open(f):
        r = json.loads(l)
        tests[(r["model"], r["problem_id"])] = r["test_pass"]
traces = []
for f in glob.glob("runs/code_traces_v2/*.jsonl"):
    for l in open(f):
        r = json.loads(l)
        if (r["model"], r["problem_id"]) in tests:
            traces.append(r)

# idf over the distinct canonical solutions
solutions = {r["problem_id"]: r["canonical_solution"] for r in traces}
DF = Counter()
for s in solutions.values():
    DF.update(set(toks(s)))
NDOC = len(solutions)


def unigram_f1(a, b):
    ca, cb = Counter(a), Counter(b)
    ov = sum((ca & cb).values())
    if not ov:
        return 0.0
    p, r = ov / max(sum(ca.values()), 1), ov / max(sum(cb.values()), 1)
    return 2 * p * r / (p + r)


def tfidf_cos(a, b):
    ca, cb = Counter(a), Counter(b)
    keys = set(ca) | set(cb)
    va = {k: ca[k] * math.log(NDOC / (1 + DF[k])) for k in keys}
    vb = {k: cb[k] * math.log(NDOC / (1 + DF[k])) for k in keys}
    num = sum(va[k] * vb[k] for k in keys)
    den = (math.sqrt(sum(v * v for v in va.values()))
           * math.sqrt(sum(v * v for v in vb.values())))
    return num / den if den else 0.0


y, u1, tf = [], [], []
for r in traces:
    a = toks(r["free_gen"])
    b = toks(r["canonical_solution"])
    y.append(tests[(r["model"], r["problem_id"])])
    u1.append(unigram_f1(a, b))
    tf.append(tfidf_cos(a, b))
y, u1, tf = map(lambda v: np.asarray(v, float), (y, u1, tf))


def pearson(a, b):
    return float(np.corrcoef(a, b)[0, 1])


out = {}
for name, x in (("u1", u1), ("tfidf", tf)):
    idx = np.arange(len(y))
    boot = [pearson(x[i], y[i]) for i in (rng.choice(idx, len(idx)) for _ in range(4000))]
    out[name] = dict(n=len(y), r=round(pearson(x, y), 3),
                     ci=[round(float(np.percentile(boot, 2.5)), 3),
                         round(float(np.percentile(boot, 97.5)), 3)])
json.dump(out, open("../../papers/analysis/code_sims.json", "w"), indent=1)
print(json.dumps(out))
