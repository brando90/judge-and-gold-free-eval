# Oracle for the separability continuum (registered P-SC suite; see build_sep_tasks.py).
# Adds per-sample `oracle` (0/1) and `canon` (canonical answer string or null) to the pool
# file in place. Validity is decided programmatically per stratum:
#   scalar : boxed integer in [lo,hi] with x % m == a
#   pair   : boxed "x,y", two DISTINCT valid integers        canon = "min,max"
#   json   : last JSON object {"values": [v1,v2,v3], ...}, three distinct valid integers
#   program: last ```python (or ```) code block defining f(); executed in an isolated
#            subprocess (python3 -I, 5 s timeout); must return a list of three distinct
#            valid integers. canon = sorted values joined by ",".
import json
import re
import subprocess
import sys

POOL = sys.argv[1] if len(sys.argv) > 1 else "runs/bon/bon_sep__meta-llama__Llama-3.1-8B-Instruct.jsonl"


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + 7, 1
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


def ints_of(s, n):
    try:
        parts = [int(p.strip()) for p in s.strip().strip("{}()[]").split(",")]
    except Exception:
        return None
    return parts if len(parts) == n else None


def valid_int(x, p):
    return p["lo"] <= x <= p["hi"] and x % p["m"] == p["a"]


def check_values(vals, n, p):
    if vals is None or len(vals) != n or len(set(vals)) != n:
        return None
    if not all(isinstance(v, int) and valid_int(v, p) for v in vals):
        return None
    return ",".join(str(v) for v in sorted(vals))


def last_json_obj(text):
    # last {...} block that parses
    for mt in reversed(list(re.finditer(r"\{[^{}]*\}", text))):
        try:
            return json.loads(mt.group(0))
        except Exception:
            continue
    return None


def last_code_block(text):
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return blocks[-1] if blocks else None


def run_program(code, p):
    prog = code + "\nimport json\nprint(json.dumps(f()))"
    try:
        r = subprocess.run([sys.executable, "-I", "-c", prog], capture_output=True,
                           text=True, timeout=5)
        if r.returncode != 0:
            return None
        vals = json.loads(r.stdout.strip().splitlines()[-1])
        if not isinstance(vals, list):
            return None
        vals = [int(v) for v in vals]
    except Exception:
        return None
    return check_values(vals, 3, p)


rows = [json.loads(l) for l in open(POOL)]
n_done = 0
for r in rows:
    if "oracle" in r:
        continue
    p = r["params"]
    oracle, canon = [], []
    for s in r["samples"]:
        c = None
        if r["stratum"] == "scalar":
            b = extract_boxed(s)
            v = ints_of(b, 1) if b else None
            c = check_values(v, 1, p) if v else None
        elif r["stratum"] == "pair":
            b = extract_boxed(s)
            v = ints_of(b, 2) if b else None
            c = check_values(v, 2, p) if v else None
        elif r["stratum"] == "json":
            o = last_json_obj(s)
            if isinstance(o, dict) and isinstance(o.get("values"), list):
                try:
                    c = check_values([int(v) for v in o["values"]], 3, p)
                except Exception:
                    c = None
        else:  # program
            code = last_code_block(s)
            c = run_program(code, p) if code and "def f" in code else None
        oracle.append(1 if c else 0)
        canon.append(c)
    r["oracle"], r["canon"] = oracle, canon
    n_done += 1

with open(POOL, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")

import collections
acc = collections.defaultdict(list)
for r in rows:
    acc[r["stratum"]].append(sum(r["oracle"]) / len(r["oracle"]))
print(f"[sep_oracle] {n_done} items scored; mean pass rate per stratum: " +
      ", ".join(f"{k}={sum(v)/len(v):.3f}" for k, v in sorted(acc.items())))
