#!/usr/bin/env python3
"""Reference 04 procedural collage/motion adaptation.
python3 showreel/seven/render_04.py --reference /path/to/04.mp4

Images in assets/04-* are generated for this build; timings are editable below.
"""
from pathlib import Path
from functools import lru_cache
import argparse, math, subprocess, sys
import cv2, numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ffbin import ffmpeg
DIR=ROOT/'showreel/seven/assets';OUT=ROOT/'public/demo/monarch-reference-04.mp4'
W,H,FPS=720,1280,30
INK=(22,21,20);WINE=(118,0,18);RED=(160,0,27);PAPER=(233,229,216);WHITE=(248,244,233)
FONT=DIR/'Inter.ttf';BOLD=ROOT/'showreel/v2/assets/Poppins-Bold.ttf';COND=DIR/'Oswald.ttf'
@lru_cache(None)
def f(size,kind='r'):
 return ImageFont.truetype(str({'r':FONT,'b':BOLD,'c':COND}[kind]),size)
def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
def p(a,b,t):return ease((t-a)/(b-a))
def mix(a,b,v):return a+(b-a)*v

def txt(d,pos,s,size=35,col=INK,kind='b',anchor='mm'):
 d.text(pos,s,font=f(size,kind),fill=col,anchor=anchor)
def roundrect(d,box,r,fill,outline=None,width=1):
 d.rounded_rectangle(tuple(map(int,box)),radius=r,fill=fill,outline=outline,width=width)

def paper(w,h):
 rng=np.random.default_rng(4024);a=np.empty((h,w,3),np.float32);noise=rng.normal(0,1.45,(h,w))
 yy,xx=np.indices((h,w));dots=((xx+2*yy)%5==0)*4.0
 for j,base in enumerate(PAPER):a[:,:,j]=base+noise-dots
 return Image.fromarray(np.uint8(np.clip(a,0,255)),'RGB')
BG=paper(W,H)

def img(name):return Image.open(DIR/('04-'+name+'.png')).convert('RGB')
IMAGES={x:img(x) for x in ['handbag','beauty','shoe','store','analyst','person-a','person-b','person-c','hand-lens']}

def extract(name):
 # GrabCut is used only for the independently generated assets, never reference frames.
 source=IMAGES[name];hh=round(512*source.height/source.width)
 rgb=np.asarray(source.resize((512,hh),Image.Resampling.LANCZOS));bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
 mask=np.zeros((hh,512),np.uint8);bg=np.zeros((1,65),np.float64);fg=np.zeros((1,65),np.float64)
 if name=='store':rect=(18,65,476,400)
 elif name=='analyst':rect=(45,110,420,hh-120)
 else:rect=(70,110,370,hh-115)
 cv2.grabCut(bgr,mask,rect,bg,fg,4,cv2.GC_INIT_WITH_RECT)
 a=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype('uint8')
 a=cv2.GaussianBlur(a,(3,3),.7)
 return Image.fromarray(np.dstack([rgb,a]),'RGBA')
STORE=extract('store');PERSON=extract('analyst');HAND=extract('hand-lens')
# Remove the source lens; a clean transparent vector rim is drawn over the
# dashboard independently so the analytics remain visible through the glass.
h=np.array(HAND);h[:int(h.shape[0]*.418),:,3]=0;HAND=Image.fromarray(h,'RGBA')

def stamp(im,sprite,cx,cy,w=None,h=None,angle=0,shadow=True):
 sp=sprite
 if w is not None:
  if h is None:h=int(sp.height*w/sp.width)
  sp=sp.resize((max(1,int(w)),max(1,int(h))),Image.Resampling.LANCZOS)
 if angle:sp=sp.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 px=int(cx-sp.width/2);py=int(cy-sp.height/2)
 if shadow:
  # small local shadow cast onto the paper; never uses image ghost frames
  pad=25; m=Image.new('L',(sp.width+pad*2,sp.height+pad*2));m.paste(sp.getchannel('A'),(pad,pad))
  m=m.filter(ImageFilter.GaussianBlur(13)).point(lambda z:int(z*.38))
  im.paste((22,18,17),(px-pad-11,py-pad+19),m)
 im.paste(sp,(px,py),sp)

def star(cx,cy,r,n=10,inner=.42):
 return [(cx+math.cos(-math.pi/2+i*math.pi/n)*(r if i%2==0 else r*inner),cy+math.sin(-math.pi/2+i*math.pi/n)*(r if i%2==0 else r*inner)) for i in range(n*2)]

