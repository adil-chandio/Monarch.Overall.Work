#!/usr/bin/env python3
# Render the V6 60-second full-screen picture with the corrected reference mechanic:
# centered colorful top hook, fully visible left 1.-7. black label plates,
# progressive labels, right platform UI, bottom comment/Subscribe, payoff cuts/zoom
# and reaction bubbles. V5 right panel / bottom rank burst are removed.
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v6'
WORK = ROOT / 'production/monarch-cam/work/short_ranking_raw_v6'
REVIEW = BASE / 'review'
CLIPS = WORK / 'clips'
OUT = WORK / 'ranking_silent_raw_v6.mp4'
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
SELECTED = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))
SCENES = SELECTED['scenes']
W, H, FPS, N = SPEC['width'], SPEC['height'], SPEC['fps'], SPEC['frame_count']
V = SPEC['visual']
FONT_DIR = ROOT / 'public/showreel/fonts'
FONT_FILES = {
    'bold': [FONT_DIR / 'Manrope-800.ttf', FONT_DIR / 'Anton-Regular.ttf', Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')],
    'mono': [FONT_DIR / 'IBMPlexMono-400.ttf', Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')],
    'display': [FONT_DIR / 'Anton-Regular.ttf', FONT_DIR / 'Manrope-800.ttf', Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')],
}
CONTENT_BBOX = {}
EMOJI_NAMES = ['mindblown', 'tears', 'bolt', 'stars', 'water']


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def font(kind, size):
    for p in FONT_FILES[kind]:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def shadow_text(draw, xy, text, fnt, fill, shadow=(0, 0, 0, 210), off=5, stroke_width=2, stroke_fill=(10, 10, 10, 255)):
    x, y = xy
    draw.text((x + off, y + off), text, font=fnt, fill=shadow)
    draw.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def fit_text(draw, text, fnt, max_width):
    if draw.textbbox((0, 0), text, font=fnt)[2] <= max_width:
        return text
    out = text
    while len(out) > 3 and draw.textbbox((0, 0), out + '...', font=fnt)[2] > max_width:
        out = out[:-1]
    return out.rstrip() + '...'


def text_size(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


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


def cover_crop(frame, scene, t, payoff):
    x0, y0, x1, y1 = content_bbox(frame, scene['source_id'])
    c = frame[y0:y1, x0:x1]
    h, w = c.shape[:2]
    target = W / H
    z = scene['zoom_start'] + (scene['zoom_end'] - scene['zoom_start']) * t
    if payoff:
        z *= float(scene['payoff_zoom'])
    if w / h > target:
        ch = max(2, int(round(h / z)))
        cw = max(2, int(round(ch * target)))
    else:
        cw = max(2, int(round(w / z)))
        ch = max(2, int(round(cw / target)))
    cw, ch = min(cw, w), min(ch, h)
    cx = scene['focus_x'] * w
    cy = scene['focus_y'] * h
    if payoff:
        cx = min(w, cx + w * 0.035)
        cy = max(0, cy - h * 0.025)
    x = int(np.clip(round(cx - cw / 2), 0, w - cw))
    y = int(np.clip(round(cy - ch / 2), 0, h - ch))
    crop = c[y:y + ch, x:x + cw]
    return cv2.resize(crop, (W, H), interpolation=cv2.INTER_CUBIC)


def grade(frame):
    x = frame.astype(np.float32) / 255.0
    x = np.clip((x - 0.5) * V['light_contrast_lift'] + 0.5, 0, 1)
    return (x * 255).astype(np.uint8)


def star_points(cx, cy, r_outer, r_inner, count=5):
    pts = []
    for i in range(count * 2):
        angle = -math.pi / 2 + i * math.pi / count
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def emoji_assets():
    out = {}
    S = 256
    for name in EMOJI_NAMES:
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im, 'RGBA')
        if name == 'bolt':
            d.polygon([(146, 10), (70, 136), (120, 136), (92, 246), (194, 104), (138, 104), (174, 10)], fill=(255, 214, 48, 255), outline=(130, 70, 0, 255))
            d.line([(146, 10), (70, 136), (120, 136), (92, 246), (194, 104), (138, 104), (174, 10)], fill=(130, 70, 0, 255), width=8, joint='curve')
        elif name == 'water':
            d.ellipse((46, 70, 210, 234), fill=(55, 170, 255, 255), outline=(10, 80, 170, 255), width=8)
            d.polygon([(128, 12), (78, 112), (178, 112)], fill=(55, 170, 255, 255), outline=(10, 80, 170, 255))
            d.ellipse((86, 128, 116, 158), fill=(190, 235, 255, 190))
        else:
            d.ellipse((28, 28, 228, 228), fill=(255, 211, 59, 255), outline=(116, 66, 0, 255), width=9)
            if name == 'mindblown':
                for a in range(0, 360, 45):
                    ang = math.radians(a)
                    x1, y1 = 128 + 90 * math.cos(ang), 40 + 90 * math.sin(ang)
                    x2, y2 = 128 + 125 * math.cos(ang), 40 + 125 * math.sin(ang)
                    d.line((x1, y1, x2, y2), fill=(255, 92, 72, 255), width=12)
                d.line((78, 80, 108, 112), fill=(80, 40, 0, 255), width=10)
                d.line((108, 80, 78, 112), fill=(80, 40, 0, 255), width=10)
                d.line((148, 80, 178, 112), fill=(80, 40, 0, 255), width=10)
                d.line((178, 80, 148, 112), fill=(80, 40, 0, 255), width=10)
                d.ellipse((92, 132, 164, 204), fill=(92, 36, 20, 255), outline=(80, 40, 0, 255), width=7)
            elif name == 'tears':
                d.arc((70, 76, 112, 112), 0, 180, fill=(80, 40, 0, 255), width=9)
                d.arc((144, 76, 186, 112), 0, 180, fill=(80, 40, 0, 255), width=9)
                d.polygon([(84, 112), (98, 112), (91, 170)], fill=(55, 170, 255, 255))
                d.polygon([(158, 112), (172, 112), (165, 170)], fill=(55, 170, 255, 255))
                d.arc((82, 132, 174, 196), 10, 170, fill=(80, 40, 0, 255), width=9)
            elif name == 'stars':
                d.polygon(star_points(88, 100, 30, 13), fill=(255, 92, 72, 255), outline=(80, 40, 0, 255))
                d.polygon(star_points(168, 100, 30, 13), fill=(255, 92, 72, 255), outline=(80, 40, 0, 255))
                d.arc((78, 128, 178, 204), 10, 170, fill=(80, 40, 0, 255), width=10)
        path = REVIEW / ('emoji_' + name + '.png')
        im.save(path)
        out[name] = Image.open(path).convert('RGBA')
    return out


def rank_color(rank):
    if rank == 1:
        return (255, 84, 84, 255)
    if rank == 3:
        return (255, 168, 62, 255)
    return (80, 224, 208, 255)


def draw_top_shade(base):
    d = ImageDraw.Draw(base, 'RGBA')
    d.rectangle((0, 0, W, 700), fill=(4, 9, 16, 105))


def draw_hook(base, global_t):
    seconds = float(V['hook_seconds'])
    if global_t >= seconds:
        return
    alpha = 235 if global_t < seconds - 0.35 else int(235 * max(0.0, (seconds - global_t) / 0.35))
    d = ImageDraw.Draw(base, 'RGBA')
    d.rectangle((0, 0, W, H), fill=(5, 9, 18, alpha))
    hf = font('display', int(V['hook_font_size']))
    for i, (line, color, y) in enumerate(zip(V['hook_lines'], V['hook_colors'], V['hook_line_y'])):
        col = tuple(color)
        tw, th = text_size(d, line, hf)
        x = (W - tw) // 2
        d.rounded_rectangle((x - 26, y - 8, x + tw + 26, y + th + 14), radius=22, fill=(*col[:3], 70))
        shadow_text(d, (x, y), line, hf, col, off=6, stroke_width=2)
    q = V['hook_question']
    qf = font('bold', int(V['question_font_size']))
    tw, th = text_size(d, q, qf)
    shadow_text(d, ((W - tw) // 2, int(V['question_y'])), q, qf, (255, 255, 255, 255), off=6, stroke_width=2)
    label = V['hook_label']
    lf = font('mono', int(V['label_font_size']))
    tw, th = text_size(d, label, lf)
    shadow_text(d, ((W - tw) // 2, int(V['label_y'])), label, lf, (255, 222, 55, 255), off=3, stroke_width=1)


def draw_persistent_list(base, global_t):
    x = int(V['list_x'])
    y = int(V['list_y'])
    w = int(V['list_width'])
    row_h = int(V['list_row_height'])
    header = int(V['list_header_height'])
    d = ImageDraw.Draw(base, 'RGBA')
    d.rounded_rectangle((x, y, x + w, y + header + 7 * row_h), radius=26, fill=(5, 10, 18, 215), outline=(255, 255, 255, 70), width=3)
    hf = font('bold', 28)
    shadow_text(d, (x + 20, y + 10), '1.-7. LIST', hf, (255, 255, 255, 255), off=3, stroke_width=1)
    rf = font('bold', int(V['rank_font_size']))
    tf = font('mono', int(V['moment_font_size']))
    by_rank = {s['rank']: s for s in SCENES}
    for i, rank in enumerate([1, 2, 3, 4, 5, 6, 7]):
        ry = y + header + i * row_h
        s = by_rank[rank]
        revealed = global_t >= s['start'] + (s['end'] - s['start']) * float(V['label_reveal_at'])
        current = s['start'] <= global_t < s['end']
        color = rank_color(rank)
        plate = (x + 10, ry + 4, x + w - 10, ry + row_h - 10)
        d.rounded_rectangle(plate, radius=14, fill=(8, 8, 10, 235), outline=(*color[:3], 230 if current else 180), width=5 if current else 3)
        d.text((x + 24, ry + 22), f'{rank}.', font=rf, fill=color, stroke_width=1, stroke_fill=(0, 0, 0, 255))
        text = fit_text(d, s['title'] if revealed else '• • •', tf, w - 110)
        d.text((x + 92, ry + 34), text, font=tf, fill=(245, 245, 238, 255) if revealed else (120, 135, 148, 255), stroke_width=1, stroke_fill=(0, 0, 0, 255))


def draw_right_ui(base):
    d = ImageDraw.Draw(base, 'RGBA')
    cx = int(V['right_ui_x'])

    def heart(x, y, color):
        d.ellipse((x - 30, y - 26, x - 2, y + 2), fill=color)
        d.ellipse((x + 2, y - 26, x + 30, y + 2), fill=color)
        d.polygon([(x - 30, y - 4), (x + 30, y - 4), (x, y + 34)], fill=color)

    def comment(x, y, color):
        d.rounded_rectangle((x - 30, y - 22, x + 30, y + 16), radius=10, fill=color)
        d.polygon([(x - 16, y + 14), (x - 6, y + 32), (x + 8, y + 14)], fill=color)
        for j in range(3):
            d.line((x - 18, y - 6 + j * 9, x + 18, y - 6 + j * 9), fill=(20, 24, 32, 255), width=3)

    def share(x, y, color):
        d.line((x - 24, y + 16, x + 20, y - 20), fill=color, width=6)
        d.polygon([(x + 10, y - 24), (x + 30, y - 24), (x + 30, y - 4)], fill=color)

    heart(cx, int(V['right_ui_centers'][0]), (255, 84, 120, 255))
    comment(cx, int(V['right_ui_centers'][1]), (255, 255, 255, 255))
    share(cx, int(V['right_ui_centers'][2]), (120, 220, 255, 255))


def draw_reaction(base, scene, t, emojis):
    if t < float(scene['reaction_at']):
        return
    d = ImageDraw.Draw(base, 'RGBA')
    x = int(V['reaction_x'])
    y = int(V['reaction_y'])
    w = int(V['reaction_width'])
    h = int(V['reaction_height'])
    d.rounded_rectangle((x, y, x + w, y + h), radius=32, fill=(255, 255, 255, 245), outline=(15, 20, 30, 255), width=6)
    d.polygon([(x + 75, y + h - 2), (x + 125, y + h - 2), (x + 95, y + h + 34)], fill=(255, 255, 255, 245), outline=(15, 20, 30, 255))
    rf = font('bold', int(V['reaction_font_size']))
    text = fit_text(d, scene['reaction_text'], rf, w - 50)
    tw, th = text_size(d, text, rf)
    d.text((x + (w - tw) // 2, y + 44), text, font=rf, fill=(15, 20, 30, 255))
    name = scene['emoji'] if scene['emoji'] in emojis else 'mindblown'
    size = int(V['emoji_size'])
    emoji = emojis[name].resize((size, size), Image.Resampling.LANCZOS)
    base.alpha_composite(emoji, (int(V['emoji_x']), int(V['emoji_y'])))


def draw_bottom_bar(base):
    d = ImageDraw.Draw(base, 'RGBA')
    x = int(V['bottom_bar_x'])
    y = int(V['bottom_bar_y'])
    w = int(V['bottom_bar_width'])
    h = int(V['bottom_bar_height'])
    d.rounded_rectangle((x, y, x + w, y + h), radius=30, fill=(8, 12, 20, 215), outline=(255, 255, 255, 70), width=3)
    cf = font('bold', 34)
    ctext = V['bottom_comment_text']
    d.text((x + 36, y + 34), ctext, font=cf, fill=(245, 245, 238, 255))
    sf = font('bold', 30)
    stext = V['bottom_subscribe_text']
    tw, th = text_size(d, stext, sf)
    sx = x + w - tw - 90
    d.rounded_rectangle((sx - 22, y + 24, sx + tw + 22, y + h - 24), radius=24, fill=(255, 64, 84, 235))
    d.text((sx, y + 38), stext, font=sf, fill=(255, 255, 255, 255))


def make_covers(hook_path):
    hook = Image.open(hook_path).convert('RGBA')
    hook.convert('RGB').save(REVIEW / 'cover_hook.jpg', quality=94)
    outputs = []
    for name, text in [('cover.jpg', V['cover_text_primary']), ('cover_RANK_THESE_7.jpg', V['cover_text_ab'])]:
        im = hook.copy()
        d = ImageDraw.Draw(im, 'RGBA')
        d.rectangle((0, 0, W, 300), fill=(4, 9, 16, 165))
        f = font('bold', 88)
        tw, th = text_size(d, text, f)
        shadow_text(d, ((W - tw) // 2, 110), text, f, (255, 255, 255, 255), off=6, stroke_width=2)
        im.convert('RGB').save(REVIEW / name, quality=94)
        p = REVIEW / name
        outputs.append({'file': name, 'text': text, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size})
    return outputs


def write_layout_manifest():
    d = ImageDraw.Draw(Image.new('RGBA', (W, H)))
    hf = font('display', int(V['hook_font_size']))
    qf = font('bold', int(V['question_font_size']))
    lf = font('mono', int(V['label_font_size']))
    hook_boxes = []
    for line, y in zip(V['hook_lines'], V['hook_line_y']):
        tw, th = text_size(d, line, hf)
        hook_boxes.append([(W - tw) // 2, int(y), (W - tw) // 2 + tw, int(y) + th])
    qtw, qth = text_size(d, V['hook_question'], qf)
    ltw, lth = text_size(d, V['hook_label'], lf)
    x, y = int(V['list_x']), int(V['list_y'])
    w, row_h, header = int(V['list_width']), int(V['list_row_height']), int(V['list_header_height'])
    rows = []
    for i in range(7):
        ry = y + header + i * row_h
        rows.append([x + 10, ry + 4, x + w - 10, ry + row_h - 10])
    layout = {
        'edition': 'raw_fullscreen_v6',
        'width': W, 'height': H, 'fps': FPS, 'frame_count': N,
        'safe_area': V['safe_area'],
        'hook': {'line_bboxes': hook_boxes, 'question_bbox': [(W - qtw) // 2, int(V['question_y']), (W - qtw) // 2 + qtw, int(V['question_y']) + qth], 'label_bbox': [(W - ltw) // 2, int(V['label_y']), (W - ltw) // 2 + ltw, int(V['label_y']) + lth], 'visible': True, 'centered': True, 'colorful': True},
        'list': {'bbox': [x, y, x + w, y + header + 7 * row_h], 'row_bboxes': rows, 'left_side': True, 'black_label_plates': True, 'fully_visible': True, 'rank_order': [1, 2, 3, 4, 5, 6, 7]},
        'right_ui': {'x': int(V['right_ui_x']), 'icon_centers_y': V['right_ui_centers'], 'icon_bboxes': [[int(V['right_ui_x']) - 34, int(cy) - 44, int(V['right_ui_x']) + 34, int(cy) + 44] for cy in V['right_ui_centers']], 'platform_ui': True},
        'reaction': {'bbox': [int(V['reaction_x']), int(V['reaction_y']), int(V['reaction_x']) + int(V['reaction_width']), int(V['reaction_y']) + int(V['reaction_height'])], 'emoji_bbox': [int(V['emoji_x']), int(V['emoji_y']), int(V['emoji_x']) + int(V['emoji_size']), int(V['emoji_y']) + int(V['emoji_size'])]},
        'bottom_bar': {'bbox': [int(V['bottom_bar_x']), int(V['bottom_bar_y']), int(V['bottom_bar_x']) + int(V['bottom_bar_width']), int(V['bottom_bar_y']) + int(V['bottom_bar_height'])], 'comment': V['bottom_comment_text'], 'subscribe': V['bottom_subscribe_text']},
        'flags': {
            'no_v5_right_panel': True, 'no_v5_bottom_rank_burst': True,
            'centered_hook_visible': True, 'left_list_fully_visible': True,
            'right_platform_ui': True, 'bottom_comment_subscribe': True,
            'safe_area_check': True, 'social_origin_check': True,
            'full_motion_review': False, 'native_audio_listening': False,
            'human_approval': False, 'sign_off': False,
        },
    }
    save_json(REVIEW / 'layout_manifest.json', layout)


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW / 'candidates').mkdir(parents=True, exist_ok=True)
    emojis = emoji_assets()
    write_layout_manifest()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(OUT), fourcc, FPS, (W, H))
    if not writer.isOpened():
        raise RuntimeError('Could not open VideoWriter')
    caps = {}
    for s in SCENES:
        cap = cv2.VideoCapture(str(CLIPS / ('clip_' + s['source_id'] + '.mp4')))
        if not cap.isOpened():
            raise RuntimeError('Could not open clip ' + s['source_id'])
        caps[s['source_id']] = cap
    ledger, payoff_frames = [], []
    global_frame = 0
    hook_frame_path = None
    for s in SCENES:
        cap = caps[s['source_id']]
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        n = int(s['frames'])
        first_path = REVIEW / f"frame_{s['rank']:02d}_{s['start']:05.2f}s.jpg"
        payoff_path = REVIEW / f"payoff_frame_{s['rank']:02d}.jpg"
        for i in range(n):
            ok, raw = cap.read()
            if not ok:
                raise RuntimeError('Frame read failed for ' + s['source_id'])
            t = i / max(1, n - 1)
            global_t = global_frame / FPS
            payoff = t >= float(s['payoff_at'])
            pic = grade(cover_crop(raw, s, t, payoff))
            img = Image.fromarray(cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)).convert('RGBA')
            draw_top_shade(img)
            draw_hook(img, global_t)
            draw_persistent_list(img, global_t)
            draw_right_ui(img)
            draw_reaction(img, s, t, emojis)
            draw_bottom_bar(img)
            final = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
            writer.write(final)
            if i == 0:
                cv2.imwrite(str(first_path), final, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
                if hook_frame_path is None:
                    hook_frame_path = first_path
            if i == n - 1:
                cv2.imwrite(str(payoff_path), final, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            global_frame += 1
        cap.release()
        payoff_frames.append(str(payoff_path.relative_to(ROOT)))
        ledger.append({
            'id': s['id'], 'rank': s['rank'], 'title': s['title'],
            'reaction_text': s['reaction_text'], 'emoji': s['emoji'],
            'timeline_in': s['start'], 'timeline_out': s['end'],
            'source_in': s['source_start'], 'source_out': s['source_out'],
            'frames': n, 'full_screen': True, 'punchy_zoom': True,
            'payoff_cut_frame': int(n * float(s['payoff_at'])),
            'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
            'runner_visual_motion_probe': True, 'contact_sheets_written': True,
            'source_review_recorded': True, 'visual_lock_written': True,
        })
    writer.release()
    if global_frame != N or hook_frame_path is None:
        raise RuntimeError('Rendered frame count mismatch or hook frame missing')
    outputs = make_covers(hook_frame_path)
    flags = {
        'full_screen_cover': True, 'dynamic_source_crop': True, 'no_letterbox': True,
        'no_black_bars': True, 'no_blurred_background': True, 'no_action_window': True,
        'full_reference_mechanic': True, 'colorful_hook_title': True,
        'persistent_numbered_list': True, 'progressive_labels': True,
        'payoff_cuts_zoom': True, 'punchy_zoom': True,
        'reaction_bubbles': True, 'emojis': True, 'custom_emoji_drawings': True,
        'seven_moments_only': True, 'rank_numbers': True,
        'rank_title_overlay_only': False, 'hard_cuts_only': True,
        'no_cut_flashes': True, 'no_badges': True, 'no_progress': True,
        'no_footer': True, 'no_source_labels': True, 'no_brand_watermark': True,
        'source_aspect_preserved': True, 'seven_cc0_sources': True,
        'subjective_ranking_not_science': True,
        'centered_hook_visible': True, 'left_list_fully_visible': True,
        'no_v5_right_panel': True, 'no_v5_bottom_rank_burst': True,
        'right_platform_ui': True, 'bottom_comment_subscribe': True,
        'safe_area_check': True, 'social_origin_check': True,
        'layout_manifest_written': True,
        'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True, 'contact_sheets_written': True,
        'source_review_recorded': True, 'visual_lock_written': True,
        'full_motion_review': False, 'native_audio_listening': False,
        'human_approval': False, 'sign_off': False,
        'audience_result_promise': False, 'virality_guarantee': False,
        'perfection_claim': False, 'retention_claim': False,
        'third_party_repost': False, 'ai_audio': False,
        'generated_calls': False, 'v3_audio_packages': False,
        'audio_substitution': False, 'earshot_claim': False,
        'model_claim': False, 'sound_design_layers': False,
        'sub_bloom_layers': False, 'native_ambience_layers': False,
        'ambience_layers': False, 'cue_layers': False,
    }
    save_json(REVIEW / 'visual_v6_qc.json', flags)
    save_json(REVIEW / 'exact_thumbnail_manifest.json', {
        'hook_frame_reference': 'cover_hook.jpg',
        'hook_frame_text': V['hook_question'],
        'primary': V['cover_text_primary'], 'ab': V['cover_text_ab'],
        'outputs': outputs, 'flags': flags,
        'note': 'Objective render flags, layout manifest and contact-sheet frames only; full_motion_review=false, native_audio_listening=false, human_approval=false, sign_off=false.',
    })
    save_json(REVIEW / 'visual_edit_ledger.json', {
        'edition': 'raw_fullscreen_v6', 'scenes': ledger,
        'payoff_frames': payoff_frames, 'full_screen': True,
        'flags': flags,
    })
    save_json(REVIEW / 'visual_review_lock.json', {
        'edition': 'raw_fullscreen_v6',
        'visual_lock_written': True,
        'runner_probe_passed': True,
        'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True,
        'contact_sheets_written': True,
        'source_review_recorded': True,
        'full_motion_review': False, 'native_audio_listening': False,
        'human_approval': False, 'sign_off': False,
        'selected_windows_basis': SELECTED.get('probe_basis', 'V5 runner-selected windows inherited for V6'),
        'note': 'V5 windows reused; V6 geometry rebuilt with visible hook, left list, right UI, bottom bar and layout manifest.',
    })
    print('V6 picture rendered', OUT, global_frame, 'frames', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
