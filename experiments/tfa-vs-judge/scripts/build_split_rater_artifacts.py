# Build the SPLIT-RATER labeling instruments for Paper A's annotation upgrade (review item 3,
# 2026-09-07): two hypothesis-blind non-author rater pools, each grading ALL 60 anchor items on
# ONE axis only, so that soundness and style labels never come from the same person.
#   pool A (soundness-only): sees problem, reference solution, trace; grades final-answer
#           correctness, soundness, and lucky-correct. No style question exists on the page.
#   pool B (style-only):     sees problem and trace ONLY (no reference solution, no checker
#           verdict), grades clarity/style. No correctness question exists on the page.
# Both instruments are blinded (model names and machine scores hidden), items are re-ordered by
# a seeded shuffle, and ids are replaced by opaque codes (S001.., T001..) with the maps written
# to human_eval/blind_maps/split_sound.json and split_style.json. Reuses build_label_artifact.py
# by source patching (same pattern as build_rater2_artifact.py). Run from experiments/tfa-vs-judge.
import json
import random

labeled = [r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
           if r.get("soundness") not in (None, "")]
ids = sorted(r["id"] for r in labeled)
assert len(ids) == 60, len(ids)
rows = {r["id"]: r for r in (json.loads(l) for l in open("human_eval/traces_to_label.jsonl"))}
base_src = open("scripts/build_label_artifact.py").read()


def build(tag, prefix, seed, q_keep, drop_reference, note_html, title):
    rng = random.Random(seed)
    order = ids[:]
    rng.shuffle(order)
    sel, bmap = [], {}
    for i, rid in enumerate(order, 1):
        code = f"{prefix}{i:03d}"
        r = dict(rows[rid])
        bmap[code] = {"id": rid, "model": r["model"]}
        r["id"] = code
        r["order"] = i
        r["model"] = "hidden"
        r["cell"] = "-"
        r["cell_desc"] = ""
        if drop_reference:
            r["gold_solution"] = "(withheld for this task)"
            r["gold_answer"] = ""
            r["gold_answer_disp"] = ""
        sel.append(r)
    json.dump(bmap, open(f"human_eval/blind_maps/split_{tag}.json", "w"), indent=1)
    tr_path = f"human_eval/traces_split_{tag}.jsonl"
    with open(tr_path, "w") as f:
        for r in sel:
            f.write(json.dumps(r) + "\n")
    src = base_src
    src = src.replace('open("human_eval/traces_to_label.jsonl")', f'open("{tr_path}")')
    for a, b in ((f'open("human_eval/label_artifact_v2.html", "w")', f'open("human_eval/label_split_{tag}.html", "w")'),
                 ('"wrote human_eval/label_artifact_v2.html', f'"wrote human_eval/label_split_{tag}.html'),
                 ('open("human_eval/label_artifact_v2.html")', f'open("human_eval/label_split_{tag}.html")'),
                 ("const KEY='tfa_label_artifact_v1';", f"const KEY='tfa_label_split_{tag}_v1';"),
                 ("<h1>Reasoning-trace labeling</h1>", f"<h1>{title}</h1>"),
                 ("'tfa_labels.json'", f"'tfa_labels_split_{tag}.json'"),
                 ("'tfa_labels.csv'", f"'tfa_labels_split_{tag}.csv'")):
        assert a in src, a
        src = src.replace(a, b)
    # keep only the requested questions
    keep_line = "Q = [q for q in Q if q[0] in %r]\n" % (q_keep,)
    marker = "def card(d):"
    assert marker in src
    src = src.replace(marker, keep_line + "\n" + marker, 1)
    # progress / done-tag keyed on the instrument's own axis
    axis = "soundness" if "soundness" in q_keep else "style"
    src = src.replace("(s.soundness==null)", f"(s.{axis}==null)")
    src = src.replace("(store[c.dataset.id]||{}).soundness!=null", f"(store[c.dataset.id]||{{}}).{axis}!=null")
    if drop_reference:
        # remove the reference-solution block and the checker verdict line from the card
        a = """    parts.append(f'<div class=block><div class=lbl>Reference solution &mdash; answer {to_html(ga)}</div>'
                 f'<div class=body>{render_body(d["gold_solution"])}</div></div>')
"""
        assert a in src
        src = src.replace(a, "")
        a = """    parts.append(f'<div class="scores rev">TFA {d["tfa"]} &middot; judge {d["judge"]}/10 &middot; '
                 f'final answer {verdict} (deterministic checker)</div>')
"""
        assert a in src
        src = src.replace(a, "")
    # replace the instruction note
    start = src.index("<div class=note>")
    end = src.index("</div>", start) + len("</div>")
    src = src[:start] + "<div class=note>" + note_html + "</div>" + src[end:]
    exec(compile(src, f"build_label_artifact[{tag}].py", "exec"), {"__name__": "__main__"})


build("sound", "S", 20260907,
      q_keep=["answer_correct", "soundness", "lucky"], drop_reference=False,
      title="Reasoning soundness grading (60 items)",
      note_html=("You are grading <b>reasoning soundness only</b>. For each item, read the problem and the "
                 "reference solution, then judge whether every step of the model's trace is valid and whether the "
                 "argument actually establishes the answer. <b>Ignore wording, length, formatting, and how "
                 "polished the writing looks</b>; a messy trace with valid reasoning scores high, a beautifully "
                 "written trace with a gap scores low. You are grading blind: the model name and all automatic "
                 "scores are hidden on purpose. Your work saves in this browser as you go. <b>When you finish, put "
                 "your name above, click Download, and send the file back.</b>"))
build("style", "T", 20260908,
      q_keep=["style"], drop_reference=True,
      title="Clarity and style grading (60 items)",
      note_html=("You are grading <b>clarity and style only</b>: how clear, organized, and readable the model's "
                 "write-up is. <b>Do not try to judge whether the mathematics is correct</b>; no reference "
                 "solution is shown and none is needed. A wrong solution can be beautifully written and a correct "
                 "one can be a mess; you are scoring the writing. You are grading blind: the model name and all "
                 "automatic scores are hidden on purpose. Your work saves in this browser as you go. <b>When you "
                 "finish, put your name above, click Download, and send the file back.</b>"))
print("wrote human_eval/label_split_sound.html, human_eval/label_split_style.html, blind maps in human_eval/blind_maps/")
