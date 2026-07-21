"""Parse a unified-diff patch and separate the tokens that carry the fix (changed content lines) from
the tokens that are copy-through context or diff scaffolding. This backs the SWE-bench "Agentic-TFA"
estimator in docs/agentic-tfa-plan.md: teacher-forcing the whole diff is dominated by unchanged context
lines (trivially copied from the in-context file) and hunk-header line-number arithmetic (format noise),
so the faithful estimator masks TFA to the changed content lines, the analog of the paper's content-token
variant. This module also builds a normalized search/replace edit representation.

A unified-diff line is classified as:
  file_header : 'diff --git', 'index ', '--- ', '+++ '
  hunk_header : '@@ ... @@'
  add         : '+<content>'  (a line the fix introduces)
  del         : '-<content>'  (a line the fix removes)
  context     : ' <content>'  (unchanged, present verbatim in the in-context file)
Only add/del content is the "signal"; everything else is copy-through or scaffolding.
"""
import re

def classify_lines(patch: str):
    out = []
    for ln in patch.splitlines():
        if ln.startswith(("diff --git", "index ", "--- ", "+++ ", "new file", "deleted file", "similarity ", "rename ")):
            out.append(("file_header", ln))
        elif ln.startswith("@@"):
            out.append(("hunk_header", ln))
        elif ln.startswith("+"):
            out.append(("add", ln[1:]))
        elif ln.startswith("-"):
            out.append(("del", ln[1:]))
        else:
            out.append(("context", ln[1:] if ln.startswith(" ") else ln))
    return out

def changed_line_text(patch: str) -> str:
    """The masked TFA target: just the added/removed content lines, in order, newline-joined."""
    return "\n".join(c for t, c in classify_lines(patch) if t in ("add", "del"))

def search_replace_blocks(patch: str):
    """A normalized edit representation: per hunk, (removed_block, added_block), dropping line-number
    arithmetic. Teacher-forcing this instead of the raw diff removes the hunk-header noise."""
    blocks, dels, adds = [], [], []
    def flush():
        if dels or adds:
            blocks.append(("\n".join(dels), "\n".join(adds)))
    for t, c in classify_lines(patch):
        if t == "hunk_header":
            flush(); dels, adds = [], []
        elif t == "del":
            dels.append(c)
        elif t == "add":
            adds.append(c)
        elif t == "file_header":
            flush(); dels, adds = [], []
    flush()
    return blocks

def token_stats(patch: str, tok=None):
    """Token counts by category. If tok is a HF tokenizer, counts real tokens; else counts whitespace
    words as a proxy. Returns dict with changed / context / header / total and the changed fraction."""
    def n(s):
        if not s: return 0
        return len(tok(s, add_special_tokens=False)["input_ids"]) if tok is not None else len(s.split())
    cat = {"add": 0, "del": 0, "context": 0, "file_header": 0, "hunk_header": 0}
    for t, c in classify_lines(patch):
        cat[t] += n(c)
    changed = cat["add"] + cat["del"]
    context = cat["context"]
    header = cat["file_header"] + cat["hunk_header"]
    total = changed + context + header
    return dict(changed=changed, context=context, header=header, total=total,
                changed_frac=(changed / total if total else 0.0))
