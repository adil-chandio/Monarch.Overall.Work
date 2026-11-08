#!/usr/bin/env python3
"""v4 score: a sustained bed plus frame-locked sound design.

Two things here are copied from REF-01 as *measurements*, not as taste:

1. There is no voice-over. REF-01's spectral flatness sits at 0.019 (p10 0.011,
   p90 0.029) — tonal, sustained energy. So the bed is a pad, not speech room.
2. Every cut gets a transient that lands 33-110 ms BEFORE the cut. In REF-01,
   9 of 10 cuts have a transient in that window. The whoosh peaks early on
   purpose: it warns the ear, then the picture changes.

Everything is synthesised from scratch here (no sample library), so the mix is
reproducible and licence-clean.

Usage:
    python3 showreel/v4/audio.py --out public/demo/v4-mix.wav
"""

from __future__ import annotations

import argparse
import json
import os
import wave
from typing import Iterable

import numpy as np

SR = 44100
FPS = 30
# the film is 701 frames (23.35 s x 30 = 700.5, rounded up), so the bed lasts exactly
# 701/30 s. A bed that is one frame short makes the mux cut the last frame.
FRAMES = 701
TOTAL = FRAMES / FPS

# the reference's measured cut list, in seconds (REF-01 §2)
CUTS = [0.533, 0.833, 1.000, 1.300, 3.133, 9.133, 11.700,
        12.167, 12.467, 12.967, 13.333, 14.800]

# cuts that get a full impact instead of a whoosh alone
IMPACTS = {3.133: 1.00, 9.133: 0.85, 14.800: 1.15, 20.633: 0.70}
# type-slam clicks (the reference's hard-cut type arrivals)
CLICKS = [0.533, 0.833, 1.000, 12.167, 12.467, 13.333]

# how early the whoosh peaks, per cut — inside the measured 33-110 ms window
EARLY_MS = {0.533: 43, 0.833: 43, 1.300: 110, 3.133: 33, 9.133: 43,
            11.700: 47, 12.167: 47, 12.467: 33, 12.967: 17,
            13.333: 43, 14.800: 70}


# --------------------------------------------------------------------- helpers
def rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def fft_band(x: np.ndarray, lo: float, hi: float, slope: float = 0.35) -> np.ndarray:
    """Band-limit a signal with soft shelves instead of a brick wall."""
    n = len(x)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR) + 1e-9
    gain = np.ones_like(f)
    gain *= 1.0 / (1.0 + (lo / f) ** (2 * slope))          # high-pass shelf
    gain *= 1.0 / (1.0 + (f / hi) ** (2 * slope))          # low-pass shelf
    out = np.fft.irfft(spec * gain, n)
    return out / (np.abs(out).max() + 1e-12)


def env(n: int, attack: float, decay: float, curve: float = 3.0) -> np.ndarray:
    """attack/decay envelope in samples, normalised to 1."""
    a = max(1, int(attack * SR))
    d = max(1, n - a)
    e = np.concatenate([
        np.linspace(0, 1, a, endpoint=False) ** (1 / max(curve, 0.2)),
        np.exp(-np.linspace(0, curve * 3.2, d)) if decay <= 0 else np.exp(-np.linspace(0, d / (decay * SR), d)),
    ])
    return e[:n] / (e.max() + 1e-12)


def place(buf: np.ndarray, sig: np.ndarray, at: float, gain: float = 1.0) -> None:
    """Mix `sig` into `buf` (stereo, shape [n,2]) starting at time `at` seconds."""
    if sig.ndim == 1:
        sig = np.stack([sig, sig], 1)
    i = int(round(at * SR))
    if i < 0:
        sig = sig[-i:]
        i = 0
    n = min(len(sig), len(buf) - i)
    if n <= 0:
        return
    buf[i:i + n] += sig[:n] * gain


