# LoRA DPO training for the certificate gating experiment (see dpo_pairs.py for the
# registered predictions). Identical hyperparameters for both arms; only the pair file
# differs. Run on one GPU.
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument("--cond", required=True, help="arm tag; pairs file defaults to {out}/pairs_{cond}.jsonl")
ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
ap.add_argument("--pairs", default=None, help="override pairs file path")
ap.add_argument("--epochs", type=float, default=1.0)
ap.add_argument("--beta", type=float, default=0.1)
ap.add_argument("--lr", type=float, default=5e-6)
ap.add_argument("--out", default="runs/dpo")
args = ap.parse_args()

import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer

rows = [json.loads(l) for l in open(args.pairs or f"{args.out}/pairs_{args.cond}.jsonl")]
tok = AutoTokenizer.from_pretrained(args.model)


def to_chat(r):
    return dict(
        prompt=tok.apply_chat_template([{"role": "user", "content": r["prompt"]}],
                                       tokenize=False, add_generation_prompt=True),
        chosen=r["chosen"], rejected=r["rejected"])


ds = Dataset.from_list([to_chat(r) for r in rows])
# transformers >=5 takes dtype=, <5 takes torch_dtype=; accept either so this runs on the
# training venv as well as the inference one.
try:
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.bfloat16)
except TypeError:
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16)
model.config.use_cache = False

out_dir = f"{args.out}/adapter_{args.cond}"
cfg = DPOConfig(
    output_dir=out_dir, per_device_train_batch_size=1, gradient_accumulation_steps=8,
    num_train_epochs=args.epochs, learning_rate=args.lr, beta=args.beta,
    logging_steps=20, save_strategy="no", bf16=True, gradient_checkpointing=True,
    max_length=1536, report_to=[], seed=0)
peft_cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
trainer = DPOTrainer(model=model, args=cfg, train_dataset=ds,
                     processing_class=tok, peft_config=peft_cfg)
trainer.train()
trainer.save_model(out_dir)
print(f"[dpo_train] saved {out_dir}")
