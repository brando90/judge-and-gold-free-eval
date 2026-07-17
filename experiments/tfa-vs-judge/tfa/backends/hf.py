# TLDR: Ground-truth teacher-forcing TFA via HF Transformers. Slow but exact;
# used to validate the vLLM backend bit-for-bit on a toy. One forward pass over
# concat(prompt_ids, gold_ids); position (p+k-1) predicts gold token k.
from __future__ import annotations

from tfa.core import PosRecord
from tfa.backends.common import make_ids


def load_hf(model_name: str, dtype: str = "bfloat16", device: str = "cuda"):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=getattr(torch, dtype)
    ).to(device).eval()
    return model, tok


def tfa_records_hf(model, tokenizer, question: str, gold_solution: str, dataset: str) -> list[PosRecord]:
    import torch

    prompt_ids, gold_ids, content_flags = make_ids(tokenizer, question, gold_solution, dataset)
    if not gold_ids:
        return []
    input_ids = torch.tensor([prompt_ids + gold_ids], device=model.device)
    with torch.no_grad():
        logits = model(input_ids).logits[0]  # [T, V]
    logprobs = torch.log_softmax(logits.float(), dim=-1)

    p = len(prompt_ids)
    records: list[PosRecord] = []
    for k, gid in enumerate(gold_ids):
        pos = p + k - 1  # logits at `pos` predict the token at `pos+1` == gold token k
        row = logprobs[pos]
        top1 = int(row.argmax().item())
        records.append(PosRecord(
            gold_id=int(gid), top1_id=top1,
            gold_logprob=float(row[gid].item()), is_content=content_flags[k],
        ))
    return records
