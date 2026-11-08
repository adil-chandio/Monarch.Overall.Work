#!/usr/bin/env python3
"""Assemble an internal five-scene research study for frame-by-frame QA.

Not a final film. It deliberately refuses to invent missing shot inputs. Its
512px diffusion shots are enlarged, the tracking plates are flat approximations,
foley is provisionally timed, and research-model licenses remain unresolved.
Requires OpenCV, NumPy, imageio-ffmpeg and externally supplied sound mix.
"""
import argparse
from pathlib import Path
import subprocess
import cv2
import imageio_ffmpeg
import numpy as np

ROOT=Path(__file__).resolve().parent
FPS=24
WIDTH=1280
HEIGHT=720


def frames(path,count):
 cap=cv2.VideoCapture(str(path))
 if not cap.isOpened():raise ValueError(f'Cannot read {path}')
 actual_fps=cap.get(cv2.CAP_PROP_FPS)
 if abs(actual_fps-FPS)>.01:raise ValueError(f'Expected 24 fps: {path}')
 try:
  for i in range(count):
   ok,frame=cap.read()
   if not ok:raise ValueError(f'{path} ended at frame {i}; expected {count}')
   yield frame
 finally:cap.release()


def fit_cover(frame,width=WIDTH,height=HEIGHT):
 # Center-crop to target aspect before resizing; never stretch faces.
 h,w=frame.shape[:2]
 if w*height>h*width:
  crop_w=max(1,round(h*width/height));x=(w-crop_w)//2;frame=frame[:,x:x+crop_w]
 elif w*height<h*width:
  crop_h=max(1,round(w*height/width));y=(h-crop_h)//2;frame=frame[y:y+crop_h,:]
 return cv2.resize(frame,(width,height),interpolation=cv2.INTER_LANCZOS4)


def aerial_transform(frame,i):
 # Smooth digital push over a moving generated clip. It is NOT a physical
 # descending 3D camera; the distinction must remain visible in QA notes.
 h,w=frame.shape[:2];t=i/95;t=t*t*(3-2*t)
 mat=cv2.getRotationMatrix2D((w/2,h*.56),0,1+.22*t);mat[1,2]-=h/288*8*t
 return cv2.warpAffine(frame,mat,(w,h),flags=cv2.INTER_LANCZOS4)


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--walk',type=Path,required=True);p.add_argument('--run',type=Path,required=True)
 p.add_argument('--close',type=Path,required=True);p.add_argument('--audio',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args()
 shots=[('walk',a.walk,96),('gate',ROOT/'clips/wan4-gate.mp4',120),('aerial',ROOT/'clips/wan4-aerial.mp4',96),('run',a.run,72),('close',a.close,96)]
 for _,path,_ in shots:
  if not path.is_file():raise FileNotFoundError(path)
 if not a.audio.is_file():raise FileNotFoundError(a.audio)
 a.out.parent.mkdir(parents=True,exist_ok=True); ff=imageio_ffmpeg.get_ffmpeg_exe()
 cmd=[ff,'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{WIDTH}x{HEIGHT}','-r',str(FPS),'-i','pipe:0',
      '-i',str(a.audio),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',
      '-c:a','aac','-b:a','192k','-t','20','-movflags','+faststart',str(a.out)]
 enc=subprocess.Popen(cmd,stdin=subprocess.PIPE);total=0
 try:
  for name,path,count in shots:
   for i,frame in enumerate(frames(path,count)):
    if name=='aerial':frame=aerial_transform(frame,i)
    if frame.shape[:2]!=(HEIGHT,WIDTH):frame=fit_cover(frame)
    enc.stdin.write(frame.tobytes());total+=1
   print(name,count,flush=True)
  if total!=480:raise ValueError('Wrong total frame count')
  enc.stdin.close()
  if enc.wait()!=0:raise RuntimeError('Encoding failed')
  print('20-second INTERNAL RESEARCH STUDY ONLY, not a final or cleared film')
 finally:
  if enc.poll() is None:
   if enc.stdin and not enc.stdin.closed:enc.stdin.close()
   enc.wait()

if __name__=='__main__':main()
