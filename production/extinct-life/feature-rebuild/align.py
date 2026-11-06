"""Estimated phonetic timing from reference synthesis / MFCC DTW, not verified ASR.
The selected natural voice remains the film voice. eSpeak is an alignment guide only.
"""
from pathlib import Path
import ctypes as ct,json,re,wave,hashlib,subprocess
import imageio_ffmpeg
import numpy as np
import espeakng_loader,librosa
P=Path(__file__).resolve().parent;R=P.parents[2];C=R/'.cache/extinct-rebuild';A=C/'alignment';A.mkdir(exist_ok=True,parents=True)
lib=espeakng_loader.load_library()
class Id(ct.Union):_fields_=[('number',ct.c_int),('name',ct.c_char_p),('string',ct.c_char*8)]
class Event(ct.Structure):_fields_=[('type',ct.c_int),('unique',ct.c_uint),('text_position',ct.c_int),('length',ct.c_int),('audio_position',ct.c_int),('sample',ct.c_int),('user_data',ct.c_void_p),('id',Id)]
CB=ct.CFUNCTYPE(ct.c_int,ct.POINTER(ct.c_short),ct.c_int,ct.POINTER(Event));chunks=[];events=[]
@CB
def callback(samples,n,ev):
 if n and samples:chunks.append(np.ctypeslib.as_array(samples,shape=(n,)).copy())
 if ev:
  j=0
  while ev[j].type:
   if ev[j].type==1:events.append({'position':ev[j].text_position,'length':ev[j].length,'ms':ev[j].audio_position})
   j+=1
 return 0
lib.espeak_Initialize.argtypes=[ct.c_int,ct.c_int,ct.c_char_p,ct.c_int];lib.espeak_Initialize.restype=ct.c_int
rate=lib.espeak_Initialize(2,0,str(Path(espeakng_loader.get_data_path()).parent).encode(),0)
assert rate>0
lib.espeak_SetSynthCallback(callback);assert lib.espeak_SetVoiceByName(b'ur')==0,'Urdu guide voice unavailable'
lib.espeak_SetParameter(1,170,0)
lib.espeak_Synth.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint,ct.c_int,ct.c_uint,ct.c_uint,ct.POINTER(ct.c_uint),ct.c_void_p]
all_records=[]
for i,item in enumerate(json.loads((P/'narration-ur.json').read_text())):
 chunks.clear();events.clear();txt=item['text'];buf=ct.create_string_buffer(txt.encode());uid=ct.c_uint()
 assert lib.espeak_Synth(buf,len(buf),0,1,0,1,ct.byref(uid),None)==0
 lib.espeak_Synchronize();guide=np.concatenate(chunks).astype(np.float32)/32768
 voicefile=C/'voice'/f'{i+1:02d}.wav'
 if not voicefile.exists():
  voicefile.parent.mkdir(exist_ok=True,parents=True)
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'voice'/f'{i+1:02d}.flac'),'-c:a','pcm_s16le',str(voicefile)],check=True)
 with wave.open(str(voicefile)) as w:sr=w.getframerate();actual=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768
 # 20ms MFCC frames; normalize timbre so alignment follows phonetic structure.
 fs=16000;hop=320
 def features(y,source_sr):
  y=librosa.resample(y,orig_sr=source_sr,target_sr=fs)
  m=librosa.feature.mfcc(y=y,sr=fs,n_mfcc=16,n_fft=512,hop_length=hop)[1:]
  return (m-m.mean(axis=1,keepdims=True))/(m.std(axis=1,keepdims=True)+1e-5)
 ref=features(guide,rate);tar=features(actual,sr)
 cost,wp=librosa.sequence.dtw(X=ref,Y=tar,metric='cosine',global_constraints=True,band_rad=.35)
 wp=wp[::-1];ref_idx=np.arange(ref.shape[1]);mapping=np.zeros(ref.shape[1])
 for k in ref_idx:
  matches=wp[wp[:,0]==k,1];mapping[k]=np.median(matches) if len(matches) else np.nan
 valid=np.isfinite(mapping);mapping=np.interp(ref_idx,ref_idx[valid],mapping[valid])*.02
 records=[]
 for event in events:
  pos=max(0,event['position']-1);n=event['length'];word=txt[pos:pos+n]
  ti=float(np.interp(event['ms']/20,ref_idx,mapping));records.append(dict(text=word,char_start=pos,char_end=pos+n,start=round(ti,3)))
 for j,r in enumerate(records):r['end']=round(records[j+1]['start'] if j+1<len(records) else len(actual)/sr,3)
 result=dict(chapter=i,duration=len(actual)/sr,words=records,method='eSpeak Urdu reference / CMVN MFCC DTW; estimated, not ASR-verified word alignment',local_cost=float(cost[-1,-1]/len(wp)))
 (A/f'chapter-{i}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 all_records.append(result);print(i+1,'words',len(records),'seconds',len(actual)/sr,'cost',round(result['local_cost'],3),flush=True)
(P/'estimated-timings.json').write_text(json.dumps(all_records,ensure_ascii=False,indent=2)+'\n')
