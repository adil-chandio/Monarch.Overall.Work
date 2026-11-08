#!/usr/bin/env python3
"""Make every-frame review sheets and basic metadata for a research clip.

Metrics here cannot certify likeness, anatomy, or physical contact. Outputs
are local review aids, not final video assets.
"""
import argparse, json, pathlib
import cv2
import numpy as np
from PIL import Image, ImageDraw

p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--out',required=True);a=p.parse_args()
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
cap=cv2.VideoCapture(a.video)
if not cap.isOpened(): raise SystemExit('Cannot open video')
fps=cap.get(cv2.CAP_PROP_FPS); frames=[]
while True:
    ok,frame=cap.read()
    if not ok: break
    frames.append(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
cap.release()
if not frames: raise SystemExit('Video contained no decodable frames')
h,w=frames[0].shape[:2]
if any(f.shape!=(h,w,3) for f in frames): raise SystemExit('Variable-size frames')
# Full frame sheets in temporal order. 7 frames per sheet, no frame skipped.
for start in range(0,len(frames),7):
    chunk=frames[start:start+7]; tile_w=240; tile_h=round(h*tile_w/w)
    canvas=Image.new('RGB',(len(chunk)*tile_w,tile_h+28),'white');d=ImageDraw.Draw(canvas)
    for j,frame in enumerate(chunk):
        tile=Image.fromarray(frame).resize((tile_w,tile_h),Image.Resampling.LANCZOS)
        canvas.paste(tile,(j*tile_w,0));d.text((j*tile_w+3,tile_h+4),f'frame {start+j}',fill='black')
    canvas.save(out/f'frames-{start:03d}-{start+len(chunk)-1:03d}.jpg',quality=92)
# Absolute mean pixel differences are descriptive only: camera motion and
# illumination can dominate them, so a threshold is not a quality assessment.
deltas=[float(np.mean(cv2.absdiff(frames[i-1],frames[i]))) for i in range(1,len(frames))]
meta={'frames_decoded':len(frames),'fps':fps,'width':w,'height':h,'duration_encoded_seconds':len(frames)/fps if fps else None,'frame_difference_mean':float(np.mean(deltas)) if deltas else None,'frame_difference_max':max(deltas) if deltas else None,'warning':'These numbers do not establish likeness, gait, foot contact, or visual quality. Review every frame and real-time playback.'}
(out/'inspection-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2))
