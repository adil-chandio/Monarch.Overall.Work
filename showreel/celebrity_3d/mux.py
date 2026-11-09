"""Join rendered clips, add previously selected narration and original procedural score."""
import math,sys,subprocess,wave
from pathlib import Path
import numpy as np
import imageio_ffmpeg
base=Path(__file__).resolve().parent;chunks=Path(sys.argv[1]);out=Path(sys.argv[2]);ff=imageio_ffmpeg.get_ffmpeg_exe();sr=48000;duration=60
listfile=chunks/'list.txt'; listfile.write_text(''.join("file '"+str((chunks/f'{i:02d}.mp4').resolve())+"'\n" for i in range(12)))
picture=chunks/'picture.mp4';score=chunks/'score.wav'
subprocess.run([ff,'-y','-v','error','-f','concat','-safe','0','-i',str(listfile),'-c','copy',str(picture)],check=True)
t=np.arange(sr*duration,dtype=np.float32)/sr;a=np.zeros_like(t);notes=[110,138.59,164.81,207.65,123.47,146.83,185,220]
for i in range(120):
 pos=int(i*.5*sr);n=min(int(.9*sr),len(a)-pos)
 if n<=0:break
 u=np.arange(n,dtype=np.float32)/sr;env=np.minimum(u/.025,1)*np.exp(-u*3.8);f=notes[(i//8*4+i%4)%len(notes)];a[pos:pos+n]+=.022*env*(np.sin(2*np.pi*f*u)+.28*np.sin(2*np.pi*f*2*u))
for at in [0,8,16,24,42,51]:
 pos=int(at*sr);n=min(int(.45*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.028*np.sin(2*np.pi*(90*u-30*u*u))*np.exp(-9*u)
a*=np.minimum(1,np.minimum(t,(duration-t))).clip(0,1)
with wave.open(str(score),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes((a*32767).astype('<i2').tobytes())
inputs=[]
for k in range(1,8):inputs+=['-i',str(base.parent/'celebrity_pov'/'audio'/f'{k:02}.wav')]
offsets=[.35,8,16.2,24.15,33.6,41.85,51];filters=[f'[{i}:a]aresample=48000,adelay={int(at*1000)}:all=1[v{i}]' for i,at in enumerate(offsets,1)]
filters+=['[8:a]volume=0.55[m]',''.join(f'[v{i}]' for i in range(1,8))+'[m]amix=inputs=8:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]']
out.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([ff,'-y','-v','error','-i',str(picture),*inputs,'-i',str(score),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
print('output',out)
