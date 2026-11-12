#!/usr/bin/env python3
"""V19 — deep-dive pass: the winners' full upload history, and what actually made them win.

V18.1 measured 24 search lanes. A search lane is a *prompt*, not a channel: it says
"these 50 videos rank for this query". V19 asks a different, harder question:

    For the channels that are actually winning (short AND long), what does their
    OWN catalogue look like — and which of their videos beat their own median?

New in V19 (all real Data API, quota-budgeted):
  1. WINNER CHANNEL DEEP DIVE — for ~30 selected channels (short winners, long winners,
     newer/growing winners), pull up to 100 recent uploads each, then video stats for all of
     them. This gives per-channel distributions, not search-rank mirages.
  2. OUTLIER MINING — for every channel, compute median and flag every video >=3x its own
     channel median. Those are the real "this one popped" events, and their titles/durations
     are compared against the channel's own losers. This is the closest public-API answer to
     "what did they do differently".
  3. FORMAT LADDER — duration x format for every winner: short vs 8-15m vs 20-30m vs 1h+,
     per channel, so "does this channel do both" gets a number instead of a vibe.
  4. FIRST-100-VIDEO CURVE — for newer channels, is the win at video #5 or video #80? Public
     proxy for "how fast did this channel find its format".
  5. TITLE / DESCRIPTION DIFF — outlier vs non-outlier titles within the same channel:
     numbers, questions, length, emoji, hashtags, "world's/strongest/illegal" style claims.
  6. LONG-FORM STRUCTURE PROXY — description chapters + duration + description length for
     every winner's long videos, so we can say what a winning long video *publishes*, and
     what it does not.
  7. COLLAB / SERIES PROXY — repeated title stems per channel (same format re-run), which is
     the public signature of a working series vs one lucky video.

Boundary (same as V18, enforced):
  Public Data API metadata only. No video/audio download, no frame inspection, no private
  retention/CTR/RPM, no invented transcripts, no verified growth ranking, no causal claim,
  no legal/human/upload/monetisation claim.
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
from yt_intel import client, forensic  # noqa: E402

BASE = ROOT / "research" / "deep_forensic_v19"
OUT = BASE / "api_evidence"
OUT.mkdir(parents=True, exist_ok=True)

KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
if not KEY:
    raise SystemExit("YOUTUBE_API_KEY is not set; refusing to call this a real-API run")

V18 = ROOT / "research" / "deep_forensic_v18" / "api_evidence"

# Channels we deep-dive are resolved from the V18 corpus itself (channel ids are real).
# A few names are forced in, because they are the specific winners this study is about.
FOCUS_NAMES = [
    "JayFindsThings", "Science and fun", "KLT", "GeoGlobeTales", "Howtown", "Earthstic",
    "Mark Rober", "Sick Science!", "Alan Becker", "Maupin Farrier Co", "TysyTube Restoration",
    "Hafu Go", "NileRed", "MinuteMinis", "National Geographic", "Story TV", "Cosmetic Plus",
]

SHORT_MAX = 240
MEDIUM_MAX = 1200


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def log(*a):
    print(*a, flush=True)


def iso_since(days):
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_item(it):
    sn = it.get("snippet", {}) or {}
    st = it.get("statistics", {}) or {}
    cd = it.get("contentDetails", {}) or {}
    stt = it.get("status", {}) or {}
    dur = forensic.parse_duration(cd.get("duration", "")) or 0
    age = forensic.parse_age_days(sn.get("publishedAt", ""))
    views = int(st.get("viewCount") or 0)
    likes = int(st.get("likeCount") or 0)
    comments = int(st.get("commentCount") or 0)
    desc = sn.get("description") or ""
    chap = len(re.findall(r"(?m)^\s*(?:\d{1,2}:)?\d{1,2}:\d{2}\s", desc))
    return {
        "id": it.get("id"), "title": sn.get("title", ""), "channel": sn.get("channelTitle", ""),
        "channel_id": sn.get("channelId", ""), "published": sn.get("publishedAt", ""),
        "age_days": round(age, 1) if age else None, "duration": cd.get("duration", ""),
        "duration_seconds": dur, "views": views, "likes": likes, "comments": comments,
        "like_rate": round(likes / views, 5) if views else None,
        "comment_rate": round(comments / views, 5) if views else None,
        "views_per_day": round((views / age) if age else 0, 1),
        "title_len": len(sn.get("title", "") or ""),
        "title_words": len((sn.get("title", "") or "").split()),
        "has_number": bool(re.search(r"\d", sn.get("title", "") or "")),
        "has_question": "?" in (sn.get("title", "") or ""),
        "has_hashtag": "#" in (sn.get("title", "") or ""),
        "tags": (sn.get("tags") or [])[:30], "tag_count": len(sn.get("tags") or []),
        "description": desc[:6000], "description_words": len(desc.split()),
        "chapter_count": chap, "caption": cd.get("caption") == "true",
        "definition": cd.get("definition"),
        "made_for_kids": bool(stt.get("madeForKids") or stt.get("selfDeclaredMadeForKids")),
        "live": sn.get("liveBroadcastContent"),
        "thumbnail": (sn.get("thumbnails", {}).get("maxres") or sn.get("thumbnails", {}).get("high", {})).get("url", ""),
        "category_id": sn.get("categoryId"),
        "default_language": sn.get("defaultLanguage"),
    }


def videos(ids):
    ids = [i for i in dict.fromkeys(ids) if i]
    out = []
    for i in range(0, len(ids), 50):
        try:
            d = client._api("videos", {
                "part": "snippet,statistics,contentDetails,status",
                "id": ",".join(ids[i:i + 50])}, "videos")
        except Exception as e:  # noqa: BLE001
            log("  videos.list failed", type(e).__name__, str(e)[:160])
            continue
        for it in d.get("items", []) or []:
            out.append(parse_item(it))
        time.sleep(0.1)
    return out


def channel_by_id(cid):
    try:
        d = client._api("channels", {"part": "snippet,statistics,contentDetails,brandingSettings",
                                     "id": cid}, "channels")
    except Exception as e:  # noqa: BLE001
        log("  channels.list failed", repr(e)[:140])
        return None, None
    items = d.get("items") or []
    if not items:
        return None, None
    it = items[0]
    sn, st, cd = it.get("snippet", {}) or {}, it.get("statistics", {}) or {}, it.get("contentDetails", {}) or {}
    age = forensic.parse_age_days(sn.get("publishedAt", ""))
    ch = {
        "channel_id": it.get("id"), "title": sn.get("title"), "handle": sn.get("customUrl"),
        "published": sn.get("publishedAt"), "age_days": round(age, 1) if age else None,
        "country": sn.get("country"), "subs": int(st["subscriberCount"]) if st.get("subscriberCount") else None,
        "channel_views": int(st["viewCount"]) if st.get("viewCount") else None,
        "video_count": int(st["videoCount"]) if st.get("videoCount") else None,
        "uploads_playlist": (cd.get("relatedPlaylists") or {}).get("uploads"),
        "newer_since_2023": bool(age and age <= 3 * 365),
    }
    return ch, ch.get("uploads_playlist")


def uploads(pid, pages=3):
    ids = []
    token = None
    for _ in range(pages):
        params = {"part": "snippet,contentDetails", "playlistId": pid, "maxResults": 50}
        if token:
            params["pageToken"] = token
        try:
            d = client._api("playlistItems", params, "playlistItems")
        except Exception as e:  # noqa: BLE001
            log("  playlistItems failed", repr(e)[:140])
            break
        for it in d.get("items", []) or []:
            vid = (it.get("contentDetails") or {}).get("videoId")
            if vid:
                ids.append(vid)
        token = d.get("nextPageToken")
        if not token:
            break
        time.sleep(0.1)
    return ids


def resolve_from_v18():
    """Pick focus channels from the V18 corpus: biggest channel ids by corpus wins."""
    raw = json.loads((V18 / "video_details_v18.json").read_text())["videos"]
    by_ch = defaultdict(lambda: {"n": 0, "views": 0, "name": "", "buckets": Counter()})
    for r in raw:
        cid = r.get("channel_id")
        if not cid:
            continue
        d = by_ch[cid]
        d["n"] += 1
        d["views"] += r.get("views") or 0
        d["name"] = r.get("channel") or d["name"]
        s = r.get("duration_seconds") or 0
        d["buckets"]["short" if s < SHORT_MAX else ("medium" if s <= MEDIUM_MAX else "long")] += 1
    ranked = sorted(by_ch.items(), key=lambda kv: -kv[1]["views"])
    return ranked


def bucket(sec):
    if sec < SHORT_MAX:
        return "short"
    if sec <= MEDIUM_MAX:
        return "medium"
    return "long"


def channel_stats(rows):
    if not rows:
        return {}
    v = sorted(r["views"] for r in rows)
    med = statistics.median(v)
    m = statistics.mean(v)
    return {
        "n": len(rows), "total": sum(v), "median": int(med), "mean": int(m),
        "p25": v[len(v) // 4], "p75": v[(3 * len(v)) // 4], "max": v[-1], "min": v[0],
        "median_duration": statistics.median([r["duration_seconds"] for r in rows]),
        "short_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "short") / len(rows), 3),
        "medium_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "medium") / len(rows), 3),
        "long_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "long") / len(rows), 3),
        "caption_rate": round(sum(1 for r in rows if r["caption"]) / len(rows), 3),
        "median_like_rate": statistics.median([r["like_rate"] for r in rows if r["like_rate"] is not None]) if any(r["like_rate"] for r in rows) else None,
        "median_views_per_day": int(statistics.median([r["views_per_day"] for r in rows])),
    }


def outliers(rows, k=3.0):
    """Videos >= k x the channel's own median. The real 'this one popped' set."""
    if len(rows) < 5:
        return [], (statistics.median([r["views"] for r in rows]) if rows else 0)
    med = statistics.median([r["views"] for r in rows])
    out = [r for r in rows if med and r["views"] >= k * med]
    out.sort(key=lambda r: -r["views"])
    return out, med


