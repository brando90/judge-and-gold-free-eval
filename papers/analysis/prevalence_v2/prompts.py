# Exact prompts for the prevalence v2 audit. PROTOCOL.md quotes these strings verbatim.
# DEFINITIONS reuses the v1 label definitions (papers/analysis/prevalence/RESULTS.md) word for word;
# the only addition is the final "Scope" line, which extends the NQ-open rules to the other open-domain sets.

DEFINITIONS = """DEFINITIONS (applied strictly)
- MULTI (k>1): the question as written is satisfied by at least two final answers that are not equivalent (not the same number, expression, or set written differently). Examples: "find a positive integer n such that ...", "give an example of ...", a question genuinely ambiguous between two readings with different correct answers, or a free parameter the question leaves unpinned.
- UNIQUE (k=1): exactly one correct final answer up to equivalence. This includes "find all x" questions whose answer is one set, smallest/largest questions, equivalent forms, and numeric answers within rounding tolerance.
- UNCLEAR: cannot be decided without deep solving, or the question is malformed (missing figure or choices, inconsistent data, undefined symbols).
- Surface-equivalent forms (1/2 vs 0.5, x=3 vs 3) are not MULTI. A wrong reference is not MULTI by itself. Conservative rule: when in doubt, UNIQUE or UNCLEAR.
- Extra NQ-open rules: aliases are not MULTI. MULTI requires genuinely different correct entities, a genuine two-reading ambiguity, or a temporal question whose answer has changed and whose wording fixes no time (temporal items are reported separately). Complete co-author or co-developer sets and fixed-set answers ("who survives", "which aqueducts") count as one answer.
- Rules settled during adjudication: "find the value of x" with two roots is MULTI, because each root satisfies the question as written (not a "find all"). A question whose stated request differs from the quantity the reference answers is UNCLEAR.
- Scope: the extra NQ-open rules apply to every open-domain factual question (people, places, titles, dates, events, records) in any dataset."""

SUBTYPES = """SUBTYPES
- If the label is MULTI, use one of: "multiple_entities" (different correct entities or objects satisfy the question), "ambiguous_reading" (two defensible readings of the question have different correct answers), "temporal" (the answer has changed over time and the wording fixes no time), "multiple_solutions" (a math, science or puzzle question satisfied by several non-equivalent values or objects, such as two roots, an example request, or an unpinned parameter), "other".
- If the label is UNCLEAR, use one of: "malformed", "needs_deep_solving", "unverifiable", "other".
- If the label is UNIQUE, use ""."""

SYSTEM_ANNOTATOR = f"""You are one of two independent annotators in an audit of datasets that grade each question against a single reference answer. For the item you are given, decide whether the question as written admits two or more distinct valid final answers. Apply the definitions below exactly as written. You work independently and do not see any other annotator's labels. Items come from several datasets and are presented one at a time; judge each item on its own.

{DEFINITIONS}

{SUBTYPES}

OUTPUT FORMAT
First write a short reasoning of at most 120 words. Then end the response with one JSON object on its own line and nothing after it; the JSON object is what gets recorded:
{{"label": "MULTI|UNIQUE|UNCLEAR", "alternative": "<a concrete second valid answer if MULTI, else empty>", "subtype": "..."}}"""

SYSTEM_ADJUDICATOR = f"""You are the adjudicator in an audit of datasets that grade each question against a single reference answer. Two independent annotators labeled the item below and disagreed (or one of them failed to produce a label). Decide the final label by applying the definitions below exactly as written. The annotators' reasoning may contain errors; check their claims against the question instead of deferring to either one.

{DEFINITIONS}

{SUBTYPES}

OUTPUT FORMAT
First write a short reasoning of at most 120 words. Then end the response with one JSON object on its own line and nothing after it:
{{"label": "MULTI|UNIQUE|UNCLEAR", "alternative": "<a concrete second valid answer if MULTI, else empty>", "subtype": "...", "reason": "<one sentence stating why this is the final label>"}}"""

SINGLE_ANSWER_NOTE = ("Dataset note: the dataset authors designed these questions to have a single answer. Count MULTI "
                      "only when the question as written admits a different correct entity or a genuinely different reading.")

DATASETS = {
    # v2 datasets
    "simpleqa": {"name": "SimpleQA (test set)", "note": SINGLE_ANSWER_NOTE},
    "browsecomp": {"name": "BrowseComp (test set)", "note": ""},
    "hle": {"name": "Humanity's Last Exam (text-only, exact-match answers)", "note": ""},
    "triviaqa": {"name": "TriviaQA (rc.nocontext, validation)", "note": SINGLE_ANSWER_NOTE},
    "webinstruct": {"name": "WebInstruct-verified (train)", "note": ""},
    # v1 datasets (Pass B relabel)
    "math500": {"name": "MATH-500 (test)", "note": ""},
    "gsm8k": {"name": "GSM8K (test)", "note": ""},
    "deepscaler": {"name": "DeepScaleR-Preview (train)", "note": ""},
    "nqopen": {"name": "Natural Questions open (validation)",
               "note": "Reference format: when the dataset accepts several reference strings, they are separated by ' | '."},
}


def render_item(ds, it):
    meta = DATASETS[ds]
    lines = [f"Dataset: {meta['name']}"]
    if meta["note"]:
        lines.append(meta["note"])
    lines += ["", "Question:", it["question"], "", "Reference answer:", it["reference"]]
    if it.get("aliases"):
        lines += ["", "Reference aliases (also accepted by the dataset):", "; ".join(it["aliases"])]
    return "\n".join(lines)


def render_annotator_block(k, row):
    if row is None or row.get("label") not in ("MULTI", "UNIQUE", "UNCLEAR"):
        return f"Annotator {k} label: (no label: annotation failed)"
    return "\n".join([
        f"Annotator {k} label: {row['label']}",
        f"Annotator {k} subtype: {row.get('subtype', '')}",
        f"Annotator {k} alternative: {row.get('alternative', '')}",
        f"Annotator {k} reasoning:",
        row.get("reasoning", "") or "(none given)",
    ])


def render_adjudication(ds, it, first, second):
    return "\n".join([render_item(ds, it), "", render_annotator_block(1, first), "", render_annotator_block(2, second)])
