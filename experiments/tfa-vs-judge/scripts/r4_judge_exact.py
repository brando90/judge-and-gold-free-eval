# R4-A / R4-B judge harness (papers/D-iclr/registration_round4.md). Prompts identical to bon_judge.py (rubric a),
# with an exact expected score for tokenizers that write "10" as two tokens: for every "1" score token t in the
# first-position top-20, one more forward step on prompt+t gives q = P("0" | prompt, t), and t contributes
# 10 with weight p_t*q and 1 with weight p_t*(1-q). Also stores the legacy bon_judge.py value and the greedy integer.
# Output rows: problem_id, escore (exact; None = missing), escore_legacy, greedy, mass, flag
#   flag 0 = expected score, 1 = captured mass < 0.25 so the greedy integer is used, 2 = no score (missing).
import argparse, json, math, os, re, sys

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--name", required=True, help="output tag for the pool: repl, replrot, kstrat, mace, math")
ap.add_argument("--judge", required=True)
ap.add_argument("--cond", choices=["noref", "ref", "refans"], required=True)
ap.add_argument("--domain", choices=["synthk", "mace", "math"], required=True)
ap.add_argument("--tasks", default=None)
ap.add_argument("--band", type=float, nargs=2, default=None)
ap.add_argument("--out", default="runs/r4/scores")
ap.add_argument("--gpu-util", type=float, default=0.5)
ap.add_argument("--max-model-len", type=int, default=4096)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
tag = args.judge.replace("/", "__")
out = f"{args.out}/{args.name}__{tag}__{args.cond}_a.jsonl"
if os.path.exists(out):
    print("[skip]", out); raise SystemExit
if args.cond == "refans" and args.domain != "math":
    raise SystemExit("refans is defined for MATH-500 only")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC, RUBRIC_TIES

pool = [json.loads(l) for l in open(args.pool)]
if args.tasks:
    tmap = {}
    for l in open(args.tasks):
        t = json.loads(l)
        tmap[t.get("problem_id") or t.get("task_id")] = t
    for r in pool:
        r.update({k: v for k, v in tmap.get(r["problem_id"], {}).items() if k not in r})
pool = [r for r in pool if "oracle" in r]
if args.domain == "mace":  # audited domains only (registration_round4.md), as in r3_mace_accuracy_analysis.py
    import ast
    pool = [r for r in pool if (r["params"] if isinstance(r["params"], dict) else ast.literal_eval(r["params"]))["domain"]
            in ("River", "Language")]
if args.band:
    lo, hi = args.band
    pool = [r for r in pool if lo <= sum(r["oracle"]) / len(r["oracle"]) <= hi]
print(f"[r4] {len(pool)} tasks x {len(pool[0]['samples'])} samples, {args.name}/{args.cond}", flush=True)

REFANS_SYS = RUBRIC[("ref", "a")].replace("a reference solution known to be correct", "a reference answer known to be correct")
assert REFANS_SYS != RUBRIC[("ref", "a")]

tok = AutoTokenizer.from_pretrained(args.judge)
CAND = {}
for v in range(11):
    for s_ in (str(v), " " + str(v)):
        ids = tok.encode(s_, add_special_tokens=False)
        if len(ids) == 1:
            CAND.setdefault(ids[0], v)
TEN_SINGLE = 10 in CAND.values()
ZERO = {i for i in range(len(tok)) if tok.decode([i]) == "0"} if not TEN_SINGLE else set()
print(f"[r4] ten_single={TEN_SINGLE} zero_tokens={sorted(ZERO)[:5]}", flush=True)


