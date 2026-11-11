"""Sample the A/V sequence's voice+score alignment, not a listening review."""
import json,subprocess
from pathlib import Path
import numpy as np
from scipy.signal import correlate,correlation_lags
import imageio_ffmpeg
base=Path(__file__).resolve().parent;root=base.parents[4];ff=imageio_ffmpeg.get_ffmpeg_exe()
source=base.parent/'soundtrack-draft/Narration-Score-DRAFT.m4a';cut=root/'.cache/mammoth-edit/environment-354-384-incomplete-workprint.mp4'
# Compare decoded mono waveforms at three short locations; added foley and AAC
# can reduce correlation. This does not test all samples or intelligibility.
def grab(path,start,duration=3):
 b=subprocess.run([ff,'-v','error','-ss',str(start),'-i',str(path),'-t',str(duration),'-vn','-ac','1','-ar','8000','-f','f32le','-'],capture_output=True,check=True).stdout
 return np.frombuffer(b,dtype='<f4').astype(np.float64)
results=[]
original=grab(source,354,30);edited=grab(cut,0,30)
for t in (2.,14.,25.):
 start=int(t*8000);end=start+24000
 a=original[start:end].copy();b=edited[start:end].copy();a-=a.mean();b-=b.mean()
 corr=correlate(b,a,mode='full',method='fft');lags=correlation_lags(len(b),len(a),mode='full');valid=np.abs(lags)<=400
 k=np.argmax(corr[valid]);lag=lags[valid][k];r=corr[valid][k]/np.sqrt(np.dot(a,a)*np.dot(b,b));results.append({'sequence_time':t,'lag_ms':float(lag/8),'correlation':float(r)})
if any(abs(r['lag_ms'])>20 or r['correlation']<.90 for r in results):raise SystemExit('Sampled audio alignment failed: '+str(results))
print(json.dumps({'status':'sampled waveform alignment only; no human listening or full-length sync validation','samples':results},indent=2))
