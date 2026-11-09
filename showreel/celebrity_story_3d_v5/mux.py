"""Original synthetic stereo score/effects, plus seven closely spaced voice cues.
No sampled music or real crowd sounds; all effects are procedural approximations.
"""
import json,sys,subprocess,tempfile,wave
from pathlib import Path
import numpy as np,imageio_ffmpeg
P=Path(__file__).resolve().parent;video=Path(sys.argv[1]);out=Path(sys.argv[2]);cues=json.loads((P/'script.json').read_text());ff=imageio_ffmpeg.get_ffmpeg_exe();sr=48000;N=sr*60;rng=np.random.default_rng(2904)
stereo=np.zeros((N,2),dtype=np.float32)
def add(mono,at,pan=0):
 i=max(0,int(at*sr));n=min(len(mono),N-i)
 if n>0:
  stereo[i:i+n,0]+=mono[:n]*np.sqrt((1-pan)/2);stereo[i:i+n,1]+=mono[:n]*np.sqrt((1+pan)/2)
def tone(freq,duration,kind='pad'):
 t=np.arange(int(duration*sr),dtype=np.float32)/sr
 if kind=='pad':
  env=np.minimum(1,t/1.0)*np.minimum(1,(duration-t)/1.2);return (.52*np.sin(2*np.pi*freq*t)+.23*np.sin(2*np.pi*freq*2*t)+.10*np.sin(2*np.pi*freq*3*t))*env
 env=np.exp(-3.1*t)*(1-np.exp(-45*t));return (np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*freq*2*t))*env
# A composed four-chord minor-key motif. Warm keyboard and soft pads evolve by act.
chords=[(146.83,174.61,220.0),(130.81,164.81,196.0),(116.54,146.83,174.61),(130.81,164.81,196.0)]
for bar in range(8):
 at=bar*7.5;d=min(8.8,60-at);energy=(.011,.013,.017,.020,.013,.016,.020,.012)[bar]
 for j,f in enumerate(chords[bar%4]):add(tone(f,d)*energy,at,(-.6,0,.6)[j])
for n in range(80):
 at=n*.75;bar=n//10;f=chords[bar%4][n%3]*(2 if n%4==3 else 1);amp=.011 if at<19.7 or at>=52.2 else .017
 add(tone(f,1.5,'keys')*amp,at, -.38 if n%2 else .38)
# Soft pulse for momentum, increasing at the public event, then settling.
for n in range(80):
 at=n*.75;t=np.arange(int(.18*sr),dtype=np.float32)/sr;env=np.exp(-t*22);amp=.012 if 16.44<=at<49.06 else .006
 add(np.sin(2*np.pi*(69*t-25*t*t))*env*amp,at,0)
# Broad low-passed noise: private room air vs more diffuse event ambience.
noise=rng.standard_normal(N).astype(np.float32);sm=np.convolve(noise,np.ones(240,dtype=np.float32)/240,mode='same')
t=np.arange(N,dtype=np.float32)/sr;env=np.where((t>=16.44)&(t<27.6)|((t>=36.45)&(t<49.06)),.045,.016);env*=np.minimum(1,t/.8)*np.minimum(1,(60-t)/1.2)
add(sm*env,0,-.25);add(np.roll(sm,827)*env,0,.3)
# Brief designed sounds. These are synthesized rather than real Foley recordings.
def click(at,pan=0,amp=.025,d=.06):
 t=np.arange(int(d*sr),dtype=np.float32)/sr;add((rng.standard_normal(len(t)).astype(np.float32)*np.exp(-t*70))*amp,at,pan)
def soft_step(at,pan):
 t=np.arange(int(.17*sr),dtype=np.float32)/sr;add((np.sin(2*np.pi*95*t)*np.exp(-t*24)+rng.standard_normal(len(t)).astype(np.float32)*np.exp(-t*55)*.2)*.016,at,pan)
# Phone buzz, ceramic tick, stride accents, flashes and gentle transition swells.
for at in (.25,.42):
 t=np.arange(int(.12*sr),dtype=np.float32)/sr;add(np.sin(2*np.pi*125*t)*np.exp(-t*16)*.018,at,-.3)
click(10.7,-.1,.008,.025)
for at in np.arange(13.7,16.3,.75):soft_step(at,-.22 if int(at*10)%2 else .22)
for at in np.arange(16.6,24.1,.75):soft_step(at,-.22 if int(at*10)%2 else .22)
for at in np.arange(46.2,49.0,.75):soft_step(at,-.22 if int(at*10)%2 else .22)
for k,at in enumerate((17.70,19.58,23.14,25.43,26.92,39.38,41.69,46.38,46.87,47.78,48.31)):click(at,(-.55,.55)[k%2],.022,.045)
for at in (9.85,16.44,24.4,36.45,46.08,49.06):
 d=.75;t=np.arange(int(d*sr),dtype=np.float32)/sr;sw=rng.standard_normal(len(t)).astype(np.float32);sw=np.convolve(sw,np.ones(40,dtype=np.float32)/40,mode='same');add(sw*np.sin(np.pi*t/d)**2*.012,at-.48,0)
stereo*=np.minimum(1,np.arange(N)/(sr*.35))[:,None].astype(np.float32)
with tempfile.TemporaryDirectory() as td:
 bed=Path(td)/'bed.wav'
 with wave.open(str(bed),'wb') as w:w.setparams((2,2,sr,0,'NONE','not compressed'));w.writeframes((np.clip(stereo,-1,1)*32767).astype('<i2').tobytes())
 inputs=[]
 for i in range(len(cues)):inputs+=['-i',str(P/'trimmed'/f'{i+1:02}.wav')]
 filters=[f'[{i+1}:a]aresample=48000,adelay={int(x["start"]*1000)}:all=1,volume=0.84[v{i+1}]' for i,x in enumerate(cues)]
 filters+=[f'[{len(cues)+1}:a]volume=1.0[m]',''.join(f'[v{i+1}]' for i in range(len(cues)))+f'[m]amix=inputs={len(cues)+1}:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-16:TP=-1.5:LRA=8,aresample=48000[a]']
 subprocess.run([ff,'-y','-v','error','-i',str(video),*inputs,'-i',str(bed),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)],check=True)
