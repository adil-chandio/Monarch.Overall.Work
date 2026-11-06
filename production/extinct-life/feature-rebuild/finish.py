"""Assemble the complete film, normalize audio, and audit the actual final encode."""
from pathlib import Path
import sys,json,re,subprocess,wave,math
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent; R=P.parents[2]; C=R/'.cache/extinct-rebuild'; F=imageio_ffmpeg.get_ffmpeg_exe()
plan=json.loads((P/'timeline.json').read_text())
out=R/'deliverables/Extinct_Life_EP01_Urdnglish_ShortShot_Rebuild_1080p.mp4'
def run(args,**kw):return subprocess.run([F,*map(str,args)],check=True,**kw)
def loudness(file):
 r=run(['-hide_banner','-i',file,'-vn','-af','loudnorm=I=-16:TP=-2.8:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True)
 return json.loads(re.search(r'\{\s*"input_i".*?\}',r.stderr,re.S).group())
# New narration/mix only. The old opening and old full-film MP4 are never inputs.
pre=loudness(C/'mix.wav');(C/'pre-normalization.json').write_text(json.dumps(pre,indent=2))
if '--audio-only' in sys.argv:
 print('Complete audio assembled and measured.');sys.exit(0)
files=[C/f'chapter-{i}.mp4' for i in range(8)]
assert all(x.exists() for x in files), 'Render all chapters first'
(C/'picture-list.txt').write_text(''.join("file '"+str(x)+"'\n" for x in files))
meta=';FFMETADATA1\ntitle=The Lost World Inside a Handful of Dirt\nartist=Extinct Life\ncomment=Original 2.5D illustration; synthetic narration and original synthetic score.\n'
chapters=[(c['title'],round(c['start_frame']/30*1000),round((c['start_frame']+c['frames'])/30*1000)) for c in plan['chapters']]
for title,a,b in chapters:meta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={a}\nEND={b}\ntitle={title}\n'
(C/'chapters.txt').write_text(meta)
af=f"loudnorm=I=-16:TP=-2.8:LRA=11:measured_I={pre['input_i']}:measured_TP={pre['input_tp']}:measured_LRA={pre['input_lra']}:measured_thresh={pre['input_thresh']}:offset={pre['target_offset']}:linear=true"
expected=plan['frames']
run(['-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',C/'picture-list.txt','-i',C/'mix.wav','-i',C/'chapters.txt','-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','libx264','-threads','4','-preset','fast','-crf','20','-maxrate','1550k','-bufsize','3100k','-pix_fmt','yuv420p','-vf','setpts=N/(30*TB),setsar=1','-fps_mode','passthrough','-c:a','aac','-b:a','192k','-af',af,'-frames:v',str(expected),'-movflags','+faststart',out])
assert out.stat().st_size<100*1024*1024,'Artifact exceeds GitHub single-file limit'
# A full decode is separate from creative approval.
r=run(['-hide_banner','-i',out,'-an','-vf','freezedetect=n=-60dB:d=1,blackdetect=d=0.35:pix_th=0.02:pic_th=0.99','-progress','pipe:1','-f','null','-'],capture_output=True,text=True)
frames=[int(x) for x in re.findall(r'^frame=(\d+)$',r.stdout,re.M)];assert frames[-1]==expected,(frames[-1],expected)
assert '1920x1080' in r.stderr and '30 fps' in r.stderr
issues=[x for x in r.stderr.splitlines() if 'freeze_' in x or 'black_start:' in x]
assert not any('black_start:' in x for x in issues),'Unexpected black interval'
motion=run(['-v','error','-i',out,'-vf','fps=2,scale=320:180','-an','-f','framemd5','-'],capture_output=True,text=True)
hashes=[x.split(',')[-1].strip() for x in motion.stdout.splitlines() if x.strip() and not x.startswith('#')]
levels=loudness(out);assert float(levels['input_tp'])<-.5
# Sample every chapter in the final encode, plus opening and closing.
times=[(c['start_frame']+c['frames']*p)/30 for c in plan['chapters'] for p in [.12,.6]]+[plan['seconds']-.25]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
for page in range(2):
 sheet=Image.new('RGB',(1440,760),'#10242d');d=ImageDraw.Draw(sheet)
 for n,t in enumerate(times[page*10:(page+1)*10]):
  file=C/f'final-{page*10+n:02d}.jpg';run(['-y','-v','error','-ss',str(t),'-i',out,'-frames:v','1',file])
  x=n%4*360;y=n//4*253;sheet.paste(Image.open(file).resize((360,203)),(x,y));d.text((x+8,y+214),f'{int(t)//60:02d}:{t%60:04.1f} / FINAL ENCODE',font=font,fill='#e6bc75')
 sheet.save(C/f'final-contact-{page}.jpg',quality=92)
qc=dict(file=str(out.relative_to(R)),bytes=out.stat().st_size,native_resolution=[1920,1080],fps=30,duration_seconds=plan['seconds'],decoded_frames=frames[-1],expected_frames=expected,chapters=8,new_body_shots=len(plan['shots']),original_opening_reused_seconds=0,new_voice_clips=8,voice_id='voice-01',language='Temporary easy Urdu-English',max_shot_seconds=max((x['end_frame']-x['start_frame'])/30 for x in plan['shots']),timing_method=plan['timing_method'],audio_measurement=levels,half_second_samples=dict(count=len(hashes),unique=len(set(hashes))),black_or_freeze_events=issues,interpretation='Low-motion diagnostics are retained; shot duration and motion hashes are technical checks, not evidence of zero boredom.',sampled_final_times=times,review_scope='All 231 native previews generated; 47 subject representatives and selected full-resolution frames inspected, plus 17 final encode samples. Not a complete real-time audiovisual watch or independently verified word alignment.',scientific_scope='Interpretive animation, not validated anatomy, actual microscopy, measured reads or actual study-site footage.',owner_full_film_approval='pending',youtube_upload=False)
(P/'QC.json').write_text(json.dumps(qc,indent=2)+'\n');print(json.dumps({k:v for k,v in qc.items() if k not in ['black_or_freeze_events','sampled_final_times']},indent=2))
