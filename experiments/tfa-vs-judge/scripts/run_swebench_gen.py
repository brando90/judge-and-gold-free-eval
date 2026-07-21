#!/usr/bin/env python
# Free-generate a candidate patch per SWE-bench Verified instance, in the SAME gold-context setting used
# for patch-TFA (issue + reconstructed pre-edit hunks), so the harness target matches the TFA signal. Emit
# SWE-bench predictions format: {instance_id, model_name_or_path, model_patch} for scoring via sb-cli.
from __future__ import annotations
import argparse, json, os, re, sys
from tfa.backends.vllm_backend import load_vllm

def line_kind(ln):
    b = ln.rstrip("\n")
    if b.startswith(("+++", "---")): return "header"
    if b[:1] == "+": return "add"
    if b[:1] == "-": return "del"
    if b.startswith("@@") or b.startswith(("diff --git", "index ", "new file", "deleted file", "rename ", "similarity ")): return "header"
    return "context"

def pre_edit_context(patch, max_chars=8000):
    out = []
    for ln in patch.splitlines():
        k = line_kind(ln)
        if k in ("context", "del"): out.append(ln[1:] if ln[:1] in (" ", "-") else ln)
    return "\n".join(out)[:max_chars]

def build_msg(issue, patch, max_issue_chars=5000):
    issue = (issue or "").strip()[:max_issue_chars]
    code = pre_edit_context(patch)
    return ("You are fixing a bug in a Python repository. Given the issue and the relevant code, produce the "
            "fix as a unified diff (git patch), starting with 'diff --git'. Output ONLY the diff.\n\nIssue:\n"
            + issue + "\n\nRelevant code to modify:\n" + code + "\n\nUnified diff of the fix:\n")

def extract_patch(text):
    # take from the first 'diff --git' (or '--- ') to the end; strip code fences
    text = text.replace("```diff", "").replace("```patch", "").replace("```", "")
    m = re.search(r"(diff --git .*)", text, re.S)
    if m: return m.group(1).strip() + "\n"
    m = re.search(r"(--- a/.*)", text, re.S)
    return (m.group(1).strip() + "\n") if m else ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--gpu-mem-util", type=float, default=0.6)
    ap.add_argument("--max-tokens", type=int, default=1200)
    ap.add_argument("--out", default="runs/swebench_pred")
    args = ap.parse_args()

    from datasets import load_dataset
    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    if args.limit: ds = ds.select(range(args.limit))
    llm, tok = load_vllm(args.model, tp_size=1, gpu_memory_utilization=args.gpu_mem_util)
    from vllm import SamplingParams
    prompts = [tok.apply_chat_template([{"role": "user", "content": build_msg(r["problem_statement"], r["patch"])}],
                                       tokenize=False, add_generation_prompt=True) for r in ds]
    sp = SamplingParams(max_tokens=args.max_tokens, temperature=0.0, seed=0)
    outs = llm.generate(prompts, sp)

    os.makedirs(args.out, exist_ok=True)
    safe = args.model.replace("/", "__")
    path = f"{args.out}/{safe}.jsonl"
    nonempty = 0
    with open(path, "w") as f:
        for r, o in zip(ds, outs):
            patch = extract_patch(o.outputs[0].text)
            if patch.strip(): nonempty += 1
            f.write(json.dumps({"instance_id": r["instance_id"], "model_name_or_path": args.model,
                                "model_patch": patch}) + "\n")
    print(f"[done] {path}  n={len(ds)}  non-empty patches={nonempty}")
    sys.stdout.flush(); sys.stderr.flush(); os._exit(0)

if __name__ == "__main__":
    main()
