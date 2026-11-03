#!/usr/bin/env python3
"""Append one line to public/yt-intel/run-log.jsonl.

Why this exists as a file instead of an inline heredoc: a heredoc inside a YAML `run: |`
block is indented, and `<<'PY'` (unlike `<<-PY`) requires its terminator at column 0. The
first attempt at this produced `public/yt-intel/lanes.json` containing the *script source*
instead of its output — the shell fed the heredoc to the redirect and python never ran the
way it looked like it would. Three CI runs were lost to that, so the construct is banned
here: scripts are files, and files are testable.

Usage: python scripts/append-run-log.py public/yt-intel/run-log.jsonl
"""
from __future__ import annotations

import json
import os
import sys
import time


def main(argv: list[str]) -> int:
    path = argv[1] if len(argv) > 1 else "public/yt-intel/run-log.jsonl"
    row = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
        "sha": (os.environ.get("GITHUB_SHA") or "")[:7],
        "run": os.environ.get("GITHUB_RUN_ID", ""),
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"run-log: {row['at']} {row['event']} {row['sha']} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
