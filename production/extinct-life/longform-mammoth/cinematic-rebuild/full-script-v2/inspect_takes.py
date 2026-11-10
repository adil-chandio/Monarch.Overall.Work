"""Measure the speech takes without altering their speed or treating them as a finished film."""
import hashlib, json, subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np

B = Path(__file__).resolve().parent
S = json.loads((B / 'narration.json').read_text())
ff = imageio_ffmpeg.get_ffmpeg_exe()
t = 0.6
results = []
for sec in S['sections']:
    f = B / (sec['id'] + '.mp3')
    raw = subprocess.run([ff, '-v', 'error', '-i', str(f), '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'],
                         check=True, capture_output=True).stdout
    samples = np.frombuffer(raw, dtype='<f4')
    assert len(samples) > 16000 and np.isfinite(samples).all(), f
    dur = len(samples) / 16000
    peak = float(np.max(np.abs(samples)))
    assert 0.01 < peak < 1.2, (f, peak)
    results.append({'id': sec['id'], 'chapter': sec['chapter'], 'start': round(t, 3),
                    'duration': round(dur, 3), 'end': round(t + dur, 3),
                    'peak_sample': round(peak, 4), 'bytes': f.stat().st_size,
                    'sha256': hashlib.sha256(f.read_bytes()).hexdigest()})
    t += dur + 0.8
plan = {'duration_seconds': round(t + 4.2, 3), 'sections': results,
        'notes': 'Measured decoded durations plus chapter gaps; no video, captions, final score or human listening review.'}
(B / 'take-timeline.json').write_text(json.dumps(plan, indent=2) + '\n')
print(json.dumps(plan, indent=2))
