#!/usr/bin/env python3
# Runner-side probe for rights-cleared social-origin Commons originals.
# Measures each file's own native audio stream and one-frame-per-second motion,
# then writes contact sheets and objective window scores. No audio is added.
from __future__ import annotations
import hashlib, json, math, re, shutil, subprocess, time
from pathlib import Path
import numpy as np
import requests
import soundfile as sf
import pyloudnorm as pyln
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v7'
WORK = ROOT / 'production/monarch-cam/work/short_ranking_raw_v7/candidates'
REVIEW = BASE / 'review/candidates'
MEDIA = WORK / 'media'
FRAMES = WORK / 'frames'
V3_CACHE = ROOT / 'production/monarch-cam/work/short_ranking_v3/media'
V4_CACHE = ROOT / 'production/monarch-cam/work/short_ranking_raw_v4/media'
for p in (WORK, REVIEW, MEDIA, FRAMES):
    p.mkdir(parents=True, exist_ok=True)

MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
HEADERS = {
    'User-Agent': 'MonarchCamViralV7/1.0 (https://github.com/adil-chandio/Monarch.Overall.Work; rights-cleared social-origin candidate review)',
    'Accept': 'video/webm,application/octet-stream;q=0.9,*/*;q=0.8',
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
RETRY = Retry(
    total=6, connect=6, read=6, status=6, backoff_factor=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(['GET']),
    respect_retry_after_header=True, raise_on_status=False,
)
SESSION.mount('https://', HTTPAdapter(max_retries=RETRY))
SESSION.mount('http://', HTTPAdapter(max_retries=RETRY))
SR = 48000
WINDOW_S = 0.5
SEGMENT_S = 8.6
AUDIBLE_DBFS = -75.0
SELECTABLE_DBFS = -65.0
MIN_MOTION = 0.10
API = 'https://commons.wikimedia.org/w/api.php'


def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def sha1(path):
    h = hashlib.sha1()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


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


def api_download_urls(asset):
    """Resolve exact Commons VP9/Opus derivative URLs from the API, not guessed paths."""
    params = {
        'action': 'query', 'format': 'json', 'formatversion': '2',
        'prop': 'videoinfo', 'titles': asset['commons_title'],
        'viprop': 'url|derivatives',
    }
    r = SESSION.get(API, params=params, timeout=90)
    r.raise_for_status()
    data = r.json()
    pages = data.get('query', {}).get('pages', [])
    urls = []
    if pages and 'videoinfo' in pages[0]:
        vi = pages[0]['videoinfo'][0]
        derivs = vi.get('derivatives', []) or []
        for key in ('480p.vp9.webm', '240p.vp9.webm'):
            chosen = next((d for d in derivs if d.get('transcodekey') == key and 'opus' in d.get('type', '')), None)
            if chosen and str(chosen.get('src', '')).startswith('https://upload.wikimedia.org/wikipedia/commons/transcoded/'):
                urls.append(chosen['src'])
        if str(vi.get('url', '')).startswith('https://upload.wikimedia.org/wikipedia/commons/'):
            urls.append(vi['url'])
    for url in asset.get('download_urls', []):
        if url not in urls:
            urls.append(url)
    if not urls:
        raise RuntimeError('No Commons download URL resolved for ' + asset['id'])
    time.sleep(1)
    return urls


def download(asset):
    dest = MEDIA / asset['local_filename']
    if dest.exists() and dest.stat().st_size >= 100000:
        return dest, 'cached_candidate_media'
    cache_dir = V4_CACHE if asset.get('cache_dir') == 'v4' else V3_CACHE
    cache_name = asset.get('cache_filename')
    if cache_name:
        cached = cache_dir / cache_name
        if cached.exists() and cached.stat().st_size >= 100000:
            shutil.copy2(cached, dest)
            print('Using cached original', asset['id'], dest.stat().st_size, flush=True)
            return dest, 'legacy_cached_media'
    last = None
    tmp = dest.with_suffix('.download')
    for url in api_download_urls(asset):
        try:
            r = SESSION.get(url, timeout=240, allow_redirects=True, stream=True)
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
                raise RuntimeError('short streamed response ' + str(total))
            tmp.replace(dest)
            print('Retrieved Commons candidate', asset['id'], 'from', url, total, 'bytes', flush=True)
            time.sleep(3)
            return dest, url
        except Exception as e:
            last = e
            if tmp.exists():
                tmp.unlink()
            print('Candidate download failed', asset['id'], url, repr(e), flush=True)
            time.sleep(10)
    raise RuntimeError('Could not retrieve ' + asset['id'] + ': ' + repr(last))


def probe(path):
    p = run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path],
            capture_output=True, check=True)
    return json.loads(p.stdout)


