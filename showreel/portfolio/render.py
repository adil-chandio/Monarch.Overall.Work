#!/usr/bin/env python3
"""MONARCH portfolio: original character and project clips, supplied reference soundtrack.

Run from repo root: python3 showreel/portfolio/render.py
The reference video is not needed; only the user-supplied soundtrack was retained.
"""
import math, subprocess, sys, time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0,'tools')
from ffbin import ffmpeg

cv2.setNumThreads(1)
W,H,FPS=1280,720,30
N=1097
ROOT=Path('showreel/portfolio')
TMP=Path('/tmp/monarch-portfolio');TMP.mkdir(exist_ok=True)
FONTS=Path('showreel/v2/assets')
ANTON=str(FONTS/'Anton-Regular.ttf'); BOLD=str(FONTS/'Poppins-Bold.ttf'); MED=str(FONTS/'Poppins-Medium.ttf')

def prepare_video(path, offset, seconds, w, h, name):
    out=TMP/(name+'.mp4')
    if out.exists():return str(out)
    subprocess.run([ffmpeg(),'-v','error','-y','-ss',str(offset),'-i',path,'-t',str(seconds),
       '-vf',f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS}',
       '-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(out)],check=True)
    return str(out)

def curve(v):
    x=max(0.,min(1.,v));return x*x*(3-2*x)
def anim(t,a,b):return curve((t-a)/(b-a))

def text_img(text,font,size,color,stretch=None):
    ft=ImageFont.truetype(font,size); bbox=ft.getbbox(text,stroke_width=0)
    im=Image.new('RGBA',(bbox[2]-bbox[0]+6,bbox[3]-bbox[1]+6),(0,0,0,0))
    ImageDraw.Draw(im).text((3-bbox[0],3-bbox[1]),text,font=ft,fill=(*color,255))
    if stretch: im=im.resize(stretch,Image.Resampling.LANCZOS)
    a=np.array(im);return cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2BGR),a[:,:,3]

def put(frame,img,mask,x,y,opacity=1.0):
    x,y=int(round(x)),int(round(y)); h,w=mask.shape
    x0=max(0,x);y0=max(0,y);x1=min(W,x+w);y1=min(H,y+h)
    if x1<=x0 or y1<=y0 or opacity<=0:return
    sx=x0-x;sy=y0-y
    a=(mask[sy:sy+y1-y0,sx:sx+x1-x0].astype(np.float32)*(opacity/255.0))[...,None]
    roi=frame[y0:y1,x0:x1]
    roi[:]=np.clip(roi*(1-a)+img[sy:sy+y1-y0,sx:sx+x1-x0]*a,0,255).astype(np.uint8)

def overlay_text(f,asset,x,y,alpha=1):put(f,asset[0],asset[1],x,y,alpha)

def prepare_character():
    src=cv2.imread(str(ROOT/'assets/character.png'))
    # Bright chroma green is deliberately very far from the subject's dark clothes.
    b,g,r=cv2.split(src.astype(np.float32)); excess=g-np.maximum(r,b)
    alpha=np.clip((35-excess)/28,0,1)
    alpha=cv2.GaussianBlur(alpha,(0,0),.8)
    # Remove green spill at the edge without tinting the character's mask.
    src[:,:,1]=np.minimum(src[:,:,1],np.maximum(src[:,:,0],src[:,:,2])+4)
    src=cv2.resize(src,(405,604),interpolation=cv2.INTER_AREA)
    alpha=cv2.resize(alpha,(405,604),interpolation=cv2.INTER_AREA)
    return src,np.uint8(np.clip(alpha*255,0,255))

def bg():
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    glow=np.exp(-(((xx-640)/475)**2+((yy-450)/340)**2)*1.5)
    lower=np.clip((yy/H)**1.7,0,1)
    out=np.empty((H,W,3),np.uint8)
    out[:,:,0]=np.clip(8+9*glow+3*lower,0,255)
    out[:,:,1]=np.clip(8+10*glow+4*lower,0,255)
    out[:,:,2]=np.clip(12+53*glow+29*lower,0,255)
    return out

def rounded_mask(w,h,r):
    m=np.zeros((h,w),np.uint8)
    cv2.rectangle(m,(r,0),(w-r-1,h-1),255,-1)
    cv2.rectangle(m,(0,r),(w-1,h-r-1),255,-1)
    for x in (r,w-r-1):
        for y in (r,h-r-1):cv2.circle(m,(x,y),r,255,-1,cv2.LINE_AA)
    return m

# Fast rounded cards with a soft, cached shadow. Clip images are fully ours.
MASKS={}
def card(f,im,x,y,alpha=1):
    h,w=im.shape[:2]
    key=(w,h)
    if key not in MASKS:
        m=rounded_mask(w,h,9); shadow=cv2.GaussianBlur(m,(0,0),5);MASKS[key]=(m,shadow)
    m,shadow=MASKS[key]
    black=np.zeros_like(im);put(f,black,shadow,x+3,y+5,alpha*.65)
    border=cv2.dilate(m,np.ones((3,3),np.uint8));border_im=np.full_like(im,(150,151,167))
    put(f,border_im,border,x,y,alpha*.65)
    put(f,im,m,x,y,alpha)

