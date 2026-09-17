#!/usr/bin/env python
# R30-B (papers/D-iclr-v5/registration_round30.md): the benchmark pool with a reference that is CHOSEN
# rather than drawn at random. Two pre-specified rules over the listed answers in runs/mace_tasks.jsonl:
#
#   first   ref := valid_answers[0]. Exogenous: it uses MACE's own ordering and nothing about our models.
#   modal   ref := the listed answer produced by most of the four answering models. A model answer counts
#           for the FIRST listed answer it matches, in list order. Ties are broken by list order. Questions
#           where no model produces a listed answer fall back to first-listed and are flagged and counted.
#
# Answers, oracle labels and answer lists are unchanged; only the reference and the match groups differ.
# Groups are recomputed with the normalized-containment rule of r20_build_leaderboard_pool.py, which is the
# same rule r22_build_redraw_pool.py used, so the new groups are comparable with the existing ones.
#
# No blind rows are seeded. The shipped SimpleQA and BrowseComp/HLE graders have no blind condition at all
# (runs/r24/std_*/pool.jsonl hold only ref and reflist), and this part's baseline is answer-list accuracy,
# which is the pool's own oracle field rather than a blind grader run.
#
# Run from experiments/tfa-vs-judge. Writes:
#   runs/r30/canon_first_pool.jsonl, runs/r30/canon_modal_pool.jsonl
# Each row keeps every field of the source pool and adds: ref (the chosen reference), ref_draw (the original
# random draw), group (recomputed), group_draw (the original groups), rule, and modal_fallback.
import collections
import json
import os
import re

SRC = "runs/r20/mace_gen/pool.jsonl"
TASKS = "runs/mace_tasks.jsonl"
OUT = {"first": "runs/r30/canon_first_pool.jsonl", "modal": "runs/r30/canon_modal_pool.jsonl"}


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


def answer_of(sample):
    return boxed(sample) or sample[-200:]


def groups_for(t, ref):
    out = []
    for s, ok in zip(t["samples"], t["oracle"]):
        a = answer_of(s)
        out.append("invalid" if not ok else ("match" if contains(a, ref) else "nonmatch"))
    return out


def modal_ref(t, valid):
    """The listed answer most of the models produce; ties and no-match fall back to list order."""
    counts = collections.Counter()
    for s, ok in zip(t["samples"], t["oracle"]):
        if not ok:
            continue
        a = answer_of(s)
        for v in valid:                      # first listed answer this model answer matches
            if contains(a, v):
                counts[v] += 1
                break
    if not counts:
        return valid[0], True                # fallback, flagged
    top = max(counts.values())
    return next(v for v in valid if counts.get(v, 0) == top), False   # ties -> list order


tasks = {t["problem_id"]: t for t in map(json.loads, open(TASKS))}
pool = [json.loads(l) for l in open(SRC)]
os.makedirs("runs/r30", exist_ok=True)

for rule, path in OUT.items():
    rows, changed, fallback, moved = [], 0, 0, 0
    for t in pool:
        valid = tasks[t["problem_id"]]["valid_answers"]
        if rule == "first":
            ref, fb = valid[0], False
        else:
            ref, fb = modal_ref(t, valid)
        groups = groups_for(t, ref)
        changed += norm(ref) != norm(t["ref"])
        fallback += fb
        moved += sum(a != b for a, b in zip(t["group"], groups))
        rows.append(dict(t, ref=ref, ref_draw=t["ref"], group=groups, group_draw=t["group"],
                         rule=rule, modal_fallback=fb))
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    n_ans = sum(len(r["samples"]) for r in rows)
    print(f"[{rule}] {path}: {len(rows)} questions, {changed} change reference, "
          f"{moved} of {n_ans} answers change match group, {fallback} modal fallbacks")
