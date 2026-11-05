#!/usr/bin/env python3
"""Rebuild reference 02 at its native timing; supply user's reference for audio.
python3 showreel/seven/render_02.py --reference /path/to/02.mp4
"""
from pathlib import Path
import argparse, math, subprocess, sys
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ffbin import ffmpeg
W,H,FPS=720,1280,30
OUT=ROOT/'public/demo/monarch-reference-02.mp4'
REG=ROOT/'showreel/v2/assets/Poppins-Medium.ttf'
BOLD=ROOT/'showreel/v2/assets/Poppins-Bold.ttf'
ITAL=ROOT/'showreel/seven/assets/InstrumentSerif-Italic.ttf'
RED=(205,0,24); BLACK=(8,8,10); LIGHT=(255,241,242); WHITE=(255,255,255)
@lru_cache(None)
def font(size,kind='r'):
 return ImageFont.truetype(str({'r':REG,'b':BOLD,'i':ITAL}[kind]),size)
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
def ease(a,b,t):return smooth((t-a)/(b-a))
def lerp(a,b,p):return a+(b-a)*p
def text(d,xy,s,size=36,fill=BLACK,kind='r',anchor='mm',stroke=0):
 d.text(xy,s,font=font(size,kind),fill=fill,anchor=anchor,stroke_width=stroke)
def centered_pair(d,y,left,right,size=53,color=RED):
 f=font(size);a=d.textlength(left,font=f);b=d.textlength(right,font=f);x=(W-a-b)/2
 text(d,(x,y),left,size,anchor='lm');text(d,(x+a,y),right,size,fill=color,anchor='lm')
def rounded(d,rect,r,fill,outline=None,width=1):d.rounded_rectangle(tuple(map(int,rect)),r,fill=fill,outline=outline,width=width)
def corners(d,rect,col=RED,length=128,width=4):
 x0,y0,x1,y1=rect
 for x,y,sx,sy in [(x0,y0,1,1),(x1,y0,-1,1),(x0,y1,1,-1),(x1,y1,-1,-1)]:
  d.line([(x+sx*length,y),(x,y),(x,y+sy*length)],fill=col,width=width)

def glow(size=430):
 im=Image.new('RGBA',(size,size));d=ImageDraw.Draw(im);d.ellipse((90,90,size-90,size-90),outline=(225,20,35,35),width=50)
 return im.filter(ImageFilter.GaussianBlur(24))
GLOW=glow(440)
def addglow(im,cx,cy):im.paste(GLOW,(int(cx-220),int(cy-220)),GLOW)

def icon_person(d,cx,cy,scale,col):
 r=19*scale;d.ellipse((cx-r,cy-42*scale-r,cx+r,cy-42*scale+r),fill=col)
 d.pieslice((cx-34*scale,cy-23*scale,cx+34*scale,cy+37*scale),180,360,fill=col)

