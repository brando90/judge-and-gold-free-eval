#!/usr/bin/env python3
r"""Experiment 04: format-robust answer extraction (frozen in PREREG.md before any experiment-04 number was computed).

fr_answer(text) -> (answer or None, tier) with tier in {"boxed", "phrase", "math", "number", "none"}:
  1. boxed : the last \boxed{...} (experiment 03's extract_boxed). Unchanged.
  2. phrase: no box. The text after the LAST match of "final answer", "the answer is", "answer:" (case-insensitive), cut at the
             first line break; if that span holds math ($..$, \(..\), \[..\], $$..$$) the LAST math span of it, else the span
             stripped of markdown `*`, a trailing period and surrounding spaces, when non-empty and at most 60 characters.
  3. math  : no phrase. The LAST math span of the whole text ($..$, \(..\), \[..\], $$..$$); when it holds "=" the part after the
             last "=" (a trailing "\approx"-style span is not special-cased).
  4. number: no math span. The last number token (-?digits, optional decimal or a/b fraction, thousands commas removed).
  5. none  : nothing found.
Pure string code, no model, no gold.
"""
import importlib.util, re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("boxed", _REPO / "experiments/tfa-vs-judge/tfa/boxed.py")
_boxed = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_boxed)
extract_boxed = _boxed.extract_boxed

_MATH = re.compile(r"\$\$(.+?)\$\$|\\\[(.+?)\\\]|\\\((.+?)\\\)|\$([^$\n]+?)\$", re.S)
_PHRASE = re.compile(r"(final answer|the answer is|answer\s*:)", re.I)
_NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?(?:/\d+)?")


def _last_math(s):
    last = None
    for m in _MATH.finditer(s):
        g = next((x for x in m.groups() if x is not None), None)
        if g is not None and g.strip():
            last = g.strip()
    return last


def _after_eq(t):
    return t.rsplit("=", 1)[1].strip() if "=" in t else t


def fr_answer(text):
    b = extract_boxed(text)
    if b:
        return b, "boxed"
    ms = list(_PHRASE.finditer(text))
    if ms:
        # cut at the first non-empty line after the match (the answer may sit on the next line after "Final Answer")
        lines = [l for l in text[ms[-1].end():].split("\n") if l.strip(" *:\t")]
        span = lines[0] if lines else ""
        mm = _last_math(span)
        if mm:
            return _after_eq(mm), "phrase"
        t = span.replace("*", "").strip().rstrip(".").strip(" :")
        if t and len(t) <= 60:
            return t, "phrase"
    mm = _last_math(text)
    if mm:
        return _after_eq(mm), "math"
    nums = _NUM.findall(text)
    if nums:
        return nums[-1].replace(",", ""), "number"
    return None, "none"
