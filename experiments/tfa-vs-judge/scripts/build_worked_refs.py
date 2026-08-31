# Worked-reference construction for the E1 / H-METHOD pair (Paper D follow-up).
# INTERNAL REGISTRATION (construction half): this file, the generated
# runs/kstrat_worked_refs.jsonl, the bon_judge.py refsol/refsol2 conditions, and the frozen
# producer papers/analysis/worked_ref_analysis.py are committed BEFORE any refsol/refsol2
# judge score exists; the commit timestamp is the registration (no OSF post per current
# hold). The registered predictions P-W1/P-W2/P-W3 live in the producer's header.
#
# Motivation. Every reference-condition result in Paper D shows the judge a BARE answer
# string ("31") as the reference. Practitioners hand judges a worked solution. Two questions
# follow, and both are answered by re-judging the FROZEN 64-sample kstrat pools — no new
# generation, so the samples cannot adapt to the manipulation:
#   E1 (worked-reference arm): does a worked reference anchor MORE than a bare answer (more
#      surface for the judge to match on) or LESS (more information about the problem)?
#   H-METHOD (method rotation): on the 15 k=1 items there is exactly ONE valid answer, so
#      every oracle-valid sample carries the SAME final answer. Rotating the reference from
#      derivation route A to route B therefore holds answer-matching constant BY
#      CONSTRUCTION, and any score movement is pure METHOD anchoring. This is the paper's
#      answer-rotation experiment run in method space.
#
# What this file builds. For every one of the 75 k-stratified items (runs/kstrat_tasks.jsonl)
# it emits TWO short templated worked derivations, sol_a and sol_b, that BOTH end in the
# item's own ref_answer by visibly different routes — no model in the loop, so every
# reference is auditable and reproducible from this file alone:
#   crt       A combine the congruences modulo m*n and read the arithmetic chain
#             B list the residue class mod n across the range and filter it by the mod-m test
#   subset    A add the chosen elements in a descending running total
#             B complement: the full set sums to S, so drop the elements totalling S - target
#   goldbach  A scan primes p upward, testing whether N - p is prime
#             B scan primes q downward from N, testing whether N - q is prime
#   divcount  A prime factorization and the (e1+1)(e2+1)... divisor-count formula
#             B list the divisors outright after rejecting a nearby in-range candidate
#   digitsum  A scan the multiples of q in the d-digit range, summing digits
#             B digit-first: choose d digits summing to s, then divide by q to verify
# The routes are lifted from the derivation templates of build_simcorr_candidates.py
# (valid_near = method A, valid_far = method B). ADAPTATION: simcorr's valid_far deliberately
# lands on a DIFFERENT valid answer for k > 1 items; here both routes must land on the SAME
# answer (the item's ref_answer), because holding the answer fixed is the whole point of
# H-METHOD, so every B route is re-pointed at ref_answer and its rejection lines are chosen
# to fall strictly before ref_answer along the B scan order.
#
# Hard rules asserted below, per item (hard-fail, no silent skipping):
#   - the extracted \boxed answer of BOTH derivations equals the item's ref_answer, and both
#     pass the family oracle (checker code lifted verbatim from repl_oracle.py, per the
#     project rule that the math is never reimplemented);
#   - the two derivations differ substantially: token-level Jaccard < 0.6;
#   - the length ratio max(len)/min(len) between sol_a and sol_b is <= 1.6 (neutral filler
#     sentences are inserted before the \boxed line of the shorter text to equalize; they
#     never touch the math), so a length confound cannot masquerade as a method effect.
# Deterministic: SEED fixes the filler rotation; there is no sampling anywhere.
# Output: runs/kstrat_worked_refs.jsonl, one row per item:
#   problem_id, ref_answer, sol_a, sol_b, family (+ method_a/method_b labels, lengths,
#   length_ratio, jaccard for audit).
# Run from experiments/tfa-vs-judge:  python3 scripts/build_worked_refs.py
import ast
import json
import os
import random
import re
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260831
TASKS = "runs/kstrat_tasks.jsonl"
OUT = "runs/kstrat_worked_refs.jsonl"
MAX_JACCARD = 0.6
MAX_LEN_RATIO = 1.6
FILLERS = [
    "A quick re-check against the problem statement confirms this choice.",
    "Re-reading the problem, every stated requirement has been addressed above.",
    "No further conditions remain to check, so this settles the problem.",
]

