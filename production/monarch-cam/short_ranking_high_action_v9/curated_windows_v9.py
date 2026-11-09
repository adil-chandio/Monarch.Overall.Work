#!/usr/bin/env python3
"""Second-pass V9 high-action curated-window runner scout.

Reads the committed 20-candidate scout report, downloads each unique source
once, and extracts explicit 8.6 s windows chosen from the real motion-overview
and best-window contact sheets. Each window gets its own 0.5 s contact sheet,
direct native-audio RMS/continuity check and frame-difference motion score.

This does not render the final Short and does not lock the final seven. It is a
visual inspection aid, not human full-motion/native-audio listening, creative
approval, an exact reference match, a currently trending claim or full legal
compliance.
"""
from __future__ import annotations

import hashlib
import json
import math
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
WORK = ROOT / 'production/monarch-cam/work/high_action_v9_curated'
REVIEW = BASE / 'review/curated_windows'
MEDIA = WORK / 'media'
FRAMES = WORK / 'frames'
for p in (WORK, MEDIA, FRAMES):
    p.mkdir(parents=True, exist_ok=True)
shutil.rmtree(REVIEW, ignore_errors=True)
REVIEW.mkdir(parents=True, exist_ok=True)

WINDOWS = json.loads((BASE / 'curated_windows_v9.json').read_text(encoding='utf-8'))
SCOUT = json.loads((BASE / 'review/scout/scout_report.json').read_text(encoding='utf-8'))
ASSETS = {a['id']: a for a in SCOUT['assets']}
SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'MonarchCamHighActionV9Curated/1.0 (https://github.com/adil-chandio/Monarch.Overall.Work; rights-cleared curated-window review)',
    'Accept': 'video/webm, application/ogg;q=0.9,*/*;q=0.8',
})
RETRY = Retry(total=6, connect=6, read=6, status=6, backoff_factor=3,
              status_forcelist=[429, 500, 502, 503, 504],
              allowed_methods=frozenset(['GET']), respect_retry_after_header=True,
              raise_on_status=False)
SESSION.mount('https://', HTTPAdapter(max_retries=RETRY))
SESSION.mount('http://', HTTPAdapter(max_retries=RETRY))

SR = 48000
SEGMENT_S = 8.6
BLOCK_S = 0.5
SELECTABLE_DBFS = -65.0
MIN_CURATED_MOTION = 4.0


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


def dbfs(value):
    return round(float(max(-120.0, 20 * math.log10(max(float(value), 1e-12)))), 2)


def sha1_file(path):
    h = hashlib.sha1()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


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
    time.sleep(0.5)
    return total, sha1_file(dest)


def make_sheet(out, title, subtitle, tiles, cols=4, rows=5):
    cw, ch, tw, th = 336, 220, 320, 180
    canvas = Image.new('RGB', (cols * cw, 64 + rows * ch), '#101820')
    d = ImageDraw.Draw(canvas)
    d.text((16, 10), title[:110], font=font(18), fill='#F4F1E8')
    d.text((16, 36), subtitle[:130], font=font(14), fill='#A9B8C4')
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


def decode_window_audio(raw, start):
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{start:.3f}', '-i', raw,
           '-t', f'{SEGMENT_S:.3f}', '-map', '0:a:0', '-vn',
           '-ac', '1', '-ar', str(SR), '-f', 'f32le',
           '-acodec', 'pcm_f32le', 'pipe:1']
    p = run(cmd, capture_output=True, check=True)
    if not p.stdout:
        raise RuntimeError('No native audio decoded')
    x = np.frombuffer(p.stdout, dtype='<f4').astype(np.float32)
    centered = x - np.mean(x)
    rms = dbfs(float(np.sqrt(np.mean(centered ** 2))))
    peak = dbfs(float(np.max(np.abs(centered))))
    dc = round(float(np.mean(x)), 8)
    block = int(BLOCK_S * SR)
    blocks = []
    for i in range(int(SEGMENT_S / BLOCK_S)):
        seg = x[i * block:(i + 1) * block]
        if len(seg) < block // 2:
            continue
        ac = seg - np.mean(seg)
        blocks.append({
            'start': round(start + i * BLOCK_S, 3),
            'rms_dbfs': dbfs(float(np.sqrt(np.mean(ac ** 2)))),
            'peak_dbfs': dbfs(float(np.max(np.abs(ac)))),
            'samples': int(len(seg)),
        })
    quiet = sum(1 for b in blocks if b['rms_dbfs'] <= SELECTABLE_DBFS)
    continuous = bool(blocks and len(blocks) >= 17 and quiet == 0)
    return {
        'audio_stream_decoded': True,
        'samples': int(len(x)),
        'decoded_duration_seconds': round(len(x) / SR, 3),
        'rms_dbfs': rms, 'peak_dbfs': peak, 'dc_offset': dc,
        'half_second_blocks': blocks,
        'quiet_half_second_block_count': quiet,
        'continuous_native_audio': continuous,
        'native_audio_confirmed': bool(rms > SELECTABLE_DBFS and continuous),
        'no_added_audio_layers': True,
        'raw_per_window_native_audio_only': True,
    }


