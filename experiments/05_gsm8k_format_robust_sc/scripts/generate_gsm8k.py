#!/usr/bin/env python3
"""Experiment 05 generation: n=16 GSM8K test samples per problem, experiment 04 sampler.

Local vLLM only. This file does not import vLLM, datasets, or any paid client until main()
asks for generation. Importing it is safe on a CPU.

    python3 generate_gsm8k.py --write-tasks-only --tasks /lfs/mercury2/0/brando9/judge-free-eval-exp05/tasks_gsm8k_test.jsonl
    CUDA_VISIBLE_DEVICES=0,1 python3 generate_gsm8k.py --model meta-llama/Llama-3.1-8B-Instruct --tp 2 \\
        --tasks .../tasks_gsm8k_test.jsonl --out .../gen

Writes <out>/bon_gsm8k__<hf id with / as __>.jsonl. Problems already in that file are skipped.
Refuses to sample if the GSM8K test count or hash differs from PREREG.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Frozen in PREREG.md at commit time, from tfa.data.load_problems("gsm8k").
EXPECTED_N = 1319
DATASET_REVISION = "740312add88f781978c0658806c59bc2815b9866"
EXPECTED_SHA256 = "2ab55b8ba24d95e56625bf32c8be06010990fce4b0f4c08bb44d289f68cfb587"

N_DEFAULT = 16
TEMPERATURE = 1.0
TOP_P = 0.95
MAX_TOKENS = 1024
SEED = 0
MAX_MODEL_LEN = 4096
DTYPE = "bfloat16"
UTIL = 0.90

PROMPT_PREFIX = (
    "Solve the following math problem. Show your reasoning step by step, "
    "then give the final answer in \\boxed{}.\n\n"
)

# id, label, Hugging Face id, tensor-parallel size on a 16 GB GPU.
# 7B/8B are TP 2. Qwen3-1.7B is TP 1 (the substring "7B" is not a 7B model).
MODELS = [
    ("llama31_8b", "Llama-3.1-8B-Instruct", "meta-llama/Llama-3.1-8B-Instruct", 2),
    ("qwen25_7b", "Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-7B-Instruct", 2),
    ("qwen3_4b", "Qwen3-4B (non-thinking)", "Qwen/Qwen3-4B", 1),
    ("qwen3_1p7b", "Qwen3-1.7B (non-thinking)", "Qwen/Qwen3-1.7B", 1),
    ("dsmath_7b_rl", "DeepSeek-Math-7B-RL", "deepseek-ai/deepseek-math-7b-rl", 2),
    ("mistral_7b", "Mistral-7B-Instruct-v0.2", "mistralai/Mistral-7B-Instruct-v0.2", 2),
    ("qwen3_8b", "Qwen3-8B (non-thinking)", "Qwen/Qwen3-8B", 2),
    ("qwen35_4b", "Qwen3.5-4B (non-thinking)", "Qwen/Qwen3.5-4B", 1),
    ("llama3_8b", "Llama-3-8B-Instruct", "meta-llama/Meta-Llama-3-8B-Instruct", 2),
    ("dsmath_7b_inst", "DeepSeek-Math-7B-Instruct", "deepseek-ai/deepseek-math-7b-instruct", 2),
]
TP2_IDS = {hf for _i, _l, hf, tp in MODELS if tp == 2}

REPO = Path(__file__).resolve().parents[3]


def prompt_of(problem: str) -> str:
    return PROMPT_PREFIX + problem


def thinking_kwargs(name: str) -> dict:
    """Qwen3 and Qwen3.5 non-thinking mode. Qwen2.5 does not contain 'Qwen3'."""
    return {"enable_thinking": False} if "Qwen3" in name else {}


def gsm8k_gold(answer_field: str) -> str:
    """Gold string after ####, GSM8K grader normalization (strip, drop thousands commas)."""
    if "####" not in answer_field:
        raise ValueError("GSM8K answer field has no #### marker")
    return answer_field.split("####")[-1].strip().replace(",", "")


def official_extract_answer(completion: str) -> str:
    """OpenAI grade_school_math/dataset.py extract_answer. '[invalid]' when the pattern misses."""
    import re
    match = re.search(r"#### (\-?[0-9\.\,]+)", completion)
    if not match:
        return "[invalid]"
    return match.group(1).strip().replace(",", "")


def grade_normalize(extracted: str) -> str:
    """Same normalization extract_answer applies to the captured number: strip, drop commas."""
    return extracted.strip().replace(",", "")


def task_sha256(tasks: list[dict]) -> str:
    h = hashlib.sha256()
    for t in tasks:
        h.update(str(t["problem_id"]).encode())
        h.update(b"\0")
        h.update(t["problem"].encode())
        h.update(b"\0")
        h.update(t["gold"].encode())
        h.update(b"\n")
    return h.hexdigest()


def assert_frozen(tasks: list[dict]) -> None:
    if len(tasks) != EXPECTED_N:
        raise SystemExit(f"GSM8K test count {len(tasks)} != frozen {EXPECTED_N}; not sampling")
    got = task_sha256(tasks)
    if got != EXPECTED_SHA256:
        raise SystemExit(f"GSM8K test hash {got} != frozen {EXPECTED_SHA256}; not sampling")


