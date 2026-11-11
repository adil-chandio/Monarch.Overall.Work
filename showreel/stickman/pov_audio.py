"""The sound of "POV: the stadium goes quiet".

    python -m showreel.stickman.pov_audio [--out deliverables/pov-stadium.wav]

Ninety seconds of stereo at 48 kHz, synthesised from the film's own state. There is
no library here and no licence to argue about: a crowd is noise with a shape, an
impact is a low sweep plus a crack, and a stadium that goes quiet is the same crowd
with its gain taken to zero and a room left behind it.

The rule the whole mix obeys: **nothing is triggered by a clock, everything is
triggered by the film.** Footsteps are found by watching the ankles cross the
ground plane in `Pov.state`, the impact is the frame the ball's story clock starts,
and the crowd's gain is `churn` -- the same number that moves the stand in the
picture. If the cut moves, the sound moves with it.

Three decisions worth naming:

**The silence is not silence.** `churn` goes to zero for twenty-nine seconds, and a
digital zero there sounds like a broken file. What is left is room tone at -46 dB
plus the things you can hear in a stadium that has stopped: a heartbeat, boots,
breath, a ball being set down.

**The roar arrives late.** Contact is at 37.30 and the crowd does not come back
until 41.50 -- the ball hits in the quiet, the net swishes in the quiet, and only
then does the room let go. Bringing the noise in on contact throws away the four
seconds that the whole film is built to reach.

**The replay is not the same sound.** It is the same event heard through a
broadcast: the crowd ducked under it, the impact muffled, and a fifth-of-speed
wobble on everything, because a replay is tape and tape is not honest about pitch.
"""

from __future__ import annotations

import argparse
import math
import sys
import wave

import numpy as np

from .pov import CONTACT, GRASS_STEP, QUESTION, SHUSH, TOTAL, Pov
from .film import FPS

SR = 48000
SAMPLE_RATE = SR
TAIL = 0.0


# ------------------------------------------------------------------ utilities

def _n(seconds):
    return int(round(seconds * SR))


def _white(n, seed):
    return np.random.default_rng(seed).standard_normal(n).astype(np.float32)


def _shape(x, breaks):
    """Filter by multiplying the spectrum with a piecewise log-log magnitude.

    A one-pole filter in numpy means a Python loop over four million samples, and a
    convolution with an impulse response costs more than the mix is worth. Shaping
    the spectrum is one FFT and exact.
    """
    n = len(x)
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    fx = np.log(np.maximum(breaks[0][0], freqs.clip(breaks[0][0])))
    lx = np.log(np.array([b[0] for b in breaks], float))
    ly = np.array([b[1] for b in breaks], float)
    gain = np.exp(np.interp(np.log(np.maximum(freqs, breaks[0][0])), lx, ly))
    spec = np.fft.rfft(x)
    spec *= gain
    return np.fft.irfft(spec, n).astype(np.float32)


def _norm(x, rms=0.2):
    r = float(np.sqrt(np.mean(x * x))) or 1.0
    return (x * (rms / r)).astype(np.float32)


def _env(n, pts):
    """Envelope from (time, value) breakpoints; times in seconds."""
    ts = np.array([p[0] for p in pts], float)
    vs = np.array([p[1] for p in pts], float)
    return np.interp(np.arange(n) / SR, ts, vs).astype(np.float32)


def _decay(n, k):
    return np.exp(-np.arange(n) / SR / k).astype(np.float32)


def _mix(dst, t0, sig, gain=1.0, pan=0.0):
    """Add a mono signal into a stereo buffer at ``t0`` with equal-power pan."""
    i = int(round(t0 * SR))
    if i >= dst.shape[1] or i + len(sig) <= 0:
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    m = min(len(sig), dst.shape[1] - i)
    if m <= 0:
        return
    a = (pan + 1.0) * math.pi / 4.0
    dst[0, i:i + m] += sig[:m] * gain * math.cos(a)
    dst[1, i:i + m] += sig[:m] * gain * math.sin(a)


# ------------------------------------------------------------------- elements

