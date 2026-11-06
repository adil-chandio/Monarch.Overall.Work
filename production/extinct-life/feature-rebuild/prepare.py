from pathlib import Path
import re,json,wave,math,subprocess
import numpy as np
import imageio_ffmpeg
from story import BOARDS
P=Path(__file__).resolve().parent;R=P.parents[2];C=R/'.cache/extinct-rebuild';C.mkdir(exist_ok=True);FPS=30;SR=48000
narr=json.loads((P/'narration-ur.json').read_text());timings=json.loads((P/'estimated-timings.json').read_text())
keywords={'birch':['birch'],'poplar':['poplar'],'conifer':['conifers'],'hare':['خرگوش'],'deer':['reindeer'],'goose':['geese','goose'],'mastodon':['mastodon'],'pollen':['pollen'],'mineral':['mineral','minerals'],'sequence':['sequence','sequences'],'library':['reference'],'vial':['نکالنا','contamination'],'frost':['سردی'],'dna':['dna'],'age':['بیس'],'fossil':['fossil','fossils'],'cell':['cells','cells'],'camera':['camera','footage'],'coast':['ساحل'],'genome':['genome'],'clock':['وقت'],'chemistry':['chemistry']}
shots=[];chapters=[];cursor=0;voice_data=[]
for ci,(n,align,board) in enumerate(zip(narr,timings,BOARDS)):
 text=n['text'];sentences=[m for m in re.finditer(r'[^۔؟]+[۔؟]?',text) if m.group().strip()];assert len(sentences)==len(board),(ci,len(sentences),len(board))
 voicefile=C/'voice'/f'{ci+1:02d}.wav'
 if not voicefile.exists():
  voicefile.parent.mkdir(exist_ok=True,parents=True)
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'voice'/f'{ci+1:02d}.flac'),'-c:a','pcm_s16le',str(voicefile)],check=True)
 with wave.open(str(voicefile)) as w:rate=w.getframerate();data=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768
 frames=math.ceil((len(data)/rate+.32)*FPS);duration=frames/FPS;voice_data.append((cursor/FPS+.12,rate,data));chapters.append(dict(index=ci,start_frame=cursor,frames=frames,title=n['chapter'],voice_seconds=len(data)/rate))
 words=align['words'];onsets=[]
 for sentence in sentences:
  start=next((w['start'] for w in words if w['char_end']>sentence.start()+len(sentence.group())-len(sentence.group().lstrip())),0)
  onsets.append(start+.12)
 onsets[0]=0;onsets.append(duration)
 for si,(m,definition) in enumerate(zip(sentences,board)):
  a,b=onsets[si:si+2];stages=definition.split('/');bounds=[a]
  for k,stage in enumerate(stages[1:],1):
   topic=stage.split(':')[0];expected=a+(b-a)*k/len(stages)
   possible=[w['start']+.12 for w in words if m.start()<=w['char_start']<m.end() and any(z in w['text'].lower() for z in keywords.get(topic,[]))]
   proposed=min(possible,key=lambda t:abs(t-expected)) if possible else expected
   lo=bounds[-1]+min(.45,(b-a)/len(stages)*.55);hi=b-(len(stages)-k)*min(.45,(b-a)/len(stages)*.55)
   bounds.append(max(lo,min(hi,proposed)))
  bounds.append(b)
  for k,stage in enumerate(stages):
   topic,action=stage.split(':');first=round(bounds[k]*FPS);end=round(bounds[k+1]*FPS)
   if end<=first:continue
   count=math.ceil((end-first)/78)
   for take in range(count):
    f=first+round((end-first)*take/count);e=first+round((end-first)*(take+1)/count)
    idx=len(shots);shots.append(dict(index=idx,chapter=ci,sentence=si,subject=topic,action=action,start_frame=cursor+f,end_frame=cursor+e,variant=idx,view=idx%7,phrase=m.group().strip(),char_start=m.start(),char_end=m.end(),cue_timing='estimated phonetic DTW; not ASR verified',sound=(action in ['tear','break','extract','bind','sample','takeoff','filter','scan','grow','fly','hop','read','protect','join','open','reveal'] and (idx%4==0 or action in ['tear','extract','takeoff'])),cut='match-action' if take else 'subject-cut'))
 cursor+=frames
