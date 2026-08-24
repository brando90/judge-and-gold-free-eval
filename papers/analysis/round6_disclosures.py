# Producer for the round-6 disclosure artifacts, so every number in Paper D traces to a
# committed script (closes the reviewer's reproducibility qualification).
# Writes: mitigation_registered_contrasts.json (registered P-M3 step, registered
# vs-single-reference contrasts, and the M2 soft-gate multiplier audit) and
# repl_disclosures.json (boxed compliance, pass rates, pilot overlap and its sensitivity,
# eligible-vs-in-band counts). Run from experiments/tfa-vs-judge.
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

# ---------------- part 1: k-stratified experiment (mitigation_registered_contrasts.json)
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
kpool = {}
for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" not in r: continue
    t = tasks[r["problem_id"]]; r["k"] = t["k"]; r["ref_answer"] = t["ref_answer"]
    kpool[r["problem_id"]] = r
JUD = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
def ksc(j, c, rep):
    for p in ("kstrat", "synthk"):
        f = f"runs/bon_scores_kstrat/{p}__{j}__{c}_{rep}.jsonl"
        if os.path.exists(f):
            return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(f)}
    raise FileNotFoundError(c)
out1, G = {}, {}
for j in JUD:
    for c in ("noref", "ref", "m1", "m2"):
        a, b = ksc(j, c, "a"), ksc(j, c, "b"); g = {}
        for pid, it in kpool.items():
            if pid not in a: continue
            if not (0.05 <= float(np.mean(it["oracle"])) <= 0.95): continue
            cu = ns["per_item_curves"](it, a[pid], b[pid]); nl = ns["permutation_null"](it, a[pid], b[pid])
            g[pid] = cu[64]["judge_gain"] - cu[64]["true_gain"] - nl
        G[(j, c)] = g
for j in JUD:
    d = {p: G[(j, "ref")][p] - G[(j, "noref")][p] for p in G[(j, "ref")] if p in G[(j, "noref")]}
    hi = np.array([v for p, v in d.items() if kpool[p]["k"] > 1])
    lo = np.array([v for p, v in d.items() if kpool[p]["k"] == 1])
    boots = [float(np.mean(rng.choice(hi, len(hi))) - np.mean(rng.choice(lo, len(lo)))) for _ in range(4000)]
    out1[f"PM3_step__{j}"] = dict(n_hi=len(hi), n_lo=len(lo), step=round(float(hi.mean() - lo.mean()), 3),
                                  ci=[round(float(np.percentile(boots, 2.5)), 3),
                                      round(float(np.percentile(boots, 97.5)), 3)])
    for m in ("m1", "m2"):
        pids = [p for p in G[(j, m)] if p in G[(j, "ref")] and kpool[p]["k"] > 1]
        dd = np.array([G[(j, m)][p] - G[(j, "ref")][p] for p in pids])
        out1[f"{m}_vs_ref__{j}"] = dict(n=len(dd), delta=round(float(dd.mean()), 3), ci=bci(dd))
    blind, m2 = ksc(j, "noref", "a"), ksc(j, "m2", "a")
    mm, nn = [], []
    for pid, it in kpool.items():
        if pid not in m2 or pid not in blind: continue
        refn = norm(it["ref_answer"])
        for i, ok in enumerate(it["oracle"]):
            if not ok or blind[pid][i] <= 0.01: continue
            mult = min(m2[pid][i] / blind[pid][i], 1.5)
            (mm if norm(boxed(it["samples"][i]) or it["samples"][i]) == refn else nn).append(mult)
    out1[f"m2_gate__{j}"] = dict(n_match=len(mm), n_other=len(nn),
        mean_mult_matching=round(float(np.mean(mm)), 3), mean_mult_other=round(float(np.mean(nn)), 3),
        frac_soft_matching=round(float(np.mean([(0.05 < x < 0.95) for x in mm])), 3),
        frac_soft_other=round(float(np.mean([(0.05 < x < 0.95) for x in nn])), 3))
json.dump(out1, open("../../papers/analysis/mitigation_registered_contrasts.json", "w"), indent=1)

# ---------------- part 2: replication disclosures (repl_disclosures.json)
rpool = {}
for l in open("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" in r: rpool[r["problem_id"]] = r
pilot_texts = {json.loads(l)["problem"] for l in open("runs/repl_pilot_tasks.jsonl")}
mtasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/repl_main_tasks.jsonl")}
overlap = [pid for pid, t in mtasks.items() if t["problem"] in pilot_texts]
inband = [p for p in rpool if 0.2 <= float(np.mean(rpool[p]["oracle"])) <= 0.8]
def rsc(j, c, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
            for l in open(f"runs/bon_scores_repl/synthk__{j}__{c}_{rep}.jsonl")}
per = {}
for j in JUD:
    ra, rb, na, nb = rsc(j, "ref", "a"), rsc(j, "ref", "b"), rsc(j, "noref", "a"), rsc(j, "noref", "b")
    for pid in inband:
        it = rpool[pid]
        if pid not in ra: continue
        cr = ns["per_item_curves"](it, ra[pid], rb[pid]); nr = ns["permutation_null"](it, ra[pid], rb[pid])
        cn = ns["per_item_curves"](it, na[pid], nb[pid]); nn2 = ns["permutation_null"](it, na[pid], nb[pid])
        per.setdefault(pid, []).append((cr[64]["judge_gain"] - cr[64]["true_gain"] - nr)
                                       - (cn[64]["judge_gain"] - cn[64]["true_gain"] - nn2))
def pooled(pids):
    D = np.array([per[p] for p in pids if p in per]); idx = np.arange(len(D))
    b = [float(D[rng.choice(idx, len(idx))].mean()) for _ in range(4000)]
    return round(float(D.mean()), 3), [round(float(np.percentile(b, 2.5)), 3),
                                       round(float(np.percentile(b, 97.5)), 3)], len(D)
ov_in = [p for p in overlap if p in inband]
full = pooled([p for p in inband if p in per])
excl = pooled([p for p in inband if p in per and p not in ov_in])
elig = []
for pid, it in rpool.items():
    refn = norm(mtasks[pid]["ref_answer"])
    kinds = {norm(boxed(it["samples"][i]) or it["samples"][i]) == refn
             for i, ok in enumerate(it["oracle"]) if ok}
    if kinds == {True, False}: elig.append(pid)
out2 = dict(
    boxed_compliance_all=round(float(np.mean([np.mean([boxed(s) is not None for s in r["samples"]])
                                              for r in rpool.values()])), 3),
    boxed_compliance_inband=round(float(np.mean([np.mean([boxed(s) is not None for s in rpool[p]["samples"]])
                                                 for p in inband])), 3),
    mean_pass_all_items=round(float(np.mean([np.mean(r["oracle"]) for r in rpool.values()])), 3),
    mean_pass_inband=round(float(np.mean([np.mean(rpool[p]["oracle"]) for p in inband])), 3),
    pilot_overlap_total=len(overlap), pilot_overlap_inband=len(ov_in),
    E1_full=dict(delta=full[0], ci=full[1], n=full[2]),
    E1_excluding_pilot_overlap=dict(delta=excl[0], ci=excl[1], n=excl[2]),
    eligible_items_total=len(elig), eligible_and_inband=len([p for p in elig if p in inband]),
    note="P-R2/P-R3 use all eligible items; E1 alone applies the registered [0.2,0.8] band")
json.dump(out2, open("../../papers/analysis/repl_disclosures.json", "w"), indent=1)
print(json.dumps({"contrasts": len(out1), "disclosures": len(out2)}))