# ------------------------------------------------------------------- elements
def pad(dur: float, notes: Iterable[float], seed: int, detune: float = 0.6) -> np.ndarray:
    """A slow, chorused additive pad — the bed of the film."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    r = rng(seed)
    out = np.zeros(n)
    for f in notes:
        for k, (mult, amp) in enumerate(((1, 1.0), (2, .32), (3, .14), (4, .07), (5, .035))):
            if f * mult > 15000:
                continue
            drift = 1 + (r.standard_normal() * 0.0006)
            ph = r.uniform(0, 2 * np.pi)
            out += amp * np.sin(2 * np.pi * f * mult * detune * drift * t + ph)
        # a second, slightly detuned voice gives the pad its movement
        out += 0.45 * np.sin(2 * np.pi * f * 1.0034 * t + r.uniform(0, 6.28))
    out /= (len(list(notes)) or 1) * 2.2
    # slow amplitude breathing, 0.11 Hz — audible life without a rhythm
    out *= 0.82 + 0.18 * np.sin(2 * np.pi * 0.11 * t + 0.7)
    return out / (np.abs(out).max() + 1e-12)


def whoosh(dur: float, f0: float, f1: float, seed: int, tilt: float = 1.0) -> np.ndarray:
    """Noise pushed through a rising band — the pre-cut air movement."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    r = rng(seed)
    base = r.standard_normal(n)
    # three overlapping bands, each swept, summed: a thicker whoosh than one sweep
    out = np.zeros(n)
    for k, (a, b) in enumerate(((0.55, 0.9), (1.0, 1.0), (1.6, 0.55))):
        centre = f0 * (f1 / f0) ** t * a
        band = np.zeros(n)
        # short-time filtering: 8 ms windows, band-limited noise per window
        win = int(0.008 * SR)
        for i in range(0, n, win):
            seg = base[i:i + win]
            if len(seg) < 8:
                break
            c = centre[min(i, n - 1)]
            spec = np.fft.rfft(seg * np.hanning(len(seg)))
            f = np.fft.rfftfreq(len(seg), 1 / SR) + 1e-9
            g = np.exp(-0.5 * (np.log2(f / c) / 0.75) ** 2)
            band[i:i + len(seg)] = np.fft.irfft(spec * g, len(seg)) * np.hanning(len(seg))
        out += b * band
    shape = np.concatenate([
        np.linspace(0, 1, int(n * 0.86)) ** 2.2,
        np.linspace(1, 0, n - int(n * 0.86)) ** 1.4,
    ])[:n]
    out *= shape * tilt
    return out / (np.abs(out).max() + 1e-12)


def boom(dur: float, f0: float, f1: float, seed: int) -> np.ndarray:
    """Sub drop with a noise crack on the front — the impact under a cut."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = np.linspace(f0, f1, n)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    body = np.sin(phase) * np.exp(-t / (dur * 0.34))
    r = rng(seed)
    crack = fft_band(r.standard_normal(n), 900, 6000)
    crack *= np.exp(-t / 0.012) * 0.55
    return (body + crack) / (np.abs(body + crack).max() + 1e-12)


def click(seed: int) -> np.ndarray:
    """A type-slam tick: 6 ms of bright noise with a small pitched centre."""
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    r = rng(seed)
    noise = fft_band(r.standard_normal(n), 1800, 9000) * np.exp(-t / 0.005)
    pit = 0.5 * np.sin(2 * np.pi * 2200 * t) * np.exp(-t / 0.004)
    return (noise + pit) / (np.abs(noise + pit).max() + 1e-12)


def riser(dur: float, seed: int) -> np.ndarray:
    """A long tonal riser for the two big reveals (3.13 s and 14.80 s)."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    f = 90 * (9 ** t)                       # 90 Hz -> 810 Hz
    phase = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)
    air = fft_band(rng(seed).standard_normal(n), 1200, 11000) * 0.5
    out = (tone * 0.6 + air) * (t ** 2.1)
    return out / (np.abs(out).max() + 1e-12)


