"""G1 original style package and G2 graphics-motion DEVELOPMENT proof, not the final film.
No footage from V3/V4 or competitors. Generated scene plates remain still concepts;
the continuous motion proof uses new authored process/diagram animation, not pans over plates.
"""
import json,math,subprocess,hashlib,wave,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps
import imageio_ffmpeg
B=Path(__file__).resolve().parent;ROOT=B.parents[2];OUT=ROOT/'.cache/extinct-v5-development';OUT.mkdir(parents=True,exist_ok=True)
STYLE=B/'style';STYLE.mkdir(exist_ok=True);W,H=1920,1080;FPS=30
plan=json.loads((B.parent/'film-v5-plan/storyboard.json').read_text());manifest=json.loads((B.parent/'film-v3/manifest.json').read_text());beats=plan['beats'];FF=imageio_ffmpeg.get_ffmpeg_exe()
START=next(r['start_frame'] for r in beats if r['id']=='V5-18');END=next(r['end_frame'] for r in beats if r['id']=='V5-26');N=END-START
IVORY='#eee7d6';MUTED='#a1b4b6';COPPER='#d0a878';TEAL='#66c4c3'
fonts={}
def font(size,serif=False):
 key=(size,serif)
 if key not in fonts:fonts[key]=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/'+('DejaVuSerif.ttf' if serif else 'DejaVuSans.ttf'),size)
 return fonts[key]
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def text(d,pos,s,size=28,color=IVORY,serif=False):d.text(pos,s,font=font(size,serif),fill=color,stroke_width=0)
def wrap(d,pos,s,size=30,width=660,color=MUTED,serif=False):
 words=s.split();line='';y=pos[1]
 for word in words:
  test=(line+' '+word).strip()
  if d.textlength(test,font=font(size,serif))>width and line:text(d,(pos[0],y),line,size,color,serif);y+=size*1.45;line=word
  else:line=test
 if line:text(d,(pos[0],y),line,size,color,serif)
def base(seed=0):
 y,x=np.mgrid[0:H,0:W];r=np.sqrt(((x-W*.39)/W)**2+((y-H*.37)/H)**2);light=np.exp(-r*3.5);rng=np.random.default_rng(seed);grain=rng.normal(0,.8,(H,W));a=np.empty((H,W,3),dtype=np.uint8)
 for c,(lo,hi) in enumerate([(7,12),(19,22),(25,25)]):a[:,:,c]=np.clip(lo+light*hi+grain,0,255)
 return Image.fromarray(a)
BG=base(4)
MATERIAL=ImageOps.fit(Image.open(STYLE/'mineral-material.png').convert('RGB'),(W,H))
# Original generated material plate; only the newly authored foreground mechanism animates.
mask=np.zeros((H,W,4),dtype=np.uint8);mask[:,:,:3]=[4,15,20];mask[:,:,3]=np.tile(np.linspace(245,35,W).astype(np.uint8),(H,1));MATERIAL=Image.alpha_composite(MATERIAL.convert('RGBA'),Image.fromarray(mask)).convert('RGB')
def header(im,chapter,qualifier='SCHEMATIC ILLUSTRATION · NOT ACTUAL SEQUENCE READS'):
 d=ImageDraw.Draw(im);text(d,(86,58),'E X T I N C T   L I F E',23);d.line((86,104,148,104),fill=COPPER,width=3);text(d,(86,125),chapter.upper(),21,MUTED);text(d,(86,1007),qualifier,22,MUTED)
def sphere(d,x,y,r,color=0):
 # Deliberate shaded 2.5D vector construction, not a claim of a 3D rig.
 palette=[(91,143,145),(146,128,100),(166,172,160)];v=palette[color%3]
 for q in range(int(r),0,-2):
  k=1-q/max(r,1);gain=.40+.60*math.sqrt(max(0,1-(1-k)**2));col=tuple(int(c*gain) for c in v);dx=-r*.18*k;dy=-r*.20*k
  d.ellipse((x-q+dx,y-q+dy,x+q+dx,y+q+dy),fill=col)
 d.ellipse((x-r*.40,y-r*.47,x-r*.1,y-r*.20),fill=tuple(min(255,int(c*1.1)) for c in v))
