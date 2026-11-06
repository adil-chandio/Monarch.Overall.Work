#!/usr/bin/env python3
"""Create original kinetic-typography portfolio samples, from our own assets only.

Three 9-second vertical edits plus four landscape edits composed from those originals.
All sound in the vertical samples is procedural; the portfolio uses its reference audio.
Run from repo root: python3 showreel/portfolio/create_samples.py
"""
import math, subprocess, sys, time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.io import wavfile
sys.path.insert(0,'tools');from ffbin import ffmpeg
cv2.setNumThreads(1)
ROOT=Path('showreel/portfolio'); OUT=Path('public/demo/portfolio-samples'); OUT.mkdir(parents=True,exist_ok=True)
TMP=Path('/tmp/monarch-original-samples');TMP.mkdir(exist_ok=True)
FONT='showreel/v2/assets/Anton-Regular.ttf';MED='showreel/v2/assets/Poppins-Medium.ttf';BOLD='showreel/v2/assets/Poppins-Bold.ttf'
FPS=30;DUR=9.;SR=48000

def clamp(x):return max(0.,min(1.,x))
def ease(x):
 x=clamp(x);return 1-(1-x)**3

def text_asset(word,size=100,col=(245,240,235),maxw=460,font=FONT):
 font=ImageFont.truetype(font,size); box=font.getbbox(word)
 p=Image.new('RGBA',(box[2]-box[0]+8,box[3]-box[1]+8))
 ImageDraw.Draw(p).text((4-box[0],4-box[1]),word,font=font,fill=(*col,255))
 if p.width>maxw:
  p=p.resize((maxw,round(p.height*maxw/p.width)),Image.Resampling.LANCZOS)
 a=np.asarray(p);return cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2BGR),a[:,:,3]

def put(f,img,mask,x,y,opacity=1.):
 h,w=mask.shape;H,W=f.shape[:2];x=int(round(x));y=int(round(y));x0=max(0,x);y0=max(0,y);x1=min(W,x+w);y1=min(H,y+h)
 if x1<=x0 or y1<=y0 or opacity<=0:return
 a=mask[y0-y:y1-y,x0-x:x1-x].astype(np.float32)[...,None]*(opacity/255)
 dst=f[y0:y1,x0:x1];dst[:]=(dst*(1-a)+img[y0-y:y1-y,x0-x:x1-x]*a).astype(np.uint8)

def put_anim(f,asset,x,y,local,delay):
 u=ease((local-delay)/.28)
 if u<=0:return
 # Restrained scale-settle, plus a short upward move. Position remains safe inside frame.
 z=1+.07*(1-u);img,mask=asset
 if z>1.001:
  size=(int(img.shape[1]*z),int(img.shape[0]*z));im=cv2.resize(img,size);ma=cv2.resize(mask,size)
 else:im,ma=img,mask
 put(f,im,ma,x,y+20*(1-u),u)

def photo(path,w,h):
 im=cv2.imread(str(path));assert im is not None,path
 s=max(w/im.shape[1],h/im.shape[0]);im=cv2.resize(im,(int(im.shape[1]*s)+2,int(im.shape[0]*s)+2),interpolation=cv2.INTER_AREA)
 y=(im.shape[0]-h)//2;x=(im.shape[1]-w)//2
 return im[y:y+h,x:x+w]

def push(img,t,w,h):
 z=1.04+.065*(t/DUR); sw=int(w*z);sh=int(h*z)
 im=cv2.resize(img,(sw,sh),interpolation=cv2.INTER_LINEAR)
 x=int((sw-w)*(.44+.09*math.sin(t*.45)));y=int((sh-h)*(.38+.06*math.sin(t*.32)))
 return im[y:y+h,x:x+w].copy()

def character(w=350,h=523):
 src=cv2.imread(str(ROOT/'assets/character.png'));b,g,r=cv2.split(src.astype(np.float32));a=np.clip((35-(g-np.maximum(r,b)))/28,0,1)
 a=cv2.GaussianBlur(a,(0,0),.8);src[:,:,1]=np.minimum(src[:,:,1],np.maximum(src[:,:,0],src[:,:,2])+4)
 return cv2.resize(src,(w,h)),cv2.resize(np.uint8(a*255),(w,h))

