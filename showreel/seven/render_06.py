#!/usr/bin/env python3
"""Build the silent 10-second MONARCH adaptation of reference 06."""
from pathlib import Path
import math,sys,subprocess
from functools import lru_cache
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ffbin import ffmpeg
AS=ROOT/'showreel/seven/assets';OUT=ROOT/'public/demo/monarch-reference-06.mp4'
W,H=1080,1920; FPS=60; CW,CH=720,965; CX,CY=180,220
INK=(17,17,19);RED=(170,8,31);WHITE=(247,247,246)
@lru_cache(None)
def font(size,kind='reg'):
 f={'reg':AS/'Inter.ttf','bold':ROOT/'showreel/v2/assets/Poppins-Bold.ttf','italic':AS/'InstrumentSerif-Italic.ttf'}[kind]
 return ImageFont.truetype(str(f),size)
def text(d,xy,s,size,col=INK,kind='reg',anchor='mm',stroke=0):
 d.text(xy,s,font=font(size,kind),fill=col,anchor=anchor,stroke_width=stroke,stroke_fill=col)
def ease(x):
 x=min(1,max(0,x));return x*x*(3-2*x)
def p(a,b,t):return ease((t-a)/(b-a))
def lerp(a,b,x):return a+(b-a)*x

def key(path):
 im=Image.open(path).convert('RGB');arr=np.array(im).astype(np.float32);r,g,b=arr[:,:,0],arr[:,:,1],arr[:,:,2]
 strength=g-np.maximum(r,b);alpha=np.uint8(np.clip((100-strength)*3,0,255));alpha=cv2.GaussianBlur(alpha,(3,3),.5)
 arr[:,:,1]=np.minimum(g,np.maximum(r,b));rgba=np.dstack([np.uint8(arr),alpha]);a=Image.fromarray(rgba,'RGBA')
 box=a.getchannel('A').getbbox();return a.crop(box) if box else a
BUST=key(AS/'06-bust.png');CROWN=key(AS/'06-crown.png');PROFILE=Image.open(AS/'06-profile.png').convert('RGBA')

def put(im,img,x,y,w,h=None,angle=0,alpha=255):
 if h is None:h=w*img.height/img.width
 sp=img.resize((max(1,int(w)),max(1,int(h))),Image.Resampling.LANCZOS)
 if angle:sp=sp.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 if alpha<255:sp.putalpha(sp.getchannel('A').point(lambda q:q*int(max(0,alpha))//255))
 im.paste(sp,(int(x-sp.width/2),int(y-sp.height/2)),sp)

def shadow(im,box,r=25,alpha=100,blur=25,offset=(15,20)):
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);x0,y0,x1,y1=box
 d.rounded_rectangle((x0+offset[0],y0+offset[1],x1+offset[0],y1+offset[1]),radius=r,fill=(0,0,0,alpha))
 im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))

def background():
 y,x=np.mgrid[0:H,0:W];rng=np.random.default_rng(6126)
 shade=204+11*np.sin(x/230+y/550)+7*np.sin(x/150-y/310)+rng.normal(0,2,(H,W));shade=np.clip(shade,0,255).astype('uint8')
 im=Image.fromarray(np.stack([shade,shade,shade],axis=2),'RGB').convert('RGBA')
 # A shadowed, independently drawn editing timeline behind the card.
 shadow(im,(90,1115,990,1505),16,125,25,(18,22));d=ImageDraw.Draw(im)
 d.rounded_rectangle((90,1115,990,1505),radius=18,fill=(27,27,30),outline=(220,220,220),width=4)
 d.rounded_rectangle((97,1122,983,1498),radius=12,fill=(23,23,26))
 for i in range(38):
  yy=1127+i*9; col=(38+i%3*4,38+i%3*4,42+i%3*4);d.rectangle((100,yy,979,yy+8),fill=col)
  d.rectangle((106,yy+2,111,yy+6),fill=(145,145,148));d.rectangle((119,yy+1,126,yy+7),fill=[(100,60,74),(67,85,108),(87,97,73)][i%3])
  d.rectangle((137,yy+3,176+(i%5)*8,yy+4),fill=(118,118,120))
  start=300+(i*79)%440;length=60+(i*47)%210;end=min(980,start+length)
  d.rectangle((start,yy+1,end,yy+7),fill=[(70,62,72),(83,33,42),(61,76,72),(80,77,55)][i%4])
 d.line((405,1122,405,1499),fill=(188,45,57),width=1)
 # Raised studio badge.
 shadow(im,(474,45,606,180),22,95,16,(16,18));d=ImageDraw.Draw(im)
 d.rounded_rectangle((474,45,606,180),radius=23,fill=(37,3,10),outline=(185,64,81),width=6)
 text(d,(540,111),'M',70,(244,216,221),'bold')
 # Floating main card shadow.
 shadow(im,(CX,CY,CX+CW,CY+CH),46,140,28,(18,25))
 return im
