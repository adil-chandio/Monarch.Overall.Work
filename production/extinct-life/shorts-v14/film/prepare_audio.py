"""Reconstruct selected narration from archived FLAC; no rerun or speed change."""
import pathlib,json,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
import imageio_ffmpeg
B=pathlib.Path('production/extinct-life/shorts-v14');C=pathlib.Path('.cache/shorts-v14');C.mkdir(parents=True,exist_ok=True);(C/'stills').mkdir(exist_ok=True)
s=json.loads((B/'film/timeline.json').read_text());sr=48000;x=np.zeros(round(s['duration']*sr));ff=imageio_ffmpeg.get_ffmpeg_exe()
for i,start in enumerate(s['voice_starts'],1):
 wav=C/f'voice-{i:02}.wav';subprocess.run([ff,'-y','-v','error','-i',str(B/'audio'/f'voice-{i:02}.flac'),'-c:a','pcm_s16le',str(wav)],check=True)
 rate,a=wavfile.read(wav);a=a.astype(float)/32768
 if a.ndim>1:a=a.mean(axis=1)
 a=resample_poly(a,sr,rate);offset=round(start*sr);x[offset:offset+len(a)]+=a
wavfile.write(C/'narration.wav',sr,(x*32767).astype(np.int16))
print('Selected narration reconstructed, natural speed,',s['duration'],'seconds')
