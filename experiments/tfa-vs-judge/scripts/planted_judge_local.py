#!/usr/bin/env python
# Judge the planted-error tasks with the two frontier judges (Opus via claude -p, GPT via litellm)
# and print the causal detection table: mean score drop vs orig2 per (position x magnitude) cell.
import argparse, json, os, re, subprocess, collections, numpy as np
from concurrent.futures import ThreadPoolExecutor

RUBRIC = open_rubric = None
from tfa.judge import build_prompt, _parse_score

def opus(prompt, timeout=120):
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    r = subprocess.run(["claude", "-p", "--model", "claude-opus-4-8"], input=prompt,
                       capture_output=True, text=True, env=env, timeout=timeout)
    return _parse_score(r.stdout or "") if r.returncode == 0 else None

def gpt(prompt):
    import litellm; litellm.drop_params = True
    try:
        r = litellm.completion(model="openai/gpt-5.2", messages=[{"role": "user", "content": prompt}],
                               temperature=0.0, seed=0, max_tokens=300)
        return _parse_score(r.choices[0].message.content or "")
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="runs/planted_tasks.jsonl")
    ap.add_argument("--judges", default="opus,gpt")
    ap.add_argument("--workers_opus", type=int, default=8)
    ap.add_argument("--workers_gpt", type=int, default=16)
    ap.add_argument("--out", default="runs/planted_scores.jsonl")
    args = ap.parse_args()

    tasks = [json.loads(l) for l in open(args.tasks)]
    prompts = [(t, build_prompt(t["question"], t["gold"], t["candidate"])) for t in tasks]
    rows = []
    if "opus" in args.judges:
        with ThreadPoolExecutor(max_workers=args.workers_opus) as ex:
            scores = list(ex.map(lambda tp: opus(tp[1]), prompts))
        rows += [dict(judge="opus", task_id=t["task_id"], pid=t["pid"], cond=t["cond"], score=s)
                 for (t, _), s in zip(prompts, scores)]
        print("opus done", flush=True)
    if "gpt" in args.judges:
        with ThreadPoolExecutor(max_workers=args.workers_gpt) as ex:
            scores = list(ex.map(lambda tp: gpt(tp[1]), prompts))
        rows += [dict(judge="gpt", task_id=t["task_id"], pid=t["pid"], cond=t["cond"], score=s)
                 for (t, _), s in zip(prompts, scores)]
        print("gpt done", flush=True)
    with open(args.out, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")

    # paired detection table
    by = collections.defaultdict(dict)
    for r in rows:
        if r["score"] is not None: by[(r["judge"], r["pid"])][r["cond"]] = r["score"]
    print(f"\nCausal detection (score DROP vs orig2; higher drop = error detected):")
    print(f"{'judge':6s} {'cond':12s} {'drop':>7s} {'95% CI':>16s} {'%detected(drop>=3)':>18s} {'n':>4s}")
    RNG = np.random.RandomState(0)
    for judge in ("gpt", "opus"):
        for cond in ("early_gross", "early_small", "late_gross", "late_small"):
            d = [v["orig2"] - v[cond] for (j, _), v in by.items()
                 if j == judge and "orig2" in v and cond in v]
            if len(d) < 20: continue
            d = np.array(d); boot = [np.mean(d[RNG.randint(0, len(d), len(d))]) for _ in range(2000)]
            lo, hi = np.percentile(boot, [2.5, 97.5])
            det = 100 * float(np.mean(d >= 3))
            print(f"{judge:6s} {cond:12s} {d.mean():7.2f} [{lo:6.2f},{hi:6.2f}] {det:17.0f}% {len(d):4d}")

if __name__ == "__main__":
    main()
