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

# (name, frame seconds in the reel, kicker, headline, note for the reviewer)
CANDIDATES = [
    ('A-they-were-still-here', 790.0, '4,000 YEARS AGO', 'STILL HERE',
     'golden-hour herd; the warm sky is the only warm field in the film, so it stops a '
     'scroll in a cold feed. Payoff is the film\'s own claim.'),
    ('B-what-killed-them', 745.0, 'WRANGEL ISLAND', 'WHO KILLED THEM?',
     'question form, no answer offered. The pale plain gives the type its contrast; the '
     'question is the film\'s actual spine.'),
    ('C-one-genome', 640.0, 'ONE ISLAND, ONE HERD', 'TEN GENERATIONS',
     'map frame; the missing samples are literally the shape on screen. Weakest of the '
     'three on emotion, strongest on specificity.'),
]


def label(text, size, x, y, color, shadow=6, spacing=1):
    """drawtext with a hard drop shadow, so type survives a bright sky."""
    return (f"drawtext=text='{text}':fontfile={fonts}/Anton-Regular.ttf:"
            f"fontsize={size}:fontcolor={color}:x={x}:y={y}:line_spacing={spacing}:"
            f"shadowcolor=black@0.62:shadowx=0:shadowy={shadow}")


def build(name, t, kicker, headline, _note):
    dst = out / f'{name}.jpg'
    # Crop inward before scaling: the herd sits centre-right in the source frame, and a
    # little push to the right keeps it clear of the type block.
    crop = 'crop=1280:660:0:0,scale=1280:660,pad=1280:720:0:30:color=0x0B1114'
    grade = ('eq=contrast=1.14:saturation=1.18:brightness=0.01,'
             'colorbalance=rs=0.03:bs=-0.03,'
             'vignette=PI/5.0')
    # One type block, lower left, three words maximum, and nothing over a face or a tusk.
    filters = [
        crop, grade,
        label(headline.replace('\n', ' '), 104, 60, 500, 'white', 7),
        label(kicker, 30, 64, 462, '0xF2C46B', 3),
    ]
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-loglevel', 'error',
        '-ss', f'{t:.3f}', '-i', str(reel), '-frames:v', '1',
        '-vf', ','.join(filters), '-q:v', '2', str(dst),
    ], check=True)
    return dst


def main():
    if '--list' in sys.argv:
        for name, t, kicker, headline, note in CANDIDATES:
            print(f'{name:26} {t:7.1f}s  "{kicker} / {headline}"\n{"":26}{note}')
        return
    out.mkdir(parents=True, exist_ok=True)
    for name, t, kicker, headline, note in CANDIDATES:
        p = build(name, t, kicker, headline, note)
        print(f'{p.relative_to(root)}  {p.stat().st_size // 1024} KB')
    print('Every pixel is a frame of the reel; no illustrated or stock artwork.')


if __name__ == '__main__':
    main()
