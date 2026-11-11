"""An imagined football star's day, drawn as original 2D scenes on every frame.
No photo plates, reference-video frames, or stock footage are used.
"""
from pathlib import Path
import argparse, math, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
W,H,FPS=540,960,24
ROOT=Path(__file__).resolve().parent
AUDIO=ROOT.parent/'celebrity_pov'/'audio'
INK=(27,31,32); BLACK=(24,29,31); PAPER=(244,233,211); SKY=(201,218,210); GOLD=(227,171,85); RED=(160,63,52); WHITE=(250,245,230)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F={s:ImageFont.truetype(FONT,s) for s in (12,15,18,21,25,30,38,48,58)}
CUTS=[0,2.5,5.5,8,11.5,14,16,18.5,21,24,27,30,33.6,37.4,41.85,45,48,51,55,60]
SUBS=[(.35,3.6,'YOU WAKE UP AS','CRISTIANO RONALDO.'),(3.6,7.8,'THE VIEW IS INCREDIBLE.','BUT THERE IS MORE.'),(8,11.2,'BREAKFAST FUELS','THE DAY AHEAD.'),(11.2,15.7,'TRAINING LIKE A CHAMPION','IS ANOTHER STORY.'),(16.2,19.8,'ON THE TRAINING PITCH,','EVERY TOUCH MATTERS.'),(19.8,23.9,'STRENGTH. MOVEMENT.','SKILL.'),(24.15,27.6,'NOW YOU STEP OUTSIDE.','FANS RECOGNIZE YOU.'),(27.6,33.2,'A QUICK TRIP BECOMES','CAMERAS AND CROWDS.'),(33.6,37.4,'THE SPOTLIGHT OPENS','DOORS...'),(37.4,41.6,'BUT PRIVATE MOMENTS','GET HARDER TO FIND.'),(41.85,45.7,'AFTER THE NOISE,','TIME TO RECOVER.'),(45.7,50.6,'AND BE CLOSE TO','THE PEOPLE YOU LOVE.'),(51,54.4,'LUXURY. DISCIPLINE.','ATTENTION.'),(54.4,59.8,'WOULD YOU TAKE','THIS LIFE FOR A DAY?')]
def clamp(x):return max(0,min(1,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def lerp(a,b,u):return a+(b-a)*u
def anim(t,keys):
 if t<=keys[0][0]:return keys[0][1]
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if t<=b:return lerp(x,y,smooth((t-a)/(b-a)))
 return keys[-1][1]
def line(d,pts,c=INK,w=5):
 d.line(pts,fill=c,width=max(1,int(w)),joint='curve')
 r=w/2
 for x,y in (pts[0],pts[-1]):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
def circle(d,x,y,r,c,outline=None,w=2):d.ellipse((x-r,y-r,x+r,y+r),fill=c,outline=outline,width=w)
def text(d,xy,s,size=18,c=INK,anchor='mm'):d.text(xy,s,font=F[size],fill=c,anchor=anchor)
def gradient(im,top,bottom):
 d=ImageDraw.Draw(im)
 for y in range(0,H,4):
  u=y/H;d.rectangle((0,y,W,y+4),fill=tuple(round(lerp(a,b,u)) for a,b in zip(top,bottom)))
def rect(d,box,fill,outline=INK,w=4,r=0):
 if r:d.rounded_rectangle(box,r,fill=fill,outline=outline,width=w)
 else:d.rectangle(box,fill=fill,outline=outline,width=w)
def scenery(im,scene,t):
 if scene in ('home','breakfast','lounge'):
  gradient(im,(204,220,213),(236,196,155));d=ImageDraw.Draw(im)
  d.rectangle((0,90,540,680),fill=(223,211,188));d.rectangle((0,665,540,960),fill=(156,129,105))
  d.rectangle((22,127,518,568),fill=(178,208,201),outline=INK,width=7)
  circle(d,402,218,51,(245,205,140));
  for i in range(20):
   x=i*30-10;h=40+(i*71%120);d.rectangle((x,568-h,x+22,568),fill=(120+i%3*8,155+i%3*6,150+i%3*5))
   for j in range(3):
    if (i+j)%3:d.rectangle((x+5+j*6,575-h,x+8+j*6,581-h),fill=(233,220,176))
  for x in (22,270,518):line(d,[(x,127),(x,568)],INK,7)
  line(d,[(22,353),(518,353)],INK,7)
  for y in range(700,960,52):line(d,[(0,y),(540,y)],(132,108,90),2)
  if scene=='home':
   rect(d,(31,600,305,744),(105,114,107),INK,5,15);rect(d,(36,574,300,680),(244,235,215),INK,5,12);rect(d,(49,586,142,622),(251,246,228),INK,3,10)
   rect(d,(420,603,507,715),(122,89,65),INK,4,4);line(d,[(465,602),(465,530)],INK,5);d.polygon([(437,531),(492,531),(481,502),(447,502)],fill=(238,205,149),outline=INK,width=4)
  elif scene=='breakfast':
   rect(d,(36,640,505,672),(134,93,64),INK,5,5)
   for x in (75,465):line(d,[(x,671),(x,794)],INK,10)
   d.ellipse((179,626,308,660),fill=WHITE,outline=INK,width=3);circle(d,244,643,13,GOLD)
   rect(d,(345,594,380,641),(233,237,221),INK,3,3);line(d,[(380,604),(394,604),(394,626),(380,626)],INK,3)
  else:
   rect(d,(60,610,478,740),(197,188,166),INK,5,22);rect(d,(75,657,465,746),(224,212,189),INK,4,14)
   rect(d,(157,785,388,806),(125,92,69),INK,4,5)
 elif scene=='pitch':
  gradient(im,(173,206,200),(222,227,186));d=ImageDraw.Draw(im)
  for i in range(14):
   x=i*46-5;h=45+i*23%70;d.rectangle((x,460-h,x+31,460),fill=(124,157,145))
  d.rectangle((0,460,540,960),fill=(123,167,112))
  for i in range(7):d.polygon([(i*95-80,460),(i*95-30,460),(i*165+10,960),(i*165-75,960)],fill=(133,176,120))
  d.line([(60,685),(480,685)],fill=(224,237,206),width=4);d.ellipse((175,590,365,720),outline=(224,237,206),width=4)
  line(d,[(70,472),(70,347),(470,347),(470,472)],WHITE,7)
  for x in range(75,470,38):line(d,[(x,351),(x,470)],(213,227,203),1)
  for y in range(365,470,25):line(d,[(72,y),(468,y)],(213,227,203),1)
 else:
  gradient(im,(179,201,193),(228,194,161));d=ImageDraw.Draw(im)
  for j in range(9):
   x=j*75-50;h=150+(j*63%190);rect(d,(x,565-h,x+62,566),(141+j%3*10,155+j%3*8,148+j%3*7),INK,3)
   for k in range(3):
    for q in range(4):d.rectangle((x+8+k*15,580-h+q*27,x+15+k*15,592-h+q*27),fill=(220,220,192))
  d.rectangle((0,567,540,960),fill=(146,143,129));line(d,[(0,570),(540,570)],INK,5)
  for j in range(5):line(d,[(j*130-20,650),(j*130+140,960)],(178,170,150),3)
 return d

def figure(d,x,ground,s,t,action='idle',shirt=RED,face='neutral',flip=1):
 # Hand-authored skeletal poses: legs, arms, head and body independently animated.
 bob=0
 if action in ('walk','run'):bob=-abs(math.sin(t*(7 if action=='walk' else 10)))*5*s
 hip=(x,ground-104*s+bob);neck=(x,ground-190*s+bob);head=(x,ground-225*s+bob)
 if action in ('walk','run'):
  u=math.sin(t*(7 if action=='walk' else 10));amp=38 if action=='walk' else 60
  feet=[(x+(-24+amp*u)*s,ground-max(0,u)*24*s),(x+(24-amp*u)*s,ground-max(0,-u)*24*s)]
  knees=[(x+(-15+amp*.45*u)*s,ground-(55+max(0,u)*10)*s),(x+(15-amp*.45*u)*s,ground-(55+max(0,-u)*10)*s)]
 elif action=='kick':
  k=anim(t,[(0,0),(.4,-.7),(.7,-.7),(1.05,1),(1.55,.5),(2.5,0)])
  feet=[(x-27*s,ground),(x+(28+70*k)*s,ground-24*max(k,0)*s)];knees=[(x-17*s,ground-55*s),(x+(18+32*k)*s,ground-(54+16*max(k,0))*s)]
 elif action=='sit':feet=[(x-57*s,ground),(x+60*s,ground)];knees=[(x-44*s,ground-48*s),(x+45*s,ground-48*s)]
 else:feet=[(x-30*s,ground),(x+30*s,ground)];knees=[(x-17*s,ground-54*s),(x+17*s,ground-54*s)]
 d.ellipse((x-63*s,ground-5*s,x+63*s,ground+12*s),fill=(102,115,96))
 for knee,foot in zip(knees,feet):
  line(d,[hip,knee,foot],INK,13*s);line(d,[hip,knee,foot],(240,229,207),8*s);line(d,[(foot[0]-8*s,foot[1]),(foot[0]+13*s,foot[1])],INK,10*s)
 # pale simple body, bold contrasting outline
 d.polygon([(x-37*s,neck[1]+5*s),(x+37*s,neck[1]+5*s),(x+25*s,hip[1]+3*s),(x-25*s,hip[1]+3*s)],fill=shirt,outline=INK,width=max(2,int(4*s)))
 d.line([(x-24*s,neck[1]+23*s),(x+24*s,neck[1]+23*s)],fill=(235,218,192),width=max(1,int(2*s)))
 if action=='drink':
  a=anim(t,[(0,0),(.65,0),(1.2,1),(2.15,1),(2.7,0)]);hands=[(x-45*s,ground-130*s),(x+(53-37*a)*s,ground-(132+82*a)*s)]
 elif action in ('wave','selfie'):
  a=anim(t,[(0,0),(.55,1),(3,1)]);hands=[(x-54*s,ground-130*s),(x+(53+5*math.sin(t*7))*s,ground-(130+90*a)*s)]
 else:
  u=math.sin(t*(7 if action=='walk' else 10)) if action in ('walk','run') else 0
  hands=[(x-55*s,ground-(135+25*u)*s),(x+55*s,ground-(135-25*u)*s)]
 for i,hand in enumerate(hands):
  shoulder=(x+(-30 if i==0 else 30)*s,neck[1]+15*s);elbow=((shoulder[0]+hand[0])/2+(-8 if i==0 else 8)*s,(shoulder[1]+hand[1])/2)
  line(d,[shoulder,elbow,hand],INK,10*s);circle(d,*hand,6*s,PAPER,INK,max(1,int(2*s)))
 circle(d,*head,31*s,BLACK,INK,max(2,int(3*s)))
 # expressive eyes and mouth on circular dark face, no copied character design
 eye=3.5*s if face!='surprised' else 6*s
 for dx in (-11,11):circle(d,head[0]+dx*s,head[1]-2*s,eye,WHITE)
 if face=='surprised':d.ellipse((x-4*s,head[1]+10*s,x+4*s,head[1]+18*s),fill=WHITE)
 elif face=='happy':d.arc((x-10*s,head[1]+3*s,x+10*s,head[1]+18*s),0,180,fill=WHITE,width=max(1,int(2*s)))
 else:line(d,[(x-5*s,head[1]+12*s),(x+5*s,head[1]+12*s)],WHITE,2*s)
 if action=='drink':
  hx,hy=hands[1];rect(d,(hx-8*s,hy-18*s,hx+12*s,hy+5*s),WHITE,INK,max(1,int(2*s)),3)
 if action=='selfie':
  hx,hy=hands[1];rect(d,(hx-10*s,hy-25*s,hx+12*s,hy+7*s),(60,73,75),INK,max(1,int(2*s)),3)

def ball(d,x,y,r=18,angle=0):
 circle(d,x,y,r,WHITE,INK,3);circle(d,x+r*.24*math.cos(angle),y+r*.24*math.sin(angle),r*.34,INK)

def label_time(d,t):
 names=['MORNING','BREAKFAST','TRAINING','PUBLIC LIFE','EVENING']
 name=names[0 if t<8 else 1 if t<16 else 2 if t<24 else 3 if t<41.85 else 4]
 rect(d,(22,28,190,62),BLACK,None,0,4);text(d,(33,45),name,15,WHITE,'lm')
 text(d,(518,46),'IMAGINED DAY',12,INK,'rm')

def compose(t):
 i=next((k for k in range(len(CUTS)-1) if CUTS[k]<=t<CUTS[k+1]),len(CUTS)-2);u=t-CUTS[i]
 scene=('home' if i<3 else 'breakfast' if i<5 else 'pitch' if i<9 else 'street' if i<14 else 'lounge')
 im=Image.new('RGB',(W,H));d=scenery(im,scene,t)
 if i==0:
  figure(d,210,695,.95,u,'idle',shirt=(230,222,203),face='surprised');text(d,(270,236),'A DIFFERENT LIFE',25,INK)
 elif i==1:
  # Large reaction insert, explicitly distinct from an establishing shot.
  circle(d,270,452,155,BLACK);circle(d,216,427,20,WHITE);circle(d,324,427,20,WHITE);d.ellipse((252,488,288,530),fill=WHITE)
  text(d,(270,224),'WAIT... IS THIS REAL?',21,INK)
 elif i==2:
  figure(d,anim(u,[(0,140),(2.5,365)]),706,.94,u,'walk',shirt=(230,222,203));text(d,(270,245),'MORNING VIEW',21,INK)
 elif i==3:figure(d,270,659,.90,u,'drink',shirt=(231,224,207),face='happy')
 elif i==4:
  circle(d,270,420,113,BLACK);circle(d,232,411,13,WHITE);circle(d,307,411,13,WHITE);line(d,[(248,469),(290,469)],WHITE,5)
  text(d,(270,245),'NEXT UP: TRAINING',21,INK)
 elif i==5:
  figure(d,anim(u,[(0,90),(2,345)]),720,.85,u,'run');ball(d,420,707)
 elif i==6:
  figure(d,190,720,.94,u,'kick');bx=anim(u,[(0,240),(.96,240),(1.35,420),(2.5,510)]);ball(d,bx,705,18,u*6 if u>1 else 0)
 elif i==7:
  for j in range(3):
   x=100+j*160;circle(d,x,393,49,(236,224,194),INK,4);text(d,(x,393),['01','02','03'][j],25,RED)
  text(d,(270,500),'STRENGTH  •  MOVEMENT  •  SKILL',15,INK)
  figure(d,270,735,.7,u,'run')
 elif i==8:
  figure(d,anim(u,[(0,150),(2.8,365)]),720,.90,u,'run');ball(d,anim(u,[(0,250),(2.8,465)]),704,17,u*4)
 elif i==9:
  for x in (70,470):figure(d,x,700,.53,u+x/100,'wave',shirt=(105,133,126))
  figure(d,270,730,.95,u,'walk',shirt=(216,212,193));text(d,(270,220),'SPOTTED.',30,INK)
 elif i==10:
  for x in (80,460):figure(d,x,740,.65,u+x/100,'selfie',shirt=(125,143,129),face='happy')
  figure(d,270,720,.96,u,'wave',shirt=(217,212,194),face='happy')
  if (u*2.4)%1 < .12:
   for x,y in ((132,385),(420,420)):circle(d,x,y,22,WHITE)
 elif i==11:
  circle(d,270,429,125,BLACK);circle(d,229,413,13,WHITE);circle(d,311,413,13,WHITE);line(d,[(247,472),(290,472)],WHITE,5)
  text(d,(270,230),'NO QUIET ERRANDS',21,INK)
 elif i==12:
  figure(d,anim(u,[(0,110),(3.5,390)]),720,.9,u,'walk',shirt=(217,212,194))
  for j in range(3):figure(d,75+j*195,760,.45,u+j,'selfie',shirt=(110,133,126))
 elif i==13:
  rect(d,(120,318,420,618),(235,223,196),INK,5,9);text(d,(270,383),'FAME',38,INK)
  line(d,[(173,464),(367,464)],INK,3);text(d,(270,520),'A LITTLE LESS PRIVACY',18,RED)
 elif i==14:figure(d,220,750,.94,u,'sit',shirt=(231,224,208));text(d,(270,236),'TIME TO RESET',21,INK)
 elif i==15:
  figure(d,205,741,.86,u,'sit',shirt=(231,224,208),face='happy');figure(d,355,741,.66,u,'wave',shirt=(163,105,92),face='happy')
 elif i==16:
  circle(d,270,433,126,BLACK);circle(d,228,420,12,WHITE);circle(d,310,420,12,WHITE);d.arc((235,441,305,490),0,180,fill=WHITE,width=5)
  text(d,(270,237),'THE MOMENTS THAT MATTER',18,INK)
 elif i==17:
  for j,(x,s) in enumerate(((125,'LUXURY'),(270,'DISCIPLINE'),(415,'ATTENTION'))):
   circle(d,x,400,57,(237,226,198),INK,4);text(d,(x,400),str(j+1),30,RED);text(d,(x,495),s,15,INK)
  figure(d,270,740,.72,u,'idle',shirt=(230,223,205))
 else:
  figure(d,270,740,.92,u,'wave',shirt=(231,224,207),face='happy');text(d,(270,235),'WOULD YOU TAKE',21,INK);text(d,(270,271),'THIS LIFE FOR A DAY?',25,INK)
 label_time(d,t)
 # Subtitles are paraphrases of the pre-existing English narration.
 rect(d,(28,818,512,902),BLACK,None,0,8)
 for a,b,l1,l2 in SUBS:
  if a<=t<b:
   text(d,(270,845),l1,18 if len(l1)<27 else 15,WHITE);text(d,(270,875),l2,18 if len(l2)<27 else 15,(239,198,131));break
 d.rectangle((28,918,512,921),fill=(145,135,119));d.rectangle((28,918,28+int(484*t/60),921),fill=RED)
 if t<.35:im=Image.blend(Image.new('RGB',(W,H),(18,24,23)),im,smooth(t/.35))
 return im

def bed(path):
 sr=48000;t=np.arange(sr*60,dtype=np.float32)/sr;a=np.zeros_like(t);notes=[110,138.59,164.81,207.65,123.47,146.83,185,220]
 for i in range(120):
  pos=int(i*.5*sr);n=min(int(.9*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;env=np.minimum(u/.025,1)*np.exp(-u*3.8);f=notes[(i//8*4+i%4)%len(notes)];a[pos:pos+n]+=.022*env*(np.sin(2*np.pi*f*u)+.28*np.sin(2*np.pi*f*2*u))
 for at in CUTS[:-1]:
  pos=int(at*sr);n=min(int(.25*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.018*np.sin(2*np.pi*(90*u-30*u*u))*np.exp(-12*u)
 a*=np.minimum(1,np.minimum(t,60-t)).clip(0,1)
 with wave.open(str(path),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes((a*32767).astype('<i2').tobytes())
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='deliverables/monarch-reference-style-pov.mp4');p.add_argument('--stills',action='store_true');args=p.parse_args()
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
