"""Fictional celebrity POV: original cinematic 2D animation, not reference footage.
Every visual frame is generated from vector primitives, gradients and blur layers.
"""
from pathlib import Path
import argparse,math,subprocess,tempfile,wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
from motion import foot_target, knee as ik_knee, rolling
ROOT=Path(__file__).resolve().parent; AUDIO=ROOT.parent/'celebrity_pov'/'audio'
W,H,FPS=960,540,24;CW,CH=1040,600
INK=(18,21,28,255);TEXT=(240,229,209,255);AMBER=(248,192,112,255)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';F={s:ImageFont.truetype(FONT,s) for s in (11,13,16,18,22,27,34,42,52)}
CUTS=[0,3,5.7,8,11.5,14,16,18.5,21.3,24,27.1,30,33.6,37.4,41.85,45.1,48.3,51,55,60]
SUBS=[(.35,3.6,'YOU WAKE UP AS CRISTIANO RONALDO.'),(3.6,7.8,'THE VIEW IS INCREDIBLE. BUT THERE IS MORE.'),(8,11.2,'BREAKFAST FUELS THE DAY AHEAD.'),(11.2,15.7,'TRAINING LIKE A CHAMPION IS ANOTHER STORY.'),(16.2,19.8,'ON THE TRAINING PITCH, EVERY TOUCH MATTERS.'),(19.8,23.9,'STRENGTH. MOVEMENT. SKILL.'),(24.15,27.6,'NOW YOU STEP OUTSIDE. FANS RECOGNIZE YOU.'),(27.6,33.2,'A QUICK TRIP BECOMES CAMERAS AND CROWDS.'),(33.6,37.4,'THE SPOTLIGHT OPENS DOORS...'),(37.4,41.6,'BUT PRIVATE MOMENTS GET HARDER TO FIND.'),(41.85,45.7,'AFTER THE NOISE, TIME TO RECOVER.'),(45.7,50.6,'AND BE CLOSE TO THE PEOPLE YOU LOVE.'),(51,54.4,'LUXURY. DISCIPLINE. ATTENTION.'),(54.4,59.8,'WOULD YOU TAKE THIS LIFE FOR A DAY?')]
def clamp(x):return max(0,min(1,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def lerp(a,b,x):return a+(b-a)*x
def anim(t,k):
 if t<=k[0][0]:return k[0][1]
 for (a,x),(b,y) in zip(k,k[1:]):
  if t<=b:return lerp(x,y,smooth((t-a)/(b-a)))
 return k[-1][1]
# Actor world-space paths; deliberately moderate speeds so a planted foot
# remains believable at the authored leg length and stride.
WALK_PATHS={2:(350,460,2.3,1.0),5:(240,380,2.0,.85),9:(430,540,3.0,1.05),12:(390,520,3.6,1.0)}
def path_x(shot,local):
 start,end,duration,_=WALK_PATHS[shot]
 return start+(end-start)*smooth(local/duration)

def step_times(shot):
 """Derive sole touchdown times from the same path/gait used for drawing."""
 start,_,duration,scale=WALK_PATHS[shot];out=[]
 for shift in (0,.5):
  prev=foot_target(start,start,0,scale,shift)[1]
  for k in range(1,int(duration*120)+1):
   t=k/120;planted=foot_target(path_x(shot,t),start,0,scale,shift)[1]
   if planted and not prev:out.append(CUTS[shot]+t)
   prev=planted
 return sorted(out)

def ellipse(d,box,fill,outline=None,width=1):d.ellipse(tuple(int(x) for x in box),fill=fill,outline=outline,width=max(1,int(width)))
def line(d,pts,fill=INK,width=3):
 width=max(1,int(width));pts=[tuple(int(x) for x in p) for p in pts];d.line(pts,fill=fill,width=width,joint='curve');r=width/2
 for x,y in (pts[0],pts[-1]):ellipse(d,(x-r,y-r,x+r,y+r),fill)
def rr(d,box,fill,outline=None,width=1,r=0):
 b=tuple(int(x) for x in box)
 if r:d.rounded_rectangle(b,int(r),fill=fill,outline=outline,width=int(width))
 else:d.rectangle(b,fill=fill,outline=outline,width=int(width))
def txt(d,xy,s,size=16,fill=TEXT,anchor='mm'):d.text(xy,s,font=F[size],fill=fill,anchor=anchor,stroke_width=1,stroke_fill=(10,12,20,110))
def grad(im,c0,c1,top=0,bottom=CH):
 d=ImageDraw.Draw(im);span=max(1,bottom-top)
 for y in range(top,bottom,3):
  u=(y-top)/span;d.rectangle((0,y,CW,y+3),fill=tuple(round(lerp(c0[i],c1[i],u)) for i in range(3))+(255,))
def glow(im,x,y,r,color,opacity=110,blur=35):
 lay=Image.new('RGBA',im.size);d=ImageDraw.Draw(lay);ellipse(d,(x-r,y-r,x+r,y+r),(*color,opacity));im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))
