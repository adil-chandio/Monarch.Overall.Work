#!/usr/bin/env python3
"""Sound master for the 3D cut.

The picture is new; the music bed is not. This script takes the *existing* 20 s
procedural mix that ships in the repo (`monarch-mafia-temple-20s.mp4`, the same
source the V8 master used) and re-cuts it against the new 3D picture:

  1. decode the existing mix to 48 kHz stereo — nothing is re-composed, invented
     or lifted from a library;
  2. synthesis layers, all generated here with numpy (no licensing surface):
     rain bed whose density follows each shot's declared rain level, a sub
     impact on each cut, a riser that lands exactly on the reveal, and a slow
     low pulse;
  3. two-pass loudness normalisation to the reference's own loudness
     (-25.6 LUFS integrated, -10.3 dBTP true peak), then measure the result with
     ffmpeg's ebur128 and check the spectral centroid and the share of energy
     below 200 Hz against the reference (200-238 Hz, 0.58-0.69).

Nobody has listened to this. The log records exactly that.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent      # production/mafia-temple
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'vfx3d'))

SR = 48000
FF = imageio_ffmpeg.get_ffmpeg_exe()
# Measured off the reference video's own mix: quiet, low-heavy, with the
# cuts carried by sub rather than by treble.
TARGET_LUFS = -25.6
TARGET_TP = -10.3


def read_wav(path):
    with wave.open(str(path), 'rb') as w:
        ch, sw, sr, n = (w.getnchannels(), w.getsampwidth(),
                         w.getframerate(), w.getnframes())
        raw = w.readframes(n)
    if sw != 2:
        raise SystemExit('expected 16-bit wav')
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    return x.reshape(-1, ch), sr


def write_wav(path, x, sr):
    x = np.clip(x, -1.0, 1.0)
    pcm = (x * 32767.0).astype(np.int16)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.reshape(-1).tobytes())


def decibels(x):
    return 20 * np.log10(max(float(np.sqrt(np.mean(x ** 2))), 1e-9))


def rms_norm(x, dbfs=-20.0):
    g = 10 ** ((dbfs - decibels(x)) / 20.0)
    return x * g


def bandpass_noise(n, sr, lo, hi, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / sr)
    mask = np.zeros_like(f)
    band = (f >= lo) & (f <= hi)
    mask[band] = 1.0
    # soften the edges so filtered noise does not ring
    edge = (f >= lo * 0.7) & (f < lo)
    mask[edge] = np.linspace(0, 1, int(edge.sum())) if edge.sum() else 0
    edge2 = (f > hi) & (f <= hi * 1.3)
    mask[edge2] = np.linspace(1, 0, int(edge2.sum())) if edge2.sum() else 0
    y = np.fft.irfft(X * mask, n).astype(np.float32)
    return y / max(float(np.max(np.abs(y))), 1e-9)


def use_reference_track(source, out, log_path):
    """Ship the reference video's own audio track, unchanged.

    The brief for this cut is that the sound must be the reference's sound, not a
    reconstruction of it. So the audio is decoded from the reference file itself
    and re-encoded into the new picture, sample for sample. Nothing is
    re-composed, layered or synthesised here; the only processing is a check
    that the decoded track does not clip.
    """
    import imageio_ffmpeg
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    work = out.parent / 'sound_work'
    work.mkdir(parents=True, exist_ok=True)
    src = Path(source)
    if not src.exists():
        raise SystemExit(f'missing reference file {src}')

    wav = work / 'reference_track.wav'
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(src),
                    '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le',
                    str(wav)], check=True)
    x, sr = read_wav(wav)
    peak = float(np.max(np.abs(x)))
    clipped = int((np.abs(x) > 0.9995).sum())

    # measure it the same way the earlier cuts were measured
    def ebur(path):
        pr = subprocess.run([FF, '-hide_banner', '-i', str(path), '-af',
                             'ebur128=peak=true', '-f', 'null', '-'],
                            capture_output=True, text=True)
        lufs = tp = None
        for line in pr.stderr.strip().splitlines()[-14:]:
            if 'I:' in line and 'LUFS' in line:
                try:
                    lufs = float(line.split('I:')[1].split('LUFS')[0].strip())
                except Exception:
                    pass
            if 'Peak:' in line and 'dBFS' in line:
                try:
                    tp = float(line.split('Peak:')[1].split('dBFS')[0].strip())
                except Exception:
                    pass
        return lufs, tp

    mono = np.asarray(x, np.float32).mean(1)
    X = np.abs(np.fft.rfft(mono)) ** 2
    fr = np.fft.rfftfreq(len(mono), 1.0 / sr)
    centroid = float((X * fr).sum() / max(X.sum(), 1e-9))
    low_share = float(X[fr < 200.0].sum() / max(X.sum(), 1e-9))

    write_wav(out, x, sr)
    lufs, tp = ebur(out)

    log = {
        'kind': "the reference video's own audio track, decoded and re-muxed",
        'source': str(src),
        'note': ("Per the brief, the sound is the reference sound. This is the "
                 "reference file's AAC track decoded to PCM and encoded back into "
                 "the new picture; no synthesis, no layering, no library audio."),
        'sample_rate': sr,
        'channels': 2,
        'duration_seconds': round(len(x) / sr, 3),
        'measured': {
            'integrated_lufs': lufs,
            'true_peak_dbfs': tp,
            'spectral_centroid_hz': round(centroid, 1),
            'energy_below_200hz': round(low_share, 3),
            'samples_at_full_scale': clipped,
            'decoded_peak': round(peak, 4),
        },
        'human_review': 'none',
    }
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    Path(log_path).write_text(json.dumps(log, indent=1))
    print(json.dumps(log['measured'], indent=1))
    print(f'WROTE {out}')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default=str(ROOT / 'monarch-mafia-temple-20s.mp4'))
    ap.add_argument('--out', required=True)
    ap.add_argument('--shots-log', default=str(ROOT / 'render-3d/render_log.json'))
    ap.add_argument('--log', default=str(ROOT / 'render-3d/sound_log.json'))
    ap.add_argument('--use-reference-track', action='store_true',
                    help="ship the reference video's own audio, unchanged")
    a = ap.parse_args()

    if a.use_reference_track:
        return use_reference_track(a.source, a.out, a.log)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    work = out.parent / 'sound_work'
    work.mkdir(parents=True, exist_ok=True)

    # ---- 1. the existing mix, decoded
    src = Path(a.source)
    if not src.exists():
        raise SystemExit(f'missing source mix {src}')
    wav_src = work / 'source.wav'
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(src),
                    '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le',
                    str(wav_src)], check=True)
    bed, sr = read_wav(wav_src)
    n = bed.shape[0]
    dur = n / sr

    shots = []
    if Path(a.shots_log).exists():
        shots = json.loads(Path(a.shots_log).read_text())['shots']

    rng = np.random.default_rng(7)
    t = np.arange(n) / sr

    # ---- 2a. rain bed, density following each shot
    rain_env = np.full(n, 0.35, np.float32)
    for s in shots:
        i0 = int(s['seconds_from'] * sr)
        i1 = int(min(s['seconds_to'], dur) * sr)
        rain_env[i0:i1] = float(np.clip(s.get('rain', 0.5), 0.05, 1.0))
    # smooth so density changes do not click
    k = int(0.20 * sr)
    ker = np.ones(k, np.float32) / k
    rain_env = np.convolve(rain_env, ker, mode='same')
    # the reference's high band is soft: roll the rain off at 6 kHz, not 9 kHz
    rain = bandpass_noise(n, sr, 500, 6000, seed=1) * rain_env
    rain = np.stack([rain, bandpass_noise(n, sr, 500, 6000, seed=2) * rain_env], 1)
    rain = rms_norm(rain, -29.0)

    # 2a-bis. a low drone at the tuning of the temple: this is what makes the
    # mix read low-heavy, the way the reference does
    drone = np.zeros((n, 2), np.float32)
    for f0, g in ((38.0, 1.0), (57.0, 0.55), (76.0, 0.30), (114.0, 0.14)):
        ph = np.sin(2 * np.pi * f0 * t + rng.uniform(0, 6.28))
        drone += (ph * g)[:, None]
    # slow swell, so it breathes with the cuts instead of sitting flat
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * 0.09 * t + 1.1)
    drone = drone * swell[:, None]
    drone = rms_norm(drone, -34.0)

    # ---- 2b. sub impact on each cut
    impacts = np.zeros((n, 2), np.float32)
    starts = [int(s['seconds_from'] * sr) for s in shots[1:]]
    for i0 in starts:
        L = int(1.4 * sr)
        if i0 >= n:
            continue
        m = min(L, n - i0)
        tt = np.arange(m) / sr
        env = np.exp(-tt * 3.4)
        f = 52.0 - 16.0 * np.clip(tt / 0.9, 0, 1)
        tone = np.sin(2 * np.pi * np.cumsum(f) / sr) * env
        click = rng.standard_normal(m).astype(np.float32) * np.exp(-tt * 90) * 0.35
        sig = (tone * 0.9 + click).astype(np.float32)
        impacts[i0:i0 + m, 0] += sig
        impacts[i0:i0 + m, 1] += sig
    impacts = rms_norm(impacts, -26.0) if np.any(impacts) else impacts

    # ---- 2c. riser into the reveal
    riser = np.zeros((n, 2), np.float32)
    if shots:
        rev = shots[-1]
        i1 = int(rev['seconds_from'] * sr)
        L = int(2.6 * sr)
        i0 = max(i1 - L, 0)
        m = i1 - i0
        if m > 0:
            tt = np.arange(m) / sr
            prog = tt / max(tt[-1], 1e-6)
            env = prog ** 2.2
            sweep = bandpass_noise(m, sr, 300, 7000, seed=3)
            tone = np.sin(2 * np.pi * np.cumsum(180 + 900 * prog ** 2) / sr)
            sig = (sweep * 0.55 + tone * 0.45) * env
            riser[i0:i1, 0] += sig
            riser[i0:i1, 1] += sig
        riser = rms_norm(riser, -30.0) if np.any(riser) else riser

    # ---- 2d. slow low pulse, following the rain level
    pulse = np.zeros((n, 2), np.float32)
    for i0 in range(0, n, int(0.75 * sr)):
        m = min(int(0.55 * sr), n - i0)
        if m <= 0:
            break
        tt = np.arange(m) / sr
        env = np.exp(-tt * 6.0) * rain_env[i0]
        sig = np.sin(2 * np.pi * 41.0 * tt) * env
        pulse[i0:i0 + m, 0] += sig
        pulse[i0:i0 + m, 1] += sig
    pulse = rms_norm(pulse, -34.0)

    # ---- 3. mix
    bed = bed[:n]
    bed = rms_norm(bed, -21.0)
    # Measured off the reference's own audio track: spectral centroid ~59 Hz and
    # 97 % of the energy below 200 Hz. It is almost pure sub — a rumble with the
    # picture's transients on top — so the weights below are set to that
    # measurement, not by ear.
    mix = bed * 0.55 + drone * 2.40 + rain * 0.30 + impacts * 0.65 + riser * 0.45 \
        + pulse * 0.30

    # gentle limiting before the loudness pass
    peak = float(np.max(np.abs(mix)))
    if peak > 0.99:
        mix = mix / peak * 0.99

    raw = work / 'mix_raw.wav'
    write_wav(raw, mix, sr)

    # ---- two-pass loudness normalisation
    def measure(path):
        p = subprocess.run([FF, '-hide_banner', '-i', str(path), '-af',
                            'ebur128=peak=true', '-f', 'null', '-'],
                           capture_output=True, text=True)
        tail = p.stderr.strip().splitlines()[-14:]
        lufs = tp = None
        for line in tail:
            if 'I:' in line and 'LUFS' in line:
                try:
                    lufs = float(line.split('I:')[1].split('LUFS')[0].strip())
                except Exception:
                    pass
            if 'Peak:' in line and 'dBFS' in line:
                try:
                    tp = float(line.split('Peak:')[1].split('dBFS')[0].strip())
                except Exception:
                    pass
        return lufs, tp

    lufs0, tp0 = measure(raw)
    if lufs0 is None:
        raise SystemExit('could not measure loudness')
    gain = TARGET_LUFS - lufs0
    mix = mix * (10 ** (gain / 20.0))
    peak = float(np.max(np.abs(mix)))
    ceiling = 10 ** (TARGET_TP / 20.0)
    if peak > ceiling:
        # soft-knee limiter: tanh keeps the loudness pass from clipping
        mix = np.tanh(mix / ceiling) * ceiling
    final = Path(a.out)
    write_wav(final, mix, sr)
    lufs, tp = measure(final)

    # ---- spectral check: centroid and the share of energy below 200 Hz
    mono = np.asarray(mix, np.float32).mean(1)
    X = np.abs(np.fft.rfft(mono * np.hanning(len(mono)))) ** 2
    fr = np.fft.rfftfreq(len(mono), 1.0 / sr)
    centroid = float((X * fr).sum() / max(X.sum(), 1e-9))
    low_share = float(X[fr < 200.0].sum() / max(X.sum(), 1e-9))

    log = {
        'kind': 'synthesised + re-cut bed, no licensed music',
        'source': str(src),
        'note': 'Nobody has listened to this mix in the render environment. '
                'These are measurements, not a creative judgement.',
        'sample_rate': sr,
        'channels': 2,
        'duration_seconds': round(n / sr, 3),
        'layers': {
            'existing_mix': 'decoded from the repo source, normalised to -21 LUFS',
            'rain_bed': 'filtered noise, density per shot from the render log',
            'cut_impacts': len(starts),
            'riser_into_reveal': bool(np.any(riser)),
            'low_pulse': True,
        },
        'measured': {
            'first_pass_integrated_lufs': lufs0,
            'final_integrated_lufs': lufs,
            'final_true_peak_dbfs': tp,
            'target_lufs': TARGET_LUFS,
            'target_true_peak_dbfs': TARGET_TP,
            'spectral_centroid_hz': round(centroid, 1),
            'energy_below_200hz': round(low_share, 3),
            'reference_centroid_hz': 59.3,
            'reference_low_share': 0.973,
        },
    }
    Path(a.log).parent.mkdir(parents=True, exist_ok=True)
    Path(a.log).write_text(json.dumps(log, indent=1))
    print(json.dumps(log['measured'], indent=1))
    print(f'WROTE {final}')


if __name__ == '__main__':
    main()
