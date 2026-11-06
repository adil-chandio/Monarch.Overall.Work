#!/usr/bin/env python3
"""MONARCH reference 01: frame-based reconstruction. Provide the original reference
as --reference for its soundtrack. Images, shapes and typography are rebuilt here.
Example: python3 showreel/seven/render_01.py --reference /path/to/01.mp4
"""
import argparse, math, subprocess, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ffbin import ffmpeg
W,H,FPS=1276,718,30
FONT=ROOT/'showreel/v2/assets/Poppins-Bold.ttf'
OUT=ROOT/'public/demo/monarch-reference-01.mp4'

# Smooth, reference-timed pose interpolation. X/Y are the body centre; the lens
# points in direction angle degrees clockwise from vertical.
POSE=[(0,638,900,0),(.36,638,800,0),(.5,638,617,0),(.65,638,324,0),(.82,638,220,0),(1.03,638,174,-30),(1.18,638,172,0),(1.4,638,263,0),(1.65,638,563,0),(1.78,638,560,0),(2.03,638,382,0),(2.2,638,369,0),(2.5,638,396,0),(2.63,638,396,0),(3.16,320,402,117),(3.4,310,399,117),(3.55,319,397,117),(4.13,966,173,242),(4.4,979,168,242),(4.52,974,170,242),(5.06,253,360,90),(5.25,250,360,90),(5.35,260,360,90),(5.78,1193,360,90),(6.01,1220,360,90),(6.08,1220,360,90),(6.75,-65,360,90)]
def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
def pose(t):
 for a,b in zip(POSE,POSE[1:]):
  if a[0]<=t<=b[0]:
   f=ease((t-a[0])/(b[0]-a[0]));return tuple(a[i]+(b[i]-a[i])*f for i in (1,2,3))
 return POSE[-1][1:]

def glyph(text, width, height, outline=False):
 font=ImageFont.truetype(str(FONT),160)
 bbox=font.getbbox(text,stroke_width=3)
 im=Image.new('L',(bbox[2]-bbox[0]+8,bbox[3]-bbox[1]+8),0)
 d=ImageDraw.Draw(im);d.text((4-bbox[0],4-bbox[1]),text,font=font,fill=255,stroke_width=3 if outline else 0,stroke_fill=255)
 if outline:
  inside=Image.new('L',im.size,0);ImageDraw.Draw(inside).text((4-bbox[0],4-bbox[1]),text,font=font,fill=255)
  im=Image.fromarray(np.maximum(np.asarray(im).astype(np.int16)-np.asarray(inside).astype(np.int16),0).astype(np.uint8))
 return np.array(im.resize((width,height),Image.Resampling.LANCZOS))

def paste_mask(dest, mask, x,y):
 h,w=mask.shape;x=int(x);y=int(y); l=max(x,0);r=min(x+w,W);u=max(y,0);b=min(y+h,H)
 if l<r and u<b:dest[u:b,l:r]=np.maximum(dest[u:b,l:r],mask[u-y:b-y,l-x:r-x])

# Reference final lockup is left aligned and occupies the centre ~620x190.
logo=np.zeros((H,W),np.uint8)
paste_mask(logo,glyph('the',205,69,True),353,230)
paste_mask(logo,glyph('MONARCH',616,55),353,306)
paste_mask(logo,glyph('STUDIO',440,56,True),353,366)
# The original I/dot is a solid graphic accent through the bottom row.
cv2.rectangle(logo,(685,355),(703,420),255,-1)
cv2.rectangle(logo,(800,404),(819,420),255,-1)
words={s:glyph(s,w,49) for s,w in [('THE',135),('MONARCH',370),('STUDIO',258)]}

# Reference-like grainy diagonal light: bright red/lavender on left, deep
# black-red at right, a softly defined diagonal shadow running through it.
y,x=np.mgrid[:H,:W].astype(np.float32)
light=np.clip(1-x/W,0,1)
shadow=1/(1+np.exp(-np.clip((y-(.84*H-.46*x))/27,-20,20)))
base=np.empty((H,W,3),np.float32)
base[:,:,0]=28+215*light-35*shadow
base[:,:,1]=5+160*light**2-15*shadow
base[:,:,2]=9+170*light**2-18*shadow
rng=np.random.default_rng(1907);noise=rng.normal(0,4,(H,W)).astype(np.float32)
base=np.clip(base+noise[:,:,None],0,255).astype(np.uint8)

# Hand-drawn projector icon, antialiased, with the reference's separated
# semicircular lens and rounded body. Sprite points upward at zero degrees.
S=3
cam=Image.new('RGBA',(180*S,180*S));d=ImageDraw.Draw(cam)
d.rounded_rectangle((46*S,90*S,134*S,146*S),radius=13*S,fill=(0,0,0,255))
body=cam.resize((180,180),Image.Resampling.LANCZOS)
d.pieslice((65*S,37*S,115*S,90*S),0,180,fill=(0,0,0,255))
cam=cam.resize((180,180),Image.Resampling.LANCZOS)

def composite(frame,mask,color=(255,255,255)):
 # use OpenCV vectorised interpolation for antialiased edges
 alpha=mask.astype(np.float32)[:,:,None]/255
 return np.clip(frame*(1-alpha)+np.array(color,dtype=np.float32)*alpha,0,255).astype(np.uint8)