def extract_window_frames(raw, aid, tag, start):
    frames_dir = FRAMES / f'{aid}_{tag}'
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-nostdin', '-y', '-hide_banner', '-loglevel', 'warning',
           '-ss', f'{start:.3f}', '-i', raw, '-t', f'{SEGMENT_S:.3f}',
           '-vf', 'fps=2,scale=320:-2', '-q:v', '3', '-start_number', '0',
           '-frames:v', '20', frames_dir / '%05d.jpg']
    run(cmd, capture_output=True, text=True, check=True)
    frames = sorted(frames_dir.glob('*.jpg'))
    if len(frames) < 8:
        raise RuntimeError('Insufficient 0.5 s review frames')
    arrays = []
    for fp in frames:
        im = Image.open(fp).convert('L')
        im.thumbnail((160, 90), Image.Resampling.LANCZOS)
        arrays.append(np.asarray(im, dtype=np.float32))
    scores = [float(np.mean(np.abs(arrays[i + 1] - arrays[i]))) for i in range(len(arrays) - 1)]
    return frames, {
        'review_frames': len(frames),
        'curated_motion_score': round(float(np.mean(scores)) if scores else 0.0, 4),
        'max_frame_motion_score': round(float(np.max(scores)) if scores else 0.0, 4),
        'motion_threshold': MIN_CURATED_MOTION,
    }


def process_window(spec, asset, raw):
    aid, start = spec['id'], float(spec['start'])
    tag = f'{start:.1f}'.replace('.', 'p')
    entry = {
        'id': aid, 'start': start, 'end': round(start + SEGMENT_S, 3),
        'reason': spec['reason'], 'title': asset['title'],
        'creator': asset['creator'], 'source_page': asset['source_page'],
        'platform': asset['platform'], 'action_hint': asset['action_hint'],
        'moment_label': asset['moment_label'], 'reaction_text': asset['reaction_text'],
        'license_short_name': asset['license_short_name'],
        'license_id': asset['license_id'],
        'api_license_verified': asset['api_license_verified'],
        'original_sha1': asset['original_sha1'],
        'original_url': asset['original_url'],
        'download_url': asset['download_url'],
        'download_kind': asset['download_kind'],
        'downloaded_sha1': asset['downloaded_sha1'],
        'scout_native_audio_eligible': asset['audio']['native_audio_eligible'],
        'probe_completed': False, 'visual_review_required': True,
    }
    print('V9 curated window:', aid, start, spec['reason'], flush=True)
    try:
        frames, motion = extract_window_frames(raw, aid, tag, start)
        audio = decode_window_audio(raw, start)
        tiles = []
        for i, fp in enumerate(frames[:20]):
            t = start + i * BLOCK_S
            label = f'{int(t)//60:02d}:{t%60:04.1f}'
            tiles.append((fp, label))
        out = REVIEW / f'curated_{aid}_{tag}_window.jpg'
        sheet = make_sheet(out, f'V9 CURATED WINDOW - {aid.upper()} - START {start:.1f}s',
                           spec['reason'] + '; native audio and visual review pending', tiles, 4, 5)
        eligible = bool(audio['native_audio_confirmed'] and motion['curated_motion_score'] >= MIN_CURATED_MOTION)
        entry.update({
            'probe_completed': True,
            'status': 'runner_curated_window_contact_sheet_written_visual_review_pending',
            'contact_sheet': sheet,
            'audio': audio,
            'motion': motion,
            'window_eligible': eligible,
            'window_eligibility_note': 'Direct 8.6 s native audio RMS/17-block continuity plus 0.5 s frame-difference motion; visual payoff still requires inspection.',
            'current_trending_claim': False,
            'exact_reference_clip_claim': False,
            'full_legal_compliance_claim': False,
            'human_full_motion_review': False,
            'human_native_audio_listening': False,
            'creative_approval': False,
        })
        return entry
    except Exception as e:
        entry.update({'status': 'curated_window_probe_failed', 'error': repr(e)})
        return entry


