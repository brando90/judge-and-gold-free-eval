# POST HOC (no registration weight): under best-of-n selection, which correct answer does a
# single-reference judge pick?
#
# Rung 2 of the reward-signal question. The policy-gradient simulation (rl_simulation.py) shows what
# a reference reward would pull a policy toward. This asks the same question about the thing people
# actually deploy: best-of-n selection, where a judge scores n sampled candidates and the highest
# scorer is returned. No training, no simulation dynamics -- just argmax over stored scores.
#
# For each task and each budget n, take the FIRST n of the 64 stored candidates (the sample order is
# the pressure schedule, so prefixes are honest best-of-n), pick the argmax under each reward, and
# record two things: whether the pick is correct at all, and -- given it is correct -- whether it is
# the particular correct answer the judge was shown.
#
# Three rewards, as in rl_simulation.py:
#   oracle      ground truth; ties broken by first index
#   referenced  judge's expected score with the reference shown   (what pipelines deploy)
#   blind       judge's expected score with no reference          (CONTROL)
#
# If the reference were an answer key, the referenced selector would track the oracle selector on
# both readouts. If it rewards agreement, its picks concentrate on the shown answer as n grows,
# because a larger pool offers more chances for the matching answer to appear.
import json, os, random, re

SEED = 0
BUDGETS = [1, 2, 4, 8, 16, 32, 64]
E = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "experiments", "tfa-vs-judge")


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", str(a).strip().casefold()) or None


def mnorm(a):
    return re.sub(r"[^a-z0-9]+", "", (a or "").strip().casefold())


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(text) and d:
        d += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


def matches(sample, ref_answer, domain):
    if domain == "mace":
        a, rn = mnorm(extract_boxed(sample) or sample[-200:]), mnorm(ref_answer)
        return int(a == rn or (len(rn) > 3 and rn in a))
    return int(norm(extract_boxed(sample) or sample) == norm(ref_answer))


def load(pool_f, scores_dir, judge, rep, domain):
    pool = [json.loads(l) for l in open(os.path.join(E, pool_f))]
    def sc(cond):
        p = os.path.join(E, scores_dir, f"{domain}__{judge}__{cond}_{rep}.jsonl")
        return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(p))}
    ref, blind = sc("ref"), sc("noref")
    items = []
    for t in pool:
        pid = t["problem_id"]
        if pid not in ref or pid not in blind:
            continue
        if domain == "mace" and (t.get("k") or 0) < 2:
            continue
        oracle = [int(o) for o in t["oracle"]]
        match = [matches(s, t["ref_answer"], domain) for s in t["samples"]]
        if sum(oracle) == 0:
            continue
        # a task can only show concentration if BOTH a matching and a non-matching correct
        # answer are available to choose between
        if not (any(o and m for o, m in zip(oracle, match)) and
                any(o and not m for o, m in zip(oracle, match))):
            continue
        items.append(dict(pid=pid, oracle=oracle, match=match, ref=ref[pid], blind=blind[pid]))
    return items


def pick(item, reward_key, n):
    """argmax over the first n candidates; ties to the lowest index, as a deployed selector would."""
    if reward_key == "oracle":
        sc = [float(o) for o in item["oracle"][:n]]
    else:
        sc = [(s if s is not None else -1e9) for s in item[reward_key][:n]]
    best, bi = None, 0
    for i, v in enumerate(sc):
        if best is None or v > best:
            best, bi = v, i
    return bi


def boot(vals, tag, B=2000):
    rng = random.Random(f"{SEED}|{tag}|{len(vals)}")
    ms = []
    for _ in range(B):
        s = [rng.choice(vals) for _ in vals]
        ms.append(sum(s) / len(s))
    ms.sort()
    return sum(vals) / len(vals), ms[int(.025 * B)], ms[int(.975 * B)]


if __name__ == "__main__":
    REPL = "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"
    MACE = "runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"
    CELLS = [("arithmetic", REPL, "runs/bon_scores_repl", "Qwen__Qwen2.5-7B-Instruct", "a", "synthk"),
             ("arithmetic", REPL, "runs/bon_scores_repl", "microsoft__phi-4", "a", "synthk"),
             ("MACE", MACE, "runs/bon_scores_mace", "Qwen__Qwen2.5-7B-Instruct", "a", "mace"),
             ("MACE", MACE, "runs/bon_scores_mace", "microsoft__phi-4", "a", "mace"),
             ("MACE", MACE, "runs/bon_scores_mace", "anthropic__claude-sonnet-5", "a", "mace")]
    out = {}
    print("Best-of-n selection over stored judge scores. Which correct answer gets picked?\n")
    for pool, pf, sd, judge, rep, dom in CELLS:
        items = load(pf, sd, judge, rep, dom)
        print(f"  {pool} / {judge}   ({len(items)} tasks with both a matching and a non-matching correct answer)")
        print(f"    {'n':>4}  {'oracle':>18}  {'blind (control)':>18}  {'referenced':>18}")
        cell = {}
        for n in BUDGETS:
            row = {}
            for rk in ("oracle", "blind", "ref"):
                mm = []
                for it in items:
                    i = pick(it, rk, n)
                    if it["oracle"][i]:                 # only correct picks can concentrate
                        mm.append(float(it["match"][i]))
                m, lo, hi = boot(mm, f"{judge}|{rk}|{n}") if mm else (float("nan"),) * 3
                row[rk] = dict(p_match_given_correct=m, ci=[lo, hi], n_correct_picks=len(mm))
            cell[n] = row
            f = lambda rk: f"{row[rk]['p_match_given_correct']:.3f} [{row[rk]['ci'][0]:.2f},{row[rk]['ci'][1]:.2f}]"
            print(f"    {n:>4}  {f('oracle'):>18}  {f('blind'):>18}  {f('ref'):>18}")
        out[f"{pool}|{judge}|{rep}"] = cell
        d64 = cell[64]["ref"]["p_match_given_correct"] - cell[64]["oracle"]["p_match_given_correct"]
        b64 = cell[64]["blind"]["p_match_given_correct"] - cell[64]["oracle"]["p_match_given_correct"]
        print(f"    at n=64: referenced - oracle = {d64:+.3f}   blind - oracle = {b64:+.3f} (control)\n")
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "bon_reference_selection_results.json"), "w"), indent=1)
    print("  wrote papers/analysis/bon_reference_selection_results.json")
