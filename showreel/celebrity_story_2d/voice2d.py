"""Drive the mouth chart from the narration itself.

The mouth is not animated by eye. Each narration take is analysed into a
per-frame energy track at film frame rate, and that track picks the viseme:
silence closes the mouth, loud syllables open it wide, and the transitions are
smoothed so the shapes read as speech instead of as a blinking hole.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parent
V6 = P.parent / 'celebrity_story_3d_v6'
FPS = 24
SR = 16000

# energy buckets -> viseme. Ordered by openness; weighted toward the shapes a
# front-on speaker actually makes, with "ah/eh" dominating.
_LADDER = [
    (0.00, 'M'),
    (0.10, 'MBP'),
    (0.20, 'I'),
    (0.32, 'E'),
    (0.46, 'L'),
    (0.62, 'A'),
    (0.80, 'O'),
]


def _read_wav_mono(path):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([ff, '-v', 'error', '-i', str(path), '-f', 's16le',
                        '-ac', '1', '-ar', str(SR), '-'], capture_output=True)
    if r.returncode != 0:
        return np.zeros(0, np.float32)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def _envelope(sig, hop):
    """RMS per hop, lightly compressed, normalised to 0..1."""
    if len(sig) == 0:
        return np.zeros(0, np.float32)
    n = len(sig) // hop
    if n == 0:
        return np.zeros(0, np.float32)
    frames = sig[:n * hop].reshape(n, hop)
    e = np.sqrt((frames ** 2).mean(axis=1))
    # compress: speech is very peaky, and raw RMS under-drives the mouth
    e = np.log1p(e * 26.0)
    hi = float(np.percentile(e, 96)) or 1.0
    return np.clip(e / hi, 0, 1)


def build_track(cues, total_frames, fps=FPS):
    """Return (openness[], viseme[]) at film frame rate for the whole film."""
    n = total_frames
    open_ = np.zeros(n, np.float32)
    track = ['M'] * n
    hop = SR // fps
    for i, cue in enumerate(cues, start=1):
        path = V6 / 'trimmed' / f'{i:02d}.wav'
        if not path.exists():
            continue
        sig = _read_wav_mono(path)
        env = _envelope(sig, hop)
        f0 = int(round(cue['start'] * fps))
        for k, e in enumerate(env):
            f = f0 + k
            if 0 <= f < n:
                open_[f] = max(open_[f], float(e))
    # smooth so shapes change on the syllable, not on the sample
    if n:
        k = np.array([0.12, 0.22, 0.32, 0.22, 0.12], np.float32)
        pad = np.pad(open_, 2, mode='edge')
        open_ = np.convolve(pad, k, mode='valid')[:n]
    for f, e in enumerate(open_):
        v = 'M'
        for thr, name in _LADDER:
            if e >= thr:
                v = name
        track[f] = v
    return open_.tolist(), track


def script():
    with open(P / 'script.json') as fh:
        return json.load(fh)


if __name__ == '__main__':
    cues = script()
    op, tr = build_track(cues, 1440)
    import collections
    print('cue starts:', [round(c['start'], 2) for c in cues])
    print('openness max', round(max(op), 3), 'mean', round(sum(op) / len(op), 3))
    print('visemes', collections.Counter(tr).most_common())
    head = ''.join(t[0] for t in tr[:120])
    print('first 5s:', head)
