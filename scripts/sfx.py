#!/usr/bin/env python3
"""Procedural sound design for the orca film, synced to the beat sheet.

No sample library: every cue is synthesised with numpy so the whole bed is
reproducible from the repo and there is nothing to license or lose.

Cues, and what each one is for:

  sub_boom      a 48 Hz sine with a fast pitch drop and a long decay. Lands on a
                cut where something arrives. This is the single most useful cue in
                this genre: it sells a hard cut without any picture change.
  whoosh        band-limited noise with a fast spectral sweep, 0.5 s. Used on every
                transition and every time an animal crosses frame.
  sonar_ping    a 1.1 kHz sine, exponential decay, small reverb tail. The reference
                uses a sonar motif constantly; the ping has to land exactly on the
                ring's emission or the two read as unrelated.
  whale_call    a low swept sine with vibrato and a breathy noise layer. Humpback
                moans sit around 200-600 Hz with a slow downward glide.
  riser         noise swelling over 1.4 s into a beat. Used before the species card.
  impact_tick   a very short filtered click for the pyramid rows appearing.
  bubble_burst  a cluster of short pitch-rising blips.
  teeth_sting   a metallic cluster for the "JUST PLAYING DEFENCE" card.

The output is a single 60 s stereo WAV at 44.1 kHz plus a cues JSON that records
which cue landed on which beat, so the mix can be re-derived rather than re-guessed.

Run:  python scripts/sfx.py --out /tmp/sfx.wav --cues /tmp/sfx-cues.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

SR = 44100
DURATION = 60.0


def t_axis(seconds):
    return np.arange(int(seconds * SR), dtype=np.float64) / SR


def fade(y, a=0.004, d=0.02):
    """Click-free in and out. A cue without this pops on every cut."""
    n = len(y)
    na, nd = max(1, int(a * SR)), max(1, int(d * SR))
    na, nd = min(na, n // 2), min(nd, n // 2)
    y[:na] *= np.linspace(0, 1, na) ** 1.5
    y[-nd:] *= np.linspace(1, 0, nd) ** 1.5
    return y


def lp(y, cutoff):
    """One-pole low-pass. Cheap, and enough for noise shaping."""
    a = math.exp(-2 * math.pi * cutoff / SR)
    out = np.empty_like(y)
    acc = 0.0
    for i in range(len(y)):
        acc = (1 - a) * y[i] + a * acc
        out[i] = acc
    # vectorised where possible; the loop above is only used on short cues
    return out


def lp_fast(y, cutoff):
    """Vectorised single-pole low-pass, scipy-free.

    y[n] = (1-a)x[n] + a*y[n-1]  =>  y = (1-a) * cumsum(x * a**-n) * a**n

    `cutoff` may be an array, which the riser uses to sweep a filter over time.
    The first version assumed a scalar and crashed the instant the riser ran.
    """
    cutoff = np.asarray(cutoff, dtype=np.float64)
    a = np.exp(-2 * math.pi * cutoff / SR)
    if a.ndim == 0:
        a = float(a)
    n = np.arange(len(y))
    an = a ** n
    with np.errstate(over="ignore", invalid="ignore"):
        s = np.cumsum(y / np.maximum(an, 1e-280))
    out = (1 - a) * s * an
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)


def hp_fast(y, cutoff):
    return y - lp_fast(y, cutoff)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def noise(n, seed=0):
    rng = np.random.default_rng(seed)
    return rng.standard_normal(n)


# ---------------------------------------------------------------------------
# Cues
# ---------------------------------------------------------------------------
def c_sub_boom(dur=1.6, f0=68.0, f1=34.0, gain=1.0):
    t = t_axis(dur)
    # pitch drops fast then holds, like a real sub hit
    f = f1 + (f0 - f1) * np.exp(-t * 9.0)
    phase = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(phase) * env_exp(len(t), dur * 0.28)
    click = hp_fast(noise(len(t), 11), 1800) * env_exp(len(t), 0.012) * 0.22
    return fade((body + click) * gain * 0.9, 0.003, dur * 0.35)


def c_whoosh(dur=0.55, up=True, gain=1.0, seed=3):
    t = t_axis(dur)
    n = noise(len(t), seed)
    k = t / dur
    # crossfade between a dark and a bright version of the same noise
    dark = lp_fast(n, 420)
    bright = hp_fast(n, 2600)
    m = k if up else 1 - k
    y = dark * (1 - m) + bright * m
    shape = np.sin(np.pi * np.clip(k, 0, 1)) ** 1.6
    return fade(y * shape * gain * 0.55, 0.01, 0.05)


def c_sonar_ping(dur=1.14, f=1180.0, gain=1.0):
    t = t_axis(dur)
    tone = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.02 * t)
    y = tone * env_exp(len(t), 0.14)
    # a small room tail so it does not sound like a test tone
    tail = np.concatenate([np.zeros(int(0.09 * SR)), y[:-int(0.09 * SR)] * 0.30])
    return fade((y + tail) * gain * 0.42, 0.002, 0.12)


def c_whale_call(dur=2.6, f0=340.0, f1=150.0, gain=1.0, vib=5.0):
    t = t_axis(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 1.5) + vib * np.sin(2 * np.pi * 4.4 * t)
    phase = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(phase) + 0.30 * np.sin(2 * phase) + 0.12 * np.sin(3 * phase)
    breath = lp_fast(noise(len(t), 21), 900) * 0.16
    shape = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
    return fade((tone + breath) * shape * gain * 0.34, 0.09, dur * 0.4)


def c_riser(dur=1.5, gain=1.0):
    t = t_axis(dur)
    k = t / dur
    n = noise(len(t), 33)
    y = lp_fast(n, 300 + 5200 * k ** 2)
    y *= (k ** 2.2)
    tone = np.sin(2 * np.pi * np.cumsum(80 + 900 * k ** 2) / SR) * (k ** 3) * 0.35
    return fade((y * 0.8 + tone) * gain * 0.6, 0.05, 0.03)


def c_impact_tick(dur=0.22, f=760.0, gain=1.0, seed=5):
    t = t_axis(dur)
    tone = np.sin(2 * np.pi * f * t) * env_exp(len(t), 0.035)
    click = hp_fast(noise(len(t), seed), 3000) * env_exp(len(t), 0.006)
    return fade((tone * 0.5 + click * 0.35) * gain, 0.001, 0.03)


def c_bubble_burst(dur=1.5, n_bub=26, gain=1.0, seed=9):
    out = np.zeros(int(dur * SR))
    rng = np.random.default_rng(seed)
    for i in range(n_bub):
        at = int(rng.uniform(0, dur - 0.15) * SR)
        d = 0.045 + rng.uniform(0, 0.05)
        t = t_axis(d)
        f0 = rng.uniform(300, 900)
        f = f0 * (1 + 5.0 * t / d)          # bubbles rise in pitch
        tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(len(t), d * 0.30)
        seg = fade(tone * rng.uniform(0.4, 1.0) * 0.35, 0.001, 0.01)
        end = min(len(out), at + len(seg))
        out[at:end] += seg[: end - at]
    return out * gain


def c_teeth_sting(dur=0.9, gain=1.0):
    """A metallic cluster: three detuned partials with a hard attack."""
    t = t_axis(dur)
    y = np.zeros(len(t))
    for f, a, tau in ((1318, 0.5, 0.10), (1975, 0.3, 0.07), (2637, 0.18, 0.05)):
        y += a * np.sin(2 * np.pi * f * t) * env_exp(len(t), tau)
    y += hp_fast(noise(len(t), 41), 4000) * env_exp(len(t), 0.010) * 0.35
    return fade(y * gain * 0.30, 0.001, 0.2)


# ---------------------------------------------------------------------------
# The cue sheet. Every entry is (time, cue function, gain, stereo pan -1..1)
# Times come from beats() in scripts/orca-film.py and are duplicated here on
# purpose: the mixer must not import the renderer, or a picture change silently
# moves the sound.
# ---------------------------------------------------------------------------
CUES = [
    # 0.00 orcas glide in
    (0.15, "sub_boom", 0.55, 0.0),
    (0.60, "whoosh", 0.42, -0.5),
    (1.30, "whale_call", 0.34, -0.25),
    # 5.20 wash
    (5.05, "whoosh", 0.55, 0.3),
    # 6.10 arc
    (6.10, "whoosh", 0.45, 0.6),
    (6.30, "whale_call", 0.22, 0.4),
    # 9.40 escort
    (9.40, "sub_boom", 0.62, 0.0),
    (9.55, "whale_call", 0.38, -0.3),
    (10.40, "sonar_ping", 0.30, 0.5),
    # 14.25 krill
    (14.25, "whoosh", 0.40, -0.4),
    (14.60, "bubble_burst", 0.32, -0.2),
    (15.60, "bubble_burst", 0.24, 0.3),
    # 18.60 card
    (18.05, "riser", 0.60, 0.0),
    (18.60, "sub_boom", 0.72, 0.0),
    (18.75, "whale_call", 0.42, 0.0),
    # 22.40 pyramid
    (22.40, "impact_tick", 0.50, 0.0),
    (22.72, "impact_tick", 0.44, 0.0),
    (23.04, "impact_tick", 0.40, 0.0),
    (23.36, "impact_tick", 0.36, 0.0),
    # 25.60 boss of the sea
    (25.60, "sub_boom", 0.55, 0.0),
    (25.70, "teeth_sting", 0.42, 0.0),
    # 27.64 scan
    (27.64, "sonar_ping", 0.50, 0.0),
    (28.56, "sonar_ping", 0.36, 0.25),
    (29.48, "sonar_ping", 0.26, -0.25),
    # 31.40 flock
    (31.40, "whoosh", 0.36, -0.6),
    (32.20, "whale_call", 0.26, 0.2),
    # 35.60 wheel
    (35.60, "whoosh", 0.40, 0.6),
    (35.80, "sonar_ping", 0.34, -0.4),
    # 39.20 plan view
    (39.20, "sonar_ping", 0.46, 0.0),
    (40.60, "teeth_sting", 0.26, 0.0),
    # 42.40 rise
    (42.10, "riser", 0.50, 0.0),
    (42.40, "whale_call", 0.46, 0.0),
    (42.55, "bubble_burst", 0.26, 0.0),
    # 45.60 card 2 / Gansbaai
    (45.60, "sub_boom", 0.58, 0.0),
    (45.60, "whoosh", 0.30, -0.5),
    # 49.60 orcas on the scene
    (49.60, "whoosh", 0.44, 0.5),
    (49.85, "sub_boom", 0.50, 0.0),
    (50.60, "sonar_ping", 0.32, 0.35),
    # 54.00 playing defence
    (54.00, "sub_boom", 0.66, 0.0),
    (54.05, "teeth_sting", 0.46, 0.0),
    (54.60, "whale_call", 0.40, 0.0),
    (57.20, "whoosh", 0.34, -0.4),
    (58.40, "sub_boom", 0.48, 0.0),
]

BUILDERS = {
    "sub_boom": c_sub_boom,
    "whoosh": c_whoosh,
    "sonar_ping": c_sonar_ping,
    "whale_call": c_whale_call,
    "riser": c_riser,
    "impact_tick": c_impact_tick,
    "bubble_burst": c_bubble_burst,
    "teeth_sting": c_teeth_sting,
}


def build(duration=DURATION):
    n = int(duration * SR)
    left = np.zeros(n)
    right = np.zeros(n)
    placed = []
    for idx, (at, name, gain, pan) in enumerate(CUES):
        fn = BUILDERS[name]
        # a little deterministic variation so repeated cues do not phase-lock
        seed = 100 + idx
        try:
            cue = fn(gain=gain, seed=seed)
        except TypeError:
            cue = fn(gain=gain)
        if cue.ndim == 1:
            cue = np.stack([cue, cue], axis=1)
        i0 = int(at * SR)
        i1 = min(n, i0 + len(cue))
        if i0 >= n:
            continue
        seg = cue[: i1 - i0]
        if seg.ndim == 1:
            seg = np.stack([seg, seg], axis=1)
        lg = math.sqrt((1 - pan) / 2)
        rg = math.sqrt((1 + pan) / 2)
        left[i0:i1] += seg[:, 0] * lg
        right[i0:i1] += seg[:, 1] * rg
        placed.append({"t": round(at, 2), "cue": name, "gain": gain, "pan": pan,
                       "len": round(len(seg) / SR, 3)})
    mix = np.stack([left, right], axis=1)
    peak = float(np.max(np.abs(mix))) or 1.0
    mix = mix / peak * 0.72          # leave headroom for the voice
    return mix, placed


def write_wav(path, mix):
    data = (np.clip(mix, -1, 1) * 32767).astype("<i2")
    n_frames, n_ch = data.shape
    import struct
    with open(path, "wb") as fh:
        fh.write(b"RIFF")
        fh.write(struct.pack("<I", 36 + n_frames * n_ch * 2))
        fh.write(b"WAVEfmt ")
        fh.write(struct.pack("<IHHIIHH", 16, 1, n_ch, SR, SR * n_ch * 2, n_ch * 2, 16))
        fh.write(b"data")
        fh.write(struct.pack("<I", n_frames * n_ch * 2))
        fh.write(data.tobytes())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/sfx.wav")
    ap.add_argument("--cues", default="/tmp/sfx-cues.json")
    ap.add_argument("--duration", type=float, default=DURATION)
    a = ap.parse_args()
    mix, placed = build(a.duration)
    write_wav(a.out, mix)
    Path(a.cues).write_text(json.dumps(placed, indent=1))
    print(f"{a.out}  {len(mix)/SR:.2f}s  {len(placed)} cues  peak {float(np.max(np.abs(mix))):.2f}")
    from collections import Counter
    print("  " + "  ".join(f"{k}x{v}" for k, v in sorted(Counter(c["cue"] for c in placed).items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
