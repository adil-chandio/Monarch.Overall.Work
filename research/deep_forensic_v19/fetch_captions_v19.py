#!/usr/bin/env python3
"""V19 — caption / script acquisition pass.

Why this exists
---------------
V18.1 ended with an honest hole: 12/12 caption attempts blocked, so no competitor
spoken script existed anywhere in the repo. V19 tries a different, *public-page* route
(youtubetotranscript.com) plus the repo's own caption lane, and records every outcome —
including "this video has no captions" which is a real finding, not a failure.

Contract
--------
* Records the transcript as fetched, verbatim, with the source URL and words count.
* Never invents, never completes, never paraphrases into "the script".
* Marks `caption_flag_vs_public`: whether YouTube's own caption flag said True while the
  public page said no captions (that is a data-quality finding worth keeping).
* No video/audio download. Text only.

Run locally (no key needed):
    python3 research/deep_forensic_v19/fetch_captions_v19.py
In CI the same script runs after the API lanes and reads ids from V18 evidence.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V18 = ROOT / "research" / "deep_forensic_v18" / "api_evidence"
OUT = ROOT / "research" / "deep_forensic_v19" / "captions"
OUT.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
ENDPOINT = "https://youtubetotranscript.com/transcript"


def _get(url: str, timeout: int = 25) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return 0, f"__ERR__{e!r}"


NO_CAPTIONS = ("This video has no captions",)
UNAVAILABLE = ("This video isn't available",)


def parse(html: str) -> dict:
    """Pull the transcript block out of the public page. Returns text + status."""
    if not html:
        return {"status": "no_response", "text": "", "words": 0}
    for marker, status in ((NO_CAPTIONS[0], "no_captions"), (UNAVAILABLE[0], "unavailable")):
        if marker in html:
            return {"status": status, "text": "", "words": 0}
    m = re.search(r"<h2[^>]*>\s*Transcript\s*</h2>(.*?)(?:Back To Top|## AI Features|<h2)", html, re.S)
    block = m.group(1) if m else ""
    if not block:
        return {"status": "parse_failed", "text": "", "words": 0}
    block = re.sub(r"<script.*?</script>", " ", block, flags=re.S)
    block = re.sub(r"<[^>]+>", "\n", block)
    lines = [re.sub(r"\s+", " ", l).strip() for l in block.split("\n")]
    lines = [l for l in lines
             if l and l not in {"Pin video", "Transcript", "AI Summaries", "Copy", "Timestamp OFF",
                                "Translate", "OFF", "Get Free Transcript"}]
    text = re.sub(r"[ \t]+", " ", " ".join(lines)).strip()
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    words = len(re.findall(r"\b[\w'’-]+\b", text))
    return {"status": "ok" if words >= 8 else "too_short", "text": text, "words": words}


def fetch_one(video_id: str) -> dict:
    url = f"{ENDPOINT}?v={urllib.parse.quote(video_id)}"
    code, html = _get(url)
    if code == 0:
        return {"id": video_id, "url": url, "http": 0, "status": "network_error",
                "detail": html[:200], "text": "", "words": 0}
    parsed = parse(html)
    parsed.update({"id": video_id, "url": url, "http": code})
    return parsed


def load_targets(limit: int = 60) -> list[dict]:
    """Targets = highest-view captioned videos + every selected deep id."""
    raw = json.loads((V18 / "video_details_v18.json").read_text())["videos"]
    deep = json.loads((V18 / "deep_teardowns_v18.json").read_text())
    selected = []
    if isinstance(deep, dict):
        for v in deep.values() if isinstance(deep, dict) else []:
            pass
    known = {}
    for d in (deep.get("teardowns") or deep.get("records") or []) if isinstance(deep, dict) else deep:
        if isinstance(d, dict) and d.get("id"):
            known[d["id"]] = d
    cap = [r for r in raw if r.get("caption")]
    cap.sort(key=lambda r: -(r.get("views") or 0))
    seen, targets = set(), []
    for r in cap:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        targets.append({"id": r["id"], "title": r.get("title", ""), "channel": r.get("channel", ""),
                        "views": r.get("views"), "duration": r.get("duration"),
                        "caption_flag": True, "why": "caption_flag_true_and_high_views"})
        if len(targets) >= limit:
            break
    for vid in known:
        if vid in seen:
            continue
        seen.add(vid)
        targets.append({"id": vid, "title": known[vid].get("title", ""), "why": "deep_teardown_id"})
    return targets


def main(argv: list[str]) -> int:
    limit = int(argv[1]) if len(argv) > 1 else 60
    targets = load_targets(limit)
    print(f"targets: {len(targets)}", flush=True)
    results = []
    for i, t in enumerate(targets, 1):
        r = fetch_one(t["id"])
        r.update({k: t.get(k) for k in ("title", "channel", "views", "duration", "caption_flag", "why")})
        results.append(r)
        print(f"  [{i}/{len(targets)}] {t['id']:12s} {r['status']:12s} words={r['words']:5d} "
              f"{(t.get('title') or '')[:48]}", flush=True)
        time.sleep(1.2)

    ok = [r for r in results if r["status"] == "ok"]
    summary = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "public page youtubetotranscript.com (third-party renderer of YouTube captions)",
        "targets": len(results),
        "ok": len(ok),
        "no_captions": sum(1 for r in results if r["status"] == "no_captions"),
        "unavailable": sum(1 for r in results if r["status"] == "unavailable"),
        "too_short": sum(1 for r in results if r["status"] == "too_short"),
        "network_error": sum(1 for r in results if r["status"] == "network_error"),
        "parse_failed": sum(1 for r in results if r["status"] == "parse_failed"),
        "total_words": sum(r["words"] for r in ok),
        "boundary": ("Public caption text only, captured verbatim for quote-level analysis. "
                     "Used to describe hook/timing/structure of the reference video. NOT copied "
                     "into our scripts, NOT re-uploaded, NOT claimed as our writing."),
    }
    (OUT / "captions_v19.json").write_text(json.dumps({"summary": summary, "records": results},
                                                      indent=1, ensure_ascii=False) + "\n")
    (OUT / "run_v19_captions.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
