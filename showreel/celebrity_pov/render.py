"""Original, no-stock illustrated 2.5D test: animated articulated character + layered scenes.
The backgrounds are generated plates, not stock footage. All figure, prop, camera,
typography and score animation is rendered frame-by-frame as a function of time.
"""
from pathlib import Path
import argparse,math,subprocess,tempfile,wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parent
W,H,FPS,DUR=540,960,30,60
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONTREG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F={n:ImageFont.truetype(FONT,n) for n in (14,16,20,25,29,34,40,47,54)}
FR=ImageFont.truetype(FONTREG,15)
BG={n:Image.open(ROOT/'assets'/f'{n}.png').convert('RGB').resize((570,1014),Image.Resampling.LANCZOS) for n in ('bedroom','training','public')}
# Times are aligned with separately generated voice clips, not guessed from playback.
START=[.35,8.0,16.2,24.15,33.6,41.85,51.0]
SCENES=[0,7.7,15.9,24,33.4,41.7,50.9,60]
SUBS=[
(0.4,3.7,'YOU WAKE UP AS','CRISTIANO RONALDO.'),(3.7,7.1,'THE VIEW IS INCREDIBLE.','BUT THERE’S MORE.'),
(8,11.1,'BREAKFAST FUELS','THE DAY AHEAD.'),(11.1,15.2,'LOOKING LIKE A CHAMPION','IS ONE THING...'),
(16.2,19.6,'ON THE TRAINING PITCH,','EVERY TOUCH MATTERS.'),(19.6,23.6,'STRENGTH. MOVEMENT.','SKILL.'),
(24.15,27.2,'NOW YOU STEP OUTSIDE.','FANS RECOGNIZE YOU.'),(27.2,32.8,'A QUICK TRIP BECOMES','CAMERAS AND CROWDS.'),
(33.6,37.0,'THE SPOTLIGHT OPENS','DOORS...'),(37,40.9,'BUT PRIVATE MOMENTS','GET HARDER TO FIND.'),
(41.85,45.5,'AFTER THE NOISE,','TIME TO RECOVER.'),(45.5,50.2,'AND BE CLOSE TO','THE PEOPLE YOU LOVE.'),
(51,54.2,'LUXURY. DISCIPLINE.','ATTENTION.'),(54.2,59,'WOULD YOU TAKE','THIS LIFE FOR A DAY?')]
HEAD=[('POV: YOU ARE','RONALDO'),('FIRST','FUEL'),('THE WORK','BEHIND IT'),('FAME','FOLLOWS YOU'),('THE PRICE','OF FAME'),('TIME TO','RECOVER'),('ONE DAY','AS RONALDO')]
def mix(a,b,t):return a+(b-a)*max(0,min(1,t))
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def line(d,pts,color,width):
 d.line(pts,fill=color,width=width,joint='curve')
 for x,y in pts:d.ellipse((x-width/2,y-width/2,x+width/2,y+width/2),fill=color)
