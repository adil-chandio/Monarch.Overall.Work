#!/usr/bin/env python3
"""Hard QC gate for V13 clip acquisition. Fails the build on ANY unsafe or unverified clip."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research" / "caught_on_camera_v13"
from acquire_clips_v13 import BLOCK_TERMS, EXCLUDE_TOKENS, ALLOWED_LICENSES  # noqa: E402

bad = []
led = json.loads((BASE / "rights_ledger_v13.json").read_text())
assets = led["assets"]
hw = json.loads((BASE / "hook_windows_v13.json").read_text())

if len(assets) < 12:
    bad.append(f"too_few_safe_clips: {len(assets)} < 12")
if len({a["commons_page"] for a in assets}) != len(assets):
    bad.append("duplicate_commons_page")
if len({a["title"] for a in assets}) != len(assets):
    bad.append("duplicate_title")

for a in assets:
    t = a["title"]
    blob = " ".join([t, a.get("categories", ""), a.get("usage_terms", "")]).lower()
    for b in BLOCK_TERMS:
        if b in blob:
            bad.append(f"unsafe_term[{b}] in {t[:50]}")
            break
    for e in EXCLUDE_TOKENS:
        if e in t.lower():
            bad.append(f"excluded_asset[{e}] {t[:50]}")
            break
    lic = (a.get("license") or "").lower()
    if not any(x in lic for x in ("public domain", "cc0", "cc by 3.0", "cc by 4.0", "cc-by-3.0", "cc-by-4.0")):
        bad.append(f"licence_not_cleared: {t[:40]} = {a.get('license')}")
    if not a.get("commons_page", "").startswith("https://commons.wikimedia.org/"):
        bad.append(f"bad_source_page {t[:40]}")
    if not a.get("commons_sha1"):
        bad.append(f"no_commons_sha1 {t[:40]}")
    p = BASE / a["local_window_file"]
    if not p.exists():
        bad.append(f"missing_window {a['local_window_file']}")
        continue
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    if h.hexdigest() != a["local_window_sha256"]:
        bad.append(f"sha256_mismatch {p.name}")
    # probe the actual window: duration, video + audio stream
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type", "-of", "json", str(p)],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        dur = float(d["format"]["duration"])
        kinds = {s["codec_type"] for s in d["streams"]}
        if not (9.4 <= dur <= 10.6):
            bad.append(f"window_duration_{dur:.2f}s {p.name}")
        if "video" not in kinds:
            bad.append(f"no_video_stream {p.name}")
        if "audio" not in kinds:
            bad.append(f"no_native_audio_stream {p.name}")
    except Exception as e:
        bad.append(f"ffprobe_failed {p.name}: {type(e).__name__}")

if len(hw["windows"]) != len(assets):
    bad.append("hook_windows_count_mismatch")

out = {
    "generated_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
    "clips_checked": len(assets),
    "blocked_terms": list(BLOCK_TERMS),
    "violations": bad,
    "status": "ALL_PASS" if not bad else "FAIL",
    "human_watch_through_required": True,
    "family_safe_guarantee": False,
    "not_a_legal_opinion": True,
}
(BASE / "review" / "validation_v13.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": out["status"], "clips": len(assets), "violations": bad[:20]}, indent=2))
sys.exit(0 if not bad else 1)
