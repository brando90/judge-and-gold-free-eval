# Build the deployment-pool audit labeling instrument: 60 candidates sampled from the BoN math
# pool (the 7B generator's own samples on in-band items), stratified half correct / half
# incorrect by the oracle, one candidate per item. Labeling these closes the population-shift
# gap: the audit was measured on 17 models' solutions while pressure pools come from one
# generator. Reuses build_label_artifact.py with patched IO and storage key.
import json, random

rng = random.Random(20260823)
pool = [json.loads(l) for l in open("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")]
gold = {json.loads(l)["problem_id"]: json.loads(l) for l in open("m500_full.jsonl")}
inband = [r for r in pool if "oracle" in r and 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8]
rng.shuffle(inband)

rows, want_correct = [], 30
for r in inband[:60]:
    g = gold.get(r["problem_id"])
    if g is None:
        continue
    want = 1 if want_correct > 0 else 0
    idxs = [i for i, ok in enumerate(r["oracle"]) if ok == want] or list(range(len(r["oracle"])))
    i = rng.choice(idxs)
    if r["oracle"][i] == 1:
        want_correct -= 1
    rows.append(dict(
        id=f"DEP-{r['problem_id']}-s{i}",
        cell="P", cell_desc="deployment pool (7B generator, best-of-n candidate)",
        dataset="MATH-500", model="Qwen2.5-7B-Instruct (sampled)",
        tfa=0.0, judge=0.0, correct=int(r["oracle"][i]),
        question=g["question"], gold_solution=g["solution"],
        gold_answer=g["answer"], gold_answer_disp=g["answer"],
        trace=r["samples"][i], order=0))
rng.shuffle(rows)
for k, r in enumerate(rows, 1):
    r["order"] = k
with open("human_eval/traces_deppool.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(f"wrote human_eval/traces_deppool.jsonl ({len(rows)} items, "
      f"{sum(r['correct'] for r in rows)} correct)")

src = open("scripts/build_label_artifact.py").read()
src = src.replace('open("human_eval/traces_to_label.jsonl")', 'open("human_eval/traces_deppool.jsonl")')
src = src.replace('open("human_eval/label_artifact_v2.html", "w")', 'open("human_eval/label_deppool.html", "w")')
src = src.replace('"wrote human_eval/label_artifact_v2.html', '"wrote human_eval/label_deppool.html')
src = src.replace('open("human_eval/label_artifact_v2.html")', 'open("human_eval/label_deppool.html")')
src = src.replace("const KEY='tfa_label_artifact_v1';", "const KEY='tfa_label_deppool_v1';")
src = src.replace("<h1>Reasoning-trace labeling</h1>",
                  "<h1>Reasoning-trace labeling &mdash; deployment pool (60 items)</h1>")
src = src.replace("'tfa_labels.json'", "'tfa_labels_deppool.json'")
src = src.replace("'tfa_labels.csv'", "'tfa_labels_deppool.csv'")
exec(compile(src, "build_label_artifact.py", "exec"))