def fragment(d,x,y,t,scale=1,damaged=False):
 pts=[]
 for i in range(7):
  xx=x+i*62*scale;yy=y+math.sin(i*.85+t*.3)*22*scale;pts.append((xx,yy))
 for i,(a,b) in enumerate(zip(pts,pts[1:])):
  if not(damaged and i==3):d.line((*a,*b),fill='#9bb9b1',width=max(2,int(5*scale)))
 for i,(xx,yy) in enumerate(pts):sphere(d,xx,yy,14*scale,i)
def mineral(im,t,mode):
 d=ImageDraw.Draw(im)
 # Different mineral geometry/staging for binding, protection and release tasks.
 if mode in ['cold','binding','release']:
  # Tactile material is a concept plate, not a claim of specimen footage or an exact mineral lattice.
  d.line((870,805,1280,615,1690,693),fill='#829997',width=2)
  if mode=='cold':fragment(d,1020,400,t,1.25,True);text(d,(1120,345),'LOSS SLOWS — NOT STOPS',23,MUTED)
  elif mode=='binding':
   p=ease(t/3.6);fragment(d,825+165*p,360+295*p,t,1.15);d.line((1215,710,1430,810,1620,810),fill=COPPER,width=2);text(d,(1430,824),'MINERAL SURFACE',22,COPPER)
  else:
   p=ease((t-1.2)/4);fragment(d,985,652-130*p,t,1.18);d.line((1178,720,1178,660-130*p),fill=COPPER,width=3);text(d,(1320,400),'RETENTION',25,MUTED);text(d,(1320,443),'RELEASE',25,COPPER)
 else:
  d.polygon([(750,790),(1630,720),(1750,870),(830,930)],fill='#566964');d.polygon([(750,790),(830,930),(830,975),(750,840)],fill='#283e40');fragment(d,1000,775,t,1.1)
  for j in range(6):
   x=850+j*155;y=400+(t*28+j*50)%220;sphere(d,x,y,8,2);d.line((x,y+20,x,y+48),fill='#40595b',width=2)
  d.arc((910,595,1530,875),180,360,fill=COPPER,width=3);text(d,(1120,554),'A PROTECTIVE CONTEXT',24,COPPER)

