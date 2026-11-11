#!/usr/bin/env python3
"""Build local frame-by-frame QA sheets for a *private* research clip.

This tool does not upload files and does not decide whether motion or identity
is acceptable. Inspect every frame, especially shoes and contact. Supply the
receipt from the same private archive to verify that its sha256 matches.
All resulting sheets contain recognizable material: keep them private.

Example:
  python inspect_private_motion.py video.mp4 --receipt receipt.json \
      --output /tmp/private-qa --foot-crop 240,255,540,448
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
from PIL import Image, ImageDraw


def sha256_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def crop_rectangle(value):
    try:
        coords = tuple(map(int, value.split(',')))
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Crop must be x0,y0,x1,y1') from exc
    if len(coords) != 4 or coords[0] < 0 or coords[1] < 0 or coords[2] <= coords[0] or coords[3] <= coords[1]:
        raise argparse.ArgumentTypeError('Invalid x0,y0,x1,y1 crop')
    return coords


def sheets(frames, output, prefix, columns, rows, width, crop=None):
    per_sheet = columns * rows
    for start in range(0, len(frames), per_sheet):
        selected = frames[start:start + per_sheet]
        images = [frame.crop(crop) if crop else frame for frame in selected]
        height = max(1, round(width * images[0].height / images[0].width))
        tile_height = height + 20
        canvas = Image.new('RGB', (columns * width, rows * tile_height), 'black')
        draw = ImageDraw.Draw(canvas)
        for index, image in enumerate(images):
            x = index % columns * width
            y = index // columns * tile_height
            draw.text((x + 4, y + 2), str(start + index), fill='white')
            canvas.paste(image.resize((width, height), Image.Resampling.LANCZOS), (x, y + 20))
        canvas.save(output / f'{prefix}-{start:04d}.jpg', quality=92)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--foot-crop', type=crop_rectangle)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text())
    entries = [v for v in receipt.get('variants', []) if v.get('name') == args.video.name]
    digest = sha256_file(args.video)
    if len(entries) != 1 or digest != entries[0].get('sha256'):
        raise ValueError('Receipt missing or video checksum mismatch')
    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise ValueError('Cannot decode video')
    fps = cap.get(cv2.CAP_PROP_FPS)
    declared = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if not (0 < fps < 120 and 0 < declared <= 1000 and width > 0 and height > 0):
        raise ValueError('Unexpected video metadata')
    if args.foot_crop and (args.foot_crop[2] > width or args.foot_crop[3] > height):
        raise ValueError('Foot crop is outside the frame')
    frames = []
    try:
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            if bgr.shape[:2] != (height, width):
                raise ValueError('Frame dimensions changed')
            frames.append(Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)))
            if len(frames) > declared:
                raise ValueError('Unexpected extra frames')
    finally:
        cap.release()
    if len(frames) != declared or (receipt.get('frames_requested') and len(frames) != receipt['frames_requested']):
        raise ValueError('Decoded frame count does not match metadata/receipt')
    args.output.mkdir(parents=True, exist_ok=True)
    sheets(frames, args.output, 'full', 4, 5, 416)
    if args.foot_crop:
        sheets(frames, args.output, 'feet', 4, 4, 320, args.foot_crop)
    info = {'video_sha256': digest, 'frames': len(frames), 'fps': fps,
            'width': width, 'height': height, 'duration_seconds': len(frames) / fps,
            'status': 'research_only_visual_review_required'}
    (args.output / 'qa-metadata.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps(info, indent=2))


if __name__ == '__main__':
    main()
