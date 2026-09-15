# PRE-SPECIFIED producer for R24 (papers/D-iclr-v2/registration_round24.md); committed before any R24 call.
# Run from experiments/tfa-vs-judge. A score of 7 or above counts as correct (binary templates store 10 or 0).
#   --part a --cell NAME --scores FILE --out JSON
#       Standard graders on runs/r20/mace_gen/pool.jsonl, conditions ref and reflist. Questions: all four answers scored in both.
#       Per model and pooled: accuracy under each condition and under the answer list; condition minus list; reflist minus ref;
#       credit for correct answers that differ from the reference, that match it, and for wrong answers. Question bootstrap,
#       2,000 resamples, seed 0, paired.
#   --part b --leaderboard FILE --redraw FILE --out JSON
#       GPT-4.1 with the paper's rubric: blind and first-draw referenced accuracy against the list on runs/r20/mace_gen/pool.jsonl;
#       credit under the first and second draws for correct answers whose match changes (runs/r22/redraw_pool.jsonl).
#   --part c --judge NAME --scores FILE --out JSON
#       The answer list on runs/r8/sonnet_mace.jsonl (16 candidates per task): per task, grading AUROC of correct answers that
#       differ from the single reference against wrong answers (ties half), and their false-rejection rate (score 3 or below),
#       under noref, ref and reflist, on candidates scored in all three. Task bootstrap, 1,000 resamples, seed 0.
#   --part d --combined FILE --thinking FILE --sentence FILE --out JSON
#       Rise in false rejections and change in grading AUROC (referenced minus blind, each file against its own blind calls) for
#       thinking plus the full-credit sentence, thinking alone (R19-B) and the sentence alone (R20-B).
import argparse
import json

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--part", choices=("a", "b", "c", "d"), required=True)
ap.add_argument("--cell")
ap.add_argument("--scores")
ap.add_argument("--leaderboard")
ap.add_argument("--redraw")
ap.add_argument("--judge")
ap.add_argument("--combined")
ap.add_argument("--thinking")
ap.add_argument("--sentence")
ap.add_argument("--out", required=True)
args = ap.parse_args()
T = 7


