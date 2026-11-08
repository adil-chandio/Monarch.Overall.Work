#!/usr/bin/env python3
"""Approximate a descending camera from a still and estimated relative depth.

Research only. This is a single-image 2.5D reprojection, not a real 3D scene:
there are no hidden surfaces or physically measured depths, and large camera
moves may reveal distortions, duplicated edges, and invented geometry.
Requires OpenCV, NumPy and imageio-ffmpeg.
"""
import argparse
from pathlib import Path
import subprocess
import cv2
import imageio_ffmpeg
import numpy as np


def depth_reproject(image, depth, phase, forward=.085, down=.022, crop=.90, iterations=4):
 """Inverse-project a plane of normalized near=1 relative depth, no z-buffer."""
 if image.ndim!=3 or image.shape[:2]!=depth.shape: raise ValueError('Image and depth size mismatch')
 if not 0<=phase<=1 or not 0<crop<=1 or iterations<1: raise ValueError('Invalid camera parameters')
 h,w=depth.shape; yy,xx=np.indices((h,w),dtype=np.float32)
 cx=(w-1)/2;cy=(h-1)*.55;focal=w*1.10
 target_x=cx+(xx-cx)*crop;target_y=cy+(yy-cy)*crop
 z_shift=forward*phase; y_shift=down*phase
 u=target_x.copy();v=target_y.copy()
 for _ in range(iterations):
  d=cv2.remap(depth,u,v,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
  inv_z=.60+.90*np.clip(d,0,1)
  u=cx+(target_x-cx)*(1-z_shift*inv_z)
  v=cy+(target_y-cy)*(1-z_shift*inv_z)+focal*y_shift*inv_z
 return cv2.remap(image,u,v,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--image',type=Path,required=True);p.add_argument('--depth',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--frames',type=int,default=96);p.add_argument('--forward',type=float,default=.085);p.add_argument('--down',type=float,default=.022);p.add_argument('--crop',type=float,default=.90);p.add_argument('--fog',action='store_true',help='add a synthetic drifting ground-mist layer');a=p.parse_args()
 if a.frames<2 or not 0<=a.forward<=.25 or not 0<=a.down<=.1 or not 0<a.crop<=1:raise ValueError('Camera parameters out of bounds')
 image=cv2.imread(str(a.image),cv2.IMREAD_COLOR);depth=cv2.imread(str(a.depth),cv2.IMREAD_UNCHANGED)
 if image is None or depth is None or depth.ndim!=2:raise ValueError('Missing/invalid image or depth')
 image=cv2.resize(image,(1280,720),interpolation=cv2.INTER_AREA)
 scale=65535 if depth.dtype==np.uint16 else 255
 depth=cv2.resize(depth.astype('float32')/scale,(1280,720),interpolation=cv2.INTER_LINEAR)
 depth=cv2.bilateralFilter(depth,7,.06,4)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 if a.fog:
  rng=np.random.default_rng(419)
  noise=cv2.resize(rng.random((16,64),dtype=np.float32),(1536,720),interpolation=cv2.INTER_CUBIC)
  noise2=cv2.resize(rng.random((24,100),dtype=np.float32),(1536,720),interpolation=cv2.INTER_CUBIC)
  row=np.arange(720,dtype='float32')/720
  band=np.exp(-((row-.72)/.13)**2)[:,None]
 proc=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1280x720','-r','24','-i','pipe:0','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(a.output)],stdin=subprocess.PIPE)
 try:
  for i in range(a.frames):
   t=i/(a.frames-1);t=t*t*(3-2*t)
   frame=depth_reproject(image,depth,t,forward=a.forward,down=a.down,crop=a.crop)
   if a.fog:
    # Slow advected 2D noise only. It does not interact with true 3D geometry.
    offset=round(65*t);f=.55*noise[:,offset:offset+1280]+.45*noise2[:,(100-offset):(1380-offset)]
    alpha=(np.clip(f,0,1)*band*.13)[:,:,None]
    frame=(frame.astype('float32')*(1-alpha)+np.array([95,98,97],dtype='float32')*alpha).clip(0,255).astype('uint8')
   proc.stdin.write(frame.tobytes())
  proc.stdin.close()
  if proc.wait()!=0:raise RuntimeError('Encoding failed')
 finally:
  if proc.poll() is None:
   if proc.stdin and not proc.stdin.closed:proc.stdin.close()
   proc.wait()
 print(f'{a.frames} frames; approximate 2.5D reprojection of one image, not genuine 3D; research only')

if __name__=='__main__':main()
