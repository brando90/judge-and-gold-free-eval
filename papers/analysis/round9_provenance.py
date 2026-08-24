# Producer for the round-9 analyses demanded by the internal v18 review (Gates 1 and 2).
#   (1) linkage_power: the round-8 sweep treated the inflation measurement SD as
#       unidentifiable and swept it. It is identifiable: the design has two rubric
#       replicates, so the roles-swapped estimator (selection on b, reporting on a) gives a
#       second estimate of every item's inflation, and SD(e_ab - e_ba)/sqrt(2) estimates the
#       measurement SD of the single (a,b) estimate the linkage actually used. This section
#       recomputes the exact-pathway simulation at that data-implied noise, with two fixes to
#       the round-8 sim: true margins are deconvolved (round 8 drew them from the OBSERVED
#       margins and then added measurement noise again, double-counting), and the pathway
#       slope is set so the exact pathway reproduces the deconvolved variance of observed
#       inflation (round 8 stipulated 0.22 and wrongly noted that slope "only sets scale").
#       Reports where each observed r falls in the simulated null (percentile).
#   (2) composition: the band-match multiplicity composition figures quoted in the paper
#       (share of k>=8 items, mean k) previously existed in no committed artifact.
#   (3) boxed_decomposition: the boxed-compliance delta decomposition quoted in sec:repl
#       (previously computed by boxed_diag.py, which wrote nothing).
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

JUD = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
out = {}

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

# ================= (1) linkage power at the data-implied measurement noise =========
def infl_est(it, sa, sb, na_, nb_):
    cr = ns["per_item_curves"](it, sa, sb); nr = ns["permutation_null"](it, sa, sb)
    cn = ns["per_item_curves"](it, na_, nb_); nn = ns["permutation_null"](it, na_, nb_)
    return ((cr[64]["judge_gain"] - cr[64]["true_gain"] - nr)
            - (cn[64]["judge_gain"] - cn[64]["true_gain"] - nn))

power = {}
for j in JUD:
    ra, rb = ksc(j, "ref", "a"), ksc(j, "ref", "b")
    na, nb = ksc(j, "noref", "a"), ksc(j, "noref", "b")
    xs_ab, xs_ba, ys_ab, ys_ba = [], [], [], []
    m_counts, o_counts, wsd = [], [], []
    for pid, it in kpool.items():
        if it["k"] <= 1 or pid not in ra or pid not in na: continue
        if not (0.05 <= float(np.mean(it["oracle"])) <= 0.95): continue
        refn = norm(it["ref_answer"])
        ms_a, os_a, ms_b, os_b = [], [], [], []
        for i, ok in enumerate(it["oracle"]):
            if not ok: continue
            match = norm(boxed(it["samples"][i]) or it["samples"][i]) == refn
            (ms_a if match else os_a).append(ra[pid][i])
            (ms_b if match else os_b).append(rb[pid][i])
        if not (ms_a and os_a): continue
        xs_ab.append(float(np.mean(ms_a) - np.mean(os_a)))
        xs_ba.append(float(np.mean(ms_b) - np.mean(os_b)))
        ys_ab.append(infl_est(it, ra[pid], rb[pid], na[pid], nb[pid]))
        ys_ba.append(infl_est(it, rb[pid], ra[pid], nb[pid], na[pid]))
        m_counts.append(len(ms_a)); o_counts.append(len(os_a))
        if len(ms_a) > 1: wsd.append(float(np.std(ms_a, ddof=1)))
        if len(os_a) > 1: wsd.append(float(np.std(os_a, ddof=1)))
    xs_ab, xs_ba = np.array(xs_ab), np.array(xs_ba)
    ys_ab, ys_ba = np.array(ys_ab), np.array(ys_ba)
    n_items = len(xs_ab)
    # measurement SD of the single (a,b) estimates actually used in round7_linkage
    infl_meas_sd = float(np.std(ys_ab - ys_ba, ddof=1) / np.sqrt(2))
    marg_meas_sd = float(np.std(xs_ab - xs_ba, ddof=1) / np.sqrt(2))
    obs_r = float(np.corrcoef(xs_ab, ys_ab)[0, 1])
    # deconvolved (true) variances; floor at 10% of observed to keep the sim defined
    v_marg_true = max(float(np.var(xs_ab, ddof=1)) - marg_meas_sd ** 2,
                      0.1 * float(np.var(xs_ab, ddof=1)))
    v_infl_true = max(float(np.var(ys_ab, ddof=1)) - infl_meas_sd ** 2,
                      0.1 * float(np.var(ys_ab, ddof=1)))
    # exact pathway: slope chosen so the pathway reproduces the true inflation variance
    slope = float(np.sqrt(v_infl_true / v_marg_true))
    shrink = float(np.sqrt(v_marg_true / np.var(xs_ab, ddof=1)))
    mmean = float(xs_ab.mean())

    def sim(reps=4000):
        rs = []
        for _ in range(reps):
            base = rng.choice(xs_ab, n_items)
            true_margin = mmean + (base - mmean) * shrink   # deconvolved, not observed
            true_infl = slope * true_margin
            obs_margin = true_margin + rng.normal(0, marg_meas_sd, n_items)
            obs_infl = true_infl + rng.normal(0, infl_meas_sd, n_items)
            rs.append(float(np.corrcoef(obs_margin, obs_infl)[0, 1]))
        return np.array(rs)

    rs = sim()
    power[j] = dict(
        n_items=n_items,
        observed_r_ab=round(obs_r, 3),
        infl_measurement_sd=round(infl_meas_sd, 3),
        margin_measurement_sd=round(marg_meas_sd, 3),
        obs_infl_sd=round(float(np.std(ys_ab, ddof=1)), 3),
        obs_margin_sd=round(float(np.std(xs_ab, ddof=1)), 3),
        implied_exact_slope=round(slope, 3),
        sim_r_mean=round(float(rs.mean()), 3),
        sim_r_pct2_5=round(float(np.percentile(rs, 2.5)), 3),
        sim_r_pct97_5=round(float(np.percentile(rs, 97.5)), 3),
        observed_r_percentile_in_sim=round(float((rs < obs_r).mean()) * 100, 1),
        mean_valid_matching=round(float(np.mean(m_counts)), 2),
        mean_valid_other=round(float(np.mean(o_counts)), 2),
        within_item_judge_score_sd=round(float(np.mean(wsd)), 3))