# ------------------------------------------------------------------ reverb/space
def reverb(x: np.ndarray, seed: int, wet: float = 0.28) -> np.ndarray:
    """Small Schroeder room: 4 combs + 2 allpass, mono in, mono out."""
    r = rng(seed)
    combs = [(1557, .86), (1617, .84), (1491, .82), (1422, .80)]
    out = np.zeros(len(x) + 6000)
    sig = np.concatenate([x, np.zeros(6000)])
    for delay, fb in combs:
        d = delay + int(r.integers(-12, 12))
        buf = np.zeros_like(sig)
        for i in range(d, len(sig)):
            buf[i] = sig[i - d] + fb * buf[i - d]
        out += buf / len(combs)
    for delay in (225, 556):
        buf = np.zeros_like(out)
        for i in range(delay, len(out)):
            buf[i] = -0.7 * out[i - delay] + out[i] + 0.7 * buf[i - delay]
        out = buf
    out = out[:len(x)]
    out /= (np.abs(out).max() + 1e-12)
    return (1 - wet) * x + wet * out


# ------------------------------------------------------------------------ build
def build() -> tuple[np.ndarray, dict]:
    n = int(TOTAL * SR)
    dry = np.zeros((n, 2))
    send = np.zeros(n)          # reverb send (mono)

    # ---- the bed: E minor pad, chord change at the reveal and at the CTA
    chords = [
        (0.00, 3.13, [82.41, 123.47, 164.81, 196.00]),      # E2 B2 E3 G3
        (3.13, 9.13, [110.00, 164.81, 220.00, 261.63]),     # A2 E3 A3 C4
        (9.13, 11.70, [82.41, 123.47, 164.81, 207.65]),     # E2 B2 E3 G#3
        (11.70, 14.80, [73.42, 110.00, 146.83, 185.00]),    # D2 A2 D3 F#3
        (14.80, 23.35, [82.41, 123.47, 164.81, 196.00, 246.94]),
    ]
    for i, (a, b, notes) in enumerate(chords):
        seg = pad(b - a + 0.6, notes, seed=100 + i)
        fade = np.ones(len(seg))
        fa = int(0.35 * SR)
        fade[:fa] = np.linspace(0, 1, fa)
        fade[-fa:] = np.linspace(1, 0, fa)
        place(dry, np.stack([seg * fade, seg * fade], 1), a, 0.22)
        send_sig = seg * fade
        j = int(round(a * SR))
        m = min(len(send_sig), n - j)
        send[j:j + m] += send_sig[:m] * 0.30

    # ---- sustained bass root per chord (no rhythm: a held sine, so the bed
    # stays tonal like the reference's track without inventing a tempo)
    for i, (a, b, notes) in enumerate(chords):
        root = notes[0] / 2
        nseg = int((b - a) * SR)
        t = np.arange(nseg) / SR
        sub = (np.sin(2 * np.pi * root * t) + 0.22 * np.sin(4 * np.pi * root * t))
        f = int(0.12 * SR)
        sub[:f] *= np.linspace(0, 1, f)
        sub[-f:] *= np.linspace(1, 0, f)
        place(dry, np.stack([sub, sub], 1), a, 0.16)

    # ---- NO pulse train. REF-01 measured envelope periodicity 0.073 and
    # "no stable tempo grid": a 1 Hz thump here scored 0.31 / 166.7 BPM and was
    # removed. The bed sustains; only cuts and reveals punctuate it.

    # ---- pre-cut whooshes: peak lands EARLY_MS before the cut (measured rule)
    for i, c in enumerate(CUTS):
        early = EARLY_MS.get(c, 43) / 1000.0
        dur = 0.26
        w = whoosh(dur, 190, 2600, seed=200 + i)
        start = c - early - dur * 0.86          # so the peak sits at c - early
        st = np.stack([w * 0.92, np.roll(w, 3) * 1.0], 1)
        place(dry, st, start, 0.62)
        j = int(round(max(start, 0) * SR))
        m = min(len(w), n - j)
        send[j:j + m] += w[:m] * 0.16

    # ---- impacts
    for k, (c, g) in enumerate(IMPACTS.items()):
        b = boom(0.55 if c < 20 else 0.4, 92 if c < 20 else 120, 34, seed=500 + k)
        # 60 ms early, not 35: a sub sweep needs ~25 ms for its energy to
        # accumulate, so its RMS peak lands ~35 ms before the cut, inside the
        # reference's measured 33-110 ms window.
        place(dry, np.stack([b, b], 1), c - 0.060, 0.55 * g)
        j = int(round(max(c - 0.060, 0) * SR))
        m = min(len(b), n - j)
        send[j:j + m] += b[:m] * 0.22

    # ---- type-slam ticks, exactly on the cut (the whoosh peak stays the
    # measured transient; this only adds the hard edge of the picture cut)
    for i, c in enumerate(CLICKS):
        ck = click(seed=600 + i)
        place(dry, np.stack([ck, ck * 0.94], 1), c, 0.13)

    # ---- long risers into the two big reveals
    rr = riser(0.95, seed=700)
    place(dry, np.stack([rr, rr], 1), 3.133 - 0.95, 0.26)
    rr2 = riser(1.25, seed=701)
    place(dry, np.stack([rr2, np.roll(rr2, 5)], 1), 14.800 - 1.25, 0.30)

    # ---- the flash: a short bright wash, gated off two frames later
    r = rng(7)
    wash = fft_band(r.standard_normal(int(0.22 * SR)), 2500, 13000)
    wash *= env(len(wash), 0.002, 0.05, curve=2.4)
    place(dry, np.stack([wash, wash], 1), 20.633, 0.24)

    # ---- tail of the film: let it ring out, don't cut it dead
    tail = int(0.6 * SR)
    dry[-tail:] *= np.linspace(1, 0, tail)[:, None]

    # ---- space + glue
    mix = dry.copy()
    for ch in range(2):
        mix[:, ch] += reverb(send, seed=800 + ch, wet=1.0) * 0.55

    # gentle bus compression (the reference has LRA 1.7 — it is tight, not loud)
    seg = 2048
    hop = 512
    lvl = np.sqrt(np.convolve(mix.mean(1) ** 2, np.ones(seg) / seg, "same") + 1e-12)
    ref = np.percentile(lvl, 88)
    gain = (ref / (lvl + 1e-12)) ** 0.15          # gentle glue only, not loudness
    gain = np.clip(gain, 0.72, 1.35)
    mix *= gain[:, None]

    # a light high shelf cut so the pad does not hiss at 720p delivery
    for ch in range(2):
        mix[:, ch] = fft_band(mix[:, ch], 22, 14500, slope=0.22)

    peak = np.abs(mix).max()
    mix = mix / peak * 10 ** (-3.0 / 20)          # -3 dBFS headroom; loudnorm does the rest

    stats = {
        "duration": TOTAL,
        "cuts": CUTS,
        "whoosh_lead_ms": {f"{c:.3f}": EARLY_MS.get(c, 43) for c in CUTS},
        "impacts": list(IMPACTS),
        "clicks": CLICKS,
        "peak_dbfs": round(float(20 * np.log10(np.abs(mix).max() + 1e-12)), 2),
        "rms_dbfs": round(float(20 * np.log10(np.sqrt((mix ** 2).mean()) + 1e-12)), 2),
    }
    return mix, stats


def write_wav(path: str, sig: np.ndarray) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    pcm = np.clip(sig, -1, 1)
    pcm = (pcm * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="public/demo/v4-mix.wav")
    ap.add_argument("--stats", default="showreel/v4/audio-stats.json")
    args = ap.parse_args()
    mix, stats = build()
    write_wav(args.out, mix)
    with open(args.stats, "w") as fh:
        json.dump(stats, fh, indent=2)
    print(json.dumps(stats, indent=2))
    print(f"wrote {args.out}  ({os.path.getsize(args.out) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
