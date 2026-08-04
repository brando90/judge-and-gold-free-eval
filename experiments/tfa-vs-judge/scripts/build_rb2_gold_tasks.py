# Build the gold-reference arm for the RB2 math subset.
# Pass 1 output (gen_rb2_math_gold.py) gives two-family-verified final answers.
# This script: (a) re-collects GPT's FULL worked solution for each agreed prompt, so the
# reference is a complete response like the other arms (own/weak/mid), not a bare answer;
# (b) keeps a solution only if its final line still matches the verified gold answer;
# (c) writes runs/rb2_gold_tasks.jsonl in the exact pairref schema of runs/rb2_tasks.jsonl
#     (question, gold, A, B, cond CW/WC), restricted to agreed pids.
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor

GOLD = "runs/rb2_math_gold.jsonl"
TASKS = "runs/rb2_tasks.jsonl"
SOLS = "runs/rb2_math_gold_solutions.jsonl"
OUT = "runs/rb2_gold_tasks.jsonl"
SOLVE = ("Solve this problem. Think briefly, then give your final answer on the last line "
         "in the exact form:\nFINAL: <answer>\n\nProblem:\n")

def final_of(text):
    m = re.findall(r"FINAL:\s*(.+)", text or "")
    return m[-1].strip() if m else None

def norm(a):
    if a is None: return None
    s = a.strip().strip("$").replace(",", "").rstrip(".").strip()
    s = re.sub(r"\\boxed\{(.*)\}", r"\1", s).strip()
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else str(f)
    except ValueError:
        return re.sub(r"\s+", " ", s.lower())

gold = {json.loads(l)["pid"]: json.loads(l) for l in open(GOLD)}
agreed = {p: g for p, g in gold.items() if g["agree"]}
print(f"{len(agreed)}/{len(gold)} prompts have two-family-verified answers")

done = {}
if os.path.exists(SOLS):
    done = {json.loads(l)["pid"]: json.loads(l) for l in open(SOLS)}
todo = [p for p in agreed if p not in done]
if todo:
    from litellm import completion
    def solve(pid):
        q = agreed[pid]["question"]
        r = completion(model="openai/gpt-5.2", messages=[{"role": "user", "content": SOLVE + q}], timeout=120)
        return dict(pid=pid, solution=r.choices[0].message.content)
    with open(SOLS, "a") as f, ThreadPoolExecutor(max_workers=4) as ex:
        for row in ex.map(solve, todo):
            f.write(json.dumps(row) + "\n"); f.flush(); done[row["pid"]] = row
    print(f"collected {len(todo)} full solutions")

kept, dropped = {}, 0
for pid, g in agreed.items():
    sol = done.get(pid, {}).get("solution")
    if sol and norm(final_of(sol)) == norm(g["gold"]):
        kept[pid] = sol
    else:
        dropped += 1
print(f"kept {len(kept)} solutions whose final answer matches the verified gold ({dropped} dropped)")

rows = [json.loads(l) for l in open(TASKS)]
n = 0
with open(OUT, "w") as f:
    for r in rows:
        if r["dataset"] == "rb2_Math" and r["pid"] in kept:
            r = dict(r); r["gold"] = kept[r["pid"]]; r["label_src"] = "two_family_verified_gold"
            f.write(json.dumps(r) + "\n"); n += 1
print(f"wrote {OUT}: {n} rows ({n//2} pairs x 2 orders)")