BASE=background()
# Card background: a subtle off-white diagonal paper grain and palm shadows.
def card_bg():
 y,x=np.mgrid[0:CH,0:CW];rng=np.random.default_rng(617)
 shade=np.clip(238-8*((x-CW/2)**2/(CW/2)**2+(y-CH/2)**2/(CH/2)**2)+rng.normal(0,1.3,(CH,CW)),0,255).astype('uint8')
 im=Image.fromarray(np.stack([shade,shade,shade],axis=2),'RGB').convert('RGBA')
 leaf=Image.new('RGBA',(CW,CH));d=ImageDraw.Draw(leaf)
 for i in range(14):
  xx=340+i*19;d.line([(580,55),(xx,60+i*18),(xx-75,90+i*24)],fill=(85,85,85,11),width=3)
 im=Image.alpha_composite(im,leaf.filter(ImageFilter.GaussianBlur(3)))
 return im
CARD=card_bg(); MASK=Image.new('L',(CW,CH));ImageDraw.Draw(MASK).rounded_rectangle((0,0,CW-1,CH-1),radius=47,fill=255)

def arrow(im,x,y,ang):
 a=Image.new('RGBA',(180,180));d=ImageDraw.Draw(a)
 d.polygon([(8,12),(150,12),(150,42),(52,42),(52,135),(20,135),(20,45),(8,33)],fill=(9,9,11,255))
 a=a.rotate(ang,resample=Image.Resampling.BICUBIC,expand=False)
 im.paste(a,(x-90+5,y-90+6),a.filter(ImageFilter.GaussianBlur(3)))
 im.paste(a,(x-90,y-90),a)

def book():
 # Original MONARCH OS project, presented as an editorial cover, not a product screenshot.
 b=Image.new('RGBA',(215,286));d=ImageDraw.Draw(b)
 d.rounded_rectangle((7,4,211,282),radius=4,fill=(49,49,51),outline=(18,18,19),width=4)
 for z in [16,20,25,30]:d.rectangle((z,13,211-(z-7),273-(z-7)),outline=(180-z,180-z,180-z),width=1)
 d.rectangle((7,4,20,282),fill=(25,25,27));d.line((14,11,14,276),fill=(145,145,145),width=2)
 text(d,(115,48),'MONARCH',16,(233,233,233),'bold');text(d,(115,69),'OS',11,(220,220,220),'reg')
 # relief cameo from the independently generated bust
 put(b,BUST,113,159,96)
 text(d,(115,246),'ONE WORKSPACE',9,(210,210,210),'reg')
 return b
BOOK=book()

def grid(d):
 for x in range(191,530,23):
  for y in range(438,800,23):
   d.line((x-2,y,x+2,y),fill=(156,156,156,150),width=1);d.line((x,y-2,x,y+2),fill=(156,156,156,150),width=1)

def brackets(d):
 for x,dx in [(70,55),(650,-55)]:
  for y,dy in [(225,58),(770,-58)]:
   d.line((x,y,x+dx,y),fill=INK,width=3);d.line((x,y,x,y+dy),fill=INK,width=3)

