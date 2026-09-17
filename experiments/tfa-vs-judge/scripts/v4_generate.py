# v4 production candidate generation for MathRefBench.
# Run from experiments/tfa-vs-judge:
#   python scripts/v4_generate.py --model gpt-4.1-mini-2025-04-14 --provider openai --price-in 0.4 --price-out 1.6
#
# Draws --n-samples candidate solutions for every checkable item (189 of 324) using the v4 candidate
# prompt verbatim. This pool is the input to every v4 judging experiment, so it is generated once.
#
# Two things differ from the pilot (scripts/v4_pilot_generate.py) and both matter:
#
#   1. TEMPERATURE IS SET EXPLICITLY. The pilot asked for one answer per item and never passed a
#      temperature. Drawing 64 samples at temperature 0 would return 64 near-identical strings and
#      the whole point of the pool -- a spread of distinct valid and invalid answers -- would be lost.
#
#   2. VALIDITY COMES FROM THE CHECKER, NOT THE ANSWER BANK. v4_checkers.py decides correctness from
#      the problem definition alone. The bank is a SAMPLE of valid answers (1,874 of 2,198 solutions
#      carry origin "generated"), so an answer absent from it may still be correct -- and those
#      correct-but-unbanked answers are precisely what the paper studies. bank_match is still
#      recorded, but only so the two signals can be compared; `valid` is the ground truth.
import argparse
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))  # judge-free-eval/
BENCH = os.path.join(ROOT, "datasets/final_mathrefbench.jsonl")
PROMPT = os.path.join(ROOT, "datasets/multirefbench_single_answer_v1.prompt")

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--provider", choices=("anthropic", "openai"), required=True)
ap.add_argument("--n-samples", type=int, default=64, help="candidate solutions per item")
ap.add_argument("--temperature", type=float, default=1.0)
ap.add_argument("--max-tokens", type=int, default=16000)
ap.add_argument("--workers", type=int, default=24)
ap.add_argument("--cap-usd", type=float, default=75.0)
ap.add_argument("--price-in", type=float, required=True)
ap.add_argument("--price-out", type=float, required=True)
ap.add_argument("--out-dir", default="runs/v4_pool")
ap.add_argument("--limit-items", type=int, default=0, help="debug: first N items only")
ap.add_argument("--items-file", default=None,
                help="restrict to the question_ids listed in this file, one per line. Used to probe "
                     "a targeted subset (e.g. the items a weaker generator never solved) without "
                     "regenerating the whole pool.")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

sys.path.insert(0, HERE)
import v4_checkers as C        # our checkers:            189 math_constraint items
import v4_mc_checkers as MC    # upstream MathConstruct:   67 mathconstruct items
import v4_csp_checkers as CSP  # upstream Math-Constraint: 61 more math_constraint items


def checkable(r):
    """317 of 324 items can be graded without consulting the answer bank:

        189  math_constraint  v4_checkers.py      pure-Python predicates
         67  mathconstruct    v4_mc_checkers.py   upstream check()
         61  math_constraint  v4_csp_checkers.py  upstream verify(), 0.47s/call via pycsp3

    The 7 excluded are low_autocorrelation, whose verifier rejects Math-Constraint's OWN stored
    solution -- a checker that rejects correct answers is the failure this paper studies, so those
    items stay unscored rather than scored wrongly.
    """
    if r["question_id"].startswith("math_constraint"):
        return C.family(r) in C.CHECKERS or CSP.covers(r)
    return MC.covers(r)


rows = [json.loads(l) for l in open(BENCH)]
items = [r for r in rows if checkable(r)]
# Applied AFTER checkable(), so a targeted probe can never generate for an item we cannot score.
if args.items_file:
    keep = {ln.strip() for ln in open(args.items_file) if ln.strip()}
    items = [r for r in items if r["question_id"] in keep]
    missing = keep - {r["question_id"] for r in items}
    if missing:
        print(f"[warn] {len(missing)} id(s) in {args.items_file} are not checkable or not in the "
              f"benchmark and were dropped, e.g. {sorted(missing)[:3]}", flush=True)
    if not items:
        raise SystemExit(f"--items-file matched no checkable items: {args.items_file}")
items.sort(key=lambda r: r["question_id"])
if args.limit_items:
    items = items[: args.limit_items]

template = open(PROMPT).read()
STRICT = ("\n\nThe boxed answer must be the literal value in exactly the format above: digits, "
          "commas and brackets only. Do not use LaTeX environments, \\ldots, ellipses, set-builder "
          "notation, or any abbreviation inside the box; write every element explicitly.")


