"""Check the metadata package against the reel it actually describes.

This does not check that the copy is *good* - no script can. It checks the things that are
objectively wrong when they are wrong:

  * a chapter timestamp that does not land on a line of narration
  * a chapter list the platform will refuse to render (first not at 00:00, a chapter
    under 10 seconds, fewer than three chapters)
  * a title whose stated character count is wrong, or that overflows mobile truncation
  * a thumbnail that is the wrong aspect ratio or over the file-size ceiling

Usage:
  python validate_metadata.py            # exit 1 on any failure
"""
import json
import re
import struct
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[5]
pkg = root / 'production/extinct-life/longform-mammoth/cinematic-rebuild'
doc = (pkg / 'METADATA-RESEARCH.md').read_text()
caps = json.loads((pkg / 'full-script-v2/caption-data.json').read_text())['captions']
reel_duration = 796.07
MOBILE_TRUNCATION = 70   # characters safe on a phone browse shelf
CHAPTER_MIN = 10          # YouTube: each chapter at least 10 s
TOLERANCE = 2.5           # a chapter may start up to 2.5 s before its first word

fails, warns = [], []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def warn(cond, msg):
    if cond:
        warns.append(msg)


# ---- 1. chapters land on narration and satisfy the platform's rules ----------
chapters = [(int(m) * 60 + int(s), name)
            for m, s, name in re.findall(r'^(\d{2}):(\d{2}) (.+)$', doc, re.M)]
check(len(chapters) >= 3, f'only {len(chapters)} chapter lines; YouTube needs at least 3')
check(bool(chapters) and chapters[0][0] == 0,
      'first chapter must be at 00:00 or the list will not render at all')

starts = [c['start'] for c in caps]
for t, name in chapters:
    near = min((abs(t - s) for s in starts), default=9e9)
    check(near <= TOLERANCE,
          f'chapter {t // 60}:{t % 60:02d} "{name}" is {near:.1f}s from any narration start')

for (a, an), (b, bn) in zip(chapters, chapters[1:]):
    check(b - a >= CHAPTER_MIN,
          f'chapter "{an}" is only {b - a}s long; minimum is {CHAPTER_MIN}s')
check(chapters[-1][0] < reel_duration,
      f'last chapter starts at {chapters[-1][0]}s, past the {reel_duration}s reel')

# ---- 2. titles: stated counts must be true, and fit mobile -------------------
for m in re.finditer(r'\*\*(.+?)\*\*[^\n]*\n?>? ?`(\d+) characters?`', doc):
    title, claimed = m.group(1), int(m.group(2))
    check(len(title) == claimed,
          f'title "{title}" is {len(title)} chars, document claims {claimed}')

for line in doc.splitlines():
    m = re.match(r'\| \d+ \| \*\*(.+?)\*\* \| (\d+) \|', line)
    if m:
        title, claimed = m.group(1), int(m.group(2))
        check(len(title) == claimed,
              f'table title "{title}" is {len(title)} chars, claims {claimed}')
        check(len(title) <= MOBILE_TRUNCATION,
              f'table title "{title}" is {len(title)} chars, over {MOBILE_TRUNCATION}')


# ---- 3. thumbnails: 16:9, under the 2 MB ceiling -----------------------------
def jpeg_size(path):
    with path.open('rb') as f:
        data = f.read()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack('>HH', data[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack('>H', data[i + 2:i + 4])[0]
    raise ValueError(f'no SOF marker in {path.name}')


thumbs = sorted((root / 'public/thumbnails').glob('*.jpg'))
check(len(thumbs) == 4, f'{len(thumbs)} thumbnails found; package describes exactly 4 (A-D)')
# The native test caps at three variants, so the package must supply 3 launch + 1 spare.
check(len(thumbs) >= 3, 'Test & Compare needs at least three variants')
for p in thumbs:
    w, h = jpeg_size(p)
    check(w * 9 == h * 16, f'{p.name} is {w}x{h}, not 16:9')
    check(p.stat().st_size < 2_000_000,
          f'{p.name} is {p.stat().st_size / 1e6:.2f} MB, over the 2 MB ceiling')

print(f'chapters     : {len(chapters)}  (shortest gap '
      f'{min((b - a) for (a, _), (b, _) in zip(chapters, chapters[1:]))}s)')
# 1920x1080 test copies: one sub-1280 variant degrades the whole experiment to 854x480
big = sorted((root / 'public/thumbnails/upload-1920').glob('*.jpg'))
check(len(big) == len(thumbs), f'{len(big)} upload copies for {len(thumbs)} thumbnails')
for p in big:
    w, h = jpeg_size(p)
    check((w, h) == (1920, 1080), f'{p.name} is {w}x{h}, test variants must be >= 1280x720')
    check(p.stat().st_size < 2_000_000,
          f'{p.name} is {p.stat().st_size / 1e6:.2f} MB, over the 2 MB ceiling')

print(f'upload copies: {len(big)}  all 1920x1080')
print(f'thumbnails   : {len(thumbs)}  '
      + ', '.join(f'{p.name.split("-")[0]} {jpeg_size(p)[0]}x{jpeg_size(p)[1]}' for p in thumbs))
print(f'reel duration: {reel_duration}s')
for w in warns:
    print(f'  warn: {w}')
for f in fails:
    print(f'  FAIL: {f}')
print('PASS' if not fails else f'{len(fails)} failure(s)')
sys.exit(1 if fails else 0)
