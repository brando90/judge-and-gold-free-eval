# Shared helpers for the prevalence v2 audit: key loading (never printed), capped spend ledgers,
# label parsing, and the statistics used in the report (Wilson interval, Cohen's kappa, bootstrap).
import atexit
import json
import math
import os
import random
import re
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../.."))
V1_DIR = os.path.join(REPO, "papers/analysis/prevalence")

V2_DATASETS = ["simpleqa", "browsecomp", "hle", "triviaqa", "webinstruct"]
V1_DATASETS = ["math500", "gsm8k", "deepscaler", "nqopen"]
LABELS = ("MULTI", "UNIQUE", "UNCLEAR")

# USD per million tokens, as fixed in the audit brief (used for the ledger and the caps).
PRICES = {
    "claude-sonnet-5": (3.00, 15.00),
    "claude-opus-5": (15.00, 75.00),
    "gpt-5-mini-2025-08-07": (0.25, 2.00),
}
PROVIDER = {"claude-sonnet-5": "anthropic", "claude-opus-5": "anthropic", "gpt-5-mini-2025-08-07": "openai"}
CAPS_USD = {"anthropic": 12.00, "openai": 8.00}
CACHE_WRITE_MULT, CACHE_READ_MULT = 1.25, 0.10  # Anthropic 5-minute cache write / read multipliers
OPENAI_CACHED_MULT = 0.10  # OpenAI cached-input multiplier for gpt-5-mini


def env_value(name):
    """Read a key from the repo .env (skipping commented lines), falling back to the environment."""
    path = os.path.join(REPO, ".env")
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if s.startswith(name + "="):
                    return s.split("=", 1)[1].strip().strip("\"'")
    v = os.environ.get(name)
    if v:
        return v
    raise SystemExit(f"{name} not found in .env or environment")


def cost_usd(model, usage):
    pin, pout = (p / 1e6 for p in PRICES[model])
    if PROVIDER[model] == "anthropic":
        return (usage.get("input_tokens", 0) * pin
                + usage.get("cache_creation_input_tokens", 0) * pin * CACHE_WRITE_MULT
                + usage.get("cache_read_input_tokens", 0) * pin * CACHE_READ_MULT
                + usage.get("output_tokens", 0) * pout)
    cached = usage.get("cached_tokens", 0)
    return ((usage.get("prompt_tokens", 0) - cached) * pin + cached * pin * OPENAI_CACHED_MULT
            + usage.get("completion_tokens", 0) * pout)


class Ledger:
    """Per-provider spend ledger with a hard cap. Each call reserves its worst-case cost before it is
    sent, so concurrent calls can never push recorded spend past the cap."""

    def __init__(self, provider):
        self.provider = provider
        self.cap = CAPS_USD[provider]
        self.path = os.path.join(HERE, f"spend_{provider}.json")
        self.lockfile = os.path.join(HERE, f"spend_{provider}.lock")
        try:
            fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
        except FileExistsError:
            raise SystemExit(f"{self.lockfile} exists: another {provider} process is running (delete it if stale)")
        atexit.register(lambda: os.path.exists(self.lockfile) and os.remove(self.lockfile))
        self.lock = threading.Lock()
        self.reserved = 0.0
        self.cap_hit = False
        if os.path.exists(self.path):
            self.d = json.load(open(self.path))
        else:
            self.d = {"provider": provider, "cap_usd": self.cap, "usd": 0.0, "calls": 0, "by_stage": {},
                      "prices_usd_per_million": {m: PRICES[m] for m in PRICES if PROVIDER[m] == provider}}

    def reserve(self, amount):
        with self.lock:
            if self.d["usd"] + self.reserved + amount > self.cap:
                self.cap_hit = True
                return False
            self.reserved += amount
            return True

    def settle(self, reserved, stage, model, usage):
        c = cost_usd(model, usage) if usage else 0.0
        with self.lock:
            self.reserved -= reserved
            self.d["usd"] += c
            self.d["calls"] += 1 if usage else 0
            s = self.d["by_stage"].setdefault(stage, {"model": model, "usd": 0.0, "calls": 0, "tokens": {}})
            s["usd"] += c
            s["calls"] += 1 if usage else 0
            for k, v in (usage or {}).items():
                s["tokens"][k] = s["tokens"].get(k, 0) + int(v or 0)
            self._save()
        return c

    def add_manual(self, stage, model, usage):
        self.settle(0.0, stage, model, usage)

    def _save(self):
        tmp = self.path + ".tmp"
        json.dump(self.d, open(tmp, "w"), indent=1)
        os.replace(tmp, self.path)

    def summary(self):
        return f"{self.provider} spend ${self.d['usd']:.4f} / cap ${self.cap:.2f} ({self.d['calls']} calls)"


def parse_label(text):
    """Return (parsed dict, reasoning text) from a response that ends with a JSON object, else (None, text)."""
    dec = json.JSONDecoder()
    best, start = None, None
    for m in re.finditer(r"\{", text or ""):
        try:
            obj, _ = dec.raw_decode(text[m.start():])
        except ValueError:
            continue
        if isinstance(obj, dict) and "label" in obj:
            best, start = obj, m.start()
    if best is None:
        return None, (text or "").strip()
    lab = str(best.get("label", "")).strip().upper()
    if lab not in LABELS:
        return None, (text or "").strip()
    out = {"label": lab, "alternative": str(best.get("alternative") or "").strip(),
           "subtype": str(best.get("subtype") or "").strip()}
    if "reason" in best:
        out["reason"] = str(best.get("reason") or "").strip()
    reasoning = text[:start].strip()
    reasoning = re.sub(r"```(json)?\s*$", "", reasoning).strip()
    return out, reasoning


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def last_by_id(path):
    """Latest successful row per id (resumable append-only files); failed rows only if nothing better."""
    out = {}
    if not os.path.exists(path):
        return out
    for r in load_jsonl(path):
        if r.get("label") in LABELS or r["id"] not in out:
            out[r["id"]] = r
    return out


def wilson(k, n, z=1.959964):
    if n == 0:
        return [float("nan"), float("nan")]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def kappa(a, b, cats):
    n = len(a)
    if n == 0:
        return float("nan"), None
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return po, ((po - pe) / (1 - pe) if pe < 1 else None)


def bootstrap_kappa(a, b, cats, reps=2000, seed=0):
    rng = random.Random(seed)
    n = len(a)
    vals = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        _, k = kappa([a[i] for i in idx], [b[i] for i in idx], cats)
        if k is not None:
            vals.append(k)
    if len(vals) < reps * 0.5:
        return None
    vals.sort()
    return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]]
