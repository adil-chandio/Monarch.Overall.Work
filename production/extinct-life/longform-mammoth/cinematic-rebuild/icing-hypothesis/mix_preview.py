"""Fourteen-second experimental review only; never a documentary delivery."""
from pathlib import Path
import hashlib, json, re, subprocess
import imageio_ffmpeg
root=Path(__file__).resolve().parents[5]
base=Path(__file__).resolve().parent
cache=root/'.cache/mammoth-icing-hypothesis'
video=cache/'icing-motion-review-silent.mp4'
manifest=cache/'render-manifest.json'
score=base.parent/'soundtrack-draft/Narration-Score-DRAFT.m4a'
rain=base.parent/'ambience-sources/jmbphilmes-rain-rainbar-60s.mp3'
out=cache/'icing-av-comparison.mp4'
for p in (video,manifest,score,rain):
    if not p.is_file():raise SystemExit(f'Missing input: {p}')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads(manifest.read_text())
if r['frames']!=420 or sha(video)!=r['output_sha256']:raise SystemExit('Wrong or stale motion render')
for path,expected in r['input_sha256'].items():
    if not (root/path).is_file() or sha(root/path)!=expected:raise SystemExit(f'Render source changed: {path}')
# Captions suggest 06:10–06:24, not human-aligned. The rain is a Brazil
# source candidate, not a sound recording of Wrangel, and has not been auditioned.
cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-hide_banner','-loglevel','error',
     '-i',str(video),'-ss','370','-i',str(score),'-ss','0','-i',str(rain),
     '-filter_complex','[1:a]atrim=duration=14,asetpts=PTS-STARTPTS[base];'
     '[2:a]atrim=duration=14,asetpts=PTS-STARTPTS,highpass=f=160,lowpass=f=6500,'
     'volume=0.025,afade=t=in:st=0:d=1.2,afade=t=out:st=6.6:d=2[rain];'
     '[base][rain]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:level=0[a]',
     '-map','0:v:0','-map','[a]','-vf','trim=end_frame=420,setpts=PTS-STARTPTS',
     '-t','14','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-threads','2',
     '-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True)
checked=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i',str(out),'-filter_complex','ebur128=peak=true','-f','null','-'],check=True,capture_output=True,text=True)
frames=re.findall(r'frame=\s*(\d+)',checked.stderr);peak=re.findall(r'Peak:\s*(-?[\d.]+) dBFS',checked.stderr);loud=re.findall(r'I:\s*(-?[\d.]+) LUFS',checked.stderr)
if not frames or int(frames[-1])!=420 or not peak or float(peak[-1])> -1 or not loud:raise SystemExit('Decode or peak check failed')
report={'status':'temporary comparison: needs continuous listening and scientific/creative review','voice_offset_seconds':370,'rain_offset_seconds':0,'decoded_frames':int(frames[-1]),'integrated_lufs':float(loud[-1]),'true_peak_dbtp':float(peak[-1]),'inputs':{str(p.relative_to(root)):sha(p) for p in (video,manifest,score,rain)},'output_sha256':sha(out)}
(cache/'av-comparison-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
