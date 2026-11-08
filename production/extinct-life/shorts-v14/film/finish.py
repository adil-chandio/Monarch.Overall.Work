"""Require completed native halves, mux, decode and measure. No upload."""
import json,pathlib,subprocess,hashlib,re,sys
import numpy as np
from PIL import Image,ImageDraw
import imageio_ffmpeg
ROOT=pathlib.Path.cwd();B=ROOT/'production/extinct-life/shorts-v14';C=ROOT/'.cache/shorts-v14';R=B/'review';R.mkdir(exist_ok=True);FF=imageio_ffmpeg.get_ffmpeg_exe();OUT=ROOT/'deliverables/Extinct-Life-V14-Mastodon-Short-1080x1920.mp4'
for a,b in [(0,750),(750,1500)]:
 q=json.loads((C/f'render-{a}-{b}.json').read_text());assert q['frames']==b-a and not q['page_errors']
parts=C/'concat.txt';parts.write_text(''.join("file '"+str(C/f'part-{a}-{b}.mp4')+"'\n" for a,b in [(0,750),(750,1500)]))
subprocess.run([FF,'-y','-v','warning','-f','concat','-safe','0','-i',str(parts),'-i',str(C/'mix.wav'),'-map','0:v:0','-map','1:a:0','-vf','eq=brightness=0.015:gamma=1.06:saturation=1.04','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-t','50',str(OUT)],check=True)
# Every encoded frame decoded and measured; moving scene ROI excludes header/captions/progress bar.
p=subprocess.Popen([FF,'-v','error','-i',str(OUT),'-an','-vf','scale=270:480','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
count=0;means=[];diffs=[];last=None;sampled={};needed=set(range(0,1500,30))|{1499}
while True:
 raw=p.stdout.read(270*480*3)
 if not raw:break
 assert len(raw)==270*480*3
 a=np.frombuffer(raw,np.uint8).reshape(480,270,3);means.append(float(a.mean()));roi=a[120:325,30:240].astype(float)
 if last is not None:diffs.append(float(np.abs(roi-last).mean()))
 last=roi
 if count in needed:sampled[count]=Image.fromarray(a.copy())
 count+=1
stderr=p.stderr.read().decode();assert p.wait()==0,stderr;assert count==1500,count;assert min(means)>5
# Full-res representative encoded frames, including corrected animal, sediment and end bridge.
frames=[60,270,450,660,780,930,1080,1260,1440]
for f in frames:
 subprocess.run([FF,'-y','-v','error','-i',str(OUT),'-vf',f'select=eq(n\\,{f})','-frames:v','1','-q:v','2',str(R/f'{f:04}.jpg')],check=True)
# Time-indexed overview: each image is an actual decoded frame, not generated competitor reference.
sheet=Image.new('RGB',(270*6,510*9),'#081c24');d=ImageDraw.Draw(sheet)
for i,(f,im) in enumerate(sorted(sampled.items())):
 x=i%6*270;y=i//6*510;sheet.paste(im,(x,y));d.text((x+8,y+482),f'{f/30:05.2f}s / frame {f}',fill='#ffffff')
sheet.save(R/'encoded-overview.jpg',quality=87)
# Final encoded AAC measurement (not only the intermediate WAV).
q=subprocess.run([FF,'-hide_banner','-i',str(OUT),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
m=re.findall(r'\{\s*"input_i".*?\}',q.stderr,re.S);assert m,'No loudness result';sound=json.loads(m[-1]);(R/'encoded-loudness.json').write_text(json.dumps(sound,indent=2)+'\n')
meta=subprocess.run([FF,'-hide_banner','-i',str(OUT),'-f','null','-'],capture_output=True,text=True,check=True);(R/'decode-log.txt').write_text(meta.stderr)
assert '1080x1920' in meta.stderr and '30 fps' in meta.stderr
assert -19<float(sound['input_i'])<-13
assert float(sound['input_tp'])<=-.5
sha=hashlib.sha256(OUT.read_bytes()).hexdigest();sources={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((B/'film').glob('*')) if f.is_file()}
qc={'decoded_frames':count,'expected_frames':1500,'width':1080,'height':1920,'fps':30,'duration_seconds':50,'native_3d_resolution':[1080,1920],'interpolated_frames':False,'upscaled_3d':False,'nonblack_all_frames':True,'min_mean_pixel_value':min(means),'scene_roi_adjacent_frame_difference':{'mean':float(np.mean(diffs)),'min':min(diffs),'max':max(diffs),'exact_repeated_roi_pairs':sum(x==0 for x in diffs),'note':'Signal diagnostic, not proof of character realism, aesthetic quality or retention.'},'encoded_full_resolution_inspection_frames':frames,'one_per_second_overview_frames':len(sampled),'final_encoded_audio':sound,'unit_tests':{'command':'.venv/bin/python production/extinct-life/shorts-v14/film/test_timeline.py','passed':8},'source_sha256':sources,'file_sha256':sha,'competitor_frame_by_frame_watch_completed':False,'independent_anatomical_validation':False,'full_perceptual_audio_listening_approval':False,'owner_creative_acceptance':False,'public_upload_performed':False}
(B/'QC.json').write_text(json.dumps(qc,indent=2)+'\n');(B/'DELIVERY.json').write_text(json.dumps({'status':'Rendered review candidate; owner acceptance pending','file':str(OUT.relative_to(ROOT)),'bytes':OUT.stat().st_size,'sha256':sha,'duration_seconds':50,'dimensions':[1080,1920],'fps':30,'title':'How Do You Find a Mastodon Without Its Body?','caption_file':'production/extinct-life/shorts-v14/English.srt','related_video_youtube_id':None,'related_video_link_configured':False,'voice_speed_changed':False,'music':'Original instrumental score','sfx':'Original synthetic illustrative Foley','v13_v14_changed':False,'public_upload_performed':False},indent=2)+'\n')
print(json.dumps({'file':str(OUT.relative_to(ROOT)),'bytes':OUT.stat().st_size,'frames':count,'sound':sound,'sha256':sha},indent=2))
