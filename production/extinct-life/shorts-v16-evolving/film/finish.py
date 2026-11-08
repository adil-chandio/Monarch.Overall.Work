"""Complete V16 with one retained opening segment and newly rendered evolving scenes; no looping."""
from pathlib import Path
import json,hashlib,subprocess,re
import numpy as np
from PIL import Image,ImageDraw
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'production/extinct-life/shorts-v16-evolving';C=ROOT/'.cache/shorts-v16';R=B/'review';R.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe();S=json.loads((B/'film/timeline.json').read_text());N=S['total_frames'];FPS=S['fps'];FINAL=ROOT/'deliverables/Extinct-Life-V16-Evolving-Story-1080x1920.mp4';FINAL.parent.mkdir(exist_ok=True);OUT=C/'candidate-reviewed.mp4'
build=hashlib.sha256((B/'film/scene.mjs').read_bytes()+(B/'film/timeline.json').read_bytes()).hexdigest();r=json.loads((C/'render-323-1305.json').read_text());assert r['source_sha256']==build and r['from']==323 and r['to']==1305 and r['frames']==982 and not r['page_errors']
runs=[{'scene':'opening','from':0,'to':130},{'scene':'sampling','from':130,'to':323}]+r['scene_runs'];assert len(runs)==10 and len({x['scene'] for x in runs})==10;assert all(a['to']==z['from'] for a,z in zip(runs,runs[1:]));assert runs[-1]['to']==N
base=ROOT/'deliverables/Extinct-Life-V15-Continuity-Rebuild-1080x1920.mp4';basehash=hashlib.sha256(base.read_bytes()).hexdigest();assert basehash=='20307333d5e9306b568f9ec7dc6d54ba9153d17eff059136dc9aca81e15707de'
filters='[0:v]trim=end_frame=323,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]'
subprocess.run([FF,'-y','-v','warning','-i',str(base),'-i',str(C/'part-323-1305.mp4'),'-i',str(C/'mix.wav'),'-filter_complex',filters,'-map','[v]','-map','2:a:0','-c:v','libx264','-preset','fast','-crf','19','-threads','2','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','aac','-b:a','256k','-movflags','+faststart','-t','43.5',str(OUT)],check=True)
assembly={'method':'Approved opening + sampling retained ONCE, then new lab/cell/binding/comparison/basin/limits/checks/canyon progression','retained_v15_frames':[0,323],'new_native_render_frames':[323,1305],'new_native_frame_count':982,'base_sha256':basehash,'looped_or_repeated_edit_segments':False,'meaningful_scene_run_count':10,'same_set_return_count':0,'actual_scene_runs':runs,'quality_multiplier_verified':False}
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
frames=[30,180,270,390,480,600,720,810,930,990,1110,1260]
for f in frames:
 subprocess.run([FF,'-y','-v','error','-i',str(OUT),'-vf',f'select=eq(n\\,{f})','-frames:v','1','-q:v','2',str(R/f'{f:04}.jpg')],check=True)
sheet=Image.new('RGB',(270*6,510*((len(samples)+5)//6)),'#10232a');d=ImageDraw.Draw(sheet)
for i,(f,im) in enumerate(sorted(samples.items())):
 x=i%6*270;y=i//6*510;sheet.paste(im,(x,y));d.text((x+8,y+483),f'{f/FPS:.2f}s / f{f}',fill='#ffffff')
sheet.save(R/'encoded-overview.jpg',quality=86)
q=subprocess.run([FF,'-hide_banner','-i',str(OUT),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);matches=re.findall(r'\{\s*"input_i".*?\}',q.stderr,re.S);assert matches;sound=json.loads(matches[-1]);(R/'encoded-loudness.json').write_text(json.dumps(sound,indent=2)+'\n')
meta=subprocess.run([FF,'-hide_banner','-i',str(OUT),'-f','null','-'],capture_output=True,text=True,check=True);(R/'decode-log.txt').write_text(meta.stderr);assert '1080x1920' in meta.stderr and '30 fps' in meta.stderr
assert -19<float(sound['input_i'])<-13;assert float(sound['input_tp'])<=-.5
baseline=json.loads((B/'PROTECTED-BASELINES.json').read_text())
for name,expected in baseline.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,'Protected existing film changed: '+name
OUT.replace(FINAL);OUT=FINAL
sha=hashlib.sha256(OUT.read_bytes()).hexdigest();sources={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((B/'film').glob('*')) if f.is_file()};baseline=json.loads((B/'PROTECTED-BASELINES.json').read_text())
for name,expected in baseline.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,'Protected existing film changed: '+name
qc={'status':'technical export checks complete; owner creative acceptance pending','decoded_frames':count,'expected_frames':N,'width':1080,'height':1920,'fps':FPS,'duration_seconds':S['duration'],'native_3d_resolution':[1080,1920],'interpolated_frames':False,'upscaled_3d':False,'all_frames_nonblack':True,'minimum_mean_pixel_value':min(means),'scene_roi_adjacent_frame_differences':{'mean':float(np.mean(diffs)),'min':min(diffs),'max':max(diffs),'exact_repeated_roi_pairs':sum(x==0 for x in diffs),'limit':'A signal check, not proof of useful motion, correct contacts or aesthetic quality.'},'extracted_native_review_frames_NOT_yet_a_watch_attestation':frames,'overview_sample_positions':len(samples),'assembly':assembly,'source_build_sha256':build,'source_sha256':sources,'file_sha256':sha,'encoded_audio':sound,'voice_pitch_preserving_tempo':S['story_time_scale'],'voice_source_and_tempo_unchanged_from_v15':True,'protected_baselines_match':True,'competitor_exhaustive_study_complete':False,'independent_anatomical_validation':False,'full_perceptual_listening_certified':False,'owner_creative_acceptance':False,'youtube_published':False}
(B/'QC.json').write_text(json.dumps(qc,indent=2)+'\n');(B/'DELIVERY.json').write_text(json.dumps({'status':'Complete rendered Short; owner review pending','file':str(OUT.relative_to(ROOT)),'bytes':OUT.stat().st_size,'sha256':sha,'duration_seconds':S['duration'],'dimensions':[1080,1920],'fps':FPS,'caption_file':str((B/'English.srt').relative_to(ROOT)),'v15_preserved':True,'retained_opening_and_sampling_frames':323,'new_native_frames':982,'v13_and_v14_full_films_changed':False,'selected_thumbnail_changed':False,'narration_text':'Existing approved 102-word English Short text, preserved','tempo_unchanged_from_v15':True,'short_only_pitch_preserving_tempo':S['story_time_scale'],'youtube_published':False,'related_video_link_configured':False},indent=2)+'\n')
print(json.dumps({'file':str(OUT),'bytes':OUT.stat().st_size,'frames':count,'seconds':S['duration'],'encoded_audio':sound,'sha256':sha},indent=2))
