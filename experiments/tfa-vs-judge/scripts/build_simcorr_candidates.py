# Candidate construction for the similarity-vs-correctness 2x2 (Paper D follow-up).
# INTERNAL REGISTRATION (construction half): this file, the generated task file, and the
# frozen analysis producer papers/analysis/simcorr_analysis.py are committed BEFORE any judge
# scores exist; the commit is the registration (no OSF post per current hold). The registered
# predictions P-SC1/P-SC2 live in the producer's header.
#
# Design. For 40 items (8 per constraint family) of the frozen replication pool
# runs/repl_main_tasks.jsonl, build four short, deterministic, templated worked solutions per
# item — no model in the loop, so every candidate is auditable:
#   valid_near   CORRECT; boxes the item's ref_answer via the family's canonical route
#   valid_far    CORRECT per the oracle; a DIFFERENT valid answer via a visibly different
#                derivation route (scan instead of congruence algebra, complement instead of
#                greedy, top-down instead of bottom-up, divisor listing instead of the
#                factor-count formula, digit-first instead of multiple-first)
#   invalid_near the canonical (reference-style) route with exactly ONE substantive slip
#                (wrong step size, arithmetic slip in the last addition, a false primality /
#                divisibility / digit-sum claim); FAILS the oracle
#   invalid_far  wrong AND structurally unrelated to the reference route; FAILS the oracle
# Hard rules asserted below, per item: oracle verdicts are exactly [1, 1, 0, 0] on the full
# candidate texts (checker code lifted verbatim from repl_oracle.py — not reimplemented);
# valid_far's boxed answer != ref_answer; the four boxed answers are pairwise distinct; the
# four candidate character lengths stay within a max/min ratio of 1.6 (neutral filler
# sentences are inserted before the \boxed line to equalize; they never touch the math).
# Output: runs/simcorr_tasks.jsonl, one row per item with the four texts in the fixed order
# [valid_near, valid_far, invalid_near, invalid_far] (= A, B, C, D in the analysis), their
# answers, oracle verdicts, lengths, and length_ratio. Rows carry problem/ref_answer/samples
# so bon_judge.py can consume them directly.
# Run from experiments/tfa-vs-judge:  python3 scripts/build_simcorr_candidates.py
import ast
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260827
N_PER_FAM = 8
TYPES = ["valid_near", "valid_far", "invalid_near", "invalid_far"]
FILLERS = [
    "A final re-check against the problem statement confirms the boxed value.",
    "Each requirement stated in the problem has been addressed in the steps above.",
    "No other conditions apply, so this settles the problem.",
]

# reuse the frozen checker verbatim: lift only the function defs out of repl_oracle.py
# (importing the module would fire its argparse/pool-rewrite main path)
_ns = {}
for _node in ast.parse(open(os.path.join(HERE, "repl_oracle.py")).read()).body:
    if isinstance(_node, (ast.Import, ast.ImportFrom, ast.FunctionDef)):
        exec(compile(ast.Module(body=[_node], type_ignores=[]), "repl_oracle.py", "exec"), _ns)
valid, extract_boxed = _ns["valid"], _ns["extract_boxed"]
is_prime, ndiv = _ns["is_prime"], _ns["ndiv"]


def bx(a):
    return "\\boxed{" + str(a) + "}"


