"""No-stock 2.5D rebuild. Every visual frame is generated from independent layers.

Ship, duck and container are AI-generated keyed cutouts. The animated ocean,
map, lighting and motion are code-generated; no stock video is read. Existing
synthetic narration/music are supplied separately. The maps are illustrative.
"""
import argparse, math, subprocess, tempfile, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import imageio_ffmpeg
import render as base

W,H,FPS,DURATION=base.W,base.H,base.FPS,base.DURATION
ROOT=Path(__file__).resolve().parents[2]
CONTAINER=base.key_asset(Path(__file__).parent/'assets/container.png')
# Small, purposefully layered procedural water field; no pre-rendered plates.
SW,SH=360,640
YY,XX=np.mgrid[0:SH,0:SW].astype(np.float32)

def ocean(t):
 # Moving height-field-like light patterns; long and short waves advance at
 # different velocities, creating changing light and apparent depth.
 x=XX/SW;y=YY/SH
 drift=t*.12
 a=np.sin(x*21+y*31-drift*4.3)
 b=np.sin(x*39-y*19+drift*3.1)
 c=np.sin(x*74+y*67-drift*6.2)
 broad=np.sin(x*7-y*11+drift*1.7)
 glint=np.maximum(0,(a*.45+b*.3+c*.12+broad*.13)-.25)**2
 depth=np.clip(y,0,1)
 fog=np.exp(-((x-.70)**2/.12+(y-.22)**2/.09))
 vign=np.clip(1-.36*((x-.5)**2/.25+(y-.5)**2/.25),.45,1)
 arr=np.empty((SH,SW,3),np.uint8)
 for channel in range(3):
  v=([15,53,68][channel]+depth*[8,23,27][channel]+broad*[4,9,11][channel]+fog*[6,18,20][channel]+glint*[96,151,150][channel])*vign
  arr[:,:,channel]=np.clip(v,0,255).astype(np.uint8)
 return Image.fromarray(arr,'RGB').resize((W,H),Image.Resampling.BILINEAR)

def foreground(im,t):
 # Distinct front-plane highlights travel independently from the background.
 overlay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(overlay)
 for i in range(36):
  yy=520+(i*79)%600;xx=((i*173+t*(12+(i%4)*6))%860)-70
  length=16+(i%5)*9
  d.line((xx,yy,xx+length,yy-2),fill=(162,207,202,25+(i%4)*8),width=2)
 im.alpha_composite(overlay)
base.waves=foreground

def compose(t):
 bg=ocean(t)
 if 9.9<=t<13.1:
  u=t-9.9; im=Image.alpha_composite(bg.convert('RGBA'),Image.new('RGBA',(W,H),(3,20,29,45)))
  base.sprite(im,base.SHIP,338+u*36,675+u*4,880+u*30,angle=-2+math.sin(t)*2)
  v=base.ease((u-.5)/2);base.sprite(im,CONTAINER,470+v*100,680+v*210,140+v*60,angle=-8-v*35)
  foreground(im,t)
  base.labels(im,t,['A CONTAINER','OVERBOARD.'],'STYLIZED  /  NOT ARCHIVAL FOOTAGE',9.9)
  return im.convert('RGB')
 return base.compose(t,bg)

def make_cues(path):
 # Original procedural low-level impacts and air swell, not stock audio.
 sr=48000;t=np.arange(round(sr*DURATION))/sr
 bed=(np.sin(2*np.pi*61*t)+.3*np.sin(2*np.pi*92*t))*0.008
 for at in [0,3,9.9,12.1,13.1,17.2,22.55,29.3,33.05,39.4]:
  dt=t-at; m=(dt>=0)&(dt<.45);z=dt[m]
  bed[m]+=0.025*np.sin(2*np.pi*(95-60*z)*z)*np.exp(-z*9)
 data=(np.clip(bed,-.8,.8)*32767).astype('<i2')
 with wave.open(str(path),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(data.tobytes())

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--audio',default=str(ROOT/'deliverables/monarch-invisible-thread-animated.mp4'));a=p.parse_args()
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  picture=Path(temp)/'picture.mp4'; cues=Path(temp)/'cues.wav'
  enc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(picture)],stdin=subprocess.PIPE)
  for f in range(round(FPS*DURATION)):
   enc.stdin.write(compose(f/FPS).tobytes())
   if f%300==0:print(f'rendered {f}/{round(FPS*DURATION)}',flush=True)
  enc.stdin.close()
  if enc.wait():raise RuntimeError('picture encoding failed')
  make_cues(cues)
  flt='[1:a]highpass=f=35,acompressor=threshold=0.16:ratio=2.2:attack=10:release=150[v];[2:a]volume=0.55[s];[v][s]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]'
  subprocess.run([ff,'-y','-v','error','-i',str(picture),'-i',a.audio,'-i',str(cues),'-filter_complex',flt,'-map','0:v','-map','[a]','-t',str(DURATION),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)],check=True)
if __name__=='__main__':main()
