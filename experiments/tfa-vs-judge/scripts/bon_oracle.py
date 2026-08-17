# Oracle-score BoN pools in place: adds "oracle" (list of 0/1 per sample) to each row.
# math: boxed-answer match (normalized string; equivalence-adjudication pass happens later and
# only ever flips 0->1, so the filter is conservative). code: executed official tests, parallel.
import argparse, json, multiprocessing as mp, os, re, subprocess, tempfile

ap = argparse.ArgumentParser()
ap.add_argument("--domain", choices=["math", "code"], required=True)
ap.add_argument("--pool", required=True)
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


def norm(a):
    if a is None:
        return None
    a = a.strip().strip("$ ").replace("\\!", "").replace("\\,", "").replace(" ", "")
    a = re.sub(r"\\text\{([^}]*)\}", r"\1", a)
    a = re.sub(r"\\dfrac", r"\\frac", a)
    a = a.rstrip(".")
    return a


def extract_code(fg, question):
    m = re.findall(r"```(?:python)?\n(.*?)```", fg, re.S)
    if m:
        code = max(m, key=len)
        return code if "def " in code else question + code
    return question + fg if "def " not in fg else fg


def run_one(prog):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
        tf.write(prog); path = tf.name
    try:
        p = subprocess.run(["python3", path], capture_output=True, timeout=10)
        ok = int(p.returncode == 0)
    except Exception:
        ok = 0
    os.unlink(path)
    return ok


rows = [json.loads(l) for l in open(args.pool)]
if args.domain == "math":
    for r in rows:
        gold = norm(r["answer"])
        r["oracle"] = [int(norm(extract_boxed(s)) == gold and gold is not None)
                       for s in r["samples"]]
else:
    progs, spans = [], []
    for r in rows:
        start = len(progs)
        for s in r["samples"]:
            code = extract_code(s, r["question"])
            progs.append(code + "\n\n" + r["test"] + f"\n\ncheck({r['entry_point']})\n")
        spans.append((start, len(progs)))
    with mp.Pool(16) as pool:
        oks = pool.map(run_one, progs, chunksize=8)
    for r, (a, b) in zip(rows, spans):
        r["oracle"] = oks[a:b]

tmp = args.pool + ".tmp"
with open(tmp, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
os.replace(tmp, args.pool)
import numpy as np
pr = [sum(r["oracle"]) / len(r["oracle"]) for r in rows]
inband = sum(1 for p in pr if 0.2 <= p <= 0.8)
print(f"[oracle {args.domain}] items {len(rows)} mean pass {np.mean(pr):.3f} "
      f"in-band[0.2,0.8] {inband}", flush=True)