# reuse the frozen checker verbatim: lift only the function defs out of repl_oracle.py
# (importing the module would fire its argparse/pool-rewrite main path)
_ns = {}
for _node in ast.parse(open(os.path.join(HERE, "repl_oracle.py")).read()).body:
    if isinstance(_node, (ast.Import, ast.ImportFrom, ast.FunctionDef)):
        exec(compile(ast.Module(body=[_node], type_ignores=[]), "repl_oracle.py", "exec"), _ns)
valid, extract_boxed = _ns["valid"], _ns["extract_boxed"]
is_prime, ndiv = _ns["is_prime"], _ns["ndiv"]

METHODS = {
    "crt": ("combine-congruences-mod-mn", "list-residue-class-and-filter"),
    "subset": ("running-total-of-chosen-elements", "complement-of-the-left-out-elements"),
    "goldbach": ("scan-primes-upward", "scan-primes-downward-from-N"),
    "divcount": ("prime-factorization-divisor-formula", "list-divisors-outright"),
    "digitsum": ("scan-multiples-summing-digits", "digit-first-then-divide"),
}


def bx(a):
    return "\\boxed{" + str(a) + "}"


def dsum(x):
    return sum(int(c) for c in str(x))


def dstr(x):
    return "+".join(str(x))


def toks(t):
    return set(re.findall(r"[a-z]+|\d+", t.lower()))


def jaccard(x, y):
    a, b = toks(x), toks(y)
    return len(a & b) / max(len(a | b), 1)


def elide(seq, n):
    return ", ".join(str(x) for x in seq[:n]) + (", ..." if len(seq) > n else "")


def factor(x):
    fs, d = [], 2
    while d * d <= x:
        e = 0
        while x % d == 0:
            x //= d
            e += 1
        if e:
            fs.append((d, e))
        d += 1
    if x > 1:
        fs.append((x, 1))
    return fs


def divisors(x):
    return [i for i in range(1, x + 1) if x % i == 0]


def refs_crt(p, ref):
    m, n, a, b, lo, hi = p["m"], p["n"], p["a"], p["b"], p["lo"], p["hi"]
    r = int(ref)
    M = m * n
    first = lo + ((r - lo) % M)
    chain = list(range(first, hi + 1, M))
    modn = [x for x in range(lo, hi + 1) if x % n == b]
    rej = [x for x in modn if x < r and x % m != a][:2]
    rejtxt = "".join(f"{x} mod {m} = {x % m}, rejected; " for x in rej)
    cont = "continuing down the list, " if rej else ""
    sol_a = (
        f"The two requirements are x ≡ {a} (mod {m}) and x ≡ {b} (mod {n}). Since {m} and "
        f"{n} are coprime, they collapse into a single condition modulo {m}*{n} = {M}: "
        f"adding {M} to any solution preserves both remainders. So the solutions inside "
        f"[{lo}, {hi}] form the arithmetic chain {elide(chain, 4)}. Take x = {r} from that "
        f"chain: {r} = {m}*{r // m} + {a} and {r} = {n}*{r // n} + {b}, and "
        f"{lo} <= {r} <= {hi}. {bx(r)}")
    sol_b = (
        f"Handle the conditions one at a time by listing. The values in [{lo}, {hi}] that "
        f"leave remainder {b} on division by {n} are {elide(modn, 5)}. Now walk along that "
        f"list from the bottom applying the other test, division by {m}: {rejtxt}{cont}"
        f"{r} mod {m} = {a}, which is exactly what was asked. Both conditions hold for "
        f"x = {r}, and it lies in the given interval. {bx(r)}")
    return sol_a, sol_b


