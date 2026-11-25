#!/usr/bin/env python3
"""Experiment 04 analysis: format-robust SC (fallback extraction) vs gold pass@1, 6 old models (Part A) and old + new models (Part B).

Implements PREREG.md. CPU only, no model calls. Reuses experiment 03's matcher (scripts/analyze.py there).
    ~/.venvs/jfe/bin/python experiments/04_format_robust_sc_and_more_models/scripts/analyze.py
Writes results/results.json, results/tables.md, results/model_rank.png.
"""
from __future__ import annotations
import importlib.util, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from scipy.stats import kendalltau, spearmanr

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parent.parent
OUT = EXP / "results"; GEN = OUT / "gen"
EXP03 = REPO / "experiments/03_model_level_ranking_sc"

def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); sys.modules[name] = m; s.loader.exec_module(m); return m
sys.argv = [sys.argv[0]]  # exp 03's module reads --quick from argv
a03 = _load("a03", EXP03 / "scripts/analyze.py")
fr = _load("fr_extract", HERE / "fr_extract.py")

N, BOOT, SEED = 16, 2000, 20261126
NEW = [
    ("qwen3_8b", "Qwen3-8B (non-thinking)", GEN / "bon_math__Qwen__Qwen3-8B.jsonl"),
    ("qwen35_4b", "Qwen3.5-4B (non-thinking)", GEN / "bon_math__Qwen__Qwen3.5-4B.jsonl"),
    ("llama3_8b", "Llama-3-8B-Instruct", GEN / "bon_math__meta-llama__Meta-Llama-3-8B-Instruct.jsonl"),
    ("dsmath_7b_inst", "DeepSeek-Math-7B-Instruct", GEN / "bon_math__deepseek-ai__deepseek-math-7b-instruct.jsonl"),
]
OLD = [m[0] for m in a03.MODELS]
MODELS = list(a03.MODELS) + NEW
VARIANTS = ["strict", "fr", "fr_stop", "fr12"]


def answer(text, finish, variant):
    """(answer or None, tier) of one sample under a variant."""
    if variant == "strict":
        b = fr.extract_boxed(text); return (b, "boxed") if b else (None, "none")
    a, t = fr.fr_answer(text)
    if variant == "fr_stop" and t != "boxed" and finish == "length":
        return None, "none"
    if variant == "fr12" and t in ("math", "number"):
        return None, "none"
    return a, t


def kD(a, b): return a03.kendall_D(a, b)
def ktau(a, b): return a03.tau(a, b)


def verdict_A(D, maxgap, pD3):
    if D >= 4 or maxgap >= 0.10: return "NO"
    if D <= 2 and maxgap < 0.05 and pD3 >= 0.80: return "YES"
    return "INCONCLUSIVE"


def verdict_B(t, maxgap, pt):
    if t < 0.60 or maxgap >= 0.10: return "NO"
    if t >= 0.80 and maxgap < 0.05 and pt >= 0.80: return "YES"
    return "INCONCLUSIVE"


