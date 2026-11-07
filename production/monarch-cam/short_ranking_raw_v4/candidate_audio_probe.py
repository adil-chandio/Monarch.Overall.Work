#!/usr/bin/env python3
# Runner-side probe for independently verified CC0 replacement clips.
# Measures each file's own native audio stream, then builds coarse visual contact sheets.
# No audio is added, generated, or borrowed from another moment.
from __future__ import annotations
import hashlib, json, math, re, shutil, subprocess, time
from pathlib import Path
import numpy as np
import requests
import soundfile as sf
import pyloudnorm as pyln
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v4'
WORK = ROOT / 'production/monarch-cam/work/short_ranking_raw_v4/candidates'
REVIEW = BASE / 'review/candidates'
MEDIA = WORK / 'media'
FRAMES = WORK / 'frames'
CACHE_MEDIA = ROOT / 'production/monarch-cam/work/short_ranking_v3/media'
for p in (WORK, REVIEW, MEDIA, FRAMES):
    p.mkdir(parents=True, exist_ok=True)

MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
HEADERS = {'User-Agent': 'MonarchCamRawV4/1.0 (CC0 Wikimedia Commons candidate review; contact via GitHub repo owner)'}
SESSION = requests.Session()
RETRY = Retry(
    total=5, backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(['GET']),
    respect_retry_after_header=True, raise_on_status=False,
)
SESSION.mount('https://', HTTPAdapter(max_retries=RETRY))
SESSION.mount('http://', HTTPAdapter(max_retries=RETRY))
SR = 48000
WINDOW_S = 0.5
SEGMENT_S = 7.0
AUDIBLE_DBFS = -70.0


def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return default
    return default


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def font(size):
    for p in [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
              Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def download(asset):
    dest = MEDIA / asset['local_filename']
    cache_name = asset.get('cache_filename')
    if cache_name:
        cached = CACHE_MEDIA / cache_name
        if cached.exists() and cached.stat().st_size >= 100000:
            shutil.copy2(cached, dest)
            print('Using V3 cached', asset['id'], dest.stat().st_size, flush=True)
            return dest
    last = None
    for url in asset['download_urls']:
        try:
            r = SESSION.get(url, headers=HEADERS, timeout=180, allow_redirects=True)
            r.raise_for_status()
            if len(r.content) < 100000:
                raise RuntimeError('short response')
            dest.write_bytes(r.content)
            print('Retrieved', asset['id'], len(r.content), flush=True)
            time.sleep(3)
            return dest
        except Exception as e:
            last = e
            print('Candidate download failed', asset['id'], url, repr(e), flush=True)
            time.sleep(10)
    raise RuntimeError('Could not retrieve ' + asset['id'] + ': ' + repr(last))


def probe(path):
    p = run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path],
            capture_output=True, check=True)
    return json.loads(p.stdout)


def decode_audio(raw, aid, has_audio):
    wav = WORK / (aid + '_audio.wav')
    if not has_audio:
        return None
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', raw,
         '-map', '0:a:0', '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', wav], check=True)
    x, sr = sf.read(wav, dtype='float32', always_2d=True)
    if sr != SR:
        raise RuntimeError('Unexpected sample rate for ' + aid)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    x = x[:, :2]
    x = x - np.mean(x, axis=0, keepdims=True)
    return x


def rms_dbfs(x):
    return round(float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)), 2)


def peak_dbfs(x):
    return round(float(20 * np.log10(max(float(np.max(np.abs(x))), 1e-12))), 2)


