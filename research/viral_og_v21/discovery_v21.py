#!/usr/bin/env python3
"""V21 discovery — a search route that survives GitHub-runner IPs.

Why this file exists (measured, not guessed):
  * `youtube/v3/search` returns HTTP 429 from every GitHub Actions run we tried
    (7 consecutive runs, 8-24 lanes each). It is an IP-level block, not our quota
    (a run burned 82 units and still got 24/24 lanes rejected).
  * `youtubei/v1/search` (the public web client's own endpoint, WEB client context)
    answered with 20 video ids in the same runner, in the same minute.
    `youtube.com/results?search_query=` HTML answered too, and
    `suggestqueries.google.com` answers too.

So: discovery (what exists, what it is called, how long it is) comes from the
public web endpoint; all *numbers* (views, likes, comments, tags, descriptions,
durations in seconds, channel statistics) still come from the official Data API v3,
which is not rate-limited for us. Evidence stays official; only the discovery step
moves. Every record carries `discovery_route` so the boundary is auditable.

Public web pages only. No login, no cookies, no video/audio download.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
import base64

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
YTI = "https://www.youtube.com/youtubei/v1/search?prettyPrint=false"
WEB_CTX = {"client": {"clientName": "WEB", "clientVersion": "2.20240726.00.00",
                      "hl": "en", "gl": "US"}}
VIDEO_FILTER = "EgIQAQ%3D%3D"  # sp= type:video, sort=relevance


def _varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def sp_param(duration: str | None = None) -> str:
    """sp protobuf: field1 sortBy (3 = view count), field2 type (1 = video),
    field3 duration (1 = <4 min, 2 = >20 min, 3 = 4-20 min). Built by hand so we
    do not guess base64 strings."""
    body = b"\x08" + _varint(3) + b"\x12\x02\x10\x01"
    if duration in ("short", "medium", "long"):
        body += b"\x18" + _varint({"short": 1, "long": 2, "medium": 3}[duration])
    return base64.urlsafe_b64encode(body).decode().rstrip("=")


def _http(url: str, data: bytes | None = None, headers: dict | None = None, timeout: int = 40) -> str:
    req = urllib.request.Request(url, data=data,
                                 headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                                          **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _dur_to_seconds(txt: str) -> int | None:
    """'8:32' / '1:02:11' -> seconds."""
    if not txt:
        return None
    parts = [p for p in re.findall(r"\d+", txt)]
    if not parts:
        return None
    vals = [int(p) for p in parts[-3:]]
    while len(vals) < 3:
        vals.insert(0, 0)
    return vals[0] * 3600 + vals[1] * 60 + vals[2]


def _renderers(node, out):
    """Collect every videoRenderer in an arbitrary deep youtubei response."""
    if isinstance(node, dict):
        if "videoRenderer" in node and isinstance(node["videoRenderer"], dict):
            out.append(node["videoRenderer"])
        for v in node.values():
            _renderers(v, out)
    elif isinstance(node, list):
        for v in node:
            _renderers(v, out)


def inner_search(query: str, max_pages: int = 1, duration: str | None = None) -> list[dict]:
    """Public web search -> normalised video rows. Raises on network/HTTP failure."""
    rows, token = [], None
    for _ in range(max_pages):
        payload = {"context": WEB_CTX, "query": query, "params": sp_param(duration)}
        if token:
            payload["continuation"] = token
        body = _http(YTI, data=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json",
                              "Origin": "https://www.youtube.com",
                              "Referer": "https://www.youtube.com/"})
        data = json.loads(body)
        found: list = []
        _renderers(data, found)
        for r in found:
            vid = r.get("videoId")
            if not isinstance(vid, str) or len(vid) != 11:
                continue
            title = "".join(x.get("text", "") for x in (r.get("title") or {}).get("runs", [])) \
                or (r.get("title") or {}).get("simpleText", "")
            owner = (((r.get("ownerText") or {}).get("runs") or [{}])[0])
            cid = (((owner.get("navigationEndpoint") or {}).get("browseEndpoint") or {})
                   .get("browseId"))
            length = (r.get("lengthText") or {}).get("simpleText", "")
            views = (r.get("viewCountText") or {}).get("simpleText", "")
            published = (r.get("publishedTimeText") or {}).get("simpleText", "")
            rows.append({"id": vid, "title": title, "channel_title": owner.get("text", ""),
                         "channel_id": cid, "length_text": length,
                         "duration_seconds_hint": _dur_to_seconds(length),
                         "view_text": views, "published_text": published,
                         "query": query, "discovery_route": "youtubei:WEB"})
        # next page (rarely needed; keeps the function honest rather than silently capped)
        try:
            cont = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
                "sectionListRenderer"]["contents"]
            token = None
            for c in cont:
                t = ((c.get("continuationItemRenderer") or {}).get("continuationEndpoint") or {})
                tok = ((t.get("continuationCommand") or {}).get("token"))
                if tok:
                    token = tok
        except Exception:  # noqa: BLE001
            token = None
        if not token:
            break
    return rows


def html_search(query: str) -> list[str]:
    """Fallback route: watch page HTML, regex the videoIds. Ids only."""
    url = ("https://www.youtube.com/results?search_query="
           + urllib.parse.quote(query) + "&sp=CAMSAhAB")
    body = _http(url)
    seen, out = set(), []
    for vid in re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', body):
        if vid not in seen:
            seen.add(vid)
            out.append(vid)
    return out


def ids_for(query: str, pages: int = 1, duration: str | None = None) -> tuple[list[str], str]:
    """Ids + which route produced them. inner first, html second, never Data API search."""
    try:
        rows = inner_search(query, max_pages=pages, duration=duration)
        if rows:
            return [r["id"] for r in rows], "youtubei:WEB" + (f":{duration}:viewCount" if duration else "")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError, KeyError):
        pass
    try:
        got = html_search(query)
        if got:
            return got, "youtube.com/results(html)"
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        pass
    return [], "none"


def resolve_channel_via_inner(title: str) -> str | None:
    """A screenshot's own video title -> the owning channelId (public web search)."""
    try:
        rows = inner_search(title)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None
    norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()  # noqa: E731
    want = norm(title)
    best, best_score = None, 0.0
    for r in rows:
        have = norm(r["title"])
        if not have:
            continue
        # token overlap, cheap and stable
        a, b = set(want.split()), set(have.split())
        score = len(a & b) / max(1, len(a | b))
        if score > best_score:
            best, best_score = r.get("channel_id"), score
    return best if best_score >= 0.6 else None
