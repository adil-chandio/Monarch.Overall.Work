"""Illustrated recreation of a user-supplied farm outbreak opening.
All visuals are drawn from primitives per frame; no source frames or source audio.
Narration is original paraphrase, not a verified reference transcript.
"""
from pathlib import Path
import argparse,math,subprocess,tempfile,wave,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parent;S=1.5;W,H=960,540;FPS=30;DUR=60
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F={size:ImageFont.truetype(FONT,round(size*S)) for size in (6,7,8,9,10,11,12,14,16,19)}
INK=(15,15,20,255);CREAM=(233,225,207,255);DARK=(14,16,18,255);GREEN=(150,190,112,255)
def v(x):return round(x*S)
def box(b):return tuple(v(q) for q in b)
def ellipse(d,b,fill,outline=None,width=1):d.ellipse(box(b),fill=fill,outline=outline,width=max(1,v(width)))
def rectangle(d,b,fill,outline=None,width=1):d.rectangle(box(b),fill=fill,outline=outline,width=max(1,v(width)))
def rounded(d,b,r,fill,outline=None,width=1):d.rounded_rectangle(box(b),v(r),fill=fill,outline=outline,width=max(1,v(width)))
def line(d,pts,fill,width=1):d.line([(v(x),v(y)) for x,y in pts],fill=fill,width=max(1,v(width)),joint='curve')
def poly(d,pts,fill,outline=None,width=1):d.polygon([(v(x),v(y)) for x,y in pts],fill=fill,outline=outline,width=max(1,v(width)))
def text(d,p,s,size=9,fill=CREAM,anchor='mm'):d.text((v(p[0]),v(p[1])),s,font=F[size],fill=fill,anchor=anchor)
def clamp(x):return max(0,min(1,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def lerp(a,b,u):return a+(b-a)*u
def anim(t,keys):
 if t<=keys[0][0]:return keys[0][1]
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if t<=b:return lerp(x,y,ease((t-a)/(b-a)))
 return keys[-1][1]
def grad(im,c0,c1):
 d=ImageDraw.Draw(im)
 for y in range(0,360,2):
  u=y/360;c=tuple(round(lerp(c0[i],c1[i],u)) for i in range(3))+(255,);rectangle(d,(0,y,640,y+2),c)
def glow(im,x,y,r,color,alpha=120,blur=35):
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer);ellipse(d,(x-r,y-r,x+r,y+r),(*color,alpha));im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(v(blur))))
def sky(im,sun=335,suny=180):
 grad(im,(90,71,102),(209,145,115));glow(im,sun,suny,70,(255,201,147),180,45)
 d=ImageDraw.Draw(im);ellipse(d,(sun-23,suny-23,sun+23,suny+23),(255,219,164,255))
 cloud=Image.new('RGBA',(W,H));cd=ImageDraw.Draw(cloud)
 for x,y,rx in [(150,75,60),(280,64,63),(450,80,78),(530,61,75),(314,90,83)]:ellipse(cd,(x-rx,y-3,x+rx,y+3),(238,192,173,28))
 im.alpha_composite(cloud.filter(ImageFilter.GaussianBlur(v(3))));d=ImageDraw.Draw(im)
 # Distant irregular trees and spires form a layered skyline.
 for j in range(41):
  x=j*17-8;h=15+(j*29%27);ellipse(d,(x,190-h,x+25,202),(45,38,49,255))
  if j%3==0:poly(d,[(x+7,195),(x+13,155-(j*13%12)),(x+18,195)],(39,35,45,255))
 rectangle(d,(0,198,640,229),(50,43,49,255))
 return im

def field(im,ground=202,t=0):
 d=ImageDraw.Draw(im);rectangle(d,(0,ground,640,340),(62,76,52,255))
 for j in range(20):
  y=ground+j*7;line(d,[(0,y),(640,y)],(68,81,55,255),.5)
 # Fine irregular grass creates depth without introducing a still-image plate.
 for j in range(350):
  xx=(j*137)%640; yy=ground+((j*53)%max(1,340-ground));h=1+(j%3)
  line(d,[(xx,yy),(xx+(.5 if j%2 else -.5)+.8*math.sin(t*1.2+xx*.03+yy*.02),yy-h)],(84,98,62,255),.4)
 for x in range(0,640,29):line(d,[(x,ground-8),(x,ground+18)],(42,43,38,255),1)
 for y in (ground-5,ground+2):line(d,[(0,y),(640,y)],(35,37,34,255),1)
 return im