def main():
    t0 = time.time()
    tasks = [json.loads(l) for l in open(REPO / "experiments/tfa-vs-judge/runs/bon_math_tasks.jsonl")]
    pids = [t["problem_id"] for t in tasks]; gold = {t["problem_id"]: t["answer"] for t in tasks}; P = len(pids)
    data, missing = {}, []
    for mid, label, path in MODELS:
        if not Path(path).exists():
            missing.append(mid); continue
        rows = {}
        for l in open(path):
            r = json.loads(l); rows[r["problem_id"]] = r
        if len(rows) < P:
            missing.append(f"{mid} (only {len(rows)} problems)"); continue
        data[mid] = dict(label=label, samples=[rows[p]["samples"][:N] for p in pids],
                         finish=[(rows[p].get("finish") or ["stop"] * N)[:N] for p in pids])
    mids = [m for m in (x[0] for x in MODELS) if m in data]
    print("models", mids, "missing", missing, flush=True)

    # answers per variant
    ans = {v: {m: [[answer(s, f, v) for s, f in zip(data[m]["samples"][pi], data[m]["finish"][pi])] for pi in range(P)] for m in mids} for v in VARIANTS}

    # caches (seeded from experiment 03's)
    kp, gp = OUT / "key_cache.json", OUT / "gold_cache.json"
    kc = json.load(open(kp)) if kp.exists() else json.load(open(EXP03 / "results/key_cache.json"))
    gc = json.load(open(gp)) if gp.exists() else json.load(open(EXP03 / "results/gold_cache.json"))
    allans = {(pi, a) for v in VARIANTS for m in mids for pi in range(P) for a, t in ans[v][m][pi] if a}
    kneed = sorted({(mode, a) for _, a in allans for mode in ("norm", "raw") if f"{mode}\x00{a}" not in kc})
    gneed = sorted({(pids[pi], a) for pi, a in allans if f"{pids[pi]}\x00{a}" not in gc})
    print("keys", len(kneed), "gold", len(gneed), flush=True)
    with Pool(4) as pool:
        if kneed:
            for (mode, a), k in zip(kneed, pool.map(a03._key_job, kneed, chunksize=200)): kc[f"{mode}\x00{a}"] = k
        if gneed:
            for (p, a), v in zip(gneed, pool.map(a03._gold_job, [(gold[p], a) for p, a in gneed], chunksize=200)): gc[f"{p}\x00{a}"] = v
    json.dump(kc, open(kp, "w")); json.dump(gc, open(gp, "w"))
    print(f"caches {time.time()-t0:.0f}s", flush=True)

    def per_problem(v, m, mode="norm", n=N):
        sc, p1, nb = np.zeros(P), np.zeros(P), np.zeros(P)
        for pi in range(P):
            row = ans[v][m][pi][:n]
            keys = [kc[f"{mode}\x00{a}"] if a else None for a, t in row]
            sc[pi] = a03.problem_sc(a03.clusters(keys))
            p1[pi] = np.mean([gc[f"{pids[pi]}\x00{a}"] if a else 0 for a, t in row])
            nb[pi] = np.mean([1.0 if t == "boxed" else 0.0 for a, t in row])
        return sc, p1, nb

    PP = {}  # (variant, mode, n) -> m -> (sc, p1, boxed)
    for key in [(v, "norm", N) for v in VARIANTS] + [("fr", "raw", N), ("strict", "raw", N), ("fr", "norm", 8), ("strict", "norm", 8)]:
        PP[key] = {m: per_problem(key[0], m, key[1], key[2]) for m in mids}
    print(f"per-problem {time.time()-t0:.0f}s", flush=True)

    R = dict(models=mids, labels={m: data[m]["label"] for m in mids}, missing=missing, n=N)
    # model-level table
    tab = {}
    for m in mids:
        s_sc, s_p1, s_nb = PP[("strict", "norm", N)][m]; f_sc, f_p1, _ = PP[("fr", "norm", N)][m]
        tiers = {t: float(np.mean([t2 == t for row in ans["fr"][m] for a, t2 in row])) for t in ("boxed", "phrase", "math", "number", "none")}
        trunc = float(np.mean([f == "length" for row in data[m]["finish"] for f in row]))
        tab[m] = dict(sc_strict=float(s_sc.mean()), sc_fr=float(f_sc.mean()), p1_strict=float(s_p1.mean()), p1_fr=float(f_p1.mean()),
                      boxed_rate=float(s_nb.mean()), tiers=tiers, truncated=trunc,
                      sc_fr_stop=float(PP[("fr_stop", "norm", N)][m][0].mean()), p1_fr_stop=float(PP[("fr_stop", "norm", N)][m][1].mean()),
                      sc_fr12=float(PP[("fr12", "norm", N)][m][0].mean()), p1_fr12=float(PP[("fr12", "norm", N)][m][1].mean()),
                      sc_fr_raw=float(PP[("fr", "raw", N)][m][0].mean()))
    R["table"] = tab

    rng = np.random.default_rng(SEED)
    idxs = [rng.integers(0, P, P) for _ in range(BOOT)]

    def rank_block(group, cand, target, rule):
        """cand/target = (variant, mode, n, index 0=sc/1=p1). Returns dict of D, tau, spearman, boot, discordant pairs, verdict."""
        g = [m for m in group if m in mids]
        c = np.array([PP[cand[:3]][m][cand[3]] for m in g]); t = np.array([PP[target[:3]][m][target[3]] for m in g])
        cm, tm = c.mean(1), t.mean(1)
        D = kD(cm, tm); tv = ktau(cm, tm); pairs = []
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                if (cm[i] - cm[j]) * (tm[i] - tm[j]) < 0:
                    pairs.append(dict(a=g[i], b=g[j], gap=float(abs(tm[i] - tm[j])), cand_gap=float(abs(cm[i] - cm[j]))))
        Ds, Ts = [], []
        for idx in idxs:
            cb, tb = c[:, idx].mean(1), t[:, idx].mean(1); Ds.append(kD(cb, tb)); Ts.append(ktau(cb, tb))
        Ds, Ts = np.array(Ds), np.array(Ts)
        maxgap = max([p["gap"] for p in pairs], default=0.0)
        pD3, pt = float(np.mean(Ds <= 3)), float(np.mean(Ts >= 0.733))
        v = verdict_A(D, maxgap, pD3) if rule == "A" else verdict_B(tv, maxgap, pt)
        return dict(M=len(g), pairs_total=len(g) * (len(g) - 1) // 2, D=D, tau=tv, spearman=float(spearmanr(cm, tm)[0]), boot_P_D_le_3=pD3,
                    boot_P_tau_ge_0733=pt, tau_ci=[float(np.percentile(Ts, 2.5)), float(np.percentile(Ts, 97.5))], discordant=pairs,
                    max_discordant_gap=maxgap, verdict=v)

    V = lambda v, mode="norm", n=N: (v, mode, n)
    R["A"] = {
        "primary_scfr_vs_p1fr": rank_block(OLD, V("fr") + (0,), V("fr") + (1,), "A"),
        "scfr_vs_p1strict": rank_block(OLD, V("fr") + (0,), V("strict") + (1,), "A"),
        "scstrict_vs_p1fr": rank_block(OLD, V("strict") + (0,), V("fr") + (1,), "A"),
        "scstrict_vs_p1strict (exp 03)": rank_block(OLD, V("strict") + (0,), V("strict") + (1,), "A"),
        "S1_fr_stop": rank_block(OLD, V("fr_stop") + (0,), V("fr_stop") + (1,), "A"),
        "S2_fr12": rank_block(OLD, V("fr12") + (0,), V("fr12") + (1,), "A"),
        "S3_raw_keys": rank_block(OLD, V("fr", "raw") + (0,), V("fr") + (1,), "A"),
        "S4_n8": rank_block(OLD, V("fr", "norm", 8) + (0,), V("fr") + (1,), "A"),
    }
    R["B"] = {
        "primary_scfr_vs_p1fr": rank_block(mids, V("fr") + (0,), V("fr") + (1,), "B"),
        "scfr_vs_p1strict": rank_block(mids, V("fr") + (0,), V("strict") + (1,), "B"),
        "scstrict_vs_p1strict": rank_block(mids, V("strict") + (0,), V("strict") + (1,), "B"),
        "S1_fr_stop": rank_block(mids, V("fr_stop") + (0,), V("fr_stop") + (1,), "B"),
        "S2_fr12": rank_block(mids, V("fr12") + (0,), V("fr12") + (1,), "B"),
    }
    # flip: DeepSeek-Math-RL vs Mistral
    flip = {}
    a, b = "dsmath_7b_rl", "mistral_7b"
    for name, cand, target in [("sc_fr_vs_p1_fr", V("fr") + (0,), V("fr") + (1,)), ("sc_fr_vs_p1_strict", V("fr") + (0,), V("strict") + (1,)),
                                ("sc_strict_vs_p1_strict (exp 03)", V("strict") + (0,), V("strict") + (1,))]:
        c, t = PP[cand[:3]], PP[target[:3]]
        cd = np.array([c[a][cand[3]][i] - c[b][cand[3]][i] for i in idxs]); td = np.array([t[a][target[3]][i] - t[b][target[3]][i] for i in idxs])
        cdm = c[a][cand[3]].mean() - c[b][cand[3]].mean(); tdm = t[a][target[3]].mean() - t[b][target[3]].mean()
        flip[name] = dict(sc_diff=float(cdm), p1_diff=float(tdm), concordant=bool(cdm * tdm > 0), boot_P_concordant=float(np.mean(cd.mean(1) * td.mean(1) > 0)) if False else float(np.mean(np.array([c[a][cand[3]][i].mean() - c[b][cand[3]][i].mean() for i in idxs]) * np.array([t[a][target[3]][i].mean() - t[b][target[3]][i].mean() for i in idxs]) > 0)))
    R["flip_dsmath_vs_mistral"] = flip
    # close pairs
    def close(group):
        g = [m for m in group if m in mids]; t = {m: tab[m]["p1_fr"] for m in g}; s = {m: tab[m]["sc_fr"] for m in g}; out = []
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                gp_ = abs(t[g[i]] - t[g[j]])
                if gp_ < 0.05: out.append(dict(a=g[i], b=g[j], gap=float(gp_), concordant=bool((t[g[i]] - t[g[j]]) * (s[g[i]] - s[g[j]]) > 0)))
        return out
    R["close_pairs_old"], R["close_pairs_all"] = close(OLD), close(mids)
    # gap placement of new models (by pass@1_fr and strict)
    old_sorted = sorted(((tab[m]["p1_strict"], m) for m in OLD if m in mids), reverse=True)
    place = {}
    for m in mids:
        if m in OLD: continue
        x = tab[m]["p1_strict"]; hi = [o for o in old_sorted if o[0] >= x]; lo = [o for o in old_sorted if o[0] < x]
        up, dn = (hi[-1] if hi else None), (lo[0] if lo else None)
        place[m] = dict(p1_strict=x, above=up[1] if up else None, below=dn[1] if dn else None,
                        inside_gap_ge_005=bool(up and dn and up[0] - dn[0] >= 0.05))
    R["placement"] = place
    json.dump(R, open(OUT / "results.json", "w"), indent=1)
    write_tables(R); make_fig(R)
    print(f"done {time.time()-t0:.0f}s")


