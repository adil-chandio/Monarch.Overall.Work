#!/usr/bin/env python3
"""Experimental flat-plate dolly for a rear-view 512px walk test.

Not a finished shot. The background zoom is a 2D approximation, not real 3D
parallax; motion, contact, lighting, mask edges and model rights require QA.
"""
import argparse
from pathlib import Path
import subprocess
import cv2
import imageio_ffmpeg
import mediapipe as mp
import numpy as np
from research_depth_camera import depth_reproject
ROOT=Path(__file__).resolve().parent


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--depth',type=Path,help='relative depth for experimental 2.5D camera');a=p.parse_args()
 cap=cv2.VideoCapture(str(a.input));fps=cap.get(cv2.CAP_PROP_FPS);total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 if not cap.isOpened() or (int(cap.get(3)),int(cap.get(4)))!=(512,512) or not 0<fps<120 or total<2: raise ValueError('Expected 512x512 walk research clip')
 plate=cv2.imread(str(ROOT/'keyframes/street-clean-vfx.jpg'))
 if plate is None: raise ValueError('Missing background plate')
 plate=cv2.resize(plate,(1280,720)); depth=None
 if a.depth:
  depth=cv2.imread(str(a.depth),cv2.IMREAD_UNCHANGED)
  if depth is None or depth.ndim!=2:raise ValueError('Invalid depth map')
  divisor=65535 if depth.dtype==np.uint16 else 255
  depth=cv2.resize(depth.astype('float32')/divisor,(1280,720),interpolation=cv2.INTER_LINEAR)
  depth=cv2.bilateralFilter(depth,7,.06,4)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 enc=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1280x720','-r',str(fps),'-i','pipe:0','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(a.output)],stdin=subprocess.PIPE)
 try:
  with mp.solutions.pose.Pose(model_complexity=1,enable_segmentation=True,min_detection_confidence=.5,min_tracking_confidence=.5) as pose:
   for i in range(total):
    ok,frame=cap.read()
    if not ok: raise ValueError(f'Video ended early at frame {i}')
    result=pose.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    if result.segmentation_mask is None: raise ValueError(f'No pose segmentation at frame {i}')
    mask=result.segmentation_mask
    binary=(mask>.35).astype('uint8');count,labels,stats,_=cv2.connectedComponentsWithStats(binary,8)
    if count<2: raise ValueError(f'No foreground at frame {i}')
    idx=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);binary=(labels==idx).astype('uint8')
    binary=cv2.morphologyEx(binary,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8));alpha=cv2.GaussianBlur(binary.astype('float32'),(0,0),1.5)
    t=i/(total-1)
    if depth is not None:
     smooth=t*t*(3-2*t);bg=depth_reproject(plate,depth,smooth,forward=.10,down=0,crop=.91)
    else:
     mat=cv2.getRotationMatrix2D((640,345),0,1+.16*t)
     bg=cv2.warpAffine(plate,mat,(1280,720),flags=cv2.INTER_LANCZOS4)
    actor=cv2.resize(frame,(720,720),interpolation=cv2.INTER_LANCZOS4);alpha=cv2.resize(alpha,(720,720),interpolation=cv2.INTER_LINEAR)[:,:,None]
    bg[:,108:828]=(actor*alpha+bg[:,108:828]*(1-alpha)).astype('uint8')
    enc.stdin.write(bg.tobytes())
  enc.stdin.close()
  if enc.wait()!=0: raise RuntimeError('Encoding failed')
  print(f'{total} frames; approximate plate camera, unverified masks and contact; RESEARCH ONLY')
 finally:
  cap.release()
  if enc.poll() is None:
   if enc.stdin and not enc.stdin.closed: enc.stdin.close()
   enc.wait()

if __name__=='__main__': main()
