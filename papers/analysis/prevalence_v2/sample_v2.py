# Sample 200 items per v2 dataset with random.seed(0); random.sample(range(N), 200), sorted.
# No API calls. Writes items_<ds>.jsonl and sampling_manifest.json (sources, revisions, row counts, failures).
# Usage (from anywhere): python sample_v2.py [simpleqa browsecomp hle triviaqa webinstruct]
import base64
import csv
import hashlib
import io
import json
import os
import random
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HERE, V2_DATASETS, env_value

N = 200
SIMPLEQA_URL = "https://openaipublic.blob.core.windows.net/simple-evals/simple_qa_test_set.csv"
BROWSECOMP_URL = "https://openaipublic.blob.core.windows.net/simple-evals/browse_comp_test_set.csv"


def sample_rows(n_rows, n=N):
    random.seed(0)
    return sorted(random.sample(range(n_rows), n))


# derive_key and decrypt copied verbatim from openai/simple-evals browsecomp_eval.py
def derive_key(password: str, length: int) -> bytes:
    """Derive a fixed-length key from the password using SHA256."""
    hasher = hashlib.sha256()
    hasher.update(password.encode())
    key = hasher.digest()
    return key * (length // len(key)) + key[: length % len(key)]


def decrypt(ciphertext_b64: str, password: str) -> str:
    """Decrypt base64-encoded ciphertext with XOR."""
    encrypted = base64.b64decode(ciphertext_b64)
    key = derive_key(password, len(encrypted))
    decrypted = bytes(a ^ b for a, b in zip(encrypted, key))
    return decrypted.decode()


def fetch_csv(url):
    with urllib.request.urlopen(url, timeout=300) as r:
        raw = r.read()
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    return rows, hashlib.sha256(raw).hexdigest()


def hf_parquet(repo_id, filename, columns):
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, hf_hub_download
    token = env_value("HF_TOKEN")
    sha = HfApi(token=token).dataset_info(repo_id).sha
    path = hf_hub_download(repo_id, filename, repo_type="dataset", revision=sha, token=token)
    return pq.read_table(path, columns=columns).to_pandas(), sha


def save(name, items):
    with open(os.path.join(HERE, f"items_{name}.jsonl"), "w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(name, len(items), flush=True)


def build(name):
    if name == "simpleqa":
        rows, digest = fetch_csv(SIMPLEQA_URL)
        idx = sample_rows(len(rows))
        items = [{"id": f"simpleqa-{i}", "row": i, "question": rows[i]["problem"], "reference": rows[i]["answer"],
                  "aliases": [], "metadata": rows[i]["metadata"]} for i in idx]
        return items, {"source": SIMPLEQA_URL, "csv_sha256": digest, "n_rows": len(rows)}
    if name == "browsecomp":
        rows, digest = fetch_csv(BROWSECOMP_URL)
        idx = sample_rows(len(rows))
        items = [{"id": f"browsecomp-{i}", "row": i, "question": decrypt(rows[i]["problem"], rows[i]["canary"]),
                  "reference": decrypt(rows[i]["answer"], rows[i]["canary"]), "aliases": [],
                  "problem_topic": rows[i]["problem_topic"], "canary": rows[i]["canary"]} for i in idx]
        return items, {"source": BROWSECOMP_URL, "csv_sha256": digest, "n_rows": len(rows),
                       "canary": rows[0]["canary"], "decryption": "derive_key/decrypt from openai/simple-evals browsecomp_eval.py"}
    if name == "hle":
        df, sha = hf_parquet("cais/hle", "data/test-00000-of-00001.parquet",
                             ["id", "question", "image", "answer", "answer_type", "category", "raw_subject", "canary"])
        keep = df[(df["answer_type"] == "exactMatch") & (df["image"].fillna("") == "")].reset_index()
        idx = sample_rows(len(keep))
        items = [{"id": f"hle-{keep.loc[i, 'id']}", "row": int(keep.loc[i, "index"]), "filtered_row": i,
                  "question": keep.loc[i, "question"], "reference": keep.loc[i, "answer"], "aliases": [],
                  "category": keep.loc[i, "category"], "raw_subject": keep.loc[i, "raw_subject"],
                  "canary": keep.loc[i, "canary"]} for i in idx]
        return items, {"source": "cais/hle test split", "revision": sha, "n_rows_total": len(df),
                       "filter": "answer_type == 'exactMatch' and image == ''", "n_rows": len(keep),
                       "canary": df["canary"].iloc[0], "sampling_index": "positions in the filtered table (dataset order)"}
    if name == "triviaqa":
        df, sha = hf_parquet("mandarjoshi/trivia_qa", "rc.nocontext/validation-00000-of-00001.parquet",
                             ["question", "question_id", "answer"])
        idx = sample_rows(len(df))
        items = []
        for i in idx:
            ans = df.loc[i, "answer"]
            value = ans["value"]
            aliases = []
            for a in list(ans["aliases"]):
                if a != value and a not in aliases:
                    aliases.append(a)
            items.append({"id": f"triviaqa-{i}", "row": i, "qid": df.loc[i, "question_id"],
                          "question": df.loc[i, "question"], "reference": value, "aliases": aliases})
        return items, {"source": "mandarjoshi/trivia_qa, config rc.nocontext, validation split", "revision": sha,
                       "n_rows": len(df), "reference": "answer.value; aliases = answer.aliases minus the value, deduplicated, dataset order"}
    if name == "webinstruct":
        df, sha = hf_parquet("TIGER-Lab/WebInstruct-verified", "data/train-00000-of-00001.parquet",
                             ["id", "question", "answer", "answer_type", "category", "difficulty"])
        idx = sample_rows(len(df))
        items = [{"id": f"webinstruct-{i}", "row": i, "source_id": df.loc[i, "id"], "question": df.loc[i, "question"],
                  "reference": df.loc[i, "answer"], "aliases": [], "answer_type": df.loc[i, "answer_type"],
                  "category": df.loc[i, "category"], "difficulty": df.loc[i, "difficulty"]} for i in idx]
        return items, {"source": "TIGER-Lab/WebInstruct-verified train split", "revision": sha, "n_rows": len(df)}
    raise ValueError(name)


if __name__ == "__main__":
    which = sys.argv[1:] or V2_DATASETS
    mpath = os.path.join(HERE, "sampling_manifest.json")
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
    for name in which:
        try:
            items, meta = build(name)
            assert len(items) == N and len({it["id"] for it in items}) == N, name
            save(name, items)
            manifest[name] = {"status": "ok", "n_sampled": len(items),
                              "sampling": f"random.seed(0); random.sample(range({meta['n_rows']}), {N}); sorted", **meta}
        except Exception as e:  # record and continue; no substitution
            print(f"{name} FAILED: {type(e).__name__}: {e}", flush=True)
            manifest[name] = {"status": "failed", "error": f"{type(e).__name__}: {str(e)[:500]}"}
    json.dump(manifest, open(mpath, "w"), indent=1)
