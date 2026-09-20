# POST HOC (no registration weight): the KL-regularized optimum, computed in closed form.
#
# WHY THIS AND NOT A TRAINING RUN. RLHF maximises E[r] - beta * KL(pi || pi_base). The optimum is
# analytic:
#
#     pi*(y)  proportional to  pi_base(y) * exp(r(y) / beta)
#
# a tilt of the base policy toward high reward. Both terms are already measured: pi_base from how
# often each distinct answer appears among the 64 stored samples, r from the stored judge scores. So
# the entire optimisation path -- beta = infinity (no optimisation) down to beta -> 0 (argmax) -- can
# be traced exactly, with no training, no seeds, and no gradient noise. This supersedes the REINFORCE
# simulation in rl_simulation.py, which was a noisy approximation of this same object.
#
# WHAT WE PLOT. At each KL budget: the proxy reward (mean judge score), the true reward (oracle
# accuracy), and -- the quantity this paper cares about and which the reward-overoptimisation
# literature does not track -- the share of correct probability mass sitting on the ONE answer the
# judge was shown. Gao, Schulman and Hilton (2022) show proxy reward climbing while true reward peaks
# and falls. The question here is where the reference collapse sits relative to that peak: if the
# answer distribution narrows onto the reference BEFORE accuracy degrades, a team monitoring accuracy
# sees nothing during the phase when the damage is done.
#
# CROSS-CHECK. Best-of-n has an analytic KL of log(n) - (n-1)/n nats, so the n = 4, 16, 64 cells of
# bon_reference_selection.py sit at about 0.64, 1.71 and 3.17 nats. The tilt curve and the BoN points
# should agree where they overlap; disagreement would mean one of the two is not measuring what it
# claims.
#
# LIMIT, unchanged from the rest of this line of work: the policy can only redistribute mass over
# answers that were sampled. Real RL explores. This sharpens the mechanism; it does not demonstrate
# harm to a trained policy.
import json, math, os, re

E = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "experiments", "tfa-vs-judge")
BETAS = [None, 8.0, 4.0, 2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]   # None = base policy


def norm(a):
    return re.sub(r"[\s\.\,\!\'\"\$]+", "", str(a).strip().casefold()) or None


def mnorm(a):
    return re.sub(r"[^a-z0-9]+", "", (a or "").strip().casefold())


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def matches(sample, ref_answer, domain):
    if domain == "mace":
        a, rn = mnorm(boxed(sample) or sample[-200:]), mnorm(ref_answer)
        return int(a == rn or (len(rn) > 3 and rn in a))
    return int(norm(boxed(sample) or sample) == norm(ref_answer))


def load(pool_f, scores_dir, judge, rep, domain):
    pool = [json.loads(l) for l in open(os.path.join(E, pool_f))]
    def sc(cond):
        p = os.path.join(E, scores_dir, f"{domain}__{judge}__{cond}_{rep}.jsonl")
        return {r["problem_id"]: r["escore"] for r in (json.loads(l) for l in open(p))}
    ref = sc("ref")
    items = []
    for t in pool:
        pid = t["problem_id"]
        if pid not in ref:
            continue
        if domain == "mace" and (t.get("k") or 0) < 2:
            continue
        oracle = [int(o) for o in t["oracle"]]
        match = [matches(s, t["ref_answer"], domain) for s in t["samples"]]
        if not (any(o and m for o, m in zip(oracle, match)) and
                any(o and not m for o, m in zip(oracle, match))):
            continue
        items.append(dict(pid=pid, oracle=oracle, match=match, r=ref[pid]))
    return items


