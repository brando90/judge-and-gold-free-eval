# Producer for the round-8 analyses demanded by the v15 cold read.
#   (1) matched_population: E1, selection collapse, and anchoring margin all recomputed on the
#       SAME item set (the 83 items that are both eligible and inside the registered band), so
#       the replication table's three endpoints can be compared without a population footnote.
#   (2) m1_pressure: the residual-anchoring worry. M1 removes inflation at best-of-64, but it
#       leaves part of the anchoring premium standing. If that residual re-emerges under more
#       optimization, M1's recommendation is fragile. Recompute M1-vs-blind and ref-vs-blind at
#       every best-of-n budget on the k>1 strata.
#   (3) linkage_sim: a noise simulation showing that a per-item margin/inflation correlation can
#       be near zero even when anchoring fully drives inflation, given the per-item sample sizes
#       actually available. Bounds what the negative linkage result can and cannot mean.
# All post hoc. None registered. Run from experiments/tfa-vs-judge.
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

JUD = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
out = {}

# ================= (1) matched population on the replication pool =================
rpool = {}
for l in open("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" in r: rpool[r["problem_id"]] = r
mtasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/repl_main_tasks.jsonl")}
inband = {p for p in rpool if 0.2 <= float(np.mean(rpool[p]["oracle"])) <= 0.8}
eligible = set()
for pid, it in rpool.items():
    refn = norm(mtasks[pid]["ref_answer"])
    kinds = {norm(boxed(it["samples"][i]) or it["samples"][i]) == refn
             for i, ok in enumerate(it["oracle"]) if ok}
    if kinds == {True, False}: eligible.add(pid)
matched = sorted(inband & eligible)
def rsc(j, c, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
            for l in open(f"runs/bon_scores_repl/synthk__{j}__{c}_{rep}.jsonl")}
ns["NS"] = [1, 64]
per, collapse, margins = {}, {}, {}
for j in JUD:
    ra, rb, na, nb = rsc(j, "ref", "a"), rsc(j, "ref", "b"), rsc(j, "noref", "a"), rsc(j, "noref", "b")
    mg, refonly, blindonly = [], 0, 0
    for pid in matched:
        it = rpool[pid]
        if pid not in ra: continue
        cr = ns["per_item_curves"](it, ra[pid], rb[pid]); nr = ns["permutation_null"](it, ra[pid], rb[pid])
        cn = ns["per_item_curves"](it, na[pid], nb[pid]); nn = ns["permutation_null"](it, na[pid], nb[pid])
        per.setdefault(pid, []).append((cr[64]["judge_gain"] - cr[64]["true_gain"] - nr)
                                       - (cn[64]["judge_gain"] - cn[64]["true_gain"] - nn))
        refn = norm(mtasks[pid]["ref_answer"])
        ms, os_ = [], []
        for i, ok in enumerate(it["oracle"]):
            if not ok: continue
            (ms if norm(boxed(it["samples"][i]) or it["samples"][i]) == refn else os_).append(ra[pid][i])
        if ms and os_: mg.append(float(np.mean(ms) - np.mean(os_)))
        # selection collapse: did the arm's best-of-64 pick land on a matching valid answer?
        def picks_match(sa):
            i = int(np.argmax(sa))
            return bool(it["oracle"][i]) and norm(boxed(it["samples"][i]) or it["samples"][i]) == refn
        pr, pb = picks_match(ra[pid]), picks_match(na[pid])
        if pr and not pb: refonly += 1
        elif pb and not pr: blindonly += 1
    collapse[j] = dict(referenced_only=refonly, blind_only=blindonly)
    margins[j] = dict(n=len(mg), margin=round(float(np.mean(mg)), 2), ci=bci(mg))
D = np.array([np.mean(v) for v in per.values()])
b = [float(np.mean(rng.choice(D, len(D)))) for _ in range(4000)]
out["matched_population"] = dict(
    n_items=len(D), note="all three endpoints on the 83 items that are both eligible and in-band",
    E1=dict(delta=round(float(D.mean()), 3),
            ci=[round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)]),
    selection_collapse=collapse, anchoring_margin=margins)

# ================= (2) does M1's residual premium re-emerge under pressure? ==========
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
kpool = {}
for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" not in r: continue
    t = tasks[r["problem_id"]]; r["k"] = t["k"]; r["ref_answer"] = t["ref_answer"]
    kpool[r["problem_id"]] = r
def ksc(j, c, rep):
    for p in ("kstrat", "synthk"):
        f = f"runs/bon_scores_kstrat/{p}__{j}__{c}_{rep}.jsonl"
        if os.path.exists(f):
            return {json.loads(l)["problem_id"]: json.loads(l)["escore"] for l in open(f)}
    raise FileNotFoundError(c)
