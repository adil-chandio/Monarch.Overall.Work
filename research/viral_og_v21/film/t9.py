import sys
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, film as F
from PIL import Image
W,H=960,540
L,R=32.0,3.4
def frame(name,pos,tgt,fov,mouth=1.6,torch=14.0,tpos=(-2.4,1.5,-10.0),bear=None,expose=1.0,vol=2.2):
    cam=E.Cam(W,H,pos=pos,target=tgt,fov=fov)
    sky=F.sky(cam,W,H)
    lights=[dict(kind='portal',pos=[0.0,0.9,L*0.5+2.0],col=(0.44,0.62,1.00),pow=mouth,
                 spot_dir=(0,0,-1),spot_cos=0.0),
            dict(pos=list(tpos),col=(1.00,0.56,0.22),pow=torch)]
    hg=F.march_bg(cam,W,H,L,R)
    bg,depth=F.shade_bg(hg,cam,lights,L,R,sky_img=sky)
    img=bg
    if bear is not None:
        b=S.bear(bear[0],scale=1.0)
        b['P']=b['P']+np.array([bear[1],0.0,bear[2]],np.float32)
        c,d,e=E.shade_points(b,cam,lights); b['_col']=c
        sp=F.splat(b,cam,W,H,depth,cone=hg['cone_r'])
        img=bg*(1-sp['cov'][...,None])+sp['col']*sp['cov'][...,None]
        print(name,'cov',round(float(sp['cov'].mean()),3))
    v=F.volumetrics(cam,W,H,L,R,lights,density=0.020)
    out=F.grade(img+v*vol,exposure=expose,seed=7)
    Image.fromarray(E.to_u8(out)).save('out/%s.png'%name)
    print(name,'bg',round(float(bg.mean()),3))
frame('t9a',[0.2,1.25,-7.5],[0.0,1.05,L*0.5],46,1.6,16.0,(-2.6,1.2,-6.0),('stand',0.0,3.2))
frame('t9b',[0.0,1.15,-3.6],[0.0,1.05,L*0.5],54,2.2,10.0,(-2.0,1.0,-3.2),('rear',0.0,1.4))
