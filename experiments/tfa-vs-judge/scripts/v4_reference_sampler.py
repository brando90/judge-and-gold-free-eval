# Which stored reference answer do we show the judge?
#
# In condition C1 the judge sees ONE reference. Something must choose which of the item's up-to-7
# stored answers that is, and the choice cannot be uniform-random.
#
# THE CONFOUND THIS EXISTS TO REMOVE
# ----------------------------------
# Every item's reference bank holds one CANONICAL answer (origin != "generated", always stored at
# index 0) plus machine-generated ones. Measured on this pool: gpt-4.1-mini reproduces the canonical
# answer 2.17x more often than chance (22 of 71 bank matches vs 10.1 expected, sd 2.95, z = 4.02,
# p = 5.8e-05).
#
# So under uniform sampling, WHICH reference we show is correlated with WHETHER the candidate
# matches it: show the canonical one and the candidate disproportionately matches (case A); show a
# generated one and it disproportionately differs (case B). If judges then score matching answers
# higher, "judges favour the answer they were shown" is indistinguishable from "canonical answers
# are easier to rediscover" -- a property of the generator, nothing to do with judging.
#
# The fix is to balance reference `origin` by construction and record it as a covariate, so case A
# and case B are compared on equal footing.
#
# SECOND BALANCE: POSITION
# ------------------------
# P1 grades the same candidate against two different correct references (R1, R2) and asks whether
# the verdict follows the reference. If the canonical answer were always R1, then reference origin
# and presentation order would be confounded too, so pairs alternate which side it takes.
import argparse
import collections
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
BENCH = os.path.join(ROOT, "datasets/final_mathrefbench.jsonl")
SEED = 20260916


def canonical(sol):
    """The published answer, as opposed to a machine-generated one. Always index 0 in this
    benchmark (verified: all 206 origin!='generated' entries sit at position 0)."""
    return sol.get("origin") != "generated"


def reference_classes(item):
    """Distinct answers, deduplicated by normalized_answer_id, split by origin.

    Dedup matters: the bank can hold several entries of the same answer class, and showing the
    'same' reference twice would silently weaken a swap trial into a no-op.
    """
    seen, canon, gen = set(), [], []
    for s in item["solutions"]:
        k = s["normalized_answer_id"]
        if k in seen:
            continue
        seen.add(k)
        (canon if canonical(s) else gen).append(s)
    return canon, gen


def sample_single(item, n_trials, seed=SEED):
    """C1 references for n_trials gradings of one item, balanced on origin.

    Returns [(solution, origin_label)]. Alternates canonical/generated so the balance holds at every
    prefix, not just in total -- a run stopped early is still balanced.
    """
    canon, gen = reference_classes(item)
    rng = random.Random(f"{seed}:{item['question_id']}")
    if not canon and not gen:
        return []
    if not canon:
        return [(rng.choice(gen), "generated") for _ in range(n_trials)]
    if not gen:
        return [(rng.choice(canon), "canonical") for _ in range(n_trials)]
    out = []
    for i in range(n_trials):
        if i % 2 == 0:
            out.append((rng.choice(canon), "canonical"))
        else:
            out.append((rng.choice(gen), "generated"))
    return out


def sample_pairs(item, n_pairs, seed=SEED):
    """Reference PAIRS for the P1 swap: the same candidate graded against R1 then R2.

    Returns [(r1, r2, label)] where r1 != r2 as answer classes. Balanced two ways:
      * origin   -- across pairs, canonical appears about as often as generated
      * position -- when a pair mixes canonical and generated, the canonical one takes the R1 slot
                    in half the pairs, so origin is not confounded with presentation order.
    Returns [] if the item has fewer than 2 distinct answer classes, since there is nothing to swap.
    """
    canon, gen = reference_classes(item)
    allrefs = canon + gen
    if len(allrefs) < 2:
        return []
    rng = random.Random(f"{seed}:pairs:{item['question_id']}")
    out = []
    for i in range(n_pairs):
        if canon and gen:
            c, g = rng.choice(canon), rng.choice(gen)
            out.append((c, g, "canonical_first") if i % 2 == 0 else (g, c, "generated_first"))
        else:
            a, b = rng.sample(allrefs, 2)
            out.append((a, b, "same_origin"))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="self-test: does the sampler actually balance?")
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--pairs", type=int, default=8)
    args = ap.parse_args()

    items = [json.loads(l) for l in open(BENCH)]
    print(f"items: {len(items)}")

    cls = [len(reference_classes(it)[0]) + len(reference_classes(it)[1]) for it in items]
    print(f"distinct reference classes per item: min {min(cls)}, median {sorted(cls)[len(cls)//2]}, max {max(cls)}")
    print(f"items with >=2 classes (swappable): {sum(1 for c in cls if c >= 2)}/{len(items)}")
    print(f"items with a canonical reference   : {sum(1 for it in items if reference_classes(it)[0])}/{len(items)}")

    origin = collections.Counter()
    for it in items:
        for _, lab in sample_single(it, args.trials):
            origin[lab] += 1
    tot = sum(origin.values())
    print(f"\nC1 single references over all items x {args.trials} trials: {dict(origin)}")
    print(f"  canonical share {origin['canonical']/tot:.1%}  (uniform sampling would give ~1/7 = 14.3%)")

    pos = collections.Counter()
    bad = 0
    for it in items:
        for r1, r2, lab in sample_pairs(it, args.pairs):
            pos[lab] += 1
            if r1["normalized_answer_id"] == r2["normalized_answer_id"]:
                bad += 1
    print(f"\nP1 pairs: {dict(pos)}")
    print(f"  pairs whose two references are the SAME class (must be 0): {bad}")
    det = sample_single(items[0], 4) == sample_single(items[0], 4)
    print(f"\ndeterministic for a fixed seed: {det}")
