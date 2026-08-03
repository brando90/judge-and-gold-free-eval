# E2 builder: planted-error subtlety ladder (causal). Take CLEANED-correct GSM8K solutions with >=4
# computed steps ("= number" occurrences). For each, produce 4 corruptions + control:
#   pos in {early, late} x mag in {small (+/-~10% or +-2), gross (x10+7)}
# We corrupt exactly ONE computed result (the text after an '=' sign), leaving all other text including
# the stated final answer unchanged -> an internal inconsistency whose downstream footprint (position)
# and salience (magnitude) are mechanically controlled. A perfect rubric-following judge scores corrupted
# reasoning low; detection = score(orig2) - score(corrupted), paired, both freshly judged.
import json, glob, re, random, collections
from subtlety_e1 import extract_answer, load_cc, CC_ALL

def gold_ans(gold):
    m = re.search(r"####\s*([^\n]+)", gold or "")
    return extract_answer("#### " + m.group(1)) if m else extract_answer(gold)

NUM_AFTER_EQ = re.compile(r"=\s*\$?(-?\d[\d,]*\.?\d*)")

def corrupt(text, which, mag, rng):
    """Corrupt the which-th (index into eq list) computed number. Returns new text or None."""
    ms = list(NUM_AFTER_EQ.finditer(text))
    if not ms: return None
    m = ms[which]
    raw = m.group(1); clean = raw.replace(",", "")
    try: val = float(clean)
    except Exception: return None
    if mag == "small":
        delta = max(1, round(abs(val) * 0.1)) if abs(val) >= 10 else rng.choice([1, 2])
        newv = val + rng.choice([-1, 1]) * delta
    else:
        newv = val * 10 + 7
    if newv == val: newv = val + 3
    news = str(int(newv)) if float(newv).is_integer() else f"{newv:.2f}"
    s, e = m.span(1)
    return text[:s] + news + text[e:]

def main():
    cc_ds = load_cc("runs/scores_gsm8k.jsonl")
    get_cc = lambda m, p: cc_ds.get((m, p), CC_ALL.get((m, p)))
    rng = random.Random(0)
    cands = []
    seen_items = set()
    for g in ["runs/gsm8k/*.judged.jsonl", "runs/all/gsm8k__*.jsonl"]:
        for fp in glob.glob(g):
            for line in open(fp):
                r = json.loads(line)
                mdl, pid = r.get("model"), r.get("problem_id")
                if pid in seen_items or not r.get("free_gen"): continue
                c = get_cc(mdl, pid)
                ans, ga = extract_answer(r["free_gen"]), gold_ans(r.get("gold_solution"))
                correct = (c == 1) or (ans is not None and ga is not None and ans == ga)
                if not correct: continue
                eqs = list(NUM_AFTER_EQ.finditer(r["free_gen"]))
                if len(eqs) < 4 or len(r["free_gen"]) > 3000: continue
                seen_items.add(pid)
                cands.append(r)
    rng.shuffle(cands); cands = cands[:130]
    print(f"{len(cands)} correct, >=4-step GSM8K solutions selected")

    tasks = []
    tid = 0
    for r in cands:
        text = r["free_gen"]; n_eq = len(list(NUM_AFTER_EQ.finditer(text)))
        idx_early, idx_late = 0, n_eq - 2 if n_eq >= 2 else n_eq - 1   # avoid the very final eq
        base = dict(dataset="gsm8k", pid=r["problem_id"], solver=r["model"],
                    question=r["question"], gold=r["gold_solution"])
        variants = [("orig2", text)]
        ok = True
        for tag, which, mag in [("early_small", idx_early, "small"), ("early_gross", idx_early, "gross"),
                                ("late_small", idx_late, "small"), ("late_gross", idx_late, "gross")]:
            ct = corrupt(text, which, mag, rng)
            if ct is None or ct == text: ok = False; break
            variants.append((tag, ct))
        if not ok: continue
        for tag, ct in variants:
            tasks.append(dict(task_id=tid, cond=tag, candidate=ct, **base)); tid += 1
    with open("runs/planted_tasks.jsonl", "w") as f:
        for t in tasks: f.write(json.dumps(t) + "\n")
    n_items = len(tasks) // 5
    print(f"wrote runs/planted_tasks.jsonl: {len(tasks)} tasks ({n_items} items x 5 conditions)")

if __name__ == "__main__":
    main()