out["linkage_power"] = dict(
    note=("exact-pathway simulation at the DATA-IMPLIED inflation measurement SD, estimated "
          "by roles-swapped split-half from the two rubric replicates; margins deconvolved "
          "before the pathway is applied; slope set so the exact pathway reproduces the "
          "deconvolved inflation variance. observed_r_percentile_in_sim < 2.5 rejects an "
          "exact per-item linear pathway at that noise level."),
    by_judge=power)

# ================= (2) composition figures used by the band-match discussion =========
def kdist(pids, pool):
    ks = [pool[p]["k"] for p in pids]
    return dict(n=len(ks), share_k_ge_8=round(float(np.mean([k >= 8 for k in ks])), 3),
                mean_k=round(float(np.mean(ks)), 2))
band_pids = [p for p, it in kpool.items()
             if it["k"] > 1 and 0.2 <= float(np.mean(it["oracle"])) <= 0.8
             and p in ksc(JUD[0], "ref", "a")]
rpool = {}
for l in open("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" in r: rpool[r["problem_id"]] = r
rtasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/repl_main_tasks.jsonl")} \
    if os.path.exists("runs/repl_main_tasks.jsonl") else {}
repl_inband = [p for p in rpool if 0.2 <= float(np.mean(rpool[p]["oracle"])) <= 0.8]
def repl_k(p):
    t = rtasks.get(p, {})
    return t.get("k") or t.get("n_solutions")
repl_ks = [repl_k(p) for p in repl_inband if repl_k(p) is not None]
out["composition"] = dict(
    band_matched_kstrat=kdist(band_pids, kpool),
    replication_inband=dict(n=len(repl_ks),
                            share_k_ge_8=round(float(np.mean([k >= 8 for k in repl_ks])), 3),
                            mean_k=round(float(np.mean(repl_ks)), 2)) if repl_ks else
                       dict(note="replication task k counts unavailable"),
    note="multiplicity composition of the two populations compared in the band-match")

# ================= (3) boxed-compliance decomposition (was boxed_diag.py, unwritten) ==
def rsc(j, c, rep):
    return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
            for l in open(f"runs/bon_scores_repl/synthk__{j}__{c}_{rep}.jsonl")}
