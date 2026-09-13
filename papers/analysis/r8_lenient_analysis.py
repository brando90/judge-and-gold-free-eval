# POST HOC re-analysis for the round-8 revision (no registration weight). Run from experiments/tfa-vs-judge after
# r8_lenient_labels.py (and, when available, r8_lenient_labels_model.py). Writes papers/analysis/r8_lenient_results.json.
# For each constructed pool (replication; k-pool at k=1 and k>1), judge, and labeling, with NO candidates set aside:
#   acc   best-of-64 accuracy, referenced minus blind, ties averaged, tasks with pass rate in [0.2, 0.8] under that labeling
#         (acc_regset: the task set of the registered labels instead);
#   G_all per-task AUROC for correct vs wrong, referenced minus blind;
#   G_nm  per-task AUROC for correct answers that do not match the reference vs wrong answers, referenced minus blind;
#   FR    share of correct non-matching answers scored 3 or below, referenced minus blind (points / 100).
# Labelings: strict (registered), lenient (rule, primary), model (model-extracted answers for unboxed replies, if present),
# boxed_only (registered labels, unboxed candidates dropped). Matching uses the lenient extraction for every labeling.
# Also: blind-then-reveal and the max(blind, referenced) rule on the k-pool at k>1 under each labeling (original scorer),
# the k-step (k>1 minus k=1), and the share of wrong candidates whose extracted answer equals the reference's.
import json
import os

import numpy as np

NBOOT = 1000
OUT = "../../papers/analysis/r8_lenient_results.json"
S4 = "runs/r4/scores"


def boot(x, seed=0):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
    return [round(float(x.mean()), 4), [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)], int(len(x))]


def boot_diff(a, b, seed=0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return None
    rng = np.random.default_rng(seed)
    d = [a[rng.integers(0, len(a), len(a))].mean() - b[rng.integers(0, len(b), len(b))].mean() for _ in range(NBOOT)]
    return [round(float(a.mean() - b.mean()), 4), [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]]


def rows(f):
    return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(f))} if os.path.exists(f) else None


