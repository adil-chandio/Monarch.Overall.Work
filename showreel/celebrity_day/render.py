"""Original celebrity-day POV, with reference-inspired illustrated compositions.
Every frame is generated; no reference images, footage, or sound are used.
"""
from pathlib import Path
import importlib.util, math, json, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('farm',P.parent/'farm_reference'/'render.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
W,H,FPS,DUR=960,540,30,60
v=f.v; rect=f.rectangle; ell=f.ellipse; poly=f.poly; line=f.line; text=f.text; rnd=f.rounded; ease=f.ease; lerp=f.lerp; clamp=f.clamp
INK=(17,17,23,255); WHITE=(237,228,213,255); SKIN=(191,145,116,255)

def room(im, t, night=False):
 f.grad(im,(48,42,62) if night else (107,82,104),(59,52,66) if night else (196,146,123));d=ImageDraw.Draw(im)
 # Walls, panel seams and softly illuminated window with layered city depth.
 rect(d,(0,20,200,340),(65,55,66,255));rect(d,(468,20,640,340),(64,53,64,255));rect(d,(0,282,640,340),(55,45,52,255))
 for x in (30,105,175,491,566,624):line(d,[(x,20),(x,281)],(91,71,78,255),1)
 rect(d,(194,37,469,280),(33,32,43,255));rect(d,(201,44,462,272),(119,97,110,255) if not night else (55,58,77,255))
 # Window gradient and silhouettes.
 for y in range(45,272,3):
  u=(y-45)/227;c=tuple(int(lerp(a,b,u)) for a,b in zip((93,78,104) if not night else (37,40,63),(224,158,122) if not night else (80,73,98)))+(255,)
  rect(d,(202,y,461,y+3),c)
 ell(d,(358,128,414,184),(248,203,158,255) if not night else (171,169,160,255))
 for j in range(17):
  x=205+j*16;h=20+(j*29%75);rect(d,(x,270-h,x+15,270),(46,44,55,255))
  for yy in range(270-h+8,266,14):
   for xx in (x+3,x+10):
    if (xx+yy+j)%4:rect(d,(xx,yy,xx+2,yy+3),(154,136,122,255))
 for x in (200,330,461):line(d,[(x,42),(x,274)],(40,36,43,255),4)
 line(d,[(201,273),(462,273)],(43,37,43,255),5)
 # Inset cabinet and warm bedside lamp.
 rect(d,(470,240,640,340),(50,41,45,255));line(d,[(475,251),(640,251)],(118,87,77,255),2)
 line(d,[(555,243),(555,200)],(30,27,31,255),4);poly(d,[(538,200),(572,200),(565,176),(545,176)],(218,178,142,255))

def hand(im,x,y,angle=0,scale=1):
 # Forearm, palm and fingers are constructed in local coordinates and rotate as a unit.
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
 poly(d,[(x-17*scale,y+80*scale),(x-13*scale,y+24*scale),(x-16*scale,y+3*scale),(x-9*scale,y-12*scale),(x+1*scale,y-14*scale),(x+12*scale,y-6*scale),(x+15*scale,y+18*scale),(x+21*scale,y+80*scale)],SKIN,INK,1)
 for j in range(3):line(d,[(x+(-7+j*5)*scale,y-7*scale),(x+(-7+j*5)*scale,y+5*scale)],(141,103,88,255),.7)
 rect(d,(x-20*scale,y+54*scale,x+21*scale,y+85*scale),(47,55,67,255));line(d,[(x-18*scale,y+53*scale),(x+19*scale,y+53*scale)],(194,181,165,255),2)
 im.alpha_composite(layer.rotate(angle,resample=Image.Resampling.BICUBIC,center=(v(x),v(y+65*scale))))

def phone(im,t):
 d=ImageDraw.Draw(im);rounded=(39,39,47,255)
 rnd(d,(243,74,396,306),13,INK,(190,162,145,255),2);rnd(d,(251,83,388,297),8,(73,76,89,255))
 text(d,(319,105),'6:14',19,WHITE);text(d,(319,124),'MONDAY',7,(204,195,190,255))
 for j,(title,sub) in enumerate((('TEAM','Car arrives at 8:15'),('SCHEDULE','Training  /  interview'),('MESSAGES','12 new requests'))):
  yy=144+j*43;u=ease((t-(j*.45))/.45)
  rnd(d,(259,yy+10*(1-u),380,yy+34+10*(1-u)),4,(112,107,113,255));text(d,(267,yy+8+10*(1-u)),title,7,WHITE,'lm');text(d,(267,yy+21+10*(1-u)),sub,6,(226,216,210,255),'lm')
 hand(im,400,270,-12,.8)

def gym(im,t):
 f.grad(im,(50,54,66),(102,91,88));d=ImageDraw.Draw(im);rect(d,(0,260,640,340),(49,48,52,255))
 for x in (25,170,315,460,605):line(d,[(x,20),(x,258)],(31,34,39,255),3)
 for y in (90,165,260):line(d,[(0,y),(640,y)],(68,68,73,255),2)
 rect(d,(45,53,250,224),(52,66,75,255),(140,132,128,255),2)
 for j in range(6):rect(d,(58+j*30,190-(j*17%75),79+j*30,220),(42,51,58,255))
 # Trainer counts in foreground; a real articulated person, not protagonist.
 f.person(im,440+1.5*math.sin(t*1.6),270,1.35,t,'villager','idle');text(d,(495,100),'READY?',10,WHITE)
 # POV gloved hands lift and lower dumbbells with staggered oscillation.
 q=(1-math.cos((t-12)*math.pi*1.2))/2
 for side in (-1,1):
  x=320+side*125;y=305-68*q
  hand(im,x,y,side*12,.95);d=ImageDraw.Draw(im);line(d,[(x-30,y-20),(x+30,y-20)],(157,160,160,255),5)
  for xx in (x-32,x+25):rnd(d,(xx,y-35,xx+8,y-5),2,(28,29,32,255),(111,110,111,255),1)

def city(im,t):
 f.grad(im,(94,78,105),(217,159,128));d=ImageDraw.Draw(im)
 # Moving near and distant buildings create camera parallax, with wrapped coordinates.
 for layer,(vel,base,col) in enumerate(((8,185,(69,61,75,255)),(23,222,(47,46,57,255)))):
  for j in range(-2,12):
   x=(j*100-(t*vel)%100);h=46+(j*37%84);rect(d,(x,base-h,x+90,base+35),col)
   for yy in range(int(base-h+10),base+20,17):
    for xx in range(int(x+9),int(x+85),18):rect(d,(xx,yy,xx+3,yy+5),(159,141,139,255))
 rect(d,(0,254,640,340),(58,56,61,255))
 for j in range(7):
  x=(j*140-t*65)%850-100;poly(d,[(x,294),(x+70,294),(x+60,301),(x-12,301)],(180,164,151,255))

def car(im,t):
 city(im,t);d=ImageDraw.Draw(im)
 # Window frame and armrest keep the POV inside a moving vehicle.
 poly(d,[(0,20),(44,20),(67,260),(0,273)],(23,23,30,255));poly(d,[(600,20),(640,20),(640,278),(583,260)],(23,23,30,255));poly(d,[(0,270),(640,270),(640,340),(0,340)],(32,30,37,255))
 line(d,[(44,25),(598,25)],(25,24,29,255),12);line(d,[(68,259),(584,259)],(128,110,110,255),3)
 rnd(d,(236,290,404,310),5,(72,67,69,255));hand(im,350,310,12,.65)
 # Fans approach as the car slows, flashes remain brief and irregular.
 if t>27:
  for j in range(5):
   x=130+j*95+(t-27)*10;f.person(im,x,252,.55,t+j,'villager','idle')
   d=ImageDraw.Draw(im);rect(d,(x+4,214,x+12,225),(26,25,27,255),(211,202,191,255),.6)
  if int(t*8)%19 in (0,1):rect(d,(0,20,640,270),(248,240,223,50))

def studio(im,t):
 f.grad(im,(40,42,57),(89,72,80));d=ImageDraw.Draw(im);rect(d,(0,275,640,340),(45,42,49,255))
 for x in (75,565):
  line(d,[(x,95),(x,282)],(24,24,29,255),3);poly(d,[(x-33,48),(x+33,48),(x+24,104),(x-24,104)],(221,197,170,255));line(d,[(x-35,282),(x,250),(x+35,282)],(27,26,30,255),3)
 # Interviewer responds subtly; oversized lens in foreground emphasizes POV.
 f.person(im,410+2*math.sin(t*1.2),275,1.55,t,'villager','idle');d=ImageDraw.Draw(im)
 rnd(d,(105,132,232,235),9,(31,31,37,255));ell(d,(185,143,264,225),(16,17,21,255),(131,132,136,255),3);ell(d,(203,160,248,208),(53,64,75,255),(104,108,115,255),2);ell(d,(213,169,226,181),(140,157,158,255))
 text(d,(325,69),'ON AIR',9,(237,205,186,255));ell(d,(282,65,289,72),(218,62,64,255))

def autograph(im,t):
 f.grad(im,(82,70,81),(148,116,101));d=ImageDraw.Draw(im);rect(d,(0,265,640,340),(64,59,61,255));f.person(im,321+1.5*math.sin(t*1.7),245,1.5,t,'villager','idle')
 # barrier and card; the POV hand moves its pen tip along a scripted signature path.
 d=ImageDraw.Draw(im);line(d,[(0,258),(640,258)],(37,34,39,255),8);line(d,[(0,284),(640,284)],(37,34,39,255),6)
 for x in range(20,640,80):line(d,[(x,257),(x,339)],(37,34,39,255),5)
 poly(d,[(230,260),(390,260),(412,337),(210,337)],(223,215,200,255),INK,1)
 # Trace the signature progressively: time maps to pen position.
 points=[(250+i*2,305-9*math.sin(i*.25)-3*math.sin(i*.67)) for i in range(43)]
 n=max(1,min(len(points),int((t-40)*15)))
 if n>1:line(d,points[:n],(44,42,45,255),1.4)
 px,py=points[n-1];line(d,[(px,py),(px+28,py+24)],(35,35,39,255),3);hand(im,px+35,py+38,-28,.72)

def premiere(im,t):
 f.grad(im,(44,37,51),(107,72,76));d=ImageDraw.Draw(im);rect(d,(0,20,640,235),(38,35,45,255))
 for x in range(0,640,80):line(d,[(x,20),(x,235)],(75,57,67,255),2)
 poly(d,[(230,215),(410,215),(595,340),(45,340)],(123,37,49,255));line(d,[(230,215),(45,340)],(206,159,136,255),2);line(d,[(410,215),(595,340)],(206,159,136,255),2)
 for side in (-1,1):
  for j in range(5):
   x=320+side*(175+j*28);y=215+j*13;f.person(im,x,y,.42+j*.045,t+j,'villager','idle')
   d=ImageDraw.Draw(im);rect(d,(x-4,y-30,x+5,y-22),(26,26,30,255),(196,189,181,255),.6)
 for j in range(5):
  if int(t*9+j*7)%37==0:
   x=80+j*116;ell(d,(x-25,100,x+25,150),(250,244,221,115))
 hand(im,490,235,-38+12*math.sin(t*3),.9)

def compose(t):
 im=Image.new('RGBA',(W,H))
 if t<6.5:
  room(im,t);d=ImageDraw.Draw(im)
  # Sheets part as the viewer wakes; foreground hands rise into frame.
  poly(d,[(0,274),(190,251),(320,280),(470,249),(640,272),(640,340),(0,340)],(91,87,97,255))
  if t>2.0:
   u=ease((t-2)/2);hand(im,194,320-45*u,-12,1);hand(im,448,320-42*u,12,1)
 elif t<12.5:room(im,t);im=im.filter(ImageFilter.GaussianBlur(v(2)));phone(im,t-6.5)
 elif t<19:gym(im,t)
 elif t<25.5:
  room(im,t);d=ImageDraw.Draw(im);rnd(d,(201,222,314,306),6,(61,57,60,255));ell(d,(221,236,278,250),(190,164,144,255));rnd(d,(240,251,273,296),4,(226,216,197,255));ell(d,(244,248,269,255),(86,62,49,255));hand(im,320-22*ease((t-19)/2),304-25*ease((t-19)/2),-20,.8)
 elif t<32.3:car(im,t)
 elif t<39.5:studio(im,t)
 elif t<47.1:autograph(im,t)
 elif t<53.4:premiere(im,t)
 else:
  room(im,t,True);d=ImageDraw.Draw(im);poly(d,[(0,290),(640,290),(640,340),(0,340)],(31,31,38,255));rnd(d,(281,283,360,325),5,(25,25,30,255));text(d,(320,301),'NO NEW ALERTS',6,(136,140,145,255))
 # A restrained animated push-in and drift, reset at each edit.
 cuts=(0,6.5,12.5,19,25.5,32.3,39.5,47.1,53.4)
 start=max(c for c in cuts if c<=t);u=clamp((t-start)/6)
 zoom=1.015+.025*u;cw=int(W/zoom);ch=int(H/zoom)
 left=int((W-cw)/2+3*math.sin(t*.7));top=int((H-ch)/2+2*math.sin(t*.5))
 left=max(0,min(W-cw,left));top=max(0,min(H-ch,top))
 im=im.crop((left,top,left+cw,top+ch)).resize((W,H),Image.Resampling.BICUBIC)
 # Grain-like ambient motes give depth and movement without source footage.
 d=ImageDraw.Draw(im)
 for j in range(16):
  xx=(j*113+math.sin(t*.35+j)*4)%640;yy=30+(j*37+t*(.4+j%3))%300
  ell(d,(xx-.5,yy-.5,xx+.5,yy+.5),(225,201,182,65))
 out=f.vignette(im);d=ImageDraw.Draw(out,'RGBA');rect(d,(0,0,640,20),(0,0,0,255));rect(d,(0,340,640,360),(0,0,0,255))
 text(d,(25,33),'POV',7,(221,208,194,230),'lm');text(d,(52,33),'FAMOUS',9,(231,198,145,255),'lm')
 if t<6.5:text(d,(25,304),'6:14 AM',10,WHITE,'lm')
 if t>53.4:text(d,(25,304),'11:42 PM',10,WHITE,'lm')
 if t<.5:out=Image.blend(Image.new('RGB',(W,H)),out,ease(t/.5))
 if t>59.5:out=Image.blend(out,Image.new('RGB',(W,H)),ease((t-59.5)/.5))
 return out

def score(path):
 # Original understated synth bed, a light pulse, and short designed transitions.
 sr=48000;t=np.arange(sr*DUR,dtype=np.float32)/sr;a=np.zeros_like(t);rng=np.random.default_rng(807)
 for freq in (65.41,97.999,130.81,164.81):
  a+=.0035*np.sin(2*np.pi*freq*t)*(0.6+0.4*np.sin(2*np.pi*.055*t))
 for beat in np.arange(0,60,.75):
  start=int(beat*sr);n=min(int(.16*sr),len(a)-start);u=np.arange(n,dtype=np.float32)/sr
  a[start:start+n]+=.004*np.sin(2*np.pi*92*u)*np.exp(-u*20)
 for at in (6.5,12.5,19,25.5,32.3,39.5,47.1,53.4):
  start=int(at*sr);n=min(int(.3*sr),len(a)-start);u=np.arange(n,dtype=np.float32)/sr
  a[start:start+n]+=.004*rng.standard_normal(n)*np.exp(-u*15)
 a*=np.minimum(1,np.minimum(t,60-t)).clip(0,1)
 with wave.open(str(path),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes((a*32767).astype('<i2').tobytes())

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--stills',action='store_true');p.add_argument('--output',default='deliverables/celebrity-day-pov.mp4');args=p.parse_args()
 if args.stills:
  for t in (1,4,8,13,16,21,27,30,34,37,41,44,49,52,56):compose(t).save(P/f'preview-{t}.jpg')
  return
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as td:
  video=Path(td)/'video.mp4';music=Path(td)/'score.wav';score(music)
  proc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(video)],stdin=subprocess.PIPE)
  for n in range(FPS*DUR):
   proc.stdin.write(compose(n/FPS).tobytes())
   if n%150==0:print('FRAME',n,flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('encode failed')
  entries=json.loads((P/'script.json').read_text());inputs=[]
  for k in range(len(entries)):inputs+=['-i',str(P/'audio'/f'{k+1:02}.wav')]
  filters=[f'[{i+1}:a]aresample=48000,adelay={int(x["start"]*1000)}:all=1[v{i+1}]' for i,x in enumerate(entries)]
  filters+=['[10:a]volume=0.8[m]',''.join(f'[v{i+1}]' for i in range(len(entries)))+'[m]amix=inputs=10:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]']
  subprocess.run([ff,'-y','-v','error','-i',str(video),*inputs,'-i',str(music),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
 print('OUTPUT',out)
if __name__=='__main__':main()
