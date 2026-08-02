#!/usr/bin/env python
# Causal nuisance certificate: intervene on SURFACE (length / formatting) while holding the correct
# answer's content fixed, re-judge fresh, and measure each judge's score sensitivity. An unbiased judge
# gives ~0 change; a surface-biased judge moves. Perturbations are mechanical and content-preserving, so
# there is no "the rewrite added quality" confound.
#   orig2    : fresh re-judge of the original (controls RTM + judge noise)
#   verbose  : same content with benign connective filler + preamble (non-redundant extra length)
#   reformat : same words wrapped in markdown step headers (pure formatting surface, no new words)
#   dup      : redundant duplication (extreme length)
# Runs both judges: GPT-5.2 via litellm, Opus 4.8 via `claude -p` (session login).
import argparse, glob, json, random, statistics
from concurrent.futures import ThreadPoolExecutor
from tfa.judge import build_prompt, _parse_score
from run_judge_cli import judge_via_cli
from judge_nuisance import load_cc

CONNS = ["Now, ", "Next, ", "To be clear, ", "As a result, ", "Observe that ", "Carefully, "]

def dup(t):
    t = t or ""
    return t + "\n\nTo be thorough, here is the same solution restated step by step:\n" + t

def verbose(t):
    lines = [l for l in (t or "").split("\n") if l.strip()]
    body = "\n".join(CONNS[i % len(CONNS)] + l for i, l in enumerate(lines))
    return ("Let me solve this problem carefully, explaining each step in detail.\n\n" + body +
            "\n\nThus, after careful step-by-step reasoning, we arrive at the final result stated above.")

def reformat(t):
    lines = [l for l in (t or "").split("\n") if l.strip()]
    return "\n".join(f"**Step {i+1}.** {l}" for i, l in enumerate(lines))

VARIANTS = {"orig2": lambda t: t, "verbose": verbose, "reformat": reformat, "dup": dup}

def judge_gpt(prompt, model="openai/gpt-5.2"):
    import litellm
    litellm.drop_params = True
    try:
        r = litellm.completion(model=model, messages=[{"role": "user", "content": prompt}],
                               temperature=0.0, seed=0, max_tokens=400)
        return _parse_score(r.choices[0].message.content or "")
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--globs", default="runs/gsm8k/*.judged.opus.jsonl")
    ap.add_argument("--scores", default="runs/scores_gsm8k.jsonl")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--max_score", type=float, default=9.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--out", default="runs/causal_battery_gsm8k.jsonl")
    args = ap.parse_args()

    cc = load_cc(args.scores)
    pool = []
    for f in glob.glob(args.globs):
        for line in open(f):
            r = json.loads(line)
            old = r.get("judge_score")
            if cc.get((r.get("model"), r.get("problem_id"))) == 1.0 and r.get("free_gen") \
               and old is not None and float(old) <= args.max_score:
                pool.append(r)
    random.Random(0).shuffle(pool); pool = pool[:args.n]
    print(f"selected {len(pool)} correct non-ceiling items; {len(VARIANTS)} variants x 2 judges", flush=True)

    jobs = []  # (pid, model, variant, prompt)
    for r in pool:
        q, g = r["question"], r["gold_solution"]
        for v, fn in VARIANTS.items():
            jobs.append((r["problem_id"], r["model"], v, build_prompt(q, g, fn(r["free_gen"]))))

    def run_opus(j):
        pid, m, v, p = j; return (pid, m, v, "opus", judge_via_cli(p, "claude-opus-4-8", args.timeout))
    def run_gpt(j):
        pid, m, v, p = j; return (pid, m, v, "gpt", judge_gpt(p))

    res = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        res += list(ex.map(run_opus, jobs)); print("opus done", flush=True)
    with ThreadPoolExecutor(max_workers=16) as ex:
        res += list(ex.map(run_gpt, jobs)); print("gpt done", flush=True)

    by = {}
    for pid, m, v, judge, s in res:
        by.setdefault((pid, m), {})[f"{judge}_{v}"] = s
    rows = [dict(problem_id=p, model=m, **d) for (p, m), d in by.items()]
    with open(args.out, "w") as fo:
        for row in rows: fo.write(json.dumps(row) + "\n")

    def summ(judge, v):
        d = [row[f"{judge}_{v}"] - row[f"{judge}_orig2"] for row in rows
             if row.get(f"{judge}_{v}") is not None and row.get(f"{judge}_orig2") is not None]
        if not d: return "n/a"
        m = statistics.mean(d); se = (statistics.pstdev(d) / len(d) ** 0.5) if len(d) > 1 else 0
        return f"{m:+.2f} [{m-1.96*se:+.2f},{m+1.96*se:+.2f}] {100*sum(x>0 for x in d)/len(d):3.0f}%+ n={len(d)}"

    print(f"\nScore change vs orig2 (both fresh), by judge:")
    for judge in ("gpt", "opus"):
        print(f"  {judge.upper()}")
        for v in ("verbose", "reformat", "dup"):
            print(f"    {v:9s}: {summ(judge, v)}")
    print(f"\nwrote {args.out}")

if __name__ == "__main__":
    main()
