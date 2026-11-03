#!/usr/bin/env python3
"""
MONARCH® Showreel v3 ("PROOF OVER PROMISES — ABSOLUTE CINEMA EDITION")
Python Studio DSP Music & Eargasm Foley Synthesizer + 60fps FFT Telemetry Exporter.

Generates:
1. `public/showreel/audio_master_60fps.m4a` (36.000s = 2,160 frames @ 60fps, 48kHz Stereo AAC)
   - Key: D Minor -> D Major 9 Picardy Finale | Tempo: 125 BPM (28.8 frames/beat)
   - Stems:
     * 7-voice detuned Juno/Prophet analog poly-pad (Dm9 -> Bbmaj9 -> Gm9 -> Asus4/A7b9) w/ 24dB LPF + sidechain pump
     * Karplus-Strong + warm glass-felt 16th-note arpeggio w/ stereo dotted-8th ping-pong delay
     * Warm Reese sub-bass (<135Hz mono-centered) + deep velvet kick + organic room clap + silk shaker
     * Zero-harshness ASMR foley: formant-filtered pink-noise silk whooshes, lubed "thock" cursor clicks,
       in-key Dm11 marimba-glass card deals, vacuum time-stops, and concert-hall velvet reverb (fftconvolve)
2. `public/showreel/audio_reactive.json` — exact per-frame (f=0..2159) sub/mid/high envelopes + 24-band FFT spectrum
   so the 60fps HTML5 Canvas shaders, volumetric god-rays, and holographic equalizer react with 0ms latency.
3. `showreel/beat_sheet.json` — frame-exact choreography map.
"""
import json
import os
import subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
import imageio_ffmpeg

SR = 48000
FPS = 60
TOTAL_FRAMES = 2160  # 36.000s @ 60.0 fps
DUR = TOTAL_FRAMES / FPS
BPM = 125.0
BEAT_S = 60.0 / BPM          # 0.480s (28.8 frames)
SIXTEENTH_S = BEAT_S / 4.0   # 0.120s (7.2 frames)

BEAT_SHEET = {
    "fps": FPS,
    "total_frames": TOTAL_FRAMES,
    "duration_s": DUR,
    "bpm": BPM,
    "card_deals": [308, 323, 337, 350, 362],
    "quad_pops": [666, 680, 694, 708],
    "rail_ticks": [1488, 1522, 1556, 1590],
    "seams": {
        "hook_click_portal": 148,
        "to_deck_deal": 288,
        "laser_scan_lock": 496,
        "crash_zoom_punch": 516,
        "to_cinema_monoliths": 648,
        "monolith_reframe_matrix": 852,
        "to_web_tunnel": 1050,
        "tunnel_zoom_maya": 1185,
        "tunnel_zoom_store": 1300,
        "web_vault_click": 1392,
        "to_vault_unlock": 1428,
        "vault_unlock_click": 1656,
        "to_finale_cinema": 1800,
    },
}


# ---------------- DSP FILTER & REVERB HELPERS ---------------- #
def midi_to_hz(m: float) -> float:
    return 440.0 * (2.0 ** ((m - 69.0) / 12.0))


def lpf(sig: np.ndarray, cutoff_hz: float, order: int = 4) -> np.ndarray:
    wn = np.clip(cutoff_hz / (SR * 0.5), 0.002, 0.98)
    sos = signal.butter(order, wn, btype="low", output="sos")
    return signal.sosfilt(sos, sig)


def bpf(sig: np.ndarray, low_hz: float, high_hz: float, order: int = 3) -> np.ndarray:
    lo = np.clip(low_hz / (SR * 0.5), 0.002, 0.95)
    hi = np.clip(high_hz / (SR * 0.5), lo + 0.005, 0.98)
    sos = signal.butter(order, [lo, hi], btype="band", output="sos")
    return signal.sosfilt(sos, sig)