def refs_subset(p, ref):
    vals, target = p["vals"], p["target"]
    R = sorted((int(x) for x in ref.split(",")), reverse=True)
    S = sum(vals)
    removed = sorted(v for v in vals if v not in R)
    assert removed, "complement route needs at least one left-out element"
    assert sum(removed) == S - target
    parts, s = [], R[0]
    prev = s
    for v in R[1:]:
        s += v
        parts.append(f"{prev} + {v} = {s}")
        prev = s
    chain = ", ".join(parts) if parts else f"the single value {R[0]}"
    sol_a = (
        f"Work forward from the largest usable values and keep a running total. Choosing "
        f"{', '.join(map(str, R))} and adding them in turn: {chain} — landing exactly on the "
        f"target {target}. Every element used comes from the given set and is used once. "
        f"{bx(','.join(str(x) for x in sorted(R)))}")
    sol_b = (
        f"Go through the elements that are left out instead. The whole set "
        f"{{{', '.join(map(str, vals))}}} totals {S}, so a subset hits {target} exactly when "
        f"the discarded elements total {S} - {target} = {S - target}. Discarding "
        f"{', '.join(map(str, removed))} removes precisely {S - target}, so whatever remains "
        f"must total {target}: that leftover subset is "
        f"{', '.join(str(x) for x in sorted(R))}. {bx(','.join(str(x) for x in sorted(R)))}")
    return sol_a, sol_b


def refs_goldbach(p, ref):
    N = p["N"]
    rp, rq = (int(x) for x in ref.split(","))

    def sfac(c):
        return next(i for i in range(2, c + 1) if c % i == 0)

    def comptxt(c):
        return f"{c} = {sfac(c)}*{c // sfac(c)}, composite"

    up = [x for x in range(2, rp) if is_prime(x) and not is_prime(N - x)][:2]
    uptxt = " ".join(f"p = {x}: {N} - {x} = {N - x}, and {comptxt(N - x)}." for x in up)
    down = [q for q in range(N - 1, rq, -1)
            if is_prime(q) and N - q > 1 and not is_prime(N - q)][:2]
    downtxt = " ".join(f"q = {q}: {N} - {q} = {N - q}, and {comptxt(N - q)}." for q in down)
    sol_a = (
        f"Scan the primes p upward from the bottom and test whether the complement "
        f"{N} - p is prime as well. " + (uptxt + " " if uptxt else "")
        + f"p = {rp}: {N} - {rp} = {rq}, which is prime. So {rp} and {rq} are distinct "
        f"primes with {rp} < {rq} and {rp} + {rq} = {N}. {bx(f'{rp},{rq}')}")
    sol_b = (
        f"Come at the split from the large side: take the biggest prime q below {N} whose "
        f"complement is also prime, working downward. " + (downtxt + " " if downtxt else "")
        + f"q = {rq}: {N} - {rq} = {rp}, which is prime. The larger prime is therefore "
        f"{rq} and its partner is {rp}, two distinct primes summing to {N}. "
        f"{bx(f'{rp},{rq}')}")
    return sol_a, sol_b


def refs_divcount(p, ref):
    lo, hi, k = p["lo"], p["hi"], p["k"]
    r = int(ref)
    fs = factor(r)
    facstr = " * ".join(f"{q}^{e}" if e > 1 else f"{q}" for q, e in fs)
    prodstr = " * ".join(f"({e}+1)" for _, e in fs)
    prodval = (" * ".join(str(e + 1) for _, e in fs) + " = ") if len(fs) > 1 else ""
    ds = divisors(r)
    assert len(ds) == k
    rej = [y for y in range(lo, hi + 1) if y < r and ndiv(y) != k][-1:]
    rejtxt = ""
    if rej:
        y = rej[0]
        dy = divisors(y)
        rejtxt = (f"{y}: divisors {elide(dy, 5)} — {len(dy)} of them, not {k}. ")
    sol_a = (
        f"The divisor count of x is fixed by its prime factorization: if "
        f"x = p1^e1 * p2^e2 * ... then x has ({'e1+1'})({'e2+1'})... divisors. Factor "
        f"candidates in [{lo}, {hi}] and look for the count {k}. Here {r} = {facstr}, so its "
        f"divisor count is {prodstr} = {prodval}{k}, and {lo} <= {r} <= {hi}. {bx(r)}")
    sol_b = (
        f"Walk through the range listing divisors outright. {rejtxt}{r}: divisors "
        f"{', '.join(map(str, ds))} — exactly {k} of them, which is the count required, and "
        f"{r} sits inside [{lo}, {hi}]. {bx(r)}")
    return sol_a, sol_b


