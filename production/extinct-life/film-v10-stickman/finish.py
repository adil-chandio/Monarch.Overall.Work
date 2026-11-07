"""61-second sentence-aligned stickman experiment; approved narration at original sample timing."""
import hashlib,json,re,subprocess,sys,urllib.request,wave
from pathlib import Path
import numpy as np
import imageio_ffmpeg
B=Path(__file__).resolve().parent;ROOT=B.parents[2];C=ROOT/'.cache/extinct-v10';C.mkdir(parents=True,exist_ok=True);FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000;N=61*SR
schedule=json.load(open(B/'schedule.json'));license=json.load(open(B.parent/'film-v9-full/MUSIC-LICENSE.json'))['tracks'][0]
def run(args):
 p=subprocess.run([FF,'-y','-hide_banner',*map(str,args)],capture_output=True,check=True);return p

def decode(p,seconds=61):
 return np.frombuffer(run(['-v','error','-i',p,'-t',seconds,'-ar',SR,'-ac','1','-f','f32le','pipe:1']).stdout,dtype='<f4').copy()
def wav(p,a):
 with wave.open(str(p),'wb')as w:w.setnchannels(1 if a.ndim==1 else a.shape[1]);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(a,-.999,.999)*32767).astype('<i2').tobytes())
def audio():
 v=np.zeros(N,np.float32);assets=[]
 for chapter in schedule['chapters']:
  p=ROOT/chapter['voice'];sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==chapter['voice_sha256'];a=decode(p);start=chapter['start_frame']*1600;length=min(len(a),N-start);v[start:start+length]=a[:length];assets.append({'voice_file':chapter['voice'],'sha256':sha,'timeline_start_sample':start,'samples_used':length})
 wav(C/'approved-voice.wav',v);fx=np.zeros(N,np.float32);rng=np.random.default_rng(104);events=[]
 for t,kind,level in [(3.9,'soft-reject',.004),(5.02,'soft-reject',.004),(6.15,'fragment-reveal',.006),(8.3,'lens-handle',.004),(26.6,'paper',.006),(33.5,'dry-leaf',.005),(38.2,'sediment',.005),(44.9,'felt-contact',.004),(53.8,'foot',.006),(54.7,'foot',.005),(55.6,'foot',.005),(56.5,'foot',.005),(58.0,'shed',.003)]:
  dur=.3 if kind in ['paper','dry-leaf','sediment','shed']else .17;n=int(dur*SR);u=np.arange(n)/SR;noise=np.convolve(rng.normal(0,1,n),np.ones(29)/29,mode='same');noise/=max(float(np.max(np.abs(noise))),1e-9);env=np.sin(np.pi*np.arange(n)/n)**2;sig=(noise*.65+np.sin(2*np.pi*(140 if kind=='foot'else 330)*u)*.25)*env*level;i=int(t*SR);fx[i:i+n]+=sig;events.append({'seconds':t,'kind':kind,'gain':level,'synthetic_not_field_recording':True})
 score=np.zeros(N,np.float32)
 if '--voice-only'not in sys.argv:
  p=C/'sb_hiraeth.mp3'
  if not p.exists():
   req=urllib.request.Request(license['official_download'],headers={'User-Agent':'Monarch attributed CC-BY animation production'})
   with urllib.request.urlopen(req,timeout=100)as r:p.write_bytes(r.read(35_000_000))
  a=decode(p);assert len(a)>=N;score=a[:N];rms=np.sqrt(np.mean(score*score));score*=.018/max(float(rms),1e-9);tt=np.arange(N)/SR;score*=np.minimum(1,tt/2)*np.minimum(1,(61-tt)/1.4);cs=np.concatenate(([0],np.cumsum(np.pad(v*v,(2400,2400)),dtype=np.float64)));voice_env=np.sqrt(np.maximum(0,(cs[4801:]-cs[:-4801])/4801));score*=1-.50*np.clip(voice_env/.04,0,1)
  music={'credit':license['required_credit'],'license_url':license['license_url'],'source_url':license['official_download'],'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'excerpt_seconds':[0,61]}
 else:music={'preview_only_no_music':True}
 mix=v+score+fx;peak=float(np.max(np.abs(mix)));gain=min(1,.93/max(peak,1e-9));mix*=gain;wav(C/'proof.wav',np.stack([mix,mix],axis=1));report={'seconds':61,'samples':N,'approved_voice_assets':assets,'voice_speed_changed':False,'chapter_gap_preserved':True,'no_time_stretch':True,'music':music,'synthetic_foley_events':events,'peak_before_safety_gain':peak,'global_safety_gain':gain,'continuous_human_listening_claimed':False};(B/'AUDIO-QC.json').write_text(json.dumps(report,indent=2)+'\n')

def assemble():
 parts=sorted(C.glob('part-*-*.mp4'),key=lambda p:int(p.stem.split('-')[1]));assert len(parts)==6,len(parts)
 (C/'concat.txt').write_text('\n'.join("file '"+str(p.resolve())+"'"for p in parts)+'\n');run(['-v','error','-f','concat','-safe','0','-i',C/'concat.txt','-c','copy',C/'picture.mp4'])
 out=C/'Extinct_Life_Stickman_3D_Experiment_English_1080p.mp4';run(['-v','error','-i',C/'picture.mp4','-i',C/'proof.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-af','loudnorm=I=-16:TP=-2.5:LRA=9','-c:a','aac','-b:a','192k','-ar',SR,'-t','61','-movflags','+faststart','-metadata','comment='+license['required_credit']+'; original conceptual 3D science illustration, not a recovered portrait.',out])
 p=run(['-v','error','-i',out,'-map','0:v:0','-an','-fps_mode','passthrough','-progress','pipe:1','-f','null','-']);counts=re.findall(r'frame=(\d+)',p.stdout.decode());assert int(counts[-1])==1830,counts[-1]
 probe=run(['-i',out,'-af','loudnorm=I=-16:TP=-2:LRA=9:print_format=json','-f','null','-']);text=probe.stderr.decode();levels=json.loads(text[text.rfind('{'):text.rfind('}')+1]);qc={'status':'rendered experiment, owner creative review pending','width':1920,'height':1080,'fps':30,'duration_seconds':61,'decoded_frames':1830,'full_video_decode':True,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'audio_levels':levels,'voice_speed_changed':False,'v9_unchanged':True,'generated_image_assets':0,'rendered_articulated_3d':True,'continuous_human_av_review_claimed':False};(B/'QC.json').write_text(json.dumps(qc,indent=2)+'\n')
if '--assemble' in sys.argv:assemble()
else:audio()
