#!/usr/bin/env python3
"""Screen stock candidates, no user likeness or source videos committed.

GitHub blobs on this public repo are not private. Relay only thumbnail sheets
and a provenance index for already-public source clips, never user assets.
An identifiable stock performer must not be depicted in a criminal context.
"""
import base64, hashlib, json, os, pathlib, tempfile
import cv2, requests
from PIL import Image,ImageDraw

urls={
 '8533913':'https://videos.pexels.com/video-files/8533913/8533913-uhd_2560_1440_25fps.mp4',
 '8533445':'https://videos.pexels.com/video-files/8533445/8533445-uhd_2560_1440_25fps.mp4',
 '4468823':'https://videos.pexels.com/video-files/4468823/4468823-uhd_2560_1440_24fps.mp4',
}
repo=os.environ['GH_REPO'];s=requests.Session();s.headers.update({'User-Agent':'Monarch-Motion-Research/1.0'})
token=os.environ['GH_TOKEN']; index={}
with tempfile.TemporaryDirectory() as td:
 for ident,url in urls.items():
    path=pathlib.Path(td)/f'{ident}.mp4'; h=hashlib.sha256(); size=0
    with s.get(url,stream=True,timeout=(30,120)) as response:
        response.raise_for_status()
        with path.open('wb') as f:
            for c in response.iter_content(1024*1024):
                if c:
                    size+=len(c)
                    if size>200_000_000: raise ValueError('Source too large')
                    h.update(c);f.write(c)
    cap=cv2.VideoCapture(str(path)); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
    w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if n<48 or not fps: raise ValueError('Source could not be decoded: '+ident)
    sheet=Image.new('RGB',(320*5,200*2),'#111');draw=ImageDraw.Draw(sheet)
    for i in range(10):
        frame=min(n-1,round(i*(n-1)/9));cap.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,arr=cap.read()
        if not ok: raise ValueError('Cannot decode '+ident)
        im=Image.fromarray(cv2.cvtColor(arr,cv2.COLOR_BGR2RGB));im.thumbnail((320,180));x=(i%5)*320;y=(i//5)*200;sheet.paste(im,(x,y));draw.text((x+3,y+181),f'{frame/fps:.2f} sec',fill='white')
    cap.release(); sheet_path=pathlib.Path(td)/f'clips-{ident}.jpg';sheet.save(sheet_path,quality=85)
    index[ident]={'url':url,'sha256':h.hexdigest(),'bytes':size,'fps':fps,'frames':n,'resolution':[w,height]}
    data=base64.b64encode(sheet_path.read_bytes()).decode()
    r=requests.post(f'https://api.github.com/repos/{repo}/git/blobs',json={'content':data,'encoding':'base64'},headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'},timeout=120);r.raise_for_status()
    print(f'::notice title=Stock sheet::{sheet_path.name} {r.json()["sha"]}',flush=True)
    path.unlink()
 p=pathlib.Path(td)/'index.json';p.write_text(json.dumps(index,indent=2));data=base64.b64encode(p.read_bytes()).decode()
 r=requests.post(f'https://api.github.com/repos/{repo}/git/blobs',json={'content':data,'encoding':'base64'},headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'},timeout=120);r.raise_for_status()
 print(f'::notice title=Stock index::stock-index.json {r.json()["sha"]}',flush=True)