def lab(im,t):
 d=ImageDraw.Draw(im);d.polygon([(740,775),(1690,775),(1810,910),(675,910)],fill='#293e45');d.line((740,775,1690,775),fill='#7a9293',width=2)
 for j in range(3):
  x=840+j*180;d.rounded_rectangle((x,540,x+95,824),radius=32,fill='#1d3940',outline='#789499',width=3);d.rounded_rectangle((x+6,670+j*25,x+89,816),radius=27,fill=['#397a7d','#587c72','#698076'][j]);d.line((x+15,576,x+15,730),fill='#a0b6b0',width=3);d.rounded_rectangle((x-7,525,x+102,556),radius=9,fill='#6b8888') if j else d.ellipse((x-5,534,x+100,553),fill='#0b252b',outline='#89a4a3',width=3)
 p=ease(t/1.5);xx=880;yy=300+90*p;d.rounded_rectangle((xx-18,yy-80,xx+18,yy+75),radius=10,fill='#aab8b2');d.polygon([(xx-14,yy+75),(xx+14,yy+75),(xx+3,yy+145),(xx-3,yy+145)],fill='#748e8e')
 if 1.5<t<2.3:
  y=yy+145+ease((t-1.5)/.8)*120;d.ellipse((xx-5,y-10,xx+5,y+10),fill=TEAL)
 for k in range(6):
  if t>2.4+k*.55:
   x=1480+(k%2)*130;y=430+(k//2)*95;d.rounded_rectangle((x,y,x+95,y+33),radius=5,fill='#365d64');text(d,(x+9,y+4),['A C','T G','G A','C T','A T','G C'][k],19,IVORY)
 text(d,(1430,780),'SHORT FRAGMENTS',23,COPPER)

def strips(d,x,y,letters,highlight=0,missing=False):
 if missing:d.rounded_rectangle((x,y,x+590,y+75),radius=9,outline='#617274',width=2);text(d,(x+20,y+22),'REFERENCE NOT AVAILABLE',24,MUTED);return
 for i,l in enumerate(letters):
  fill=('#346f74' if i<highlight else '#263c44');d.rounded_rectangle((x+i*72,y,x+i*72+61,y+75),radius=8,fill=fill,outline='#4b666b',width=1);text(d,(x+i*72+18,y+15),l,33,IVORY)
def comparison(im,t,mode):
 d=ImageDraw.Draw(im)
 if mode=='identity':
  fragment(d,920,500,t,1.55);d.line((1060,640,1580,640),fill='#5e777a',width=2);text(d,(1060,668),'IDENTITY: UNASSIGNED',27,COPPER)
 elif mode=='align':
  n=int(ease(t/3.5)*8);text(d,(900,285),'SURVIVING PIECE',24,COPPER);strips(d,900,340,'ACTGATCG',n);text(d,(900,555),'REFERENCE',24,MUTED);strips(d,900,610,'ACTGATCG',n)
  for i in range(n):d.line((930+i*72,430,930+i*72,593),fill='#548a8b',width=2)
 elif mode=='ambiguity':
  strips(d,990,285,'ACTGATCG',8)
  for yy,label,s in [(545,'RELATED REFERENCE A','ACTGATCG'),(745,'RELATED REFERENCE B','ACTGATCG')]:
   e=ease((t-.5)/2);d.line((1260,380,1580,440,1580,yy+37,1485,yy+37),fill=COPPER,width=3);text(d,(900,yy-48),label,22,MUTED);strips(d,900,yy,s,int(8*e))
 else:
  text(d,(895,280),'REFERENCE CATALOGUE',25,COPPER);strips(d,895,355,'ACTGATCG',4);strips(d,895,485,'',missing=True)
  d.line((1200,590,1200,700,1580,700),fill=COPPER,width=3);text(d,(900,755),'SUPPORTED FAMILY BRANCH',30,IVORY);text(d,(900,805),'NOT NECESSARILY ONE EXACT SPECIES',22,MUTED)

TITLES={18:('Cold buys time.','Loss can slow. Preservation is not permanent.','cold'),19:('The mineral connection.','Some DNA can bind to sediment surfaces.','binding'),20:('More than a covering.','Parts of the sediment may help traces last.','protection'),21:('Protection has a catch.','What holds a fragment can make release difficult.','release'),22:('Recover. Then read.','Not an intact instruction book. Fragments from many lives.','lab'),23:('A fragment. No name.','The next question is identity.','identity'),24:('Find the correspondence.','Compare surviving sequences with references.','align'),25:('A match can be shared.','Related animals may share similar stretches.','ambiguity'),26:('A gap in the catalogue.','Supported lineage does not always mean exact species.','missing')}
def graphic(global_frame):
 r=next(r for r in beats if r['start_frame']<=global_frame<r['end_frame']);num=int(r['id'][-2:]);t=(global_frame-r['start_frame'])/30;title,sub,mode=TITLES[num];im=MATERIAL.copy() if mode in ['cold','binding','release'] else BG.copy()
 if mode in ['cold','binding','protection','release']:mineral(im,t,mode)
 elif mode=='lab':lab(im,t)
 else:comparison(im,t,mode)
 d=ImageDraw.Draw(im);reveal=ease(t/.55);yy=295+int(20*(1-reveal));wrap(d,(86,yy),title,64,680,IVORY,True);wrap(d,(90,515),sub,30,575,MUTED)
 d.line((90,650,370+int(180*min(t/4,1)),650),fill=COPPER,width=2)
 qualifier='CONCEPTUAL MATERIAL PROCESS · NOT TO SCALE' if num<22 else 'ILLUSTRATIVE EXTRACTION · NOT STUDY FOOTAGE' if num==22 else 'SCHEMATIC COMPARISON · NOT ACTUAL SEQUENCE READS'
 header(im,'DEVELOPMENT PROOF / '+r['id'],qualifier);text(d,(90,920),'EXISTING ENGLISH VOICE · NO SPEED CHANGE',19,MUTED)
 return im

def styles():
 for name,caption,qual in [('01-living-world.png','A trace of a giant.','AI-GENERATED CONCEPT · ILLUSTRATIVE RECONSTRUCTION · NOT AN APPROVED ANIMAL RIG'),('05-community.png','Beyond one animal.','AI-GENERATED CONCEPT · NOT A RECOVERED ENCOUNTER'),('06-record.png','An incomplete record.','AI-GENERATED ILLUSTRATIVE RECORD MOTIF · NOT A CLAIMED SITE SPECIMEN')]:
  im=ImageOps.fit(Image.open(STYLE/name).convert('RGB'),(W,H));overlay=Image.new('RGBA',(W,H));a=np.zeros((H,W,4),dtype=np.uint8);a[:,:,:3]=[4,15,20];a[:,:,3]=(np.linspace(125,0,W)[None,:]).astype(np.uint8);im=Image.alpha_composite(im.convert('RGBA'),Image.fromarray(a)).convert('RGB');d=ImageDraw.Draw(im);text(d,(88,177),caption,64,IVORY,True);header(im,'STYLE DEVELOPMENT',qual);im.save(STYLE/name.replace('.png','-designed.jpg'),quality=94)
 # Accurate geographical outline, not a fantasy Greenland shape.
 im=BG.copy();d=ImageDraw.Draw(im);geo=json.loads((B/'geography.json').read_text());project=lambda p:(1270+(p[0]+42)*14,780-(p[1]-60)*23)
 for f in geo['features']:
  geometry=f['geometry'];polys=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
  for p in polys:
   points=[project(v) for v in p[0]];d.polygon(points,fill='#456765' if f['name']=='Greenland' else '#1c353e',outline='#78948e' if f['name']=='Greenland' else '#304f57',width=2)
 fade=np.tile((np.clip((970-np.arange(W))/300,0,1)*255).astype(np.uint8),(H,1));im=Image.composite(BG,im,Image.fromarray(fade));d=ImageDraw.Draw(im)
 x,y=project((-22.4,82.4));d.ellipse((x-8,y-8,x+8,y+8),fill=COPPER);d.line((x+12,y,x+130,y),fill=COPPER,width=2);text(d,(x-50,y-58),'FORMATION AREA',21,COPPER);text(d,(86,290),'The place.\nNot the world.',65,IVORY,True);wrap(d,(90,535),'Kap København Formation\nNorth Greenland',30,600);text(d,(90,690),'REPORTED IN NATURE · 2022',24,COPPER);header(im,'LOCATION / EVIDENCE','NATURAL EARTH OUTLINE · APPROXIMATE FORMATION-AREA LOCATOR');im.save(STYLE/'02-location.jpg',quality=94)
 graphic(next(r['start_frame'] for r in beats if r['id']=='V5-19')+100).save(STYLE/'03-mineral.jpg',quality=94)
 graphic(next(r['start_frame'] for r in beats if r['id']=='V5-25')+80).save(STYLE/'04-reference.jpg',quality=94)

def audio():
 # Preserve existing natural chapter timing, including its original end padding.
 chunks=[];chosen=[c for c in manifest['chapters'] if c['start_frame']<END and c['start_frame']+c['frames']>START]
 for c in chosen:
  target=OUT/(c['id']+'.wav');subprocess.run([FF,'-y','-v','error','-i',str(B.parent/'film-v3/voice'/f'{c["id"]}.flac'),'-af',f'apad,atrim=0:{c["frames"]/30}','-ar','48000','-ac','1',str(target)],check=True)
  with wave.open(str(target)) as f:a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(np.float32)/32768
  first=max(START,c['start_frame'])-c['start_frame'];end=min(END,c['start_frame']+c['frames'])-c['start_frame'];chunks.append(a[first*1600:end*1600])
 voice=np.concatenate(chunks);assert len(voice)==N*1600
 def wav(path,a):
  with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(48000);f.writeframes((np.clip(a,-.98,.98)*32767).astype('<i2').tobytes())
 wav(OUT/'voice.wav',voice)
 # Original temporary score / schematic contact sound sketches, NOT cleared final foley or approved music.
 count=len(voice);score=np.zeros(count,dtype=np.float32);rng=np.random.default_rng(73)
 for start,freq in [(0,146.83),(8,174.61),(16,130.81),(24,164.81),(32,146.83),(40,174.61),(48,130.81),(56,146.83)]:
  end=min(count,int((start+12)*48000));n=end-int(start*48000)
  if n<=0:continue
  t=np.arange(n)/48000;env=np.minimum(t/2,1)*np.minimum((n/48000-t)/4,1)
  tone=sum(np.sin(2*np.pi*freq*k*t+.17*k)/k**2 for k in [1,2,3,4]);score[int(start*48000):end]+=(tone*env*.018).astype(np.float32)
 for r in beats:
  if START<=r['start_frame']<END:
   at=int((r['start_frame']-START)/30*48000+.5*48000);n=min(10000,count-at)
   if n>0:
    t=np.arange(n)/48000;noise=rng.normal(0,1,n);noise=np.convolve(noise,np.ones(19)/19,mode='same');score[at:at+n]+=(noise*np.exp(-t*24)*.06).astype(np.float32)
 wav(OUT/'temp-score.wav',score)
 subprocess.run([FF,'-y','-v','error','-i',str(OUT/'voice.wav'),'-i',str(OUT/'temp-score.wav'),'-filter_complex','[0:a]asplit[v][sc];[1:a][sc]sidechaincompress=threshold=0.025:ratio=5:attack=35:release=350[m];[v][m]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-2.5:LRA=9,aformat=sample_rates=48000[mix]','-map','[mix]',str(OUT/'mix.wav')],check=True)

def render():
 enc=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','4',str(OUT/'picture.mp4')],stdin=subprocess.PIPE)
 try:
  prior=None
  for i in range(N):
   f=START+i;im=graphic(f);r=next(r for r in beats if r['start_frame']<=f<r['end_frame']);age=f-r['start_frame']
   if age<15 and r['start_frame']>START:
    old=graphic(r['start_frame']-1);im=Image.blend(old,im,ease(age/15))
   enc.stdin.write(im.tobytes())
   if i%150==0:print('frames',i,'/',N,flush=True)
  enc.stdin.close();code=enc.wait();assert code==0
 finally:
  if enc.poll() is None:enc.kill()
 subprocess.run([FF,'-y','-v','error','-i',str(OUT/'picture.mp4'),'-i',str(OUT/'mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-af','volume=0.5dB','-t',str(N/30),'-movflags','+faststart',str(OUT/'Extinct_Life_V5_Graphics_Motion_Development.mp4')],check=True)
 subprocess.run([FF,'-v','error','-i',str(OUT/'Extinct_Life_V5_Graphics_Motion_Development.mp4'),'-f','null','-'],check=True)
 p=subprocess.run([FF,'-hide_banner','-i',str(OUT/'Extinct_Life_V5_Graphics_Motion_Development.mp4'),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
 (OUT/'encoded-audio-measurement.txt').write_text(p.stderr[p.stderr.rfind('Summary:'):])
 report={'status':'DEVELOPMENT PROOF, NOT FINAL FILM','width':W,'height':H,'fps':FPS,'frames':N,'duration_seconds':N/30,'source_start_frame':START,'source_end_frame':END,'voice':'original approved voice-02, no speed change, continuous original excerpt','original_visual_tasks':[r['id'] for r in beats if START<=r['start_frame']<END],'motion':'new authored 2D/2.5D process and comparison animation; not native 3D animal animation','style_plates':'AI-generated concept images, NOT animated in this proof','sound':'original temporary score and schematic sound sketches; final licensed score/recorded foley not selected or approved','full_export_decode':'passed','human_listen_claimed':False,'anatomy_expert_approval':False,'full_film_rendered':False}
 (B/'PROOF-QC.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':
 styles();audio()
 if '--styles-only' not in sys.argv:render()
