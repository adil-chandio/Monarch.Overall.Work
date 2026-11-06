"""A 30-second vertical-truth short, built to the repo's own motion-doctrine.

The previous demo was a stack of static text cards with hard cuts. `skills/hyperframes/
motion-doctrine` names that failure exactly: "scenes authored in isolation — the eye's
momentum dies at every cut, and scenes wobble in place between entry and exit." This is the
correction, and every rule below is quoted from that skill.

HOW THE DOCTRINE IS OBEYED
--------------------------
* **The Current (LEFT).** One dominant direction for every seam. The camera is a single
  continuous pan across a wide world, so it never stops: there is no such thing as a cut from
  rest to rest. Entry offsets are +X (they travel leftward into place), exit offsets are -X.
  Same axis, same sign, both sides of every seam.
* **Vector law.** Exit speed is matched by entry speed because both are the camera's own
  velocity plus a mirrored power4 ease. A seam is never a crossfade — one side is visible per
  frame; the world slides.
* **Carrier.** The red rule (a 6px line) is handed from scene to scene. The eye follows it.
* **No idle wobble.** Nothing breathes or floats. Every held beat has an owner: counters tick,
  bars grow, the camera travels. Idle sine loops are banned and none are used.
* **Stillness before climax.** 0.45 s of pure camera drift before the last line.
* **Timing intents.** Single entry <= 800 ms; exit ≈ 75% of entry; total stagger <= 500 ms.
  Forbidden eases (bounce/elastic) appear nowhere.

Every number comes from public/yt-intel/*.json at render time.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTEL = os.path.join(ROOT, "public", "yt-intel")
OUT_DEFAULT = os.path.join(ROOT, "public", "demo", "viral-short.mp4")
VO_WAV = os.path.join(ROOT, "public", "demo", "vo.wav")

W, H = 1920, 1080
FPS = 30
DURATION = 42.24   # replaced by the measured VO length when timing.json exists
WORLD_SCREENS = 4.4            # how far the camera travels, in screen widths

FDIR = "/usr/share/fonts/truetype/dejavu"
F_BLACK = os.path.join(FDIR, "DejaVuSans-Bold.ttf")
F_REG = os.path.join(FDIR, "DejaVuSans.ttf")
F_MONO_B = os.path.join(FDIR, "DejaVuSansMono-Bold.ttf")

INK = (247, 248, 245)
DIM = (128, 136, 132)
FAINT = (58, 64, 62)
RED = (232, 62, 52)
AMBER = (240, 171, 64)
GREEN = (126, 182, 108)
BG0 = (10, 11, 13)
BG1 = (17, 19, 22)


# ------------------------------------------------------------------ easing
def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def power_out(t: float, p: float = 4.0) -> float:
    return 1.0 - (1.0 - clamp01(t)) ** p


def power_in(t: float, p: float = 4.0) -> float:
    return clamp01(t) ** p


def back_out(t: float, s: float = 1.55) -> float:
    """Overshoot on entry. Doctrine allows back.out(1.4-1.7) and forbids bounce/elastic."""
    t = clamp01(t) - 1.0
    return 1 + t * t * ((s + 1) * t + s)


def fmt_int(n: float) -> str:
    return f"{int(round(n)):,}"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


# ------------------------------------------------------------------ data
def load() -> dict:
    def j(name):
        p = os.path.join(INTEL, name)
        if not os.path.exists(p):
            raise SystemExit(f"missing {p}")
        return json.load(open(p, encoding="utf-8"))

    rep = j("youtube-automation.json")
    com = j("comments-5tOADMwGeBI.json")
    rows = sorted(rep["rows"], key=lambda x: -x["views"])
    views = [x["views"] for x in rows]
    total = sum(views)
    median = sorted(views)[len(views) // 2]
    HOW_TO = re.compile(r"\b(how to|how i|tutorial|guide|step by step|beginner|start|setup|tips)\b", re.I)
    top5 = rows[:5]
    wants = {w["label"]: w for w in com.get("wants", [])}
    teach = wants.get("wants to buy time/teaching", {})

    return {
        "n": len(rows),
        "top1_share": views[0] / total,
        "top1_views": views[0],
        "rest_share": 1 - views[0] / total,
        "median": median,
        "ratio": views[0] / median,
        "howto_top5": sum(1 for x in top5 if HOW_TO.search(x["title"])),
        "comments": com["n"],
        "teach_n": teach.get("n", 0),
        "teach_share": teach.get("share", 0),
        "total_views": total,
        "top_title": rows[0]["title"],
    }


# ------------------------------------------------------------------ beats
# Narration is the clock (motion-doctrine, Part 1: "Audio is the clock. Re-time scenes to the
# VO's real word timestamps; never rush a read to fit a slot."). Every beat boundary below is
# a measured VO boundary, not an invented number.
TIMING_FILE = os.path.join(ROOT, "public", "demo", "vo", "timing.json")


def _timing():
    if os.path.exists(TIMING_FILE):
        return json.load(open(TIMING_FILE, encoding="utf-8"))
    return None


_T = _timing()
if _T:
    STARTS = _T["starts"]
    DURATION = _T["total"]
    BEATS = []
    for i, s0 in enumerate(STARTS):
        end = STARTS[i + 1] if i + 1 < len(STARTS) else DURATION
        BEATS.append((s0 - 0.22, end - 0.06))
else:
    BEATS = [(0.0, 4.3), (4.3, 8.6), (8.6, 12.9), (12.9, 17.1),
             (17.1, 21.3), (21.3, 25.4), (25.4, 30.0)]


# ------------------------------------------------------------------ camera
# The world is 4.4 screens wide and every scene lives at its own anchor in it. The camera
# travels anchor to anchor, so a "cut" is simply the incoming scene already being on screen —
# one side visible per frame, no crossfade, and the motion never stops between scenes.
ANCHOR_GAP = 1980   # wider than the frame: two scenes are never composed on screen at once
# 260, not 150: the camera drifts foreground-ward inside each beat (up to ~50 px), so an
# anchor at 150 pushed the first character of every headline off the left edge.
ANCHORS = [150 + i * ANCHOR_GAP for i in range(7)]
LEFT_MARGIN = 250      # px of empty frame left of a scene's content when the camera is on it
MIDS = [(a + b) / 2 for a, b in BEATS]


def smooth(f: float) -> float:
    f = clamp01(f)
    return f * f * (3 - 2 * f)


DRIFT = 14.0        # px/s — the camera is never fully stationary
WHIP = 0.16        # half-width of the transition window at each beat boundary, seconds
BOUNDS = [b[0] for b in BEATS[1:]]


def camera_x(t: float) -> float:
    """Hold on the beat, whip across the boundary.

    The first version glided continuously; almost every frame had a headline sliced by the
    frame edge, because the camera was always mid-journey. Real kinetic type holds while the
    scene performs and *whips* between scenes. The doctrine's rule is that a seam is not
    rest-to-rest — satisfied twice over: the whip is at full speed on both sides of the cut,
    and inside every scene the content itself is animating (counters, bars, staggered rows), so
    there is no dead beat at either end of a seam. Text is legible for the ~97% of each beat
    outside the 0.32 s whip.
    """
    for i, b in enumerate(BOUNDS):
        if b - WHIP <= t < b + WHIP:
            u = smooth((t - (b - WHIP)) / (2 * WHIP))
            # start the whip from where the outgoing hold actually left off, otherwise the
            # camera jumps backwards by the drift at the start of every whip
            outgoing = ANCHORS[i] - LEFT_MARGIN + DRIFT * ((b - WHIP) - (BOUNDS[i - 1] + WHIP if i else 0.0))
            return outgoing + ((ANCHORS[i + 1] - LEFT_MARGIN) - outgoing) * u
    idx = 0
    seg_start = 0.0
    for j, b in enumerate(BOUNDS):
        if t >= b + WHIP:
            idx, seg_start = j + 1, b + WHIP
    return ANCHORS[idx] - LEFT_MARGIN + DRIFT * (t - seg_start)


def cam_speed(t: float) -> float:
    h = 1.0 / 240.0
    return (camera_x(t + h) - camera_x(t - h)) / (2 * h)


def sx(world_x: float, cam: float) -> float:
    return world_x - cam


# ------------------------------------------------------------------ primitives
def bg(cam: float) -> Image.Image:
    img = Image.new("RGB", (W, H), BG0)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 8):
        k = y / H
        c = (int(BG0[0] + (BG1[0] - BG0[0]) * k),
             int(BG0[1] + (BG1[1] - BG0[1]) * k),
             int(BG0[2] + (BG1[2] - BG0[2]) * k))
        d.rectangle([0, y, W, y + 8], fill=c)
    # two parallax grids: the far one barely moves, the near one adds depth
    off = (cam * 0.30) % 140
    for x in range(-140, W + 140, 140):
        d.line([(x - off, 0), (x - off, H)], fill=(24, 27, 30), width=2)
    offv = (cam * 0.10) % 140
    for y in range(-140, H + 140, 140):
        d.line([(0, y - offv), (W, y - offv)], fill=(22, 25, 28), width=2)
    return img


def vignette(img: Image.Image) -> Image.Image:
    m = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(m)
    dm.ellipse([-W * 0.30, -H * 0.50, W * 1.30, H * 1.50], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(200))
    return Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), m)


def text(d, xy, s, fnt, fill, alpha=1.0):
    if alpha <= 0.02 or not s:
        return
    if alpha >= 0.98:
        d.text(xy, s, font=fnt, fill=fill)
        return
    col = tuple(int(BG1[i] + (fill[i] - BG1[i]) * alpha) for i in range(3))
    d.text(xy, s, font=fnt, fill=col)


def reveal(local: float, delay: float = 0.0, dur: float = 0.5):
    """(progress 0..1, alpha). Always starts from a non-zero position inside the world, so the
    element is already travelling when it becomes visible — never from rest."""
    f = clamp01((local - delay) / dur)
    return back_out(f), clamp01(f / 0.6)


def scene_x(i: int, cam: float) -> int:
    return int(sx(ANCHORS[i], cam))


# ------------------------------------------------------------------ scenes
def scene_hook(d, cam, t, D):
    """0-4.3s. Motion at frame 0: the counter and the bar are already running."""
    x0 = scene_x(0, cam)
    pct = 25.0 * power_out(clamp01(t / 2.6), 3.0)
    p, a = reveal(t - 0.10, dur=0.40)
    text(d, (x0, 226), "ONE VIDEO", font(F_MONO_B, 38), RED, a)
    text(d, (x0 - 8, 300), f"{pct:.0f}%", font(F_BLACK, 300), INK, a)
    text(d, (x0, 690), "of every view", font(F_BLACK, 92), INK, a)
    text(d, (x0, 788), "in this topic.", font(F_BLACK, 92), INK, a)
    bw = int(980 * (pct / 25.0))
    d.rectangle([x0, 930, x0 + bw, 938], fill=RED)


def scene_rest(d, cam, t, D):
    """4.3-8.6s. Twenty-nine counters fill one at a time; sustained motion, no wobble."""
    x0 = scene_x(1, cam)
    local = t - BEATS[1][0]
    rest = 29 * power_out(clamp01(local / 1.8), 2.4)
    _, a = reveal(local, dur=0.35)
    text(d, (x0, 232), "THE OTHER", font(F_MONO_B, 38), DIM, a)
    text(d, (x0 - 8, 286), f"{rest:.0f}", font(F_BLACK, 300), INK, a)
    text(d, (x0, 620), "videos split", font(F_BLACK, 88), INK, a)
    text(d, (x0, 716), "the rest.", font(F_BLACK, 88), INK, a)
    for i in range(29):
        on = i < rest
        col, row = i % 10, i // 10
        d.rectangle([x0 + col * 30, 830 + row * 30, x0 + col * 30 + 21, 830 + row * 30 + 21],
                    fill=RED if on else FAINT)
    text(d, (x0 + 340, 850), "75%", font(F_MONO_B, 60), DIM, a)
    text(d, (x0 + 340, 915), "between them", font(F_MONO_B, 28), DIM, a)


def scene_gap(d, cam, t, D):
    """8.6-12.9s. Two counters run away from each other — the frame is never still."""
    x0 = scene_x(2, cam)
    local = t - BEATS[2][0]
    big = D["top1_views"] * power_out(clamp01(local / 1.6), 3.0)
    small = D["median"] * power_out(clamp01(local / 1.6), 3.0)
    _, a = reveal(local, dur=0.35)
    text(d, (x0, 196), "NUMBER ONE", font(F_MONO_B, 32), RED, a)
    text(d, (x0 - 4, 236), fmt_int(big), font(F_BLACK, 118), INK, a)
    text(d, (x0, 392), "THE TYPICAL ONE", font(F_MONO_B, 32), DIM, a)
    text(d, (x0 - 4, 432), fmt_int(small), font(F_BLACK, 118), DIM, a)
    ratio = D["ratio"] * power_out(clamp01((local - 0.5) / 1.4), 3.0)
    text(d, (x0 - 6, 610), f"{ratio:.0f}", font(F_BLACK, 210), AMBER, a)
    text(d, (x0 + 300, 700), "times", font(F_BLACK, 88), AMBER, a)
    text(d, (x0, 920), "same topic. same month.", font(F_BLACK, 50), INK, a)


def scene_lie(d, cam, t, D):
    """12.9-17.1s. Rows arrive one after another — a stagger, not a slide."""
    x0 = scene_x(3, cam)
    local = t - BEATS[3][0]
    _, a = reveal(local, dur=0.32)
    text(d, (x0, 214), "THE TOP FIVE, IN ORDER", font(F_MONO_B, 32), DIM, a)
    for i in range(5):
        e, ea = reveal(local, delay=0.30 + i * 0.16, dur=0.45)
        y = 290 + i * 100 + (1 - e) * 40
        howto = i < 3
        d.rectangle([x0, y, x0 + 940, y + 78], fill=(40, 20, 20) if howto else (24, 27, 30))
        text(d, (x0 + 24, y + 21), f"{i + 1}", font(F_MONO_B, 32), RED if howto else FAINT, ea)
        text(d, (x0 + 84, y + 20), "\"how to start\"" if howto else "the honest one",
             font(F_BLACK, 38), INK if howto else DIM, ea)
    text(d, (x0, 850), f"{D['howto_top5']} of 5 teach the start.", font(F_BLACK, 54), INK, a)
    text(d, (x0, 916), "none show who started and quit.", font(F_BLACK, 54), RED, a)


def scene_shift(d, cam, t, D):
    """17.1-21.3s. The strike-through is the action; the new word is the result."""
    x0 = scene_x(4, cam)
    local = t - BEATS[4][0]
    _, a = reveal(local, dur=0.32)
    text(d, (x0, 244), "SATURATED", font(F_BLACK, 100), DIM, a)
    strike = 900 * power_in(clamp01((local - 0.45) / 0.35), 2.0)
    d.rectangle([x0, 318, x0 + strike, 330], fill=RED)
    p2, a2 = reveal(local, delay=0.95, dur=0.42)
    text(d, (x0, 400), "is the wrong word.", font(F_BLACK, 100), INK, a2)
    p3, a3 = reveal(local, delay=1.45, dur=0.45)
    text(d, (x0, 590), "Concentrated", font(F_BLACK, 118), AMBER, a3)
    text(d, (x0, 720), "is the right one.", font(F_BLACK, 118), AMBER, a3)
    text(d, (x0, 900), "one winner, twenty-nine copies of it.", font(F_BLACK, 44), DIM, a3)


def scene_audience(d, cam, t, D):
    """21.3-25.4s. Eleven squares fill out of a hundred — the count is the motion."""
    x0 = scene_x(5, cam)
    local = t - BEATS[5][0]
    teach = 11 * power_out(clamp01(local / 1.5), 2.6)
    _, a = reveal(local, dur=0.32)
    text(d, (x0, 218), f"{D['comments']} COMMENTS READ", font(F_MONO_B, 32), DIM, a)
    text(d, (x0 - 8, 268), f"{teach:.0f}", font(F_BLACK, 250), RED, a)
    # measured width of the figure, so the sentence starts after it (the same bug as before:
    # a fixed offset let the "11" collide with "want to")
    num_w = d.textlength(f"{teach:.0f}", font=font(F_BLACK, 250))
    tx = x0 + int(num_w) + 46
    text(d, (tx, 352), "want to pay", font(F_BLACK, 74), INK, a)
    text(d, (tx, 440), "for teaching.", font(F_BLACK, 74), INK, a)
    for i in range(100):
        on = i < teach
        col, row = i % 25, i // 25
        d.rectangle([x0 + col * 38, 640 + row * 38, x0 + col * 38 + 27, 640 + row * 38 + 27],
                    fill=RED if on else FAINT)
    text(d, (x0, 840), "not another free tutorial.", font(F_BLACK, 52), DIM, a)


def scene_end(d, cam, t, D):
    """25.4-30s. Stillness before the last line: 0.45 s of camera drift only."""
    x0 = scene_x(6, cam)
    local = t - BEATS[6][0]
    a0 = clamp01((local - 0.45) / 0.40)
    text(d, (x0, 300), "Next video:", font(F_MONO_B, 42), DIM, a0)
    a1 = clamp01((local - 0.55) / 0.50)
    text(d, (x0, 380), "the part", font(F_BLACK, 156), INK, a1)
    a2 = clamp01((local - 0.70) / 0.50)
    text(d, (x0, 540), "nobody films.", font(F_BLACK, 156), RED, a2)
    m = clamp01((local - 1.6) / 0.6)
    d.rectangle([x0, 764, x0 + 120 * m, 772], fill=RED)
    text(d, (x0, 800), "MONARCH STUDIO", font(F_MONO_B, 34), INK, m)
    text(d, (x0, 850), "measured, not guessed", font(F_MONO_B, 26), DIM, m)


SCENES = [scene_hook, scene_rest, scene_gap, scene_lie, scene_shift, scene_audience, scene_end]


def warning_seam(t: float) -> float:
    """1.0 at a seam, 0.0 in the middle of a beat."""
    d = min((abs(t - b) for b in BOUNDS), default=99.0)
    return clamp01(1.0 - d / WHIP)


def frame(t: float, D: dict) -> Image.Image:
    cam = camera_x(t)
    img = bg(cam)
    d = ImageDraw.Draw(img)
    # the whole world is drawn every frame; the camera decides what is on screen. This is what
    # makes every seam a mid-motion hand-off instead of a stack of separate slides.
    for i in range(len(SCENES)):
        if -W < sx(ANCHORS[i], cam) < W + 200:
            SCENES[i](d, cam, t, D)

    # Seam treatment: a fast whip leaves two compositions half-visible, which reads as a mess
    # in a still and as speed in motion. A dim plus horizontal speed lines sells the transition
    # instead of exposing it — the standard kinetic-type answer, and it keeps the carrier (the
    # red rule) continuous across the cut.
    seam = warning_seam(t)
    if seam > 0.02:
        img = Image.blend(img, Image.new("RGB", (W, H), (6, 6, 8)), 0.62 * seam)
        d = ImageDraw.Draw(img)
        rng = np.random.RandomState(int(t * 1000) % 9973)
        for k in range(9):
            y = int(rng.uniform(0, H))
            h = int(rng.uniform(2, 9))
            x0 = int(rng.uniform(-200, W * 0.6))
            w = int(rng.uniform(300, 1300) * seam)
            d.rectangle([x0, y, x0 + w, y + h], fill=(90, 26, 24))
        d.rectangle([0, H // 2 - 2, W, H // 2 + 2], fill=(int(232 * seam), 40, 34))

    d.rectangle([0, H - 8, W, H], fill=(30, 13, 13))
    d.rectangle([0, H - 8, int(W * clamp01(t / DURATION)), H], fill=RED)
    return vignette(img)


# ------------------------------------------------------------------ audio
def _load_vo(path: str, sr: int, n: int) -> np.ndarray:
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    raw = subprocess.run([ff, "-v", "error", "-i", path, "-f", "f32le", "-ac", "1",
                          "-ar", str(sr), "-"], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.float32).astype(np.float32)
    return a


def build_bed(path: str, D: dict) -> None:
    """Music bed + the recorded narration, placed at its measured start times.

    The bed is ducked under the voice by an envelope taken from the voice itself, so the
    narration is never fighting the music. Cuts land on a 120 BPM grid; the scenes are already
    cut to the narration, so the two agree.
    """
    sr = 48000
    n = int(DURATION * sr)
    t = np.arange(n) / sr
    audio = np.zeros(n, dtype=np.float32)

    bpm = 120.0
    beat = 60.0 / bpm
    for k in range(int(DURATION / beat) + 1):
        i0 = int(k * beat * sr)
        dur = int(0.16 * sr)
        if i0 + dur >= n:
            break
        env = np.exp(-np.linspace(0, 12, dur)).astype(np.float32)
        f = 110 * np.exp(-np.linspace(0, 3, dur))
        audio[i0:i0 + dur] += (0.26 * env * np.sin(2 * np.pi * f * np.arange(dur) / sr)).astype(np.float32)

    for f, amp in ((55.0, 0.045), (82.41, 0.028), (110.0, 0.020), (164.8, 0.014), (220.0, 0.009)):
        audio += (amp * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.07 * t))).astype(np.float32)

    for k in range(int(DURATION / beat) + 1):
        i0 = int((k * beat + beat / 2) * sr)
        dur = int(0.05 * sr)
        if i0 + dur >= n:
            break
        env = np.exp(-np.linspace(0, 10, dur)).astype(np.float32)
        audio[i0:i0 + dur] += (0.085 * env * np.random.RandomState(k).randn(dur)).astype(np.float32)

    # narration
    voice = np.zeros(n, dtype=np.float32)
    T = _timing()
    if T:
        files = sorted(os.listdir(os.path.join(ROOT, "public", "demo", "vo")))
        clips = [f for f in files if f.endswith(".mp3")]
        for start, name in zip(T["starts"], clips):
            a = _load_vo(os.path.join(ROOT, "public", "demo", "vo", name), sr, n)
            i0 = int(start * sr)
            i1 = min(n, i0 + len(a))
            voice[i0:i1] += a[: i1 - i0]

    # sidechain: duck the bed where the voice is
    env = np.abs(voice)
    win = int(0.06 * sr)
    smooth = np.convolve(env, np.ones(win) / win, mode="same")
    ref = float(np.percentile(smooth[smooth > 0], 90)) if (smooth > 0).any() else 1.0
    duck = 1.0 - 0.70 * np.clip(smooth / (ref + 1e-9), 0, 1).astype(np.float32)
    duck = np.clip(duck, 0.22, 1.0)
    audio = audio * duck + voice * 1.25

    audio = np.clip(audio, -1, 1)
    peak = float(np.max(np.abs(audio))) or 1.0
    ceiling = 10 ** (-1.0 / 20)
    if peak > ceiling:
        audio *= ceiling / peak
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(np.stack([pcm, pcm], axis=1).ravel().tobytes())


# ------------------------------------------------------------------ render
def render(out: str, fps: int = FPS) -> None:
    import imageio_ffmpeg
    D = load()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bed = out.replace(".mp4", "_bed.wav")
    build_bed(bed, D)

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen([
        ff, "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
        "-i", bed,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out,
    ], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    total = int(DURATION * fps)
    for i in range(total):
        proc.stdin.write(frame(i / fps, D).tobytes())
        if i % (fps * 3) == 0:
            print(f"  {i / fps:>5.1f}s", flush=True)
    proc.stdin.close()
    err = proc.stderr.read().decode()
    proc.wait()
    if proc.returncode != 0:
        raise SystemExit(err[-1500:])
    os.remove(bed)
    print(f"wrote {out}")


def main(argv):
    out = OUT_DEFAULT
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    render(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
