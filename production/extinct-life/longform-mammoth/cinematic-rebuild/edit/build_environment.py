"""Assemble 354–384s to one provisional picture/sound sequence, not a film."""
from pathlib import Path
import hashlib,json,re,subprocess
import imageio_ffmpeg
base=Path(__file__).resolve().parent;root=base.parents[4];work=root/'.cache/mammoth-edit';work.mkdir(parents=True,exist_ok=True)
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def render(file,expected_frames):
 p=root/file;m=json.loads((p.parent/'render-manifest.json').read_text())
 if not p.is_file() or digest(p)!=m['output_sha256'] or m['fps']!=30 or m['frames']!=expected_frames:raise SystemExit('Invalid render: '+str(p))
 for name,h in m['input_sha256'].items():
  if not (root/name).is_file() or digest(root/name)!=h:raise SystemExit('Stale render source: '+name)
 return p
stream=render('.cache/mammoth-stream-scene/stream-scene-motion-review-silent.mp4',480)
ice=render('.cache/mammoth-icing-hypothesis/icing-motion-review-silent.mp4',420)
audio=base.parent/'soundtrack-draft/Narration-Score-DRAFT.m4a';brook=base.parent/'ambience-sources/brook-candidate/ambience-stream-clear.mp3';rain=base.parent/'ambience-sources/jmbphilmes-rain-rainbar-60s.mp3'
for p,sha in [(audio,'434f2c344b428982edf8b00607b8361c4c45bec95da6ac5330c87428a45c3760'),(brook,'497209be73f6f05e46e924c6801dbab3921d1c587b531657120af14c546964dc'),(rain,'ed9ee4e9c2af21b4187fac8b88b7fe80d2b21ffb712a912fe5ace49237110093')]:
 if not p.is_file() or digest(p)!=sha:raise SystemExit('Unexpected/missing input: '+str(p))
out=work/'environment-354-384-incomplete-workprint.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe()
filters='[0:v]fps=30,trim=end_frame=480,setpts=PTS-STARTPTS[v0];[1:v]fps=30,trim=end_frame=420,setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[v];'
filters+='[2:a]atrim=duration=30,asetpts=PTS-STARTPTS[base];[3:a]atrim=duration=17,asetpts=PTS-STARTPTS,volume=0.2,afade=t=in:st=0:d=0.8,afade=t=out:st=15.4:d=1.6[brook];'
filters+='[4:a]atrim=duration=14.7,asetpts=PTS-STARTPTS,volume=0.025,afade=t=in:st=0:d=1.6,afade=t=out:st=12.7:d=2,adelay=15300:all=1[rain];[base][brook][rain]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.82:level=0[a]'
cmd=[ff,'-y','-hide_banner','-loglevel','error','-filter_complex_threads','2','-i',str(stream),'-i',str(ice),'-ss','354','-i',str(audio),'-ss','8','-i',str(brook),'-i',str(rain),'-filter_complex',filters,'-map','[v]','-map','[a]','-frames:v','900','-c:v','libx264','-preset','fast','-crf','20','-threads','2','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True)
r=subprocess.run([ff,'-hide_banner','-i',str(out),'-filter_complex','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
frames=re.findall(r'frame=\s*(\d+)',r.stderr);peak=re.findall(r'Peak:\s*(-?[\d.]+) dBFS',r.stderr);lu=re.findall(r'I:\s*(-?[\d.]+) LUFS',r.stderr)
if not frames or int(frames[-1])!=900 or not peak or float(peak[-1])>-1 or not lu:raise SystemExit('Decode/frame/peak failed')
report={'status':'incomplete candidate 30-second sequence; not a final film or mix','start_frame':10620,'frames':900,'fps':30,'lufs':float(lu[-1]),'true_peak_dbtp':float(peak[-1]),'inputs':{str(p.relative_to(root)):digest(p) for p in [stream,ice,audio,brook,rain]},'output_sha256':digest(out)}
(work/'environment-qc.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
