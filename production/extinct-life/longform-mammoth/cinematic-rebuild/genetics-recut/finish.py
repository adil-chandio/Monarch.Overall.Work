"""Finish one experimental 29.77-second scene; never overwrite any full-film master."""
import hashlib, json, subprocess
from pathlib import Path
import imageio_ffmpeg

B=Path(__file__).resolve().parent;R=B.parents[4];C=R/'.cache/mammoth-genetics-recut';F=B.parent/'full-script'
manifest=json.loads((C/'render.json').read_text())
h=hashlib.sha256()
for name in ['scene.mjs','stage.html']:h.update((B/name).read_bytes())
assert manifest['scene_sha256']==h.hexdigest(), 'scene changed after render; rerender first'
assert (manifest['frames'],manifest['fps'],manifest['width'],manifest['height'])==(893,30,1280,720)
assert not manifest['errors']
plan=json.loads((F/'planned-shots.json').read_text());take=json.loads((F/'take-timeline.json').read_text())
t=next(x for x in take['sections'] if x['id']=='03-genome');start=t['start'];length=893/30

def stamp(s):
    ms=round(max(0,s)*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);ss,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{ss:02},{ms:03}'
cs=[]
for cue in plan['captions']:
    if cue['end']<=start or cue['start']>=start+length:continue
    a=max(start,cue['start'])-start;b=min(start+length,cue['end'])-start
    cs.append(f"{len(cs)+1}\n{stamp(a)} --> {stamp(b)}\n{cue['text']}\n")
(C/'excerpt.srt').write_text('\n'.join(cs))
ff=imageio_ffmpeg.get_ffmpeg_exe();video=C/'lab-plate.mp4';audio=F/'03-genome.mp3';out=R/'deliverables/Last-Mammoths-Genetics-3D-Recut-Test.mp4'
subprocess.run([ff,'-y','-v','warning','-i',str(video),'-i',str(audio),
 '-filter_complex',f"[0:v]subtitles='{C/'excerpt.srt'}':fontsdir='{R/'public/showreel/fonts'}':force_style='FontName=Manrope,FontSize=21,Alignment=2,MarginV=25,Outline=1.5,Shadow=1'[v]",
 '-map','[v]','-map','1:a:0','-t',f'{length:.9f}','-c:v','libx264','-preset','medium',
 '-b:v','1800k','-maxrate','2600k','-bufsize','5200k','-r','30','-threads','2','-pix_fmt','yuv420p',
 '-af','loudnorm=I=-16:TP=-2.5:LRA=7,volume=-0.5dB','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
subprocess.run([ff,'-v','error','-i',str(out),'-f','null','-'],check=True)
frames,duration=imageio_ffmpeg.count_frames_and_secs(str(out));assert frames==893,(frames,duration)
loud=subprocess.run([ff,'-hide_banner','-i',str(out),'-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
raw=loud[loud.rfind('{'):loud.rfind('}')+1];levels=json.loads(raw)
assert float(levels['input_tp']) < -1.0,levels
qc={'file':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,
    'frames':frames,'fps':30,'duration_s':round(duration,3),'dimensions':[1280,720],'scene_sha256':manifest['scene_sha256'],
    'master_narration_offset_s':start,'loudness_i_lufs':float(levels['input_i']),'true_peak_dbtp':float(levels['input_tp']),
    'full_decode_errors':False,'score_or_sfx':'none; narration only','captions':'automatic alignment; not human reviewed',
    'limitations':'Partial 3D scene, stylized reconstruction and schematic DNA; not a full film, no continuous subjective audio or visual review.'}
(B/'SCENE-TEST-QC.json').write_text(json.dumps(qc,indent=2)+'\n');print(json.dumps(qc,indent=2))