def auroc(sc, lab):
    pos = np.array([s for s, l in zip(sc, lab) if l and s is not None], float)
    neg = np.array([s for s, l in zip(sc, lab) if not l and s is not None], float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def sel_acc(scores, oracle, keep):
    ix = [i for i in range(len(oracle)) if keep[i] and scores[i] is not None]
    if not ix:
        return None
    s = np.array([scores[i] for i in ix], float)
    o = np.array([oracle[i] for i in ix], float)
    return float(o[np.isclose(s, s.max(), rtol=0, atol=1e-9)].mean())


def jl(f):
    return [json.loads(l) for l in open(f)]


LAB = {name: {r["problem_id"]: r for r in jl(f"runs/r8/lenient_{name}.jsonl")} for name in ("repl", "kpool")}
for name in ("repl", "kpool"):
    f = f"runs/r8/model_{name}.jsonl"
    if os.path.exists(f):
        for r in jl(f):
            LAB[name][r["problem_id"]]["model"] = r["model"]
            LAB[name][r["problem_id"]]["model_match"] = r["model_match"]


def labeling(L, how):
    """(labels, keep mask, matches-reference) for one task under one labeling."""
    n = len(L["strict"])
    if how == "strict":
        return L["strict"], [1] * n, L["match"]
    if how == "lenient":
        return L["lenient"], [1] * n, L["match"]
    if how == "model":
        return (L["model"], [1] * n, L["model_match"]) if "model" in L else (None, None, None)
    if how == "boxed_only":
        return L["strict"], L["boxed"], L["match"]
    raise ValueError(how)


def metrics(pool, pids, b, r, how):
    acc, acc_reg, gall, gnm, fr, lure = [], [], [], [], [], []
    for pid in pids:
        if pid not in b or pid not in r:
            continue
        L = LAB[pool][pid]
        lab, keep, mt = labeling(L, how)
        if lab is None:
            return None
        ix = [i for i in range(len(lab)) if keep[i]]
        o = [lab[i] for i in ix]
        sb, sr = [b[pid][i] for i in ix], [r[pid][i] for i in ix]
        pr = np.mean(o) if o else 0
        a1, a0 = sel_acc(sr, o, [1] * len(o)), sel_acc(sb, o, [1] * len(o))
        if a1 is not None and a0 is not None:
            if 0.2 <= pr <= 0.8:
                acc.append(a1 - a0)
            sp = np.mean(L["strict"])
            if 0.2 <= sp <= 0.8:
                acc_reg.append(a1 - a0)
        x0, x1 = auroc(sb, o), auroc(sr, o)
        if x0 is not None and x1 is not None:
            gall.append((x0, x1))
        nm = [j for j, i in enumerate(ix) if not (lab[i] and mt[i])]
        lab_nm = [o[j] for j in nm]
        x0, x1 = auroc([sb[j] for j in nm], lab_nm), auroc([sr[j] for j in nm], lab_nm)
        if x0 is not None and x1 is not None:
            gnm.append((x0, x1))
        cnm = [j for j in nm if o[j]]
        fb = [sb[j] <= 3 for j in cnm if sb[j] is not None]
        fr_ = [sr[j] <= 3 for j in cnm if sr[j] is not None]
        if fb and fr_:
            fr.append(np.mean(fr_) - np.mean(fb))
        refx = next((L["extracted"][i] for i in range(len(lab)) if L["match"][i]), None)
        wrong = [i for i in ix if not lab[i]]
        if wrong and refx is not None:
            lure.append(np.mean([L["extracted"][i] == refx for i in wrong]))
    g = lambda v, k: boot([x[k] for x in v])
    return dict(acc=boot(acc), acc_regset=boot(acc_reg), G_all=boot([x[1] - x[0] for x in gall]), G_all_blind=g(gall, 0), G_all_ref=g(gall, 1),
                G_nm=boot([x[1] - x[0] for x in gnm]), G_nm_blind=g(gnm, 0), G_nm_ref=g(gnm, 1), FR=boot(fr),
                wrong_share_stating_reference=boot(lure), _acc_raw=acc)


JUDGES = {
    "repl": {"Qwen2.5-7B": f"{S4}/repl__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl",
             "phi-4": "runs/bon_scores_repl/synthk__microsoft__phi-4__{}_a.jsonl",
             "GPT-4.1": "runs/bon_scores_repl/synthk__openai__gpt-4.1-2025-04-14__{}_a.jsonl"},
    "kpool": {"Qwen2.5-7B": f"{S4}/kstrat__Qwen__Qwen2.5-7B-Instruct__{{}}_a.jsonl",
              "Qwen2.5-14B": f"{S4}/kstrat__Qwen__Qwen2.5-14B-Instruct__{{}}_a.jsonl",
              "gemma-2-9b": f"{S4}/kstrat__google__gemma-2-9b-it__{{}}_a.jsonl",
              "phi-4": "runs/bon_scores_kstrat/synthk__microsoft__phi-4__{}_a.jsonl",
              "Mistral-7B": f"{S4}/kstrat__mistralai__Mistral-7B-Instruct-v0.3__{{}}_a.jsonl",
              "GPT-4.1": "runs/bon_scores_kstrat/synthk__openai__gpt-4.1-2025-04-14__{}_a.jsonl"},
}
HOWS = ("strict", "lenient", "model", "boxed_only")
res = {"pools": {}}
for pool, js in JUDGES.items():
    subsets = {"all": list(LAB[pool])} if pool == "repl" else {
        "k1": [p for p, L in LAB[pool].items() if int(L["k"]) == 1], "kgt1": [p for p, L in LAB[pool].items() if int(L["k"]) > 1]}
    for jn, pat in js.items():
        b, r = rows(pat.format("noref")), rows(pat.format("ref"))
        if not (b and r):
            continue
        for sub, pids in subsets.items():
            for how in HOWS:
                m = metrics(pool, pids, b, r, how)
                if m is not None:
                    res["pools"].setdefault(f"{pool}|{sub}", {}).setdefault(jn, {})[how] = m
        if pool == "kpool":
            for how in HOWS:
                d = res["pools"].get("kpool|kgt1", {}).get(jn, {}).get(how)
                e = res["pools"].get("kpool|k1", {}).get(jn, {}).get(how)
                if d and e:
                    d["k_step_acc"] = boot_diff(d["_acc_raw"], e["_acc_raw"])
for d in res["pools"].values():
    for j in d.values():
        for m in j.values():
            m.pop("_acc_raw", None)

# blind-then-reveal and max rule, k-pool k>1, original scorer for all three score sets
KJ = {"Qwen2.5-7B": "Qwen__Qwen2.5-7B-Instruct", "Qwen2.5-14B": "Qwen__Qwen2.5-14B-Instruct", "gemma-2-9b": "google__gemma-2-9b-it", "phi-4": "microsoft__phi-4"}
res["rules_kpool_kgt1"] = {}
for jn, jt in KJ.items():
    b, r, m1 = (rows(f"runs/bon_scores_kstrat/synthk__{jt}__noref_a.jsonl"), rows(f"runs/bon_scores_kstrat/synthk__{jt}__ref_a.jsonl"),
                rows(f"runs/bon_scores_kstrat/kstrat__{jt}__m1_a.jsonl"))
    if not (b and r and m1):
        continue
    for how in HOWS:
        acc = {"reference": [], "max": [], "blind_then_reveal": []}
        for pid, L in LAB["kpool"].items():
            if int(L["k"]) == 1 or not all(pid in x for x in (b, r, m1)):
                continue
            lab, keep, _ = labeling(L, how)
            if lab is None:
                break
            ix = [i for i in range(len(lab)) if keep[i]]
            o = [lab[i] for i in ix]
            if not o or not (0.2 <= np.mean(o) <= 0.8):
                continue
            ones = [1] * len(o)
            base = sel_acc([b[pid][i] for i in ix], o, ones)
            acc["reference"].append(sel_acc([r[pid][i] for i in ix], o, ones) - base)
            acc["max"].append(sel_acc([max(b[pid][i], r[pid][i]) for i in ix], o, ones) - base)
            acc["blind_then_reveal"].append(sel_acc([m1[pid][i] for i in ix], o, ones) - base)
        else:
            res["rules_kpool_kgt1"].setdefault(jn, {})[how] = {k: boot(v) for k, v in acc.items()}

# label agreement between the rule and the model extraction (unboxed replies only)
agree = {}
for pool in ("repl", "kpool"):
    a = n = rl = ml = 0
    for L in LAB[pool].values():
        if "model" not in L:
            break
        for i, bx in enumerate(L["boxed"]):
            if bx:
                continue
            n += 1
            a += L["lenient"][i] == L["model"][i]
            rl += L["lenient"][i]
            ml += L["model"][i]
    if n:
        agree[pool] = dict(unboxed=n, agreement=round(a / n, 4), rule_correct=rl, model_correct=ml)
res["rule_vs_model_agreement_unboxed"] = agree
json.dump(res, open(OUT, "w"), indent=1)


def short(x):
    return None if x is None else (round(x[0], 3), x[1][0], x[1][1])


for key, d in res["pools"].items():
    for jn, hows in d.items():
        for how, m in hows.items():
            print(f"{key:12s} {jn:12s} {how:10s} acc {short(m['acc'])} G_all {short(m['G_all'])} G_nm {short(m['G_nm'])} "
                  f"FR {short(m['FR'])} kstep {m.get('k_step_acc')} lure {short(m['wrong_share_stating_reference'])}")
for jn, hows in res["rules_kpool_kgt1"].items():
    for how, v in hows.items():
        print("RULES kpool>1", jn, how, {k: short(x) for k, x in v.items()})
print("AGREE", agree)
