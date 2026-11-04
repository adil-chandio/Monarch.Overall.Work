"""Grade simulation: reproduce a scene's CSS filter chain + overlay in numpy and
report the shot's mean colour, so a grade can be chosen against the reference's
measured number instead of by eye and a 7-minute render.

CSS filter semantics used (per filter-effects spec):
  brightness(b)  c' = c * b
  saturate(s)    c' = L + s*(c - L),  L = .213R + .715G + .072B
  contrast(k)    c' = (c - .5)*k + .5
"""
import numpy as np
from PIL import Image, ImageFilter

TARGET_S15 = dict(rgb=(60, 83, 24), green=0.424)   # REF-01 0.83-1.00 shot
TARGET_S7 = dict(rgb=(52, 29, 29))                 # REF-01 9.13-11.70 shot
TARGET_S14 = dict(rgb=(59, 26, 23), red=0.495)     # REF-01 14.80-23.30 shot


def load(path, w=720, h=1280):
    im = Image.open(path).convert("RGB").resize((w, h), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32) / 255.0


def brightness(a, b):
    return a * b


def saturate(a, s):
    L = (a * np.array([.213, .715, .072], dtype=np.float32)).sum(axis=2, keepdims=True)
    return L + s * (a - L)


def contrast(a, k):
    return (a - 0.5) * k + 0.5


def hue_rotate(a, deg):
    c, s = np.cos(np.deg2rad(deg)), np.sin(np.deg2rad(deg))
    m = np.array([
        [.213 + c * .787 - s * .213, .715 - c * .715 - s * .715, .072 - c * .072 + s * .928],
        [.213 - c * .213 + s * .143, .715 + c * .285 + s * .140, .072 - c * .072 - s * .283],
        [.213 - c * .213 - s * .787, .715 - c * .715 + s * .715, .072 + c * .928 + s * .072],
    ], dtype=np.float32)
    return a @ m.T


def over(base, colour, alpha):
    """normal-blend a flat colour at alpha over the base"""
    return base * (1 - alpha) + np.asarray(colour, dtype=np.float32) / 255.0 * alpha


def vertical_gradient_overlay(a, stops):
    """stops = [(pos, colour, alpha), ...] top->bottom, alpha in 0..1"""
    h = a.shape[0]
    pos = np.linspace(0, 1, h)
    out = a.copy()
    for i in range(len(stops) - 1):
        p0, c0, a0 = stops[i]
        p1, c1, a1 = stops[i + 1]
        m = (pos >= p0) & (pos <= p1)
        if not m.any():
            continue
        f = ((pos[m] - p0) / max(p1 - p0, 1e-6))[:, None, None]
        col = (np.array(c0, dtype=np.float32) * (1 - f) + np.array(c1, dtype=np.float32) * f) / 255.0
        al = (a0 * (1 - f[:, :, 0]) + a1 * f[:, :, 0])[:, :, None]
        out[m] = out[m] * (1 - al) + col * al
    return out


def stats(a):
    px = (np.clip(a, 0, 1) * 255).reshape(-1, 3)
    mean = px.mean(axis=0)
    green = ((px[:, 1] > px[:, 0] + 25) & (px[:, 1] > px[:, 2] + 15)).mean()
    red = ((px[:, 0] > px[:, 1] + 25) & (px[:, 0] > px[:, 2] + 25)).mean()
    return mean.round(0).astype(int), green, red


def s15_variant(name, br, sa, hue, white_a, want=0.424):
    a = load("showreel/v4/assets/plate-bag-green.png")
    a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(3)), dtype=np.float32) / 255.0
    a = brightness(a, br)
    a = saturate(a, sa)
    a = hue_rotate(a, hue)
    a = vertical_gradient_overlay(a, [
        (0.0, (255, 255, 255), white_a), (0.38, (255, 255, 255), white_a * 0.18),
        (1.0, (0, 0, 0), 0.18)])
    m, g, r = stats(a)
    print(f"  {name:34s} rgb {m}  green% {g*100:5.1f}  (target {TARGET_S15['rgb']} / {want*100:.1f}%)")


def s7_variant(name, br, sa, ct):
    a = load("showreel/v4/assets/plate-cta-hero.png")
    a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(3)), dtype=np.float32) / 255.0
    a = brightness(a, br)
    a = contrast(a, ct)
    a = saturate(a, sa)
    m, g, r = stats(a)
    print(f"  {name:34s} rgb {m}  (target {TARGET_S7['rgb']})")


if __name__ == "__main__":
    print("S15  ·  BILLION on green — REF-01 wants a bright kelly green field")
    print("  current build measured in the master: rgb [49 65 45] green% 15.8")
    s15_variant("current 1.22/.78/-6deg/.34", 1.22, .78, -6, .34)
    s15_variant("1.40/.95/0deg/.30", 1.40, .95, 0, .30)
    s15_variant("1.55/1.05/0deg/.26", 1.55, 1.05, 0, .26)
    s15_variant("1.70/1.10/+2deg/.22", 1.70, 1.10, 2, .22)
    s15_variant("1.90/1.15/+3deg/.18", 1.90, 1.15, 3, .18)
    print("\nS7  ·  the 2.57 s main shot — REF-01 wants a lifted maroon, not a dark brown")
    print("  current build measured in the master: rgb [22 12 6]")
    for n, br, sa, ct in (("current .70/1.28/.55", .70, .55, 1.28),
                          (".92/1.12/.85", .92, .85, 1.12),
                          ("1.05/1.10/.95", 1.05, .95, 1.10),
                          ("1.15/1.05/1.00", 1.15, 1.00, 1.05)):
        s7_variant(n, br, sa, ct)