def draw_person(im,x,ground,s,t,mode='walk',shirt=(35,57,84),num=True,skin=(247,233,207),direction=1):
 d=ImageDraw.Draw(im,'RGBA'); u=t
 # center is pelvis; articulated limbs with visibly changing knees, elbows and feet.
 bob=math.sin(u*5)*3*s if mode in ('walk','train') else math.sin(u*1.7)*1.5*s
 hip=(x,ground-88*s+bob); shoulder=(x-3*s,ground-175*s+bob); head=(x-4*s,ground-213*s+bob)
 phase=u*(5.4 if mode=='walk' else 6.5); swing=math.sin(phase)
 d.ellipse((x-67*s,ground-9*s,x+67*s,ground+9*s),fill=(4,12,22,105))
 if mode=='sit':
  knee1=(x-42*s,ground-48*s);foot1=(x-75*s,ground-5*s);knee2=(x+36*s,ground-54*s);foot2=(x+64*s,ground-5*s)
 elif mode=='train':
  knee1=(x-26*s+26*s*swing,ground-45*s-18*s*max(0,swing));foot1=(x-47*s+45*s*swing,ground-6*s-31*s*max(0,swing))
  knee2=(x+24*s-19*s*swing,ground-45*s-12*s*max(0,-swing));foot2=(x+41*s-30*s*swing,ground-5*s-20*s*max(0,-swing))
 else:
  knee1=(x-18*s+20*s*swing,ground-47*s);foot1=(x-29*s+38*s*swing,ground-5*s-17*s*max(0,swing))
  knee2=(x+18*s-20*s*swing,ground-47*s);foot2=(x+29*s-38*s*swing,ground-5*s-17*s*max(0,-swing))
 outline=(13,22,37,255);leg=(225,228,224,255)
 for knee,foot in ((knee2,foot2),(knee1,foot1)):
  line(d,[hip,knee,foot],outline,int(18*s));line(d,[hip,knee,foot],leg,int(11*s));d.rounded_rectangle((foot[0]-15*s,foot[1]-5*s,foot[0]+17*s,foot[1]+6*s),radius=int(5*s),fill=outline)
 d.polygon([(x-36*s,shoulder[1]+2*s),(x+30*s,shoulder[1]+2*s),(x+24*s,hip[1]+8*s),(x-28*s,hip[1]+8*s)],fill=outline)
 d.polygon([(x-29*s,shoulder[1]+7*s),(x+23*s,shoulder[1]+7*s),(x+18*s,hip[1]),(x-21*s,hip[1])],fill=shirt+(255,))
 if num:
  d.text((x-8*s,shoulder[1]+28*s),'7',font=F[25] if s>.8 else F[20],fill=(243,202,110,230))
 if mode=='phone': elbow1=(x-51*s,ground-138*s);hand1=(x-67*s,ground-179*s); elbow2=(x+52*s,ground-142*s);hand2=(x+63*s,ground-184*s)
 elif mode=='drink':elbow1=(x-48*s,ground-137*s);hand1=(x-24*s,ground-185*s+4*s*math.sin(u*2));elbow2=(x+48*s,ground-140*s);hand2=(x+45*s,ground-108*s)
 elif mode=='wave':elbow1=(x-53*s,ground-142*s);hand1=(x-72*s,ground-106*s);elbow2=(x+42*s,ground-181*s);hand2=(x+40*s+12*s*math.sin(u*3),ground-222*s)
 else:
  elbow1=(x-51*s,ground-139*s+18*s*swing);hand1=(x-60*s,ground-110*s+24*s*swing)
  elbow2=(x+50*s,ground-139*s-18*s*swing);hand2=(x+60*s,ground-110*s-24*s*swing)
 for e,h in ((elbow1,hand1),(elbow2,hand2)):
  line(d,[shoulder,e,h],outline,max(3,int(15*s)));line(d,[shoulder,e,h],skin+(255,),max(2,int(8*s)))
 r=30*s;d.ellipse((head[0]-r-3,head[1]-r-3,head[0]+r+3,head[1]+r+3),fill=outline);d.ellipse((head[0]-r,head[1]-r,head[0]+r,head[1]+r),fill=skin+(255,))
 d.pieslice((head[0]-r,head[1]-r-1,head[0]+r,head[1]+r),180,355,fill=(25,30,39,255))
 d.ellipse((head[0]+5*s,head[1]-1*s,head[0]+8*s,head[1]+3*s),fill=outline)
 if mode=='drink':
  d.rounded_rectangle((hand1[0]-5*s,hand1[1]-17*s,hand1[0]+12*s,hand1[1]+5*s),radius=int(3*s),fill=(241,249,252,220),outline=(23,31,46,255),width=2)
 if mode=='phone':d.rounded_rectangle((hand2[0]-8*s,hand2[1]-18*s,hand2[0]+8*s,hand2[1]+7*s),radius=3,fill=(217,228,238,255),outline=outline,width=3)
