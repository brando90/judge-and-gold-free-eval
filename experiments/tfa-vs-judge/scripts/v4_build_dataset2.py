# Assemble Dataset 2 (Pool B): the hard-item companion to Dataset 1.
#
#   python scripts/v4_rescore.py --in runs/v4_pool/gpt-5.6-sol.jsonl --out runs/v4_pool/poolb_scored.jsonl
#   python scripts/v4_build_dataset2.py --pool runs/v4_pool/poolb_scored.jsonl --out runs/v4_pool/dataset2.jsonl
#
# WHY A SECOND DATASET RATHER THAN A BIGGER FIRST ONE
# ---------------------------------------------------
# Dataset 1 (gpt-4.1-mini, 64 draws) leaves 161 of 317 items unusable: 140 where it never produced a
# valid answer and 21 where it produced only one distinct answer. Those are not bad items -- they are
# the HARD ones, and they are where the paper's effect should be strongest, because a judge that
# cannot solve the problem itself has no choice but to lean on the reference it was shown.
#
# Recovering them needs a stronger generator (gpt-5.6-sol: 79% valid per draw on these items, vs
# gpt-4.1-mini's 0%). That makes generator identity differ between the two pools, so they are kept as
# SEPARATE DATASETS and never merged. Within-pool comparisons stay clean; a cross-pool comparison
# would confound item difficulty with generator identity, which is exactly the kind of silent
# confound this paper is about.
#
# SELECTION RULE
# --------------
# An item is usable when it has >=2 DISTINCT valid candidate answers. Two valid answers that happen
# to be the same string are one answer, and the swap test needs two genuinely different correct
# answers to swap between.
import argparse
import collections
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))


def norm(a):
    """Format-insensitive answer key. MUST stay identical to the definitions in v4_generate.py and
    v4_rescore.py: if the three disagree about what counts as "the same answer", the pool becomes
    internally inconsistent with no trace of why."""
    nums = re.findall(r"-?\d+", str(a))
    if nums and not re.search(r"[a-zA-Z]{3,}", str(a)):
        return ",".join(nums)
    return re.sub(r"[\s\$]+", "", str(a)).strip().lower()

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True, help="scored candidate pool (output of v4_rescore.py)")
ap.add_argument("--bench", default=os.path.join(ROOT, "datasets/final_mathrefbench.jsonl"))
ap.add_argument("--dataset1", default="runs/v4_pool/final_scored.jsonl",
                help="Dataset 1 scored pool, used only to report overlap and combined coverage")
ap.add_argument("--case-c-pool", default=None,
                help="where invalid (case C) candidates come from. Defaults to --dataset1, which is "
                     "correct for Dataset 2: its strong generator is ~70%% valid and yields too few "
                     "wrong answers to measure false acceptance. When building DATASET 1 itself, "
                     "pass its own pool here so case C shares that dataset's generator.")
ap.add_argument("--out", default="runs/v4_pool/dataset2.jsonl")
ap.add_argument("--min-distinct", type=int, default=2)
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

bench = {r["question_id"]: r for r in (json.loads(l) for l in open(args.bench))}


