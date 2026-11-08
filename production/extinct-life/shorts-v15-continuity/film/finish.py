"""Mux only matching complete native-render receipts, then audit the actual encoded delivery.
No upload. Signal diagnostics are not creative/perceptual/anatomical approval.
"""
from pathlib import Path
import json,hashlib,subprocess,re
import numpy as np
from PIL import Image,ImageDraw
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'production/extinct-life/shorts-v15-continuity';C=ROOT/'.cache/shorts-v15';R=B/'review';R.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe();S=json.loads((B/'film/timeline.json').read_text());N=S['total_frames'];FPS=S['fps'];FINAL=ROOT/'deliverables/Extinct-Life-V15-Continuity-Rebuild-1080x1920.mp4';FINAL.parent.mkdir(exist_ok=True);OUT=C/'candidate-reviewed.mp4'
build=hashlib.sha256((B/'film/scene.mjs').read_bytes()+(B/'film/timeline.json').read_bytes()).hexdigest();receipts=[]
for start,end in [(0,650),(650,N)]:
 r=json.loads((C/f'render-{start}-{end}.json').read_text());assert r['from']==start and r['to']==end and r['frames']==end-start and not r['page_errors'];receipts.append(r)
if all(r['source_sha256']==build for r in receipts):
 parts=C/'concat-final.txt';parts.write_text(''.join("file '"+str(C/f'part-{a}-{b}.mp4')+"'\n" for a,b in [(0,650),(650,N)]))
 subprocess.run([FF,'-y','-v','warning','-f','concat','-safe','0','-i',str(parts),'-i',str(C/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-t',str(S['duration']),str(OUT)],check=True)
 assembly={'method':'matching native halves; first-generation H264 video copied'}
else:
 archived=(B/'film/base-render-scene.mjs').read_text();current=(B/'film/scene.mjs').read_text()
 expected=archived.replace("cell=ball(macro,V(-1.9,.45,-.7)","cell=ball(macro,V(-1.9,.45,.3)").replace("label='MOLECULAR PROCESS · NOT TO SCALE';","if(cell.visible)aim(-.7,.55,7.5,-1.3,.25,-.3);label='MOLECULAR PROCESS · NOT TO SCALE';")
 assert current==expected,'Unbounded source changes cannot be replaced by a small framing patch'
 basebuild=hashlib.sha256((B/'film/base-render-scene.mjs').read_bytes()+(B/'film/timeline.json').read_bytes()).hexdigest();assert all(r['source_sha256']==basebuild for r in receipts)
 patch=json.loads((C/'render-439-527.json').read_text());assert patch['source_sha256']==build and patch['from']==439 and patch['to']==527 and patch['frames']==88 and not patch['page_errors']
 import math
 assert math.ceil(16.8/S['story_time_scale']*FPS)==439 and math.ceil(20.19/S['story_time_scale']*FPS)==527
 binding=json.loads((C/'framing-patch.json').read_text());base=Path(binding['base_complete_file']);assert hashlib.sha256(base.read_bytes()).hexdigest()==binding['base_complete_sha256']
 filters='[0:v]trim=end_frame=439,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[0:v]trim=start_frame=527,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]'
 subprocess.run([FF,'-y','-v','warning','-i',str(base),'-i',str(C/'part-439-527.mp4'),'-filter_complex',filters,'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-movflags','+faststart','-t',str(S['duration']),str(OUT)],check=True)
 assembly={'method':'88-frame native framing correction spliced into base edit; final H264 re-encode, unchanged AAC copied','base_build_sha256':basebuild,'base_video_sha256':binding['base_complete_sha256'],'patched_range_inclusive_exclusive':[439,527],'patch_build_sha256':build,'unchanged_outside_patch_condition':True}
p=subprocess.Popen([FF,'-v','error','-i',str(OUT),'-an','-vf','scale=270:480','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
means=[];diffs=[];last=None;samples={};count=0;needed=set(range(0,N,FPS))|{N-1}
while True:
 raw=p.stdout.read(270*480*3)
 if not raw:break
 assert len(raw)==270*480*3
 a=np.frombuffer(raw,np.uint8).reshape(480,270,3);means.append(float(a.mean()));roi=a[110:325,25:245].astype(np.float32)
 if last is not None:diffs.append(float(np.abs(roi-last).mean()))
 last=roi
 if count in needed:samples[count]=Image.fromarray(a.copy())
 count+=1
err=p.stderr.read().decode();assert p.wait()==0,err;assert count==N,(count,N);assert min(means)>5
frames=[30,180,270,480,600,720,810,930,1110,1260]
for f in frames:
 subprocess.run([FF,'-y','-v','error','-i',str(OUT),'-vf',f'select=eq(n\\,{f})','-frames:v','1','-q:v','2',str(R/f'{f:04}.jpg')],check=True)
sheet=Image.new('RGB',(270*6,510*((len(samples)+5)//6)),'#10232a');d=ImageDraw.Draw(sheet)
for i,(f,im) in enumerate(sorted(samples.items())):
 x=i%6*270;y=i//6*510;sheet.paste(im,(x,y));d.text((x+8,y+483),f'{f/FPS:.2f}s / f{f}',fill='#ffffff')
sheet.save(R/'encoded-overview.jpg',quality=86)
q=subprocess.run([FF,'-hide_banner','-i',str(OUT),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);matches=re.findall(r'\{\s*"input_i".*?\}',q.stderr,re.S);assert matches;sound=json.loads(matches[-1]);(R/'encoded-loudness.json').write_text(json.dumps(sound,indent=2)+'\n')
meta=subprocess.run([FF,'-hide_banner','-i',str(OUT),'-f','null','-'],capture_output=True,text=True,check=True);(R/'decode-log.txt').write_text(meta.stderr);assert '1080x1920' in meta.stderr and '30 fps' in meta.stderr
assert -19<float(sound['input_i'])<-13;assert float(sound['input_tp'])<=-.5
OUT.replace(FINAL);OUT=FINAL
sha=hashlib.sha256(OUT.read_bytes()).hexdigest();sources={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((B/'film').glob('*')) if f.is_file()};baseline=json.loads((B/'PROTECTED-BASELINES.json').read_text())
for name,expected in baseline.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,'Protected existing film changed: '+name
qc={'status':'technical export checks complete; owner creative acceptance pending','decoded_frames':count,'expected_frames':N,'width':1080,'height':1920,'fps':FPS,'duration_seconds':S['duration'],'native_3d_resolution':[1080,1920],'interpolated_frames':False,'upscaled_3d':False,'all_frames_nonblack':True,'minimum_mean_pixel_value':min(means),'scene_roi_adjacent_frame_differences':{'mean':float(np.mean(diffs)),'min':min(diffs),'max':max(diffs),'exact_repeated_roi_pairs':sum(x==0 for x in diffs),'limit':'A signal check, not proof of useful motion, correct contacts or aesthetic quality.'},'extracted_native_review_frames_NOT_yet_a_watch_attestation':frames,'overview_sample_positions':len(samples),'assembly':assembly,'source_build_sha256':build,'source_sha256':sources,'file_sha256':sha,'encoded_audio':sound,'voice_pitch_preserving_tempo':S['story_time_scale'],'voice_changed_only_in_new_short':True,'protected_baselines_match':True,'competitor_exhaustive_study_complete':False,'independent_anatomical_validation':False,'full_perceptual_listening_certified':False,'owner_creative_acceptance':False,'youtube_published':False}
(B/'QC.json').write_text(json.dumps(qc,indent=2)+'\n');(B/'DELIVERY.json').write_text(json.dumps({'status':'Complete rendered Short; owner review pending','file':str(OUT.relative_to(ROOT)),'bytes':OUT.stat().st_size,'sha256':sha,'duration_seconds':S['duration'],'dimensions':[1080,1920],'fps':FPS,'caption_file':str((B/'English.srt').relative_to(ROOT)),'old_short_preserved':True,'v13_and_v14_full_films_changed':False,'selected_thumbnail_changed':False,'narration_text':'Existing approved 102-word English Short text, preserved','short_only_pitch_preserving_tempo':S['story_time_scale'],'youtube_published':False,'related_video_link_configured':False},indent=2)+'\n')
print(json.dumps({'file':str(OUT),'bytes':OUT.stat().st_size,'frames':count,'seconds':S['duration'],'encoded_audio':sound,'sha256':sha},indent=2))
