# Structural mitigation protocols for OSF qugbd (registered before data).
# M1 blind-then-reveal: call 1 scores blind; call 2 shows the judge its own blind score and the
#   reference, instructing that a correct answer differing from the reference keeps its score;
#   the reported score is call 2's.
# M2 equivalence-gated: call 1 scores blind; call 2 answers only whether the candidate's final
#   answer is valid for the question (reference shown as one valid example); final score is the
#   blind score if judged valid, else zero.
# Output: runs/bon_scores_kstrat/{domain}__{judge}__{cond}_{rep}.jsonl rows {problem_id, escore}
import argparse, json, math, os, re, sys
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--judge", required=True)
ap.add_argument("--cond", choices=["m1", "m2"], required=True)
ap.add_argument("--rep", choices=["a", "b"], required=True)
ap.add_argument("--out", default="runs/bon_scores_kstrat")
ap.add_argument("--max-model-len", type=int, default=4096)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
tag = args.judge.replace("/", "__")
out = f"{args.out}/kstrat__{tag}__{args.cond}_{args.rep}.jsonl"
if os.path.exists(out):
    print("[skip]", out); raise SystemExit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC_TIES

pool = [json.loads(l) for l in open(args.pool)]
tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/kstrat_tasks.jsonl")}
for r in pool:
    t = tasks[r["problem_id"]]
    r["question"] = t["problem"]; r["ref_answer"] = t["ref_answer"]

tok = AutoTokenizer.from_pretrained(args.judge)
CAND = {}
for v in range(11):
    for s in (str(v), " " + str(v)):
        ids = tok.encode(s, add_special_tokens=False)
        if len(ids) == 1:
            CAND.setdefault(ids[0], v)
YES = [i for s in ("Yes", " Yes", "YES", "yes", " yes") for i in [tok.encode(s, add_special_tokens=False)] if len(i) == 1]
YES = {i[0] for i in YES}
NO = [i for s in ("No", " No", "NO", "no", " no") for i in [tok.encode(s, add_special_tokens=False)] if len(i) == 1]
NO = {i[0] for i in NO}

def chat(sysmsg, user):
    return tok.apply_chat_template([{"role": "system", "content": sysmsg},
                                    {"role": "user", "content": user}],
                                   tokenize=False, add_generation_prompt=True)

def blind_prompt(r, s):
    return chat(RUBRIC_TIES[("noref", args.rep)],
                f"Problem:\n{r['question']}\n\nCandidate solution:\n{s}\n\nScore:")

def m1_prompt(r, s, blind_score):
    sysmsg = RUBRIC_TIES[("ref", args.rep)] + (
        " You have already assessed this candidate without seeing any reference. "
        "A correct answer that differs from the reference must keep the score you gave it; "
        "revise only if the reference reveals the candidate is actually wrong.")
    return chat(sysmsg,
                f"Problem:\n{r['question']}\n\nReference answer (one valid answer, trusted):\n"
                f"{r['ref_answer']}\n\nCandidate solution:\n{s}\n\n"
                f"Your blind score for this candidate was {blind_score:.1f} out of 10.\n\nScore:")

def m2_prompt(r, s):
    sysmsg = ("You check answer validity. The question may have several valid answers. "
              "Answer with exactly one word: Yes if the candidate's final answer is a valid "
              "answer to the question, No otherwise. The reference is one valid example, not "
              "the only one.")
    return chat(sysmsg,
                f"Problem:\n{r['question']}\n\nReference (one valid answer):\n{r['ref_answer']}\n\n"
                f"Candidate solution:\n{s}\n\nIs the candidate's final answer valid?")

llm = LLM(model=args.judge, dtype="bfloat16", gpu_memory_utilization=0.9,
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

def yes_prob(o):
    lp = o.outputs[0].logprobs[0] if o.outputs[0].logprobs else {}
    py = sum(math.exp(i.logprob) for t, i in lp.items() if t in YES)
    pn = sum(math.exp(i.logprob) for t, i in lp.items() if t in NO)
    if py + pn < 0.05:
        return 1.0 if "yes" in (o.outputs[0].text or "").lower() else 0.0
    return py / (py + pn)

with open(out, "w") as f:
    B = 20
    for i in range(0, len(pool), B):
        chunk = pool[i:i + B]
        prompts, spans = [], []
        for r in chunk:
            spans.append((len(prompts), len(prompts) + len(r["samples"])))
            prompts += [blind_prompt(r, s) for s in r["samples"]]
        blind_out = llm.generate(prompts, sp)
        blind = {}
        for r, (a, b) in zip(chunk, spans):
            blind[r["problem_id"]] = [escore_of(o) for o in blind_out[a:b]]
        prompts2 = []
        for r, (a, b) in zip(chunk, spans):
            bs = blind[r["problem_id"]]
            if args.cond == "m1":
                prompts2 += [m1_prompt(r, s, bs[j]) for j, s in enumerate(r["samples"])]
            else:
                prompts2 += [m2_prompt(r, s) for s in r["samples"]]
        out2 = llm.generate(prompts2, sp)
        for r, (a, b) in zip(chunk, spans):
            bs = blind[r["problem_id"]]
            if args.cond == "m1":
                esc = [escore_of(o) for o in out2[a:b]]
            else:
                esc = [bs[j] * yes_prob(o) for j, o in enumerate(out2[a:b])]
            f.write(json.dumps(dict(problem_id=r["problem_id"], escore=esc)) + "\n")
        f.flush()
        print(f"[{args.cond}] {min(i + B, len(pool))}/{len(pool)}", flush=True)
print("[mitigation done]", out, flush=True)
