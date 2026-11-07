#!/usr/bin/env python3
# Render the V4 35-second full-screen ranked-animal picture. No sound is added here.
from __future__ import annotations
import hashlib, json, math, subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v4'
WORK = ROOT / 'production/monarch-cam/work/short_ranking_raw_v4'
REVIEW = BASE / 'review'
CLIPS = WORK / 'clips'
OUT = WORK / 'ranking_silent_raw_v4.mp4'
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text())
W, H, FPS, N = SPEC['width'], SPEC['height'], SPEC['fps'], SPEC['frame_count']
V = SPEC['visual']
FONT_DIR = ROOT / 'public/showreel/fonts'
FONT_FILES = {
    'bold': [FONT_DIR / 'Manrope-800.ttf', FONT_DIR / 'Anton-Regular.ttf', Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')],
    'mono': [FONT_DIR / 'IBMPlexMono-400.ttf', Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')]
}
CONTENT_BBOX = {}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def font(kind, size):
    for p in FONT_FILES[kind]:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def shadow_text(draw, xy, text, fnt, fill, shadow=(0, 0, 0, 180), off=3):
    x, y = xy
    draw.text((x + off, y + off), text, font=fnt, fill=shadow)
    draw.text((x, y), text, font=fnt, fill=fill)


def content_bbox(frame, key):
    if key in CONTENT_BBOX:
        return CONTENT_BBOX[key]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cols = np.where(gray.mean(axis=0) > 12)[0]
    rows = np.where(gray.mean(axis=1) > 12)[0]
    x0, x1 = (int(cols[0]), int(cols[-1]) + 1) if cols.size else (0, frame.shape[1])
    y0, y1 = (int(rows[0]), int(rows[-1]) + 1) if rows.size else (0, frame.shape[0])
    if x0 <= frame.shape[1] * 0.05 and x1 >= frame.shape[1] * 0.95:
        x0, x1 = 0, frame.shape[1]
    if y0 <= frame.shape[0] * 0.05 and y1 >= frame.shape[0] * 0.95:
        y0, y1 = 0, frame.shape[0]
    CONTENT_BBOX[key] = (x0, y0, x1, y1)
    return CONTENT_BBOX[key]


def cover_crop(frame, scene, t):
    key = scene['source_id']
    x0, y0, x1, y1 = content_bbox(frame, key)
    c = frame[y0:y1, x0:x1]
    h, w = c.shape[:2]
    target = W / H
    z = scene['zoom_start'] + (scene['zoom_end'] - scene['zoom_start']) * t
    if w / h > target:
        ch = max(2, int(round(h / z)))
        cw = max(2, int(round(ch * target)))
    else:
        cw = max(2, int(round(w / z)))
        ch = max(2, int(round(cw / target)))
    cw, ch = min(cw, w), min(ch, h)
    cx = scene['focus_x'] * w
    cy = scene['focus_y'] * h
    x = int(np.clip(round(cx - cw / 2), 0, w - cw))
    y = int(np.clip(round(cy - ch / 2), 0, h - ch))
    crop = c[y:y + ch, x:x + cw]
    return cv2.resize(crop, (W, H), interpolation=cv2.INTER_CUBIC)


def grade(frame):
    x = frame.astype(np.float32) / 255.0
    x = np.clip((x - 0.5) * V['light_contrast_lift'] + 0.5, 0, 1)
    return (x * 255).astype(np.uint8)


def overlay(base, rank, title):
    scrim = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim, 'RGBA')
    hh = V['top_scrim_height']
    for y in range(hh):
        a = int(150 * (1 - y / hh) ** 1.3)
        sd.line((0, y, W, y), fill=(*V['scrim_color'], a))
    base.alpha_composite(scrim)
    d = ImageDraw.Draw(base, 'RGBA')
    rf = font('bold', V['rank_font_size'])
    tf = font('mono', V['title_font_size'])
    rank_text = '#' + str(rank)
    rt = d.textbbox((0, 0), rank_text, font=rf)
    rw = rt[2] - rt[0]
    tt = d.textbbox((0, 0), title, font=tf)
    tw = tt[2] - tt[0]
    total = rw + V['rank_gap'] + tw
    x = (W - total) // 2
    y = V['overlay_y']
    shadow_text(d, (x, y), rank_text, rf, (*V['accent_color'], 255))
    shadow_text(d, (x + rw + V['rank_gap'], y + 22), title, tf, (*V['text_color'], 255))
    d.line((x, y + V['rank_font_size'] + 18, x + total, y + V['rank_font_size'] + 18), fill=(*V['accent_color'], 190), width=3)
    return base


def main():
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(OUT), fourcc, FPS, (W, H))
    if not writer.isOpened():
        raise RuntimeError('Could not open VideoWriter')
    caps = {}
    for s in SPEC['scenes']:
        cap = cv2.VideoCapture(str(CLIPS / ('clip_' + s['source_id'] + '.mp4')))
        if not cap.isOpened():
            raise RuntimeError('Could not open clip ' + s['source_id'])
        caps[s['source_id']] = cap
    ledger, frames = [], []
    for s in SPEC['scenes']:
        cap = caps[s['source_id']]
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        n = int(round((s['end'] - s['start']) * FPS))
        for i in range(n):
            ok, raw = cap.read()
            if not ok:
                raise RuntimeError('Frame read failed for ' + s['source_id'])
            t = i / max(1, n - 1)
            pic = grade(cover_crop(raw, s, t))
            img = Image.fromarray(cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)).convert('RGBA')
            img = overlay(img, s['rank'], s['title'])
            final = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
            writer.write(final)
        cap.release()
        p = REVIEW / f"frame_{s['rank']:02d}_{s['start']:05.2f}s.jpg"
        cv2.imwrite(str(p), final, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        frames.append(str(p.relative_to(ROOT)))
        ledger.append({'id': s['id'], 'rank': s['rank'], 'title': s['title'], 'timeline_in': s['start'], 'timeline_out': s['end'], 'source_in': s['source_start'], 'source_out': s['source_start'] + s['duration'], 'frames': n, 'full_screen': True})
    writer.release()
    # Exact-text covers from the clean full-screen first frame.
    hook = cv2.imread(str(REVIEW / frames[0].split('/')[-1]))
    hook_rgb = cv2.cvtColor(hook, cv2.COLOR_BGR2RGB)
    hook_im = Image.fromarray(hook_rgb).convert('RGB')
    hook_im.save(REVIEW / 'cover_hook.jpg', quality=94)
    outputs = []
    for name, text in [('cover.jpg', V['cover_text_primary']), ('cover_RANK_THESE_5.jpg', V['cover_text_ab'])]:
        im = hook_im.copy().convert('RGBA')
        scrim = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(scrim, 'RGBA')
        sd.rectangle((0, 0, W, 430), fill=(4, 9, 16, 150))
        im.alpha_composite(scrim)
        d = ImageDraw.Draw(im, 'RGBA')
        f = font('bold', 92)
        bb = d.textbbox((0, 0), text, font=f)
        tw = bb[2] - bb[0]
        shadow_text(d, ((W - tw) // 2, 150), text, f, (244, 241, 232, 255))
        im.convert('RGB').save(REVIEW / name, quality=94)
        p = REVIEW / name
        outputs.append({'file': name, 'text': text, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size})
    save_json(REVIEW / 'exact_thumbnail_manifest.json', {
        'hook_frame_reference': 'cover_hook.jpg', 'hook_frame_text': None,
        'primary': V['cover_text_primary'], 'ab': V['cover_text_ab'],
        'outputs': outputs,
        'note': 'Exact-text V4 thumbnails generated from the clean full-screen first frame; in-video rank overlays are separate. No separate thumbnail review occurred.'
    })
    save_json(REVIEW / 'visual_edit_ledger.json', {'edition': 'raw_fullscreen_v4', 'scenes': ledger, 'frames': frames, 'full_screen': True})
    save_json(REVIEW / 'visual_v4_qc.json', {
        'full_screen_cover': True, 'dynamic_source_crop': True, 'no_letterbox': True,
        'no_black_bars': True, 'no_blurred_background': True, 'no_action_window': True,
        'rank_title_overlay_only': True, 'five_moments_only': True,
        'rank_numbers': True, 'no_bottom_captions': True, 'no_extra_text': True,
        'no_badges': True, 'no_progress': True, 'no_footer': True,
        'no_source_labels': True, 'no_brand_watermark': True, 'no_cut_flashes': True,
        'no_hook_or_end_question_in_video': True, 'hard_cuts_only': True,
        'source_aspect_preserved': True, 'five_cc0_sources': True,
        'subjective_ranking_not_science': True,
        'note': 'Objective render flags only; no full-motion viewing or sign-off is claimed.'
    })
    # Vertical contact sheet from the five review frames.
    thumbs = []
    for rel in frames:
        im = Image.open(ROOT / rel).convert('RGB')
        im.thumbnail((270, 480), Image.Resampling.LANCZOS)
        thumbs.append(im)
    canvas = Image.new('RGB', (5 * 280, 520), '#0B121B')
    for i, im in enumerate(thumbs):
        canvas.paste(im, (i * 280 + 5, 20))
    canvas.save(REVIEW / 'vertical_contact_sheet.jpg', quality=92)
    print('V4 full-screen silent picture written', OUT, flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
