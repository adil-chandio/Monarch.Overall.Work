"""Retain approved V15 voice/edit; add restrained cues for newly introduced visual events."""
from pathlib import Path
import json,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[4];C=ROOT/'.cache/shorts-v16';B=ROOT/'production/extinct-life/shorts-v16-evolving';sr,base=wavfile.read(ROOT/'.cache/shorts-v15/mix.wav');assert sr==48000
x=base.astype(np.float64)/32768;rng=np.random.default_rng(1604);events=[]
def add(start,duration,kind,level):
 t=np.arange(round(duration*sr))/sr
 if kind=='liquid detail':
  phase=2*np.pi*(800*t+1400*t*t);y=np.sin(phase)*np.exp(-t*35)*(1-np.exp(-t*250))
 else:
  y=sosfilt(butter(2,[180,1800 if kind=='river texture' else 1000],btype='bandpass',fs=sr,output='sos'),rng.normal(0,1,len(t)));y*=np.sin(np.pi*t/duration)**2
 off=round(start*sr);n=min(len(y),len(x)-off);x[off:off+n]+=y[:n,None]*level*np.array([[.8,1.]])
 events.append({'output_time':start,'duration':duration,'type':kind,'synthetic_illustration_not_field_recording':True,'linear_mix_level':level})
add(14.3*.87,.22,'liquid detail',.05)
add(28.94*.87,(34.35-28.94)*.87,'river texture',.06)
add(45.93*.87,43.5-45.93*.87,'canyon air',.045)
C.mkdir(exist_ok=True);wavfile.write(C/'enhanced-premix.wav',sr,(np.clip(x,-.98,.98)*32767).astype(np.int16))
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(C/'enhanced-premix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=7','-ar','48000','-c:a','pcm_s16le',str(C/'mix.wav')],check=True)
(B/'SOUND-DESIGN.json').write_text(json.dumps({'base':'Approved V15 mix; unchanged narration text, selected voice and 43.5-second tempo','new_tempo_change_from_v15':False,'copied_competitor_audio':False,'additional_original_synthetic_events':events,'limits':'Scheduled cues, not independently measured perceptual onsets; no independent listening approval','final_encoded_measurement_required':True},indent=2)+'\n')
