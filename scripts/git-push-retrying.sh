#!/usr/bin/env bash
# Pull --rebase and push, retrying on contention.
#
# Why this exists: 40 workflows end with a bare
#     git pull --rebase origin <branch>
#     git push origin HEAD:<branch>
# with no retry. Normally only one runs at a time, so it never mattered.
# Measured 2026-11-13: a commit touching 17 workflow files fires all 17 at the
# same second (each has `paths: [<its own file>]`). Four of them raced on the
# same ref and failed with a non-fast-forward push. The render work in all four
# had already succeeded — only the write-back lost.
#
# A push that fails because someone else pushed first is not a broken pipeline.
# It is a race. This retries with jitter until it wins or genuinely gives up.
#
# Usage:
#   bash scripts/git-push-retrying.sh <branch> [max attempts]
#
# Exit 0 when the branch is up to date with the remote, whether or not this
# run was the one that pushed.
set -uo pipefail

BRANCH="${1:?branch required}"
ATTEMPTS="${2:-6}"

for attempt in $(seq 1 "$ATTEMPTS"); do
  # Rebase onto whatever landed while we were working. --autostash because a
  # render job may have left working-tree changes; -X theirs is deliberately NOT
  # used — a real conflict must surface rather than be silently discarded.
  if ! git pull --rebase origin "$BRANCH"; then
    echo "git-push-retrying: pull --rebase failed on attempt $attempt (real conflict, not contention)" >&2
    git rebase --abort 2>/dev/null || true
    exit 1
  fi

  if git push origin "HEAD:$BRANCH"; then
    echo "git-push-retrying: pushed on attempt $attempt"
    exit 0
  fi

  # Jitter by attempt number so 17 jobs do not retry in lockstep.
  sleep $(( (attempt * 7) % 23 + 3 ))
  echo "git-push-retrying: push rejected on attempt $attempt (likely another workflow pushed first), retrying…"
done

echo "git-push-retrying: gave up after $ATTEMPTS attempts" >&2
exit 1
