#!/usr/bin/env python3
"""
Audio: concatenate VO reels, time-stretch to the picture, then synthesize the
whole sound bed from the repo's design rules (monarch-sound-design) — ambience,
torch, wind, sub-boom transitions, riser, drone score, and a reverb tail.

Every cue is placed on a *stated* beat (chapter time), not on a vibe.
"""
import json, math, os, re, subprocess, sys
import numpy as np

SR = 48000
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
OUT = "out"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr[-2000:]); raise SystemExit(1)
    return p

def dur(p):
    o = subprocess.run([FF, "-i", p], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", o)
    h, mi, s = m.groups(); return int(h) * 3600 + int(mi) * 60 + float(s)

# ------------------------------------------------------------------ VO assembly
def build_vo(target_len, reels):
    # 1. concat with a fixed breath gap between reels
    gap = 0.42
    files = []
    tmpdir = os.path.join(OUT, "tmp"); os.makedirs(tmpdir, exist_ok=True)
    sil = os.path.join(tmpdir, "gap.wav")
    if not os.path.exists(sil):
        sh([FF, "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(gap), sil])
    parts = []
    for i, f in enumerate(reels):
        w = os.path.join(tmpdir, "vo_%02d.wav" % i)
        if not os.path.exists(w):
            sh([FF, "-y", "-i", f, "-ar", str(SR), "-ac", "1", w])
        parts += [w, sil]
    parts = parts[:-1]
    lis = os.path.join(tmpdir, "list.txt")
    open(lis, "w").write("".join("file '%s'\n" % os.path.abspath(p) for p in parts))
    raw = os.path.join(tmpdir, "vo_raw.wav")
    sh([FF, "-y", "-f", "concat", "-safe", "0", "-i", lis, "-c", "copy", raw])
    d = dur(raw)
    # 2. fit to picture: stretch only if needed, cap +12% so it stays natural
    ratio = target_len / d
    ratio = max(0.86, min(1.14, ratio))
    fitted = os.path.join(tmpdir, "vo_fit.wav")
    # atempo is chained for >2x; here it's always a single small factor
    sh([FF, "-y", "-i", raw, "-filter:a", f"atempo={ratio:.5f}",
        "-ar", str(SR), "-ac", "1", fitted])
    # 3. breath / pacing: tiny room reverb + gentle de-ess + level
    final = os.path.join(OUT, "vo_master.wav")
    sh([FF, "-y", "-i", fitted, "-filter:a",
        "highpass=f=70,lowpass=f=13500,"
        "acompressor=threshold=-18dB:ratio=2.6:attack=12:release=180,"
        "loudnorm=I=-16:TP=-1.5:LRA=9",
        "-ar", str(SR), "-ac", "1", final])
    return final, dur(raw), dur(fitted), ratio

# ------------------------------------------------------------------ synthesis

def t_(n): return np.arange(n, dtype=np.float32) / SR

def pink(n, rng):
    w = rng.normal(0, 1, n).astype(np.float32)
    # simple 1/f shaping in the frequency domain
    F = np.fft.rfft(w)
    f = np.fft.rfftfreq(n, 1 / SR)
    F = F / np.maximum(f, 20.0) ** 0.5
    out = np.fft.irfft(F, n).astype(np.float32)
    return out / (np.abs(out).max() + 1e-9)

def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    e = np.ones(n, np.float32)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n); e[:na] = np.linspace(0, 1, na) ** 0.6
    if nd and na + nd < n:
        e[na:na + nd] = np.linspace(1, s, nd)
        e[na + nd:] = s
    if nr and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr) ** 1.6
    return e

def bp(x, lo, hi, order=2):
    """Cheap zero-phase band-pass via FFT mask (deterministic, no scipy)."""
    n = len(x)
    F = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo > 0:
        m *= 1.0 / (1.0 + (lo / np.maximum(f, 1e-6)) ** (2 * order))
    if hi > 0:
        m *= 1.0 / (1.0 + (f / hi) ** (2 * order))
    return np.fft.irfft(F * m, n).astype(np.float32)

def whoosh(dur_, f0=280, f1=2600, gain=0.5, rng=None):
    n = int(dur_ * SR); rng = rng or np.random.default_rng(1)
    x = pink(n, rng)
    out = np.zeros(n, np.float32)
    chunk = 2048
    for i in range(0, n, chunk):
        t = i / max(n - 1, 1)
        fc = f0 + (f1 - f0) * t ** 1.7
        seg = x[i:i + chunk]
        out[i:i + chunk] = bp(seg, fc * 0.55, min(fc * 1.8, 18000), 2)
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2.0
    return (out * e * gain).astype(np.float32)

def sub_boom(dur_=1.5, f0=62, f1=34, gain=0.6):
    n = int(dur_ * SR); t = t_(n)
    f = f0 * (f1 / f0) ** (t / dur_)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 3.0)
    x += 0.25 * np.sin(2 * ph) * np.exp(-t * 5.0)
    # soft clip for body, then remove DC
    x = np.tanh(x * 1.6)
    return (x * gain).astype(np.float32)