def cands_crt(p, ref, valids):
    m, n, a, b, lo, hi = p["m"], p["n"], p["a"], p["b"], p["lo"], p["hi"]
    r = int(ref)
    M = m * n
    first = lo + ((r - lo) % M)
    chain = list(range(first, hi + 1, M))
    far = max((int(v) for v in valids if int(v) != r), key=lambda v: (abs(v - r), v))
    wrong = r + n if r + n <= hi else r - n
    assert lo <= wrong <= hi and not valid(p, str(wrong))
    modn = [x for x in range(lo, hi + 1) if x % n == b]
    rej = [x for x in modn if x % m != a][:2]
    assert rej and far in modn
    mid = (lo + hi) // 2
    bad = [x for x in modn if x % m != a and x != wrong]
    assert bad
    w2 = min(bad, key=lambda x: (abs(x - mid), x))
    texts = {
        "valid_near":
            f"We need x ≡ {a} (mod {m}) and x ≡ {b} (mod {n}). Since {m} and {n} are coprime, "
            f"the two congruences combine into one condition modulo {m}*{n} = {M}, and adding "
            f"{M} preserves both remainders, so the solutions in range are "
            f"{', '.join(map(str, chain[:4]))}{', ...' if len(chain) > 4 else ''}. Take "
            f"x = {r}: {r} = {m}*{r // m} + {a} and {r} = {n}*{r // n} + {b}, with "
            f"{lo} <= {r} <= {hi}. {bx(r)}",
        "valid_far":
            f"Work from the second condition directly: the numbers in [{lo}, {hi}] leaving "
            f"remainder {b} after division by {n} are {', '.join(map(str, modn[:5]))}"
            f"{', ...' if len(modn) > 5 else ''}. Test the first condition down this list: "
            f"{rej[0]} mod {m} = {rej[0] % m}, rejected"
            + (f"; {rej[1]} mod {m} = {rej[1] % m}, rejected" if len(rej) > 1 else "")
            + f"; but {far} mod {m} = {a}, as required. So x = {far} meets both conditions. "
            f"{bx(far)}",
        "invalid_near":
            f"We need x ≡ {a} (mod {m}) and x ≡ {b} (mod {n}). Since {m} and {n} are coprime, "
            f"the two congruences combine into one condition modulo {m}*{n} = {M}. The "
            f"solutions step by {n}, because adding {n} changes neither remainder; stepping "
            f"once from the solution {r} gives {wrong}, which lies in [{lo}, {hi}] and "
            f"satisfies both congruences. {bx(wrong)}",
        "invalid_far":
            f"Estimate from the middle: the midpoint of [{lo}, {hi}] is about {mid}. A number "
            f"close to it leaving remainder {b} after division by {n} is {w2}, and dividing "
            f"{w2} by {m} leaves remainder {a} as well, so both conditions are met and "
            f"x = {w2} is a valid choice. {bx(w2)}",
    }
    return texts, dict(valid_near=str(r), valid_far=str(far),
                       invalid_near=str(wrong), invalid_far=str(w2))


def cands_subset(p, ref, valids):
    vals, target = p["vals"], p["target"]
    R = sorted(int(x) for x in ref.split(","))
    others = [s for s in (sorted(int(x) for x in v.split(",")) for v in valids) if s != R]
    assert others
    far = max(others, key=lambda s: (len(set(s) ^ set(R)), s))
    S = sum(vals)
    x0 = min(R)
    unused = [v for v in vals if v not in R]
    assert unused
    y = min(unused, key=lambda v: (abs(v - x0), v))
    Rn = sorted([v for v in R if v != x0] + [y])
    assert sum(Rn) != target and not valid(p, ",".join(map(str, Rn)))
    srt = sorted(vals, key=lambda v: (abs(v - target / 3), v))
    W = None
    for j in range(2, len(srt)):
        c = sorted(srt[:2] + [srt[j]])
        if len(set(c)) == 3 and sum(c) != target and set(c) != set(Rn):
            W = c
            break
    assert W and not valid(p, ",".join(map(str, W)))

    def greedy(sub_desc, slip):
        steps, tot = [], 0
        for i, v in enumerate(sub_desc):
            tot += v
            if i == len(sub_desc) - 1 and slip:
                steps.append(f"then {v}, bringing the total to exactly {target}")
            else:
                steps.append((f"take {v}" if i == 0 else f"then {v}") + f" (total {tot})")
        return ", ".join(steps)

    removed = sorted(v for v in vals if v not in far)
    assert sum(removed) == S - target
    texts = {
        "valid_near":
            f"Build the subset from the largest useful values, tracking the running total: "
            f"{greedy(sorted(R, reverse=True), False)}, landing exactly on {target}. Every "
            f"element chosen is in the given set and used once. "
            f"{bx(','.join(map(str, R)))}",
        "valid_far":
            f"The full set {{{', '.join(map(str, vals))}}} sums to {S}. A subset totals "
            f"{target} exactly when the elements left out total {S} - {target} = "
            f"{S - target}. Leaving out {', '.join(map(str, removed))} removes exactly "
            f"{S - target}, so the remaining values {', '.join(map(str, far))} must sum to "
            f"{target}. {bx(','.join(map(str, far)))}",
        "invalid_near":
            f"Build the subset from the largest useful values, tracking the running total: "
            f"{greedy(sorted(Rn, reverse=True), True)}. Every element chosen is in the given "
            f"set and used once. {bx(','.join(map(str, Rn)))}",
        "invalid_far":
            f"Since three values averaging about {target}/3 ≈ {round(target / 3)} would do "
            f"it, take members of the set near that size: {', '.join(map(str, W))}. Adding "
            f"them up: {W[0]} + {W[1]} + {W[2]} = {target}, exactly the required total. "
            f"{bx(','.join(map(str, W)))}",
    }
    return texts, dict(valid_near=",".join(map(str, R)), valid_far=",".join(map(str, far)),
                       invalid_near=",".join(map(str, Rn)), invalid_far=",".join(map(str, W)))


