"""Public thumbnail variants and limited, unverified video-model descriptions.

No video or audio is downloaded. YouTube still variants may be custom or
machine-selected; neither timing nor derivation from the film is assumed.
The model is not a substitute for independently watching the video.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'monarch_viral_audit'))
from forensic_followup import gemini_window, MODEL

ROOT=Path(__file__).resolve().parent


def windows(seconds):
    if seconds <= 60:return [(0,seconds,'full requested short duration')]
    mid=seconds//2
    return [(0,min(20,seconds),'opening 20s'),
            (max(0,mid-10),min(seconds,mid+10),'middle 20s'),
            (max(0,seconds-20),seconds,'ending 20s')]


def examine(task,key):
    vid, label, start, end, window=task
    result=gemini_window(key,vid,label+' / '+window,start,end,1)
    if result.get('http_status') in (429,503):
        first=result
        time.sleep(8)
        result=gemini_window(key,vid,label+' / '+window,start,end,1)
        result['earlier_attempt']={'http_status':first.get('http_status'),'status':first.get('status')}
    return result


def main():
    targets=json.loads((ROOT/'visual_targets.json').read_text())
    key=os.getenv('GEMINI_API_KEY')
    tasks=[];thumbnails=[];records=[]
    with tempfile.TemporaryDirectory(prefix='monarch-media-') as folder:
        tmp=Path(folder);(tmp/'stills').mkdir()
        for target in targets:
            vid=target['video_id'];seconds=target['duration_seconds'];label=target['label']
            if not (isinstance(vid,str) and len(vid)==11 and isinstance(seconds,(int,float)) and 0<seconds<43200):
                raise ValueError('Invalid target ID or duration')
            for kind in ('hqdefault','1','2','3'):
                url=f'https://i.ytimg.com/vi/{vid}/{kind}.jpg'
                r={'video_id':vid,'kind':kind,'url':url}
                try:
                    with urllib.request.urlopen(url,timeout=25) as res:
                        content=res.read(3*1024*1024+1);r['http_status']=res.status
                    if len(content)>3*1024*1024 or not content.startswith(b'\xff\xd8\xff'):
                        r['status']='non_jpeg_or_oversized'
                    else:
                        name=f'{vid}-{kind}.jpg';(tmp/'stills'/name).write_bytes(content)
                        r.update({'status':'ok','bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'filename':name})
                except urllib.error.HTTPError as exc:r.update({'status':'http_error','http_status':exc.code})
                except Exception as exc:r.update({'status':'error','error_type':type(exc).__name__})
                thumbnails.append(r)
            for start,end,window in windows(seconds):tasks.append((vid,label,start,end,window))
        # Limited independent windows, not the video as a continuous viewing.
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures={pool.submit(examine,t,key):t for t in tasks}
            for f in as_completed(futures):
                t=futures[f]
                try:result=f.result()
                except Exception as exc:result={'video_id':t[0],'status':'error','error_type':type(exc).__name__}
                records.append(result);print('model-window',t[0],t[4],result['status'],flush=True)
        archive=Path(os.environ['RUNNER_TEMP'])/'og-stills.zip'
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for f in sorted((tmp/'stills').glob('*.jpg')):z.write(f,'stills/'+f.name)
    data={'schema':1,'runner_reported_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
          'method':'Public thumbnail variants manually reviewed separately. Numbered variants are still images, not verified timed video frames. Gemini input: selected windows, one frame per second requested, potentially imperfect; answers are model-generated descriptions and do not establish continuous playback, exact cuts, audio or audience reactions.',
          'model':MODEL,'targets':targets,'thumbnails':thumbnails,'visual_descriptions':records,
          'stills_zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
    (Path(os.environ['RUNNER_TEMP'])/'og-media.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print('RESULT stills',sum(t['status']=='ok' for t in thumbnails),'/',len(thumbnails),
          'model windows',sum(r.get('status')=='ok' for r in records),'/',len(tasks),flush=True)


if __name__=='__main__':main()
