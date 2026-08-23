# Task pool for Paper D's clean preregistered replication (OSF draft, registration 3).
# Design goals fixed before any model sees a task:
#  - Multi-valid tasks whose validity is PROGRAMMATICALLY verifiable from the answer alone
#    (no enumeration needed for checking), across five diverse constraint families.
#  - Harder than the saturated synthk grid (target: Llama-3.1-8B best-of-64 pass rates in
#    [0.2, 0.8]); a 20-item PILOT calibrates the difficulty mix and does not enter analysis.
#  - Reference = one valid answer sampled from the (enumerable) solution set.
# Families (all answers are integers or small integer tuples, boxed):
#  crt: x in [lo, hi] with x = a mod m and x = b mod n (m, n coprime; many solutions in range)
#  subset: a subset of a given multiset summing to a target (answer: the subset as a list)
#  goldbach: an ordered pair of distinct primes summing to an even N
#  divcount: an integer in [lo, hi] with exactly k divisors
#  digitsum: a d-digit multiple of q with digit sum s
import argparse
import json
import random


def primes_upto(n):
    s = [True] * (n + 1)
    s[0:2] = [False, False]
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = [False] * len(s[i * i::i])
    return [i for i, b in enumerate(s) if b]


PRIMES = primes_upto(20000)
PSET = set(PRIMES)


def ndiv(x):
    c = 0
    i = 1
    while i * i <= x:
        if x % i == 0:
            c += 2 if i * i != x else 1
        i += 1
    return c


def gen_crt(rng, hard):
    while True:
        m, n = rng.choice([2, 3]), rng.choice([3, 4, 5])
        if m == n or __import__("math").gcd(m, n) != 1:
            continue
        a, b = rng.randrange(m), rng.randrange(n)
        span = (30, 90) if hard else (10, 60)
        lo = rng.randrange(*span)
        hi = lo + (m * n * (3 if hard else 5))
        sols = [x for x in range(lo, hi + 1) if x % m == a and x % n == b]
        if 2 <= len(sols) <= 8:
            q = (f"Give one integer x with {lo} <= x <= {hi} such that x leaves remainder "
                 f"{a} when divided by {m} and remainder {b} when divided by {n}.")
            return q, dict(fam="crt", lo=lo, hi=hi, m=m, a=a, n=n, b=b), [str(s) for s in sols]


def gen_subset(rng, hard):
    while True:
        k = 7 if hard else 6
        vals = sorted(rng.sample(range(3, 60 if hard else 40), k))
        target = sum(rng.sample(vals, rng.randrange(3, 5)))
        sols = []
        for mask in range(1, 1 << k):
            sub = [vals[i] for i in range(k) if mask >> i & 1]
            if sum(sub) == target:
                sols.append(",".join(map(str, sorted(sub))))
        if 2 <= len(sols) <= 10:
            q = (f"From the numbers {{{', '.join(map(str, vals))}}}, give one subset whose "
                 f"elements sum to exactly {target}. Write the subset as comma-separated "
                 f"numbers inside the box, for example \\boxed{{3,10,{target - 13}}}.")
            return q, dict(fam="subset", vals=vals, target=target), sols


def gen_goldbach(rng, hard):
    while True:
        N = rng.randrange(200, 800, 2) if hard else rng.randrange(40, 200, 2)
        pairs = []
        for p in PRIMES:
            if p >= N:
                break
            qq = N - p
            if qq in PSET and p < qq:
                pairs.append(f"{p},{qq}")
        if 2 <= len(pairs) <= (34 if hard else 24):
            q = (f"Give one pair of distinct primes p and q with p < q and p + q = {N}. "
                 f"Write the pair as p,q inside the box, for example \\boxed{{7,{N - 7}}}.")
            return q, dict(fam="goldbach", N=N), pairs


def gen_divcount(rng, hard):
    while True:
        k = rng.choice([4, 6] if hard else [2, 3])
        lo = rng.randrange(100, 500) if hard else rng.randrange(10, 80)
        hi = lo + (30 if hard else 20)
        sols = [str(x) for x in range(lo, hi + 1) if ndiv(x) == k]
        if 2 <= len(sols) <= 12:
            q = (f"Give one integer x with {lo} <= x <= {hi} that has exactly {k} positive "
                 f"divisors (including 1 and x).")
            return q, dict(fam="divcount", lo=lo, hi=hi, k=k), sols


def gen_digitsum(rng, hard):
    while True:
        d = 3 if hard else 2
        qq = rng.choice([7, 11] if hard else [2, 3, 5])
        s = rng.randrange(10, 20) if hard else rng.randrange(4, 13)
        lo, hi = 10 ** (d - 1), 10 ** d - 1
        sols = [str(x) for x in range(lo, hi + 1)
                if x % qq == 0 and sum(map(int, str(x))) == s]
        if 2 <= len(sols) <= 60:
            q = (f"Give one {d}-digit number that is divisible by {qq} and whose digits "
                 f"sum to {s}.")
            return q, dict(fam="digitsum", d=d, q=qq, s=s), sols


FAMS = [gen_crt, gen_subset, gen_goldbach, gen_divcount, gen_digitsum]


def build(rng, n, hard_frac, prefix):
    rows = []
    per = n // len(FAMS)
    for gi, gen in enumerate(FAMS):
        for j in range(per):
            hard = rng.random() < hard_frac
            if gen in (gen_crt, gen_divcount):
                hard = False
            q, params, sols = gen(rng, hard)
            ref = rng.choice(sols)
            rows.append(dict(problem_id=f"{prefix}/{params['fam']}-{gi * per + j}",
                             problem=q, params=params, hard=hard,
                             ref_answer=ref, n_solutions=len(sols),
                             valid_answers=sols if len(sols) <= 60 else sols[:60]))
    return rows


ap = argparse.ArgumentParser()
ap.add_argument("--hard-frac", type=float, default=0.5,
                help="fraction of hard-tier items (the pilot's calibration knob)")
ap.add_argument("--n-main", type=int, default=120)
ap.add_argument("--n-pilot", type=int, default=20)
args = ap.parse_args()

rng = random.Random(20260825)
pilot = build(rng, args.n_pilot, args.hard_frac, "pilot")
main = build(rng, args.n_main, args.hard_frac, "repl")
with open("runs/repl_pilot_tasks.jsonl", "w") as f:
    for r in pilot:
        f.write(json.dumps(r) + "\n")
with open("runs/repl_main_tasks.jsonl", "w") as f:
    for r in main:
        f.write(json.dumps(r) + "\n")
from collections import Counter
print("pilot:", len(pilot), dict(Counter(r["params"]["fam"] for r in pilot)))
print("main:", len(main), dict(Counter(r["params"]["fam"] for r in main)),
      "hard:", sum(r["hard"] for r in main))
