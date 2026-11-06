"""Assemble eight genuinely rendered chapters, natural speech, original score and motivated foley.
No image slideshow, speed change, reused proof footage, or unimplemented fallback.
"""
import hashlib,json,math,re,subprocess,wave,sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2];CACHE=ROOT/'.cache/extinct-v3';FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000
m=json.loads((BASE/'manifest.json').read_text());D=m['duration_seconds'];N=round(D*SR)
OUT=ROOT/'deliverables/Extinct_Life_v3_Full_English_1080p.mp4';OUT.parent.mkdir(exist_ok=True)
def run(args):return subprocess.run([FF,'-hide_banner','-y',*map(str,args)],capture_output=True,text=True,check=True)
def wav(path,a):
 with wave.open(str(path),'wb') as w:w.setnchannels(1 if a.ndim==1 else 2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
def levels(path):
 r=run(['-i',path,'-af','loudnorm=I=-16:TP=-1.8:LRA=9:print_format=json','-f','null','-']);s=r.stderr;return json.loads(s[s.rfind('{'):s.rfind('}')+1])
voice=np.zeros(N,np.float32)
for c in m['chapters']:
 p=CACHE/f'{c["id"]}-48.wav';run(['-loglevel','error','-i',ROOT/c['voice'],'-ar',SR,'-ac',1,p])
 with wave.open(str(p)) as w:v=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
 start=round(c['start_frame']/30*SR);end=start+len(v);assert end<=N;voice[start:end]=v
score=np.zeros((N,2),np.float32);rng=np.random.default_rng(20261106)
def note(time,duration,midi,level,kind='felt',pan=0):
 start=round(time*SR);n=min(round(duration*SR),N-start)
 if n<=0:return
 t=np.arange(n,dtype=np.float32)/SR;f=440*2**((midi-69)/12);y=np.zeros(n,np.float32)
 if kind=='felt':
  for k in range(1,7):y+=np.sin(2*np.pi*f*k*t+.06*k)*np.exp(-t*(.6+k*.12))/(k**2.4)
  env=np.minimum(1,t/.018)*np.minimum(1,(duration-t)/.25);y*=env
 else:
  vib=.003*np.sin(t*2*np.pi*4.8)
  for k in range(1,6):y+=np.sin(2*np.pi*f*k*t+vib*k)/(k**1.9)
  env=np.minimum(1,t/1.7)*np.minimum(1,(duration-t)/1.8);y*=env
 y*=level;left=math.sqrt((1-pan)/2);right=math.sqrt((1+pan)/2);score[start:start+n,0]+=y*left;score[start:start+n,1]+=y*right
 # A restrained stereo room tail, not a repeated transition whoosh.
 if kind=='felt':
  for delay,gain in [(.173,.12),(.319,.08),(.557,.055)]:
   p=start+round(delay*SR);nn=min(n,N-p)
   if nn>0:score[p:p+nn,0]+=y[:nn]*gain*right;score[p:p+nn,1]+=y[:nn]*gain*left
# Original slow-evolving D-minor/add9 harmonic bed with space beneath narration.
chords=[[50,57,64,65],[46,53,60,65],[48,55,62,64],[45,52,59,64],[50,57,62,69],[53,60,65,67],[48,55,62,69],[45,52,57,64]]
for bar,time in enumerate(np.arange(0,D,8.4)):
 chord=chords[(bar//2)%len(chords)];energy=.8+.2*math.sin(time*.012)
 for j,pitch in enumerate(chord):note(float(time),10.2,pitch,.0026*energy,'strings',(-.65+j*.43))
 note(float(time+.45),5.7,chord[0]-12,.004,'strings',0)
 if bar%2==0:
  melody=[chord[2]+12,chord[1]+12,chord[3]+12,chord[2]+12]
  for j,pitch in enumerate(melody):note(float(time+1.6+j*2.4),4.1,pitch,.0048,'felt',-.35+j*.23)
# Resolve towards an open D/F/A voicing under the final return, never a loud logo sting.
for pitch in [50,57,65,69]:note(D-9,9,pitch,.003,'strings',0)
foley=np.zeros((N,2),np.float32)
def texture_event(time,duration,kind,level,pan=0):
 start=round(time*SR);n=min(round(duration*SR),N-start)
 if n<=0:return
 t=np.arange(n,dtype=np.float32)/SR;noise=rng.normal(0,1,n).astype(np.float32);noise=np.convolve(noise,np.ones(21,np.float32)/21,'same')
 if kind=='foot':y=(noise*.5+np.sin(2*np.pi*(70*t-15*t*t))*.5)*np.exp(-t*17)
 elif kind=='drop':y=np.sin(2*np.pi*(650*t-180*t*t))*np.exp(-t*22)+noise*np.exp(-t*28)*.15
 elif kind=='grain':y=noise*np.exp(-t*5)
 else:y=noise*(.45+.2*np.sin(t*2.1))*np.minimum(1,t/.35)*np.minimum(1,(duration-t)/.35)
 y*=level;foley[start:start+n,0]+=y*math.sqrt((1-pan)/2);foley[start:start+n,1]+=y*math.sqrt((1+pan)/2)
for c in m['chapters']:
 off=c['start_frame']/30
 for row in c['sentences']:
  time=off+row['start'];dur=max(.2,row['end']-row['start']);world,mode=row['mode'].split('-')
  if world in ['river','coast']:texture_event(time,dur,'air',.007,-.2)
  if world=='habit':
   texture_event(time,dur,'air',.004,.3)
   if mode=='mastodon':
    for event in np.arange(time+.15,time+dur,1.8):texture_event(float(event),.4,'foot',.009,-.35)
  if mode in ['bind','break','hold']:texture_event(time+.35,.65,'grain',.009,.15)
  if mode=='extract':texture_event(time+.65,.22,'drop',.009,.2)
  if mode=='takeoff':
   for event in np.arange(time+.4,time+min(dur,3),.7):texture_event(float(event),.2,'grain',.008,.45)
# Slow envelope follower gently ducks score under actual speech, preserving natural pauses.
block=2400;padded=np.pad(voice,(0,(-len(voice))%block));rms=np.sqrt(np.mean(padded.reshape(-1,block)**2,axis=1));env=np.repeat(rms,block)[:N];duck=1-.52*np.clip(env/.06,0,1)
score*=duck[:,None];foley*=.85
fade=np.minimum(1,np.arange(N,dtype=np.float32)/SR/1.3)*np.minimum(1,(N-np.arange(N,dtype=np.float32))/SR/2)
score*=fade[:,None];foley*=fade[:,None]
mix=voice[:,None]*.87+score+foley
wav(CACHE/'score.wav',score);wav(CACHE/'foley.wav',foley);wav(CACHE/'mix.wav',mix)
# Optional English subtitles, sentence timing estimated from forced word alignment.
def stamp(t):
 ms=round(t*1000);h,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{mi:02}:{s:02},{ms:03}'
srt=[]
for c in m['chapters']:
 off=c['start_frame']/30
 for row in c['sentences']:
  srt.append(f'{len(srt)+1}\n{stamp(off+row["start"])} --> {stamp(off+row["end"])}\n{row["text"]}\n')
sub=BASE/'English-v3.srt';sub.write_text('\n'.join(srt))
if '--audio-only' in sys.argv:
 a=levels(CACHE/'mix.wav');(CACHE/'audio-qc.json').write_text(json.dumps(a,indent=2));print('Audio-only work check; NOT a finished film:',json.dumps(a));sys.exit(0)
# Strictly require all eight actual chapter encodes and their frame reports.
parts=[]
for c in m['chapters']:
 d=CACHE/f'ch{c["index"]:02}';p=d/'picture.mp4'
 if not p.exists():
  reports=sorted([json.loads(r.read_text()) for r in d.glob('render-*.json')],key=lambda r:r['first_frame']);assert reports
  cursor=0;segments=[]
  for r in reports:
   assert r['first_frame']==cursor and not r['page_errors'];cursor=r['last_frame_exclusive'];segments.append(d/f'part-{r["first_frame"]}-{r["last_frame_exclusive"]}.mp4')
  assert cursor==c['frames'];lst=d/'parts.txt';lst.write_text(''.join("file '"+str(v)+"'\n" for v in segments));run(['-f','concat','-safe','0','-i',lst,'-c','copy',p])
 else:
  r=json.loads((d/f'render-0-{c["frames"]}.json').read_text());assert r['native_frames']==c['frames'] and not r['page_errors']
 assert p.exists();parts.append(p)
concat=CACHE/'pictures.txt';concat.write_text(''.join("file '"+str(p)+"'\n" for p in parts))
a=levels(CACHE/'mix.wav');norm='loudnorm=I=-16:TP=-1.8:LRA=9:linear=true:'+':'.join(f'{k}={a[v]}' for k,v in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')])
run(['-f','concat','-safe','0','-i',concat,'-i',CACHE/'mix.wav','-i',sub,'-map','0:v:0','-map','1:a:0','-map','2:s:0','-c:v','copy','-af',norm,'-c:a','aac','-b:a','256k','-ar',SR,'-c:s','mov_text','-metadata:s:s:0','language=eng','-metadata','title=The Lost World Inside a Handful of Dirt','-t',f'{D:.9f}','-movflags','+faststart',OUT])
measured=levels(OUT)
decode=run(['-i',OUT,'-map','0:v:0','-vf','blackdetect=d=0.7:pix_th=0.035,freezedetect=n=-48dB:d=1.5','-progress','pipe:1','-nostats','-f','null','-']);frames=int(re.findall(r'^frame=(\d+)',decode.stdout,re.M)[-1]);assert frames==m['total_frames'],(frames,m['total_frames']);assert '1920x1080' in decode.stderr
assert abs(float(measured['input_i'])+16)<1.1;assert float(measured['input_tp'])<=-.8
report={'file':str(OUT.relative_to(ROOT)),'width':1920,'height':1080,'fps':30,'decoded_frames':frames,'duration_seconds':D,'voice_seconds':m['narration_seconds'],'voice_id':'voice-02','voice_time_stretched':False,'script_sha256':m['script_sha256'],'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'bytes':OUT.stat().st_size,'shots':len(m['shots']),'maximum_shot_seconds':max(s['duration_seconds'] for s in m['shots']),'audio_measurement':measured,'score':'original procedural felt-key/string-style score; not a recorded orchestra or licensed stock track','foley':'original synthesized wind/water texture, foot contacts, granular and liquid events','full_video_decode_checked':True,'detector_log':decode.stderr,'render_complete':True,'owner_quality_approval':False,'creative_status':'Full rendered production candidate; technical checks are not owner quality approval','av_review_limit':'Representative stills and deterministic motion states checked; not a verified human full-length watch/listen','youtube_upload':False}
(BASE/'QC.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='detector_log'},indent=2))
