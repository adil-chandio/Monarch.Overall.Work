"""Create a temporary local 12-second A/V comparison; never a final soundtrack."""
from pathlib import Path
import hashlib, json, re, subprocess
import imageio_ffmpeg

root=Path(__file__).resolve().parents[5]
base=Path(__file__).resolve().parent
cache=root/'.cache/mammoth-foraging-review'
video=cache/'foraging-motion-review-silent.mp4'
score=base.parent/'soundtrack-draft/Narration-Score-DRAFT.m4a'
wind=base.parent/'ambience-sources/felix-blume-wind-muges.ogg'
out=cache/'foraging-av-comparison.mp4'
for path in (video,score,wind):
    if not path.is_file():raise SystemExit(f'Missing input: {path}')
# Start corresponds approximately to storyboard 02:10; timing is provisional.
# Use one channel of the derivative as a precaution, not a verified MS decode.
# Gentle filtered wind is deliberately low, but only listening can establish whether
# the sound is suitable or resembles the previously rejected mechanical bed.
cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-hide_banner','-loglevel','error',
     '-i',str(video),'-ss','129.81','-i',str(score),'-ss','24','-i',str(wind),
     '-filter_complex',
     '[1:a]atrim=duration=12,asetpts=PTS-STARTPTS[base];'
     '[2:a]atrim=duration=12,asetpts=PTS-STARTPTS,pan=mono|c0=c0,'
     'highpass=f=150,lowpass=f=6000,volume=0.035,'
     'afade=t=in:st=0:d=1.5,afade=t=out:st=10:d=2[wind];'
     '[base][wind]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:level=0[a]',
     '-map','0:v:0','-map','[a]','-t','12','-c:v','copy','-c:a','aac','-b:a','160k',
     '-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True)
checked=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i',str(out),'-filter_complex','ebur128=peak=true','-f','null','-'],check=True,capture_output=True,text=True)
frames=re.findall(r'frame=\s*(\d+)',checked.stderr)
peak=re.findall(r'Peak:\s*(-?[\d.]+) dBFS',checked.stderr)
loud=re.findall(r'I:\s*(-?[\d.]+) LUFS',checked.stderr)
if not frames or int(frames[-1])!=360:raise SystemExit('Expected exactly 360 decoded video frames')
if not peak or float(peak[-1])> -1.0:raise SystemExit('True peak exceeds preview ceiling')
if not loud:raise SystemExit('Loudness measurement unavailable')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'status':'temporary comparison only; requires continuous listening, source and picture review',
          'narration_offset_seconds':129.81,'wind_offset_seconds':24,'decoded_frames':int(frames[-1]),'integrated_lufs':float(loud[-1]),'true_peak_dbtp':float(peak[-1]),
          'inputs':{str(p.relative_to(root)):sha(p) for p in (video,score,wind)},'output_sha256':sha(out)}
(cache/'av-comparison-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
