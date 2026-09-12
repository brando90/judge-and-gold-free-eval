# POST-HOC failure-mode profile of the DPO run-1 arms (reviewer-requested, external NeurIPS
# review: "do you observe qualitative failure modes... that distinguish [the ref arm] from
# standard reward model overoptimization?"). Not registered; computed from generations already
# on disk from the original run (runs/dpo_mv/eval_{base,ref,m1}_{train,heldout}.jsonl), which
# stores 8 samples/item and per-sample oracle labels. No new generation or judging.
import json
import statistics as st
import collections


def load(f):
    return [json.loads(l) for l in open(f)]


def samples_of(r):
    s = r["samples"]
    return json.loads(s) if isinstance(s, str) else s


def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


def repetition_rate(t, n=4):
    words = t.split()
    if len(words) < n + 1:
        return 0.0
    grams = [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]
    c = collections.Counter(grams)
    return 1 - len(c) / len(grams) if grams else 0.0


out = {}
for split in ("train", "heldout"):
    for arm in ("base", "ref", "m1"):
        rows = load(f"runs/dpo_mv/eval_{arm}_{split}.jsonl")
        lens, boxed_ok, reps = [], [], []
        n_valid = n_tot = 0
        unboxed_valid = unboxed_invalid = 0
        for r in rows:
            samps = samples_of(r)
            for s, o in zip(samps, r["oracle"]):
                lens.append(len(s))
                b = boxed(s)
                boxed_ok.append(b is not None)
                reps.append(repetition_rate(s))
                if b is None:
                    (unboxed_valid if o else unboxed_invalid)
                    if o:
                        unboxed_valid += 1
                    else:
                        unboxed_invalid += 1
                n_tot += 1
                n_valid += o
        out[f"{arm}_{split}"] = dict(
            n_items=len(rows), mean_len=round(st.mean(lens), 0), boxed_rate=round(st.mean(boxed_ok), 3),
            mean_4gram_repeat=round(st.mean(reps), 3), accuracy=round(n_valid / n_tot, 3),
            unboxed_but_valid=unboxed_valid, unboxed_and_invalid=unboxed_invalid)

json.dump(out, open("dpo_failure_profile.json", "w"), indent=1)
for k, v in out.items():
    print(k, v)
