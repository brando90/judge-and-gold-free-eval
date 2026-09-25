#!/usr/bin/env bash
# Archive experiments/tfa-vs-judge/runs/ to /dfs on the SNAP cluster.
#
# WHY IT IS BUILT THIS WAY. Every analysis producer hardcodes its input path -- `runs/r4/scores/...`,
# `runs/bon/bon_repl__*.jsonl` and so on. Physically reorganising the local tree would break all 127
# of them at once. So the archive keeps a BYTE-EXACT MIRROR under raw/, which rsyncs straight back
# into place and leaves every path working, and layers an experiment-oriented index of SYMLINKS on
# top of it. The index is for humans reading the archive; the mirror is what the code needs. Nothing
# is duplicated: the symlink tree costs a few kilobytes.
#
# Usage:
#   scripts/archive_runs.sh push        copy the mirror up, build the index, verify checksums
#   scripts/archive_runs.sh index       rebuild only the by-experiment symlink index
#   scripts/archive_runs.sh verify      re-checksum on the remote and diff against the local manifest
#   scripts/archive_runs.sh restore     pull the mirror back down into runs/ (refuses to clobber)
#
# Requires a live Kerberos ticket: kinit srivatsavad@CS.STANFORD.EDU
set -euo pipefail

HOST="${JFE_HOST:-skampere1}"
DEST="${JFE_DEST:-/dfs/scratch0/srivatsavad/jfe-archive}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"     # experiments/tfa-vs-judge
MAP="$HERE/scripts/runs_experiment_map.tsv"
SSH=(ssh -o GSSAPIAuthentication=yes -o GSSAPIDelegateCredentials=yes -o ConnectTimeout=25)

die() { echo "ERROR: $*" >&2; exit 1; }

check_ticket() {
  klist -s 2>/dev/null || die "no valid Kerberos ticket. Run: kinit srivatsavad@CS.STANFORD.EDU"
}

manifest() {
  # Deterministic: sorted, NUL-separated, .DS_Store and AppleDouble excluded. Paths are relative to
  # $HERE so the same manifest validates the local tree and the remote mirror.
  #
  # LC_ALL=C is load-bearing. macOS sort and GNU sort disagree on collation for names containing
  # '.', '_' and mixed case, and this project's filenames are full of all three
  # (battery_Qwen_Qwen2.5-14B-Instruct_noref.jsonl). Without it, a diff of the two sides reports
  # dozens of files as missing on one end and extra on the other when nothing is wrong at all.
  cd "$HERE"
  LC_ALL=C find runs -type f ! -name '.DS_Store' ! -name '._*' -print0 \
    | LC_ALL=C sort -z | xargs -0 shasum -a 256
}

cmd_push() {
  check_ticket
  cd "$HERE"
  [[ -f "$MAP" ]] || die "missing $MAP"

  echo "== 1/5  local manifest"
  manifest > /tmp/jfe_runs.sha256
  echo "   $(wc -l < /tmp/jfe_runs.sha256) files, $(du -sh runs | cut -f1)"

  echo "== 2/5  copy mirror -> $HOST:$DEST/raw/"
  "${SSH[@]}" "$HOST" "mkdir -p '$DEST/raw' '$DEST/meta'"
  # tar over ssh rather than rsync: macOS ships openrsync (protocol 29, "rsync 2.6.9 compatible"),
  # which rejects --info=progress2 and other modern flags, and silently prints its usage instead of
  # failing loudly. tar is the same everywhere. -z compresses on the wire; JSONL compresses hard,
  # so 1.4 GB moves as roughly a tenth of that. Correctness is established by the checksum pass in
  # step 5, not by the transfer tool.
  #
  # COPYFILE_DISABLE=1 is required. Many files in this tree carry extended attributes (ls shows
  # them with a trailing '@'), and bsdtar silently emits an AppleDouble "._name" companion for each
  # one. A first run put 836 of those on the cluster -- 2,708 remote files against 1,872 real ones.
  # They are macOS resource forks, meaningless on Linux, and they make the archive look corrupt.
  COPYFILE_DISABLE=1 tar -c -z -f - --exclude='.DS_Store' --exclude='._*' runs \
    | "${SSH[@]}" "$HOST" "mkdir -p '$DEST/raw' && tar -x -z -f - -C '$DEST/raw'"

  echo "== 3/5  ship manifest, map and reader docs"
  scp -q -o GSSAPIAuthentication=yes /tmp/jfe_runs.sha256 "$HOST:$DEST/meta/runs.sha256"
  scp -q -o GSSAPIAuthentication=yes "$MAP" "$HOST:$DEST/meta/runs_experiment_map.tsv"
  # orientation for anyone who reaches the archive without the repo in front of them
  scp -q -o GSSAPIAuthentication=yes "$HERE/scripts/archive_README.md" "$HOST:$DEST/README.md"

  echo "== 4/5  build the by-experiment index on the remote"
  build_index

  echo "== 5/5  verify"
  cmd_verify
}