def windows(d,x,y,lit=False):
 rectangle(d,(x,y,x+28,y+32),(24,24,27,255))
 rectangle(d,(x+3,y+3,x+25,y+29),(113,116,115,255) if not lit else (156,142,117,255))
 line(d,[(x+14,y+2),(x+14,y+31)],(27,27,29,255),2);line(d,[(x+1,y+16),(x+27,y+16)],(27,27,29,255),2)
def house(d,x,y,scale=1):
 def P(X,Y):return (x+X*scale,y+Y*scale)
 def R(x1,y1,x2,y2,c):rectangle(d,(*P(x1,y1),*P(x2,y2)),c)
 R(0,0,158,120,(94,74,73,255))
 for j in range(1,20):line(d,[P(0,j*6),P(158,j*6)],(113,87,79,255),.55*scale)
 poly(d,[P(-9,0),P(78,-55),P(167,0)],(21,19,22,255));R(116,-60,131,-25,(27,24,27,255))
 ellipse(d,(*P(73,-30),*P(85,-18)),(90,92,119,255))
 for xx in (20,105):
  for yy in (14,72):
   X,Y=P(xx,yy);windows(d,X,Y)
 R(69,81,95,120,(43,36,36,255));R(15,69,146,74,(66,52,51,255))

def barn(d,x,y):
 # warm timber boards and two sliding doors
 poly(d,[(x-5,y+2),(x+7,y-30),(x+76,y-57),(x+149,y-30),(x+160,y+2)],(19,18,22,255))
 rectangle(d,(x,y,x+155,y+119),(121,64,61,255))
 for k in range(1,20):line(d,[(x+k*8,y+2),(x+k*8,y+118)],(151,79,70,255),.7)
 rectangle(d,(x+35,y+38,x+121,y+119),(149,85,77,255),(217,185,162,255),2)
 line(d,[(x+78,y+38),(x+78,y+119)],(222,190,165,255),2)
 for a,b in ((35,78),(78,121)):
  line(d,[(x+a,y+39),(x+b,y+119)],(223,187,161,255),1.5);line(d,[(x+b,y+39),(x+a,y+119)],(223,187,161,255),1.5)
 rectangle(d,(x+61,y-28,x+92,y-1),(33,28,29,255),(193,162,143,255),1)
 line(d,[(x+62,y-27),(x+91,y-2)],(207,175,151,255),1);line(d,[(x+91,y-27),(x+62,y-2)],(207,175,151,255),1)

def silo(d,x,y):
 rounded(d,(x,y,x+43,y+172),20,(48,44,45,255));rectangle(d,(x,y+20,x+43,y+172),(49,45,46,255))
 for j in range(11):line(d,[(x,y+26+j*14),(x+43,y+26+j*14)],(77,63,61,255),1)
 rectangle(d,(x+5,y+25,x+11,y+168),(67,57,55,255))

def farm(im,t,view='full'):
 sky(im,270 if view=='full' else 325);field(im,208,t);d=ImageDraw.Draw(im)
 rectangle(d,(0,291,640,340),(83,69,68,255));ellipse(d,(-120,295,740,360),(88,75,73,255))
 if view=='full':house(d,84,169);barn(d,426,172);silo(d,596,126)
 else:barn(d,432,170);silo(d,597,124)
 # Dark nearby fence posts, intentionally soft as depth cue.
 layer=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(layer)
 for x in (-9,14,615,650):rounded(ld,(x-8,145,x+8,335),6,(17,17,21,190))
 im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(v(3))))
 return im

def valley(im):
 sky(im,398,160);d=ImageDraw.Draw(im)
 poly(d,[(0,155),(90,132),(155,155),(270,142),(355,159),(480,135),(580,164),(640,152),(640,200),(0,200)],(61,54,73,255))
 rectangle(d,(0,196,640,340),(81,93,65,255))
 poly(d,[(0,236),(190,202),(310,222),(490,193),(640,213),(640,340),(0,340)],(84,102,64,255))
 poly(d,[(0,290),(220,218),(220,221),(0,295)],(137,135,108,255))
 for x,y in ((380,225),(12,232),(570,235)):
  rectangle(d,(x-9,y-9,x+9,y+8),(42,38,38,255));poly(d,[(x-13,y-9),(x,y-19),(x+13,y-9)],(27,26,31,255))
 # miniature farm at distance
 rectangle(d,(477,181,511,218),(83,68,66,255));poly(d,[(472,181),(495,164),(516,181)],(31,27,32,255));rectangle(d,(519,191,555,218),(120,68,63,255));poly(d,[(516,191),(535,180),(558,191)],(30,27,32,255))
 return im

