# Frontier-judge harness over provider APIs, producing score files in EXACTLY the format the
# frozen producers read (rows {problem_id, escore: [float|null per sample]}, file
# {out}/{prefix}__{judge_tag}__{cond}_{rep}.jsonl), so repl_analysis / mitigation_analysis and
# their registered successors run unchanged on frontier judges.
#
# INTERNAL REGISTRATION (harness half; predictions live in papers/analysis/frontier_phase2_analysis.py
# and papers/D-reference-laws/registration.md): committed BEFORE any frontier API score exists.
#
# Why a new path. The earlier frontier check (frontier_judge.py) went through the Claude CLI, which
# returns one sampled integer, so only margins could be read. This harness has two score functions,
# pinned here so the choice cannot be made after seeing data:
#   openai    : logprob-EXPECTED value over the score tokens 0..10 at the first generated position,
#               the open judges' estimator (bon_judge.py), from top_logprobs=5 (the API maximum on
#               GPT-5.x), renormalized over the score-token mass; reasoning_effort="none" because
#               GPT-5.x refuses logprobs with any reasoning; temperature 0; max_completion_tokens 4.
#               Fallback identical to bon_judge: if score-token mass < 0.25, parse the text.
#   anthropic : SAMPLED INTEGER (the Messages API exposes no logprobs), temperature 0, max_tokens 4,
#               last integer 0..10 in the reply. Margin readouts only; NO inflation is computed from
#               this path (the score-resolution finding: an 11-value judge ties under best-of-64).
# Prompts are byte-for-byte the open judges' prompts: system = bon_rubrics.RUBRIC_TIES[(cond_key, rep)]
# (+ the M1 sentence from mitigation_judge.py), user = Problem / Reference answer (trusted) /
# Candidate solution / Score:. Providers receive system and user as separate roles, as vLLM does.
#
# Conditions: noref | ref | m1 (needs --blind-scores = this judge's noref_{rep} file, as in
# mitigation_judge.py: the second call shows the reference and the blind score).
# Modes: sync (thread pool, resumable per item) | batch-submit (OpenAI Batch API or Anthropic
# Message Batches; writes {out}.batch.json) | batch-collect (fetch results, write the score file).
# --valid-only judges oracle-valid samples only (margin experiments) and writes null elsewhere.
#
# Usage (from experiments/tfa-vs-judge):
#   python3 scripts/frontier_api_judge.py --provider openai --model gpt-5.4-2026-03-05 \
#       --pool runs/bon/bon_repl__meta-llama__Llama-3.1-8B-Instruct.jsonl --tasks runs/repl_main_tasks.jsonl \
#       --out runs/bon_scores_repl --prefix synthk --cond ref --rep a --mode batch-submit
import argparse
import json
import math
import os
import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bon_rubrics import RUBRIC_TIES  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--provider", choices=["openai", "anthropic"], required=True)
ap.add_argument("--model", required=True, help="pinned model id, e.g. gpt-5.4-2026-03-05")
ap.add_argument("--pool", required=True)
ap.add_argument("--tasks", default=None, help="task file to fill missing problem/ref fields")
ap.add_argument("--out", required=True, help="score directory, e.g. runs/bon_scores_repl")
ap.add_argument("--prefix", default="synthk", help="file prefix the producer expects")
ap.add_argument("--cond", choices=["noref", "ref", "m1"], required=True)
ap.add_argument("--rep", choices=["a", "b"], required=True)
ap.add_argument("--mode", choices=["sync", "batch-submit", "batch-collect"], default="sync")
ap.add_argument("--blind-scores", default=None, help="m1: this judge's noref_{rep} score file")
ap.add_argument("--valid-only", action="store_true")
ap.add_argument("--limit-items", type=int, default=0, help="pilot: judge only the first N items")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--reasoning-effort", default="none",
                help="openai gpt-5.x only; 'none' is the only value that returns logprobs")
args = ap.parse_args()

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
if args.provider == "openai" and not OPENAI_KEY:
    raise SystemExit("OPENAI_API_KEY not set (set -a; source .env; set +a)")