def sky(im,t,mode='dawn'):
 # A single stylized day arc: sun climbs, crosses the sky, then descends.
 day=clamp(t/60);height=math.sin(math.pi*day);sunx=735-450*day;suny=282-108*height
 top=tuple(round(lerp(a,b,height)) for a,b in zip((45,44,70),(70,96,112)))
 low=tuple(round(lerp(a,b,height)) for a,b in zip((187,120,105),(162,178,168)))
 grad(im,top,low)
 glow(im,sunx,suny,100,(255,191,125),130,65);d=ImageDraw.Draw(im)
 ellipse(d,(sunx-31,suny-31,sunx+31,suny+31),(255,208,153,225))
 clouds=Image.new('RGBA',im.size);cd=ImageDraw.Draw(clouds)
 for i in range(9):
  y=85+i*22;x=50+i*127+(t*1.5)%25
  ellipse(cd,(x-84,y-3,x+84,y+3),(219,178,164,36))
 im.alpha_composite(clouds.filter(ImageFilter.GaussianBlur(4)));d=ImageDraw.Draw(im)
 d.polygon([(0,310),(130,273),(260,300),(395,266),(525,299),(665,270),(770,290),(900,263),(1040,293),(1040,390),(0,390)],fill=(54,58,65,255))
 d.polygon([(0,327),(110,303),(240,318),(365,291),(510,316),(650,294),(820,318),(975,286),(1040,300),(1040,390),(0,390)],fill=(38,46,52,255))
 for i in range(50):
  x=i*23+(i%3)*3;h=7+(i*37%44);d.rectangle((x,328-h,x+15,340),fill=(30,36,41,255))
  if i%3==0:d.polygon([(x-3,328-h),(x+7,316-h),(x+18,328-h)],fill=(30,36,41,255))
 return d

def hotel(im,t,variant='bedroom'):
 sky(im,t);d=ImageDraw.Draw(im)
 # Window view layered behind architectural foreground.
 d.rectangle((0,330,CW,CH),fill=(83,70,72,255));d.polygon([(0,451),(1040,451),(1040,600),(0,600)],fill=(74,62,63,255))
 for j in range(11):
  x=j*105;d.line((x,455,520+(x-520)*1.8,600),fill=(132,98,83,100),width=2)
 d.rectangle((0,0,92,478),fill=(38,33,42,255));d.rectangle((952,0,1040,478),fill=(38,33,42,255));d.rectangle((0,0,1040,98),fill=(40,35,45,255))
 for x in (93,520,952):d.rectangle((x-5,96,x+5,455),fill=(36,31,36,255))
 d.rectangle((90,290,952,300),fill=(37,32,37,255));d.rectangle((90,450,952,465),fill=(35,30,35,255))
 for x in range(110,950,32):
  h=15+(x*37%55);d.rectangle((x,382-h,x+21,389),fill=(49,51,59,255))
  if x%3:d.rectangle((x+5,389-h,x+9,393-h),fill=(255,201,129,170))
 # Curtain folds, sill highlights and distant glass reflections.
 for x in (12,32,52,972,992,1012):
  line(d,[(x,99),(x+6,441)],(65,52,57,255),3)
 line(d,[(103,452),(940,452)],(195,148,114,150),2)
 # Soft, motivated window light, composited instead of hard painted streaks.
 beam=Image.new('RGBA',im.size);bd=ImageDraw.Draw(beam)
 bd.polygon([(735,300),(801,300),(936,599),(627,599)],fill=(255,180,117,24))
 im.alpha_composite(beam.filter(ImageFilter.GaussianBlur(18)));d=ImageDraw.Draw(im)
 # Layered plant, pot and floor contact ground the interior.
 ellipse(d,(896,496,1032,522),(24,27,28,120))
 d.polygon([(936,470),(996,470),(987,520),(946,520)],fill=(80,64,61,255),outline=INK,width=3)
 for j in range(7):
  bx=965+(j-3)*7; tip=(965+(j-3)*17,406-abs(3-j)*5)
  line(d,[(965,474),tip],(69,91,77,255),3)
  ellipse(d,(tip[0]-8,tip[1]-19,tip[0]+8,tip[1]+7),(55+j*3,77+j*3,66+j*2,255))
 if variant=='bedroom':
  d.polygon([(80,443),(427,443),(468,512),(58,512)],fill=(35,34,40,255),outline=(18,20,26,255),width=4)
  rr(d,(91,425,424,481),(161,151,137,255),INK,3,10);rr(d,(108,420,244,450),(217,206,185,255),INK,2,8)
  d.polygon([(240,447),(422,447),(456,507),(217,507)],fill=(113,117,119,255),outline=INK,width=3)
  line(d,[(258,459),(410,459),(437,493)],(150,147,139,255),2)
  line(d,[(250,469),(400,469)],(94,99,101,255),2)
  rr(d,(108,409,420,425),(82,72,72,255),INK,2,4)
  rr(d,(114,424,210,446),(224,212,192,255),INK,2,7)
  rr(d,(218,424,305,446),(200,192,177,255),INK,2,7)
  rr(d,(810,442,920,523),(65,49,48,255),INK,3,4);line(d,[(865,443),(865,367)],(41,36,38,255),5)
  d.polygon([(835,369),(896,369),(883,336),(849,336)],fill=(235,188,127,255),outline=INK,width=3);glow(im,865,363,25,(255,184,105),72,24)
 elif variant=='breakfast':
  d.polygon([(215,450),(830,450),(877,483),(171,483)],fill=(125,87,71,255),outline=INK,width=4)
  for x in (225,813):line(d,[(x,481),(x-12,568)],INK,8)
  ellipse(d,(438,443,564,469),(222,208,186,255),INK,3);ellipse(d,(472,448,522,462),(198,152,91,255));rr(d,(612,404,643,451),(190,201,190,255),INK,3,3)
  ellipse(d,(482,451,497,460),(233,206,143,255));ellipse(d,(502,451,517,459),(206,170,104,255))
  line(d,[(383,445),(424,453)],(219,215,201,255),3);line(d,[(575,448),(607,453)],(219,215,201,255),3)
  rr(d,(687,410,715,450),(83,100,100,255),INK,2,4)
  line(d,[(691,415),(709,415)],(183,203,191,255),2)
 elif variant=='lounge':
  rr(d,(250,401,787,499),(117,105,100,255),INK,4,18);rr(d,(264,447,773,515),(148,131,118,255),INK,3,14)
  d.polygon([(331,528),(706,528),(745,552),(301,552)],fill=(96,64,58,255),outline=INK,width=3)
  ellipse(d,(502,508,546,532),(218,190,143,255),INK,2)
  rr(d,(292,416,380,459),(143,124,113,255),INK,2,8)
  rr(d,(668,416,752,459),(160,136,120,255),INK,2,8)
  line(d,[(280,470),(758,470)],(194,164,138,255),2)
  rr(d,(622,523,676,529),(74,59,58,255),None,0,2)
  line(d,[(629,525),(667,525)],(221,196,161,255),1)
 return im

