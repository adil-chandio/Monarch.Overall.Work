"""Deterministic 1280x720 thumbnail renderer — three archetypes that actually differ.

No AI images, no stock, no network. The point is not "a pretty card": it is that every
archetype is a different *psychological bet*, and `score.py` measures which one reads in
a phone feed.

  A  NUMBER SLAM     — the proof archetype. A huge verifiable number IS the thumbnail.
  B  FACE + 3 WORDS  — the authority archetype. A face plus a three-word promise.
  C  CONTRAST SPLIT  — the tension archetype. Two states, one red slash, one word.
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT_DIR = os.path.join(ROOT, "public", "showreel", "fonts")
W, H = 1280, 720

OBSIDIAN = (11, 11, 13)
BONE = (242, 239, 233)
RED = (224, 27, 43)
ASH = (150, 150, 156)


def _f(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def display(size):
    return _f("Anton-Regular.ttf", size)


def mono(size):
    return _f("IBMPlexMono-400.ttf", size)


def sans(size, weight=800):
    return _f("Manrope-800.ttf" if weight >= 700 else "Manrope-700.ttf", size)


def _portrait(scale: float, target_h: int, flip: bool = False):
    """Cut the masked portrait out and scale it to sit on a thumbnail edge."""
    p = os.path.join(ROOT, "public", "proof", "portrait-masked.png")
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGBA")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    h = int(target_h * scale)
    w = int(im.width * h / im.height)
    return im.resize((w, h), Image.LANCZOS)


def _vignette(im: Image.Image, strength: float = 0.55) -> Image.Image:
    """Soft darkening at the frame edge — keeps the eye on the subject."""
    import numpy as np
    w, h = im.size
    yy, xx = np.meshgrid(np.linspace(0, 1, h), np.linspace(0, 1, w), indexing="ij")
    r = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) / 0.7071
    m = np.clip(1.0 - strength * r ** 2.2, 0.0, 1.0)
    arr = np.asarray(im.convert("RGB"), dtype=np.float64) * m[..., None]
    return Image.fromarray(arr.clip(0, 255).astype("uint8"))


def _grain(im: Image.Image, amount: int = 6) -> Image.Image:
    import numpy as np
    rng = np.random.default_rng(7)
    a = np.asarray(im, dtype=np.int16)
    n = rng.normal(0, amount, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype("uint8"))


def _rules(d: ImageDraw.ImageDraw, colour, inset=44):
    """Thin frame rules — the studio's signature, and free focal containment."""
    d.line([(inset, inset), (W - inset, inset)], fill=colour, width=2)
    d.line([(inset, H - inset), (W - inset, H - inset)], fill=colour, width=2)


