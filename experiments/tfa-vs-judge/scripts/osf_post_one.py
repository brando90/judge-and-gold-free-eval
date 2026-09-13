# Post ONE registration block from papers/registrations/osf_drafts.md to an EXISTING OSF project.
# The original scripts/osf_post.py creates a new project, posts every block (it asserts exactly
# three), and submits through a draft "actions" endpoint that OSF has since retired (404). This
# script posts a single named block using the flow verified on 2026-09-13 (Registration 7 ->
# osf.io/bx8hp), and does nothing irreversible unless --post is given.
#
# Verified OSF v2 flow (the published swagger spec is stale on two of these steps):
#   1. POST  /nodes/{project}/draft_registrations/        schema = Open-Ended Registration
#   2. PATCH /draft_registrations/{draft}/                title + registration_responses.summary
#   3. PATCH /draft_registrations/{draft}/relationships/subjects/   (POST returns 405)
#      OSF refuses to register a draft with no subjects.
#   4. POST  /nodes/{project}/registrations/              draft_registration + registration_choice
# The result is a PUBLIC, IMMUTABLE, timestamped registration once the project administrators'
# approval window passes. OSF stores ">" as "&gt;"; unescaping reproduces the text exactly, and
# this script checks that before registering.
#
# DRY RUN (default): prints the target, title, and exact text; makes no network request.
# Usage (from experiments/tfa-vs-judge):
#   python3 scripts/osf_post_one.py --number 8 --project kszeu                    # dry run
#   OSF_TOKEN=... python3 scripts/osf_post_one.py --number 8 --project kszeu --post
import argparse
import html
import json
import os
import sys
import urllib.error
import urllib.request

# The two subjects Registrations 1-3 and 7 carry (bepress taxonomy on the OSF registry provider).
DEFAULT_SUBJECTS = ["584240da54be81056cecabbb",   # Computer Sciences
                    "584240d954be81056ceca9a1"]   # Physical Sciences and Mathematics

ap = argparse.ArgumentParser()
ap.add_argument("--number", type=int, required=True, help="registration number in osf_drafts.md")
ap.add_argument("--project", required=True, help="existing OSF project (node) id, e.g. kszeu")
ap.add_argument("--subjects", nargs="+", default=DEFAULT_SUBJECTS)
ap.add_argument("--post", action="store_true", help="actually publish; omit for a dry run")
args = ap.parse_args()

src = open("../../papers/registrations/osf_drafts.md").read()
blocks = {}
for part in src.split("\n## Registration ")[1:]:
    title_line, _, body = part.partition("\n")
    num = title_line.split(":", 1)[0].strip()
    # the registered text ends at the next horizontal rule or at the first appended note
    body = body.split("\n---\n")[0].split("\n**External registration")[0].split("\n**Deviations and outcome")[0]
    blocks[num] = ("Registration " + title_line.strip(), body.strip())
key = str(args.number)
if key not in blocks:
    sys.exit(f"no Registration {key}; found {sorted(blocks, key=int)}")
title, body = blocks[key]
summary = f"{title}\n\n{body}"
if len(summary) > 24000:
    sys.exit(f"summary is {len(summary)} chars, over OSF's 24000 limit; refusing to truncate a registration")

print(f"target project: https://osf.io/{args.project}/")
print(f"title: {title}")
print(f"length: {len(summary)} chars | subjects: {args.subjects}")
if not args.post:
    print("\n----- DRY RUN: this exact text would be registered -----\n")
    print(summary)
    print("\n----- no request made; re-run with --post to publish -----")
    sys.exit(0)

TOKEN = os.environ.get("OSF_TOKEN")
if not TOKEN:
    sys.exit("set OSF_TOKEN")
API = "https://api.osf.io/v2"
HDRS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/vnd.api+json"}


def req(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, headers=HDRS, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            b = resp.read().decode()
            return json.loads(b) if b else {}
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} on {method} {url}: {e.read().decode()[:800]}")
        raise


print("project title:", req("GET", f"{API}/nodes/{args.project}/")["data"]["attributes"]["title"])
sid = next(s["id"] for s in req("GET", f"{API}/schemas/registrations/?page[size]=100")["data"]
           if s["attributes"]["name"] == "Open-Ended Registration")
did = req("POST", f"{API}/nodes/{args.project}/draft_registrations/", {
    "data": {"type": "draft_registrations", "relationships": {"registration_schema": {
        "data": {"type": "registration-schemas", "id": sid}}}}})["data"]["id"]
req("PATCH", f"{API}/draft_registrations/{did}/", {
    "data": {"type": "draft_registrations", "id": did,
             "attributes": {"title": title, "registration_responses": {"summary": summary}}}})
req("PATCH", f"{API}/draft_registrations/{did}/relationships/subjects/",
    {"data": [{"type": "subjects", "id": s} for s in args.subjects]})
saved = req("GET", f"{API}/draft_registrations/{did}/")["data"]["attributes"]["registration_responses"]["summary"]
if html.unescape(saved) != summary:
    sys.exit(f"draft {did}: stored text differs from the committed text beyond HTML escaping; not registering")
n_subj = len(req("GET", f"{API}/draft_registrations/{did}/subjects/").get("data", []))
if n_subj < 1:
    sys.exit(f"draft {did}: no subjects attached; not registering")
reg = req("POST", f"{API}/nodes/{args.project}/registrations/", {
    "data": {"type": "registrations",
             "attributes": {"draft_registration": did, "registration_choice": "immediate"}}})["data"]
a = reg["attributes"]
print(f"registered https://osf.io/{reg['id']}/ at {a.get('date_registered')} "
      f"(pending approval: {a.get('pending_registration_approval')})")
