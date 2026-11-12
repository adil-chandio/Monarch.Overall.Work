#!/usr/bin/env python3
"""V18 DEEP 10x forensic — real YouTube Data API, Shorts AND long, growing channels.

New in V18 (vs V17):
  * 24 lanes: 6 themes x 3 explicit duration buckets (short <4m / medium 4-20m / long >20m)
    plus 6 fresh "recent" lanes. Shorts aur long dono alag alag measure hote hain.
  * Growing-channel deep dive: 2023+ channels + top cumulative + top corpus-hit channels,
    each with 25 real recent uploads and public velocity proxies. NOT a verified ranking.
  * Description / script forensics on EVERY >=1M-view video (hook type, numbers, emoji,
    hashtags, URLs, chapter markers, CTA patterns, script-like synopsis flag).
  * 40 deep teardowns: receipt + description beats + chapters + comments + thumbnail stats
    + public-caption attempt + explicit "not observed" ledger.
  * Cross-tab aggregates: Shorts vs Medium vs Long on views, likes, comments, captions,
    chapters, hooks, tags, titles.

Boundary (unchanged and enforced):
  Public Data API fields + public metadata only. No competitor video/audio download.
  No video-frame inspection. No private retention/CTR/RPM. No invented transcripts.
  No verified growth ranking. No causal virality claim. No legal opinion.
  No upload/publish/monetisation claim. No guaranteed views. No human approval.
  No perfection claim. Creator-published descriptions are synopses, NOT verbatim VO.
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

BASE = ROOT / "research" / "deep_forensic_v18"
OUT = BASE / "api_evidence"
OUT.mkdir(parents=True, exist_ok=True)

KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
if not KEY:
    raise SystemExit("YOUTUBE_API_KEY is not set; refusing to call this a real-API run")

THEMES = [
    {"slug": "map_geo", "theme": "map / geography explainer", "q": "map animation geography explained"},
    {"slug": "science_explainer", "theme": "science explainer / humor", "q": "science experiment explained funny"},
    {"slug": "satisfying_restoration", "theme": "oddly satisfying / restoration", "q": "oddly satisfying restoration"},
    {"slug": "animal_rescue", "theme": "animal rescue", "q": "animal rescue caught on camera"},
    {"slug": "viral_breakdown", "theme": "viral breakdown / analysis", "q": "viral video breakdown analysis"},
    {"slug": "microdrama", "theme": "microdrama / vertical series", "q": "microdrama short series"},
]
DURATIONS = [("short", "short"), ("medium", "medium"), ("long", "long")]
REGIONS = ["US", "PK", "GB", "IN"]

LANES = []
for t in THEMES:
    for bucket, yt_dur in DURATIONS:
        LANES.append({"slug": f"{t['slug']}_{bucket}_all", "theme": t["theme"],
                      "q": t["q"], "order": "viewCount", "days": 0,
                      "duration_bucket": bucket, "videoDuration": yt_dur})
for t in THEMES:
    LANES.append({"slug": f"{t['slug']}_recent", "theme": t["theme"],
                  "q": t["q"] + " 2026", "order": "date", "days": 365,
                  "duration_bucket": "any", "videoDuration": None})

UNSAFE_TITLE = re.compile(
    r"\b(murder|homicide|suicide|death|dead|kill|killed|shooting|stab|gore|blood|"
    r"autopsy|bomb|blast|explosion|terror|war|missile|crash|rollover|drowning|"
    r"abuse|assault|rape|kidnap|robbery|police chase|beheading|execution)\b", re.I)
CHAP_RE = re.compile(r"(?m)^\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s*([^\n]{0,120})")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF]")
NUM_RE = re.compile(r"\b\d[\d,.]*\b")
URL_RE = re.compile(r"https?://\S+")
HASH_RE = re.compile(r"#\w+")
CTA_PATTERNS = {
    "subscribe": r"\bsubscribe\b", "comment": r"\bcomment(s| below)?\b",
    "follow": r"\bfollow\b", "link": r"https?://|\blink in (bio|description)\b",
    "part2": r"\bpart\s*2\b|\bnext part\b|\bepisode\b|\bseries\b",
    "credits": r"\bcredits?\b|\bsource(s)?\b", "chapters": r"\bchapters?\b|\btimestamps?\b",
    "ai": r"\bAI\b|\bartificial intelligence\b", "disclaimer": r"\bdisclaimer\b|\bnot.*footage\b|\bsimulat",
    "affiliate": r"\baffiliate\b", "newsletter": r"\bnewsletter\b", "donate": r"\bdonate\b|\bdonation\b",
}
STOP = set("the a an and or of to in on for with is are was were be been being this that these those "
           "i you he she it we they my your our their his her its as at by from into about how why what "
           "when who which can will just do does did not no yes vs video videos new 2026 2025 2024 "
           "shorts short yt youtube fyp viral".split())


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
    vpd = forensic.vph(views, age)
    desc = sn.get("description") or ""
    return {
        "id": it.get("id"), "title": sn.get("title", ""),
        "channel": sn.get("channelTitle", ""), "channel_id": sn.get("channelId", ""),
        "published": sn.get("publishedAt", ""), "age_days": round(age, 1) if age else None,
        "duration": cd.get("duration", ""), "duration_seconds": dur,
        "views": views, "likes": likes, "comments": comments,
        "like_rate": round(likes / views, 5) if views else None,
        "comment_rate": round(comments / views, 5) if views else None,
        "views_per_day": round(vpd * 24, 1) if vpd else None,
        "category_id": sn.get("categoryId"), "default_language": sn.get("defaultLanguage"),
        "default_audio_language": sn.get("defaultAudioLanguage"),
        "live_broadcast_content": sn.get("liveBroadcastContent"),
        "tags": (sn.get("tags") or [])[:30], "description": desc[:6000],
        "description_length": len(desc),
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
        "recording_date": rd.get("recordingDate"), "location_description": rd.get("locationDescription"),
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
        time.sleep(0.12)
    return out


def search_lane(lane):
    params = {"part": "snippet", "q": lane["q"], "type": "video", "maxResults": 50,
              "order": lane["order"], "regionCode": "US", "relevanceLanguage": "en",
              "safeSearch": "moderate"}
    if lane.get("videoDuration"):
        params["videoDuration"] = lane["videoDuration"]
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
            sn, st = it.get("snippet", {}) or {}, it.get("statistics", {}) or {}
            cd = it.get("contentDetails", {}) or {}
            bs = (it.get("brandingSettings", {}) or {}).get("channel", {}) or {}
            td, status = it.get("topicDetails", {}) or {}, it.get("status", {}) or {}
            age = forensic.parse_age_days(sn.get("publishedAt", ""))
            out.append({
                "channel_id": it.get("id"), "title": sn.get("title"), "handle": sn.get("customUrl"),
                "published": sn.get("publishedAt"), "channel_age_days": round(age, 1) if age else None,
                "country": sn.get("country"), "description": (sn.get("description") or "")[:1500],
                "subscribers": int(st["subscriberCount"]) if st.get("subscriberCount") else None,
                "channel_views": int(st["viewCount"]) if st.get("viewCount") else None,
                "channel_video_count": int(st["videoCount"]) if st.get("videoCount") else None,
                "hidden_subscribers": bool(st.get("hiddenSubscriberCount")),
                "uploads_playlist": (cd.get("relatedPlaylists") or {}).get("uploads"),
                "keywords": bs.get("keywords", ""), "topic_categories": td.get("topicCategories", [])[:12],
                "made_for_kids": bool(status.get("madeForKids") or status.get("selfDeclaredMadeForKids")),
                "newer_channel_created_since_2023": bool(age and age <= 3 * 365),
            })
        time.sleep(0.12)
    out.sort(key=lambda c: (c["channel_views"] or 0), reverse=True)
    return out


def recent_uploads(ch):
    pid = ch.get("uploads_playlist")
    if not pid:
        return []
    try:
        d = client._api("playlistItems", {"part": "snippet,contentDetails",
                                          "playlistId": pid, "maxResults": 25}, "playlistItems")
    except Exception:
        return []
    out = []
    for it in d.get("items", []) or []:
        cd, sn = it.get("contentDetails", {}) or {}, it.get("snippet", {}) or {}
        vid = cd.get("videoId")
        if vid:
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
        items.append({"text": top.get("textDisplay", ""),
                      "likes": int(top.get("likeCount") or 0),
                      "replies": int(sn.get("totalReplyCount") or 0),
                      "author": top.get("authorDisplayName", ""),
                      "published": top.get("publishedAt", "")})
    return {"video_id": video_id, "status": "ok" if items else "empty", "comments": items}


def teardown_for(video_id):
    try:
        return {"video_id": video_id, "status": "ok",
                "teardown": reverse.teardown(video_id, fetch_transcript=True)}
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
        return {"status": "unavailable", "n": 0, "rows": [], "aggregate": {}}
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
            "avg_busy": round(statistics.mean(r["busy"] for r in rows), 3),
            "avg_accent_share": round(statistics.mean(r["accent_share"] for r in rows), 3),
            "avg_lower_text_energy": round(statistics.mean(r["text_edge_energy"]["lower"] for r in rows), 3),
            "hue_families": hues.most_common(),
            "note": "image statistics only; not OCR, not face recognition, not video-frame edit analysis",
        },
    }


def description_forensics(row):
    """Creator-published description = synopsis / chapter list, NOT a verbatim VO transcript."""
    text = row.get("description") or ""
    title = row.get("title") or ""
    clean = re.sub(r"https?://\S+", " ", text)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean.strip()) if s.strip()]
    first = sentences[0][:240] if sentences else ""
    words = re.findall(r"\b[\w']+\b", clean)
    numbers = NUM_RE.findall(clean)
    emojis = EMOJI_RE.findall(text)
    hashtags = HASH_RE.findall(text)
    urls = URL_RE.findall(text)
    chapters = [{"time": m.group(1), "label": m.group(2).strip()[:100]}
                for m in CHAP_RE.finditer(text)]
    low = first.lower()
    if re.search(r"^(why|how|what|when|who|did you know|have you ever|ever wondered|many people)", low) or "?" in first[:80]:
        hook_type = "question"
    elif re.search(r"\b(difference between|vs\.?|versus)\b", low) or "difference" in low:
        hook_type = "comparison"
    elif re.search(r"\b(all|every|nobody|lying|wrong|don't|many people|you probably)\b", low):
        hook_type = "belief_challenge"
    elif numbers and numbers[0] in first:
        hook_type = "number"
    elif first.count(",") >= 2:
        hook_type = "list"
    else:
        hook_type = "statement"
    cta = {k: bool(re.search(rx, text, re.I)) for k, rx in CTA_PATTERNS.items()}
    word_count = len(words)
    script_like = word_count >= 50 and (
        len(numbers) >= 2 or len(chapters) >= 3 or
        hook_type in ("question", "comparison", "belief_challenge"))
    return {
        "id": row["id"], "title": title, "channel": row.get("channel"),
        "views": row.get("views"), "duration_seconds": row.get("duration_seconds"),
        "duration_bucket": bucket_of(row.get("duration_seconds") or 0),
        "hook_sentence": first, "hook_type": hook_type,
        "sentence_count": len(sentences), "word_count": word_count,
        "number_count": len(numbers), "number_tokens": numbers[:25],
        "emoji_count": len(emojis), "hashtag_count": len(hashtags),
        "url_count": len(urls), "chapter_count": len(chapters), "chapters": chapters[:20],
        "cta": cta, "script_like_synopsis": bool(script_like),
        "description_length": row.get("description_length") or len(text),
        "caption": row.get("caption"), "category_id": row.get("category_id"),
        "classification_note": "creator-published description / chapter metadata; not a verbatim spoken transcript",
    }


def bucket_of(sec):
    if sec < 240:
        return "short"
    if sec <= 1200:
        return "medium"
    return "long"


def lane_metrics(rows):
    views = [r["views"] for r in rows if isinstance(r.get("views"), int)]
    if not views:
        return {"n": 0, "total_views": 0, "median_views": 0, "top3_share": 0,
                "winner_ratio": None, "million_count": 0, "ten_million_count": 0,
                "fresh_30d_share": None, "median_duration_s": None, "short_share": None,
                "caption_rate": None, "median_like_rate": None, "median_comment_rate": None,
                "median_views_per_day": None, "top_titles": [], "top_channels": []}
    total = sum(views)
    med = statistics.median(views)
    ages = [r["age_days"] for r in rows if isinstance(r.get("age_days"), (int, float))]
    durs = [r["duration_seconds"] for r in rows if isinstance(r.get("duration_seconds"), (int, float))]
    likes = [r["like_rate"] for r in rows if isinstance(r.get("like_rate"), (int, float))]
    crs = [r["comment_rate"] for r in rows if isinstance(r.get("comment_rate"), (int, float))]
    vpds = [r["views_per_day"] for r in rows if isinstance(r.get("views_per_day"), (int, float))]
    top = sorted(rows, key=lambda r: -(r.get("views") or 0))[:5]
    ch = Counter(r.get("channel") for r in rows).most_common(5)
    return {
        "n": len(rows), "total_views": total, "median_views": int(med),
        "top3_share": round(sum(sorted(views, reverse=True)[:3]) / total, 3) if total else 0,
        "winner_ratio": round(max(views) / med, 1) if med else None,
        "million_count": sum(1 for v in views if v >= 1_000_000),
        "ten_million_count": sum(1 for v in views if v >= 10_000_000),
        "fresh_30d_share": round(sum(1 for a in ages if a <= 30) / len(ages), 3) if ages else None,
        "median_duration_s": int(statistics.median(durs)) if durs else None,
        "short_share": round(sum(1 for d in durs if d < 240) / len(durs), 3) if durs else None,
        "caption_rate": round(sum(1 for r in rows if r.get("caption")) / len(rows), 3),
        "median_like_rate": round(statistics.median(likes), 5) if likes else None,
        "median_comment_rate": round(statistics.median(crs), 5) if crs else None,
        "median_views_per_day": round(statistics.median(vpds), 1) if vpds else None,
        "top_titles": [{"title": r["title"], "views": r["views"], "id": r["id"]} for r in top],
        "top_channels": [{"channel": c, "n": n} for c, n in ch],
    }


def pct(x):
    return f"{(x or 0) * 100:.1f}%"


def num(x):
    return f"{x:,}" if isinstance(x, int) else str(x)


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(str(x) for x in r) + " |")
    return lines


def main():
    log("V18 DEEP forensic start; key present =", bool(KEY))
    categories = video_categories()
    save("video_categories_v18.json", {"count": len(categories), "categories": categories})

    # 1) 24 lanes: Shorts / Medium / Long + recent
    lane_reports, lane_ids = [], []
    for lane in LANES:
        res = search_lane(lane)
        rec = {**lane, **{k: res[k] for k in ("status", "params")},
               "ids_count": len(res["ids"]), "page": res.get("page"),
               "detail": res.get("detail"), "ids": res["ids"]}
        lane_reports.append(rec)
        lane_ids.extend(res["ids"])
        log(f"lane {lane['slug']}: {rec['status']} {len(res['ids'])} ids")
        time.sleep(0.2)
    save("lanes_v18.json", {"count": len(lane_reports), "lanes": lane_reports})

    # 2) mostPopular 4 regions
    pop = [most_popular(r) for r in REGIONS]
    save("most_popular_v18.json", {"regions": REGIONS, "snapshots": pop})
    pop_ids = [r["id"] for s in pop for r in s["rows"] if r.get("id")]

    # 3) bulk video details
    all_ids = list(dict.fromkeys(lane_ids + pop_ids))
    log("resolving", len(all_ids), "unique videos")
    vrows = video_details(all_ids)
    vby = {r["id"]: r for r in vrows if r.get("id")}
    save("video_details_v18.json", {"count": len(vby), "videos": list(vby.values())})

    # 4) channels
    cids = [r["channel_id"] for r in vby.values() if r.get("channel_id")]
    chans = channel_details(cids)
    cby = {c["channel_id"]: c for c in chans}
    save("channel_statistics_v18.json", {"count": len(chans), "channels": chans})

    # 5) growing-channel recent uploads (2023+ + top cumulative + top corpus-hit)
    corpus_ch_hits = Counter(r["channel_id"] for r in vby.values()
                             if isinstance(r.get("views"), int) and r["views"] >= 1_000_000)
    newer = [c for c in chans if c.get("newer_channel_created_since_2023")]
    top_cum = chans[:25]
    top_hit = [cby[cid] for cid, _ in corpus_ch_hits.most_common(25) if cid in cby]
    selected = list({c["channel_id"]: c for c in newer + top_cum + top_hit}.values())[:45]
    log("growing-channel sample", len(selected))
    uploads, upload_ids = [], []
    for ch in selected:
        items = recent_uploads(ch)
        uploads.append({"channel_id": ch["channel_id"], "channel": ch["title"],
                        "status": "ok" if items else "empty", "count": len(items), "items": items})
        upload_ids.extend(i["id"] for i in items)
        time.sleep(0.12)
    new_upload_ids = [i for i in dict.fromkeys(upload_ids) if i not in vby]
    upl_rows = video_details(new_upload_ids)
    for r in upl_rows:
        vby[r["id"]] = r
    # Re-save the FULL resolved corpus (lanes + mostPopular + recent uploads).
    # V18.1 fix: the first save happened before recent-upload resolution, so it
    # omitted ~1,100 legitimate API rows. Every derived artifact was computed
    # from the full in-memory vby, but the raw dump must match it exactly.
    save("video_details_v18.json", {"count": len(vby), "videos": list(vby.values())})
    recent_by_channel = defaultdict(list)
    for r in upl_rows:
        recent_by_channel[r["channel_id"]].append(r)
    for c in chans:
        rs = recent_by_channel.get(c["channel_id"], [])
        vv = [r["views"] for r in rs if isinstance(r.get("views"), int)]
        dates = sorted(dt.datetime.fromisoformat(r["published"].replace("Z", "+00:00"))
                       for r in rs if r.get("published"))
        gaps = [(dates[i + 1] - dates[i]).total_seconds() / 86400 for i in range(len(dates) - 1)]
        age = c.get("channel_age_days") or 0
        cv = c.get("channel_views") or 0
        nv = c.get("channel_video_count") or 0
        c["recent_upload_count"] = len(rs)
        c["recent_upload_median_views"] = int(statistics.median(vv)) if vv else None
        c["recent_upload_cadence_days"] = round(statistics.median(gaps), 1) if gaps else None
        c["views_per_channel_day"] = round(cv / max(1, age), 2)
        c["views_per_video"] = round(cv / max(1, nv), 2)
        c["million_view_videos_in_corpus"] = corpus_ch_hits.get(c["channel_id"], 0)
    growing = []
    for c in selected:
        growing.append({
            "channel_id": c["channel_id"], "channel": c["title"], "handle": c.get("handle"),
            "created": (c.get("published") or "")[:10], "age_days": c.get("channel_age_days"),
            "country": c.get("country"), "subscribers": c.get("subscribers"),
            "channel_views": c.get("channel_views"), "channel_video_count": c.get("channel_video_count"),
            "views_per_channel_day": c.get("views_per_channel_day"),
            "views_per_video": c.get("views_per_video"),
            "recent_upload_count": c.get("recent_upload_count"),
            "recent_upload_median_views": c.get("recent_upload_median_views"),
            "recent_upload_cadence_days": c.get("recent_upload_cadence_days"),
            "million_view_videos_in_corpus": c.get("million_view_videos_in_corpus"),
            "newer_channel_created_since_2023": c.get("newer_channel_created_since_2023"),
            "note": "public cumulative/age/recent-upload proxy only; NOT a verified subscriber-growth ranking",
        })
    growing.sort(key=lambda x: -(x["views_per_channel_day"] or 0))
    save("growing_channels_v18.json", {"sampled": len(growing), "channels": growing})
    save("recent_uploads_v18.json", {"channels_sampled": len(uploads), "uploads": uploads})
    save("channel_statistics_v18.json", {"count": len(chans), "channels": chans})

    # 6) lane metrics
    lane_metrics_out = []
    for lr in lane_reports:
        rows = [vby[i] for i in lr["ids"] if i in vby]
        lane_metrics_out.append({"slug": lr["slug"], "theme": lr["theme"], "query": lr["q"],
                                 "order": lr["order"], "days": lr["days"],
                                 "duration_bucket": lr["duration_bucket"],
                                 "videoDuration": lr.get("videoDuration"),
                                 "status": lr["status"], "ids_count": lr["ids_count"],
                                 "metrics": lane_metrics(rows)})
    save("lane_metrics_v18.json", {"count": len(lane_metrics_out), "lanes": lane_metrics_out})

    # 7) million-view corpus + description forensics on EVERY one
    all_rows = list(vby.values())
    million = [r for r in all_rows if isinstance(r.get("views"), int) and r["views"] >= 1_000_000]
    ten_million = [r for r in million if r["views"] >= 10_000_000]
    candidates = [r for r in million if not r.get("title_safety_excluded")]
    candidates.sort(key=lambda r: -(r.get("views") or 0))
    save("million_view_videos_v18.json", {
        "count": len(million), "ten_million_count": len(ten_million),
        "candidate_count": len(candidates), "videos": candidates[:200]})
    desc_rows = [description_forensics(r) for r in candidates]
    save("description_forensics_v18.json", {"count": len(desc_rows), "items": desc_rows})

    # 8) pattern aggregates + Shorts vs Medium vs Long cross-tab
    hook_counts = Counter(d["hook_type"] for d in desc_rows)
    cta_counts = {k: sum(1 for d in desc_rows if d["cta"][k]) for k in CTA_PATTERNS}
    buckets = defaultdict(list)
    for r in candidates:
        buckets[bucket_of(r.get("duration_seconds") or 0)].append(r)
    bucket_desc = defaultdict(list)
    for d in desc_rows:
        bucket_desc[d["duration_bucket"]].append(d)
    cross = {}
    for b in ("short", "medium", "long"):
        rs, ds = buckets[b], bucket_desc[b]
        cross[b] = {
            "n": len(rs),
            "median_views": int(statistics.median([r["views"] for r in rs])) if rs else None,
            "total_views": sum(r["views"] for r in rs),
            "million_count": len(rs),
            "ten_million_count": sum(1 for r in rs if r["views"] >= 10_000_000),
            "median_duration_s": int(statistics.median([r["duration_seconds"] for r in rs])) if rs else None,
            "median_like_rate": round(statistics.median([r["like_rate"] for r in rs if isinstance(r.get("like_rate"), float)]), 5) if rs else None,
            "median_comment_rate": round(statistics.median([r["comment_rate"] for r in rs if isinstance(r.get("comment_rate"), float)]), 5) if rs else None,
            "caption_rate": round(sum(1 for r in rs if r.get("caption")) / len(rs), 3) if rs else None,
            "script_like_rate": round(sum(1 for d in ds if d["script_like_synopsis"]) / len(ds), 3) if ds else None,
            "chapter_rate": round(sum(1 for d in ds if d["chapter_count"] >= 3) / len(ds), 3) if ds else None,
            "median_description_words": int(statistics.median([d["word_count"] for d in ds])) if ds else None,
            "median_numbers_in_description": int(statistics.median([d["number_count"] for d in ds])) if ds else None,
            "hook_types": dict(Counter(d["hook_type"] for d in ds)),
            "top_title_tokens": Counter(w for r in rs for w in re.findall(r"[a-z0-9']+", r["title"].lower())
                                        if w not in STOP and len(w) > 2).most_common(12),
            "top_tags": Counter(t.lower() for r in rs for t in r.get("tags", [])).most_common(12),
        }
    aggregates = {
        "million_view_videos": len(candidates),
        "hook_type_distribution": dict(hook_counts),
        "cta_counts": cta_counts,
        "median_description_words": int(statistics.median([d["word_count"] for d in desc_rows])) if desc_rows else None,
        "median_numbers_in_description": int(statistics.median([d["number_count"] for d in desc_rows])) if desc_rows else None,
        "median_hashtags": int(statistics.median([d["hashtag_count"] for d in desc_rows])) if desc_rows else None,
        "median_urls": int(statistics.median([d["url_count"] for d in desc_rows])) if desc_rows else None,
        "script_like_rate": round(sum(1 for d in desc_rows if d["script_like_synopsis"]) / len(desc_rows), 3) if desc_rows else None,
        "chapter_rate": round(sum(1 for d in desc_rows if d["chapter_count"] >= 3) / len(desc_rows), 3) if desc_rows else None,
        "emoji_present_rate": round(sum(1 for d in desc_rows if d["emoji_count"] > 0) / len(desc_rows), 3) if desc_rows else None,
        "cross_bucket": cross,
        "top_title_tokens": Counter(w for r in candidates for w in re.findall(r"[a-z0-9']+", r["title"].lower())
                                    if w not in STOP and len(w) > 2).most_common(40),
        "top_tags": Counter(t.lower() for r in candidates for t in r.get("tags", [])).most_common(40),
        "top_topic_categories": Counter(t.rsplit("/", 1)[-1].replace("_", " ") for r in candidates
                                        for t in r.get("topic_categories", [])).most_common(25),
        "median_views": int(statistics.median([r["views"] for r in candidates])) if candidates else None,
        "median_duration_s": int(statistics.median([r["duration_seconds"] for r in candidates])) if candidates else None,
        "median_like_rate": round(statistics.median([r["like_rate"] for r in candidates if isinstance(r.get("like_rate"), float)]), 5) if candidates else None,
        "median_comment_rate": round(statistics.median([r["comment_rate"] for r in candidates if isinstance(r.get("comment_rate"), float)]), 5) if candidates else None,
    }
    save("pattern_aggregates_v18.json", aggregates)

    # 9) deep teardown selection: views + velocity + newer-channel + each duration bucket
    recent_candidates = [r for r in candidates if r.get("age_days") is not None and r["age_days"] <= 365]
    recent_candidates.sort(key=lambda r: -(r.get("views_per_day") or 0))
    newer_ids = {c["channel_id"] for c in chans if c.get("newer_channel_created_since_2023")}
    by_views = candidates[:12]
    by_velocity = [r for r in recent_candidates if r["id"] not in {x["id"] for x in by_views}][:8]
    by_newer = [r for r in candidates if r.get("channel_id") in newer_ids
                and r["id"] not in {x["id"] for x in by_views + by_velocity}][:8]
    short_hits = [r for r in candidates if (r.get("duration_seconds") or 0) < 240][:6]
    medium_hits = [r for r in candidates if 240 <= (r.get("duration_seconds") or 0) <= 1200][:6]
    long_hits = [r for r in candidates if (r.get("duration_seconds") or 0) > 1200][:6]
    deep_ids = list(dict.fromkeys([r["id"] for r in
                                   by_views + by_velocity + by_newer + short_hits + medium_hits + long_hits]))[:40]
    save("selected_forensic_ids_v18.json", {
        "deep_ids": deep_ids,
        "by_views": [r["id"] for r in by_views], "by_velocity": [r["id"] for r in by_velocity],
        "by_newer_channel": [r["id"] for r in by_newer],
        "short_hits": [r["id"] for r in short_hits], "medium_hits": [r["id"] for r in medium_hits],
        "long_hits": [r["id"] for r in long_hits]})

    # 10) deep teardowns: description beats + chapters + comments + thumbnail + transcript
    desc_by = {d["id"]: d for d in desc_rows}
    comments_out, teardowns, deep_rows = [], [], []
    for idx, vid in enumerate(deep_ids):
        row = vby.get(vid, {})
        c = comments_for(vid) if idx < 24 else {"video_id": vid, "status": "not_requested", "comments": []}
        if c["status"] == "ok":
            c["mining"] = forensic.comment_mining(c["comments"])
        comments_out.append(c)
        td = teardown_for(vid) if idx < 12 else None
        if td:
            teardowns.append(td)
        deep_rows.append({
            "video_id": vid,
            "receipt": {k: row.get(k) for k in (
                "id", "title", "channel", "channel_id", "published", "age_days", "duration",
                "duration_seconds", "views", "likes", "comments", "like_rate", "comment_rate",
                "views_per_day", "category_id", "default_language", "caption", "definition",
                "topic_categories", "tags", "thumbnail", "made_for_kids", "licensed_content")},
            "duration_bucket": bucket_of(row.get("duration_seconds") or 0),
            "description_forensics": desc_by.get(vid),
            "creator_published_script_beats": (desc_by.get(vid) or {}).get("chapters", []),
            "comment_mining": (c.get("mining") or {"status": c["status"]}),
            "transcript_attempt": (td or {}).get("teardown", {}).get("transcript_status") if td else "not_requested",
            "editing_observation": {
                "status": "not_observed",
                "detail": ("competitor video frames, cuts/sec, transitions, music, sound design, "
                           "caption animation, colour grade and retention curve were not inspected; "
                           "no video/audio download was performed"),
            },
            "boundary": "third-party copyrighted work, research only, not source footage",
        })
        time.sleep(0.1)
    save("comments_v18.json", {"count": len(comments_out), "items": comments_out})
    save("reverse_teardowns_v18.json", {"count": len(teardowns), "items": teardowns})
    save("deep_teardowns_v18.json", {"count": len(deep_rows), "items": deep_rows})
    thumbs = thumbnail_stats(deep_ids)
    save("thumbnail_forensics_v18.json", thumbs)
    transcript_status = Counter()
    for t in teardowns:
        transcript_status[(t.get("teardown", {}).get("transcript_status") or {}).get("status", "missing")] += 1

    # 11) run record
    run = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "key_present": True, "secret_value_printed_or_stored": False,
        "lanes": len(lane_reports),
        "short_bucket_lanes": sum(1 for l in lane_reports if l["duration_bucket"] == "short"),
        "medium_bucket_lanes": sum(1 for l in lane_reports if l["duration_bucket"] == "medium"),
        "long_bucket_lanes": sum(1 for l in lane_reports if l["duration_bucket"] == "long"),
        "recent_lanes": sum(1 for l in lane_reports if l["duration_bucket"] == "any"),
        "lane_rows": len(lane_ids), "unique_videos": len(vby),
        "channels_resolved": len(chans), "growing_channels_sampled": len(growing),
        "recent_upload_channels": len(uploads),
        "most_popular_regions": sum(1 for s in pop if s["status"] == "ok"),
        "video_categories": len(categories),
        "million_view_videos": len(million), "ten_million_videos": len(ten_million),
        "candidate_videos_after_title_safety": len(candidates),
        "description_forensics": len(desc_rows), "deep_teardowns": len(deep_rows),
        "comments_videos": sum(1 for c in comments_out if c["status"] == "ok"),
        "transcript_attempts": len(teardowns), "transcript_status_counts": dict(transcript_status),
        "thumbnail_stats": thumbs.get("n", 0),
        "quota_used_approx": client.BUDGET.state.get("used"),
        "quota_calls": client.BUDGET.state.get("calls"),
        "boundary": ("Public Data API fields + public metadata only. No competitor video/audio "
                     "download, no video-frame inspection, no private retention/CTR/RPM, no "
                     "invented transcripts, no verified growth ranking, no causal virality claim, "
                     "no legal opinion, no upload/publish/monetisation claim, no guaranteed views, "
                     "no human approval, no perfection claim. Creator-published descriptions are "
                     "synopses / chapter metadata, NOT verbatim spoken transcripts."),
    }
    save("run_v18.json", run)
    save("analysis_manifest_v18.json", {
        "note": "every derived artifact below was computed from the full in-memory video map; the raw video_details dump is re-saved after recent-upload resolution",
        "unique_videos_in_memory_and_raw_dump": len(vby),
        "lane_reports": len(lane_reports), "lane_rows": len(lane_ids),
        "most_popular_regions": len(pop), "channels_resolved": len(chans),
        "growing_channels_sampled": len(growing), "recent_upload_channels": len(uploads),
        "million_view_videos": len(million), "candidate_videos": len(candidates),
        "description_forensics": len(desc_rows), "deep_teardowns": len(deep_rows),
        "comments_videos": sum(1 for c in comments_out if c["status"] == "ok"),
        "transcript_attempts": len(teardowns), "thumbnail_stats": thumbs.get("n", 0),
        "duration_bucket_lanes": {"short": 6, "medium": 6, "long": 6, "recent_any": 6},
    })
    log("run record", json.dumps(run, indent=2))

    # 12) data appendix
    L = []
    A = L.append
    A("# V18 DEEP 10x Forensic — real-API data appendix (Shorts + Medium + Long)")
    A("")
    A(f"Generated UTC: `{run['generated_utc']}`. Key present: `{run['key_present']}`. Secret value never printed or stored.")
    A("")
    A("## Honest capability boundary")
    A("")
    A("- Public Data API: views, likes, comments, duration, title, tags, description, category, topic, caption flag, channel stats, recent uploads, top comments.")
    A("- Public text: creator-published `snippet.description` (synopsis / chapters / sources) on every >=1M-view video. This is NOT a verbatim VO transcript.")
    A("- Public captions: attempted on 12 teardowns; failures are recorded, never filled with invented words.")
    A("- Public images: thumbnail pixel statistics only. Not OCR, not face recognition, not video-frame edit analysis.")
    A("- NOT observed: competitor video pixels, cuts/sec, transitions, music, sound design, retention curve, CTR, RPM, impressions, subscriber-growth ranking, legal clearance, human watch-through.")
    A("- No third-party video/audio is used as source footage. No upload/publish/monetisation/legal/human/guaranteed-views/virality/perfection claim.")
    A("")
    A("## API evidence counts")
    A("")
    L.extend(table(["Evidence", "Count"], [[k, v] for k, v in run.items()
                                           if isinstance(v, (int, float, str)) and k not in ("boundary", "generated_utc", "key_present")]))
    A("")
    A("## 24 lanes — Shorts / Medium / Long / Recent")
    A("")
    rows = []
    for lm in lane_metrics_out:
        m = lm["metrics"]
        rows.append([lm["slug"], lm["duration_bucket"], lm["order"], lm["days"] or "all",
                     m["n"], num(m["total_views"]), num(m["median_views"]), pct(m["top3_share"]),
                     str(m["winner_ratio"]), m["million_count"], m["ten_million_count"],
                     pct(m["fresh_30d_share"]) if m["fresh_30d_share"] is not None else "n/a",
                     str(m["median_duration_s"]), pct(m["short_share"]) if m["short_share"] is not None else "n/a",
                     pct(m["caption_rate"]) if m["caption_rate"] is not None else "n/a"])
    L.extend(table(["Lane", "Bucket", "Order", "Window", "n", "Total", "Median", "Top3", "Win/med",
                    ">=1M", ">=10M", "Fresh30", "Med dur s", "Short share", "Caption"], rows))
    A("")
    A("`short` = <4 min, `medium` = 4–20 min, `long` = >20 min (YouTube `videoDuration`). Corpus-shape signals, not growth ranking or promise.")
    A("")
    A("## Shorts vs Medium vs Long — million-view cross-tab")
    A("")
    cross_rows = []
    for b in ("short", "medium", "long"):
        c = cross[b]
        cross_rows.append([b, c["n"], num(c["total_views"]), num(c["median_views"]),
                           c["ten_million_count"], c["median_duration_s"],
                           c["median_like_rate"], c["median_comment_rate"],
                           pct(c["caption_rate"]), pct(c["script_like_rate"]),
                           pct(c["chapter_rate"]), c["median_description_words"],
                           c["median_numbers_in_description"]])
    L.extend(table(["Bucket", "n(>=1M)", "Total views", "Median views", ">=10M", "Med dur s",
                    "Med like rate", "Med comment rate", "Caption", "Script-like synopsis",
                    "Chapters>=3", "Med desc words", "Med numbers"], cross_rows))
    A("")
    A("## Description / script forensics on every >=1M-view video")
    A("")
    L.extend(table(["Signal", "Value"], [
        ["Videos analysed", len(desc_rows)],
        ["Hook types", json.dumps(dict(hook_counts))],
        ["Median description words", aggregates["median_description_words"]],
        ["Median numbers in description", aggregates["median_numbers_in_description"]],
        ["Median hashtags", aggregates["median_hashtags"]],
        ["Median URLs", aggregates["median_urls"]],
        ["Script-like synopsis rate", pct(aggregates["script_like_rate"])],
        ["Chapter rate (>=3 markers)", pct(aggregates["chapter_rate"])],
        ["Emoji present rate", pct(aggregates["emoji_present_rate"])],
        ["CTA counts", json.dumps(cta_counts)],
        ["Top title tokens", json.dumps(aggregates["top_title_tokens"][:20])],
        ["Top tags", json.dumps(aggregates["top_tags"][:20])],
    ]))
    A("")
    A("`script_like_synopsis` means the creator's own description is >=50 words and carries >=2 numbers, >=3 chapters, or a question/comparison/belief-challenge hook. It is a public synopsis, not a spoken transcript.")
    A("")
    A("## Growing-channel public proxies (NOT a verified growth ranking)")
    A("")
    grow_rows = [[g["channel"], g["created"], g["age_days"], num(g["subscribers"] or 0),
                  num(g["channel_views"] or 0), g["channel_video_count"],
                  num(int(g["views_per_channel_day"] or 0)), num(int(g["views_per_video"] or 0)),
                  g["million_view_videos_in_corpus"], g["recent_upload_median_views"],
                  str(g["newer_channel_created_since_2023"])] for g in growing[:25]]
    L.extend(table(["Channel", "Created", "Age d", "Subs", "Channel views", "Videos",
                    "Views/day", "Views/video", ">=1M in corpus", "Recent med views", "Since 2023"], grow_rows))
    A("")
    A("## Top 25 million-view videos (deep-forensic pool)")
    A("")
    top_rows = [[r["title"][:80], r["channel"][:24], num(r["views"]), r["duration_seconds"],
                 bucket_of(r["duration_seconds"]), r["published"][:10],
                 pct(r["like_rate"]), pct(r["comment_rate"]), r["id"]] for r in candidates[:25]]
    L.extend(table(["Title", "Channel", "Views", "Dur s", "Bucket", "Published", "Like", "Comment", "ID"], top_rows))
    A("")
    A("## Deep teardown ledger (what was and was not observed)")
    A("")
    A("Every one of the 40 deep teardowns stores: full public receipt, description-forensics record, creator-published chapter beats, comment mining (first 24), public-caption attempt (first 12), thumbnail statistics, and an explicit `editing_observation.status = not_observed` for frames/cuts/music/retention. See `api_evidence/deep_teardowns_v18.json`.")
    A("")
    A("## Thumbnail aggregate (image statistics only)")
    A("")
    L.extend(table(["Signal", "Value"], [[k, str(v)] for k, v in thumbs.get("aggregate", {}).items()]))
    A("")
    A("## Files")
    A("")
    for f in ["run_v18.json", "lanes_v18.json", "lane_metrics_v18.json", "video_details_v18.json",
              "channel_statistics_v18.json", "growing_channels_v18.json", "recent_uploads_v18.json",
              "million_view_videos_v18.json", "description_forensics_v18.json",
              "pattern_aggregates_v18.json", "selected_forensic_ids_v18.json",
              "deep_teardowns_v18.json", "comments_v18.json", "reverse_teardowns_v18.json",
              "thumbnail_forensics_v18.json", "most_popular_v18.json", "video_categories_v18.json"]:
        A(f"- `{f}`")
    A("")
    A("---")
    A("")
    A("**NOT claimed:** upload/publish, monetisation, legal clearance, human creative approval, guaranteed views, virality, perfection, private retention/CTR/RPM, invented transcripts, verified growth ranking, causal claim, video-frame editing analysis. Technical/API evidence is not creative approval.")
    (BASE / "DEEP_FORENSIC_V18.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    log("V18 DONE")


if __name__ == "__main__":
    main()
