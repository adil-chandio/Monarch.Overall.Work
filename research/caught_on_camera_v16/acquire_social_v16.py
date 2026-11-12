#!/usr/bin/env python3
"""V16 social viral acquisition: 20 NEW YouTube/TikTok/Dailymotion clips via yt-dlp.

NOT V14 Commons repeats. Downloads viral caught-on-camera funny/shocking moments
from social platforms in the Actions runner (full outbound network), applies the
SAME hard content-safety gate (blocks graphic/tragic: crash, disaster, blood, gore,
dead, etc.), picks objective 10s hook windows (motion + surprise), normalizes to
960x540/30fps/H.264/AAC, keeps native audio, writes social rights ledger with
source URL + platform + "licence unknown, human review required" (NO clearance claim).

No legal opinion, no monetisation claim, no upload/publish, no human approval.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE13 = ROOT / "research" / "caught_on_camera_v13"
BASE16 = ROOT / "research" / "caught_on_camera_v16"
sys.path.insert(0, str(BASE13))
sys.path.insert(0, str(ROOT))

import acquire_clips_v13 as acq  # noqa: E402
import clip_safety_v13 as safe  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

URLS = BASE16 / "social_urls_v16.json"
WORK = ROOT / "production" / "monarch-cam" / "work" / "caught_on_camera_social_v16"
WINDOWS = BASE13 / "windows"
REVIEW = BASE13 / "review"
for p in (WORK, WINDOWS, REVIEW):
    p.mkdir(parents=True, exist_ok=True)

FF = acq.FF
WINDOW_S = acq.WINDOW_S


def log(*a):
    print(*a, flush=True)


def has_audio(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    return "Audio:" in r.stderr


def encode_window(src, start, dest, native_audio):
    vf = ("scale=1152:648:force_original_aspect_ratio=decrease,"
          "pad=1152:648:(ow-iw)/2:(oh-ih)/2:black,setsar=1,"
          "crop=960:540:96:54,fps=30,format=yuv420p")
    common = [FF, "-y", "-v", "error", "-ss", f"{start:.3f}", "-t", str(WINDOW_S),
              "-i", str(src)]
    tail = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt",
            "yuv420p", "-r", "30", "-g", "60", "-c:a", "aac", "-b:a", "128k",
            "-ar", "48000", "-ac", "2", "-t", str(WINDOW_S), "-movflags",
            "+faststart", str(dest)]
    if native_audio:
        fc = ("[0:v]" + vf + ",setpts=PTS-STARTPTS[v];"
              "[0:a]atrim=0:" + str(WINDOW_S) + ",asetpts=PTS-STARTPTS,"
              "aresample=48000,aformat=channel_layouts=stereo[a]")
        cmd = common + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]"] + tail
    else:
        fc = ("[0:v]" + vf + ",setpts=PTS-STARTPTS[v];"
              "[1:a]atrim=0:" + str(WINDOW_S) + ",asetpts=PTS-STARTPTS[a]")
        cmd = common + ["-f", "lavfi", "-t", str(WINDOW_S), "-i",
                        "anullsrc=channel_layout=stereo:sample_rate=48000",
                        "-filter_complex", fc, "-map", "[v]", "-map", "[a]"] + tail
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log("  encode failed", r.stderr[-300:])
    return r.returncode == 0 and dest.exists() and dest.stat().st_size > 10000


def contact(items):
    tw, th, cols = 320, 180, 4
    rows = (len(items) + cols - 1) // cols
    im = Image.new("RGB", (tw * cols, (th + 26) * rows), (10, 16, 26))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except Exception:
        f = ImageFont.load_default()
    for i, it in enumerate(items):
        p = REVIEW / f"curated_{it['id']:02d}.jpg"
        if not p.exists():
            continue
        tile = Image.open(p).convert("RGB").resize((tw, th))
        x, y = (i % cols) * tw, (i // cols) * (th + 26)
        im.paste(tile, (x, y))
        d.text((x + 5, y + th + 5), f"{it['id']:02d} {it['short'][:34]}",
               font=f, fill=(91, 214, 208))
    out = REVIEW / "curated_contact_sheet_v13.jpg"
    im.save(out, quality=88)
    log("contact sheet", out)


def main():
    spec = json.loads(URLS.read_text(encoding="utf-8"))
    urls = spec["urls"]
    accepted, failures = [], []
    for p in list(WINDOWS.glob("curated_*.mp4")) + list(REVIEW.glob("curated_*.jpg")):
        p.unlink(missing_ok=True)

    for n, item in enumerate(urls, 1):
        url, short, platform = item["url"], item["short"], item["platform"]
        log(f"[{n:02d}] {short} <- {url}")
        # Safety gate over URL + short (title/description checked after download via yt-dlp info)
        blob = f"{url} {short}"
        ok, blocked, prio = safe.safety_gate(blob)
        if not ok:
            failures.append({"url": url, "reason": "content_safety", "term": blocked})
            continue
        raw = WORK / f"social_raw_{n:02d}.media"
        # yt-dlp download: best 720p, mp4, no playlist
        cmd = ["yt-dlp", "--no-playlist", "-f",
               "bv*[height<=720]+ba/b[height<=720]/b",
               "--merge-output-format", "mp4", "-o", str(raw), url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if r.returncode != 0 or not raw.exists():
            # try fallback: any format
            r2 = subprocess.run(["yt-dlp", "--no-playlist", "-f", "b",
                                 "--merge-output-format", "mp4", "-o", str(raw), url],
                                capture_output=True, text=True, timeout=300)
            if r2.returncode != 0 or not raw.exists():
                failures.append({"url": url, "reason": "download_failed",
                                 "detail": (r.stderr or "")[-200:]})
                continue
        # Get title/description via yt-dlp info for safety gate
        info = subprocess.run(["yt-dlp", "--no-playlist", "--print",
                               "%(title)s | %(description)s", url],
                              capture_output=True, text=True, timeout=120)
        info_text = (info.stdout or "")[:2000]
        ok2, blocked2, _ = safe.safety_gate(info_text + " " + short)
        if not ok2:
            failures.append({"url": url, "reason": "content_safety_info", "term": blocked2})
            raw.unlink(missing_ok=True)
            continue
        real_dur = acq.probe_duration(raw) or 0
        if real_dur < WINDOW_S + 0.5:
            failures.append({"url": url, "reason": "probe_too_short", "duration_s": real_dur})
            raw.unlink(missing_ok=True)
            continue
        start, score = acq.hook_start(raw, real_dur)
        start = min(start, max(0.0, real_dur - 12.0))
        start = max(0.0, min(start, real_dur - WINDOW_S - 0.2))
        native = has_audio(raw)
        out = WINDOWS / f"curated_{n:02d}.mp4"
        if not encode_window(raw, start, out, native):
            failures.append({"url": url, "reason": "encode_failed"})
            raw.unlink(missing_ok=True)
            continue
        acq.frame(out, REVIEW / f"curated_{n:02d}.jpg")
        entry = {
            "id": n, "title": f"Social: {short}", "short": short,
            "origin_query": f"{platform} viral",
            "commons_page": url, "commons_pageid": 0,
            "license": "unknown - human review required",
            "license_id": "unknown", "license_url": "",
            "usage_terms": "Third-party social clip. Licence unknown. Human legal review required. No clearance claimed.",
            "artist": platform, "credit": url,
            "attribution_required": False,
            "categories": f"Social viral|{platform}",
            "copyrighted": "True", "restrictions": "",
            "commons_sha1": "", "download_url": url,
            "source_duration_s": round(real_dur, 3),
            "source_bytes": raw.stat().st_size, "source_mime": "video/mp4",
            "window": {"start_s": round(start, 3), "end_s": round(start + WINDOW_S, 3),
                       "duration_s": WINDOW_S, "score": score},
            "local_window_file": f"windows/curated_{n:02d}.mp4",
            "local_window_sha256": acq.sha256(out),
            "local_window_bytes": out.stat().st_size,
            "native_audio_kept": native, "audio_added": (not native),
            "content_safety": {"keyword_gate": "passed", "positive_score": prio,
                               "human_watch_through_required": True,
                               "family_safe_claim": False},
            "human_legal_review": False, "not_a_legal_opinion": True,
            "platform": platform, "source_url": url,
        }
        accepted.append(entry)
        raw.unlink(missing_ok=True)
        time.sleep(0.3)

    ledger = {
        "project": "Monarch Cam V16 social viral pool",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "yt-dlp social download + safety gate + objective 10s hook window.",
        "note": "20 NEW social viral clips (YouTube/TikTok/Dailymotion). NOT V14 Commons repeats. Licence unknown, human review required.",
        "curated_count": len(urls), "accepted_count": len(accepted),
        "failed_count": len(failures), "failures": failures,
        "content_safety_gate": {"human_watch_through_required": True, "family_safe_guarantee": False},
        "boundary": "Third-party social clips. No legal opinion, no monetisation claim, no upload/publish, no human approval.",
        "assets": accepted,
    }
    (BASE13 / "rights_ledger_curated_v13.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (BASE13 / "hook_windows_curated_v13.json").write_text(
        json.dumps({"accepted": accepted, "failures": failures}, indent=2) + "\n", encoding="utf-8")
    sel = {"selection_version": "v16-social-20", "count": len(accepted),
           "note": "V16 20 NEW social viral clips.",
           "clips": [{"id": f"C{a['id']:02d}", "window_file": a["local_window_file"],
                      "ledger": "rights_ledger_curated_v13.json", "pool": "social_v16",
                      "short": a["short"]} for a in accepted]}
    (BASE13 / "selected_windows_v13.json").write_text(
        json.dumps(sel, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    contact(accepted)
    log(f"accepted {len(accepted)}/{len(urls)} failed {len(failures)}")


if __name__ == "__main__":
    main()
