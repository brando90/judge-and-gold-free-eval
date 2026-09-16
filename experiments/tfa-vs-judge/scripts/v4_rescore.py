# Re-score the v4 candidate pool offline, from each row's stored reply text.
#
#   python scripts/v4_rescore.py --in runs/v4_pool/gpt-4.1-mini-2025-04-14.jsonl
#
# Why this exists: generation is slow and costs real money, so the pool stores each model reply in
# full (`text`). Scoring is then a pure function of that text and can be redone for free whenever a
# checker changes -- no regeneration, and no need to stop a running job to fix a checker.
#
# It also makes the pool self-consistent. Rows written before and after the checker semantics fix
# (answer-level failure -> False, infrastructure failure -> None) would otherwise disagree; this
# pass re-derives every verdict with one version of the checkers.
#
# Writes a NEW file rather than editing in place, so the raw generation output stays untouched.
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, HERE)
import v4_checkers as C        # noqa: E402  189 math_constraint items, pure-Python predicates
import v4_mc_checkers as MC    # noqa: E402   67 mathconstruct items, upstream check()
import v4_csp_checkers as CSP  # noqa: E402   61 math_constraint items, upstream verify()

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True)
ap.add_argument("--out", default=None, help="default: <in>.scored.jsonl")
ap.add_argument("--bench", default=os.path.join(ROOT, "datasets/final_mathrefbench.jsonl"))
args = ap.parse_args()
out_path = args.out or args.inp.replace(".jsonl", "") + ".scored.jsonl"

bench = {r["question_id"]: r for r in (json.loads(l) for l in open(args.bench))}


def norm(a):
    """Format-insensitive key: compare answers by integer content when they have one."""
    nums = re.findall(r"-?\d+", str(a))
    if nums and not re.search(r"[a-zA-Z]{3,}", str(a)):
        return ",".join(nums)
    return re.sub(r"[\s\$]+", "", str(a)).strip().lower()


def extract(text):
    """Last <FINAL_ANSWER> tag, with or without a \\boxed{} wrapper inside it."""
    tags = re.findall(r"<FINAL_ANSWER>(.*?)</FINAL_ANSWER>", text, re.S)
    if tags:
        inner = tags[-1].strip()
        box = re.findall(r"\\boxed\{(.*)\}", inner, re.S)
        return (box[-1] if box else inner).strip()
    m = re.findall(r"\\boxed\{(.*?)\}", text, re.S)
    return m[-1].strip() if m else None


rows = []
torn = 0
for line in open(args.inp):
    try:
        rows.append(json.loads(line))
    except json.JSONDecodeError:
        torn += 1  # a killed run can leave one partial final line

changed = 0
reasons = collections.Counter()
cases = collections.Counter()

with open(out_path, "w") as f:
    for r in rows:
        if r.get("error"):
            f.write(json.dumps(r) + "\n")
            continue
        b = bench.get(r["question_id"])
        text = r.get("text") or ""
        ans = extract(text) if text else r.get("answer")

        # This must mirror v4_generate.py's scoring exactly. If the re-scorer and the generator
        # disagree about which checker owns an item, the pool becomes internally inconsistent --
        # worse than either being wrong on its own, because the disagreement is invisible.
        if b is None:
            v, why = None, "not_in_bench"
        elif not ans:
            v, why = False, "no_answer"
        elif r["question_id"].startswith("math_constraint"):
            v, why = C.check(b, ans, with_reason=True)
            if v is None:                 # our predicates miss it -> upstream solver fallback
                v, why = CSP.check(b, ans, with_reason=True)
        else:
            # Pass the full reply: upstream pulls the LAST \boxed{} out itself and needs that LaTeX.
            v, why = MC.check(b, ans, raw_text=text, with_reason=True)

        banked = bool(ans and b and norm(ans) in {norm(s["answer"]) for s in b["solutions"]})
        if r.get("valid") != v:
            changed += 1
        r.update(answer=ans, valid=v, reason=why, bank_match=banked)
        reasons[why] += 1
        cases["A_valid_banked" if (v and banked) else
              "B_valid_unbanked" if v else
              "C_invalid" if v is False else "undecided"] += 1
        f.write(json.dumps(r) + "\n")

print(f"rescored {len(rows)} rows -> {out_path}" + (f"  ({torn} torn line(s) skipped)" if torn else ""))
print(f"verdicts changed vs stored: {changed}")
print("reasons:", dict(reasons))
print("pool composition:")
tot_valid = cases["A_valid_banked"] + cases["B_valid_unbanked"]
for k in ("A_valid_banked", "B_valid_unbanked", "C_invalid", "undecided"):
    share = f"{cases[k]/tot_valid:.0%} of valid" if k.startswith(("A_", "B_")) and tot_valid else ""
    print(f"  {k:20s} {cases[k]:6d}  {share}")
