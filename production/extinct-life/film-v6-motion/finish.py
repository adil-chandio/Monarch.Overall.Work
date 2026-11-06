"""Assemble selected actual-3D clips with approved voice and attributed composed music.
Music is downloaded from the composer's normal public link. No login/bypass or silent substitute.
"""
import hashlib,json,re,subprocess,urllib.request,wave,sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
B=Path(__file__).resolve().parent;ROOT=B.parents[2];C=ROOT/'.cache/extinct-v6';C.mkdir(parents=True,exist_ok=True);FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000
m=json.loads((B/'schedule.json').read_text());N=m['total_frames']*1600;D=m['total_frames']/30
lic=json.loads((B/'MUSIC-LICENSE.json').read_text())
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
if not mp3.exists():
 req=urllib.request.Request(lic['official_download'],headers={'User-Agent':'Monarch documentary production / attributed CC-BY use'})
 with urllib.request.urlopen(req,timeout=90) as r,mp3.open('wb') as f:
  data=r.read(35*1024*1024+1);assert len(data)<=35*1024*1024,'Unexpectedly large music response';f.write(data)
score=pcm(mp3,2)[:N];assert len(score)==N,'Track shorter than excerpt; no unapproved looping'
# Smooth dialogue envelope and understated scored bed; recorded/composed track, not the old tone loop.
power=np.pad(v.astype(np.float64)**2,(2400,2399));cum=np.concatenate(([0.],np.cumsum(power)));env=np.sqrt(np.maximum(0,(cum[4800:]-cum[:-4800])/4800)).astype(np.float32);duck=1-.42*np.clip(env/.1,0,1)
t=np.arange(N,dtype=np.float32)/SR;fade=np.minimum(1,t/1.5)*np.minimum(1,(D-t)/2);score*=.14*duck[:,None]*fade[:,None]
rng=np.random.default_rng(160619);foley=np.zeros((N,2),np.float32)
def contact(at,amp=.1,duration=.2,pan=0):
 i=round(at*SR);n=min(round(duration*SR),N-i)
 if n<=0 or i<0:return
 tt=np.arange(n)/SR;noise=rng.normal(0,1,n);grain=np.convolve(noise,np.ones(21)/21,mode='same');s=(grain*.7+.3*np.sin(2*np.pi*72*tt))*np.exp(-tt*22)*amp;foley[i:i+n,0]+=s*(1-pan);foley[i:i+n,1]+=s*(1+pan)
# Continuous low-level water texture across transport/living scenes, with no sentence resets.
for channel in range(2):
 z=rng.normal(0,1,N);bed=np.convolve(z,np.ones(101)/101,mode='same').astype(np.float32);bed*=.024*(.8+.2*np.sin(t*.4+channel))
 foley[:,channel]+=bed*fade
living=m['segments'][2]['start_frame']/30
for phase in [0,.25,.5,.75]:
 for cycle in range(1,8):
  at=(cycle-phase)*3.7
  if at<D-living:contact(living+at,.15,.22,.06 if phase>.4 else -.06)
for offset in [5.55,5.78,6.0]:contact(living+offset,.12,.3,-.1)
for batch in [0,2.4,4.8]:
 for j in range(10):contact(m['segments'][1]['start_frame']/30+batch+j*.045,.025,.10,(j%3-1)*.1)
# Wing texture follows the same 10 rad/s wing cycle as the 3D pose and attenuates on departure.
flight=np.maximum(0,t-living-5.55);wing=(t>living+5.55)*np.maximum(0,np.sin(t*10))**8*np.exp(-flight/6)
for channel in range(2):
 noise=rng.normal(0,1,N);filtered=np.convolve(noise,np.ones(13)/13,mode='same');foley[:,channel]+=(filtered*wing*.035).astype(np.float32)
mix=v[:,None]+score+foley;wav(C/'score-excerpt.wav',score);wav(C/'foley.wav',foley);wav(C/'mix.wav',mix)
def levels(p):
 q=run(['-i',p,'-vn','-af','loudnorm=I=-16:TP=-1.8:LRA=9:print_format=json','-f','null','-']);return json.loads(q.stderr[q.stderr.rfind('{'):q.stderr.rfind('}')+1])
a=levels(C/'mix.wav');norm='loudnorm=I=-16:TP=-1.8:LRA=9:linear=true:'+':'.join(f'{k}={a[v]}' for k,v in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')]);norm+=',aresample=192000,alimiter=limit=0.70:level=false:attack=5:release=80:latency=1,aresample=48000'
run(['-i',C/'mix.wav','-af',norm,C/'proof.wav'])
(B/'CREDITS.md').write_text("# Music attribution\n\n"+lic['required_credit']+'\n\n'+lic['official_track_page']+'\n\nLicence: '+lic['license_url']+'\n\n'+lic['modifications']+'.\n\nIf published on YouTube, this credit must be included in the video description. This delivery is on GitHub only. Foley is original synthesized sound design, not claimed as recorded field sound.\n')
if '--audio-only' in sys.argv:print('Attributed composed-track candidate and existing voice prepared; no listening approval claimed');sys.exit(0)
reports=sorted([json.loads(p.read_text()) for p in C.glob('render-*.json')],key=lambda r:r['from']);cursor=0;parts=[]
for r in reports:assert r['from']==cursor and not r['page_errors'];cursor=r['to'];parts.append(C/f'part-{r["from"]}-{r["to"]}.mp4')
assert cursor==m['total_frames'],(cursor,m['total_frames']);lst=C/'concat.txt';lst.write_text(''.join("file '"+str(p)+"'\n" for p in parts));out=C/'Extinct_Life_V6_Actual_3D_Motion_Development.mp4'
run(['-f','concat','-safe','0','-i',lst,'-i',C/'proof.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar',SR,'-metadata','comment',lic['required_credit']+' | '+lic['license_url'],'-t',f'{D:.9f}','-movflags','+faststart',out])
encoded=levels(out);assert abs(float(encoded['input_i'])+16)<1.1,encoded;assert float(encoded['input_tp'])<=-1.5,encoded
q=run(['-i',out,'-map','0:v:0','-progress','pipe:1','-nostats','-f','null','-']);decoded=int(re.findall(r'^frame=(\d+)',q.stdout,re.M)[-1]);assert decoded==m['total_frames'];assert '1920x1080' in q.stderr
report={'status':'Selected actual-3D development excerpt, not the full film','width':1920,'height':1080,'fps':30,'native_frames':decoded,'duration_seconds':D,'script_sha256':m['script_sha256'],'voice_speed_changed':False,'new_voice_generated':False,'generated_scene_images_used':False,'old_rendered_movie_used':False,'v4_geometry_and_style_baseline_reused':True,'new_motion':['stance-phase foot locking','leg joint continuity','articulated goose neck/head flight posture and retracted feet','one-way takeoff with surface rings','geometric branch contact','source-to-sample transport','successive deposition batches'],'composed_music':lic,'music_download_sha256':hashlib.sha256(mp3.read_bytes()).hexdigest(),'foley':'Original synthesized contacts/water/wing details; not recorded field audio','encoded_audio':encoded,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'full_decode':True,'full_film_complete':False,'human_full_watch_listen_claimed':False,'biological_accuracy_expert_validated':False,'owner_creative_approval':False}
(B/'QC.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
