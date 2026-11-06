#!/usr/bin/env python3
"""Scene-specific enhanced MONARCH adaptations. See README for build and limitations."""
from pathlib import Path
import argparse, importlib.util, math, subprocess, sys
from functools import lru_cache
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont,ImageChops
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'tools'))
from ffbin import ffmpeg
AS=ROOT/'showreel/seven/assets'; DIR=ROOT/'showreel/seven'
COUNTS={1:660,2:1572,3:720,4:2194,5:1084,6:600,7:1380}
DUR={1:11.,2:26.2,3:12.,4:1097/30,5:542/30,6:10.,7:23.}
FPS=60

def load(n):
 spec=importlib.util.spec_from_file_location('reference_render',DIR/f'render_{n:02}.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def ease(q):
 q=max(0.,min(1.,q));return q*q*(3-2*q)
def smooth(a,b,t):return ease((t-a)/(b-a))

def tilt_sprite(image,yaw,pitch=0):
 """Small image-plane perspective, not a 3D model; never warps a full frame."""
 a=np.array(image.convert('RGBA'));h,w=a.shape[:2]
 # Opposing top/bottom edges move independently like a shallow 3D card.
 dx=w*yaw;dy=h*pitch
 src=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
 dst=np.float32([[max(0,dx),max(0,dy)],[w-1+min(0,dx),max(0,-dy)],[w-1+min(0,dx),h-1-min(0,-dy)],[max(0,dx),h-1-min(0,dy)]])
 M=cv2.getPerspectiveTransform(src,dst);out=cv2.warpPerspective(a,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
 return Image.fromarray(out,'RGBA')

def keyed_icon(name):
 im=Image.open(AS/f'enhanced-05-{name}.png').convert('RGB').resize((160,160),Image.Resampling.LANCZOS)
 a=np.array(im).astype(np.int16);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];strength=g-np.maximum(r,b)
 alpha=np.uint8(np.clip((70-strength)*4,0,255));a[:,:,1]=np.minimum(g,np.maximum(r,b));return Image.fromarray(np.dstack([a.astype('uint8'),alpha]),'RGBA')

def setup(n,m):
 state={'t':0.}
 if n==1:
  # Reference-like soft optical projection and anti-aliased moving beam.
  def enhanced(i):
   t=i/30
   if t>=6.08:return m.frame_at(i)
   f=np.full((m.H,m.W,3),255,np.uint8);cx,cy,ang=m.pose(t)
   if t>=2.27:
    a=math.radians(ang);dx,dy=math.sin(a),-math.cos(a);tx,ty=cx+54*dx,cy+54*dy
    if 3.05<t<3.70:
     adj=ease((t-3.05)/.12)*ease((3.70-t)/.12);tx-=10*adj;ty-=15*adj
    spread=math.radians(24);d1=(math.sin(a-spread),-math.cos(a-spread));d2=(math.sin(a+spread),-math.cos(a+spread))
    pts=np.array([[tx,ty],[tx+3000*d1[0],ty+3000*d1[1]],[tx+3000*d2[0],ty+3000*d2[1]]],np.int32)
    mask=np.zeros((m.H,m.W),np.uint8);cv2.fillConvexPoly(mask,pts,255,lineType=cv2.LINE_AA)
    soft=cv2.GaussianBlur(mask,(0,0),4);a=soft.astype(np.float32)[:,:,None]/255
    f=np.uint8(np.clip(f*(1-a)+m.base*a,0,255))
    f=m.composite(f,cv2.bitwise_and(m.logo,mask))
   if t>=.35:f=m.draw_camera(f,cx,cy,ang,lens=t>=2.24)
   if 1.49<t<2.24:
    ly=np.interp(t,[1.49,1.60,1.80,2,2.20,2.24],[180,130,95,105,279,340])
    cv2.ellipse(f,(638,int(ly)),(25,25),0,0,180,(0,0,0),-1,cv2.LINE_AA)
   return Image.fromarray(f)
  return lambda i:enhanced(i/2)
 if n==2:
  def card(im,x,y,title,desc,delay,t):
   q=m.ease(delay,delay+.35,t)
   if q<=0:return
   sprite=Image.new('RGBA',(185,200));d=ImageDraw.Draw(sprite)
   d.rounded_rectangle((1,1,183,198),radius=22,fill=(255,255,255,255),outline=(218,209,210,255),width=2)
   d.ellipse((16,18,52,54),fill=m.RED);m.text(d,(34,36),'M',19,m.WHITE,'b')
   m.text(d,(61,28),title,12,m.BLACK,'b','lm');m.text(d,(61,45),'MONARCH STUDIO',9,(135,135,135),'r','lm')
   for j,line in enumerate(desc):m.text(d,(15,82+j*18),line,12,m.BLACK,'r','lm')
   for j in range(5):d.ellipse((17+j*18,172,25+j*18,180),fill=m.RED)
   sprite=tilt_sprite(sprite,.025*math.sin(t*2+x),.012*math.sin(t*1.7+x))
   xx=int(x+2*math.sin(t*1.6+x));yy=int(y+(1-q)*60+2*math.sin(t*1.8+y))
   sh=Image.new('L',(225,240));sh.paste(sprite.getchannel('A'),(20,20));sh=sh.filter(ImageFilter.GaussianBlur(11)).point(lambda z:int(z*.23))
   im.paste((61,19,25),(xx-14,yy-10),sh);im.paste(sprite,(xx,yy),sprite)
  m.service_card=card
  def hexagon(im,cx,cy,label,which,t,start):
   q=m.ease(start,start+.34,t)
   if q<=0:return
   d=ImageDraw.Draw(im);r=116*q;pts=[]
   for a in [-90,-30,30,90,150,210]:
    v=math.radians(a);pts.append((cx+math.cos(v)*r,cy+math.sin(v)*r))
   d.polygon([(x+7,y+11) for x,y in pts],fill=(236,222,223));d.polygon(pts,fill=m.RED)
   if q>.8:
    d.line([pts[0],pts[1]],fill=(247,90,100),width=4);d.line([pts[2],pts[3]],fill=m.BLACK,width=5);d.line([pts[4],pts[5]],fill=m.BLACK,width=5)
    m.icon_hex(d,cx,cy,which)
    if which==0:d.line((cx,cy-115,cx,cy-185,cx-78,cy-258),fill=m.BLACK,width=3);m.text(d,(cx-60,cy-279),label,24)
    elif which==1:d.line((cx,cy-115,cx,cy-185,cx+78,cy-258),fill=m.BLACK,width=3);m.text(d,(cx+80,cy-279),label,24)
    else:d.line((cx,cy+115,cx,cy+185,cx+78,cy+258),fill=m.BLACK,width=3);m.text(d,(cx+125,cy+279),label,24)
  m.hexagon=hexagon
  return lambda i:m.frame(i/FPS)
 if n==3:
  # The source resolves the greeting into the name before the eye; use a shallow dimensional lockup.
  def we(t):
   im=m.BG.copy()
   if t<2.70:
    q=m.p(2.33,2.58,t);m.put_text(im,'We’re',(m.mix(800,505,q),360),244,'normal',m.BLACK,shadow=True,width=360)
   else:
    q=m.p(2.70,3.02,t);width=m.mix(510,700,q)
    for j in range(5,0,-1):m.put_text(im,'MONARCH',(640-j*1.8,360+j*1.8),108,'bold',(65,65,65),width=width)
    m.put_text(im,'MONARCH',(640,360),108,'bold',m.BLACK,shadow=True,width=width)
   return im
  m.we=we
  orig=m.draw_eye
  def eye(t):
   im=orig(t)
   if 4.8<t<6.35:
    cx=m.mix(640,452,m.p(5.03,5.72,t));r=212;ir=r*.77
    overlay=Image.new('RGBA',(m.W,m.H));d=ImageDraw.Draw(overlay);red=m.p(5.05,5.50,t)
    # Clip the highlights to the eye silhouette, so no lines leak into the black field.
    col=(int(m.mix(155,190,red)),int(m.mix(155,42,red)),int(m.mix(155,48,red)))
    for dr in (0,8,16):d.arc((cx-ir+dr,360-ir+dr,cx+ir-dr,360+ir-dr),195,298,fill=col,width=2)
    hlx=cx+r*.51;hly=360-r*.55;d.ellipse((hlx-8,hly-8,hlx+8,hly+8),fill=(255,255,255))
    hh=m.mix(360,153,m.p(3.42,5.70,t));rx=m.mix(760,640,m.p(3.42,5.70,t));power=m.mix(.5,1.0,m.p(3.42,5.7,t))
    mask=Image.fromarray(m.eye_mask(hh,rx,power),'L');overlay.putalpha(ImageChops.multiply(overlay.getchannel('A'),mask));im.paste(overlay,(0,0),overlay)
   return im
  m.draw_eye=eye
  return lambda i:m.frame(i/2)
 if n==4:
  orig=m.stamp
  tracked=list(m.CARDS.values())+list(m.ADS.values())+m.PEOPLE+[m.STORE]
  sources={id(v):v for v in tracked};phases={id(v):i*.47 for i,v in enumerate(tracked)}
  @lru_cache(maxsize=160)
  def warped(key,step):return tilt_sprite(sources[key],step*.004,step*.0015)
  def stamp(im,sprite,cx,cy,w=None,h=None,angle=0,shadow=True):
   key=id(sprite);t=state['t']
   if key in sources:
    phase=phases[key];step=int(round(5*math.sin(t*1.35+phase)))
    sprite=warped(key,step);cx+=2.2*math.sin(t*1.5+phase);cy+=2.3*math.cos(t*1.2+phase)
   return orig(im,sprite,cx,cy,w,h,angle,shadow)
  m.stamp=stamp
  def frame(i):state['t']=i/FPS;return m.frame(i/2)
  return frame
 if n==5:
  for name in ('camera','mouse','pencil'):m.ICONS[name]=keyed_icon(name)
  original=m.icon
  def icon(im,name,x,y,size=80,angle=0):
   if name in ('camera','mouse','pencil'):
    s=m.ICONS[name].resize((max(1,int(size)),max(1,int(size))),Image.Resampling.NEAREST)
    if angle:s=s.rotate(angle,Image.Resampling.NEAREST,expand=True)
    im.paste(s,(int(x-s.width/2),int(y-s.height/2)),s)
   else:original(im,name,x,y,size,angle)
  m.icon=icon
  oldput=m.put
  def put(im,sprite,x,y,w,h=None,angle=0,opacity=255):
   t=state['t']
   if sprite is m.PROFILE or sprite is m.BACK or sprite is m.HAND:
    x+=5*math.sin((t-3.78)*1.5);y+=4*math.cos((t-3.78)*1.4);angle+=2*math.sin(t*1.2)
   oldput(im,sprite,x,y,w,h,angle,opacity)
  m.put=put
  def frame(i):state['t']=i/FPS;return m.frame(i/2)
  return frame
 if n==6:
  oldput=m.put
  @lru_cache(maxsize=32)
  def book(step):return tilt_sprite(m.BOOK,step*.006,step*.002)
  def put(im,img,x,y,w,h=None,angle=0,alpha=255):
   t=state['t']
   if img is m.BOOK:
    img=book(int(round(5*math.sin(t*2))));y+=5*math.sin(t*2.1);angle+=2*math.sin(t*1.3)
   elif img is m.BUST:
    x+=5*math.sin(t*1.4);y+=3*math.cos(t*1.4)
   elif img is m.PROFILE:
    x+=4*math.sin(t*1.4);angle+=1.5*math.sin(t*1.5)
   elif img is m.CROWN:
    y+=5*math.sin(t*2);angle+=2*math.sin(t*1.3)
   oldput(im,img,x,y,w,h,angle,alpha)
  m.put=put
  def frame(i):state['t']=i/FPS;return m.card(i/FPS).convert('RGB').crop((0,0,720,964))
  return frame
 if n==7:
  oldput=m.put
  def put(im,sp,x,y,w,h=None,angle=0,opacity=255):
   t=state['t']
   if sp is m.FRAMED:
    x+=5*math.sin(t*1.4);y+=7*math.cos(t*1.3);angle+=1.1*math.sin(t*1.5)
   elif sp is m.HELMET:
    x+=8*math.sin(t*1.25);y+=6*math.cos(t*1.45);angle+=1.3*math.sin(t*1.2)
   oldput(im,sp,x,y,w,h,angle,opacity)
  m.put=put
  # Sequence-specific slide and reveal of the independent foreground layers.
  def story(t):
   im=m.PAPER.copy();m.deco(im,t);d=ImageDraw.Draw(im)
   d.rectangle((0,610,365,970),fill=m.RED)
   q=m.p(14.4,14.85,t); xx=int(m.lerp(-190,80,q)); yy=int(375+4*math.sin(t*1.6))
   im.paste(m.FIST_FIXED,(xx,yy),m.FIST_FIXED);d=ImageDraw.Draw(im)
   m.text(d,(735,335),"We don't",64,m.INK,'bold');m.text(d,(735,415),'just make',54,m.INK,'reg')
   if t>14.9:m.text(d,(735,505),'content',82,m.INK,'bold')
   if t>15.6:d.line((575,515,575+325*m.p(15.6,15.95,t),515),fill=m.RED,width=8)
   if t>16.2:m.text(d,(345,1060),'We build stories',50,m.INK,'reg')
   if t>17.3:m.text(d,(345,1155),'that last.',58,m.RED,'bold')
   if t>16.0:
    q=m.p(16.0,16.55,t);dx=int((1-q)*370);d.rectangle((610+dx,1500,1080+dx,1745),fill=m.RED)
    m.put(im,m.HELMET,825+dx,1515,310);d=ImageDraw.Draw(im)
    d.rectangle((620+dx,1680,1060+dx,1780),fill=(37,21,20),outline=(190,148,100),width=5);m.text(d,(840+dx,1727),'MONARCH',64,(236,210,175),'narrow')
   return im
  m.story=story
  def frame(i):state['t']=i/FPS;return m.frame(i)
  return frame
 raise ValueError(n)

def render(n,refdir):
 m=load(n);make=setup(n,m);w,h=(720,964) if n==6 else (m.W,m.H)
 out=ROOT/f'public/demo/monarch-reference-{n:02}-enhanced.mp4';tmp=out.with_suffix('.silent.mp4') if n<=5 else out
 out.parent.mkdir(parents=True,exist_ok=True)
 enc=subprocess.Popen([ffmpeg(),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r','60','-i','-','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
 try:
  for i in range(COUNTS[n]):
   image=make(i)
   if isinstance(image,np.ndarray):data=image.tobytes()
   else:data=image.convert('RGB').tobytes()
   enc.stdin.write(data)
   if i%180==0:print(f'video {n}: {i}/{COUNTS[n]}',flush=True)
  enc.stdin.close()
  if enc.wait():raise RuntimeError('encoder failed')
  if n<=5:
   ref=refdir/f'{n:02}.mp4'
   subprocess.run([ffmpeg(),'-y','-v','error','-i',str(tmp),'-i',str(ref),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(DUR[n]),'-movflags','+faststart',str(out)],check=True)
 finally:
  if enc.poll() is None:enc.kill();enc.wait()
  if n<=5:tmp.unlink(missing_ok=True)
 print('Wrote',out,flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--video',type=int,choices=range(1,8),required=True);ap.add_argument('--reference-dir',type=Path,default=Path('/home/user/reference-inputs/seven'));ap.add_argument('--sample',type=float,nargs='*');a=ap.parse_args()
 if a.sample is not None:
  m=load(a.video);make=setup(a.video,m)
  for t in a.sample:
   im=make(round(t*FPS));im=Image.fromarray(im) if isinstance(im,np.ndarray) else im
   im.convert('RGB').save(f'/tmp/enhanced-{a.video}-{t}.jpg',quality=93)
 else:render(a.video,a.reference_dir)
if __name__=='__main__':main()