# Rebuild only the symlink index. Separated from push so a map change costs seconds instead of a
# full re-transfer; `index` is the subcommand.
build_index() {
  check_ticket
  [[ -f "$MAP" ]] || die "missing $MAP"
  scp -q -o GSSAPIAuthentication=yes "$MAP" "$HOST:$DEST/meta/runs_experiment_map.tsv"
  "${SSH[@]}" "$HOST" "bash -s" <<REMOTE
set -euo pipefail
cd "$DEST"
rm -rf by-experiment && mkdir -p by-experiment
ROOT=\$(pwd)
# map columns: experiment <TAB> glob-relative-to-runs <TAB> one-line note
#
# The link keeps its path RELATIVE TO runs/, not just its basename. Linking by basename silently
# loses data: r3/scores and r4/scores both feed p1-rotation, so the second overwrote the first and
# r4/scores -- the registered headline result -- was absent from the index entirely. Mirroring the
# relative path makes by-experiment/p1-rotation/r4/scores and .../r3/scores distinct.
collisions=0
tail -n +2 meta/runs_experiment_map.tsv | while IFS=\$'\t' read -r exp pat note; do
  [[ -z "\${exp:-}" || "\$exp" == \#* ]] && continue
  shopt -s nullglob
  for p in raw/runs/\$pat; do
    [[ -e "\$p" ]] || continue
    rel="\${p#raw/runs/}"
    dest="by-experiment/\$exp/\$rel"
    mkdir -p "\$(dirname "\$dest")"
    if [[ -L "\$dest" ]]; then
      cur=\$(readlink "\$dest")
      [[ "\$cur" == "\$ROOT/\$p" ]] || { echo "   COLLISION \$dest: \$cur vs \$ROOT/\$p"; }
    fi
    ln -sfn "\$ROOT/\$p" "\$dest"
  done
  shopt -u nullglob
done
echo "   groups: \$(find by-experiment -maxdepth 1 -mindepth 1 -type d | wc -l)"
echo "   links:  \$(find by-experiment -type l | wc -l)"
# Every link must resolve. A dangling link means the map points at data the mirror does not hold.
bad=\$(find by-experiment -type l ! -exec test -e {} \; -print | wc -l)
echo "   dangling links: \$bad"
[[ "\$bad" -eq 0 ]] || { echo "   FAIL: dangling links in the index"; exit 1; }
REMOTE
}

cmd_verify() {
  check_ticket
  echo "== remote re-checksum (this reads every byte; it is the point)"
  "${SSH[@]}" "$HOST" "cd '$DEST/raw' && LC_ALL=C find runs -type f ! -name '.DS_Store' ! -name '._*' -print0 | LC_ALL=C sort -z | xargs -0 sha256sum" \
    | awk '{print $1"  "$2}' | LC_ALL=C sort -k2 > /tmp/jfe_remote.sha256
  cd "$HERE"; manifest | awk '{print $1"  "$2}' | LC_ALL=C sort -k2 > /tmp/jfe_local.sha256
  if diff -q /tmp/jfe_local.sha256 /tmp/jfe_remote.sha256 >/dev/null; then
    echo "   OK: $(wc -l < /tmp/jfe_local.sha256) files match byte for byte"
  else
    echo "   MISMATCH -- differing or missing entries:"
    diff /tmp/jfe_local.sha256 /tmp/jfe_remote.sha256 | head -40
    exit 1
  fi
}

cmd_restore() {
  check_ticket
  cd "$HERE"
  [[ -d runs && -n "$(ls -A runs 2>/dev/null)" ]] && \
    die "runs/ is not empty. Restoring would overwrite local data; move it aside first."
  "${SSH[@]}" "$HOST" "cd '$DEST/raw' && tar -c -z -f - runs" | tar -x -z -f - -C "$HERE"
  echo "restored into $HERE/runs"
}

case "${1:-}" in
  push)    cmd_push ;;
  index)   build_index ;;
  verify)  cmd_verify ;;
  restore) cmd_restore ;;
  *) echo "usage: $0 {push|index|verify|restore}" >&2; exit 2 ;;
esac
