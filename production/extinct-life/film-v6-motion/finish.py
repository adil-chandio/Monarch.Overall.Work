"""Assemble selected actual-3D clips with approved voice and attributed composed music.
Music is downloaded from the composer's normal public link. No login/bypass or silent substitute.
"""
import hashlib,json,re,subprocess,urllib.request,wave,sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
B=Path(__file__).resolve().parent;ROOT=B.parents[2];C=ROOT/'.cache/extinct-v6';C.mkdir(parents=True,exist_ok=True);FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000
m=json.loads((B/'schedule.json').read_text());N=m['total_frames']*1600;D=m['total_frames']/30
lic=json.loads((B/'MUSIC-LICENSE.json').read_text());cues=json.loads((B/'action-cues.json').read_text())
def run(args):return subprocess.run([FF,'-y','-hide_banner','-loglevel','info',*map(str,args)],capture_output=True,text=True,check=True)
def wav(p,a):
 with wave.open(str(p),'wb') as w:w.setnchannels(a.shape[1] if a.ndim>1 else 1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(a,-.999,.999)*32767).astype('<i2').tobytes())
def pcm(p,channels=1):
 q=C/'decode.wav';run(['-i',p,'-t',str(D+2),'-ar',SR,'-ac',channels,q])
 with wave.open(str(q)) as w:a=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768
 return a.reshape(-1,channels) if channels>1 else a
voice=[]
for row in m['voice_clips']:
 a=pcm(B.parent/'film-v3/voice'/f'{row["chapter"]}.flac');voice.append(a[row['local_start_frame']*1600:row['local_end_frame']*1600])
v=np.concatenate(voice);assert len(v)==N
wav(C/'voice.wav',v)
if '--voice-only' in sys.argv:wav(C/'proof.wav',v);print('Voice-only live review audio, not final mix');sys.exit(0)
mp3=C/'sb_hiraeth.mp3'
# Multi-root artifact upload preserves .cache/ paths; reuse the officially downloaded source.
nested=C/'.cache/extinct-v6/sb_hiraeth.mp3'
if not mp3.exists() and nested.exists():mp3.write_bytes(nested.read_bytes())
if not mp3.exists():
 req=urllib.request.Request(lic['official_download'],headers={'User-Agent':'Monarch documentary production / attributed CC-BY use'})
 with urllib.request.urlopen(req,timeout=90) as r,mp3.open('wb') as f:
  data=r.read(35*1024*1024+1);assert len(data)<=35*1024*1024,'Unexpectedly large music response';f.write(data)
score=pcm(mp3,2)[:N];assert len(score)==N,'Track shorter than excerpt; no unapproved looping'
# Separate material textures and slow, narration-aware gain controls; no hard tone contacts.
sys.path.insert(0,str(B))
from sound import design,audit,smooth,REVISION
foley,env,sound_report=design(v,m,cues)
wav(C/'foley-unfiltered.wav',foley)
run(['-i',C/'foley-unfiltered.wav','-af','highpass=f=70,lowpass=f=4200,equalizer=f=3200:t=q:w=0.7:g=-3',C/'foley-shaped.wav'])
foley=pcm(C/'foley-shaped.wav',2)[:N];assert len(foley)==N
edge=480;edgefade=smooth(np.linspace(0,1,edge));foley[:edge]*=edgefade[:,None];foley[-edge:]*=edgefade[::-1,None]
pre=audit(foley,v);gain=1.
if pre['voiced_region_foley_relative_db'] is not None and pre['voiced_region_foley_relative_db'] < -30:
 gain=min(8.,10**((-28-pre['voiced_region_foley_relative_db'])/20),.08/max(1e-9,float(np.max(np.abs(foley)))))
foley*=gain;sound_report['bus_gain']=gain;sound_report['measured']=audit(foley,v)
check=sound_report['measured'];assert check['peak_dbfs']<=-18,check;assert check['maximum_sample_step']<.01,check;assert check['energy_fraction_above_6khz']<.001,check;assert check['endpoints_zero'],check
if check['voiced_region_foley_relative_db'] is not None:assert check['voiced_region_foley_relative_db']<=-16,check
# Gently shape the score's dialogue region, retaining the attributed composed recording.
wav(C/'score-source.wav',score)
run(['-i',C/'score-source.wav','-af','highpass=f=40,lowpass=f=14500,equalizer=f=2500:t=q:w=0.8:g=-1.5',C/'score-shaped.wav'])
score=pcm(C/'score-shaped.wav',2)[:N];assert len(score)==N
t=np.arange(N,dtype=np.float32)/SR;fade=smooth(t/1.5)*smooth((D-t)/2)
score*=.14*(1-.45*smooth(env/.065))[:,None]*fade[:,None]
mix=v[:,None]+score+foley;premaster_peak=float(np.max(np.abs(mix)));premaster_gain=min(1.,.95/max(1e-12,premaster_peak));mix*=premaster_gain;sound_report['premaster_peak_before_safety']=premaster_peak;sound_report['premaster_safety_gain']=premaster_gain
(B/'SOUND-QC.json').write_text(json.dumps(sound_report,indent=2)+'\n')
wav(C/'score-excerpt.wav',score);wav(C/'foley.wav',foley);wav(C/'mix.wav',mix)
def levels(p):
 q=run(['-i',p,'-vn','-af','loudnorm=I=-16:TP=-2.5:LRA=9:print_format=json','-f','null','-']);return json.loads(q.stderr[q.stderr.rfind('{'):q.stderr.rfind('}')+1])