def write_tables(R):
    T, L, o = R["table"], R["labels"], []
    o += ["# Experiment 04 tables (generated by scripts/analyze.py)", "", "n = 16 samples x 500 MATH-500 problems per model.", "",
          "| model | pass@1 strict | pass@1 fr | SC strict | SC fr | boxed | phrase | math | number | none | truncated |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in sorted(R["models"], key=lambda m: -T[m]["p1_fr"]):
        t = T[m]; ti = t["tiers"]
        o.append(f"| {L[m]} | {t['p1_strict']:.3f} | {t['p1_fr']:.3f} | {t['sc_strict']:.3f} | {t['sc_fr']:.3f} | {ti['boxed']:.2f} | {ti['phrase']:.2f} | {ti['math']:.2f} | {ti['number']:.2f} | {ti['none']:.2f} | {t['truncated']:.2f} |")
    for part in ("A", "B"):
        o += ["", f"## Part {part}: SC vs pass@1 ranking", "", "| comparison | M | D | tau | Spearman | boot P(D<=3) | boot P(tau>=0.733) | max discordant gap | verdict |", "|---|---|---|---|---|---|---|---|---|"]
        for k, r in R[part].items():
            o.append(f"| {k} | {r['M']} | {r['D']}/{r['pairs_total']} | {r['tau']:.3f} | {r['spearman']:.3f} | {r['boot_P_D_le_3']:.2f} | {r['boot_P_tau_ge_0733']:.2f} | {r['max_discordant_gap']:.3f} | {r['verdict']} |")
        r = R[part]["primary_scfr_vs_p1fr"]
        o.append(""); o.append("Discordant pairs (primary): " + (", ".join(f"{L[p['a']]} vs {L[p['b']]} (gap {p['gap']:.3f}, SC gap {p['cand_gap']:.3f})" for p in r["discordant"]) or "none"))
    o += ["", "## DeepSeek-Math-7B-RL vs Mistral-7B: concordant?", "", "| comparison | SC diff (DS - Mistral) | pass@1 diff | concordant | boot P(concordant) |", "|---|---|---|---|---|"]
    for k, f in R["flip_dsmath_vs_mistral"].items():
        o.append(f"| {k} | {f['sc_diff']:+.4f} | {f['p1_diff']:+.4f} | {f['concordant']} | {f['boot_P_concordant']:.2f} |")
    o += ["", "## Placement of new models (pass@1 strict)", ""]
    for m, p in R["placement"].items():
        o.append(f"- {L[m]}: pass@1 {p['p1_strict']:.3f}, between {L.get(p['below'], '-')} and {L.get(p['above'], '-')}; inside a gap of >=0.05: {p['inside_gap_ge_005']}")
    o += ["", f"Close pairs (pass@1 fr gap < 0.05): old {len(R['close_pairs_old'])}, all {len(R['close_pairs_all'])}; concordant in all: {sum(c['concordant'] for c in R['close_pairs_all'])}/{len(R['close_pairs_all'])}"]
    for c in R["close_pairs_all"]:
        o.append(f"- {L[c['a']]} vs {L[c['b']]}: gap {c['gap']:.3f}, concordant {c['concordant']}")
    (OUT / "tables.md").write_text("\n".join(o) + "\n")


def make_fig(R):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    T, L = R["table"], R["labels"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for k, (key, name) in enumerate([("sc_strict", "SC strict (boxed only)"), ("sc_fr", "SC format-robust")]):
        for m in R["models"]:
            x, y = T[m]["p1_fr"], T[m][key]
            ax[k].scatter(x, y, color="C0" if m in {a for a in R["models"] if a in [n[0] for n in []]} else ("C1" if m not in R["placement"] else "C3"))
            ax[k].annotate(L[m].split(" ")[0], (x, y), fontsize=7)
        ax[k].set_xlabel("gold pass@1 (format-robust)"); ax[k].set_ylabel(name); ax[k].grid(True)
        ax[k].set_title(f"{name} (red = new models)")
    fig.tight_layout(); fig.savefig(OUT / "model_rank.png", dpi=130)


if __name__ == "__main__":
    main()