def pitch(im,t):
 sky(im,t);d=ImageDraw.Draw(im)
 d.rectangle((0,344,1040,600),fill=(48,76,55,255));d.polygon([(0,358),(1040,358),(1040,420),(0,394)],fill=(58,94,66,255))
 for i in range(17):
  x=i*72-60;d.polygon([(x,350),(x+35,350),(x+115,600),(x+50,600)],fill=(66,101,72,100))
 d.line((0,470,1040,470),fill=(177,192,161,150),width=3);d.ellipse((327,383,710,510),outline=(176,192,160,110),width=3)
 for x in (111,931):line(d,[(x,350),(x,240)],(211,213,196,255),5)
 line(d,[(111,240),(931,240)],(211,213,196,255),5)
 for x in range(125,930,53):line(d,[(x,245),(x,347)],(174,179,166,65),1)
 for y in range(260,350,22):line(d,[(112,y),(930,y)],(174,179,166,65),1)
 # Distant stand and railings add a midground between pitch and horizon.
 d.polygon([(0,339),(0,319),(1040,319),(1040,340)],fill=(36,43,42,255))
 for j in range(52):
  x=j*20; ellipse(d,(x,321+(j%3)*4,x+4,325+(j%3)*4),(174,165,144,120))
 d.line((0,339,1040,339),fill=(195,178,148,110),width=2)
 for x in (145,240,810,900):
  d.polygon([(x-5,474),(x+5,474),(x+10,485),(x-10,485)],fill=(214,148,78,255),outline=INK,width=1)
 # stadium light poles create a motivated rim.
 for x in (45,991):
  line(d,[(x,165),(x,350)],(32,38,40,255),5);rr(d,(x-19,153,x+19,165),(236,213,171,255));glow(im,x,160,15,(255,213,159),85,22)
 return im

def street(im,t):
 sky(im,t,'night');d=ImageDraw.Draw(im)
 for i in range(11):
  x=i*108-15;h=110+(i*71%150);d.rectangle((x,347-h,x+88,350),fill=(38+i%3*5,43+i%3*4,54+i%3*4,255))
  for xx in range(x+8,x+80,19):
   for yy in range(354-h,337,23):
    if (xx+yy+i)%4:rr(d,(xx,yy,xx+8,yy+10),(234,186,129,100))
 # Shop awnings and road furniture provide believable depth cues.
 for x in (45,370,690):
  rr(d,(x,300,x+112,348),(34,40,48,255),(79,85,90,255),2)
  rr(d,(x+8,308,x+104,335),(79,91,95,255),None,0)
  line(d,[(x,301),(x+112,301)],(208,159,117,255),3)
 d.rectangle((0,350,1040,600),fill=(53,53,57,255));d.polygon([(0,468),(1040,430),(1040,600),(0,600)],fill=(40,42,48,255))
 for x in range(0,1050,120):line(d,[(x,465),(x+150,600)],(113,104,99,100),2)
 for x in (84,960):
  line(d,[(x,340),(x,170)],(30,32,37,255),6);ellipse(d,(x-8,161,x+8,177),(255,218,164,255));glow(im,x,170,16,(255,197,127),80,24)
 return im