def tilt(item, beta):
    """pi*(y) proportional to pi_base(y) * exp(r(y)/beta), over the 64 sampled candidates.

    pi_base is uniform over the samples as drawn, so repeated answers carry their own
    multiplicity -- that is what makes this the base POLICY and not a uniform prior over
    distinct answers. Returns (probs, KL(pi* || pi_base)) in nats."""
    n = len(item["oracle"])
    r = [(s if s is not None else 0.0) for s in item["r"]]
    if beta is None:
        p = [1.0 / n] * n
        return p, 0.0
    m = max(r)
    w = [math.exp((ri - m) / beta) for ri in r]
    Z = sum(w)
    p = [wi / Z for wi in w]
    kl = 0.0
    for pi in p:
        if pi > 0:
            kl += pi * math.log(pi * n)      # log(pi / (1/n))
    return p, kl


if __name__ == "__main__":
    REPL = "runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"
    MACE = "runs/bon/bon_mace__meta-llama__Llama-3.1-8B-Instruct.jsonl"
    CELLS = [("arithmetic", REPL, "runs/bon_scores_repl", "Qwen__Qwen2.5-7B-Instruct", "a", "synthk"),
             ("arithmetic", REPL, "runs/bon_scores_repl", "microsoft__phi-4", "a", "synthk"),
             ("MACE", MACE, "runs/bon_scores_mace", "Qwen__Qwen2.5-7B-Instruct", "a", "mace"),
             ("MACE", MACE, "runs/bon_scores_mace", "microsoft__phi-4", "a", "mace"),
             ("MACE", MACE, "runs/bon_scores_mace", "anthropic__claude-sonnet-5", "a", "mace")]
    out = {}
    print("KL-regularized optimum in closed form. pi* ∝ pi_base * exp(r/beta). No training.\n")
    for pool, pf, sd, judge, rep, dom in CELLS:
        items = load(pf, sd, judge, rep, dom)
        print(f"  {pool} / {judge}   ({len(items)} items)")
        print(f"    {'beta':>8}{'KL (nats)':>11}{'proxy (judge)':>15}{'true (accuracy)':>17}{'P(ref|correct)':>16}")
        rows = []
        for b in BETAS:
            kls, proxies, accs, mrs = [], [], [], []
            for it in items:
                p, kl = tilt(it, b)
                kls.append(kl)
                proxies.append(sum(pi * (s if s is not None else 0.0) for pi, s in zip(p, it["r"])))
                acc = sum(pi for pi, o in zip(p, it["oracle"]) if o)
                accs.append(acc)
                if acc > 1e-9:
                    mrs.append(sum(pi for pi, o, m in zip(p, it["oracle"], it["match"]) if o and m) / acc)
            row = dict(beta=b, kl=sum(kls) / len(kls), proxy=sum(proxies) / len(proxies),
                       accuracy=sum(accs) / len(accs), p_ref_given_correct=sum(mrs) / len(mrs))
            rows.append(row)
            bl = "base" if b is None else f"{b:g}"
            print(f"    {bl:>8}{row['kl']:>11.2f}{row['proxy']:>15.2f}{row['accuracy']:>17.3f}"
                  f"{row['p_ref_given_correct']:>16.3f}")
        # where does the true reward peak, and where has the reference collapse already happened?
        pk = max(rows, key=lambda r: r["accuracy"])
        base, tightest = rows[0], rows[-1]
        print(f"    peak accuracy {pk['accuracy']:.3f} at KL {pk['kl']:.2f}; "
              f"P(ref|correct) there {pk['p_ref_given_correct']:.3f} "
              f"(base {base['p_ref_given_correct']:.3f})")
        out[f"{pool}|{judge}|{rep}"] = dict(rows=rows, peak_kl=pk["kl"],
                                            peak_accuracy=pk["accuracy"],
                                            p_ref_at_peak=pk["p_ref_given_correct"],
                                            p_ref_at_base=base["p_ref_given_correct"])
        print()
    # best-of-n KL equivalence, for the cross-check against bon_reference_selection.py
    print("  best-of-n KL equivalence: KL(n) = log n - (n-1)/n")
    for n in (2, 4, 16, 64):
        print(f"    n={n:>3}  KL = {math.log(n) - (n - 1) / n:.2f} nats")
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "kl_tilt_results.json"), "w"), indent=1)
    print("\n  wrote papers/analysis/kl_tilt_results.json")
