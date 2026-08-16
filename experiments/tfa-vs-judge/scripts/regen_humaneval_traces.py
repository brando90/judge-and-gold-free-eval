# Regenerate HumanEval free-gen traces WITH text for the code labeling set (the original runs
# saved only scores). 3 models (mirroring the math labeling design), greedy, one GPU.
import json, os, sys
from vllm import LLM, SamplingParams


MODELS = ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-14B-Instruct", "microsoft/phi-4"]
OUT = "runs/code_traces_v2"
os.makedirs(OUT, exist_ok=True)
ds = [json.loads(l) for l in open("humaneval.jsonl")]
def prompt_of(q):
    return ("Complete the following Python function. Output the full function implementation.\n\n"
            + q + "\n")
for M in MODELS:
    tag = M.replace("/", "__")
    out = f"{OUT}/humaneval__{tag}.jsonl"
    if os.path.exists(out) and sum(1 for _ in open(out)) >= 164:
        print("skip", tag); continue
    llm = LLM(model=M, dtype="bfloat16", gpu_memory_utilization=0.9, max_model_len=4096)
    sp = SamplingParams(max_tokens=1024, temperature=0.0)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(M)
    prompts = [tok.apply_chat_template([{"role": "user", "content": prompt_of(r["prompt"])}],
                                       tokenize=False, add_generation_prompt=True) for r in ds]
    outs = llm.generate(prompts, sp)
    with open(out, "w") as f:
        for r, o in zip(ds, outs):
            f.write(json.dumps(dict(problem_id=r["task_id"], model=M, question=r["prompt"],
                                    canonical_solution=r["canonical_solution"], test=r["test"],
                                    entry_point=r["entry_point"], free_gen=o.outputs[0].text)) + "\n")
    print("wrote", out)
    del llm
    import gc, torch; gc.collect(); torch.cuda.empty_cache()
print("[done]")
