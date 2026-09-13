import json, random, sys, os
from datasets import load_dataset

OUT = os.path.dirname(os.path.abspath(__file__))
N = 200

def sample_rows(n_rows, n=N):
    random.seed(0)
    return sorted(random.sample(range(n_rows), n))

def save(name, items):
    with open(os.path.join(OUT, f"items_{name}.jsonl"), "w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    import csv
    with open(os.path.join(OUT, f"items_{name}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(items[0].keys()))
        w.writeheader()
        for it in items:
            w.writerow(it)
    print(name, len(items))

which = sys.argv[1:]

if "math500" in which:
    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    idx = sample_rows(len(ds))
    save("math500", [{"id": f"math500-{i}", "row": i, "unique_id": ds[i]["unique_id"],
                      "question": ds[i]["problem"], "reference": ds[i]["answer"]} for i in idx])

if "gsm8k" in which:
    ds = load_dataset("openai/gsm8k", "main", split="test")
    idx = sample_rows(len(ds))
    save("gsm8k", [{"id": f"gsm8k-{i}", "row": i, "question": ds[i]["question"],
                    "reference": ds[i]["answer"].split("####")[-1].strip()} for i in idx])

if "deepscaler" in which:
    ds = load_dataset("agentica-org/DeepScaleR-Preview-Dataset", split="train")
    idx = sample_rows(len(ds))
    save("deepscaler", [{"id": f"deepscaler-{i}", "row": i, "question": ds[i]["problem"],
                         "reference": ds[i]["answer"]} for i in idx])

if "nqopen" in which:
    ds = load_dataset("google-research-datasets/nq_open", split="validation")
    idx = sample_rows(len(ds))
    save("nqopen", [{"id": f"nqopen-{i}", "row": i, "question": ds[i]["question"],
                     "reference": " | ".join(ds[i]["answer"])} for i in idx])

if "triviaqa" in which:
    ds = load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation")
    idx = sample_rows(len(ds))
    save("triviaqa", [{"id": f"triviaqa-{i}", "row": i, "qid": ds[i]["question_id"],
                       "question": ds[i]["question"], "reference": ds[i]["answer"]["value"],
                       "aliases": "; ".join(ds[i]["answer"]["aliases"][:8])} for i in idx])
