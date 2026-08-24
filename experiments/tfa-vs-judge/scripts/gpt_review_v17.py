# GPT-5.2 cold read of Paper D v17, carrying the v15 revision context so the reviewer can
# audit its own five asks. Same convention as scripts/gpt_review.py (chat.completions,
# model gpt-5.2, pdftotext -layout extraction).
import subprocess
import sys

from openai import OpenAI

pdf, out = sys.argv[1], sys.argv[2]
text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True,
                      text=True, check=True).stdout
if len(text) > 180_000:
    text = text[:180_000] + "\n[TRUNCATED]"

PROMPT = """You are a brutally honest area-chair-level reviewer for a top ML venue \
(NeurIPS/ICML calibre). You reviewed an earlier draft of this paper (v15) and scored it \
7/10, WEAK ACCEPT, with axis scores Novelty 6, Soundness 7, Completeness 6, Impact 7, \
Readability 8. You left five ranked asks:

  ASK 1. Stop calling anchoring "the mechanism" without qualifying the missing per-item \
link. Match Abstract/Conclusion language to Sec 3.2's negative per-item correlation.
  ASK 2. Make the replication table's populations consistent across endpoints, or provide \
a matched-population version, so E1 / anchoring margin / selection collapse are comparable.
  ASK 3. Test the "judge blind first, then reveal" mitigation under higher selection \
pressure or adaptive optimization, since a residual anchoring premium is admitted.
  ASK 4. Replace or supplement the post-hoc "step" inference on the synthetic grid with a \
registered model-based analysis, or downgrade the universality language.
  ASK 5. Broaden judge coverage for the mitigations beyond two judges, to support the \
prescriptive recommendation table.

The authors say they revised twice since. Their claimed changes:
  - Matched-population recomputation on the n=83 endpoint intersection, replacing the \
endpoint-population footnote.
  - The mitigation tested under rising selection pressure from best-of-2 to best-of-64.
  - The attenuation simulation that bounded the negative per-item linkage was recalibrated \
from the pool rather than from stipulated constants; the authors say the resulting \
conclusion was RETRACTED and the negative linkage is now reported as uninformative.
  - The band-matched comparison now claims only that a pass-rate confound is removed, not \
full comparability.
  - The prediction ledger and provenance discussion were moved out of the exploratory \
subsection into a top-level section.

Review the CURRENT text below. Two obligations:

PART 1 -- a fresh cold read, not anchored to your earlier score. Weight four axes equally:
1. NOVELTY: genuinely new against the prior art the paper cites and anything else you know?
2. SOUNDNESS: are the designs capable of supporting the claims? Interrogate power, \
confounds, estimator choices, annotator provenance, selection effects, and any claim that \
would not survive a hostile conference Q&A.
3. COMPLETENESS: what would a skeptical reader still demand?
4. IMPACT: who changes what tomorrow? Consequential or folk knowledge?
Also judge READABILITY for a new reader: can a first-year PhD student follow the abstract, \
find the main result within two pages, and parse the tables?
Structure it: (a) three-sentence summary of what the paper claims; (b) the four axis \
assessments with scores 1-10 and concrete quotes; (c) readability verdict; (d) the five \
highest-leverage concrete improvements, ranked; (e) overall score 1-10 and accept/reject \
lean with confidence.

PART 2 -- an ask audit. For EACH of your five asks give a verdict of RESOLVED, PARTIALLY \
RESOLVED, or NOT RESOLVED, with a quoted sentence or named table as evidence. Where a \
claimed change is not actually present in the text, say so plainly.

PART 3 -- answer three questions:
(a) Is the retraction of the simulation conclusion handled honestly, or does the paper \
still lean on the mechanism elsewhere in a way the retraction undercuts?
(b) What is the single strongest reason to reject this paper?
(c) At a top-tier venue, what is your modal outcome prediction?

Be specific: quote sentences, name tables. Do not be polite for politeness's sake; find \
the weaknesses the authors hope you will miss.

PAPER TEXT:
"""

client = OpenAI()
resp = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": PROMPT + text}],
    max_completion_tokens=8000)
review = resp.choices[0].message.content
open(out, "w").write(review)
u = resp.usage
print(f"wrote {out}  tokens in/out {u.prompt_tokens}/{u.completion_tokens}")
