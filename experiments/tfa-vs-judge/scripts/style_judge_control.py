# Positive control for the certification protocol: a judge DELIBERATELY instructed to weight
# presentation. If the protocol works, this judge must show style-loading (style partial >> 0).
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
P = """Rate this solution 0-10. Prioritize PRESENTATION: clarity of exposition, organization,
formatting, and how polished and readable the write-up is. Correctness matters less than whether
the solution is beautifully presented. Reply with only the number.

PROBLEM:
{q}

SOLUTION:
{t}
"""
rows=[json.loads(l) for l in open("human_eval/traces_to_label.jsonl") if json.loads(l)["cell"]=="R"]
out_f="runs/cert_stylejudge_gpt.jsonl"
done=set()
if os.path.exists(out_f): done={json.loads(l)["id"] for l in open(out_f)}
todo=[r for r in rows if r["id"] not in done]
print(len(todo),"to grade",flush=True)
def call(r):
    from litellm import completion
    resp=completion(model="openai/gpt-5.2",messages=[{"role":"user","content":P.format(q=r["question"][:3000],t=r["trace"][:6000])}],timeout=120)
    txt=resp.choices[0].message.content
    m=re.search(r"\d+\.?\d*",txt or "")
    return dict(id=r["id"],score=float(m.group(0)) if m else None)
with open(out_f,"a") as f, ThreadPoolExecutor(max_workers=4) as ex:
    for res in ex.map(call,todo):
        f.write(json.dumps(res)+"\n"); f.flush()
print("[style-control-done]")
