# GPU-free derisk for the SWE-bench arm of docs/agentic-tfa-plan.md: across all SWE-bench Verified gold
# patches, how much of a diff is the fix (changed +/- content lines) versus copy-through context and
# hunk/path headers? If context+header dominates, whole-diff teacher-forcing is mostly trivial copying
# and the plan's masked (changed-line-only) estimator is the right one. Uses the real Qwen2.5-Coder
# tokenizer for token-accurate counts.
import numpy as np
from datasets import load_dataset
from tfa.diff_mask import token_stats, changed_line_text, classify_lines

def main():
    tok = None
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-7B-Instruct")
        unit = "tokens (Qwen2.5-Coder)"
    except Exception as e:
        print("tokenizer unavailable, using whitespace-word proxy:", e); unit = "words"

    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    rows = [token_stats(r["patch"], tok) for r in ds]
    cf = np.array([x["changed_frac"] for x in rows])
    changed = np.array([x["changed"] for x in rows])
    total = np.array([x["total"] for x in rows])
    nfiles = np.array([sum(1 for t, _ in classify_lines(r["patch"]) if t == "file_header" and _.startswith("diff --git")) for r in ds])

    print(f"SWE-bench Verified gold patches: n={len(ds)}   unit={unit}")
    print(f"  whole-diff size:        median {np.median(total):.0f}, p90 {np.percentile(total,90):.0f} {unit}")
    print(f"  CHANGED (+/-) content:  median {np.median(changed):.0f}, p90 {np.percentile(changed,90):.0f} {unit}")
    print(f"  changed fraction of diff: median {np.median(cf):.2f}, mean {cf.mean():.2f}  "
          f"(so ~{100*(1-np.median(cf)):.0f}% of the median diff is copy-through context + headers)")
    print(f"  patches touching >1 file: {100*np.mean(nfiles>1):.0f}%   (context-length / oracle-file spread)")
    print(f"  changed content <= 40 {unit}: {100*np.mean(changed<=40):.0f}% of patches "
          f"(short signal, so mask precision matters)")

if __name__ == "__main__":
    main()
