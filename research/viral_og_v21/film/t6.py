import sys, time
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, film as F
from PIL import Image
W,H=960,540
L,R=30.0,3.6
def shot(pos,tgt,fov,name,expose=1.0,power=120.0,bump=1.0):
    cam=E.Cam(W,H,pos=pos,target=tgt,fov=fov)
    sky=F.sky(cam,W,H)
    lights=[dict(pos=[0.0,0.6,L*0.5-1.0],col=(0.40,0.58,1.00),pow=power),
            dict(pos=[-2.2,1.2,-8.0],col=(1.00,0.56,0.22),pow=3.2)]
    hg=F.march_bg(cam,W,H,L,R)
    bg,depth=F.shade_bg(hg,cam,lights,L,R,sky_img=sky,bump=bump)
    vol=F.volumetrics(cam,W,H,L,R,lights,density=0.016)
    img=bg+vol*1.1
    Image.fromarray(E.to_u8(F.grade(img,exposure=expose,seed=3))).save('out/%s.png'%name)
    return bg
shot([0.0,1.2,-9.5],[0.0,1.0,L*0.5],44,'t6a',1.0,130)
shot([1.6,1.5,-11.0],[-0.4,1.0,4.0],40,'t6b',1.0,150)
print('ok')