def pink_noise(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    white = rng.standard_normal(n)
    # Voss-McCartney / spectral 1/sqrt(f) shaping
    spec = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    scale = 1.0 / np.sqrt(np.maximum(freqs, 20.0))
    pink = np.fft.irfft(spec * scale, n=n)
    mx = np.max(np.abs(pink)) + 1e-9
    return pink / mx



def _biquad(sig: np.ndarray, b, a) -> np.ndarray:
    return signal.lfilter(b, a, sig)


def peaking(sig: np.ndarray, f0: float, gain_db: float, q: float = 0.7) -> np.ndarray:
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * min(f0, SR * 0.45) / SR
    alpha = np.sin(w0) / (2 * q)
    b0 = 1 + alpha * A
    b1 = -2 * np.cos(w0)
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha / A
    return _biquad(sig, np.array([b0, b1, b2]) / a0, np.array([1.0, a1 / a0, a2 / a0]))


def high_shelf(sig: np.ndarray, f0: float, gain_db: float, slope: float = 1.0) -> np.ndarray:
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * min(f0, SR * 0.45) / SR
    cw, sw = np.cos(w0), np.sin(w0)
    alpha = sw / 2 * np.sqrt((A + 1 / A) * (1 / slope - 1) + 2)
    tsa = 2 * np.sqrt(A) * alpha
    b0 = A * ((A + 1) + (A - 1) * cw + tsa)
    b1 = -2 * A * ((A - 1) + (A + 1) * cw)
    b2 = A * ((A + 1) + (A - 1) * cw - tsa)
    a0 = (A + 1) - (A - 1) * cw + tsa
    a1 = 2 * ((A - 1) - (A + 1) * cw)
    a2 = (A + 1) - (A - 1) * cw - tsa
    return _biquad(sig, np.array([b0, b1, b2]) / a0, np.array([1.0, a1 / a0, a2 / a0]))


def hpf(sig: np.ndarray, f0: float, order: int = 3) -> np.ndarray:
    wn = np.clip(f0 / (SR * 0.5), 0.002, 0.95)
    return signal.sosfilt(signal.butter(order, wn, btype="high", output="sos"), sig)


def exciter(sig: np.ndarray, drive: float = 2.6, f0: float = 3400.0, amount: float = 0.34) -> np.ndarray:
    """Aural exciter: generates coherent upper harmonics from the existing mid band.
    Sounds expensive (analog air) instead of hissy, unlike plain noise shelves."""
    mid = bpf(sig, 900.0, 5200.0, order=2)
    harm = np.tanh(mid * drive)
    harm = hpf(harm, f0, order=3)
    harm = bpf(harm, f0, 12500.0, order=2)
    return sig + harm * amount


def air_band(sig: np.ndarray, f_lo: float, f_hi: float, amount: float) -> np.ndarray:
    """Additive studio-air sheen (band-limited, never harsh)."""
    band = bpf(sig, f_lo, f_hi, order=2)
    return sig + band * amount


def build_velvet_hall_ir(rt60: float = 2.15) -> np.ndarray:
    n = int(SR * rt60)
    t = np.linspace(0, rt60, n, endpoint=False)
    pre = int(0.020 * SR)  # 20ms pre-delay for transient clarity
    env = np.exp(-6.91 * t / rt60)
    # Smooth early buildup so reverb never clicks
    env *= np.minimum(1.0, t / 0.035)
    ir_l = np.roll(pink_noise(n, 901) * env, pre)
    ir_r = np.roll(pink_noise(n, 902) * env, pre + int(0.007 * SR))
    ir_l[:pre] = 0.0
    ir_r[:pre] = 0.0
    ir_l = bpf(ir_l, 165.0, 4100.0, order=2)
    ir_r = bpf(ir_r, 165.0, 4100.0, order=2)
    norm = np.sqrt(np.sum(ir_l**2) + 1e-9) * 1.45
    return np.stack([ir_l / norm, ir_r / norm], axis=1)


def apply_stereo_reverb(st: np.ndarray, ir: np.ndarray, wet: float = 0.34) -> np.ndarray:
    n = st.shape[0]
    wet_l = signal.fftconvolve(st[:, 0], ir[:, 0], mode="full")[:n]
    wet_r = signal.fftconvolve(st[:, 1], ir[:, 1], mode="full")[:n]
    # Subtle cross-feed for lush 3D width
    out_l = st[:, 0] + wet * (0.82 * wet_l + 0.18 * wet_r)
    out_r = st[:, 1] + wet * (0.82 * wet_r + 0.18 * wet_l)
    return np.stack([out_l, out_r], axis=1)


def apply_pingpong_delay(st: np.ndarray, delay_s: float, feedback: float = 0.38, wet: float = 0.28) -> np.ndarray:
    d = int(round(delay_s * SR))
    n = st.shape[0]
    dl = np.zeros(n, dtype=np.float64)
    dr = np.zeros(n, dtype=np.float64)
    mono = 0.5 * (st[:, 0] + st[:, 1])
    tap = lpf(mono, 3100.0, order=2)
    for k in range(1, 7):
        off = k * d
        if off >= n:
            break
        gain = (feedback ** k) * wet
        if k % 2 == 1:
            dl[off:] += tap[: n - off] * gain
        else:
            dr[off:] += tap[: n - off] * gain
        tap = lpf(tap, 2600.0, order=1)
    return np.stack([st[:, 0] + dl, st[:, 1] + dr], axis=1)


def add_mono(buf: np.ndarray, sig: np.ndarray, frame: float, pan: float = 0.0):
    idx = int(round((frame / FPS) * SR))
    if idx >= buf.shape[0]:
        return
    if idx < 0:
        sig = sig[-idx:]
        idx = 0
    n = min(len(sig), buf.shape[0] - idx)
    if n <= 0:
        return
    lg = np.sqrt(0.5 * (1.0 - np.clip(pan, -0.92, 0.92)))
    rg = np.sqrt(0.5 * (1.0 + np.clip(pan, -0.92, 0.92)))
    buf[idx : idx + n, 0] += sig[:n] * lg
    buf[idx : idx + n, 1] += sig[:n] * rg


def add_stereo(buf: np.ndarray, sig_st: np.ndarray, frame: float):
    idx = int(round((frame / FPS) * SR))
    if idx >= buf.shape[0]:
        return
    if idx < 0:
        sig_st = sig_st[-idx:]
        idx = 0
    n = min(sig_st.shape[0], buf.shape[0] - idx)
    if n <= 0:
        return
    buf[idx : idx + n] += sig_st[:n]


# ---------------- MUSICAL SYNTHESIS INSTRUMENTS ---------------- #
def synth_unison_chord(midi_notes, dur_s: float, cutoff_hz: float = 1350.0, gain: float = 0.22) -> np.ndarray:
    """7-voice detuned warm analog poly-synth chord with stereo spread & velvet 24dB LPF."""
    n = int(SR * dur_s)
    t = np.linspace(0, dur_s, n, endpoint=False)
    detunes_cents = [-15.0, -9.0, -3.5, 0.0, 3.5, 9.0, 15.0]
    pans = [-0.75, -0.45, -0.18, 0.0, 0.18, 0.45, 0.75]

    att = np.minimum(1.0, t / 0.14)
    rel = np.minimum(1.0, (dur_s - t) / 0.22)
    env = (att ** 1.3) * (rel ** 1.4)

    out_l = np.zeros(n, dtype=np.float64)
    out_r = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(int(sum(midi_notes) * 13))

    for m in midi_notes:
        base_f = midi_to_hz(m)
        for c, p in zip(detunes_cents, pans):
            f = base_f * (2.0 ** (c / 1200.0))
            ph0 = rng.uniform(0, 2 * np.pi)
            # Band-limited warm saw approximation (first 6 harmonics w/ soft rolloff)
            wave = np.zeros(n, dtype=np.float64)
            for h in range(1, 7):
                if f * h < 9000.0:
                    wave += ((-1) ** (h + 1)) * (1.0 / (h ** 1.18)) * np.sin(2 * np.pi * (f * h) * t + ph0 * h)
            lg = np.sqrt(0.5 * (1.0 - p))
            rg = np.sqrt(0.5 * (1.0 + p))
            out_l += wave * lg
            out_r += wave * rg

    norm = len(midi_notes) * 3.8
    out_l = lpf(np.tanh((out_l / norm) * 1.25), cutoff_hz, order=4) * env * gain
    out_r = lpf(np.tanh((out_r / norm) * 1.25), cutoff_hz, order=4) * env * gain
    for ch in (0, 1):
        v = hpf(np.stack([out_l, out_r], axis=1)[:, ch], 190.0, order=3)
        v = peaking(v, 340.0, -2.2, q=0.9)
        v = high_shelf(v, 4300.0, 2.8)
        if ch == 0:
            out_l = v
        else:
            out_r = v
    return np.stack([out_l, out_r], axis=1)


def synth_felt_glass_pluck(midi_note: float, dur_s: float = 0.55, velocity: float = 0.8) -> np.ndarray:
    """Warm felt-piano + glass-marimba hybrid pluck (zero harshness, pure ear candy)."""
    n = int(SR * dur_s)
    t = np.linspace(0, dur_s, n, endpoint=False)
    f = midi_to_hz(midi_note)

    # Soft 4ms felt attack so there is zero digital click
    att = np.minimum(1.0, t / 0.0045)
    body = (
        1.00 * np.sin(2 * np.pi * f * t) * np.exp(-t * 5.2)
        + 0.42 * np.sin(2 * np.pi * (f * 2.0) * t + 0.4) * np.exp(-t * 9.5)
        + 0.18 * np.sin(2 * np.pi * (f * 3.0) * t + 1.1) * np.exp(-t * 16.0)
        + 0.09 * np.sin(2 * np.pi * (f * 4.0) * t) * np.exp(-t * 26.0)
    )
    # Soft velvet mallet transient
    mallet = lpf(pink_noise(n, int(midi_note * 31)), 1900.0, order=3) * np.exp(-t * 75.0) * 0.22
    sig = (body + mallet) * att * (velocity * 0.30)
    sig = lpf(sig, 11000.0, order=2)
    sig = peaking(sig, 2900.0, 3.2, q=0.8)
    sig = high_shelf(sig, 6200.0, 3.6)
    return hpf(sig, 120.0, order=2)


def synth_reese_bass(midi_note: float, dur_s: float, gain: float = 0.34) -> np.ndarray:
    """Deep, silky mono-centered Reese sub-bass (<135Hz warm chest weight)."""
    n = int(SR * dur_s)
    t = np.linspace(0, dur_s, n, endpoint=False)
    f = midi_to_hz(midi_note)
    f1 = f * (2.0 ** (-9.0 / 1200.0))
    f2 = f * (2.0 ** (9.0 / 1200.0))

    # Rich detuned low harmonics + pure sub fundamental
    saw1 = np.sin(2 * np.pi * f1 * t) + 0.5 * np.sin(4 * np.pi * f1 * t) + 0.28 * np.sin(6 * np.pi * f1 * t)
    saw2 = np.sin(2 * np.pi * f2 * t + 0.8) + 0.5 * np.sin(4 * np.pi * f2 * t + 0.8) + 0.28 * np.sin(6 * np.pi * f2 * t)
    sub = np.sin(2 * np.pi * f * t) * 1.15

    att = np.minimum(1.0, t / 0.025)
    rel = np.minimum(1.0, (dur_s - t) / 0.045)
    raw = np.tanh((0.42 * (saw1 + saw2) + sub) * 1.2)
    return lpf(raw, 138.0, order=4) * att * rel * gain


# ---------------- VELVET DRUMS & CREAMY ASMR FOLEY ---------------- #
def kick_velvet(gain: float = 0.62) -> np.ndarray:
    dur = 0.38
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    # Smooth pitch sweep 118Hz -> 43Hz (deep chest punch, zero piercing click)
    freq = 43.0 + 75.0 * np.exp(-t * 32.0)
    ph = 2 * np.pi * np.cumsum(freq) / SR
    sub = np.sin(ph) * np.exp(-t * 7.8) * np.minimum(1.0, t / 0.002)
    # Warm felt-beater knock around 360Hz
    knock = np.sin(2 * np.pi * 360.0 * t) * np.exp(-t * 95.0) * 0.24
    return lpf(np.tanh((sub + knock) * 1.32), 1400.0, order=3) * gain


def clap_velvet(gain: float = 0.30) -> np.ndarray:
    dur = 0.20
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    base = bpf(pink_noise(n, 555), 750.0, 2700.0, order=3)
    # 3 organic micro-layered claps (0ms, 11ms, 22ms)
    env = (
        0.55 * np.exp(-t * 90.0)
        + 0.65 * np.where(t >= 0.011, np.exp(-np.maximum(0, t - 0.011) * 85.0), 0.0)
        + 0.85 * np.where(t >= 0.022, np.exp(-np.maximum(0, t - 0.022) * 34.0), 0.0)
    )
    wood = np.sin(2 * np.pi * 235.0 * t) * np.exp(-t * 55.0) * 0.35
    wires = bpf(pink_noise(n, 556), 2900.0, 7200.0, order=2) * env * 0.30
    return (base * env * 0.65 + wood + wires) * gain


def shaker_silk(accent: bool = False, gain: float = 0.165) -> np.ndarray:
    dur = 0.075 if not accent else 0.115
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    air = bpf(pink_noise(n, 777 if accent else 778), 6800.0, 13500.0, order=2)
    air = high_shelf(air, 9000.0, 3.0)
    env = np.sin(np.pi * np.minimum(1.0, t / 0.014)) * np.exp(-t * (28.0 if accent else 46.0))
    return air * env * (gain * (1.35 if accent else 1.0))


def thock_click(gain: float = 0.44) -> np.ndarray:
    """Creamy lubed custom mechanical switch / Leica shutter 'thock' (zero high-freq刺耳 beep!)."""
    dur = 0.095
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Downstroke: warm 155Hz mahogany resonance + 820Hz damped PBT keycap tap
    down_body = np.sin(2 * np.pi * 155.0 * t) * np.exp(-t * 95.0) * 0.72
    down_tap = np.sin(2 * np.pi * 820.0 * t) * np.exp(-t * 210.0) * 0.38
    down_felt = bpf(pink_noise(n, 303), 400.0, 1800.0, order=2) * np.exp(-t * 180.0) * 0.28
    # Soft upstroke 36ms later
    t2 = np.maximum(0.0, t - 0.036)
    up = np.where(
        t >= 0.036,
        (np.sin(2 * np.pi * 210.0 * t2) * 0.45 + np.sin(2 * np.pi * 1020.0 * t2) * 0.24) * np.exp(-t2 * 160.0),
        0.0,
    )
    tick = np.sin(2 * np.pi * 3100.0 * t) * np.exp(-t * 330.0) * 0.17
    return lpf(down_body + down_tap + down_felt + up + tick, 12000.0, order=2) * gain


def silk_whoosh(dur_s: float = 0.42, pan_start: float = -0.6, pan_end: float = 0.6, gain: float = 0.46) -> np.ndarray:
    """Hollywood formant-sculpted silk air whoosh + chest air push (ZERO sine laser whistle!)."""
    n = int(SR * dur_s)
    t = np.linspace(0, dur_s, n, endpoint=False)
    u = t / dur_s
    bell = np.sin(np.pi * u) ** 1.85

    p_noise = pink_noise(n, int(dur_s * 1000 + 17))
    low_band = bpf(p_noise, 110.0, 360.0, order=2) * (1.0 - np.abs(2 * u - 1.0))
    mid_band = bpf(p_noise, 340.0, 1150.0, order=2) * (np.sin(np.pi * u) ** 2.6)
    airy_band = bpf(p_noise, 1400.0, 6800.0, order=2) * (np.sin(np.pi * u) ** 3.4) * 0.62

    # Subtle 56Hz cinema chest air movement
    chest = np.sin(2 * np.pi * (52.0 + 24.0 * bell) * t) * bell * 0.28
    mono = (low_band * 0.65 + mid_band * 0.72 + airy_band + chest) * bell * gain

    pans = pan_start + (pan_end - pan_start) * u
    lg = np.sqrt(0.5 * (1.0 - np.clip(pans, -0.9, 0.9)))
    rg = np.sqrt(0.5 * (1.0 + np.clip(pans, -0.9, 0.9)))
    return np.stack([mono * lg, mono * rg], axis=1)


def musical_card_deal(midi_note: float, pan: float = 0.0, gain: float = 0.34) -> np.ndarray:
    """In-key marimba-glass harmonic tap + velvet paper slide."""
    dur = 0.28
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    paper = bpf(pink_noise(n, int(midi_note * 19)), 650.0, 2400.0, order=2) * np.exp(-t * 72.0) * 0.32
    thump = np.sin(2 * np.pi * 135.0 * t) * np.exp(-t * 68.0) * 0.42
    note = synth_felt_glass_pluck(midi_note, dur_s=dur, velocity=0.95) * 2.1
    mono = (paper + thump + note) * gain
    lg = np.sqrt(0.5 * (1.0 - pan))
    rg = np.sqrt(0.5 * (1.0 + pan))
    return np.stack([mono * lg, mono * rg], axis=1)


def cinema_sub_boom(dur_s: float = 1.25, root_hz: float = 36.71, gain: float = 0.68) -> np.ndarray:
    """Warm IMAX-style sub-drop + octave velvet bloom."""
    n = int(SR * dur_s)
    t = np.linspace(0, dur_s, n, endpoint=False)
    freq = root_hz + 68.0 * np.exp(-t * 19.0)
    ph = 2 * np.pi * np.cumsum(freq) / SR
    sub = np.sin(ph) * np.exp(-t * 2.6) * np.minimum(1.0, t / 0.004)
    warm_oct = np.tanh(1.5 * np.sin(ph * 2.0)) * np.exp(-t * 4.5) * 0.28
    felt_hit = bpf(pink_noise(n, 404), 120.0, 680.0, order=2) * np.exp(-t * 32.0) * 0.30
    mono = lpf(np.tanh((sub + warm_oct + felt_hit) * 1.28), 900.0, order=3) * gain
    return np.stack([mono, mono], axis=1)


# Master-chain knobs. Defaults are the shipped values; override for A/B measurement:
#   MONARCH_EXCITER=0 MONARCH_SHELF=3.0 MONARCH_LIMIT=0.62 python3 showreel/build_audio_60fps.py
EXC_AMOUNT = float(os.environ.get("MONARCH_EXCITER", "0.45"))
EXC_DRIVE = float(os.environ.get("MONARCH_EXC_DRIVE", "3.2"))
SHELF_6K = float(os.environ.get("MONARCH_SHELF", "6.2"))
LIMIT = os.environ.get("MONARCH_LIMIT", "0.62")  # AAC overshoots ~0.9 dB net; this lands -14.0 LUFS / ~-3.1 dBTP
STEM_DUMP = os.environ.get("MONARCH_STEM_DUMP")


def main():
    os.makedirs("showreel", exist_ok=True)
    os.makedirs("public/showreel", exist_ok=True)
    with open("showreel/beat_sheet.json", "w") as f:
        json.dump(BEAT_SHEET, f, indent=2)

    total_samples = int(SR * DUR)
    s = BEAT_SHEET["seams"]

    # Separate buses so harmonic stems get lush reverb/delay while sub-bass stays phase-locked!
    music_harmonic = np.zeros((total_samples, 2), dtype=np.float64)
    arp_bus = np.zeros((total_samples, 2), dtype=np.float64)
    sub_drums_bus = np.zeros((total_samples, 2), dtype=np.float64)
    sfx_bus = np.zeros((total_samples, 2), dtype=np.float64)

    # ---------- 1. INTRO ATMOSPHERE (0.0s -> 2.46s | f=0..148) ---------- #
    # Warm D-minor9 velvet swell before the portal click drop!
    intro_pad = synth_unison_chord([50, 57, 60, 64, 65], dur_s=2.45, cutoff_hz=1150.0, gain=0.19)
    add_stereo(music_harmonic, intro_pad, 0)
    intro_notes = [62, 65, 69, 76, 74, 69, 65, 64]
    for i, mn in enumerate(intro_notes):
        f_pos = i * 16
        if f_pos < 138:
            add_mono(arp_bus, synth_felt_glass_pluck(mn, 0.48, 0.72), f_pos, pan=(-0.35 if i % 2 == 0 else 0.35))

    # ---------- 2. MAIN CHORD PROGRESSION & HYPNOTIC ARPEGGIO (f=148..1788) ---------- #
    # Progression (each chord = 4 beats = 1.92s = 115.2 frames):
    # Dm9 -> Bbmaj9 -> Gm9 -> Asus4/A7b9 (repeats with rising filter openness & energy!)
    prog_chords = [
        {"pad": [50, 53, 57, 60, 64], "bass": 38, "arp": [62, 65, 69, 76, 72, 69, 65, 64]},  # Dm9 (D2 sub)
        {"pad": [46, 50, 53, 57, 60], "bass": 34, "arp": [58, 62, 65, 72, 69, 65, 62, 60]},  # Bbmaj9 (Bb1 sub)
        {"pad": [43, 46, 50, 53, 57], "bass": 31, "arp": [62, 67, 70, 74, 70, 67, 65, 62]},  # Gm9 (G1 sub)
        {"pad": [45, 50, 52, 55, 58], "bass": 33, "arp": [61, 64, 69, 74, 70, 69, 64, 57]},  # A7sus/b9 (A1 sub)
    ]

    bar_frames = BEAT_S * 4.0 * FPS  # 115.2 frames per 4-beat bar
    start_f = float(s["hook_click_portal"])
    end_groove_f = float(s["to_finale_cinema"] - 14)  # Vacuum hush 14 frames before Finale!

    bar_idx = 0
    cur_f = start_f
    while cur_f < end_groove_f - 20:
        ch = prog_chords[bar_idx % len(prog_chords)]
        dur_bar_s = min(BEAT_S * 4.0, (end_groove_f - cur_f) / FPS)
        # Filter opens gradually across the story arc (1100Hz -> 2150Hz) for rising emotion!
        cutoff = 1150.0 + 1650.0 * min(1.0, (cur_f - start_f) / (end_groove_f - start_f))
        pad_st = synth_unison_chord(ch["pad"], dur_s=dur_bar_s + 0.12, cutoff_hz=cutoff, gain=0.20)
        add_stereo(music_harmonic, pad_st, cur_f)

        # Reese sub-bass (2 sustained glides per bar)
        add_mono(sub_drums_bus, synth_reese_bass(ch["bass"], dur_s=dur_bar_s * 0.48, gain=0.275), cur_f)
        if dur_bar_s > BEAT_S * 2.1:
            add_mono(
                sub_drums_bus,
                synth_reese_bass(ch["bass"], dur_s=dur_bar_s * 0.48, gain=0.26),
                cur_f + BEAT_S * 2.0 * FPS,
            )

        # 16th-note Felt-Glass Arpeggio (16 steps per bar, 3+3+2 tresillo accent!)
        accents = {0, 3, 6, 8, 11, 14}
        arp_notes = ch["arp"]
        for step in range(16):
            sf = cur_f + step * (SIXTEENTH_S * FPS)
            if sf >= end_groove_f - 6:
                break
            # Respect micro-vacuum pockets before Crash-Zoom & Vault Unlock!
            if (s["crash_zoom_punch"] - 12 <= sf < s["crash_zoom_punch"]) or (
                s["vault_unlock_click"] - 12 <= sf < s["vault_unlock_click"]
            ):
                continue
            mn = arp_notes[step % len(arp_notes)]
            if step >= 8 and step % 4 == 3:
                mn += 12  # Sparkling upper octave shimmer on phrase turnarounds
            vel = 0.92 if step in accents else 0.56
            pan = np.sin(step * 0.85) * 0.42
            add_mono(arp_bus, synth_felt_glass_pluck(mn, 0.44, vel), sf, pan=pan)
            if cur_f >= 1050.0 and step in accents:
                spark = synth_felt_glass_pluck(mn + 24, 0.30, vel * 0.5)
                spark = hpf(spark, 4200.0, order=2)
                add_mono(arp_bus, spark * 0.30, sf, pan=-pan)

        cur_f += bar_frames
        bar_idx += 1

    # ---------- 3. DEEP HOUSE / CINEMA PERCUSSION + SIDECHAIN PUMP ---------- #
    sidechain = np.ones(total_samples, dtype=np.float64)
    beat_f = start_f
    beat_i = 0
    while beat_f < end_groove_f - 8:
        # Micro-hush right before Crash-Zoom (f=502..515) & Vault Unlock (f=1644..1655)
        in_pocket = (s["crash_zoom_punch"] - 15 <= beat_f < s["crash_zoom_punch"]) or (
            s["vault_unlock_click"] - 14 <= beat_f < s["vault_unlock_click"]
        )
        if not in_pocket:
            add_mono(sub_drums_bus, kick_velvet(gain=0.50), beat_f)
            # Carve smooth musical sidechain ducking on harmonic & sub buses!
            sc_idx = int(round((beat_f / FPS) * SR))
            sc_len = int(0.30 * SR)
            n_sc = min(sc_len, total_samples - sc_idx)
            if n_sc > 0:
                tsc = np.linspace(0, 1, n_sc)
                duck = 0.34 + 0.66 * (tsc ** 1.45)
                duck[: int(0.008 * SR)] = np.linspace(1.0, 0.34, min(n_sc, int(0.008 * SR)))
                sidechain[sc_idx : sc_idx + n_sc] = np.minimum(sidechain[sc_idx : sc_idx + n_sc], duck)

            if beat_i % 2 == 1:
                add_mono(sfx_bus, clap_velvet(gain=0.26), beat_f)

            # 16th silk shakers for effortless forward momentum
            for sub16 in range(4):
                sh_f = beat_f + sub16 * (SIXTEENTH_S * FPS)
                if sh_f < end_groove_f - 8:
                    add_mono(
                        sfx_bus,
                        shaker_silk(accent=(sub16 == 2), gain=0.155),
                        sh_f,
                        pan=(-0.28 if sub16 % 2 == 0 else 0.28),
                    )
        beat_f += BEAT_S * FPS
        beat_i += 1

    # Glass shimmer sustain: ultra-quiet high cluster tremolo = premium sparkle bed
    sh_len = int(SR * (end_groove_f / FPS))
    if sh_len > 0:
        tsh = np.linspace(0, sh_len / SR, sh_len, endpoint=False)
        trem = 0.55 + 0.45 * np.sin(2 * np.pi * (BPM / 60.0 / 2.0) * tsh) ** 2
        shim = np.zeros(sh_len, dtype=np.float64)
        for fhz, g in [(2349.3, 0.044), (2960.0, 0.030), (3520.0, 0.021), (4698.6, 0.013)]:
            shim += np.sin(2 * np.pi * fhz * tsh) * g
        shim *= trem * np.minimum(1.0, tsh / 1.2)
        shim = high_shelf(shim, 6000.0, 3.0)
        add_stereo(music_harmonic, np.stack([shim, np.roll(shim, 137) * 0.92], axis=1), start_f)

    # Apply sidechain pump to pad!
    music_harmonic[:, 0] *= sidechain
    music_harmonic[:, 1] *= sidechain

    # ---------- 3b. AIR BED (top-octave only, keeps the mix premium not brittle) ---------- #
    air_start = int(round((start_f / FPS) * SR))
    air_end = int(round((TOTAL_FRAMES * 0.97 / FPS) * SR))   # carry air through the finale
    if air_end > air_start:
        n_air = min(air_end - air_start, len(music_harmonic) - air_start)
        noise = pink_noise(n_air, seed=7)
        airband = bpf(noise, 7200.0, 11500.0, order=2)
        t_air = np.arange(n_air) / SR
        slow = 0.55 + 0.45 * np.sin(2 * np.pi * 0.23 * t_air + 0.7) ** 2
        swell = np.minimum(1.0, t_air / 2.5)
        # scale so the realistic shelf + exciter land the air band ~12 dB under presence
        # (reference scores sit 10-15 dB down; more than that reads dull, less reads brittle)
        air_sig = airband * slow * swell * 0.115
        add_stereo(music_harmonic, np.stack([air_sig, np.roll(air_sig, 211)], axis=1), start_f)

    # ---------- 4. FINALE PICARDY RESOLUTION (D MAJOR 9 | f=1800..2160) ---------- #
    # Triumphant, warm, emotional D-Major-9 swell (D2, A2, D3, F#3, A3, C#4, E4)
    finale_f = float(s["to_finale_cinema"])
    finale_pad = synth_unison_chord([38, 45, 50, 54, 57, 61, 64], dur_s=5.75, cutoff_hz=3000.0, gain=0.235)
    add_stereo(music_harmonic, finale_pad, finale_f)
    add_mono(sub_drums_bus, synth_reese_bass(38, dur_s=4.8, gain=0.30), finale_f)
    add_stereo(sub_drums_bus, cinema_sub_boom(1.6, root_hz=36.71, gain=0.66), finale_f)

    # Crystalline Dmaj9 harp-glass arpeggio flourish as MONARCH® STUDIO + Adil signature draws!
    finale_harp = [54, 57, 61, 64, 66, 69, 73, 76, 78]
    for i, mn in enumerate(finale_harp):
        add_mono(arp_bus, synth_felt_glass_pluck(mn, 1.35, 0.85), finale_f + 8 + i * 5.5, pan=-0.45 + i * 0.11)
    # Luxury shimmer: airy D6/A6 bells with slow bloom for goosebumps on the lockup
    for i, mn in enumerate([98, 102, 105]):
        bell = synth_felt_glass_pluck(mn, 3.6, 0.5)
        bell *= np.minimum(1.0, np.linspace(0, 1, len(bell)) / 0.25)
        bell = high_shelf(bell, 7000.0, 6.0)
        bell = exciter(bell, 2.2, 4200.0, 0.5)
        add_mono(arp_bus, bell * 0.85, finale_f + 24 + i * 14, pan=-0.5 + i * 0.5)

    # ---------- 5. FRAME-EXACT CREAMY CINEMA FOLEY (TOPIC-LOCKED!) ---------- #
    # Scene 01: Protagonist cursor glide -> Thock click -> Portal Iris Explosion (f=148)
    add_stereo(sfx_bus, silk_whoosh(0.38, 0.65, -0.35, 0.36), 112)
    add_mono(sfx_bus, thock_click(0.56), s["hook_click_portal"], pan=-0.22)
    add_stereo(sub_drums_bus, cinema_sub_boom(1.15, 36.71, 0.68), s["hook_click_portal"])
    add_stereo(sfx_bus, silk_whoosh(0.46, -0.5, 0.5, 0.42), s["hook_click_portal"])

    # Scene 02: Seam + 5-Card Musical Harmonic Deal (Dm11: D4, F4, A4, C5, E5)
    add_stereo(sfx_bus, silk_whoosh(0.36, 0.6, -0.5, 0.42), s["to_deck_deal"] - 8)
    deal_notes = [62, 65, 69, 72, 76]
    for k, cf in enumerate(BEAT_SHEET["card_deals"]):
        add_stereo(sfx_bus, musical_card_deal(deal_notes[k], pan=-0.4 + k * 0.2, gain=0.38), cf)

    # Laser Scan Lock (f=496) -> Crash-Zoom-Punch (f=516)!
    add_mono(sfx_bus, thock_click(0.45), s["laser_scan_lock"])
    add_stereo(sfx_bus, silk_whoosh(0.30, -0.2, 0.2, 0.44), s["crash_zoom_punch"] - 7)
    add_stereo(sub_drums_bus, cinema_sub_boom(1.05, 43.65, 0.68), s["crash_zoom_punch"])

    # Scene 03: 3D Cinema Monoliths + Mosaic Reframe
    add_stereo(sfx_bus, silk_whoosh(0.40, -0.65, 0.65, 0.44), s["to_cinema_monoliths"] - 8)
    pop_notes = [65, 69, 72, 74]
    for k, qf in enumerate(BEAT_SHEET["quad_pops"]):
        add_stereo(sfx_bus, musical_card_deal(pop_notes[k], pan=(-0.45 if k % 2 == 0 else 0.45), gain=0.34), qf)
    add_stereo(sfx_bus, silk_whoosh(0.36, 0.5, -0.5, 0.38), s["monolith_reframe_matrix"] - 6)
    add_stereo(sub_drums_bus, cinema_sub_boom(0.85, 36.71, 0.48), s["monolith_reframe_matrix"])

    # Scene 04: 3D Web Z-Tunnel Zoom-Throughs + Vault CTA Click
    add_stereo(sfx_bus, silk_whoosh(0.45, -0.4, 0.4, 0.46), s["to_web_tunnel"] - 9)
    add_stereo(sfx_bus, silk_whoosh(0.38, -0.3, 0.3, 0.40), s["tunnel_zoom_maya"] - 6)
    add_stereo(sfx_bus, silk_whoosh(0.38, 0.3, -0.3, 0.40), s["tunnel_zoom_store"] - 6)
    add_mono(sfx_bus, thock_click(0.58), s["web_vault_click"], pan=-0.2)

    # Scene 05: Biometric Vault + 4-Rail Harmonic Ignition + Master Unlock Chord!
    add_stereo(sfx_bus, silk_whoosh(0.34, -0.4, 0.4, 0.40), s["to_vault_unlock"] - 6)
    rail_midi = [62, 66, 69, 74]  # D4 - F#4 - A4 - D5 rising confidence!
    for k, rf in enumerate(BEAT_SHEET["rail_ticks"]):
        add_mono(arp_bus, synth_felt_glass_pluck(rail_midi[k], 0.55, 0.88), rf, pan=0.25)
        add_mono(sfx_bus, thock_click(0.28), rf, pan=0.25)

    # Vault Unlock Click (f=1656): Creamy Thock + Sub Boom + Emerald Dmaj9 Shimmer!
    add_mono(sfx_bus, thock_click(0.62), s["vault_unlock_click"], pan=0.18)
    add_stereo(sub_drums_bus, cinema_sub_boom(1.1, 36.71, 0.64), s["vault_unlock_click"])
    unlock_shimmer = synth_unison_chord([62, 66, 69, 73, 76], dur_s=2.1, cutoff_hz=3200.0, gain=0.24)
    add_stereo(music_harmonic, unlock_shimmer, s["vault_unlock_click"])

    # Scene 06: Anamorphic Lens Flare Sweep into Finale (f=1800)
    add_stereo(sfx_bus, silk_whoosh(0.65, -0.8, 0.8, 0.44), s["to_finale_cinema"] - 8)

    # ---------- 6. STUDIO FX CHAIN (PING-PONG DELAY + VELVET HALL REVERB) ---------- #
    print("[DSP 1/3] Convolving stereo ping-pong delay & 2.15s velvet concert-hall IR...")
    ir = build_velvet_hall_ir(rt60=2.15)
    arp_fx = apply_pingpong_delay(arp_bus, delay_s=SIXTEENTH_S * 3.0, feedback=0.38, wet=0.30)
    arp_fx = apply_stereo_reverb(arp_fx, ir, wet=0.40)
    pad_fx = apply_stereo_reverb(music_harmonic, ir, wet=0.38)
    sfx_fx = apply_stereo_reverb(sfx_bus, ir, wet=0.22)

    master = pad_fx + arp_fx + sub_drums_bus + sfx_fx

    # Analog studio air bed (expensive-sounding top end, never hissy/harsh)
    n_tot = master.shape[0]
    air = bpf(pink_noise(n_tot, 1201), 3200.0, 13500.0, order=2)
    air2 = bpf(pink_noise(n_tot, 1202), 3200.0, 13500.0, order=2)
    air_gain = 0.026
    bed = np.stack([air * air_gain, air2 * air_gain], axis=1)
    bed *= np.minimum(1.0, np.linspace(0, 1, n_tot) / (SR * 0.35))[:, None]
    master += bed

    # Vacuum low-pass/gain dip on the 12 frames right before Finale (f=1786..1799) for maximum goosebumps!
    vac_a = int(round((1786 / FPS) * SR))
    vac_b = int(round((1800 / FPS) * SR))
    vac_curve = np.linspace(1.0, 0.08, vac_b - vac_a) ** 1.6
    master[vac_a:vac_b, 0] *= vac_curve
    master[vac_a:vac_b, 1] *= vac_curve

    # Finale = the emotional peak, not a fade-out. The Picardy section gets +2.6 dB
    # (0.45 s ease so it never slams) and only the last 1.1 s fades.
    # v3 measured LRA 2.0 LU because the last 5 s sat 3 dB *under* the body; making the
    # climax louder instead of quieter is what gives a real dynamic arc.
    fin_a, fin_b = int(30.0 * SR), int(35.2 * SR)
    if fin_b > fin_a:
        ramp = np.minimum(1.0, np.arange(fin_b - fin_a) / (0.45 * SR)) ** 3.0   # shape, not level
        master[fin_a:fin_b, 0] *= 1.0 + 0.04 * ramp
        master[fin_a:fin_b, 1] *= 1.0 + 0.04 * ramp

    fade_start = max(0, total_samples - int(0.62 * SR))
    fade_n = total_samples - fade_start
    fade_curve = np.linspace(1.0, 0.0, fade_n) ** 2.0
    master[fade_start:, 0] *= fade_curve
    master[fade_start:, 1] *= fade_curve

    # ---------- STUDIO MASTER BUS EQ (clarity + presence + air) ----------
    for ch in (0, 1):
        v = master[:, ch]
        v = hpf(v, 27.0, order=3)                 # rumble guard
        v = peaking(v, 320.0, -2.4, q=0.8)        # de-mud for translation
        v = peaking(v, 2500.0, 2.8, q=0.8)       # vocal-band presence / snap
        if EXC_AMOUNT > 0:
            v = exciter(v, drive=EXC_DRIVE, f0=3000.0, amount=EXC_AMOUNT)   # analog air / presence
        v = high_shelf(v, 6800.0, SHELF_6K)       # open top
        v = high_shelf(v, 11000.0, 3.6)           # premium air
        master[:, ch] = v

    # ---------- 6a. SECTION GAIN AUTOMATION (real dynamics, not compressor tricks) ---------- #
    # v3 measured LRA 2.0 LU: one flat dynamic for 30 s. These are section-level gains with
    # 0.4 s crossfades, so the build stays under the drop and the pay-off lands harder.
    section_gain = [
        (0.0, 2.55, 1.00),    # hook (already lifted below)
        (2.55, 8.5, 0.83),    # deck / build  -1.6 dB
        (8.5, 17.5, 0.90),    # monoliths     -0.9 dB
        (17.5, 23.8, 1.00),   # tunnel
        (23.8, 30.0, 1.06),   # vault         +0.5 dB
        (30.0, 36.0, 1.15),   # finale        +1.2 dB
    ]
    gain_curve = np.ones(len(master))
    for a_s, b_s, g in section_gain:
        a, b = int(a_s * SR), min(int(b_s * SR), len(master))
        if b <= a:
            continue
        ramp_n = max(1, int(0.4 * SR))
        ramp = np.ones(b - a)
        head = min(ramp_n, b - a)
        ramp[:head] = np.linspace(gain_curve[a], g, head) if a > 0 else g
        gain_curve[a:b] = ramp * g
    # smooth the whole curve so no step can click
    k = np.hanning(int(0.06 * SR)); k /= k.sum()
    gain_curve = np.convolve(gain_curve, k, mode="same")
    gain_curve = np.clip(gain_curve, 0.75, 1.25)
    master *= gain_curve[:, None]

    # ---------- 6b. BODY = THE FIX FOR "NO BODY" ---------- #
    # Measured on v3: hook -19.5 dBFS vs deck -14.7 dBFS (4.8 dB hole at the top),
    # and only ~1.4 dB of movement across 27 s of body. Fix both here, in the mix.
    body_curve = np.ones(len(master))
    hooks = int(round(2.55 * SR))
    body_curve[:hooks] = 1.0 + 0.55 * (1.0 - np.linspace(0, 1, hooks)) ** 0.7   # 8.9 dB at t=0
    master *= body_curve[:, None]

    if STEM_DUMP:
        # pre-master-bus stem for offline A/B of the mastering chain
        wavfile.write(STEM_DUMP, SR, (master / (np.abs(master).max() + 1e-9) * 0.9 * 32767).astype(np.int16))
        print(f"[stems] wrote {STEM_DUMP}")

    # Soft analog tape saturation ceiling
    peak = np.max(np.abs(master)) + 1e-9
    master = np.tanh((master / peak) * 1.14) * 0.90

    # ---------- 7. EXPORT 60FPS FFT REACTIVE TELEMETRY FOR CANVAS SHADERS ---------- #
    print("[DSP 2/3] Extracting 2,160-frame @ 60fps real-time FFT spectrum & sub/mid/high envelopes...")
    mono_an = 0.5 * (master[:, 0] + master[:, 1])
    spf = SR // FPS  # 800 samples per 60fps frame exact!
    win = np.hanning(2048)
    freqs = np.fft.rfftfreq(2048, d=1.0 / SR)
    # 24 log-spaced visual frequency edges from 38Hz to 8500Hz
    edges = np.geomspace(38.0, 8500.0, 25)

    subs, mids, highs, bins_all = [], [], [], []
    for f in range(TOTAL_FRAMES):
        center = f * spf + spf // 2
        s0 = max(0, center - 1024)
        chunk = np.zeros(2048, dtype=np.float64)
        seg = mono_an[s0 : min(total_samples, s0 + 2048)]
        chunk[: len(seg)] = seg
        mag = np.abs(np.fft.rfft(chunk * win))

        sub_e = float(np.mean(mag[(freqs >= 35) & (freqs < 130)]))
        mid_e = float(np.mean(mag[(freqs >= 130) & (freqs < 1600)]))
        hi_e = float(np.mean(mag[(freqs >= 1600) & (freqs < 8500)]))
        subs.append(sub_e)
        mids.append(mid_e)
        highs.append(hi_e)

        b24 = []
        for bi in range(24):
            mask = (freqs >= edges[bi]) & (freqs < edges[bi + 1])
            val = float(np.mean(mag[mask])) if np.any(mask) else 0.0
            # Frequency-tilt compensation so higher bars dance visibly
            b24.append(val * ((bi + 1) ** 0.52))
        bins_all.append(b24)

    def norm_arr(a):
        arr = np.array(a, dtype=np.float64)
        p98 = np.percentile(arr, 98.5) + 1e-9
        return [round(float(np.clip(v / p98, 0.0, 1.0)), 3) for v in arr]

    bins_np = np.array(bins_all, dtype=np.float64)
    bins_p98 = np.percentile(bins_np, 98.5) + 1e-9
    bins_quant = np.clip(np.round((bins_np / bins_p98) * 100.0), 0, 100).astype(int).tolist()

    telemetry = {
        "fps": FPS,
        "frames": TOTAL_FRAMES,
        "sub": norm_arr(subs),
        "mid": norm_arr(mids),
        "high": norm_arr(highs),
        "bins": bins_quant,
    }
    arc = {
        "hook": [0, 148], "deck": [148, 516], "monoliths": [516, 1050],
        "tunnel": [1050, 1428], "vault": [1428, 1800], "finale": [1800, 2160],
    }
    with open("showreel/beat_sheet.json", "w") as f:
        json.dump({**BEAT_SHEET, "arc": arc, "loudness_target": {"integrated_lufs": -14.0, "true_peak_dbtp": -1.5}}, f, indent=2)

    with open("public/showreel/audio_reactive.json", "w") as f:
        json.dump(telemetry, f, separators=(",", ":"))

    # ---------- 8. EBU R128 BROADCAST MASTERING (-14.5 LUFS / <= -1.8 dBTP) ---------- #
    print("[DSP 3/3] Mastering to 48kHz Stereo AAC (-14.5 LUFS, True Peak <= -1.8 dBTP)...")
    raw_wav = "/tmp/monarch_v3_raw.wav"
    out_m4a = "public/showreel/audio_master_60fps.m4a"
    wavfile.write(raw_wav, SR, (master * 32767.0).astype(np.int16))

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            raw_wav,
            "-af",
            "acompressor=threshold=0.42:ratio=1.6:attack=8:release=180:makeup=1.0,"
            f"loudnorm=I=-14.6:TP=-2.2:LRA=9.0,aresample=48000,alimiter=limit={LIMIT}:level=false",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-t",
            f"{DUR:.3f}",
            out_m4a,
        ],
        check=True,
        capture_output=True,
    )

    qc = subprocess.run(
        [ffmpeg, "-i", out_m4a, "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    for line in qc.stderr.splitlines():
        if any(k in line for k in ["Duration:", "I:", "Peak:"]):
            print(" ", line.strip())


if __name__ == "__main__":
    main()
