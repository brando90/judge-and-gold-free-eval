# Validity oracle for the MACE pool. Two paths, matching the two substrate types:
#   entity domains (River, Language): loose-normalized membership in the shipped valid set,
#     the Ties-style checker, whose incompleteness is bounded by the pre-run enumeration audit
#     (River 2.3%, Language 8.1% absent-from-list) and whose errors fall on the NON-matching
#     side, shrinking measured margins rather than inflating them.
#   Math: exact computation over the stated kind and range; the shipped list is not consulted,
#     so this path has no label noise at all and serves as the control.
# Adds an "oracle" field in place, mirroring repl_oracle.py. CPU only.
import argparse
import json
import math
import re

from sympy import isprime

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--tasks", default="runs/mace_tasks.jsonl")
args = ap.parse_args()


def is_square(n):
    r = math.isqrt(n)
    return r * r == n


def is_cube(n):
    r = round(n ** (1 / 3))
    return any((r + d) ** 3 == n for d in (-1, 0, 1))


_F = set()
_a, _b = 0, 1
while _a < 10 ** 13:
    _F.add(_a)
    _a, _b = _b, _a + _b


def is_tri(n):
    m = math.isqrt(8 * n + 1)
    return m * m == 8 * n + 1


KIND = {"prime": isprime, "square": is_square, "cube": is_cube,
        "fibonacci": lambda n: n in _F, "triangular": is_tri}


def norm(a):
    return re.sub(r"[^a-z0-9]+", "", a.strip().casefold())


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open(args.tasks)}
rows = [json.loads(l) for l in open(args.pool)]
n_valid = n_tot = 0
for r in rows:
    t = tasks[r["problem_id"]]
    p = t["params"]
    oracle = []
    for s in r["samples"]:
        a = boxed(s)
        if a is None:
            a = s[-200:]  # same whole-reply fallback as the other pools
        ok = 0
        if p["domain"] == "Math":
            m = re.search(r"-?\d+", a.replace(",", ""))
            if m:
                n = int(m.group(0))
                ok = int(p["lo"] <= n <= p["hi"] and KIND[p["kind"]](n))
        else:
            na = norm(a)
            ok = int(any(na == norm(v) or (len(norm(v)) > 3 and norm(v) in na)
                         for v in t["valid_answers"]))
        oracle.append(ok)
    r["oracle"] = oracle
    n_valid += sum(oracle)
    n_tot += len(oracle)

with open(args.pool, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(f"[mace_oracle] {args.pool}: {len(rows)} items, pass rate {n_valid / max(n_tot,1):.3f}")
import collections
by = collections.defaultdict(list)
for r in rows:
    t = tasks[r["problem_id"]]
    by[(t["params"]["domain"], t["k"])].append(sum(r["oracle"]) / len(r["oracle"]))
for key in sorted(by):
    v = by[key]
    print(f"   {key[0]:9s} k={key[1]}: mean pass {sum(v)/len(v):.3f} ({len(v)} items)")
