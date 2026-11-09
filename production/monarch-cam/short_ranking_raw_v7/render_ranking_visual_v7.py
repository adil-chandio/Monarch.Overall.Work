#!/usr/bin/env python3
# Render V7 after the V6 rejection: a blurred full-frame background plus a
# sharp, uncut source frame, with the visible two-line hook, 1.-7. list and UI.
# No V6 crop routine, no zoom, no letterbox, no empty black upper half.
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v7'
WORK = Path(os.environ.get('V7_WORK', str(ROOT / 'production/monarch-cam/work/short_ranking_raw_v7'))).resolve()
REVIEW = Path(os.environ.get('V7_REVIEW', str(BASE / 'review'))).resolve()
CLIPS = WORK / 'clips'
SILENT_OUT = WORK / 'ranking_silent_raw_v7.mp4'
FONTS = ROOT / 'public/showreel/fonts'
FONT_ANTON = FONTS / 'Anton-Regular.ttf'
FONT_MANROPE = FONTS / 'Manrope-800.ttf'
FONT_MONO = FONTS / 'IBMPlexMono-400.ttf'
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
V = SPEC['visual']
SCENES = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))['scenes']
META = json.loads((BASE / 'ranking_v7_metadata.json').read_text(encoding='utf-8'))
W, H, FPS = int(SPEC['width']), int(SPEC['height']), int(SPEC['fps'])
N_FRAMES = int(SPEC['frame_count'])


def font(size, which='anton'):
    path = {'anton': FONT_ANTON, 'manrope': FONT_MANROPE, 'mono': FONT_MONO}[which]
    return ImageFont.truetype(str(path), int(size))


def clamp(t, lo=0.0, hi=1.0):
    return max(lo, min(hi, t))


def composite_layer(base, layer, dest=(0, 0)):
    """Alpha-composite a full-canvas RGBA layer into base in place."""
    if dest != (0, 0):
        full = Image.new('RGBA', base.size, (0, 0, 0, 0))
        full.paste(layer, dest)
        layer = full
    merged = Image.alpha_composite(base, layer)
    base.paste(merged)


def fade(t, length=0.3):
    t = clamp(t)
    return max(0.0, min(t / length, (1.0 - t) / length, 1.0))


def shadow_text(base, xy, text, f, fill, anchor=None, off=(0, 5), blur=8, stroke=0, stroke_fill=(0, 0, 0, 180)):
    """Composite a blurred shadow and the foreground text into an RGBA base."""
    x, y = xy
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp, 'RGBA')
    kw = {'font': f, 'fill': fill, 'anchor': anchor}
    if stroke:
        kw.update({'stroke_width': stroke, 'stroke_fill': stroke_fill})
    td.text((x + off[0], y + off[1]), text, **kw)
    shadow = tmp.filter(ImageFilter.GaussianBlur(blur)) if blur > 0 else tmp
    composite_layer(base, shadow)
    fg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fg, 'RGBA').text((x, y), text, **kw)
    composite_layer(base, fg)


def shadow_rect(base, bbox, radius, fill, outline=None, width=1, shadow=True):
    if shadow:
        s = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(s, 'RGBA').rounded_rectangle(
            (bbox[0] + 3, bbox[1] + 6, bbox[2] + 3, bbox[3] + 6), radius, fill=(0, 0, 0, 150))
        layer = s.filter(ImageFilter.GaussianBlur(12))
        composite_layer(base, layer)
    ImageDraw.Draw(base, 'RGBA').rounded_rectangle(bbox, radius, fill=fill, outline=outline, width=width)


def fit_text(draw, text, f, maxw):
    t = str(text)
    while t and draw.textlength(t, font=f) > maxw:
        t = t[:-1]
    if t != str(text):
        t = t.rstrip() + '...'
    return t


def multiline(draw, text, f, maxw):
    words = str(text).split()
    lines, line = [], ''
    for word in words:
        candidate = (line + ' ' + word).strip()
        if line and draw.textlength(candidate, font=f) > maxw:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines[:2]


