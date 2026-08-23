# P-T2 anchoring-margin analysis (registered in docs/multi-valid-bon-registration.md):
# among ORACLE-VALID samples, does a referenced judge score samples matching the shown
# ref_answer higher than equally-valid non-matching samples, while a blind judge shows no
# such margin?  Margin = mean(score | valid & matches ref) - mean(score | valid & no match),
# within item, averaged over items with both kinds; per-item bootstrap CI.
# Run from experiments/tfa-vs-judge:
#   python3 ../../papers/analysis/ties_p2_margin.py runs/bon_scores_v2      (in-band smoke)
#   python3 ../../papers/analysis/ties_p2_margin.py runs/bon_scores_ties_full  (full, on cluster copy)
import json, re, sys

import numpy as np

rng = np.random.default_rng(0)
SCORES_DIR = sys.argv[1] if len(sys.argv) > 1 else "runs/bon_scores_v2"


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", a.strip().casefold()) or None


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + 7, 1
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


pool = {r["problem_id"]: r for r in
        (json.loads(l) for l in open("runs/bon/bon_ties__Qwen__Qwen2.5-7B-Instruct.jsonl"))}

import glob, os
results = []
for f in sorted(glob.glob(f"{SCORES_DIR}/ties__*__ref_a.jsonl")):
    cfg = os.path.basename(f)[:-8]
    for rep in ("a", "b"):
        path = f"{SCORES_DIR}/{cfg}_{rep}.jsonl"
        blind = path.replace("__ref_", "__noref_")
        for p, label in ((path, "ref"), (blind, "noref")):
            margins = []
            for l in open(p):
                r = json.loads(l)
                item = pool[r["problem_id"]]
                refn = norm(item["ref_answer"])
                valid = {norm(v) for v in item["valid_answers"]} - {None}
                match_scores, other_scores = [], []
                for s, esc, ok in zip(item["samples"], r["escore"], item["oracle"]):
                    if not ok:
                        continue
                    a = norm(extract_boxed(s) or s)
                    (match_scores if a == refn else other_scores).append(esc)
                if match_scores and other_scores:
                    margins.append(np.mean(match_scores) - np.mean(other_scores))
            if len(margins) >= 3:
                boot = [float(np.mean(rng.choice(margins, len(margins)))) for _ in range(2000)]
                results.append(dict(config=f"{cfg}_{rep}:{label}", n_items=len(margins),
                                    margin=round(float(np.mean(margins)), 2),
                                    ci=[round(np.percentile(boot, 2.5), 2),
                                        round(np.percentile(boot, 97.5), 2)]))

md = ["| judge (rep:cond) | n items | margin (ref-matching minus other-valid) | 95% CI |", "|---|---|---|---|"]
for r in results:
    md.append(f"| {r['config']} | {r['n_items']} | {r['margin']:+.2f} | [{r['ci'][0]:+.2f},{r['ci'][1]:+.2f}] |")
print("\n".join(md))
json.dump(results, open("../../papers/analysis/ties_p2_margin.json", "w"), indent=1)
