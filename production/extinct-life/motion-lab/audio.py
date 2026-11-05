"""Original restrained stereo score/foley for the procedural engine test, not EP01 VO."""
from pathlib import Path
import numpy as np,wave,subprocess,imageio_ffmpeg,json,re
p=Path('.cache/extinct-motion-lab');p.mkdir(parents=True,exist_ok=True)
sr=48000;dur=18;n=sr*dur;t=np.arange(n)/sr;rng=np.random.default_rng(2026)
score=np.zeros((n,2));sfx=np.zeros_like(score)
def place(buf,x,start,pan=0,gain=1):
 a=round(start*sr);b=min(n,a+len(x));x=x[:b-a]*gain
 if b<=a:return
 buf[a:b,0]+=x*np.sqrt((1-pan)/2);buf[a:b,1]+=x*np.sqrt((1+pan)/2)
def tone(f,d):
 u=np.arange(round(d*sr))/sr
 env=(1-np.exp(-u/0.35))*np.exp(-u/3.5)*np.minimum(1,(d-u)/.6)
 return (np.sin(2*np.pi*f*u)+.23*np.sin(2*np.pi*2*f*u)+.08*np.sin(2*np.pi*3*f*u))*env
# Sparse Dm9 -> Bbmaj9 -> Dmaj9, independent layers with distinct entry/exit points.
for start,notes in [(0,[50,57,60,64]),(6,[46,53,57,60]),(12,[50,57,61,64])]:
 for j,m in enumerate(notes):place(score,tone(440*2**((m-69)/12),6),start,(j-1.5)/4,.025)
for start,m in [(1.2,74),(4.8,69),(7.8,77),(10.2,72),(13.2,73),(15.6,76)]:
 u=np.arange(int(sr*1.6))/sr;sig=np.sin(2*np.pi*(440*2**((m-69)/12))*u)*np.exp(-u*4)*np.minimum(1,u/.012)*np.minimum(1,(1.6-u)/.1)
 place(score,sig,start,np.sin(start)*.45,.025)
# Grain separation cues, not a whoosh on every editorial change.
for start in [3.7,4.05,4.35,4.7,5.2,5.7]:
 u=np.arange(int(sr*.16))/sr
 noise=rng.normal(0,1,len(u));noise=np.convolve(noise,np.ones(9)/9,mode='same');sig=noise*np.exp(-u*36)*np.minimum(1,u/.006)*np.minimum(1,(.16-u)/.02)
 place(sfx,sig,start,(rng.random()-.5)*1.2,.10)
for start,d in [(6.1,.9),(11.55,.45)]:
 u=np.arange(round(sr*d))/sr;noise=rng.normal(0,1,len(u));noise=np.convolve(noise,np.ones(17)/17,mode='same')
 place(sfx,noise*np.sin(np.pi*u/d)**2,start,-.15,.045)
for start,f in [(7,54),(12,65)]:
 u=np.arange(int(sr*.8))/sr;sig=np.sin(2*np.pi*(f*u+11*(1-np.exp(-u*8))))*np.exp(-u*6)*np.minimum(1,u/.01)
 place(sfx,sig,start,0,.12)
fade=np.minimum(1,(dur-t)/.8)
def save(name,a):
 a=a*fade[:,None]
 with wave.open(str(p/name),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(a,-.98,.98)*32767).astype('<i2').tobytes())
save('score.wav',score);save('foley.wav',sfx);save('mix.wav',score+sfx)
ff=imageio_ffmpeg.get_ffmpeg_exe();out=Path('deliverables/Extinct_Life_3D_Motion_Lab_NOT_EPISODE.mp4')
assert (p/'picture.mp4').exists(),'Complete render.mjs first'
subprocess.run([ff,'-y','-v','warning','-i',str(p/'picture.mp4'),'-i',str(p/'mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-16:TP=-2:LRA=7,aresample=48000,alimiter=limit=0.80:level=false','-c:a','aac','-b:a','256k','-movflags','+faststart','-shortest',str(out)],check=True)
r=subprocess.run([ff,'-hide_banner','-i',str(out),'-vn','-af','loudnorm=I=-16:TP=-2:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
m=re.search(r'\{\s*"input_i".*?\}',r.stderr,re.S);levels=json.loads(m.group())
video_check=subprocess.run([ff,'-v','error','-i',str(out),'-map','0:v:0','-an','-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True)
frames=[int(x) for x in re.findall(r'^frame=(\d+)$',video_check.stdout,re.M)]
assert frames and frames[-1]==1080,video_check.stdout
Path('production/extinct-life/motion-lab/QC.json').write_text(json.dumps({'file':str(out),'scope':'18-second procedural engine test; NOT finished EP01, representative opening or validated final art direction','fps':60,'resolution':[1920,1080],'frames':1080,'geometry':'Original procedural Three.js meshes, no acquired or generated image plates','audio':levels,'full_decode':'Full video decode succeeded: 1080 frames; audio measurement completed. Visual layout sampled, not a full audiovisual creative review'},indent=2))
print(out,levels)
