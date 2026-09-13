# Build the recoverability-cost dose-response pools (P-RC1..P-RC4, registered in
# papers/analysis/recoverability_analysis.py, committed together with this file and the
# bon_judge.py cipher1/cipher2/cipher3 conditions BEFORE any variant judging runs).
#
# Motivation. The separability continuum (sep_continuum_analysis.py) showed a CLIFF between
# short-token strata (scalar/pair/json) and program, but only four qualitatively different
# artifact types -- not a graded dose. External review (and this session's own broadening
# pass) asked for the actual dose-response: hold the artifact type fixed (a boxed integer,
# or comma-joined integers) and vary only how much work the judge must do to decode the
# REFERENCE before it can check a match, exactly the way build_refvariant_pools.py already
# varied refword (0 extra steps, semantic-not-lexical) and refexpr (1 step, one computation)
# -- this file adds three MORE steps, chained, on top of the same replication pool, so the
# same estimator (worked_ref_analysis / maskident_analysis's per-item anchoring margin,
# matching always defined against the ORIGINAL numeral) applies unchanged.
#
# Levels (0 = bare numeral, already scored as the "repl" ref condition; this file adds 1-3):
#   cipher1 : each digit of the numeral shifted up by 3 (mod 10)                    (1 step)
#   cipher2 : cipher1's digit string, then base64-encoded                          (2 steps)
#   cipher3 : cipher2's base64 string, then reversed character-by-character        (3 steps)
# The decode rule is stated explicitly in the judge prompt (scripts/bon_judge.py's
# CIPHER_RULE), mirroring refexpr's explicit "n-1+1": the manipulation is decode COST, not
# decode impossibility, which is what lets a monotonic dose-response distinguish "anchoring
# fades because it's expensive" from "anchoring fades because the judge literally cannot
# read it" (that second, all-or-nothing case is already covered by the existing masked-ref
# condition).
#
# Outputs:
#   runs/bon/bon_replcipher1__meta-llama__Llama-3.1-8B-Instruct.jsonl
#   runs/bon/bon_replcipher2__meta-llama__Llama-3.1-8B-Instruct.jsonl
#   runs/bon/bon_replcipher3__meta-llama__Llama-3.1-8B-Instruct.jsonl
import base64
import json

SRC = "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"
rows = [json.loads(l) for l in open(SRC)]

SHIFT = 3


def digit_shift(s):
    return "".join(str((int(c) + SHIFT) % 10) for c in s)


def digit_unshift(s):
    return "".join(str((int(c) - SHIFT) % 10) for c in s)


def cipher1(x):
    return digit_shift(x)


def cipher2(x):
    return base64.b64encode(digit_shift(x).encode()).decode()


def cipher3(x):
    return base64.b64encode(digit_shift(x).encode()).decode()[::-1]


def per_int(ref, f):
    return ", ".join(f(x.strip()) for x in ref.split(","))


for tag, f in (("replcipher1", cipher1), ("replcipher2", cipher2), ("replcipher3", cipher3)):
    with open(f"runs/bon/bon_{tag}__meta-llama__Llama-3.1-8B-Instruct.jsonl", "w") as out:
        for r in rows:
            q = dict(r)
            q["ref_answer_orig"] = r["ref_answer"]
            q["ref_answer"] = per_int(r["ref_answer"], f)
            out.write(json.dumps(q) + "\n")
    print(f"[build_recoverability_pool] {tag}: {len(rows)} items")

# Sanity check: each transform round-trips back to the original digit string via the
# INVERSE operations (shift down, base64-decode, un-reverse), so the manipulation
# genuinely preserves a checkable answer (no accidental information loss) and the
# judge-facing CIPHER_RULE in bon_judge.py describes a real, reversible procedure.
for r in rows:
    for x in r["ref_answer"].split(","):
        x = x.strip()
        s1 = digit_shift(x)
        assert digit_unshift(s1) == x, "cipher1 round-trip failed"
        s2 = base64.b64encode(s1.encode()).decode()
        assert digit_unshift(base64.b64decode(s2).decode()) == x, "cipher2 round-trip failed"
        s3 = s2[::-1]
        assert digit_unshift(base64.b64decode(s3[::-1]).decode()) == x, "cipher3 round-trip failed"
print("[build_recoverability_pool] round-trip sanity check passed for all items")
