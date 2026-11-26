"""CPU checks for experiment 05. Synthetic fixtures only, plus the frozen GSM8K item list.

No generation and no fallback number on real samples.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import analyze_gsm8k as az  # noqa: E402
import generate_gsm8k as gz  # noqa: E402


def test_modules_import_without_vllm():
    assert "vllm" not in sys.modules


def test_prompt_and_sampler_match_experiment_04():
    src = (ROOT / "experiments/04_format_robust_sc_and_more_models/scripts/generate.py").read_text()
    src05 = (SCRIPTS / "generate_gsm8k.py").read_text()
    # Source text stores the escape as two backslashes; the runtime prompt has one.
    snippet = "then give the final answer in \\\\boxed{}."
    assert snippet in src
    assert snippet in src05
    assert gz.prompt_of("Q") == (
        "Solve the following math problem. Show your reasoning step by step, "
        "then give the final answer in \\boxed{}.\n\nQ"
    )
    assert (gz.TEMPERATURE, gz.TOP_P, gz.MAX_TOKENS, gz.SEED, gz.N_DEFAULT) == (1.0, 0.95, 1024, 0, 16)
    gen_src = (SCRIPTS / "generate_gsm8k.py").read_text()
    assert "SamplingParams(n=args.n, max_tokens=MAX_TOKENS, temperature=TEMPERATURE, top_p=TOP_P, seed=SEED)" in gen_src
    assert gz.thinking_kwargs("Qwen/Qwen3-8B") == {"enable_thinking": False}
    assert gz.thinking_kwargs("Qwen/Qwen3.5-4B") == {"enable_thinking": False}
    assert gz.thinking_kwargs("Qwen/Qwen2.5-7B-Instruct") == {}


def test_model_ids_match_experiment_04_results():
    recorded = json.loads(
        (ROOT / "experiments/04_format_robust_sc_and_more_models/results/results.json").read_text()
    )
    assert [m[0] for m in gz.MODELS] == recorded["models"]
    assert {m[0]: m[1] for m in gz.MODELS} == recorded["labels"]
    assert gz.MODELS[gz.MODELS.index(next(m for m in gz.MODELS if m[0] == "qwen3_1p7b"))][3] == 1
    assert all(tp == 2 for _i, _l, hf, tp in gz.MODELS if hf in gz.TP2_IDS)
    assert "Qwen/Qwen3-1.7B" not in gz.TP2_IDS
    assert len(gz.TP2_IDS) == 7


def test_prereg_locks_next_protocol():
    pre = (ROOT / "experiments/05_gsm8k_format_robust_sc/PREREG.md").read_text()
    nxt = (ROOT / "NEXT.md").read_text()
    assert "On the GSM8K test split, does format-robust SC rank the same ten models as format-robust pass@1?" in pre
    assert "YES: Kendall $\\tau \\ge 0.80$, every discordant format-robust pass@1 gap $< 0.05$, and $P(\\tau \\ge 0.733) \\ge 0.80$." in pre
    assert "NO: $\\tau < 0.60$, or any discordant gap $\\ge 0.10$." in pre
    assert "INCONCLUSIVE otherwise." in pre
    assert "1319" in pre
    assert gz.EXPECTED_SHA256 in pre
    assert gz.DATASET_REVISION in pre
    assert "before any GSM8K" in pre
    for _i, _l, hf, _tp in gz.MODELS:
        assert hf in pre
    assert "fr_extract.py" in nxt and "fr_extract.py" in pre
    assert az.BOOT == 2000 and az.SEED == 20261126 and az.N == 16


def test_launcher_covers_ten_gpus_without_overlap():
    text = (SCRIPTS / "run_mercury2.sh").read_text()
    assert "/lfs/mercury2/0/brando9/judge-free-eval-exp05/" in text
    waves = []
    current = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("gen "):
            body = s.split("&", 1)[0].split()
            gpus = [int(x) for x in body[1].split(",")]
            current.append({"gpus": gpus, "tp": int(body[2]), "hf": body[3], "batch": int(body[4])})
        elif s.startswith("wait_pids "):
            if current:
                waves.append(current)
                current = []
    assert [len(w) for w in waves] == [5, 5]
    seen = []
    for wave in waves:
        used = []
        for job in wave:
            assert job["batch"] == 4
            assert len(job["gpus"]) == job["tp"]
            used.extend(job["gpus"])
            seen.append(job["hf"])
        assert len(used) == len(set(used))
        assert set(used) <= set(range(10))
    assert seen == [m[2] for m in gz.MODELS if m[3] == 2][:5] + [m[2] for m in gz.MODELS if m[3] == 2][5:] + [m[2] for m in gz.MODELS if m[3] == 1]
    by_hf = {hf: tp for _i, _l, hf, tp in gz.MODELS}
    flat = [job for wave in waves for job in wave]
    assert {job["hf"] for job in flat} == set(by_hf)
    for job in flat:
        assert job["tp"] == by_hf[job["hf"]]


def test_gold_normalization_and_frozen_tasks():
    assert gz.gsm8k_gold("calc\n#### 1,024") == "1024"
    assert gz.official_extract_answer("calc\n#### 1,024") == "1024"
    assert gz.grade_normalize(" 1,024 ") == "1024"
    assert gz.grade_normalize("18.0") == "18.0"
    assert gz.official_extract_answer("no marker") == "[invalid]"
    with pytest.raises(ValueError):
        gz.gsm8k_gold("no marker")
    tasks = gz.rows_to_tasks([
        {"question": "q", "answer": "because\n#### 3"},
        {"question": "r", "answer": "#### 4"},
    ])
    assert tasks[0]["problem_id"] == "0" and tasks[0]["gold"] == "3"
    with pytest.raises(SystemExit):
        gz.assert_frozen(tasks)
    loaded = gz.load_frozen_tasks()
    assert len(loaded) == 1319
    assert gz.task_sha256(loaded) == gz.EXPECTED_SHA256
    assert all(t["gold"].lstrip("-").isdigit() for t in loaded)


def test_resume_skips_done_problems(tmp_path):
    tasks = [{"problem_id": "0", "problem": "a"}, {"problem_id": "1", "problem": "b"}]
    out = tmp_path / "out.jsonl"
    out.write_text(json.dumps({"problem_id": "0", "samples": []}) + "\n" + "{bad\n")
    left = gz.remaining(tasks, out)
    assert [t["problem_id"] for t in left] == ["1"]


def test_require_tp_rejects_one_gpu_for_8b_and_two_for_1_7b():
    with pytest.raises(SystemExit):
        gz.require_tp("Qwen/Qwen3-8B", 1)
    with pytest.raises(SystemExit):
        gz.require_tp("Qwen/Qwen3-1.7B", 2)
    gz.require_tp("Qwen/Qwen3-1.7B", 1)
    gz.require_tp("meta-llama/Llama-3.1-8B-Instruct", 2)


def test_verdict_boundaries_match_part_b():
    assert az.verdict_B(0.80, 0.049, 0.80) == "YES"
    assert az.verdict_B(1.0, 0.0, 1.0) == "YES"
    assert az.verdict_B(0.80, 0.05, 0.80) == "INCONCLUSIVE"
    assert az.verdict_B(0.799, 0.0, 1.0) == "INCONCLUSIVE"
    assert az.verdict_B(0.80, 0.0, 0.799) == "INCONCLUSIVE"
    assert az.verdict_B(0.60, 0.099, 0.0) == "INCONCLUSIVE"
    assert az.verdict_B(0.599, 0.0, 1.0) == "NO"
    assert az.verdict_B(1.0, 0.10, 1.0) == "NO"
    assert az.verdict_B(0.0, 0.0, 0.0) == "NO"


def test_extractor_is_the_experiment_04_file():
    mod = az.fr_module()
    assert mod.__file__.endswith("experiments/04_format_robust_sc_and_more_models/scripts/fr_extract.py")
    assert mod.fr_answer(r"\boxed{4}") == ("4", "boxed")
    assert mod.fr_answer("The answer is 7")[1] == "phrase"
    assert mod.fr_answer("we have $9$")[1] == "math"
    assert mod.fr_answer("it is 6")[1] == "number"
    assert mod.fr_answer("no digits") == (None, "none")


def test_unextractable_scores_zero_and_sc_matches_experiment_03():
    a03 = az.matcher()
    keys = ["N:5.0", "N:5.0", None, None]
    sc = a03.problem_sc(a03.clusters(keys))
    assert sc == pytest.approx(2 / 12)
    assert a03.problem_sc(a03.clusters([None, None])) == 0.0
    assert a03.gold_ok("5", "5.0") == 1
    assert a03.gold_ok("5", "6") == 0
    assert az.official_correct("5", "5.0") == 0
    assert az.official_correct("5", " 5 ") == 1
    assert az.official_correct("1024", "1,024") == 1
    assert az.official_correct("5", None) == 0


def _task(gold: str, pid: str) -> dict:
    return {"problem_id": pid, "problem": f"q{pid}", "question": f"q{pid}",
            "answer": f"work\n#### {gold}", "gold": gold}


def _boxed(text: str, finish: str = "stop") -> dict:
    return {"text": text, "finish": finish}


def test_primary_yes_secondary_no_and_seed_before_resample(tmp_path):
    tasks = [_task("5", "0")]
    by_model = {
        "A": [[_boxed(r"\boxed{5.0}"), _boxed(r"\boxed{5.0}"), _boxed(r"\boxed{5.0}"), _boxed(r"\boxed{5.0}")]],
        "B": [[_boxed(r"\boxed{5}"), _boxed(r"\boxed{5}"), _boxed(r"\boxed{7}"), _boxed(r"\boxed{8}")]],
        "C": [[_boxed("no digits"), _boxed("no digits"), _boxed("no digits"), _boxed("no digits")]],
    }
    result = az.analyze_problems(tasks, by_model, tmp_path, boot=32, seed=20261126, n=4)
    seed_doc = json.loads((tmp_path / "bootstrap_seed.json").read_text())
    assert seed_doc["recorded_before_resample"] is True
    assert seed_doc["seed"] == 20261126
    fresh = np.random.default_rng(20261126).integers(0, 1, size=(32, 1))
    assert seed_doc["n_problems"] == 1
    assert fresh.shape == (32, 1)
    primary = result["ranking"]["primary"]
    secondary = result["ranking"]["secondary"]
    assert primary["rule"] == "YES"
    assert secondary["rule"] == "NO"
    assert secondary["max_discordant_gap"] == pytest.approx(0.5)
    assert secondary["edits_primary"] is False
    assert result["verdict_primary"] is None
    assert result["complete"] is False
    assert result["table"]["A"]["p1_fr"] == pytest.approx(1.0)
    assert result["table"]["A"]["gsm8k_official"] == pytest.approx(0.0)
    assert result["table"]["B"]["sc_fr"] == pytest.approx(1 / 6)
    assert result["table"]["C"]["sc_fr"] == pytest.approx(0.0)
    assert (tmp_path / "results.json").exists()
    assert (tmp_path / "tables.md").exists()
    assert (tmp_path / "model_rank.png").exists()
    # One shared resample stream: redrawing with the recorded seed matches the generator used inside draw_indices.
    redraw = az.draw_indices(1, 32, 20261126, None)
    assert np.array_equal(redraw, fresh)


def test_s1_drops_truncated_fallback_and_keeps_boxed(tmp_path):
    tasks = [_task("5", "0")]
    by_model = {
        "A": [[
            _boxed(r"\boxed{5}", "length"),
            _boxed("The answer is 5", "length"),
        ]],
        "B": [[
            _boxed(r"\boxed{5}", "stop"),
            _boxed(r"\boxed{5}", "stop"),
        ]],
    }
    result = az.analyze_problems(tasks, by_model, tmp_path, boot=8, seed=1, n=2)
    assert result["table"]["A"]["truncated"] == pytest.approx(1.0)
    assert result["table"]["A"]["p1_fr"] == pytest.approx(1.0)
    assert result["table"]["A"]["p1_s1"] == pytest.approx(0.5)
    assert result["table"]["B"]["truncated"] == pytest.approx(0.0)
    assert result["table"]["B"]["p1_s1"] == pytest.approx(1.0)


def test_s2_keeps_phrase_and_drops_math_and_number(tmp_path):
    tasks = [_task("5", "0")]
    by_model = {
        "A": [[
            _boxed("The answer is 5"),
            _boxed("we have $5$"),
        ]],
        "B": [[
            _boxed("The answer is 5"),
            _boxed("it is 5"),
        ]],
    }
    result = az.analyze_problems(tasks, by_model, tmp_path, boot=4, seed=2, n=2)
    assert result["table"]["A"]["tiers"]["phrase"] == pytest.approx(0.5)
    assert result["table"]["A"]["tiers"]["math"] == pytest.approx(0.5)
    assert result["table"]["A"]["p1_fr"] == pytest.approx(1.0)
    assert result["table"]["A"]["p1_s2"] == pytest.approx(0.5)
    assert result["table"]["B"]["tiers"]["number"] == pytest.approx(0.5)
    assert result["table"]["B"]["p1_s2"] == pytest.approx(0.5)
    assert result["ranking"]["S1"]["role"] == "descriptive"
    assert result["ranking"]["S2"]["role"] == "descriptive"


def test_shared_bootstrap_and_discordant_gap_uses_the_target(tmp_path):
    # Two problems, identical rows, so every shared resample has the same means.
    # hi agrees with itself and with gold. lo's two samples disagree and are wrong, so SC and pass@1 both fall.
    tasks = [_task("1", "0"), _task("1", "1")]
    by_model = {
        "hi": [[_boxed(r"\boxed{1}"), _boxed(r"\boxed{1}")] for _ in range(2)],
        "lo": [[_boxed(r"\boxed{0}"), _boxed(r"\boxed{2}")] for _ in range(2)],
    }
    result = az.analyze_problems(tasks, by_model, tmp_path, boot=20, seed=7, n=2)
    assert result["ranking"]["primary"]["rule"] == "YES"
    assert result["ranking"]["primary"]["D"] == 0
    assert result["ranking"]["primary"]["tau"] == pytest.approx(1.0)
    assert result["ranking"]["primary"]["boot_P_tau_ge_0733"] == pytest.approx(1.0)
    assert result["table"]["hi"]["sc_fr"] == pytest.approx(1.0)
    assert result["table"]["lo"]["sc_fr"] == pytest.approx(0.0)
    # Discordant gap is the target gap (pass@1), not the SC gap.
    flip = {
        "steady": [[_boxed(r"\boxed{1}"), _boxed(r"\boxed{1}")]],
        "noisy": [[_boxed(r"\boxed{9}"), _boxed(r"\boxed{8}")]],
    }
    flipped = az.analyze_problems([_task("9", "0")], flip, tmp_path / "flip", boot=10, seed=7, n=2)
    pair = flipped["ranking"]["primary"]["discordant"]
    assert len(pair) == 1
    assert pair[0]["gap"] == pytest.approx(0.5)
    assert pair[0]["cand_gap"] == pytest.approx(1.0)
    assert flipped["ranking"]["primary"]["rule"] == "NO"
    assert az.protocol_complete(1319, [m[0] for m in gz.MODELS], 16, []) is True
    assert az.protocol_complete(1319, ["hi", "lo"], 16, []) is False
    assert az.protocol_complete(1318, [m[0] for m in gz.MODELS], 16, []) is False


def test_load_model_file_uses_first_n_and_missing_finish_is_stop(tmp_path):
    path = tmp_path / "bon_gsm8k__Qwen__Qwen3-4B.jsonl"
    row = {
        "problem_id": "0",
        "samples": [r"\boxed{1}", r"\boxed{2}", r"\boxed{3}"],
        "finish": ["stop", None],
        "answer": "#### 1",
        "gold": "1",
    }
    path.write_text(json.dumps(row) + "\n")
    loaded, err = az.load_model_file(path, ["0"], 2)
    assert err is None
    assert loaded[0][0]["text"] == r"\boxed{1}"
    assert loaded[0][1]["finish"] == "stop"
    assert len(loaded[0]) == 2
    _none, err = az.load_model_file(path, ["0", "1"], 2)
    assert err.startswith("missing")


def test_gate_nulls_verdict_on_partial_main(tmp_path, monkeypatch):
    tasks = [_task("1", "0")]
    # Not the frozen 1319, so assert_frozen must refuse before any ranking number.
    task_path = tmp_path / "tasks.jsonl"
    task_path.write_text(json.dumps(tasks[0]) + "\n")
    with pytest.raises(SystemExit):
        az.main(["--tasks", str(task_path), "--gen", str(tmp_path), "--out", str(tmp_path / "out")])
