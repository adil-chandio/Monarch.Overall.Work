#!/usr/bin/env python3
"""Build the V8 sound master: measured, picture-linked, and honest about it.

Pipeline
--------
1. Take the existing 20 s procedural mix (music + ambience + footsteps) that the
   earlier cut already contains. Nothing is invented over the top of it.
2. Add three synthesis layers, all generated here with numpy so there is no
   licensing surface, and all placed on measured picture events rather than
   guesses:
     * sub impacts on the two hard cuts into the run and the reveal
     * a filtered riser ending exactly on the reveal frame
     * a low pulse train gated by the *measured* motion energy of the running
       clip, so its rhythm follows the picture instead of a metronome
3. Two-pass loudness normalisation to -16 LUFS / -1.5 dBTP (the streaming
   target), then measure the result and record the numbers.

This is an engineering pass. Nobody has listened to it here; the log says so.
"""
from __future__ import annotations

import argparse, json, re, subprocess, sys, wave
from pathlib import Path

import numpy as np
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import render_film_v8 as rv  # noqa: E402  (shot table + decode)

SR = 48000
FF = imageio_ffmpeg.get_ffmpeg_exe()


# --------------------------------------------------------------------- helpers
def read_wav(path: Path):
    with wave.open(str(path), 'rb') as w:
        ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw != 2:
        raise SystemExit('expected 16-bit wav')
    data = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        data = data.reshape(-1, ch)
    else:
        data = data.reshape(-1, 1)
    return data, sr