def barn_interior(im):
 grad(im,(59,40,37),(89,66,53));d=ImageDraw.Draw(im)
 for x in range(0,640,39):
  rectangle(d,(x,20,x+37,305),(67+(x%3)*5,46+(x%3)*3,39,255));line(d,[(x+1,20),(x+1,305)],(33,27,27,255),2)
  line(d,[(x+28,20),(x+28,305)],(104,75,56,255),.8)
 for x in (15,74,175,274,373,471,571):line(d,[(x,20),(x,305)],(34,27,26,255),3)
 # Window light and translucent shaft are generated geometry, not image plates.
 win=Image.new('RGBA',(W,H));wd=ImageDraw.Draw(win)
 rectangle(wd,(335,105,439,247),(209,156,133,255));ellipse(wd,(356,190,421,255),(255,210,150,255))
 im.alpha_composite(win.filter(ImageFilter.GaussianBlur(v(1.0))))
 beam=Image.new('RGBA',(W,H));bd=ImageDraw.Draw(beam)
 poly(bd,[(355,110),(410,110),(498,306),(292,306)],(255,210,151,48))
 im.alpha_composite(beam.filter(ImageFilter.GaussianBlur(v(7))))
 d=ImageDraw.Draw(im);rectangle(d,(0,306,640,340),(85,68,53,255));line(d,[(87,228),(536,228)],(31,27,26,255),5);line(d,[(87,264),(536,264)],(31,27,26,255),5)
 for i in range(6):
  x=5+i*23;rounded(d,(x,83,x+7,107),2,(94+i%3*26,105+i%2*20,116,255));rectangle(d,(x,145,x+13,165),(195,192,175,255))
 for x in (510,556,602):rectangle(d,(x,164,x+40,196),(33,27,25,255));rectangle(d,(x,187,x+40,196),(181,153,98,255))
 rounded(d,(98,275,165,307),4,(177,155,92,255));
 for x in range(104,160,15):line(d,[(x,275),(x-3,268)],(206,183,119,255),1)
 return im

def cow(im,x,y,s=1):
 d=ImageDraw.Draw(im);ellipse(d,(x-37*s,y-19*s,x+40*s,y+16*s),(12,13,18,255),(225,201,171,255),1*s)
 ellipse(d,(x-53*s,y-20*s,x-28*s,y+2*s),(15,16,21,255));ellipse(d,(x+3*s,y-14*s,x+20*s,y-2*s),(215,216,210,255));ellipse(d,(x-20*s,y+2*s,x-7*s,y+12*s),(216,215,208,255))
 for k in (-24,-12,23,33):line(d,[(x+k*s,y+9*s),(x+k*s,y+32*s)],(18,17,20,255),3*s);line(d,[(x+k*s+2*s,y+9*s),(x+k*s+2*s,y+32*s)],(216,194,166,255),1*s)
 line(d,[(x+35*s,y-10*s),(x+44*s,y+16*s)],(231,203,168,255),1*s);ellipse(d,(x-47*s,y-17*s,x-44*s,y-14*s),CREAM)

def stride_foot(x, ground, scale, t, offset, speed, period):
 """Stance foot stays in world space for a constant-speed leftward root.
 Swing advances the foot with a smooth lift. This is kinematic, not a simulation.
 """
 phase=(t / period + offset) % 1.0
 stance=.58
 stride=speed*period*stance
 if phase < stance:
  dx=-stride/2 + speed*period*phase
  lift=0
 else:
  u=(phase-stance)/(1-stance)
  dx=lerp(stride/2,-stride/2,ease(u))
  lift=math.sin(math.pi*u)*5.5*scale
 return (x+dx,ground-lift)

def knee_for(hip,foot,length,side):
 # Two-link inverse kinematics keeps the drawn legs approximately constant length.
 dx=foot[0]-hip[0];dy=foot[1]-hip[1];dist=max(.001, math.hypot(dx,dy));half=min(dist/2,length)
 h=math.sqrt(max(0,length*length-half*half));return ((hip[0]+foot[0])/2+side*(-dy/dist)*h,(hip[1]+foot[1])/2+side*(dx/dist)*h)

