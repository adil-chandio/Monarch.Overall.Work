#!/usr/bin/env python3
"""V17 next-level niche forensic — real YouTube Data API + public metadata only.

What this does:
  * 20 search lanes across next-level fun / explainer / microdrama / faceless formats.
  * mostPopular snapshots for US, PK, GB, IN.
  * bulk video details (snippet, statistics, contentDetails, status, topicDetails,
    recordingDetails), channel statistics, recent uploads per top channel.
  * top-comment mining, transcript teardowns where captions are actually public,
    and thumbnail image statistics (not OCR, not face recognition, not video frames).
  * an explainable Markdown data appendix plus machine-readable JSON evidence.

Honest boundary:
  * No competitor video or audio is downloaded. No video frames are inspected.
  * No private retention, CTR, RPM, impression data, or verified growth ranking.
  * No invented transcripts. No causal claim that any feature caused virality.
  * No legal opinion, human creative approval, monetisation guarantee, upload/publish,
    guaranteed views, virality, perfection, or family-safety claim.
"""
from __future__ import annotations
import datetime as dt
import json
import os
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from yt_intel import client, forensic, reverse, thumbprint  # noqa: E402

BASE = ROOT / "research" / "next_level_niche_v17"
OUT = BASE / "api_evidence"
OUT.mkdir(parents=True, exist_ok=True)

KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
if not KEY:
    raise SystemExit("YOUTUBE_API_KEY is not set; refusing to call this a real-API run")

# 20 lanes: all-time high-view + recent high-signal for 10 next-level themes.
LANES = [
    {"slug": "ai_tutorial_all", "theme": "AI tool tutorial", "q": "AI tool tutorial screen recording", "order": "viewCount", "days": 0},
    {"slug": "ai_tutorial_recent", "theme": "AI tool tutorial", "q": "AI tool tutorial 2026", "order": "date", "days": 365},
    {"slug": "microdrama_all", "theme": "microdrama", "q": "microdrama short series", "order": "viewCount", "days": 0},
    {"slug": "microdrama_recent", "theme": "microdrama", "q": "microdrama 2026", "order": "date", "days": 365},
    {"slug": "science_humor_all", "theme": "science with humor", "q": "science explained with humor", "order": "viewCount", "days": 0},
    {"slug": "science_humor_recent", "theme": "science with humor", "q": "funny science explainer 2026", "order": "date", "days": 365},
    {"slug": "satisfying_all", "theme": "oddly satisfying", "q": "oddly satisfying restoration", "order": "viewCount", "days": 0},
    {"slug": "satisfying_recent", "theme": "oddly satisfying", "q": "satisfying before after 2026", "order": "date", "days": 365},
    {"slug": "animal_rescue_all", "theme": "animal rescue", "q": "animal rescue caught on camera", "order": "viewCount", "days": 0},
    {"slug": "animal_rescue_recent", "theme": "animal rescue", "q": "funny animal rescue 2026", "order": "date", "days": 365},
    {"slug": "viral_breakdown_all", "theme": "viral breakdown", "q": "viral video breakdown analysis", "order": "viewCount", "days": 0},
    {"slug": "viral_breakdown_recent", "theme": "viral breakdown", "q": "why this video went viral 2026", "order": "date", "days": 365},
    {"slug": "map_animation_all", "theme": "map animation", "q": "map animation explained geography", "order": "viewCount", "days": 0},
    {"slug": "map_animation_recent", "theme": "map animation", "q": "geography animated explainer 2026", "order": "date", "days": 365},
    {"slug": "mini_doc_all", "theme": "mini documentary", "q": "mini documentary business case study", "order": "viewCount", "days": 0},
    {"slug": "mini_doc_recent", "theme": "mini documentary", "q": "business documentary 2026", "order": "date", "days": 365},
    {"slug": "faceless_comedy_all", "theme": "faceless comedy", "q": "faceless comedy sketch", "order": "viewCount", "days": 0},
    {"slug": "faceless_comedy_recent", "theme": "faceless comedy", "q": "faceless comedy short 2026", "order": "date", "days": 365},
    {"slug": "sleep_ambient_all", "theme": "sleep / ASMR", "q": "sleep story ambient animation", "order": "viewCount", "days": 0},
    {"slug": "sleep_ambient_recent", "theme": "sleep / ASMR", "q": "ASMR animation 2026", "order": "date", "days": 365},
]

REGIONS = ["US", "PK", "GB", "IN"]
UNSAFE_TITLE = re.compile(
    r"\b(murder|homicide|suicide|death|dead|kill|killed|shooting|stab|gore|blood|"
    r"autopsy|bomb|blast|explosion|terror|war|missile|crash|rollover|drowning|"
    r"abuse|assault|rape|kidnap|robbery|police chase|beheading|execution)\b", re.I)
DESC_PATTERNS = {
    "subscribe": r"\bsubscribe\b", "link": r"https?://|\blink in (bio|description)\b",
    "follow": r"\bfollow\b", "part2": r"\bpart\s*2\b|\bnext part\b|\bepisode\b|\bseries\b",
    "comment": r"\bcomment(s| below)?\b", "discord": r"\bdiscord\b", "patreon": r"\bpatreon\b",
    "ai": r"\bAI\b|\bartificial intelligence\b", "voice": r"\bvoiceover\b|\bnarrat",
    "credits": r"\bcredits?\b|\bsource(s)?\b", "chapters": r"\bchapters?\b|\btimestamps?\b",
}

