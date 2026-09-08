# POST-HOC (review-driven, 2026-09-07) sensitivity layer for Paper A's Table 1.
# Not registered; every number it emits is labeled post hoc in the paper. It answers four
# demands of the external NeurIPS-AC review of the story draft (Agreement_Is_Not_A_Certificate):
#   (1) "raw agreement" must be more than Pearson r: score every configuration under Pearson,
#       Spearman, Kendall tau, pairwise ordering accuracy against human soundness, and AUC
#       against machine correctness, and test whether ANY marginal metric separates the two
#       style-loaded evaluators from the honest blind ladder;
#   (2) partial correlations at n~60 under axis correlation need stress tests: rank
#       (Spearman) partials, Huber-robust standardized regression, and whether the frozen
#       verdicts survive each;
#   (3) common-method bias of a single rater labeling both axes: recompute partials on the
#       30-item overlap with soundness and style taken from DIFFERENT raters (author-1 soundness
#       with annotator-3 style, and the reverse);
#   (4) a simulation of verdict error rates for the frozen point rule and the CI rule, under
#       the measured label reliabilities (soundness 0.83, style 0.48), the anchor set's observed
#       axis correlation (+0.32; the +0.82 quoted in earlier drafts was the 20-item August-9
#       block, see human_eval/labels/phase1/RESULTS_style_loading.md), and n in {20..240},
#       for prototype judges spanning the (target, nuisance) plane.
# Inputs are exactly those of head_to_head.py / interrater.py (canonical joins, same files).
# Run from experiments/tfa-vs-judge:  python3 ../../papers/analysis/cert_review_sensitivity.py
# Output: papers/analysis/cert_review_sensitivity.json (+ .md summary)
import glob
import json
import os
import re

import numpy as np
from scipy import stats

rng = np.random.default_rng(0)
OUT = "../../papers/analysis/cert_review_sensitivity"

# ------------------------------------------------------------------ statistics helpers

def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def rank(x):
    return stats.rankdata(np.asarray(x, float))


def partial(x, y, z):
    x, y, z = map(lambda a: np.asarray(a, float), (x, y, z))
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return pearson(rx, ry)


def rank_partial(x, y, z):
    return partial(rank(x), rank(y), rank(z))


def huber_std_coefs(x, s, t, c=1.345, iters=50):
    """Standardized Huber-robust regression of judge score x on [soundness, style].
    Returns (beta_soundness, beta_style) on z-scored variables (IRLS, MAD scale)."""
    X = np.column_stack([np.ones(len(x)), stats.zscore(s), stats.zscore(t)])
    y = stats.zscore(np.asarray(x, float))
    w = np.ones(len(y))
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    for _ in range(iters):
        r = y - X @ beta
        scale = np.median(np.abs(r - np.median(r))) / 0.6745 or 1e-9
        u = np.abs(r / scale)
        w = np.where(u <= c, 1.0, c / np.maximum(u, 1e-12))
        Wx = X * w[:, None]
        new = np.linalg.solve(X.T @ Wx + 1e-9 * np.eye(3), Wx.T @ y)
        if np.max(np.abs(new - beta)) < 1e-8:
            beta = new
            break
        beta = new
    return float(beta[1]), float(beta[2])


def pairwise_accuracy(x, s):
    """Fraction of item pairs with unequal human soundness that the judge orders the same way
    (ties in the judge count one half)."""
    x, s = np.asarray(x, float), np.asarray(s, float)
    tot = conc = 0.0
    n = len(x)
    for i in range(n):
        for j in range(i + 1, n):
            if s[i] == s[j]:
                continue
            tot += 1
            d = (x[i] - x[j]) * (s[i] - s[j])
            conc += 1.0 if d > 0 else (0.5 if d == 0 else 0.0)
    return conc / tot if tot else float("nan")