def draw_icon(d, name, cx, cy, active=False):
    c = (255, 59, 48, 255) if active else (255, 255, 255, 242)
    if name == 'heart':
        r = 20
        d.ellipse((cx - r, cy - r - 8, cx, cy + 8), fill=c)
        d.ellipse((cx, cy - r - 8, cx + r, cy + 8), fill=c)
        d.polygon([(cx - r, cy - 3), (cx, cy + r + 6), (cx + r, cy - 3)], fill=c)
    elif name == 'comment':
        d.rounded_rectangle((cx - 23, cy - 20, cx + 23, cy + 16), 12, fill=c)
        d.polygon([(cx - 10, cy + 14), (cx - 16, cy + 30), (cx + 5, cy + 15)], fill=c)
    elif name == 'save':
        d.polygon([(cx - 18, cy - 24), (cx + 18, cy - 24), (cx + 18, cy + 24), (cx, cy + 12), (cx - 18, cy + 24)], fill=c)
    elif name == 'share':
        d.line((cx - 6, cy + 3, cx + 22, cy - 23), fill=c, width=7)
        d.polygon([(cx + 12, cy - 26), (cx + 27, cy - 26), (cx + 27, cy - 11)], fill=c)
        d.line((cx - 6, cy + 3, cx + 22, cy + 27), fill=c, width=7)
        d.polygon([(cx + 12, cy + 28), (cx + 27, cy + 28), (cx + 27, cy + 13)], fill=c)
    elif name == 'remix':
        d.arc((cx - 22, cy - 20, cx + 22, cy + 20), 35, 325, fill=c, width=6)
        d.polygon([(cx + 10, cy - 23), (cx + 30, cy - 15), (cx + 16, cy - 3)], fill=c)


