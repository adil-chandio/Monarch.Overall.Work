"""Access layer: the ONE place that knows how to talk to YouTube.

Two lanes, chosen automatically at runtime and reported in every corpus:

  `api`     YouTube Data API v3 — needs a free key in YOUTUBE_API_KEY.
            10,000 quota units/day. search = 100 units, videos.list = 1, channels = 1.
            That is ~99 searches/day; the budget allocator below makes it last.

  `web`     Keyless fallback: public html/search/results pages + the innertube JSON
            endpoint YouTube's own web client uses, plus the public autocomplete API.
            No key, no quota — but YouTube throttles datacenter IPs, so a blocked
            response raises Blocked and the caller records `status: rate_limited`
            instead of shipping a quietly biased corpus.

Nothing here downloads video or audio. Metadata and text only.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Any

from . import http

API_KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
API_BASE = "https://www.googleapis.com/youtube/v3"
INNERTUBE = "https://www.youtube.com/youtubei/v1"
WEB_CLIENT = {
    "client": {"clientName": "WEB", "clientVersion": "2.20241101.01.00", "hl": "en", "gl": "US"},
    "user": {"lockedSafetyMode": False},
    "context": {"client": {"clientName": "WEB", "clientVersion": "2.20241101.01.00", "hl": "en", "gl": "US"}},
}


@dataclass
class Corpus:
    """Every fetch returns one of these, including how it failed."""
    kind: str
    lane: str
    query: str = ""
    items: list = field(default_factory=list)
    status: str = "ok"                 # ok | rate_limited | blocked | empty | error
    detail: str = ""
    fetched_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


def lane() -> str:
    """Which lane will actually be used right now."""
    return "api" if API_KEY else "web"


# --------------------------------------------------------------------------- quota
class Budget:
    """Data API quota allocator. Local, approximate, and deliberately conservative.

    Resets at midnight Pacific like Google's. State lives in a cache file so a CLI run
    and a CI run share the same view of the day.
    """

    COSTS = {"search": 100, "videos": 1, "channels": 1, "playlistItems": 1, "commentThreads": 1}
    DAILY = 10_000

    def __init__(self, path: str | None = None):
        self.path = path or os.path.join(http.CACHE_DIR, "budget.json")
        self.state = self._load()

    def _load(self) -> dict:
        today = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 8 * 3600))  # PT-ish
        try:
            with open(self.path) as f:
                s = json.load(f)
            if s.get("day") != today:
                raise ValueError
            return s
        except Exception:
            return {"day": today, "used": 0, "calls": {}}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.state, f)

    @property
    def remaining(self) -> int:
        return max(0, self.DAILY - self.state["used"])

    def can(self, op: str) -> bool:
        return self.remaining >= self.COSTS.get(op, 1)

    def spend(self, op: str) -> None:
        self.state["used"] += self.COSTS.get(op, 1)
        self.state["calls"][op] = self.state["calls"].get(op, 0) + 1
        self._save()


BUDGET = Budget()


def _api(path: str, params: dict, op: str) -> dict:
    if not BUDGET.can(op):
        raise http.RateLimited(f"daily Data API quota exhausted ({BUDGET.DAILY} units)")
    # spend only AFTER the response lands: a request that never reached Google (DNS, TLS,
    # blocked network) costs nothing, and counting it would make the budget lie low.
    data = http.get_json(f"{API_BASE}/{path}", {**params, "key": API_KEY})
    BUDGET.spend(op)
    return data


# --------------------------------------------------------------------------- search
def autocomplete(q: str, gl: str = "US") -> list[str]:
    """Google/YouTube search suggestions — the cheapest demand signal that exists.

    These are *real people typing*, ordered by popularity, refreshed constantly.
    It is why this module works without a key.
    """
    raw = http.get(
        "https://suggestqueries.google.com/complete/search",
        {"client": "youtube", "ds": "yt", "hl": "en", "gl": gl, "q": q},
        headers={"Accept": "application/json"},
    ).decode("utf-8", "replace")
    m = re.search(r"\((.*)\)\s*$", raw.strip(), re.S)  # jsonp-ish wrapper
    payload = m.group(1) if m else raw
    try:
        data = json.loads(payload)
    except Exception:
        return []
    out = []
    for row in data[1] if len(data) > 1 else []:
        term = row[0] if isinstance(row, list) else row
        if isinstance(term, str) and term.strip():
            out.append(term.strip())
    return out


_VIDEO_ID = re.compile(r'"videoId":"([A-Za-z0-9_-]{11})"')


# YouTube search filters, as the `sp` query parameter. These are the exact base64 tokens the
# UI puts in the URL when you click the filter chip; the keyless lane has no other way to ask.
# Verified against the tokens YouTube's own filter menu produces (type=video, sort, upload).
SP = {
    "relevance": "",
    "date": "CAI%3D",            # sort by upload date
    "viewCount": "CAM%3D",       # sort by view count
    "thisMonth": "EgQIBBAB",     # this month
    "thisWeek": "EgQIBRAB",      # this week
    "videoOnly": "EgIQAQ%3D%3D",  # videos only
}

# The two lanes accept different words for the same intent: the Data API has
# order={relevance,date,rating,title,videoCount} plus a `publishedAfter` timestamp, while the
# keyless lane has base64 filter tokens. Passing one lane's vocabulary to the other is how
# `--order thisMonth` on a keyed machine returned HTTP 400 and became a RETRY with no
# explanation. Normalise here, once.
API_ORDER = {"relevance": "relevance", "viewCount": "viewCount", "date": "date",
             "thisMonth": "date", "thisWeek": "date", "videoOnly": "relevance"}
API_WINDOW_DAYS = {"thisMonth": 30, "thisWeek": 7}


def normalise_order(order: str) -> str:
    """Map the shared vocabulary onto the Data API's, or fail loudly."""
    if order not in SP:
        raise ValueError(f"unknown order {order!r}; known: {sorted(SP)}")
    return API_ORDER[order]