def sound(idx):
 n=int(SR*DUR);y=np.zeros(n,np.float32);rng=np.random.default_rng(880+idx)
 def add(sig,t,g=1):
  i=int(t*SR);k=min(len(sig),n-i)
  if k>0:y[i:i+k]+=sig[:k]*g
 for k in range(18):
  t=np.arange(int(.21*SR))/SR;freq=35+90*np.exp(-t/.027)
  kick=np.sin(2*np.pi*np.cumsum(freq)/SR)*np.exp(-t/.09)
  add(kick,k*.5,.30)
  for j in range(4):
   tt=np.arange(int(.035*SR))/SR;hat=rng.standard_normal(len(tt))*np.exp(-tt/.008)
   add(hat,k*.5+j*.125,.022 if j%2 else .034)
  if k%2:
   tt=np.arange(int(.13*SR))/SR;snare=rng.standard_normal(len(tt))*np.exp(-tt/.045)
   add(snare,k*.5,.055)
 for t0 in [0,2.4,4.8,7.2]:
  tt=np.arange(int(.42*SR))/SR;fr=85*(25/85)**(tt/.42)
  hit=np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt/.18)
  add(hit,t0,.38)
  if t0>0:
   tt=np.arange(int(.22*SR))/SR;nz=rng.standard_normal(len(tt))*np.sin(np.pi*tt/.22)**2
   add(nz,t0-.22,.04)
 t=np.arange(n)/SR; notes=[73.42,65.41,87.31][idx]
 y+=.075*np.sin(2*np.pi*notes*t)*(.35+.65*np.exp(-(t%.5)/.22))
 y*=np.minimum(1,(DUR-t)/.3)
 y=np.tanh(y*1.4);y*=.76/max(np.max(np.abs(y)),.001)
 path=TMP/f'sample-{idx}.wav';wavfile.write(str(path),SR,(y*32767).astype(np.int16));return path

WORDS=[
 [['YOUR TIME','IS NOT','THE PROBLEM'],["IT'S WHAT",'YOU DO','WITH IT'],['MAKE','EVERY','SECOND'],['COUNT.','START NOW']],
 [['EVERYONE','IS TALKING.'],['BUT WHO','LISTENS?'],['STAND','OUT.'],['BE','REMEMBERED.']],
 [['ONE','IDEA.'],['THREE','WAYS TO','MOVE.'],['DESIGN.','CUT.','IMPACT.'],['MAKE','YOUR MARK.']]]
RED=(240,69,67);WHITE=(245,238,235)

