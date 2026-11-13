import sys, time
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, film as F
from PIL import Image
W,H=960,540
L,R=32.0,3.4
def build(cam, mouthpow=60.0, torchpow=4.0, torchpos=(-2.0,1.4,-11.0)):
    lights=[dict(pos=[0.0,0.8,L*0.5+1.4],col=(0.42,0.60,1.00),pow=mouthpow,
                 spot_dir=(0,0,-1),spot_cos=0.10),
            dict(pos=list(torchpos),col=(1.00,0.58,0.24),pow=torchpow)]
    return lights
jobs=[('t7a',[0.2,1.3,-12.0],[0.0,1.0,L*0.5],40,70.0,3.4),
      ('t7b',[2.4,1.6,-9.0],[-0.6,0.9,3.0],38,60.0,6.0),
      ('t7c',[0.0,1.6,-4.0],[0.0,0.9,L*0.5],46,100.0,2.0)]
for name,pos,tgt,fov,mp,tp in jobs:
    cam=E.Cam(W,H,pos=pos,target=tgt,fov=fov)
    sky=F.sky(cam,W,H)
    lights=build(cam,mp,tp)
    hg=F.march_bg(cam,W,H,L,R)
    bg,depth=F.shade_bg(hg,cam,lights,L,R,sky_img=sky)
    vol=F.volumetrics(cam,W,H,L,R,lights,density=0.020)
    bear=S.bear('stand',scale=1.0)
    bear['P']=bear['P']+np.array([0.0,0.0,3.6],np.float32)
    c,d,e=E.shade_points(bear,cam,lights)
    bear['_col']=c
    sp=F.splat(bear,cam,W,H,depth)
    comp=bg*(1-sp['cov'][...,None])+sp['col']*sp['cov'][...,None]
    Image.fromarray(E.to_u8(F.grade(comp+vol*1.2,exposure=1.0,seed=1))).save('out/%s.png'%name)
    print(name,'cov',round(float(sp['cov'].mean()),3))
