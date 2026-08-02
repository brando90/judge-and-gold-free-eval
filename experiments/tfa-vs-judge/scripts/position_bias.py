#!/usr/bin/env python
# Known-bias validation for the causal method: position bias in PAIRWISE judging (the canonical,
# well-documented judge bias). Take two near-equal-quality answers (both correct) to the same problem,
# present them as (A,B) and (B,A), and see if the verdict depends on ORDER rather than content.
#   p(first)   : fraction of verdicts choosing the first-shown candidate. 0.5 = unbiased; away = position bias.
#   consistent : fraction of pairs where the SAME actual answer wins under both orders (content-driven).
# If the causal method is sensitive, a real bias like this should show up (p(first) != 0.5 / low consistency).
import argparse, glob, json, re, random, collections
from concurrent.futures import ThreadPoolExecutor
from run_judge_cli import judge_via_cli
from judge_nuisance import load_cc

RUBRIC_PAIR = """You are comparing two candidate solutions to a math problem for REASONING QUALITY.
Problem:
{q}

Gold reference solution:
{g}

Candidate A:
{A}

Candidate B:
{B}

Which candidate shows better reasoning? Return STRICT JSON only: {{"winner": "A"}} or {{"winner": "B"}}."""

def winner(text):
    if not text: return None
    m = re.search(r'"winner"\s*:\s*"?([AB])', text)
    if m: return m.group(1)
    m = re.search(r"\b([AB])\b", text.strip()[-8:])
    return m.group(1) if m else None

def judge_gpt(prompt, model="openai/gpt-5.2"):
    import litellm
    litellm.drop_params = True
    try:
        r = litellm.completion(model=model, messages=[{"role": "user", "content": prompt}],
                               temperature=0.0, seed=0, max_tokens=100)
        return winner(r.choices[0].message.content or "")
    except Exception:
        return None

def judge_opus(prompt, timeout=120):
    out = judge_via_cli.__globals__  # reuse subprocess env stripping
    import subprocess, os
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    r = subprocess.run(["claude", "-p", "--model", "claude-opus-4-8"], input=prompt,
                       capture_output=True, text=True, env=env, timeout=timeout)
    return winner(r.stdout or "") if r.returncode == 0 else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--globs", default="runs/gsm8k/*.judged.opus.jsonl")
    ap.add_argument("--scores", default="runs/scores_gsm8k.jsonl")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default="runs/position_bias_gsm8k.jsonl")
    args = ap.parse_args()

    cc = load_cc(args.scores)
    byq = collections.defaultdict(list)
    for f in glob.glob(args.globs):
        for line in open(f):
            r = json.loads(line)
            if cc.get((r.get("model"), r.get("problem_id"))) == 1.0 and r.get("free_gen"):
                byq[r["problem_id"]].append(r)
    pairs = []
    for pid, rs in byq.items():
        if len(rs) >= 2:
            a, b = random.Random(hash(pid) & 0xffff).sample(rs, 2)
            if a["free_gen"] != b["free_gen"]:
                pairs.append((pid, a["question"], a["gold_solution"], a["free_gen"], b["free_gen"]))
    random.Random(0).shuffle(pairs); pairs = pairs[:args.n]
    print(f"{len(pairs)} near-equal (both-correct) pairs; 2 orders x 2 judges = {4*len(pairs)} calls", flush=True)

    jobs = []  # (pid, order, judge, prompt); order 0 = (x,y), 1 = (y,x)
    for pid, q, g, x, y in pairs:
        jobs.append((pid, 0, RUBRIC_PAIR.format(q=q, g=g, A=x, B=y)))
        jobs.append((pid, 1, RUBRIC_PAIR.format(q=q, g=g, A=y, B=x)))

    def run_opus(j): pid, o, p = j; return (pid, o, "opus", judge_opus(p))
    def run_gpt(j):  pid, o, p = j; return (pid, o, "gpt", judge_gpt(p))
    res = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        res += list(ex.map(run_opus, jobs)); print("opus done", flush=True)
    with ThreadPoolExecutor(max_workers=16) as ex:
        res += list(ex.map(run_gpt, jobs)); print("gpt done", flush=True)

    D = collections.defaultdict(dict)  # (pid,judge) -> {order:winner}
    for pid, o, judge, w in res:
        D[(pid, judge)][o] = w
    rows = [dict(problem_id=pid, judge=judge, order0=d.get(0), order1=d.get(1)) for (pid, judge), d in D.items()]
    with open(args.out, "w") as fo:
        for row in rows: fo.write(json.dumps(row) + "\n")

    print("\nPosition bias by judge (near-equal pairs):")
    for judge in ("gpt", "opus"):
        ws = [(r["order0"], r["order1"]) for r in rows if r["judge"] == judge and r["order0"] and r["order1"]]
        if not ws: print(f"  {judge}: n/a"); continue
        allw = [w for pair in ws for w in pair]
        p_first = sum(w == "A" for w in allw) / len(allw)
        # consistent = same actual answer wins: order0 winner maps x->A/y->B; order1 winner maps y->A/x->B
        consistent = sum(1 for a, b in ws if {a, b} == {"A", "B"}) / len(ws)  # A then B (or B then A) = same answer
        print(f"  {judge.upper()}: p(pick first)={p_first:.2f}  consistent(content-driven)={consistent:.2f}  n={len(ws)}")
    print(f"\nwrote {args.out}")

if __name__ == "__main__":
    main()
