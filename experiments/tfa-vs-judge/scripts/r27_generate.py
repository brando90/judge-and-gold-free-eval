# R27 (papers/D-iclr-v2/registration_round27.md): answers to 200 hard HLE questions from two cheap generators, with HLE's official
# system prompt (SYSTEM_PROMPT of centerforaisafety/hle run_model_predictions.py, vendored at 67b3251). Resumable; spend capped.
# Run from experiments/tfa-vs-judge. OpenAI: system role, default temperature (HLE leaves temperature unset), max_completion_tokens 2048.
# Anthropic: the same text as the system prompt, thinking disabled, max_tokens 2048. Output runs/r27/gen_<model>.jsonl.
import argparse
import ast
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--provider", choices=("openai", "anthropic"), required=True)
ap.add_argument("--model", required=True)
ap.add_argument("--cap-usd", type=float, required=True)
ap.add_argument("--price-in", type=float, required=True)
ap.add_argument("--price-out", type=float, required=True)
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()


def vendored(path, name):
    for node in ast.parse(open(os.path.join(HERE, "vendor", path)).read()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit(name)


SYSTEM_PROMPT = vendored("centerforaisafety_hle_eval_run_model_predictions.py", "SYSTEM_PROMPT")
items = [json.loads(l) for l in open(os.path.join(HERE, "../../../papers/analysis/prevalence_v2/items_hle.jsonl"))]
if args.dry_run:
    print(SYSTEM_PROMPT, "\n---\n", items[0]["question"])
    raise SystemExit(0)


def load_key(name):
    if os.environ.get(name):
        return os.environ[name]
    for line in open(os.path.join(HERE, "../../../.env")):
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"\'')
    raise SystemExit(f"no {name}")


outf = f"runs/r27/gen_{args.model}.jsonl"
os.makedirs("runs/r27", exist_ok=True)
ledger = f"runs/r27/spend_gen_{args.model}.json"
spend = json.load(open(ledger)) if os.path.exists(ledger) else {"usd": 0.0, "calls": 0}
lock = threading.Lock()
if args.provider == "openai":
    import openai
    client = openai.OpenAI(api_key=load_key("OPENAI_API_KEY"), max_retries=6, timeout=600)
    ERR = (openai.APIError,)
else:
    import anthropic
    client = anthropic.Anthropic(api_key=load_key("ANTHROPIC_API_KEY"), max_retries=6)
    ERR = (anthropic.APIError,)


def one(it):
    with lock:
        if spend["usd"] >= args.cap_usd:
            return None
    row = dict(problem_id=it["id"], model=args.model)
    try:
        if args.provider == "openai":
            r = client.chat.completions.create(model=args.model, max_completion_tokens=2048,
                                               messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": it["question"]}])
            text, tin, tout, stop = r.choices[0].message.content or "", r.usage.prompt_tokens, r.usage.completion_tokens, r.choices[0].finish_reason
        else:
            r = client.messages.create(model=args.model, max_tokens=2048, thinking={"type": "disabled"}, system=SYSTEM_PROMPT,
                                       messages=[{"role": "user", "content": it["question"]}])
            text = "".join(b.text for b in r.content if b.type == "text")
            tin, tout, stop = r.usage.input_tokens, r.usage.output_tokens, r.stop_reason
        row.update(text=text, stop_reason=stop, input_tokens=tin, output_tokens=tout)
        with lock:
            spend["usd"] += tin * args.price_in / 1e6 + tout * args.price_out / 1e6
            spend["calls"] += 1
    except ERR as e:
        row.update(text=None, error=f"{type(e).__name__}: {str(e)[:200]}")
    return row


done = set()
if os.path.exists(outf):
    done = {json.loads(l)["problem_id"] for l in open(outf) if not json.loads(l).get("error")}
jobs = [it for it in items if it["id"] not in done]
print(f"[r27 gen {args.model}] {len(jobs)} questions", flush=True)
with open(outf, "a") as f, ThreadPoolExecutor(8) as ex:
    for row in ex.map(one, jobs):
        if row is not None:
            f.write(json.dumps(row) + "\n")
            f.flush()
json.dump(spend, open(ledger, "w"))
print(f"[r27 gen done] {outf} spend ${spend['usd']:.2f}", flush=True)
