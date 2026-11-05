"""Full 43.6s animated explainer. Narration WAVs are supplied separately.

Requires Pillow and imageio-ffmpeg. Run:
 python showreel/duck_pilot/render_film.py --voice-dir /path/to/voice --output /path/to/film.mp4
The four inputs must be named vo1.wav ... vo4.wav. All visual and music assets
are generated here; no external footage, maps, or sound samples are used.
"""
import argparse, array, math, os, subprocess, tempfile, wave
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from render import W,H,FPS,FONT,REG,YELLOW,CREAM,SEA,duck,ease,waves,txt

DUR=43.6
SCENES=[(0,3.0,'ONE ACCIDENT','NORTH PACIFIC  /  1992'),(3,6.3,'THOUSANDS OF TOYS','ONE CONTAINER  /  OPEN OCEAN'),(6.3,9.9,'AN INVISIBLE SYSTEM','THE OCEAN IS ALWAYS MOVING'),(9.9,13.1,'A CONTAINER FALLS','STYLIZED RECONSTRUCTION'),(13.1,17.2,'~29,000 TOYS','DUCKS AND OTHER BATH TOYS'),(17.2,22.55,'ALASKA','SOME TOYS WASHED ASHORE'),(22.55,26.25,'RECOVERY CLUES','SIGHTINGS + OCEAN MODELS'),(26.25,29.3,'FOLLOW THE FLOW','ILLUSTRATIVE  /  NOT A ROUTE MAP'),(29.3,33.05,'NOT THE WHOLE OCEAN','REAL CLUES, NOT A COMPLETE MAP'),(33.05,36.3,'ONE TINY TOY','A VAST OCEAN'),(36.3,39.4,'HIDDEN CONNECTIONS','THE INVISIBLE THREAD'),(39.4,43.6,'SEE THE WORLD','DIFFERENTLY')]

def label(d,t,title,sub,start):
 # Animated type entrance; leave central area for the action.
 x=48-int(30*(1-ease((t-start)*3)))
 d.text((x,138),title,font=ImageFont.truetype(FONT,44),fill=CREAM)
 d.text((x,203),sub,font=ImageFont.truetype(REG,19),fill=(183,208,204))
 d.rounded_rectangle((48,1126,672,1130),radius=2,fill=(44,72,76))
 d.rounded_rectangle((48,1126,48+624*t/DUR,1130),radius=2,fill=YELLOW)

def ship(d,t,fall=False):
 y=690+math.sin(t*1.3)*5
 # Deep silhouette, wake, stacked dimensional containers and wheelhouse.
 for j in range(4):
  d.arc((-120+j*70,y+45+j*13,700+j*50,y+145+j*13),0,155,fill=(38,94+j*6,106+j*5),width=2)
 d.polygon([(25,y),(680,y),(620,y+90),(148,y+90)],fill=(64,78,78),outline=(142,156,146),width=3)
 d.polygon([(25,y),(680,y),(644,y+26),(57,y+26)],fill=(22,39,42))
 d.rectangle((85,y-110,156,y),fill=(79,97,91),outline=(165,173,156),width=2)
 d.rectangle((98,y-95,125,y-79),fill=(227,198,132));d.line((123,y-110,123,y-165),fill=(143,157,144),width=4)
 for row in range(3):
  for col in range(6):
   if fall and row==0 and col==4:continue
   x=164+col*72;cy=y-169+row*55;c=[(51,94,94),(134,108,72),(66,82,87)][(col+row)%3]
   d.rectangle((x,cy,x+68,cy+50),fill=c,outline=(142,151,132),width=1)
   for j in range(1,5):d.line((x+j*13,cy+3,x+j*13,cy+47),fill=(36,67,68))
 if fall:
  q=ease((t-9.9)/2.6);x=452+190*q;cy=y-169+255*q
  d.polygon([(x,cy),(x+68,cy+30*q),(x+68,cy+50+30*q),(x,cy+50)],fill=(220,145,68),outline=(243,204,133),width=2)

def toys(d,t,count=22,big=True):
 waves(d,t,380)
 for i in range(count):
  x=((i*173+t*(18+i%4*7))%920)-100;y=360+(i*137)%600+math.sin(t*1.4+i)*12
  duck(d,x,y,11+i%4*6)
 if big:duck(d,360+math.sin(t*.65)*38,725+math.sin(t*1.7)*15,80)

def current(d,t):
 # Diagrams are conceptual, not evidence of precise tracks.
 d.ellipse((37,310,683,956),fill=(8,38,52),outline=(47,94,100),width=3)
 for j in range(9):
  pts=[]
  for k in range(100):
   a=k/99*math.pi*1.84;r=40+j*31+7*math.sin(a*3+j)
   pts.append((360+math.cos(a+t*.1)*r,633+math.sin(a+t*.1)*r*.79))
  d.line(pts,fill=(25+j*4,89+j*5,100+j*5),width=2)
  q=(t*.10+j*.14)%1;x,y=pts[int(q*99)];d.ellipse((x-4,y-4,x+4,y+4),fill=YELLOW)
 duck(d,360+math.sin(t*.5)*60,633+math.cos(t*.8)*35,27)

def shore(d,t):
 waves(d,t,580)
 # Abstract shoreline with depth layers, not a geographic map.
 d.polygon([(0,310),(70,402),(135,355),(216,510),(287,415),(375,560),(461,460),(540,560),(720,425),(720,650),(0,650)],fill=(23,56,61))
 d.polygon([(0,572),(89,545),(181,600),(282,570),(370,621),(469,572),(565,617),(720,550),(720,790),(0,790)],fill=(52,77,73))
 d.polygon([(0,755),(130,728),(231,763),(344,739),(446,780),(559,748),(720,779),(720,995),(0,995)],fill=(126,131,109))
 for j in range(6):
  x=(j*137+int(t*13))%760; d.line((x,805+j*20,x+46,798+j*20),fill=(158,164,136),width=2)
 duck(d,390+math.sin(t)*5,760+math.sin(t*1.3)*5,62)

