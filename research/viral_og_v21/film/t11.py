import sys
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, film as F
from PIL import Image
W,H=960,540
def frame(name,cam_pos,tgt,fov,L,R,mp,tp,tpos,bear=None,vd=0.005,expose=None,seed=7,torch_dz=0):
    cam=E.Cam(W,H,pos=cam_pos,target=tgt,fov=fov)
    sky=F.sky(cam,W,H)
    lights=[dict(kind='portal',pos=[0,0.9,L*0.5+1.2],col=(0.46,0.64,1.00),pow=mp),
            dict(pos=list(tpos),col=(1.00,0.56,0.22),pow=tp)]
    hg=F.march_bg(cam,W,H,L,R,steps=int(max(40, L*1.6)), tmax=L*1.5)
    bg,depth=F.shade_bg(hg,cam,lights,L,R,sky_img=sky)
    img=bg
    if bear:
        b=S.bear(bear[0],scale=bear[3]); b['P']=b['P']+np.array([bear[1],0.0,bear[2]],np.float32)
        c,d,e=E.shade_points(b,cam,lights); b['_col']=c
        sp=F.splat(b,cam,W,H,depth,cone=hg['cone_r'])
        img=bg*(1-sp['cov'][...,None])+sp['col']*sp['cov'][...,None]
        print(name,'cov',round(float(sp['cov'].mean()),3))
    v=F.volumetrics(cam,W,H,L,R,lights,density=vd,res=0.22,steps=30)
    lin=img+v*1.4
    ex=expose if expose else F.auto_exposure(lin)
    print(name,'ex',round(ex,2),'p50',round(float(np.percentile(lin.mean(2),50)),4))
    Image.fromarray(E.to_u8(F.grade(lin,exposure=ex,seed=seed))).save('out/%s.png'%name)
frame('uA',[0.3,1.25,-13.0],[0.0,1.0,22.0],42,44.0,2.3,3.0,9.0,(-2.0,1.2,-11.0),('stand',0.0,6.0,1.0))
frame('uB',[0.0,1.05,-8.0],[0.0,1.05,22.0],50,44.0,2.3,6.0,7.0,(-1.6,1.0,-6.0),('rear',0.0,2.6,1.0))
frame('uC',[1.2,1.5,-16.0],[-0.5,0.9,10.0],36,44.0,2.3,2.2,12.0,(-2.4,1.5,-14.5),('walk',0.3,4.0,1.0))
