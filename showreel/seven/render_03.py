#!/usr/bin/env python3
"""Reference 03: procedural type/eye animation; reference audio passed at build time.
python3 showreel/seven/render_03.py --reference /path/to/03.mp4
"""
from pathlib import Path
from functools import lru_cache
import argparse, math, subprocess, sys
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ffbin import ffmpeg
W,H,FPS=1280,720,30
OUT=ROOT/'public/demo/monarch-reference-03.mp4'
INTER=ROOT/'showreel/seven/assets/Inter.ttf'; OSWALD=ROOT/'showreel/seven/assets/Oswald.ttf'; BOLD=ROOT/'showreel/v4/vendor/Montserrat-Black.ttf'
BLACK=(0,0,0);WHITE=(255,255,255);RED=(149,0,9)
def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
def p(a,b,t):return ease((t-a)/(b-a))
def mix(a,b,k):return a+(b-a)*k
@lru_cache(None)
def font(size,kind='normal'):
 return ImageFont.truetype(str({'normal':INTER,'bold':BOLD,'cond':OSWALD}[kind]),size)
# Hand-built satin-like background; soft diagonal highlights, not reference imagery.
y,x=np.mgrid[0:H,0:W].astype(np.float32); coord=x+y*1.12
v=np.full((H,W),212.,np.float32)
for u in [-290,80,450,820,1190,1560,1930,2300]:v+=40*np.exp(-((coord-u)/100)**2)
v+=5*(1-x/W);v=np.clip(v,0,254).astype(np.uint8)
BG=Image.fromarray(np.stack([v,v,v],2),'RGB')

@lru_cache(None)
def text_image(s,size,kind='normal'):
 f=font(size,kind);bbox=f.getbbox(s,stroke_width=0)
 im=Image.new('L',(bbox[2]-bbox[0]+8,bbox[3]-bbox[1]+8),0)
 ImageDraw.Draw(im).text((4-bbox[0],4-bbox[1]),s,font=f,fill=255)
 return im.crop(im.getbbox())

def put_text(im,s,center,size,kind='normal',color=BLACK,alpha=255,shadow=False,width=None):
 if not s:return
 mask=text_image(s,size,kind)
 if width is not None:
  mask=mask.resize((int(width),mask.height),Image.Resampling.LANCZOS)
 if alpha<255:mask=mask.point(lambda z:z*max(0,min(alpha,255))//255)
 X=int(center[0]-mask.width/2);Y=int(center[1]-mask.height/2)
 if shadow:
  pad=75
  sh=Image.new('L',(mask.width+2*pad,mask.height+2*pad));sh.paste(mask,(pad,pad))
  sh=sh.filter(ImageFilter.GaussianBlur(20)).point(lambda z:int(z*.58))
  im.paste((0,0,0),(X-pad-20,Y-pad+23),sh)
 im.paste(color,(X,Y),mask)

def dashed(draw,a,b,color=(104,104,104),width=2,dash=13,gap=9):
 dx=b[0]-a[0];dy=b[1]-a[1];distance=math.hypot(dx,dy)
 if distance<.01:return
 dx/=distance;dy/=distance
 s=0
 while s<distance:
  z=min(distance,s+dash);draw.line((a[0]+dx*s,a[1]+dy*s,a[0]+dx*z,a[1]+dy*z),fill=color,width=width);s+=dash+gap

def entry(t):
 im=BG.copy();d=ImageDraw.Draw(im)
 if t<1.16:
  # hairline registration marks stretch from a central cross and rotate upright
  q=p(.12,.85,t);angle=mix(-.27,0,q);spread=1700*q
  vx,vy=math.cos(angle),math.sin(angle)
  dashed(d,(640-spread*vx,360-spread*vy),(640+spread*vx,360+spread*vy),width=2)
  if t>.31:
   a=angle+math.pi/2
   dashed(d,(640-spread*math.cos(a),360-spread*math.sin(a)),(640+spread*math.cos(a),360+spread*math.sin(a)),width=2)
  # a soft contact shadow for the tiny black x
  sh=Image.new('L',(80,80));dd=ImageDraw.Draw(sh);dd.line((25,25,45,45),fill=190,width=4);dd.line((45,25,25,45),fill=190,width=4)
  im.paste((0,0,0),(610,343),sh.filter(ImageFilter.GaussianBlur(9)))
  d=ImageDraw.Draw(im);d.line((631,351,649,369),fill=BLACK,width=3);d.line((649,351,631,369),fill=BLACK,width=3)
 else:
  z=p(1.15,1.55,t);h=int(mix(16,154,z));s=max(14,int(h*1.4))
  # alignment guides correspond to the glyph box, then disappear as it moves
  if t<2.35:
   off=int(mix(5,78,z));top=360-int(h/2);bot=360+int(h/2)
   for xx in (640-off,640+off):dashed(d,(xx,0),(xx,H),width=2)
   for yy in (top,bot):dashed(d,(0,yy),(W,yy),width=2)
  put_text(im,'Hi',(640,360),s,'normal',BLACK,shadow=True)
 return im

def we(t):
 im=BG.copy();amount=p(2.33,2.58,t);cx=mix(800,505,amount);size=244
 put_text(im,'We’re',(cx,360),size,'normal',BLACK,shadow=True,width=360)
 return im

def eye_mask(halfheight,rx,power):
 xx=np.arange(W,dtype=np.float32);inside=np.maximum(0,1-((xx-W/2)/rx)**2)
 edge=halfheight*inside**power
 yy=np.arange(H,dtype=np.float32)[:,None]
 return np.uint8((np.abs(yy-H/2)<=edge[None,:])*255)

@lru_cache(None)
def shadow_ball():
 im=Image.new('L',(620,620));ImageDraw.Draw(im).ellipse((110,110,510,510),fill=150)
 return im.filter(ImageFilter.GaussianBlur(45))

def draw_eye(t):
 h=mix(360,153,p(3.42,5.70,t));rx=mix(760,640,p(3.42,5.70,t))
 mask=Image.fromarray(eye_mask(h,rx,mix(.5,1.0,p(3.42,5.7,t))),'L')
 surface=Image.blend(BG,Image.new('RGB',(W,H),(250,250,250)),p(4.15,5.4,t))
 if t>=4.15:
  # Saturn-like eye with solid black rim, colored iris and key light.
  d=ImageDraw.Draw(surface);e=p(4.14,4.72,t);r=mix(17,212,e);cx=mix(640,452,p(5.03,5.72,t));cy=360
  sh=shadow_ball().resize((int(r*3.1),int(r*3.1)),Image.Resampling.LANCZOS)
  surface.paste((0,0,0),(int(cx-r*1.5+55),int(cy-r*1.5+45)),sh)
  d=ImageDraw.Draw(surface);d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=BLACK)
  if r>40:
   ir=r*.77;red=p(5.05,5.50,t);col=(int(mix(120,145,red)),int(mix(120,0,red)),int(mix(120,7,red)))
   d.ellipse((cx-ir,cy-ir,cx+ir,cy+ir),fill=col)
   pupil=mix(r*.23,r*1.55,p(6.38,6.73,t));d.ellipse((cx-pupil,cy-pupil,cx+pupil,cy+pupil),fill=BLACK)
   hl=r*.21;d.ellipse((cx+r*.51-hl,cy-r*.55-hl,cx+r*.51+hl,cy-r*.55+hl),fill=WHITE)
 else:
  put_text(surface,'MONARCH',(640,368),108,'bold',BLACK,shadow=True,width=700)
 im=Image.new('RGB',(W,H),BLACK);im.paste(surface,(0,0),mask)
 if t>=6.56:
  # zoom into the iris until it fills the screen and transitions to copy
  z=p(6.60,7.20,t);cx=mix(452,640,z);r=mix(180,1500,z)
  d=ImageDraw.Draw(im);d.ellipse((cx-r,360-r,cx+r,360+r),fill=BLACK)
 return im