def actor(im,x,y,s,t,action='idle',outfit=(191,188,179,255),face='neutral',depth=False,path_origin=None):
 d=ImageDraw.Draw(im)
 distance=max(0,x-path_origin) if path_origin is not None else 0
 phase=distance/(40*s)*math.tau if s else 0
 bob=(-abs(math.sin(phase))*1.5*s if action in ('walk','run') else math.sin(t*1.8)*.45*s)
 hip=(x,y-56*s+bob);hips=[hip,hip];neck=(x,y-105*s+bob);head=(x,y-129*s+bob);headr=18*s
 ellipse(d,(x-43*s,y-5*s,x+43*s,y+7*s),(15,19,22,100))
 if action in ('walk','run'):
  if path_origin is None:raise ValueError('locomotion requires a path origin')
  feet=[foot_target(x,path_origin,y,s,shift)[0] for shift in (0,.5)]
  hips=[(x-6*s,hip[1]),(x+6*s,hip[1])]
  knees=[ik_knee(hips[j],foot,34*s,34*s,-1) for j,foot in enumerate(feet)]
 elif action=='kick':
  q=anim(t,[(0,0),(.4,-.65),(.8,-.65),(1.12,1),(1.6,.4),(2.5,0)])
  feet=[(x-15*s,y),(x+(15+43*q)*s,y-17*max(q,0)*s)];knees=[(x-9*s,y-29*s),(x+(10+18*q)*s,y-(29+8*max(q,0))*s)]
 elif action=='sit':feet=[(x-34*s,y),(x+34*s,y)];knees=[(x-26*s,y-26*s),(x+26*s,y-26*s)]
 else:feet=[(x-16*s,y),(x+16*s,y)];knees=[(x-9*s,y-29*s),(x+9*s,y-29*s)]
 for leg_hip,knee,foot in zip(hips,knees,feet):
  line(d,[leg_hip,knee,foot],(15,18,23,255),8*s);line(d,[leg_hip,knee,foot],(180,178,164,255),4.6*s);line(d,[(foot[0]-5*s,foot[1]),(foot[0]+8*s,foot[1])],(17,21,25,255),7*s)
 d.polygon([(x-22*s,neck[1]+4*s),(x+22*s,neck[1]+4*s),(x+15*s,hip[1]+2*s),(x-15*s,hip[1]+2*s)],fill=outfit,outline=INK,width=max(1,int(2*s)))
 # Clothing seams and collar add form without an image texture.
 line(d,[(x-12*s,neck[1]+7*s),(x,neck[1]+13*s),(x+12*s,neck[1]+7*s)],(91,88,87,255),1.5*s)
 line(d,[(x-13*s,hip[1]-4*s),(x+13*s,hip[1]-4*s)],(91,88,87,170),1*s)
 # Moving hands and their props remain separate from face and torso.
 if action=='drink':
  a=anim(t,[(0,0),(.5,0),(1.1,1),(2.4,1),(3,0)]);hands=[(x-30*s,y-75*s),(x+(32-19*a)*s,y-(77+40*a)*s)]
 elif action in ('wave','selfie'):
  a=anim(t,[(0,0),(.4,1),(3,1)]);hands=[(x-30*s,y-75*s),(x+(31+4*math.sin(t*7))*s,y-(75+48*a)*s)]
 else:
  q=math.sin(phase) if action in ('walk','run') else 0;hands=[(x-30*s,y-(75+17*q)*s),(x+30*s,y-(75-17*q)*s)]
 for j,h in enumerate(hands):
  shoulder=(x+(-17 if j==0 else 17)*s,neck[1]+9*s);el=((shoulder[0]+h[0])/2+(-4 if j==0 else 4)*s,(shoulder[1]+h[1])/2);line(d,[shoulder,el,h],(16,19,25,255),6*s);line(d,[shoulder,el,h],(211,198,177,255),3*s)
 # Connect head to body before drawing the rimmed face.
 line(d,[(x,head[1]+headr-2*s),(x,neck[1]+8*s)],(190,151,112,255),7*s)
 # Skin-tone rim around dark face; subtle highlight, white eyes and brows.
 ellipse(d,(head[0]-headr-2*s,head[1]-headr-2*s,head[0]+headr+2*s,head[1]+headr+2*s),(225,174,119,255))
 ellipse(d,(head[0]-headr,head[1]-headr,head[0]+headr,head[1]+headr),(19,22,30,255))
 # Offset eye highlight and timed blink are sampled from absolute shot time.
 blink=(t%4.2)>3.98 and (t%4.2)<4.10
 for dx in (-6,6):
  if blink:line(d,[(x+(dx-2)*s,head[1]),(x+(dx+2)*s,head[1])],(252,244,224,255),1.4*s)
  else:ellipse(d,(x+(dx-2.1)*s,head[1]-2*s,x+(dx+2.1)*s,head[1]+2*s),(252,244,224,255))
 d.arc((x-headr*.8,head[1]-headr*.8,x+headr*.8,head[1]+headr*.8),200,250,fill=(107,89,82,180),width=max(1,int(.9*s)))
 if face=='surprised':
  for dx in (-6,6):line(d,[(x+(dx-3)*s,head[1]-6*s),(x+(dx+3)*s,head[1]-7*s)],(252,244,224,255),1.3*s)
  ellipse(d,(x-2*s,head[1]+7*s,x+2*s,head[1]+11*s),(252,244,224,255))
 elif face=='happy':d.arc((x-6*s,head[1]+3*s,x+6*s,head[1]+11*s),0,180,fill=(252,244,224,255),width=max(1,int(1.6*s)))
 else:line(d,[(x-3*s,head[1]+8*s),(x+3*s,head[1]+8*s)],(245,238,222,255),1.4*s)
 if action=='drink':
  hx,hy=hands[1];rr(d,(hx-4*s,hy-10*s,hx+7*s,hy+2*s),(224,220,206,255),INK,max(1,int(s)),2)
 elif action=='selfie':
  hx,hy=hands[1];rr(d,(hx-6*s,hy-14*s,hx+7*s,hy+4*s),(71,78,83,255),INK,max(1,int(s)),2)

