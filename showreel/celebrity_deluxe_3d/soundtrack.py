"""Mix the ten unchanged narration takes with licensed stereo music/foley.

Every recording is pinned in assets.json and credited in ASSET_CREDITS.txt.
The film-premiere walla is deliberately indistinct; it is not new dialogue.
"""
from __future__ import annotations
import math
import subprocess
import wave
from pathlib import Path
import numpy as np

SR = 48000
DURATION = 60


def decode(path: Path, ffmpeg: str) -> np.ndarray:
    raw = subprocess.check_output([ffmpeg, '-v','error','-i',str(path),'-f','f32le',
                                   '-ac','2','-ar',str(SR),'-'])
    result = np.frombuffer(raw, dtype='<f4').reshape(-1,2).copy()
    if not len(result) or not np.isfinite(result).all():
        raise ValueError('empty or invalid audio: '+str(path))
    return result


def fade_edges(x, seconds=.012):
    x = x.copy()
    count = min(round(seconds*SR), len(x)//2)
    if count:
        ramp = np.sin(np.linspace(0, math.pi/2, count, dtype=np.float32))**2
        x[:count] *= ramp[:,None]
        x[-count:] *= ramp[::-1,None]
    return x


def automation(points, n):
    times = np.arange(n, dtype=np.float32) / SR
    return np.interp(times, [p[0] for p in points], [p[1] for p in points]).astype(np.float32)


def add_event(mix, sound, at, gain, pan=0):
    sound = fade_edges(sound, .003)
    mono = sound.mean(axis=1)
    pan = max(-1., min(1., pan))
    left = math.sqrt(2)*math.cos((pan+1)*math.pi/4)
    right = math.sqrt(2)*math.sin((pan+1)*math.pi/4)
    start = max(0,round(at*SR)); count = min(len(mono),len(mix)-start)
    if count > 0:
        mix[start:start+count,0] += mono[:count] * gain * left
        mix[start:start+count,1] += mono[:count] * gain * right


def mix(cues, source_dir: Path, narration_dir: Path, output: Path, ffmpeg: str):
    n = SR*DURATION
    voice = np.zeros((n,2), dtype=np.float32)
    duck = np.zeros(n, dtype=np.float32)
    if len(cues) != 10:
        raise ValueError('the ten original narration cues are required')
    for i, cue in enumerate(cues, 1):
        clip = decode(narration_dir/f'{i:02d}.wav', ffmpeg)
        at = round(cue['start']*SR)
        count = min(len(clip), n-at)
        voice[at:at+count] += .82*clip[:count]
        # Ease the ambience down before speech, and release it after the cue.
        start, end = cue['start'], cue['start']+cue['duration']
        lo, hi = max(0,round((start-.16)*SR)), min(n,round((end+.28)*SR))
        ts = np.arange(lo,hi,dtype=np.float32)/SR
        local = np.minimum(np.clip((ts-(start-.16))/.16,0,1),
                           np.clip(((end+.28)-ts)/.28,0,1))
        duck[lo:hi] = np.maximum(duck[lo:hi],local)
    result = voice
    piano = decode(source_dir/'piano.mp3',ffmpeg)
    if len(piano) < n:
        raise ValueError('piano recording is shorter than the film')
    score_gain = automation([(0,0),(.65,.20),(58.2,.20),(60,0)],n)
    result += piano[:n] * (score_gain*(1-.25*duck))[:,None]
    del piano,score_gain

    traffic = decode(source_dir/'city-traffic.ogg',ffmpeg)
    if len(traffic) < n:
        raise ValueError('traffic ambience is shorter than the film')
    # Distant traffic is audible outside; much quieter behind the night glass.
    traffic_gain = automation([(0,0),(16.9,0),(18,.035),(22.8,.042),
                               (45.2,.042),(46.5,.005),(50.5,.005),
                               (52,.012),(58.5,.012),(60,0)],n)
    result += traffic[:n] * (traffic_gain*(1-.30*duck))[:,None]
    del traffic,traffic_gain

    crowd = decode(source_dir/'premiere-crowd.mp3',ffmpeg)
    # Its source file is already crossfaded for looping.
    crowd = np.tile(crowd, (math.ceil(n/len(crowd)),1))[:n]
    crowd_gain = automation([(0,0),(17.1,0),(18.6,.07),(22.7,.07),(24,.14),
                             (34.7,.12),(39.8,.085),(45.3,.065),(46.5,0),(60,0)],n)
    result += crowd * (crowd_gain*(1-.30*duck))[:,None]
    del crowd,crowd_gain,duck

    step = decode(source_dir/'step-concrete.wav',ffmpeg)
    # Contact phases match the procedural walk period; cues remain approximate.
    for j in range(9):
        add_event(result, step, 24.15+j*(math.pi/7), .17, (-.18 if j%2 else .18))
    step = decode(source_dir/'step-wood.wav',ffmpeg)
    for j in range(7):
        add_event(result, step, 52.615+j*(math.pi/5.5), .11, (-.12 if j%2 else .12))
    shutter = decode(source_dir/'shutter.mp3',ffmpeg)
    for j,at in enumerate((30.45,31.27,32.05,32.88,33.53,34.15)):
        add_event(result, shutter, at, .15, (-.4 if j%2 else .35))
    add_event(result, decode(source_dir/'door-close.wav',ffmpeg),48.8,.13,-.18)
    add_event(result, decode(source_dir/'cloth.wav',ffmpeg),2.9,.065,.20)

    peak = float(np.max(np.abs(result)))
    if peak > .94:
        result *= .94/peak
    pcm = (np.clip(result,-1,1)*32767).astype('<i2')
    output.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(output),'wb') as out:
        out.setnchannels(2); out.setsampwidth(2); out.setframerate(SR)
        out.writeframes(pcm.tobytes())
    print('stereo mix: raw peak',round(peak,4),'duration',len(result)/SR,flush=True)