def auc(x, c):
    x, c = np.asarray(x, float), np.asarray(c, int)
    pos, neg = x[c == 1], x[c == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    r = stats.rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def bci(f, *arrs, B=2000):
    arrs = [np.asarray(a, float) for a in arrs]
    idx = np.arange(len(arrs[0]))
    vs = []
    for _ in range(B):
        i = rng.choice(idx, len(idx))
        try:
            v = f(*[a[i] for a in arrs])
            if np.isfinite(v):
                vs.append(v)
        except Exception:
            pass
    if len(vs) < 100:
        return None
    return [round(float(np.percentile(vs, 2.5)), 2), round(float(np.percentile(vs, 97.5)), 2)]


def frozen_verdict(sp, tp):
    if tp > 0.30:
        return "convict"
    if sp > 0.40 and tp < 0.20:
        return "pass"
    return "fail"


# ------------------------------------------------------------------ canonical joins
labs = {r["id"]: r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
        if r.get("soundness") not in (None, "")}
traces = {r["id"]: r for r in (json.loads(l) for l in open("human_eval/traces_to_label.jsonl"))}


def load_scores(path, keys=("score", "rm_score", "soundness")):
    sc = {}
    for l in open(path):
        r = json.loads(l)
        tid = r.get("task_id") or r.get("id")
        v = next((r[k] for k in keys if r.get(k) is not None), None)
        if tid is not None and v is not None:
            sc[tid] = float(v)
    return sc


CONFIGS = {}
for f in sorted(glob.glob("runs/cert_out/*.jsonl")):
    base = os.path.basename(f)[:-6]
    cond, model = base.split("_", 1)
    CONFIGS[f"{cond}:{model.split('_')[-1]}"] = load_scores(f, keys=("score",))
CONFIGS["ref:GPT-5.2 (honest)"] = {i: float(labs[i]["judge"]) for i in labs}
CONFIGS["sabotage:GPT-5.2"] = load_scores("runs/cert_stylejudge_gpt.jsonl")
CONFIGS["rm:Skywork-8B"] = load_scores("runs/rm_scores_traces.jsonl", keys=("rm_score", "score"))

HONEST_BLIND = [k for k in CONFIGS if k.startswith("noref:")]
STYLE_LOADED = ["sabotage:GPT-5.2", "rm:Skywork-8B"]

# ------------------------------------------------------------------ (1)+(2) per configuration
per_cfg = {}
for name, sc in CONFIGS.items():
    ids = [i for i in labs if i in sc]
    if len(ids) < 20:
        print(f"[warn] {name}: join {len(ids)} too small, skipped")
        continue
    x = np.array([sc[i] for i in ids])
    s = np.array([float(labs[i]["soundness"]) for i in ids])
    t = np.array([float(labs[i]["style"]) for i in ids])
    c = np.array([int(labs[i]["machine_correct"]) for i in ids])
    sp, tp = partial(x, s, t), partial(x, t, s)
    rsp, rtp = rank_partial(x, s, t), rank_partial(x, t, s)
    hb_s, hb_t = huber_std_coefs(x, s, t)
    rec = dict(
        n=len(ids),
        marginal=dict(
            pearson=round(pearson(x, s), 2),
            spearman=round(float(stats.spearmanr(x, s).statistic), 2),
            kendall=round(float(stats.kendalltau(x, s).statistic), 2),
            pairwise_acc=round(pairwise_accuracy(x, s), 3),
            auc_vs_correct=round(auc(x, c), 3),
        ),
        partial_pearson=dict(sound=round(sp, 2), style=round(tp, 2),
                             verdict=frozen_verdict(sp, tp)),
        partial_rank=dict(sound=round(rsp, 2), style=round(rtp, 2),
                          style_ci=bci(rank_partial, x, t, s),
                          verdict=frozen_verdict(rsp, rtp)),
        huber_std=dict(sound=round(hb_s, 2), style=round(hb_t, 2)),
    )
    per_cfg[name] = rec

# does any marginal metric separate the style-loaded evaluators from the honest blind ladder?
sep = {}
for m in ("pearson", "spearman", "kendall", "pairwise_acc", "auc_vs_correct"):
    vals = {k: per_cfg[k]["marginal"][m] for k in per_cfg}
    hb = [vals[k] for k in HONEST_BLIND if k in vals]
    lo, hi = min(hb), max(hb)
    inside = {k: (lo <= vals[k] <= hi) for k in STYLE_LOADED if k in vals}
    order = sorted(vals, key=lambda k: -vals[k])
    sep[m] = dict(honest_blind_range=[lo, hi],
                  style_loaded_values={k: vals[k] for k in STYLE_LOADED if k in vals},
                  style_loaded_inside_or_below_honest_blind_range={
                      k: bool(vals[k] <= hi) for k in STYLE_LOADED if k in vals},
                  rank_of_style_loaded_among_all={k: order.index(k) + 1 for k in STYLE_LOADED
                                                  if k in vals},
                  n_configs=len(vals))
style_partial_sep = {}
vals = {k: per_cfg[k]["partial_pearson"]["style"] for k in per_cfg}
hb = [vals[k] for k in HONEST_BLIND if k in vals and k != "noref:Qwen2.5-1.5B-Instruct"]
style_partial_sep = dict(
    honest_blind_range_excluding_convicted_1p5B=[min(hb), max(hb)],
    style_loaded_values={k: vals[k] for k in STYLE_LOADED},
    max_over_all_non_convicted=max(v for k, v in vals.items()
                                   if per_cfg[k]["partial_pearson"]["verdict"] != "convict"))

verdict_agreement = dict(
    n_configs=len(per_cfg),
    rank_partial_same_verdict=int(sum(per_cfg[k]["partial_pearson"]["verdict"]
                                  == per_cfg[k]["partial_rank"]["verdict"] for k in per_cfg)),
    changed={k: [per_cfg[k]["partial_pearson"]["verdict"], per_cfg[k]["partial_rank"]["verdict"]]
             for k in per_cfg
             if per_cfg[k]["partial_pearson"]["verdict"] != per_cfg[k]["partial_rank"]["verdict"]},
    huber_style_sign_matches_partial=int(sum(
        np.sign(per_cfg[k]["huber_std"]["style"]) == np.sign(per_cfg[k]["partial_pearson"]["style"])
        for k in per_cfg)),
    huber_style_convicted_min=min(per_cfg[k]["huber_std"]["style"] for k in per_cfg
                                  if per_cfg[k]["partial_pearson"]["verdict"] == "convict"),
    huber_style_nonconvicted_max=max(per_cfg[k]["huber_std"]["style"] for k in per_cfg
                                     if per_cfg[k]["partial_pearson"]["verdict"] != "convict"),
)

# ------------------------------------------------------------------ (3) split-rater partials
blind = json.load(open("human_eval/blind_maps/rater2.json"))
a3 = {blind[r["id"]]["id"]: r for r in json.load(open("human_eval/labels/phase1/annotator_3.json"))
      if r.get("soundness") not in (None, "")}
ids30 = sorted(set(a3) & set(labs))
s1 = {i: float(labs[i]["soundness"]) for i in ids30}
t1 = {i: float(labs[i]["style"]) for i in ids30}
s3 = {i: float(a3[i]["soundness"]) for i in ids30}
t3 = {i: float(a3[i]["style"]) for i in ids30}
split = {"n": len(ids30), "configs": {}}
for name, sc in CONFIGS.items():
    sub = [i for i in ids30 if i in sc]
    if len(sub) < 20:
        continue
    x = np.array([sc[i] for i in sub])
    rows = {}
    for tag, S, T in (("same_rater_author1", s1, t1), ("same_rater_annotator3", s3, t3),
                      ("split_sound1_style3", s1, t3), ("split_sound3_style1", s3, t1)):
        sv = np.array([S[i] for i in sub]); tv = np.array([T[i] for i in sub])
        rows[tag] = dict(sound=round(partial(x, sv, tv), 2), style=round(partial(x, tv, sv), 2),
                         style_ci=bci(partial, x, tv, sv), sound_ci=bci(partial, x, sv, tv))
    split["configs"][name] = dict(n=len(sub), **rows)
# axis correlation across raters (a between-rater r(s,t) is free of within-rater halo)
split["axis_correlation"] = dict(
    within_author1=round(pearson([s1[i] for i in ids30], [t1[i] for i in ids30]), 2),
    within_annotator3=round(pearson([s3[i] for i in ids30], [t3[i] for i in ids30]), 2),
    cross_sound1_style3=round(pearson([s1[i] for i in ids30], [t3[i] for i in ids30]), 2),
    cross_sound3_style1=round(pearson([s3[i] for i in ids30], [t1[i] for i in ids30]), 2),
    within_author1_full60=round(pearson([float(labs[i]["soundness"]) for i in labs],
                                        [float(labs[i]["style"]) for i in labs]), 2))

# ------------------------------------------------------------------ (4) verdict-rate simulation
# Latent soundness S and style T are standard normal with correlation RHO_LAT chosen so that the
# OBSERVED label correlation reproduces the anchor set's r(soundness, style) = +0.32 under the
# measured cross-rater reliabilities (0.83 soundness, 0.48 style): observed r = RHO_LAT *
# sqrt(REL_S * REL_T). Judge score = a*S + b*T + e, with e ~ N(0, NOISE^2); prototypes are placed
# on the (target, nuisance) plane by (a, b, noise). Partials are computed on OBSERVED labels; the
# CI rule uses the Fisher-z interval for a first-order partial (se = 1/sqrt(n-4)).
REL_S, REL_T = 0.83, 0.48
R_OBS = split["axis_correlation"]["within_author1_full60"]
RHO = float(R_OBS / np.sqrt(REL_S * REL_T))
PROTOTYPES = {  # (a, b, noise)
    "strong_honest": (1.0, 0.0, 0.5), "mid_honest": (1.0, 0.0, 1.2),
    "boundary_honest": (1.0, 0.0, 1.9), "weak_honest": (1.0, 0.0, 3.0),
    "style_loaded": (0.3, 1.0, 0.9), "mixed": (1.0, 0.7, 1.0), "mild_style": (1.0, 0.4, 1.0),
}
NS = [20, 30, 40, 60, 100, 240]
REPS = 2000
sim = dict(params=dict(observed_axis_r=R_OBS, latent_axis_rho=round(RHO, 3), rel_sound=REL_S,
                       rel_style=REL_T, reps=REPS), prototypes={})
cov = np.array([[1, RHO], [RHO, 1]])
NS_LAT = 200000
for pname, (a, b, noise_sd) in PROTOTYPES.items():
    Z = rng.multivariate_normal([0, 0], cov, NS_LAT)
    J = a * Z[:, 0] + b * Z[:, 1] + noise_sd * rng.standard_normal(NS_LAT)
    lat = dict(sound=round(partial(J, Z[:, 0], Z[:, 1]), 2), style=round(partial(J, Z[:, 1], Z[:, 0]), 2),
               raw_r_sound=round(pearson(J, Z[:, 0]), 2))
    So = Z[:, 0] + np.sqrt((1 - REL_S) / REL_S) * rng.standard_normal(NS_LAT)
    To = Z[:, 1] + np.sqrt((1 - REL_T) / REL_T) * rng.standard_normal(NS_LAT)
    obs = dict(sound=round(partial(J, So, To), 2), style=round(partial(J, To, So), 2),
               raw_r_sound=round(pearson(J, So), 2))
    by_n = {}
    for n in NS:
        cnt = {"pass": 0, "fail": 0, "convict": 0}
        cnt_ci = {"pass": 0, "fail": 0, "convict": 0, "abstain": 0}
        se = 1 / np.sqrt(n - 4)
        for _ in range(REPS):
            Z = rng.multivariate_normal([0, 0], cov, n)
            J = a * Z[:, 0] + b * Z[:, 1] + noise_sd * rng.standard_normal(n)
            So = Z[:, 0] + np.sqrt((1 - REL_S) / REL_S) * rng.standard_normal(n)
            To = Z[:, 1] + np.sqrt((1 - REL_T) / REL_T) * rng.standard_normal(n)
            sp, tp = partial(J, So, To), partial(J, To, So)
            cnt[frozen_verdict(sp, tp)] += 1
            # CI rule (frozen for Putnam, osf.io/axp3s): convict if the style partial is
            # significantly positive and exceeds 0.30; pass if the soundness-partial CI clears
            # 0.40 and the style point estimate is below 0.20; abstain if the point rule would
            # pass but the CI does not clear; fail otherwise.
            tlo = np.tanh(np.arctanh(np.clip(tp, -0.999, 0.999)) - 1.96 * se)
            slo = np.tanh(np.arctanh(np.clip(sp, -0.999, 0.999)) - 1.96 * se)
            if tlo > 0 and tp > 0.30:
                cnt_ci["convict"] += 1
            elif sp > 0.40 and tp < 0.20:
                cnt_ci["pass" if slo > 0.40 else "abstain"] += 1
            else:
                cnt_ci["fail"] += 1
        by_n[n] = dict(point_rule={k: round(v / REPS, 3) for k, v in cnt.items()},
                       ci_rule={k: round(v / REPS, 3) for k, v in cnt_ci.items()})
    sim["prototypes"][pname] = dict(a=a, b=b, noise=noise_sd, latent_partials=lat,
                                    observed_label_partials=obs, by_n=by_n)

out = dict(note="POST HOC, review-driven (2026-09-07). Not registered. Same joins as "
                "head_to_head.py / interrater.py.",
           per_config=per_cfg, marginal_separation=sep, style_partial_separation=style_partial_sep,
           verdict_agreement=verdict_agreement, split_rater=split, simulation=sim)
json.dump(out, open(OUT + ".json", "w"), indent=1)

# ------------------------------------------------------------------ markdown summary
md = ["# Review-driven sensitivity layer for Paper A (post hoc)\n",
      "## Marginal agreement metrics vs the partials, per configuration\n",
      "| config | n | Pearson | Spearman | Kendall | pairwise acc | AUC(correct) | sound partial | style partial | verdict | rank sound p | rank style p [CI] | rank verdict | Huber b_style |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for k, r in per_cfg.items():
    m, p, q, h = r["marginal"], r["partial_pearson"], r["partial_rank"], r["huber_std"]
    md.append(f"| {k} | {r['n']} | {m['pearson']:+.2f} | {m['spearman']:+.2f} | {m['kendall']:+.2f} | "
              f"{m['pairwise_acc']:.3f} | {m['auc_vs_correct']:.3f} | {p['sound']:+.2f} | {p['style']:+.2f} | "
              f"{p['verdict']} | {q['sound']:+.2f} | {q['style']:+.2f} {q['style_ci']} | {q['verdict']} | {h['style']:+.2f} |")
md.append("\n## Does any marginal metric separate the style-loaded evaluators from the honest blind ladder?\n")
md.append("| metric | honest-blind range | sabotage GPT | Skywork RM | inside/below honest-blind range |")
md.append("|---|---|---|---|---|")
for m, r in sep.items():
    v = r["style_loaded_values"]; ib = r["style_loaded_inside_or_below_honest_blind_range"]
    md.append(f"| {m} | [{r['honest_blind_range'][0]}, {r['honest_blind_range'][1]}] | "
              f"{v.get('sabotage:GPT-5.2')} | {v.get('rm:Skywork-8B')} | {ib} |")
md.append(f"\nStyle partial: honest-blind (non-convicted) range {style_partial_sep['honest_blind_range_excluding_convicted_1p5B']}, "
          f"style-loaded {style_partial_sep['style_loaded_values']}, max over all non-convicted "
          f"{style_partial_sep['max_over_all_non_convicted']}.")
md.append(f"\nVerdict agreement Pearson vs rank partials: {verdict_agreement['rank_partial_same_verdict']}/"
          f"{verdict_agreement['n_configs']}; changed: {verdict_agreement['changed']}. Huber style-coefficient: "
          f"convicted min {verdict_agreement['huber_style_convicted_min']}, non-convicted max "
          f"{verdict_agreement['huber_style_nonconvicted_max']}.")
md.append(f"\n## Split-rater partials on the {split['n']}-item overlap\n")
md.append("axis correlation r(sound,style): " + json.dumps(split["axis_correlation"]))
md.append("\n| config | n | same-rater A1 (sound/style) | same-rater A3 | split S1/T3 | split S3/T1 |")
md.append("|---|---|---|---|---|---|")
for k, r in split["configs"].items():
    f = lambda tag: f"{r[tag]['sound']:+.2f} / {r[tag]['style']:+.2f} {r[tag]['style_ci']}"
    md.append(f"| {k} | {r['n']} | {f('same_rater_author1')} | {f('same_rater_annotator3')} | "
              f"{f('split_sound1_style3')} | {f('split_sound3_style1')} |")
md.append("\n## Simulation: verdict rates by prototype and n (point rule / CI rule)\n")
md.append("| prototype | (a,b) | latent partials | observed-label partials | n | point pass/fail/convict | CI pass/fail/convict/abstain |")
md.append("|---|---|---|---|---|---|---|")
for pname, r in sim["prototypes"].items():
    for n, v in r["by_n"].items():
        pr, cr = v["point_rule"], v["ci_rule"]
        md.append(f"| {pname} | ({r['a']},{r['b']},{r['noise']}) | {r['latent_partials']} | {r['observed_label_partials']} | {n} | "
                  f"{pr['pass']}/{pr['fail']}/{pr['convict']} | {cr['pass']}/{cr['fail']}/{cr['convict']}/{cr['abstain']} |")
open(OUT + ".md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