def soccer(im,x,y,r,angle=0):
 d=ImageDraw.Draw(im);ellipse(d,(x-r+1,y-r+2,x+r+2,y+r+3),(10,15,18,100));ellipse(d,(x-r,y-r,x+r,y+r),(230,230,213,255),INK,2)
 pts=[(x+math.cos(angle+math.tau*j/5)*r*.38,y+math.sin(angle+math.tau*j/5)*r*.38) for j in range(5)]
 d.polygon(pts,fill=INK)
 for j in range(5):
  a=angle+math.tau*j/5;line(d,[pts[j],(x+math.cos(a)*r*.82,y+math.sin(a)*r*.82)],(67,68,65,255),max(1,r*.07))

def wake_in_bed(im,t):
 """A simple pose change with head and arm visible above the bed covers."""
 d=ImageDraw.Draw(im);rise=anim(t,[(0,0),(.7,0),(1.6,1),(2.4,1)])
 hx,hy=165,413-10*rise
 line(d,[(220,458),(240,438),(260+15*rise,434-40*rise)],INK,10)
 line(d,[(220,458),(240,438),(260+15*rise,434-40*rise)],(206,192,172,255),6)
 ellipse(d,(hx-23,hy-23,hx+23,hy+23),(220,175,125,255))
 ellipse(d,(hx-20,hy-20,hx+20,hy+20),(19,22,30,255))
 for dx in (-7,7):
  if t<.8:line(d,[(hx+dx-3,hy),(hx+dx+3,hy)],(251,244,225,255),2)
  else:ellipse(d,(hx+dx-3,hy-3,hx+dx+3,hy+3),(251,244,225,255))
 if t>=.8:ellipse(d,(hx-2,hy+8,hx+2,hy+12),(251,244,225,255))
 # Cover the lower arm and torso, but not the visible stretching hand.
 d.polygon([(206,452),(424,447),(456,507),(210,507)],fill=(113,117,119,255),outline=INK,width=3)
 line(d,[(237,462),(405,459),(437,493)],(150,147,139,255),2)

def foreground_table(im):
 """A foreground table occludes a seated character instead of placing feet on it."""
 d=ImageDraw.Draw(im)
 d.polygon([(215,450),(830,450),(877,483),(171,483)],fill=(125,87,71,255),outline=INK,width=4)
 line(d,[(220,456),(825,456)],(183,134,99,255),2)
 for x in (225,813):line(d,[(x,481),(x-12,568)],INK,8)
 ellipse(d,(438,443,564,469),(222,208,186,255),INK,3)
 ellipse(d,(472,448,522,462),(198,152,91,255))
 for x in (487,507):ellipse(d,(x-6,451,x+6,460),(233,206,143,255))
 line(d,[(383,445),(424,453)],(219,215,201,255),3)


