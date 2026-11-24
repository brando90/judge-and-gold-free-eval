#!/usr/bin/env python3
"""Experiment 02 pilot: gold-free, judge-free self-consistency (SC) vs judges and gold metrics.

Implements PREREG.md exactly. Analysis only: no model calls. Run from anywhere:
    ~/.venvs/jfe/bin/python experiments/02_gold_free_self_consistency/scripts/run_pilot.py
Needs: numpy, scipy, math-verify, matplotlib (venv: python3 -m venv ~/.venvs/jfe && ~/.venvs/jfe/bin/pip install math-verify numpy scipy matplotlib).
Writes results/*.json, results/tables.md, results/*.png.
"""
from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parent.parent
RUNS = REPO / "experiments" / "tfa-vs-judge" / "runs"
MATCHER = "norm" if "--normalize" in sys.argv else "raw"  # raw = PREREG matcher; norm = D3 (normalise, then parse)
OUT = EXP / ("results_v2_normalized" if MATCHER == "norm" else "results")
OUT.mkdir(exist_ok=True)

SEED = 20261124
N = 64
BOOT = 2000
PARSE_TIMEOUT = 10  # seconds per answer string (run 1 used 1 s: too many load-induced timeouts, see RESULTS.md D2)

spec = importlib.util.spec_from_file_location("boxed", REPO / "experiments/tfa-vs-judge/tfa/boxed.py")
boxed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boxed)
extract_boxed = boxed.extract_boxed

from math_verify import parse  # noqa: E402


