#!/usr/bin/env python3
"""Runner-side high-action V9 candidate scout.

The clean V8 layout is retained for a later build, but V8's clip quality was
rejected: the sources did not show enough visible, next-level action. This
script verifies a fresh pool of rights-cleared, social-origin Wikimedia Commons
files through the Commons API, downloads either a small original or a Commons
VP9/Opus derivative, measures each file's own native audio and one-frame-per-
second visual motion, and writes compact contact sheets for real visual review.

This is a candidate scout only. It does not render a final Short, does not add
audio, does not assert currently trending clips, an exact reference match, full
legal compliance, human full-motion/native-audio listening, creative approval,
perfection, retention, virality or audience results.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_high_action_v9'
WORK = ROOT / 'production/monarch-cam/work/high_action_v9_scout'
REVIEW = BASE / 'review/scout'
MEDIA = WORK / 'media'
FRAMES = WORK / 'frames'
for p in (WORK, MEDIA, FRAMES):
    p.mkdir(parents=True, exist_ok=True)
shutil.rmtree(REVIEW, ignore_errors=True)
REVIEW.mkdir(parents=True, exist_ok=True)

MANIFEST = json.loads((BASE / 'candidate_scout_v9.json').read_text(encoding='utf-8'))
API = 'https://commons.wikimedia.org/w/api.php'
HEADERS = {
    'User-Agent': 'MonarchCamHighActionV9Scout/1.0 (https://github.com/adil-chandio/Monarch.Overall.Work; rights-cleared social-origin candidate scout)',
    'Accept': 'application/json, video/webm, application/ogg;q=0.9,*/*;q=0.8',
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
RETRY = Retry(
    total=6, connect=6, read=6, status=6, backoff_factor=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(['GET']),
    respect_retry_after_header=True,
    raise_on_status=False,
)
SESSION.mount('https://', HTTPAdapter(max_retries=RETRY))
SESSION.mount('http://', HTTPAdapter(max_retries=RETRY))

SR = 48000
WINDOW_S = 0.5
SEGMENT_S = 8.6
AUDIBLE_DBFS = -75.0
SELECTABLE_DBFS = -65.0
MIN_MOTION = 0.10
HIGH_ACTION_MOTION = 8.0
SCAN_SECONDS = 600.0
ORIGINAL_DOWNLOAD_LIMIT = 25_000_000
EXT_FILTER = (
    'LicenseShortName|UsageTerms|LicenseUrl|AttributionRequired|Artist|'
    'ImageDescription|Credit|DateTimeOriginal|Categories|Restrictions|Copyrighted'
)


def run(cmd, **kw):
    return subprocess.run(list(map(str, cmd)), **kw)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def font(size):
    for p in [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
              Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def strip_html(value):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(value or ''))).strip()


def ext_value(ext, name):
    item = ext.get(name, {})
    if isinstance(item, dict):
        return strip_html(item.get('value', ''))
    return strip_html(item)


def api_get(params):
    r = SESSION.get(API, params=params, timeout=90)
    r.raise_for_status()
    time.sleep(0.25)
    return r.json()


def dbfs(value):
    return round(float(max(-120.0, 20 * math.log10(max(float(value), 1e-12)))), 2)


def sha1_file(path):
    h = hashlib.sha1()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def verify_rights(asset):
    params = {
        'action': 'query', 'format': 'json', 'formatversion': '2',
        'prop': 'imageinfo', 'titles': asset['commons_title'],
        'iiprop': 'url|size|sha1|mime|extmetadata',
        'iiextmetadatafilter': EXT_FILTER,
    }
    data = api_get(params)
    pages = data.get('query', {}).get('pages', [])
    if not pages:
        raise RuntimeError('No Commons API page for ' + asset['id'])
    page = pages[0]
    if page.get('missing') or 'imageinfo' not in page:
        raise RuntimeError('Commons API page missing imageinfo for ' + asset['id'])
    info = page['imageinfo'][0]
    ext = info.get('extmetadata', {})
    short = ext_value(ext, 'LicenseShortName')
    usage = ext_value(ext, 'UsageTerms')
    license_url = ext_value(ext, 'LicenseUrl')
    attribution = ext_value(ext, 'AttributionRequired').lower()
    credit = ext_value(ext, 'Credit')
    categories = ext_value(ext, 'Categories')
    artist = ext_value(ext, 'Artist')
    description = ext_value(ext, 'ImageDescription')
    restrictions = ext_value(ext, 'Restrictions')
    allowed = {'cc0', 'public domain', 'cc by 3.0'}
    if short.lower() not in allowed and usage.lower() not in allowed:
        raise RuntimeError('Allowed licence not confirmed for ' + asset['id'] + ': ' + repr({'short': short, 'usage': usage}))
    if short.lower() == 'cc by 3.0' and '/licenses/by/3.0' not in license_url:
        raise RuntimeError('CC BY 3.0 licence URL not confirmed for ' + asset['id'])
    if short.lower() != asset['license_short_name'].lower():
        raise RuntimeError('Licence short-name mismatch for ' + asset['id'])
    mapped = 'PD' if short.lower() == 'public domain' else ('CC0' if short.lower() == 'cc0' else 'CC-BY-3.0')
    if mapped != asset['license']:
        raise RuntimeError('Licence ID mismatch for ' + asset['id'])
    lowered = ' '.join([categories, description, credit]).lower()
    for forbidden in ['license review needed (video)', 'videos containing non-free audio', 'non-free audio',
                      'cc-by-sa', 'cc by 2.0', 'cc by 4.0', 'fair-use-only', 'section 107']:
        if forbidden in lowered:
            raise RuntimeError('Disallowed rights flag for ' + asset['id'] + ': ' + forbidden)
    if restrictions:
        raise RuntimeError('Non-empty Commons Restrictions for ' + asset['id'] + ': ' + restrictions)
    want_attr = bool(asset['attribution_required'])
    got_attr = attribution in ('true', '1', 'yes')
    if want_attr != got_attr:
        raise RuntimeError('Attribution requirement mismatch for ' + asset['id'])
    origin_text = ' '.join([credit, categories, description]).lower()
    if not any(str(tok).lower() in origin_text for tok in asset['platform_tokens']):
        raise RuntimeError('Social origin not confirmed for ' + asset['id'])
    if not str(asset['source_page']).startswith('https://commons.wikimedia.org/wiki/File:'):
        raise RuntimeError('Source page is not a Commons file page for ' + asset['id'])
    if info.get('sha1', '').lower() != asset['expected_sha1'].lower():
        raise RuntimeError('Commons API original SHA-1 mismatch for ' + asset['id'])
    if int(info.get('size', 0)) != int(asset['expected_size_bytes']):
        raise RuntimeError('Commons API original size mismatch for ' + asset['id'])
    if abs(float(info.get('duration', 0.0)) - float(asset['duration_seconds'])) > 1.0:
        raise RuntimeError('Commons API duration mismatch for ' + asset['id'])
    if int(info.get('width', 0)) != int(asset['width']) or int(info.get('height', 0)) != int(asset['height']):
        raise RuntimeError('Commons API dimensions mismatch for ' + asset['id'])
    if not info.get('url') or not str(info['url']).startswith('https://upload.wikimedia.org/'):
        raise RuntimeError('Missing Commons original URL for ' + asset['id'])
    return {
        'api_license_verified': True,
        'license_short_name': short,
        'usage_terms': usage,
        'license_url': license_url,
        'license_id': mapped,
        'attribution_required_api': got_attr,
        'artist': artist,
        'credit': credit,
        'categories': categories,
        'description': description,
        'restrictions': restrictions,
        'restrictions_status': 'none_reported_in_extmetadata',
        'original_url': info['url'],
        'original_sha1': info['sha1'].lower(),
        'original_size_bytes': int(info['size']),
        'api_duration_seconds': float(info.get('duration', 0.0)),
        'api_width': int(info['width']),
        'api_height': int(info['height']),
        'api_mime': info.get('mime'),
    }


def choose_download(title, original_url, original_size):
    if original_size <= ORIGINAL_DOWNLOAD_LIMIT:
        return original_url, 'commons_original', None
    params = {
        'action': 'query', 'format': 'json', 'formatversion': '2',
        'prop': 'videoinfo', 'titles': title,
        'viprop': 'url|derivatives|size|mime',
    }
    try:
        data = api_get(params)
        pages = data.get('query', {}).get('pages', [])
        if pages and pages[0].get('videoinfo'):
            vi = pages[0]['videoinfo'][0]
            derivs = vi.get('derivatives', []) or []
            preferred = [d for d in derivs if d.get('transcodekey') == '480p.vp9.webm' and 'opus' in d.get('type', '').lower()]
            fallback = [d for d in derivs if d.get('transcodekey') == '240p.vp9.webm' and 'opus' in d.get('type', '').lower()]
            chosen = (preferred or fallback or [None])[0]
            if chosen and str(chosen.get('src', '')).startswith('https://upload.wikimedia.org/wikipedia/commons/transcoded/'):
                return chosen['src'], 'commons_vp9_opus_transcode', chosen
    except Exception as e:
        print('Derivative lookup fell back to original for', title, repr(e), flush=True)
    return original_url, 'commons_original', None


def download(url, dest):
    tmp = dest.with_suffix('.download')
    if tmp.exists():
        tmp.unlink()
    r = SESSION.get(url, timeout=300, allow_redirects=True, stream=True)
    r.raise_for_status()
    declared = int(r.headers.get('content-length') or 0)
    if declared and declared < 100000:
        raise RuntimeError('short declared response')
    total = 0
    with tmp.open('wb') as fh:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                fh.write(chunk)
                total += len(chunk)
    if total < 100000:
        raise RuntimeError('short streamed response')
    tmp.replace(dest)
    time.sleep(1.0)
    return total, sha1_file(dest)


def probe_streams(raw, fallback_duration):
    p = run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', raw],
            capture_output=True, text=True, check=True)
    info = json.loads(p.stdout)
    streams = info.get('streams', [])
    video = next((s for s in streams if s.get('codec_type') == 'video'), {})
    audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    try:
        duration = float(info.get('format', {}).get('duration') or 0.0)
    except (TypeError, ValueError):
        duration = 0.0
    if not duration:
        duration = float(fallback_duration)
    return {
        'duration_seconds': round(duration, 3),
        'width': int(video.get('width', 0)),
        'height': int(video.get('height', 0)),
        'video_codec': video.get('codec_name'),
        'audio_stream_present': audio is not None,
        'audio_codec': (audio or {}).get('codec_name'),
        'audio_sample_rate': (audio or {}).get('sample_rate'),
        'audio_channels': (audio or {}).get('channels'),
    }


def decode_audio(raw, probed):
    if not probed['audio_stream_present']:
        return None
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-i', raw,
           '-map', '0:a:0', '-vn', '-t', f'{SCAN_SECONDS:.3f}',
           '-ac', '1', '-ar', str(SR), '-f', 'f32le',
           '-acodec', 'pcm_f32le', 'pipe:1']
    p = run(cmd, capture_output=True, check=True)
    if not p.stdout:
        return None
    return np.frombuffer(p.stdout, dtype='<f4').astype(np.float32)


def extract_overview_frames(raw, aid):
    frames_dir = FRAMES / aid / 'overview'
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-nostdin', '-y', '-hide_banner', '-loglevel', 'warning',
           '-i', raw, '-t', f'{SCAN_SECONDS:.3f}',
           '-vf', 'fps=1,scale=320:-2', '-q:v', '3', '-start_number', '0',
           frames_dir / '%05d.jpg']
    run(cmd, capture_output=True, text=True, check=True)
    frames = sorted(frames_dir.glob('*.jpg'))
    if len(frames) < 2:
        raise RuntimeError('Insufficient 1 fps review frames')
    arrays = []
    for fp in frames:
        im = Image.open(fp).convert('L')
        im.thumbnail((160, 90), Image.Resampling.LANCZOS)
        arrays.append(np.asarray(im, dtype=np.float32))
    motion_scores = [float(np.mean(np.abs(arrays[i + 1] - arrays[i]))) for i in range(len(arrays) - 1)]
    global_motion = round(float(np.mean(motion_scores)) if motion_scores else 0.0, 4)
    max_motion = round(float(np.max(motion_scores)) if motion_scores else 0.0, 4)
    return frames, motion_scores, global_motion, max_motion


def audio_windows(x, probed, motion_scores, global_motion, humor_bonus):
    scan_duration = min(float(probed['duration_seconds']), SCAN_SECONDS)
    duration = float(len(x)) / SR if x is not None else scan_duration
    block = int(WINDOW_S * SR)
    block_rms, block_peak, blocks = {}, {}, []
    if x is not None:
        prefix_x = np.concatenate(([0.0], np.cumsum(x, dtype=np.float64)))
        x64 = x.astype(np.float64)
        prefix_x2 = np.concatenate(([0.0], np.cumsum(x64 * x64)))
        for start in np.arange(0.0, duration, WINDOW_S):
            st = round(float(start), 3)
            a = int(round(st * SR))
            b = min(len(x), int(round((st + WINDOW_S) * SR)))
            if b > a:
                seg = x[a:b]
                ac = seg - np.mean(seg)
                rms = dbfs(float(np.sqrt(np.mean(ac ** 2))))
                peak = dbfs(float(np.max(np.abs(ac))))
            else:
                rms, peak = -120.0, -120.0
            block_rms[st], block_peak[st] = rms, peak
            blocks.append({'start': st, 'rms_dbfs': rms, 'peak_dbfs': peak})
    else:
        for start in np.arange(0.0, duration, WINDOW_S):
            st = round(float(start), 3)
            block_rms[st], block_peak[st] = -120.0, -120.0
            blocks.append({'start': st, 'rms_dbfs': -120.0, 'peak_dbfs': -120.0})

    n_full_blocks = int(round(SEGMENT_S / WINDOW_S))
    candidates = []
    for start in np.arange(0.0, max(0.0, duration - SEGMENT_S + 0.001), WINDOW_S):
        st = round(float(start), 3)
        if x is not None:
            a = int(round(st * SR))
            b = min(len(x), int(round((st + SEGMENT_S) * SR)))
            if b > a:
                n = b - a
                sx = float(prefix_x[b] - prefix_x[a])
                sx2 = float(prefix_x2[b] - prefix_x2[a])
                mean = sx / n
                variance = max(0.0, sx2 / n - mean * mean)
                rms = dbfs(math.sqrt(variance))
                peak = max([block_peak.get(round(st + i * WINDOW_S, 3), -120.0) for i in range(n_full_blocks + 1)] or [-120.0])
            else:
                rms, peak = -120.0, -120.0
        else:
            rms, peak = -120.0, -120.0
        a_motion = int(np.floor(st))
        b_motion = min(len(motion_scores), int(np.ceil(st + SEGMENT_S)) - 1)
        local = motion_scores[a_motion:b_motion] if b_motion > a_motion else []
        motion = round(float(np.mean(local)) if local else global_motion, 4)
        motion_norm = min(30.0, max(0.0, motion))
        audio_norm = min(20.0, max(0.0, rms + 55.0))
        score = round(0.65 * motion_norm + 0.35 * audio_norm + float(humor_bonus), 4)
        block_values = [block_rms.get(round(st + i * WINDOW_S, 3), -120.0) for i in range(n_full_blocks)]
        min_full_block_rms_dbfs = round(min(block_values), 2) if block_values else -120.0
        quiet_full_block_count = sum(1 for value in block_values if value <= SELECTABLE_DBFS)
        continuous_native_audio = bool(block_values and quiet_full_block_count == 0)
        selectable = bool(rms > SELECTABLE_DBFS and motion >= MIN_MOTION and continuous_native_audio)
        high_action = bool(motion >= HIGH_ACTION_MOTION and selectable)
        candidates.append({
            'start': st, 'end': round(min(duration, st + SEGMENT_S), 3),
            'duration': SEGMENT_S, 'rms_dbfs': rms,
            'peak_dbfs_approx': peak, 'motion_score': motion, 'score': score,
            'min_full_block_rms_dbfs': min_full_block_rms_dbfs,
            'quiet_full_block_count': quiet_full_block_count,
            'continuous_native_audio': continuous_native_audio,
            'selectable': selectable, 'high_action': high_action,
        })
    candidates.sort(key=lambda w: (w['high_action'], w['score'], w['motion_score']), reverse=True)
    audible_window_count = sum(1 for b in blocks if b['rms_dbfs'] > AUDIBLE_DBFS)
    native_audio_eligible = bool(probed['audio_stream_present'] and x is not None and audible_window_count > 0)
    if x is not None and len(x):
        centered = x - np.mean(x)
        integrated_rms_dbfs = dbfs(float(np.sqrt(np.mean(centered ** 2))))
        dc_offset = round(float(np.mean(x)), 8)
    else:
        integrated_rms_dbfs, dc_offset = -120.0, 0.0
    best = None
    best_source = 'none'
    for w in candidates:
        if w['high_action'] and native_audio_eligible:
            best, best_source = w, 'high_action_selectable_native_audio'
            break
    if best is None:
        for w in candidates:
            if w['selectable'] and native_audio_eligible:
                best, best_source = w, 'selectable_native_audio'
                break
    if best is None and candidates:
        best, best_source = candidates[0], 'visual_motion_only_no_native_audio_eligibility'
    return {
        'window_seconds': WINDOW_S, 'segment_seconds': SEGMENT_S,
        'audible_threshold_dbfs': AUDIBLE_DBFS,
        'selectable_segment_rms_dbfs_min': SELECTABLE_DBFS,
        'minimum_motion_score': MIN_MOTION,
        'high_action_motion_score_min': HIGH_ACTION_MOTION,
        'scanned_seconds': round(scan_duration, 3),
        'audio_duration_seconds': round(duration, 3),
        'audio_stream_present': bool(probed['audio_stream_present']),
        'audio_codec': probed.get('audio_codec'),
        'half_second_blocks': blocks,
        'audible_window_count': audible_window_count,
        'integrated_rms_dbfs': integrated_rms_dbfs,
        'dc_offset': dc_offset,
        'native_audio_eligible': native_audio_eligible,
        'continuous_native_audio_policy': 'Seventeen complete 0.5 s blocks inside each 8.6 s window must remain above -65.0 dBFS.',
        'global_motion_score': global_motion,
        'high_action_selectable_window_count': sum(1 for w in candidates if w['high_action']),
        'top_windows': candidates[:8],
        'best_window': best,
        'best_window_source': best_source,
        'runner_visual_motion_probe': bool(global_motion >= MIN_MOTION),
        'runner_audio_visual_probe_passed': bool(native_audio_eligible and any(w['high_action'] for w in candidates)),
        'runner_high_action_visual_probe_passed': bool(any(w['motion_score'] >= HIGH_ACTION_MOTION for w in candidates)),
        'peak_dbfs_note': 'Window peak is the maximum of the measured 0.5 s block peaks; final V9 audio QC uses the unchanged direct audio gates.',
    }


def make_sheet(out, title, subtitle, tiles, cols=4, rows=4):
    cw, ch, tw, th = 336, 220, 320, 180
    canvas = Image.new('RGB', (cols * cw, 64 + rows * ch), '#101820')
    d = ImageDraw.Draw(canvas)
    d.text((16, 10), title[:100], font=font(18), fill='#F4F1E8')
    d.text((16, 36), subtitle[:120], font=font(14), fill='#A9B8C4')
    for i, (fp, label) in enumerate(tiles[:cols * rows]):
        im = Image.open(fp).convert('RGB')
        im.thumbnail((tw, th), Image.Resampling.LANCZOS)
        tile = Image.new('RGB', (tw, th), '#05080B')
        tile.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
        x = (i % cols) * cw + 8
        y = 64 + (i // cols) * ch
        canvas.paste(tile, (x, y))
        d.text((x + 4, y + th + 5), label, font=font(16), fill='#63D7C8')
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=90)
    return str(out.relative_to(ROOT))


def motion_overview_sheet(aid, frames, motion_scores):
    ranked = sorted(range(len(motion_scores)), key=lambda i: motion_scores[i], reverse=True)
    chosen = []
    for i in ranked:
        if all(abs(i - j) >= 2 for j in chosen):
            chosen.append(i)
        if len(chosen) >= 16:
            break
    chosen.sort()
    tiles = []
    for i in chosen:
        t = float(i + 1)
        label = f'{int(t)//60:02d}:{t%60:04.1f}  motion {motion_scores[i]:.1f}'
        tiles.append((frames[i + 1], label))
    out = REVIEW / f'candidate_{aid}_motion_overview.jpg'
    return make_sheet(out, f'V9 HIGH-ACTION CANDIDATE - {aid.upper()} - MOTION OVERVIEW',
                      'Top separated 1 fps motion frames; visual review pending', tiles, 4, 4), chosen


def best_window_sheet(aid, raw, best):
    if not best:
        return None
    start = float(best['start'])
    frames_dir = FRAMES / aid / 'best_window'
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-nostdin', '-y', '-hide_banner', '-loglevel', 'warning',
           '-ss', f'{start:.3f}', '-i', raw, '-t', f'{SEGMENT_S:.3f}',
           '-vf', 'fps=2,scale=320:-2', '-q:v', '3', '-start_number', '0',
           '-frames:v', '20', frames_dir / '%05d.jpg']
    run(cmd, capture_output=True, text=True, check=True)
    frames = sorted(frames_dir.glob('*.jpg'))
    if not frames:
        raise RuntimeError('No best-window review frames')
    tiles = []
    for i, fp in enumerate(frames[:20]):
        t = start + i * 0.5
        label = f'{int(t)//60:02d}:{t%60:04.1f}'
        tiles.append((fp, label))
    out = REVIEW / f'candidate_{aid}_best_window.jpg'
    return make_sheet(out, f'V9 HIGH-ACTION CANDIDATE - {aid.upper()} - BEST 8.6s WINDOW',
                      f'Runner start {start:.1f}s; inspect full motion before final V9 selection', tiles, 4, 5)


def process_asset(asset):
    aid = asset['id']
    entry = {
        'id': aid, 'role': asset['role'], 'title': asset['title'],
        'creator': asset['creator'], 'source_page': asset['source_page'],
        'platform': asset['platform'], 'action_hint': asset['action_hint'],
        'moment_label': asset['moment_label'], 'reaction_text': asset['reaction_text'],
        'probe_completed': False, 'visual_review_pending': True,
    }
    print('V9 scout:', aid, asset['commons_title'], flush=True)
    try:
        rights = verify_rights(asset)
    except Exception as e:
        entry.update({'status': 'rights_rejected', 'error': repr(e)})
        return entry
    entry.update(rights)
    try:
        url, kind, derivative = choose_download(asset['commons_title'], rights['original_url'], rights['original_size_bytes'])
        raw = MEDIA / (aid + ('.webm' if 'webm' in str(rights['api_mime']) or 'transcoded' in url else '.ogv'))
        total, downloaded_sha1 = download(url, raw)
        probed = probe_streams(raw, rights['api_duration_seconds'])
        frames, motion_scores, global_motion, max_motion = extract_overview_frames(raw, aid)
        x = decode_audio(raw, probed)
        audio = audio_windows(x, probed, motion_scores, global_motion, asset['humor_bonus'])
        overview, chosen = motion_overview_sheet(aid, frames, motion_scores)
        best_sheet = best_window_sheet(aid, raw, audio['best_window'])
        sheets = [overview] + ([best_sheet] if best_sheet else [])
        entry.update({
            'probe_completed': True,
            'status': 'runner_contact_sheets_written_visual_review_pending',
            'download_url': url,
            'download_kind': kind,
            'download_derivative': derivative,
            'download_bytes': total,
            'downloaded_sha1': downloaded_sha1,
            'ffprobe': probed,
            'review_frames': len(frames),
            'motion_scores_count': len(motion_scores),
            'global_motion_score': global_motion,
            'max_motion_score': max_motion,
            'overview_chosen_frame_indices': chosen,
            'audio': audio,
            'contact_sheets': sheets,
            'no_added_audio': True,
            'native_source_audio_only': True,
            'social_origin_verified_via_commons_api': True,
            'current_trending_claim': False,
            'exact_reference_clip_claim': False,
            'full_legal_compliance_claim': False,
            'human_full_motion_review': False,
            'human_native_audio_listening': False,
            'creative_approval': False,
        })
        return entry
    except Exception as e:
        entry.update({'status': 'probe_failed', 'error': repr(e)})
        return entry


def main():
    started = time.time()
    entries = [process_asset(a) for a in MANIFEST['assets']]
    all_sheets = [s for e in entries for s in e.get('contact_sheets', [])]
    successful = [e for e in entries if e.get('probe_completed')]
    audible = [e for e in successful if e.get('audio', {}).get('native_audio_eligible')]
    high_action = [e for e in successful if e.get('audio', {}).get('runner_audio_visual_probe_passed')]
    top_candidates = []
    for e in successful:
        w = e.get('audio', {}).get('best_window')
        if w:
            top_candidates.append({
                'id': e['id'], 'action_hint': e['action_hint'],
                'start': w['start'], 'score': w['score'],
                'motion_score': w['motion_score'], 'rms_dbfs': w['rms_dbfs'],
                'high_action': w['high_action'], 'selectable': w['selectable'],
                'native_audio_eligible': e['audio']['native_audio_eligible'],
                'contact_sheets': e.get('contact_sheets', []),
            })
    top_candidates.sort(key=lambda c: (c['high_action'], c['native_audio_eligible'], c['score'], c['motion_score']), reverse=True)
    summary = {
        'edition': MANIFEST['edition'],
        'candidate_count': len(entries),
        'rights_and_probe_completed': len(successful),
        'rights_rejected_or_probe_failed': len(entries) - len(successful),
        'native_audio_eligible_candidates': len(audible),
        'high_action_selectable_native_audio_candidates': len(high_action),
        'contact_sheets_written': len(all_sheets),
        'elapsed_seconds': round(time.time() - started, 2),
        'top_candidates_by_runner_score': top_candidates,
        'visual_review_required': True,
        'final_v9_selection_locked': False,
        'final_v9_mp4_rendered': False,
    }
    report = {
        'edition': MANIFEST['edition'],
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'purpose': MANIFEST['purpose'],
        'workflow_scope': 'candidate_scout_only',
        'deliverable': MANIFEST['deliverable'],
        'reference_short_url': MANIFEST['reference_short_url'],
        'reference_exact_match': False,
        'reference_real_frames_obtained': False,
        'reference_full_motion_obtained': False,
        'reference_native_audio_obtained': False,
        'policy': MANIFEST['policy'],
        'flags': {
            'current_trending_claim': False,
            'exact_reference_clip_claim': False,
            'full_legal_compliance_claim': False,
            'human_full_motion_review': False,
            'human_native_audio_listening': False,
            'human_approval': False,
            'creative_sign_off': False,
            'perfection_claim': False,
            'retention_claim': False,
            'virality_claim': False,
            'audience_results_claim': False,
            'same_path_replacement': False,
            'no_added_audio': True,
            'native_source_audio_only': True,
        },
        'status_note': (
            'V8 clip quality was rejected for weak/static action. This separate V9 lane probes new high-action '
            'rights-cleared social-origin Commons candidates and commits real runner contact sheets for visual '
            'inspection. Exact currently trending named-platform clips, exact reference frames/full motion/native '
            'audio, full legal compliance, human sign-off, creative approval and audience outcomes are not claimed. '
            'Technical motion/audio measurements and CI success are not creative approval.'
        ),
        'assets': entries,
        'contact_sheets': all_sheets,
        'summary': summary,
    }
    save_json(REVIEW / 'scout_report.json', report)
    save_json(REVIEW / 'scout_summary.json', summary)
    print('V9 scout summary:', json.dumps(summary, indent=2), flush=True)
    if len(successful) < 10:
        raise SystemExit('V9 scout failed: fewer than 10 candidates completed rights, download and contact-sheet probing')


if __name__ == '__main__':
    main()
