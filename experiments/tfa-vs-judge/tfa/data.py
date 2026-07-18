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
    "gsm8k": dict(path="openai/gsm8k", name="main", split="test", revision=None),
    "gsm8k-platinum": dict(path="madrylab/gsm8k-platinum", split="test", revision=None),
    # Putnam-AXIOM (gated; needs HF_TOKEN). TFA never run here — weak-model floor expected.
    # Splits: 'original' (236), 'variations' (265, functional/contamination test), 'variations_org'.
    "putnam-axiom": dict(path="Putnam-AXIOM/putnam-axiom-dataset-v1", split="original", revision=None),
    "putnam-axiom-var": dict(path="Putnam-AXIOM/putnam-axiom-dataset-v1", split="variations", revision=None),
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
    if dataset.startswith("math500"):
        return Problem(
            id=str(row.get("unique_id", i)),
            question=row["problem"],
            gold_solution=row["solution"],
            gold_answer=str(row["answer"]),
            dataset=dataset,
            meta={"level": row.get("level"), "subject": row.get("subject")},
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
