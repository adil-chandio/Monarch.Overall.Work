#!/usr/bin/env python3
"""
V13 — deepen the real-API niche evidence: channel-level statistics for every channel
found in the caught-on-camera lanes, bulk video statistics for the top millions-view
videos, and reverse teardowns where transcripts are actually obtainable.

Only public Data API fields are used. Private retention / CTR / RPM, arbitrary competitor
transcripts and verified "growing channel" rankings are NOT invented.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research" / "caught_on_camera_v13"
LANES = BASE / "api_evidence" / "lanes"
OUT = BASE / "api_evidence" / "channels"
OUT.mkdir(parents=True, exist_ok=True)

# Running this file by path puts the script directory (not the repo root) on sys.path.
sys.path.insert(0, str(ROOT))
from yt_intel import client, reverse  # noqa: E402


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    reports, rows = [], []
    for p in sorted(LANES.glob("*.json")):
        if p.name == "run.json":
            continue
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        reports.append({"file": p.name, "topic": d.get("topic"), "order": d.get("order"),
                        "status": d.get("status"), "count": d.get("count"),
                        "verdict": (d.get("decision") or {}).get("verdict") if isinstance(d.get("decision"), dict) else None})
        for r in d.get("rows", []) or []:
            r = dict(r)
            r["_lane"] = p.stem
            rows.append(r)
    print(f"lane reports={len(reports)} rows={len(rows)}", flush=True)

    # ---- channel-level statistics (1 quota unit per 50 ids) -----------------
    cids = sorted({r.get("channel_id") for r in rows if r.get("channel_id")})
    chans = []
    for i in range(0, len(cids), 50):
        try:
            d = client._api("channels", {"part": "snippet,statistics,contentDetails,brandingSettings",
                                         "id": ",".join(cids[i:i + 50])}, "channels")
        except Exception as e:
            print("channels.list failed:", type(e).__name__, flush=True)
            continue
        for it in d.get("items", []) or []:
            st = it.get("statistics", {}) or {}
            sn = it.get("snippet", {}) or {}
            chans.append({
                "channel_id": it.get("id"), "title": sn.get("title"),
                "handle": (sn.get("customUrl") or ""),
                "published": sn.get("publishedAt"),
                "country": sn.get("country"),
                "description": (sn.get("description") or "")[:800],
                "subscribers": int(st["subscriberCount"]) if st.get("subscriberCount") else None,
                "channel_views": int(st["viewCount"]) if st.get("viewCount") else None,
                "channel_video_count": int(st["videoCount"]) if st.get("videoCount") else None,
                "hidden_subscribers": st.get("hiddenSubscriberCount", False),
                "uploads_playlist": ((it.get("contentDetails") or {}).get("relatedPlaylists") or {}).get("uploads"),
                "keywords": ((it.get("brandingSettings") or {}).get("channel") or {}).get("keywords", ""),
            })
        time.sleep(0.3)
    chans.sort(key=lambda c: (c["channel_views"] or 0), reverse=True)
    save("channel_statistics_v13.json", {"count": len(chans), "channels": chans})
    print(f"channels resolved={len(chans)}", flush=True)

    # ---- millions-view videos: bulk details (1 unit per 50 ids) -------------
    ranked = [r for r in rows if isinstance(r.get("views"), int)]
    ranked.sort(key=lambda r: r["views"], reverse=True)
    seen, top = set(), []
    for r in ranked:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        top.append(r)
        if len(top) >= 60:
            break
    vids = []
    for i in range(0, len(top), 50):
        ids = [r["id"] for r in top[i:i + 50]]
        try:
            d = client._api("videos", {"part": "snippet,statistics,contentDetails",
                                       "id": ",".join(ids)}, "videos")
        except Exception as e:
            print("videos.list failed:", type(e).__name__, flush=True)
            continue
        for it in d.get("items", []) or []:
            st = it.get("statistics", {}) or {}
            sn = it.get("snippet", {}) or {}
            cd = it.get("contentDetails", {}) or {}
            vids.append({
                "id": it.get("id"), "title": sn.get("title"),
                "channel": sn.get("channelTitle"), "channel_id": sn.get("channelId"),
                "published": sn.get("publishedAt"), "duration": cd.get("duration"),
                "views": int(st["viewCount"]) if st.get("viewCount") else None,
                "likes": int(st["likeCount"]) if st.get("likeCount") else None,
                "comments": int(st["commentCount"]) if st.get("commentCount") else None,
                "tags": sn.get("tags", [])[:30],
                "description": (sn.get("description") or "")[:2500],
                "thumbnail": (sn.get("thumbnails", {}).get("maxres")
                              or sn.get("thumbnails", {}).get("high", {})).get("url", ""),
                "category_id": sn.get("categoryId"),
            })
        time.sleep(0.3)
    vids.sort(key=lambda v: (v["views"] or 0), reverse=True)
    save("million_view_videos_v13.json", {"count": len(vids), "videos": vids})
    print(f"video details resolved={len(vids)}", flush=True)

    # ---- reverse teardowns (transcript availability recorded honestly) ------
    td = []
    for v in vids[:6]:
        try:
            r = reverse.teardown(v["id"], fetch_transcript=True)
            td.append({"id": v["id"], "title": v["title"], "views": v["views"],
                       "teardown": r})
        except Exception as e:
            td.append({"id": v["id"], "title": v["title"], "views": v["views"],
                       "status": "teardown_failed", "detail": type(e).__name__})
        time.sleep(0.5)
    save("reverse_teardowns_v13.json", {"count": len(td), "items": td})

    # ---- run record ---------------------------------------------------------
    save("run.json", {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lane_reports": reports, "lane_rows": len(rows),
        "channels_resolved": len(chans), "video_details_resolved": len(vids),
        "reverse_teardowns": len(td),
        "key_present": bool(__import__("os").environ.get("YOUTUBE_API_KEY")),
        "secret_value_printed_or_stored": False,
        "boundary": ("Public Data API fields only. No private retention, CTR, RPM, "
                     "no invented transcripts, no verified growing-channel ranking, "
                     "no legal opinion, no guaranteed views."),
    })
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
