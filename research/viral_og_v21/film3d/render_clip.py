#!/usr/bin/env python3
"""Render a time range of the 60 s film as real 3D frames -> mp4."""
import sys, os, json, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import geo3d as G, render3d as R, sdf as S, film1min as F
from PIL import Image, ImageDraw, ImageFont

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def draw_text(img, txt, pos="low"):
    if not txt: return img
    d = ImageDraw.Draw(img); H = img.height
    f = font(max(16, H // 22))
    tw = d.textlength(txt, font=f)
    y = {"low": H - int(H * 0.18), "mid": H // 2}[pos]
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text(((img.width - tw) / 2 + ox, y + oy), txt, font=f, fill=(0, 0, 0))
    d.text(((img.width - tw) / 2, y), txt, font=f, fill=(235, 233, 229))
    return img

_PARTICLES = {}


def _particles():
    if "dust" not in _PARTICLES:
        _PARTICLES["dust"] = G.Dust(n=900)
        _PARTICLES["flame"] = G.Flame(150, seed=31)
        _PARTICLES["t"] = 0.0
    return _PARTICLES


def _advance_to(T):
    P = _particles()
    while P["t"] < T - 1e-6:
        P["dust"].step(1.0 / 24.0, P["t"])
        P["t"] += 1.0 / 24.0


def _mats(nd, kind):
    n = len(nd["P"])
    m = dict(C=nd["C"], S=nd["S"], R=nd["R"], amb=nd.get("amb", np.full(n, 0.02, np.float32)))
    return m


def kind_hint(act):
    """Only shots with no subject look out of the mouth, so only they get sky."""
    return act.get("kind") == "none"


def build_frame(T, W, H, cave, shots, starts, seed=0):
    """One fully shaded 3D frame at film time T: cave raymarch, then solid props,
    then deferred-shaded air, then post."""
    k = max(j for j, st in enumerate(starts) if st <= T + 1e-6)
    local = T - starts[k]
    s = shots[k]
    eye, tgt, fov, lts, act, exp = s.sample(local)
    cam = R.Cam(W, H, eye, tgt, fov=fov)
    lights = [R.Light(a, b, c, kind=d) for (a, b, c, d) in lts]
    _advance_to(T)

    hg = R.march_set(cam, cave, W, H, steps=44)
    img, depth, tr = R.shade_set(hg, cam, cave, lights,
                                  sky=(0.052, 0.088, 0.172) if kind_hint(act) else None)

    kind = act.get("kind")
    objs, mats = [], []
    if kind == "skull":
        b = act.get("boulder")
        if b:
            objs.append(S.Boulder(b["centre"], b["radii"]))
            mats.append(dict(C=np.array([0.145, 0.136, 0.120], np.float32),
                             S=0.09, R=0.88, amb=0.02, rim=0.30))
        objs.append(S.Skull(act["pos"], act.get("rot", 0.0), act.get("scale", 1.0)))
        mats.append(dict(C=np.array([0.46, 0.415, 0.335], np.float32),
                         S=0.24, R=0.52, amb=0.035, rim=0.55))
    elif kind == "bear":
        objs.append(S.Bear(act["pos"], act.get("yaw", 0.0), fur=1.0,
                           pose=act.get("pose", 0.0), walk=act.get("walk", 0.0),
                           phase=act.get("phase", 0.0), breathe=act.get("breath", 0.0)))
        mats.append(dict(C=np.array([0.085, 0.062, 0.045], np.float32),
                         S=0.16, R=0.62, amb=0.02, rim=0.85))
    tb = act.get("torch")
    if tb:
        objs.append(S.Torch(tb))
        mats.append(dict(C=np.array([0.055, 0.040, 0.028], np.float32),
                         S=0.08, R=0.85, amb=0.02, rim=0.3))

    if objs:
        hit = R.march_objects(cam, objs, W, H, depth, steps=44)
        if hit is not None:
            # the air (flame, dust) has to be occluded by the solids, not drawn on top
            depth.reshape(-1)[hit["idx"]] = hit["t"]
            flat_i = img.reshape(-1, 3)
            N = hit["N"]
            # object-specific material + ambient occlusion straight from the SDF
            ao = np.zeros(len(hit["P"]), np.float32)
            for oi, ob in enumerate(objs):
                sel = hit["obj"] == oi
                if sel.any():
                    ao[sel] = R.sdf_ao(ob.sdf, hit["P"][sel], N[sel])
            P = hit["P"]
            for oi, m in enumerate(mats):
                sel = hit["obj"] == oi
                if not sel.any():
                    continue
                mm = dict(C=np.repeat(np.asarray(m["C"], np.float32)[None, :], int(sel.sum()), 0),
                          S=m["S"], R=m["R"], amb=m["amb"], rim=m["rim"])
                if kind == "bear" and oi == 0:
                    q = P[sel] - np.asarray(act["pos"], np.float32)[None, :]
                    # face, muzzle and eyes read lighter/darker: tells you it is a bear
                    muz = (G.smoothstep(1.34, 1.52, q[:, 2]) * G.smoothstep(0.20, 0.06, np.abs(q[:, 0])))[:, None]
                    mm["C"] = mm["C"] * (1 - muz) + np.array([0.155, 0.118, 0.088], np.float32)[None, :] * muz
                    eye = np.zeros(len(q), bool)
                    for sx in (-1, 1):
                        c = np.array([0.098 * sx, 1.222, 1.455], np.float32)
                        eye |= np.linalg.norm(q - c, axis=1) < 0.052
                    mm["C"][eye] = np.array([0.010, 0.009, 0.009], np.float32)
                    mm["R"] = np.where(eye, 0.05, mm["R"])
                    mm["S"] = np.where(eye, 2.4, mm["S"])
                flat_i[hit["idx"][sel]] = R.shade_surface(P[sel], N[sel], mm, cam, lights, cave, ao[sel])
            img = flat_i.reshape(img.shape)

    # flame + dust: additive light in the air, still simulated, never a still
    P = _particles()
    if tb and np.linalg.norm(np.asarray(tb, np.float32) - cam.eye) > 0.85:
        fp, fc, fh = P["flame"].step(1.0 / 24.0, np.asarray(tb, np.float32))
        fnd = dict(P=fp.astype(np.float32), N=R.nrm(cam.eye[None, :] - fp).astype(np.float32),
                   C=np.clip(fc, 0, 1).astype(np.float32), S=np.full(len(fp), 0.0, np.float32),
                   R=np.full(len(fp), 0.9, np.float32), PX=np.full(len(fp), 0.020, np.float32),
                   EM=(fh * 2.6).astype(np.float32))
        fs = R.splat(fnd, cam, W, H, depth, rad=1.1)
        if fs is not None:
            flat_i = img.reshape(-1, 3)
            flat_i[fs["idx"]] = flat_i[fs["idx"]] + np.clip(fs["C"], 0, 1) * (fs["EM"] * 1.6)[:, None]
            img = flat_i.reshape(img.shape)

    dustP = P["dust"].P
    near = np.linalg.norm(dustP - cam.eye[None, :], axis=1) < 7.0
    if near.sum() > 8:
        dn = dict(P=dustP[near], N=R.nrm(cam.eye[None, :] - dustP[near]).astype(np.float32),
                  C=np.full((int(near.sum()), 3), 0.62, np.float32),
                  S=np.full(int(near.sum()), 0.0, np.float32),
                  R=np.full(int(near.sum()), 0.9, np.float32),
                  PX=np.full(int(near.sum()), 0.0045, np.float32),
                  EM=np.zeros(int(near.sum()), np.float32))
        dc = R.shade_points(dn, cam, lights, cave, amb=0.0)
        ds = R.splat(dn, cam, W, H, depth, rad=1.0)
        if ds is not None:
            glow = ds["C"] * 0.5 + dc.mean(0, keepdims=True) * 0.5
            flat_i = img.reshape(-1, 3)
            flat_i[ds["idx"]] = flat_i[ds["idx"]] + glow * 0.35
            img = flat_i.reshape(img.shape)

    vol, vt = R.volumetrics(cam, cave, lights, W, H, density=0.0075, res=0.34)
    img = img * vt[..., None] + vol
    fin = R.finish(img, seed=seed, exposure=exp)
    # an edit opens and closes: 1 s up from black, 1.2 s down to black
    fade = min(1.0, T / 1.0) * min(1.0, max(0.0, (60.0 - T) / 1.2))
    if fade < 1.0:
        fin = fin * max(fade, 0.0) ** 1.4
    fr = Image.fromarray((fin * 255).astype(np.uint8))
    return draw_text(fr, s.text, s.texpos), k, s


def main():
    t0 = float(sys.argv[1]); t1 = float(sys.argv[2])
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 480
    H = int(W * 9 / 16)
    fps = 24
    out = sys.argv[4] if len(sys.argv) > 4 else "out/clip3d.mp4"
    os.makedirs("out", exist_ok=True)
    cave, shots = F.film()
    starts, acc = [], 0.0
    for s in shots:
        starts.append(acc); acc += s.dur
    n = int(round((t1 - t0) * fps))
    p = subprocess.Popen([FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-preset", "fast", "-crf", "17",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(n):
        fr, k, s = build_frame(t0 + i / fps, W, H, cave, shots, starts, seed=i)
        p.stdin.write(fr.tobytes())
        if i % 24 == 0:
            print("frame", i, "/", n, flush=True)
    p.stdin.close(); p.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