if args.provider == "anthropic" and not ANTHROPIC_KEY:
    raise SystemExit("ANTHROPIC_API_KEY not set")

tag = f"{args.provider}__{args.model.replace('/', '__')}"
os.makedirs(args.out, exist_ok=True)
outf = f"{args.out}/{args.prefix}__{tag}__{args.cond}_{args.rep}.jsonl"
batchf = outf + ".batch.json"

# ---------------------------------------------------------------- pool
pool = [json.loads(l) for l in open(args.pool)]
if args.tasks:
    tmap = {}
    for l in open(args.tasks):
        t = json.loads(l)
        tmap[t.get("problem_id") or t.get("task_id")] = t
    for r in pool:
        r.update({k: v for k, v in tmap.get(r["problem_id"], {}).items() if k not in r})
pool = [r for r in pool if "oracle" in r]
if args.limit_items:
    pool = pool[:args.limit_items]
missing = sum(1 for r in pool if not (r.get("problem") or r.get("question")))
if missing:
    raise SystemExit(f"{missing} pool rows lack problem text; pass --tasks")

BLIND = {}
if args.cond == "m1":
    if not args.blind_scores:
        raise SystemExit("--blind-scores required for m1")
    for l in open(args.blind_scores):
        w = json.loads(l)
        BLIND[w["problem_id"]] = w["escore"]

# ---------------------------------------------------------------- prompts (mirror bon_judge / mitigation_judge)
def build(r, i):
    q = r.get("problem") or r.get("question")
    s = r["samples"][i]
    if args.cond == "noref":
        sysmsg = RUBRIC_TIES[("noref", args.rep)]
        user = f"Problem:\n{q}\n\nCandidate solution:\n{s}\n\nScore:"
    elif args.cond == "ref":
        sysmsg = RUBRIC_TIES[("ref", args.rep)]
        user = f"Problem:\n{q}\n\nReference answer (trusted):\n{r['ref_answer']}\n\nCandidate solution:\n{s}\n\nScore:"
    else:  # m1, verbatim from mitigation_judge.py
        b = BLIND[r["problem_id"]][i]
        if b is None:
            return None, None
        sysmsg = RUBRIC_TIES[("ref", args.rep)] + (
            " You have already assessed this candidate without seeing any reference. "
            "A correct answer that differs from the reference must keep the score you gave it; "
            "revise only if the reference reveals the candidate is actually wrong.")
        user = (f"Problem:\n{q}\n\nReference answer (one valid answer, trusted):\n"
                f"{r['ref_answer']}\n\nCandidate solution:\n{s}\n\n"
                f"Your blind score for this candidate was {b:.1f} out of 10.\n\nScore:")
    return sysmsg, user


def wanted(r, i):
    return (not args.valid_only) or bool(r["oracle"][i])


# ---------------------------------------------------------------- request bodies
def openai_body(sysmsg, user):
    body = dict(model=args.model, messages=[{"role": "system", "content": sysmsg},
                                            {"role": "user", "content": user}],
                max_completion_tokens=4, temperature=0, logprobs=True, top_logprobs=5)
    if args.model.startswith("gpt-5"):
        body["reasoning_effort"] = args.reasoning_effort
    return body


def anthropic_body(sysmsg, user):
    return dict(model=args.model, max_tokens=4, temperature=0, system=sysmsg,
                messages=[{"role": "user", "content": user}])


# ---------------------------------------------------------------- score functions (pinned)
SCORE_TOK = {}
for v in range(11):
    for s in (str(v), " " + str(v)):
        SCORE_TOK[s] = v


