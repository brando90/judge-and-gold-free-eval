# TLDR: Dataset loaders that yield problems with a gold reasoning trace AND a
# gold final answer. MATH-500 is the fast reproduction anchor (TFA was validated
# on MATH); GSM8K is the NL-rationale transfer test. Pin revisions for repro.
from __future__ import annotations

from dataclasses import dataclass

from tfa.boxed import extract_boxed


@dataclass(frozen=True)
class Problem:
    id: str
    question: str
    gold_solution: str   # the reference reasoning trace (teacher-forced target)
    gold_answer: str     # the final answer used for boxed-correctness of free-gen
    dataset: str
    meta: dict


# Pin these before any run (repro). Verify counts/licences per research-brief.
DATASETS = {
    "math500": dict(path="HuggingFaceH4/MATH-500", split="test", revision=None),
    # Full hendrycks MATH (per-subject configs; no 'answer' field, answer is boxed in solution).
    "math-full": dict(path="EleutherAI/hendrycks_math", name="algebra", split="test", revision=None),
    "gsm8k": dict(path="openai/gsm8k", name="main", split="test", revision=None),
    "gsm8k-platinum": dict(path="madrylab/gsm8k-platinum", split="test", revision=None),
    # Putnam-AXIOM (gated; needs HF_TOKEN). TFA never run here — weak-model floor expected.
    # Splits: 'original' (236), 'variations' (265, functional/contamination test), 'variations_org'.
    "putnam-axiom": dict(path="Putnam-AXIOM/putnam-axiom-dataset-v1", split="original", revision=None),
    "putnam-axiom-var": dict(path="Putnam-AXIOM/putnam-axiom-dataset-v1", split="variations", revision=None),
    # Omni-MATH (olympiad, IMO-hard). Full gold solutions + human difficulty levels. answer field present.
    "omni-math": dict(path="KbsdJames/Omni-MATH", split="test", revision=None),
    # WS5 non-math code: canonical solution (gold for TFA) + unit tests (deterministic oracle, no judge).
    "humaneval": dict(path="openai/openai_humaneval", split="test", revision=None),
    "mbpp": dict(path="google-research-datasets/mbpp", name="full", split="test", revision=None),
}


def load_problems(dataset: str, limit: int | None = None) -> list[Problem]:
    import os
    from datasets import load_dataset

    cfg = DATASETS[dataset]
    kwargs = {k: v for k, v in cfg.items() if k in ("name", "revision") and v is not None}
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    ds = load_dataset(cfg["path"], split=cfg["split"], token=token, **kwargs)
    out: list[Problem] = []
    for i, row in enumerate(ds):
        if limit is not None and i >= limit:
            break
        out.append(_to_problem(dataset, i, row))
    return out


def _to_problem(dataset: str, i: int, row: dict) -> Problem:
    if dataset == "humaneval":
        # gold_solution = canonical completion (what TFA teacher-forces); correctness via unit tests in meta.
        return Problem(
            id=str(row.get("task_id", i)),
            question=row["prompt"],
            gold_solution=row["canonical_solution"],
            gold_answer="",
            dataset=dataset,
            meta={"_code": "humaneval", "test": row["test"], "entry_point": row["entry_point"]},
        )
    if dataset == "mbpp":
        return Problem(
            id=str(row.get("task_id", i)),
            question=row["text"],
            gold_solution=row["code"],
            gold_answer="",
            dataset=dataset,
            meta={"_code": "mbpp", "test_list": row["test_list"]},
        )
    if dataset == "omni-math":
        ans = row.get("answer") or extract_boxed(row.get("solution", "")) or ""
        return Problem(
            id=str(i),
            question=row["problem"],
            gold_solution=row["solution"],
            gold_answer=str(ans),
            dataset=dataset,
            meta={"difficulty": row.get("difficulty"), "domain": row.get("domain")},
        )
    if dataset.startswith("math500"):
        return Problem(
            id=str(row.get("unique_id", i)),
            question=row["problem"],
            gold_solution=row["solution"],
            gold_answer=str(row["answer"]),
            dataset=dataset,
            meta={"level": row.get("level"), "subject": row.get("subject")},
        )
    if dataset == "math-full":
        # EleutherAI/hendrycks_math: no 'answer' field; answer is \boxed{} in the solution.
        sol = row["solution"]
        return Problem(
            id=str(i),
            question=row["problem"],
            gold_solution=sol,
            gold_answer=extract_boxed(sol) or "",
            dataset=dataset,
            meta={"level": row.get("level"), "subject": row.get("type")},
        )
    if dataset.startswith("gsm8k"):
        sol = row["answer"]
        ans = sol.split("####")[-1].strip().replace(",", "")
        return Problem(id=str(i), question=row["question"], gold_solution=sol,
                       gold_answer=ans, dataset=dataset, meta={})
    if dataset.startswith("putnam"):
        sol = row.get("solution", "")
        # Putnam-AXIOM has no separate answer field; the answer is \boxed{} in the solution.
        ans = extract_boxed(sol) or ""
        return Problem(
            id=str(row.get("id", i)),
            question=row.get("problem") or row.get("question", ""),
            gold_solution=sol,
            gold_answer=ans,
            dataset=dataset,
            meta={"variation": row.get("variation"), "answer_type": row.get("answer_type")},
        )
    raise KeyError(dataset)