def load(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # torn final line if a job was killed mid-write
    return rows


pool = [r for r in load(args.pool) if not r.get("error")]
by_item = collections.defaultdict(lambda: {"valid": {}, "invalid": [], "draws": 0})
for r in pool:
    d = by_item[r["question_id"]]
    d["draws"] += 1
    ans = r.get("answer")
    if r.get("valid") is True and ans is not None:
        # dict keyed by answer text: collapses repeats, keeps one exemplar per distinct answer
        d["valid"].setdefault(str(ans), r)
    elif r.get("valid") is False and ans is not None:
        d["invalid"].append(r)

usable = [q for q, d in by_item.items() if len(d["valid"]) >= args.min_distinct]
usable.sort()

# Case-C supply, drawn from the Dataset 1 pool for these same items (see the note at the candidate
# loop for why). Deduplicated by answer text: 64 draws of one wrong answer is one wrong answer.
case_c = collections.defaultdict(list)
_seen_c = collections.defaultdict(set)
for r in load(args.case_c_pool or args.dataset1):
    if r.get("error") or r.get("valid") is not False:
        continue
    q, a = r["question_id"], r.get("answer")
    if a is None or q not in by_item:
        continue
    if str(a) in _seen_c[q]:
        continue
    _seen_c[q].add(str(a))
    case_c[q].append(r)

records = []
for q in usable:
    d = by_item[q]
    item = bench.get(q)
    if item is None:
        continue
    # dedupe references by answer class: the bank can hold several rows of one answer, and showing
    # the "same" reference twice would quietly turn a swap trial into a no-op
    refs, seen = [], set()
    for s in item["solutions"]:
        k = s["normalized_answer_id"]
        if k in seen:
            continue
        seen.add(k)
        refs.append({"answer": s["answer"], "normalized_answer_id": k,
                     "origin": s.get("origin"), "canonical": s.get("origin") != "generated"})
    # Compare by NORMALISED answer, not raw string. Exact-string comparison finds 8 case-A answers
    # in this pool where the normalised comparison finds 177: "0,4,1,3,2" and "[0, 4, 1, 3, 2]" are
    # the same answer, and matching on the raw text scores formatting rather than correctness. This
    # is the same bug that was fixed once in the generator pilot and reintroduced here; it had me
    # reporting case A = 0 and concluding, wrongly, that Dataset 2 has no natural case A at all.
    bank_keys = {norm(s["answer"]) for s in item["solutions"]}
    cands = []
    for a, r in d["valid"].items():
        cands.append({"answer": a, "valid": True, "sample": r.get("sample"),
                      # case A = coincides with a stored reference, case B = correct but unbanked
                      # norm(a), not a: bank_keys holds NORMALISED keys, so testing the raw answer
                      # string against them matches only when the raw form is already normalised.
                      # That bug reported 8 case-A answers where there are 44. Third instance of
                      # formatting-vs-correctness in this pipeline, and like the others it silently
                      # reclassified correct answers instead of failing.
                      "case": "A" if norm(a) in bank_keys else "B",
                      "generator": r.get("model")})
    # Case C comes from the DATASET 1 pool, not from this one. The strong generator is ~77% valid
    # on these items, so it produces almost no wrong answers (11 across 46 items) -- too few to
    # measure false acceptance. Dataset 1 already holds 5,570 distinct invalid answers for these
    # exact 161 items, covering 161/161, median 36 each: genuine failures on these problems, at no
    # extra cost.
    #
    # Rejected alternative: perturbing valid answers into wrong ones. Corruption has failed a
    # prospective manipulation check TWICE in this project (Registration 6: 5 of 7 corrupt prompts
    # never moved their judge; Registration 7: 2 of 9 cells passed, one moved the WRONG way). And a
    # perturbed correct answer is minimally distant from a correct answer -- which is the very axis
    # this paper measures, so it is the one bias that would flatter our own claim.
    #
    # The cost is a declared confound: case A/B and case C have different authors. It is confined to
    # the false-acceptance metric; the A-vs-B comparison that carries the main claim is unaffected
    # because both come from the same generator. Every candidate records its `generator` so this is
    # visible in the data, not only in prose.
    for r in case_c.get(q, []):
        cands.append({"answer": r.get("answer"), "valid": False, "sample": r.get("sample"),
                      "case": "C", "generator": r.get("model")})
    records.append({"question_id": q, "problem_name": item.get("problem_name"),
                    "problem": item.get("problem"),
                    "formatting_instructions": item.get("formatting_instructions"),
                    "generator": pool[0].get("model") if pool else None,
                    "draws": d["draws"], "references": refs, "candidates": cands})

# Reporting: how much of the benchmark the two datasets cover together.
d1 = collections.defaultdict(set)
for r in load(args.dataset1):
    if not r.get("error") and r.get("valid") is True and r.get("answer") is not None:
        d1[r["question_id"]].add(str(r["answer"]))
d1_usable = {q for q, s in d1.items() if len(s) >= args.min_distinct}

nA = sum(1 for r in records for c in r["candidates"] if c["case"] == "A")
nB = sum(1 for r in records for c in r["candidates"] if c["case"] == "B")
nC = sum(1 for r in records for c in r["candidates"] if c["case"] == "C")

print(f"pool rows                     : {len(pool):,}")
print(f"items touched                 : {len(by_item)}")
print(f"items with >={args.min_distinct} distinct valid  : {len(usable)}   <- DATASET 2")
print(f"\ncandidates in Dataset 2:")
print(f"  case A (valid, banked)      : {nA:,}")
print(f"  case B (valid, unbanked)    : {nB:,}")
print(f"  case C (invalid)            : {nC:,}")
dv = [len(by_item[q]['valid']) for q in usable]
if dv:
    print(f"  distinct valid per item     : median {sorted(dv)[len(dv)//2]}, mean {sum(dv)/len(dv):.1f}, max {max(dv)}")
print(f"\ncombined coverage:")
print(f"  Dataset 1 usable items      : {len(d1_usable)}")
print(f"  Dataset 2 usable items      : {len(usable)}")
print(f"  overlap (should be 0)       : {len(d1_usable & set(usable))}")
print(f"  TOTAL of {len(bench)} benchmark items: {len(d1_usable | set(usable))} "
      f"({len(d1_usable | set(usable))/len(bench):.0%})")

if args.dry_run:
    print("\n(dry run, nothing written)")
else:
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"\nwrote {args.out}  ({len(records)} items)")