def load(f):
    S = {}
    for line in open(f):
        r = json.loads(line)
        if r.get("score") is not None and not r.get("error"):
            S[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    return S


def boot_rows(n, nb, seed):
    rng = np.random.default_rng(seed)
    return [rng.integers(0, n, n) for _ in range(nb)]


def ci_mean(x, boots):
    x = np.asarray(x, float)
    m = [x[b].mean() for b in boots]
    return [round(float(x.mean()), 6), [round(float(np.percentile(m, 2.5)), 6), round(float(np.percentile(m, 97.5)), 6)]]


def ci_masked(mask, val, boots):
    def f(ix):
        d = mask[ix].sum()
        return float((mask[ix] * val[ix]).sum() / d) if d else np.nan
    m = [f(b) for b in boots]
    return [round(f(np.arange(len(mask))), 6), [round(float(np.nanpercentile(m, 2.5)), 6), round(float(np.nanpercentile(m, 97.5)), 6)],
            int(mask.sum())]


def auroc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0:
        return None
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def pool_matrices(pool_file, S, conds):
    pool = [json.loads(l) for l in open(pool_file)]
    n_gen = len(pool[0]["idx"])
    rows = [t for t in pool if all((t["problem_id"], i, c) in S for i in t["idx"] for c in conds)]
    M = {c: np.array([[S[(t["problem_id"], i, c)] >= T for i in t["idx"]] for t in rows], float) for c in conds}
    return pool, rows, M, n_gen


res = {"part": args.part}
if args.part == "a":
    S = load(args.scores)
    pool, rows, M, G = pool_matrices("runs/r20/mace_gen/pool.jsonl", S, ("ref", "reflist"))
    n = len(rows)
    boots = boot_rows(n, 2000, 0)
    orc = np.array([t["oracle"] for t in rows], float)
    nm = np.array([[o == 1 and g == "nonmatch" for o, g in zip(t["oracle"], t["group"])] for t in rows], float)
    mt = np.array([[o == 1 and g == "match" for o, g in zip(t["oracle"], t["group"])] for t in rows], float)
    wr = 1 - orc
    res.update(cell=args.cell, questions=n, questions_in_pool=len(pool), generators={})
    for i, g in enumerate(pool[0]["generators"]):
        res["generators"][g] = dict(list=ci_mean(orc[:, i], boots), ref=ci_mean(M["ref"][:, i], boots), reflist=ci_mean(M["reflist"][:, i], boots),
                                    ref_minus_list=ci_mean(M["ref"][:, i] - orc[:, i], boots),
                                    reflist_minus_list=ci_mean(M["reflist"][:, i] - orc[:, i], boots))
    P = dict(list=ci_mean(orc.mean(1), boots), ref=ci_mean(M["ref"].mean(1), boots), reflist=ci_mean(M["reflist"].mean(1), boots),
             ref_minus_list=ci_mean((M["ref"] - orc).mean(1), boots), reflist_minus_list=ci_mean((M["reflist"] - orc).mean(1), boots),
             reflist_minus_ref=ci_mean((M["reflist"] - M["ref"]).mean(1), boots))
    for name, mask in (("nonmatch_correct", nm), ("match_correct", mt), ("wrong", wr)):
        P[f"{name}_credited_ref"] = ci_masked(mask, M["ref"], boots)
        P[f"{name}_credited_reflist"] = ci_masked(mask, M["reflist"], boots)
        P[f"{name}_credited_reflist_minus_ref"] = ci_masked(mask, M["reflist"] - M["ref"], boots)
    res["pooled"] = P
    scored = n >= 100
    res["status"] = "scored" if scored else "not scored (fewer than 100 complete questions)"
    if scored:
        res["predictions"] = {
            "P-R24A1 ref below list (interval)": "confirmed" if P["ref_minus_list"][1][1] < 0 else (
                "falsified" if P["ref_minus_list"][1][0] > 0 else "not confirmed"),
            "P-R24A2 reflist within 5 points of list (point)": "confirmed" if abs(P["reflist_minus_list"][0]) <= 0.05 else "falsified",
            "P-R24A3 non-matching credit reflist minus ref >= 20 pp (point)":
                "confirmed" if P["nonmatch_correct_credited_reflist_minus_ref"][0] >= 0.20 else "falsified",
            "P-R24A4 wrong-answer credit reflist minus ref <= 3 pp (point)":
                "confirmed" if P["wrong_credited_reflist_minus_ref"][0] <= 0.03 else "falsified",
        }

elif args.part == "b":
    S1 = load(args.leaderboard)
    pool, rows, M, G = pool_matrices("runs/r20/mace_gen/pool.jsonl", S1, ("noref", "ref"))
    n = len(rows)
    boots = boot_rows(n, 2000, 0)
    orc = np.array([t["oracle"] for t in rows], float)
    res.update(questions_leaderboard=n, generators={})
    for i, g in enumerate(pool[0]["generators"]):
        res["generators"][g] = dict(list=ci_mean(orc[:, i], boots), blind=ci_mean(M["noref"][:, i], boots), ref=ci_mean(M["ref"][:, i], boots),
                                    ref_minus_list=ci_mean(M["ref"][:, i] - orc[:, i], boots),
                                    blind_minus_list=ci_mean(M["noref"][:, i] - orc[:, i], boots))
    res["pooled"] = dict(ref_minus_list=ci_mean((M["ref"] - orc).mean(1), boots), blind_minus_list=ci_mean((M["noref"] - orc).mean(1), boots))
    S2 = load(args.redraw)
    red = [json.loads(l) for l in open("runs/r22/redraw_pool.jsonl")]
    rrows = [t for t in red if all((t["problem_id"], i, "ref") in S1 and (t["problem_id"], i, "ref") in S2 for i in t["idx"])]
    m = len(rrows)
    rb = boot_rows(m, 2000, 0)
    r1 = np.array([[S1[(t["problem_id"], i, "ref")] >= T for i in t["idx"]] for t in rrows], float)
    r2 = np.array([[S2[(t["problem_id"], i, "ref")] >= T for i in t["idx"]] for t in rrows], float)
    ro = np.array([t["oracle"] for t in rrows], float)
    stop = np.array([[bool(o) and g1 == "match" and g2 != "match" for o, g1, g2 in zip(t["oracle"], t["group_draw1"], t["group"])] for t in rrows], float)
    start = np.array([[bool(o) and g2 == "match" and g1 != "match" for o, g1, g2 in zip(t["oracle"], t["group_draw1"], t["group"])] for t in rrows], float)
    res.update(questions_redraw=m)
    res["redraw"] = dict(draw2_minus_list=ci_mean((r2 - ro).mean(1), rb), draw2_minus_draw1=ci_mean((r2 - r1).mean(1), rb),
                         stop_credited_draw1=ci_masked(stop, r1, rb), stop_credited_draw2=ci_masked(stop, r2, rb),
                         stop_draw1_minus_draw2=ci_masked(stop, r1 - r2, rb),
                         start_credited_draw1=ci_masked(start, r1, rb), start_credited_draw2=ci_masked(start, r2, rb),
                         start_draw2_minus_draw1=ci_masked(start, r2 - r1, rb))
    P, R = res["pooled"], res["redraw"]
    ok_b = n >= 100
    ok_r = m >= 100
    res["status"] = dict(leaderboard="scored" if ok_b else "not scored", redraw="scored" if ok_r else "not scored")
    res["predictions"] = {
        "P-R24B1 ref below list (interval)": ("confirmed" if P["ref_minus_list"][1][1] < 0 else
                                              "falsified" if P["ref_minus_list"][1][0] > 0 else "not confirmed") if ok_b else "not scored",
        "P-R24B2 blind within 5 points of list (point)": ("confirmed" if abs(P["blind_minus_list"][0]) <= 0.05 else "falsified") if ok_b else "not scored",
        "P-R24B3 stop-matching credit draw1 minus draw2 > 0 (point)": ("confirmed" if R["stop_draw1_minus_draw2"][0] > 0 else "falsified") if ok_r else "not scored",
        "P-R24B4 start-matching credit draw2 minus draw1 > 0 (point)": ("confirmed" if R["start_draw2_minus_draw1"][0] > 0 else "falsified") if ok_r else "not scored",
    }

elif args.part == "c":
    S = load(args.scores)
    conds = ("noref", "ref", "reflist")
    X = {k: [] for k in ("G_blind", "G_ref", "G_reflist", "FR_blind", "FR_ref", "FR_reflist")}
    for t in (json.loads(l) for l in open("runs/r8/sonnet_mace.jsonl")):
        both = [j for j, i in enumerate(t["idx"]) if all((t["problem_id"], i, c) in S for c in conds)]
        cnm = [j for j in both if t["oracle"][j] and t["group"][j] != "match"]
        wrong = [j for j in both if not t["oracle"][j]]
        if not cnm or not wrong:
            continue
        for c, key in zip(conds, ("blind", "ref", "reflist")):
            sc = {j: S[(t["problem_id"], t["idx"][j], c)] for j in both}
            X[f"G_{key}"].append(auroc([sc[j] for j in cnm], [sc[j] for j in wrong]))
            X[f"FR_{key}"].append(np.mean([sc[j] <= 3 for j in cnm]))
    n = len(X["G_blind"])
    boots = boot_rows(n, 1000, 0)
    A = {k: np.asarray(v, float) for k, v in X.items()}
    res.update(judge=args.judge, tasks=n,
               G_blind=ci_mean(A["G_blind"], boots), G_ref=ci_mean(A["G_ref"], boots), G_reflist=ci_mean(A["G_reflist"], boots),
               G_ref_minus_blind=ci_mean(A["G_ref"] - A["G_blind"], boots), G_reflist_minus_blind=ci_mean(A["G_reflist"] - A["G_blind"], boots),
               G_reflist_minus_ref=ci_mean(A["G_reflist"] - A["G_ref"], boots),
               FR_ref_minus_blind=ci_mean(A["FR_ref"] - A["FR_blind"], boots), FR_reflist_minus_blind=ci_mean(A["FR_reflist"] - A["FR_blind"], boots),
               FR_reflist_minus_ref=ci_mean(A["FR_reflist"] - A["FR_ref"], boots))
    if n >= 20:
        res["predictions"] = {
            "P-R24C1 AUROC reflist minus blind >= -0.03 (point)": "confirmed" if res["G_reflist_minus_blind"][0] >= -0.03 else "falsified",
            "P-R24C2 false-rejection rise reflist minus blind <= 5 pp (point)": "confirmed" if res["FR_reflist_minus_blind"][0] <= 0.05 else "falsified",
            "P-R24C3 AUROC reflist minus ref > 0 (interval)": ("confirmed" if res["G_reflist_minus_ref"][1][0] > 0 else
                                                               "falsified" if res["G_reflist_minus_ref"][1][1] < 0 else "not confirmed"),
        }
    else:
        res["predictions"] = "not scored (fewer than 20 tasks)"

else:
    def change(f):
        S = load(f)
        G, F = [], []
        for t in (json.loads(l) for l in open("runs/r8/sonnet_mace.jsonl")):
            both = [j for j, i in enumerate(t["idx"]) if (t["problem_id"], i, "noref") in S and (t["problem_id"], i, "ref") in S]
            cnm = [j for j in both if t["oracle"][j] and t["group"][j] != "match"]
            wrong = [j for j in both if not t["oracle"][j]]
            if not cnm or not wrong:
                continue
            b = {j: S[(t["problem_id"], t["idx"][j], "noref")] for j in both}
            r = {j: S[(t["problem_id"], t["idx"][j], "ref")] for j in both}
            G.append(auroc([r[j] for j in cnm], [r[j] for j in wrong]) - auroc([b[j] for j in cnm], [b[j] for j in wrong]))
            F.append(np.mean([r[j] <= 3 for j in cnm]) - np.mean([b[j] <= 3 for j in cnm]))
        boots = boot_rows(len(G), 1000, 0)
        return dict(tasks=len(G), G_change=ci_mean(G, boots), FR_change=ci_mean(F, boots))
    C, TH, SE = change(args.combined), change(args.thinking), change(args.sentence)
    res.update(combined=C, thinking_alone=TH, sentence_alone=SE)
    if C["tasks"] >= 20:
        res["predictions"] = {
            "P-R24D1 FR rise combined below thinking alone and sentence alone (point)":
                "confirmed" if C["FR_change"][0] < min(TH["FR_change"][0], SE["FR_change"][0]) else "falsified",
            "P-R24D2 AUROC change combined above thinking alone and sentence alone (point)":
                "confirmed" if C["G_change"][0] > max(TH["G_change"][0], SE["G_change"][0]) else "falsified",
            "P-R24D3 FR rise combined > 0 (interval)": ("confirmed" if C["FR_change"][1][0] > 0 else
                                                        "falsified" if C["FR_change"][1][1] < 0 else "not confirmed"),
        }
    else:
        res["predictions"] = "not scored (fewer than 20 tasks)"

json.dump(res, open(args.out, "w"), indent=1)
print(json.dumps(res.get("predictions", res), indent=1))
