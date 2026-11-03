#!/usr/bin/env python3
"""Run thumbnail forensics on the best thumbnails the reports already know about.

Why this is a script and not an inline step: two heredoc-in-YAML experiments earlier today
shipped script source into a JSON file and cost three CI runs. Files are testable; inline
shell is not.

It reads `public/yt-intel/*.json` for video ids, takes the newest report first, and writes
`public/yt-intel/thumbnails.json`. Keyless: `i.ytimg.com` serves thumbnails to anyone — but
not from every network, so a total failure is reported as `unavailable`, never as `ok`.

Usage: python scripts/thumbnails.py [out.json] [--sample 12]
"""
from __future__ import annotations

import glob
import json
import os
import sys


def main(argv: list[str]) -> int:
    out_path = "public/yt-intel/thumbnails.json"
    sample = 12
    args = [a for a in argv[1:] if not a.startswith("--")]
    if args:
        out_path = args[0]
    if "--sample" in argv:
        try:
            sample = int(argv[argv.index("--sample") + 1])
        except (IndexError, ValueError):
            pass

    sys.path.insert(0, ".")
    from yt_intel import thumbprint

    # newest report first: a thumbnail study of a topic nobody is searching for any more is
    # an archaeology exercise, not research
    reports = []
    for p in glob.glob("public/yt-intel/*.json"):
        base = os.path.basename(p)
        if base in ("index.json", "lanes.json", "doctor.json", "thumbnails.json") or base.startswith("comments-"):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if d.get("status") != "ok" or not d.get("rows"):
            continue
        reports.append((d.get("fetched_at") or 0, d))

    if not reports:
        print("no measured report to take thumbnails from — nothing to do")
        with open(out_path, "w") as f:
            json.dump({"status": "no_reports"}, f, indent=2)
        return 0

    reports.sort(key=lambda t: -t[0])
    topic, report = None, None
    for _, d in reports:
        topic, report = d.get("topic"), d
        break

    ids = [r["id"] for r in report["rows"] if r.get("id")][:sample]
    print(f"thumbnails from '{topic}' · {len(ids)} videos")

    fp = thumbprint.channel_fingerprint(ids, sample=sample)
    fp["topic"] = topic
    fp["taken_from"] = "newest measured report"
    with open(out_path, "w") as f:
        json.dump(fp, f, indent=2)
    print(f"wrote {out_path}")

    if fp.get("status") != "ok":
        print(f"  {fp.get('status')}: {fp.get('detail')}")
        return 1
    print(f"  n={fp['n']} · face_rate={fp['face_rate']} · contrast={fp['avg_contrast']} "
          f"· busy={fp['avg_busy']} · {fp['reading']}")
    print(f"  top hues: {fp['top_hexes'][:3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
