# Workstream A — full breadth analysis (6 datasets) + contamination & label-noise comparisons.
# Model-level rho(mean-TFA, acc) and rho(mean-TFA, judge); item-level partial rho(TFA, judge | correct)
# with bootstrap CI + length control; within-correct / within-wrong strata.
# Critic checks: boxed_correct (gen-time) vs recomputed cc (fixed local scorer) disagreement rate.
import json, glob, collections, numpy as np
from scipy import stats
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent
from tfa.analyze import bootstrap_partial, bootstrap_corr

DSETS = [
    ("MATH-500",  "runs/math500/*.judged.jsonl",   "math500"),
    ("MATH-full", "runs/mathfull/*.judged.jsonl",  "math500"),
    ("GSM8K",     "runs/gsm8k/*.judged.jsonl",     "gsm8k"),
    ("GSM8K-Plat","runs/gsm8kp/*.judged.jsonl",    "gsm8k"),
    ("Putnam",    "runs/putnam/*.judged.jsonl",    "putnam"),
    ("Putnam-Var","runs/putnamvar/*.judged.jsonl", "putnam"),
]

def gold_ans(r, ds):
    if ds == "gsm8k": return r["gold_solution"].split("####")[-1].strip().replace(",", "")
    return extract_boxed(r["gold_solution"])

def load(glob_, ds):
    R = [json.loads(l) for fp in glob.glob(glob_) for l in open(fp)]
    R = [r for r in R if r.get("judge_score") is not None]
    for r in R:
        r["cc"] = int(answers_equivalent(extract_final_answer(r["free_gen"], ds), gold_ans(r, ds)))
    return R

def resid(y, *ctrl):
    yr = stats.rankdata(y)
    X = np.column_stack([np.ones(len(y))] + [stats.rankdata(z) for z in ctrl])
    b, _, _, _ = np.linalg.lstsq(X, yr, rcond=None)
    return yr - X @ b

results = {}
hdr = f"{'dataset':11s} {'n':>5s} {'TFArange':>11s} {'acc':>5s} {'ML(TFA,acc)':>11s} {'ML(TFA,jdg)':>11s} {'IL partial|corr (CI)':>26s} {'|corr&len':>9s} {'w-cor':>6s} {'w-wrg':>6s} {'box!=cc':>7s}"
print(hdr); print("-" * len(hdr))
for ds, g, dskey in DSETS:
    R = load(g, dskey)
    if not R:
        print(f"{ds:11s}  (no files)"); continue
    by = collections.defaultdict(list)
    for r in R: by[r["model"]].append(r)
    mt, ma, mj = [], [], []
    for m in by:
        rs = by[m]
        mt.append(np.mean([x["tfa_argmax"] for x in rs]))
        ma.append(np.mean([x["cc"] for x in rs]))
        mj.append(np.mean([x["judge_score"] for x in rs]))
    mt, ma, mj = map(np.array, (mt, ma, mj))
    t = np.array([r["tfa_argmax"] for r in R]); j = np.array([r["judge_score"] for r in R])
    c = np.array([r["cc"] for r in R]); gl = np.array([r["n_gold_tokens"] for r in R])
    disagree = np.mean([int(r.get("boxed_correct", 0)) != r["cc"] for r in R])
    pc = bootstrap_partial(t, j, c, n_boot=3000)
    plen = stats.spearmanr(resid(t, c, gl), resid(j, c, gl)).statistic
    cm, wm = c == 1, c == 0
    wc = bootstrap_corr(t[cm], j[cm]).rho if cm.sum() > 5 else float("nan")
    ww = bootstrap_corr(t[wm], j[wm]).rho if wm.sum() > 5 else float("nan")
    mlacc = stats.spearmanr(mt, ma).statistic; mljdg = stats.spearmanr(mt, mj).statistic
    results[ds] = dict(n=len(R), acc=ma.mean(), mlacc=mlacc, mljdg=mljdg,
                       pc=pc, plen=plen, wc=wc, ww=ww, ncorr=int(cm.sum()), disagree=disagree)
    print(f"{ds:11s} {len(R):5d} {mt.min():.2f}-{mt.max():.2f} {ma.mean():5.2f} "
          f"{mlacc:+11.2f} {mljdg:+11.2f}   {pc.rho:+.3f} [{pc.lo:+.2f},{pc.hi:+.2f}]   "
          f"{plen:+9.3f} {wc:+6.2f} {ww:+6.2f} {100*disagree:6.1f}%")

def compare(a, b, label):
    if a not in results or b not in results: return
    A, B = results[a], results[b]
    print(f"\n### {label}: {a} vs {b}")
    print(f"    acc:            {A['acc']:.3f}  vs {B['acc']:.3f}   (Δ={B['acc']-A['acc']:+.3f})")
    print(f"    ML rho(TFA,jdg):{A['mljdg']:+.2f}   vs {B['mljdg']:+.2f}")
    print(f"    IL partial:     {A['pc'].rho:+.3f} [{A['pc'].lo:+.2f},{A['pc'].hi:+.2f}]  vs  "
          f"{B['pc'].rho:+.3f} [{B['pc'].lo:+.2f},{B['pc'].hi:+.2f}]")

print("\n" + "=" * 70)
compare("GSM8K", "GSM8K-Plat", "LABEL-NOISE (platinum removes GSM8K label errors)")
compare("Putnam", "Putnam-Var", "CONTAMINATION (functional variations vs original)")
compare("MATH-500", "MATH-full", "SCALE (500-subset vs full-algebra n=600)")
