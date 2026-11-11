#!/usr/bin/env python3
"""Local likeness experiment, NOT a finished or authenticated facial performance.

Blends a static generated-keyframe face into a portrait run. A moving mouth is
retained from the target, but most of the overlaid face is frozen; 2D alignment
cannot reconstruct out-of-plane motion, lighting, or guaranteed likeness.
Inputs and outputs stay wherever the operator places them; no uploads occur.
Requires OpenCV, MediaPipe, NumPy and imageio-ffmpeg.
"""
import argparse, subprocess
from pathlib import Path
import cv2
import imageio_ffmpeg
import mediapipe as mp
import numpy as np

W,H=576,1024
OVAL=[10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
ANCHOR=[33,263,1,61,291,152,10,168]
MOUTH=[61,40,37,0,267,270,291,321,314,17,84,91]

def detect(mesh,img):
 crop=img[130:550,140:460]
 result=mesh.process(cv2.cvtColor(cv2.resize(crop,(640,840)),cv2.COLOR_BGR2RGB))
 if not result.multi_face_landmarks:raise ValueError('Face tracking failed; refusing untracked patch')
 return np.array([(140+l.x*320,130+l.y*420) for l in result.multi_face_landmarks[0].landmark],dtype=np.float32)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--video',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--opacity',type=float,default=.60);a=p.parse_args()
 if not 0<=a.opacity<=1:raise ValueError('Opacity must be between zero and one')
 src=cv2.imread(str(a.source));cap=cv2.VideoCapture(str(a.video))
 if src is None or src.shape[:2]!=(H,W) or not cap.isOpened() or (int(cap.get(3)),int(cap.get(4)))!=(W,H):raise ValueError('Expected 576x1024 source and video')
 fps=cap.get(5);total=int(cap.get(7))
 if not 0<fps<120 or total<2:raise ValueError('Invalid video length or FPS')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 proc=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','576x1024','-r',str(fps),'-i','pipe:0','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(a.output)],stdin=subprocess.PIPE)
 try:
  with mp.solutions.face_mesh.FaceMesh(static_image_mode=True,refine_landmarks=True,min_detection_confidence=.25) as mesh:
   s=detect(mesh,src);mask=np.zeros((H,W),np.uint8);cv2.fillConvexPoly(mask,cv2.convexHull(s[OVAL].astype('int32')),255)
   mask=cv2.erode(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)));mask=cv2.GaussianBlur(mask,(0,0),4);prev=None
   for i in range(total):
    ok,frame=cap.read()
    if not ok:raise ValueError(f'Video ended early at frame {i}')
    d=detect(mesh,frame);transform,_=cv2.estimateAffinePartial2D(s[ANCHOR],d[ANCHOR],method=cv2.LMEDS)
    if transform is None or not np.isfinite(transform).all():raise ValueError(f'Alignment failed at frame {i}')
    if prev is not None:transform=.8*transform+.2*prev
    prev=transform
    warped=cv2.warpAffine(src,transform,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    alpha=cv2.warpAffine(mask,transform,(W,H)).astype('float32')/255*a.opacity
    mm=np.zeros((H,W),np.uint8);cv2.fillConvexPoly(mm,cv2.convexHull(d[MOUTH].astype('int32')),255);mm=cv2.dilate(mm,np.ones((5,5),np.uint8));mm=cv2.GaussianBlur(mm,(0,0),3);alpha*=1-mm/255.
    frame=(frame.astype('float32')*(1-alpha[:,:,None])+warped.astype('float32')*alpha[:,:,None]).clip(0,255).astype('uint8')
    proc.stdin.write(frame.tobytes())
  proc.stdin.close()
  if proc.wait()!=0:raise RuntimeError('Encoding failed')
  print(f'{total} frames; static face blend, identity and temporal QA required; research only')
 finally:
  cap.release()
  if proc.poll() is None:
   if proc.stdin and not proc.stdin.closed:proc.stdin.close()
   proc.wait()

if __name__=='__main__':main()
