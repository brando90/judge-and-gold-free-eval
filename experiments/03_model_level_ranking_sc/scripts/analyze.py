#!/usr/bin/env python3
"""Experiment 03 analysis: model-level self-consistency (SC) ranking vs gold accuracy, plus audits A1 and A2.

Implements PREREG.md. CPU only, no model calls. Run:
    ~/.venvs/jfe/bin/python experiments/03_model_level_ranking_sc/scripts/analyze.py [--quick]
Inputs: results/gen/bon_math__<model>.jsonl (new models, n=16) and the committed Llama-3.1-8B n=64 samples.
Writes results/results.json, results/tables.md, results/*.png. Answer keys are cached in results/key_cache.json.
"""
from __future__ import annotations

import importlib.util, json, re, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parent.parent
OUT = EXP / "results"
GEN = OUT / "gen"
OUT.mkdir(exist_ok=True)
QUICK = "--quick" in sys.argv

N = 16
BOOT = 2000
SEED = 20261125
PARSE_TIMEOUT = 10

spec = importlib.util.spec_from_file_location("boxed", REPO / "experiments/tfa-vs-judge/tfa/boxed.py")
boxed = importlib.util.module_from_spec(spec); spec.loader.exec_module(boxed)
extract_boxed = boxed.extract_boxed
from math_verify import parse, verify  # noqa: E402

MODELS = [  # id, label, file (relative), n available
    ("llama31_8b", "Llama-3.1-8B-Instruct", REPO / "experiments/tfa-vs-judge/runs/bon/bon_math__meta-llama__Llama-3.1-8B-Instruct.jsonl"),
    ("qwen25_7b", "Qwen2.5-7B-Instruct", GEN / "bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl"),
    ("qwen3_4b", "Qwen3-4B (non-thinking)", GEN / "bon_math__Qwen__Qwen3-4B.jsonl"),
    ("qwen3_1p7b", "Qwen3-1.7B (non-thinking)", GEN / "bon_math__Qwen__Qwen3-1.7B.jsonl"),
    ("dsmath_7b_rl", "DeepSeek-Math-7B-RL", GEN / "bon_math__deepseek-ai__deepseek-math-7b-rl.jsonl"),
    ("mistral_7b", "Mistral-7B-Instruct-v0.2", GEN / "bon_math__mistralai__Mistral-7B-Instruct-v0.2.jsonl"),
]