def _web_search_page(q: str, sp: str = "") -> str:
    from urllib.parse import quote
    url = f"https://www.youtube.com/results?search_query={quote(q)}"
    if sp:
        url += f"&sp={sp}"
    html = http.get(url, headers={"Cookie": "SOCS=CAI; CONSENT=YES+1"}).decode("utf-8", "replace")
    if "consent.youtube.com" in html and "ytInitialData" not in html:
        raise http.Blocked("consent wall")
    return html


def _rich_grid(html: str) -> list[dict]:
    """Parse ytInitialData from a search-results page into flat video rows."""
    m = re.search(r"var ytInitialData\s*=\s*(\{.+?\});</script>", html, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except Exception:
        return []

    rows: list[dict] = []

    def walk(node):
        if isinstance(node, dict):
            if "videoRenderer" in node:
                rows.append(_from_renderer(node["videoRenderer"]))
            if "lockupViewModel" in node:                     # 2024+ web layout
                rows.append(_from_lockup(node["lockupViewModel"]))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    seen, out = set(), []
    for r in rows:
        if r and r.get("id") and r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    return out


def _txt(obj) -> str:
    if not obj:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        if "simpleText" in obj:
            return obj["simpleText"]
        if "runs" in obj:
            return "".join(r.get("text", "") for r in obj["runs"])
        if "content" in obj:
            return obj["content"]
    return ""


def _from_lockup(lv: dict) -> dict:
    """New-style lockup: id lives in contentId, text in metadata parts."""
    vid = lv.get("contentId", "")
    meta = lv.get("metadata", {}).get("lockupMetadataViewModel", {})
    title = _txt(meta.get("title"))
    rows = []
    for part in meta.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", []):
        for p in part.get("metadataParts", []):
            t = _txt(p.get("text"))
            if t:
                rows.append(t)
    published = next((r for r in rows if "ago" in r.lower()), "")
    views = _parse_count(next((r for r in rows if "view" in r.lower()), ""))
    # Two states look like data and are not:
    #   "No views"  -> _parse_count reads the word 'views' as nothing and a missing count
    #                  became a 0 in downstream medians, i.e. a video that was simply too new
    #                  to have a count was averaged in as a total failure.
    #   "Streamed 2 years ago" / "Premiered ..." -> an age, but not a publish date; and a live
    #                  stream's view count is not comparable to a normal video's.
    if views is None and re.search(r"\bno views\b", " ".join(rows), re.I):
        views = 0
    if re.match(r"^\s*(streamed|premiered|scheduled)", published, re.I):
        published = re.sub(r"^\s*(streamed|premiered|scheduled( for)?)\s*", "", published, flags=re.I)
    return {
        "id": vid, "title": title, "channel": rows[0] if rows else "",
        "meta": " · ".join(rows[1:]) if len(rows) > 1 else "",
        "views": views,
        "published": published,
    }


def _parse_count(s: str) -> int | None:
    if not s:
        return None
    m = re.search(r"([\d.,]+)\s*([KMB])?", s, re.I)
    if not m:
        return None
    try:
        n = float(m.group(1).replace(",", ""))
    except ValueError:
        return None
    mult = {"k": 1e3, "m": 1e6, "b": 1e9}.get((m.group(2) or "").lower(), 1)
    return int(n * mult)


def _from_renderer(v: dict) -> dict:
    return {
        "id": v.get("videoId", ""),
        "title": _txt(v.get("title")),
        "channel": _txt(v.get("ownerText")) or _txt(v.get("longBylineText")),
        "channel_id": (((v.get("ownerText") or {}).get("runs") or [{}])[0].get("navigationEndpoint", {})
                       .get("browseEndpoint", {}).get("browseId", "")),
        "views": _parse_count(_txt(v.get("viewCountText"))),
        "published": _txt(v.get("publishedTimeText")),
        "duration": _txt(v.get("lengthText")),
        "thumb": ((v.get("thumbnail", {}).get("thumbnails") or [{}])[-1].get("url", "")),
    }


def search(q: str, limit: int = 30, order: str = "relevance", published_after_days: int = 0) -> Corpus:
    """Search videos. API lane when a key exists, keyless web lane otherwise.

    `order` is the shared vocabulary (see SP): `thisMonth` / `thisWeek` mean "sorted newest,
    published within the window", and both lanes understand them.
    """
    if lane() == "api":
        try:
            api_order = normalise_order(order)
        except ValueError as e:
            return Corpus("search", "api", q, [], "error", str(e))
        published_after_days = published_after_days or API_WINDOW_DAYS.get(order, 0)

        params = {"part": "snippet", "q": q, "type": "video",
                  "maxResults": min(50, limit), "order": api_order}
        if published_after_days:
            import datetime as dt
            since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=published_after_days)
            params["publishedAfter"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            data = _api("search", params, "search")
            ids = [i["id"]["videoId"] for i in data.get("items", []) if i.get("id", {}).get("videoId")]
            if not ids:
                # An empty API result is not automatically "nothing exists". Google answers a
                # placeholder/invalid key with HTTP 200 and zero items, which used to land as
                # status "ok" with an empty corpus — indistinguishable from a genuinely empty
                # topic, and the worst possible way to be wrong. Say what it probably is.
                return Corpus("search", "api", q, [], "empty",
                              "the API returned zero items for a normal query — usually a "
                              "placeholder or unactivated key, or a quota of 0. Verify with: "
                              "python -m yt_intel doctor")
            stats = videos(ids).items
            return Corpus("search", "api", q, stats)
        except http.RateLimited as e:
            return Corpus("search", "api", q, [], "rate_limited", str(e))
        except Exception as e:  # noqa: BLE001 - report, never crash a corpus run
            return Corpus("search", "api", q, [], "error", repr(e))

    # The keyless lane used to ignore `order` completely, then sort locally by viewCount when
    # asked — which reads as "sorted by views" while actually being relevance-ordered, truncated
    # to 20 rows. That is a lie the caller cannot see. Ask the server instead.
    try:
        rows = _rich_grid(_web_search_page(q, SP.get(order, "")))
    except http.Blocked as e:
        return Corpus("search", "web", q, [], "blocked", str(e))
    except http.RateLimited as e:
        return Corpus("search", "web", q, [], "rate_limited", str(e))
    if order not in SP:
        return Corpus("search", "web", q, [], "error", f"unknown order {order!r}; known: {sorted(SP)}")
    return Corpus("search", "web", q, rows[:limit], "ok" if rows else "empty")


# --------------------------------------------------------------------------- videos
def videos(ids: list[str]) -> Corpus:
    """Bulk statistics for video ids (1 quota unit per call up to 50 ids)."""
    ids = [i for i in dict.fromkeys(ids) if i]
    if not ids:
        return Corpus("videos", lane(), "", [], "empty")
    if lane() == "api":
        out: list[dict] = []
        for i in range(0, len(ids), 50):
            data = _api("videos", {"part": "snippet,statistics,contentDetails", "id": ",".join(ids[i:i + 50])}, "videos")
            for it in data.get("items", []):
                st = it.get("statistics", {})
                out.append({
                    "id": it["id"],
                    "title": it.get("snippet", {}).get("title", ""),
                    "channel": it.get("snippet", {}).get("channelTitle", ""),
                    "channel_id": it.get("snippet", {}).get("channelId", ""),
                    "published": it.get("snippet", {}).get("publishedAt", ""),
                    "duration": it.get("contentDetails", {}).get("duration", ""),
                    "views": int(st["viewCount"]) if "viewCount" in st else None,
                    "likes": int(st["likeCount"]) if "likeCount" in st else None,
                    "comments": int(st["commentCount"]) if "commentCount" in st else None,
                    "tags": it.get("snippet", {}).get("tags", []),
                    "description": it.get("snippet", {}).get("description", ""),
                    "thumb": (it.get("snippet", {}).get("thumbnails", {}).get("maxres")
                              or it.get("snippet", {}).get("thumbnails", {}).get("high", {})).get("url", ""),
                })
        return Corpus("videos", "api", "", out, "ok" if out else "empty")
    # web lane: oEmbed gives title/author per id without any quota
    out = []
    for vid in ids[:60]:
        try:
            o = http.get_json("https://www.youtube.com/oembed", {"url": f"https://www.youtube.com/watch?v={vid}", "format": "json"})
            out.append({"id": vid, "title": o.get("title", ""), "channel": o.get("author_name", ""),
                        "thumb": o.get("thumbnail_url", ""), "views": None, "likes": None})
        except Exception:
            continue
    return Corpus("videos", "web", "", out, "ok" if out else "blocked")


# --------------------------------------------------------------------------- comments
def comments(video_id: str, limit: int = 100, order: str = "relevance") -> Corpus:
    """Top comments for a video (API lane only; `commentThreads` = 1 quota unit per page).

    Why comments at all: a title tells you what the uploader promised, the comments tell
    you what the audience actually wanted next. Every "part 2?", "what about X?" and
    "this didn't work because Y" is a scripted brief for the next video, free.

    The keyless lane has no honest way to do this yet (the innertube continuation call is a
    parser fight that breaks weekly), so it returns `unavailable` with the reason instead of
    an empty list that reads like "this video has no comments".
    """
    if lane() != "api":
        return Corpus("comments", "web", video_id, [], "unavailable",
                      "comments need the Data API lane (commentThreads); no key in this environment")
    try:
        data = _api("commentThreads", {
            "part": "snippet", "videoId": video_id, "maxResults": min(100, limit),
            "order": order, "textFormat": "plainText",
        }, "commentThreads")
    except http.RateLimited as e:
        return Corpus("comments", "api", video_id, [], "rate_limited", str(e))
    except Exception as e:  # noqa: BLE001 - a disabled-comments video is a result, not a crash
        return Corpus("comments", "api", video_id, [], "error", repr(e))

    out = []
    for item in data.get("items", []):
        sn = item.get("snippet", {})
        top = sn.get("topLevelComment", {}).get("snippet", {})
        out.append({
            "text": top.get("textDisplay", ""),
            "likes": int(top.get("likeCount") or 0),
            "replies": int(sn.get("totalReplyCount") or 0),
            "author": top.get("authorDisplayName", ""),
            "published": top.get("publishedAt", ""),
        })
    return Corpus("comments", "api", video_id, out, "ok" if out else "empty")


# --------------------------------------------------------------------------- channel
def channel_uploads(handle_or_id: str, max_pages: int = 100) -> Corpus:
    """API uploads inventory, not a search sample or RSS's last 15 entries.

    Preserve partial results and explicitly flag truncation / unavailable video IDs.
    An API key exposes public records only, never private Studio analytics.
    """
    from urllib.parse import urlparse
    ident = handle_or_id.strip()
    if ident.startswith(("https://", "http://")):
        parsed = urlparse(ident)
        if parsed.hostname not in ("youtube.com", "www.youtube.com", "m.youtube.com"):
            return Corpus("channel", "api", ident, [], "error", "expected a YouTube channel URL")
        parts = parsed.path.strip("/").split("/")
        ident = parts[1] if parts[0] == "channel" and len(parts) > 1 else parts[0]
    if max_pages < 1:
        return Corpus("channel", "api", ident, [], "error", "max_pages must be positive")
    rows, ids, profile = [], [], {}
    token = ""
    try:
        selector = {"id": ident} if ident.startswith("UC") and len(ident) == 24 else {"forHandle": ident.lstrip("@")}
        data = _api("channels", {"part": "snippet,statistics,contentDetails,brandingSettings", **selector}, "channels")
        profiles = data.get("items", [])
        if not profiles:
            return Corpus("channel", "api", ident, [], "empty", "channel not found by API")
        profile = profiles[0]
        playlist = profile.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
        if not playlist:
            return Corpus("channel", "api", ident, [], "error", "channel has no uploads playlist")
        for _ in range(max_pages):
            params = {"part": "contentDetails", "playlistId": playlist, "maxResults": 50}
            if token:
                params["pageToken"] = token
            page = _api("playlistItems", params, "playlistItems")
            ids.extend(i["contentDetails"]["videoId"] for i in page.get("items", [])
                       if i.get("contentDetails", {}).get("videoId"))
            token = page.get("nextPageToken", "")
            if not token:
                break
        ids = list(dict.fromkeys(ids))
        # Fetch in batches so a later error does not discard earlier successful batches.
        for start in range(0, len(ids), 50):
            rows.extend(videos(ids[start:start + 50]).items)
        missing = sorted(set(ids) - {r["id"] for r in rows})
        detail = json.dumps({"profile": profile, "inventory_complete": not token and not missing,
                             "playlist_exhausted": not token, "missing_video_ids": missing,
                             "playlist_video_count": len(ids)}, ensure_ascii=False)
        return Corpus("channel", "api", profile["id"], rows,
                      "partial" if token or missing else ("ok" if rows else "empty"), detail)
    except Exception as e:
        return Corpus("channel", "api", ident, rows, "partial" if rows else "error",
                      http.scrub(json.dumps({"error": str(e), "profile": profile,
                                             "inventory_complete": False,
                                             "playlist_video_count": len(ids)})))


def channel(handle_or_id: str) -> Corpus:
    """Channel profile + recent uploads via the channel's public RSS feed.

    RSS is the one endpoint that has stayed keyless, unauthenticated and stable for a
    decade: `feeds/videos.xml?channel_id=…`. It gives the last 15 uploads with real
    publish times, which is exactly what a velocity baseline needs.
    """
    ident = handle_or_id.strip()
    if lane() == "api":
        return channel_uploads(ident)
    cid = ident if ident.startswith("UC") and len(ident) == 24 else ""
    try:
        if not cid:
            html = http.get(
                f"https://www.youtube.com/@{ident.lstrip('@')}" if not ident.startswith("http") else ident,
                headers={"Cookie": "SOCS=CAI; CONSENT=YES+1"},
            ).decode("utf-8", "replace")
            m = re.search(r'"channelId":"(UC[\w-]{22})"', html)
            if not m:
                return Corpus("channel", "web", ident, [], "blocked", "no channelId on page")
            cid = m.group(1)
        xml = http.get("https://www.youtube.com/feeds/videos.xml", {"channel_id": cid}).decode("utf-8", "replace")
        entries = re.findall(r"<entry>(.*?)</entry>", xml, re.S)
        items = []
        for e in entries:
            g = lambda tag: (re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", e, re.S) or [None, ""])[1]
            items.append({
                "id": (re.search(r"<yt:videoId>(.*?)</yt:videoId>", e) or [None, ""])[1],
                "title": _unescape(g("title")),
                "published": g("published"),
                "views": int(g("yt:statistics") and (re.search(r'views="(\d+)"', g("yt:statistics")) or [0, 0])[1] or 0),
                "likes": int((re.search(r'<yt:starRating[^>]*count="(\d+)"', e) or [0, 0])[1] or 0),
            })
        return Corpus("channel", "web", cid, items, "ok" if items else "empty")
    except http.RateLimited as e:
        return Corpus("channel", "web", ident, [], "rate_limited", str(e))


def _unescape(s: str) -> str:
    import html as h
    return h.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


# --------------------------------------------------------------------------- captions
def transcript(video_id: str, langs: tuple[str, ...] = ("en", "en-US", "en-GB")) -> dict:
    """Fetch a video's transcript through yt-dlp's caption endpoint (no download).

    Returns {status, lang, text, words, source}. `status` is never silently "ok" when it
    is not: auto-generated captions are marked `auto`, and a video with captions
    disabled says so.
    """
    try:
        import yt_dlp  # imported lazily so the rest of the package works without it
    except ImportError:
        return {"status": "unavailable", "detail": "yt-dlp not installed", "text": "", "words": 0}

    opts = {
        "quiet": True, "no_warnings": True, "skip_download": True,
        "writesubtitles": True, "writeautomaticsub": True, "subtitleslangs": list(langs),
        "subtitlesformat": "json3", "outtmpl": "/dev/null",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "detail": str(e)[:200], "text": "", "words": 0}

    subs = (info.get("subtitles") or {})
    auto = (info.get("automatic_captions") or {})
    tracks = subs or auto
    lang = next((l for l in langs if l in tracks), next(iter(tracks), None))
    if not lang:
        return {"status": "no_captions", "text": "", "words": 0, "title": info.get("title", "")}
    urls = [t.get("url") for t in tracks[lang] if t.get("ext") == "json3"] or [t.get("url") for t in tracks[lang]]
    if not urls:
        return {"status": "no_captions", "text": "", "words": 0}
    raw = http.get(urls[0], cache=True, ttl=86400 * 30)
    text, words = _json3_text(raw)
    return {
        "status": "ok", "lang": lang, "kind": "manual" if subs else "auto",
        "text": text, "words": words, "title": info.get("title", ""),
        "duration": info.get("duration"), "chapters": info.get("chapters") or [],
    }


def _json3_text(raw: bytes) -> tuple[str, int]:
    try:
        data = json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        return "", 0
    chunks = []
    for ev in data.get("events", []):
        for seg in ev.get("segs", []) or []:
            t = seg.get("utf8", "")
            if t:
                chunks.append(t)
        if ev.get("segs"):
            chunks.append(" ")
    text = re.sub(r"\s+", " ", "".join(chunks)).strip()
    return text, len(re.findall(r"\b\w+\b", text))