def title_diff(outl, rest):
    def stats(rows):
        if not rows:
            return {}
        return {
            "n": len(rows),
            "median_title_len": statistics.median([r["title_len"] for r in rows]),
            "median_title_words": statistics.median([r["title_words"] for r in rows]),
            "number_rate": round(sum(1 for r in rows if r["has_number"]) / len(rows), 3),
            "question_rate": round(sum(1 for r in rows if r["has_question"]) / len(rows), 3),
            "hashtag_rate": round(sum(1 for r in rows if r["has_hashtag"]) / len(rows), 3),
            "median_desc_words": statistics.median([r["description_words"] for r in rows]),
            "chapter_ge3_rate": round(sum(1 for r in rows if r["chapter_count"] >= 3) / len(rows), 3),
            "median_duration": statistics.median([r["duration_seconds"] for r in rows]),
            "caption_rate": round(sum(1 for r in rows if r["caption"]) / len(rows), 3),
            "median_tag_count": statistics.median([r["tag_count"] for r in rows]),
        }
    return {"outliers": stats(outl), "the_rest": stats(rest)}


def series_stems(rows, min_n=3):
    """Repeated title stems = a working series, not a lucky one-off."""
    stop = {"the", "a", "an", "how", "to", "of", "in", "on", "for", "and", "my", "your",
            "this", "that", "with", "why", "what", "best", "new", "vs", "short", "shorts"}
    stems = Counter()
    for r in rows:
        toks = [t for t in re.findall(r"[a-zA-Z]{4,}", (r["title"] or "").lower()) if t not in stop]
        for t in set(toks):
            stems[t] += 1
    return [[s, n] for s, n in stems.most_common(30) if n >= min_n]