def make_card(name):
 im=Image.new('RGBA',(260,390),(0,0,0,0));d=ImageDraw.Draw(im)
 roundrect(d,(1,1,258,388),18,WINE,INK,2);roundrect(d,(8,8,251,381),13,(239,226,205))
 pic=ImageOps.fit(IMAGES[name],(232,254),Image.Resampling.LANCZOS,centering=(.5,.5));im.paste(pic,(14,23))
 d=ImageDraw.Draw(im);txt(d,(22,301),'MONARCH  /  01',13,INK,'b','lm');txt(d,(22,325),'CURATED GOODS',11,INK,'r','lm')
 roundrect(d,(15,345,244,375),7,RED);txt(d,(130,361),'EXPLORE',12,WHITE,'b')
 return im
CARDS={name:make_card(name) for name in ['handbag','beauty','shoe']}

def pointer(d,x,y,scale=1):
 pts=[(0,0),(0,63),(16,47),(28,69),(41,63),(29,41),(51,39)]
 d.polygon([(x+a*scale,y+b*scale) for a,b in pts],fill=INK)

def product_scene(im,t):
 d=ImageDraw.Draw(im);fan=p(.3,.95,t)
 if t>.35:
  d.polygon(star(360,505,420*fan,10,.36),fill=WINE)
  # concrete block and a receipt create the same depth and hierarchy as source
  if t>.55:
   d.polygon([(246,821),(460,818),(502,1280),(229,1280)],fill=(132,130,124))
   d.polygon([(246,821),(323,800),(500,1280),(460,1280)],fill=(101,100,96))
   d.polygon([(327,804),(499,802),(553,1158),(388,1167)],fill=(240,236,225),outline=(187,183,173),width=2)
   for k,line in enumerate(['SALES','ORDER 01     1','ORDER 02     1','ORDER 03     1','TOTAL       3']):txt(d,(431,842+k*48),line,15,INK,'c')
  txt(d,(360,292),'YOUR STORE IS SELLING',36,INK,'b')
 # Side cards swing out from the stack; center card stays in front.
 stamp(im,CARDS['beauty'],mix(360,220,fan),mix(720,555,fan),w=mix(380,235,fan),angle=mix(-5,32,fan))
 stamp(im,CARDS['shoe'],mix(365,500,fan),mix(720,555,fan),w=mix(380,235,fan),angle=mix(5,-32,fan))
 stamp(im,CARDS['handbag'],360,mix(735,548,fan),w=mix(380,235,fan),angle=0)

def ad_sprite(name):
 card=Image.new('RGBA',(220,235),WHITE+(255,));d=ImageDraw.Draw(card)
 roundrect(d,(1,1,218,233),14,WHITE,INK,2);d.rectangle((2,2,218,23),fill=(193,187,178))
 d.ellipse((8,7,18,17),fill=RED)
 pic=ImageOps.fit(IMAGES[name],(195,155),Image.Resampling.LANCZOS);card.paste(pic,(12,30))
 d=ImageDraw.Draw(card);txt(d,(110,210),'MONARCH  /  EDIT',12,INK,'b')
 return card
ADS={x:ad_sprite(x) for x in ['handbag','shoe','beauty']}

def spotlight(im,t):
 d=ImageDraw.Draw(im);q=p(1.75,2.35,t);x=mix(-170,75,q);y=685
 # projected wine beam and a flashlight-shaped lamp
 d.polygon([(x+210,y-25),(W,350),(W,1220),(x+210,y+25)],fill=WINE)
 d.rounded_rectangle((x,y-30,x+185,y+30),radius=24,fill=(35,36,36),outline=(95,96,93),width=4)
 d.polygon([(x+170,y-28),(x+207,y-51),(x+238,y-42),(x+238,y+42),(x+207,y+51),(x+170,y+28)],fill=(30,30,30))
 d.ellipse((x+212,y-44,x+239,y+44),fill=(98,5,18))
 for name,cx,cy,st in [('handbag',540,580,2.15),('shoe',580,845,2.7)]:
  k=p(st,st+.4,t)
  if k:stamp(im,ADS[name],cx,cy,w=190*k,shadow=True)
 if t>2.85:txt(ImageDraw.Draw(im),(580,1070),'THINK BIGGER',28,WHITE)

