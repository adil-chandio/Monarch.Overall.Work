#!/usr/bin/env python3
"""
V13 clip acquisition — NEW, rights-documented "caught on camera" moments.

Runs in GitHub Actions (full outbound network). Wikimedia Commons API is queried LIVE for
social-origin / CCTV / dashcam / security-camera video files whose extmetadata records a
commercial-reuse-compatible licence (PD / CC0 / CC BY 3.0 / CC BY 4.0). For each accepted
file the script:

  * downloads the original or a Commons 480p derivative,
  * objectively scores the most hooky 10-second window INSIDE the clip (motion + surprise),
  * emits a normalized 10 s MP4 "hook window" with its native audio untouched,
  * writes a per-file rights ledger (title, creator, licence, licence URL, source page,
    Commons SHA-1, download URL, local SHA-256, best-window timestamps),
  * writes a contact sheet of all hook frames for human review.

EXCLUDED: the ten V7 candidate titles, the NASA / Artemis II V10 Short, and anything whose
Commons metadata says SA / NC / fair-use-only / license-review-needed. No unverified
TikTok/Instagram/Reddit/Twitter/Dailymotion repost is downloaded; Commons file pages that
record a YouTube/Vimeo/SWNS/police-camera origin are the rights-cleared mirror instead.

No human legal review, no clearance opinion, no upload/publish, no virality claim.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research" / "caught_on_camera_v13"
WORK = ROOT / "production" / "monarch-cam" / "work" / "caught_on_camera_v13"  # ignored
WINDOWS = BASE / "windows"
REVIEW = BASE / "review"
for p in (WORK, WINDOWS, REVIEW):
    p.mkdir(parents=True, exist_ok=True)

API = "https://commons.wikimedia.org/w/api.php"
UA = ("MonarchCamV13/1.0 (https://github.com/adil-chandio/Monarch.Overall.Work; "
      "rights-documented caught-on-camera clip research)")
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept": "*/*"})

FF = "ffmpeg"
MAX_CLIPS = int(__import__("os").environ.get("V13_MAX_CLIPS", "20"))
WINDOW_S = 10.0
SAMPLE_FPS = 4

# POSITIVE, on-brand discovery: wildlife / animals / funny / surprising / skill moments.
# (The first pass used generic "caught on camera"/CCTV queries and returned murder CCTV,
# suicide bombings, missile strikes, plane crashes and robberies. That pass is REJECTED.)
QUERIES = [
    'animal "caught on camera" filetype:video',
    'wildlife "caught on camera" filetype:video',
    'CCTV animal filetype:video',
    '"security camera" bear filetype:video',
    'dog "caught on camera" filetype:video',
    'cat "caught on camera" filetype:video',
    'funny animal fail filetype:video',
    '"unexpected moment" animal filetype:video',
    'animal rescue "caught on camera" filetype:video',
    'bird "caught on camera" filetype:video',
    'squirrel feeder camera filetype:video',
    'raccoon "caught on camera" filetype:video',
    'trick shot caught on camera filetype:video',
    'skateboard fail filetype:video',
    'parkour fail filetype:video',
    'flash mob filetype:video',
    'funny fail video filetype:video',
    'octopus "caught on camera" filetype:video',
    'whale "caught on camera" filetype:video',
    'goat "caught on camera" filetype:video',
    '"caught on camera" filetype:video',
    'CCTV filetype:video',
    'dashcam filetype:video',
    '"viral video" filetype:video',
    '"unexpected moment" filetype:video',
    'funny animals filetype:video',
    'cute animals filetype:video',
    'animal fails filetype:video',
    'cat fails filetype:video',
    'dog fails filetype:video',
    'wildlife camera filetype:video',
    'bear enters house filetype:video',
    'animal in shop filetype:video',
    'unexpected animal filetype:video',
    'amazing animal moment filetype:video',
    'sports fail filetype:video',
    'fail compilation filetype:video',
]

# HARD content-safety gate. A family-safe, engaging caught-on-camera compilation must
# never contain murder / violence / war / terror / disaster / crime-victim footage.
BLOCK_TERMS = (
    "kill", "murder", "homicide", "death", "dead", "fatal", "shoot", "gun", "firearm",
    "bomb", "explosion", "blast", "missile", "strike", "attack", "terror", "suicide",
    "war", "military", "soldier", "combat", "drone", "rocket", "artillery", "invasion",
    "robbery", "burglary", "assault", "crime", "criminal", "suspect", "arrest", "stabbing",
    "knife", "blood", "gore", "victim", "kidnap", "abduct", "missing person",
    "seeking information", "police chase", "hostage", "cantonment", "precinct",
    "crash", "collision", "accident", "airline", "flight", "plane", "tornado", "hurricane",
    "earthquake", "disaster", "tragedy", "wreck", "protest", "riot", "9/11",
    "volgograd", "crimean", "bannu", "ramat gan", "nancy guthrie", "brian thompson",
    "saratov", "flight 3054", "flight77", "thai cctv", "homicide",
)
GOOD_TERMS = (
    "cat", "dog", "puppy", "kitten", "bear", "bird", "squirrel", "raccoon", "animal",
    "wildlife", "funny", "fail", "unexpected", "surprise", "trick", "skill", "catch",
    "jump", "dance", "skate", "parkour", "rescue", "monkey", "fox", "deer", "owl",
    "penguin", "whale", "dolphin", "octopus", "goat", "cow", "horse", "rabbit", "parrot",
    "hilarious", "cute", "adorable", "incredible", "amazing", "smart", "clever",
)


def safety_gate(text):
    """Return (allowed, blocked_term, positive_score)."""
    low = (text or "").lower()
    for b in BLOCK_TERMS:
        if b in low:
            return False, b, 0
    score = sum(1 for g in GOOD_TERMS if g in low)
    return True, None, score

ALLOWED_LICENSES = {"cc0", "public domain", "pd", "cc by 3.0", "cc by 4.0",
                    "cc-by-3.0", "cc-by-4.0", "public domain mark 1.0", "pd-usgov"}
BAD_LICENSE_TOKENS = ("by-sa", "by-nc", "sa 3.0", "sa 4.0", "fair use",
                      "license review needed", "review needed (video)", "all rights reserved")
VIDEO_EXT = (".webm", ".ogv", ".ogg", ".mp4", ".mov")
VIDEO_MIME = ("video/webm", "application/ogg", "video/ogg", "video/mp4",
              "video/quicktime", "video/x-matroska")

# The exact ten V7 candidates + the excluded NASA V10 / Short asset.
EXCLUDE_TOKENS = [
    "how to drop in at your local pro shop", "chicago parallel parking fail",
    "floridian cop caught on camera running from a rat",
    "floridian policeman caught on camera running from a rat",
    "funny hang-5", "funny fight - jc vs mark webb",
    "bear enters californian home", "eagan police catch man reading novel",
    "30, caption fail", "amazon delivery driver throws parcel",
    "quaker corn bran", "artemis", "water bubble", "nasa ",
]


def log(*a):
    print(*a, flush=True)


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def api(params, tries=4):
    for i in range(tries):
        try:
            r = S.get(API, params=params, timeout=40)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            log("  api retry", i + 1, type(e).__name__)
            time.sleep(2 + 2 * i)
    return {}


def search(q):
    d = api({"action": "query", "format": "json", "formatversion": "2",
             "generator": "search", "gsrsearch": q, "gsrnamespace": 6,
             "gsrlimit": 50, "prop": "imageinfo",
             "iiprop": "url|size|mime|sha1|extmetadata|mediatype"})
    return d.get("query", {}).get("pages", []) or []


def clean_meta(m):
    def v(k):
        x = m.get(k, {})
        return (x.get("value") if isinstance(x, dict) else "") or ""
    return {
        "license_short_name": v("LicenseShortName"),
        "license_id": v("License"),
        "license_url": v("LicenseUrl"),
        "usage_terms": v("UsageTerms"),
        "artist": re.sub(r"<[^>]*>", "", v("Artist")).strip(),
        "credit": re.sub(r"<[^>]*>", "", v("Credit")).strip(),
        "attribution_required": v("AttributionRequired").lower() in ("true", "1", "yes"),
        "description": re.sub(r"<[^>]*>", "", v("ImageDescription")).strip()[:1200],
        "categories": v("Categories"),
        "copyrighted": v("Copyrighted"),
        "restrictions": v("Restrictions"),
        "permission_excerpt": re.sub(r"<[^>]*>", "", v("Permission")).strip()[:600],
    }


def acceptable(page, meta):
    title = page.get("title", "")
    low = title.lower()
    if not low.endswith(VIDEO_EXT):
        return False
    if any(t in low for t in EXCLUDE_TOKENS):
        return False
    # Content-safety gate over title + description + categories, not just the filename.
    blob = " ".join([title, meta.get("description", ""), meta.get("categories", ""),
                     meta.get("credit", "")])
    ok, blocked, _ = safety_gate(blob)
    if not ok:
        return False
    lic = (meta["license_short_name"] or meta["license_id"]).strip().lower()
    if lic and lic not in ALLOWED_LICENSES and not any(x in lic for x in ("public domain", "cc0", "cc by 3.0", "cc by 4.0")):
        # accept explicit PD/CC0/CC-BY variants, reject everything else
        if not any(x in lic for x in ("public domain", "cc0", "cc by 3.0", "cc by 4.0", "cc-by-3.0", "cc-by-4.0")):
            return False
    blob = (lic + " " + meta["permission_excerpt"] + " " + meta["usage_terms"]).lower()
    if any(b in blob for b in BAD_LICENSE_TOKENS):
        return False
    if not meta["license_short_name"] and not meta["license_id"]:
        return False
    return True


def derivatives(title):
    d = api({"action": "query", "format": "json", "formatversion": "2",
             "prop": "videoinfo", "titles": title, "viprop": "url|derivatives|size|mime"})
    pages = d.get("query", {}).get("pages", []) or []
    if not pages:
        return []
    vi = (pages[0].get("videoinfo") or [{}])[0]
    out = []
    for x in vi.get("derivatives", []) or []:
        src = x.get("src", "")
        if src.startswith("//"):
            src = "https:" + src
        if not src.startswith("https://"):
            continue
        out.append({"src": src, "type": x.get("type", ""),
                    "width": x.get("width", 0), "height": x.get("height", 0),
                    "key": x.get("transcodekey", "")})
    return out


def download(url, dest, cap_mb=90):
    try:
        with S.get(url, stream=True, timeout=180) as r:
            r.raise_for_status()
            n = 0
            with open(dest, "wb") as f:
                for c in r.iter_content(1 << 20):
                    if not c:
                        continue
                    f.write(c)
                    n += len(c)
                    if n > cap_mb * (1 << 20):
                        return False
        return dest.exists() and dest.stat().st_size > 20000
    except Exception as e:
        log("  download failed", type(e).__name__, str(e)[:140])
        return False


def probe_duration(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        return 0.0
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def hook_start(path, dur):
    """Objective 'best scene' picker: 4 fps luma motion + single-frame surprise peak."""
    try:
        r = subprocess.run(
            [FF, "-v", "error", "-i", str(path), "-vf",
             f"fps={SAMPLE_FPS},scale=160:90,format=gray", "-an",
             "-f", "rawvideo", "-"], capture_output=True, timeout=180)
        raw = r.stdout
        frames = len(raw) // (160 * 90)
        if frames < 12:
            return 0.0, {"status": "too_few_frames", "frames": frames}
        a = np.frombuffer(raw[:frames * 160 * 90], dtype=np.uint8).reshape(frames, 90, 160)
        d = np.abs(a[1:].astype(np.int16) - a[:-1].astype(np.int16)).mean(axis=(1, 2)).astype(float)
        w = max(4, int(WINDOW_S * SAMPLE_FPS))
        best, bi = -1.0, 0
        for i in range(0, max(1, len(d) - w)):
            seg = d[i:i + w]
            score = float(seg.mean()) + 0.55 * float(seg.max())
            if score > best:
                best, bi = score, i
        start = max(0.0, bi / SAMPLE_FPS)
        return start, {"status": "ok", "frames_scored": int(frames),
                       "window_frames": w, "motion_mean": round(float(d.mean()), 3),
                       "window_score": round(best, 3), "start_s": round(start, 2)}
    except Exception as e:
        return 0.0, {"status": "scoring_failed", "detail": type(e).__name__}


def encode_window(src, start, dest):
    vf = ("scale=960:540:force_original_aspect_ratio=decrease,"
          "pad=960:540:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30,format=yuv420p")
    cmd = [FF, "-y", "-v", "error", "-ss", f"{start:.3f}", "-t", str(WINDOW_S),
           "-i", str(src), "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "21", "-pix_fmt", "yuv420p", "-r", "30", "-g", "60",
           "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
           "-t", str(WINDOW_S), "-movflags", "+faststart", str(dest)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and dest.exists() and dest.stat().st_size > 10000


def frame(path, out):
    subprocess.run([FF, "-y", "-v", "error", "-ss", "2", "-i", str(path),
                    "-frames:v", "1", "-update", "1", str(out)], capture_output=True)


def contact_sheet(items):
    tw, th, cols = 320, 180, 4
    rows = (len(items) + cols - 1) // cols
    im = Image.new("RGB", (tw * cols, (th + 26) * rows), (10, 16, 26))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except Exception:
        f = ImageFont.load_default()
    for i, it in enumerate(items):
        p = REVIEW / f"hook_{it['id']:02d}.jpg"
        if not p.exists():
            continue
        tile = Image.open(p).convert("RGB").resize((tw, th))
        x, y = (i % cols) * tw, (i // cols) * (th + 26)
        im.paste(tile, (x, y))
        label = f"{it['id']:02d} {it['title'][:34]}"
        d.text((x + 5, y + th + 5), label, font=f, fill=(91, 214, 208))
    im.save(REVIEW / "contact_sheet_v13.jpg", quality=88)


def main():
    # Never leak stale windows from a rejected pass into a new deliverable.
    for p in list(WINDOWS.glob("hook_*.mp4")) + list(REVIEW.glob("hook_*.jpg")):
        p.unlink(missing_ok=True)
    pool, seen, rejected_safety = [], set(), 0
    for q in QUERIES:
        pages = search(q)
        log(f"search {q!r}: {len(pages)} hits")
        for pg in pages:
            title = pg.get("title", "")
            if title in seen:
                continue
            seen.add(title)
            ii = (pg.get("imageinfo") or [{}])[0]
            if not ii:
                continue
            meta = clean_meta(ii.get("extmetadata") or {})
            if not acceptable(pg, meta):
                rejected_safety += 1
                continue
            mime = ii.get("mime", "")
            if mime and not any(m in mime for m in VIDEO_MIME) and not title.lower().endswith(VIDEO_EXT):
                continue
            dur = float(ii.get("duration") or 0)
            if dur and not (WINDOW_S + 0.5 <= dur <= 240.0):
                continue
            _, _, prio = safety_gate(" ".join([title, meta["description"], meta["categories"]]))
            pool.append({"title": title, "pageid": pg.get("pageid"),
                         "url": ii.get("url", ""), "size": ii.get("size", 0),
                         "mime": mime, "width": ii.get("width"), "height": ii.get("height"),
                         "duration": dur, "commons_sha1": ii.get("sha1", ""),
                         "descriptionurl": ii.get("descriptionurl", ""), "meta": meta,
                         "priority": prio, "query": q})
        time.sleep(0.4)
    log(f"acceptable candidate pool: {len(pool)} (safety/licence rejected: {rejected_safety})")
    save_json(REVIEW / "candidate_pool_v13.json", {"count": len(pool), "candidates": pool,
              "rejected_by_safety_or_licence": rejected_safety})

    # Prefer explicitly on-brand / hooky titles first, then small files.
    pool.sort(key=lambda x: (-x["priority"], x["size"] or 1 << 30))
    accepted, failures = [], []
    for cand in pool:
        if len(accepted) >= MAX_CLIPS:
            break
        cid = len(accepted) + 1
        raw = WORK / f"raw_{cid:02d}.media"
        urls = [cand["url"]]
        if (cand["size"] or 0) > 30 * (1 << 20):
            urls = [d["src"] for d in derivatives(cand["title"])
                    if 360 <= d.get("width", 0) <= 720] + urls
        ok = False
        used = None
        for u in urls[:4]:
            if not u.startswith("https://"):
                continue
            if download(u, raw):
                ok, used = True, u
                break
        if not ok:
            failures.append({"title": cand["title"], "reason": "download_failed"})
            continue
        dur = probe_duration(raw) or cand["duration"] or 0.0
        if dur < WINDOW_S + 0.5:
            failures.append({"title": cand["title"], "reason": "clip_too_short_for_10s_window",
                             "duration_s": round(dur, 2)})
            raw.unlink(missing_ok=True)
            continue
        st = max(0.0, dur - WINDOW_S - 0.2)   # allow the best scene ANYWHERE in the clip
        start, score = hook_start(raw, dur)
        start = min(start, st)
        win = WINDOWS / f"hook_{cid:02d}.mp4"
        if not encode_window(raw, start, win):
            failures.append({"title": cand["title"], "reason": "encode_failed"})
            raw.unlink(missing_ok=True)
            continue
        frame(win, REVIEW / f"hook_{cid:02d}.jpg")
        rec = {
            "id": cid, "title": cand["title"].replace("File:", ""),
            "commons_page": cand["descriptionurl"], "commons_pageid": cand["pageid"],
            "license": cand["meta"]["license_short_name"],
            "license_id": cand["meta"]["license_id"],
            "license_url": cand["meta"]["license_url"],
            "usage_terms": cand["meta"]["usage_terms"],
            "artist": cand["meta"]["artist"], "credit": cand["meta"]["credit"],
            "attribution_required": cand["meta"]["attribution_required"],
            "categories": cand["meta"]["categories"][:600],
            "copyrighted": cand["meta"]["copyrighted"],
            "restrictions": cand["meta"]["restrictions"][:300],
            "origin_query": cand["query"],
            "commons_sha1": cand["commons_sha1"],
            "download_url": used,
            "source_duration_s": round(dur, 2),
            "source_bytes": cand["size"], "source_mime": cand["mime"],
            "window": {"start_s": round(start, 2), "duration_s": WINDOW_S,
                       "end_s": round(start + WINDOW_S, 2), "score": score},
            "local_window_file": f"windows/hook_{cid:02d}.mp4",
            "local_window_sha256": sha256(win),
            "local_window_bytes": win.stat().st_size,
            "native_audio_kept": True, "audio_added": False,
            "content_safety": {"keyword_gate": "passed", "positive_score": cand["priority"],
                               "blocked_terms": list(BLOCK_TERMS),
                               "human_watch_through_required": True,
                               "family_safe_claim": False},
            "human_legal_review": False, "not_a_legal_opinion": True,
        }
        accepted.append(rec)
        log(f"  [{cid:02d}] {rec['title'][:64]} | {rec['license']} | window {start:.1f}s | {rec['local_window_bytes']} B")
        raw.unlink(missing_ok=True)  # only the small hook window is committed

    contact_sheet(accepted)
    ledger = {
        "project": "Caught on Camera V13 - NEW clip acquisition",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "Live Commons API namespace-6 search; extmetadata licence gate; objective motion/surprise hook-window scoring; native audio kept; 10 s normalized MP4 windows committed.",
        "queries": QUERIES,
        "candidate_pool_size": len(pool),
        "rejected_by_safety_or_licence": rejected_safety,
        "content_safety_gate": {
            "hard_blocked_terms": list(BLOCK_TERMS),
            "positive_terms": list(GOOD_TERMS),
            "reason": ("First pass returned murder CCTV, suicide bombing, missile strikes, "
                       "plane crashes and robberies. Rejected. This pass gates title + "
                       "description + categories against violence/crime/war/disaster terms "
                       "and ranks animal/funny/surprising/skill titles first."),
            "human_watch_through_required": True,
            "family_safe_guarantee": False,
        },
        "accepted_count": len(accepted),
        "failed_count": len(failures),
        "failures": failures,
        "excluded": {"v7_ten_candidates": True, "nasa_artemis_v10_short": True,
                     "licences": BAD_LICENSE_TOKENS},
        "boundary": ("Commons file pages recording a YouTube / Vimeo / SWNS / police or "
                     "security-camera origin are the rights-cleared mirror. No unverified "
                     "TikTok/Instagram/Reddit/Twitter/Dailymotion repost was downloaded. "
                     "No current-trending claim, no legal opinion, no human legal review, "
                     "no upload/publish/monetisation, no virality or perfection claim."),
        "assets": accepted,
    }
    save_json(BASE / "rights_ledger_v13.json", ledger)
    save_json(BASE / "hook_windows_v13.json", {"count": len(accepted),
              "windows": [{"id": a["id"], "title": a["title"], **a["window"],
                           "file": a["local_window_file"]} for a in accepted]})
    log(f"DONE accepted={len(accepted)} failed={len(failures)}")
    if not accepted:
        sys.exit(2)


if __name__ == "__main__":
    main()
