"""Check first 3.5s of each take against assembled narration around its expected start.

Correlation checks timing and take identity, not correctness of the spoken text,
whole-take integrity, perceived sound quality, or voice authenticity.
"""
import json, subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from scipy.signal import correlate

B=Path(__file__).resolve().parent
T=json.loads((B/'take-timeline.json').read_text())
ff=imageio_ffmpeg.get_ffmpeg_exe();sr=8000

def decode(path,start,duration):
    return np.frombuffer(subprocess.run([ff,'-v','error','-ss',str(start),'-i',str(path),'-t',str(duration),'-ac','1','-ar',str(sr),'-f','f32le','-'],check=True,stdout=subprocess.PIPE).stdout,dtype='<f4')
results=[]
for take in T['sections']:
    reference=decode(B/(take['id']+'.mp3'),0,3.5)
    origin=max(0,take['start']-.5)
    assembled=decode(B/'Narration-Draft-v2.m4a',origin,4.5)
    corr=correlate(assembled,reference,mode='valid',method='fft')
    index=int(np.argmax(np.abs(corr))); offset=origin+index/sr-take['start']
    denominator=np.linalg.norm(assembled[index:index+len(reference)])*np.linalg.norm(reference)
    score=float(abs(corr[index])/denominator) if denominator else 0
    assert abs(offset)<.06 and score>.75, (take['id'],offset,score)
    results.append({'id':take['id'],'start_offset_seconds':round(offset,4),'correlation':round(score,4)})
report={'scope':'first 3.5 seconds of each chapter only; not a listening review','chapters':results}
(B/'SYNC-QC.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
