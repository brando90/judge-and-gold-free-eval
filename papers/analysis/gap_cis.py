# Canonical excess-gap CIs and boundary contrasts for Paper A (run from experiments/tfa-vs-judge).
# Sources: runs/bon_v2_full.json per-item excess gaps (the same estimator as the summary rows),
# plus the anchor labels and 1.5B-blind audit scores for a non-degenerate conviction interval.
# Outputs papers/analysis/gap_cis.json:
#  gap_ci: per math config, mean excess gap with 95% bootstrap CI over items
#  boundary_contrasts: paired per-item bootstrap CIs for the cross-cluster pairs the text
#    compares (failed-minimum minus certified-maximum on inflation, and sabotage minus honest)
#  conviction_1p5b: jackknife CI and permutation p for the 1.5B-blind style partial, whose
#    plain bootstrap is degenerate (concentrated scores)
import json

import numpy as np

rng = np.random.default_rng(0)
d = json.load(open("runs/bon_v2_full.json"))
per = d["per_item"]
MATH = [c for c in per if c.startswith("math__")]


def boot_mean(vals, B=4000):
    vals = np.asarray(vals, float)
    b = [float(np.mean(rng.choice(vals, len(vals)))) for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 2), round(float(np.percentile(b, 97.5)), 2)]


out = {"gap_ci": {}}
for c in MATH:
    v = list(per[c].values())
    out["gap_ci"][c] = dict(n=len(v), gap=round(float(np.mean(v)), 2), ci=boot_mean(v))


def paired(c1, c2, B=4000):
    pids = sorted(set(per[c1]) & set(per[c2]))
    dd = np.array([per[c1][p] - per[c2][p] for p in pids])
    b = [float(np.mean(rng.choice(dd, len(dd)))) for _ in range(B)]
    return dict(n=len(pids), delta=round(float(dd.mean()), 2),
                ci=[round(float(np.percentile(b, 2.5)), 2),
                    round(float(np.percentile(b, 97.5)), 2)])


out["boundary_contrasts"] = {
    "3B_blind_minus_gpt_honest": paired("math__Qwen__Qwen2.5-3B-Instruct__noref",
                                        "math__gpt-5.2__ref"),
    "3B_blind_minus_14B_ref": paired("math__Qwen__Qwen2.5-3B-Instruct__noref",
                                     "math__Qwen__Qwen2.5-14B-Instruct__ref"),
    "sabotage_minus_gpt_honest": paired("math__gpt-5.2__sabotage", "math__gpt-5.2__ref"),
    "14B_blind_minus_gpt_honest": paired("math__Qwen__Qwen2.5-14B-Instruct__noref",
                                         "math__gpt-5.2__ref"),
}

# ---------------------------------------------------- 1.5B-blind conviction interval
labs = {r["id"]: r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
        if r.get("soundness") not in (None, "")}
sc = {}
for l in open("runs/cert_out/noref_Qwen_Qwen2.5-1.5B-Instruct.jsonl"):
    r = json.loads(l)
    if r.get("score") is not None:
        sc[r["task_id"]] = float(r["score"])
joined = [(sc[i], float(labs[i]["style"]), float(labs[i]["soundness"]))
          for i in sc if i in labs]
x, st, s = map(np.array, zip(*joined))


def partial(x, y, z):
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return float(np.corrcoef(rx, ry)[0, 1])


est = partial(x, st, s)
n = len(x)
jk = []
for i in range(n):
    m = np.ones(n, bool); m[i] = False
    jk.append(partial(x[m], st[m], s[m]))
jk = np.array(jk)
se = float(np.sqrt((n - 1) / n * np.sum((jk - jk.mean()) ** 2)))
perm = []
for _ in range(10000):
    perm.append(partial(rng.permutation(x), st, s))
p = float(np.mean(np.abs(perm) >= abs(est)))
out["conviction_1p5b"] = dict(n=n, style_partial=round(est, 2),
                              jackknife_ci=[round(est - 1.96 * se, 2),
                                            round(est + 1.96 * se, 2)],
                              perm_p_two_sided=round(p, 5))

json.dump(out, open("../../papers/analysis/gap_cis.json", "w"), indent=1)
print(json.dumps(out, indent=1))