def textcenter(d,xy,text,font,fill,stroke=0):
 d.text(xy,text,font=font,fill=fill,anchor='mm',stroke_width=stroke,stroke_fill=(7,15,26,230))
def background(name,t):
 x=15+int(9*math.sin(t*.16));y=26+int(10*math.sin(t*.11));im=BG[name].crop((x,y,x+W,y+H)).convert('RGBA')
 # animated foreground bars move at a different speed than the background plate.
 ov=Image.new('RGBA',(W,H));d=ImageDraw.Draw(ov)
 d.rectangle((0,0,W,265),fill=(5,13,27,105));d.rectangle((0,745,W,H),fill=(5,12,24,145))
 d.polygon([(0,0),(21+int(5*math.sin(t*.32)),0),(8,960),(0,960)],fill=(6,15,25,80))
 im.alpha_composite(ov);return im
def scene(t):
 n=min(6,next((i for i in range(7) if SCENES[i]<=t<SCENES[i+1]),6));a=t-SCENES[n]; name=['bedroom','bedroom','training','public','public','bedroom','bedroom'][n]
 im=background(name,t);d=ImageDraw.Draw(im,'RGBA')
 if n==0:
  # Intro: rise and arrive in the foreground, clearly an imagined scene.
  x=mix(170,270,smooth(a/2)); draw_person(im,x,690,1.0,a,'walk')
 elif n==1:
  d.rounded_rectangle((340,605,500,629),12,fill=(35,25,22,235));d.line((355,627,355,729),fill=(30,22,24,255),width=8);d.line((486,627,486,729),fill=(30,22,24,255),width=8)
  d.ellipse((375,588,447,615),fill=(240,242,226,255));d.ellipse((395,590,425,611),fill=(240,177,68,255))
  draw_person(im,242,697,1.02,a,'drink')
 elif n==2:
  draw_person(im,242+32*math.sin(a*.9),699,1.07,a,'train')
  bx=360+42*math.sin(a*1.5);by=710-15*max(0,math.sin(a*1.5));r=26
  d=ImageDraw.Draw(im,'RGBA');d.ellipse((bx-r,by-r,bx+r,by+r),fill=(244,242,221,255),outline=(20,26,32,255),width=3);d.polygon([(bx,by-12),(bx+11,by-4),(bx+7,by+10),(bx-7,by+10),(bx-11,by-4)],fill=(29,38,43,255))
 elif n in (3,4):
  # Foreground crowd is animated separately from the hero and illustrated backdrop.
  for j,(x,y) in enumerate([(72,735),(467,740),(33,780),(507,785)]):draw_person(im,x,y,.44,a+j*.7,'wave',shirt=(76+j*7,75,82),num=False,skin=(221,206,190))
  draw_person(im,266+int(13*math.sin(a*.7)),704,1.0,a,'wave' if n==3 else 'phone')
  d=ImageDraw.Draw(im,'RGBA')
  for i in range(5):
   z=(a*2+i*1.3)%5
   if z<.3:
    xx=[85,455,40,490,425][i];yy=[390,460,560,330,615][i];rr=5+int(7*(1-z/.3));d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(255,246,203,int(180*(1-z/.3))))
 elif n==5:draw_person(im,267,711,1.0,a,'sit')
 else:
  draw_person(im,270,707,1.06,a,'wave');d=ImageDraw.Draw(im,'RGBA')
  d.rounded_rectangle((112,335,428,374),18,fill=(11,23,38,180));textcenter(d,(270,354),'AN IMAGINED DAY',F[16],(245,207,131,255))
 d=ImageDraw.Draw(im,'RGBA');top,main=HEAD[n];slide=int(22*(1-smooth(a/.5)))
 textcenter(d,(270,116+slide),top,F[20],(243,199,120,255),1);textcenter(d,(270,164+slide),main,F[47] if len(main)<12 else F[40],(255,252,244,255),2)
 d.rounded_rectangle((160,196,380,201),2,fill=(243,193,100,230))
 if n==0:textcenter(d,(270,229),'A FICTIONAL EXPERIENCE',F[14],(245,242,232,225),1)
 for st,en,l1,l2 in SUBS:
  if st<=t<en:
   textcenter(d,(270,788),l1,F[25] if len(l1)<26 else F[20],(255,255,255,255),2)
   textcenter(d,(270,824),l2,F[25] if len(l2)<26 else F[20],(255,215,134,255),2);break
 d.rectangle((28,905,512,907),fill=(255,255,255,55));d.rectangle((28,905,28+int(484*t/DUR),907),fill=(239,195,112,230))
 d.text((28,925),'MONARCHs EDIT',font=F[14],fill=(255,255,255,190));d.text((512,925),'ILLUSTRATIVE POV',font=F[14],fill=(255,255,255,150),anchor='ra')
 # Smooth cuts through black to prevent hard single-frame flashes.
 fade=min(1, max(0,(t-SCENES[n])/.18), max(0,(SCENES[n+1]-t)/.18))
 if fade<1:im=Image.blend(Image.new('RGBA',(W,H),(5,12,22,255)),im,fade)
 return im.convert('RGB')
