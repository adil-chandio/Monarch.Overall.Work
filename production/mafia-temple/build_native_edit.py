#!/usr/bin/env python3
"""Assemble a 20s review cut from native WAN motion frames, no interpolation.

Requires numpy, opencv-python-headless, mediapipe, and imageio-ffmpeg.
Tracks iris landmarks for a subtle red-eye VFX in the close-up. It cannot fix
identity drift or guarantee artifact-free generated motion.
"""
from pathlib import Path
import subprocess
import numpy as np
import cv2
import mediapipe as mp
import imageio_ffmpeg

root=Path(__file__).resolve().parent
ff=imageio_ffmpeg.get_ffmpeg_exe()
shots=[('wan4-street-b',96),('wan4-gate',120),('wan4-aerial',96),('wan3-running',72),('wan4-face-a',96)]
w,h=512,288;frame_bytes=w*h*3
out=root/'monarch-temple-native-review.mp4'
cmd=[ff,'-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r','24','-i','pipe:0','-i',str(root/'monarch-mafia-temple-20s.mp4'),'-map','0:v','-map','1:a:0','-vf','scale=1280:720:flags=lanczos,format=yuv420p','-c:v','libx264','-preset','medium','-crf','18','-c:a','aac','-b:a','192k','-t','20','-movflags','+faststart',str(out)]
encoder=subprocess.Popen(cmd,stdin=subprocess.PIPE)
with mp.solutions.face_mesh.FaceMesh(static_image_mode=False,refine_landmarks=True,min_detection_confidence=.45,min_tracking_confidence=.45) as mesh:
 for name,count in shots:
  raw=subprocess.check_output([ff,'-v','error','-i',str(root/'clips'/f'{name}.mp4'),'-pix_fmt','rgb24','-f','rawvideo','-'])
  if len(raw)<frame_bytes*count: raise RuntimeError(f'Not enough frames in {name}')
  smoothed=None;misses=0
  for i in range(count):
   frame=np.frombuffer(raw[i*frame_bytes:(i+1)*frame_bytes],dtype=np.uint8).reshape(h,w,3).copy()
   if name=='wan4-face-a':
    detection=mesh.process(frame)
    if detection.multi_face_landmarks:
     lm=detection.multi_face_landmarks[0].landmark
     points=np.array([(lm[k].x*w,lm[k].y*h) for k in [468,473]],dtype=np.float32)
     if smoothed is None: smoothed=points
     else: smoothed=smoothed*.60+points*.40
     misses=0
    else: misses+=1
    # The eyes appear only after he is facing camera; fade the effect in.
    strength=np.clip((i-43)/22,0,1)
    if smoothed is not None and misses<2 and strength>0:
     mask=np.zeros((h,w),np.float32)
     for x,y in smoothed:
      cv2.circle(mask,(round(float(x)),round(float(y))),1,1.0,-1,lineType=cv2.LINE_AA)
     glow=cv2.GaussianBlur(mask,(0,0),sigmaX=2.0,sigmaY=1.4)
     base=cv2.GaussianBlur(mask,(0,0),sigmaX=.65,sigmaY=.65)
     # Controlled red light; apply to pixels in-place without overlapping frames.
     arr=frame.astype(np.float32)
     arr[:,:,0]=np.clip(arr[:,:,0]+strength*(glow*100+base*180),0,255)
     arr[:,:,1]=np.clip(arr[:,:,1]*(1-strength*base*.35)+strength*glow*12,0,255)
     arr[:,:,2]=np.clip(arr[:,:,2]*(1-strength*base*.45),0,255)
     frame=arr.astype(np.uint8)
   encoder.stdin.write(frame.tobytes())
  print(name, count,flush=True)
encoder.stdin.close()
if encoder.wait()!=0: raise RuntimeError('Video encoding failed')
print('REVIEW CUT',out,flush=True)
