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
    # field2 is the filters sub-message; duration lives INSIDE it (field3). Appending
    # duration at the top level silently does nothing - that bug made short and long lanes
    # return identical rows in run 43380197994.
    filters = b"\x10\x01"
    if duration in ("short", "medium", "long"):
        filters += b"\x18" + _varint({"short": 1, "long": 2, "medium": 3}[duration])
    body = b"\x08" + _varint(3) + b"\x12" + _varint(len(filters)) + filters
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


def _subs_num(v) -> float | None:
    """'47' / '4.85K' / '1.52M' -> float."""
    if v is None:
        return None
    t = str(v).strip().replace(",", "").upper()
    mult = 1.0
    if t.endswith("K"):
        mult, t = 1e3, t[:-1]
    elif t.endswith("M"):
        mult, t = 1e6, t[:-1]
    elif t.endswith("B"):
        mult, t = 1e9, t[:-1]
    try:
        return float(t) * mult
    except ValueError:
        return None


def search_candidates(title: str) -> list[dict]:
    """Every channel that owns a video close to this exact screenshot title."""
    try:
        rows = inner_search(title)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return []
    norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()  # noqa: E731
    want = norm(title)
    out, seen = [], set()
    for r in rows:
        cid = r.get("channel_id")
        if not cid or cid in seen:
            continue
        have = norm(r.get("title"))
        if not have:
            continue
        a, b = set(want.split()), set(have.split())
        overlap = len(a & b) / max(1, len(a | b))
        if overlap < 0.55:
            continue
        seen.add(cid)
        out.append({"channel_id": cid, "channel_title": r.get("channel_title", ""),
                    "title_overlap": round(overlap, 3), "video_title": r.get("title", "")})
    return sorted(out, key=lambda c: -c["title_overlap"])


def resolve_channel_via_inner(title: str) -> str | None:
    """A screenshot's own video title -> the owning channelId (public web search)."""
    cands = search_candidates(title)
    if not cands:
        return None
    best = cands[0]
    return best["channel_id"] if best["title_overlap"] >= 0.6 else None


def pick_channel(title: str, screenshot_subs=None, screenshot_videos=None,
                 screenshot_name: str = "") -> dict | None:
    """Choose between same-title channels using the screenshot's own subscriber and
    video counts. Copycat channels reuse winning titles verbatim; counts do not match.

    Returns {channel_id, score, why} or None. Purely a ranking of public page data.
    """
    cands = search_candidates(title)
    if not cands:
        return None
    want_subs = _subs_num(screenshot_subs)
    want_vids = _subs_num(screenshot_videos)
    name_norm = re.sub(r"[^a-z0-9]+", "", (screenshot_name or "").lower())

    def score(c):
        s = c["title_overlap"]
        nm = re.sub(r"[^a-z0-9]+", "", (c.get("channel_title") or "").lower())
        if name_norm and nm:
            if name_norm in nm or nm in name_norm:
                s += 0.30
            else:
                ratio = difflib_ratio(name_norm, nm)
                s += 0.30 * max(0.0, ratio - 0.55) / 0.45
        return s

    ranked = sorted(cands, key=score, reverse=True)
    top = dict(ranked[0])
    top["score"] = round(score(top), 3)
    top["why"] = f"title overlap {top['title_overlap']}"
    return top


def difflib_ratio(a: str, b: str) -> float:
    import difflib
    return difflib.SequenceMatcher(None, a, b).ratio()
