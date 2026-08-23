# CANONICAL validity analysis for the four papers. Every signal-vs-human number quoted in
# papers/A..D MUST come from this script's output (papers/analysis/canonical_validity.json/.md).
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/canonical_validity.py
#
# Anchor set: the 60 labeled items of the random-stratum instrument
# (human_eval/labels/phase1/author_1_Sri_random.json), single annotator, blind, two scales.
# For each signal: Pearson r, Spearman rho, bootstrap 95% CI (2000 resamples), n,
# partial vs soundness holding style fixed, and the within-correct subset.
import json, math, re
from collections import Counter

import numpy as np

rng = np.random.default_rng(0)


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def boot_ci(x, y, f, n=2000):
    x, y = np.asarray(x, float), np.asarray(y, float)
    idx = np.arange(len(x)); out = []
    for _ in range(n):
        i = rng.choice(idx, len(idx))
        if len(set(y[i])) < 2 or len(set(x[i])) < 2:
            continue
        out.append(f(x[i], y[i]))
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


def partial(x, y, z):
    x, y, z = map(lambda a: np.asarray(a, float), (x, y, z))
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return pearson(rx, ry)


# ---------------------------------------------------------------- anchor labels
labs = [r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
        if r.get("soundness") not in (None, "")]
for L in labs:
    pid = L["id"].split("-", 2)[2]
    L["pid"] = pid[:pid.find(".json") + 5]
    L["soundness"] = float(L["soundness"]); L["style"] = float(L["style"])
print(f"anchor: {len(labs)} labeled items")

# ---------------------------------------------------------------- signal joins
traces = {r["id"]: r for r in (json.loads(l) for l in open("human_eval/traces_to_label.jsonl"))}
embed = json.load(open("runs/embed_sims_math500.json"))
emb_by = {}
for k, v in embed.items():
    m, pid = k.split("|")
    emb_by[(m.split("/")[-1], pid)] = v
panel = {}
for critic in ("gpt", "opus"):
    for l in open(f"runs/critic_panel/math_{critic}.jsonl"):
        r = json.loads(l)
        if r.get("ok"):
            panel[(critic, r["id"])] = r
pv = {}
for l in open("runs/prm_labelset/rollout_prm__Qwen__Qwen2.5-14B-Instruct.jsonl"):
    r = json.loads(l)
    V = r["V"] if isinstance(r["V"], dict) else json.loads(r["V"].replace("'", '"'))
    V = {float(k): v for k, v in V.items()}
    pv[(r["model"].split("/")[-1], r["problem_id"])] = V
lp = {}
for l in open("runs/scores_math500_corrected.jsonl"):
    r = json.loads(l)
    lp[(r["model"].split("/")[-1], r["problem_id"])] = r.get("tfa_logprob")


def _toks(t):
    return re.findall(r"[a-z0-9]+", t.lower())


REFS = {t["pid"] if "pid" in t else None: None for t in []}
gold_toks = {}
for t in traces.values():
    gold_toks[t["id"]] = _toks(t["gold_solution"])
DF = Counter()
for t in traces.values():
    DF.update(set(_toks(t["gold_solution"])))
NDOC = len(traces)


def unigram_f1(a, b):
    ca, cb = Counter(a), Counter(b)
    ov = sum((ca & cb).values())
    if not ov:
        return 0.0
    p, r = ov / max(sum(ca.values()), 1), ov / max(sum(cb.values()), 1)
    return 2 * p * r / (p + r)


def tfidf_cos(a, b):
    ca, cb = Counter(a), Counter(b)
    keys = set(ca) | set(cb)
    va = {k: ca[k] * math.log(NDOC / (1 + DF[k])) for k in keys}
    vb = {k: cb[k] * math.log(NDOC / (1 + DF[k])) for k in keys}
    num = sum(va[k] * vb[k] for k in keys)
    den = math.sqrt(sum(v * v for v in va.values())) * math.sqrt(sum(v * v for v in vb.values()))
    return num / den if den else 0.0


rows = []
for L in labs:
    t = traces[L["id"]]
    tr_toks = _toks(t["trace"]); g_toks = gold_toks[L["id"]]
    key = (L["model"], L["pid"])
    V = pv.get(key)
    rows.append(dict(
        soundness=L["soundness"], style=L["style"], correct=int(L["machine_correct"]),
        tfa=float(L["tfa"]), judge_ref=float(L["judge"]),
        logprob=lp.get(key), embed=emb_by.get(key),
        u1=unigram_f1(tr_toks, g_toks), tfidf=tfidf_cos(tr_toks, g_toks),
        critic_gpt=panel.get(("gpt", L["id"]), {}).get("soundness"),
        critic_opus=panel.get(("opus", L["id"]), {}).get("soundness"),
        pv_v0=V and V[0.0], pv_v25=V and V[0.25], pv_v5=V and V[0.5], pv_v75=V and V[0.75],
        pv_mean=V and float(np.mean(list(V.values()))),
    ))

SIGNALS = ["tfa", "logprob", "tfidf", "u1", "embed",
           "pv_v0", "pv_v25", "pv_v5", "pv_v75", "pv_mean",
           "judge_ref", "critic_gpt", "critic_opus"]
out = {"anchor_n": len(labs), "signals": {}}
md = ["| signal | n | Pearson r [95% CI] | Spearman rho | partial r (|style) | within-correct r (n) |",
      "|---|---|---|---|---|---|"]
for sig in SIGNALS:
    sub = [r for r in rows if r[sig] is not None]
    if len(sub) < 10:
        continue
    x = [r[sig] for r in sub]; s = [r["soundness"] for r in sub]; st = [r["style"] for r in sub]
    ci = boot_ci(x, s, pearson)
    wc = [r for r in sub if r["correct"] == 1]
    wr = pearson([r[sig] for r in wc], [r["soundness"] for r in wc]) if len(wc) > 8 else None
    rec = dict(n=len(sub), pearson=pearson(x, s), ci=ci, spearman=spearman(x, s),
               partial_style=partial(x, s, st),
               within_correct_r=wr, within_correct_n=len(wc))
    out["signals"][sig] = rec
    md.append(f"| {sig} | {rec['n']} | {rec['pearson']:+.2f} [{ci[0]:+.2f},{ci[1]:+.2f}] | "
              f"{rec['spearman']:+.2f} | {rec['partial_style']:+.2f} | "
              f"{'' if wr is None else f'{wr:+.2f}'} ({rec['within_correct_n']}) |")

# style partials the other direction, judge signals only (style-loading check)
for sig in ["judge_ref", "critic_gpt", "critic_opus"]:
    sub = [r for r in rows if r[sig] is not None]
    x = [r[sig] for r in sub]; s = [r["soundness"] for r in sub]; st = [r["style"] for r in sub]
    out["signals"][sig]["style_partial"] = partial(x, st, s)

json.dump(out, open("../../papers/analysis/canonical_validity.json", "w"), indent=1)
open("../../papers/analysis/canonical_validity.md", "w").write(
    f"# Canonical validity numbers (anchor n={len(labs)}, single annotator, blind)\n\n"
    + "\n".join(md) + "\n\nAll numbers vs human soundness. Style partials (judge signals): "
    + ", ".join(f"{s}={out['signals'][s]['style_partial']:+.2f}"
                for s in ["judge_ref", "critic_gpt", "critic_opus"] if s in out["signals"]) + "\n")
print(open("../../papers/analysis/canonical_validity.md").read())