def first_hits(rows):
    """Where in the catalogue did the channel's first big video land?"""
    ordered = sorted(rows, key=lambda r: r["published"])
    med = statistics.median([r["views"] for r in ordered]) if ordered else 0
    first_big = next((i for i, r in enumerate(ordered, 1) if med and r["views"] >= 5 * med), None)
    return {"first_5x_hit_position": first_big, "catalogue_size_sampled": len(ordered),
            "if_hit_after_n": first_big}


def main():
    started = time.time()
    log("V19 deep dive — resolving focus channels from V18 corpus")
    ranked = resolve_from_v18()
    log(f"  V18 corpus channels: {len(ranked)}")

    focus = []
    seen = set()
    # 1) top corpus channels by total views (these are the actual winners)
    for cid, d in ranked[:20]:
        if cid not in seen:
            seen.add(cid)
            focus.append({"channel_id": cid, "why": "top_corpus_views", "name": d["name"]})
    # 2) top corpus channels by hit COUNT (repeat winners, not one-hit)
    for cid, d in sorted(ranked, key=lambda kv: -kv[1]["n"])[:10]:
        if cid not in seen:
            seen.add(cid)
            focus.append({"channel_id": cid, "why": "top_corpus_hit_count", "name": d["name"]})
    # 3) named winners (map / animation / long-form / farrier / science)
    name_map = {d["name"]: cid for cid, d in ranked if d.get("name")}
    for nm in FOCUS_NAMES:
        cid = name_map.get(nm)
        if cid and cid not in seen:
            seen.add(cid)
            focus.append({"channel_id": cid, "why": "named_winner", "name": nm})

    log(f"  focus channels: {len(focus)}")

    chans, catalogue, all_rows = [], {}, []
    failures = []
    for i, f in enumerate(focus, 1):
      try:
        ch, pid = channel_by_id(f["channel_id"])
        if not ch:
            log(f"  [{i}/{len(focus)}] {f['channel_id']} unresolved")
            continue
        ids = uploads(pid, pages=2) if pid else []
        rows = videos(ids) if ids else []
        rows = [r for r in rows if r["channel_id"] == ch["channel_id"]]
        stats = channel_stats(rows)
        outl, med = outliers(rows)
        rest = [r for r in rows if r not in outl]
        td = title_diff(outl, rest)
        stems = series_stems(rows)
        fh = first_hits(rows)
        chans.append({**ch, **stats, "why_selected": f["why"], "outlier_median": int(med)})
        catalogue[ch["title"] or ch["channel_id"]] = {
            "channel": ch, "stats": stats, "outliers_ge_3x_channel_median": [
                {k: r[k] for k in ("id", "title", "views", "duration_seconds", "published",
                                   "views_per_day", "like_rate", "comment_rate", "chapter_count",
                                   "description_words", "tag_count", "caption")} for r in outl[:15]],
            "title_diff_outlier_vs_rest": td, "series_stems": stems[:15],
            "first_hit": fh,
            "ladder": {
                b: channel_stats([r for r in rows if bucket(r["duration_seconds"]) == b])
                for b in ("short", "medium", "long")
            },
        }
        all_rows.extend(rows)
        log(f"  [{i}/{len(focus)}] {ch['title'][:28]:28s} uploads={len(rows):3d} med={stats.get('median',0):>11,} "
            f"outliers={len(outl):2d} short/med/long={stats.get('short_share')}/{stats.get('medium_share')}/{stats.get('long_share')}")
      except Exception as e:  # noqa: BLE001
        import traceback
        failures.append({"channel_id": f["channel_id"], "name": f.get("name"), "error": repr(e)[:300]})
        log(f"  [{i}/{len(focus)}] FAILED {f['channel_id']} {type(e).__name__}: {e}")
        traceback.print_exc()

    # ---------- cross-channel aggregates
    outlier_ids = {o["id"] for c in catalogue.values() for o in c["outliers_ge_3x_channel_median"]}
    out_full = [r for r in all_rows if r["id"] in outlier_ids]
    rest_full = [r for r in all_rows if r["id"] not in outlier_ids]

    def agg(rows, name):
        if not rows:
            return {"bucket": name, "n": 0}
        v = sorted(r["views"] for r in rows)
        return {
            "bucket": name, "n": len(rows), "median_views": int(statistics.median(v)),
            "median_duration": int(statistics.median([r["duration_seconds"] for r in rows])),
            "short_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "short") / len(rows), 3),
            "medium_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "medium") / len(rows), 3),
            "long_share": round(sum(1 for r in rows if bucket(r["duration_seconds"]) == "long") / len(rows), 3),
            "number_rate": round(sum(1 for r in rows if r["has_number"]) / len(rows), 3),
            "question_rate": round(sum(1 for r in rows if r["has_question"]) / len(rows), 3),
            "median_title_words": statistics.median([r["title_words"] for r in rows]),
            "median_desc_words": statistics.median([r["description_words"] for r in rows]),
            "chapter_ge3_rate": round(sum(1 for r in rows if r["chapter_count"] >= 3) / len(rows), 3),
            "caption_rate": round(sum(1 for r in rows if r["caption"]) / len(rows), 3),
            "median_tag_count": statistics.median([r["tag_count"] for r in rows]),
            "median_like_rate": statistics.median([r["like_rate"] for r in rows if r["like_rate"] is not None]) if any(r["like_rate"] is not None for r in rows) else None,
        }

    cross = {
        "outliers_ge_3x": agg(out_full, "outlier"),
        "the_rest": agg(rest_full, "rest"),
        "by_duration_bucket_outliers": {b: agg([r for r in out_full if bucket(r["duration_seconds"]) == b], b) for b in ("short", "medium", "long")},
    }

    run = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "key_present": True, "secret_value_printed_or_stored": False,
        "v18_source": str(V18.relative_to(ROOT)),
        "focus_channels_requested": len(focus), "focus_channels_resolved": len(chans),
        "catalogue_videos": len(all_rows), "outlier_videos_ge_3x": len(out_full),
        "channels_with_short_and_long": sum(1 for c in catalogue.values()
                                            if c["stats"].get("short_share", 0) > 0 and c["stats"].get("long_share", 0) > 0),
        "quota_calls": dict(client.BUDGET.state.get("calls", {})),
        "quota_used_approx": client.BUDGET.state.get("used", 0),
        "elapsed_s": round(time.time() - started, 1),
        "channel_failures": failures,
        "boundary": ("Public Data API metadata only. No competitor video/audio download, no frame "
                     "inspection, no private retention/CTR/RPM, no invented transcripts, no verified "
                     "growth ranking, no causal claim, no legal/human/upload/monetisation claim. "
                     "'Outlier' means >=3x that channel's own median views in the sampled catalogue."),
    }
    save("run_v19.json", run)
    save("channel_deep_v19.json", {"channels": chans, "catalogue": catalogue, "cross": cross})
    save("catalogue_videos_v19.json", {"count": len(all_rows), "videos": all_rows})
    log(f"done: {len(all_rows)} catalogue videos, {len(out_full)} outliers, quota≈{run['quota_used_approx']}")
    print(json.dumps(run, indent=1))


if __name__ == "__main__":
    main()
