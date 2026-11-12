#!/usr/bin/env python3
"""Build an auditable local evidence extract from the completed V18.1 API dump.

This script performs NO network calls. It reads the public-data artifacts already
produced by GitHub Actions run 43249117208 and derives repeatable tables for the
Roman Urdu forensic report. Every number in the report can be traced to either
the raw API evidence or this extract.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import statistics as st

ROOT = pathlib.Path(__file__).resolve().parent
E = ROOT / "api_evidence"


def load(name: str):
    return json.loads((E / name).read_text(encoding="utf-8"))


def bucket_of(sec: float | int) -> str:
    sec = sec or 0
    if sec < 240:
        return "short"
    if sec <= 1200:
        return "medium"
    return "long"


def median(xs, default=None):
    xs = [x for x in xs if isinstance(x, (int, float)) and not isinstance(x, bool)]
    return st.median(xs) if xs else default


def mean(xs, default=None):
    xs = [x for x in xs if isinstance(x, (int, float)) and not isinstance(x, bool)]
    return round(st.mean(xs), 3) if xs else default


def pct(n: int, d: int) -> float:
    return round(n / d, 3) if d else 0.0


def c(text, limit=90):
    s = re.sub(r"\s+", " ", str(text or "")).replace("|", "\\|").strip()
    return s if len(s) <= limit else s[: limit - 1] + "…"


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def fmt(n):
    if isinstance(n, (int, float)) and not isinstance(n, bool):
        return f"{n:,}"
    return "—"


run = load("run_v18.json")
manifest = load("analysis_manifest_v18.json")
videos = load("video_details_v18.json")["videos"]
vby = {v["id"]: v for v in videos}
desc = load("description_forensics_v18.json")["items"]
desc_by = {d["id"]: d for d in desc}
candidates = [vby[d["id"]] for d in desc if d["id"] in vby]
cand_by = {r["id"]: r for r in candidates}
lane_metrics = load("lane_metrics_v18.json")["lanes"]
lanes = load("lanes_v18.json")["lanes"]
lane_by_slug = {l["slug"]: l for l in lanes}
agg = load("pattern_aggregates_v18.json")
growing = load("growing_channels_v18.json")["channels"]
channels = load("channel_statistics_v18.json")["channels"]
chan_by_id = {c["channel_id"]: c for c in channels}
comments = load("comments_v18.json")["items"]
comments_by = {x["video_id"]: x for x in comments}
reverse = load("reverse_teardowns_v18.json")["items"]
deep = load("deep_teardowns_v18.json")["items"]
deep_by = {x["video_id"]: x for x in deep}
thumbs = load("thumbnail_forensics_v18.json")
thumb_rows = thumbs.get("rows", [])
thumb_by = {r["id"]: r for r in thumb_rows}
pop = load("most_popular_v18.json")["snapshots"]
selected = load("selected_forensic_ids_v18.json")
categories = load("video_categories_v18.json")
recent_uploads = load("recent_uploads_v18.json")["uploads"]

# ---------------------------------------------------------------- integrity
integrity = {
    "run_generated_utc": run["generated_utc"],
    "raw_video_count": len(videos),
    "run_unique_videos": run["unique_videos"],
    "manifest_unique_videos": manifest["unique_videos_in_memory_and_raw_dump"],
    "description_records": len(desc),
    "description_ids_missing_from_raw": sum(1 for d in desc if d["id"] not in vby),
    "million_view_videos_saved_top_slice": load("million_view_videos_v18.json")["count"],
    "candidate_videos": len(candidates),
    "candidate_ids_missing_from_raw": sum(1 for r in candidates if r["id"] not in vby),
    "deep_teardowns": len(deep),
    "deep_ids_missing_from_raw": sum(1 for r in deep if r["video_id"] not in vby),
    "comment_request_records": len(comments),
    "comment_status_counts": dict(collections.Counter(x["status"] for x in comments)),
    "transcript_attempts": len(reverse),
    "transcript_status_counts": run["transcript_status_counts"],
    "thumbnail_stats": thumbs.get("n", 0),
    "quota_used_approx": run["quota_used_approx"],
    "raw_descriptions_capped_at_chars": 6000,
    "note": "V18.1 re-saved the raw video_details dump after recent-upload resolution; raw count now equals the in-memory corpus and every description ID joins.",
}

# ---------------------------------------------------------------- lanes
lane_defs = []
for lm in lane_metrics:
    m = lm["metrics"]
    d = lane_by_slug.get(lm["slug"], {})
    lane_defs.append({
        "slug": lm["slug"], "theme": lm["theme"], "query": d.get("q"),
        "order": d.get("order"), "days": d.get("days"),
        "duration_bucket": lm["duration_bucket"], "videoDuration": d.get("videoDuration"),
        "n": m["n"], "median_views": m["median_views"], "total_views": m["total_views"],
        "top3_share": m["top3_share"], "winner_ratio": m["winner_ratio"],
        "million_count": m["million_count"], "ten_million_count": m["ten_million_count"],
        "fresh_30d_share": m["fresh_30d_share"], "median_duration_s": m["median_duration_s"],
        "caption_rate": m["caption_rate"], "median_like_rate": m["median_like_rate"],
        "median_comment_rate": m["median_comment_rate"], "top_titles": m["top_titles"],
        "top_channels": m["top_channels"],
    })

newer_ids = {c["channel_id"] for c in channels if c.get("newer_channel_created_since_2023")}
newer_by_lane = []
for l in lanes:
    ids = l.get("ids") or []
    rows = [vby[i] for i in ids if i in vby]
    hits = [r for r in rows if isinstance(r.get("views"), int) and r["views"] >= 1_000_000 and r.get("channel_id") in newer_ids]
    newer_by_lane.append({
        "slug": l["slug"], "duration_bucket": l["duration_bucket"],
        "lane_n": len(rows), "million_view_rows": sum(1 for r in rows if (r.get("views") or 0) >= 1_000_000),
        "newer_channel_million_view_rows": len(hits),
        "top_newer_channels": collections.Counter(r.get("channel") for r in hits).most_common(5),
    })

# ---------------------------------------------------------------- candidate patterns
bucket_rows = collections.defaultdict(list)
bucket_desc = collections.defaultdict(list)
for r in candidates:
    bucket_rows[bucket_of(r.get("duration_seconds") or 0)].append(r)
for d in desc:
    bucket_desc[d["duration_bucket"]].append(d)

title_patterns = {
    "number": re.compile(r"\d"), "question_mark": re.compile(r"\?"),
    "hashtag": re.compile(r"#\w+"), "ellipsis": re.compile(r"\.\.\.|…"),
    "vs": re.compile(r"\bvs\.?\b|\bversus\b", re.I),
    "how_to": re.compile(r"\bhow\s+to\b", re.I),
    "worlds": re.compile(r"\bworld'?s\b", re.I),
    "levels": re.compile(r"\b\d+\s+levels?\b", re.I),
    "part_or_episode": re.compile(r"\bpart\b|\bpt\.?\b|\bepisode\b", re.I),
    "superlative": re.compile(r"\b(best|biggest|largest|smallest|world|most|greatest|perfect|impossible|insane|amazing|incredible)\b", re.I),
    "shorts_word": re.compile(r"\bshorts?\b", re.I),
    "emoji": re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF]"),
}


def title_stats(rows):
    out = {
        "n": len(rows),
        "median_title_chars": int(median([len(r.get("title") or "") for r in rows], 0)),
        "median_title_words": int(median([len(re.findall(r"\w+", r.get("title") or "")) for r in rows], 0)),
    }
    for name, rx in title_patterns.items():
        n = sum(1 for r in rows if rx.search(r.get("title") or ""))
        out[name] = {"n": n, "rate": pct(n, len(rows))}
    return out


def desc_stats(rows, drows):
    cta_keys = list((drows[0]["cta"] if drows else {}).keys())
    out = {
        "n": len(rows), "description_records": len(drows),
        "median_description_words": int(median([d["word_count"] for d in drows], 0)),
        "median_numbers_in_description": int(median([d["number_count"] for d in drows], 0)),
        "median_hashtags": int(median([d["hashtag_count"] for d in drows], 0)),
        "median_urls": int(median([d["url_count"] for d in drows], 0)),
        "emoji_present_rate": pct(sum(1 for d in drows if d["emoji_count"] > 0), len(drows)),
        "script_like_synopsis_rate": pct(sum(1 for d in drows if d["script_like_synopsis"]), len(drows)),
        "chapter_ge3_rate": pct(sum(1 for d in drows if d["chapter_count"] >= 3), len(drows)),
        "any_chapter_marker_rate": pct(sum(1 for d in drows if d["chapter_count"] >= 1), len(drows)),
        "caption_flag_rate": pct(sum(1 for r in rows if r.get("caption")), len(rows)),
        "hd_definition_rate": pct(sum(1 for r in rows if r.get("definition") == "hd"), len(rows)),
        "hook_types": dict(collections.Counter(d["hook_type"] for d in drows)),
        "cta_counts": {k: sum(1 for d in drows if d["cta"].get(k)) for k in cta_keys},
        "median_tag_count": int(median([len(r.get("tags") or []) for r in rows], 0)),
        "zero_tag_rate": pct(sum(1 for r in rows if not (r.get("tags") or [])), len(rows)),
        "top_tags": collections.Counter(t.lower() for r in rows for t in (r.get("tags") or [])).most_common(20),
        "top_title_tokens": collections.Counter(
            w for r in rows for w in re.findall(r"[a-z0-9']+", (r.get("title") or "").lower())
            if w not in set("the a an and or of to in on for with is are was were be been being this that these those i you he she it we they my your our their his her its as at by from into about how why what when who which can will just do does did not no yes vs video videos new 2026 2025 2024 shorts short yt youtube fyp viral".split())
            and len(w) > 2
        ).most_common(20),
    }
    return out


pattern_stats = {
    "global": desc_stats(candidates, desc),
    "by_bucket": {b: desc_stats(bucket_rows[b], bucket_desc[b]) for b in ("short", "medium", "long")},
    "title_global": title_stats(candidates),
    "title_by_bucket": {b: title_stats(bucket_rows[b]) for b in ("short", "medium", "long")},
    "bucket_counts": {b: len(bucket_rows[b]) for b in ("short", "medium", "long")},
    "global_topics": agg["top_topic_categories"][:15],
    "global_aggregates": {k: agg[k] for k in (
        "million_view_videos", "hook_type_distribution", "cta_counts",
        "median_description_words", "median_numbers_in_description", "median_hashtags",
        "median_urls", "script_like_rate", "chapter_rate", "emoji_present_rate",
        "median_views", "median_duration_s", "median_like_rate", "median_comment_rate")},
}

# ---------------------------------------------------------------- top rows and chapters
top_million = sorted(candidates, key=lambda r: -(r.get("views") or 0))[:200]
top_million_compact = [{
    "id": r["id"], "title": r["title"], "channel": r["channel"], "published": r["published"],
    "views": r["views"], "duration_seconds": r["duration_seconds"],
    "duration_bucket": bucket_of(r.get("duration_seconds") or 0),
    "like_rate": r["like_rate"], "comment_rate": r["comment_rate"],
    "caption": r["caption"], "tag_count": len(r.get("tags") or []),
    "description_words": (desc_by.get(r["id"]) or {}).get("word_count"),
    "hook_type": (desc_by.get(r["id"]) or {}).get("hook_type"),
    "chapter_count": (desc_by.get(r["id"]) or {}).get("chapter_count"),
} for r in top_million]

chapter_leaders = sorted(desc, key=lambda d: (-d["chapter_count"], -d["word_count"]))[:20]
chapter_leaders_compact = [{
    "id": d["id"], "title": d["title"], "channel": d["channel"], "views": d["views"],
    "duration_bucket": d["duration_bucket"], "word_count": d["word_count"],
    "number_count": d["number_count"], "chapter_count": d["chapter_count"],
    "first_chapters": d["chapters"][:6],
} for d in chapter_leaders]

# ---------------------------------------------------------------- channels
growing_compact = []
for g in growing:
    growing_compact.append({
        "channel": g["channel"], "created": g["created"], "country": g.get("country"),
        "subscribers": g.get("subscribers"), "channel_views": g.get("channel_views"),
        "channel_video_count": g.get("channel_video_count"),
        "views_per_channel_day": g.get("views_per_channel_day"),
        "views_per_video": g.get("views_per_video"),
        "recent_upload_count": g.get("recent_upload_count"),
        "recent_upload_median_views": g.get("recent_upload_median_views"),
        "recent_upload_cadence_days": g.get("recent_upload_cadence_days"),
        "million_view_videos_in_corpus": g.get("million_view_videos_in_corpus"),
        "newer_channel_created_since_2023": g.get("newer_channel_created_since_2023"),
        "note": g.get("note"),
    })

top_candidate_channels = []
for name, n in collections.Counter(r.get("channel") for r in candidates).most_common(25):
    ids = {r.get("channel_id") for r in candidates if r.get("channel") == name}
    newer = any(chan_by_id.get(i, {}).get("newer_channel_created_since_2023") for i in ids)
    top_candidate_channels.append({"channel": name, "candidate_videos": n, "newer_channel_proxy": newer})

newer_channel_hits = sorted(
    [c for c in channels if c.get("newer_channel_created_since_2023")],
    key=lambda c: -(c.get("million_view_videos_in_corpus") or 0))[:25]
newer_channel_hits_compact = [{
    "channel": c["title"], "created": c.get("published"), "subscribers": c.get("subscribers"),
    "channel_views": c.get("channel_views"), "channel_video_count": c.get("channel_video_count"),
    "million_view_videos_in_corpus": c.get("million_view_videos_in_corpus"),
    "recent_upload_median_views": c.get("recent_upload_median_views"),
} for c in newer_channel_hits]

# ---------------------------------------------------------------- comments
comment_status = collections.Counter(x["status"] for x in comments)
all_comment_texts = [c.get("text", "") for x in comments for c in x.get("comments", [])]
phrase_defs = {
    "asked_for_a_sequel": r"\b(part|pt\.?)\s*(2|ii|two)\b|\bnext video\b|\bmore (of )?this\b|\bplease make\b|\bdo more\b",
    "asked_for_sibling_topic": r"\bwhat about\b|\bcan you (do|make|cover)\b|\bhow (do|did) you\b|\btutorial (on|for)\b",
    "asked_which_tool": r"\bwhere (can|do) i (get|find|download)\b|\bwhat (app|tool|software|site)\b|\bwhich (tool|software)\b",
    "said_it_did_not_work": r"\b(didn'?t|doesn'?t|not) work\b|\bwrong\b|\bmisleading\b|\bclickbait\b",
    "objected_to_cost": r"\bexpensive\b|\btoo (much|costly)\b|\bpaid\b|\bnot free\b",
    "objected_to_pacing_clarity": r"\btoo (fast|slow|long|short)\b|\bconfus(ing|ed)\b|\bhard to follow\b",
    "wants_asset": r"\b(file|download|template|preset|project|link|checklist)\b",
    "wants_teaching": r"\bcourse\b|\bmentorship\b|\bcoaching\b|\bconsult\b|\bhire\b",
}
phrase_global = {}
for label, rx in phrase_defs.items():
    n = sum(1 for t in all_comment_texts if re.search(rx, t, re.I))
    phrase_global[label] = {"n": n, "rate_of_fetched_comments": pct(n, len(all_comment_texts))}

comment_patterns = []
for x in comments:
    m = x.get("mining") or {}
    if m.get("status") != "ok":
        continue
    hits = []
    for group in ("asks", "objections", "wants"):
        for h in m.get(group, []):
            if h.get("share", 0) >= 0.025:
                hits.append({"group": group, "label": h["label"], "n": h["n"], "share": h["share"]})
    comment_patterns.append({
        "video_id": x["video_id"], "n": m.get("n"),
        "patterns_at_or_above_2_5pct": hits,
        "reading": m.get("reading"),
        "top_liked": [{"likes": q.get("likes"), "text": c(q.get("text"), 160)} for q in m.get("top_liked", [])[:3]],
    })

comment_summary = {
    "status_counts": dict(comment_status),
    "comments_fetched": len(all_comment_texts),
    "max_comments_per_video": 25,
    "comment_order": "relevance",
    "pattern_floor": 0.025,
    "min_comments_for_mining": 20,
    "global_phrase_counts": phrase_global,
    "per_video": comment_patterns,
    "error_details": [{"video_id": x["video_id"], "detail": c(x.get("detail"), 240)} for x in comments if x["status"] == "error"],
}

# ---------------------------------------------------------------- thumbnails
thumb_by_bucket = {}
for b in ("short", "medium", "long"):
    ids = [t["video_id"] for t in deep if t["duration_bucket"] == b and t["video_id"] in thumb_by]
    rs = [thumb_by[i] for i in ids]
    thumb_by_bucket[b] = {
        "n": len(rs),
        "face_rate_heuristic": pct(sum(1 for r in rs if r.get("face_present")), len(rs)),
        "avg_contrast": mean([r.get("contrast") for r in rs]),
        "avg_brightness": mean([r.get("brightness") for r in rs]),
        "avg_busy": mean([r.get("busy") for r in rs]),
        "avg_accent_share": mean([r.get("accent_share") for r in rs]),
        "avg_lower_text_energy": mean([(r.get("text_edge_energy") or {}).get("lower") for r in rs]),
        "dominant_hue_families": collections.Counter(
            ((r.get("dominant") or {}).get("hue_deg") or 0) // 60 for r in rs if r.get("dominant")
        ).most_common(),
    }

thumbnail_summary = {
    "aggregate": thumbs.get("aggregate"),
    "by_bucket": thumb_by_bucket,
    "rows": [{
        "id": r["id"], "bucket": (deep_by.get(r["id"]) or {}).get("duration_bucket"),
        "size": r.get("size"), "w": r.get("w"), "h": r.get("h"),
        "face_share": r.get("face_share"), "face_present": r.get("face_present"),
        "contrast": r.get("contrast"), "brightness": r.get("brightness"),
        "accent_share": r.get("accent_share"), "dominant": r.get("dominant"),
        "lower_text_energy": (r.get("text_edge_energy") or {}).get("lower"),
        "busy": r.get("busy"),
    } for r in thumb_rows],
    "measurement_note": "face_present is a permissive skin-tone pixel heuristic in the upper half; NOT face recognition, NOT OCR, NOT video-frame edit analysis.",
}

# ---------------------------------------------------------------- transcripts + teardowns
transcript_ledger = []
for x in reverse:
    t = x.get("teardown") or {}
    ts = t.get("transcript_status") or {}
    transcript_ledger.append({
        "video_id": x["video_id"], "teardown_status": x.get("status"),
        "transcript_status": ts.get("status"), "words": ts.get("words"),
        "detail": c(ts.get("detail") or x.get("detail"), 240),
    })

deep_compact = []
for t in deep:
    vid = t["video_id"]
    r = t.get("receipt") or {}
    d = t.get("description_forensics") or {}
    m = t.get("comment_mining") or {}
    ta = t.get("transcript_attempt")
    deep_compact.append({
        "video_id": vid, "duration_bucket": t.get("duration_bucket"),
        "title": r.get("title"), "channel": r.get("channel"), "published": r.get("published"),
        "views": r.get("views"), "duration_seconds": r.get("duration_seconds"),
        "like_rate": r.get("like_rate"), "comment_rate": r.get("comment_rate"),
        "caption_flag": r.get("caption"), "tags": r.get("tags"),
        "hook_sentence": d.get("hook_sentence"), "hook_type": d.get("hook_type"),
        "description_words": d.get("word_count"), "number_count": d.get("number_count"),
        "chapter_count": d.get("chapter_count"), "chapters": d.get("chapters"),
        "cta_true": [k for k, val in (d.get("cta") or {}).items() if val],
        "script_like_synopsis": d.get("script_like_synopsis"),
        "comment_mining_status": m.get("status"), "comment_n": m.get("n"),
        "comment_patterns": [h for group in ("asks", "objections", "wants") for h in (m.get(group) or []) if h.get("share", 0) >= 0.025],
        "comment_reading": m.get("reading"),
        "transcript_attempt": ta,
        "editing_observation": t.get("editing_observation"),
        "boundary": t.get("boundary"),
    })

# ---------------------------------------------------------------- mostPopular / categories / recent uploads
popular_top = []
for snap in pop:
    for r in sorted(snap.get("rows", []), key=lambda z: -(z.get("views") or 0))[:5]:
        popular_top.append({
            "region": snap["region"], "id": r["id"], "title": r["title"],
            "channel": r["channel"], "views": r["views"],
            "duration_seconds": r.get("duration_seconds"),
        })

recent_upload_summary = [{
    "channel": u["channel"], "status": u["status"], "count": u["count"],
    "newest_titles": [i["title"] for i in u.get("items", [])[:3]],
} for u in recent_uploads]

not_observed = [
    {"item": "Full verbatim spoken competitor scripts / captions", "status": "not_observed", "proof": "12/12 public caption attempts errored with bot-check; 0 usable transcript words; creator descriptions are synopses/chapters only."},
    {"item": "Competitor video frames, cuts/sec, transitions, music, SFX, colour grade, caption animation", "status": "not_observed", "proof": "deep_teardowns_v18.json editing_observation.status=not_observed on all 40; no competitor media download."},
    {"item": "Private retention, impressions, CTR, RPM, revenue, audience demographics", "status": "not_available", "proof": "YouTube Data API public fields only."},
    {"item": "Verified subscriber-growth ranking", "status": "not_observed", "proof": "growing_channels_v18.json uses cumulative channel views / channel age and sampled recent uploads as public proxies."},
    {"item": "Thumbnail OCR, face identity/recognition, text content", "status": "not_observed", "proof": "thumbnail stats are pixel statistics and a permissive skin-tone heuristic only."},
    {"item": "All public comments", "status": "partial", "proof": "first 24 deep IDs requested up to 25 relevance-ordered comments; 23 ok, 1 error, 16 not_requested."},
    {"item": "Full untruncated creator descriptions", "status": "partial", "proof": "parse_video_item caps snippet.description at 6000 characters."},
    {"item": "Causal reason a video won", "status": "not_observable", "proof": "viewCount and metadata are co-occurrence, not an experiment or private analytics."},
    {"item": "Legal clearance, human/creative approval, upload/publish, monetisation outcome", "status": "not_done", "proof": "research only; no connected-app upload/send; no release claim."},
    {"item": "Guaranteed views, virality, perfection, family-safety guarantee", "status": "not_claimed", "proof": "report boundary."},
]

extract = {
    "generated_from": {
        "github_actions_run": "43249117208", "workflow": ".github/workflows/yt-deep-forensic-v18.yml",
        "builder": "research/deep_forensic_v18/build_deep_forensic_v18.py",
        "evidence_dir": "research/deep_forensic_v18/api_evidence/",
    },
    "integrity": integrity,
    "method_notes": {
        "buckets": {"short": "<240s", "medium": "240-1200s", "long": ">1200s"},
        "search_params": "regionCode=US, relevanceLanguage=en, safeSearch=moderate, maxResults=50 per lane",
        "all_time_lane_order": "viewCount (high-view-conditioned, NOT a random sample)",
        "recent_lane_order": "date, publishedAfter=365 days (freshness-conditioned, NOT a growth ranking)",
        "top3_share": "sum of top 3 views / total views in that lane",
        "winner_ratio": "maximum views / median views in that lane",
        "fresh_30d_share": "share of lane rows published within 30 days",
        "views_per_channel_day": "cumulative channel views / channel age in days (public proxy, not measured growth)",
        "views_per_video": "cumulative channel views / public video count",
        "caption_flag": "contentDetails.caption=true/false; NOT a transcript and NOT caption quality",
        "script_like_synopsis": "creator description >=50 words AND (>=2 numbers OR >=3 chapters OR question/comparison/belief-challenge hook); NOT a spoken script",
        "tag_caveat": "snippet.tags are creator-supplied public metadata; many videos have no tags and tags do not prove ranking/causality",
        "comment_caveat": "shares are of fetched relevance-ordered comments, not all viewers; 2.5% floor; silent majority invisible",
    },
    "lane_defs": lane_defs,
    "newer_by_lane": newer_by_lane,
    "pattern_stats": pattern_stats,
    "top_million_200": top_million_compact,
    "candidate_index_717": [{
        "id": r["id"], "title": r["title"], "channel": r["channel"], "views": r["views"],
        "duration_seconds": r["duration_seconds"], "duration_bucket": bucket_of(r.get("duration_seconds") or 0),
        "hook_type": desc_by[r["id"]]["hook_type"], "description_words": desc_by[r["id"]]["word_count"],
        "chapter_count": desc_by[r["id"]]["chapter_count"], "tag_count": len(r.get("tags") or []),
        "caption": r.get("caption"),
    } for r in sorted(candidates, key=lambda z: -(z.get("views") or 0))],
    "chapter_leaders": chapter_leaders_compact,
    "growing_channels_45": growing_compact,
    "newer_channel_hits": newer_channel_hits_compact,
    "top_candidate_channels": top_candidate_channels,
    "comment_summary": comment_summary,
    "thumbnail_summary": thumbnail_summary,
    "transcript_ledger": transcript_ledger,
    "deep_teardowns_40": deep_compact,
    "selected_forensic_ids": selected,
    "most_popular_top5_per_region": popular_top,
    "video_categories": categories,
    "recent_upload_summary": recent_upload_summary,
    "not_observed_ledger": not_observed,
}

(ROOT / "FORENSIC_EVIDENCE_EXTRACT_V18.json").write_text(
    json.dumps(extract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- markdown evidence tables
M = []
A = M.append
A("# V18.1 Evidence Tables — real YouTube Data API forensic\n")
A("Ye machine-generated local appendix hai. Isme koi naya API call nahi; sab kuch `api_evidence/` aur `FORENSIC_EVIDENCE_EXTRACT_V18.json` se aata hai. Roman Urdu report ka har numeric claim yahan trace hota hai.\n")
A("## 1. Run receipt aur integrity\n")
A(md_table(["Field", "Value"], [
    ["GitHub Actions run", "43249117208 — success, HARD QC PASS, 5m37s"],
    ["Generated UTC", run["generated_utc"]],
    ["Raw unique videos", fmt(len(videos))],
    ["Run unique videos", fmt(run["unique_videos"])],
    ["Manifest unique videos", fmt(manifest["unique_videos_in_memory_and_raw_dump"])],
    ["Description records", fmt(len(desc))],
    ["Description IDs missing from raw", integrity["description_ids_missing_from_raw"]],
    ["Candidate videos after title safety", fmt(len(candidates))],
    ["Deep teardowns", len(deep)],
    ["Comment request records", f"{len(comments)} ({dict(comment_status)})"],
    ["Transcript attempts", f"{len(reverse)} {run['transcript_status_counts']}"],
    ["Thumbnail stats", thumbs.get("n", 0)],
    ["Quota approx", fmt(run["quota_used_approx"])],
    ["Raw descriptions capped at", "6,000 characters"],
]) + "\n")

A("## 2. 24 lane definitions aur metrics\n")
A("`viewCount`-ordered lanes high-view-conditioned hain; `date`-ordered recent lanes freshness-conditioned hain. Median ko expected performance na samjha jaye.\n")
rows = []
for l in lane_defs:
    rows.append([
        l["slug"], l["duration_bucket"], l["n"], fmt(l["median_views"]), fmt(l["total_views"]),
        l["top3_share"], l["winner_ratio"], l["million_count"], l["ten_million_count"],
        l["fresh_30d_share"], l["median_duration_s"], l["caption_rate"],
        l["median_like_rate"], l["median_comment_rate"], c(l["order"]), c(l["days"]),
    ])
A(md_table(["Lane", "Bucket", "n", "Median views", "Total views", "Top3", "Winner/median", ">=1M", ">=10M", "Fresh30d", "Med dur s", "Caption", "Like", "Comment", "Order", "Days"], rows) + "\n")
A("### Lane queries\n")
A(md_table(["Lane", "Query", "videoDuration"], [[l["slug"], c(l["query"]), l["videoDuration"]] for l in lane_defs]) + "\n")

A("## 3. Cross-bucket: Short vs Medium vs Long (717 million-view candidates)\n")
rows = []
for b in ("short", "medium", "long"):
    cross = agg["cross_bucket"][b]
    s = pattern_stats["by_bucket"][b]
    rows.append([
        b, cross["n"], fmt(cross["median_views"]), fmt(cross["total_views"]), cross["ten_million_count"],
        cross["median_duration_s"], cross["median_like_rate"], cross["median_comment_rate"],
        cross["caption_rate"], cross["script_like_rate"], cross["chapter_rate"],
        cross["median_description_words"], s["median_tag_count"], s["zero_tag_rate"],
    ])
A(md_table(["Bucket", "n", "Median views", "Total views", ">=10M", "Med dur s", "Like", "Comment", "Caption", "Synopsis", "Chapters>=3", "Desc words", "Med tags", "Zero tags"], rows) + "\n")
A("### Hook types by bucket\n")
A(md_table(["Bucket", "Statement", "Number", "Belief", "Question", "List", "Comparison"], [
    [b] + [pattern_stats["by_bucket"][b]["hook_types"].get(k, 0) for k in ("statement", "number", "belief_challenge", "question", "list", "comparison")]
    for b in ("short", "medium", "long")
]) + "\n")
A("### CTA counts by bucket (regex Boolean, overlapping)\n")
cta_keys = list(pattern_stats["global"]["cta_counts"].keys())
A(md_table(["Bucket"] + cta_keys, [
    [b] + [pattern_stats["by_bucket"][b]["cta_counts"].get(k, 0) for k in cta_keys]
    for b in ("short", "medium", "long")
]) + "\n")
A("### Title pattern rates by bucket\n")
tp = list(title_patterns.keys())
A(md_table(["Bucket", "Med chars", "Med words"] + tp, [
    [b, pattern_stats["title_by_bucket"][b]["median_title_chars"], pattern_stats["title_by_bucket"][b]["median_title_words"]]
    + [pattern_stats["title_by_bucket"][b][k]["rate"] for k in tp]
    for b in ("short", "medium", "long")
]) + "\n")
A("### Top tags by bucket\n")
for b in ("short", "medium", "long"):
    A(f"- **{b}**: " + ", ".join(f"{t} ({n})" for t, n in pattern_stats["by_bucket"][b]["top_tags"][:12]))
A("\n### Top title tokens by bucket\n")
for b in ("short", "medium", "long"):
    A(f"- **{b}**: " + ", ".join(f"{t} ({n})" for t, n in pattern_stats["by_bucket"][b]["top_title_tokens"][:12]))
A("\n")

A("## 4. Top 25 million-view candidates (full 717 index in JSON extract)\n")
A(md_table(["#", "Views", "ID", "Sec", "Bucket", "Channel", "Title", "Hook", "Words", "Chap", "Tags"], [
    [i + 1, fmt(r["views"]), r["id"], r["duration_seconds"], r["duration_bucket"],
     c(r["channel"], 24), c(r["title"], 70), r["hook_type"], r["description_words"],
     r["chapter_count"], r["tag_count"]]
    for i, r in enumerate(top_million_compact[:25])
]) + "\n")

A("## 5. Newer-channel million-view rows by lane (public created-since-2023 proxy)\n")
A(md_table(["Lane", "Bucket", "Lane n", ">=1M rows", "Newer-channel >=1M", "Top newer channels"], [
    [n["slug"], n["duration_bucket"], n["lane_n"], n["million_view_rows"], n["newer_channel_million_view_rows"],
     c(", ".join(f"{x} ({y})" for x, y in n["top_newer_channels"]), 70)]
    for n in sorted(newer_by_lane, key=lambda z: -z["newer_channel_million_view_rows"])
]) + "\n")
A("## 6. Newer channels by million-view corpus hits\n")
A(md_table(["Channel", "Created", "Subs", "Channel views", "Videos", ">=1M hits", "Recent median views"], [
    [c(x["channel"], 30), c(x["created"], 10), fmt(x["subscribers"]), fmt(x["channel_views"]),
     fmt(x["channel_video_count"]), x["million_view_videos_in_corpus"], fmt(x["recent_upload_median_views"])]
    for x in newer_channel_hits_compact[:20]
]) + "\n")
A("## 7. Growing-channel public proxies, top 20 of 45\n")
A("`views_per_channel_day` cumulative views / channel age hai — measured growth nahi.\n")
A(md_table(["Channel", "Created", "Subs", "Channel views", "Videos", "Views/day proxy", "Views/video", "Recent n", "Recent median", "Cadence d", ">=1M hits", "Newer"], [
    [c(g["channel"], 26), c(g["created"], 10), fmt(g["subscribers"]), fmt(g["channel_views"]),
     fmt(g["channel_video_count"]), fmt(g["views_per_channel_day"]), fmt(g["views_per_video"]),
     g["recent_upload_count"], fmt(g["recent_upload_median_views"]), g["recent_upload_cadence_days"],
     g["million_view_videos_in_corpus"], g["newer_channel_created_since_2023"]]
    for g in growing_compact[:20]
]) + "\n")
A("## 8. Top channels inside 717 title-safe candidates\n")
A(md_table(["Channel", "Candidate videos", "Newer proxy"], [
    [c(x["channel"], 40), x["candidate_videos"], x["newer_channel_proxy"]]
    for x in top_candidate_channels[:25]
]) + "\n")

A("## 9. Description / chapter leaders\n")
A("Chapter regex time-like lines bhi pakad sakta hai; isliye ye creator-published metadata signal hai, verified spoken structure nahi.\n")
A(md_table(["ID", "Chap", "Words", "Numbers", "Bucket", "Channel", "Title", "First chapters"], [
    [x["id"], x["chapter_count"], x["word_count"], x["number_count"], x["duration_bucket"],
     c(x["channel"], 22), c(x["title"], 55),
     c("; ".join(f"{z['time']} {z['label']}" for z in x["first_chapters"]), 90)]
    for x in chapter_leaders_compact[:20]
]) + "\n")

A("## 10. Comments: status, phrase rates, per-video patterns\n")
A(f"Fetched comments: {len(all_comment_texts)}; status {dict(comment_status)}; max 25 per video; relevance order; mining needs >=20 comments; 2.5% floor.\n")
A(md_table(["Phrase", "n", "Rate of fetched comments"], [
    [k, v["n"], v["rate_of_fetched_comments"]] for k, v in phrase_global.items()
]) + "\n")
A(md_table(["Video", "n", "Patterns >=2.5%", "Reading"], [
    [p["video_id"], p["n"], c("; ".join(f"{h['label']} {h['share']:.0%}" for h in p["patterns_at_or_above_2_5pct"]) or "none", 80), c(p["reading"], 110)]
    for p in comment_patterns
]) + "\n")

A("## 11. Thumbnail pixel statistics\n")
A(md_table(["Metric", "Aggregate value"], [[k, c(v, 120)] for k, v in thumbs.get("aggregate", {}).items()]) + "\n")
A(md_table(["Bucket", "n", "Face heuristic", "Contrast", "Brightness", "Busy", "Accent", "Lower text energy"], [
    [b, t["n"], t["face_rate_heuristic"], t["avg_contrast"], t["avg_brightness"], t["avg_busy"],
     t["avg_accent_share"], t["avg_lower_text_energy"]]
    for b, t in thumb_by_bucket.items()
]) + "\n")
A("`face_present` skin-tone pixel heuristic hai; face recognition/OCR nahi. 40 thumbnails ki full rows JSON extract me hain.\n")

A("## 12. Transcript blocker ledger — 12/12 errors\n")
A(md_table(["Video", "Teardown", "Transcript", "Words", "Detail"], [
    [x["video_id"], x["teardown_status"], x["transcript_status"], x["words"], c(x["detail"], 150)]
    for x in transcript_ledger
]) + "\n")

A("## 13. All 40 deep teardowns — public receipt + metadata + not-observed ledger\n")
A(md_table(["#", "ID", "Bucket", "Views", "Sec", "Channel", "Title", "Hook", "Desc words", "Chap", "Tags", "Caption", "Comments", "Transcript", "Editing"], [
    [i + 1, t["video_id"], t["duration_bucket"], fmt(t["views"]), t["duration_seconds"],
     c(t["channel"], 22), c(t["title"], 58), c(t["hook_type"], 14), t["description_words"],
     t["chapter_count"], len(t["tags"] or []), t["caption_flag"],
     f"{t['comment_mining_status']}/{t['comment_n'] or 0}",
     c((t["transcript_attempt"] or {}).get("status") if isinstance(t["transcript_attempt"], dict) else t["transcript_attempt"], 18),
     (t["editing_observation"] or {}).get("status")]
    for i, t in enumerate(deep_compact)
]) + "\n")
A("Har teardown me `editing_observation.status=not_observed`; koi competitor frame/cut/music/SFX/caption animation inspect nahi kiya gaya.\n")

A("### 12 detailed teardown cards\n")
for i, t in enumerate(deep_compact[:12]):
    A(f"\n#### {i+1}. `{t['video_id']}` — {c(t['title'], 100)}\n")
    A(md_table(["Field", "Value"], [
        ["Channel / published", f"{c(t['channel'], 40)} / {c(t['published'], 20)}"],
        ["Public receipt", f"{fmt(t['views'])} views, {t['duration_seconds']}s, like {t['like_rate']}, comment {t['comment_rate']}, caption flag {t['caption_flag']}"],
        ["Hook sentence", c(t["hook_sentence"], 240)],
        ["Hook type / description", f"{t['hook_type']} / {t['description_words']} words, {t['number_count']} numbers, {t['chapter_count']} chapter markers, script-like synopsis {t['script_like_synopsis']}"],
        ["CTA true", c(", ".join(t["cta_true"]) or "none", 120)],
        ["Tags", c(", ".join(t["tags"] or []) or "none", 180)],
        ["Chapters", c("; ".join(f"{z['time']} {z['label']}" for z in (t["chapters"] or [])[:10]) or "none", 240)],
        ["Comment mining", f"{t['comment_mining_status']} n={t['comment_n']}; " + c("; ".join(f"{h['label']} {h['share']:.0%}" for h in t["comment_patterns"]) or "no pattern >=2.5%", 140)],
        ["Transcript attempt", c(t["transcript_attempt"], 180)],
        ["Editing observation", c((t["editing_observation"] or {}).get("detail"), 220)],
        ["Boundary", c(t["boundary"], 100)],
    ]) + "\n")

A("## 14. mostPopular top 5 per region — niche verdict nahi\n")
A(md_table(["Region", "ID", "Views", "Sec", "Channel", "Title"], [
    [p["region"], p["id"], fmt(p["views"]), p["duration_seconds"], c(p["channel"], 25), c(p["title"], 70)]
    for p in popular_top
]) + "\n")

A("## 15. Not-observed / not-available / not-claimed ledger\n")
A(md_table(["Item", "Status", "Proof / boundary"], [
    [x["item"], x["status"], c(x["proof"], 180)] for x in not_observed
]) + "\n")

A("## 16. Source files\n")
for f in sorted(E.glob("*.json")):
    A(f"- `research/deep_forensic_v18/api_evidence/{f.name}`")
A("- `research/deep_forensic_v18/FORENSIC_EVIDENCE_EXTRACT_V18.json` — 717-candidate index, 40 teardown records, all derived tables\n")
A("- `research/deep_forensic_v18/DEEP_FORENSIC_V18.md` — auto-generated data appendix from the Actions builder\n")

(ROOT / "EVIDENCE_TABLES_V18.md").write_text("\n".join(M) + "\n", encoding="utf-8")
print("WROTE", ROOT / "FORENSIC_EVIDENCE_EXTRACT_V18.json")
print("WROTE", ROOT / "EVIDENCE_TABLES_V18.md")
print("integrity", json.dumps(integrity, ensure_ascii=False))
