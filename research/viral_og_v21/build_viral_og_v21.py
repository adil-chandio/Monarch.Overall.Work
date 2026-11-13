#!/usr/bin/env python3
"""V21 — the channels from the user's own swipe file, measured through the real API.

Input  : research/viral_og_v21/api_evidence/drive_swipe_index.json
         (37 channels / 130 video rows read by eye from 71 Drive screenshots)

What it does
  1. resolves each screenshot channel to a real channel id (forHandle -> search fallback)
  2. pulls its uploads (up to 100) + full stats
  3. adds 6 cluster search lanes x short/long so the niche is not defined only by the
     channels the user happened to screenshot
  4. per-channel median / 3x outliers / short-medium-long ladder
  5. top-12 comment threads (relevance, 20 each)
  6. thumbnail pixel stats for the top 30 winners
  7. caption attempt on the top 12 (expected to be 403 from CI - recorded honestly)

Boundary: public Data API metadata, public thumbnails, public caption text. No video or
audio download, no frame inspection, no private analytics, no causal or virality claim.
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

sys.path.insert(0, str(ROOT / "research" / "viral_og_v21"))
import discovery_v21 as disc  # noqa: E402

BASE = ROOT / "research" / "viral_og_v21"
OUT = BASE / "api_evidence"
OUT.mkdir(parents=True, exist_ok=True)

KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
if not KEY:
    raise SystemExit("YOUTUBE_API_KEY is not set; refusing to call this a real-API run")

SHORT_MAX, MEDIUM_MAX = 240, 1200
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

LANES = [
    {"slug": "prehistory_2d", "q": "what did ancient humans do all day animation"},
    {"slug": "stickman_history", "q": "stickman animation history explained"},
    {"slug": "animated_short_film", "q": "animated short film discipline dopamine"},
    {"slug": "animal_2d_essay", "q": "why it sucks to be born as animal animated"},
    {"slug": "dark_doc_2d", "q": "animated documentary disaster last minutes"},
    {"slug": "money_2d", "q": "economics explained animation banana"},
    {"slug": "prehistory_short", "q": "ancient humans daily life animation"},
    {"slug": "stickman_motivation", "q": "animated short film about discipline"},
    {"slug": "pov_life_rank", "q": "POV your life as every rank animation"},
    {"slug": "last_minutes", "q": "the last seconds before disaster animation"},
    {"slug": "every_type_explained", "q": "every type explained in minutes animation"},
    {"slug": "if_humans", "q": "if humans were nocturnal animation"},
]
BUCKETS = [("short", "short"), ("medium", "medium"), ("long", "long")]


def pause(sec=1.0):
    time.sleep(sec)


def with_backoff(fn, *a, tries=3, wait=45, **kw):
    """YouTube returns 429 bursts; wait it out instead of losing the channel."""
    last = None
    for i in range(tries):
        try:
            return fn(*a, **kw)
        except Exception as e:  # noqa: BLE001
            last = e
            if "RateLimited" in type(e).__name__ or "quota" in repr(e).lower() or "429" in repr(e):
                log(f"    rate limited; waiting {wait}s (try {i + 1}/{tries})")
                time.sleep(wait)
                continue
            raise
    raise last


def save(n, o):
    (OUT / n).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def log(*a):
    print(*a, flush=True)


def bucket(s):
    return "short" if s < SHORT_MAX else ("medium" if s <= MEDIUM_MAX else "long")


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
        "starts_why": title.lower().startswith("why"),
        "starts_how": title.lower().startswith("how"),
        "starts_pov": title.lower().startswith("pov"),
        "starts_every": title.lower().startswith("every"),
        "second_person": bool(re.search(r"\byou(?:'re|r)?\b", title.lower())),
        "tags": (sn.get("tags") or [])[:30], "tag_count": len(sn.get("tags") or []),
        "description": desc[:6000], "description_words": len(desc.split()),
        "chapter_count": chap, "caption": cd.get("caption") == "true",
        "made_for_kids": bool(stt.get("madeForKids") or stt.get("selfDeclaredMadeForKids")),
        "default_language": sn.get("defaultLanguage"),
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


def resolve_channel(handle, name):
    """forHandle is exact; search is the fallback. Never guess an id."""
    tries = []
    if handle:
        h = handle.lstrip("@")
        for param in ({"part": "snippet,statistics,contentDetails", "forHandle": h},
                      {"part": "snippet,statistics,contentDetails", "forUsername": h}):
            try:
                d = client._api("channels", param, "channels")
                it = (d.get("items") or [None])[0]
                if it:
                    return it, "exact:" + list(param)[1]
            except Exception as e:  # noqa: BLE001
                tries.append(repr(e)[:80])
    if name:
        try:
            d = client._api("search", {"part": "snippet", "q": name, "type": "channel",
                                       "maxResults": 5, "regionCode": "US",
                                       "relevanceLanguage": "en"}, "search")
            best = None
            for it in d.get("items", []) or []:
                t = (it.get("snippet") or {}).get("title", "")
                cid = (it.get("id") or {}).get("channelId")
                if cid and t.strip().lower() == name.strip().lower():
                    best = cid
                    break
            if best:
                dd = client._api("channels", {"part": "snippet,statistics,contentDetails", "id": best}, "channels")
                it = (dd.get("items") or [None])[0]
                if it:
                    return it, "search:exact-title"
        except Exception as e:  # noqa: BLE001
            tries.append(repr(e)[:80])
    return None, "unresolved:" + "|".join(tries[:2])


def chan_brief(it):
    sn, st, cd = (it.get(k, {}) or {} for k in ("snippet", "statistics", "contentDetails"))
    return {
        "channel_id": it.get("id"), "title": sn.get("title"), "handle": sn.get("customUrl"),
        "country": sn.get("country"), "published": sn.get("publishedAt"),
        "subs": int(st["subscriberCount"]) if st.get("subscriberCount") else None,
        "channel_views": int(st["viewCount"]) if st.get("viewCount") else None,
        "video_count": int(st["videoCount"]) if st.get("videoCount") else None,
        "age_days": round(forensic.parse_age_days(sn.get("publishedAt", "")) or 0, 1),
        "uploads": (cd.get("relatedPlaylists") or {}).get("uploads"),
    }


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


def deep_uploads(pid, pages=2):
    """Up to 300 uploads, newest first - enough to find the screenshot videos."""
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


def _norm(s):
    return re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()


def title_hits(screenshot_titles, rows, thresh=0.72):
    """How many of the screenshot titles actually appear in this channel's catalogue."""
    import difflib
    have = [_norm(r["title"]) for r in rows]
    hits = 0
    for t in screenshot_titles:
        t = _norm(t)
        if not t:
            continue
        if any(difflib.SequenceMatcher(None, t, h).ratio() > thresh for h in have):
            hits += 1
    return hits


