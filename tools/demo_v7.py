"""v7 proof demo: 8 s clip showing the new camera system + the new sound design.

Picture: handheld drift + smooth multi-sine jitter + crash-zoom punches on the beat,
cash ghost at a different depth (parallax), bouncy glass pill.
Sound:   120 bpm -- kick + 808 + hats + snare, sidechain pump, whoosh, sub drop, crash.
Built only from our own plates and procedural audio (no reference material).
"""
import json, math, subprocess, sys
import numpy as np
import cv2
import v6 as V
from v6 import H, W, rgb, ease, lerp, lin, pop, place_px, grain, vignette
from ffbin import ffmpeg

FPS = 30
DUR = 8.0
N = int(FPS * DUR)
BEATS = [0.5, 2.5, 4.0, 6.0]          # punch moments (2.5 = pill, 4.0 = sub drop)
PH = (1.7, 4.2, 2.9, 0.6, 5.1, 3.3)    # jitter phases, fixed


def scene_demo(f, t, u):
    p = ease(u, "smooth")
    V.red_room(f, t, u, push=1.05 + 0.07 * p,
               orbit_x=lerp(-40, 50, p), orbit_y=lerp(20, -24, p),
               yaw=lerp(-8.0, 5.5, p), pitch=lerp(2.2, -1.6, p), year=0.32)
    V.glow(f, V.T.get("lens"), t)
    # cash ghost, own depth, pops with the sub drop
    hp = pop(t, 4.0, 0.34, back=2.6)
    if hp > 0:
        place_px(f, V.T["cash"], 760.0, 320, 452 + 46 * (1 - min(hp, 1.0)),
                 300 - 22 * min(hp, 1.0), 0.0, opacity=min(hp, 1.0) * 0.9,
                 blur=lerp(7.0, 0.0, min(hp, 1.0)), yaw=lerp(14, 4, min(hp, 1.0)), pitch=-5.0)
    a = pop(t, 2.5, 0.30, back=2.2)
    if a > 0:
        V.card_pill(f, 232, lerp(966, 906, min(a, 1.0)), min(a, 1.0), "SUBSCRIBE", "LIKE", 268)
    vignette(f, 0.46)


LKX, LKY = 0.44, 0.42        # the look point the camera keeps on the man


def camera(f, t):
    """The new layer: smooth drift + jitter + beat punches, applied last.

    AE's "camera on a large layer" model: render zoomed up (z >= 1) and crop a 720x1280
    window from it. A crop never exposes edges and costs one resize + one slice, so it
    stays fast even on this 2-core box (warpAffine collapses to ~15 s/frame under load).
    """
    z = 1.0 + 0.045 * (t / DUR)                          # slow push-in over the shot
    z += 0.050 * math.exp(-t / 0.40)                     # opening settle from a punch
    for b in BEATS:                                     # crash-zoom punches on the beat
        if t >= b:
            z += 0.050 * math.exp(-(t - b) / 0.09)
    jx = 1.8 * math.sin(2 * math.pi * 7.3 * t + PH[0]) \
         + 1.1 * math.sin(2 * math.pi * 11.7 * t + PH[1]) \
         + 0.6 * math.sin(2 * math.pi * 17.1 * t + PH[2])
    jy = 1.4 * math.sin(2 * math.pi * 8.9 * t + PH[3]) \
         + 0.8 * math.sin(2 * math.pi * 13.3 * t + PH[4])
    # drift is clamped to the travel room the zoom provides, so the crop stays in bounds
    room_x = (z - 1) * W * 0.9; room_y = (z - 1) * H * 0.9
    dx = max(-room_x, min(room_x, -6.0 * t + jx))
    dy = max(-room_y, min(room_y, 5.0 * math.sin(2 * math.pi * 0.08 * t) + jy))
    f8 = np.clip(f, 0, 255).astype(np.uint8)
    sw, sh = int(round(W * z)), int(round(H * z))
    g = cv2.resize(f8, (sw, sh), interpolation=cv2.INTER_LINEAR)
    # window centred on the look point, then drifted
    cx0 = int(round(sw * LKX - W / 2 + dx))
    cy0 = int(round(sh * LKY - H / 2 + dy))
    cx0 = max(0, min(sw - W, cx0)); cy0 = max(0, min(sh - H, cy0))
    return g[cy0:cy0 + H, cx0:cx0 + W].copy()


