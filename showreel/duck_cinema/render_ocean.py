"""CPU ray-cast 3D ocean/toy moving-shot prototype. Requires NumPy + Pillow.

python showreel/duck_cinema/render_ocean.py --audio first_cut.mp4 --output ocean.mp4
All surfaces, camera, and waves are animated procedural geometry, no stills.
"""
import argparse, math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

W,H,FPS,DURATION=480,854,24,10
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT2='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def normalize(a):
 return a/(np.linalg.norm(a,axis=-1,keepdims=True)+1e-8)

def ocean(x,y,t):
 return .115*np.sin(x*1.8+y*.65-t*1.15)+.065*np.sin(y*2.9-x*.75-t*1.8)+.035*np.sin(x*4+y*3.3+t*.8)

def render(t):
 # Perspective camera, all arrays indexed by screen pixel.
 yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
 cam=np.array([1.7+0.28*math.sin(t*.18),-7.5+t*.11,1.72],dtype=np.float32)
 target=np.array([0,0,0.52],dtype=np.float32)
 forward=normalize(target-cam); right=normalize(np.cross(forward,np.array([0,0,1],dtype=np.float32)));up=np.cross(right,forward)
 v=(H/2-yy)/H;u=(xx-W/2)/H
 ray=normalize(forward+right*u[:,:,None]*.92+up*v[:,:,None]*.92)
 sky=np.clip(ray[:,:,2]*1.4+.3,0,1)
 col=np.empty((H,W,3),np.float32)
 col[:,:,0]=.035+sky*.17;col[:,:,1]=.071+sky*.19;col[:,:,2]=.102+sky*.20
 # Animated deep-water waves: iterative heightfield intersection, diffuse + specular.
 zdir=ray[:,:,2]; safe=np.where(np.abs(zdir)<.001,-.001,zdir)
 dist=-cam[2]/safe
 for _ in range(5):
  x=cam[0]+dist*ray[:,:,0];y=cam[1]+dist*ray[:,:,1]
  dist=(ocean(x,y,t)-cam[2])/safe
 x=cam[0]+dist*ray[:,:,0];y=cam[1]+dist*ray[:,:,1]
 water=(dist>0)&(dist<150)&(zdir<-.01)
 ep=.025; h=ocean(x,y,t);nx=(h-ocean(x+ep,y,t))/ep;ny=(h-ocean(x,y+ep,t))/ep
 n=normalize(np.stack([nx,ny,np.ones_like(nx)],axis=-1));light=normalize(np.array([-0.65,-.35,1],dtype=np.float32))
 diffuse=np.maximum(0,np.sum(n*light,axis=-1));half=normalize(light-ray)
 spec=np.maximum(0,np.sum(n*half,axis=-1))**42
 fresnel=np.clip((1-np.maximum(0,np.sum(n*-ray,axis=-1)))**3,0,1)
 fog=np.clip(dist/50,0,.65)
 for k,base in enumerate([.015,.070,.087]):
  wc=base+diffuse*[.025,.055,.06][k]+spec*[.75,.72,.6][k]+fresnel*[.10,.14,.16][k]
  wc=wc*(1-fog)+fog*[.09,.14,.17][k];col[:,:,k]=np.where(water,wc,col[:,:,k])
 # Toy: true analytic ellipsoids in 3D with nearest-hit occlusion, lighting and gloss.
 depth=np.where(water,dist,1e8).astype(np.float32)
 bob=float(ocean(np.array(0.),np.array(0.),t));
 def ellipsoid(center,radii,color,shine=45):
  nonlocal col,depth
  c=np.array(center,dtype=np.float32);r=np.array(radii,dtype=np.float32)
  oc=(cam-c)/r;d=ray/r; aa=np.sum(d*d,axis=-1);bb=2*np.sum(d*oc,axis=-1);cc=np.sum(oc*oc)-1
  disc=bb*bb-4*aa*cc; root=(-bb-np.sqrt(np.maximum(disc,0)))/(2*aa)
  hit=(disc>0)&(root>0)&(root<depth);depth=np.where(hit,root,depth)
  point=cam+root[:,:,None]*ray;norm=normalize((point-c)/(r*r));dif=np.maximum(0,np.sum(norm*light,axis=-1));half=normalize(light-ray)
  sp=np.maximum(0,np.sum(norm*half,axis=-1))**shine
  for k in range(3):col[:,:,k]=np.where(hit,color[k]*(.29+dif*.66)+sp*.55,col[:,:,k])
 # Far-to-near by geometry, depth buffer corrects order; front faces camera.
 ellipsoid([0,0,.28+bob],[.79,.54,.38],[.83,.49,.065])
 ellipsoid([0,-.37,.72+bob],[.41,.37,.43],[1,.69,.12])
 ellipsoid([.04,-.735,.63+bob],[.23,.23,.075],[.92,.24,.025])
 ellipsoid([.23,-.65,.81+bob],[.047,.045,.048],[.025,.018,.012])
 ellipsoid([-.22,-.65,.81+bob],[.047,.045,.048],[.025,.018,.012])
 # Tonemap and subtle lens vignette; composited moving type (no static images).
 vign=np.clip(1-.36*((xx-W/2)**2/(W/2)**2+(yy-H/2)**2/(H/2)**2),.42,1)
 col=np.clip(col*vign[:,:,None],0,1)**(1/2.0)
 im=Image.fromarray(np.uint8(col*255),'RGB');draw=ImageDraw.Draw(im)
 draw.text((28,31),'MONARCHS EDIT  /  THE INVISIBLE THREAD',font=ImageFont.truetype(FONT,12),fill=(199,213,207))
 if t<4.5: label=['ONE ACCIDENT.','A WORLD OF CLUES.']
 else:label=['29,000 TOYS.','ONE VAST OCEAN.']
 for i,s in enumerate(label):draw.text((27,120+i*42),s,font=ImageFont.truetype(FONT,29),fill=(245,242,225) if i==0 else (255,202,96),stroke_width=1,stroke_fill=(15,27,31))
 draw.text((28,790),'3D RECONSTRUCTION  /  NORTH PACIFIC, 1992',font=ImageFont.truetype(FONT2,11),fill=(204,216,212))
 return im

def main():
 p=argparse.ArgumentParser();p.add_argument('--audio',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 ff=imageio_ffmpeg.get_ffmpeg_exe();proc=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',a.audio,'-map','0:v','-map','1:a','-t',str(DURATION),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',a.output],stdin=subprocess.PIPE)
 for i in range(DURATION*FPS):
  proc.stdin.write(render(i/FPS).tobytes())
  if i%24==0:print('second',i//24,flush=True)
 proc.stdin.close()
 if proc.wait():raise RuntimeError('ffmpeg error')
if __name__=='__main__':main()
