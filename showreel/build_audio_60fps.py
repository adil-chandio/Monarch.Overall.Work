#!/usr/bin/env python3
"""
MONARCH® Showreel v2 ("PROOF OVER PROMISES") — Frame-Accurate 60fps Audio Engine.
Synthesizes a 120 BPM dark-luxury electronic pulse + frame-locked tactile UI foley
matched to `showreel/beat_sheet.json` (1,920 frames @ 60.0 fps = 32.000s),
mastered to EBU R128 -14 LUFS / <= -1.5 dBTP via FFmpeg loudnorm.
Zero external API credits required.
"""
import json
import os
import re
import subprocess
import numpy as np
from scipy.io import wavfile
import imageio_ffmpeg

SR = 48000
FPS = 60
TOTAL_FRAMES = 1920
DUR = TOTAL_FRAMES / FPS  # 32.000s exact

BEAT_SHEET = {
    "fps": FPS,
    "total_frames": TOTAL_FRAMES,
    "duration_s": DUR,
    "bpm": 120,
    "card_deals": [258, 276, 291, 303, 313, 321],
    "quad_pops": [582, 594, 606, 618],
    "rail_ticks": [1410, 1440, 1470, 1500],
    "seams": {
        "hook_click_invert": 120,
        "to_deck_deal": 240,
        "target_brackets": 435,
        "crash_zoom_punch": 450,
        "to_quad_films": 570,
        "quad_hero_badge": 780,
        "to_web_3d": 960,
        "web_slide_maya": 1110,
        "web_slide_store": 1215,
        "web_vault_click": 1314,
        "to_vault_unlock": 1350,
        "vault_unlock_click": 1560,
        "to_finale_lockup": 1680,
    },
}


def add_at(buf: np.ndarray, sig: np.ndarray, frame: float, pan: float = 0.0):
    idx = int(round((frame / FPS) * SR))
    if idx >= buf.shape[0] or idx < 0:
        return
    n = min(len(sig), buf.shape[0] - idx)
    if n <= 0:
        return
    l_gain = np.sqrt(0.5 * (1.0 - np.clip(pan, -0.9, 0.9)))
    r_gain = np.sqrt(0.5 * (1.0 + np.clip(pan, -0.9, 0.9)))
    buf[idx : idx + n, 0] += sig[:n] * l_gain
    buf[idx : idx + n, 1] += sig[:n] * r_gain


def kick_808(dur=0.36, f_start=135.0, f_end=38.0, gain=0.65):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    freq = f_end + (f_start - f_end) * np.exp(-t * 28.0)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-t * 8.5)
    click = np.exp(-t * 180.0) * np.sin(2 * np.pi * 1600 * t) * 0.28
    return np.tanh((np.sin(phase) * env + click) * 1.35) * gain


def snare_rim(dur=0.14, gain=0.30):
    rng = np.random.default_rng(42)
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    body = np.sin(2 * np.pi * 210 * t) * np.exp(-t * 42.0) * 0.6
    noise = rng.standard_normal(len(t)) * np.exp(-t * 34.0) * 0.55
    return (body + noise) * gain


def hat_tick(dur=0.045, open_hat=False, gain=0.11):
    if open_hat:
        dur = 0.16
    rng = np.random.default_rng(108)
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    # High-passed metallic noise
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0.0)
    n = np.diff(n, prepend=0.0) * 0.35
    decay = 16.0 if open_hat else 65.0
    return n * np.exp(-t * decay) * gain


def cursor_click(gain=0.48):
    # Two-part macOS mechanical microswitch tap (down + release 35ms later)
    dur = 0.085
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    down = (np.sin(2 * np.pi * 2400 * t) + 0.6 * np.sin(2 * np.pi * 4900 * t)) * np.exp(-t * 190.0)
    t2 = np.maximum(0.0, t - 0.034)
    up = np.where(t >= 0.034, np.sin(2 * np.pi * 3200 * t2) * np.exp(-t2 * 220.0) * 0.55, 0.0)
    return (down + up) * gain


def whoosh(dur=0.28, f0=180.0, f1=1100.0, gain=0.34):
    rng = np.random.default_rng(77)
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    env = np.maximum(0.0, np.sin(np.pi * (t / dur))) ** 1.8
    sweep = f0 + (f1 - f0) * (t / dur) ** 1.5
    ph = 2 * np.pi * np.cumsum(sweep) / SR
    air = rng.standard_normal(len(t)) * 0.28
    air = np.convolve(air, np.ones(9) / 9.0, mode="same")
    return (np.sin(ph) * 0.45 + air) * env * gain


def card_snap(pitch_mult=1.0, gain=0.36):
    dur = 0.09
    rng = np.random.default_rng(int(pitch_mult * 1000))
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    thud = np.sin(2 * np.pi * (150 * pitch_mult) * t) * np.exp(-t * 48.0) * 0.65
    paper = np.diff(rng.standard_normal(len(t)), prepend=0.0) * np.exp(-t * 85.0) * 0.35
    return (thud + paper) * gain


