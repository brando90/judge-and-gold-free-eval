# R2-A (papers/D-iclr/registration_round2.md): blind-then-reveal on unique-answer MATH-500.
# Call 1 repeats the frozen blind math prompt; call 2 shows the trusted reference solution and the
# call-1 blind score. Output rows: {problem_id, escore (call 2), blind (call 1)}.
import argparse, json, math, os, re, sys
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--judge", required=True)
ap.add_argument("--rep", choices=["a", "b"], required=True)
ap.add_argument("--pool", default="runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")
ap.add_argument("--out", default="runs/r2/scores")
ap.add_argument("--max-model-len", type=int, default=16384)
ap.add_argument("--gpu-util", type=float, default=0.45)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
tag = args.judge.replace("/", "__")
out = f"{args.out}/math__{tag}__m1_{args.rep}.jsonl"
if os.path.exists(out):
    print("[skip]", out); raise SystemExit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC

tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/bon_math_tasks.jsonl")}
pool = []
for l in open(args.pool):
    r = json.loads(l)
    pr = sum(r["oracle"]) / len(r["oracle"])
    if 0.2 <= pr <= 0.8:
        t = tasks[r["problem_id"]]
        r["question"], r["solution"] = t["problem"], t["solution"]
        pool.append(r)
print("[pool] in-band problems:", len(pool), flush=True)

tok = AutoTokenizer.from_pretrained(args.judge)
CAND = {}
for v in range(11):
    for s in (str(v), " " + str(v)):
        ids = tok.encode(s, add_special_tokens=False)
        if len(ids) == 1:
            CAND.setdefault(ids[0], v)


def chat(sysmsg, user):
    return tok.apply_chat_template([{"role": "system", "content": sysmsg},
                                    {"role": "user", "content": user}],
                                   tokenize=False, add_generation_prompt=True)


def blind_prompt(r, s):
    # identical to bon_judge.py's math noref prompt
    return chat(RUBRIC[("noref", args.rep)], f"Problem:\n{r['question']}\n\nCandidate solution:\n{s}\n\nScore:")


def m1_prompt(r, s, b):
    sysmsg = RUBRIC[("ref", args.rep)] + (
        " You have already assessed this candidate without seeing any reference. "
        "A correct solution that differs from the reference in method or presentation must keep "
        "the score you gave it; revise only if the reference reveals the candidate is actually wrong.")
    return chat(sysmsg, f"Problem:\n{r['question']}\n\nReference solution (trusted):\n{r['solution']}\n\n"
                        f"Candidate solution:\n{s}\n\nYour blind score for this candidate was {b:.1f} out of 10.\n\nScore:")


llm = LLM(model=args.judge, dtype="bfloat16", gpu_memory_utilization=args.gpu_util,
          max_model_len=args.max_model_len)
sp = SamplingParams(max_tokens=4, temperature=0.0, logprobs=20)


def escore_of(o):
    lp = o.outputs[0].logprobs[0] if o.outputs[0].logprobs else {}
    txt = (o.outputs[0].text or "").strip()
    one_means = 10 if txt.startswith("10") else 1
    num = den = 0.0
    for tid, info in lp.items():
        if tid in CAND:
            v = one_means if CAND[tid] == 1 else CAND[tid]
            p = math.exp(info.logprob); num += p * v; den += p
    if den >= 0.25:
        return num / den
    m = re.search(r"\d+", o.outputs[0].text or "")
    return min(int(m.group()), 10) if m else 5.0


with open(out + ".part", "w") as f:
    B = 10
    for i in range(0, len(pool), B):
        chunk = pool[i:i + B]
        prompts, spans = [], []
        for r in chunk:
            spans.append((len(prompts), len(prompts) + len(r["samples"])))
            prompts += [blind_prompt(r, s) for s in r["samples"]]
        o1 = llm.generate(prompts, sp)
        blind = {r["problem_id"]: [escore_of(o) for o in o1[a:b]] for r, (a, b) in zip(chunk, spans)}
        prompts2 = []
        for r in chunk:
            prompts2 += [m1_prompt(r, s, blind[r["problem_id"]][j]) for j, s in enumerate(r["samples"])]
        o2 = llm.generate(prompts2, sp)
        for r, (a, b) in zip(chunk, spans):
            f.write(json.dumps(dict(problem_id=r["problem_id"], escore=[escore_of(o) for o in o2[a:b]],
                                    blind=blind[r["problem_id"]])) + "\n")
        f.flush()
        print(f"[m1-math {args.judge} {args.rep}] {min(i + B, len(pool))}/{len(pool)}", flush=True)
os.replace(out + ".part", out)
print("[r2 done]", out, flush=True)
os._exit(0)  # vLLM 0.25.1 can hang on teardown
