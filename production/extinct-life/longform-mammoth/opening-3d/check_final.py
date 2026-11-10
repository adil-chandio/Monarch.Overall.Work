"""Delivery QC for the 3D opening: decode, loudness, duration, sampling.

This is automated measurement plus still sampling. It is not a claim of
continuous human-style audiovisual viewing.
"""
import hashlib
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[4]
B = R / 'production/extinct-life/longform-mammoth/opening-3d'
C = R / '.cache/longform-mammoth-opening'
p = R / 'deliverables/Last-Mammoths-Opening-01-3D-1080p.mp4'
ff = imageio_ffmpeg.get_ffmpeg_exe()

r = subprocess.run([ff, '-hide_banner', '-i', str(p), '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json',
                    '-f', 'null', '-'], capture_output=True, text=True, check=True)
(C / 'final-ffmpeg-qc.log').write_text(r.stderr)
a = r.stderr.rfind('{')
loud = json.loads(r.stderr[a:r.stderr.rfind('}') + 1])
assert -18.0 < float(loud['input_i']) < -14.0, loud
assert float(loud['input_tp']) <= -1.0, loud

r = subprocess.run([ff, '-v', 'error', '-i', str(p), '-map', '0:v:0', '-f', 'null', '-'],
                   capture_output=True, text=True, check=True)
assert not r.stderr, r.stderr

reader = imageio_ffmpeg.read_frames(str(p), pix_fmt='rgb24')
meta = next(reader)
count = 0
mins = []
motion = []
prior = None
samples = []
sheet = Image.new('RGB', (6 * 320, 10 * 180), '#04080f')
draw = ImageDraw.Draw(sheet)
for i, b in enumerate(reader):
    count += 1
    if i % 30 == 0:
        x = np.frombuffer(b, dtype=np.uint8).reshape(meta['size'][1], meta['size'][0], 3)
        im = Image.fromarray(x)
        small = np.asarray(im.resize((64, 36)))
        mins.append(float(small.mean()))
        if prior is not None:
            motion.append(float(np.mean(np.abs(small.astype(float) - prior.astype(float)))))
        prior = small
        j = len(samples)
        sheet.paste(im.resize((320, 180)), ((j % 6) * 320, (j // 6) * 180))
        draw.text(((j % 6) * 320 + 6, (j // 6) * 180 + 162), f'{i / 30:.1f}s', fill='white')
        samples.append(i)
        if i in [30, 240, 600, 900, 1200, 1500, 1740]:
            im.save(C / f'final-{i:04}.jpg', quality=94)

assert count == 1800, count
assert meta['size'] == (1920, 1080), meta['size']
assert meta['fps'] == 30, meta['fps']
assert min(mins) > 3.0, min(mins)
sheet.save(C / 'final-contact.jpg', quality=92)

delivery = {
    'file': str(p.relative_to(R)),
    'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
    'bytes': p.stat().st_size,
    'decoded_frames': count,
    'width': meta['size'][0],
    'height': meta['size'][1],
    'fps': meta['fps'],
    'duration_seconds': 60.0,
    'complete_decode_errors': r.stderr,
    'loudness': loud,
    'sampled_every_second_frames': len(samples),
    'minimum_sampled_rgb_mean': round(min(mins), 3),
    'minimum_adjacent_frame_difference': round(min(motion), 4),
    'render': json.loads((C / 'render-0-1800.json').read_text()),
    'review_scope': 'Automated full decode, loudness analysis and one-second still sampling. Not claimed as continuous human-like audiovisual watching or listening.',
    'youtube_published': False,
}
(B / 'DELIVERY-QC.json').write_text(json.dumps(delivery, indent=2) + '\n')
print(json.dumps({k: v for k, v in delivery.items() if k != 'render'}, indent=2))
