import sys, time
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, film as F, lighting as LG
from PIL import Image
W,H=960,540
L=30.0; R=3.6
cam=E.Cam(W,H,pos=[0.9,1.05,-4.4],target=[-0.1,1.15,L*0.5],fov=42)
t=time.time(); hg=F.march_bg(cam,W,H,L,R); print('march',round(time.time()-t,2))
sky=F.sky(cam,W,H)
lights=[dict(pos=[0.0,0.9,L*0.5-1.2],col=(0.42,0.60,1.00),pow=95.0),
        dict(pos=[-1.6,1.0,-5.2],col=(1.00,0.58,0.24),pow=1.9)]
t=time.time(); bg,depth=F.shade_bg(hg,cam,lights,L,R,sky_img=sky); print('shade_bg',round(time.time()-t,2))
# hero: bear as silhouette between camera and mouth
bear=S.bear('walk',scale=1.0)
bear['P']=bear['P']+np.array([0.0,0.0,2.2],np.float32)
col,dist,em=E.shade_points(bear,cam,lights,vis=None)
bear['_col']=col*0.9
t=time.time(); sp=F.splat(bear,cam,W,H,depth); print('splat',round(time.time()-t,2))
comp=bg*(1-sp['cov'][...,None])+sp['col']*sp['cov'][...,None]
fin=F.grade(comp,exposure=1.0)
Image.fromarray(E.to_u8(fin)).save('out/t5.png')
print('cov mean',sp['cov'].mean())