def decode_audio(raw, aid, has_audio):
    if not has_audio:
        return None
    wav = WORK / (aid + '_audio.wav')
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


def dbfs(value):
    return round(float(max(-120.0, 20 * np.log10(max(float(value), 1e-12)))), 2)


def chunk_stats(x, start, dur):
    a = int(round(start * SR))
    b = min(len(x), int(round((start + dur) * SR)))
    c = x[a:b]
    if not len(c):
        return -120.0, -120.0, 0
    ac = c - np.mean(c, axis=0, keepdims=True)
    return dbfs(float(np.sqrt(np.mean(ac ** 2)))), dbfs(float(np.max(np.abs(ac)))), int(len(c))


def contact_sheets(aid, raw):
    frames_dir = FRAMES / aid
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', raw,
         '-t', '120', '-vf', 'fps=1,scale=160:-2', '-q:v', '3', '-start_number', '0',
         frames_dir / (aid + '_%04d.jpg')], check=True)
    frames = sorted(frames_dir.glob(aid + '_*.jpg'))
    if len(frames) < 2:
        raise RuntimeError('Insufficient review frames for ' + aid)
    arrays = []
    for fp in frames:
        im = Image.open(fp).convert('L')
        arrays.append(np.asarray(im, dtype=np.float32))
    motion_scores = [float(np.mean(np.abs(arrays[i + 1] - arrays[i]))) for i in range(len(arrays) - 1)]
    global_motion = round(float(np.mean(motion_scores)) if motion_scores else 0.0, 4)
    cols, rows, cw, ch = 4, 2, 336, 246
    pages = math.ceil(len(frames) / (cols * rows))
    paths = []
    for page in range(pages):
        chunk = frames[page * cols * rows:(page + 1) * cols * rows]
        canvas = Image.new('RGB', (cols * cw, 64 + rows * ch), '#101820')
        d = ImageDraw.Draw(canvas)
        d.text((16, 10), f"V7 SOCIAL-ORIGIN CANDIDATE - {aid.upper()} - PAGE {page + 1}/{pages}", font=font(18), fill='#F4F1E8')
        d.text((16, 36), 'One frame every 1s - labels are source timestamps', font=font(14), fill='#A9B8C4')
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
            d.text((x + 4, y + 207), f"{int(t)//60:02d}:{t%60:04.1f}", font=font(19), fill='#63D7C8')
        out = REVIEW / f"candidate_{aid}_sheet_{page + 1:02d}.jpg"
        canvas.save(out, quality=92)
        paths.append(str(out.relative_to(ROOT)))
    return len(frames), paths, motion_scores, global_motion


def audio_windows(x, motion_scores, global_motion, humor_bonus):
    duration = len(x) / SR
    windows = []
    block = int(WINDOW_S * SR)
    for start in range(0, len(x) - block + 1, block):
        seg = x[start:start + block]
        ac = seg - np.mean(seg, axis=0, keepdims=True)
        windows.append({
            'start': round(start / SR, 3), 'end': round((start + block) / SR, 3),
            'rms_dbfs': dbfs(float(np.sqrt(np.mean(ac ** 2)))),
            'peak_dbfs': dbfs(float(np.max(np.abs(ac)))), 'samples': int(len(seg)),
        })
    audible = [w for w in windows if w['rms_dbfs'] > AUDIBLE_DBFS]
    candidates = []
    for st in np.arange(0.0, max(0.0, duration - SEGMENT_S + 0.001), WINDOW_S):
        st = float(round(st, 3))
        rms, peak, samples = chunk_stats(x, st, SEGMENT_S)
        a = int(np.floor(st))
        b = min(len(motion_scores), int(np.ceil(st + SEGMENT_S)) - 1)
        local = motion_scores[a:b] if b > a else []
        motion = round(float(np.mean(local)) if local else global_motion, 4)
        motion_norm = min(20.0, max(0.0, motion))
        audio_norm = min(20.0, max(0.0, rms + 55.0))
        score = round(0.6 * motion_norm + 0.4 * audio_norm + float(humor_bonus), 4)
        candidates.append({
            'start': st, 'end': round(min(duration, st + SEGMENT_S), 3),
            'duration': SEGMENT_S, 'rms_dbfs': rms, 'peak_dbfs': peak,
            'samples': samples, 'motion_score': motion,
            'score': score, 'selectable': bool(rms > SELECTABLE_DBFS and motion >= MIN_MOTION),
        })
    candidates.sort(key=lambda z: z['score'], reverse=True)
    meter = pyln.Meter(SR)
    try:
        integrated = float(meter.integrated_loudness(x.astype(np.float64)))
        if not np.isfinite(integrated):
            integrated = -120.0
    except Exception:
        integrated = -120.0
    return {
        'window_seconds': WINDOW_S, 'segment_seconds': SEGMENT_S,
        'audible_threshold_dbfs': AUDIBLE_DBFS,
        'selectable_segment_rms_dbfs_min': SELECTABLE_DBFS,
        'minimum_motion_score': MIN_MOTION,
        'windows': windows, 'top_windows': candidates[:16],
        'audible_window_count': len(audible),
        'peak_window': max(audible, key=lambda w: w['rms_dbfs']) if audible else None,
        'integrated_lufs': round(integrated, 3),
        'dc_offset': round(float(np.mean(x)), 6),
        'duration_seconds': round(duration, 3),
    }


