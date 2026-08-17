# Position-weighted TFA ablation (Brando's suggestion, full sweep). Stores PER-TOKEN reference
# hit vectors on MATH-500 (full human solution as reference) so any position-weighting scheme can
# be evaluated post-hoc locally. Registered prediction (docs/async-update-brando-aug17.md, written
# before this ran): weighting later tokens more decays the model-ranking signal monotonically
# toward the answer-only-reference null (+0.02), because the signal being reweighted is
# reference-complexity nuisance, not soundness.
# Run ON skampere1: CUDA_VISIBLE_DEVICES=7 .venv/bin/python tfa_postok.py <items_with_solutions>
import json, os, sys

from vllm import LLM, SamplingParams
from vllm.inputs import TokensPrompt
from transformers import AutoTokenizer

ITEMS_F = sys.argv[1] if len(sys.argv) > 1 else "m500_full.jsonl"
MODELS = json.load(open("m500_models.json"))
ITEMS = [json.loads(l) for l in open(ITEMS_F)]
assert all("solution" in it for it in ITEMS), "items file needs full reference solutions"
OUT = "runs/postok"; os.makedirs(OUT, exist_ok=True)
MML = 4096


def prompt(q):
    return ("Solve the following problem. Show your reasoning step by step and put the "
            f"final answer in \\boxed{{}}.\n\nProblem:\n{q}\n\nSolution:\n")


for Mname in MODELS:
    tag = Mname.replace("/", "__"); out = f"{OUT}/{tag}.jsonl"
    if os.path.exists(out) and sum(1 for _ in open(out)) >= len(ITEMS) - 5:
        print("skip", tag, flush=True); continue
    try:
        llm = LLM(model=Mname, dtype="bfloat16", gpu_memory_utilization=0.9, max_model_len=MML)
    except Exception as e:
        print("LOADFAIL", Mname, str(e)[:100], flush=True); continue
    tok = AutoTokenizer.from_pretrained(Mname)
    prompts, meta = [], []
    for it in ITEMS:
        p = prompt(it["question"])
        pid_ids = tok(p, add_special_tokens=True).input_ids
        ref_ids = tok(it["solution"], add_special_tokens=False).input_ids
        ids = (pid_ids + ref_ids)[: MML - 8]
        prompts.append(TokensPrompt(prompt_token_ids=ids))
        meta.append((it["problem_id"], len(pid_ids), len(ids) - len(pid_ids)))
    sp = SamplingParams(max_tokens=1, prompt_logprobs=1)
    outs = llm.generate(prompts, sp)
    with open(out, "w") as f:
        for (pid, np_, nr), o in zip(meta, outs):
            pl = o.prompt_logprobs
            hits = []
            for pos in range(np_, np_ + nr):
                if pos < len(pl) and pl[pos]:
                    tid = o.prompt_token_ids[pos]
                    ent = pl[pos].get(tid)
                    # hit = reference token is the argmax (rank 1) under the model
                    hits.append(1 if (ent is not None and ent.rank == 1) else 0)
            f.write(json.dumps(dict(problem_id=pid, n_ref=len(hits),
                                    hits="".join(map(str, hits)))) + "\n")
    print("[postok done]", tag, flush=True)
    del llm
