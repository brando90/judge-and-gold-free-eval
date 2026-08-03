# E1: observational error-subtlety analysis (zero new compute).
# Question: when a judge is fooled by a WRONG solution (false positive), is it because the error is
# SUBTLE? And does task difficulty predict judge FP only THROUGH subtlety (mediation signature)?
#
# Design (critic-corrected):
#   FP population: wrong (cc=0) solutions that have judge scores (Qwen ladder on MATH-500/GSM8K/Putnam,
#     both judges; plus d2 cross-family on the GPT judge).
#   Per-solution subtlety proxies, computed independently of the FP population:
#     subtle_tfa  = tfa_argmax of the wrong solution (surface proximity to the gold reference)
#     subtle_pop  = fraction of DISJOINT proxy models that produced the SAME wrong final answer
#                   (attractor errors: a wrong answer many models fall into is a plausible one)
#   Per-item difficulty, from the DISJOINT proxy pool only:
#     diff_dis    = 1 - solve rate among proxy models (never-judged models; at minimum excludes
#                   the solution's own model)
#   Tests:
#     T1 correlations of judge score on wrong solutions with each proxy (pooled + per dataset)
#     T2 regression with solver fixed effects: does subtlety survive? does difficulty's coefficient
#        shrink when subtlety enters (mediation signature)?
#     T3 within-difficulty tertiles: subtlety -> FP still?
#     T4 cross-judge: is being fooled SYSTEMATIC (gpt vs opus FP correlation on same wrong solutions),
#        and does subtlety predict the shared component?
import json, glob, re, collections, numpy as np

# ---------- answer extraction ----------
def extract_answer(text):
    if not text: return None
    m = list(re.finditer(r"\\boxed\{", text))
    if m:
        i = m[-1].end(); depth = 1; j = i
        while j < len(text) and depth > 0:
            if text[j] == "{": depth += 1
            elif text[j] == "}": depth -= 1
            j += 1
        ans = text[i:j-1]
    else:
        m2 = re.search(r"####\s*([^\n]+)", text)
        if m2: ans = m2.group(1)
        else:
            nums = re.findall(r"-?\d[\d,]*\.?\d*", text)
            ans = nums[-1] if nums else None
    if ans is None: return None
    a = ans.strip().replace(",", "").replace("$", "").replace(" ", "")
    a = a.replace("\\left", "").replace("\\right", "").replace("\\!", "").rstrip(".")
    try:
        f = float(a)
        return str(int(f)) if f == int(f) else str(f)
    except Exception:
        return a.lower()

# ---------- load ----------
def load_cc(fp):
    cc = {}
    for line in open(fp):
        r = json.loads(line)
        if r.get("cc") is not None: cc[(r["model"], r["problem_id"])] = float(r["cc"])
    return cc

DATASETS = {
    "MATH-500": dict(judged=["runs/math500/*.judged.jsonl", "runs/math500/*.judged.opus.jsonl",
                             "runs/d2/math500__*.judged.jsonl"],
                     scores="runs/scores_math500.jsonl", allglob="runs/all/math500__*.jsonl"),
    "GSM8K":    dict(judged=["runs/gsm8k/*.judged.jsonl", "runs/gsm8k/*.judged.opus.jsonl",
                             "runs/d2/gsm8k__*.judged.jsonl"],
                     scores="runs/scores_gsm8k.jsonl", allglob="runs/all/gsm8k__*.jsonl"),
    "Putnam":   dict(judged=["runs/putnam/*.judged.jsonl", "runs/putnam/*.judged.opus.jsonl",
                             "runs/d2/putnam-axiom__*.judged.jsonl"],
                     scores="runs/scores_putnam.jsonl", allglob="runs/all/putnam-axiom__*.jsonl"),
}
CC_ALL = load_cc("runs/scores_all.jsonl")   # 17 models x 6 datasets fallback

def r2(y, cols):
    X = np.column_stack([np.ones(len(y))] + cols)
    b, *_ = np.linalg.lstsq(X, y, rcond=None); p = X @ b
    st = ((y - y.mean())**2).sum()
    return (0.0 if st == 0 else 1 - ((y - p)**2).sum()/st), b

def corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if a.std() == 0 or b.std() == 0: return np.nan
    return float(np.corrcoef(a, b)[0, 1])

def dummies(ids):
    u = sorted(set(ids)); return [np.array([1.0 if x == uu else 0.0 for x in ids]) for uu in u[1:]]

