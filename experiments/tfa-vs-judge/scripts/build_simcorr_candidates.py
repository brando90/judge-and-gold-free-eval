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
#   invalid_near the canonical (reference-style) route whose derivation carries exactly ONE
#                plausible human slip; FAILS the oracle
#   invalid_far  wrong via a derivation route structurally unrelated to the reference route,
#                again carrying one plausible slip; FAILS the oracle
#
# REVISED CONSTRUCTION (2026-08-27, after blind-audit failures; round count and outcomes are
# recorded in papers/D-reference-laws/registration.md). The original errors were bald false
# equations ("digits 8+2 = 12", "403, which is prime" next to a checkable subtraction) that
# the naturalness auditor flagged as deliberate corruption. The revised rule, applied through
# one prose pipeline shared by all four classes (same skeletons, same closers, uniform
# hedging): EVERY displayed number and equation is true, and each invalid candidate carries
# exactly one plausible human slip of a registered type — a dropped-constraint assertion
# (verify one congruence, say the other "is carried by the combined class"), an element
# reused against the problem's use-once rule (all running totals true, landing exactly on
# the target), a stealth misprimality (calling 403 = 13*31 or 77 = 7*11 prime after true
# checks of 2/3/5 — the classic human slip), or a membership slip (a number with the right
# digit sum carried into a scan of multiples it does not belong to). Family eligibility is
# restricted to items where such a slip exists (digitsum q in {7,11}; a stealth composite in
# range for divcount; a stealth complement for goldbach), keeping 8 items per family from
# the frozen pool, deterministically. NO judge scores of any simcorr candidate exist at
# revision time (the audit gate blocked judging), so this revision cannot select errors
# against any judge; it targets auditor-rated naturalness only, as the registered design
# requires.
#
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
import itertools
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260827
N_PER_FAM = 8
TYPES = ["valid_near", "valid_far", "invalid_near", "invalid_far"]
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


def bx(a):
    return "\\boxed{" + str(a) + "}"


def dsum(x):
    return sum(int(c) for c in str(x))


def spf(x):
    return next((i for i in range(2, x + 1) if x % i == 0), x)


