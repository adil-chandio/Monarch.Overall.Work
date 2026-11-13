import sys, time, math
sys.path.insert(0,'.')
import numpy as np
import engine as E, scenes as S
from PIL import Image

DENS = float(len(sys.argv[1]) and sys.argv[1] or 1.0)
W,H = 960,540
t0=time.time()
cave = S.cave(length=30, radius=3.6, density=DENS)
bear = S.bear('stand', scale=1.0, detail=1.0)
# place bear: 4.5m in front, on the floor
bp = bear['P'].copy()
bp[:,2] += 0.0; bp[:,0] += 0.0; bp[:,1] += 0.0
bear['P'] = bp
skull = S.skull(scale=1.0)
skull['P'] = skull['P'] + np.array([0.0, 0.62, 1.2], np.float32)
t1=time.time()

allpts = E.merge([cave['walls'], cave['floor'], bear, skull])
print('geom', round(t1-t0,2),'s  points', allpts['P'].shape[0])

# camera: inside cave looking at mouth, bear between us and mouth (backlit silhouette)
mouth = cave['mouth']
cam = E.Cam(W,H, pos=[0.6, 0.55, -6.0], target=[-0.2, 1.05, mouth[2]], fov=46)
t2=time.time()
# lights: cool skylight from the mouth (backlight), warm torch near camera
lights = [
  dict(pos=[0.0, 0.9, mouth[2]-1.0], col=(0.62,0.76,1.00), pow=340.0, cut=10.0, shadow=True),
  dict(pos=[-1.4, 1.0, -7.2], col=(1.00,0.55,0.20), pow=3.2),
]
img,depth,em = E.render_buffer(allpts, cam, lights, W, H, fog=0.030)
t3=time.time()
cam2 = E.Cam(W,H, pos=[0.6, 0.55, -6.0], target=[-0.2, 1.05, mouth[2]], fov=46)
vol = E.volumetric(cam2, W, H, dict(density=0.020, height=3.4, ground_y=-2.4, col=(0.006,0.010,0.016)), lights, res=(0.22,0.22))
t4=time.time()
fin = E.finish(img*0.9 + vol*1.0, frame_seed=1)
t5=time.time()
print(f'shade {t3-t2:.2f}s  vol {t4-t3:.2f}s  post {t5-t4:.2f}s  total {t5-t0:.2f}s')
Image.fromarray(E.to_u8(fin)).save('out/test_%s.png'%sys.argv[1])
print('saved')
