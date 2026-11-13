import sys
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, film as F
from PIL import Image
W,H=960,540
L,R=32.0,3.4
def frame(name,pos,tgt,fov,mp=26.0,tp=2.6,tpos=(-2.4,1.5,-10.0),bear_z=4.0,bear_pose='stand',bear_dx=0.0,expose=1.0):
    cam=E.Cam(W,H,pos=pos,target=tgt,fov=fov)
    sky=F.sky(cam,W,H)
    lights=[dict(pos=[0.0,0.9,L*0.5+2.2],col=(0.40,0.58,1.00),pow=mp,spot_dir=(0,0,-1),spot_cos=0.05),
            dict(pos=list(tpos),col=(1.00,0.56,0.22),pow=tp)]
    hg=F.march_bg(cam,W,H,L,R)
    bg,depth=F.shade_bg(hg,cam,lights,L,R,sky_img=sky)
    bear=S.bear(bear_pose,scale=1.0)
    bear['P']=bear['P']+np.array([bear_dx,0.0,bear_z],np.float32)
    c,d,e=E.shade_points(bear,cam,lights)
    bear['_col']=c
    sp=F.splat(bear,cam,W,H,depth,cone=hg['cone_r'])
    comp=bg*(1-sp['cov'][...,None])+sp['col']*sp['cov'][...,None]
    vol=F.volumetrics(cam,W,H,L,R,lights,density=0.024)
    Image.fromarray(E.to_u8(F.grade(comp+vol*1.4,exposure=expose,seed=5))).save('out/%s.png'%name)
    print(name,'cov',round(float(sp['cov'].mean()),3), 'bgmean', round(float(bg.mean()),4))
frame('t8a',[0.2,1.25,-7.5],[0.0,1.05,L*0.5],46,30,2.4,(-2.6,1.2,-6.0),3.2,'stand')
frame('t8b',[0.0,1.15,-4.2],[0.0,1.05,L*0.5],52,40,2.0,(-2.2,1.0,-4.0),1.8,'rear')
frame('t8c',[1.2,1.4,-9.0],[-0.3,1.0,2.0],40,30,3.0,(-2.8,1.4,-8.0),5.0,'walk')
