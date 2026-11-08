#!/usr/bin/env python3
"""Experimental 2D running composite; NOT a finished or realistic 3D shot.

Uses a generated empty-courtyard plate and subject segmentation from the
research-only 576x1024 run pilot. The plate pans behind the body as a crude
tracking-camera test. This cannot repair anatomy, face identity, shadows, foot
contact, occlusions, lighting, parallax or temporal artifacts. The optional
tracked-face patch freezes expression; do not present output as a final film.
Requires OpenCV, MediaPipe, NumPy and imageio-ffmpeg.
"""
import argparse
from pathlib import Path
import subprocess
import cv2
import imageio_ffmpeg
import mediapipe as mp
import numpy as np

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path,help='576x1024 running research clip')
    p.add_argument('output',type=Path)
    p.add_argument('--shadow',action='store_true',help='test approximate pose-tracked ground shadows')
    args=p.parse_args()
    cap=cv2.VideoCapture(str(args.input))
    if not cap.isOpened() or (int(cap.get(3)),int(cap.get(4)))!=(576,1024):
        raise ValueError('Expected 576x1024 running research clip')
    fps=cap.get(cv2.CAP_PROP_FPS);total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not 0<fps<120 or total<2: raise ValueError('Invalid video length or frame rate')
    plate=cv2.imread(str(ROOT/'keyframes/courtyard-clean-vfx.jpg'))
    if plate is None: raise ValueError('Missing generated background plate')
    plate=cv2.resize(plate,(1376,768))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-f','rawvideo',
         '-pix_fmt','bgr24','-s','1280x720','-r',str(fps),'-i','pipe:0',
         '-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(args.output)]
    enc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as seg, mp.solutions.pose.Pose(model_complexity=1, min_detection_confidence=.5, min_tracking_confidence=.5) as pose:
            for i in range(total):
                ok,frame=cap.read()
                if not ok: raise ValueError(f'Video ended early at frame {i}')
                mask=seg.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).segmentation_mask
                binary=(mask>.35).astype('uint8')
                count,labels,stats,_=cv2.connectedComponentsWithStats(binary,8)
                if count<2: raise ValueError(f'No foreground found at frame {i}')
                idx=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
                binary=(labels==idx).astype('uint8')
                binary=cv2.morphologyEx(binary,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
                alpha=cv2.GaussianBlur(binary.astype('float32'),(0,0),1.5)
                # This is a flat-image pan, not genuine 3D parallax.
                x0=30+round(80*i/(total-1))
                bg=cv2.resize(plate[45:720,x0:x0+1200],(1280,720),interpolation=cv2.INTER_LANCZOS4)
                if args.shadow:
                    # Fictitious fixed floor plane, not solved 3D geometry. Foot
                    # points are approximate; depth and contact need manual QA.
                    pred=pose.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
                    if not pred.pose_landmarks:
                        raise ValueError(f'Pose lost at frame {i}; cannot place shadows')
                    lm=pred.pose_landmarks.landmark
                    shade=np.zeros((720,1280),np.float32)
                    for heel,toe in ((29,31),(30,32)):
                        if min(lm[heel].visibility,lm[toe].visibility)<.5:
                            raise ValueError(f'Foot tracking unreliable at frame {i}')
                        x=410+int((lm[heel].x+lm[toe].x)*.5*405)
                        height=max(0,676-max(lm[heel].y,lm[toe].y)*720)
                        strength=.38*float(np.exp(-height/75))
                        cv2.ellipse(shade,(x,676),(round(17+height*.07),round(4+height*.02)),0,0,360,strength,-1,cv2.LINE_AA)
                    shade=cv2.GaussianBlur(shade,(0,0),4)
                    bg=(bg.astype('float32')*(1-shade[:,:,None])).astype('uint8')
                actor=cv2.resize(frame,(405,720),interpolation=cv2.INTER_LANCZOS4)
                alpha=cv2.resize(alpha,(405,720),interpolation=cv2.INTER_LINEAR)[:,:,None]
                bg[:,410:815]=(actor*alpha+bg[:,410:815]*(1-alpha)).astype('uint8')
                enc.stdin.write(bg.tobytes())
        enc.stdin.close()
        if enc.wait()!=0: raise RuntimeError('Encoding failed')
        print(f'{total} frames; flat plate, unverified masks and contact; RESEARCH ONLY')
    finally:
        cap.release()
        if enc.poll() is None:
            if enc.stdin and not enc.stdin.closed: enc.stdin.close()
            enc.wait()


if __name__=='__main__': main()
