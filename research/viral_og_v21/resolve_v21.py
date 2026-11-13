#!/usr/bin/env python3
"""V21 resolver — resolve the swipe-file channels once, then cache them.

The Data API's search endpoint returns 429 bursts from CI IPs. Channel resolution must not
depend on it: handles resolve through `channels?forHandle` (cheap, not search), and anything
left over is resolved through search with a long gap between calls, then written to
channel_cache_v21.json so later runs cost zero search calls.

Run before build_viral_og_v21.py. Idempotent: already-cached names are skipped.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from yt_intel import client  # noqa: E402

BASE = ROOT / "research" / "viral_og_v21"
OUT = BASE / "api_evidence"
CACHE = OUT / "channel_cache_v21.json"
IDX = OUT / "drive_swipe_index.json"

if not os.environ.get("YOUTUBE_API_KEY", "").strip():
    raise SystemExit("YOUTUBE_API_KEY is not set")


def log(*a):
    print(*a, flush=True)


def brief(it, how):
    sn, st, cd = (it.get(k, {}) or {} for k in ("snippet", "statistics", "contentDetails"))
    return {"channel_id": it.get("id"), "title": sn.get("title"), "handle": sn.get("customUrl"),
            "country": sn.get("country"), "published": sn.get("publishedAt"),
            "subs": int(st["subscriberCount"]) if st.get("subscriberCount") else None,
            "channel_views": int(st["viewCount"]) if st.get("viewCount") else None,
            "video_count": int(st["videoCount"]) if st.get("videoCount") else None,
            "uploads": (cd.get("relatedPlaylists") or {}).get("uploads"),
            "resolved_by": how}


def try_handle(h):
    for param in ({"part": "snippet,statistics,contentDetails", "forHandle": h.lstrip("@")},
                  {"part": "snippet,statistics,contentDetails", "forUsername": h.lstrip("@")}):
        try:
            d = client._api("channels", param, "channels")
            it = (d.get("items") or [None])[0]
            if it:
                return brief(it, "forHandle")
        except Exception as e:  # noqa: BLE001
            log("   handle err", repr(e)[:90])
    return None


def try_title(title, wait=25):
    """A screenshot's own video title -> the channel that owns that exact video."""
    for attempt in range(3):
        try:
            d = client._api("search", {"part": "snippet", "q": title, "type": "video",
                                       "maxResults": 3, "regionCode": "US",
                                       "relevanceLanguage": "en"}, "search")
            it = (d.get("items") or [None])[0]
            if not it:
                return None
            cid = (it.get("snippet") or {}).get("channelId")
            dd = client._api("channels", {"part": "snippet,statistics,contentDetails", "id": cid}, "channels")
            cit = (dd.get("items") or [None])[0]
            return brief(cit, "search:title") if cit else None
        except Exception as e:  # noqa: BLE001
            log(f"   search 429/err (attempt {attempt + 1}/3): {repr(e)[:70]}")
            time.sleep(wait * (attempt + 1))
    return None


def main():
    idx = json.loads(IDX.read_text())["channels"]
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    log(f"cache has {len(cache)}/{len(idx)}")

    for name, c in idx.items():
        if name in cache:
            continue
        titles = [v["title"] for v in c.get("videos", []) if v.get("title")]
        got = None
        if c.get("handle"):
            got = try_handle(c["handle"])
            if got:
                # handle can point at a same-named impostor; keep it only if plausible
                subs_shot = c.get("subs") or ""
                if subs_shot and got.get("subs"):
                    try:
                        want = float(str(subs_shot).replace("K", "e3").replace("M", "e6"))
                        if want and got["subs"] < want * 0.35:
                            log(f"   {name}: handle subs {got['subs']:,} << screenshot {subs_shot}; "
                                f"trying title instead")
                            got = None
                    except ValueError:
                        pass
        if not got and titles:
            got = try_title(max(titles, key=len))
        if got:
            got["screenshot_name"] = name
            got["cluster"] = c.get("cluster")
            cache[name] = got
            log(f"  ok {name[:26]:26s} -> {got['title'][:30]:30s} {got['subs']} by {got['resolved_by']}")
        else:
            log(f"  FAILED {name}")
        CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False) + "\n")
        time.sleep(6)

    log(f"cache now {len(cache)}/{len(idx)}; unresolved {[n for n in idx if n not in cache]}")


if __name__ == "__main__":
    main()
