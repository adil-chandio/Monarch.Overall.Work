#!/usr/bin/env python3
"""The film's music, written as numbers: sections, harmony, groove, and a dynamics arc.

A seven-second bed can carry a loop; twenty-three seconds cannot -- the reference's own
soundtrack moves in level by more than 5 dB and changes its groove at every act break. So
this score is a list of sections, each with its chord, its intensity and the pattern it
plays, and the result is what the cue sheet then sits on top of.

The dynamics arc is taken from the reference, measured in one-second windows:
    t  0-3  -16.0 dBFS     t 9 (subscribe) -13.6 (its loudest)
    t 3-9  -17.0           t21 (CTA)       -12.9
    t13-20 -17.5           quiet between    -18.6
Nothing is copied: the harmony, the sounds and the patterns are ours, and no reference audio
is used. Only the shape of the mix is matched.

    python3 tools/film_score.py --seconds 23.267 --out audio/bed-23.wav
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ffbin import ffmpeg                               # noqa: E402
from music_bed import (SR, NOTE, tone, band, lowpass, highpass,  # noqa: E402
                       spectrum_share, TARGET)

# section: (start, end, chord in Hz, intensity 0..1, kick every s, arp pattern, rms target dBFS)
SECTIONS = [
    (0.000, 0.533, ["D3", "F3", "A3"], 0.42, 0.0, None, -16.2),
    (0.533, 1.333, ["D3", "F3", "A3"], 0.55, 0.0, ["A4", "D5"], -15.8),
    (1.333, 3.133, ["Bb2", "D3", "F3"], 0.50, 0.0, ["F4", "Bb4", "D5"], -16.4),
    (3.133, 5.200, ["D3", "F3", "A3", "D4"], 0.72, 0.50, ["A4", "D5", "F5"], -16.2),
    (5.200, 7.100, ["Bb2", "D3", "F3", "Bb3"], 0.74, 0.50, ["F4", "Bb4", "D5"], -16.8),
    (7.100, 9.167, ["F2", "A2", "C3", "F3"], 0.78, 0.50, ["C5", "F5", "A5"], -16.6),
    (9.167, 11.733, ["Bb2", "D3", "F3", "Bb3"], 0.95, 0.50, ["D5", "F5", "Bb5"], -14.6),
    (11.733, 12.200, ["C3", "E3", "G3"], 0.90, 0.25, ["G4", "C5", "E5"], -15.4),
    (12.200, 12.500, ["D3", "F3", "A3"], 0.88, 0.25, ["A4", "D5"], -15.6),
    (12.500, 12.700, ["Bb2", "D3", "F3"], 0.86, 0.20, ["F5"], -15.4),
    (12.700, 13.000, ["C3", "E3", "G3"], 0.88, 0.30, ["G5"], -15.2),
    (13.000, 14.833, ["F2", "A2", "C3", "F3"], 0.62, 0.0, ["C5", "F5"], -16.6),
    (14.833, 16.900, ["D3", "F3", "A3", "D4"], 0.70, 0.55, ["A4", "D5", "F5"], -16.9),
    (16.900, 18.700, ["Bb2", "D3", "F3", "Bb3"], 0.66, 0.55, ["F4", "Bb4", "D5"], -17.7),
    (18.700, 19.800, ["F2", "A2", "C3", "F3"], 0.76, 0.55, ["C5", "F5"], -17.2),
    (19.800, 20.633, ["C3", "E3", "G3", "C4"], 0.92, 0.25, ["E5", "G5", "C6"], -15.6),
    (20.633, 21.900, ["Bb2", "D3", "F3", "Bb3"], 1.00, 0.40, ["D5", "F5", "Bb5"], -14.2),
    (21.900, 23.267, ["D3", "F3", "A3", "D4"], 0.55, 0.62, ["A4", "D5"], -16.0),
]

RNG = np.random.default_rng(20240311)


def pad_block(notes: list[str], n: int, amp: float, rng) -> np.ndarray:
    """A chord laid down with a slow swell; each voice detuned and panned by its index."""
    out = np.zeros((n, 2))
    for i, nm in enumerate(notes):
        v = tone(NOTE[nm], n, amp / (1 + 0.3 * i), rng, "pad")
        v = lowpass(v, 4200.0, order=2)                   # keep it well away from 2-5 kHz
        pan = (i - (len(notes) - 1) / 2) * 0.14
        out[:, 0] += v * (1 - max(0.0, pan))
        out[:, 1] += v * (1 + min(0.0, pan))
    return out


def kick_burst(n: int) -> np.ndarray:
    t = np.arange(n) / SR
    f = 52 * np.exp(-t * 30) + 40
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * 0.62


def bell_note(f: float, n: int) -> np.ndarray:
    t = np.arange(n) / SR
    v = (0.7 * np.sin(2 * np.pi * f * t) + 0.22 * np.sin(2 * np.pi * f * 2.01 * t)
         + 0.08 * np.sin(2 * np.pi * f * 3.98 * t))
    env = np.exp(-t * 3.4) * (1 - np.exp(-t * 400))
    return v * env * 0.30


def add(dst: np.ndarray, x: np.ndarray, at: float, gain: float = 1.0) -> None:
    s = int(round(at * SR))
    if s < 0 or s >= dst.shape[0]:
        return
    n = min(len(x), dst.shape[0] - s)
    dst[s:s + n] += x[:n] * gain


# the reference's own loudness arc, measured in one-second windows (dBFS). It is a number
# read off the reference, not its audio: the arrangement is ours, the shape of its mix is
# what makes twenty-three seconds feel like one piece.
REF_ARC = [-14.7, -16.5, -15.9, -15.2, -16.0, -17.1, -16.6, -17.6, -17.6, -13.6, -15.1,
           -16.9, -15.4, -16.4, -14.5, -16.0, -18.4, -15.7, -18.6, -17.0, -17.8, -12.9, -16.3]


def follow_reference_arc(y: np.ndarray, seconds: float) -> np.ndarray:
    """Bend the score's level to the film's measured arc in one-second steps.

    The dynamics are the one thing a loop cannot fake: the reference drops 5 dB into its
    quiet shots and lifts 4 dB on its subscribe and CTA. This applies that contour to our
    own music as a slow gain, smoothed so it never steps at a section boundary.
    """
    from scipy.ndimage import uniform_filter1d
    n = y.shape[0]
    sec = int(SR)
    want = np.array([REF_ARC[min(i, len(REF_ARC) - 1)] for i in range(int(np.ceil(seconds)) + 1)])
    curves = []
    for i in range(len(want) - 1):
        seg = y[i * sec:min(n, (i + 1) * sec)]
        if len(seg) < sec // 4:
            curves.append(0.0)
            continue
        got = 20 * np.log10(max(np.sqrt((seg ** 2).mean()), 1e-9))
        curves.append(float(np.clip(want[i] - got, -9.0, 9.0)))
    g = np.zeros(n)
    for i, c in enumerate(curves):
        a, b = i * sec, min(n, (i + 1) * sec)
        g[a:b] = c
    g = uniform_filter1d(g, int(0.45 * SR))
    return y * (10 ** (g / 20.0))[:, None]


def build(seconds: float) -> np.ndarray:
    n = int(seconds * SR)
    y = np.zeros((n, 2))
    for (t0, t1, chord, inten, kick_iv, arp, rms_t) in SECTIONS:
        if t0 >= seconds:
            break
        t1 = min(t1, seconds)
        a = int(t0 * SR)
        m = int((t1 - t0) * SR)
        if m <= 0:
            continue
        block = np.zeros((m, 2))
        # the chord, plus its root an octave down as the body
        block += pad_block(chord, m, 0.30 * inten, RNG)
        root = lowpass(tone(NOTE[chord[0]], m, 0.34 * inten, RNG, "pad"), 190.0)
        block[:, 0] += root
        block[:, 1] += root
        # a swell-in on the section's head so sections butt against each other without a click
        head = min(m, int(0.06 * SR))
        block[:head] *= np.linspace(0, 1, head)[:, None]
        # groove
        if kick_iv:
            k = 0.0
            while k < t1 - t0:
                add(block, np.stack([kick_burst(int(0.26 * SR))] * 2, 1), k, 0.85 * inten)
                k += kick_iv
        # arp on the section's own notes, eighth notes at 120 bpm
        if arp:
            step = 0.25
            i = 0
            at = 0.0
            while at < t1 - t0:
                nm = arp[i % len(arp)]
                ln = int(0.42 * SR)
                v = bell_note(NOTE[nm], ln) * (0.55 + 0.45 * inten)
                pan = 0.35 if i % 2 == 0 else -0.35
                add(block, np.stack([v * (1 - max(0, pan)), v * (1 + min(0, pan))], 1), at, 0.9)
                at += step
                i += 1
        y[a:a + m] += block
        # section dynamics: measure and set to the target
        got = 20 * np.log10(max(np.sqrt((block ** 2).mean()), 1e-9))
        y[a:a + m] *= 10 ** ((rms_t - got) / 20.0)
    # air: a constant soft top that breathes, so the film never feels sealed
    t = np.arange(n) / SR
    for ch in (0, 1):
        air = highpass(band(RNG.normal(0, 1, n), 5200, 15500), 5000)
        slow = 0.55 + 0.45 * np.sin(2 * np.pi * t / 11.0 + ch)
        y[:, ch] += air * (0.021 * (0.5 + 0.5 * slow))
    # the whole thing through the reference's spectrum, then a gentle top-down polish
    for _ in range(5):
        share = spectrum_share(y[:, 0])
        if max(abs(np.log((TARGET[k] + 1e-9) / (share[k] + 1e-9))) for k in TARGET) < 0.08:
            break
        for k, (lo, hi) in {"sub": (20, 120), "low": (120, 400), "mid": (400, 1500),
                            "hi": (1500, 5000), "air": (5000, 16000)}.items():
            g = float(np.clip((TARGET[k] / max(share[k], 1e-6)) ** 0.7, 0.3, 3.5))
            for c in (0, 1):
                y[:, c] += band(y[:, c], lo, hi) * (g - 1)
    y = np.stack([highpass(y[:, 0], 30), highpass(y[:, 1], 30)], 1)
    y = follow_reference_arc(y, seconds)
    f = int(0.05 * SR)
    y[:f] *= np.linspace(0, 1, f)[:, None]
    y[-f:] *= np.linspace(1, 0, f)[:, None]
    # the arc is relative: put the bed where a bed belongs (median 50 ms about -20.5 dBFS)
    # and let the effects and the final loudness stage do the rest. No peak clamping here --
    # clamping is what would flatten the very dynamics this function just built.
    w = int(0.05 * SR)
    m = y.mean(1)[: (y.shape[0] // w) * w].reshape(-1, w)
    med = float(np.median(np.sqrt((m ** 2).mean(1))))
    y *= 10 ** (-20.5 / 20.0) / max(med, 1e-9)
    return y


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=23.267)
    ap.add_argument("--out", default="audio/bed-23.wav")
    a = ap.parse_args()
    y = build(a.seconds)
    raw = (np.clip(y, -1, 1) * 2147483000).astype(np.int32).tobytes()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    w = subprocess.Popen([ffmpeg(), "-v", "error", "-y", "-f", "s32le", "-ar", str(SR), "-ac", "2",
                          "-i", "-", "-c:a", "pcm_s24le", a.out], stdin=subprocess.PIPE)
    w.stdin.write(raw)
    w.stdin.close()
    w.wait()
    got = spectrum_share(y[:, 0])
    print(f"  score {a.seconds:.3f}s -> {a.out}  peak {20 * np.log10(np.abs(y).max()):.1f} dBFS")
    print("  band share  target / got: " + "  ".join(f"{k} {TARGET[k]:.3f}/{got[k]:.3f}" for k in TARGET))
    for i in range(0, int(a.seconds)):
        seg = y[i * SR:(i + 1) * SR]
        if len(seg) < SR // 2:
            break
        print(f"    t={i:2d}s rms {20 * np.log10(max(np.sqrt((seg ** 2).mean()), 1e-9)):6.1f} dBFS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