# ---------------------------------------------------------------- answer matching (experiment 02 matcher)
def norm_plain(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def pre_norm(s: str) -> str:
    t = s.strip()
    while t.startswith("$") and t.endswith("$") and len(t) >= 2:
        t = t[1:-1].strip()
    t = t.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac").replace("\\left", "").replace("\\right", "")
    t = t.replace("\\!", "").replace("\\,", "").replace("\\ ", " ")
    t = re.sub(r"[.,;]+\s*$", "", t)
    return t.strip()


def canon_key(mode: str, s: str) -> str:
    """mode 'norm' (primary, D3) or 'raw'. Equal keys = same answer."""
    t = pre_norm(s) if mode == "norm" else s
    k = "S:" + norm_plain(t)
    try:
        p = parse("$" + t + "$", parsing_timeout=PARSE_TIMEOUT)
        if p and not isinstance(p[0], str):
            e = p[0]
            try:
                if getattr(e, "is_number", False):
                    k = "N:" + repr(round(float(e.evalf()), 6))
                else:
                    k = "E:" + str(e)
            except Exception:
                k = "E:" + str(e)
    except Exception:
        pass
    return k


def _key_job(a):
    return canon_key(a[0], a[1])


def gold_ok(gold: str, ans: str) -> int:
    try:
        g = parse("$" + pre_norm(gold) + "$", parsing_timeout=PARSE_TIMEOUT)
        p = parse("$" + pre_norm(ans) + "$", parsing_timeout=PARSE_TIMEOUT)
        if not g or not p:
            return int(norm_plain(pre_norm(gold)) == norm_plain(pre_norm(ans)))
        return int(bool(verify(g, p, timeout_seconds=PARSE_TIMEOUT)))
    except Exception:
        return int(norm_plain(pre_norm(gold)) == norm_plain(pre_norm(ans)))


def _gold_job(a):
    return gold_ok(a[0], a[1])


def _pair_job(a):
    """pairwise equivalence of two normalised answer strings: (equal, unparseable, timeout)."""
    s1, s2 = a
    try:
        p1 = parse("$" + s1 + "$", parsing_timeout=PARSE_TIMEOUT)
        p2 = parse("$" + s2 + "$", parsing_timeout=PARSE_TIMEOUT)
    except Exception:
        return (0, 1, 0)
    if not p1 or not p2:
        return (0, 1, 0)
    try:
        r = bool(verify(p1, p2, timeout_seconds=PARSE_TIMEOUT)) or bool(verify(p2, p1, timeout_seconds=PARSE_TIMEOUT))
        return (int(r), 0, 0)
    except Exception:
        return (0, 0, 1)


# ---------------------------------------------------------------- statistics helpers
def clusters(keys: list[str | None]) -> np.ndarray:
    ids = np.full(len(keys), -1, dtype=int)
    seen: dict[str, int] = {}
    for i, k in enumerate(keys):
        if k is not None:
            ids[i] = seen.setdefault(k, len(seen))
    return ids


def problem_sc(ids: np.ndarray) -> float:
    """pairwise agreement rate = mean item SC, unboxed counted 0."""
    n = len(ids)
    v = ids[ids >= 0]
    if len(v) == 0 or n < 2:
        return 0.0
    c = np.bincount(v)
    return float((c * (c - 1)).sum() / (n * (n - 1)))


def problem_sc_boxed(ids: np.ndarray):
    v = ids[ids >= 0]
    if len(v) < 2:
        return np.nan
    c = np.bincount(v)
    return float((c * (c - 1)).sum() / (len(v) * (len(v) - 1)))


def scp(ids: np.ndarray) -> float:
    v = ids[ids >= 0]
    return 0.0 if len(v) == 0 else float(np.bincount(v).max() / len(ids))


def plurality_correct(ids: np.ndarray, corr: np.ndarray) -> float:
    v = ids[ids >= 0]
    if len(v) == 0:
        return 0.0
    cid = int(np.bincount(v).argmax())  # ties -> lowest id = first-occurring cluster
    return float(corr[np.where(ids == cid)[0][0]])


def select_rule_a(ids, corr):
    """experiment 02 rule: argmax item SC, ties to the lowest index; returns (correct, selected_is_unboxed, max_sc_zero)."""
    n = len(ids)
    sc = np.zeros(n)
    for i in range(n):
        if ids[i] >= 0:
            sc[i] = (np.sum(ids == ids[i]) - 1) / (n - 1)
    j = int(np.argmax(sc))
    return float(corr[j]), int(ids[j] < 0), int(sc.max() == 0)


def select_rule_b(ids, corr):
    """fixed rule: as A, but when all SC are 0 pick the first boxed sample; none boxed = wrong."""
    n = len(ids)
    sc = np.zeros(n)
    for i in range(n):
        if ids[i] >= 0:
            sc[i] = (np.sum(ids == ids[i]) - 1) / (n - 1)
    if sc.max() == 0:
        b = np.where(ids >= 0)[0]
        return float(corr[b[0]]) if len(b) else 0.0
    return float(corr[int(np.argmax(sc))])


def kendall_D(a, b):
    """number of discordant pairs between two score vectors (ties count as not discordant)."""
    D = 0
    m = len(a)
    for i in range(m):
        for j in range(i + 1, m):
            if (a[i] - a[j]) * (b[i] - b[j]) < 0:
                D += 1
    return D


def tau(a, b):
    t = kendalltau(a, b)[0]
    return float(t) if t == t else 0.0


def main():
    t0 = time.time()
    tasks = [json.loads(l) for l in open(REPO / "experiments/tfa-vs-judge/runs/bon_math_tasks.jsonl")]
    pids = [t["problem_id"] for t in tasks]
    gold = {t["problem_id"]: t["answer"] for t in tasks}
    level = np.array([int(t["level"]) for t in tasks])
    P = len(pids)

    # ---- load
    data, missing = {}, []
    for mid, label, path in MODELS:
        if not path.exists():
            missing.append(mid); continue
        rows = {}
        for l in open(path):
            r = json.loads(l); rows[r["problem_id"]] = r
        if len(rows) < P:
            missing.append(f"{mid} (only {len(rows)} problems)"); continue
        data[mid] = dict(label=label, samples=[rows[p]["samples"] for p in pids],
                         finish=[rows[p].get("finish") for p in pids],
                         oracle=[json.loads(rows[p]["oracle"]) if isinstance(rows[p].get("oracle"), str) else rows[p].get("oracle") for p in pids])
    mids = [m for m in (x[0] for x in MODELS) if m in data]
    print("models:", mids, "missing:", missing, flush=True)

    # ---- answers
    ans = {m: [[extract_boxed(s) for s in data[m]["samples"][pi]] for pi in range(P)] for m in mids}
    if QUICK:
        pass

    # ---- keys (cached) for both matchers
    cache_path = OUT / "key_cache.json"
    cache = json.load(open(cache_path)) if cache_path.exists() else {}
    need = sorted({(mode, a) for m in mids for row in ans[m] for a in row if a for mode in ("norm", "raw") if f"{mode}\x00{a}" not in cache})
    print("keys to compute:", len(need), flush=True)
    if need:
        with Pool(4) as pool:
            res = pool.map(_key_job, need, chunksize=200)
        for (mode, a), k in zip(need, res):
            cache[f"{mode}\x00{a}"] = k
        json.dump(cache, open(cache_path, "w"))
    print(f"keys done {time.time()-t0:.0f}s", flush=True)

    # ---- gold correctness (cached)
    gpath = OUT / "gold_cache.json"
    gcache = json.load(open(gpath)) if gpath.exists() else {}
    gneed = sorted({(pids[pi], a) for m in mids for pi in range(P) for a in ans[m][pi] if a and f"{pids[pi]}\x00{a}" not in gcache})
    print("gold checks to compute:", len(gneed), flush=True)
    if gneed:
        with Pool(4) as pool:
            res = pool.map(_gold_job, [(gold[p], a) for p, a in gneed], chunksize=200)
        for (p, a), v in zip(gneed, res):
            gcache[f"{p}\x00{a}"] = v
        json.dump(gcache, open(gpath, "w"))
    print(f"gold done {time.time()-t0:.0f}s", flush=True)

    def keys_of(m, pi, mode, n):
        return [(cache[f"{mode}\x00{a}"] if a else None) for a in ans[m][pi][:n]]

    def corr_of(m, pi, n):
        return np.array([gcache[f"{pids[pi]}\x00{a}"] if a else 0 for a in ans[m][pi][:n]], dtype=float)

    R = dict(models=mids, labels={m: data[m]["label"] for m in mids}, missing=missing, n=N)

    def per_problem(mode, n, nsamp_cap=None):
        """per-problem arrays per model for the first n samples."""
        out = {}
        for m in mids:
            sc = np.zeros(P); scpv = np.zeros(P); scb = np.full(P, np.nan); p1 = np.zeros(P); maj = np.zeros(P)
            p16 = np.zeros(P); box = np.zeros(P); plur_corr = np.zeros(P); plur_sc = np.zeros(P)
            for pi in range(P):
                ids = clusters(keys_of(m, pi, mode, n)); c = corr_of(m, pi, n)
                sc[pi] = problem_sc(ids); scpv[pi] = scp(ids); scb[pi] = problem_sc_boxed(ids)
                p1[pi] = c.mean(); maj[pi] = plurality_correct(ids, c); p16[pi] = float(c.max() > 0)
                box[pi] = float(np.mean(ids >= 0)); plur_corr[pi] = maj[pi]; plur_sc[pi] = scpv[pi]
            out[m] = dict(sc=sc, scp=scpv, scb=scb, pass1=p1, maj=maj, passk=p16, boxed=box)
        return out

    PP = per_problem("norm", N)
    PPraw = per_problem("raw", N)

    # ---- model-level table
    def model_vals(pp, idx=None):
        idx = np.arange(P) if idx is None else idx
        return {m: dict(sc=float(pp[m]["sc"][idx].mean()), scp=float(pp[m]["scp"][idx].mean()),
                        scb=float(np.nanmean(pp[m]["scb"][idx])), pass1=float(pp[m]["pass1"][idx].mean()),
                        maj=float(pp[m]["maj"][idx].mean()), passk=float(pp[m]["passk"][idx].mean()),
                        boxed=float(pp[m]["boxed"][idx].mean())) for m in mids}

    MV = model_vals(PP); R["model_level"] = MV; R["model_level_raw_matcher"] = model_vals(PPraw)
    cands = ["sc", "scp", "scb", "maj", "passk", "boxed"]
    tgt = np.array([MV[m]["pass1"] for m in mids])
    E1 = {}
    for cnd in cands:
        v = np.array([MV[m][cnd] for m in mids])
        E1[cnd] = dict(D=kendall_D(v, tgt), tau=tau(v, tgt), spearman=float(spearmanr(v, tgt)[0]), pearson=float(pearsonr(v, tgt)[0]) if len(mids) > 2 else None)
    R["E1"] = E1
    # discordant pairs for primary
    sc_v = np.array([MV[m]["sc"] for m in mids])
    disc = []
    for i in range(len(mids)):
        for j in range(i + 1, len(mids)):
            if (sc_v[i] - sc_v[j]) * (tgt[i] - tgt[j]) < 0:
                disc.append(dict(a=mids[i], b=mids[j], pass1_gap=float(abs(tgt[i] - tgt[j])), sc_gap=float(abs(sc_v[i] - sc_v[j]))))
    R["E1_discordant_pairs"] = disc
    # bootstrap
    rng = np.random.default_rng(SEED)
    Ds = {c: [] for c in cands}; taus = {c: [] for c in cands}
    pair_match = {}
    pairs = [(i, j) for i in range(len(mids)) for j in range(i + 1, len(mids))]
    pm = {p: 0 for p in pairs}
    for b in range(BOOT):
        idx = rng.integers(0, P, P)
        mv = model_vals(PP, idx)
        t = np.array([mv[m]["pass1"] for m in mids])
        for cnd in cands:
            v = np.array([mv[m][cnd] for m in mids])
            Ds[cnd].append(kendall_D(v, t)); taus[cnd].append(tau(v, t))
            if cnd == "sc":
                for (i, j) in pairs:
                    if (v[i] - v[j]) * (t[i] - t[j]) > 0:
                        pm[(i, j)] += 1
    R["E1_boot"] = {c: dict(P_D_le_3=float(np.mean(np.array(Ds[c]) <= 3)), P_D_le_2=float(np.mean(np.array(Ds[c]) <= 2)),
                            D_mean=float(np.mean(Ds[c])), tau_ci=[float(np.percentile(taus[c], 2.5)), float(np.percentile(taus[c], 97.5))]) for c in cands}
    R["E1_pair_concordance_prob"] = {f"{mids[i]}|{mids[j]}": pm[(i, j)] / BOOT for (i, j) in pairs}
    D_sc = E1["sc"]["D"]; maxgap = max([d["pass1_gap"] for d in disc], default=0.0)
    pD3 = R["E1_boot"]["sc"]["P_D_le_3"]
    if D_sc >= 4 or maxgap >= 0.10:
        verdict = "NO"
    elif D_sc <= 2 and maxgap < 0.05 and pD3 >= 0.80:
        verdict = "YES"
    else:
        verdict = "INCONCLUSIVE"
    R["E1_verdict"] = dict(verdict=verdict, D=D_sc, max_discordant_pass1_gap=maxgap, boot_P_D_le_3=pD3,
                           boxed_control_D=E1["boxed"]["D"], boxed_control_beats_or_ties_sc=bool(E1["boxed"]["D"] <= D_sc))

    # ---- E2 level and gap
    R["E2"] = dict(pearson_sc_pass1=E1["sc"]["pearson"],
                   gaps={m: dict(sc_minus_pass1=MV[m]["sc"] - MV[m]["pass1"], scp_minus_pass1=MV[m]["scp"] - MV[m]["pass1"]) for m in mids})

    # ---- E3 confident wrongness per model
    E3 = {}
    for m in mids:
        sp_, mj = PP[m]["scp"], PP[m]["maj"]
        sel = sp_ >= 0.5
        E3[m] = dict(coverage=float(sel.mean()), precision=float(mj[sel].mean()) if sel.any() else None,
                     passes=bool(sel.any() and mj[sel].mean() >= 0.90))
    R["E3"] = E3

    # ---- E4 split-half stability
    rng2 = np.random.default_rng(SEED + 1)
    id_cache = {m: [clusters(keys_of(m, pi, "norm", N)) for pi in range(P)] for m in mids}
    corr_cache = {m: [corr_of(m, pi, N) for pi in range(P)] for m in mids}
    t_ss, t_sg, t_gg = [], [], []
    for s in range(50 if QUICK else 200):
        perm = rng2.permutation(N); h1, h2 = perm[:N // 2], perm[N // 2:]
        scs = [[], []]; p1s = [[], []]
        for m in mids:
            for h, hs in enumerate((h1, h2)):
                scs[h].append(np.mean([problem_sc(id_cache[m][pi][hs]) for pi in range(P)]))
                p1s[h].append(np.mean([corr_cache[m][pi][hs].mean() for pi in range(P)]))
        t_ss.append(tau(scs[0], scs[1])); t_sg.append(tau(scs[0], p1s[1])); t_gg.append(tau(p1s[0], p1s[1]))
    R["E4"] = dict(sc_half_vs_sc_half_tau=float(np.mean(t_ss)), sc_half_vs_pass1_other_half_tau=float(np.mean(t_sg)), pass1_half_vs_half_tau=float(np.mean(t_gg)))

    # ---- E5 per level
    E5 = {}
    for name, sel in (("levels_1_2", level <= 2), ("levels_4_5", level >= 4)):
        idx = np.where(sel)[0]; mv = model_vals(PP, idx)
        a = np.array([mv[m]["sc"] for m in mids]); b = np.array([mv[m]["pass1"] for m in mids])
        E5[name] = dict(tau=tau(a, b), D=kendall_D(a, b), pass1={m: mv[m]["pass1"] for m in mids}, sc={m: mv[m]["sc"] for m in mids})
    R["E5"] = E5

    # ---- Llama oracle agreement and Llama n=64 supplement
    if "llama31_8b" in data and data["llama31_8b"]["oracle"][0] is not None:
        agree = tot = 0
        for pi in range(P):
            c = corr_of("llama31_8b", pi, 64); o = np.array(data["llama31_8b"]["oracle"][pi][:64])
            agree += int((c == o).sum()); tot += len(o)
        R["llama_oracle_agreement"] = agree / tot
        pp64 = {}
        sc64 = np.array([problem_sc(clusters(keys_of("llama31_8b", pi, "norm", 64))) for pi in range(P)])
        p64 = np.array([corr_of("llama31_8b", pi, 64).mean() for pi in range(P)])
        R["llama_n64"] = dict(sc=float(sc64.mean()), pass1=float(p64.mean()))

    # ---- A1 unboxed argmax
    A1 = {}
    for m in mids:
        for nn in ([N] + ([64] if m == "llama31_8b" else [])):
            ra, rb, un, z = [], [], [], []
            for pi in range(P):
                ids = clusters(keys_of(m, pi, "norm", nn)); c = corr_of(m, pi, nn)
                a_, u_, z_ = select_rule_a(ids, c); b_ = select_rule_b(ids, c)
                ra.append(a_); rb.append(b_); un.append(u_); z.append(z_)
            ra, rb = np.array(ra), np.array(rb); d = rb - ra
            bs = [d[rng.integers(0, P, P)].mean() for _ in range(1000)]
            key = f"{m}@{nn}"
            A1[key] = dict(max_sc_zero_share=float(np.mean(z)), selected_unboxed_share=float(np.mean(un)), acc_rule_a=float(ra.mean()),
                           acc_rule_b=float(rb.mean()), diff_b_minus_a=float(d.mean()), diff_ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                           all_unboxed_share=float(np.mean([np.all(clusters(keys_of(m, pi, "norm", nn)) < 0) for pi in range(P)])))
    R["A1"] = A1
    sel_a = np.array([A1[f"{m}@{N}"]["acc_rule_a"] for m in mids]); sel_b = np.array([A1[f"{m}@{N}"]["acc_rule_b"] for m in mids])
    R["A1_ranking"] = dict(D_vs_pass1_rule_a=kendall_D(sel_a, tgt), D_vs_pass1_rule_b=kendall_D(sel_b, tgt),
                           order_a=[mids[i] for i in np.argsort(-sel_a)], order_b=[mids[i] for i in np.argsort(-sel_b)])
    R["A1_pass"] = bool(all(A1[f"{m}@{N}"]["selected_unboxed_share"] <= 0.01 and abs(A1[f"{m}@{N}"]["diff_b_minus_a"]) <= 0.005 for m in mids))
    print(f"A1 done {time.time()-t0:.0f}s", flush=True)

    # ---- A2 canonical keys vs pairwise verify
    rng3 = np.random.default_rng(SEED)
    A2 = {}; per_model_sc_key, per_model_sc_pair = {}, {}
    NA = 12 if QUICK else 60
    for m in mids:
        elig = [pi for pi in range(P) if len({norm_plain(pre_norm(a)) for a in ans[m][pi][:N] if a}) >= 2]
        pick = sorted(rng3.choice(elig, size=min(NA, len(elig)), replace=False).tolist())
        jobs, meta = [], []
        for pi in pick:
            strs = sorted({norm_plain(pre_norm(a)) for a in ans[m][pi][:N] if a})
            for i in range(len(strs)):
                for j in range(i + 1, len(strs)):
                    jobs.append((strs[i], strs[j])); meta.append((pi, strs[i], strs[j]))
        with Pool(4) as pool:
            res = pool.map(_pair_job, jobs, chunksize=20)
        eq = {}; unp = tmo = 0
        agree_eq = agree_ne = key_eq_ver_ne = key_ne_ver_eq = 0
        for (pi, s1, s2), (e, u, t_) in zip(meta, res):
            ke = canon_key("norm", s1) == canon_key("norm", s2)
            unp += u; tmo += t_
            if u:
                continue
            eq[(pi, s1, s2)] = bool(e)
            if ke and e: agree_eq += 1
            elif (not ke) and (not e): agree_ne += 1
            elif ke and not e: key_eq_ver_ne += 1
            else: key_ne_ver_eq += 1
        npairs = agree_eq + agree_ne + key_eq_ver_ne + key_ne_ver_eq
        # partitions by pairwise connected components
        dscp, sck, scp_ = [], [], []
        for pi in pick:
            strs = sorted({norm_plain(pre_norm(a)) for a in ans[m][pi][:N] if a})
            par = {s: s for s in strs}
            def f(x):
                while par[x] != x:
                    par[x] = par[par[x]]; x = par[x]
                return x
            for (p2, s1, s2), e in eq.items():
                if p2 == pi and e:
                    par[f(s1)] = f(s2)
            lab = [f(norm_plain(pre_norm(a))) if a else None for a in ans[m][pi][:N]]
            idp = clusters(lab); idk = clusters(keys_of(m, pi, "norm", N))
            dscp.append(abs(scp(idp) - scp(idk))); sck.append(problem_sc(idk)); scp_.append(problem_sc(idp))
        A2[m] = dict(problems=len(pick), pairs_compared=npairs, unparseable_pairs=unp, timeouts=tmo, both_equal=agree_eq, both_different=agree_ne,
                     key_equal_verify_not=key_eq_ver_ne, key_different_verify_equal=key_ne_ver_eq,
                     disagreement_rate=(key_eq_ver_ne + key_ne_ver_eq) / npairs if npairs else None,
                     mean_abs_dSCP=float(np.mean(dscp)), sc_key=float(np.mean(sck)), sc_pairwise=float(np.mean(scp_)))
        per_model_sc_key[m] = float(np.mean(sck)); per_model_sc_pair[m] = float(np.mean(scp_))
        print(f"A2 {m} done {time.time()-t0:.0f}s", flush=True)
    R["A2"] = A2
    kk = np.array([per_model_sc_key[m] for m in mids]); pw = np.array([per_model_sc_pair[m] for m in mids])
    R["A2_ranking"] = dict(D_between_key_and_pairwise_order=kendall_D(kk, pw), order_key=[mids[i] for i in np.argsort(-kk)], order_pairwise=[mids[i] for i in np.argsort(-pw)])
    tot_pairs = sum(A2[m]["pairs_compared"] for m in mids); tot_dis = sum(A2[m]["key_equal_verify_not"] + A2[m]["key_different_verify_equal"] for m in mids)
    R["A2_pass"] = bool(tot_pairs and tot_dis / tot_pairs <= 0.01 and max(A2[m]["mean_abs_dSCP"] for m in mids) <= 0.01 and R["A2_ranking"]["D_between_key_and_pairwise_order"] == 0)
    R["A2_overall_disagreement_rate"] = tot_dis / tot_pairs if tot_pairs else None

    json.dump(R, open(OUT / ("results_quick.json" if QUICK else "results.json"), "w"), indent=1)
    write_tables(R)
    make_figs(R)
    print("DONE", f"{time.time()-t0:.0f}s", flush=True)


def write_tables(R):
    mids = R["models"]; L = R["labels"]; MV = R["model_level"]
    o = []
    o.append("# Experiment 03 tables (generated by scripts/analyze.py)\n")
    o.append("## Model level (n=16 samples x 500 MATH-500 problems each; primary matcher = normalised keys)\n")
    o.append("| model | pass@1 | maj@16 | pass@16 | SC (pairwise agreement) | mean SCP | SC boxed-only | boxed rate |")
    o.append("|---|---|---|---|---|---|---|---|")
    for m in sorted(mids, key=lambda m: -MV[m]["pass1"]):
        v = MV[m]
        o.append(f"| {L[m]} | {v['pass1']:.3f} | {v['maj']:.3f} | {v['passk']:.3f} | {v['sc']:.3f} | {v['scp']:.3f} | {v['scb']:.3f} | {v['boxed']:.3f} |")
    o.append("\n## E1 ranking vs pass@1 (D = discordant model pairs of 15)\n")
    o.append("| candidate | D | Kendall tau | Spearman | boot P(D<=3) | tau 95% CI |")
    o.append("|---|---|---|---|---|---|")
    for c, e in R["E1"].items():
        b = R["E1_boot"][c]
        o.append(f"| {c} | {e['D']} | {e['tau']:.3f} | {e['spearman']:.3f} | {b['P_D_le_3']:.2f} | [{b['tau_ci'][0]:.2f}, {b['tau_ci'][1]:.2f}] |")
    o.append(f"\nVerdict (frozen rule): **{R['E1_verdict']['verdict']}**; discordant pairs: {json.dumps(R['E1_discordant_pairs'])}\n")
    o.append("## E3 confident wrongness per model\n\n| model | coverage SCP>=0.5 | precision of plurality | passes 0.90 |\n|---|---|---|---|")
    for m in mids:
        e = R["E3"][m]
        o.append(f"| {L[m]} | {e['coverage']:.3f} | {e['precision'] if e['precision'] is None else round(e['precision'], 3)} | {e['passes']} |")
    o.append("\n## A1 argmax picks unboxed\n\n| model@n | max SC = 0 share | selected unboxed share | acc rule A (02) | acc rule B (fixed) | B - A [95% CI] |\n|---|---|---|---|---|---|")
    for k, e in R["A1"].items():
        o.append(f"| {k} | {e['max_sc_zero_share']:.3f} | {e['selected_unboxed_share']:.3f} | {e['acc_rule_a']:.3f} | {e['acc_rule_b']:.3f} | {e['diff_b_minus_a']:+.4f} [{e['diff_ci'][0]:+.4f}, {e['diff_ci'][1]:+.4f}] |")
    o.append("\n## A2 canonical keys vs pairwise Math-Verify\n\n| model | problems | pairs | both equal | both different | key equal, verify not | key different, verify equal | unparseable | timeouts | mean abs dSCP |\n|---|---|---|---|---|---|---|---|---|---|")
    for m in mids:
        e = R["A2"][m]
        o.append(f"| {L[m]} | {e['problems']} | {e['pairs_compared']} | {e['both_equal']} | {e['both_different']} | {e['key_equal_verify_not']} | {e['key_different_verify_equal']} | {e['unparseable_pairs']} | {e['timeouts']} | {e['mean_abs_dSCP']:.4f} |")
    (OUT / ("tables_quick.md" if QUICK else "tables.md")).write_text("\n".join(o) + "\n")


def make_figs(R):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    mids = R["models"]; L = R["labels"]; MV = R["model_level"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for k, (cnd, name) in enumerate((("sc", "SC (pairwise agreement)"), ("boxed", "boxed rate (control)"))):
        x = [MV[m]["pass1"] for m in mids]; y = [MV[m][cnd] for m in mids]
        ax[k].scatter(x, y)
        for m, xi, yi in zip(mids, x, y):
            ax[k].annotate(L[m].split(" ")[0], (xi, yi), fontsize=7)
        ax[k].set_xlabel("gold pass@1"); ax[k].set_ylabel(name); ax[k].grid(True)
        ax[k].set_title(f"{name}: Kendall D={R['E1'][cnd]['D']}/15")
    fig.tight_layout(); fig.savefig(OUT / ("model_rank_quick.png" if QUICK else "model_rank.png"), dpi=130)


if __name__ == "__main__":
    main()
