# Model-critic panel: grade traces on the SAME blind soundness/style rubric the humans use.
# Critics from two families: gpt-5.2 (metered OpenAI) and Opus 4.8 (free claude -p session).
# Purpose: (a) calibrate critics against the human labels on the overlap; (b) provisional
# coverage of unlabeled items so analysis is not blocked on human throughput.
#   python scripts/critic_panel.py <traces.jsonl> <critic: gpt|opus> <out.jsonl> [--cells R]
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

traces_f, critic, out_f = sys.argv[1], sys.argv[2], sys.argv[3]
cells = sys.argv[5].split(",") if len(sys.argv) > 5 and sys.argv[4] == "--cells" else None

RUBRIC = """You are grading the REASONING QUALITY of a model's solution. You see the problem, a
known-correct reference solution, and the model's solution to grade. Grade two INDEPENDENT scales:

soundness (0-10): is every step valid and does the argument actually establish the answer?
Ignore wording, length, and formatting. Anchors: 2 = major logical error or unjustified leap;
5 = partly justified, real gaps; 8 = fully valid, at most minor slips.

style (0-10): how clear, organized, and readable is the writing, independent of correctness?
A wrong answer can still score high. Anchors: 2 = confusing or rambling; 5 = readable;
8 = clear and well-structured.

Also: lucky = "yes" if the final answer is right but reached through unsound/incomplete reasoning, else "no".

Reply with ONLY a JSON object: {"soundness": <int>, "style": <int>, "lucky": "<yes|no>"}

PROBLEM:
{q}

REFERENCE SOLUTION:
{g}

MODEL SOLUTION TO GRADE:
{t}
"""

def build(r):
    return RUBRIC.replace("{q}", r["question"][:4000]).replace("{g}", r["gold_solution"][:4000]).replace("{t}", r["trace"][:6000])

def call_gpt(p):
    from litellm import completion
    r = completion(model="openai/gpt-5.2", messages=[{"role": "user", "content": p}], timeout=120)
    return r.choices[0].message.content

def call_opus(p):
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    r = subprocess.run(["claude", "-p", "--model", "claude-opus-4-8", p],
                       capture_output=True, text=True, timeout=240, env=env)
    return r.stdout

CALL = {"gpt": call_gpt, "opus": call_opus}[critic]

def parse(txt):
    m = re.search(r"\{[^{}]*\}", txt or "")
    if not m: return None
    try:
        d = json.loads(m.group(0))
        return dict(soundness=float(d["soundness"]), style=float(d["style"]), lucky=str(d.get("lucky", "")))
    except Exception:
        return None

rows = [json.loads(l) for l in open(traces_f)]
if cells: rows = [r for r in rows if r.get("cell") in cells]
done = set()
if os.path.exists(out_f):
    done = {json.loads(l)["id"] for l in open(out_f)}
todo = [r for r in rows if r["id"] not in done]
print(f"{critic}: {len(done)} done, {len(todo)} to grade", flush=True)

def work(r):
    try:
        g = parse(CALL(build(r)))
    except Exception as e:
        g = None
    return dict(id=r["id"], critic=critic, **(g or {}), ok=g is not None)

with open(out_f, "a") as f, ThreadPoolExecutor(max_workers=4) as ex:
    for i, res in enumerate(ex.map(work, todo)):
        f.write(json.dumps(res) + "\n"); f.flush()
        if (i+1) % 25 == 0: print(f"{i+1}/{len(todo)}", flush=True)
n_ok = sum(1 for l in open(out_f) if json.loads(l).get("ok"))
print(f"[panel-done] {critic}: {n_ok} graded ok")
