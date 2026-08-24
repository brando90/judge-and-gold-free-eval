# Stronger matching baselines for Paper B (external-review demand: the grading null must not
# rest on strawman metrics). Adds four modern/serious similarity signals to the five already
# reported, scored against the same anchors:
#   sympy_equiv   symbolic equivalence of the extracted final answer with the gold answer
#                 (math anchor): the strongest possible "matching" signal for final answers
#   nli_entail    entailment probability that the gold solution follows from the candidate
#                 (cross-encoder NLI, run locally)
#   embed_e5      cosine similarity under a modern retrieval embedder (E5), not the older
#                 sentence encoder already reported
#   ast_sim       (code) tree-edit similarity between candidate and canonical solution ASTs
# Reported exactly like the existing metrics: Pearson with human soundness on the 60-item
# math anchor (and with executed tests on the 492 code traces where applicable), bootstrap CIs.
# Run from experiments/tfa-vs-judge.
import ast
import difflib
import json
import re
import sys

import numpy as np

rng = np.random.default_rng(0)


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def bci(x, y, B=2000):
    x, y = np.asarray(x, float), np.asarray(y, float)
    idx = np.arange(len(x))
    vs = []
    for _ in range(B):
        i = rng.choice(idx, len(idx))
        if len(set(y[i])) < 2 or len(set(x[i])) < 2:
            continue
        vs.append(pearson(x[i], y[i]))
    return [round(float(np.percentile(vs, 2.5)), 2), round(float(np.percentile(vs, 97.5)), 2)]


def extract_boxed(t):
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, d = i + 7, 1
    while j < len(t) and d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1]


out = {}

# ---------------------------------------------------------------- math anchor
labs = [r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
        if r.get("soundness") not in (None, "")]
traces = {r["id"]: r for r in (json.loads(l) for l in open("human_eval/traces_to_label.jsonl"))}

# (a) symbolic equivalence of final answers
try:
    from sympy import simplify
    from sympy.parsing.latex import parse_latex
    HAVE_SYMPY = True
except Exception:
    HAVE_SYMPY = False


def sym_equiv(a, b):
    if a is None or b is None:
        return 0.0
    a, b = a.strip(), b.strip()
    if a == b:
        return 1.0
    if not HAVE_SYMPY:
        return 0.0
    try:
        ea, eb = parse_latex(a), parse_latex(b)
        return 1.0 if simplify(ea - eb) == 0 else 0.0
    except Exception:
        return 0.0


rows = []
for L in labs:
    t = traces[L["id"]]
    cand = extract_boxed(t["trace"])
    gold = t.get("gold_answer") or extract_boxed(t["gold_solution"])
    rows.append((sym_equiv(cand, gold), float(L["soundness"])))
x, s = zip(*rows)
out["sympy_equiv_math"] = dict(n=len(rows), r=round(pearson(x, s), 2), ci=bci(x, s),
                               note="symbolic equivalence of extracted final answers, "
                                    "sympy where parseable else string identity")

# (b) modern embedding similarity (E5) and (c) NLI entailment, both local
try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    emb = SentenceTransformer("intfloat/e5-base-v2")
    ce = CrossEncoder("cross-encoder/nli-deberta-v3-base")
    HAVE_ST = True
except Exception as e:
    print("[warn] sentence-transformers unavailable:", str(e)[:120])
    HAVE_ST = False

if HAVE_ST:
    cands = ["query: " + traces[L["id"]]["trace"][:4000] for L in labs]
    golds = ["passage: " + traces[L["id"]]["gold_solution"][:4000] for L in labs]
    ec = emb.encode(cands, normalize_embeddings=True, show_progress_bar=False)
    eg = emb.encode(golds, normalize_embeddings=True, show_progress_bar=False)
    sim = (ec * eg).sum(1)
    s = [float(L["soundness"]) for L in labs]
    out["embed_e5_math"] = dict(n=len(s), r=round(pearson(sim, s), 2), ci=bci(sim, s),
                                note="E5-base-v2 cosine, candidate trace vs gold solution")
    pairs = [(traces[L["id"]]["trace"][:2000], traces[L["id"]]["gold_solution"][:2000])
             for L in labs]
    logits = ce.predict(pairs, show_progress_bar=False)
    ent = np.exp(logits[:, 1]) / np.exp(logits).sum(1)  # entailment prob
    out["nli_entail_math"] = dict(n=len(s), r=round(pearson(ent, s), 2), ci=bci(ent, s),
                                  note="DeBERTa NLI entailment probability, candidate -> gold")

# ---------------------------------------------------------------- code anchor
import glob
import os

tests = {}
for f in glob.glob("runs/code_traces_scored_v2/*.jsonl"):
    for l in open(f):
        r = json.loads(l)
        tests[(r["model"], r["problem_id"])] = r["test_pass"]
ctr = []
for f in glob.glob("runs/code_traces_v2/*.jsonl"):
    for l in open(f):
        r = json.loads(l)
        if (r["model"], r["problem_id"]) in tests:
            ctr.append(r)


def ast_sim(a, b):
    def dump(src):
        try:
            return ast.dump(ast.parse(src))
        except Exception:
            return src
    return difflib.SequenceMatcher(None, dump(a), dump(b)).ratio()


def code_of(free_gen, question):
    m = re.findall(r"```(?:python)?\n(.*?)```", free_gen, re.S)
    if m:
        c = max(m, key=len)
        return c if "def " in c else question + c
    return question + free_gen if "def " not in free_gen else free_gen


xs = [ast_sim(code_of(r["free_gen"], r["question"]), r["canonical_solution"]) for r in ctr]
ys = [tests[(r["model"], r["problem_id"])] for r in ctr]
out["ast_sim_code"] = dict(n=len(xs), r=round(pearson(xs, ys), 3), ci=bci(xs, ys),
                           note="AST-dump sequence similarity vs canonical solution, "
                                "correlated with executed-test outcome")

json.dump(out, open("../../papers/analysis/strong_baselines.json", "w"), indent=1)
print(json.dumps(out, indent=1))
