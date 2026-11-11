"""Mix timed narration with original synthesized bed and transition/flash accents."""
import json,sys,subprocess,tempfile,wave
from pathlib import Path
import numpy as np,imageio_ffmpeg
P=Path(__file__).resolve().parent;video=Path(sys.argv[1]);out=Path(sys.argv[2]);cues=json.loads((P/'script.json').read_text());ff=imageio_ffmpeg.get_ffmpeg_exe()
with tempfile.TemporaryDirectory() as td:
 sr=48000;t=np.arange(sr*60,dtype=np.float32)/sr;a=np.zeros_like(t);rng=np.random.default_rng(23)
 # A restrained chordal bed, with harmonic motion and short transition accents.
 for base in (55,82.407,110,164.81):a+=.0035*np.sin(2*np.pi*base*t)*(.75+.25*np.sin(2*np.pi*.045*t))
 for i,at in enumerate(np.arange(0,60,.75)):
  pos=int(at*sr);n=min(int(.2*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.004*np.sin(2*np.pi*85*u)*np.exp(-u*20)
 for at in (7.2,13.5,19.7,27.6,36.4,44.3,52.2):
  pos=int(at*sr);n=int(.28*sr);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.003*rng.standard_normal(n)*np.exp(-u*12)
 # Brief synthetic shutter noises during the press event.
 for at in (20.3,21.2,22.9,24.6,26.2,38.8,40.7,45.1,46.4,48.8,50.2):
  pos=int(at*sr);n=int(.045*sr);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.011*rng.standard_normal(n)*np.exp(-u*80)
 a*=np.minimum(1,np.minimum(t,60-t)).clip(0,1);bed=Path(td)/'bed.wav'
 with wave.open(str(bed),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes((a*32767).astype('<i2').tobytes())
 inputs=[]
 for i in range(len(cues)):inputs+=['-i',str(P/'audio'/f'{i+1:02}.wav')]
 filters=[f'[{i+1}:a]aresample=48000,adelay={int(x["start"]*1000)}:all=1[v{i+1}]' for i,x in enumerate(cues)]
 filters+=['[9:a]volume=0.8[m]',''.join(f'[v{i+1}]' for i in range(len(cues)))+'[m]amix=inputs=9:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]']
 subprocess.run([ff,'-y','-v','error','-i',str(video),*inputs,'-i',str(bed),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