def store_scene(im,t):
 d=ImageDraw.Draw(im);d.rectangle((0,790,W,H),fill=WINE)
 q=p(4.35,6.25,t);size=int(mix(320,650,q));stamp(im,STORE,360,725-size*.2,w=size,h=size,shadow=True)
 if t>5.3:txt(ImageDraw.Draw(im),(360,315),'BUILD WHAT COMES NEXT',34)
 pointer(ImageDraw.Draw(im),mix(240,500,p(4.55,6.6,t)),1040,1.3)

def intro_monarch(im,t):
 d=ImageDraw.Draw(im);txt(d,(360,575),'MONARCH',72,INK,'b')
 if t>7.45:txt(d,(360,690),'STARTS WITH YOUR STORE',29)
 pointer(d,175,1000,1.2)

def product_row(im,t):
 d=ImageDraw.Draw(im);txt(d,(360,200),'WHAT SELLS BEST?',43)
 for i,(x,col) in enumerate([(0,(163,141,128)),(240,(221,211,193)),(480,(128,133,108))]):
  shift=int((1-p(8.45+i*.12,8.8+i*.12,t))*250)
  card=Image.new('RGBA',(225,700),col+(255,));pic=ImageOps.fit(IMAGES['beauty'],(225,700),Image.Resampling.LANCZOS)
  if i==1:pic=Image.blend(pic,ImageOps.colorize(ImageOps.grayscale(pic),(34,29,27),(245,239,230)),.65)
  if i==2:pic=Image.blend(pic,ImageOps.colorize(ImageOps.grayscale(pic),(25,35,22),(224,231,199)),.6)
  card.paste(pic,(0,0))
  mask=Image.new('L',(225,700));ImageDraw.Draw(mask).rounded_rectangle((0,0,224,699),radius=48,fill=255);card.putalpha(mask)
  stamp(im,card,x+112,660+shift,w=225,h=700,shadow=False)
 pointer(ImageDraw.Draw(im),385,780,1.2)

def persona_sprite(name,label):
 im=Image.new('RGBA',(260,300),WHITE+(255,));photo=ImageOps.fit(IMAGES[name],(246,240),Image.Resampling.LANCZOS);im.paste(photo,(7,6))
 d=ImageDraw.Draw(im);txt(d,(15,274),label,17,INK,'b','lm')
 for i in range(4):d.rectangle((201+i*11,281-8-i*6,208+i*11,281),fill=INK)
 return im
PEOPLE=[persona_sprite('person-a','AUDIENCE A'),persona_sprite('person-b','AUDIENCE B'),persona_sprite('person-c','AUDIENCE C')]

def audience_scene(im,t):
 q=p(9.72,10.2,t)
 for i,(x,y) in enumerate([(515,230),(424,550),(550,870)]):stamp(im,PEOPLE[i],x,mix(y+170,y,q),w=260,angle=[-7,3,0][i])
 txt(ImageDraw.Draw(im),(165,780),"WHO'S",42);txt(ImageDraw.Draw(im),(165,840),'BUYING?',42)

def question_scene(im,t):
 stamp(im,PERSON,365,1010,w=720,shadow=True)
 stamp(im,ADS['shoe'],210,280,w=200,angle=7)
 # phone UI mock, with no fabricated review data
 ph=Image.new('RGBA',(180,260),INK+(255,));d=ImageDraw.Draw(ph);roundrect(d,(16,23,164,242),12,WHITE);d.ellipse((27,40,53,66),fill=RED)
 for j in range(5):d.rounded_rectangle((30,83+j*25,150-(j%2)*23,89+j*25),2,fill=(165,160,152))
 stamp(im,ph,550,270,w=180,shadow=True)
 d=ImageDraw.Draw(im);txt(d,(365,550),'WHERE DO THEY',44);txt(d,(365,608),'HESITATE?',44)

