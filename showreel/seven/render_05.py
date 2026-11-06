#!/usr/bin/env python3
"""Reference 05 4:3 MONARCH motion adaptation.
python3 showreel/seven/render_05.py --reference /path/to/05.mp4
"""
from pathlib import Path
from functools import lru_cache
import argparse,math,subprocess,sys
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ffbin import ffmpeg
DIR=ROOT/'showreel/seven/assets';OUT=ROOT/'public/demo/monarch-reference-05.mp4'
W,H,FPS=960,720,30;INK=(20,18,19);RED=(178,0,28);WHITE=(247,247,245)
FONT=DIR/'Inter.ttf'; BOLD=ROOT/'showreel/v2/assets/Poppins-Bold.ttf'
@lru_cache(None)
def font(n,k='r'):return ImageFont.truetype(str(BOLD if k=='b' else FONT),n)
def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
def p(a,b,t):return ease((t-a)/(b-a))
def mix(a,b,k):return a+(b-a)*k
def text(d,pos,s,size=26,col=INK,k='r',anchor='mm'):d.text(pos,s,font=font(size,k),fill=col,anchor=anchor)

def vignette(dark=False):
 yy,xx=np.mgrid[:H,:W].astype(np.float32);dist=((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2
 rng=np.random.default_rng(5004);noise=rng.normal(0,1.6,(H,W))
 if dark:v=19-4*np.minimum(dist,2)+noise
 else:v=241-26*np.minimum(dist/1.7,1)+noise
 a=np.uint8(np.clip(v,0,255));return Image.fromarray(np.stack([a,a,a],2),'RGB')
LIGHT=vignette(False);DARK=vignette(True);BLACK=Image.new('RGB',(W,H),(0,0,0))

def keyed(name,red=False):
 im=Image.open(DIR/('05-'+name+'.png')).convert('RGB');im.thumbnail((600,1050),Image.Resampling.LANCZOS)
 rgb=np.asarray(im).astype(np.float32);r=rgb[:,:,0];g=rgb[:,:,1];b=rgb[:,:,2]
 strength=g-np.maximum(r,b);alpha=np.uint8(np.clip((100-strength)*3,0,255));alpha=cv2.GaussianBlur(alpha,(3,3),.6)
 # neutralize green fringe and optionally light the figure in MONARCH red
 rgb[:,:,1]=np.minimum(g,np.maximum(r,b))
 if red:
  lum=rgb[:,:,0]*.30+rgb[:,:,1]*.59+rgb[:,:,2]*.11
  rgb[:,:,0]=np.clip(lum*1.45,0,255);rgb[:,:,1]=lum*.13;rgb[:,:,2]=lum*.18
 return Image.fromarray(np.dstack([np.uint8(np.clip(rgb,0,255)),alpha]),'RGBA')
PROFILE=keyed('character-profile',True);BACK=keyed('character-back',True);HAND=keyed('hand',True)
ICONS={p.stem:Image.open(p).convert('RGBA') for p in (DIR/'05-icons').glob('*.png')}
# The end-card butterfly is recolored for the MONARCH palette.
px=np.array(ICONS['butterfly']);lum=px[:,:,:3].astype(np.uint16).mean(axis=2).astype(np.uint8)
px[:,:,0]=np.minimum(255,lum.astype(np.uint16)*2);px[:,:,1]=lum//5;px[:,:,2]=lum//5
ICONS['butterfly']=Image.fromarray(px,'RGBA')

def put(im,sprite,x,y,w,h=None,angle=0,opacity=255):
 if h is None:h=int(sprite.height*w/sprite.width)
 s=sprite.resize((max(1,int(w)),max(1,int(h))),Image.Resampling.LANCZOS)
 if angle:s=s.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 if opacity<255:
  a=s.getchannel('A').point(lambda z:z*max(0,opacity)//255);s.putalpha(a)
 im.paste(s,(int(x-s.width/2),int(y-s.height/2)),s)

def icon(im,name,x,y,size=80,angle=0):
 # nearest-neighbour enlargement creates the small game-sprite treatment.
 src=ICONS[name].resize((32,32),Image.Resampling.LANCZOS).resize((int(size),int(size)),Image.Resampling.NEAREST)
 put(im,src,x,y,size,size,angle)

def star(cx,cy,r,n=8):
 return [(cx+math.cos(i*math.pi/n-math.pi/2)*(r if i%2==0 else r*.28),cy+math.sin(i*math.pi/n-math.pi/2)*(r if i%2==0 else r*.28)) for i in range(n*2)]

def typed(d,pos,s,t,start,end,size=27,col=INK,k='r',anchor='mm',cursor=False):
 count=max(0,min(len(s),math.ceil(len(s)*p(start,end,t))))
 show=s[:count];text(d,pos,show,size,col,k,anchor)
 if cursor and t<end+.1:
  width=d.textlength(show,font=font(size,k));x=pos[0]+width/2+8 if anchor=='mm' else pos[0]+width+8
  d.rectangle((x,pos[1]-size*.45,x+7,pos[1]+size*.45),fill=col)

def opening(t):
 im=LIGHT.copy();d=ImageDraw.Draw(im)
 if t<.27:
  # hand-sketched opener that rapidly gives way to oversized type
  d.line([(260,600),(285,90)],fill=INK,width=12);d.line([(310,600),(325,115)],fill=INK,width=12)
  d.line([(255,395),(390,380)],fill=INK,width=10);d.ellipse((360,250,465,370),outline=INK,width=9)
  d.line([(500,125),(540,440),(580,275),(630,440),(720,110)],fill=INK,width=10)
 elif t<.72:
  n=int(mix(380,65,p(.27,.72,t)));text(d,(W/2,360),'how do you know',n,INK,'b')
 else:
  typed(d,(480,360),'how do you know your ideas are becoming something new?',t,.8,2.35,24,INK,'r')
  if 1.25<t<1.85:
   d.arc((370,300,610,425),210,320,fill=(50,45,45),width=2)
  if t>2.05:
   for name,x,y,s,delay in [('camera',410,207,65,2.1),('bulb',640,240,52,2.2),('note',550,475,72,2.22),('plant',630,605,100,2.3)]:
    q=p(delay,delay+.25,t)
    if q:icon(im,name,x,y,max(1,int(s*q)))
  if t>2.42:
   # Restrained four-point red flare on a black intrusion: keep the sentence legible.
   q=p(2.42,3.4,t);d=ImageDraw.Draw(im)
   d.ellipse((-720,-120,-50+275*q,840),fill=(12,10,11))
   pts=[(-20,240),(250*q,45),(90*q,360),(200*q,560),(-20,475)]
   d.polygon(pts,fill=(183,0,27))
   typed(d,(480,360),'how do you know your ideas are becoming something new?',t,.8,2.35,24,INK,'r')
   # Invert the portion over the dark wipe so no words disappear.
   contrast=Image.new('RGBA',(W,H),(0,0,0,0))
   typed(ImageDraw.Draw(contrast),(480,360),'how do you know your ideas are becoming something new?',t,.8,2.35,24,WHITE,'r')
   edge=max(0,min(W,int(-50+275*q)))
   if edge:
    part=contrast.crop((0,0,edge,H));im.paste(part,(0,0),part)
 return im

def character_scene(t):
 im=BLACK.copy()
 if t<5.75:
  # Single AI-derived still, subtly translated/rotated rather than fake video.
  tilt=mix(-7,4,p(3.78,5.6,t));cy=mix(545,530,p(3.8,5.6,t))
  put(im,PROFILE,565,cy,455,angle=tilt)
  d=ImageDraw.Draw(im);text(d,(210,360),"You'll feel it.",25,WHITE)
  # white orbit tracks the head and leaves no prior-frame ghost
  a=int(mix(190,360,p(4.15,5.6,t)));d.arc((405,285,745,465),a,a+210,fill=WHITE,width=3)
 else:
  z=p(5.75,6.1,t);im=Image.blend(BLACK,LIGHT,z)
  put(im,BACK,520,580,440,angle=mix(-2,0,z))
  d=ImageDraw.Draw(im);text(d,(212,350),'before anyone sees',24,WHITE if z<.45 else INK)
 return im

ARR=[('camera',485,405,135),('headphones',310,450,130),('guitar',215,380,95),('bonsai',585,425,120),('stopwatch',710,420,120),('puzzle',835,300,125),('note',285,250,100),('bulb',490,235,90),('compass',650,230,105),('key',790,225,90),('books',150,320,100),('teapot',820,435,85)]
def spread(t,variant=0):
 im=LIGHT.copy();d=ImageDraw.Draw(im)
 if variant==0:
  q=p(6.35,7.0,t)
  for i,(name,x,y,s) in enumerate(ARR):
   a=p(6.35+i*.024,6.7+i*.024,t);scale=max(1,int(s*a))
   xx=mix(480,x,q);yy=mix(350,y,q);icon(im,name,xx,yy,scale,angle=4*math.sin(t*3+i))
 elif variant==1:
  subset=[('alarm',110,350,115),('coffee',200,340,85),('note',310,330,95),('headphones',430,375,120),('pencil',535,340,100),('bottle',640,390,95),('books',750,330,110),('stopwatch',850,350,105)]
  for i,(name,x,y,s) in enumerate(subset):icon(im,name,x+3*math.sin(t*4+i),y,s,angle=2*math.sin(t*3+i))
 else:
  for i,(name,x,y,s) in enumerate(ARR):icon(im,name,x+8*math.sin(t*5+i),y,s,angle=3*math.sin(t*4+i))
 return im

def object_scene(t,name,word,start,end):
 im=DARK.copy();d=ImageDraw.Draw(im);q=p(start,start+.35,t)
 if name=='mouse':
  d.polygon(star(310,400,155*q),fill=(202,6,35));size=mix(90,220,q);icon(im,name,310,405,size,angle=-25)
 elif name=='pencil':
  d.polygon([(0,625),(220,505),(455,520),(960,240),(960,340),(535,605),(285,625),(130,720),(0,720)],fill=(188,0,25))
  icon(im,name,300,380,mix(80,230,q),angle=-20)
 else:
  icon(im,name,310,370,mix(100,210,q));
  d.ellipse((690,70,730,110),fill=RED);d.ellipse((770,95,795,120),fill=RED)
 d=ImageDraw.Draw(im);typed(d,(700,410),word,t,start+.05,end,42,WHITE,'r',cursor=True)
 d.arc((420,430,600,570),0,110,fill=(230,230,230),width=3);d.line((690,120,850,10),fill=(210,210,210),width=3)
 return im

def ring_scene(t):
 im=LIGHT.copy();d=ImageDraw.Draw(im)
 names=['stopwatch','teapot','yarn','plant','moon','candle','hourglass','door','note','bonsai','bulb','camera']
 center=(480,360);angle=t*.35
 for i,name in enumerate(names):
  a=2*math.pi*i/len(names)+angle;x=center[0]+250*math.cos(a);y=center[1]+250*math.sin(a)
  icon(im,name,x,y,90,angle=math.sin(t+i)*4)
 d.ellipse((457,337,503,383),fill=INK)
 return im

def float_scene(t):
 im=LIGHT.copy()
 for i,name in enumerate(['camera','bulb','key','yarn','books','door','note','compass','puzzle','moon','plant']):
  a=i*2.399+(t-13)*.18;x=480+320*math.cos(a);y=360+235*math.sin(a)
  icon(im,name,x,y,80+10*math.sin(i*3),angle=math.sin(t+i)*7)
 d=ImageDraw.Draw(im)
 for i in range(5):
  x=90+i*170;y=130+(i%3)*170;d.ellipse((x,y,x+14,y+14),fill=INK)
 return im

def hand_scene(t):
 im=BLACK.copy();q=p(13.78,14.2,t)
 put(im,HAND,mix(590,575,q),mix(720,550,q),500,angle=mix(-10,5,p(13.85,15.5,t)))
 d=ImageDraw.Draw(im);text(d,(190,395),'in the way',25,WHITE)
 if t>14.35:typed(d,(775,315),'we create',t,14.35,14.9,25,WHITE,cursor=True)
 for i in range(5):
  x=335+i*82;d.ellipse((x,65+i%2*12,x+5+i%3,70+i%2*12),fill=WHITE)
 if t<14.65:
  d.arc((340,270,680,470),int(280*p(13.8,14.6,t)),int(280*p(13.8,14.6,t))+230,fill=(235,235,235),width=2)
 return im

def ending(t):
 im=DARK.copy();d=ImageDraw.Draw(im)
 letters='MONARCH'
 for i,ch in enumerate(letters):
  if t>15.93+i*.12:text(d,(75+i*115+(95 if i>=3 else 0),355),ch,35,WHITE)
 if t<16.95:icon(im,'bulb',410,355,75)
 else:icon(im,'butterfly',410,355,85)
 return im

def frame(i):
 t=i/FPS
 if t<3.78:return opening(t)
 if t<6.35:return character_scene(t)
 if t<8.20:return spread(t,0)
 if t<9.30:return object_scene(t,'mouse','ideas.',8.20,8.92)
 if t<9.82:return spread(t,1)
 if t<10.78:return object_scene(t,'pencil','craft.',9.82,10.45)
 if t<11.33:return spread(t,2)
 if t<11.95:return object_scene(t,'hourglass','focus.',11.33,11.77)
 if t<12.95:return ring_scene(t)
 if t<13.78:return float_scene(t)
 if t<15.86:return hand_scene(t)
 if t<17.35:return ending(t)
 im=LIGHT.copy();d=ImageDraw.Draw(im);q=p(17.35,17.75,t)
 text(d,(480,360),'MONARCH',max(9,int(mix(30,18,q))),INK,'r')
 return im

def main():
 a=argparse.ArgumentParser();a.add_argument('--reference',required=True);args=a.parse_args()
 OUT.parent.mkdir(parents=True,exist_ok=True);tmp=OUT.with_suffix('.silent.mp4')
 proc=subprocess.Popen([ffmpeg(),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
 try:
  for i in range(542):
   proc.stdin.write(frame(i).tobytes())
   if i%60==0:print(f'{i}/542 frames',flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('render failed')
  subprocess.run([ffmpeg(),'-y','-v','error','-i',str(tmp),'-i',args.reference,'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(542/30),'-movflags','+faststart',str(OUT)],check=True)
 finally:
  if proc.poll() is None:proc.kill();proc.wait()
  tmp.unlink(missing_ok=True)
 print('Wrote',OUT)
if __name__=='__main__':main()