def person(im,x,ground,s=1,t=0,kind='farmer',action='idle',root_speed=None):
 d=ImageDraw.Draw(im);green=kind=='zombie';moving=action in ('walk','run')
 period=.78 if action=='run' else 1.05
 speed=root_speed if root_speed is not None else (27.6 if action=='run' else 16.0)
 phase=t/period; bounce=abs(math.sin(phase*2*math.pi))*1.4*s if moving else 0
 lean=(-4.0 if action=='run' else -1.1)*s if moving else 0
 hip=(x,ground-22*s-bounce);neck=(x+lean,ground-42*s-bounce);head=(neck[0]-1*s,ground-49*s-bounce)
 if moving:
  feet=[stride_foot(x,ground,s,t,offset,speed,period) for offset in (0,.5)]
 else:feet=[(x-4*s,ground),(x+4*s,ground)]
 ellipse(d,(x-14*s,ground-2*s,x+14*s,ground+3*s),(20,22,19,135))
 for i,ft in enumerate(feet):
  kn=knee_for(hip,ft,12*s,-1 if i==0 else 1)
  line(d,[hip,kn,ft],(12,13,17,255),3.7*s)
  line(d,[hip,kn,ft],(170,188,156,255) if green else (206,214,211,255),1.5*s)
  line(d,[ft,(ft[0]-3*s,ft[1])],(16,17,18,255),2*s)
 torso=(100,122,84,255) if green else ((150,164,119,255) if kind=='villager' else (164,188,192,255))
 poly(d,[(neck[0]-5*s,neck[1]),(neck[0]+5*s,neck[1]),(hip[0]+7*s,hip[1]),(hip[0]-6*s,hip[1])],torso,INK,1*s)
 if green:
  swing=math.sin(phase*2*math.pi)*2*s if moving else 0
  line(d,[(neck[0]-2*s,neck[1]+4*s),(neck[0]-11*s,neck[1]+8*s+swing),(neck[0]-16*s,neck[1]+6*s+swing)],(172,190,147,255),2*s)
 else:
  q=math.sin(phase*2*math.pi) if moving else 0
  for side in (-1,1):
   shoulder=(neck[0]+side*4*s,neck[1]+4*s);elbow=(shoulder[0]+side*4*s+q*side*5*s,shoulder[1]+9*s)
   hand=(elbow[0]+q*side*4*s,elbow[1]+6*s)
   line(d,[shoulder,elbow,hand],(210,217,209,255),2*s)
 hr=7*s;ellipse(d,(head[0]-hr-s,head[1]-hr-s,head[0]+hr+s,head[1]+hr+s),(112,143,91,255) if green else (196,157,112,255))
 ellipse(d,(head[0]-hr,head[1]-hr,head[0]+hr,head[1]+hr),(38,56,37,255) if green else (14,15,20,255))
 if kind=='farmer':
  ellipse(d,(head[0]-8*s,head[1]-9*s,head[0]+8*s,head[1]-2*s),(174,15,35,255));ellipse(d,(head[0]-3*s,head[1]-9*s,head[0]+3*s,head[1]-3*s),(241,237,223,255));line(d,[(head[0]-9*s,head[1]-2*s),(head[0]+9*s,head[1]-2*s)],(112,11,23,255),2*s)
 for dx in (-2,2):ellipse(d,(head[0]+(dx-1)*s,head[1]-s,head[0]+(dx+1)*s,head[1]+s),(217,244,158,255) if green else CREAM)
 if action=='bucket':
  rectangle(d,(x+7*s,ground-20*s,x+17*s,ground-8*s),(210,219,213,255),INK,.8*s)
  d.arc(box((x+6*s,ground-24*s,x+18*s,ground-14*s)),180,360,fill=INK,width=max(1,v(.8*s)))

