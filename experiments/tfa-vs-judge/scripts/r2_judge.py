# R2-B judge harness (papers/D-iclr/registration_round2.md).
#   --protocol reason  : Qwen3-8B, thinking on, paper rubric a with a "Score: N" final line
#   --protocol mtbench : verbatim FastChat MT-Bench single-math-v1 (reference) / single-v1 (blind)
# Output rows: {problem_id, idx, score (float or null), n_tokens, tail (last 400 chars)}.
import argparse, json, os, re, sys
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--protocol", choices=["reason", "mtbench"], required=True)
ap.add_argument("--pool", choices=["rot", "ksub"], required=True)
ap.add_argument("--cond", choices=["noref", "ref", "refrot"], required=True)
ap.add_argument("--judge", required=True)
ap.add_argument("--out", default="runs/r2/scores")
ap.add_argument("--gpu-util", type=float, default=0.45)
ap.add_argument("--max-model-len", type=int, default=8192)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
tag = args.judge.replace("/", "__")
out = f"{args.out}/{args.pool}__{args.protocol}__{tag}__{args.cond}.jsonl"
if os.path.exists(out):
    print("[skip]", out); raise SystemExit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC_TIES

pool = [json.loads(l) for l in open(f"runs/r2/{'rot_sub' if args.pool == 'rot' else 'ksub'}.jsonl")]
tok = AutoTokenizer.from_pretrained(args.judge)

REASON_TAIL = ("Think it through, then end your reply with a final line of the form 'Score: N', "
               "where N is an integer from 0 to 10.")
MT_SYS = "You are a helpful assistant."
MT_REF = ("[Instruction]\nPlease act as an impartial judge and evaluate the quality of the response provided by an AI "
          "assistant to the user question displayed below. Your evaluation should consider correctness and helpfulness. "
          "You will be given a reference answer and the assistant's answer. Begin your evaluation by comparing the "
          "assistant's answer with the reference answer. Identify and correct any mistakes. Be as objective as possible. "
          "After providing your explanation, you must rate the response on a scale of 1 to 10 by strictly following "
          "this format: \"[[rating]]\", for example: \"Rating: [[5]]\".\n\n[Question]\n{question}\n\n"
          "[The Start of Reference Answer]\n{ref_answer_1}\n[The End of Reference Answer]\n\n"
          "[The Start of Assistant's Answer]\n{answer}\n[The End of Assistant's Answer]")
MT_BLIND = ("[Instruction]\nPlease act as an impartial judge and evaluate the quality of the response provided by an AI "
            "assistant to the user question displayed below. Your evaluation should consider factors such as the "
            "helpfulness, relevance, accuracy, depth, creativity, and level of detail of the response. Begin your "
            "evaluation by providing a short explanation. Be as objective as possible. After providing your explanation, "
            "you must rate the response on a scale of 1 to 10 by strictly following this format: \"[[rating]]\", for "
            "example: \"Rating: [[5]]\".\n\n[Question]\n{question}\n\n[The Start of Assistant's Answer]\n{answer}\n"
            "[The End of Assistant's Answer]")


def strip_last_sentence(rubric):
    # paper rubrics end with "Respond with only the integer score." (a)
    return re.sub(r"\s*Respond with only the integer score\.\s*$", "", rubric)


def ref_of(r):
    return r["ref_rot"] if args.cond == "refrot" else r["ref_orig"]


def build(r, s):
    if args.protocol == "reason":
        key = "noref" if args.cond == "noref" else "ref"
        sysmsg = strip_last_sentence(RUBRIC_TIES[(key, "a")]) + " " + REASON_TAIL
        parts = [f"Problem:\n{r['question']}"]
        if args.cond != "noref":
            parts.append(f"Reference answer (trusted):\n{ref_of(r)}")
        parts.append(f"Candidate solution:\n{s}")
        msgs = [{"role": "system", "content": sysmsg}, {"role": "user", "content": "\n\n".join(parts)}]
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=True)
    if args.cond == "noref":
        user = MT_BLIND.format(question=r["question"], answer=s)
    else:
        user = MT_REF.format(question=r["question"], ref_answer_1=ref_of(r), answer=s)
    return tok.apply_chat_template([{"role": "system", "content": MT_SYS}, {"role": "user", "content": user}],
                                   tokenize=False, add_generation_prompt=True)


def parse(text):
    if args.protocol == "reason":
        body = text.split("</think>")[-1]
        m = re.findall(r"Score:\s*\**\s*(\d+(?:\.\d+)?)", body)
        if not m:
            return None
        v = float(m[-1])
        return v if 0 <= v <= 10 else None
    m = re.findall(r"\[\[(\d+(?:\.\d+)?)\]\]", text)
    if not m:
        return None
    v = float(m[-1])
    return v if 1 <= v <= 10 else None


if args.protocol == "reason":
    sp = SamplingParams(max_tokens=4096, temperature=0.6, top_p=0.95, top_k=20, seed=0)
else:
    sp = SamplingParams(max_tokens=1024, temperature=0.0)
llm = LLM(model=args.judge, dtype="bfloat16", gpu_memory_utilization=args.gpu_util,
          max_model_len=args.max_model_len, seed=0)

prompts, meta = [], []
for r in pool:
    for j, s in enumerate(r["samples"]):
        prompts.append(build(r, s)); meta.append((r["problem_id"], r["idx"][j]))
print(f"[{args.protocol}/{args.pool}/{args.cond}] {len(prompts)} prompts", flush=True)

rows = {}
B = 512
n_bad = 0
for i in range(0, len(prompts), B):
    outs = llm.generate(prompts[i:i + B], sp)
    for (pid, idx), o in zip(meta[i:i + B], outs):
        text = o.outputs[0].text or ""
        v = parse(text)
        n_bad += v is None
        rows.setdefault(pid, []).append(dict(idx=idx, score=v, n_tokens=len(o.outputs[0].token_ids), tail=text[-400:]))
    print(f"  {min(i + B, len(prompts))}/{len(prompts)} unparseable so far {n_bad}", flush=True)

with open(out + ".part", "w") as f:
    for pid, lst in rows.items():
        f.write(json.dumps(dict(problem_id=pid, idx=[x["idx"] for x in lst], score=[x["score"] for x in lst],
                                n_tokens=[x["n_tokens"] for x in lst], tail=[x["tail"] for x in lst])) + "\n")
os.replace(out + ".part", out)
print(f"[r2 done] {out} unparseable={n_bad}/{len(prompts)}", flush=True)
import psutil
for _c in psutil.Process().children(recursive=True):
    try:
        _c.kill()
    except Exception:
        pass
os._exit(0)