def tagline(t,im=None):
 if im is None:im=Image.new('RGB',(W,H),BLACK)
 if t<6.70:return im
 # Left-to-right build with a changing final role, same white/red hierarchy.
 your='Your';creative='Creative';role=''
 if t<7.18:
  n=max(1,int(4*p(6.70,7.05,t)));put_text(im,your[:n],(640,360),148,'cond',WHITE);return im
 if t<8.06:
  n=max(0,math.ceil(len(creative)*p(7.20,8.04,t)));right=creative[:n]
  f=font(148,'cond');dummy=ImageDraw.Draw(im);a=dummy.textlength(your,font=f);b=dummy.textlength(right,font=f);gap=30
  x=(W-a-(gap+b if right else 0))/2
  put_text(im,your,(x+a/2,360),148,'cond',WHITE)
  if right:put_text(im,right,(x+a+gap+b/2,360),148,'cond',RED)
  return im
 if t<8.75:role='Studio'
 elif t<9.55:role='Designer'
 else:role='Partner'
 f=font(148,'cond');d=ImageDraw.Draw(im);a=d.textlength(your,font=f);b=d.textlength(creative,font=f);c=d.textlength(role,font=f);gap=30;scale=min(1,960/(a+b+c+gap*2))
 # uniform smaller font if needed to retain the reference margins
 if scale<1:
  sz=int(148*scale);f=font(sz,'cond');a=d.textlength(your,font=f);b=d.textlength(creative,font=f);c=d.textlength(role,font=f);gap=int(30*scale)
 else:sz=148
 x=(W-a-b-c-2*gap)/2
 put_text(im,your,(x+a/2,360),sz,'cond',WHITE)
 put_text(im,creative,(x+a+gap+b/2,360),sz,'cond',RED)
 put_text(im,role,(x+a+gap+b+gap+c/2,360),sz,'cond',WHITE)
 return im

def frame(i):
 t=i/FPS
 if t<2.33:return entry(t)
 if t<3.40:return we(t)
 if t<6.70:return draw_eye(t)
 if t<7.07:return tagline(t,draw_eye(t))
 if t<10.90:return tagline(t)
 im=BG.copy()
 if t<11.60:
  q=p(11.12,11.6,t);put_text(im,'MONARCH',(640,360),95,'cond',BLACK,alpha=int(255*(1-q)),width=320)
 if t>11.40:
  a=int(255*p(11.4,11.75,t));d=ImageDraw.Draw(im);c=(255-a,255-a,255-a)
  d.line((631,351,649,369),fill=c,width=3);d.line((649,351,631,369),fill=c,width=3)
 return im

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--reference',required=True);args=ap.parse_args()
 OUT.parent.mkdir(parents=True,exist_ok=True);tmp=OUT.with_suffix('.silent.mp4')
 proc=subprocess.Popen([ffmpeg(),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
 try:
  for i in range(360):
   proc.stdin.write(frame(i).tobytes())
   if i%30==0:print(f'{i}/360 frames',flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('video encode failed')
  subprocess.run([ffmpeg(),'-y','-v','error','-i',str(tmp),'-i',args.reference,'-map','0:v:0','-map','1:a:0','-c','copy','-t','12','-movflags','+faststart',str(OUT)],check=True)
 finally:
  if proc.poll() is None:proc.kill();proc.wait()
  tmp.unlink(missing_ok=True)
 print('Wrote',OUT)
if __name__=='__main__':main()