def audio_windows(x):
    block = int(WINDOW_S * SR)
    windows = []
    for start in range(0, len(x) - block + 1, block):
        seg = x[start:start + block]
        windows.append({
            'start': round(start / SR, 3),
            'end': round((start + block) / SR, 3),
            'rms_dbfs': rms_dbfs(seg),
            'peak_dbfs': peak_dbfs(seg),
            'samples': int(len(seg)),
        })
    audible = [w for w in windows if w['rms_dbfs'] > AUDIBLE_DBFS]
    seg_len = int(SEGMENT_S * SR)
    step = int(WINDOW_S * SR)
    top = []
    for start in range(0, max(0, len(x) - seg_len + 1), step):
        seg = x[start:start + seg_len]
        top.append({
            'start': round(start / SR, 3),
            'end': round((start + seg_len) / SR, 3),
            'rms_dbfs': rms_dbfs(seg),
            'peak_dbfs': peak_dbfs(seg),
            'samples': int(len(seg)),
        })
    top.sort(key=lambda w: w['rms_dbfs'], reverse=True)
    meter = pyln.Meter(SR)
    try:
        integrated = float(meter.integrated_loudness(x.astype(np.float64)))
        if not np.isfinite(integrated):
            integrated = -120.0
    except Exception:
        integrated = -120.0
    return {
        'window_seconds': WINDOW_S,
        'segment_seconds': SEGMENT_S,
        'audible_threshold_dbfs': AUDIBLE_DBFS,
        'windows': windows,
        'top_7s_windows': top[:12],
        'audible_window_count': len(audible),
        'peak_window': max(audible, key=lambda w: w['rms_dbfs']) if audible else None,
        'integrated_lufs': round(integrated, 3),
        'dc_offset': round(float(np.mean(x)), 6),
        'duration_seconds': round(len(x) / SR, 3),
    }


