import sys, time
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, lighting as LG
from PIL import Image
W,H=960,540
cave=S.cave(length=30, radius=3.6, density=1.0)
bear=S.bear('stand',scale=1.0)
allpts=E.merge([cave['walls'],cave['floor'],bear])
mouth=cave['mouth']
L=[LG.rig_mouth(mouth,power=9.0,length=30,radius=3.6),
   LG.rig_torch([-1.3,1.0,-5.4],power=0.35,length=30,radius=3.6)]
vis=LG.apply_visibility(allpts,L,30,3.6)
cam=E.Cam(W,H,pos=[0.6,0.75,-6.4],target=[0.0,1.05,mouth[2]],fov=44)
t=time.time()
img,depth,em=E.render_buffer(allpts,cam,L,W,H,vis=vis,fog=0.030)
print('render',round(time.time()-t,2))
Image.fromarray(E.to_u8(E.finish(img,exposure=1.0,bloom_amt=0.18,streak_amt=0.12))).save('out/test3_clean.png')
print('ok', img.max(), img.mean())