a=levels(C/'mix.wav');norm='loudnorm=I=-16:TP=-2.5:LRA=9:linear=true:'+':'.join(f'{k}={a[v]}' for k,v in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')]);norm+=',aresample=192000,alimiter=limit=0.70:level=false:attack=5:release=80:latency=1,aresample=48000'
run(['-i',C/'mix.wav','-af',norm,C/'proof.wav'])
(B/'CREDITS.md').write_text("# Music attribution\n\n"+lic['required_credit']+'\n\n'+lic['official_track_page']+'\n\nLicence: '+lic['license_url']+'\n\n'+lic['modifications']+'.\n\nIf published on YouTube, this credit must be included in the video description. This delivery is on GitHub only. Foley is original synthesized sound design, not claimed as recorded field sound.\n')
if '--audio-only' in sys.argv:print('Attributed composed-track candidate and existing voice prepared; no listening approval claimed');sys.exit(0)
reports=sorted([json.loads(p.read_text()) for p in C.glob('render-*.json')],key=lambda r:r['from']);cursor=0;parts=[]
for r in reports:assert r['from']==cursor and not r['page_errors'];cursor=r['to'];parts.append(C/f'part-{r["from"]}-{r["to"]}.mp4')
assert cursor==m['total_frames'],(cursor,m['total_frames']);lst=C/'concat.txt';lst.write_text(''.join("file '"+str(p)+"'\n" for p in parts));out=C/'Extinct_Life_V6_Actual_3D_Motion_Development.mp4'
run(['-f','concat','-safe','0','-i',lst,'-i',C/'proof.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar',SR,'-metadata','comment='+lic['required_credit']+' | '+lic['license_url'],'-t',f'{D:.9f}','-movflags','+faststart',out])
encoded=levels(out);assert abs(float(encoded['input_i'])+16)<1.1,encoded;assert float(encoded['input_tp'])<=-1.5,encoded
q=run(['-i',out,'-map','0:v:0','-progress','pipe:1','-nostats','-f','null','-']);decoded=int(re.findall(r'^frame=(\d+)',q.stdout,re.M)[-1]);assert decoded==m['total_frames'];assert '1920x1080' in q.stderr
report={'status':'Selected actual-3D development excerpt, not the full film','width':1920,'height':1080,'fps':30,'native_frames':decoded,'duration_seconds':D,'script_sha256':m['script_sha256'],'voice_speed_changed':False,'new_voice_generated':False,'generated_scene_images_used':False,'old_rendered_movie_used':False,'v4_geometry_and_style_baseline_reused':True,'action_revision':cues['revision'],'new_motion':['visible leaf current tracer with surface landing rings','stream-following visible markers and spatially dispersed settlement','five visibly accumulating sediment bands with exposed marker cohorts','deposit-age bracket attached to whole section','subtle head orientation and detached leaves after branch contact','stance-phase foot locking','leg joint continuity','articulated goose neck/head flight posture and retracted feet','one-way takeoff with surface rings','geometric branch contact','source-to-sample transport','successive deposition batches'],'composed_music':lic,'music_download_sha256':hashlib.sha256(mp3.read_bytes()).hexdigest(),'visual_refinements':['irregular approximate wave/sky shading','wind-responsive shore reeds with matched depth deformation','fine section-cap grain geometry','environmental marker label fade-out'],'sound_revision':REVISION,'sound_audit':sound_report['measured'],'foley':'Soft material-specific non-tonal synthesized sound design; not recorded field audio or verified binaural ASMR','encoded_audio':encoded,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'full_decode':True,'full_film_complete':False,'human_full_watch_listen_claimed':False,'biological_accuracy_expert_validated':False,'owner_creative_approval':False}
(B/'QC.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
