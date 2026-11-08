#!/usr/bin/env python3
"""MONARCH portfolio with seven enhanced reference adaptations in the showcase.

Repro: python3 showreel/portfolio/render_v4.py
"""
import math, subprocess, sys, time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, 'tools')
from ffbin import ffmpeg

cv2.setNumThreads(1)
S=1.5
W,H,FPS=1920,1080,30
N=1097
ROOT=Path('showreel/portfolio')
TMP=Path('/tmp/monarch-portfolio-v4'); TMP.mkdir(exist_ok=True)
FONTS=Path('showreel/v2/assets')
ANTON=str(FONTS/'Anton-Regular.ttf'); BOLD=str(FONTS/'Poppins-Bold.ttf'); MED=str(FONTS/'Poppins-Medium.ttf')

def px(v):return int(round(v*S))
def ease(v):
    v=max(0.,min(1.,v)); return v*v*(3.-2.*v)
def anim(t,a,b):return ease((t-a)/(b-a))
def outc(v):
    v=max(0.,min(1.,v));return 1-(1-v)**3

def text_img(text,font,size,color,stretch=None):
    ft=ImageFont.truetype(font,px(size)); box=ft.getbbox(text)
    im=Image.new('RGBA',(box[2]-box[0]+px(5),box[3]-box[1]+px(5)))
    ImageDraw.Draw(im).text((px(2)-box[0],px(2)-box[1]),text,font=ft,fill=(*color,255))
    if stretch: im=im.resize((px(stretch[0]),px(stretch[1])),Image.Resampling.LANCZOS)
    a=np.asarray(im);return cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2BGR),a[:,:,3]

def put(f,img,mask,x,y,alpha=1):
    x,y=px(x),px(y); h,w=mask.shape; x0=max(0,x);y0=max(0,y);x1=min(W,x+w);y1=min(H,y+h)
    if alpha<=0 or x0>=x1 or y0>=y1:return
    sx,sy=x0-x,y0-y
    a=mask[sy:sy+y1-y0,sx:sx+x1-x0].astype(np.float32)[...,None]*(alpha/255.)
    z=f[y0:y1,x0:x1]; z[:]=(z*(1-a)+img[sy:sy+y1-y0,sx:sx+x1-x0]*a).astype(np.uint8)

def text(f,asset,x,y,alpha=1):put(f,asset[0],asset[1],x,y,alpha)
def line(f,a,b,color,th=1):cv2.line(f,(px(a[0]),px(a[1])),(px(b[0]),px(b[1])),color,max(1,px(th)),cv2.LINE_AA)

def char_asset():
    src=cv2.imread(str(ROOT/'assets/character.png'))
    b,g,r=cv2.split(src.astype(np.float32));alpha=np.clip((35-(g-np.maximum(r,b)))/28,0,1)
    alpha=cv2.GaussianBlur(alpha,(0,0),.8)
    src[:,:,1]=np.minimum(src[:,:,1],np.maximum(src[:,:,0],src[:,:,2])+4)
    return (cv2.resize(src,(px(405),px(604)),interpolation=cv2.INTER_CUBIC),
            cv2.resize(np.uint8(alpha*255),(px(405),px(604)),interpolation=cv2.INTER_LINEAR))

def background():
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);xx/=S;yy/=S
    glow=np.exp(-(((xx-640)/420)**2+((yy-390)/350)**2)*1.7)
    lower=(yy/720)**1.8
    f=np.empty((H,W,3),np.uint8)
    f[:,:,0]=np.clip(8+8*glow+2*lower,0,255)
    f[:,:,1]=np.clip(8+9*glow+3*lower,0,255)
    f[:,:,2]=np.clip(12+53*glow+22*lower,0,255)
    # Precisely weighted graphic grid; not video reference material.
    for x in range(80,1280,80):line(f,(x,0),(x,720),(12,12,25))
    for y in range(80,720,80):line(f,(0,y),(1280,y),(12,12,25))
    return f

