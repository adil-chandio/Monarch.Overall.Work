"""Original instrumental score and restrained editorial sound for the 3D opening.

Everything is procedurally synthesised here: no third-party music, no samples,
no field recordings, no competitor audio. The narration is the platform voice-04
take, placed unsped.
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import imageio_ffmpeg

B = Path(__file__).resolve().parent
C = Path('.cache/longform-mammoth-opening')
C.mkdir(parents=True, exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
sr = 48000
DUR = 60.0
N = int(DUR * sr)
t = np.arange(N) / sr
rng = np.random.default_rng(91517)

# ---------------------------------------------------------------- narration
subprocess.run([ff, '-y', '-v', 'error', '-i', str(B / 'source/narration.mp3'), '-ar', str(sr),
                '-ac', '1', '-c:a', 'pcm_s16le', str(C / 'voice.wav')], check=True)
_, v = wavfile.read(C / 'voice.wav')
v = v.astype(float) / 32768.0
voice = np.zeros(N)
VOICE_AT = 0.55
start = int(VOICE_AT * sr)
voice[start:start + len(v)] = v
voice = sosfilt(butter(2, 70, fs=sr, btype='highpass', output='sos'), voice)


def add(dst, y, at, gain=1.0, pan=0.0):
    """Stereo-free additive insert with a soft fade so nothing clicks."""
    i = int(at * sr)
    if i >= len(dst):
        return
    n = min(len(y), len(dst) - i)
    seg = y[:n].copy()
    f = min(int(0.02 * sr), n // 2)
    if f > 0:
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
    dst[i:i + n] += seg * gain


def noise_band(lo, hi, seconds, seed_shift=0):
    n = int(seconds * sr)
    y = rng.normal(size=n) + rng.normal(size=n) * 0.6
    y = sosfilt(butter(2, [lo, hi], fs=sr, btype='bandpass', output='sos'), y)
    return y


# ---------------------------------------------------------------- score
music = np.zeros(N)
EVENTS = []

# Cold sub drone: D1 + A1 with a slow breathing swell.
for freq, gain, phase in [(36.708, 0.30, 0.0), (55.0, 0.20, 1.1), (73.416, 0.10, 2.3)]:
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * t / 26.0 + phase)
    add(music, np.sin(2 * np.pi * freq * t + phase) * swell, 0.0, gain)

# High shimmer pad that arrives with the "strange part" beat and keeps building.
shimmer_in = 18.95
shimmer_i = int(shimmer_in * sr)
sh = noise_band(3200, 7800, DUR - shimmer_in)
sh_t = t[shimmer_i:shimmer_i + len(sh)]
env = np.clip((sh_t - shimmer_in) / 6.0, 0, 1) * np.clip((DUR - sh_t) / 9.0, 0, 1)
mod = 0.65 + 0.35 * np.sin(2 * np.pi * 0.23 * sh_t + 1.3)
add(music, sh * env * mod, shimmer_in, 0.020)

# Pulse: 60 BPM soft sub hits, sparse at first, denser once the case board appears.
beat = 60.0 / 60.0
for j, at in enumerate(np.arange(0.4, DUR - 0.4, beat)):
    strength = 0.35 if at < 18.95 else (0.6 if at < 31.1 else (0.85 if at < 44.0 else 0.5))
    if j % 2 == 1 and at < 31.1:
        strength *= 0.5
    dur = 0.5
    n = int(dur * sr)
    tt = np.arange(n) / sr
    y = np.sin(2 * np.pi * (54 * tt - 60 * tt ** 2)) * np.exp(-tt * 12) * np.minimum(1, tt / 0.006)
    add(music, y, at, 0.055 * strength)
    EVENTS.append({'at': round(float(at), 3), 'type': 'soft low pulse'})

# Sparse bell motif (witness cards beat), in D minor.
bell_times = [27.4, 29.9, 32.4, 34.1, 36.6, 39.1, 40.8, 42.3]
for k, at in enumerate(bell_times):
    freq = [146.83, 174.61, 220.0, 130.81][k % 4] * 2
    dur = 2.2
    n = int(dur * sr)
    tt = np.arange(n) / sr
    y = (np.sin(2 * np.pi * freq * tt) + 0.42 * np.sin(2 * np.pi * freq * 2.01 * tt)
         + 0.18 * np.sin(2 * np.pi * freq * 3.0 * tt)) * np.exp(-tt * 3.4) * np.minimum(1, tt / 0.004)
    add(music, y, at, 0.030 if at < 43 else 0.018)

# Slow string-like swell under the empty slot (the missing final witness).
swell_n = int(6.6 * sr)
st = np.arange(swell_n) / sr
swell_env = np.sin(np.pi * np.clip(st / 6.6, 0, 1)) ** 1.6
saw = sum(np.sin(2 * np.pi * f * st + i) for i, f in enumerate([110.0, 164.81, 220.0, 329.63])) / 4
saw = sosfilt(butter(2, [120, 2400], fs=sr, btype='bandpass', output='sos'), saw)
add(music, saw * swell_env, 34.0, 0.034)

# Final resolve: a warm F-major colour over D minor at the closing title.
res_n = int(8.6 * sr)
rt = np.arange(res_n) / sr
res_env = np.minimum(1, rt / 1.1) * np.clip((8.6 - rt) / 4.0, 0, 1)
for f in [146.83, 220.0, 261.63, 329.63]:
    add(music, np.sin(2 * np.pi * f * rt) * res_env, 51.4, 0.026)

# ---------------------------------------------------------------- sfx
fx = np.zeros(N)
FX = []

# Arctic wind bed, filtered noise with slow amplitude movement.
wind = noise_band(180, 1100, DUR)
wind_env = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 7.3 + 0.6)) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 3.1))
add(fx, wind * wind_env, 0.0, 0.030)
FX.append({'at': 0.0, 'type': 'low arctic wind bed (filtered noise, no recording)'})


def low_drop(at, length=1.6, f0=120.0, f1=38.0, gain=0.16):
    n = int(length * sr)
    tt = np.arange(n) / sr
    f = f1 + (f0 - f1) * np.exp(-tt * 4.0)
    phase = 2 * np.pi * np.cumsum(f) / sr
    y = np.sin(phase) * np.exp(-tt * 2.4) * np.minimum(1, tt / 0.01)
    add(fx, y, at, gain)
    FX.append({'at': round(at, 3), 'type': 'descending low impact'})


def glass_shimmer(at, length=1.9, gain=0.05):
    n = int(length * sr)
    tt = np.arange(n) / sr
    y = np.zeros(n)
    for f in [1174.7, 1567.98, 2093.0, 2637.0]:
        y += np.sin(2 * np.pi * f * tt + f * 0.001) * np.exp(-tt * (2.0 + f / 2600))
    add(fx, y / 4, at, gain)
    FX.append({'at': round(at, 3), 'type': 'glass shimmer (synthetic, short decay)'})


def card_thunk(at, gain=0.10):
    n = int(0.26 * sr)
    tt = np.arange(n) / sr
    y = np.sin(2 * np.pi * (128 * tt - 190 * tt ** 2)) * np.exp(-tt * 22) * np.minimum(1, tt / 0.003)
    add(fx, y, at, gain)
    FX.append({'at': round(at, 3), 'type': 'soft card placement thunk'})


low_drop(18.90)
card_thunk(31.05, 0.09)
glass_shimmer(35.85, 0.045)
glass_shimmer(40.65, 0.040)
low_drop(50.55, 1.9, 96.0, 30.0, 0.13)

# ---------------------------------------------------------------- ducking and mix
step = 240
frames = voice[:N // step * step].reshape(-1, step)
small = np.sqrt(np.mean(frames ** 2, axis=1))
active = (small > 0.014).astype(float)
future = np.maximum.reduce([np.roll(active, -j) for j in range(10)])
env = np.zeros(len(future))
level = 0.0
for i, x in enumerate(future):
    level += (x - level) * (0.6 if x > level else 0.04)
    env[i] = level
duck = 1 - 0.78 * np.interp(t, np.arange(len(env)) * 0.005, env)
fade = np.minimum(1, t / 0.9) * np.minimum(1, np.maximum(0, (DUR - t) / 2.2))
music *= duck * fade
fx *= np.sqrt(duck) * fade

mix = (voice * 0.95 + music + fx)[:, None]
wavfile.write(C / 'music.wav', sr, (np.clip(music, -0.99, 0.99) * 32767).astype(np.int16))
wavfile.write(C / 'sfx.wav', sr, (np.clip(fx, -0.99, 0.99) * 32767).astype(np.int16))
wavfile.write(C / 'premix.wav', sr, (np.clip(mix, -0.99, 0.99) * 32767).astype(np.int16))
subprocess.run([ff, '-y', '-v', 'error', '-i', str(C / 'premix.wav'),
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=6', '-ar', str(sr), '-c:a', 'pcm_s16le',
                str(C / 'mix.wav')], check=True)

qc = {
    'original_composition': True,
    'third_party_music_samples': False,
    'field_recordings_used': False,
    'competitor_audio_used': False,
    'narration_voice_id': 'voice-04',
    'speech_rate_change': False,
    'narration_start_seconds': VOICE_AT,
    'narration_source_seconds': round(len(v) / sr, 3),
    'duration_seconds': DUR,
    'master_target_lufs': -16,
    'master_target_true_peak': -1.5,
    'ducking': 'Approx 50ms lookahead, fast attenuation, smooth release; maximum music gain reduction 78 percent',
    'score': 'Original procedural synthesis: D-minor sub drone, filtered shimmer pad, 60 BPM low pulse, sparse bell motif, slow string swell, F-major-colour resolve.',
    'sfx_events': FX,
    'sfx_count': len(FX),
    'music_pulse_events': len(EVENTS),
    'full_listening_certified': False,
}
(B / 'SOUND-DESIGN.json').write_text(json.dumps(qc, indent=2) + '\n')
print('mix.wav written:', (C / 'mix.wav').stat().st_size, 'bytes; sfx events:', len(FX))
