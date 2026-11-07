"""Rear-view controls for the 07_05 CMU slow walk research test.

No mocap source is stored in the repo. Frame 20..495 at 120Hz yields 96
consecutive, not looped, output frames at 24fps. Root translation is removed
for a tracking camera; the resulting still background is not itself a tracking
shot. Joint mapping and simulated contact require visual QA.
"""
from pathlib import Path
import numpy as np
from bvh import Bvh
from PIL import Image, ImageDraw
from mocap_to_poses import JOINTS, LIMBS, joint_matrix


def make_poses(bvh_text, output_dir, *_):
    motion=Bvh(bvh_text)
    if motion.nframes < 496 or abs(motion.frame_time - 1/120) > .0001:
        raise ValueError('Expected 120 Hz capture 07_05, 496 frames minimum')
    dest=Path(output_dir);dest.mkdir(parents=True,exist_ok=True)
    # Root travels approximately +Z in this take, viewed from behind. BVH +X
    # appears on image right; translation is removed for camera tracking.
    for i, frame in enumerate(range(20,500,5)):
        cache={}; pos={name:joint_matrix(motion,name,frame,cache)[:3,3] for name in JOINTS}
        root=pos['Hips']
        points={name:(round(256+18*(p[0]-root[0])),round(474-18*(p[1]-1))) for name,p in pos.items()}
        points['Nose']=points['Head']  # no visible face landmarks in rear view
        canvas=Image.new('RGB',(512,512));draw=ImageDraw.Draw(canvas)
        for a,b,color in LIMBS: draw.line([points[a],points[b]],fill=color,width=8)
        for _,b,color in LIMBS:
            x,y=points[b];draw.ellipse((x-4,y-4,x+4,y+4),fill=tuple(min(255,round(c/.6)) for c in color))
        canvas.save(dest/f'frame_{i}.png')
    return 96