def pov_cup(im,t):
 """Animated first-person reach: hand and cup move together once grasped."""
 d=ImageDraw.Draw(im);u=anim(t,[(0,0),(.45,0),(1.1,1),(2.35,1),(3.35,0)])
 # Hand reaches the mug then lifts it; easing gives anticipation and follow-through.
 lift=anim(t,[(0,0),(1.1,0),(1.8,72),(2.35,0),(3.5,0)])
 cupx,cupy=530,432-lift
 d.polygon([(0,555),(1040,555),(1040,600),(0,600)],fill=(68,52,50,255))
 d.polygon([(175,492),(850,492),(995,600),(35,600)],fill=(119,85,70,255),outline=INK,width=5)
 ellipse(d,(cupx-41,488,cupx+50,507),(38,32,33,130))
 # Cup is drawn before the hand so it is grasped, not floating in front.
 rr(d,(cupx-32,cupy-16,cupx+34,cupy+60),(220,211,190,255),INK,4,9)
 d.arc((cupx+15,cupy-2,cupx+63,cupy+44),270,90,fill=(210,200,181,255),width=9)
 ellipse(d,(cupx-31,cupy-21,cupx+33,cupy-7),(234,226,204,255),INK,3)
 ellipse(d,(cupx-25,cupy-18,cupx+27,cupy-9),(88,68,58,255))
 # The moving forearm and sleeve occupy the foreground like a point-of-view shot.
 start=(1005,610);elbow=(860,550-30*u);hand=(lerp(745,cupx+38,u),lerp(525,cupy+18,u))
 line(d,[start,elbow,hand],INK,55);line(d,[start,elbow,hand],(199,187,169,255),43)
 ellipse(d,(hand[0]-27,hand[1]-24,hand[0]+25,hand[1]+22),(216,177,143,255),INK,3)
 for j in range(3):line(d,[(hand[0]-11+j*7,hand[1]-12),(hand[0]-8+j*7,hand[1]+3)],(161,122,103,255),2)
 for j in range(3):
  yy=cupy-45-j*13-math.sin(t*2+j)*3
  d.arc((cupx-18+j*11,yy-12,cupx+j*11,yy+10),190,330,fill=(225,216,196,100),width=2)


def dribble_pose(t):
 """Return ball and boot positions for the hand-authored contact beat."""
 distance,_=rolling(t-1.04,250,95)
 ballx=526+distance
 bally=416-.16*distance
 footx=anim(t,[(0,410),(.55,395),(1.04,493),(1.42,550),(2.8,470)])
 footy=anim(t,[(0,465),(.55,470),(1.04,453),(1.42,441),(2.8,480)])
 return ballx,bally,footx,footy


def pov_dribble(im,t):
 """A first-person lower-body insert; the contact is authored, not simulated."""
 d=ImageDraw.Draw(im);ballx,bally,footx,footy=dribble_pose(t)
 distance,_=rolling(t-1.04,250,95)
 soccer(im,ballx,bally,25,distance/25)
 # The shoe's upper-right corner meets the lower-left of the ball at contact.
 d.polygon([(620,600),(650,560),(footx+2,footy+8),(footx+25,footy+14),(730,600)],fill=(194,192,179,255),outline=INK,width=5)
 d.polygon([(footx-30,footy-9),(footx+8,footy-20),(footx+33,footy-12),(footx+35,footy+8),(footx-24,footy+13)],fill=(38,43,46,255),outline=INK,width=4)
 line(d,[(footx-3,footy-9),(footx+14,footy-13)],(224,216,196,255),3)
 ellipse(d,(280,556,425,579),(16,20,21,105))
 d.polygon([(258,600),(291,514),(331,496),(359,507),(347,562),(386,600)],fill=(194,192,179,255),outline=INK,width=5)


def phone_hand(im,t):
 d=ImageDraw.Draw(im)
 # Sleeve and palm reach the handset; small motion is deterministic.
 dy=5*math.sin(t*.7)
 line(d,[(900,600),(750,535+dy),(592,440+dy)],INK,47)
 line(d,[(900,600),(750,535+dy),(592,440+dy)],(195,183,165,255),37)
 ellipse(d,(570,421+dy,615,463+dy),(211,171,138,255),INK,3)
 for j in range(3):line(d,[(586+j*6,426+dy),(586+j*6,438+dy)],(160,119,101,255),2)


def camera_crop(im,i,u):
 """Shot-local eased push/track on overscanned procedural scenes."""
 duration=CUTS[i+1]-CUTS[i];p=smooth(u/duration)
 # Close-ups are already framed large; an understated push gives hierarchy.
 z0,z1=(1.015,1.07) if i in (1,4,6,11,13,16) else (1.0,1.035)
 zoom=lerp(z0,z1,p);w=round(W/zoom);h=round(H/zoom)
 center_x=520+((p-.5)*20 if i in (2,5,7,9,12) else 0)
 center_y=300+((p-.5)*5)
 left=round(clamp((center_x-w/2)/(CW-w))*(CW-w)) if CW>w else 0
 top=round(clamp((center_y-h/2)/(CH-h))*(CH-h)) if CH>h else 0
 return im.crop((left,top,left+w,top+h)).resize((W,H),Image.Resampling.LANCZOS).convert('RGB')