def riser(dur=0.65, f0=110.0, f1=780.0, gain=0.28):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    u = (t / dur) ** 2.2
    freq = f0 + (f1 - f0) * u
    ph = 2 * np.pi * np.cumsum(freq) / SR
    return (np.sin(ph) + 0.4 * np.sin(ph * 1.5)) * u * gain


def sub_impact(dur=0.95, gain=0.72):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    freq = 42.0 + 115.0 * np.exp(-t * 22.0)
    ph = 2 * np.pi * np.cumsum(freq) / SR
    punch = np.exp(-t * 110.0) * np.sin(2 * np.pi * 920 * t) * 0.35
    return np.tanh((np.sin(ph) * np.exp(-t * 4.2) + punch) * 1.45) * gain


def chord_unlock(dur=1.45, gain=0.40):
    # Crystalline D-minor9 -> D-major9 luxury settlement unlock shimmer
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    freqs = [293.66, 440.0, 554.37, 659.25, 880.0, 1174.66]
    sig = np.zeros_like(t)
    for i, f in enumerate(freqs):
        t_del = np.maximum(0.0, t - i * 0.018)
        env = np.where(t >= i * 0.018, np.exp(-t_del * (2.6 + i * 0.35)), 0.0)
        sig += np.sin(2 * np.pi * f * t_del) * env / len(freqs)
    return sig * 2.2 * gain


def finale_braam(dur=3.2, gain=0.58):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    att = np.minimum(1.0, t / 0.08)
    dec = np.exp(-np.maximum(0.0, t - 0.08) * 1.15)
    env = att * dec
    # Deep D1 (36.71 Hz) + D2 (73.42 Hz) + A2 (110 Hz) warm analog brass/sub
    w = (
        0.58 * np.sin(2 * np.pi * 36.71 * t)
        + 0.38 * np.tanh(2.1 * np.sin(2 * np.pi * 73.42 * t))
        + 0.22 * np.sin(2 * np.pi * 110.0 * t)
        + 0.12 * np.sin(2 * np.pi * 146.83 * t)
    )
    return w * env * gain


