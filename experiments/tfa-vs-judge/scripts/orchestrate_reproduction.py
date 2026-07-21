#!/usr/bin/env python
# Resumable orchestrator for the all-family reproduction. Fills missing (model, dataset) cells for the
# family ladders across the 6 datasets, boxed accuracy only (no judge). Runs 3 concurrent workers, one per
# GPU (1,2,3), each pulling the next job from a shared queue. Idempotent (skips any cell already present in
# any runs/* dir) and fault-tolerant (logs and continues past a failed cell). Launch under nohup.
import os, sys, glob, subprocess, threading, queue, time, datetime

ROOT = os.path.expanduser("~/tfa-vs-judge")
os.chdir(ROOT)
TOK = "/dfs/scratch0/srivatsavad/jfe_raw/tokens"
os.makedirs("runs/all", exist_ok=True); os.makedirs("logs", exist_ok=True); os.makedirs(TOK, exist_ok=True)
GPUS = [1, 2, 3]

# Family ladders (clean instruct + math-specialized). Reasoning models handled separately (long-gen).
MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.3", "mistralai/Ministral-8B-Instruct-2410", "mistralai/Mistral-Small-Instruct-2409",
    "microsoft/Phi-3.5-mini-instruct", "microsoft/Phi-3-medium-4k-instruct", "microsoft/phi-4",
    "allenai/OLMo-2-1124-7B-Instruct", "allenai/OLMo-2-1124-13B-Instruct", "allenai/OLMo-2-0325-32B-Instruct",
    "Qwen/Qwen2.5-Math-7B-Instruct", "deepseek-ai/deepseek-math-7b-instruct", "mistralai/Mathstral-7B-v0.1",
]
DATASETS = {"math500": 500, "math-full": 600, "gsm8k": 500, "gsm8k-platinum": 500,
            "putnam-axiom": 236, "putnam-axiom-var": 265}

def safe(m): return m.replace("/", "__")

def done(model, dataset):
    # present in ANY run dir, judged or not
    pat = f"runs/*/{dataset}__{safe(model)}*.jsonl"
    return len(glob.glob(pat)) > 0

def log(msg):
    line = f"[{datetime.datetime.now():%m-%d %H:%M:%S}] {msg}"
    with open("logs/orchestrate.log", "a") as f: f.write(line + "\n")
    print(line, flush=True)

jobs = queue.Queue()
skipped = 0
for m in MODELS:
    for d, lim in DATASETS.items():
        if done(m, d):
            skipped += 1
        else:
            jobs.put((m, d, lim))
log(f"queued {jobs.qsize()} cells, skipped {skipped} already-present, {len(GPUS)} workers")

def worker(gpu):
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu), PYTHONPATH=".",
               HF_HOME="/lfs/skampere1/0/srivatsavad/.cache/huggingface")
    while True:
        try:
            m, d, lim = jobs.get_nowait()
        except queue.Empty:
            log(f"gpu{gpu}: queue empty, worker exiting"); return
        lg = f"logs/all_{safe(m)}_{d}.log"
        log(f"gpu{gpu}: START {m} {d} (limit {lim})")
        t0 = time.time()
        cmd = [".venv/bin/python", "scripts/run_all.py", "--model", m, "--dataset", d,
               "--limit", str(lim), "--no-judge", "--save-tokens", TOK, "--out", "runs/all"]
        try:
            with open(lg, "w") as f:
                rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT)
        except Exception as e:
            rc = -99; log(f"gpu{gpu}: EXC {m} {d}: {e}")
        ok = "OK" if (rc == 0 and done(m, d)) else f"FAIL(rc={rc})"
        log(f"gpu{gpu}: END   {m} {d} {ok} in {int(time.time()-t0)}s")
        jobs.task_done()

threads = [threading.Thread(target=worker, args=(g,), daemon=False) for g in GPUS]
for t in threads: t.start()
for t in threads: t.join()
log("ORCHESTRATOR DONE")
