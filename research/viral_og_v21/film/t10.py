import sys
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, film as F
from PIL import Image
W,H=960,540
L,R=32.0,3.4
def frame(name,cam_pos,tgt,fov,mp=1500.0,tp=26.0,tpos=(-2.6,1.2,-6.0),bear=None,vd=0.006,seed=7,sky_bright=1.0):
    cam=E.Cam(W,H,pos=cam_pos,target=tgt,fov=fov)
    sky=F.sky(cam,W,H)*sky_bright
    lights=[dict(kind='portal',pos=[0,0.9,L*0.5+1.5],col=(0.46,0.64,1.00),pow=mp),
            dict(pos=list(tpos),col=(1.00,0.56,0.22),pow=tp)]
    hg=F.march_bg(cam,W,H,L,R)
    bg,depth=F.shade_bg(hg,cam,lights,L,R,sky_img=sky)
    img=bg
    if bear:
        b=S.bear(bear[0],scale=bear[3]); b['P']=b['P']+np.array([bear[1],0.0,bear[2]],np.float32)
        c,d,e=E.shade_points(b,cam,lights); b['_col']=c
        sp=F.splat(b,cam,W,H,depth,cone=hg['cone_r'])
        img=bg*(1-sp['cov'][...,None])+sp['col']*sp['cov'][...,None]
    v=F.volumetrics(cam,W,H,L,R,lights,density=vd)
    lin=img+v*1.5
    ex=F.auto_exposure(lin)
    print(name,'exposure',round(ex,2),'p50lin',round(float(np.percentile(lin.mean(2),50)),4))
    Image.fromarray(E.to_u8(F.grade(lin,exposure=ex,seed=seed))).save('out/%s.png'%name)
frame('tA',[0.2,1.25,-7.5],[0.0,1.05,L*0.5],46,4.6,11,(-2.6,1.2,-6.0),('stand',0.0,3.4,1.0))
frame('tB',[0.0,1.10,-3.4],[0.0,1.05,L*0.5],54,7.4,8,(-2.2,1.0,-3.0),('rear',0.0,1.5,1.0))
frame('tC',[1.1,1.45,-9.5],[-0.4,1.0,3.0],40,4.6,13,(-2.9,1.5,-9.0),('walk',0.2,6.0,1.0))
