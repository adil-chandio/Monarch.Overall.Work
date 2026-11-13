"""Render one still from a shot so a look can be judged before the whole cut."""
from __future__ import annotations

import argparse
import sys
import time

import numpy as np
from PIL import Image

from . import engine, geom, world


def render_still(set_name, eye, target, fov, w, h, *, fog=0.05,
                 fog_tint=(0.055, 0.075, 0.115), ambient=(0.045, 0.055, 0.085),
                 mist=0.35, exposure=1.0, contrast=1.16, saturation=1.10,
                 streak=0.22, vignette=0.42, grain=0.010, seed=0,
                 wet=0.42, moon=None, moon_size=1.0, time=0.0,
                 dyn_fn=None, shadow_scale=5):
    frame = engine.Frame(set_name, w, h)
    rd, ro, right, up = geom.camera_rays(w, h, eye, target, fov_deg=fov)
    ty = float(np.tan(np.radians(fov) * 0.5))
    cam = (np.asarray(eye, np.float32), right, up, ty, w / h)
    fwd = geom.normalise(np.asarray(target, np.float32) - np.asarray(eye, np.float32))
    cam = (np.asarray(eye, np.float32), fwd, right, up, ty, w / h)

    dyn = None
    if dyn_fn is not None:
        dyn = engine._flatten(dyn_fn())

    t, mat, nrm = frame.trace(ro, rd, dyn=dyn, cam=cam)
    col, hit, dist = frame.shade(ro, rd, t, mat, nrm, frame.lights, fog,
                                 fog_tint, ambient, mist=mist, time=time,
                                 )
    # sky behind
    skym = ~hit
    if skym.any():
        col[skym] = frame.sky(rd[skym], fog_tint, moon, moon_size, time)
    col = frame.wet(col, ro, rd, t, mat, nrm, frame.lights, fog_tint,
                    strength=wet, time=time)
    col = frame.mist_layer(col, hit, t, rd, strength=mist)
    return col, frame


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', default='face')
    ap.add_argument('--eye', default='0,1.62,0.64')
    ap.add_argument('--target', default='0,1.60,0')
    ap.add_argument('--fov', type=float, default=30.0)
    ap.add_argument('--size', default='480x270')
    ap.add_argument('--out', default='/tmp/still.png')
    ap.add_argument('--exposure', type=float, default=1.0)
    ap.add_argument('--contrast', type=float, default=1.16)
    ap.add_argument('--saturation', type=float, default=1.10)
    ap.add_argument('--fog', type=float, default=0.05)
    a = ap.parse_args(argv)
    w, h = (int(x) for x in a.size.split('x'))
    eye = [float(x) for x in a.eye.split(',')]
    tgt = [float(x) for x in a.target.split(',')]
    t0 = time.time()
    col, _f = render_still(a.set, eye, tgt, a.fov, w, h, fog=a.fog,
                           exposure=a.exposure, contrast=a.contrast,
                           saturation=a.saturation)
    img = engine.Frame.grade(col, exposure=a.exposure, contrast=a.contrast,
                             saturation=a.saturation)
    Image.fromarray(img).save(a.out)
    print(f'{a.out} {w}x{h} in {time.time()-t0:.1f}s '
          f'luma={img.mean():.1f}')


if __name__ == '__main__':
    sys.exit(main())
