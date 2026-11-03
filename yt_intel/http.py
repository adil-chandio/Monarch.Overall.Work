"""One HTTP surface for the whole package.

Why a wrapper instead of requests.get everywhere:

- **Retry with backoff** on 429/500/503, because YouTube throttles and a silent retry
  loop is what produces biased corpora.
- **Rate limiting that is polite by default.** The scraper is not the important part of
  the internet; 1 request/second sustained, burst of 3.
- **A disk cache** keyed by URL+params, so re-running an analysis costs nothing and two
  runs of the same query return identical bytes (reproducibility).
- **Honest errors**: `RateLimited` is a distinct exception so callers can mark a corpus
  incomplete instead of pretending it is complete.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

CACHE_DIR = os.environ.get("YT_INTEL_CACHE", os.path.join(".cache", "yt-intel"))
TIMEOUT = float(os.environ.get("YT_INTEL_TIMEOUT", "25"))
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
_RATE = {"last": 0.0, "min_gap": float(os.environ.get("YT_INTEL_MIN_GAP", "1.0"))}


class RateLimited(Exception):
    """YouTube/Google asked us to slow down (or blocked the datacenter IP)."""


class Blocked(RateLimited):
    """Consent-wall / bot-wall response rather than a plain 429."""


def _cache_path(url: str, body: str | None = None) -> str:
    h = hashlib.sha256((url + "|" + (body or "")).encode()).hexdigest()[:32]
    return os.path.join(CACHE_DIR, h + ".json")


def _wait() -> None:
    gap = _RATE["min_gap"]
    dt = time.time() - _RATE["last"]
    if dt < gap:
        time.sleep(gap - dt + random.uniform(0, 0.25))
    _RATE["last"] = time.time()


def get(
    url: str,
    params: dict[str, Any] | None = None,
    *,
    headers: dict[str, str] | None = None,
    cache: bool = True,
    ttl: float = 3600.0,
    retries: int = 3,
    body: str | None = None,
    method: str | None = None,
) -> bytes:
    """GET (or POST when body is given) with cache, backoff and rate limiting."""
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    path = _cache_path(url, body)
    if cache and os.path.exists(path):
        age = time.time() - os.path.getmtime(path)
        if age < ttl:
            with open(path, "rb") as f:
                return f.read()

    hdrs = {
        "User-Agent": UA,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    }
    if headers:
        hdrs.update(headers)

    last_err: Exception | None = None
    for attempt in range(retries):
        _wait()
        req = urllib.request.Request(
            url, data=body.encode() if body else None, headers=hdrs, method=method or ("POST" if body else "GET")
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                raw = resp.read()
            if cache:
                os.makedirs(CACHE_DIR, exist_ok=True)
                tmp = path + ".tmp"
                with open(tmp, "wb") as f:
                    f.write(raw)
                os.replace(tmp, path)
            return raw
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                last_err = e
                _RATE["last"] = time.time() + 2 ** attempt
                continue
            if e.code in (401, 403):
                raise Blocked(f"{e.code} for {url}") from e
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            _RATE["last"] = time.time() + 2 ** attempt
            continue
    raise RateLimited(f"gave up after {retries} attempts on {url}: {last_err}")


def get_json(url: str, params: dict[str, Any] | None = None, **kw) -> Any:
    return json.loads(get(url, params, **kw).decode("utf-8", "replace"))


def clear_cache() -> None:
    if os.path.isdir(CACHE_DIR):
        for f in os.listdir(CACHE_DIR):
            if f.endswith(".json"):
                os.remove(os.path.join(CACHE_DIR, f))
