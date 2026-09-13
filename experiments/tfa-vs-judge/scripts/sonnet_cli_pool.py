# R8-A (papers/D-iclr/registration_round8.md): Claude Sonnet 5 through the claude CLI (subscription login), score-only
# (rubric a, thinking off), blind and referenced, on candidate subsamples that include wrong answers. Same interface
# settings as sonnet_cli_mace.py (R5-A FAST). Calls are ordered task by task with both conditions for each candidate,
# so an interrupted run leaves complete, paired tasks. Resumable. Run from experiments/tfa-vs-judge.
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC_TIES

ap = argparse.ArgumentParser()
ap.add_argument("--pool", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--workers", type=int, default=4)
args = ap.parse_args()
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
outf = os.path.abspath(args.out)
SETTINGS = json.dumps({"alwaysThinkingEnabled": False})
ENV = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
WORKDIR = tempfile.mkdtemp(prefix="sonnet_cli_pool_")


def parse(text):
    m = re.findall(r"\b(10|[0-9])\b", text)
    return float(m[-1]) if m else None


def one(job):
    t, j, cond = job
    user = f"Problem:\n{t['question']}\n\n"
    if cond == "ref":
        user += f"Reference answer (trusted):\n{t['ref']}\n\n"
    user += f"Candidate solution:\n{t['samples'][j]}\n\nScore:"
    cmd = ["claude", "-p", "--model", "claude-sonnet-5", "--system-prompt", RUBRIC_TIES[(cond, "a")], "--tools", "",
           "--no-session-persistence", "--strict-mcp-config", "--setting-sources", "", "--output-format", "json",
           "--settings", SETTINGS]
    row = dict(problem_id=t["problem_id"], idx=t["idx"][j], cond=cond)
    for _ in range(3):
        try:
            p = subprocess.run(cmd, input=user, capture_output=True, text=True, env=ENV, cwd=WORKDIR, timeout=600)
            d = json.loads(p.stdout)
            if d.get("is_error"):
                raise RuntimeError(str(d.get("result"))[:200])
            text = d.get("result") or ""
            u = d.get("usage") or {}
            row.update(score=parse(text), output_tokens=u.get("output_tokens"), tail=text[-200:])
            row.pop("error", None)
            return row
        except Exception as e:  # noqa: BLE001 - record and retry
            row.update(score=None, error=f"{type(e).__name__}: {str(e)[:200]}")
    return row


done = set()
if os.path.exists(outf):
    for l in open(outf):
        r = json.loads(l)
        if not r.get("error"):
            done.add((r["problem_id"], r["idx"], r["cond"]))
pool = [json.loads(l) for l in open(args.pool)]
jobs = [(t, j, c) for t in pool for j in range(len(t["samples"])) for c in ("noref", "ref")
        if (t["problem_id"], t["idx"][j], c) not in done]
print(f"[sonnet-cli-pool {os.path.basename(args.pool)}] {len(jobs)} calls", flush=True)
lock = threading.Lock()
n_bad = 0
with open(outf, "a") as f, ThreadPoolExecutor(args.workers) as ex:
    for i, row in enumerate(ex.map(one, jobs)):
        n_bad += row.get("score") is None
        with lock:
            f.write(json.dumps(row) + "\n")
            f.flush()
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(jobs)} unparseable/errors {n_bad}", flush=True)
        if n_bad >= 40 and n_bad > 0.5 * (i + 1):
            print("[sonnet-cli-pool] stopping: most calls fail (usage limit?)", flush=True)
            break
print(f"[sonnet-cli-pool done] {outf} unparseable/errors={n_bad}", flush=True)