def compose(t):
 i=next((k for k in range(len(CUTS)-1) if CUTS[k]<=t<CUTS[k+1]),18);u=t-CUTS[i];im=Image.new('RGBA',(CW,CH));
 if i<3:hotel(im,t,'bedroom')
 elif i<4:hotel(im,t,'breakfast')
 elif i<9:pitch(im,t)
 elif i<14:street(im,t)
 else:hotel(im,t,'lounge')
 # Close-up backgrounds are intentionally defocused, as in the reviewed source.
 if i in (1,4,11,16):im=im.filter(ImageFilter.GaussianBlur(5))
 d=ImageDraw.Draw(im)
 if i==0:wake_in_bed(im,u)
 elif i==1:actor(im,540,820,4.4,u,'idle',face='happy' if u<.9 else 'surprised')
 elif i==2:actor(im,path_x(2,u),478,1,u,'walk',path_origin=350)
 elif i==3:pov_cup(im,u)
 elif i==4:actor(im,520,820,4.4,u,'idle',face='neutral')
 elif i==5:actor(im,path_x(5,u),460,.85,u,'run',outfit=(151,66,57,255),path_origin=240)
 elif i==6:
  actor(im,420,462,1.2,u,'kick',outfit=(151,66,57,255))
  # The near-foot kick makes contact around u=.98; after impact the ball rolls
  # with constant resistance and rotates by travelled distance / radius.
  distance,_=rolling(u-.98,420,145)
  soccer(im,475+distance,450,12,distance/12)
 elif i==7:pov_dribble(im,u)
 elif i==8:
  actor(im,520,465,1.1,u,'wave',outfit=(151,66,57,255));
  for j,label in enumerate(('STRENGTH','MOVEMENT','SKILL')):
   x=185+j*335;txt(ImageDraw.Draw(im),(x,208),label,13,AMBER);line(ImageDraw.Draw(im),[(x,225),(x,270)],(231,181,124,140),1)
 elif i==9:
  for j,x in enumerate((120,260,780,930)):actor(im,x,475,.60,u+j*.3,'wave',outfit=(99,112,110,255))
  actor(im,path_x(9,u),483,1.05,u,'walk',path_origin=430)
 elif i==10:
  for j,x in enumerate((180,360,720,900)):actor(im,x,470,.72,u+j*.2,'selfie',outfit=(97,114,115,255))
  actor(im,525,465,1.1,u,'wave',face='happy')
  if (u*2.5)%1<.12:
   for x in (200,870):glow(im,x,302,9,(255,241,215),200,15)
 elif i==11:actor(im,520,820,4.4,u,'idle')
 elif i==12:
  for j,x in enumerate((150,280,760,900)):actor(im,x,480,.65,u+j*.3,'selfie',outfit=(99,112,110,255))
  actor(im,path_x(12,u),475,1,u,'walk',path_origin=390)
 elif i==13:
  # A foreground phone with the background deliberately softened behind it.
  im=im.filter(ImageFilter.GaussianBlur(5));d=ImageDraw.Draw(im);rr(d,(434,198,605,470),(31,33,42,255),(190,159,129,255),3,16);rr(d,(446,215,593,445),(75,71,77,255),None,1,5);txt(d,(520,282),'ALWAYS ON',18,TEXT);txt(d,(520,322),'A LITTLE LESS PRIVACY',11,AMBER);phone_hand(im,u)
 elif i==14:
  actor(im,430,505,1,u,'sit',face='neutral')
  rr(ImageDraw.Draw(im),(264,463,773,515),(148,131,118,255),INK,3,14)
 elif i==15:
  actor(im,408,505,.95,u,'sit',face='happy');actor(im,650,505,.72,u,'wave',outfit=(153,104,96,255),face='happy')
  rr(ImageDraw.Draw(im),(264,463,773,515),(148,131,118,255),INK,3,14)
 elif i==16:actor(im,520,820,4.4,u,'idle',face='happy')
 elif i==17:
  for j,l in enumerate(('LUXURY','DISCIPLINE','ATTENTION')):txt(ImageDraw.Draw(im),(260+j*260,205),l,16,AMBER)
  actor(im,520,488,1.03,u,'idle')
 else:actor(im,520,488,1.05,u,'wave',face='happy');txt(ImageDraw.Draw(im),(520,200),'WOULD YOU TAKE THIS LIFE?',22,TEXT)
 # Restrained drifting light particles; fixed-position function of time, no random flicker.
 d=ImageDraw.Draw(im)
 for j in range(22):
  x=(j*83+11*math.sin(t*.13+j))%CW;y=110+(j*73+t*(2+j%3))%370
  ellipse(d,(x-1,y-1,x+1,y+1),(245,210,169,45))
 # Simulated camera move. Crop from an overscanned scene, never from a still photograph.
 im=camera_crop(im,i,u)
 # Soft vignette over the image, applied consistently to every generated frame.
 im=Image.composite(Image.new('RGB',(W,H),(12,14,20)),im,VIGNETTE)
 d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,0,W,20),fill=(10,12,16,255));d.rectangle((0,H-21,W,H),fill=(10,12,16,255))
 phases=['MORNING','BREAKFAST','TRAINING','PUBLIC LIFE','EVENING'];phase=phases[0 if t<8 else 1 if t<16 else 2 if t<24 else 3 if t<41.85 else 4]
 txt(d,(22,36),phase,11,(231,211,183,180),'lm');txt(d,(W-22,36),'FICTIONAL POV',11,(231,211,183,180),'rm')
 for a,b,s in SUBS:
  if a<=t<b:
   d.rounded_rectangle((145,477,815,513),6,fill=(13,16,23,180));txt(d,(480,495),s,13,TEXT);break
 if t<.4:im=Image.blend(Image.new('RGB',(W,H),(7,9,13)),im,smooth(t/.4))
 return im

