# R27-B post hoc descriptives (not registered; reported as post hoc). Run from experiments/tfa-vs-judge.
# On the registered R27-B question set (both answers labeled, every condition graded), for each judge:
#   1. false acceptance per referenced condition, restricted to answers that state an "Answer:" line (generation not cut off);
#   2. among solve-first false acceptances with the reference, the share whose reply (last 300 characters stored) says the reference
#      is wrong (regex below), a lower bound because only the reply's tail is stored.
import json
import re
import sys

JUDGES = sys.argv[1:] or ["gpt41", "sonnet"]
ANSWER_LINE = re.compile(r"answer\s*:", re.I)
REF_WRONG = re.compile(r"reference(?: answer)?[^.]{0,80}\b(incorrect|wrong|not correct|mistaken|typo|error)|"
                       r"\b(incorrect|wrong|mistaken)\b[^.]{0,20}reference", re.I)
CONDS = ("hle|ref", "direct|noref", "direct|ref", "solve|noref", "solve|ref")


def graded(path):
    out = {}
    for line in open(path):
        r = json.loads(line)
        if r.get("score") is not None and not r.get("error"):
            out[(r["problem_id"], r["idx"], r.get("cond", "ref"))] = r
    return out


labels = {(k[0], k[1]): r["score"] for k, r in graded("runs/r27/labels_o3mini/pool.jsonl").items()}
pool = {t["problem_id"]: t for t in map(json.loads, open("runs/r27/hle_pool.jsonl"))}
result = {"note": "post hoc; R27-B question set", "judges": {}}
for j in JUDGES:
    cells = {t: graded(f"runs/r27/hle_{t}_{j}/scores.jsonl") for t in ("hle", "direct", "solve")}

    def score(cond, pid, idx):
        t, c = cond.split("|")
        r = cells[t].get((pid, idx, c))
        return None if r is None else r["score"]

    qs = [pid for pid, t in pool.items()
          if all((pid, i) in labels for i in t["idx"]) and all(score(c, pid, i) is not None for c in CONDS for i in t["idx"])]
    wrong = [(pid, i, j2) for pid in qs for j2, i in enumerate(pool[pid]["idx"]) if labels[(pid, i)] == 0.0]
    stated = [w for w in wrong if ANSWER_LINE.search(re.sub(r"[*_`]", "", pool[w[0]]["samples"][w[2]]))]
    d = {"questions": len(qs), "wrong": len(wrong), "wrong_with_answer_line": len(stated), "false_acceptance_answer_line": {}}
    for c in CONDS:
        d["false_acceptance_answer_line"][c] = round(sum(score(c, pid, i) == 10.0 for pid, i, _ in stated) / len(stated), 6)
    fa = [(pid, i) for pid, i, _ in wrong if score("solve|ref", pid, i) == 10.0]
    says = sum(bool(REF_WRONG.search(cells["solve"][(pid, i, "ref")].get("tail", ""))) for pid, i in fa)
    d["solve_ref_false_acceptances"] = len(fa)
    d["solve_ref_fa_reply_says_reference_wrong"] = [says, round(says / len(fa), 6) if fa else None]
    result["judges"][j] = d
json.dump(result, open(f"../../papers/analysis/r27b_posthoc_{'_'.join(JUDGES)}.json", "w"), indent=1)
print(json.dumps(result, indent=1))