def _tracked(d, xy, text, font, fill, tracking=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + tracking
    return x


# ---------------------------------------------------------------- archetype A
def archetype_number_slam(number="583,290", kicker="VERIFIED VIEWS · NOT AN ESTIMATE",
                          footer="PROOF OVER PROMISES", accent=RED):
    im = Image.new("RGB", (W, H), BONE)
    d = ImageDraw.Draw(im)
    # faint measurement grid: reads as "instrument", not "poster"
    for x in range(0, W, 80):
        d.line([(x, 0), (x, H)], fill=(228, 224, 216), width=1)
    for y in range(0, H, 80):
        d.line([(0, y), (W, y)], fill=(228, 224, 216), width=1)

    pom = _portrait(1.0, H)

    _tracked(d, (64, 58), kicker, mono(22), (90, 88, 84), tracking=3)

    # size the number to the space the portrait does not occupy, then place everything
    # relative to the number's REAL ink bounds (font metrics lie about Anton's cap line)
    free_w = (W - pom.width + 10 if pom else W) - 58 - 40
    size = 300
    while size > 90 and d.textlength(number, font=display(size)) > free_w:
        size -= 6

    layer = Image.new("L", (W, H), 0)
    ImageDraw.Draw(layer).text((58, 140), number, font=display(size), fill=255)
    ink = layer.getbbox()                      # (x0, y0, x1, y1) of the actual glyphs
    im.paste(Image.new("RGB", (W, H), OBSIDIAN), (0, 0), layer)

    rule_y = ink[3] + 38          # clear of the comma's descender
    d.rectangle([64, rule_y, 64 + min(430, ink[2] - 64), rule_y + 13], fill=accent)
    f2 = display(84)
    d.text((64, rule_y + 40), "REAL", font=f2, fill=accent)
    d.text((64 + d.textlength("REAL ", font=f2), rule_y + 40), "NUMBERS.", font=f2, fill=OBSIDIAN)
    _tracked(d, (64, H - 96), footer, mono(24), (40, 40, 42), tracking=4)
    d.line([(36, H - 40), (W - 36, H - 40)], fill=(200, 196, 188), width=2)
    d.line([(36, 36), (W - 36, 36)], fill=(200, 196, 188), width=2)
    if pom:
        im.paste(pom, (W - pom.width + 10, H - pom.height), pom)
    return _grain(im)


# ---------------------------------------------------------------- archetype B
def archetype_face_words(words=("PROOF", "OVER", "PROMISES"),
                         kicker="MONARCH® STUDIO · HYDERABAD, PK"):
    im = Image.new("RGB", (W, H), OBSIDIAN)
    drain = Image.new("RGB", (int(W * 0.55), H), (17, 17, 20))
    im.paste(drain, (0, 0))
    pom = _portrait(1.0, H)
    if pom:
        im.paste(pom, (W - pom.width + 30, H - pom.height), pom)
    im = _vignette(im, 0.72).filter(ImageFilter.UnsharpMask(2, 120, 3))
    d = ImageDraw.Draw(im)
    _tracked(d, (60, 56), kicker, mono(21), ASH, tracking=3)
    y = 150
    for i, word in enumerate(words):
        f = display(126 if len(word) < 8 else 108)
        d.text((58, y), word, font=f, fill=RED if i == 1 else BONE)
        y += 128
    d.rectangle([58, H - 150, 58 + 8, H - 60], fill=RED)
    _tracked(d, (88, H - 122), "ZERO BOUGHT NUMBERS", mono(22), ASH, tracking=3)
    _rules(d, (44, 44, 48))
    return _grain(im)


# ---------------------------------------------------------------- archetype C
def archetype_contrast(left="PROMISES.", right="PROOF.", kicker="2.5 YEARS · 1 PRACTICE"):
    im = Image.new("RGB", (W, H), BONE)
    d = ImageDraw.Draw(im)
    split = int(W * 0.52)
    d.rectangle([split, 0, W, H], fill=OBSIDIAN)

    f_small = display(74)
    for i, line in enumerate(["EVERYONE", "SHIPS", "PROMISES"]):
        d.text((58, 180 + i * 82), line, font=f_small, fill=(176, 172, 164))

    # the left headline must fit inside the light panel, with 46 px of air before the slash
    panel = split - 58 - 46
    size = 184
    while size > 60 and d.textlength(left, font=display(size)) > panel:
        size -= 6
    d.text((58, 430), left, font=display(size), fill=OBSIDIAN)

    pom = _portrait(1.0, H)
    if pom:
        tinted = pom.copy()
        im.paste(tinted, (W - tinted.width + 4, H - tinted.height), tinted)

    right_panel = W - (split + 52) - 86        # leave room for the portrait cheek
    size = 150
    while size > 56 and d.textlength(right, font=display(size)) > right_panel:
        size -= 4
    d.text((split + 52, 200), right, font=display(size), fill=BONE)
    d.text((split + 56, 372), "OVER", font=display(96), fill=RED)
    d.text((split + 56, 470), "PROMISES", font=display(96), fill=BONE)

    # the slash: one red diagonal, no gradient tricks
    d.polygon([(split - 26, H), (split + 15, H), (split + 74, 0), (split + 33, 0)], fill=RED)
    _tracked(d, (split + 52, 80), kicker, mono(20), ASH, tracking=3)
    _rules(d, (206, 202, 194))
    return _grain(im)


ARCHETYPES = {
    "A-number-slam": archetype_number_slam,
    "B-face-words": archetype_face_words,
    "C-contrast-split": archetype_contrast,
}


def render_thumbnail(archetype="A-number-slam", size=(1280, 720), **kw):
    im = ARCHETYPES[archetype](**kw)
    return im.resize(size, Image.LANCZOS) if size != (W, H) else im


def render_suite(out_dir="public/showreel/thumbs", **overrides):
    """Render all three archetypes + the 168x94 feed proofs used for grading."""
    os.makedirs(out_dir, exist_ok=True)
    out = {}
    for name, fn in ARCHETYPES.items():
        kw = overrides.get(name, {})
        im = fn(**kw)
        path = os.path.join(out_dir, f"{name}.jpg")
        im.save(path, quality=92, subsampling=1)
        feed = im.resize((FEED_W, FEED_H), Image.LANCZOS)
        feed.save(os.path.join(out_dir, f"{name}__feed.jpg"), quality=92)
        out[name] = path
    return out


FEED_W, FEED_H = 168, 94


if __name__ == "__main__":
    for k, v in render_suite().items():
        print(k, "->", v)
