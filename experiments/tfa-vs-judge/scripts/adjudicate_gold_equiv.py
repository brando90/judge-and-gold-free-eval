# Second pass on runs/rb2_math_gold.jsonl: strict string matching under-counts agreement
# (unicode minus, units spelled out, 18^4 vs 104976). For rows where both families answered
# but the strings differ, ask Opus (free CLI session) whether the two answers express the
# same result. Marks agree=True + gold=gpt_answer where EQUIVALENT. Rewrites the file.
import json, os, subprocess
from concurrent.futures import ThreadPoolExecutor

F = "runs/rb2_math_gold.jsonl"
rows = [json.loads(l) for l in open(F)]
disputed = [r for r in rows if not r["agree"] and r["gpt_answer"] and r["opus_answer"]]
print(f"{len(disputed)} disputed rows to adjudicate")

PROMPT = ("Two people answered the same math question. Decide whether their final answers express "
          "the same result, ignoring formatting, notation, rounding style, and whether units are "
          "abbreviated or spelled out. Reply with exactly one word: EQUIVALENT or DIFFERENT.\n\n"
          "Question:\n{q}\n\nAnswer 1: {a}\n\nAnswer 2: {b}\n")

def check(r):
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    p = subprocess.run(["claude", "-p", "--model", "claude-opus-4-8",
                        PROMPT.format(q=r["question"][:2000], a=r["gpt_answer"], b=r["opus_answer"])],
                       capture_output=True, text=True, timeout=240, env=env)
    verdict = "EQUIVALENT" in p.stdout.upper() and "DIFFERENT" not in p.stdout.upper().replace("EQUIVALENT", "")
    return r["pid"], verdict, p.stdout.strip()[:80]

with ThreadPoolExecutor(max_workers=4) as ex:
    results = dict((pid, (v, txt)) for pid, v, txt in ex.map(check, disputed))

n_up = 0
for r in rows:
    if r["pid"] in results:
        v, txt = results[r["pid"]]
        r["equiv_verdict"] = txt
        if v:
            r["agree"] = True; r["gold"] = r["gpt_answer"]; r["agree_via"] = "opus_equivalence"; n_up += 1
with open(F, "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print(f"upgraded {n_up} of {len(disputed)} disputed rows to agree")
print("total agreed now:", sum(1 for r in rows if r["agree"]), "/", len(rows))
