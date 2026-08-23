# Programmatic validity oracle for the replication pool: checks an extracted answer against
# the item's constraint parameters directly. No enumeration, no membership list: the checker
# is exact by construction for every family. Adds "oracle" (0/1 per sample) in place.
import argparse
import json
import math
import os
import re

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--tasks", default=None,
                help="task file to join params by problem_id when the pool lacks them; "
                     "defaults by pool name (replpilot -> pilot tasks, repl -> main tasks)")
args = ap.parse_args()


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + 7, 1
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


def ints_of(a):
    return [int(x) for x in re.findall(r"-?\d+", a or "")]


def is_prime(x):
    if x < 2:
        return False
    for p in range(2, int(x ** 0.5) + 1):
        if x % p == 0:
            return False
    return True


def ndiv(x):
    c, i = 0, 1
    while i * i <= x:
        if x % i == 0:
            c += 2 if i * i != x else 1
        i += 1
    return c


def valid(params, answer_text):
    xs = ints_of(answer_text)
    f = params["fam"]
    if f == "crt":
        if len(xs) != 1:
            return False
        x = xs[0]
        return (params["lo"] <= x <= params["hi"] and x % params["m"] == params["a"]
                and x % params["n"] == params["b"])
    if f == "subset":
        if not xs:
            return False
        avail = list(params["vals"])
        for x in xs:
            if x in avail:
                avail.remove(x)
            else:
                return False
        return sum(xs) == params["target"]
    if f == "goldbach":
        if len(xs) != 2:
            return False
        p, q = xs
        return p < q and p + q == params["N"] and is_prime(p) and is_prime(q)
    if f == "divcount":
        if len(xs) != 1:
            return False
        x = xs[0]
        return params["lo"] <= x <= params["hi"] and ndiv(x) == params["k"]
    if f == "digitsum":
        if len(xs) != 1:
            return False
        x = xs[0]
        return (len(str(x)) == params["d"] and x % params["q"] == 0
                and sum(map(int, str(x))) == params["s"])
    return False


rows = [json.loads(l) for l in open(args.pool)]
if rows and "params" not in rows[0]:
    tf = args.tasks or ("runs/kstrat_tasks.jsonl" if "kstrat" in args.pool else
                        "runs/repl_pilot_tasks.jsonl" if "replpilot" in args.pool
                        else "runs/repl_main_tasks.jsonl")
    tmap = {json.loads(l)["problem_id"]: json.loads(l) for l in open(tf)}
    for r in rows:
        r["params"] = tmap[r["problem_id"]]["params"]
        r["hard"] = tmap[r["problem_id"]].get("hard")
for r in rows:
    r["oracle"] = [int(valid(r["params"], extract_boxed(s) or s[-100:]))
                   for s in r["samples"]]
tmp = args.pool + ".tmp"
with open(tmp, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
os.replace(tmp, args.pool)
import numpy as np
pr = [sum(r["oracle"]) / len(r["oracle"]) for r in rows]
inband = sum(1 for p in pr if 0.2 <= p <= 0.8)
print(f"[repl oracle] items {len(rows)} mean pass {np.mean(pr):.3f} "
      f"in-band[0.2,0.8] {inband}/{len(rows)}", flush=True)