def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def log(*a):
    print(*a, flush=True)

def iso_since(days):
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_video_item(it):
    sn = it.get("snippet", {}) or {}
    st = it.get("statistics", {}) or {}
    cd = it.get("contentDetails", {}) or {}
    status = it.get("status", {}) or {}
    td = it.get("topicDetails", {}) or {}
    rd = it.get("recordingDetails", {}) or {}
    dur = forensic.parse_duration(cd.get("duration", "")) or 0
    age = forensic.parse_age_days(sn.get("publishedAt", ""))
    views = int(st.get("viewCount") or 0)
    likes = int(st.get("likeCount") or 0)
    comments = int(st.get("commentCount") or 0)
    vph = forensic.vph(views, age)
    return {
        "id": it.get("id"), "title": sn.get("title", ""),
        "channel": sn.get("channelTitle", ""), "channel_id": sn.get("channelId", ""),
        "published": sn.get("publishedAt", ""), "age_days": round(age, 1) if age else None,
        "duration": cd.get("duration", ""), "duration_seconds": dur,
        "views": views, "likes": likes, "comments": comments,
        "like_rate": round(likes / views, 5) if views else None,
        "comment_rate": round(comments / views, 5) if views else None,
        "views_per_day": round(vph * 24, 1) if vph else None,
        "category_id": sn.get("categoryId"), "default_language": sn.get("defaultLanguage"),
        "default_audio_language": sn.get("defaultAudioLanguage"),
        "live_broadcast_content": sn.get("liveBroadcastContent"),
        "tags": (sn.get("tags") or [])[:30],
        "description": (sn.get("description") or "")[:4000],
        "description_length": len(sn.get("description") or ""),
        "thumbnail": (sn.get("thumbnails", {}).get("maxres") or sn.get("thumbnails", {}).get("high", {})).get("url", ""),
        "caption": cd.get("caption") == "true", "definition": cd.get("definition"),
        "dimension": cd.get("dimension"), "projection": cd.get("projection"),
        "licensed_content": bool(cd.get("licensedContent")),
        "privacy_status": status.get("privacyStatus"), "upload_status": status.get("uploadStatus"),
        "embeddable": bool(status.get("embeddable")),
        "public_stats_viewable": bool(status.get("publicStatsViewable")),
        "made_for_kids": bool(status.get("madeForKids") or status.get("selfDeclaredMadeForKids")),
        "topic_categories": td.get("topicCategories", [])[:12],
        "topic_ids": td.get("topicIds", [])[:12],
        "recording_date": rd.get("recordingDate"),
        "location_description": rd.get("locationDescription"),
        "title_safety_excluded": bool(UNSAFE_TITLE.search(sn.get("title", "") or "")),
    }

def video_details(ids):
    ids = [i for i in dict.fromkeys(ids) if i]
    out = []
    for i in range(0, len(ids), 50):
        try:
            d = client._api("videos", {
                "part": "snippet,statistics,contentDetails,status,topicDetails,recordingDetails",
                "id": ",".join(ids[i:i + 50])}, "videos")
        except Exception as e:
            log("  videos.list failed", type(e).__name__, str(e)[:160])
            continue
        for it in d.get("items", []) or []:
            out.append(parse_video_item(it))
        time.sleep(0.15)
    return out

def search_lane(lane):
    params = {
        "part": "snippet", "q": lane["q"], "type": "video", "maxResults": 50,
        "order": lane["order"], "regionCode": "US", "relevanceLanguage": "en",
        "safeSearch": "moderate",
    }
    if lane["days"]:
        params["publishedAfter"] = iso_since(lane["days"])
    try:
        d = client._api("search", params, "search")
        ids = [x["id"]["videoId"] for x in d.get("items", []) if x.get("id", {}).get("videoId")]
        return {"status": "ok" if ids else "empty", "ids": ids,
                "page": d.get("pageInfo", {}), "params": params}
    except Exception as e:
        return {"status": "error", "ids": [], "detail": repr(e), "params": params}

def most_popular(region):
    try:
        d = client._api("videos", {
            "part": "snippet,statistics,contentDetails,status,topicDetails",
            "chart": "mostPopular", "regionCode": region, "maxResults": 50}, "videos")
        return {"region": region, "status": "ok", "rows": [parse_video_item(it) for it in d.get("items", []) or []]}
    except Exception as e:
        return {"region": region, "status": "error", "detail": repr(e), "rows": []}

def video_categories():
    try:
        d = client._api("videoCategories", {"part": "snippet", "regionCode": "US"}, "videoCategories")
        return {it["id"]: it.get("snippet", {}).get("title") for it in d.get("items", []) or []}
    except Exception:
        return {}

