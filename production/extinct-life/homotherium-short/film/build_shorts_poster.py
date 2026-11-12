"""Build the Shorts poster carriers from the film's own extracted assets.

Design constraint that drives everything here: a Shorts thumbnail is only ever seen at
about 108x192 in a phone shelf. Type that is tasteful at 1080x1920 is invisible there, so
these are built mobile-first - the words are laid out at final display size and checked
cropped to a 108x192 tile before they are accepted.

Every element is already in the film: the specimen cutout is the same RGBA that
`prepare_assets.py` extracted from the published figures, and the palette is the film's own
navy and gold. Nothing is drawn that the film does not contain, so the poster cannot promise
a shot the video never delivers.

Usage:
  python build_shorts_poster.py
"""
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[4]   # .../Monarch.Overall.Work
pkg = root / 'production/extinct-life/homotherium-short'
out = root / 'public/thumbnails/shorts-homotherium'
W, H = 1080, 1920

NAVY_DEEP = (11, 20, 26)
NAVY = (16, 30, 38)
GOLD = (232, 189, 122)
CREAM = (243, 238, 228)
FONT = root / 'public/showreel/fonts/Anton-Regular.ttf'
FONT_BODY = root / 'public/showreel/fonts/Manrope-800.ttf'

# (slug, kicker, headline lines, asset, headline size, note)
VARIANTS = [
    ('A-35000-years', 'STILL HAS FUR', ['35,000', 'YEARS OLD'], 'cub.png', 210,
     'the number is the hook and the specimen is the proof. Reads at 108px because the '
     'digits are the largest thing in frame.'),
    ('B-real-specimen', 'NOT A RECONSTRUCTION', ['A REAL', 'CUB'], 'cub.png', 200,
     'leads with authenticity, which is the film\'s actual differentiator and the thing '
     'AI-generated palaeo content cannot claim.'),
    ('C-more-than-a-skeleton', 'SOFT TISSUE', ['MORE THAN', 'A SKELETON'], 'paw.png', 150,
     'the comparison angle: this is what bones cannot show. Weakest single hook, strongest '
     'for an audience that already watches palaeo content.'),
]


def font(path, size):
    return ImageFont.truetype(str(path), size)


def tracked(draw, xy, text, f, fill, tracking=6):
    """Draw text with letter tracking; Anton at display size sits too tight otherwise."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking


def build(slug, kicker, lines, asset, size, _note):
    img = Image.new('RGB', (W, H), NAVY_DEEP)
    d = ImageDraw.Draw(img)
    # Subtle vertical gradient so the card does not read as flat black on an OLED phone.
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(
            int(NAVY_DEEP[i] + (NAVY[i] - NAVY_DEEP[i]) * (1 - abs(0.5 - t) * 2))
            for i in range(3)))

    # ---- specimen ----
    # Sized to sit inside the middle band and never touch the headline or the footer. A
    # specimen cropped by the frame edge reads as an accident, not a crop.
    spec = Image.open(pkg / 'assets' / asset).convert('RGBA')
    band_top, band_bottom = 760, 1580
    max_h = band_bottom - band_top
    max_w = int(W * 0.92)
    scale = min(max_w / spec.width, max_h / spec.height)
    spec = spec.resize((int(spec.width * scale), int(spec.height * scale)), Image.LANCZOS)
    # A soft gold glow behind the specimen separates it from the navy without a box.
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.06, band_top - 40, W * 0.94, band_bottom + 40], fill=(*GOLD, 22))
    img.paste(Image.alpha_composite(img.convert('RGBA'), glow).convert('RGB'), (0, 0))
    d = ImageDraw.Draw(img)
    img.paste(spec, ((W - spec.width) // 2,
                     band_top + (max_h - spec.height) // 2), spec)
    d = ImageDraw.Draw(img)

    # ---- type: top block, deliberately oversized ----
    tracked(d, (78, 210), kicker, font(FONT_BODY, 44), GOLD, 8)
    y = 300
    for line in lines:
        d.text((72, y), line, font=font(FONT, size), fill=CREAM,
               stroke_width=0, anchor='la')
        y += int(size * 1.02)

    # ---- evidence strip: a solid footer, so the attribution is never lost in the artwork ----
    d.rectangle([0, 1640, W, H], fill=NAVY_DEEP)
    d.rectangle([0, 1640, W, 1644], fill=GOLD)
    tracked(d, (72, 1690), 'REAL SPECIMEN  ·  NOT A LIVING ANIMAL', font(FONT_BODY, 34), CREAM, 4)
    tracked(d, (72, 1748), 'LOPATIN ET AL. 2024  ·  CC BY 4.0', font(FONT_BODY, 28), (150, 165, 172), 3)

    dst = out / f'{slug}.jpg'
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, 'JPEG', quality=92, optimize=True)
    # Shelf proof: the 108x192 tile is what a viewer actually sees.
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-loglevel',
                    'error', '-i', str(dst), '-vf', 'scale=108:192', '-q:v', '2',
                    str(out / f'shelf-{slug[:1]}-108.jpg')], check=True)
    return dst


if __name__ == '__main__':
    for slug, kicker, lines, asset, size, note in VARIANTS:
        p = build(slug, kicker, lines, asset, size, note)
        print(f'{p.relative_to(root)}  {p.stat().st_size // 1024} KB')
