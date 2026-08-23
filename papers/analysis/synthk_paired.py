# Post-hoc re-analysis of the synthk grid demanded by the round-4 review (labeled post hoc:
# the frozen pre-committed analysis is synthk_analysis.py; this adds the paired inference the
# review required). Run from experiments/tfa-vs-judge. Produces synthk_paired.json with:
#  paired_pooled: per judge, per-item paired (ref minus blind) excess-gap deltas pooled over
#    the k>1 strata, item bootstrap CI; and the k=1 paired delta separately.
#  trend: per judge, OLS slope of the per-item paired delta on log2(k) over k>=1 items,
#    item-bootstrap CI (step-vs-ramp: a positive k1->k2 jump with flat slope beyond).
#  step: per judge, paired contrast (mean delta at k>=2) minus (delta at k=1), bootstrap CI.
#  mcnemar: rotation-arm collapse contrast as an exact McNemar test on the 18 paired items
#    (ref-match indicator per item under referenced vs blind selection).
#  llama_k1_audit: per-sample boxed-extraction and oracle rates for the Llama-pool k=1
#    stratum versus the Qwen pool's, to locate the k=1 non-replication's proximate cause.
import json
import math
import re
import sys

import numpy as np

sys.path.insert(0, "scripts")
src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}
exec(compile(src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def load_pool(path):
    return {r["problem_id"]: r for r in (json.loads(l) for l in open(path)) if "oracle" in r}


def scores(d, jtag, cond, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
            for l in open(f"{d}/synthk__{jtag}__{cond}_{rep}.jsonl")}


def per_item_gaps(pool, sa, sb):
    gaps = {}
    for pid, it in pool.items():
        if pid not in sa or pid not in sb:
            continue
        pr = float(np.mean(it["oracle"]))
        if not (0.05 <= pr <= 0.95):
            continue
        curves = ns["per_item_curves"](it, sa[pid], sb[pid])
        null = ns["permutation_null"](it, sa[pid], sb[pid])
        gaps[pid] = curves[64]["judge_gain"] - curves[64]["true_gain"] - null
    return gaps


def boot_mean(d, B=4000):
    d = np.asarray(d, float)
    b = [float(np.mean(rng.choice(d, len(d)))) for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)]


qpool = load_pool("runs/bon/bon_synthk__Qwen__Qwen2.5-7B-Instruct.jsonl")
JUDGES = ["Qwen__Qwen2.5-1.5B-Instruct", "Qwen__Qwen2.5-3B-Instruct",
          "Qwen__Qwen2.5-7B-Instruct", "Qwen__Qwen2.5-14B-Instruct",
          "meta-llama__Llama-3.1-8B-Instruct", "microsoft__phi-4"]
out = {"paired_pooled": {}, "step": {}, "trend": {}}
for jtag in JUDGES:
    ra = scores("runs/bon_scores_synthk", jtag, "ref", "a")
    rb = scores("runs/bon_scores_synthk", jtag, "ref", "b")
    na = scores("runs/bon_scores_synthk", jtag, "noref", "a")
    nb = scores("runs/bon_scores_synthk", jtag, "noref", "b")
    gr = per_item_gaps(qpool, ra, rb)
    gn = per_item_gaps(qpool, na, nb)
    pids = sorted(set(gr) & set(gn))
    d = {p: gr[p] - gn[p] for p in pids}
    ks = {p: qpool[p]["k"] for p in pids}
    hi = [d[p] for p in pids if ks[p] > 1]
    lo = [d[p] for p in pids if ks[p] == 1]
    out["paired_pooled"][jtag] = dict(
        n_hi=len(hi), delta_kgt1=round(float(np.mean(hi)), 3), ci_kgt1=boot_mean(hi),
        n_k1=len(lo), delta_k1=round(float(np.mean(lo)), 3),
        ci_k1=boot_mean(lo) if len(lo) >= 3 else None)
    # step contrast: mean(k>1 deltas) - mean(k=1 deltas), joint item bootstrap
    boots = []
    hi_a, lo_a = np.asarray(hi), np.asarray(lo)
    for _ in range(4000):
        boots.append(float(np.mean(rng.choice(hi_a, len(hi_a))) -
                           np.mean(rng.choice(lo_a, len(lo_a)))))
    out["step"][jtag] = dict(step=round(float(np.mean(hi_a) - np.mean(lo_a)), 3),
                             ci=[round(float(np.percentile(boots, 2.5)), 3),
                                 round(float(np.percentile(boots, 97.5)), 3)])
    # trend beyond k=2: slope of delta on log2 k among k>1 items
    x = np.array([math.log2(ks[p]) for p in pids if ks[p] > 1])
    y = np.array([d[p] for p in pids if ks[p] > 1])
    slope = float(np.polyfit(x, y, 1)[0])
    bs = []
    idx = np.arange(len(x))
    for _ in range(4000):
        i = rng.choice(idx, len(idx))
        if len(set(x[i])) < 2:
            continue
        bs.append(float(np.polyfit(x[i], y[i], 1)[0]))
    out["trend"][jtag] = dict(slope_per_log2k=round(slope, 3),
                              ci=[round(float(np.percentile(bs, 2.5)), 3),
                                  round(float(np.percentile(bs, 97.5)), 3)])

# ---- McNemar for the rotation-arm collapse (paired 18 items, ref vs blind selection match)
rot_pool = {r["problem_id"]: r for r in (json.loads(l) for l in
            open("runs/bon/bon_tiesrot__Qwen__Qwen2.5-7B-Instruct.jsonl"))}
mc = {}
for jm in ["Qwen2.5-1.5B-Instruct", "Qwen2.5-3B-Instruct", "Qwen2.5-7B-Instruct",
           "Qwen2.5-14B-Instruct"]:
    sr = {json.loads(l)["problem_id"]: json.loads(l)["escore"]
          for l in open(f"runs/bon_scores_ties_rot/ties__Qwen__{jm}__ref_a.jsonl")}
    sn = {json.loads(l)["problem_id"]: json.loads(l)["escore"]
          for l in open(f"runs/bon_scores_ties_full/ties__Qwen__{jm}__noref_a.jsonl")}
    b01 = b10 = 0
    n = 0
    for pid, it in rot_pool.items():
        if pid not in sr or pid not in sn:
            continue
        refn = norm(it["ref_answer"])
        kinds = {norm(boxed(it["samples"][i]) or it["samples"][i]) == refn
                 for i, ok in enumerate(it["oracle"]) if ok}
        if kinds != {True, False}:
            continue
        n += 1

        def match(sc):
            sel = int(np.argmax(sc[pid]))
            return bool(it["oracle"][sel]) and \
                norm(boxed(it["samples"][sel]) or it["samples"][sel]) == refn
        mr, mn = match(sr), match(sn)
        if mr and not mn:
            b10 += 1
        elif mn and not mr:
            b01 += 1
    nd = b10 + b01
    p = sum(math.comb(nd, k) for k in range(min(b01, b10) + 1)) * 2 / (2 ** nd) if nd else 1.0
    mc[jm] = dict(n=n, ref_only=b10, blind_only=b01, mcnemar_p=round(min(p, 1.0), 5))
out["mcnemar"] = mc

# ---- Llama-pool k=1 audit
lpool = load_pool("runs/bon/bon_synthk__meta-llama__Llama-3.1-8B-Instruct.jsonl")
def k1_audit(pool):
    rows = []
    for it in pool.values():
        if it["k"] != 1:
            continue
        nb = sum(1 for s in it["samples"] if boxed(s) is not None)
        rows.append(dict(pid=it["problem_id"], boxed_rate=round(nb / len(it["samples"]), 2),
                         oracle_rate=round(float(np.mean(it["oracle"])), 2)))
    return dict(n=len(rows),
                mean_boxed=round(float(np.mean([r["boxed_rate"] for r in rows])), 3),
                mean_oracle=round(float(np.mean([r["oracle_rate"] for r in rows])), 3))
out["llama_k1_audit"] = dict(llama_pool=k1_audit(lpool), qwen_pool=k1_audit(qpool))

json.dump(out, open("../../papers/analysis/synthk_paired.json", "w"), indent=1)
print(json.dumps(out, indent=1))