def crowd_bed(n, seed=5):
    """Three layers: a wide roar, voices inside it, and a rumble underneath."""
    wide = _norm(_shape(_white(n, seed), [
        (25, -13.0), (90, -5.0), (250, -1.0), (700, 0.0), (1600, -1.2),
        (3200, -5.0), (7000, -11.0), (18000, -20.0)]), 0.25)
    voices = _norm(_shape(_white(n, seed + 1), [
        (140, -14.0), (420, -2.0), (900, -0.6), (1500, 0.0), (2600, -4.0),
        (5000, -13.0), (12000, -22.0)]), 0.20)
    rumble = _norm(_shape(_white(n, seed + 2), [
        (18, -3.0), (50, 0.0), (110, -2.0), (240, -12.0), (600, -26.0)]), 0.30)
    return [wide, voices, rumble]


def slow_lfo(n, seed, rate=0.35):
    """A very slow random envelope: a crowd swells, it does not sit still."""
    m = max(2, int(n / SR * rate) + 4)
    rng = np.random.default_rng(seed)
    pts = rng.random(m).astype(np.float32)
    return np.interp(np.linspace(0, m - 1, n), np.arange(m), pts).astype(np.float32)


def thump(dur=0.34, f0=95.0, f1=42.0, seed=3):
    n = _n(dur)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / dur) ** 0.6
    phase = 2.0 * math.pi * np.cumsum(f) / SR
    body = np.sin(phase) * _decay(n, dur * 0.22)
    click = _white(n, seed) * _decay(n, 0.0018) * 0.5
    return (body + click).astype(np.float32)


def crack(dur=0.075, seed=4):
    n = _n(dur)
    x = _shape(_white(n, seed), [(400, -18.0), (1500, 0.0), (5000, -2.0),
                                 (12000, -14.0)])
    return _norm(x * _decay(n, 0.012), 0.3)


def swish(dur=0.5, seed=6):
    n = _n(dur)
    x = _shape(_white(n, seed), [(300, -22.0), (900, -4.0), (2200, 0.0),
                                 (5200, -3.0), (11000, -18.0)])
    env = _env(n, [(0.0, 0.0), (dur * 0.18, 1.0), (dur * 0.45, 0.7),
                   (dur, 0.0)])
    return _norm(x * env, 0.28)


def foot(dur=0.17, seed=7, hard=False):
    n = _n(dur)
    scuff = _shape(_white(n, seed), [(180, -6.0), (700, 0.0), (2400, -6.0),
                                     (7000, -18.0)])
    scuff = _norm(scuff * _decay(n, 0.016), 0.22)
    body = thump(dur, 120.0 if hard else 85.0, 48.0, seed + 1) * 0.5
    m = min(len(body), n)
    return (scuff[:m] + body[:m]).astype(np.float32)


def whistle(dur=0.24):
    n = _n(dur)
    t = np.arange(n) / SR
    vib = 1.0 + 0.012 * np.sin(2.0 * math.pi * 31.0 * t)
    s = (np.sin(2 * math.pi * 2680 * t * vib)
         + 0.7 * np.sin(2 * math.pi * 3140 * t * vib))
    env = _env(n, [(0.0, 0.0), (0.012, 1.0), (dur * 0.75, 0.9), (dur, 0.0)])
    return _norm(s * env, 0.16)


def heart(seed=8):
    n = _n(0.34)
    a = np.sin(2 * math.pi * (52.0) * np.arange(n) / SR) * _decay(n, 0.055)
    b = np.sin(2 * math.pi * (44.0) * np.arange(_n(0.20)) / SR) * _decay(_n(0.20), 0.045)
    out = np.zeros(n, np.float32)
    out += a.astype(np.float32)
    k = _n(0.155)
    m = min(len(b), n - k)
    out[k:k + m] += b[:m].astype(np.float32) * 0.72
    return _norm(out, 0.5)


def clap(dur=0.9, seed=9):
    n = _n(dur)
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(seed)
    for _ in range(14):
        i = int(rng.random() * (n - _n(0.03)))
        out[i:i + _n(0.03)] += _shape(_white(_n(0.03), int(rng.integers(1e6))),
                                      [(500, -8.0), (2000, 0.0), (6000, -10.0)])
    return _norm(out, 0.16)