def refs_digitsum(p, ref):
    d, q, s = p["d"], p["q"], p["s"]
    r = int(ref)
    lo, hi = 10 ** (d - 1), 10 ** d - 1
    mults = [x for x in range(lo, hi + 1) if x % q == 0]
    rej = [x for x in mults if x < r and dsum(x) != s][-2:]
    rejtxt = "".join(f"{x}: digits {dstr(x)} = {dsum(x)}, no. " for x in rej)
    sol_a = (
        f"Run through the multiples of {q} inside the {d}-digit range and add up the digits "
        f"of each one as we go. {rejtxt}{r}: digits {dstr(r)} = {s}, which is the required "
        f"sum. So {r} is a {d}-digit multiple of {q} with digit sum {s}. {bx(r)}")
    sol_b = (
        f"Build the digits before the number. We need {d} digits adding to {s}; take "
        f"{', '.join(str(r))}, since {dstr(r)} = {s}, which spells the {d}-digit number {r}. "
        f"Now check the other condition by dividing: {r} = {q}*{r // q}, so {r} is a multiple "
        f"of {q} with no remainder. Both requirements are met. {bx(r)}")
    return sol_a, sol_b


FAM_FN = dict(crt=refs_crt, subset=refs_subset, goldbach=refs_goldbach,
              divcount=refs_divcount, digitsum=refs_digitsum)

rng = random.Random(SEED)
rows = [json.loads(l) for l in open(TASKS)]
out_rows = []
for row in rows:
    fam = row["params"]["fam"]
    sol_a, sol_b = FAM_FN[fam](row["params"], row["ref_answer"])
    # equalize lengths with neutral filler before the \boxed line of the shorter derivation
    fi = rng.randrange(len(FILLERS))
    for _ in range(30):
        La, Lb = len(sol_a), len(sol_b)
        if max(La, Lb) / min(La, Lb) <= 1.5:
            break
        pad = FILLERS[fi % len(FILLERS)] + " "
        fi += 1
        if La < Lb:
            bp = sol_a.rfind("\\boxed")
            sol_a = sol_a[:bp] + pad + sol_a[bp:]
        else:
            bp = sol_b.rfind("\\boxed")
            sol_b = sol_b[:bp] + pad + sol_b[bp:]
    La, Lb = len(sol_a), len(sol_b)
    ratio = max(La, Lb) / min(La, Lb)
    jac = jaccard(sol_a, sol_b)
    pid = row["problem_id"]
    for tag, txt in (("sol_a", sol_a), ("sol_b", sol_b)):
        got = extract_boxed(txt)
        assert got == row["ref_answer"], f"{pid} {tag}: boxed {got!r} != ref {row['ref_answer']!r}"
        assert valid(row["params"], got), f"{pid} {tag}: oracle rejects {got!r}"
    assert jac < MAX_JACCARD, f"{pid}: derivations too similar, jaccard {jac:.3f}"
    assert ratio <= MAX_LEN_RATIO, f"{pid}: length ratio {ratio:.2f}"
    ma, mb = METHODS[fam]
    out_rows.append(dict(problem_id=pid, ref_answer=row["ref_answer"], sol_a=sol_a, sol_b=sol_b,
                         family=fam, k=row["k"], method_a=ma, method_b=mb,
                         lengths=[La, Lb], length_ratio=round(ratio, 3),
                         jaccard=round(jac, 3)))

with open(OUT, "w") as f:
    for r in out_rows:
        f.write(json.dumps(r) + "\n")

fams = Counter(r["family"] for r in out_rows)
ks = Counter(r["k"] for r in out_rows)
jacs = [r["jaccard"] for r in out_rows]
ratios = [r["length_ratio"] for r in out_rows]
lens = [x for r in out_rows for x in r["lengths"]]
print(f"[worked refs] wrote {len(out_rows)} items -> {OUT}")
print(f"  per family: {dict(fams)}")
print(f"  per k: {dict(sorted(ks.items()))}   (k=1 items drive H-METHOD: {ks[1]})")
print(f"  jaccard(sol_a, sol_b): mean {statistics.mean(jacs):.3f} max {max(jacs):.3f} "
      f"(band < {MAX_JACCARD} asserted)")
print(f"  length ratio: mean {statistics.mean(ratios):.3f} max {max(ratios):.3f} "
      f"(band <= {MAX_LEN_RATIO} asserted)")
print(f"  derivation chars: mean {statistics.mean(lens):.0f} min {min(lens)} max {max(lens)}")
print("  all assertions passed: both derivations box the item's ref_answer, both pass the "
      "family oracle, jaccard band, length band")