# ---------------------------------------------------------------- answer matching
def norm_plain(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def pre_norm(s: str) -> str:
    """D3 normalisation before parsing: strip $ wrappers, trailing period/comma, \\dfrac->\\frac, \\left/\\right, thin spaces."""
    t = s.strip()
    while t.startswith("$") and t.endswith("$") and len(t) >= 2:
        t = t[1:-1].strip()
    t = t.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac").replace("\\left", "").replace("\\right", "")
    t = t.replace("\\!", "").replace("\\,", "").replace("\\ ", " ")
    t = re.sub(r"[.,;]+\s*$", "", t)
    return t.strip()


_KEY_CACHE: dict[str, str] = {}


def canon_key(s: str) -> str:
    """Canonical key of an answer string from Math-Verify's parser: equal keys = same answer.

    Numeric expressions are keyed by their value rounded to 6 digits, other expressions by sympy's str.
    If the parser returns nothing, fall back to the whitespace-normalised string. (Deviation D1: replaces
    pairwise verify(), too slow on the shared CPU.)
    """
    k = _KEY_CACHE.get(s)
    if k is not None:
        return k
    k = "S:" + norm_plain(s)
    t = pre_norm(s) if MATCHER == "norm" else s
    if MATCHER == "norm":
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
    _KEY_CACHE[s] = k
    return k


def cluster_mv(answers: list[str | None]) -> np.ndarray:
    """Cluster ids per sample by canonical key; missing answer -> id -1."""
    ids = np.full(len(answers), -1, dtype=int)
    seen: dict[str, int] = {}
    for i, a in enumerate(answers):
        if a is None or a == "":
            continue
        ids[i] = seen.setdefault(canon_key(a), len(seen))
    return ids


def cluster_plain(answers: list[str | None]) -> np.ndarray:
    ids = np.full(len(answers), -1, dtype=int)
    seen: dict[str, int] = {}
    for i, a in enumerate(answers):
        if a is None or a == "":
            continue
        k = a  # strict: raw string equality, no normalisation at all
        ids[i] = seen.setdefault(k, len(seen))
    return ids


def sc_from_ids(ids: np.ndarray) -> np.ndarray:
    n = len(ids)
    out = np.zeros(n)
    for i in range(n):
        if ids[i] >= 0:
            out[i] = (np.sum(ids == ids[i]) - 1) / (n - 1)
    return out


def scp_from_ids(ids: np.ndarray) -> float:
    v = ids[ids >= 0]
    if len(v) == 0:
        return 0.0
    return np.bincount(v).max() / len(ids)


# ---------------------------------------------------------------- P1 surface rewrites
REWRITES = [
    lambda s: s.replace(r"\frac", r"\dfrac") if r"\frac" in s else None,
    lambda s: s.replace(r"\dfrac", r"\frac") if r"\dfrac" in s else None,
    lambda s: s.replace(" ", "") if " " in s else None,
    lambda s: s.replace(r"\left(", "(").replace(r"\right)", ")") if r"\left(" in s else None,
    lambda s: s + "." if not s.endswith(".") else None,
    lambda s: s[:-1] if s.endswith(".") else None,
    lambda s: "$" + s + "$" if not s.startswith("$") else None,
]


REWRITES_HELD = [  # P1b: not used by the D3 normaliser
    lambda s: re.sub(r"\\frac\{(-?\d+)\}\{(\d+)\}", r"\1/\2", s) if re.search(r"\\frac\{-?\d+\}\{\d+\}", s) else None,
    lambda s: s + ".0" if re.fullmatch(r"-?\d+", s.strip()) else None,
    lambda s: "." + s.strip()[2:] if re.fullmatch(r"0\.\d+", s.strip()) else None,
    lambda s: (lambda m: m.group(2) + "+" + m.group(1))(re.fullmatch(r"([a-z0-9^]+)\+([a-z0-9^]+)", s.strip())) if re.fullmatch(r"([a-z0-9^]+)\+([a-z0-9^]+)", s.strip()) else None,
    lambda s: re.sub(r"\\sqrt\{(\d)\}", r"\\sqrt \1", s) if re.search(r"\\sqrt\{\d\}", s) else None,
]


def perturb(s: str, rng: np.random.Generator, rewrites=None) -> str:
    rewrites = REWRITES if rewrites is None else rewrites
    order = rng.permutation(len(rewrites))
    for k in order:
        r = rewrites[k](s)
        if r is not None and r != s:
            return r
    return s


# ---------------------------------------------------------------- per-problem worker
def work(args):
    pid, samples, oracle, seed = args
    rng = np.random.default_rng(seed)
    ans = [extract_boxed(t) for t in samples]
    ids = cluster_mv(ans)
    ids_plain = cluster_plain(ans)
    sc = sc_from_ids(ids)
    sc_plain = sc_from_ids(ids_plain)
    # P1: perturb each answer, re-cluster both ways
    pans = [perturb(a, rng) if a else a for a in ans]
    sc_mv_pert = sc_from_ids(cluster_mv(pans))
    sc_plain_pert = sc_from_ids(cluster_plain(pans))
    pans2 = [perturb(a, rng, REWRITES_HELD) if a else a for a in ans]
    sc_mv_pert2 = sc_from_ids(cluster_mv(pans2))
    sc_plain_pert2 = sc_from_ids(cluster_plain(pans2))
    # P2: random halves
    perm = rng.permutation(N)
    ha, hb = perm[: N // 2], perm[N // 2:]
    scp_a = scp_from_ids(ids[ha])
    scp_b = scp_from_ids(ids[hb])

    def plurality(h):
        v = ids[h]
        v = v[v >= 0]
        return int(np.bincount(v).argmax()) if len(v) else -2

    pa_, pb_ = plurality(ha), plurality(hb)
    plur_agree = pa_ == pb_ and pa_ >= 0
    # item-level split-half SC: agreement with half A (excl. self) vs half B (excl. self)
    sc_a = np.zeros(N)
    sc_b = np.zeros(N)
    for i in range(N):
        if ids[i] < 0:
            continue
        ra = [j for j in ha if j != i]
        rb = [j for j in hb if j != i]
        sc_a[i] = np.mean(ids[ra] == ids[i])
        sc_b[i] = np.mean(ids[rb] == ids[i])
    # P3: SC with n_ref random reference samples, 20 repeats
    eq = (ids[:, None] == ids[None, :]) & (ids[:, None] >= 0)
    np.fill_diagonal(eq, False)
    sc_n = {}
    for n_ref in (4, 8, 16, 32, 63):
        reps = []
        for _ in range(20):
            r = rng.random((N, N))
            np.fill_diagonal(r, 2.0)
            pick = np.argsort(r, axis=1)[:, :n_ref]
            reps.append(np.take_along_axis(eq, pick, axis=1).mean(axis=1))
        sc_n[n_ref] = np.array(reps)  # (20, 64)
    return dict(pid=pid, ids=ids, sc=sc, sc_plain=sc_plain, sc_mv_pert=sc_mv_pert,
                sc_plain_pert=sc_plain_pert, sc_mv_pert2=sc_mv_pert2, sc_plain_pert2=sc_plain_pert2, scp=scp_from_ids(ids), scp_a=scp_a, scp_b=scp_b,
                plur_agree=plur_agree, sc_a=sc_a, sc_b=sc_b, sc_n=sc_n,
                n_missing=int(np.sum(ids < 0)),
                keys={a: _KEY_CACHE[a] for a in set(ans) | set(pans) | set(pans2) if a})


# ---------------------------------------------------------------- stats helpers
def auroc(score: np.ndarray, y: np.ndarray) -> float:
    pos = y == 1
    n1, n0 = pos.sum(), (~pos).sum()
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = rankdata(score)
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def pooled_auroc(S: np.ndarray, Y: np.ndarray) -> float:
    return auroc(S.ravel(), Y.ravel())


def within_auroc(S: np.ndarray, Y: np.ndarray) -> np.ndarray:
    return np.array([auroc(S[p], Y[p]) for p in range(len(S))])


def sel_acc(S: np.ndarray, Y: np.ndarray) -> np.ndarray:
    # argmax score, ties -> lowest index (np.argmax returns first max)
    return np.array([Y[p, np.argmax(S[p])] for p in range(len(S))], dtype=float)


def boot_ci(x: np.ndarray, rng, nb=BOOT):
    x = x[~np.isnan(x)]
    idx = rng.integers(0, len(x), size=(nb, len(x)))
    m = x[idx].mean(axis=1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def boot_diff(a: np.ndarray, b: np.ndarray, rng, nb=BOOT):
    ok = ~(np.isnan(a) | np.isnan(b))
    d = (a - b)[ok]
    idx = rng.integers(0, len(d), size=(nb, len(d)))
    m = d[idx].mean(axis=1)
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def pass_at_k(n, c, k):
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


# ---------------------------------------------------------------- main
def main():
    rng = np.random.default_rng(SEED)
    G = [json.loads(l) for l in open(RUNS / "bon/bon_math__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
    pid_index = {g["problem_id"]: i for i, g in enumerate(G)}
    jobs = [(g["problem_id"], g["samples"], np.array(g["oracle"]), SEED + i) for i, g in enumerate(G)]
    with Pool(4) as pool:
        R = pool.map(work, jobs, chunksize=8)
    Y = np.array([g["oracle"] for g in G])  # (500, 64)
    level = np.array([g["level"] for g in G])
    SC = np.stack([r["sc"] for r in R])
    SCP = np.array([r["scp"] for r in R])
    res: dict = {"matcher": MATCHER, "parse_timeout_s": PARSE_TIMEOUT, "seed": SEED, "n_problems": len(G), "n_samples": N}
    res["data_quality"] = {
        "samples_without_box_share": float(np.mean([r["n_missing"] for r in R]) / N),
        "gold_pass_at_1_mean": float(Y.mean()),
        "problems_both_classes": int(sum(0 < y.sum() < N for y in Y)),
    }

    # judges
    J = {}
    jdir = RUNS / "bon_scores_llama"
    for size in ("1.5B", "3B", "7B", "14B"):
        for mode in ("noref", "ref"):
            reps = {}
            for rep in ("a", "b"):
                f = jdir / f"math__Qwen__Qwen2.5-{size}-Instruct__{mode}_{rep}.jsonl"
                reps[rep] = {json.loads(l)["problem_id"]: np.array(json.loads(l)["escore"]) for l in open(f)}
            J[(size, mode)] = reps
    sub = sorted(J[("14B", "noref")]["a"].keys(), key=lambda p: pid_index[p])
    sub_idx = np.array([pid_index[p] for p in sub])
    res["n_judge_subset"] = len(sub)
    Ysub, SCsub = Y[sub_idx], SC[sub_idx]
    jscore = {}
    for (size, mode), reps in J.items():
        jscore[(size, mode)] = np.stack([(reps["a"][p] + reps["b"][p]) / 2 for p in sub])
    # alignment control
    ctrl = pooled_auroc(jscore[("14B", "ref")], Ysub)
    res["alignment_control_14B_ref_pooled_auroc"] = ctrl
    res["alignment_control_pass"] = bool(ctrl >= 0.85)

    # E1 / E2 on judge subset
    names = {"SC (M)": SCsub}
    for (size, mode), s in jscore.items():
        names[f"Qwen-{size} {mode}"] = s
    E1, E2 = {}, {}
    w = {k: within_auroc(v, Ysub) for k, v in names.items()}
    a = {k: sel_acc(v, Ysub) for k, v in names.items()}
    for k in names:
        E1[k] = dict(zip(("mean", "lo", "hi"), boot_ci(w[k], rng)))
        E1[k]["pooled_auroc"] = pooled_auroc(names[k], Ysub)
        E2[k] = dict(zip(("mean", "lo", "hi"), boot_ci(a[k], rng)))
    passk = {k: float(np.mean([pass_at_k(N, int(y.sum()), k) for y in Ysub])) for k in (1, 4, 16, 64)}
    passk_all = {k: float(np.mean([pass_at_k(N, int(y.sum()), k) for y in Y])) for k in (1, 4, 16, 64)}
    res["E1_within_problem_auroc"] = E1
    res["E2_selection_accuracy"] = E2
    res["pass_at_k_subset176"] = passk
    res["pass_at_k_all500"] = passk_all
    noref = [k for k in names if k.endswith("noref")]
    best_noref = max(noref, key=lambda k: E1[k]["mean"])
    best_noref_sel = max(noref, key=lambda k: E2[k]["mean"])
    res["best_noref_by_auroc"] = best_noref
    res["best_noref_by_selection"] = best_noref_sel
    res["E1_SC_minus_best_noref"] = dict(zip(("mean", "lo", "hi"), boot_diff(w["SC (M)"], w[best_noref], rng)))
    res["E2_SC_minus_best_noref_sel"] = dict(zip(("mean", "lo", "hi"), boot_diff(a["SC (M)"], a[best_noref_sel], rng)))
    # SC on all 500 (E1 for SC only)
    w_all = within_auroc(SC, Y)
    res["E1_SC_all500_within"] = dict(zip(("mean", "lo", "hi"), boot_ci(w_all, rng)))
    res["E1_SC_all500_pooled"] = pooled_auroc(SC, Y)
    res["E2_SC_all500_selection"] = dict(zip(("mean", "lo", "hi"), boot_ci(sel_acc(SC, Y), rng)))

    # E3
    pass1 = Y.mean(axis=1)
    res["E3_spearman_scp_pass1_all"] = float(spearmanr(SCP, pass1).statistic)
    res["E3_by_level"] = {int(L): dict(n=int((level == L).sum()),
                                       rho=float(spearmanr(SCP[level == L], pass1[level == L]).statistic),
                                       mean_pass1=float(pass1[level == L].mean()),
                                       mean_scp=float(SCP[level == L].mean())) for L in sorted(set(level))}

    # P1
    P1 = {}
    for nm, o, p in (("Math-Verify matcher", "sc", "sc_mv_pert"), ("plain string matcher", "sc_plain", "sc_plain_pert"),
                     ("P1b held-out rewrites, Math-Verify matcher", "sc", "sc_mv_pert2"),
                     ("P1b held-out rewrites, plain string matcher", "sc_plain", "sc_plain_pert2")):
        A = np.stack([r[o] for r in R]).ravel()
        B = np.stack([r[p] for r in R]).ravel()
        P1[nm] = dict(mean_abs_delta=float(np.mean(np.abs(A - B))), spearman=float(spearmanr(A, B).statistic))
        P1[nm]["pass"] = bool(P1[nm]["mean_abs_delta"] < 0.01 and P1[nm]["spearman"] >= 0.99)
    res["P1_surface_invariance"] = P1

    # P2
    sa = np.array([r["scp_a"] for r in R])
    sb = np.array([r["scp_b"] for r in R])
    P2 = dict(scp_half_spearman=float(spearmanr(sa, sb).statistic),
              plurality_agree=float(np.mean([r["plur_agree"] for r in R])),
              item_sc_half_spearman=float(spearmanr(np.stack([r["sc_a"] for r in R]).ravel(),
                                                    np.stack([r["sc_b"] for r in R]).ravel()).statistic))
    reps_ab = {}
    for (size, mode), reps in J.items():
        x = np.concatenate([reps["a"][p] for p in sub])
        y = np.concatenate([reps["b"][p] for p in sub])
        reps_ab[f"Qwen-{size} {mode}"] = float(spearmanr(x, y).statistic)
    P2["judge_replica_a_vs_b_item_spearman"] = reps_ab
    P2["pass"] = bool(P2["scp_half_spearman"] >= 0.90 and P2["plurality_agree"] >= 0.90)
    res["P2_repeat_stability"] = P2

    # P3
    P3 = {}
    for n_ref in (4, 8, 16, 32, 63):
        arr = np.stack([r["sc_n"][n_ref] for r in R])  # (500, 20, 64)
        vals = []
        for rep in range(20):
            wa = within_auroc(arr[:, rep, :], Y)
            vals.append(float(np.nanmean(wa)))
        P3[str(n_ref)] = float(np.mean(vals))
    ks = [str(k) for k in (4, 8, 16, 32, 63)]
    steps = [P3[ks[i + 1]] - P3[ks[i]] for i in range(len(ks) - 1)]
    res["P3_monotone_in_evidence"] = dict(within_auroc_by_n_ref=P3, steps=steps,
                                          **{"pass": bool(all(s >= -0.01 for s in steps))})

    # P4: corrupt one answer with another problem's plurality answer
    plur = []
    for g, r in zip(G, R):
        ans = [extract_boxed(t) for t in g["samples"]]
        v = r["ids"]
        vv = v[v >= 0]
        k = int(np.bincount(vv).argmax()) if len(vv) else -1
        plur.append(ans[int(np.where(v == k)[0][0])] if k >= 0 else None)
    p4_total = p4_drop = 0
    for pi, (g, r) in enumerate(zip(G, R)):
        ans = [extract_boxed(t) for t in g["samples"]]
        ids = r["ids"]
        cand = [i for i in range(N) if r["sc"][i] > 0]
        if not cand:
            continue
        s = cand[int(rng.integers(len(cand)))]
        for _ in range(20):
            q = int(rng.integers(len(G)))
            if q == pi or not plur[q]:
                continue
            new_ids = cluster_mv(ans[:s] + [plur[q]] + ans[s + 1:])
            matches = int(np.sum(new_ids == new_ids[s])) - 1 if new_ids[s] >= 0 else 0
            if matches == 0:
                p4_total += 1
                p4_drop += 1  # corrupted SC is 0 < original SC (> 0)
                break
            # the chance answer matched an existing cluster: it is not a wrong answer, resample
    res["P4_bug_detection"] = dict(items_tested=p4_total, share_scored_below_original=(p4_drop / max(p4_total, 1)),
                                   note="near-tautological by construction; resampled when the injected answer was equivalent to a sample answer",
                                   **{"pass": bool(p4_total > 0 and p4_drop / p4_total >= 0.95)})

    # P5
    sel_ok = sel_acc(SC, Y)
    P5 = {}
    for thr in (0.3, 0.5, 0.7, 0.9):
        m = SCP >= thr
        P5[str(thr)] = dict(coverage=float(m.mean()), precision=float(sel_ok[m].mean()) if m.any() else None,
                            n_problems=int(m.sum()))
    res["P5_confident_wrongness"] = dict(by_threshold=P5, **{"pass": bool(P5["0.5"]["precision"] is not None and P5["0.5"]["precision"] >= 0.90)})
    P5L = {}
    for L in sorted(set(level)):
        m = (SCP >= 0.5) & (level == L)
        P5L[int(L)] = dict(n_confident=int(m.sum()), precision=float(sel_ok[m].mean()) if m.any() else None,
                           share_of_level=float(m.sum() / (level == L).sum()))
    res["P5_by_level_at_scp_0_5"] = P5L
    # ECE of SC as P(correct) (item level, all 500)
    bins = np.minimum((SC.ravel() * 10).astype(int), 9)
    yv = Y.ravel()
    sv = SC.ravel()
    ece = 0.0
    cal = []
    for b in range(10):
        m = bins == b
        if m.any():
            cal.append((float(sv[m].mean()), float(yv[m].mean()), int(m.sum())))
            ece += m.mean() * abs(sv[m].mean() - yv[m].mean())
    res["P5_ece_item_level"] = float(ece)
    res["P5_calibration_bins"] = cal
    # item-level Spearman SC vs gold bit, pooled
    res["pooled_spearman_sc_vs_gold_bit"] = float(spearmanr(SC.ravel(), Y.ravel()).statistic)

    # key table for deterministic re-runs and parse-failure share
    allkeys = {}
    for r in R:
        allkeys.update(r["keys"])
    json.dump(allkeys, open(OUT / "answer_keys.json", "w"), indent=0, sort_keys=True)
    res["answer_key_table"] = dict(unique_strings=len(allkeys),
                                   fallback_to_plain_string_share=float(np.mean([v.startswith("S:") for v in allkeys.values()])))

    # EXPLORATORY (not in PREREG; added after run 1 to explain results; labelled as such)
    IDS = np.stack([r["ids"] for r in R])
    boxed = IDS >= 0
    ex = {}
    sub_boxed = boxed[sub_idx]
    def within_masked(S, Yv, M):
        out = []
        for p in range(len(S)):
            m = M[p]
            out.append(auroc(S[p][m], Yv[p][m]) if m.sum() > 1 else float("nan"))
        return np.array(out)
    ex["has_box_only_scorer_within_auroc_subset176"] = float(np.nanmean(within_auroc(sub_boxed.astype(float), Ysub)))
    ex["boxed_only_within_auroc_subset176"] = {k: dict(zip(("mean", "lo", "hi"), boot_ci(within_masked(v, Ysub, sub_boxed), rng)))
                                               for k, v in names.items()}
    ex["boxed_only_within_auroc_all500_SC"] = dict(zip(("mean", "lo", "hi"), boot_ci(within_masked(SC, Y, boxed), rng)))
    ex["share_samples_boxed_among_wrong"] = float(boxed[Y == 0].mean())
    ex["share_samples_boxed_among_correct"] = float(boxed[Y == 1].mean())
    conf = SCP >= 0.5
    ex["plurality_agree_halves_when_scp_ge_0_5"] = float(np.mean([r["plur_agree"] for r, c in zip(R, conf) if c]))
    ex["plurality_agree_halves_when_scp_lt_0_5"] = float(np.mean([r["plur_agree"] for r, c in zip(R, conf) if not c]))
    ex["plurality_ties_share"] = float(np.mean([np.sort(np.bincount(r["ids"][r["ids"] >= 0]))[-2:].tolist()[0] == np.bincount(r["ids"][r["ids"] >= 0]).max()
                                                 if (r["ids"] >= 0).sum() > 1 and len(np.bincount(r["ids"][r["ids"] >= 0])) > 1 else False for r in R]))
    res["EXPLORATORY_post_hoc"] = ex

    # verdict (PREREG decision rule)
    d1, d2 = res["E1_SC_minus_best_noref"], res["E2_SC_minus_best_noref_sel"]
    props = res["P1_surface_invariance"]["Math-Verify matcher"]["pass"] and res["P2_repeat_stability"]["pass"] \
        and res["P3_monotone_in_evidence"]["pass"]
    p5 = res["P5_confident_wrongness"]["pass"]
    if not res["alignment_control_pass"]:
        verdict = "J files not aligned: judge comparison dropped"
    elif d1["lo"] > -0.02 and d2["mean"] >= 0 and props and p5:
        verdict = "YES"
    elif d1["lo"] > -0.02 and d2["mean"] >= 0 and props and not p5:
        verdict = "YES with a stated abstention region (P5 failed)"
    elif d1["mean"] < -0.05 or not props:
        verdict = "NO"
    else:
        verdict = "INCONCLUSIVE"
    res["verdict_per_prereg"] = verdict

    json.dump(res, open(OUT / "results.json", "w"), indent=1, default=float)
    write_tables(res)
    make_figs(res, SC, Y)
    print(json.dumps({k: res[k] for k in ("verdict_per_prereg", "alignment_control_14B_ref_pooled_auroc",
                                           "E1_SC_minus_best_noref", "E2_SC_minus_best_noref_sel")}, indent=1))


def write_tables(r):
    L = []
    L.append("## E1 within-problem AUROC vs the gold bit (176-problem judge subset, 95% CI over problems)\n")
    L.append("| scorer | needs gold | needs judge | AUROC | 95% CI | pooled AUROC |\n|---|---|---|---|---|---|")
    for k, v in r["E1_within_problem_auroc"].items():
        gold = "yes" if k.endswith(" ref") else "no"
        judge = "no" if k.startswith("SC") else "yes"
        L.append(f"| {k} | {gold} | {judge} | {v['mean']:.3f} | [{v['lo']:.3f}, {v['hi']:.3f}] | {v['pooled_auroc']:.3f} |")
    L.append("\n## E2 selection accuracy (argmax score; 176 problems)\n")
    L.append("| scorer | accuracy | 95% CI |\n|---|---|---|")
    for k, v in r["E2_selection_accuracy"].items():
        L.append(f"| {k} | {v['mean']:.3f} | [{v['lo']:.3f}, {v['hi']:.3f}] |")
    pk = r["pass_at_k_subset176"]
    L.append(f"| mean pass@1 (random sample) | {pk[1]:.3f} | |")
    L.append(f"| pass@4 / pass@16 / pass@64 (oracle) | {pk[4]:.3f} / {pk[16]:.3f} / {pk[64]:.3f} | |")
    (OUT / "tables.md").write_text("\n".join(L) + "\n")


def make_figs(r, SC, Y):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 4.5))
    cal = r["P5_calibration_bins"]
    ax.plot([c[0] for c in cal], [c[1] for c in cal], "o-", label="SC (all 500 problems)")
    ax.plot([0, 1], [0, 1], "k--", label="perfect")
    ax.set_xlabel("SC score (agreement with other samples)")
    ax.set_ylabel("share correct vs gold")
    ax.grid(True)
    ax.legend()
    ax.set_title("SC as probability of correct")
    fig.tight_layout()
    fig.savefig(OUT / "calibration.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ks = list(r["E1_within_problem_auroc"].keys())
    ms = [r["E1_within_problem_auroc"][k]["mean"] for k in ks]
    err = [[r["E1_within_problem_auroc"][k]["mean"] - r["E1_within_problem_auroc"][k]["lo"] for k in ks],
           [r["E1_within_problem_auroc"][k]["hi"] - r["E1_within_problem_auroc"][k]["mean"] for k in ks]]
    ax.barh(range(len(ks)), ms, xerr=err)
    ax.set_yticks(range(len(ks)))
    ax.set_yticklabels(ks)
    ax.axvline(0.5, color="k", ls=":")
    ax.set_xlabel("within-problem AUROC vs gold correctness")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(OUT / "auroc.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
