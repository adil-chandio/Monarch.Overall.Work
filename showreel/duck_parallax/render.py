"""Frame-exact 2.5D documentary reconstruction: moving layers, no still slides.

Inputs: AI-generated isolated ship + duck cutouts, illustrative moving ocean
footage, Natural Earth geography, and the earlier narration/music mix. Visuals
are reconstructions and ocean flow is conceptual, not actual toy trajectories.
Requires Pillow, NumPy, imageio-ffmpeg and Linux DejaVu fonts.
"""
import argparse, json, math, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[2]; W,H,FPS=720,1280,30; DURATION=43.6
ASSET=Path(__file__).parent/'assets'; SRC=ROOT/'showreel/duck_cinema/assets/mga-waves-excerpt.mp4'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTS={s:ImageFont.truetype(FONT,s) for s in (19,24,32,43,48,58,72,86)}
R19=ImageFont.truetype(REG,19);R17=ImageFont.truetype(REG,17)
GOLD=(245,195,99,255);WHITE=(245,244,229,255)

def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)

def key_asset(path):
 img=Image.open(path).convert('RGB');rgb=np.array(img).astype(np.int16)
 r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
 dominance = g - np.maximum(r,b)
 alpha=np.where(g>80,np.clip(255-(dominance-15)*5,0,255),255).astype(np.uint8)
 # Only chroma-key dominant green; object colors and alpha are retained.
 rgba=np.dstack([rgb.astype(np.uint8),alpha]);im=Image.fromarray(rgba,'RGBA')
 box=im.getbbox()
 if box is None:raise ValueError(f'empty chroma mask for {path}')
 return im.crop(box)

DUCK=key_asset(ASSET/'duck.png');SHIP=key_asset(ASSET/'ship.png')

