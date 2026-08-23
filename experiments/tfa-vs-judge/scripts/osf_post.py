# Post the three preregistrations to OSF via the v2 API.
# Usage: OSF_TOKEN=... python3 scripts/osf_post.py
# Flow per registration: create a draft registration on the project (Open-Ended Registration
# schema), fill its summary with the registration text, then register it immediately
# (no embargo), producing a public immutable timestamped registration.
import json
import os
import sys
import urllib.request

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
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} on {method} {url}: {e.read().decode()[:800]}")
        raise


# ------------------------------------------------ split the drafts file
src = open("../../papers/registrations/osf_drafts.md").read()
blocks = []
for part in src.split("\n## Registration ")[1:]:
    title_line, _, body = part.partition("\n")
    title = "Registration " + title_line.strip()
    blocks.append((title, body.strip()))
assert len(blocks) == 3, len(blocks)

# ------------------------------------------------ project
proj = req("POST", f"{API}/nodes/", {
    "data": {"type": "nodes", "attributes": {
        "title": "Judge-free evaluation: preregistrations (certificate, Putnam replication, reference-lever replication)",
        "category": "project",
        "description": "Preregistrations for three experiments in the judge-free-eval project. "
                       "Each registration below freezes design, predictions, and analysis before data."}}})
pid = proj["data"]["id"]
print("project:", pid, f"https://osf.io/{pid}/")

# ------------------------------------------------ find the Open-Ended Registration schema
schemas = req("GET", f"{API}/schemas/registrations/?page[size]=100")
sid = None
for s in schemas["data"]:
    if s["attributes"]["name"] == "Open-Ended Registration":
        sid = s["id"]
print("schema:", sid)

for title, body in blocks:
    draft = req("POST", f"{API}/nodes/{pid}/draft_registrations/", {
        "data": {"type": "draft_registrations",
                 "relationships": {"registration_schema": {
                     "data": {"type": "registration-schemas", "id": sid}}}}})
    did = draft["data"]["id"]
    req("PATCH", f"{API}/draft_registrations/{did}/", {
        "data": {"type": "draft_registrations", "id": did, "attributes": {
            "title": title,
            "registration_responses": {"summary": f"{title}\n\n{body}"[:24000]}}}})
    reg = req("POST", f"{API}/draft_registrations/{did}/actions/", {
        "data": {"type": "actions", "attributes": {"trigger": "submit"}}})
    print("submitted draft:", did, title[:60])
print("done: check https://osf.io/" + pid + "/registrations/")
