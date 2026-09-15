# Independent annotation passes for the prevalence v2 audit. Resumable (append-only; finished ids skipped),
# spend-capped per provider (common.Ledger). Neither pass reads the other pass's labels.
#   Pass A: python annotate.py --pass A                     -> labels_passA_<ds>.jsonl   (claude-sonnet-5)
#   Pass B: python annotate.py --pass B                     -> labels_passB_<ds>.jsonl   (gpt-5-mini-2025-08-07)
#   v1 relabel: python annotate.py --pass B --v1            -> labels_passB_v1_<ds>.jsonl
import argparse
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (HERE, LABELS, V1_DATASETS, V1_DIR, V2_DATASETS, Ledger, env_value, last_by_id, load_jsonl,
                    parse_label)
from prompts import SYSTEM_ANNOTATOR, render_item

PASS_A = dict(model="claude-sonnet-5", provider="anthropic", max_tokens=800, thinking="disabled")
PASS_B = dict(model="gpt-5-mini-2025-08-07", provider="openai", reasoning_effort="medium", max_completion_tokens=12000)
MAX_ATTEMPTS = 3  # first call plus up to two retries when the API errors, refuses, or the JSON cannot be parsed

ap = argparse.ArgumentParser()
ap.add_argument("--pass", dest="which", choices=("A", "B"), required=True)
ap.add_argument("--v1", action="store_true", help="relabel the 800 v1 items (Pass B only)")
ap.add_argument("--datasets", default=None)
ap.add_argument("--workers", type=int, default=8)
args = ap.parse_args()
if args.v1 and args.which != "B":
    raise SystemExit("--v1 relabel is defined for Pass B only")

cfg = PASS_A if args.which == "A" else PASS_B
datasets = args.datasets.split(",") if args.datasets else (V1_DATASETS if args.v1 else V2_DATASETS)
ledger = Ledger(cfg["provider"])
stage = f"pass{args.which}" + ("_v1relabel" if args.v1 else "")

if cfg["provider"] == "anthropic":
    import anthropic
    client = anthropic.Anthropic(api_key=env_value("ANTHROPIC_API_KEY"), max_retries=6)
    API_ERRORS = (anthropic.APIError,)
else:
    import openai
    client = openai.OpenAI(api_key=env_value("OPENAI_API_KEY"), max_retries=6)
    API_ERRORS = (openai.APIError,)


def reserve_amount(user):
    in_tok = (len(SYSTEM_ANNOTATOR) + len(user)) / 2.5  # generous chars-to-tokens bound
    from common import PRICES
    pin, pout = PRICES[cfg["model"]]
    out_tok = cfg.get("max_tokens") or cfg.get("max_completion_tokens")
    return (in_tok * pin + out_tok * pout) / 1e6


def call(user):
    if cfg["provider"] == "anthropic":
        r = client.messages.create(
            model=cfg["model"], max_tokens=cfg["max_tokens"], thinking={"type": cfg["thinking"]},
            system=[{"type": "text", "text": SYSTEM_ANNOTATOR, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user}])
        text = "".join(b.text for b in r.content if b.type == "text")
        u = r.usage
        usage = dict(input_tokens=u.input_tokens, output_tokens=u.output_tokens,
                     cache_creation_input_tokens=u.cache_creation_input_tokens or 0,
                     cache_read_input_tokens=u.cache_read_input_tokens or 0)
        return text, r.stop_reason, usage, r.model
    r = client.chat.completions.create(
        model=cfg["model"], reasoning_effort=cfg["reasoning_effort"], max_completion_tokens=cfg["max_completion_tokens"],
        messages=[{"role": "system", "content": SYSTEM_ANNOTATOR}, {"role": "user", "content": user}])
    ch = r.choices[0]
    u = r.usage
    usage = dict(prompt_tokens=u.prompt_tokens, completion_tokens=u.completion_tokens,
                 cached_tokens=getattr(u.prompt_tokens_details, "cached_tokens", 0) or 0,
                 reasoning_tokens=getattr(u.completion_tokens_details, "reasoning_tokens", 0) or 0)
    stop = "refusal" if getattr(ch.message, "refusal", None) else ch.finish_reason
    return ch.message.content or "", stop, usage, r.model


def one(job):
    ds, it = job
    user = render_item(ds, it)
    row = dict(id=it["id"], dataset=ds, annotator=f"pass{args.which}", model=cfg["model"],
               params={k: v for k, v in cfg.items() if k not in ("model", "provider")},
               label=None, alternative="", subtype="", reasoning="", attempts=0, usage=[], cost_usd=0.0)
    for attempt in range(MAX_ATTEMPTS):
        amt = reserve_amount(user)
        if not ledger.reserve(amt):
            row["error"] = "spend cap reached"
            return row
        row["attempts"] = attempt + 1
        try:
            text, stop, usage, served = call(user)
        except API_ERRORS as e:
            ledger.settle(amt, stage, cfg["model"], None)
            row["error"] = f"{type(e).__name__}: {str(e)[:300]}"
            continue
        row["cost_usd"] += ledger.settle(amt, stage, cfg["model"], usage)
        row["usage"].append(usage)
        row.update(response=text, stop_reason=stop, served_model=served)
        parsed, reasoning = parse_label(text)
        if parsed:
            row.update(parsed)
            row["reasoning"] = reasoning
            row.pop("error", None)
            return row
        row["error"] = f"unparseable response (stop_reason={stop})"
    return row


out_name = (lambda ds: f"labels_pass{args.which}_v1_{ds}.jsonl") if args.v1 else (lambda ds: f"labels_pass{args.which}_{ds}.jsonl")
jobs = []
for ds in datasets:
    ipath = os.path.join(V1_DIR if args.v1 else HERE, f"items_{ds}.jsonl")
    if not os.path.exists(ipath):
        print(f"[skip] {ds}: no items file {ipath}", flush=True)
        continue
    done = {i for i, r in last_by_id(os.path.join(HERE, out_name(ds))).items() if r.get("label") in LABELS}
    jobs += [(ds, it) for it in load_jsonl(ipath) if it["id"] not in done]
print(f"[{stage} {cfg['model']}] {len(jobs)} items to label; {ledger.summary()}", flush=True)

files = {}
wlock = threading.Lock()
n_fail = 0
with ThreadPoolExecutor(args.workers) as ex:
    for i, row in enumerate(ex.map(one, jobs)):
        n_fail += row.get("label") is None
        with wlock:
            if row["dataset"] not in files:
                files[row["dataset"]] = open(os.path.join(HERE, out_name(row["dataset"])), "a")
            if row.get("error") != "spend cap reached" or row["attempts"]:
                files[row["dataset"]].write(json.dumps(row, ensure_ascii=False) + "\n")
                files[row["dataset"]].flush()
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(jobs)} failed={n_fail} {ledger.summary()}", flush=True)
for f in files.values():
    f.close()
print(f"[{stage} done] failed/unlabeled={n_fail} {ledger.summary()}" + ("  CAP REACHED" if ledger.cap_hit else ""), flush=True)
sys.exit(3 if ledger.cap_hit else 0)