def prepare_video(path,offset,seconds,w,h,name):
    out=TMP/(name+'.mp4')
    if out.exists() and out.stat().st_size == 0: out.unlink()
    if not out.exists():
        subprocess.run([ffmpeg(),'-v','error','-y','-ss',str(offset),'-i',path,'-t',str(seconds),
         '-vf',f'scale={px(w)}:{px(h)}:force_original_aspect_ratio=decrease,pad={px(w)}:{px(h)}:(ow-iw)/2:(oh-ih)/2:color=0x111015,fps={FPS}',
         '-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(out)],check=True)
    return str(out)

class Clip:
    def __init__(self,path):self.cap=cv2.VideoCapture(path)
    def next(self):
        ok,frame=self.cap.read()
        if not ok:self.cap.set(cv2.CAP_PROP_POS_FRAMES,0);ok,frame=self.cap.read()
        if not ok:raise RuntimeError('Cannot read prepared clip')
        return frame

MASKS={}
def rounded_mask(w,h,r):
    key=(w,h,r)
    if key not in MASKS:
        im=np.zeros((h,w),np.uint8)
        cv2.rectangle(im,(r,0),(w-r-1,h-1),255,-1);cv2.rectangle(im,(0,r),(w-1,h-r-1),255,-1)
        for x in (r,w-r-1):
            for y in (r,h-r-1):cv2.circle(im,(x,y),r,255,-1,cv2.LINE_AA)
        MASKS[key]=im
    return MASKS[key]

def card(f,im,x,y,alpha=1,angle=0):
    h,w=im.shape[:2]; mask=rounded_mask(w,h,px(9))
    if abs(angle)>.01:
        mat=cv2.getRotationMatrix2D((w/2,h/2),angle,1.)
        im=cv2.warpAffine(im,mat,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        mask=cv2.warpAffine(mask,mat,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    # Local drop shadow + 1px rim keep bright and dark projects legible on the background.
    black=np.zeros_like(im);shadow=cv2.GaussianBlur(mask,(0,0),px(4))
    put(f,black,shadow,x+3,y+5,alpha*.7)
    border=cv2.dilate(mask,np.ones((3,3),np.uint8));rim=np.full_like(im,(140,140,165))
    put(f,rim,border,x,y,alpha*.65);put(f,im,mask,x,y,alpha)

def pill(w,h):
    im=Image.new('RGBA',(px(w),px(h)))
    d=ImageDraw.Draw(im);d.rounded_rectangle((1,1,px(w)-2,px(h)-2),radius=px(h/2),fill=(245,242,239,255),outline=(255,255,255,255),width=px(1))
    a=np.array(im);return cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2BGR),a[:,:,3]

def main():
    print('Preparing native-resolution project panels...',flush=True)
    videos=Path('public/demo')
    def panel(n,offset,seconds,w,h,name):
        return Clip(prepare_video(str(videos/f'monarch-reference-{n:02}-enhanced.mp4'),offset,seconds,w,h,name))
    # Every source retains its original aspect ratio; pad, do not crop.
    first=[panel(2,7.3,6,205,385,'first-02'),
           panel(4,3.2,6,205,385,'first-04'),
           panel(6,1.2,6,205,385,'first-06')]
    wide=[panel(1,2.3,7.1,400,225,'wide-01'),
          panel(3,2.2,7.1,400,225,'wide-03'),
          panel(5,4.2,7.1,400,225,'wide-05')]
    last=[panel(2,13.5,10.2,205,385,'last-02'),
          panel(7,7.5,10.2,205,385,'last-07'),
          panel(4,13.0,10.2,205,385,'last-04')]
    teaser=[panel(1,2.5,5.4,128,72,'teaser-01'),
            panel(3,2.5,5.4,128,72,'teaser-03')]
    back=background();char,cm=char_asset(); char_cache={}
    title=text_img('PORTFOLIO',ANTON,260,(174,34,43),(1160,205))
    hello=text_img('HELLO, WE ARE',MED,16,(207,184,182));brand=text_img('MONARCH',ANTON,64,(244,80,76))
    role=text_img('Video editor',BOLD,27,(245,236,233))
    service=[text_img(s,MED,16,(220,201,198)) for s in ['Short-form editing','Documentary editing','Motion graphics','Creative storytelling']]
    top_left=text_img('M / MONARCH STUDIO',BOLD,13,(227,205,202));top_right=text_img('SELECTED WORK  /  2026',MED,12,(177,147,147))
    eyebrow=text_img('CREATIVE DIRECTION   /   EDITING',MED,11,(175,148,146))
    number=[text_img(s,MED,13,(235,184,179)) for s in ['01  /  03','02  /  03','03  /  03']]
    stage=[text_img(s,ANTON,30,(248,227,220)) for s in ['VERTICAL STORIES','MOTION IN FRAME','MORE SELECTED WORK']]
    subt=[text_img(s,MED,13,(199,169,167)) for s in ['VIDEOS 02  /  04  /  06','VIDEOS 01  /  03  /  05','VIDEOS 02  /  07  /  04']]
    badge=[text_img(s,MED,11,(234,197,193)) for s in ['02  /  MOTION','04  /  STRATEGY','06  /  MONARCH OS','01  /  MONARCH STUDIO','03  /  CREATIVE PARTNER','05  /  IDEAS','02  /  CLARITY','07  /  THE VISION','04  /  MONARCH STUDIO']]
    wide_badge_back=[]
    for asset in badge[3:6]:
        hh,ww=asset[1].shape; ww+=px(8);hh+=px(4)
        wide_badge_back.append((np.zeros((hh,ww,3),np.uint8),rounded_mask(ww,hh,px(3))))
    endbrand=text_img('MONARCH',ANTON,104,(246,76,73));endline=text_img('STORIES MADE TO MOVE.',MED,16,(230,211,205))
    hook=text_img('MOVE.',ANTON,200,(246,76,73));hookline=text_img('STORIES MADE TO',MED,16,(230,211,205))
    search=pill(540,58);query='Showcasing our work...'; queries=[text_img(query[:i],MED,16,(45,39,42)) if i else None for i in range(len(query)+1)]
    # Accent marks, all driven by measured source-audio attacks.
    beats=[.70,1.35,2.05,3.,4.05,5.00,6.15,7.,8.15,9.05,12.,12.65,18.,18.6,25.1,25.85,35.3]
    target=Path('public/demo/monarch-portfolio-v4.mp4');target.parent.mkdir(parents=True,exist_ok=True)
    proc=subprocess.Popen([ffmpeg(),'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-i',str(ROOT/'assets/reference-sound.m4a'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','17',
        '-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(target)],stdin=subprocess.PIPE)
    started=time.time()
    for i in range(N):
        t=i/FPS; f=back.copy()
        # Fine animated streaks and motion cues live behind the character and type.
        for k in range(16):
            x=(58+k*91+int(t*(4+(k%3)*2)))%1280; y=120+(k*71)%515
            cv2.circle(f,(px(x),px(y)),max(1,px(.8)),(40,40,83),-1,cv2.LINE_AA)
        beat=max((math.exp(-(t-b)/.12) for b in beats if 0<=t-b<.7),default=0.)
        cx,cy=640,342
        for k,(rx,ry) in enumerate(((190,242),(215,264),(240,285))):
            cv2.ellipse(f,(px(cx),px(cy)),(px(rx),px(ry)),0,0,360,(22+k*3,22+k*3,54+int(beat*12)),max(1,px(.7)),cv2.LINE_AA)
        # A restrained traveling line punctuates each section transition behind content.
        for cut in (9.05,12.,18.,25.1,35.0):
            dt=t-cut
            if 0<=dt<.45:
                xx=-100+1500*outc(dt/.45)
                line(f,(xx-80,90),(xx+80,630),(28,32,120),2)
        text(f,top_left,48,28,.9);text(f,top_right,1025,28,.9)
        line(f,(48,62),(1232,62),(45,43,80))
        # Fully clear the intro before the showcase so stale copy cannot ghost behind panels.
        outro=anim(t,34.75,35.20)
        dim=(1-anim(t,8.72,9.2))*(1-outro)
        # A brief typography-first cold open, then the character and portfolio reveal.
        ha=anim(t,.05,.22)*(1-anim(t,.50,.68))
        text(f,hookline,470,190,ha)
        text(f,hook,430,218+(1-anim(t,.05,.32))*45,ha)
        title_y=82-130*(1-outc((t-.65)/.55))
        text(f,title,60+2*math.sin(t*.32),title_y,anim(t,.68,1.12)*dim)
        rise=outc((t-.62)/.85)
        # Layer-specific drift creates parallax without synthetic face movement.
        sway=3*math.sin(t*.45)
        # A continuous foreground push, with tiny beat impulses, makes the still
        # portrait feel dimensional without inventing facial animation.
        scale=1+.045*anim(t,1.0,8.5)+.004*beat
        size=(int(round(char.shape[1]*scale)),int(round(char.shape[0]*scale)))
        if size not in char_cache:
            char_cache[size]=(cv2.resize(char,size,interpolation=cv2.INTER_LINEAR),
                              cv2.resize(cm,size,interpolation=cv2.INTER_LINEAR))
        ch,am=char_cache[size];logical_w=size[0]/S;logical_h=size[1]/S
        cy0=720-logical_h+(1-rise)*300+2*math.sin(t*.4)
        put(f,ch,am,640-logical_w/2+sway,cy0,anim(t,.62,1.18)*dim)
        text(f,hello,78,422,anim(t,1.35,1.75)*dim)
        text(f,brand,78,446+(1-anim(t,2.00,2.40))*24,anim(t,2.00,2.40)*dim)
        if dim>.01:
            line(f,(80,532),(80+120*anim(t,2.55,2.95),532),
                 (int(54*dim),int(48*dim),int(184*dim)),1)
        text(f,eyebrow,79,546,anim(t,2.7,3.1)*dim)
        text(f,role,906,424,anim(t,3.45,3.95)*dim)
        for k,lab in enumerate(service):
            a=anim(t,4.05+k*.65,4.45+k*.65)*dim
            if a > 0:
                cv2.circle(f,(px(911),px(474+k*28)),px(2),
                           (int(75*a),int(75*a),int(160*a)), -1, cv2.LINE_AA)
            text(f,lab,924,464+k*28,a)
        # Two edited-film previews move in during the introduction, before the grid.
        if 3.8 <= t < 9.1:
            for k,c in enumerate(teaser):
                thumb=c.next();a=anim(t,3.8+k*.18,4.3+k*.18)*(1-anim(t,8.75,9.1))
                card(f,thumb,80+k*140,587+(1-anim(t,3.8+k*.18,4.3+k*.18))*30,a)
        # Search transition, retains the original soundtrack.
        if 9.2<=t<12.05:
            a=anim(t,9.25,9.7)*(1-anim(t,11.65,12.02))
            text(f,search,370,315+(1-anim(t,9.25,9.7))*24,a)
            cv2.circle(f,(px(400),px(344)),px(9),(65,62,75),px(2),cv2.LINE_AA)
            line(f,(407,351),(413,357),(65,62,75),2)
            n=int(len(query)*anim(t,10.0,11.35))
            if n:text(f,queries[n],430,337,a)
        # Sequential showcase headings are editorial graphics, never cover the panels.
        section=0 if 12.0<=t<18 else 1 if 18<=t<25.05 else 2 if 25.05<=t<35.05 else -1
        if section>=0:
            t0=[12.,18.,25.05][section];t1=[18.,25.05,35.05][section]
            a=anim(t,t0,t0+.5)*(1-anim(t,t1-.3,t1))
            if section == 1:
                # Header sits above the landscape grid, not underneath its top-left card.
                text(f,stage[section],60,70,a)
                text(f,number[section],405,76,a)
                text(f,subt[section],500,76,a)
            else:
                text(f,number[section],62,103,a); text(f,stage[section],60,128,a)
                text(f,subt[section],61,170,a)
        if 12<=t<18:
            for k,c in enumerate(first):
                im=c.next();start=12.08+k*.15;p=outc((t-start)/.65);a=anim(t,start,start+.4)*(1-anim(t,17.55,18))
                x=306+k*232 + (k-1)*3*math.sin(t*.65); y=169+(1-p)*360+3*math.sin(t*.5+k)
                card(f,im,x,y,a,[-1.3,0,1.3][k]);text(f,badge[k],x+2,572,a)
        if 18<=t<25.05:
            for k,c in enumerate(wide):
                im=c.next();start=18.03+k*.13;p=outc((t-start)/.55);a=anim(t,start,start+.4)*(1-anim(t,24.72,25.05))
                x=226+(k%2)*427 if k<2 else 440; y=104+(k//2)*243+(1-p)*240
                card(f,im,x,y,a)
                put(f,wide_badge_back[k][0],wide_badge_back[k][1],x+5,y+201,a*.72)
                text(f,badge[k+3],x+9,y+203,a)
        if 25.05<=t<35.25:
            for k,c in enumerate(last):
                im=c.next();start=25.15+k*.14;p=outc((t-start)/.65);a=anim(t,start,start+.4)*(1-anim(t,34.75,35.25))
                x=306+k*232+(k-1)*3*math.sin(t*.7);y=169+(1-p)*360+3*math.sin(t*.5+k)
                card(f,im,x,y,a,[-1.2,0,1.2][k]);text(f,badge[k+6],x+2,572,a)
        # A short branded closing resolves the story instead of cutting the montage off.
        if t>=34.75:
            a=anim(t,34.75,35.25)
            # A dedicated closing composition: no faded intro copy crossing the face.
            put(f,ch,am,800,cy0,a)
            text(f,endbrand,156,278+(1-a)*35,a)
            text(f,endline,161,416,a)
            line(f,(162,451),(162+220*a,451),
                 (int(56*a),int(50*a),int(194*a)),1)
        # Timeline / section metadata, a small and consistent lower-edge visual anchor.
        line(f,(48,678),(1232,678),(35,32,57),1)
        line(f,(48,678),(48+1184*min(t/36.55,1),678),(50,47,187),1)
        proc.stdin.write(f.tobytes())
        if i%150==0:print(f'frame {i}/{N} | {time.time()-started:.0f}s',flush=True)
    proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('FFmpeg failed')
    print(f'Wrote {target} ({time.time()-started:.1f}s)',flush=True)

if __name__=='__main__':main()
