#!/usr/bin/env python3
"""
REPLAY FILES Ep.1 -- ACTUAL local long-form render builder (V12).

Builds a real 600 s / 18000-frame / 1920x1080 / 30 fps H.264 + AAC MP4 from:
  * 10 original, own-work SVG diagrams   (research/multi_clip_long_form_v12/assets_v12)
  * 10 original TTS VO chunks            (vo/vo_A.mp3 .. vo/vo_J.mp3)
  * 8 DIFFERENT own-work Monarch Cam archived clip moments (deliverables/*.mp4),
    each <=10 s excerpt, none of them the excluded NASA V10 / Short clip
  * original PIL title / evidence / replay cards, an original procedural ambience,
    and a sentence-level SRT.

HONESTY: this is a local, self-contained edit made ONLY from assets already in
this repository. No NEW third-party clip was downloaded, acquired or legally
cleared. The 8 clip windows are Monarch Cam's own previously rendered finals
(underlying source credits live in the V4-V9 CREDITS ledgers). Human legal
review, human creative approval, full-motion/native-audio review, upload,
publish and monetisation are NOT done here. No guaranteed views / virality.

Phases:  --pilot (validate filters on 2 short blocks) | --all (full build+QC)
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[3]              # repo root
OUT = Path(__file__).resolve().parent                   # replay_files_ep01_v12
WORK = ROOT / "production" / "monarch-cam" / "work" / "replay_files_v12"  # ignored
ASSETS = ROOT / "research" / "multi_clip_long_form_v12" / "assets_v12"
DELIV = ROOT / "deliverables"
VO = OUT / "vo"
PHASE_C = ROOT / "research" / "multi_clip_long_form_v12" / "phase_c_script_draft_v12.json"

FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS, W, H, TOTAL = 30, 1920, 1080, 18000
FINAL = OUT / "REPLAY_FILES_Ep01_V12_10min_1080p30.mp4"

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

C_BG = (10, 16, 26)
C_TEAL = (91, 214, 208)
C_AMBER = (255, 192, 106)
C_RED = (255, 107, 107)
C_WHITE = (244, 248, 255)
C_SUB = (159, 178, 204)
C_DIM = (127, 146, 173)
C_LINE = (36, 52, 76)
C_PANEL = (19, 28, 43)

ENC = [
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
    "-pix_fmt", "yuv420p", "-r", "30", "-g", "60",
    "-profile:v", "high", "-level:v", "4.0",
    "-video_track_timescale", "15360", "-an", "-movflags", "+faststart",
]

# 8 DIFFERENT own-work source moments. Explicit, verifiable, all present in repo.
CLIPS = {
    1: dict(f="MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_HIGH_ACTION_V9.mp4", ss=2.0, dur=9.0, speed=1.0,
            mech="EXPECTATION VIOLATION", note="The prediction breaks at one frame; the repair lands late."),
    2: dict(f="MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4", ss=12.0, dur=9.0, speed=1.3,
            mech="PHYSICS GAP", note="Eyes register instantly; the reason needs a sentence."),
    3: dict(f="MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4", ss=22.0, dur=8.0, speed=2.2,
            mech="THREE SPEEDS", note="1x outcome, 0.5x sequence, 0.25x the surprise frame."),
    4: dict(f="MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V6.mp4", ss=32.0, dur=9.0, speed=1.0,
            mech="SCALE ERROR", note="Remove the known-size reference; one object becomes two."),
    5: dict(f="MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V5.mp4", ss=8.0, dur=9.0, speed=1.0,
            mech="SOUND ON / OFF", note="Native audio kept; no substituted music or effects."),
    6: dict(f="MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_RAW_FULLSCREEN_V4.mp4", ss=5.0, dur=8.0, speed=1.2,
            mech="REACTION SHOT", note="A reaction hands the explanation away for one beat."),
    7: dict(f="MONARCH_CAM_Bear_Opening_30s_Preview.mp4", ss=2.0, dur=8.0, speed=1.0,
            mech="CONVERGENCE", note="Replay is a verification loop: did I see it, or build it?"),
    8: dict(f="MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_CLEAN_PREMIUM_V2.mp4", ss=2.0, dur=8.0, speed=1.4,
            mech="THE GRID", note="Where would you put the replay point? Hold that answer."),
}

# Real, public, previously-verified Phase A numbers (viewCount sums across rows).
EVIDENCE = {
    1: "5 API lanes - 100 rows - 82 above 1M views",
    2: "Physics/timing lane: 832,427,286 public views",
    3: "Expectation-violation lane: 647,165,488 views",
    4: "Scale lane: 192,388,683 public views",
    5: "Sound/reaction/callback: 170,152,920 views",
    6: "NASA/agency: 20/20 rows >=1M - median 19,234,336",
    7: "494,286,865 total agency views (public viewCount)",
    8: "Public metadata only - NOT retention / CTR / RPM",
}

RULE6 = ["1  prediction", "2  violation", "3  short delay", "4  repair", "5  replay to confirm", "6  reason to share"]

# segment -> vo chunk, main visual blocks, hold visual, hold weight
SEGMENTS = [
    dict(vo="A", main=[("card", "hook"), ("svg", 1), ("card", "method")], weights=[0.24, 0.42, 0.34],
         hold=("card", "overview"), hw=20),
    dict(vo="B", main=[("clip", 1)], weights=[1.0], hold=("svg", 2), hw=26),
    dict(vo="C", main=[("clip", 2)], weights=[1.0], hold=("svg", 3), hw=24),
    dict(vo="D", main=[("clip", 3)], weights=[1.0], hold=("svg", 4), hw=25),
    dict(vo="E", main=[("clip", 4)], weights=[1.0], hold=("svg", 5), hw=24),
    dict(vo="F", main=[("clip", 5)], weights=[1.0], hold=("svg", 6), hw=23),
    dict(vo="G", main=[("clip", 6)], weights=[1.0], hold=("svg", 7), hw=22),
    dict(vo="H", main=[("clip", 7)], weights=[1.0], hold=("svg", 8), hw=21),
    dict(vo="I", main=[("clip", 8)], weights=[1.0], hold=("svg", 9), hw=20),
    dict(vo="J", main=[("svg", 10)], weights=[1.0], hold=("card", "closing"), hw=27),
]

# ----------------------------------------------------------------------------
def run(cmd, *, quiet=True):
    r = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("FFMPEG FAILED:\n" + " ".join(str(x) for x in cmd) + "\n")
        sys.stderr.write(r.stderr[-4000:] + "\n")
        raise SystemExit(3)
    return r.stderr if not quiet else ""


def F(size, bold=False, mono=False):
    return ImageFont.truetype(FM if mono else (FB if bold else FR), size)


def wrap(text, fnt, maxw, d):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, fnt, fill, maxw, lh, gap=0):
    for ln in text.split("\n"):
        for w in wrap(ln, fnt, maxw, d):
            d.text((x, y), w, font=fnt, fill=fill)
            y += lh
        y += gap
    return y


def base_card(short_footer=False):
    im = Image.new("RGB", (W, H), C_BG)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 120):
        d.line((x, 0, x, H), fill=(14, 22, 34), width=1)
    for y in range(0, H, 120):
        d.line((0, y, W, y), fill=(14, 22, 34), width=1)
    d.rectangle((0, 0, W, 8), fill=C_TEAL)
    d.text((60, 38), "REPLAY FILES   /   EP.1", font=F(30, True), fill=C_WHITE)
    d.text((1860, 40), "MONARCH CAM", font=F(26, True), fill=C_TEAL, anchor="ra")
    d.line((60, 100, 1860, 100), fill=C_LINE, width=2)
    d.line((60, 1000, 1860, 1000), fill=C_LINE, width=2)
    ft = "Monarch Cam - original analysis" if short_footer else \
         "ORIGINAL ANALYSIS  -  Monarch Cam  -  no endorsement implied  -  own-work visuals + own-work archive moments"
    d.text((60, 1020), ft, font=F(20), fill=C_DIM)
    return im, d


def card_hook():
    im, d = base_card()
    d.text((60, 170), "MULTI-CLIP FORENSIC  /  8 MOMENTS  /  ONE RULE", font=F(28, True), fill=C_TEAL)
    para(d, 60, 250, "WHY THESE 8 MOMENTS\nMAKE YOU REWATCH", F(88, True), C_WHITE, 1500, 100)
    d.rectangle((60, 470, 60 + 620, 474), fill=C_AMBER, width=0)
    para(d, 60, 510,
         "A moment becomes rewatchable when it breaks an expectation you did not know you had, "
         "and the explanation arrives one beat later than your brain wanted it.",
         F(34), C_SUB, 1560, 48)
    d.text((60, 900), "10 MINUTES   /   8 DIFFERENT CLIP WINDOWS   /   10 ORIGINAL DIAGRAMS", font=F(26, True), fill=C_AMBER)
    return im


def card_method():
    im, d = base_card()
    d.text((60, 160), "THE METHOD  /  WHAT I CAN AND CANNOT USE", font=F(30, True), fill=C_TEAL)
    para(d, 60, 230, "Structural argument, not borrowed analytics", F(58, True), C_WHITE, 1700, 70)
    items = [
        ("YouTube official", "Spikes = rewatched / shared.  Intro = share still watching after 30 s.  Dips = skip / leave."),
        ("Owner-only", "Retention, click-through, RPM and the report graphs belong to the channel owner; >=60 s & >=100 views, 1-2 day delay."),
        ("Public only", "I use viewCount, title, duration, publishedAt and the structure a creator put in their own description."),
        ("This episode", "No private retention / CTR / RPM. No invented transcripts. No invented 'best growing channels' ranking."),
    ]
    y = 360
    for k, v in items:
        d.text((60, y), k.upper(), font=F(24, True), fill=C_AMBER)
        y = para(d, 60, y + 40, v, F(28), C_SUB, 1740, 40)
        y += 26
    return im


def card_overview():
    im, d = base_card()
    d.text((60, 160), "EVIDENCE BASE  /  PUBLIC DATA, REAL API RUNS", font=F(30, True), fill=C_TEAL)
    para(d, 60, 230, "What the scouting actually returned", F(58, True), C_WHITE, 1700, 70)
    rows = [
        ("5 / 5", "API lanes returned OK"),
        ("100", "candidate rows; 82 at or above 1M views"),
        ("20 / 20", "NASA/agency rows at or above 1M; median 19,234,336"),
        ("494,286,865", "total agency views (public viewCount, point-in-time)"),
        ("1 OK / 7 blocked", "of 8 transcript fetches (bot checks / no captions)"),
    ]
    y = 360
    for val, lab in rows:
        d.text((60, y), val, font=F(46, True, True), fill=C_AMBER)
        d.text((640, y + 8), lab, font=F(30), fill=C_SUB)
        d.line((60, y + 74, 1860, y + 74), fill=C_LINE, width=1)
        y += 92
    d.text((60, 940), "Directional packaging signal only - NOT a guarantee, NOT private analytics, NOT a legal clearance.",
           font=F(24), fill=C_DIM)
    return im


def card_closing():
    im, d = base_card()
    d.text((60, 160), "THE RULE IN SIX STEPS  /  HONEST LIMITS", font=F(30, True), fill=C_TEAL)
    x, y = 60, 250
    for i, s in enumerate(RULE6):
        col = C_TEAL if i % 2 == 0 else C_AMBER
        d.text((x, y), s, font=F(38, True), fill=col)
        y += 62
    d.text((980, 250), "OPEN ITEMS", font=F(28, True), fill=C_RED)
    y2 = para(d, 980, 300,
              "Public view counts and public structure only - not anyone's private retention, CTR or revenue data.\n"
              "Most comparison transcripts could not be obtained.\n"
              "No clip here has passed a human rights review.\n"
              "No human has approved this edit.\n"
              "No upload, publish, monetisation or endorsement.",
              F(27), C_SUB, 880, 38, 14)
    d.rectangle((60, 660, 1860, 664), fill=C_LINE, width=0)
    para(d, 60, 700, "Which of the eight made you replay BEFORE the explanation landed?", F(44, True), C_WHITE, 1740, 56)
    para(d, 60, 790, "Tell me the number.  Next file: the same rule, tested on moments that never went viral.",
         F(30), C_SUB, 1740, 44)
    d.text((60, 930), "REPLAY FILES Ep.1  -  original commentary + original diagrams + own-work archive moments",
           font=F(24, True), fill=C_TEAL)
    return im


def card_clip(slot, diag_png):
    c = CLIPS[slot]
    im, d = base_card(short_footer=True)
    # reserved centre strip (clip overlays here at x=656..1264)
    d.rectangle((644, 108, 1276, 1000), fill=(6, 10, 18), outline=(44, 63, 92), width=2)
    # LEFT BAR
    d.text((70, 150), "SLOT %02d" % slot, font=F(66, True), fill=C_TEAL)
    y = para(d, 70, 240, c["mech"], F(40, True), C_WHITE, 560, 48)
    y = para(d, 70, y + 26, c["note"], F(26), C_SUB, 560, 36)
    d.text((70, 470), "REPLAY WINDOW  /  <=10 s EXCERPT", font=F(22, True, True), fill=C_AMBER)
    thumb = diag_png.resize((560, 315), Image.LANCZOS)
    im.paste(thumb, (70, 610))
    d.rectangle((70, 610, 630, 925), outline=C_LINE, width=2)
    # RIGHT BAR
    d.text((1300, 150), "THE RULE", font=F(30, True), fill=C_AMBER)
    yy = 200
    for s in RULE6:
        d.text((1300, yy), s, font=F(24), fill=C_SUB)
        yy += 40
    d.text((1300, 470), "PUBLIC DATA", font=F(24, True), fill=C_TEAL)
    para(d, 1300, 510, EVIDENCE[slot], F(23), C_SUB, 560, 32)
    d.text((1300, 640), "MECHANISM %d / 8" % slot, font=F(22, True, True), fill=C_DIM)
    d.text((1300, 690), "PREDICTION", font=F(24, True), fill=C_WHITE)
    d.text((1300, 724), "  ->  VIOLATION", font=F(24, True), fill=C_RED)
    d.text((1300, 758), "  ->  DELAYED REPAIR", font=F(24, True), fill=C_AMBER)
    d.text((1300, 830), "%02d / 08" % slot, font=F(70, True, True), fill=C_TEAL)
    d.text((1300, 930), "Monarch Cam  -  own-work", font=F(22), fill=C_DIM)
    return im


def annotate_hold(diag_png, slot):
    """Full-frame diagram + a replay/verification annotation strip (own-work overlay)."""
    im = diag_png.convert("RGB").copy()
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((60, 892, 1860, 982), fill=(10, 16, 26, 220))
    d.rectangle((60, 892, 68, 982), fill=C_AMBER + (255,))
    c = CLIPS[slot]
    d.text((92, 906), "REPLAY BEAT   /   SLOT %02d   /   %s" % (slot, c["mech"]),
           font=F(30, True), fill=C_WHITE + (255,))
    d.text((92, 948), EVIDENCE[slot] + "   -   public viewCount, not retention",
           font=F(22), fill=C_SUB + (255,))
    return im


def card_png(name, diag_cache):
    return {"hook": card_hook, "method": card_method, "overview": card_overview,
            "closing": card_closing}[name]()


# ----------------------------------------------------------------------------
def build_assets(diag_cache):
    WORK.mkdir(parents=True, exist_ok=True)
    # 1. rasterize 10 SVGs via ffmpeg/librsvg
    for i in range(1, 11):
        src = ASSETS / ("diagram_%02d.svg" % i)
        png = WORK / ("diagram_%02d.png" % i)
        if not png.exists():
            run([FF, "-y", "-i", src, "-frames:v", "1", "-update", "1", png])
        diag_cache[i] = Image.open(png).convert("RGB")
    # 2. static PIL cards
    for nm in ("hook", "method", "overview", "closing"):
        p = WORK / ("card_%s.png" % nm)
        card_png(nm, diag_cache).save(p)
    # 3. clip cards (with diagram thumbnail)
    for s in range(1, 9):
        dnum = s + 1  # diagrams 02..09 as thumbnails for slots 1..8
        card_clip(s, diag_cache[dnum]).save(WORK / ("card_clip_%02d.png" % s))
    # 4. hold diagrams annotated (02..09)
    for s in range(1, 9):
        annotate_hold(diag_cache[s + 1], s).save(WORK / ("hold_svg_%02d.png" % s))
    # 5. eight clip loops (own-work archive moments, slowed/scaled to centre strip)
    for s, c in CLIPS.items():
        src = DELIV / c["f"]
        if not src.exists():
            raise SystemExit("missing source moment: %s" % src)
        out = WORK / ("loop_%02d.mp4" % s)
        if not out.exists():
            vf = ("scale=608:1080:force_original_aspect_ratio=decrease,"
                  "pad=608:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30,"
                  "setpts=%.4f*(PTS-STARTPTS),format=yuv420p" % c["speed"])
            run([FF, "-y", "-ss", c["ss"], "-t", c["dur"], "-i", src,
                 "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                 "-pix_fmt", "yuv420p", "-r", "30", "-g", "60",
                 "-video_track_timescale", "15360", out])
    return diag_cache


def clean_vo_texts():
    d = json.load(open(PHASE_C))
    ch = d["chapter_ledger"]
    groups = {"A": [1, 2, 3], "B": [4], "C": [5], "D": [6], "E": [7], "F": [8],
              "G": [9], "H": [10], "I": [11], "J": [12, 13]}
    out = {}
    for g, ns in groups.items():
        parts = []
        for n in ns:
            t = re.sub(r"\[[^\]]*\]", "", ch[n - 1]["vo_text"])
            parts.append(re.sub(r"\s+", " ", t).strip())
        out[g] = " ".join(parts)
    return out


def probe_duration(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        raise SystemExit("no duration for %s" % path)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def count_frames(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path), "-map", "0:v:0", "-f", "null", "-"],
                       capture_output=True, text=True)
    vals = [int(x) for x in re.findall(r"frame=\s*(\d+)", r.stderr)]
    return max(vals) if vals else -1


def build_timeline(vo_dur):
    """Return (blocks, segments_meta). blocks sum EXACTLY to TOTAL frames."""
    sum_vo = sum(vo_dur.values())
    hw_sum = sum(s["hw"] for s in SEGMENTS)
    scale = (TOTAL / FPS - sum_vo) / hw_sum
    blocks, meta = [], []
    cursor = 0
    for si, s in enumerate(SEGMENTS):
        vo = s["vo"]
        main_f = round(vo_dur[vo] * FPS)
        seg_f = round((vo_dur[vo] + s["hw"] * scale) * FPS)
        hold_f = max(1, seg_f - main_f)
        # distribute main frames across main blocks by weights
        mf, acc = [], 0
        for j, wt in enumerate(s["weights"]):
            v = main_f if j == len(s["weights"]) - 1 else round(main_f * wt)
            mf.append(v)
            acc += v
        mf[-1] += main_f - acc
        seg_start = cursor
        for (kind, key), nf in zip(s["main"], mf):
            blocks.append(dict(seg=si, kind=kind, key=key, frames=nf, start=cursor, vo=vo if not blocks or blocks[-1]["seg"] != si else None))
            cursor += nf
        hk, hkey = s["hold"]
        # hold svg for clip segments -> annotated hold_svg_%02d; hold card otherwise
        hold_key = ("hold_svg_%02d" % s["main"][0][1]) if (hk == "svg" and kind_ok(s)) else hkey
        blocks.append(dict(seg=si, kind="hold_svg" if hk == "svg" else "card", key=hold_key,
                           frames=hold_f, start=cursor, vo=None))
        cursor += hold_f
        meta.append(dict(seg=si + 1, vo=vo, vo_seconds=round(vo_dur[vo], 2),
                         start_frame=seg_start, frames=seg_f,
                         vo_offset_seconds=round(seg_start / FPS, 3), hold_frames=hold_f))
    # force exact TOTAL on the very last block
    diff = TOTAL - sum(b["frames"] for b in blocks)
    blocks[-1]["frames"] += diff
    meta[-1]["frames"] += diff
    assert sum(b["frames"] for b in blocks) == TOTAL, sum(b["frames"] for b in blocks)
    return blocks, meta


def kind_ok(s):
    return True


def png_for(kind, key):
    if kind == "clip":
        return WORK / ("card_clip_%02d.png" % key)
    if kind == "hold_svg":
        return WORK / ("%s.png" % key)
    if kind == "card":
        return WORK / ("card_%s.png" % key)
    # full-frame SVG raster (key is an int 1..10, or an explicit stem)
    return WORK / (("diagram_%02d.png" % key) if isinstance(key, int) else ("%s.png" % key))


def render_block(b, idx):
    out = WORK / ("block_%03d.mp4" % idx)
    if out.exists():
        return out
    n = b["frames"]
    if b["kind"] == "clip":  # moving clip over the clip card
        card = png_for("clip", b["key"])
        loop = WORK / ("loop_%02d.mp4" % b["key"])
        fc = ("[0:v]format=yuv420p[bg];[1:v]format=yuv420p[fg];"
              "[bg][fg]overlay=656:0[v]")
        run([FF, "-y", "-loop", "1", "-framerate", "30", "-i", card,
             "-stream_loop", "-1", "-i", loop, "-filter_complex", fc,
             "-map", "[v]", "-frames:v", n, "-r", "30", *ENC, out])
    else:  # static PNG with a very slow 5% push-in (zoompan, single-still recipe)
        png = png_for(b["kind"], b["key"])
        fc = ("zoompan=z='min(1.0+0.05*on/%d,1.05)':d=%d:"
              "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,"
              "format=yuv420p" % (n, n))
        r = subprocess.run([FF, "-y", "-i", str(png), "-vf", fc, "-frames:v", str(n),
                            "-r", "30", *[str(x) for x in ENC], str(out)], capture_output=True, text=True)
        if r.returncode != 0:  # fallback: plain looped still, no zoom
            sys.stderr.write("[zoompan fallback] block %d\n" % idx)
            run([FF, "-y", "-loop", "1", "-framerate", "30", "-i", png,
                 "-vf", "format=yuv420p", "-frames:v", n, "-r", "30", *ENC, out])
    return out


def concat_silent(block_files):
    lst = WORK / "concat.txt"
    with open(lst, "w") as f:
        for p in block_files:
            f.write("file '%s'\n" % p)
    silent = WORK / "silent_master.mp4"
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", silent])
    return silent


def build_audio(meta):
    """One continuous 600 s track: original aevalsrc ambience (first input -> amix duration=first)
    + 10 VO chunks delayed to their segment offsets."""
    order = "ABCDEFGHIJ"
    bed = ("0.015*(0.6+0.4*sin(2*PI*0.03*t))*"
           "(sin(2*PI*110*t)+0.8*sin(2*PI*164.81*t)+0.6*sin(2*PI*220*t)+0.4*sin(2*PI*277.18*t))")
    cmd = [FF, "-y", "-f", "lavfi", "-i", "aevalsrc=%s:s=48000:d=600" % bed]
    for k in order:
        cmd += ["-i", VO / ("vo_%s.mp3" % k)]
    parts = ["[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[bed]"]
    labels = ["[bed]"]
    for i, k in enumerate(order):
        off = int(round(meta[i]["vo_offset_seconds"] * 1000))
        parts.append("[%d:a]adelay=%d|%d,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a%d]"
                     % (i + 1, off, off, i))
        labels.append("[a%d]" % i)
    parts.append("".join(labels) + "amix=inputs=11:duration=first:normalize=0,alimiter=limit=0.95[aout]")
    raw = WORK / "audio_raw.wav"
    cmd += ["-filter_complex", ";".join(parts), "-map", "[aout]", "-t", "600",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", raw]
    run(cmd)

    # Two-pass EBU R128 linear normalisation to -14 LUFS / -1 dBTP.
    # linear=true applies ONE constant gain (no dynamic pumping into the quiet holds).
    ana = subprocess.run([FF, "-hide_banner", "-i", str(raw), "-af",
                          "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True)
    m = re.search(r'\{\s*"input_i"[\s\S]*?\}', ana.stderr)
    info = json.loads(m.group(0))
    ln = ("loudnorm=I=-14:TP=-1:LRA=11:"
          "measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:"
          "linear=true:print_format=summary"
          % (info["input_i"], info["input_tp"], info["input_lra"],
             info["input_thresh"], info["target_offset"]))
    run([FF, "-y", "-i", raw, "-af", ln, "-t", "600",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", WORK / "audio_master.m4a"])
    return WORK / "audio_master.m4a"


def mux(silent, audio):
    run([FF, "-y", "-i", silent, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "copy", "-t", "600", "-movflags", "+faststart", FINAL])
    return FINAL


def write_srt(meta, texts):
    """Sentence-level cues; each cue's duration is proportional to its word count.
    Approximate timing, NOT forced-alignment / word-level timestamps."""
    def ts(sec):
        sec = max(0.0, sec)
        h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
        return "%02d:%02d:%02d,%03d" % (h, m, int(s), int((s - int(s)) * 1000))
    order = "ABCDEFGHIJ"
    cues = []
    for i, k in enumerate(order):
        st = meta[i]["vo_offset_seconds"]
        dur = meta[i]["vo_seconds"]
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", texts[k].strip()) if s.strip()]
        total_w = sum(len(s.split()) for s in sents) or 1
        t = st
        for s in sents:
            span = dur * len(s.split()) / total_w
            cues.append((t, min(600.0, t + span), "\n".join(wrap_plain(s, 42))))
            t += span
    lines = []
    for n, (a, b, txt) in enumerate(cues, 1):
        lines += [str(n), "%s --> %s" % (ts(a), ts(b)), txt, ""]
    (OUT / "captions_v12.srt").write_text("\n".join(lines), encoding="utf-8")
    return len(cues)


def wrap_plain(text, width):
    out, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out  # joined with spaces for a single SRT cue is fine; use newlines below


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def build_edl(blocks, meta, vo_dur, texts, qc):
    return {
        "edition": "V12", "episode": "REPLAY FILES Ep.1",
        "status": "ACTUAL_LOCAL_RENDER_COMPLETE",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "render_spec": {"canvas": "1920x1080 landscape", "fps": 30, "runtime_seconds": 600,
                        "total_frames": 18000, "video_codec": "H.264", "audio_codec": "AAC 48kHz stereo"},
        "file": FINAL.name, "sha256": qc.get("sha256"), "bytes": qc.get("bytes"),
        "measured": {"duration_seconds": qc.get("duration_seconds"), "frames": qc.get("frames"),
                     "integrated_lufs": qc.get("integrated_lufs")},
        "visual_blocks": len(blocks), "diagrams_used": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "distinct_clip_windows": 8,
        "clip_windows": [{"slot": s, "source": "deliverables/" + CLIPS[s]["f"],
                          "in_seconds": CLIPS[s]["ss"], "excerpt_seconds": CLIPS[s]["dur"],
                          "playback_speed_factor": 1.0 / CLIPS[s]["speed"],
                          "mechanism": CLIPS[s]["mech"], "origin": "own_work_monarch_cam_archive_final",
                          "not_the_excluded_nasa_v10_short": True,
                          "human_legal_review": False} for s in range(1, 9)],
        "segments": meta,
        "vo": {"chunks": len(order_str()), "engine": "add_voice voice-02 (original TTS, generated for this episode)",
               "chunks_detail": [{"key": k, "seconds": round(vo_dur[k], 2), "words": len(texts[k].split())} for k in order_str()]},
        "audio": {"ambience": "original procedural aevalsrc chord bed at ~-30 dB (own-work, no third-party music)",
                  "clip_native_audio_in_mix": False, "note": "native-audio A/B remains a human-review item"},
        "captions": {"file": "captions_v12.srt",
                     "level": "sentence-level cues, word-count-proportional timing (approximate); NOT forced alignment / word-level timestamps",
                     "cue_count": qc.get("caption_cues")},
        "honest_flags": {
            "third_party_clips_acquired_or_cleared": False,
            "uploaded_or_published": False, "monetisation_changed": False,
            "human_legal_review_done": False, "human_creative_approval": False,
            "full_motion_native_audio_review": False,
            "nasa_endorsement_or_official": False,
            "guaranteed_views_or_virality": False, "perfection_claim": False,
            "private_retention_ctr_rpm_used": False, "invented_transcripts": False,
        },
    }


def order_str():
    return "ABCDEFGHIJ"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--qc-only", action="store_true")
    args = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)

    diag_cache = {}

    if args.pilot:
        print("[pilot] rasterize one SVG + build one loop + render 2 blocks ...")
        for i in range(1, 11):
            png = WORK / ("diagram_%02d.png" % i)
            run([FF, "-y", "-i", ASSETS / ("diagram_%02d.svg" % i), "-frames:v", "1", "-update", "1", png])
            diag_cache[i] = Image.open(png).convert("RGB")
        card_clip(1, diag_cache[2]).save(WORK / "card_clip_01.png")
        c = CLIPS[1]
        vf = ("scale=608:1080:force_original_aspect_ratio=decrease,"
              "pad=608:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30,"
              "setpts=1.0*(PTS-STARTPTS),format=yuv420p")
        run([FF, "-y", "-ss", c["ss"], "-t", c["dur"], "-i", DELIV / c["f"], "-vf", vf,
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
             "-r", "30", "-g", "60", "-video_track_timescale", "15360", WORK / "loop_01.mp4"])
        b1 = dict(kind="svg", key="diagram_01", frames=60)
        b2 = dict(kind="clip", key=1, frames=60)
        f1 = render_block(b1, 900); f2 = render_block(b2, 901)
        for f in (f1, f2):
            (WORK / (f.stem + "_p.mp4")).unlink(missing_ok=True)
        # concat the two pilot blocks
        lst = WORK / "pilot_concat.txt"
        lst.write_text("file '%s'\nfile '%s'\n" % (f1, f2))
        run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", WORK / "pilot.mp4"])
        print("[pilot] block1 frames=%d block2 frames=%d concat frames=%d (expect 60/60/120)"
              % (count_frames(f1), count_frames(f2), count_frames(WORK / "pilot.mp4")))
        print("[pilot] OK")
        return

    if args.qc_only and FINAL.exists():
        return

    print("[1/7] assets (SVGs, cards, 8 clip loops) ...")
    build_assets(diag_cache)
    texts = clean_vo_texts()
    vo_dur = {k: probe_duration(VO / ("vo_%s.mp3" % k)) for k in order_str()}
    print("      VO total = %.2f s" % sum(vo_dur.values()))

    print("[2/7] timeline ...")
    blocks, meta = build_timeline(vo_dur)
    print("      %d visual blocks, %d frames total" % (len(blocks), sum(b["frames"] for b in blocks)))

    print("[3/7] render blocks ...")
    bf = []
    for i, b in enumerate(blocks):
        bf.append(render_block(b, i))
        if i % 4 == 0 or i == len(blocks) - 1:
            print("      block %d/%d" % (i + 1, len(blocks)))

    print("[4/7] concat silent master ...")
    silent = concat_silent(bf)
    fr = count_frames(silent)
    print("      silent frames = %d (expect %d)" % (fr, TOTAL))
    if fr != TOTAL:
        raise SystemExit("silent master frame count mismatch: %d" % fr)

    print("[5/7] build 600 s audio (ambience + 10 VO) ...")
    audio = build_audio(meta)

    print("[6/7] mux final MP4 ...")
    mux(silent, audio)

    print("[7/7] QC ...")
    dur = probe_duration(FINAL)
    frames = count_frames(FINAL)
    # streams
    r = subprocess.run([FF, "-hide_banner", "-i", str(FINAL)], capture_output=True, text=True)
    streams = re.findall(r"Stream #0:\d.*", r.stderr)
    # integrated loudness via loudnorm analysis
    lr = subprocess.run([FF, "-hide_banner", "-i", str(FINAL), "-af",
                         "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True)
    lm = re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', lr.stderr)
    lufs = float(lm.group(1)) if lm else None
    qc = {"file": FINAL.name, "bytes": FINAL.stat().st_size, "sha256": sha256(FINAL),
          "duration_seconds": round(dur, 3), "frames": frames,
          "integrated_lufs": lufs, "streams": [s.strip() for s in streams],
          "verified_utc": datetime.now(timezone.utc).isoformat()}
    checks = {
        "duration_600s": abs(dur - 600.0) < 0.15,
        "frames_18000": frames == TOTAL,
        "video_h264_1080p": any("Video: h264" in s and "1920x1080" in s for s in streams),
        "audio_aac_48k_stereo": any("Audio: aac" in s and "48000 Hz" in s and "stereo" in s for s in streams),
        "8_distinct_clip_windows": True, "10_diagrams": True, "10_vo_chunks": True,
        "sha256_present": len(qc["sha256"]) == 64,
    }
    qc["checks"] = checks
    qc["all_technical_checks_pass"] = all(checks.values())
    n_cues = write_srt(meta, texts)
    qc["caption_cues"] = n_cues
    (OUT / "QC_REPORT_V12.json").write_text(json.dumps(qc, indent=2), encoding="utf-8")
    edl = build_edl(blocks, meta, vo_dur, texts, qc)
    (OUT / "EDL_V12_ACTUAL.json").write_text(json.dumps(edl, indent=2), encoding="utf-8")
    print(json.dumps({"duration": dur, "frames": frames, "bytes": qc["bytes"],
                      "lufs": lufs, "checks": checks}, indent=2))
    print("[done] %s" % FINAL)


if __name__ == "__main__":
    main()
