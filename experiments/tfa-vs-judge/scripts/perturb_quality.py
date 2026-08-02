#!/usr/bin/env python
# Coherence check for the certificate's quality axis under surface perturbations.
# On a BALANCED sample (equal correct/incorrect, so accuracy has variance), re-judge under conditions:
#   orig     : graded rubric, original text
#   verbose  : graded rubric, text + connective filler (more length, no content)
#   reformat : graded rubric, text wrapped in markdown step headers
#   binary   : binary "is the final answer correct?" rubric, original text
# For each condition report corr(score, accuracy) and the quality signal (= corr^2), plus the mean score
# change vs orig. Two questions answered: (a) does the quality signal stay put under length/format
# perturbations (i.e. does it move only when scores move)? (b) does the binary rubric inflate the quality
# signal -- and is that "better" or just redundant with the cheap correctness check we already have?
import argparse, glob, json, re, random, os, subprocess
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from tfa.judge import build_prompt, _parse_score
from judge_nuisance import load_cc

CONNS = ["Now, ", "Next, ", "To be clear, ", "As a result, ", "Observe that ", "Carefully, "]
def verbose(t):
    lines = [l for l in (t or "").split("\n") if l.strip()]
    body = "\n".join(CONNS[i % len(CONNS)] + l for i, l in enumerate(lines))
    return "Let me solve this carefully, step by step.\n\n" + body + "\n\nThus we reach the result above."
def reformat(t):
    lines = [l for l in (t or "").split("\n") if l.strip()]
    return "\n".join(f"**Step {i+1}.** {l}" for i, l in enumerate(lines))

RUBRIC_BINARY = """Determine whether the candidate solution's FINAL ANSWER is correct, using the gold reference.
Problem:
{question}

Gold reference solution:
{gold}

Candidate solution:
{candidate}

Return STRICT JSON only: {{"score": 10}} if the final answer is correct, else {{"score": 0}}."""

def gpt(prompt, mt=400):
    import litellm; litellm.drop_params = True
    try:
        r = litellm.completion(model="openai/gpt-5.2", messages=[{"role": "user", "content": prompt}],
                               temperature=0.0, seed=0, max_tokens=mt)
        return _parse_score(r.choices[0].message.content or "")
    except Exception:
        return None
def opus(prompt, mt=400):
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    r = subprocess.run(["claude", "-p", "--model", "claude-opus-4-8"], input=prompt,
                       capture_output=True, text=True, env=env, timeout=120)
    return _parse_score(r.stdout or "") if r.returncode == 0 else None

def corr(a, b):
    a, b = np.array(a, float), np.array(b, float)
    return 0.0 if a.std() == 0 or b.std() == 0 else float(np.corrcoef(a, b)[0, 1])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--globs", default="runs/gsm8k/*.judged.jsonl")
    ap.add_argument("--scores", default="runs/scores_gsm8k.jsonl")
    ap.add_argument("--name", default="GSM8K")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--judge", default="gpt", choices=["gpt", "opus"])
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--out", default="runs/perturb_quality_gsm8k_gpt.jsonl")
    args = ap.parse_args()

    cc = load_cc(args.scores)
    recs = []
    for f in glob.glob(args.globs):
        for line in open(f):
            r = json.loads(line)
            k = (r.get("model"), r.get("problem_id"))
            if k in cc and r.get("free_gen") and r.get("question"):
                r["cc"] = cc[k]; recs.append(r)
    pos = [r for r in recs if r["cc"] == 1.0]; neg = [r for r in recs if r["cc"] == 0.0]
    random.Random(0).shuffle(pos); random.Random(1).shuffle(neg)
    h = args.n // 2; sample = pos[:h] + neg[:h]; random.Random(2).shuffle(sample)
    print(f"{args.name}: {len(sample)} items ({sum(r['cc'] for r in sample):.0f} correct); judge={args.judge}", flush=True)

    J = gpt if args.judge == "gpt" else opus
    def conds(r):
        q, g, c = r["question"], r["gold_solution"], r["free_gen"]
        return {"orig": build_prompt(q, g, c), "verbose": build_prompt(q, g, verbose(c)),
                "reformat": build_prompt(q, g, reformat(c)),
                "binary": RUBRIC_BINARY.format(question=q, gold=g, candidate=c)}
    def do(r):
        out = {"cc": r["cc"], "problem_id": r["problem_id"], "model": r["model"]}
        for k, p in conds(r).items():
            out[k] = J(p, 200 if k == "binary" else 400)
        return out
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        rows = list(ex.map(do, sample))
    with open(args.out, "w") as fo:
        for row in rows: fo.write(json.dumps(row) + "\n")

    print(f"\n  {'condition':9s} {'corr(acc)':>9s} {'quality%':>9s} {'meanScore':>9s} {'dScore vs orig':>14s} {'n':>4s}")
    base = {row["problem_id"]: row.get("orig") for row in rows}
    for k in ("orig", "verbose", "reformat", "binary"):
        pr = [(row[k], row["cc"], row.get("orig")) for row in rows if row.get(k) is not None]
        c = corr([x[0] for x in pr], [x[1] for x in pr])
        ms = float(np.mean([x[0] for x in pr]))
        ds = [x[0] - x[2] for x in pr if x[2] is not None]
        dsm = float(np.mean(ds)) if ds else float("nan")
        print(f"  {k:9s} {c:+9.3f} {100*c*c:8.1f}% {ms:9.2f} {dsm:+14.2f} {len(pr):4d}")
    print(f"\nwrote {args.out}")

if __name__ == "__main__":
    main()
