"""Mechanical take-start checks only; not intelligibility or listening review."""
import json,subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from scipy.signal import correlate
B=Path(__file__).resolve().parent;C=B.parent;T=json.loads((C/'full-script-v2/take-timeline.json').read_text());ff=imageio_ffmpeg.get_ffmpeg_exe();sr=8000

def decode(path,start,duration):
 return np.frombuffer(subprocess.run([ff,'-v','error','-ss',str(start),'-i',str(path),'-t',str(duration),'-ac','1','-ar',str(sr),'-f','f32le','-'],check=True,stdout=subprocess.PIPE).stdout,dtype='<f4')
results=[]
for take in T['sections']:
 reference=decode(C/'full-script-v2'/(take['id']+'.mp3'),0,3.5)
 origin=max(0,take['start']-.5);mix=decode(B/'Narration-Score-DRAFT.m4a',origin,4.5)
 corr=correlate(mix,reference,mode='valid',method='fft');idx=int(np.argmax(np.abs(corr)))
 offset=origin+idx/sr-take['start'];den=np.linalg.norm(mix[idx:idx+len(reference)])*np.linalg.norm(reference);score=float(abs(corr[idx])/den) if den else 0
 assert abs(offset)<.06 and score>.65,(take['id'],offset,score)
 results.append({'id':take['id'],'start_offset_seconds':round(offset,4),'correlation':round(score,4)})
report={'scope':'first 3.5 seconds per chapter only; no listening or full-take integrity review','chapters':results}
(B/'SYNC-QC.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
