"""Mux the rendered 3D frames with the mixed soundtrack into the delivery file."""
import json
import hashlib
import subprocess
from pathlib import Path

import imageio_ffmpeg

B = Path(__file__).resolve().parent
R = Path(__file__).resolve().parents[4]
C = R / '.cache/longform-mammoth-opening'
D = R / 'deliverables'
D.mkdir(exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()

video = C / 'part-0-1800.mp4'
if not video.exists():
    raise SystemExit('Rendered video part is missing: ' + str(video))
# Refuse incomplete, stale or substituted renders. An aborted MP4 may still exist
# at the target path; a successful run writes its matching manifest only at exit.
manifest_path = C / 'render-0-1800.json'
if not manifest_path.exists():
    raise SystemExit('Full-render manifest is missing; refusing to mux an unverified part.')
manifest = json.loads(manifest_path.read_text())
expected = hashlib.sha256((B / 'scene.mjs').read_bytes() + (B / 'timeline.json').read_bytes()).hexdigest()
if (manifest.get('from'), manifest.get('to'), manifest.get('frames')) != (0, 1800, 1800):
    raise SystemExit('Render manifest does not describe the full 1800-frame opening.')
if manifest.get('source_sha256') != expected or manifest.get('page_errors'):
    raise SystemExit('Render is stale or reported page errors; rerender before finishing.')
if manifest.get('video_sha256') != hashlib.sha256(video.read_bytes()).hexdigest():
    raise SystemExit('Rendered video does not match its manifest.')

audio = C / 'mix.wav'
if not audio.exists():
    raise SystemExit('Mixed soundtrack is missing: ' + str(audio))

out = D / 'Last-Mammoths-Opening-01-3D-1080p.mp4'
subprocess.run([
    ff, '-y', '-v', 'error',
    '-i', str(video), '-i', str(audio),
    '-map', '0:v:0', '-map', '1:a:0',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
    '-movflags', '+faststart', '-shortest',
    str(out)
], check=True)

# burned-in subtitles already exist in the picture; ship a sidecar SRT as well.
timeline = json.loads((B / 'timeline.json').read_text())


def stamp(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


lines = []
for i, c in enumerate(timeline['captions'], 1):
    lines.append(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}\n")
(B / 'English.srt').write_text('\n'.join(lines))

print(json.dumps({
    'deliverable': str(out.relative_to(R)),
    'bytes': out.stat().st_size,
    'captions_srt': str((B / 'English.srt').relative_to(R)),
}, indent=2))
