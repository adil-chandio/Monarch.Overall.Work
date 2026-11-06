"""Build measured chapter/shot timings and a quiet, original synthetic body soundtrack."""
from pathlib import Path
import json, wave, math, subprocess
import imageio_ffmpeg
import numpy as np
P=Path(__file__).resolve().parent; R=P.parents[2]; C=R/'.cache/extinct-feature'; SR=48000; FPS=30
narr=json.loads((P/'narration.json').read_text())
# Cut boundaries are editorial/paragraph-level, not word-aligned subtitles.
boards=[
 [('field','The far northern edge'),('map','A different Greenland'),('botany','Traces of vegetation'),('pollen','An older window'),('core','A second archive')],
 [('woodland','Life leaves traces'),('shedding','An invisible trail'),('transport','Into water and sediment'),('fragments','A mixed archive'),('transport','Not one afternoon')],
 [('fragments','Messages break apart'),('cold','Cold conditions'),('mineral','A mineral shelter'),('mineral-close','Protection, not perfection'),('core','Chemistry matters')],
 [('lab','Recover the fragments'),('reads','Read, then compare'),('reference','More than one possible relative'),('branch','Where identification stops'),('lab-check','Test the interpretation')],
 [('woodland','A community reappears'),('fauna','Different lives, different traces'),('mastodon','A mastodon lineage'),('botany','Not a modern postcard'),('woodland','A lost combination')],
 [('fauna','The scene is an interpretation'),('transport','Across space and time'),('missing','Not found does not mean absent'),('uncertain','Evidence / illustration'),('mastodon','Keep the distinction visible')],
 [('pollen','Different windows'),('triad','Evidence together'),('reference','Agreement and open questions'),('age','An approximate age'),('triad','A reconstruction with edges')],
 [('fragments','Not a resurrection'),('mineral-close','Surviving pieces'),('dissolve-world','A partly readable past'),('cold','What the ground kept'),('end','The animal is gone. The story isn’t.')]
]
chapters=[]; shots=[]; cursor=0; voices=[]
for i,item in enumerate(narr):
 f=C/'voice'/f'{i+1:02d}.wav'
 if not f.exists():
  f.parent.mkdir(parents=True,exist_ok=True)
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'narration'/f'{i+1:02d}.flac'),'-c:a','pcm_s16le',str(f)],check=True)
 with wave.open(str(f)) as w:
  assert w.getsampwidth()==2 and w.getnchannels()==1
  rate=w.getframerate(); data=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768
 dur=len(data)/rate; frames=math.ceil((dur+1.45)*FPS); d=frames/FPS
 chapters.append(dict(index=i,title=item['title'],start_frame=cursor,frames=frames,voice_start=.65,voice_duration=dur,source=str(f.relative_to(R))))
 voices.append((cursor/FPS+.65,rate,data))
 # Five independently staged takes per chapter, roughly 9–11 seconds each.
 weights=[0,.20,.40,.60,.80,1]
 for j,(kind,title) in enumerate(boards[i]):
  a=cursor+round(frames*weights[j]); b=cursor+round(frames*weights[j+1])
  shots.append(dict(index=len(shots),chapter=i,kind=kind,title=title,start_frame=a,end_frame=b,transition_frames=10 if shots else 12))
 cursor+=frames
plan=dict(title='The Lost World Inside a Handful of Dirt',fps=FPS,width=1920,height=1080,opening_seconds=45,body_frames=cursor,body_seconds=cursor/FPS,total_seconds=45+cursor/FPS,chapters=chapters,shots=shots,source_doi='10.1038/s41586-022-05453-y',timing_note='Measured chapter speech; editorial shot timing, not word alignment.')
assert 360<=plan['total_seconds']<=480,plan['total_seconds']
(P/'timeline.json').write_text(json.dumps(plan,indent=2)+'\n')
N=round(cursor/FPS*SR); t=np.arange(N,dtype=np.float32)/SR
# Original restrained pad: no third-party score and no claimed authentic animal/site sound.
score=np.zeros(N,dtype=np.float32)
chords=[[130.8128,155.5635,195.9977],[116.5409,146.8324,174.6141],[103.8262,130.8128,155.5635],[97.9989,130.8128,164.8138]]
for i,ch in enumerate(chapters):
 a=round(ch['start_frame']/FPS*SR); b=round((ch['start_frame']+ch['frames'])/FPS*SR); z=t[a:b]-a/SR; duration=(b-a)/SR
 envelope=np.minimum(1,z/2)*np.minimum(1,(duration-z)/2)
 for j,hz in enumerate(chords[i%4]):
  tone=np.sin(2*np.pi*hz*z+j*.3)+.2*np.sin(2*np.pi*hz*2*z+.4)
  score[a:b]+=tone.astype(np.float32)*envelope*.0045*(.85+.15*np.sin(z*.18+j))
# Low synthetic air, explicitly not field recording.
rng=np.random.default_rng(7441); air=rng.normal(0,.0007,N).astype(np.float32)
mono=score+air
for start,rate,data in voices:
 x=np.interp(np.arange(round(len(data)/rate*SR))/SR,np.arange(len(data))/rate,data).astype(np.float32)
 # Consistent voice RMS without hard compression; final loudness normalization is separate.
 rms=float(np.sqrt(np.mean(x*x))); x*=min(2.0,.115/max(rms,.001),.82/max(float(np.max(np.abs(x))),.001))
 a=round(start*SR); mono[a:a+len(x)]+=x[:max(0,min(len(x),N-a))]
# Purposeful quiet material contacts only in schematic lab/mineral shots; no whoosh spam.
for s in shots:
 if s['kind'] not in ['mineral','mineral-close','lab','reads']:continue
 for frac in [.3,.57]:
  a=round((s['start_frame']+(s['end_frame']-s['start_frame'])*frac)/FPS*SR); z=np.arange(4800)/SR
  cue=(rng.normal(0,1,len(z))*.5+np.sin(z*2*np.pi*360))*.006*np.exp(-z*65)
  mono[a:a+len(cue)]+=cue[:len(mono[a:a+len(cue)])]
assert np.max(np.abs(mono))<1, 'Unexpected clipping before normalization'
L=mono+score*.12; RR=mono-score*.12
pcm=(np.clip(np.stack([L,RR],1),-.999,.999)*32767).astype('<i2')
with wave.open(str(C/'body_mix.wav'),'wb') as w:w.setparams((2,2,SR,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
(C/'audio-build.json').write_text(json.dumps({'sample_rate':SR,'seconds':N/SR,'pre_normalization_peak':float(np.max(np.abs(pcm.astype(np.float32)/32768))),'voice_id':'voice-00','new_voice_clips':8,'score':'Original mathematical synthesis','ambience':'Synthetic air, not field audio'},indent=2))
print(json.dumps({'body_seconds':cursor/FPS,'total_seconds':plan['total_seconds'],'frames':cursor,'shots':len(shots)},indent=2))
