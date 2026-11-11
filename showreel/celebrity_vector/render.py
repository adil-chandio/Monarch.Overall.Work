"""Fully code-rendered 60s illustrated 2.5D-style animation.
No image, video, photo, stock-footage or pre-rendered visual inputs.
Every visual frame is a deterministic function of time and drawn from shapes.
Audio: user-selected synthetic narration plus original procedural music.
"""
from pathlib import Path
import argparse, math, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parent; AUDIO=ROOT.parent/'celebrity_pov'/'audio'
W,H,FPS,DURATION=540,960,30,60
FNT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F={s:ImageFont.truetype(FNT,s) for s in (12,14,16,18,21,24,28,32,40,45,52)}
WHITE=(247,244,230,255);INK=(13,20,32,255);GOLD=(248,199,101,255)
CUTS=[0,4,8,12,16,20,24,28,33.4,37.4,41.7,46.2,51,55,60]
VOICES=[.35,8.,16.2,24.15,33.6,41.85,51.]
SUBS=[(.35,3.6,'YOU WAKE UP AS','CRISTIANO RONALDO.'),(3.6,7.4,'THE VIEW IS INCREDIBLE.','BUT THERE’S MORE.'),
(8,11.2,'BREAKFAST FUELS','THE DAY AHEAD.'),(11.2,15.4,'TRAINING LIKE A CHAMPION','IS ANOTHER STORY.'),
(16.2,19.8,'ON THE TRAINING PITCH,','EVERY TOUCH MATTERS.'),(19.8,23.7,'STRENGTH. MOVEMENT.','SKILL.'),
(24.15,27.6,'NOW YOU STEP OUTSIDE.','FANS RECOGNIZE YOU.'),(27.6,33.1,'A QUICK TRIP BECOMES','CAMERAS AND CROWDS.'),
(33.6,37.3,'THE SPOTLIGHT OPENS','DOORS...'),(37.3,41.4,'BUT PRIVATE MOMENTS','GET HARDER TO FIND.'),
(41.85,45.7,'AFTER THE NOISE,','TIME TO RECOVER.'),(45.7,50.5,'AND BE CLOSE TO','THE PEOPLE YOU LOVE.'),
(51,54.3,'LUXURY. DISCIPLINE.','ATTENTION.'),(54.3,59.4,'WOULD YOU TAKE','THIS LIFE FOR A DAY?')]

