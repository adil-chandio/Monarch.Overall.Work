"""Natural-speed selected chapter 3 voice with a newly rendered 3D production sequence.
Run from the repository root, after render.mjs. Working media remains in .cache.
"""
from pathlib import Path
import hashlib,json,subprocess,wave
import numpy as np
import imageio_ffmpeg
ROOT=Path.cwd();BASE=ROOT/'production/extinct-life/feature-3d';CACHE=ROOT/'.cache/extinct-feature-3d/ch02';OUT=ROOT/'deliverables/Extinct_Life_3D_Chapter03_Production_1080p.mp4'
FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000;DURATION=52.1;N=round(SR*DURATION)

def run(args):
    return subprocess.run([FF,'-hide_banner','-y',*map(str,args)],check=True,capture_output=True,text=True)
def wav(path,a):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1 if a.ndim==1 else a.shape[1]);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())

voice=ROOT/'production/extinct-life/feature-rebuild/voice/03.flac'
run(['-i',voice,'-ar',SR,'-ac',1,CACHE/'voice-48.wav'])
with wave.open(str(CACHE/'voice-48.wav')) as w:
    v=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64)/32768
assert len(v)/SR==51.76, f'Unexpected selected narration duration: {len(v)/SR}'
v=np.pad(v,(0,N-len(v)))
t=np.arange(N)/SR;rng=np.random.default_rng(77421)
# Wide, low-level textured air. FFT colouring is deterministic, not licensed stock.
def air():
    a=rng.normal(size=N);spec=np.fft.rfft(a);freq=np.fft.rfftfreq(N,1/SR);spec*=np.exp(-freq/1700)/np.maximum(freq,38)**.65;spec[freq<42]=0
    y=np.fft.irfft(spec,n=N);return y/np.std(y)
fade=np.minimum(1,t/1.1)*np.minimum(1,(DURATION-t)/.8)
pad=np.zeros((N,2))
for j,f in enumerate([146.8324,220.,329.6276]):
    env=(.55+.15*np.sin(t*.35+j))*fade
    for channel in range(2):
        y=np.sin(2*np.pi*f*t+.016*np.sin(t*.6+j+channel*.1))+.19*np.sin(2*np.pi*f*2*t+j*.7)
        pad[:,channel]+=y*env*.0035
for ch in range(2):pad[:,ch]+=air()*.0024*fade*(.78+.14*np.sin(t*.31+ch))
# One restrained contact texture, motivated by settlement, not one whoosh per cut.
contact=np.maximum(t-21.8,0);gate=(t>=21.8)*np.exp(-contact*5)
for ch in range(2):
    grit=air()*.0024*gate
    resonant=(np.sin(2*np.pi*540*contact)+.45*np.sin(2*np.pi*805*contact))*np.exp(-contact*9)*.002*(t>=21.8)
    pad[:,ch]+=grit+resonant
breakage=np.maximum(t-6.07,0);pad+=((t>=6.07)*np.exp(-breakage*14)*np.sin(2*np.pi*690*breakage)*.0014)[:,None]
# 50-ms RMS voice envelope with a slow release; the bed survives sentence breaks.
window=2400;blocks=np.sqrt(np.mean(v[:N//window*window].reshape(-1,window)**2,axis=1));env=np.interp(np.arange(N),np.arange(len(blocks))*window,blocks)
a=np.zeros_like(env);last=0
for i in range(0,N,480):
    x=float(np.max(env[i:i+480]));last=max(x,last*.97);a[i:i+480]=last
duck=1-.48*np.clip(a/.05,0,1);pad*=duck[:,None]
mix=pad+v[:,None]*.89
wav(CACHE/'bed.wav',pad);wav(CACHE/'mix.wav',mix)
# Measured two-pass EBU normalization, preserving the voice's actual timing.
measure=run(['-i',CACHE/'mix.wav','-af','loudnorm=I=-16:TP=-1.8:LRA=9:print_format=json','-f','null','-'])
s=measure.stderr;j=json.loads(s[s.rfind('{'):s.rfind('}')+1]);norm='loudnorm=I=-16:TP=-1.8:LRA=9:linear=true:'+':'.join(f'{k}={j[v]}' for k,v in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')])
run(['-i',CACHE/'picture.mp4','-i',CACHE/'mix.wav','-map','0:v:0','-map','1:a:0','-vf','scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,eq=contrast=1.02:brightness=0.010:saturation=0.93:gamma=1.035','-c:v','libx264','-preset','fast','-crf','19','-threads','2','-pix_fmt','yuv420p','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-af',norm,'-c:a','aac','-b:a','192k','-ar',SR,'-t',DURATION,'-movflags','+faststart',OUT])
qc=run(['-i',OUT,'-af','loudnorm=I=-16:TP=-1.8:LRA=9:print_format=json','-f','null','-']);s=qc.stderr;levels=json.loads(s[s.rfind('{'):s.rfind('}')+1])
media=run(['-i',OUT,'-map','0:v:0','-f','null','-'])
assert '1920x1080' in media.stderr and '30 fps' in media.stderr
assert OUT.stat().st_size>1000000
report={'file':str(OUT.relative_to(ROOT)),'duration_seconds':DURATION,'frames_expected':1563,'resolution':[1920,1080],'fps':30,'shots':json.loads((BASE/'sequence.json').read_text())['chapter_02_shots'],'narration_seconds':51.76,'voice_time_stretched':False,'audio_measurement':levels,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'voice_file_sha256':hashlib.sha256(voice.read_bytes()).hexdigest(),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'creative_status':'Approved short-reference style; this is only chapter 3 of the full film, not the completed feature.','review_limit':'Native production previews inspected locally. Encoded chapter not yet visually reviewed; no verified full real-time audiovisual watch/listen.'}
(BASE/'render-reports').mkdir(exist_ok=True)
(BASE/'render-reports/chapter-03.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
