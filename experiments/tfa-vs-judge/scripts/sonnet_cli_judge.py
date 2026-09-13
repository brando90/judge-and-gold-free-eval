# R3-B (papers/D-iclr/registration_round3b.md): Claude Sonnet 5 through the claude CLI (subscription login),
# three arms: fast (integer-only rubric, thinking off), visible (think-it-through rubric, thinking off),
# think (think-it-through rubric, thinking on). Resumable. Run from experiments/tfa-vs-judge.
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
ap.add_argument("--arm", choices=["fast", "visible", "think"], required=True)
ap.add_argument("--cond", choices=["ref", "refrot"], required=True)
ap.add_argument("--pool", default="runs/r3/sonnet_rot.jsonl")
ap.add_argument("--out", default="runs/r3/sonnet")
ap.add_argument("--workers", type=int, default=6)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
outf = os.path.abspath(f"{args.out}/{args.arm}__{args.cond}.jsonl")

TAIL = ("Think it through, then end your reply with a final line of the form 'Score: N', "
        "where N is an integer from 0 to 10.")
if args.arm == "fast":
    SYSTEM = RUBRIC_TIES[("ref", "a")]
else:
    SYSTEM = re.sub(r"\s*Respond with only the integer score\.\s*$", "", RUBRIC_TIES[("ref", "a")]) + " " + TAIL
SETTINGS = json.dumps({"alwaysThinkingEnabled": args.arm == "think"})
ENV = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
WORKDIR = tempfile.mkdtemp(prefix="sonnet_cli_")


def parse(text):
    if args.arm == "fast":
        m = re.findall(r"\b(10|[0-9])\b", text)
        return float(m[-1]) if m else None
    m = re.findall(r"Score:\s*\**\s*(\d+(?:\.\d+)?)", text)
    if not m:
        return None
    v = float(m[-1])
    return v if 0 <= v <= 10 else None


def one(job):
    t, j = job
    ref = t["ref_rot"] if args.cond == "refrot" else t["ref_orig"]
    user = f"Problem:\n{t['question']}\n\nReference answer (trusted):\n{ref}\n\nCandidate solution:\n{t['samples'][j]}"
    if args.arm == "fast":
        user += "\n\nScore:"
    cmd = ["claude", "-p", "--model", "claude-sonnet-5", "--system-prompt", SYSTEM, "--tools", "",
           "--no-session-persistence", "--strict-mcp-config", "--setting-sources", "", "--output-format", "json",
           "--settings", SETTINGS]
    row = dict(problem_id=t["problem_id"], idx=t["idx"][j], cls=t["cls"][j])
    for attempt in range(3):
        try:
            p = subprocess.run(cmd, input=user, capture_output=True, text=True, env=ENV, cwd=WORKDIR, timeout=600)
            d = json.loads(p.stdout)
            if d.get("is_error"):
                raise RuntimeError(str(d.get("result"))[:200])
            text = d.get("result") or ""
            u = d.get("usage") or {}
            row.update(score=parse(text), output_tokens=u.get("output_tokens"),
                       thinking_tokens=(u.get("output_tokens_details") or {}).get("thinking_tokens"),
                       input_tokens=u.get("input_tokens"), cache_tokens=u.get("cache_creation_input_tokens"),
                       tail=text[-400:])
            return row
        except Exception as e:  # noqa: BLE001 - record and retry
            row.update(score=None, error=f"{type(e).__name__}: {str(e)[:200]}")
    return row


done = set()
if os.path.exists(outf):
    for l in open(outf):
        r = json.loads(l)
        if not r.get("error"):
            done.add((r["problem_id"], r["idx"]))
pool = [json.loads(l) for l in open(args.pool)]
jobs = [(t, j) for t in pool for j in range(len(t["samples"])) if (t["problem_id"], t["idx"][j]) not in done]
print(f"[sonnet-cli {args.arm}/{args.cond}] {len(jobs)} calls", flush=True)
lock = threading.Lock()
n_bad = 0
with open(outf, "a") as f, ThreadPoolExecutor(args.workers) as ex:
    for i, row in enumerate(ex.map(one, jobs)):
        n_bad += row.get("score") is None
        with lock:
            f.write(json.dumps(row) + "\n")
            f.flush()
        if (i + 1) % 30 == 0:
            print(f"  {i + 1}/{len(jobs)} unparseable/errors {n_bad}", flush=True)
print(f"[sonnet-cli done] {outf} unparseable/errors={n_bad}", flush=True)
