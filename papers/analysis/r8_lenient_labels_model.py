# POST HOC secondary labeling for the round-8 revision (no registration weight). Run from experiments/tfa-vs-judge after
# r8_lenient_labels.py and scripts/r8_extract_answers.py. Writes runs/r8/model_{repl,kpool}.jsonl.
# model label = registered label OR (for an unboxed reply) the constraint check accepts the answer Qwen2.5-14B-Instruct
# says the reply commits to; boxed replies keep the rule-based lenient label (their extraction is the box).
import ast
import json
import re

from r8_lenient_labels import POOLS, check, ints_of

for name, f in POOLS.items():
    ext = {}
    for l in open(f"runs/r8/extract_{name}__Qwen2.5-14B-Instruct.jsonl"):
        r = json.loads(l)
        ext[(r["problem_id"], r["idx"])] = r["answer"]
    lab = {json.loads(l)["problem_id"]: json.loads(l) for l in open(f"runs/r8/lenient_{name}.jsonl")}
    n = none = 0
    with open(f"runs/r8/model_{name}.jsonl", "w") as out:
        for t in (json.loads(l) for l in open(f)):
            p = t["params"] if isinstance(t["params"], dict) else ast.literal_eval(t["params"])
            L = lab[t["problem_id"]]
            refx = sorted(ints_of(t["ref_answer"]))
            m, mm = [], []
            for i, o in enumerate(t["oracle"]):
                if L["boxed"][i]:
                    m.append(L["lenient"][i])
                    mm.append(L["match"][i])
                    continue
                a = ext[(t["problem_id"], i)]
                n += 1
                if re.search(r"\bNONE\b", a) or not re.search(r"\d", a):
                    none += 1
                    m.append(int(o))
                    mm.append(int(bool(o) and L["match"][i]))
                    continue
                xs = ints_of(a.split("\n")[0])
                ok = check(p, xs)
                m.append(int(bool(o) or ok))
                # match is read from the same extraction that made the label
                mm.append(int(sorted(xs) == refx) if ok else int(bool(o) and L["match"][i]))
            out.write(json.dumps(dict(problem_id=t["problem_id"], model=m, model_match=mm)) + "\n")
    print(f"[r8 model labels] {name}: {n} unboxed replies, {none} with no committed answer")
