# Programmatic checkers for MathRefBench's math_constraint items.
#
# Why this exists. The benchmark ships an answer BANK, but the bank is a sample: 1,874 of 2,198
# stored solutions have origin "generated", and 306 of 324 items carry exactly 7 of them, which is
# a cap rather than the true number of valid answers. Scoring candidates by bank membership would
# therefore count a correct-but-unbanked answer as wrong -- exactly the error the paper is about.
# These checkers decide validity from the problem's own definition and original_parameters, so
# "correct but different from every shown reference" is decidable without any judge or bank.
#
# Each checker takes (answer_obj, params) and returns True / False / None (None = not checkable here).
# Answers are parsed from the boxed final answer; most families are flat integer lists.
#
# Run from experiments/tfa-vs-judge:  python scripts/v4_checkers.py     (prints coverage on the bank)
import json
import os
import re
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
BENCH = os.path.join(ROOT, "datasets/final_mathrefbench.jsonl")


# ---------------------------------------------------------------- parsing
def ints(a):
    """Flat list of integers from a list, nested list, or string."""
    if isinstance(a, (list, tuple)):
        out = []
        for x in a:
            out.extend(ints(x) or [])
        return out
    if isinstance(a, int):
        return [a]
    if isinstance(a, str):
        if "unsat" in a.lower():
            return None
        return [int(m) for m in re.findall(r"-?\d+", a)]
    return None