def card(t):
 im=CARD.copy(); d=ImageDraw.Draw(im)
 arrow(im,78,75,-12+math.sin(t*1.5)*4);arrow(im,642,890,180+math.sin(t*1.8)*5)
 d=ImageDraw.Draw(im)
 if t<2.35:
  # bust grows into view from below, as in the supplied sequence
  q=p(.12,.85,t);size=lerp(180,465,q); y=lerp(1080,800,q)
  put(im,BUST,360,y,size)
  d=ImageDraw.Draw(im)
  if t>.35:text(d,(240,373),'One vision',32,INK,'reg')
  if t>1.10:text(d,(436,373),'built to be',32,INK,'reg')
  if t>1.72:text(d,(442,416),'created',38,RED,'bold')
  if t>.8:
   d.line((675,38,675,895),fill=(60,60,63),width=1);d.line((565,165,707,165),fill=(40,40,43),width=1)
   d.polygon([(675,139),(680,160),(702,165),(680,170),(675,192),(670,170),(650,165),(670,160)],fill=INK)
 elif t<5.30:
  q=p(2.35,2.85,t);grid(d)
  text(d,(440,355),'Today',35,INK,'italic');text(d,(360,400),'MONARCH OS',43,INK,'bold')
  y=lerp(640,635,q); w=lerp(220,205,q); put(im,BOOK,360,y,w,angle=lerp(15,0,p(2.4,3.35,t)))
  d=ImageDraw.Draw(im)
  if t>3.55:
   text(d,(300,855),'brings together',37,INK,'italic')
   reveal=p(4.0,4.55,t)
   if reveal>0:
    line=Image.new('RGBA',(480,80));ld=ImageDraw.Draw(line);text(ld,(0,35),'five work domains',35,RED,'bold','lm')
    wid=int(line.width*reveal);im.paste(line.crop((0,0,wid,80)),(180,874),line.crop((0,0,wid,80)))
  # controlled fragments around the typography, never covering it
  for i in range(4):
   x=[45,610,40,620][i];y0=[140,170,720,740][i]+18*math.sin(t*2+i)
   d.polygon([(x,y0),(x+32,y0+8),(x+45,y0+38),(x+10,y0+33)],fill=(160,160,160,80))
 elif t<7.70:
  q=p(5.30,5.75,t);size=lerp(250,410,q)
  d.line((0,364,720,612),fill=(80,80,80,150),width=2);d.line((80,0,630,965),fill=(80,80,80,150),width=2)
  text(d,(360,350),'MONARCH Studio',35,INK,'reg')
  shadow(im,(int(360-size/2),int(590-size/2),int(360+size/2),int(590+size/2)),0,75,12,(8,12))
  put(im,PROFILE,360,590,size,size)
  d=ImageDraw.Draw(im)
  if t>6.25:text(d,(360,830),"isn't just",39,INK,'bold')
  if t>6.70:
   s='editing';rw=int(244*p(6.7,7.2,t));d.rectangle((238,865,238+rw,930),fill=INK)
   label=Image.new('RGBA',(260,65));ld=ImageDraw.Draw(label);text(ld,(8,32),s,56,WHITE,'bold','lm')
   if rw: im.paste(label.crop((0,0,min(rw,260),65)),(238,865),label.crop((0,0,min(rw,260),65)))
 else:
  brackets(d)
  if t>7.83:text(d,(360,375),"it's about",48,INK,'reg')
  q=p(7.8,8.4,t);put(im,CROWN,360,650,lerp(100,260,q))
  d=ImageDraw.Draw(im)
  # animated dotted circular orbit, behind the caption
  phase=(t-7.7)*2
  for i in range(52):
   a=i*2*math.pi/52+phase
   if i<49:
    x=360+180*math.cos(a);y=650+180*math.sin(a);d.ellipse((x-3,y-3,x+3,y+3),fill=INK)
  if t>8.55:
   text(d,(315,880),'Control over',50,INK,'reg');text(d,(532,880),'chaos',50,RED,'italic')
 return im

def frame(i):
 t=i/FPS;im=BASE.copy();panel=card(t)
 # rounded panel clipping is applied once, no off-card leaks
 panel.putalpha(MASK);im.alpha_composite(panel,(CX,CY));d=ImageDraw.Draw(im)
 d.rounded_rectangle((CX,CY,CX+CW,CY+CH),radius=47,outline=(248,248,248),width=5)
 # The original had an editor timeline CTA: replace it with MONARCH's own words.
 # Faint dark halo gives the white typography similar separation from the timeline.
 for off in [(0,0)]:
  text(d,(540,1282),'Explore MONARCH',49,WHITE,'bold',stroke=1)
  text(d,(540,1407),'Project Work',112,WHITE,'bold',stroke=1)
 return im.convert('RGB')

def main():
 OUT.parent.mkdir(parents=True,exist_ok=True)
 proc=subprocess.Popen([ffmpeg(),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT)],stdin=subprocess.PIPE)
 try:
  for i in range(600):
   proc.stdin.write(frame(i).tobytes())
   if i%60==0:print(f'{i}/600',flush=True)
  proc.stdin.close()
  if proc.wait()!=0:raise RuntimeError('ffmpeg failed')
 finally:
  if proc.poll() is None:proc.kill();proc.wait()
 print('Wrote',OUT)
if __name__=='__main__':main()
