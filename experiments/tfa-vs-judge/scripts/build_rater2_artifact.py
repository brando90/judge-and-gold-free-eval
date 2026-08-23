# Build the rater-2 / external-annotator labeling instrument: 30 items sampled (seeded) from
# the 60 random-stratum items author 1 already labeled, so every second-rater label yields an
# inter-rater agreement pair. Reuses build_label_artifact.py wholesale with patched IO paths,
# title, and localStorage key (so progress does not collide with other instruments).
import json, random

labeled = [r for r in json.load(open("human_eval/labels/phase1/author_1_Sri_random.json"))
           if r.get("soundness") not in (None, "")]
rng = random.Random(20260822)
ids = sorted(r["id"] for r in labeled)
pick = set(rng.sample(ids, 30))

rows = [json.loads(l) for l in open("human_eval/traces_to_label.jsonl")]
sel = [r for r in rows if r["id"] in pick]
assert len(sel) == 30, len(sel)
for i, r in enumerate(sorted(sel, key=lambda x: x["order"]), 1):
    r["order"] = i
with open("human_eval/traces_rater2.jsonl", "w") as f:
    for r in sorted(sel, key=lambda x: x["order"]):
        f.write(json.dumps(r) + "\n")

src = open("scripts/build_label_artifact.py").read()
src = src.replace('open("human_eval/traces_to_label.jsonl")', 'open("human_eval/traces_rater2.jsonl")')
src = src.replace('open("human_eval/label_artifact_v2.html", "w")', 'open("human_eval/label_rater2.html", "w")')
src = src.replace('"wrote human_eval/label_artifact_v2.html', '"wrote human_eval/label_rater2.html')
src = src.replace('open("human_eval/label_artifact_v2.html")', 'open("human_eval/label_rater2.html")')
src = src.replace("const KEY='tfa_label_artifact_v1';", "const KEY='tfa_label_rater2_v1';")
src = src.replace("<h1>Reasoning-trace labeling</h1>",
                  "<h1>Reasoning-trace labeling &mdash; rater 2 / external (30 items)</h1>")
src = src.replace("'tfa_labels.json'", "'tfa_labels_rater2.json'")
src = src.replace("'tfa_labels.csv'", "'tfa_labels_rater2.csv'")
exec(compile(src, "build_label_artifact.py", "exec"))