def cands_goldbach(p, ref, valids):
    N = p["N"]
    rp, rq = (int(x) for x in ref.split(","))
    pairs = [tuple(int(x) for x in v.split(",")) for v in valids]

    def sfac(c):
        return next(i for i in range(2, c + 1) if c % i == 0)

    rej = [x for x in range(2, rp) if is_prime(x) and not is_prime(N - x)][:2]
    rejtxt = " ".join(f"p = {x}: {N} - {x} = {N - x} = {sfac(N - x)}*{(N - x) // sfac(N - x)}"
                      f", composite." for x in rej)
    p0 = next((x for x in range(2, N // 2 + 1) if is_prime(x) and not is_prime(N - x)
               and x not in rej and x != rp), None)
    assert p0
    c0 = N - p0
    assert not valid(p, f"{p0},{c0}")
    if pairs[0] != (rp, rq):
        pf, qf = pairs[0]
        route = "top"
    else:
        pf, qf = pairs[-1]
        route = "mid"
    assert (pf, qf) != (rp, rq)
    if route == "top":
        tr = [q2 for q2 in range(N - 1, qf, -1) if is_prime(q2) and not is_prime(N - q2)][:2]
        trtxt = " ".join(f"q = {q2}: {N} - {q2} = {N - q2}, not prime." for q2 in tr)
        far_text = (f"Come at it from the large side: find the biggest prime q below {N} "
                    f"whose complement is also prime. " + (trtxt + " " if trtxt else "")
                    + f"q = {qf}: {N} - {qf} = {pf}, which is prime. So p = {pf}, q = {qf}: "
                    f"both prime, {pf} < {qf}, and {pf} + {qf} = {N}. {bx(f'{pf},{qf}')}")
    else:
        far_text = (f"Look for a pair straddling the midpoint {N}/2 = {N // 2}. Checking "
                    f"numbers near it, {pf} is prime, and its partner {N} - {pf} = {qf} is "
                    f"prime as well, with {pf} < {qf}. Their sum is {N} by construction, so "
                    f"this pair qualifies. {bx(f'{pf},{qf}')}")
    got = None
    for x in range(N // 3, 1, -1):
        if is_prime(x):
            q3 = next((yy for yy in range(N - x - 1, x, -1) if is_prime(yy)), None)
            if q3 and x + q3 != N and (x, q3) != (p0, c0):
                got = (x, q3)
                break
    assert got
    p3, q3 = got
    assert not valid(p, f"{p3},{q3}")
    scan = f"Search upward through the primes p and test whether {N} - p is prime. "
    texts = {
        "valid_near":
            scan + (rejtxt + " " if rejtxt else "")
            + f"p = {rp}: {N} - {rp} = {rq}, which is prime. So {rp} and {rq} are distinct "
            f"primes with {rp} < {rq} and {rp} + {rq} = {N}. {bx(f'{rp},{rq}')}",
        "valid_far": far_text,
        "invalid_near":
            scan + (rejtxt + " " if rejtxt else "")
            + f"p = {p0}: {N} - {p0} = {c0}, which is prime. So {p0} and {c0} are distinct "
            f"primes with {p0} < {c0} and {p0} + {c0} = {N}. {bx(f'{p0},{c0}')}",
        "invalid_far":
            f"Split {N} as a small prime plus a large prime, taking the small one near "
            f"{N}/3: p = {p3} is prime, and on the large side q = {q3} is prime too. Then "
            f"p + q = {p3} + {q3} = {N}, as required, with p < q. {bx(f'{p3},{q3}')}",
    }
    return texts, dict(valid_near=f"{rp},{rq}", valid_far=f"{pf},{qf}",
                       invalid_near=f"{p0},{c0}", invalid_far=f"{p3},{q3}")


def cands_divcount(p, ref, valids):
    lo, hi, k = p["lo"], p["hi"], p["k"]
    r = int(ref)
    far = max((int(v) for v in valids if int(v) != r), key=lambda v: (abs(v - r), v))

    def divs(x):
        return [i for i in range(1, x + 1) if x % i == 0]

    def near_off(center, pred):
        for off in range(1, hi - lo + 1):
            for yy in (center - off, center + off):
                if lo <= yy <= hi and pred(yy):
                    return yy
        return None

    if k == 2:
        y = (near_off(r, lambda v: ndiv(v) != k and v % 2 == 1)
             or near_off(r, lambda v: ndiv(v) != k))
    else:
        y = near_off(r, lambda v: ndiv(v) != k)
    assert y and not valid(p, str(y))
    u = near_off(far, lambda v: ndiv(v) != k and v != y)
    assert u
    ud = divs(u)
    ushow = ", ".join(map(str, ud[:4])) + (", ..." if len(ud) > 4 else "")
    isq = int(round(r ** 0.5))
    if k == 2:
        sq = int(r ** 0.5)
        tp = [q for q in (2, 3, 5, 7, 11, 13) if q <= sq] or [2]
        checks = "; ".join(f"{r} = {q}*{r // q} + {r % q}" for q in tp)
        sqy = int(y ** 0.5)
        near_text = (f"A number has exactly 2 divisors precisely when it is prime. Test "
                     f"x = {r} by trial division up to sqrt({r}) ≈ {sq}: {checks}. No prime "
                     f"divides it, so the divisors of {r} are just 1 and {r} — exactly 2 — "
                     f"and {lo} <= {r} <= {hi}. {bx(r)}")
        inear_text = (f"A number has exactly 2 divisors precisely when it is prime. Test "
                      f"x = {y} by trial division up to sqrt({y}) ≈ {sqy}: every prime up to "
                      f"{sqy} leaves a nonzero remainder, so nothing smaller divides {y}. "
                      f"Its divisors are just 1 and {y} — exactly 2 — and "
                      f"{lo} <= {y} <= {hi}. {bx(y)}")
        fshow = f"1 and {far}"
    else:
        near_text = (f"Exactly 3 divisors forces x = p^2 for a prime p, since the divisors "
                     f"are then 1, p, p^2. Here {r} = {isq}^2 and {isq} is prime, so the "
                     f"divisors of {r} are 1, {isq}, {r} — exactly 3 — and {r} lies in "
                     f"[{lo}, {hi}]. {bx(r)}")
        inear_text = (f"Exactly 3 divisors forces x = p^2 for a prime p, since the divisors "
                      f"are then 1, p, p^2. Here {y} = {isq}^2 and {isq} is prime, so the "
                      f"divisors of {y} are 1, {isq}, {y} — exactly 3 — and {y} lies in "
                      f"[{lo}, {hi}]. {bx(y)}")
        fshow = f"1, {int(round(far ** 0.5))}, {far}"
    w = next(v for v in range(hi, lo - 1, -1) if ndiv(v) != k and v not in (y, u, far))
    assert not valid(p, str(w))
    if k == 2:
        fake = f"1 and {w}"
    else:
        f0 = next((i for i in range(2, int(w ** 0.5) + 1) if w % i == 0), None)
        fake = f"1, {f0 or int(round(w ** 0.5))}, {w}"
    texts = {
        "valid_near": near_text,
        "valid_far":
            f"Walk through the range listing divisors outright. {u}: divisors {ushow} — "
            f"{len(ud)} of them, not {k}. {far}: divisors {fshow} — exactly {k}. And "
            f"{lo} <= {far} <= {hi}, so x = {far} is a valid answer. {bx(far)}",
        "invalid_near": inear_text,
        "invalid_far":
            f"Walk down from the top of the range checking divisor counts. At x = {w} the "
            f"divisors come out to {fake} — exactly {k} of them — and {w} lies in "
            f"[{lo}, {hi}], so x = {w} works. {bx(w)}",
    }
    return texts, dict(valid_near=str(r), valid_far=str(far),
                       invalid_near=str(y), invalid_far=str(w))


def cands_digitsum(p, ref, valids):
    d, q, s = p["d"], p["q"], p["s"]
    r = int(ref)
    lo, hi = 10 ** (d - 1), 10 ** d - 1

    def ds(x):
        return sum(int(c) for c in str(x))

    def dstr(x):
        return "+".join(str(x))

    far = max((int(v) for v in valids if int(v) != r), key=lambda v: (abs(v - r), v))
    t = r // q
    y = None
    for off in range(1, hi):
        for yy in (r - off * q, r + off * q):
            if lo <= yy <= hi and ds(yy) != s:
                y = yy
                break
        if y:
            break
    assert y and y % q == 0 and not valid(p, str(y))
    rejm = None
    for jj in (t - 1, t + 1, t - 2, t + 2, t - 3, t + 3):
        m2 = q * jj
        if lo <= m2 <= hi and ds(m2) != s and m2 != y:
            rejm = m2
            break
    w = next((v for v in range(hi, lo - 1, -1) if ds(v) == s and v % q != 0), None)
    assert w and not valid(p, str(w))
    rej = f"{q}*{rejm // q} = {rejm}: digits {dstr(rejm)} = {ds(rejm)}, no. " if rejm else ""
    scan = f"Run through the multiples of {q} in the {d}-digit range, adding digits as we go. "
    texts = {
        "valid_near":
            scan + rej + f"{q}*{t} = {r}: digits {dstr(r)} = {s}. So {r} is a {d}-digit "
            f"multiple of {q} whose digits sum to {s}. {bx(r)}",
        "valid_far":
            f"Choose the digits before the number: we need {d} digits summing to {s}, say "
            f"{', '.join(str(far))} ({dstr(far)} = {s}), giving {far}. For divisibility, "
            f"{far} = {q}*{far // q} exactly, so {far} is a multiple of {q}. Both conditions "
            f"hold for this {d}-digit number. {bx(far)}",
        "invalid_near":
            scan + rej + f"{q}*{y // q} = {y}: digits {dstr(y)} = {s}. So {y} is a {d}-digit "
            f"multiple of {q} whose digits sum to {s}. {bx(y)}",
        "invalid_far":
            f"Choose the digits before the number: we need {d} digits summing to {s}, say "
            f"{', '.join(str(w))} ({dstr(w)} = {s}), giving {w}. For divisibility, "
            f"{w} = {q}*{round(w / q)}, so {w} is a multiple of {q}. Both conditions hold "
            f"for this {d}-digit number. {bx(w)}",
    }
    return texts, dict(valid_near=str(r), valid_far=str(far),
                       invalid_near=str(y), invalid_far=str(w))


FAM_FN = dict(crt=cands_crt, subset=cands_subset, goldbach=cands_goldbach,
              divcount=cands_divcount, digitsum=cands_digitsum)

rows = [json.loads(l) for l in open("runs/repl_main_tasks.jsonl")]
byfam, skipped = {}, {}
for i, row in enumerate(rows):
    fam = row["params"]["fam"]
    try:
        texts, ans = FAM_FN[fam](row["params"], row["ref_answer"], row["valid_answers"])
    except (AssertionError, StopIteration):
        skipped[fam] = skipped.get(fam, 0) + 1
        continue
    byfam.setdefault(fam, []).append((i, row, texts, ans))

rng = random.Random(SEED)
out_rows = []
for fam in ("crt", "subset", "goldbach", "divcount", "digitsum"):
    elig = byfam.get(fam, [])
    assert len(elig) >= N_PER_FAM, f"{fam}: only {len(elig)} eligible items"
    for pi in sorted(rng.sample(range(len(elig)), N_PER_FAM)):
        i, row, texts, ans = elig[pi]
        # equalize lengths: insert neutral filler before the \boxed line of the shortest
        fi = 0
        for _ in range(30):
            Ls = {ty: len(texts[ty]) for ty in TYPES}
            if max(Ls.values()) / min(Ls.values()) <= 1.55:
                break
            short = min(TYPES, key=lambda ty: Ls[ty])
            bp = texts[short].rfind("\\boxed")
            texts[short] = texts[short][:bp] + FILLERS[fi % len(FILLERS)] + " " + texts[short][bp:]
            fi += 1
        Ls = [len(texts[ty]) for ty in TYPES]
        ratio = max(Ls) / min(Ls)
        assert ratio <= 1.6, f"{row['problem_id']}: length ratio {ratio:.2f}"
        oracle = [int(bool(valid(row["params"], extract_boxed(texts[ty])))) for ty in TYPES]
        assert oracle == [1, 1, 0, 0], f"{row['problem_id']}: oracle {oracle}"
        assert ans["valid_near"] == row["ref_answer"]
        assert ans["valid_far"] != row["ref_answer"]
        assert len({ans[ty] for ty in TYPES}) == 4
        out_rows.append(dict(problem_id=row["problem_id"].replace("repl/", "simcorr/"),
                             source_id=row["problem_id"], problem=row["problem"],
                             params=row["params"], hard=row["hard"],
                             ref_answer=row["ref_answer"], cand_order=list(TYPES),
                             samples=[texts[ty] for ty in TYPES],
                             cand_answers=[ans[ty] for ty in TYPES], oracle=oracle,
                             lengths=Ls, length_ratio=round(ratio, 3)))

with open("runs/simcorr_tasks.jsonl", "w") as f:
    for r in out_rows:
        f.write(json.dumps(r) + "\n")

from collections import Counter
import statistics
fams = Counter(r["params"]["fam"] for r in out_rows)
ratios = [r["length_ratio"] for r in out_rows]
lens = [x for r in out_rows for x in r["lengths"]]
print(f"[simcorr build] wrote {len(out_rows)} items -> runs/simcorr_tasks.jsonl")
print(f"  per family: {dict(fams)}   ineligible skipped: {dict(skipped) or 'none'}")
print(f"  length ratio: mean {statistics.mean(ratios):.3f} max {max(ratios):.3f} "
      f"(band <= 1.6 asserted)  candidate chars: mean {statistics.mean(lens):.0f} "
      f"min {min(lens)} max {max(lens)}")
print("  all assertions passed: oracle [1,1,0,0] per item, valid_far != ref, "
      "4 distinct answers, length band")
