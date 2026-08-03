# Code-domain replication of the verification phase change (P3-code).
# Take HumanEval canonical solutions, apply ONE subtle mechanical mutation (boundary/operator/off-by-one),
# and keep only mutants that (a) run without exception on the official tests, (b) FAIL at least one
# assertion (truly wrong), i.e. coherent-wrong code verified by a TRUE ORACLE (executing tests).
# Judges see docstring + candidate code, NO reference (realistic code-review mode). Conditions: mutant vs
# original canonical (control), paired per problem.
import json, re, random, subprocess, sys, tempfile, os

MUTS = [
    (r"<=", "<"), (r">=", ">"), (r"(?<![<>=!])<(?!=)", "<="), (r"(?<![<>=!])>(?!=)", ">="),
    (r"\+ 1\b", "+ 2"), (r"- 1\b", "- 2"), (r"\+ 1\)", "+ 2)"), (r"range\(1,", "range(2,"),
    (r"\band\b", "or"), (r"\bor\b", "and"), (r"== 0\b", "== 1"), (r"!= 0\b", "!= 1"),
    (r"\* 2\b", "* 3"), (r"// 2\b", "// 3"), (r"max\(", "min("), (r"min\(", "max("),
]

def run_tests(prompt, solution, test, entry_point, timeout=8):
    code = prompt + solution + "\n" + test + f"\n\ncheck({entry_point})\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code); path = f.name
    try:
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0: return "pass"
        return "assert_fail" if "AssertionError" in (r.stderr or "") else "error"
    except subprocess.TimeoutExpired:
        return "timeout"
    finally:
        os.unlink(path)

def main():
    from datasets import load_dataset
    ds = load_dataset("openai/openai_humaneval")["test"]
    rng = random.Random(0)
    tasks, tid, stats = [], 0, {"ok": 0, "equiv": 0, "crash": 0, "nomut": 0, "base_fail": 0}
    for r in ds:
        base = run_tests(r["prompt"], r["canonical_solution"], r["test"], r["entry_point"])
        if base != "pass": stats["base_fail"] += 1; continue
        # try mutations in random order until one yields coherent-wrong
        muts = MUTS[:]; rng.shuffle(muts)
        chosen = None
        for pat, rep in muts:
            if not re.search(pat, r["canonical_solution"]): continue
            # mutate exactly ONE occurrence (random)
            occ = [m for m in re.finditer(pat, r["canonical_solution"])]
            m = occ[rng.randrange(len(occ))]
            mut = r["canonical_solution"][:m.start()] + re.sub(pat, rep, m.group(0)) + r["canonical_solution"][m.end():]
            if mut == r["canonical_solution"]: continue
            res = run_tests(r["prompt"], mut, r["test"], r["entry_point"])
            if res == "assert_fail": chosen = mut; break
            elif res == "pass": stats["equiv"] += 1
            else: stats["crash"] += 1
        if chosen is None: stats["nomut"] += 1; continue
        stats["ok"] += 1
        q = r["prompt"]  # docstring+signature is the spec
        tasks.append(dict(task_id=tid, cond="mutant", pid=r["task_id"], dataset="humaneval",
                          solver="MUT", question=q, gold="(no reference solution provided)",
                          candidate=(q + chosen), cc=0.0, label_src="code_mutant", tfa=None)); tid += 1
        tasks.append(dict(task_id=tid, cond="orig", pid=r["task_id"], dataset="humaneval",
                          solver="MUT", question=q, gold="(no reference solution provided)",
                          candidate=(q + r["canonical_solution"]), cc=1.0, label_src="code_orig", tfa=None)); tid += 1
    with open("runs/code_mutant_tasks.jsonl", "w") as f:
        for t in tasks: f.write(json.dumps(t) + "\n")
    print(f"stats: {stats} -> {stats['ok']} coherent-wrong mutants (+paired originals) = {len(tasks)} tasks")

if __name__ == "__main__":
    main()
