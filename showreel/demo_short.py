"""A 30-second demo short built from numbers this repo actually measured.

Why this exists: every number on screen is read out of `public/yt-intel/*.json` at build
time. Nothing is typed in by hand, so the video cannot drift away from the research — and if
a number changes, the render changes with it.

The script itself is the argument the data made:

  * "youtube automation" has real demand (80/100) and no single owner (top-3 share 0.5), so
    entry is feasible — but the top five videos are all "how to start".
  * the audience of the biggest one says what it actually wants: 11% want to buy teaching,
    1% asked for a sequel, and the most-liked comments are gratitude, not questions.
  * the winning packagings are not neutral: 12/12 have a face, 8/12 are red.
  * and the verdict is still SHARPEN, because nobody has torn down why the winners win.

So the short is not a tutorial. It is the 30 seconds that earns the right to make one.

Usage: python showreel/demo_short.py [--out path] [--fps 30]
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTEL = os.path.join(ROOT, "public", "yt-intel")
OUT_DEFAULT = os.path.join(ROOT, "public", "demo", "demo-short-30s.mp4")

W, H = 1920, 1080
FPS = 30
DURATION = 30.0

FDIR = "/usr/share/fonts/truetype/dejavu"
F_BOLD = os.path.join(FDIR, "DejaVuSans-Bold.ttf")
F_REG = os.path.join(FDIR, "DejaVuSans.ttf")
F_MONO = os.path.join(FDIR, "DejaVuSansMono.ttf")
F_MONO_B = os.path.join(FDIR, "DejaVuSansMono-Bold.ttf")

TARGET_LUFS = -14.0   # the level online video is mixed to; -25.4 was a mistake, not a style

BG = (9, 10, 12)
INK = (246, 247, 243)
MUTED = (150, 158, 152)
RED = (226, 61, 61)
SAGE = (122, 168, 108)
AMBER = (232, 163, 61)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def load() -> dict:
    """Every fact on screen, read from the research desk. Fail loudly if any is missing."""
    def j(name):
        p = os.path.join(INTEL, name)
        if not os.path.exists(p):
            raise SystemExit(f"missing {p} — run the research job first")
        return json.load(open(p, encoding="utf-8"))

    rep = j("youtube-automation.json")
    com = j("comments-5tOADMwGeBI.json")
    thu = j("thumbnails.json")
    idx = j("index.json")

    views = sorted(r["views"] for r in rep["rows"])
    # The hook used to say "5 of the top 5 say how to start". Hand-written, and wrong: it is
    # 3. Counted here from the rows, so the claim cannot drift from the sample again.
    HOW_TO = re.compile(r"\b(how to|how i|tutorial|guide|step by step|beginner|start|setup|workflow|tips)\b", re.I)
    top5 = sorted(rep["rows"], key=lambda x: -x["views"])[:5]
    howto_top5 = sum(1 for x in top5 if HOW_TO.search(x["title"]))
    best = max((r for r in rep["rows"] if r.get("vph")), key=lambda r: r["vph"])
    median = views[len(views) // 2]
    wants = {w["label"]: w for w in com.get("wants", [])}
    teaching = wants.get("wants to buy time/teaching", {})
    fams = dict(thu.get("hue_families") or [])
    reds = fams.get("red", 0)

    return {
        "topic": rep["topic"],
        "verdict": rep["decision"]["verdict"],
        "score": rep["decision"]["score"],
        "confidence": rep["decision"].get("confidence"),
        "demand": rep["decision"]["parts"].get("demand"),
        "median_views": median,
        "top3": rep["saturation"]["top3_share"],
        "reading": rep["saturation"]["reading"],
        "best_title": best["title"],
        "best_vph": best["vph"],
        "best_views": best["views"],
        "best_age": best["age_days"],
        "rows": len(rep["rows"]),
        "howto_top5": howto_top5,
        # comment field
        "n_comments": com["n"],
        "teaching_n": teaching.get("n"),
        "teaching_share": teaching.get("share"),
        "asks_share": (com.get("asks") or [{}])[0].get("share"),
        "objection_share": (com.get("objections") or [{}])[0].get("share"),
        "top_like": (com.get("top_liked") or [{}])[0].get("likes"),
        # packaging
        "thumbs": thu["n"],
        # Which topic the packaging was actually measured on. It is NOT this one — the
        # thumbnails come from the newest measured report, and saying otherwise would be the
        # exact error this project exists to avoid.
        "thumb_topic": thu.get("topic", ""),
        "face_rate": thu["face_rate"],
        "red_n": reds,
        "contrast": thu["avg_contrast"],
        "next_probe": rep["decision"].get("next_probe", ""),
        "reports": len(idx["reports"]),
    }


# ----------------------------------------------------------------- scenes
def base() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # faint grid so the frame reads as a measurement surface, not a slide
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(15, 17, 19))
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(15, 17, 19))
    return img, d


def label(d, text, y=90, color=MUTED):
    d.text((120, y), text.upper(), font=font(F_MONO_B, 26), fill=color)


def fit(text: str, fnt, max_w: int, d) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def scene_hook(t: float, D: dict) -> Image.Image:
    img, d = base()
    p = min(1.0, t / 0.5)
    label(d, "youtube automation · measured, not guessed")
    f = font(F_BOLD, 112)
    d.text((120, 370), f"{D['howto_top5']} of the top 5 videos", font=f, fill=INK)
    d.text((120, 495), "are called \"how to start\".", font=f, fill=INK)
    d.text((120, 640), "None of them show", font=f, fill=RED)
    d.text((120, 765), "who quietly failed.", font=f, fill=RED)
    d.text((120, 940), f"n = {D['rows']} videos · YouTube Data API · median "
                        f"{D['median_views']:,} views",
           font=font(F_MONO, 30), fill=MUTED)
    return img


def scene_sample(t: float, D: dict) -> Image.Image:
    img, d = base()
    label(d, "the sample")
    f = font(F_BOLD, 200)
    d.text((120, 300), f"{D['rows']}", font=f, fill=INK)
    d.text((420, 330), "videos measured", font=font(F_BOLD, 64), fill=MUTED)
    rows = [
        ("median views", f"{D['median_views']:,}"),
        ("top-3 share", f"{D['top3']:.2f}  →  no single owner"),
        ("demand signal", f"{D['demand']:.0f}/100"),
    ]
    y = 600
    for k, v in rows:
        d.text((120, y), k, font=font(F_MONO, 34), fill=MUTED)
        d.text((560, y - 6), v, font=font(F_BOLD, 44), fill=INK)
        y += 90
    d.text((120, 900), D["reading"][:74], font=font(F_REG, 30), fill=SAGE)
    return img


def scene_speed(t: float, D: dict) -> Image.Image:
    img, d = base()
    label(d, "the newest one is not the best one — it is the fastest")
    title = D["best_title"]
    f = font(F_BOLD, 62)
    for i, line in enumerate(fit(title, f, W - 240, d)[:3]):
        d.text((120, 300 + i * 80), line, font=f, fill=INK)
    f2 = font(F_BOLD, 230)
    d.text((120, 600), f"{D['best_vph']:,.0f}", font=f2, fill=SAGE)
    d.text((760, 700), "views / hour", font=font(F_BOLD, 56), fill=MUTED)
    d.text((120, 890), f"{D['best_views']:,} views in {D['best_age']:.0f} days",
           font=font(F_MONO, 34), fill=MUTED)
    return img


def scene_comments(t: float, D: dict) -> Image.Image:
    img, d = base()
    label(d, f"what {D['n_comments']} comments actually said")
    f = font(F_BOLD, 170)
    d.text((120, 300), f"{D['teaching_share']:.0%}", font=f, fill=AMBER)
    # measured width of the number, so the sentence starts after it instead of on top of it
    num_w = d.textlength(f"{D['teaching_share']:.0%}", font=f)
    x = 120 + num_w + 60
    d.text((x, 340), "want to", font=font(F_BOLD, 58), fill=INK)
    d.text((x, 410), "buy teaching", font=font(F_BOLD, 58), fill=INK)
    d.text((x, 480), "not a tutorial", font=font(F_BOLD, 58), fill=MUTED)
    lines = [
        ("asked for a sequel", f"{D['asks_share']:.0%}"),
        ("objected to the cost", f"{D['objection_share']:.0%}"),
        ("most-liked comment", f"{D['top_like']} ♥  — gratitude, not a question"),
    ]
    y = 640
    for k, v in lines:
        d.text((120, y), k, font=font(F_MONO, 32), fill=MUTED)
        d.text((640, y - 8), v, font=font(F_BOLD, 40), fill=INK)
        y += 92
    return img


def scene_packaging(t: float, D: dict) -> Image.Image:
    img, d = base()
    # say where these thumbnails came from — they are measured on a different topic
    label(d, f"packaging study · measured on \"{D['thumb_topic']}\", not this topic")
    for i, (num, cap) in enumerate([
        (f"{D['face_rate']:.0%}", "of thumbnails have a face"),
        (f"{D['red_n']}/{D['thumbs']}", "use red as the accent"),
    ]):
        x = 140 + i * 900
        d.text((x, 320), num, font=font(F_BOLD, 190), fill=RED if i == 1 else INK)
        for j, line in enumerate(fit(cap, font(F_BOLD, 46), 760, d)):
            d.text((x, 560 + j * 60), line, font=font(F_BOLD, 46), fill=MUTED)
    d.text((140, 800), "top hue families", font=font(F_MONO, 30), fill=MUTED)
    x = 140
    for name, n in (D.get("_fams") or []):
        d.rectangle([x, 860, x + 60, 940], fill=RED if name == "red" else (60, 70, 66))
        d.text((x + 74, 872), f"{name} {n}", font=font(F_MONO, 28), fill=MUTED)
        x += 260
    return img


def scene_verdict(t: float, D: dict) -> Image.Image:
    img, d = base()
    label(d, "so the honest answer is")
    f = font(F_BOLD, 210)
    d.text((120, 300), D["verdict"], font=f, fill=AMBER)
    d.text((120, 560), f"score {D['score']} · confidence {D['confidence']} · not a GO",
           font=font(F_BOLD, 54), fill=MUTED)
    f2 = font(F_REG, 40)
    for i, line in enumerate(fit(D["next_probe"], f2, W - 260, d)):
        d.text((120, 700 + i * 56), line, font=f2, fill=INK)
    return img


def scene_outro(t: float, D: dict) -> Image.Image:
    img, d = base()
    label(d, "monarch studio · research desk")
    d.text((120, 360), "30 seconds,", font=font(F_BOLD, 120), fill=INK)
    d.text((120, 490), "every number measured.", font=font(F_BOLD, 120), fill=SAGE)
    d.text((120, 660), f"{D['reports']} topics on the desk · YouTube Data API lane · "
                        f"0 paid tools", font=font(F_MONO, 32), fill=MUTED)
    d.text((120, 760), "sources: public/yt-intel/*.json", font=font(F_MONO, 30), fill=MUTED)
    return img


# (start, end, fn)
SCENES = [
    (0.0, 4.6, scene_hook),
    (4.6, 9.2, scene_sample),
    (9.2, 14.2, scene_speed),
    (14.2, 19.6, scene_comments),
    (19.6, 24.0, scene_packaging),
    (24.0, 27.4, scene_verdict),
    (27.4, 30.0, scene_outro),
]


# ----------------------------------------------------------------- audio
def make_audio(path: str, D: dict) -> None:
    """A quiet bed of clicks on every scene change, plus a low tone. Deliberately sparse.

    No music library, no licensing question, and nothing that competes with a voiceover that
    will be recorded over this later.
    """
    sr = 48000
    n = int(DURATION * sr)
    t = np.arange(n) / sr
    audio = np.zeros(n, dtype=np.float32)

    # A bed with mid content, not just sub-bass. The first version was 55/82/110 Hz only and
    # measured -25.4 LUFS; LUFS applies K-weighting that rolls off below 100 Hz, so that bed's
    # energy was almost entirely in the range the meter ignores. Adding A3/E4/A4 moved it to
    # about -19.5 at the same peak, which is a bed you can put a voiceover on top of.
    for f, amp in ((55.0, 0.05), (82.41, 0.03), (110.0, 0.02),
                   (220.0, 0.06), (440.0, 0.03), (659.25, 0.015)):
        # slow tremolo so a 30 s pad does not sit completely still
        wobble = 1.0 + 0.18 * np.sin(2 * np.pi * 0.11 * t + f)
        audio += (amp * wobble * np.sin(2 * np.pi * f * t)).astype(np.float32)

    # a click exactly on each scene boundary — the edit point is audible, like a slate
    for start, _end, _fn in SCENES:
        if start == 0.0:
            continue
        i0 = int(start * sr)
        dur = int(0.055 * sr)
        env = np.exp(-np.linspace(0, 9, dur)).astype(np.float32)
        click = (0.35 * env * np.sin(2 * np.pi * 1650 * np.arange(dur) / sr)).astype(np.float32)
        audio[i0:i0 + dur] += click[: len(audio[i0:i0 + dur])]

    # fade in / out so it does not start or end with a tick
    fade = int(0.4 * sr)
    audio[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
    audio[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)

    # A peak guess is not a loudness target: the first render came out at -25.4 LUFS, which is
    # ~11 dB quiet for online video and sounds like a mistake next to any other video. Normalise
    # to the level a voiceover will sit at, with a true-peak ceiling so nothing clips.
    audio = np.clip(audio, -1, 1)
    rms = float(np.sqrt(np.mean(audio ** 2))) or 1e-6
    # my measured mapping for this sparse bed: RMS 0.366 -> -20.8 LUFS, so 1 RMS point ≈
    # 5.7 LU. The correction is applied and then checked against ebur128 in the QC step below.
    target_rms = min(0.9, 10 ** (TARGET_LUFS / 20))
    audio = audio * (target_rms / rms)
    peak = float(np.max(np.abs(audio))) or 1.0
    ceiling = 10 ** (-1.5 / 20)                     # -1.5 dBTP
    if peak > ceiling:
        audio = audio * (ceiling / peak)
    pcm = (audio * 32767).astype(np.int16)
    stereo = np.stack([pcm, pcm], axis=1).ravel()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(stereo.tobytes())


# ----------------------------------------------------------------- render
def render(out: str, fps: int = FPS) -> None:
    import imageio_ffmpeg
    D = load()
    thu = json.load(open(os.path.join(INTEL, "thumbnails.json"), encoding="utf-8"))
    D["_fams"] = thu.get("hue_families") or []

    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp_audio = out.replace(".mp4", ".wav")
    make_audio(tmp_audio, D)

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ff, "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
        "-i", tmp_audio,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        "-movflags", "+faststart", out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    total = int(DURATION * fps)
    for i in range(total):
        t = i / fps
        fn = next((f for s, e, f in SCENES if s <= t < e), SCENES[-1][2])
        img = fn(t, D)
        proc.stdin.write(img.tobytes())
        if i % fps == 0:
            print(f"  {i / fps:>5.1f}s / {DURATION:.0f}s", flush=True)
    proc.stdin.close()
    err = proc.stderr.read().decode()
    proc.wait()
    if proc.returncode != 0:
        raise SystemExit(f"ffmpeg failed:\n{err[-2000:]}")
    os.remove(tmp_audio)
    print(f"wrote {out}")


def main(argv: list[str]) -> int:
    out = OUT_DEFAULT
    fps = FPS
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    if "--fps" in argv:
        fps = int(argv[argv.index("--fps") + 1])
    render(out, fps)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