def audio_bed(path):
 sr=48000;t=np.arange(sr*DUR,dtype=np.float32)/sr; audio=np.zeros(t.shape,dtype=np.float32)
 notes=[110,138.59,164.81,207.65,123.47,146.83,185.0,220]
 for i in range(120):
  start=i*.5;idx=int(start*sr);L=min(int(.9*sr),len(audio)-idx)
  if L<=0:break
  u=np.arange(L,dtype=np.float32)/sr; f=notes[(i//8*4+i%4)%len(notes)]; env=np.minimum(u/.025,1)*np.exp(-u*3.8)
  audio[idx:idx+L]+=.022*env*(np.sin(2*np.pi*f*u)+.28*np.sin(2*np.pi*f*2*u))
 for at in SCENES[:-1]:
  idx=int(at*sr);L=min(int(.6*sr),len(audio)-idx);u=np.arange(L,dtype=np.float32)/sr
  audio[idx:idx+L]+=.04*np.sin(2*np.pi*(86*u-24*u*u))*np.exp(-u*9)
 audio*=np.minimum(1,np.minimum(t/1.2,(DUR-t)/1.2)).clip(0,1)
 with wave.open(str(path),'wb') as f:f.setparams((1,2,sr,0,'NONE','not compressed'));f.writeframes((audio*32767).astype('<i2').tobytes())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default='deliverables/monarch-celebrity-pov-test.mp4');ap.add_argument('--stills',action='store_true');args=ap.parse_args()
 if args.stills:
  for t in (1.5,9.5,18.5,27,36,45,54):scene(t).save(ROOT/f'qa-{t}.jpg',quality=90)
  return
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as td:
  tmp=Path(td);vid=tmp/'picture.mp4';bed=tmp/'score.wav';audio_bed(bed)
  cmd=[ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(vid)]
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for f in range(FPS*DUR):
   p.stdin.write(scene(f/FPS).tobytes())
   if f%150==0:print('render',f,'/',FPS*DUR,flush=True)
  p.stdin.close()
  if p.wait():raise RuntimeError('Video encoding failed')
  ins=[]
  for i in range(1,8):ins+=['-i',str(ROOT/'audio'/f'{i:02}.wav')]
  filters=[]
  for i,at in enumerate(START,1):filters.append(f'[{i}:a]aresample=48000,adelay={int(at*1000)}:all=1,volume=1.0[v{i}]')
  filters.append('[8:a]volume=0.55[m]');filters.append(''.join(f'[v{i}]' for i in range(1,8))+'[m]amix=inputs=8:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]')
  subprocess.run([ff,'-y','-v','error','-i',str(vid),*ins,'-i',str(bed),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
if __name__=='__main__':main()
