"""Integrate available sequences at provisional narrative offsets.

These are separate editorial inserts, not a complete film, not picture lock,
and not a substitute for the missing footage or continuous sound review.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
import imageio_ffmpeg
base=Path(__file__).resolve().parent;root=base.parents[4]
audio=root/'production/extinct-life/longform-mammoth/cinematic-rebuild/soundtrack-draft/Narration-Score-DRAFT.m4a'
choices={
 'genome-comparison':('.cache/mammoth-comparison-lab/comparison-lab-motion-review-silent.mp4',None,5182/30,600),
 'hypothesis':('.cache/mammoth-icing-hypothesis/icing-motion-review-silent.mp4','e2ed9b28d179b12d7e7d54d5be3bcbb782d61c6638df3f3c7f64cb75229f6040',370.,420),
 'genomic-gap':('.cache/mammoth-genome-gap/genome-gap-motion-review-silent.mp4',None,629.0666666667,510),
}
if len(sys.argv)!=2 or sys.argv[1] not in choices:raise SystemExit('usage: build_insert.py genome-comparison|hypothesis|genomic-gap')
name=sys.argv[1];file,expected,offset,frames=choices[name];video=root/file
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((video.parent/'render-manifest.json').read_text())
if manifest['frames']!=frames or manifest['fps']!=30:raise SystemExit('Wrong render frame count or rate')
for source,checksum in manifest['input_sha256'].items():
 if not (root/source).is_file() or digest(root/source)!=checksum:raise SystemExit(f'Render source changed: {source}')
if expected is None:expected=manifest['output_sha256']
if manifest['output_sha256']!=expected:raise SystemExit('Unexpected render manifest')
if not video.is_file() or digest(video)!=expected:raise SystemExit('Missing or changed input render')
if digest(audio)!='434f2c344b428982edf8b00607b8361c4c45bec95da6ac5330c87428a45c3760':raise SystemExit('Unexpected soundtrack')
out=root/f'.cache/mammoth-edit/{name}-incomplete-workprint.mp4';out.parent.mkdir(parents=True,exist_ok=True)
ff=imageio_ffmpeg.get_ffmpeg_exe();duration=frames/30
cmd=[ff,'-y','-hide_banner','-loglevel','error','-i',str(video),'-ss',str(offset),'-i',str(audio),'-filter_complex',f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS[a]','-map','0:v:0','-map','[a]','-frames:v',str(frames),'-c:v','libx264','-preset','fast','-crf','20','-threads','2','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True)
r=subprocess.run([ff,'-hide_banner','-i',str(out),'-filter_complex','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
f=re.findall(r'frame=\s*(\d+)',r.stderr);peak=re.findall(r'Peak:\s*(-?[\d.]+) dBFS',r.stderr);lu=re.findall(r'I:\s*(-?[\d.]+) LUFS',r.stderr)
if not f or int(f[-1])!=frames or not peak or float(peak[-1])>-1 or not lu:raise SystemExit('Decode/frame/peak failure')
report={'status':'incomplete separate editorial insert, not final','narration_offset_seconds':offset,'frames':frames,'fps':30,'lufs':float(lu[-1]),'true_peak_dbtp':float(peak[-1]),'input_sha256':expected,'audio_sha256':digest(audio),'output_sha256':digest(out)}
(out.parent/f'{name}-qc.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
