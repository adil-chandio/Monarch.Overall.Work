#!/usr/bin/env python3
"""Score for the reference-matched cut.

The target was measured off the reference's audio, not guessed:

    integrated loudness  -25.6 LUFS
    loudness range         1.3 LU
    true peak             -10.3 dBFS
    spectral centroid      200-238 Hz
    58-69% of energy below 200 Hz

So: no melody, no percussion kit, no rise-and-fall. A low drone with slow
beating, a filtered noise bed, a handful of sub impacts on the cuts, and two
temple bowls. Everything below 200 Hz carries the body; the top end is only
there to stop it sounding like a test tone.

Usage:
  python qc/vfx3d/sound.py --out render-3d/sound.wav [--log render-3d/sound_log.json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(20261111)


def env(n, attack, decay, curve=2.0):
    """Fast attack, exponential decay, in samples."""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    d = np.exp(-t / max(decay, 1e-4))
    return (a ** curve) * d


def add(buf, sig, at):
    i = int(at * SR)
    j = min(i + len(sig), buf.shape[0])
    if i >= buf.shape[0]:
        return
    buf[i:j] += sig[:j - i]


def lowpass(x, k=24):
    """One-pole cascade: cheap, steep enough for a sub-only bed."""
    y = x
    for _ in range(k):
        y = np.concatenate([[y[0]], y[1:] * 0.35 + y[:-1] * 0.65])
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='render-3d/sound.wav')
    ap.add_argument('--log', default='render-3d/sound_log.json')
    ap.add_argument('--lufs', type=float, default=-25.6)
    args = ap.parse_args()

    t = np.arange(N) / SR
    L = np.zeros(N, np.float64)
    R = np.zeros(N, np.float64)

    # ---------------------------------------------------------------- the bed
    # Two detuned sub sines, 38 Hz and 40.5 Hz: the beat between them is the
    # slow pulse the reference has, without ever being a rhythm.
    for f, amp, ph in ((38.0, 0.34, 0.0), (40.5, 0.26, 1.1),
                       (57.0, 0.20, 2.0), (76.5, 0.16, 0.4),
                       (114.0, 0.13, 3.1)):
        s = np.sin(2 * np.pi * f * t + ph)
        # slow amplitude drift, so no two seconds are identical
        drift = 0.78 + 0.22 * np.sin(2 * np.pi * (0.043 + f * 1e-4) * t + ph)
        L += s * amp * drift
        R += s * amp * np.roll(drift, 401)      # a few ms of width, no phasing

    # ------------------------------------------------------- filtered noise
    # Wind through cedar: white noise pushed down to a low rumble, with a slow
    # moving cutoff so the texture breathes.
    noise = rng.standard_normal(N)
    bed = lowpass(noise, k=9)
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * 0.031 * t + 0.7)
    bed = bed * swell * 0.75
    L += bed
    R += np.roll(bed, 977) * 0.98

    # A quiet mid band: the reference keeps ~35% of its energy above 200 Hz, so
    # the score needs air as well as sub. High-passed noise, heavily attenuated.
    air = rng.standard_normal(N)
    for _ in range(6):                       # crude high-pass
        air = air - np.concatenate([[0.0], lowpass(air, k=1)[:-1]])
    air = lowpass(air, k=2)                  # tame the top two octaves
    air = air * (0.55 + 0.45 * np.sin(2 * np.pi * 0.017 * t + 2.2))
    L += air * 0.045
    R += np.roll(air, 613) * 0.043

    # ------------------------------------------------------ impacts on cuts
    # Events are collected separately from the bed: the bed is levelled to a
    # fixed RMS, the events are summed on top, and that is what keeps the
    # dynamic range the reference has.
    ev_buf = np.zeros((N, 2), np.float64)
    # Frames 96, 216, 312, 384, 432 -> 4.0, 9.0, 13.0, 16.0, 18.0 s
    for at, gain in ((4.0, 0.55), (9.0, 0.42), (13.0, 0.62),
                     (16.0, 0.40), (18.0, 0.34)):
        n = int(SR * 1.8)
        tt = np.arange(n) / SR
        # pitch drops from 96 Hz to 44 Hz: a hall drum, not a kick sample
        f = 96.0 * np.exp(-tt * 1.9) + 42.0
        sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.0015, 0.42)
        # a little air on the hit so it has a transient
        hit = lowpass(rng.standard_normal(n), k=3) * env(n, 0.002, 0.09) * 0.55
        add(ev_buf[:, 0], (sig + hit) * gain, at)
        add(ev_buf[:, 1], (sig + hit) * gain * 0.96, at + 0.004)

    # ------------------------------------------------------- temple bowls
    # Inharmonic partials, long decay: the only mid-range events in the score.
    for at, f0, gain in ((9.0, 186.0, 0.85), (16.0, 236.0, 0.66)):
        n = int(SR * 7.0)
        tt = np.arange(n) / SR
        sig = np.zeros(n)
        for k, a in ((1.0, 1.0), (2.76, 0.42), (5.40, 0.20), (8.93, 0.09)):
            sig += a * np.sin(2 * np.pi * f0 * k * tt + k) * \
                np.exp(-tt / (2.4 / k))
        sig *= env(n, 0.010, 3.2)
        add(ev_buf[:, 0], sig * gain, at)
        add(ev_buf[:, 1], sig * gain * 0.92, at + 0.006)

    # ---------------------------------------------------------- first/last
    # The reference ramps in over the first second and fades over the last.
    fade_in = np.clip(t / 0.9, 0, 1) ** 1.4
    fade_out = np.clip((DUR - t) / 1.1, 0, 1) ** 1.6
    L *= fade_in * fade_out
    R *= fade_in * fade_out
    ev_buf *= (fade_in * fade_out)[:, None]

    # Master. No global saturation: the reference has a 15 dB crest factor
    # (-25.6 LUFS against a -10.3 dBTP peak), which only exists if the impacts
    # are allowed to be peaky and the bed stays low. So the bed is levelled
    # first, then the events are summed on top, then loudness is corrected.
    bed = st = np.stack([L, R], 1)
    bed_rms = np.sqrt((st ** 2).mean())
    st = st / max(bed_rms, 1e-9) * 0.038          # bed sits low in the mix
    ev = ev_buf.copy()
    # events are levelled by their own PEAK, not their RMS: an RMS-normalised
    # impact has to be huge to be an impact, and that is what flattened the
    # dynamic range in the first master
    st = st + ev / max(np.abs(ev).max(), 1e-9) * 0.30   # events carry the peaks

    # Peak limiter with a real envelope (5 ms attack, 90 ms release) rather
    # than a global tanh: it shaves the isolated transients and leaves the bed
    # and the dynamic range alone.
    st = limit(st, thresh=10 ** (-10.8 / 20.0), sr=SR)

    tmp = Path(args.out).with_suffix('.tmp.wav')
    tmp.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(4):
        write_wav(tmp, st)
        lufs, tp = measure(tmp)
        err = args.lufs - lufs
        if abs(err) < 0.2:
            break
        st = limit(st * 10 ** (err / 20.0), thresh=10 ** (-10.8 / 20.0), sr=SR)
    tmp.unlink(missing_ok=True)
    write_wav(Path(args.out), st)
    lufs2, tp2 = measure(Path(args.out))

    log = dict(target_lufs=args.lufs, lufs=round(lufs2, 2),
               true_peak_db=round(tp2, 2),
               sr=SR, seconds=DUR,
               notes='synthesised score: sub drone, filtered noise bed, cut '
                     'impacts, two temple bowls; no melody, no percussion kit')
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(json.dumps(log, indent=1))
    print(json.dumps(log, indent=1))


def limit(x, thresh, sr=SR, look=0.004, release=0.090):
    """Peak limiter with look-ahead.

    The first version had no look-ahead and simply missed every transient: the
    envelope could not rise fast enough, so the peaks went through and the
    measured true peak was 3 dB above the limiter's threshold. This one takes
    the maximum of the *next* 4 ms, so the gain is already down when the peak
    arrives, then releases over 90 ms.
    """
    peak = np.abs(x).max(1)
    w = max(int(look * sr), 2)
    padded = np.pad(peak, (0, w), mode='edge')
    ahead = np.lib.stride_tricks.sliding_window_view(padded, w).max(1)[:len(peak)]
    r = 1.0 - np.exp(-1.0 / (release * sr))
    env = np.empty_like(ahead)
    e = 0.0
    for i in range(len(ahead)):
        e = ahead[i] if ahead[i] > e else e + (ahead[i] - e) * r
        env[i] = e
    gain = np.minimum(1.0, thresh / np.maximum(env, 1e-9))
    return x * gain[:, None]


def write_wav(path, stereo):
    pcm = np.clip(stereo, -1, 1)
    pcm = (pcm * 32767.0).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def measure(path):
    """Integrated LUFS and true peak, straight from ffmpeg's ebur128."""
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([ff, '-hide_banner', '-nostats', '-i', str(path),
                        '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    txt = r.stderr
    lufs = tp = None
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith('I:'):
            lufs = float(line.split()[1])
        if line.startswith('Peak:'):
            # the LAST Peak line is the true peak of the whole file; earlier
            # ones are per-window and reading the first was under-reading it
            try:
                tp = float(line.split()[1])
            except (ValueError, IndexError):
                pass
    if lufs is None:
        raise SystemExit('could not measure loudness:\n' + txt[-1500:])
    return lufs, (tp if tp is not None else 0.0)


if __name__ == '__main__':
    main()