def falling_villager(im,t):
 """Art-directed fall: lower centre of mass, extend hands, then settle on ground."""
 d=ImageDraw.Draw(im);u=ease((t-26.48)/.55)
 # The character carries leftward momentum through the impact.
 x=lerp(320,298,u);hip=(x,lerp(253,270,u));neck=(lerp(x-4,x-22,u),lerp(236,271,u));head=(lerp(x-5,x-30,u),lerp(230,270,u))
 feet=[(lerp(317,326,u),275),(lerp(329,342,u),275)]
 ellipse(d,(x-45,273,x+50,279),(20,22,19,130))
 for i,ft in enumerate(feet):
  kn=knee_for(hip,ft,10.5,-1 if i==0 else 1);line(d,[hip,kn,ft],INK,4);line(d,[hip,kn,ft],(203,213,207,255),1.5)
 line(d,[hip,neck],INK,11);line(d,[hip,neck],(150,164,119,255),8)
 for off in (-1,1):
  shoulder=(neck[0],neck[1]+off*2);hand=(lerp(neck[0]-6,head[0]-7,u),lerp(neck[1]+12,275,u));elbow=((shoulder[0]+hand[0])/2,(shoulder[1]+hand[1])/2-2)
  line(d,[shoulder,elbow,hand],(211,216,205,255),2)
 ellipse(d,(head[0]-7,head[1]-7,head[0]+7,head[1]+7),(196,157,112,255));ellipse(d,(head[0]-6,head[1]-6,head[0]+6,head[1]+6),INK)
 ellipse(d,(head[0]-3,head[1]-1,head[0]-1,head[1]+1),CREAM)
 # Impact dust expands and fades, rather than remaining fixed to the character.
 if 26.9<t<27.65:
  age=t-26.9;alpha=int(85*(1-age/.75));layer=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(layer)
  for j in range(7):
   px=292+(j-3)*(4+age*8);py=274-age*(3+j%3*3);r=2+age*(3+j%2)
   ellipse(ld,(px-r,py-r,px+r,py+r),(183,168,127,alpha))
  im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(v(2))))

def close_face(im,expression='surprised',t=0):
 d=ImageDraw.Draw(im);x,y,r=320,213,102
 # small shoulders behind head, warm rim and side-light
 poly(d,[(212,340),(232,323),(263,309),(377,309),(409,323),(428,340)],(153,179,187,255))
 ellipse(d,(x-r-3,y-r-3,x+r+3,y+r+3),(221,175,127,255));ellipse(d,(x-r,y-r,x+r,y+r),(13,13,20,255))
 d.arc(box((x-r+2,y-r+2,x+r-2,y+r-2)),50,145,fill=(115,91,77,255),width=v(2))
 # dark hair peeking out beneath the cap
 ellipse(d,(211,151,239,199),(126,85,54,255));ellipse(d,(401,151,429,199),(126,85,54,255))
 ellipse(d,(215,73,425,166),(179,12,38,255));ellipse(d,(269,76,371,161),(246,245,232,255))
 ellipse(d,(211,136,429,164),(144,11,30,255));ellipse(d,(312,66,328,82),(164,8,28,255))
 for ex in (282,358):
  if expression in ('surprised','alert'):
   ellipse(d,(ex-24,176,ex+24,224),(247,244,229,255));ellipse(d,(ex-16,184,ex+16,216),(15,15,20,255));ellipse(d,(ex-8,192,ex+8,208),(247,244,229,255))
  else:ellipse(d,(ex-8,192,ex+8,208),(247,244,229,255))
 if expression=='happy':d.arc(box((303,216,337,244)),5,175,fill=(247,244,229,255),width=v(4))
 elif expression=='surprised':ellipse(d,(309,235,331,266),(247,244,229,255))
 else:
  line(d,[(268,180),(294,186)],(248,244,231,255),5);line(d,[(346,186),(372,180)],(248,244,231,255),5)
  line(d,[(306,247),(314,242),(321,245),(328,240),(335,245)],(246,242,229,255),4)

def rings(im,cx,cy,t):
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
 for i in range(3):
  r=12+((t*16+i*30)%100);ellipse(d,(cx-r,cy-r,cx+r,cy+r),None,(224,207,182,max(0,52-int(r*.3))),.6)
 im.alpha_composite(layer)

def back_shoulder(im):
 """Defocused rear-of-head foreground, not a second frontal character."""
 d=ImageDraw.Draw(im)
 poly(d,[(365,345),(394,308),(439,280),(548,280),(590,307),(620,345)],(144,170,176,255))
 ellipse(d,(426,168,564,305),(9,12,16,255),(104,90,76,255),2)
 ellipse(d,(423,150,566,219),(168,14,34,255))
 ellipse(d,(420,201,570,220),(111,10,21,255))