def channel_details(ids):
    ids = [i for i in dict.fromkeys(ids) if i]
    out = []
    for i in range(0, len(ids), 50):
        try:
            d = client._api("channels", {
                "part": "snippet,statistics,contentDetails,brandingSettings,topicDetails,status",
                "id": ",".join(ids[i:i + 50])}, "channels")
        except Exception as e:
            log("  channels.list failed", type(e).__name__, str(e)[:160])
            continue
        for it in d.get("items", []) or []:
            sn = it.get("snippet", {}) or {}
            st = it.get("statistics", {}) or {}
            cd = it.get("contentDetails", {}) or {}
            bs = (it.get("brandingSettings", {}) or {}).get("channel", {}) or {}
            td = it.get("topicDetails", {}) or {}
            status = it.get("status", {}) or {}
            age = forensic.parse_age_days(sn.get("publishedAt", ""))
            out.append({
                "channel_id": it.get("id"), "title": sn.get("title"),
                "handle": sn.get("customUrl"), "published": sn.get("publishedAt"),
                "channel_age_days": round(age, 1) if age else None,
                "country": sn.get("country"), "description": (sn.get("description") or "")[:1200],
                "subscribers": int(st["subscriberCount"]) if st.get("subscriberCount") else None,
                "channel_views": int(st["viewCount"]) if st.get("viewCount") else None,
                "channel_video_count": int(st["videoCount"]) if st.get("videoCount") else None,
                "hidden_subscribers": bool(st.get("hiddenSubscriberCount")),
                "uploads_playlist": (cd.get("relatedPlaylists") or {}).get("uploads"),
                "keywords": bs.get("keywords", ""), "topic_categories": td.get("topicCategories", [])[:12],
                "made_for_kids": bool(status.get("madeForKids") or status.get("selfDeclaredMadeForKids")),
            })
        time.sleep(0.15)
    out.sort(key=lambda c: (c["channel_views"] or 0), reverse=True)
    return out

def recent_uploads(ch):
    pid = ch.get("uploads_playlist")
    if not pid:
        return []
    try:
        d = client._api("playlistItems", {"part": "snippet,contentDetails", "playlistId": pid, "maxResults": 25}, "playlistItems")
    except Exception:
        return []
    out = []
    for it in d.get("items", []) or []:
        cd = it.get("contentDetails", {}) or {}
        sn = it.get("snippet", {}) or {}
        vid = cd.get("videoId")
        if not vid:
            continue
        out.append({"id": vid, "title": sn.get("title", ""),
                    "published": cd.get("videoPublishedAt") or sn.get("publishedAt", ""),
                    "channel_id": ch["channel_id"], "channel": ch["title"]})
    return out

def comments_for(video_id, limit=25):
    try:
        d = client._api("commentThreads", {"part": "snippet,replies", "videoId": video_id,
                                           "maxResults": limit, "order": "relevance",
                                           "textFormat": "plainText"}, "commentThreads")
    except Exception as e:
        return {"video_id": video_id, "status": "error", "detail": repr(e), "comments": []}
    items = []
    for it in d.get("items", []) or []:
        sn = it.get("snippet", {}) or {}
        top = sn.get("topLevelComment", {}).get("snippet", {}) or {}
        items.append({"text": top.get("textDisplay", ""), "likes": int(top.get("likeCount") or 0),
                      "replies": int(sn.get("totalReplyCount") or 0),
                      "author": top.get("authorDisplayName", ""),
                      "published": top.get("publishedAt", "")})
    return {"video_id": video_id, "status": "ok" if items else "empty", "comments": items}

def teardown_for(video_id):
    try:
        return {"video_id": video_id, "status": "ok", "teardown": reverse.teardown(video_id, fetch_transcript=True)}
    except Exception as e:
        return {"video_id": video_id, "status": "error", "detail": repr(e)}

