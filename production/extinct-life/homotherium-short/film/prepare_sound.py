from pathlib import Path
import json,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly,butter,sosfilt
import imageio_ffmpeg
B=Path(__file__).resolve().parents[1];R=B.parents[2];C=R/'.cache/homotherium-short';C.mkdir(parents=True,exist_ok=True);FF=imageio_ffmpeg.get_ffmpeg_exe();sr=48000
subprocess.run([FF,'-y','-v','error','-i',str(B/'source/narration.flac'),'-ar',str(sr),'-ac','1',str(C/'voice-48.wav')],check=True);_,v=wavfile.read(C/'voice-48.wav');voice=v.astype(float)/32768
n=51*sr;t=np.arange(n)/sr;rng=np.random.default_rng(42);bed=np.zeros(n)
for f in [73.416,110,146.832,220]:bed+=np.sin(2*np.pi*f*t+.1*np.sin(t*.3))*.0018
bed*=np.sin(np.pi*t/51)**.8
x=np.column_stack([bed,bed*.96]);off=round(.25*sr);x[off:off+len(voice)]+=voice[:,None]*.95
for at in [.2,6.74,12.92,17.73,23.19,27.37,32.83,34.72,39.04,44.05]:
 st=round(at*sr);tt=np.arange(round(.4*sr))/sr;y=sosfilt(butter(2,[350,2200],fs=sr,btype='bandpass',output='sos'),rng.normal(0,1,len(tt)))*np.sin(np.pi*tt/.4)**2*.012;y+=np.sin(2*np.pi*(165*tt-70*tt**2))*np.exp(-tt*22)*.022;x[st:st+len(y)]+=y[:,None]*np.array([[.8,1.]])
wavfile.write(C/'premix.wav',sr,(np.clip(x,-.99,.99)*32767).astype(np.int16));subprocess.run([FF,'-y','-v','error','-i',str(C/'premix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=7','-ar',str(sr),'-c:a','pcm_s16le',str(C/'mix.wav')],check=True)
(B/'SOUND-DESIGN.json').write_text(json.dumps({'narration':'User-selected voice-04, original continuous 50.046-second performance, unsped; starts at 0.25s','background':'Original procedural quiet sine pad and synthetic transition accents; not field recordings or competitor audio','competitor_media_used':False,'third_party_music_used':False,'full_listening_certified':False},indent=2)+'\n')
