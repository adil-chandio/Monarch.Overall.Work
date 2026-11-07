"""Build research pose controls from CMU motion 09_01 (120 Hz) at 24 fps.

The root translation is removed for a tracking camera. This is an experimental
side projection, not a full camera or cloth/foot-contact simulation.
"""
from math import cos, radians, sin
from pathlib import Path
import numpy as np
from bvh import Bvh
from PIL import Image, ImageDraw

JOINTS = ['Hips','LeftUpLeg','LeftLeg','LeftFoot','LeftToeBase','RightUpLeg','RightLeg','RightFoot','RightToeBase','Neck1','Head','LeftArm','LeftForeArm','LeftHand','RightArm','RightForeArm','RightHand']
# COCO/OpenPose ordering and colors expected by StableAnimator's DWPose renderer.
LIMBS=[('Neck1','RightArm',(153,0,0)),('Neck1','LeftArm',(153,51,0)),
       ('RightArm','RightForeArm',(153,102,0)),('RightForeArm','RightHand',(153,153,0)),
       ('LeftArm','LeftForeArm',(102,153,0)),('LeftForeArm','LeftHand',(51,153,0)),
       ('Neck1','RightUpLeg',(0,153,0)),('RightUpLeg','RightLeg',(0,153,51)),
       ('RightLeg','RightFoot',(0,153,102)),('Neck1','LeftUpLeg',(0,153,153)),
       ('LeftUpLeg','LeftLeg',(0,102,153)),('LeftLeg','LeftFoot',(0,51,153)),
       ('Neck1','Nose',(0,0,153))]

def joint_matrix(motion, name, frame, cache):
    if name in cache:
        return cache[name]
    parent = motion.joint_parent(name)
    parent_matrix = np.eye(4) if parent is None else joint_matrix(motion, parent.value[1], frame, cache)
    matrix = np.eye(4)
    matrix[:3,3] = motion.joint_offset(name)
    channels = motion.joint_channels(name)
    for channel, value in zip(channels, motion.frame_joint_channels(frame, name, channels)):
        if channel.endswith('position'):
            matrix['XYZ'.index(channel[0]),3] += value
            continue
        angle = radians(value); c, s = cos(angle), sin(angle); rot = np.eye(4)
        if channel[0] == 'X': rot[:3,:3] = [[1,0,0],[0,c,-s],[0,s,c]]
        if channel[0] == 'Y': rot[:3,:3] = [[c,0,s],[0,1,0],[-s,0,c]]
        if channel[0] == 'Z': rot[:3,:3] = [[c,-s,0],[s,c,0],[0,0,1]]
        matrix = matrix @ rot
    cache[name] = parent_matrix @ matrix
    return cache[name]

def make_poses(bvh_text, output_dir, face_offsets=None):
    motion = Bvh(bvh_text)
    if motion.nframes < 141 or abs(motion.frame_time - 1/120) > .0001:
        raise ValueError('Expected the 120 fps CMU 09_01 capture with at least 141 frames')
    output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
    for index, frame in enumerate(range(20,140,5)):
        cache={}
        pos={name:joint_matrix(motion,name,frame,cache)[:3,3]*.06 for name in JOINTS}
        root=pos['Hips']
        points={name:(round(240+240*(p[2]-root[2])),round(485-255*p[1])) for name,p in pos.items()}
        # Position the face marker on the forward side of the head rather than
        # leaving its orientation unspecified. Offsets were extracted from the
        # generated character keyframe, not the user's original photo.
        hx,hy=points['Head']; points['Nose']=(hx+38,hy-16)
        canvas=Image.new('RGB',(512,512)); draw=ImageDraw.Draw(canvas)
        for a,b,color in LIMBS: draw.line([points[a],points[b]],fill=color,width=8)
        for _,b,color in LIMBS:
            x,y=points[b]; draw.ellipse((x-4,y-4,x+4,y+4),fill=tuple(min(255,round(c/.6)) for c in color))
        if face_offsets:
            nx,ny=points['Nose']
            for dx,dy in face_offsets:
                x,y=round(nx+dx),round(ny+dy)
                if 0<=x<512 and 0<=y<512: draw.ellipse((x-1,y-1,x+1,y+1),fill=(255,255,255))
        canvas.save(output/f'frame_{index}.png')
    return 24
