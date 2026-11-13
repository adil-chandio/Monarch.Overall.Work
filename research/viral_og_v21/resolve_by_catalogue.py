#!/usr/bin/env python3
"""Resolve a screenshot channel by the *shape of its catalogue*, not by one title.

Why: `title -> channel` keeps landing on tiny copycat uploads, because copycats reuse
winning titles verbatim (that is the whole trick) and a fresh upload can outrank the
original for its own title. What a copycat cannot fake is the catalogue: how many of
the screenshot's videos exist on the same channel, and do the view magnitudes line up.

This script takes the screenshot's own rows (titles + view text + duration) and scores
every channel that appears for any of those titles by:
    title match count (weight 1.0 per match, fuzzy)
  + view-magnitude agreement (log-distance penalty)
It writes api_evidence/catalogue_match_v21.json and prints a ranked shortlist per
channel. Read-only against public web search; no Data API search.
"""
from __future__ import annotations

import difflib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "viral_og_v21"))
import discovery_v21 as disc  # noqa: E402

BASE = ROOT / "research" / "viral_og_v21"
OUT = BASE / "api_evidence"
IDX = OUT / "drive_swipe_index.json"
TARGET = OUT / "catalogue_match_v21.json"


def view_num(txt):
    if not txt:
        return None
    t = str(txt).strip().replace(",", "").upper()
    mult = 1.0
    if t.endswith("K"):
        mult, t = 1e3, t[:-1]
    elif t.endswith("M"):
        mult, t = 1e6, t[:-1]
    elif t.endswith("B"):
        mult, t = 1e9, t[:-1]
    try:
        return float(t) * mult
    except ValueError:
        return None


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def main():
    idx = json.loads(IDX.read_text())["channels"]
    done = json.loads(TARGET.read_text()) if TARGET.exists() else {}
    for name, c in idx.items():
        if name in done:
            continue
        shots = [v for v in c.get("videos", []) if v.get("title")]
        scores = {}
        for v in shots[:6]:
            try:
                rows = disc.inner_search(v["title"])
            except Exception as e:  # noqa: BLE001
                print("  search err", repr(e)[:90], flush=True)
                continue
            want = norm(v["title"])
            wv = view_num(v.get("views_text"))
            for r in rows:
                have = norm(r.get("title"))
                if not have:
                    continue
                sim = difflib.SequenceMatcher(None, want, have).ratio()
                if sim < 0.8:
                    continue
                cid = r.get("channel_id")
                if not cid:
                    continue
                s = scores.setdefault(cid, {"channel_id": cid, "channel_title": r.get("channel_title"),
                                            "matches": 0, "view_pen": 0.0, "titles": []})
                s["matches"] += 1
                s["titles"].append(r.get("title"))
                rv = view_num(r.get("view_text"))
                if wv and rv:
                    s["view_pen"] += min(3.0, abs(math.log10(max(rv, 1)) - math.log10(max(wv, 1))))
        ranked = sorted(scores.values(),
                        key=lambda s: -(s["matches"] * 1.0 - 0.5 * s["view_pen"]))
        for s in ranked:
            s["score"] = round(s["matches"] - 0.5 * s["view_pen"], 3)
            s["view_pen"] = round(s["view_pen"], 3)
        done[name] = {"screenshot_name": name, "cluster": c.get("cluster"),
                      "shots": len(shots), "candidates": ranked[:5]}
        TARGET.write_text(json.dumps(done, indent=1, ensure_ascii=False) + "\n")
        top = ranked[0] if ranked else None
        print(f"{name[:26]:26s} -> " + (f"{top['channel_title'][:24]:24s} matches={top['matches']} "
                                        f"pen={top['view_pen']} score={top['score']}" if top else "NO CANDIDATE"),
              flush=True)
    print(f"wrote {TARGET.relative_to(ROOT)} for {len(done)} channels")


if __name__ == "__main__":
    main()