def riser(dur_=2.2, gain=0.30, rng=None):
    n = int(dur_ * SR); rng = rng or np.random.default_rng(2)
    x = pink(n, rng)
    t = np.linspace(0, 1, n)
    # sweep a high band upward
    out = np.zeros(n, np.float32)
    chunk = 4096
    for i in range(0, n, chunk):
        tt = i / max(n - 1, 1)
        fc = 500 * (9.0 ** tt)
        out[i:i + chunk] = bp(x[i:i + chunk], fc * 0.7, min(fc * 1.9, 18000), 2)
    e = (t ** 2.2) * np.clip((1 - t) * 8, 0, 1)
    return (out / (np.abs(out).max() + 1e-9) * e * gain).astype(np.float32)

def torch_loop(n, rng):
    """Crackling fire: filtered noise bed + random micro crackles."""
    base = pink(n, rng) * 0.10
    base = bp(base, 120, 5200, 2)
    cr = np.zeros(n, np.float32)
    k = int(n / SR * 14)
    for _ in range(k):
        i = rng.integers(0, n - 2000)
        L = int(rng.integers(90, 900))
        burst = rng.normal(0, 1, L).astype(np.float32) * np.exp(-np.arange(L) / (L * 0.25))
        burst = bp(burst, 900, 7000, 1) * rng.uniform(0.05, 0.30)
        cr[i:i + L] += burst[:max(0, min(L, n - i))]
    return (base + cr).astype(np.float32)

def wind_loop(n, rng):
    x = pink(n, rng)
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * np.cumsum(np.full(n, 0.07, np.float32)) / SR)
    out = bp(x, 90, 900, 2) * mod
    return (out / (np.abs(out).max() + 1e-9) * 0.35).astype(np.float32)

def drone_score(n, chords, rng):
    """Slow organ-like drone, one chord per chapter, crossfaded. Mono-safe sub."""
    out = np.zeros(n, np.float32)
    per = n // len(chords)
    for i, ch in enumerate(chords):
        s = i * per
        e = min(n, s + per + int(1.6 * SR))
        m = e - s
        t = t_(m)
        seg = np.zeros(m, np.float32)
        for k, f in enumerate(ch):
            for det in (-0.19, 0.0, 0.21):
                ff = f * (1 + det / 100.0)
                seg += np.sin(2 * np.pi * ff * t + rng.uniform(0, 6.28)) * (0.55 if k == 0 else 0.30)
        seg *= (0.55 + 0.45 * np.sin(2 * np.pi * 0.045 * t + rng.uniform(0, 6.28)))
        # gentle low-pass so it sits under speech
        seg = bp(seg, 30, 2600, 2)
        envw = np.ones(m, np.float32)
        f = int(1.2 * SR)
        if i > 0: envw[:f] = np.linspace(0, 1, f) ** 1.4
        if i < len(chords) - 1: envw[-f:] *= np.linspace(1, 0, f) ** 1.4
        out[s:e] += seg * envw
    out = out / (np.abs(out).max() + 1e-9)
    return (out * 0.20).astype(np.float32)

# simple Schroeder-ish reverb (deterministic, no deps)
def reverb(x, mix=0.20, t60=2.2, rng=None):
    rng = rng or np.random.default_rng(3)
    n = len(x)
    ir_n = int(t60 * SR)
    ir = rng.normal(0, 1, ir_n).astype(np.float32) * np.exp(-np.arange(ir_n) / (t60 * SR / 6.9))
    ir = bp(ir, 180, 6500, 1)
    ir = ir / (np.abs(ir).sum() + 1e-9)
    wet = np.fft.irfft(np.fft.rfft(x, n + ir_n) * np.fft.rfft(ir, n + ir_n), n + ir_n)[:n].astype(np.float32)
    return (x * (1 - mix) + wet * mix * 8.0).astype(np.float32)

def place(track, clip, at, gain=1.0):
    s = int(at * SR)
    e = min(len(track), s + len(clip))
    if s >= len(track) or e <= s:
        return
    track[s:e] += clip[:e - s] * gain