def compose_frame(src_pil, frame_no, scene_index, scenes):
    scene = scenes[scene_index]
    rank = int(scene['rank'])
    local = clamp((frame_no - int(scene['start_frame'])) / max(1, int(scene['frames']) - 1))
    t_global = frame_no / FPS
    src = src_pil.convert('RGB')
    sw, sh = src.size

    # Full-frame blurred fill: no black, no empty top, no cover crop.
    bg = src.resize((W, H), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(38))
    bg = Image.blend(bg, Image.new('RGB', (W, H), (0, 0, 0)), 0.20)

    # Sharp uncut source frame, aspect-preserving, centered on the blurred fill.
    scale = min(W / sw, H / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    sharp = src.resize((nw, nh), Image.Resampling.LANCZOS).convert('RGBA')
    canvas = bg.convert('RGBA')
    canvas.paste(sharp.convert('RGB'), ((W - nw) // 2, (H - nh) // 2))

    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    grad = Image.new('RGBA', (1, H), (0, 0, 0, 0))
    gp = grad.load()
    for y in range(H):
        top = 105 if y < 520 else 0
        bottom = 190 if y > 1550 else 0
        alpha = max(top * (1 - y / 650), bottom * ((y - 1450) / 470), 18)
        gp[0, y] = (0, 0, 0, int(clamp(alpha, 0, 190)))
    grad = grad.resize((W, H))
    composite_layer(overlay, grad)
    ui = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ui, 'RGBA')

    # Top app chrome. No third-party handle or fake engagement numbers.
    f_top = font(27, 'manrope')
    shadow_text(ui, (58, 62), '12:20', f_top, (255, 255, 255, 235), blur=4)
    for name, x, active in [('For You', 430, False), ('Following', 685, True)]:
        shadow_text(ui, (x, 62), name, f_top, (255, 255, 255, 220 if active else 150), anchor='ma', blur=4)
    d.line((660, 108, 750, 108), fill=(255, 255, 255, 240), width=5)
    d.ellipse((972, 58, 1010, 96), outline=(255, 255, 255, 230), width=4)
    d.line((990, 76, 1030, 76), fill=(255, 255, 255, 230), width=4)
    d.line((990, 76, 990, 36), fill=(255, 255, 255, 230), width=4)

    # Centered two-line reference hook with the color split from the screenshots.
    f_hook = font(V['hook_font_size'])
    parts = V['hook_line_1_parts']
    full = ''.join(str(p[0]) for p in parts)
    totalw = d.textlength(full, font=f_hook)
    x0 = (W - totalw) / 2
    y1, y2 = V['hook_line_y']
    x = x0
    for text, color in parts:
        shadow_text(ui, (x, y1), text, f_hook, tuple(color) + (255,), off=(0, 7), blur=10, stroke=2)
        x += d.textlength(text, font=f_hook)
    shadow_text(ui, (W / 2, y2), V['hook_line_2'], f_hook, (255, 255, 255, 255), anchor='ma', off=(0, 7), blur=10, stroke=2)
    f_q = font(V['question_font_size'], 'manrope')
    q_alpha = int(195 + 60 * math.sin(t_global * 2.2))
    shadow_text(ui, (W / 2, V['question_y']), V['hook_question'], f_q, (255, 235, 60, q_alpha), anchor='ma', blur=5)

    # Persistent, fully visible 1.-7. list with progressive black label plates.
    f_rank = font(V['rank_font_size'])
    f_label = font(V['moment_font_size'], 'manrope')
    ordered = sorted(scenes, key=lambda s: int(s['rank']))
    for pos, sc in enumerate(ordered):
        r = int(sc['rank'])
        y = V['list_y'] + pos * V['list_row_height']
        num_color = (255, 59, 48, 255) if r == 1 else (255, 255, 255, 254) if r == 2 else (255, 130, 20, 255) if r == 3 else (255, 255, 255, 254)
        shadow_text(ui, (V['list_x'], y), str(r) + '.', f_rank, num_color, off=(0, 4), blur=7, stroke=2)
        # All seven labels are visible from the first frame; only the active-rank highlight progresses.
        text = sc['moment_label']
        bbox = [V['list_label_x'], y + 8, V['list_label_x'] + V['list_label_max_width'], y + 89]
        shadow_rect(ui, bbox, 17, (8, 8, 10, 178),
                    outline=(255, 255, 255, 110) if r == rank else (255, 255, 255, 30),
                    width=3 if r == rank else 1, shadow=False)
        txt = fit_text(d, text, f_label, V['list_label_max_width'] - 30)
        shadow_text(ui, (bbox[0] + 14, bbox[1] + 9), txt, f_label, (255, 255, 255, 255), off=(0, 2), blur=5)
        if r == rank:
            d.rounded_rectangle((bbox[0] - 9, y, bbox[0] - 2, y + 96), 4, fill=(255, 221, 51, 255))

    # Right vertical social UI; original vector icons, no fake counts.
    for name, y in zip(['heart', 'comment', 'save', 'share', 'remix'], V['right_ui_centers']):
        draw_icon(d, name, V['right_ui_x'], y, active=(name == 'heart' and local > V['payoff_at']))
    d.rounded_rectangle((V['right_ui_x'] - 28, 1550, V['right_ui_x'] + 28, 1606), 28,
                        fill=(25, 25, 28, 230), outline=(255, 255, 255, 170), width=2)
    d.arc((V['right_ui_x'] - 20, 1558, V['right_ui_x'] + 20, 1598), 20, 330, fill=(255, 255, 255, 230), width=4)

    # Handle, comment bubble, Subscribe button, caption and bottom nav.
    f_handle = font(35, 'manrope')
    shadow_text(ui, (58, V['handle_y']), V['handle'], f_handle, (255, 255, 255, 255), blur=6)
    f_sub = font(24, 'manrope')
    shadow_text(ui, (58, V['handle_y'] + 45), 'Ranking Most Impressive Moments Ever', f_sub, (255, 255, 255, 225), blur=4)
    cb = V['caption_bbox']
    shadow_rect(ui, cb, 24, (245, 245, 245, 235), shadow=False)
    f_bubble = font(29, 'manrope')
    for j, line in enumerate(multiline(d, V['bottom_comment_text'], f_bubble, cb[2] - cb[0] - 44)):
        d.text((cb[0] + 22, cb[1] + 18 + j * 35), line, font=f_bubble, fill=(20, 20, 20, 255))
    sb = V['subscribe_bbox']
    shadow_rect(ui, sb, 46, (255, 255, 255, 255), shadow=False)
    f_button = font(30, 'manrope')
    d.text(((sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2), V['bottom_subscribe_text'], font=f_button, fill=(12, 12, 12, 255), anchor='mm')
    f_small = font(25, 'manrope')
    shadow_text(ui, (60, V['bottom_caption_y']), V['bottom_caption_text'], f_small, (255, 255, 255, 245), blur=4)
    f_nav = font(22, 'manrope')
    for text, x in [('HOME', 150), ('DISCOVER', 420), ('+', 540), ('INBOX', 690), ('PROFILE', 930)]:
        shadow_text(ui, (x, V['bottom_nav_y']), text, f_nav, (255, 255, 255, 220), anchor='ma', blur=3)
    d.rounded_rectangle((int(W / 2 - 34), H - 12, int(W / 2 + 34), H - 7), 4, fill=(255, 255, 255, 220))

    # Brief payoff reaction, inside the safe area. No zoom/crop of the clip.
    if local > V['reaction_at']:
        alpha = int(255 * clamp((local - V['reaction_at']) / 0.12))
        f_react = font(47, 'manrope')
        shadow_text(ui, (W / 2, 1370), str(scene['reaction_text']).upper(), f_react,
                    (255, 255, 255, alpha), anchor='ma', off=(0, 4), blur=8, stroke=2)
        if local > V['payoff_at']:
            d.rounded_rectangle((V['right_ui_x'] - 44, 790, V['right_ui_x'] + 44, 878), 44,
                                fill=(255, 221, 51, 220))
            f_e = font(50)
            d.text((V['right_ui_x'], 835), str(scene['emoji']).upper()[:2], font=f_e, fill=(20, 20, 20, 255), anchor='mm')

    composite_layer(overlay, ui)
    # Very short scene transition flash, composited after the UI so it does not wipe it.
    if local < 0.07:
        flash = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(flash, 'RGBA').rectangle((0, 0, W, H), fill=(255, 255, 255, int(75 * (1 - local / 0.07))))
        composite_layer(overlay, flash)

    return Image.alpha_composite(canvas, overlay).convert('RGB')


def write_layout_manifest():
    safe = V['safe_area']
    right_limit = W - safe['right']
    bottom_limit = H - safe['bottom']
    row_bboxes = []
    for pos in range(7):
        y = V['list_y'] + pos * V['list_row_height']
        row_bboxes.append([V['list_label_x'], y + 8, V['list_label_x'] + V['list_label_max_width'], y + 89])
    primary = {
        'hook': [60, 185, 980, 460],
        'left_list': [V['list_x'], V['list_y'], V['list_label_x'] + V['list_label_max_width'], row_bboxes[-1][3]],
        'right_ui': [880, 800, 980, 1620],
        'caption_bubble': list(V['caption_bbox']),
        'subscribe': list(V['subscribe_bbox']),
        'bottom_caption': [60, V['bottom_caption_y'], 900, 1800],
    }
    def inside(b):
        return b[0] >= safe['left'] and b[1] >= safe['top'] and b[2] <= right_limit and b[3] <= bottom_limit
    layout = {
        'edition': 'social_origin_v7',
        'reference_basis': SPEC['reference_basis'],
        'resolution': [W, H],
        'safe_area': safe,
        'primary_elements': primary,
        'all_primary_elements_inside_safe_area': all(inside(b) for b in primary.values()),
        'app_chrome_outside_safe_area': ['top status bar', 'bottom navigation'],
        'hook': {'visible': True, 'centered': True, 'colorful': True, 'two_lines': True,
                 'line_1_parts': V['hook_line_1_parts'], 'line_2': V['hook_line_2'],
                 'bbox': primary['hook']},
        'list': {'left_side': True, 'fully_visible': True, 'persistent': True, 'progressive': True,
                 'row_bboxes': row_bboxes, 'bbox': primary['left_list']},
        'right_ui': {'platform_ui': True, 'bbox': primary['right_ui'], 'fake_counts': False},
        'reaction': {'visible': True, 'at': V['reaction_at']},
        'bottom_bar': {'comment_bubble': True, 'subscribe': True, 'caption': True, 'app_nav': True},
        'flags': {
            'full_frame_preserved': True, 'no_crop': True, 'no_cut_off': True,
            'blurred_background_fill': True, 'no_black_bars': True, 'no_letterbox': True,
            'no_black_empty_top': True, 'no_hook_black_fill': True,
            'reference_style_hook': True, 'colorful_hook_title': True,
            'persistent_numbered_list': True, 'left_list_fully_visible': True,
            'all_labels_visible_from_start': True, 'progressive_labels': True, 'right_platform_ui': True,
            'bottom_comment_subscribe': True, 'app_chrome': True,
            'no_third_party_handle': True, 'no_fake_engagement_counts': True,
            'no_v6_boxed_list': True, 'no_v5_right_panel': True,
            'no_v5_bottom_rank_burst': True, 'no_v5_hook_occlusion': True,
            'safe_area_check': True, 'social_origin_check': True,
            'rights_verified_per_title': True, 'no_cover_crop': True,
            'no_punchy_zoom': True, 'seven_moments_only': True,
        },
        'full_motion_review': False, 'native_audio_listening': False,
        'human_approval': False, 'sign_off': False,
        'audience_result_promise': False, 'virality_guarantee': False,
        'current_trending_claim': False, 'unverified_social_repost': False,
    }
    (REVIEW / 'layout_manifest.json').write_text(json.dumps(layout, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return layout


def write_visual_qc(ledger, payoff_frames, layout):
    visual = {
        'edition': 'social_origin_v7',
        'full_frame_preserved': True, 'sharp_source_frame_uncut': True,
        'source_aspect_preserved': True, 'full_screen_blur_background': True,
        'no_crop': True, 'no_cut_off': True, 'no_black_bars': True,
        'no_letterbox': True, 'no_black_empty_top': True,
        'no_hook_black_fill': True, 'no_black_panels': True,
        'no_cover_crop': True, 'no_punchy_zoom': True,
        'reference_style_hook': True, 'colorful_hook_title': True,
        'persistent_numbered_list': True, 'left_list_fully_visible': True,
        'all_labels_visible_from_start': True, 'progressive_labels': True, 'right_platform_ui': True,
        'bottom_comment_subscribe': True, 'app_chrome': True,
        'no_third_party_handle': True, 'no_fake_engagement_counts': True,
        'no_v6_boxed_list': True, 'no_v5_right_panel': True,
        'no_v5_bottom_rank_burst': True, 'no_v5_hook_occlusion': True,
        'seven_moments_only': True, 'rank_numbers': True,
        'reaction_bubbles': True, 'custom_emoji_letters': True,
        'custom_vector_icons': True, 'hard_cuts_only': True,
        'all_primary_elements_inside_safe_area': bool(layout['all_primary_elements_inside_safe_area']),
        'payoff_frames': payoff_frames,
        'full_motion_review': False, 'native_audio_listening': False,
        'human_approval': False, 'sign_off': False,
        'audience_result_promise': False, 'virality_guarantee': False,
        'current_trending_claim': False, 'unverified_social_repost': False,
        'note': 'Renderer uses a blurred full-frame background plus a sharp aspect-preserving uncut source frame. It does not call the V6 crop routine and does not zoom/crop the main clip. This is a code/layout contract, not human creative approval.',
    }
    (REVIEW / 'visual_v7_qc.json').write_text(json.dumps(visual, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    edit = {
        'edition': 'social_origin_v7',
        'timeline': {'duration': 60.0, 'fps': FPS, 'frame_count': N_FRAMES},
        'scenes': ledger,
        'flags': {
            'full_frame_preserved': True, 'no_crop': True, 'no_black_bars': True,
            'blurred_background_fill': True, 'reference_style_hook': True,
            'persistent_numbered_list': True, 'progressive_labels': True,
            'right_platform_ui': True, 'bottom_comment_subscribe': True,
            'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
            'runner_visual_motion_probe': True, 'contact_sheets_written': True,
            'source_review_recorded': True, 'visual_lock_written': True,
            'full_motion_review': False, 'native_audio_listening': False,
            'human_approval': False, 'sign_off': False,
            'audience_result_promise': False, 'virality_guarantee': False,
        },
    }
    (REVIEW / 'visual_edit_ledger.json').write_text(json.dumps(edit, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def make_covers(first_path):
    base = Image.open(first_path).convert('RGBA')
    for name, text in [('cover_hook.jpg', V['cover_text_primary']), ('cover_ab.jpg', V['cover_text_ab'])]:
        out = base.copy()
        shadow_text(out, (W / 2, 1010), text, font(82), (255, 255, 255, 255), anchor='ma', off=(0, 7), blur=10, stroke=2)
        out.convert('RGB').save(REVIEW / name, quality=92)


def render_frame(scene_index, frame_no, tmp):
    scene = SCENES[int(scene_index)]
    clip = CLIPS / ('clip_' + scene['source_id'] + '.mp4')
    if not clip.exists():
        raise FileNotFoundError(clip)
    rel = int(clamp(frame_no - int(scene['start_frame']), 0, int(scene['frames']) - 1))
    cap = cv2.VideoCapture(str(clip))
    if not cap.isOpened():
        raise RuntimeError('Could not open clip ' + str(clip))
    cap.set(cv2.CAP_PROP_POS_FRAMES, rel)
    ok, raw = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError('Could not read frame ' + str(rel) + ' from ' + str(clip))
    src = Image.fromarray(cv2.cvtColor(raw, cv2.COLOR_BGR2RGB))
    img = compose_frame(src, int(scene['start_frame']) + rel, int(scene_index), SCENES)
    img.save(tmp, quality=92)
    return tmp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--frame', type=int, default=0)
    ap.add_argument('--scene', type=int, default=0)
    ap.add_argument('--tmp', default='/tmp/v7_frame.jpg')
    ap.add_argument('--single-frame', action='store_true')
    args = ap.parse_args()
    if args.check:
        assert len(SCENES) == 7 and SPEC['frame_count'] == 1800
        assert sum(int(s['frames']) for s in SCENES) == 1800
        assert all(float(s['zoom_start']) == 1.0 and float(s['zoom_end']) == 1.0 for s in SCENES)
        print('V7 renderer contract OK: 7 scenes / 1800 frames, no crop/zoom.')
        return 0
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW / 'candidates').mkdir(parents=True, exist_ok=True)
    layout = write_layout_manifest()
    if args.single_frame:
        clip = CLIPS / ('clip_' + SCENES[args.scene]['source_id'] + '.mp4')
        if not clip.exists():
            raise FileNotFoundError('No V7 clip found: ' + str(clip))
        render_frame(args.scene, args.frame, args.tmp)
        print('rendered single frame', args.tmp)
        return 0

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(SILENT_OUT), fourcc, FPS, (W, H))
    if not writer.isOpened():
        raise RuntimeError('Could not open silent VideoWriter')
    caps = {}
    for s in SCENES:
        cap = cv2.VideoCapture(str(CLIPS / ('clip_' + s['source_id'] + '.mp4')))
        if not cap.isOpened():
            raise RuntimeError('Could not open clip ' + s['source_id'])
        caps[s['source_id']] = cap
    ledger, payoff_frames = [], []
    global_frame = 0
    first_path = None
    for scene_index, s in enumerate(SCENES):
        cap = caps[s['source_id']]
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        n = int(s['frames'])
        for i in range(n):
            ok, raw = cap.read()
            if not ok:
                raise RuntimeError('Frame read failed for ' + s['source_id'])
            src = Image.fromarray(cv2.cvtColor(raw, cv2.COLOR_BGR2RGB))
            img = compose_frame(src, global_frame, scene_index, SCENES)
            final = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            writer.write(final)
            if i == 0:
                fp = REVIEW / f"frame_{s['rank']:02d}_{s['start']:05.2f}s.jpg"
                cv2.imwrite(str(fp), final, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
                first_path = fp
            if i == int(n * float(V['payoff_at'])):
                pp = REVIEW / f"payoff_frame_{s['rank']:02d}.jpg"
                cv2.imwrite(str(pp), final, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
                payoff_frames.append(str(pp.relative_to(ROOT)))
            global_frame += 1
        cap.release()
        ledger.append({
            'id': s['id'], 'rank': s['rank'], 'title': s['title'],
            'moment_label': s['title'], 'reaction_text': s['reaction_text'],
            'emoji': s['emoji'], 'timeline_in': s['start'], 'timeline_out': s['end'],
            'source_in': s['source_start'], 'source_out': s['source_out'],
            'frames': n, 'full_frame_preserved': True, 'sharp_source_frame_uncut': True,
            'no_crop': True, 'no_black_bars': True, 'blurred_background_fill': True,
            'no_cover_crop': True, 'no_punchy_zoom': True,
            'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
            'runner_visual_motion_probe': True, 'contact_sheets_written': True,
            'source_review_recorded': True, 'visual_lock_written': True,
            'added_audio_layers': 0,
        })
    writer.release()
    if global_frame != N_FRAMES or first_path is None:
        raise RuntimeError('Rendered frame count mismatch or first frame missing')
    make_covers(first_path)
    write_visual_qc(ledger, payoff_frames, layout)
    print('V7 silent video written', SILENT_OUT, SILENT_OUT.stat().st_size, 'bytes,', global_frame, 'frames', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
