# Build reference-variant pools for the masking-and-identity mechanistic suite
# (P-MS1..P-MS3, registered in papers/analysis/maskident_analysis.py, committed together
# with this file BEFORE any variant judging runs).
#
# Three variants, changing ONLY the reference string the judge sees:
#   refword  (replication pool): every integer in ref_answer rendered as English words
#            ("31" -> "thirty-one"; lists element-wise, joined ", "). Semantically the
#            identical answer, lexically disjoint from every candidate's numerals.
#   refexpr  (replication pool): every integer n rendered as "{n-1}+1" ("31" -> "30+1").
#            Semantically identical, equality now requires one computation step.
#   masked worked refs (k-stratified pool, cond refsol): kstrat_worked_refs.jsonl with the
#            final answer hidden. Pinned masking: boxed content replaced by "hidden"; for
#            scalar families (crt, divcount, digitsum) every word-boundary occurrence of
#            the answer integer in sol_a is replaced by "(hidden)"; for list families
#            (subset, goldbach) every occurrence of the full list string is replaced (the
#            derivation may still name elements individually — disclosed; the registered
#            P-MS3 therefore scores scalar families only).
#
# Outputs:
#   runs/bon/bon_replword__meta-llama__Llama-3.1-8B-Instruct.jsonl
#   runs/bon/bon_replexpr__meta-llama__Llama-3.1-8B-Instruct.jsonl
#   runs/kstrat_worked_refs_masked.jsonl
import json
import re

ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
        "fourteen fifteen sixteen seventeen eighteen nineteen").split()
TENS = "zero ten twenty thirty forty fifty sixty seventy eighty ninety".split()


def words(n):
    n = int(n)
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else "-" + ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + words(n % 100))
    if n < 1000000:
        return words(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + words(n % 1000))
    raise ValueError(n)


def per_int(ref, f):
    return ", ".join(f(x.strip()) for x in ref.split(","))


SRC = "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"
rows = [json.loads(l) for l in open(SRC)]
for tag, f in (("replword", lambda x: words(x)),
               ("replexpr", lambda x: f"{int(x)-1}+1")):
    with open(f"runs/bon/bon_{tag}__meta-llama__Llama-3.1-8B-Instruct.jsonl", "w") as out:
        for r in rows:
            q = dict(r)
            q["ref_answer_orig"] = r["ref_answer"]
            q["ref_answer"] = per_int(r["ref_answer"], f)
            out.write(json.dumps(q) + "\n")
    print(f"[build_refvariant_pools] {tag}: {len(rows)} items")

SCALAR_FAMS = {"crt", "divcount", "digitsum"}
n_masked = 0
with open("runs/kstrat_worked_refs_masked.jsonl", "w") as out:
    for l in open("runs/kstrat_worked_refs.jsonl"):
        t = json.loads(l)
        ref = t["ref_answer"]
        sol = t["sol_a"]
        sol = re.sub(r"\\boxed\{[^}]*\}", r"\\boxed{hidden}", sol)
        if t["family"] in SCALAR_FAMS:
            sol = re.sub(rf"\b{re.escape(ref)}\b", "(hidden)", sol)
        else:
            sol = sol.replace(ref, "(hidden)")
        t["sol_a"] = sol
        t["sol_b"] = sol  # cond refsol reads sol_a only; keep b identical for safety
        out.write(json.dumps(t) + "\n")
        n_masked += 1
print(f"[build_refvariant_pools] masked worked refs: {n_masked}")
