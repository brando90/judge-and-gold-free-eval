# Answer-swap counterfactual support metric (registered prediction: WORKS — it verifies rather
# than compares; docs/async-update-brando-aug17.md written before this ran).
# support = per-token lp of the trace's own final boxed answer minus per-token lp of a swapped
# alternative answer in the same slot, under a fixed scorer model. Judge-free; measures whether
# the reasoning prefix actually pins down the answer it asserts.
# Run ON skampere1: CUDA_VISIBLE_DEVICES=7 .venv/bin/python answer_swap.py
import glob, json, os, re

from vllm import LLM, SamplingParams
from vllm.inputs import TokensPrompt
from transformers import AutoTokenizer

SCORER = "Qwen/Qwen2.5-7B-Instruct"
GOLD = {json.loads(l)["problem_id"]: json.loads(l)["answer"] for l in open("m500_full.jsonl")}
OUT = "runs/answer_swap.jsonl"
MML = 4096


def text_of(r):
    for k in ("free_gen", "generation", "output", "gen", "text", "response", "completion"):
        if isinstance(r.get(k), str) and r[k]:
            return r[k]
    return None


def distractor(ans, pid, gold):
    if ans.strip() != gold.get(pid, "").strip() and gold.get(pid):
        return gold[pid]                       # wrong answer -> swap in the gold
    m = re.fullmatch(r"-?\d+(\.\d+)?", ans.strip())
    if m:                                       # correct numeric -> off-by-one
        v = float(ans);  return str(int(v) + 1) if v == int(v) else str(v + 1)
    return ans + " + 1"                         # correct symbolic -> corrupted form


tok = AutoTokenizer.from_pretrained(SCORER)
llm = LLM(model=SCORER, dtype="bfloat16", gpu_memory_utilization=0.9, max_model_len=MML)
sp = SamplingParams(max_tokens=1, prompt_logprobs=1)

done = set()
if os.path.exists(OUT):
    done = {(json.loads(l)["model"], json.loads(l)["problem_id"]) for l in open(OUT)}

FILES = sorted(glob.glob("runs/all/math500__*.jsonl")) + \
        sorted(g for g in glob.glob("runs/math500/math500__*.jsonl") if ".opus." not in g)
f = open(OUT, "a")
for fn in FILES:
    rows = [json.loads(l) for l in open(fn)]
    prompts, meta = [], []
    for r in rows:
        pid, model = r["problem_id"], r["model"]
        if (model, pid) in done:
            continue
        t = text_of(r)
        if not t or pid not in GOLD:
            continue
        # split at the LAST \boxed{...}: prefix + answer region (through closing brace)
        starts = [m.start() for m in re.finditer(r"\\boxed\{", t)]
        if not starts:
            continue
        s = starts[-1]
        depth, i = 0, s + len("\\boxed{") - 1
        for i in range(s + len("\\boxed") , len(t)):
            if t[i] == "{":
                depth += 1
            elif t[i] == "}":
                depth -= 1
                if depth == 0:
                    break
        else:
            continue
        prefix, ans = t[:s], t[s + len("\\boxed{"): i]
        alt = distractor(ans, pid, GOLD)
        pre_ids = tok(prefix[-6000:], add_special_tokens=True).input_ids
        for variant, label in ((ans, "orig"), (alt, "swap")):
            reg = "\\boxed{" + variant + "}"
            reg_ids = tok(reg, add_special_tokens=False).input_ids
            ids = (pre_ids + reg_ids)
            if len(ids) > MML - 8:
                ids = ids[-(MML - 8):]
                cut = len(ids) - len(reg_ids)
            else:
                cut = len(pre_ids)
            prompts.append(TokensPrompt(prompt_token_ids=ids))
            meta.append((model, pid, label, cut, len(reg_ids)))
    if not prompts:
        continue
    outs = llm.generate(prompts, sp)
    acc = {}
    for (model, pid, label, cut, nreg), o in zip(meta, outs):
        lp = 0.0; n = 0
        for pos in range(cut, cut + nreg):
            if pos < len(o.prompt_logprobs or []) and o.prompt_logprobs[pos]:
                ent = o.prompt_logprobs[pos].get(o.prompt_token_ids[pos])
                if ent is not None:
                    lp += ent.logprob; n += 1
        acc.setdefault((model, pid), {})[label] = lp / max(n, 1)
    for (model, pid), d in acc.items():
        if "orig" in d and "swap" in d:
            f.write(json.dumps(dict(model=model, problem_id=pid, lp_orig=d["orig"],
                                    lp_swap=d["swap"], support=d["orig"] - d["swap"])) + "\n")
            done.add((model, pid))  # dedupe across runs/all and runs/math500 variants
    f.flush()
    print("[swap done]", fn, flush=True)
f.close()
print("[answer_swap complete]", flush=True)
