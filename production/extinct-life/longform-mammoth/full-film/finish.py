"""Assemble the original 30 fps opening and interpolated 3D documentary plates.

The old opening soundtrack is intentionally discarded. Output receives the new
voice/music/effects mix and timed captions on the post-opening shots.
"""
import json,math,subprocess,hashlib
from pathlib import Path
import imageio_ffmpeg

B=Path(__file__).resolve().parent;R=B.parents[3];C=R/'.cache/longform-mammoth-full';D=R/'deliverables';D.mkdir(exist_ok=True)
P=json.loads((B/'timeline.json').read_text());ff=imageio_ffmpeg.get_ffmpeg_exe()
source=R/'deliverables/Last-Mammoths-Opening-01-3D-1080p.mp4';plate=C/'visual-4fps.mp4';audio=C/'mix.wav';manifest=C/'render.json'
for f in [source,plate,audio,manifest]:
 if not f.exists():raise SystemExit('Missing required input: '+str(f))
m=json.loads(manifest.read_text());assert m['errors']==[] and m['count']==math.ceil((P['duration']-60)*4)
opening=json.loads((B.parent/'opening-3d/timeline.json').read_text())
all_cues=opening['captions']+P['captions']

def stamp(s):
 ms=round(s*1000);h,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);sec,ms=divmod(ms,1000)
 return f'{h:02}:{mi:02}:{sec:02},{ms:03}'
(B/'English.srt').write_text('\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(all_cues,1)))

def ass_time(s):
 s=max(0,s);cs=round(s*100);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100);return f'{h}:{m:02}:{s:02}.{cs:02}'
head='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Caption,Manrope,48,&H00F6F6F6,&H00FFFFFF,&HAA101820,&HAA101820,-1,0,0,0,100,100,0,0,3,12,0,2,70,70,50,1\nStyle: Source,Manrope,25,&H00F6F6F6,&H00FFFFFF,&HAA101820,&HAA101820,-1,0,0,0,100,100,0,0,3,10,0,2,90,90,60,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
lines=[]
for c in P['captions']:
 text=c['text'].replace('{','').replace('}','').replace('\\','')
 lines.append(f"Dialogue: 0,{ass_time(c['start']-60)},{ass_time(c['end']-60)},Caption,,0,0,0,,{text}")
# Source card appears after the final spoken line, over the existing closing shot.
source_start = max(P['chapters'][-1]['end'] + .5, P['duration'] - 5.0) - 60
source_end = P['duration'] - .15 - 60
source_text = (r'SOURCES: PLOS GENETICS 2017 · 10.1371/journal.pgen.1006601\N'
               r'QUATERNARY SCIENCE REVIEWS 2019 · 10.1016/j.quascirev.2019.105884\N'
               r'CELL 2024 · 10.1016/j.cell.2024.05.033  |  CELL 2025 · 10.1016/j.cell.2025.08.003')
lines.append(f"Dialogue: 1,{ass_time(source_start)},{ass_time(source_end)},Source,,0,0,0,,{source_text}")
(C/'captions.ass').write_text(head+'\n'.join(lines)+'\n')
# Blend temporal samples for slow 3D motion, upscale to 1080p, then overlay
# captions at native resolution. The final sampled frame is extended to cover
# the exact soundtrack duration.
seconds=P['duration']-60
filters=(f"[0:v]trim=duration=60,setpts=PTS-STARTPTS,setsar=1[op];"
         f"[1:v]setpts=PTS-STARTPTS,minterpolate=fps=30:mi_mode=blend,"
         f"tpad=stop_mode=clone:stop_duration=0.3,trim=duration={seconds:.3f},"
         f"scale=1920:1080:flags=lanczos,setsar=1,ass='{C/'captions.ass'}':fontsdir='{R/'public/showreel/fonts'}'[body];"
         f"[op][body]concat=n=2:v=1:a=0[v]")
out=D/'Last-Mammoths-Full-Film-3D-1080p.mp4'
subprocess.run([ff,'-y','-v','warning','-i',str(source),'-i',str(plate),'-i',str(audio),
 '-filter_complex',filters,'-map','[v]','-map','2:a:0','-t',str(P['duration']),
 '-c:v','libx264','-preset','veryfast','-b:v','550k','-maxrate','950k','-bufsize','1900k',
 '-threads','2','-pix_fmt','yuv420p','-r','30','-af','volume=-1.0dB','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
print(json.dumps({'file':str(out.relative_to(R)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'captions':len(all_cues)},indent=2))