def escore_openai(choice):
    """bon_judge.py estimator on API logprobs: expected value over score tokens, mass-renormalized."""
    txt = (choice["message"]["content"] or "").strip()
    lp = choice.get("logprobs") or {}
    content = lp.get("content") or []
    top = content[0].get("top_logprobs", []) if content else []
    one_means = 10 if txt.startswith("10") else 1
    num = den = 0.0
    for t in top:
        tok = t["token"]
        if tok in SCORE_TOK:
            v = one_means if SCORE_TOK[tok] == 1 else SCORE_TOK[tok]
            p = math.exp(t["logprob"])
            num += p * v
            den += p
    if den >= 0.25:
        return num / den
    m = re.search(r"\d+", txt)
    return float(min(int(m.group()), 10)) if m else 5.0


def escore_anthropic(text):
    """Sampled integer: last integer 0..10 in the reply (frontier_judge.py's corrected parser)."""
    ints = [int(x) for x in re.findall(r"\b(10|[0-9])\b", text or "")]
    return float(ints[-1]) if ints else 5.0


# ---------------------------------------------------------------- HTTP
def post(url, body, headers, timeout=120):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503, 529) and attempt < 7:
                time.sleep(min(60, 2 ** attempt))
                continue
            raise SystemExit(f"HTTP {e.code}: {msg}")
        except Exception:
            if attempt < 7:
                time.sleep(min(60, 2 ** attempt))
                continue
            raise
    raise SystemExit("unreachable")


def get(url, headers, raw=False, timeout=120):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        b = resp.read()
        return b if raw else json.loads(b)


OA_H = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
AN_H = {"x-api-key": ANTHROPIC_KEY or "", "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"}


def call_one(sysmsg, user):
    if args.provider == "openai":
        d = post("https://api.openai.com/v1/chat/completions", openai_body(sysmsg, user), OA_H)
        return escore_openai(d["choices"][0])
    d = post("https://api.anthropic.com/v1/messages", anthropic_body(sysmsg, user), AN_H)
    text = "".join(b.get("text", "") for b in d.get("content", []))
    return escore_anthropic(text)


