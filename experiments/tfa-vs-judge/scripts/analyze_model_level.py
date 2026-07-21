# Reusable model-level analysis for WS-V/WS1/WS2/WS4: per-model mean-TFA vs boxed accuracy (and judge
# if present), reported under Pearson, Spearman, Kendall tau-b, and ICC, pooled and within-family, with
# bootstrap CIs, and outlier flags (models far off the TFA-target line, e.g. math-specialized offset).
# Boxed accuracy is recomputed with the fixed scorer, never the stale stored boxed_correct.
import json, glob, argparse, collections, numpy as np
from scipy import stats
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent

def fam(m):
    m = m.lower()
    if "qwen2.5-math" in m or "qwen2-math" in m: return "Qwen-Math"
    if "deepseek-math" in m: return "DeepSeek-Math"
    if "mathstral" in m: return "Mathstral"
    if "numina" in m: return "NuminaMath"
    if "r1-distill" in m or "deepseek-r1" in m: return "R1-Distill"
    if "qwen2.5" in m or "qwen2-" in m: return "Qwen2.5"
    if "qwen3" in m: return "Qwen3"
    if "mistral" in m: return "Mistral"
    if "phi" in m: return "Phi"
    if "olmo" in m: return "OLMo"
    if "llama" in m: return "Llama"
    if "gemma" in m: return "Gemma"
    return "other"

MATH_SPECIALIZED = {"Qwen-Math", "DeepSeek-Math", "Mathstral", "NuminaMath"}

def gold_ans(r, dk):
    return r["gold_solution"].split("####")[-1].strip().replace(",", "") if dk == "gsm8k" else extract_boxed(r["gold_solution"])

def icc(x, y, form="A1"):
    # ICC on z-scored series (cross-scale). Two raters (k=2), n targets. Returns ICC(2,1) absolute
    # agreement (A1) or ICC(3,1) consistency (C1). After z-scoring, both are ~ Pearson; reported per PI.
    x = (np.asarray(x, float) - np.mean(x)) / (np.std(x) + 1e-12)
    y = (np.asarray(y, float) - np.mean(y)) / (np.std(y) + 1e-12)
    M = np.column_stack([x, y]); n, k = M.shape
    gm = M.mean(); rm = M.mean(1); cm = M.mean(0)
    SSR = k * np.sum((rm - gm) ** 2); SSC = n * np.sum((cm - gm) ** 2)
    SST = np.sum((M - gm) ** 2); SSE = SST - SSR - SSC
    MSR = SSR / (n - 1); MSC = SSC / (k - 1); MSE = SSE / ((n - 1) * (k - 1))
    if form == "C1":
        return (MSR - MSE) / (MSR + (k - 1) * MSE)
    return (MSR - MSE) / (MSR + (k - 1) * MSE + (k / n) * (MSC - MSE))

def allcorr(x, y):
    return dict(pearson=stats.pearsonr(x, y)[0], spearman=stats.spearmanr(x, y).statistic,
                kendall=stats.kendalltau(x, y).statistic, icc=icc(x, y, "A1"))

def boot_ci(x, y, fn, nb=2000):
    n = len(x); vals = []
    for _ in range(nb):
        idx = np.random.randint(0, n, n)
        try: vals.append(fn(x[idx], y[idx]))
        except Exception: pass
    return np.nanpercentile(vals, 2.5), np.nanpercentile(vals, 97.5)

def load_permodel(globs, dk, drop32b=True):
    P = {}
    for g in globs:
        for f in glob.glob(g):
            R = [json.loads(l) for l in open(f)]
            R = [r for r in R if r]
            if not R: continue
            m = R[0]["model"]
            if drop32b and "32B" in m: continue
            cc = [int(answers_equivalent(extract_final_answer(r["free_gen"], dk), gold_ans(r, dk))) for r in R]
            js = [r["judge_score"] for r in R if r.get("judge_score") is not None]
            P[m.split("/")[-1]] = dict(fam=fam(m), tfa=float(np.mean([r["tfa_argmax"] for r in R])),
                                       acc=float(np.mean(cc)), judge=float(np.mean(js)) if js else None, n=len(R))
    return P

