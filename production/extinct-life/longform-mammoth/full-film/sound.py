"""Create a new non-mechanical score, restrained effects, and narration mix.

No original opening drone, wind, sub pulse or industrial bed is reused. The
new accompaniment is sparse harmonic sine-based felt notes and slowly evolving
chords, with gentle pitched transition accents; there is no propeller-like
modulation. Generated narration is placed at its original speed.
"""
import json, subprocess, wave
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import imageio_ffmpeg

B=Path(__file__).resolve().parent;R=B.parents[3]; C=R/'.cache/longform-mammoth-full';C.mkdir(parents=True,exist_ok=True)
P=json.loads((B/'timeline.json').read_text());ff=imageio_ffmpeg.get_ffmpeg_exe();sr=48000
N=int(round(P['duration']*sr));voice=np.zeros(N,np.float32);music=np.zeros(N,np.float32);effects=np.zeros(N,np.float32)

def decode(src):
 out=subprocess.run([ff,'-v','error','-i',str(src),'-ar',str(sr),'-ac','1','-f','f32le','-'],capture_output=True,check=True).stdout
 return np.frombuffer(out,np.float32)

def place_voice(src,start):
 v=decode(src);i=round(start*sr)
 assert i+len(v)<=N,(src,len(v),N-i)
 voice[i:i+len(v)]=v

place_voice(B.parent/'opening-3d/source/narration.mp3',.55)
for c in P['chapters']:place_voice(B/'source'/f"{c['id']}.mp3",c['start'])
# Remove subsonic microphone/voice content without changing speed.
voice[:]=sosfilt(butter(2,75,fs=sr,btype='highpass',output='sos'),voice).astype(np.float32)

def put(dst, wave, at, gain=1.):
 i=max(0,round(at*sr));end=min(N,i+len(wave));dst[i:end]+=wave[:end-i]*gain

# D minor, Bb, F and C: slowly breathing harmonic changes with no tremolo,
# percussion, sub drone or filtered wind. Crossfades are deliberately long.
chords=[[146.83,174.61,220.0],[174.61,220.0,261.63],[130.81,164.81,196.0],[146.83,196.0,233.08]]
for n,at in enumerate(np.arange(0,P['duration'],18.0)):
 dur=min(23.0,P['duration']-at);tt=np.arange(round(dur*sr),dtype=np.float32)/sr
 attack=np.clip(tt/4,0,1);release=np.clip((dur-tt)/4,0,1);env=np.minimum(attack,release)
 y=np.zeros_like(tt)
 for f in chords[n%4]:
  # Integer harmonics only: no detuned oscillators or rapid beating.
  y += (np.sin(2*np.pi*f*tt) + .16*np.sin(2*np.pi*2*f*tt))*0.333
 put(music,y*env,at,.018)

# Restrained bell/piano notes, widely spaced, with a soft attack and a smooth
# decay. Never a steady 60 bpm pulse. Integer harmonics avoid mechanical beat.
melody=[440.,523.25,587.33,523.25,392.,440.,349.23,392.,440.,349.23,329.63,392.]
for n,at in enumerate(np.arange(3.5,P['duration']-2,5.7)):
 f=melody[n%len(melody)];dur=3.1;tt=np.arange(round(dur*sr),dtype=np.float32)/sr
 env=(1-np.exp(-tt*14))*np.exp(-tt*1.8)*np.minimum(1,(dur-tt)*4)
 y=(np.sin(2*np.pi*f*tt)+.18*np.sin(2*np.pi*2*f*tt)+.06*np.sin(2*np.pi*3*f*tt))*env
 put(music,y,at,.019)

# Sparse soft editorial cues at the chapter openings only. Avoid repetitive
# whooshes, rumble, metallic impacts and narrow high-frequency noise.
for n,c in enumerate(P['chapters']):
 at=c['start']-.22; tt=np.arange(int(sr*1.35),dtype=np.float32)/sr
 env=(1-np.exp(-tt*12))*np.exp(-tt*2.5)*np.minimum(1,(1.35-tt)*5)
 f=[329.63,392.,440.,523.25][n%4]
 y=(np.sin(2*np.pi*f*tt)+.15*np.sin(2*np.pi*f*2*tt))*env
 put(effects,y,at,.012)

# Voice-aware attenuation with smooth attack/release, in 10 ms frames.
hop=480;pad=(-N)%hop;v=np.pad(voice,(0,pad));rms=np.sqrt(np.mean(v.reshape(-1,hop)**2,axis=1))
activity=(rms>.009).astype(np.float32);env=np.zeros_like(activity);level=0.
for i,val in enumerate(activity):
 level+=(val-level)*(.24 if val>level else .025);env[i]=level
# Interpolate in chunks rather than allocating a huge time coordinate array.
for start in range(0,N,sr*20):
 end=min(N,start+sr*20);xs=np.arange(start,end,dtype=np.float32)/hop
 duck=1-.5*np.interp(xs,np.arange(len(env)),env).astype(np.float32)
 music[start:end]*=duck

fadein=np.linspace(0,1,sr,dtype=np.float32);music[:sr]*=fadein;effects[:sr]*=fadein
fadeout=np.linspace(1,0,2*sr,dtype=np.float32);music[-2*sr:]*=fadeout;effects[-2*sr:]*=fadeout
# Keep voice centred and give only the quiet music/accents a subtle stereo
# spread. A short delayed copy at low gain avoids detuned beating.
left=voice*.94 + music + effects
right=voice*.94 + music*.86 + effects*.82
shift=int(.023*sr)
right[shift:] += music[:-shift]*.14 + effects[:-shift]*.18
peak=max(float(np.max(np.abs(left))),float(np.max(np.abs(right))))
assert peak<1.0, f'premix exceeds full scale: {peak}'
stereo=np.empty((N,2),dtype=np.int16)
stereo[:,0]=(left*32767).astype(np.int16)
stereo[:,1]=(right*32767).astype(np.int16)
wavfile.write(C/'premix.wav',sr,stereo)
subprocess.run([ff,'-y','-v','error','-i',str(C/'premix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=6','-ar',str(sr),'-c:a','pcm_s16le',str(C/'mix.wav')],check=True)
(B/'SOUND-DESIGN.json').write_text(json.dumps({'duration':P['duration'],'voice':'voice-04, original speed','opening_old_score_reused':False,'wind_drone_or_machine_bed':False,'music':'Original soft harmonic chords and sparse felt-like bell melody, without sub pulses or detuned beating','effects':'Ten soft pitched chapter accents; no mechanical rumble or continuous wind','caption':'automatic forced alignment','master_target':'-16 LUFS, -1.5 dBTP','human_listening_review':False},indent=2)+'\n')
print('Audio mix complete',P['duration'],'seconds; premix peak',round(peak,4))
