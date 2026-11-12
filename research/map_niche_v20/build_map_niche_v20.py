#!/usr/bin/env python3
"""V20 — niche-locked deep dive: MAP / GEOGRAPHY, English, US-first, short + long.

Why: the user's stated target is a US/English audience, 3D animation is available, and V18
ranked map/geography #1 for that combination. V20 stops general sampling and goes all-in on
this one niche:

  1. 12 search lanes = 4 sub-themes x (short | medium | long)
       - geography explainer   ("geography explained animation")
       - map animation         ("map animation country facts")
       - borders / geopolitics ("why borders look like this map")
       - history maps          ("history map animation explained")
  2. Top-25 channel catalogues (up to 100 uploads each) -> per-channel median, 3x outliers,
     short/medium/long ladder, title patterns, series stems.
  3. Bucket x outlier cross-tabs inside the niche only.
  4. Thumbnail pixel stats for the niche outliers (public image GET; no video download).
  5. Caption attempt on the niche outliers (public renderer; records every outcome).

Boundary: public Data API metadata + public thumbnails + public caption text. No video or
audio download, no frame inspection, no private analytics, no invented transcripts, no
causal/virality/legal/monetisation claim.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from yt_intel import client, forensic, thumbprint  # noqa: E402

BASE = ROOT / "research" / "map_niche_v20"
OUT = BASE / "api_evidence"
OUT.mkdir(parents=True, exist_ok=True)

KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
if not KEY:
    raise SystemExit("YOUTUBE_API_KEY is not set; refusing to call this a real-API run")

SUBTHEMES = [
    {"slug": "geo_explainer", "q": "geography explained animation"},
    {"slug": "map_animation", "q": "map animation country facts"},
    {"slug": "borders_geo", "q": "why borders look like this map"},
    {"slug": "history_map", "q": "history map animation explained"},
]
DURS = [("short", "short"), ("medium", "medium"), ("long", "long")]
LANES = [{"slug": f"{s['slug']}_{d}_all", "q": s["q"], "videoDuration": dv, "bucket": d,
          "order": "viewCount"} for s in SUBTHEMES for d, dv in DURS]

SHORT_MAX, MEDIUM_MAX = 240, 1200
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def save(n, o):
    (OUT / n).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def log(*a):
    print(*a, flush=True)


def parse_item(it):
    sn, st, cd, stt = (it.get(k, {}) or {} for k in ("snippet", "statistics", "contentDetails", "status"))
    dur = forensic.parse_duration(cd.get("duration", "")) or 0
    age = forensic.parse_age_days(sn.get("publishedAt", ""))
    views = int(st.get("viewCount") or 0)
    likes = int(st.get("likeCount") or 0)
    cm = int(st.get("commentCount") or 0)
    desc = sn.get("description") or ""
    title = sn.get("title", "") or ""
    chap = len(re.findall(r"(?m)^\s*(?:\d{1,2}:)?\d{1,2}:\d{2}\s", desc))
    return {
        "id": it.get("id"), "title": title, "channel": sn.get("channelTitle", ""),
        "channel_id": sn.get("channelId", ""), "published": sn.get("publishedAt", ""),
        "published_month": (sn.get("publishedAt") or "")[:7],
        "age_days": round(age, 1) if age else None, "duration": cd.get("duration", ""),
        "duration_seconds": dur, "views": views, "likes": likes, "comments": cm,
        "like_rate": round(likes / views, 5) if views else None,
        "comment_rate": round(cm / views, 5) if views else None,
        "views_per_day": round((views / age) if age else 0, 1),
        "title_len": len(title), "title_words": len(title.split()),
        "has_number": bool(re.search(r"\d", title)), "has_question": "?" in title,
        "has_hashtag": "#" in title, "has_emoji": bool(re.search("[\U0001F300-\U0001FAFF]", title)),
        "tags": (sn.get("tags") or [])[:30], "tag_count": len(sn.get("tags") or []),
        "description": desc[:6000], "description_words": len(desc.split()),
        "chapter_count": chap, "caption": cd.get("caption") == "true",
        "definition": cd.get("definition"), "made_for_kids":
            bool(stt.get("madeForKids") or stt.get("selfDeclaredMadeForKids")),
        "category_id": sn.get("categoryId"), "default_language": sn.get("defaultLanguage"),
        "default_audio_language": sn.get("defaultAudioLanguage"),
        "thumbnail": (sn.get("thumbnails", {}).get("maxres") or sn.get("thumbnails", {}).get("high", {})).get("url", ""),
    }


def videos(ids):
    ids = [i for i in dict.fromkeys(ids) if i]
    out = []
    for i in range(0, len(ids), 50):
        try:
            d = client._api("videos", {"part": "snippet,statistics,contentDetails,status",
                                       "id": ",".join(ids[i:i + 50])}, "videos")
        except Exception as e:  # noqa: BLE001
            log("  videos failed", repr(e)[:120])
            continue
        out += [parse_item(x) for x in d.get("items", []) or []]
        time.sleep(0.1)
    return out


def search_lane(lane):
    params = {"part": "snippet", "q": lane["q"], "type": "video", "maxResults": 50,
              "order": "viewCount", "regionCode": "US", "relevanceLanguage": "en",
              "safeSearch": "moderate", "videoDuration": lane["videoDuration"]}
    try:
        d = client._api("search", params, "search")
        ids = [x["id"]["videoId"] for x in d.get("items", []) if x.get("id", {}).get("videoId")]
        return {"status": "ok" if ids else "empty", "ids": ids, "params": params}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "ids": [], "detail": repr(e)[:200], "params": params}


def channel_info(cid):
    try:
        d = client._api("channels", {"part": "snippet,statistics,contentDetails", "id": cid}, "channels")
    except Exception:  # noqa: BLE001
        return None, None
    it = (d.get("items") or [None])[0]
    if not it:
        return None, None
    sn, st, cd = (it.get(k, {}) or {} for k in ("snippet", "statistics", "contentDetails"))
    return {
        "channel_id": cid, "title": sn.get("title"), "handle": sn.get("customUrl"),
        "country": sn.get("country"), "published": sn.get("publishedAt"),
        "subs": int(st["subscriberCount"]) if st.get("subscriberCount") else None,
        "channel_views": int(st["viewCount"]) if st.get("viewCount") else None,
        "video_count": int(st["videoCount"]) if st.get("videoCount") else None,
        "age_days": round(forensic.parse_age_days(sn.get("publishedAt", "")) or 0, 1),
    }, (cd.get("relatedPlaylists") or {}).get("uploads")


def upload_ids(pid, pages=2):
    out, token = [], None
    for _ in range(pages):
        p = {"part": "contentDetails", "playlistId": pid, "maxResults": 50}
        if token:
            p["pageToken"] = token
        try:
            d = client._api("playlistItems", p, "playlistItems")
        except Exception:  # noqa: BLE001
            break
        out += [(i.get("contentDetails") or {}).get("videoId") for i in d.get("items", []) or []]
        token = d.get("nextPageToken")
        if not token:
            break
    return [i for i in out if i]


def bucket(s):
    return "short" if s < SHORT_MAX else ("medium" if s <= MEDIUM_MAX else "long")


def stats(rows):
    if not rows:
        return {"n": 0}
    v = sorted(r["views"] for r in rows)
    return {
        "n": len(rows), "total": sum(v), "median": int(statistics.median(v)),
        "p25": v[len(v) // 4], "p75": v[(3 * len(v)) // 4], "max": v[-1],
        "median_duration": int(statistics.median([r["duration_seconds"] for r in rows])),
        "short_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "short") / len(rows), 3),
        "medium_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "medium") / len(rows), 3),
        "long_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "long") / len(rows), 3),
        "number_rate": round(sum(1 for r in rows if r["has_number"]) / len(rows), 3),
        "question_rate": round(sum(1 for r in rows if r["has_question"]) / len(rows), 3),
        "emoji_rate": round(sum(1 for r in rows if r["has_emoji"]) / len(rows), 3),
        "hashtag_rate": round(sum(1 for r in rows if r["has_hashtag"]) / len(rows), 3),
        "median_title_words": statistics.median([r["title_words"] for r in rows]),
        "median_desc_words": statistics.median([r["description_words"] for r in rows]),
        "chapter_ge3_rate": round(sum(1 for r in rows if r["chapter_count"] >= 3) / len(rows), 3),
        "caption_rate": round(sum(1 for r in rows if r["caption"]) / len(rows), 3),
        "median_tag_count": statistics.median([r["tag_count"] for r in rows]),
        "median_like_rate": statistics.median([r["like_rate"] for r in rows if r["like_rate"] is not None]) if any(r["like_rate"] is not None for r in rows) else None,
        "median_views_per_day": int(statistics.median([r["views_per_day"] for r in rows])),
    }


def cap_attempt(vid):
    url = f"https://youtubetotranscript.com/transcript?v={urllib.parse.quote(vid)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode("utf-8", "replace")
            code = r.status
    except Exception as e:  # noqa: BLE001
        return {"id": vid, "http": getattr(e, "code", 0), "status": "blocked_or_error",
                "detail": repr(e)[:140], "words": 0, "text": ""}
    if "This video has no captions" in html:
        return {"id": vid, "http": code, "status": "no_captions", "words": 0, "text": ""}
    if "This video isn't available" in html:
        return {"id": vid, "http": code, "status": "unavailable", "words": 0, "text": ""}
    m = re.search(r"<h2[^>]*>\s*Transcript\s*</h2>(.*?)(?:Back To Top)", html, re.S)
    if not m:
        return {"id": vid, "http": code, "status": "parse_failed", "words": 0, "text": ""}
    txt = re.sub(r"<[^>]+>", " ", m.group(1))
    txt = re.sub(r"\s+", " ", txt).strip()
    return {"id": vid, "http": code, "status": "ok", "text": txt[:8000],
            "words": len(re.findall(r"\b[\w'-]+\b", txt))}



PHRASE_BUCKETS = {
    "sequel_or_next": r"\b(part\s*2|part two|next (video|part|episode)|more of this|do more|make more)\b",
    "did_not_know": r"\b(i (never|didn'?t) kn(e|o)w|had no idea|never knew|til that|today i learned|tIL)\b",
    "correction_claim": r"\b(actually|wrong|incorrect|not true|false|misleading|you forgot|umm actually)\b",
    "ask_how_made": r"\b(how (did|do) you (make|animate|edit)|what (app|software|program)|which (app|software)|blender|after effects)\b",
    "country_request": r"\b(do|make|cover|please do)\b.{0,40}\b(country|countries|state|india|china|usa|america|africa|europe|brazil|russia)\b",
    "personal_tie": r"\b(i (live|am from|was born)|my (country|city|town|state)|here in)\b",
    "map_nerd": r"\b(border|enclave|exclave|parallel|meridian|projection|cartograph)\w*\b",
}


def mine_comments(vid, max_results=20):
    """Public commentThreads, relevance order. Counts are of FETCHED comments only."""
    try:
        d = client._api("commentThreads", {"part": "snippet", "videoId": vid,
                                          "maxResults": max_results, "order": "relevance",
                                          "textFormat": "plainText"}, "commentThreads")
    except Exception as e:  # noqa: BLE001
        return {"id": vid, "status": "error", "detail": repr(e)[:160], "fetched": 0, "buckets": {}}
    texts = []
    for it in d.get("items", []) or []:
        sn = ((it.get("snippet") or {}).get("topLevelComment") or {}).get("snippet") or {}
        t = (sn.get("textDisplay") or "").strip()
        if t:
            texts.append(t)
    if not texts:
        return {"id": vid, "status": "no_comments_returned", "fetched": 0, "buckets": {}}
    buckets = {}
    for name, rx in PHRASE_BUCKETS.items():
        n = sum(1 for t in texts if re.search(rx, t, re.I))
        buckets[name] = {"n": n, "share": round(n / len(texts), 3)}
    lenses = sum(1 for t in texts if len(re.findall(r"\b\w+\b", t)) >= 25)
    questions = sum(1 for t in texts if "?" in t)
    return {"id": vid, "status": "ok", "fetched": len(texts), "buckets": buckets,
            "questions": questions, "long_comments": lenses,
            "sample": [t[:220] for t in texts[:5]]}


def main():
    t0 = time.time()
    lanes_out, all_ids = [], []
    for l in LANES:
        r = search_lane(l)
        lanes_out.append({**l, **r, "ids_count": len(r["ids"])})
        all_ids += r["ids"]
        log(f"lane {l['slug']:24s} {r['status']:6s} ids={len(r['ids'])}")
    rows = videos(all_ids)
    log(f"videos resolved {len(rows)} / unique ids {len(set(all_ids))}")

    by_lane = {l["slug"]: [r for r in rows if r["id"] in set(l["ids"])] for l in lanes_out}
    lane_stats = {k: stats(v) for k, v in by_lane.items()}

    # channel ranking inside the niche
    ch_agg = defaultdict(lambda: {"n": 0, "views": 0, "name": "", "ids": []})
    for r in rows:
        a = ch_agg[r["channel_id"] or r["channel"]]
        a["n"] += 1
        a["views"] += r["views"]
        a["name"] = r["channel"] or a["name"]
        a["ids"].append(r["id"])
    top_ch = sorted(ch_agg.items(), key=lambda kv: -kv[1]["views"])[:25]

    catalogue, chan_rows = {}, []
    for i, (cid, a) in enumerate(top_ch, 1):
        info, pid = channel_info(cid)
        if not info:
            continue
        ids = upload_ids(pid) if pid else []
        cr = videos(ids)
        cr = [r for r in cr if r["channel_id"] == cid]
        st = stats(cr)
        med = statistics.median([r["views"] for r in cr]) if cr else 0
        outl = sorted([r for r in cr if med and r["views"] >= 3 * med], key=lambda r: -r["views"])
        chan_rows.append({**info, **st, "corpus_hits": a["n"], "corpus_views": a["views"],
                          "outlier_count": len(outl)})
        catalogue[info["title"] or cid] = {
            "channel": info, "stats": st,
            "ladder": {b: stats([r for r in cr if bucket(r["duration_seconds"]) == b])
                       for b in ("short", "medium", "long")},
            "outliers": [{k: r[k] for k in ("id", "title", "views", "duration_seconds", "published",
                                            "views_per_day", "like_rate", "comment_rate",
                                            "chapter_count", "description_words", "tag_count", "caption")}
                         for r in outl[:12]],
            "top_by_views": [{k: r[k] for k in ("id", "title", "views", "duration_seconds")}
                             for r in sorted(cr, key=lambda r: -r["views"])[:8]],
        }
        log(f"  ch [{i}/{len(top_ch)}] {info['title'][:26]:26s} n={len(cr):3d} med={int(med):>11,} out={len(outl)}")

    # niche-wide outliers (across the whole lane corpus, not per channel)
    allv = sorted(rows, key=lambda r: -r["views"])
    out_ids = {r["id"] for c in catalogue.values() for r in c["outliers"]}
    nic_out = [r for r in rows if r["id"] in out_ids]
    rest = [r for r in rows if r["id"] not in out_ids]

    thumbs = []
    for r in [x for x in nic_out if x["views"] >= 1_000_000][:30]:
        try:
            arr, size = thumbprint.fetch(r["id"])
            if arr is not None:
                t = thumbprint.analyse(arr, size)
                thumbs.append({"id": r["id"], "title": r["title"], "views": r["views"],
                               "bucket": bucket(r["duration_seconds"]), **t})
        except Exception:  # noqa: BLE001
            continue

    caps = []
    for r in [x for x in nic_out if x["views"] >= 1_000_000][:12]:
        c = cap_attempt(r["id"])
        c.update({"title": r["title"], "channel": r["channel"], "views": r["views"],
                  "duration_seconds": r["duration_seconds"]})
        caps.append(c)

    cm = []
    for r in [x for x in allv if x["views"] >= 2_000_000][:12]:
        c = mine_comments(r["id"])
        c.update({"title": r["title"], "channel": r["channel"], "views": r["views"],
                  "duration_seconds": r["duration_seconds"]})
        cm.append(c)
    agg = defaultdict(int)
    fetched = 0
    for c in cm:
        fetched += c.get("fetched", 0)
        for k, v in (c.get("buckets") or {}).items():
            agg[k] += v["n"]
    comment_agg = {"videos_attempted": len(cm), "comments_fetched": fetched,
                   "order": "relevance, max 20 per video", "bucket_counts": dict(agg),
                   "bucket_share_of_fetched": {k: round(v / fetched, 3) for k, v in agg.items()} if fetched else {},
                   "boundary": ("Shares are of FETCHED relevance-ordered comments only, not of all "
                                "viewers; the silent majority is invisible. No sentiment scoring, no "
                                "demographic inference.")}

    run = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "key_present": True, "secret_value_printed_or_stored": False,
        "niche": "map / geography, English, US-first (regionCode=US, relevanceLanguage=en)",
        "lanes": len(LANES), "lane_rows": sum(l["ids_count"] for l in lanes_out),
        "unique_videos": len({r["id"] for r in rows}), "channels_in_lanes": len(ch_agg),
        "channels_deep": len(catalogue), "catalogue_videos": sum(c["stats"].get("n", 0) for c in catalogue.values()),
        "niche_outliers_3x": len(nic_out),
        "thumbnail_stats": len(thumbs), "caption_attempts": len(caps),
        "comments_fetched": comment_agg["comments_fetched"],
        "caption_status_counts": dict(Counter(c["status"] for c in caps)),
        "quota_used_approx": client.BUDGET.state.get("used", 0),
        "quota_calls": dict(client.BUDGET.state.get("calls", {})),
        "elapsed_s": round(time.time() - t0, 1),
        "boundary": ("Public Data API metadata + public thumbnails + public caption text only. "
                     "No video/audio download, no frame inspection, no private retention/CTR/RPM, "
                     "no invented transcripts, no verified growth ranking, no causal claim, no "
                     "legal/human/upload/monetisation claim."),
    }
    save("run_v20.json", run)
    save("lanes_v20.json", {"lanes": lanes_out})
    save("lane_stats_v20.json", lane_stats)
    save("videos_v20.json", {"count": len(rows), "videos": rows})
    save("channels_v20.json", {"count": len(chan_rows), "channels": chan_rows})
    save("channel_deep_v20.json", {"catalogue": catalogue,
                                  "outlier_cross": {"outliers": stats(nic_out), "rest": stats(rest)}})
    save("thumbnails_v20.json", {"count": len(thumbs), "rows": thumbs})
    save("captions_v20.json", {"count": len(caps), "attempts": caps})
    save("comments_v20.json", {"aggregate": comment_agg, "videos": cm})
    log(f"comments fetched {comment_agg['comments_fetched']} across {len(cm)} videos; buckets {comment_agg['bucket_counts']}")
    log(f"done in {run['elapsed_s']}s — {run['unique_videos']} videos, {len(catalogue)} channels, "
        f"{len(nic_out)} outliers, {len(thumbs)} thumbs, captions {run['caption_status_counts']}")
    print(json.dumps(run, indent=1))


if __name__ == "__main__":
    main()
