import sys, time
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, lighting as LG
from PIL import Image
W,H=960,540
cave=S.cave(length=30, radius=3.6, density=1.0)
bear=S.bear('walk',scale=1.0)
allpts=E.merge([cave['walls'],cave['floor'],bear])
mouth=cave['mouth']
cam=E.Cam(W,H,pos=[0.9,1.0,-4.6],target=[-0.1,1.15,mouth[2]],fov=42)
plate=S.sky_plate(cam,W,H)
L=[LG.rig_mouth(mouth,power=26.0,length=30,radius=3.6),
   LG.rig_torch([-1.5,1.0,-5.2],power=1.1,length=30,radius=3.6)]
vis=LG.apply_visibility(allpts,L,30,3.6)
t=time.time()
img,depth,em=E.render_buffer(allpts,cam,L,W,H,vis=vis,fog=0.026,bg=plate)
print('render',round(time.time()-t,2))
vol=E.volumetric(cam,W,H,dict(density=0.012,height=4.0,ground_y=-2.8,col=(0.004,0.007,0.014)),L,res=(0.2,0.2))
fin=E.finish(img+vol*1.0,exposure=0.85,bloom_amt=0.22,streak_amt=0.14)
Image.fromarray(E.to_u8(fin)).save('out/test4.png')
print('mean',img.mean(),'max',img.max())
