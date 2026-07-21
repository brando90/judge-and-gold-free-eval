#!/usr/bin/env python
# Agentic A1 (docs/agentic-tfa-plan.md), second modality: teacher-force the gold tool-call trajectory and
# measure TFA. The gold assistant turn is <tool_call>{'arguments': {...}, 'name': '...'}</tool_call>, a real
# token sequence, so TFA is well-defined. We report whole-TFA and a content-masked TFA (non-punctuation
# tokens: the argument values and names, i.e. the competence-bearing part, not the JSON scaffolding).
# CAVEAT: this dataset's gold is model-generated, so cross-family numbers are style-confounded; treat as a
# within-family / modality probe, per the plan's provenance warning.
from __future__ import annotations
import argparse, json, os, sys, re, numpy as np
from tfa.backends.vllm_backend import load_vllm
from tfa.backends.common import _FORMATTING

PROMPT_LOGPROBS_K = 5

def first_toolcall(conv):
    """Return (prompt_text, gold_text) for the first assistant turn that emits a tool_call."""
    sys_txt, user_txt = "", ""
    for m in conv:
        role = m.get("from") or m.get("role")
        val = m.get("value") or m.get("content") or ""
        if role == "system": sys_txt = val
        elif role in ("human", "user"): user_txt = val
        elif role in ("gpt", "assistant") and "<tool_call>" in val:
            return sys_txt, user_txt, val
    return None

def build_prompt(tok, sys_txt, user_txt):
    msgs = []
    if sys_txt: msgs.append({"role": "system", "content": sys_txt})
    msgs.append({"role": "user", "content": user_txt})
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return tok(text, add_special_tokens=False).input_ids

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--limit", type=int, default=800)
    ap.add_argument("--gpu-mem-util", type=float, default=0.6)
    ap.add_argument("--max-gold-tokens", type=int, default=600)
    ap.add_argument("--out", default="runs/toolcall")
    args = ap.parse_args()

    from datasets import load_dataset
    ds = load_dataset("interstellarninja/tool-calls-multiturn", split="train")
    if args.limit: ds = ds.select(range(min(args.limit, len(ds))))
    llm, tok = load_vllm(args.model, tp_size=1, gpu_memory_utilization=args.gpu_mem_util)

    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    prepared, kept = [], []
    for i, r in enumerate(ds):
        fc = first_toolcall(r["conversations"])
        if not fc: continue
        sys_txt, user_txt, gold = fc
        pids = build_prompt(tok, sys_txt, user_txt)
        gold_ids = tok(gold, add_special_tokens=False).input_ids
        if not gold_ids or len(gold_ids) > args.max_gold_tokens: continue
        content = [not bool(_FORMATTING.match(tok.decode([t]))) for t in gold_ids]
        if not any(content): continue
        prepared.append((pids, gold_ids, content)); kept.append(r.get("id", i))
    prompts = [TokensPrompt(prompt_token_ids=(p + g)) for (p, g, _) in prepared]
    sp = SamplingParams(max_tokens=1, temperature=1.0, prompt_logprobs=PROMPT_LOGPROBS_K)
    outs = llm.generate(prompts, sp)

    os.makedirs(args.out, exist_ok=True)
    safe = args.model.replace("/", "__")
    path = f"{args.out}/toolcall__{safe}.jsonl"
    W, C = [], []
    with open(path, "w") as f:
        for (pids, gold_ids, content), out, iid in zip(prepared, outs, kept):
            plps = out.prompt_logprobs; p = len(pids)
            hw = tw = hc = tcn = 0
            for k, gid in enumerate(gold_ids):
                d = plps[p + k]
                if not d: continue
                top1 = min(d.items(), key=lambda kv: kv[1].rank)[0]
                m = int(top1 == gid)
                tw += 1; hw += m
                if content[k]: tcn += 1; hc += m
            if tcn == 0: continue
            whole = hw / tw; masked = hc / tcn
            W.append(whole); C.append(masked)
            f.write(json.dumps({"id": iid, "model": args.model, "tfa_whole": whole,
                                "tfa_masked_content": masked, "n_content_tokens": tcn, "n_total_tokens": tw}) + "\n")
    print(f"[done] {path}  n={len(C)}  content-TFA={np.mean(C):.3f}  whole-TFA={np.mean(W):.3f}")
    sys.stdout.flush(); sys.stderr.flush(); os._exit(0)

if __name__ == "__main__":
    main()
