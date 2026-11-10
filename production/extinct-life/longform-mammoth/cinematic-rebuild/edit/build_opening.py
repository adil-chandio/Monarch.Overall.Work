"""Build a strictly labelled incomplete 85-second editorial assembly.

No placeholders are represented as final shots. Requires previously rendered,
exactly hash-pinned source clips; never downloads or substitutes assets.
"""
import hashlib,json,re,subprocess
from pathlib import Path
import imageio_ffmpeg
base=Path(__file__).resolve().parent
root=base.parents[4]
plan=json.loads((base/'opening-cut.json').read_text())
output=root/'.cache/mammoth-edit/opening-incomplete-workprint.mp4'
output.parent.mkdir(parents=True,exist_ok=True)
ff=imageio_ffmpeg.get_ffmpeg_exe()
def check(path,expected):
 if not path.is_file():raise SystemExit(f'Missing source {path}; rerender exact assets, do not substitute')
 actual=hashlib.sha256(path.read_bytes()).hexdigest()
 if actual!=expected:raise SystemExit(f'Source hash mismatch: {path}')
check(root/plan['audio'],plan['audio_sha256'])
shots=plan['shots'];cursor=0
for s in shots:
 if s['start']!=cursor or s['frames']<1:raise SystemExit('Timeline is not contiguous')
 cursor+=s['frames'];check(root/s['file'],s['sha256'])
 # Fail before editing if a source has been rendered shorter than requested.
 probe=subprocess.run([ff,'-hide_banner','-i',str(root/s['file'])],capture_output=True,text=True)
 match=re.search(r'Duration: (\d+):(\d+):([\d.]+)',probe.stderr)
 if not match:raise SystemExit(f"Could not read source duration: {s['file']}")
 h,m,sec=match.groups();duration=int(h)*3600+int(m)*60+float(sec)
 if duration+0.001 < s['in']+s['frames']/plan['fps']:raise SystemExit(f"Insufficient source frames: {s['file']}")
if cursor!=plan['duration_frames']:raise SystemExit('Duration mismatch')
cmd=[ff,'-y','-hide_banner','-loglevel','error','-filter_complex_threads','2']
for s in shots:cmd+=['-ss',str(s['in']),'-i',str(root/s['file'])]
cmd+=['-i',str(root/plan['audio'])]
filters=[]
for i,s in enumerate(shots):
 filters.append(f'[{i}:v]fps=30,trim=end_frame={s["frames"]},setpts=PTS-STARTPTS,scale=1280:720,setsar=1,format=yuv420p[v{i}]')
filters.append(''.join(f'[v{i}]' for i in range(len(shots)))+f'concat=n={len(shots)}:v=1:a=0[v]')
# Preserve the existing unreviewed soundtrack unchanged, apart from the end fade.
filters.append(f'[{len(shots)}:a]atrim=duration=85,asetpts=PTS-STARTPTS,afade=t=out:st=84:d=1[a]')
cmd+=['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-frames:v',str(plan['duration_frames']),'-c:v','libx264','-preset','fast','-crf','20','-threads','2','-c:a','aac','-b:a','160k','-movflags','+faststart',str(output)]
subprocess.run(cmd,check=True)
r=subprocess.run([ff,'-hide_banner','-i',str(output),'-filter_complex','ebur128=peak=true','-f','null','-'],check=True,capture_output=True,text=True)
frames=re.findall(r'frame=\s*(\d+)',r.stderr);peaks=re.findall(r'Peak:\s*(-?[\d.]+) dBFS',r.stderr);loud=re.findall(r'I:\s*(-?[\d.]+) LUFS',r.stderr)
if not frames or int(frames[-1])!=plan['duration_frames'] or not peaks or float(peaks[-1])>-1 or not loud:raise SystemExit('Output failed mechanical decode or peak check')
report={'status':'incomplete editorial assembly; not a finished film','duration_frames':int(frames[-1]),'fps':30,'lufs':float(loud[-1]),'true_peak_dbtp':float(peaks[-1]),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
(output.parent/'opening-qc.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