def shush(dur=0.62, seed=10):
    n = _n(dur)
    x = _shape(_white(n, seed), [(700, -20.0), (1800, -2.0), (3600, 0.0),
                                 (7000, -8.0), (14000, -22.0)])
    env = _env(n, [(0.0, 0.0), (0.10, 0.85), (0.30, 0.55), (dur, 0.0)])
    return _norm(x * env, 0.10)


def riser(dur=2.1, seed=11):
    n = _n(dur)
    lo = _shape(_white(n, seed), [(120, -6.0), (600, 0.0), (2000, -10.0)])
    hi = _shape(_white(n, seed + 1), [(900, -14.0), (3000, 0.0), (9000, -6.0)])
    t = np.linspace(0.0, 1.0, n).astype(np.float32)
    x = lo * (1.0 - t) ** 2 + hi * t ** 2
    return _norm(x * (t ** 1.6), 0.16)


def sub_drop(dur=1.3):
    n = _n(dur)
    t = np.arange(n) / SR
    f = 72.0 * np.exp(-t / 0.36) + 26.0
    return _norm(np.sin(2 * math.pi * np.cumsum(f) / SR) * _decay(n, 0.5), 0.34)


def note(freq, dur=1.9):
    n = _n(dur)
    tt = np.arange(n) / SR
    x = (np.sin(2 * math.pi * freq * tt)
         + 0.35 * np.sin(2 * math.pi * freq * 2 * tt)
         + 0.12 * np.sin(2 * math.pi * freq * 3 * tt))
    env = _env(n, [(0.0, 0.0), (0.006, 1.0), (0.5, 0.35), (dur, 0.0)])
    return _norm(x * env, 0.18)


# ------------------------------------------------------------------ the score

def track_film(fps=200.0):
    """Walk the film and record what the mix needs to know.

    One pass at 200 Hz. Every number the sound uses -- the crowd's gain, where the
    feet land, when the ball's clock starts -- comes out of this, so the mix cannot
    drift away from the cut.
    """
    pov = Pov()
    ts = np.arange(0.0, TOTAL, 1.0 / fps)
    churn = np.zeros(len(ts), np.float32)
    steps = []
    prev = {"near": None, "far": None}
    for i, t in enumerate(ts):
        s = pov.state(float(t))
        churn[i] = s["churn"]
        h = s["hero"]
        if h is None:
            prev = {"near": None, "far": None}
            continue
        for side in ("near", "far"):
            y = float(getattr(h, "ankle_" + side)[1])
            p = prev[side]
            if p is not None and p < -8.0 <= y:
                steps.append((float(t), side, abs(p - y)))
            prev[side] = y
    return ts, churn, steps


