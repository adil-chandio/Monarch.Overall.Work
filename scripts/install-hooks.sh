#!/usr/bin/env bash
# Install the repo's Git hooks. Run once per clone:
#
#   bash scripts/install-hooks.sh
#
# Uses core.hooksPath, so it does not touch .git/hooks and cannot be lost when
# Git regenerates it. Uninstall with: git config --unset core.hooksPath
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

chmod +x scripts/hooks/pre-commit
chmod +x scripts/hooks/commit-msg 2>/dev/null || true
git config core.hooksPath scripts/hooks

echo "hooks installed → core.hooksPath = scripts/hooks"
echo "  pre-commit: blocks media and >=100 MB files from entering history"
echo "  bypass a single commit with: git commit --no-verify"