def clock(im,t):
 d=ImageDraw.Draw(im); p=ease(1.27,1.75,t)
 shift=int((1-p)*260);box=(-1100,320+shift,900,2180+shift)
 d.arc(box,270,350,fill=RED,width=6)
 # tick marks follow the upper edge of the giant clock face
 cx,cy=-100,1250+shift; rx,ry=1000,930
 for i in range(43):
  a=math.radians(263+i*1.1);x=cx+rx*math.cos(a);y=cy+ry*math.sin(a)
  dx,dy=math.cos(a),math.sin(a);l=22 if i%10==0 else 10
  d.line((x,y,x-dx*l,y-dy*l),fill=BLACK if i%10==0 else (219,219,219),width=3 if i%10==0 else 1)
 for deg in (274,287,300,313):
  a=math.radians(deg);x=cx+rx*math.cos(a);y=cy+ry*math.sin(a)
  d.ellipse((x-9,y-9,x+9,y+9),fill=WHITE,outline=BLACK,width=3);d.ellipse((x-4,y-4,x+4,y+4),fill=RED)
 # slender black pointer and faceted cut-out, as in the reference
 pivot=(45,990+shift);tip=(380,320+shift)
 d.polygon([(-38,1115+shift),(20,990+shift),(286,458+shift),(316,463+shift),(66,1007+shift)],fill=BLACK)
 d.polygon([(291,462+shift),(267,432+shift),(308,405+shift),(328,356+shift),(325,414+shift)],fill=BLACK)
 d.polygon([(280,429+shift),(307,412+shift),(312,438+shift),(280,461+shift)],fill=WHITE)
 d.line((304,411+shift,380,320+shift),fill=BLACK,width=9)
 d.ellipse((pivot[0]-37,pivot[1]-37,pivot[0]+37,pivot[1]+37),fill=BLACK)
 d.ellipse((pivot[0]-19,pivot[1]-19,pivot[0]+19,pivot[1]+19),fill=RED)
 if t>1.58:
  text(d,(434,972),'Because',45,anchor='mm')
 if t>1.74:
  text(d,(439,1026),'every second',70,RED,'i')
  text(d,(434,1074),'A clear message gives your audience',17)
  text(d,(434,1093),'a reason to stop and understand.',17)

def audience(im,t):
 d=ImageDraw.Draw(im);p=ease(2.75,3.12,t);s=1-p
 corners(d,(70,207+int(s*70),650,1028-int(s*70)),length=125,width=4)
 text(d,(360,388),'Your audience',53)
 if t>3.12:text(d,(360,444),'decides',70,RED,'i')
 if t>3.0:
  for x,scale,color in [(124,.75,(217,78,87)),(222,1.,RED),(360,1.28,BLACK),(498,1.,RED),(598,.75,(217,78,87))]:icon_person(d,x,681,scale,color)
  corners(d,(298,544,425,703),length=19,width=3)
 if t>3.2:
  text(d,(360,810),'Your audience spends seconds deciding',19)
  text(d,(360,834),'whether your message is worth attention.',19)

def service_card(im,x,y,title,desc,delay,t):
 p=ease(delay,delay+.28,t)
 if p<=0:return
 y+=int((1-p)*55);d=ImageDraw.Draw(im)
 rounded(d,(x,y,x+185,y+200),24,WHITE,(217,217,222),3)
 d.ellipse((x+16,y+18,x+52,y+54),fill=RED)
 text(d,(x+34,y+36),'M',19,WHITE,'b')
 text(d,(x+61,y+28),title,12,BLACK,'b',anchor='lm')
 text(d,(x+61,y+45),'MONARCH STUDIO',9,(135,135,135),anchor='lm')
 for j,line in enumerate(desc):text(d,(x+15,y+82+j*18),line,12,BLACK,anchor='lm')
 for j in range(5):d.ellipse((x+17+j*18,y+172,x+25+j*18,y+180),fill=RED)

def testimonials(im,t):
 d=ImageDraw.Draw(im)
 for x in [244,356,468]:
  text(d,(x,620),'?',175,(251,234,235),'r')
 text(d,(360,650),'Make it understood',54)
 service_card(im,70,255,'BRAND STRATEGY',['Clear thinking.','A sharper story.','A focused direction.'],4.67,t)
 service_card(im,505,360,'MOTION DESIGN',['Visuals in motion.','Made to connect.','Built to be remembered.'],5.02,t)
 service_card(im,143,792,'BRAND IDENTITY',['Distinctive design.','One clear voice.','Every detail matters.'],5.28,t)

def timer(im,t):
 d=ImageDraw.Draw(im); p=ease(6.30,6.48,t);scale=0.7+0.3*p; r=int(140*scale);cx=360;cy=640
 d.arc((cx-r,cy-r,cx+r,cy+r),0,359,fill=(210,210,210),width=21)
 end=int(-90+270*ease(6.4,7.1,t));d.arc((cx-r,cy-r,cx+r,cy+r),-90,end,fill=RED,width=21)
 number=max(0,10-int(max(0,t-6.42)*12))
 text(d,(cx,cy),str(number),104)
 text(d,(cx,cy+185),'Seconds to connect',43)

