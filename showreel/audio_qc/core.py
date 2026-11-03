"""
Core measurement primitives for MONARCH audio QC.

Pure numpy/scipy. Decodes with the ffmpeg binary shipped by imageio-ffmpeg when the
input is not already a wav. Everything returns plain dicts/lists so it can be
serialised to JSON and read by the app.

Bands are fixed so that two files are always compared on the same grid.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from typing import Iterable

import numpy as np
from scipy import signal

SAMPLE_RATE = 48000

# Eight bands used everywhere. Edges in Hz.
BANDS = [
    ("sub", 20, 60),
    ("bass", 60, 120),
    ("low_mid", 120, 250),
    ("mid", 250, 500),
    ("high_mid", 500, 1000),
    ("presence", 1000, 2500),
    ("harsh", 2500, 5000),      # the band that makes things read as "irritating"
    ("air", 5000, 12000),
]


def _ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # pragma: no cover - fallback for CI images with system ffmpeg
        return "ffmpeg"


def load_audio(path: str, sr: int = SAMPLE_RATE) -> tuple[np.ndarray, int]:
    """Return (samples[N,2] float32 in -1..1, sample_rate). Mono files are duplicated."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    if path.lower().endswith(".wav"):
        from scipy.io import wavfile
        rate, data = wavfile.read(path)
        x = data.astype(np.float32)
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        peak = np.abs(x).max()
        if peak > 1.5:  # integer PCM
            x = x / 32768.0
    else:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            out = tmp.name
        try:
            subprocess.run(
                [_ffmpeg_exe(), "-v", "error", "-y", "-i", path,
                 "-ac", "2", "-ar", str(sr), "-f", "wav", out],
                check=True, capture_output=True,
            )
            from scipy.io import wavfile
            rate, data = wavfile.read(out)
            x = data.astype(np.float32)
            if x.ndim == 1:
                x = np.stack([x, x], axis=1)
            if np.abs(x).max() > 1.5:
                x = x / 32768.0
        finally:
            if os.path.exists(out):
                os.unlink(out)

    if rate != sr:
        g = np.gcd(int(rate), int(sr))
        x = signal.resample_poly(x, sr // g, int(rate) // g, axis=0)
        rate = sr
    return x.astype(np.float32), int(rate)


def band_energy_curve(x: np.ndarray, sr: int = SAMPLE_RATE, hop_s: float = 0.25,
                      nfft: int = 4096) -> dict:
    """Per-band energy over time. x is mono 1-D. Returns {band: [dB per hop]}."""
    mono = x if x.ndim == 1 else x.mean(axis=1)
    hop = max(1, int(hop_s * sr))
    f, t, Z = signal.stft(mono, fs=sr, nperseg=nfft, noverlap=nfft - hop, window="hann")
    power = np.abs(Z) ** 2
    out = {}
    for name, lo, hi in BANDS:
        sel = (f >= lo) & (f < hi)
        e = power[sel].sum(axis=0)
        out[name] = (10 * np.log10(np.maximum(e, 1e-12))).tolist()
    out["_t"] = t.tolist()
    return out


def _k_weight(x: np.ndarray, sr: int) -> np.ndarray:
    """ITU-R BS.1770 K-weighting (high shelf + high pass)."""
    # stage 1: high shelf
    f0, gain_db, q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2 * q)
    b1 = [A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha),
          -2 * A * ((A - 1) + (A + 1) * np.cos(w0)),
          A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)]
    a1 = [(A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha,
          2 * ((A - 1) - (A + 1) * np.cos(w0)),
          (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha]
    # stage 2: high pass
    f0b, qb = 38.13547087602444, 0.5003270373238773
    w0b = 2 * np.pi * f0b / sr
    alphab = np.sin(w0b) / (2 * qb)
    b2 = [1.0, -2.0, 1.0]
    a2 = [1 + alphab, -2 * np.cos(w0b), 1 - alphab]
    y = signal.lfilter(np.array(b1) / a1[0], np.array(a1) / a1[0], x)
    y = signal.lfilter(np.array(b2) / a2[0], np.array(a2) / a2[0], y)
    return y


def loudness_stats(x: np.ndarray, sr: int = SAMPLE_RATE) -> dict:
    """Integrated LUFS (BS.1770 gated), LRA approximation, true peak estimate."""
    mono = x if x.ndim == 1 else x
    if mono.ndim > 1:
        # BS.1770 sums channel powers with channel weights G_c = 1.0 for L/R.
        # Averaging instead of summing introduces a -3.01 dB error on stereo.
        kw = np.stack([_k_weight(mono[:, c], sr) for c in range(mono.shape[1])], axis=1)
        power = (kw ** 2).sum(axis=1)
    else:
        power = _k_weight(mono, sr) ** 2

    block = int(0.4 * sr)
    step = int(0.1 * sr)
    if len(power) < block:
        raise ValueError("audio shorter than one 400 ms block")
    n = 1 + (len(power) - block) // step
    blocks = np.array([power[i * step:i * step + block].mean() for i in range(n)])
    lufs_blocks = -0.691 + 10 * np.log10(np.maximum(blocks, 1e-12))

    # absolute gate -70, relative gate -10 below the ungated mean
    kept = lufs_blocks[lufs_blocks > -70]
    if kept.size == 0:
        integrated = -70.0
    else:
        rel = -0.691 + 10 * np.log10(np.mean(10 ** ((kept + 0.691) / 10))) - 10
        final = kept[kept > rel]
        integrated = -0.691 + 10 * np.log10(np.mean(10 ** ((final + 0.691) / 10)))

    short = np.convolve(lufs_blocks, np.ones(30) / 30, mode="valid") if lufs_blocks.size >= 30 else lufs_blocks
    lra = float(np.percentile(short, 95) - np.percentile(short, 10))

    peak = float(np.abs(x).max())
    true_peak = 20 * np.log10(peak + 1e-12)
    clipped = int(np.sum(np.abs(x) >= 0.999))
    dc = float(np.mean(x, axis=0).tolist()[0] if x.ndim > 1 else np.mean(x))

    return {
        "integrated_lufs": round(float(integrated), 2),
        "lra_lu": round(lra, 2),
        "sample_peak_dbfs": round(true_peak, 2),
        "clipped_samples": clipped,
        "dc_offset": round(abs(dc), 6),
        "duration_s": round(len(x) / sr, 3),
    }


def spectral_profile(x: np.ndarray, sr: int = SAMPLE_RATE) -> dict:
    """Long-term band balance in dB, plus the harshness ratio that predicts 'irritating'."""
    mono = x if x.ndim == 1 else x.mean(axis=1)
    f, p = signal.welch(mono, fs=sr, nperseg=8192)
    out, total = {}, 0.0
    for name, lo, hi in BANDS:
        sel = (f >= lo) & (f < hi)
        e = float(p[sel].sum())
        out[name] = e
        total += e
    db = {k: round(10 * np.log10(max(v, 1e-18) / max(total, 1e-18)), 2) for k, v in out.items()}
    ref = db["high_mid"]
    harsh_ratio = round(db["harsh"] - ref, 2)
    air_ratio = round(db["air"] - ref, 2)
    return {
        "band_db_rel_total": db,
        "harsh_over_high_mid_db": harsh_ratio,
        "air_over_high_mid_db": air_ratio,
        "harsh": harsh_ratio > 2.0,
        "dull": air_ratio < -18.0,
    }


def onset_density(x: np.ndarray, sr: int = SAMPLE_RATE, hop_s: float = 1.0) -> dict:
    """Events per second, per window. A crude but useful 'how busy is this' curve."""
    mono = x if x.ndim == 1 else x.mean(axis=1)
    env = np.abs(signal.hilbert(mono))
    win = int(0.02 * sr)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    d = np.diff(env, prepend=env[0])
    thresh = np.percentile(d, 99.0)
    idx = signal.find_peaks(d, height=max(thresh, 1e-5), distance=int(0.06 * sr))[0]
    hop = int(hop_s * sr)
    counts = []
    for start in range(0, len(mono), hop):
        counts.append(int(np.sum((idx >= start) & (idx < start + hop))))
    return {"onsets_per_s": counts, "total_onsets": int(len(idx)),
            "mean_per_s": round(float(np.mean(counts)), 2)}


def analyse(path: str) -> dict:
    x, sr = load_audio(path)
    mono = x.mean(axis=1)
    return {
        "path": os.path.basename(path),
        "loudness": loudness_stats(x, sr),
        "spectrum": spectral_profile(x, sr),
        "bands": band_energy_curve(mono, sr),
        "onsets": onset_density(mono, sr),
    }
