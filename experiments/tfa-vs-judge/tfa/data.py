# TLDR: Dataset loaders that yield problems with a gold reasoning trace AND a
# gold final answer. MATH-500 is the fast reproduction anchor (TFA was validated
# on MATH); GSM8K is the NL-rationale transfer test. Pin revisions for repro.
from __future__ import annotations

from dataclasses import dataclass


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
    # Putnam-AXIOM: TFA never run here (new territory); expect weak-model floor.
    "putnam-axiom": dict(path="Putnam-AXIOM/putnam-axiom-dataset-v1", split="train", revision=None),
}


def load_problems(dataset: str, limit: int | None = None) -> list[Problem]:
    from datasets import load_dataset

    cfg = DATASETS[dataset]
    kwargs = {k: v for k, v in cfg.items() if k in ("name", "revision") and v is not None}
    ds = load_dataset(cfg["path"], split=cfg["split"], **kwargs)
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
        return Problem(
            id=str(row.get("id", i)),
            question=row.get("problem") or row.get("question", ""),
            gold_solution=row.get("solution", ""),
            gold_answer=str(row.get("answer", "")),
            dataset=dataset,
            meta={"variation": row.get("variation")},
        )
    raise KeyError(dataset)
