#!/usr/bin/env python3
"""Render the main-frame-only, silent MONARCH adaptation of reference 07."""
from pathlib import Path
from functools import lru_cache
import math,subprocess,sys
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ffbin import ffmpeg
AS=ROOT/'showreel/seven/assets';OUT=ROOT/'public/demo/monarch-reference-07.mp4'
W,H,FPS=1080,1920,60
INK=(19,17,19);RED=(165,0,24);WHITE=(250,249,248)
@lru_cache(None)
def font(size,kind='reg'):
 f={'reg':AS/'Inter.ttf','bold':ROOT/'showreel/v2/assets/Poppins-Bold.ttf','narrow':AS/'Oswald.ttf','serif':AS/'InstrumentSerif-Italic.ttf'}[kind]
 return ImageFont.truetype(str(f),int(size))
def text(d,pos,s,size,color=INK,kind='reg',anchor='mm'):
 d.text(pos,s,font=font(size,kind),fill=color,anchor=anchor)
def ease(q):
 q=max(0,min(1,q));return q*q*(3-2*q)
def p(a,b,t):return ease((t-a)/(b-a))
def lerp(a,b,q):return a+(b-a)*q

def key(name):
 im=Image.open(AS/('07-'+name+'.png')).convert('RGB');arr=np.asarray(im).astype(np.float32);r,g,b=arr[:,:,0],arr[:,:,1],arr[:,:,2]
 alpha=np.uint8(np.clip((55-(g-np.maximum(r,b)))*5,0,255));alpha=cv2.GaussianBlur(alpha,(3,3),.5)
 arr[:,:,1]=np.minimum(g,np.maximum(r,b));out=Image.fromarray(np.dstack([arr.astype('uint8'),alpha]),'RGBA')
 box=out.getchannel('A').getbbox();return out.crop(box) if box else out
BACK=Image.open(AS/'07-warrior-back.png').convert('RGB')
SIDE=key('warrior-side');FRAME=key('frame');HANDS=key('hands');HELMET=key('helmet');FIST=key('fist')

