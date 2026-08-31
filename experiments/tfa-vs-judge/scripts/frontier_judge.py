# Frontier-judge anchoring check. Does a frontier-class judge anchor on the shown reference
# the way the open 1.5B-14B judges do?
# INTERNAL REGISTRATION: this header pins the design, estimator, and predictions, and the file
# is git-committed BEFORE any frontier score exists. No OSF post (external registration on hold).
#
# Why this matters. Every judge measured so far is an open model of at most 14B parameters, and
# anchoring DECREASES with scale on our within-family ladder (same-sample rotation flip +9.5 at
# 1.5B, +3.1 at 14B; k>1 margin +5.17 at 7B, +4.06 at 14B) without reaching zero. Whether that
# trend hits zero by frontier scale decides whether this paper describes production systems or
# only small open judges. That question is currently answered by extrapolation.
#
# ESTIMATOR CHOICE, and the constraint that forces it. The vLLM judges score by the
# logprob-expected value over the tokens 0..10, giving ~2500 distinct values. The CLI path
# returns text only, so a frontier score here is a SAMPLED INTEGER: 11 possible values. By this
# paper's own score-resolution finding, an 11-value judge ties massively under best-of-n and its
# INFLATION estimate would be an artifact of tie-breaking, not a measurement. We therefore do NOT
# compute inflation for the frontier judge. The readout is the ANCHORING MARGIN, a mean over many
# samples, which is well resolved even when each individual score is an integer. This restriction
# is a design decision, not a result, and is stated in the paper alongside the numbers.
#
# Design (pinned):
#   Pool: the frozen k-stratified pool, k>1 items where reference-matching and non-matching
#   oracle-valid samples coexist (the same 37-item population the open judges' margins use).
#   Per item: up to 6 matching and 6 non-matching valid samples, chosen by numpy default_rng(0).
#   Conditions: blind (no reference) and referenced (the item's ref_answer), rubric a text taken
#   verbatim from bon_rubrics.RUBRIC_TIES so the prompt matches the open judges exactly.
#   Score parse: first integer 0..10 in the reply; unparseable replies are dropped and counted.
#   Margin per item = mean(matching) - mean(non-matching); reported as the item-level mean with
#   a cluster bootstrap over items (NBOOT=1000, numpy default_rng(0)).
#
# REGISTERED PREDICTIONS:
#   P-F1: the frontier judge's REFERENCED margin is positive with a 95% CI excluding zero, i.e.
#     it anchors. Rationale: the scale trend decreases but has not reached zero by 14B.
#   P-F2: its BLIND margin's CI contains zero (control: no preference between equally valid
#     answers when no reference is shown).
#   P-F3 (directional, no CI requirement): its referenced margin is SMALLER than the open
#     judges' (+4.06 to +5.32 on this pool), continuing the capability trend.
#   A null on P-F1 is the most consequential outcome available here: it would bound the paper's
#   claim to sub-frontier judges and must be reported as prominently as a positive.
#
# Run from experiments/tfa-vs-judge:
#   python3 scripts/frontier_judge.py --model sonnet --workers 8
import argparse
import json
import os
import random
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

sys.path.insert(0, "scripts")
from bon_rubrics import RUBRIC_TIES

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="sonnet")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--per-group", type=int, default=6)
ap.add_argument("--timeout", type=float, default=120)
ap.add_argument("--out", default="runs/frontier_judge")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)

_ENV = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
rng = np.random.default_rng(0)


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
pool = {json.loads(l)["problem_id"]: json.loads(l)
        for l in open("runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl")}

jobs = []
for pid, it in sorted(pool.items()):
    if tasks[pid]["k"] <= 1:
        continue
    refn = norm(it["ref_answer"])
    match, nomatch = [], []
    for i, ok in enumerate(it["oracle"]):
        if not ok:
            continue
        a = norm(boxed(it["samples"][i]) or it["samples"][i])
        (match if a == refn else nomatch).append(i)
    if not match or not nomatch:
        continue
    pick = lambda g: list(rng.choice(g, min(args.per_group, len(g)), replace=False))
    for grp, idxs in (("match", pick(match)), ("nomatch", pick(nomatch))):
        for i in idxs:
            for cond in ("noref", "ref"):
                jobs.append(dict(problem_id=pid, idx=int(i), group=grp, cond=cond))

