# Build the E4 judging task file for the judge x solver reliability matrix (runs on cluster).
# Candidates: solutions from solvers spanning capability (Qwen 0.5B..32B + phi-4, OLMo-13B, Mistral-7B)
# on MATH-500 and GSM8K, with CLEANED labels:
#   - flip cc=0 -> 1 when extracted answer == gold answer (robust normalization; scorer bugs)
#   - GSM8K: flip when answer == platinum gold; DROP items not present in platinum (suspect)
# Per (dataset, solver): up to 120 wrong + 120 correct, balanced where possible.
# Plus calibration probes per dataset: gold-as-candidate (expect high) and shuffled-garbage (expect low),
# used as the judge compliance gate (critic requirement).
import json, glob, re, random, collections, hashlib
from subtlety_e1 import extract_answer, load_cc, CC_ALL

def gold_ans(gold, ds):
    if ds == "gsm8k":
        m = re.search(r"####\s*([^\n]+)", gold or "")
        if m: return extract_answer("#### " + m.group(1))
    return extract_answer(gold)

def qkey(q): return hashlib.md5(re.sub(r"\s+", " ", (q or "").strip())[:160].encode()).hexdigest()

plat_gold = {}
for fp in glob.glob("runs/all/gsm8k-platinum__*.jsonl"):
    for line in open(fp):
        r = json.loads(line)
        plat_gold[qkey(r.get("question"))] = gold_ans(r.get("gold_solution"), "gsm8k")
    break

SOLVERS = ["Qwen/Qwen2.5-0.5B-Instruct", "Qwen/Qwen2.5-3B-Instruct", "Qwen/Qwen2.5-14B-Instruct",
           "Qwen/Qwen2.5-32B-Instruct", "microsoft/phi-4", "allenai/OLMo-2-1124-13B-Instruct",
           "mistralai/Mistral-7B-Instruct-v0.3"]
CFG = {"math500": dict(globs=["runs/math500/*.judged.jsonl", "runs/d2/math500__*.judged.jsonl",
                              "runs/all/math500__*.jsonl"], scores="runs/scores_math500.jsonl"),
       "gsm8k":   dict(globs=["runs/gsm8k/*.judged.jsonl", "runs/d2/gsm8k__*.judged.jsonl",
                              "runs/all/gsm8k__*.jsonl"], scores="runs/scores_gsm8k.jsonl")}

tasks, seen = [], set()
rng = random.Random(0)
for ds, cfg in CFG.items():
    cc_ds = load_cc(cfg["scores"])
    get_cc = lambda m, p: cc_ds.get((m, p), CC_ALL.get((m, p)))
    by_solver = collections.defaultdict(dict)
    golds = {}
    for g in cfg["globs"]:
        for fp in glob.glob(g):
            for line in open(fp):
                r = json.loads(line)
                m = r.get("model"); pid = r.get("problem_id")
                if m not in SOLVERS or (m, pid, ds) in seen: continue
                c = get_cc(m, pid)
                if c is None or not r.get("free_gen"): continue
                ans = extract_answer(r["free_gen"]); ga = gold_ans(r.get("gold_solution"), ds)
                cc2, src = c, "cc"
                if c == 0 and ans is not None and ga is not None and ans == ga:
                    cc2, src = 1.0, "flip_bug"
                if ds == "gsm8k":
                    pg = plat_gold.get(qkey(r.get("question")))
                    if pg is None: continue                    # not in platinum -> drop (suspect)
                    if c == 0 and ans is not None and ans == pg and pg != ga:
                        cc2, src = 1.0, "flip_platinum"
                seen.add((m, pid, ds))
                by_solver[m][pid] = dict(dataset=ds, solver=m, pid=pid, question=r["question"],
                                         gold=r["gold_solution"], candidate=r["free_gen"],
                                         cc=cc2, label_src=src,
                                         tfa=r.get("tfa_argmax"))
                golds[pid] = (r["question"], r["gold_solution"])
    for m, d in by_solver.items():
        wrong = [t for t in d.values() if t["cc"] == 0]
        right = [t for t in d.values() if t["cc"] == 1]
        rng.shuffle(wrong); rng.shuffle(right)
        take = wrong[:120] + right[:120]
        tasks.extend(take)
        print(f"{ds:8s} {m.split('/')[-1]:28s} wrong={len(wrong[:120]):3d} correct={len(right[:120]):3d}")
    # calibration probes
    pids = list(golds)[:30]
    for pid in pids:
        q, g = golds[pid]
        tasks.append(dict(dataset=ds, solver="CALIB", pid=pid, question=q, gold=g,
                          candidate=g, cc=1.0, label_src="calib_gold", tfa=None))
        words = g.split(); rng.shuffle(words)
        tasks.append(dict(dataset=ds, solver="CALIB", pid=pid, question=q, gold=g,
                          candidate=" ".join(words[:max(20, len(words)//2)]), cc=0.0,
                          label_src="calib_garbage", tfa=None))

rng.shuffle(tasks)
with open("runs/matrix_tasks.jsonl", "w") as f:
    for i, t in enumerate(tasks):
        t["task_id"] = i; f.write(json.dumps(t) + "\n")
print(f"\nTOTAL tasks: {len(tasks)}  (per judge model)")
