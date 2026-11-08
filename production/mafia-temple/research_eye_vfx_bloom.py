#!/usr/bin/env python3
"""Tracked iris glow for a research close-up, not a finished VFX shot.

Requires OpenCV, MediaPipe, NumPy, imageio-ffmpeg. It aborts if face detection
is lost while the effect is visible; visual review is required for every frame,
including eye occlusion and whether the glow actually follows the irises.
"""
import argparse
from pathlib import Path
import subprocess
import cv2
import imageio_ffmpeg
import mediapipe as mp
import numpy as np


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 cap=cv2.VideoCapture(str(a.input));w=int(cap.get(3));h=int(cap.get(4));fps=cap.get(5);n=int(cap.get(7))
 if not cap.isOpened() or min(w,h)<100 or not 0<fps<120 or n<2: raise ValueError('Invalid input')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 proc=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(a.output)],stdin=subprocess.PIPE)
 try:
  with mp.solutions.face_mesh.FaceMesh(static_image_mode=False,refine_landmarks=True,min_detection_confidence=.45,min_tracking_confidence=.45) as mesh:
   for i in range(n):
    ok,frame=cap.read()
    if not ok: raise ValueError(f'Input ended at frame {i}')
    result=mesh.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    t=i/(n-1); fade=np.clip((t-.64)/.20,0,1);fade=fade*fade*(3-2*fade)
    if fade:
     if not result.multi_face_landmarks: raise ValueError(f'Face tracking lost at frame {i}')
     lm=result.multi_face_landmarks[0].landmark
     eye_data=[(468,[469,470,471,472],[33,160,158,133,153,144]),(473,[474,475,476,477],[362,385,387,263,373,380])]
     core=np.zeros((h,w),np.float32);eye_mask=np.zeros((h,w),np.float32)
     for center,iris,eye in eye_data:
      cx=lm[center].x*w;cy=lm[center].y*h
      radius=float(np.mean([np.hypot(lm[k].x*w-cx,lm[k].y*h-cy) for k in iris]))
      if not 1.5<radius<.04*w: raise ValueError(f'Unreliable iris at frame {i}')
      cv2.circle(core,(round(cx),round(cy)),max(1,round(radius*.85)),1.,-1,cv2.LINE_AA)
      polygon=np.array([[(round(lm[k].x*w),round(lm[k].y*h)) for k in eye]],np.int32)
      cv2.fillPoly(eye_mask,polygon,1.,lineType=cv2.LINE_AA)
     eye_mask=cv2.GaussianBlur(eye_mask,(0,0),1.0)
     iris=cv2.GaussianBlur(core,(0,0),.8)*eye_mask
     # A hot red-orange source and two soft additive bloom scales. The larger
     # halo is deliberately restrained so it lights nearby skin rather than
     # looking like a flat red filter. This is still a 2D approximation.
     near=cv2.GaussianBlur(core,(0,0),max(2,w/320))
     far=cv2.GaussianBlur(core,(0,0),max(3,w/100))
     arr=frame.astype(np.float32)
     alpha=(iris*fade*.85)[:,:,None]
     hot=np.empty_like(arr)
     hot[:,:,0]=28;hot[:,:,1]=55;hot[:,:,2]=255
     arr=arr*(1-alpha)+hot*alpha
     arr[:,:,2]+=fade*(near*115+far*90)
     arr[:,:,1]+=fade*(near*14+far*7)
     arr[:,:,0]+=fade*(near*3+far*2)
     frame=np.clip(arr,0,255).astype('uint8')
    proc.stdin.write(frame.tobytes())
  proc.stdin.close()
  if proc.wait()!=0:raise RuntimeError('Encoding failed')
  print(f'{n} tracked frames; research preview only; inspect every glow frame')
 finally:
  cap.release()
  if proc.poll() is None:
   if proc.stdin and not proc.stdin.closed:proc.stdin.close()
   proc.wait()

if __name__=='__main__': main()
