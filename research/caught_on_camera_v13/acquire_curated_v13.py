#!/usr/bin/env python3
"""V13 curated recovery pass: ten rights-cleared V7 social-origin Commons clips.

The positive-only V13 Commons pass produced safe but low-energy footage (landscape
repeats, microscopy, interviews). This pass uses an explicit, human-readable list of
original Commons file pages with YouTube / Vimeo / SWNS / police / social-video origin
that V12 ignored. It applies the SAME hard content-safety and licence gate, downloads
in the Actions runner, selects an objective 10-second motion/surprise window, normalizes
to 960x540 / 30 fps / H.264 / AAC, keeps native audio where present, adds a silent AAC
track where the source is silent, and deletes raw originals. It does NOT use the
rejected V12 eight archived finals or the NASA V10 / Short.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research" / "caught_on_camera_v13"
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(ROOT))

import acquire_clips_v13 as acq  # noqa: E402
import clip_safety_v13 as safe  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

CURATED = BASE / "curated_titles_v13.json"
WORK = ROOT / "production" / "monarch-cam" / "work" / "caught_on_camera_curated_v13"
WINDOWS = BASE / "windows"
REVIEW = BASE / "review"
for p in (WORK, WINDOWS, REVIEW):
    p.mkdir(parents=True, exist_ok=True)

FF = acq.FF
WINDOW_S = acq.WINDOW_S


def log(*a):
    print(*a, flush=True)


def get_page(title):
    d = acq.api({"action": "query", "format": "json", "formatversion": "2",
                 "titles": title, "prop": "imageinfo",
                 "iiprop": "url|size|mime|sha1|extmetadata|mediatype"})
    pages = d.get("query", {}).get("pages", []) or []
    if not pages:
        return None
    pg = pages[0]
    if pg.get("missing") is not None or "imageinfo" not in pg:
        return None
    return pg


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
    spec = json.loads(CURATED.read_text(encoding="utf-8"))
    titles = spec["titles"]
    accepted, failures = [], []

    for n, item in enumerate(titles, 1):
        title, short, origin = item["title"], item["short"], item["origin"]
        log(f"[{n:02d}] {short}  <- {title}")
        pg = get_page(title)
        if not pg:
            failures.append({"title": title, "reason": "commons_page_missing"})
            continue
        ii = (pg.get("imageinfo") or [{}])[0]
        meta = acq.clean_meta(ii.get("extmetadata") or {})
        blob = " ".join([title, meta["description"], meta["categories"], meta["credit"]])
        ok, blocked, prio = safe.safety_gate(blob)
        if not ok:
            failures.append({"title": title, "reason": "content_safety", "term": blocked})
            continue
        lic = (meta["license_short_name"] or meta["license_id"]).strip().lower()
        good_lic = (lic in safe.ALLOWED_LICENSES or
                    any(x in lic for x in ("public domain", "cc0", "cc by 3.0",
                                          "cc by 4.0", "cc-by-3.0", "cc-by-4.0")))
        licence_blob = (lic + " " + meta["permission_excerpt"] + " " +
                        meta["usage_terms"]).lower()
        if not good_lic or any(b in licence_blob for b in acq.BAD_LICENSE_TOKENS):
            failures.append({"title": title, "reason": "licence_not_cleared", "licence": lic})
            continue
        dur = float(ii.get("duration") or 0)
        if dur and dur < WINDOW_S + 0.5:
            failures.append({"title": title, "reason": "too_short", "duration_s": dur})
            continue

        raw = WORK / f"curated_raw_{n:02d}.media"
        urls = [ii.get("url", "")]
        if (ii.get("size") or 0) > 30 * (1 << 20):
            urls = [d["src"] for d in acq.derivatives(title)
                    if 360 <= d.get("width", 0) <= 720] + urls
        used, ok_dl = None, False
        for u in urls[:4]:
            if u.startswith("https://") and acq.download(u, raw, cap_mb=120):
                used, ok_dl = True, u
                break
        if not ok_dl:
            failures.append({"title": title, "reason": "download_failed"})
            continue
        real_dur = acq.probe_duration(raw) or dur
        if real_dur < WINDOW_S + 0.5:
            failures.append({"title": title, "reason": "probe_too_short",
                             "duration_s": real_dur})
            raw.unlink(missing_ok=True)
            continue
        start, score = acq.hook_start(raw, real_dur)
        start = max(0.0, min(start, real_dur - WINDOW_S - 0.2))
        native = has_audio(raw)
        out = WINDOWS / f"curated_{n:02d}.mp4"
        if not encode_window(raw, start, out, native):
            failures.append({"title": title, "reason": "encode_failed"})
            raw.unlink(missing_ok=True)
            continue
        acq.frame(out, REVIEW / f"curated_{n:02d}.jpg")
        entry = {
            "id": n, "title": title, "short": short, "origin_query": origin,
            "commons_page": ii.get("descriptionurl", ""),
            "commons_pageid": pg.get("pageid"),
            "license": meta["license_short_name"] or meta["license_id"],
            "license_id": meta["license_id"],
            "license_url": meta["license_url"],
            "usage_terms": meta["usage_terms"],
            "artist": meta["artist"], "credit": meta["credit"],
            "attribution_required": meta["attribution_required"],
            "categories": meta["categories"][:600],
            "copyrighted": meta["copyrighted"], "restrictions": meta["restrictions"],
            "commons_sha1": ii.get("sha1", ""), "download_url": used,
            "source_duration_s": round(real_dur, 3),
            "source_bytes": ii.get("size", 0), "source_mime": ii.get("mime", ""),
            "window": {"start_s": round(start, 3), "end_s": round(start + WINDOW_S, 3),
                       "duration_s": WINDOW_S, "score": score},
            "local_window_file": f"windows/curated_{n:02d}.mp4",
            "local_window_sha256": acq.sha256(out),
            "local_window_bytes": out.stat().st_size,
            "native_audio_kept": native,
            "audio_added": (not native),
            "content_safety": {"keyword_gate": "passed", "positive_score": prio,
                               "human_watch_through_required": True,
                               "family_safe_claim": False},
            "human_legal_review": False, "not_a_legal_opinion": True,
        }
        accepted.append(entry)
        raw.unlink(missing_ok=True)
        time.sleep(0.3)

    acq.save_json(BASE / "rights_ledger_curated_v13.json", {
        "project": "Monarch Cam V13 curated recovery pool",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "Live Commons API by exact file title + extmetadata licence gate + objective 10s hook window.",
        "note": spec["note"],
        "curated_count": len(titles),
        "accepted_count": len(accepted),
        "failed_count": len(failures),
        "failures": failures,
        "content_safety_gate": {"hard_blocked_terms": list(safe.BLOCK_TERMS),
                                "human_watch_through_required": True,
                                "family_safe_guarantee": False},
        "boundary": ("Not the rejected V12 eight archived finals, not NASA V10 / Short, "
                     "not unverified social-platform reposts. No legal opinion, no "
                     "monetisation claim, no upload/publish, no human approval."),
        "assets": accepted,
    })
    acq.save_json(BASE / "hook_windows_curated_v13.json", {
        "count": len(accepted),
        "windows": [{"id": a["id"], "title": a["title"], "short": a["short"],
                     "window": a["window"], "file": a["local_window_file"]}
                    for a in accepted],
    })
    contact([{"id": a["id"], "short": a["short"]} for a in accepted])
    log(f"accepted={len(accepted)} failed={len(failures)}")
    if len(accepted) < 10:
        log("FAILURES", json.dumps(failures, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
