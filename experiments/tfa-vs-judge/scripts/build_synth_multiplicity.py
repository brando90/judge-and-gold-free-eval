# Synthetic enumerable-multiplicity tasks (registered pre-run; predictions P-S1..P-S5 below).
# Task families with EXACTLY k valid answers, k in {1,2,4,8,16}, programmatic oracle, so the
# unique-answer control (k=1) lives inside the same design and multiplicity is a dose.
#
# REGISTERED PREDICTIONS (committed before any generation or judging):
#  P-S1 (dose-response): the referenced judge's anchoring margin and its excess-gap penalty
#        relative to blind increase with k; at k=1 the reference HELPS (gap decreases).
#  P-S2 (mitigation A): adding the instruction "the reference is one valid answer among
#        possibly many; any correct answer deserves full credit" reduces the anchoring margin.
#  P-S3 (mitigation B): showing min(3,k) valid answers reduces the margin below single-ref.
#  P-S4 (cross-family judges): the k>1 inversion direction replicates for Llama-3.1-8B and
#        phi-4 judges (not only Qwen).
#  P-S5 (cross-family generator): the inversion direction replicates on a Llama-3.1-8B pool.
import json, random

rng = random.Random(20260824)


def primes_upto(n):
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = [False] * len(sieve[i * i::i])
    return [i for i, b in enumerate(sieve) if b]


PRIMES = primes_upto(4000)


def window_with_k_primes(k):
    for _ in range(4000):
        i = rng.randrange(0, len(PRIMES) - k - 1)
        lo = PRIMES[i] + 1 if k > 0 else 0
        # window (lo-1, hi+1) exclusive containing exactly PRIMES[i+1..i+k]
        a = PRIMES[i]
        b = PRIMES[i + k + 1]
        vals = [p for p in PRIMES if a < p < b]
        if len(vals) == k and b - a < 600:
            return a, b, vals
    return None


def divisors(n):
    return [d for d in range(2, n) if n % d == 0]


tasks = []
uid = 0
for k in (1, 2, 4, 8, 16):
    made = 0
    while made < 6:  # 6 prime-window tasks per k
        w = window_with_k_primes(k)
        if w is None:
            break
        a, b, vals = w
        tasks.append(dict(problem_id=f"synthk/prime-{uid}", k=k,
                          problem=f"Give one prime number p with {a} < p < {b}.",
                          valid_answers=[str(v) for v in vals]))
        uid += 1; made += 1
    made = 0
    tries = 0
    while made < 6 and tries < 20000:  # 6 divisor tasks per k
        tries += 1
        n = rng.randrange(20, 3000)
        dv = divisors(n)
        if len(dv) == k:
            tasks.append(dict(problem_id=f"synthk/div-{uid}", k=k,
                              problem=f"Give one divisor of {n} that is neither 1 nor {n}.",
                              valid_answers=[str(d) for d in dv]))
            uid += 1; made += 1

for t in tasks:
    t["ref_answer"] = rng.choice(t["valid_answers"])
    t["multi_refs"] = rng.sample(t["valid_answers"], min(3, len(t["valid_answers"])))
with open("runs/bon_synthk_tasks.jsonl", "w") as f:
    for t in tasks:
        f.write(json.dumps(t) + "\n")
from collections import Counter
print("tasks:", len(tasks), "per k:", dict(Counter(t["k"] for t in tasks)))