if __name__ == "__main__":
    OUT = {}
    for name, cfg in DATASETS.items():
        cc_ds = load_cc(cfg["scores"])
        def get_cc(model, pid):
            return cc_ds.get((model, pid), CC_ALL.get((model, pid)))

        # judged records
        judged = []           # dicts with judge tag
        judged_models = set()
        for g in cfg["judged"]:
            for fp in glob.glob(g):
                for line in open(fp):
                    r = json.loads(line)
                    if r.get("judge_score") is None: continue
                    c = get_cc(r["model"], r["problem_id"])
                    if c is None: continue
                    jm = str(r.get("judge_model", ""))
                    jt = "opus" if "opus" in jm or "claude" in jm else "gpt"
                    judged.append(dict(model=r["model"], pid=r["problem_id"], judge=jt,
                                       score=float(r["judge_score"]), cc=c,
                                       tfa=float(r.get("tfa_argmax") or np.nan),
                                       ans=extract_answer(r.get("free_gen"))))
                    judged_models.add(r["model"])

        # proxy pool: runs/all models NOT in the judged set (strict disjoint)
        pool = collections.defaultdict(dict)   # pid -> {model: (cc, ans)}
        pool_models = set()
        for fp in glob.glob(cfg["allglob"]):
            rows = [json.loads(l) for l in open(fp)]
            if not rows: continue
            m = rows[0]["model"]
            if m in judged_models: continue
            pool_models.add(m)
            for r in rows:
                c = get_cc(m, r["problem_id"])
                if c is None: continue
                pool[r["problem_id"]][m] = (c, extract_answer(r.get("free_gen")))

        # per-item disjoint difficulty + wrong-answer popularity
        diff_dis, wrong_pop = {}, collections.defaultdict(dict)
        for pid, d in pool.items():
            ccs = [v[0] for v in d.values()]
            if len(ccs) >= 4: diff_dis[pid] = 1 - float(np.mean(ccs))
            wrongs = [v[1] for v in d.values() if v[0] == 0 and v[1] is not None]
            if wrongs:
                cnt = collections.Counter(wrongs)
                for a, k in cnt.items(): wrong_pop[pid][a] = k / len(d)

        # FP population: wrong judged solutions with all proxies available
        P = [j for j in judged if j["cc"] == 0 and j["pid"] in diff_dis and not np.isnan(j["tfa"])]
        for j in P:
            j["pop"] = wrong_pop.get(j["pid"], {}).get(j["ans"], 0.0)
            j["diff"] = diff_dis[j["pid"]]

        OUT[name] = dict(n_pool_models=len(pool_models), n_wrong=len(P))
        print(f"\n===== {name}: {len(P)} wrong judged solutions | proxy pool {len(pool_models)} disjoint models =====")
        for jt in ("gpt", "opus"):
            S = [j for j in P if j["judge"] == jt]
            if len(S) < 80: print(f"  [{jt}] n={len(S)} too small"); continue
            y = np.array([j["score"] for j in S])
            tfa = np.array([j["tfa"] for j in S]); popl = np.array([j["pop"] for j in S])
            dif = np.array([j["diff"] for j in S]); mdl = [j["model"] for j in S]
            z = lambda v: (v - v.mean())/(v.std()+1e-9)
            tfa_z, pop_z, dif_z = z(tfa), z(popl), z(dif)
            fe = dummies(mdl)
            # T1
            print(f"  [{jt}] n={len(S)}  FP-score mean={y.mean():.2f}")
            print(f"    T1 corr(score, tfa)={corr(y,tfa):+.3f}  corr(score, pop)={corr(y,popl):+.3f}  corr(score, diff)={corr(y,dif):+.3f}")
            # T2 nested regressions with solver FE
            r2_fe,_ = r2(y, fe)
            r2_d, bd = r2(y, fe+[dif_z])
            r2_s, bs = r2(y, fe+[tfa_z, pop_z])
            r2_ds, bds = r2(y, fe+[dif_z, tfa_z, pop_z])
            beta_d_alone = bd[-1]; beta_d_full = bds[-3]; beta_tfa = bds[-2]; beta_pop = bds[-1]
            shrink = 100*(1 - beta_d_full/beta_d_alone) if abs(beta_d_alone) > 1e-9 else np.nan
            print(f"    T2 R2: FE={100*r2_fe:.1f}%  +diff={100*r2_d:.1f}%  +subtle={100*r2_s:.1f}%  +both={100*r2_ds:.1f}%")
            print(f"       beta_diff alone={beta_d_alone:+.3f} -> with subtlety={beta_d_full:+.3f} (shrink {shrink:.0f}%)  beta_tfa={beta_tfa:+.3f} beta_pop={beta_pop:+.3f}")
            # T3 within-difficulty tertiles
            qs = np.quantile(dif, [1/3, 2/3])
            msg = []
            for lo, hi, tag in [(-1, qs[0], "easy"), (qs[0], qs[1], "mid"), (qs[1], 2, "hard")]:
                m = (dif > lo) & (dif <= hi)
                if m.sum() >= 40:
                    msg.append(f"{tag}: r_tfa={corr(y[m],tfa[m]):+.2f} r_pop={corr(y[m],popl[m]):+.2f} (n={int(m.sum())})")
            print(f"    T3 within-difficulty tertiles: " + " | ".join(msg))
            OUT[name][jt] = dict(n=len(S), r_tfa=corr(y,tfa), r_pop=corr(y,popl), r_diff=corr(y,dif),
                                 r2_fe=r2_fe, r2_d=r2_d, r2_s=r2_s, r2_ds=r2_ds,
                                 beta_d_alone=float(beta_d_alone), beta_d_full=float(beta_d_full),
                                 beta_tfa=float(beta_tfa), beta_pop=float(beta_pop))
        # T4 cross-judge systematicity (Qwen ladder has both judges on same solutions)
        both = collections.defaultdict(dict)
        for j in P: both[(j["model"], j["pid"])][j["judge"]] = j
        pairs = [(d["gpt"], d["opus"]) for d in both.values() if "gpt" in d and "opus" in d]
        if len(pairs) >= 80:
            g = np.array([p[0]["score"] for p in pairs]); o = np.array([p[1]["score"] for p in pairs])
            shared = (g + o) / 2
            tfa2 = np.array([p[0]["tfa"] for p in pairs]); pop2 = np.array([p[0]["pop"] for p in pairs])
            print(f"    T4 cross-judge (n={len(pairs)}): corr(gpt,opus FP)={corr(g,o):+.3f}  "
                  f"corr(shared, tfa)={corr(shared,tfa2):+.3f}  corr(shared, pop)={corr(shared,pop2):+.3f}")
            OUT[name]["cross"] = dict(n=len(pairs), r_gpt_opus=corr(g,o),
                                      r_shared_tfa=corr(shared,tfa2), r_shared_pop=corr(shared,pop2))

    json.dump(OUT, open("runs/subtlety_e1.json", "w"), indent=2, default=float)
    print("\nwrote runs/subtlety_e1.json")