def phone(im,t):
 d=ImageDraw.Draw(im);rounded(d,(269,58,407,329),16,(190,155,127,255));rounded(d,(273,62,403,325),14,(29,23,29,255));rounded(d,(284,105,394,145),6,(188,33,50,255))
 text(d,(339,125),'! EMERGENCY ALERT',9,(255,247,235,255))
 lines=[('REMAIN INDOORS.',.5),('AVOID PHYSICAL',1.0),('CONTACT WITH ANY',1.5),('SHOWING EXTREME',2.2),('AGGRESSION OR',2.8),('CONFUSION.',3.2)]
 for j,(s,when) in enumerate(lines):
  if t>=when:text(d,(286,168+j*13),s,8,(247,242,231,255),'lm')
 poly(d,[(382,326),(411,325),(450,354),(414,360)],(158,181,187,255),INK,1)

def vignette(im):
 return Image.composite(Image.new('RGB',(W,H),(9,8,13)),im.convert('RGB'),VIGNETTE)
def compose(t):
 im=Image.new('RGBA',(W,H));
 if t<2.033:farm(im,t)
 elif t<3.667:
  barn_interior(im);person(im,294,307,.8,t,'farmer','bucket');cow(im,435,277,.95)
 elif t<4.867:
  barn_interior(im);im=im.filter(ImageFilter.GaussianBlur(v(6)));close_face(im,'happy' if t<3.933 else 'surprised',t)
 elif t<7.967:
  farm(im,t,'barn')
  if t>5.5:rings(im,325,174,t-5.5)
 elif t<11.767:
  valley(im)
  if t>=9.2:
   d=ImageDraw.Draw(im)
   for i in range(22):ellipse(d,(100+i*11,254-i*.7,102+i*11,256-i*.7),(234,213,167,170))
   text(d,(330,229),'0.5 MILE',8,(246,224,171,255))
 elif t<15.033:
  farm(im,t);person(im,anim(t,[(11.767,451),(15.033,330)]),294,.66,t,'farmer','walk')
 elif t<18.767:
  farm(im,t,'barn');person(im,anim(t,[(15.033,400),(18.767,270)]),243,.38,t,'zombie','run')
  layer=Image.new('RGBA',(W,H));back_shoulder(layer);im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(v(3))))
 elif t<22.5:
  sky(im,470);field(im,201,t);person(im,353-27.6*(t-18.767),260,.83,t,'villager','run',27.6);person(im,540-30.8*(t-18.767),260,.83,t,'zombie','run',30.8)
 elif t<26:
  sky(im,475);field(im,201,t);person(im,320,289,2.2,t,'zombie','run');d=ImageDraw.Draw(im);text(d,(469,107),'TOO STIFF',11,(247,222,202,255));line(d,[(438,115),(345,180)],(223,110,108,255),1)
  if t>24.4:text(d,(70,280),'TOO FAST',9,(244,221,199,255));line(d,[(123,279),(315,258)],(222,112,106,255),1)
 elif t<27.8:
  sky(im,470);field(im,201,t);person(im,428-27*(t-26),275,.85,t,'zombie','run',27)
  if t<26.48:person(im,334-29*(t-26),275,.85,t,'villager','run',29)
  else:falling_villager(im,t)
 elif t<32.8:
  sky(im,468);field(im,200,t)
  for j,x in enumerate((150,280,410)):
   u=clamp((t-(27.8+j*.35))/.8);person(im,x,340-72*ease(u),.8,t+j*.3,'zombie','idle')
  d=ImageDraw.Draw(im)
  for x in range(0,640,13):line(d,[(x,340),(x+(x%5)-2,307+(x*3%15))],(39,53,39,255),.7)
 elif t<35.833:
  sky(im,470);field(im,201,t);d=ImageDraw.Draw(im)
  for x in (307,356,405,454,503,552,600):line(d,[(x,242),(x,295)],(23,24,23,255),3)
  for y in (253,276):line(d,[(306,y),(620,y)],(25,25,24,255),3)
  for j in range(6):cow(im,335+j*31,286+(j%2)*7,.42)
 elif t<38.367:
  farm(im,t);im=im.filter(ImageFilter.GaussianBlur(v(5)));close_face(im,'worried',t)
 elif t<42.333:
  farm(im,t);im=im.filter(ImageFilter.GaussianBlur(v(5)));phone(im,t-38.367)
 elif t<47.533:
  farm(im,t);im=im.filter(ImageFilter.GaussianBlur(v(5)));close_face(im,'alert',t)
 elif t<52.467:
  valley(im)
  for j,(x,y) in enumerate(((130,245),(200,240),(290,235),(396,224),(530,234))):rings(im,x,y,t-47.533+j*.17)
 else:
  farm(im,t);person(im,anim(t,[(52.467,375),(60,280)]),294,.66,t,'farmer','walk')
  if t>54:
   layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
   for j,(x,y,r) in enumerate(((40,310,46),(609,298,52))):
    ellipse(d,(x-r,y-r,x+r,y+r),(15,26,18,240))
    for ex in (x-r*.34,x+r*.34):ellipse(d,(ex-6,y-5,ex+6,y+7),(199,241,138,235))
   im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(v(5))))
 # Sparse motes and cinematic, deliberately restrained letterbox.
 d=ImageDraw.Draw(im)
 for j in range(22):
  x=(j*83+math.sin(t*.4+j)*3)%640;y=56+(j*47+t*(.6+j%3)*2)%260
  ellipse(d,(x-.7,y-.7,x+.7,y+.7),(238,209,171,90))
 out=vignette(im);d=ImageDraw.Draw(out,'RGBA');rectangle(d,(0,0,640,20),(0,0,0,255));rectangle(d,(0,340,640,360),(0,0,0,255))
 text(d,(24,33),'DAY',7,(218,207,188,220),'lm');text(d,(52,33),'1',12,(224,196,123,255),'lm')
 if t<2.033:text(d,(25,296),'◷ 6:14 AM',10,(236,225,206,230),'lm')
 if t<.4:out=Image.blend(Image.new('RGB',(W,H),(0,0,0)),out,ease(t/.4))
 return out