def cands_crt(p, ref, valids):
    m, n, a, b, lo, hi = p["m"], p["n"], p["a"], p["b"], p["lo"], p["hi"]
    r = int(ref)
    M = m * n
    first = lo + ((r - lo) % M)
    chain = list(range(first, hi + 1, M))
    far = max((int(v) for v in valids if int(v) != r), key=lambda v: (abs(v - r), v))
    modn = [x for x in range(lo, hi + 1) if x % n == b]
    rej = [x for x in modn if x % m != a][:2]
    assert rej and far in modn
    # slip design: break the congruence that takes actual division to check (mod 4 first,
    # then mod 3), preserving the visually salient one (parity / last digit) where possible
    fail_mod = next((z for z in (4, 3, 9, 8, 7, 6, 5) if z in (m, n)), n)
    pres = m if fail_mod == n else n
    a_pres = a if pres == m else b
    b_fail = b if fail_mod == n else a
    wrong = r + pres if r + pres <= hi else r - pres
    assert lo <= wrong <= hi and not valid(p, str(wrong))
    mid = (lo + hi) // 2
    w2c = [x for x in range(lo, hi + 1)
           if x % pres == a_pres and not valid(p, str(x)) and x != wrong]
    assert w2c
    w2 = min(w2c, key=lambda x: (abs(x - mid), x))
    firstw = lo + ((wrong - lo) % M)
    chainw = list(range(firstw, hi + 1, M))

    def vline(x, mod, res):
        # verification line "x = mod*q + res"; TRUE when x % mod == res, otherwise the
        # quotient is chosen so the claimed value is off by the minimum possible amount
        # (an off-by-one / small carry slip)
        if x % mod == res:
            return f"{x} = {mod}*{x // mod} + {res}"
        qo = round((x - res) / mod)
        return f"{x} = {mod}*{qo} + {res}"
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
            + f"; and continuing down the list, {far} mod {m} = {a}, as required. So "
            f"x = {far} meets both conditions. {bx(far)}",
        "invalid_near":
            f"We need x ≡ {a} (mod {m}) and x ≡ {b} (mod {n}). Since {m} and {n} are coprime, "
            f"the two congruences combine into one condition modulo {m}*{n} = {M}, and adding "
            f"{M} preserves both remainders, so the solutions in range are "
            f"{', '.join(map(str, chainw[:4]))}{', ...' if len(chainw) > 4 else ''}. Take "
            f"x = {wrong}: {vline(wrong, m, a)} and {vline(wrong, n, b)}, with "
            f"{lo} <= {wrong} <= {hi}. {bx(wrong)}",
        "invalid_far":
            f"Write the congruence modulo {pres} as x = {pres}t + {a_pres} and substitute it "
            f"into the congruence modulo {fail_mod}; solving for t and lifting back, "
            f"t = {w2 // pres} works, giving x = {pres}*{w2 // pres} + {a_pres} = {w2}. And "
            f"{vline(w2, fail_mod, b_fail)}, with {lo} <= {w2} <= {hi}, so both conditions "
            f"hold. {bx(w2)}",
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
    unused = [v for v in vals if v not in R]
    assert unused

    def chain(seq, slip_at=None, delta=0):
        # displayed addition chain; partial sums are TRUE except that the partial at
        # addition index slip_at (1-based) and onward absorb -delta, so every later
        # displayed addition is again exactly true and the chain lands on the target
        parts, s = [], seq[0]
        prev = s
        for i, v in enumerate(seq[1:], 1):
            s += v
            disp = s - (delta if slip_at is not None and i >= slip_at else 0)
            parts.append(f"{prev} + {v} = {disp}")
            prev = disp
        return ", ".join(parts)

    # invalid_near: swap one element of R for an unused value with the smallest possible
    # sum offset; one mid-chain transcribed partial sum, all later additions exactly true
    swaps = []
    for x0 in R:
        for y0 in unused:
            Rn2 = sorted([v for v in R if v != x0] + [y0])
            if sum(Rn2) == target or len(set(Rn2)) != len(Rn2):
                continue
            dd = y0 - x0
            # a slip of +-10 preserves the units digit of the partial sum: a classic
            # forgotten/extra-carry error, far more plausible than a random offset
            swaps.append((0 if dd % 10 == 0 else 1, abs(dd), x0, y0, tuple(Rn2)))
    assert swaps
    _, _, x0, y0, Rn = min(swaps)
    Rn = list(Rn)
    delta = sum(Rn) - target
    seqn = sorted(Rn, reverse=True)
    slip_at = min(2, len(Rn) - 1)
    assert not valid(p, ",".join(map(str, Rn)))
    # invalid_far: three mid-sized values whose true sum misses the target by as little as
    # possible; one partial-sum slip, second displayed addition exactly true
    W = None
    for c in sorted(itertools.combinations(sorted(set(vals)), 3),
                    key=lambda c: (0 if (sum(c) - target) % 10 == 0 else 1,
                                   abs(sum(c) - target), c)):
        cs = sorted(c)
        if sum(cs) == target or cs in (Rn, R, far):
            continue
        W = cs
        break
    assert W and not valid(p, ",".join(map(str, W)))
    t1 = target - W[2]
    removed = sorted(v for v in vals if v not in far)
    assert sum(removed) == S - target
    texts = {
        "valid_near":
            f"Pick out values that reach the target: {', '.join(map(str, sorted(R, reverse=True)))}. "
            f"Adding them in turn: {chain(sorted(R, reverse=True))} — exactly the target. "
            f"Every element chosen is in the given set and used once. "
            f"{bx(','.join(map(str, R)))}",
        "valid_far":
            f"The full set {{{', '.join(map(str, vals))}}} sums to {S}. A subset totals "
            f"{target} exactly when the elements left out total {S} - {target} = "
            f"{S - target}. Leaving out {', '.join(map(str, removed))} removes exactly "
            f"{S - target}, so the remaining values {', '.join(map(str, far))} must sum to "
            f"{target}. {bx(','.join(map(str, far)))}",
        "invalid_near":
            f"Pick out values that reach the target: {', '.join(map(str, seqn))}. "
            f"Adding them in turn: {chain(seqn, slip_at, delta)} — exactly the target. "
            f"Every element chosen is in the given set and used once. "
            f"{bx(','.join(map(str, Rn)))}",
        "invalid_far":
            f"Try a compact subset of three mid-sized values from the set: {W[0]}, {W[1]}, "
            f"and {W[2]}. Adding them in turn: {W[0]} + {W[1]} = {t1}, and {t1} + {W[2]} = "
            f"{target}, landing exactly on the required total. Each value is in the given "
            f"set and used once. {bx(','.join(map(str, W)))}",
    }
    return texts, dict(valid_near=",".join(map(str, R)), valid_far=",".join(map(str, far)),
                       invalid_near=",".join(map(str, Rn)), invalid_far=",".join(map(str, W)))


