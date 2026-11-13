"""Temporary public-thumbnail review and five bounded unverified model windows.

No videos or captions are downloaded. Numbered variants are not timed frames.
The image bundle is encrypted before transfer and never committed. Model
outputs are explicitly observations from a model, not independently watched
footage, audio, scripts, audience responses, or reasons for success.
"""
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

IDS=[
    'oeBOgv9iU8s','cW8fVC4my1g','dpUUb32Q0KI','fMrGLuNe67U','BTTccTEjjyQ',
    'hopBzK6BOwo','BTUV6mq4VLQ','pXx5Q9OY68Q','uj2p4fJ4cB4','m8c_9InGxNM',
    'jh79YSCC8mM','RM9BeNFGuls','67H2LEar7vM','BFzpswX9iRg','wp_-bJ5uzLw',
    'KTku_oPAJpE','EYEC58EbeNI','DxyOpu84-EE','eB7FeQoYqFM','WwlLrKLdU5E',
]
MODEL_WINDOWS=[
    ('oeBOgv9iU8s','Hindi-labelled chocolate Short candidate',0,20),
    ('dpUUb32Q0KI','Hindi-labelled water-clock low-view candidate',0,14),
    ('hopBzK6BOwo','English Hoover Dam: opening window only',0,25),
    ('BTUV6mq4VLQ','Spanish Hoover Dam: opening window only',0,25),
    ('KTku_oPAJpE','Arabic-title underwater-pillar video: opening window only',0,25),
]


def model_task(task,key):
    vid,label,start,end=task
    result=gemini_window(key,vid,label,start,end,1)
    if result.get('http_status') in (429,503):
        first=result;time.sleep(8)
        result=gemini_window(key,vid,label,start,end,1)
        result['earlier_attempt']={'status':first.get('status'),'http_status':first.get('http_status')}
    return result


def main():
    root=Path(os.environ['RUNNER_TEMP']);thumbs=[];models=[]
    with tempfile.TemporaryDirectory(prefix='language-visual-') as td:
        tmp=Path(td)
        for vid in IDS:
            for kind in ('hqdefault','1','2','3'):
                url=f'https://i.ytimg.com/vi/{vid}/{kind}.jpg'
                r={'video_id':vid,'kind':kind,'url':url}
                try:
                    with urllib.request.urlopen(url,timeout=20) as response:
                        data=response.read(2*1024*1024+1);r['http_status']=response.status
                    if len(data)>2*1024*1024 or not data.startswith(b'\xff\xd8\xff'):
                        r['status']='non_jpeg_or_oversized'
                    else:
                        name=f'{vid}-{kind}.jpg';(tmp/name).write_bytes(data)
                        r.update({'status':'ok','filename':name,'bytes':len(data),
                                  'sha256':hashlib.sha256(data).hexdigest()})
                except urllib.error.HTTPError as exc:r.update({'status':'http_error','http_status':exc.code})
                except Exception as exc:r.update({'status':'error','error_type':type(exc).__name__})
                thumbs.append(r)
        key=os.environ.get('GEMINI_API_KEY')
        with ThreadPoolExecutor(max_workers=2) as pool:
            fs={pool.submit(model_task,t,key):t for t in MODEL_WINDOWS}
            for f in as_completed(fs):
                try:r=f.result()
                except Exception as exc:r={'video_id':fs[f][0],'status':'error','error_type':type(exc).__name__}
                models.append(r);print('model-window',r.get('video_id'),r['status'],flush=True)
        bundle=root/'language-stills.zip'
        with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for f in sorted(tmp.glob('*.jpg')):archive.write(f,'stills/'+f.name)
    output={'schema':1,'runner_reported_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'method':'Public thumbnail and numbered still variants are not verified video frames or timings. '
                     'Five bounded model windows are unverified model descriptions, not direct playback, '
                     'spoken language, exact editing, retention, audience response or proof of production rights.',
            'model':MODEL,'thumbnails':thumbs,'visual_descriptions':models,
            'stills_zip_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest()}
    (root/'language-visual.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('RESULT stills',sum(x['status']=='ok' for x in thumbs),'/',len(thumbs),
          'model windows',sum(x['status']=='ok' for x in models),'/',len(MODEL_WINDOWS),flush=True)

if __name__=='__main__':main()