def icon_hex(d,cx,cy,kind):
 # Simple line icons in place of the original's third-party icon artwork.
 if kind==0:
  d.ellipse((cx-50,cy-50,cx+50,cy+50),outline=WHITE,width=4)
  for dx in [-22,0,22]:
   d.ellipse((cx+dx-10,cy-22,cx+dx+10,cy-2),outline=WHITE,width=3)
   d.arc((cx+dx-16,cy, cx+dx+16,cy+32),180,360,fill=WHITE,width=3)
  d.line((cx-57,cy,cx-46,cy),fill=WHITE,width=4);d.line((cx+46,cy,cx+57,cy),fill=WHITE,width=4)
 elif kind==1:
  d.ellipse((cx-49,cy-49,cx+49,cy+49),outline=WHITE,width=4)
  d.polygon([(cx,cy-40),(cx-19,cy-7),(cx-17,cy+19),(cx+17,cy+19),(cx+19,cy-7)],outline=WHITE,width=4)
  d.ellipse((cx-7,cy-17,cx+7,cy-3),outline=WHITE,width=3)
  d.line((cx-12,cy+27,cx,cy+42,cx+12,cy+27),fill=WHITE,width=3)
 else:
  d.line((cx-49,cy+43,cx+48,cy+43),fill=WHITE,width=4)
  for x,h in [(-32,25),(-6,45),(20,67)]:d.rectangle((cx+x,cy+40-h,cx+x+17,cy+40),outline=WHITE,width=4)
  d.line((cx-46,cy+3,cx-20,cy-12,cx,cy-4,cx+30,cy-35),fill=WHITE,width=4)
  d.line((cx+20,cy-35,cx+30,cy-35,cx+30,cy-24),fill=WHITE,width=3)

def hexagon(im,cx,cy,label,which,t,start):
 p=ease(start,start+.34,t)
 if p<=0:return
 d=ImageDraw.Draw(im);r=116*p;pts=[]
 for a in [-90,-30,30,90,150,210]:
  v=math.radians(a);pts.append((cx+math.cos(v)*r,cy+math.sin(v)*r))
 d.polygon(pts,fill=RED)
 if p>.8:
  d.line([pts[0],pts[1]],fill=BLACK,width=5);d.line([pts[2],pts[3]],fill=BLACK,width=5);d.line([pts[4],pts[5]],fill=BLACK,width=5)
  icon_hex(d,cx,cy,which)
  if which==0:
   d.line((cx,cy-115,cx,cy-185,cx-78,cy-258),fill=BLACK,width=3);text(d,(cx-60,cy-279),label,24)
  elif which==1:
   d.line((cx,cy-115,cx,cy-185,cx+78,cy-258),fill=BLACK,width=3);text(d,(cx+80,cy-279),label,24)
  else:
   d.line((cx,cy+115,cx,cy+185,cx+78,cy+258),fill=BLACK,width=3);text(d,(cx+125,cy+279),label,24)