def report(name, P, target="acc"):
    names = list(P)
    tfa = np.array([P[m]["tfa"] for m in names]); tgt = np.array([P[m][target] for m in names if P[m][target] is not None])
    if len(tgt) != len(tfa):
        print(f"  ({target} missing for some models; skipping)"); return
    fams = [P[m]["fam"] for m in names]; qmask = np.array([f == "Qwen2.5" for f in fams])
    print(f"\n== {name}: TFA vs {target}  (n={len(names)} models, {len(set(fams))} families) ==")
    for label, mask in [("POOLED", np.ones(len(names), bool)), ("Qwen2.5-only", qmask)]:
        if mask.sum() < 3: continue
        c = allcorr(tfa[mask], tgt[mask])
        ci = {k: boot_ci(tfa[mask], tgt[mask], (lambda a, b, kk=k: allcorr(a, b)[kk])) for k in c}
        print(f"  {label:13s} pearson={c['pearson']:+.2f}[{ci['pearson'][0]:+.2f},{ci['pearson'][1]:+.2f}] "
              f"spearman={c['spearman']:+.2f} kendall={c['kendall']:+.2f} icc={c['icc']:+.2f}")
    # outliers: standardized residual of target ~ tfa (OLS). |z|>1.5 flagged.
    b = np.polyfit(tfa, tgt, 1); resid = tgt - np.polyval(b, tfa); rz = resid / (resid.std() + 1e-12)
    THR = 1.5
    out_idx = [i for i in range(len(names)) if abs(rz[i]) > THR]
    if out_idx:
        print("  OUTLIERS (|std-resid|>%.1f), the models off the TFA->%s line:" % (THR, target))
        for i in sorted(out_idx, key=lambda j: -abs(rz[j])):
            direction = ("TFA INFLATED: high gold-token match for its accuracy -> training-style / tokenizer "
                         "familiarity with the reference, not ability" if rz[i] < 0
                         else "TFA UNDERSTATES: solves well but predicts the gold poorly -> different solution style")
            print(f"     {names[i]:34s} family={P[names[i]]['fam']:13s} TFA={P[names[i]]['tfa']:.3f} "
                  f"{target}={P[names[i]][target]:.3f} z={rz[i]:+.2f}  [{direction}]")
        keep = np.array([i not in out_idx for i in range(len(names))])
        c2 = allcorr(tfa[keep], tgt[keep])
        drop_fams = sorted(set(P[names[i]]["fam"] for i in out_idx))
        print(f"  POOLED minus |z|-outliers ({', '.join(drop_fams)}; n={keep.sum()}): "
              f"pearson={c2['pearson']:+.2f} spearman={c2['spearman']:+.2f} kendall={c2['kendall']:+.2f} icc={c2['icc']:+.2f}")
    else:
        print("  no |std-resid|>%.1f outliers." % THR)
    # Named removal: the math-specialized family (interpretable "remove the outlier family").
    ms_mask = np.array([P[names[i]]["fam"] in MATH_SPECIALIZED for i in range(len(names))])
    if ms_mask.any() and (~ms_mask).sum() >= 3:
        c3 = allcorr(tfa[~ms_mask], tgt[~ms_mask])
        ms_fams = sorted(set(P[names[i]]["fam"] for i in range(len(names)) if ms_mask[i]))
        print(f"  POOLED minus MATH-SPECIALIZED family ({', '.join(ms_fams)}; n={(~ms_mask).sum()}): "
              f"pearson={c3['pearson']:+.2f} spearman={c3['spearman']:+.2f} kendall={c3['kendall']:+.2f} icc={c3['icc']:+.2f}"
              f"   [reason: math-tuned models reproduce the gold style (high TFA) beyond their solving ability]")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--anchor", action="append", default=[], help="name:glob1,glob2:dskey")
    ap.add_argument("--target", default="acc", choices=["acc", "judge"])
    args = ap.parse_args()
    DEFAULT = [
        ("MATH-500", ["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl", "runs/wsv/math500__*.jsonl"], "math500"),
        ("GSM8K", ["runs/gsm8k/*.judged.jsonl", "runs/d2/gsm8k__*.judged.jsonl"], "gsm8k"),
        ("Putnam", ["runs/putnam/*.judged.jsonl", "runs/d2/putnam-axiom__*.judged.jsonl", "runs/wsv/putnam-axiom__*.jsonl"], "putnam"),
    ]
    anchors = DEFAULT if not args.anchor else [(a.split(":")[0], a.split(":")[1].split(","), a.split(":")[2]) for a in args.anchor]
    for name, globs, dk in anchors:
        P = load_permodel(globs, dk)
        if P: report(name, P, args.target)
