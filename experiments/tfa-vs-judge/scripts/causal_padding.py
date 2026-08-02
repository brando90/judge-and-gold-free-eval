#!/usr/bin/env python
# Causal test of the certificate's length-bias flag: intervene on length while holding the (correct)
# answer fixed, re-judge, and see whether the score moves. ORIG = the model's own correct answer;
# PAD = same answer with a redundant correct restatement appended (more length, no new information);
# COMPRESS = a terse correct statement of the answer. All three are re-judged FRESH with the same judge
# call, so the paired deltas d_pad = pad-orig and d_comp = compress-orig are internally valid.
# Opus runs locally via `claude -p` (session login); GPT-5.2 needs OPENAI_API_KEY (cluster/key).
import argparse, glob, json, re, random, statistics
from concurrent.futures import ThreadPoolExecutor
from tfa.judge import build_prompt
from run_judge_cli import judge_via_cli
from judge_nuisance import load_cc

def gold_answer(gold):
    m = re.search(r"####\s*([^\n]+)", gold or "")
    if m: return m.group(1).strip()
    nums = re.findall(r"-?\d[\d,]*\.?\d*", gold or "")
    return nums[-1] if nums else "the value above"

def pad(text):
    return (text or "") + "\n\nTo be thorough, here is the same solution restated step by step:\n" + (text or "")

def compress(gold):
    return f"The final answer is {gold_answer(gold)}."

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--globs", default="runs/gsm8k/*.judged.opus.jsonl")
    ap.add_argument("--scores", default="runs/scores_gsm8k.jsonl")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--max_score", type=float, default=9.0, help="keep correct items with old score <= this (headroom)")
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--out", default="runs/causal_padding_gsm8k_opus.jsonl")
    args = ap.parse_args()

    cc = load_cc(args.scores)
    pool = []
    for f in glob.glob(args.globs):
        for line in open(f):
            r = json.loads(line)
            key = (r.get("model"), r.get("problem_id"))
            old = r.get("judge_score")
            # correct answers with HEADROOM (not already at the ceiling), so padding can move the score
            if cc.get(key) == 1.0 and r.get("free_gen") and old is not None and float(old) <= args.max_score:
                pool.append(r)
    random.Random(0).shuffle(pool)
    pool = pool[:args.n]
    print(f"selected {len(pool)} correct, non-ceiling (old score <= {args.max_score}) items; "
          f"3 fresh conditions x {len(pool)} = {3*len(pool)} calls via {args.model}")

    jobs = []
    for r in pool:
        q, g = r["question"], r["gold_solution"]
        # orig2 = fresh re-judge of the SAME unpadded text (controls RTM + judge noise); pad and orig2
        # are both fresh, so pad - orig2 is the clean padding effect. compress is secondary (confounded).
        jobs.append((r["problem_id"], r["model"], "orig2", build_prompt(q, g, r["free_gen"])))
        jobs.append((r["problem_id"], r["model"], "pad", build_prompt(q, g, pad(r["free_gen"]))))
        jobs.append((r["problem_id"], r["model"], "compress", build_prompt(q, g, compress(g))))

    old_orig = {(r["problem_id"], r["model"]): float(r["judge_score"]) for r in pool}

    def run(j):
        pid, mdl, cond, prompt = j
        return (pid, mdl, cond, judge_via_cli(prompt, args.model, args.timeout))
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        res = list(ex.map(run, jobs))

    by = {}
    for pid, mdl, cond, s in res:
        by.setdefault((pid, mdl), {})[cond] = s
    rows = [dict(problem_id=p, model=m, old_orig=old_orig.get((p, m)), **c) for (p, m), c in by.items()]
    with open(args.out, "w") as fo:
        for row in rows: fo.write(json.dumps(row) + "\n")

    def deltas(k, base):
        return [row[k] - row[base] for row in rows
                if row.get(k) is not None and row.get(base) is not None]
    dp = deltas("pad", "orig2")          # primary: padding effect, both fresh
    dc = deltas("compress", "orig2")     # secondary: terse (confounded by less reasoning shown)
    rtm = deltas("orig2", "old_orig")    # sanity: fresh re-judge vs old score (RTM / noise / drift)
    def summ(d):
        if not d: return "n/a"
        m = statistics.mean(d); sd = statistics.pstdev(d) if len(d) > 1 else 0
        se = sd / (len(d) ** 0.5) if d else 0
        pos = sum(x > 0 for x in d) / len(d)
        return f"mean {m:+.2f} (95% ~[{m-1.96*se:+.2f},{m+1.96*se:+.2f}]), {100*pos:.0f}% positive, n={len(d)}"
    print(f"\n{args.model} on GSM8K (correct, non-ceiling answers):")
    print(f"  padding effect  pad - orig2 (both fresh, longer w/ no new info): {summ(dp)}")
    print(f"  terse effect    compress - orig2 (confounded by less reasoning): {summ(dc)}")
    print(f"  sanity          orig2 - old_orig (re-judge drift / RTM):         {summ(rtm)}")
    complete = sum(all(row.get(k) is not None for k in ('orig2','pad','compress')) for row in rows)
    print(f"  complete triples: {complete}/{len(rows)};  wrote {args.out}")

if __name__ == "__main__":
    main()