# Curated noun anchors for the coat/size/behaviour clause: do not reuse the
# first 'Mastodon' timestamp for all three later spoken properties.
group=[s for s in shots if s['chapter']==4 and s['sentence']==3]
assert len(group)==5
words=timings[4]['words'];ch=chapters[4]
def anchor(word):return ch['start_frame']+round((next(w['start'] for w in words if w['text']==word)+.12)*FPS)
color,size,behaviour=[anchor(w) for w in ['رنگ','جسامت','رویہ']]
start,end=group[0]['start_frame'],group[-1]['end_frame']
points=[start,round((start+color)/2),color,size,behaviour,end]
for s,a,b,action in zip(group,points,points[1:],['reveal','reveal','coat','scale','behaviour']):s.update(start_frame=a,end_frame=b,action=action,curated_anchor=True)
# Frame coverage is exact, independently of timing-estimation quality.
assert shots[0]['start_frame']==0 and shots[-1]['end_frame']==cursor
for a,b in zip(shots,shots[1:]):assert a['end_frame']==b['start_frame'],(a,b)
assert max(s['end_frame']-s['start_frame'] for s in shots)<=90
plan=dict(fps=FPS,width=1920,height=1080,frames=cursor,seconds=cursor/FPS,chapters=chapters,shots=shots,opening_reused=False,timing_method='Estimated word/phrase timing: eSpeak reference + MFCC DTW against actual selected-voice audio. Not verified ASR or human word alignment.')
(P/'timeline.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
N=cursor*1600;t=np.arange(N,dtype=np.float32)/SR;voice=np.zeros(N,np.float32)
for start,rate,data in voice_data:
 x=np.interp(np.arange(round(len(data)/rate*SR))/SR,np.arange(len(data))/rate,data).astype(np.float32);x*=min(1.8,.12/max(.001,float(np.sqrt(np.mean(x*x)))),.78/max(.001,float(np.max(np.abs(x)))))
 a=round(start*SR);voice[a:a+len(x)]+=x
# Envelope-linked musical ducking; no copyrighted/stock music or authentic animal recordings.
window=2400;energy=np.convolve(np.abs(voice[::480]),np.ones(15)/15,'same');duck=np.interp(np.arange(N)/480,np.arange(len(energy)),np.clip(energy/.05,0,1));duck=(1-.65*duck).astype(np.float32)
score=np.zeros(N,np.float32)
chords=[[146.8324,174.6141,220],[130.8128,164.8138,195.9977],[116.5409,146.8324,174.6141],[110,146.8324,184.9972]]
for i,ch in enumerate(chapters):
 a=ch['start_frame']*1600;b=(ch['start_frame']+ch['frames'])*1600;z=t[a:b]-a/SR;dur=(b-a)/SR;env=np.minimum(1,z/.6)*np.minimum(1,(dur-z)/.8)
 for j,hz in enumerate(chords[i%4]):score[a:b]+=(np.sin(z*2*np.pi*hz+j*.3)+.18*np.sin(z*2*np.pi*hz*2))*.007*env
 score[a:b]+=np.sin(z*2*np.pi*chords[i%4][0]/4)*.007*np.exp(-((z%(60/88))*5))
# Sparse, original three-note mallet motif, with low-level interaural echo.
for ch in chapters:
 start=ch['start_frame']/30;end=(ch['start_frame']+ch['frames'])/30
 for base in np.arange(start+.3,end-1,60/88*16):
  for k,hz in enumerate([293.6648,349.2282,440.0]):
   a=round((base+k*.34)*SR);length=min(round(1.5*SR),N-a)
   if length<=0:continue
   z=np.arange(length,dtype=np.float32)/SR
   score[a:a+length]+=(np.sin(z*2*np.pi*hz)+.22*np.sin(z*2*np.pi*hz*3))*.003*np.exp(-z*4)
score*=duck
rng=np.random.default_rng(107);fx=np.zeros((N,2),np.float32)
for s in shots:
 if not s['sound']:continue
 a=round((s['start_frame']/30+.22)*SR);length=min(12000,N-a);z=np.arange(length)/SR
 noise=rng.normal(0,1,length);action=s['action']
 if action=='tear':
  envelope=np.exp(-z*12)*(0.4+0.6*np.sin(z*2*np.pi*39)**2);cue=np.diff(noise,prepend=0)*.009*envelope
 elif action in ['extract','sample']:
  cue=np.sin(2*np.pi*(1100*z-1800*z*z))*.022*np.exp(-z*28)+noise*.003*np.exp(-z*35)
 elif action in ['bind','protect','join']:
  cue=(np.sin(z*2*np.pi*620)+.35*np.sin(z*2*np.pi*1247))*.012*np.exp(-z*16)+noise*.002*np.exp(-z*40)
 elif action in ['fly','takeoff','grow']:
  smooth=np.convolve(noise,np.ones(7)/7,'same');cue=smooth*.025*np.exp(-z*10)*np.sin(z*2*np.pi*11)**2
 elif action in ['scan','read','filter','break']:
  cue=noise*.012*np.exp(-z*65)+np.sin(z*2*np.pi*540)*.011*np.exp(-z*42)
 else:
  cue=np.sin(2*np.pi*(150*z-180*z*z))*.022*np.exp(-z*27)+noise*.005*np.exp(-z*30)
 pan=.25+.5*((s['index']*13)%17)/17;fx[a:a+length,0]+=cue*np.sqrt(1-pan);fx[a:a+length,1]+=cue*np.sqrt(pan)
L=voice+score+fx[:,0];RR=voice+score*.96+fx[:,1];pcm=np.stack([L,RR],1);assert np.max(abs(pcm))<1
with wave.open(str(C/'mix.wav'),'wb') as w:w.setparams((2,2,SR,0,'NONE','not compressed'));w.writeframes((pcm*32767).astype('<i2').tobytes())
# Preserve temporary narration in compact editable lossless files.
D=P/'voice';D.mkdir(exist_ok=True)
for i in range(8):subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(C/'voice'/f'{i+1:02d}.wav'),'-c:a','flac',str(D/f'{i+1:02d}.flac')],check=True)
print(json.dumps(dict(seconds=plan['seconds'],shots=len(shots),max_shot_seconds=max((s['end_frame']-s['start_frame'])/30 for s in shots),subjects=len(set(s['subject'] for s in shots))),indent=2))
