#!/usr/bin/env python3
"""Hard QC gate for the final V13 20-clip selection.

Fails the build on ANY unsafe term, excluded NASA asset, unclear licence, missing
window, SHA-256 mismatch, bad duration, or missing video stream. A silent source is
NOT a failure: `acquire_curated_v13.py` adds a silent AAC track and the builder keeps
the native audio ducked under the English VO. No audio stream is recorded as a
silent source that still requires human watch-through.
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
from clip_safety_v13 import BLOCK_TERMS, EXCLUDE_TOKENS, ALLOWED_LICENSES  # noqa: E402

bad, silent_sources = [], []
selection = json.loads((BASE / "selected_windows_v13.json").read_text(encoding="utf-8"))
clips = selection["clips"]
ledgers = {}
for name in ("rights_ledger_v13.json", "rights_ledger_curated_v13.json"):
    d = json.loads((BASE / name).read_text(encoding="utf-8"))
    for a in d["assets"]:
        ledgers[(name, a["local_window_file"])] = a

if len(clips) != 20:
    bad.append(f"selection_count_{len(clips)}_not_20")
if len({c["window_file"] for c in clips}) != len(clips):
    bad.append("duplicate_window_file")
if len({c["id"] for c in clips}) != len(clips):
    bad.append("duplicate_clip_id")

for c in clips:
    key = (c["ledger"], c["window_file"])
    a = ledgers.get(key)
    if not a:
        bad.append(f"no_ledger_entry {c['id']} {c['window_file']}")
        continue
    blob = " ".join([a.get("title", ""), a.get("categories", ""),
                     a.get("usage_terms", ""), a.get("credit", "")]).lower()
    for b in BLOCK_TERMS:
        if b in blob:
            bad.append(f"unsafe_term[{b}] in {a['title'][:50]}")
            break
    for e in EXCLUDE_TOKENS:
        if e in a.get("title", "").lower():
            bad.append(f"excluded_asset[{e}] {a['title'][:50]}")
            break
    lic = (a.get("license") or "").lower()
    if not any(x in lic for x in ("public domain", "cc0", "cc by 3.0", "cc by 4.0",
                                 "cc-by-3.0", "cc-by-4.0", "pd")):
        bad.append(f"licence_not_cleared: {a['title'][:40]} = {a.get('license')}")
    if not a.get("commons_page", "").startswith("https://commons.wikimedia.org/"):
        bad.append(f"bad_source_page {a['title'][:40]}")
    if not a.get("commons_sha1"):
        bad.append(f"no_commons_sha1 {a['title'][:40]}")
    p = BASE / c["window_file"]
    if not p.exists():
        bad.append(f"missing_window {c['window_file']}")
        continue
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    if h.hexdigest() != a["local_window_sha256"]:
        bad.append(f"sha256_mismatch {p.name}")
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
            silent_sources.append({"id": c["id"], "file": c["window_file"],
                                   "action": "silent_AAC_track_added_or_required"})
        else:
            silent_sources.append({"id": c["id"], "file": c["window_file"],
                                   "action": "none_native_audio_present"})
    except Exception as e:
        bad.append(f"ffprobe_failed {p.name}: {type(e).__name__}")

out = {
    "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "selection_version": selection["selection_version"],
    "clips_checked": len(clips),
    "ledgers": ["rights_ledger_v13.json", "rights_ledger_curated_v13.json"],
    "blocked_terms": list(BLOCK_TERMS),
    "excluded_assets": list(EXCLUDE_TOKENS),
    "silent_or_audio_status": silent_sources,
    "violations": bad,
    "status": "ALL_PASS" if not bad else "FAIL",
    "human_watch_through_required": True,
    "family_safe_guarantee": False,
    "not_a_legal_opinion": True,
    "technical_qc_is_not_creative_approval": True,
}
(BASE / "review" / "validation_v13.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": out["status"], "clips": len(clips),
                  "violations": bad[:30]}, indent=2))
sys.exit(0 if not bad else 1)
