# Build the judging trial manifest: exactly which judge calls we intend to make, and why.
#
#   python scripts/v4_build_trials.py --pool runs/v4_pool/gpt-4.1-mini-2025-04-14.jsonl \
#       --out runs/v4_trials/trials.jsonl --n-valid 3 --n-invalid 3
#
# Written and inspected BEFORE any judging spend, so the design is auditable rather than implied by
# whatever the runner happens to do.
#
# CONDITIONS
#   C0        judge sees no reference at all         -> baseline, and the entry point for P3
#   C1_match  reference IS the candidate's own answer
#   C1_differ reference is a DIFFERENT correct answer
#
# C1_match is a controlled manipulation, not a coincidence. The alternative -- waiting for the
# generator to reproduce an answer already in the 7-entry bank -- yields only 84 usable items out of
# 256, because items have thousands of valid answers and the bank stores 7. Worse, the coincidences
# that do occur are biased: canonical answers are reproduced 2.17x more often than chance, which is
# the exact confound the reference sampler exists to remove. Constructing the match deliberately
# gives 161 items and a paired within-candidate comparison.
#
# The candidate's own answer is a legitimate reference: it is verified correct by a checker, and the
# bank's own entries are themselves mostly machine-generated (1,874 of 2,198).
#
# P1 (swap) reads off two C1_differ trials for one candidate carrying different references.
# P2 compares C1_match against C1_differ for the same candidate.
# P3 compares C0 against C1_differ for candidates the judge accepted blind.
import argparse
import collections
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, HERE)
import v4_reference_sampler as RS  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--bench", default=os.path.join(ROOT, "datasets/final_mathrefbench.jsonl"))
ap.add_argument("--out", default="runs/v4_trials/trials.jsonl")
ap.add_argument("--n-valid", type=int, default=3, help="valid candidates sampled per item")
ap.add_argument("--n-invalid", type=int, default=3, help="invalid candidates sampled per item")
ap.add_argument("--methods", default="M0,M3")
ap.add_argument("--judges", default="gpt-4.1-2025-04-14")
ap.add_argument("--seed", type=int, default=20260916)
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

bench = {r["question_id"]: r for r in (json.loads(l) for l in open(args.bench))}
pool = []
for line in open(args.pool):
    try:
        pool.append(json.loads(line))
    except json.JSONDecodeError:
        pass  # torn final line from a running job

by_item = collections.defaultdict(lambda: {"valid": [], "invalid": []})
for r in pool:
    if r.get("error") or not r.get("answer"):
        continue
    v = r.get("valid")
    if v is True:
        by_item[r["question_id"]]["valid"].append(r)
    elif v is False:
        by_item[r["question_id"]]["invalid"].append(r)

methods = [m.strip() for m in args.methods.split(",") if m.strip()]
judges = [j.strip() for j in args.judges.split(",") if j.strip()]

trials = []
skipped = collections.Counter()
for qid, groups in sorted(by_item.items()):
    item = bench.get(qid)
    if item is None:
        skipped["not_in_bench"] += 1
        continue
    # An item needs at least one VALID candidate: C1_match has no meaning without one, and a
    # judge-grades-a-correct-answer comparison is the whole experiment.
    if not groups["valid"]:
        skipped["no_valid_candidate"] += 1
        continue

    rng = random.Random(f"{args.seed}:{qid}")
    # Deduplicate by answer text first: 40 copies of one answer is one candidate, not forty.
    def pick(rows, k):
        seen, uniq = set(), []
        for r in rows:
            a = str(r.get("answer"))
            if a not in seen:
                seen.add(a)
                uniq.append(r)
        rng.shuffle(uniq)
        return uniq[:k]

    chosen = [(r, True) for r in pick(groups["valid"], args.n_valid)] + \
             [(r, False) for r in pick(groups["invalid"], args.n_invalid)]

    # Two distinct references per candidate, origin- and position-balanced.
    pairs = RS.sample_pairs(item, len(chosen), seed=args.seed)
    if not pairs:
        skipped["no_reference_pair"] += 1
        continue

    for i, (cand, is_valid) in enumerate(chosen):
        r1, r2, pair_label = pairs[i % len(pairs)]
        base = {"question_id": qid, "sample": cand["sample"],
                "candidate": cand["answer"], "candidate_valid": is_valid,
                "pair_label": pair_label}
        specs = [("C0", None, None)]
        if is_valid:
            # the candidate's own answer, shown back as the reference
            specs.append(("C1_match", cand["answer"], "self"))
        # two different correct references -> P1 reads the swap off this pair
        specs.append(("C1_differ", r1["answer"], "canonical" if RS.canonical(r1) else "generated"))
        specs.append(("C1_differ", r2["answer"], "canonical" if RS.canonical(r2) else "generated"))
        for cond, ref, origin in specs:
            for m in methods:
                for j in judges:
                    trials.append(dict(base, condition=cond, reference=ref,
                                       reference_origin=origin, method=m, judge=j,
                                       trial_id=f"{qid}|{cand['sample']}|{cond}|{origin}|{m}|{j}"))

items_used = len({t["question_id"] for t in trials})
cands = len({(t["question_id"], t["sample"]) for t in trials})
print(f"pool rows                : {len(pool):,}")
print(f"items with candidates    : {len(by_item)}")
print(f"items used               : {items_used}   skipped: {dict(skipped)}")
print(f"distinct candidates      : {cands:,}   ({args.n_valid} valid + {args.n_invalid} invalid per item)")
print(f"TRIALS (judge calls)     : {len(trials):,}")
print(f"  by condition : {dict(collections.Counter(t['condition'] for t in trials))}")
print(f"  by method    : {dict(collections.Counter(t['method'] for t in trials))}")
print(f"  by ref origin: {dict(collections.Counter(t['reference_origin'] for t in trials))}")
# Cost, priced PER METHOD. M0 asks for a grade plus a brief justification; M3 asks the judge to
# solve the problem itself first, so its replies look like generation output (median 1,457 output
# tokens over 12,941 draws, p90 5,653) rather than a short verdict. Pricing both as M0 understates
# the bill roughly twofold, which is the sort of estimate that gets a run approved and then
# overspends.
PRICE = {"gpt-4.1-2025-04-14": (2.0, 8.0), "gpt-4.1-mini-2025-04-14": (0.4, 1.6),
         "claude-sonnet-5": (3.0, 15.0)}
OUT_TOKENS = {"M0": 400, "M3": 2000}
IN_TOKENS = 900
by_mj = collections.Counter((t["method"], t["judge"]) for t in trials)
total = 0.0
for (m, j), k in sorted(by_mj.items()):
    pin, pout = PRICE.get(j, (2.0, 8.0))
    c = k * (IN_TOKENS * pin / 1e6 + OUT_TOKENS.get(m, 400) * pout / 1e6)
    total += c
    print(f"  {j} {m}: {k:,} calls x ~{OUT_TOKENS.get(m, 400)} out tok = ${c:,.0f}")
print(f"  ESTIMATED TOTAL: ${total:,.0f}   (input assumed ~{IN_TOKENS} tok/call)")

if not args.dry_run:
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        for t in trials:
            f.write(json.dumps(t) + "\n")
    print(f"\nwrote {args.out}")
else:
    print("\n(dry run, nothing written)")