def render_vertical(idx,path):
 w,h=540,960
 files=[['timepiece.png','workstation.png'],['city.png','signal.png'],['prism.png','prism.png']][idx]
 sources=[photo(ROOT/'assets'/p,w,h) for p in files]
 char,cm=character(); wav=sound(idx)
 # All type is measured ahead; image font rasterization is not inside the frame loop.
 texts=[[text_asset(s,88,RED if j==len(group)-1 else WHITE,450) for j,s in enumerate(group)] for group in WORDS[idx]]
 tag=text_asset(['01 / THE TIME EDIT','02 / THE STORY EDIT','03 / THE MOTION EDIT'][idx],15,(231,197,187),460,MED)
 caption=text_asset('A MONARCH MOTION STUDY',13,(213,176,169),460,MED)
 audio=['-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','160k']
 proc=subprocess.Popen([ffmpeg(),'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(FPS),'-i','-']+audio+['-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
 for i in range(int(DUR*FPS)):
  t=i/FPS;seg=min(3,int(t//2.4));starts=[0,2.4,4.8,7.2];local=t-starts[seg]
  # Segment 3 has shorter duration; all text stays in the vertical safe area.
  if idx<2 or seg in (1,3):
   f=push(sources[seg%2],t,w,h)
   f=cv2.addWeighted(f,.78,np.zeros_like(f),.22,0)
   if seg==1:
    shade=np.full_like(f,(11,10,16));f=cv2.addWeighted(f,.56,shade,.44,0)
  else:
   yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
   glow=np.exp(-(((xx-270)/220)**2+((yy-510)/280)**2)*1.5)
   f=np.zeros((h,w,3),np.uint8);f[:,:,0]=8+glow*7;f[:,:,1]=8+glow*8;f[:,:,2]=12+glow*70
   z=1+.035*t/DUR;cs=cv2.resize(char,(int(350*z),int(523*z)));ms=cv2.resize(cm,(cs.shape[1],cs.shape[0]))
   put(f,cs,ms,(w-cs.shape[1])/2+4*math.sin(t*.6),h-cs.shape[0]+10,1.)
  # Dark typography shelf, leaving photographic context visible.
  overlay=np.zeros_like(f);overlay[:410]=(8,8,12)
  f=cv2.addWeighted(f,.88,overlay,.12,0)
  if seg==1 and idx==0:
   center=(405,660);cv2.circle(f,center,110,(50,50,160),2,cv2.LINE_AA)
   a=t*2.1;end=(int(center[0]+90*math.sin(a)),int(center[1]-90*math.cos(a)))
   cv2.line(f,center,end,(60,70,235),4,cv2.LINE_AA)
   for k in range(12):
    q=k*math.pi/6;x=int(center[0]+98*math.sin(q));y=int(center[1]-98*math.cos(q));cv2.circle(f,(x,y),2,(100,100,210),-1,cv2.LINE_AA)
  if seg==1 and idx==1:
   # Subject-tracking bracket and scanning line, visual rather than fake captioning.
   for x in (112,430):
    cv2.line(f,(x,440),(x,500),(60,80,235),2,cv2.LINE_AA)
   cv2.line(f,(112,440),(150,440),(60,80,235),2,cv2.LINE_AA)
   cv2.line(f,(392,440),(430,440),(60,80,235),2,cv2.LINE_AA)
  if seg==1 and idx==2:
   for k in range(3):
    xx=70+k*130;hh=int(90*ease((local-k*.15)/.7))
    cv2.rectangle(f,(xx,810-hh),(xx+100,810),(35,40,145+k*25),2,cv2.LINE_AA)
  # White/red text on upper negative space with timed reveals.
  put(f,tag[0],tag[1],44,48,.9)
  for j,asset in enumerate(texts[seg]):put_anim(f,asset,42,112+j*91,local,j*.18)
  # Accent stroke and finishing typography move in on the same cadence.
  p=ease((local-.35)/.4);cv2.line(f,(44,398),(44+int(162*p),398),(60,65,235),3,cv2.LINE_AA)
  put(f,caption[0],caption[1],44,910,.9)
  # A one-frame light pulse on the edit rather than a long wash across text.
  if seg and 0<=local<1/FPS+.001:f=cv2.addWeighted(f,.84,np.full_like(f,(60,55,100)),.16,0)
  proc.stdin.write(f.tobytes())
 proc.stdin.close()
 if proc.wait():raise RuntimeError('Vertical encoder failed')
 print('  wrote',path,flush=True)

def render_wide(idx,src,path):
 w,h=960,540
 groups=[
  [['TIME','IS A','CHOICE.'],['MAKE','EACH','CUT.'],['HOLD','THE','MOMENT.']],
  [['CUT','THROUGH','NOISE.'],['TELL','A BETTER','STORY.'],['STAND','OUT','HERE.']],
  [['IDEAS','INTO','MOTION.'],['DESIGN','THE','FEELING.'],['CREATE','YOUR','MARK.']],
  [['MAKE','IT','MATTER.'],['MAKE','IT','MOVE.'],['MAKE','IT','MONARCH.']]][idx]
 titles=[[text_asset(q,96,RED if j==2 else WHITE,420) for j,q in enumerate(g)] for g in groups]
 images=[['timepiece.png','workstation.png'],['city.png','signal.png'],['prism.png','workstation.png'],['signal.png','prism.png']][idx]
 bgs=[photo(ROOT/'assets'/p,440,h) for p in images]
 tag=text_asset(['01 / TIME','02 / STORY','03 / MOTION','04 / IMPACT'][idx],16,(223,181,174),450,MED)
 foot=text_asset('MONARCH  /  ORIGINAL EDIT',13,(206,170,165),450,MED)
 proc=subprocess.Popen([ffmpeg(),'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(FPS),'-i','-',
 '-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
 yy,xx=np.mgrid[0:h,0:w].astype(np.float32);g=np.exp(-(((xx-480)/400)**2+((yy-270)/320)**2)*1.6)
 base=np.zeros((h,w,3),np.uint8);base[:,:,0]=8+g*7;base[:,:,1]=8+g*8;base[:,:,2]=12+g*55
 for i in range(int(8*FPS)):
  t=i/FPS;seg=min(2,int(t//2.4));phase=t-seg*2.4;f=base.copy()
  for x in range(0,w,100):cv2.line(f,(x,0),(x,h),(17,17,31),1)
  # Different original photographic plates cut on the scene beat; no borrowed frames.
  im=push(bgs[seg%2],t,440,h);im=cv2.addWeighted(im,.8,np.zeros_like(im),.2,0)
  ix=520 if idx%2==0 else 0;f[:,ix:ix+440]=im
  tx=45 if idx%2==0 else 495
  put(f,tag[0],tag[1],tx,38,.9)
  for j,asset in enumerate(titles[seg]):put_anim(f,asset,tx,93+j*100,phase,j*.14)
  cv2.line(f,(tx,446),(tx+int(190*ease(phase/.8)),446),(56,60,230),3,cv2.LINE_AA)
  put(f,foot[0],foot[1],tx,480,.9)
  edge=520 if idx%2==0 else 440
  cv2.line(f,(edge,0),(edge,h),(40,45,165),2,cv2.LINE_AA)
  if seg and phase < 1/FPS+.001:f=cv2.addWeighted(f,.9,np.full_like(f,(40,40,80)),.1,0)
  proc.stdin.write(f.tobytes())
 proc.stdin.close()
 if proc.wait():raise RuntimeError('Wide encoder failed')
 print('  wrote',path,flush=True)

def main():
 names=['time-edit.mp4','story-edit.mp4','motion-edit.mp4']
 for i,n in enumerate(names):render_vertical(i,OUT/n)
 for i in range(4):render_wide(i,OUT/names[i%3],OUT/f'landscape-{i+1:02d}.mp4')
if __name__=='__main__':main()
