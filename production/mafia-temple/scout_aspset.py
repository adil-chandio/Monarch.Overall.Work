#!/usr/bin/env python3
"""CPU-only scout: download CC0 ASPset test archive, make small visual sheets.

No user photo or generated likeness is involved. Source videos never enter Git;
only temporary, low-resolution contact sheets are uploaded for two-day review.
This is candidate screening, not proof of consent, fit or production rights.
"""
import hashlib, json, pathlib, shutil, tarfile, tempfile, time
import requests
import cv2
from PIL import Image, ImageDraw

URL='https://archive.org/download/aspset510/aspset510_v1_test-videos.tar.gz'
EXPECTED_MD5='797eca0da0ac76746a8df7beaf8d2ab6'
EXPECTED_SIZE=1386554365
out=pathlib.Path('/tmp/driver-scout-output');out.mkdir(exist_ok=True)
base=pathlib.Path(tempfile.mkdtemp(prefix='aspset-scout-'))
archive=base/'test-videos.tar.gz'
hashmd5=hashlib.md5(); count=0
print('Downloading ASPset test video archive; no user image is involved',flush=True)
with requests.get(URL,stream=True,timeout=(30,180),headers={'User-Agent':'Monarch-research/1.0'}) as r:
    r.raise_for_status()
    with archive.open('wb') as f:
        for chunk in r.iter_content(4*1024*1024):
            if chunk:
                f.write(chunk);hashmd5.update(chunk);count+=len(chunk)
                if count>EXPECTED_SIZE: raise ValueError('Archive exceeds published size')
if count!=EXPECTED_SIZE or hashmd5.hexdigest()!=EXPECTED_MD5:
    raise ValueError(f'Archive differs from published metadata: bytes={count}, md5={hashmd5.hexdigest()}')
print('Archive checksum verified; scanning members',flush=True)
clips=[]
with tarfile.open(archive,'r:gz') as tf:
    members=[m for m in tf if m.isfile() and pathlib.PurePosixPath(m.name).suffix.lower() in ('.mp4','.avi','.mov','.mkv')]
    print('Video members:',len(members),flush=True)
    if not members: raise ValueError('No video members found')
    if len(members)>300: raise ValueError('Unexpectedly many videos')
    for idx,m in enumerate(members):
        target=base/'current-video'
        with tf.extractfile(m) as inp,target.open('wb') as dst: shutil.copyfileobj(inp,dst)
        cap=cv2.VideoCapture(str(target))
        n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
        w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if n<2 or not fps or not w or not h: raise ValueError('Cannot decode '+m.name)
        imgs=[]
        for fraction in (0.05,0.25,0.45,0.65,0.85):
            frame=min(n-1,round(fraction*(n-1)));cap.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,arr=cap.read()
            if not ok: raise ValueError('Cannot decode frame '+m.name)
            image=Image.fromarray(cv2.cvtColor(arr,cv2.COLOR_BGR2RGB));image.thumbnail((240,135));imgs.append(image.copy())
        cap.release();target.unlink()
        clips.append({'member':m.name,'frames':n,'fps':fps,'width':w,'height':h,'seconds':round(n/fps,3),'images':imgs})
        if idx%10==0: print('Inspected',idx+1,'/',len(members),flush=True)
for start in range(0,len(clips),8):
    batch=clips[start:start+8]; sheet=Image.new('RGB',(1200,len(batch)*160),'#111');d=ImageDraw.Draw(sheet)
    for row,clip in enumerate(batch):
        for j,im in enumerate(clip['images']):sheet.paste(im,(j*240,row*160))
        d.text((3,row*160+137),f"{start+row:03d} {clip['member']} {clip['seconds']}s {clip['fps']:.2f}fps",fill='white')
    sheet.save(out/f'clips-{start:03d}-{start+len(batch)-1:03d}.jpg',quality=86)
    print('Saved sheet',start,flush=True)
for c in clips: del c['images']
(out/'index.json').write_text(json.dumps({'archive':URL,'bytes':count,'md5':hashmd5.hexdigest(),'clips':clips,'note':'Dataset owner declares CC0. Visual candidate selection and personality/consent review remain necessary.'},indent=2))
print('SCOUT_COMPLETE',flush=True)
shutil.rmtree(base)
