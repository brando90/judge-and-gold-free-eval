#!/usr/bin/env python3
"""Experiment 05 analysis: format-robust SC vs format-robust pass@1 on GSM8K, Part B rule.

CPU only. No model calls and no paid API. Implements PREREG.md.
Gold for the primary endpoint is experiment 03's gold_ok (the matcher experiment 04 calls).
The extractor is experiment 04's fr_extract.py, imported, not copied.

    python3 analyze_gsm8k.py
    python3 analyze_gsm8k.py --tasks <tasks.jsonl> --gen <gen dir> --out <results dir>

Writes bootstrap_seed.json before any resample, then results.json, tables.md, and model_rank.png.
Verdict fields are null unless all ten frozen models have n=16 on all 1319 items.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import generate_gsm8k as frozen  # noqa: E402

BOOT = 2000
SEED = 20261126
N = 16
TAU_BOOT_CUTOFF = 0.733
DEFAULT_ROOT = Path("/lfs/mercury2/0/brando9/judge-free-eval-exp05")

_FR = None
_A03 = None


def fr_module():
    global _FR
    if _FR is None:
        path = REPO / "experiments/04_format_robust_sc_and_more_models/scripts/fr_extract.py"
        spec = importlib.util.spec_from_file_location("fr_extract_exp04", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _FR = mod
    return _FR


def matcher():
    """Experiment 03 analyze.py: canon_key, gold_ok, clusters, problem_sc, kendall_D, tau."""
    global _A03
    if _A03 is None:
        path = REPO / "experiments/03_model_level_ranking_sc/scripts/analyze.py"
        spec = importlib.util.spec_from_file_location("a03_for_exp05", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["a03_for_exp05"] = mod
        spec.loader.exec_module(mod)
        _A03 = mod
    return _A03


def verdict_B(tau: float, maxgap: float, p_tau: float) -> str:
    """Part B rule, experiment 04 PREREG, unchanged."""
    if tau < 0.60 or maxgap >= 0.10:
        return "NO"
    if tau >= 0.80 and maxgap < 0.05 and p_tau >= 0.80:
        return "YES"
    return "INCONCLUSIVE"


def apply_variant(text: str, finish: str, variant: str) -> tuple[str | None, str]:
    answer, tier = fr_module().fr_answer(text if text is not None else "")
    if variant == "fr_stop" and tier != "boxed" and finish == "length":
        return None, "none"
    if variant == "fr12" and tier in ("math", "number"):
        return None, "none"
    return answer, tier


def official_correct(gold: str, extracted: str | None) -> int:
    if extracted is None:
        return 0
    return int(frozen.grade_normalize(extracted) == gold)


def draw_indices(n_problems: int, boot: int, seed: int, record_path: Path | None) -> np.ndarray:
    """Write the seed, then draw one (boot, n_problems) index array shared by every model."""
    payload = {
        "seed": int(seed),
        "bootstrap": int(boot),
        "n_problems": int(n_problems),
        "recorded_before_resample": True,
    }
    if record_path is not None:
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(json.dumps(payload) + "\n")
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_problems, size=(boot, n_problems))


def protocol_complete(n_problems: int, model_ids: list[str], n: int, missing: list) -> bool:
    expected = [m[0] for m in frozen.MODELS]
    return (not missing) and n == N and n_problems == frozen.EXPECTED_N and list(model_ids) == expected


def rank_block(cand: np.ndarray, target: np.ndarray, idxs: np.ndarray, labels: list[str]) -> dict:
    """cand, target: shape (M, P). idxs: shape (boot, P), the same rows for every model."""
    a03 = matcher()
    cm = cand.mean(axis=1)
    tm = target.mean(axis=1)
    pairs = []
    m = len(labels)
    for i in range(m):
        for j in range(i + 1, m):
            if (cm[i] - cm[j]) * (tm[i] - tm[j]) < 0:
                pairs.append({
                    "a": labels[i], "b": labels[j],
                    "gap": float(abs(tm[i] - tm[j])),
                    "cand_gap": float(abs(cm[i] - cm[j])),
                })
    taus = np.empty(len(idxs), dtype=float)
    for b, idx in enumerate(idxs):
        taus[b] = a03.tau(cand[:, idx].mean(axis=1), target[:, idx].mean(axis=1))
    tv = a03.tau(cm, tm)
    maxgap = max((p["gap"] for p in pairs), default=0.0)
    p_tau = float(np.mean(taus >= TAU_BOOT_CUTOFF))
    spearman = _spearman(cm, tm)
    return {
        "M": m,
        "pairs_total": m * (m - 1) // 2,
        "D": a03.kendall_D(cm, tm),
        "tau": tv,
        "spearman": spearman,
        "boot_P_tau_ge_0733": p_tau,
        "tau_ci": [float(np.percentile(taus, 2.5)), float(np.percentile(taus, 97.5))],
        "discordant": pairs,
        "max_discordant_gap": float(maxgap),
        "rule": verdict_B(tv, maxgap, p_tau),
    }


def _spearman(a: np.ndarray, b: np.ndarray):
    from scipy.stats import spearmanr
    if len(a) < 2 or np.unique(a).size < 2 or np.unique(b).size < 2:
        return None
    r = spearmanr(a, b)[0]
    if r != r:
        return None
    return float(r)


def _cache_get(cache: dict, key: str, build):
    if key not in cache:
        cache[key] = build()
    return cache[key]


def score_models(tasks: list[dict], by_model: dict[str, list[list[dict]]], n: int) -> dict:
    """by_model[mid][problem][sample] = {text, finish}. Problems aligned with tasks."""
    a03 = matcher()
    golds = []
    for t in tasks:
        gold = frozen.gsm8k_gold(t["answer"])
        if "gold" in t and t["gold"] != gold:
            raise SystemExit(f"task gold field != grader gold for {t.get('problem_id')}")
        golds.append(gold)
    p = len(tasks)
    variants = ("fr", "fr_stop", "fr12")
    key_cache: dict[str, str] = {}
    gold_cache: dict[str, int] = {}
    per = {}
    tiers = {}
    truncated = {}
    for mid, rows in by_model.items():
        if len(rows) != p:
            raise SystemExit(f"{mid} has {len(rows)} problems, tasks have {p}")
        trunc = []
        tier_counts = {k: 0 for k in ("boxed", "phrase", "math", "number", "none")}
        per[mid] = {}
        for variant in variants:
            sc = np.zeros(p)
            p1 = np.zeros(p)
            off = np.zeros(p)
            for pi, samples in enumerate(rows):
                if len(samples) < n:
                    raise SystemExit(f"{mid} problem {pi} has {len(samples)} samples, want {n}")
                use = samples[:n]
                extracted = [apply_variant(s["text"], s.get("finish") or "stop", variant) for s in use]
                if variant == "fr":
                    for s in use:
                        trunc.append(1.0 if (s.get("finish") or "stop") == "length" else 0.0)
                    for _a, tier in extracted:
                        tier_counts[tier] += 1
                keys = []
                for ans, _tier in extracted:
                    if ans is None:
                        keys.append(None)
                    else:
                        keys.append(_cache_get(key_cache, "norm\x00" + ans, lambda a=ans: a03.canon_key("norm", a)))
                sc[pi] = a03.problem_sc(a03.clusters(keys))
                hits = []
                ohits = []
                for ans, _tier in extracted:
                    if ans is None:
                        hits.append(0)
                        ohits.append(0)
                    else:
                        g = golds[pi]
                        hits.append(_cache_get(gold_cache, g + "\x00" + ans, lambda gg=g, a=ans: a03.gold_ok(gg, a)))
                        ohits.append(official_correct(g, ans))
                p1[pi] = float(np.mean(hits))
                off[pi] = float(np.mean(ohits))
            per[mid][variant] = {"sc": sc, "p1": p1, "official": off}
        total = sum(tier_counts.values())
        tiers[mid] = {k: (v / total if total else 0.0) for k, v in tier_counts.items()}
        truncated[mid] = float(np.mean(trunc)) if trunc else 0.0
    return {"per": per, "tiers": tiers, "truncated": truncated, "golds": golds}


def analyze_problems(tasks, by_model, out_dir: Path, boot: int = BOOT, seed: int = SEED, n: int = N) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = list(by_model)
    missing = []
    idxs = draw_indices(len(tasks), boot, seed, out_dir / "bootstrap_seed.json")
    scored = score_models(tasks, by_model, n)
    per = scored["per"]

    def matrix(variant: str, field: str) -> np.ndarray:
        return np.stack([per[m][variant][field] for m in labels], axis=0)

    primary = rank_block(matrix("fr", "sc"), matrix("fr", "p1"), idxs, labels)
    secondary = rank_block(matrix("fr", "sc"), matrix("fr", "official"), idxs, labels)
    secondary["edits_primary"] = False
    s1 = rank_block(matrix("fr_stop", "sc"), matrix("fr_stop", "p1"), idxs, labels)
    s2 = rank_block(matrix("fr12", "sc"), matrix("fr12", "p1"), idxs, labels)
    s1["role"] = "descriptive"
    s2["role"] = "descriptive"
    table = {}
    for mid in labels:
        fr = per[mid]["fr"]
        table[mid] = {
            "sc_fr": float(fr["sc"].mean()),
            "p1_fr": float(fr["p1"].mean()),
            "gsm8k_official": float(fr["official"].mean()),
            "truncated": scored["truncated"][mid],
            "tiers": scored["tiers"][mid],
            "sc_s1": float(per[mid]["fr_stop"]["sc"].mean()),
            "p1_s1": float(per[mid]["fr_stop"]["p1"].mean()),
            "sc_s2": float(per[mid]["fr12"]["sc"].mean()),
            "p1_s2": float(per[mid]["fr12"]["p1"].mean()),
        }
    complete = protocol_complete(len(tasks), labels, n, missing)
    result = {
        "seed": seed,
        "bootstrap": boot,
        "n": n,
        "n_problems": len(tasks),
        "task_sha256": frozen.task_sha256(tasks) if len(tasks) == frozen.EXPECTED_N else None,
        "dataset_revision": frozen.DATASET_REVISION,
        "models": labels,
        "labels": {m[0]: m[1] for m in frozen.MODELS},
        "missing": missing,
        "complete": complete,
        "table": table,
        "ranking": {"primary": primary, "secondary": secondary, "S1": s1, "S2": s2},
        "verdict_primary": primary["rule"] if complete else None,
        "verdict_secondary": secondary["rule"] if complete else None,
    }
    (out_dir / "results.json").write_text(json.dumps(result, indent=1) + "\n")
    (out_dir / "tables.md").write_text(render_tables(result))
    write_figure(result, out_dir / "model_rank.png")
    return result


def render_tables(result: dict) -> str:
    labels = result["labels"]
    lines = [
        "# Experiment 05 tables (generated by scripts/analyze_gsm8k.py)",
        "",
        f"n = {result['n']} samples x {result['n_problems']} GSM8K test problems per model.",
        f"complete = {result['complete']}. Verdicts are null unless complete is true.",
        "",
        "| model | pass@1 fr | GSM8K official | SC fr | boxed | phrase | math | number | none | truncated |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    order = sorted(result["models"], key=lambda m: -result["table"][m]["p1_fr"])
    for mid in order:
        t = result["table"][mid]
        ti = t["tiers"]
        name = labels.get(mid, mid)
        lines.append(
            f"| {name} | {t['p1_fr']:.3f} | {t['gsm8k_official']:.3f} | {t['sc_fr']:.3f} | "
            f"{ti['boxed']:.2f} | {ti['phrase']:.2f} | {ti['math']:.2f} | {ti['number']:.2f} | "
            f"{ti['none']:.2f} | {t['truncated']:.2f} |"
        )
    lines += ["", "## Rankings", "",
              "| comparison | role | M | D | tau | boot P(tau>=0.733) | max discordant gap | rule | quoted verdict |",
              "|---|---|---:|---:|---:|---:|---:|---|---|"]
    quoted = {
        "primary": result["verdict_primary"],
        "secondary": result["verdict_secondary"],
        "S1": None,
        "S2": None,
    }
    for key in ("primary", "secondary", "S1", "S2"):
        r = result["ranking"][key]
        role = "endpoint" if key in ("primary", "secondary") else "descriptive"
        q = quoted[key]
        lines.append(
            f"| {key} | {role} | {r['M']} | {r['D']}/{r['pairs_total']} | {r['tau']:.3f} | "
            f"{r['boot_P_tau_ge_0733']:.2f} | {r['max_discordant_gap']:.3f} | {r['rule']} | {q} |"
        )
        disc = r["discordant"]
        if disc:
            bits = ", ".join(
                f"{labels.get(p['a'], p['a'])} vs {labels.get(p['b'], p['b'])} (gap {p['gap']:.3f})"
                for p in disc
            )
        else:
            bits = "none"
        lines.append("")
        lines.append(f"Discordant pairs ({key}): {bits}")
    lines.append("")
    return "\n".join(lines)


def write_figure(result: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = result["labels"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    specs = (("p1_fr", "format-robust pass@1"), ("gsm8k_official", "official GSM8K accuracy"))
    for ax, (key, xlabel) in zip(axes, specs):
        for mid in result["models"]:
            t = result["table"][mid]
            ax.scatter(t[key], t["sc_fr"], color="C0")
            ax.annotate(labels.get(mid, mid).split(" ")[0], (t[key], t["sc_fr"]), fontsize=7)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("format-robust SC")
        ax.grid(True)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def load_model_file(path: Path, pids: list[str], n: int):
    rows = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        rows[str(r["problem_id"])] = r
    absent = [pid for pid in pids if pid not in rows]
    if absent:
        return None, f"missing {len(absent)} problems"
    out = []
    for pid in pids:
        r = rows[pid]
        samples = r["samples"]
        finish = r.get("finish") or ["stop"] * len(samples)
        if len(samples) < n:
            return None, f"only {len(samples)} samples"
        problem = []
        for i in range(n):
            fin = finish[i] if i < len(finish) and finish[i] else "stop"
            problem.append({"text": samples[i], "finish": fin})
        out.append(problem)
    return out, None


def main(argv: list[str] | None = None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Experiment 05 GSM8K analysis (CPU, no paid API)")
    ap.add_argument("--tasks", default=str(DEFAULT_ROOT / "tasks_gsm8k_test.jsonl"))
    ap.add_argument("--gen", default=str(DEFAULT_ROOT / "gen"))
    ap.add_argument("--out", default=str(DEFAULT_ROOT / "results"))
    args = ap.parse_args(argv)
    tasks = frozen.read_jsonl(Path(args.tasks))
    frozen.assert_frozen(tasks)
    pids = [str(t["problem_id"]) for t in tasks]
    by_model = {}
    missing = []
    ordered = []
    for mid, _label, hf, _tp in frozen.MODELS:
        path = frozen.out_path_for(Path(args.gen), hf)
        ordered.append(mid)
        if not path.exists():
            missing.append(mid)
            continue
        loaded, err = load_model_file(path, pids, N)
        if err:
            missing.append(f"{mid} ({err})")
            continue
        by_model[mid] = loaded
    out = Path(args.out)
    if len(by_model) < 2:
        out.mkdir(parents=True, exist_ok=True)
        draw_indices(len(tasks), BOOT, SEED, out / "bootstrap_seed.json")
        payload = {
            "seed": SEED, "bootstrap": BOOT, "n": N, "n_problems": len(tasks),
            "complete": False, "missing": missing, "models": list(by_model),
            "verdict_primary": None, "verdict_secondary": None,
        }
        (out / "results.json").write_text(json.dumps(payload, indent=1) + "\n")
        print("not enough models to rank", missing, flush=True)
        return
    # Preserve the frozen model order among the models that loaded.
    by_model = {mid: by_model[mid] for mid in ordered if mid in by_model}
    result = analyze_problems(tasks, by_model, out, boot=BOOT, seed=SEED, n=N)
    result["missing"] = missing
    result["complete"] = protocol_complete(len(tasks), list(by_model), N, missing)
    result["verdict_primary"] = result["ranking"]["primary"]["rule"] if result["complete"] else None
    result["verdict_secondary"] = result["ranking"]["secondary"]["rule"] if result["complete"] else None
    (out / "results.json").write_text(json.dumps(result, indent=1) + "\n")
    (out / "tables.md").write_text(render_tables(result))
    print(
        f"complete={result['complete']} primary={result['verdict_primary']} "
        f"secondary={result['verdict_secondary']} missing={missing}",
        flush=True,
    )


if __name__ == "__main__":
    main()
