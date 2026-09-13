# Post ONE registration block from papers/registrations/osf_drafts.md to an EXISTING OSF project.
# The original scripts/osf_post.py creates a new project and posts every block (it asserts
# exactly three), so it cannot add a later registration. This script posts a single named block
# and does nothing irreversible unless --post is given.
#
# DRY RUN (default): prints the target project, the title, and the exact text that would be
# registered; makes no network request.
# --post: creates a draft registration (Open-Ended Registration schema) on the project, fills
# its summary, and submits it with no embargo. On OSF that produces a PUBLIC, IMMUTABLE,
# timestamped registration (admins may have an approval window before it is visible).
#
# Usage (from experiments/tfa-vs-judge):
#   python3 scripts/osf_post_one.py --number 7 --project <osf_project_id>          # dry run
#   OSF_TOKEN=... python3 scripts/osf_post_one.py --number 7 --project <id> --post  # publishes
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--number", type=int, required=True, help="registration number in osf_drafts.md")
ap.add_argument("--project", required=True, help="existing OSF project (node) id, e.g. abcde")
ap.add_argument("--post", action="store_true", help="actually publish; omit for a dry run")
args = ap.parse_args()

src = open("../../papers/registrations/osf_drafts.md").read()
blocks = {}
for part in src.split("\n## Registration ")[1:]:
    title_line, _, body = part.partition("\n")
    num = title_line.split(":", 1)[0].strip()
    # a block ends at the next horizontal rule; appended deviation notes stay with their block
    blocks[num] = ("Registration " + title_line.strip(), body.split("\n---\n")[0].strip())
key = str(args.number)
if key not in blocks:
    sys.exit(f"no Registration {key}; found {sorted(blocks, key=int)}")
title, body = blocks[key]
summary = f"{title}\n\n{body}"
if len(summary) > 24000:
    sys.exit(f"summary is {len(summary)} chars, over OSF's 24000 limit; refusing to truncate a registration")

print(f"target project: https://osf.io/{args.project}/")
print(f"title: {title}")
print(f"length: {len(summary)} chars")
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


node = req("GET", f"{API}/nodes/{args.project}/")
print("project title:", node["data"]["attributes"]["title"])
sid = next(s["id"] for s in req("GET", f"{API}/schemas/registrations/?page[size]=100")["data"]
           if s["attributes"]["name"] == "Open-Ended Registration")
draft = req("POST", f"{API}/nodes/{args.project}/draft_registrations/", {
    "data": {"type": "draft_registrations", "relationships": {"registration_schema": {
        "data": {"type": "registration-schemas", "id": sid}}}}})
did = draft["data"]["id"]
req("PATCH", f"{API}/draft_registrations/{did}/", {
    "data": {"type": "draft_registrations", "id": did,
             "attributes": {"title": title, "registration_responses": {"summary": summary}}}})
req("POST", f"{API}/draft_registrations/{did}/actions/", {
    "data": {"type": "actions", "attributes": {"trigger": "submit"}}})
print(f"submitted draft {did}: check https://osf.io/{args.project}/registrations/")
