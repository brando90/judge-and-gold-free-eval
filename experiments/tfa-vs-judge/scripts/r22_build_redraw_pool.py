# R22-B (papers/D-iclr/registration_round22.md): the benchmark pool with a second reference drawn from each MACE answer list.
# For each question of runs/r20/mace_gen/pool.jsonl, the new reference is drawn with random.Random(23) from the listed answers that
# neither contain nor are contained in the first reference (normalized as in r20_build_leaderboard_pool.py); a question with no such
# answer is dropped. Answers and answer-list labels are unchanged; match groups are recomputed against the new reference.
# Each grader's score file is seeded with its existing blind calls (blind scores do not depend on the reference), so the harness adds
# only referenced calls. Run from experiments/tfa-vs-judge.
# Outputs: runs/r22/redraw_pool.jsonl (field ref = second draw, ref_draw1 = first draw, group_draw1 = first-draw groups);
# runs/r22/redraw_{sonnet,opus,haiku}_api/pool.jsonl (seeded blind rows).
import json
import os
import random
import re

GRADERS = {"sonnet": "runs/r20/leaderboard_sonnet_api/pool.jsonl", "opus": "runs/r21/leaderboard_opus_api/pool.jsonl",
           "haiku": "runs/r21/leaderboard_haiku_api/pool.jsonl"}


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


def contains(a, v):
    na, nv = norm(a), norm(v)
    return na == nv or (len(nv) > 3 and nv in na)


rng = random.Random(23)
tasks = {t["problem_id"]: t for t in map(json.loads, open("runs/mace_tasks.jsonl"))}
os.makedirs("runs/r22", exist_ok=True)
out, dropped = [], []
for t in map(json.loads, open("runs/r20/mace_gen/pool.jsonl")):
    old = t["ref"]
    cands = [v for v in tasks[t["problem_id"]]["valid_answers"] if not contains(v, old) and not contains(old, v)]
    if not cands:
        dropped.append(t["problem_id"])
        continue
    new = rng.choice(sorted(cands))
    groups = []
    for s, ok in zip(t["samples"], t["oracle"]):
        a = boxed(s) or s[-200:]
        groups.append("invalid" if not ok else ("match" if contains(a, new) else "nonmatch"))
    out.append(dict(t, ref=new, ref_draw1=old, group=groups, group_draw1=t["group"]))
with open("runs/r22/redraw_pool.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")
keep = {r["problem_id"] for r in out}
for g, src in GRADERS.items():
    dst = f"runs/r22/redraw_{g}_api/pool.jsonl"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        print("[exists]", dst)
        continue
    with open(dst, "w") as f:
        n = 0
        for l in open(src):
            r = json.loads(l)
            if r["cond"] == "noref" and r["problem_id"] in keep and r.get("score") is not None and not r.get("error"):
                f.write(json.dumps(r) + "\n")
                n += 1
    print(f"[seeded] {dst}: {n} blind rows")
moved = sum(g1 != g2 for r in out for g1, g2 in zip(r["group_draw1"], r["group"]))
print(f"redraw pool: {len(out)} questions, {len(dropped)} dropped (no alternative answer), {moved} answers change group")
