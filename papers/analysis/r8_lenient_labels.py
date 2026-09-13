# POST HOC relabeling for the round-8 revision (external review of the round-7 draft). No registration weight.
# Run from experiments/tfa-vs-judge. Writes runs/r8/lenient_{repl,kpool}.jsonl and papers/analysis/r8_lenient_labels.json.
#
# The registered checkers read an answer from \boxed{} and otherwise from the whole reply (k-pool) or its last 100
# characters (replication), so a correct answer stated in prose usually counts as wrong. This script adds a
# format-lenient label, fixed before any judge score is read with it:
#   extracted answer = the \boxed{} content if present; otherwise, from the last line of the reply that contains a digit,
#     - remainder, divisor-count, digit-sum tasks (one integer): the last integer in the reply;
#     - subset-sum and Goldbach tasks (several integers): a trailing "= target" / "sums to target" is dropped, the line is
#       cut at its last ":", ";", sentence-ending ".", " is " or " are ", and the integers of the last piece that has any
#       are the answer (Goldbach: the last two, in increasing order);
#   lenient label = registered label OR the task's programmatic constraint check accepts the extracted answer.
#   An answer matches the reference when its extracted integers equal the reference's as a multiset.
# The check is the constraint itself (repl_oracle.py), so it needs no answer list.
import ast
import json
import os
import re
from collections import Counter

OUT = "../../papers/analysis/r8_lenient_labels.json"
os.makedirs("runs/r8", exist_ok=True)
POOLS = {"repl": "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl",
         "kpool": "runs/bon/bon_kstrat__meta-llama__Llama-3.1-8B-Instruct.jsonl"}


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def ints_of(a):
    return [int(x) for x in re.findall(r"-?\d+", (a or "").replace("\\!", "").replace("{,}", ""))]


def is_prime(x):
    return x >= 2 and all(x % p for p in range(2, int(x ** 0.5) + 1))


def ndiv(x):
    c, i = 0, 1
    while i * i <= x:
        if x % i == 0:
            c += 2 if i * i != x else 1
        i += 1
    return c


def check(p, xs):
    f = p["fam"]
    if f in ("crt", "divcount", "digitsum"):
        if len(xs) != 1:
            return False
        x = xs[0]
        if f == "crt":
            return p["lo"] <= x <= p["hi"] and x % p["m"] == p["a"] and x % p["n"] == p["b"]
        if f == "divcount":
            return p["lo"] <= x <= p["hi"] and x > 0 and ndiv(x) == p["k"]
        return x > 0 and len(str(x)) == p["d"] and x % p["q"] == 0 and sum(map(int, str(x))) == p["s"]
    if f == "subset":
        if not xs:
            return False
        avail = list(p["vals"])
        for x in xs:
            if x not in avail:
                return False
            avail.remove(x)
        return sum(xs) == p["target"]
    if f == "goldbach":
        if len(xs) != 2:
            return False
        a, b = sorted(xs)
        return a < b and a + b == p["N"] and is_prime(a) and is_prime(b)
    return False


def extract(p, s):
    b = boxed(s)
    if b is not None:
        xs = ints_of(b)
        return (sorted(xs) if p["fam"] == "goldbach" else xs), True
    lines = [l for l in s.strip().splitlines() if re.search(r"\d", l)]
    if not lines:
        return [], False
    if p["fam"] in ("crt", "divcount", "digitsum"):
        xs = ints_of(s)
        return xs[-1:], False
    target = p["target"] if p["fam"] == "subset" else p["N"]
    line = re.sub(r"(=|equals?|sums? (?:up )?to|adds? up to|totals?|is equal to)\s*\$?\s*%d\s*[\.\!\$]*\s*$" % target, "", lines[-1].strip())
    pieces = [x for x in re.split(r"[:;]|\.(?=\s|$)|\bis\b|\bare\b", line) if re.search(r"\d", x)]
    xs = ints_of(pieces[-1]) if pieces else []
    if p["fam"] == "goldbach":
        xs = sorted(xs[-2:])
    return xs, False


summary = {}
for name, f in POOLS.items():
    pool = [json.loads(l) for l in open(f)]
    c = Counter()
    with open(f"runs/r8/lenient_{name}.jsonl", "w") as out:
        for t in pool:
            p = t["params"] if isinstance(t["params"], dict) else ast.literal_eval(t["params"])
            refx = sorted(ints_of(t["ref_answer"]))
            len_, match, ext, isbox = [], [], [], []
            for s, o in zip(t["samples"], t["oracle"]):
                xs, bx = extract(p, s)
                ok = int(bool(o) or check(p, xs))
                len_.append(ok)
                match.append(int(ok and sorted(xs) == refx))
                ext.append(",".join(map(str, xs)))
                isbox.append(int(bx))
                c["samples"] += 1
                c["boxed"] += bx
                c["strict_correct"] += int(o)
                c["lenient_correct"] += ok
                if ok and not o:
                    c["flip_to_correct_boxed" if bx else "flip_to_correct_unboxed"] += 1
                if o and not check(p, xs):
                    c["strict_correct_not_rechecked"] += 1
            out.write(json.dumps(dict(problem_id=t["problem_id"], k=t["k"], strict=t["oracle"], lenient=len_, match=match,
                                      boxed=isbox, extracted=ext)) + "\n")
    summary[name] = dict(c)
json.dump(summary, open(OUT, "w"), indent=1)
print(json.dumps(summary, indent=1))