def build(verbose=True):
    n = _n(TOTAL)
    ts, churn, steps = track_film()
    if verbose:
        print(f"  tracked {len(ts)} film states, {len(steps)} footfalls", flush=True)

    t = np.arange(n) / SR
    crowd_gain = np.interp(t, ts, churn).astype(np.float32)
    # The tunnel eats the top of the crowd until the aperture is open.
    tunnel = np.interp(t, [0.0, 4.6, 6.4], [0.35, 0.45, 1.0]).astype(np.float32)

    out = np.zeros((2, n), np.float32)
    wide, voices, rumble = crowd_bed(n)
    for i, layer in enumerate((wide, voices, rumble)):
        lfo = slow_lfo(n, 40 + i, rate=0.22 + 0.13 * i)
        lfo = 0.72 + 0.46 * lfo
        gain = (1.0, 0.55, 0.75)[i]
        g = (crowd_gain * tunnel * lfo * gain).astype(np.float32)
        if i == 1:
            # Voices are slightly right of centre and slightly behind: one stereo
            # image, not three mono copies of the same noise.
            out[0] += layer * g * 0.80
            out[1] += layer * g * 1.00
        elif i == 2:
            out[0] += layer * g
            out[1] += layer * g
        else:
            out[0] += layer * g * 1.00
            out[1] += layer * g * 0.86

    # -- room tone: what is left when the crowd stops --------------------
    room = _norm(_shape(_white(n, 21), [(30, -8.0), (180, 0.0), (600, -4.0),
                                        (2000, -18.0)]), 1.0)
    out += room * 0.0021

    # -- feet -------------------------------------------------------------
    for (ts_, side, lift) in steps:
        if ts_ < 0.4 or ts_ > 81.0:
            continue
        hard = 1.0 if 31.0 <= ts_ <= CONTACT else 0.0
        g = (0.125 + 0.085 * hard) * min(1.6, 0.6 + lift / 26.0)
        pan = -0.16 if side == "near" else 0.16
        _mix(out, ts_ - 0.010, foot(hard=bool(hard)), gain=g, pan=pan)

    # -- the silence punctuation ------------------------------------------
    _mix(out, GRASS_STEP - 0.02, sub_drop(), gain=0.42)
    _mix(out, GRASS_STEP + 0.02, swish(0.35), gain=0.16, pan=0.1)

    # -- heart, only while the room is holding its breath ---------------
    beats = []
    bt = GRASS_STEP + 0.55
    while bt < 31.6:
        u = (bt - GRASS_STEP) / (31.6 - GRASS_STEP)
        bpm = 58.0 + 52.0 * u ** 1.4
        beats.append(bt)
        bt += 60.0 / bpm
    for i, b in enumerate(beats):
        fade = min(1.0, i / 3.0) * (1.0 - 0.55 * (b - GRASS_STEP) / 24.0)
        _mix(out, b, heart(), gain=0.21 * fade, pan=0.0)

    # -- the ball, before the strike --------------------------------------
    for k in range(3):
        _mix(out, 14.6 + k * 0.42, foot(hard=False, seed=30 + k), gain=0.10, pan=0.12)
    _mix(out, 17.9, thump(0.18, 160.0, 70.0), gain=0.10, pan=0.15)
    # he sets it down on the spot
    _mix(out, 23.05, thump(0.16, 150.0, 60.0), gain=0.12, pan=0.0)

    # -- the score: a drone that gets louder as the room gets quieter -----
    drone_n = _n(37.35)
    td = np.arange(drone_n) / SR
    drone = (np.sin(2 * math.pi * 55.0 * td) * 0.6
             + np.sin(2 * math.pi * 82.5 * td) * 0.35
             + 0.18 * np.sin(2 * math.pi * 110.0 * td))
    drone *= (1.0 + 0.12 * np.sin(2 * math.pi * 0.22 * td))
    d_env = _env(drone_n, [(0.0, 0.0), (GRASS_STEP, 0.10), (20.0, 0.26),
                           (30.0, 0.44), (36.4, 0.60), (CONTACT, 0.30),
                           (37.35, 0.0)])
    seg = (drone * d_env).astype(np.float32) * 0.042
    out[0, :drone_n] += seg
    out[1, :drone_n] += seg * 0.94

    # three notes, far apart, in the long look
    for i, (nt, f) in enumerate(((24.6, 110.0), (27.4, 130.81), (30.2, 146.83))):
        s = note(f, 2.2)
        _mix(out, nt, s, gain=0.085 - 0.008 * i, pan=-0.2 + 0.2 * i)

    # -- the riser into the strike ---------------------------------------
    _mix(out, CONTACT - 2.1, riser(2.1), gain=0.30, pan=0.0)

    # -- contact ----------------------------------------------------------
    _mix(out, CONTACT - 0.004, crack(), gain=0.55)
    _mix(out, CONTACT - 0.002, thump(0.42, 120.0, 38.0), gain=0.85)
    _mix(out, CONTACT + 0.005, swish(0.22), gain=0.25, pan=0.25)

    # the ball, in the air, over a silent crowd
    _mix(out, CONTACT + 0.05, swish(0.60), gain=0.20, pan=0.35)
    _mix(out, CONTACT + 0.52, swish(0.42, seed=12), gain=0.34, pan=0.45)   # the net
    _mix(out, CONTACT + 0.54, thump(0.20, 90.0, 45.0), gain=0.22, pan=0.45)

    # -- the roar ---------------------------------------------------------
    _mix(out, 41.50, clap(1.1), gain=0.55, pan=-0.2)
    _mix(out, 41.58, clap(1.1, seed=13), gain=0.45, pan=0.25)
    _mix(out, 42.60, whistle(), gain=0.30, pan=0.1)
    _mix(out, 45.90, clap(0.8, seed=14), gain=0.28, pan=0.3)

    # -- the replay: the same event through a broadcast --------------------
    rp = slice(_n(49.0), _n(58.0))
    # tape: a slow pitch wobble on everything underneath the replay
    idx = np.arange(rp.stop - rp.start)
    wob = 1.0 + 0.006 * np.sin(2 * math.pi * 0.9 * idx / SR)
    phase = np.cumsum(wob)
    for ch in (0, 1):
        seg_ = out[ch, rp]
        warped = np.interp(phase, np.arange(len(seg_)), seg_)
        out[ch, rp] = (seg_ * 0.30 + warped * 0.70).astype(np.float32)
    _mix(out, 49.05, swish(0.9, seed=15), gain=0.16, pan=-0.3)     # the riser, reversed
    _mix(out, 52.35, crack(), gain=0.30, pan=0.1)                 # contact again
    _mix(out, 52.37, thump(0.55, 95.0, 34.0), gain=0.60, pan=0.1)
    _mix(out, 52.9, swish(0.8, seed=16), gain=0.22, pan=0.2)

    # -- the shush --------------------------------------------------------
    _mix(out, SHUSH + 0.10, shush(), gain=0.85, pan=0.0)
    _mix(out, SHUSH + 0.12, heart(), gain=0.18)

    # -- the tunnel takes the crowd back ----------------------------------
    far = np.interp(t, [79.0, 82.0, TOTAL], [1.0, 0.34, 0.22]).astype(np.float32)
    out *= far

    # -- the last thing: one low hit under the card -----------------------
    _mix(out, QUESTION - 0.02, thump(0.9, 74.0, 30.0), gain=0.55)
    _mix(out, QUESTION + 0.02, note(55.0, 3.4), gain=0.12)

    # -- master -----------------------------------------------------------
    out = np.tanh(out * 1.15) / math.tanh(1.15)
    peak = float(np.max(np.abs(out))) or 1.0
    out *= 0.89 / peak
    return out


