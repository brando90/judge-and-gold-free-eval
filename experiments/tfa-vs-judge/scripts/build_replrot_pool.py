# Build the ROTATED-REFERENCE replication pool for the fresh exact-oracle rotation
# replication (P-RR1..P-RR3, registered in papers/analysis/replrot_analysis.py, committed
# together with this file BEFORE any rotated judging runs).
#
# Motivation. The original rotation experiment (paper D, P1) inherits the exploratory Ties
# pool and its incomplete enumerated-set checker. External review named a fresh rotation
# replication on an exact-oracle pool as the single highest-value confirmatory run. This
# builds it from the FROZEN 120-item replication pool (exact programmatic oracles, stored
# full valid sets, Llama-3.1-8B generator): identical samples, identical oracle, the ONLY
# change is which valid answer occupies ref_answer.
#
# Rotation rule (pinned; POOL-AWARE like the original rotation, disclosed as such): for each
# item, among valid_answers excluding the original ref_answer, pick the one most frequent as
# a loose-normalized boxed answer among the item's oracle-VALID samples (ties broken by
# sorted answer string). Items with no valid non-matching answer present in the pool keep
# the first alternative valid answer (sorted) and are excluded from gainer/loser readouts by
# the analysis, which recomputes membership per item. Pool-awareness biases nothing within
# an item: the same-sample paired readout compares the identical text under two references.
#
# Output: runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl (pool rows with
# rotated ref_answer; carries rot_from = original ref_answer for the analysis).
import json
import re

def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None

def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + 7, 1
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]

tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/repl_main_tasks.jsonl")}
rows = [json.loads(l) for l in open("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl")]
out = open("runs/bon/bon_replrot__meta-llama__Llama-3.1-8B-Instruct.jsonl", "w")
n_pool_aware = n_fallback = 0
for r in rows:
    t = tasks[r["problem_id"]]
    orig = r.get("ref_answer", t["ref_answer"])
    alts = [a for a in t["valid_answers"] if norm(a) != norm(orig)]
    counts = {}
    for s, ok in zip(r["samples"], r["oracle"]):
        if not ok:
            continue
        b = norm(extract_boxed(s) or s)
        for a in alts:
            if norm(a) == b:
                counts[a] = counts.get(a, 0) + 1
    if counts:
        rot = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        n_pool_aware += 1
    else:
        rot = sorted(alts)[0]
        n_fallback += 1
    q = dict(r)
    q["rot_from"] = orig
    q["ref_answer"] = rot
    out.write(json.dumps(q) + "\n")
out.close()
print(f"[build_replrot_pool] {len(rows)} items: {n_pool_aware} pool-aware rotations, "
      f"{n_fallback} fallback (no valid non-matching answer in pool)")
