#!/usr/bin/env python3
# Frontier API harness for the corruption panel (Paper A, Registration 7). Committed before any
# score exists. Scoring mirrors scripts/bon_judge_gpt.py, the harness behind the published GPT-5.2
# arms: system rubric + user message, max_completion_tokens=4, logprobs with top_logprobs=5,
# escore = expected value over score tokens when captured mass >= 0.25, else the parsed integer,
# else 5.0. Unlike that harness, every score records WHICH path produced it (lp / parsed /
# default / missing), so a silent fallback is measurable and gated (FALLBACK_MAX).
#
# Phase ordering is enforced here, not only in the registration:
#   --input calib : allowed once the registration is committed
#   --input audit : refuses unless the frozen manipulation result exists and admits the cell
#   batch-submit  : refuses unless the frozen audit verdicts exist and include the cell
#
# Run from experiments/tfa-vs-judge with OPENAI_API_KEY in the environment:
#   python3 scripts/corruption_judge_api.py --mode probe
#   python3 scripts/corruption_judge_api.py --mode sync --input calib --cell g41_style
#   python3 scripts/corruption_judge_api.py --mode sync --input audit --cell g41_style
#   python3 scripts/corruption_judge_api.py --mode batch-submit  --cell g41_style --rep a
#   python3 scripts/corruption_judge_api.py --mode batch-collect --cell g41_style --rep a
import argparse
import json
import math
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corruption_specs import (BATCH_DISCOUNT, CELLS, JUDGES, cell_judge,  # noqa: E402
                              cell_treatment, system_prompt)

ap = argparse.ArgumentParser()
ap.add_argument("--mode", choices=["probe", "sync", "batch-submit", "batch-collect"], required=True)
ap.add_argument("--cell", choices=CELLS)
ap.add_argument("--input", choices=["calib", "audit"])
ap.add_argument("--rep", choices=["a", "b"], default="a")
ap.add_argument("--cap", type=float, default=40.0, help="hard stop on cumulative ledger spend, USD")
ap.add_argument("--workers", type=int, default=16)
args = ap.parse_args()

if not os.environ.get("OPENAI_API_KEY"):
    raise SystemExit("OPENAI_API_KEY not set (set -a; source <path>/.env; set +a)")
from openai import OpenAI  # noqa: E402

client = OpenAI(max_retries=0, timeout=120)
OUT = "runs/corruption"
BON_OUT = "runs/bon_scores_corruption"
MANIP = "../../papers/analysis/corruption_manipulation.json"
VERD = "../../papers/analysis/corruption_verdicts.json"
os.makedirs(OUT, exist_ok=True)
SPEND_F = f"{OUT}/spend.json"
_lock = threading.Lock()
_ledger = json.load(open(SPEND_F)) if os.path.exists(SPEND_F) else {"usd": 0.0, "by_model": {}}
_resolved = set()
SCORE_TOK = re.compile(r"\s?(\d|10)")


def charge(judge, tin, tout, discount=1.0):
    usd = (tin * judge["price_in"] + tout * judge["price_out"]) / 1e6 * discount
    with _lock:
        _ledger["usd"] += usd
        _ledger["by_model"][judge["model"]] = _ledger["by_model"].get(judge["model"], 0.0) + usd
        json.dump(_ledger, open(SPEND_F, "w"), indent=1)


def messages(sysm, question, reference, text):
    user = (f"Problem:\n{question}\n\nReference solution (trusted):\n{reference}\n\n"
            f"Candidate solution:\n{text[:6000]}\n\nScore:")
    return [{"role": "system", "content": sysm}, {"role": "user", "content": user}]


def body(judge, msgs):
    b = dict(model=judge["model"], messages=msgs, max_completion_tokens=4,
             logprobs=True, top_logprobs=5)
    if judge["reasoning_none"]:
        b["reasoning_effort"] = "none"
    return b


def escore_from(top, content):
    num = den = 0.0
    for t in top or []:
        tok = t["token"] if isinstance(t, dict) else t.token
        lp = t["logprob"] if isinstance(t, dict) else t.logprob
        m = SCORE_TOK.fullmatch(tok)
        if m:
            p = math.exp(lp)
            num += p * int(m.group(1))
            den += p
    if den >= 0.25:
        return num / den, "lp"
    m = re.search(r"\d+", content or "")
    if m:
        return float(min(int(m.group()), 10)), "parsed"
    return 5.0, "default"