y,x=np.ogrid[-1:1:complex(H),-1:1:complex(W)];v=np.clip((np.sqrt((x*.82)**2+(y*.9)**2)-.25)*.6,0,.65);VIGNETTE=Image.fromarray((v*255).astype('uint8'),'L')

def bed(path):
 sr=48000;t=np.arange(sr*60,dtype=np.float32)/sr;a=np.zeros_like(t);notes=[110,138.59,164.81,207.65,123.47,146.83,185,220]
 for i in range(120):
  pos=int(i*.5*sr);n=min(int(.9*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;env=np.minimum(u/.025,1)*np.exp(-u*3.8);f=notes[(i//8*4+i%4)%len(notes)];a[pos:pos+n]+=.022*env*(np.sin(2*np.pi*f*u)+.28*np.sin(2*np.pi*f*2*u))
 for at in CUTS[:-1]:
  pos=int(at*sr);n=min(int(.25*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.018*np.sin(2*np.pi*(90*u-30*u*u))*np.exp(-12*u)
 # Original low-level Foley accents placed against visible actions.
 rng=np.random.default_rng(20261105)
 def impact(at,kind):
  pos=int(at*sr);n=min(int(.23*sr),len(a)-pos)
  if n<=0:return
  u=np.arange(n,dtype=np.float32)/sr
  if kind=='foot':cue=(.013*np.sin(2*np.pi*94*u)+.006*rng.standard_normal(n))*np.exp(-u*22)
  elif kind=='kick':cue=(.045*np.sin(2*np.pi*(105*u-45*u*u))+.009*rng.standard_normal(n))*np.exp(-u*20)
  elif kind=='shutter':cue=.012*rng.standard_normal(n)*np.exp(-u*65)
  else:cue=.010*np.sin(2*np.pi*780*u)*np.exp(-u*16)
  a[pos:pos+n]+=cue.astype(np.float32)
 for shot in WALK_PATHS:
  for at in step_times(shot):impact(at,'foot')
 for at in (16.98,19.54):impact(at,'kick')
 for at in (27.45,28.3,29.15):impact(at,'shutter')
 for at in (9.1,38.1):impact(at,'small')
 a*=np.minimum(1,np.minimum(t,60-t)).clip(0,1)
 with wave.open(str(path),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes((a*32767).astype('<i2').tobytes())
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='deliverables/monarch-cinematic-pov-v3.mp4');p.add_argument('--stills',action='store_true');args=p.parse_args()
 if args.stills:
  for t in (1,4,7,10,13,17,19,22,25,29,32,35,39,43,46,49,53,57):compose(t).save(ROOT/f'preview-{t}.jpg',quality=90)
  return
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  tmp=Path(tmp);video=tmp/'video.mp4';music=tmp/'bed.wav';bed(music)
  proc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(video)],stdin=subprocess.PIPE)
  for n in range(FPS*60):
   proc.stdin.write(compose(n/FPS).tobytes())
   if n%120==0:print('frame',n,'/',FPS*60,flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('video encoding failed')
  inputs=[]
  for k in range(1,8):inputs+=['-i',str(AUDIO/f'{k:02}.wav')]
  offsets=[.35,8,16.2,24.15,33.6,41.85,51];filters=[f'[{i}:a]aresample=48000,adelay={int(at*1000)}:all=1[v{i}]' for i,at in enumerate(offsets,1)]
  filters+=['[8:a]volume=0.55[m]',''.join(f'[v{i}]' for i in range(1,8))+'[m]amix=inputs=8:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]']
  subprocess.run([ff,'-y','-v','error','-i',str(video),*inputs,'-i',str(music),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
 print('OUTPUT',out,flush=True)
if __name__=='__main__':main()
