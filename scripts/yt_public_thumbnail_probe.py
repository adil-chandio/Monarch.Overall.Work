"""Check public, ordinary YouTube thumbnail URLs, not video playback or frames.
Numbered stills are merely low-resolution thumbnail candidates: timestamps and
whether they are extracted from the current footage are not verified.
"""
import hashlib,json,urllib.error,urllib.request
from pathlib import Path
out=Path('audit-output/youtube-thumbnails');out.mkdir(parents=True,exist_ok=True)
rows=[]
for vid in ['aWHX5Awe_TI','8wtQAI_ZZlQ','GHT3RyE9wGI']:
 for variant in ['1.jpg','2.jpg','3.jpg','hqdefault.jpg']:
    row={'video_id':vid,'variant':variant,'url':f'https://i.ytimg.com/vi/{vid}/{variant}'}
    try:
        req=urllib.request.Request(row['url'],headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=20) as r:
            data=r.read(1000000);row.update(http=r.status,content_type=r.headers.get('Content-Type'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        if row['content_type'].startswith('image/') and data[:2]==b'\xff\xd8':(out/f'{vid}-{variant}').write_bytes(data)
    except urllib.error.HTTPError as e:row.update(http=e.code)
    except Exception as e:row['error_type']=type(e).__name__
    rows.append(row)
Path('audit-output/yt-public-thumbnail-probe.json').write_text(json.dumps({'method':'Public YouTube numbered thumbnail URLs; not a video frame extraction or timestamp verification.', 'rows':rows},indent=2)+'\n')
print(json.dumps(rows,indent=2))
