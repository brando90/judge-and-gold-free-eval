# Build independently verified gold answers for the RB2 math subset, so a genuine
# "correct reference" arm can be added to the Part-4 experiment without leaking the label.
# Two frontier families solve each prompt; we keep only prompts where their FINAL answers
# agree (same two-family adjudication standard as the Part-1 answer-key work).
#   GPT arm  : metered OpenAI key (source veribench .env first)
#   Opus arm : free `claude -p` session login (never the metered ANTHROPIC_API_KEY)
# Output: runs/rb2_math_gold.jsonl  {pid, question, gpt_answer, opus_answer, agree, gold}
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

PROMPTS = json.load(open("/Users/srivatsavadaruru/.claude/jobs/8e09e785/tmp/rb2_math_prompts.json"))
OUT = "runs/rb2_math_gold.jsonl"
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

def gpt_solve(q):
    from litellm import completion
    r = completion(model="openai/gpt-5.2", messages=[{"role": "user", "content": SOLVE + q}], timeout=120)
    return r.choices[0].message.content

def opus_solve(q):
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    p = subprocess.run(["claude", "-p", "--model", "claude-opus-4-8", SOLVE + q],
                       capture_output=True, text=True, timeout=240, env=env)
    return p.stdout

def work(item):
    pid, q = item
    row = {"pid": pid, "question": q}
    try: row["gpt_raw"] = gpt_solve(q)
    except Exception as e: row["gpt_raw"] = None; row["gpt_err"] = str(e)[:200]
    try: row["opus_raw"] = opus_solve(q)
    except Exception as e: row["opus_raw"] = None; row["opus_err"] = str(e)[:200]
    row["gpt_answer"] = final_of(row.get("gpt_raw"))
    row["opus_answer"] = final_of(row.get("opus_raw"))
    row["agree"] = norm(row["gpt_answer"]) is not None and norm(row["gpt_answer"]) == norm(row["opus_answer"])
    row["gold"] = row["gpt_answer"] if row["agree"] else None
    return row

done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        done.add(json.loads(l)["pid"])
todo = [(p, q) for p, q in PROMPTS.items() if p not in done]
print(f"{len(done)} done, {len(todo)} to solve", flush=True)
with open(OUT, "a") as f, ThreadPoolExecutor(max_workers=4) as ex:
    for i, row in enumerate(ex.map(work, todo)):
        keep = {k: v for k, v in row.items() if k not in ("gpt_raw", "opus_raw")}
        f.write(json.dumps(keep) + "\n"); f.flush()
        if (i + 1) % 10 == 0: print(f"{i+1}/{len(todo)}", flush=True)
n_agree = sum(1 for l in open(OUT) if json.loads(l)["agree"])
print(f"TOTAL {len(done)+len(todo)} | two-family agreement on {n_agree}")
