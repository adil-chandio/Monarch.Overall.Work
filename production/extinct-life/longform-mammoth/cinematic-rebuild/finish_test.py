"""Finish ONLY the 22 s exploratory 3D test; never overwrite the full-film master."""
import json, subprocess, hashlib
from pathlib import Path
import imageio_ffmpeg

B=Path(__file__).resolve().parent
R=B.parents[3]
C=R/'.cache/longform-mammoth-cinematic-rebuild'
A=R/'.cache/longform-mammoth-full/mix.wav'
P=json.loads((B.parent/'full-film/timeline.json').read_text())
manifest=json.loads((C/'render-0-660.json').read_text())
assert manifest['from']==0 and manifest['to']==660 and manifest['frames']==660
assert manifest['fps']==30 and manifest['width']==1280 and manifest['height']==720
assert manifest['page_errors']==[]
assert A.exists(), 'Build the replacement mix with full-film/sound.py first.'

def stamp(s):
    ms=round(s*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);sec,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{sec:02},{ms:03}'
cues=[]
for c in P['captions']:
    if c['end'] <= 60 or c['start'] >= 82: continue
    start=max(c['start'],60)-60;end=min(c['end'],82)-60
    cues.append(f"{len(cues)+1}\n{stamp(start)} --> {stamp(end)}\n{c['text']}\n")
(C/'test.srt').write_text('\n'.join(cues))
out=R/'deliverables/Last-Mammoths-3D-Isolation-Test-22s.mp4'
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-y','-v','warning','-i',str(C/'part-0-660.mp4'),'-ss','60','-t','22','-i',str(A),
 '-map','0:v:0','-map','1:a:0','-vf',f"subtitles='{C/'test.srt'}':fontsdir='{R/'public/showreel/fonts'}':force_style='FontName=Manrope,FontSize=21,Alignment=2,MarginV=28,Outline=1,Shadow=1'",
 '-t','22','-r','30','-c:v','libx264','-preset','medium','-b:v','1800k','-maxrate','2500k','-bufsize','5000k','-pix_fmt','yuv420p','-threads','2',
 '-af','volume=-1dB','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
subprocess.run([ff,'-v','error','-i',str(out),'-f','null','-'],check=True)
print(json.dumps({'file':str(out.relative_to(R)),'duration_s':22,'fps':30,'width':1280,'height':720,
                  'frame_count':660,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
                  'disclaimer':'Experimental excerpt only; subtitles auto-aligned; no full-film completion or continuous listening review.'},indent=2))
