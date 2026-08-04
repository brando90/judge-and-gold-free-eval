# Extend the human-labeling set for the validity study (Brando review, point 2), WITHOUT
# invalidating any labels already collected on the original 42 diagnostic traces.
#
# Reuse guarantee: labels key on the trace `id` (in both label.html and the Artifact, and in
# returned CSVs), and browser progress keys on unchanged localStorage keys. This script keeps
# the original 42 rows byte-identical (same ids, same order 1-42) and APPENDS:
#   Stratum R: 200 traces sampled uniformly at random from the MATH-500 pool (no selection on
#              TFA, judge, or correctness), so validity correlations rho(TFA, human) and
#              rho(judge, human) can be estimated without disagreement-selection bias.
#   Shared block: the first 40 R-items are flagged shared=1; every labeler grades these, giving
#              inter-rater agreement and the human-human ceiling to compare the judge against.
import json, glob, csv, random, re, collections
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent

random.seed(1)
OUTDIR = "human_eval"
N_RANDOM, N_SHARED = 200, 40

def texify(t):
    t = re.sub(r"\$\$(.+?)\$\$", r"\\[\1\\]", t, flags=re.S)
    t = re.sub(r"\$([^$\n]+?)\$", r"\\(\1\\)", t)
    return t

existing = [json.loads(l) for l in open(f"{OUTDIR}/traces_to_label.jsonl")]
existing = [r for r in existing if r.get("cell") != "R"]          # idempotent re-runs
existing_keys = set()
for r in existing:
    parts = r["id"].split("-")
    existing_keys.add((r["dataset"], r["model"][:8], "-".join(parts[2:-1])))
print(f"kept {len(existing)} original diagnostic rows (ids unchanged)")

# MATH-500 pool, same files the diagnostic set drew from
GLOBS = ["runs/math500/*Qwen2.5-7B*.judged.jsonl", "runs/math500/*Qwen2.5-14B*.judged.jsonl",
         "runs/d2/math500__*phi-4*.judged.jsonl"]
pool = []
for g in GLOBS:
    for f in glob.glob(g):
        pool += [json.loads(l) for l in open(f)]
pool = [r for r in pool if r.get("judge_score") is not None]
pool = [r for r in pool if ("MATH-500", r["model"].split("/")[-1][:8], str(r["problem_id"])) not in existing_keys]
print(f"pool after exclusions: {len(pool)}")

sample = random.sample(pool, N_RANDOM)
random.shuffle(sample)
rows_r = []
for k, r in enumerate(sample):
    ga = extract_boxed(r["gold_solution"])
    cc = int(answers_equivalent(extract_final_answer(r["free_gen"], "math500"), ga))
    shared = 1 if k < N_SHARED else 0
    rows_r.append(dict(
        id=f"MATH-R-{r['problem_id']}-{r['model'].split('/')[-1][:8]}",
        cell="R",
        cell_desc="random validity sample (drawn uniformly, no selection on scores)"
                  + (" · SHARED BLOCK: every labeler grades this one" if shared else ""),
        shared=shared, dataset="MATH-500", model=r["model"].split("/")[-1],
        tfa=round(r["tfa_argmax"], 3), judge=r["judge_score"], correct=cc,
        question=texify(r["question"]), gold_solution=texify(r["gold_solution"]),
        gold_answer=str(ga), gold_answer_disp="\\(" + str(ga) + "\\)",
        trace=texify(r["free_gen"])))

# shared block first among the new items, then the rest
rows_r.sort(key=lambda r: (-r["shared"]))
allrows = existing + rows_r
for i, r in enumerate(allrows): r["order"] = i + 1

with open(f"{OUTDIR}/traces_to_label.jsonl", "w") as f:
    for r in allrows: f.write(json.dumps(r) + "\n")
cols = ["order", "id", "dataset", "model", "cell", "cell_desc", "shared", "correct", "tfa", "judge",
        "gold_answer", "question", "gold_solution", "trace"]
with open(f"{OUTDIR}/traces_to_label.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
    for r in allrows: w.writerow(r)
print(f"total {len(allrows)} traces: {len(existing)} diagnostic + {len(rows_r)} random "
      f"({N_SHARED} of them shared/double-label)")
cnt = collections.Counter(r["model"] for r in rows_r)
print("random stratum by model:", dict(cnt))

# rebuild label.html by reusing the HTML template embedded in make_labeling_set.py
src = open("scripts/make_labeling_set.py").read()
tpl = src.split('HTML = """', 1)[1].rsplit('"""', 1)[0]
open(f"{OUTDIR}/label.html", "w").write(tpl.replace("__DATA__", json.dumps(allrows)))
print("rebuilt human_eval/label.html")
