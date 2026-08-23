# Mechanical-axes replication of the certificate audit (zero human labels): target axis =
# machine correctness (0/1), nuisance axis = log response length. If the audit instrument is
# axis-pluggable, this degraded audit should reproduce the pass/fail structure of the human
# audit on the same thirteen configurations. Registered expectations, stated before running:
# (E1) referenced ladder judges and the honest frontier show positive correctness partials
# and near-zero length partials (they were causally cleared for length); (E2) the style-loaded
# configurations are NOT necessarily convicted here, because length is a different nuisance
# axis than style: a clean length partial with a style conviction in the human audit is the
# expected demonstration that axes are complementary instruments, not interchangeable ones.
# Run from experiments/tfa-vs-judge.
import glob
import json
import os

import numpy as np

rng = np.random.default_rng(0)


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def partial(x, y, z):
    x, y, z = map(lambda a: np.asarray(a, float), (x, y, z))
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return pearson(rx, ry)


def boot(fn, x, y, z, B=2000):
    x, y, z = map(lambda a: np.asarray(a, float), (x, y, z))
    idx = np.arange(len(x))
    vs = []
    for _ in range(B):
        i = rng.choice(idx, len(idx))
        try:
            vs.append(fn(x[i], y[i], z[i]))
        except Exception:
            pass
    return [round(float(np.percentile(vs, 2.5)), 2), round(float(np.percentile(vs, 97.5)), 2)]


traces = {r["id"]: r for r in (json.loads(l) for l in open("human_eval/traces_to_label.jsonl"))}
labs = {r["id"]: r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
        if r.get("soundness") not in (None, "")}
corr = {i: float(labs[i]["machine_correct"]) for i in labs}
leng = {i: float(np.log(1 + len(traces[i]["trace"]))) for i in labs}

CONFIGS = []
for f in sorted(glob.glob("runs/cert_out/*.jsonl")):
    base = os.path.basename(f)[:-6]
    cond, model = base.split("_", 1)
    CONFIGS.append((f"{cond}:{model.split('_')[-1] if '/' not in model else model}", f))
CONFIGS.append(("sabotage:GPT-5.2", "runs/cert_stylejudge_gpt.jsonl"))
CONFIGS.append(("rm:Skywork-8B", "runs/rm_scores_traces.jsonl"))

out = {}
for name, path in CONFIGS:
    sc = {}
    for l in open(path):
        r = json.loads(l)
        tid = r.get("task_id") or r.get("id")
        v = r.get("score") if r.get("score") is not None else r.get("rm_score")
        if tid is not None and v is not None:
            sc[tid] = float(v)
    j = [(sc[i], corr[i], leng[i]) for i in sc if i in labs]
    if len(j) < 20:
        continue
    x, c, L = map(np.array, zip(*j))
    out[name] = dict(n=len(j),
                     corr_partial=round(partial(x, c, L), 2), corr_ci=boot(partial, x, c, L),
                     len_partial=round(partial(x, L, c), 2), len_ci=boot(partial, x, L, c))
# honest frontier judge scores are stored on the labels themselves
x = np.array([float(labs[i]["judge"]) for i in labs])
c = np.array([corr[i] for i in labs]); L = np.array([leng[i] for i in labs])
out["ref:GPT-5.2 (honest)"] = dict(n=len(labs),
                                   corr_partial=round(partial(x, c, L), 2), corr_ci=boot(partial, x, c, L),
                                   len_partial=round(partial(x, L, c), 2), len_ci=boot(partial, x, L, c))
json.dump(out, open("../../papers/analysis/mech_axes_audit.json", "w"), indent=1)
for k, v in out.items():
    print(f"{k:35s} corr {v['corr_partial']:+.2f} {v['corr_ci']}  len {v['len_partial']:+.2f} {v['len_ci']}  n={v['n']}")