def pills(im,t):
 addglow(im,150+55*math.sin(t*1.3),-40);addglow(im,550+60*math.sin(t*1.5),1330)
 d=ImageDraw.Draw(im)
 entries=[(14.05,70,450,298,70,'Built with clarity',True),(14.75,396,450,245,70,'Sharper',False),(15.38,70,566,249,63,'More intentional',False),(16.28,327,564,351,70,'Made to connect',True),(17.55,70,671,431,62,'Designed to move people',True),(19.25,233,766,460,57,'Every detail matters',False)]
 for k,(start,x,y,w,h,s,col) in enumerate(entries):
  p=ease(start,start+.4,t)
  if not p:continue
  xx=x+int((1-p)*(-260 if k%2==0 else 300))
  rounded(d,(xx,y,xx+w,y+h),h//2,RED if col else WHITE, None if col else BLACK,2)
  text(d,(xx+w/2,y+h/2),s,26 if len(s)<22 else 22,WHITE if col else BLACK)

def frame(t):
 im=Image.new('RGB',(W,H),WHITE);d=ImageDraw.Draw(im)
 if t<1.27:
  d.ellipse((-340,-340,310,310),outline=(240,196,200),width=3)
  d.ellipse((520,999,920,1399),outline=(240,196,200),width=3)
  if t>.35:
   if t<.78:text(d,(360,640),'Attention',56)
   else:
    addglow(im,500,650);d=ImageDraw.Draw(im)
    centered_pair(d,640,'Attention is ','valuable.',49)
    for x,y,dt in [(585,590,.8),(500,700,.93),(600,720,1.05)]:
     if t>dt:text(d,(x,y),'$',18,RED)
 elif t<2.75:clock(im,t)
 elif t<4.35:audience(im,t)
 elif t<6.30:testimonials(im,t)
 elif t<7.32:timer(im,t)
 elif t<11.27:
  hexagon(im,225,535,'Missed connections',0,t,7.32)
  hexagon(im,466,535,'Lost momentum',1,t,8.20)
  hexagon(im,354,753,'Missed opportunities',2,t,9.72)
 elif t<13.90:
  if t<11.8:s='Brands'
  elif t<12.18:s='that'
  elif t<12.75:s='lead.'
  elif t<13.05:s=''
  else:s='Win attention.'
  if s:
   addglow(im,360,640);d=ImageDraw.Draw(im)
   text(d,(360,640),s,70 if t>=13.05 else 52,BLACK if t>=13.05 else RED,'i' if t>=13.05 else 'r')
 elif t<21.35:pills(im,t)
 elif t<24.25:
  addglow(im,510,640);d=ImageDraw.Draw(im)
  if t<23.05:
   s='Because clarity builds connection.';n=int(len(s)*ease(21.43,22.95,t));text(d,(360,640),s[:n],32)
  else:
   p=ease(23.05,23.45,t);text(d,(130-int(280*p),640),'Because clarity builds',31,(175,175,175))
   text(d,(430,640),'Make it MONARCH.',51,BLACK,'r')
   if t>23.27:d.arc((205,563,677,717),-80,int(-80+360*ease(23.27,23.85,t)),fill=RED,width=4)
 else:
  d=ImageDraw.Draw(im);x=360;y=625
  # original, bespoke M emblem replaces the reference's creator logo
  d.polygon([(x-56,y+24),(x-42,y-29),(x-17,y-29),(x,y-3),(x+17,y-29),(x+42,y-29),(x+56,y+24),(x+30,y+24),(x+23,y-4),(x,y+24),(x-23,y-4),(x-30,y+24)],fill=BLACK)
  d.polygon([(x-12,y-42),(x,y-52),(x+12,y-42),(x,y-33)],fill=RED)
  text(d,(360,686),'MONARCH',24,BLACK,'b')
 return im

def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',required=True);args=p.parse_args()
 OUT.parent.mkdir(parents=True,exist_ok=True);temp=OUT.with_suffix('.silent.mp4')
 enc=subprocess.Popen([ffmpeg(),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(temp)],stdin=subprocess.PIPE)
 try:
  for i in range(786):
   enc.stdin.write(frame(i/FPS).tobytes())
   if i%90==0: print(f'{i}/786',flush=True)
  enc.stdin.close()
  if enc.wait():raise RuntimeError('video render failed')
  subprocess.run([ffmpeg(),'-y','-v','error','-i',str(temp),'-i',args.reference,'-map','0:v:0','-map','1:a:0','-c','copy','-t','26.2','-movflags','+faststart',str(OUT)],check=True)
 finally:
  if enc.poll() is None:enc.kill();enc.wait()
  temp.unlink(missing_ok=True)
 print('Wrote',OUT)
if __name__=='__main__':main()