def clamp(x):return max(0,min(1,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def lerp(a,b,x):return a+(b-a)*x
def point(a,b,u):return (lerp(a[0],b[0],u),lerp(a[1],b[1],u))
def track(t,keys):
 if t<=keys[0][0]:return keys[0][1]
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if t<=b:return lerp(x,y,ease((t-a)/(b-a)))
 return keys[-1][1]
def ellipse(d,c,r,fill,outline=None,width=1):x,y=c;d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=width)
def stroke(d,pts,fill,w):
 d.line(pts,fill=fill,width=w,joint='curve')
 for x,y in pts:d.ellipse((x-w/2,y-w/2,x+w/2,y+w/2),fill=fill)
def label(d,pos,txt,font,fill=WHITE):d.text(pos,txt,font=font,fill=fill,anchor='mm',stroke_width=2,stroke_fill=(6,11,20,200))
def grad(im,top,bottom):
 d=ImageDraw.Draw(im);step=8
 for y in range(0,H,step):
  u=y/H;c=tuple(int(lerp(top[i],bottom[i],u)) for i in range(3));d.rectangle((0,y,W,y+step),fill=c)

def scene_bg(im,kind,t,shot):
 d=ImageDraw.Draw(im,'RGBA'); shift=int(7*math.sin(t*.25))
 if kind=='bedroom':
  grad(im,(25,36,66),(123,86,84));d=ImageDraw.Draw(im,'RGBA')
  d.rectangle((35,260,505,622),fill=(222,166,112,255));d.rectangle((44,269,496,613),fill=(242,180,114,255))
  ellipse(d,(380,401),61,(255,214,152,230))
  for i in range(15):
   x=47+i*34+int(shift*.25);height=35+(i*47%100);d.rectangle((x,611-height,x+25,611),fill=(105+i%3*13,94,104,255))
   for j in range(2):d.rectangle((x+4+j*10,614-height+10,x+7+j*10,618-height+10),fill=(252,206,139,220))
  for x in (36,267,497):d.rectangle((x-5,259,x+5,624),fill=(20,30,46,255))
  d.rectangle((35,428,505,440),fill=(20,30,46,255))
  d.polygon([(0,615),(540,615),(540,960),(0,960)],fill=(69,52,55,255))
  for i in range(7):
   x=i*95-30+shift;d.line((270,617,x,960),fill=(121,90,73,150),width=3)
  d.rounded_rectangle((65,581,391,690),18,fill=(47,46,61,255),outline=(20,24,35,255),width=5)
  d.rounded_rectangle((75,568,375,650),16,fill=(200,187,166,255));d.rounded_rectangle((87,576,185,619),12,fill=(239,226,201,255));d.rounded_rectangle((165,608,379,662),13,fill=(135,130,131,255))
 elif kind=='kitchen':
  grad(im,(28,48,67),(117,87,71));d=ImageDraw.Draw(im,'RGBA')
  d.rectangle((41,280,500,616),fill=(35,52,70,255));d.rectangle((48,287,493,609),fill=(217,169,122,255))
  for i in range(12):
   x=50+i*39+shift//3;ht=30+(i*71%110);d.rectangle((x,609-ht,x+28,609),fill=(83,84+i%3*8,102,255))
  for x in (45,270,495):d.rectangle((x-4,280,x+4,617),fill=(24,30,43,255))
  d.polygon([(0,621),(540,621),(540,960),(0,960)],fill=(73,62,66,255))
  d.polygon([(0,644),(354,644),(418,722),(0,722)],fill=(175,138,111,255),outline=INK,width=4)
  d.ellipse((40,657,172,687),fill=(241,233,211,255),outline=INK,width=3);d.ellipse((79,662,125,680),fill=(249,187,87,255))
  d.polygon([(435,473),(500,473),(500,615),(435,615)],fill=(35,45,55,255));d.line((445,490,445,590),fill=(209,173,113,255),width=3)
 elif kind=='gym':
  grad(im,(15,38,65),(29,104,105));d=ImageDraw.Draw(im,'RGBA')
  d.polygon([(48,274),(493,274),(493,610),(48,610)],fill=(33,87,91,255),outline=(101,195,180,255),width=5)
  d.polygon([(50,500),(490,500),(490,609),(50,609)],fill=(33,123,92,255));d.line((48,552,493,552),fill=(162,218,181,190),width=2);d.ellipse((210,524,330,580),outline=(162,218,181,180),width=3)
  for x in (44,270,496):d.line((x,275,x,611),fill=(24,46,61,255),width=9)
  d.polygon([(0,615),(540,615),(540,960),(0,960)],fill=(34,55,67,255))
  for i in range(8):d.line((270,615,i*105-100+shift*2,960),fill=(93,135,137,120),width=2)
  for x in (50,470):d.rounded_rectangle((x-10,521,x+10,633),4,fill=(24,32,44,255));d.ellipse((x-28,544,x+28,600),outline=(184,210,205,255),width=9)
 elif kind=='stadium':
  grad(im,(14,24,51),(76,68,87));d=ImageDraw.Draw(im,'RGBA')
  d.ellipse((-90,291,630,660),fill=(38,48,71,255),outline=(243,191,103,255),width=6)
  d.ellipse((-40,337,580,598),fill=(19,28,49,255),outline=(123,132,155,255),width=4)
  for x in range(-20,560,55):d.line((270,380,x,613),fill=(83,94,118,180),width=3)
  d.polygon([(0,620),(540,620),(540,960),(0,960)],fill=(40,45,59,255))
  for i in range(10):d.line((270,620,i*80-90+shift*2,960),fill=(101,102,112,150),width=2)
  for x in (55,480):d.rectangle((x-4,430,x+4,644),fill=(28,33,45,255));ellipse(d,(x,430),13,(255,214,135,255))
 else: # lounge
  grad(im,(23,35,55),(92,75,88));d=ImageDraw.Draw(im,'RGBA')
  d.rectangle((30,315,510,610),fill=(36,50,75,255));d.ellipse((325,334,388,397),fill=(244,213,158,255))
  for i in range(16):
   x=32+i*32+shift//3;ht=30+(i*61%105);d.rectangle((x,609-ht,x+26,609),fill=(29,40+i%3*8,62,255))
  for x in (30,270,510):d.rectangle((x-5,310,x+5,616),fill=(18,28,42,255))
  d.rectangle((0,617,540,960),fill=(57,51,61,255));d.rounded_rectangle((60,577,478,718),22,fill=(119,120,130,255),outline=(23,27,35,255),width=5);d.rounded_rectangle((75,640,464,720),18,fill=(158,154,150,255))
 # independently-moving foreground decorative plane
 d.polygon([(0,243),(14+shift//2,243),(22+shift,744),(0,763)],fill=(7,15,28,115))
 d.polygon([(540,243),(527-shift//2,243),(519-shift,744),(540,763)],fill=(7,15,28,115))

def human(d,x,g,s,local,action='walk',color=(43,83,112,255),number=True):
 # Joint positions recomputed for each frame; stance uses grounded feet.
 x=float(x); g=float(g); bob=0
 if action=='walk':bob=2.5*math.sin(local*6)
 elif action=='kick':bob=-3*max(0,math.sin(local*4))
 hip=(x,g-104*s+bob);neck=(x,g-201*s+bob);head=(x,g-239*s+bob)
 if action=='walk':
  k=math.sin(local*5.6);lift=max(0,k);lift2=max(0,-k)
  left=(x-32*s+27*s*k,g-4*s-23*s*lift);right=(x+32*s-27*s*k,g-4*s-23*s*lift2)
  kl=(x-19*s+14*s*k,g-55*s-7*s*lift);kr=(x+19*s-14*s*k,g-55*s-7*s*lift2)
 elif action=='kick':
  k=track(local,[(0,0),(.7,0),(1.05,-1),(1.5,1),(1.9,0),(4,0)])
  left=(x-24*s,g-3*s);kl=(x-16*s,g-53*s);kr=(x+20*s+20*s*k,g-55*s-15*s*max(k,0));right=(x+29*s+58*s*k,g-3*s-24*s*max(k,0))
 elif action=='sit':
  kl=(x-45*s,g-50*s);kr=(x+43*s,g-50*s);left=(x-55*s,g-4*s);right=(x+56*s,g-4*s)
 else:kl=(x-18*s,g-54*s);kr=(x+18*s,g-54*s);left=(x-30*s,g-4*s);right=(x+30*s,g-4*s)
 d.ellipse((x-69*s,g-7*s,x+69*s,g+11*s),fill=(5,11,18,100))
 for knee,foot in ((kl,left),(kr,right)):
  stroke(d,[hip,knee,foot],INK,max(5,int(20*s)));stroke(d,[hip,knee,foot],(230,232,222,255),max(3,int(12*s)))
  d.rounded_rectangle((foot[0]-16*s,foot[1]-5*s,foot[0]+18*s,foot[1]+6*s),radius=max(2,int(5*s)),fill=(22,26,35,255))
 d.polygon([(x-38*s,neck[1]+8*s),(x+38*s,neck[1]+8*s),(x+29*s,hip[1]+8*s),(x-29*s,hip[1]+8*s)],fill=INK)
 d.polygon([(x-30*s,neck[1]+15*s),(x+30*s,neck[1]+15*s),(x+23*s,hip[1]),(x-23*s,hip[1])],fill=color)
 d.line([(x-30*s,neck[1]+33*s),(x+30*s,neck[1]+33*s)],fill=(103,157,169,130),width=max(2,int(3*s)))
 if number and s>=.75:d.text((x,neck[1]+53*s),'7',font=F[24],fill=GOLD,anchor='mm')
 if action=='drink':
  u=track(local,[(0,0),(0.8,0),(1.55,1),(2.8,1),(3.6,0),(4,0)])
  elbowA=(x-54*s,g-159*s);handA=point((x-66*s,g-128*s),(x-15*s,g-231*s),u);elbowB=(x+45*s,g-155*s);handB=(x+56*s,g-116*s)
 elif action=='wave':
  u=track(local,[(0,0),(.8,1),(3,1),(4,0)]);elbowA=(x-48*s,g-155*s);handA=(x-65*s,g-125*s);elbowB=(x+40*s,g-190*s);handB=(x+56*s+10*s*math.sin(local*4)*u,g-231*s)
 elif action=='kick':elbowA=(x-50*s,g-155*s);handA=(x-77*s,g-130*s);elbowB=(x+50*s,g-155*s);handB=(x+74*s,g-125*s)
 elif action=='sit':elbowA=(x-48*s,g-160*s);handA=(x-45*s,g-133*s);elbowB=(x+48*s,g-160*s);handB=(x+48*s,g-133*s)
 else:
  k=math.sin(local*5.6) if action=='walk' else 0;elbowA=(x-49*s,g-158*s-12*s*k);handA=(x-60*s,g-126*s-25*s*k);elbowB=(x+49*s,g-158*s+12*s*k);handB=(x+60*s,g-126*s+25*s*k)
 for elbow,hand in ((elbowA,handA),(elbowB,handB)):
  stroke(d,[neck,elbow,hand],INK,max(5,int(17*s)));stroke(d,[neck,elbow,hand],(242,224,199,255),max(3,int(10*s)))
 ellipse(d,head,34*s,INK);ellipse(d,head,30*s,(243,227,202,255));d.pieslice((head[0]-30*s,head[1]-30*s,head[0]+30*s,head[1]+30*s),180,359,fill=(23,29,39,255))
 d.line((head[0]-13*s,head[1]+4*s,head[0]-6*s,head[1]+4*s),fill=INK,width=max(2,int(3*s)))
 d.line((head[0]+7*s,head[1]+4*s,head[0]+14*s,head[1]+4*s),fill=INK,width=max(2,int(3*s)))
 d.arc((head[0]-8*s,head[1]+4*s,head[0]+10*s,head[1]+18*s),0,180,fill=INK,width=max(1,int(2*s)))
 if action=='drink':
  hx,hy=handA;d.rounded_rectangle((hx-9*s,hy-20*s,hx+10*s,hy+5*s),radius=max(2,int(3*s)),fill=(245,245,230,255),outline=INK,width=2);d.arc((hx+5*s,hy-17*s,hx+17*s,hy),270,90,fill=INK,width=2)

def football(d,x,y,r):
 ellipse(d,(x,y),r,(245,243,226,255),INK,3);d.polygon([(x,y-r*.45),(x+r*.42,y-r*.12),(x+r*.25,y+r*.38),(x-r*.25,y+r*.38),(x-r*.42,y-r*.12)],fill=(26,33,42,255))
def hands(d,t,style):
 # Foreground POV arm silhouettes, independently keyed reaching and settling.
 q=track(t,[(0,0),(.5,0),(1.4,1),(3,1),(4,0)]);dy=45*(1-q)
 stroke(d,[(-25,768),(65,685+dy),(207,627+dy)],INK,30);stroke(d,[(-25,768),(65,685+dy),(207,627+dy)],(239,219,193,255),23)
 stroke(d,[(566,768),(475,685+dy),(333,627+dy)],INK,30);stroke(d,[(566,768),(475,685+dy),(333,627+dy)],(239,219,193,255),23)
 if style=='wake':return
 if style=='phone':d.rounded_rectangle((208,465+dy,332,681+dy),radius=19,fill=(19,28,40,255),outline=(230,194,121,255),width=4);d.rounded_rectangle((218,480+dy,322,665+dy),radius=8,fill=(55,75,97,255));d.ellipse((255,601+dy,285,631+dy),outline=WHITE,width=3)
 else:
  d.rounded_rectangle((205,578+dy,337,672+dy),radius=11,fill=(236,226,208,255),outline=INK,width=4);d.arc((322,592+dy,367,648+dy),270,90,fill=INK,width=6)

def overlay(d,t,i,lt):
 # Short title has editorial meaning; safe lower caption region.
 titles=[('POV: YOU ARE','RONALDO'),('A DIFFERENT','MORNING'),('A CHAMPION','NEEDS FUEL'),('ONE SMALL','MOMENT'),('THE WORK','BEHIND IT'),('EVERY','TOUCH MATTERS'),('EVERYONE','KNOWS YOU'),('THE CAMERAS','ARE ALWAYS ON'),('THE PRICE','OF FAME'),('A LITTLE','PRIVACY?'),('TIME TO','RECOVER'),('THE PEOPLE','YOU LOVE'),('THE LIFE','OF A LEGEND'),('WOULD YOU','TAKE THIS LIFE?')]
 d.rectangle((0,0,540,226),fill=(5,13,28,100));lead,headline=titles[i]
 label(d,(270,105),lead,F[18],GOLD);label(d,(270,153),headline,F[40] if len(headline)<=15 else F[32],WHITE)
 d.rounded_rectangle((166,187,374,193),3,fill=GOLD)
 if i==0:label(d,(270,218),'AN IMAGINED EXPERIENCE',F[12],WHITE)
 d.rectangle((0,750,540,960),fill=(5,12,24,165))
 for a,b,l1,l2 in SUBS:
  if a<=t<b:
   label(d,(270,792),l1,F[24] if len(l1)<27 else F[21],WHITE);label(d,(270,828),l2,F[24] if len(l2)<27 else F[21],GOLD);break
 d.rectangle((29,902,511,904),fill=(255,255,255,60));d.rectangle((29,902,29+int(482*t/60),904),fill=GOLD)
 d.text((29,921),'MONARCHs EDIT',font=F[12],fill=(255,255,255,200));d.text((511,921),'FICTIONAL POV',font=F[12],fill=(255,255,255,180),anchor='ra')

def compose(t):
 i=next((k for k in range(len(CUTS)-1) if CUTS[k]<=t<CUTS[k+1]),13);lt=t-CUTS[i]
 im=Image.new('RGB',(W,H));kind=['bedroom','bedroom','kitchen','kitchen','gym','gym','stadium','stadium','stadium','stadium','lounge','lounge','bedroom','stadium'][i]
 scene_bg(im,kind,t,i);d=ImageDraw.Draw(im,'RGBA')
 if i==0:
  hands(d,lt,'wake')
 elif i==1:
  x=track(lt,[(0,180),(.4,180),(3.8,340)]);human(d,x,711,1.05,lt,'walk')
 elif i==2:human(d,295,715,1.05,lt,'drink')
 elif i==3:hands(d,lt,'cup')
 elif i==4:
  x=track(lt,[(0,160),(.3,160),(3.9,340)]);human(d,x,718,1.05,lt,'walk');football(d,420,708,22)
 elif i==5:
  human(d,218,715,1.05,lt,'kick');ballx=track(lt,[(0,283),(1.2,283),(1.7,390),(3.8,470)]);football(d,ballx,710,23)
 elif i in (6,7,8):
  # Animated fans, discrete foreground characters and individually timed flashes.
  for j,(x,g) in enumerate([(65,729),(474,725),(30,779),(510,779)]):human(d,x,g,.40,lt+j*.31,'wave',color=(101,106+j*8,117,255),number=False)
  x=track(lt,[(0,220),(.3,220),(3.9,300)]) if i==6 else 270;human(d,x,710,1.0,lt,'walk' if i==6 else 'wave')
  for j in range(5):
   u=(lt*1.5+j*.91)%3.2
   if u<.18:
    xx=[55,480,84,451,501][j];yy=[380,410,530,557,600][j];r=5+15*(1-u/.18);ellipse(d,(xx,yy),r,(255,239,191,int(210*(1-u/.18))))
 elif i==9:hands(d,lt,'phone')
 elif i==10:human(d,260,710,1.0,lt,'sit')
 elif i==11:
  human(d,207,710,.93,lt,'sit');human(d,345,713,.69,lt,'wave',color=(142,101,97,255),number=False)
 elif i==12:human(d,270,710,1.05,lt,'wave')
 else:
  for j,x in enumerate((65,478)):human(d,x,747,.43,lt+j,'wave',color=(106,99,109,255),number=False)
  human(d,270,710,1.05,lt,'wave')
 overlay(d,t,i,lt)
 # brief dark dip at edit boundaries; no uninitialized blank frames.
 fade=min(1,(t-CUTS[i])/.12,(CUTS[i+1]-t)/.12)
 if fade<1:im=Image.blend(Image.new('RGB',(W,H),(6,12,23)),im,max(0,fade))
 return im

def make_bed(path):
 sr=48000;t=np.arange(sr*DURATION,dtype=np.float32)/sr;a=np.zeros(t.shape,dtype=np.float32);notes=[110,138.59,164.81,207.65,123.47,146.83,185,220]
 for i in range(120):
  pos=int(i*.5*sr);n=min(int(.9*sr),len(a)-pos)
  if n<=0:break
  u=np.arange(n,dtype=np.float32)/sr;env=np.minimum(u/.025,1)*np.exp(-u*3.8);f=notes[(i//8*4+i%4)%len(notes)]
  a[pos:pos+n]+=.022*env*(np.sin(2*np.pi*f*u)+.28*np.sin(2*np.pi*f*2*u))
 for at in CUTS[:-1]:
  pos=int(at*sr);n=min(int(.45*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.028*np.sin(2*np.pi*(90*u-30*u*u))*np.exp(-9*u)
 a*=np.minimum(1,np.minimum(t/1.0,(DURATION-t)/1.0)).clip(0,1)
 with wave.open(str(path),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes((a*32767).astype('<i2').tobytes())

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='deliverables/monarch-pov-fully-rendered-test.mp4');p.add_argument('--stills',action='store_true');args=p.parse_args()
 if args.stills:
  for t in (2,6,10,14,18,22,26,30,35,39,44,48,53,57):compose(t).save(ROOT/f'qa-{t}.jpg',quality=90)
  return
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  tmp=Path(tmp);video=tmp/'picture.mp4';bed=tmp/'bed.wav';make_bed(bed)
  cmd=[ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(video)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for n in range(FPS*DURATION):
   proc.stdin.write(compose(n/FPS).tobytes())
   if n%150==0:print(f'frame {n}/{FPS*DURATION}',flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('video encode failure')
  inputs=[]
  for k in range(1,8):inputs+=['-i',str(AUDIO/f'{k:02}.wav')]
  filters=[f'[{i}:a]aresample=48000,adelay={int(at*1000)}:all=1[v{i}]' for i,at in enumerate(VOICES,1)]
  filters+=['[8:a]volume=0.55[m]',''.join(f'[v{i}]' for i in range(1,8))+'[m]amix=inputs=8:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]']
  subprocess.run([ff,'-y','-v','error','-i',str(video),*inputs,'-i',str(bed),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
if __name__=='__main__':main()