# ---------------------------------------------------------------- audio
SR = 48000
def one_pole(x, fc):
    a = 1 - math.exp(-2 * math.pi * fc / SR)
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y

def add(buf, sig, t0, pan=0.0):
    i0 = int(t0 * SR)
    n = min(len(sig), len(buf) - i0)
    if n <= 0: return
    l = (1 - pan) * 0.7071; r = (1 + pan) * 0.7071
    buf[i0:i0 + n, 0] += sig[:n] * l
    buf[i0:i0 + n, 1] += sig[:n] * r

def kick(t0):
    n = int(0.22 * SR); t = np.arange(n) / SR
    f = 52 * (30 / 52) ** (t / 0.16)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.10)
    _c = np.random.randn(int(0.004 * SR))
    click = _c * np.exp(-np.arange(len(_c)) / (0.001 * SR))
    s = s * 0.95 + np.concatenate([one_pole(click, 4000) * 0.4, np.zeros(len(s) - len(click))])
    return s

def note808(t0, f0, dur=0.42, glide=0.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 * (f0 - glide) ** (t / dur) if glide else np.full(n, f0)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - np.exp(-t / 0.004)) * np.exp(-t / 0.30)
    return s * 0.85

def hat(t0, v=1.0):
    n = int(0.03 * SR)
    s = np.random.randn(n) * np.exp(-np.arange(n) / (0.006 * SR))
    return one_pole(s, 7500) * 0.30 * v

def snare(t0):
    n = int(0.16 * SR); t = np.arange(n) / SR
    s = (np.random.randn(n) * 0.7 + np.sin(2 * np.pi * 190 * t) * 0.5) * np.exp(-t / 0.07)
    return one_pole(s, 2100) * 0.5 + s * 0.18