NS = [2, 4, 8, 16, 32, 64]
ns["NS"] = sorted({1, *NS})
press = {}
for j in JUD:
    arms = {c: (ksc(j, c, "a"), ksc(j, c, "b")) for c in ("noref", "ref", "m1")}
    acc = {c: {n: [] for n in NS} for c in ("ref", "m1")}
    for pid, it in kpool.items():
        if it["k"] <= 1: continue
        if not (0.05 <= float(np.mean(it["oracle"])) <= 0.95): continue
        if any(pid not in arms[c][0] for c in arms): continue
        cur = {c: ns["per_item_curves"](it, arms[c][0][pid], arms[c][1][pid]) for c in arms}
        for n in NS:
            g = {c: cur[c][n]["judge_gain"] - cur[c][n]["true_gain"] for c in arms}
            for c in ("ref", "m1"): acc[c][n].append(g[c] - g["noref"])
    press[j] = {c: {f"n={n}": dict(n_items=len(acc[c][n]), delta=round(float(np.mean(acc[c][n])), 3),
                                   ci=bci(acc[c][n])) for n in NS} for c in ("ref", "m1")}
out["m1_pressure"] = dict(note=("paired hack-gap delta versus blind at k>1, raw units; if M1's "
                                "residual anchoring re-emerged under optimization its curve would "
                                "climb with n the way the single reference's does"), by_judge=press)

# ================= (3) can a real effect show a null per-item correlation? ==========
# SUPERSEDED (round 9): this sweep treated the inflation measurement SD as unidentifiable.
# It is identifiable by roles-swapped split-half from the two rubric replicates; see
# round9_provenance.py (linkage_power), which also fixes two defects here: true margins are
# drawn from the OBSERVED margins and measurement noise re-added (double-counting), and the
# stipulated slope note ("slope only sets scale, not the correlation") is wrong -- with
# additive noise the slope enters r directly. Kept unchanged for the record.
# Anchoring drives inflation exactly, item-for-item, then both are measured with the sampling
# noise the real design has. Two of the three noise parameters are ESTIMATED FROM THE POOL rather
# than stipulated; the third (how noisily per-item inflation itself is measured) is not directly
# identifiable, so it is swept and the recovered correlation reported across the sweep.
cal_match, cal_other, cal_sd, cal_margins = [], [], [], []
for j in JUD:
    ra, _ = ksc(j, "ref", "a"), None
    for pid, it in kpool.items():
        if it["k"] <= 1 or pid not in ra: continue
        if not (0.05 <= float(np.mean(it["oracle"])) <= 0.95): continue
        refn = norm(it["ref_answer"])
        ms, os_ = [], []
        for i, ok in enumerate(it["oracle"]):
            if not ok: continue
            (ms if norm(boxed(it["samples"][i]) or it["samples"][i]) == refn else os_).append(ra[pid][i])
        if not (ms and os_): continue
        cal_match.append(len(ms)); cal_other.append(len(os_))
        if len(ms) > 1: cal_sd.append(float(np.std(ms, ddof=1)))
        if len(os_) > 1: cal_sd.append(float(np.std(os_, ddof=1)))
        cal_margins.append(float(np.mean(ms) - np.mean(os_)))
nm, no = float(np.mean(cal_match)), float(np.mean(cal_other))
sd = float(np.mean(cal_sd))
obs_margins = np.array(cal_margins)

def sim(infl_noise, n_items=35, slope=0.22, reps=400):
    rs = []
    for _ in range(reps):
        true_margin = rng.choice(obs_margins, n_items)   # empirical margin distribution
        true_infl = slope * true_margin                  # exact linear pathway, no slack
        obs_margin = true_margin + rng.normal(0, sd, n_items) * np.sqrt(1.0 / nm + 1.0 / no)
        obs_infl = true_infl + rng.normal(0, infl_noise, n_items)
        rs.append(float(np.corrcoef(obs_margin, obs_infl)[0, 1]))
    rs = np.array(rs)
    return dict(mean_r=round(float(rs.mean()), 3),
                pct2_5=round(float(np.percentile(rs, 2.5)), 3),
                pct97_5=round(float(np.percentile(rs, 97.5)), 3))
sweep = {f"infl_noise={x}": sim(x) for x in (0.25, 0.55, 1.0, 1.5)}
out["linkage_sim"] = dict(
    note=("ground truth: inflation is an exact linear function of the per-item anchoring margin. "
          "Margins are drawn from the pool's own empirical margin distribution and observed with "
          "the pool's own judge-score SD and valid-sample counts. The inflation measurement SD is "
          "not directly identifiable from the data, so it is swept."),
    calibrated_from_data=dict(mean_valid_matching_samples=round(nm, 2),
                              mean_valid_other_samples=round(no, 2),
                              within_item_judge_score_sd=round(sd, 3),
                              n_items_with_margins=len(obs_margins),
                              observed_margin_mean=round(float(obs_margins.mean()), 2)),
    stipulated=dict(slope=0.22, n_items=35, note="slope only sets scale, not the correlation"),
    swept_inflation_measurement_sd=sweep)
json.dump(out, open("../../papers/analysis/round8_followups.json", "w"), indent=1)
print(json.dumps(out, indent=1))