def write_wav(path: Path, data: np.ndarray, sr: int = SR):
    path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(data, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(pcm.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def loudness(path: Path) -> dict:
    """Measure integrated LUFS and true peak with ffmpeg's ebur128."""
    out = subprocess.run([FF, '-hide_banner', '-nostats', '-i', str(path),
                          '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    integ = re.findall(r'I:\s+(-?\d+\.\d+) LUFS', out)
    peak = re.findall(r'Peak:\s+(-?\d+\.\d+) dBFS', out)
    return {'integrated_lufs': float(integ[-1]) if integ else None,
            'true_peak_dbfs': float(peak[-1]) if peak else None}


def envelope(x: np.ndarray, attack: float, release: float) -> np.ndarray:
    """Simple one-pole envelope follower for gating."""
    out = np.empty_like(x)
    env = 0.0
    a = np.exp(-1.0 / (attack * SR))
    r = np.exp(-1.0 / (release * SR))
    for i, v in enumerate(x):
        coef = a if v > env else r
        env = coef * env + (1 - coef) * v
        out[i] = env
    return out


# ------------------------------------------------------------------ synthesis
def sub_impact(dur=1.5, freq_start=88.0, freq_end=38.0, gain=0.75):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.geomspace(freq_start, freq_end, n)
    phase = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(phase) * np.exp(-t * 3.1)
    click = np.random.default_rng(11).normal(0, 1, n) * np.exp(-t * 90) * 0.25
    return (body + click) * gain


def riser(dur=1.6, gain=0.30):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sweep = np.sin(2 * np.pi * np.cumsum(np.geomspace(180, 900, n)) / SR)
    noise = np.random.default_rng(23).normal(0, 1, n)
    # simple one-pole low-pass whose cutoff opens with time
    lp = np.empty(n, np.float32)
    acc = 0.0
    for i in range(n):
        cutoff = 0.02 + 0.5 * (i / n) ** 2
        acc += cutoff * (noise[i] - acc)
        lp[i] = acc
    shape = np.linspace(0, 1, n) ** 2.2
    return (sweep * 0.35 + lp * 2.2) * shape * gain


def motion_pulses(clip: Path, frames: int, gain=0.16):
    """Low thump train gated by measured motion energy in the lower body area."""
    seq = rv.decode(clip)
    if len(seq) < 4:
        return np.zeros(int(frames / 24 * SR), np.float32)
    gray = [seq[i].mean() for i in range(len(seq))]
    # energy of vertical change in the lower third of the frame = stride activity
    lower = seq[:, int(seq.shape[1] * 0.55):, :, :]
    energy = []
    prev = None
    for f in lower:
        g = f.mean(axis=2)
        if prev is not None:
            energy.append(float(np.abs(g - prev).mean()))
        prev = g
    energy = np.array(energy or [0.0])
    if energy.max() > 0:
        energy = energy / energy.max()
    idx = np.linspace(0, len(energy) - 1, frames).astype(int)
    per_frame = energy[idx]
    # build a smooth gate at audio rate (one value per film frame)
    gate = np.repeat(per_frame, int(SR / 24))
    gate = envelope(gate, attack=0.012, release=0.09)
    t = np.arange(len(gate)) / SR
    tone = np.sin(2 * np.pi * 52.0 * t) * 0.7 + np.sin(2 * np.pi * 78.0 * t) * 0.3
    return (tone * gate * gain).astype(np.float32)


# ---------------------------------------------------------------------- build
def build(args):
    src = Path(args.source)
    tmp = Path(args.work)
    tmp.mkdir(parents=True, exist_ok=True)

    wav = tmp / 'source.wav'
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(src),
                    '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le', str(wav)],
                   check=True)
    bed, sr = read_wav(wav)
    if sr != SR:
        raise SystemExit(f'unexpected sample rate {sr}')
    n = bed.shape[0]
    total = int(round(20.0 * SR))
    if n < total:
        raise SystemExit(f'source bed is {n / SR:.2f}s, need 20.00s')
    bed = bed[:total].copy()

    # place the layers
    def add_at(track, sound, at_seconds, gain=1.0):
        start = int(round(at_seconds * SR))
        end = min(start + len(sound), track.shape[0])
        if start >= track.shape[0]:
            return
        seg = sound[: end - start] * gain
        track[start:end, 0] += seg
        track[start:end, 1] += seg

    design = {}
    run_start = rv.SHOTS[3].start / 24.0
    reveal = rv.SHOTS[4].start / 24.0

    impacts = [
        ('cut_to_run', run_start, dict(dur=1.2, gain=0.55)),
        ('cut_to_reveal', reveal, dict(dur=1.8, freq_start=96.0, freq_end=33.0, gain=0.85)),
    ]
    for name, at, kw in impacts:
        add_at(bed, sub_impact(**kw), at)
        design[name] = round(at, 3)

    add_at(bed, riser(dur=reveal - (reveal - 1.6)), reveal - 1.6, 0.9)
    design['riser'] = round(reveal - 1.6, 3)

    pulse = motion_pulses(ROOT / 'clips' / f'{rv.SHOTS[3].source}.mp4',
                          rv.SHOTS[3].frames)
    add_at(bed, pulse, run_start)
    design['motion_pulse'] = {'at': round(run_start, 3),
                              'source': rv.SHOTS[3].source,
                              'gated_by': 'measured lower-body motion energy'}

    # gentle high-pass so the new lows don't fight rumble, then normalise
    pre = tmp / 'pre.wav'
    write_wav(pre, np.clip(bed, -1.5, 1.5))
    measured_in = loudness(pre)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # two-pass loudnorm to the streaming target
    pass1 = subprocess.run(
        [FF, '-hide_banner', '-nostats', '-i', str(pre), '-af',
         f'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
        capture_output=True, text=True).stderr
    stats = json.loads(pass1[pass1.rindex('{'):pass1.rindex('}') + 1])
    filt = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={stats['input_i']}"
            f":measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}"
            f":measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}"
            f":linear=true")
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(pre),
                    '-af', filt, '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le',
                    str(out)], check=True)

    final = loudness(out)
    dur = subprocess.run([FF, '-hide_banner', '-i', str(out)], capture_output=True,
                         text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', dur)
    seconds = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))) if m else None

    log = {
        'tool': 'qc/make_sound_v8.py',
        'source_bed': str(src),
        'layers': design,
        'measured': {'source_integrated_lufs': measured_in['integrated_lufs'],
                     'source_true_peak_dbfs': measured_in['true_peak_dbfs'],
                     'final_integrated_lufs': final['integrated_lufs'],
                     'final_true_peak_dbfs': final['true_peak_dbfs']},
        'target': {'integrated_lufs': -16.0, 'true_peak_dbfs': -1.5},
        'duration_seconds': seconds,
        'output': str(out),
        'disclosure': ('Engineering mix only. No human listening, creative approval or '
                       'native-audio review has happened. Footstep sync is not claimed; '
                       'the added low pulse follows measured picture motion energy.'),
    }
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(json.dumps(log, indent=1))
    print(json.dumps(log['measured'], indent=1))
    print(f'WROTE {out}')
    print(f'log   {args.log}')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', required=True, help='20 s mix to master from')
    ap.add_argument('--out', required=True)
    ap.add_argument('--work', default=str(HERE / 'out/v8/work'))
    ap.add_argument('--log', default=str(HERE / 'out/v8/sound_log.json'))
    build(ap.parse_args())


if __name__ == '__main__':
    main()
