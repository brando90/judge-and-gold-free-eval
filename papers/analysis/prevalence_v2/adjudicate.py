# Adjudication of Pass A / Pass B disagreements with claude-opus-5 (thinking disabled, no temperature).
# Resumable and spend-capped. Raw calls -> adjudication_calls_<ds>.jsonl; the full 200-item table with final
# labels -> adjudicated_<ds>.jsonl (rebuilt on every run, including the pre-registered cap/failure fallback).
#   python adjudicate.py [--datasets simpleqa,...] [--assemble-only]
import argparse
import json
import os
import random
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HERE, LABELS, PRICES, V2_DATASETS, last_by_id, load_jsonl, parse_label

ADJ = dict(model="claude-opus-5", provider="anthropic", max_tokens=800, thinking="disabled")
MAX_ATTEMPTS = 3

ap = argparse.ArgumentParser()
ap.add_argument("--datasets", default=",".join(V2_DATASETS))
ap.add_argument("--workers", type=int, default=6)
ap.add_argument("--assemble-only", action="store_true")
args = ap.parse_args()
datasets = [d for d in args.datasets.split(",") if os.path.exists(os.path.join(HERE, f"items_{d}.jsonl"))]


def valid(r):
    return r is not None and r.get("label") in LABELS


def needs_adjudication(a, b):
    return not (valid(a) and valid(b) and a["label"] == b["label"])


def order_swapped(item_id):
    # Pre-registered, seeded presentation order: Pass A is shown as Annotator 1 unless this draw is < 0.5.
    return random.Random(f"adj-{item_id}").random() < 0.5


def fallback(a, b):
    """Pre-registered fallback when adjudication cannot be obtained (cap or repeated failure)."""
    la = a["label"] if valid(a) else None
    lb = b["label"] if valid(b) else None
    if la is None and lb is None:
        return "UNCLEAR"
    if la is None or lb is None:
        return la or lb
    pair = {la, lb}
    if pair == {"MULTI", "UNIQUE"}:
        return "UNIQUE"
    return "UNCLEAR"  # {MULTI, UNCLEAR} or {UNIQUE, UNCLEAR}


def load_state(ds):
    items = load_jsonl(os.path.join(HERE, f"items_{ds}.jsonl"))
    A = last_by_id(os.path.join(HERE, f"labels_passA_{ds}.jsonl"))
    B = last_by_id(os.path.join(HERE, f"labels_passB_{ds}.jsonl"))
    C = last_by_id(os.path.join(HERE, f"adjudication_calls_{ds}.jsonl"))
    return items, A, B, C


