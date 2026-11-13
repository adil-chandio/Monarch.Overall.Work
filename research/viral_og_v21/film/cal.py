import sys
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, film as F
W,H=480,270
L,R=32.0,3.4
cam=E.Cam(W,H,pos=[0.2,1.25,-7.5],target=[0.0,1.05,L*0.5],fov=46)
sky=F.sky(cam,W,H)
def stats(a,n):
    print(n,' p50 %.4f p90 %.4f p99 %.4f max %.3f'%(np.percentile(a,50),np.percentile(a,90),np.percentile(a,99),a.max()))
hg=F.march_bg(cam,W,H,L,R,steps=36)
for mp in (0.6,1.6,4.0):
    for tp in (2.0,6.0,14.0):
        lights=[dict(kind='portal',pos=[0,0.9,L*0.5+2],col=(0.44,0.62,1.0),pow=mp,spot_dir=(0,0,-1),spot_cos=0.0),
                dict(pos=[-2.6,1.2,-6.0],col=(1.0,0.56,0.22),pow=tp)]
        bg,depth=F.shade_bg(hg,cam,lights,L,R,sky_img=sky)
        print('mp',mp,'tp',tp,end='  '); stats(bg.mean(2),'bg')
lights=[dict(kind='portal',pos=[0,0.9,L*0.5+2],col=(0.44,0.62,1.0),pow=1.6,spot_dir=(0,0,-1),spot_cos=0.0),
        dict(pos=[-2.6,1.2,-6.0],col=(1.0,0.56,0.22),pow=6.0)]
v=F.volumetrics(cam,W,H,L,R,lights,density=0.020)
stats(v.mean(2),'vol d=0.020')
v2=F.volumetrics(cam,W,H,L,R,lights,density=0.006)
stats(v2.mean(2),'vol d=0.006')