def thumbnail_stats(video_ids):
    rows = []
    for vid in video_ids:
        try:
            arr, size = thumbprint.fetch(vid)
            if arr is None:
                continue
            rec = thumbprint.analyse(arr, size)
            rec["id"] = vid
            rows.append(rec)
        except Exception:
            continue
    if not rows:
        return {"status": "unavailable", "n": 0, "rows": []}
    hues = Counter()
    for r in rows:
        dom = r.get("dominant")
        if dom:
            hues[(dom["hue_deg"] // 60) % 6] += 1
    return {
        "status": "ok", "n": len(rows), "rows": rows,
        "aggregate": {
            "face_rate": round(sum(1 for r in rows if r["face_present"]) / len(rows), 3),
            "avg_contrast": round(statistics.mean(r["contrast"] for r in rows), 3),
            "avg_brightness": round(statistics.mean(r["brightness"] for r in rows), 3),
            "avg_busy": round(statistics.mean(r["busy"] for r in rows), 2),
            "avg_accent_share": round(statistics.mean(r["accent_share"] for r in rows), 3),
            "avg_lower_text_energy": round(statistics.mean(r["text_edge_energy"]["lower"] for r in rows), 2),
            "hue_families": hues.most_common(),
            "note": "image statistics only; not OCR, not face recognition, not video-frame editing analysis",
        },
    }

def pct(x):
    return f"{x:.1%}" if isinstance(x, (int, float)) else "n/a"

def num(x):
    return f"{x:,}" if isinstance(x, int) else (f"{x:,.1f}" if isinstance(x, float) else "n/a")

def esc(s, n=90):
    s = re.sub(r"\s+", " ", str(s or "")).strip().replace("|", "\\|")
    return s[:n] + ("…" if len(s) > n else "")

def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(str(x) for x in r) + " |")
    return lines

def lane_metrics(rows):
    views = [r["views"] for r in rows if isinstance(r.get("views"), int)]
    if not views:
        return {"n": 0, "total_views": 0, "median_views": 0, "top3_share": 0,
                "winner_ratio": None, "million_count": 0, "ten_million_count": 0,
                "fresh_30d_share": None, "median_duration_s": None, "short_share": None,
                "caption_rate": None, "median_like_rate": None, "median_comment_rate": None,
                "median_views_per_day": None, "top_titles": []}
    total = sum(views)
    med = statistics.median(views)
    top3 = sum(sorted(views, reverse=True)[:3]) / total if total else 0
    ages = [r["age_days"] for r in rows if isinstance(r.get("age_days"), (int, float))]
    durs = [r["duration_seconds"] for r in rows if isinstance(r.get("duration_seconds"), (int, float))]
    likes = [r["like_rate"] for r in rows if isinstance(r.get("like_rate"), (int, float))]
    crs = [r["comment_rate"] for r in rows if isinstance(r.get("comment_rate"), (int, float))]
    vpds = [r["views_per_day"] for r in rows if isinstance(r.get("views_per_day"), (int, float))]
    top = sorted(rows, key=lambda r: -(r.get("views") or 0))[:5]
    return {
        "n": len(rows), "total_views": total, "median_views": int(med),
        "top3_share": round(top3, 3), "winner_ratio": round(max(views) / med, 1) if med else None,
        "million_count": sum(1 for v in views if v >= 1_000_000),
        "ten_million_count": sum(1 for v in views if v >= 10_000_000),
        "fresh_30d_share": round(sum(1 for a in ages if a <= 30) / len(ages), 3) if ages else None,
        "median_duration_s": int(statistics.median(durs)) if durs else None,
        "short_share": round(sum(1 for d in durs if d <= 180) / len(durs), 3) if durs else None,
        "caption_rate": round(sum(1 for r in rows if r.get("caption")) / len(rows), 3),
        "median_like_rate": round(statistics.median(likes), 5) if likes else None,
        "median_comment_rate": round(statistics.median(crs), 5) if crs else None,
        "median_views_per_day": round(statistics.median(vpds), 1) if vpds else None,
        "top_titles": [{"title": r["title"], "views": r["views"], "id": r["id"]} for r in top],
    }

def main():
    log("V17 forensic start; key present =", bool(KEY))
    categories = video_categories()
    save("video_categories_v17.json", {"count": len(categories), "categories": categories})

    # 1) search lanes
    lane_reports, lane_video_ids = [], []
    for lane in LANES:
        res = search_lane(lane)
        rec = {**lane, **{k: res[k] for k in ("status", "params")},
               "ids_count": len(res["ids"]), "page": res.get("page"),
               "detail": res.get("detail"), "ids": res["ids"]}
        lane_reports.append(rec)
        lane_video_ids.extend(res["ids"])
        log(f"lane {lane['slug']}: {rec['status']} {len(res['ids'])} ids")
        time.sleep(0.25)
    save("lanes_v17.json", {"count": len(lane_reports), "lanes": lane_reports})

    # 2) mostPopular
    pop = [most_popular(r) for r in REGIONS]
    save("most_popular_v17.json", {"regions": REGIONS, "snapshots": pop})
    pop_ids = [r["id"] for s in pop for r in s["rows"] if r.get("id")]

    # 3) bulk video details
    all_ids = list(dict.fromkeys(lane_video_ids + pop_ids))
    log("resolving", len(all_ids), "unique videos")
    vrows = video_details(all_ids)
    vby = {r["id"]: r for r in vrows if r.get("id")}
    save("video_details_v17.json", {"count": len(vby), "videos": list(vby.values())})

    # 4) channel details
    cids = [r["channel_id"] for r in vby.values() if r.get("channel_id")]
    chans = channel_details(cids)
    cby = {c["channel_id"]: c for c in chans}
    save("channel_statistics_v17.json", {"count": len(chans), "channels": chans})

    # 5) recent uploads for top 20 channels by cumulative channel views
    uploads, upload_ids = [], []
    for ch in chans[:20]:
        items = recent_uploads(ch)
        uploads.append({"channel_id": ch["channel_id"], "channel": ch["title"],
                        "status": "ok" if items else "empty", "count": len(items), "items": items})
        upload_ids.extend(i["id"] for i in items)
        time.sleep(0.15)
    upl_rows = video_details([i for i in dict.fromkeys(upload_ids) if i not in vby])
    for r in upl_rows:
        vby[r["id"]] = r
    recent_by_channel = defaultdict(list)
    for r in upl_rows:
        recent_by_channel[r["channel_id"]].append(r)
    for c in chans:
        rs = recent_by_channel.get(c["channel_id"], [])
        vv = [r["views"] for r in rs if isinstance(r.get("views"), int)]
        dates = sorted(dt.datetime.fromisoformat(r["published"].replace("Z", "+00:00"))
                       for r in rs if r.get("published"))
        gaps = [(dates[i + 1] - dates[i]).total_seconds() / 86400 for i in range(len(dates) - 1)]
        c["recent_upload_count"] = len(rs)
        c["recent_upload_median_views"] = int(statistics.median(vv)) if vv else None
        c["recent_upload_cadence_days"] = round(statistics.median(gaps), 1) if gaps else None
        c["newer_channel_created_since_2023"] = bool(c["channel_age_days"] and c["channel_age_days"] <= 3 * 365)
    save("recent_uploads_v17.json", {"channels_sampled": len(uploads), "uploads": uploads})
    save("channel_statistics_v17.json", {"count": len(chans), "channels": chans})

    # 6) lane metrics + corpus-wide signals
    lane_metrics_out = []
    for lr in lane_reports:
        rows = [vby[i] for i in lr["ids"] if i in vby]
        lane_metrics_out.append({"slug": lr["slug"], "theme": lr["theme"], "query": lr["q"],
                                 "order": lr["order"], "days": lr["days"],
                                 "status": lr["status"], "ids_count": lr["ids_count"],
                                 "metrics": lane_metrics(rows)})
    save("lane_metrics_v17.json", {"count": len(lane_metrics_out), "lanes": lane_metrics_out})

    all_rows = list(vby.values())
    million = [r for r in all_rows if isinstance(r.get("views"), int) and r["views"] >= 1_000_000]
    ten_million = [r for r in million if r["views"] >= 10_000_000]
    candidates = [r for r in million if not r.get("title_safety_excluded")]
    candidates.sort(key=lambda r: -(r.get("views") or 0))
    recent_candidates = [r for r in candidates if r.get("age_days") is not None and r["age_days"] <= 365]
    recent_candidates.sort(key=lambda r: -(r.get("views_per_day") or 0))
    top_by_views = candidates[:8]
    top_by_velocity = [r for r in recent_candidates if r["id"] not in {x["id"] for x in top_by_views}][:4]
    teardown_ids = list(dict.fromkeys([r["id"] for r in top_by_views + top_by_velocity]))[:12]
    thumb_ids = [r["id"] for r in candidates[:24]]
    save("million_view_videos_v17.json", {"count": len(million), "ten_million_count": len(ten_million),
         "candidate_count": len(candidates), "videos": candidates[:100]})
    save("selected_forensic_ids_v17.json", {"teardown_ids": teardown_ids, "thumbnail_ids": thumb_ids,
         "by_views": [r["id"] for r in top_by_views], "by_velocity": [r["id"] for r in top_by_velocity]})

    # 7) title / tag / description / topic / language signals
    stop = set("the a an and or of to in on for with is are was were be been being this that these those "
               "i you he she it we they my your our their his her its as at by from into about how why what "
               "when who which can will just do does did not no yes vs video videos new 2026 2025".split())
    toks = Counter()
    for r in million:
        for w in re.findall(r"[a-z0-9']+", r["title"].lower()):
            if w not in stop and len(w) > 2:
                toks[w] += 1
    tags = Counter(t.lower() for r in million for t in r.get("tags", []))
    topics = Counter(t.rsplit("/", 1)[-1].replace("_", " ") for r in million for t in r.get("topic_categories", []))
    desc_hits = {k: sum(1 for r in million if re.search(rx, r["description"], re.I)) for k, rx in DESC_PATTERNS.items()}
    signals = {
        "million_view_videos": len(million), "top_title_tokens": toks.most_common(40),
        "top_tags": tags.most_common(40), "top_topic_categories": topics.most_common(25),
        "description_pattern_counts": desc_hits,
        "caption_true_share": round(sum(1 for r in million if r.get("caption")) / len(million), 3) if million else None,
        "short_or_3min_share": round(sum(1 for r in million if r.get("duration_seconds", 0) <= 180) / len(million), 3) if million else None,
        "english_default_language_share": round(sum(1 for r in million if (r.get("default_language") or "").lower().startswith("en")) / len(million), 3) if million else None,
        "median_views": int(statistics.median([r["views"] for r in million])) if million else None,
        "median_duration_s": int(statistics.median([r["duration_seconds"] for r in million if r.get("duration_seconds")])) if million else None,
        "median_like_rate": round(statistics.median([r["like_rate"] for r in million if isinstance(r.get("like_rate"), float)]), 5) if million else None,
        "median_comment_rate": round(statistics.median([r["comment_rate"] for r in million if isinstance(r.get("comment_rate"), float)]), 5) if million else None,
    }
    save("corpus_signals_v17.json", signals)

    # 8) comments + teardowns + thumbnails
    comments_out = []
    for vid in teardown_ids:
        c = comments_for(vid)
        c["mining"] = forensic.comment_mining(c["comments"]) if c["status"] == "ok" else {"status": c["status"]}
        comments_out.append(c)
        time.sleep(0.15)
    save("comments_v17.json", {"count": len(comments_out), "items": comments_out})

    teardowns = [teardown_for(vid) for vid in teardown_ids]
    save("reverse_teardowns_v17.json", {"count": len(teardowns), "items": teardowns})
    transcript_status = Counter()
    for t in teardowns:
        td = t.get("teardown", {}) or {}
        transcript_status[(td.get("transcript_status") or {}).get("status", "missing")] += 1

    thumbs = thumbnail_stats(thumb_ids)
    save("thumbnail_forensics_v17.json", thumbs)

    # 9) run record
    run = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "key_present": True, "secret_value_printed_or_stored": False,
        "lane_reports": len(lane_reports), "lane_rows": len(lane_video_ids),
        "unique_videos": len(vby), "channels_resolved": len(chans),
        "most_popular_regions": sum(1 for s in pop if s["status"] == "ok"),
        "video_categories": len(categories),
        "million_view_videos": len(million), "ten_million_videos": len(ten_million),
        "candidate_videos_after_title_safety": len(candidates),
        "comments_videos": sum(1 for c in comments_out if c["status"] == "ok"),
        "teardowns": len(teardowns), "transcript_status_counts": dict(transcript_status),
        "thumbnail_stats": thumbs.get("n", 0),
        "quota_used_approx": client.BUDGET.state.get("used"),
        "quota_calls": client.BUDGET.state.get("calls"),
        "boundary": ("Public Data API fields + public metadata only. No competitor video/audio "
                     "download, no video-frame inspection, no private retention/CTR/RPM, no "
                     "invented transcripts, no verified growth ranking, no causal virality claim, "
                     "no legal opinion, no upload/publish/monetisation claim, no guaranteed views, "
                     "no human approval, no perfection claim."),
    }
    save("run.json", run)
    log("run record", json.dumps(run, indent=2))

    # 10) Markdown data appendix
    L = []
    A = L.append
    A("# V17 Next-Level Niche Forensic — real-API data appendix")
    A("")
    A(f"Generated UTC: `{run['generated_utc']}`. Key present: `{run['key_present']}`. Secret value never printed or stored.")
    A("")
    A("## Roman Urdu summary")
    A("")
    A("Yeh report **research evidence** hai, final creative approval nahi. Isme 20 search lanes, 4 regions ke most-popular snapshots, channel statistics, recent uploads, public comments, jahan captions mile wahan transcript teardowns, aur thumbnail image statistics hain. Competitor video/audio download nahi kiya, video frames inspect nahi kiye, private retention/CTR/RPM nahi liye. Isliye \"har ek cheez microscopic\" ka claim sirf **public metadata + public text + thumbnail statistics** tak hai; usse aage ka claim honest nahi hoga.")
    A("")
    A("## Honest capability boundary")
    A("")
    A("- Public Data API fields: views, likes, comments, duration, title, tags, description, category, topic, caption flag, channel stats, recent uploads, top comments.")
    A("- Public text: transcript **only where captions are actually available**; otherwise the teardown records `no_captions` / `error`.")
    A("- Public images: thumbnail pixel statistics only. Not OCR, not face recognition, not a video-frame edit analysis.")
    A("- NOT observed: competitor video pixels, cuts per second, music, sound design, retention curve, CTR, RPM, impressions, subscriber growth ranking, legal clearance, human watch-through.")
    A("- No third-party video is used as source footage. No upload, publish, monetisation, legal opinion, human approval, guaranteed views, virality or perfection claim.")
    A("")
    A("## Third-party web signals (not our API data)")
    A("")
    A("- AIR Media-Tech / TubeAI's 144,370-channel study reports Sep 2026 median subscriber growth of 0.97%/month for 10K–100K-subscriber channels; kids 1.59%, ASMR 1.56%, creator economy 1.50%, AI/ML 1.44%, education 1.30%. AIR's 300-channel Studio data puts education/science median RPM at $10.22 vs $2.43 entertainment and $0.33 kids. Six of the ten fastest-growing channels in their Social Blade check grew mainly on Shorts; microdramas passed 6.5B views in H1 2026 with watch time up over 50% YoY. [1](https://air.io/en/audience-growth/whos-growing-fastest-on-youtube-and-which-niches-are-hot-in-2025)")
    A("- vidIQ frames AI tools/workflow tutorials as a fastest-growing cluster and says to show AI as a tool with real screen recordings and original commentary, not as fully generated filler. [2](https://vidiq.com/blog/post/best-youtube-niches/)")
    A("- OpusClip's 13.5M-clip dataset reports captions in 80.2% and caption animation in 78.6% of analysed viral clips; `Expert Explainer` is the top storyline pattern; conversational delivery is 59.4%; authority/credibility hooks averaged 6,706 views in their hook subset. This is a vendor dataset, not official YouTube data. [5](https://www.opus.pro/research/how-to-go-viral-youtube)")
    A("- Revid's 176,367-TikTok study found faceless videos median 113.9K views vs 67.4K for one person on camera, and faceless tutorials 155.6K vs 52.5K on-camera tutorials. This is TikTok data from videos that already did well, so it is correlational, not a YouTube growth guarantee. [8](https://www.revid.ai/blog/best-faceless-youtube-niches)")
    A("- YouTube's 2026 CEO letter says Shorts averages 200 billion daily views and more than 1M channels used its AI creation tools daily in December 2025, while framing AI as a tool for expression, not a replacement. [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/)")
    A("- YouTube's Aug 2026 YPP update says that from Feb 1 2027, Shorts ads/subscription revenue sharing requires 10M qualified Shorts views in 90 days, and new YPP applicants need 8,000 watch hours or 20M qualified Shorts views. Existing YPP channels are not impacted by the entry-threshold change. [2](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/)")
    A("- YouTube's monetisation policy says mass-produced, generic, repetitive or templated content and reused compilations without substantive original commentary/narrative can be ineligible for monetisation. A monetised channel should therefore avoid template compilations and add visible original research, voice and structure. [1](https://support.google.com/youtube/answer/1311392?hl=en)")
    A("")
    A("## API evidence counts")
    A("")
    L.extend(table(["Evidence", "Count"], [
        ["Search lanes", run["lane_reports"]], ["Lane video rows", run["lane_rows"]],
        ["Unique videos resolved", run["unique_videos"]], ["Channels resolved", run["channels_resolved"]],
        ["mostPopular regions", run["most_popular_regions"]], ["Video categories", run["video_categories"]],
        ["Videos >= 1M views", run["million_view_videos"]], ["Videos >= 10M views", run["ten_million_videos"]],
        ["Candidate videos after title safety", run["candidate_videos_after_title_safety"]],
        ["Videos with comments fetched", run["comments_videos"]], ["Teardowns attempted", run["teardowns"]],
        ["Usable transcript statuses", json.dumps(run["transcript_status_counts"])],
        ["Thumbnails analysed", run["thumbnail_stats"]],
        ["Approx. quota units used", run["quota_used_approx"]],
    ]))
    A("")
    A("## Lane demand table (API `search.list` + `videos.list`)")
    A("")
    rows = []
    for lm in lane_metrics_out:
        m = lm["metrics"]
        rows.append([lm["slug"], lm["order"], lm["days"] or "all", m["n"], num(m["total_views"]),
                     num(m["median_views"]), pct(m["top3_share"]),
                     str(m["winner_ratio"]), m["million_count"], m["ten_million_count"],
                     pct(m["fresh_30d_share"]) if m["fresh_30d_share"] is not None else "n/a",
                     str(m["median_duration_s"]), pct(m["short_share"]) if m["short_share"] is not None else "n/a",
                     pct(m["caption_rate"]) if m["caption_rate"] is not None else "n/a"])
    L.extend(table(["Lane", "Order", "Window", "n", "Total views", "Median views", "Top3 share",
                    "Winner/median", ">=1M", ">=10M", "Fresh 30d", "Med dur s", "<=3min", "Captions"], rows))
    A("")
    A("`Top3 share` lower = less winner-takes-all. `Winner/median` lower = easier entry. These are corpus-shape signals, not a growth ranking or a promise.")
    A("")
    A("## Corpus-wide million-view signals")
    A("")
    L.extend(table(["Signal", "Value"], [
        ["Median views", num(signals["median_views"])],
        ["Median duration (s)", str(signals["median_duration_s"])],
        ["<=3 min share", pct(signals["short_or_3min_share"])],
        ["Caption flag true", pct(signals["caption_true_share"])],
        ["English default language", pct(signals["english_default_language_share"])],
        ["Median like rate", str(signals["median_like_rate"])],
        ["Median comment rate", str(signals["median_comment_rate"])],
        ["Top title tokens", ", ".join(f"{w}({n})" for w, n in signals["top_title_tokens"][:20])],
        ["Top tags", ", ".join(f"{w}({n})" for w, n in signals["top_tags"][:20])],
        ["Top topic categories", ", ".join(f"{w}({n})" for w, n in signals["top_topic_categories"][:12])],
        ["Description patterns", ", ".join(f"{k}={v}" for k, v in desc_hits.items())],
    ]))
    A("")
    A("## Top 25 million-view videos in this API snapshot")
    A("")
    rows = []
    for r in candidates[:25]:
        rows.append([esc(r["title"], 72), esc(r["channel"], 28), num(r["views"]), num(r["likes"]),
                     num(r["comments"]), str(r["duration_seconds"]), str(r["age_days"]),
                     num(r["views_per_day"]), "Y" if r["caption"] else "N",
                     str(r["default_language"] or "-"), esc(categories.get(r["category_id"], r["category_id"]), 18)])
    L.extend(table(["Title", "Channel", "Views", "Likes", "Comments", "Dur s", "Age d", "Views/day", "Cap", "Lang", "Category"], rows))
    A("")
    A("`Views/day` is a public velocity proxy from views and publish date only. It is NOT retention, CTR, RPM, or a growth ranking.")
    A("")
    A("## Channel snapshot (top 20 by cumulative channel views)")
    A("")
    rows = []
    for c in chans[:20]:
        rows.append([esc(c["title"], 34), esc(c["handle"] or "-", 18), esc(c["country"] or "-", 8),
                     str(c["published"])[:10], str(c["channel_age_days"]),
                     num(c["subscribers"]), num(c["channel_views"]), num(c["channel_video_count"]),
                     str(c["recent_upload_count"]), num(c["recent_upload_median_views"]),
                     str(c["recent_upload_cadence_days"]), "Y" if c["newer_channel_created_since_2023"] else "N"])
    L.extend(table(["Channel", "Handle", "Country", "Created", "Age d", "Subs", "Channel views", "Videos",
                    "Recent n", "Recent med views", "Cadence d", "Since 2023"], rows))
    A("")
    A("`Since 2023` only means the channel's public creation date is within ~3 years of this run. It is NOT a verified fastest-growing ranking.")
    A("")
    A("## mostPopular snapshots")
    A("")
    rows = []
    for s in pop:
        top = sorted(s["rows"], key=lambda r: -(r.get("views") or 0))[:3]
        rows.append([s["region"], s["status"], len(s["rows"]),
                     " | ".join(f"{esc(r['title'], 42)} ({num(r['views'])})" for r in top) or "-"])
    L.extend(table(["Region", "Status", "n", "Top 3 by views"], rows))
    A("")
    A("## Transcript / script / hook teardowns")
    A("")
    tr_rows = []
    for t in teardowns:
        td = t.get("teardown", {}) or {}
        ts = td.get("transcript_status") or {}
        sc = td.get("script") or {}
        hk = td.get("hook") or {}
        rp = td.get("replication") or {}
        tr_rows.append([t["video_id"], ts.get("status", "missing"), ts.get("kind", "-"),
                        str(sc.get("words", "-")), str(sc.get("wpm", "-")), str(sc.get("reading_grade", "-")),
                        str(sc.get("cta_count", "-")), esc(sc.get("first_30_words", ""), 70),
                        str(hk.get("claim_type", "-")), "Y" if hk.get("opens_with_you") else "N",
                        "Y" if hk.get("opens_with_number") else "N",
                        esc("; ".join(rp.get("keep", [])[:2]), 50)])
    L.extend(table(["Video", "Transcript", "Kind", "Words", "WPM", "Grade", "CTAs", "First 30 words",
                    "Claim type", "You", "Number", "Keep"], tr_rows))
    A("")
    A("Only short excerpts and computed metrics are stored. No full competitor transcript is reproduced. `no_captions` is a real result, not a gap filled with invented text.")
    A("")
    A("## Structure / psychology / replication (where a transcript existed)")
    A("")
    for t in teardowns:
        td = t.get("teardown", {}) or {}
        if (td.get("transcript_status") or {}).get("status") != "ok":
            continue
        A(f"### `{t['video_id']}` — {esc(td.get('receipt', {}).get('title', ''), 90)}")
        A("")
        A(f"- Receipt: {num(td.get('receipt', {}).get('views'))} views, {td.get('duration_seconds')} s, {td.get('receipt', {}).get('vph')} views/hour.")
        A(f"- Hook: `{esc((td.get('hook') or {}).get('first_sentence', ''), 180)}`")
        A(f"- Structure: " + "; ".join(f"{s.get('at')} {s.get('title')}" for s in (td.get("structure") or [])[:8]))
        A("- Psychology: " + "; ".join(d.get("driver", "") for d in (td.get("psychology") or {}).get("drivers", [])))
        A("- Replication keep: " + "; ".join((td.get("replication") or {}).get("keep", [])))
        A("- Replication change: " + "; ".join((td.get("replication") or {}).get("change", [])))
        A("- Replication beat: " + "; ".join((td.get("replication") or {}).get("beat", [])))
        A("")
    A("The teardown maps co-occurrence only. It does NOT claim the video won because of any one feature.")
    A("")
    A("## Top-comment mining")
    A("")
    cm_agg = Counter()
    top_liked = []
    for c in comments_out:
        m = c.get("mining") or {}
        if m.get("status") == "ok":
            for bucket in ("asks", "objections", "wants"):
                for h in m.get(bucket, []):
                    cm_agg[(bucket, h["label"])] += h["n"]
            for x in m.get("top_liked", [])[:2]:
                top_liked.append((x.get("likes") or 0, c["video_id"], x.get("text", "")))
    rows = [[b, lab, n] for (b, lab), n in cm_agg.most_common(20)]
    L.extend(table(["Bucket", "Label", "Hits across sampled comment fields"], rows if rows else [["-", "no pattern cleared the tool's floor", 0]]))
    A("")
    A("Most-liked comment snippets (short excerpts, not full comment threads):")
    A("")
    for likes, vid, txt in sorted(top_liked, reverse=True)[:8]:
        A(f"- `{vid}` · {likes} likes · {esc(txt, 160)}")
    A("")
    A("Caveat: shares are of the comments fetched, not of everyone who watched; a silent majority is invisible here by construction.")
    A("")
    A("## Thumbnail image statistics")
    A("")
    agg = thumbs.get("aggregate") or {}
    L.extend(table(["Metric", "Value"], [
        ["Thumbnails analysed", thumbs.get("n", 0)],
        ["Face-present rate", pct(agg.get("face_rate"))],
        ["Avg contrast", str(agg.get("avg_contrast"))],
        ["Avg brightness", str(agg.get("avg_brightness"))],
        ["Avg busy/edge energy", str(agg.get("avg_busy"))],
        ["Avg accent share", str(agg.get("avg_accent_share"))],
        ["Avg lower text-band energy", str(agg.get("avg_lower_text_energy"))],
        ["Hue families", str(agg.get("hue_families"))],
        ["Note", agg.get("note", "unavailable")],
    ]))
    A("")
    A("Per-thumbnail rows are in `thumbnail_forensics_v17.json`. These are crude image statistics with a stated purpose, not OCR and not a model's opinion.")
    A("")
    A("## Files")
    A("")
    for p in sorted(OUT.glob("*.json")):
        A(f"- `{p.name}`")
    A("")
    A("---")
    A("")
    A("**NOT claimed:** YouTube upload/publish, monetisation, legal clearance, human creative approval, family-safety guarantee, guaranteed views, virality, perfection, private retention/CTR/RPM, invented transcripts, verified growth ranking, social-platform origin, view-count causation, NASA endorsement, official status. Technical/API evidence is not creative approval. A human must still watch candidate videos and review rights before any publication.")
    (BASE / "FORENSIC_REPORT_V17.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    log("DONE", run["unique_videos"], "videos,", run["million_view_videos"], "million-view")

if __name__ == "__main__":
    main()
