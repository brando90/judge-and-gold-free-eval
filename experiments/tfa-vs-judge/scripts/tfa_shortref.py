# SEV 2.1 deconfound: TFA with a SHORT, LOW-ENTROPY reference ("The final answer is \boxed{X}.")
# on the same MATH-500 items. Same saturation, same items; only reference complexity changes.
import json, os
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

MODELS = json.load(open("m500_models.json"))
ITEMS = [json.loads(l) for l in open("m500_short.jsonl")]
OUT = "runs/shortref"; os.makedirs(OUT, exist_ok=True)
def prompt(q):
    return ("Solve the following problem. Show your reasoning step by step and put the "
            f"final answer in \\boxed{{}}.\n\nProblem:\n{q}\n\nSolution:\n")
for Mname in MODELS:
    tag = Mname.replace("/", "__"); out = f"{OUT}/{tag}.jsonl"
    if os.path.exists(out) and sum(1 for _ in open(out)) >= len(ITEMS) - 5:
        print("skip", tag, flush=True); continue
    try:
        mml = 4096
        llm = LLM(model=Mname, dtype="bfloat16", gpu_memory_utilization=0.9, max_model_len=mml)
    except Exception as e:
        print("LOADFAIL", Mname, str(e)[:100], flush=True); continue
    tok = AutoTokenizer.from_pretrained(Mname)
    prompts, meta = [], []
    for it in ITEMS:
        p = prompt(it["question"]); ref = f"The final answer is \\boxed{{{it['answer']}}}."
        pid_ids = tok(p, add_special_tokens=True).input_ids
        ref_ids = tok(ref, add_special_tokens=False).input_ids
        from vllm.inputs import TokensPrompt
        prompts.append(TokensPrompt(prompt_token_ids=(pid_ids + ref_ids)[: mml - 8]))
        meta.append((it["problem_id"], len(pid_ids), len(ref_ids)))
    sp = SamplingParams(max_tokens=1, prompt_logprobs=1)
    outs = llm.generate(prompts, sp)
    with open(out, "w") as f:
        for (pid, np_, nr), o in zip(meta, outs):
            pl = o.prompt_logprobs
            hits = tot = 0
            for pos in range(np_, np_ + nr):
                if pos < len(pl) and pl[pos]:
                    tid = o.prompt_token_ids[pos]
                    ent = pl[pos].get(tid)
                    if ent is not None:
                        tot += 1; hits += (getattr(ent, "rank", 99) == 1)
            f.write(json.dumps(dict(problem_id=pid, model=Mname,
                                    tfa_short=(hits / tot if tot else None), n_ref=tot)) + "\n")
    print("wrote", out, flush=True)
    del llm
    import gc, torch; gc.collect(); torch.cuda.empty_cache()
print("[shortref-done]")
