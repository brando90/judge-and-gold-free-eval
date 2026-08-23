# Independent second-opinion review of a paper PDF by GPT-5.2 (different model family from
# the drafting/reviewing pipeline). Extracts text with pdftotext and requests a strict
# four-axis area-chair review. Usage:
#   OPENAI_API_KEY=... python3 scripts/gpt_review.py <paper.pdf> <out.md>
import subprocess
import sys

from openai import OpenAI

pdf, out = sys.argv[1], sys.argv[2]
text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True,
                      text=True, check=True).stdout
if len(text) > 180_000:
    text = text[:180_000] + "\n[TRUNCATED]"

PROMPT = """You are a brutally honest area-chair-level reviewer for a top ML venue \
(NeurIPS/ICML calibre). Review the paper below with equal weight on four axes:
1. NOVELTY: is the contribution genuinely new against the prior art the paper itself cites, \
and against anything else you know?
2. SOUNDNESS: are the experimental designs capable of supporting the claims? Interrogate \
power, confounds, estimator choices, annotator provenance, selection effects, and any claim \
that would not survive a hostile conference Q&A.
3. COMPLETENESS: what would a skeptical reader still demand?
4. IMPACT: who changes what tomorrow because of this paper? Is the result consequential or \
folk knowledge?
Also judge READABILITY for a new reader: can a first-year PhD student follow the abstract, \
find the main result within two pages, and parse the tables?
Structure your review: (a) a three-sentence summary of what the paper claims; (b) the four \
axis assessments with scores 1-10 and concrete quotes; (c) readability verdict; (d) the five \
highest-leverage concrete improvements, ranked; (e) overall score 1-10 and accept/reject \
lean. Be specific: quote sentences, name tables. Do not be polite for politeness's sake; \
find the weaknesses the authors hope you will miss.

PAPER TEXT:
"""

client = OpenAI()
resp = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": PROMPT + text}],
    max_completion_tokens=6000)
review = resp.choices[0].message.content
open(out, "w").write(review)
u = resp.usage
print(f"wrote {out}  tokens in/out {u.prompt_tokens}/{u.completion_tokens}")