def whoosh(t0, dur=0.55, f0=300, f1=4200, amp=0.8):
    n = int(dur * SR); out = np.zeros(n)
    hop = int(0.03 * SR); win = np.hanning(hop)
    for k in range(n // hop):
        seg = np.random.randn(hop); X = np.fft.rfft(seg * win)
        fr = np.fft.rfftfreq(hop, 1 / SR)
        c = f0 * (f1 / f0) ** (k * hop / n); wdt = max(120.0, 0.45 * c)
        X *= np.exp(-((fr - c) ** 2) / (2 * wdt ** 2))
        out[k * hop:k * hop + hop] += np.fft.irfft(X, hop) * win / 0.5
    return out * np.exp(-np.arange(n) / (0.35 * n)) * amp

def subdrop(t0):
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = 90 * (18 / 90) ** (np.minimum(t, 0.35) / 0.35)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    return s * 1.25

def crash(t0):
    n = int(0.9 * SR); t = np.arange(n) / SR
    s = np.random.randn(n) * np.exp(-t / 0.28)
    return one_pole(s, 5200) * 0.5

def build_audio():
    buf = np.zeros((int(SR * (DUR + 0.6)), 2))
    beat = 0.5
    nbeats = int(DUR / beat)
    # 808 line (D minor): 2 notes per bar
    notes = [73.42, 73.42, 65.41, 87.31, 65.41, 73.42, 87.31, 73.42, 65.41, 65.41, 58.27, 65.41]
    for k in range(len(notes)):
        t0 = k * beat
        if t0 < DUR - 0.3:
            add(buf, note808(t0, notes[k], glide=12.0), t0)
    for k in range(nbeats + 1):
        t0 = k * beat
        if t0 >= DUR: break
        add(buf, kick(t0), t0)
        if k >= 4:  # hats enter on the build
            for j in range(4):
                v = [1.0, 0.5, 0.8, 0.55][(j + k) % 4]
                add(buf, hat(t0 + j * beat / 4, v), t0 + j * beat / 4, pan=[-0.3, 0.3, 0, 0.2][j % 4])
        if k % 2 == 1 and k >= 3:
            add(buf, snare(t0), t0, pan=0.15)
    # hat roll into the fade
    for j in range(8):
        add(buf, hat(6.0 + j * 0.0625, 1.0 - j * 0.07), 6.0 + j * 0.0625)
    # pad (wide)
    n = int(SR * DUR)
    t = np.arange(n) / SR
    chord = (0.5 * np.sin(2 * np.pi * 146.83 * t) + 0.42 * np.sin(2 * np.pi * 174.61 * t) +
             0.42 * np.sin(2 * np.pi * 220.0 * t) + 0.25 * np.sin(2 * np.pi * 261.63 * t))
    chord = one_pole(chord, 1400) * 0.13 * np.minimum(t / 0.8, 1.0)
    add(buf, chord, 0.0, pan=-0.4); add(buf, chord, 0.0, pan=0.4)
    # the events
    add(buf, whoosh(0.0, amp=0.9), 2.95)
    add(buf, subdrop(0.0), 4.0)
    add(buf, kick(0.0) * 1.1, 4.0)
    add(buf, whoosh(0.0, dur=0.4, f0=200, f1=900, amp=0.5), 4.80)
    add(buf, crash(0.0), 5.0, pan=0.25)
    # sidechain pump on everything except 808/sub: apply to a copy (approx: dip the mix)
    out = buf.copy()
    pump = np.ones(len(out))
    for k in range(nbeats + 1):
        t0 = k * beat
        seg = slice(int(t0 * SR), int(t0 * SR) + int(0.3 * SR))
        tt = np.arange(seg.stop - seg.start) / SR
        pump[seg] = np.minimum(pump[seg], 1 - 0.30 * np.exp(-tt / 0.11))
    out *= pump[:, None]
    # fade out
    fl = np.ones(len(out)); i1 = int((DUR - 0.4) * SR)
    fl[i1:] = np.linspace(1, 0, len(out) - i1)
    out *= fl[:, None]
    out = np.tanh(out * 1.4)
    pk = np.abs(out).max()
    out = out / pk * (10 ** (-0.5 / 20))
    return out[: int(SR * DUR)]

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "spec/v5-02.json"))
    V.prepare(spec)
    ff = ffmpeg()
    audio = build_audio()
    wav = (audio * 32767).astype("<i2").tobytes()
    # render video
    proc = subprocess.Popen([ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "fast", "-crf", "17",
                             "-pix_fmt", "yuv420p", "-an", "/tmp/forensic/demo_v.mp4"],
                            stdin=subprocess.PIPE)
    import time
    t0 = time.time()
    for i in range(N):
        t = i / FPS
        f = np.zeros((H, W, 3), np.float32)
        scene_demo(f, t, i / N)
        grain(f, 1.0, i * 7919 + 13)
        f = camera(f, t)
        proc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
        if i % 30 == 0:
            print(f"frame {i}/{N}  {time.time() - t0:.0f}s", flush=True)
    proc.stdin.close(); proc.wait()
    print(f"video {N} frames in {time.time() - t0:.0f}s", flush=True)
    subprocess.run([ff, "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2",
                    "-i", "pipe:0", "-c:a", "aac", "-b:a", "192k", "/tmp/forensic/demo_a.m4a"],
                   input=wav, check=True)
    subprocess.run([ff, "-v", "error", "-y", "-i", "/tmp/forensic/demo_v.mp4",
                    "-i", "/tmp/forensic/demo_a.m4a", "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", "public/demo/v7-preview.mp4"], check=True)
    print("wrote public/demo/v7-preview.mp4")