def call(judge, msgs):
    delay = 2.0
    for attempt in range(7):
        with _lock:
            if _ledger["usd"] >= args.cap:
                raise SystemExit(f"HARD STOP: ledger ${_ledger['usd']:.2f} >= cap ${args.cap:.2f}")
        try:
            r = client.chat.completions.create(**body(judge, msgs))
            _resolved.add(r.model)
            charge(judge, r.usage.prompt_tokens, r.usage.completion_tokens)
            ch = r.choices[0]
            top = ch.logprobs.content[0].top_logprobs if (ch.logprobs and ch.logprobs.content) else []
            return escore_from(top, ch.message.content)
        except SystemExit:
            raise
        except Exception as e:  # rate limits, timeouts, transient 5xx
            if attempt == 6:
                raise
            print(f"[retry {attempt + 1}] {type(e).__name__}: {str(e)[:120]}", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 60)


def write_meta(path, extra):
    json.dump(dict(models_resolved=sorted(_resolved), ledger_usd=round(_ledger["usd"], 4), **extra),
              open(path, "w"), indent=1)


def run_sync(cell, rows, key_fn, row_fn, outf):
    judge = cell_judge(cell)
    sysm = system_prompt(cell_treatment(cell), "a")
    done = set()
    if os.path.exists(outf):
        done = {key_fn(json.loads(l)) for l in open(outf)}
    todo = [r for r in rows if key_fn(r) not in done]
    print(f"[sync] {cell} {args.input}: {len(todo)} to score ({len(done)} done), "
          f"ledger ${_ledger['usd']:.2f} cap ${args.cap:.2f}", flush=True)

    def one(r):
        return row_fn(r, *call(judge, messages(sysm, *r["_msg"])))

    counts = {}
    with open(outf, "a") as f, ThreadPoolExecutor(args.workers) as ex:
        for k, res in enumerate(ex.map(one, todo), 1):
            f.write(json.dumps(res) + "\n")
            f.flush()
            if k % 100 == 0:
                print(f"[sync] {k}/{len(todo)} ledger ${_ledger['usd']:.2f}", flush=True)
    for l in open(outf):
        src = json.loads(l)["src"]
        counts[src] = counts.get(src, 0) + 1
    write_meta(outf.replace(".jsonl", ".meta.json"),
               dict(cell=cell, input=args.input, rep="a", model_requested=judge["model"],
                    src_counts=counts))
    print(f"[sync done] {outf} src {counts} ledger ${_ledger['usd']:.2f}", flush=True)


def inband_pool():
    pool = [json.loads(l) for l in open("runs/bon/bon_math__Qwen__Qwen2.5-7B-Instruct.jsonl")]
    tasks = {json.loads(l)["problem_id"]: json.loads(l) for l in open("runs/bon_math_tasks.jsonl")}
    pool = [r for r in pool if 0.2 <= sum(r["oracle"]) / len(r["oracle"]) <= 0.8]
    for r in pool:
        r["problem"], r["solution"] = tasks[r["problem_id"]]["problem"], tasks[r["problem_id"]]["solution"]
    return pool


if args.mode == "probe":
    toy = messages(system_prompt("honest", "a"), "What is 2+2?", "2+2=4, so the answer is 4.",
                   "Adding, 2+2=4. The answer is $\\boxed{4}$.")
    for j in JUDGES:
        s, src = call(j, toy)
        print(f"[probe] {j['model']}: escore {s:.3f} via {src}")
    print(f"[probe] resolved models {sorted(_resolved)} ledger ${_ledger['usd']:.4f}")

elif args.mode == "sync":
    if not (args.cell and args.input):
        raise SystemExit("--cell and --input are required for sync")
    if args.input == "calib":
        rows = [json.loads(l) for l in open("runs/corruption_calib.jsonl")]
        for r in rows:
            r["_msg"] = (r["question"], r["solution"], r["text"])
        run_sync(args.cell, rows, lambda r: (r["cid"], r["variant"]),
                 lambda r, s, src: dict(cid=r["cid"], variant=r["variant"], correct=r["correct"],
                                        escore=s, src=src),
                 f"{OUT}/calib__{args.cell}.jsonl")
    else:
        if not os.path.exists(MANIP):
            raise SystemExit("frozen manipulation result missing: run and commit corruption_manipulation.py first")
        m = json.load(open(MANIP))
        if m.get("stopped"):
            raise SystemExit("manipulation stopping rule engaged: there is no audit phase")
        if args.cell not in m["entering_cells"]:
            raise SystemExit(f"{args.cell} did not enter the panel")
        rows = [json.loads(l) for l in open("human_eval/traces_to_label.jsonl")]
        for r in rows:
            r["_msg"] = (r["question"], r["gold_solution"], r["trace"])
        run_sync(args.cell, rows, lambda r: r.get("task_id", r.get("id")),
                 lambda r, s, src: dict(task_id=r["id"], score=s, src=src),
                 f"{OUT}/cert__{args.cell}.jsonl")

