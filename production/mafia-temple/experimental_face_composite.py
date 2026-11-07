#!/usr/bin/env python3
"""Research-only tracked-face compositing test, NOT a production renderer.

Input MUST be the square StableAnimator running test at 512x512. The source is
an approved AI-generated keyframe, not the original reference photo. This
reprojects a *static* face into a moving shot: it cannot animate expression,
change the view realistically, or guarantee likeness, contact, or continuity.
Never pass its output off as a final film. Requires OpenCV, MediaPipe, Pillow,
NumPy, and FFmpeg (or imageio-ffmpeg).
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
LANDMARKS = [33,263,1,61,291,152]


def detect(mesh, bgr):
    # Known pilot framing; other shots/views require a separate tracker.
    crop = bgr[10:180, 170:350]
    rgb = cv2.cvtColor(cv2.resize(crop, (720, 680)), cv2.COLOR_BGR2RGB)
    result = mesh.process(rgb)
    if not result.multi_face_landmarks:
        raise ValueError('Face detection failed; refusing to use an untracked patch')
    return np.array([(170 + p.x * 180, 10 + p.y * 170)
                     for p in result.multi_face_landmarks[0].landmark], dtype=np.float32)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('output', type=Path, help='Experimental preview, not final footage')
    args = parser.parse_args()
    # Exact crop used as StableAnimator input.
    reference = (Image.open(ROOT/'keyframes/shot-04.jpg').convert('RGB')
                 .crop((345,30,1057,742)).resize((512,512),Image.Resampling.LANCZOS))
    source = cv2.cvtColor(np.asarray(reference), cv2.COLOR_RGB2BGR)
    capture = cv2.VideoCapture(str(args.video))
    if not capture.isOpened() or (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))) != (512,512):
        raise ValueError('Expected 512x512 running pilot')
    fps = capture.get(cv2.CAP_PROP_FPS)
    if not 0 < fps < 120:
        raise ValueError('Invalid input frame rate')
    face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True,max_num_faces=1,min_detection_confidence=.25)
    src_points = detect(face_mesh,source)
    mask = np.zeros((512,512),np.uint8)
    cv2.fillConvexPoly(mask,cv2.convexHull(src_points[OVAL].astype(np.int32)),255)
    mask = cv2.GaussianBlur(mask,(7,7),2)
    previous = None
    try:
        with tempfile.TemporaryDirectory(prefix='run-face-qa-') as temp:
            count = 0
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                dst_points = detect(face_mesh,frame)
                transform, _ = cv2.estimateAffinePartial2D(src_points[LANDMARKS],dst_points[LANDMARKS],method=cv2.LMEDS)
                if transform is None or not np.isfinite(transform).all():
                    raise ValueError(f'Face alignment failed at frame {count}')
                if previous is not None:
                    transform = .75*transform + .25*previous
                previous = transform
                warped = cv2.warpAffine(source,transform,(512,512),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
                alpha = cv2.warpAffine(mask,transform,(512,512)).astype(np.float32)[:,:,None]/255
                result = np.clip(warped.astype(np.float32)*alpha+frame.astype(np.float32)*(1-alpha),0,255).astype(np.uint8)
                if not cv2.imwrite(str(Path(temp)/f'frame_{count:04d}.png'),result):
                    raise OSError('Unable to save preview frame')
                count += 1
            if not count:
                raise ValueError('Empty video')
            import imageio_ffmpeg
            args.output.parent.mkdir(parents=True,exist_ok=True)
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error',
                '-framerate',str(fps),'-i',str(Path(temp)/'frame_%04d.png'),
                '-c:v','libx264','-crf','16','-pix_fmt','yuv420p',str(args.output)],check=True)
            print(f'{count} frames, {fps:g} fps; experimental static-face patch, NOT production footage')
    finally:
        capture.release()
        face_mesh.close()


if __name__ == '__main__':
    main()
