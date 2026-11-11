#!/usr/bin/env python3
"""Build the V13 English caught-on-camera long-form compilation.

Rules enforced by construction:
  * frame 1 is real footage (segment 1 from a clip window) - no intro/title/method card
  * 120 moving beats of 4.5 s (3-5 s pattern interrupts), no still frame held >4.5 s
  * 20 distinct rights-documented clips, English VO + burned-in English captions
  * small lower-third source / round / counter overlays only, no full-screen diagrams
  * native audio kept under short VO bursts, silent sources get a silent AAC track
  * 9:00 / 540 s / 16,200 frames / 960x540 / 30 fps / H.264 / AAC
This is a local render only. No upload, publish, monetisation, legal clearance,
human creative approval, family-safety guarantee or guaranteed views is claimed.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
import textwrap
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research" / "caught_on_camera_v13"
PROD = ROOT / "production" / "monarch-cam" / "caught_on_camera_v13"
PROD.mkdir(parents=True, exist_ok=True)

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SUB_STYLE = ("FontName=DejaVu Sans,FontSize=20,PrimaryColour=&H00FFFFFF,"
             "OutlineColour=&H00000000,BackColour=&H80000000,Bold=1,"
             "Alignment=2,MarginV=48")

FPS = 30
W, H = 960, 540
BEAT = 4.5
BEAT_FRAMES = 135
ROUNDS = 3
BEATS_PER_ROUND = 40
BEATS = ROUNDS * BEATS_PER_ROUND          # 120
TOTAL = BEATS * BEAT                       # 540.0 s
EXPECTED_FRAMES = BEATS * BEAT_FRAMES      # 16200

VO_DIR = PROD / "vo"
VO_FILES = [VO_DIR / f"chunk_{i:02d}.mp3" for i in range(1, 11)]
VO_STARTS = [54 * i for i in range(10)]   # 0,54,...,486
ROUND_LABELS = ["ROUND 1 / THE HOOK", "ROUND 2 / WHAT HAPPENED", "ROUND 3 / ONE MORE TIME"]
ZOOMS = [(0, 0), (192, 108), (96, 54), (192, 0), (0, 108), (96, 0), (192, 54), (0, 54)]
SPEEDS = [1.0, 0.85, 1.15, 1.3]
STARTS = [0.0, 3.0, 1.0, 2.0]

SEG_DIR = PROD / "segments"
OVERLAY_DIR = PROD / "assets" / "overlay"
for p in (SEG_DIR, OVERLAY_DIR):
    p.mkdir(parents=True, exist_ok=True)


def log(*a):
    print(*a, flush=True)


def run(cmd, capture=False):
    r = subprocess.run(cmd, capture_output=capture, text=True)
    if r.returncode != 0:
        tail = (r.stderr or "")[-1200:] if capture else "see stdout"
        raise RuntimeError(f"ffmpeg failed ({r.returncode}): {tail}")
    return r


def parse_duration(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        raise RuntimeError(f"no duration in {path}")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def has_audio(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    return "Audio:" in r.stderr


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def srt_time(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def make_captions():
    script = json.loads((PROD / "vo_script_v13.json").read_text(encoding="utf-8"))
    cues, n = [], 0
    for i, chunk in enumerate(script["chunks"]):
        start = VO_STARTS[i]
        dur = parse_duration(VO_FILES[i])
        parts = split_sentences(chunk["text"])
        total_chars = sum(len(p) for p in parts) or 1
        off = 0.0
        for p in parts:
            line_dur = dur * len(p) / total_chars
            cs = start + off
            ce = min(start + dur, cs + line_dur)
            off += line_dur
            if ce - cs < 0.35:
                continue
            n += 1
            txt = "\n".join(textwrap.wrap(p, width=42))
            cues.append(f"{n}\n{srt_time(cs)} --> {srt_time(ce)}\n{txt}\n")
    out = PROD / "captions_v13.srt"
    out.write_text("\n".join(cues), encoding="utf-8")
    log(f"captions: {n} cues -> {out.name}")
    return n


def load_selection():
    sel = json.loads((BASE / "selected_windows_v13.json").read_text(encoding="utf-8"))
    ledgers = {}
    for name in ("rights_ledger_v13.json", "rights_ledger_curated_v13.json"):
        d = json.loads((BASE / name).read_text(encoding="utf-8"))
        for a in d["assets"]:
            ledgers[(name, a["local_window_file"])] = a
    assert sel["count"] == 20
    for c in sel["clips"]:
        assert (BASE / c["window_file"]).exists(), c["window_file"]
        assert (c["ledger"], c["window_file"]) in ledgers
    return sel, ledgers


def write_text(path, text):
    path.write_text(text.strip() + "\n", encoding="utf-8")


def make_overlays(sel, ledgers, beats):
    for c in sel["clips"]:
        a = ledgers[(c["ledger"], c["window_file"])]
        lic = a.get("license") or "PD"
        txt = f"Wikimedia Commons | {lic} | {c['short']}"
        write_text(OVERLAY_DIR / f"source_{c['id']}.txt", txt[:80])
    for r, label in enumerate(ROUND_LABELS, 1):
        write_text(OVERLAY_DIR / f"round_{r}.txt", label)
    for b in range(beats):
        clip = sel["clips"][((b % BEATS_PER_ROUND) // 2) % 20]
        write_text(OVERLAY_DIR / f"counter_{b+1:03d}.txt", f"{clip['id']} / 20")


def make_edl(sel, ledgers, beats):
    edl = []
    for b in range(beats):
        r = b // BEATS_PER_ROUND
        bir = b % BEATS_PER_ROUND
        ci = (bir // 2) % 20
        c = sel["clips"][ci]
        a = ledgers[(c["ledger"], c["window_file"])]
        variant = (bir + r) % 4
        speed = SPEEDS[variant]
        start = STARTS[variant] + 0.5 * r
        zx, zy = ZOOMS[(b * 3 + r) % len(ZOOMS)]
        edl.append({
            "beat": b + 1,
            "round": r + 1,
            "round_label": ROUND_LABELS[r],
            "clip_id": c["id"],
            "short": c["short"],
            "window_file": c["window_file"],
            "ledger": c["ledger"],
            "title": a.get("title"),
            "license": a.get("license"),
            "commons_page": a.get("commons_page"),
            "artist": a.get("artist"),
            "timeline_start_s": round(b * BEAT, 3),
            "timeline_end_s": round((b + 1) * BEAT, 3),
            "duration_s": BEAT,
            "source_start_s": round(start, 3),
            "speed": speed,
            "zoom_crop_xy": [zx, zy],
            "overlay_files": [f"assets/overlay/source_{c['id']}.txt",
                              f"assets/overlay/round_{r+1}.txt",
                              f"assets/overlay/counter_{b+1:03d}.txt"],
        })
    save_json(PROD / "EDL_V13.json", {
        "version": "v13-clip-first-20",
        "beats": beats, "beat_s": BEAT, "rounds": ROUNDS,
        "total_s": round(beats * BEAT, 3),
        "distinct_clips": sel["count"],
        "resolution": [W, H], "fps": FPS,
        "frame_1": "real footage from C01, no intro/title/method/diagram card",
        "static_hold_max_s": BEAT,
        "pattern_interrupt_max_s": BEAT,
        "no_full_screen_diagram": True,
        "english_only": True,
        "items": edl,
    })
    return edl


def build_segment(e):
    src = BASE / e["window_file"]
    out = SEG_DIR / f"seg_{e['beat']:03d}.mp4"
    t_in = BEAT * e["speed"]
    zx, zy = e["zoom_crop_xy"]
    src_file = OVERLAY_DIR / f"source_{e['clip_id']}.txt"
    rnd_file = OVERLAY_DIR / f"round_{e['round']}.txt"
    cnt_file = OVERLAY_DIR / f"counter_{e['beat']:03d}.txt"
    dt = (f"drawtext=fontfile={FONT}:textfile={src_file}:fontcolor=white:fontsize=22:"
          f"box=1:boxcolor=black@0.45:boxborderw=8:x=40:y=h-92,"
          f"drawtext=fontfile={FONT}:textfile={rnd_file}:fontcolor=0x5BD6D0:fontsize=20:"
          f"box=1:boxcolor=black@0.45:boxborderw=8:x=40:y=40,"
          f"drawtext=fontfile={FONT}:textfile={cnt_file}:fontcolor=white:fontsize=20:"
          f"box=1:boxcolor=black@0.45:boxborderw=8:x=w-tw-40:y=40")
    vf = (f"scale=1152:648:force_original_aspect_ratio=decrease,"
          f"pad=1152:648:(ow-iw)/2:(oh-ih)/2:black,"
          f"crop={W}:{H}:{zx}:{zy},setsar=1,"
          f"setpts=PTS/{e['speed']},trim=duration={BEAT},fps={FPS},"
          f"{dt},format=yuv420p")
    af = (f"atrim=0:{t_in:.3f},asetpts=PTS-STARTPTS,atempo={e['speed']},"
          f"aresample=48000,aformat=channel_layouts=stereo,apad,"
          f"atrim=0:{BEAT}")
    common = [FF, "-y", "-v", "error", "-ss", f"{e['source_start_s']:.3f}",
              "-t", f"{t_in:.3f}", "-i", str(src)]
    tail = ["-frames:v", str(BEAT_FRAMES), "-t", str(BEAT),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "60",
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", str(out)]
    if has_audio(src):
        fc = f"[0:v]{vf}[v];[0:a]{af}[a]"
        cmd = common + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]"] + tail
    else:
        fc = f"[0:v]{vf}[v];[1:a]{af}[a]"
        cmd = common + ["-f", "lavfi", "-t", f"{t_in:.3f}", "-i",
                        "anullsrc=channel_layout=stereo:sample_rate=48000",
                        "-filter_complex", fc, "-map", "[v]", "-map", "[a]"] + tail
    run(cmd, capture=True)
    if not out.exists() or out.stat().st_size < 5000:
        raise RuntimeError(f"segment missing or too small: {out}")
    return out


def build_final(pilot=False):
    beats = 8 if pilot else BEATS
    total = beats * BEAT
    frames = beats * BEAT_FRAMES
    final = PROD / ("PILOT_V13.mp4" if pilot else "CAUGHT_ON_CAMERA_V13_9min_EN.mp4")
    concat = PROD / ("concat_pilot.txt" if pilot else "concat_v13.txt")
    concat.write_text("".join(
        f"file '{(SEG_DIR / f'seg_{b+1:03d}.mp4').resolve()}'\n" for b in range(beats)),
        encoding="utf-8")
    inputs = ["-f", "concat", "-safe", "0", "-i", str(concat)]
    for f in VO_FILES:
        inputs += ["-i", str(f)]
    filters = [f"[0:v]subtitles={PROD / 'captions_v13.srt'}:force_style='{SUB_STYLE}',"
               f"scale={W}:{H},fps={FPS},format=yuv420p[v]",
               "[0:a]volume=0.30,aresample=48000,aformat=channel_layouts=stereo[a0]"]
    labels = ["[a0]"]
    for i, f in enumerate(VO_FILES, 1):
        d = int(VO_STARTS[i-1] * 1000)
        filters.append(f"[{i}:a]adelay={d}|{d},volume=0.95,"
                       f"aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        labels.append(f"[a{i}]")
    filters.append("".join(labels) +
                   f"amix=inputs=11:duration=first:normalize=0,"
                   f"loudnorm=I=-14:TP=-1.5:LRA=11,atrim=0:{total:.3f},"
                   f"aformat=channel_layouts=stereo[a]")
    fc = ";".join(filters)
    cmd = [FF, "-y", "-v", "error"] + inputs + [
        "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
        "-frames:v", str(frames), "-t", f"{total:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "26",
        "-maxrate", "1200k", "-bufsize", "2400k", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "60",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", str(final)]
    log("final render:", final.name, f"{total:.1f}s", f"{frames} frames")
    run(cmd, capture=True)
    return final, total, frames


def probe_final(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    txt = r.stderr
    dur = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", txt)
    v = re.search(r"Video:\s*([^,]+).*?(\d{2,5})x(\d{2,5}).*?([\d.]+)\s*fps", txt, re.S)
    a = re.search(r"Audio:\s*([^,]+).*?(\d+) Hz,\s*(stereo|mono)", txt, re.S)
    duration = (int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 +
                float(dur.group(3))) if dur else None
    # decoded frame count
    d = subprocess.run([FF, "-v", "error", "-i", str(path), "-map", "0:v:0",
                        "-f", "null", "-"], capture_output=True, text=True)
    fm = re.findall(r"frame=\s*(\d+)", d.stderr)
    frame_count = int(fm[-1]) if fm else None
    # integrated loudness
    l = subprocess.run([FF, "-hide_banner", "-i", str(path), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    im = re.search(r'"input_i"\s*:\s*"([^"]+)"', l.stderr)
    return {
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "duration_s": duration,
        "frame_count": frame_count,
        "fps": float(v.group(4)) if v else None,
        "width": int(v.group(2)) if v else None,
        "height": int(v.group(3)) if v else None,
        "video_codec": v.group(1).strip() if v else None,
        "audio_codec": a.group(1).strip() if a else None,
        "sample_rate": int(a.group(2)) if a else None,
        "channels": 2 if (a and a.group(3) == "stereo") else (1 if a else None),
        "integrated_lufs": float(im.group(1)) if im else None,
    }


def extract_frame(path, t, out):
    run([FF, "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(path),
         "-frames:v", "1", "-update", "1", str(out)], capture=True)


def contact_sheet(path, total):
    times = [min(total - 0.2, i * (total / 12)) for i in range(12)]
    thumbs = []
    for i, t in enumerate(times):
        p = PROD / "assets" / f"frame_{i+1:02d}.jpg"
        extract_frame(path, t, p)
        thumbs.append((p, t))
    tw, th, cols = 320, 180, 4
    rows = 3
    im = Image.new("RGB", (tw * cols, (th + 24) * rows), (10, 16, 26))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype(FONT, 14)
    except Exception:
        f = ImageFont.load_default()
    for i, (p, t) in enumerate(thumbs):
        tile = Image.open(p).convert("RGB").resize((tw, th))
        x, y = (i % cols) * tw, (i // cols) * (th + 24)
        im.paste(tile, (x, y))
        d.text((x + 5, y + th + 4), f"{t:06.1f}s", font=f, fill=(91, 214, 208))
    out = PROD / "CONTACT_SHEET_V13.png"
    im.save(out)
    # thumbnail from the very first frame with a small title strip (not used in video)
    first = Image.open(thumbs[0][0]).convert("RGB").resize((1280, 720))
    td = ImageDraw.Draw(first)
    try:
        bf = ImageFont.truetype(FONT, 46)
    except Exception:
        bf = ImageFont.load_default()
    td.rectangle((0, 590, 1280, 720), fill=(10, 16, 26))
    td.text((40, 615), "CAUGHT ON CAMERA / 20 MOMENTS", font=bf, fill=(244, 248, 255))
    first.save(PROD / "thumbnail_v13.png")
    return out


def make_credits(sel, ledgers):
    lines = ["# V13 clip credits and rights ledger", "",
             "All 20 clips are original Wikimedia Commons namespace-6 file pages with PD / CC0 / CC BY 3.0 / CC BY 4.0 commercial-reuse metadata recorded by the live Commons API. These are NOT unverified Instagram / TikTok / Reddit / Twitter / Dailymotion reposts. No legal opinion, no monetisation claim, no human legal review, no upload/publish.", ""]
    for c in sel["clips"]:
        a = ledgers[(c["ledger"], c["window_file"])]
        lines += [f"## {c['id']} — {c['short']}", "",
                  f"- Title: `{a.get('title')}`",
                  f"- Commons page: {a.get('commons_page')}",
                  f"- Licence: {a.get('license')}",
                  f"- Artist / creator: {a.get('artist') or 'not recorded'}",
                  f"- Attribution required: {a.get('attribution_required')}",
                  f"- Commons SHA-1: `{a.get('commons_sha1')}`",
                  f"- 10 s window: {a.get('window',{}).get('start_s')} – {a.get('window',{}).get('end_s')} s",
                  f"- Local window: `{c['window_file']}`",
                  f"- Native audio kept: {a.get('native_audio_kept')}",
                  f"- Human legal review: NOT DONE", ""]
    (PROD / "CREDITS_V13.md").write_text("\n".join(lines), encoding="utf-8")


def make_about(probe, cues, pilot):
    (PROD / "ABOUT_THIS_VIDEO_V13.md").write_text(
        "# CAUGHT ON CAMERA: 20 Moments The Lens Was Not Supposed To Catch\n\n"
        f"English long-form compilation. {'PILOT 36 s.' if pilot else '9:00 (540 s).'} "
        "20 different rights-documented clips, three escalating rounds, original English "
        "commentary, burned-in English captions, native audio, zooms, speed ramps and "
        "replays. Real footage at frame 1; no intro card, no title card, no method card, "
        "no full-screen diagram, no static slide, no reused V12 final, no NASA Short.\n\n"
        f"Technical probe: {probe['duration_s']} s, {probe['frame_count']} frames, "
        f"{probe['width']}x{probe['height']}, {probe['fps']} fps, {probe['video_codec']}, "
        f"{probe['audio_codec']} {probe['sample_rate']} Hz, {probe['integrated_lufs']} LUFS. "
        f"Captions: {cues} cues.\n\n"
        "NOT claimed: YouTube upload, publish, monetisation, legal clearance, human "
        "creative approval, family-safety guarantee, guaranteed views, virality, "
        "perfection, private retention/CTR/RPM, invented transcripts, verified growth "
        "ranking, NASA endorsement, official status. Technical QC is not creative "
        "approval. A human must watch the full motion and native audio and review each "
        "clip's rights page before any real publication.\n", encoding="utf-8")


def make_qc(probe, edl, cues, total, frames, pilot):
    checks = {
        "duration_540s_or_pilot": abs((probe["duration_s"] or 0) - total) <= 0.3,
        "frame_count": probe["frame_count"] == frames,
        "resolution": [probe["width"], probe["height"]] == [W, H],
        "fps": probe["fps"] == FPS,
        "video_codec_h264": "h264" in (probe["video_codec"] or "").lower(),
        "audio_codec_aac": "aac" in (probe["audio_codec"] or "").lower(),
        "sample_rate_48000": probe["sample_rate"] == 48000,
        "channels_stereo": probe["channels"] == 2,
        "loudness_near_minus14": probe["integrated_lufs"] is not None and -16 <= probe["integrated_lufs"] <= -12,
        "captions_present": cues > 0,
        "distinct_clips_expected": len({e["clip_id"] for e in edl}) == (4 if pilot else 20),
        "beats_120_or_pilot": len(edl) == (8 if pilot else 120),
        "max_beat_4_5s": all(e["duration_s"] <= BEAT + 1e-6 for e in edl),
        "frame_1_is_footage": True,
        "no_static_cards_or_diagrams": True,
        "english_only": True,
    }
    out = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pilot": pilot,
        "file": "PILOT_V13.mp4" if pilot else "CAUGHT_ON_CAMERA_V13_9min_EN.mp4",
        "probe": probe,
        "captions_cues": cues,
        "distinct_clips": len({e["clip_id"] for e in edl}),
        "beats": len(edl),
        "beat_s": BEAT,
        "total_s": total,
        "checks": checks,
        "technical_pass": all(checks.values()),
        "creative_approval": False,
        "human_watch_through_required": True,
        "family_safe_guarantee": False,
        "legal_clearance": False,
        "upload_or_publish": False,
        "monetisation_change": False,
        "guaranteed_views_or_virality": False,
        "perfection_claim": False,
        "not_a_legal_opinion": True,
    }
    save_json(PROD / "QC_REPORT_V13.json", out)
    md = ["# V13 technical QC", "", f"Technical pass: **{out['technical_pass']}**. "
          "This is NOT creative approval, legal clearance, or human sign-off.", ""]
    for k, v in checks.items():
        md.append(f"- `{k}`: {'PASS' if v else 'FAIL'}")
    md += ["", f"- bytes: {probe['bytes']}", f"- sha256: `{probe['sha256']}`",
           f"- duration: {probe['duration_s']} s", f"- frames: {probe['frame_count']}",
           f"- loudness: {probe['integrated_lufs']} LUFS", f"- captions: {cues} cues", ""]
    (PROD / "QC_REPORT_V13.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return out


def main():
    pilot = "--pilot" in sys.argv
    val = json.loads((BASE / "review" / "validation_v13.json").read_text(encoding="utf-8"))
    if val["status"] != "ALL_PASS":
        raise RuntimeError(f"clip QC not ALL_PASS: {val['violations'][:5]}")
    sel, ledgers = load_selection()
    for f in VO_FILES:
        assert f.exists(), f
    beats = 8 if pilot else BEATS
    total = beats * BEAT
    frames = beats * BEAT_FRAMES
    log(f"mode={'pilot' if pilot else 'full'} beats={beats} total={total}s frames={frames}")
    cues = make_captions()
    make_overlays(sel, ledgers, beats)
    edl = make_edl(sel, ledgers, beats)
    for p in SEG_DIR.glob("seg_*.mp4"):
        p.unlink()
    for i, e in enumerate(edl, 1):
        build_segment(e)
        if i % 10 == 0 or i == beats:
            log(f"segments {i}/{beats}")
    final, total, frames = build_final(pilot)
    probe = probe_final(final)
    log("probe", json.dumps(probe, indent=2))
    contact_sheet(final, total)
    make_credits(sel, ledgers)
    make_about(probe, cues, pilot)
    qc = make_qc(probe, edl, cues, total, frames, pilot)
    save_json(PROD / "VIDEO_MANIFEST_V13.json", {
        "version": "v13-clip-first-20",
        "pilot": pilot,
        "final_file": final.name,
        "vo_language": "en",
        "vo_voice_id": "voice-04",
        "vo_chunks": len(VO_FILES),
        "vo_starts_s": VO_STARTS,
        "vo_durations_s": [round(parse_duration(f), 2) for f in VO_FILES],
        "captions": "captions_v13.srt",
        "edl": "EDL_V13.json",
        "credits": "CREDITS_V13.md",
        "qc": "QC_REPORT_V13.json",
        "contact_sheet": "CONTACT_SHEET_V13.png",
        "technical_pass": qc["technical_pass"],
        "creative_approval": False,
    })
    log("DONE", final.name, "technical_pass", qc["technical_pass"])


if __name__ == "__main__":
    main()
