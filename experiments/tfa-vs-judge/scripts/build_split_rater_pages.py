# Build the DEPLOYABLE split-rater labeling pages from the two generated instruments
# (human_eval/label_split_{sound,style}.html, from build_split_rater_artifacts.py).
#
# Two changes, both required before handing the pages to hypothesis-blind annotators:
#  1. REMOVE hidden leaks. The generated cards carried the GPT judge score, the automatic
#     correctness flag, the reference-match score, the source model and the diagnostic cell as
#     data attributes and CSS-hidden elements. Hidden is not removed: anyone opening developer
#     tools could read them. Only the opaque item code and display order remain.
#  2. SAVE labels properly. Each page saves to the artifact's shared store when it runs as a
#     published artifact with the db capability (one document per annotator:
#     labels/<pool>__<initials>), and otherwise falls back to this browser's storage with a
#     copy-out Export, so the same file also works opened locally or emailed.
# Output: human_eval/label_split_{sound,style}_v2.html. Run from experiments/tfa-vs-judge.
import re

POOLS = {
    "sound": dict(axis="soundness", title="Trace Soundness Grading", has_reference=True),
    "style": dict(axis="style", title="Trace Clarity Grading", has_reference=False),
}

EXTRA_CSS = """
.sync{font-size:13px;color:var(--mut);padding:3px 10px;border:1px solid var(--bd);border-radius:999px;white-space:nowrap}
.sync[data-kind="ok"]{color:var(--good);border-color:color-mix(in srgb,var(--good) 45%,var(--bd))}
.sync[data-kind="warn"]{color:var(--warn);border-color:color-mix(in srgb,var(--warn) 45%,var(--bd))}
#who{min-width:170px}
#who:focus-visible,button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.exportpanel{position:fixed;inset:8% 10%;z-index:99;background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:10px;box-shadow:0 12px 40px rgba(0,0,0,.35)}
.exportbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.exhelp{margin:0;font-size:13px;color:var(--mut)}
#exta{flex:1;font:12px ui-monospace,monospace;white-space:pre;background:var(--field);color:var(--fg);border:1px solid var(--bd);border-radius:8px;padding:10px}
"""

SCRIPT = r"""<script>
const POOL = "__POOL__", AXIS = "__AXIS__", KEY = "tfa_split_" + POOL + "_v2";
const cards = [...document.querySelectorAll(".card")];
const who = document.getElementById("who"), statusEl = document.getElementById("sync"), exportBtn = document.getElementById("export");
let store = {};
try { store = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}
who.value = store.__who || "";
let db = null, timer = null, dirty = false;

function slug(s){ return (s||"").trim().toLowerCase().replace(/[^a-z0-9_-]+/g,"-").replace(/^-+|-+$/g,"").slice(0,40); }
function persistLocal(){ try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} }
function grab(c){ const s = {}; c.querySelectorAll("input[type=radio]:checked").forEach(r => { s[r.name.split("__")[1]] = r.value; });
  const ta = c.querySelector("textarea"); if (ta && ta.value) s.notes = ta.value; return s; }
function mark(c){ const s = store[c.dataset.id] || {}; c.querySelector(".done-tag").hidden = (s[AXIS] == null); }
function graded(){ return cards.filter(c => (store[c.dataset.id] || {})[AXIS] != null).length; }
function prog(){ document.getElementById("prog").textContent = graded() + " / " + cards.length + " graded"; }
function paint(){ cards.forEach(c => { const s = store[c.dataset.id] || {};
  c.querySelectorAll("input[type=radio]").forEach(r => { r.checked = s[r.name.split("__")[1]] === r.value; });
  const ta = c.querySelector("textarea"); if (ta) ta.value = s.notes || ""; mark(c); }); prog(); }
function setStatus(t, kind){ statusEl.textContent = t; statusEl.dataset.kind = kind || ""; }
function labels(){ const out = {}; cards.forEach(c => { if (store[c.dataset.id]) out[c.dataset.id] = store[c.dataset.id]; }); return out; }
function docRef(){ const r = slug(who.value); return (db && r) ? db.doc("labels/" + POOL + "__" + r) : null; }

async function flush(){
  timer = null;
  if (!db) { setStatus("Saved in this browser only. Press Export when you finish.", "local"); return; }
  const ref = docRef();
  if (!ref) { setStatus("Type your initials to start saving", "warn"); return; }
  setStatus("Saving…", "busy");
  try {
    await ref.set({ pool: POOL, rater: who.value.trim(), updated: new Date().toISOString(),
                    n_graded: graded(), n_items: cards.length, labels: labels() });
    dirty = false;
    setStatus(graded() === cards.length ? "All " + cards.length + " graded and saved. You can close this page." : "Saved", "ok");
  } catch (e) {
    if (e && e.code === "unavailable") { setStatus("Retrying save…", "busy"); setTimeout(flush, 1500 + Math.random() * 1500); }
    else setStatus("Save failed (" + ((e && e.code) || "error") + "). Your grades are kept in this browser.", "warn");
  }
}
function schedule(){ dirty = true; persistLocal(); if (timer) clearTimeout(timer); timer = setTimeout(flush, 700); }
function onChange(c){ store[c.dataset.id] = grab(c); mark(c); prog(); schedule(); }
cards.forEach(c => {
  c.querySelectorAll("input[type=radio]").forEach(r => r.addEventListener("change", () => onChange(c)));
  const ta = c.querySelector("textarea"); if (ta) ta.addEventListener("input", () => onChange(c));
});

async function loadRemote(){
  const ref = docRef(); if (!ref) return;
  setStatus("Loading your saved grades…", "busy");
  try {
    const snap = await ref.get();
    if (snap.exists) {
      const remote = (snap.data().labels) || {}; let added = 0;
      for (const id in remote) { if (!store[id]) { store[id] = remote[id]; added++; } }
      if (added) { persistLocal(); paint(); }
    }
    if (dirty || Object.keys(labels()).length) schedule(); else setStatus("Ready", "ok");
  } catch (e) { setStatus("Could not load saved grades (" + ((e && e.code) || "error") + ")", "warn"); }
}
who.addEventListener("change", () => { store.__who = who.value; persistLocal(); if (db) loadRemote(); else flush(); });
window.addEventListener("pagehide", () => { if (timer) { clearTimeout(timer); flush(); } });

paint();
setStatus("Connecting…", "busy");
(window.claude && window.claude.use ? window.claude.use("db") : Promise.resolve(null)).then(ns => {
  db = ns || null;
  exportBtn.hidden = !!db;
  if (!db) { setStatus("Saved in this browser only. Press Export when you finish.", "local"); return; }
  if (slug(who.value)) loadRemote(); else setStatus("Type your initials to start saving", "warn");
}).catch(() => { exportBtn.hidden = false; setStatus("Saved in this browser only. Press Export when you finish.", "local"); });

exportBtn.addEventListener("click", () => {
  const name = "labels_" + POOL + "_" + (slug(who.value) || "rater") + ".json";
  const text = JSON.stringify({ pool: POOL, rater: who.value.trim(), exported: new Date().toISOString(), labels: labels() }, null, 1);
  let p = document.getElementById("exportpanel");
  if (!p) {
    p = document.createElement("div"); p.id = "exportpanel"; p.className = "exportpanel";
    p.innerHTML = '<div class=exportbar><b id=exname></b><span class=grow></span><button id=excopy>Copy</button><button class=ghost id=exclose>Close</button></div>'
      + '<p class=exhelp>Copy this text into a file with the name shown and send it back.</p><textarea id=exta spellcheck=false></textarea>';
    document.body.appendChild(p);
    document.getElementById("exclose").onclick = () => p.remove();
    document.getElementById("excopy").onclick = async () => {
      const t = document.getElementById("exta"); t.select();
      try { await navigator.clipboard.writeText(t.value); } catch (e) { try { document.execCommand("copy"); } catch (e2) {} }
      document.getElementById("excopy").textContent = "Copied";
    };
  }
  document.getElementById("exname").textContent = name;
  const ta = document.getElementById("exta"); ta.value = text; ta.focus(); ta.select();
});
</script>"""

