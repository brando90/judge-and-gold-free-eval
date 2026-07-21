#!/usr/bin/env python
# Agentic A0 (docs/agentic-tfa-plan.md): teacher-force the gold PR diff of each SWE-bench Verified task and
# measure TFA, MASKED to the changed content lines (the +/- lines), which is the faithful estimator, plus a
# whole-diff TFA as the contaminated baseline. One vLLM load per model. This computes the SIGNAL side; the
# pass@ target (fraction of hidden tests) is a separate harness run and is not done here.
from __future__ import annotations
import argparse, json, os, sys, numpy as np
from tfa.backends.vllm_backend import load_vllm
from tfa.backends.common import _FORMATTING

PROMPT_LOGPROBS_K = 5

def line_kind(ln: str):
    body = ln.rstrip("\n")
    if body.startswith(("+++", "---")): return "header"
    if body[:1] == "+": return "add"
    if body[:1] == "-": return "del"
    if body.startswith("@@") or body.startswith(("diff --git", "index ", "new file", "deleted file", "rename ", "similarity ")):
        return "header"
    return "context"

def tag_gold(tok, patch: str):
    """Tokenize the gold patch line-by-line, tagging each token. Returns gold_ids and two masks:
    changed (+/- content) and added (+ content only, the tokens the model must generate that are NOT in
    the pre-edit context we hand it, hence the most faithful competence signal)."""
    gold_ids, changed, added = [], [], []
    for ln in patch.splitlines(keepends=True):
        k = line_kind(ln)
        ids = tok(ln, add_special_tokens=False).input_ids
        gold_ids += ids
        changed += [k in ("add", "del")] * len(ids)
        added += [k == "add"] * len(ids)
    return gold_ids, changed, added

def pre_edit_context(patch: str, max_chars=8000):
    """Reconstruct the code the fix edits (context + deleted lines, prefixes stripped), i.e. the 'oracle
    hunk context' around each change, so the model is told what code to modify without a repo checkout."""
    out = []
    for ln in patch.splitlines():
        k = line_kind(ln)
        if k in ("context", "del"): out.append(ln[1:] if ln[:1] in (" ", "-") else ln)
    return "\n".join(out)[:max_chars]

def build_prompt(tok, issue: str, patch: str, max_issue_chars=5000):
    # oracle-hunk-context variant: give the issue AND the pre-edit code regions, ask for the fix as a diff.
    # With the code in context, the diff's context and deleted lines are copyable, so the ADDED-line mask
    # isolates the tokens that require actually knowing the fix. Fixed wording for reproducibility.
    issue = (issue or "").strip()[:max_issue_chars]
    code = pre_edit_context(patch)
    msg = ("You are fixing a bug in a Python repository. Given the issue and the relevant code, produce the "
           "fix as a unified diff (git patch).\n\nIssue:\n" + issue + "\n\nRelevant code to modify:\n" + code +
           "\n\nUnified diff of the fix:\n")
    return tok(msg, add_special_tokens=True).input_ids

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--gpu-mem-util", type=float, default=0.85)
    ap.add_argument("--max-gold-tokens", type=int, default=1400)   # skip pathologically long diffs
    ap.add_argument("--out", default="runs/swebench")
    args = ap.parse_args()

    from datasets import load_dataset
    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    if args.limit: ds = ds.select(range(args.limit))
    llm, tok = load_vllm(args.model, tp_size=args.tp, gpu_memory_utilization=args.gpu_mem_util)

    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    prepared, kept = [], []
    for r in ds:
        gold_ids, changed, added = tag_gold(tok, r["patch"])
        if not any(added) or len(gold_ids) > args.max_gold_tokens: continue
        pids = build_prompt(tok, r["problem_statement"], r["patch"])
        prepared.append((pids, gold_ids, changed, added)); kept.append(r["instance_id"])
    prompts = [TokensPrompt(prompt_token_ids=(p + g)) for (p, g, _, _) in prepared]
    sp = SamplingParams(max_tokens=1, temperature=1.0, prompt_logprobs=PROMPT_LOGPROBS_K)
    outs = llm.generate(prompts, sp)

    os.makedirs(args.out, exist_ok=True)
    safe = args.model.replace("/", "__")
    path = f"{args.out}/swebench__{safe}.jsonl"
    W, C, A = [], [], []
    with open(path, "w") as f:
        for (pids, gold_ids, changed, added), out, iid in zip(prepared, outs, kept):
            plps = out.prompt_logprobs; p = len(pids)
            hw = tw = hc = tc = ha = ta = 0
            for k, gid in enumerate(gold_ids):
                d = plps[p + k]
                if not d: continue
                top1 = min(d.items(), key=lambda kv: kv[1].rank)[0]
                m = int(top1 == gid)
                tw += 1; hw += m
                if changed[k]: tc += 1; hc += m
                if added[k]: ta += 1; ha += m
            if ta == 0: continue
            whole = hw / tw; masked = hc / tc if tc else 0.0; addedtfa = ha / ta
            W.append(whole); C.append(masked); A.append(addedtfa)
            f.write(json.dumps({"instance_id": iid, "model": args.model,
                                "tfa_whole": whole, "tfa_masked_changed": masked, "tfa_masked_added": addedtfa,
                                "n_added_tokens": ta, "n_changed_tokens": tc, "n_total_tokens": tw}) + "\n")
    print(f"[done] {path}  n={len(A)}  added-TFA={np.mean(A):.3f}  changed-TFA={np.mean(C):.3f}  whole-TFA={np.mean(W):.3f}")
    sys.stdout.flush(); sys.stderr.flush(); os._exit(0)

if __name__ == "__main__":
    main()
