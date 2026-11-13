#!/usr/bin/env bash
# Commit only if the index actually has something staged.
#
# Why this exists: 15 workflows did `git add <folder>` followed by a bare
# `git commit`. Once .gitignore stopped those folders from being added
# (config/media-policy.json -> render evidence), the add stages nothing and
# `git commit` exits 1 with "nothing to commit". Before, that add always found
# files, so the failure mode never appeared. This makes the commit conditional
# and harmless either way, without touching what the job actually produces.
#
# Usage, from any step with a configured user.name/user.email:
#   bash scripts/git-commit-if-changed.sh "commit message" [more git-add paths…]
#
#   bash scripts/git-commit-if-changed.sh 'Record V7 QC [skip ci]'
#   bash scripts/git-commit-if-changed.sh 'Record V7 QC [skip ci]' production/extinct-life/film-v7-full
#
# Exits 0 whether or not there was anything to commit. Never fails a pipeline
# just because a media folder is now excluded.
set -uo pipefail

MSG="${1:?commit message required}"
shift || true

# Optional extra paths to stage. Ignored paths are silently skipped by git add,
# which is exactly the behaviour we want now.
if [ "$#" -gt 0 ]; then
  git add -- "$@" >/dev/null 2>&1 || true
fi

if git diff --cached --quiet; then
  echo "git-commit-if-changed: nothing staged (media folders are excluded from Git by policy) — skipping commit"
  exit 0
fi

if git commit -m "$MSG"; then
  echo "git-commit-if-changed: committed"
else
  echo "git-commit-if-changed: commit failed" >&2
  exit 1
fi
