import sys, time, math
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, lighting as LG
from PIL import Image
W,H = 960,540
cave = S.cave(length=30, radius=3.6, density=1.0)
bear = S.bear('stand', scale=1.0)
tip = S.skull(scale=1.0); tip['P'] = tip['P'] + np.array([0.0,0.62,1.2],np.float32)
allpts = E.merge([cave['walls'], cave['floor'], bear, tip])
mouth = cave['mouth']
L = [LG.rig_mouth(mouth, power=140.0, length=30.0, radius=3.6),
     LG.rig_torch([-1.2, 0.9, -5.6], power=9.0, length=30.0, radius=3.6)]
t=time.time()
vis = LG.apply_visibility(allpts, L, 30.0, 3.6)
print('vis', round(time.time()-t,2))
cam = E.Cam(W,H, pos=[0.5,0.6,-6.2], target=[0.0,1.0,mouth[2]], fov=44)
img,depth,em = E.render_buffer(allpts, cam, L, W, H, vis=vis, fog=0.030)
vol = E.volumetric(E.Cam(W,H,pos=[0.5,0.6,-6.2],target=[0.0,1.0,mouth[2]],fov=44), W,H,
                   dict(density=0.016, height=3.6, ground_y=-2.6, col=(0.004,0.007,0.012)), L, res=(0.20,0.20))
fin = E.finish(img + vol*1.2, frame_seed=3, exposure=1.5)
Image.fromarray(E.to_u8(fin)).save('out/test2.png')
print('ok')
