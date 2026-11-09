"""Approximate, error-prone speech recognition for each minute; not a transcript verification."""
import argparse,concurrent.futures,json,subprocess,tempfile
from pathlib import Path
from pocketsphinx import AudioFile
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('out');p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--seconds',type=float,default=4037.717914);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
def segment(start):
 result={'start_seconds':start,'end_seconds':min(start+60,a.seconds)}
 with tempfile.TemporaryDirectory() as temp:
  wav=Path(temp)/'audio.wav'
  try:
   subprocess.run([a.ffmpeg,'-v','error','-ss',str(start),'-i',a.source,'-t',str(min(60,a.seconds-start)),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le','-y',str(wav)],check=True,timeout=60)
   result['approximate_asr']=' '.join(str(x) for x in AudioFile(audio_file=str(wav),samprate=16000))
  except Exception as e:result['error_type']=type(e).__name__;result['error_message']=str(e)[:200]
 return result
starts=list(range(0, max(0, __import__("math").ceil(a.seconds)), 60));results=[]
with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
 for item in pool.map(segment,starts):
  results.append(item);print('ASR minute',len(results),'/',len(starts),flush=True)
(out/'asr.json').write_text(json.dumps({'method':'PocketSphinx approximate local speech recognition; errors expected. Minute boundaries can split words. Not listened or verified; do not quote as verbatim.','segments':results},indent=2,ensure_ascii=False)+'\n')
