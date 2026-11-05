#!/usr/bin/env python3
"""A music bed written as numbers, graded to the reference's own spectrum.

The reference's soundtrack measures, over its quiet passages:

    sub 20-120 Hz   5.7 %      low 120-400   22.0 %      mid 400-1500  29.2 %
    hi 1500-5000   15.2 %      air 5-16k     27.2 %      RMS -16 dBFS, peak -0.4

Twenty-seven percent of the energy in the air band is the signature of that kind of reel:
a bright, wide top over a soft low body. So the bed here is built to that profile rather
than to taste -- a dark harmonic pad, a soft pulse, and an airy layer -- and then a static
EQ moves it onto those numbers. The notes are a minor sequence in D; none of them are
taken from the reference, only the *shape* of the mix is.

    python3 tools/music_bed.py --seconds 7.0 --out audio/bed-7.wav
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ffbin import ffmpeg

SR = 48000
TARGET = {"sub": 0.057, "low": 0.220, "mid": 0.292, "hi": 0.152, "air": 0.272}
BANDS = {"sub": (20, 120), "low": (120, 400), "mid": (400, 1500),
         "hi": (1500, 5000), "air": (5000, 16000)}

# D minor, a slow turn: i - VI - III - VII. Roots in Hz, two octaves for the pad.
NOTE = {"D2": 73.42, "F2": 87.31, "A2": 110.0, "Bb2": 116.54, "C3": 130.81, "D3": 146.83,
        "F3": 174.61, "A3": 220.0, "Bb3": 233.08, "C4": 261.63, "D4": 293.66,
        "F4": 349.23, "A4": 440.0, "D5": 587.33, "A5": 880.0, "D6": 1174.66,
        "E3": 164.81, "G3": 196.0, "C5": 523.25, "Bb4": 466.16, "E5": 659.26,
        "G4": 392.0, "G5": 783.99, "Bb5": 932.33, "F5": 698.46, "C6": 1046.5}
CHORDS = [("D2", ["D3", "F3", "A3", "D4"]),
          ("Bb2", ["D3", "F3", "Bb3", "D4"]),
          ("F2", ["C4", "F3", "A3", "F4"]),
          ("C3", ["D4", "F3", "A3", "C4"])]


def rng(seed: int):
    return np.random.default_rng(seed)


def tone(f: float, n: int, amp: float, r, kind: str = "pad") -> np.ndarray:
    """One note. A pad is a few detuned partials with a soft attack; a pluck decays fast."""
    t = np.arange(n) / SR
    out = np.zeros(n, np.float64)
    partials = (1, 2, 3, 4.02, 5.01) if kind == "pad" else (1, 2, 3)
    for i, p in enumerate(partials):
        det = 1 + r.normal(0, 0.0012)
        out += (0.55 ** i) * np.sin(2 * np.pi * f * p * det * t + r.uniform(0, 6.28))
    if kind == "pad":
        att = min(int(0.28 * SR), max(1, n // 3))
        env = np.ones(n)
        env[:att] = np.linspace(0, 1, att) ** 1.6
        env *= 1 - np.linspace(0, 1, n) ** 3.0 * 0.55
    else:
        env = np.exp(-t * 7.0) * (1 - np.exp(-t * 900))
    return amp * out * env


def lowpass(x: np.ndarray, fc: float, order: int = 4) -> np.ndarray:
    from scipy.signal import butter, sosfilt
    sos = butter(order, fc / (SR / 2), btype="low", output="sos")
    return sosfilt(sos, x)


def highpass(x: np.ndarray, fc: float, order: int = 2) -> np.ndarray:
    from scipy.signal import butter, sosfilt
    sos = butter(order, fc / (SR / 2), btype="high", output="sos")
    return sosfilt(sos, x)


def band(x: np.ndarray, lo: float, hi: float, order: int = 2) -> np.ndarray:
    from scipy.signal import butter, sosfilt
    sos = butter(order, [lo / (SR / 2), hi / (SR / 2)], btype="band", output="sos")
    return sosfilt(sos, x)


def spectrum_share(x: np.ndarray) -> dict:
    seg = x[:int(2.0 * SR)]
    S = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    tot = S.sum() + 1e-12
    return {k: float(S[(f >= lo) & (f < hi)].sum() / tot) for k, (lo, hi) in BANDS.items()}


def build(seconds: float, seed: int = 7) -> np.ndarray:
    n = int(seconds * SR)
    r = rng(seed)
    t = np.arange(n) / SR
    left = np.zeros(n)
    right = np.zeros(n)
    # ---- pad: the four chords, two bars each, each note placed with a little width
    bar = seconds / max(1, len(CHORDS))
    for ci, (root, notes) in enumerate(CHORDS):
        start = int(ci * bar * SR)
        length = min(n - start, int((bar + 0.5) * SR))
        if length <= 0:
            continue
        for ni, nm in enumerate(notes):
            f = NOTE[nm]
            v = tone(f, length, 0.20 / (1 + 0.25 * ni), r, "pad")
            pan = (ni - len(notes) / 2 + 0.5) / max(1, len(notes)) * 1.1
            left[start:start + length] += v * (1 - max(0, pan) * 0.6)
            right[start:start + length] += v * (1 + min(0, pan) * 0.6)
        # the root, an octave down, filtered: the low body
        v = lowpass(tone(NOTE[root], length, 0.42, r, "pad"), 220)
        left[start:start + length] += v
        right[start:start + length] += v
    # ---- pulse: a soft kick every beat, felt rather than heard
    beat = 60 / 96
    for k in range(int(seconds / beat) + 1):
        s = int(k * beat * SR)
        ln = min(n - s, int(0.30 * SR))
        if ln <= 0:
            continue
        tt = np.arange(ln) / SR
        f = 54 * np.exp(-tt * 26) + 41
        k_ = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9.5) * 0.5
        left[s:s + ln] += k_
        right[s:s + ln] += k_
    # ---- air: filtered noise that swells, the 27 % that makes the reference read bright
    air_l = highpass(band(r.normal(0, 1, n), 5000, 15000), 4800)
    air_r = highpass(band(r.normal(0, 1, n), 5000, 15000), 4800)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / max(1.0, seconds) * 1.0 - 1.2)
    air = 0.055 * (0.35 + 0.65 * swell)
    left += air_l * air
    right += air_r * air
    # ---- a pluck motif: two notes per bar, in the mid band, quiet
    for ci in range(len(CHORDS)):
        for half in (0.0, 0.5):
            s = int((ci + half) * bar * SR)
            ln = min(n - s, int(0.9 * SR))
            if ln <= 0:
                continue
            nm = "D5" if half == 0 else "A5"
            v = band(tone(NOTE[nm], ln, 0.075, r, "pluck"), 600, 4200)
            pan = 0.35 if half == 0 else -0.35
            left[s:s + ln] += v * (1 - max(0, pan) * 0.5)
            right[s:s + ln] += v * (1 + min(0, pan) * 0.5)
    st = np.stack([left, right], 1)
    # ---- move the static EQ onto the reference's own numbers, in passes, because one
    # pass cannot converge: cutting the sub hands its share to the bands above it
    for _ in range(6):
        share = spectrum_share(st[:, 0])
        worst = max(abs(np.log((TARGET[k] + 1e-9) / (share[k] + 1e-9))) for k in BANDS)
        if worst < 0.06:
            break
        for k, (lo, hi) in BANDS.items():
            if share[k] < 1e-6:
                continue
            g = float(np.clip((TARGET[k] / share[k]) ** 0.75, 0.25, 4.0))
            if abs(np.log(g)) < 0.02:
                continue
            for ch in (0, 1):
                st[:, ch] += band(st[:, ch], lo, hi) * (g - 1)
    st = np.stack([highpass(st[:, 0], 28), highpass(st[:, 1], 28)], 1)
    st *= 0.55 / max(np.abs(st).max(), 1e-9)           # headroom: effects go on top
    fade = int(0.06 * SR)
    st[:fade] *= np.linspace(0, 1, fade)[:, None]
    st[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return st


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=7.0)
    ap.add_argument("--out", default="audio/bed-7.wav")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    st = build(a.seconds, a.seed)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    # 24-bit PCM through ffmpeg, so no extra dependency is needed to write it
    raw = (np.clip(st, -1, 1) * 2147483000).astype(np.int32).tobytes()
    w = subprocess.Popen([ffmpeg(), "-v", "error", "-y", "-f", "s32le", "-ar", str(SR), "-ac", "2",
                          "-i", "-", "-c:a", "pcm_s24le", a.out], stdin=subprocess.PIPE)
    w.stdin.write(raw)
    w.stdin.close()
    w.wait()
    got = spectrum_share(st[:, 0])
    print(f"  bed {a.seconds:.2f}s -> {a.out}")
    print("  band share  target / got")
    for k in BANDS:
        print(f"    {k:4s} {TARGET[k]:.3f} / {got[k]:.3f}")
    print(f"  peak {20 * np.log10(np.abs(st).max()):.1f} dBFS  rms "
          f"{20 * np.log10(np.sqrt((st ** 2).mean())):.1f} dBFS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