def render(r):
    return (template.replace("[PROBLEM]", r["problem"])
                    .replace("[ANSWER_FORMAT]", r["formatting_instructions"] + STRICT))


def norm(a):
    """Format-insensitive key: compare answers by their integer content when they have one,
    else by stripped text. Without this, '0,4,1,3,2' and '[0, 4, 1, 3, 2]' look different."""
    nums = re.findall(r"-?\d+", str(a))
    if nums and not re.search(r"[a-zA-Z]{3,}", str(a)):
        return ",".join(nums)
    return re.sub(r"[\s\$]+", "", str(a)).strip().lower()


def extract(text):
    """Take the last <FINAL_ANSWER> tag, with or without a \\boxed{} wrapper inside it."""
    tags = re.findall(r"<FINAL_ANSWER>(.*?)</FINAL_ANSWER>", text, re.S)
    if tags:
        inner = tags[-1].strip()
        box = re.findall(r"\\boxed\{(.*)\}", inner, re.S)
        return (box[-1] if box else inner).strip()
    m = re.findall(r"\\boxed\{(.*?)\}", text, re.S)
    return m[-1].strip() if m else None


def load_key(name):
    """ANTHROPIC_API_KEY is capped until 2026-10-01; _1 and _2 work, _3 is invalid."""
    if os.environ.get(name):
        return os.environ[name]
    want = [name] if name != "ANTHROPIC_API_KEY" else ["ANTHROPIC_API_KEY_1", "ANTHROPIC_API_KEY_2", name]
    vals = {}
    for line in open(os.path.join(ROOT, ".env")):
        for w in want:
            if line.startswith(w + "="):
                v = line.split("=", 1)[1].strip().strip("\"'")
                if v:
                    vals.setdefault(w, v)
    for w in want:
        if w in vals:
            return vals[w]
    raise SystemExit(f"no {name}")


tag = args.model.replace("/", "_")
outf = os.path.join(args.out_dir, f"{tag}.jsonl")
ledger = os.path.join(args.out_dir, f"spend_{tag}.json")

if args.dry_run:
    print(f"{len(items)} items x {args.n_samples} samples = {len(items) * args.n_samples} calls")
    print(f"temperature {args.temperature}, cap ${args.cap_usd}, -> {outf}")
    print("--- rendered prompt, first item ---")
    print(render(items[0])[:1200])
    sys.exit(0)

os.makedirs(args.out_dir, exist_ok=True)
spend = json.load(open(ledger)) if os.path.exists(ledger) else {"usd": 0.0, "calls": 0}
lock = threading.Lock()
by_id = {r["question_id"]: r for r in items}

if args.provider == "anthropic":
    import anthropic
    client = anthropic.Anthropic(api_key=load_key("ANTHROPIC_API_KEY"), max_retries=8)
    ERRORS = (anthropic.APIError,)
else:
    import httpx
    import openai
    # timeout=900 caused a 9-minute stall with zero rows written. Diagnosis (macOS `sample`): all
    # 24 workers parked in ssl__SSLSocket_read on connections that had sent a request and would
    # never get a response, while a fresh connection from another process answered in 1.1s. The
    # account was nowhere near a rate limit (149,999,990 of 150M TPM remaining), so these were dead
    # sockets, and a 15-minute timeout meant every worker sat on one instead of retrying.
    #
    # Observed latency: p50 12s, p99 155s, max 158s -- so 300s is generous and still fails fast
    # enough for a retry to rescue the slot. max_keepalive_connections=0 stops pooled sockets being
    # reused: 45 ESTABLISHED connections for 24 workers showed stale ones accumulating, which is how
    # a dead socket gets handed back out. The extra TLS handshake (~100ms) is nothing against a 12s
    # call.
    # max_retries=3 / timeout=240, not 8 / 300. The timeout is per ATTEMPT, so 8 retries let a
    # single dead socket hold a worker for 8 x 300s = 2400s. Measured over 46 heartbeats of pass 1:
    # oldest-in-flight reached 2574s with only 2 resets, and throughput fell 67.8 -> 54.6 rows/min
    # (a 2.9 se drop) as wedged slots reached equilibrium -- roughly 19%. Bounded, but avoidable.
    # 3 x 240s caps a wedged slot at ~720s instead. Observed latency is p99 155s, max 158s, so a
    # 240s timeout never cuts a legitimate call short, and pass 1 ran 3,300 draws with 0 errors on
    # 8 retries, so 3 is ample headroom for transient failures.
    client = openai.OpenAI(
        api_key=load_key("OPENAI_API_KEY"), max_retries=3, timeout=240.0,
        http_client=httpx.Client(
            timeout=httpx.Timeout(240.0, connect=15.0, read=240.0),
            limits=httpx.Limits(max_connections=args.workers + 4, max_keepalive_connections=0)))
    ERRORS = (openai.APIError,)

