#!/usr/bin/env python3
"""Review a 3-second Pexels driver window, using no user images.

The stock artist is not to be depicted in the film: derive pose only. GitHub
blob outputs are publicly accessible, hence only already-public stock previews
are relayed, not any user photo or private assets.
"""
import base64, hashlib, io, json, os, pathlib, tempfile
import cv2, requests
from PIL import Image,ImageDraw
URL='https://videos.pexels.com/video-files/32740423/13958018_1440_2560_30fps.mp4'
EXPECTED='fef029f40687ee924f0eaef6e3da932485441db4b9a3c992780121b12507e28d'
FPS=16;FRAMES=49;START=0.25
with tempfile.TemporaryDirectory() as td:
    p=pathlib.Path(td)/'src.mp4'; r=requests.get(URL,timeout=180);r.raise_for_status();p.write_bytes(r.content)
    if hashlib.sha256(r.content).hexdigest()!=EXPECTED: raise ValueError('Source changed')
    cap=cv2.VideoCapture(str(p));srcfps=cap.get(cv2.CAP_PROP_FPS);total=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print('source fps/frames',srcfps,total,flush=True)
    frames=[]
    for i in range(FRAMES):
        n=round((START+i/FPS)*srcfps);cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,arr=cap.read()
        if not ok:raise ValueError('Failed frame '+str(n))
        arr=cv2.flip(arr,1); im=Image.fromarray(cv2.cvtColor(arr,cv2.COLOR_BGR2RGB));im=im.resize((160,278),Image.Resampling.LANCZOS);frames.append(im)
    cap.release();headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'}
    for start in range(0,FRAMES,7):
        group=frames[start:start+7];out=Image.new('RGB',(160*len(group),300),'black');d=ImageDraw.Draw(out)
        for j,im in enumerate(group):out.paste(im,(160*j,0));d.text((160*j+3,281),str(start+j),fill='white')
        buf=io.BytesIO();out.save(buf,format='JPEG',quality=88)
        content=base64.b64encode(buf.getvalue()).decode();r=requests.post(f"https://api.github.com/repos/{os.environ['GH_REPO']}/git/blobs",json={'content':content,'encoding':'base64'},headers=headers,timeout=60);r.raise_for_status()
        print(f'::notice title=Window sheet::window-{start:03d}.jpg {r.json()["sha"]}',flush=True)