def cands_goldbach(p, ref, valids):
    N = p["N"]
    # eligibility: large enough that complements are 3-digit and factoring them is real work
    assert N >= 200
    rp, rq = (int(x) for x in ref.split(","))
    pairs = [tuple(int(x) for x in v.split(",")) for v in valids]

    def sfac(c):
        return next(i for i in range(2, c + 1) if c % i == 0)

    rejected = [x for x in range(2, rp) if is_prime(x) and not is_prime(N - x)]
    # invalid_near: the canonical scan stops early at a prime whose complement is a STEALTH
    # composite (largest smallest-prime-factor available, so 2/3/5 checks all pass); the
    # subtraction and the sum are TRUE — the single slip is the primality claim
    def sqcube(v):  # recognizable perfect squares/cubes make poor "primes"
        return int(round(v ** 0.5)) ** 2 == v or int(round(v ** (1 / 3))) ** 3 == v

    p0c = [x for x in rejected if N - x > 1 and spf(N - x) >= 7]
    assert p0c
    p0 = max(p0c, key=lambda x: (not sqcube(N - x), spf(N - x), -x))
    c0 = N - p0
    assert not valid(p, f"{p0},{c0}")
    rej = [x for x in rejected if x != p0][:2]
    rejtxt = " ".join(f"p = {x}: {N} - {x} = {N - x} = {sfac(N - x)}*{(N - x) // sfac(N - x)}"
                      f", composite." for x in rej)
    rej_in = [x for x in rejected if x < p0][:2]
    rejtxt_in = " ".join(f"p = {x}: {N} - {x} = {N - x} = "
                         f"{sfac(N - x)}*{(N - x) // sfac(N - x)}, composite." for x in rej_in)
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
    # invalid_far: split near N/3; complement subtraction TRUE, stealth-composite complement
    # claimed prime
    p3 = None
    third = N // 3
    for minspf, allow_sq in ((11, False), (7, False), (11, True), (7, True)):
        for off in range(0, 200):
            for c in (third - off, third + off):
                if (c > 2 and c < N - c and is_prime(c) and N - c > 1
                        and not is_prime(N - c) and spf(N - c) >= minspf
                        and (allow_sq or not sqcube(N - c)) and c not in (p0, rp, pf)):
                    p3 = c
                    break
            if p3:
                break
        if p3:
            break
    assert p3
    q3 = N - p3
    assert p3 < q3 and not valid(p, f"{p3},{q3}")
    scan = f"Search upward through the primes p and test whether {N} - p is prime. "
    texts = {
        "valid_near":
            scan + (rejtxt + " " if rejtxt else "")
            + f"p = {rp}: {N} - {rp} = {rq}, which is prime. So {rp} and {rq} are distinct "
            f"primes with {rp} < {rq} and {rp} + {rq} = {N}. {bx(f'{rp},{rq}')}",
        "valid_far": far_text,
        "invalid_near":
            scan + (rejtxt_in + " " if rejtxt_in else "")
            + f"p = {p0}: {N} - {p0} = {c0}, which is prime. So {p0} and {c0} are distinct "
            f"primes with {p0} < {c0} and {p0} + {c0} = {N}. {bx(f'{p0},{c0}')}",
        "invalid_far":
            f"Split {N} with the smaller prime taken near {N}/3 ≈ {third}: p = {p3} is "
            f"prime, and its complement {N} - {p3} = {q3} is prime as well. That gives "
            f"distinct primes with {p3} < {q3} summing to {N}, as required. "
            f"{bx(f'{p3},{q3}')}",
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

    isq = int(round(r ** 0.5))
    if k == 2:

        def ruleline(x):
            # the incomplete small-prime argument, TRUE line by line for every number it is
            # applied to (odd, last digit, digit sum); the conclusion is the only slip when
            # x has a larger prime factor. The SAME wording carries the valid candidate, so
            # no class has a private template.
            return (f"it is odd, it does not end in 0 or 5, and its digit sum {dsum(x)} is "
                    f"not a multiple of 3, so no small prime divides it and {x} is prime")

        near_text0 = (f"A number has exactly 2 divisors precisely when it is prime. Test "
                      f"x = {r}: {ruleline(r)}. Its divisors are just 1 and {r} — exactly "
                      f"2 — and {lo} <= {r} <= {hi}. {bx(r)}")
        # both invalid answers are IN-RANGE composites presented as primes through the same
        # incomplete-argument template; eligibility requires a stealth composite (smallest
        # prime factor >= 7) in range so every displayed check is TRUE
        stealth = [v for v in range(lo, hi + 1)
                   if v % 2 and v % 3 and v % 5 and not is_prime(v)]
        assert stealth
        y = min(stealth, key=lambda v: (abs(v - r), v))
        inear_text = (f"A number has exactly 2 divisors precisely when it is prime. Test "
                      f"x = {y}: {ruleline(y)}. Its divisors are just 1 and {y} — exactly "
                      f"2 — and {lo} <= {y} <= {hi}. {bx(y)}")
        assert not valid(p, str(y))
        wcand = [v for v in range(lo, hi + 1)
                 if v % 2 and v % 3 and v % 5 and not is_prime(v) and v != y]
        if not wcand:
            wcand = [v for v in range(lo, hi + 1)
                     if v % 2 and v % 5 and not is_prime(v) and v != y]
        assert wcand

        def table(v):  # small times-table products read as obviously composite
            return int(any(v % f == 0 and f <= 12 and v // f <= 12 for f in range(2, 13)))

        w = min(wcand, key=lambda v: (0 if spf(v) >= 7 else 1, table(v),
                                      1 if int(v ** 0.5) ** 2 == v else 0, -v))
        if spf(w) >= 7:
            wline = ruleline(w)
        else:
            wline = (f"it is odd, it does not end in 0 or 5, and no small prime divides "
                     f"it, so {w} is prime")
        ifar_text = (f"Walk down from the top of the range testing for primes. At x = {w}: "
                     f"{wline} — divisors 1 and {w}, exactly 2 — with "
                     f"{lo} <= {w} <= {hi}. {bx(w)}")
        assert w != y and not valid(p, str(w))
        fshow = f"1 and {far}"
    else:
        near_text0 = (f"Exactly 3 divisors forces x = p^2 for a prime p, since the divisors "
                      f"are then 1, p, p^2. Here {r} = {isq}^2 and {isq} is prime, so the "
                      f"divisors of {r} are 1, {isq}, {r} — exactly 3 — and {r} lies in "
                      f"[{lo}, {hi}]. {bx(r)}")
        y = near_off(r, lambda v: ndiv(v) != k)
        assert y and not valid(p, str(y))
        inear_text = (f"Exactly 3 divisors forces x = p^2 for a prime p, since the divisors "
                      f"are then 1, p, p^2. Here {isq} is prime and {isq}^2 = {y}, so the "
                      f"divisors of {y} are 1, {isq}, {y} — exactly 3 — and {y} lies in "
                      f"[{lo}, {hi}]. {bx(y)}")
        sq_comps = [t for t in range(2, int(hi ** 0.5) + 2)
                    if not is_prime(t) and lo <= t * t <= hi and t * t not in (y, far, r)]
        assert sq_comps
        t3 = max(sq_comps)
        w = t3 * t3
        ifar_text = (f"An exact count of 3 divisors needs a perfect square, since divisors "
                     f"pair up except at the square root. Walking down from the top, "
                     f"{w} = {t3}^2 is a square in [{lo}, {hi}], with divisors 1, {t3}, "
                     f"{w} — exactly 3. {bx(w)}")
        assert w != y and not valid(p, str(w))
        fshow = f"1, {int(round(far ** 0.5))}, {far}"
    u = near_off(far, lambda v: ndiv(v) != k and v not in (y, w))
    assert u
    ud = divs(u)
    ushow = ", ".join(map(str, ud[:4])) + (", ..." if len(ud) > 4 else "")
    texts = {
        "valid_near": near_text0,
        "valid_far":
            f"Walk through the range listing divisors outright. {u}: divisors {ushow} — "
            f"{len(ud)} of them, not {k}. {far}: divisors {fshow} — exactly {k}. And "
            f"{lo} <= {far} <= {hi}, so x = {far} is a valid answer. {bx(far)}",
        "invalid_near": inear_text,
        "invalid_far": ifar_text,
    }
    return texts, dict(valid_near=str(r), valid_far=str(far),
                       invalid_near=str(y), invalid_far=str(w))


def cands_digitsum(p, ref, valids):
    d, q, s = p["d"], p["q"], p["s"]
    # eligibility: only moduli whose divisibility cannot be read off the digits (no parity,
    # no last-digit, no digit-sum rule)
    assert q not in (2, 3, 5, 9, 10)
    r = int(ref)
    lo, hi = 10 ** (d - 1), 10 ** d - 1

    def ds(x):
        return sum(int(c) for c in str(x))

    def dstr(x):
        return "+".join(str(x))

    far = max((int(v) for v in valids if int(v) != r), key=lambda v: (abs(v - r), v))
    t = r // q
    # invalid answers: digit sum is exactly s (the digit line shown is the number's REAL
    # digits and is TRUE); the single slip is membership in the scan of multiples /
    # the divisibility claim, which requires an actual division to refute
    def pal(v):
        return int(str(v) == str(v)[::-1])

    pool = [v for v in range(lo, hi + 1) if ds(v) == s and v % q != 0]
    assert pool
    # avoid well-memorized numbers: primes (a prime claimed divisible is easy to spot) and
    # palindromes; keep the far pick mid-range rather than at the extreme ends
    def nearmult(v):  # remainder 1 or q-1: the claimed division is off by exactly one
        return 0 if v % q in (1, q - 1) else 1

    y = min(pool, key=lambda v: (int(is_prime(v)), pal(v), nearmult(v), abs(v - r), v))
    assert not valid(p, str(y))
    wpool = [v for v in pool if v != y]
    assert wpool
    w = min(wpool, key=lambda v: (int(is_prime(v)), pal(v), nearmult(v),
                                  0 if 3 * lo <= v <= 9 * lo - 1 else 1, -abs(v - r), v))
    assert w and not valid(p, str(w))
    rejm = None
    for jj in (t - 1, t + 1, t - 2, t + 2, t - 3, t + 3):
        m2 = q * jj
        if lo <= m2 <= hi and ds(m2) != s and m2 not in (y, w):
            rejm = m2
            break
    rej = f"{rejm}: digits {dstr(rejm)} = {ds(rejm)}, no. " if rejm else ""
    scan = f"Run through the multiples of {q} in the {d}-digit range, adding digits as we go. "
    texts = {
        "valid_near":
            scan + rej + f"{r}: digits {dstr(r)} = {s}. So {r} is a {d}-digit multiple of "
            f"{q} whose digits sum to {s}. {bx(r)}",
        "valid_far":
            f"Choose the digits before the number: we need {d} digits summing to {s}, say "
            f"{', '.join(str(far))} ({dstr(far)} = {s}), giving {far}. Dividing by {q} "
            f"leaves no remainder, so {far} is a multiple of {q}. Both conditions hold for "
            f"this {d}-digit number. {bx(far)}",
        "invalid_near":
            scan + rej + f"{y}: digits {dstr(y)} = {s}. So {y} is a {d}-digit multiple of "
            f"{q} whose digits sum to {s}. {bx(y)}",
        "invalid_far":
            f"Choose the digits before the number: we need {d} digits summing to {s}, say "
            f"{', '.join(str(w))} ({dstr(w)} = {s}), giving {w}. Dividing by {q} leaves no "
            f"remainder, so {w} is a multiple of {q}. Both conditions hold for this "
            f"{d}-digit number. {bx(w)}",
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
