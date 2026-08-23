# Length-matched control for the answer-line intervention (registered pre-run; prediction
# below committed before any scoring). The answer-line collapse (+0.35 -> +0.02) could in
# principle be a token-count artifact rather than an informativeness effect: the short
# reference has ~15 tokens against ~180 for a worked solution. This arm holds length fixed
# and removes information: the reference is a FIXED content-free boilerplate paragraph,
# identical across items, padded to roughly the mean worked-reference length, followed by
# the same answer line. Same items, same models, same TFA machinery as tfa_shortref.py.
#
# REGISTERED PREDICTION P-L1: the across-model ranking signal stays collapsed on the padded
# reference (Spearman with accuracy near the answer-line value, far below the worked-reference
# +0.35), because the boilerplate is predictable for every model regardless of ability;
# informativeness, not token count, drives the ranking signal.
import json, os

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

MODELS = json.load(open("m500_models.json"))
ITEMS = [json.loads(l) for l in open("m500_short.jsonl")]
OUT = "runs/padref"; os.makedirs(OUT, exist_ok=True)

BOILER = ("We approach this problem carefully and systematically. First we read the problem "
          "statement and identify what is being asked. Then we recall the relevant "
          "definitions and standard techniques for problems of this kind. We set up the "
          "necessary expressions, carry out the required computations step by step, and "
          "simplify the result. We double-check each step of the computation to make sure "
          "no arithmetic mistakes were made along the way. Having verified that the "
          "reasoning is consistent and the calculations are correct, we can now state the "
          "final result of the problem with confidence. ")


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
    from vllm.inputs import TokensPrompt
    for it in ITEMS:
        p = prompt(it["question"])
        ref = BOILER + f"The final answer is \\boxed{{{it['answer']}}}."
        pid_ids = tok(p, add_special_tokens=True).input_ids
        ref_ids = tok(ref, add_special_tokens=False).input_ids
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
                                    tfa_pad=(hits / tot if tot else None), n_ref=tot)) + "\n")
    print("wrote", out, flush=True)
    del llm
    import gc, torch; gc.collect(); torch.cuda.empty_cache()
print("[padref-done]")
