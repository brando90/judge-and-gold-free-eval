# GPT-5.2 cold read of Paper D v19, carrying the v17 revision context for an ask audit.
import subprocess
import sys

from openai import OpenAI

pdf, out = sys.argv[1], sys.argv[2]
text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True,
                      text=True, check=True).stdout
if len(text) > 180_000:
    text = text[:180_000] + "\n[TRUNCATED]"

PROMPT = """You are a brutally honest area-chair-level reviewer for a top ML venue \
(NeurIPS/ICML calibre). You reviewed an earlier draft (v17) and scored it 7/10, WEAK \
ACCEPT (Novelty 6, Soundness 7, Completeness 6, Impact 7, Readability 7.5). Your five \
ranked asks were:
  ASK 1. Test the blind-then-reveal mitigation against an adaptive attacker (you rated \
this the top ask; the authors say it remains future work, stated as a limitation).
  ASK 2. Add 2-4 more judge models across at least two more families for the mitigations \
(the authors say an externally registered extension is queued but has not run).
  ASK 3. Make the k=2 step confirmatory or tone it down (the authors say the step claim \
is now anchored on the externally registered P-M3 contrast, confirmed for both judges, \
with the six-judge grid demoted to exploratory support).
  ASK 4. Add a worked example making the inflation metric concrete (the authors say one \
was added to Setup from a committed producer).
  ASK 5. Move load-bearing caveats out of table notes into main text (the authors say the \
band-match comparability discussion and the matched-population recompute moved into prose).

Also new since v17: an internal review found that the paper's claim that its per-item \
margin-to-inflation linkage test was 'uninformative' was wrong — the measurement noise IS \
identifiable from the rubric replicates — and the authors say they retracted it: the paper \
now reports that an exact per-item linear pathway is REJECTED for both judges, with the \
supersession recorded in the ledger and registration history. The abstract was also \
rewritten to a 12-sentence structure.

Review the CURRENT text below.

PART 1 — a fresh cold read, not anchored to your earlier scores: (a) three-sentence \
summary; (b) NOVELTY, SOUNDNESS, COMPLETENESS, IMPACT scored 1-10 with concrete quotes; \
(c) READABILITY verdict for a new reader; (d) five highest-leverage concrete improvements, \
ranked; (e) overall score 1-10, accept/reject lean, confidence.

PART 2 — ask audit: for EACH of the five asks, RESOLVED / PARTIALLY RESOLVED / NOT \
RESOLVED, with a quoted sentence or named table as evidence. If a claimed change is not \
actually in the text, say so plainly.

PART 3 — three questions:
(a) Is the linkage retraction-of-a-retraction (uninformative -> rejected) handled \
honestly and coherently across abstract, mechanism section, ledger, and limitations, or \
are there residual sentences that still soft-pedal it?
(b) Does the worked example actually make the inflation metric parseable to an outsider?
(c) What is your modal outcome prediction at a top-tier venue, and what single addition \
would most raise it?

Be specific: quote sentences, name tables. Find the weaknesses the authors hope you miss.

PAPER TEXT:
"""

client = OpenAI()
resp = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": PROMPT + text}],
    max_completion_tokens=8000)
open(out, "w").write(resp.choices[0].message.content)
u = resp.usage
print(f"wrote {out}  tokens in/out {u.prompt_tokens}/{u.completion_tokens}")