def assemble(ds):
    items, A, B, C = load_state(ds)
    rows = []
    for it in items:
        a, b, c = A.get(it["id"]), B.get(it["id"]), C.get(it["id"])
        r = dict(id=it["id"], row=it["row"], question=it["question"], reference=it["reference"],
                 aliases=it.get("aliases", []),
                 passA_label=a["label"] if valid(a) else None, passA_subtype=(a or {}).get("subtype", ""),
                 passA_alternative=(a or {}).get("alternative", ""), passA_reasoning=(a or {}).get("reasoning", ""),
                 passB_label=b["label"] if valid(b) else None, passB_subtype=(b or {}).get("subtype", ""),
                 passB_alternative=(b or {}).get("alternative", ""), passB_reasoning=(b or {}).get("reasoning", ""))
        if not needs_adjudication(a, b):
            r.update(label=a["label"], subtype=a.get("subtype", "") if a["label"] != "UNIQUE" else "",
                     alternative=a.get("alternative", "") if a["label"] == "MULTI" else "",
                     adjudicated=False, adjudication_status="agreement", adjudication_reason="")
        elif valid(c):
            r.update(label=c["label"], subtype=c.get("subtype", "") if c["label"] != "UNIQUE" else "",
                     alternative=c.get("alternative", "") if c["label"] == "MULTI" else "",
                     adjudicated=True, adjudication_status="adjudicated",
                     adjudication_reason=c.get("reason", "") or c.get("reasoning", ""),
                     adjudicator_reasoning=c.get("reasoning", ""), adjudication_order_swapped=c.get("order_swapped"))
        else:
            lab = fallback(a, b)
            src = a if valid(a) and a["label"] == lab else (b if valid(b) and b["label"] == lab else None)
            r.update(label=lab, subtype=(src or {}).get("subtype", "") if lab != "UNIQUE" else "",
                     alternative=(src or {}).get("alternative", "") if lab == "MULTI" else "",
                     adjudicated=False, adjudication_status="fallback_no_adjudication",
                     adjudication_reason=(c or {}).get("error", "not attempted"))
        rows.append(r)
    with open(os.path.join(HERE, f"adjudicated_{ds}.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return rows


if not args.assemble_only:
    import anthropic
    from common import Ledger, env_value
    from prompts import SYSTEM_ADJUDICATOR, render_adjudication

    ledger = Ledger("anthropic")
    client = anthropic.Anthropic(api_key=env_value("ANTHROPIC_API_KEY"), max_retries=6)

    per_ds = []
    for ds in datasets:
        items, A, B, C = load_state(ds)
        todo = [(ds, it, A.get(it["id"]), B.get(it["id"])) for it in items
                if needs_adjudication(A.get(it["id"]), B.get(it["id"])) and not valid(C.get(it["id"]))]
        if any(it["id"] not in A or it["id"] not in B for it in items):
            print(f"[warn] {ds}: some items lack a Pass A or Pass B row; run the passes first", flush=True)
        per_ds.append(todo)
    jobs = []  # round-robin across datasets so a cap stop leaves each dataset partially covered, not one starved
    for k in range(max((len(t) for t in per_ds), default=0)):
        jobs += [t[k] for t in per_ds if k < len(t)]

    def one(job):
        ds, it, a, b = job
        swapped = order_swapped(it["id"])
        first, second = (b, a) if swapped else (a, b)
        user = render_adjudication(ds, it, first, second)
        row = dict(id=it["id"], dataset=ds, annotator="adjudicator", model=ADJ["model"],
                   params={k: v for k, v in ADJ.items() if k not in ("model", "provider")}, order_swapped=swapped,
                   passA_label=a.get("label") if a else None, passB_label=b.get("label") if b else None,
                   label=None, attempts=0, usage=[], cost_usd=0.0)
        pin, pout = PRICES[ADJ["model"]]
        amt = ((len(SYSTEM_ADJUDICATOR) + len(user)) / 2.5 * pin + ADJ["max_tokens"] * pout) / 1e6
        for attempt in range(MAX_ATTEMPTS):
            if not ledger.reserve(amt):
                row["error"] = "spend cap reached"
                return row
            row["attempts"] = attempt + 1
            try:
                r = client.messages.create(
                    model=ADJ["model"], max_tokens=ADJ["max_tokens"], thinking={"type": ADJ["thinking"]},
                    system=[{"type": "text", "text": SYSTEM_ADJUDICATOR, "cache_control": {"type": "ephemeral"}}],
                    messages=[{"role": "user", "content": user}])
            except anthropic.APIError as e:
                ledger.settle(amt, "adjudication", ADJ["model"], None)
                row["error"] = f"{type(e).__name__}: {str(e)[:300]}"
                continue
            u = r.usage
            usage = dict(input_tokens=u.input_tokens, output_tokens=u.output_tokens,
                         cache_creation_input_tokens=u.cache_creation_input_tokens or 0,
                         cache_read_input_tokens=u.cache_read_input_tokens or 0)
            row["cost_usd"] += ledger.settle(amt, "adjudication", ADJ["model"], usage)
            row["usage"].append(usage)
            text = "".join(bl.text for bl in r.content if bl.type == "text")
            row.update(response=text, stop_reason=r.stop_reason, served_model=r.model)
            parsed, reasoning = parse_label(text)
            if parsed:
                row.update(parsed)
                row["reasoning"] = reasoning
                row.pop("error", None)
                return row
            row["error"] = f"unparseable response (stop_reason={r.stop_reason})"
        return row

    print(f"[adjudication {ADJ['model']}] {len(jobs)} disagreements to adjudicate; {ledger.summary()}", flush=True)
    files, wlock, n_fail = {}, threading.Lock(), 0
    with ThreadPoolExecutor(args.workers) as ex:
        for i, row in enumerate(ex.map(one, jobs)):
            n_fail += row.get("label") is None
            with wlock:
                if row["dataset"] not in files:
                    files[row["dataset"]] = open(os.path.join(HERE, f"adjudication_calls_{row['dataset']}.jsonl"), "a")
                files[row["dataset"]].write(json.dumps(row, ensure_ascii=False) + "\n")
                files[row["dataset"]].flush()
            if (i + 1) % 25 == 0:
                print(f"  {i + 1}/{len(jobs)} failed={n_fail} {ledger.summary()}", flush=True)
    for f in files.values():
        f.close()
    print(f"[adjudication done] failed={n_fail} {ledger.summary()}" + ("  CAP REACHED" if ledger.cap_hit else ""), flush=True)

for ds in datasets:
    rows = assemble(ds)
    st = {}
    for r in rows:
        st[r["adjudication_status"]] = st.get(r["adjudication_status"], 0) + 1
    print(f"[assembled] {ds}: {st}", flush=True)