parts = {}
for j in JUD:
    ra2, rb2, na2, nb2 = rsc(j, "ref", "a"), rsc(j, "ref", "b"), rsc(j, "noref", "a"), rsc(j, "noref", "b")
    for pid in repl_inband:
        it = rpool[pid]
        if pid not in ra2: continue
        cr = ns["per_item_curves"](it, ra2[pid], rb2[pid]); cn = ns["per_item_curves"](it, na2[pid], nb2[pid])
        parts.setdefault(pid, []).append(dict(
            jg_ref=cr[64]["judge_gain"], tg_ref=cr[64]["true_gain"],
            jg_bl=cn[64]["judge_gain"], tg_bl=cn[64]["true_gain"]))
bc = {p: float(np.mean([boxed(s) is not None for s in rpool[p]["samples"]])) for p in repl_inband}
med = float(np.median([bc[p] for p in parts]))
dec = {}
for name, sel in (("clean_ge_median", lambda p: bc[p] >= med), ("messy_lt_median", lambda p: bc[p] < med)):
    ps = [p for p in parts if sel(p)]
    def m(k): return round(float(np.mean([np.mean([d[k] for d in parts[p]]) for p in ps])), 3)
    dec[name] = dict(n=len(ps),
                     base_acc=round(float(np.mean([np.mean(rpool[p]["oracle"]) for p in ps])), 3),
                     judge_gain_ref=m("jg_ref"), judge_gain_blind=m("jg_bl"),
                     judge_gain_delta=round(m("jg_ref") - m("jg_bl"), 3),
                     true_gain_ref=m("tg_ref"), true_gain_blind=m("tg_bl"),
                     true_gain_delta=round(m("tg_ref") - m("tg_bl"), 3))
out["boxed_decomposition"] = dict(median_boxed_rate=round(med, 3), by_stratum=dec)

# ================= (4) worked example of the inflation estimator ====================
# One replication item, chosen by a deterministic rule (the in-band item whose per-item
# referenced-minus-blind inflation delta under Qwen-7B is closest to the pooled E1 point
# estimate), unpacked into raw score points so the estimator is concrete.
j = JUD[0]
ra2, rb2 = rsc(j, "ref", "a"), rsc(j, "ref", "b")
na2, nb2 = rsc(j, "noref", "a"), rsc(j, "noref", "b")
per_delta = {}
for pid in repl_inband:
    it = rpool[pid]
    if pid not in ra2: continue
    per_delta[pid] = infl_est(it, ra2[pid], rb2[pid], na2[pid], nb2[pid])
E1_QWEN = 1.287  # repl_results.json per-judge point estimate
wpid = min(per_delta, key=lambda p: abs(per_delta[p] - E1_QWEN))
it = rpool[wpid]

def unpack(sa, sb):
    base_b = float(np.mean(sb)); base_sd = float(np.std(sb)) or 1.0
    base_acc = float(np.mean(it["oracle"]))
    i = int(np.argmax(sa))
    return dict(selected_reported_score=round(sb[i], 2),
                pool_mean_score=round(base_b, 2), pool_score_sd=round(base_sd, 2),
                selected_valid=bool(it["oracle"][i]), pool_valid_rate=round(base_acc, 3),
                judge_gain_sd_units=round((sb[i] - base_b) / base_sd, 2),
                true_gain=round(it["oracle"][i] - base_acc, 3))
w_ref = unpack(ra2[wpid], rb2[wpid])
w_bl = unpack(na2[wpid], nb2[wpid])
null_ref = ns["permutation_null"](it, ra2[wpid], rb2[wpid])
null_bl = ns["permutation_null"](it, na2[wpid], nb2[wpid])
out["worked_example"] = dict(
    selection_rule="in-band item with Qwen-7B per-item delta closest to the per-judge E1 point estimate",
    problem_id=wpid, per_item_delta=round(per_delta[wpid], 3),
    referenced=w_ref, blind=w_bl,
    permutation_null_ref=round(null_ref, 3), permutation_null_blind=round(null_bl, 3),
    note=("hack gap per arm = judge_gain - true_gain - permutation null; the per-item "
          "inflation delta differences the two arms' gaps. The tie-splitting selection in "
          "per_item_curves makes the committed estimator's per-item delta differ slightly "
          "from the single-argmax unpacking shown here, which is illustrative only."))

json.dump(out, open("../../papers/analysis/round9_provenance.json", "w"), indent=1)
print(json.dumps(out, indent=1))
