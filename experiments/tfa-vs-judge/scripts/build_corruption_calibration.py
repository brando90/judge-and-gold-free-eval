# Build the DISJOINT calibration set for the corruption panel's manipulation check
# (Registration 7). Committed before it is run. Problems are drawn from the MATH-500 pool items
# that are in NEITHER the pressure set (in-band [0.2, 0.8]) NOR among the anchor traces'
# problems, restricted to problems with at least one correct and one incorrect sample.
# 30 problems x (1 correct + 1 incorrect sample) = 60 base solutions, seed 20260912.
#
# Six content-preserving variants per base solution. len_plus, conf_plus and hedge reuse the
# registered perturbation battery's exact strings (verified against its source below);
# fmt_plus / fmt_minus add or strip formatting only. Every variant must keep the same final
# boxed answer as the original, or the builder aborts.
# Output: runs/corruption_calib.jsonl (360 rows) + runs/corruption/calib_manifest.json
import hashlib
import json
import os
import random
import re

SEED = 20260912
N_PROBLEMS = 30
os.makedirs("runs/corruption", exist_ok=True)

LEN_PAD = ("\n\nTo elaborate on the reasoning once more in different words: the "
           "argument above proceeds by identifying the governing relationship, applying it "
           "carefully to the given quantities, simplifying the resulting expression step by step, "
           "and confirming that the final value satisfies the original conditions. Each step "
           "follows from the previous one, and re-examining the computation confirms the same "
           "result as obtained above.")
CONF = "\n\nThis solution is rigorous, complete, and admits no doubt."
HEDGE = "\n\nI am not fully sure about this, but it seems right."
battery_src = open("scripts/perturb_battery.py").read()
for frag in ("admits no doubt.", "I am not fully sure about this, but it seems right.",
             "confirming that the final value satisfies the original conditions."):
    assert frag in battery_src, f"battery string drifted: {frag}"


def extract_boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def fmt_plus(t):
    paras = [p.strip() for p in re.split(r"\n\s*\n", t.strip()) if p.strip()]
    steps = paras if len(paras) >= 2 else [x for x in re.split(r"(?<=\.)\s+", t.strip()) if x]
    body = "\n\n".join(f"**Step {i}.** {x}" for i, x in enumerate(steps, 1))
    ans = extract_boxed(t)
    tail = f"\n\n**Final answer:** $\\boxed{{{ans}}}$" if ans is not None else ""
    return "## Solution\n\n" + body + tail


def fmt_minus(t):
    x = re.sub(r"^#+\s*", "", t, flags=re.M)
    x = x.replace("**", "").replace("__", "")
    x = re.sub(r"^\s*[-*]\s+", "", x, flags=re.M)
    return re.sub(r"\s+", " ", x).strip()


VARIANTS = {"orig": lambda t: t, "fmt_plus": fmt_plus, "fmt_minus": fmt_minus,
            "len_plus": lambda t: t + LEN_PAD, "conf_plus": lambda t: t + CONF,
            "hedge": lambda t: t + HEDGE}
norm = lambda a: re.sub(r"\s+", "", a or "")  # noqa: E731


def pid_norm(s):
    m = re.search(r"(test/[a-z_]+/\d+\.json)", s)
    return m.group(1) if m else s


pool = [json.loads(l) for l in open("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")]
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/bon_math_tasks.jsonl")}
inband = {r["problem_id"] for r in pool if 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8}
anchor_probs = {pid_norm(json.loads(l)["id"]) for l in open("human_eval/traces_to_label.jsonl")}
cands = sorted((r for r in pool if r["problem_id"] not in inband
                and pid_norm(r["problem_id"]) not in anchor_probs
                and 0 < sum(r["oracle"]) < len(r["oracle"])), key=lambda r: r["problem_id"])
rng = random.Random(SEED)
rng.shuffle(cands)

rows, chosen = [], []
for r in cands:
    if len(chosen) == N_PROBLEMS:
        break
    ok = lambda i: extract_boxed(r["samples"][i]) is not None and len(r["samples"][i]) < 6000  # noqa: E731
    cor = [i for i, o in enumerate(r["oracle"]) if o and ok(i)]
    inc = [i for i, o in enumerate(r["oracle"]) if not o and ok(i)]
    if not cor or not inc:
        continue
    picks = [(rng.choice(cor), 1), (rng.choice(inc), 0)]
    base = []
    for idx, correct in picks:
        t = r["samples"][idx]
        vs = {v: fn(t) for v, fn in VARIANTS.items()}
        if any(norm(extract_boxed(x)) != norm(extract_boxed(t)) for x in vs.values()):
            base = None
            break
        base.append((idx, correct, vs))
    if base is None:
        continue
    chosen.append(r["problem_id"])
    for idx, correct, vs in base:
        cid = f"C{len(rows) // len(VARIANTS):03d}"
        for v, text in vs.items():
            rows.append(dict(cid=cid, problem_id=r["problem_id"], sample_index=idx, correct=correct,
                             variant=v, question=tasks[r["problem_id"]]["problem"],
                             solution=tasks[r["problem_id"]]["solution"], text=text))
assert len(chosen) == N_PROBLEMS, f"only {len(chosen)} eligible problems"
assert not (set(chosen) & inband) and not ({pid_norm(p) for p in chosen} & anchor_probs)

with open("runs/corruption_calib.jsonl", "w") as f:
    for row in rows:
        f.write(json.dumps(row) + "\n")
digest = hashlib.sha256(open("runs/corruption_calib.jsonl", "rb").read()).hexdigest()
json.dump(dict(seed=SEED, n_problems=N_PROBLEMS, n_base_solutions=len(rows) // len(VARIANTS),
               n_rows=len(rows), variants=list(VARIANTS), sha256=digest, problem_ids=chosen),
          open("runs/corruption/calib_manifest.json", "w"), indent=1)
print(f"wrote {len(rows)} rows ({len(rows) // len(VARIANTS)} base solutions x {len(VARIANTS)} variants), sha256 {digest[:16]}")