print(f"[frontier] {len(set(j['problem_id'] for j in jobs))} items, {len(jobs)} judge calls")


def build_prompt(job):
    it = pool[job["problem_id"]]
    sysmsg = RUBRIC_TIES[(job["cond"], "a")]
    parts = [f"Problem:\n{it['question']}"]
    if job["cond"] == "ref":
        parts.append(f"Reference answer (trusted):\n{it['ref_answer']}")
    parts.append(f"Candidate solution:\n{it['samples'][job['idx']]}\n\nScore:")
    return sysmsg + "\n\n" + "\n\n".join(parts)


def run_one(job):
    p = build_prompt(job)
    try:
        r = subprocess.run(["claude", "-p", "--model", args.model], input=p,
                           capture_output=True, text=True, timeout=args.timeout, env=_ENV)
        # take the LAST integer 0..10: replies are almost always a bare number, but a
        # reply that shows arithmetic before its verdict would otherwise be misparsed
        nums = re.findall(r"\b(10|[0-9])\b", r.stdout)
        job["score"] = int(nums[-1]) if nums else None
        job["raw"] = r.stdout.strip()[:200]
    except Exception as e:
        job["score"] = None
        job["raw"] = f"ERROR {str(e)[:120]}"
    return job


with ThreadPoolExecutor(args.workers) as ex:
    results = list(ex.map(run_one, jobs))

outf = f"{args.out}/frontier_{args.model}.jsonl"
with open(outf, "w") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")
n_bad = sum(1 for r in results if r["score"] is None)
print(f"[frontier] wrote {outf}; unparseable {n_bad}/{len(results)}")


def ci(vals):
    v = np.asarray(vals, float)
    b = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(1000)]
    return float(v.mean()), [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


summary = {"model": args.model, "n_calls": len(results), "n_unparseable": n_bad,
           "distinct_scores": sorted(set(r["score"] for r in results if r["score"] is not None))}
for cond in ("ref", "noref"):
    per_item = {}
    for r in results:
        if r["cond"] != cond or r["score"] is None:
            continue
        per_item.setdefault(r["problem_id"], {"match": [], "nomatch": []})[r["group"]].append(r["score"])
    margins = [np.mean(v["match"]) - np.mean(v["nomatch"])
               for v in per_item.values() if v["match"] and v["nomatch"]]
    if margins:
        m, c = ci(margins)
        summary[f"{cond}_margin"] = dict(mean=round(m, 3), ci=[round(c[0], 3), round(c[1], 3)],
                                         n_items=len(margins))
        print(f"  {cond:6s} margin {m:+.3f} [{c[0]:+.3f}, {c[1]:+.3f}] (n={len(margins)} items)")

if "ref_margin" in summary and "noref_margin" in summary:
    summary["P_F1_anchors"] = bool(summary["ref_margin"]["ci"][0] > 0)
    summary["P_F2_blind_null"] = bool(summary["noref_margin"]["ci"][0] <= 0 <= summary["noref_margin"]["ci"][1])
    summary["P_F3_smaller_than_open"] = bool(summary["ref_margin"]["mean"] < 4.06)
    print(f"\nP-F1 (anchors): {'CONFIRMED' if summary['P_F1_anchors'] else 'NOT CONFIRMED'}")
    print(f"P-F2 (blind null): {'holds' if summary['P_F2_blind_null'] else 'fails'}")
    print(f"P-F3 (smaller than open judges): {'holds' if summary['P_F3_smaller_than_open'] else 'fails'}")
json.dump(summary, open("../../papers/analysis/frontier_judge.json", "w"), indent=1)