# Resume. A unit of work is (question_id, sample index), so an interrupted run picks up exactly the
# draws it is missing. Errored rows are not marked done and will be retried; truncated rows ARE
# marked done, flagged, and left for inspection -- retrying them forever would stall the run on a
# handful of items whose constructions do not fit in the token budget.
done = set()
if os.path.exists(outf):
    for l in open(outf):
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            continue  # torn final line from a killed run
        if not r.get("error"):
            done.add((r["question_id"], r["sample"]))

units = [(r["question_id"], i) for r in items for i in range(args.n_samples)]
todo = [u for u in units if u not in done]
random.Random(20260902).shuffle(todo)  # spread each item's draws over time, so a mid-run stop
                                       # leaves partial coverage of every item rather than a
                                       # complete prefix and nothing after it


def one(unit):
    qid, idx = unit
    with lock:
        if spend["usd"] >= args.cap_usd:
            return None
    r = by_id[qid]
    t0 = time.time()
    # `row` is bound BEFORE the try because the except handler and the return both reference it.
    # Assigned inside the try, anything raising first would make the handler itself die with
    # UnboundLocalError, losing the draw behind a misleading traceback. py_compile does not catch
    # that -- it is a runtime binding error, not a syntax one.
    # Record the temperature we ACTUALLY sent. The Anthropic path cannot pass one on SDK 1.6.0, so
    # the API default applies; writing args.temperature there would assert a setting we never sent.
    row = {"question_id": qid, "sample": idx, "model": args.model,
           "temperature": (None if args.provider == "anthropic" else args.temperature),
           "temperature_source": ("api_default" if args.provider == "anthropic" else "explicit"),
           "family": C.family(r)}
    # Registration goes INSIDE the try so the finally always removes it. Registered before the try,
    # the entry leaks permanently if anything in between raises, and a leaked entry is
    # indistinguishable from a wedged worker in the heartbeat -- during pass 1 one entry grew by 60s
    # on 128 of 136 beats, reaching 133 minutes, far past the max_retries x timeout bound.
    try:
        with lock:
            inflight[unit] = t0
        if args.provider == "anthropic":
            # NO temperature argument. anthropic SDK 1.6.0 removed it from BOTH messages.create()
            # and messages.stream() -- passing it raises TypeError. (The earlier pilot ran on the
            # 0.x SDK, where it was accepted, so this only surfaced after the 1.x upgrade.)
            # Anthropic's API default is temperature 1.0, which is what we want for diverse draws,
            # so omitting it gives the intended behaviour rather than silently sampling greedily.
            #
            # The SDK also refuses a non-streaming request whose max_tokens implies >10 minutes of
            # generation, so stream whenever the cap is large.
            if args.max_tokens > 8192:
                with client.messages.stream(model=args.model, max_tokens=args.max_tokens,
                                            messages=[{"role": "user", "content": render(r)}]) as s:
                    resp = s.get_final_message()
            else:
                resp = client.messages.create(model=args.model, max_tokens=args.max_tokens,
                                              messages=[{"role": "user", "content": render(r)}])
            text = "".join(b.text for b in resp.content if b.type == "text")
            tin, tout, stop = resp.usage.input_tokens, resp.usage.output_tokens, resp.stop_reason
        else:
            resp = client.chat.completions.create(
                model=args.model, messages=[{"role": "user", "content": render(r)}],
                max_completion_tokens=args.max_tokens, temperature=args.temperature)
            text = resp.choices[0].message.content or ""
            tin, tout = resp.usage.prompt_tokens, resp.usage.completion_tokens
            stop = resp.choices[0].finish_reason
        ans = extract(text)
        bank = {norm(s["answer"]): s["normalized_answer_id"] for s in r["solutions"]}
        # A reply with no parseable answer is a FAILED draw, not an undecidable one: there is
        # nothing to submit, so it counts against best-of-n exactly as a wrong answer does. It must
        # be False here, because v4_rescore.py records False for this case -- and a generator that
        # disagreed with the re-scorer would leave the pool inconsistent with no trace of why.
        # The distinction from a genuinely wrong answer is preserved in the reason field.
        if not ans:
            ok = False
        elif r["question_id"].startswith("math_constraint"):
            ok = C.check(r, ans)
            if ok is None:                 # solver-backed fallback for items our predicates miss
                ok = CSP.check(r, ans)
        else:
            # Pass the full reply: upstream pulls the LAST \boxed{} out itself, and its parser
            # needs that LaTeX. Handing it the bare extracted string loses list-depth information.
            ok = MC.check(r, ans, raw_text=text)
        row.update(answer=ans,
                   valid=ok,
                   bank_match=bool(ans and norm(ans) in bank),
                   matched_class=bank.get(norm(ans)) if ans else None,
                   truncated=(stop in ("length", "max_tokens")),
                   stop_reason=stop, input_tokens=tin, output_tokens=tout,
                   seconds=round(time.time() - t0, 1),
                   text=text)  # full reply kept: judges grade the solution, not just the answer,
                               # and regenerating the pool costs real money
        with lock:
            spend["usd"] += tin * args.price_in / 1e6 + tout * args.price_out / 1e6
            spend["calls"] += 1
    except ERRORS as e:
        row.update(error=f"{type(e).__name__}: {str(e)[:300]}")
    finally:
        with lock:
            inflight.pop(unit, None)
    return row