def build(r, s):
    if args.domain == "math":
        sysmsg = REFANS_SYS if args.cond == "refans" else RUBRIC[(args.cond, "a")]
    else:
        sysmsg = RUBRIC_TIES[(args.cond, "a")]
    q = r.get("problem") or r.get("question") or r.get("prompt")
    parts = [f"Problem:\n{q}"]
    if args.cond == "ref":
        if args.domain == "math":
            parts.append(f"Reference solution (trusted):\n{r['solution']}")
        else:
            parts.append(f"Reference answer (trusted):\n{r['ref_answer']}")
    if args.cond == "refans":
        parts.append(f"Reference answer (trusted):\n{r['answer']}")
    parts.append(f"Candidate solution:\n{s}\n\nScore:")
    try:
        return tok.apply_chat_template([{"role": "system", "content": sysmsg},
                                        {"role": "user", "content": "\n\n".join(parts)}],
                                       tokenize=False, add_generation_prompt=True)
    except Exception:
        return tok.apply_chat_template([{"role": "user", "content": sysmsg + "\n\n" + "\n\n".join(parts)}],
                                       tokenize=False, add_generation_prompt=True)


llm = LLM(model=args.judge, dtype="bfloat16", gpu_memory_utilization=args.gpu_util,
          max_model_len=args.max_model_len, seed=0)
sp1 = SamplingParams(max_tokens=4, temperature=0.0, logprobs=20)
sp2 = SamplingParams(max_tokens=1, temperature=0.0, logprobs=20)
n_flag = [0, 0, 0]
with open(out + ".part", "w") as f:
    B = 25
    for i in range(0, len(pool), B):
        chunk = pool[i:i + B]
        prompts, spans = [], []
        for r in chunk:
            spans.append((len(prompts), len(prompts) + len(r["samples"])))
            prompts += [build(r, s) for s in r["samples"]]
        outs = llm.generate(prompts, sp1, use_tqdm=False)
        q0 = {}
        if not TEN_SINGLE:
            keys, tprompts = [], []
            for n, o in enumerate(outs):
                lp = o.outputs[0].logprobs[0] if o.outputs[0].logprobs else {}
                for tid in lp:
                    if CAND.get(tid) == 1:
                        keys.append((n, tid))
                        tprompts.append({"prompt_token_ids": list(o.prompt_token_ids) + [tid]})
            if tprompts:
                for key, o2 in zip(keys, llm.generate(tprompts, sp2, use_tqdm=False)):
                    lp2 = o2.outputs[0].logprobs[0] if o2.outputs[0].logprobs else {}
                    q0[key] = sum(math.exp(lp2[z].logprob) for z in ZERO if z in lp2)
        for r, (a, b) in zip(chunk, spans):
            ex, leg, gr, mass, flag = [], [], [], [], []
            for n in range(a, b):
                o = outs[n]
                lp = o.outputs[0].logprobs[0] if o.outputs[0].logprobs else {}
                text = o.outputs[0].text or ""
                txt = text.strip()
                one_means = 10 if txt.startswith("10") else 1
                num = numL = den = 0.0
                for tid, info in lp.items():
                    if tid not in CAND:
                        continue
                    p = math.exp(info.logprob)
                    v = CAND[tid]
                    den += p
                    if v == 1 and not TEN_SINGLE:
                        q = q0.get((n, tid), 0.0)
                        num += p * (10 * q + 1 * (1 - q))
                    else:
                        num += p * v
                    numL += p * (one_means if v == 1 else v)
                g = re.match(r"\s*(10|\d)", text)
                gr.append(int(g.group(1)) if g else None)
                mass.append(round(den, 4))
                if den >= 0.25:
                    ex.append(num / den); leg.append(numL / den); flag.append(0)
                else:
                    m = re.search(r"\d+", text)
                    if m:
                        ex.append(float(min(int(m.group()), 10))); leg.append(float(min(int(m.group()), 10))); flag.append(1)
                    else:
                        ex.append(None); leg.append(5.0); flag.append(2)
                n_flag[flag[-1]] += 1
            f.write(json.dumps(dict(problem_id=r["problem_id"], escore=ex, escore_legacy=leg, greedy=gr,
                                    mass=mass, flag=flag)) + "\n")
        f.flush()
        print(f"[r4] {min(i + B, len(pool))}/{len(pool)} flags={n_flag}", flush=True)
os.replace(out + ".part", out)
print(f"[r4 done] {out} flags={n_flag}", flush=True)
import psutil
for _c in psutil.Process().children(recursive=True):
    try:
        _c.kill()
    except Exception:
        pass
os._exit(0)
