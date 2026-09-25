"""Enforce that scripts/runs_experiment_map.tsv accounts for every file under runs/.

The map drives the by-experiment/ index that archive_runs.sh builds on /dfs. That index is how a
reader navigates 1.4 GB of judge output, so a file the map misses is a file that, to anyone reading
the archive, does not exist. This script fails if:

  - any glob in the map matches nothing (a stale row, pointing at data that has been renamed)
  - any file under runs/ is matched by no glob (an unindexed file)

Overlap is allowed and expected: the shared candidate pools are read by several experiments, so
bon/bon_repl__*.jsonl legitimately appears under pools, p1-rotation and rl-mechanism.

Run from experiments/tfa-vs-judge/:   python scripts/check_runs_map.py
"""

import collections
import glob
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(HERE, "scripts", "runs_experiment_map.tsv")
RUNS = os.path.join(HERE, "runs")


def load_map():
    rows = []
    for n, line in enumerate(open(MAP), 1):
        line = line.rstrip("\n")
        if not line or line.startswith("#") or line.startswith("experiment\t"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            sys.exit(f"{MAP}:{n}: expected TAB-separated columns, got {line[:70]!r}")
        rows.append((parts[0], parts[1]))
    return rows


def expand(pattern):
    """Files matched by one glob. A matched directory contributes everything under it."""
    out = set()
    for hit in glob.glob(os.path.join(RUNS, pattern)):
        if os.path.isdir(hit):
            for root, _dirs, files in os.walk(hit):
                for f in files:
                    if f != ".DS_Store":
                        out.add(os.path.relpath(os.path.join(root, f), RUNS))
        elif os.path.basename(hit) != ".DS_Store":
            out.add(os.path.relpath(hit, RUNS))
    return out


def main():
    if not os.path.isdir(RUNS):
        sys.exit(f"no runs/ directory at {RUNS}")
    rows = load_map()
    groups = collections.defaultdict(set)
    empty = []
    for exp, pattern in rows:
        hits = expand(pattern)
        if not hits:
            empty.append((exp, pattern))
        groups[exp] |= hits

    on_disk = {os.path.relpath(os.path.join(r, f), RUNS)
               for r, _d, fs in os.walk(RUNS) for f in fs if f != ".DS_Store"}
    covered = set().union(*groups.values()) if groups else set()
    missing = on_disk - covered

    print(f"  map: {len(rows)} rows, {len(groups)} groups")
    for exp in sorted(groups):
        size = sum(os.path.getsize(os.path.join(RUNS, f))
                   for f in groups[exp] if os.path.exists(os.path.join(RUNS, f)))
        print(f"    {exp:<16}{len(groups[exp]):>6} files  {size / 1e9:>7.2f} GB")
    print(f"  files under runs/: {len(on_disk)}   covered: {len(covered & on_disk)}")

    ok = True
    if empty:
        ok = False
        print(f"\n  FAIL: {len(empty)} glob(s) match nothing (stale rows):")
        for exp, pattern in empty:
            print(f"    {exp}\t{pattern}")
    if missing:
        ok = False
        print(f"\n  FAIL: {len(missing)} file(s) in no group:")
        for d, n in collections.Counter(m.split("/")[0] for m in sorted(missing)).most_common(20):
            print(f"    {n:>5}  {d}")
    if ok:
        print("\n  OK: every glob matches, every file is indexed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
