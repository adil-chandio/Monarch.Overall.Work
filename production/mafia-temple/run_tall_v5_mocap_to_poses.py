"""Build research pose controls from CMU motion 09_01 (120 Hz) at 24 fps.

The root translation is removed for a tracking camera. This is an experimental
side projection, not a full camera or cloth/foot-contact simulation.
"""
from math import cos, radians, sin, atan2
from colorsys import hsv_to_rgb
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

def make_poses(bvh_text, output_dir, face_offsets=None, hand_offsets=None, frame_count=24):
    motion = Bvh(bvh_text)
    if motion.nframes < 141 or abs(motion.frame_time - 1/120) > .0001:
        raise ValueError('Expected the 120 fps CMU 09_01 capture with at least 141 frames')
    output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
    # 20..107 approximates one full running gait (120 Hz). Repeat the
    # actual recorded gait for a longer continuous tracking-camera test.
    if frame_count < 1:
        raise ValueError('frame_count must be positive')
    samples = (range(20, 140, 5) if frame_count == 24 else
               (20 + (index * 5) % 88 for index in range(frame_count)))
    for index, frame in enumerate(samples):
        cache={}
        pos={name:joint_matrix(motion,name,frame,cache)[:3,3]*.06 for name in JOINTS}
        root=pos['Hips']
        # Map the old 712px square crop into the original-image 432x768
        # portrait crop (472,0,904,768), then resize to 576x1024.
        points={name:(round((345+(240+240*(p[2]-root[2]))*712/512-472)*4/3),
                      round((30+(485-255*p[1])*712/512)*4/3)) for name,p in pos.items()}
        # Position the face marker on the forward side of the head rather than
        # leaving its orientation unspecified. Offsets were extracted from the
        # generated character keyframe, not the user's original photo.
        hx,hy=points['Head']; points['Nose']=(hx+70,hy-30)
        # Match the 82% scaled generated-character reference and leave more
        # room for the swing of the feet inside the portrait crop.
        points={name:(round(288+.82*(x-288)),round(950+.82*(y-950))) for name,(x,y) in points.items()}
        canvas=Image.new('RGB',(576,1024)); draw=ImageDraw.Draw(canvas)
        # Side-view projection collapses the two arms onto each other. Fade the
        # farther arm's control while hands overlap in screen space, instead of
        # asking the model to draw intersecting hands. Experimental only: the
        # model still must infer anatomically valid occlusion and sleeve.
        distance=float(np.linalg.norm(np.array(points['LeftHand'])-np.array(points['RightHand'])))
        far_fade=float(np.clip((distance-30)/80,0,1))
        def fade_for(joint): return far_fade if joint in ('RightForeArm','RightHand') else 1.0
        for a,b,color in LIMBS:
            fade=fade_for(b)
            draw.line([points[a],points[b]],fill=tuple(round(c*fade) for c in color),width=8)
        for _,b,color in LIMBS:
            x,y=points[b];fade=fade_for(b)
            draw.ellipse((x-4,y-4,x+4,y+4),fill=tuple(min(255,round(c/.6*fade)) for c in color))
        if face_offsets:
            nx,ny=points['Nose']
            for dx,dy in face_offsets:
                x,y=round(nx+dx*1.520),round(ny+dy*1.520)
                if 0<=x<576 and 0<=y<1024: draw.ellipse((x-1,y-1,x+1,y+1),fill=(255,255,255))
        # Experimental generated-keyframe fist landmarks, rotated with each
        # projected forearm. This is approximate 2D guidance, not actual hand
        # mocap or a guarantee that fingers are physically correct.
        if hand_offsets:
            edges = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
                     (0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),
                     (0,17),(17,18),(18,19),(19,20)]
            for side in ('Left','Right'):
                wrist=np.array(points[side+'Hand'],dtype=float)
                elbow=np.array(points[side+'ForeArm'],dtype=float)
                delta=wrist-elbow
                # Source template is oriented approximately upwards.
                angle=atan2(delta[1],delta[0])+np.pi/2
                c,s=cos(angle),sin(angle)
                # Smaller projected fingers: v1's full-size guide led to visibly
                # oversized, splayed hands. This remains only approximate.
                rotated=[(round(wrist[0]+.84*(dx*c-dy*s)),
                          round(wrist[1]+.84*(dx*s+dy*c))) for dx,dy in hand_offsets]
                for j,(a,b) in enumerate(edges):
                    fade=far_fade if side=='Right' else 1.0
                    rgb=tuple(round(255*v*fade) for v in hsv_to_rgb(j/len(edges),1,1))
                    draw.line([rotated[a],rotated[b]],fill=rgb,width=2)
                for x,y in rotated:
                    draw.ellipse((x-2,y-2,x+2,y+2),fill=(0,0,round(255*(far_fade if side=='Right' else 1))))
        canvas.save(output/f'frame_{index}.png')
    return frame_count