y,x=np.ogrid[-1:1:complex(H),-1:1:complex(W)];vg=np.clip((np.sqrt((x*.9)**2+(y*.8)**2)-.2)*.5,0,.72);VIGNETTE=Image.fromarray((vg*255).astype('uint8'),'L')

def score(path):
 sr=48000;t=np.arange(sr*DUR,dtype=np.float32)/sr;a=np.zeros_like(t);rng=np.random.default_rng(427)
 # Low drone and subtle pulsing tension; original synthesis, not reference audio.
 a+=.012*np.sin(2*np.pi*55*t)*(0.5+.5*np.sin(2*np.pi*.035*t))+.006*np.sin(2*np.pi*82.41*t)
 for at in (5.6,11.77,15.03,18.77,22.5,26,27.8,35.83,38.37,42.33,47.53,52.47,54.1):
  pos=int(at*sr);n=min(int(.35*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr
  a[pos:pos+n]+=(.014*np.sin(2*np.pi*(75*u-20*u*u))+.002*rng.standard_normal(n))*np.exp(-u*12)
 a*=np.minimum(1,np.minimum(t,60-t)).clip(0,1)
 with wave.open(str(path),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes((a*32767).astype('<i2').tobytes())
def main():
 p=argparse.ArgumentParser();p.add_argument('--stills',action='store_true');p.add_argument('--output',default='deliverables/monarch-farm-reference-recreation.mp4');args=p.parse_args()
 if args.stills:
  for t in (1,3,4,6,9,13,16,20,23,26.7,29,34,37,40,44,49,56):compose(t).save(ROOT/f'preview-{t}.jpg',quality=92)
  return
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as td:
  tmp=Path(td);video=tmp/'video.mp4';music=tmp/'score.wav';score(music)
  proc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(video)],stdin=subprocess.PIPE)
  for n in range(FPS*DUR):
   proc.stdin.write(compose(n/FPS).tobytes())
   if n%150==0:print('FRAME',n,'/',FPS*DUR,flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('visual encode failed')
  scripts=json.loads((ROOT/'script.json').read_text());inputs=[]
  for k in range(len(scripts)):inputs+=['-i',str(ROOT/'audio'/f'{k+1:02}.wav')]
  filters=[f'[{i+1}:a]aresample=48000,adelay={int(x["start"]*1000)}:all=1[v{i+1}]' for i,x in enumerate(scripts)]
  filters+=['[10:a]volume=0.8[m]',''.join(f'[v{i+1}]' for i in range(len(scripts)))+'[m]amix=inputs=10:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]']
  subprocess.run([ff,'-y','-v','error','-i',str(video),*inputs,'-i',str(music),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
 print('OUTPUT',out)
if __name__=='__main__':main()
