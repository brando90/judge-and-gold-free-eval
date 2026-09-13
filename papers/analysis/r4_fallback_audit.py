# POST HOC data-quality audit (registration_round4.md, Amendment 1). Counts, per legacy score file, the scores exactly
# equal to the 5.0 no-score fallback of bon_judge.py and the integer-valued scores. Run from experiments/tfa-vs-judge.
# Writes papers/analysis/r4_fallback_audit.json.
import glob
import json

files = sorted(glob.glob("runs/bon_scores_repl/*.jsonl") + glob.glob("runs/bon_scores_replrot/*.jsonl")
               + glob.glob("runs/bon_scores_kstrat/*.jsonl") + glob.glob("runs/bon_scores_mace/*.jsonl")
               + glob.glob("runs/bon_scores_synthk*/*.jsonl") + glob.glob("runs/bon_scores_refword/*.jsonl")
               + glob.glob("runs/bon_scores_refexpr/*.jsonl") + glob.glob("runs/bon_scores_refsolmask/*.jsonl")
               + glob.glob("runs/bon_scores_sep/*.jsonl") + glob.glob("runs/bon_scores_codeexem/*.jsonl")
               + glob.glob("runs/r2/frozen_math/*.jsonl") + glob.glob("runs/r3/scores/mace__*.jsonl"))
out = {}
for f in files:
    vals = [v for l in open(f) for v in json.loads(l).get("escore", []) if v is not None]
    if vals:
        n5 = sum(v == 5.0 for v in vals)
        out[f] = dict(n=len(vals), fallback_5=n5, share_5=round(n5 / len(vals), 4),
                      share_integer=round(sum(float(v).is_integer() for v in vals) / len(vals), 4))
json.dump(out, open("../../papers/analysis/r4_fallback_audit.json", "w"), indent=1)
flag = {f: v for f, v in out.items() if v["share_5"] > 0.01}
print(len(out), "files;", len(flag), "with more than 1% exact 5.0:")
for f, v in flag.items():
    print(f"  {f}: {100 * v['share_5']:.1f}% (integer {100 * v['share_integer']:.1f}%)")
