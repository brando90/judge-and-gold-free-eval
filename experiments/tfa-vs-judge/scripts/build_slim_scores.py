# Rebuild the committed slim per-item scores so they contain ALL 17 models x 6 math datasets (the
# previous scores_all.jsonl was missing the Qwen core ladder). Correctness (cc) is recomputed with the
# fixed scorer from the raw judged runs, exactly as scripts/analyze_model_level.py does, so the slim file
# regenerates the model-level correlations without a GPU. Writes runs/scores_all_full.jsonl.
import json, glob, collections
from tfa.boxed import extract_boxed, extract_final_answer, answers_equivalent

def fam(m):
    m = m.lower()
    if "qwen2.5-math" in m or "qwen2-math" in m: return "Qwen-Math"
    if "deepseek-math" in m: return "DeepSeek-Math"
    if "mathstral" in m: return "Mathstral"
    if "qwen2.5" in m or "qwen2-" in m: return "Qwen2.5"
    if "mistral" in m: return "Mistral"
    if "phi" in m: return "Phi"
    if "olmo" in m: return "OLMo"
    return "other"

def gold_ans(r, dk):
    return r["gold_solution"].split("####")[-1].strip().replace(",", "") if dk == "gsm8k" else extract_boxed(r["gold_solution"])

A = "runs/all/{0}__*.jsonl"
ANCH = [
    ("math500", ["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl", "runs/wsv/math500__*.jsonl", A.format("math500")], "math500"),
    ("math-full", ["runs/mathfull/*.judged.jsonl", A.format("math-full")], "math500"),
    ("gsm8k", ["runs/gsm8k/*.judged.jsonl", "runs/d2/gsm8k__*.judged.jsonl", A.format("gsm8k")], "gsm8k"),
    ("gsm8k-platinum", ["runs/gsm8kp/*.judged.jsonl", A.format("gsm8k-platinum")], "gsm8k"),
    ("putnam-axiom", ["runs/putnam/*.judged.jsonl", "runs/d2/putnam-axiom__*.judged.jsonl", "runs/wsv/putnam-axiom__*.jsonl", A.format("putnam-axiom")], "putnam"),
    ("putnam-axiom-var", ["runs/putnamvar/*.judged.jsonl", A.format("putnam-axiom-var")], "putnam"),
]

out = open("runs/scores_all_full.jsonl", "w")
seen = collections.defaultdict(set)   # dataset -> models
n = 0
for dsname, globs, dk in ANCH:
    for g in globs:
        for f in glob.glob(g):
            R = [json.loads(l) for l in open(f)]
            R = [r for r in R if r]
            if not R: continue
            m = R[0]["model"]
            if "Qwen2.5-32B" in m: continue                 # match the 5-model Qwen ladder used throughout
            mm = m.split("/")[-1]
            if mm in seen[dsname]: continue                 # first file wins (avoid dup dirs)
            seen[dsname].add(mm)
            for r in R:
                cc = int(answers_equivalent(extract_final_answer(r["free_gen"], dk), gold_ans(r, dk)))
                row = dict(model=m, dataset=dsname, problem_id=r["problem_id"],
                           tfa_argmax=r["tfa_argmax"], tfa_logprob=r.get("tfa_logprob"),
                           n_gold_tokens=r.get("n_gold_tokens"), boxed_correct=r.get("boxed_correct"), cc=cc)
                if r.get("judge_score") is not None: row["judge_score"] = r["judge_score"]
                out.write(json.dumps(row) + "\n"); n += 1
out.close()
print("WROTE runs/scores_all_full.jsonl rows=%d" % n)
for ds in seen: print("  %-18s %2d models" % (ds, len(seen[ds])))
