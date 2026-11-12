"""Experimental 2-D retarget of CMU 35_17 onto a public generated still.

Pose-only output has no texture or stock video. Uses the repeated nearest-pose
source loop 35..124 at 120 Hz, sampled at 24 fps. Constant per-bone 2D
similarity transforms preserve the start-frame joint fit, but may distort
anatomy under changing 3D occlusion; there is no contact solver. Inspect every
frame and do not treat this as verified movement or a final shot.
"""
import hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
from bvh import Bvh
import numpy as np
import run_tall_v5_mocap_to_poses as p

SHA='50c6469efea1edbba0f7acd46b1fa72e0b74b78e1698aa1b441990bd2a78d730'
# Approximate MediaPipe positions from the previously-public generated image,
# rescaled to 832x448; these are not the user's original photograph.
TARGET={'Nose':(458,88),'Neck1':(430,108),'LeftArm':(392,115),'LeftForeArm':(342,156),'LeftHand':(341,205),
 'RightArm':(461,125),'RightForeArm':(470,183),'RightHand':(490,172),
 'LeftUpLeg':(396,227),'LeftLeg':(444,298),'LeftFoot':(456,393),'LeftToeBase':(498,394),
 'RightUpLeg':(420,231),'RightLeg':(380,309),'RightFoot':(316,353),'RightToeBase':(322,392)}
PARENTS={'LeftForeArm':'LeftArm','LeftHand':'LeftForeArm','RightForeArm':'RightArm','RightHand':'RightForeArm',
 'LeftLeg':'LeftUpLeg','LeftFoot':'LeftLeg','LeftToeBase':'LeftFoot',
 'RightLeg':'RightUpLeg','RightFoot':'RightLeg','RightToeBase':'RightFoot','Nose':'Neck1'}
ANCHORS=('Neck1','LeftArm','RightArm','LeftUpLeg','RightUpLeg')

def project(m,frame):
 c={};pos={j:p.joint_matrix(m,j,frame,c)[:3,3]*.06 for j in p.JOINTS};root=pos['Hips']
 pts={n:np.array(((345+(240+240*(v[2]-root[2]))*712/512-472)*4/3,(30+(485-255*v[1])*712/512)*4/3)) for n,v in pos.items()}
 h=pts['Head'];pts['Nose']=h+np.array((70,-30))
 return {n:np.array((288+.82*(v[0]-288),950+.82*(v[1]-950))) for n,v in pts.items()}

def build(source,dest):
 data=Path(source).read_bytes()
 if hashlib.sha256(data).hexdigest()!=SHA:raise ValueError('Unexpected mocap source')
 m=Bvh(data.decode());assert m.nframes>=126 and abs(m.frame_time-1/120)<.0001
 base=project(m,35);target={k:np.array(v,dtype=float) for k,v in TARGET.items()};factors={}
 for child,parent in PARENTS.items():
  a=complex(*(base[child]-base[parent]));b=complex(*(target[child]-target[parent]));
  if abs(a)<1:raise ValueError('Unstable projected bone')
  factors[child]=b/a
 atlas=Image.new('RGB',(8*832,10*448))
 for i in range(73):
  raw=project(m,35+(5*i)%90);pts={n:target[n]+(raw[n]-base[n])*.45 for n in ANCHORS}
  for child,parent in PARENTS.items():
   vec=complex(*(raw[child]-raw[parent]))*factors[child];pts[child]=pts[parent]+np.array((vec.real,vec.imag))
  pts={k:tuple(np.rint(v).astype(int)) for k,v in pts.items()}
  canvas=Image.new('RGB',(832,448));d=ImageDraw.Draw(canvas)
  for a,b,col in p.LIMBS:d.line([pts[a],pts[b]],fill=col,width=6)
  for _,b,col in p.LIMBS:
   x,y=pts[b];d.ellipse((x-3,y-3,x+3,y+3),fill=tuple(min(255,round(c/.6)) for c in col))
  atlas.paste(canvas,((i%8)*832,(i//8)*448))
 atlas.save(dest,optimize=True);print('73-frame retargeted research guide created')
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('usage: make_cmu_wide_retarget.py source.bvh output.png')
 build(*sys.argv[1:])
