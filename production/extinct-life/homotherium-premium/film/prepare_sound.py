"""Deterministic original instrumental score and selective stereo editorial SFX."""
from pathlib import Path
import json,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import imageio_ffmpeg
R=Path(__file__).resolve().parents[4];B=R/'production/extinct-life/homotherium-premium';C=R/'.cache/homotherium-premium';C.mkdir(parents=True,exist_ok=True);ff=imageio_ffmpeg.get_ffmpeg_exe();sr=48000;N=46*sr;t=np.arange(N)/sr;rng=np.random.default_rng(8401)
subprocess.run([ff,'-y','-v','error','-i',str(R/'production/extinct-life/homotherium-short/source/narration.flac'),'-ar',str(sr),'-ac','1',str(C/'original-voice.wav')],check=True)
_,v=wavfile.read(C/'original-voice.wav');v=v.astype(float)/32768;voice=np.zeros(N)
for e in json.loads((B/'AUDIO-EDITS.json').read_text())['edits']:
 clip=v[round(e['source_start']*sr):round(e['source_end']*sr)].copy();f=round(.008*sr);clip[:f]*=np.linspace(0,1,f);clip[-f:]*=np.linspace(1,0,f);st=round(e['destination_start']*sr);voice[st:st+len(clip)]+=clip
# Remove rumble without brightening sibilance. No pitch/rate changes.
voice=sosfilt(butter(2,65,fs=sr,btype='highpass',output='sos'),voice)
def stereo_add(dst,y,st,pan=0,gain=1):
 st=round(st*sr);a=max(0,-st);b=min(len(y),N-st)
 if b<=a:return
 dst[st+a:st+b,0]+=y[a:b]*np.sqrt((1-pan)/2)*gain;dst[st+a:st+b,1]+=y[a:b]*np.sqrt((1+pan)/2)*gain
music=np.zeros((N,2));fx=np.zeros((N,2));beat=60/116;bar=beat*4
# D minor / B-flat / F / C. Soft, dark harmony; no borrowed recording, sample or melody.
chords=[[146.832,174.614,220],[116.541,146.832,174.614],[130.813,174.614,220],[130.813,164.814,195.998]]
for j,at in enumerate(np.arange(0,46,bar)):
 tt=np.arange(round((bar+.4)*sr))/sr;env=np.minimum(1,tt/.28)*np.minimum(1,np.maximum(0,(bar+.4-tt)/.45));growth=.58+.42*min(1,at/16)
 for k,freq in enumerate(chords[(j//2)%4]):
  y=(np.sin(2*np.pi*freq*tt+.003*np.sin(tt*3))+np.sin(2*np.pi*freq*1.0015*tt))*.5;stereo_add(music,y*env,at,(-.45,0,.45)[k],.006*growth)
 # Round bass pulse, deliberately low in level and filtered in the final mix.
 root=chords[(j//2)%4][0]/2;stereo_add(music,np.sin(2*np.pi*root*tt)*env,at,0,.009*growth)
# Sparse plucked motif and short beat transients. More restraint during the caveat section.
for j,at in enumerate(np.arange(.12,45.4,beat)):
 caution= .55 if 35<at<41 else 1
 if j%2==0:
  tt=np.arange(round(.23*sr))/sr;y=np.sin(2*np.pi*(51*tt+1.2*(1-np.exp(-tt*32))))*np.exp(-tt*25)*np.minimum(1,tt/.008);stereo_add(music,y,at,0,.035*caution)
 if j%4==2:
  tt=np.arange(round(.12*sr))/sr;y=sosfilt(butter(2,[2500,6200],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(tt)))*np.exp(-tt*58)*np.minimum(1,tt/.006);stereo_add(music,y,at,.3 if j%8==2 else -.3,.008*caution)
 if j%4==1:
  freq=chords[(int(at/bar)//2)%4][j//4%3]*2;tt=np.arange(round(.65*sr))/sr;env=np.exp(-tt*7)*np.minimum(1,tt/.012);y=(np.sin(2*np.pi*freq*tt)+.16*np.sin(2*np.pi*freq*2*tt))*env;stereo_add(music,y,at,-.45 if j%8==1 else .45,.007*caution);stereo_add(music,y,at+.19,.45 if j%8==1 else -.45,.0018*caution)
S=json.loads((B/'film/timeline.json').read_text());events=[]
# Seven soft transition sweeps plus four tactile detail taps, not a whoosh on every cut.
for index in [5,9,16,18,28,30,32]:
 at=S['scenes'][index]['start'];length=.28;tt=np.arange(round(length*sr))/sr;noise=sosfilt(butter(2,[700,4200],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(tt)));env=np.sin(np.pi*tt/length)**2;stereo_add(fx,noise*env,at-.13,-.3,.019);stereo_add(fx,noise*env,at-.11,.3,.012)
 tt2=np.arange(round(.22*sr))/sr;impact=np.sin(2*np.pi*(85*tt2-90*tt2**2))*np.exp(-tt2*28)*np.minimum(1,tt2/.008);stereo_add(fx,impact,at,0,.03);events.append({'at':at,'type':'soft stereo transition sweep + rounded low impact'})
for index in [2,20,22,23]:
 at=S['scenes'][index]['start'];tt=np.arange(round(.08*sr))/sr;y=(np.sin(2*np.pi*700*tt)+.2*np.sin(2*np.pi*1400*tt))*np.exp(-tt*85)*np.minimum(1,tt/.003);stereo_add(fx,y,at,.2 if index%2 else -.2,.012);events.append({'at':at,'type':'quiet tactile detail accent'})
# Lookahead speech ducking, smooth release. Voice is centered; music/SFX sit behind it.
step=240;small=np.sqrt(np.mean(voice[:N//step*step].reshape(-1,step)**2,axis=1));active=(small>.017).astype(float);future=np.maximum.reduce([np.roll(active,-j) for j in range(9)]);env=np.zeros(len(future));level=0
for i,x in enumerate(future):level+=(x-level)*(.55 if x>level else .035);env[i]=level
duck=1-.73*np.interp(t,np.arange(len(env))*.005,env);fade=np.minimum(1,t/.18)*np.minimum(1,np.maximum(0,(46-t)/.45));music*=duck[:,None]*fade[:,None];fx*=np.sqrt(duck[:,None])*fade[:,None]
music*=3.0;fx*=1.3
mix=voice[:,None]*.95+music+fx
for name,x in [('music',music),('sfx',fx),('premix',mix)]:wavfile.write(C/f'{name}.wav',sr,(np.clip(x,-.99,.99)*32767).astype(np.int16))
subprocess.run([ff,'-y','-v','error','-i',str(C/'premix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=6','-ar',str(sr),'-c:a','pcm_s16le',str(C/'mix.wav')],check=True)
q={'original_composition':True,'third_party_music_samples':False,'tempo_bpm':116,'harmony':'D minor / B-flat / F / C; soft pad, low bass, restrained plucked motif and rhythmic transients','voice_id':'voice-04','speech_rate_change':False,'voice_filter':'Second-order 65Hz highpass only before mix','ducking':'Approx 40ms lookahead, fast attenuation, smooth release; max music gain reduction 73 percent','sfx_events':sorted(events,key=lambda x:x['at']),'sfx_count':len(events),'source':'Original procedural synthesis, seed 8401; no actual recovery-site sounds','duration_seconds':46,'master_target_lufs':-16,'master_target_true_peak':-1.5,'continuous_human_style_listening_claimed':False};(B/'SOUND-DESIGN.json').write_text(json.dumps(q,indent=2)+'\n');print('Built original score and',len(events),'curated SFX events')