def main():
    started = time.time()
    audio_report, video_ledger, all_sheets = {}, [], []
    for asset in MANIFEST['assets']:
        aid = asset['id']
        entry = {
            'id': aid, 'role': asset.get('role', 'rights_cleared_social_origin_candidate'), 'title': asset['title'],
            'creator': asset['creator'], 'source_page': asset['source_page'],
            'description': asset.get('description', asset.get('origin_note', '')), 'license': asset['license'],
            'license_url': asset['license_url'], 'mime': asset['mime'],
            'expected_duration_seconds': asset['duration_seconds'],
            'expected_width': asset['width'], 'expected_height': asset['height'],
            'expected_audio_codec': asset['expected_audio_codec'],
            'probe_completed': False,
        }
        audio_entry = {'id': aid, 'role': asset.get('role', 'rights_cleared_social_origin_candidate'), 'source_page': asset['source_page']}
        try:
            raw, used_url = download(asset)
            info = probe(raw)
            streams = info.get('streams', [])
            video = next((s for s in streams if s.get('codec_type') == 'video'), {})
            audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
            has_audio = audio is not None
            n, sheets, motion_scores, global_motion = contact_sheets(aid, raw)
            all_sheets.extend(sheets)
            x = decode_audio(raw, aid, has_audio)
            if x is None:
                audio_entry.update({
                    'audio_stream_present': False, 'audible_window_count': 0,
                    'windows': [], 'top_windows': [], 'peak_window': None,
                    'integrated_lufs': -120.0, 'dc_offset': 0.0,
                    'duration_seconds': 0.0, 'note': 'No native audio stream in this rights-cleared Commons file.',
                    'runner_audio_visual_probe_passed': False,
                    'runner_visual_motion_probe': False,
                })
            else:
                a = audio_windows(x, motion_scores, global_motion, asset.get('humor_bonus', 0.0))
                audio_entry.update(a)
                audio_entry['audio_stream_present'] = True
                audio_entry['audio_codec'] = (audio or {}).get('codec_name')
                best = a['top_windows'][0] if a['top_windows'] else None
                audio_entry['runner_audio_visual_probe_passed'] = bool(
                    best and best['rms_dbfs'] > SELECTABLE_DBFS and best['motion_score'] >= MIN_MOTION
                )
                audio_entry['runner_visual_motion_probe'] = bool(global_motion >= MIN_MOTION)
            audio_entry['download_url'] = used_url
            entry.update({
                'local_filename': str(raw.relative_to(ROOT)),
                'download_url': used_url, 'bytes': raw.stat().st_size, 'sha1': sha1(raw), 'sha256': sha256(raw),
                'duration_seconds': float(info.get('format', {}).get('duration', 0.0)),
                'width': int(video.get('width', 0)), 'height': int(video.get('height', 0)),
                'display_width': asset.get('display_width', int(video.get('width', 0))),
                'display_height': asset.get('display_height', int(video.get('height', 0))),
                'video_codec': video.get('codec_name'),
                'audio_codec': (audio or {}).get('codec_name'),
                'audio_stream_present': has_audio,
                'review_frames': n, 'contact_sheets': sheets,
                'global_motion_score': global_motion,
                'minimum_motion_score': MIN_MOTION,
                'runner_visual_motion_probe': bool(global_motion >= MIN_MOTION),
                'runner_audio_visual_probe_passed': bool(audio_entry.get('runner_audio_visual_probe_passed')),
                'best_window': (audio_entry.get('top_windows') or [None])[0],
                'probe_completed': True,
            })
            print('Probe OK', aid, 'audio', has_audio, 'motion', global_motion,
                  'selectable', entry['runner_audio_visual_probe_passed'], flush=True)
        except Exception as e:
            entry['error'] = repr(e)
            audio_entry['error'] = repr(e)
            audio_entry['runner_audio_visual_probe_passed'] = False
            audio_entry['runner_visual_motion_probe'] = False
            print('Probe FAILED', aid, repr(e), flush=True)
        audio_report[aid] = audio_entry
        video_ledger.append(entry)
        time.sleep(2)

    completed = sum(1 for e in video_ledger if e.get('probe_completed'))
    av_pass = sum(1 for e in video_ledger if e.get('runner_audio_visual_probe_passed'))
    motion_pass = sum(1 for e in video_ledger if e.get('runner_visual_motion_probe'))
    # V7 has 12 candidates; require at least seven measurable audio/motion sources.
    flags = {
        'runner_probe_passed': bool(completed >= 7),
        'runner_audio_visual_probe_passed': bool(av_pass >= 7),
        'runner_visual_motion_probe': bool(motion_pass >= 7),
        'contact_sheets_written': bool(all_sheets),
        'source_review_recorded': True,
        'visual_lock_written': False,
        'no_unverified_reposts': True,
        'current_trending_claim': False,
        'unverified_social_repost': False,
        'full_motion_review': False,
        'native_audio_listening': False,
        'human_approval': False,
        'sign_off': False,
        'audience_result_promise': False,
        'virality_guarantee': False,
        'perfection_claim': False,
        'retention_claim': False,
        'hypnosis_claim': False,
        'three_x_claim': False,
        'subscribe_claim': False,
        'like_claim': False,
        'same_path_replacement': False,
        'factual_superlative_claim': False,
        'third_party_repost': False,
        'ai_audio': False,
        'generated_calls': False,
        'v3_audio_packages': False,
        'audio_substitution': False,
        'earshot_claim': False,
        'model_claim': False,
        'sound_design_layers': False,
        'sub_bloom_layers': False,
        'native_ambience_layers': False,
        'ambience_layers': False,
        'cue_layers': False,
    }
    save_json(REVIEW / 'candidate_audio_probe.json', {
        'edition': 'social_origin_v7_candidate_probe',
        'checked_on': MANIFEST['checked_on'],
        'policy': MANIFEST['policy'],
        'sample_rate': SR,
        'assets': audio_report,
        'flags': flags,
        'retrieved_unix': int(started),
    })
    save_json(REVIEW / 'candidate_video_ledger.json', {
        'edition': 'social_origin_v7_candidate_probe',
        'checked_on': MANIFEST['checked_on'],
        'candidate_count': len(video_ledger),
        'completed_count': completed,
        'audio_visual_pass_count': av_pass,
        'motion_pass_count': motion_pass,
        'flags': flags,
        'assets': video_ledger,
    })
    save_json(REVIEW / 'candidate_review_manifest.json', {
        'edition': 'social_origin_v7_candidate_probe',
        'checked_on': MANIFEST['checked_on'],
        'source_pages': {a['id']: a['source_page'] for a in MANIFEST['assets']},
        'rights_declaration': 'Ten rights-cleared PD/CC BY Wikimedia Commons social-origin candidates; selected originals are rechecked per-title through the Commons API extmetadata and original SHA-1. Two CC BY candidates with third-party copyright language in their descriptions were excluded.',
        'credits': {a['id']: a['creator'] for a in MANIFEST['assets']},
        'audio_probe': str((REVIEW / 'candidate_audio_probe.json').relative_to(ROOT)),
        'video_ledger': str((REVIEW / 'candidate_video_ledger.json').relative_to(ROOT)),
        'contact_sheets': sorted(set(all_sheets)),
        'flags': flags,
        'no_added_audio_layers': True,
        'native_source_audio_only': True,
        'rights_cleared_social_origin_files_only': True,
        'no_unverified_reposts': True,
        'note': 'Objective runner measurements and one-frame-per-second contact sheets only; full_motion_review=false, native_audio_listening=false, human_approval=false, sign_off=false.',
    })
    if not all([flags['runner_probe_passed'], flags['runner_audio_visual_probe_passed'], flags['runner_visual_motion_probe'], flags['contact_sheets_written']]):
        raise RuntimeError('Candidate probe did not produce seven measurable audio/motion candidates')
    print('Candidate probe complete', completed, 'completed', av_pass, 'audio/visual pass', len(all_sheets), 'sheets', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
