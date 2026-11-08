#!/usr/bin/env python3
"""Original procedural score and effects for v7; no reference samples are used.

120 BPM, separate ducked bed and drums, 808, hat/snare, timed impacts and sweeps.
Writes 48kHz stereo PCM; mux and measure true peak after AAC encoding separately.
"""
import argparse
import math
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
DURATION = 698 / 30
rng = np.random.default_rng(7241)

def add(bus, x, t, gain=1., pan=0.):
    start = max(0, round(t * SR)); end = min(len(bus), start + len(x))
    if end <= start: return
    x = x[:end-start] * gain
    bus[start:end, 0] += x * math.sqrt((1-pan)/2)
    bus[start:end, 1] += x * math.sqrt((1+pan)/2)

def noise(n): return rng.standard_normal(n)

def kick():
    t = np.arange(int(.28*SR))/SR
    f = 32 + 100*np.exp(-t/.026)
    return .68*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/.085) + .12*noise(len(t))*np.exp(-t/.003)

def bass(f):
    t = np.arange(int(.50*SR))/SR
    hz = f + 9*np.exp(-t/.035)
    phase = 2*np.pi*np.cumsum(hz)/SR
    env = (1-np.exp(-t/.006))*np.exp(-t/.48)*np.minimum(1,(.5-t)/.035)
    return (.50*np.sin(phase) + .055*np.sin(phase*2))*env

def hat(velocity):
    t = np.arange(int(.07*SR))/SR
    z = signal.sosfilt(signal.butter(2, 6000, btype='highpass', fs=SR, output='sos'),noise(len(t)))
    return z*np.exp(-t/.013)*.12*velocity

def snare():
    t = np.arange(int(.20*SR))/SR
    n=signal.sosfilt(signal.butter(2,[1200,8000],btype='bandpass',fs=SR,output='sos'),noise(len(t)))
    return (.19*n + .14*np.sin(2*np.pi*190*t))*np.exp(-t/.065)

def sub():
    t = np.arange(int(.62*SR))/SR
    f=90*(18/90)**(np.minimum(t,.38)/.38)
    return .8*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/.32)*(1-np.exp(-t/.003))

def sweep(dur):
    n=int(dur*SR); t=np.arange(n)/SR
    z=noise(n)
    z=signal.sosfilt(signal.butter(2,[450,7000],btype='bandpass',fs=SR,output='sos'),z)
    return .18*z*np.sin(np.pi*t/dur)**2

def crash():
    t=np.arange(int(.8*SR))/SR
    z=signal.sosfilt(signal.butter(2,3000,btype='highpass',fs=SR,output='sos'),noise(len(t)))
    return .20*z*np.exp(-t/.22)

def build():
    n=round(DURATION*SR)
    music=np.zeros((n,2),dtype=np.float32); drums=np.zeros_like(music); effects=np.zeros_like(music)
    notes=[73.42,73.42,65.41,87.31,65.41,73.42,87.31,73.42,65.41,65.41,58.27,65.41]
    for k in range(math.ceil(DURATION/.5)):
        at=k*.5
        add(music,bass(notes[k%len(notes)]),at)
        add(drums,kick(),at)
        if k%2: add(drums,snare(),at,pan=.12)
        for j,v in enumerate([1,.5,.8,.55]):
            add(drums,hat(v),at+j*.125,pan=[-.25,.25,-.1,.1][j])
    t=np.arange(n)/SR
    pad=sum(a*np.sin(2*np.pi*f*t) for a,f in [(.030,146.83),(.023,174.61),(.022,220),(.012,261.63)])
    pad*=np.minimum(t/.8,1)
    add(music,pad,0,pan=-.3); add(music,pad,0,pan=.3)
    # Duck only the sustained bed, not the drum transient or impact.
    phase=t%.5
    music *= (1-.72*np.exp(-phase/.095))[:,None]
    for t0 in (11.75,12.0,20.75): add(effects,sub(),t0)
    for t0 in (.25,11.42,20.35): add(effects,sweep(.38),t0,pan=-.15)
    for t0 in (.5,11.67,20.75): add(effects,crash(),t0,pan=.15)
    y=music+drums+effects
    y*=np.minimum(1,(DURATION-t)/.4)[:,None]
    # Smoothly saturate, leaving codec headroom. dBTP is verified after mux.
    y=np.tanh(y*1.25)
    y*=10**(-2/20)/np.max(np.abs(y))
    return y

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
    y=build();wavfile.write(a.out,SR,(y*32767).astype(np.int16))
    print(f'{len(y)/SR:.3f}s peak {20*np.log10(np.abs(y).max()):.2f} dBFS rms {20*np.log10(np.sqrt(np.mean(y*y))):.2f} dBFS')
if __name__=='__main__':main()
