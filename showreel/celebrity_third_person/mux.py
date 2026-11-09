"""Concatenate silent render shards and mux original narration and synthesized score."""
import sys,json,subprocess,tempfile,wave
from pathlib import Path
import imageio_ffmpeg
import numpy as np
P=Path(__file__).resolve().parent
clips=Path(sys.argv[1]);output=Path(sys.argv[2]);ff=imageio_ffmpeg.get_ffmpeg_exe();entries=json.loads((P/'script.json').read_text())
with tempfile.TemporaryDirectory() as td:
 tmp=Path(td);listing=tmp/'clips.txt';listing.write_text(''.join("file '%s'\n"% (clips/f'{i:02}.mp4').resolve() for i in range(12)));video=tmp/'video.mp4'
 subprocess.run([ff,'-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(video)],check=True)
 sr=48000;t=np.arange(sr*60,dtype=np.float32)/sr;a=np.zeros_like(t);rng=np.random.default_rng(1804)
 for freq in (55,82.41,110,138.59):a+=.003*np.sin(2*np.pi*freq*t)*(.7+.3*np.sin(2*np.pi*.045*t))
 for beat in np.arange(0,60,.75):
  pos=int(beat*sr);n=min(int(.18*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.005*np.sin(2*np.pi*87*u)*np.exp(-u*19)
 for at in (3.4,7,12.5,16,19,25.5,28.7,32.3,36,39.3,43,46.7,50.3,53.4):
  pos=int(at*sr);n=min(int(.22*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.003*rng.standard_normal(n)*np.exp(-u*16)
 a*=np.minimum(1,np.minimum(t,60-t)).clip(0,1);score=tmp/'score.wav'
 with wave.open(str(score),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes((a*32767).astype('<i2').tobytes())
 inputs=[]
 for i in range(len(entries)):inputs+=['-i',str(P/'audio'/f'{i+1:02}.wav')]
 filters=[f'[{i+1}:a]aresample=48000,adelay={int(e["start"]*1000)}:all=1[v{i+1}]' for i,e in enumerate(entries)]
 filters+=['[10:a]volume=0.8[m]',''.join(f'[v{i+1}]' for i in range(len(entries)))+'[m]amix=inputs=10:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]']
 subprocess.run([ff,'-y','-v','error','-i',str(video),*inputs,'-i',str(score),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(output)],check=True)
