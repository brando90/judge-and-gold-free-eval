# Code-execution oracle for WS5 (non-math). Runs candidate code against the benchmark's own unit tests in
# an isolated subprocess with a wall-clock timeout, and returns pass/fail. This is the deterministic
# correctness signal for code, the analog of Math-Verify for math. HumanEval and MBPP are benign coding
# tasks; still, the code is untrusted model output, so it runs in a separate process (never exec'd in-proc)
# with a timeout and no argv, and the temp file is always removed.
import os, sys, subprocess, tempfile


def _run(src: str, timeout: float = 12.0) -> bool:
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(src)
        r = subprocess.run([sys.executable, path], capture_output=True, timeout=timeout,
                           env={"PYTHONHASHSEED": "0", "PATH": os.environ.get("PATH", "")})
        return r.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False
    finally:
        try: os.unlink(path)
        except OSError: pass


def humaneval_pass(prompt: str, completion: str, test: str, entry_point: str, timeout: float = 12.0) -> bool:
    # HumanEval: prompt = signature+docstring, completion = function body, test defines check(candidate).
    src = f"{prompt}{completion}\n{test}\ncheck({entry_point})\n"
    return _run(src, timeout)


def mbpp_pass(code: str, test_list, timeout: float = 12.0) -> bool:
    # MBPP: code = full solution, test_list = assert strings referencing the function by name.
    src = code + "\n" + "\n".join(test_list) + "\n"
    return _run(src, timeout)


def code_correct(row: dict, completion: str, timeout: float = 12.0) -> bool:
    """Dataset-agnostic entry: judge a model completion for one code problem."""
    if row.get("_code") == "humaneval":
        return humaneval_pass(row["question"], completion, row["_test"], row["_entry"], timeout)
    if row.get("_code") == "mbpp":
        return mbpp_pass(completion, row["_test_list"], timeout)
    raise ValueError("not a code row")
