from pathlib import Path
import json,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import imageio_ffmpeg
R=Path(__file__).resolve().parents[4];B=R/'production/extinct-life/homotherium-fastcut';C=R/'.cache/homotherium-fastcut';C.mkdir(parents=True,exist_ok=True);src=R/'production/extinct-life/homotherium-short';ff=imageio_ffmpeg.get_ffmpeg_exe();sr=48000
subprocess.run([ff,'-y','-v','error','-i',str(src/'source/narration.flac'),'-ar',str(sr),'-ac','1',str(C/'voice.wav')],check=True)
_,v=wavfile.read(C/'voice.wav');v=v.astype(float)/32768
old=json.loads((src/'film/timeline.json').read_text())['captions'];cursor=.12;out=np.zeros(46*sr);cues=[];edits=[]
for c in old:
 a=max(0,c['start']-.25-.06);b=min(len(v)/sr,c['end']-.25+.07);clip=v[round(a*sr):round(b*sr)].copy();fade=round(.008*sr);clip[:fade]*=np.linspace(0,1,fade);clip[-fade:]*=np.linspace(1,0,fade);start=round(cursor*sr);out[start:start+len(clip)]+=clip
 cues.append({'start':round(cursor+(c['start']-.25-a),4),'end':round(cursor+(c['end']-.25-a),4),'lines':c['lines']});edits.append({'source_start':a,'source_end':b,'destination_start':cursor,'speed':1});cursor+=len(clip)/sr+.08
assert cursor<46
plans=[['fur','head','age-old'],['fur','head-tight'],['map-wide','map-pin'],['head'],['not-alive'],['skull','teeth'],['skull-top'],['head','identity'],['skull'],['teeth','age-young','head'],['compare'],['ear','compare-ear'],['neck'],['paw','paw-pair'],['fur','ear','paw','skull'],['partial'],['skull','uncertain'],['not-alive'],['head-tight'],['fur','head']]
shots=[]
for i,(c,types) in enumerate(zip(cues,plans)):
 start=0 if i==0 else round((cues[i-1]['end']+c['start'])/2*30)/30;end=round((c['end']+cues[i+1]['start'])/2*30)/30 if i<len(cues)-1 else 46
 bounds=[round((start+(end-start)*j/len(types))*30)/30 for j in range(len(types)+1)]
 for j,kind in enumerate(types):shots.append({'id':f'{len(shots)+1:02}-{kind}','kind':kind,'start':bounds[j],'end':bounds[j+1]})
# Minimal caption chunks keep visual attention on the evidence. Editorial timing, not certified ASR.
chunks=[]
for c in cues:
 groups=[]
 for line in c['lines']:
  words=line.split();n=(len(words)+4)//5;q,rem=divmod(len(words),n);offset=0
  for j in range(n):
   size=q+(j<rem);groups.append(words[offset:offset+size]);offset+=size
 weights=[len(' '.join(g)) for g in groups];total=sum(weights);position=c['start']
 for j,(g,w) in enumerate(zip(groups,weights)):
  end=c['end'] if j==len(groups)-1 else position+(c['end']-c['start'])*w/total
  chunks.append({'start':round(position,4),'end':round(end,4),'text':' '.join(g)});position=end
s={'width':1080,'height':1920,'fps':30,'duration':46,'total_frames':1380,'captions':chunks,'speech_phrases':cues,'scenes':shots,'base_commit':'d61ed05','no_3d':True,'no_voice_speedup':True,'alignment':'Speech-silence-based phrase trims; short caption chunk subdivisions are editorial, not forced alignment'};(B/'film/timeline.json').write_text(json.dumps(s,indent=2)+'\n');(B/'AUDIO-EDITS.json').write_text(json.dumps({'raw_voice':'../homotherium-short/source/narration.flac','edits':edits,'speech_speed':1,'end_of_voice':cursor-.08,'duration':46},indent=2)+'\n')
# Original tempo-led sound design, ducked under the narration; no animal sounds or fake field recordings.
t=np.arange(len(out))/sr;voice=out.copy();env=np.convolve((np.abs(voice[::240])>.018).astype(float),np.ones(41)/41,mode='same');duck=1-.72*np.interp(t,np.arange(len(env))*.005,env)
beat=60/116;bed=np.zeros(len(out));rng=np.random.default_rng(281)
for i,at in enumerate(np.arange(.12,45.5,beat)):
 st=round(at*sr);tt=np.arange(round(.22*sr))/sr
 if i%2==0:y=np.sin(2*np.pi*(57*tt+1.8*(1-np.exp(-tt*45))))*np.exp(-tt*24)*.027
 else:y=sosfilt(butter(2,[1800,6500],fs=sr,btype='bandpass',output='sos'),rng.normal(0,1,len(tt)))*np.exp(-tt*65)*.008
 bed[st:st+len(y)]+=y
for freq in [73.416,110,146.832]:bed+=np.sin(2*np.pi*freq*t)*.0013*np.sin(np.pi*t/46)
fx=np.zeros((len(out),2));sfx=[]
for i,shot in enumerate(shots):
 at=shot['start'];kind=shot['kind'];strength=.014 if i%3==0 else .005
 if kind in ['map-wide','skull','identity','age-young','partial','not-alive']:strength=.021
 st=round(at*sr);tt=np.arange(round(.16*sr))/sr;y=sosfilt(butter(2,[550,4200],fs=sr,btype='bandpass',output='sos'),rng.normal(0,1,len(tt)))*np.sin(np.pi*tt/.16)**2*strength;y+=np.sin(2*np.pi*(120*tt-220*tt**2))*np.exp(-tt*42)*strength
 fx[st:st+len(y),0]+=y*(.8 if i%2 else 1);fx[st:st+len(y),1]+=y*(1 if i%2 else .8);sfx.append({'at':at,'type':'short synthetic cut accent','amplitude':strength})
mix=voice[:,None]*.95+(bed*duck)[:,None]+fx*duck[:,None];mix*=np.minimum(1,(46-t)/.2)[:,None];wavfile.write(C/'premix.wav',sr,(np.clip(mix,-.99,.99)*32767).astype(np.int16));subprocess.run([ff,'-y','-v','error','-i',str(C/'premix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=7','-ar',str(sr),'-c:a','pcm_s16le',str(C/'mix.wav')],check=True)
(B/'SOUND-DESIGN.json').write_text(json.dumps({'original_synthetic_audio':True,'tempo_bpm':116,'narration_unchanged_speed':True,'method':'Shorten inter-phrase silence, do not accelerate speech. Quiet original rhythm, low pad and cut-linked accents dynamically ducked below voice.','sfx':sfx,'competitor_media_or_third_party_music_used':False},indent=2)+'\n')
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(B/'English.srt').write_text('\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(chunks,1))+'\n');print('duration',46,'shots',len(shots),'caption_chunks',len(chunks),'voice_end',cursor-.08)
