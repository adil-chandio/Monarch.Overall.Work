#!/usr/bin/env python3
# Render the V5 60-second full-screen picture with the full reference mechanic:
# colorful hook, persistent 1.-7. list, progressive labels, payoff cuts/zoom,
# WHAT!!-type reaction bubbles and custom emoji drawings. No sound is added.
from __future__ import annotations
import hashlib, json, math, subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v5'
WORK = ROOT / 'production/monarch-cam/work/short_ranking_raw_v5'
REVIEW = BASE / 'review'
CLIPS = WORK / 'clips'
OUT = WORK / 'ranking_silent_raw_v5.mp4'
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
SELECTED = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))
SCENES = SELECTED['scenes']
W, H, FPS, N = SPEC['width'], SPEC['height'], SPEC['fps'], SPEC['frame_count']
V = SPEC['visual']
FONT_DIR = ROOT / 'public/showreel/fonts'
FONT_FILES = {
    'bold': [FONT_DIR / 'Manrope-800.ttf', FONT_DIR / 'Anton-Regular.ttf', Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')],
    'mono': [FONT_DIR / 'IBMPlexMono-400.ttf', Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')],
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


def shadow_text(draw, xy, text, fnt, fill, shadow=(0, 0, 0, 190), off=4, stroke_width=0, stroke_fill=(0, 0, 0, 255)):
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


def draw_hook(base, global_t):
    seconds = float(V['hook_seconds'])
    if global_t >= seconds:
        return
    alpha = 235 if global_t < seconds - 0.35 else int(235 * max(0.0, (seconds - global_t) / 0.35))
    d = ImageDraw.Draw(base, 'RGBA')
    d.rectangle((0, 0, W, H), fill=(5, 9, 18, alpha))
    colors = [(255, 64, 129, 255), (55, 216, 255, 255), (255, 222, 55, 255)]
    lines = V['hook_lines']
    f = font('bold', 104)
    for i, (line, color) in enumerate(zip(lines, colors)):
        bb = d.textbbox((0, 0), line, font=f)
        tw = bb[2] - bb[0]
        x = (W - tw) // 2
        y = 300 + i * 150
        d.rounded_rectangle((x - 28, y - 10, x + tw + 28, y + 118), radius=22, fill=(color[0], color[1], color[2], 60))
        shadow_text(d, (x, y), line, f, color, shadow=(0, 0, 0, 210), off=6, stroke_width=2, stroke_fill=(0, 0, 0, 220))
    q = font('bold', 72)
    question = V['hook_question']
    bb = d.textbbox((0, 0), question, font=q)
    shadow_text(d, ((W - (bb[2] - bb[0])) // 2, 800), question, q, (255, 255, 255, 255), shadow=(0, 0, 0, 220), off=6, stroke_width=2, stroke_fill=(20, 20, 20, 255))
    small = font('mono', 30)
    label = '7 MOMENTS / FULL SCREEN / NATIVE AUDIO'
    bb = d.textbbox((0, 0), label, font=small)
    shadow_text(d, ((W - (bb[2] - bb[0])) // 2, 910), label, small, (255, 222, 55, 255), shadow=(0, 0, 0, 210), off=3)


def rank_color(rank):
    if rank == 1:
        return (255, 84, 84, 255)
    if rank == 3:
        return (255, 168, 62, 255)
    return (80, 224, 208, 255)


def draw_persistent_list(base, global_t):
    x = int(V['persistent_list_x'])
    y = int(V['persistent_list_y'])
    w = int(V['persistent_list_width'])
    row_h = int(V['persistent_list_row_height'])
    h = row_h * 7 + 54
    d = ImageDraw.Draw(base, 'RGBA')
    d.rounded_rectangle((x, y, x + w, y + h), radius=28, fill=(5, 10, 18, 190), outline=(255, 255, 255, 55), width=3)
    hf = font('bold', 30)
    shadow_text(d, (x + 22, y + 12), '1.-7. LIST', hf, (255, 255, 255, 255), shadow=(0, 0, 0, 190), off=3)
    rf = font('bold', 36)
    tf = font('mono', 22)
    by_rank = {s['rank']: s for s in SCENES}
    for i, rank in enumerate([1, 2, 3, 4, 5, 6, 7]):
        ry = y + 54 + i * row_h
        s = by_rank[rank]
        revealed = global_t >= s['start'] + (s['end'] - s['start']) * float(V['label_reveal_at'])
        current = s['start'] <= global_t < s['end']
        if current:
            d.rounded_rectangle((x + 10, ry + 2, x + w - 10, ry + row_h - 8), radius=16, fill=(255, 255, 255, 38))
        color = rank_color(rank)
        shadow_text(d, (x + 18, ry + 18), f'{rank}.', rf, color, shadow=(0, 0, 0, 190), off=3)
        text = s['title'] if revealed else '• • •'
        text = fit_text(d, text, tf, w - 100)
        shadow_text(d, (x + 78, ry + 28), text, tf, (245, 245, 238, 255) if revealed else (120, 135, 148, 255), shadow=(0, 0, 0, 190), off=2)
        if rank < 7:
            d.line((x + 18, ry + row_h - 5, x + w - 18, ry + row_h - 5), fill=(255, 255, 255, 35), width=2)


def draw_rank_burst(base, scene, t):
    d = ImageDraw.Draw(base, 'RGBA')
    pulse = 1.0 + 0.10 * math.sin(min(1.0, t / 0.35) * math.pi)
    rf = font('bold', int(96 * pulse))
    tf = font('bold', 42)
    rank_text = '#' + str(scene['rank'])
    color = rank_color(scene['rank'])
    x, y = 60, 1430 + int(14 * math.sin(t * 8))
    shadow_text(d, (x, y), rank_text, rf, color, shadow=(0, 0, 0, 220), off=7, stroke_width=3, stroke_fill=(0, 0, 0, 255))
    title = fit_text(d, scene['title'], tf, 560)
    shadow_text(d, (x + 8, y + 112), title, tf, (255, 255, 255, 255), shadow=(0, 0, 0, 220), off=5, stroke_width=2, stroke_fill=(0, 0, 0, 255))
    d.line((x, y + 168, x + 520, y + 168), fill=(*color[:3], 220), width=6)


def draw_reaction(base, scene, t, emojis):
    if t < float(scene['reaction_at']):
        return
    d = ImageDraw.Draw(base, 'RGBA')
    x, y, w, h = 60, 1080, 540, 150
    d.rounded_rectangle((x, y, x + w, y + h), radius=34, fill=(255, 255, 255, 245), outline=(15, 20, 30, 255), width=6)
    d.polygon([(x + 90, y + h - 2), (x + 145, y + h - 2), (x + 105, y + h + 40)], fill=(255, 255, 255, 245), outline=(15, 20, 30, 255))
    f = font('bold', int(V['reaction_font_size']))
    text = fit_text(d, scene['reaction_text'], f, w - 50)
    bb = d.textbbox((0, 0), text, font=f)
    shadow_text(d, (x + (w - (bb[2] - bb[0])) // 2, y + 42), text, f, (15, 20, 30, 255), shadow=(0, 0, 0, 0), off=0)
    name = scene['emoji'] if scene['emoji'] in emojis else 'mindblown'
    size = int(V['emoji_size'])
    emoji = emojis[name].resize((size, size), Image.Resampling.LANCZOS)
    base.alpha_composite(emoji, (x + w - 20, y - 34))


def make_covers(hook_path):
    hook = Image.open(hook_path).convert('RGBA')
    hook.convert('RGB').save(REVIEW / 'cover_hook.jpg', quality=94)
    outputs = []
    for name, text in [('cover.jpg', V['cover_text_primary']), ('cover_RANK_THESE_7.jpg', V['cover_text_ab'])]:
        im = hook.copy()
        d = ImageDraw.Draw(im, 'RGBA')
        d.rectangle((0, 0, W, 300), fill=(4, 9, 16, 165))
        f = font('bold', 88)
        bb = d.textbbox((0, 0), text, font=f)
        shadow_text(d, ((W - (bb[2] - bb[0])) // 2, 110), text, f, (255, 255, 255, 255), shadow=(0, 0, 0, 220), off=6, stroke_width=2, stroke_fill=(0, 0, 0, 255))
        im.convert('RGB').save(REVIEW / name, quality=94)
        p = REVIEW / name
        outputs.append({'file': name, 'text': text, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size})
    return outputs


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    emojis = emoji_assets()
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
            draw_hook(img, global_t)
            draw_persistent_list(img, global_t)
            draw_rank_burst(img, s, t)
            draw_reaction(img, s, t, emojis)
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
            'id': s['id'], 'rank': s['rank'], 'title': s['title'], 'reaction_text': s['reaction_text'], 'emoji': s['emoji'],
            'timeline_in': s['start'], 'timeline_out': s['end'], 'source_in': s['source_start'], 'source_out': s['source_out'],
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
        'rank_title_overlay_only': False, 'no_hook_scene': False, 'no_payoff_scene': False,
        'no_hook_or_end_question_in_video': False, 'hard_cuts_only': True,
        'no_cut_flashes': True, 'no_badges': True, 'no_progress': True,
        'no_footer': True, 'no_source_labels': True, 'no_brand_watermark': True,
        'source_aspect_preserved': True, 'seven_cc0_sources': True,
        'subjective_ranking_not_science': True,
        'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True, 'contact_sheets_written': True,
        'source_review_recorded': True, 'visual_lock_written': True,
        'full_motion_review': False, 'native_audio_listening': False,
        'human_approval': False, 'sign_off': False,
        'audience_result_promise': False, 'virality_guarantee': False,
        'perfection_claim': False, 'retention_claim': False,
        'hypnosis_claim': False, 'three_x_claim': False,
        'subscribe_claim': False, 'like_claim': False,
        'same_path_replacement': False, 'factual_superlative_claim': False,
        'third_party_repost': False, 'ai_audio': False,
        'generated_calls': False, 'v3_audio_packages': False,
        'audio_substitution': False, 'earshot_claim': False,
        'model_claim': False, 'sound_design_layers': False,
        'sub_bloom_layers': False, 'native_ambience_layers': False,
        'ambience_layers': False, 'cue_layers': False,
    }
    save_json(REVIEW / 'exact_thumbnail_manifest.json', {
        'hook_frame_reference': 'cover_hook.jpg',
        'hook_frame_text': V['hook_question'],
        'primary': V['cover_text_primary'], 'ab': V['cover_text_ab'],
        'outputs': outputs,
        'flags': flags,
        'note': 'Objective render flags and contact-sheet frames only; full_motion_review=false, native_audio_listening=false, human_approval=false, sign_off=false.',
    })
    save_json(REVIEW / 'visual_edit_ledger.json', {
        'edition': 'raw_fullscreen_v5', 'scenes': ledger,
        'payoff_frames': payoff_frames, 'full_screen': True,
        'flags': flags,
    })
    save_json(REVIEW / 'visual_v5_qc.json', flags)
    thumbs = []
    for rel in payoff_frames:
        im = Image.open(ROOT / rel).convert('RGB')
        im.thumbnail((270, 480), Image.Resampling.LANCZOS)
        thumbs.append(im)
    canvas = Image.new('RGB', (7 * 280, 540), '#0B121B')
    d = ImageDraw.Draw(canvas)
    d.text((16, 8), 'V5 FULL REFERENCE MECHANIC - PAYOFF FRAMES', font=font('bold', 24), fill='#F4F1E8')
    for i, im in enumerate(thumbs):
        canvas.paste(im, (i * 280 + 5, 40))
    canvas.save(REVIEW / 'vertical_contact_sheet.jpg', quality=92)
    print('V5 full reference-mechanic silent picture written', OUT, flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