def evidence(d,t):
 # Research chart; animated plotted signals do not represent measurements.
 d.rounded_rectangle((44,325,676,910),radius=12,fill=(12,40,49),outline=(69,112,115),width=2)
 for x in range(82,650,55):d.line((x,390,x,850),fill=(24,63,69))
 for y in range(390,851,55):d.line((80,y,650,y),fill=(24,63,69))
 for j in range(3):
  pts=[]
  for x in range(82,650,4):
   y=610+110*math.sin(x*.008+j*.9+t*.13)+j*45;pts.append((x,y))
  d.line(pts,fill=[(62,135,140),(69,103,107),(210,162,74)][j],width=3)
 for j in range(7):
  x=115+j*74;y=610+110*math.sin(x*.008+t*.13)
  if (t*2+j)%7>1:d.ellipse((x-6,y-6,x+6,y+6),fill=YELLOW)
 d.text((70,870),'CONCEPTUAL DATA VISUALIZATION',font=ImageFont.truetype(REG,16),fill=(148,182,179))

def frame(t):
 scene=next((s for s in SCENES if s[0]<=t<s[1]),SCENES[-1]);start,end,title,sub=scene
 im=Image.new('RGB',(W,H),SEA);d=ImageDraw.Draw(im)
 for y in range(H):
  z=y/H;d.line((0,y,W,y),fill=(int(5+6*z),int(19+17*z),int(30+21*z)))
 # Slow-moving atmospheric particle field, deterministic, original.
 for i in range(45):
  x=(i*113+int(t*(4+i%5)))%W;y=(i*193+int(t*(3+i%3)))%H
  d.ellipse((x,y,x+1,y+1),fill=(32,71,75))
 if t<3:ship(d,t)
 elif t<6.3:toys(d,t,17)
 elif t<9.9:current(d,t)
 elif t<13.1:ship(d,t,True)
 elif t<17.2:toys(d,t)
 elif t<22.55:shore(d,t)
 elif t<26.25:evidence(d,t)
 elif t<29.3:current(d,t)
 elif t<33.05:evidence(d,t)
 elif t<36.3:toys(d,t,9)
 elif t<39.4:current(d,t)
 else:
  current(d,t); d.text((49,1000),'MONARCHS EDIT',font=ImageFont.truetype(FONT,26),fill=YELLOW)
 d.text((48,57),'MONARCHS EDIT  /  THE INVISIBLE THREAD',font=ImageFont.truetype(FONT,17),fill=(167,192,188))
 d.line((48,95,672,95),fill=(55,92,95))
 label(d,t,title,sub,start)
 # Fast in-scene dark-to-clear seam; no empty flash frames.
 q=min(1,(t-start)/.16)
 if q<1:im=Image.blend(Image.new('RGB',(W,H),(4,17,26)),im,ease(q)*.8+.2)
 return im

def make_music(path):
 sr=24000; samples=array.array('h')
 for n in range(int(sr*DUR)):
  t=n/sr; fade=max(0,min(1,t/.4,(DUR-t)/1.2));pulse=.7+.3*math.sin(2*math.pi*.08*t)
  pad=(math.sin(2*math.pi*73.42*t)+.45*math.sin(2*math.pi*110*t)+.2*math.sin(2*math.pi*146.8*t))*.04*pulse
  thud=0
  for at,_,_,_ in SCENES:
   dt=t-at
   if 0<=dt<.65:thud+=.07*math.sin(2*math.pi*(68-15*dt)*dt)*math.exp(-dt*7)
  samples.append(int(max(-.9,min(.9,(pad+thud)*fade))*32767))
 with wave.open(path,'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(samples.tobytes())

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--voice-dir',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 for i in range(1,5):
  if not os.path.isfile(os.path.join(a.voice_dir,f'vo{i}.wav')):ap.error(f'missing vo{i}.wav in voice directory')
 os.makedirs(os.path.dirname(os.path.abspath(a.output)),exist_ok=True);ff=imageio_ffmpeg.get_ffmpeg_exe()
 with tempfile.TemporaryDirectory() as temp:
  vid=os.path.join(temp,'picture.mp4');music=os.path.join(temp,'music.wav')
  enc=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',vid],stdin=subprocess.PIPE)
  for i in range(round(FPS*DUR)):enc.stdin.write(frame(i/FPS).tobytes())
  enc.stdin.close()
  if enc.wait():raise RuntimeError('video encoder failed')
  make_music(music); cmd=[ff,'-y','-loglevel','error','-i',vid]
  for i in range(1,5):cmd+=['-i',os.path.join(a.voice_dir,f'vo{i}.wav')]
  cmd+=['-i',music]
  flt='[1:a]adelay=0|0[a1];[2:a]adelay=9900|9900[a2];[3:a]adelay=22550|22550[a3];[4:a]adelay=33050|33050[a4];[5:a]volume=0.38[bed];[a1][a2][a3][a4][bed]amix=inputs=5:duration=longest:normalize=0,highpass=f=35,alimiter=limit=0.85:level=false[a]'
  subprocess.run(cmd+['-filter_complex',flt,'-map','0:v','-map','[a]','-t',str(DUR),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',a.output],check=True)
if __name__=='__main__':main()