def tile(kind):
 im=Image.new('RGBA',(236,236));d=ImageDraw.Draw(im)
 roundrect(d,(4,12,228,228),25,INK);roundrect(d,(4,4,228,218),24,WHITE);roundrect(d,(13,13,219,210),18,RED)
 col=WHITE;cx=116;cy=112
 if kind=='target':
  for r in [64,43,21]:d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=col,width=8)
  d.line((cx-5,cy+5,cx+55,cy-55),fill=col,width=10);d.polygon([(cx+38,cy-61),(cx+75,cy-75),(cx+61,cy-38)],fill=col)
 elif kind=='bulb':
  d.ellipse((75,47,157,129),outline=col,width=9);d.line((84,119,96,143,138,143,149,119),fill=col,width=9);d.line((99,156,135,156),fill=col,width=8)
  for a in range(0,360,45):
   A=math.radians(a);d.line((cx+66*math.cos(A),cy+66*math.sin(A),cx+80*math.cos(A),cy+80*math.sin(A)),fill=col,width=6)
 elif kind=='image':
  roundrect(d,(50,52,182,168),9,None,col,8);d.ellipse((72,68,95,91),fill=col);d.polygon([(60,153),(97,111),(119,134),(143,105),(173,153)],fill=col)
 elif kind=='social':
  roundrect(d,(51,47,181,177),32,None,col,9);d.ellipse((83,79,149,145),outline=col,width=9);d.ellipse((151,68,166,83),fill=col)
 elif kind=='chart':
  for i,h in enumerate([41,65,85]):d.rectangle((65+i*35,166-h,86+i*35,166),fill=col)
  d.line((55,101,93,79,117,92,165,49),fill=col,width=9);d.line((143,49,165,49,165,71),fill=col,width=8)
 elif kind=='gear':
  d.ellipse((60,57,172,169),outline=col,width=10);d.ellipse((93,90,139,136),outline=col,width=8)
  for a in range(0,360,45):
   A=math.radians(a);d.line((cx+51*math.cos(A),cy+51*math.sin(A),cx+75*math.cos(A),cy+75*math.sin(A)),fill=col,width=11)
 elif kind=='cart':
  d.line((50,69,69,69,82,142,158,142,175,92,74,92),fill=None if False else col,width=9)
  d.ellipse((84,156,103,175),fill=col);d.ellipse((143,156,162,175),fill=col)
  d.line((83,108,166,108),fill=col,width=4);d.line((83,125,161,125),fill=col,width=4)
 return im
TILES={name:tile(name) for name in ['target','bulb','image','social','chart','gear','cart']}

def make_map():
 im=paper(1440,3300);d=ImageDraw.Draw(im)
 pts=[(540,360),(1020,800),(320,1250),(1050,1620),(500,1990),(1050,2410),(590,2880)]
 # black hand-drawn connectors, layered behind every tile
 for i in range(len(pts)-1):
  x1,y1=pts[i];x2,y2=pts[i+1];d.line((x1,y1,x1+75,y1+160,x2-65,y2-100,x2,y2),fill=(38,35,33),width=5,joint='curve')
 for (x,y),kind,ang in zip(pts,['target','bulb','image','social','chart','gear','cart'],[0,-15,0,0,0,0,0]):
  ImageDraw.Draw(im).polygon(star(x+112,y-108,46,8,.38),fill=INK)
  stamp(im,TILES[kind],x,y,w=236,angle=ang)
 return im
MAP=make_map()

def icons_scene(t):
 # A continuous virtual camera travels down a large connected board.
 keys=[(13.7,200,-100),(14.7,180,0),(15.7,390,480),(16.8,40,800),(18,410,1300),(19.3,220,1650),(20.35,370,2050),(21.55,240,2240)]
 for a,b in zip(keys,keys[1:]):
  if a[0]<=t<=b[0]:
   z=p(a[0],b[0],t);x=int(mix(a[1],b[1],z));y=int(mix(a[2],b[2],z));break
 else:x,y=keys[-1][1:]
 x=max(0,min(720,x));y=max(0,min(2020,y))
 return MAP.crop((x,y,x+W,y+H))

def test_scene(im,t):
 for i,(x,w,yy) in enumerate([(145,155,615),(360,210,575),(575,235,560)]):
  z=p(23.2+i*.12,23.55+i*.12,t)
  if z<=0:continue
  card=Image.new('RGBA',(240,410),WHITE+(255,));pic=ImageOps.fit(IMAGES['beauty'],(220,300),Image.Resampling.LANCZOS);card.paste(pic,(10,10))
  d=ImageDraw.Draw(card);txt(d,(20,337),'CREATIVE '+chr(65+i),15,INK,'b','lm');txt(d,(20,374),'TEST VERSION',12,INK,'r','lm')
  stamp(im,card,x,yy+(1-z)*160,w=w)
 txt(ImageDraw.Draw(im),(360,975),'TEST THE MESSAGE & ANGLE',31)

