#!/usr/bin/env python3
"""
Score for the 60 s cut, written with the repo's own score grammar
(tools/film_score.py + tools/music_bed.py): a section list of chord, intensity,
kick rate and arp pattern, a slow dynamics arc, pads low-passed away from the
2-5 kHz harshness band, sub kept mono.
"""
import math, os, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

SR = 48000
NOTE = {"C": 16.35, "C#": 17.32, "D": 18.35, "D#": 19.45, "E": 20.60, "F": 21.83,
        "F#": 23.12, "G": 24.50, "G#": 25.96, "A": 27.50, "A#": 29.14, "B": 30.87}


def hz(name):
    n = NOTE[name[:-1]] * (2 ** (int(name[-1]) - 0))
    return n


def tone(f, n, amp, rng, kind="pad"):
    t = np.arange(n) / SR
    if kind == "pad":
        v = np.zeros(n)
        for det in (-0.11, 0.0, 0.13):
            v += np.sin(2 * np.pi * f * (1 + det / 100) * t + rng.uniform(0, 6.28))
        v += 0.25 * np.sin(2 * np.pi * f * 2 * t)
        v /= 2.6
        env = np.minimum(1.0, t / 0.35) * np.minimum(1.0, (n / SR - t) / 0.5)
        return v * env * amp
    # pluck / arp
    v = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.01 * t)
         + 0.12 * np.sin(2 * np.pi * f * 3.97 * t))
    return v * np.exp(-t * 4.2) * (1 - np.exp(-t * 500)) * amp


def lowpass(x, fc, order=2):
    n = len(x)
    F = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = 1 / (1 + (f / fc) ** (2 * order))
    return np.fft.irfft(F * m, n).astype(np.float32)


def st(x, pan):
    a = (pan + 1) * 0.25 * math.pi
    return np.stack([x * math.cos(a), x * math.sin(a)], 1)


# sections: (start, end, chord, intensity, kick_every, arp, rms_db)
SECTIONS = [
    (0.0, 9.0,   ["D2", "A2", "D3"], 0.34, 0.0,  None,                        -24.0),
    (9.0, 17.0,  ["D2", "F2", "A2"], 0.46, 0.0,  ["D4", "A4"],                -23.4),
    (17.0, 27.0, ["A#1", "D2", "F2"], 0.62, 1.20, ["F3", "A#3", "D4"],        -22.6),
    (27.0, 36.0, ["A#1", "D2", "F2", "A#2"], 0.86, 0.80, ["D4", "F4", "A#4"], -21.6),
    (36.0, 46.0, ["F1", "C2", "F2"], 0.55, 1.00, ["C4", "F4"],                -23.2),
    (46.0, 54.0, ["A1", "C#2", "E2"], 0.78, 0.70, ["E4", "A4", "C#5"],        -22.0),
    (54.0, 60.0, ["D2", "A2", "D3"], 0.40, 0.0,  None,                        -26.0),
]

RNG = np.random.default_rng(20261105)


def build(dur=60.0):
    n = int(dur * SR)
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    for (a, b, chord, inten, kick, arp, rms) in SECTIONS:
        i0, i1 = int(a * SR), int(min(b, dur) * SR)
        m = i1 - i0
        if m <= 0:
            continue
        pad = np.zeros(m, np.float32)
        for k, nm in enumerate(chord):
            pad += tone(hz(nm), m, 0.30 / (1 + 0.35 * k), RNG, "pad")
        pad = lowpass(pad, 1800, 2) * inten
        # section envelope, 0.6 s in/out
        f = int(0.6 * SR)
        env = np.ones(m, np.float32)
        if a > 0: env[:f] = np.linspace(0, 1, f) ** 1.3
        if b < dur: env[-f:] *= np.linspace(1, 0, f) ** 1.3
        pad *= env
        L[i0:i1] += pad
        R[i0:i1] += pad * 0.98
        if arp:
            step = 0.75
            t = a
            k = 0
            while t < b - 0.1:
                nm = arp[k % len(arp)]
                ln = int(1.4 * SR)
                v = lowpass(tone(hz(nm), ln, 0.14, RNG, "pluck"), 4200, 2)
                j0 = int(t * SR)
                mm = min(ln, n - j0)
                if mm > 0:
                    pan = 0.35 if k % 2 else -0.35
                    s = st(v[:mm], pan)
                    L[j0:j0 + mm] += s[:, 0] * env[:1][0] if False else s[:, 0] * inten
                    R[j0:j0 + mm] += s[:, 1] * inten
                t += step
                k += 1
        if kick:
            t = a
            while t < b - 0.05:
                ln = int(0.9 * SR)
                tt = np.arange(ln) / SR
                fk = 54 * np.exp(-tt * 26) + 38
                v = np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-tt * 10) * 0.30 * inten
                j0 = int(t * SR); mm = min(ln, n - j0)
                if mm > 0:
                    L[j0:j0 + mm] += v[:mm] * 0.7071
                    R[j0:j0 + mm] += v[:mm] * 0.7071
                t += kick
    # slow dynamics arc: breathe, never step
    sec = SR
    gain = np.ones(n, np.float32)
    arc = [0.75, 0.85, 1.0, 1.12, 0.9, 1.15, 0.7]
    for i in range(int(dur)):
        g = arc[min(i // 9, len(arc) - 1)]
        gain[i * sec:min(n, (i + 1) * sec)] = g
    k = int(2.0 * SR)
    ker = np.hanning(k); ker /= ker.sum()
    gain = np.convolve(gain, ker, "same").astype(np.float32)
    L *= gain; R *= gain
    # fit the level once, on the loudest moment, so the written dynamics arc
    # survives: six per-section peaks would flatten the whole score
    peak = max(np.abs(L).max(), np.abs(R).max(), 1e-9)
    return np.stack([L, R], 1) / peak * 0.72


if __name__ == "__main__":
    st_ = build()
    import wave
    p = os.path.join(os.path.dirname(__file__), "out", "score60.wav")
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(st_, -1, 1) * 32767).astype("<i2").tobytes())
    print("wrote", p, st_.shape, "peak %.3f" % np.abs(st_).max())
