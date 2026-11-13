"""Probe which discovery route survives GitHub-runner IPs. Read-only, prints counts only."""
import json, os, urllib.request, urllib.parse, urllib.error, sys

KEY = os.environ.get("YOUTUBE_API_KEY", "")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

def http(url, data=None, headers=None, timeout=30):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")

def probe(name, fn):
    try:
        out = fn()
        print(f"[{name}] OK -> {out}", flush=True)
    except Exception as e:
        print(f"[{name}] FAIL -> {type(e).__name__}: {str(e)[:220]}", flush=True)

Q = "what did ancient humans do all day animation"

def data_api():
    u = ("https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&order=viewCount"
         f"&maxResults=5&q={urllib.parse.quote(Q)}&key={KEY}")
    _, body = http(u)
    j = json.loads(body)
    return f"items={len(j.get('items', []))} first={j.get('items',[{}])[0].get('id',{}).get('videoId')}"

def yt_inner(client_name, client_version, extra=None):
    ctx = {"client": {"clientName": client_name, "clientVersion": client_version,
                      "hl": "en", "gl": "US"}}
    if extra: ctx["client"].update(extra)
    payload = {"context": ctx, "query": Q, "params": "EgIQAQ%3D%3D"}
    data = json.dumps(payload).encode()
    _, body = http("https://www.youtube.com/youtubei/v1/search?prettyPrint=false",
                   data=data, headers={"Content-Type": "application/json",
                                       "Origin": "https://www.youtube.com",
                                       "Referer": "https://www.youtube.com/"})
    ids = set()
    def walk(o):
        if isinstance(o, dict):
            vid = o.get("videoId")
            if isinstance(vid, str) and len(vid) == 11: ids.add(vid)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(json.loads(body))
    return f"videoIds={len(ids)} sample={list(ids)[:3]} bytes={len(body)}"

def html_results():
    u = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(Q) + "&sp=CAMSAhAB"
    _, body = http(u, headers={"Accept-Language": "en-US,en;q=0.9"})
    import re
    ids = set(re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', body))
    return f"videoIds={len(ids)} consent_wall={'consent.youtube' in body} bytes={len(body)}"

def suggest():
    u = ("https://suggestqueries.google.com/complete/search?client=firefox&gl=us&q="
         + urllib.parse.quote("what did ancient humans"))
    _, body = http(u)
    return f"len={len(body)} sample={body[:120]}"

print(f"key_present={bool(KEY)}", flush=True)
probe("dataapi_search", data_api)
probe("yt_inner_WEB", lambda: yt_inner("WEB", "2.20240726.00.00"))
probe("yt_inner_ANDROID", lambda: yt_inner("ANDROID", "19.09.37", {"androidSdkVersion": 30}))
probe("yt_inner_IOS", lambda: yt_inner("IOS", "19.09.3", {"deviceModel": "iPhone14,3"}))
probe("yt_html_results", html_results)
probe("google_suggest", suggest)