class Clip:
    def __init__(self,path):self.c=cv2.VideoCapture(path);self.last=None
    def next(self):
        ok,frame=self.c.read()
        if not ok:self.c.set(cv2.CAP_PROP_POS_FRAMES,0);ok,frame=self.c.read()
        if not ok:raise RuntimeError('Cannot decode project clip')
        return frame
    def reset(self):self.c.set(cv2.CAP_PROP_POS_FRAMES,0)

def main():
    print('Preparing project clips...',flush=True)
    vertical=[Clip(prepare_video('public/proof/lawone.web.mp4',5,12,170,330,'portrait-law')),
              Clip(prepare_video('public/proof/paanch.web.mp4',4,12,170,330,'portrait-paanch')),
              Clip(prepare_video('public/proof/intro.mp4',8,12,170,330,'portrait-intro'))]
    wide=[Clip(prepare_video('public/demo-preview.mp4',5,8,390,219,'wide-monarch')),
          Clip(prepare_video('public/demo/demo-short-30s.mp4',4,8,390,219,'wide-edit')),
          Clip(prepare_video('public/proof/lawone.web.mp4',7,8,390,219,'wide-law')),
          Clip(prepare_video('public/proof/paanch.web.mp4',6,8,390,219,'wide-paanch'))]
    back=bg();char,mask=prepare_character()
    title=text_img('PORTFOLIO',ANTON,280,(177,39,48),(1160,230))
    small=text_img("Hello i'm",MED,20,(238,222,218));brand=text_img('MONARCH',ANTON,62,(229,82,78))
    role=text_img('Video editor',BOLD,30,(238,226,224))
    labels=[text_img(x,MED,17,(219,200,198)) for x in ['*  Short-form editing','*  Documentary editing','*  Motion graphics','*  Creative storytelling']]
    pil=Image.new('RGBA',(500,58),(0,0,0,0));d=ImageDraw.Draw(pil)
    d.rounded_rectangle((0,0,499,57),radius=29,fill=(250,247,244,255),outline=(217,204,204,255),width=2)
    d.ellipse((20,17,43,40),outline=(177,39,48),width=3);d.line((40,38,49,47),fill=(177,39,48),width=3)
    sa=np.array(pil);search=(cv2.cvtColor(sa[:,:,:3],cv2.COLOR_RGB2BGR),sa[:,:,3])
    query='Showcasing my work...';queries=[text_img(query[:i],MED,16,(52,46,49)) if i else None for i in range(len(query)+1)]
    out=Path('public/demo/monarch-portfolio.mp4');out.parent.mkdir(parents=True,exist_ok=True)
    proc=subprocess.Popen([ffmpeg(),'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}',
        '-r',str(FPS),'-i','-','-i',str(ROOT/'assets/reference-sound.m4a'),'-map','0:v:0','-map','1:a:0',
        '-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','copy',
        '-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
    started=time.time()
    for i in range(N):
        t=i/FPS;f=back.copy()
        # Intro background remains as a faded hero through the portfolio, like reference.
        hero_dim=1-.73*anim(t,8.75,9.15)
        a=anim(t,.18,.90)*hero_dim
        overlay_text(f,title,60,-180+180*anim(t,.18,.90),a)
        ca=anim(t,.55,1.25)*hero_dim
        put(f,char,mask,438,720-604+(1-anim(t,.55,1.25))*330,ca)
        overlay_text(f,small,106,449,anim(t,1.3,1.7)*hero_dim)
        overlay_text(f,brand,106,475,anim(t,2.1,2.65)*hero_dim)
        overlay_text(f,role,900,448,anim(t,3.3,3.9)*hero_dim)
        for k,l in enumerate(labels):overlay_text(f,l,900,492+k*27,anim(t,4.2+k*.68,4.55+k*.68)*hero_dim)
        # Search prompt (9.4–11.9), with a typed reveal.
        if 9.3<t<12.05:
            a=anim(t,9.35,9.8)*(1-anim(t,11.65,12.0))
            overlay_text(f,search,390,329,a)
            n=int(len(query)*anim(t,10.05,11.35))
            if n:overlay_text(f,queries[n],452,348,a)
        # Three vertical previews.
        if 12.0<=t<18.05:
            for k,c in enumerate(vertical):
                p=c.next(); a=anim(t,12.05+k*.13,12.7+k*.13)*(1-anim(t,17.55,18.05))
                card(f,p,360+k*195,180+(1-anim(t,12.05+k*.13,12.7+k*.13))*420,a)
        if abs(t-25.0)<.02:
            for c in vertical:c.reset()
        # Four landscape project windows, arriving one after another.
        if 18.0<=t<25.3:
            for k,c in enumerate(wide):
                p=c.next(); a=anim(t,18.03+k*.13,18.55+k*.13)*(1-anim(t,24.85,25.28))
                x=235+(k%2)*420; y=100+(k//2)*245+(1-anim(t,18.03+k*.13,18.55+k*.13))*310
                card(f,p,x,y,a)
        # Three vertically framed edits, closing at the exact source runtime.
        if t>=25.15:
            for k,c in enumerate(vertical):
                p=c.next(); a=anim(t,25.15+k*.13,25.8+k*.13)
                card(f,p,360+k*195,180+(1-anim(t,25.15+k*.13,25.8+k*.13))*350,a)
        proc.stdin.write(f.tobytes())
        if i%150==0:print(f'frame {i}/{N} | {time.time()-started:.0f}s',flush=True)
    proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('FFmpeg failed')
    print(f'Wrote {out} ({time.time()-started:.1f}s)',flush=True)

if __name__=='__main__':main()
