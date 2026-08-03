# E2 v2: PROPAGATED coherent-wrong candidates -- the real subtle-error instrument.
# For each base item (correct GSM8K solution), GPT-5.2 rewrites it carrying ONE early numeric change
# through the whole solution consistently (internally coherent, wrong final answer). Then a MECHANICAL
# verifier: (1) every "a op b = c" stated in the rewrite must be arithmetically true (+-0.01),
# (2) extracted final answer != gold, (3) rewrite length within 2x of original. Only verified rewrites
# become tasks -- immune to label noise (we made the error) and to generator sloppiness (verified).
# Depth knob: change planted at step 1 (deep propagation) vs second-to-last step (shallow propagation,
# only the final answer inherits it). Both are coherent; "shallow" is the subtler edit (less text changed).
import json, re, random, argparse
from concurrent.futures import ThreadPoolExecutor
from subtlety_e1 import extract_answer

ARITH = re.compile(r"(-?\d[\d,]*\.?\d*)\s*([-+*/x×])\s*(-?\d[\d,]*\.?\d*)\s*=\s*(-?\d[\d,]*\.?\d*)")

def arithmetic_ok(text):
    bad = 0; tot = 0
    for m in ARITH.finditer(text):
        a, op, b, c = m.groups()
        try:
            a, b, c = float(a.replace(",", "")), float(b.replace(",", "")), float(c.replace(",", ""))
        except Exception:
            continue
        tot += 1
        v = a + b if op == "+" else a - b if op == "-" else a * b if op in "*x×" else (a / b if b else None)
        if v is None or abs(v - c) > 0.011 * max(1, abs(c)): bad += 1
    return bad == 0 and tot >= 2, tot, bad

REWRITE = """Rewrite the following (correct) solution so that it contains ONE specific arithmetic change and
stays PERFECTLY internally consistent: {instr}
Carry the changed value through EVERY subsequent step and the final answer, recomputing all downstream
arithmetic correctly given the change. Do not flag or explain the change. Keep the same style and length.
Every arithmetic statement you write (a op b = c) must be arithmetically TRUE; only the one changed input
makes the final answer wrong. End with the final answer in the same format as the original.

Problem:
{q}

Original correct solution:
{sol}

Output ONLY the rewritten solution, nothing else."""

def rewrite(item, mode):
    import litellm; litellm.drop_params = True
    instr = ("in the FIRST computation step, misread one input number (e.g. off by one or a plausible misparse of the problem)"
             if mode == "deep" else
             "in the LAST computation step before the final answer, use a plausibly wrong operation or input")
    try:
        r = litellm.completion(model="openai/gpt-5.2",
                               messages=[{"role": "user", "content": REWRITE.format(instr=instr, q=item["question"], sol=item["candidate"])}],
                               temperature=0.3, max_tokens=1200)
        return (r.choices[0].message.content or "").strip()
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    # bases: the orig2 candidates from planted_tasks (known-correct, well-structured)
    bases = {}
    for line in open("runs/planted_tasks.jsonl"):
        t = json.loads(line)
        if t["cond"] == "orig2": bases[t["pid"]] = t
    items = list(bases.values())[:args.n]
    print(f"{len(items)} base items")

    def gold_ans(g):
        m = re.search(r"####\s*([^\n]+)", g or "")
        return extract_answer("#### " + m.group(1)) if m else extract_answer(g)

    jobs = [(it, mode) for it in items for mode in ("deep", "shallow")]
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        outs = list(ex.map(lambda jm: (jm[0], jm[1], rewrite(*jm)), jobs))

    tasks, stats = [], {"ok": 0, "bad_arith": 0, "same_ans": 0, "fail": 0}
    tid = 0
    for it, mode, txt in outs:
        if not txt or len(txt) > 2.2 * len(it["candidate"]) + 500: stats["fail"] += 1; continue
        ok, tot, bad = arithmetic_ok(txt)
        if not ok: stats["bad_arith"] += 1; continue
        ga, ra = gold_ans(it["gold"]), extract_answer(txt)
        if ra is None or ga is None or ra == ga: stats["same_ans"] += 1; continue
        stats["ok"] += 1
        tasks.append(dict(task_id=tid, cond=f"prop_{mode}", pid=it["pid"], dataset="gsm8k",
                          solver="PROP", question=it["question"], gold=it["gold"], candidate=txt,
                          cc=0.0, label_src=f"propagated_{mode}", tfa=None)); tid += 1
    # controls: fresh orig2 for the SAME pids that got at least one verified rewrite
    keep = {t["pid"] for t in tasks}
    for pid in keep:
        it = bases[pid]
        tasks.append(dict(task_id=tid, cond="orig2", pid=pid, dataset="gsm8k", solver="PROP",
                          question=it["question"], gold=it["gold"], candidate=it["candidate"],
                          cc=1.0, label_src="orig2", tfa=None)); tid += 1
    with open("runs/propagated_tasks.jsonl", "w") as f:
        for t in tasks: f.write(json.dumps(t) + "\n")
    print(f"verification: {stats} | wrote runs/propagated_tasks.jsonl: {len(tasks)} tasks over {len(keep)} items")

if __name__ == "__main__":
    main()