def main():
    os.makedirs("showreel", exist_ok=True)
    os.makedirs("public/showreel", exist_ok=True)
    with open("showreel/beat_sheet.json", "w") as f:
        json.dump(BEAT_SHEET, f, indent=2)

    mix = np.zeros((int(SR * DUR), 2), dtype=np.float64)

    # 1. Warm dark atmospheric drone bed (0s -> 27.6s, then silence sting before finale!)
    bed_len = int(SR * 27.55)
    tb = np.linspace(0, 27.55, bed_len, endpoint=False)
    bed_env = np.minimum(1.0, tb / 0.4) * np.minimum(1.0, (27.55 - tb) / 0.35)
    drone_l = (0.055 * np.sin(2 * np.pi * 73.42 * tb) + 0.032 * np.sin(2 * np.pi * 110.0 * tb + 0.3)) * bed_env
    drone_r = (0.055 * np.sin(2 * np.pi * 73.42 * tb) + 0.032 * np.sin(2 * np.pi * 110.2 * tb - 0.3)) * bed_env
    mix[:bed_len, 0] += drone_l
    mix[:bed_len, 1] += drone_r

    # 2. Opening editorial hook (0.0s -> 2.0s: crisp minimalist ticks before beat drop)
    add_at(mix, card_snap(1.2, 0.38), 0)
    for f_tick in [30, 60, 90]:
        add_at(mix, hat_tick(gain=0.14), f_tick, pan=((f_tick // 30) % 2 - 0.5) * 0.3)
    add_at(mix, whoosh(0.32, 240, 1300, 0.36), 96, pan=0.25)

    # 3. f=120 (2.00s): CURSOR CLICK + OBSIDIAN INVERSION DROP + 120 BPM GROOVE (f=120..1650)
    add_at(mix, cursor_click(0.62), 120)
    add_at(mix, sub_impact(0.9, 0.78), 120)

    # 120 BPM = 30 frames per beat (quarter note), 15 frames per 8th, 7.5 frames per 16th
    for beat_idx, f_beat in enumerate(range(120, 1650, 30)):
        # Silence pocket right before crash-zoom (f=435..449) & before finale (f>=1650)
        if 430 <= f_beat < 450:
            continue
        if beat_idx % 2 == 0:
            add_at(mix, kick_808(gain=0.52), f_beat)
        else:
            add_at(mix, snare_rim(gain=0.28), f_beat)
        # 8th-note hi-hats with stereo motion
        add_at(mix, hat_tick(gain=0.09), f_beat, pan=-0.2)
        if f_beat + 15 < 1650:
            add_at(mix, hat_tick(open_hat=(beat_idx % 4 == 3), gain=0.11), f_beat + 15, pan=0.2)

    # Synced bassline pulses on D1/F1/G1/A1 during active groove
    bass_notes = [36.71, 36.71, 43.65, 41.20]
    for bar_i, f_bar in enumerate(range(120, 1620, 120)):
        bf = bass_notes[bar_i % len(bass_notes)]
        for sub_off in [0, 45, 75]:
            if 425 <= f_bar + sub_off < 455:
                continue
            tb2 = np.linspace(0, 0.34, int(SR * 0.34), endpoint=False)
            bsig = np.tanh(1.8 * np.sin(2 * np.pi * bf * tb2)) * np.exp(-tb2 * 5.5) * 0.22
            add_at(mix, bsig, f_bar + sub_off)

    # 4. Exact Visual Seam & Choreography Foley!
    s = BEAT_SHEET["seams"]
    # Seam to Beat 02 Deck Deal
    add_at(mix, whoosh(0.26, 180, 1200, 0.44), s["to_deck_deal"] - 6, pan=-0.3)
    for k, cf in enumerate(BEAT_SHEET["card_deals"]):
        add_at(mix, card_snap(0.95 + k * 0.08, 0.42), cf, pan=-0.35 + k * 0.14)

    # Target brackets + Crash-zoom punch!
    add_at(mix, cursor_click(0.45), s["target_brackets"])
    add_at(mix, riser(0.25, 220, 980, 0.34), s["target_brackets"])
    add_at(mix, sub_impact(0.85, 0.78), s["crash_zoom_punch"])

    # Seam to Beat 03 Quad-Split Real Films
    add_at(mix, whoosh(0.28, 950, 210, 0.46), s["to_quad_films"] - 6, pan=0.3)
    pans = [-0.45, 0.45, -0.45, 0.45]
    for k, qf in enumerate(BEAT_SHEET["quad_pops"]):
        add_at(mix, card_snap(1.1 + k * 0.1, 0.44), qf, pan=pans[k])
    add_at(mix, sub_impact(0.65, 0.55), s["quad_hero_badge"])

    # Seam to Beat 04 3D Signature Web Flyover
    add_at(mix, whoosh(0.34, 160, 1050, 0.46), s["to_web_3d"] - 8)
    add_at(mix, card_snap(1.25, 0.38), s["web_slide_maya"], pan=-0.2)
    add_at(mix, card_snap(1.35, 0.38), s["web_slide_store"], pan=0.2)
    add_at(mix, cursor_click(0.60), s["web_vault_click"], pan=0.15)

    # Seam to Beat 05 Client Vault & 4-Rail Settlement
    add_at(mix, whoosh(0.26, 300, 1400, 0.40), s["to_vault_unlock"] - 5)
    rail_freqs = [440.0, 554.37, 659.25, 880.0]
    for k, rf in enumerate(BEAT_SHEET["rail_ticks"]):
        tr = np.linspace(0, 0.18, int(SR * 0.18), endpoint=False)
        ping = np.sin(2 * np.pi * rail_freqs[k] * tr) * np.exp(-tr * 18.0) * 0.26
        add_at(mix, ping, rf, pan=0.25)

    # Vault Unlock Click + Crystalline Chord!
    add_at(mix, cursor_click(0.65), s["vault_unlock_click"])
    add_at(mix, chord_unlock(1.5, 0.48), s["vault_unlock_click"] + 2)
    add_at(mix, sub_impact(0.75, 0.52), s["vault_unlock_click"] + 2)

    # Silence sting (f=1655..1680) -> Finale Braam + Ink Signature!
    add_at(mix, riser(0.38, 120, 660, 0.32), s["to_finale_lockup"] - 23)
    add_at(mix, finale_braam(3.3, 0.68), s["to_finale_lockup"])

    # Clean fade-out last 0.35s so zero tail click
    tail = int(SR * 0.35)
    mix[-tail:] *= np.linspace(1.0, 0.0, tail)[:, None]

    # Write float32 WAV and normalize to exact -14.0 LUFS / <= -1.5 dBTP via FFmpeg
    peak = np.max(np.abs(mix))
    mix_norm = (mix / max(peak, 1e-6)) * 0.82
    raw_wav = "/tmp/showreel_raw_60fps.wav"
    out_m4a = "public/showreel/audio_master_60fps.m4a"
    wavfile.write(raw_wav, SR, (mix_norm * 32767).astype(np.int16))

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg, "-y", "-i", raw_wav,
            "-af", "acompressor=threshold=-18dB:ratio=4:attack=3:release=55:makeup=3.5,loudnorm=I=-14.0:TP=-2.6:LRA=7,aresample=48000,alimiter=limit=0.63:level=false",
            "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k",
            out_m4a,
        ],
        check=True,
        capture_output=True,
    )
    eb = subprocess.run(
        [ffmpeg, "-nostats", "-i", out_m4a, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True,
        text=True,
    ).stderr
    m_i = re.findall(r"I:\s*([-\d.]+)\s*LUFS", eb)
    m_tp = re.findall(r"Peak:\s*([-\d.]+)\s*dBFS", eb)
    lufs = float(m_i[-1]) if m_i else None
    tp = float(m_tp[-1]) if m_tp else None
    os.remove(raw_wav)
    print(f"Audio Master Ready: {out_m4a} | Duration={DUR:.3f}s | Integrated={lufs} LUFS | TruePeak={tp} dBTP")


if __name__ == "__main__":
    main()
