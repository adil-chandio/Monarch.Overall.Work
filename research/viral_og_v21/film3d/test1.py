import sys, time
sys.path.insert(0,'.')
import numpy as np, geo3d as G, render3d as R, film1min as F
from PIL import Image
W,H=480,270
cave,shots=F.film()
s=shots[2]
eye,tgt,fov,lts,act=s.sample(4.0)
print('eye',eye,'tgt',tgt,'fov',fov)
cam=R.Cam(W,H,eye,tgt,fov=fov)
lights=[R.Light(p,c,pw,kind=k) for (p,c,pw,k) in lts]
t0=time.time(); hg=R.march_set(cam,cave,W,H); print('march',round(time.time()-t0,2))
t0=time.time(); bg,depth=R.shade_set(hg,cam,cave,lights); print('shade',round(time.time()-t0,2))
nd=G.bear(0.0,pose=0.0,walk=0.0)
nd['P']=nd['P']+np.array([0,0,3.4],np.float32)
t0=time.time(); col=R.shade_points(nd,cam,lights,cave,amb=0.02); print('chars',round(time.time()-t0,2))
sp=R.splat(nd,cam,W,H,depth,col)
img=bg*(1-sp['cov'][...,None])+sp['col']*sp['cov'][...,None]
out=R.finish(img,seed=1)
Image.fromarray((out*255).astype(np.uint8)).save('out3d_test.png')
print('cov',round(float(sp['cov'].mean()),3),'bgmean',round(float(bg.mean()),4))
