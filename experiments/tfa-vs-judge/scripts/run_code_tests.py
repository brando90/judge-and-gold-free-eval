# Execute regenerated HumanEval traces against official tests -> free ground-truth pass/fail.
import json, glob, re, subprocess, tempfile, os
OUT = "runs/code_traces_scored"
os.makedirs(OUT, exist_ok=True)
def extract(fg, question):
    m = re.findall(r"```(?:python)?\n(.*?)```", fg, re.S)
    if m:
        code = max(m, key=len)
        return code if "def " in code else question + code
    return question + fg if "def " not in fg else fg
for fp in glob.glob("runs/code_traces/humaneval__*.jsonl"):
    out = OUT + "/" + fp.split("/")[-1]
    if os.path.exists(out): print("skip", out, flush=True); continue
    rows = [json.loads(l) for l in open(fp)]
    with open(out, "w") as f:
        for r in rows:
            code = extract(r["free_gen"], r["question"])
            prog = code + "\n\n" + r["test"] + f"\n\ncheck({r['entry_point']})\n"
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
                tf.write(prog); path = tf.name
            try:
                p = subprocess.run(["python3", path], capture_output=True, timeout=10)
                ok = int(p.returncode == 0)
            except Exception:
                ok = 0
            os.unlink(path)
            f.write(json.dumps(dict(problem_id=r["problem_id"], model=r["model"], test_pass=ok)) + "\n")
    print("wrote", out, flush=True)
print("[tests-done]")