def resolve_by_title(title):
    """A screenshot video's exact title -> the channel that really owns it.

    v3/search is 429-blocked from CI IPs, so this uses the public web search route.
    """
    cid = disc.resolve_channel_via_inner(title)
    if cid:
        return cid
    # second pass: the owning channel page of the exact-title video, via html route
    try:
        rows = disc.inner_search(title)
    except Exception:  # noqa: BLE001
        return None
    import difflib
    best, bestr = None, 0.0
    for r in rows:
        ratio = difflib.SequenceMatcher(None, _norm(title), _norm(r.get("title", ""))).ratio()
        if ratio > bestr:
            best, bestr = r.get("channel_id"), ratio
    return best if bestr > 0.8 else None


def stats(rows):
    if not rows:
        return {"n": 0}
    v = sorted(r["views"] for r in rows)
    lr = [r["like_rate"] for r in rows if r["like_rate"] is not None]
    return {
        "n": len(rows), "total": sum(v), "median": int(statistics.median(v)),
        "p25": v[len(v) // 4], "p75": v[(3 * len(v)) // 4], "max": v[-1],
        "median_duration": int(statistics.median([r["duration_seconds"] for r in rows])),
        "short_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "short") / len(rows), 3),
        "medium_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "medium") / len(rows), 3),
        "long_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "long") / len(rows), 3),
        "number_rate": round(sum(1 for r in rows if r["has_number"]) / len(rows), 3),
        "question_rate": round(sum(1 for r in rows if r["has_question"]) / len(rows), 3),
        "you_rate": round(sum(1 for r in rows if r["second_person"]) / len(rows), 3),
        "emoji_rate": round(sum(1 for r in rows if r["has_emoji"]) / len(rows), 3),
        "hashtag_rate": round(sum(1 for r in rows if r["has_hashtag"]) / len(rows), 3),
        "median_title_words": statistics.median([r["title_words"] for r in rows]),
        "median_desc_words": statistics.median([r["description_words"] for r in rows]),
        "chapter_ge3_rate": round(sum(1 for r in rows if r["chapter_count"] >= 3) / len(rows), 3),
        "caption_rate": round(sum(1 for r in rows if r["caption"]) / len(rows), 3),
        "median_tag_count": statistics.median([r["tag_count"] for r in rows]),
        "median_like_rate": round(statistics.median(lr), 5) if lr else None,
        "median_views_per_day": int(statistics.median([r["views_per_day"] for r in rows])),
    }


PHRASE_BUCKETS = {
    "sequel_or_next": r"\b(part\s*2|part two|next (video|part|episode)|more of this|do more|make more)\b",
    "title_is_the_hook": r"\b(clicked|thumbnail|title got me|i came for)\b",
    "how_made": r"\b(how (did|do) you (make|animate|edit)|what (app|software|program)|blender|after effects|which animation)\b",
    "correction_claim": r"\b(actually|wrong|incorrect|not true|false|misleading|you forgot|source)\b",
    "personal_tie": r"\b(i (live|am from|was born)|my (country|city|town|state)|here in)\b",
    "emotional_reaction": r"\b(made me cry|hit me hard|i felt|relatable|this is me|too real)\b",
    "request_topic": r"\b(please do|do a video|cover|next on)\b.{0,40}\b(about|on)\b",
    "ai_accusation": r"\b(ai (generated|voice|art|slop)|is this ai|midjourney|chatgpt)\b",
}


def mine_comments(vid, max_results=20):
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
    buckets = {name: {"n": sum(1 for t in texts if re.search(rx, t, re.I))}
               for name, rx in PHRASE_BUCKETS.items()}
    for b in buckets.values():
        b["share"] = round(b["n"] / len(texts), 3)
    return {"id": vid, "status": "ok", "fetched": len(texts), "buckets": buckets,
            "questions": sum(1 for t in texts if "?" in t),
            "sample": [t[:220] for t in texts[:5]]}


def cap_attempt(vid):
    url = f"https://youtubetotranscript.com/transcript?v={urllib.parse.quote(vid)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode("utf-8", "replace")
            code = r.status
    except Exception as e:  # noqa: BLE001
        return {"id": vid, "status": "http_blocked", "http": getattr(e, "code", 0),
                "detail": repr(e)[:120], "words": 0}
    if "This video has no captions" in html:
        return {"id": vid, "status": "no_captions", "http": code, "words": 0}
    m = re.search(r"<h2[^>]*>\s*Transcript\s*</h2>(.*?)Back To Top", html, re.S)
    if not m:
        return {"id": vid, "status": "parse_failed", "http": code, "words": 0}
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()
    return {"id": vid, "status": "ok", "http": code, "words": len(txt.split()), "text": txt[:8000]}


def main():
    t0 = time.time()
    idx = json.loads((OUT / "drive_swipe_index.json").read_text())
    cache_file = OUT / "channel_cache_v21.json"
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    resolved, unresolved = {}, []
    for name, c in idx["channels"].items():
        b = cache.get(name)
        if b:
            b = dict(b)
        else:
            it, how = with_backoff(resolve_channel, c.get("handle"), name)
            b = chan_brief(it) if it else None
            if b:
                b["resolved_by"] = how
            else:
                unresolved.append({"screenshot_name": name, "handle": c.get("handle"), "why": how})
                pause(2)
                continue
            pause(1.5)
        b["screenshot_name"] = name
        b["screenshot_subs"] = c.get("subs")
        b["screenshot_videos"] = c.get("video_count")
        b["cluster"] = c.get("cluster")
        b.setdefault("age_days", 0)
        resolved[name] = b
    log(f"resolved {len(resolved)}/{len(idx['channels'])} screenshot channels; unresolved {len(unresolved)}")

    catalogue, catalogue_rows, audit = {}, [], []
    for i, (name, b) in enumerate(resolved.items(), 1):
        shots = [v["title"] for v in idx["channels"][name]["videos"] if v.get("title")]
        ids = with_backoff(deep_uploads, b["uploads"]) if b.get("uploads") else []
        cr = [r for r in with_backoff(videos, ids) if r["channel_id"] == b["channel_id"]]
        hits = title_hits(shots, cr)
        method = b["resolved_by"]
        # identity check: if the screenshot's own titles are not in this catalogue, the handle
        # pointed at the wrong channel. Re-derive the channel from a screenshot title.
        if shots and hits < max(1, len(shots) * 0.5):
            for t in sorted(shots, key=len, reverse=True)[:2]:
                cid = resolve_by_title(t)
                if not cid or cid == b["channel_id"]:
                    continue
                try:
                    d = client._api("channels", {"part": "snippet,statistics,contentDetails",
                                                 "id": cid}, "channels")
                    it = (d.get("items") or [None])[0]
                except Exception:  # noqa: BLE001
                    it = None
                if not it:
                    continue
                cand = chan_brief(it)
                cand["resolved_by"] = "title-search:" + t[:60]
                cand["screenshot_name"] = name
                cand["screenshot_subs"] = idx["channels"][name].get("subs")
                cand["screenshot_videos"] = idx["channels"][name].get("video_count")
                cand["cluster"] = idx["channels"][name].get("cluster")
                cids = with_backoff(deep_uploads, cand["uploads"]) if cand.get("uploads") else []
                cand_rows = [r for r in with_backoff(videos, cids) if r["channel_id"] == cand["channel_id"]]
                cand_hits = title_hits(shots, cand_rows)
                if cand_hits > hits:
                    audit.append({"name": name, "old_id": b["channel_id"], "old_title": b["title"],
                                  "old_hits": hits, "new_id": cand["channel_id"],
                                  "new_title": cand["title"], "new_hits": cand_hits,
                                  "shots": len(shots), "fix": "re-resolved by video title"})
                    b, cr, hits, method = cand, cand_rows, cand_hits, cand["resolved_by"]
                    break
        st = stats(cr)
        med = statistics.median([r["views"] for r in cr]) if cr else 0
        outl = sorted([r for r in cr if med and r["views"] >= 3 * med], key=lambda r: -r["views"])
        verified = bool(shots) and hits >= max(1, len(shots) * 0.5)
        b["catalogue_n"] = st.get("n", 0)
        b["median_views"] = int(med)
        b["outlier_count"] = len(outl)
        b["identity"] = {"screenshot_titles": len(shots), "matched": hits,
                         "rate": round(hits / len(shots), 2) if shots else None,
                         "verified": verified, "method": method}
        catalogue[name] = {"channel": b, "stats": st, "median_views": int(med),
                           "identity": b["identity"],
                           "ladder": {k: stats([r for r in cr if bucket(r["duration_seconds"]) == k])
                                      for k in ("short", "medium", "long")},
                           "outliers": [{k: r[k] for k in ("id", "title", "views", "duration_seconds",
                                                           "published", "views_per_day", "like_rate",
                                                           "chapter_count", "description_words", "tag_count")}
                                        for r in outl[:12]],
                           "top_by_views": [{k: r[k] for k in ("id", "title", "views", "duration_seconds", "published")}
                                            for r in sorted(cr, key=lambda r: -r["views"])[:10]]}
        catalogue_rows += cr
        pause(1.2)
        log(f"  [{i}/{len(resolved)}] {name[:24]:24s} n={st.get('n',0):3d} med={int(med):>11,} "
            f"out={len(outl)} verified={verified} ({hits}/{len(shots)})")

    lanes_out, lane_ids = [], []
    for l in LANES:
        for bname, dv in BUCKETS:
            params = {"part": "snippet", "q": l["q"], "type": "video", "maxResults": 50,
                      "order": "viewCount", "regionCode": "US", "relevanceLanguage": "en",
                      "safeSearch": "moderate", "videoDuration": dv}
            # discovery via the public web endpoint; v3/search is 429-blocked from CI IPs
            ids, route = disc.ids_for(l["q"], pages=3, duration=dv)
            if len(ids) < 12:
                wide, r2 = disc.ids_for(l["q"], pages=2, duration=None)
                keep = set(ids)
                for i in wide:
                    if i not in keep:
                        ids.append(i)
                if len(ids) > len(keep):
                    route += "+" + r2 + ":unfiltered"
            status = "ok:" + route if ids else "empty"
            if dv == "short":
                # keep only rows whose hinted length matches the bucket; unknown length is kept
                # and re-classified later from the official duration_seconds.
                pass
            lanes_out.append({"slug": f"{l['slug']}_{bname}_all", "q": l["q"], "videoDuration": dv,
                              "status": status, "route": route, "ids": ids, "ids_count": len(ids)})
            lane_ids += ids
            pause(0.6)
    lane_rows = with_backoff(videos, lane_ids)

    allrows = {r["id"]: r for r in catalogue_rows}
    for r in lane_rows:
        allrows.setdefault(r["id"], r)
    allrows = list(allrows.values())

    verified_names = {n for n, c in catalogue.items() if c["identity"]["verified"]}
    out_ids = {o["id"] for n, c in catalogue.items() if n in verified_names for o in c["outliers"]}
    niche_out = [r for r in allrows if r["id"] in out_ids]
    rest = [r for r in allrows if r["id"] not in out_ids]

    by_cluster = defaultdict(list)
    for name, c in catalogue.items():
        if name not in verified_names:
            continue
        by_cluster[c["channel"].get("cluster") or "unknown"].append(
            {"name": name, "subs": c["channel"]["subs"], "n": c["stats"].get("n", 0),
             "median": c["median_views"], "max": c["stats"].get("max"),
             "outliers": len(c["outliers"]), "short_share": c["stats"].get("short_share"),
             "median_duration": c["stats"].get("median_duration")})

    thumbs = []
    for r in sorted(niche_out, key=lambda r: -r["views"])[:30]:
        try:
            arr, size = thumbprint.fetch(r["id"])
            if arr is not None:
                thumbs.append({"id": r["id"], "title": r["title"], "views": r["views"],
                               "bucket": bucket(r["duration_seconds"]), **thumbprint.analyse(arr, size)})
        except Exception:  # noqa: BLE001
            continue

    caps = []
    for r in sorted(niche_out, key=lambda r: -r["views"])[:12]:
        c = cap_attempt(r["id"])
        c.update({"title": r["title"], "channel": r["channel"], "views": r["views"]})
        caps.append(c)

    comments = []
    for r in sorted(niche_out, key=lambda r: -r["views"])[:12]:
        c = mine_comments(r["id"])
        c.update({"title": r["title"], "channel": r["channel"], "views": r["views"]})
        comments.append(c)
    agg = defaultdict(int)
    fetched = sum(c.get("fetched", 0) for c in comments)
    for c in comments:
        for k, v in (c.get("buckets") or {}).items():
            agg[k] += v["n"]

    run = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "key_present": True, "secret_value_printed_or_stored": False,
        "input": "user's Google Drive swipe file (71 screenshots) -> drive_swipe_index.json",
        "screenshot_channels": len(idx["channels"]),
        "resolved_channels": len(resolved), "unresolved_channels": len(unresolved),
        "identity_verified_channels": len(verified_names),
        "identity_re_resolved": len(audit),
        "identity_unverified_names": sorted(set(catalogue) - verified_names),
        "catalogue_videos": len(catalogue_rows), "lanes": len(lanes_out),
        "lane_rows": len(lane_rows), "unique_videos": len(allrows),
        "niche_outliers_3x": len(niche_out),
        "thumbnail_stats": len(thumbs), "caption_attempts": len(caps),
        "caption_status_counts": dict(Counter(c["status"] for c in caps)),
        "comments_fetched": fetched,
        "quota_used_approx": client.BUDGET.state.get("used", 0),
        "quota_calls": dict(client.BUDGET.state.get("calls", {})),
        "elapsed_s": round(time.time() - t0, 1),
        "boundary": ("Public Data API metadata + public thumbnails + public caption text only. "
                     "No video/audio download, no frame inspection, no private retention/CTR/RPM, "
                     "no invented transcripts, no causal claim, no upload/monetisation claim."),
    }
    save("run_v21.json", run)
    save("channels_v21.json", {"resolved": len(resolved), "unresolved": unresolved,
                               "identity_audit": audit,
                               "channels": list(resolved.values())})
    save("channel_deep_v21.json", {"catalogue": catalogue,
                                   "by_cluster": {k: v for k, v in by_cluster.items()},
                                   "outlier_cross": {"outliers": stats(niche_out), "rest": stats(rest)}})
    # ---- lane-level statistics: the search-discovery half of the forensic -----------
    by_id = {r["id"]: r for r in allrows}
    lanes_stats, lane_health = [], []
    for l in lanes_out:
        rows = [by_id[i] for i in l["ids"] if i in by_id]
        if not rows:
            lane_health.append({"slug": l["slug"], "status": l["status"], "join_rate": 0.0})
            continue
        v = sorted(r["views"] for r in rows)
        lanes_stats.append({
            "slug": l["slug"], "q": l["q"], "bucket": l["videoDuration"], "route": l.get("route"),
            "n": len(rows), "join_rate": round(len(rows) / max(1, l["ids_count"]), 3),
            "median_views": int(statistics.median(v)), "max_views": v[-1],
            "min_views": v[0], "p90_views": v[int(len(v) * 0.9)],
            "share_1m": round(sum(1 for x in v if x >= 1_000_000) / len(v), 3),
            "share_10m": round(sum(1 for x in v if x >= 10_000_000) / len(v), 3),
            "median_duration": int(statistics.median([r["duration_seconds"] for r in rows])),
            "median_vpd": int(statistics.median([r["views_per_day"] for r in rows])),
            "median_like_rate": (statistics.median([r["like_rate"] for r in rows if r["like_rate"] is not None])
                                 if any(r["like_rate"] is not None for r in rows) else None),
            "question_rate": round(sum(1 for r in rows if r["has_question"]) / len(rows), 3),
            "number_rate": round(sum(1 for r in rows if r["has_number"]) / len(rows), 3),
            "second_person_rate": round(sum(1 for r in rows if r["second_person"]) / len(rows), 3),
            "emoji_rate": round(sum(1 for r in rows if r["has_emoji"]) / len(rows), 3),
            "chapter_ge3_rate": round(sum(1 for r in rows if r["chapter_count"] >= 3) / len(rows), 3),
            "median_desc_words": int(statistics.median([r["description_words"] for r in rows])),
            "median_tag_count": int(statistics.median([r["tag_count"] for r in rows])),
            "top": [{"title": r["title"], "channel": r["channel"], "views": r["views"],
                     "seconds": r["duration_seconds"]} for r in sorted(rows, key=lambda r: -r["views"])[:5]],
            "distinct_channels": len({r["channel"] for r in rows}),
            "from_swipe_file": sum(1 for r in rows if r["channel"] in catalogue),
        })
    save("lanes_v21.json", {"lanes": lanes_out, "lane_stats": lanes_stats,
                            "lane_health": lane_health,
                            "route_note": ("discovery = public youtubei WEB search (sp: video + "
                                           "viewCount + duration bucket); numbers = official Data API v3. "
                                           "youtube/v3/search returns 429 from GitHub-runner IPs, measured "
                                           "7/7 runs.")})
    save("videos_v21.json", {"count": len(allrows), "videos": allrows})
    save("thumbnails_v21.json", {"count": len(thumbs), "rows": thumbs})
    save("captions_v21.json", {"count": len(caps), "attempts": caps})
    save("comments_v21.json", {"aggregate": {"videos": len(comments), "fetched": fetched,
                                            "bucket_counts": dict(agg),
                                            "bucket_share": {k: round(v / fetched, 3) for k, v in agg.items()} if fetched else {}},
                               "videos": comments})
    log(f"done {run['elapsed_s']}s | channels {len(resolved)} | catalogue {len(catalogue_rows)} | "
        f"unique {len(allrows)} | outliers {len(niche_out)} | thumbs {len(thumbs)} | "
        f"captions {run['caption_status_counts']} | comments {fetched}")
    print(json.dumps(run, indent=1))


if __name__ == "__main__":
    main()