def draw_camera(frame,cx,cy,ang, lens=True):
 # Body centre lies at sprite (90,118); lens 90px above canvas centre.
 a=math.radians(ang); bx=28*math.sin(a);by=-28*math.cos(a)
 rotated=(cam if lens else body).rotate(-ang,resample=Image.Resampling.BICUBIC)
 anchorx=cx+bx;anchory=cy+by
 px=int(round(anchorx-90));py=int(round(anchory-90))
 rgba=np.asarray(rotated); x0=max(0,px);x1=min(W,px+180);y0=max(0,py);y1=min(H,py+180)
 if x0<x1 and y0<y1:
  sub=rgba[y0-py:y1-py,x0-px:x1-px];al=sub[:,:,3:4].astype(np.float32)/255
  frame[y0:y1,x0:x1]=(frame[y0:y1,x0:x1]*(1-al)).astype(np.uint8)
 return frame

def title(frame,name,cy=359,clip=None,color=(255,255,255)):
 m=np.zeros((H,W),np.uint8);a=words[name];paste_mask(m,a,(W-a.shape[1])/2,cy-a.shape[0]/2)
 if clip is not None:m=cv2.bitwise_and(m,clip)
 return composite(frame,m,color)

def frame_at(i):
 t=i/FPS
 f=np.full((H,W,3),255,np.uint8)
 if t<6.08:
  cx,cy,ang=pose(t)
  if t>=2.27:
   a=math.radians(ang);dx,dy=math.sin(a),-math.cos(a)
   tipx,tipy=cx+54*dx,cy+54*dy
   if 3.05 < t < 3.70:
    adjust=ease((t-3.05)/.12)*ease((3.70-t)/.12)
    tipx -= 10*adjust; tipy -= 15*adjust  # leading edge of the lens
   spread=math.radians(24)
   d1=(math.sin(a-spread),-math.cos(a-spread));d2=(math.sin(a+spread),-math.cos(a+spread))
   pts=np.array([[tipx,tipy],[tipx+3000*d1[0],tipy+3000*d1[1]],[tipx+3000*d2[0],tipy+3000*d2[1]]],np.int32)
   mask=np.zeros((H,W),np.uint8);cv2.fillConvexPoly(mask,pts,255,lineType=cv2.LINE_AA)
   f=np.where(mask[:,:,None]>0,base,f)
   f=composite(f,cv2.bitwise_and(logo,mask))
  if t>=.35: f=draw_camera(f,cx,cy,ang,lens=t>=2.24)
  # falling lens initially moves separately before connecting to the body
  if 1.49<t<2.24:
   ly=np.interp(t,[1.49,1.60,1.80,2.00,2.20,2.24],[180,130,95,105,279,340])
   cv2.ellipse(f,(638,int(ly)),(25,25),0,0,180,(0,0,0),-1,cv2.LINE_AA)
  return f
 dark=np.array([99,5,12],np.uint8)
 if t<7.2:
  cx,cy,ang=pose(t);edge=int(np.clip(cx+55,0,W));f[:,edge:]=dark
  clip=np.zeros((H,W),np.uint8);clip[:,edge:]=255
  f=title(f,'THE',clip=clip); f=draw_camera(f,cx,cy,90) if t<6.78 else f
  return f
 if t<8.0:
  # A white field pushes down over the red field.
  f[:]=dark
  p=ease((t-7.2)/.38);edge=int(H*p);f[:edge]=255
  clip=np.zeros((H,W),np.uint8);clip[:edge]=255
  f=title(f,'MONARCH',cy=int(-30+389*p),clip=clip,color=(0,0,0))
  if t<7.58:
   clip[:]=0;clip[edge:]=255;f=title(f,'THE',cy=int(359+H*p),clip=clip)
  return f
 if t<8.67:
  # Dark red panel sweeps from right to left, covering the white card.
  p=ease((t-8.0)/.22);edge=int(W*(1-p));f[:,edge:]=dark
  clip=np.zeros((H,W),np.uint8);clip[:,edge:]=255;f=title(f,'STUDIO',clip=clip)
  clip[:]=0;clip[:,:edge]=255;f=title(f,'MONARCH',clip=clip,color=(0,0,0))
  return f
 # Final gradient panel slides in from the top, bringing in the lockup.
 p=ease((t-8.67)/.35);edge=int(H*p)
 f[:]=dark;f[:edge]=base[:edge]
 f=title(f,'STUDIO',cy=int(359+H*p))
 m=np.zeros((H,W),np.uint8);m[:edge]=logo[:edge];f=composite(f,m)
 return f

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--reference',required=True);args=ap.parse_args()
 OUT.parent.mkdir(parents=True,exist_ok=True)
 temp=OUT.with_suffix('.silent.mp4')
 cmd=[ffmpeg(),'-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(temp)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for i in range(330):
   proc.stdin.write(frame_at(i).tobytes())
   if i%30==0: print(f'{i}/330 frames',flush=True)
  proc.stdin.close();rc=proc.wait()
  if rc:raise RuntimeError('video encoder failed')
  # Copy source audio unchanged. Stop at the 11-second video duration.
  subprocess.run([ffmpeg(),'-y','-v','error','-i',str(temp),'-i',args.reference,'-map','0:v:0','-map','1:a:0','-c','copy','-t','11','-movflags','+faststart',str(OUT)],check=True)
 finally:
  if proc.poll() is None:proc.kill();proc.wait()
  temp.unlink(missing_ok=True)
 print('Wrote',OUT)
if __name__=='__main__':main()
