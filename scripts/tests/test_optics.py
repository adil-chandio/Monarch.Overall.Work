"""The two optics bugs that made v3 a smear, as regression tests.

Neither of these threw. The film rendered, encoded, passed its audio gates and
uploaded. It just looked like a blurred teal rectangle with black blobs drifting
through it, and the cause was two independent mistakes in the same subsystem.

1. linear_depth() inverted a different projection than the one draw() used.
   perspective() here sets w=+z and stores d=(z-near)/(z*(far-near)) with
   far=200. linear_depth() applied the OpenGL [-1,1] inverse with hard-coded
   near=0.05, far=400. A body 10 m from the camera reported 0.100 m, a factor
   of 100. Every post effect that reads depth - fog, CoC, the god-ray near
   mask, caustic falloff - was driven by that number.

2. depth_of_field() normalised its circle of confusion by the focus distance and
   clipped it to 1. With a focus of 9 m and strength 4, everything past 18 m was
   fully blurred, and the subjects sit at 10-30 m. Combined with (1), every pixel
   in every frame got the widest kernel.

Run:  .venv/bin/python scripts/tests/test_optics.py
"""
import sys, numpy as np
sys.path.insert(0, "/home/user/Monarch.Overall.Work")
from scripts.lib.tri3d import Renderer, ellipse_ring, tube

fail = 0

# 1. linear_depth must invert the projection for the ACTUAL near/far planes.
#    v3 inverted a [-1,1] OpenGL projection with hard-coded 0.05/400 while
#    perspective() used [0,1] and 200, so a body at 10 m measured 0.100 m.
r = Renderer(64, 36, ssaa=1)
for truth in (3.0, 10.0, 40.0, 120.0):
    rad = max(0.6, truth * 0.03)
    sph = tube([ellipse_ring((0, 0, z), rad, rad, 24) for z in np.linspace(-rad, rad, 12)],
               (200, 50, 50), "skin")
    sph.v = sph.v + np.array([0, 0, truth], dtype=np.float32)
    r.set_camera(np.array([0., 0., 0.]), np.array([0., 0., 1.]), fov=40)
    r.draw(sph)
    got = float(r.linear_depth()[18, 32])
    err = abs(got - truth) / truth
    # sampled on the sphere's front face, which is `rad` nearer than its centre
    tol = 0.02 + rad / truth
    ok = err <= tol
    print(f"  {'ok  ' if ok else 'FAIL'} depth {truth:6.1f} m -> {got:8.2f} m (err {err*100:5.1f}%, tol {tol*100:.0f}%)")
    fail += not ok

# 2. a focused subject must stay sharp: DOF has to be selective, not global.
#    v3 saturated the CoC on every pixel and blurred the entire film.
def sharpness(im):
    a = im.mean(axis=2)
    return float(np.abs(4*a[1:-1,1:-1]-a[:-2,1:-1]-a[2:,1:-1]-a[1:-1,:-2]-a[1:-1,2:]).mean())

r2 = Renderer(320, 180, ssaa=1)
r2.set_camera(np.array([0., 0., -6.]), np.array([0., 0., 3.]), fov=46)
for x in (-2.4, 0.0, 2.4):
    sph = tube([ellipse_ring((0, 0, z), 0.9, 0.9, 20) for z in np.linspace(-0.9, 0.9, 10)],
               (190, 190, 190), "skin")
    sph.v = sph.v + np.array([x, 0, 3.0], dtype=np.float32)
    r2.draw(sph)
im = r2.resolve().copy()
focused = r2.depth_of_field(im, 9.0, 1.0)
blurred = r2.depth_of_field(im, 0.2, 1.0)     # focus nothing that is on screen
s_f, s_b = sharpness(focused), sharpness(blurred)
ratio = s_f / max(1e-6, s_b)
ok = s_f > s_b and ratio > 1.05
print(f"  {'ok  ' if ok else 'FAIL'} DOF selective: focused={s_f:.4f} defocused={s_b:.4f} "
      f"ratio={ratio:.2f} (must be >1.05)")
fail += not ok

print("\nFAIL" if fail else "\nPASS  depth inverse + selective DOF")
sys.exit(1 if fail else 0)
