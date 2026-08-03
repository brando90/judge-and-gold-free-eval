# Adjudicate the GSM8K attractor-FP effect: genuine "plausible error fools the judge" vs BENCHMARK
# LABEL ERROR (models+judge right, gold wrong -- the GSM8K-Platinum story).
# For every judged wrong-with-attractor-answer GSM8K record:
#   (a) extraction check: attractor answer == gold answer under robust numeric normalization? -> cc bug
#   (b) platinum check: match the item into GSM8K-Platinum by question text; does the platinum gold
#       differ from the gsm8k gold, or does platinum mark this a bad/ambiguous item? -> label error
#   (c) residual: genuinely disputed items (attractor != gold, platinum agrees with gold) = candidate
#       real judge failures; list a few for frontier arbitration.
import json, glob, re, collections, hashlib, numpy as np
from subtlety_e1 import extract_answer, load_cc, CC_ALL

def gold_answer_gsm8k(gold):
    m = re.search(r"####\s*([^\n]+)", gold or "")
    return extract_answer("#### " + m.group(1)) if m else extract_answer(gold)

def qkey(q):  # robust question key
    return hashlib.md5(re.sub(r"\s+", " ", (q or "").strip())[:160].encode()).hexdigest()

# --- platinum golds by question ---
plat_gold = {}
for fp in glob.glob("runs/all/gsm8k-platinum__*.jsonl"):
    for line in open(fp):
        r = json.loads(line)
        plat_gold[qkey(r.get("question"))] = gold_answer_gsm8k(r.get("gold_solution"))
    break  # one model file suffices (same items)

cc_ds = load_cc("runs/scores_gsm8k.jsonl")
get_cc = lambda m, p: cc_ds.get((m, p), CC_ALL.get((m, p)))

# --- pool attractors (disjoint models), as in E1b ---
judged, judged_models = [], set()
for g in ["runs/gsm8k/*.judged.jsonl", "runs/gsm8k/*.judged.opus.jsonl", "runs/d2/gsm8k__*.judged.jsonl"]:
    for fp in glob.glob(g):
        for line in open(fp):
            r = json.loads(line)
            if r.get("judge_score") is None: continue
            c = get_cc(r["model"], r["problem_id"])
            if c is None: continue
            jm = str(r.get("judge_model", ""))
            judged.append(dict(model=r["model"], pid=r["problem_id"],
                               judge=("opus" if ("opus" in jm or "claude" in jm) else "gpt"),
                               score=float(r["judge_score"]), cc=c, q=r.get("question"),
                               gold=r.get("gold_solution"), ans=extract_answer(r.get("free_gen")),
                               bx=r.get("boxed_correct")))
            judged_models.add(r["model"])
pool = collections.defaultdict(dict)
for fp in glob.glob("runs/all/gsm8k__*.jsonl"):
    rows = [json.loads(l) for l in open(fp)]
    if not rows or rows[0]["model"] in judged_models: continue
    m = rows[0]["model"]
    for r in rows:
        c = get_cc(m, r["problem_id"])
        if c is not None: pool[r["problem_id"]][m] = (c, extract_answer(r.get("free_gen")))
attract = {}
for pid, d in pool.items():
    cnt = collections.Counter(v[1] for v in d.values() if v[0] == 0 and v[1] is not None)
    attract[pid] = {a for a, k in cnt.items() if k >= 2}

A = [j for j in judged if j["cc"] == 0 and j["ans"] and j["ans"] in attract.get(j["pid"], set())]
print(f"{len(A)} judged wrong-with-attractor-answer records ({len(set(j['pid'] for j in A))} items)")

cats = collections.Counter(); examples = collections.defaultdict(list)
for j in A:
    g_orig = gold_answer_gsm8k(j["gold"])
    g_plat = plat_gold.get(qkey(j["q"]))
    if j["ans"] == g_orig:
        cat = "EXTRACT_BUG(ans==gold)"          # cc said wrong but answer equals gold -> scorer bug
    elif g_plat is None:
        cat = "NOT_IN_PLATINUM(removed=suspect item)"   # platinum dropped/changed the item
    elif g_plat != g_orig and j["ans"] == g_plat:
        cat = "LABEL_ERROR(platinum agrees with model)"  # platinum fixed gold to the attractor
    elif g_plat != g_orig:
        cat = "LABEL_CHANGED(other)"
    else:
        cat = "GENUINE_DISPUTE(gold confirmed)"          # candidate real judge failure
    cats[cat] += 1
    if len(examples[cat]) < 3:
        examples[cat].append(dict(pid=j["pid"], model=j["model"].split("/")[-1], judge=j["judge"],
                                  score=j["score"], ans=j["ans"], gold=g_orig, plat=g_plat))

print("\nAdjudication of attractor records:")
tot = sum(cats.values())
for c, k in cats.most_common():
    print(f"  {c:42s} {k:4d}  ({100*k/tot:.0f}%)")

# judge scores by category: label-error records should be scored HIGH (judge right), genuine disputes?
print("\nMean judge score by category (high on label errors = judge was RIGHT):")
sc = collections.defaultdict(list)
for j in A:
    g_orig = gold_answer_gsm8k(j["gold"]); g_plat = plat_gold.get(qkey(j["q"]))
    if j["ans"] == g_orig: c = "EXTRACT_BUG"
    elif g_plat is None: c = "NOT_IN_PLATINUM"
    elif g_plat != g_orig and j["ans"] == g_plat: c = "LABEL_ERROR"
    elif g_plat != g_orig: c = "LABEL_CHANGED"
    else: c = "GENUINE_DISPUTE"
    sc[c].append(j["score"])
for c, v in sorted(sc.items()):
    print(f"  {c:16s} n={len(v):4d} mean={np.mean(v):.2f}  FP>=7: {100*float(np.mean(np.array(v)>=7)):.0f}%")

print("\nExamples (GENUINE_DISPUTE first):")
for c in ["GENUINE_DISPUTE(gold confirmed)", "LABEL_ERROR(platinum agrees with model)", "NOT_IN_PLATINUM(removed=suspect item)"]:
    for e in examples.get(c, []):
        print(f"  [{c.split('(')[0]}] pid={e['pid']} {e['model']} judge={e['judge']} score={e['score']} ans={e['ans']} gold={e['gold']} plat={e['plat']}")