def contact_sheets(aid, raw):
    frames_dir = FRAMES / aid
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', raw,
         '-vf', 'fps=1,scale=320:-2', '-q:v', '3', '-start_number', '0',
         frames_dir / (aid + '_%04d.jpg')], check=True)
    frames = sorted(frames_dir.glob(aid + '_*.jpg'))
    if not frames:
        raise RuntimeError('No review frames for ' + aid)
    cols, rows, cw, ch = 4, 2, 336, 246
    pages = math.ceil(len(frames) / (cols * rows))
    paths = []
    for page in range(pages):
        chunk = frames[page * cols * rows:(page + 1) * cols * rows]
        canvas = Image.new('RGB', (cols * cw, 64 + rows * ch), '#101820')
        d = ImageDraw.Draw(canvas)
        d.text((16, 10), f"V4 REPLACEMENT CANDIDATE - {aid.upper()} - PAGE {page + 1}/{pages}",
               font=font(18), fill='#F4F1E8')
        d.text((16, 36), 'One frame every 1s - labels are source timestamps',
               font=font(14), fill='#A9B8C4')
        for i, fp in enumerate(chunk):
            m = re.search(r'_(\d+)\.jpg$', fp.name)
            t = float(int(m.group(1)) if m else i)
            im = Image.open(fp).convert('RGB')
            im.thumbnail((320, 202), Image.Resampling.LANCZOS)
            tile = Image.new('RGB', (320, 202), '#05080B')
            tile.paste(im, ((320 - im.width) // 2, (202 - im.height) // 2))
            x = (i % cols) * cw + 8
            y = 64 + (i // cols) * ch
            canvas.paste(tile, (x, y))
            d.text((x + 4, y + 207), f"{int(t)//60:02d}:{t%60:04.1f}",
                   font=font(19), fill='#63D7C8')
        out = REVIEW / f"candidate_{aid}_sheet_{page + 1:02d}.jpg"
        canvas.save(out, quality=92)
        paths.append(str(out.relative_to(ROOT)))
    return len(frames), paths


def main():
    started = time.time()
    prev_audio = load_json(REVIEW / 'candidate_audio_probe.json', {'assets': {}})
    prev_video_list = load_json(REVIEW / 'candidate_video_ledger.json', {'assets': []}).get('assets', [])
    prev_video = {e['id']: e for e in prev_video_list if 'id' in e}
    prev_manifest = load_json(REVIEW / 'candidate_review_manifest.json', {})
    audio_report, video_ledger = {}, []
    all_sheets = list(prev_manifest.get('contact_sheets', []))

    for asset in MANIFEST['assets']:
        aid = asset['id']
        if asset.get('skip_probe'):
            audio_report[aid] = prev_audio.get('assets', {}).get(aid, {
                'id': aid, 'role': asset['role'], 'source_page': asset['source_page'],
                'note': 'Previously verified; probe skipped to avoid repeated Wikimedia downloads.'
            })
            prev_entry = prev_video.get(aid)
            if prev_entry:
                video_ledger.append(prev_entry)
                all_sheets.extend(prev_entry.get('contact_sheets', []))
            else:
                video_ledger.append({'id': aid, 'note': 'Previously verified; entry missing from ledger.'})
            print('Skip already-verified', aid, flush=True)
            continue

        entry = {
            'id': aid, 'role': asset['role'], 'title': asset['title'],
            'creator': asset['creator'], 'source_page': asset['source_page'],
            'description': asset['description'], 'license': asset['license'],
            'license_url': asset['license_url'], 'mime': asset['mime'],
            'expected_duration_seconds': asset['duration_seconds'],
            'expected_width': asset['width'], 'expected_height': asset['height'],
            'expected_audio_codec': asset['expected_audio_codec'],
        }
        audio_entry = {'id': aid, 'role': asset['role'], 'source_page': asset['source_page']}
        try:
            raw = download(asset)
            info = probe(raw)
            streams = info.get('streams', [])
            video = next((s for s in streams if s.get('codec_type') == 'video'), {})
            audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
            has_audio = audio is not None
            entry.update({
                'local_filename': str(raw.relative_to(ROOT)),
                'bytes': raw.stat().st_size,
                'sha256': sha256(raw),
                'duration_seconds': float(info.get('format', {}).get('duration', 0.0)),
                'width': int(video.get('width', 0)),
                'height': int(video.get('height', 0)),
                'video_codec': video.get('codec_name'),
                'audio_codec': (audio or {}).get('codec_name'),
                'audio_stream_present': has_audio,
            })
            x = decode_audio(raw, aid, has_audio)
            if x is None:
                audio_entry.update({
                    'audio_stream_present': False, 'audible_window_count': 0,
                    'windows': [], 'top_7s_windows': [], 'peak_window': None,
                    'integrated_lufs': -120.0, 'dc_offset': 0.0,
                    'duration_seconds': 0.0,
                    'note': 'No native audio stream in the CC0 file.'
                })
            else:
                a = audio_windows(x)
                audio_entry.update(a)
                audio_entry['audio_stream_present'] = True
                audio_entry['audio_codec'] = (audio or {}).get('codec_name')
            n, sheets = contact_sheets(aid, raw)
            entry.update({'review_frames': n, 'contact_sheets': sheets})
            all_sheets.extend(sheets)
            print('Probe OK', aid, 'audible_windows', audio_entry.get('audible_window_count'),
                  'frames', n, flush=True)
        except Exception as e:
            entry['error'] = repr(e)
            audio_entry['error'] = repr(e)
            print('Probe FAILED', aid, repr(e), flush=True)
        audio_report[aid] = audio_entry
        video_ledger.append(entry)
        time.sleep(5)

    all_sheets = sorted(set(all_sheets))
    save_json(REVIEW / 'candidate_audio_probe.json', {
        'edition': 'raw_fullscreen_v4_replacement_probe',
        'checked_on': MANIFEST['checked_on'],
        'policy': MANIFEST['policy'],
        'sample_rate': SR,
        'assets': audio_report,
        'retrieved_unix': int(started),
    })
    save_json(REVIEW / 'candidate_video_ledger.json', {
        'edition': 'raw_fullscreen_v4_replacement_probe',
        'checked_on': MANIFEST['checked_on'],
        'assets': video_ledger,
    })
    save_json(REVIEW / 'candidate_review_manifest.json', {
        'edition': 'raw_fullscreen_v4_replacement_probe',
        'checked_on': MANIFEST['checked_on'],
        'source_pages': {a['id']: a['source_page'] for a in MANIFEST['assets']},
        'rights_declaration': 'Every candidate is CC0 1.0 via Wikimedia Commons; attribution is recorded voluntarily.',
        'credits': {a['id']: a['creator'] for a in MANIFEST['assets']},
        'audio_probe': str((REVIEW / 'candidate_audio_probe.json').relative_to(ROOT)),
        'video_ledger': str((REVIEW / 'candidate_video_ledger.json').relative_to(ROOT)),
        'contact_sheets': all_sheets,
        'full_motion_review': False,
        'native_audio_listening': False,
        'human_approval': False,
        'virality_guarantee': False,
        'no_added_audio_layers': True,
        'native_source_audio_only': True,
        'note': 'Objective runner measurements and one-frame-per-second contact sheets only; no human full-motion or native-audio listening is claimed.',
    })
    print('Candidate probe complete', len(video_ledger), 'assets', len(all_sheets), 'sheets', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
