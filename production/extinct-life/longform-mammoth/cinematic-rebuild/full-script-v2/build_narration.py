"""Build a continuous *draft narration*, not a soundtrack or documentary master.

Inputs are original-speed takes. Gaps follow take-timeline.json; there is no
musical score or SFX. This does not replace listening or caption review.
"""
import hashlib, json, re, subprocess
from pathlib import Path
import imageio_ffmpeg

B = Path(__file__).resolve().parent
R = B.parents[4]
F = imageio_ffmpeg.get_ffmpeg_exe()
T = json.loads((B / 'take-timeline.json').read_text())
items = T['sections']
files = [B / (x['id'] + '.mp3') for x in items]
for item, file in zip(items, files):
    assert hashlib.sha256(file.read_bytes()).hexdigest() == item['sha256'], f'Changed take: {file}'

# Use silence segments rather than retiming any voice. Initial 0.6s, intertake
# gaps of 0.8s, and final 5.0s reproduce inspect_takes.py's measured timeline.
parts = []
labels = []
def silence(label, duration):
    parts.append(f'anullsrc=r=48000:cl=mono,atrim=duration={duration:.6f},asetpts=PTS-STARTPTS[{label}]')
    labels.append(f'[{label}]')
silence('pre', items[0]['start'])
for i, item in enumerate(items):
    parts.append(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=mono,asetpts=PTS-STARTPTS[voice{i}]')
    labels.append(f'[voice{i}]')
    if i < len(items)-1:
        gap = round(items[i+1]['start'] - item['end'], 3)
        assert abs(gap - .8) < .002
        silence(f'gap{i}', gap)
    else:
        silence('post', round(T['duration_seconds'] - item['end'], 3))
parts.append(''.join(labels) + f'concat=n={len(labels)}:v=0:a=1,loudnorm=I=-16:TP=-2.5:LRA=7,volume=-0.5dB[out]')
out = B / 'Narration-Draft-v2.m4a'
cmd = [F, '-y', '-v', 'warning']
for file in files: cmd += ['-i', str(file)]
cmd += ['-filter_complex', ';'.join(parts), '-map', '[out]', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(out)]
subprocess.run(cmd, check=True)
# Decode the entire file and measure integrated loudness/true peak. The process
# returning successfully is not a subjective quality assessment.
p = subprocess.run([F, '-hide_banner', '-i', str(out), '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True, check=True)
raw = p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}') + 1]
levels = json.loads(raw)
assert float(levels['input_tp']) < -1, levels
match = re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)', p.stderr)
assert match, 'missing measured output duration'
duration = int(match[1])*3600 + int(match[2])*60 + float(match[3])
assert abs(duration - T['duration_seconds']) < .12, (duration, T['duration_seconds'])
qc = {'file': out.name, 'bytes': out.stat().st_size, 'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
      'expected_duration_seconds': T['duration_seconds'], 'reported_duration_seconds': duration,
      'integrated_loudness_lufs': float(levels['input_i']), 'true_peak_dbtp': float(levels['input_tp']),
      'full_decode_errors': False, 'speed_change': False, 'music_or_sfx': False,
      'subjective_review': 'Not continuously listened to; TTS wording, pacing and pronunciation need human review.',
      'scope': 'Draft adaptation narration only; not a finished soundtrack or film.'}
(B/'NARRATION-QC.json').write_text(json.dumps(qc, indent=2)+'\n')
print(json.dumps(qc, indent=2))
