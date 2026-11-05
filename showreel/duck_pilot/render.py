"""MONARCH ocean documentary motion proof; animated vector scenes, no still plates.

Install Pillow and imageio-ffmpeg, then:
  python showreel/duck_pilot/render.py --voice /path/to/narration.wav --output /path/to/proof.mp4
The 10-second proof is a creative/technical test, not a complete documentary.
"""
import argparse, math, os, random, subprocess, tempfile, wave
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

W,H,FPS,SECONDS=720,1280,30,10.5
YELLOW=(255,203,84); CREAM=(245,246,234); SEA=(6,22,37); BLUE=(31,95,112)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
def txt(d,xy,s,size,color=CREAM):
 d.text(xy,s,font=ImageFont.truetype(FONT,size),fill=color,stroke_width=0)
def duck(d,x,y,size,angle=0):
 # Independently animated object, not an image plate.
 s=size; d.ellipse((x-s*.7,y-s*.3,x+s*.7,y+s*.4),fill=(239,181,56));d.ellipse((x-s*.47,y-s*.83,x+s*.25,y-s*.07),fill=(255,210,94));d.ellipse((x-s*.12,y-s*.59,x-s*.04,y-s*.51),fill=(24,36,38));d.polygon([(x-s*.53,y-s*.5),(x-s*.8,y-s*.42),(x-s*.5,y-s*.3)],fill=(224,127,53))
def waves(d,t,base=760):
 for k in range(9):
  y=base+k*55; color=(13+k*2,47+k*3,62+k*4)
  points=[(x,y+math.sin(x*.012+t*(.8+k*.04)+k)*8) for x in range(-10,W+20,10)]
  d.line(points,fill=color,width=2 if k<5 else 3)
def header(d):
 txt(d,(48,58),'MONARCH  /  FIELD NOTES',17,(166,190,189));d.line((48,96,672,96),fill=(67,96,100),width=1)
def scene(t):
 im=Image.new('RGB',(W,H),SEA);d=ImageDraw.Draw(im)
 for y in range(H):
  z=y/H;d.line((0,y,W,y),fill=(int(6+5*z),int(20+17*z),int(32+19*z)))
 header(d)
 if t<3.4:
  # Cargo ship and timed container departure, intentionally stylized.
  waves(d,t,790)
  d.ellipse((405,180,970,745),fill=(10,34,46),outline=(31,65,72),width=3)
  shift=ease((t-1.35)/1.4); x=0
  d.polygon([(40,760),(690,760),(626,832),(155,835)],fill=(69,80,77),outline=(191,185,155),width=2)
  d.polygon([(45,760),(690,760),(635,790),(82,790)],fill=(30,43,45))
  for row in range(3):
   for col in range(7):
    xx=120+col*70;yy=580+row*55
    if row==0 and col==5: continue
    color=[(53,96,96),(122,105,73),(62,77,85)][(col+row)%3];d.rectangle((xx,yy,xx+65,yy+49),fill=color,outline=(156,158,135),width=1)
    for j in range(1,5):d.line((xx+j*13,yy+4,xx+j*13,yy+45),fill=(35,66,70),width=1)
  cx=470+120*shift;cy=580+165*shift;d.polygon([(cx,cy),(cx+65,cy+20*shift),(cx+65,cy+50+20*shift),(cx,cy+50)],fill=(222,147,67),outline=(244,202,128),width=2)
  txt(d,(48,230),'ONE CONTAINER.',44);txt(d,(48,292),'ONE OCEAN.',56,YELLOW)
  d.text((49,370),'NORTH PACIFIC  /  1992',font=ImageFont.truetype(REG,22),fill=(190,204,196))
 elif t<6.9:
  u=t-3.4; waves(d,t,350)
  # Autonomous floating toy shapes move at varied speeds along waves.
  for i in range(15):
   x=((i*119+u*(29+i%3*9))%940)-110;y=460+(i*103)%490+math.sin(u*1.5+i)*15
   duck(d,x,y,14+(i%4)*5)
  duck(d,368+math.sin(u)*18,755+math.sin(u*1.8)*15,90)
  txt(d,(48,215),'~29,000',84,YELLOW);txt(d,(52,323),'FLOATING TOYS',34)
  d.text((52,379),'BATH TOYS, INCLUDING DUCKS',font=ImageFont.truetype(REG,19),fill=(182,205,200))
 else:
  u=t-6.9
  # Motion is illustrative, not a real route/geographic map.
  d.ellipse((50,260,670,880),fill=(8,39,53),outline=(50,103,112),width=3)
  for j in range(8):
   pts=[]
   for k in range(100):
    a=k/99*math.pi*1.85; r=42+j*32+7*math.sin(a*3+j);px=360+math.cos(a+u*.09)*r;py=570+math.sin(a+u*.09)*r*.72;pts.append((px,py))
   d.line(pts,fill=(28+j*3,96+j*4,107+j*4),width=2)
   p=(u*.11+j*.13)%1; k=int(p*99); px,py=pts[k];d.ellipse((px-5,py-5,px+5,py+5),fill=YELLOW)
  duck(d,360+75*math.sin(u*.7),570+30*math.cos(u*.7),31)
  txt(d,(48,180),'INVISIBLE',48);txt(d,(48,240),'CURRENTS',56,YELLOW)
  d.text((49,923),'ILLUSTRATIVE MOTION  •  NOT A ROUTE MAP',font=ImageFont.truetype(REG,18),fill=(186,201,197))
 # unobtrusive progress indicator, frame-accurate
 d.rounded_rectangle((48,1125,672,1129),radius=2,fill=(52,75,77));d.rounded_rectangle((48,1125,48+624*t/SECONDS,1129),radius=2,fill=YELLOW)
 return im

def main():
 p=argparse.ArgumentParser();p.add_argument('--voice',required=True);p.add_argument('--output',required=True);args=p.parse_args()
 os.makedirs(os.path.dirname(os.path.abspath(args.output)),exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  vid=os.path.join(temp,'picture.mp4');audio=os.path.join(temp,'music.wav');ff=imageio_ffmpeg.get_ffmpeg_exe()
  enc=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p',vid],stdin=subprocess.PIPE)
  for i in range(int(FPS*SECONDS)):enc.stdin.write(scene(i/FPS).tobytes())
  enc.stdin.close()
  if enc.wait():raise RuntimeError('video encode failed')
  # Original synth, restrained and mixed well below voice; timed low thuds at picture changes.
  import array
  sr=24000; samples=array.array('h')
  for n in range(int(sr*SECONDS)):
   t=n/sr;fade=min(1,t/.18,(SECONDS-t)/.5);base=(math.sin(2*math.pi*73.42*t)+.4*math.sin(2*math.pi*110*t))*0.045
   cue=0
   for at in [0,3.4,6.9]:
    dt=t-at
    if 0<=dt<.7:cue+=.06*math.sin(2*math.pi*(72-18*dt)*dt)*math.exp(-dt*7)
   samples.append(int(max(-.9,min(.9,(base+cue)*max(0,fade)))*32767))
  with wave.open(audio,'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(samples.tobytes())
  mix='[1:a]volume=1.0[voice];[2:a]volume=0.4[bed];[voice][bed]amix=inputs=2:duration=longest:normalize=0,highpass=f=35,alimiter=limit=0.85:level=false[a]'
  subprocess.run([ff,'-y','-loglevel','error','-i',vid,'-i',args.voice,'-i',audio,'-filter_complex',mix,'-map','0:v','-map','[a]','-t',str(SECONDS),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',args.output],check=True)
if __name__=='__main__':main()
