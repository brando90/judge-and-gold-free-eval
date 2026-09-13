# R3-D (papers/D-iclr/registration_round3.md): blind-then-reveal (m1) and the soft validity gate (m2) on the
# MACE River+Language pool, with prompts copied verbatim from mitigation_judge.py (which is hard-wired to the
# k-pool task file). Output: runs/r3/scores/mace__{judge}__{cond}_a.jsonl rows {problem_id, escore, blind}.
import argparse, ast, json, math, os, re, sys
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--judge", required=True)
ap.add_argument("--cond", choices=["m1", "m2"], required=True)
ap.add_argument("--out", default="runs/r3/scores")
ap.add_argument("--gpu-util", type=float, default=0.45)
ap.add_argument("--max-model-len", type=int, default=4096)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
tag = args.judge.replace("/", "__")
out = f"{args.out}/mace__{tag}__{args.cond}_a.jsonl"
if os.path.exists(out):
    print("[skip]", out); raise SystemExit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC_TIES

tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/mace_tasks.jsonl")}
pool = []
for l in open("runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" not in r:
        continue
    t = tasks[r["problem_id"]]
    params = t["params"] if isinstance(t["params"], dict) else ast.literal_eval(t["params"])
    if params["domain"] in ("River", "Language"):
        r["question"], r["ref_answer"] = t["question"], t["ref_answer"]
        pool.append(r)
print("[pool] River+Language tasks:", len(pool), flush=True)

tok = AutoTokenizer.from_pretrained(args.judge)
CAND = {}
for v in range(11):
    for s in (str(v), " " + str(v)):
        ids = tok.encode(s, add_special_tokens=False)
        if len(ids) == 1:
            CAND.setdefault(ids[0], v)
YES = {i[0] for s in ("Yes", " Yes", "YES", "yes", " yes") for i in [tok.encode(s, add_special_tokens=False)] if len(i) == 1}
NO = {i[0] for s in ("No", " No", "NO", "no", " no") for i in [tok.encode(s, add_special_tokens=False)] if len(i) == 1}


def chat(sysmsg, user):
    try:
        return tok.apply_chat_template([{"role": "system", "content": sysmsg}, {"role": "user", "content": user}],
                                       tokenize=False, add_generation_prompt=True)
    except Exception:
        return tok.apply_chat_template([{"role": "user", "content": sysmsg + "\n\n" + user}],
                                       tokenize=False, add_generation_prompt=True)


def blind_prompt(r, s):
    return chat(RUBRIC_TIES[("noref", "a")], f"Problem:\n{r['question']}\n\nCandidate solution:\n{s}\n\nScore:")


def m1_prompt(r, s, b):
    sysmsg = RUBRIC_TIES[("ref", "a")] + (
        " You have already assessed this candidate without seeing any reference. "
        "A correct answer that differs from the reference must keep the score you gave it; "
        "revise only if the reference reveals the candidate is actually wrong.")
    return chat(sysmsg, f"Problem:\n{r['question']}\n\nReference answer (one valid answer, trusted):\n"
                        f"{r['ref_answer']}\n\nCandidate solution:\n{s}\n\n"
                        f"Your blind score for this candidate was {b:.1f} out of 10.\n\nScore:")


def m2_prompt(r, s):
    sysmsg = ("You check answer validity. The question may have several valid answers. "
              "Answer with exactly one word: Yes if the candidate's final answer is a valid "
              "answer to the question, No otherwise. The reference is one valid example, not "
              "the only one.")
    return chat(sysmsg, f"Problem:\n{r['question']}\n\nReference (one valid answer):\n{r['ref_answer']}\n\n"
                        f"Candidate solution:\n{s}\n\nIs the candidate's final answer valid?")


llm = LLM(model=args.judge, dtype="bfloat16", gpu_memory_utilization=args.gpu_util, max_model_len=args.max_model_len)
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


def yes_prob(o):
    lp = o.outputs[0].logprobs[0] if o.outputs[0].logprobs else {}
    py = sum(math.exp(i.logprob) for t, i in lp.items() if t in YES)
    pn = sum(math.exp(i.logprob) for t, i in lp.items() if t in NO)
    if py + pn < 0.05:
        return 1.0 if "yes" in (o.outputs[0].text or "").lower() else 0.0
    return py / (py + pn)


with open(out + ".part", "w") as f:
    B = 25
    for i in range(0, len(pool), B):
        chunk = pool[i:i + B]
        prompts, spans = [], []
        for r in chunk:
            spans.append((len(prompts), len(prompts) + len(r["samples"])))
            prompts += [blind_prompt(r, s) for s in r["samples"]]
        o1 = llm.generate(prompts, sp)
        blind = {r["problem_id"]: [escore_of(o) for o in o1[a:b]] for r, (a, b) in zip(chunk, spans)}
        p2 = []
        for r in chunk:
            if args.cond == "m1":
                p2 += [m1_prompt(r, s, blind[r["problem_id"]][j]) for j, s in enumerate(r["samples"])]
            else:
                p2 += [m2_prompt(r, s) for s in r["samples"]]
        o2 = llm.generate(p2, sp)
        for r, (a, b) in zip(chunk, spans):
            bs = blind[r["problem_id"]]
            esc = [escore_of(o) for o in o2[a:b]] if args.cond == "m1" else [bs[j] * yes_prob(o) for j, o in enumerate(o2[a:b])]
            f.write(json.dumps(dict(problem_id=r["problem_id"], escore=esc, blind=bs)) + "\n")
        f.flush()
        print(f"[mace {args.cond} {args.judge}] {min(i + B, len(pool))}/{len(pool)}", flush=True)
os.replace(out + ".part", out)
print("[r3 done]", out, flush=True)
import psutil
for _c in psutil.Process().children(recursive=True):
    try:
        _c.kill()
    except Exception:
        pass
os._exit(0)
