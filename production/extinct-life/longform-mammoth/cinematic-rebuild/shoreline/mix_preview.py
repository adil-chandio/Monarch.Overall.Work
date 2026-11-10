"""Temporary four-second shoreline A/V comparison, never a finished sequence."""
from pathlib import Path
import hashlib, json, re, subprocess
import imageio_ffmpeg

root = Path(__file__).resolve().parents[5]
base = Path(__file__).resolve().parent
cache = root / '.cache/mammoth-shoreline-review'
video = cache / 'shoreline-motion-review-silent.mp4'
score = base.parent / 'soundtrack-draft/Narration-Score-DRAFT.m4a'
wave = base.parent / 'ambience-sources/amholma-quiet-beach-pulse.ogg'
render_manifest = cache / 'render-manifest.json'
out = cache / 'shoreline-av-comparison.mp4'
for p in (video, score, wave, render_manifest):
    if not p.is_file():
        raise SystemExit(f'Missing input: {p}')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads(render_manifest.read_text())
if manifest['output_sha256'] != sha(video) or manifest['frames'] < 120:
    raise SystemExit('Render manifest does not match or render is too short')
# Draft storyboard 19–23s: approximate location transition, not locked audio.
# We use only a low-level mono FLORIDA derivative for audition, not Arctic evidence.
cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-loglevel', 'error',
       '-i', str(video), '-ss', '19', '-i', str(score), '-ss', '20', '-i', str(wave),
       '-filter_complex',
       '[1:a]atrim=duration=4,asetpts=PTS-STARTPTS[base];'
       '[2:a]atrim=duration=4,asetpts=PTS-STARTPTS,highpass=f=150,lowpass=f=6500,'
       'volume=0.025,afade=t=in:st=0:d=1,afade=t=out:st=3:d=1[amb];'
       '[base][amb]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:level=0[a]',
       '-map', '0:v:0', '-map', '[a]', '-vf', 'trim=end_frame=120,setpts=PTS-STARTPTS',
       '-t', '4', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', '-threads', '2', '-c:a', 'aac', '-b:a', '160k',
       '-movflags', '+faststart', str(out)]
subprocess.run(cmd, check=True)
checked = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-i', str(out),
                          '-filter_complex', 'ebur128=peak=true', '-f', 'null', '-'],
                         check=True, capture_output=True, text=True)
frames = re.findall(r'frame=\s*(\d+)', checked.stderr)
peak = re.findall(r'Peak:\s*(-?[\d.]+) dBFS', checked.stderr)
loud = re.findall(r'I:\s*(-?[\d.]+) LUFS', checked.stderr)
if not frames or int(frames[-1]) != 120 or not peak or float(peak[-1]) > -1 or not loud:
    raise SystemExit('Decode or loudness check failed')
report = {'status': 'temporary technical comparison; requires continuous listening and creative/science review',
          'voice_offset_seconds': 19, 'wave_offset_seconds': 20, 'decoded_frames': int(frames[-1]),
          'integrated_lufs': float(loud[-1]), 'true_peak_dbtp': float(peak[-1]),
          'inputs': {str(p.relative_to(root)): sha(p) for p in (video, score, wave, render_manifest)},
          'output_sha256': sha(out)}
(cache / 'av-comparison-manifest.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