print(f"[v4 pool {args.model}] {len(todo)} of {len(units)} draws remaining "
      f"({len(items)} items x {args.n_samples}), spend ${spend['usd']:.2f}, cap ${args.cap_usd}",
      flush=True)

n = 0
t_start = time.time()
inflight = {}          # unit -> start time; lets a stall say WHAT is stuck, not merely that we stalled
done_evt = threading.Event()


def heartbeat():
    """Log rows written, in-flight count and oldest in-flight age every 60s.

    Without this a stall is invisible -- the job simply stops writing and the cause has to be
    reconstructed afterwards from socket tables. That is how a dead-socket hang produced three wrong
    diagnoses (head-of-queue blocking, oversized max_tokens, rate limiting) before macOS `sample`
    showed 24 threads parked in ssl__SSLSocket_read. An oldest-in-flight age climbing past the ~158s
    worst observed call is the signature of that failure.
    """
    last = -1
    while not done_evt.wait(60):
        with lock:
            ages = sorted(time.time() - t for t in inflight.values())
            cur = n
        oldest = f", oldest in-flight {ages[-1]:.0f}s" if ages else ""
        flag = "   <-- NO PROGRESS SINCE LAST BEAT" if cur == last else ""
        print(f"  [hb] {cur}/{len(todo)} rows | in-flight {len(ages)}{oldest}{flag}", flush=True)
        last = cur


threading.Thread(target=heartbeat, daemon=True).start()
# as_completed, not ex.map: map yields in SUBMISSION order, so one call that hangs through its
# timeout and retries would block every finished row behind it from being written -- on a run this
# long that risks losing hours of paid work to a single stuck request.
with open(outf, "a") as f, ThreadPoolExecutor(args.workers) as ex:
    futs = [ex.submit(one, u) for u in todo]
    for fut in as_completed(futs):
        row = fut.result()
        if row is None:
            continue
        with lock:
            f.write(json.dumps(row) + "\n")
            f.flush()
            spend_now = spend["usd"]
        n += 1
        if n % 200 == 0:
            rate = n / max(time.time() - t_start, 1) * 3600
            left = (len(todo) - n) / max(rate, 1e-9)
            print(f"  {n}/{len(todo)} | ${spend_now:.2f} | {rate:.0f}/h | ~{left:.1f}h left", flush=True)
            json.dump(spend, open(ledger, "w"))

json.dump(spend, open(ledger, "w"))

got = [json.loads(l) for l in open(outf)]
ok = [r for r in got if not r.get("error")]
val = [r for r in ok if r.get("valid") is True]
inv = [r for r in ok if r.get("valid") is False]
unp = [r for r in ok if r.get("answer") is None]
trunc = [r for r in ok if r.get("truncated")]
banked = [r for r in val if r.get("bank_match")]
print(f"[done] {args.model}: {len(ok)} draws | valid {len(val)} | invalid {len(inv)} "
      f"| unparseable {len(unp)} | truncated {len(trunc)} | spend ${spend['usd']:.2f}", flush=True)
print(f"  of the {len(val)} valid answers, {len(banked)} are in the bank and "
      f"{len(val) - len(banked)} are correct but UNBANKED (the pool the paper needs)", flush=True)
