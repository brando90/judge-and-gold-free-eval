# POST HOC simulation (no registration weight): does a single-reference judge reward, used as an RL
# reward signal, pull a policy toward the one correct answer it was shown?
#
# WHAT THIS IS. A policy-gradient simulation over scores that ALREADY EXIST. For each task we hold 64
# candidate responses, an exact oracle label for each, whether each matches the shown reference, and
# each candidate's expected judge score under a blind and a referenced call. The "policy" is a
# softmax over those 64 fixed candidates, trained by REINFORCE against one of three reward signals.
# No model is trained and no text is generated: the action space is the stored candidate set.
#
# WHAT THIS IS NOT. Evidence that RL training on a reference-guided verifier distorts a real policy.
# A real policy explores an open output space and can produce answers this candidate set does not
# contain. This simulation can only redistribute mass over answers already sampled. It is offered as
# a mechanism check, not as the demonstrated downstream harm the paper declines to claim.
#
# THREE REWARDS, same policy, same items, same seed:
#   oracle      R = 1 if the exact checker says the answer is correct          (ground truth)
#   referenced  R = judge's expected score / 10, reference shown                (what pipelines use)
#   blind       R = judge's expected score / 10, no reference                   (CONTROL: isolates the
#               reference, since any drift here comes from judge noise, not from the shown answer)
#
# READOUT. After training: P(valid), and among valid picks, P(matches the shown reference). If the
# reference signal merely tracked correctness, the referenced policy would match the oracle policy on
# both. If it rewards agreement, it concentrates valid mass on the matching answer.
import json, math, os, random, sys

NSTEP, LR, SEED = 4000, 0.05, 0
random.seed(SEED)

E = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "experiments", "tfa-vs-judge")


def norm(a):
    import re
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", str(a).strip().casefold()) or None


def extract_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(text) and d:
        d += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    return text[i + 7:j - 1]


def load(pool_f, scores_dir, judge, rep):
    pool = [json.loads(l) for l in open(os.path.join(E, pool_f))]
    def sc(cond):
        p = os.path.join(E, scores_dir, f"synthk__{judge}__{cond}_{rep}.jsonl")
        return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(p))}
    ref, blind = sc("ref"), sc("noref")
    items = []
    for t in pool:
        pid = t["problem_id"]
        if pid not in ref or pid not in blind:
            continue
        refn = norm(t["ref_answer"])
        oracle, match = [], []
        for s, o in zip(t["samples"], t["oracle"]):
            oracle.append(int(o))
            match.append(int(norm(extract_boxed(s) or s) == refn))
        if sum(oracle) == 0:
            continue                      # nothing correct to converge onto
        items.append(dict(pid=pid, oracle=oracle, match=match,
                          ref=ref[pid], blind=blind[pid]))
    return items


def train(item, reward_key):
    """REINFORCE over a softmax on the 64 stored candidates.

    Seeded per (item, reward) so a cell's result does not depend on the order in which
    cells are evaluated. With a single global seed the same cell moved by 0.04 between
    runs purely from call order; this makes every number below reproducible."""
    rng = random.Random(f"{SEED}|{item['pid']}|{reward_key}")
    n = len(item["oracle"])
    theta = [0.0] * n
    base = 0.0
    if reward_key == "oracle":
        R = [float(o) for o in item["oracle"]]
    else:
        R = [max(0.0, min(1.0, (s if s is not None else 0.0) / 10.0)) for s in item[reward_key]]
    for _ in range(NSTEP):
        m = max(theta)
        ex = [math.exp(t - m) for t in theta]
        Z = sum(ex)
        p = [e / Z for e in ex]
        r = rng.random()
        c, a = 0.0, n - 1
        for i, pi in enumerate(p):
            c += pi
            if r <= c:
                a = i
                break
        adv = R[a] - base
        base += 0.01 * (R[a] - base)
        for i in range(n):
            theta[i] += LR * adv * ((1.0 if i == a else 0.0) - p[i])
    m = max(theta)
    ex = [math.exp(t - m) for t in theta]
    Z = sum(ex)
    return [e / Z for e in ex]


def evaluate(items, reward_key):
    """Returns per-item arrays so differences can be paired and bootstrapped by item."""
    pv, pm, keys = [], {}, []
    for it in items:
        p = train(it, reward_key)
        valid = sum(p[i] for i in range(len(p)) if it["oracle"][i])
        vm = sum(p[i] for i in range(len(p)) if it["oracle"][i] and it["match"][i])
        pv.append(valid)
        # only items carrying BOTH a matching and a non-matching correct answer can show drift
        if valid > 1e-6 and any(it["oracle"][i] and it["match"][i] for i in range(len(p))) \
           and any(it["oracle"][i] and not it["match"][i] for i in range(len(p))):
            pm[it["pid"]] = vm / valid
            keys.append(it["pid"])
    return pv, pm, keys


def boot(vals, B=2000, tag=""):
    vals = list(vals)
    rng = random.Random(f"{SEED}|boot|{tag}|{len(vals)}")
    ms = []
    for _ in range(B):
        s = [rng.choice(vals) for _ in vals]
        ms.append(sum(s) / len(s))
    ms.sort()
    return sum(vals) / len(vals), ms[int(.025 * B)], ms[int(.975 * B)]


if __name__ == "__main__":
    CELLS = [("replication", "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl",
              "runs/bon_scores_repl", "Qwen__Qwen2.5-7B-Instruct", "a"),
             ("replication", "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl",
              "runs/bon_scores_repl", "microsoft__phi-4", "a")]
    out = {}
    print("Policy-gradient simulation over STORED judge scores. Not RL training; see header.\n")
    print(f"  {'pool':<12}{'judge':<26}{'reward':<12}{'P(valid)':>10}{'P(match|valid)':>16}{'items':>7}")
    for pool, pf, sd, judge, rep in CELLS:
        items = load(pf, sd, judge, rep)
        row = {}
        got = {}
        for rk in ("oracle", "blind", "ref"):
            pv, pm, keys = evaluate(items, rk)
            got[rk] = (pv, pm, keys)
            mv = sum(pv) / len(pv)
            mm = sum(pm.values()) / len(pm) if pm else float("nan")
            row[rk] = dict(p_valid=mv, p_match_given_valid=mm, n_items_scored=len(pm))
            print(f"  {pool:<12}{judge:<26}{rk:<12}{mv:>10.3f}{mm:>16.3f}{len(pm):>7}")
        shared = [k for k in got["oracle"][2] if k in got["ref"][1] and k in got["blind"][1]]
        for lbl, rk in (("ref", "ref"), ("blind", "blind")):
            diffs = [got[rk][1][k] - got["oracle"][1][k] for k in shared]
            m, lo, hi = boot(diffs, tag=f'{judge}|{lbl}')
            row[f"{lbl}_minus_oracle_match"] = dict(mean=m, ci=[lo, hi], n_items=len(shared))
            tag = "  (control)" if lbl == "blind" else ""
            print(f"  {'':<12}{'':<26}{'-> ' + lbl + '-oracle':<12}{'':>10}"
                  f"{m:>+10.3f} [{lo:+.3f},{hi:+.3f}]{tag}")
        print()
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "rl_simulation_results.json"), "w"), indent=1)
    print("  wrote papers/analysis/rl_simulation_results.json")
