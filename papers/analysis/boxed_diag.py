# Diagnostic: is the negative boxed-compliance / inflation correlation an artifact
# (noisier oracle attenuates true_gain) or a mechanism (reference string is a bigger
# edge when the answer is not cleanly boxed)? Decompose the delta into its parts.
import json, re, sys
import numpy as np
sys.path.insert(0, "scripts")
_src = open("scripts/bon_analysis.py").read().split("if __name__")[0]
ns = {}; exec(compile(_src, "bon_analysis", "exec"), ns)
def boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0: return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0); j += 1
    return t[i + 7:j - 1]
rpool = {}
for l in open("runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl"):
    r = json.loads(l)
    if "oracle" in r: rpool[r["problem_id"]] = r
inband = [p for p in rpool if 0.2 <= float(np.mean(rpool[p]["oracle"])) <= 0.8]
JUD = ["Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"]
def rsc(j,c,rep): return {json.loads(l)["problem_id"]: json.loads(l)["escore"]
    for l in open(f"runs/bon_scores_repl/synthk__{j}__{c}_{rep}.jsonl")}
parts = {}
for j in JUD:
    ra,rb,na,nb = rsc(j,"ref","a"),rsc(j,"ref","b"),rsc(j,"noref","a"),rsc(j,"noref","b")
    for pid in inband:
        it = rpool[pid]
        if pid not in ra: continue
        cr = ns["per_item_curves"](it,ra[pid],rb[pid]); cn = ns["per_item_curves"](it,na[pid],nb[pid])
        parts.setdefault(pid,[]).append(dict(
            jg_ref=cr[64]["judge_gain"], tg_ref=cr[64]["true_gain"],
            jg_bl=cn[64]["judge_gain"], tg_bl=cn[64]["true_gain"]))
bc = {p: float(np.mean([boxed(s) is not None for s in rpool[p]["samples"]])) for p in inband}
med = float(np.median([bc[p] for p in parts]))
for name, sel in (("clean (>=median)", lambda p: bc[p] >= med), ("messy (<median)", lambda p: bc[p] < med)):
    ps = [p for p in parts if sel(p)]
    def m(k): return float(np.mean([np.mean([d[k] for d in parts[p]]) for p in ps]))
    base = float(np.mean([np.mean(rpool[p]["oracle"]) for p in ps]))
    print(f"{name:18s} n={len(ps):3d}  base_acc={base:.3f}  "
          f"judge_gain ref={m('jg_ref'):+.3f} blind={m('jg_bl'):+.3f} (d={m('jg_ref')-m('jg_bl'):+.3f}) | "
          f"true_gain ref={m('tg_ref'):+.3f} blind={m('tg_bl'):+.3f} (d={m('tg_ref')-m('tg_bl'):+.3f})")