def put(im,sp,x,y,w,h=None,angle=0,opacity=255):
 if h is None:h=w*sp.height/sp.width
 a=sp.resize((max(1,int(w)),max(1,int(h))),Image.Resampling.LANCZOS)
 if angle:a=a.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if opacity<255:a.putalpha(a.getchannel('A').point(lambda z:z*int(max(0,opacity))//255))
 im.paste(a,(int(x-a.width/2),int(y-a.height/2)),a)

def paper():
 y,x=np.mgrid[0:H,0:W];rng=np.random.default_rng(706)
 shade=244-3*(x/W)-2*(y/H)+rng.normal(0,1.55,(H,W))
 # softly falling diagonal shadows on textured paper
 for intercept in [360,1100,1800]:
  dist=x*.75+y-intercept
  shade-=12*np.exp(-dist**2/(2*40**2))
 shade=np.uint8(np.clip(shade,0,255));return Image.fromarray(np.stack([shade,shade,shade],2),'RGB').convert('RGBA')
PAPER=paper()
# Isolated golden/red corner object derived from the independently generated frame.
CORNER=FRAME.crop((int(FRAME.width*.55),0,FRAME.width,int(FRAME.height*.23)))

def deco(im,t):
 put(im,CORNER,1000+20*math.sin(t*1.4),90,360,angle=5*math.sin(t))
 put(im,CORNER,65,1850,260,angle=180+4*math.sin(t*1.4))

def grid(im,cx,cy):
 d=ImageDraw.Draw(im)
 for x in range(cx-210,cx+211,28):
  for y in range(cy-210,cy+211,28):d.ellipse((x-1,y-1,x+1,y+1),fill=(142,142,142,170))

def draw_label(d,cx,cy,word):
 text(d,(cx,cy-35),'NO',125,INK,'bold')
 bbox=d.textbbox((0,0),word,font=font(48,'bold'));w=bbox[2]-bbox[0]+35
 d.rectangle((cx-w/2,cy+38,cx+w/2,cy+106),fill=RED);text(d,(cx,cy+71),word,48,WHITE,'bold')

def framed_art():
 # The rear image is an independently generated illustration, not source footage.
 w,h=780,1180
 f=FRAME.resize((w,h),Image.Resampling.LANCZOS)
 im=Image.new('RGBA',(w,h))
 photo=ImageOps.fit(BACK,(int(w*.58),int(h*.64)),method=Image.Resampling.LANCZOS)
 im.paste(photo,(int(w*.21),int(h*.215)))
 im.alpha_composite(f)
 return im
FRAMED=framed_art()
# Pre-size repeated cutouts for the portrait shots.
SIDE_FIXED=SIDE.resize((670,int(670*SIDE.height/SIDE.width)),Image.Resampling.LANCZOS)
HANDS_FIXED=HANDS.resize((850,int(850*HANDS.height/HANDS.width)),Image.Resampling.LANCZOS)
# Feather the cropped lower edge of the fabric instead of showing a hard seam.
ha=np.array(HANDS_FIXED);n=min(60,ha.shape[0]);ha[-n:,:,3]=(ha[-n:,:,3].astype(np.float32)*np.linspace(1,0,n)[:,None]).astype('uint8')
HANDS_FIXED=Image.fromarray(ha,'RGBA')
HELMET_FIXED=HELMET.resize((600,int(600*HELMET.height/HELMET.width)),Image.Resampling.LANCZOS)
FIST_FIXED=FIST.resize((220,int(220*FIST.height/FIST.width)),Image.Resampling.LANCZOS)
fa=np.array(FIST_FIXED);n=min(65,fa.shape[0]);fa[-n:,:,3]=(fa[-n:,:,3].astype(np.float32)*np.linspace(1,0,n)[:,None]).astype('uint8')
FIST_FIXED=Image.fromarray(fa,'RGBA')
BG_BACK=ImageOps.fit(BACK,(W,H),method=Image.Resampling.LANCZOS)
SKY=BG_BACK.crop((0,0,W,420)).resize((W,H),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(22))
reveal=np.full((H,W),255,dtype=np.uint8)
reveal[:150,:]=np.linspace(0,255,150,dtype=np.uint8)[:,None]
REVEAL_MASK=Image.fromarray(reveal,'L')

def opening(t):
 # The warrior rises from the bottom as the camera reveals the image.
 offset=int(lerp(1040,0,p(0,1.6,t)))
 im=SKY.copy();im.paste(BG_BACK,(0,offset),REVEAL_MASK)
 return im.convert('RGBA')

def gallery(t):
 im=PAPER.copy();deco(im,t)
 # Zoom back from the initial image into an ornate floating portrait.
 q=p(2.38,3.15,t);width=lerp(1660,790,q)
 if t<3.5:cx=540
 elif t<4.8:cx=lerp(540,240,p(3.5,4.2,t))
 else:cx=lerp(240,825,p(4.8,5.35,t))
 cy=960;put(im,FRAMED,cx,cy,width)
 d=ImageDraw.Draw(im)
 if 3.65<t<4.9:
  alpha=p(3.65,4.0,t);x=int(lerp(1120,850,alpha));draw_label(d,x,965,'LIMITS')
 if t>=5.05:
  alpha=p(5.05,5.4,t);x=int(lerp(-140,270,alpha));draw_label(d,x,965,'SHORTCUTS')
 # understated clouds below the frame: soft translucent layered ellipses.
 cloud=Image.new('RGBA',(W,H));cd=ImageDraw.Draw(cloud)
 for j in range(6):
  x=cx-250+j*110+18*math.sin(t*1.5+j);y=1580+24*math.sin(j*2+t)
  cd.ellipse((x-90,y-35,x+90,y+48),fill=(230,230,230,int(155*p(2.7,3.2,t))))
 im.alpha_composite(cloud.filter(ImageFilter.GaussianBlur(17)))
 return im

def bold_statement(t):
 im=PAPER.copy();deco(im,t);grid(im,540,960);d=ImageDraw.Draw(im)
 if t>=6.4:text(d,(540,925),'Just bold,',80,INK,'bold')
 if t>7.05:text(d,(385,1015),'unyielding',66,INK,'bold')
 if t>7.34:
  text(d,(765,1015),'CRAFT',64,WHITE,'bold');d.rectangle((650,977,905,1054),fill=RED);text(d,(777,1015),'CRAFT',64,WHITE,'bold')
 return im

def vision(t):
 im=PAPER.copy();deco(im,t)
 # moving subject stays to the left so text is never covered.
 x=lerp(-175,185,p(9,9.8,t));y=1250
 im.paste(SIDE_FIXED,(int(x-SIDE_FIXED.width/2),int(y-SIDE_FIXED.height/2)),SIDE_FIXED)
 d=ImageDraw.Draw(im)
 text(d,(710,375),'THE VISION',50,INK,'serif');text(d,(710,490),'MONARCH',120,RED,'narrow')
 text(d,(710,570),'C R E A T I V E   S T U D I O',22,INK,'bold')
 if t>10.80:text(d,(735,780),'WE',48,INK,'narrow')
 if t>11.05:text(d,(735,875),'TURN',72,RED,'narrow')
 if t>11.45:text(d,(735,970),'IDEAS INTO',43,INK,'reg')
 if t>11.85:
  d.rectangle((605,1035,865,1118),fill=RED);text(d,(735,1073),'IMPACT',60,WHITE,'narrow')
 return im

def ideas(t):
 im=PAPER.copy();deco(im,t);d=ImageDraw.Draw(im)
 # sweeping crimson fabric ribbon behind hands
 pts=[(0,570),(140,660),(330,750),(550,810),(760,820),(930,770),(1080,700),(1080,1100),(870,1080),(640,1030),(400,960),(190,840),(0,690)]
 d.polygon(pts,fill=RED)
 im.paste(HANDS_FIXED,(int((W-HANDS_FIXED.width)/2),780),HANDS_FIXED)
 d=ImageDraw.Draw(im);text(d,(540,210),'We bring',56,INK,'reg')
 if t>12.86:text(d,(540,330),'IDEAS',138,RED,'narrow')
 if t>13.55:text(d,(540,440),'TO LIFE',64,INK,'bold')
 return im

def story(t):
 im=PAPER.copy();deco(im,t);d=ImageDraw.Draw(im)
 d.rectangle((0,610,365,970),fill=RED)
 im.paste(FIST_FIXED,(80,375),FIST_FIXED)
 d=ImageDraw.Draw(im)
 text(d,(735,335),"We don't",64,INK,'bold');text(d,(735,415),'just make',54,INK,'reg')
 if t>14.9:text(d,(735,505),'content',82,INK,'bold')
 if t>15.6:d.line((575,515,900,515),fill=RED,width=8)
 if t>16.2:text(d,(345,1060),'We build stories',50,INK,'reg')
 if t>17.3:text(d,(345,1155),'that last.',58,RED,'bold')
 # A small helmet/plaque recalls the reference's shield and nameplate.
 d.rectangle((610,1500,1080,1745),fill=RED)
 put(im,HELMET,825,1515,310)
 d=ImageDraw.Draw(im);d.rectangle((620,1680,1060,1780),fill=(37,21,20),outline=(190,148,100),width=5)
 text(d,(840,1727),'MONARCH',64,(236,210,175),'narrow')
 return im

def ending(t):
 im=PAPER.copy();deco(im,t);d=ImageDraw.Draw(im)
 text(d,(540,310),'The vision',108,INK,'bold')
 if t>20.4:text(d,(540,430),'THAT NEVER',55,INK,'narrow')
 if t>21.0:text(d,(540,585),'settles',185,RED,'bold')
 # soft crimson smoke remains behind the helmet, separate from the text
 smoke=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(smoke)
 for i in range(9):
  x=(i*191+57)%1180-50;y=1650+(i%3)*80+35*math.sin(t+i)
  sd.ellipse((x-160,y-160,x+160,y+160),fill=(112,0,22,90))
 im.alpha_composite(smoke.filter(ImageFilter.GaussianBlur(40)))
 x=lerp(500,540,p(19.4,20.2,t));y=lerp(1660,1370,p(19.4,20.2,t))
 put(im,HELMET,x,y,800)
 return im

def frame(i):
 t=i/FPS
 if t<2.38:im=opening(t)
 elif t<6.4:im=gallery(t)
 elif t<9.0:im=bold_statement(t)
 elif t<12.5:im=vision(t)
 elif t<14.4:im=ideas(t)
 elif t<19.4:im=story(t)
 else:im=ending(t)
 return im.convert('RGB')

def main():
 OUT.parent.mkdir(parents=True,exist_ok=True)
 proc=subprocess.Popen([ffmpeg(),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT)],stdin=subprocess.PIPE)
 try:
  for i in range(1380):
   proc.stdin.write(frame(i).tobytes())
   if i%120==0:print(f'{i}/1380 frames',flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('render failed')
 finally:
  if proc.poll() is None:proc.kill();proc.wait()
 print('Wrote',OUT)
if __name__=='__main__':main()