def prepare_map():
 data=json.loads((ROOT/'showreel/duck_documentary/natural_earth_110m_land.geojson').read_text())
 im=Image.new('RGBA',(W,H),(7,30,42,245));d=ImageDraw.Draw(im)
 def project(lon,lat):
  if lon<0:lon+=360
  return (int((lon-100)/175*W),int(1020-(lat-8)/75*850))
 for lat in range(10,80,10):
  y=project(180,lat)[1];d.line((0,y,W,y),fill=(25,65,74,200),width=1)
 for lon in range(100,280,20):
  x=project(lon,30)[0];d.line((x,90,x,1100),fill=(25,65,74,200),width=1)
 for feature in data['features']:
  g=feature['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  for poly in polys:
   if not poly:continue
   pts=[project(*p[:2]) for p in poly[0]]
   if len(pts)>2 and not any(abs(pts[i][0]-pts[i-1][0])>W*.7 for i in range(1,len(pts))):
    d.polygon(pts,fill=(53,83,83,255),outline=(120,151,146,255),width=2)
 x,y=project(-150,64);d.text((x-40,y-30),'ALASKA',font=FONTS[19],fill=GOLD)
 return im
MAP=prepare_map()

def sprite(im,asset,x,y,width,angle=0,opacity=255):
 h=int(width*asset.height/asset.width);obj=asset.resize((int(width),max(1,h)),Image.Resampling.LANCZOS)
 if angle:obj=obj.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 if opacity<255:obj.putalpha(obj.getchannel('A').point(lambda q:q*opacity//255))
 # opacity and body are independent from the real ocean backplane.
 im.alpha_composite(obj,(int(x-obj.width/2),int(y-obj.height/2)))

def waves(im,t):
 # Foreground sea sheen and compositional depth: projected curves move with the swell.
 d=ImageDraw.Draw(im,'RGBA')
 for k in range(8):
  y=725+k*63;pts=[(x,y+math.sin(x*.010+t*.9+k)*9) for x in range(-8,W+20,18)]
  d.line(pts,fill=(117,168,166,20+k*3),width=2)

def current(im,t):
 d=ImageDraw.Draw(im,'RGBA')
 for j in range(6):
  pts=[(x,570+j*63+27*math.sin(x*.008+j*.65+t*.35)) for x in range(35,690,8)]
  d.line(pts,fill=(89,176,176,100),width=2)
  a=(t*.14+j*.17)%1;x,y=pts[int(a*(len(pts)-1))];d.ellipse((x-5,y-5,x+5,y+5),fill=GOLD)

def labels(im,t,title,sub,start):
 d=ImageDraw.Draw(im,'RGBA');x=54-int(30*(1-ease((t-start)/.6)))
 # Type is intentionally short, safe-area bound; staggered easing, not a title card.
 d.text((54,60),'MONARCHS EDIT  /  THE INVISIBLE THREAD',font=FONTS[19],fill=(200,216,208,230))
 d.text((54,101),'STYLIZED RECONSTRUCTION',font=R17,fill=(188,202,199,210))
 f=FONTS[58] if max(map(len,title))<15 else FONTS[48]
 for j,line in enumerate(title):
  y=220+j*68+int(20*(1-ease((t-start-j*.08)/.55)))
  d.text((x,y),line,font=f,fill=WHITE if j==0 else GOLD,stroke_width=1,stroke_fill=(0,0,0,120))
 d.text((54,1020),sub,font=R19,fill=(221,226,212,235),stroke_width=1,stroke_fill=(0,0,0,110))
 d.rounded_rectangle((54,1110,666,1114),2,fill=(213,224,218,65));d.rounded_rectangle((54,1110,54+612*t/DURATION,1114),2,fill=GOLD)

def compose(t,bg):
 bg=bg.convert('RGBA');veil=Image.new('RGBA',(W,H),(3,20,29,130));im=Image.alpha_composite(bg,veil)
 # Scene objects occupy the middle plane. Foreground moves at a different rate.
 if t<3:
  u=t; sprite(im,SHIP,350+35*u,640-8*u,900+25*u,angle=-3+math.sin(t*.8)*1.8)
  waves(im,t);labels(im,t,['ONE ACCIDENT.','ONE OCEAN.'],'NORTH PACIFIC  /  1992',0)
 elif t<6.3:
  u=t-3
  for i in range(8):
   x=(i*167+u*(36+i*5))%900-80;y=635+(i%3)*115+math.sin(t+i)*12
   sprite(im,DUCK,x,y,85+i%3*20,angle=math.sin(t+i)*4)
  sprite(im,DUCK,380+u*20,760+math.sin(t*1.5)*13,320+u*15,angle=math.sin(t)*3)
  waves(im,t);labels(im,t,['THOUSANDS','OF TOYS.'],'A STRANGE SPILL',3)
 elif t<9.9:
  current(im,t);sprite(im,DUCK,380+math.sin(t*.6)*45,750,170,angle=3*math.sin(t))
  labels(im,t,['SOMETHING','INVISIBLE.'],'THE OCEAN IS ALWAYS MOVING',6.3)
 elif t<13.1:
  u=t-9.9;sprite(im,SHIP,338+u*36,675+u*4,880+u*30,angle=-2+math.sin(t)*2)
  d=ImageDraw.Draw(im,'RGBA');v=ease((u-.5)/2);x=460+v*130;y=660+v*220
  d.polygon([(x-37,y-14),(x+32,y-6),(x+34,y+28),(x-35,y+20)],fill=(185,110,60,255),outline=(241,188,111,255),width=3)
  waves(im,t);labels(im,t,['A CONTAINER','OVERBOARD.'],'STYLIZED  /  NOT ARCHIVAL FOOTAGE',9.9)
 elif t<17.2:
  u=t-13.1
  for i in range(15):
   x=(i*117+u*(20+i*3))%880-80;y=520+(i*119)%440+math.sin(t+i)*13
   sprite(im,DUCK,x,y,65+(i%3)*25,angle=math.sin(t+i)*4)
  sprite(im,DUCK,350+u*22,770+math.sin(t)*12,270+u*10,angle=math.sin(t)*3)
  waves(im,t);labels(im,t,['~29,000','FLOATING TOYS.'],'BATH TOYS  /  NOT ALL DUCKS',13.1)
 elif t<22.55:
  im=Image.alpha_composite(im,MAP);current(im,t);labels(im,t,['SOME REACHED','ALASKA.'],'ILLUSTRATIVE FLOW  /  NOT TOY ROUTES',17.2)
 elif t<29.3:
  im=Image.alpha_composite(im,MAP);current(im,t)
  st=22.55 if t<26.25 else 26.25
  title=['SIGHTINGS','BECAME CLUES.'] if t<26.25 else ['CURRENTS','AND WIND.']
  labels(im,t,title,'CONCEPTUAL GRAPHIC  /  NOT ACTUAL TRACKS',st)
 elif t<33.05:
  current(im,t);sprite(im,DUCK,380+math.sin(t)*35,750,190,angle=math.sin(t)*3)
  labels(im,t,['NOT THE WHOLE','OCEAN.'],'REAL CLUES  /  NOT A COMPLETE MAP',29.3)
 elif t<39.4:
  u=t-33.05;sprite(im,DUCK,360+u*9,750+math.sin(t*1.1)*15,360+u*14,angle=math.sin(t*.8)*3)
  waves(im,t);st=33.05 if t<36.3 else 36.3
  labels(im,t,['ONE TINY TOY.','A VAST SYSTEM.'] if t<36.3 else ['HIDDEN','CONNECTIONS.'],'THE INVISIBLE THREAD',st)
 else:
  current(im,t);sprite(im,DUCK,350+math.sin(t)*25,760+math.sin(t*.8)*10,300,angle=math.sin(t)*3)
  labels(im,t,['A NEW WAY','TO SEE.'],'MONARCHS EDIT',39.4)
 return im.convert('RGB')

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--audio',default=str(ROOT/'deliverables/monarch-invisible-thread-animated.mp4'));args=p.parse_args()
 ff=imageio_ffmpeg.get_ffmpeg_exe();dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  video=str(Path(tmp)/'picture.mp4')
  reader=subprocess.Popen([ff,'-v','error','-stream_loop','-1','-i',str(SRC),'-vf','fps=30,scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280','-an','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
  enc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',video],stdin=subprocess.PIPE)
  try:
   for n in range(round(DURATION*FPS)):
    raw=reader.stdout.read(W*H*3)
    if len(raw)!=W*H*3:raise RuntimeError('ocean source ended unexpectedly')
    frame=compose(n/FPS,Image.frombytes('RGB',(W,H),raw));enc.stdin.write(frame.tobytes())
    if n%300==0:print(f'rendered {n}/{round(DURATION*FPS)} frames',flush=True)
  finally:
   reader.terminate();reader.stdout.close();enc.stdin.close()
  if enc.wait():raise RuntimeError('picture encode failed')
  subprocess.run([ff,'-y','-v','error','-i',video,'-i',args.audio,'-map','0:v','-map','1:a','-t',str(DURATION),'-c:v','copy','-af','highpass=f=35,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000','-c:a','aac','-b:a','192k','-movflags','+faststart',str(dest)],check=True)
if __name__=='__main__':main()
