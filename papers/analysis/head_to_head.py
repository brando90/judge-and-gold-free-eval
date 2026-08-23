# HEAD-TO-HEAD: does naive validation (raw judge-human agreement) predict which judge
# configurations get gamed under best-of-64 pressure, versus the audit's partial-correlation
# verdict? Run from experiments/tfa-vs-judge. Output: papers/analysis/head_to_head.{json,md}
#
# Per configuration: naive = Pearson corr(score, human soundness) on the 60-item anchor.
# Audit = (soundness partial | style, style partial | soundness) on the same items.
# Outcome = excess hack gap under BoN-64 on math (from runs/bon_v2_full.json summaries).
import glob, json, os

import numpy as np

rng = np.random.default_rng(0)


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def partial(x, y, z):
    x, y, z = map(lambda a: np.asarray(a, float), (x, y, z))
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return pearson(rx, ry)


labs = {r["id"]: r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
        if r.get("soundness") not in (None, "")}

# BoN math outcomes per config
bon = json.load(open("runs/bon_v2_full.json"))["summary"]


def outcome(cfg_key):
    s = bon.get(cfg_key)
    return None if s is None else dict(excess_gap=round(s["excess_gap"], 2),
                                       regret=round(s["oracle_regret64"], 3))


CONFIGS = []
for f in sorted(glob.glob("runs/cert_out/*.jsonl")):
    base = os.path.basename(f)[:-6]
    cond, model = base.split("_", 1)
    model = model.replace("_", "/", 1)
    CONFIGS.append((f"{cond}:{model.split('/')[-1]}", f,
                    f"math__Qwen__{model.split('/')[-1]}__{cond}"))
# frontier rows: honest (stored judge field) and sabotaged
rows_out = []
for name, path, bon_key in CONFIGS:
    scores = {}
    for l in open(path):
        r = json.loads(l)
        if r.get("score") is not None:
            scores[r["task_id"]] = float(r["score"])
    joined = [(scores[i], labs[i]["soundness"], labs[i]["style"])
              for i in scores if i in labs]
    if len(joined) < 20:
        continue
    x, s, st = zip(*[(a, float(b), float(c)) for a, b, c in joined])
    rows_out.append(dict(config=name, n=len(joined),
                         naive_pearson=round(pearson(x, s), 2),
                         sound_partial=round(partial(x, s, st), 2),
                         style_partial=round(partial(x, st, s), 2),
                         bon=outcome(bon_key)))

# honest frontier (judge field on same labels) and sabotaged GPT
x = [float(labs[i]["judge"]) for i in labs]
s = [float(labs[i]["soundness"]) for i in labs]
st = [float(labs[i]["style"]) for i in labs]
rows_out.append(dict(config="ref:GPT-5.2 (honest)", n=len(labs),
                     naive_pearson=round(pearson(x, s), 2),
                     sound_partial=round(partial(x, s, st), 2),
                     style_partial=round(partial(x, st, s), 2),
                     bon=dict(excess_gap=0.38, regret=0.117)))
sab = {}
for l in open("runs/cert_stylejudge_gpt.jsonl"):
    r = json.loads(l)
    tid = r.get("task_id") or r.get("id")
    sc = r.get("score") or r.get("soundness")
    if tid is not None and sc is not None:
        sab[tid] = float(sc)
joined = [(sab[i], float(labs[i]["soundness"]), float(labs[i]["style"]))
          for i in sab if i in labs]
if len(joined) >= 20:
    x, s, st = zip(*joined)
    rows_out.append(dict(config="sabotage:GPT-5.2", n=len(joined),
                         naive_pearson=round(pearson(x, s), 2),
                         sound_partial=round(partial(x, s, st), 2),
                         style_partial=round(partial(x, st, s), 2),
                         bon=dict(excess_gap=0.85, regret=0.133)))
else:
    print(f"[warn] sabotage join too small: {len(joined)} (keys look like {list(sab)[:2]})")

md = ["| config | n | naive r (raw agreement) | soundness partial | style partial | BoN gap | regret |",
      "|---|---|---|---|---|---|---|"]
for r in rows_out:
    b = r["bon"] or {}
    md.append(f"| {r['config']} | {r['n']} | {r['naive_pearson']:+.2f} | {r['sound_partial']:+.2f} | "
              f"{r['style_partial']:+.2f} | {b.get('excess_gap','')} | {b.get('regret','')} |")
json.dump(rows_out, open("../../papers/analysis/head_to_head.json", "w"), indent=1)
open("../../papers/analysis/head_to_head.md", "w").write(
    "# Naive validation vs the audit, as predictors of BoN-64 gaming (math)\n\n" + "\n".join(md) + "\n")
print("\n".join(md))
