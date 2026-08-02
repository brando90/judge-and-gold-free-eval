# Step 1 of the "reliable judges without ground truth" program: the YARDSTICK.
#
# Decompose an evaluator's per-item score into a QUALITY part (anchored on ground-truth correctness)
# and a SURFACE-NUISANCE part (response length, formatting, LaTeX density). The surface-nuisance
# fraction is the certificate: how much of the score is explained by things a good judge should ignore.
# We validate it where we HAVE ground truth (MATH-500, GSM8K, Putnam), so it can transfer to
# low-ground-truth domains from only a small anchor. We run it on two LLM judges (gpt-5.2, opus) and,
# for comparison, on TFA, so the yardstick can RANK evaluators by how surface-dominated they are.
#
# Two views per (dataset, evaluator, judge):
#   (A) full set:    variance of score explained by correctness, by surface, and by both.
#   (B) correct-only: among already-correct answers (correctness constant), variance explained by surface
#                     -- the sharpest "looks right vs is right" nuisance number.
import json, glob, collections, numpy as np

# judged files carry judge_score + free_gen + tfa; correctness (cc, the authoritative field) is joined
# from the per-dataset scores files by (model, problem_id). boxed_correct in the judged files is unreliable
# (all-zero on GSM8K/Putnam), so we never use it.
DATASETS = [
    ("MATH-500", ["runs/math500/*.judged*.jsonl"], "runs/scores_math500.jsonl"),
    ("GSM8K",    ["runs/gsm8k/*.judged*.jsonl"],    "runs/scores_gsm8k.jsonl"),
    ("Putnam",   ["runs/putnam/*.judged*.jsonl"],   "runs/scores_putnam.jsonl"),
]

def load_cc(scores_file):
    cc = {}
    for line in open(scores_file):
        r = json.loads(line)
        if r.get("cc") is not None:
            cc[(r["model"], r["problem_id"])] = float(r["cc"])
    return cc

def surface_features(t):
    t = t or ""
    L = len(t)
    words = t.split()
    return [
        np.log1p(L),                                   # log char length
        np.log1p(len(words)),                          # log word count
        t.count("\n"),                                 # line / step count
        (t.count("$") + t.count("\\")) / (L + 1.0),    # LaTeX / formatting density
        1.0 if "\\boxed" in t else 0.0,                # presence of a boxed answer
    ]

def load(globs, cc):
    recs = collections.defaultdict(list)   # judge_model -> list of records
    seen = matched = 0
    for g in globs:
        for f in glob.glob(g):
            for line in open(f):
                r = json.loads(line)
                if r.get("judge_score") is None: continue
                seen += 1
                key = (r.get("model"), r.get("problem_id"))
                if key not in cc: continue          # need a correctness anchor
                r["cc"] = cc[key]; matched += 1
                recs[r.get("judge_model", "?")].append(r)
    return recs, seen, matched

def r2(y, cols):
    # R^2 of OLS y ~ [1, *cols]
    X = np.column_stack([np.ones(len(y))] + cols)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ beta
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 0.0 if ss_tot == 0 else 1.0 - ss_res / ss_tot

def analyze(recs, score_key):
    y = np.array([float(r[score_key]) for r in recs], float)
    if len(y) < 30 or y.std() == 0: return None
    correct = np.array([float(r["cc"]) for r in recs], float)
    surf = np.array([surface_features(r.get("free_gen", "")) for r in recs], float)
    # standardize surface columns
    surf = (surf - surf.mean(0)) / (surf.std(0) + 1e-9)
    surf_cols = [surf[:, i] for i in range(surf.shape[1])]
    R_correct = r2(y, [correct])
    R_surface = r2(y, surf_cols)
    R_full    = r2(y, [correct] + surf_cols)
    out = {
        "n": len(y),
        "var_correct": R_correct,                 # explained by being right
        "var_surface": R_surface,                 # explained by surface (total)
        "var_full": R_full,
        "surface_beyond_correct": max(0.0, R_full - R_correct),   # nuisance not just from correctness
        "nuisance_frac_of_explained": (max(0.0, R_full - R_correct) / R_full) if R_full > 1e-9 else 0.0,
    }
    # (B) among already-correct answers
    mask = correct == 1
    if mask.sum() >= 30 and y[mask].std() > 0:
        surf_c = surf[mask]
        out["within_correct_surface"] = r2(y[mask], [surf_c[:, i] for i in range(surf_c.shape[1])])
        out["within_correct_length"] = r2(y[mask], [surf_c[:, 0]])   # log char length alone
        out["within_correct_n"] = int(mask.sum())
    return out

if __name__ == "__main__":
    results = {}
    for name, globs, scores_file in DATASETS:
        cc = load_cc(scores_file)
        recs_by_judge, seen, matched = load(globs, cc)
        print(f"# {name}: {matched}/{seen} judged records matched a cc anchor ({100*matched/max(seen,1):.0f}%)")
        results[name] = {}
        for judge, recs in sorted(recs_by_judge.items()):
            # merge to one record per (model, problem_id) is not needed; pool all responses
            row = {"judge_score": analyze(recs, "judge_score"),
                   "tfa_argmax":  analyze(recs, "tfa_argmax")}
            results[name][judge] = row

    # ---- print ----
    print(f"\n{'YARDSTICK: surface-nuisance decomposition of evaluators':}\n")
    hdr = f"{'dataset':9s} {'judge':16s} {'evaluator':11s} {'n':>5s} {'byCorrect':>9s} {'bySurface':>9s} {'surf>corr':>9s} {'inCorrect(surf)':>15s}"
    print(hdr); print("-" * len(hdr))
    for name in results:
        for judge in results[name]:
            for ev in ("judge_score", "tfa_argmax"):
                o = results[name][judge][ev]
                if not o: continue
                wc = o.get("within_correct_surface")
                wcs = f"{100*wc:6.1f}% (n={o.get('within_correct_n','?')})" if wc is not None else "n/a"
                jl = judge.split("/")[-1]
                print(f"{name:9s} {jl:16s} {ev:11s} {o['n']:5d} {100*o['var_correct']:8.1f}% "
                      f"{100*o['var_surface']:8.1f}% {100*o['surface_beyond_correct']:8.1f}% {wcs:>15s}")
        print()
    json.dump(results, open("runs/judge_nuisance.json", "w"), indent=2)
    print("wrote runs/judge_nuisance.json")