# ---------------------------------------------------------------- modes
def write_rows(rows):
    with open(outf, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


if args.mode == "sync":
    done = {}
    if os.path.exists(outf):
        for l in open(outf):
            w = json.loads(l)
            done[w["problem_id"]] = w["escore"]
    todo = [r for r in pool if r["problem_id"] not in done]
    print(f"[frontier {tag}] {args.cond}_{args.rep}: {len(done)} items done, {len(todo)} to judge",
          flush=True)
    n_calls = 0
    for r in todo:
        jobs = {}
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            for i in range(len(r["samples"])):
                if not wanted(r, i):
                    continue
                sysmsg, user = build(r, i)
                if sysmsg is None:
                    continue
                jobs[ex.submit(call_one, sysmsg, user)] = i
            esc = [None] * len(r["samples"])
            for fut in as_completed(jobs):
                esc[jobs[fut]] = fut.result()
                n_calls += 1
        done[r["problem_id"]] = esc
        write_rows([dict(problem_id=p, escore=e) for p, e in done.items()])
        print(f"  {r['problem_id']}: {sum(e is not None for e in esc)} scored", flush=True)
    print(f"[frontier {tag}] wrote {outf} ({n_calls} calls this run)")

elif args.mode == "batch-submit":
    if os.path.exists(batchf):
        raise SystemExit(f"{batchf} exists; collect or delete it first")
    reqs = []
    for r in pool:
        for i in range(len(r["samples"])):
            if not wanted(r, i):
                continue
            sysmsg, user = build(r, i)
            if sysmsg is None:
                continue
            cid = f"{r['problem_id']}|{i}"
            if args.provider == "openai":
                reqs.append(dict(custom_id=cid, method="POST", url="/v1/chat/completions",
                                 body=openai_body(sysmsg, user)))
            else:
                reqs.append(dict(custom_id=cid.replace("/", "_")[:64],
                                 params=anthropic_body(sysmsg, user)))
    print(f"[frontier {tag}] submitting {len(reqs)} requests", flush=True)
    if args.provider == "openai":
        # upload the JSONL, then create the batch
        boundary = "----frontierbatch"
        payload = b"".join([
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"purpose\"\r\n\r\nbatch\r\n".encode(),
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"reqs.jsonl\"\r\n"
            f"Content-Type: application/jsonl\r\n\r\n".encode(),
            "".join(json.dumps(q) + "\n" for q in reqs).encode(),
            f"\r\n--{boundary}--\r\n".encode()])
        req = urllib.request.Request("https://api.openai.com/v1/files", data=payload,
                                     headers={"Authorization": f"Bearer {OPENAI_KEY}",
                                              "Content-Type": f"multipart/form-data; boundary={boundary}"},
                                     method="POST")
        with urllib.request.urlopen(req, timeout=600) as resp:
            fid = json.loads(resp.read())["id"]
        b = post("https://api.openai.com/v1/batches",
                 dict(input_file_id=fid, endpoint="/v1/chat/completions", completion_window="24h",
                      metadata=dict(tag=tag, cond=args.cond, rep=args.rep, prefix=args.prefix)), OA_H)
        json.dump(dict(provider="openai", batch_id=b["id"], input_file_id=fid, n=len(reqs),
                       submitted=time.strftime("%Y-%m-%dT%H:%M:%S")), open(batchf, "w"), indent=1)
        print(f"[frontier {tag}] OpenAI batch {b['id']} submitted ({len(reqs)} requests) -> {batchf}")
    else:
        hdr = dict(AN_H)
        b = post("https://api.anthropic.com/v1/messages/batches", dict(requests=reqs), hdr)
        json.dump(dict(provider="anthropic", batch_id=b["id"], n=len(reqs),
                       submitted=time.strftime("%Y-%m-%dT%H:%M:%S")), open(batchf, "w"), indent=1)
        print(f"[frontier {tag}] Anthropic batch {b['id']} submitted ({len(reqs)} requests) -> {batchf}")

else:  # batch-collect
    meta = json.load(open(batchf))
    esc = {r["problem_id"]: [None] * len(r["samples"]) for r in pool}
    if meta["provider"] == "openai":
        b = get(f"https://api.openai.com/v1/batches/{meta['batch_id']}", OA_H)
        print(f"[frontier {tag}] batch {b['id']} status={b['status']} counts={b.get('request_counts')}")
        if b["status"] != "completed":
            raise SystemExit("not completed yet")
        raw = get(f"https://api.openai.com/v1/files/{b['output_file_id']}/content", OA_H, raw=True)
        n_err = 0
        for line in raw.decode().splitlines():
            o = json.loads(line)
            pid, i = o["custom_id"].rsplit("|", 1)
            resp = o.get("response") or {}
            if resp.get("status_code") != 200:
                n_err += 1
                continue
            esc[pid][int(i)] = escore_openai(resp["body"]["choices"][0])
        if b.get("error_file_id"):
            print("  error file present:", b["error_file_id"])
        print(f"  parsed; {n_err} failed requests")
    else:
        b = get(f"https://api.anthropic.com/v1/messages/batches/{meta['batch_id']}", AN_H)
        print(f"[frontier {tag}] batch {b['id']} status={b['processing_status']} counts={b.get('request_counts')}")
        if b["processing_status"] != "ended":
            raise SystemExit("not ended yet")
        cid_map = {}
        for r in pool:
            for i in range(len(r["samples"])):
                cid_map[f"{r['problem_id']}|{i}".replace("/", "_")[:64]] = (r["problem_id"], i)
        raw = get(b["results_url"], AN_H, raw=True)
        n_err = 0
        for line in raw.decode().splitlines():
            o = json.loads(line)
            pid, i = cid_map[o["custom_id"]]
            res = o["result"]
            if res["type"] != "succeeded":
                n_err += 1
                continue
            text = "".join(blk.get("text", "") for blk in res["message"]["content"])
            esc[pid][i] = escore_anthropic(text)
        print(f"  parsed; {n_err} failed requests")
    write_rows([dict(problem_id=p, escore=e) for p, e in esc.items()])
    n_scored = sum(e is not None for v in esc.values() for e in v)
    print(f"[frontier {tag}] wrote {outf}: {len(esc)} items, {n_scored} scored samples")
