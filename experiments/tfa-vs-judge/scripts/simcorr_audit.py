# Blind naturalness audit for the similarity-vs-correctness 2x2 (see
# build_simcorr_candidates.py / simcorr_analysis.py). Required by the registered design
# BEFORE any judging: an independent model audits candidate naturalness without seeing
# judge scores (none exist) and without knowing the hypothesis or which candidates are
# valid. The auditor is Claude via the local CLI session login (run_judge_cli.py pattern;
# ANTHROPIC_API_KEY stripped so no metered credits are used).
#
# PASS CRITERION, pinned before running (this file is committed before its first run):
#   (a) every candidate class (valid-near / valid-far / invalid-near / invalid-far,
#       identified only AFTER the audit by de-shuffling) has mean naturalness >= 3.0/5;
#   (b) the "reads as artificial or deliberately corrupted" flag rate for invalid-near
#       does not exceed the maximum flag rate of the other three classes by more than
#       25 percentage points. If (b) fails, the constructed errors are too detectable
#       and judging must not proceed until construction is revised.
# The auditor sees, per item: the problem and the four candidate solutions in a
# seed-shuffled order labeled S1..S4, and is asked only about writing naturalness.
#
# Run from experiments/tfa-vs-judge:  python3 scripts/simcorr_audit.py [--workers 8]
import argparse
import json
import os
import random
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--model", default="haiku")
ap.add_argument("--timeout", type=float, default=120)
args = ap.parse_args()

_ENV = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
rng = random.Random(20260827)
CLASSES = ["valid_near", "valid_far", "invalid_near", "invalid_far"]

PROMPT = """You are auditing short written math solutions for WRITING NATURALNESS only.
You are NOT grading correctness. For each solution below, rate how naturally it reads as
something a language model would write when solving the problem (1 = clearly artificial,
templated, or deliberately manipulated text; 5 = fully natural solution prose), and flag
any solution that reads as artificially constructed or deliberately corrupted.

Problem:
{problem}

{cands}

Respond with ONLY a JSON object, no other text, in this exact form:
{{"S1": {{"naturalness": <1-5>, "artificial": <true|false>}}, "S2": {{...}}, "S3": {{...}}, "S4": {{...}}}}"""


def audit_item(row):
    order = list(range(4))
    rng2 = random.Random(20260827 + hash(row["problem_id"]) % 100000)
    rng2.shuffle(order)
    cands = "\n\n".join(f"Solution S{i+1}:\n{row['samples'][order[i]]}" for i in range(4))
    p = PROMPT.format(problem=row["problem"], cands=cands)
    try:
        r = subprocess.run(["claude", "-p", "--model", args.model], input=p,
                           capture_output=True, text=True, timeout=args.timeout, env=_ENV)
        m = re.search(r"\{.*\}", r.stdout, re.S)
        j = json.loads(m.group(0))
        out = {}
        for i in range(4):
            cls = CLASSES[order[i]]
            v = j[f"S{i+1}"]
            out[cls] = dict(naturalness=int(v["naturalness"]), artificial=bool(v["artificial"]))
        return row["problem_id"], out
    except Exception as e:
        return row["problem_id"], dict(error=str(e)[:200])


rows = [json.loads(l) for l in open("runs/simcorr_tasks.jsonl")]
with ThreadPoolExecutor(args.workers) as ex:
    results = dict(ex.map(audit_item, rows))

ok = {pid: r for pid, r in results.items() if "error" not in r}
print(f"audited {len(ok)}/{len(rows)} items ({len(rows)-len(ok)} errors)")
summary = {}
for cls in CLASSES:
    nats = [r[cls]["naturalness"] for r in ok.values()]
    flags = [r[cls]["artificial"] for r in ok.values()]
    summary[cls] = dict(mean_naturalness=round(sum(nats) / len(nats), 2),
                        artificial_flag_rate=round(sum(flags) / len(flags), 3))
    print(f"{cls:14s} naturalness {summary[cls]['mean_naturalness']:.2f}  "
          f"artificial-flag rate {summary[cls]['artificial_flag_rate']:.1%}")

crit_a = all(s["mean_naturalness"] >= 3.0 for s in summary.values())
others = max(summary[c]["artificial_flag_rate"] for c in CLASSES if c != "invalid_near")
crit_b = summary["invalid_near"]["artificial_flag_rate"] - others <= 0.25
verdict = "PASS" if (crit_a and crit_b) else "FAIL"
print(f"criterion (a) all means >= 3.0: {crit_a}; "
      f"criterion (b) invalid_near flag excess {summary['invalid_near']['artificial_flag_rate']-others:+.3f} <= 0.25: {crit_b}")
print(f"AUDIT {verdict}: judging {'may proceed' if verdict == 'PASS' else 'MUST NOT proceed'}")
json.dump(dict(summary=summary, verdict=verdict, per_item=results),
          open("runs/simcorr_audit.json", "w"), indent=1)
