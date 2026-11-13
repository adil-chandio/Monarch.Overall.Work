import sys, time
sys.path.insert(0,'.')
import numpy as np, geo3d as G, render3d as R, film1min as F
from PIL import Image
W,H=960,540
cave,shots=F.film()
tiles=[]
def shot(idx, u, name):
    s=shots[idx]
    eye,tgt,fov,lts,act=s.sample(u*s.dur)
    cam=R.Cam(W,H,eye,tgt,fov=fov)
    lights=[R.Light(p,c,pw,kind=k) for (p,c,pw,k) in lts]
    hg=R.march_set(cam,cave,W,H)
    bg,depth=R.shade_set(hg,cam,cave,lights)
    img=bg
    # characters
    if act['kind']=='bear':
        nd=G.bear(0.0,pose=act.get('pose',0),walk=act.get('walk',0),phase=act.get('phase',0),
                  head_yaw=act.get('yaw',0),breathe=act.get('breath',0))
        nd['P']=nd['P']+np.asarray(act['pos'],np.float32)
    elif act['kind']=='skull':
        nd=G.skull(scale=act.get('scale',1.0))
        nd['P']=nd['P']+np.asarray(act['pos'],np.float32)
        # rock under the skull
        rk=G.rocks((0,-0.12,0.0), n=420, radius=0.30)
        colr=R.shade_points(rk,cam,lights,cave,amb=0.01)
        spr=R.splat(rk,cam,W,H,depth,colr)
        img=img*(1-spr['cov'][...,None])+spr['col']*spr['cov'][...,None]
    else:
        nd=None
    if nd is not None:
        col=R.shade_points(nd,cam,lights,cave,amb=0.02)
        sp=R.splat(nd,cam,W,H,depth,col)
        img=img*(1-sp['cov'][...,None])+sp['col']*sp['cov'][...,None]
    vol=R.volumetrics(cam,cave,lights,W,H,density=0.020,res=0.30)
    out=R.finish(img+vol*1.6,seed=int(u*97))
    print(name,'bgmean %.4f'%bg.mean(),'max %.2f'%img.max())
    tiles.append((name,(out*255).astype(np.uint8)))
shot(0,0.4,'s1 skull')
shot(2,0.5,'s3 bear')
shot(3,0.7,'s4 rear')
shot(5,0.4,'s6 walk')
cols=2; rows=2
sheet=np.zeros((rows*H,cols*W,3),np.uint8)
for i,(n,im) in enumerate(tiles):
    r,c=divmod(i,cols); sheet[r*H:(r+1)*H, c*W:(c+1)*W]=im
Image.fromarray(sheet).save('out3d_sheet.png')