# --------------------------------------------------------------------- report

def measure(out):
    """Everything a listener would notice, as numbers."""
    def rms(a, b):
        s = out[:, _n(a):_n(b)]
        return float(np.sqrt(np.mean(s * s))) if s.size else 0.0

    def db(x):
        return 20.0 * math.log10(max(x, 1e-12))

    secs = {
        "0-7.9 tunnel (loud)": rms(0.2, 7.8),
        "7.9-9 silence drop": rms(7.95, 8.9),
        "9-31 the quiet": rms(9.0, 31.0),
        "31-37 the run-up": rms(31.0, CONTACT),
        "37.3-41.5 after the ball": rms(CONTACT + 0.1, 41.4),
        "41.5-49 the roar": rms(41.6, 48.9),
        "49-58 the replay": rms(49.1, 57.9),
        "58-72 the turn": rms(58.1, 71.9),
        "72-82 the walk-off": rms(72.1, 81.9),
        "82-90 the card": rms(82.1, 89.9),
    }
    # onset of the impact, to the millisecond
    seg = np.abs(out[0, _n(CONTACT - 0.25):_n(CONTACT + 0.25)])
    onset = float(np.argmax(np.abs(np.diff(seg))) / SR) + CONTACT - 0.25
    return {
        "sections": secs,
        "dbfs": {k: round(db(v), 1) for k, v in secs.items()},
        "peak": float(np.max(np.abs(out))),
        "clipped": int(np.sum(np.abs(out) >= 0.9999)),
        "onset": onset,
    }


def write(path, out):
    pcm = np.clip(out.T, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pov_audio")
    ap.add_argument("--out", default="deliverables/pov-stadium.wav")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    out = build(verbose=not a.quiet)
    write(a.out, out)
    m = measure(out)
    print(f"wrote {a.out}  ({out.shape[1] / SR:.2f} s stereo @ {SR} Hz)")
    for k, v in m["dbfs"].items():
        print(f"  {k:26s} {v:7.1f} dBFS")
    print(f"  peak {m['peak']:.3f}   clipped {m['clipped']}   "
          f"impact onset {m['onset']:.3f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
