#!/usr/bin/env python
# Does an improved judge prompt raise the quality signal (= corr(judge, accuracy)^2) on GSM8K/Putnam?
# We re-judge the SAME sampled items (stratified over correct/incorrect, so accuracy has variance) with
# the ORIGINAL rubric and an IMPROVED "solve-first" rubric, both fresh, and compare corr(score, cc).
# Default judge is GPT-5.2 (litellm); pass --judge opus for the claude CLI path.
import argparse, glob, json, re, random, os, subprocess
from concurrent.futures import ThreadPoolExecutor
from tfa.judge import build_prompt, _parse_score
from judge_nuisance import load_cc

RUBRIC_IMPROVED = """You are an expert mathematics grader. FIRST solve the problem yourself step by step and
determine the correct final answer. THEN grade the candidate solution's REASONING QUALITY from 0 to 10,
using your own solution and the gold reference:
- judge whether the candidate's final answer is correct, AND whether each step is valid and justified;
- a correct final answer reached by invalid or hand-wavy reasoning must score low;
- do NOT reward length, verbosity, or formatting.

Problem:
{question}

Gold reference solution:
{gold}

Candidate solution:
{candidate}

Reason briefly, then output the JSON verdict as the FINAL line: {{"score": <float 0-10>}}."""

RUBRIC_BINARY = """Determine whether the candidate solution's FINAL ANSWER is correct, using the gold reference.
Problem:
{question}

Gold reference solution:
{gold}

Candidate solution:
{candidate}

Return STRICT JSON only: {{"score": 10}} if the final answer is correct, else {{"score": 0}}."""

def parse_last_score(text):
    if not text: return None
    ms = re.findall(r'\{[^{}]*?"score"[^{}]*?\}', text)
    for m in reversed(ms):
        try: return float(json.loads(m)["score"])
        except Exception: pass
    ms = re.findall(r'score\D{0,5}([0-9]+(?:\.[0-9]+)?)', text, re.IGNORECASE)
    return float(ms[-1]) if ms else None

def gpt(prompt, parse, max_tokens):
    import litellm; litellm.drop_params = True
    try:
        r = litellm.completion(model="openai/gpt-5.2", messages=[{"role": "user", "content": prompt}],
                               temperature=0.0, seed=0, max_tokens=max_tokens)
        return parse(r.choices[0].message.content or "")
    except Exception:
        return None

def opus(prompt, parse, timeout=120):
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    r = subprocess.run(["claude", "-p", "--model", "claude-opus-4-8"], input=prompt,
                       capture_output=True, text=True, env=env, timeout=timeout)
    return parse(r.stdout or "") if r.returncode == 0 else None

def corr(a, b):
    import numpy as np
    a, b = np.array(a, float), np.array(b, float)
    return 0.0 if a.std() == 0 or b.std() == 0 else float(np.corrcoef(a, b)[0, 1])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--globs", default="runs/gsm8k/*.judged.jsonl")
    ap.add_argument("--scores", default="runs/scores_gsm8k.jsonl")
    ap.add_argument("--name", default="GSM8K")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--judge", default="gpt", choices=["gpt", "opus"])
    ap.add_argument("--rubric", default="solvefirst", choices=["solvefirst", "binary"])
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--out", default="runs/improved_prompt_gsm8k_gpt.jsonl")
    args = ap.parse_args()

    cc = load_cc(args.scores)
    recs = []
    for f in glob.glob(args.globs):
        for line in open(f):
            r = json.loads(line)
            k = (r.get("model"), r.get("problem_id"))
            if k in cc and r.get("free_gen") and r.get("question"):
                r["cc"] = cc[k]; recs.append(r)
    # stratify: balance correct / incorrect so accuracy has variance
    pos = [r for r in recs if r["cc"] == 1.0]; neg = [r for r in recs if r["cc"] == 0.0]
    random.Random(0).shuffle(pos); random.Random(1).shuffle(neg)
    half = args.n // 2
    sample = pos[:half] + neg[:half]; random.Random(2).shuffle(sample)
    print(f"{args.name}: {len(sample)} items ({sum(r['cc'] for r in sample):.0f} correct); judge={args.judge}", flush=True)

    J = gpt if args.judge == "gpt" else opus
    RUB = RUBRIC_IMPROVED if args.rubric == "solvefirst" else RUBRIC_BINARY
    mt = 800 if args.rubric == "solvefirst" else 200
    def do(r):
        q, g, c = r["question"], r["gold_solution"], r["free_gen"]
        orig = J(build_prompt(q, g, c), _parse_score, 400)
        impr = J(RUB.format(question=q, gold=g, candidate=c), parse_last_score, mt)
        return dict(problem_id=r["problem_id"], model=r["model"], cc=r["cc"], orig=orig, improved=impr)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        rows = list(ex.map(do, sample))
    with open(args.out, "w") as fo:
        for row in rows: fo.write(json.dumps(row) + "\n")

    for key in ("orig", "improved"):
        pairs = [(row[key], row["cc"]) for row in rows if row.get(key) is not None]
        c = corr([p[0] for p in pairs], [p[1] for p in pairs])
        print(f"  {key:9s}: corr(score,accuracy)={c:+.3f}  quality signal (corr^2)={100*c*c:4.1f}%  n={len(pairs)}")
    print(f"wrote {args.out}")

if __name__ == "__main__":
    main()