for pool, cfg in POOLS.items():
    s = open(f"human_eval/label_split_{pool}.html").read()
    s = re.sub(r' data-(?:dataset|model|cell|tfa|judge|correct)="[^"]*"', "", s)
    s = re.sub(r'<span class="chip rev">.*?</span>', "", s, flags=re.S)
    s = re.sub(r'<div class="cell rev">.*?</div>', "", s, flags=re.S)
    s = re.sub(r'<div class="scores rev">.*?</div>', "", s, flags=re.S)
    s, n = re.subn(r'<input type=text id=who placeholder="[^"]*">\s*<button class=ghost id=dljson>Export JSON</button>\s*<button id=dlcsv>Export / download CSV</button>',
                   '<input type=text id=who placeholder="your initials" autocomplete=off aria-label="your initials"><span id=sync class=sync role=status></span><button id=export hidden>Export</button>', s)
    assert n == 1, f"{pool}: header controls not found"
    s, n = re.subn(r"Your work saves in this browser as you go\. <b>.*?</b>",
                   "<b>Type your initials in the box at the top first.</b> Your grades then save automatically as you go. "
                   "If the status says they are saved in this browser only, press Export when you finish and send the text back.",
                   s, flags=re.S)
    assert n == 1, f"{pool}: instruction note not found"
    k = s.rfind("<script>")
    assert k > 0 and s.rstrip().endswith("</script>"), f"{pool}: final script block not found"
    s = s[:k] + SCRIPT.replace("__POOL__", pool).replace("__AXIS__", cfg["axis"])
    s = s.replace("</style>", EXTRA_CSS + "</style>", 1)
    s = f"<title>{cfg['title']}</title>\n" + s
    n_cards = s.count("<article class=card")
    assert n_cards == 60, f"{pool}: {n_cards} cards"
    for leak in ("data-judge", "data-tfa", "data-correct", "data-model", "data-cell", 'class="scores rev"', 'class="chip rev"', "deterministic checker"):
        assert leak not in s, f"{pool}: leak remains: {leak}"
    ref_blocks = s.count("Reference solution")
    assert (ref_blocks == 60) if cfg["has_reference"] else (ref_blocks == 0), f"{pool}: reference blocks {ref_blocks}"
    if pool == "style":
        assert "Reasoning soundness, 0-10" not in s and "Final answer correct?" not in s, "style pool shows a correctness question"
    else:
        assert "Clarity and style, 0-10" not in s, "soundness pool shows a style question"
    out = f"human_eval/label_split_{pool}_v2.html"
    open(out, "w").write(s)
    print(f"wrote {out}: {len(s) // 1024} KB, {n_cards} cards, reference blocks {ref_blocks}, leaks removed")