def folder_scene(im,t):
 q=p(24.72,25.15,t);x=360;y=mix(950,705,q);sprite=Image.new('RGBA',(465,600));d=ImageDraw.Draw(sprite)
 d.rectangle((30,30,445,585),fill=(202,202,205));d.rectangle((10,10,425,565),fill=(153,153,146),outline=(81,81,77),width=3)
 d.arc((60,8,100,145),90,270,fill=INK,width=5);d.line((415,235,455,255),fill=INK,width=7);d.rectangle((440,220,465,285),fill=INK)
 txt(d,(225,388),'READ THE',61,INK,'b');txt(d,(225,468),'RESULTS',61,INK,'b')
 stamp(im,sprite,x,y,w=465,angle=mix(-8,0,q))

def analytics(im,t):
 # Redraw an editable analytics dashboard, then independently animate the lens.
 d=ImageDraw.Draw(im);d.rectangle((36,300,684,823),fill=(31,28,27));d.rectangle((48,312,672,811),fill=(243,233,218))
 txt(d,(95,356),'MONARCH  /  ANALYTICS',21,INK,'b','lm');txt(d,(95,402),'PERFORMANCE OVERVIEW',15,INK,'r','lm')
 for i in range(10):
  h=(i*19+46)%135+40;d.rectangle((80+i*25,655-h,95+i*25,655),fill=RED if i>4 else (130,128,125))
 d.line([(x,690-65*math.sin(x/95)) for x in range(345,650,6)],fill=RED,width=7)
 txt(d,(95,748),'ILLUSTRATIVE DATA',17,INK,'b','lm')
 d.rectangle((175,842,545,855),fill=(88,84,79));d.rectangle((315,823,404,955),fill=(110,108,102));d.rectangle((215,950,505,975),fill=INK)
 # Move the hand/lens as a distinct composited layer across the screen.
 cx=mix(440,285,p(26.45,29.30,t));width=650;height=int(HAND.height*width/HAND.width);cy=1000
 lensy=int(cy-height/2+.297*height);r=int(.205*width)
 d=ImageDraw.Draw(im);d.ellipse((cx-r+8,lensy-r+10,cx+r+8,lensy+r+10),outline=(120,110,104),width=8)
 d.ellipse((cx-r,lensy-r,cx+r,lensy+r),outline=(95,16,22),width=9)
 d.ellipse((cx-r+8,lensy-r+8,cx+r-8,lensy+r-8),outline=(239,228,220),width=3)
 stamp(im,HAND,cx,cy,w=width,shadow=True)

def frame(i):
 t=i/FPS
 if 13.7<=t<21.7:return icons_scene(t)
 im=BG.copy();d=ImageDraw.Draw(im)
 if t<1.75:product_scene(im,t)
 elif t<4.15:spotlight(im,t)
 elif t<6.8:store_scene(im,t)
 elif t<8.45:intro_monarch(im,t)
 elif t<9.72:product_row(im,t)
 elif t<10.8:audience_scene(im,t)
 elif t<12.75:question_scene(im,t)
 elif t<13.7:txt(d,(360,640),'BUILD A GROWTH SYSTEM',30)
 elif t<23.2:txt(d,(360,640),"WE DON'T JUST LAUNCH AND WAIT",27)
 elif t<24.72:test_scene(im,t)
 elif t<26.45:folder_scene(im,t)
 elif t<29.75:analytics(im,t)
 elif t<33.05:
  if t<30.5:s='IF YOU HAVE'
  elif t<31.5:s='A STRONG PRODUCT'
  else:s='AND REAL SALES'
  txt(d,(360,630),s,38)
 else:
  txt(d,(360,574),"LET'S BUILD",40)
  txt(d,(360,650),'MONARCH',68,INK,'b')
  if t>34.2:txt(d,(360,718),'YOUR CREATIVE GROWTH PARTNER',24)
 return im

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--reference',required=True);args=ap.parse_args()
 OUT.parent.mkdir(parents=True,exist_ok=True);tmp=OUT.with_suffix('.silent.mp4')
 proc=subprocess.Popen([ffmpeg(),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
 try:
  for i in range(1097):
   proc.stdin.write(frame(i).tobytes())
   if i%90==0:print(f'{i}/1097 frames',flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('video encoding failed')
  subprocess.run([ffmpeg(),'-y','-v','error','-i',str(tmp),'-i',args.reference,'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(1097/30),'-movflags','+faststart',str(OUT)],check=True)
 finally:
  if proc.poll() is None:proc.kill();proc.wait()
  tmp.unlink(missing_ok=True)
 print('Wrote',OUT)
if __name__=='__main__':main()
