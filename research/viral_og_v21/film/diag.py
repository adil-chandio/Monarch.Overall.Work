import sys; sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S
from PIL import Image
W,H=420,300
tiles=[]
def shot(nd, cam_pos, cam_tgt, fov=40, name='x'):
    cam=E.Cam(W,H,pos=cam_pos,target=cam_tgt,fov=fov)
    L=[dict(pos=list(np.asarray(cam_pos,np.float32)+np.array([1.2,1.0,1.2])),col=(1,0.96,0.92),pow=90.0)]
    img,_,_=E.render_buffer(nd,cam,L,W,H,fog=0.0)
    tiles.append((name,E.to_u8(E.finish(img,exposure=1.0,bloom_amt=0.05,streak_amt=0,grain_amt=0.0))))
b=S.bear('stand')
shot(b,[4.6,1.4,3.4],[0,1.05,0.6],40,'bear 3q')
shot(b,[0.0,1.3,5.6],[0,1.05,0.6],40,'bear front')
b2=S.bear('rear'); shot(b2,[4.2,1.8,3.6],[0,1.3,0.2],40,'rear')
b3=S.bear('walk'); shot(b3,[4.6,1.5,2.6],[0,1.0,0.0],40,'walk')
sk=S.skull(scale=6.0); shot(sk,[0.0,0.15,1.55],[0,0,0],40,'skull side')
sk2=S.skull(scale=6.0); shot(sk2,[0.55,0.28,1.15],[0,0,0.05],40,'skull 3q')
cols=3; rows=(len(tiles)+cols-1)//cols
sheet=np.zeros((rows*H,cols*W,3),np.uint8)
for i,(nm,im) in enumerate(tiles):
    r,c=divmod(i,cols); sheet[r*H:(r+1)*H,c*W:(c+1)*W]=im
Image.fromarray(sheet).save('out/diag.png'); print('ok',len(tiles))
