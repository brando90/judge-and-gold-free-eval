# Producer for the two round-7 analyses demanded by the cold-read review.
#   (1) band_match: the k-stratified single-reference-vs-blind inflation deltas at k>1
#       recomputed under the REPLICATION's registered [0.2, 0.8] pass-rate band, so the
#       +1.50/+1.07 of the mitigation table and the +1.19 of the replication table can be
#       compared instead of being fenced off by a "do not difference these" note.
#   (2) margin_linkage: the per-item quantitative link from anchoring margin to inflation.
#       If anchoring is the pathway, an item whose reference-matching valid answers are
#       scored above its other valid answers should be the item that inflates under
#       selection. Reports the per-item correlation and a binned predicted-vs-observed table.
# Post hoc. Neither is registered. Run from experiments/tfa-vs-judge.
import json, os, re, sys
import numpy as np
sys.path.insert(0, "scripts")
_src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}; exec(compile(_src, "bon_analysis", "exec"), ns)
rng = np.random.default_rng(0)

def norm(a): return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None
def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0: return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0); j += 1
    return t[i + 7:j - 1]
def bci(v, B=4000):
    v = np.asarray(v, float)
    b = [float(np.mean(rng.choice(v, len(v)))) for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)]

tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
pool = {}
for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" not in r: continue
    t = tasks[r["problem_id"]]; r["k"] = t["k"]; r["ref_answer"] = t["ref_answer"]
    pool[r["problem_id"]] = r
JUD = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
def sc(j, c, rep):
    for p in ("kstrat", "synthk"):
        f = f"runs/bon_scores_kstrat/{p}__{j}__{c}_{rep}.jsonl"
        if os.path.exists(f):
            return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(f)}
    raise FileNotFoundError(c)

out = {}
# ---- (1) the same contrast under each band, so the comparison is licensed
BANDS = {"registered_kstrat_[0.05,0.95]": (0.05, 0.95), "replication_[0.2,0.8]": (0.2, 0.8)}
for j in JUD:
    ra, rb = sc(j, "ref", "a"), sc(j, "ref", "b")
    na, nb = sc(j, "noref", "a"), sc(j, "noref", "b")
    per = {}
    for pid, it in pool.items():
        if pid not in ra or pid not in na: continue
        cr = ns["per_item_curves"](it, ra[pid], rb[pid]); nr = ns["permutation_null"](it, ra[pid], rb[pid])
        cn = ns["per_item_curves"](it, na[pid], nb[pid]); nn = ns["permutation_null"](it, na[pid], nb[pid])
        per[pid] = ((cr[64]["judge_gain"] - cr[64]["true_gain"] - nr)
                    - (cn[64]["judge_gain"] - cn[64]["true_gain"] - nn))
    for bname, (lo, hi) in BANDS.items():
        v = [d for pid, d in per.items()
             if pool[pid]["k"] > 1 and lo <= float(np.mean(pool[pid]["oracle"])) <= hi]
        out.setdefault("band_match", {})[f"{j}|{bname}"] = dict(
            n=len(v), delta=round(float(np.mean(v)), 3), ci=bci(v))

# ---- (2) per-item margin -> per-item inflation, the quantitative linkage
link = {}
for j in JUD:
    ra, rb = sc(j, "ref", "a"), sc(j, "ref", "b")
    na, nb = sc(j, "noref", "a"), sc(j, "noref", "b")
    xs, ys = [], []
    for pid, it in pool.items():
        if pid not in ra or pid not in na: continue
        if not (0.05 <= float(np.mean(it["oracle"])) <= 0.95): continue
        if it["k"] <= 1: continue
        refn = norm(it["ref_answer"])
        ms, os_ = [], []
        for i, ok in enumerate(it["oracle"]):
            if not ok: continue
            a = norm(boxed(it["samples"][i]) or it["samples"][i])
            (ms if a == refn else os_).append(ra[pid][i])
        if not (ms and os_): continue
        margin = float(np.mean(ms) - np.mean(os_))          # anchoring margin, referenced arm
        cr = ns["per_item_curves"](it, ra[pid], rb[pid]); nr = ns["permutation_null"](it, ra[pid], rb[pid])
        cn = ns["per_item_curves"](it, na[pid], nb[pid]); nn = ns["permutation_null"](it, na[pid], nb[pid])
        infl = ((cr[64]["judge_gain"] - cr[64]["true_gain"] - nr)
                - (cn[64]["judge_gain"] - cn[64]["true_gain"] - nn))
        xs.append(margin); ys.append(infl)
    xs, ys = np.array(xs), np.array(ys)
    r = float(np.corrcoef(xs, ys)[0, 1])
    zb = [np.arctanh(np.clip(np.corrcoef(xs[i], ys[i])[0, 1], -0.999, 0.999))
          for i in (rng.choice(len(xs), len(xs)) for _ in range(4000))]
    b1, b0 = np.polyfit(xs, ys, 1)
    terc = np.percentile(xs, [33.3, 66.7])
    bins = []
    for lab, sel in (("low margin", xs <= terc[0]),
                     ("mid margin", (xs > terc[0]) & (xs <= terc[1])),
                     ("high margin", xs > terc[1])):
        bins.append(dict(bin=lab, n=int(sel.sum()),
                         mean_margin=round(float(xs[sel].mean()), 2),
                         mean_inflation=round(float(ys[sel].mean()), 3),
                         ci=bci(ys[sel])))
    link[j] = dict(n_items=len(xs), r=round(r, 3),
                   r_ci=[round(float(np.tanh(np.percentile(zb, 2.5))), 3),
                         round(float(np.tanh(np.percentile(zb, 97.5))), 3)],
                   slope_inflation_per_margin_point=round(float(b1), 3),
                   intercept=round(float(b0), 3), tercile_bins=bins)
out["margin_linkage"] = link
out["note"] = ("post hoc, not registered; band_match licenses comparing the k-stratified "
               "k>1 deltas with the replication's E1 by putting both on the same pass-rate "
               "band; margin_linkage tests whether the per-item anchoring margin predicts "
               "the per-item inflation it is claimed to cause")
json.dump(out, open("../../papers/analysis/round7_linkage.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:2000])