elif args.mode == "batch-submit":
    if not args.cell:
        raise SystemExit("--cell is required")
    if not os.path.exists(VERD):
        raise SystemExit("frozen audit verdicts missing: run and commit corruption_verdicts.py first")
    v = json.load(open(VERD))
    if v.get("stopped") or args.cell not in v["configs"]:
        raise SystemExit(f"{args.cell} has no frozen verdict")
    side = f"{OUT}/bon_req__{args.cell}_{args.rep}.batch.json"
    if os.path.exists(side):
        raise SystemExit(f"already submitted: {side}")
    judge = cell_judge(args.cell)
    sysm = system_prompt(cell_treatment(args.cell), args.rep)
    pool = inband_pool()
    req = f"{OUT}/bon_req__{args.cell}_{args.rep}.jsonl"
    n = 0
    with open(req, "w") as f:
        for i, r in enumerate(pool):
            for j, s in enumerate(r["samples"]):
                f.write(json.dumps(dict(custom_id=f"{args.cell}-{args.rep}-{i:03d}-{j:02d}",
                                        method="POST", url="/v1/chat/completions",
                                        body=body(judge, messages(sysm, r["problem"], r["solution"], s)))) + "\n")
                n += 1
    up = client.files.create(file=open(req, "rb"), purpose="batch")
    b = client.batches.create(input_file_id=up.id, endpoint="/v1/chat/completions",
                              completion_window="24h",
                              metadata=dict(cell=args.cell, rep=args.rep, registration="paperA-R7"))
    json.dump(dict(batch_id=b.id, input_file_id=up.id, n=n, model=judge["model"],
                   problem_ids=[r["problem_id"] for r in pool], n_samples=len(pool[0]["samples"]),
                   submitted=time.strftime("%Y-%m-%dT%H:%M:%S")), open(side, "w"), indent=1)
    print(f"[batch-submit] {args.cell} rep {args.rep}: {n} requests, batch {b.id}")

else:  # batch-collect
    side_f = f"{OUT}/bon_req__{args.cell}_{args.rep}.batch.json"
    side = json.load(open(side_f))
    judge = cell_judge(args.cell)
    b = client.batches.retrieve(side["batch_id"])
    print(f"[batch-collect] {args.cell} rep {args.rep}: status {b.status} counts {b.request_counts}")
    if b.status != "completed":
        raise SystemExit(0)
    got, counts = {}, {}
    for line in client.files.content(b.output_file_id).text.splitlines():
        o = json.loads(line)
        _, _, i, j = o["custom_id"].rsplit("-", 3)
        resp = o.get("response") or {}
        if resp.get("status_code") != 200:
            continue
        bd = resp["body"]
        _resolved.add(bd.get("model"))
        u = bd.get("usage", {})
        charge(judge, u.get("prompt_tokens", 0), u.get("completion_tokens", 0), BATCH_DISCOUNT)
        ch = bd["choices"][0]
        top = ((ch.get("logprobs") or {}).get("content") or [{}])[0].get("top_logprobs", [])
        got[(int(i), int(j))] = escore_from(top, (ch.get("message") or {}).get("content"))
    os.makedirs(BON_OUT, exist_ok=True)
    outf = f"{BON_OUT}/math__{args.cell}_{args.rep}.jsonl"
    with open(outf, "w") as f:
        for i, pid in enumerate(side["problem_ids"]):
            esc = []
            for j in range(side["n_samples"]):
                s, src = got.get((i, j), (5.0, "missing"))
                counts[src] = counts.get(src, 0) + 1
                esc.append(s)
            f.write(json.dumps(dict(problem_id=pid, escore=esc)) + "\n")
    write_meta(outf.replace(".jsonl", ".meta.json"),
               dict(cell=args.cell, rep=args.rep, batch_id=side["batch_id"], src_counts=counts))
    print(f"[batch-collect done] {outf} src {counts} ledger ${_ledger['usd']:.2f}")
