# POST HOC (R8-A Amendment 1): agreement between Sonnet 5 scores from the CLI partial run and the Messages API on the
# calls both interfaces completed. Run from experiments/tfa-vs-judge. Writes papers/analysis/r8_interface_agreement.json.
import json

import numpy as np
from scipy.stats import spearmanr


def load(f):
    out = {}
    for l in open(f):
        r = json.loads(l)
        if not r.get("error") and r.get("score") is not None:
            out[(r["problem_id"], r["idx"], r["cond"])] = r["score"]
    return out


cli, api = load("runs/r8/sonnet/repl.jsonl"), load("runs/r8/sonnet_api/repl.jsonl")
res = {}
for cond in ("noref", "ref", "both"):
    keys = [k for k in cli if k in api and (cond == "both" or k[2] == cond)]
    a, b = np.array([cli[k] for k in keys]), np.array([api[k] for k in keys])
    res[cond] = dict(calls=len(keys), exact_agreement=round(float((a == b).mean()), 4),
                     within_one=round(float((np.abs(a - b) <= 1).mean()), 4), mean_abs_diff=round(float(np.abs(a - b).mean()), 3),
                     mean_cli=round(float(a.mean()), 3), mean_api=round(float(b.mean()), 3),
                     spearman=round(float(spearmanr(a, b).correlation), 3))
json.dump(res, open("../../papers/analysis/r8_interface_agreement.json", "w"), indent=1)
print(json.dumps(res, indent=1))
