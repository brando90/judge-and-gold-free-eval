# R8-A frozen producer (papers/D-iclr/registration_round8.md). Run from experiments/tfa-vs-judge.
# Reads runs/r8/sonnet_{repl,mace,kpool}.jsonl (pools) and runs/r8/sonnet/{pool}.jsonl (Sonnet 5 CLI scores, both
# conditions). Writes papers/analysis/r8_sonnet_results.json.
# Per pool and task (16 candidates), referenced minus blind:
#   G_nm   per-task AUROC, correct answers that do not match the reference vs wrong answers (ties count half);
#   G_all  per-task AUROC, all correct vs wrong;
#   FR     share of non-matching correct answers scored 3 or below;
#   margin mean score of matching correct minus non-matching correct answers;
#   acc    best-of-16 accuracy, ties averaged; and the max(blind, referenced) rule's accuracy minus blind (descriptive).
# Labels: lenient (primary) for the constructed pools, with strict as a secondary readout; the MACE oracle for MACE.
# A candidate whose call failed or whose reply had no score is missing in that condition; a task enters a readout when the
# groups that readout needs have at least one scored candidate in both conditions. A pool with fewer than 20 tasks with
# all 32 calls scored is "not scored". Intervals: task bootstrap, 1,000 resamples, numpy default_rng(0).
import argparse
import json
import os

import numpy as np

# Amendment 1: API scores by default; --scores runs/r8/sonnet --out ../../papers/analysis/r8_sonnet_cli_partial.json for the CLI run
ap = argparse.ArgumentParser()
ap.add_argument("--scores", default="runs/r8/sonnet_api")
ap.add_argument("--out", default="../../papers/analysis/r8_sonnet_results.json")
ARGS = ap.parse_args()
NBOOT = 1000
OUT = ARGS.out


def boot(x, seed=0):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def auroc(sc, lab):
    pos = np.array([s for s, l in zip(sc, lab) if l and s is not None], float)
    neg = np.array([s for s, l in zip(sc, lab) if not l and s is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def sel_acc(scores, oracle):
    ix = [i for i, s in enumerate(scores) if s is not None]
    if not ix:
        return None
    s = np.array([scores[i] for i in ix], float)
    o = np.array([oracle[i] for i in ix], float)
    return float(o[s == s.max()].mean())


def verdict(ci, direction):
    if ci is None:
        return "not scored"
    lo, hi = ci[1]
    if (direction > 0 and lo > 0) or (direction < 0 and hi < 0):
        return "confirmed"
    if (direction > 0 and hi < 0) or (direction < 0 and lo > 0):
        return "falsified"
    return "not confirmed"


res = {"pools": {}}
for pool in ("repl", "mace", "kpool"):
    pf, sf = f"runs/r8/sonnet_{pool}.jsonl", f"{ARGS.scores}/{pool}.jsonl"
    if not os.path.exists(sf):
        res["pools"][pool] = "no scores"
        continue
    S, calls, bad = {}, 0, 0
    for l in open(sf):
        r = json.loads(l)
        calls += 1
        if r.get("error") or r.get("score") is None:
            bad += 1
            continue
        S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    labelings = ("lenient", "strict") if pool != "mace" else ("oracle",)
    out = dict(calls=calls, failed_or_unparseable=bad)
    for how in labelings:
        R = {k: [] for k in ("G_nm", "G_all", "FR", "margin", "acc", "acc_max_rule", "G_nm_blind", "G_nm_ref", "G_all_blind", "G_all_ref")}
        complete = 0
        for t in (json.loads(l) for l in open(pf)):
            pid = t["problem_id"]
            b = [S.get((pid, i, "noref")) for i in t["idx"]]
            r = [S.get((pid, i, "ref")) for i in t["idx"]]
            complete += all(v is not None for v in b + r)
            lab = t[how]
            grp = ["invalid" if not o else ("match" if g == "match" else "nonmatch") for o, g in zip(lab, t["group"])]
            both = [i for i in range(len(b)) if b[i] is not None and r[i] is not None]
            nm = [i for i in both if grp[i] != "match"]
            x0, x1 = auroc([b[i] for i in nm], [grp[i] == "nonmatch" for i in nm]), auroc([r[i] for i in nm], [grp[i] == "nonmatch" for i in nm])
            if x0 is not None and x1 is not None:
                R["G_nm"].append(x1 - x0); R["G_nm_blind"].append(x0); R["G_nm_ref"].append(x1)
            x0, x1 = auroc([b[i] for i in both], [lab[i] for i in both]), auroc([r[i] for i in both], [lab[i] for i in both])
            if x0 is not None and x1 is not None:
                R["G_all"].append(x1 - x0); R["G_all_blind"].append(x0); R["G_all_ref"].append(x1)
            cnm = [i for i in both if grp[i] == "nonmatch"]
            cm = [i for i in both if grp[i] == "match"]
            if cnm:
                R["FR"].append(np.mean([r[i] <= 3 for i in cnm]) - np.mean([b[i] <= 3 for i in cnm]))
            if cnm and cm:
                R["margin"].append((np.mean([r[i] for i in cm]) - np.mean([r[i] for i in cnm])) - (np.mean([b[i] for i in cm]) - np.mean([b[i] for i in cnm])))
            if both and 0 < sum(lab[i] for i in both) < len(both):
                o = [lab[i] for i in both]
                a0 = sel_acc([b[i] for i in both], o)
                R["acc"].append(sel_acc([r[i] for i in both], o) - a0)
                R["acc_max_rule"].append(sel_acc([max(b[i], r[i]) for i in both], o) - a0)
        out[how] = {k: boot(v) for k, v in R.items()}
        out[how]["tasks_all_calls_scored"] = complete
        if complete < 20:
            out[how]["status"] = "not scored (fewer than 20 complete tasks)"
    res["pools"][pool] = out


def get(pool, how, key):
    d = res["pools"].get(pool)
    if not isinstance(d, dict) or d.get(how, {}).get("status"):
        return None
    return d[how][key]


res["predictions"] = {
    "P-R8A1 repl G_nm < 0": verdict(get("repl", "lenient", "G_nm"), -1),
    "P-R8A2 repl FR > 0": verdict(get("repl", "lenient", "FR"), +1),
    "P-R8A3 mace G_nm < 0": verdict(get("mace", "oracle", "G_nm"), -1),
    "P-R8A4 mace FR > 0": verdict(get("mace", "oracle", "FR"), +1),
    "P-R8A5 kpool G_nm < 0": verdict(get("kpool", "lenient", "G_nm"), -1),
    "P-R8A6 repl margin > 0 (manipulation check)": verdict(get("repl", "lenient", "margin"), +1),
}
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