def composite(entries):
    completed = [e for e in entries if e.get('contact_sheet')]
    sheets = [e['contact_sheet'] for e in completed]
    cols = 4
    rows = max(1, math.ceil(len(sheets) / cols))
    cw, ch = 336, 310
    canvas = Image.new('RGB', (cols * cw, rows * ch), '#0b1018')
    d = ImageDraw.Draw(canvas)
    for i, e in enumerate(completed):
        fp = ROOT / e['contact_sheet']
        im = Image.open(fp).convert('RGB')
        im.thumbnail((320, 275), Image.Resampling.LANCZOS)
        x = (i % cols) * cw + 8
        y = (i // cols) * ch + 26
        canvas.paste(im, (x + (320 - im.width) // 2, y))
        label = f"{i+1:02d} {e['id']} @ {e['start']:.1f}s"
        info = (f"motion {e['motion']['curated_motion_score']} | audio "
                f"{str(e['audio']['native_audio_confirmed'])[:1]} | eligible "
                f"{str(e['window_eligible'])[:1]}")
        d.text((x, 4 + (i // cols) * ch), label, font=font(16), fill='#F4F1E8')
        d.text((x, 20 + (i // cols) * ch), info, font=font(12), fill='#63D7C8')
    out = REVIEW / 'v9_curated_windows_all.jpg'
    canvas.save(out, quality=92)
    return str(out.relative_to(ROOT))


def main():
    started = time.time()
    entries = []
    fetched = {}
    for spec in WINDOWS['windows']:
        aid = spec['id']
        asset = ASSETS.get(aid)
        if not asset:
            entries.append({'id': aid, 'start': spec['start'], 'status': 'candidate_missing_in_scout_report'})
            continue
        if aid not in fetched:
            try:
                url = asset['download_url']
                ext = '.webm' if ('webm' in url or asset.get('download_kind') == 'commons_vp9_opus_transcode') else '.ogv'
                raw = MEDIA / (aid + ext)
                total, got = download(url, raw)
                if got.lower() != str(asset['downloaded_sha1']).lower():
                    raise RuntimeError('Downloaded SHA-1 differs from committed scout report')
                fetched[aid] = raw
                print('Downloaded', aid, total, got, flush=True)
            except Exception as e:
                fetched[aid] = e
                print('Download failed', aid, repr(e), flush=True)
        raw = fetched[aid]
        if isinstance(raw, Exception):
            entries.append({'id': aid, 'start': spec['start'], 'status': 'download_failed', 'error': repr(raw)})
            continue
        entries.append(process_window(spec, asset, raw))
    completed = [e for e in entries if e.get('probe_completed')]
    eligible = [e for e in completed if e.get('window_eligible')]
    sheet = composite(entries) if completed else None
    summary = {
        'edition': WINDOWS['edition'],
        'window_count': len(WINDOWS['windows']),
        'completed': len(completed),
        'failed': len(entries) - len(completed),
        'native_audio_confirmed_windows': sum(1 for e in completed if e['audio']['native_audio_confirmed']),
        'runner_eligible_windows': len(eligible),
        'contact_sheets_written': len(completed) + (1 if sheet else 0),
        'elapsed_seconds': round(time.time() - started, 2),
        'visual_review_required': True,
        'final_v9_selection_locked': False,
        'final_v9_mp4_rendered': False,
    }
    report = {
        'edition': WINDOWS['edition'],
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'purpose': WINDOWS['purpose'],
        'source_report': WINDOWS['source_report'],
        'workflow_scope': 'curated_window_scout_only',
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
            'These runner 0.5 s contact sheets and native-audio checks are a second-pass visual curation aid after '
            'the rejected V8 clip quality. They are not human full-motion/native-audio listening, creative approval, '
            'an exact reference match, currently trending named-platform clips, full legal compliance or audience results.'
        ),
        'composite_contact_sheet': sheet,
        'windows': entries,
        'summary': summary,
    }
    save_json(REVIEW / 'curated_window_report.json', report)
    save_json(REVIEW / 'curated_window_summary.json', summary)
    print('V9 curated summary:', json.dumps(summary, indent=2), flush=True)
    if len(completed) < 20:
        raise SystemExit('V9 curated-window scout failed: fewer than 20 windows completed')


if __name__ == '__main__':
    main()