def rows_to_tasks(rows: list[dict]) -> list[dict]:
    tasks = []
    for i, row in enumerate(rows):
        gold = gsm8k_gold(row["answer"])
        tasks.append({
            "problem_id": str(i),
            "problem": row["question"],
            "question": row["question"],
            "answer": row["answer"],
            "gold": gold,
        })
    return tasks


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_frozen_tasks() -> list[dict]:
    """Repo loader's GSM8K mapping, pinned to the revision recorded in PREREG.md."""
    sys.path.insert(0, str(REPO / "experiments/tfa-vs-judge"))
    from datasets import load_dataset
    from tfa.data import _to_problem

    ds = load_dataset("openai/gsm8k", "main", split="test", revision=DATASET_REVISION)
    tasks = []
    for i, row in enumerate(ds):
        problem = _to_problem("gsm8k", i, row)
        if official_extract_answer(problem.gold_solution) != problem.gold_answer:
            raise SystemExit(f"loader gold != official extract_answer at item {i}; not sampling")
        tasks.append({
            "problem_id": problem.id,
            "problem": problem.question,
            "question": problem.question,
            "answer": problem.gold_solution,
            "gold": problem.gold_answer,
        })
    assert_frozen(tasks)
    return tasks


def write_tasks(path: Path, tasks: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    tmp.replace(path)


def prepare_tasks(path: Path) -> list[dict]:
    loaded = load_frozen_tasks()
    if path.exists():
        existing = read_jsonl(path)
        assert_frozen(existing)
        return existing
    write_tasks(path, loaded)
    return loaded


def remaining(tasks: list[dict], out_path: Path) -> list[dict]:
    done = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                done.add(str(json.loads(line)["problem_id"]))
            except (json.JSONDecodeError, KeyError):
                continue
    return [t for t in tasks if t["problem_id"] not in done]


def out_path_for(out_dir: Path, name: str) -> Path:
    return out_dir / f"bon_gsm8k__{name.replace('/', '__')}.jsonl"


def require_tp(name: str, tp: int) -> None:
    if name in TP2_IDS and tp < 2:
        raise SystemExit(
            f"{name} is a 7B/8B model; tensor_parallel_size must be 2 so it fits in 16 GB"
        )
    if name not in TP2_IDS and tp != 1:
        raise SystemExit(f"{name} is not a 7B/8B model; launch it with tensor_parallel_size 1")


def generate(args: argparse.Namespace) -> None:
    """vLLM sampling. Called only from main(), so a spawn child does not construct another engine."""
    name = args.name or args.model
    require_tp(name, args.tp)
    if args.n != N_DEFAULT:
        raise SystemExit(f"n is frozen at {N_DEFAULT}")
    tasks = prepare_tasks(Path(args.tasks))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_path_for(out_dir, name)
    todo = remaining(tasks, out)
    print(f"[gen] {name}: {len(todo)} problems remaining, n={args.n}, tp={args.tp}", flush=True)
    if not todo:
        print("[gen] nothing to do", out, flush=True)
        return

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    tok = AutoTokenizer.from_pretrained(args.model)
    kw = thinking_kwargs(name)
    prompts = [
        tok.apply_chat_template(
            [{"role": "user", "content": prompt_of(r["problem"])}],
            tokenize=False, add_generation_prompt=True, **kw,
        )
        for r in todo
    ]
    llm = LLM(
        model=args.model,
        dtype=DTYPE,
        tensor_parallel_size=args.tp,
        gpu_memory_utilization=args.util,
        max_model_len=args.max_model_len,
        max_num_seqs=args.batch * args.n,
        enforce_eager=True,
    )
    sp = SamplingParams(n=args.n, max_tokens=MAX_TOKENS, temperature=TEMPERATURE, top_p=TOP_P, seed=SEED)
    with out.open("a") as f:
        for i in range(0, len(todo), args.batch):
            chunk = todo[i:i + args.batch]
            outs = llm.generate(prompts[i:i + args.batch], sp)
            for r, o in zip(chunk, outs):
                texts = [c.text for c in o.outputs]
                finishes = [c.finish_reason for c in o.outputs]
                if len(texts) != args.n:
                    raise SystemExit(f"{name} problem {r['problem_id']} returned {len(texts)} samples, want {args.n}")
                row = {
                    "problem_id": r["problem_id"],
                    "model": name,
                    "samples": texts,
                    "finish": finishes,
                    "answer": r["answer"],
                    "gold": r["gold"],
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[gen] {min(i + args.batch, len(todo))}/{len(todo)}", flush=True)
    print("[gen done]", out, flush=True)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Experiment 05 GSM8K sampling (local vLLM, no paid API)")
    ap.add_argument("--model", default=None, help="HF id or a local snapshot directory")
    ap.add_argument("--name", default=None, help="HF id used in the output name and the Qwen3 check")
    ap.add_argument("--tp", type=int, default=None, help="tensor parallel size (2 for 7B/8B, 1 otherwise)")
    ap.add_argument("--n", type=int, default=N_DEFAULT)
    ap.add_argument("--batch", type=int, default=4, help="problems per vLLM call; 4 fits 16 GB with n=16")
    ap.add_argument("--util", type=float, default=UTIL)
    ap.add_argument("--max-model-len", type=int, default=MAX_MODEL_LEN)
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--write-tasks-only", action="store_true")
    args = ap.parse_args(argv)
    if args.write_tasks_only:
        tasks = prepare_tasks(Path(args.tasks))
        print(f"[tasks] {len(tasks)} frozen sha256={task_sha256(tasks)}", flush=True)
        return
    if not args.model:
        raise SystemExit("--model is required unless --write-tasks-only")
    if args.tp is None:
        name = args.name or args.model
        args.tp = 2 if name in TP2_IDS else 1
    if args.out is None:
        raise SystemExit("--out is required unless --write-tasks-only")
    generate(args)


if __name__ == "__main__":
    main()
