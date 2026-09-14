# PRE-SPECIFIED producer for R22-A (papers/D-iclr/registration_round22.md); committed before any R22 call.
# Run from experiments/tfa-vs-judge. Writes papers/analysis/r22a_label_audit.json.
# Reader label = registered label OR the task's constraint check accepts the integers of the last non-empty line of the reader's
# answer; NONE (or no digit) on that line keeps the registered label. The constraint check is `check` from r8_lenient_labels.py,
# copied verbatim below so that importing it does not re-run that script. Readouts are per stratum (pool x any-format label) and
# pooled with weights proportional to stratum population sizes.
import json
import re

OUT = "../../papers/analysis/r22a_label_audit.json"


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


S = [json.loads(l) for l in open("runs/r22/label_sample.jsonl")]
R = {}
for l in open("runs/r22/opus_read.jsonl"):
    r = json.loads(l)
    if r.get("answer") is not None and not r.get("error"):
        R[(r["problem_id"], r["idx"])] = r
rows = []
for s in S:
    r = R.get((s["problem_id"], s["idx"]))
    if r is None:
        continue
    lines = [x.strip() for x in r["answer"].splitlines() if x.strip()]
    last = lines[-1] if lines else ""
    none = bool(re.search(r"\bNONE\b", last)) or not re.search(r"\d", last)
    reader = s["registered"] if none else int(bool(s["registered"]) or check(s["params"], ints_of(last)))
    rows.append(dict(stratum=s["stratum"], size=s["stratum_size"], any_format=s["any_format"], qwen14b=s["qwen14b"], reader=reader, none=int(none),
                     pool=s["pool"], problem_id=s["problem_id"], idx=s["idx"], reader_line=last))


def mean(xs):
    return round(sum(xs) / len(xs), 4) if xs else None


res = {"answered": len(rows), "sampled": len(S), "scored": len(rows) >= 180, "strata": {}}
for st in sorted({r["stratum"] for r in rows}):
    g = [r for r in rows if r["stratum"] == st]
    res["strata"][st] = dict(n=len(g), size=g[0]["size"], agree_any_format=mean([r["any_format"] == r["reader"] for r in g]),
                             agree_qwen14b=mean([r["qwen14b"] == r["reader"] for r in g]), reader_correct=mean([r["reader"] for r in g]),
                             none=mean([r["none"] for r in g]))


def weighted(key, sel):
    sts = [(st, d) for st, d in res["strata"].items() if sel(st)]
    tot = sum(d["size"] for _, d in sts)
    return round(sum(d["size"] * d[key] for _, d in sts) / tot, 4) if tot else None


res["pooled"] = dict(
    agree_any_format=weighted("agree_any_format", lambda st: True),
    agree_qwen14b=weighted("agree_qwen14b", lambda st: True),
    any_correct_confirmed=weighted("reader_correct", lambda st: st.endswith("|correct")),
    any_wrong_called_correct=weighted("reader_correct", lambda st: st.endswith("|wrong")),
    none_share=weighted("none", lambda st: True))
for pool in ("repl", "kpool"):
    res[f"pool_{pool}"] = dict(agree_any_format=weighted("agree_any_format", lambda st: st.startswith(pool + "|")),
                               agree_qwen14b=weighted("agree_qwen14b", lambda st: st.startswith(pool + "|")))
res["predictions"] = {
    "P-R22A1 weighted agreement >= 0.85": None if not res["scored"] else ("confirmed" if res["pooled"]["agree_any_format"] >= 0.85 else "falsified"),
    "P-R22A2 any-format correct confirmed >= 0.90": None if not res["scored"] else ("confirmed" if res["pooled"]["any_correct_confirmed"] >= 0.90 else "falsified"),
    "P-R22A3 any-format wrong called correct <= 0.15": None if not res["scored"] else ("confirmed" if res["pooled"]["any_wrong_called_correct"] <= 0.15 else "falsified"),
}
res["disagreements"] = [dict(stratum=r["stratum"], problem_id=r["problem_id"], idx=r["idx"], any_format=r["any_format"], reader=r["reader"], reader_line=r["reader_line"][:80])
                        for r in rows if r["any_format"] != r["reader"]]
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "disagreements"}, indent=1))