def pairs(a):
    """List of (u, v) edge pairs from a nested list or string."""
    if isinstance(a, (list, tuple)) and a and isinstance(a[0], (list, tuple)) and len(a[0]) == 2:
        return [(int(u), int(v)) for u, v in a]
    flat = ints(a)
    if flat is None or len(flat) % 2:
        return None
    return [(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]


# ---------------------------------------------------------------- graph helpers
def adj(n, edges):
    g = {i: set() for i in range(n)}
    for u, v in edges:
        if not (0 <= u < n and 0 <= v < n) or u == v:
            return None
        g[u].add(v); g[v].add(u)
    return g


def max_clique_size(g, n):
    best = 0
    def grow(cur, cand):
        nonlocal best
        if not cand:
            best = max(best, len(cur)); return
        if len(cur) + len(cand) <= best:
            return
        for v in sorted(cand):
            grow(cur + [v], {u for u in cand if u > v and u in g[v]})
    grow([], set(range(n)))
    return best


def max_independent_set_size(g, n):
    comp = {i: set(range(n)) - g[i] - {i} for i in range(n)}
    return max_clique_size(comp, n)


def chromatic_number(g, n):
    for k in range(1, n + 1):
        color = {}
        def ok(v, c):
            return all(color.get(u) != c for u in g[v])
        def go(i):
            if i == n:
                return True
            for c in range(k):
                if ok(i, c):
                    color[i] = c
                    if go(i + 1):
                        return True
                    del color[i]
            return False
        if go(0):
            return k
    return n


def girth(g, n):
    best = float("inf")
    from collections import deque
    for s in range(n):
        dist = {s: 0}; par = {s: None}; q = deque([s])
        while q:
            u = q.popleft()
            for w in g[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1; par[w] = u; q.append(w)
                elif w != par[u]:
                    best = min(best, dist[u] + dist[w] + 1)
    return best


def connectivity_at_least(g, n, k):
    """Vertex connectivity >= k, by brute force over small removal sets."""
    if n <= k:
        return False
    for r in range(k):
        for rem in combinations(range(n), r):
            keep = [v for v in range(n) if v not in rem]
            if not keep:
                return False
            seen = {keep[0]}; stack = [keep[0]]
            while stack:
                u = stack.pop()
                for w in g[u]:
                    if w not in rem and w not in seen:
                        seen.add(w); stack.append(w)
            if len(seen) != len(keep):
                return False
    return True


# ---------------------------------------------------------------- family checkers
def c_queens(a, p):
    n = p["n"]; x = ints(a)
    if x is None or len(x) != n or sorted(x) != list(range(n)):
        return False
    return all(abs(x[i] - x[j]) != abs(i - j) for i, j in combinations(range(n), 2))


def c_all_interval(a, p):
    n = p["n"]; x = ints(a)
    if x is None or sorted(x) != list(range(n)):
        return False
    d = sorted(abs(x[i + 1] - x[i]) for i in range(n - 1))
    return d == list(range(1, n))


def c_langford(a, p):
    n = p["n"]; x = ints(a)
    if x is None or len(x) != 2 * n or sorted(x) != sorted(list(range(1, n + 1)) * 2):
        return False
    for v in range(1, n + 1):
        i, j = [k for k, y in enumerate(x) if y == v]
        if j - i != v + 1:
            return False
    return True


def c_costas(a, p):
    n = p["n"]; x = ints(a)
    if x is None or len(x) != n or sorted(x) != list(range(n)):
        return False
    seen = set()
    for d in range(1, n):
        for c in range(n - d):
            v = (d, x[c + d] - x[c])
            if v in seen:
                return False
            seen.add(v)
    return True


def c_golomb(a, p):
    n = p["n"]; x = ints(a)
    if x is None or len(x) != n or x != sorted(x) or len(set(x)) != n:
        return False
    d = [b - a_ for a_, b in combinations(x, 2)]
    return len(set(d)) == len(d)


def c_knight(a, p):
    n = p["n"]; x = ints(a)
    side = int(round(n ** 0.5)) if n > 8 else n
    if x is None or sorted(x) != list(range(len(x))):
        return False
    side = int(round(len(x) ** 0.5))
    if side * side != len(x):
        return False
    for u, v in zip(x, x[1:]):
        dr, dc = abs(u // side - v // side), abs(u % side - v % side)
        if sorted((dr, dc)) != [1, 2]:
            return False
    return True


def c_debruijn(a, p):
    b, n = p["b"], p["n"]; x = ints(a)
    if x is None or len(x) != b ** n or any(not 0 <= v < b for v in x):
        return False
    seen = {tuple(x[(i + k) % len(x)] for k in range(n)) for i in range(len(x))}
    return len(seen) == b ** n


def c_quasigroup(a, p):
    n = p["n"]; x = ints(a)
    if x is None or len(x) != n * n:
        return False
    g = [x[i * n:(i + 1) * n] for i in range(n)]
    rows = all(sorted(r) == list(range(n)) for r in g)
    cols = all(sorted(col) == list(range(n)) for col in zip(*g))
    return rows and cols


def c_ortholatin(a, p):
    n = p["n"]; x = ints(a)
    if x is None or len(x) != 2 * n * n:
        return False
    X = [x[i * n:(i + 1) * n] for i in range(n)]
    Y = [x[n * n + i * n: n * n + (i + 1) * n] for i in range(n)]
    for g in (X, Y):
        if not all(sorted(r) == list(range(n)) for r in g):
            return False
        if not all(sorted(c) == list(range(n)) for c in zip(*g)):
            return False
    return len({(X[i][j], Y[i][j]) for i in range(n) for j in range(n)}) == n * n


def c_hadamard(a, p):
    """Legendre pair: each sequence sums to 1, and every cyclic autocorrelation pair sums to -2."""
    n = p["n"]; x = ints(a)
    if x is None or len(x) != 2 * n or any(v not in (-1, 1) for v in x):
        return False
    A, B = x[:n], x[n:]
    if sum(A) != 1 or sum(B) != 1:
        return False
    for s in range(1, (n + 1) // 2):
        if sum(A[i] * A[(i + s) % n] for i in range(n)) + sum(B[i] * B[(i + s) % n] for i in range(n)) != -2:
            return False
    return True


def c_antimagic(a, p):
    n = p["n"]; x = ints(a)
    if x is None or len(x) != n * n + 2 * n + 2:
        return False
    grid, sums = x[: n * n], x[n * n:]
    if sorted(grid) != list(range(1, n * n + 1)):
        return False
    g = [grid[i * n:(i + 1) * n] for i in range(n)]
    got = [sum(r) for r in g] + [sum(c) for c in zip(*g)]
    got += [sum(g[i][i] for i in range(n)), sum(g[i][n - 1 - i] for i in range(n))]
    if sorted(got) != sorted(sums):
        return False
    s = sorted(got)
    return s == list(range(s[0], s[0] + len(s)))


def c_ramsey(a, p):
    n, r, s = p["n"], p["r"], p["s"]; x = ints(a)
    e = list(combinations(range(n), 2))
    if x is None or len(x) != len(e):
        return False
    col = {pair: c for pair, c in zip(e, x)}
    def mono(size, want):
        for verts in combinations(range(n), size):
            if all(col[tuple(sorted(pq))] == want for pq in combinations(verts, 2)):
                return True
        return False
    return not mono(r, 0) and not mono(s, 1)


def c_social(a, p):
    g_size, n_groups, weeks = p["group_size"], p["n_groups"], p["n_weeks"]
    players = g_size * n_groups; x = ints(a)
    if x is None or len(x) != players * weeks:
        return False
    met = set()
    for w in range(weeks):
        assign = x[w * players:(w + 1) * players]
        if any(not 0 <= v < n_groups for v in assign):
            return False
        for gid in range(n_groups):
            grp = [pl for pl, v in enumerate(assign) if v == gid]
            if len(grp) != g_size:
                return False
            for pair in combinations(sorted(grp), 2):
                if pair in met:
                    return False
                met.add(pair)
    return True


def c_number(a, p):
    """Partition 1..n into k subsets with equal sums (target n(n+1)/2k)."""
    n, k = p["n"], p["k"]; x = ints(a)
    if x is None or len(x) != n or any(not 0 <= v < k for v in x):
        return False
    target, rem = divmod(n * (n + 1) // 2, k)
    if rem:
        return False
    return all(sum(i + 1 for i in range(n) if x[i] == part) == target for part in range(k))


def c_bibd(a, p):
    v, k, ld = p["v"], p["k"], p["ld"]
    b = ld * v * (v - 1) // (k * (k - 1)); r = ld * (v - 1) // (k - 1)
    x = ints(a)
    if x is None or len(x) != v * b or any(y not in (0, 1) for y in x):
        return False
    M = [x[i * b:(i + 1) * b] for i in range(v)]
    if any(sum(row) != r for row in M):
        return False
    if any(sum(col) != k for col in zip(*M)):
        return False
    return all(sum(M[i][j] * M[i2][j] for j in range(b)) == ld for i, i2 in combinations(range(v), 2))


def c_pysms(a, p):
    n = p["vertices"]; e = pairs(a)
    if e is None:
        return False
    e = [(min(u, v), max(u, v)) for u, v in e]
    if len(set(e)) != len(e):
        return False
    g = adj(n, e)
    if g is None:
        return False
    deg = [len(g[i]) for i in range(n)]
    checks = {
        "min_degree": lambda t: min(deg) >= t, "delta_low": lambda t: min(deg) >= t,
        "max_degree": lambda t: max(deg) <= t, "Delta_upp": lambda t: max(deg) <= t,
        "max_edges": lambda t: len(e) <= t, "min_edges": lambda t: len(e) >= t,
        "num_edges_upp": lambda t: len(e) <= t, "num_edges_low": lambda t: len(e) >= t,
        "max_clique": lambda t: max_clique_size(g, n) <= t,
        "max_independent_set": lambda t: max_independent_set_size(g, n) <= t,
        "min_chromatic_number": lambda t: chromatic_number(g, n) >= t,
        "max_chromatic_number": lambda t: chromatic_number(g, n) <= t,
        "min_girth": lambda t: girth(g, n) >= t,
        "min_connectivity": lambda t: connectivity_at_least(g, n, t),
    }
    for key, val in p.items():
        if key == "vertices":
            continue
        if key not in checks:
            return None                      # unknown constraint: do not claim a verdict
        if not checks[key](val):
            return False
    return True


CHECKERS = {
    "queens": c_queens, "all": c_all_interval, "langford": c_langford, "costas": c_costas,
    "golomb": c_golomb, "knight": c_knight, "debruijn": c_debruijn, "quasigroup": c_quasigroup,
    "ortholatin": c_ortholatin, "hadamard": c_hadamard, "antimagic": c_antimagic,
    "ramsey": c_ramsey, "social": c_social, "number": c_number, "bibd": c_bibd, "pysms": c_pysms,
}
# Families needing the generated instance (graph, partial grid) that original_parameters does not
# carry, so they stay bank-scored: graph (colouring), max (clique), latin, magic, graceful, low, non.


def family(row):
    return re.split(r"[_0-9]", row["problem_name"])[0]


def check(row, answer):
    """True / False / None for a candidate answer to this item."""
    f = CHECKERS.get(family(row))
    if f is None or not row["question_id"].startswith("math_constraint"):
        return None
    try:
        return f(answer, row["original_parameters"])
    except Exception:
        return None


if __name__ == "__main__":
    rows = [json.loads(l) for l in open(BENCH)]
    import collections
    cov = collections.Counter(); wrong = collections.Counter(); tot = collections.Counter()
    for r in rows:
        fam = family(r)
        for s in r["solutions"]:
            v = check(r, s["answer"])
            tot[fam] += 1
            if v is None:
                cov["unchecked"] += 1
            elif v:
                cov["verified"] += 1
            else:
                cov["FAILED"] += 1; wrong[fam] += 1
    items_checkable = sum(1 for r in rows if CHECKERS.get(family(r)) and r["question_id"].startswith("math_constraint"))
    print(f"items with a checker: {items_checkable} of {len(rows)}")
    print(f"bank solutions: verified {cov['verified']}, failed {cov['FAILED']}, unchecked {cov['unchecked']}")
    if wrong:
        print("families with failures (checker bug or bad bank entry):")
        for f, c in wrong.most_common():
            print(f"   {c:4d} / {tot[f]:4d}  {f}")
