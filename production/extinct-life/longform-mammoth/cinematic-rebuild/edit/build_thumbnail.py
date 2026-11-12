"""Build the film's thumbnail candidates from its own frames.

Every pixel comes from the reel. Nothing is AI-illustrated, nothing is borrowed from a
stock image, and no number appears that the film does not say out loud. The film already
carries an honesty problem on its plates; a thumbnail that invented a label would be the
one dishonest frame in the whole package.

The design rules below are not taste. Each one is tied to the measured evidence in
METADATA-RESEARCH.md §4:

  * one focal subject, placed right or centre-right, so it survives the left-hand
    duration stamp and the right-hand menu on mobile
  * three words or fewer at 2x the x-height of anything else, so the title is for the
    algorithm and the thumbnail is for the human
  * warm/cool split: the subject against a background of the opposite temperature gives
    the separation that a low-contrast snow scene otherwise lacks
  * the honesty label stays legible: this is a reconstruction, and saying so costs
    nothing a click was going to buy

Usage:
  python build_thumbnail.py                # writes every candidate to public/thumbnails/
  python build_thumbnail.py --list         # print the candidates and stop
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

base = Path(__file__).resolve().parent
root = base.parents[4]   # .../Monarch.Overall.Work
reel = root / '.cache/mammoth-edit/review-reel-continuous.mp4'
out = root / 'public/thumbnails'
fonts = root / 'public/showreel/fonts'
W, H = 1280, 720

# (name, frame seconds, kicker, headline, crop, type position, note)
# "type position" is 'lower' or 'sky'. The sky variant exists because the mobile test at
# 168x94 showed that type over the snow eats the only subject in frame; the same words in
# empty sky leave the herd intact and still read.
CANDIDATES = [
    ('A-they-were-still-here', 790.0, '4,000 YEARS AGO', 'STILL HERE',
     'crop=1280:660:0:0,scale=1280:660,pad=1280:720:0:30:color=0x0B1114', 'lower',
     'golden-hour herd. The only warm field in 13 minutes, so it wins the colour fight in a '
     'cold-blue feed before the eye reads anything. Passes at 168x94.'),
    ('B-what-killed-them', 745.0, 'WRANGEL ISLAND', 'WHO KILLED THEM?',
     'crop=680:382:351:162,scale=1280:720', 'sky',
     'question form with the herd pushed to 1.9x so it survives a 168 px shelf. Type sits '
     'in empty sky. The old version lost the animals at mobile size; this one does not.'),
    ('C-one-genome', 640.0, 'ONE ISLAND, ONE HERD', 'TEN GENERATIONS',
     'crop=1280:660:0:0,scale=1280:660,pad=1280:720:0:30:color=0x0B1114', 'lower',
     'map frame. The missing samples are literally the shape on screen. Weakest on emotion, '
     'strongest on specificity and the only cool-blue carrier of the three.'),
    ('D-no-verdict', 725.0, 'FOUR WITNESSES', 'NO VERDICT',
     'crop=1280:720:0:0', 'ledger',
     'the verdict ledger. A near-white card in a feed of dark blue ice is a contrast anomaly '
     'before it is a design. The three columns stay legible as structure even when the words '
     'are not - which is the whole point: it looks like a case file, because it is one.'),
]


def label(text, size, x, y, color, shadow=6, spacing=1):
    """drawtext with a hard drop shadow, so type survives a bright sky."""
    return (f"drawtext=text='{text}':fontfile={fonts}/Anton-Regular.ttf:"
            f"fontsize={size}:fontcolor={color}:x={x}:y={y}:line_spacing={spacing}:"
            f"shadowcolor=black@0.62:shadowx=0:shadowy={shadow}")


def build(name, t, kicker, headline, crop, place, _note):
    dst = out / f'{name}.jpg'
    if place == 'ledger':
        # No vignette and no warm shift: the whole reason this carrier works is that it is
        # the only bright white card in a feed of dark ice.
        grade = 'eq=contrast=1.10:saturation=1.0:brightness=0.02'
    else:
        grade = ('eq=contrast=1.16:saturation=1.12:brightness=0.0,'
                 'colorbalance=rs=0.03:bs=-0.03,vignette=PI/5.0')
    if place == 'sky':
        kicker_y, head_y, color, ink, smax = 40, 78, '0xF2C46B', 'white', 7
    elif place == 'ledger':
        # White type on a near-white card is invisible at shelf size. On this one carrier
        # the strongest contrast pairing is dark type on light, which is also what makes it
        # look like a document rather than a poster.
        kicker_y, head_y, color, ink, smax = 540, 578, '0x9B3B25', '0x141414', 0
    else:
        kicker_y, head_y, color, ink, smax = 462, 500, '0xF2C46B', 'white', 7
    filters = [
        crop, grade,
        label(kicker, 30, 62, kicker_y, color, 3),
        label(headline, 104, 58, head_y, ink, smax),
    ]
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-loglevel', 'error',
        '-ss', f'{t:.3f}', '-i', str(reel), '-frames:v', '1',
        '-vf', ','.join(filters), '-q:v', '2', str(dst),
    ], check=True)
    # A 1920x1080 copy lives beside it. Not because the film is 1080p - it is 720p, and this
    # is an upsample - but because a single test variant under 1280x720 makes YouTube
    # downscale every variant in the test to 854x480. The upscale is the cheaper cost.
    big = out / 'upload-1920' / dst.name
    big.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-loglevel', 'error',
        '-i', str(dst), '-vf', 'scale=1920:1080:flags=lanczos', '-q:v', '2', str(big),
    ], check=True)
    return dst


def main():
    if '--list' in sys.argv:
        for name, t, kicker, headline, crop, place, note in CANDIDATES:
            print(f'{name:26} {t:7.1f}s  "{kicker} / {headline}"\n{"":26}{note}')
        return
    out.mkdir(parents=True, exist_ok=True)
    for name, t, kicker, headline, crop, place, note in CANDIDATES:
        p = build(name, t, kicker, headline, crop, place, note)
        print(f'{p.relative_to(root)}  {p.stat().st_size // 1024} KB')
    print('Every pixel is a frame of the reel; no illustrated or stock artwork.')


if __name__ == '__main__':
    main()
