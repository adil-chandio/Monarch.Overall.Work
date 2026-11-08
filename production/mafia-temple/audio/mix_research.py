#!/usr/bin/env python3
"""Build a research-only draft sound bed, not a finished soundtrack.

Uses externally supplied CC0 sources listed in SOURCES.md. The rough footstep
positions come from input mocap, not confirmed visual contacts; re-time them on
approved picture. Final creative and listening review is still required.

Usage: python mix_research.py --foley-dir /path/to/blocky-stories/assets/audio \
    --music /path/to/searching.ogg --output /tmp/temple-sound-research.wav
Requires numpy and imageio-ffmpeg. No external assets are committed by this tool.
"""
import argparse
from pathlib import Path
import subprocess
import wave

import imageio_ffmpeg
import numpy as np

RATE=48000
DURATION=20
N=RATE*DURATION


def decode(path, seconds=None):
    cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(path)]
    if seconds is not None: cmd += ['-t',str(seconds)]
    cmd += ['-f','f32le','-ac','2','-ar',str(RATE),'pipe:1']
    pcm=np.frombuffer(subprocess.check_output(cmd),np.float32)
    if not len(pcm) or len(pcm)%2: raise ValueError(f'Empty or invalid audio: {path}')
    return pcm.reshape(-1,2)


def automation(points):
    t=np.arange(N,dtype=np.float32)/RATE
    return np.interp(t,[p[0] for p in points],[p[1] for p in points]).astype(np.float32)[:,None]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--foley-dir',type=Path,required=True)
    p.add_argument('--music',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    music=decode(a.music,DURATION+1)
    if len(music)<N: raise ValueError('Music must be at least 20 seconds')
    mix=music[:N]*automation([(0,0),(0.6,.12),(3.5,.13),(4.3,.17),(9,.16),(13,.21),(16,.20),(19.3,.14),(20,0)])
    for name,env in [
      ('rain',[(0,0),(0.8,.18),(3.6,.18),(4.8,.04),(8.8,.04),(9.7,.02),(13,.02),(14,.08),(16,.03),(18.5,.02),(20,0)]),
      ('wind',[(0,0),(1,.05),(3.8,.07),(4.5,.13),(8.6,.13),(9.4,.17),(12.5,.17),(13.5,.07),(16,.05),(18.8,.04),(20,0)])]:
        data=decode(a.foley_dir/'amb'/f'{name}.wav',DURATION+1)
        if len(data)<N: raise ValueError(f'{name} is too short')
        mix+=data[:N]*automation(env)
    steps=[decode(a.foley_dir/'steps'/'stone'/f'stone_{i:02d}.wav') for i in range(1,7)]
    # Provisional contacts from the BVH guide. Do not assume diffusion output
    # is synchronized: inspect visible shoe-ground contact before final mix.
    walk=[0,16,36,54,76,92]
    run=[5,14,23,31,40,49,58,67]
    for j,frame in enumerate(walk+run):
        running=j>=len(walk)
        time=(13 if running else 0)+frame/24
        sample=steps[j%len(steps)]
        start=round(time*RATE);end=min(start+len(sample),N)
        gain=.15 if running else .12
        pan=-.15 if j%2 else .15
        stereo=np.array([1-pan,1+pan],dtype=np.float32)
        mix[start:end]+=gain*sample[:end-start]*stereo
    peak=float(np.max(np.abs(mix)))
    if peak>.85: mix*=.85/peak
    fade=int(.08*RATE);mix[:fade]*=np.linspace(0,1,fade)[:,None];mix[-fade:]*=np.linspace(1,0,fade)[:,None]
    pcm=np.clip(mix*32767,-32768,32767).astype('<i2')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(a.output),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
    print(f'20-second research-only mix at {RATE}Hz; peak {min(peak,.85):.3f}; footstep sync and listening QA required')


if __name__=='__main__': main()
